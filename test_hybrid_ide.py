"""
Test script for Hybrid IDE setup
Verifies all components are ready
"""

import sys
import subprocess
from pathlib import Path
import requests

def test_react_build():
    """Test if React is built"""
    print("Testing React build...")
    dist = Path('ui/dist')
    if not dist.exists():
        print("  [FAIL] ui/dist not found")
        return False
    
    index_html = dist / 'index.html'
    if not index_html.exists():
        print("  [FAIL] ui/dist/index.html not found")
        return False
    
    # Check for CDN dependencies (should be none)
    with open(index_html, 'r') as f:
        content = f.read()
        if 'https://' in content and 'cdn' in content.lower():
            print("  [WARN] CDN links detected in index.html")
        
    print("  [PASS] React build exists")
    return True

def test_python_packages():
    """Test if required packages are installed"""
    print("Testing Python packages...")
    required = ['webview', 'flask', 'flask_cors', 'psutil', 'requests']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"  [FAIL] Missing packages: {', '.join(missing)}")
        return False
    
    print("  [PASS] All required packages installed")
    return True

def test_backend_available():
    """Test if backend can be started"""
    print("Testing backend availability...")
    backend_script = Path('DeathAIAUS_Backend.py')
    
    if not backend_script.exists():
        print("  [WARN] DeathAIAUS_Backend.py not found (AI features may not work)")
        return True  # Not critical
    
    print("  [PASS] Backend script found")
    return True

def test_pantheon_models():
    """Test if Pantheon models are accessible"""
    print("Testing Pantheon models...")
    pantheon_dir = Path('G:/My Drive/DeathAIAUS_PANTHEON')
    
    if not pantheon_dir.exists():
        print("  [WARN] Pantheon directory not found (AI features may not work)")
        return True  # Not critical
    
    gguf_files = list(pantheon_dir.rglob('*.gguf'))
    print(f"  [INFO] Found {len(gguf_files)} GGUF models")
    
    if gguf_files:
        print("  [PASS] Pantheon models accessible")
    else:
        print("  [WARN] No GGUF models found")
    
    return True

def test_bridge_file():
    """Test if bridge file exists"""
    print("Testing bridge file...")
    bridge = Path('webview_bridge.py')
    
    if not bridge.exists():
        print("  [FAIL] webview_bridge.py not found")
        return False
    
    print("  [PASS] Bridge file exists")
    return True

def test_hybrid_ide():
    """Test if hybrid IDE file exists"""
    print("Testing hybrid IDE file...")
    hybrid = Path('deathaius_ide_hybrid.py')
    
    if not hybrid.exists():
        print("  [FAIL] deathaius_ide_hybrid.py not found")
        return False
    
    print("  [PASS] Hybrid IDE file exists")
    return True

def main():
    print("=" * 60)
    print("DeathAIAUS Hybrid IDE - Component Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_react_build,
        test_python_packages,
        test_backend_available,
        test_pantheon_models,
        test_bridge_file,
        test_hybrid_ide
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  [ERROR] {e}")
            results.append(False)
        print()
    
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if all(results):
        print("Status: ALL TESTS PASSED - Ready to launch!")
    elif passed >= total - 2:
        print("Status: MOSTLY READY - Some warnings, but should work")
    else:
        print("Status: NOT READY - Fix errors before launching")
    
    print("=" * 60)
    
    return all(results)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

