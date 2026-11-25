<!-- d0844603-579f-41f4-af7d-5de29318331d f8c6ca67-3a68-4d7a-897c-512c3ef14f94 -->
# IDE Complete Audit and Smart Model Loading System

## Overview

1. Implement smart on-demand model loading with ReapGate
2. Fix AI chat errors with proper error handling
3. Complete IDE audit to remove dead code and ensure everything is connected

## Part 1: Smart On-Demand Model Loading

### 1.1 Add Model Loading API to ReapGate

**File:** `ReapGate/server.go`

**Add new endpoints:**

- `POST /v1/models/load` - Load a specific model
- `POST /v1/models/unload` - Unload current model
- `GET /v1/models/current` - Get currently loaded model
- `GET /v1/models/status` - Get model loading status (% loaded)

**Implementation:**

```go
// Load model endpoint
r.POST("/v1/models/load", func(c *gin.Context) {
    var req struct {
        ModelPath string `json:"model_path"`
    }
    c.BindJSON(&req)
    
    // Unload current model
    mm.UnloadCurrentModel()
    
    // Load new model with progress
    err := mm.LoadModel(req.ModelPath)
    if err != nil {
        c.JSON(500, gin.H{"error": err.Error()})
        return
    }
    
    c.JSON(200, gin.H{"status": "loaded", "model": req.ModelPath})
})
```

### 1.2 Add Smart Model Manager to IDE

**File:** `deathaius_ide_fc.py`

**Add new class before `DeathAIAUSIDE`:**

```python
class SmartModelManager:
    """Manages on-demand model loading and unloading"""
    
    def __init__(self, ide):
        self.ide = ide
        self.current_loaded_model = None
        self.loading_in_progress = False
        self.workflow_to_model = {
            'coding': ide.workflow_models.get('coding_generate'),
            'review': ide.workflow_models.get('review_check'),
            'testing': ide.workflow_models.get('test_generate'),
            'planning': ide.workflow_models.get('plan_architect')
        }
    
    def ensure_model_loaded(self, workflow_type, callback=None):
        """Ensure correct model is loaded for workflow"""
        required_model = self.workflow_to_model.get(workflow_type)
        
        if not required_model:
            raise Exception(f"No model configured for {workflow_type} workflow")
        
        # Already loaded
        if self.current_loaded_model == required_model:
            if callback:
                callback(100)
            return True
        
        # Load new model
        return self.load_model(required_model, callback)
    
    def load_model(self, model_name, progress_callback=None):
        """Load model via ReapGate"""
        self.loading_in_progress = True
        
        try:
            # Get model path
            model_path = self.ide.model_map.get(model_name, model_name)
            
            # Call ReapGate load API
            response = requests.post(
                "http://localhost:7777/v1/models/load",
                json={"model_path": model_path},
                timeout=120
            )
            
            if response.status_code == 200:
                self.current_loaded_model = model_name
                if progress_callback:
                    progress_callback(100)
                return True
            else:
                raise Exception(f"Failed to load model: {response.text}")
                
        finally:
            self.loading_in_progress = False
```

### 1.3 Update AI Call Methods to Use Smart Loading

**File:** `deathaius_ide_fc.py`

**Modify `_call_model`:**

```python
def _call_model(self, model_display_name, system_prompt, user_message, timeout, workflow='coding'):
    """Call AI model via ReapGate with smart loading"""
    
    # Ensure correct model is loaded
    if hasattr(self, 'smart_model_manager'):
        self.smart_model_manager.ensure_model_loaded(workflow)
    
    # ... rest of existing code
```

### 1.4 Add Model Loading Progress UI

**File:** `deathaius_ide_fc.py`

**Add progress indicator:**

