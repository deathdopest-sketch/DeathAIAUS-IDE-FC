"""
Search and Replace Dialog
Provides find/replace functionality in files and projects
"""
import tkinter as tk
from tkinter import ttk
import os
import re
from components import death_theme as T


class SearchDialog:
    """Search and replace dialog for the IDE"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.dialog = None
        self.search_var = None
        self.replace_var = None
        self.case_sensitive = None
        self.regex_mode = None
        self.whole_word = None
        self.current_match_index = -1
        self.matches = []

    def show_find(self):
        """Show find dialog"""
        self._create_dialog("Find")

    def show_replace(self):
        """Show find and replace dialog"""
        self._create_dialog("Replace")

    def _create_dialog(self, mode="Find"):
        """Create the search dialog"""
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.focus()
            return

        self.dialog = tk.Toplevel(self.ide.root)
        self.dialog.title(f"{mode} in File")
        self.dialog.geometry("500x250")
        self.dialog.configure(bg=T.BG3)
        self.dialog.transient(self.ide.root)

        # Search field
        search_frame = tk.Frame(self.dialog, bg=T.BG3)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(search_frame, text="Find:", bg=T.BG3, fg=T.TEXT,
                width=10, anchor='w').pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               bg=T.BG, fg=T.TEXT, insertbackground=T.TEXT)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        search_entry.focus()

        # Replace field (if in replace mode)
        if mode == "Replace":
            replace_frame = tk.Frame(self.dialog, bg=T.BG3)
            replace_frame.pack(fill=tk.X, padx=10, pady=5)

            tk.Label(replace_frame, text="Replace:", bg=T.BG3, fg=T.TEXT,
                    width=10, anchor='w').pack(side=tk.LEFT)

            self.replace_var = tk.StringVar()
            replace_entry = tk.Entry(replace_frame, textvariable=self.replace_var,
                                    bg=T.BG, fg=T.TEXT, insertbackground=T.TEXT)
            replace_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Options
        options_frame = tk.Frame(self.dialog, bg=T.BG3)
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        self.case_sensitive = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Case sensitive",
                      variable=self.case_sensitive,
                      bg=T.BG3, fg=T.TEXT, selectcolor=T.BG,
                      activebackground=T.BG3).pack(side=tk.LEFT, padx=5)

        self.regex_mode = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Regex",
                      variable=self.regex_mode,
                      bg=T.BG3, fg=T.TEXT, selectcolor=T.BG,
                      activebackground=T.BG3).pack(side=tk.LEFT, padx=5)

        self.whole_word = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Whole word",
                      variable=self.whole_word,
                      bg=T.BG3, fg=T.TEXT, selectcolor=T.BG,
                      activebackground=T.BG3).pack(side=tk.LEFT, padx=5)

        # Scope
        scope_frame = tk.Frame(self.dialog, bg=T.BG3)
        scope_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(scope_frame, text="Scope:", bg=T.BG3, fg=T.TEXT).pack(side=tk.LEFT, padx=5)

        self.scope_var = tk.StringVar(value="current")
        tk.Radiobutton(scope_frame, text="Current file", variable=self.scope_var, value="current",
                      bg=T.BG3, fg=T.TEXT, selectcolor=T.BG,
                      activebackground=T.BG3).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(scope_frame, text="All open files", variable=self.scope_var, value="open",
                      bg=T.BG3, fg=T.TEXT, selectcolor=T.BG,
                      activebackground=T.BG3).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(scope_frame, text="Project", variable=self.scope_var, value="project",
                      bg=T.BG3, fg=T.TEXT, selectcolor=T.BG,
                      activebackground=T.BG3).pack(side=tk.LEFT, padx=5)

        # Results
        self.results_label = tk.Label(self.dialog, text="", bg=T.BG3, fg=T.TEXT2,
                                     font=(T.UI, 9))
        self.results_label.pack(fill=tk.X, padx=10, pady=5)

        # Buttons
        button_frame = tk.Frame(self.dialog, bg=T.BG3)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(button_frame, text="Find Next", command=self.find_next,
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT, padx=15).pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="Find Previous", command=self.find_previous,
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT, padx=15).pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="Find All", command=self.find_all,
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT, padx=15).pack(side=tk.LEFT, padx=5)

        if mode == "Replace":
            tk.Button(button_frame, text="Replace", command=self.replace_current,
                     bg=T.BLOOD, fg=T.TEXT, relief=tk.FLAT, padx=15).pack(side=tk.LEFT, padx=5)

            tk.Button(button_frame, text="Replace All", command=self.replace_all,
                     bg=T.BLOOD, fg=T.TEXT, relief=tk.FLAT, padx=15).pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="Close", command=self.close_dialog,
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT, padx=15).pack(side=tk.RIGHT, padx=5)

        # Bind Enter key
        search_entry.bind('<Return>', lambda e: self.find_next())
        if mode == "Replace" and hasattr(self, 'replace_var'):
            replace_entry.bind('<Return>', lambda e: self.replace_current())

    def _get_current_editor(self):
        """Get the current editor widget"""
        if hasattr(self.ide, 'tabs') and self.ide.tabs.current_editor:
            return self.ide.tabs.current_editor
        elif hasattr(self.ide, 'code_editor'):
            return self.ide.code_editor
        return None

    def _build_pattern(self, search_text):
        """Build regex pattern from search text and options"""
        if not search_text:
            return None

        if self.regex_mode.get():
            pattern = search_text
        else:
            pattern = re.escape(search_text)

        if self.whole_word.get():
            pattern = r'\b' + pattern + r'\b'

        flags = 0 if self.case_sensitive.get() else re.IGNORECASE

        try:
            return re.compile(pattern, flags)
        except re.error as e:
            self.results_label.config(text=f"Invalid regex: {e}", fg=T.BLOOD_LIGHT)
            return None

    def find_next(self):
        """Find next occurrence"""
        editor = self._get_current_editor()
        if not editor:
            return

        search_text = self.search_var.get()
        if not search_text:
            return

        pattern = self._build_pattern(search_text)
        if not pattern:
            return

        # Get content from current position to end
        current_pos = editor.index("insert")
        content = editor.get(current_pos, "end-1c")

        match = pattern.search(content)
        if match:
            # Calculate absolute position
            start_idx = editor.index(f"{current_pos}+{match.start()}c")
            end_idx = editor.index(f"{current_pos}+{match.end()}c")

            # Select and show
            editor.tag_remove("sel", "1.0", "end")
            editor.tag_add("sel", start_idx, end_idx)
            editor.mark_set("insert", end_idx)
            editor.see(start_idx)

            self.results_label.config(text=f"Found at {start_idx}", fg=T.BILE)
        else:
            # Wrap around to beginning
            content = editor.get("1.0", current_pos)
            match = pattern.search(content)
            if match:
                start_idx = editor.index(f"1.0+{match.start()}c")
                end_idx = editor.index(f"1.0+{match.end()}c")

                editor.tag_remove("sel", "1.0", "end")
                editor.tag_add("sel", start_idx, end_idx)
                editor.mark_set("insert", end_idx)
                editor.see(start_idx)

                self.results_label.config(text=f"Found at {start_idx} (wrapped)", fg=T.BILE)
            else:
                self.results_label.config(text="No matches found", fg=T.BLOOD_LIGHT)

    def find_previous(self):
        """Find previous occurrence"""
        editor = self._get_current_editor()
        if not editor:
            return

        search_text = self.search_var.get()
        if not search_text:
            return

        pattern = self._build_pattern(search_text)
        if not pattern:
            return

        # Get content from start to current position
        current_pos = editor.index("insert")
        content = editor.get("1.0", current_pos)

        # Find all matches up to current position
        matches = list(pattern.finditer(content))
        if matches:
            # Get last match
            match = matches[-1]
            start_idx = editor.index(f"1.0+{match.start()}c")
            end_idx = editor.index(f"1.0+{match.end()}c")

            # Select and show
            editor.tag_remove("sel", "1.0", "end")
            editor.tag_add("sel", start_idx, end_idx)
            editor.mark_set("insert", start_idx)
            editor.see(start_idx)

            self.results_label.config(text=f"Found at {start_idx}", fg=T.BILE)
        else:
            # Wrap around to end
            content = editor.get(current_pos, "end-1c")
            matches = list(pattern.finditer(content))
            if matches:
                match = matches[-1]
                start_idx = editor.index(f"{current_pos}+{match.start()}c")
                end_idx = editor.index(f"{current_pos}+{match.end()}c")

                editor.tag_remove("sel", "1.0", "end")
                editor.tag_add("sel", start_idx, end_idx)
                editor.mark_set("insert", start_idx)
                editor.see(start_idx)

                self.results_label.config(text=f"Found at {start_idx} (wrapped)", fg=T.BILE)
            else:
                self.results_label.config(text="No matches found", fg=T.BLOOD_LIGHT)

    def find_all(self):
        """Find all occurrences and highlight them"""
        editor = self._get_current_editor()
        if not editor:
            return

        search_text = self.search_var.get()
        if not search_text:
            return

        pattern = self._build_pattern(search_text)
        if not pattern:
            return

        # Clear previous highlights
        editor.tag_remove("search_highlight", "1.0", "end")

        # Configure highlight tag
        editor.tag_configure("search_highlight", background=T.BILE_DEEP, foreground=T.TEXT)

        # Find all matches
        content = editor.get("1.0", "end-1c")
        matches = list(pattern.finditer(content))

        for match in matches:
            start_idx = editor.index(f"1.0+{match.start()}c")
            end_idx = editor.index(f"1.0+{match.end()}c")
            editor.tag_add("search_highlight", start_idx, end_idx)

        if matches:
            self.results_label.config(text=f"Found {len(matches)} matches", fg=T.BILE)
            # Go to first match
            first_match = matches[0]
            start_idx = editor.index(f"1.0+{first_match.start()}c")
            editor.mark_set("insert", start_idx)
            editor.see(start_idx)
        else:
            self.results_label.config(text="No matches found", fg=T.BLOOD_LIGHT)

    def replace_current(self):
        """Replace current selection"""
        editor = self._get_current_editor()
        if not editor or not self.replace_var:
            return

        try:
            # Check if there's a selection
            sel_start = editor.index("sel.first")
            sel_end = editor.index("sel.last")

            # Replace selected text
            editor.delete(sel_start, sel_end)
            editor.insert(sel_start, self.replace_var.get())

            # Highlight syntax if available
            if hasattr(editor, 'highlight_syntax'):
                editor.highlight_syntax()

            self.results_label.config(text="Replaced", fg=T.BILE)

            # Find next
            self.find_next()

        except tk.TclError:
            self.results_label.config(text="No selection", fg=T.BLOOD_LIGHT)

    def replace_all(self):
        """Replace all occurrences"""
        editor = self._get_current_editor()
        if not editor or not self.replace_var:
            return

        search_text = self.search_var.get()
        replace_text = self.replace_var.get()

        if not search_text:
            return

        pattern = self._build_pattern(search_text)
        if not pattern:
            return

        content = editor.get("1.0", "end-1c")
        new_content = pattern.sub(replace_text, content)

        # Count replacements
        count = len(list(pattern.finditer(content)))

        if count > 0:
            # Replace content
            editor.delete("1.0", "end")
            editor.insert("1.0", new_content)

            # Highlight syntax if available
            if hasattr(editor, 'highlight_syntax'):
                editor.highlight_syntax()

            self.results_label.config(text=f"Replaced {count} occurrences", fg=T.BILE)
        else:
            self.results_label.config(text="No matches found", fg=T.BLOOD_LIGHT)

    def close_dialog(self):
        """Close the search dialog"""
        editor = self._get_current_editor()
        if editor:
            # Clear highlights
            editor.tag_remove("search_highlight", "1.0", "end")

        if self.dialog:
            self.dialog.destroy()
            self.dialog = None
