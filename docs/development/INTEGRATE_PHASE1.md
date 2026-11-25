# 🚀 Phase 1 Integration Guide

All Phase 1 features are complete! Here's how to integrate them into your main IDE.

## ✅ Components Created:

1. **components/code_editor.py** - Enhanced editor with syntax highlighting
2. **components/ai_chat.py** - Persistent AI chat sidebar
3. **components/file_tabs.py** - Multi-file tab system
4. **components/shortcuts.py** - Keyboard shortcuts handler
5. **components/search.py** - Find and replace dialog

---

## 📋 Integration Steps:

### Step 1: Import Components
Add these imports at the top of `deathaius_ide_fc.py`:

```python
from components.file_tabs import FileTabs
from components.shortcuts import ShortcutsHandler
from components.search import SearchDialog
from components.ai_chat import AIChatInterface
```

### Step 2: Update IDE Layout
Replace the current editor setup with the new tab system.

**Find this section** (around line 400-500 in `setup_gui()`):
```python
# OLD CODE - Remove this:
self.code_editor = scrolledtext.ScrolledText(
    editor_frame,
    wrap=tk.WORD,
    font=('Consolas', 11),
    bg='#1e1e1e',
    fg='#d4d4d4',
    insertbackground='white',
    undo=True,
    maxundo=-1
)
self.code_editor.pack(fill=tk.BOTH, expand=True)
```

**Replace with:**
```python
# NEW CODE - Multi-file tab system with enhanced editor:
self.tabs = FileTabs(editor_frame, self)
self.tabs.pack(fill=tk.BOTH, expand=True)

# For backward compatibility, create a property
@property
def code_editor(self):
    """Get current editor for backward compatibility"""
    return self.tabs.current_editor if self.tabs.current_editor else None
```

### Step 3: Add AI Chat Sidebar
In `setup_gui()`, find where the main paned window is created and add a chat section.

**Find this:**
```python
main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
```

**After creating main_paned and adding editor_frame, add:**
```python
# AI Chat sidebar (right side)
chat_frame = tk.Frame(main_paned, bg='#2d2d2d', width=400)
main_paned.add(chat_frame, weight=1)

self.ai_chat = AIChatInterface(chat_frame, self)
self.ai_chat.pack(fill=tk.BOTH, expand=True)
```

### Step 4: Setup Keyboard Shortcuts
In `__init__()`, after creating the root window:

```python
# Keyboard shortcuts
self.shortcuts = ShortcutsHandler(self)
self.shortcuts.bind_all(self.root)
```

### Step 5: Setup Search Dialog
In `__init__()`, add:

```python
# Search dialog
self.search_dialog = SearchDialog(self)
```

### Step 6: Update File Operations
Update `open_file()` to use the new tab system:

**Find:**
```python
def open_file(self, filepath=None):
    if not filepath:
        filepath = filedialog.askopenfilename(...)

    if filepath:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        self.code_editor.delete("1.0", tk.END)
        self.code_editor.insert("1.0", content)
        self.current_file = filepath
```

**Replace with:**
```python
def open_file(self, filepath=None):
    if not filepath:
        filepath = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("Python files", "*.py"),
                ("JavaScript files", "*.js"),
                ("All files", "*.*")
            ]
        )

    if filepath:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add to tab system
        self.tabs.add_tab(filepath, content)
        self.current_file = filepath
```

### Step 7: Update Save Operations
Update `save_file()`:

**Find:**
```python
def save_file(self):
    if not self.current_file:
        # Save as...
        filepath = filedialog.asksaveasfilename(...)
        if filepath:
            self.current_file = filepath

    if self.current_file:
        content = self.code_editor.get("1.0", tk.END)
        with open(self.current_file, 'w', encoding='utf-8') as f:
            f.write(content)
```

**Replace with:**
```python
def save_file(self):
    if not self.current_file or self.current_file.startswith("Untitled"):
        # Save as...
        filepath = filedialog.asksaveasfilename(
            title="Save File",
            defaultextension=".py",
            filetypes=[
                ("Python files", "*.py"),
                ("JavaScript files", "*.js"),
                ("All files", "*.*")
            ]
        )
        if filepath:
            # Remove old untitled tab if exists
            if self.current_file and self.current_file.startswith("Untitled"):
                old_file = self.current_file
                self.current_file = filepath
                if old_file in self.tabs.tabs:
                    # Update tab instead of closing
                    tab_data = self.tabs.tabs[old_file]
                    del self.tabs.tabs[old_file]
                    self.tabs.tabs[filepath] = tab_data
            else:
                self.current_file = filepath

    if self.current_file:
        content = self.tabs.get_current_content()
        with open(self.current_file, 'w', encoding='utf-8') as f:
            f.write(content)

        # Mark as saved
        self.tabs.save_current()
        self.status_bar.config(text=f"💾 Saved: {self.current_file}")
```

### Step 8: Update Streaming Execution
The streaming file writer should work with tabs. Update `execute_tools_with_streaming()`:

**Find where files are written and add:**
```python
# After writing file, open in tab if it's in workspace
if self.workspace_path and full_path.startswith(self.workspace_path):
    relative_path = os.path.relpath(full_path, self.workspace_path)
    # Open in new tab
    self.tabs.add_tab(full_path, content)
```

---

## 🎨 Optional Enhancements:

### Add Toolbar Buttons
In `setup_gui()`, add buttons for new features:

```python
# In the toolbar section, add:
tk.Button(toolbar, text="🔍 Find", command=self.search_dialog.show_find,
         bg='#3d3d3d', fg='#00ff00', relief=tk.FLAT).pack(side=tk.LEFT, padx=2)

tk.Button(toolbar, text="📝 New", command=self.tabs.new_file,
         bg='#3d3d3d', fg='#00ff00', relief=tk.FLAT).pack(side=tk.LEFT, padx=2)
```

### Add View Menu
Create a menu for toggling chat sidebar:

```python
view_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='#00ff00')
menubar.add_cascade(label="View", menu=view_menu)

def toggle_chat():
    if self.ai_chat.winfo_viewable():
        self.ai_chat.pack_forget()
    else:
        self.ai_chat.pack(fill=tk.BOTH, expand=True)

view_menu.add_command(label="Toggle AI Chat", command=toggle_chat)
```

### Add Quick Open (Ctrl+P)
Add this method to your IDE class:

```python
def show_quick_open(self):
    """Quick file open dialog"""
    if not self.workspace_path:
        return

    # Create quick open dialog
    dialog = tk.Toplevel(self.root)
    dialog.title("Quick Open")
    dialog.geometry("600x400")
    dialog.configure(bg='#2d2d2d')

    # Search field
    search_var = tk.StringVar()
    search_entry = tk.Entry(dialog, textvariable=search_var,
                           font=('Arial', 12), bg='#1e1e1e', fg='#cccccc')
    search_entry.pack(fill=tk.X, padx=10, pady=10)
    search_entry.focus()

    # File list
    listbox = tk.Listbox(dialog, bg='#1e1e1e', fg='#cccccc',
                        font=('Arial', 10), selectbackground='#0066cc')
    listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Get all files in workspace
    all_files = []
    for root, dirs, files in os.walk(self.workspace_path):
        for file in files:
            if file.endswith(('.py', '.js', '.txt', '.md')):
                rel_path = os.path.relpath(os.path.join(root, file), self.workspace_path)
                all_files.append(rel_path)

    def update_list(*args):
        listbox.delete(0, tk.END)
        search_text = search_var.get().lower()
        for file in all_files:
            if search_text in file.lower():
                listbox.insert(tk.END, file)

    def open_selected(event=None):
        selection = listbox.curselection()
        if selection:
            file = listbox.get(selection[0])
            full_path = os.path.join(self.workspace_path, file)
            self.open_file(full_path)
            dialog.destroy()

    search_var.trace('w', update_list)
    listbox.bind('<Double-Button-1>', open_selected)
    search_entry.bind('<Return>', open_selected)

    # Initial population
    update_list()
```

---

## 🧪 Testing After Integration:

1. **Launch IDE**: `python deathaius_ide_fc.py`
2. **Test Tabs**: Click "+ New", open multiple files
3. **Test Shortcuts**:
   - Ctrl+S (save)
   - Ctrl+F (find)
   - Ctrl+N (new file)
   - Ctrl+W (close tab)
   - Ctrl+Tab (next tab)
4. **Test Search**: Ctrl+F, search for text, try regex
5. **Test AI Chat**: Ask questions, use quick actions
6. **Test Syntax Highlighting**: Type Python/JavaScript code

---

## ⚠️ Potential Issues:

### Issue 1: Code Editor Reference
Some functions might still reference `self.code_editor` directly. Update them to use:
```python
editor = self.tabs.current_editor if self.tabs.current_editor else None
if not editor:
    return
# Use editor instead of self.code_editor
```

### Issue 2: File Context for AI
The AI chat needs to access current file content. Make sure:
```python
# In ai_chat.py, _build_context() expects:
self.ide.tabs.current_editor  # The current editor widget
self.ide.current_file         # The current file path
```

### Issue 3: Modified Tracking
Connect editor modifications to tab system:
```python
# In FileTabs.add_tab(), after creating editor:
def on_modify(event=None):
    self.mark_modified(filepath, True)

editor.bind('<<Modified>>', on_modify)
```

---

## 🎯 Summary:

**Replace:**
- Old `scrolledtext.ScrolledText` → `FileTabs` with `EnhancedCodeEditor`

**Add:**
- AI chat sidebar
- Keyboard shortcuts
- Search dialog

**Update:**
- File operations (open, save)
- References to `code_editor`

After integration, you'll have:
- ✅ Professional code editor with syntax highlighting
- ✅ Multi-file tabs
- ✅ Persistent AI chat
- ✅ Full keyboard shortcuts
- ✅ Find & replace

Ready for **Phase 2** features! 🚀
