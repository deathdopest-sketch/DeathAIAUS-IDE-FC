"""
Extension System
Plugin architecture for extending IDE functionality
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import importlib.util
import sys
from components import death_theme as T


class Extension:
    """Base extension class"""

    def __init__(self, manifest):
        self.manifest = manifest
        self.name = manifest.get('name', 'Unknown')
        self.version = manifest.get('version', '1.0.0')
        self.author = manifest.get('author', 'Unknown')
        self.description = manifest.get('description', '')
        self.enabled = False
        self.module = None

    def activate(self, ide_instance):
        """Activate extension"""
        pass

    def deactivate(self):
        """Deactivate extension"""
        pass

    def on_file_open(self, file_path):
        """Called when file is opened"""
        pass

    def on_file_save(self, file_path):
        """Called when file is saved"""
        pass

    def on_text_change(self, editor, file_path):
        """Called when text changes"""
        pass


class ExtensionManager:
    """Manages IDE extensions"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.extensions = {}  # name -> Extension
        self.extensions_dir = os.path.join(
            os.path.expanduser('~'),
            '.deathaius_extensions'
        )

        # Create extensions directory
        os.makedirs(self.extensions_dir, exist_ok=True)

        # Load extensions
        self.load_extensions()

    def load_extensions(self):
        """Load all extensions from directory"""
        if not os.path.exists(self.extensions_dir):
            return

        for item in os.listdir(self.extensions_dir):
            ext_path = os.path.join(self.extensions_dir, item)
            if os.path.isdir(ext_path):
                self._load_extension(ext_path)

    def _load_extension(self, ext_path):
        """Load single extension"""
        try:
            # Load manifest
            manifest_path = os.path.join(ext_path, 'manifest.json')
            if not os.path.exists(manifest_path):
                return

            with open(manifest_path, 'r') as f:
                manifest = json.load(f)

            name = manifest.get('name')
            if not name:
                return

            # Load main module
            main_file = manifest.get('main', 'main.py')
            main_path = os.path.join(ext_path, main_file)

            if not os.path.exists(main_path):
                return

            # Import module
            spec = importlib.util.spec_from_file_location(name, main_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)

            # Create extension instance
            if hasattr(module, 'Extension'):
                extension = module.Extension(manifest)
                extension.module = module
                self.extensions[name] = extension

        except Exception as e:
            print(f"Failed to load extension {ext_path}: {e}")

    def activate_extension(self, name):
        """Activate an extension"""
        if name not in self.extensions:
            return False

        extension = self.extensions[name]
        if extension.enabled:
            return True

        try:
            extension.activate(self.ide)
            extension.enabled = True
            self._save_extension_state()
            return True
        except Exception as e:
            print(f"Failed to activate extension {name}: {e}")
            return False

    def deactivate_extension(self, name):
        """Deactivate an extension"""
        if name not in self.extensions:
            return False

        extension = self.extensions[name]
        if not extension.enabled:
            return True

        try:
            extension.deactivate()
            extension.enabled = False
            self._save_extension_state()
            return True
        except Exception as e:
            print(f"Failed to deactivate extension {name}: {e}")
            return False

    def get_extensions(self):
        """Get all extensions"""
        return self.extensions

    def trigger_hook(self, hook_name, *args, **kwargs):
        """Trigger extension hook"""
        for extension in self.extensions.values():
            if extension.enabled:
                hook_method = getattr(extension, hook_name, None)
                if hook_method and callable(hook_method):
                    try:
                        hook_method(*args, **kwargs)
                    except Exception as e:
                        print(f"Extension {extension.name} hook {hook_name} error: {e}")

    def _save_extension_state(self):
        """Save enabled extensions state"""
        config_file = os.path.join(self.extensions_dir, 'config.json')
        try:
            state = {
                'enabled': [name for name, ext in self.extensions.items() if ext.enabled]
            }
            with open(config_file, 'w') as f:
                json.dump(state, f, indent=2)
        except:
            pass

    def _load_extension_state(self):
        """Load enabled extensions state"""
        config_file = os.path.join(self.extensions_dir, 'config.json')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    state = json.load(f)
                    for name in state.get('enabled', []):
                        self.activate_extension(name)
            except:
                pass

    def install_extension(self, source_path):
        """Install extension from directory or zip"""
        try:
            # Copy to extensions directory
            import shutil

            if os.path.isdir(source_path):
                # Get extension name from manifest
                manifest_path = os.path.join(source_path, 'manifest.json')
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                    name = manifest.get('name')

                if not name:
                    return False, "Invalid manifest: missing name"

                dest_path = os.path.join(self.extensions_dir, name)

                # Remove existing
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)

                # Copy
                shutil.copytree(source_path, dest_path)

                # Load extension
                self._load_extension(dest_path)

                return True, f"Extension '{name}' installed successfully"

        except Exception as e:
            return False, f"Installation failed: {e}"

    def uninstall_extension(self, name):
        """Uninstall extension"""
        if name not in self.extensions:
            return False, "Extension not found"

        try:
            # Deactivate first
            self.deactivate_extension(name)

            # Remove directory
            import shutil
            ext_path = os.path.join(self.extensions_dir, name)
            if os.path.exists(ext_path):
                shutil.rmtree(ext_path)

            # Remove from loaded extensions
            del self.extensions[name]

            return True, f"Extension '{name}' uninstalled"

        except Exception as e:
            return False, f"Uninstall failed: {e}"


