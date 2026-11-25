"""
Smart Context System
Intelligent context gathering for AI assistance
"""
import os
import ast
import re
from collections import defaultdict


class SmartContext:
    """Intelligent context gathering for AI"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.project_index = {}  # file_path -> metadata
        self.symbol_index = {}  # symbol_name -> locations
        self.dependency_graph = defaultdict(set)  # file -> dependencies
        self.last_indexed = 0

    def index_project(self, workspace_path):
        """Index the entire project"""
        if not workspace_path or not os.path.exists(workspace_path):
            return

        self.project_index = {}
        self.symbol_index = {}
        self.dependency_graph = defaultdict(set)

        # Walk through project
        for root, dirs, files in os.walk(workspace_path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]

            for file in files:
                if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx')):
                    file_path = os.path.join(root, file)
                    try:
                        self._index_file(file_path)
                    except Exception as e:
                        print(f"Failed to index {file_path}: {e}")

        self.last_indexed = os.path.getmtime(workspace_path)

    def _index_file(self, file_path):
        """Index a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            metadata = {
                'path': file_path,
                'size': len(content),
                'lines': content.count('\n'),
                'functions': [],
                'classes': [],
                'imports': [],
                'exports': [],
            }

            # Detect language
            ext = os.path.splitext(file_path)[1]
            if ext == '.py':
                self._index_python(file_path, content, metadata)
            elif ext in ['.js', '.jsx', '.ts', '.tsx']:
                self._index_javascript(file_path, content, metadata)

            self.project_index[file_path] = metadata

        except Exception as e:
            print(f"Error indexing {file_path}: {e}")

    def _index_python(self, file_path, content, metadata):
        """Index Python file"""
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # Functions
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'decorators': [d.id if isinstance(d, ast.Name) else '' for d in node.decorator_list]
                    }
                    metadata['functions'].append(func_info)

                    # Add to symbol index
                    if node.name not in self.symbol_index:
                        self.symbol_index[node.name] = []
                    self.symbol_index[node.name].append({
                        'file': file_path,
                        'line': node.lineno,
                        'type': 'function'
                    })

                # Classes
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'line': node.lineno,
                        'bases': [self._get_name(base) for base in node.bases],
                        'methods': []
                    }

                    # Get methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info['methods'].append({
                                'name': item.name,
                                'line': item.lineno
                            })

                    metadata['classes'].append(class_info)

                    # Add to symbol index
                    if node.name not in self.symbol_index:
                        self.symbol_index[node.name] = []
                    self.symbol_index[node.name].append({
                        'file': file_path,
                        'line': node.lineno,
                        'type': 'class'
                    })

                # Imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        metadata['imports'].append(alias.name)
                        self.dependency_graph[file_path].add(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        metadata['imports'].append(node.module)
                        self.dependency_graph[file_path].add(node.module)

        except SyntaxError:
            pass  # Skip files with syntax errors

    def _index_javascript(self, file_path, content, metadata):
        """Index JavaScript file (basic regex-based)"""
        # Functions
        func_pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?\(|let\s+(\w+)\s*=\s*(?:async\s+)?\(|var\s+(\w+)\s*=\s*(?:async\s+)?\()'
        for match in re.finditer(func_pattern, content):
            func_name = next(g for g in match.groups() if g)
            line = content[:match.start()].count('\n') + 1

            metadata['functions'].append({
                'name': func_name,
                'line': line
            })

            if func_name not in self.symbol_index:
                self.symbol_index[func_name] = []
            self.symbol_index[func_name].append({
                'file': file_path,
                'line': line,
                'type': 'function'
            })

        # Classes
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            line = content[:match.start()].count('\n') + 1

            metadata['classes'].append({
                'name': class_name,
                'line': line
            })

            if class_name not in self.symbol_index:
                self.symbol_index[class_name] = []
            self.symbol_index[class_name].append({
                'file': file_path,
                'line': line,
                'type': 'class'
            })

        # Imports
        import_pattern = r'import\s+(?:{[^}]+}|\w+)\s+from\s+["\']([^"\']+)["\']|require\(["\']([^"\']+)["\']\)'
        for match in re.finditer(import_pattern, content):
            module = match.group(1) or match.group(2)
            metadata['imports'].append(module)
            self.dependency_graph[file_path].add(module)

        # Exports
        export_pattern = r'export\s+(?:default\s+)?(?:function\s+(\w+)|class\s+(\w+)|const\s+(\w+))'
        for match in re.finditer(export_pattern, content):
            export_name = next(g for g in match.groups() if g)
            metadata['exports'].append(export_name)

    def _get_name(self, node):
        """Get name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return ''

    def get_context_for_query(self, query, current_file=None, max_context=5000):
        """Get relevant context for an AI query"""
        context_parts = []
        total_chars = 0

        # 1. Current file context
        if current_file and current_file in self.project_index:
            file_meta = self.project_index[current_file]
            context = f"Current file: {os.path.basename(current_file)}\n"

            if file_meta['classes']:
                context += f"Classes: {', '.join(c['name'] for c in file_meta['classes'])}\n"
            if file_meta['functions']:
                func_names = [f['name'] for f in file_meta['functions'][:10]]
                context += f"Functions: {', '.join(func_names)}\n"

            context_parts.append(context)
            total_chars += len(context)

        # 2. Related symbols mentioned in query
        words = re.findall(r'\b\w+\b', query)
        for word in words:
            if total_chars >= max_context:
                break

            if word in self.symbol_index:
                locations = self.symbol_index[word]
                for loc in locations[:3]:  # Max 3 locations per symbol
                    if total_chars >= max_context:
                        break

                    context = f"\n{word} ({loc['type']}) defined in {os.path.basename(loc['file'])}:{loc['line']}\n"
                    context_parts.append(context)
                    total_chars += len(context)

        # 3. Project structure summary
        if total_chars < max_context:
            structure = self.get_project_structure_summary()
            if structure:
                context_parts.append(f"\nProject structure:\n{structure}\n")

        return ''.join(context_parts)

    def get_project_structure_summary(self):
        """Get a summary of project structure"""
        if not self.project_index:
            return ""

        summary = []
        file_count = len(self.project_index)
        total_lines = sum(meta['lines'] for meta in self.project_index.values())
        total_functions = sum(len(meta['functions']) for meta in self.project_index.values())
        total_classes = sum(len(meta['classes']) for meta in self.project_index.values())

        summary.append(f"Files: {file_count}")
        summary.append(f"Total lines: {total_lines}")
        summary.append(f"Functions: {total_functions}")
        summary.append(f"Classes: {total_classes}")

        return '\n'.join(summary)

    def get_dependencies_for_file(self, file_path):
        """Get dependencies for a file"""
        return list(self.dependency_graph.get(file_path, []))

    def find_symbol(self, symbol_name):
        """Find all locations of a symbol"""
        return self.symbol_index.get(symbol_name, [])

    def find_references(self, symbol_name, workspace_path):
        """Find all references to a symbol in the project"""
        references = []

        for file_path in self.project_index.keys():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Simple regex search
                pattern = r'\b' + re.escape(symbol_name) + r'\b'
                for match in re.finditer(pattern, content):
                    line_num = content[:match.start()].count('\n') + 1
                    # Get the line content
                    lines = content.split('\n')
                    line_content = lines[line_num - 1] if line_num <= len(lines) else ""

                    references.append({
                        'file': file_path,
                        'line': line_num,
                        'column': match.start() - content.rfind('\n', 0, match.start()) - 1,
                        'content': line_content.strip()
                    })
            except:
                pass

        return references

    def get_relevant_files_for_query(self, query, max_files=5):
        """Get most relevant files for a query"""
        if not self.project_index:
            return []

        # Score files based on query keywords
        scores = {}
        query_words = set(re.findall(r'\b\w+\b', query.lower()))

        for file_path, metadata in self.project_index.items():
            score = 0

            # Check file name
            file_name = os.path.basename(file_path).lower()
            for word in query_words:
                if word in file_name:
                    score += 10

            # Check symbols
            for func in metadata['functions']:
                if func['name'].lower() in query_words:
                    score += 5

            for cls in metadata['classes']:
                if cls['name'].lower() in query_words:
                    score += 5

            # Check imports
            for imp in metadata['imports']:
                if any(word in imp.lower() for word in query_words):
                    score += 2

            if score > 0:
                scores[file_path] = score

        # Sort by score and return top files
        sorted_files = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [f[0] for f in sorted_files[:max_files]]

    def get_ai_context_string(self, query, current_file=None):
        """Get formatted context string for AI"""
        parts = []

        # Project summary
        parts.append("=== PROJECT CONTEXT ===")
        parts.append(self.get_project_structure_summary())
        parts.append("")

        # Current file
        if current_file:
            parts.append(f"=== CURRENT FILE: {os.path.basename(current_file)} ===")
            if current_file in self.project_index:
                meta = self.project_index[current_file]
                if meta['classes']:
                    parts.append(f"Classes: {', '.join(c['name'] for c in meta['classes'])}")
                if meta['functions']:
                    parts.append(f"Functions: {', '.join(f['name'] for f in meta['functions'][:20])}")
                if meta['imports']:
                    parts.append(f"Imports: {', '.join(meta['imports'][:10])}")
            parts.append("")

        # Relevant files
        relevant = self.get_relevant_files_for_query(query, max_files=3)
        if relevant:
            parts.append("=== RELEVANT FILES ===")
            for file_path in relevant:
                parts.append(f"- {os.path.relpath(file_path, self.ide.workspace_path)}")
                meta = self.project_index[file_path]
                if meta['functions']:
                    parts.append(f"  Functions: {', '.join(f['name'] for f in meta['functions'][:5])}")
            parts.append("")

        return '\n'.join(parts)


class ContextAwareAssistant:
    """AI assistant with smart context"""

    def __init__(self, ide_instance, smart_context):
        self.ide = ide_instance
        self.context = smart_context

    def ask(self, query, include_current_file=True):
        """Ask AI with smart context"""
        current_file = None
        if include_current_file and hasattr(self.ide, 'current_file'):
            current_file = self.ide.current_file

        # Get context
        context_str = self.context.get_ai_context_string(query, current_file)

        # Get current file content if needed
        file_content = ""
        if include_current_file and current_file:
            try:
                if hasattr(self.ide, 'tabs') and self.ide.tabs.current_editor:
                    file_content = self.ide.tabs.current_editor.get('1.0', 'end-1c')
                elif hasattr(self.ide, 'code_editor'):
                    file_content = self.ide.code_editor.get('1.0', 'end-1c')
            except:
                pass

        # Build prompt
        system_prompt = f"""You are an AI coding assistant with access to project context.

{context_str}

Current file content:
```
{file_content[:2000]}  # Limit to first 2000 chars
```

Provide helpful, context-aware responses."""

        # Call model
        if hasattr(self.ide, '_call_model'):
            return self.ide._call_model(
                self.ide.coder_model.get() if hasattr(self.ide, 'coder_model') else 'default',
                system_prompt,
                query,
                120
            )

        return "AI model not available"
