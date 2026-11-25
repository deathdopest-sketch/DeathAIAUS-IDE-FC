#!/usr/bin/env python3
"""
Simple test to verify Gemini-Compatible Backend works
"""

import requests
import json

def test_gemini_backend():
    """Test the Gemini-Compatible Backend"""
    print("Testing Gemini-Compatible Backend...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8888/health", timeout=5)
        if response.status_code == 200:
            print("[OK] Health endpoint working")
            print(f"  Response: {response.json()}")
        else:
            print(f"[ERROR] Health endpoint failed: {response.status_code}")
            return False
        
        # Test simple generation
        request_data = {
            "model": "gemini-2.5-flash",
            "contents": "Hello, how are you?",
            "config": {}
        }
        
        response = requests.post(
            "http://localhost:8888/v1/models/generate",
            json=request_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] Content generation working")
            print(f"  Response: {data['text'][:100]}...")
        else:
            print(f"[ERROR] Content generation failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

def test_deathaiaus_backend():
    """Test the DeathAIAUS Backend"""
    print("\nTesting DeathAIAUS Backend...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8889/health", timeout=5)
        if response.status_code == 200:
            print("[OK] Health endpoint working")
            print(f"  Response: {response.json()}")
        else:
            print(f"[ERROR] Health endpoint failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Simple Backend Test")
    print("=" * 50)
    
    # Test DeathAIAUS backend first
    deathaiaus_ok = test_deathaiaus_backend()
    
    # Test Gemini backend
    gemini_ok = test_gemini_backend()
    
    print("\n" + "=" * 50)
    print("Test Results")
    print("=" * 50)
    print(f"DeathAIAUS Backend: {'PASS' if deathaiaus_ok else 'FAIL'}")
    print(f"Gemini Backend: {'PASS' if gemini_ok else 'FAIL'}")
    
    if deathaiaus_ok and gemini_ok:
        print("\n[SUCCESS] All tests passed! The system is working.")
    else:
        print("\n[FAILED] Some tests failed. Check the logs above.")
