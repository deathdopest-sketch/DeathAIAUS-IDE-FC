"""
AI Chat Interface - Persistent conversation sidebar
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from datetime import datetime
from components import death_theme as T


class AIChatInterface(ttk.Frame):
    """Persistent AI chat sidebar"""

    def __init__(self, parent, ide_instance, show_header=True):
        super().__init__(parent)
        self.ide = ide_instance
        self.conversation_history = []
        self.ai_name = getattr(ide_instance, 'ai_name', 'Thanatos')

        # Header
        if show_header:
            header = T.pane_header(self, self.ai_name)
            clear = tk.Label(header, text="CLEAR", bg=T.BG3, fg=T.MUTED, font=(T.MONO, 8), cursor='hand2')
            clear.pack(side=tk.RIGHT, padx=T.S4)
            clear.bind('<Button-1>', lambda e: self.clear_chat())

        # Chat display
        chat_frame = tk.Frame(self, bg=T.BG)
        chat_frame.pack(fill=tk.BOTH, expand=True)

        self.chat_display = tk.Text(
            chat_frame,
            wrap=tk.WORD,
            font=(T.UI, 11),
            bg=T.BG,
            fg=T.TEXT,
            state='disabled',
            cursor='arrow',
            relief=tk.FLAT, bd=0, highlightthickness=0,
            padx=T.S6, pady=T.S4,
            spacing1=3, spacing2=4, spacing3=3,
        )
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(chat_frame, command=self.chat_display.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_display.config(yscrollcommand=scrollbar.set)

        # Configure tags
        self.chat_display.tag_configure("user", foreground=T.TEXT2, font=(T.MONO, 8, 'bold'),
                                        spacing1=T.S6, spacing3=T.S1)
        self.chat_display.tag_configure("ai", foreground=T.BLOOD_LIGHT, font=(T.MONO, 8, 'bold'),
                                        spacing1=T.S6, spacing3=T.S1)
        self.chat_display.tag_configure("user_body", lmargin1=T.S4, lmargin2=T.S4, foreground=T.TEXT2)
        self.chat_display.tag_configure("code", background=T.BG3, font=(T.MONO, 10),
                                       foreground=T.TEXT, lmargin1=T.S4, lmargin2=T.S4,
                                       spacing1=T.S2, spacing3=T.S2)
        self.chat_display.tag_configure("timestamp", foreground=T.MUTED, font=(T.MONO, 8))
        self.chat_display.tag_configure("error", foreground=T.BLOOD_LIGHT, background=T.BLOOD_DEEP)

        tk.Frame(self, bg=T.BORDER2, height=1).pack(fill=tk.X)

        # Composer: context + input + actions
        composer = tk.Frame(self, bg=T.BG3, padx=T.S4, pady=T.S4)
        composer.pack(fill=tk.X)

        context_frame = tk.Frame(composer, bg=T.BG3)
        context_frame.pack(fill=tk.X, pady=(0, T.S3))

        T.hud(context_frame, "Context").pack(side=tk.LEFT, padx=(0, T.S3))

        self.include_current_file = tk.BooleanVar(value=True)
        ttk.Checkbutton(context_frame, text="Current file",
                        variable=self.include_current_file).pack(side=tk.LEFT, padx=(0, T.S3))

        self.include_project = tk.BooleanVar(value=False)
        ttk.Checkbutton(context_frame, text="Project",
                        variable=self.include_project).pack(side=tk.LEFT)

        # Input text (blood left edge)
        input_wrap = tk.Frame(composer, bg=T.BLOOD)
        input_wrap.pack(fill=tk.X)
        self.chat_input = tk.Text(input_wrap, height=4, font=(T.UI, 11),
                                  bg=T.BG, fg=T.TEXT, insertbackground=T.BLOOD_LIGHT, insertwidth=2,
                                  relief=tk.FLAT, bd=0, highlightthickness=0,
                                  padx=T.S3, pady=T.S3, wrap=tk.WORD)
        self.chat_input.pack(fill=tk.BOTH, expand=True, padx=(2, 0))
        self.chat_input.bind("<Return>", self._on_enter)
        self.chat_input.bind("<Shift-Return>", self._on_shift_enter)

        # Quick actions + send
        actions_frame = tk.Frame(composer, bg=T.BG3)
        actions_frame.pack(fill=tk.X, pady=(T.S3, 0))

        quick_actions = [
            ("Explain", "Explain this code"),
            ("Fix", "Find and fix errors"),
            ("Improve", "Suggest improvements"),
            ("Test", "Write tests for this")
        ]

        for label, prompt in quick_actions:
            T.button(actions_frame, label, lambda p=prompt: self.quick_action(p),
                     size='sm').pack(side=tk.LEFT, padx=(0, T.S2))

        T.button(actions_frame, "Transmit", self.send_message,
                 variant='primary', size='sm').pack(side=tk.RIGHT)

    def _on_enter(self, event):
        """Handle Enter key"""
        if not event.state & 0x1:  # Shift not pressed
            self.send_message()
            return "break"

    def _on_shift_enter(self, event):
        """Handle Shift+Enter for newline"""
        return None  # Allow default behavior

    def quick_action(self, prompt):
        """Execute a quick action"""
        self.chat_input.delete("1.0", tk.END)
        self.chat_input.insert("1.0", prompt)
        self.send_message()

    def send_message(self):
        """Send message to AI"""
        message = self.chat_input.get("1.0", tk.END).strip()
        if not message:
            return

        # Clear input
        self.chat_input.delete("1.0", tk.END)

        # Add to display
        self.add_message("user", message)

        # Build context
        context = self._build_context()

        # Send to AI in background
        threading.Thread(target=self._ai_response_thread,
                        args=(message, context), daemon=True).start()

    def _build_context(self):
        """Build context for AI"""
        context = ""

        if self.include_current_file.get() and hasattr(self.ide, 'current_file') and self.ide.current_file:
            try:
                if hasattr(self.ide, 'tabs') and self.ide.tabs.current_editor:
                    content = self.ide.tabs.current_editor.get('1.0', tk.END)
                    context += f"\n\nCurrent file: {self.ide.current_file}\n"
                    context += f"```\n{content}\n```\n"
            except:
                pass

        if self.include_project.get() and hasattr(self.ide, 'project_context') and self.ide.project_context:
            context += f"\n\nProject: {self.ide.workspace_path}\n"
            context += f"Files: {', '.join(self.ide.project_context['files'][:10])}\n"

        return context

    def _ai_response_thread(self, message, context):
        """Get AI response in background"""
        try:
            system_prompt = f"""You are an AI coding assistant integrated into an IDE.
