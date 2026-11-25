"""
Split View Editing
Side-by-side editor panels for comparing and editing multiple files
"""
import tkinter as tk
from tkinter import ttk
from components.code_editor import EnhancedCodeEditor
from components import death_theme as T


class SplitView(tk.Frame):
    """Split view container for multiple editors"""

    def __init__(self, parent, ide_instance):
        super().__init__(parent, bg=T.BG)
        self.ide = ide_instance
        self.split_mode = None  # None, 'vertical', 'horizontal'
        self.editors = []  # List of editor info dicts
        self.paned_window = None

        self.setup_ui()

    def setup_ui(self):
        """Setup initial single editor view"""
        # Single editor container (default)
        self.single_container = tk.Frame(self, bg=T.BG)
        self.single_container.pack(fill=tk.BOTH, expand=True)

    def enable_split(self, mode='vertical'):
        """Enable split view"""
        if self.split_mode == mode:
            return  # Already in this mode

        self.split_mode = mode

        # Clear single container
        for widget in self.single_container.winfo_children():
            widget.pack_forget()

        # Create paned window
        if self.paned_window:
            self.paned_window.destroy()

        orient = tk.VERTICAL if mode == 'horizontal' else tk.HORIZONTAL
        self.paned_window = ttk.PanedWindow(self.single_container, orient=orient)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Create two editor panels
        self._create_split_panels()

    def _create_split_panels(self):
        """Create split editor panels"""
        # Clear existing editors
        self.editors = []

        # Left/Top panel
        left_frame = tk.Frame(self.paned_window, bg=T.BG)
        self.paned_window.add(left_frame, weight=1)

        left_header = tk.Frame(left_frame, bg=T.BG3, height=30)
        left_header.pack(fill=tk.X)
        left_header.pack_propagate(False)

        left_label = tk.Label(left_header, text="Editor 1", bg=T.BG3,
                             fg=T.BILE, font=(T.UI, 9, 'bold'))
        left_label.pack(side=tk.LEFT, padx=10, pady=5)

        left_editor = EnhancedCodeEditor(left_frame)
        left_editor.pack(fill=tk.BOTH, expand=True)

        self.editors.append({
            'frame': left_frame,
            'header': left_header,
            'label': left_label,
            'editor': left_editor,
            'file': None
        })

        # Right/Bottom panel
        right_frame = tk.Frame(self.paned_window, bg=T.BG)
        self.paned_window.add(right_frame, weight=1)

        right_header = tk.Frame(right_frame, bg=T.BG3, height=30)
        right_header.pack(fill=tk.X)
        right_header.pack_propagate(False)

        right_label = tk.Label(right_header, text="Editor 2", bg=T.BG3,
                              fg=T.BILE, font=(T.UI, 9, 'bold'))
        right_label.pack(side=tk.LEFT, padx=10, pady=5)

        right_editor = EnhancedCodeEditor(right_frame)
        right_editor.pack(fill=tk.BOTH, expand=True)

        self.editors.append({
            'frame': right_frame,
            'header': right_header,
            'label': right_label,
            'editor': right_editor,
            'file': None
        })

        # Copy content from main editor if available
        if hasattr(self.ide, 'tabs') and self.ide.tabs.current_editor:
            content = self.ide.tabs.current_editor.get('1.0', 'end-1c')
            left_editor.insert('1.0', content)
            left_editor.highlight_syntax()

    def disable_split(self):
        """Disable split view and return to single editor"""
        self.split_mode = None

        if self.paned_window:
            self.paned_window.destroy()
            self.paned_window = None

        self.editors = []

    def load_file_in_panel(self, panel_index, file_path, content):
        """Load file into specific panel"""
        if panel_index >= len(self.editors):
            return

        editor_info = self.editors[panel_index]
        editor = editor_info['editor']

        # Clear and insert content
        editor.delete('1.0', 'end')
        editor.insert('1.0', content)

        # Detect and set language
        if file_path.endswith('.py'):
            editor.set_language('Python')
        elif file_path.endswith(('.js', '.jsx')):
            editor.set_language('JavaScript')

        editor.highlight_syntax()
        editor.update_line_numbers()

        # Update header
        import os
        editor_info['file'] = file_path
        editor_info['label'].config(text=os.path.basename(file_path))

    def get_panel_count(self):
        """Get number of editor panels"""
        return len(self.editors)

    def get_panel_editor(self, panel_index):
        """Get editor widget for panel"""
        if panel_index < len(self.editors):
            return self.editors[panel_index]['editor']
        return None

    def sync_scroll(self, enable=True):
        """Enable/disable synchronized scrolling"""
        if not enable or len(self.editors) < 2:
            return

        def on_scroll(*args):
            # Sync all editors to same position
            for editor_info in self.editors:
                editor_info['editor'].yview_moveto(args[0])

        # Bind scrolling
        for editor_info in self.editors:
            editor = editor_info['editor']
            scrollbar = editor.master.winfo_children()[-1]  # Get scrollbar
            if isinstance(scrollbar, tk.Scrollbar):
                scrollbar.config(command=on_scroll)


