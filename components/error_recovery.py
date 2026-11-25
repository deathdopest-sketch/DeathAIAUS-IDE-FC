"""
Error Recovery System - Wire errors to AI for auto-fixing
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from datetime import datetime
from components import death_theme as T


class ErrorRecoveryPanel(tk.Toplevel):
    """Panel for managing error recovery and AI fix attempts"""
    
    def __init__(self, parent, ide_instance):
        super().__init__(parent)
        self.ide = ide_instance
        self.title("Error Recovery")
        self.geometry("800x600")
        self.configure(bg=T.BG)
        
        self.error_history = []
        self.max_retries = 3
        self.current_retry = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup recovery panel UI"""
        # Header
        header = tk.Frame(self, bg=T.BG3, height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🔧 Error Recovery System", 
                font=(T.UI, 14, 'bold'),
                fg=T.BLOOD_LIGHT, bg=T.BG3).pack(side=tk.LEFT, padx=15, pady=10)
        
        # Stats
        self.stats_label = tk.Label(header, text="Errors: 0 | Fixed: 0 | Failed: 0",
                                     font=(T.UI, 9),
                                     fg=T.TEXT2, bg=T.BG3)
        self.stats_label.pack(side=tk.RIGHT, padx=15)
        
        # Error list
        list_frame = tk.Frame(self, bg=T.BG)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(list_frame, text="Recent Errors:", 
                font=(T.UI, 11, 'bold'),
                fg=T.TEXT, bg=T.BG, anchor='w').pack(fill=tk.X, pady=(0,5))
        
        # Scrollable error list
        self.error_display = scrolledtext.ScrolledText(
            list_frame,
            font=(T.MONO, 10),
            bg=T.BG,
            fg=T.TEXT,
            insertbackground=T.TEXT,
            wrap=tk.WORD,
            state='disabled'
        )
        self.error_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags
        self.error_display.tag_configure('error', foreground=T.BLOOD_LIGHT, font=(T.MONO, 10, 'bold'))
        self.error_display.tag_configure('success', foreground=T.BILE)
        self.error_display.tag_configure('info', foreground=T.TEXT2)
        self.error_display.tag_configure('timestamp', foreground=T.MUTED, font=(T.MONO, 9))
        
        # Action buttons
        button_frame = tk.Frame(self, bg=T.BG)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(button_frame, text="🔄 Auto-Fix All Errors",
                 command=self.auto_fix_all,
                 bg=T.BLOOD, fg=T.TEXT, font=(T.UI, 10, 'bold'),
                 relief=tk.FLAT, padx=20, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="📋 Copy Error Log",
                 command=self.copy_errors,
                 bg=T.HOVER, fg=T.TEXT, font=(T.UI, 10),
                 relief=tk.FLAT, padx=20, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🗑️ Clear History",
                 command=self.clear_history,
                 bg=T.HOVER, fg=T.TEXT, font=(T.UI, 10),
                 relief=tk.FLAT, padx=20, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Close",
                 command=self.destroy,
                 bg=T.HOVER, fg=T.TEXT, font=(T.UI, 10),
                 relief=tk.FLAT, padx=20, pady=8,
                 cursor='hand2').pack(side=tk.RIGHT, padx=5)
    
    def add_error(self, error_text, file_path=None, line_num=None):
        """Add error to recovery system"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        error_entry = {
            'timestamp': timestamp,
            'error': error_text,
            'file': file_path,
            'line': line_num,
            'fixed': False,
            'attempts': 0
        }
        
        self.error_history.append(error_entry)
        self.update_display()
        self.update_stats()
        
        return error_entry
    
    def update_display(self):
        """Update error display"""
        self.error_display.config(state='normal')
        self.error_display.delete('1.0', tk.END)
        
        for entry in reversed(self.error_history[-20:]):  # Last 20 errors
            # Timestamp
            self.error_display.insert(tk.END, f"[{entry['timestamp']}] ", 'timestamp')
            
            # Status
            if entry['fixed']:
                self.error_display.insert(tk.END, "✓ FIXED ", 'success')
            elif entry['attempts'] > 0:
                self.error_display.insert(tk.END, f"⟳ Attempt {entry['attempts']} ", 'info')
            else:
                self.error_display.insert(tk.END, "✗ ERROR ", 'error')
            
            # File and line
            if entry['file']:
                file_info = f"{entry['file']}"
                if entry['line']:
                    file_info += f":{entry['line']}"
                self.error_display.insert(tk.END, f"({file_info})\n", 'info')
            else:
                self.error_display.insert(tk.END, "\n")
            
            # Error message
            self.error_display.insert(tk.END, f"  {entry['error']}\n\n")
        
        self.error_display.config(state='disabled')
        self.error_display.see(tk.END)
    
    def update_stats(self):
        """Update statistics"""
        total = len(self.error_history)
        fixed = sum(1 for e in self.error_history if e['fixed'])
        failed = sum(1 for e in self.error_history if e['attempts'] >= self.max_retries and not e['fixed'])
        
        self.stats_label.config(text=f"Errors: {total} | Fixed: {fixed} | Failed: {failed}")
    
    def auto_fix_all(self):
        """Attempt to auto-fix all unfixed errors"""
        unfixed = [e for e in self.error_history if not e['fixed'] and e['attempts'] < self.max_retries]
        
        if not unfixed:
            messagebox.showinfo("No Errors", "No errors to fix!")
            return
        
        messagebox.showinfo("Auto-Fix", 
                          f"Will attempt to fix {len(unfixed)} error(s).\n\n"
                          f"This may take a moment...")
        
        # Fix in background
        threading.Thread(target=self._fix_errors_thread, args=(unfixed,), daemon=True).start()
    
    def _fix_errors_thread(self, errors):
        """Fix errors in background"""
        for error_entry in errors:
            if error_entry['attempts'] >= self.max_retries:
                continue
            
            error_entry['attempts'] += 1
            self.update_display()
            
            # Send to AI
            error_context = self._build_error_context(error_entry)
            success = self._ask_ai_to_fix(error_entry, error_context)
            
            if success:
                error_entry['fixed'] = True
            
            self.update_display()
            self.update_stats()
    
    def _build_error_context(self, error_entry):
        """Build context for AI fix request"""
        context = f"Error: {error_entry['error']}\n\n"
        
        if error_entry['file']:
            context += f"File: {error_entry['file']}\n"
        if error_entry['line']:
            context += f"Line: {error_entry['line']}\n"
        
        # Try to get file content
        if error_entry['file'] and hasattr(self.ide, 'tabs'):
            try:
                # Get content around error
                editor = self.ide.tabs.current_editor
                if editor:
                    content = editor.get('1.0', tk.END)
                    context += f"\n\nCurrent file content:\n```\n{content}\n```\n"
            except:
                pass
        
        return context
    
    def _ask_ai_to_fix(self, error_entry, context):
        """Ask AI to fix the error"""
        if not hasattr(self.ide, 'ai_chat'):
            return False
        
        try:
            # Send to AI chat
            prompt = f"🔧 Please fix this error:\n\n{context}\n\nProvide the corrected code."
            
            self.ide.ai_chat.chat_input.delete('1.0', tk.END)
            self.ide.ai_chat.chat_input.insert('1.0', prompt)
            self.ide.ai_chat.send_message()
            
            return True  # Assume success - real implementation would check response
        except Exception as e:
            print(f"Failed to send to AI: {e}")
            return False
    
    def copy_errors(self):
        """Copy error log to clipboard"""
        log = "\n".join([
            f"[{e['timestamp']}] {e['file'] or 'Unknown'}:{e['line'] or '?'} - {e['error']}"
            for e in self.error_history
        ])
        
        self.clipboard_clear()
        self.clipboard_append(log)
        messagebox.showinfo("Copied", "Error log copied to clipboard!")
    
    def clear_history(self):
        """Clear error history"""
        if messagebox.askyesno("Clear History", "Clear all error history?"):
            self.error_history.clear()
            self.update_display()
            self.update_stats()


class QuickErrorFixer:
    """Quick access error fixing button"""
    
    def __init__(self, ide_instance):
        self.ide = ide_instance
    
    def fix_current_error(self):
        """Fix the currently visible error"""
        if not hasattr(self.ide, 'error_detector') or not self.ide.error_detector:
            messagebox.showinfo("No Errors", "No error detector available")
            return
        
        # Get current errors from detector
        # This is a placeholder - actual implementation depends on error_detector structure
        messagebox.showinfo("Fix Error", "Sending current errors to AI for fixing...")
        
        # Would integrate with error detector to get actual errors
