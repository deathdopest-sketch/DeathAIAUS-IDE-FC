"""
Inline AI Suggestions
GitHub Copilot-style inline code completions
"""
import tkinter as tk
from tkinter import font as tkfont
import threading
import time
from components import death_theme as T


class InlineSuggestion:
    """Manages inline AI suggestions for code editor"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.enabled = True
        self.suggestion_text = ""
        self.suggestion_visible = False
        self.last_check_time = 0
        self.check_delay = 1.5  # Wait 1.5s after typing stops
        self.current_editor = None
        self.suggestion_tag = "inline_suggestion"
        self.typing_timer = None

    def setup_editor(self, editor, file_path=""):
        """Setup inline suggestions for an editor"""
        self.current_editor = editor

        # Configure suggestion tag
        editor.tag_configure(
            self.suggestion_tag,
            foreground=T.MUTED,
            background=T.BG3
        )

        # Bind events
        editor.bind('<KeyRelease>', self.on_key_release)
        editor.bind('<Tab>', self.accept_suggestion)
        editor.bind('<Escape>', self.dismiss_suggestion)
        editor.bind('<Button-1>', lambda e: self.dismiss_suggestion())

    def on_key_release(self, event):
        """Handle key release - trigger suggestion check"""
        if not self.enabled:
            return

        # Ignore modifier keys
        if event.keysym in ['Shift_L', 'Shift_R', 'Control_L', 'Control_R',
                           'Alt_L', 'Alt_R', 'Meta_L', 'Meta_R']:
            return

        # Dismiss on special keys
        if event.keysym in ['Escape', 'Return', 'BackSpace', 'Delete']:
            self.dismiss_suggestion()
            return

        # Schedule suggestion check
        self.schedule_suggestion_check()

    def schedule_suggestion_check(self):
        """Schedule a suggestion check after typing stops"""
        # Cancel previous timer
        if self.typing_timer:
            self.current_editor.after_cancel(self.typing_timer)

        # Dismiss current suggestion while typing
        self.dismiss_suggestion()

        # Schedule new check
        self.typing_timer = self.current_editor.after(
            int(self.check_delay * 1000),
            self.check_for_suggestion
        )

    def check_for_suggestion(self):
        """Check if we should show a suggestion"""
        if not self.enabled or not self.current_editor:
            return

        try:
            # Get context
            cursor_pos = self.current_editor.index('insert')
            line_num = int(cursor_pos.split('.')[0])
            col_num = int(cursor_pos.split('.')[1])

            # Get current line
            current_line = self.current_editor.get(f"{line_num}.0", f"{line_num}.end")

            # Don't suggest on empty lines or if at beginning of line
            if not current_line.strip() or col_num == 0:
                return

            # Get preceding context (last 10 lines)
            start_line = max(1, line_num - 10)
            context = self.current_editor.get(f"{start_line}.0", cursor_pos)

            # Request suggestion in background
            threading.Thread(
                target=self._request_suggestion_thread,
                args=(context, cursor_pos, line_num, col_num),
                daemon=True
            ).start()

        except Exception as e:
            print(f"Suggestion check error: {e}")

    def _request_suggestion_thread(self, context, cursor_pos, line_num, col_num):
        """Request AI suggestion in background thread"""
        try:
            # Detect language
            language = "Python"
            if hasattr(self.current_editor, 'current_language'):
                language = self.current_editor.current_language

            # Build prompt
            prompt = f"""Complete the following {language} code. Provide ONLY the completion text that should come next, without any explanations or markdown.

Context:
```
{context}
```

