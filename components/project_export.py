"""
Project Sharing and Export
Export projects as archives, templates, or shareable packages
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import zipfile
import shutil
from datetime import datetime
from components import death_theme as T


class ProjectExporter:
    """Export projects in various formats"""

    def __init__(self):
        pass

    def export_as_zip(self, project_path, output_path, include_venv=False):
        """Export project as ZIP archive"""
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(project_path):
                    # Skip certain directories
                    if not include_venv:
                        dirs[:] = [d for d in dirs if d not in [
                            '__pycache__', '.git', 'node_modules', 'venv',
                            '.venv', 'dist', 'build', '.idea', '.vscode'
                        ]]

                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, project_path)
                        zipf.write(file_path, arcname)

            return True, f"Exported to {output_path}"

        except Exception as e:
            return False, f"Export failed: {e}"

    def export_as_template(self, project_path, template_name, description=""):
        """Export project as reusable template"""
        try:
            template_dir = os.path.join(
                os.path.expanduser('~'),
                '.deathaius_templates',
                template_name
            )

            os.makedirs(template_dir, exist_ok=True)

            # Copy project files
            for item in os.listdir(project_path):
                if item in ['__pycache__', '.git', 'node_modules', 'venv', '.venv']:
                    continue

                src = os.path.join(project_path, item)
                dst = os.path.join(template_dir, item)

                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)

            # Create template metadata
            metadata = {
                'name': template_name,
                'description': description,
                'created': datetime.now().isoformat(),
                'files': os.listdir(template_dir)
            }

            with open(os.path.join(template_dir, 'template.json'), 'w') as f:
                json.dump(metadata, f, indent=2)

            return True, f"Template saved: {template_name}"

        except Exception as e:
            return False, f"Template export failed: {e}"

    def create_shareable_package(self, project_path, output_path):
        """Create shareable package with README"""
        try:
            # Create temp directory
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                package_dir = os.path.join(temp_dir, os.path.basename(project_path))
                os.makedirs(package_dir)

                # Copy project
                for item in os.listdir(project_path):
                    if item in ['__pycache__', '.git', 'node_modules', 'venv']:
                        continue

                    src = os.path.join(project_path, item)
                    dst = os.path.join(package_dir, item)

                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)

                # Add sharing metadata
                share_info = {
                    'exported_by': 'DeathAIAUS IDE',
                    'exported_at': datetime.now().isoformat(),
                    'project_name': os.path.basename(project_path)
                }

                with open(os.path.join(package_dir, 'SHARE_INFO.json'), 'w') as f:
                    json.dump(share_info, f, indent=2)

                # Create ZIP
                shutil.make_archive(output_path.replace('.zip', ''), 'zip', temp_dir)

            return True, f"Package created: {output_path}"

        except Exception as e:
            return False, f"Package creation failed: {e}"


class ExportDialog(tk.Toplevel):
    """Dialog for exporting projects"""

    def __init__(self, parent, project_path):
        super().__init__(parent)
        self.project_path = project_path
        self.exporter = ProjectExporter()
        self.title("Export Project")
        self.geometry("600x500")
        self.configure(bg=T.BG3)

        self.setup_ui()

    def setup_ui(self):
        """Setup export UI"""
        # Header
        header = tk.Frame(self, bg=T.BG, height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        project_name = os.path.basename(self.project_path)
        tk.Label(header, text=f"📦 Export: {project_name}",
                font=(T.UI, 12, 'bold'), fg=T.BILE, bg=T.BG).pack(pady=15)

        # Export options
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ZIP Archive tab
        zip_frame = tk.Frame(notebook, bg=T.BG3)
        notebook.add(zip_frame, text="ZIP Archive")

        tk.Label(zip_frame, text="Export as ZIP Archive",
                font=(T.UI, 11, 'bold'), bg=T.BG3, fg=T.TEXT).pack(pady=20)

        self.include_venv_var = tk.BooleanVar(value=False)
        tk.Checkbutton(zip_frame, text="Include virtual environment",
                      variable=self.include_venv_var,
                      bg=T.BG3, fg=T.TEXT, selectcolor=T.BG).pack(pady=10)

        tk.Button(zip_frame, text="📁 Export as ZIP",
                 command=self.export_zip,
                 bg=T.HOVER, fg=T.TEXT, font=(T.UI, 10, 'bold'),
                 relief=tk.FLAT, padx=30, pady=10).pack(pady=20)

        # Template tab
        template_frame = tk.Frame(notebook, bg=T.BG3)
        notebook.add(template_frame, text="Template")

        tk.Label(template_frame, text="Save as Project Template",
                font=(T.UI, 11, 'bold'), bg=T.BG3, fg=T.TEXT).pack(pady=20)

        tk.Label(template_frame, text="Template Name:", bg=T.BG3,
                fg=T.TEXT).pack()
        self.template_name_var = tk.StringVar(value=os.path.basename(self.project_path))
        tk.Entry(template_frame, textvariable=self.template_name_var,
                bg=T.BG, fg=T.TEXT, width=40).pack(pady=5)

        tk.Label(template_frame, text="Description:", bg=T.BG3,
                fg=T.TEXT).pack(pady=(10, 0))
        self.template_desc_var = tk.StringVar()
        tk.Entry(template_frame, textvariable=self.template_desc_var,
                bg=T.BG, fg=T.TEXT, width=40).pack(pady=5)

        tk.Button(template_frame, text="💾 Save as Template",
                 command=self.export_template,
                 bg=T.BLOOD, fg=T.TEXT, font=(T.UI, 10, 'bold'),
                 relief=tk.FLAT, padx=30, pady=10).pack(pady=20)

        # Share tab
        share_frame = tk.Frame(notebook, bg=T.BG3)
        notebook.add(share_frame, text="Share")

        tk.Label(share_frame, text="Create Shareable Package",
                font=(T.UI, 11, 'bold'), bg=T.BG3, fg=T.TEXT).pack(pady=20)

        tk.Label(share_frame,
                text="Creates a clean package with:\n• Project files\n• README\n• Share info\n• No build artifacts",
                bg=T.BG3, fg=T.TEXT2, justify=tk.LEFT).pack(pady=10)

        tk.Button(share_frame, text="📤 Create Shareable Package",
                 command=self.create_package,
                 bg=T.AMBER, fg=T.TEXT, font=(T.UI, 10, 'bold'),
                 relief=tk.FLAT, padx=30, pady=10).pack(pady=20)

    def export_zip(self):
        """Export as ZIP"""
        output_file = filedialog.asksaveasfilename(
            title="Export as ZIP",
            defaultextension=".zip",
            filetypes=[("ZIP files", "*.zip")],
            initialfile=f"{os.path.basename(self.project_path)}.zip"
        )

        if not output_file:
            return

        success, message = self.exporter.export_as_zip(
            self.project_path,
            output_file,
            self.include_venv_var.get()
        )

        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

    def export_template(self):
        """Export as template"""
        name = self.template_name_var.get().strip()
        description = self.template_desc_var.get().strip()

        if not name:
            messagebox.showwarning("Warning", "Please enter a template name")
            return

        success, message = self.exporter.export_as_template(
            self.project_path,
            name,
            description
        )

        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

    def create_package(self):
        """Create shareable package"""
        output_file = filedialog.asksaveasfilename(
            title="Create Shareable Package",
            defaultextension=".zip",
            filetypes=[("ZIP files", "*.zip")],
            initialfile=f"{os.path.basename(self.project_path)}_share.zip"
        )

        if not output_file:
            return

        success, message = self.exporter.create_shareable_package(
            self.project_path,
            output_file
        )

        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)