class SplitViewManager:
    """Manages split view functionality"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.split_view = None
        self.is_split = False

    def toggle_vertical_split(self):
        """Toggle vertical split (side-by-side)"""
        if self.is_split and self.split_view and self.split_view.split_mode == 'vertical':
            self.close_split()
        else:
            self.open_split('vertical')

    def toggle_horizontal_split(self):
        """Toggle horizontal split (top-bottom)"""
        if self.is_split and self.split_view and self.split_view.split_mode == 'horizontal':
            self.close_split()
        else:
            self.open_split('horizontal')

    def open_split(self, mode='vertical'):
        """Open split view"""
        if not hasattr(self.ide, 'tabs'):
            return

        # Get current tab container
        tab_container = self.ide.tabs

        # Hide current editor
        if tab_container.current_editor:
            tab_container.current_editor.pack_forget()

        # Create split view if not exists
        if not self.split_view:
            self.split_view = SplitView(tab_container.editor_container, self.ide)

        self.split_view.enable_split(mode)
        self.split_view.pack(fill=tk.BOTH, expand=True)
        self.is_split = True

        # Load current file into left panel
        if tab_container.current_tab:
            current_file = tab_container.current_tab
            content = tab_container.current_editor.get('1.0', 'end-1c') if tab_container.current_editor else ""
            self.split_view.load_file_in_panel(0, current_file, content)

    def close_split(self):
        """Close split view"""
        if not self.split_view:
            return

        self.split_view.disable_split()
        self.split_view.pack_forget()
        self.is_split = False

        # Restore main editor
        if hasattr(self.ide, 'tabs') and self.ide.tabs.current_editor:
            self.ide.tabs.current_editor.pack(fill=tk.BOTH, expand=True)

    def compare_files(self, file1_path, file2_path):
        """Open two files in split view for comparison"""
        self.open_split('vertical')

        # Load files
        try:
            with open(file1_path, 'r', encoding='utf-8') as f:
                content1 = f.read()
            with open(file2_path, 'r', encoding='utf-8') as f:
                content2 = f.read()

            self.split_view.load_file_in_panel(0, file1_path, content1)
            self.split_view.load_file_in_panel(1, file2_path, content2)

            # Enable sync scroll for comparison
            self.split_view.sync_scroll(True)

        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Failed to load files: {e}")

    def load_file_in_panel(self, panel_index, file_path):
        """Load file into specific panel"""
        if not self.is_split or not self.split_view:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.split_view.load_file_in_panel(panel_index, file_path, content)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def get_active_editors(self):
        """Get list of active editor widgets"""
        if self.is_split and self.split_view:
            return [e['editor'] for e in self.split_view.editors]
        elif hasattr(self.ide, 'tabs') and self.ide.tabs.current_editor:
            return [self.ide.tabs.current_editor]
        return []


class SplitViewToolbar(tk.Frame):
    """Toolbar for split view controls"""

    def __init__(self, parent, split_manager):
        super().__init__(parent, bg=T.BG3)
        self.split_manager = split_manager

        tk.Label(self, text="View:", bg=T.BG3, fg=T.TEXT,
                font=(T.UI, 9)).pack(side=tk.LEFT, padx=10)

        # Split buttons
        tk.Button(self, text="⬌ Split Vertical",
                 command=self.split_manager.toggle_vertical_split,
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT,
                 font=(T.UI, 9), padx=10).pack(side=tk.LEFT, padx=2)

        tk.Button(self, text="⬍ Split Horizontal",
                 command=self.split_manager.toggle_horizontal_split,
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT,
                 font=(T.UI, 9), padx=10).pack(side=tk.LEFT, padx=2)

        tk.Button(self, text="✕ Close Split",
                 command=self.split_manager.close_split,
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT,
                 font=(T.UI, 9), padx=10).pack(side=tk.LEFT, padx=2)

        # Sync scroll toggle
        self.sync_var = tk.BooleanVar(value=False)
        tk.Checkbutton(self, text="Sync Scroll",
                      variable=self.sync_var,
                      command=self.toggle_sync,
                      bg=T.BG3, fg=T.TEXT, selectcolor=T.BG,
                      activebackground=T.BG3,
                      font=(T.UI, 9)).pack(side=tk.LEFT, padx=10)

    def toggle_sync(self):
        """Toggle synchronized scrolling"""
        if self.split_manager.split_view:
            self.split_manager.split_view.sync_scroll(self.sync_var.get())
