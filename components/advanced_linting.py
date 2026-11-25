"""
Advanced Real-Time Linting
Enhanced linting with inline warnings, quick fixes, and code quality metrics
"""
import tkinter as tk
from tkinter import ttk
import re
import ast
from components import death_theme as T


class LintMessage:
    """Single lint message"""

    def __init__(self, line, column, severity, message, rule_id="", fix=None):
        self.line = line
        self.column = column
        self.severity = severity  # 'error', 'warning', 'info', 'hint'
        self.message = message
        self.rule_id = rule_id
        self.fix = fix  # Optional QuickFix object


class QuickFix:
    """Quick fix for a lint message"""

    def __init__(self, title, replacement, start_pos, end_pos):
        self.title = title
        self.replacement = replacement
        self.start_pos = start_pos
        self.end_pos = end_pos


class AdvancedLinter:
    """Advanced linting with real-time display"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.lint_messages = {}  # file_path -> [LintMessage]
        self.gutter_widgets = {}  # editor -> {line -> widget}

    def setup_editor(self, editor, file_path=""):
        """Setup advanced linting on editor"""
        # Configure tags for different severities
        editor.tag_configure("error_underline",
                           underline=True,
                           underlinefg=T.BLOOD_LIGHT)
        editor.tag_configure("warning_underline",
                           underline=True,
                           underlinefg=T.AMBER)
        editor.tag_configure("info_underline",
                           underline=True,
                           underlinefg=T.SIGNAL)
        editor.tag_configure("hint_underline",
                           underline=True,
                           underlinefg=T.TEXT2)

        # Configure line highlight
        editor.tag_configure("error_line", background=T.BLOOD_DEEP)
        editor.tag_configure("warning_line", background=T.BLOOD_DEEP)

        # Bind hover for tooltips
        editor.bind('<Motion>', lambda e: self._show_tooltip(editor, e))
        editor.bind('<Leave>', lambda e: self._hide_tooltip())

        # Initialize gutter
        if editor not in self.gutter_widgets:
            self.gutter_widgets[editor] = {}

    def lint_code(self, editor, file_path, content, language="Python"):
        """Perform linting and display results"""
        messages = []

        if language == "Python":
            messages = self._lint_python(content)
        elif language == "JavaScript":
            messages = self._lint_javascript(content)

        # Store messages
        self.lint_messages[file_path] = messages

        # Display in editor
        self._display_lint_messages(editor, messages)

        return messages

    def _lint_python(self, content):
        """Advanced Python linting"""
        messages = []
        lines = content.split('\n')

        # Syntax check
        try:
            ast.parse(content)
        except SyntaxError as e:
            messages.append(LintMessage(
                e.lineno or 1,
                e.offset or 0,
                'error',
                e.msg,
                'syntax-error'
            ))

        # Advanced checks
        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Trailing whitespace
            if line != line.rstrip():
                messages.append(LintMessage(
                    i, len(line.rstrip()),
                    'hint',
                    'Trailing whitespace',
                    'trailing-whitespace',
                    QuickFix('Remove trailing whitespace',
                           line.rstrip(), f"{i}.0", f"{i}.end")
                ))

            # Line too long
            if len(line) > 88:  # PEP 8 suggests 79, but 88 is common
                messages.append(LintMessage(
                    i, 88,
                    'warning',
                    f'Line too long ({len(line)}/88)',
                    'line-too-long'
                ))

            # Missing docstring
            if stripped.startswith('def ') or stripped.startswith('class '):
                # Check next line
                if i < len(lines):
                    next_line = lines[i].strip()
                    if not (next_line.startswith('"""') or next_line.startswith("'''")):
                        messages.append(LintMessage(
                            i, 0,
                            'info',
                            'Missing docstring',
                            'missing-docstring'
                        ))

            # TODO comparison
            if '== None' in line or '!= None' in line:
                messages.append(LintMessage(
                    i, line.find('==') if '==' in line else line.find('!='),
                    'warning',
                    'Use "is None" instead of "== None"',
                    'none-comparison',
                    QuickFix('Replace with "is None"',
                           line.replace('== None', 'is None').replace('!= None', 'is not None'),
                           f"{i}.0", f"{i}.end")
                ))

            # Mutable default argument
            if 'def ' in line and ('=[]' in line or '={}' in line):
                messages.append(LintMessage(
                    i, line.find('=['),
                    'warning',
                    'Dangerous default value [] (mutable)',
                    'dangerous-default-value'
                ))

            # Bare except
            if stripped == 'except:':
                messages.append(LintMessage(
                    i, 0,
                    'warning',
                    'Bare except clause catches all exceptions',
                    'bare-except',
                    QuickFix('Replace with "except Exception:"',
                           '    except Exception:',
                           f"{i}.0", f"{i}.end")
                ))

            # print() statements (could be debug code)
            if 'print(' in stripped and not stripped.startswith('#'):
                messages.append(LintMessage(
                    i, stripped.find('print('),
                    'hint',
                    'print() statement found (debug code?)',
                    'print-statement'
                ))

            # TODO comments
            if 'TODO' in stripped or 'FIXME' in stripped:
                messages.append(LintMessage(
                    i, 0,
                    'info',
                    'TODO comment found',
                    'todo-comment'
                ))

        return messages

    def _lint_javascript(self, content):
        """Advanced JavaScript linting"""
        messages = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Missing semicolon
            if stripped and not stripped.endswith((';', '{', '}', ',', ':', '//')) and \
               any(kw in stripped for kw in ['const ', 'let ', 'var ', 'return ']):
                messages.append(LintMessage(
                    i, len(line) - 1,
                    'warning',
                    'Missing semicolon',
                    'semi',
                    QuickFix('Add semicolon', line.rstrip() + ';', f"{i}.0", f"{i}.end")
                ))

            # == instead of ===
            if '==' in stripped and '===' not in stripped and '!==' not in stripped:
                messages.append(LintMessage(
                    i, stripped.find('=='),
                    'warning',
                    'Use === instead of ==',
                    'eqeqeq',
                    QuickFix('Replace with ===',
                           stripped.replace('==', '==='),
                           f"{i}.0", f"{i}.end")
                ))

            # var instead of let/const
            if stripped.startswith('var '):
                messages.append(LintMessage(
                    i, 0,
                    'warning',
                    'Use let or const instead of var',
                    'no-var',
                    QuickFix('Replace with const', stripped.replace('var ', 'const '),
                           f"{i}.0", f"{i}.end")
                ))

            # console.log
            if 'console.log' in stripped:
                messages.append(LintMessage(
                    i, stripped.find('console.log'),
                    'warning',
                    'console.log() found (debug code?)',
                    'no-console'
                ))

        return messages

    def _display_lint_messages(self, editor, messages):
        """Display lint messages in editor"""
        # Clear previous markings
        for tag in ['error_underline', 'warning_underline', 'info_underline', 'hint_underline',
                   'error_line', 'warning_line']:
            editor.tag_remove(tag, '1.0', 'end')

        # Clear gutter
        if editor in self.gutter_widgets:
            for widget in self.gutter_widgets[editor].values():
                try:
                    widget.destroy()
                except:
                    pass
            self.gutter_widgets[editor] = {}

        # Apply new markings
        for msg in messages:
            # Underline
            tag = f"{msg.severity}_underline"
            try:
                start = f"{msg.line}.{msg.column}"
                end = f"{msg.line}.end"
                editor.tag_add(tag, start, end)
            except:
                pass

            # Line highlight for errors
            if msg.severity == 'error':
                try:
                    editor.tag_add('error_line', f"{msg.line}.0", f"{msg.line}.end")
                except:
                    pass

            # Gutter indicator
            self._add_gutter_indicator(editor, msg)

    def _add_gutter_indicator(self, editor, message):
        """Add indicator in gutter (line number area)"""
        if not hasattr(editor, 'line_numbers'):
            return

        try:
            # Create indicator
            indicator_color = {
                'error': T.BLOOD_LIGHT,
                'warning': T.AMBER,
                'info': T.SIGNAL,
                'hint': T.TEXT2
            }.get(message.severity, T.TEXT2)

            # TODO: Add visual indicator in line number area
            # This would require custom line number widget

        except Exception as e:
            print(f"Gutter indicator error: {e}")

    def _show_tooltip(self, editor, event):
        """Show tooltip on hover"""
        try:
            # Get position
            index = editor.index(f"@{event.x},{event.y}")
            line_num = int(index.split('.')[0])

            # Find messages for this line
            file_path = getattr(editor, 'file_path', '')
            if file_path not in self.lint_messages:
                return

            line_messages = [msg for msg in self.lint_messages[file_path]
                           if msg.line == line_num]

            if line_messages:
                self._show_tooltip_widget(editor, event, line_messages)
            else:
                self._hide_tooltip()

        except:
            pass

    def _show_tooltip_widget(self, editor, event, messages):
        """Show tooltip widget"""
        # TODO: Implement tooltip widget
        pass

    def _hide_tooltip(self):
        """Hide tooltip"""
        # TODO: Implement
        pass

    def apply_quick_fix(self, editor, fix):
        """Apply a quick fix"""
        if not fix:
            return

        try:
            editor.delete(fix.start_pos, fix.end_pos)
            editor.insert(fix.start_pos, fix.replacement)

            # Rehighlight
            if hasattr(editor, 'highlight_syntax'):
                editor.highlight_syntax()

        except Exception as e:
            print(f"Quick fix error: {e}")