```python
def show_model_loading_progress(self, model_name, workflow):
    """Show loading progress in status bar"""
    progress_window = tk.Toplevel(self.root)
    progress_window.title("Loading AI Model")
    progress_window.geometry("400x150")
    
    label = tk.Label(progress_window, 
                    text=f"Loading {model_name} for {workflow}...",
                    font=('Arial', 11))
    label.pack(pady=20)
    
    progress = ttk.Progressbar(progress_window, length=300, mode='indeterminate')
    progress.pack(pady=10)
    progress.start()
    
    status = tk.Label(progress_window, text="This may take 5-15 seconds...",
                     font=('Arial', 9), fg='#666666')
    status.pack(pady=5)
    
    return progress_window
```

## Part 2: Fix AI Chat Errors

### 2.1 Comprehensive Error Handling in `_call_model`

**File:** `deathaius_ide_fc.py` (Lines 3138-3155)

**Replace with:**

```python
def _call_model(self, model_display_name, system_prompt, user_message, timeout, workflow='coding'):
    """Call AI model via ReapGate/LM Studio with full error handling"""
    
    # Validate model selected
    if not model_display_name or model_display_name == 'default':
        raise Exception("No AI model selected. Please select a model from Settings > AI Model.")
    
    # Ensure model is loaded (smart loading)
    if hasattr(self, 'smart_model_manager'):
        try:
            self.smart_model_manager.ensure_model_loaded(workflow)
        except Exception as e:
            raise Exception(f"Failed to load model: {e}")
    
    model_id = self.model_map.get(model_display_name, model_display_name)
    
    # Health check
    try:
        health = requests.get("http://localhost:7777/health", timeout=2)
        if health.status_code != 200:
            raise Exception("ReapGate not responding. Please restart IDE.")
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to ReapGate. Please restart IDE.")
    except requests.exceptions.Timeout:
        raise Exception("ReapGate timeout. Backend may be overloaded.")
    
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 4000,
        "stream": False
    }
    
    try:
        response = requests.post(self.api_url, json=payload, timeout=timeout)
        response.raise_for_status()
        
        result = response.json()
        if 'choices' not in result or len(result['choices']) == 0:
            raise Exception("Invalid response. Model may not be loaded.")
        
        return result['choices'][0]['message']['content'].strip()
        
    except requests.exceptions.Timeout:
        raise Exception(f"Request timed out after {timeout}s. Try shorter prompt.")
    except requests.exceptions.ConnectionError:
        raise Exception("Lost connection to ReapGate. Please restart IDE.")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise Exception(f"Model '{model_id}' not found.")
        elif e.response.status_code == 500:
            raise Exception("ReapGate error. Check logs.")
        else:
            raise Exception(f"HTTP {e.response.status_code}: {e.response.text}")
    except KeyError:
        raise Exception("Unexpected response format.")
```

### 2.2 Add ReapGate Status Indicator

**File:** `deathaius_ide_fc.py`

**In `__init__` after status bar creation:**

```python
# ReapGate status indicator
self.reapgate_status_label = tk.Label(
    self.status_frame,
    text="⚪ ReapGate: Checking...",
    fg='#888888',
    bg='#2b2b2b',
    font=('Consolas', 9)
)
self.reapgate_status_label.pack(side=tk.RIGHT, padx=5)

# Start checker
self.check_reapgate_status()
```

### 2.3 Add Retry Mechanism

**File:** `deathaius_ide_fc.py`

**Add method:**

```python
def _call_model_with_retry(self, model_display_name, system_prompt, user_message, timeout, workflow='coding', max_retries=2):
    """Call model with automatic retry"""
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            return self._call_model(model_display_name, system_prompt, user_message, timeout, workflow)
        except Exception as e:
            last_error = e
            error_str = str(e)
            
            # Retry on transient errors only
            if any(x in error_str for x in ["timeout", "connection", "overloaded"]):
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
            raise
    
    raise last_error
```

## Part 3: Complete IDE Audit

### 3.1 Find Dead-End Functions

**Search for:**

