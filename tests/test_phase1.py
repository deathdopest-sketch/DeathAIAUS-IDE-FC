#!/usr/bin/env python3
"""
Test Phase 1 Features
Demonstrates the new Enhanced Code Editor and AI Chat Interface
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add components to path
sys.path.insert(0, os.path.dirname(__file__))

from components.code_editor import EnhancedCodeEditor
from components.ai_chat import AIChatInterface


class Phase1TestIDE:
    """Minimal IDE to test Phase 1 features"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DeathAIAUS IDE - Phase 1 Test")
        self.root.geometry("1400x800")
        self.root.configure(bg='#1e1e1e')

        # Mock IDE attributes needed by AI Chat
        self.current_file = None
        self.workspace_path = os.path.dirname(__file__)
        self.project_context = None
        self.coder_model = type('obj', (object,), {'get': lambda: 'test-model'})()

        self.setup_gui()

    def setup_gui(self):
        """Setup the test GUI"""
        # Main container
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)

        # Left: Editor
        editor_frame = tk.Frame(main_paned, bg='#1e1e1e')
        main_paned.add(editor_frame, weight=3)

        # Editor header
        header = tk.Frame(editor_frame, bg='#2d2d2d', height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="💀 Enhanced Code Editor Test",
                font=('Arial', 12, 'bold'), fg='#00ff00', bg='#2d2d2d').pack(side=tk.LEFT, padx=10)

        # Language selector
        tk.Label(header, text="Language:", bg='#2d2d2d', fg='#cccccc').pack(side=tk.LEFT, padx=5)
        self.lang_var = tk.StringVar(value="Python")
        lang_combo = ttk.Combobox(header, textvariable=self.lang_var,
                                  values=["Python", "JavaScript"],
                                  state='readonly', width=12)
        lang_combo.pack(side=tk.LEFT, padx=5)
        lang_combo.bind('<<ComboboxSelected>>', self.change_language)

        # Buttons
        tk.Button(header, text="Load Sample", command=self.load_sample,
                 bg='#0066cc', fg='white', relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        tk.Button(header, text="Highlight", command=self.manual_highlight,
                 bg='#00aa00', fg='white', relief=tk.FLAT).pack(side=tk.LEFT, padx=5)

        # Enhanced code editor
        self.code_editor = EnhancedCodeEditor(editor_frame)
        self.code_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add sample text
        sample_python = '''# Sample Python Code
import tkinter as tk
from datetime import datetime

class Example:
    """Example class"""

    def __init__(self, name):
        self.name = name
        self.count = 0

    @property
    def status(self):
        """Get status"""
        return f"{self.name}: {self.count}"

    def increment(self):
        """Increment counter"""
        self.count += 1
        return True

# Main code
if __name__ == "__main__":
    example = Example("test")
    for i in range(10):
        example.increment()
    print(example.status)
'''
        self.code_editor.insert("1.0", sample_python)
        self.code_editor.highlight_syntax()
        self.code_editor.update_line_numbers()

        # Right: AI Chat
        chat_frame = tk.Frame(main_paned, bg='#2d2d2d', width=400)
        main_paned.add(chat_frame, weight=1)

        # AI Chat interface
        self.ai_chat = AIChatInterface(chat_frame, self)
        self.ai_chat.pack(fill=tk.BOTH, expand=True)

        # Add welcome message
        self.ai_chat.add_message("ai", "👋 Welcome to Phase 1 Testing!\n\n✨ Features Active:\n• Syntax highlighting\n• Line numbers\n• AI Chat interface\n\nTry typing some code or ask me a question!")

        # Instructions
        info_frame = tk.Frame(self.root, bg='#2d2d2d')
        info_frame.pack(fill=tk.X, side=tk.BOTTOM)

        info_text = """
🧪 TESTING PHASE 1 FEATURES:
1️⃣ Enhanced Code Editor: Type code and see syntax highlighting in real-time
2️⃣ AI Chat: Ask questions (Note: Requires LM Studio running for AI responses)
3️⃣ Quick Actions: Try "Explain", "Fix", "Improve" buttons
        """

        tk.Label(info_frame, text=info_text, bg='#2d2d2d', fg='#cccccc',
                font=('Arial', 9), justify=tk.LEFT).pack(padx=10, pady=5)

    def change_language(self, event=None):
        """Change syntax highlighting language"""
        lang = self.lang_var.get()
        self.code_editor.set_language(lang)

        if lang == "JavaScript":
            sample_js = '''// Sample JavaScript Code
const express = require('express');
const app = express();

class Server {
    constructor(port) {
        this.port = port;
        this.app = app;
    }

    async start() {
        try {
            this.app.listen(this.port, () => {
                console.log(`Server running on port ${this.port}`);
            });
            return true;
        } catch (error) {
            console.error('Failed to start:', error);
            return false;
        }
    }
}

// Initialize
const server = new Server(3000);
server.start();
'''
            self.code_editor.delete("1.0", tk.END)
            self.code_editor.insert("1.0", sample_js)
            self.code_editor.highlight_syntax()

    def load_sample(self):
        """Load sample code"""
        self.change_language()

    def manual_highlight(self):
        """Manually trigger syntax highlighting"""
        self.code_editor.highlight_syntax()
        self.code_editor.update_line_numbers()

    def _call_model(self, model_name, system_prompt, user_message, timeout):
        """Mock AI call for testing (returns helpful message)"""
        # This is a mock - replace with actual LM Studio call
        return f"""I'm a test response!

To enable real AI responses:
1. Start LM Studio on localhost:1234
2. Load a model
3. The AI chat will work automatically

For now, I can show you that the chat interface is working perfectly!

Try typing some code in the editor and I'll help you with it once connected to a real model."""

    def run(self):
        """Run the test IDE"""
        self.root.mainloop()


if __name__ == "__main__":
    print("🚀 Starting Phase 1 Test IDE...")
    print("✅ Enhanced Code Editor")
    print("✅ AI Chat Interface")
    print("\n📝 Features to test:")
    print("   • Syntax highlighting (type Python or JavaScript code)")
    print("   • Line numbers (scroll to see)")
    print("   • AI Chat (ask questions)")
    print("   • Quick actions (Explain, Fix, Improve, Test buttons)")
    print("\n⚠️  Note: AI responses require LM Studio running")
    print("\n🎯 Starting GUI...\n")

    ide = Phase1TestIDE()
    ide.run()
