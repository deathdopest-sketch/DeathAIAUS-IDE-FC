#!/usr/bin/env python3
"""
DeathAIAUS Backend Launcher
===========================

Simple launcher script for the DeathAIAUS Python Backend.
This script handles startup, error checking, and provides a clean interface.

Author: DeathAIAUS
Copyright: DeathAIAUS 2025
"""

import os
import sys
import time
import subprocess
import threading
import requests
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import llama_cpp
        print("All dependencies are installed")
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please run: pip install llama-cpp-python[server]")
        return False

def check_pantheon_path():
    """Check if Pantheon models directory exists"""
    pantheon_path = Path(r"G:\My Drive\DeathAIAUS_PANTHEON")
    if pantheon_path.exists():
        print(f"Pantheon directory found: {pantheon_path}")
        return True
    else:
        print(f"Pantheon directory not found: {pantheon_path}")
        print("Please check if Google Drive is mounted and accessible")
        return False

def check_port_available(port=8888):
    """Check if port is available"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=1)
        print(f"Port {port} is already in use")
        return False
    except:
        print(f"Port {port} is available")
        return True

def start_backend():
    """Start the DeathAIAUS Backend"""
    print("Starting DeathAIAUS Backend...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check Pantheon path
    if not check_pantheon_path():
        return False
    
    # Check port availability
    if not check_port_available():
        print("Try: python start_deathaiaus_backend.py --port 8889")
        return False
    
    # Start backend
    try:
        print("\nLaunching DeathAIAUS Backend...")
        print("Server will be available at: http://localhost:8888")
        print("Health check: http://localhost:8888/health")
        print("Models list: http://localhost:8888/v1/models")
        print("Chat API: http://localhost:8888/v1/chat/completions")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)
        
        # Import and run backend
        from DeathAIAUS_Backend import DeathAIAUSBackend
        
        backend = DeathAIAUSBackend()
        backend.run(host="localhost", port=8888)
        
    except KeyboardInterrupt:
        print("\n\nDeathAIAUS Backend stopped by user")
        return True
    except Exception as e:
        print(f"\nError starting backend: {e}")
        return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DeathAIAUS Backend Launcher")
    parser.add_argument("--port", type=int, default=8888, help="Port to use (default: 8888)")
    parser.add_argument("--check-only", action="store_true", help="Only check dependencies and exit")
    
    args = parser.parse_args()
    
    print("DeathAIAUS Backend Launcher")
    print("=" * 50)
    
    if args.check_only:
        print("Checking system requirements...")
        deps_ok = check_dependencies()
        pantheon_ok = check_pantheon_path()
        port_ok = check_port_available(args.port)
        
        if deps_ok and pantheon_ok and port_ok:
            print("\nAll checks passed! System is ready.")
            return 0
        else:
            print("\nSome checks failed. Please fix the issues above.")
            return 1
    
    # Start backend
    success = start_backend()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
