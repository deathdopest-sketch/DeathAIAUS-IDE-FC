# 🗂️ Using Your Google Drive AI Models

## ✅ **Your IDE Now Supports Google Drive Models!**

The AI Model Server has been configured to automatically use your models from:
```
G:\My Drive
```

---

## 🎯 **How It Works:**

### **Automatic Detection**

The IDE will:
1. ✅ **First** check `G:\My Drive\.deathaius_models` for models
2. ✅ **Then** scan `G:\My Drive` root for any `.gguf` or `.bin` files
3. ✅ **Display all** found models in the Model Manager

**No copying needed!** Your models stay on Google Drive.

---

## 🚀 **Quick Start:**

### **Option 1: Browse for Your Model**

1. Open IDE
2. Go to **AI → Model Manager**
3. Click **"📁 Browse for Model..."** button
4. Browse to your Google Drive location
5. Select your `.gguf` or `.bin` model
6. Model loads automatically!

### **Option 2: Auto-Detection**

1. Put your `.gguf` models in `G:\My Drive`
2. Open IDE
3. Go to **AI → Model Manager**
4. Click **Refresh**
5. See your models listed with **(Google Drive)** label
6. Select and click **Load Model**

### **Option 3: Organized Folder**

1. Create `G:\My Drive\.deathaius_models` folder
2. Move/copy your models there
3. They'll appear as regular models (without Google Drive label)

---

## 📁 **Supported Model Files:**

✅ `.gguf` files (GGUF format - recommended)
✅ `.bin` files (GGML format - older)

**Common model filenames:**
- `codellama-7b-instruct.Q4_K_M.gguf`
- `deepseek-coder-6.7b-instruct.Q4_K_M.gguf`
- `mistral-7b-instruct-v0.2.Q4_K_M.gguf`
- `phi-2.Q4_K_M.gguf`
- Any other GGUF/GGML model

---

## 🎨 **Benefits:**

✅ **No copying** - Models stay on Google Drive
✅ **Save space** - No duplication
✅ **Easy switching** - Browse to any location
✅ **Auto-scan** - Finds models automatically
✅ **Cloud backup** - Google Drive keeps them safe

---

## 💡 **Tips:**

### **For Best Performance:**

1. **Fast Models (Good for Inline Suggestions):**
   - DeepSeek Coder 1.3B
   - TinyLlama 1.1B
   - Phi-2

2. **Smart Models (Good for Chat):**
   - CodeLlama 7B
   - Mistral 7B Instruct
   - DeepSeek Coder 6.7B

3. **Balance:**
   - Use small model (1-2B) for inline suggestions
   - Use larger model (6-7B) for chat/explanations

### **Settings for Google Drive Models:**

**If Google Drive is on HDD:**
- Context: 2048 tokens (faster loading)
- Threads: 4-6
- GPU Layers: 35+ (offload to GPU to reduce disk reads)

**If Google Drive is on SSD:**
- Context: 4096 tokens
- Threads: 8
- GPU Layers: 0 (CPU) or 35+ (GPU)

---

## 🔧 **Customization:**

### **Change Default Location:**

Edit `components/ai_model_server.py`:

```python
# Line 21-28 (already updated for you!)
def __init__(self, models_dir=None):
    if models_dir:
        self.models_dir = models_dir
    elif os.path.exists(r'G:\My Drive'):
        self.models_dir = r'G:\My Drive\.deathaius_models'
    else:
        self.models_dir = os.path.join(os.path.expanduser('~'), '.deathaius_models')
```

**To change location:**
Replace `r'G:\My Drive'` with your path, e.g.:
- `r'D:\AI Models'`
- `r'E:\Models'`
- `r'C:\Users\YourName\Models'`

---

## 📊 **Example Setup:**

### **Google Drive Structure:**

```
G:\My Drive\
├── .deathaius_models\                    # Organized models
│   ├── codellama-7b.Q4_K_M.gguf         # 3.8GB
│   ├── deepseek-coder-1.3b.Q4_K_M.gguf  # 800MB
│   └── mistral-7b.Q4_K_M.gguf           # 4.1GB
│
├── phi-2.Q4_K_M.gguf                     # Also works in root
└── tinyllama-1.1b.Q4_K_M.gguf           # Also works in root
```

**All will be detected automatically!**

---

## 🧪 **Testing:**

### **Test Auto-Detection:**

1. Put a `.gguf` file in `G:\My Drive`
2. Open Model Manager
3. Click Refresh
4. Should see model with **(Google Drive)** label

### **Test Browse:**

1. Click **📁 Browse for Model...**
2. Should start in `G:\My Drive`
3. Navigate to your model
4. Select it
5. Should load immediately

### **Test Loading:**

1. Select any detected model
2. Click **Load Model**
3. Status should show "✓ Loaded: [model name]"
4. Status bar should show green checkmark

---

## ❓ **FAQ:**

**Q: Do I need to copy models to a specific folder?**
A: No! Browse to your model wherever it is, or put it in `G:\My Drive` root.

**Q: Will models download to Google Drive?**
A: Yes, downloads go to `G:\My Drive\.deathaius_models` by default.

**Q: Can I use models from multiple locations?**
A: Yes! Use **Browse for Model** to load from anywhere.

**Q: What if Google Drive isn't available?**
A: IDE falls back to `~/.deathaius_models` in your user folder.

**Q: Do models need to be on Google Drive?**
A: No! You can browse to any location (external drives, network drives, etc.)

---

## 🎉 **You're All Set!**

Your IDE now:
- ✅ Automatically finds models on Google Drive
- ✅ Lets you browse to any model location
- ✅ Saves downloads to Google Drive
- ✅ Shows all models in one place

**Just open Model Manager and browse to your models!** 🚀
