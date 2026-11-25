"""
Built-in AI Model Server
Integrated model inference engine for the IDE - no external servers needed
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
import queue
import json
import subprocess
import sys
from datetime import datetime
import urllib.request
import urllib.error
from components import death_theme as T


class AIModelServer:
    """Built-in AI model server for code generation"""

    def __init__(self, models_dir=None):
        # Default to Google Drive if it exists, otherwise use user home
        if models_dir:
            self.models_dir = models_dir
        elif os.path.exists(r'G:\My Drive'):
            self.models_dir = r'G:\My Drive\.deathaius_models'
        else:
            self.models_dir = os.path.join(os.path.expanduser('~'), '.deathaius_models')

        os.makedirs(self.models_dir, exist_ok=True)

        self.config_file = os.path.join(self.models_dir, 'config.json')
        self.current_model = None
        self.server_process = None
        self.is_running = False
        self.inference_queue = queue.Queue()

        # Load config
        self.config = self._load_config()

        # Start inference thread
        self.inference_thread = threading.Thread(target=self._inference_loop, daemon=True)
        self.inference_thread.start()

    def _load_config(self):
        """Load model configuration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass

        # Default config
        return {
            'current_model': None,
            'installed_models': [],
            'server_port': 8080,
            'context_length': 4096,
            'threads': 4,
            'gpu_layers': 0  # CPU-only by default
        }

    def _save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def list_installed_models(self):
        """List all installed models - recursively scans Google Drive"""
        models = []
        seen_paths = set()

        def scan_directory(directory, label=""):
            """Recursively scan directory for models"""
            if not os.path.exists(directory):
                return

            try:
                for root, dirs, files in os.walk(directory):
                    # Skip hidden directories and system folders
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['$RECYCLE.BIN', 'System Volume Information']]

                    for file in files:
                        if file.endswith('.gguf') or file.endswith('.bin'):
                            model_path = os.path.join(root, file)

                            # Skip duplicates
                            if model_path in seen_paths:
                                continue
                            seen_paths.add(model_path)

                            try:
                                size_mb = os.path.getsize(model_path) / (1024 * 1024)

                                # Get relative path for display
                                rel_path = os.path.relpath(root, directory)
                                if rel_path == '.':
                                    display_name = file
                                else:
                                    display_name = f"{file} ({rel_path})"

                                if label:
                                    display_name += f" [{label}]"

                                models.append({
                                    'name': display_name,
                                    'path': model_path,
                                    'size_mb': size_mb,
                                    'type': 'GGUF' if file.endswith('.gguf') else 'GGML'
                                })
                            except Exception as e:
                                print(f"Error reading {model_path}: {e}")
            except Exception as e:
                print(f"Error scanning {directory}: {e}")

        # Scan models directory
        if os.path.exists(self.models_dir):
            scan_directory(self.models_dir, "Local")

        # Scan Google Drive recursively
        gdrive_path = r'G:\My Drive'
        if os.path.exists(gdrive_path):
            scan_directory(gdrive_path, "Google Drive")

        return models

    def load_model(self, model_path):
        """Load model for inference"""
        if not os.path.exists(model_path):
            return False, "Model file not found"

        # Stop current model
        self.stop_server()

        self.current_model = model_path
        self.config['current_model'] = model_path
        self._save_config()

        return True, f"Model loaded: {os.path.basename(model_path)}"

    def start_server(self):
        """Start model server (using llama-cpp-python or similar)"""
        if not self.current_model:
            return False, "No model loaded"

        if self.is_running:
            return True, "Server already running"

        # Start inference engine
        self.is_running = True

        return True, "Server started"

    def stop_server(self):
        """Stop model server"""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                self.server_process.kill()

            self.server_process = None

        self.is_running = False

    def generate(self, prompt, max_tokens=512, temperature=0.7, callback=None):
        """Generate text from model"""
        if not self.is_running or not self.current_model:
            if callback:
                callback("Error: Model not loaded or server not running")
            return "Error: Model not loaded"

        # Queue inference request
        request = {
            'prompt': prompt,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'callback': callback,
            'timestamp': datetime.now()
        }

        self.inference_queue.put(request)

    def _inference_loop(self):
        """Background inference processing loop"""
        while True:
            try:
                request = self.inference_queue.get(timeout=1.0)
                self._process_inference(request)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Inference error: {e}")

    def _process_inference(self, request):
        """Process single inference request"""
        # Placeholder for actual inference
        # In production, this would use llama-cpp-python or similar

        prompt = request['prompt']
        callback = request.get('callback')

        # Simulate inference (replace with actual model call)
        import time

        response = self._simple_inference(prompt, request.get('max_tokens', 512))

        if callback:
            # Stream response word by word
            words = response.split()
            for word in words:
                callback(word + ' ')
                time.sleep(0.05)  # Simulate streaming

        return response

    def _simple_inference(self, prompt, max_tokens):
        """Simple inference fallback (replace with actual model)"""
        # This is a placeholder - in production you'd use:
        # - llama-cpp-python
        # - transformers
        # - ggml
        # - llama.cpp subprocess

        # For now, return a helpful message
        return f"[Model inference would process: '{prompt[:50]}...' | Max tokens: {max_tokens}]"

    def get_model_info(self):
        """Get current model info"""
        if not self.current_model:
            return None

        return {
            'name': os.path.basename(self.current_model),
            'path': self.current_model,
            'loaded': self.is_running,
            'size_mb': os.path.getsize(self.current_model) / (1024 * 1024)
        }


