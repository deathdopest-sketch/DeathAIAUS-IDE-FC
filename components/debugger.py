"""
Integrated Debugger
Python debugger with breakpoints, step through, and variable inspection
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import queue
import os
import sys
import json
from components import death_theme as T


class DebugSession:
    """Manages a debug session"""

    def __init__(self, file_path, working_dir=None):
        self.file_path = file_path
        self.working_dir = working_dir or os.path.dirname(file_path)
        self.process = None
        self.is_running = False
        self.breakpoints = set()  # Set of line numbers
        self.current_line = None
        self.variables = {}
        self.output_queue = queue.Queue()

    def start(self):
        """Start debug session"""
        self.is_running = True
        # TODO: Implement actual debugger integration (pdb, etc.)

    def stop(self):
        """Stop debug session"""
        self.is_running = False
        if self.process:
            self.process.terminate()

    def add_breakpoint(self, line_num):
        """Add breakpoint"""
        self.breakpoints.add(line_num)

    def remove_breakpoint(self, line_num):
        """Remove breakpoint"""
        self.breakpoints.discard(line_num)

    def step_over(self):
        """Step over current line"""
        # TODO: Implement
        pass

    def step_into(self):
        """Step into function"""
        # TODO: Implement
        pass

    def step_out(self):
        """Step out of function"""
        # TODO: Implement
        pass

    def continue_execution(self):
        """Continue to next breakpoint"""
        # TODO: Implement
        pass


class DebuggerPanel(tk.Frame):
    """Debugger control panel"""

    def __init__(self, parent, ide_instance):
        super().__init__(parent, bg=T.BG3)
        self.ide = ide_instance
        self.debug_session = None
        self.breakpoint_markers = {}  # editor -> {line -> marker_id}

        self.setup_ui()

    def setup_ui(self):
        """Setup debugger UI"""
        # Header
        header = tk.Frame(self, bg=T.BG, height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="🐛 Debugger", font=(T.UI, 11, 'bold'),
                fg=T.BILE, bg=T.BG).pack(side=tk.LEFT, padx=10, pady=10)

        # Control buttons
        btn_frame = tk.Frame(self, bg=T.BG3)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        self.start_btn = tk.Button(
            btn_frame,
            text="▶ Start",
            command=self.start_debug,
            bg=T.BLOOD,
            fg=T.TEXT,
            relief=tk.FLAT,
            padx=10
        )
        self.start_btn.pack(side=tk.LEFT, padx=2)

        self.stop_btn = tk.Button(
            btn_frame,
            text="⬛ Stop",
            command=self.stop_debug,
            bg=T.BLOOD,
            fg=T.TEXT,
            relief=tk.FLAT,
            padx=10,
            state='disabled'
        )
        self.stop_btn.pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame,
            text="⤵ Step Over",
            command=self.step_over,
            bg=T.HOVER,
            fg=T.TEXT,
            relief=tk.FLAT,
            padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame,
            text="↴ Step Into",
            command=self.step_into,
            bg=T.HOVER,
            fg=T.TEXT,
            relief=tk.FLAT,
            padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame,
            text="↑ Step Out",
            command=self.step_out,
            bg=T.HOVER,
            fg=T.TEXT,
            relief=tk.FLAT,
            padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame,
            text="▶▶ Continue",
            command=self.continue_debug,
            bg=T.BLOOD,
            fg=T.TEXT,
            relief=tk.FLAT,
            padx=10
        ).pack(side=tk.LEFT, padx=2)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Variables tab
        var_frame = tk.Frame(self.notebook, bg=T.BG)
        self.notebook.add(var_frame, text="Variables")

        self.var_tree = ttk.Treeview(
            var_frame,
            columns=('value', 'type'),
            show='tree headings'
        )
        self.var_tree.heading('#0', text='Name')
        self.var_tree.heading('value', text='Value')
        self.var_tree.heading('type', text='Type')
        self.var_tree.pack(fill=tk.BOTH, expand=True)

        # Call stack tab
        stack_frame = tk.Frame(self.notebook, bg=T.BG)
        self.notebook.add(stack_frame, text="Call Stack")

        self.stack_list = tk.Listbox(
            stack_frame,
            bg=T.BG,
            fg=T.TEXT,
            font=(T.MONO, 9)
        )
        self.stack_list.pack(fill=tk.BOTH, expand=True)

        # Breakpoints tab
        bp_frame = tk.Frame(self.notebook, bg=T.BG)
        self.notebook.add(bp_frame, text="Breakpoints")

        self.bp_list = tk.Listbox(
            bp_frame,
            bg=T.BG,
            fg=T.TEXT,
            font=(T.MONO, 9)
        )
        self.bp_list.pack(fill=tk.BOTH, expand=True)
        self.bp_list.bind('<Double-Button-1>', self.jump_to_breakpoint)

        # Output tab
        output_frame = tk.Frame(self.notebook, bg=T.BG)
        self.notebook.add(output_frame, text="Output")

        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            bg=T.BG,
            fg=T.TEXT,
            font=(T.MONO, 9),
            state='disabled'
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def setup_editor_debugging(self, editor, file_path=""):
        """Setup debugging features on editor"""
        # Bind click on line number area for breakpoints
        if hasattr(editor, 'line_numbers'):
            editor.line_numbers.bind('<Button-1>',
                lambda e: self._toggle_breakpoint_click(editor, e))

        # Store editor reference
        if editor not in self.breakpoint_markers:
            self.breakpoint_markers[editor] = {}

    def _toggle_breakpoint_click(self, editor, event):
        """Toggle breakpoint on line number click"""
        try:
            # Get line number from click position
            index = editor.line_numbers.index(f"@{event.x},{event.y}")
            line_num = int(index.split('.')[0])

            self.toggle_breakpoint(editor, line_num)

        except Exception as e:
            print(f"Breakpoint toggle error: {e}")

    def toggle_breakpoint(self, editor, line_num):
        """Toggle breakpoint at line"""
        if editor not in self.breakpoint_markers:
            self.breakpoint_markers[editor] = {}

        if line_num in self.breakpoint_markers[editor]:
            # Remove breakpoint
            self._remove_breakpoint_marker(editor, line_num)
            if self.debug_session:
                self.debug_session.remove_breakpoint(line_num)
        else:
            # Add breakpoint
            self._add_breakpoint_marker(editor, line_num)
            if self.debug_session:
                self.debug_session.add_breakpoint(line_num)

        # Update breakpoint list
        self.update_breakpoint_list()

    def _add_breakpoint_marker(self, editor, line_num):
        """Add breakpoint visual marker"""
        # Configure breakpoint tag if not exists
        if 'breakpoint' not in editor.tag_names():
            editor.tag_configure('breakpoint', background=T.BLOOD)

        # Add tag to line
        editor.tag_add('breakpoint', f"{line_num}.0", f"{line_num}.end")

        # Store marker
        self.breakpoint_markers[editor][line_num] = True

        # Add marker to line number area
        if hasattr(editor, 'line_numbers'):
            # TODO: Add visual breakpoint indicator

            pass

    def _remove_breakpoint_marker(self, editor, line_num):
        """Remove breakpoint visual marker"""
        # Remove tag
        editor.tag_remove('breakpoint', f"{line_num}.0", f"{line_num}.end")

        # Remove from storage
        if line_num in self.breakpoint_markers[editor]:
            del self.breakpoint_markers[editor][line_num]

    def update_breakpoint_list(self):
        """Update breakpoint list display"""
        self.bp_list.delete(0, tk.END)

        for editor, breakpoints in self.breakpoint_markers.items():
            for line_num in sorted(breakpoints.keys()):
                # Get file path
                file_path = "current_file"  # TODO: Get actual file path
                self.bp_list.insert(tk.END, f"🔴 {file_path}:{line_num}")

    def jump_to_breakpoint(self, event=None):
        """Jump to selected breakpoint"""
        selection = self.bp_list.curselection()
        if not selection:
            return

        # Parse breakpoint info
        bp_text = self.bp_list.get(selection[0])
        # Format: "🔴 file:line"
        parts = bp_text.split(':')
        if len(parts) >= 2:
            try:
                line_num = int(parts[-1])
                # TODO: Jump to line in editor
            except:
                pass

    def start_debug(self):
        """Start debugging current file"""
        if not hasattr(self.ide, 'current_file') or not self.ide.current_file:
            self.write_output("No file open for debugging\n")
            return

        file_path = self.ide.current_file

        # Save file first
        if hasattr(self.ide, 'save_file'):
            self.ide.save_file()

        # Create debug session
        self.debug_session = DebugSession(file_path)

        # Transfer breakpoints
        for editor, breakpoints in self.breakpoint_markers.items():
            for line_num in breakpoints.keys():
                self.debug_session.add_breakpoint(line_num)

        # Run script with debugger
        self._run_with_debugger(file_path)

        # Update UI
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')

        self.write_output(f"🐛 Debugging: {os.path.basename(file_path)}\n")

    def _run_with_debugger(self, file_path):
        """Run script with Python debugger"""
        def run_thread():
            try:
                # Simple execution (can be enhanced with pdb integration)
                result = subprocess.run(
                    [sys.executable, file_path],
                    capture_output=True,
                    text=True,
                    cwd=os.path.dirname(file_path),
                    timeout=60
                )

                self.after(0, self.write_output, result.stdout)
                if result.stderr:
                    self.after(0, self.write_output, f"\nErrors:\n{result.stderr}")

                self.after(0, self.write_output, f"\n✓ Process exited with code {result.returncode}\n")

            except subprocess.TimeoutExpired:
                self.after(0, self.write_output, "\n⚠ Process timeout\n")
            except Exception as e:
                self.after(0, self.write_output, f"\n✗ Error: {e}\n")
            finally:
                self.after(0, self.stop_debug)

        threading.Thread(target=run_thread, daemon=True).start()

    def stop_debug(self):
        """Stop debugging"""
        if self.debug_session:
            self.debug_session.stop()
            self.debug_session = None

        # Update UI
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')

        self.write_output("\n🛑 Debugging stopped\n")

    def step_over(self):
        """Step over current line"""
        if self.debug_session:
            self.debug_session.step_over()

    def step_into(self):
        """Step into function"""
        if self.debug_session:
            self.debug_session.step_into()

    def step_out(self):
        """Step out of function"""
        if self.debug_session:
            self.debug_session.step_out()

    def continue_debug(self):
        """Continue execution"""
        if self.debug_session:
            self.debug_session.continue_execution()

    def write_output(self, text):
        """Write to output console"""
        self.output_text.config(state='normal')
        self.output_text.insert('end', text)
        self.output_text.see('end')
        self.output_text.config(state='disabled')

    def update_variables(self, variables):
        """Update variable display"""
        # Clear tree
        for item in self.var_tree.get_children():
            self.var_tree.delete(item)

        # Add variables
        for name, value in variables.items():
            self.var_tree.insert(
                '',
                'end',
                text=name,
                values=(str(value), type(value).__name__)
            )

    def update_call_stack(self, stack):
        """Update call stack display"""
        self.stack_list.delete(0, tk.END)
        for frame in stack:
            self.stack_list.insert(tk.END, frame)


class QuickRunPanel(tk.Frame):
    """Quick run panel for scripts"""

    def __init__(self, parent, ide_instance):
        super().__init__(parent, bg=T.BG3)
        self.ide = ide_instance

        # Run button
        tk.Button(
            self,
            text="▶ Run",
            command=self.run_current,
            bg=T.BLOOD,
            fg=T.TEXT,
            relief=tk.FLAT,
            font=(T.UI, 9, 'bold'),
            padx=15
        ).pack(side=tk.LEFT, padx=5)

        # Debug button
        tk.Button(
            self,
            text="🐛 Debug",
            command=self.debug_current,
            bg=T.HOVER,
            fg=T.TEXT,
            relief=tk.FLAT,
            font=(T.UI, 9),
            padx=15
        ).pack(side=tk.LEFT, padx=5)

        # Run with args
        tk.Label(self, text="Args:", bg=T.BG3, fg=T.TEXT,
                font=(T.UI, 9)).pack(side=tk.LEFT, padx=5)

        self.args_var = tk.StringVar()
        tk.Entry(
            self,
            textvariable=self.args_var,
            bg=T.BG,
            fg=T.TEXT,
            font=(T.UI, 9),
            width=20
        ).pack(side=tk.LEFT, padx=5)

    def run_current(self):
        """Run current file"""
        if hasattr(self.ide, 'current_file') and self.ide.current_file:
            # Save first
            if hasattr(self.ide, 'save_file'):
                self.ide.save_file()

            # Run in terminal
            if hasattr(self.ide, 'terminal_tabs'):
                cmd = f'python "{self.ide.current_file}" {self.args_var.get()}'
                self.ide.terminal_tabs.execute_in_current(cmd)

    def debug_current(self):
        """Debug current file"""
        if hasattr(self.ide, 'debugger_panel'):
            self.ide.debugger_panel.start_debug()
