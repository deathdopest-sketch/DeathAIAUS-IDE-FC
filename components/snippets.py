"""
Code Snippets Manager
Create and use code snippets with tab completion
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from components import death_theme as T


class Snippet:
    """Single code snippet"""

    def __init__(self, name, prefix, body, description="", language=""):
        self.name = name
        self.prefix = prefix
        self.body = body
        self.description = description
        self.language = language

    def expand(self, **kwargs):
        """Expand snippet with placeholders"""
        expanded = self.body
        for key, value in kwargs.items():
            expanded = expanded.replace(f"${{{key}}}", value)
        return expanded

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'name': self.name,
            'prefix': self.prefix,
            'body': self.body,
            'description': self.description,
            'language': self.language
        }

    @staticmethod
    def from_dict(data):
        """Create from dictionary"""
        return Snippet(
            data['name'],
            data['prefix'],
            data['body'],
            data.get('description', ''),
            data.get('language', '')
        )


class SnippetLibrary:
    """Built-in snippet library"""

    @staticmethod
    def get_python_snippets():
        """Get Python snippets"""
        return [
            Snippet(
                name="Function",
                prefix="def",
                body='''def ${function_name}(${params}):
    """${description}"""
    ${body}
    return ${return_value}''',
                description="Function definition",
                language="Python"
            ),
            Snippet(
                name="Class",
                prefix="class",
                body='''class ${class_name}:
    """${description}"""

    def __init__(self, ${params}):
        ${init_body}

    def ${method_name}(self):
        """${method_description}"""
        ${method_body}''',
                description="Class definition",
                language="Python"
            ),
            Snippet(
                name="If Main",
                prefix="ifmain",
                body='''if __name__ == "__main__":
    ${body}''',
                description="If main block",
                language="Python"
            ),
            Snippet(
                name="Try Except",
                prefix="try",
                body='''try:
    ${code}
except ${exception} as e:
    ${handler}''',
                description="Try except block",
                language="Python"
            ),
            Snippet(
                name="For Loop",
                prefix="for",
                body='''for ${item} in ${iterable}:
    ${body}''',
                description="For loop",
                language="Python"
            ),
            Snippet(
                name="List Comprehension",
                prefix="lc",
                body='''[${expression} for ${item} in ${iterable} if ${condition}]''',
                description="List comprehension",
                language="Python"
            ),
            Snippet(
                name="Dict Comprehension",
                prefix="dc",
                body='''{${key}: ${value} for ${item} in ${iterable}}''',
                description="Dictionary comprehension",
                language="Python"
            ),
        ]

    @staticmethod
    def get_javascript_snippets():
        """Get JavaScript snippets"""
        return [
            Snippet(
                name="Function",
                prefix="func",
                body='''function ${function_name}(${params}) {
    ${body}
    return ${return_value};
}''',
                description="Function declaration",
                language="JavaScript"
            ),
            Snippet(
                name="Arrow Function",
                prefix="arrow",
                body='''const ${name} = (${params}) => {
    ${body}
};''',
                description="Arrow function",
                language="JavaScript"
            ),
            Snippet(
                name="Class",
                prefix="class",
                body='''class ${class_name} {
    constructor(${params}) {
        ${constructor_body}
    }

    ${method_name}() {
        ${method_body}
    }
}''',
                description="Class definition",
                language="JavaScript"
            ),
            Snippet(
                name="For Loop",
                prefix="for",
                body='''for (let ${i} = 0; ${i} < ${length}; ${i}++) {
    ${body}
}''',
                description="For loop",
                language="JavaScript"
            ),
            Snippet(
                name="For Each",
                prefix="foreach",
                body='''${array}.forEach((${item}) => {
    ${body}
});''',
                description="ForEach loop",
                language="JavaScript"
            ),
            Snippet(
                name="Promise",
                prefix="promise",
                body='''new Promise((resolve, reject) => {
    ${body}
});''',
                description="Promise",
                language="JavaScript"
            ),
            Snippet(
                name="Async Function",
                prefix="async",
                body='''async function ${name}(${params}) {
    try {
        ${body}
    } catch (error) {
        ${error_handler}
    }
}''',
                description="Async function",
                language="JavaScript"
            ),
        ]


class SnippetManager:
    """Manages code snippets"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.snippets = {}  # language -> {prefix -> Snippet}
        self.custom_snippets = {}

        self._load_builtin_snippets()
        self._load_custom_snippets()

    def _load_builtin_snippets(self):
        """Load built-in snippets"""
        # Python
        self.snippets['Python'] = {}
        for snippet in SnippetLibrary.get_python_snippets():
            self.snippets['Python'][snippet.prefix] = snippet

        # JavaScript
        self.snippets['JavaScript'] = {}
        for snippet in SnippetLibrary.get_javascript_snippets():
            self.snippets['JavaScript'][snippet.prefix] = snippet

    def _load_custom_snippets(self):
        """Load custom snippets from file"""
        config_file = os.path.join(os.path.expanduser('~'), '.deathaius_snippets.json')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    for lang, snippets in data.items():
                        if lang not in self.custom_snippets:
                            self.custom_snippets[lang] = {}
                        for prefix, snippet_data in snippets.items():
                            self.custom_snippets[lang][prefix] = Snippet.from_dict(snippet_data)
            except Exception as e:
                print(f"Failed to load custom snippets: {e}")

    def save_custom_snippets(self):
        """Save custom snippets to file"""
        config_file = os.path.join(os.path.expanduser('~'), '.deathaius_snippets.json')
        try:
            data = {}
            for lang, snippets in self.custom_snippets.items():
                data[lang] = {prefix: snippet.to_dict() for prefix, snippet in snippets.items()}

            with open(config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save custom snippets: {e}")

    def get_snippets_for_language(self, language):
        """Get all snippets for a language"""
        snippets = {}

        # Built-in
        if language in self.snippets:
            snippets.update(self.snippets[language])

        # Custom
        if language in self.custom_snippets:
            snippets.update(self.custom_snippets[language])

        return snippets

    def find_snippet(self, prefix, language):
        """Find snippet by prefix"""
        snippets = self.get_snippets_for_language(language)
        return snippets.get(prefix)

    def add_custom_snippet(self, snippet):
        """Add custom snippet"""
        if snippet.language not in self.custom_snippets:
            self.custom_snippets[snippet.language] = {}

        self.custom_snippets[snippet.language][snippet.prefix] = snippet
        self.save_custom_snippets()

    def delete_custom_snippet(self, prefix, language):
        """Delete custom snippet"""
        if language in self.custom_snippets and prefix in self.custom_snippets[language]:
            del self.custom_snippets[language][prefix]
            self.save_custom_snippets()

    def setup_editor(self, editor, language="Python"):
        """Setup snippet expansion on editor"""
        editor.bind('<Tab>', lambda e: self._try_expand_snippet(editor, language))

    def _try_expand_snippet(self, editor, language):
        """Try to expand snippet at cursor"""
        try:
            # Get word before cursor
            cursor_pos = editor.index('insert')
            line_start = editor.index('insert linestart')
            line_content = editor.get(line_start, cursor_pos)

            # Find last word
            words = line_content.split()
            if not words:
                return None

            prefix = words[-1]

            # Find snippet
            snippet = self.find_snippet(prefix, language)
            if snippet:
                # Remove prefix
                start_pos = editor.index(f'insert - {len(prefix)}c')
                editor.delete(start_pos, cursor_pos)

                # Insert snippet
                self._insert_snippet(editor, snippet)
                return "break"  # Prevent default Tab behavior

        except Exception as e:
            print(f"Snippet expansion error: {e}")

        return None

    def _insert_snippet(self, editor, snippet):
        """Insert snippet with placeholder support"""
        # Get placeholders
        import re
        placeholders = re.findall(r'\$\{([^}]+)\}', snippet.body)

        if not placeholders:
            # No placeholders, just insert
            editor.insert('insert', snippet.body)
            return

        # Show placeholder dialog
        self._show_placeholder_dialog(editor, snippet, placeholders)

    def _show_placeholder_dialog(self, editor, snippet, placeholders):
        """Show dialog for placeholder values"""
        dialog = tk.Toplevel(self.ide.root if hasattr(self.ide, 'root') else None)
        dialog.title(f"Snippet: {snippet.name}")
        dialog.geometry("400x400")
        dialog.configure(bg=T.BG3)

        tk.Label(dialog, text=f"Fill in snippet placeholders:",
                bg=T.BG3, fg=T.TEXT, font=(T.UI, 11, 'bold')).pack(pady=10)

        # Placeholder inputs
        entries = {}
        for placeholder in placeholders:
            frame = tk.Frame(dialog, bg=T.BG3)
            frame.pack(fill=tk.X, padx=20, pady=5)

            tk.Label(frame, text=f"{placeholder}:", bg=T.BG3, fg=T.TEXT,
                    font=(T.UI, 9), width=15, anchor='w').pack(side=tk.LEFT)

            entry = tk.Entry(frame, font=(T.UI, 9), bg=T.BG, fg=T.TEXT)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            entries[placeholder] = entry

        # Focus first entry
        if entries:
            list(entries.values())[0].focus()

        def insert_snippet():
            """Insert snippet with values"""
            values = {key: entry.get() for key, entry in entries.items()}
            expanded = snippet.expand(**values)
            editor.insert('insert', expanded)

            # Highlight syntax if available
            if hasattr(editor, 'highlight_syntax'):
                editor.highlight_syntax()

            dialog.destroy()

        # Buttons
        button_frame = tk.Frame(dialog, bg=T.BG3)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Insert", command=insert_snippet,
                 bg=T.BLOOD, fg=T.TEXT, font=(T.UI, 10, 'bold'),
                 relief=tk.FLAT, padx=20).pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                 bg=T.HOVER, fg=T.TEXT, font=(T.UI, 10),
                 relief=tk.FLAT, padx=20).pack(side=tk.LEFT, padx=5)

        # Bind Enter to insert
        dialog.bind('<Return>', lambda e: insert_snippet())


