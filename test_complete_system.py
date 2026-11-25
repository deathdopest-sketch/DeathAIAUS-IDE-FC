#!/usr/bin/env python3
"""
Complete System Test for DeathAIAUS IDE FC with Python Backend
"""

import requests
import time
import json

def test_backend():
    """Test DeathAIAUS Backend"""
    print("=" * 60)
    print("TESTING DEATHAIAUS BACKEND")
    print("=" * 60)
    
    try:
        # Health check
        response = requests.get("http://localhost:8888/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"Backend: {health_data.get('backend', 'Unknown')}")
            print(f"Models Available: {health_data.get('models_available', 0)}")
            print(f"Current Model: {health_data.get('current_model', 'None')}")
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Backend not running: {e}")
        return False
    
    try:
        # Models list
        response = requests.get("http://localhost:8888/v1/models", timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            models = models_data.get('data', [])
            print(f"Found {len(models)} models")
            
            # Show first few models
            for i, model in enumerate(models[:5]):
                print(f"   {i+1}. {model.get('name', 'Unknown')} ({model.get('tier', 'Unknown')})")
            
            if len(models) > 5:
                print(f"   ... and {len(models) - 5} more models")
        else:
            print(f"Models list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Models list error: {e}")
        return False
    
    return True

def test_chat_completion():
    """Test chat completion"""
    print("\n" + "=" * 60)
    print("TESTING CHAT COMPLETION")
    print("=" * 60)
    
    try:
        payload = {
            "model": "MINOR_DEITIES/IZANAMI/IZANAMI-DeathAIAUS-1.5B-Q4_0.gguf",
            "messages": [
                {"role": "user", "content": "Hello! Can you help me write a simple Python function?"}
            ],
            "temperature": 0.7,
            "max_tokens": 100,
            "stream": False
        }
        
        print("Sending test message...")
        response = requests.post("http://localhost:8888/v1/chat/completions", 
                               json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"AI Response: {content[:100]}...")
                return True
            else:
                print("No response generated")
                return False
        else:
            print(f"Chat completion failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Chat completion error: {e}")
        return False

def test_model_loading():
    """Test model loading"""
    print("\n" + "=" * 60)
    print("TESTING MODEL LOADING")
    print("=" * 60)
    
    try:
        # Try to load a different model
        payload = {"model": "MINOR_DEITIES/ANUBIS/ANUBIS-DeathAIAUS-1.2B-Q8_0.gguf"}
        
        print("Loading ANUBIS model...")
        response = requests.post("http://localhost:8888/v1/models/load", 
                               json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Model loaded: {result.get('message', 'Success')}")
            
            # Check current model
            response = requests.get("http://localhost:8888/v1/models/current", timeout=5)
            if response.status_code == 200:
                current = response.json()
                print(f"Current model: {current.get('model_id', 'Unknown')}")
                return True
            else:
                print("Could not get current model")
                return False
        else:
            print(f"Model loading failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Model loading error: {e}")
        return False

def test_pantheon_info():
    """Test Pantheon information"""
    print("\n" + "=" * 60)
    print("TESTING PANTHEON INFO")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:8888/pantheon", timeout=5)
        if response.status_code == 200:
            pantheon_data = response.json()
            pantheon = pantheon_data.get('pantheon', {})
            recommendations = pantheon_data.get('usage_recommendations', {})
            
            print(f"Pantheon models: {len(pantheon)}")
            print(f"Workflow recommendations: {len(recommendations)}")
            
            # Show some recommendations
            for workflow, info in list(recommendations.items())[:3]:
                primary = info.get('primary', [])
                print(f"   {workflow}: {', '.join(primary[:2])}")
            
            return True
        else:
            print(f"Pantheon info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Pantheon info error: {e}")
        return False

def main():
    """Run all tests"""
    print("DEATHAIAUS IDE FC - COMPLETE SYSTEM TEST")
    print("Testing Python Backend Integration")
    print("=" * 60)
    
    # Wait for backend to be ready
    print("Waiting for backend to be ready...")
    time.sleep(2)
    
    tests = [
        ("Backend Health", test_backend),
        ("Chat Completion", test_chat_completion),
        ("Model Loading", test_model_loading),
        ("Pantheon Info", test_pantheon_info)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"{test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\nALL TESTS PASSED! DeathAIAUS Backend is working perfectly!")
        print("Ready to use with DeathAIAUS IDE FC")
    else:
        print(f"\n{len(results) - passed} tests failed. Check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
