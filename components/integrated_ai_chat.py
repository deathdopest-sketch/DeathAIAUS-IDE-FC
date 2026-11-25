"""
Integrated AI Chat with Built-in Model Server
Connects existing AI features to the built-in model server
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from datetime import datetime
from components import death_theme as T


class IntegratedAIChat(tk.Frame):
    """AI chat using built-in model server"""

    def __init__(self, parent, ide_instance, ai_server):
        super().__init__(parent, bg=T.BG)
        self.ide = ide_instance
        self.ai_server = ai_server

        self.conversation_history = []

        self.setup_ui()

    def setup_ui(self):
        """Setup chat UI"""
        # Header
        header = tk.Frame(self, bg=T.BG3, height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="🤖 AI Assistant", font=(T.UI, 11, 'bold'),
                fg=T.BILE, bg=T.BG3).pack(side=tk.LEFT, padx=10)

        # Model status
        self.model_status = tk.Label(header, text="No model loaded",
                                     font=(T.UI, 9), fg=T.TEXT2, bg=T.BG3)
        self.model_status.pack(side=tk.RIGHT, padx=10)

        # Update model status
        self.update_model_status()

        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            self,
            bg=T.BG,
            fg=T.TEXT,
            font=(T.MONO, 10),
            wrap=tk.WORD,
            state=tk.DISABLED,
            insertbackground=T.TEXT
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configure tags
        self.chat_display.tag_configure('user', foreground=T.SIGNAL)
        self.chat_display.tag_configure('assistant', foreground=T.BILE)
        self.chat_display.tag_configure('system', foreground=T.TEXT2, font=(T.MONO, 9))
        self.chat_display.tag_configure('error', foreground=T.BLOOD_LIGHT)
        self.chat_display.tag_configure('code', background=T.BG3, font=(T.MONO, 9))

        # Input area
        input_frame = tk.Frame(self, bg=T.BG3)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.input_field = tk.Text(
            input_frame,
            bg=T.BG,
            fg=T.TEXT,
            font=(T.MONO, 10),
            height=3,
            insertbackground=T.TEXT
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Bind Enter key
        self.input_field.bind('<Return>', self.on_enter_key)
        self.input_field.bind('<Shift-Return>', lambda e: None)  # Allow newline with Shift+Enter

        # Send button
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            bg=T.BLOOD,
            fg=T.TEXT,
            font=(T.UI, 10, 'bold'),
            relief=tk.FLAT,
            padx=20
        )
        self.send_button.pack(side=tk.RIGHT)

        # Quick actions
        actions_frame = tk.Frame(self, bg=T.BG)
        actions_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        tk.Button(actions_frame, text="📝 Explain Code", command=lambda: self.quick_action('explain'),
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT, font=(T.UI, 8)).pack(side=tk.LEFT, padx=2)

        tk.Button(actions_frame, text="🐛 Find Bugs", command=lambda: self.quick_action('bugs'),
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT, font=(T.UI, 8)).pack(side=tk.LEFT, padx=2)

        tk.Button(actions_frame, text="⚡ Optimize", command=lambda: self.quick_action('optimize'),
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT, font=(T.UI, 8)).pack(side=tk.LEFT, padx=2)

        tk.Button(actions_frame, text="📚 Add Docs", command=lambda: self.quick_action('docs'),
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT, font=(T.UI, 8)).pack(side=tk.LEFT, padx=2)

        tk.Button(actions_frame, text="🔧 Refactor", command=lambda: self.quick_action('refactor'),
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT, font=(T.UI, 8)).pack(side=tk.LEFT, padx=2)

        tk.Button(actions_frame, text="🧪 Write Tests", command=lambda: self.quick_action('tests'),
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT, font=(T.UI, 8)).pack(side=tk.LEFT, padx=2)

        # Clear button
        tk.Button(actions_frame, text="🗑️ Clear", command=self.clear_chat,
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT, font=(T.UI, 8)).pack(side=tk.RIGHT, padx=2)

    def update_model_status(self):
        """Update model status label"""
        model_info = self.ai_server.get_model_info()

        if model_info and model_info['loaded']:
            self.model_status.config(
                text=f"✓ {model_info['name']}",
                fg=T.BILE
            )
        else:
            self.model_status.config(
                text="⚠️ No model loaded - click to load",
                fg=T.AMBER
            )
            self.model_status.bind('<Button-1>', lambda e: self.open_model_manager())

        # Schedule next update
        self.after(3000, self.update_model_status)

    def open_model_manager(self):
        """Open model manager"""
        from components.ai_model_server import ModelManagerDialog

        # Get root window
        root = self.winfo_toplevel()
        ModelManagerDialog(root, self.ai_server)

    def on_enter_key(self, event):
        """Handle Enter key"""
        # Check if Shift is held
        if event.state & 0x1:  # Shift key
            return  # Allow newline

        # Send message
        self.send_message()
        return 'break'  # Prevent default newline

    def send_message(self):
        """Send user message"""
        message = self.input_field.get('1.0', tk.END).strip()

        if not message:
            return

        # Clear input
        self.input_field.delete('1.0', tk.END)

        # Check if model is loaded
        if not self.ai_server.is_running or not self.ai_server.current_model:
            self.add_message('system', "⚠️ No model loaded. Please load a model from the Model Manager.", 'error')
            return

        # Add user message to chat
        self.add_message('user', message, 'user')

        # Add to history
        self.conversation_history.append({'role': 'user', 'content': message})

        # Disable send button
        self.send_button.config(state=tk.DISABLED, text="Thinking...")

        # Get context from current file
        context = self._get_current_context()

        # Build prompt
        full_prompt = self._build_prompt(message, context)

        # Generate response
        def response_callback(text):
            self.after(0, lambda: self._append_to_chat(text))

        def generate_thread():
            try:
                self.ai_server.generate(
                    full_prompt,
                    max_tokens=512,
                    temperature=0.7,
                    callback=response_callback
                )

                # Re-enable send button
                self.after(0, lambda: self.send_button.config(state=tk.NORMAL, text="Send"))

            except Exception as e:
                self.after(0, lambda: self.add_message('system', f"Error: {e}", 'error'))
                self.after(0, lambda: self.send_button.config(state=tk.NORMAL, text="Send"))

        # Start generation in thread
        threading.Thread(target=generate_thread, daemon=True).start()

        # Start assistant message
        self.add_message('assistant', '', 'assistant', end='')

    def _get_current_context(self):
        """Get context from current editor"""
        context = {}

        # Try to get current file content
        if hasattr(self.ide, 'get_current_editor'):
            editor = self.ide.get_current_editor()
            if editor:
                context['current_file'] = editor.get('1.0', 'end-1c')

        # Try to get selected text
        if hasattr(self.ide, 'get_selected_text'):
            selected = self.ide.get_selected_text()
            if selected:
                context['selection'] = selected

        return context

    def _build_prompt(self, message, context):
        """Build full prompt with context"""
        prompt_parts = []

        # System prompt
        prompt_parts.append("You are an AI coding assistant integrated into an IDE. Be concise and helpful.")

        # Add context if available
        if context.get('selection'):
            prompt_parts.append(f"\n\nSelected code:\n```\n{context['selection']}\n```")
        elif context.get('current_file'):
            # Limit current file context to avoid token overflow
            file_content = context['current_file']
            if len(file_content) > 1000:
                file_content = file_content[:500] + "\n...\n" + file_content[-500:]

            prompt_parts.append(f"\n\nCurrent file:\n```\n{file_content}\n```")

        # Add conversation history (last 3 turns)
        if self.conversation_history:
            prompt_parts.append("\n\nConversation history:")
            for turn in self.conversation_history[-6:]:  # Last 3 user+assistant pairs
                role = turn['role'].capitalize()
                content = turn['content'][:200]  # Limit length
                prompt_parts.append(f"{role}: {content}")

        # Add current message
        prompt_parts.append(f"\n\nUser: {message}")
        prompt_parts.append("\nAssistant:")

        return '\n'.join(prompt_parts)

    def _append_to_chat(self, text):
        """Append text to chat (for streaming)"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, text, 'assistant')
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def add_message(self, role, message, tag='assistant', end='\n\n'):
        """Add message to chat display"""
        self.chat_display.config(state=tk.NORMAL)

        # Add timestamp for user/assistant messages
        if role in ['user', 'assistant']:
            timestamp = datetime.now().strftime('%H:%M')
            prefix = f"[{timestamp}] {role.capitalize()}: "
            self.chat_display.insert(tk.END, prefix, tag)

        self.chat_display.insert(tk.END, message + end, tag)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

        # Add to history (for assistant)
        if role == 'assistant' and message:
            self.conversation_history.append({'role': 'assistant', 'content': message})

    def quick_action(self, action_type):
        """Perform quick action"""
        # Get current selection or file
        context = self._get_current_context()

        if not context.get('selection') and not context.get('current_file'):
            self.add_message('system', "⚠️ No code available. Please open a file or select code.", 'error')
            return

        code = context.get('selection') or context.get('current_file', '')

        # Limit code length
        if len(code) > 1000:
            code = code[:1000] + "\n... (truncated)"

        # Build prompt based on action
        prompts = {
            'explain': f"Explain this code:\n\n```\n{code}\n```",
            'bugs': f"Find potential bugs in this code:\n\n```\n{code}\n```",
            'optimize': f"Suggest optimizations for this code:\n\n```\n{code}\n```",
            'docs': f"Add documentation to this code:\n\n```\n{code}\n```",
            'refactor': f"Suggest refactoring for this code:\n\n```\n{code}\n```",
            'tests': f"Write unit tests for this code:\n\n```\n{code}\n```"
        }

        prompt = prompts.get(action_type, code)

        # Set in input field and send
        self.input_field.delete('1.0', tk.END)
        self.input_field.insert('1.0', prompt)
        self.send_message()

    def clear_chat(self):
        """Clear chat history"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete('1.0', tk.END)
        self.chat_display.config(state=tk.DISABLED)

        self.conversation_history.clear()

        self.add_message('system', "Chat cleared. Start a new conversation!", 'system')


class IntegratedInlineSuggestions:
    """Inline suggestions using built-in model server"""

    def __init__(self, ide_instance, ai_server):
        self.ide = ide_instance
        self.ai_server = ai_server
        self.enabled = True
        self.suggestion_text = ""
        self.check_timer = None
        self.suggestion_tag = 'ai_suggestion'

    def setup_editor(self, editor, file_path=""):
        """Setup editor for inline suggestions"""
        # Configure suggestion tag
        editor.tag_configure(
            self.suggestion_tag,
            foreground=T.MUTED,
            background=T.BG3
        )

        # Bind events
        editor.bind('<<Modified>>', lambda e: self.on_text_changed(editor))
        editor.bind('<Tab>', lambda e: self.accept_suggestion(editor))
        editor.bind('<Escape>', lambda e: self.dismiss_suggestion(editor))

    def on_text_changed(self, editor):
        """Handle text change"""
        if not self.enabled:
            return

        # Clear previous timer
        if self.check_timer:
            editor.after_cancel(self.check_timer)

        # Dismiss current suggestion
        self.dismiss_suggestion(editor)

        # Schedule suggestion check
        self.check_timer = editor.after(1500, lambda: self.check_for_suggestion(editor))

    def check_for_suggestion(self, editor):
        """Check if suggestion should be shown"""
        if not self.ai_server.is_running:
            return

        try:
            # Get current line
            cursor_pos = editor.index(tk.INSERT)
            line_num = int(cursor_pos.split('.')[0])

            # Get context (current line + previous lines)
            start_line = max(1, line_num - 10)
            context = editor.get(f"{start_line}.0", f"{line_num}.end")

            # Get current line content
            current_line = editor.get(f"{line_num}.0", f"{line_num}.end")

            # Only suggest if line is not empty and ends with certain patterns
            if not current_line.strip():
                return

            # Build prompt
            prompt = f"""Complete this code:

