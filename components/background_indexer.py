"""
Background Code Indexing
Indexes codebase in background for fast search and AI context
"""
import tkinter as tk
from tkinter import ttk
import os
import threading
import time
import ast
import re
import json
from collections import defaultdict
import queue
from components import death_theme as T


class CodeIndex:
    """Indexed codebase data"""

    def __init__(self):
        self.symbols = {}  # symbol_name -> [{file, line, type, context}]
        self.files = {}  # file_path -> {symbols, imports, size, modified}
        self.references = defaultdict(set)  # symbol -> set of files
        self.imports = defaultdict(set)  # module -> set of files
        self.last_indexed = 0
        self.index_version = 1

    def add_symbol(self, name, file_path, line, symbol_type, context=""):
        """Add symbol to index"""
        if name not in self.symbols:
            self.symbols[name] = []

        self.symbols[name].append({
            'file': file_path,
            'line': line,
            'type': symbol_type,
            'context': context
        })

        self.references[name].add(file_path)

    def add_import(self, module, file_path):
        """Add import to index"""
        self.imports[module].add(file_path)

    def search(self, query, limit=50):
        """Search index for query"""
        results = []

        # Exact match
        if query in self.symbols:
            results.extend(self.symbols[query][:limit])

        # Partial match
        if len(results) < limit:
            for name, locations in self.symbols.items():
                if query.lower() in name.lower() and name != query:
                    results.extend(locations)
                    if len(results) >= limit:
                        break

        return results[:limit]

    def get_file_symbols(self, file_path):
        """Get all symbols in file"""
        if file_path in self.files:
            return self.files[file_path].get('symbols', [])
        return []

    def save_to_file(self, path):
        """Save index to file"""
        try:
            data = {
                'version': self.index_version,
                'last_indexed': self.last_indexed,
                'symbols': {k: v for k, v in list(self.symbols.items())[:10000]},  # Limit size
                'files': dict(list(self.files.items())[:1000])
            }

            with open(path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Failed to save index: {e}")

    def load_from_file(self, path):
        """Load index from file"""
        if not os.path.exists(path):
            return False

        try:
            with open(path, 'r') as f:
                data = json.load(f)

            self.index_version = data.get('version', 1)
            self.last_indexed = data.get('last_indexed', 0)
            self.symbols = data.get('symbols', {})
            self.files = data.get('files', {})

            # Rebuild references and imports
            for name, locations in self.symbols.items():
                for loc in locations:
                    self.references[name].add(loc['file'])

            return True

        except Exception as e:
            print(f"Failed to load index: {e}")
            return False


class BackgroundIndexer:
    """Indexes codebase in background thread"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.index = CodeIndex()
        self.is_indexing = False
        self.indexing_queue = queue.Queue()
        self.progress_callback = None
        self.workspace_path = None

        # Load saved index
        self._load_index()

        # Start indexing thread
        self.indexer_thread = threading.Thread(target=self._indexing_loop, daemon=True)
        self.indexer_thread.start()

    def _load_index(self):
        """Load saved index"""
        index_file = os.path.join(os.path.expanduser('~'), '.deathaius_index', 'code_index.json')
        if os.path.exists(index_file):
            self.index.load_from_file(index_file)

    def _save_index(self):
        """Save index to disk"""
        index_dir = os.path.join(os.path.expanduser('~'), '.deathaius_index')
        os.makedirs(index_dir, exist_ok=True)

        index_file = os.path.join(index_dir, 'code_index.json')
        self.index.save_to_file(index_file)

    def index_workspace(self, workspace_path, progress_callback=None):
        """Start indexing workspace"""
        self.workspace_path = workspace_path
        self.progress_callback = progress_callback

        # Queue indexing request
        self.indexing_queue.put(('index_workspace', workspace_path))

    def reindex_file(self, file_path):
        """Reindex single file"""
        self.indexing_queue.put(('index_file', file_path))

    def _indexing_loop(self):
        """Background indexing loop"""
        while True:
            try:
                task_type, path = self.indexing_queue.get(timeout=1.0)

                if task_type == 'index_workspace':
                    self._index_workspace_sync(path)
                elif task_type == 'index_file':
                    self._index_file_sync(path)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Indexing error: {e}")

    def _index_workspace_sync(self, workspace_path):
        """Index entire workspace (blocking)"""
        self.is_indexing = True

        try:
            # Clear old index for this workspace
            # (In production, you'd do incremental updates)

            files_to_index = []

            # Walk workspace
            for root, dirs, files in os.walk(workspace_path):
                # Skip common ignore directories
                dirs[:] = [d for d in dirs if d not in [
                    '.git', '__pycache__', 'node_modules', '.venv', 'venv',
                    'dist', 'build', '.idea', '.vscode'
                ]]

                for file in files:
                    if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx')):
                        file_path = os.path.join(root, file)
                        files_to_index.append(file_path)

            # Index files
            total = len(files_to_index)
            for i, file_path in enumerate(files_to_index):
                self._index_file_sync(file_path)

                # Report progress
                if self.progress_callback:
                    progress = int((i + 1) / total * 100)
                    self.progress_callback(progress, file_path)

                # Small delay to not hog CPU
                time.sleep(0.001)

            # Update timestamp
            self.index.last_indexed = time.time()

            # Save index
            self._save_index()

        finally:
            self.is_indexing = False

    def _index_file_sync(self, file_path):
        """Index single file (blocking)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Detect language
            ext = os.path.splitext(file_path)[1]

            if ext == '.py':
                self._index_python_file(file_path, content)
            elif ext in ['.js', '.jsx', '.ts', '.tsx']:
                self._index_javascript_file(file_path, content)

            # Store file metadata
            self.index.files[file_path] = {
                'size': len(content),
                'modified': os.path.getmtime(file_path),
                'lines': content.count('\n')
            }

        except Exception as e:
            print(f"Failed to index {file_path}: {e}")

    def _index_python_file(self, file_path, content):
        """Index Python file"""
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # Functions
                if isinstance(node, ast.FunctionDef):
                    # Get context (docstring or first line)
                    context = ast.get_docstring(node) or ""
                    if len(context) > 100:
                        context = context[:100] + "..."

                    self.index.add_symbol(
                        node.name,
                        file_path,
                        node.lineno,
                        'function',
                        context
                    )

                # Classes
                elif isinstance(node, ast.ClassDef):
                    context = ast.get_docstring(node) or ""
                    if len(context) > 100:
                        context = context[:100] + "..."

                    self.index.add_symbol(
                        node.name,
                        file_path,
                        node.lineno,
                        'class',
                        context
                    )

                # Imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        self.index.add_import(alias.name, file_path)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.index.add_import(node.module, file_path)

        except SyntaxError:
            pass  # Skip files with syntax errors

    def _index_javascript_file(self, file_path, content):
        """Index JavaScript file (regex-based)"""
        # Functions
        func_pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?\()'
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1) or match.group(2)
            line = content[:match.start()].count('\n') + 1

            self.index.add_symbol(
                func_name,
                file_path,
                line,
                'function',
                ''
            )

        # Classes
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            line = content[:match.start()].count('\n') + 1

            self.index.add_symbol(
                class_name,
                file_path,
                line,
                'class',
                ''
            )

        # Imports
        import_pattern = r'import\s+.*?from\s+["\']([^"\']+)["\']'
        for match in re.finditer(import_pattern, content):
            module = match.group(1)
            self.index.add_import(module, file_path)

    def search(self, query):
        """Search index"""
        return self.index.search(query)

    def get_symbol_locations(self, symbol_name):
        """Get all locations of symbol"""
        return self.index.symbols.get(symbol_name, [])


