"""
Error Detection and Linting
Real-time error detection and code quality checking
"""
import tkinter as tk
import re
import ast
import subprocess
import threading
from collections import defaultdict
from components import death_theme as T


class ErrorDetector:
    """Real-time error detection and linting"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.errors = defaultdict(list)  # file_path -> list of errors
        self.warnings = defaultdict(list)
        self.check_delay = 1000  # 1 second after typing stops
        self.check_timer = None
        self.error_markers = {}  # Store error marker widgets

    def setup_editor(self, editor, file_path):
        """Setup error detection for an editor"""
        # Bind to text changes
        editor.bind('<<Modified>>', lambda e: self.schedule_check(editor, file_path))

        # Configure error tags
        editor.tag_configure("error", background=T.BLOOD_DEEP, underline=True)
        editor.tag_configure("warning", background=T.BLOOD_DEEP, underline=True)

    def schedule_check(self, editor, file_path):
        """Schedule a check after typing stops"""
        if self.check_timer:
            editor.after_cancel(self.check_timer)

        self.check_timer = editor.after(
            self.check_delay,
            lambda: self.check_code(editor, file_path)
        )

    def check_code(self, editor, file_path):
        """Check code for errors"""
        content = editor.get("1.0", "end-1c")

        # Detect language
        language = "Python"
        if hasattr(editor, 'current_language'):
            language = editor.current_language
        elif file_path.endswith('.js'):
            language = "JavaScript"

        # Run checks in background
        threading.Thread(
            target=self._check_thread,
            args=(editor, file_path, content, language),
            daemon=True
        ).start()

    def _check_thread(self, editor, file_path, content, language):
        """Background thread for checking code"""
        errors = []
        warnings = []

        try:
            if language == "Python":
                errors, warnings = self._check_python(content)
            elif language == "JavaScript":
                errors, warnings = self._check_javascript(content)

            # Update on main thread
            editor.after(0, self._update_errors, editor, file_path, errors, warnings)

        except Exception as e:
            print(f"Error detection failed: {e}")

    def _check_python(self, content):
        """Check Python code"""
        errors = []
        warnings = []

        # Syntax check using ast
        try:
            ast.parse(content)
        except SyntaxError as e:
            errors.append({
                'line': e.lineno,
                'column': e.offset,
                'message': e.msg,
                'type': 'SyntaxError'
            })
        except Exception as e:
            errors.append({
                'line': 1,
                'column': 0,
                'message': str(e),
                'type': 'ParseError'
            })

        # Basic linting rules
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Undefined variables (simple check)
            if '=' in line:
                parts = line.split('=')
                if len(parts) == 2:
                    # Check for comparison in assignment
                    if '==' in parts[0]:
                        warnings.append({
                            'line': i,
                            'column': 0,
                            'message': 'Possible typo: == in assignment',
                            'type': 'PossibleBug'
                        })

            # Unused imports (simple)
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                module_name = line.split()[1].split('.')[0]
                if content.count(module_name) == 1:  # Only appears in import
                    warnings.append({
                        'line': i,
                        'column': 0,
                        'message': f'Unused import: {module_name}',
                        'type': 'UnusedImport'
                    })

            # Line too long
            if len(line) > 120:
                warnings.append({
                    'line': i,
                    'column': 120,
                    'message': 'Line too long (>120 characters)',
                    'type': 'LineLength'
                })

            # Missing docstring for functions/classes
            if line.strip().startswith('def ') or line.strip().startswith('class '):
                if i + 1 < len(lines):
                    next_line = lines[i].strip()
                    if not (next_line.startswith('"""') or next_line.startswith("'''")):
                        warnings.append({
                            'line': i,
                            'column': 0,
                            'message': 'Missing docstring',
                            'type': 'MissingDocstring'
                        })

        # Try pylint if available
        try:
            result = subprocess.run(
                ['pylint', '--output-format=json', '-'],
                input=content,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 or result.stdout:
                import json
                pylint_results = json.loads(result.stdout)
                for issue in pylint_results:
                    severity = issue.get('type', 'warning')
                    if severity in ['error', 'fatal']:
                        errors.append({
                            'line': issue['line'],
                            'column': issue.get('column', 0),
                            'message': issue['message'],
                            'type': issue.get('symbol', 'error')
                        })
                    else:
                        warnings.append({
                            'line': issue['line'],
                            'column': issue.get('column', 0),
                            'message': issue['message'],
                            'type': issue.get('symbol', 'warning')
                        })
        except:
            pass  # Pylint not available or failed

        return errors, warnings

    def _check_javascript(self, content):
        """Check JavaScript code"""
        errors = []
        warnings = []

        lines = content.split('\n')

        # Basic syntax checks
        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Missing semicolons
            if stripped and not stripped.endswith((';', '{', '}', ',')) and \
               any(kw in stripped for kw in ['const ', 'let ', 'var ', 'return ']):
                warnings.append({
                    'line': i,
                    'column': len(line) - 1,
                    'message': 'Missing semicolon',
                    'type': 'MissingSemicolon'
                })

            # console.log statements
            if 'console.log' in stripped:
                warnings.append({
                    'line': i,
                    'column': stripped.index('console.log'),
                    'message': 'console.log statement (remove before production)',
                    'type': 'ConsoleLog'
                })

            # == instead of ===
            if '==' in stripped and '===' not in stripped:
                warnings.append({
                    'line': i,
                    'column': stripped.index('=='),
                    'message': 'Use === instead of ==',
                    'type': 'LooseEquality'
                })

            # Var instead of let/const
            if stripped.startswith('var '):
                warnings.append({
                    'line': i,
                    'column': 0,
                    'message': 'Use let or const instead of var',
                    'type': 'VarUsage'
                })

        # Try eslint if available
        try:
            result = subprocess.run(
                ['eslint', '--format=json', '--stdin'],
                input=content,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.stdout:
                import json
                eslint_results = json.loads(result.stdout)
                if eslint_results and len(eslint_results) > 0:
                    for issue in eslint_results[0].get('messages', []):
                        severity = issue.get('severity', 1)
                        if severity == 2:  # Error
                            errors.append({
                                'line': issue['line'],
                                'column': issue.get('column', 0),
                                'message': issue['message'],
                                'type': issue.get('ruleId', 'error')
                            })
                        else:  # Warning
                            warnings.append({
                                'line': issue['line'],
                                'column': issue.get('column', 0),
                                'message': issue['message'],
                                'type': issue.get('ruleId', 'warning')
                            })
        except:
            pass  # ESLint not available or failed

        return errors, warnings

    def _update_errors(self, editor, file_path, errors, warnings):
        """Update error markers in editor (main thread)"""
        # Clear previous error tags
        editor.tag_remove("error", "1.0", "end")
        editor.tag_remove("warning", "1.0", "end")

        # Store errors
        self.errors[file_path] = errors
        self.warnings[file_path] = warnings

        # Mark errors
        for error in errors:
            line = error['line']
            try:
                start = f"{line}.0"
                end = f"{line}.end"
                editor.tag_add("error", start, end)
            except:
                pass

        # Mark warnings
        for warning in warnings:
            line = warning['line']
            try:
                start = f"{line}.0"
                end = f"{line}.end"
                editor.tag_add("warning", start, end)
            except:
                pass

        # Update error panel if exists
        if hasattr(self.ide, 'error_panel'):
            self.ide.error_panel.update_errors(file_path, errors, warnings)

        # Update status bar
        if hasattr(self.ide, 'status_bar'):
            error_count = len(errors)
            warning_count = len(warnings)
            if error_count > 0:
                self.ide.status_bar.config(
                    text=f"❌ {error_count} errors, ⚠️ {warning_count} warnings",
                    fg=T.BLOOD_LIGHT
                )
            elif warning_count > 0:
                self.ide.status_bar.config(
                    text=f"⚠️ {warning_count} warnings",
                    fg=T.AMBER
                )
            else:
                self.ide.status_bar.config(text="✓ No issues", fg=T.BILE)

    def get_errors_for_file(self, file_path):
        """Get errors for a specific file"""
        return self.errors.get(file_path, [])

    def get_warnings_for_file(self, file_path):
        """Get warnings for a specific file"""
        return self.warnings.get(file_path, [])

    def clear_errors(self, file_path):
        """Clear errors for a file"""
        if file_path in self.errors:
            del self.errors[file_path]
        if file_path in self.warnings:
            del self.warnings[file_path]


class ErrorPanel(tk.Frame):
    """Panel showing all errors and warnings"""

    def __init__(self, parent, ide_instance):
        super().__init__(parent, bg=T.BG)
        self.ide = ide_instance

        # Header
        header = tk.Frame(self, bg=T.BG3, height=30)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="⚠️ Problems", font=(T.UI, 10, 'bold'),
                fg=T.BILE, bg=T.BG3).pack(side=tk.LEFT, padx=10, pady=5)

        self.count_label = tk.Label(header, text="0 issues", bg=T.BG3,
                                    fg=T.TEXT2, font=(T.UI, 9))
        self.count_label.pack(side=tk.LEFT)

        # Error list
        list_frame = tk.Frame(self, bg=T.BG)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.error_list = tk.Listbox(
            list_frame,
            bg=T.BG,
            fg=T.TEXT,
            font=(T.MONO, 9),
            selectbackground=T.HOVER,
            activestyle='none',
            yscrollcommand=scrollbar.set
        )
        self.error_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.error_list.yview)

        # Bind double-click to jump to error
        self.error_list.bind('<Double-Button-1>', self.jump_to_error)

        self.error_data = []  # Store error details

    def update_errors(self, file_path, errors, warnings):
        """Update the error list"""
        self.error_list.delete(0, tk.END)
        self.error_data = []

        # Add errors
        for error in errors:
            display = f"❌ {file_path}:{error['line']} - {error['message']}"
            self.error_list.insert(tk.END, display)
            self.error_list.itemconfig(tk.END, fg=T.BLOOD_LIGHT)
            self.error_data.append({
                'file': file_path,
                'line': error['line'],
                'type': 'error',
                'data': error
            })

        # Add warnings
        for warning in warnings:
            display = f"⚠️ {file_path}:{warning['line']} - {warning['message']}"
            self.error_list.insert(tk.END, display)
            self.error_list.itemconfig(tk.END, fg=T.AMBER)
            self.error_data.append({
                'file': file_path,
                'line': warning['line'],
                'type': 'warning',
                'data': warning
            })

        # Update count
        total = len(errors) + len(warnings)
        self.count_label.config(text=f"{len(errors)} errors, {len(warnings)} warnings")

    def jump_to_error(self, event=None):
        """Jump to error location in editor"""
        selection = self.error_list.curselection()
        if not selection:
            return

        error_info = self.error_data[selection[0]]
        file_path = error_info['file']
        line = error_info['line']

        # Open file if not current
        if hasattr(self.ide, 'current_file') and self.ide.current_file != file_path:
            if hasattr(self.ide, 'open_file'):
                self.ide.open_file(file_path)

        # Jump to line
        if hasattr(self.ide, 'tabs') and self.ide.tabs.current_editor:
            editor = self.ide.tabs.current_editor
            editor.mark_set("insert", f"{line}.0")
            editor.see(f"{line}.0")
            editor.focus()