1. Functions that are defined but never called
2. Import statements for unused modules
3. Commented-out code blocks
4. Duplicate functionality
5. Methods that reference non-existent attributes

**Tools to use:**

- `grep` for function definitions and their usage
- Check each component file systematically
- Verify all callbacks are connected
- Ensure all UI elements have handlers

### 3.2 Check Component Connections

**Verify:**

- All AI chat components properly call `_call_model`
- All UI buttons have command handlers
- All menu items trigger actual functions
- All keyboard shortcuts are registered
- Theme settings actually change themes
- Model selection actually changes models

### 3.3 Remove Useless Code

**Target:**

- Old Phase 1-6 import statements no longer needed
- Backup/legacy code in comments
- Unused helper functions
- Dead feature flags
- Orphaned configuration options

### 3.4 Systematic Audit Checklist

**Main IDE File (`deathaius_ide_fc.py`):**

- [ ] Check all methods are called somewhere
- [ ] Verify all imports are used
- [ ] Remove commented-out code
- [ ] Check all UI elements have handlers
- [ ] Verify all shortcuts work

**Components:**

- [ ] `ai_chat.py` - Verify connects to `_call_model`
- [ ] `code_actions.py` - Check all actions work
- [ ] `code_editor.py` - Verify syntax highlighting works
- [ ] `file_tabs.py` - Check tab switching works
- [ ] `search.py` - Verify search/replace works
- [ ] `shortcuts.py` - Test all keyboard shortcuts

**Features to Test:**

- [ ] File operations (open, save, new)
- [ ] AI chat sends messages
- [ ] Code actions trigger AI
- [ ] Theme switching works
- [ ] Model selection works
- [ ] Search and replace works
- [ ] Syntax highlighting works
- [ ] Git operations work (if implemented)

## Implementation Steps

### Phase 1: Smart Model Loading (Priority 1)

1. Add model loading API to ReapGate
2. Implement SmartModelManager in IDE
3. Update `_call_model` to use smart loading
4. Add loading progress UI
5. Test model swapping

### Phase 2: Error Handling (Priority 1)

1. Update `_call_model` with comprehensive error handling
2. Add ReapGate status indicator
3. Add retry mechanism
4. Update AI chat components to use retry
5. Test error scenarios

### Phase 3: IDE Audit (Priority 2)

1. Audit main IDE file
2. Audit each component file
3. Remove dead code
4. Fix broken connections
5. Test all features work

### Phase 4: Testing (Priority 1)

1. Test AI chat with model loading
2. Test model swapping between workflows
3. Test error handling and recovery
4. Test all IDE features still work
5. Performance testing

## Expected Results

- **Smart Loading:** Models load on-demand in 5-15 seconds
- **Low Memory:** Only 1 model in RAM at a time (4-22GB saved)
- **Fast Startup:** IDE starts instantly, no model preloading
- **Better Errors:** Clear messages with fix suggestions
- **Clean Code:** No dead functions, all features connected
- **Reliable AI:** Automatic retry, proper error recovery

## Part 4: Production Readiness Checklist

### 4.1 Error Logging and Crash Recovery

**Add comprehensive logging system:**

1. **IDE Crash Handler** - `deathaius_ide_fc.py`

   - Wrap main loop in try/except with crash recovery
   - Auto-save open files before crash
   - Generate crash report with stack trace
   - Offer to restart IDE or send crash report

2. **ReapGate Error Logging** - `ReapGate/server.go`

   - Add structured logging to file (`logs/reapgate.log`)
   - Log all API requests/responses
   - Log model loading/unloading events
   - Add request ID tracking for debugging

3. **Launcher Error Recovery** - `DeathAIAUS_Launcher.py`

   - Already has logging, verify it captures all errors
   - Add automatic retry on transient failures
   - Keep last 7 days of logs, auto-delete old ones

### 4.2 User Data Protection

**Implement auto-save and backup:**

