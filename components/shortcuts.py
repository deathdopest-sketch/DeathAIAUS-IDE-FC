"""
Keyboard Shortcuts Handler
Provides IDE-wide keyboard shortcuts
"""
import tkinter as tk


class ShortcutsHandler:
    """Manages keyboard shortcuts for the IDE"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.shortcuts = {}
        self._setup_shortcuts()

    def _setup_shortcuts(self):
        """Define all keyboard shortcuts"""
        self.shortcuts = {
            '<Control-s>': self.save_file,
            '<Control-S>': self.save_file,
            '<Control-w>': self.close_tab,
            '<Control-W>': self.close_tab,
            '<Control-n>': self.new_file,
            '<Control-N>': self.new_file,
            '<Control-f>': self.find,
            '<Control-F>': self.find,
            '<Control-h>': self.replace,
            '<Control-H>': self.replace,
            '<Control-p>': self.quick_open,
            '<Control-P>': self.quick_open,
            '<Control-Tab>': self.next_tab,
            '<Control-Shift-Tab>': self.previous_tab,
            '<Control-slash>': self.toggle_comment,
            '<Control-d>': self.duplicate_line,
            '<Control-D>': self.duplicate_line,
            '<Control-z>': self.undo,
            '<Control-Z>': self.undo,
            '<Control-y>': self.redo,
            '<Control-Y>': self.redo,
            '<Control-a>': self.select_all,
            '<Control-A>': self.select_all,
        }

    def bind_all(self, widget):
        """Bind all shortcuts to a widget"""
        for key, func in self.shortcuts.items():
            widget.bind(key, lambda e, f=func: self._execute_shortcut(f, e))

    def _execute_shortcut(self, func, event):
        """Execute a shortcut function"""
        try:
            func(event)
            return "break"  # Prevent default behavior
        except Exception as e:
            print(f"Shortcut error: {e}")
            return "break"

    def save_file(self, event=None):
        """Ctrl+S: Save current file"""
        if hasattr(self.ide, 'save_file'):
            self.ide.save_file()
        return "break"

    def close_tab(self, event=None):
        """Ctrl+W: Close current tab"""
        if hasattr(self.ide, 'tabs') and self.ide.tabs.current_tab:
            self.ide.tabs.close_tab(self.ide.tabs.current_tab)
        return "break"

    def new_file(self, event=None):
        """Ctrl+N: Create new file"""
        if hasattr(self.ide, 'tabs'):
            self.ide.tabs.new_file()
        return "break"

    def find(self, event=None):
        """Ctrl+F: Open find dialog"""
        if hasattr(self.ide, 'search_dialog'):
            self.ide.search_dialog.show_find()
        return "break"

    def replace(self, event=None):
        """Ctrl+H: Open find and replace dialog"""
        if hasattr(self.ide, 'search_dialog'):
            self.ide.search_dialog.show_replace()
        return "break"

    def quick_open(self, event=None):
        """Ctrl+P: Quick file open"""
        if hasattr(self.ide, 'show_quick_open'):
            self.ide.show_quick_open()
        return "break"

    def next_tab(self, event=None):
        """Ctrl+Tab: Switch to next tab"""
        if hasattr(self.ide, 'tabs') and self.ide.tabs.tabs:
            tabs_list = list(self.ide.tabs.tabs.keys())
            if self.ide.tabs.current_tab in tabs_list:
                current_idx = tabs_list.index(self.ide.tabs.current_tab)
                next_idx = (current_idx + 1) % len(tabs_list)
                self.ide.tabs.switch_to_tab(tabs_list[next_idx])
        return "break"

    def previous_tab(self, event=None):
        """Ctrl+Shift+Tab: Switch to previous tab"""
        if hasattr(self.ide, 'tabs') and self.ide.tabs.tabs:
            tabs_list = list(self.ide.tabs.tabs.keys())
            if self.ide.tabs.current_tab in tabs_list:
                current_idx = tabs_list.index(self.ide.tabs.current_tab)
                prev_idx = (current_idx - 1) % len(tabs_list)
                self.ide.tabs.switch_to_tab(tabs_list[prev_idx])
        return "break"

    def toggle_comment(self, event=None):
        """Ctrl+/: Toggle line comment"""
        if hasattr(self.ide, 'tabs') and self.ide.tabs.current_editor:
            editor = self.ide.tabs.current_editor
            try:
                # Get selected lines or current line
                if editor.tag_ranges("sel"):
                    start = editor.index("sel.first")
                    end = editor.index("sel.last")
                else:
                    start = editor.index("insert linestart")
                    end = editor.index("insert lineend")

                start_line = int(start.split('.')[0])
                end_line = int(end.split('.')[0])

                # Determine comment character based on language
                lang = editor.current_language if hasattr(editor, 'current_language') else 'Python'
                comment_char = '#' if lang == 'Python' else '//'

                # Check if lines are commented
                first_line = editor.get(f"{start_line}.0", f"{start_line}.end")
                is_commented = first_line.strip().startswith(comment_char)

                # Toggle comments
                for line_num in range(start_line, end_line + 1):
                    line_content = editor.get(f"{line_num}.0", f"{line_num}.end")

                    if is_commented:
                        # Remove comment
                        if line_content.strip().startswith(comment_char):
                            # Find the comment and remove it
                            idx = line_content.find(comment_char)
                            new_content = line_content[:idx] + line_content[idx+len(comment_char):].lstrip()
                            editor.delete(f"{line_num}.0", f"{line_num}.end")
                            editor.insert(f"{line_num}.0", new_content)
                    else:
                        # Add comment
                        # Find first non-whitespace character
                        stripped = line_content.lstrip()
                        if stripped:  # Only comment non-empty lines
                            indent = len(line_content) - len(stripped)
                            new_content = line_content[:indent] + comment_char + ' ' + stripped
                            editor.delete(f"{line_num}.0", f"{line_num}.end")
                            editor.insert(f"{line_num}.0", new_content)

                # Rehighlight
                if hasattr(editor, 'highlight_syntax'):
                    editor.highlight_syntax()

            except Exception as e:
                print(f"Toggle comment error: {e}")
        return "break"

    def duplicate_line(self, event=None):
        """Ctrl+D: Duplicate current line or selection"""
        if hasattr(self.ide, 'tabs') and self.ide.tabs.current_editor:
            editor = self.ide.tabs.current_editor
            try:
                if editor.tag_ranges("sel"):
                    # Duplicate selection
                    content = editor.get("sel.first", "sel.last")
                    editor.insert("sel.last", content)
                else:
                    # Duplicate current line
                    line_num = editor.index("insert").split('.')[0]
                    line_content = editor.get(f"{line_num}.0", f"{line_num}.end")
                    editor.insert(f"{line_num}.end", "\n" + line_content)
            except Exception as e:
                print(f"Duplicate line error: {e}")
        return "break"

    def undo(self, event=None):
        """Ctrl+Z: Undo"""
        if hasattr(self.ide, 'tabs') and self.ide.tabs.current_editor:
            try:
                self.ide.tabs.current_editor.edit_undo()
            except:
                pass
        return "break"

    def redo(self, event=None):
        """Ctrl+Y: Redo"""
        if hasattr(self.ide, 'tabs') and self.ide.tabs.current_editor:
            try:
                self.ide.tabs.current_editor.edit_redo()
            except:
                pass
        return "break"

    def select_all(self, event=None):
        """Ctrl+A: Select all"""
        if hasattr(self.ide, 'tabs') and self.ide.tabs.current_editor:
            editor = self.ide.tabs.current_editor
            editor.tag_add("sel", "1.0", "end-1c")
            editor.mark_set("insert", "1.0")
            editor.see("insert")
        return "break"

    def add_custom_shortcut(self, key_sequence, callback):
        """Add a custom keyboard shortcut"""
        self.shortcuts[key_sequence] = callback