Complete from the cursor position. Provide only the next 1-3 lines of code that would logically follow."""

            system_prompt = """You are an AI code completion assistant. Provide only the code completion, no explanations, no markdown blocks, no comments about the code. Just the raw completion text."""

            # Call AI model
            if hasattr(self.ide, '_call_model'):
                response = self.ide._call_model(
                    self.ide.coder_model.get() if hasattr(self.ide, 'coder_model') else 'default',
                    system_prompt,
                    prompt,
                    30  # Short timeout for suggestions
                )

                # Clean response
                suggestion = self._clean_suggestion(response)

                if suggestion:
                    # Show suggestion on main thread
                    self.current_editor.after(
                        0,
                        self._show_suggestion,
                        suggestion,
                        cursor_pos
                    )

        except Exception as e:
            print(f"Suggestion request error: {e}")

    def _clean_suggestion(self, response):
        """Clean AI response to get just the code"""
        if not response:
            return ""

        # Remove markdown code blocks
        if '```' in response:
            parts = response.split('```')
            if len(parts) >= 3:
                response = parts[1]
                # Remove language identifier
                if '\n' in response:
                    response = response.split('\n', 1)[1]

        # Strip and limit to first few lines
        lines = response.strip().split('\n')
        suggestion_lines = lines[:3]  # Max 3 lines

        # Don't suggest if too long
        suggestion = '\n'.join(suggestion_lines)
        if len(suggestion) > 200:
            return ""

        return suggestion

    def _show_suggestion(self, suggestion, position):
        """Show inline suggestion (called on main thread)"""
        if not self.current_editor or not suggestion:
            return

        try:
            # Verify cursor hasn't moved
            current_pos = self.current_editor.index('insert')
            if current_pos != position:
                return

            # Store suggestion
            self.suggestion_text = suggestion
            self.suggestion_visible = True

            # Insert suggestion with tag
            self.current_editor.insert(position, suggestion, self.suggestion_tag)

            # Add marker for end of suggestion
            end_pos = self.current_editor.index(position + f" + {len(suggestion)}c")
            self.current_editor.mark_set("suggestion_end", end_pos)

        except Exception as e:
            print(f"Show suggestion error: {e}")

    def accept_suggestion(self, event=None):
        """Accept the current suggestion (Tab key)"""
        if not self.suggestion_visible or not self.suggestion_text:
            return None  # Allow default Tab behavior

        try:
            # Remove the suggestion tag (keeps the text)
            ranges = self.current_editor.tag_ranges(self.suggestion_tag)
            if ranges:
                start, end = ranges[0], ranges[1]
                self.current_editor.tag_remove(self.suggestion_tag, start, end)

                # Move cursor to end of suggestion
                self.current_editor.mark_set('insert', end)
                self.current_editor.see('insert')

                # Highlight syntax
                if hasattr(self.current_editor, 'highlight_syntax'):
                    self.current_editor.highlight_syntax()

            self.suggestion_visible = False
            self.suggestion_text = ""

            return "break"  # Prevent default Tab

        except Exception as e:
            print(f"Accept suggestion error: {e}")
            return None

    def dismiss_suggestion(self, event=None):
        """Dismiss the current suggestion"""
        if not self.suggestion_visible:
            return

        try:
            # Remove suggestion text
            ranges = self.current_editor.tag_ranges(self.suggestion_tag)
            if ranges:
                self.current_editor.delete(ranges[0], ranges[1])

            self.suggestion_visible = False
            self.suggestion_text = ""

        except Exception as e:
            print(f"Dismiss suggestion error: {e}")

    def toggle_enabled(self):
        """Toggle suggestions on/off"""
        self.enabled = not self.enabled
        if not self.enabled:
            self.dismiss_suggestion()
        return self.enabled


class SuggestionStatusWidget(tk.Frame):
    """Status widget showing suggestion state"""

    def __init__(self, parent, inline_suggestion):
        super().__init__(parent, bg=T.BG3)
        self.inline_suggestion = inline_suggestion

        self.status_label = tk.Label(
            self,
            text="✨ AI Suggestions: ON",
            bg=T.BG3,
            fg=T.BILE,
            font=(T.UI, 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

        # Toggle button
        self.toggle_btn = tk.Button(
            self,
            text="Toggle",
            command=self.toggle,
            bg=T.HOVER,
            fg=T.TEXT,
            relief=tk.FLAT,
            padx=10
        )
        self.toggle_btn.pack(side=tk.LEFT, padx=5)

        # Hint label
        self.hint_label = tk.Label(
            self,
            text="Tab: Accept • Esc: Dismiss",
            bg=T.BG3,
            fg=T.TEXT2,
            font=(T.UI, 8)
        )
        self.hint_label.pack(side=tk.LEFT, padx=10)

    def toggle(self):
        """Toggle suggestions"""
        enabled = self.inline_suggestion.toggle_enabled()
        if enabled:
            self.status_label.config(text="✨ AI Suggestions: ON", fg=T.BILE)
        else:
            self.status_label.config(text="✨ AI Suggestions: OFF", fg=T.TEXT2)


class MultiLineSuggestion:
    """Enhanced multi-line suggestion system"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.inline_suggestion = InlineSuggestion(ide_instance)

    def setup_editor(self, editor, file_path=""):
        """Setup enhanced suggestions"""
        self.inline_suggestion.setup_editor(editor, file_path)

        # Add additional keybindings
        editor.bind('<Control-space>', self.trigger_manual_suggestion)
        editor.bind('<Alt-]>', self.next_suggestion)
        editor.bind('<Alt-[>', self.previous_suggestion)

    def trigger_manual_suggestion(self, event=None):
        """Manually trigger suggestion (Ctrl+Space)"""
        self.inline_suggestion.check_for_suggestion()
        return "break"

    def next_suggestion(self, event=None):
        """Get next suggestion alternative"""
        # TODO: Implement multiple suggestion alternatives
        return "break"

    def previous_suggestion(self, event=None):
        """Get previous suggestion alternative"""
        # TODO: Implement multiple suggestion alternatives
        return "break"


