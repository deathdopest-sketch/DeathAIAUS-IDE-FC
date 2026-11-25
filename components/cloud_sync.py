"""
Cloud Sync for Settings
Sync IDE settings, themes, snippets, and preferences across devices
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import hashlib
import time
from datetime import datetime
from components import death_theme as T


class SettingsSync:
    """Syncs settings to local/cloud storage"""

    def __init__(self):
        self.sync_dir = os.path.join(os.path.expanduser('~'), '.deathaius_sync')
        os.makedirs(self.sync_dir, exist_ok=True)

        self.settings_file = os.path.join(self.sync_dir, 'settings.json')
        self.last_sync = 0

    def export_settings(self, ide_instance):
        """Export all IDE settings"""
        settings = {
            'version': '1.0.0',
            'exported': datetime.now().isoformat(),
            'settings': {}
        }

        # Theme
        if hasattr(ide_instance, 'theme_manager'):
            settings['settings']['theme'] = ide_instance.theme_manager.current_theme.name

        # Keyboard shortcuts (custom)
        # Extensions (enabled list)
        if hasattr(ide_instance, 'extension_manager'):
            settings['settings']['extensions'] = [
                name for name, ext in ide_instance.extension_manager.extensions.items()
                if ext.enabled
            ]

        # Editor preferences
        settings['settings']['editor'] = {
            'font_size': 11,
            'tab_size': 4,
            'word_wrap': False,
            'line_numbers': True,
            'auto_save': False
        }

        # AI preferences
        settings['settings']['ai'] = {
            'inline_suggestions': True,
            'auto_complete': True,
            'model': getattr(ide_instance, 'coder_model', 'default')
        }

        return settings

    def import_settings(self, settings, ide_instance):
        """Import settings to IDE"""
        try:
            # Theme
            if 'theme' in settings.get('settings', {}):
                theme_name = settings['settings']['theme']
                if hasattr(ide_instance, 'theme_manager'):
                    ide_instance.theme_manager.apply_theme(theme_name)

            # Extensions
            if 'extensions' in settings.get('settings', {}):
                enabled_extensions = settings['settings']['extensions']
                if hasattr(ide_instance, 'extension_manager'):
                    for ext_name in enabled_extensions:
                        ide_instance.extension_manager.activate_extension(ext_name)

            # Editor preferences
            if 'editor' in settings.get('settings', {}):
                # Apply editor settings
                pass

            return True, "Settings imported successfully"

        except Exception as e:
            return False, f"Failed to import settings: {e}"

    def save_to_file(self, settings, file_path=None):
        """Save settings to file"""
        if not file_path:
            file_path = self.settings_file

        try:
            with open(file_path, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save settings: {e}")
            return False

    def load_from_file(self, file_path=None):
        """Load settings from file"""
        if not file_path:
            file_path = self.settings_file

        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load settings: {e}")
            return None

    def sync_with_cloud(self, cloud_provider=None):
        """Sync with cloud provider (placeholder for actual cloud integration)"""
        # This would integrate with services like:
        # - GitHub Gist
        # - Dropbox
        # - Google Drive
        # - Custom server
        pass


class SyncDialog(tk.Toplevel):
    """Dialog for managing sync"""

    def __init__(self, parent, ide_instance):
        super().__init__(parent)
        self.ide = ide_instance
        self.sync = SettingsSync()
        self.title("Settings Sync")
        self.geometry("600x500")
        self.configure(bg=T.BG3)

        self.setup_ui()

    def setup_ui(self):
        """Setup sync UI"""
        # Header
        header = tk.Frame(self, bg=T.BG, height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="☁️ Settings Sync", font=(T.UI, 12, 'bold'),
                fg=T.BILE, bg=T.BG).pack(pady=15)

        # Tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Export tab
        export_frame = tk.Frame(notebook, bg=T.BG3)
        notebook.add(export_frame, text="Export")

        tk.Label(export_frame, text="Export IDE Settings", font=(T.UI, 11, 'bold'),
                bg=T.BG3, fg=T.TEXT).pack(pady=20)

        tk.Label(export_frame, text="This will export:\n• Theme\n• Extensions\n• Editor preferences\n• AI settings",
                bg=T.BG3, fg=T.TEXT2, justify=tk.LEFT).pack(pady=10)

        tk.Button(export_frame, text="📤 Export to File",
                 command=self.export_to_file,
                 bg=T.HOVER, fg=T.TEXT, font=(T.UI, 10, 'bold'),
                 relief=tk.FLAT, padx=30, pady=10).pack(pady=20)

        # Import tab
        import_frame = tk.Frame(notebook, bg=T.BG3)
        notebook.add(import_frame, text="Import")

        tk.Label(import_frame, text="Import IDE Settings", font=(T.UI, 11, 'bold'),
                bg=T.BG3, fg=T.TEXT).pack(pady=20)

        tk.Label(import_frame, text="This will import settings from a file.\nCurrent settings will be overwritten.",
                bg=T.BG3, fg=T.TEXT2, justify=tk.LEFT).pack(pady=10)

        tk.Button(import_frame, text="📥 Import from File",
                 command=self.import_from_file,
                 bg=T.BLOOD, fg=T.TEXT, font=(T.UI, 10, 'bold'),
                 relief=tk.FLAT, padx=30, pady=10).pack(pady=20)

        # Cloud sync tab
        cloud_frame = tk.Frame(notebook, bg=T.BG3)
        notebook.add(cloud_frame, text="Cloud Sync")

        tk.Label(cloud_frame, text="Cloud Sync (Coming Soon)", font=(T.UI, 11, 'bold'),
                bg=T.BG3, fg=T.TEXT).pack(pady=20)

        tk.Label(cloud_frame,
                text="Cloud sync will allow you to sync settings across devices.\n\nPlanned integrations:\n• GitHub Gist\n• Dropbox\n• Google Drive\n• Custom server",
                bg=T.BG3, fg=T.TEXT2, justify=tk.LEFT).pack(pady=10)

        # GitHub Gist (placeholder)
        gist_frame = tk.Frame(cloud_frame, bg=T.BG3)
        gist_frame.pack(pady=20)

        tk.Label(gist_frame, text="GitHub Personal Access Token:",
                bg=T.BG3, fg=T.TEXT).pack()

        self.gist_token_var = tk.StringVar()
        tk.Entry(gist_frame, textvariable=self.gist_token_var,
                bg=T.BG, fg=T.TEXT, show='*', width=40).pack(pady=5)

        tk.Button(gist_frame, text="Connect to GitHub Gist",
                 command=self.connect_gist,
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT,
                 state='disabled').pack(pady=5)

    def export_to_file(self):
        """Export settings to file"""
        from tkinter import filedialog

        # Get settings
        settings = self.sync.export_settings(self.ide)

        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            title="Export Settings",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"deathaius_settings_{datetime.now().strftime('%Y%m%d')}.json"
        )

        if file_path:
            if self.sync.save_to_file(settings, file_path):
                messagebox.showinfo("Success", f"Settings exported to:\n{file_path}")
            else:
                messagebox.showerror("Error", "Failed to export settings")

    def import_from_file(self):
        """Import settings from file"""
        from tkinter import filedialog

        # Ask for file
        file_path = filedialog.askopenfilename(
            title="Import Settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not file_path:
            return

        # Load settings
        settings = self.sync.load_from_file(file_path)

        if not settings:
            messagebox.showerror("Error", "Failed to load settings file")
            return

        # Confirm import
        confirm = messagebox.askyesno(
            "Confirm Import",
            "This will overwrite your current settings.\n\nContinue?"
        )

        if not confirm:
            return

        # Import
        success, message = self.sync.import_settings(settings, self.ide)

        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

    def connect_gist(self):
        """Connect to GitHub Gist (placeholder)"""
        token = self.gist_token_var.get().strip()

        if not token:
            messagebox.showwarning("Warning", "Please enter your GitHub Personal Access Token")
            return

        # TODO: Implement GitHub Gist integration
        messagebox.showinfo("Coming Soon", "GitHub Gist integration coming soon!")


class AutoSyncManager:
    """Manages automatic syncing"""

    def __init__(self, ide_instance, interval=300):
        self.ide = ide_instance
        self.sync = SettingsSync()
        self.interval = interval  # seconds
        self.enabled = False
        self.last_sync = 0

    def enable(self):
        """Enable auto-sync"""
        self.enabled = True
        self._schedule_sync()

    def disable(self):
        """Disable auto-sync"""
        self.enabled = False

    def _schedule_sync(self):
        """Schedule next sync"""
        if not self.enabled:
            return

        # Export settings
        settings = self.sync.export_settings(self.ide)
        self.sync.save_to_file(settings)

        self.last_sync = time.time()

        # Schedule next sync
        if hasattr(self.ide, 'root'):
            self.ide.root.after(self.interval * 1000, self._schedule_sync)


class SettingsBackup:
    """Create and restore settings backups"""

    def __init__(self):
        self.backup_dir = os.path.join(os.path.expanduser('~'), '.deathaius_backup')
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_backup(self, ide_instance, name=None):
        """Create settings backup"""
        if not name:
            name = datetime.now().strftime('%Y%m%d_%H%M%S')

        sync = SettingsSync()
        settings = sync.export_settings(ide_instance)

        backup_file = os.path.join(self.backup_dir, f"backup_{name}.json")

        if sync.save_to_file(settings, backup_file):
            return True, backup_file
        else:
            return False, None

    def list_backups(self):
        """List available backups"""
        if not os.path.exists(self.backup_dir):
            return []

        backups = []
        for file in os.listdir(self.backup_dir):
            if file.startswith('backup_') and file.endswith('.json'):
                file_path = os.path.join(self.backup_dir, file)
                backups.append({
                    'name': file,
                    'path': file_path,
                    'created': datetime.fromtimestamp(os.path.getmtime(file_path)),
                    'size': os.path.getsize(file_path)
                })

        return sorted(backups, key=lambda x: x['created'], reverse=True)

    def restore_backup(self, backup_path, ide_instance):
        """Restore from backup"""
        sync = SettingsSync()
        settings = sync.load_from_file(backup_path)

        if not settings:
            return False, "Failed to load backup"

        return sync.import_settings(settings, ide_instance)

    def delete_backup(self, backup_path):
        """Delete backup"""
        try:
            os.remove(backup_path)
            return True
        except:
            return False


class BackupManagerDialog(tk.Toplevel):
    """Dialog for managing backups"""

    def __init__(self, parent, ide_instance):
        super().__init__(parent)
        self.ide = ide_instance
        self.backup = SettingsBackup()
        self.title("Backup Manager")
        self.geometry("600x400")
        self.configure(bg=T.BG3)

        self.setup_ui()
        self.load_backups()

    def setup_ui(self):
        """Setup backup UI"""
        # Header
        header = tk.Frame(self, bg=T.BG, height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="💾 Backup Manager", font=(T.UI, 12, 'bold'),
                fg=T.BILE, bg=T.BG).pack(side=tk.LEFT, padx=10, pady=15)

        tk.Button(header, text="+ Create Backup", command=self.create_backup,
                 bg=T.BLOOD, fg=T.TEXT, relief=tk.FLAT).pack(side=tk.RIGHT, padx=10)

        # Backup list
        list_frame = tk.Frame(self, bg=T.BG)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.backup_list = tk.Listbox(
            list_frame,
            bg=T.BG,
            fg=T.TEXT,
            font=(T.UI, 10),
            selectbackground=T.HOVER,
            yscrollcommand=scrollbar.set
        )
        self.backup_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.backup_list.yview)

        # Buttons
        btn_frame = tk.Frame(self, bg=T.BG3)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(btn_frame, text="Restore", command=self.restore_backup,
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT, padx=20).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Delete", command=self.delete_backup,
                 bg=T.BLOOD, fg=T.TEXT, relief=tk.FLAT, padx=20).pack(side=tk.LEFT, padx=5)

    def load_backups(self):
        """Load backup list"""
        self.backup_list.delete(0, tk.END)

        backups = self.backup.list_backups()

        for backup in backups:
            created = backup['created'].strftime('%Y-%m-%d %H:%M:%S')
            size_kb = backup['size'] / 1024

            display = f"{created} - {size_kb:.1f} KB"
            self.backup_list.insert(tk.END, display)

        if not backups:
            self.backup_list.insert(tk.END, "No backups found")

    def create_backup(self):
        """Create new backup"""
        success, path = self.backup.create_backup(self.ide)

        if success:
            messagebox.showinfo("Success", f"Backup created:\n{path}")
            self.load_backups()
        else:
            messagebox.showerror("Error", "Failed to create backup")

    def restore_backup(self):
        """Restore selected backup"""
        selection = self.backup_list.curselection()
        if not selection:
            return

        backups = self.backup.list_backups()
        if selection[0] >= len(backups):
            return

        backup = backups[selection[0]]

        confirm = messagebox.askyesno(
            "Confirm Restore",
            "Restore from this backup?\nCurrent settings will be overwritten."
        )

        if not confirm:
            return

        success, message = self.backup.restore_backup(backup['path'], self.ide)

        if success:
            messagebox.showinfo("Success", "Backup restored successfully")
        else:
            messagebox.showerror("Error", message)

    def delete_backup(self):
        """Delete selected backup"""
        selection = self.backup_list.curselection()
        if not selection:
            return

        backups = self.backup.list_backups()
        if selection[0] >= len(backups):
            return

        backup = backups[selection[0]]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Delete this backup?"
        )

        if confirm:
            if self.backup.delete_backup(backup['path']):
                messagebox.showinfo("Success", "Backup deleted")
                self.load_backups()
            else:
                messagebox.showerror("Error", "Failed to delete backup")
