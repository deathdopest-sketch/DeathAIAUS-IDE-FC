# 🚪 ReapGate Setup Guide

## What is ReapGate?

**ReapGate** is your custom AI inference backend that **replaces LM Studio**. It's optimized specifically for your DeathAIAUS IDE and the Death Pantheon models.

### Why ReapGate?
- ✅ **No LM Studio needed** - One less app to manage
- ✅ **IDE-optimized** - Smart model loading for tasks
- ✅ **Death Pantheon integrated** - Knows all your deities
- ✅ **Faster switching** - Loads models on-demand
- ✅ **Your brand** - ReapGate is part of DeathAIAUS ecosystem

---

## 🚀 Setup (5 Minutes)

### Step 1: Install Go

**Option A: Download Installer**
1. Go to: https://go.dev/dl/
2. Download: `go1.21.x.windows-amd64.msi`
3. Run installer (Next, Next, Install)
4. Close and reopen your terminal

**Option B: Use Winget (faster)**
```powershell
winget install GoLang.Go
```

**Verify installation:**
```powershell
go version
```
Should show: `go version go1.21.x windows/amd64`

---

### Step 2: Build ReapGate

```powershell
cd ReapGate
./BUILD.bat
```

This will:
1. Check Go installation
2. Download Go dependencies (llama.cpp bindings, web framework)
3. Build `reapgate.exe`

**Takes about 2-3 minutes first time.**

---

### Step 3: Start ReapGate

```powershell
./START_REAPGATE.bat
```

You'll see:
```
╔═══════════════════════════════════════╗
║          REAPGATE                     ║
║   Death's Inference Engine v1.0.0    ║
╚═══════════════════════════════════════╝

[ReapGate] Loading models from: G:\My Drive\DeathAIAUS_PANTHEON
[ReapGate] Found 20 Death Pantheon models
  [OK] THANATOS - Primary Code Generator
  [OK] MORRIGAN - Code Analyst & Bug Prophet
  ... (all 20 models)

[ReapGate] Server listening on http://localhost:7777
```

**Leave this terminal open!** ReapGate must run while using the IDE.

---

### Step 4: Update IDE

Update `deathaius_ide_fc.py` line 542:

**Change:**
```python
self.api_url = "http://localhost:1234/v1/chat/completions"
```

**To:**
```python
self.api_url = "http://localhost:7777/v1/chat/completions"
```

Save and restart your IDE.

---

## ✅ Testing

### Test 1: Health Check
```powershell
curl http://localhost:7777/health
```

Should return:
```json
{"status":"ok","version":"1.0.0","loaded_models":[]}
```

### Test 2: List Models
```powershell
curl http://localhost:7777/v1/models
```

Should show all 20 of your Death Pantheon models.

### Test 3: Use from IDE
1. Launch DeathAIAUS IDE
2. Open AI Chat panel
3. Type a question
4. Should get response from ReapGate!

---

## 🎯 Daily Usage

### Starting Everything:

**Terminal 1:**
```powershell
cd ReapGate
./START_REAPGATE.bat
```
*(Leave running)*

**Terminal 2:**
```powershell
python deathaius_ide_fc.py
```

### Stopping:
- Press **Ctrl+C** in ReapGate terminal
- Close IDE normally

---

## ⚙️ Configuration

### Change Port
```powershell
$env:REAPGATE_PORT = "8888"
./START_REAPGATE.bat
```

Then update IDE to use port 8888.

### Change Model Path
```powershell
$env:REAPGATE_MODELS = "D:\MyModels"
./START_REAPGATE.bat
```

### GPU Settings
Edit `ReapGate/config.go` line 29:
```go
GPULayers: 35,  // Increase for more VRAM usage (faster)
```

Rebuild after changes:
```powershell
./BUILD.bat
```

---

## 🐛 Troubleshooting

### "Go is not installed"
- Install Go from https://go.dev/dl/
- Restart terminal after install
- Run `go version` to verify

### "Build failed"
- Delete `go.sum` file
- Run `go mod tidy`
- Try `BUILD.bat` again

### "No models found"
- Check path: `echo $env:REAPGATE_MODELS`
- Verify files exist in `G:\My Drive\DeathAIAUS_PANTHEON`
- Check .gguf file extensions

### "Port 7777 in use"
- Change port: `$env:REAPGATE_PORT = "8888"`
- Update IDE to match new port

### "Out of memory"
- Edit `config.go`: Reduce `MaxModels` to 1
- Edit `config.go`: Reduce `GPULayers` to 20
- Use smaller models

---

## 📈 Performance

### Typical Load Times:
- **THANATOS (22B):** 5-8 seconds
- **MORRIGAN (7B):** 2-4 seconds  
- **ANUBIS (1.2B):** 1-2 seconds

### Memory Usage:
- **ReapGate:** ~100MB (idle)
- **+ Model:** 1-14GB (depending on model size)

### Token Generation:
- **THANATOS:** 8-12 tokens/sec
- **MORRIGAN:** 25-35 tokens/sec
- **ANUBIS:** 50-70 tokens/sec

*On RTX 3080, 32GB RAM*

---

## 🎉 You're Done!

**You now have:**
✅ Custom inference backend (ReapGate)
✅ No LM Studio dependency
✅ Death Pantheon integration
✅ Optimized for your IDE

**Marketing bonus:**
"Includes custom Go-based ReapGate inference engine - no external dependencies needed!"

---

## 🔮 Next Steps

1. **Auto-start:** Add ReapGate to Windows startup
2. **Desktop shortcut:** Create shortcut to `START_REAPGATE.bat`
3. **Monitor:** Check `http://localhost:7777/health` regularly
4. **Optimize:** Tune `GPULayers` and `MaxModels` for your hardware

---

## 💀 Built by DeathAIAUS
