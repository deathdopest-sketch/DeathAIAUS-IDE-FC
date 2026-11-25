"""
Theme Customization System
Multiple color themes and customization options
"""
import tkinter as tk
from tkinter import ttk, colorchooser
import json
import os


class Theme:
    """Theme definition"""

    def __init__(self, name, colors):
        self.name = name
        self.colors = colors

    def apply_to_widget(self, widget, widget_type):
        """Apply theme colors to a widget"""
        if widget_type == 'editor':
            widget.config(
                bg=self.colors['editor_bg'],
                fg=self.colors['editor_fg'],
                insertbackground=self.colors['cursor']
            )
        elif widget_type == 'sidebar':
            widget.config(
                bg=self.colors['sidebar_bg'],
                fg=self.colors['sidebar_fg']
            )
        elif widget_type == 'header':
            widget.config(
                bg=self.colors['header_bg'],
                fg=self.colors['header_fg']
            )

    def get_syntax_colors(self):
        """Get syntax highlighting colors"""
        return {
            'keyword': self.colors.get('syntax_keyword', '#569CD6'),
            'string': self.colors.get('syntax_string', '#CE9178'),
            'comment': self.colors.get('syntax_comment', '#6A9955'),
            'function': self.colors.get('syntax_function', '#DCDCAA'),
            'class': self.colors.get('syntax_class', '#4EC9B0'),
            'number': self.colors.get('syntax_number', '#B5CEA8'),
            'decorator': self.colors.get('syntax_decorator', '#C586C0'),
        }


