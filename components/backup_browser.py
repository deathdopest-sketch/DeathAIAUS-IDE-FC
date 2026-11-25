"""
Backup Browser - Browse and restore AI backup files
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import shutil
from datetime import datetime
from components import death_theme as T


class BackupBrowser(tk.Toplevel):
    """Browse and restore backups from ai_backups folder"""
    
    def __init__(self, parent, ide_instance):
        super().__init__(parent)
        self.ide = ide_instance
        self.title("AI Backup Browser")
        self.geometry("1000x600")
        self.configure(bg=T.BG)
        
        self.backup_dir = os.path.join(self.ide.workspace_path, 'ai_backups')
        
        self.setup_ui()
        self.load_backups()
    
    def setup_ui(self):
        """Setup UI"""
        # Header
        header = tk.Frame(self, bg=T.BG3, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="💾 Backup Browser", 
                font=(T.UI, 14, 'bold'),
                fg=T.BILE, bg=T.BG3).pack(side=tk.LEFT, padx=15, pady=15)
        
        info = tk.Label(header, text=f"Location: {self.backup_dir}",
                       font=(T.UI, 9),
                       fg=T.TEXT2, bg=T.BG3)
        info.pack(side=tk.LEFT)
        
        # Main content - split view
        content = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=T.BG)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left: Backup list
        left_frame = tk.Frame(content, bg=T.BG)
        content.add(left_frame)
        
        tk.Label(left_frame, text="Backup Files:",
                font=(T.UI, 11, 'bold'),
                fg=T.TEXT, bg=T.BG, anchor='w').pack(fill=tk.X, pady=(0,5))
        
        # Treeview for backups
        tree_frame = tk.Frame(left_frame, bg=T.BG2)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(tree_frame, columns=('date', 'size'),
                                 yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        self.tree.heading('#0', text='File')
        self.tree.heading('date', text='Date')
        self.tree.heading('size', text='Size')
        
        self.tree.column('#0', width=300)
        self.tree.column('date', width=150)
        self.tree.column('size', width=80)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Right: Preview
        right_frame = tk.Frame(content, bg=T.BG)
        content.add(right_frame)
        
        tk.Label(right_frame, text="Preview:",
                font=(T.UI, 11, 'bold'),
                fg=T.TEXT, bg=T.BG, anchor='w').pack(fill=tk.X, pady=(0,5))
        
        self.preview = tk.Text(right_frame, font=(T.MONO, 10),
                              bg=T.BG2, fg=T.TEXT, wrap=tk.NONE)
        self.preview.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbars to preview
        preview_scroll_y = ttk.Scrollbar(self.preview, orient=tk.VERTICAL, command=self.preview.yview)
        preview_scroll_x = ttk.Scrollbar(self.preview, orient=tk.HORIZONTAL, command=self.preview.xview)
        self.preview.configure(yscrollcommand=preview_scroll_y.set, xscrollcommand=preview_scroll_x.set)
        
        # Buttons
        button_frame = tk.Frame(self, bg=T.BG)
        button_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        
        tk.Button(button_frame, text="✓ Restore Selected",
                 command=self.restore_backup,
                 bg=T.BLOOD, fg=T.TEXT, font=(T.UI, 10, 'bold'),
                 relief=tk.FLAT, padx=20, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="👁️ Compare with Current",
                 command=self.compare_with_current,
                 bg=T.HOVER, fg=T.TEXT, font=(T.UI, 10),
                 relief=tk.FLAT, padx=20, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🗑️ Delete Backup",
                 command=self.delete_backup,
                 bg=T.BLOOD, fg=T.TEXT, font=(T.UI, 10),
                 relief=tk.FLAT, padx=20, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Close",
                 command=self.destroy,
                 bg=T.HOVER, fg=T.TEXT, font=(T.UI, 10),
                 relief=tk.FLAT, padx=20, pady=8,
                 cursor='hand2').pack(side=tk.RIGHT, padx=5)
    
    def load_backups(self):
        """Load backup files"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not os.path.exists(self.backup_dir):
            self.preview.delete('1.0', tk.END)
            self.preview.insert('1.0', "No backups found.\n\nBackups will be created automatically when AI modifies files.")
            return
        
        # List backup files
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.endswith('.bak'):
                path = os.path.join(self.backup_dir, file)
                stat = os.stat(path)
                backups.append({
                    'name': file,
                    'path': path,
                    'date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'size': f"{stat.st_size / 1024:.1f} KB"
                })
        
        # Sort by date (newest first)
        backups.sort(key=lambda x: x['date'], reverse=True)
        
        # Add to tree
        for backup in backups:
            self.tree.insert('', 'end', text=backup['name'],
                           values=(backup['date'], backup['size']),
                           tags=(backup['path'],))
        
        if not backups:
            self.preview.delete('1.0', tk.END)
            self.preview.insert('1.0', "No backups found.")
    
    def on_select(self, event):
        """Handle selection"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item = selected[0]
        path = self.tree.item(item, 'tags')[0]
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.preview.delete('1.0', tk.END)
            self.preview.insert('1.0', content)
        except Exception as e:
            self.preview.delete('1.0', tk.END)
            self.preview.insert('1.0', f"Error loading preview: {e}")
    
    def restore_backup(self):
        """Restore selected backup"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a backup to restore")
            return
        
        item = selected[0]
        backup_path = self.tree.item(item, 'tags')[0]
        backup_name = self.tree.item(item, 'text')
        
        # Extract original filename
        original_name = backup_name.replace('.bak', '').split('_')[0] if '_' in backup_name else backup_name.replace('.bak', '')
        
        if messagebox.askyesno("Restore Backup", 
                              f"Restore backup to current file?\n\n"
                              f"This will replace the current content."):
            try:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Insert into current editor
                if hasattr(self.ide, 'code_editor') and self.ide.code_editor:
                    self.ide.code_editor.delete('1.0', tk.END)
                    self.ide.code_editor.insert('1.0', content)
                    messagebox.showinfo("Restored", "Backup restored successfully!")
                else:
                    messagebox.showerror("Error", "No active editor to restore to")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to restore: {e}")
    
    def compare_with_current(self):
        """Compare backup with current file"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a backup to compare")
            return
        
        item = selected[0]
        backup_path = self.tree.item(item, 'tags')[0]
        
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            
            if hasattr(self.ide, 'code_editor') and self.ide.code_editor:
                current_content = self.ide.code_editor.get('1.0', 'end-1c')
                
                # Show diff
                from components.diff_viewer import DiffViewer
                DiffViewer(self.ide.root, "Backup Comparison", 
                          backup_content, current_content, 
                          "Backup vs Current")
            else:
                messagebox.showerror("Error", "No active editor for comparison")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compare: {e}")
    
    def delete_backup(self):
        """Delete selected backup"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a backup to delete")
            return
        
        item = selected[0]
        backup_path = self.tree.item(item, 'tags')[0]
        backup_name = self.tree.item(item, 'text')
        
        if messagebox.askyesno("Delete Backup", 
                              f"Delete backup '{backup_name}'?\n\nThis cannot be undone."):
            try:
                os.remove(backup_path)
                self.load_backups()
                messagebox.showinfo("Deleted", "Backup deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {e}")
