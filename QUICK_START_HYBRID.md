# 🚀 DeathAIAUS Hybrid IDE - Quick Start

## Instant Launch

```bash
python DeathAIAUS_Launcher.py
```

**That's it!** The launcher handles everything automatically.

---

## What Happens

1. ✅ Branded splash screen appears
2. ✅ Checks all components
3. ✅ Starts DeathAIAUS Backend (if not running)
4. ✅ Waits for backend ready (~5 seconds)
5. ✅ Launches hybrid IDE
6. ✅ Opens modern React UI in native window

---

## First Time Setup (Already Done!)

All prerequisites were checked and are ready:
- ✅ Python 3.13.7
- ✅ Node.js 22.18.0
- ✅ Windows Long Paths enabled
- ✅ WebView2 Runtime installed
- ✅ All packages installed
- ✅ React build complete
- ✅ 20 Pantheon models detected

**You're ready to go!**

---

## Test First (Optional)

Want to verify everything before launching?

```bash
python test_hybrid_ide.py
```

Expected output:
```
Testing React build...             [PASS]
Testing Python packages...         [PASS]
Testing backend availability...    [PASS]
Testing Pantheon models...         [PASS] (20 models found)
Testing bridge file...             [PASS]
Testing hybrid IDE file...         [PASS]

Results: 6/6 tests passed
Status: ALL TESTS PASSED - Ready to launch!
```

---

## Commands Reference

### Launch IDE
```bash
# Method 1: With launcher (recommended)
python DeathAIAUS_Launcher.py

# Method 2: Direct launch
python deathaius_ide_hybrid.py

# Method 3: Double-click desktop shortcut
# (Run CREATE_DESKTOP_SHORTCUT.bat first)
```

### Test & Verify
```bash
# Full component tests
python test_hybrid_ide.py

# Quick startup test
python quick_test_hybrid.py

# Check backend health
curl http://localhost:8888/health
```

### React Development
```bash
cd ui

# Dev mode (no bridge functions)
npm run dev

# Rebuild
npm run build
```

### Backend
```bash
# Start backend manually
python start_deathaiaus_backend.py

# Check backend
curl http://localhost:8888/v1/models
```

---

## Keyboard Shortcuts (In IDE)

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | AI Composer |
| `Ctrl+Shift+M` | Session Memory |
| `Ctrl+S` | Save File |
| `Ctrl+O` | Open File Dialog |
| `Ctrl+N` | New File |
| `Ctrl+/` | Toggle Comment |
| `Ctrl+F` | Find in File |
| `Ctrl+H` | Find & Replace |

---

## Troubleshooting

### IDE won't start
```bash
# Check Python
python --version  # Should be 3.8+

# Check components
python test_hybrid_ide.py

# Check logs
type logs\launcher.log
```

### Backend not responding
```bash
# Restart backend via IDE menu:
AI > Restart Backend

# Or manually:
python start_deathaiaus_backend.py --port 8888
```

### React UI looks broken
```bash
# Rebuild React
cd ui
npm run build
cd ..

# Relaunch IDE
python DeathAIAUS_Launcher.py
```

### Models not loading
1. Check models exist: `G:\My Drive\DeathAIAUS_PANTHEON\*.gguf`
2. Check backend: http://localhost:8888/v1/models
3. Try loading manually in IDE: AI > Model Manager

---

## File Locations

### Core Files
- **Main:** `deathaius_ide_hybrid.py`
- **Launcher:** `DeathAIAUS_Launcher.py`
- **Bridge:** `webview_bridge.py`
- **Backend:** `DeathAIAUS_Backend.py`

### UI
- **React Source:** `ui/src/`
- **Built UI:** `ui/dist/`
- **Bridge:** `ui/bridge.ts`
- **Services:** `ui/services/`

### Models
- **Location:** `G:\My Drive\DeathAIAUS_PANTHEON\`
- **Config:** `death_pantheon.json`

### Logs
- **Launcher:** `logs/launcher.log`
- **Backend:** Console output

---

## Support

### Documentation
- `HYBRID_IDE_COMPLETE.md` - Full implementation details
- `AUTOMATED_BUILD_COMPLETE.md` - Build summary
- `DEATHAIAUS_IDE_FEATURES.md` - All features
- This file - Quick start

### Contact
- **Website:** https://deathaiaustralia.com.au/
- **Discord:** https://discord.gg/RMjAtWb4
- **Email:** deathdopest@gmail.com

---

## What's Next?

### Using the IDE
1. Launch: `python DeathAIAUS_Launcher.py`
2. Create or open a project
3. Start coding with AI assistance
4. Use Task Planner for complex projects
5. Let the AI help you build!

### Advanced Features
- Configure workflow models (AI > Configure Workflow Models)
- View session memory (AI > Session Memory)
- Check performance stats (AI > Model Manager)
- Use native file dialogs (File > Open/Save)

---

**Ready?** Just run:

```bash
python DeathAIAUS_Launcher.py
```

🎉 **Enjoy your hybrid IDE!**

