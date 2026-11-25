package main

import (
	"fmt"
	"log"
	"net/http"
	"path/filepath"
	"strings"
	
	"github.com/gin-gonic/gin"
)

// Server handles HTTP requests
type Server struct {
	config       *Config
	modelManager *ModelManager
	router       *gin.Engine
}

// ChatCompletionRequest matches OpenAI API format
type ChatCompletionRequest struct {
	Model       string    `json:"model"`
	Messages    []Message `json:"messages"`
	Temperature float64   `json:"temperature"`
	MaxTokens   int       `json:"max_tokens"`
	Stream      bool      `json:"stream"`
}

// Message represents a chat message
type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

// ChatCompletionResponse matches OpenAI API format
type ChatCompletionResponse struct {
	ID      string   `json:"id"`
	Object  string   `json:"object"`
	Created int64    `json:"created"`
	Model   string   `json:"model"`
	Choices []Choice `json:"choices"`
}

// Choice represents a response choice
type Choice struct {
	Index   int     `json:"index"`
	Message Message `json:"message"`
}

// ModelInfo represents model information
type ModelInfo struct {
	ID      string `json:"id"`
	Object  string `json:"object"`
	OwnedBy string `json:"owned_by"`
}

// ModelsResponse represents the models list response
type ModelsResponse struct {
	Object string      `json:"object"`
	Data   []ModelInfo `json:"data"`
}

// NewServer creates a new HTTP server
func NewServer(config *Config, modelManager *ModelManager) *Server {
	// Set Gin to release mode
	gin.SetMode(gin.ReleaseMode)
	
	router := gin.Default()
	
	server := &Server{
		config:       config,
		modelManager: modelManager,
		router:       router,
	}
	
	server.setupRoutes()
	return server
}

func (s *Server) setupRoutes() {
	// Health check
	s.router.GET("/health", s.handleHealth)
	
	// Models list (OpenAI compatible)
	s.router.GET("/v1/models", s.handleModels)
	
	// Chat completions (OpenAI compatible)
	s.router.POST("/v1/chat/completions", s.handleChatCompletion)
	
	// ReapGate specific endpoints
	s.router.GET("/reapgate/loaded", s.handleLoadedModels)
	s.router.GET("/reapgate/pantheon", s.handlePantheon)
	
	// Model loading endpoints
	s.router.POST("/v1/models/load", s.handleLoadModel)
	s.router.POST("/v1/models/unload", s.handleUnloadModel)
	s.router.GET("/v1/models/current", s.handleCurrentModel)
	s.router.GET("/v1/models/status", s.handleModelStatus)
}

// handleHealth returns server health status
func (s *Server) handleHealth(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":  "ok",
		"version": Version,
		"loaded_models": s.modelManager.GetLoadedModels(),
	})
}

// handleModels returns list of available models
func (s *Server) handleModels(c *gin.Context) {
	models := s.modelManager.ScanModels()
	
	var modelInfos []ModelInfo
	for _, model := range models {
		modelInfos = append(modelInfos, ModelInfo{
			ID:      model.FullPath,
			Object:  "model",
			OwnedBy: "DeathAIAUS",
		})
	}
	
	c.JSON(http.StatusOK, ModelsResponse{
		Object: "list",
		Data:   modelInfos,
	})
}

// handleChatCompletion handles chat completion requests
func (s *Server) handleChatCompletion(c *gin.Context) {
	var req ChatCompletionRequest
	if err := c.BindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	// Find model path
	modelPath := s.findModelPath(req.Model)
	if modelPath == "" {
		c.JSON(http.StatusNotFound, gin.H{"error": fmt.Sprintf("Model not found: %s", req.Model)})
		return
	}
	
	// Build prompt from messages
	prompt := s.buildPrompt(req.Messages)
	
	// Set default max tokens
	maxTokens := req.MaxTokens
	if maxTokens == 0 {
		maxTokens = 512
	}
	
	log.Printf("[Server] Request: model=%s, max_tokens=%d", filepath.Base(modelPath), maxTokens)
	
	// Generate response
	response, err := s.modelManager.Predict(modelPath, prompt, maxTokens)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	
	// Return OpenAI-compatible response
	c.JSON(http.StatusOK, ChatCompletionResponse{
		ID:      "reapgate-" + fmt.Sprintf("%d", c.Request.Context().Value("request_id")),
		Object:  "chat.completion",
		Created: 0,
		Model:   req.Model,
		Choices: []Choice{
			{
				Index: 0,
				Message: Message{
					Role:    "assistant",
					Content: response,
				},
			},
		},
	})
}

