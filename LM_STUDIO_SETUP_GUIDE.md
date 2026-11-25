# LM Studio Setup Guide for DeathAIAUS IDE FC

## Complete Step-by-Step Tutorial

This guide will help you set up LM Studio as a temporary backend for DeathAIAUS IDE FC while we work on adding Qwen2 support to ReapGate.

---

## Part 1: Install LM Studio

### Step 1: Download LM Studio
1. Go to **https://lmstudio.ai/**
2. Click the **Download** button
3. Choose your operating system (Windows in your case)
4. Wait for the installer to download (approximately 500MB)

### Step 2: Install LM Studio
1. Run the downloaded installer
2. Follow the installation wizard
3. Accept the license agreement
4. Choose installation location (default is fine)
5. Wait for installation to complete
6. Launch LM Studio when installation finishes

---

## Part 2: Load Your Qwen2 Pantheon Models

### Step 1: Open Local Models Section
1. Launch LM Studio
2. Look for the **"My Models"** or **"Local Models"** tab
3. Click the **"+"** or **"Add Model"** button

### Step 2: Import Your Pantheon Models
LM Studio can load models from your local directory.

**Option A: Import Individual Model**
1. Click **"Load from local path"** or **"Import Model"**
2. Navigate to: `G:\My Drive\DeathAIAUS_PANTHEON`
3. Browse to the model you want to use (start with smallest):
   - Recommended: `MINOR_DEITIES\IZANAMI\IZANAMI-DeathAIAUS-1.5B-Q4_0.gguf`
4. Select the .gguf file and click **Open**
5. Wait for LM Studio to import the model

**Option B: Point to Directory** (if LM Studio supports it)
1. Go to LM Studio Settings
2. Look for **"Model Paths"** or **"Custom Model Directory"**
3. Add path: `G:\My Drive\DeathAIAUS_PANTHEON`
4. LM Studio will scan and list all your Pantheon models