class ModelDownloader:
    """Download models from HuggingFace and other sources"""

    def __init__(self, models_dir):
        self.models_dir = models_dir

        # Curated list of coding models
        self.available_models = [
            {
                'name': 'DeepSeek Coder 1.3B (GGUF)',
                'size': '1.3B parameters',
                'size_mb': 800,
                'url': 'https://huggingface.co/TheBloke/deepseek-coder-1.3b-base-GGUF/resolve/main/deepseek-coder-1.3b-base.Q4_K_M.gguf',
                'filename': 'deepseek-coder-1.3b-q4.gguf',
                'description': 'Fast coding model, good for autocomplete'
            },
            {
                'name': 'CodeLlama 7B (GGUF)',
                'size': '7B parameters',
                'size_mb': 3800,
                'url': 'https://huggingface.co/TheBloke/CodeLlama-7B-GGUF/resolve/main/codellama-7b.Q4_K_M.gguf',
                'filename': 'codellama-7b-q4.gguf',
                'description': 'Meta\'s code generation model'
            },
            {
                'name': 'Mistral 7B Instruct (GGUF)',
                'size': '7B parameters',
                'size_mb': 4100,
                'url': 'https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf',
                'filename': 'mistral-7b-instruct-q4.gguf',
                'description': 'General purpose, excellent for chat'
            },
            {
                'name': 'Phi-2 (GGUF)',
                'size': '2.7B parameters',
                'size_mb': 1600,
                'url': 'https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf',
                'filename': 'phi-2-q4.gguf',
                'description': 'Small but powerful, fast inference'
            },
            {
                'name': 'TinyLlama 1.1B (GGUF)',
                'size': '1.1B parameters',
                'size_mb': 650,
                'url': 'https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf',
                'filename': 'tinyllama-1.1b-q4.gguf',
                'description': 'Tiny model, very fast, limited capabilities'
            }
        ]

    def download_model(self, model_info, progress_callback=None):
        """Download model file"""
        url = model_info['url']
        filename = model_info['filename']
        output_path = os.path.join(self.models_dir, filename)

        # Check if already exists
        if os.path.exists(output_path):
            return False, "Model already downloaded"

        try:
            def reporthook(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(int((downloaded / total_size) * 100), 100)
                    progress_callback(percent, downloaded, total_size)

            # Download file
            urllib.request.urlretrieve(url, output_path, reporthook)

            return True, output_path

        except Exception as e:
            # Clean up partial download
            if os.path.exists(output_path):
                os.remove(output_path)

            return False, f"Download failed: {e}"

    def get_available_models(self):
        """Get list of available models to download"""
        return self.available_models


class ModelManagerDialog(tk.Toplevel):
    """UI for managing AI models"""

    def __init__(self, parent, ai_server):
        super().__init__(parent)
        self.ai_server = ai_server
        self.downloader = ModelDownloader(ai_server.models_dir)

        self.title("AI Model Manager")
        self.geometry("800x600")
        self.configure(bg=T.BG3)

        self.setup_ui()
        self.load_models()

    def setup_ui(self):
        """Setup UI"""
        # Header
        header = tk.Frame(self, bg=T.BG, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="🤖 AI Model Manager",
                font=(T.UI, 14, 'bold'), fg=T.BILE, bg=T.BG).pack(side=tk.LEFT, padx=15, pady=15)

        # Current model status
        self.status_label = tk.Label(header, text="No model loaded",
                                     font=(T.UI, 9), fg=T.TEXT2, bg=T.BG)
        self.status_label.pack(side=tk.RIGHT, padx=15)

        # Tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Installed models tab
        installed_frame = tk.Frame(notebook, bg=T.BG3)
        notebook.add(installed_frame, text="Installed Models")
        self.setup_installed_tab(installed_frame)

        # Download models tab
        download_frame = tk.Frame(notebook, bg=T.BG3)
        notebook.add(download_frame, text="Download Models")
        self.setup_download_tab(download_frame)

        # Settings tab
        settings_frame = tk.Frame(notebook, bg=T.BG3)
        notebook.add(settings_frame, text="Settings")
        self.setup_settings_tab(settings_frame)

    def setup_installed_tab(self, parent):
        """Setup installed models tab"""
        tk.Label(parent, text="Installed Models", font=(T.UI, 11, 'bold'),
                bg=T.BG3, fg=T.TEXT).pack(pady=10)

        # Model list
        list_frame = tk.Frame(parent, bg=T.BG)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.installed_list = tk.Listbox(
            list_frame,
            bg=T.BG,
            fg=T.TEXT,
            font=(T.MONO, 10),
            selectbackground=T.HOVER,
            yscrollcommand=scrollbar.set
        )
        self.installed_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.installed_list.yview)

        # Buttons
        btn_frame = tk.Frame(parent, bg=T.BG3)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(btn_frame, text="Load Model", command=self.load_selected_model,
                 bg=T.BLOOD, fg=T.TEXT, font=(T.UI, 10, 'bold'),
                 relief=tk.FLAT, padx=20).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Delete Model", command=self.delete_model,
                 bg=T.BLOOD, fg=T.TEXT, font=(T.UI, 10, 'bold'),
                 relief=tk.FLAT, padx=20).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Refresh", command=self.load_models,
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT, padx=20).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="📁 Browse for Model...", command=self.browse_for_model,
                 bg=T.BLOOD, fg=T.TEXT, relief=tk.FLAT, padx=20).pack(side=tk.LEFT, padx=5)

    def setup_download_tab(self, parent):
        """Setup download models tab"""
        tk.Label(parent, text="Available Models to Download",
                font=(T.UI, 11, 'bold'), bg=T.BG3, fg=T.TEXT).pack(pady=10)

        # Available models list
        list_frame = tk.Frame(parent, bg=T.BG)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.available_list = tk.Listbox(
            list_frame,
            bg=T.BG,
            fg=T.TEXT,
            font=(T.MONO, 9),
            selectbackground=T.HOVER,
            yscrollcommand=scrollbar.set
        )
        self.available_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.available_list.yview)

        # Populate available models
        for model in self.downloader.get_available_models():
            display = f"{model['name']} - {model['size']} ({model['size_mb']}MB)\n  {model['description']}"
            self.available_list.insert(tk.END, display)

        # Download button
        btn_frame = tk.Frame(parent, bg=T.BG3)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(btn_frame, text="📥 Download Selected Model",
                 command=self.download_selected_model,
                 bg=T.HOVER, fg=T.TEXT, font=(T.UI, 10, 'bold'),
                 relief=tk.FLAT, padx=30, pady=10).pack()

        # Progress
        self.download_progress = ttk.Progressbar(btn_frame, mode='determinate', length=400)
        self.download_progress.pack(pady=10)

        self.download_status = tk.Label(btn_frame, text="", bg=T.BG3, fg=T.TEXT2)
        self.download_status.pack()

    def setup_settings_tab(self, parent):
        """Setup settings tab"""
        tk.Label(parent, text="Model Server Settings",
                font=(T.UI, 11, 'bold'), bg=T.BG3, fg=T.TEXT).pack(pady=20)

        settings_frame = tk.Frame(parent, bg=T.BG3)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        # Context length
        tk.Label(settings_frame, text="Context Length:", bg=T.BG3,
                fg=T.TEXT).grid(row=0, column=0, sticky=tk.W, pady=10)

        self.context_var = tk.IntVar(value=self.ai_server.config.get('context_length', 4096))
        context_spin = tk.Spinbox(settings_frame, from_=512, to=32768, increment=512,
                                 textvariable=self.context_var, bg=T.BG, fg=T.TEXT,
                                 width=15)
        context_spin.grid(row=0, column=1, padx=10, pady=10)

        # Threads
        tk.Label(settings_frame, text="CPU Threads:", bg=T.BG3,
                fg=T.TEXT).grid(row=1, column=0, sticky=tk.W, pady=10)

        self.threads_var = tk.IntVar(value=self.ai_server.config.get('threads', 4))
        threads_spin = tk.Spinbox(settings_frame, from_=1, to=16,
                                 textvariable=self.threads_var, bg=T.BG, fg=T.TEXT,
                                 width=15)
        threads_spin.grid(row=1, column=1, padx=10, pady=10)

        # GPU layers
        tk.Label(settings_frame, text="GPU Layers (0 = CPU only):", bg=T.BG3,
                fg=T.TEXT).grid(row=2, column=0, sticky=tk.W, pady=10)

        self.gpu_var = tk.IntVar(value=self.ai_server.config.get('gpu_layers', 0))
        gpu_spin = tk.Spinbox(settings_frame, from_=0, to=100,
                             textvariable=self.gpu_var, bg=T.BG, fg=T.TEXT,
                             width=15)
        gpu_spin.grid(row=2, column=1, padx=10, pady=10)

        # Save button
        tk.Button(settings_frame, text="Save Settings", command=self.save_settings,
                 bg=T.BLOOD, fg=T.TEXT, relief=tk.FLAT, padx=20).grid(row=3, column=0,
                                                                         columnspan=2, pady=20)

        # Info
        info_text = """
ℹ️ Settings Info:

• Context Length: Maximum tokens the model can process
• CPU Threads: More threads = faster inference (use CPU cores)
• GPU Layers: Number of model layers to offload to GPU
  (Requires CUDA/Metal support)

⚠️ Changes take effect after reloading the model
        """

        tk.Label(settings_frame, text=info_text, bg=T.BG3, fg=T.TEXT2,
                justify=tk.LEFT, font=(T.UI, 9)).grid(row=4, column=0,
                                                         columnspan=2, pady=20)

    def load_models(self):
        """Load installed models list"""
        self.installed_list.delete(0, tk.END)

        models = self.ai_server.list_installed_models()

        if not models:
            self.installed_list.insert(tk.END, "No models installed")
            return

        for model in models:
            display = f"{model['name']} - {model['size_mb']:.1f} MB ({model['type']})"
            self.installed_list.insert(tk.END, display)

        # Update status
        model_info = self.ai_server.get_model_info()
        if model_info:
            status = f"✓ Loaded: {model_info['name']}"
            self.status_label.config(text=status, fg=T.BILE)
        else:
            self.status_label.config(text="No model loaded", fg=T.TEXT2)

    def load_selected_model(self):
        """Load selected model"""
        selection = self.installed_list.curselection()
        if not selection:
            return

        models = self.ai_server.list_installed_models()
        if selection[0] >= len(models):
            return

        model = models[selection[0]]

        success, message = self.ai_server.load_model(model['path'])

        if success:
            self.ai_server.start_server()
            messagebox.showinfo("Success", message)
            self.load_models()  # Refresh
        else:
            messagebox.showerror("Error", message)

    def delete_model(self):
        """Delete selected model"""
        selection = self.installed_list.curselection()
        if not selection:
            return

        models = self.ai_server.list_installed_models()
        if selection[0] >= len(models):
            return

        model = models[selection[0]]

        confirm = messagebox.askyesno("Confirm Delete",
                                      f"Delete {model['name']}?\n\nThis cannot be undone.")

        if confirm:
            try:
                os.remove(model['path'])
                messagebox.showinfo("Success", "Model deleted")
                self.load_models()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {e}")

    def download_selected_model(self):
        """Download selected model"""
        selection = self.available_list.curselection()
        if not selection:
            return

        models = self.downloader.get_available_models()
        model = models[selection[0]]

        # Confirm download
        confirm = messagebox.askyesno("Confirm Download",
                                      f"Download {model['name']}?\n\nSize: {model['size_mb']} MB")

        if not confirm:
            return

        # Download in thread
        def download_thread():
            def progress_callback(percent, downloaded, total):
                self.download_progress['value'] = percent
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total / (1024 * 1024)
                self.download_status.config(
                    text=f"Downloading: {mb_downloaded:.1f} / {mb_total:.1f} MB ({percent}%)"
                )

            self.download_status.config(text="Starting download...")

            success, result = self.downloader.download_model(model, progress_callback)

            if success:
                self.download_status.config(text="Download complete!", fg=T.BILE)
                self.download_progress['value'] = 100
                messagebox.showinfo("Success", f"Model downloaded successfully!\n\n{result}")
                self.load_models()
            else:
                self.download_status.config(text="Download failed", fg=T.BLOOD_LIGHT)
                messagebox.showerror("Error", result)

            self.download_progress['value'] = 0

        threading.Thread(target=download_thread, daemon=True).start()

    def browse_for_model(self):
        """Browse for model file from any location"""
        from tkinter import filedialog

        # Start browse from Google Drive if it exists
        initial_dir = r'G:\My Drive' if os.path.exists(r'G:\My Drive') else os.path.expanduser('~')

        model_path = filedialog.askopenfilename(
            title="Select AI Model File",
            initialdir=initial_dir,
            filetypes=[
                ("GGUF Models", "*.gguf"),
                ("GGML Models", "*.bin"),
                ("All Files", "*.*")
            ]
        )

        if not model_path:
            return

        # Immediately load the selected model
        success, message = self.ai_server.load_model(model_path)

        if success:
            self.ai_server.start_server()
            messagebox.showinfo("Success", f"{message}\n\nModel ready to use!")
            self.load_models()
        else:
            messagebox.showerror("Error", message)

    def save_settings(self):
        """Save settings"""
        self.ai_server.config['context_length'] = self.context_var.get()
        self.ai_server.config['threads'] = self.threads_var.get()
        self.ai_server.config['gpu_layers'] = self.gpu_var.get()

        self.ai_server._save_config()

        messagebox.showinfo("Success", "Settings saved!\n\nReload the model for changes to take effect.")


class ModelStatusWidget(tk.Frame):
    """Widget showing current model status"""

    def __init__(self, parent, ai_server):
        super().__init__(parent, bg=T.BG3)
        self.ai_server = ai_server

        # Icon
        self.icon_label = tk.Label(self, text="🤖", bg=T.BG3, font=(T.UI, 12))
        self.icon_label.pack(side=tk.LEFT, padx=5)

        # Status
        self.status_label = tk.Label(self, text="No model loaded",
                                     bg=T.BG3, fg=T.TEXT2, font=(T.UI, 9))
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Update periodically
        self.update_status()

    def update_status(self):
        """Update status display"""
        model_info = self.ai_server.get_model_info()

        if model_info and model_info['loaded']:
            self.status_label.config(
                text=f"✓ {model_info['name']} ({model_info['size_mb']:.0f}MB)",
                fg=T.BILE
            )
        elif model_info:
            self.status_label.config(
                text=f"⏸ {model_info['name']} (not running)",
                fg=T.AMBER
            )
        else:
            self.status_label.config(text="No model loaded", fg=T.TEXT2)

        # Schedule next update
        self.after(2000, self.update_status)
