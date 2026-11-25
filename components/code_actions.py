"""
Code Actions Menu
Right-click context menu with AI-powered code actions
"""
import tkinter as tk
from tkinter import messagebox
import threading
from components import death_theme as T


class CodeActionsMenu:
    """Context menu with code actions"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.menu = None
        self.selected_text = ""
        self.selection_range = None

    def setup_bindings(self, text_widget):
        """Setup right-click bindings on a text widget"""
        text_widget.bind('<Button-3>', self.show_menu)  # Right-click

    def show_menu(self, event):
        """Show context menu at cursor position"""
        widget = event.widget

        # Get selection
        try:
            self.selected_text = widget.get("sel.first", "sel.last")
            self.selection_range = (widget.index("sel.first"), widget.index("sel.last"))
        except tk.TclError:
            # No selection - get current line
            line_start = widget.index("insert linestart")
            line_end = widget.index("insert lineend")
            self.selected_text = widget.get(line_start, line_end)
            self.selection_range = (line_start, line_end)

        if not self.selected_text.strip():
            return

        # Create menu
        if self.menu:
            self.menu.destroy()

        self.menu = tk.Menu(widget, tearoff=0, bg=T.BG3, fg=T.TEXT,
                           activebackground=T.HOVER, activeforeground=T.TEXT)

        # AI Actions
        self.menu.add_command(label="✨ Explain Code", command=self.explain_code)
        self.menu.add_command(label="🔧 Refactor", command=self.refactor_code)
        self.menu.add_command(label="🐛 Find Bugs", command=self.find_bugs)
        self.menu.add_command(label="📝 Add Comments", command=self.add_comments)
        self.menu.add_command(label="🧪 Generate Tests", command=self.generate_tests)

        self.menu.add_separator()

        # Quick Actions
        self.menu.add_command(label="🔀 Extract Function", command=self.extract_function)
        self.menu.add_command(label="📋 Duplicate", command=lambda: self.duplicate_code(widget))
        self.menu.add_command(label="💬 Toggle Comment", command=lambda: self.toggle_comment(widget))

        self.menu.add_separator()

        # Standard Actions
        self.menu.add_command(label="✂️ Cut", command=lambda: widget.event_generate("<<Cut>>"))
        self.menu.add_command(label="📋 Copy", command=lambda: widget.event_generate("<<Copy>>"))
        self.menu.add_command(label="📌 Paste", command=lambda: widget.event_generate("<<Paste>>"))

        # Show menu
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def explain_code(self):
        """Explain selected code using AI"""
        if not self.selected_text.strip():
            return

        # Send to AI chat if available
        if hasattr(self.ide, 'ai_chat'):
            prompt = f"Explain this code:\n\n```\n{self.selected_text}\n```"
            self.ide.ai_chat.chat_input.delete("1.0", tk.END)
            self.ide.ai_chat.chat_input.insert("1.0", prompt)
            self.ide.ai_chat.send_message()
        else:
            # Call AI directly
            self._call_ai_action(
                "Explain this code in detail",
                self.selected_text,
                action_type="explain"
            )

    def refactor_code(self):
        """Refactor selected code using AI"""
        self._call_ai_action(
            "Refactor this code to improve readability and performance. Return ONLY the refactored code.",
            self.selected_text,
            action_type="replace"
        )

    def find_bugs(self):
        """Find potential bugs in selected code"""
        self._call_ai_action(
            "Analyze this code for bugs and potential issues. List any problems found.",
            self.selected_text,
            action_type="explain"
        )

    def add_comments(self):
        """Add comments to selected code"""
        self._call_ai_action(
            "Add helpful comments to this code. Return the code with comments added.",
            self.selected_text,
            action_type="replace"
        )

    def generate_tests(self):
        """Generate unit tests for selected code"""
        self._call_ai_action(
            "Generate unit tests for this code. Return ONLY the test code.",
            self.selected_text,
            action_type="insert"
        )

    def extract_function(self):
        """Extract selected code into a function"""
        # Simple extraction - AI can do better
        if not self.selected_text.strip():
            return

        dialog = tk.Toplevel(self.ide.root)
        dialog.title("Extract Function")
        dialog.geometry("400x150")
        dialog.configure(bg=T.BG3)

        tk.Label(dialog, text="Function name:", bg=T.BG3, fg=T.TEXT,
                font=(T.UI, 10)).pack(pady=10)

        name_var = tk.StringVar(value="extracted_function")
        name_entry = tk.Entry(dialog, textvariable=name_var, font=(T.UI, 10),
                             bg=T.BG, fg=T.TEXT)
        name_entry.pack(pady=5, padx=20, fill=tk.X)
        name_entry.focus()
        name_entry.select_range(0, tk.END)

        def extract():
            func_name = name_var.get().strip()
            if not func_name:
                return

            # Get language
            lang = "Python"  # Default
            if hasattr(self.ide, 'tabs') and self.ide.tabs.current_editor:
                editor = self.ide.tabs.current_editor
                if hasattr(editor, 'current_language'):
                    lang = editor.current_language

            # Generate function
            if lang == "Python":
                func_code = f"def {func_name}():\n"
                for line in self.selected_text.split('\n'):
                    func_code += f"    {line}\n"
                func_code += f"\n\n{func_name}()"
            else:  # JavaScript
                func_code = f"function {func_name}() {{\n"
                for line in self.selected_text.split('\n'):
                    func_code += f"    {line}\n"
                func_code += f"}}\n\n{func_name}();"

            # Replace selection
            if self.selection_range and hasattr(self.ide, 'tabs'):
                editor = self.ide.tabs.current_editor
                if editor:
                    editor.delete(self.selection_range[0], self.selection_range[1])
                    editor.insert(self.selection_range[0], func_code)

                    if hasattr(editor, 'highlight_syntax'):
                        editor.highlight_syntax()

            dialog.destroy()

        tk.Button(dialog, text="Extract", command=extract,
                 bg=T.BLOOD, fg=T.TEXT, font=(T.UI, 10, 'bold'),
                 relief=tk.FLAT, padx=20).pack(pady=10)

    def duplicate_code(self, widget):
        """Duplicate selected code"""
        if self.selection_range:
            widget.insert(self.selection_range[1], "\n" + self.selected_text)

    def toggle_comment(self, widget):
        """Toggle comments on selected lines"""
        if not self.selection_range:
            return

        # Detect language
        lang = "Python"
        if hasattr(widget, 'current_language'):
            lang = widget.current_language

        comment_char = '#' if lang == 'Python' else '//'

        # Get line range
        start_line = int(self.selection_range[0].split('.')[0])
        end_line = int(self.selection_range[1].split('.')[0])

        # Check if first line is commented
        first_line = widget.get(f"{start_line}.0", f"{start_line}.end")
        is_commented = first_line.strip().startswith(comment_char)

        # Toggle comments
        for line_num in range(start_line, end_line + 1):
            line_content = widget.get(f"{line_num}.0", f"{line_num}.end")

            if is_commented:
                # Remove comment
                if line_content.strip().startswith(comment_char):
                    idx = line_content.find(comment_char)
                    new_content = line_content[:idx] + line_content[idx+len(comment_char):].lstrip()
                    widget.delete(f"{line_num}.0", f"{line_num}.end")
                    widget.insert(f"{line_num}.0", new_content)
            else:
                # Add comment
                stripped = line_content.lstrip()
                if stripped:
                    indent = len(line_content) - len(stripped)
                    new_content = line_content[:indent] + comment_char + ' ' + stripped
                    widget.delete(f"{line_num}.0", f"{line_num}.end")
                    widget.insert(f"{line_num}.0", new_content)

        # Rehighlight
        if hasattr(widget, 'highlight_syntax'):
            widget.highlight_syntax()

    def _call_ai_action(self, prompt, code, action_type="explain"):
        """Call AI for code action"""
        if not hasattr(self.ide, '_call_model'):
            messagebox.showerror("Error", "AI model not available")
            return

        # Show loading
        if hasattr(self.ide, 'status_bar'):
            self.ide.status_bar.config(text=f"🤖 AI processing...")

        # Call in background
        threading.Thread(
            target=self._ai_action_thread,
            args=(prompt, code, action_type),
            daemon=True
        ).start()

    def _ai_action_thread(self, prompt, code, action_type):
        """Background thread for AI action"""
        try:
            # Build full prompt
            full_prompt = f"{prompt}\n\n```\n{code}\n```"

            system_prompt = """You are a code assistant. Provide clear, concise responses.
