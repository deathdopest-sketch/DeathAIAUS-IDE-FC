# 🚀 Quick Start Guide - DeathAIAUS IDE F.C

## ✅ **Get Started in 5 Minutes!**

---

## 📦 **Step 1: Install Dependencies**

### **Option A: Full AI Power (Recommended)**
```bash
pip install -r requirements.txt
pip install llama-cpp-python
```

### **Option B: Basic Installation**
```bash
pip install -r requirements.txt
```
*(AI will use Python fallback mode)*

### **Option C: GPU Acceleration (Optional)**

**For NVIDIA GPU:**
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

**For Apple Silicon (M1/M2/M3):**
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/metal
```

---

## 🎯 **Step 2: Launch the IDE**

```bash
python deathaius_ide_integrated.py
```

**What happens:**
1. ✅ Welcome screen appears
2. ✅ Choose: New Project or Load Existing
3. ✅ IDE opens with built-in AI ready!

---

## 🤖 **Step 3: Setup AI (First Time Only)**

### **If you already have models on Google Drive:**

1. Your models in `G:\My Drive` are **automatically detected**!
2. Click **AI → Model Manager**
3. Click **Refresh**
4. Select your model
5. Click **Load Model**
6. Done! ✅

### **If you need to download a model:**

1. Click **AI → Model Manager**
2. Go to **Download Models** tab
3. Select **DeepSeek Coder 1.3B** (800MB - fastest)
4. Click **Download Selected Model**
5. Wait for download (progress bar shown)
6. Go to **Installed Models** tab
7. Select the model
8. Click **Load Model**
9. Done! ✅

### **If your models are elsewhere:**

1. Click **AI → Model Manager**
2. Click **📁 Browse for Model...**
3. Navigate to your `.gguf` file
4. Select it
5. Model loads automatically! ✅

---

## 💡 **Step 4: Use AI Features**

### **AI Chat:**
1. Look at right panel → **💬 AI Assistant**
2. Type your question
3. Click **Send** or press **Enter**
4. Get instant AI help!

**Quick Action Buttons:**
- **📝 Explain Code** - Understand code
- **🐛 Find Bugs** - Spot issues
- **⚡ Optimize** - Performance tips
- **📚 Add Docs** - Generate documentation
- **🔧 Refactor** - Improve code
- **🧪 Write Tests** - Create unit tests

### **Inline AI Suggestions:**
1. Open a code file
2. Start typing code
3. Wait 1.5 seconds
4. Gray suggestion appears
5. Press **Tab** to accept
6. Press **Esc** to dismiss

### **Code Navigation:**
1. Multi-file tabs (open multiple files)
2. File tree on left (click to open)
3. Keyboard shortcuts (Ctrl+S, Ctrl+F, etc.)

---

## ⚙️ **Recommended Settings**

### **For Fast Inline Suggestions:**
- Model: DeepSeek Coder 1.3B or TinyLlama 1.1B
- Context: 2048 tokens
- Threads: 4-6
- GPU Layers: 0 (CPU) or 10-20 (GPU)

### **For Smart Chat:**
- Model: CodeLlama 7B or Mistral 7B
- Context: 4096 tokens
- Threads: 8
- GPU Layers: 35 (GPU) or 0 (CPU)

**Change settings:**
1. **AI → Model Manager**
2. **Settings** tab
3. Adjust sliders
4. Click **Save Settings**

---

## 🎯 **Typical Workflow**

### **Starting a New Project:**

1. **Launch IDE** → Select "Start New Project"
2. **Load a model** → AI → Model Manager
3. **Describe project** → Fill in "What Do You Want to Build?"
4. **Run Feasibility Check** → Click "STEP 0: Feasibility Check"
5. **Start coding!** → Use AI chat for help

### **Working with Existing Code:**

1. **Launch IDE** → Select "Load Existing Project"
2. **Load a model** → AI → Model Manager
3. **Open files** → Click files in tree or use Ctrl+O
4. **Get AI help:**
   - Select code → Click "📝 Explain Code"
   - Ask in chat → "How do I optimize this?"
   - Use inline suggestions → Type and wait

---

## 🔑 **Keyboard Shortcuts**

- **Ctrl+S** - Save file
- **Ctrl+N** - New file
- **Ctrl+O** - Open file
- **Ctrl+F** - Find in file
- **Ctrl+H** - Replace
- **Ctrl+M** - Open Model Manager
- **Tab** - Accept AI suggestion
- **Esc** - Dismiss AI suggestion

---

## 📊 **Checking Model Status**

**Bottom right of IDE:**
- 🤖 **Green ✓** = Model loaded and running
- 🤖 **Orange ⏸** = Model loaded but not running
- 🤖 **Gray** = No model loaded

**Click the status to open Model Manager!**

---

## ❓ **Troubleshooting**

### **"No model loaded" error:**
→ Go to **AI → Model Manager** and load a model

### **Inline suggestions not appearing:**
→ Check **AI → Enable Inline Suggestions** is checked

### **AI responses are slow:**
→ Use a smaller model (1-2B parameters)
→ Reduce context length in Settings
→ Enable GPU layers if you have a GPU

### **Model not found in Google Drive:**
→ Click **Refresh** in Model Manager
→ Or use **📁 Browse for Model** to manually select

### **Download fails:**
→ Check internet connection
→ Try downloading model manually from HuggingFace
→ Place in `G:\My Drive\.deathaius_models`

---

## 🎉 **You're Ready!**

Your IDE now has:
- ✅ Built-in AI (no LM Studio needed)
- ✅ Inline code suggestions
- ✅ AI chat assistant
- ✅ Quick action buttons
- ✅ Google Drive model support
- ✅ Full code editor features

**Start coding with AI assistance!** 🚀

---

## 📚 **Next Steps:**

- Read `GOOGLE_DRIVE_MODELS.md` for model management
- Read `PHASE6_COMPLETE.md` for all AI features
- Read `PHASE1-5_COMPLETE.md` for other IDE features

**Need help?** Ask the AI chat: "How do I...?"
