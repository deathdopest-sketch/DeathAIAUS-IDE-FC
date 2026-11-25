"""
Session Memory UI - View and manage what AI remembers
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import json
import os
from components import death_theme as T


class SessionMemoryPanel(tk.Toplevel):
    """Panel to view and manage AI session memory"""
    
    def __init__(self, parent, ide_instance):
        super().__init__(parent)
        self.ide = ide_instance
        self.title("AI Session Memory")
        self.geometry("900x700")
        self.configure(bg=T.BG)
        
        self.setup_ui()
        self.load_memory()
        
    def setup_ui(self):
        """Setup memory panel UI"""
        # Header
        header = tk.Frame(self, bg=T.BG3, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🧠 AI Session Memory", 
                font=(T.UI, 14, 'bold'),
                fg=T.SIGNAL, bg=T.BG3).pack(side=tk.LEFT, padx=15, pady=15)
        
        tk.Label(header, text="What the AI remembers about your project",
                font=(T.UI, 9, 'italic'),
                fg=T.TEXT2, bg=T.BG3).pack(side=tk.LEFT, padx=(0,15))
        
        # Tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Conversation History
        conv_frame = tk.Frame(notebook, bg=T.BG)
        notebook.add(conv_frame, text="💬 Conversations")
        self.setup_conversation_tab(conv_frame)
        
        # Tab 2: Project Context
        context_frame = tk.Frame(notebook, bg=T.BG)
        notebook.add(context_frame, text="📁 Project Context")
        self.setup_context_tab(context_frame)
        
        # Tab 3: Learned Patterns
        patterns_frame = tk.Frame(notebook, bg=T.BG)
        notebook.add(patterns_frame, text="🎯 Learned Patterns")
        self.setup_patterns_tab(patterns_frame)
        
        # Button bar
        button_frame = tk.Frame(self, bg=T.BG)
        button_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        
        tk.Button(button_frame, text="💾 Export Memory",
                 command=self.export_memory,
                 bg=T.HOVER, fg=T.TEXT, font=(T.UI, 10),
                 relief=tk.FLAT, padx=20, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🗑️ Clear Memory",
                 command=self.clear_memory,
                 bg=T.BLOOD, fg=T.TEXT, font=(T.UI, 10),
                 relief=tk.FLAT, padx=20, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🔄 Refresh",
                 command=self.load_memory,
                 bg=T.HOVER, fg=T.TEXT, font=(T.UI, 10),
                 relief=tk.FLAT, padx=20, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Close",
                 command=self.destroy,
                 bg=T.HOVER, fg=T.TEXT, font=(T.UI, 10),
                 relief=tk.FLAT, padx=20, pady=8,
                 cursor='hand2').pack(side=tk.RIGHT, padx=5)
    
    def setup_conversation_tab(self, parent):
        """Setup conversation history tab"""
        tk.Label(parent, text="Recent AI Conversations:",
                font=(T.UI, 11, 'bold'),
                fg=T.TEXT, bg=T.BG, anchor='w').pack(fill=tk.X, padx=10, pady=(10,5))
        
        self.conversation_display = scrolledtext.ScrolledText(
            parent,
            font=(T.UI, 10),
            bg=T.BG2,
            fg=T.TEXT,
            wrap=tk.WORD,
            state='disabled'
        )
        self.conversation_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        
        # Configure tags
        self.conversation_display.tag_configure('user', foreground=T.BILE, font=(T.UI, 10, 'bold'))
        self.conversation_display.tag_configure('ai', foreground=T.SIGNAL, font=(T.UI, 10, 'bold'))
        self.conversation_display.tag_configure('timestamp', foreground=T.MUTED, font=(T.UI, 9))
    
    def setup_context_tab(self, parent):
        """Setup project context tab"""
        tk.Label(parent, text="What AI Knows About Your Project:",
                font=(T.UI, 11, 'bold'),
                fg=T.TEXT, bg=T.BG, anchor='w').pack(fill=tk.X, padx=10, pady=(10,5))
        
        self.context_display = scrolledtext.ScrolledText(
            parent,
            font=(T.MONO, 10),
            bg=T.BG2,
            fg=T.TEXT,
            wrap=tk.WORD,
            state='disabled'
        )
        self.context_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
    
    def setup_patterns_tab(self, parent):
        """Setup learned patterns tab"""
        tk.Label(parent, text="Patterns AI Has Learned:",
                font=(T.UI, 11, 'bold'),
                fg=T.TEXT, bg=T.BG, anchor='w').pack(fill=tk.X, padx=10, pady=(10,5))
        
        self.patterns_display = scrolledtext.ScrolledText(
            parent,
            font=(T.UI, 10),
            bg=T.BG2,
            fg=T.TEXT,
            wrap=tk.WORD,
            state='disabled'
        )
        self.patterns_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
    
    def load_memory(self):
        """Load memory from AI memory component"""
        # Load conversation history
        if hasattr(self.ide, 'ai_chat') and hasattr(self.ide.ai_chat, 'conversation_history'):
            self.load_conversations()
        else:
            self.conversation_display.config(state='normal')
            self.conversation_display.delete('1.0', tk.END)
            self.conversation_display.insert('1.0', "No conversation history available.\n\n"
                                                     "Start chatting with AI to build memory!")
            self.conversation_display.config(state='disabled')
        
        # Load project context
        if hasattr(self.ide, 'smart_context'):
            self.load_project_context()
        else:
            self.context_display.config(state='normal')
            self.context_display.delete('1.0', tk.END)
            self.context_display.insert('1.0', "Project context not available.")
            self.context_display.config(state='disabled')
        
        # Load learned patterns
        if hasattr(self.ide, 'ai_memory'):
            self.load_patterns()
        else:
            self.patterns_display.config(state='normal')
            self.patterns_display.delete('1.0', tk.END)
            self.patterns_display.insert('1.0', "AI Memory component not initialized.")
            self.patterns_display.config(state='disabled')
    
    def load_conversations(self):
        """Load conversation history"""
        self.conversation_display.config(state='normal')
        self.conversation_display.delete('1.0', tk.END)
        
        history = self.ide.ai_chat.conversation_history
        if not history:
            self.conversation_display.insert('1.0', "No conversations yet.\n\nStart chatting to build history!")
        else:
            for entry in history[-50:]:  # Last 50 messages
                role = entry.get('role', 'unknown')
                content = entry.get('content', '')
                timestamp = entry.get('timestamp', datetime.now().strftime('%H:%M:%S'))
                
                self.conversation_display.insert(tk.END, f"\n[{timestamp}] ", 'timestamp')
                if role == 'user':
                    self.conversation_display.insert(tk.END, "You: ", 'user')
                else:
                    self.conversation_display.insert(tk.END, "AI: ", 'ai')
                
                self.conversation_display.insert(tk.END, f"{content}\n")
        
        self.conversation_display.config(state='disabled')
    
    def load_project_context(self):
        """Load project context"""
        self.context_display.config(state='normal')
        self.context_display.delete('1.0', tk.END)
        
        context = "📂 Project Information:\n\n"
        context += f"Location: {self.ide.workspace_path}\n\n"
        
        # Get project structure from smart context
        if hasattr(self.ide.smart_context, 'project_files'):
            context += f"Files: {len(self.ide.smart_context.project_files)}\n"
        
        if hasattr(self.ide.smart_context, 'symbols'):
            context += f"Symbols tracked: {len(self.ide.smart_context.symbols)}\n"
        
        context += "\n🎯 Current Focus:\n\n"
        if hasattr(self.ide, 'current_file') and self.ide.current_file:
            context += f"Working on: {self.ide.current_file}\n"
        
        context += "\n💡 Recent Actions:\n\n"
        context += "- Files opened\n"
        context += "- AI queries made\n"
        context += "- Code modifications\n"
        
        self.context_display.insert('1.0', context)
        self.context_display.config(state='disabled')
    
    def load_patterns(self):
        """Load learned patterns"""
        self.patterns_display.config(state='normal')
        self.patterns_display.delete('1.0', tk.END)
        
        patterns = "🎯 Learned Patterns:\n\n"
        patterns += "• Coding style preferences\n"
        patterns += "• Frequently used libraries\n"
        patterns += "• Common error patterns\n"
        patterns += "• Workflow preferences\n\n"
        patterns += "📊 Statistics:\n\n"
        patterns += f"Total interactions: {len(self.ide.ai_chat.conversation_history) if hasattr(self.ide, 'ai_chat') else 0}\n"
        patterns += f"Files worked on: {len(self.ide.tabs.tabs) if hasattr(self.ide, 'tabs') else 0}\n"
        
        self.patterns_display.insert('1.0', patterns)
        self.patterns_display.config(state='disabled')
    
    def export_memory(self):
        """Export memory to file"""
        try:
            memory_data = {
                'timestamp': datetime.now().isoformat(),
                'conversation_history': self.ide.ai_chat.conversation_history if hasattr(self.ide, 'ai_chat') else [],
                'workspace': self.ide.workspace_path,
                'current_file': self.ide.current_file if hasattr(self.ide, 'current_file') else None
            }
            
            export_path = os.path.join(self.ide.workspace_path, 'ai_memory_export.json')
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2)
            
            messagebox.showinfo("Export", f"Memory exported to:\n{export_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")
    
    def clear_memory(self):
        """Clear AI memory"""
        if messagebox.askyesno("Clear Memory", 
                              "This will clear all conversation history and learned patterns.\n\n"
                              "Are you sure?"):
            if hasattr(self.ide, 'ai_chat'):
                self.ide.ai_chat.conversation_history.clear()
            
            messagebox.showinfo("Cleared", "AI memory has been cleared.")
            self.load_memory()
