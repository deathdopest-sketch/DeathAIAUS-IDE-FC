#!/usr/bin/env python3
"""
DeathAIAUS IDE F.C (Feasibility Check) - FULLY INTEGRATED with Built-in AI
VERSION: 4.0 - Complete AI Integration with Phase 6

Now with BUILT-IN AI MODEL SERVER - No LM Studio needed!

Created by: DeathAIAUS Botmaker Team
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, Menu
import threading
import subprocess
import os
import queue
import json
from datetime import datetime
from pathlib import Path
import re
import shutil
import time

# Import existing components
from MODEL_TOOLS import SafeToolbox, ToolEnabledModel
from components.file_tabs import FileTabs
from components.shortcuts import ShortcutsHandler
from components.search import SearchDialog

# Import Phase 6 AI components
from components.ai_model_server import AIModelServer, ModelManagerDialog, ModelStatusWidget
from components.integrated_ai_chat import IntegratedAIChat, IntegratedInlineSuggestions

# Import the original modules we need from the base IDE
import sys
sys.path.insert(0, os.path.dirname(__file__))
from deathaius_ide_fc import WelcomeScreen, FeasibilityAnalyzer


class DeathAIAUSIDE:
    """Integrated IDE with built-in AI model server"""

    def __init__(self):
        """Initialize IDE with welcome screen"""
        # Show welcome screen
        welcome = WelcomeScreen()
        welcome_data = welcome.show()

        if not welcome_data:
            # User closed welcome screen
            sys.exit(0)

        # Extract welcome data
        action = welcome_data.get('action')
        path = welcome_data.get('path')
        name = welcome_data.get('name')
        language = welcome_data.get('language')

        self.root = tk.Tk()
        self.root.title(f"DeathAIAUS IDE F.C - {name} 🤖 AI-Powered")

        # Get screen dimensions and set to 90% of screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)

        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.state('normal')  # Start normal, user can maximize if needed

        # === PHASE 6: Initialize AI Model Server ===
        print("Initializing built-in AI model server...")
        self.ai_server = AIModelServer()  # Auto-uses Google Drive

        # Core systems
        self.feasibility_analyzer = FeasibilityAnalyzer()

        # Workspace
        self.workspace_path = path
        self.backup_path = os.path.join(self.workspace_path, ".deathaius_backups")
        os.makedirs(self.workspace_path, exist_ok=True)
        os.makedirs(self.backup_path, exist_ok=True)
        self.toolbox = SafeToolbox(self.workspace_path)

        # Auto-backup wrapper
        self.original_write_file = self.toolbox.write_file
        self.toolbox.write_file = self.write_file_with_backup

        # Store welcome data
        self.welcome_data = {'action': action, 'path': path, 'name': name, 'language': language}

        # State
        self.current_file = None
        self.current_project = None
        self.feasibility_report = None
        self.project_context = None
        self.message_queue = queue.Queue()
        self.is_running = False

        # Languages
        self.languages = {
            'Python': {'ext': '.py', 'run_cmd': 'python {file}'},
            'JavaScript': {'ext': '.js', 'run_cmd': 'node {file}'},
            'TypeScript': {'ext': '.ts', 'run_cmd': 'ts-node {file}'},
            'C++': {'ext': '.cpp', 'run_cmd': 'g++ {file} -o out && .\\out'},
            'Go': {'ext': '.go', 'run_cmd': 'go run {file}'},
            'Rust': {'ext': '.rs', 'run_cmd': 'rustc {file} && .\\{file}.exe'},
            'Java': {'ext': '.java', 'run_cmd': 'javac {file} && java {name}'},
            'C#': {'ext': '.cs', 'run_cmd': 'csc {file} && .\\{file}.exe'},
        }

        self.setup_gui()

        # Initialize components (after GUI setup)
        self.shortcuts = ShortcutsHandler(self)
        self.shortcuts.bind_all(self.root)
        self.search_dialog = SearchDialog(self)

        # === PHASE 6: Setup Inline AI Suggestions ===
        self.inline_suggestions = IntegratedInlineSuggestions(self, self.ai_server)

        self.load_file_tree()
        self.check_queue()

        print("✅ IDE initialized with built-in AI!")

    @property
    def code_editor(self):
        """Get current editor"""
        if hasattr(self, 'tabs') and self.tabs.current_editor:
            return self.tabs.current_editor.text_widget if hasattr(self.tabs.current_editor, 'text_widget') else self.tabs.current_editor
        return None

    def write_file_with_backup(self, file_path, content):
        """Write file with automatic backup"""
        if os.path.exists(file_path):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(self.backup_path, f"{os.path.basename(file_path)}.{timestamp}.bak")
            shutil.copy2(file_path, backup_file)

        return self.original_write_file(file_path, content)

    def setup_gui(self):
        """Setup GUI with AI integration"""
        # Menu bar
        self.setup_menu_bar()

        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)

        # Left: File tree
        self.setup_file_tree(main_paned)

        # Center: Editor + Terminal
        self.setup_center_panel(main_paned)

        # Right: AI Panel (with integrated AI chat)
        self.setup_ai_panel(main_paned)

        # Status bar with model status
        self.setup_status_bar()

    def setup_menu_bar(self):
        """Setup menu bar with AI menu"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New File", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open File", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Find", command=lambda: self.search_dialog.show_find(), accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace", command=lambda: self.search_dialog.show_replace(), accelerator="Ctrl+H")

        # === PHASE 6: AI Menu ===
        ai_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🤖 AI", menu=ai_menu)

        ai_menu.add_command(
            label="Model Manager...",
            command=self.open_model_manager,
            accelerator="Ctrl+M"
        )

        ai_menu.add_separator()

        # Inline suggestions toggle
        self.inline_suggestions_enabled = tk.BooleanVar(value=True)
        ai_menu.add_checkbutton(
            label="Enable Inline Suggestions",
            variable=self.inline_suggestions_enabled,
            command=self.toggle_inline_suggestions
        )

        ai_menu.add_separator()

        ai_menu.add_command(label="Start AI Server", command=self.start_ai_server)
        ai_menu.add_command(label="Stop AI Server", command=self.stop_ai_server)

        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="AI Setup Guide", command=self.show_ai_guide)

    def setup_status_bar(self):
        """Status bar with model status widget"""
        status_frame = tk.Frame(self.root, bg='#2d2d2d')
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Status text
        self.status_var = tk.StringVar(value="Ready - AI-Powered IDE")
        status_label = tk.Label(status_frame, textvariable=self.status_var,
                               bg='#2d2d2d', fg='#cccccc', anchor=tk.W,
                               font=('Arial', 9))
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # === PHASE 6: Model Status Widget ===
        self.model_status_widget = ModelStatusWidget(status_frame, self.ai_server)
        self.model_status_widget.pack(side=tk.RIGHT, padx=5)

    def setup_file_tree(self, parent):
        """File tree"""
        left_frame = ttk.Frame(parent, width=250)
        parent.add(left_frame, weight=0)

        header = ttk.Frame(left_frame)
        header.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(header, text="Workspace", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Button(header, text="Restore", width=8, command=self.restore_from_backup).pack(side=tk.RIGHT, padx=2)
        ttk.Button(header, text="+", width=3, command=self.new_file).pack(side=tk.RIGHT, padx=2)

        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, show='tree')
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.file_tree.yview)
        self.file_tree.bind('<Double-Button-1>', self.open_file_from_tree)

    def setup_center_panel(self, parent):
        """Editor and terminal"""
        center_frame = ttk.Frame(parent)
        parent.add(center_frame, weight=2)

        # Toolbar
        toolbar = ttk.Frame(center_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        self.file_label = ttk.Label(toolbar, text="No file open", font=('Arial', 9))
        self.file_label.pack(side=tk.LEFT, padx=5)

        ttk.Button(toolbar, text="Load Project", command=self.load_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Scan Project", command=self.scan_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔍 Find", command=lambda: self.search_dialog.show_find()).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📝 New", command=self.new_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Save", command=self.save_file).pack(side=tk.RIGHT, padx=2)
        ttk.Button(toolbar, text="Run", command=self.run_current_file).pack(side=tk.RIGHT, padx=2)

        # Editor with tabs
        editor_container = ttk.Frame(center_frame)
        editor_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tabs = FileTabs(editor_container, self)
        self.tabs.pack(fill=tk.BOTH, expand=True)

        # Terminal
        terminal_frame = ttk.LabelFrame(center_frame, text="Terminal Output", height=200)
        terminal_frame.pack(fill=tk.BOTH, padx=5, pady=5)
        terminal_frame.pack_propagate(False)

        self.terminal_output = scrolledtext.ScrolledText(terminal_frame, wrap=tk.WORD,
                                                         font=('Consolas', 9),
                                                         bg='#1e1e1e', fg='#00ff00')
        self.terminal_output.pack(fill=tk.BOTH, expand=True)

    def setup_ai_panel(self, parent):
        """AI panel with integrated chat"""
        right_frame = ttk.Frame(parent, width=550)
        parent.add(right_frame, weight=0)

        # Header
        header = ttk.Frame(right_frame)
        header.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(header, text="DeathAIAUS IDE F.C 🤖", font=('Arial', 14, 'bold')).pack()
        ttk.Label(header, text="Built-in AI Model Server",
                 font=('Arial', 9), foreground='green').pack()

        # Feasibility Dashboard
        feasibility_frame = ttk.LabelFrame(right_frame, text="REALITY CHECK DASHBOARD")
        feasibility_frame.pack(fill=tk.X, padx=5, pady=5)

        self.feasibility_score_label = ttk.Label(feasibility_frame, text="Feasibility: Not Analyzed",
                                                font=('Arial', 11, 'bold'))
        self.feasibility_score_label.pack(padx=5, pady=5)

        self.complexity_label = ttk.Label(feasibility_frame, text="Complexity: Unknown")
        self.complexity_label.pack(padx=5, pady=2)

        self.time_estimate_label = ttk.Label(feasibility_frame, text="Est. Time: Unknown")
        self.time_estimate_label.pack(padx=5, pady=2)

        # Configuration
        config_frame = ttk.LabelFrame(right_frame, text="Configuration")
        config_frame.pack(fill=tk.X, padx=5, pady=5)

        # Language
        lang_frame = ttk.Frame(config_frame)
        lang_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(lang_frame, text="Language:").pack(side=tk.LEFT)
        default_lang = self.welcome_data.get('language', 'Python')
        self.language_var = tk.StringVar(value=default_lang)
        ttk.Combobox(lang_frame, textvariable=self.language_var,
                    values=list(self.languages.keys()), state='readonly', width=15).pack(side=tk.LEFT, padx=5)

        # Project description
        desc_frame = ttk.LabelFrame(right_frame, text="What Do You Want to Build?")
        desc_frame.pack(fill=tk.BOTH, padx=5, pady=5)

        self.project_description = scrolledtext.ScrolledText(desc_frame, height=4, wrap=tk.WORD)
        self.project_description.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.project_description.insert('1.0', "Describe your project...\n\nBe specific about what you want.")

        # Action buttons
        action_frame = ttk.Frame(right_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(action_frame, text="STEP 0: Feasibility Check",
                  command=self.run_feasibility_check).pack(fill=tk.X, pady=2)

        ttk.Button(action_frame, text="🤖 Open Model Manager",
                  command=self.open_model_manager).pack(fill=tk.X, pady=2)

        # === PHASE 6: Integrated AI Chat ===
        chat_frame = ttk.LabelFrame(right_frame, text="💬 AI Assistant (Built-in)")
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.ai_chat = IntegratedAIChat(chat_frame, self, self.ai_server)
        self.ai_chat.pack(fill=tk.BOTH, expand=True)

    # === AI Model Management Methods ===

    def open_model_manager(self):
        """Open model manager dialog"""
        ModelManagerDialog(self.root, self.ai_server)

    def start_ai_server(self):
        """Start AI server"""
        if not self.ai_server.current_model:
            messagebox.showwarning("No Model", "Please load a model first.\n\nGo to AI → Model Manager")
            self.open_model_manager()
            return

        success, message = self.ai_server.start_server()
        if success:
            messagebox.showinfo("Success", message)
            self.status_var.set("AI Server Running ✓")
        else:
            messagebox.showerror("Error", message)

    def stop_ai_server(self):
        """Stop AI server"""
        self.ai_server.stop_server()
        messagebox.showinfo("Stopped", "AI server stopped")
        self.status_var.set("AI Server Stopped")

    def toggle_inline_suggestions(self):
        """Toggle inline AI suggestions"""
        if hasattr(self, 'inline_suggestions'):
            self.inline_suggestions.enabled = self.inline_suggestions_enabled.get()

            if self.inline_suggestions.enabled:
                self.status_var.set("Inline AI Suggestions Enabled ✓")
            else:
                self.status_var.set("Inline AI Suggestions Disabled")

    def show_ai_guide(self):
        """Show AI setup guide"""
        guide_text = """
🤖 Built-in AI Model Server Guide

1. DOWNLOAD A MODEL:
   • Go to AI → Model Manager
   • Click "Download Models" tab
   • Select a model (recommended: DeepSeek Coder 1.3B)
   • Click Download

2. OR BROWSE FOR YOUR MODEL:
   • Go to AI → Model Manager
   • Click "📁 Browse for Model..."
   • Navigate to your .gguf file
   • Model loads automatically!

3. USE AI FEATURES:
   • AI Chat: Ask questions, get help
   • Inline Suggestions: Type code, wait 1.5s, see suggestions
   • Quick Actions: Explain, Debug, Optimize, etc.

Your models in G:\\My Drive are automatically detected!

For more info, see GOOGLE_DRIVE_MODELS.md
        """

        messagebox.showinfo("AI Setup Guide", guide_text)

    def show_about(self):
        """Show about dialog"""
        about_text = """
DeathAIAUS IDE F.C
Version 4.0 - Fully Integrated AI

Features:
• 26 Major Features
• Built-in AI Model Server
• No LM Studio needed
• Uses your Google Drive models
• Free, local, private AI

Created by DeathAIAUS Team
        """
        messagebox.showinfo("About", about_text)

    # === File Operations ===

    def new_file(self):
        """Create new file"""
        if hasattr(self, 'tabs'):
            self.tabs.new_file()

    def open_file(self, event=None):
        """Open file"""
        filepath = filedialog.askopenfilename()
        if filepath:
            if hasattr(self, 'tabs'):
                self.tabs.open_file(filepath)

    def open_file_from_tree(self, event):
        """Open file from tree double-click"""
        selection = self.file_tree.selection()
        if selection:
            item = self.file_tree.item(selection[0])
            filepath = item.get('values', [''])[0] if item.get('values') else None
            if filepath and os.path.isfile(filepath):
                if hasattr(self, 'tabs'):
                    self.tabs.open_file(filepath)

    def save_file(self):
        """Save current file"""
        if hasattr(self, 'tabs') and self.tabs.current_editor:
            self.tabs.save_current_file()
            self.status_var.set("File saved ✓")

    def run_current_file(self):
        """Run current file"""
        if not self.code_editor:
            return

        # Save first
        self.save_file()

        # Get current file
        current_tab = self.tabs.get_current_tab_info()
        if not current_tab or not current_tab.get('filepath'):
            messagebox.showwarning("No File", "Please save the file first")
            return

        filepath = current_tab['filepath']
        lang = self.language_var.get()

        if lang not in self.languages:
            messagebox.showerror("Error", f"Unsupported language: {lang}")
            return

        cmd = self.languages[lang]['run_cmd'].format(file=filepath, name=Path(filepath).stem)

        self.terminal_output.insert(tk.END, f"\n{'='*60}\n")
        self.terminal_output.insert(tk.END, f"Running: {cmd}\n")
        self.terminal_output.insert(tk.END, f"{'='*60}\n")

        def run_thread():
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                self.terminal_output.insert(tk.END, result.stdout)
                if result.stderr:
                    self.terminal_output.insert(tk.END, f"\nErrors:\n{result.stderr}")
                self.terminal_output.insert(tk.END, f"\nExit code: {result.returncode}\n")
            except Exception as e:
                self.terminal_output.insert(tk.END, f"\nError: {e}\n")

            self.terminal_output.see(tk.END)

        threading.Thread(target=run_thread, daemon=True).start()

    # === Project Operations ===

    def load_file_tree(self):
        """Load file tree from workspace"""
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        if not os.path.exists(self.workspace_path):
            return

        for item in os.listdir(self.workspace_path):
            if item.startswith('.'):
                continue

            full_path = os.path.join(self.workspace_path, item)
            if os.path.isfile(full_path):
                self.file_tree.insert('', tk.END, text=item, values=[full_path])
            elif os.path.isdir(full_path):
                node = self.file_tree.insert('', tk.END, text=f"📁 {item}", values=[full_path])
                # Add children
                try:
                    for subitem in os.listdir(full_path):
                        if subitem.startswith('.'):
                            continue
                        subpath = os.path.join(full_path, subitem)
                        if os.path.isfile(subpath):
                            self.file_tree.insert(node, tk.END, text=subitem, values=[subpath])
                except:
                    pass

    def load_project(self):
        """Load project from directory"""
        path = filedialog.askdirectory()
        if path:
            self.workspace_path = path
            self.load_file_tree()
            self.status_var.set(f"Loaded: {path}")

    def scan_project(self):
        """Scan project structure"""
        if not os.path.exists(self.workspace_path):
            messagebox.showwarning("No Workspace", "No workspace loaded")
            return

        files = []
        for root, dirs, filenames in os.walk(self.workspace_path):
            # Skip hidden/build dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]

            for filename in filenames:
                if not filename.startswith('.'):
                    files.append(os.path.join(root, filename))

        messagebox.showinfo("Project Scan", f"Found {len(files)} files in project")

    def restore_from_backup(self):
        """Restore file from backup"""
        if not os.path.exists(self.backup_path):
            messagebox.showinfo("No Backups", "No backups found")
            return

        backups = os.listdir(self.backup_path)
        if not backups:
            messagebox.showinfo("No Backups", "No backups found")
            return

        # Show backup selection dialog (simplified)
        messagebox.showinfo("Backups", f"Found {len(backups)} backup files in:\n{self.backup_path}")

    # === Feasibility Check ===

    def run_feasibility_check(self):
        """Run feasibility check"""
        description = self.project_description.get('1.0', tk.END).strip()
        if not description or "Describe your project" in description:
            messagebox.showwarning("Warning", "Describe your project first")
            return

        lang = self.language_var.get()

        # Run analysis
        self.feasibility_report = self.feasibility_analyzer.analyze(description, lang)

        # Update dashboard
        score = self.feasibility_report['feasibility_score']
        if score >= 8:
            color = 'green'
        elif score >= 6:
            color = 'orange'
        elif score >= 4:
            color = 'red'
        else:
            color = 'darkred'

        self.feasibility_score_label.config(
            text=f"Feasibility: {score}/10",
            foreground=color
        )
        self.complexity_label.config(text=f"Complexity: {self.feasibility_report['complexity_level']}")
        self.time_estimate_label.config(text=f"Est. Time: {self.feasibility_report['estimated_time']}")

        # Show summary
        warnings_text = '\n'.join(f"• {w}" for w in self.feasibility_report['warnings']) if self.feasibility_report['warnings'] else "No major concerns"

        summary = f"""
Feasibility Score: {score}/10
Complexity: {self.feasibility_report['complexity_level']}
Estimated Time: {self.feasibility_report['estimated_time']}

Warnings:
{warnings_text}
        """

        messagebox.showinfo("Feasibility Report", summary)

    # === Queue Management ===

    def check_queue(self):
        """Check message queue"""
        try:
            while True:
                msg = self.message_queue.get_nowait()
                # Process message
        except queue.Empty:
            pass

        self.root.after(100, self.check_queue)

    def run(self):
        """Start IDE"""
        self.root.mainloop()


if __name__ == "__main__":
    ide = DeathAIAUSIDE()
    ide.run()
