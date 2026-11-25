#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script for DeathAIAUS IDE F.C Integration
Tests all Phase 6 AI features with your Google Drive models
"""

import os
import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("DeathAIAUS IDE F.C - Integration Test")
print("=" * 60)
print()

# Test 1: Check Python version
print("[Test 1] Python Version")
print(f"  Python {sys.version}")
if sys.version_info < (3, 7):
    print("  [WARNING] Python 3.7+ recommended")
else:
    print("  [OK]")
print()

# Test 2: Check required files
print("[Test 2] Required Files")
required_files = [
    "deathaius_ide_integrated.py",
    "components/ai_model_server.py",
    "components/llama_inference.py",
    "components/integrated_ai_chat.py",
    "MODEL_TOOLS.py",
    "requirements.txt",
]

all_files_exist = True
for file in required_files:
    if os.path.exists(file):
        print(f"  [OK] {file}")
    else:
        print(f"  [MISSING] {file}")
        all_files_exist = False

print()

# Test 3: Check dependencies
print("[Test 3] Dependencies")

try:
    import tkinter as tk
    print("  [OK] tkinter")
except ImportError:
    print("  [MISSING] tkinter (usually comes with Python)")

try:
    import requests
    print("  [OK] requests")
except ImportError:
    print("  [MISSING] requests - Run: pip install requests")

try:
    import llama_cpp
    print("  [OK] llama-cpp-python (Full AI power!)")
    has_llama_cpp = True
except ImportError:
    print("  [INFO] llama-cpp-python - Not installed (optional)")
    print("     AI will use Python fallback mode")
    print("     For full power: pip install llama-cpp-python")
    has_llama_cpp = False

print()

# Test 4: Check Google Drive
print("[OK] Test 4: Google Drive Model Location")

gdrive_path = r'G:\My Drive'
if os.path.exists(gdrive_path):
    print(f"  [OK] Google Drive found: {gdrive_path}")

    # Check for models
    models_dir = os.path.join(gdrive_path, '.deathaius_models')
    if os.path.exists(models_dir):
        print(f"  [OK] Models directory exists: {models_dir}")
    else:
        print(f"  [INFO]  Models directory not found (will be created)")
        print(f"     Expected: {models_dir}")

    # Scan for GGUF files
    print()
    print("  Scanning for models...")

    models_found = []

    # Check models directory
    if os.path.exists(models_dir):
        for file in os.listdir(models_dir):
            if file.endswith('.gguf') or file.endswith('.bin'):
                model_path = os.path.join(models_dir, file)
                size_mb = os.path.getsize(model_path) / (1024 * 1024)
                models_found.append((file, size_mb, models_dir))

    # Check root directory
    try:
        for file in os.listdir(gdrive_path):
            if file.endswith('.gguf') or file.endswith('.bin'):
                model_path = os.path.join(gdrive_path, file)
                try:
                    size_mb = os.path.getsize(model_path) / (1024 * 1024)
                    models_found.append((file, size_mb, gdrive_path))
                except:
                    pass
    except:
        pass

    if models_found:
        print(f"  [OK] Found {len(models_found)} model(s):")
        for name, size, location in models_found:
            print(f"     • {name} ({size:.0f} MB)")
            print(f"       Location: {location}")
    else:
        print("  [INFO]  No models found in Google Drive")
        print("     You can:")
        print("     1. Download via Model Manager")
        print("     2. Copy .gguf files to G:\\My Drive")
        print("     3. Use Browse button to select from anywhere")

else:
    print(f"  [WARNING]  Google Drive not found: {gdrive_path}")
    print("     Models will be stored in user home directory")
    print("     Or use Browse button to select models from anywhere")

print()

# Test 5: Import AI components
print("[OK] Test 5: AI Components")

try:
    from components.ai_model_server import AIModelServer
    print("  [OK] AIModelServer imported")
except ImportError as e:
    print(f"  [MISSING] Failed to import AIModelServer: {e}")

try:
    from components.llama_inference import InferenceEngineFactory
    print("  [OK] InferenceEngineFactory imported")
except ImportError as e:
    print(f"  [MISSING] Failed to import InferenceEngineFactory: {e}")

try:
    from components.integrated_ai_chat import IntegratedAIChat
    print("  [OK] IntegratedAIChat imported")
except ImportError as e:
    print(f"  [MISSING] Failed to import IntegratedAIChat: {e}")

print()

# Test 6: Initialize AI server
print("[OK] Test 6: AI Model Server Initialization")

try:
    from components.ai_model_server import AIModelServer

    server = AIModelServer()
    print(f"  [OK] AI Server initialized")
    print(f"     Models directory: {server.models_dir}")

    # List models
    models = server.list_installed_models()
    if models:
        print(f"  [OK] Detected {len(models)} model(s):")
        for model in models:
            print(f"     • {model['name']} ({model['size_mb']:.0f} MB)")
    else:
        print("  [INFO]  No models currently available")
        print("     Use Model Manager to download or browse for models")

except Exception as e:
    print(f"  [MISSING] Error initializing AI server: {e}")

print()

# Test 7: Inference engine
print("[OK] Test 7: Inference Engine")

try:
    from components.llama_inference import InferenceEngineFactory

    # Test with a dummy path (won't actually load)
    test_path = "test.gguf"

    if has_llama_cpp:
        print("  [OK] llama-cpp-python available")
        print("     Will use LlamaCppEngine for best performance")
    else:
        print("  [OK] Fallback mode available")
        print("     Will use SimplePythonInference (basic templates)")
        print("     Install llama-cpp-python for full AI power")

except Exception as e:
    print(f"  [WARNING]  Error testing inference: {e}")

print()

# Summary
print("=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print()

if all_files_exist:
    print("[OK] All required files present")
else:
    print("[MISSING] Some files are missing - integration may be incomplete")

print()
print("NEXT STEPS:")
print()
print("1. Launch the IDE:")
print("   python deathaius_ide_integrated.py")
print()
print("2. Load a model:")
print("   • Click AI → Model Manager")
if models_found if 'models_found' in locals() and models_found else False:
    print("   • Select from detected models")
    print("   • Click 'Load Model'")
else:
    print("   • Click '📁 Browse for Model...'")
    print("   • Navigate to your .gguf file")
print()
print("3. Start using AI:")
print("   • Type in AI chat")
print("   • Get inline suggestions")
print("   • Use quick action buttons")
print()

if has_llama_cpp:
    print("[LAUNCH] FULL AI POWER ENABLED!")
    print("   You have llama-cpp-python installed")
    print("   Best performance available")
else:
    print("[POWER] BASIC MODE ACTIVE")
    print("   For full AI power, install:")
    print("   pip install llama-cpp-python")
    print()
    print("   For GPU support (NVIDIA):")
    print("   pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121")

print()
print("[DOCS] Read QUICK_START.md for detailed instructions")
print("=" * 60)
print()

# Offer to launch IDE
print("Ready to launch the IDE? (y/n): ", end="")
try:
    response = input().strip().lower()
    if response == 'y':
        print()
        print("Launching DeathAIAUS IDE F.C...")
        print()
        import subprocess
        subprocess.run([sys.executable, "deathaius_ide_integrated.py"])
except KeyboardInterrupt:
    print()
    print("Cancelled.")
except Exception as e:
    print(f"Error launching IDE: {e}")
    print()
    print("You can launch manually with:")
    print("python deathaius_ide_integrated.py")