1. **Auto-Save System**

   - Save open files every 2 minutes
   - Create `.autosave` directory for recovery files
   - Auto-restore unsaved changes on crash recovery
   - Clear auto-save files on clean shutdown

2. **Project Backup**

   - Already has `workspace_backups/` directory
   - Verify backup creation before destructive AI operations
   - Add setting for backup retention (default: 10 backups)
   - Add "Restore from Backup" menu option

3. **Settings Backup**

   - Save user settings to `config/user_settings.json`
   - Include: theme, model selections, workflow configs
   - Auto-restore on startup

### 4.3 Performance Optimization

**Ensure IDE runs smoothly:**

1. **Memory Management**

   - Implement file size limits (warn on >10MB files)
   - Add streaming for large file reads
   - Monitor memory usage, warn if >90% RAM used

2. **UI Responsiveness**

   - Move all AI calls to background threads (verify existing)
   - Add loading indicators for long operations
   - Implement request cancellation for AI calls

3. **ReapGate Performance**

   - Add model preloading option (optional startup flag)
   - Implement model caching in RAM
   - Add GPU memory monitoring

### 4.4 Security and Validation

**Protect against malicious input:**

1. **Input Validation**

   - Validate file paths (prevent directory traversal)
   - Sanitize AI prompts (max length: 50,000 chars)
   - Validate model paths (only allow `.gguf` files)

2. **Resource Limits**

   - Max AI response tokens: 4,000 (already set)
   - Max concurrent AI requests: 3
   - Request timeout: 120s (already set)

3. **API Security**

   - ReapGate: Add optional API key authentication
   - Rate limiting: 60 requests/minute per endpoint
   - CORS configuration for local-only access

### 4.5 Documentation and User Guidance

**Help users understand the IDE:**

1. **Update User Documentation**

   - `docs/getting-started/USER_GUIDE.md` - Complete feature guide
   - `docs/getting-started/TROUBLESHOOTING.md` - Common issues
   - `docs/getting-started/MODEL_SETUP.md` - Model configuration
   - Include screenshots and examples

2. **In-IDE Help System**

   - Add "Help" menu with:
     - Quick Start Guide (opens in browser)
     - Keyboard Shortcuts Reference
     - About Dialog (version, copyright, contact)
     - Check for Updates (checks GitHub releases)

3. **First-Run Experience**

   - Detect first run (no config file)
   - Show welcome wizard:
     - Explain ReapGate and model loading
     - Guide through model selection
     - Set up first workflow
   - Create example project to demonstrate features

### 4.6 Installer and Distribution

**Make installation easy:**

1. **Windows Installer**

   - Create `DeathAIAUS_IDE_Installer.exe` using Inno Setup or NSIS
   - Bundle Python runtime (py2exe or PyInstaller)
   - Include ReapGate.exe and MinGW DLLs
   - Create Start Menu shortcuts
   - Add uninstaller

2. **Portable Version**

   - Create `DeathAIAUS_IDE_Portable.zip`
   - Include all dependencies
   - No installation required
   - Settings stored in app directory

3. **Auto-Update System**

   - Check GitHub releases API on startup
   - Notify user of new versions
   - Download and apply updates automatically (optional)
   - Rollback mechanism if update fails

### 4.7 Testing Suite

**Verify everything works:**

1. **Automated Tests**

   - Create `tests/test_ide.py` - Test core IDE functions
   - Create `tests/test_reapgate.py` - Test ReapGate API
   - Create `tests/test_launcher.py` - Test launcher logic
   - Run tests before each release

2. **Manual Testing Checklist**

   - [ ] Fresh install on clean Windows VM
   - [ ] Model loading/unloading works
   - [ ] AI chat responds correctly
   - [ ] All workflows function
   - [ ] Theme switching works
   - [ ] File operations work
   - [ ] Crash recovery works
   - [ ] ReapGate starts/stops cleanly
   - [ ] Shortcut creation works

