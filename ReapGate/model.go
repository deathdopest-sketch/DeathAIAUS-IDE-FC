package main

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"

	llama "github.com/go-skynet/go-llama.cpp"
)

// ModelManager manages loading and unloading of models
type ModelManager struct {
	config       *Config
	pantheon     map[string]PantheonModel
	loadedModels map[string]*LoadedModel
	mu           sync.RWMutex
}

// LoadedModel represents a model loaded in memory
type LoadedModel struct {
	Model        *llama.LLama // llama model instance
	PantheonInfo *PantheonModel
	LastUsed     time.Time
	UseCount     int
}

// NewModelManager creates a new model manager
func NewModelManager(config *Config) *ModelManager {
	return &ModelManager{
		config:       config,
		pantheon:     LoadPantheonConfig(),
		loadedModels: make(map[string]*LoadedModel),
	}
}

// ScanModels scans for available .gguf models
func (mm *ModelManager) ScanModels() []*PantheonModel {
	var models []*PantheonModel

	err := filepath.Walk(mm.config.ModelPath, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return nil
		}

		if !info.IsDir() && strings.HasSuffix(strings.ToLower(info.Name()), ".gguf") {
			// Try to match with pantheon
			if pantheonModel := MatchPantheonModel(path, mm.pantheon); pantheonModel != nil {
				models = append(models, pantheonModel)
			} else {
				// Unknown model, add with basic info
				models = append(models, &PantheonModel{
					Filename: info.Name(),
					FullPath: path,
					Deity:    "Unknown",
					Role:     "General Purpose",
				})
			}
		}

		return nil
	})

	if err != nil {
		log.Printf("[ModelManager] Error scanning models: %v", err)
	}

	return models
}

// LoadModel loads a model into memory
func (mm *ModelManager) LoadModel(modelPath string) error {
	mm.mu.Lock()
	defer mm.mu.Unlock()

	// Check if already loaded
	if loaded, exists := mm.loadedModels[modelPath]; exists {
		loaded.LastUsed = time.Now()
		loaded.UseCount++
		log.Printf("[ModelManager] Using cached model: %s", modelPath)
		return nil
	}

	// Check if we need to unload old models
	if len(mm.loadedModels) >= mm.config.MaxModels {
		mm.unloadOldestModel()
	}

	log.Printf("[ModelManager] Loading model: %s", modelPath)
	start := time.Now()

	// Load model with llama.cpp
	log.Printf("[ModelManager] Attempting to load model: %s", modelPath)
	log.Printf("[ModelManager] Using context size: 2048, GPU layers: %d", mm.config.GPULayers)
	
	model, err := llama.New(modelPath,
		llama.SetContext(2048),
		llama.SetGPULayers(mm.config.GPULayers))
	if err != nil {
		log.Printf("[ModelManager] Model loading failed with error: %v", err)
		log.Printf("[ModelManager] Error type: %T", err)
		return fmt.Errorf("failed to load model: %v", err)
	}
	
	log.Printf("[ModelManager] Model loaded successfully: %s", modelPath)

	// Get pantheon info if available
	var pantheonInfo *PantheonModel
	if matched := MatchPantheonModel(modelPath, mm.pantheon); matched != nil {
		pantheonInfo = matched
	}

	mm.loadedModels[modelPath] = &LoadedModel{
		Model:        model,
		PantheonInfo: pantheonInfo,
		LastUsed:     time.Now(),
		UseCount:     1,
	}

	elapsed := time.Since(start)
	log.Printf("[ModelManager] Model loaded in %v", elapsed)

	return nil
}

// GetModel gets a loaded model (loading if necessary)
func (mm *ModelManager) GetModel(modelPath string) (*LoadedModel, error) {
	mm.mu.RLock()
	if loaded, exists := mm.loadedModels[modelPath]; exists {
		mm.mu.RUnlock()
		loaded.LastUsed = time.Now()
		loaded.UseCount++
		return loaded, nil
	}
	mm.mu.RUnlock()

	// Load model if not in memory
	if err := mm.LoadModel(modelPath); err != nil {
		return nil, err
	}

	mm.mu.RLock()
	defer mm.mu.RUnlock()
	return mm.loadedModels[modelPath], nil
}

