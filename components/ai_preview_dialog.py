"""
AI Preview Dialog - Show changes BEFORE applying them

Shows:
- Side-by-side diff of proposed changes
- Which files will be modified
- What exactly will change
- Approve/Reject buttons

Prevents AI from destroying your code without warning!

Part of DeathAIAUS IDE FC - The Honest AI IDE
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import difflib
import os
from components import death_theme as T


class AIPreviewDialog(tk.Toplevel):
    """Preview AI-proposed changes before applying"""
    
    def __init__(self, parent, file_path, original_content, proposed_content, callback=None):
        super().__init__(parent)
        self.file_path = file_path
        self.original_content = original_content
        self.proposed_content = proposed_content
        self.callback = callback
        self.approved = False
        
        self.title(f"Preview Changes: {os.path.basename(file_path)}")
        self.geometry("1200x700")
        self.configure(bg=T.BG)
        
        # Make modal
        self.grab_set()
        self.transient(parent)
        
        self.setup_ui()
        self.show_diff()
    
    def setup_ui(self):
        """Setup UI"""
        # Header
        header = tk.Frame(self, bg=T.BG2, height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Title
        title_frame = tk.Frame(header, bg=T.BG2)
        title_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Label(title_frame, text="⚠️ AI Proposed Changes",
                font=(T.UI, 14, 'bold'),
                fg=T.AMBER, bg=T.BG2).pack(anchor=tk.W)
        
        tk.Label(title_frame, text=f"File: {self.file_path}",
                font=(T.UI, 10),
                fg=T.TEXT, bg=T.BG2).pack(anchor=tk.W)
        
        # Action buttons
        button_frame = tk.Frame(header, bg=T.BG2)
        button_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Approve button (green)
        self.approve_btn = tk.Button(button_frame, text="✓ Apply Changes",
                                     command=self.approve_changes,
                                     bg=T.BLOOD, fg=T.TEXT,
                                     font=(T.UI, 12, 'bold'),
                                     relief=tk.FLAT, padx=30, pady=10,
                                     cursor='hand2')
        self.approve_btn.pack(side=tk.LEFT, padx=5)
        
        # Reject button (red)
        reject_btn = tk.Button(button_frame, text="✗ Reject Changes",
                               command=self.reject_changes,
                               bg=T.BLOOD, fg=T.TEXT,
                               font=(T.UI, 12, 'bold'),
                               relief=tk.FLAT, padx=30, pady=10,
                               cursor='hand2')
        reject_btn.pack(side=tk.LEFT, padx=5)
        
        # Info bar
        info_bar = tk.Frame(self, bg=T.BG3, height=40)
        info_bar.pack(fill=tk.X)
        info_bar.pack_propagate(False)
        
        self.info_label = tk.Label(info_bar, text="Review changes below...",
                                   font=(T.UI, 10),
                                   fg=T.TEXT, bg=T.BG3)
        self.info_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Diff view container
        diff_container = tk.Frame(self, bg=T.BG)
        diff_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Side-by-side layout
        # Original (left)
        left_frame = tk.LabelFrame(diff_container, text="Original",
                                   bg=T.BG2, fg=T.TEXT,
                                   font=(T.UI, 10, 'bold'))
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.original_text = scrolledtext.ScrolledText(
            left_frame,
            wrap=tk.NONE,
            font=(T.MONO, 10),
            bg=T.BG,
            fg=T.TEXT,
            insertbackground=T.TEXT,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.original_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Proposed (right)
        right_frame = tk.LabelFrame(diff_container, text="Proposed Changes",
                                    bg=T.BG2, fg=T.TEXT,
                                    font=(T.UI, 10, 'bold'))
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.proposed_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.NONE,
            font=(T.MONO, 10),
            bg=T.BG,
            fg=T.TEXT,
            insertbackground=T.TEXT,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.proposed_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure tags for highlighting
        self.original_text.tag_config('delete', background=T.BLOOD_DEEP, foreground=T.BLOOD_LIGHT)
        self.proposed_text.tag_config('insert', background=T.BILE_DEEP, foreground=T.BILE_LIGHT)
        self.proposed_text.tag_config('replace', background=T.BILE_DEEP, foreground=T.BILE_LIGHT)
        
        # Keyboard shortcuts
        self.bind('<Return>', lambda e: self.approve_changes())
        self.bind('<Escape>', lambda e: self.reject_changes())
        self.bind('<Control-a>', lambda e: self.approve_changes())
        self.bind('<Control-r>', lambda e: self.reject_changes())
    
    def show_diff(self):
        """Show the diff between original and proposed"""
        original_lines = self.original_content.splitlines(keepends=True)
        proposed_lines = self.proposed_content.splitlines(keepends=True)
        
        # Calculate diff
        differ = difflib.Differ()
        diff = list(differ.compare(original_lines, proposed_lines))
        
        # Count changes
        adds = sum(1 for line in diff if line.startswith('+ '))
        dels = sum(1 for line in diff if line.startswith('- '))
        
        # Update info label
        self.info_label.config(
            text=f"📊 Changes: +{adds} additions, -{dels} deletions | "
                 f"Press Enter to approve, Esc to reject"
        )
        
        # Show original with deletions highlighted
        self.original_text.delete('1.0', tk.END)
        for line in diff:
            if line.startswith('  '):  # Unchanged
                self.original_text.insert(tk.END, line[2:])
            elif line.startswith('- '):  # Deleted
                start = self.original_text.index(tk.END + '-1c')
                self.original_text.insert(tk.END, line[2:])
                end = self.original_text.index(tk.END + '-1c')
                self.original_text.tag_add('delete', start, end)
        
        # Show proposed with additions highlighted
        self.proposed_text.delete('1.0', tk.END)
        for line in diff:
            if line.startswith('  '):  # Unchanged
                self.proposed_text.insert(tk.END, line[2:])
            elif line.startswith('+ '):  # Added
                start = self.proposed_text.index(tk.END + '-1c')
                self.proposed_text.insert(tk.END, line[2:])
                end = self.proposed_text.index(tk.END + '-1c')
                self.proposed_text.tag_add('insert', start, end)
        
        # Make read-only
        self.original_text.config(state='disabled')
        self.proposed_text.config(state='disabled')
    
    def approve_changes(self):
        """Approve and apply changes"""
        self.approved = True
        if self.callback:
            self.callback(True, self.proposed_content)
        self.destroy()
    
    def reject_changes(self):
        """Reject changes"""
        self.approved = False
        if self.callback:
            self.callback(False, None)
        self.destroy()


class MultiFilePreviewDialog(tk.Toplevel):
    """Preview changes across multiple files"""
    
    def __init__(self, parent, changes_dict, callback=None):
        """
        changes_dict: {file_path: (original_content, proposed_content)}
        """
        super().__init__(parent)
        self.changes_dict = changes_dict
        self.callback = callback
        self.approved = False
        
        self.title(f"Preview Changes: {len(changes_dict)} files")
        self.geometry("1200x700")
        self.configure(bg=T.BG)
        
        # Make modal
        self.grab_set()
        self.transient(parent)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        # Header
        header = tk.Frame(self, bg=T.BG2, height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Title
        title_frame = tk.Frame(header, bg=T.BG2)
        title_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Label(title_frame, text="⚠️ Multi-File Changes",
                font=(T.UI, 14, 'bold'),
                fg=T.AMBER, bg=T.BG2).pack(anchor=tk.W)
        
        tk.Label(title_frame, text=f"{len(self.changes_dict)} files will be modified",
                font=(T.UI, 10),
                fg=T.TEXT, bg=T.BG2).pack(anchor=tk.W)
        
        # Action buttons
        button_frame = tk.Frame(header, bg=T.BG2)
        button_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Approve All button (green)
        approve_btn = tk.Button(button_frame, text="✓ Apply All Changes",
                               command=self.approve_all,
                               bg=T.BLOOD, fg=T.TEXT,
                               font=(T.UI, 12, 'bold'),
                               relief=tk.FLAT, padx=30, pady=10,
                               cursor='hand2')
        approve_btn.pack(side=tk.LEFT, padx=5)
        
        # Reject All button (red)
        reject_btn = tk.Button(button_frame, text="✗ Reject All",
                              command=self.reject_all,
                              bg=T.BLOOD, fg=T.TEXT,
                              font=(T.UI, 12, 'bold'),
                              relief=tk.FLAT, padx=30, pady=10,
                              cursor='hand2')
        reject_btn.pack(side=tk.LEFT, padx=5)
        
        # Main content
        content = tk.Frame(self, bg=T.BG)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # File list (left)
        list_frame = tk.LabelFrame(content, text="Modified Files",
                                   bg=T.BG2, fg=T.TEXT,
                                   font=(T.UI, 10, 'bold'),
                                   width=300)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        list_frame.pack_propagate(False)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(
            list_frame,
            bg=T.BG,
            fg=T.TEXT,
            selectbackground=T.HOVER,
            font=(T.UI, 10),
            bd=0,
            yscrollcommand=scrollbar.set
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Populate file list
        for file_path in sorted(self.changes_dict.keys()):
            self.file_listbox.insert(tk.END, os.path.basename(file_path))
        
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        self.file_listbox.selection_set(0)
        
        # Diff view (right)
        diff_frame = tk.Frame(content, bg=T.BG)
        diff_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.diff_text = scrolledtext.ScrolledText(
            diff_frame,
            wrap=tk.NONE,
            font=(T.MONO, 10),
            bg=T.BG,
            fg=T.TEXT,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.diff_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags
        self.diff_text.tag_config('delete', foreground=T.BLOOD_LIGHT)
        self.diff_text.tag_config('insert', foreground=T.BILE_LIGHT)
        self.diff_text.tag_config('info', foreground=T.SIGNAL_LIGHT)
        
        # Show first file
        self.on_file_select(None)
        
        # Keyboard shortcuts
        self.bind('<Return>', lambda e: self.approve_all())
        self.bind('<Escape>', lambda e: self.reject_all())
    
    def on_file_select(self, event):
        """Show diff for selected file"""
        selection = self.file_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        file_path = sorted(self.changes_dict.keys())[index]
        original, proposed = self.changes_dict[file_path]
        
        # Show unified diff
        self.diff_text.config(state='normal')
        self.diff_text.delete('1.0', tk.END)
        
        # Header
        self.diff_text.insert(tk.END, f"File: {file_path}\n", 'info')
        self.diff_text.insert(tk.END, "=" * 80 + "\n\n", 'info')
        
        # Generate unified diff
        original_lines = original.splitlines(keepends=True)
        proposed_lines = proposed.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines,
            proposed_lines,
            fromfile='Original',
            tofile='Proposed',
            lineterm=''
        )
        
        for line in diff:
            if line.startswith('---') or line.startswith('+++') or line.startswith('@@'):
                self.diff_text.insert(tk.END, line + '\n', 'info')
            elif line.startswith('-'):
                self.diff_text.insert(tk.END, line + '\n', 'delete')
            elif line.startswith('+'):
                self.diff_text.insert(tk.END, line + '\n', 'insert')
            else:
                self.diff_text.insert(tk.END, line + '\n')
        
        self.diff_text.config(state='disabled')
    
    def approve_all(self):
        """Approve all changes"""
        self.approved = True
        if self.callback:
            self.callback(True, self.changes_dict)
        self.destroy()
    
    def reject_all(self):
        """Reject all changes"""
        self.approved = False
        if self.callback:
            self.callback(False, None)
        self.destroy()