3. **Performance Benchmarks**

   - IDE startup time: <3 seconds
   - Model loading time: 5-15 seconds
   - AI response time: 2-30 seconds (depends on model)
   - UI remains responsive during AI operations

### 4.8 Legal and Compliance

**Protect yourself legally:**

1. **License Files**

   - Verify `license.txt` has proper copyright
   - Add licenses for dependencies
   - Create `THIRD_PARTY_LICENSES.txt`

2. **Terms of Service**

   - Create `TERMS_OF_SERVICE.md`
   - Clarify: no warranty, use at own risk
   - State: AI models are user's responsibility
   - Pricing: $99 standard price (promotional pricing handled separately)
   - Refund policy

3. **Privacy Policy**

   - Create `PRIVACY_POLICY.md`
   - State: no data collection, all local
   - Explain: crash reports are optional
   - Clarify: no analytics or tracking

### 4.9 Quality Assurance

**Final checks before release:**

1. **Code Quality**

   - Remove all debug print statements
   - Remove unused imports and dead code (Part 3)
   - Add docstrings to all public functions
   - Run linter (flake8, pylint)

2. **Branding Consistency**

   - Verify "DeathAIAUS" spelling everywhere
   - Check copyright year (2025)
   - Verify all icons are correct
   - Check window titles and branding

3. **Error Messages**

   - Ensure all error messages are user-friendly
   - Provide actionable solutions
   - Test error handling paths

### 4.10 Release Preparation

**Get ready to ship:**

1. **Version Management**

   - Set version to 1.0.0 in all files
   - Create `CHANGELOG.md`
   - Tag release in Git

2. **Build Release Package**

   - Build installer
   - Build portable ZIP
   - Include all documentation
   - Create checksums (SHA256)

3. **Release Assets**

   - Upload to GitHub Releases
   - Create download page on website
   - Prepare marketing materials
   - Write launch announcement

## Production Implementation Priority

### Critical (Must Have - Week 1)

1. Error logging and crash recovery
2. Auto-save system
3. Input validation and security
4. Performance optimization
5. Bug fixes from IDE audit

### Important (Should Have - Week 2)

1. Complete user documentation
2. First-run wizard
3. In-IDE help system
4. Automated testing suite
5. Windows installer

### Nice to Have (Week 3)

1. Auto-update system
2. Performance benchmarks
3. Portable version
4. Advanced security features

## Part 5: Licensing and Monetization System

### 5.1 License Key System

**Implementation in `deathaius_ide_fc.py`:**