// handleLoadedModels returns currently loaded models
func (s *Server) handleLoadedModels(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"loaded_models": s.modelManager.GetLoadedModels(),
	})
}

// handlePantheon returns Death Pantheon information
func (s *Server) handlePantheon(c *gin.Context) {
	models := s.modelManager.ScanModels()
	c.JSON(http.StatusOK, gin.H{
		"pantheon": models,
		"count":    len(models),
	})
}

// handleLoadModel loads a specific model
func (s *Server) handleLoadModel(c *gin.Context) {
	var req struct {
		ModelPath string `json:"model_path"`
	}
	if err := c.BindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	// Find model path if not absolute
	modelPath := req.ModelPath
	if !filepath.IsAbs(modelPath) {
		foundPath := s.findModelPath(modelPath)
		if foundPath == "" {
			c.JSON(http.StatusNotFound, gin.H{"error": fmt.Sprintf("Model not found: %s", modelPath)})
			return
		}
		modelPath = foundPath
	}
	
	// Unload current model
	s.modelManager.UnloadCurrentModel()
	
	// Load new model
	err := s.modelManager.LoadModel(modelPath)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"status": "loaded",
		"model":  modelPath,
	})
}

// handleUnloadModel unloads the current model
func (s *Server) handleUnloadModel(c *gin.Context) {
	s.modelManager.UnloadCurrentModel()
	c.JSON(http.StatusOK, gin.H{
		"status": "unloaded",
	})
}

// handleCurrentModel returns the currently loaded model
func (s *Server) handleCurrentModel(c *gin.Context) {
	current := s.modelManager.GetCurrentModel()
	c.JSON(http.StatusOK, gin.H{
		"current_model": current,
	})
}

// handleModelStatus returns model loading status
func (s *Server) handleModelStatus(c *gin.Context) {
	status := s.modelManager.GetModelStatus()
	c.JSON(http.StatusOK, gin.H{
		"status": status,
	})
}

// findModelPath finds the full path for a model
func (s *Server) findModelPath(modelIdentifier string) string {
	models := s.modelManager.ScanModels()
	
	modelLower := strings.ToLower(modelIdentifier)
	
	// Try exact path match
	for _, model := range models {
		if model.FullPath == modelIdentifier {
			return model.FullPath
		}
	}
	
	// Try filename match
	for _, model := range models {
		if strings.ToLower(model.Filename) == modelLower {
			return model.FullPath
		}
	}
	
	// Try deity name match
	for _, model := range models {
		if strings.ToLower(model.Deity) == modelLower {
			return model.FullPath
		}
	}
	
	// Try partial match
	for _, model := range models {
		if strings.Contains(strings.ToLower(model.FullPath), modelLower) {
			return model.FullPath
		}
	}
	
	return ""
}

// buildPrompt builds a prompt from chat messages
func (s *Server) buildPrompt(messages []Message) string {
	var parts []string
	
	for _, msg := range messages {
		switch msg.Role {
		case "system":
			parts = append(parts, fmt.Sprintf("### System:\n%s\n", msg.Content))
		case "user":
			parts = append(parts, fmt.Sprintf("### User:\n%s\n", msg.Content))
		case "assistant":
			parts = append(parts, fmt.Sprintf("### Assistant:\n%s\n", msg.Content))
		}
	}
	
	parts = append(parts, "### Assistant:\n")
	
	return strings.Join(parts, "\n")
}

// Start starts the HTTP server
func (s *Server) Start(addr string) error {
	return s.router.Run(addr)
}
