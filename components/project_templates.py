"""
Project Templates System
Quick project initialization with predefined structures
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
from components import death_theme as T


class ProjectTemplate:
    """Single project template definition"""

    def __init__(self, name, description, language, files, folders, dependencies=None):
        self.name = name
        self.description = description
        self.language = language
        self.files = files  # Dict of filename -> content
        self.folders = folders  # List of folder paths
        self.dependencies = dependencies or {}  # Package manager -> packages

    def create_project(self, root_path, project_name):
        """Create project from template"""
        project_path = os.path.join(root_path, project_name)

        # Create project directory
        os.makedirs(project_path, exist_ok=True)

        # Create folders
        for folder in self.folders:
            # Replace placeholders in folder names
            folder = folder.replace('{{PROJECT_NAME}}', project_name)
            folder = folder.replace('{{project_name}}', project_name.lower().replace(' ', '_'))
            folder_path = os.path.join(project_path, folder)
            os.makedirs(folder_path, exist_ok=True)

        # Create files
        for filename, content in self.files.items():
            file_path = os.path.join(project_path, filename)

            # Replace placeholders
            content = content.replace('{{PROJECT_NAME}}', project_name)
            content = content.replace('{{project_name}}', project_name.lower().replace(' ', '_'))

            # Ensure directory exists (only if file is in a subdirectory)
            file_dir = os.path.dirname(file_path)
            if file_dir and file_dir != project_path:
                os.makedirs(file_dir, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        return project_path


class TemplateLibrary:
    """Library of built-in project templates"""

    @staticmethod
    def get_templates():
        """Get all available templates"""
        return {
            'python_basic': TemplateLibrary.python_basic(),
            'python_flask': TemplateLibrary.python_flask(),
            'python_django': TemplateLibrary.python_django(),
            'javascript_node': TemplateLibrary.javascript_node(),
            'javascript_react': TemplateLibrary.javascript_react(),
            'javascript_express': TemplateLibrary.javascript_express(),
            'html_basic': TemplateLibrary.html_basic(),
            'python_ml': TemplateLibrary.python_ml(),
        }

    @staticmethod
    def python_basic():
        """Basic Python project"""
        return ProjectTemplate(
            name="Python Basic",
            description="Simple Python project with basic structure",
            language="Python",
            files={
                'main.py': '''"""
{{PROJECT_NAME}} - Main Entry Point
"""

def main():
    """Main function"""
    print("Hello from {{PROJECT_NAME}}!")

if __name__ == "__main__":
    main()
''',
                'README.md': '''# {{PROJECT_NAME}}

A Python project.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```
''',
                'requirements.txt': '''# Project dependencies
''',
                '.gitignore': '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
.venv
pip-log.txt
pip-delete-this-directory.txt
.pytest_cache/
''',
            },
            folders=['tests', 'src'],
            dependencies={'pip': []}
        )

    @staticmethod
    def python_flask():
        """Flask web application"""
        return ProjectTemplate(
            name="Python Flask",
            description="Flask web application with basic structure",
            language="Python",
            files={
                'app.py': '''from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
''',
                'templates/index.html': '''<!DOCTYPE html>
<html>
<head>
    <title>{{PROJECT_NAME}}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>Welcome to {{PROJECT_NAME}}</h1>
</body>
</html>
''',
                'static/style.css': '''body {
    font-family: Arial, sans-serif;
    margin: 40px;
    background: #f0f0f0;
}

h1 {
    color: #333;
}
''',
                'requirements.txt': '''Flask==3.0.0
''',
                'README.md': '''# {{PROJECT_NAME}}

Flask web application.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Visit http://localhost:5000
''',
                '.gitignore': '''__pycache__/
*.py[cod]
venv/
.env
instance/
''',
            },
            folders=['templates', 'static'],
            dependencies={'pip': ['Flask']}
        )

    @staticmethod
    def python_django():
        """Django web application"""
        return ProjectTemplate(
            name="Python Django",
            description="Django web application starter",
            language="Python",
            files={
                'manage.py': '''#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{{project_name}}.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
''',
                'requirements.txt': '''Django==4.2.0
''',
                'README.md': '''# {{PROJECT_NAME}}

Django web application.

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
''',
            },
            folders=['{{project_name}}', 'templates', 'static'],
            dependencies={'pip': ['Django']}
        )

    @staticmethod
    def javascript_node():
        """Basic Node.js project"""
        return ProjectTemplate(
            name="JavaScript Node",
            description="Node.js project with npm",
            language="JavaScript",
            files={
                'index.js': '''console.log('Hello from {{PROJECT_NAME}}!');

// Your code here
''',
                'package.json': '''{
  "name": "{{project_name}}",
  "version": "1.0.0",
  "description": "{{PROJECT_NAME}}",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "test": "echo \\"Error: no test specified\\" && exit 1"
  },
  "keywords": [],
  "author": "",
  "license": "MIT"
}
''',
                'README.md': '''# {{PROJECT_NAME}}

Node.js project.

## Installation

```bash
npm install
```

## Usage

```bash
npm start
```
''',
                '.gitignore': '''node_modules/
npm-debug.log
.env
''',
            },
            folders=['src'],
            dependencies={'npm': []}
        )

    @staticmethod
    def javascript_react():
        """React application"""
        return ProjectTemplate(
            name="JavaScript React",
            description="React application starter",
            language="JavaScript",
            files={
                'src/App.js': '''import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <h1>Welcome to {{PROJECT_NAME}}</h1>
    </div>
  );
}

export default App;
''',
                'src/index.js': '''import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
''',
                'public/index.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{{PROJECT_NAME}}</title>
</head>
<body>
    <div id="root"></div>
</body>
</html>
''',
                'package.json': '''{
  "name": "{{project_name}}",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  }
}
''',
                'README.md': '''# {{PROJECT_NAME}}

React application.

## Setup

```bash
npm install
npm start
```
''',
            },
            folders=['src', 'public'],
            dependencies={'npm': ['react', 'react-dom', 'react-scripts']}
        )

    @staticmethod
    def javascript_express():
        """Express.js server"""
        return ProjectTemplate(
            name="JavaScript Express",
            description="Express.js web server",
            language="JavaScript",
            files={
                'server.js': '''const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static('public'));

app.get('/', (req, res) => {
    res.send('Welcome to {{PROJECT_NAME}}');
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
''',
                'package.json': '''{
  "name": "{{project_name}}",
  "version": "1.0.0",
  "description": "Express server for {{PROJECT_NAME}}",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "express": "^4.18.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.0"
  }
}
''',
                'README.md': '''# {{PROJECT_NAME}}

Express.js server.

## Setup

```bash
npm install
npm start
```
''',
            },
            folders=['routes', 'public'],
            dependencies={'npm': ['express']}
        )

    @staticmethod
    def html_basic():
        """Basic HTML website"""
        return ProjectTemplate(
            name="HTML Basic",
            description="Basic HTML/CSS/JS website",
            language="HTML",
            files={
                'index.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{PROJECT_NAME}}</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header>
        <h1>{{PROJECT_NAME}}</h1>
    </header>
    <main>
        <p>Welcome to your new website!</p>
    </main>
    <script src="js/script.js"></script>
</body>
</html>
''',
                'css/style.css': '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
}

header {
    background: #333;
    color: #fff;
    padding: 1rem;
    text-align: center;
}

main {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 1rem;
}
''',
                'js/script.js': '''console.log('{{PROJECT_NAME}} loaded!');

// Your JavaScript code here
''',
                'README.md': '''# {{PROJECT_NAME}}

Basic HTML website.

Open index.html in a web browser.
''',
            },
            folders=['css', 'js', 'images'],
            dependencies={}
        )

    @staticmethod
    def python_ml():
        """Python Machine Learning project"""
        return ProjectTemplate(
            name="Python ML",
            description="Machine Learning project with common libraries",
            language="Python",
            files={
                'train.py': '''"""
{{PROJECT_NAME}} - Training Script
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