When asked to return code, return ONLY the code without explanations or markdown.
When asked to explain, be clear and helpful."""

            # Call model
            response = self.ide._call_model(
                self.ide.coder_model.get() if hasattr(self.ide, 'coder_model') else 'default',
                system_prompt,
                full_prompt,
                60
            )

            # Process response on main thread
            self.ide.root.after(0, self._process_ai_response, response, action_type)

        except Exception as e:
            self.ide.root.after(0, lambda: messagebox.showerror(
                "Error", f"AI action failed: {e}"))

        finally:
            # Clear status
            if hasattr(self.ide, 'status_bar'):
                self.ide.root.after(0, lambda: self.ide.status_bar.config(text="Ready"))

    def _process_ai_response(self, response, action_type):
        """Process AI response (on main thread)"""
        if action_type == "explain":
            # Show in AI chat or message box
            if hasattr(self.ide, 'ai_chat'):
                self.ide.ai_chat.add_message("ai", response)
            else:
                messagebox.showinfo("AI Response", response)

        elif action_type == "replace":
            # Replace selected code
            if self.selection_range and hasattr(self.ide, 'tabs'):
                editor = self.ide.tabs.current_editor
                if editor:
                    # Strip markdown if present
                    clean_response = response.strip()
                    if '```' in clean_response:
                        parts = clean_response.split('```')
                        if len(parts) >= 3:
                            clean_response = parts[1]
                            # Remove language identifier
                            if '\n' in clean_response:
                                clean_response = clean_response.split('\n', 1)[1]

                    editor.delete(self.selection_range[0], self.selection_range[1])
                    editor.insert(self.selection_range[0], clean_response.strip())

                    if hasattr(editor, 'highlight_syntax'):
                        editor.highlight_syntax()

        elif action_type == "insert":
            # Insert after selection
            if self.selection_range and hasattr(self.ide, 'tabs'):
                editor = self.ide.tabs.current_editor
                if editor:
                    # Strip markdown if present
                    clean_response = response.strip()
                    if '```' in clean_response:
                        parts = clean_response.split('```')
                        if len(parts) >= 3:
                            clean_response = parts[1]
                            if '\n' in clean_response:
                                clean_response = clean_response.split('\n', 1)[1]

                    editor.insert(self.selection_range[1], "\n\n" + clean_response.strip())

                    if hasattr(editor, 'highlight_syntax'):
                        editor.highlight_syntax()


class QuickFixProvider:
    """Provides quick fixes for common code issues"""

    def __init__(self, ide_instance):
        self.ide = ide_instance

    def get_quick_fixes(self, line_content, language="Python"):
        """Get quick fixes for a line of code"""
        fixes = []

        if language == "Python":
            # Missing colon
            if any(kw in line_content for kw in ['def ', 'class ', 'if ', 'for ', 'while ']):
                if not line_content.rstrip().endswith(':'):
                    fixes.append({
                        'title': 'Add missing colon',
                        'fix': line_content.rstrip() + ':'
                    })

            # Missing quotes
            if '=' in line_content and '"' not in line_content and "'" not in line_content:
                parts = line_content.split('=')
                if len(parts) == 2 and parts[1].strip() and not parts[1].strip().isdigit():
                    fixes.append({
                        'title': 'Add quotes around string',
                        'fix': f"{parts[0]}= '{parts[1].strip()}'"
                    })

        elif language == "JavaScript":
            # Missing semicolon
            if not line_content.rstrip().endswith((';', '{', '}')):
                if any(kw in line_content for kw in ['const ', 'let ', 'var ', 'return ']):
                    fixes.append({
                        'title': 'Add missing semicolon',
                        'fix': line_content.rstrip() + ';'
                    })

        return fixes

    def apply_fix(self, editor, line_num, new_content):
        """Apply a quick fix"""
        editor.delete(f"{line_num}.0", f"{line_num}.end")
        editor.insert(f"{line_num}.0", new_content)

        if hasattr(editor, 'highlight_syntax'):
            editor.highlight_syntax()
