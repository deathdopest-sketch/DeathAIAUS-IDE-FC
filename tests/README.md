# Tests

This folder contains test scripts and utilities for verifying the IDE functionality.

## 🧪 Test Files

### Integration Tests
- **[test_integration.py](test_integration.py)** - Comprehensive integration test suite
  - Checks Python version
  - Verifies required files exist
  - Tests dependencies
  - Validates Google Drive models
  - Checks AI components

### Phase Testing
- **[test_phase1.py](test_phase1.py)** - Phase 1 feature tests
  - Multi-file tabs
  - Syntax highlighting
  - Keyboard shortcuts
  - Search & replace
  - AI chat integration

### Utilities
- **[MODEL_TOOLS.py](MODEL_TOOLS.py)** - Model management utilities
  - Model detection
  - Model validation
  - Configuration helpers

## 🚀 Running Tests

### Quick Test (Recommended)
```bash
# From project root
python tests/test_integration.py
```

### Run All Tests
```bash
# Test integration
python tests/test_integration.py

# Test Phase 1 features
python tests/test_phase1.py
```

## ✅ What Tests Check

### System Requirements
- ✅ Python 3.8+ installed
- ✅ Required packages available
- ✅ Core files present

### File Structure
- ✅ Main IDE files exist
- ✅ Component files present
- ✅ Documentation available

### AI Components
- ✅ Model server components
- ✅ AI chat integration
- ✅ Inline suggestions system
- ✅ Model detection

### Google Drive Models
- ✅ G: drive accessible (if available)
- ✅ .gguf models detected
- ✅ Model paths valid

## 📊 Expected Output

### Successful Test Run
```
[+] Python 3.13.0 (OK)
[+] Required files present (OK)
[+] All dependencies installed (OK)
[+] Google Drive: 20+ models found (OK)
[+] AI components verified (OK)

✅ All tests passed!
```

### Failed Test Example
```
[!] Python version too old: 3.7.0
[!] Missing dependency: tkinter
[!] Missing file: deathaius_ide_fc.py

❌ Some tests failed - see errors above
```

## 🔧 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "File not found" errors
- Make sure you're running from project root
- Check that all files are present

### Google Drive test fails
- Normal if G: drive not mounted
- IDE will still work, just no auto-detected models

## 💡 Before Launching IDE

Always run tests first to ensure everything is set up correctly:
```bash
python tests/test_integration.py
```

If all tests pass, you're ready to launch:
```bash
python deathaius_ide_fc.py
```

## 📖 More Info

- **[Requirements](../requirements.txt)** - Dependencies list
- **[Getting Started](../docs/getting-started/)** - Setup guides
- **[Development Docs](../docs/development/)** - Technical details
