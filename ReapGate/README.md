# 🚪 ReapGate - Death's Inference Engine

**Optimized AI model inference backend for DeathAIAUS IDE**

ReapGate is a high-performance Go-based inference server that loads and runs your Death Pantheon models (.gguf files) without needing LM Studio or other external tools.

---

## ✨ Features

- ✅ **REST API** - OpenAI-compatible endpoints
- ✅ **Death Pantheon Integration** - Auto-detects and names your models
- ✅ **Smart Model Management** - Loads/unloads models on demand
- ✅ **Memory Efficient** - Keeps only active models in RAM
- ✅ **GPU Acceleration** - Automatic CUDA/Metal support
- ✅ **Zero Dependencies** - Single binary executable
- ✅ **Fast Startup** - Ready in seconds
- ✅ **IDE Optimized** - Task-based model switching

---

## 🚀 Quick Start

### Step 1: Install Go

**Windows:**
```powershell
# Download and install from: https://go.dev/dl/
# Or use winget:
winget install GoLang.Go
```

**After install, verify:**
```powershell
go version
# Should show: go version go1.21.x windows/amd64
```

### Step 2: Build ReapGate

```powershell
cd ReapGate
go mod download
go build -o reapgate.exe
```

This will create `reapgate.exe` in the ReapGate folder.

### Step 3: Run ReapGate

```powershell
./reapgate.exe
```

You should see:
```
╔═══════════════════════════════════════════════════════════╗
║                     REAPGATE                              ║
║            Death's Inference Engine v1.0.0               ║
╚═══════════════════════════════════════════════════════════╝

[ReapGate] Starting Death's Inference Engine v1.0.0
[ReapGate] Loading models from: G:\My Drive\DeathAIAUS_PANTHEON
[ReapGate] Found 20 Death Pantheon models
  [OK] THANATOS - Primary Code Generator
  [OK] MORRIGAN - Code Analyst & Bug Prophet
  ... etc
[ReapGate] Server listening on http://localhost:7777
[ReapGate] Press Ctrl+C to stop
```

### Step 4: Test It

Open another terminal:
```powershell
curl http://localhost:7777/health
```

---

## 🔧 Configuration

### Environment Variables

```powershell
# Model directory (default: G:\My Drive\DeathAIAUS_PANTHEON)
$env:REAPGATE_MODELS = "C:\path\to\your\models"

# Server host (default: localhost)
$env:REAPGATE_HOST = "localhost"

# Server port (default: 7777)
$env:REAPGATE_PORT = "7777"
```

### Config File (coming soon)
`reapgate.yaml` will support advanced configuration.

---

## 📡 API Endpoints

### Health Check
```
GET http://localhost:7777/health
```

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "loaded_models": ["THANATOS", "MORRIGAN"]
}
```

### List Models
```
GET http://localhost:7777/v1/models
```

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "G:\\My Drive\\DeathAIAUS_PANTHEON\\DeathAIAUS-THANATOS-22B-Q4_K_M.gguf",
      "object": "model",
      "owned_by": "DeathAIAUS"
    }
  ]
}
```

### Chat Completion (OpenAI Compatible)
```
POST http://localhost:7777/v1/chat/completions
Content-Type: application/json

{
  "model": "THANATOS",
  "messages": [
    {"role": "system", "content": "You are a helpful coding assistant."},
    {"role": "user", "content": "Write a hello world in Python"}
  ],
  "max_tokens": 512,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "id": "reapgate-123",
  "object": "chat.completion",
  "model": "THANATOS",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Here's a hello world in Python:\n\n```python\nprint('Hello, World!')\n```"
      }
    }
  ]
}
```

### ReapGate Specific Endpoints

**Get Loaded Models:**
```
GET http://localhost:7777/reapgate/loaded
```

**Get Pantheon Info:**
```
GET http://localhost:7777/reapgate/pantheon
```

---

## 🔗 Integrate with DeathAIAUS IDE

Update IDE to use ReapGate:

In `deathaius_ide_fc.py`, change:
```python
self.api_url = "http://localhost:1234/v1/chat/completions"  # Old (LM Studio)
```

To:
```python
self.api_url = "http://localhost:7777/v1/chat/completions"  # New (ReapGate)
```

That's it! The IDE will now use ReapGate instead of LM Studio.

---

## 🎯 Model Selection

You can specify models by:

1. **Deity Name:** `"THANATOS"`, `"MORRIGAN"`, etc.
2. **Full Path:** `"G:\\My Drive\\...\\DeathAIAUS-THANATOS-22B-Q4_K_M.gguf"`
3. **Filename:** `"DeathAIAUS-THANATOS-22B-Q4_K_M.gguf"`

ReapGate will automatically find and load the correct model.

---

## ⚡ Performance Tips

### GPU Acceleration
ReapGate automatically uses your GPU if available (CUDA/Metal).

**Adjust GPU layers** (more = faster, but uses more VRAM):
```go
// In config.go, line 29:
GPULayers: 35,  // Default
// Increase to 50-60 if you have >8GB VRAM
// Decrease to 20-25 if you have <6GB VRAM
```

### Memory Management
ReapGate keeps 2 models in memory by default.

**Adjust max models:**
```go
// In config.go, line 28:
MaxModels: 2,  // Default
// Increase to 3-4 if you have >32GB RAM
// Decrease to 1 if you have <16GB RAM
```

---

## 🐛 Troubleshooting

### "Model not found"
- Check model path: `$env:REAPGATE_MODELS`
- Verify .gguf files exist
- Check spelling of model name

### "Out of memory"
- Reduce `MaxModels` in config
- Reduce `GPULayers` in config
- Use smaller models

### "Port already in use"
- Change port: `$env:REAPGATE_PORT = "8888"`
- Check if LM Studio is running on 7777

### Build Errors
- Ensure Go 1.21+ installed
- Run `go mod tidy`
- Delete `go.sum` and retry

---

## 🏗️ Building for Distribution

### Create standalone executable:
```powershell
go build -ldflags="-s -w" -o reapgate.exe
```

This creates a smaller binary with stripped symbols.

### Include with IDE:
1. Build `reapgate.exe`
2. Place in IDE root folder
3. Create `START_REAPGATE.bat`:
```batch
@echo off
start "" reapgate.exe
```
4. Users run this before launching IDE

---

## 🔮 Roadmap

**v1.1:**
- [ ] WebSocket streaming support
- [ ] Model warmup on startup
- [ ] Config file support
- [ ] Web UI for chat/model management

**v1.2:**
- [ ] Multi-model parallel processing
- [ ] Request queuing
- [ ] Performance metrics/logging
- [ ] Auto-model selection based on task

**v2.0:**
- [ ] Built-in chat UI
- [ ] Model quantization on-the-fly
- [ ] Distributed inference (multi-GPU)
- [ ] Plugin system

---

## 📊 Performance Benchmarks

| Model | Load Time | Memory | Tokens/sec |
|-------|-----------|--------|------------|
| THANATOS (22B) | 8s | 13GB | 8-12 |
| MORRIGAN (7B) | 3s | 5GB | 25-35 |
| ANUBIS (1.2B) | 1s | 2GB | 50-70 |

*Tested on RTX 3080 (10GB VRAM), 32GB RAM*

---

## 🎓 Learn More

- [Go Documentation](https://go.dev/doc/)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)
- [Gin Web Framework](https://gin-gonic.com/)

---

## 📜 License

Copyright © 2025 DeathAIAUS. All rights reserved.

---

**Built with 💀 by DeathAIAUS**
