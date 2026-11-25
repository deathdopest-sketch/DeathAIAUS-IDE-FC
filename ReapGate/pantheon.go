package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
)

// PantheonModel represents a Death Pantheon AI model
type PantheonModel struct {
	Deity      string `json:"name"`
	Mythology  string `json:"mythology"`
	Title      string `json:"title"`
	Role       string `json:"role"`
	Tier       string `json:"tier"`
	Size       string `json:"size"`
	Power      string `json:"power"`
	Emoji      string `json:"emoji"`
	Filename   string `json:"-"`
	FullPath   string `json:"-"`
}

// PantheonConfig holds the pantheon configuration
type PantheonConfig struct {
	Pantheon map[string]PantheonModel `json:"pantheon"`
}

// LoadPantheonConfig loads the Death Pantheon configuration
func LoadPantheonConfig() map[string]PantheonModel {
	configPath := filepath.Join("..", "death_pantheon.json")
	
	data, err := os.ReadFile(configPath)
	if err != nil {
		return make(map[string]PantheonModel)
	}
	
	var config PantheonConfig
	if err := json.Unmarshal(data, &config); err != nil {
		return make(map[string]PantheonModel)
	}
	
	return config.Pantheon
}

// MatchPantheonModel tries to match a filename to a pantheon deity
func MatchPantheonModel(filename string, pantheon map[string]PantheonModel) *PantheonModel {
	filenameLower := strings.ToLower(filepath.Base(filename))
	
	// Check if it's a DeathAIAUS branded file
	if strings.Contains(filenameLower, "deathaius") {
		// Extract deity name from filename
		// Format: DeathAIAUS-DEITY-SIZE-QUANT.gguf
		parts := strings.Split(strings.TrimPrefix(filenameLower, "deathaius-"), "-")
		if len(parts) > 0 {
			deityName := strings.ToUpper(parts[0])
			
			// Find matching deity
			for _, model := range pantheon {
				if strings.ToUpper(model.Deity) == deityName {
					matchedModel := model
					matchedModel.Filename = filepath.Base(filename)
					matchedModel.FullPath = filename
					return &matchedModel
				}
			}
		}
	}
	
	// Try exact match with original filename
	for originalName, model := range pantheon {
		if strings.ToLower(originalName) == filenameLower {
			matchedModel := model
			matchedModel.Filename = filepath.Base(filename)
			matchedModel.FullPath = filename
			return &matchedModel
		}
	}
	
	// Partial match
	for originalName, model := range pantheon {
		if strings.Contains(filenameLower, strings.ToLower(originalName)) ||
		   strings.Contains(strings.ToLower(originalName), filenameLower) {
			matchedModel := model
			matchedModel.Filename = filepath.Base(filename)
			matchedModel.FullPath = filename
			return &matchedModel
		}
	}
	
	return nil
}

// GetDisplayName returns a formatted display name for a model
func (m *PantheonModel) GetDisplayName() string {
	if m.Deity != "" {
		return m.Emoji + " " + m.Deity + " - " + m.Role
	}
	return m.Filename
}
