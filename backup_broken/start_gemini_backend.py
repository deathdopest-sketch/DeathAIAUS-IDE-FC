#!/usr/bin/env python3
"""
Gemini-Compatible Backend Launcher
=================================

Launcher script for the Gemini-Compatible Backend that:
1. Checks dependencies
2. Verifies DeathAIAUS backend is running
3. Starts the Gemini-Compatible Backend
4. Provides health monitoring

Author: DeathAIAUS
Copyright: DeathAIAUS 2025
"""

import os
import sys
import time
import logging
import argparse
import requests
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/gemini_launcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

def check_dependencies():
    """Check if required dependencies are installed"""
    logger.info("Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"[OK] {package} is installed")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"[ERROR] {package} is missing")
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        logger.error("Install with: pip install " + " ".join(missing_packages))
        return False
    
    logger.info("All dependencies are installed")
    return True

def check_deathaiaus_backend(url: str = "http://localhost:8889", timeout: int = 5):
    """Check if DeathAIAUS backend is running"""
    logger.info(f"Checking DeathAIAUS backend at {url}...")
    
    try:
        response = requests.get(f"{url}/health", timeout=timeout)
        if response.status_code == 200:
            logger.info("[OK] DeathAIAUS backend is running")
            return True
        else:
            logger.error(f"[ERROR] DeathAIAUS backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("[ERROR] Cannot connect to DeathAIAUS backend")
        logger.error("Make sure DeathAIAUS backend is running on port 8889")
        return False
    except requests.exceptions.Timeout:
        logger.error("[ERROR] DeathAIAUS backend connection timeout")
        return False
    except Exception as e:
        logger.error(f"[ERROR] Error checking DeathAIAUS backend: {e}")
        return False

def check_port_available(port: int, host: str = "127.0.0.1"):
    """Check if port is available"""
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            logger.error(f"[ERROR] Port {port} is already in use")
            return False
        else:
            logger.info(f"[OK] Port {port} is available")
            return True
    except Exception as e:
        logger.error(f"[ERROR] Error checking port {port}: {e}")
        return False

def find_free_port(start_port: int = 8888, max_attempts: int = 100):
    """Find a free port starting from start_port"""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result != 0:
                logger.info(f"Found free port: {port}")
                return port
        except:
            continue
    
    raise RuntimeError(f"No free ports found in range {start_port}-{start_port + max_attempts}")

def start_gemini_backend(host: str = "127.0.0.1", port: int = 8888, 
                        deathaiaus_url: str = "http://localhost:8889"):
    """Start the Gemini-Compatible Backend"""
    logger.info("Starting Gemini-Compatible Backend...")
    
    try:
        # Import and start the backend
        from gemini_compatible_backend import GeminiCompatibleBackend
        
        backend = GeminiCompatibleBackend(deathaiaus_url)
        backend.start(host, port)
        
    except ImportError as e:
        logger.error(f"✗ Cannot import gemini_compatible_backend: {e}")
        logger.error("Make sure gemini_compatible_backend.py is in the current directory")
        return False
    except Exception as e:
        logger.error(f"✗ Error starting Gemini-Compatible Backend: {e}")
        return False

def monitor_health(port: int = 8888, interval: int = 30):
    """Monitor backend health"""
    logger.info(f"Starting health monitoring (checking every {interval}s)...")
    
    while True:
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Health check: {data['status']} - {data['sessions']} sessions")
            else:
                logger.warning(f"Health check failed: status {response.status_code}")
        except Exception as e:
            logger.error(f"Health check error: {e}")
        
        time.sleep(interval)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Gemini-Compatible Backend Launcher")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8888, help="Port to bind to")
    parser.add_argument("--deathaiaus-url", default="http://localhost:8889", 
                       help="URL of DeathAIAUS backend")
    parser.add_argument("--check-only", action="store_true", 
                       help="Only check dependencies and backend, don't start")
    parser.add_argument("--monitor", action="store_true", 
                       help="Start health monitoring after backend starts")
    parser.add_argument("--find-port", action="store_true", 
                       help="Find a free port if specified port is busy")
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("Gemini-Compatible Backend Launcher")
    logger.info("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Dependency check failed. Exiting.")
        sys.exit(1)
    
    # Check DeathAIAUS backend
    if not check_deathaiaus_backend(args.deathaiaus_url):
        logger.error("DeathAIAUS backend check failed. Exiting.")
        sys.exit(1)
    
    # Check port availability
    if not check_port_available(args.port, args.host):
        if args.find_port:
            try:
                args.port = find_free_port(args.port)
                logger.info(f"Using port {args.port} instead")
            except RuntimeError as e:
                logger.error(f"Could not find free port: {e}")
                sys.exit(1)
        else:
            logger.error("Port check failed. Use --find-port to find alternative.")
            sys.exit(1)
    
    if args.check_only:
        logger.info("All checks passed. Exiting (check-only mode).")
        return
    
    # Start backend
    logger.info("All checks passed. Starting Gemini-Compatible Backend...")
    
    try:
        if args.monitor:
            # Start monitoring in background
            import threading
            monitor_thread = threading.Thread(
                target=monitor_health, 
                args=(args.port, 30),
                daemon=True
            )
            monitor_thread.start()
        
        start_gemini_backend(args.host, args.port, args.deathaiaus_url)
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