def main():
    """Main training function"""
    print("Starting training...")
    # Your training code here

if __name__ == "__main__":
    main()
''',
                'requirements.txt': '''numpy==1.24.0
pandas==2.0.0
scikit-learn==1.3.0
matplotlib==3.7.0
jupyter==1.0.0
''',
                'README.md': '''# {{PROJECT_NAME}}

Machine Learning project.

## Setup

```bash
pip install -r requirements.txt
```

## Training

```bash
python train.py
```
''',
                '.gitignore': '''__pycache__/
*.py[cod]
venv/
.ipynb_checkpoints/
data/
models/*.pkl
*.h5
''',
            },
            folders=['data', 'models', 'notebooks'],
            dependencies={'pip': ['numpy', 'pandas', 'scikit-learn', 'matplotlib', 'jupyter']}
        )


class ProjectTemplateDialog(tk.Toplevel):
    """Dialog for creating project from template"""

    def __init__(self, parent, ide_instance):
        super().__init__(parent)
        self.ide = ide_instance
        self.title("Create Project from Template")
        self.geometry("700x600")
        self.configure(bg=T.BG3)

        self.selected_template = None
        self.templates = TemplateLibrary.get_templates()

        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        # Header
        header = tk.Frame(self, bg=T.BG, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="📋 Create New Project", font=(T.UI, 14, 'bold'),
                fg=T.BILE, bg=T.BG).pack(pady=20)

        # Template selection
        main_frame = tk.Frame(self, bg=T.BG3)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(main_frame, text="Select Template:", bg=T.BG3, fg=T.TEXT,
                font=(T.UI, 11, 'bold')).pack(anchor='w', pady=(0, 10))

        # Template list
        list_frame = tk.Frame(main_frame, bg=T.BG)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.template_list = tk.Listbox(
            list_frame,
            bg=T.BG,
            fg=T.TEXT,
            font=(T.UI, 10),
            selectbackground=T.HOVER,
            activestyle='none',
            yscrollcommand=scrollbar.set,
            height=8
        )
        self.template_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.template_list.yview)

        # Populate templates
        for key, template in self.templates.items():
            display = f"📦 {template.name} - {template.description}"
            self.template_list.insert(tk.END, display)

        self.template_list.bind('<<ListboxSelect>>', self.on_template_select)

        # Template description
        self.description_text = tk.Text(main_frame, height=4, bg=T.BG,
                                       fg=T.TEXT2, font=(T.UI, 9),
                                       wrap=tk.WORD, state='disabled')
        self.description_text.pack(fill=tk.X, pady=(0, 10))

        # Project name
        tk.Label(main_frame, text="Project Name:", bg=T.BG3, fg=T.TEXT,
                font=(T.UI, 10)).pack(anchor='w', pady=(10, 5))

        self.name_var = tk.StringVar(value="MyProject")
        tk.Entry(main_frame, textvariable=self.name_var, font=(T.UI, 10),
                bg=T.BG, fg=T.TEXT).pack(fill=tk.X, pady=(0, 10))

        # Location
        location_frame = tk.Frame(main_frame, bg=T.BG3)
        location_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(location_frame, text="Location:", bg=T.BG3, fg=T.TEXT,
                font=(T.UI, 10)).pack(anchor='w', pady=(0, 5))

        loc_entry_frame = tk.Frame(location_frame, bg=T.BG3)
        loc_entry_frame.pack(fill=tk.X)

        self.location_var = tk.StringVar(value=os.path.expanduser('~'))
        tk.Entry(loc_entry_frame, textvariable=self.location_var,
                font=(T.UI, 10), bg=T.BG, fg=T.TEXT).pack(
                    side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        tk.Button(loc_entry_frame, text="Browse...", command=self.browse_location,
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT).pack(side=tk.RIGHT)

        # Buttons
        button_frame = tk.Frame(self, bg=T.BG3)
        button_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Button(button_frame, text="Create Project", command=self.create_project,
                 bg=T.BLOOD, fg=T.TEXT, font=(T.UI, 10, 'bold'),
                 relief=tk.FLAT, padx=30, pady=8).pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="Cancel", command=self.destroy,
                 bg=T.HOVER, fg=T.TEXT, font=(T.UI, 10),
                 relief=tk.FLAT, padx=30, pady=8).pack(side=tk.RIGHT, padx=5)

    def on_template_select(self, event=None):
        """Handle template selection"""
        selection = self.template_list.curselection()
        if not selection:
            return

        idx = selection[0]
        template_key = list(self.templates.keys())[idx]
        template = self.templates[template_key]

        # Update description
        self.description_text.config(state='normal')
        self.description_text.delete('1.0', 'end')
        self.description_text.insert('1.0', f"{template.description}\n\nLanguage: {template.language}\n")
        if template.dependencies:
            deps = ', '.join(f"{k}: {len(v)}" for k, v in template.dependencies.items() if v)
            if deps:
                self.description_text.insert('end', f"Dependencies: {deps}\n")
        self.description_text.config(state='disabled')

        self.selected_template = template

    def browse_location(self):
        """Browse for project location"""
        directory = filedialog.askdirectory(initialdir=self.location_var.get())
        if directory:
            self.location_var.set(directory)

    def create_project(self):
        """Create project from template"""
        if not self.selected_template:
            messagebox.showwarning("Warning", "Please select a template")
            return

        project_name = self.name_var.get().strip()
        if not project_name:
            messagebox.showwarning("Warning", "Please enter a project name")
            return

        location = self.location_var.get()
        if not os.path.isdir(location):
            messagebox.showerror("Error", "Invalid location")
            return

        try:
            project_path = self.selected_template.create_project(location, project_name)
            messagebox.showinfo("Success", f"Project created at:\n{project_path}")

            # Open project in IDE
            if hasattr(self.ide, 'workspace_path'):
                self.ide.workspace_path = project_path

            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create project:\n{e}")