### Step 3: Verify Model is Loaded
1. Check the **"My Models"** tab
2. You should see your imported model listed
3. Note the model name/ID (you'll need this later)

---

## Part 3: Start the LM Studio Server

### Step 1: Navigate to Developer Tab
1. Click on the **"Developer"** or **"Server"** tab in LM Studio
2. This is where you'll start the local API server

### Step 2: Load a Model
1. In the Server/Developer tab, find the **"Select Model"** dropdown
2. Choose your imported Pantheon model (IZANAMI 1.5B recommended)
3. Wait for the model to load into memory (may take 30-60 seconds)
4. You'll see a status message when loading is complete

### Step 3: Configure Server Settings
1. **Port**: Should be set to `1234` (default)
2. **Context Length**: Set to `2048` or higher
3. **GPU Offload**: Enable if you have a GPU, otherwise leave on CPU
4. **Temperature**: Leave at default (0.7)

### Step 4: Start the Server
1. Click the **"Start Server"** button
2. Server status should change to **"Running"**
3. You should see: `Server running on http://localhost:1234`
4. Keep LM Studio open and running in the background

### Step 5: Verify Server is Running
1. Open a web browser
2. Navigate to: `http://localhost:1234/v1/models`
3. You should see JSON output listing your loaded model
4. If you get an error, server isn't running properly

---

## Part 4: Configure DeathAIAUS IDE FC

### Step 1: Fix IDE Backend Detection
Before starting the IDE, we need to update the code to properly support LM Studio.

**File to edit**: `deathaius_ide_fc.py`

**Location**: Lines 3249-3271

**Current Problem**: The `_call_model` method only checks for ReapGate and doesn't use the detected backend.

**Required Fix**:
Replace the hardcoded ReapGate health check with dynamic backend detection:

```python
# OLD CODE (lines 3249-3271):
# Health check and auto-start ReapGate if needed
try:
    health = requests.get("http://localhost:7777/health", timeout=5)
    if health.status_code != 200:
        raise Exception(f"ReapGate health check failed...")
except requests.exceptions.ConnectionError as e:
    # Try to start ReapGate automatically
    ...

# NEW CODE (replacement):
# Health check based on detected backend
if self.backend_name == "ReapGate":
    try:
        health = requests.get("http://localhost:7777/health", timeout=5)
        if health.status_code != 200:
            raise Exception(f"ReapGate health check failed with status {health.status_code}.")
    except requests.exceptions.ConnectionError:
        # Try to start ReapGate automatically
        print("ReapGate not available. Attempting to start...")
        if self.start_reapgate_if_needed():
            time.sleep(3)
            try:
                health = requests.get("http://localhost:7777/health", timeout=5)
                if health.status_code != 200:
                    raise Exception("ReapGate started but not responding.")
            except:
                raise Exception("Cannot connect to ReapGate. Please use LM Studio or restart IDE.")
        else:
            raise Exception("No AI backend available. Start LM Studio or ReapGate.")

elif self.backend_name == "LM Studio":
    try:
        # Check LM Studio is running
        response = requests.get("http://localhost:1234/v1/models", timeout=5)
        if response.status_code != 200:
            raise Exception("LM Studio server not responding.")
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to LM Studio. Please start LM Studio server on port 1234.")

else:
    raise Exception("No AI backend detected. Please start LM Studio or ReapGate.")

# Skip smart loading if using LM Studio (ReapGate-specific feature)
if self.backend_name == "ReapGate" and hasattr(self, 'smart_model_manager'):
    try:
        self.smart_model_manager.ensure_model_loaded(workflow)
    except Exception as e:
        print(f"Smart loading warning: {e}")
        pass
```

### Step 2: Start the IDE
1. Make sure LM Studio server is running
2. Run: `python DeathAIAUS_Launcher.py`
3. Wait for splash screen to complete
4. IDE should open

### Step 3: Verify Backend Connection
1. Check the status bar at the bottom of the IDE
2. Look for backend indicator (should show "LM Studio")
3. Or check the startup logs for "Backend: LM Studio"

---

## Part 5: Test AI Features

### Test 1: AI Chat
1. Look for the **AI Chat** sidebar on the right
2. Type a simple message: "Hello, can you help me?"
3. Press Enter or click Send
4. You should receive a response from the AI
5. Check LM Studio window - you should see activity/request logs

### Test 2: AI Composer (Ctrl+K)
1. Open or create a Python file
2. Press **Ctrl+K** to open the AI Composer
3. Type a request: "Create a hello world function"
4. Press Enter
5. AI should generate code
6. Code should appear in the composer window

### Test 3: Code Analysis
1. Select some code in the editor
2. Right-click and look for AI options
3. Try "Explain Code" or similar options
4. Verify AI responds with analysis

### Test 4: Model Selection
1. Go to **Settings > AI Model**
2. You should see your Pantheon model listed
3. Verify it's selected
4. Try changing to a different model (if you loaded multiple)

---

## Part 6: Troubleshooting

### Issue: "Cannot connect to backend"
**Solution:**
1. Check LM Studio is running
2. Verify server status shows "Running"
3. Test URL in browser: `http://localhost:1234/v1/models`
4. Restart LM Studio server if needed
5. Restart IDE

### Issue: "No model loaded"
**Solution:**
1. Go to LM Studio Developer tab
2. Select your model from dropdown
3. Click "Load Model"
4. Wait for loading to complete
5. Verify status shows model is loaded

### Issue: "Responses are very slow"
**Solution:**
1. Use smaller model (IZANAMI 1.5B instead of THANATOS 22B)
2. Enable GPU offload in LM Studio settings
3. Reduce context length to 1024 or 512
4. Close other applications to free RAM

### Issue: "Model not found in LM Studio"
**Solution:**
1. Verify .gguf file exists: `G:\My Drive\DeathAIAUS_PANTHEON\...\[model].gguf`
2. Re-import model in LM Studio
3. Check file isn't corrupted (should be several GB in size)
4. Try a different model to test

### Issue: "IDE still tries to use ReapGate"
**Solution:**
1. Verify code changes were saved to `deathaius_ide_fc.py`
2. Restart IDE completely
3. Check if ReapGate is running in background: `tasklist | findstr reapgate`
4. Kill ReapGate if found: `taskkill /f /im reapgate.exe`
5. Start IDE again with only LM Studio running

---

## Part 7: Tips for Best Performance

### Choose the Right Model
- **For testing/development**: IZANAMI (1.5B) - Fast responses
- **For coding assistance**: ANUBIS (1.2B) or MORRIGAN (7B)
- **For complex tasks**: AZRAEL (8B) - Good balance
- **For production**: THANATOS (22B) - Best quality, but slower

### Optimize LM Studio Settings
1. **GPU Layers**: Set to maximum if you have GPU
2. **Context Length**: 2048 is good balance
3. **CPU Threads**: Set to number of CPU cores - 2
4. **Batch Size**: Increase to 512 for faster processing

### Monitor Performance
1. Watch LM Studio's performance metrics
2. Check RAM usage (should be < 75%)
3. Monitor response times
4. Adjust model or settings if too slow

---

## Part 8: Working with Multiple Models

### Loading Different Models
1. Stop the current server in LM Studio
2. Select different model from dropdown
3. Wait for new model to load
4. Start server again
5. IDE will automatically use the new model

### Switching Models During Development
- You'll need to manually switch in LM Studio
- IDE doesn't support hot-swapping with LM Studio
- ReapGate (when fixed) will support automatic model switching

---

## Summary Checklist

- [ ] Downloaded and installed LM Studio
- [ ] Imported Pantheon model (IZANAMI 1.5B recommended)
- [ ] Started LM Studio server on port 1234
- [ ] Verified server running at http://localhost:1234
- [ ] Updated `deathaius_ide_fc.py` with LM Studio support
- [ ] Launched DeathAIAUS IDE
- [ ] Verified backend shows "LM Studio"
- [ ] Tested AI Chat - got response
- [ ] Tested AI Composer (Ctrl+K) - generated code
- [ ] Tested code analysis features
- [ ] IDE is now functional for continued development!

---

## Next Steps

Once you have the IDE working with LM Studio:
1. Use the IDE to continue development
2. Test all features thoroughly
3. Document any issues or limitations
4. Meanwhile, work on Phase 2: Adding Qwen2 support to ReapGate
5. Once ReapGate supports Qwen2, switch back for full feature set

---

## Important Notes

- **LM Studio is temporary**: This is a workaround to get you productive
- **Some features limited**: Smart Model Manager won't work with LM Studio
- **Manual model switching**: You'll need to change models in LM Studio manually
- **Keep LM Studio running**: Don't close it while using the IDE
- **Final goal**: Get ReapGate working with Qwen2 for full features

---

**Questions or issues? Check the troubleshooting section or restart both LM Studio and the IDE.**
