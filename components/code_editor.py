"""
Enhanced Code Editor with Syntax Highlighting
"""
import tkinter as tk
from tkinter import ttk
from tkinter import font
import re
from components import death_theme as T


class EnhancedCodeEditor(tk.Frame):
    """Code editor with line numbers and syntax highlighting"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent)

        # Line numbers
        self.configure(bg=T.BG)
        self.line_numbers = tk.Text(self, width=5, padx=T.S3, pady=T.S3, takefocus=0, border=0,
                                    background=T.BG, foreground=T.MUTED, font=(T.MONO, 11),
                                    spacing1=2, spacing3=2, highlightthickness=0,
                                    state='disabled', wrap='none', cursor='arrow')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        tk.Frame(self, bg=T.BORDER2, width=1).pack(side=tk.LEFT, fill=tk.Y)

        # Text editor
        self.text_widget = tk.Text(self, wrap='none', undo=True, maxundo=-1,
                                   font=(T.MONO, 11), bg=T.BG, fg=T.TEXT,
                                   insertbackground=T.BLOOD_LIGHT, insertwidth=2,
                                   selectbackground=T.BLOOD, selectforeground=T.TEXT,
                                   padx=T.S4, pady=T.S3, spacing1=2, spacing3=2,
                                   relief=tk.FLAT, bd=0, highlightthickness=0,
                                   **kwargs)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.config(yscrollcommand=scrollbar.set)

        # Configure syntax highlighting tags
        self.text_widget.tag_configure("keyword", foreground=T.SYNTAX['keyword'])
        self.text_widget.tag_configure("string", foreground=T.SYNTAX['string'])
        self.text_widget.tag_configure("comment", foreground=T.SYNTAX['comment'], font=(T.MONO, 11, 'italic'))
        self.text_widget.tag_configure("function", foreground=T.SYNTAX['function'])
        self.text_widget.tag_configure("number", foreground=T.SYNTAX['number'])
        self.text_widget.tag_configure("class", foreground=T.SYNTAX['class'])
        self.text_widget.tag_configure("decorator", foreground=T.SYNTAX['decorator'])

        # Language
        self.current_language = "Python"

        # Bind events
        self.text_widget.bind("<<Change>>", self._on_change)
        self.text_widget.bind("<KeyRelease>", self._on_key_release)
        self.text_widget.bind("<Button-1>", lambda e: self.update_line_numbers())
        self.text_widget.bind("<MouseWheel>", lambda e: self.update_line_numbers())

        # Track changes for modified indicator
        self.is_modified = False

    def _on_change(self, event=None):
        """Handle text changes"""
        self.is_modified = True

    def _on_key_release(self, event):
        """Handle key release"""
        self.update_line_numbers()

        # Trigger syntax highlighting on certain keys
        if event.char in ['\n', '\r', ' ', '\t', ':', ')']:
            self.after(10, self.highlight_syntax)

    def update_line_numbers(self):
        """Update line numbers"""
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)

        line_count = int(self.text_widget.index('end-1c').split('.')[0])
        line_numbers_string = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')

    def highlight_syntax(self):
        """Apply syntax highlighting"""
        # Remove all existing tags
        for tag in ["keyword", "string", "comment", "function", "number", "class", "decorator"]:
            self.text_widget.tag_remove(tag, "1.0", tk.END)

        if self.current_language == "Python":
            self._highlight_python()
        elif self.current_language == "JavaScript":
            self._highlight_javascript()

    def _highlight_python(self):
        """Highlight Python syntax"""
        content = self.text_widget.get("1.0", tk.END)

        # Keywords
        keywords = ["def", "class", "import", "from", "if", "else", "elif", "for", "while",
                   "return", "try", "except", "with", "as", "pass", "break", "continue",
                   "True", "False", "None", "and", "or", "not", "in", "is", "lambda",
                   "yield", "async", "await", "raise", "finally", "assert", "del", "global",
                   "nonlocal"]

        for keyword in keywords:
            pattern = r'\b' + keyword + r'\b'
            for match in re.finditer(pattern, content):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_widget.tag_add("keyword", start, end)

        # Strings (single and double quotes)
        string_patterns = [r'"(?:[^"\\]|\\.)*"', r"'(?:[^'\\]|\\.)*'", r'""".*?"""', r"'''.*?'''"]
        for pattern in string_patterns:
            for match in re.finditer(pattern, content, re.DOTALL):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_widget.tag_add("string", start, end)

        # Comments
        for match in re.finditer(r'#[^\n]*', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_widget.tag_add("comment", start, end)

        # Function definitions
        for match in re.finditer(r'\bdef\s+(\w+)', content):
            start = f"1.0+{match.start(1)}c"
            end = f"1.0+{match.end(1)}c"
            self.text_widget.tag_add("function", start, end)

        # Class definitions
        for match in re.finditer(r'\bclass\s+(\w+)', content):
            start = f"1.0+{match.start(1)}c"
            end = f"1.0+{match.end(1)}c"
            self.text_widget.tag_add("class", start, end)

        # Decorators
        for match in re.finditer(r'@\w+', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_widget.tag_add("decorator", start, end)

        # Numbers
        for match in re.finditer(r'\b\d+\.?\d*\b', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_widget.tag_add("number", start, end)

    def _highlight_javascript(self):
        """Highlight JavaScript syntax"""
        content = self.text_widget.get("1.0", tk.END)

        keywords = ["function", "const", "let", "var", "if", "else", "for", "while",
                   "return", "class", "import", "export", "async", "await", "try", "catch",
                   "new", "this", "super", "extends", "static", "null", "undefined",
                   "true", "false"]

        for keyword in keywords:
            pattern = r'\b' + keyword + r'\b'
            for match in re.finditer(pattern, content):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_widget.tag_add("keyword", start, end)

        # Strings
        string_patterns = [r'"(?:[^"\\]|\\.)*"', r"'(?:[^'\\]|\\.)*'", r'`(?:[^`\\]|\\.)*`']
        for pattern in string_patterns:
            for match in re.finditer(pattern, content, re.DOTALL):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_widget.tag_add("string", start, end)

        # Comments
        for match in re.finditer(r'//[^\n]*', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_widget.tag_add("comment", start, end)

        # Multi-line comments
        for match in re.finditer(r'/\*.*?\*/', content, re.DOTALL):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_widget.tag_add("comment", start, end)

    def set_language(self, language):
        """Set the programming language for syntax highlighting"""
        self.current_language = language
        self.highlight_syntax()

    def get(self, start, end=None):
        """Get text from editor"""
        return self.text_widget.get(start, end)

    def insert(self, index, text, *args):
        """Insert text into editor"""
        self.text_widget.insert(index, text, *args)
        self.update_line_numbers()

    def delete(self, start, end=None):
        """Delete text from editor"""
        self.text_widget.delete(start, end)
        self.update_line_numbers()

    def mark_saved(self):
        """Mark file as saved"""
        self.is_modified = False