class IndexingProgressWidget(tk.Frame):
    """Widget showing indexing progress"""

    def __init__(self, parent):
        super().__init__(parent, bg=T.BG3)

        # Progress bar
        self.progress = ttk.Progressbar(
            self,
            mode='determinate',
            length=200
        )
        self.progress.pack(side=tk.LEFT, padx=10, pady=5)

        # Status label
        self.status_label = tk.Label(
            self,
            text="Ready",
            bg=T.BG3,
            fg=T.TEXT,
            font=(T.UI, 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=5)

    def update_progress(self, percent, current_file=""):
        """Update progress"""
        self.progress['value'] = percent

        file_name = os.path.basename(current_file) if current_file else ""
        self.status_label.config(text=f"Indexing... {percent}% - {file_name}")

    def set_ready(self):
        """Set to ready state"""
        self.progress['value'] = 0
        self.status_label.config(text="✓ Indexing complete", fg=T.BILE)


class GlobalSearchDialog(tk.Toplevel):
    """Global search dialog using index"""

    def __init__(self, parent, background_indexer):
        super().__init__(parent)
        self.indexer = background_indexer
        self.title("Global Search")
        self.geometry("700x500")
        self.configure(bg=T.BG3)

        self.setup_ui()

    def setup_ui(self):
        """Setup search UI"""
        # Search input
        input_frame = tk.Frame(self, bg=T.BG3)
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(input_frame, text="🔍", bg=T.BG3, fg=T.BILE,
                font=(T.UI, 14)).pack(side=tk.LEFT, padx=5)

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search())

        search_entry = tk.Entry(
            input_frame,
            textvariable=self.search_var,
            font=(T.UI, 12),
            bg=T.BG,
            fg=T.TEXT,
            insertbackground=T.TEXT
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        search_entry.focus()

        # Results
        results_frame = tk.Frame(self, bg=T.BG)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(results_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.results_list = tk.Listbox(
            results_frame,
            bg=T.BG,
            fg=T.TEXT,
            font=(T.MONO, 10),
            selectbackground=T.HOVER,
            yscrollcommand=scrollbar.set
        )
        self.results_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_list.yview)

        self.results_list.bind('<Double-Button-1>', self.on_result_select)
        self.results_list.bind('<Return>', self.on_result_select)

        # Status
        self.status_label = tk.Label(
            self,
            text="Type to search...",
            bg=T.BG3,
            fg=T.TEXT2,
            font=(T.UI, 9)
        )
        self.status_label.pack(pady=5)

    def search(self):
        """Perform search"""
        query = self.search_var.get().strip()

        self.results_list.delete(0, tk.END)

        if len(query) < 2:
            self.status_label.config(text="Type at least 2 characters...")
            return

        # Search index
        results = self.indexer.search(query)

        if not results:
            self.status_label.config(text="No results found", fg=T.BLOOD_LIGHT)
            return

        # Display results
        for result in results:
            icon = {
                'function': '🔧',
                'class': '📦',
                'variable': '📌'
            }.get(result.get('type', ''), '📄')

            file_name = os.path.basename(result['file'])
            display = f"{icon} {result.get('type', 'symbol')} in {file_name}:{result['line']}"

            if result.get('context'):
                display += f" - {result['context'][:50]}"

            self.results_list.insert(tk.END, display)

        self.status_label.config(text=f"{len(results)} results", fg=T.BILE)

    def on_result_select(self, event=None):
        """Handle result selection"""
        selection = self.results_list.curselection()
        if not selection:
            return

        # Get result
        query = self.search_var.get().strip()
        results = self.indexer.search(query)

        if selection[0] < len(results):
            result = results[selection[0]]

            # Open file and jump to line
            # TODO: Integrate with IDE file opening
            print(f"Open {result['file']}:{result['line']}")

            self.destroy()
