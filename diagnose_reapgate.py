#!/usr/bin/env python3
"""
ReapGate Diagnostic Script
Tests ReapGate connection and model loading
"""

import requests
import json
import os

def test_reapgate():
    print("ReapGate Diagnostic Tool")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing ReapGate Health...")
    try:
        response = requests.get("http://localhost:7777/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   [OK] Health OK: {health_data}")
        else:
            print(f"   [ERROR] Health failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"   [ERROR] Cannot connect to ReapGate: {e}")
        print("   [TIP] Try: AI > Restart ReapGate or run restart_reapgate.bat")
        return
    
    # Test 2: Models List
    print("\n2. Testing Models List...")
    try:
        response = requests.get("http://localhost:7777/v1/models", timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            models = models_data.get('data', [])
            print(f"   [OK] Found {len(models)} models")
            
            if models:
                print("   Available models:")
                for i, model in enumerate(models[:3]):  # Show first 3
                    model_id = model['id']
                    model_name = model_id.split('\\')[-1] if '\\' in model_id else model_id
                    print(f"      {i+1}. {model_name}")
                
                # Test 3: Model Loading
                print("\n3. Testing Model Loading...")
                test_model = models[0]['id']
                print(f"   Testing model: {test_model.split('\\')[-1]}")
                
                payload = {
                    "model": test_model,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                }
                
                try:
                    response = requests.post(
                        "http://localhost:7777/v1/chat/completions",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if 'choices' in result and len(result['choices']) > 0:
                            print("   [OK] Model loaded and responded successfully!")
                            print(f"   Response: {result['choices'][0]['message']['content'][:50]}...")
                        else:
                            print("   [WARNING] Model loaded but no response generated")
                    else:
                        print(f"   [ERROR] Model loading failed: {response.status_code}")
                        print(f"   Error: {response.text}")
                        
                except Exception as e:
                    print(f"   [ERROR] Model loading error: {e}")
            else:
                print("   [WARNING] No models found")
                print("   [TIP] Check if models exist in G:\\My Drive\\DeathAIAUS_PANTHEON")
        else:
            print(f"   [ERROR] Models list failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   [ERROR] Models list error: {e}")
    
    # Test 4: File System Check
    print("\n4. Checking Model Files...")
    model_path = "G:\\My Drive\\DeathAIAUS_PANTHEON"
    if os.path.exists(model_path):
        print(f"   [OK] Model directory exists: {model_path}")
        try:
            gguf_files = []
            for root, dirs, files in os.walk(model_path):
                for file in files:
                    if file.endswith('.gguf'):
                        gguf_files.append(os.path.join(root, file))
            
            print(f"   Found {len(gguf_files)} .gguf files")
            if gguf_files:
                print("   Sample files:")
                for i, file in enumerate(gguf_files[:3]):
                    print(f"      {i+1}. {os.path.basename(file)}")
            else:
                print("   [WARNING] No .gguf files found")
        except Exception as e:
            print(f"   [ERROR] Error scanning files: {e}")
    else:
        print(f"   [ERROR] Model directory not found: {model_path}")
        print("   [TIP] Check if Google Drive is mounted and accessible")
    
    print("\n" + "=" * 50)
    print("Diagnostic complete!")

if __name__ == "__main__":
    test_reapgate()
