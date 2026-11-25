package main

import (
	"os"
	"path/filepath"
)

// Config holds ReapGate configuration
type Config struct {
	Host      string
	Port      string
	ModelPath string
	MaxModels int // Max models to keep in memory
	GPULayers int // Number of layers to offload to GPU
}

// LoadConfig loads configuration from environment or uses defaults
func LoadConfig() *Config {
	config := &Config{
		Host:      getEnv("REAPGATE_HOST", DefaultHost),
		Port:      getEnv("REAPGATE_PORT", DefaultPort),
		ModelPath: getModelPath(),
		MaxModels: 2, // Keep 2 models in memory max
		GPULayers: 35, // Default GPU layers (adjust based on VRAM)
	}
	
	return config
}

// getModelPath finds the Death Pantheon model directory
func getModelPath() string {
	// Try environment variable first
	if path := os.Getenv("REAPGATE_MODELS"); path != "" {
		return path
	}
	
	// Try Google Drive default
	googleDrivePath := filepath.Join("G:", "My Drive", "DeathAIAUS_PANTHEON")
	if _, err := os.Stat(googleDrivePath); err == nil {
		return googleDrivePath
	}
	
	// Try local workspace
	localPath := filepath.Join(".", "models")
	if _, err := os.Stat(localPath); err == nil {
		return localPath
	}
	
	// Default to current directory
	return "."
}

// getEnv gets environment variable or returns default
func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
