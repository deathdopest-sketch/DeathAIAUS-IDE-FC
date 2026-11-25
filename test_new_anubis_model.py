#!/usr/bin/env python3
"""
Test New ANUBIS Model
====================

This script tests the newly converted ANUBIS model to ensure it works
properly with the simple_backend.py.

Author: DeathAIAUS
Date: 2025
"""

import os
import sys
import time
import requests
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_new_anubis_model.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_gguf_file():
    """Check if the new GGUF file exists"""
    gguf_file = "DeathAIAUS-Anubis-Phi-1.5-Q8_0.gguf"
    
    if not os.path.exists(gguf_file):
        logger.error(f"GGUF file not found: {gguf_file}")
        logger.error("Please run the conversion process first")
        return False
    
    file_size = os.path.getsize(gguf_file) / (1024**3)  # GB
    logger.info(f"Found GGUF file: {gguf_file} ({file_size:.2f} GB)")
    return True

def start_backend():
    """Start the simple_backend.py"""
    logger.info("Starting simple_backend.py...")
    
    try:
        # Start backend in background
        process = subprocess.Popen(
            [sys.executable, "simple_backend.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for startup
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            logger.info("Backend started successfully")
            return process
        else:
            stdout, stderr = process.communicate()
            logger.error(f"Backend failed to start. STDOUT: {stdout}")
            logger.error(f"STDERR: {stderr}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to start backend: {e}")
        return None

def test_backend_health():
    """Test backend health endpoint"""
    logger.info("Testing backend health...")
    
    try:
        response = requests.get("http://localhost:8888/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Backend health: {data}")
            return True
        else:
            logger.error(f"Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Health check failed: {e}")
        return False

def test_model_loading():
    """Test model loading"""
    logger.info("Testing model loading...")
    
    try:
        response = requests.get("http://localhost:8888/v1/models/current", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Current model: {data}")
            return True
        else:
            logger.error(f"Model loading failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Model loading test failed: {e}")
        return False

def test_text_generation():
    """Test text generation"""
    logger.info("Testing text generation...")
    
    test_prompts = [
        "Hello, how are you?",
        "Write a simple Python function to add two numbers:",
        "What is the capital of Australia?"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        logger.info(f"Test {i}: {prompt}")
        
        try:
            response = requests.post(
                "http://localhost:8888/v1/chat/completions",
                json={
                    "model": "ANUBIS-PHI-NEW",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 100,
                    "temperature": 0.7
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                logger.info(f"Response: {content[:200]}...")
            else:
                logger.error(f"Generation failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Generation test failed: {e}")
            return False
        
        # Small delay between tests
        time.sleep(2)
    
    return True

def stop_backend(process):
    """Stop the backend process"""
    if process:
        logger.info("Stopping backend...")
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
        logger.info("Backend stopped")

def main():
    """Main test function"""
    logger.info("=" * 60)
    logger.info("ANUBIS MODEL TEST - Starting")
    logger.info("=" * 60)
    
    backend_process = None
    
    try:
        # Check GGUF file exists
        if not check_gguf_file():
            logger.error("GGUF file check failed. Aborting.")
            sys.exit(1)
        
        # Start backend
        backend_process = start_backend()
        if not backend_process:
            logger.error("Failed to start backend. Aborting.")
            sys.exit(1)
        
        # Test backend health
        if not test_backend_health():
            logger.error("Backend health check failed. Aborting.")
            sys.exit(1)
        
        # Test model loading
        if not test_model_loading():
            logger.error("Model loading test failed. Aborting.")
            sys.exit(1)
        
        # Test text generation
        if not test_text_generation():
            logger.error("Text generation test failed. Aborting.")
            sys.exit(1)
        
        # Success!
        logger.info("=" * 60)
        logger.info("SUCCESS: All tests passed!")
        logger.info("The new ANUBIS model is working correctly.")
        logger.info("=" * 60)
        
        return True
        
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        stop_backend(backend_process)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