class ThemeLibrary:
    """Built-in theme library"""

    @staticmethod
    def get_themes():
        """Get all available themes"""
        return {
            'dark': ThemeLibrary.dark_theme(),
            'death': ThemeLibrary.death_theme(),
            'light': ThemeLibrary.light_theme(),
            'monokai': ThemeLibrary.monokai_theme(),
            'dracula': ThemeLibrary.dracula_theme(),
            'nord': ThemeLibrary.nord_theme(),
            'gruvbox': ThemeLibrary.gruvbox_theme(),
            'solarized_dark': ThemeLibrary.solarized_dark_theme(),
        }

    @staticmethod
    def dark_theme():
        """VS Code Dark+ theme"""
        return Theme('Dark', {
            'editor_bg': '#1e1e1e',
            'editor_fg': '#d4d4d4',
            'sidebar_bg': '#252526',
            'sidebar_fg': '#cccccc',
            'header_bg': '#2d2d2d',
            'header_fg': '#cccccc',
            'cursor': 'white',
            'selection': '#264f78',
            'line_number_bg': '#1e1e1e',
            'line_number_fg': '#858585',
            'syntax_keyword': '#569CD6',
            'syntax_string': '#CE9178',
            'syntax_comment': '#6A9955',
            'syntax_function': '#DCDCAA',
            'syntax_class': '#4EC9B0',
            'syntax_number': '#B5CEA8',
            'syntax_decorator': '#C586C0',
        })

    @staticmethod
    def death_theme():
        """DeathAI Australia — red-black void, aged bone, arterial red (see death_theme.py)"""
        from components import death_theme as T
        return Theme('Death', {
            'editor_bg': T.BG,
            'editor_fg': T.TEXT,
            'sidebar_bg': T.BG2,
            'sidebar_fg': T.TEXT2,
            'header_bg': T.BG3,
            'header_fg': T.TEXT,
            'cursor': T.BLOOD_LIGHT,
            'selection': T.BLOOD,
            'line_number_bg': T.BG,
            'line_number_fg': T.MUTED,
            'syntax_keyword': T.SYNTAX['keyword'],
            'syntax_string': T.SYNTAX['string'],
            'syntax_comment': T.SYNTAX['comment'],
            'syntax_function': T.SYNTAX['function'],
            'syntax_class': T.SYNTAX['class'],
            'syntax_number': T.SYNTAX['number'],
            'syntax_decorator': T.SYNTAX['decorator'],
        })

    @staticmethod
    def light_theme():
        """Light theme"""
        return Theme('Light', {
            'editor_bg': '#ffffff',
            'editor_fg': '#000000',
            'sidebar_bg': '#f3f3f3',
            'sidebar_fg': '#000000',
            'header_bg': '#e0e0e0',
            'header_fg': '#000000',
            'cursor': 'black',
            'selection': '#add6ff',
            'line_number_bg': '#f3f3f3',
            'line_number_fg': '#237893',
            'syntax_keyword': '#0000ff',
            'syntax_string': '#a31515',
            'syntax_comment': '#008000',
            'syntax_function': '#795e26',
            'syntax_class': '#267f99',
            'syntax_number': '#098658',
            'syntax_decorator': '#af00db',
        })

    @staticmethod
    def monokai_theme():
        """Monokai theme"""
        return Theme('Monokai', {
            'editor_bg': '#272822',
            'editor_fg': '#f8f8f2',
            'sidebar_bg': '#1e1f1c',
            'sidebar_fg': '#f8f8f2',
            'header_bg': '#1e1f1c',
            'header_fg': '#f8f8f2',
            'cursor': '#f8f8f2',
            'selection': '#49483e',
            'line_number_bg': '#272822',
            'line_number_fg': '#90908a',
            'syntax_keyword': '#f92672',
            'syntax_string': '#e6db74',
            'syntax_comment': '#75715e',
            'syntax_function': '#a6e22e',
            'syntax_class': '#66d9ef',
            'syntax_number': '#ae81ff',
            'syntax_decorator': '#fd971f',
        })

    @staticmethod
    def dracula_theme():
        """Dracula theme"""
        return Theme('Dracula', {
            'editor_bg': '#282a36',
            'editor_fg': '#f8f8f2',
            'sidebar_bg': '#21222c',
            'sidebar_fg': '#f8f8f2',
            'header_bg': '#21222c',
            'header_fg': '#f8f8f2',
            'cursor': '#f8f8f2',
            'selection': '#44475a',
            'line_number_bg': '#282a36',
            'line_number_fg': '#6272a4',
            'syntax_keyword': '#ff79c6',
            'syntax_string': '#f1fa8c',
            'syntax_comment': '#6272a4',
            'syntax_function': '#50fa7b',
            'syntax_class': '#8be9fd',
            'syntax_number': '#bd93f9',
            'syntax_decorator': '#ffb86c',
        })

    @staticmethod
    def nord_theme():
        """Nord theme"""
        return Theme('Nord', {
            'editor_bg': '#2e3440',
            'editor_fg': '#d8dee9',
            'sidebar_bg': '#3b4252',
            'sidebar_fg': '#d8dee9',
            'header_bg': '#3b4252',
            'header_fg': '#d8dee9',
            'cursor': '#d8dee9',
            'selection': '#434c5e',
            'line_number_bg': '#2e3440',
            'line_number_fg': '#4c566a',
            'syntax_keyword': '#81a1c1',
            'syntax_string': '#a3be8c',
            'syntax_comment': '#616e88',
            'syntax_function': '#88c0d0',
            'syntax_class': '#8fbcbb',
            'syntax_number': '#b48ead',
            'syntax_decorator': '#d08770',
        })

    @staticmethod
    def gruvbox_theme():
        """Gruvbox Dark theme"""
        return Theme('Gruvbox', {
            'editor_bg': '#282828',
            'editor_fg': '#ebdbb2',
            'sidebar_bg': '#3c3836',
            'sidebar_fg': '#ebdbb2',
            'header_bg': '#3c3836',
            'header_fg': '#ebdbb2',
            'cursor': '#ebdbb2',
            'selection': '#504945',
            'line_number_bg': '#282828',
            'line_number_fg': '#665c54',
            'syntax_keyword': '#fb4934',
            'syntax_string': '#b8bb26',
            'syntax_comment': '#928374',
            'syntax_function': '#fabd2f',
            'syntax_class': '#83a598',
            'syntax_number': '#d3869b',
            'syntax_decorator': '#fe8019',
        })

    @staticmethod
    def solarized_dark_theme():
        """Solarized Dark theme"""
        return Theme('Solarized Dark', {
            'editor_bg': '#002b36',
            'editor_fg': '#839496',
            'sidebar_bg': '#073642',
            'sidebar_fg': '#839496',
            'header_bg': '#073642',
            'header_fg': '#839496',
            'cursor': '#839496',
            'selection': '#073642',
            'line_number_bg': '#002b36',
            'line_number_fg': '#586e75',
            'syntax_keyword': '#859900',
            'syntax_string': '#2aa198',
            'syntax_comment': '#586e75',
            'syntax_function': '#b58900',
            'syntax_class': '#268bd2',
            'syntax_number': '#d33682',
            'syntax_decorator': '#cb4b16',
        })


