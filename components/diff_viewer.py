"""
Multi-File Diff Viewer
Side-by-side diff viewer for comparing file versions
"""
import tkinter as tk
from tkinter import ttk
import difflib
import os
from components import death_theme as T


class DiffViewer(tk.Toplevel):
    """Side-by-side diff viewer window"""

    def __init__(self, parent, file_path, old_content, new_content, title="Diff Viewer"):
        super().__init__(parent)
        self.title(title)
        self.geometry("1200x700")
        self.configure(bg=T.BG)

        self.file_path = file_path
        self.old_content = old_content
        self.new_content = new_content

        self.setup_ui()
        self.show_diff()

    def setup_ui(self):
        """Setup the diff viewer UI"""
        # Header
        header = tk.Frame(self, bg=T.BG3, height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text=f"📊 {os.path.basename(self.file_path)}",
                font=(T.UI, 11, 'bold'), fg=T.BILE, bg=T.BG3).pack(
                    side=tk.LEFT, padx=10, pady=10)

        # View mode buttons
        self.view_mode = tk.StringVar(value="side-by-side")

        tk.Radiobutton(header, text="Side by Side", variable=self.view_mode,
                      value="side-by-side", command=self.show_diff,
                      bg=T.BG3, fg=T.TEXT, selectcolor=T.BG,
                      activebackground=T.BG3).pack(side=tk.RIGHT, padx=5)

        tk.Radiobutton(header, text="Unified", variable=self.view_mode,
                      value="unified", command=self.show_diff,
                      bg=T.BG3, fg=T.TEXT, selectcolor=T.BG,
                      activebackground=T.BG3).pack(side=tk.RIGHT, padx=5)

        # Main container
        self.main_frame = tk.Frame(self, bg=T.BG)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def show_diff(self):
        """Display diff based on selected mode"""
        # Clear previous content
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        if self.view_mode.get() == "side-by-side":
            self._show_side_by_side()
        else:
            self._show_unified()

    def _show_side_by_side(self):
        """Show side-by-side diff"""
        # Create paned window
        paned = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left side (old)
        left_frame = tk.Frame(paned, bg=T.BG)
        paned.add(left_frame, weight=1)

        tk.Label(left_frame, text="Original", bg=T.BG3, fg=T.BLOOD_LIGHT,
                font=(T.UI, 10, 'bold')).pack(fill=tk.X)

        left_text_frame = tk.Frame(left_frame)
        left_text_frame.pack(fill=tk.BOTH, expand=True)

        left_line_numbers = tk.Text(left_text_frame, width=4, bg=T.BG3,
                                    fg=T.TEXT2, font=(T.MONO, 9),
                                    state='disabled', relief=tk.FLAT)
        left_line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        left_text = tk.Text(left_text_frame, bg=T.BG, fg=T.TEXT,
                           font=(T.MONO, 9), wrap=tk.NONE, state='disabled')
        left_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        left_scroll = tk.Scrollbar(left_text_frame, command=left_text.yview)
        left_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        left_text.config(yscrollcommand=left_scroll.set)

        # Right side (new)
        right_frame = tk.Frame(paned, bg=T.BG)
        paned.add(right_frame, weight=1)

        tk.Label(right_frame, text="Modified", bg=T.BG3, fg=T.BILE,
                font=(T.UI, 10, 'bold')).pack(fill=tk.X)

        right_text_frame = tk.Frame(right_frame)
        right_text_frame.pack(fill=tk.BOTH, expand=True)

        right_line_numbers = tk.Text(right_text_frame, width=4, bg=T.BG3,
                                     fg=T.TEXT2, font=(T.MONO, 9),
                                     state='disabled', relief=tk.FLAT)
        right_line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        right_text = tk.Text(right_text_frame, bg=T.BG, fg=T.TEXT,
                            font=(T.MONO, 9), wrap=tk.NONE, state='disabled')
        right_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_scroll = tk.Scrollbar(right_text_frame, command=right_text.yview)
        right_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        right_text.config(yscrollcommand=right_scroll.set)

        # Configure tags
        left_text.tag_configure("removed", background=T.BLOOD_DEEP, foreground=T.BLOOD_LIGHT)
        left_text.tag_configure("unchanged", background=T.BG)
        right_text.tag_configure("added", background=T.BILE_DEEP, foreground=T.BILE)
        right_text.tag_configure("unchanged", background=T.BG)

        # Generate diff
        old_lines = self.old_content.split('\n')
        new_lines = self.new_content.split('\n')

        differ = difflib.Differ()
        diff = list(differ.compare(old_lines, new_lines))

        # Process diff
        left_text.config(state='normal')
        right_text.config(state='normal')
        left_line_numbers.config(state='normal')
        right_line_numbers.config(state='normal')

        left_line = 1
        right_line = 1

        for line in diff:
            if line.startswith('  '):  # Unchanged
                content = line[2:]
                left_line_numbers.insert(tk.END, f"{left_line}\n")
                left_text.insert(tk.END, content + '\n', "unchanged")
                right_line_numbers.insert(tk.END, f"{right_line}\n")
                right_text.insert(tk.END, content + '\n', "unchanged")
                left_line += 1
                right_line += 1

            elif line.startswith('- '):  # Removed from old
                content = line[2:]
                left_line_numbers.insert(tk.END, f"{left_line}\n")
                left_text.insert(tk.END, content + '\n', "removed")
                right_line_numbers.insert(tk.END, "\n")
                right_text.insert(tk.END, "\n")
                left_line += 1

            elif line.startswith('+ '):  # Added to new
                content = line[2:]
                left_line_numbers.insert(tk.END, "\n")
                left_text.insert(tk.END, "\n")
                right_line_numbers.insert(tk.END, f"{right_line}\n")
                right_text.insert(tk.END, content + '\n', "added")
                right_line += 1

            elif line.startswith('? '):  # Diff hints (ignore)
                pass

        left_text.config(state='disabled')
        right_text.config(state='disabled')
        left_line_numbers.config(state='disabled')
        right_line_numbers.config(state='disabled')

        # Sync scrolling
        def sync_scroll(*args):
            left_text.yview_moveto(args[0])
            right_text.yview_moveto(args[0])

        left_scroll.config(command=lambda *args: sync_scroll(*args))
        right_scroll.config(command=lambda *args: sync_scroll(*args))

    def _show_unified(self):
        """Show unified diff"""
        text_frame = tk.Frame(self.main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Line numbers
        line_numbers = tk.Text(text_frame, width=4, bg=T.BG3, fg=T.TEXT2,
                              font=(T.MONO, 9), state='disabled', relief=tk.FLAT)
        line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Text widget
        text = tk.Text(text_frame, bg=T.BG, fg=T.TEXT,
                      font=(T.MONO, 9), wrap=tk.NONE)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = tk.Scrollbar(text_frame, command=text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scrollbar.set)

        # Configure tags
        text.tag_configure("header", foreground=T.SIGNAL, font=(T.MONO, 9, 'bold'))
        text.tag_configure("added", background=T.BILE_DEEP, foreground=T.BILE)
        text.tag_configure("removed", background=T.BLOOD_DEEP, foreground=T.BLOOD_LIGHT)
        text.tag_configure("context", foreground=T.TEXT)

        # Generate unified diff
        old_lines = self.old_content.split('\n')
        new_lines = self.new_content.split('\n')

        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile='Original',
            tofile='Modified',
            lineterm=''
        )

        line_num = 1
        line_numbers.config(state='normal')

        for line in diff:
            if line.startswith('---') or line.startswith('+++'):
                text.insert(tk.END, line + '\n', "header")
            elif line.startswith('@@'):
                text.insert(tk.END, line + '\n', "header")
            elif line.startswith('+'):
                text.insert(tk.END, line + '\n', "added")
            elif line.startswith('-'):
                text.insert(tk.END, line + '\n', "removed")
            else:
                text.insert(tk.END, line + '\n', "context")

            line_numbers.insert(tk.END, f"{line_num}\n")
            line_num += 1

        line_numbers.config(state='disabled')