class ExtensionManagerDialog(tk.Toplevel):
    """Dialog for managing extensions"""

    def __init__(self, parent, extension_manager):
        super().__init__(parent)
        self.extension_manager = extension_manager
        self.title("Extension Manager")
        self.geometry("800x600")
        self.configure(bg=T.BG3)

        self.setup_ui()
        self.load_extensions()

    def setup_ui(self):
        """Setup UI"""
        # Header
        header = tk.Frame(self, bg=T.BG, height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="🔌 Extension Manager", font=(T.UI, 12, 'bold'),
                fg=T.BILE, bg=T.BG).pack(pady=15)

        # Main container
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left: Extension list
        left_frame = tk.Frame(main_paned, bg=T.BG3)
        main_paned.add(left_frame, weight=1)

        tk.Label(left_frame, text="Installed Extensions:", bg=T.BG3, fg=T.TEXT,
                font=(T.UI, 10, 'bold')).pack(anchor='w', padx=5, pady=5)

        # Extension list
        list_frame = tk.Frame(left_frame, bg=T.BG)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.ext_list = tk.Listbox(
            list_frame,
            bg=T.BG,
            fg=T.TEXT,
            font=(T.UI, 10),
            selectbackground=T.HOVER,
            yscrollcommand=scrollbar.set
        )
        self.ext_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.ext_list.yview)

        self.ext_list.bind('<<ListboxSelect>>', self.on_extension_select)

        # Buttons
        btn_frame = tk.Frame(left_frame, bg=T.BG3)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(btn_frame, text="+ Install", command=self.install_extension,
                 bg=T.BLOOD, fg=T.TEXT, relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=2)

        tk.Button(btn_frame, text="✕ Uninstall", command=self.uninstall_extension,
                 bg=T.BLOOD, fg=T.TEXT, relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=2)

        # Right: Extension details
        right_frame = tk.Frame(main_paned, bg=T.BG3)
        main_paned.add(right_frame, weight=2)

        tk.Label(right_frame, text="Extension Details:", bg=T.BG3, fg=T.TEXT,
                font=(T.UI, 10, 'bold')).pack(anchor='w', padx=5, pady=5)

        # Details display
        self.details_frame = tk.Frame(right_frame, bg=T.BG3)
        self.details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Name
        tk.Label(self.details_frame, text="Name:", bg=T.BG3, fg=T.TEXT2).pack(anchor='w', pady=2)
        self.name_label = tk.Label(self.details_frame, text="--", bg=T.BG3,
                                   fg=T.TEXT, font=(T.UI, 11, 'bold'))
        self.name_label.pack(anchor='w', pady=2)

        # Version
        tk.Label(self.details_frame, text="Version:", bg=T.BG3, fg=T.TEXT2).pack(anchor='w', pady=2)
        self.version_label = tk.Label(self.details_frame, text="--", bg=T.BG3, fg=T.TEXT)
        self.version_label.pack(anchor='w', pady=2)

        # Author
        tk.Label(self.details_frame, text="Author:", bg=T.BG3, fg=T.TEXT2).pack(anchor='w', pady=2)
        self.author_label = tk.Label(self.details_frame, text="--", bg=T.BG3, fg=T.TEXT)
        self.author_label.pack(anchor='w', pady=2)

        # Description
        tk.Label(self.details_frame, text="Description:", bg=T.BG3, fg=T.TEXT2).pack(anchor='w', pady=2)
        self.desc_text = tk.Text(self.details_frame, height=5, bg=T.BG, fg=T.TEXT,
                                font=(T.UI, 9), wrap=tk.WORD, state='disabled')
        self.desc_text.pack(fill=tk.X, pady=2)

        # Status
        tk.Label(self.details_frame, text="Status:", bg=T.BG3, fg=T.TEXT2).pack(anchor='w', pady=10)
        self.status_label = tk.Label(self.details_frame, text="Disabled", bg=T.BG3,
                                     fg=T.BLOOD_LIGHT, font=(T.UI, 10, 'bold'))
        self.status_label.pack(anchor='w', pady=2)

        # Toggle button
        self.toggle_btn = tk.Button(
            self.details_frame,
            text="Enable",
            command=self.toggle_extension,
            bg=T.HOVER,
            fg=T.TEXT,
            font=(T.UI, 10, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=5,
            state='disabled'
        )
        self.toggle_btn.pack(pady=10)

    def load_extensions(self):
        """Load extensions into list"""
        self.ext_list.delete(0, tk.END)

        for name, ext in self.extension_manager.get_extensions().items():
            status = "✓" if ext.enabled else "○"
            display = f"{status} {ext.name} v{ext.version}"
            self.ext_list.insert(tk.END, display)

    def on_extension_select(self, event=None):
        """Handle extension selection"""
        selection = self.ext_list.curselection()
        if not selection:
            return

        idx = selection[0]
        extensions = list(self.extension_manager.get_extensions().values())
        if idx >= len(extensions):
            return

        ext = extensions[idx]

        # Update details
        self.name_label.config(text=ext.name)
        self.version_label.config(text=ext.version)
        self.author_label.config(text=ext.author)

        self.desc_text.config(state='normal')
        self.desc_text.delete('1.0', 'end')
        self.desc_text.insert('1.0', ext.description)
        self.desc_text.config(state='disabled')

        # Update status
        if ext.enabled:
            self.status_label.config(text="Enabled", fg=T.BILE)
            self.toggle_btn.config(text="Disable", state='normal')
        else:
            self.status_label.config(text="Disabled", fg=T.BLOOD_LIGHT)
            self.toggle_btn.config(text="Enable", state='normal')

    def toggle_extension(self):
        """Toggle extension enabled state"""
        selection = self.ext_list.curselection()
        if not selection:
            return

        idx = selection[0]
        extensions = list(self.extension_manager.get_extensions().items())
        if idx >= len(extensions):
            return

        name, ext = extensions[idx]

        if ext.enabled:
            success = self.extension_manager.deactivate_extension(name)
        else:
            success = self.extension_manager.activate_extension(name)

        if success:
            self.load_extensions()
            self.ext_list.selection_set(idx)
            self.on_extension_select()

    def install_extension(self):
        """Install new extension"""
        directory = filedialog.askdirectory(title="Select Extension Directory")
        if not directory:
            return

        success, message = self.extension_manager.install_extension(directory)

        if success:
            messagebox.showinfo("Success", message)
            self.load_extensions()
        else:
            messagebox.showerror("Error", message)

    def uninstall_extension(self):
        """Uninstall selected extension"""
        selection = self.ext_list.curselection()
        if not selection:
            return

        idx = selection[0]
        extensions = list(self.extension_manager.get_extensions().items())
        if idx >= len(extensions):
            return

        name, ext = extensions[idx]

        confirm = messagebox.askyesno(
            "Confirm Uninstall",
            f"Uninstall extension '{ext.name}'?"
        )

        if confirm:
            success, message = self.extension_manager.uninstall_extension(name)

            if success:
                messagebox.showinfo("Success", message)
                self.load_extensions()
            else:
                messagebox.showerror("Error", message)


# Example extension template
EXAMPLE_EXTENSION_MANIFEST = '''
{
  "name": "example-extension",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "An example extension for DeathAIAUS IDE",
  "main": "main.py",
  "hooks": [
    "on_file_open",
    "on_file_save",
    "on_text_change"
  ]
}
'''

EXAMPLE_EXTENSION_CODE = '''
"""
Example Extension for DeathAIAUS IDE
"""

class Extension:
    """Extension class"""

    def __init__(self, manifest):
        self.manifest = manifest
        self.name = manifest.get('name', 'Example')
        self.version = manifest.get('version', '1.0.0')
        self.author = manifest.get('author', 'Unknown')
        self.description = manifest.get('description', '')
        self.enabled = False
        self.ide = None

    def activate(self, ide_instance):
        """Called when extension is activated"""
        self.ide = ide_instance
        print(f"{self.name} activated!")

        # Add menu item
        if hasattr(ide_instance, 'menubar'):
            # TODO: Add menu item

            pass

    def deactivate(self):
        """Called when extension is deactivated"""
        print(f"{self.name} deactivated!")

    def on_file_open(self, file_path):
        """Called when a file is opened"""
        print(f"File opened: {file_path}")

    def on_file_save(self, file_path):
        """Called when a file is saved"""
        print(f"File saved: {file_path}")

    def on_text_change(self, editor, file_path):
        """Called when text changes"""
        pass
'''
