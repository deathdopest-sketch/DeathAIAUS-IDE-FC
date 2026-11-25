# 🚀 Phase 1 Features - Quick Reference

## ⌨️ Keyboard Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+S` | Save | Save current file |
| `Ctrl+N` | New File | Create new untitled file |
| `Ctrl+W` | Close Tab | Close current tab |
| `Ctrl+F` | Find | Open find dialog |
| `Ctrl+H` | Replace | Open find & replace dialog |
| `Ctrl+P` | Quick Open | Quick file picker (if workspace loaded) |
| `Ctrl+Tab` | Next Tab | Switch to next tab |
| `Ctrl+Shift+Tab` | Previous Tab | Switch to previous tab |
| `Ctrl+/` | Toggle Comment | Comment/uncomment selected lines |
| `Ctrl+D` | Duplicate | Duplicate current line or selection |
| `Ctrl+Z` | Undo | Undo last change |
| `Ctrl+Y` | Redo | Redo last undone change |
| `Ctrl+A` | Select All | Select all text in editor |

## 📝 Multi-File Tabs

### Creating Files
- Click **"+ New"** button in tab bar
- Or press `Ctrl+N`
- Creates "Untitled-X" files

### Opening Files
- Double-click in file tree
- Or click **File menu → Open**
- Or drag into editor

### Switching Tabs
- Click tab with mouse
- Or use `Ctrl+Tab` / `Ctrl+Shift+Tab`

### Closing Tabs
- Click **×** button on tab
- Or press `Ctrl+W`
- Prompts to save if modified

### Modified Indicator
- Asterisk (*) appears on unsaved tabs
- Disappears after saving

## 🎨 Syntax Highlighting

### Supported Languages
- **Python** (.py files)
- **JavaScript** (.js, .jsx files)

### Color Scheme (VS Code Dark)
- **Keywords**: Blue (#569CD6)
- **Strings**: Orange (#CE9178)
- **Comments**: Green (#6A9955)
- **Functions**: Yellow (#DCDCAA)
- **Numbers**: Light green (#B5CEA8)
- **Classes**: Teal (#4EC9B0)
- **Decorators**: Purple (#C586C0)

### Features
- Real-time highlighting as you type
- Line numbers on the left
- Dark theme optimized for long coding sessions

## 💬 AI Chat Sidebar

### Sending Messages
1. Type your question in the input box
2. Press `Enter` or click **Send**
3. Shift+Enter for multi-line input

### Quick Actions
- **Explain** - "Explain this code"
- **Fix** - "Find and fix errors"
- **Improve** - "Suggest improvements"
- **Test** - "Write tests for this"

### Context Options
- ☑️ **Current file** - Includes open file in context
- ☐ **Project** - Includes entire project structure
- Toggle checkboxes to control what AI sees

### Chat Features
- Persistent conversation history
- Code blocks formatted with syntax highlighting
- Timestamps on each message
- Clear button (🗑️) to reset conversation

## 🔍 Find & Replace

### Opening
- Press `Ctrl+F` for Find
- Press `Ctrl+H` for Find & Replace
- Or click **🔍 Find** button in toolbar

### Search Options
- ☐ **Case sensitive** - Match exact case
- ☐ **Regex** - Use regular expressions
- ☐ **Whole word** - Match complete words only

### Scope
- **Current file** - Search only open file
- **All open files** - Search all tabs
- **Project** - Search entire workspace

### Actions
- **Find Next** - Jump to next match
- **Find Previous** - Jump to previous match
- **Find All** - Highlight all matches
- **Replace** - Replace current match
- **Replace All** - Replace all matches at once

### Tips
- Use `.*` in regex mode to match anything
- Case-insensitive by default
- Wraps around at end of file

## 🎯 Common Workflows

### Starting a New Project
1. Launch IDE (shows welcome screen)
2. Choose "Start New Project"
3. Enter name and language
4. Click "Create Project"

### Editing Multiple Files
1. Open files from tree or with Ctrl+O
2. Switch between tabs with Ctrl+Tab
3. Edit and save with Ctrl+S

### AI-Assisted Coding
1. Open or create a file
2. Write initial code
3. Ask AI in chat sidebar for help
4. Use Quick Actions for common tasks

### Finding & Replacing
1. Press Ctrl+F
2. Enter search term
3. Use Find Next or Find All
4. Switch to Replace if needed

### Using Keyboard Shortcuts
1. Keep fingers on home row
2. Use Ctrl+N for new files
3. Use Ctrl+W to close when done
4. Use Ctrl+/ to comment code quickly

## 🎨 Toolbar Buttons

| Button | Action |
|--------|--------|
| Load Project | Load existing project folder |
| Scan Project | Analyze project structure for AI |
| 🔍 Find | Open find dialog (Ctrl+F) |
| 📝 New | Create new file (Ctrl+N) |
| Save | Save current file (Ctrl+S) |
| Run | Execute current file |

## 💡 Pro Tips

1. **Fast File Creation**: Use Ctrl+N instead of menus
2. **Quick Tab Navigation**: Ctrl+Tab is faster than clicking
3. **Batch Commenting**: Select multiple lines, press Ctrl+/
4. **Regex Search**: Enable regex for powerful pattern matching
5. **AI Context**: Toggle "Current file" in AI chat for better help
6. **Duplicate Fast**: Ctrl+D duplicates lines instantly
7. **Clean Workspace**: Ctrl+W closes tabs quickly

## 🐛 Troubleshooting

### Tab Not Opening
- Check if file exists in workspace
- Try refreshing file tree
- Restart IDE if persistent

### Syntax Highlighting Not Working
- Verify file extension (.py, .js)
- Save file first
- Close and reopen tab

### Keyboard Shortcut Not Working
- Check if dialog is open
- Ensure focus is on editor
- Try clicking editor first

### AI Chat Not Responding
- Check LM Studio is running (localhost:1234)
- Verify model is loaded
- Check terminal for errors

## 📚 Additional Resources

- **Full Integration Guide**: See `INTEGRATE_PHASE1.md`
- **Component Details**: Check `components/` folder
- **Testing Guide**: See `TEST_PHASE1_NOW.md`
- **Complete Summary**: See `PHASE1_INTEGRATION_COMPLETE.md`

---

**Quick Start**: Launch IDE → Press Ctrl+N → Start coding → Ask AI for help!