class ThemeManager:
    """Manages theme application and switching"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.themes = ThemeLibrary.get_themes()
        self.current_theme = self.themes['death']
        self.custom_themes = {}

        # Load custom themes
        self.load_custom_themes()

    def load_custom_themes(self):
        """Load custom themes from file"""
        config_file = os.path.join(os.path.expanduser('~'), '.deathaius_themes.json')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    for name, colors in data.items():
                        self.custom_themes[name] = Theme(name, colors)
            except:
                pass

    def save_custom_themes(self):
        """Save custom themes to file"""
        config_file = os.path.join(os.path.expanduser('~'), '.deathaius_themes.json')
        try:
            data = {name: theme.colors for name, theme in self.custom_themes.items()}
            with open(config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save custom themes: {e}")

    def get_all_themes(self):
        """Get all themes (built-in + custom)"""
        all_themes = dict(self.themes)
        all_themes.update(self.custom_themes)
        return all_themes

    def apply_theme(self, theme_name):
        """Apply theme to IDE"""
        all_themes = self.get_all_themes()
        if theme_name not in all_themes:
            return

        theme = all_themes[theme_name]
        self.current_theme = theme

        # Apply to root
        if hasattr(self.ide, 'root'):
            self.ide.root.config(bg=theme.colors['editor_bg'])

        # Apply to editors
        if hasattr(self.ide, 'tabs') and self.ide.tabs:
            for tab_data in self.ide.tabs.tabs.values():
                editor = tab_data['editor']
                self._apply_to_editor(editor, theme)

        # Apply to sidebar panels
        self._apply_to_sidebar(theme)

        # Save preference
        self._save_theme_preference(theme_name)

    def _apply_to_editor(self, editor, theme):
        """Apply theme to code editor"""
        if not editor:
            return

        # Background and foreground
        editor.config(
            bg=theme.colors['editor_bg'],
            fg=theme.colors['editor_fg'],
            insertbackground=theme.colors['cursor']
        )

        # Line numbers
        if hasattr(editor, 'line_numbers'):
            editor.line_numbers.config(
                bg=theme.colors['line_number_bg'],
                fg=theme.colors['line_number_fg']
            )

        # Syntax highlighting
        syntax_colors = theme.get_syntax_colors()
        for tag, color in syntax_colors.items():
            editor.text_widget.tag_configure(tag, foreground=color)

        # Selection
        editor.text_widget.tag_configure("sel", background=theme.colors['selection'])

    def _apply_to_sidebar(self, theme):
        """Apply theme to sidebar panels"""
        # Git panel
        if hasattr(self.ide, 'git_panel'):
            self._update_widget_colors(self.ide.git_panel, theme.colors['sidebar_bg'], theme.colors['sidebar_fg'])

        # AI chat
        if hasattr(self.ide, 'ai_chat'):
            self._update_widget_colors(self.ide.ai_chat, theme.colors['sidebar_bg'], theme.colors['sidebar_fg'])

    def _update_widget_colors(self, widget, bg, fg):
        """Recursively update widget colors"""
        try:
            if isinstance(widget, (tk.Frame, tk.Label, tk.Button)):
                widget.config(bg=bg)
                if isinstance(widget, (tk.Label, tk.Button)):
                    widget.config(fg=fg)

            # Update children
            for child in widget.winfo_children():
                self._update_widget_colors(child, bg, fg)
        except:
            pass

    def _save_theme_preference(self, theme_name):
        """Save theme preference"""
        config_file = os.path.join(os.path.expanduser('~'), '.deathaius_config.json')
        try:
            config = {}
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)

            config['theme'] = theme_name

            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except:
            pass

    def load_theme_preference(self):
        """Load saved theme preference"""
        config_file = os.path.join(os.path.expanduser('~'), '.deathaius_config.json')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    theme_name = config.get('theme', 'death')
                    self.apply_theme(theme_name)
            except:
                pass


class ThemeCustomizerDialog(tk.Toplevel):
    """Dialog for customizing themes"""

    def __init__(self, parent, theme_manager):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.title("Theme Customizer")
        self.geometry("600x700")
        self.configure(bg='#2d2d2d')

        self.custom_colors = dict(self.theme_manager.current_theme.colors)

        self.setup_ui()

    def setup_ui(self):
        """Setup customizer UI"""
        # Header
        header = tk.Frame(self, bg='#1e1e1e', height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="🎨 Theme Customizer", font=('Arial', 12, 'bold'),
                fg='#00ff00', bg='#1e1e1e').pack(pady=15)

        # Theme selector
        select_frame = tk.Frame(self, bg='#2d2d2d')
        select_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(select_frame, text="Base Theme:", bg='#2d2d2d', fg='#cccccc',
                font=('Arial', 10)).pack(side=tk.LEFT, padx=5)

        self.theme_var = tk.StringVar(value=self.theme_manager.current_theme.name)
        theme_combo = ttk.Combobox(
            select_frame,
            textvariable=self.theme_var,
            values=list(self.theme_manager.get_all_themes().keys()),
            state='readonly'
        )
        theme_combo.pack(side=tk.LEFT, padx=5)
        theme_combo.bind('<<ComboboxSelected>>', self.on_theme_select)

        # Color options
        scroll_frame = tk.Frame(self, bg='#2d2d2d')
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        canvas = tk.Canvas(scroll_frame, bg='#2d2d2d', highlightthickness=0)
        scrollbar = tk.Scrollbar(scroll_frame, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2d2d2d')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create color pickers
        self.color_buttons = {}
        color_labels = {
            'editor_bg': 'Editor Background',
            'editor_fg': 'Editor Foreground',
            'sidebar_bg': 'Sidebar Background',
            'sidebar_fg': 'Sidebar Foreground',
            'header_bg': 'Header Background',
            'header_fg': 'Header Foreground',
            'cursor': 'Cursor',
            'selection': 'Selection',
            'syntax_keyword': 'Syntax: Keywords',
            'syntax_string': 'Syntax: Strings',
            'syntax_comment': 'Syntax: Comments',
            'syntax_function': 'Syntax: Functions',
            'syntax_class': 'Syntax: Classes',
            'syntax_number': 'Syntax: Numbers',
        }

        for key, label in color_labels.items():
            color_frame = tk.Frame(scrollable_frame, bg='#2d2d2d')
            color_frame.pack(fill=tk.X, pady=5)

            tk.Label(color_frame, text=label, bg='#2d2d2d', fg='#cccccc',
                    font=('Arial', 9), width=20, anchor='w').pack(side=tk.LEFT, padx=5)

            color = self.custom_colors.get(key, '#000000')
            btn = tk.Button(
                color_frame,
                text=color,
                bg=color,
                fg=self._contrast_color(color),
                command=lambda k=key: self.pick_color(k),
                relief=tk.FLAT,
                width=15
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.color_buttons[key] = btn

        # Buttons
        button_frame = tk.Frame(self, bg='#2d2d2d')
        button_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Button(button_frame, text="Apply", command=self.apply_custom_theme,
                 bg='#00aa00', fg='white', font=('Arial', 10, 'bold'),
                 relief=tk.FLAT, padx=20).pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="Save As...", command=self.save_custom_theme,
                 bg='#0066cc', fg='white', font=('Arial', 10),
                 relief=tk.FLAT, padx=20).pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="Close", command=self.destroy,
                 bg='#3d3d3d', fg='#cccccc', font=('Arial', 10),
                 relief=tk.FLAT, padx=20).pack(side=tk.RIGHT, padx=5)

    def on_theme_select(self, event=None):
        """Handle theme selection"""
        theme_name = self.theme_var.get()
        all_themes = self.theme_manager.get_all_themes()
        if theme_name in all_themes:
            theme = all_themes[theme_name]
            self.custom_colors = dict(theme.colors)

            # Update color buttons
            for key, btn in self.color_buttons.items():
                color = self.custom_colors.get(key, '#000000')
                btn.config(text=color, bg=color, fg=self._contrast_color(color))

    def pick_color(self, color_key):
        """Pick color for a key"""
        current_color = self.custom_colors.get(color_key, '#000000')
        color = colorchooser.askcolor(color=current_color, title=f"Choose {color_key}")

        if color[1]:  # If color was selected
            self.custom_colors[color_key] = color[1]
            self.color_buttons[color_key].config(
                text=color[1],
                bg=color[1],
                fg=self._contrast_color(color[1])
            )

    def _contrast_color(self, hex_color):
        """Get contrasting color for text"""
        # Remove #
        hex_color = hex_color.lstrip('#')
        # Convert to RGB
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # Calculate luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return '#000000' if luminance > 0.5 else '#ffffff'

    def apply_custom_theme(self):
        """Apply custom theme"""
        custom_theme = Theme('Custom', self.custom_colors)
        self.theme_manager.current_theme = custom_theme
        self.theme_manager.apply_theme('custom')

    def save_custom_theme(self):
        """Save custom theme"""
        from tkinter import simpledialog
        name = simpledialog.askstring("Save Theme", "Enter theme name:")
        if name:
            self.theme_manager.custom_themes[name] = Theme(name, self.custom_colors)
            self.theme_manager.save_custom_themes()
            tk.messagebox.showinfo("Success", f"Theme '{name}' saved!")
