"""
Multi-File Tab System
"""
import tkinter as tk
from tkinter import ttk
import os
from components import death_theme as T


class FileTabs(ttk.Frame):
    """Tab system for managing multiple open files"""

    def __init__(self, parent, ide_instance):
        super().__init__(parent)
        self.ide = ide_instance
        self.tabs = {}  # filepath -> (tab_id, editor)
        self.current_tab = None
        self.current_editor = None

        # Tab bar
        self.tab_bar = tk.Frame(self, bg=T.BG3, height=T.HEADER_H + 4)
        self.tab_bar.pack(fill=tk.X, side=tk.TOP)
        self.tab_bar.pack_propagate(False)
        tk.Frame(self, bg=T.BORDER2, height=1).pack(fill=tk.X, side=tk.TOP)

        # Editor container
        self.editor_container = tk.Frame(self, bg=T.BG)
        self.editor_container.pack(fill=tk.BOTH, expand=True)

        # New file button
        new_btn = tk.Label(self.tab_bar, text="+", bg=T.BG3, fg=T.MUTED,
                           font=(T.MONO, 13), padx=T.S4, cursor='hand2')
        new_btn.pack(side=tk.RIGHT, fill=tk.Y)
        new_btn.bind('<Button-1>', lambda e: self.new_file())
        new_btn.bind('<Enter>', lambda e: new_btn.config(fg=T.BLOOD_LIGHT))
        new_btn.bind('<Leave>', lambda e: new_btn.config(fg=T.MUTED))

    def new_file(self):
        """Create a new untitled file"""
        # Count existing untitled files
        untitled_count = sum(1 for path in self.tabs.keys() if path.startswith("Untitled"))
        filename = f"Untitled-{untitled_count + 1}"

        self.add_tab(filename, "")

    def add_tab(self, filepath, content=""):
        """Add a new tab"""
        from components.code_editor import EnhancedCodeEditor

        # Don't duplicate tabs
        if filepath in self.tabs:
            self.switch_to_tab(filepath)
            return

        # Create tab button
        tab_frame = tk.Frame(self.tab_bar, bg=T.BG3)
        tab_frame.pack(side=tk.LEFT, fill=tk.Y)
        strip = tk.Frame(tab_frame, bg=T.BG3, height=2)
        strip.pack(fill=tk.X, side=tk.TOP)
        tk.Frame(tab_frame, bg=T.BORDER2, width=1).pack(side=tk.RIGHT, fill=tk.Y)

        # Tab label
        filename = os.path.basename(filepath) if os.path.isabs(filepath) else filepath
        tab_label = tk.Label(tab_frame, text=f"› {filename}", bg=T.BG3, fg=T.MUTED,
                            font=(T.MONO, 9), padx=T.S4, cursor='hand2')
        tab_label.pack(side=tk.LEFT, fill=tk.Y)
        tab_label.bind('<Button-1>', lambda e: self.switch_to_tab(filepath))

        # Close button
        close_btn = tk.Label(tab_frame, text="✕", bg=T.BG3, fg=T.MUTED,
                            font=(T.MONO, 8), padx=T.S2, cursor='hand2')
        close_btn.pack(side=tk.LEFT, fill=tk.Y, padx=(0, T.S2))
        close_btn.bind('<Button-1>', lambda e: self.close_tab(filepath))
        close_btn.bind('<Enter>', lambda e: close_btn.config(fg=T.BLOOD_LIGHT))
        close_btn.bind('<Leave>', lambda e: close_btn.config(fg=T.MUTED))

        # Create editor
        editor = EnhancedCodeEditor(self.editor_container)
        if content:
            editor.insert("1.0", content)
            editor.highlight_syntax()
            editor.update_line_numbers()

        # Detect language from file extension
        if filepath.endswith('.py'):
            editor.set_language('Python')
        elif filepath.endswith(('.js', '.jsx')):
            editor.set_language('JavaScript')

        # Store tab
        self.tabs[filepath] = {
            'frame': tab_frame,
            'label': tab_label,
            'close': close_btn,
            'strip': strip,
            'editor': editor,
            'modified': False
        }

        # Switch to new tab
        self.switch_to_tab(filepath)

    def switch_to_tab(self, filepath):
        """Switch to a different tab"""
        if filepath not in self.tabs:
            return

        # Hide current editor
        if self.current_editor:
            self.current_editor.pack_forget()

        # Update tab appearances
        for path, tab_data in self.tabs.items():
            if path == filepath:
                # Active tab
                tab_data['frame'].config(bg=T.BG)
                tab_data['label'].config(bg=T.BG, fg=T.TEXT)
                tab_data['close'].config(bg=T.BG)
                tab_data['strip'].config(bg=T.BLOOD_LIGHT)
            else:
                # Inactive tab
                tab_data['frame'].config(bg=T.BG3)
                tab_data['label'].config(bg=T.BG3, fg=T.MUTED)
                tab_data['close'].config(bg=T.BG3)
                tab_data['strip'].config(bg=T.BG3)

        # Show new editor
        self.current_tab = filepath
        self.current_editor = self.tabs[filepath]['editor']
        self.current_editor.pack(fill=tk.BOTH, expand=True)

        # Update IDE's current file reference
        if hasattr(self.ide, 'current_file'):
            self.ide.current_file = filepath

    def close_tab(self, filepath):
        """Close a tab"""
        if filepath not in self.tabs:
            return

        tab_data = self.tabs[filepath]

        # Check if modified
        if tab_data['editor'].is_modified:
            from tkinter import messagebox
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                f"Save changes to {os.path.basename(filepath)}?"
            )
            if response is None:  # Cancel
                return
            elif response:  # Yes - save
                if hasattr(self.ide, 'save_file'):
                    self.ide.save_file()

        # Remove tab
        tab_data['frame'].destroy()
        tab_data['editor'].destroy()
        del self.tabs[filepath]

        # Switch to another tab if available
        if self.tabs:
            next_filepath = list(self.tabs.keys())[0]
            self.switch_to_tab(next_filepath)
        else:
            self.current_tab = None
            self.current_editor = None
            if hasattr(self.ide, 'current_file'):
                self.ide.current_file = None

    def mark_modified(self, filepath, modified=True):
        """Mark tab as modified"""
        if filepath in self.tabs:
            self.tabs[filepath]['modified'] = modified
            filename = os.path.basename(filepath) if os.path.isabs(filepath) else filepath
            if modified:
                self.tabs[filepath]["label"].config(text=f"› {filename} ●")
            else:
                self.tabs[filepath]["label"].config(text=f"› {filename}")

    def get_current_content(self):
        """Get content of current tab"""
        if self.current_editor:
            return self.current_editor.get("1.0", tk.END)
        return ""

    def save_current(self):
        """Save current tab"""
        if self.current_tab:
            self.tabs[self.current_tab]['editor'].mark_saved()
            self.mark_modified(self.current_tab, False)
