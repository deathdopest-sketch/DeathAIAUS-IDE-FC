#!/usr/bin/env python3
"""
Test DeathAIAUS Backend
"""

import requests
import time

def test_backend():
    print("Testing DeathAIAUS Backend...")
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8888/health", timeout=5)
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Backend: {data.get('backend', 'Unknown')}")
            print(f"Models: {data.get('models_available', 0)}")
            print(f"Current model: {data.get('current_model', 'None')}")
        else:
            print(f"Health check failed: {response.text}")
    except Exception as e:
        print(f"Health check error: {e}")
    
    try:
        # Test models endpoint
        response = requests.get("http://localhost:8888/v1/models", timeout=5)
        print(f"Models endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data.get('data', []))} models")
        else:
            print(f"Models endpoint failed: {response.text}")
    except Exception as e:
        print(f"Models endpoint error: {e}")

if __name__ == "__main__":
    test_backend()