// Predict generates text using a loaded model
func (mm *ModelManager) Predict(modelPath, prompt string, maxTokens int) (string, error) {
	loaded, err := mm.GetModel(modelPath)
	if err != nil {
		return "", err
	}

	log.Printf("[ModelManager] Generating response (max tokens: %d)", maxTokens)

	// Generate response
	result, err := loaded.Model.Predict(prompt,
		llama.SetTokens(maxTokens),
		llama.SetTemperature(0.7))
	if err != nil {
		return "", fmt.Errorf("prediction failed: %v", err)
	}

	return result, nil
}

// unloadOldestModel unloads the least recently used model
func (mm *ModelManager) unloadOldestModel() {
	var oldestPath string
	var oldestTime time.Time = time.Now()

	for path, loaded := range mm.loadedModels {
		if loaded.LastUsed.Before(oldestTime) {
			oldestTime = loaded.LastUsed
			oldestPath = path
		}
	}

	if oldestPath != "" {
		log.Printf("[ModelManager] Unloading old model: %s", oldestPath)
		if model, exists := mm.loadedModels[oldestPath]; exists {
			model.Model.Free()
		}
		delete(mm.loadedModels, oldestPath)
	}
}

// Cleanup unloads all models
func (mm *ModelManager) Cleanup() {
	mm.mu.Lock()
	defer mm.mu.Unlock()

	log.Println("[ModelManager] Cleaning up all models...")
	for path, loaded := range mm.loadedModels {
		log.Printf("[ModelManager] Unloading: %s", path)
		loaded.Model.Free()
	}
	mm.loadedModels = make(map[string]*LoadedModel)
}

// GetLoadedModels returns info about currently loaded models
func (mm *ModelManager) GetLoadedModels() []string {
	mm.mu.RLock()
	defer mm.mu.RUnlock()

	var models []string
	for path := range mm.loadedModels {
		models = append(models, filepath.Base(path))
	}
	return models
}

// UnloadCurrentModel unloads all currently loaded models
func (mm *ModelManager) UnloadCurrentModel() {
	mm.mu.Lock()
	defer mm.mu.Unlock()

	log.Println("[ModelManager] Unloading all current models...")
	for path, loaded := range mm.loadedModels {
		log.Printf("[ModelManager] Unloading: %s", path)
		loaded.Model.Free()
	}
	mm.loadedModels = make(map[string]*LoadedModel)
}

// GetCurrentModel returns the currently loaded model path
func (mm *ModelManager) GetCurrentModel() string {
	mm.mu.RLock()
	defer mm.mu.RUnlock()

	// Return the most recently used model
	var currentPath string
	var latestTime time.Time

	for path, loaded := range mm.loadedModels {
		if loaded.LastUsed.After(latestTime) {
			latestTime = loaded.LastUsed
			currentPath = path
		}
	}

	return currentPath
}

// GetModelStatus returns the current model loading status
func (mm *ModelManager) GetModelStatus() map[string]interface{} {
	mm.mu.RLock()
	defer mm.mu.RUnlock()

	status := map[string]interface{}{
		"loaded_count": len(mm.loadedModels),
		"max_models":   mm.config.MaxModels,
		"models":       make([]map[string]interface{}, 0),
	}

	for path, loaded := range mm.loadedModels {
		modelInfo := map[string]interface{}{
			"path":      path,
			"filename":  filepath.Base(path),
			"last_used": loaded.LastUsed,
			"use_count": loaded.UseCount,
		}

		if loaded.PantheonInfo != nil {
			modelInfo["deity"] = loaded.PantheonInfo.Deity
			modelInfo["role"] = loaded.PantheonInfo.Role
		}

		status["models"] = append(status["models"].([]map[string]interface{}), modelInfo)
	}

	return status
}
