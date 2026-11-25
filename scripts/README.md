# Scripts

This folder contains all batch (.bat) and PowerShell (.ps1) scripts for launching and managing the IDE.

## 🚀 Launch Scripts

### Quick Launch (Recommended)
- **[LAUNCH_IDE.bat](LAUNCH_IDE.bat)** - One-click launcher, no console window, instant start

### Alternative Launchers
- **[launch.bat](launch.bat)** - Original launcher with brief message
- **[QUICK_START.bat](QUICK_START.bat)** - Quick start script

### Desktop Shortcut Creators
- **[CREATE_DESKTOP_SHORTCUT.bat](CREATE_DESKTOP_SHORTCUT.bat)** - Creates desktop shortcut automatically
- **[DESKTOP_SHORTCUT_SIMPLE.bat](DESKTOP_SHORTCUT_SIMPLE.bat)** - Simple desktop shortcut creation
- **[MAKE_SHORTCUT.ps1](MAKE_SHORTCUT.ps1)** - PowerShell shortcut creator

## 📋 Usage

### Daily Use (Easiest)
```bash
# 1. One-time setup - create desktop shortcut
CREATE_DESKTOP_SHORTCUT.bat

# 2. Daily use - double-click the desktop shortcut
```

### Direct Launch
```bash
# From this scripts folder
LAUNCH_IDE.bat

# Or use the quick start
QUICK_START.bat
```

### From Root Directory
```bash
# Launch from project root
python deathaius_ide_fc.py

# Or the integrated version
python deathaius_ide_integrated.py
```

## 🎯 Recommended Setup

1. **Run once:** `CREATE_DESKTOP_SHORTCUT.bat`
2. **Daily:** Double-click the desktop shortcut
3. **Optional:** Pin shortcut to taskbar for even faster access

## ⚙️ Customization

### Change Python Path
Edit LAUNCH_IDE.bat if Python isn't in PATH:
```batch
start "" "C:\Python313\pythonw.exe" deathaius_ide_fc.py
```

### Add Keyboard Shortcut
1. Right-click desktop shortcut
2. Properties → Shortcut key
3. Press desired key combo (e.g., Ctrl+Alt+D)

### Auto-Start on Boot
1. Press Win+R, type `shell:startup`
2. Copy desktop shortcut to that folder

## 🔧 Troubleshooting

### "Python not found"
- Install Python 3.8+ from python.org
- Or edit LAUNCH_IDE.bat with full Python path

### Console window stays open
- Use LAUNCH_IDE.bat instead of launch.bat
- It uses pythonw.exe which runs without console

### Shortcut creation fails
- Run CREATE_DESKTOP_SHORTCUT.bat as Administrator
- Or manually create shortcut pointing to LAUNCH_IDE.bat

## 📖 More Info

See **[docs/getting-started/LAUNCHER_README.md](../docs/getting-started/LAUNCHER_README.md)** for detailed launcher documentation.