1. **License Validation Class**
```python
class LicenseManager:
    """Manages license activation and validation"""
    
    def __init__(self):
        self.license_file = Path("config/license.dat")
        self.license_key = None
        self.is_licensed = False
        self.is_trial = False
        self.trial_days_remaining = 0
        self.feature_level = "free"  # free, trial, full
        
    def check_license(self):
        """Check if valid license exists"""
        if self.license_file.exists():
            try:
                with open(self.license_file, 'r') as f:
                    data = json.load(f)
                    self.license_key = data.get('key')
                    if self.validate_license_key(self.license_key):
                        self.is_licensed = True
                        self.feature_level = "full"
                        return True
            except:
                pass
        
        # Check trial
        trial_file = Path("config/trial.dat")
        if trial_file.exists():
            try:
                with open(trial_file, 'r') as f:
                    data = json.load(f)
                    install_date = datetime.fromisoformat(data['installed'])
                    days_elapsed = (datetime.now() - install_date).days
                    if days_elapsed < 14:
                        self.is_trial = True
                        self.trial_days_remaining = 14 - days_elapsed
                        self.feature_level = "trial"
                        return True
        else:
            # First run - start trial
            self.start_trial()
            return True
        
        # No valid license or trial
        self.feature_level = "free"
        return False
    
    def validate_license_key(self, key):
        """Validate license key format and checksum"""
        if not key or len(key) != 29:  # Format: DAIDE-XXXXX-XXXXX-XXXXX-XXXXX
            return False
        
        parts = key.split('-')
        if len(parts) != 5 or parts[0] != 'DAIDE':
            return False
        
        # Validate checksum (last segment)
        checksum = self.calculate_checksum('-'.join(parts[:4]))
        return checksum == parts[4]
    
    def calculate_checksum(self, data):
        """Calculate checksum for license key"""
        import hashlib
        hash_obj = hashlib.sha256(data.encode())
        return hash_obj.hexdigest()[:5].upper()
    
    def activate_license(self, key):
        """Activate license with provided key"""
        if self.validate_license_key(key):
            self.license_file.parent.mkdir(exist_ok=True)
            with open(self.license_file, 'w') as f:
                json.dump({
                    'key': key,
                    'activated': datetime.now().isoformat(),
                    'version': '1.0.0'
                }, f)
            self.is_licensed = True
            self.feature_level = "full"
            return True
        return False
    
    def start_trial(self):
        """Start 14-day trial"""
        trial_file = Path("config/trial.dat")
        trial_file.parent.mkdir(exist_ok=True)
        with open(trial_file, 'w') as f:
            json.dump({
                'installed': datetime.now().isoformat(),
                'version': '1.0.0'
            }, f)
        self.is_trial = True
        self.trial_days_remaining = 14
        self.feature_level = "trial"
```

2. **Feature Restrictions for Free Version**
```python
def check_feature_access(self, feature):
    """Check if user has access to feature"""
    if self.license_manager.feature_level == "full":
        return True
    
    if self.license_manager.feature_level == "trial":
        # Trial has full access but shows reminder
        return True
    
    # Free version restrictions
    free_features = {
        'basic_ai_chat': True,
        'single_model': True,
        'file_editing': True,
        'syntax_highlighting': True,
        'workflows': False,  # Premium feature
        'multiple_models': False,  # Premium feature
        'smart_context': False,  # Premium feature
        'error_recovery': False,  # Premium feature
        'session_memory': False,  # Premium feature
        'code_actions': False,  # Premium feature
    }
    
    return free_features.get(feature, False)
```