class MultiFileDiffManager:
    """Manages multiple diff viewers for different file comparisons"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.open_diffs = {}

    def show_file_diff(self, file_path, old_content, new_content):
        """Show diff for a file"""
        # Close existing diff for this file
        if file_path in self.open_diffs:
            try:
                self.open_diffs[file_path].destroy()
            except:
                pass

        # Create new diff viewer
        viewer = DiffViewer(
            self.ide.root,
            file_path,
            old_content,
            new_content,
            title=f"Diff: {os.path.basename(file_path)}"
        )

        self.open_diffs[file_path] = viewer

        # Clean up when closed
        def on_close():
            if file_path in self.open_diffs:
                del self.open_diffs[file_path]
            viewer.destroy()

        viewer.protocol("WM_DELETE_WINDOW", on_close)

        return viewer

    def show_unsaved_changes(self, file_path, saved_content, current_content):
        """Show diff between saved and current version"""
        return self.show_file_diff(
            file_path,
            saved_content,
            current_content
        )

    def show_git_diff(self, file_path, git_version, current_version):
        """Show diff between git version and current version"""
        return self.show_file_diff(
            file_path,
            git_version,
            current_version
        )

    def compare_files(self, file_path_1, file_path_2):
        """Compare two different files"""
        try:
            with open(file_path_1, 'r', encoding='utf-8') as f:
                content_1 = f.read()

            with open(file_path_2, 'r', encoding='utf-8') as f:
                content_2 = f.read()

            viewer = DiffViewer(
                self.ide.root,
                f"{os.path.basename(file_path_1)} ↔ {os.path.basename(file_path_2)}",
                content_1,
                content_2,
                title="File Comparison"
            )

            return viewer

        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Failed to compare files: {e}")
            return None

    def close_all_diffs(self):
        """Close all open diff viewers"""
        for viewer in list(self.open_diffs.values()):
            try:
                viewer.destroy()
            except:
                pass
        self.open_diffs.clear()
