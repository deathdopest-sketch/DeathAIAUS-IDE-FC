"""
Git Integration Panel
Provides git status, commit, push, pull, branch management
"""
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import threading
from components import death_theme as T


class GitPanel(ttk.Frame):
    """Git integration sidebar panel"""

    def __init__(self, parent, ide_instance):
        super().__init__(parent)
        self.ide = ide_instance
        self.repo_path = ide_instance.workspace_path if hasattr(ide_instance, 'workspace_path') else None
        self.current_branch = ""
        self.is_git_repo = False

        self._check_git_repo()
        self.setup_ui()

        # Auto-refresh every 5 seconds
        self.auto_refresh = True
        self._start_auto_refresh()

    def _check_git_repo(self):
        """Check if workspace is a git repository"""
        if not self.repo_path:
            return

        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            self.is_git_repo = result.returncode == 0
        except:
            self.is_git_repo = False

    def setup_ui(self):
        """Setup the Git panel UI"""
        # Header
        header = tk.Frame(self, bg=T.BG3, height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="🔀 Git", font=(T.UI, 12, 'bold'),
                fg=T.BILE, bg=T.BG3).pack(side=tk.LEFT, padx=10, pady=10)

        # Refresh button
        tk.Button(header, text="🔄", command=self.refresh_status,
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT).pack(side=tk.RIGHT, padx=5)

        if not self.is_git_repo:
            # Not a git repo - show init option
            no_git_frame = tk.Frame(self, bg=T.BG)
            no_git_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            tk.Label(no_git_frame, text="Not a Git repository",
                    bg=T.BG, fg=T.TEXT2, font=(T.UI, 10)).pack(pady=20)

            tk.Button(no_git_frame, text="Initialize Git Repository",
                     command=self.init_repo,
                     bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT,
                     font=(T.UI, 10), padx=20, pady=5).pack(pady=10)
            return

        # Branch info
        self.branch_frame = tk.Frame(self, bg=T.BG3)
        self.branch_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(self.branch_frame, text="Branch:", bg=T.BG3, fg=T.TEXT2,
                font=(T.UI, 9)).pack(side=tk.LEFT, padx=5)

        self.branch_label = tk.Label(self.branch_frame, text="main", bg=T.BG3,
                                     fg=T.BILE, font=(T.UI, 9, 'bold'))
        self.branch_label.pack(side=tk.LEFT)

        tk.Button(self.branch_frame, text="⚑", command=self.show_branches,
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT,
                 font=(T.UI, 8)).pack(side=tk.RIGHT, padx=5)

        # Changes section
        changes_label = tk.Frame(self, bg=T.BG3)
        changes_label.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(changes_label, text="Changes:", bg=T.BG3, fg=T.TEXT,
                font=(T.UI, 10, 'bold')).pack(side=tk.LEFT, padx=5)

        self.changes_count_label = tk.Label(changes_label, text="0", bg=T.BG3,
                                           fg=T.TEXT2, font=(T.UI, 9))
        self.changes_count_label.pack(side=tk.LEFT)

        # Changes list
        list_frame = tk.Frame(self, bg=T.BG)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.changes_list = tk.Listbox(
            list_frame,
            bg=T.BG,
            fg=T.TEXT,
            font=(T.MONO, 9),
            selectbackground=T.HOVER,
            selectforeground=T.TEXT,
            activestyle='none',
            yscrollcommand=scrollbar.set,
            relief=tk.FLAT
        )
        self.changes_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.changes_list.yview)

        # Bind double-click to view diff
        self.changes_list.bind('<Double-Button-1>', self.view_diff)

        # Commit section
        commit_frame = tk.Frame(self, bg=T.BG3)
        commit_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(commit_frame, text="Commit message:", bg=T.BG3, fg=T.TEXT,
                font=(T.UI, 9)).pack(anchor='w', padx=5, pady=2)

        self.commit_message = tk.Text(commit_frame, height=3, font=(T.UI, 9),
                                      bg=T.BG, fg=T.TEXT, insertbackground=T.TEXT,
                                      wrap=tk.WORD)
        self.commit_message.pack(fill=tk.X, padx=5, pady=2)

        # Commit buttons
        button_frame = tk.Frame(self, bg=T.BG3)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(button_frame, text="Stage All", command=self.stage_all,
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT,
                 font=(T.UI, 9), padx=10).pack(side=tk.LEFT, padx=2)

        tk.Button(button_frame, text="Commit", command=self.commit,
                 bg=T.BLOOD, fg=T.TEXT, relief=tk.FLAT,
                 font=(T.UI, 9, 'bold'), padx=10).pack(side=tk.LEFT, padx=2)

        # Actions
        actions_frame = tk.Frame(self, bg=T.BG3)
        actions_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(actions_frame, text="↓ Pull", command=self.pull,
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT,
                 font=(T.UI, 9), padx=15).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        tk.Button(actions_frame, text="↑ Push", command=self.push,
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT,
                 font=(T.UI, 9), padx=15).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        # Status bar
        self.git_status_label = tk.Label(self, text="Ready", bg=T.BG,
                                         fg=T.TEXT2, font=(T.UI, 8),
                                         anchor='w')
        self.git_status_label.pack(fill=tk.X, padx=5, pady=2)

        # Initial refresh
        self.refresh_status()

    def init_repo(self):
        """Initialize git repository"""
        if not self.repo_path:
            messagebox.showerror("Error", "No workspace path set")
            return

        try:
            subprocess.run(['git', 'init'], cwd=self.repo_path, check=True)
            self.is_git_repo = True
            messagebox.showinfo("Success", "Git repository initialized!")

            # Recreate UI
            for widget in self.winfo_children():
                widget.destroy()
            self.setup_ui()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize git: {e}")

    def refresh_status(self):
        """Refresh git status"""
        if not self.is_git_repo:
            return

        threading.Thread(target=self._refresh_status_thread, daemon=True).start()

    def _refresh_status_thread(self):
        """Background thread for refreshing status"""
        try:
            # Get current branch
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.current_branch = result.stdout.strip()
                self.branch_label.config(text=self.current_branch)

            # Get status
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                lines = [l for l in lines if l]  # Remove empty lines

                # Update UI on main thread
                self.after(0, self._update_changes_list, lines)
        except Exception as e:
            self.after(0, lambda: self.git_status_label.config(
                text=f"Error: {str(e)[:50]}", fg=T.BLOOD_LIGHT))

    def _update_changes_list(self, status_lines):
        """Update the changes list (called on main thread)"""
        self.changes_list.delete(0, tk.END)
        self.changes_count_label.config(text=str(len(status_lines)))

        for line in status_lines:
            if len(line) < 3:
                continue

            status_code = line[:2]
            filename = line[3:]

            # Color code based on status
            if 'M' in status_code:
                prefix = "📝 "
                color = T.AMBER  # Modified - orange
            elif 'A' in status_code:
                prefix = "✨ "
                color = T.BILE  # Added - green
            elif 'D' in status_code:
                prefix = "🗑️ "
                color = T.BLOOD_LIGHT  # Deleted - red
            elif '?' in status_code:
                prefix = "❓ "
                color = T.TEXT2  # Untracked - gray
            else:
                prefix = "📄 "
                color = T.TEXT

            display_text = f"{prefix}{filename}"
            self.changes_list.insert(tk.END, display_text)
            self.changes_list.itemconfig(tk.END, fg=color)

        if status_lines:
            self.git_status_label.config(text=f"{len(status_lines)} changes", fg=T.BILE)
        else:
            self.git_status_label.config(text="Working tree clean", fg=T.TEXT2)

    def view_diff(self, event=None):
        """View diff for selected file"""
        selection = self.changes_list.curselection()
        if not selection:
            return

        # Get filename (remove emoji prefix)
        display_text = self.changes_list.get(selection[0])
        filename = display_text.split(' ', 1)[1] if ' ' in display_text else display_text

        # Get diff
        try:
            result = subprocess.run(
                ['git', 'diff', 'HEAD', filename],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout:
                self._show_diff_dialog(filename, result.stdout)
            else:
                # File might be untracked
                result = subprocess.run(
                    ['git', 'diff', filename],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0 and result.stdout:
                    self._show_diff_dialog(filename, result.stdout)
                else:
                    messagebox.showinfo("Info", "No diff available (untracked or unchanged file)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get diff: {e}")

    def _show_diff_dialog(self, filename, diff_text):
        """Show diff in a dialog"""
        dialog = tk.Toplevel(self)
        dialog.title(f"Diff: {filename}")
        dialog.geometry("800x600")
        dialog.configure(bg=T.BG)

        # Diff viewer
        text = tk.Text(dialog, font=(T.MONO, 9), bg=T.BG, fg=T.TEXT,
                      wrap=tk.NONE)
        text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbars
        h_scroll = tk.Scrollbar(text, orient=tk.HORIZONTAL, command=text.xview)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll = tk.Scrollbar(text, command=text.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        # Configure tags for diff coloring
        text.tag_configure("added", foreground=T.BILE, background=T.BILE_DEEP)
        text.tag_configure("removed", foreground=T.BLOOD_LIGHT, background=T.BLOOD_DEEP)
        text.tag_configure("header", foreground=T.SIGNAL, font=(T.MONO, 9, 'bold'))

        # Insert and color diff
        for line in diff_text.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                text.insert(tk.END, line + '\n', "added")
            elif line.startswith('-') and not line.startswith('---'):
                text.insert(tk.END, line + '\n', "removed")
            elif line.startswith('@@') or line.startswith('diff') or line.startswith('index'):
                text.insert(tk.END, line + '\n', "header")
            else:
                text.insert(tk.END, line + '\n')

        text.config(state='disabled')

    def stage_all(self):
        """Stage all changes"""
        try:
            subprocess.run(['git', 'add', '.'], cwd=self.repo_path, check=True)
            self.git_status_label.config(text="All changes staged", fg=T.BILE)
            self.refresh_status()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stage files: {e}")

    def commit(self):
        """Commit staged changes"""
        message = self.commit_message.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Warning", "Please enter a commit message")
            return

        try:
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.git_status_label.config(text="Committed successfully", fg=T.BILE)
                self.commit_message.delete("1.0", tk.END)
                self.refresh_status()
            else:
                messagebox.showerror("Error", f"Commit failed:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to commit: {e}")

    def pull(self):
        """Pull from remote"""
        self.git_status_label.config(text="Pulling...", fg=T.SIGNAL)
        threading.Thread(target=self._pull_thread, daemon=True).start()

    def _pull_thread(self):
        """Background pull operation"""
        try:
            result = subprocess.run(
                ['git', 'pull'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                self.after(0, lambda: self.git_status_label.config(
                    text="Pull successful", fg=T.BILE))
                self.after(0, self.refresh_status)
            else:
                self.after(0, lambda: messagebox.showerror(
                    "Error", f"Pull failed:\n{result.stderr}"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Pull failed: {e}"))

    def push(self):
        """Push to remote"""
        self.git_status_label.config(text="Pushing...", fg=T.SIGNAL)
        threading.Thread(target=self._push_thread, daemon=True).start()

    def _push_thread(self):
        """Background push operation"""
        try:
            result = subprocess.run(
                ['git', 'push'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                self.after(0, lambda: self.git_status_label.config(
                    text="Push successful", fg=T.BILE))
            else:
                self.after(0, lambda: messagebox.showerror(
                    "Error", f"Push failed:\n{result.stderr}"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Push failed: {e}"))

    def show_branches(self):
        """Show branch management dialog"""
        dialog = tk.Toplevel(self)
        dialog.title("Branches")
        dialog.geometry("400x500")
        dialog.configure(bg=T.BG3)

        # Branch list
        tk.Label(dialog, text="Branches:", bg=T.BG3, fg=T.TEXT,
                font=(T.UI, 10, 'bold')).pack(anchor='w', padx=10, pady=5)

        list_frame = tk.Frame(dialog, bg=T.BG)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        branch_list = tk.Listbox(list_frame, bg=T.BG, fg=T.TEXT,
                                font=(T.MONO, 9), yscrollcommand=scrollbar.set)
        branch_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=branch_list.yview)

        # Get branches
        try:
            result = subprocess.run(
                ['git', 'branch', '-a'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for branch in result.stdout.split('\n'):
                    branch = branch.strip()
                    if branch:
                        is_current = branch.startswith('*')
                        branch_name = branch.lstrip('* ')
                        display = f"{'→ ' if is_current else '  '}{branch_name}"
                        branch_list.insert(tk.END, display)
                        if is_current:
                            branch_list.itemconfig(tk.END, fg=T.BILE)
        except:
            pass

        # New branch
        new_branch_frame = tk.Frame(dialog, bg=T.BG3)
        new_branch_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(new_branch_frame, text="New branch:", bg=T.BG3, fg=T.TEXT).pack(anchor='w')

        new_branch_var = tk.StringVar()
        tk.Entry(new_branch_frame, textvariable=new_branch_var,
                bg=T.BG, fg=T.TEXT).pack(fill=tk.X, pady=5)

        def create_branch():
            name = new_branch_var.get().strip()
            if name:
                try:
                    subprocess.run(['git', 'branch', name], cwd=self.repo_path, check=True)
                    messagebox.showinfo("Success", f"Branch '{name}' created")
                    dialog.destroy()
                    self.refresh_status()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create branch: {e}")

        tk.Button(new_branch_frame, text="Create Branch", command=create_branch,
                 bg=T.BLOOD, fg=T.TEXT, relief=tk.FLAT).pack()

    def _start_auto_refresh(self):
        """Start auto-refresh timer"""
        if self.auto_refresh and self.is_git_repo:
            self.refresh_status()
            self.after(5000, self._start_auto_refresh)
