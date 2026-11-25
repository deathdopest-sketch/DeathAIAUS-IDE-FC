package main

import (
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
)

const (
	// ReapGate version
	Version = "1.0.0"
	
	// Default configuration
	DefaultPort = "7777"
	DefaultHost = "localhost"
)

func main() {
	// ASCII art banner
	printBanner()
	
	// Load configuration
	config := LoadConfig()
	log.Printf("[ReapGate] Starting Death's Inference Engine v%s", Version)
	log.Printf("[ReapGate] Loading models from: %s", config.ModelPath)
	
	// Initialize model manager
	modelManager := NewModelManager(config)
	defer modelManager.Cleanup()
	
	// Scan for Death Pantheon models
	models := modelManager.ScanModels()
	log.Printf("[ReapGate] Found %d Death Pantheon models", len(models))
	for _, model := range models {
		log.Printf("  [OK] %s - %s", model.Deity, model.Role)
	}
	
	// Start HTTP server
	server := NewServer(config, modelManager)
	
	// Handle graceful shutdown
	go func() {
		sigChan := make(chan os.Signal, 1)
		signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
		<-sigChan
		
		log.Println("[ReapGate] Shutting down gracefully...")
		modelManager.Cleanup()
		os.Exit(0)
	}()
	
	// Start server
	addr := fmt.Sprintf("%s:%s", config.Host, config.Port)
	log.Printf("[ReapGate] Server listening on http://%s", addr)
	log.Printf("[ReapGate] API endpoint: http://%s/v1/chat/completions", addr)
	log.Printf("[ReapGate] Health check: http://%s/health", addr)
	log.Printf("[ReapGate] Models list: http://%s/v1/models", addr)
	log.Println("[ReapGate] Press Ctrl+C to stop")
	
	if err := server.Start(addr); err != nil {
		log.Fatalf("[ReapGate] Server error: %v", err)
	}
}

func printBanner() {
	banner := `
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     ██████╗ ███████╗ █████╗ ██████╗  ██████╗  █████╗    ║
║     ██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝ ██╔══██╗   ║
║     ██████╔╝█████╗  ███████║██████╔╝██║  ███╗███████║   ║
║     ██╔══██╗██╔══╝  ██╔══██║██╔═══╝ ██║   ██║██╔══██║   ║
║     ██║  ██║███████╗██║  ██║██║     ╚██████╔╝██║  ██║   ║
║     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝   ║
║                                                           ║
║            Death's Inference Engine v1.0.0               ║
║         Optimized for DeathAIAUS IDE                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
`
	fmt.Println(banner)
}
