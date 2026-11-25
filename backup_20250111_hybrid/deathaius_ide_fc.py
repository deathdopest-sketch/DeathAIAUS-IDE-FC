#!/usr/bin/env python3
"""
DeathAIAUS IDE F.C (Feasibility Check) - Brutally Honest AI Coding Assistant
VERSION: 3.0 - Full Honesty Implementation

The IDE that tells you the TRUTH before you waste months.
Will still help with massive projects - but you'll know it's massive.

Copyright (c) 2025 DeathAIAUS. All rights reserved.
Standards: DeathAIAUS Professional Bot Development Standards
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import subprocess
import os
import queue
import requests
import json
from datetime import datetime
from pathlib import Path
import re
import shutil
import time

# Phase 1 Components
from components.file_tabs import FileTabs
from components.shortcuts import ShortcutsHandler
from components.search import SearchDialog
from components.ai_chat import AIChatInterface
from components.code_editor import EnhancedCodeEditor

# Phase 2 Components  
from components.git_panel import GitPanel
from components.diff_viewer import DiffViewer
from components.code_actions import CodeActionsMenu
from components.error_detector import ErrorDetector
from components.smart_context import SmartContext

# Phase 3 Components (with graceful fallback)
try:
    from components.terminal_tabs import TerminalTabs
except ImportError:
    TerminalTabs = None
try:
    from components.split_view import SplitViewManager as SplitView
except ImportError:
    SplitView = None
try:
    from components.project_templates import TemplateLibrary as ProjectTemplates
except ImportError:
    ProjectTemplates = None
try:
    from components.themes import ThemeManager
except ImportError:
    ThemeManager = None
try:
    from components.snippets import SnippetManager
except ImportError:
    SnippetManager = None

# Phase 4 Components (with graceful fallback)
try:
    from components.inline_suggestions import InlineSuggestions
except ImportError:
    InlineSuggestions = None
try:
    from components.streaming_ai import StreamingAI
except ImportError:
    StreamingAI = None
try:
    from components.debugger import DebuggerPanel as Debugger
except ImportError:
    Debugger = None
try:
    from components.advanced_linting import AdvancedLinter
except ImportError:
    AdvancedLinter = None

# Phase 5 Components (with graceful fallback)
try:
    from components.ai_memory import AIMemory
except ImportError:
    AIMemory = None
try:
    from components.background_indexer import BackgroundIndexer
except ImportError:
    BackgroundIndexer = None
try:
    from components.cloud_sync import CloudSync
except ImportError:
    CloudSync = None
try:
    from components.project_export import ProjectExporter
except ImportError:
    ProjectExporter = None

# Phase 6 Components (with graceful fallback)
try:
    from components.ai_model_server import AIModelServer
except ImportError:
    AIModelServer = None
try:
    from components.integrated_ai_chat import IntegratedAIChat
except ImportError:
    IntegratedAIChat = None

# Advanced Components (Performance tracking, previews, etc.)
try:
    from components.model_performance_tracker import ModelPerformanceTracker, ModelPerformancePanel
except ImportError:
    ModelPerformanceTracker = None
    ModelPerformancePanel = None

try:
    from components.ai_preview_dialog import AIPreviewDialog, MultiFilePreviewDialog
except ImportError:
    AIPreviewDialog = None
    MultiFilePreviewDialog = None

try:
    from components.task_planner import TaskPlannerPanel
except ImportError:
    TaskPlannerPanel = None

# Additional Components (with graceful fallback)
try:
    from components.minimap import CodeMinimap
except ImportError:
    CodeMinimap = None
try:
    from components.extensions import ExtensionManager
except ImportError:
    ExtensionManager = None

class WelcomeScreen:
    """Cursor-style welcome screen for project selection"""

    def __init__(self):
        self.selected_action = None
        self.selected_path = None
        self.project_name = None
        self.project_language = None

        # Full language list (76 languages)
        self.all_languages = [
            'Python', 'JavaScript', 'TypeScript', 'C++', 'C', 'C#', 'Go', 'Rust', 'Java', 'Kotlin',
            'Swift', 'PHP', 'Ruby', 'Perl', 'Lua', 'R', 'Julia', 'Scala', 'Haskell', 'Elixir',
            'Erlang', 'Clojure', 'F#', 'Dart', 'Groovy', 'Nim', 'Crystal', 'D', 'Zig', 'OCaml',
            'Racket', 'Scheme', 'Common Lisp', 'Fortran', 'COBOL', 'Pascal', 'Ada', 'Assembly (x86)',
            'BASIC', 'Visual Basic', 'SQL', 'HTML', 'CSS', 'SCSS', 'SASS', 'LESS', 'Shell', 'Batch',
            'PowerShell', 'Makefile', 'CMake', 'Dockerfile', 'YAML', 'JSON', 'XML', 'TOML', 'Markdown',
            'LaTeX', 'MATLAB', 'Octave', 'Mathematica', 'VimScript', 'Emacs Lisp', 'AWK', 'Sed', 'Tcl',
            'Prolog', 'Verilog', 'VHDL', 'Solidity', 'Move', 'Cairo', 'Vyper', 'WebAssembly', 'GraphQL',
            'Protocol Buffers', 'Thrift'
        ]

    def show(self):
        """Show welcome dialog and return user choice"""
        dialog = tk.Tk()
        dialog.title("DeathAIAUS IDE F.C - Welcome")
        dialog.geometry("700x500")
        dialog.configure(bg='#1e1e1e')

        # Center the window
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"700x500+{x}+{y}")

        # Header
        header_frame = tk.Frame(dialog, bg='#1e1e1e')
        header_frame.pack(pady=30)

        title = tk.Label(header_frame, text="💀 DeathAIAUS IDE F.C 💀",
                        font=('Arial', 24, 'bold'), fg='#00ff00', bg='#1e1e1e')
        title.pack()

        subtitle = tk.Label(header_frame, text="Brutally Honest AI Coding Assistant",
                           font=('Arial', 12), fg='#ff0000', bg='#1e1e1e')
        subtitle.pack()

        # Main content
        content_frame = tk.Frame(dialog, bg='#2d2d2d', relief=tk.RAISED, bd=2)
        content_frame.pack(padx=50, pady=20, fill=tk.BOTH, expand=True)

        # Buttons
        btn_style = {'font': ('Arial', 12), 'width': 30, 'height': 2, 'relief': tk.RAISED, 'bd': 2}

        new_project_btn = tk.Button(content_frame, text="🆕 Start New Project",
                                    command=lambda: self.new_project(dialog),
                                    bg='#00aa00', fg='white', **btn_style)
        new_project_btn.pack(pady=15)

        load_project_btn = tk.Button(content_frame, text="📂 Load Existing Project",
                                     command=lambda: self.load_project(dialog),
                                     bg='#0066cc', fg='white', **btn_style)
        load_project_btn.pack(pady=15)

        # Recent projects section
        recent_label = tk.Label(content_frame, text="Recent Projects",
                               font=('Arial', 10, 'bold'), fg='#cccccc', bg='#2d2d2d')
        recent_label.pack(pady=(20, 5))

        recent_frame = tk.Frame(content_frame, bg='#2d2d2d')
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Load recent projects
        recent_projects = self.load_recent_projects()
        if recent_projects:
            for proj in recent_projects[:5]:  # Show last 5
                proj_btn = tk.Button(recent_frame,
                                    text=f"📁 {proj['name']} - {proj['path']}",
                                    command=lambda p=proj: self.load_recent(dialog, p),
                                    bg='#3d3d3d', fg='#cccccc', anchor='w',
                                    font=('Arial', 9), relief=tk.FLAT, bd=0)
                proj_btn.pack(fill=tk.X, pady=2)
        else:
            no_recent = tk.Label(recent_frame, text="No recent projects",
                                fg='#888888', bg='#2d2d2d', font=('Arial', 9, 'italic'))
            no_recent.pack()

        # Footer
        footer = tk.Label(dialog, text="(c) 2025 DeathAIAUS | v3.0",
                         font=('Arial', 8), fg='#666666', bg='#1e1e1e')
        footer.pack(side=tk.BOTTOM, pady=10)

        dialog.mainloop()

        return self.selected_action, self.selected_path, self.project_name, self.project_language

    def new_project(self, dialog):
        """Handle new project creation"""
        # Create new project dialog
        new_dialog = tk.Toplevel(dialog)
        new_dialog.title("New Project")
        new_dialog.geometry("500x400")
        new_dialog.configure(bg='#2d2d2d')

        # Center dialog
        new_dialog.update_idletasks()
        x = (new_dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (new_dialog.winfo_screenheight() // 2) - (400 // 2)
        new_dialog.geometry(f"500x400+{x}+{y}")

        tk.Label(new_dialog, text="Create New Project", font=('Arial', 14, 'bold'),
                fg='#00ff00', bg='#2d2d2d').pack(pady=20)

        # Project name
        tk.Label(new_dialog, text="Project Name:", fg='#cccccc', bg='#2d2d2d').pack(pady=5)
        name_entry = tk.Entry(new_dialog, width=40, font=('Arial', 10))
        name_entry.pack(pady=5)

        # Language selection
        tk.Label(new_dialog, text="Programming Language:", fg='#cccccc', bg='#2d2d2d').pack(pady=5)
        lang_var = tk.StringVar(value='Python')
        lang_combo = ttk.Combobox(new_dialog, textvariable=lang_var, values=self.all_languages,
                                  state='readonly', width=37)
        lang_combo.pack(pady=5)

        # Location
        tk.Label(new_dialog, text="Project Location:", fg='#cccccc', bg='#2d2d2d').pack(pady=5)
        location_frame = tk.Frame(new_dialog, bg='#2d2d2d')
        location_frame.pack(pady=5)

        location_entry = tk.Entry(location_frame, width=30, font=('Arial', 10))
        location_entry.insert(0, os.path.expanduser("~/Desktop"))
        location_entry.pack(side=tk.LEFT, padx=5)

        def browse_location():
            path = filedialog.askdirectory(title="Select Project Location")
            if path:
                location_entry.delete(0, tk.END)
                location_entry.insert(0, path)

        tk.Button(location_frame, text="Browse", command=browse_location,
                 bg='#0066cc', fg='white').pack(side=tk.LEFT)

        # Create button
        def create_project():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Error", "Please enter a project name")
                return

            location = location_entry.get()
            project_path = os.path.join(location, name)

            if os.path.exists(project_path):
                if not messagebox.askyesno("Confirm", f"Directory {project_path} already exists. Use it anyway?"):
                    return
            else:
                os.makedirs(project_path, exist_ok=True)

            self.selected_action = 'new'
            self.selected_path = project_path
            self.project_name = name
            self.project_language = lang_var.get()

            self.save_recent_project(name, project_path)
            new_dialog.destroy()
            dialog.destroy()

        tk.Button(new_dialog, text="Create Project", command=create_project,
                 bg='#00aa00', fg='white', font=('Arial', 12, 'bold'),
                 width=20, height=2).pack(pady=30)

    def load_project(self, dialog):
        """Handle loading existing project"""
        path = filedialog.askdirectory(title="Select Project Directory")
        if path:
            self.selected_action = 'load'
            self.selected_path = path
            self.project_name = os.path.basename(path)

            self.save_recent_project(self.project_name, path)
            dialog.destroy()

    def load_recent(self, dialog, project):
        """Load a recent project"""
        if os.path.exists(project['path']):
            self.selected_action = 'load'
            self.selected_path = project['path']
            self.project_name = project['name']
            dialog.destroy()
        else:
            messagebox.showerror("Error", f"Project path no longer exists:\n{project['path']}")

    def load_recent_projects(self):
        """Load recent projects from config file"""
        try:
            config_file = os.path.expanduser("~/.deathaius_ide_recent.json")
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []

    def save_recent_project(self, name, path):
        """Save project to recent list"""
        try:
            config_file = os.path.expanduser("~/.deathaius_ide_recent.json")
            recent = self.load_recent_projects()

            # Remove if already exists
            recent = [p for p in recent if p['path'] != path]

            # Add to front
            recent.insert(0, {'name': name, 'path': path, 'timestamp': datetime.now().isoformat()})

            # Keep only last 10
            recent = recent[:10]

            with open(config_file, 'w') as f:
                json.dump(recent, f, indent=2)
        except:
            pass

class FeasibilityAnalyzer:
    """Analyzes project feasibility before starting - the TRUTH TELLER"""
    
    def __init__(self):
        self.warning_patterns = {
            # Impossible/extremely difficult patterns
            'impossible': [
                r'break\s+(?:into|hack|bypass|crack)',
                r'scrape\s+(?:facebook|instagram|twitter|tiktok)',
                r'clone\s+(?:netflix|spotify|youtube|amazon|uber)',
                r'build.*(?:in|within)\s+(?:minutes|an?\s+hour|24\s+hours)',
                r'real[- ]?time.*(?:stock|crypto|forex).*prediction',
                r'bypass.*(?:cloudflare|captcha|bot\s+detection)',
                r'generate.*unlimited.*(?:money|revenue|profit)',
            ],
            # Very complex (months of work)
            'months_work': [
                r'(?:full|complete).*(?:ecommerce|marketplace|social\s+network)',
                r'(?:mmorpg|multiplayer\s+game|game\s+engine)',
                r'operating\s+system',
                r'browser\s+(?:from\s+scratch|engine)',
                r'(?:3d\s+rendering|physics)\s+engine',
                r'blockchain.*from\s+scratch',
                r'(?:compiler|interpreter).*from\s+scratch',
                r'video\s+(?:editor|streaming\s+platform)',
            ],
            # Heavy dependencies (complex setup)
            'heavy_deps': [
                r'machine\s+learning.*(?:train|model)',
                r'deep\s+learning',
                r'computer\s+vision.*(?:object|face|person)',
                r'natural\s+language.*(?:nlp|processing)',
                r'real[- ]?time.*(?:video|audio).*processing',
                r'distributed\s+system',
                r'kubernetes|docker\s+orchestration',
            ],
            # Legal/TOS issues
            'legal_issues': [
                r'scrape.*(?:without|bypass).*(?:permission|terms)',
                r'reverse\s+engineer',
                r'crack|pirate|torrent',
                r'spam|mass\s+email',
                r'ddos|dos\s+attack',
            ],
        }
    
    def analyze(self, description, language):
        """Run full feasibility analysis - returns dict with warnings and scores"""
        desc_lower = description.lower()
        
        result = {
            'feasibility_score': 10,  # 1-10, 10 = very feasible
            'complexity_level': 'Unknown',
            'estimated_time': 'Unknown',
            'warnings': [],
            'red_flags': [],
            'recommendations': [],
            'reality_check': '',
            'proceed': True,  # False = recommend not proceeding
        }
        
        # Check for impossible patterns
        for pattern in self.warning_patterns['impossible']:
            if re.search(pattern, desc_lower):
                result['red_flags'].append(f"IMPOSSIBLE REQUEST DETECTED: Pattern '{pattern}'")
                result['feasibility_score'] = max(1, result['feasibility_score'] - 5)
                result['proceed'] = False
        
        # Check for months of work
        months_matches = []
        for pattern in self.warning_patterns['months_work']:
            if re.search(pattern, desc_lower):
                months_matches.append(pattern)
                result['feasibility_score'] = max(2, result['feasibility_score'] - 3)
        
        if months_matches:
            result['warnings'].append(f"MAJOR COMPLEXITY: This is a {len(months_matches)*2}-6 month project minimum")
            result['complexity_level'] = 'Months of Work (Team Effort)'
        
        # Check for heavy dependencies
        for pattern in self.warning_patterns['heavy_deps']:
            if re.search(pattern, desc_lower):
                result['warnings'].append(f"Heavy dependency: Requires specialized libraries/infrastructure")
                result['feasibility_score'] = max(3, result['feasibility_score'] - 2)
        
        # Check for legal issues
        for pattern in self.warning_patterns['legal_issues']:
            if re.search(pattern, desc_lower):
                result['red_flags'].append(f"LEGAL/TOS ISSUE: This may violate terms of service or laws")
                result['feasibility_score'] = max(1, result['feasibility_score'] - 4)
                result['proceed'] = False
        
        # Word count complexity heuristic
        word_count = len(description.split())
        feature_count = desc_lower.count(' and ') + desc_lower.count(',')
        
        if word_count > 200 or feature_count > 10:
            result['warnings'].append(f"SCOPE CREEP DETECTED: {feature_count} features mentioned - expect scope expansion")
            result['feasibility_score'] = max(4, result['feasibility_score'] - 1)
        
        # Set complexity level if not already set
        if result['complexity_level'] == 'Unknown':
            if result['feasibility_score'] >= 8:
                result['complexity_level'] = 'Simple (Hours)'
                result['estimated_time'] = '2-8 hours'
            elif result['feasibility_score'] >= 6:
                result['complexity_level'] = 'Medium (Days)'
                result['estimated_time'] = '1-3 days'
            elif result['feasibility_score'] >= 4:
                result['complexity_level'] = 'Complex (Weeks)'
                result['estimated_time'] = '1-4 weeks'
            else:
                result['complexity_level'] = 'Massive (Months)'
                result['estimated_time'] = '2-12 months'
        
        # Generate reality check message
        if result['feasibility_score'] <= 3:
            result['reality_check'] = "STOP: This project is NOT feasible for a solo developer with AI assistance. This needs a team, significant budget, and months of development. I can still help if you understand this."
        elif result['feasibility_score'] <= 5:
            result['reality_check'] = "WARNING: This is a MASSIVE undertaking. Expect months of work, multiple rewrites, and significant challenges. Are you prepared for this commitment?"
        elif result['feasibility_score'] <= 7:
            result['reality_check'] = "HEADS UP: This is more complex than it seems. Budget weeks, not hours. Be prepared to learn and debug extensively."
        else:
            result['reality_check'] = "This looks feasible. Still expect some challenges and debugging time."
        
        # Recommendations
        if result['red_flags']:
            result['recommendations'].append("DO NOT PROCEED with current approach - legal/technical barriers")
            result['recommendations'].append("Consider: legal alternatives, scaled-down version, or different approach")
        elif result['feasibility_score'] <= 5:
            result['recommendations'].append("Start with MVP (Minimum Viable Product) - one core feature only")
            result['recommendations'].append("Plan for iterative development over months")
            result['recommendations'].append("Budget for learning curve and debugging")
            result['recommendations'].append("Consider hiring experienced developers for complex parts")
        elif result['feasibility_score'] <= 7:
            result['recommendations'].append("Break into smaller milestones")
            result['recommendations'].append("Prototype core features first")
            result['recommendations'].append("Plan for testing and iteration time")
        
        return result


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
        
        # If no workflow model configured, use default model selection
        if not required_model:
            # Get the currently selected model from the IDE
            current_model = getattr(self.ide, 'selected_model', None)
            if not current_model:
                # Try to get from model dropdown if it exists
                try:
                    current_model = self.ide.model_var.get()
                except:
                    pass
            
            if not current_model or current_model == 'default':
                # No model selected, skip smart loading
                if callback:
                    callback(100)
                return True
            
            required_model = current_model
        
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


class DeathAIAUSIDE:
    """The brutally honest AI coding IDE"""
    
    def __init__(self, welcome_data=None):
        # Show welcome screen if no data provided
        if welcome_data is None:
            welcome = WelcomeScreen()
            action, path, name, language = welcome.show()

            if action is None:  # User closed welcome screen
                import sys
                sys.exit(0)

            welcome_data = {
                'action': action,
                'path': path,
                'name': name,
                'language': language
            }

        self.root = tk.Tk()
        self.root.title(f"DeathAIAUS IDE F.C - {welcome_data.get('name', 'Workspace')}")

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

        # Core systems
        # Use ReapGate (custom inference backend) on port 7777
        # Fallback to LM Studio on port 1234 if ReapGate not running
        self.api_url = "http://localhost:7777/v1/chat/completions"
        self.backend_name = "ReapGate"
        
        # Load Death Pantheon configuration
        self.pantheon = self.load_pantheon_config()
        
        # Detect which backend is available (ReapGate or LM Studio)
        self.detect_api_backend()
        
        self.available_models = self.detect_models()
        self.feasibility_analyzer = FeasibilityAnalyzer()
        
        # Workflow model assignments (configurable)
        self.workflow_models = {
            'coding_generate': None,  # Step 1: Generate
            'coding_analyze': None,   # Step 2: Analyze
            'coding_validate': None,  # Step 3: Validate
            'large_plan': None,       # Step 1: Plan
            'large_implement': None,  # Step 2: Implement
            'large_review': None,     # Step 3: Review
            'quick_prototype': None,  # Step 1: Prototype
            'quick_task': None,       # Step 2: Task
            'quick_logic': None,      # Step 3: Logic
            'security_detect': None,  # Step 1: Detect
            'security_destroy': None, # Step 2: Destroy
            'security_test': None,    # Step 3: Test
        }
        self.load_workflow_config()

        # Initialize Smart Model Manager
        self.smart_model_manager = SmartModelManager(self)

        # Workspace - use project path from welcome screen
        self.workspace_path = welcome_data['path']
        self.backup_path = os.path.join(self.workspace_path, ".deathaius_backups")
        os.makedirs(self.workspace_path, exist_ok=True)
        os.makedirs(self.backup_path, exist_ok=True)
        # Legacy toolbox removed - functionality moved to components
        # self.toolbox = SafeToolbox(self.workspace_path)

        # Store welcome data for later use
        self.welcome_data = welcome_data

        # Command and file approval settings
        self.auto_approve_commands = False
        self.auto_approve_file_changes = False  # Cursor-style code approval
        self.command_approval_queue = queue.Queue()

        # State
        self.current_file = None
        self.current_project = None
        self.feasibility_report = None
        self.project_context = None  # Store scanned project context
        self.message_queue = queue.Queue()
        self.is_running = False
        self.loading_animation_active = False
        self.loading_frame_index = 0
        
        # Languages - Full comprehensive list (76 languages)
        self.languages = {
            'Python': {'ext': '.py', 'run_cmd': 'python {file}', 'recommended_models': ['codestral', 'qwen'], 'typical_time': 'Small: 5-15min, Medium: 30-60min, Large: 2-4hrs'},
            'JavaScript': {'ext': '.js', 'run_cmd': 'node {file}', 'recommended_models': ['codestral', 'dolphin'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-6hrs'},
            'TypeScript': {'ext': '.ts', 'run_cmd': 'ts-node {file}', 'recommended_models': ['codestral', 'qwen'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'C++': {'ext': '.cpp', 'run_cmd': 'g++ {file} -o out && .\\out', 'recommended_models': ['codestral'], 'typical_time': 'Small: 20-30min, Medium: 2-3hrs, Large: 6-12hrs'},
            'C': {'ext': '.c', 'run_cmd': 'gcc {file} -o out && .\\out', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-3hrs, Large: 4-10hrs'},
            'C#': {'ext': '.cs', 'run_cmd': 'csc {file} && .\\{file}.exe', 'recommended_models': ['codestral', 'qwen'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'Go': {'ext': '.go', 'run_cmd': 'go run {file}', 'recommended_models': ['codestral', 'qwen'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-5hrs'},
            'Rust': {'ext': '.rs', 'run_cmd': 'rustc {file} && .\\{file}.exe', 'recommended_models': ['codestral'], 'typical_time': 'Small: 20-30min, Medium: 2-4hrs, Large: 8-16hrs'},
            'Java': {'ext': '.java', 'run_cmd': 'javac {file} && java {name}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 20-30min, Medium: 1-2hrs, Large: 4-8hrs'},
            'Kotlin': {'ext': '.kt', 'run_cmd': 'kotlinc {file} -include-runtime -d out.jar && java -jar out.jar', 'recommended_models': ['codestral'], 'typical_time': 'Small: 20-30min, Medium: 1-2hrs, Large: 4-8hrs'},
            'Swift': {'ext': '.swift', 'run_cmd': 'swift {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'PHP': {'ext': '.php', 'run_cmd': 'php {file}', 'recommended_models': ['codestral', 'qwen'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-6hrs'},
            'Ruby': {'ext': '.rb', 'run_cmd': 'ruby {file}', 'recommended_models': ['codestral', 'qwen'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-6hrs'},
            'Perl': {'ext': '.pl', 'run_cmd': 'perl {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-6hrs'},
            'Lua': {'ext': '.lua', 'run_cmd': 'lua {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 5-15min, Medium: 30-60min, Large: 2-4hrs'},
            'R': {'ext': '.r', 'run_cmd': 'Rscript {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-6hrs'},
            'Julia': {'ext': '.jl', 'run_cmd': 'julia {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-6hrs'},
            'Scala': {'ext': '.scala', 'run_cmd': 'scala {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 20-30min, Medium: 1-2hrs, Large: 4-8hrs'},
            'Haskell': {'ext': '.hs', 'run_cmd': 'runhaskell {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 25-35min, Medium: 2-3hrs, Large: 6-12hrs'},
            'Elixir': {'ext': '.ex', 'run_cmd': 'elixir {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'Erlang': {'ext': '.erl', 'run_cmd': 'escript {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'Clojure': {'ext': '.clj', 'run_cmd': 'clojure {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 20-30min, Medium: 1-2hrs, Large: 4-8hrs'},
            'F#': {'ext': '.fs', 'run_cmd': 'dotnet fsi {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 20-30min, Medium: 1-2hrs, Large: 4-8hrs'},
            'Dart': {'ext': '.dart', 'run_cmd': 'dart {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'Groovy': {'ext': '.groovy', 'run_cmd': 'groovy {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'Nim': {'ext': '.nim', 'run_cmd': 'nim c -r {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'Crystal': {'ext': '.cr', 'run_cmd': 'crystal {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'D': {'ext': '.d', 'run_cmd': 'rdmd {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'Zig': {'ext': '.zig', 'run_cmd': 'zig run {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 20-30min, Medium: 2-3hrs, Large: 6-10hrs'},
            'OCaml': {'ext': '.ml', 'run_cmd': 'ocaml {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 20-30min, Medium: 2-3hrs, Large: 6-10hrs'},
            'Racket': {'ext': '.rkt', 'run_cmd': 'racket {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'Scheme': {'ext': '.scm', 'run_cmd': 'scheme --script {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'Common Lisp': {'ext': '.lisp', 'run_cmd': 'sbcl --script {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 20-30min, Medium: 2-3hrs, Large: 6-10hrs'},
            'Fortran': {'ext': '.f90', 'run_cmd': 'gfortran {file} -o out && .\\out', 'recommended_models': ['codestral'], 'typical_time': 'Small: 20-30min, Medium: 2-3hrs, Large: 6-10hrs'},
            'COBOL': {'ext': '.cob', 'run_cmd': 'cobc -x {file} && .\\{file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 30-40min, Medium: 3-4hrs, Large: 8-12hrs'},
            'Pascal': {'ext': '.pas', 'run_cmd': 'fpc {file} && .\\{file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'Ada': {'ext': '.adb', 'run_cmd': 'gnatmake {file} && .\\{file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 25-35min, Medium: 2-3hrs, Large: 6-10hrs'},
            'Assembly (x86)': {'ext': '.asm', 'run_cmd': 'nasm -f win64 {file} && gcc out.o -o out && .\\out', 'recommended_models': ['codestral'], 'typical_time': 'Small: 40-60min, Medium: 4-6hrs, Large: 12-20hrs'},
            'BASIC': {'ext': '.bas', 'run_cmd': 'freebasic {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-6hrs'},
            'Visual Basic': {'ext': '.vb', 'run_cmd': 'vbc {file} && .\\{file}.exe', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'SQL': {'ext': '.sql', 'run_cmd': 'echo "Run in database client"', 'recommended_models': ['codestral', 'qwen'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-6hrs'},
            'HTML': {'ext': '.html', 'run_cmd': 'start {file}', 'recommended_models': ['codestral', 'qwen'], 'typical_time': 'Small: 5-15min, Medium: 30-60min, Large: 2-4hrs'},
            'CSS': {'ext': '.css', 'run_cmd': 'echo "Include in HTML"', 'recommended_models': ['codestral', 'qwen'], 'typical_time': 'Small: 5-15min, Medium: 30-60min, Large: 2-4hrs'},
            'SCSS': {'ext': '.scss', 'run_cmd': 'sass {file} out.css', 'recommended_models': ['codestral'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-6hrs'},
            'SASS': {'ext': '.sass', 'run_cmd': 'sass {file} out.css', 'recommended_models': ['codestral'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-6hrs'},
            'LESS': {'ext': '.less', 'run_cmd': 'lessc {file} out.css', 'recommended_models': ['codestral'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-6hrs'},
            'Shell': {'ext': '.sh', 'run_cmd': 'bash {file}', 'recommended_models': ['codestral', 'qwen'], 'typical_time': 'Small: 5-15min, Medium: 30-60min, Large: 2-4hrs'},
            'Batch': {'ext': '.bat', 'run_cmd': '{file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 5-15min, Medium: 30-60min, Large: 2-4hrs'},
            'PowerShell': {'ext': '.ps1', 'run_cmd': 'powershell -File {file}', 'recommended_models': ['codestral', 'qwen'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-6hrs'},
            'Makefile': {'ext': '', 'run_cmd': 'make', 'recommended_models': ['codestral'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-6hrs'},
            'CMake': {'ext': '.cmake', 'run_cmd': 'cmake . && make', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'Dockerfile': {'ext': '', 'run_cmd': 'docker build -t app .', 'recommended_models': ['codestral', 'qwen'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'YAML': {'ext': '.yaml', 'run_cmd': 'echo "Configuration file"', 'recommended_models': ['codestral', 'qwen'], 'typical_time': 'Small: 5-15min, Medium: 30-60min, Large: 2-4hrs'},
            'JSON': {'ext': '.json', 'run_cmd': 'echo "Data file"', 'recommended_models': ['codestral', 'qwen'], 'typical_time': 'Small: 5-10min, Medium: 20-40min, Large: 1-2hrs'},
            'XML': {'ext': '.xml', 'run_cmd': 'echo "Data file"', 'recommended_models': ['codestral'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-6hrs'},
            'TOML': {'ext': '.toml', 'run_cmd': 'echo "Configuration file"', 'recommended_models': ['codestral'], 'typical_time': 'Small: 5-15min, Medium: 30-60min, Large: 2-4hrs'},
            'Markdown': {'ext': '.md', 'run_cmd': 'echo "Documentation file"', 'recommended_models': ['qwen', 'dolphin'], 'typical_time': 'Small: 5-15min, Medium: 30-60min, Large: 2-4hrs'},
            'LaTeX': {'ext': '.tex', 'run_cmd': 'pdflatex {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'MATLAB': {'ext': '.m', 'run_cmd': 'matlab -batch "run({file})"', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'Octave': {'ext': '.m', 'run_cmd': 'octave {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'Mathematica': {'ext': '.wl', 'run_cmd': 'wolframscript -file {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 20-30min, Medium: 2-3hrs, Large: 6-10hrs'},
            'VimScript': {'ext': '.vim', 'run_cmd': 'vim -S {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-6hrs'},
            'Emacs Lisp': {'ext': '.el', 'run_cmd': 'emacs --script {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'AWK': {'ext': '.awk', 'run_cmd': 'awk -f {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-6hrs'},
            'Sed': {'ext': '.sed', 'run_cmd': 'sed -f {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-6hrs'},
            'Tcl': {'ext': '.tcl', 'run_cmd': 'tclsh {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-6hrs'},
            'Prolog': {'ext': '.pl', 'run_cmd': 'swipl -s {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 25-35min, Medium: 2-3hrs, Large: 6-10hrs'},
            'Verilog': {'ext': '.v', 'run_cmd': 'iverilog {file} && vvp a.out', 'recommended_models': ['codestral'], 'typical_time': 'Small: 30-40min, Medium: 3-4hrs, Large: 8-12hrs'},
            'VHDL': {'ext': '.vhdl', 'run_cmd': 'ghdl -a {file} && ghdl -e {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 30-40min, Medium: 3-4hrs, Large: 8-12hrs'},
            'Solidity': {'ext': '.sol', 'run_cmd': 'solc {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 20-30min, Medium: 2-3hrs, Large: 6-10hrs'},
            'Move': {'ext': '.move', 'run_cmd': 'move build', 'recommended_models': ['codestral'], 'typical_time': 'Small: 25-35min, Medium: 2-3hrs, Large: 6-10hrs'},
            'Cairo': {'ext': '.cairo', 'run_cmd': 'cairo-compile {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 25-35min, Medium: 2-3hrs, Large: 6-10hrs'},
            'Vyper': {'ext': '.vy', 'run_cmd': 'vyper {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 20-30min, Medium: 2-3hrs, Large: 6-10hrs'},
            'WebAssembly': {'ext': '.wat', 'run_cmd': 'wat2wasm {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 25-35min, Medium: 2-3hrs, Large: 6-10hrs'},
            'GraphQL': {'ext': '.graphql', 'run_cmd': 'echo "Schema file"', 'recommended_models': ['codestral'], 'typical_time': 'Small: 10-20min, Medium: 45-90min, Large: 3-6hrs'},
            'Protocol Buffers': {'ext': '.proto', 'run_cmd': 'protoc {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
            'Thrift': {'ext': '.thrift', 'run_cmd': 'thrift --gen {file}', 'recommended_models': ['codestral'], 'typical_time': 'Small: 15-25min, Medium: 1-2hrs, Large: 4-8hrs'},
        }
        
        self.setup_gui()
        
        # Initialize ALL Phase 1-6 Components (after GUI is setup)
        self.initialize_all_components()
        
        # Setup keyboard shortcuts for new features
        self.setup_keyboard_shortcuts()
        
        self.load_file_tree()
        self.check_queue()
    
    def initialize_all_components(self):
        """Initialize all Phase 1-6 components"""
        print("[+] Initializing Phase 1-6 components...")
        
        # Phase 1: Core Editor Features
        self.shortcuts = ShortcutsHandler(self)
        self.shortcuts.bind_all(self.root)
        self.search_dialog = SearchDialog(self)
        print("  [OK] Phase 1: Editor, Tabs, Search, Shortcuts")
        
        # Phase 2: Git & Code Quality
        try:
            if hasattr(self, 'sidebar_container'):
                self.git_panel = GitPanel(self.sidebar_container, self)
                # Will be packed when user opens it
            # Note: DiffViewer is created on-demand, not during init
            self.diff_viewer = None
            self.code_actions = CodeActionsMenu(self)
            self.error_detector = ErrorDetector(self)
            self.smart_context = SmartContext(self.workspace_path)
            print("  [OK] Phase 2: Git, Diff, Code Actions, Error Detection")
        except Exception as e:
            print(f"  [WARN] Phase 2 partial: {e}")
        
        # Phase 3: Productivity Tools
        try:
            if ThemeManager:
                self.theme_manager = ThemeManager(self)  # Takes ide_instance, not root
            if SnippetManager:
                self.snippet_manager = SnippetManager(self)
            if ProjectTemplates:
                self.project_templates = ProjectTemplates()
            print("  [OK] Phase 3: Themes, Snippets, Templates")
        except Exception as e:
            print(f"  [WARN] Phase 3 partial: {e}")
        
        # Phase 4: Advanced AI
        try:
            if InlineSuggestions:
                self.inline_suggestions = InlineSuggestions(self, None)  # AI server set later
            if StreamingAI:
                self.streaming_ai = StreamingAI(self)
            if AdvancedLinter:
                self.advanced_linter = AdvancedLinter(self)
            print("  [OK] Phase 4: Inline AI, Streaming, Advanced Linting")
        except Exception as e:
            print(f"  [WARN] Phase 4 partial: {e}")
        
        # Phase 5: Cloud & Memory
        try:
            if AIMemory:
                self.ai_memory = AIMemory(self.workspace_path)
            if BackgroundIndexer:
                self.background_indexer = BackgroundIndexer(self.workspace_path)
            if CloudSync:
                self.cloud_sync = CloudSync(self.workspace_path)
            if ProjectExporter:
                self.project_exporter = ProjectExporter()  # Takes no arguments
            print("  [OK] Phase 5: AI Memory, Indexing, Cloud Sync, Export")
        except Exception as e:
            print(f"  [WARN] Phase 5 partial: {e}")
        
        # Phase 6: Built-in AI Server
        try:
            if AIModelServer:
                self.ai_model_server = AIModelServer()
                # Replace ai_chat with integrated version if server available
                if self.ai_model_server and hasattr(self, 'ai_chat'):
                    # Keep existing ai_chat but enhance with model server
                    pass
            print("  [OK] Phase 6: Built-in AI Model Server")
        except Exception as e:
            print(f"  [WARN] Phase 6 partial: {e}")
        
        # Additional Features
        try:
            if ExtensionManager:
                self.extension_manager = ExtensionManager(self)
            print("  [OK] Extensions Manager")
        except Exception as e:
            print(f"  [WARN] Extensions partial: {e}")

        # Advanced Features
        try:
            if ModelPerformanceTracker:
                self.performance_tracker = ModelPerformanceTracker(self.workspace_path)
            print("  [OK] Model Performance Tracker")
        except Exception as e:
            print(f"  [WARN] Performance Tracker partial: {e}")

        print("[+] Component initialization complete!")
    
    @property
    def code_editor(self):
        """Get current editor for backward compatibility"""
        if hasattr(self, 'tabs') and self.tabs.current_editor:
            return self.tabs.current_editor.text_widget if hasattr(self.tabs.current_editor, 'text_widget') else self.tabs.current_editor
        return None
    
    def clean_model_name(self, filename, file_size_bytes=None):
        """Convert filename to simple, user-friendly display name with version and size"""
        original = filename
        lower_name = filename.lower()

        # Extract base model name
        base_name = None
        if 'qwen' in lower_name:
            base_name = 'Qwen'
        elif 'codestral' in lower_name:
            base_name = 'Codestral'
        elif 'dolphin' in lower_name:
            base_name = 'Dolphin'
        elif 'mistral' in lower_name:
            base_name = 'Mistral'
        elif 'llama' in lower_name:
            base_name = 'Llama'
        elif 'deepseek' in lower_name:
            base_name = 'DeepSeek'
        elif 'wizardcoder' in lower_name:
            base_name = 'WizardCoder'
        elif 'starcoder' in lower_name:
            base_name = 'StarCoder'
        elif 'phind' in lower_name:
            base_name = 'Phind'
        elif 'granite' in lower_name:
            base_name = 'Granite'
        else:
            # Use first part of filename as base
            base_name = filename.split('-')[0].split('_')[0].capitalize()

        # Extract version numbers (7b, 13b, 22b, 2.5, etc.)
        version = ''
        version_match = re.search(r'(\d+\.?\d*)[bB]', original)
        if version_match:
            version = f" {version_match.group(1)}B"
        else:
            version_match = re.search(r'[v-]?(\d+\.?\d+)', original)
            if version_match:
                version = f" v{version_match.group(1)}"

        # Extract quantization (Q4_0, Q4_K_M, etc.)
        quant = ''
        quant_match = re.search(r'[Qq](\d+)[_-]?([Kk])?[_-]?([MmSs])?', original)
        if quant_match:
            q_num = quant_match.group(1)
            q_type = quant_match.group(2) or ''
            q_size = quant_match.group(3) or ''
            quant = f" Q{q_num}{q_type.upper()}{q_size.upper()}"

        # Format file size
        size_str = ''
        if file_size_bytes:
            gb = file_size_bytes / (1024**3)
            if gb >= 1:
                size_str = f" ({gb:.1f}GB)"
            else:
                mb = file_size_bytes / (1024**2)
                size_str = f" ({mb:.0f}MB)"

        return f"{base_name}{version}{quant}{size_str}".strip()
    
    def load_pantheon_config(self):
        """Load Death Pantheon model naming configuration"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'death_pantheon.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[WARN] Could not load pantheon config: {e}")
        return {"pantheon": {}, "usage_recommendations": {}, "tiers": {}}
    
    def load_workflow_config(self):
        """Load saved workflow model assignments"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'workflow_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    self.workflow_models.update(saved)
                    print("[OK] Loaded workflow configuration")
        except Exception as e:
            print(f"[WARN] Could not load workflow config: {e}")
    
    def save_workflow_config(self):
        """Save workflow model assignments"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'workflow_config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.workflow_models, f, indent=2)
            print("[OK] Saved workflow configuration")
        except Exception as e:
            print(f"[WARN] Could not save workflow config: {e}")
    
    def get_pantheon_name(self, filename):
        """Get the Death Pantheon name for a model file"""
        if not hasattr(self, 'pantheon') or not self.pantheon:
            return None
        
        # Normalize filename for matching
        filename_lower = filename.lower()
        
        # Check if this is already a DeathAIAUS branded file
        if 'deathaius' in filename_lower:
            # Extract deity name from branded filename
            # Format: DeathAIAUS-DEITY-SIZE-QUANT.gguf
            parts = filename_lower.replace('deathaius-', '').split('-')
            if parts:
                deity_name = parts[0].upper()
                # Find matching deity in pantheon
                for model_file, info in self.pantheon.get('pantheon', {}).items():
                    if info['name'].upper() == deity_name:
                        return info
        
        # Try exact match with original filename
        for model_file, info in self.pantheon.get('pantheon', {}).items():
            if model_file.lower() == filename_lower:
                return info
        
        # Try partial match (in case of path differences)
        for model_file, info in self.pantheon.get('pantheon', {}).items():
            if model_file.lower() in filename_lower or filename_lower in model_file.lower():
                return info
        
        # Check aliases if they exist
        for model_file, info in self.pantheon.get('pantheon', {}).items():
            if 'aliases' in info:
                for alias in info['aliases']:
                    if alias.lower() == filename_lower or alias.lower() in filename_lower:
                        return info
        
        return None
    
    def detect_api_backend(self):
        """Detect which AI backend is available (DeathAIAUS Backend, ReapGate, or LM Studio)"""
        # Try DeathAIAUS Python Backend first (our new primary backend)
        try:
            response = requests.get("http://localhost:8888/health", timeout=2)
            if response.status_code == 200:
                self.api_url = "http://localhost:8888/v1/chat/completions"
                self.backend_name = "DeathAIAUS Backend"
                return True
        except:
            pass

        # Fallback to ReapGate
        try:
            response = requests.get("http://localhost:7777/health", timeout=2)
            if response.status_code == 200:
                self.api_url = "http://localhost:7777/v1/chat/completions"
                self.backend_name = "ReapGate"
                return True
        except:
            pass
        
        # Fallback to LM Studio
        try:
            response = requests.get("http://localhost:1234/v1/models", timeout=2)
            if response.status_code == 200:
                self.api_url = "http://localhost:1234/v1/chat/completions"
                self.backend_name = "LM Studio"
                return True
        except:
            pass
        
        self.backend_name = "None"
        return False
    
    def detect_models(self):
        """Detect available models from ReapGate/LM Studio AND local .gguf files"""
        self.model_map = {}
        models = []

        # First, try ReapGate API
        try:
            response = requests.get("http://localhost:7777/v1/models", timeout=2)
            if response.status_code == 200:
                api_models = response.json().get('data', [])
                for m in api_models:
                    model_id = m['id']
                    file_size = m.get('size', None)
                    
                    # Check if this is a pantheon model
                    pantheon_info = self.get_pantheon_name(model_id)
                    if pantheon_info:
                        display_name = f"{pantheon_info['emoji']} {pantheon_info['name']} - {pantheon_info['role']}"
                    else:
                        display_name = self.clean_model_name(model_id, file_size)

                    if display_name in self.model_map:
                        counter = 2
                        while f"{display_name} #{counter}" in self.model_map:
                            counter += 1
                        display_name = f"{display_name} #{counter}"

                    self.model_map[display_name] = model_id
                    models.append(display_name)
        except:
            # Fallback to LM Studio API
            try:
                response = requests.get("http://localhost:1234/v1/models", timeout=2)
                if response.status_code == 200:
                    api_models = response.json().get('data', [])
                    for m in api_models:
                        model_id = m['id']
                        file_size = m.get('size', None)
                        
                        # Check if this is a pantheon model
                        pantheon_info = self.get_pantheon_name(model_id)
                        if pantheon_info:
                            display_name = f"{pantheon_info['emoji']} {pantheon_info['name']} - {pantheon_info['role']}"
                        else:
                            display_name = self.clean_model_name(model_id, file_size)

                        if display_name in self.model_map:
                        counter = 2
                            while f"{display_name} #{counter}" in self.model_map:
                            counter += 1
                            display_name = f"{display_name} #{counter}"

                        self.model_map[display_name] = model_id
                        models.append(display_name)
        except:
            pass

        # Second, scan for local .gguf models (Google Drive)
        local_model_paths = []
        
        # Check Google Drive - NEW DeathAIAUS_PANTHEON folder
        if os.path.exists(r'G:\My Drive\DeathAIAUS_PANTHEON'):
            local_model_paths.append(r'G:\My Drive\DeathAIAUS_PANTHEON')
        if os.path.exists(r'G:\My Drive\DeathAIAUS_PANTHEON\LMStudio_Models'):
            local_model_paths.append(r'G:\My Drive\DeathAIAUS_PANTHEON\LMStudio_Models')
        if os.path.exists(r'G:\My Drive\DeathAIAUS_PANTHEON\GPT4All_Original'):
            local_model_paths.append(r'G:\My Drive\DeathAIAUS_PANTHEON\GPT4All_Original')
        
        # Also check old GPT4All_Models folder as fallback
        if os.path.exists(r'G:\My Drive\GPT4All_Models'):
            local_model_paths.append(r'G:\My Drive\GPT4All_Models')
        if os.path.exists(r'G:\My Drive\GPT4All_Models\LMStudio_Models'):
            local_model_paths.append(r'G:\My Drive\GPT4All_Models\LMStudio_Models')
        if os.path.exists(r'G:\My Drive\GPT4All_Models\GPT4All_Original'):
            local_model_paths.append(r'G:\My Drive\GPT4All_Models\GPT4All_Original')
        
        # Check common local paths
        if os.path.exists(os.path.expanduser('~/.cache/lm-studio/models')):
            local_model_paths.append(os.path.expanduser('~/.cache/lm-studio/models'))
        if os.path.exists(os.path.expanduser('~/models')):
            local_model_paths.append(os.path.expanduser('~/models'))
        
        # Scan for .gguf files
        for base_path in local_model_paths:
            try:
                for root, dirs, files in os.walk(base_path):
                    for file in files:
                        if file.endswith('.gguf'):
                            full_path = os.path.join(root, file)
                            
                            # Check if this is a pantheon model
                            pantheon_info = self.get_pantheon_name(file)
                            if pantheon_info:
                                display_name = f"{pantheon_info['emoji']} {pantheon_info['name']} - {pantheon_info['role']}"
                            else:
                                clean_name = self.clean_model_name(file, os.path.getsize(full_path))
                                display_name = f"📁 {clean_name}"
                            
                            if display_name not in self.model_map:
                                self.model_map[display_name] = full_path
                                models.append(display_name)
            except Exception as e:
                continue

        if not models:
            # Fallback: Add option to browse for model
            self.model_map = {'🔍 Browse for model...': 'browse'}
            return list(self.model_map.keys())

        return sorted(models)
    
    def write_file_with_backup(self, file_path: str, content: str) -> str:
        """Write file with automatic backup"""
        full_path = os.path.join(self.workspace_path, file_path)
        
        if os.path.exists(full_path):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{os.path.basename(file_path)}.{timestamp}.backup"
            backup_full_path = os.path.join(self.backup_path, backup_name)
            
            try:
                shutil.copy2(full_path, backup_full_path)
                self.message_queue.put(('ai', f"Backed up: {backup_name}"))
            except Exception as e:
                self.message_queue.put(('ai', f"Backup failed: {e}"))
        
        return self.original_write_file(file_path, content)
    
    def setup_menu_bar(self):
        """Create comprehensive menu bar with all Phase 1-6 features"""
        menubar = tk.Menu(self.root, bg='#2d2d2d', fg='#ffffff')
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='#ffffff')
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New File (Ctrl+N)", command=self.new_file)
        file_menu.add_command(label="Open File (Ctrl+O)", command=lambda: self.open_file())
        file_menu.add_command(label="Save (Ctrl+S)", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Load Project", command=self.load_project)
        file_menu.add_command(label="Scan Project", command=self.scan_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='#ffffff')
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Find (Ctrl+F)", 
                             command=lambda: self.search_dialog.show_find() if hasattr(self, 'search_dialog') else None)
        edit_menu.add_command(label="Replace (Ctrl+H)",
                             command=lambda: self.search_dialog.show_replace() if hasattr(self, 'search_dialog') else None)
        edit_menu.add_separator()
        edit_menu.add_command(label="Undo (Ctrl+Z)", command=lambda: None)
        edit_menu.add_command(label="Redo (Ctrl+Y)", command=lambda: None)
        
        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='#ffffff')
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="↩️ Undo Last AI Change (Ctrl+Shift+Z)", command=self.undo_last_ai_change)
        view_menu.add_separator()
        view_menu.add_command(label="Toggle Terminal", command=lambda: self.toggle_terminal() if hasattr(self, 'toggle_terminal') else None)
        view_menu.add_command(label="Show File Tree", command=lambda: None)
        view_menu.add_separator()
        view_menu.add_command(label="Themes...", command=self.show_theme_selector)
        view_menu.add_command(label="Minimap", command=lambda: None)
        
        # Git Menu (Phase 2)
        git_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='#ffffff')
        menubar.add_cascade(label="Git", menu=git_menu)
        git_menu.add_command(label="Show Git Panel", command=self.show_git_panel)
        git_menu.add_command(label="Commit...", command=lambda: None)
        git_menu.add_command(label="Push", command=lambda: None)
        git_menu.add_command(label="Pull", command=lambda: None)
        git_menu.add_command(label="View Diff...", command=self.show_diff_viewer)
        git_menu.add_separator()
        git_menu.add_command(label="Initialize Repository", command=lambda: None)
        
        # Tools Menu (Phase 3)
        tools_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='#ffffff')
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="🔧 Error Recovery (Ctrl+Shift+E)", command=self.show_error_recovery)
        tools_menu.add_command(label="💾 Browse Backups (Ctrl+Shift+B)", command=self.show_backup_browser)
        tools_menu.add_command(label="📦 Scan Dependencies", command=self.scan_dependencies)
        tools_menu.add_separator()
        tools_menu.add_command(label="📋 Task Planner (Ctrl+Shift+P)", command=self.show_task_planner)
        tools_menu.add_command(label="Snippets Manager", command=self.show_snippets_manager)
        tools_menu.add_command(label="Project Templates", command=self.show_project_templates)
        tools_menu.add_command(label="Error List", command=self.show_error_list)
        tools_menu.add_separator()
        tools_menu.add_command(label="Debugger", command=self.show_debugger)
        tools_menu.add_command(label="Extensions", command=self.show_extensions_manager)
        
        # AI Menu (Phase 4-6)
        ai_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='#ffffff')
        menubar.add_cascade(label="AI", menu=ai_menu)
        ai_menu.add_command(label="AI Composer (Ctrl+K)", command=self.toggle_composer)
        ai_menu.add_command(label="🧠 Session Memory (Ctrl+Shift+M)", command=self.show_session_memory)
        ai_menu.add_separator()
        ai_menu.add_command(label="Model Manager", command=self.show_model_manager)
        ai_menu.add_command(label="⚙️ Configure Workflow Models", command=self.configure_workflow_models)
        ai_menu.add_separator()
        ai_menu.add_command(label="🚀 Start DeathAIAUS Backend", command=self.start_deathaiaus_backend)
        ai_menu.add_command(label="🔄 Restart ReapGate", command=self.restart_reapgate)
        ai_menu.add_command(label="🔍 Test Backend Connection", command=self.test_backend_connection)
        ai_menu.add_command(label="🏛️ Death's Pantheon", command=self.show_pantheon_viewer)
        ai_menu.add_command(label="📊 Model Performance Stats", command=self.show_model_stats)
        ai_menu.add_checkbutton(label="Enable Inline Suggestions", command=self.toggle_inline_suggestions)
        ai_menu.add_separator()
        ai_menu.add_command(label="Settings", command=self.show_settings_dialog)
        
        # Project Menu (Phase 5)
        project_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='#ffffff')
        menubar.add_cascade(label="Project", menu=project_menu)
        project_menu.add_command(label="Export Project", command=self.show_export_project)
        project_menu.add_command(label="Cloud Sync Settings", command=self.show_cloud_sync)
        project_menu.add_command(label="Reindex Project", command=self.reindex_project)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='#ffffff')
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts_help)
        help_menu.add_command(label="About", command=self.show_about)
    
    def setup_toolbar(self):
        """Setup prominent toolbar with quick access buttons"""
        toolbar = tk.Frame(self.root, bg='#2d2d2d', height=50)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        toolbar.pack_propagate(False)
        
        # Left side - Critical actions
        left_frame = tk.Frame(toolbar, bg='#2d2d2d')
        left_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Fix Errors button (red, prominent)
        self.fix_errors_btn = tk.Button(left_frame, text="🔧 Fix Errors",
                                       command=self.show_error_recovery,
                                       bg='#ff6666', fg='white',
                                       font=('Segoe UI', 10, 'bold'),
                                       relief=tk.FLAT, padx=20, pady=8,
                                       cursor='hand2')
        self.fix_errors_btn.pack(side=tk.LEFT, padx=5)
        
        # Undo AI button (orange, important)
        tk.Button(left_frame, text="↩️ Undo AI",
                 command=self.undo_last_ai_change,
                 bg='#ff9900', fg='white',
                 font=('Segoe UI', 10, 'bold'),
                 relief=tk.FLAT, padx=20, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # Separator
        tk.Frame(left_frame, bg='#444444', width=2, height=30).pack(side=tk.LEFT, padx=10)
        
        # Backups button (blue)
        tk.Button(left_frame, text="💾 Backups",
                 command=self.show_backup_browser,
                 bg='#0066cc', fg='white',
                 font=('Segoe UI', 10),
                 relief=tk.FLAT, padx=20, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # Memory button (cyan)
        tk.Button(left_frame, text="🧠 Memory",
                 command=self.show_session_memory,
                 bg='#00aaff', fg='white',
                 font=('Segoe UI', 10),
                 relief=tk.FLAT, padx=20, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # Model Stats button (purple)
        tk.Button(left_frame, text="📊 Model Stats",
                 command=self.show_model_stats,
                 bg='#9900ff', fg='white',
                 font=('Segoe UI', 10),
                 relief=tk.FLAT, padx=20, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # Right side - Status indicators
        right_frame = tk.Frame(toolbar, bg='#2d2d2d')
        right_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Error count indicator
        self.error_count_var = tk.StringVar(value="✓ No Errors")
        self.error_indicator = tk.Label(right_frame, textvariable=self.error_count_var,
                                       bg='#00aa00', fg='white',
                                       font=('Segoe UI', 9, 'bold'),
                                       padx=10, pady=5, cursor='hand2')
        self.error_indicator.pack(side=tk.RIGHT, padx=5)
        self.error_indicator.bind('<Button-1>', lambda e: self.show_error_recovery())
    
    def show_shortcuts_help(self):
        """Show keyboard shortcuts help"""
        shortcuts_text = """
        Keyboard Shortcuts:
        
        Ctrl+N - New File
        Ctrl+O - Open File
        Ctrl+S - Save File
        Ctrl+W - Close Tab
        Ctrl+F - Find
        Ctrl+H - Replace
        Ctrl+K - AI Composer
        Ctrl+Tab - Next Tab
        Ctrl+/ - Toggle Comment
        Ctrl+D - Duplicate Line
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        DeathAIAUS IDE F.C
        Version: 3.0 - Cursor Style Edition
        
        All Phase 1-6 Features Integrated:
        - 26 Major Features
        - Cursor-style Layout
        - Built-in AI
        - Professional Tools
        
        Copyright (c) 2025 DeathAIAUS
        All rights reserved.
        """
        messagebox.showinfo("About", about_text)
    
    # Menu Helper Methods
    def show_theme_selector(self):
        """Show theme selector dialog"""
        try:
            if hasattr(self, 'theme_manager') and self.theme_manager:
                # Use simple theme selector for easy switching
                from components.simple_theme_selector import SimpleThemeSelector
                SimpleThemeSelector(self.root, self.theme_manager)
            else:
                messagebox.showinfo("Themes", "Theme manager not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open themes: {e}")
    
    def show_git_panel(self):
        """Show/toggle git panel"""
        try:
            if hasattr(self, 'git_panel') and self.git_panel:
                messagebox.showinfo("Git", "Git panel feature coming soon!")
            else:
                messagebox.showinfo("Git", "Git integration not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open git panel: {e}")
    
    def show_diff_viewer(self):
        """Show diff viewer for current file"""
        try:
            if not self.code_editor:
                messagebox.showinfo("Diff Viewer", "No file open to diff")
                return
            
            current_file = getattr(self.tabs.current_editor, 'file_path', None) if hasattr(self, 'tabs') else None
            if not current_file or not os.path.exists(current_file):
                messagebox.showinfo("Diff Viewer", "Current file has no saved version")
                return
            
            # Read saved version
            with open(current_file, 'r', encoding='utf-8') as f:
                saved_content = f.read()
            
            # Get current content
            current_content = self.code_editor.get('1.0', 'end-1c')
            
            # Show diff
            from components.diff_viewer import DiffViewer
            DiffViewer(self.root, current_file, saved_content, current_content, "Unsaved Changes")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show diff: {e}")
    
    def show_snippets_manager(self):
        """Show snippets manager"""
        try:
            if hasattr(self, 'snippet_manager') and self.snippet_manager:
                messagebox.showinfo("Snippets", "Snippets manager coming soon!")
            else:
                messagebox.showinfo("Snippets", "Snippets manager not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open snippets: {e}")
    
    def show_project_templates(self):
        """Show project templates"""
        try:
            if hasattr(self, 'project_templates') and self.project_templates:
                messagebox.showinfo("Templates", "Project templates coming soon!")
            else:
                messagebox.showinfo("Templates", "Project templates not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open templates: {e}")
    
    def show_error_list(self):
        """Show error list panel"""
        try:
            if hasattr(self, 'error_detector') and self.error_detector:
                messagebox.showinfo("Errors", "Error list coming soon!")
            else:
                messagebox.showinfo("Errors", "Error detector not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open error list: {e}")
    
    def show_debugger(self):
        """Show debugger panel"""
        try:
            messagebox.showinfo("Debugger", "Debugger feature coming soon!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open debugger: {e}")
    
    def show_extensions_manager(self):
        """Show extensions manager"""
        try:
            if hasattr(self, 'extension_manager') and self.extension_manager:
                messagebox.showinfo("Extensions", "Extensions manager coming soon!")
            else:
                messagebox.showinfo("Extensions", "Extensions not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open extensions: {e}")
    
    def show_model_stats(self):
        """Show model performance statistics"""
        try:
            if hasattr(self, 'performance_tracker') and self.performance_tracker:
                ModelPerformancePanel(self.root, self.performance_tracker)
            else:
                messagebox.showinfo("Model Stats", "Performance tracker not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show model stats: {e}")
    
    def show_model_manager(self):
        """Show AI model manager"""
        try:
            # Create a nice dialog window
            dialog = tk.Toplevel(self.root)
            dialog.title("AI Model Manager")
            dialog.geometry("600x500")
            dialog.configure(bg='#2d2d2d')
            
            # Header
            header = tk.Frame(dialog, bg='#1e1e1e', height=60)
            header.pack(fill=tk.X)
            header.pack_propagate(False)
            
            tk.Label(header, text=f"🤖 AI Models ({len(self.available_models)} detected)", 
                    font=('Segoe UI', 14, 'bold'),
                    fg='#00ff00', bg='#1e1e1e').pack(pady=15)
            
            # Model list
            list_frame = tk.Frame(dialog, bg='#2d2d2d')
            list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            model_listbox = tk.Listbox(
                list_frame,
                bg='#1e1e1e',
                fg='#ffffff',
                selectbackground='#0066cc',
                font=('Segoe UI', 10),
                bd=0,
                yscrollcommand=scrollbar.set
            )
            model_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=model_listbox.yview)
            
            # Add models
            current_model = self.coder_model.get()
            for i, model in enumerate(self.available_models, 1):
                prefix = "✓ " if model == current_model else "   "
                model_listbox.insert(tk.END, f"{prefix}{i}. {model}")
            
            # Info
            info_frame = tk.Frame(dialog, bg='#2d2d2d')
            info_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
            
            tk.Label(info_frame, 
                    text="💡 Use the dropdown in the AI panel (bottom right) to switch models",
                    font=('Segoe UI', 9, 'italic'), 
                    fg='#888888', bg='#2d2d2d').pack()
            
            # Workflow configuration section
            workflow_section = tk.Frame(dialog, bg='#2d2d2d')
            workflow_section.pack(fill=tk.X, padx=20, pady=(10, 10))
            
            tk.Label(workflow_section, text="⚙️ Configure Workflows",
                    font=('Segoe UI', 11, 'bold'),
                    fg='#00ff00', bg='#2d2d2d').pack(anchor='w', pady=(0, 5))
            
            tk.Label(workflow_section, text="Assign models to specific workflow steps:",
                    font=('Segoe UI', 9),
                    fg='#cccccc', bg='#2d2d2d').pack(anchor='w', pady=(0, 10))
            
            workflows_btn_frame = tk.Frame(workflow_section, bg='#2d2d2d')
            workflows_btn_frame.pack(fill=tk.X)
            
            workflows = [
                ("Coding Projects", "coding"),
                ("Large Projects", "large"),
                ("Quick Tasks", "quick"),
                ("Security Audit", "security")
            ]
            
            for i, (workflow_name, workflow_key) in enumerate(workflows):
                btn = tk.Button(workflows_btn_frame, text=f"⚙️ {workflow_name}",
                              command=lambda wf=workflow_name: [self.configure_workflow(wf), dialog.lift()],
                              bg='#6366f1', fg='#ffffff',
                              font=('Segoe UI', 9, 'bold'),
                              relief=tk.FLAT, padx=12, pady=6,
                              cursor='hand2')
                if i < 2:
                    btn.pack(side=tk.LEFT, padx=2, pady=2)
                else:
                    btn.pack(side=tk.LEFT, padx=2, pady=2)
            
            # Close button
            tk.Button(dialog, text="Close", command=dialog.destroy,
                     bg='#3d3d3d', fg='#ffffff', 
                     font=('Segoe UI', 10),
                     relief=tk.FLAT, padx=30, pady=8).pack(pady=(0, 20))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show models: {e}")
    
    def show_pantheon_viewer(self):
        """Show the Death Pantheon - organized view of all models by tier"""
        try:
            # Create a nice dialog window
            dialog = tk.Toplevel(self.root)
            dialog.title("🏛️ Death's Pantheon - AI Model Hierarchy")
            dialog.geometry("900x700")
            dialog.configure(bg='#1e1e1e')
            
            # Header
            header = tk.Frame(dialog, bg='#0d0d0d', height=80)
            header.pack(fill=tk.X)
            header.pack_propagate(False)
            
            tk.Label(header, text="🏛️ DEATH'S PANTHEON", 
                    font=('Segoe UI', 18, 'bold'),
                    fg='#ffffff', bg='#0d0d0d').pack(pady=10)
            tk.Label(header, text="The hierarchy of AI deities at your command", 
                    font=('Segoe UI', 10, 'italic'),
                    fg='#888888', bg='#0d0d0d').pack()
            
            # Main content area with scrollbar
            main_frame = tk.Frame(dialog, bg='#1e1e1e')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            canvas = tk.Canvas(main_frame, bg='#1e1e1e', highlightthickness=0)
            scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='#1e1e1e')
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Group models by tier
            tiers = {
                "Primary": "👑 PRIMARY PANTHEON",
                "Warrior": "⚔️ WARRIOR PANTHEON",
                "Wisdom": "🧙 WISDOM PANTHEON",
                "Underworld": "🌊 UNDERWORLD PANTHEON",
                "Minor": "🔮 MINOR DEITIES",
                "Special": "🎨 SPECIAL PURPOSE"
            }
            
            pantheon = self.pantheon.get('pantheon', {})
            
            # Organize models by tier
            models_by_tier = {tier: [] for tier in tiers.keys()}
            for model_file, info in pantheon.items():
                tier = info.get('tier', 'Minor')
                models_by_tier[tier].append((model_file, info))
            
            # Display each tier
            for tier_key, tier_title in tiers.items():
                if models_by_tier[tier_key]:
                    # Tier header
                    tier_frame = tk.Frame(scrollable_frame, bg='#2d2d2d', pady=5)
                    tier_frame.pack(fill=tk.X, pady=(10, 5))
                    
                    tk.Label(tier_frame, text=tier_title,
                            font=('Segoe UI', 12, 'bold'),
                            fg='#00ff00', bg='#2d2d2d').pack(anchor='w', padx=10)
                    
                    # Models in this tier
                    for model_file, info in sorted(models_by_tier[tier_key], key=lambda x: x[1]['name']):
                        model_frame = tk.Frame(scrollable_frame, bg='#252525', relief=tk.RAISED, bd=1)
                        model_frame.pack(fill=tk.X, pady=2, padx=10)
                        
                        # Model header
                        header_line = tk.Frame(model_frame, bg='#252525')
                        header_line.pack(fill=tk.X, padx=10, pady=(8, 2))
                        
                        tk.Label(header_line, 
                                text=f"{info['emoji']} {info['name']}",
                                font=('Segoe UI', 11, 'bold'),
                                fg='#ffffff', bg='#252525').pack(side=tk.LEFT)
                        
                        tk.Label(header_line,
                                text=f"[{info['mythology']}]",
                                font=('Segoe UI', 9),
                                fg='#888888', bg='#252525').pack(side=tk.LEFT, padx=10)
                        
                        # Model details
                        tk.Label(model_frame,
                                text=f"📜 {info['title']}",
                                font=('Segoe UI', 9, 'italic'),
                                fg='#cccccc', bg='#252525').pack(anchor='w', padx=10)
                        
                        tk.Label(model_frame,
                                text=f"⚡ Role: {info['role']}",
                                font=('Segoe UI', 9),
                                fg='#00aaff', bg='#252525').pack(anchor='w', padx=10)
                        
                        tk.Label(model_frame,
                                text=f"📊 {info['size']} | {info['power']}",
                                font=('Segoe UI', 8),
                                fg='#666666', bg='#252525').pack(anchor='w', padx=10, pady=(0, 8))
            
            # Usage recommendations with configure buttons (inside scrollable area)
            rec_frame = tk.Frame(scrollable_frame, bg='#2d2d2d', pady=10)
            rec_frame.pack(fill=tk.X, padx=10, pady=(20, 10))
            
            tk.Label(rec_frame, text="💡 Configurable Workflows:",
                    font=('Segoe UI', 11, 'bold'),
                    fg='#00ff00', bg='#2d2d2d').pack(anchor='w', pady=(0, 10))
            
            workflows = [
                ("Coding Projects", "Generate → Analyze → Validate", "THANATOS → MORRIGAN → ANUBIS"),
                ("Large Projects", "Plan → Implement → Review", "ODIN → OSIRIS → YAMA"),
                ("Quick Tasks", "Prototype → Task → Logic", "IZANAMI → MORANA → PSYCHE"),
                ("Security Audit", "Detect → Destroy → Test", "SEKHMET → KALI → ARES")
            ]
            
            for workflow_name, steps, defaults in workflows:
                wf_frame = tk.Frame(rec_frame, bg='#1e1e1e', relief=tk.RAISED, bd=1)
                wf_frame.pack(fill=tk.X, pady=5)
                
                info_frame = tk.Frame(wf_frame, bg='#1e1e1e')
                info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=8)
                
                tk.Label(info_frame, text=f"🎯 {workflow_name}",
                        font=('Segoe UI', 10, 'bold'),
                        fg='#ffffff', bg='#1e1e1e').pack(anchor='w')
                
                tk.Label(info_frame, text=f"{steps}",
                        font=('Segoe UI', 9),
                        fg='#00aaff', bg='#1e1e1e').pack(anchor='w')
                
                tk.Label(info_frame, text=f"Default: {defaults}",
                        font=('Segoe UI', 8),
                        fg='#888888', bg='#1e1e1e').pack(anchor='w')
                
                tk.Button(wf_frame, text="⚙️ Configure",
                         command=lambda wf=workflow_name: self.configure_workflow(wf),
                         bg='#6366f1', fg='#ffffff',
                         font=('Segoe UI', 9, 'bold'),
                         relief=tk.FLAT, padx=15, pady=5,
                         cursor='hand2').pack(side=tk.RIGHT, padx=10, pady=8)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Close button
            tk.Button(dialog, text="Close", command=dialog.destroy,
                     bg='#3d3d3d', fg='#ffffff', 
                     font=('Segoe UI', 10, 'bold'),
                     relief=tk.FLAT, padx=40, pady=10).pack(pady=(0, 20))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show pantheon: {e}")
    
    def configure_workflow(self, workflow_name):
        """Configure model assignments for a specific workflow"""
        try:
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Configure {workflow_name} Workflow")
            dialog.geometry("700x500")
            dialog.configure(bg='#1e1e1e')
            
            # Header
            header = tk.Frame(dialog, bg='#0d0d0d', height=60)
            header.pack(fill=tk.X)
            header.pack_propagate(False)
            
            tk.Label(header, text=f"⚙️ {workflow_name}", 
                    font=('Segoe UI', 14, 'bold'),
                    fg='#ffffff', bg='#0d0d0d').pack(pady=15)
            
            # Main content
            content = tk.Frame(dialog, bg='#1e1e1e')
            content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
            
            # Define workflow steps
            workflows = {
                'Coding Projects': [
                    ('coding_generate', '1️⃣ Generate Code', 'THANATOS'),
                    ('coding_analyze', '2️⃣ Analyze Code', 'MORRIGAN'),
                    ('coding_validate', '3️⃣ Validate/Test', 'ANUBIS')
                ],
                'Large Projects': [
                    ('large_plan', '1️⃣ Plan Architecture', 'ODIN'),
                    ('large_implement', '2️⃣ Implement', 'OSIRIS'),
                    ('large_review', '3️⃣ Review Quality', 'YAMA')
                ],
                'Quick Tasks': [
                    ('quick_prototype', '1️⃣ Rapid Prototype', 'IZANAMI'),
                    ('quick_task', '2️⃣ Quick Task', 'MORANA'),
                    ('quick_logic', '3️⃣ Logic Check', 'PSYCHE')
                ],
                'Security Audit': [
                    ('security_detect', '1️⃣ Detect Threats', 'SEKHMET'),
                    ('security_destroy', '2️⃣ Destroy Vulnerabilities', 'KALI'),
                    ('security_test', '3️⃣ Aggressive Testing', 'ARES')
                ]
            }
            
            steps = workflows.get(workflow_name, [])
            dropdowns = {}
            
            for key, label, default in steps:
                step_frame = tk.Frame(content, bg='#2d2d2d', relief=tk.RAISED, bd=1)
                step_frame.pack(fill=tk.X, pady=10)
                
                tk.Label(step_frame, text=label,
                        font=('Segoe UI', 11, 'bold'),
                        fg='#ffffff', bg='#2d2d2d').pack(anchor='w', padx=15, pady=(10, 5))
                
                tk.Label(step_frame, text=f"Recommended: {default}",
                        font=('Segoe UI', 9, 'italic'),
                        fg='#888888', bg='#2d2d2d').pack(anchor='w', padx=15)
                
                # Dropdown for model selection
                var = tk.StringVar(value=self.workflow_models.get(key) or f'(Use {default})')
                combo = ttk.Combobox(step_frame, textvariable=var,
                                    values=self.available_models, width=50, state='readonly')
                combo.pack(padx=15, pady=(5, 10), fill=tk.X)
                dropdowns[key] = var
            
            # Button frame
            button_frame = tk.Frame(dialog, bg='#1e1e1e')
            button_frame.pack(fill=tk.X, padx=30, pady=(0, 20))
            
            def save_config():
                for key, var in dropdowns.items():
                    value = var.get()
                    if value and not value.startswith('(Use'):
                        self.workflow_models[key] = value
                self.save_workflow_config()
                messagebox.showinfo("Success", f"{workflow_name} workflow configured!")
                dialog.destroy()
            
            def reset_defaults():
                for key, label, default in steps:
                    self.workflow_models[key] = None
                    if key in dropdowns:
                        dropdowns[key].set(f'(Use {default})')
                self.save_workflow_config()
                messagebox.showinfo("Reset", "Workflow reset to default recommendations")
            
            tk.Button(button_frame, text="💾 Save Configuration",
                     command=save_config,
                     bg='#6366f1', fg='#ffffff',
                     font=('Segoe UI', 10, 'bold'),
                     relief=tk.FLAT, padx=20, pady=10).pack(side=tk.RIGHT, padx=5)
            
            tk.Button(button_frame, text="🔄 Reset to Defaults",
                     command=reset_defaults,
                     bg='#3d3d3d', fg='#ffffff',
                     font=('Segoe UI', 10),
                     relief=tk.FLAT, padx=20, pady=10).pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to configure workflow: {e}")
    
    def toggle_inline_suggestions(self):
        """Toggle inline AI suggestions"""
        try:
            if hasattr(self, 'inline_suggestions') and self.inline_suggestions:
                messagebox.showinfo("Inline AI", "Inline suggestions feature coming soon!")
            else:
                messagebox.showinfo("Inline AI", "Inline suggestions not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle suggestions: {e}")
    
    def show_ai_memory(self):
        """Show AI conversation memory"""
        try:
            if hasattr(self, 'ai_memory') and self.ai_memory:
                messagebox.showinfo("AI Memory", "AI memory viewer coming soon!")
            else:
                messagebox.showinfo("AI Memory", "AI memory not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show AI memory: {e}")
    
    def show_export_project(self):
        """Show project export dialog"""
        try:
            if hasattr(self, 'project_exporter') and self.project_exporter:
                messagebox.showinfo("Export", "Project export coming soon!")
            else:
                messagebox.showinfo("Export", "Project exporter not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")
    
    def show_cloud_sync(self):
        """Show cloud sync settings"""
        try:
            if hasattr(self, 'cloud_sync') and self.cloud_sync:
                messagebox.showinfo("Cloud Sync", "Cloud sync settings coming soon!")
            else:
                messagebox.showinfo("Cloud Sync", "Cloud sync not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open cloud sync: {e}")
    
    def reindex_project(self):
        """Reindex project files"""
        try:
            if hasattr(self, 'background_indexer') and self.background_indexer:
                messagebox.showinfo("Indexing", "Reindexing project in background...")
                # Trigger reindex
            else:
                messagebox.showinfo("Indexing", "Background indexer not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reindex: {e}")
    
    # NEW FEATURE METHODS - Wire everything together
    def show_error_recovery(self):
        """Show error recovery panel"""
        try:
            from components.error_recovery import ErrorRecoveryPanel
            ErrorRecoveryPanel(self.root, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open error recovery: {e}")
    
    def show_session_memory(self):
        """Show session memory UI"""
        try:
            from components.session_memory_ui import SessionMemoryPanel
            SessionMemoryPanel(self.root, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open session memory: {e}")
    
    def show_backup_browser(self):
        """Show backup browser"""
        try:
            from components.backup_browser import BackupBrowser
            BackupBrowser(self.root, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open backup browser: {e}")
    
    def undo_last_ai_change(self):
        """Undo the last AI modification"""
        import os
        backup_dir = os.path.join(self.workspace_path, 'ai_backups')
        
        if not os.path.exists(backup_dir):
            messagebox.showinfo("No Backups", 
                              "No backup folder found.\n\nBackups are created automatically when AI modifies files.")
            return
        
        backups = [f for f in os.listdir(backup_dir) if f.endswith('.bak')]
        if not backups:
            messagebox.showinfo("No Backups", 
                              "No AI changes to undo.\n\nBackups are created when AI modifies files.")
            return
        
        # Sort by modification time (newest first)
        backups.sort(key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)), reverse=True)
        
        # Show backup browser with newest backup pre-selected
        self.show_backup_browser()
        messagebox.showinfo("Undo AI Change", 
                          f"Found {len(backups)} backup(s).\n\n"
                          f"Most recent: {backups[0]}\n\n"
                          f"Select and restore to undo AI changes.")
    
    def show_task_planner(self):
        """Show task planner UI"""
        try:
            if TaskPlannerPanel:
                TaskPlannerPanel(self.root, self)
            else:
                messagebox.showinfo("Task Planner", "Task planner not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open task planner: {e}")
    
    def scan_dependencies(self):
        """Scan for missing dependencies"""
        try:
            # Get current file content
            if not self.code_editor:
                messagebox.showinfo("Scan Dependencies", "No file open to scan")
                return
            
            content = self.code_editor.get('1.0', tk.END)
            
            # Simple import detection (Python example)
            import re
            imports = re.findall(r'^\s*(?:from|import)\s+(\w+)', content, re.MULTILINE)
            
            if not imports:
                messagebox.showinfo("Scan Dependencies", "No imports found in current file")
                return
            
            # Check which are installed
            import importlib
            missing = []
            for module in set(imports):
                try:
                    importlib.import_module(module)
                except ImportError:
                    missing.append(module)
            
            if missing:
                result = messagebox.askyesno("Missing Dependencies",
                                            f"Found {len(missing)} missing dependencies:\n\n" +
                                            "\n".join(f"• {m}" for m in missing) +
                                            "\n\nInstall them now?")
                if result:
                    self.install_dependencies(missing)
            else:
                messagebox.showinfo("Dependencies", 
                                  f"✓ All {len(set(imports))} imports are available!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scan dependencies: {e}")
    
    def install_dependencies(self, packages):
        """Install missing dependencies"""
        import subprocess
        
        try:
            for package in packages:
                self.log_terminal(f"Installing {package}...\n")
                result = subprocess.run(['pip', 'install', package],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.log_terminal(f"✓ Installed {package}\n")
                else:
                    self.log_terminal(f"✗ Failed to install {package}\n")
            
            messagebox.showinfo("Installation Complete", 
                              f"Attempted to install {len(packages)} package(s).\n\n"
                              f"Check terminal for details.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install dependencies: {e}")
    
    def setup_keyboard_shortcuts(self):
        """Setup all keyboard shortcuts"""
        # Existing shortcuts are bound elsewhere, add new ones here
        self.root.bind('<Control-Shift-E>', lambda e: self.show_error_recovery())
        self.root.bind('<Control-Shift-e>', lambda e: self.show_error_recovery())
        
        self.root.bind('<Control-Shift-Z>', lambda e: self.undo_last_ai_change())
        self.root.bind('<Control-Shift-z>', lambda e: self.undo_last_ai_change())
        
        self.root.bind('<Control-Shift-M>', lambda e: self.show_session_memory())
        self.root.bind('<Control-Shift-m>', lambda e: self.show_session_memory())
        
        self.root.bind('<Control-Shift-B>', lambda e: self.show_backup_browser())
        self.root.bind('<Control-Shift-b>', lambda e: self.show_backup_browser())
        
        self.root.bind('<Control-Shift-P>', lambda e: self.show_task_planner())
        self.root.bind('<Control-Shift-p>', lambda e: self.show_task_planner())
    
    def setup_gui(self):
        """Setup GUI with all Phase 1-6 features"""
        # Create comprehensive menu bar
        self.setup_menu_bar()
        
        # Add prominent toolbar with quick access buttons
        self.setup_toolbar()
        
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left: File tree
        self.setup_file_tree(main_paned)
        
        # Center: Editor + Terminal
        self.setup_center_panel(main_paned)
        
        # Right: AI + Feasibility
        self.setup_ai_panel(main_paned)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Honesty is our policy")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # ReapGate status indicator
        self.reapgate_status_label = tk.Label(
            self.root,
            text="⚪ ReapGate: Checking...",
            fg='#888888',
            bg='#2b2b2b',
            font=('Consolas', 9)
        )
        self.reapgate_status_label.pack(side=tk.BOTTOM, anchor=tk.E, padx=5, pady=2)
        
        # Start checker
        self.check_reapgate_status()
    
    def setup_file_tree(self, parent):
        """File tree with restore button"""
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
        """Editor and terminal with resizable split"""
        center_frame = ttk.Frame(parent)
        parent.add(center_frame, weight=2)
        
        # Toolbar
        toolbar = ttk.Frame(center_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        self.file_label = ttk.Label(toolbar, text="No file open", font=('Arial', 9))
        self.file_label.pack(side=tk.LEFT, padx=5)

        ttk.Button(toolbar, text="Load Project", command=self.load_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Scan Project", command=self.scan_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔍 Find", command=lambda: self.search_dialog.show_find() if hasattr(self, 'search_dialog') else None).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📝 New", command=lambda: self.tabs.new_file() if hasattr(self, 'tabs') else None).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Save", command=self.save_file).pack(side=tk.RIGHT, padx=2)
        ttk.Button(toolbar, text="Run", command=self.run_current_file).pack(side=tk.RIGHT, padx=2)
        
        # Create resizable paned window for editor and terminal
        editor_terminal_paned = ttk.PanedWindow(center_frame, orient=tk.VERTICAL)
        editor_terminal_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Editor - Multi-file tab system with enhanced editor
        editor_container = ttk.Frame(editor_terminal_paned)
        editor_terminal_paned.add(editor_container, weight=3)

        self.tabs = FileTabs(editor_container, self)
        self.tabs.pack(fill=tk.BOTH, expand=True)

        # Terminal (resizable)
        terminal_container = ttk.Frame(editor_terminal_paned)
        editor_terminal_paned.add(terminal_container, weight=1)

        # Terminal header with collapse button
        terminal_header = ttk.Frame(terminal_container)
        terminal_header.pack(fill=tk.X)

        ttk.Label(terminal_header, text="Terminal Output", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5, pady=2)
        self.terminal_collapse_btn = ttk.Button(terminal_header, text="▼ Hide", width=8,
                                               command=lambda: self.toggle_terminal())
        self.terminal_collapse_btn.pack(side=tk.RIGHT, padx=5, pady=2)

        self.terminal_output = scrolledtext.ScrolledText(terminal_container, wrap=tk.WORD,
                                                         font=('Consolas', 9),
                                                         bg='#1e1e1e', fg='#00ff00',
                                                         height=10)
        self.terminal_output.pack(fill=tk.BOTH, expand=True)

        # Store references for collapse functionality
        self.editor_terminal_paned = editor_terminal_paned
        self.terminal_container = terminal_container
        self.terminal_visible = True
    
    def setup_ai_panel(self, parent):
        """Cursor.ink-style AI panel - Clean and minimal"""
        right_frame = tk.Frame(parent, width=400, bg='#1e1e1e')
        parent.add(right_frame, weight=0)
        
        # Clean header like Cursor
        header = tk.Frame(right_frame, bg='#252525', height=45)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Title with icon
        title_frame = tk.Frame(header, bg='#252525')
        title_frame.pack(side=tk.LEFT, padx=15, pady=10)
        
        tk.Label(title_frame, text="🤖", font=('Segoe UI', 16), 
                bg='#252525', fg='#ffffff').pack(side=tk.LEFT, padx=(0,8))
        tk.Label(title_frame, text="AI Chat", font=('Segoe UI', 13, 'bold'),
                bg='#252525', fg='#ffffff').pack(side=tk.LEFT)
        
        # Settings button (top right)
        settings_btn = tk.Button(header, text="⚙", font=('Segoe UI', 14),
                                bg='#252525', fg='#888888', bd=0, cursor='hand2',
                                activebackground='#2d2d2d', activeforeground='#ffffff',
                                command=self.show_settings_dialog)
        settings_btn.pack(side=tk.RIGHT, padx=10)
        
        # Main AI Chat (takes full space like Cursor)
        self.ai_chat = AIChatInterface(right_frame, self)
        self.ai_chat.pack(fill=tk.BOTH, expand=True)
        
        # Quick settings bar at bottom (minimal)
        settings_bar = tk.Frame(right_frame, bg='#1a1a1a', height=35)
        settings_bar.pack(fill=tk.X, side=tk.BOTTOM)
        settings_bar.pack_propagate(False)
        
        # Model selector (like Cursor's model dropdown)
        tk.Label(settings_bar, text="Model:", bg='#1a1a1a', fg='#888888',
                font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(10,5))
        
        self.coder_model = tk.StringVar(value=self.available_models[0] if self.available_models else 'default')
        model_combo = ttk.Combobox(settings_bar, textvariable=self.coder_model,
                                   values=self.available_models, width=20, state='readonly')
        model_combo.pack(side=tk.LEFT, padx=5)
        
        # Language selector
        default_lang = self.welcome_data.get('language', 'Python')
        self.language_var = tk.StringVar(value=default_lang)
        
        # Initialize other model roles (separate StringVars for Settings)
        self.planner_model = tk.StringVar(value=self.available_models[0] if self.available_models else 'default')
        self.tester_model = tk.StringVar(value=self.available_models[0] if self.available_models else 'default')
        self.reviewer_model = tk.StringVar(value=self.available_models[0] if self.available_models else 'default')
        
        # Create a hidden text widget for methods that still reference project_description
        self.project_description = tk.Text(right_frame, height=1)
        self.project_description.pack_forget()  # Hide it
        
        # Create dummy widgets for backward compatibility
        self.feasibility_btn = tk.Button(right_frame)
        self.analyze_btn = tk.Button(right_frame)
        self.build_btn = tk.Button(right_frame)
        self.test_btn = tk.Button(right_frame)
        self.feasibility_score_label = tk.Label(right_frame)
        self.complexity_label = tk.Label(right_frame)
        self.time_estimate_label = tk.Label(right_frame)
        
        # Hide all dummy widgets
        for widget in [self.feasibility_btn, self.analyze_btn, self.build_btn, self.test_btn,
                      self.feasibility_score_label, self.complexity_label, self.time_estimate_label]:
            widget.pack_forget()
        
        # Create composer panel (Cursor-style bottom popup)
        self.setup_composer_panel()
    
    def show_settings_dialog(self):
        """Show settings dialog (like Cursor's settings)"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Settings")
        dialog.geometry("500x600")
        dialog.configure(bg='#1e1e1e')
        dialog.transient(self.root)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (250)
        y = (dialog.winfo_screenheight() // 2) - (300)
        dialog.geometry(f"500x600+{x}+{y}")
        
        # Title
        title_frame = tk.Frame(dialog, bg='#252525', height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="⚙️  Settings", font=('Segoe UI', 14, 'bold'),
                bg='#252525', fg='#ffffff').pack(side=tk.LEFT, padx=20, pady=15)
        
        # Content with tabs
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Models
        models_tab = tk.Frame(notebook, bg='#1e1e1e')
        notebook.add(models_tab, text="Models")
        
        tk.Label(models_tab, text="Core AI Model Roles", font=('Segoe UI', 11, 'bold'),
                bg='#1e1e1e', fg='#ffffff').pack(pady=15)
        
        tk.Label(models_tab, text="Assign models to common development roles:",
                font=('Segoe UI', 9), fg='#888888', bg='#1e1e1e').pack(pady=(0, 10))
        
        # Coder model
        coder_frame = tk.Frame(models_tab, bg='#252525')
        coder_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(coder_frame, text="💻 Coder (Code Generation):", bg='#252525', fg='#cccccc',
                font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=10, pady=5)
        ttk.Combobox(coder_frame, textvariable=self.coder_model,
                    values=self.available_models, width=40).pack(padx=10, pady=5)
        tk.Label(coder_frame, text="Recommended: THANATOS (22B)", 
                font=('Segoe UI', 8), fg='#666666', bg='#252525').pack(anchor='w', padx=10, pady=(0, 5))
        
        # Planner model
        planner_frame = tk.Frame(models_tab, bg='#252525')
        planner_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(planner_frame, text="🗺️ Planner (Architecture & Design):", bg='#252525', fg='#cccccc',
                font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=10, pady=5)
        ttk.Combobox(planner_frame, textvariable=self.planner_model,
                    values=self.available_models, width=40).pack(padx=10, pady=5)
        tk.Label(planner_frame, text="Recommended: ODIN (13B)", 
                font=('Segoe UI', 8), fg='#666666', bg='#252525').pack(anchor='w', padx=10, pady=(0, 5))
        
        # Tester model
        tester_frame = tk.Frame(models_tab, bg='#252525')
        tester_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(tester_frame, text="🧪 Tester (Validation & QA):", bg='#252525', fg='#cccccc',
                font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=10, pady=5)
        ttk.Combobox(tester_frame, textvariable=self.tester_model,
                    values=self.available_models, width=40).pack(padx=10, pady=5)
        tk.Label(tester_frame, text="Recommended: ANUBIS (1.2B)", 
                font=('Segoe UI', 8), fg='#666666', bg='#252525').pack(anchor='w', padx=10, pady=(0, 5))
        
        # Reviewer model
        reviewer_frame = tk.Frame(models_tab, bg='#252525')
        reviewer_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(reviewer_frame, text="📋 Reviewer (Code Review & Quality):", bg='#252525', fg='#cccccc',
                font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=10, pady=5)
        ttk.Combobox(reviewer_frame, textvariable=self.reviewer_model,
                    values=self.available_models, width=40).pack(padx=10, pady=5)
        tk.Label(reviewer_frame, text="Recommended: YAMA (13B)", 
                font=('Segoe UI', 8), fg='#666666', bg='#252525').pack(anchor='w', padx=10, pady=(0, 5))
        
        # Add workflow configuration link
        workflow_info = tk.Frame(models_tab, bg='#1e1e1e')
        workflow_info.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        tk.Label(workflow_info, text="💡 Advanced: Configure Workflows", 
                font=('Segoe UI', 10, 'bold'),
                bg='#1e1e1e', fg='#00ff00').pack(anchor='w')
        
        tk.Label(workflow_info, text="Assign specific models to each workflow step:",
                font=('Segoe UI', 9),
                bg='#1e1e1e', fg='#cccccc').pack(anchor='w', pady=(5,10))
        
        workflows_btn_frame = tk.Frame(models_tab, bg='#1e1e1e')
        workflows_btn_frame.pack(fill=tk.X, padx=20)
        
        workflows = [
            ("Coding Projects", "coding"),
            ("Large Projects", "large"),
            ("Quick Tasks", "quick"),
            ("Security Audit", "security")
        ]
        
        for workflow_name, workflow_key in workflows:
            btn = tk.Button(workflows_btn_frame, text=f"⚙️ {workflow_name}",
                          command=lambda wf=workflow_name: [self.configure_workflow(wf), dialog.lift()],
                          bg='#6366f1', fg='#ffffff',
                          font=('Segoe UI', 9, 'bold'),
                          relief=tk.FLAT, padx=15, pady=8,
                          cursor='hand2')
            btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Tab 2: Language & Behavior
        behavior_tab = tk.Frame(notebook, bg='#1e1e1e')
        notebook.add(behavior_tab, text="Behavior")
        
        tk.Label(behavior_tab, text="Default Language", font=('Segoe UI', 11, 'bold'),
                bg='#1e1e1e', fg='#ffffff').pack(pady=15)
        
        lang_frame = tk.Frame(behavior_tab, bg='#252525')
        lang_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(lang_frame, text="Programming Language:", bg='#252525', fg='#cccccc',
                font=('Segoe UI', 10)).pack(anchor='w', padx=10, pady=5)
        ttk.Combobox(lang_frame, textvariable=self.language_var, 
                    values=list(self.languages.keys()), width=40, state='readonly').pack(padx=10, pady=5)
        
        # Auto-approve settings
        tk.Label(behavior_tab, text="Approval Settings", font=('Segoe UI', 11, 'bold'),
                bg='#1e1e1e', fg='#ffffff').pack(pady=(20,10))
        
        approval_frame = tk.Frame(behavior_tab, bg='#252525')
        approval_frame.pack(fill=tk.X, padx=20, pady=10)

        self.auto_approve_var = tk.BooleanVar(value=self.auto_approve_commands)
        self.auto_approve_files_var = tk.BooleanVar(value=self.auto_approve_file_changes)
        
        tk.Checkbutton(approval_frame, text="Auto-approve commands",
                                        variable=self.auto_approve_var,
                      bg='#252525', fg='#cccccc', selectcolor='#1e1e1e',
                      activebackground='#252525', font=('Segoe UI', 10)).pack(anchor='w', padx=10, pady=5)
        
        tk.Checkbutton(approval_frame, text="Auto-approve file changes (⚠️ Not recommended)",
                      variable=self.auto_approve_files_var,
                      bg='#252525', fg='#cccccc', selectcolor='#1e1e1e',
                      activebackground='#252525', font=('Segoe UI', 10)).pack(anchor='w', padx=10, pady=5)
        
        tk.Label(approval_frame, text="💡 Leave OFF to review changes like Cursor",
                font=('Segoe UI', 9), bg='#252525', fg='#888888').pack(anchor='w', padx=10, pady=(5,10))
        
        # Close button
        close_btn = tk.Button(dialog, text="Close", command=dialog.destroy,
                             bg='#0066cc', fg='white', font=('Segoe UI', 10, 'bold'),
                             bd=0, padx=30, pady=10, cursor='hand2')
        close_btn.pack(pady=15)
    
    def setup_composer_panel(self):
        """Create Cursor-style composer panel (bottom popup)"""
        # Composer panel (initially hidden)
        self.composer_visible = False
        self.composer_panel = tk.Frame(self.root, bg='#252525', height=300)
        
        # Composer header
        composer_header = tk.Frame(self.composer_panel, bg='#2d2d2d', height=40)
        composer_header.pack(fill=tk.X)
        composer_header.pack_propagate(False)
        
        tk.Label(composer_header, text="✨ AI Composer", font=('Segoe UI', 12, 'bold'),
                bg='#2d2d2d', fg='#ffffff').pack(side=tk.LEFT, padx=15, pady=10)
        
        # Close button
        close_btn = tk.Button(composer_header, text="×", font=('Segoe UI', 16),
                             bg='#2d2d2d', fg='#888888', bd=0, cursor='hand2',
                             command=self.toggle_composer)
        close_btn.pack(side=tk.RIGHT, padx=10)
        
        # Composer input area
        input_frame = tk.Frame(self.composer_panel, bg='#252525')
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Prompt input
        self.composer_input = scrolledtext.ScrolledText(
            input_frame,
            height=8,
            wrap=tk.WORD,
            font=('Segoe UI', 11),
            bg='#1e1e1e',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.composer_input.pack(fill=tk.BOTH, expand=True)
        self.composer_input.insert('1.0', 'Ask AI to generate code...')
        self.composer_input.bind('<FocusIn>', lambda e: self.composer_input.delete('1.0', tk.END) if 'Ask AI' in self.composer_input.get('1.0', tk.END) else None)
        
        # Action buttons
        button_frame = tk.Frame(self.composer_panel, bg='#252525')
        button_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        
        # Generate button (big, like Cursor)
        self.generate_btn = tk.Button(button_frame, text="✨ Generate Code",
                                font=('Segoe UI', 11, 'bold'),
                                bg='#6366f1', fg='white', bd=0,
                                padx=30, pady=10, cursor='hand2',
                                command=self.composer_generate)
        self.generate_btn.pack(side=tk.RIGHT, padx=5)
        
        # Bind Enter key to generate
        self.composer_input.bind('<Control-Return>', lambda e: self.composer_generate())
        
        # Cancel button
        cancel_btn = tk.Button(button_frame, text="Cancel",
                              font=('Segoe UI', 10),
                              bg='#3d3d3d', fg='#cccccc', bd=0,
                              padx=20, pady=10, cursor='hand2',
                              command=self.toggle_composer)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Add keyboard shortcut to show composer (Ctrl+K like Cursor)
        self.root.bind('<Control-k>', lambda e: self.toggle_composer())
        self.root.bind('<Control-K>', lambda e: self.toggle_composer())
    
    def toggle_composer(self):
        """Show/hide composer panel (Cursor-style)"""
        if not hasattr(self, 'composer_panel'):
            messagebox.showinfo("Composer", "Composer panel not initialized")
            return
            
        if self.composer_visible:
            self.composer_panel.pack_forget()
            self.composer_visible = False
        else:
            # Pack at bottom, no 'before' parameter
            self.composer_panel.pack(side=tk.BOTTOM, fill=tk.X)
            self.composer_input.focus()
            self.composer_visible = True
    
    def composer_generate(self):
        """Generate code using AI composer"""
        prompt = self.composer_input.get('1.0', tk.END).strip()
        if not prompt or 'Ask AI' in prompt or not prompt:
            messagebox.showwarning("Empty Prompt", "Please enter a request for the AI")
            return
        
        # Show generating feedback
        self.composer_input.delete('1.0', tk.END)
        self.composer_input.insert('1.0', '⏳ Generating...')
        self.composer_input.config(state='disabled')
        
        # Send to AI chat
        if hasattr(self, 'ai_chat'):
            # Add to chat display
            self.ai_chat.chat_input.delete('1.0', tk.END)
            self.ai_chat.chat_input.insert('1.0', f"💡 Composer Request: {prompt}")
            self.ai_chat.send_message()
            
            # Show success message
            def reset_composer():
                self.composer_input.config(state='normal')
                self.composer_input.delete('1.0', tk.END)
                self.composer_input.insert('1.0', 'Ask AI to generate code...')
                self.toggle_composer()
                messagebox.showinfo("AI Composer", 
                    "✓ Request sent to AI!\n\nCheck the AI Chat panel on the right for the response.")
            
            # Reset after a moment
            self.root.after(1000, reset_composer)
        else:
            self.composer_input.config(state='normal')
            self.composer_input.delete('1.0', tk.END)
            self.composer_input.insert('1.0', 'Ask AI to generate code...')
            messagebox.showerror("Error", "AI Chat not available")
    
    def run_feasibility_check(self):
        """Run feasibility analysis FIRST"""
        description = self.project_description.get('1.0', tk.END).strip()
        if not description or "Describe your project" in description:
            messagebox.showwarning("Warning", "Describe your project first")
            return
        
        lang = self.language_var.get()
        
        self.log_ai("="*60)
        self.log_ai("RUNNING FEASIBILITY CHECK")
        self.log_ai("="*60)
        
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
        
        # Log results
        self.log_ai(f"\nFEASIBILITY SCORE: {score}/10")
        self.log_ai(f"COMPLEXITY: {self.feasibility_report['complexity_level']}")
        self.log_ai(f"ESTIMATED TIME: {self.feasibility_report['estimated_time']}")
        
        if self.feasibility_report['red_flags']:
            self.log_ai("\nRED FLAGS:")
            for flag in self.feasibility_report['red_flags']:
                self.log_ai(f"  ! {flag}")
        
        if self.feasibility_report['warnings']:
            self.log_ai("\nWARNINGS:")
            for warning in self.feasibility_report['warnings']:
                self.log_ai(f"  * {warning}")
        
        if self.feasibility_report['recommendations']:
            self.log_ai("\nRECOMMENDATIONS:")
            for rec in self.feasibility_report['recommendations']:
                self.log_ai(f"  > {rec}")
        
        self.log_ai(f"\nREALITY CHECK:")
        self.log_ai(f"{self.feasibility_report['reality_check']}")
        
        # Show dialog
        if not self.feasibility_report['proceed']:
            result = messagebox.askyesnocancel(
                "SERIOUS WARNING",
                f"{self.feasibility_report['reality_check']}\n\n"
                "RED FLAGS DETECTED:\n" + "\n".join(f"- {f}" for f in self.feasibility_report['red_flags']) + "\n\n"
                "YES = Proceed anyway (you've been warned)\n"
                "NO = Revise project\n"
                "CANCEL = Stop"
            )
            if result is None:  # Cancel
                return
            elif result:  # Yes - proceed anyway
                self.log_ai("\nUSER CHOSE TO PROCEED DESPITE RED FLAGS")
                self.analyze_btn.config(state=tk.NORMAL)
            else:  # No - revise
                self.log_ai("\nUSER CHOSE TO REVISE PROJECT")
                return
        elif score <= 5:
            result = messagebox.askyesno(
                "MASSIVE PROJECT WARNING",
                f"{self.feasibility_report['reality_check']}\n\n"
                f"This will take: {self.feasibility_report['estimated_time']}\n\n"
                "Are you REALLY prepared for this commitment?\n\n"
                "I'll help you, but you need to know what you're getting into."
            )
            if not result:
                self.log_ai("\nUSER CHOSE TO RECONSIDER")
                return
            self.log_ai("\nUSER ACCEPTED MASSIVE PROJECT COMMITMENT")
        elif score <= 7:
            result = messagebox.askyesno(
                "Complexity Warning",
                f"{self.feasibility_report['reality_check']}\n\n"
                "This is more work than you might think. Continue?"
            )
            if not result:
                return
        
        # Enable next steps
        self.analyze_btn.config(state=tk.NORMAL)
        self.log_ai("\n" + "="*60)
        self.log_ai("FEASIBILITY CHECK COMPLETE - Proceed to Step 1")
        self.log_ai("="*60)
        self.status_var.set(f"Feasibility: {score}/10 - Ready for Analysis")
    
    def start_analysis(self):
        """Phase 1: Detailed planning with honesty"""
        if not self.feasibility_report:
            messagebox.showwarning("Warning", "Run feasibility check first!")
            return
        
        description = self.project_description.get('1.0', tk.END).strip()
        self.is_running = True
        self.analyze_btn.config(state=tk.DISABLED)
        self.status_var.set("Running analysis...")
        
        threading.Thread(target=self._analysis_thread, args=(description,), daemon=True).start()
    
    def _analysis_thread(self, description):
        """Analysis with reality checks"""
        try:
            lang = self.language_var.get()
            planner = self.planner_model.get()

            self.message_queue.put(('ai', f"\n{'='*60}"))
            self.message_queue.put(('ai', f"PHASE 1: DETAILED ANALYSIS"))
            self.message_queue.put(('ai', f"{'='*60}"))
            self.message_queue.put(('ai', f"Language: {lang}"))
            self.message_queue.put(('ai', f"Model: {planner}"))
            self.message_queue.put(('start_loading', 'DeathAIAUS is planning your project'))
            
            # Enhanced prompt with feasibility results
            system_prompt = f"""You are an HONEST project planner for {lang} development.

FEASIBILITY ANALYSIS ALREADY RAN:
- Score: {self.feasibility_report['feasibility_score']}/10
- Complexity: {self.feasibility_report['complexity_level']}
- Estimated Time: {self.feasibility_report['estimated_time']}

YOUR JOB:
1. Break into SPECIFIC, ACTIONABLE steps
2. Give REALISTIC time estimates (be honest, not optimistic)
3. List EXACT packages/dependencies needed
4. Identify what could go wrong
5. Make REASONABLE ASSUMPTIONS - don't ask too many questions, proceed with best practices

FORMAT:
## Honest Project Breakdown

### Phase 1: [Name] (Est: X hours/days)
- Step 1: [specific task]
- Step 2: [specific task]
...

### Phase 2: [Name] (Est: X hours/days)
...

### Dependencies & Setup
- Exact package names
- Version requirements
- System requirements
- API keys/accounts needed

### Reality Checks
- What will be hardest
- Where you'll get stuck
- What to do when stuck

### Assumptions Made
- [List any assumptions you made to proceed]

BE BRUTALLY HONEST about time and difficulty.
DO NOT ask questions - make reasonable assumptions and proceed."""

            # Add project context if available
            user_prompt = f"Create detailed, honest plan:\n\n{description}"
            if self.project_context:
                user_prompt += f"\n\nEXISTING PROJECT CONTEXT:\n"
                user_prompt += f"Project has {len(self.project_context['files'])} files, {self.project_context['total_lines']} lines of code\n"
                user_prompt += f"Key files: {', '.join(self.project_context['files'][:10])}\n"
                user_prompt += f"Plan how to integrate with or extend this existing codebase.\n"

            response = self._call_model(planner, system_prompt, user_prompt, 300)

            self.message_queue.put(('stop_loading', None))
            self.message_queue.put(('ai', f"\n{response}"))
            self.message_queue.put(('ai', f"\n{'='*60}"))
            self.message_queue.put(('ai', f"Review this plan. If good, proceed to Step 2: Build"))
            
            self.current_project = {
                'description': description,
                'language': lang,
                'plan': response,
                'feasibility': self.feasibility_report,
                'created': datetime.now()
            }
            
            self.message_queue.put(('enable_build', None))

        except Exception as e:
            self.message_queue.put(('stop_loading', None))
            self.message_queue.put(('ai', f"\nERROR: {e}"))
        finally:
            self.message_queue.put(('phase_complete', None))
    
    def start_build(self):
        """Phase 2: Build with checkpoints"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Complete analysis first")
            return
        
        # Final warning for massive projects
        if self.feasibility_report['feasibility_score'] <= 5:
            confirm = messagebox.askyesno(
                "Final Warning",
                f"This is a {self.feasibility_report['estimated_time']} project.\n\n"
                "The AI will build what it can, but this WILL require:\n"
                "- Multiple iterations\n"
                "- Significant debugging\n"
                "- Learning on your part\n"
                "- Possible architectural changes\n\n"
                "Start building anyway?"
            )
            if not confirm:
                return
        
        self.is_running = True
        self.build_btn.config(state=tk.DISABLED)
        self.status_var.set("Building...")
        
        threading.Thread(target=self._build_thread, daemon=True).start()
    
    def _build_thread(self):
        """Build with tool integration"""
        try:
            lang = self.language_var.get()
            coder = self.coder_model.get()
            # Legacy tool model removed
            # tool_model = ToolEnabledModel(coder, self.toolbox)

            self.message_queue.put(('ai', f"\n{'='*60}"))
            self.message_queue.put(('ai', f"PHASE 2: BUILDING"))
            self.message_queue.put(('ai', f"{'='*60}"))
            self.message_queue.put(('start_loading', 'DeathAIAUS is coding your project'))
            
            system_prompt = f"""You are a {lang} coder with FILE SYSTEM ACCESS.

CRITICAL: Output ONLY raw use_tool() calls. NO markdown, NO code blocks, NO explanations.

WRONG (don't do this):
```python
use_tool("write_file", "main.py", "code")
```

CORRECT (do this):
use_tool("write_file", "main.py", "import pygame\\npygame.init()\\nscreen = pygame.display.set_mode((800,600))")

Requirements:
- Proper error handling (try/except)
- Input validation
- Clear comments

Project: {self.current_project['description'][:300]}

OUTPUT RAW TOOL CALLS NOW (no markdown blocks)"""

            # Simplified user prompt
            user_prompt = "Create the main file with working code. Output use_tool() calls only."

            response = self._call_model(coder, system_prompt, user_prompt, 600)

            self.message_queue.put(('stop_loading', None))
            self.message_queue.put(('ai', f"\n{response}"))
            
            # Execute tools with live updates
            tool_results = self.execute_tools_with_streaming(response)
            if tool_results:
                self.message_queue.put(('ai', f"\n✓ File operations complete"))
                self.message_queue.put(('refresh_tree', None))
            else:
                self.message_queue.put(('ai', f"\nWARNING: No tools used - AI might be in 'chat mode'"))
                self.message_queue.put(('ai', f"Try asking it to 'create the files now using the tools'"))
            
            self.message_queue.put(('enable_test', None))

        except requests.exceptions.Timeout:
            self.message_queue.put(('stop_loading', None))
            self.message_queue.put(('ai', f"\n{'='*60}"))
            self.message_queue.put(('ai', f"ERROR: Model timed out (600s/10 minute limit)"))
            self.message_queue.put(('ai', f"\nTIPS TO FIX:"))
            self.message_queue.put(('ai', f"1. Simplify your project description"))
            self.message_queue.put(('ai', f"2. Try a faster/smaller model"))
            self.message_queue.put(('ai', f"3. Break into smaller tasks"))
            self.message_queue.put(('ai', f"4. Check ReapGate or LM Studio is running and model is loaded"))
            self.message_queue.put(('ai', f"{'='*60}"))
        except Exception as e:
            self.message_queue.put(('stop_loading', None))
            self.message_queue.put(('ai', f"\nERROR: {e}"))
        finally:
            self.message_queue.put(('phase_complete', None))
    
    def start_testing(self):
        """Phase 3: Testing"""
        self.is_running = True
        self.test_btn.config(state=tk.DISABLED)
        self.status_var.set("Testing...")
        
        threading.Thread(target=self._test_thread, daemon=True).start()
    
    def _test_thread(self):
        """Testing with honesty"""
        try:
            tester = self.planner_model.get()  # Use planner for testing
            # Legacy tool model removed
            # tool_model = ToolEnabledModel(tester, self.toolbox)
            
            self.message_queue.put(('ai', f"\n{'='*60}"))
            self.message_queue.put(('ai', f"PHASE 3: TESTING"))
            self.message_queue.put(('ai', f"{'='*60}"))
            self.message_queue.put(('start_loading', 'DeathAIAUS is testing your code'))
            
            system_prompt = """You are a QA tester. You have FILE SYSTEM ACCESS through tools.

CRITICAL: YOU MUST USE TOOLS - DO NOT JUST DESCRIBE WHAT TO DO!

Available tools:
- use_tool("read_file", "filename")
- use_tool("run_command", "command")
- use_tool("list_directory", ".")

EXAMPLE - Output use_tool() calls like this:
use_tool("list_directory", ".")
use_tool("read_file", "calculator.py")
use_tool("run_command", "python calculator.py")

Then report what you see from the tool results.

START NOW - Output use_tool() calls to test the project files."""

            response = self._call_model(tester, system_prompt,
                                       "Test the project files that were created. Report honest results.",
                                       300)

            self.message_queue.put(('stop_loading', None))
            self.message_queue.put(('ai', f"\n{response}"))
            
            tool_results = self.execute_tools_with_streaming(response)
            if tool_results:
                self.message_queue.put(('ai', f"\nTest Results:\n{tool_results}"))
            
        except Exception as e:
            self.message_queue.put(('stop_loading', None))
            self.message_queue.put(('ai', f"\nERROR: {e}"))
        finally:
            self.message_queue.put(('phase_complete', None))
    
    def toggle_auto_approve(self):
        """Toggle auto-approve setting for commands"""
        self.auto_approve_commands = self.auto_approve_var.get()
        status = "enabled" if self.auto_approve_commands else "disabled"
        self.log_ai(f"\n⚙️ Auto-approve commands {status}")

    def toggle_auto_approve_files(self):
        """Toggle auto-approve setting for file changes"""
        self.auto_approve_file_changes = self.auto_approve_files_var.get()
        status = "enabled" if self.auto_approve_file_changes else "disabled"
        self.log_ai(f"\n⚙️ Auto-approve file changes {status}")
        if self.auto_approve_file_changes:
            self.log_ai("   ⚠️ WARNING: You will NOT see code reviews like Cursor.sh!")

    def request_command_approval(self, command):
        """Request user approval to run a command"""
        # Create approval dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Command Approval Required")
        dialog.geometry("600x300")
        dialog.configure(bg='#2d2d2d')
        dialog.transient(self.root)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"600x300+{x}+{y}")

        # Header
        tk.Label(dialog, text="⚠️ AI wants to run a command", font=('Arial', 14, 'bold'),
                fg='#ffaa00', bg='#2d2d2d').pack(pady=15)

        # Command display
        tk.Label(dialog, text="Command:", font=('Arial', 10, 'bold'),
                fg='#cccccc', bg='#2d2d2d').pack(pady=5)

        command_frame = tk.Frame(dialog, bg='#1e1e1e', relief=tk.SUNKEN, bd=2)
        command_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        command_text = tk.Text(command_frame, height=4, font=('Consolas', 10),
                              bg='#1e1e1e', fg='#00ff00', wrap=tk.WORD)
        command_text.insert('1.0', command)
        command_text.config(state=tk.DISABLED)
        command_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Warning
        tk.Label(dialog, text="⚠️ Only approve commands you trust",
                font=('Arial', 9, 'italic'), fg='#ff6666', bg='#2d2d2d').pack(pady=5)

        # Result storage
        result = {'approved': False}

        # Auto-approve checkbox
        auto_var = tk.BooleanVar(value=False)
        tk.Checkbutton(dialog, text="Auto-approve all commands (not recommended)",
                      variable=auto_var, bg='#2d2d2d', fg='#cccccc',
                      selectcolor='#1e1e1e', activebackground='#2d2d2d',
                      activeforeground='#cccccc').pack(pady=5)

        # Buttons
        button_frame = tk.Frame(dialog, bg='#2d2d2d')
        button_frame.pack(pady=15)

        def approve():
            result['approved'] = True
            if auto_var.get():
                self.auto_approve_commands = True
            dialog.destroy()

        def deny():
            result['approved'] = False
            dialog.destroy()

        tk.Button(button_frame, text="✓ Allow", command=approve,
                 bg='#00aa00', fg='white', font=('Arial', 11, 'bold'),
                 width=12, height=2).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="✗ Deny", command=deny,
                 bg='#cc0000', fg='white', font=('Arial', 11, 'bold'),
                 width=12, height=2).pack(side=tk.LEFT, padx=10)

        # Wait for user response
        dialog.wait_window()

        return result['approved']

    def request_code_approval(self, filename, new_content):
        """Request user approval for code changes (Cursor-style)"""
        # Check if file exists to show diff
        full_path = os.path.join(self.workspace_path, filename)
        file_exists = os.path.exists(full_path)
        old_content = ""

        if file_exists:
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    old_content = f.read()
            except:
                old_content = "[Could not read existing file]"

        # Create approval dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Review Code Changes - {filename}")
        dialog.geometry("900x700")
        dialog.configure(bg='#2d2d2d')
        dialog.transient(self.root)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (900 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f"900x700+{x}+{y}")

        # Header
        header_frame = tk.Frame(dialog, bg='#1e1e1e')
        header_frame.pack(fill=tk.X, pady=(0,10))

        if file_exists:
            tk.Label(header_frame, text=f"📝 AI wants to modify: {filename}",
                    font=('Arial', 14, 'bold'), fg='#ffaa00', bg='#1e1e1e').pack(pady=15)
        else:
            tk.Label(header_frame, text=f"📄 AI wants to create: {filename}",
                    font=('Arial', 14, 'bold'), fg='#00ff00', bg='#1e1e1e').pack(pady=15)

        # Create notebook for tabs
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: New Code (always show)
        new_code_frame = ttk.Frame(notebook)
        notebook.add(new_code_frame, text="📄 New Code")

        new_code_text = scrolledtext.ScrolledText(new_code_frame, wrap=tk.NONE,
                                                  font=('Consolas', 10),
                                                  bg='#1e1e1e', fg='#d4d4d4')
        new_code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        new_code_text.insert('1.0', new_content)
        new_code_text.config(state=tk.DISABLED)

        # Syntax highlighting for new code
        self._apply_basic_syntax_highlighting(new_code_text, filename)

        # Tab 2: Old Code (if file exists)
        if file_exists:
            old_code_frame = ttk.Frame(notebook)
            notebook.add(old_code_frame, text="📋 Current Code")

            old_code_text = scrolledtext.ScrolledText(old_code_frame, wrap=tk.NONE,
                                                      font=('Consolas', 10),
                                                      bg='#1e1e1e', fg='#d4d4d4')
            old_code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            old_code_text.insert('1.0', old_content)
            old_code_text.config(state=tk.DISABLED)

            self._apply_basic_syntax_highlighting(old_code_text, filename)

            # Tab 3: Diff View
            diff_frame = ttk.Frame(notebook)
            notebook.add(diff_frame, text="🔍 Changes")

            diff_text = scrolledtext.ScrolledText(diff_frame, wrap=tk.NONE,
                                                  font=('Consolas', 10),
                                                  bg='#1e1e1e', fg='#cccccc')
            diff_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Generate simple diff
            old_lines = old_content.split('\n')
            new_lines = new_content.split('\n')

            diff_text.insert('1.0', f"--- {filename} (current)\n", 'header')
            diff_text.insert('end', f"+++ {filename} (new)\n\n", 'header')

            # Simple line-by-line comparison
            max_lines = max(len(old_lines), len(new_lines))
            for i in range(max_lines):
                old_line = old_lines[i] if i < len(old_lines) else ""
                new_line = new_lines[i] if i < len(new_lines) else ""

                if old_line != new_line:
                    if i < len(old_lines):
                        diff_text.insert('end', f"- {old_line}\n", 'removed')
                    if i < len(new_lines):
                        diff_text.insert('end', f"+ {new_line}\n", 'added')
                else:
                    diff_text.insert('end', f"  {old_line}\n", 'unchanged')

            # Configure diff colors
            diff_text.tag_config('header', foreground='#6495ed')
            diff_text.tag_config('removed', foreground='#ff6b6b', background='#4a1f1f')
            diff_text.tag_config('added', foreground='#69ff69', background='#1f4a1f')
            diff_text.tag_config('unchanged', foreground='#888888')
            diff_text.config(state=tk.DISABLED)

        # Stats
        stats_frame = tk.Frame(dialog, bg='#2d2d2d')
        stats_frame.pack(fill=tk.X, padx=20, pady=5)

        lines_count = len(new_content.split('\n'))
        chars_count = len(new_content)

        tk.Label(stats_frame, text=f"📊 {lines_count} lines • {chars_count} characters",
                font=('Arial', 9), fg='#888888', bg='#2d2d2d').pack(side=tk.LEFT)

        # Result storage
        result = {'approved': False, 'auto_approve': False}

        # Buttons
        button_frame = tk.Frame(dialog, bg='#2d2d2d')
        button_frame.pack(pady=15)

        # Auto-approve checkbox
        auto_var = tk.BooleanVar(value=False)
        tk.Checkbutton(button_frame, text="Auto-approve all file changes",
                      variable=auto_var, bg='#2d2d2d', fg='#cccccc',
                      selectcolor='#1e1e1e', activebackground='#2d2d2d',
                      activeforeground='#cccccc').pack(pady=5)

        btn_frame = tk.Frame(button_frame, bg='#2d2d2d')
        btn_frame.pack()

        def approve():
            result['approved'] = True
            result['auto_approve'] = auto_var.get()
            dialog.destroy()

        def reject():
            result['approved'] = False
            dialog.destroy()

        tk.Button(btn_frame, text="✓ Accept Changes", command=approve,
                 bg='#00aa00', fg='white', font=('Arial', 12, 'bold'),
                 width=18, height=2).pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, text="✗ Reject", command=reject,
                 bg='#cc0000', fg='white', font=('Arial', 12, 'bold'),
                 width=18, height=2).pack(side=tk.LEFT, padx=10)

        # Wait for user response
        dialog.wait_window()

        return result

    def _apply_basic_syntax_highlighting(self, text_widget, filename):
        """Apply basic syntax highlighting to code preview"""
        content = text_widget.get('1.0', 'end-1c')

        # Define some basic syntax highlighting
        text_widget.tag_config('keyword', foreground='#569cd6')
        text_widget.tag_config('string', foreground='#ce9178')
        text_widget.tag_config('comment', foreground='#6a9955')
        text_widget.tag_config('function', foreground='#dcdcaa')

        # Keywords based on file extension
        ext = os.path.splitext(filename)[1].lower()

        keywords = []
        if ext in ['.py']:
            keywords = ['def', 'class', 'import', 'from', 'return', 'if', 'else', 'elif',
                       'for', 'while', 'try', 'except', 'with', 'as', 'lambda', 'async', 'await']
        elif ext in ['.js', '.ts']:
            keywords = ['function', 'const', 'let', 'var', 'return', 'if', 'else',
                       'for', 'while', 'class', 'import', 'export', 'async', 'await']

        # Highlight keywords
        for keyword in keywords:
            start = '1.0'
            while True:
                pos = text_widget.search(r'\m' + keyword + r'\M', start, stopindex='end', regexp=True)
                if not pos:
                    break
                end = f"{pos}+{len(keyword)}c"
                text_widget.tag_add('keyword', pos, end)
                start = end

        # Highlight strings (simple)
        for quote in ['"', "'"]:
            start = '1.0'
            while True:
                pos = text_widget.search(quote, start, stopindex='end')
                if not pos:
                    break
                end_pos = text_widget.search(quote, f"{pos}+1c", stopindex='end')
                if end_pos:
                    text_widget.tag_add('string', pos, f"{end_pos}+1c")
                    start = f"{end_pos}+1c"
                else:
                    break

        # Highlight comments
        if ext in ['.py']:
            start = '1.0'
            while True:
                pos = text_widget.search('#', start, stopindex='end')
                if not pos:
                    break
                line_end = text_widget.index(f"{pos} lineend")
                text_widget.tag_add('comment', pos, line_end)
                start = f"{pos}+1 line"
        elif ext in ['.js', '.ts']:
            start = '1.0'
            while True:
                pos = text_widget.search('//', start, stopindex='end')
                if not pos:
                    break
                line_end = text_widget.index(f"{pos} lineend")
                text_widget.tag_add('comment', pos, line_end)
                start = f"{pos}+1 line"

    def execute_tools_with_streaming(self, response):
        """Execute tools with live streaming updates like Cursor"""
        import re

        # Strip markdown code blocks if present
        response = re.sub(r'```(?:python)?\s*\n', '', response)
        response = re.sub(r'```\s*$', '', response)

        tool_pattern = r'use_tool\(([^,]+),\s*"([^"]+)"(?:,\s*"([^"]+)")?\)'
        tool_matches = re.finditer(tool_pattern, response)

        results = []
        tool_found = False

        for match in tool_matches:
            tool_found = True
            tool_name = match.group(1).strip().strip('"')
            arg1 = match.group(2).strip()
            arg2 = match.group(3).strip() if match.group(3) else None

            # Show what we're doing in real-time
            if tool_name == "write_file":
                self.message_queue.put(('ai', f"\n📝 AI wants to write: {arg1}"))

                # Check if auto-approve is enabled for file changes
                if not self.auto_approve_file_changes:
                    # Request approval from user (Cursor-style)
                    if arg2:
                        approval_result = self.request_code_approval(arg1, arg2)
                        if not approval_result['approved']:
                            self.message_queue.put(('ai', f"   ✗ Changes to {arg1} rejected by user"))
                            self.message_queue.put(('terminal', f"Rejected: {arg1}\n"))
                            results.append(f"[REJECTED] User rejected changes to {arg1}")
                            continue

                        # Check if user wants to auto-approve future changes
                        if approval_result.get('auto_approve', False):
                            self.auto_approve_file_changes = True
                            self.message_queue.put(('ai', "   ⚙️ Auto-approve enabled for file changes"))
                    else:
                        results.append(f"[ERROR] write_file requires 2 arguments")
                        continue

                self.message_queue.put(('terminal', f"Creating file: {arg1}\n"))

                # Execute the tool
                try:
                    if arg2:
                        result = self.toolbox.write_file(arg1, arg2)
                        self.message_queue.put(('ai', f"   ✓ {arg1} created ({len(arg2)} chars)"))
                        self.message_queue.put(('refresh_tree', None))  # Update file tree immediately

                        # Open in tab if it's in workspace
                        full_path = os.path.join(self.workspace_path, arg1)
                        if os.path.exists(full_path):
                            # Queue the file to be opened in a tab
                            self.message_queue.put(('open_in_tab', (full_path, arg2)))

                        results.append(f"[SUCCESS] {result}")
                    else:
                        results.append(f"[ERROR] write_file requires 2 arguments")
                except Exception as e:
                    self.message_queue.put(('ai', f"   ✗ Error: {e}"))
                    results.append(f"[ERROR] {e}")

            elif tool_name == "run_command":
                self.message_queue.put(('ai', f"\n▶ Command requested: {arg1}"))

                # Check if auto-approve is enabled
                if not self.auto_approve_commands:
                    # Request approval from user
                    approval = self.request_command_approval(arg1)
                    if not approval:
                        self.message_queue.put(('ai', f"   ✗ Command denied by user"))
                        results.append(f"[DENIED] Command was denied by user")
                        continue

                self.message_queue.put(('ai', f"   ✓ Executing..."))
                try:
                    result = self.toolbox.run_command(arg1)
                    self.message_queue.put(('terminal', f"{result}\n"))
                    results.append(f"[COMMAND] {result}")
                except Exception as e:
                    self.message_queue.put(('ai', f"   ✗ Error: {e}"))
                    results.append(f"[ERROR] {e}")

            elif tool_name == "read_file":
                self.message_queue.put(('ai', f"\n📖 Reading {arg1}..."))
                try:
                    result = self.toolbox.read_file(arg1)
                    results.append(f"[READ] {result[:200]}...")
                except Exception as e:
                    results.append(f"[ERROR] {e}")

            elif tool_name == "list_directory":
                try:
                    result = self.toolbox.list_directory(arg1)
                    results.append(f"[LIST] {result}")
                except Exception as e:
                    results.append(f"[ERROR] {e}")

        if tool_found:
            return "\n".join(results)

        return None

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
                # If smart loading fails, continue with regular model call
                # This allows the IDE to work even if smart loading has issues
                print(f"Smart loading warning: {e}")
                pass
        
        model_id = self.model_map.get(model_display_name, model_display_name)
        
        # Health check based on detected backend
        if self.backend_name == "DeathAIAUS Backend":
            try:
                health = requests.get("http://localhost:8888/health", timeout=5)
                if health.status_code != 200:
                    raise Exception(f"DeathAIAUS Backend health check failed with status {health.status_code}. Please restart backend.")
            except requests.exceptions.ConnectionError:
                raise Exception("Cannot connect to DeathAIAUS Backend. Please start it with: python start_deathaiaus_backend.py")
            except requests.exceptions.Timeout:
                raise Exception("DeathAIAUS Backend timeout. Backend may be overloaded.")
        
        elif self.backend_name == "ReapGate":
            try:
                health = requests.get("http://localhost:7777/health", timeout=5)
                if health.status_code != 200:
                    raise Exception(f"ReapGate health check failed with status {health.status_code}. Please restart IDE.")
            except requests.exceptions.ConnectionError as e:
                # Try to start ReapGate automatically
                print(f"Connection error: {e}. Attempting to start ReapGate...")
                if self.start_reapgate_if_needed():
                    # Wait a moment for it to fully start
                    time.sleep(3)
                    try:
                        health = requests.get("http://localhost:7777/health", timeout=5)
                        if health.status_code == 200:
                            print("ReapGate started successfully!")
                            pass  # Success, continue
                        else:
                            raise Exception(f"ReapGate started but health check failed with status {health.status_code}.")
                    except Exception as e2:
                        raise Exception(f"Cannot connect to ReapGate after restart: {e2}")
                else:
                    raise Exception("Cannot start ReapGate automatically. Please use AI > Restart ReapGate or restart IDE.")
            except requests.exceptions.Timeout:
                raise Exception("ReapGate timeout. Backend may be overloaded. Try AI > Restart ReapGate.")
        
        elif self.backend_name == "LM Studio":
            try:
                # Check LM Studio is running
                response = requests.get("http://localhost:1234/v1/models", timeout=5)
                if response.status_code != 200:
                    raise Exception("LM Studio server not responding.")
            except requests.exceptions.ConnectionError:
                raise Exception("Cannot connect to LM Studio. Please start LM Studio server on port 1234.")
        
        else:
            raise Exception("No AI backend detected. Please start DeathAIAUS Backend, ReapGate, or LM Studio.")
        
        # Skip smart loading if not using ReapGate (ReapGate-specific feature)
        if self.backend_name == "ReapGate" and hasattr(self, 'smart_model_manager'):
            try:
                self.smart_model_manager.ensure_model_loaded(workflow)
            except Exception as e:
                print(f"Smart loading warning: {e}")
                pass
        
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
                error_text = e.response.text
                if "failed to load model" in error_text:
                    raise Exception(f"Model loading failed: {error_text}\n\nTry:\n1. AI > Test ReapGate Connection\n2. AI > Restart ReapGate\n3. Check if model files exist in G:\\My Drive\\DeathAIAUS_PANTHEON")
                else:
                    raise Exception(f"ReapGate error: {error_text}")
            else:
                raise Exception(f"HTTP {e.response.status_code}: {e.response.text}")
        except KeyError:
            raise Exception("Unexpected response format.")
    
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
    
    def check_reapgate_status(self):
        """Check ReapGate status and update indicator"""
        def check():
            try:
                response = requests.get("http://localhost:7777/health", timeout=2)
                if response.status_code == 200:
                    self.reapgate_status_label.config(
                        text="🟢 ReapGate: Ready",
                        fg='#4CAF50'
                    )
                else:
                    self.reapgate_status_label.config(
                        text="🟡 ReapGate: Error",
                        fg='#FF9800'
                    )
            except:
                self.reapgate_status_label.config(
                    text="🔴 ReapGate: Offline",
                    fg='#F44336'
                )
            
            # Schedule next check in 10 seconds
            self.root.after(10000, check)
        
        # Start checking
        check()
    
    def start_reapgate_if_needed(self):
        """Start ReapGate if it's not running"""
        try:
            response = requests.get("http://localhost:7777/health", timeout=2)
            if response.status_code == 200:
                return True  # Already running
        except:
            pass
        
        # Try to start ReapGate
        try:
            import subprocess
            import os
            
            # Check if ReapGate.exe exists
            reapgate_path = os.path.join(os.getcwd(), "ReapGate", "reapgate.exe")
            if os.path.exists(reapgate_path):
                # Start ReapGate in background
                subprocess.Popen([reapgate_path], 
                               cwd=os.path.join(os.getcwd(), "ReapGate"),
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                
                # Wait for it to start
                for i in range(30):  # Wait up to 30 seconds
                    time.sleep(1)
                    try:
                        response = requests.get("http://localhost:7777/health", timeout=2)
                        if response.status_code == 200:
                            return True
                    except:
                        continue
                
                return False
            else:
                return False
        except Exception as e:
            print(f"Failed to start ReapGate: {e}")
            return False
    
    def restart_reapgate(self):
        """Restart ReapGate backend"""
        try:
            # Kill any existing ReapGate processes
            import psutil
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'reapgate' in proc.info['name'].lower():
                        proc.kill()
                except:
                    pass
            
            # Wait a moment
            time.sleep(2)
            
            # Start ReapGate
            if self.start_reapgate_if_needed():
                messagebox.showinfo("Success", "ReapGate restarted successfully!")
            else:
                messagebox.showerror("Error", "Failed to restart ReapGate. Check logs.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restart ReapGate: {e}")
    
    def start_deathaiaus_backend(self):
        """Start DeathAIAUS Python Backend"""
        try:
            import subprocess
            import threading
            
            def start_backend():
                try:
                    # Start the backend in a separate process
                    subprocess.Popen([
                        sys.executable, "start_deathaiaus_backend.py"
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    # Wait a moment for startup
                    time.sleep(3)
                    
                    # Test connection
                    try:
                        response = requests.get("http://localhost:8888/health", timeout=5)
                        if response.status_code == 200:
                            self.root.after(0, lambda: messagebox.showinfo("Success", "DeathAIAUS Backend started successfully!"))
                        else:
                            self.root.after(0, lambda: messagebox.showerror("Error", "Backend started but not responding properly."))
                    except:
                        self.root.after(0, lambda: messagebox.showerror("Error", "Backend started but connection test failed."))
                        
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to start DeathAIAUS Backend: {e}"))
            
            # Start in background thread
            thread = threading.Thread(target=start_backend, daemon=True)
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start DeathAIAUS Backend: {e}")
    
    def test_backend_connection(self):
        """Test backend connection and show detailed status"""
        status_info = []
        
        # Test DeathAIAUS Backend
        try:
            response = requests.get("http://localhost:8888/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                status_info.append(f"✅ DeathAIAUS Backend: {health_data.get('backend', 'Unknown')}")
                status_info.append(f"   Models Available: {health_data.get('models_available', 0)}")
                status_info.append(f"   Current Model: {health_data.get('current_model', 'None')}")
            else:
                status_info.append("❌ DeathAIAUS Backend: Not responding")
        except:
            status_info.append("❌ DeathAIAUS Backend: Not running")
        
        # Test ReapGate
        try:
            response = requests.get("http://localhost:7777/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                status_info.append(f"✅ ReapGate: {health_data.get('status', 'Unknown')}")
            else:
                status_info.append("❌ ReapGate: Not responding")
        except:
            status_info.append("❌ ReapGate: Not running")
        
        # Test LM Studio
        try:
            response = requests.get("http://localhost:1234/v1/models", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                model_count = len(models_data.get('data', []))
                status_info.append(f"✅ LM Studio: {model_count} models available")
            else:
                status_info.append("❌ LM Studio: Not responding")
        except:
            status_info.append("❌ LM Studio: Not running")
        
        # Show status
        status_text = "\n".join(status_info)
        messagebox.showinfo("Backend Status", f"Current Backend: {self.backend_name}\n\n{status_text}")
    
    def configure_workflow_models(self):
        """Show dialog to configure workflow models"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Configure Workflow Models")
        dialog.geometry("600x500")
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"600x500+{x}+{y}")
        
        # Title
        title = tk.Label(dialog, text="Configure AI Models for Workflows", 
                        font=('Arial', 14, 'bold'))
        title.pack(pady=20)
        
        # Instructions
        instructions = tk.Label(dialog, 
                               text="Assign specific models to different workflow steps for optimal performance.\n"
                                    "Leave empty to use the default selected model.",
                               font=('Arial', 10), justify=tk.LEFT)
        instructions.pack(pady=10)
        
        # Create scrollable frame
        canvas = tk.Canvas(dialog)
        scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Get available models
        available_models = list(self.model_map.keys())
        if not available_models:
            available_models = ["No models detected"]
        
        # Workflow configurations
        workflow_configs = [
            ("Coding - Generate", "coding_generate"),
            ("Coding - Analyze", "coding_analyze"), 
            ("Coding - Validate", "coding_validate"),
            ("Large Projects - Plan", "large_plan"),
            ("Large Projects - Implement", "large_implement"),
            ("Large Projects - Review", "large_review"),
            ("Quick Tasks - Prototype", "quick_prototype"),
            ("Quick Tasks - Task", "quick_task"),
            ("Quick Tasks - Logic", "quick_logic"),
            ("Security - Detect", "security_detect"),
            ("Security - Destroy", "security_destroy"),
            ("Security - Test", "security_test"),
        ]
        
        # Create dropdowns for each workflow
        self.workflow_vars = {}
        for i, (label, key) in enumerate(workflow_configs):
            frame = tk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, padx=20, pady=5)
            
            tk.Label(frame, text=label, width=25, anchor=tk.W).pack(side=tk.LEFT)
            
            var = tk.StringVar(value=self.workflow_models.get(key) or "")
            dropdown = ttk.Combobox(frame, textvariable=var, values=available_models, width=30)
            dropdown.pack(side=tk.LEFT, padx=10)
            
            self.workflow_vars[key] = var
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def save_config():
            for key, var in self.workflow_vars.items():
                value = var.get()
                self.workflow_models[key] = value if value and value != "No models detected" else None
            
            self.save_workflow_config()
            self.smart_model_manager.workflow_to_model = {
                'coding': self.workflow_models.get('coding_generate'),
                'review': self.workflow_models.get('review_check'),
                'testing': self.workflow_models.get('test_generate'),
                'planning': self.workflow_models.get('plan_architect')
            }
            messagebox.showinfo("Success", "Workflow configuration saved!")
            dialog.destroy()
        
        tk.Button(button_frame, text="Save Configuration", command=save_config,
                 bg='#4CAF50', fg='white', padx=20, pady=5).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                 padx=20, pady=5).pack(side=tk.LEFT, padx=10)
    
    # File management methods
    def load_file_tree(self):
        """Load workspace files"""
        self.file_tree.delete(*self.file_tree.get_children())
        root_node = self.file_tree.insert('', 'end', text=self.workspace_path, open=True)
        self._populate_tree(root_node, self.workspace_path)
    
    def _populate_tree(self, parent, path):
        """Recursively populate tree"""
        try:
            for item in sorted(os.listdir(path)):
                if item.startswith('.'):
                    continue
                item_path = os.path.join(path, item)
                node = self.file_tree.insert(parent, 'end', text=item, values=[item_path])
                if os.path.isdir(item_path):
                    self.file_tree.insert(node, 'end')
        except:
            pass
    
    def open_file_from_tree(self, event):
        """Open file from tree"""
        selection = self.file_tree.selection()
        if selection:
            values = self.file_tree.item(selection[0], 'values')
            if values and os.path.isfile(values[0]):
                self.open_file(values[0])
    
    def open_file(self, file_path=None):
        """Open file in editor"""
        if not file_path:
            file_path = filedialog.askopenfilename(
                title="Open File",
                filetypes=[
                    ("Python files", "*.py"),
                    ("JavaScript files", "*.js"),
                    ("Text files", "*.txt"),
                    ("Markdown files", "*.md"),
                    ("All files", "*.*")
                ]
            )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add to tab system
            self.tabs.add_tab(file_path, content)
            self.current_file = file_path
            self.file_label.config(text=os.path.basename(file_path))
            self.log_terminal(f"Opened: {file_path}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open: {e}")
    
    def save_file(self):
        """Save current file"""
        if not self.current_file or self.current_file.startswith("Untitled"):
            # Save as...
            file_path = filedialog.asksaveasfilename(
                initialdir=self.workspace_path,
                title="Save File",
                defaultextension=".py",
                filetypes=[
                    ("Python files", "*.py"),
                    ("JavaScript files", "*.js"),
                    ("Text files", "*.txt"),
                    ("Markdown files", "*.md"),
                    ("All files", "*.*")
                ]
            )
            if not file_path:
                return
            
            # Remove old untitled tab if exists
            if self.current_file and self.current_file.startswith("Untitled"):
                old_file = self.current_file
                self.current_file = file_path
                if old_file in self.tabs.tabs:
                    # Update tab instead of closing
                    tab_data = self.tabs.tabs[old_file]
                    del self.tabs.tabs[old_file]
                    self.tabs.tabs[file_path] = tab_data
                    # Update tab label
                    tab_data['label'].config(text=os.path.basename(file_path))
            else:
            self.current_file = file_path
        
        if self.current_file:
        try:
                content = self.tabs.get_current_content()
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
                    
                # Mark as saved
                self.tabs.save_current()
                self.file_label.config(text=os.path.basename(self.current_file))
            self.log_terminal(f"Saved: {self.current_file}\n")
            self.load_file_tree()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")
    
    def new_file(self):
        """Create new file (delegates to tab system)"""
        if hasattr(self, 'tabs'):
            self.tabs.new_file()
        else:
            # Fallback for old system
        file_path = filedialog.asksaveasfilename(initialdir=self.workspace_path)
        if file_path:
            with open(file_path, 'w') as f:
                f.write("")
            self.open_file(file_path)
            self.load_file_tree()
    
    def load_project(self):
        """Load an existing project directory"""
        project_dir = filedialog.askdirectory(title="Select Project Directory")
        if not project_dir:
            return

        try:
            # Update workspace path
            self.workspace_path = project_dir
            # Legacy toolbox removed
            # self.toolbox.working_directory = project_dir

            # Reload file tree
            self.load_file_tree()

            # Log the loaded project
            self.log_terminal(f"\n{'='*50}\n")
            self.log_terminal(f"Loaded project: {project_dir}\n")
            self.log_terminal(f"{'='*50}\n")

            messagebox.showinfo("Success", f"Loaded project:\n{project_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load project: {e}")

    def scan_project(self):
        """Scan the current project and generate context for AI"""
        if not os.path.exists(self.workspace_path):
            messagebox.showwarning("Warning", "No project loaded")
            return

        self.log_terminal(f"\n{'='*50}\n")
        self.log_terminal(f"Scanning project: {self.workspace_path}\n")
        self.log_terminal(f"{'='*50}\n")

        threading.Thread(target=self._scan_project_thread, daemon=True).start()

    def _scan_project_thread(self):
        """Scan project in background thread"""
        try:
            # Collect project structure
            file_structure = []
            code_summary = []
            total_lines = 0

            # Supported file extensions
            code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rs', '.php', '.rb'}

            for root, dirs, files in os.walk(self.workspace_path):
                # Skip common non-code directories
                dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', 'venv', 'env', 'dist', 'build'}]

                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.workspace_path)
                    ext = os.path.splitext(file)[1]

                    if ext in code_extensions:
                        file_structure.append(rel_path)

                        # Read file content
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                lines = content.count('\n')
                                total_lines += lines

                                # Extract key information (classes, functions)
                                if ext == '.py':
                                    imports = re.findall(r'^import\s+(\S+)|^from\s+(\S+)', content, re.MULTILINE)
                                    classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
                                    functions = re.findall(r'^def\s+(\w+)', content, re.MULTILINE)

                                    if classes or functions:
                                        code_summary.append(f"\n{rel_path}:")
                                        if classes:
                                            code_summary.append(f"  Classes: {', '.join(classes)}")
                                        if functions:
                                            code_summary.append(f"  Functions: {', '.join(functions[:10])}")  # Limit to first 10
                        except:
                            pass

            # Generate scan report
            scan_report = f"""
PROJECT SCAN COMPLETE
{'='*60}

Project Path: {self.workspace_path}
Total Code Files: {len(file_structure)}
Total Lines of Code: {total_lines}

FILE STRUCTURE:
{chr(10).join('  ' + f for f in sorted(file_structure[:50]))}
{'  ... and more' if len(file_structure) > 50 else ''}

CODE SUMMARY:
{''.join(code_summary[:20])}
{'... and more' if len(code_summary) > 20 else ''}

{'='*60}
Project context loaded. You can now ask AI to modify or extend this project.
"""

            # Store project context for AI
            self.project_context = {
                'path': self.workspace_path,
                'files': file_structure,
                'total_lines': total_lines,
                'summary': code_summary
            }

            self.message_queue.put(('terminal', scan_report))

        except Exception as e:
            self.message_queue.put(('terminal', f"\nERROR scanning project: {e}\n"))

    def run_current_file(self):
        """Run current file"""
        if not self.current_file:
            messagebox.showwarning("Warning", "No file to run")
            return

        lang = self.language_var.get()
        run_cmd = self.languages[lang]['run_cmd'].format(file=self.current_file)

        self.log_terminal(f"\n{'='*50}\n")
        self.log_terminal(f"Running: {run_cmd}\n")
        self.log_terminal(f"{'='*50}\n")

        threading.Thread(target=self._run_file_thread, args=(run_cmd,), daemon=True).start()
    
    def _run_file_thread(self, command):
        """Run file in background"""
        try:
            result = subprocess.run(
                ['powershell', '-Command', command],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=os.path.dirname(self.current_file) if self.current_file else self.workspace_path
            )
            
            self.message_queue.put(('terminal', result.stdout))
            if result.stderr:
                self.message_queue.put(('terminal', f"ERRORS:\n{result.stderr}"))
            self.message_queue.put(('terminal', f"\nExit code: {result.returncode}\n"))
            
        except Exception as e:
            self.message_queue.put(('terminal', f"\nERROR: {e}\n"))
    
    def restore_from_backup(self):
        """Restore from backup"""
        backups = sorted([f for f in os.listdir(self.backup_path) if f.endswith('.backup')], reverse=True)
        
        if not backups:
            messagebox.showinfo("No Backups", "No backup files found")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Restore from Backup")
        dialog.geometry("600x400")
        
        ttk.Label(dialog, text="Select backup:", font=('Arial', 10, 'bold')).pack(pady=10)
        
        listbox = tk.Listbox(dialog, font=('Consolas', 9))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for backup in backups:
            listbox.insert(tk.END, backup)
        
        def do_restore():
            selection = listbox.curselection()
            if not selection:
                return
            
            backup_file = backups[selection[0]]
            original_name = '.'.join(backup_file.split('.')[:-2]) + '.' + backup_file.split('.')[-2]
            
            confirm = messagebox.askyesno("Confirm", f"Restore {original_name}?")
            if confirm:
                try:
                    shutil.copy2(os.path.join(self.backup_path, backup_file),
                               os.path.join(self.workspace_path, original_name))
                    messagebox.showinfo("Success", f"Restored {original_name}")
                    self.load_file_tree()
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Restore failed: {e}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(btn_frame, text="Restore", command=do_restore).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def log_terminal(self, text):
        """Log to terminal"""
        self.terminal_output.insert(tk.END, text)
        self.terminal_output.see(tk.END)
    
    def log_ai(self, text):
        """Log to AI panel"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.ai_log.insert(tk.END, f"[{timestamp}] {text}\n")
        self.ai_log.see(tk.END)

    def start_loading_animation(self, message="DeathAIAUS AI is thinking"):
        """Start the loading animation"""
        self.loading_animation_active = True
        self.loading_frame_index = 0
        self.animate_loading(message)

    def stop_loading_animation(self):
        """Stop the loading animation"""
        self.loading_animation_active = False
        self.loading_label.config(text="")

    def animate_loading(self, message):
        """Animate the loading indicator"""
        if not self.loading_animation_active:
            return

        # Skull animation frames
        frames = [
            "💀 ⚡ 💀 ⚡ 💀",
            "⚡ 💀 ⚡ 💀 ⚡",
            "💀 ⚡ 💀 ⚡ 💀",
            "⚡ 💀 ⚡ 💀 ⚡"
        ]

        # Spinner frames
        spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

        frame = frames[self.loading_frame_index % len(frames)]
        spin = spinner[self.loading_frame_index % len(spinner)]

        display_text = f"{frame}  {spin} {message} {spin}  {frame}"
        self.loading_label.config(text=display_text)

        self.loading_frame_index += 1
        self.root.after(150, lambda: self.animate_loading(message))

    def check_queue(self):
        """Check message queue"""
        try:
            while True:
                msg_type, content = self.message_queue.get_nowait()

                if msg_type == 'terminal':
                    self.log_terminal(content)
                elif msg_type == 'ai':
                    self.log_ai(content)
                elif msg_type == 'refresh_tree':
                    self.load_file_tree()
                elif msg_type == 'enable_build':
                    self.build_btn.config(state=tk.NORMAL)
                elif msg_type == 'enable_test':
                    self.test_btn.config(state=tk.NORMAL)
                elif msg_type == 'phase_complete':
                    self.analyze_btn.config(state=tk.NORMAL)
                    self.status_var.set("Phase complete")
                    self.is_running = False
                elif msg_type == 'start_loading':
                    self.start_loading_animation(content)
                elif msg_type == 'stop_loading':
                    self.stop_loading_animation()
                elif msg_type == 'open_in_tab':
                    # Open file in tab (content is tuple of (filepath, file_content))
                    filepath, file_content = content
                    self.tabs.add_tab(filepath, file_content)

        except queue.Empty:
            pass

        self.root.after(100, self.check_queue)
    
    def toggle_terminal(self):
        """Toggle terminal visibility"""
        if self.terminal_visible:
            # Hide terminal
            self.terminal_output.pack_forget()
            self.terminal_collapse_btn.config(text="▶ Show")
            self.terminal_visible = False
        else:
            # Show terminal
            self.terminal_output.pack(fill=tk.BOTH, expand=True)
            self.terminal_collapse_btn.config(text="▼ Hide")
            self.terminal_visible = True

    def toggle_description(self):
        """Toggle project description / feasibility workflow visibility"""
        if self.desc_visible:
            # Hide description section
            self.desc_container.pack_forget()
            self.desc_collapse_btn.config(text="▶ Show")
            self.desc_visible = False
        else:
            # Show description section
            self.desc_container.pack(fill=tk.X, padx=5, pady=5)
            self.desc_collapse_btn.config(text="▼ Hide")
            self.desc_visible = True

    def toggle_ai_log(self):
        """Toggle AI communication log visibility"""
        if self.log_visible:
            # Hide AI log
            self.log_container.pack_forget()
            self.log_collapse_btn.config(text="▶ Show")
            self.log_visible = False
        else:
            # Show AI log
            self.log_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.log_collapse_btn.config(text="▼ Hide")
            self.log_visible = True
    
    def run(self):
        """Run the IDE"""
        self.root.mainloop()


if __name__ == "__main__":
    print("=" * 70)
    print("DeathAIAUS IDE F.C - Feasibility Check Edition")
    print("=" * 70)
    print("[+] Brutally honest feasibility analysis")
    print("[+] Reality checks at every step")
    print("[+] Will help with massive projects - but you'll KNOW they're massive")
    print("[+] Automatic backups before AI changes")
    print("[+] Multi-language support")
    print()
    print("Detecting models...")
    
    ide = DeathAIAUSIDE()
    ide.run()