3. **Activation Dialog**
```python
def show_activation_dialog(self):
    """Show license activation dialog"""
    dialog = tk.Toplevel(self.root)
    dialog.title("Activate DeathAIAUS IDE")
    dialog.geometry("500x400")
    dialog.resizable(False, False)
    
    # Center dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
    y = (dialog.winfo_screenheight() // 2) - (400 // 2)
    dialog.geometry(f"500x400+{x}+{y}")
    
    # Title
    title = tk.Label(dialog, text="DeathAIAUS IDE Activation", 
                     font=('Arial', 16, 'bold'))
    title.pack(pady=20)
    
    # Trial info or purchase info
    if self.license_manager.is_trial:
        info_text = f"Trial: {self.license_manager.trial_days_remaining} days remaining\n\n"
        info_text += "Purchase a license for $99 to unlock:\n"
        info_text += "✓ Unlimited models\n"
        info_text += "✓ All AI workflows\n"
        info_text += "✓ Smart context & error recovery\n"
        info_text += "✓ Session memory\n"
        info_text += "✓ Free updates forever (v1.x)\n"
    else:
        info_text = "Free version includes:\n"
        info_text += "✓ Basic AI chat\n"
        info_text += "✓ Single model\n"
        info_text += "✓ File editing\n\n"
        info_text += "Upgrade to Pro for $99:\n"
        info_text += "✓ Unlimited models & workflows\n"
        info_text += "✓ Advanced AI features\n"
        info_text += "✓ Free updates forever (v1.x)\n"
    
    info = tk.Label(dialog, text=info_text, justify=tk.LEFT, 
                   font=('Arial', 10))
    info.pack(pady=10)
    
    # Purchase button
    def open_purchase():
        import webbrowser
        webbrowser.open('https://paypal.me/DeathAIAUS?country.x=AU&locale.x=en_AU')
        messagebox.showinfo("Purchase", 
            "After payment, send your PayPal email to deathaiaus@outlook.com\n"
            "to receive your license key within 24 hours.")
    
    purchase_btn = tk.Button(dialog, text="💳 Purchase License ($99)", 
                            command=open_purchase,
                            font=('Arial', 12, 'bold'),
                            bg='#4CAF50', fg='white',
                            padx=20, pady=10)
    purchase_btn.pack(pady=20)
    
    # Activation section
    tk.Label(dialog, text="Already have a license key?", 
            font=('Arial', 10)).pack(pady=10)
    
    key_frame = tk.Frame(dialog)
    key_frame.pack(pady=5)
    
    key_entry = tk.Entry(key_frame, width=35, font=('Consolas', 11))
    key_entry.pack(side=tk.LEFT, padx=5)
    key_entry.insert(0, "DAIDE-XXXXX-XXXXX-XXXXX-XXXXX")
    
    def activate():
        key = key_entry.get().strip().upper()
        if self.license_manager.activate_license(key):
            messagebox.showinfo("Success", 
                "License activated successfully!\nThank you for supporting DeathAIAUS!")
            dialog.destroy()
            self.root.title("DeathAIAUS IDE FC - Licensed")
        else:
            messagebox.showerror("Error", 
                "Invalid license key. Please check and try again.")
    
    activate_btn = tk.Button(key_frame, text="Activate", 
                            command=activate,
                            bg='#2196F3', fg='white',
                            padx=15, pady=5)
    activate_btn.pack(side=tk.LEFT)
    
    # Continue button
    continue_btn = tk.Button(dialog, text="Continue with current version", 
                            command=dialog.destroy)
    continue_btn.pack(pady=20)
```


### 5.2 Update System

**Check for updates on startup:**

```python
def check_for_updates(self):
    """Check GitHub releases for new version"""
    try:
        response = requests.get(
            "https://api.github.com/repos/YourUsername/DeathAIAUS-IDE-FC/releases/latest",
            timeout=5
        )
        if response.status_code == 200:
            latest = response.json()
            latest_version = latest['tag_name'].replace('v', '')
            current_version = "1.0.0"
            
            if self.version_newer(latest_version, current_version):
                self.show_update_notification(latest_version, latest['html_url'])
    except:
        pass  # Fail silently

def version_newer(self, new, current):
    """Compare version strings"""
    new_parts = [int(x) for x in new.split('.')]
    current_parts = [int(x) for x in current.split('.')]
    return new_parts > current_parts

def show_update_notification(self, version, url):
    """Show update available notification"""
    result = messagebox.askyesno(
        "Update Available",
        f"DeathAIAUS IDE v{version} is available!\n\n"
        f"You are currently running v1.0.0\n\n"
        f"Free updates are included with your license.\n"
        f"Would you like to download it now?"
    )
    if result:
        import webbrowser
        webbrowser.open(url)
```

### 5.3 License Key Generator (Separate Tool)

**Create `tools/generate_license_key.py`:**

```python
#!/usr/bin/env python3
"""
DeathAIAUS IDE License Key Generator
For internal use only - generate keys for customers
"""

import hashlib
import random
import string

def generate_license_key():
    """Generate a valid license key"""
    # Generate 4 random segments
    segments = []
    for i in range(4):
        segment = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        segments.append(segment)
    
    # Calculate checksum
    data = '-'.join(['DAIDE'] + segments)
    hash_obj = hashlib.sha256(data.encode())
    checksum = hash_obj.hexdigest()[:5].upper()
    
    # Final key
    key = f"DAIDE-{'-'.join(segments)}-{checksum}"
    return key

if __name__ == "__main__":
    print("DeathAIAUS IDE License Key Generator")
    print("=" * 50)
    
    count = input("How many keys to generate? ")
    try:
        count = int(count)
        print(f"\nGenerating {count} license keys:\n")
        
        for i in range(count):
            key = generate_license_key()
            print(f"{i+1}. {key}")
        
        print(f"\n{count} keys generated successfully!")
        print("\nStore these securely and send to customers after payment verification.")
    except ValueError:
        print("Invalid number")
```