class SmartCompletion:
    """Smart context-aware completions"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.completion_cache = {}  # Cache recent completions

    def get_context_completion(self, editor, trigger_char=""):
        """Get context-aware completion"""
        try:
            # Get cursor position
            cursor_pos = editor.index('insert')
            line_num = int(cursor_pos.split('.')[0])

            # Get current line
            current_line = editor.get(f"{line_num}.0", cursor_pos)

            # Get word being typed
            words = current_line.split()
            if not words:
                return []

            current_word = words[-1]

            # Get completions based on context
            completions = []

            # Import completions
            if current_line.strip().startswith('import ') or current_line.strip().startswith('from '):
                completions = self._get_import_completions(current_word)

            # Method/attribute completions
            elif '.' in current_word:
                completions = self._get_attribute_completions(current_word)

            # Variable completions
            else:
                completions = self._get_variable_completions(editor, current_word)

            return completions

        except Exception as e:
            print(f"Context completion error: {e}")
            return []

    def _get_import_completions(self, prefix):
        """Get import completions"""
        # Common Python modules
        common_modules = [
            'os', 'sys', 'json', 'time', 'datetime', 'math', 'random',
            'tkinter', 'threading', 'subprocess', 'collections', 're',
            'numpy', 'pandas', 'matplotlib', 'requests', 'flask', 'django'
        ]

        return [m for m in common_modules if m.startswith(prefix)]

    def _get_attribute_completions(self, dotted):
        """Get attribute completions for object.attribute"""
        # Basic implementation - can be enhanced with actual object inspection
        parts = dotted.split('.')
        if len(parts) < 2:
            return []

        obj = parts[0]

        # Common patterns
        if obj in ['os', 'sys', 'json', 'time']:
            # Common methods for these modules
            return [
                f"{obj}.path", f"{obj}.getcwd", f"{obj}.listdir",
                f"{obj}.read", f"{obj}.write", f"{obj}.open"
            ]

        return []

    def _get_variable_completions(self, editor, prefix):
        """Get variable completions from current file"""
        try:
            content = editor.get('1.0', 'end')

            # Find all variable/function names
            import re
            # Python patterns
            patterns = [
                r'def\s+(\w+)',  # Functions
                r'class\s+(\w+)',  # Classes
                r'(\w+)\s*=',  # Variables
            ]

            names = set()
            for pattern in patterns:
                matches = re.findall(pattern, content)
                names.update(matches)

            # Filter by prefix
            return sorted([n for n in names if n.startswith(prefix)])

        except:
            return []


class CompletionPopup:
    """Popup menu for completions"""

    def __init__(self, editor):
        self.editor = editor
        self.popup = None
        self.completions = []
        self.selected_index = 0

    def show(self, completions, position=None):
        """Show completion popup"""
        if not completions:
            return

        self.completions = completions
        self.selected_index = 0

        # Create popup if doesn't exist
        if self.popup:
            self.popup.destroy()

        self.popup = tk.Toplevel(self.editor)
        self.popup.wm_overrideredirect(True)

        # Position near cursor
        if not position:
            x, y, _, _ = self.editor.bbox('insert')
            x += self.editor.winfo_rootx()
            y += self.editor.winfo_rooty() + 20
        else:
            x, y = position

        self.popup.geometry(f"+{x}+{y}")

        # Listbox
        self.listbox = tk.Listbox(
            self.popup,
            bg=T.BG3,
            fg=T.TEXT,
            selectbackground=T.HOVER,
            selectforeground=T.TEXT,
            relief=tk.FLAT,
            height=min(10, len(completions)),
            width=30
        )
        self.listbox.pack()

        # Populate
        for item in completions:
            self.listbox.insert(tk.END, item)

        self.listbox.selection_set(0)

        # Bindings
        self.editor.bind('<Down>', self.select_next)
        self.editor.bind('<Up>', self.select_previous)
        self.editor.bind('<Return>', self.accept)
        self.editor.bind('<Escape>', self.dismiss)

    def select_next(self, event=None):
        """Select next completion"""
        self.selected_index = (self.selected_index + 1) % len(self.completions)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(self.selected_index)
        self.listbox.see(self.selected_index)
        return "break"

    def select_previous(self, event=None):
        """Select previous completion"""
        self.selected_index = (self.selected_index - 1) % len(self.completions)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(self.selected_index)
        self.listbox.see(self.selected_index)
        return "break"

    def accept(self, event=None):
        """Accept selected completion"""
        if self.completions and self.popup:
            completion = self.completions[self.selected_index]
            self.editor.insert('insert', completion)
            self.dismiss()
        return "break"

    def dismiss(self, event=None):
        """Dismiss popup"""
        if self.popup:
            self.popup.destroy()
            self.popup = None

        # Unbind
        self.editor.unbind('<Down>')
        self.editor.unbind('<Up>')
        self.editor.unbind('<Return>')
        self.editor.unbind('<Escape>')
