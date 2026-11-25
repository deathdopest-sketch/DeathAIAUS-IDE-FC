"""
Simple Theme Selector - Quick theme switching
"""
import tkinter as tk
from tkinter import ttk, messagebox

class SimpleThemeSelector(tk.Toplevel):
    """Simple dialog for quickly switching themes"""
    
    def __init__(self, parent, theme_manager):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.title("Select Theme")
        self.geometry("400x500")
        self.configure(bg='#2d2d2d')
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.selected_theme = None
        self.setup_ui()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup simple UI"""
        # Header
        header = tk.Frame(self, bg='#1e1e1e', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🎨 Choose Theme", 
                font=('Segoe UI', 14, 'bold'),
                fg='#00ff00', bg='#1e1e1e').pack(pady=15)
        
        # Theme list
        list_frame = tk.Frame(self, bg='#2d2d2d')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Scrollable listbox
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.theme_listbox = tk.Listbox(
            list_frame,
            bg='#1e1e1e',
            fg='#ffffff',
            selectbackground='#0066cc',
            selectforeground='#ffffff',
            font=('Segoe UI', 11),
            bd=0,
            highlightthickness=1,
            highlightbackground='#444444',
            highlightcolor='#0066cc',
            yscrollcommand=scrollbar.set
        )
        self.theme_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.theme_listbox.yview)
        
        # Add themes
        all_themes = self.theme_manager.get_all_themes()
        current_theme_name = self.theme_manager.current_theme.name
        
        for i, theme_name in enumerate(sorted(all_themes.keys())):
            display_name = f"  {theme_name}"
            if theme_name == current_theme_name:
                display_name = f"✓ {theme_name} (current)"
            self.theme_listbox.insert(tk.END, display_name)
            
            # Select current theme
            if theme_name == current_theme_name:
                self.theme_listbox.selection_set(i)
                self.theme_listbox.see(i)
        
        # Double-click to apply
        self.theme_listbox.bind('<Double-Button-1>', lambda e: self.apply_theme())
        
        # Preview frame
        preview_frame = tk.Frame(self, bg='#2d2d2d')
        preview_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        tk.Label(preview_frame, text="💡 Tip: Double-click to apply instantly",
                font=('Segoe UI', 9, 'italic'), fg='#888888', bg='#2d2d2d').pack()
        
        # Buttons
        button_frame = tk.Frame(self, bg='#2d2d2d')
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        tk.Button(button_frame, text="✓ Apply Theme", 
                 command=self.apply_theme,
                 bg='#00aa00', fg='white', 
                 font=('Segoe UI', 11, 'bold'),
                 relief=tk.FLAT, padx=30, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", 
                 command=self.destroy,
                 bg='#3d3d3d', fg='#cccccc', 
                 font=('Segoe UI', 10),
                 relief=tk.FLAT, padx=20, pady=8,
                 cursor='hand2').pack(side=tk.RIGHT, padx=5)
        
        # Keyboard shortcuts
        self.bind('<Return>', lambda e: self.apply_theme())
        self.bind('<Escape>', lambda e: self.destroy())
    
    def apply_theme(self):
        """Apply selected theme"""
        selection = self.theme_listbox.curselection()
        if not selection:
            messagebox.showinfo("Select Theme", "Please select a theme first")
            return
        
        # Get theme name (remove markers)
        theme_text = self.theme_listbox.get(selection[0])
        theme_name = theme_text.replace('✓ ', '').replace('  ', '').replace(' (current)', '').strip()
        
        # Apply theme
        try:
            self.theme_manager.apply_theme(theme_name)
            self.selected_theme = theme_name
            messagebox.showinfo("Theme Applied", 
                              f"✓ Theme '{theme_name}' applied successfully!\n\nYour IDE colors have been updated.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply theme: {e}")