class SnippetManagerDialog(tk.Toplevel):
    """Dialog for managing snippets"""

    def __init__(self, parent, snippet_manager):
        super().__init__(parent)
        self.snippet_manager = snippet_manager
        self.title("Snippet Manager")
        self.geometry("800x600")
        self.configure(bg=T.BG3)

        self.setup_ui()

    def setup_ui(self):
        """Setup manager UI"""
        # Header
        header = tk.Frame(self, bg=T.BG, height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="📝 Snippet Manager", font=(T.UI, 12, 'bold'),
                fg=T.BILE, bg=T.BG).pack(pady=15)

        # Main container
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left: Snippet list
        left_frame = tk.Frame(main_paned, bg=T.BG3)
        main_paned.add(left_frame, weight=1)

        tk.Label(left_frame, text="Snippets:", bg=T.BG3, fg=T.TEXT,
                font=(T.UI, 10, 'bold')).pack(anchor='w', padx=5, pady=5)

        # Language filter
        lang_frame = tk.Frame(left_frame, bg=T.BG3)
        lang_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(lang_frame, text="Language:", bg=T.BG3, fg=T.TEXT).pack(side=tk.LEFT)

        self.lang_var = tk.StringVar(value="Python")
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var,
                                  values=["Python", "JavaScript"],
                                  state='readonly', width=15)
        lang_combo.pack(side=tk.LEFT, padx=5)
        lang_combo.bind('<<ComboboxSelected>>', self.on_language_change)

        # Snippet list
        list_frame = tk.Frame(left_frame, bg=T.BG)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.snippet_list = tk.Listbox(
            list_frame,
            bg=T.BG,
            fg=T.TEXT,
            font=(T.MONO, 9),
            selectbackground=T.HOVER,
            yscrollcommand=scrollbar.set
        )
        self.snippet_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.snippet_list.yview)

        self.snippet_list.bind('<<ListboxSelect>>', self.on_snippet_select)

        # Buttons
        btn_frame = tk.Frame(left_frame, bg=T.BG3)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(btn_frame, text="+ New", command=self.new_snippet,
                 bg=T.BLOOD, fg=T.TEXT, relief=tk.FLAT).pack(side=tk.LEFT, padx=2)

        tk.Button(btn_frame, text="✕ Delete", command=self.delete_snippet,
                 bg=T.BLOOD, fg=T.TEXT, relief=tk.FLAT).pack(side=tk.LEFT, padx=2)

        # Right: Snippet details
        right_frame = tk.Frame(main_paned, bg=T.BG3)
        main_paned.add(right_frame, weight=2)

        tk.Label(right_frame, text="Snippet Details:", bg=T.BG3, fg=T.TEXT,
                font=(T.UI, 10, 'bold')).pack(anchor='w', padx=5, pady=5)

        # Details form
        details_frame = tk.Frame(right_frame, bg=T.BG3)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Name
        tk.Label(details_frame, text="Name:", bg=T.BG3, fg=T.TEXT).pack(anchor='w', pady=2)
        self.name_var = tk.StringVar()
        tk.Entry(details_frame, textvariable=self.name_var, bg=T.BG,
                fg=T.TEXT).pack(fill=tk.X, pady=2)

        # Prefix
        tk.Label(details_frame, text="Prefix:", bg=T.BG3, fg=T.TEXT).pack(anchor='w', pady=2)
        self.prefix_var = tk.StringVar()
        tk.Entry(details_frame, textvariable=self.prefix_var, bg=T.BG,
                fg=T.TEXT).pack(fill=tk.X, pady=2)

        # Description
        tk.Label(details_frame, text="Description:", bg=T.BG3, fg=T.TEXT).pack(anchor='w', pady=2)
        self.desc_var = tk.StringVar()
        tk.Entry(details_frame, textvariable=self.desc_var, bg=T.BG,
                fg=T.TEXT).pack(fill=tk.X, pady=2)

        # Body
        tk.Label(details_frame, text="Body:", bg=T.BG3, fg=T.TEXT).pack(anchor='w', pady=2)
        self.body_text = tk.Text(details_frame, height=15, bg=T.BG,
                                fg=T.TEXT, font=(T.MONO, 9), wrap=tk.NONE)
        self.body_text.pack(fill=tk.BOTH, expand=True, pady=2)

        # Save button
        tk.Button(details_frame, text="Save Snippet", command=self.save_snippet,
                 bg=T.HOVER, fg=T.TEXT, font=(T.UI, 10, 'bold'),
                 relief=tk.FLAT, padx=20, pady=5).pack(pady=10)

        # Load initial snippets
        self.load_snippets()

    def load_snippets(self):
        """Load snippets for current language"""
        self.snippet_list.delete(0, tk.END)
        language = self.lang_var.get()
        snippets = self.snippet_manager.get_snippets_for_language(language)

        for prefix, snippet in snippets.items():
            display = f"{prefix} - {snippet.name}"
            self.snippet_list.insert(tk.END, display)

    def on_language_change(self, event=None):
        """Handle language change"""
        self.load_snippets()

    def on_snippet_select(self, event=None):
        """Handle snippet selection"""
        selection = self.snippet_list.curselection()
        if not selection:
            return

        # Get snippet
        language = self.lang_var.get()
        snippets = self.snippet_manager.get_snippets_for_language(language)
        prefix = list(snippets.keys())[selection[0]]
        snippet = snippets[prefix]

        # Load into form
        self.name_var.set(snippet.name)
        self.prefix_var.set(snippet.prefix)
        self.desc_var.set(snippet.description)
        self.body_text.delete('1.0', 'end')
        self.body_text.insert('1.0', snippet.body)

    def new_snippet(self):
        """Create new snippet"""
        self.name_var.set("")
        self.prefix_var.set("")
        self.desc_var.set("")
        self.body_text.delete('1.0', 'end')

    def save_snippet(self):
        """Save current snippet"""
        name = self.name_var.get().strip()
        prefix = self.prefix_var.get().strip()
        body = self.body_text.get('1.0', 'end-1c')

        if not name or not prefix or not body:
            messagebox.showwarning("Warning", "Please fill in all required fields")
            return

        snippet = Snippet(
            name=name,
            prefix=prefix,
            body=body,
            description=self.desc_var.get(),
            language=self.lang_var.get()
        )

        self.snippet_manager.add_custom_snippet(snippet)
        self.load_snippets()
        messagebox.showinfo("Success", "Snippet saved!")

    def delete_snippet(self):
        """Delete selected snippet"""
        selection = self.snippet_list.curselection()
        if not selection:
            return

        language = self.lang_var.get()
        snippets = self.snippet_manager.get_snippets_for_language(language)
        prefix = list(snippets.keys())[selection[0]]

        # Only delete custom snippets
        if language in self.snippet_manager.custom_snippets and \
           prefix in self.snippet_manager.custom_snippets[language]:
            self.snippet_manager.delete_custom_snippet(prefix, language)
            self.load_snippets()
            messagebox.showinfo("Success", "Snippet deleted!")
        else:
            messagebox.showwarning("Warning", "Cannot delete built-in snippets")
