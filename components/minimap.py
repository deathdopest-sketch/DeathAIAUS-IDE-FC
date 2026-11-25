"""
Code Minimap
Visual overview of code structure for navigation
"""
import tkinter as tk
from tkinter import Canvas
import re
from components import death_theme as T


class CodeMinimap(tk.Canvas):
    """Minimap widget showing code overview"""

    def __init__(self, parent, editor_widget, **kwargs):
        super().__init__(
            parent,
            width=kwargs.get('width', 120),
            bg=kwargs.get('bg', T.VOID),
            highlightthickness=0,
            **{k: v for k, v in kwargs.items() if k not in ['width', 'bg']}
        )

        self.editor = editor_widget
        self.char_height = 2  # Height of each line in minimap
        self.char_width = 1   # Width of each character
        self.viewport_rect = None

        # Colors
        self.colors = {
            'text': T.HOVER,
            'keyword': T.SYNTAX['keyword'],
            'string': T.SYNTAX['string'],
            'comment': T.SYNTAX['comment'],
            'viewport': '#264f7880',  # Semi-transparent
            'selection': T.BLOOD
        }

        # Bind events
        self.bind('<Button-1>', self.on_click)
        self.bind('<B1-Motion>', self.on_drag)
        self.bind('<MouseWheel>', self.on_scroll)

        # Update minimap periodically
        self.update_minimap()

    def update_minimap(self):
        """Update minimap display"""
        self.delete('all')  # Clear canvas

        try:
            # Get editor content
            content = self.editor.get('1.0', 'end-1c')
            lines = content.split('\n')

            # Draw lines
            for i, line in enumerate(lines):
                y = i * self.char_height
                self._draw_line(y, line)

            # Draw viewport rectangle
            self._draw_viewport()

            # Schedule next update
            self.after(100, self.update_minimap)

        except Exception as e:
            print(f"Minimap update error: {e}")

    def _draw_line(self, y, line):
        """Draw a single line"""
        if not line.strip():
            return

        # Simple syntax highlighting
        x = 0

        # Check for comments
        if '#' in line:
            comment_start = line.index('#')
            # Draw before comment
            if comment_start > 0:
                self._draw_text(x, y, line[:comment_start], self.colors['text'])
                x += len(line[:comment_start]) * self.char_width
            # Draw comment
            self._draw_text(x, y, line[comment_start:], self.colors['comment'])
            return

        # Check for strings
        if '"' in line or "'" in line:
            self._draw_text(x, y, line, self.colors['string'])
            return

        # Check for keywords
        keywords = ['def', 'class', 'import', 'from', 'if', 'for', 'while', 'return']
        found_keyword = False
        for keyword in keywords:
            if line.strip().startswith(keyword + ' '):
                self._draw_text(x, y, line, self.colors['keyword'])
                found_keyword = True
                break

        if not found_keyword:
            self._draw_text(x, y, line, self.colors['text'])

    def _draw_text(self, x, y, text, color):
        """Draw text as a line"""
        if not text.strip():
            return

        # Draw as a simple rectangle representing the line
        width = min(len(text.strip()), 100) * self.char_width

        self.create_rectangle(
            x, y,
            x + width, y + self.char_height,
            fill=color,
            outline=''
        )

    def _draw_viewport(self):
        """Draw viewport rectangle"""
        try:
            # Get visible portion of editor
            first_visible = self.editor.index('@0,0')
            last_visible = self.editor.index('@0,9999')

            first_line = int(first_visible.split('.')[0])
            last_line = int(last_visible.split('.')[0])

            # Calculate viewport rectangle
            y1 = (first_line - 1) * self.char_height
            y2 = last_line * self.char_height

            # Delete old viewport
            if self.viewport_rect:
                self.delete(self.viewport_rect)

            # Draw new viewport
            self.viewport_rect = self.create_rectangle(
                0, y1,
                self.winfo_width(), y2,
                fill=self.colors['viewport'],
                outline=self.colors['selection'],
                width=1
            )

        except Exception as e:
            print(f"Viewport draw error: {e}")

    def on_click(self, event):
        """Handle click on minimap"""
        self._jump_to_position(event.y)

    def on_drag(self, event):
        """Handle drag on minimap"""
        self._jump_to_position(event.y)

    def on_scroll(self, event):
        """Handle mouse wheel"""
        # Scroll editor
        if event.delta > 0:
            self.editor.yview_scroll(-1, 'units')
        else:
            self.editor.yview_scroll(1, 'units')

    def _jump_to_position(self, y):
        """Jump editor to minimap position"""
        try:
            # Calculate line number
            line_num = int(y / self.char_height) + 1

            # Scroll editor to line
            self.editor.see(f"{line_num}.0")
            self.editor.mark_set('insert', f"{line_num}.0")

        except Exception as e:
            print(f"Jump error: {e}")


class EnhancedMinimap(CodeMinimap):
    """Enhanced minimap with additional features"""

    def __init__(self, parent, editor_widget, **kwargs):
        super().__init__(parent, editor_widget, **kwargs)

        self.show_bookmarks = True
        self.show_errors = True
        self.bookmarks = set()  # Set of line numbers
        self.errors = set()  # Set of line numbers

    def add_bookmark(self, line_num):
        """Add bookmark indicator"""
        self.bookmarks.add(line_num)

    def remove_bookmark(self, line_num):
        """Remove bookmark"""
        self.bookmarks.discard(line_num)

    def add_error(self, line_num):
        """Add error indicator"""
        self.errors.add(line_num)

    def clear_errors(self):
        """Clear all errors"""
        self.errors.clear()

    def update_minimap(self):
        """Update minimap with indicators"""
        super().update_minimap()

        # Draw bookmarks
        if self.show_bookmarks:
            for line_num in self.bookmarks:
                y = (line_num - 1) * self.char_height
                self.create_oval(
                    2, y,
                    8, y + self.char_height,
                    fill=T.SIGNAL,
                    outline=''
                )

        # Draw errors
        if self.show_errors:
            for line_num in self.errors:
                y = (line_num - 1) * self.char_height
                self.create_rectangle(
                    0, y,
                    3, y + self.char_height,
                    fill=T.BLOOD_LIGHT,
                    outline=''
                )


class MinimapContainer(tk.Frame):
    """Container for minimap with controls"""

    def __init__(self, parent, editor_widget):
        super().__init__(parent, bg=T.VOID)

        self.editor = editor_widget

        # Minimap
        self.minimap = EnhancedMinimap(self, editor_widget)
        self.minimap.pack(fill=tk.BOTH, expand=True)

        # Controls (optional)
        self.setup_controls()

    def setup_controls(self):
        """Setup minimap controls"""
        # Add zoom controls, toggle options, etc.
        pass


class MinimapManager:
    """Manages minimaps for multiple editors"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.minimaps = {}  # editor -> minimap

    def add_minimap(self, editor, container):
        """Add minimap for editor"""
        if editor in self.minimaps:
            return self.minimaps[editor]

        minimap = MinimapContainer(container, editor)
        self.minimaps[editor] = minimap

        return minimap

    def remove_minimap(self, editor):
        """Remove minimap for editor"""
        if editor in self.minimaps:
            self.minimaps[editor].destroy()
            del self.minimaps[editor]

    def update_all(self):
        """Update all minimaps"""
        for minimap in self.minimaps.values():
            minimap.minimap.update_minimap()