class LintingStatusBar(tk.Frame):
    """Status bar showing linting results"""

    def __init__(self, parent):
        super().__init__(parent, bg=T.BG3, height=25)
        self.pack_propagate(False)

        self.error_label = tk.Label(
            self,
            text="✗ 0",
            bg=T.BG3,
            fg=T.BLOOD_LIGHT,
            font=(T.UI, 9)
        )
        self.error_label.pack(side=tk.LEFT, padx=5)

        self.warning_label = tk.Label(
            self,
            text="⚠ 0",
            bg=T.BG3,
            fg=T.AMBER,
            font=(T.UI, 9)
        )
        self.warning_label.pack(side=tk.LEFT, padx=5)

        self.info_label = tk.Label(
            self,
            text="ℹ 0",
            bg=T.BG3,
            fg=T.SIGNAL,
            font=(T.UI, 9)
        )
        self.info_label.pack(side=tk.LEFT, padx=5)

    def update_counts(self, messages):
        """Update counts from messages"""
        errors = sum(1 for m in messages if m.severity == 'error')
        warnings = sum(1 for m in messages if m.severity == 'warning')
        infos = sum(1 for m in messages if m.severity in ['info', 'hint'])

        self.error_label.config(text=f"✗ {errors}")
        self.warning_label.config(text=f"⚠ {warnings}")
        self.info_label.config(text=f"ℹ {infos}")