Help the user with their code. Be concise but helpful.
Provide code in markdown code blocks when relevant.

{context}"""

            # Call AI model
            response = self.ide._call_model(
                self.ide.coder_model.get() if hasattr(self.ide, 'coder_model') else 'default',
                system_prompt,
                message,
                120
            )

            self.add_message("ai", response)

        except Exception as e:
            self.add_message("ai", f"Error: {str(e)}", is_error=True)

    def add_message(self, sender, message, is_error=False):
        """Add message to chat display"""
        timestamp = datetime.now().strftime('%H:%M:%S')

        self.chat_display.config(state='normal')

        # Sender line:  // THANATOS  23:14:02
        if sender == "user":
            self.chat_display.insert(tk.END, "\nYOU  ", "user")
        else:
            self.chat_display.insert(tk.END, f"\n// {self.ai_name.upper()}  ", "ai")
        self.chat_display.insert(tk.END, f"{timestamp}\n", "timestamp")

        # Message with code block parsing
        if is_error:
            self.chat_display.insert(tk.END, f" {message} ", "error")
        elif sender == "user":
            self.chat_display.insert(tk.END, message, "user_body")
        else:
            self._insert_formatted_message(message)

        self.chat_display.insert(tk.END, "\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

        # Store in history
        self.conversation_history.append({
            "role": sender,
            "content": message,
            "timestamp": timestamp
        })

    def _insert_formatted_message(self, message):
        """Insert message with code block formatting"""
        parts = message.split("```")
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Regular text
                self.chat_display.insert(tk.END, part)
            else:  # Code block
                # Remove language identifier if present
                lines = part.split('\n', 1)
                code = lines[1] if len(lines) > 1 else lines[0]
                self.chat_display.insert(tk.END, f"\n{code}\n", "code")

    def clear_chat(self):
        """Clear chat history"""
        self.chat_display.config(state='normal')
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state='disabled')
        self.conversation_history = []
        self.add_message("ai", "Chat cleared. How can I help you?")
