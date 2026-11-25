"""
Interactive Terminal Tabs
Multiple terminal sessions with tab management
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import queue
import os
import sys
from components import death_theme as T


class TerminalTab:
    """Single terminal session"""

    def __init__(self, parent, tab_id, working_dir=None):
        self.parent = parent
        self.tab_id = tab_id
        self.working_dir = working_dir or os.getcwd()
        self.process = None
        self.output_queue = queue.Queue()
        self.is_running = False

        self.setup_ui()
        self.start_shell()

    def setup_ui(self):
        """Setup terminal UI"""
        self.frame = tk.Frame(self.parent, bg=T.BG)

        # Output area
        output_frame = tk.Frame(self.frame, bg=T.BG)
        output_frame.pack(fill=tk.BOTH, expand=True)

        self.output = scrolledtext.ScrolledText(
            output_frame,
            bg=T.VOID,
            fg=T.TEXT,
            font=(T.MONO, 10),
            insertbackground=T.TEXT,
            wrap=tk.CHAR,
            state='disabled'
        )
        self.output.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Configure tags for colored output
        self.output.tag_configure("error", foreground=T.BLOOD_LIGHT)
        self.output.tag_configure("success", foreground=T.BILE)
        self.output.tag_configure("warning", foreground=T.AMBER)
        self.output.tag_configure("info", foreground=T.SIGNAL)
        self.output.tag_configure("prompt", foreground=T.BILE, font=(T.MONO, 10, 'bold'))

        # Input area
        input_frame = tk.Frame(self.frame, bg=T.BG3)
        input_frame.pack(fill=tk.X, padx=2, pady=2)

        # Prompt label
        self.prompt_label = tk.Label(input_frame, text="$", bg=T.BG3,
                                     fg=T.BILE, font=(T.MONO, 10, 'bold'))
        self.prompt_label.pack(side=tk.LEFT, padx=(5, 2))

        # Input field
        self.input_field = tk.Entry(
            input_frame,
            bg=T.BG,
            fg=T.TEXT,
            font=(T.MONO, 10),
            insertbackground=T.TEXT,
            relief=tk.FLAT
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        self.input_field.bind('<Return>', self.execute_command)
        self.input_field.bind('<Up>', self.history_up)
        self.input_field.bind('<Down>', self.history_down)
        self.input_field.bind('<Control-c>', self.interrupt_process)

        # Command history
        self.command_history = []
        self.history_index = -1

        # Send button
        tk.Button(input_frame, text="▶", command=lambda: self.execute_command(None),
                 bg=T.BLOOD, fg=T.TEXT, relief=tk.FLAT, padx=10).pack(side=tk.RIGHT, padx=2)

    def start_shell(self):
        """Start shell process"""
        self.is_running = True

        # Determine shell based on platform
        if sys.platform == 'win32':
            shell_cmd = 'cmd.exe'
        else:
            shell_cmd = os.environ.get('SHELL', '/bin/bash')

        try:
            self.process = subprocess.Popen(
                shell_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.working_dir,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Start output reader threads
            threading.Thread(target=self._read_output, args=(self.process.stdout,), daemon=True).start()
            threading.Thread(target=self._read_output, args=(self.process.stderr, "error"), daemon=True).start()
            threading.Thread(target=self._update_output, daemon=True).start()

            # Initial prompt
            self.write_output(f"Terminal {self.tab_id} started in {self.working_dir}\n", "info")
            self.write_output(f"$ ", "prompt")

        except Exception as e:
            self.write_output(f"Failed to start shell: {e}\n", "error")

    def _read_output(self, pipe, tag=""):
        """Read output from process"""
        try:
            for line in iter(pipe.readline, ''):
                if line:
                    self.output_queue.put((line, tag))
        except:
            pass

    def _update_output(self):
        """Update output display (runs in background)"""
        while self.is_running:
            try:
                line, tag = self.output_queue.get(timeout=0.1)
                self.frame.after(0, self._append_output, line, tag)
            except queue.Empty:
                continue
            except:
                break

    def _append_output(self, text, tag=""):
        """Append text to output (must run on main thread)"""
        self.output.config(state='normal')
        if tag:
            self.output.insert(tk.END, text, tag)
        else:
            self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.config(state='disabled')

    def write_output(self, text, tag=""):
        """Write text to output"""
        self.output.config(state='normal')
        if tag:
            self.output.insert(tk.END, text, tag)
        else:
            self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.config(state='disabled')

    def execute_command(self, event=None):
        """Execute command from input field"""
        command = self.input_field.get().strip()
        if not command:
            return "break"

        # Clear input
        self.input_field.delete(0, tk.END)

        # Add to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)

        # Show command in output
        self.write_output(f"{command}\n", "success")

        # Handle special commands
        if command.startswith('cd '):
            self._change_directory(command[3:].strip())
        elif command == 'clear':
            self.clear_output()
        elif command == 'exit':
            self.close()
        else:
            # Send to shell
            self._send_to_shell(command)

        return "break"

    def _send_to_shell(self, command):
        """Send command to shell process"""
        if self.process and self.process.poll() is None:
            try:
                self.process.stdin.write(command + '\n')
                self.process.stdin.flush()
            except Exception as e:
                self.write_output(f"Error executing command: {e}\n", "error")

    def _change_directory(self, path):
        """Change working directory"""
        try:
            if path.startswith('"') and path.endswith('"'):
                path = path[1:-1]
            elif path.startswith("'") and path.endswith("'"):
                path = path[1:-1]

            new_dir = os.path.abspath(os.path.join(self.working_dir, path))
            if os.path.isdir(new_dir):
                self.working_dir = new_dir
                os.chdir(new_dir)
                if self.process:
                    self._send_to_shell(f'cd "{new_dir}"')
                self.write_output(f"Changed directory to: {new_dir}\n", "info")
            else:
                self.write_output(f"Directory not found: {path}\n", "error")
        except Exception as e:
            self.write_output(f"Failed to change directory: {e}\n", "error")

    def history_up(self, event=None):
        """Navigate command history up"""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.input_field.delete(0, tk.END)
            self.input_field.insert(0, self.command_history[self.history_index])
        return "break"

    def history_down(self, event=None):
        """Navigate command history down"""
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.input_field.delete(0, tk.END)
            self.input_field.insert(0, self.command_history[self.history_index])
        elif self.history_index >= len(self.command_history) - 1:
            self.history_index = len(self.command_history)
            self.input_field.delete(0, tk.END)
        return "break"

    def interrupt_process(self, event=None):
        """Interrupt running process (Ctrl+C)"""
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.write_output("\n^C\n", "warning")
            except:
                pass
        return "break"

    def clear_output(self):
        """Clear terminal output"""
        self.output.config(state='normal')
        self.output.delete("1.0", tk.END)
        self.output.config(state='disabled')
        self.write_output("$ ", "prompt")

    def close(self):
        """Close terminal and cleanup"""
        self.is_running = False
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                self.process.kill()


class TerminalTabs(ttk.Frame):
    """Terminal tabs manager"""

    def __init__(self, parent, ide_instance):
        super().__init__(parent)
        self.ide = ide_instance
        self.terminals = {}  # tab_id -> TerminalTab
        self.tab_id_counter = 1
        self.current_tab = None

        self.setup_ui()

    def setup_ui(self):
        """Setup terminal tabs UI"""
        # Tab bar
        self.tab_bar = tk.Frame(self, bg=T.BG3, height=35)
        self.tab_bar.pack(fill=tk.X, side=tk.TOP)
        self.tab_bar.pack_propagate(False)

        # New terminal button
        new_btn = tk.Button(self.tab_bar, text="+ Terminal", command=self.new_terminal,
                           bg=T.HOVER, fg=T.BILE, relief=tk.FLAT,
                           font=(T.UI, 9), padx=10)
        new_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Terminal container
        self.terminal_container = tk.Frame(self, bg=T.BG)
        self.terminal_container.pack(fill=tk.BOTH, expand=True)

        # Create initial terminal
        self.new_terminal()

    def new_terminal(self, working_dir=None):
        """Create a new terminal tab"""
        tab_id = self.tab_id_counter
        self.tab_id_counter += 1

        # Use workspace path or current dir
        if not working_dir:
            if hasattr(self.ide, 'workspace_path') and self.ide.workspace_path:
                working_dir = self.ide.workspace_path
            else:
                working_dir = os.getcwd()

        # Create tab button
        tab_frame = tk.Frame(self.tab_bar, bg=T.HOVER, bd=1, relief=tk.RAISED)
        tab_frame.pack(side=tk.LEFT, padx=1, pady=2)

        # Tab label
        tab_label = tk.Label(tab_frame, text=f"Terminal {tab_id}",
                            bg=T.HOVER, fg=T.TEXT,
                            font=(T.UI, 9), padx=10, pady=5, cursor='hand2')
        tab_label.pack(side=tk.LEFT)
        tab_label.bind('<Button-1>', lambda e: self.switch_to_tab(tab_id))

        # Close button
        close_btn = tk.Label(tab_frame, text="×", bg=T.HOVER, fg=T.TEXT2,
                            font=(T.UI, 12, 'bold'), padx=5, cursor='hand2')
        close_btn.pack(side=tk.LEFT)
        close_btn.bind('<Button-1>', lambda e: self.close_tab(tab_id))
        close_btn.bind('<Enter>', lambda e: close_btn.config(fg=T.BLOOD_LIGHT))
        close_btn.bind('<Leave>', lambda e: close_btn.config(fg=T.TEXT2))

        # Create terminal
        terminal = TerminalTab(self.terminal_container, tab_id, working_dir)

        # Store tab
        self.terminals[tab_id] = {
            'frame': tab_frame,
            'label': tab_label,
            'terminal': terminal
        }

        # Switch to new tab
        self.switch_to_tab(tab_id)

    def switch_to_tab(self, tab_id):
        """Switch to a different terminal tab"""
        if tab_id not in self.terminals:
            return

        # Hide current terminal
        if self.current_tab and self.current_tab in self.terminals:
            self.terminals[self.current_tab]['terminal'].frame.pack_forget()

        # Update tab appearances
        for tid, tab_data in self.terminals.items():
            if tid == tab_id:
                # Active tab
                tab_data['frame'].config(bg=T.BG, relief=tk.SUNKEN)
                tab_data['label'].config(bg=T.BG, fg=T.TEXT)
            else:
                # Inactive tab
                tab_data['frame'].config(bg=T.HOVER, relief=tk.RAISED)
                tab_data['label'].config(bg=T.HOVER, fg=T.TEXT)

        # Show new terminal
        self.current_tab = tab_id
        self.terminals[tab_id]['terminal'].frame.pack(fill=tk.BOTH, expand=True)
        self.terminals[tab_id]['terminal'].input_field.focus()

    def close_tab(self, tab_id):
        """Close a terminal tab"""
        if tab_id not in self.terminals:
            return

        tab_data = self.terminals[tab_id]

        # Close terminal
        tab_data['terminal'].close()

        # Remove tab UI
        tab_data['frame'].destroy()
        tab_data['terminal'].frame.destroy()
        del self.terminals[tab_id]

        # Switch to another tab if available
        if self.terminals:
            next_tab_id = list(self.terminals.keys())[0]
            self.switch_to_tab(next_tab_id)
        else:
            self.current_tab = None

    def execute_in_current(self, command):
        """Execute command in current terminal"""
        if self.current_tab and self.current_tab in self.terminals:
            terminal = self.terminals[self.current_tab]['terminal']
            terminal.input_field.delete(0, tk.END)
            terminal.input_field.insert(0, command)
            terminal.execute_command()

    def get_current_terminal(self):
        """Get current terminal instance"""
        if self.current_tab and self.current_tab in self.terminals:
            return self.terminals[self.current_tab]['terminal']
        return None


class QuickCommandPanel(tk.Frame):
    """Quick command shortcuts panel"""

    def __init__(self, parent, terminal_tabs):
        super().__init__(parent, bg=T.BG3)
        self.terminal_tabs = terminal_tabs

        tk.Label(self, text="Quick Commands:", bg=T.BG3, fg=T.TEXT,
                font=(T.UI, 9, 'bold')).pack(side=tk.LEFT, padx=10)

        # Common commands
        commands = [
            ("📁 ls/dir", "dir" if sys.platform == 'win32' else "ls -la"),
            ("🐍 Python", "python --version"),
            ("📦 pip", "pip list"),
            ("🔧 Git Status", "git status"),
            ("🧹 Clear", "clear" if sys.platform != 'win32' else "cls"),
        ]

        for label, cmd in commands:
            btn = tk.Button(self, text=label,
                           command=lambda c=cmd: self.run_command(c),
                           bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT,
                           font=(T.UI, 8), padx=8, pady=2)
            btn.pack(side=tk.LEFT, padx=2)

    def run_command(self, command):
        """Run command in current terminal"""
        self.terminal_tabs.execute_in_current(command)