class CodeQualityPanel(tk.Frame):
    """Panel showing code quality metrics"""

    def __init__(self, parent):
        super().__init__(parent, bg=T.BG3)

        # Header
        tk.Label(self, text="📊 Code Quality", font=(T.UI, 10, 'bold'),
                bg=T.BG3, fg=T.BILE).pack(anchor='w', padx=10, pady=10)

        # Metrics
        self.metrics_frame = tk.Frame(self, bg=T.BG3)
        self.metrics_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        self.metric_labels = {}

        metrics = [
            ('lines', 'Lines of Code'),
            ('complexity', 'Complexity'),
            ('maintainability', 'Maintainability'),
            ('coverage', 'Test Coverage')
        ]

        for key, label in metrics:
            frame = tk.Frame(self.metrics_frame, bg=T.BG3)
            frame.pack(fill=tk.X, pady=5)

            tk.Label(frame, text=f"{label}:", bg=T.BG3, fg=T.TEXT,
                    font=(T.UI, 9), width=15, anchor='w').pack(side=tk.LEFT)

            value_label = tk.Label(frame, text="--", bg=T.BG3, fg=T.BILE,
                                  font=(T.UI, 9, 'bold'))
            value_label.pack(side=tk.LEFT)

            self.metric_labels[key] = value_label

    def update_metrics(self, content, language="Python"):
        """Update code quality metrics"""
        lines = len(content.split('\n'))
        self.metric_labels['lines'].config(text=str(lines))

        # Calculate complexity (basic)
        complexity = self._calculate_complexity(content, language)
        self.metric_labels['complexity'].config(text=str(complexity))

        # Maintainability index (0-100)
        maintainability = max(0, min(100, 100 - complexity * 2))
        color = T.BILE if maintainability > 70 else T.AMBER if maintainability > 40 else T.BLOOD_LIGHT
        self.metric_labels['maintainability'].config(text=f"{maintainability}%", fg=color)

        # Coverage (if available)
        self.metric_labels['coverage'].config(text="N/A")

    def _calculate_complexity(self, content, language):
        """Calculate cyclomatic complexity (basic)"""
        # Count decision points
        keywords = ['if', 'elif', 'else', 'for', 'while', 'and', 'or', 'try', 'except']
        complexity = 1  # Base complexity

        for keyword in keywords:
            complexity += content.count(f' {keyword} ')
            complexity += content.count(f'\t{keyword} ')

        return complexity