### 5.4 Payment Integration

**Update About/Help Menu:**

```python
def create_help_menu(self):
    """Create Help menu with purchase link"""
    help_menu = tk.Menu(self.menubar, tearoff=0)
    self.menubar.add_cascade(label="Help", menu=help_menu)
    
    help_menu.add_command(label="📖 User Guide", command=self.show_user_guide)
    help_menu.add_command(label="⌨️ Keyboard Shortcuts", command=self.show_shortcuts)
    help_menu.add_separator()
    help_menu.add_command(label="🔄 Check for Updates", command=self.check_for_updates)
    help_menu.add_separator()
    
    if not self.license_manager.is_licensed:
        help_menu.add_command(label="💎 Upgrade to Pro ($99)", 
                            command=self.show_activation_dialog)
        help_menu.add_separator()
    
    help_menu.add_command(label="🔑 Enter License Key", 
                         command=self.show_activation_dialog)
    help_menu.add_command(label="📧 Contact Support", 
                         command=lambda: self.open_url('mailto:deathaiaus@outlook.com'))
    help_menu.add_separator()
    help_menu.add_command(label="ℹ️ About", command=self.show_about_dialog)
```

### 5.5 Terms of Service and Refund Policy

**Create `TERMS_OF_SERVICE.md`:**

```markdown
# DeathAIAUS IDE - Terms of Service

## 1. License Grant
By purchasing DeathAIAUS IDE, you receive a perpetual license to use version 1.x of the software.

## 2. What's Included
- One license per user/machine
- Free updates for all 1.x versions (1.0, 1.1, 1.2, etc.)
- Email support (deathaiaus@outlook.com)
- 14-day money-back guarantee

## 3. What's NOT Included
- Major version upgrades (e.g., DeathAIAUS IDE 2.0) require separate purchase
- AI models (user must provide their own)
- Custom development or consulting

## 4. Refund Policy
- Full refund within 14 days of purchase
- Email deathaiaus@outlook.com with your PayPal email
- Refunds processed within 3-5 business days
- License key will be deactivated

## 5. Warranty Disclaimer
DeathAIAUS IDE is provided "AS IS" without warranty of any kind.
Use at your own risk. The author is not liable for any damages.

## 6. AI Model Responsibility
You are responsible for the AI models you use and any content generated.

## 7. Payment
- Price: $99 USD (promotional pricing may vary)
- Payment via PayPal: https://paypal.me/DeathAIAUS
- License keys sent within 24 hours of payment verification

## 8. Contact
Email: deathaiaus@outlook.com
Website: [Your website]
Discord: [Your Discord]
```

## Production Readiness Score

Before release, verify:

- [ ] All Critical items complete
- [ ] All Important items complete
- [ ] Manual testing checklist 100% passed
- [ ] No known crashes or data loss bugs
- [ ] Documentation complete and accurate
- [ ] Legal files (license, terms, privacy) ready
- [ ] Installer tested on clean Windows VM
- [ ] License system tested (activation, trial, restrictions)
- [ ] Payment flow tested (PayPal link, key delivery)
- [ ] Ready for paying customers ($99)

### To-dos

- [ ] Create DeathAIAUS_Launcher.py with splash screen, logging, and ReapGate management
- [ ] Update launch.bat to call new Python launcher
- [ ] Create logs/ directory with .gitignore
- [ ] Test launcher with all error scenarios and retry logic