{context}"""

            # Generate suggestion
            def on_suggestion(text):
                self.show_suggestion(editor, text.strip())

            # Request completion (async)
            threading.Thread(
                target=lambda: self.ai_server.generate(
                    prompt,
                    max_tokens=100,
                    temperature=0.3,
                    callback=lambda t: editor.after(0, lambda: on_suggestion(t))
                ),
                daemon=True
            ).start()

        except Exception as e:
            print(f"Suggestion error: {e}")

    def show_suggestion(self, editor, suggestion):
        """Show inline suggestion"""
        if not suggestion:
            return

        try:
            # Get cursor position
            cursor_pos = editor.index(tk.INSERT)

            # Insert suggestion
            editor.insert(cursor_pos, suggestion, self.suggestion_tag)

            # Store suggestion
            self.suggestion_text = suggestion

        except Exception as e:
            print(f"Show suggestion error: {e}")

    def accept_suggestion(self, editor):
        """Accept current suggestion"""
        if self.suggestion_text:
            # Remove tag (make it permanent)
            editor.tag_remove(self.suggestion_tag, '1.0', tk.END)
            self.suggestion_text = ""
            return 'break'

    def dismiss_suggestion(self, editor):
        """Dismiss current suggestion"""
        if self.suggestion_text:
            # Find and remove suggestion
            ranges = editor.tag_ranges(self.suggestion_tag)
            if ranges:
                editor.delete(ranges[0], ranges[-1])

            self.suggestion_text = ""
