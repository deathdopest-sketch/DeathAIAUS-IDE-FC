#!/usr/bin/env python3
"""
DeathAIAUS IDE Launcher
Professional launcher with branded splash screen that starts the DeathAIAUS Python Backend,
then launches the IDE only when the backend is ready.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import requests
import logging
import os
import sys
import signal
import psutil
from datetime import datetime
from pathlib import Path


class LauncherSplash:
    """Branded splash screen with progress tracking"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DeathAIAUS IDE Launcher")
        self.root.geometry("700x450")
        self.root.resizable(False, False)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.root.winfo_screenheight() // 2) - (450 // 2)
        self.root.geometry(f"700x450+{x}+{y}")
        
        # Set window icon
        try:
            icon_paths = [
                Path("assets/icon_32.ico"),
                Path("assets/icon.ico"),
                Path("assets/icon.png")
            ]
            
            for icon_path in icon_paths:
                if icon_path.exists():
                    if icon_path.suffix == '.ico':
                        self.root.iconbitmap(str(icon_path))
                    else:
                        self.root.iconphoto(True, tk.PhotoImage(file=str(icon_path)))
                    break
        except Exception as e:
            print(f"Could not set icon: {e}")
        
        # Configure dark theme
        self.root.configure(bg='#1a1a1a')
        
        # Create main frame
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # ASCII Art
        ascii_art = """▓█████▄ ▓█████ ▄▄▄      ▄▄▄█████▓ ██░ ██  ▄▄▄       ██▓ ▄▄▄       █    ██   ██████ 
▒██▀ ██▌▓█   ▀▒████▄    ▓  ██▒ ▓▒▓██░ ██▒▒████▄    ▓██▒▒████▄     ██  ▓██▒▒██    ▒ 
░██   █▌▒███  ▒██  ▀█▄  ▒ ▓██░ ▒░▒██▀▀██░▒██  ▀█▄  ▒██▒▒██  ▀█▄  ▓██  ▒██░░ ▓██▄   
░▓█▄   ▌▒▓█  ▄░██▄▄▄▄██ ░ ▓██▓ ░ ░▓█ ░██ ░██▄▄▄▄██ ░██░░██▄▄▄▄██ ▓▓█  ░██░  ▒   ██▒
░▒████▓ ░▒████▒▓█   ▓██▒  ▒██▒ ░ ░▓█▒░██▓ ▓█   ▓██▒░██░ ▓█   ▓██▒▒▒█████▓ ▒██████▒▒
 ▒▒▓  ▒ ░░ ▒░ ░▒▒   ▓▒█░  ▒ ░░    ▒ ░░▒░▒ ▒▒   ▓▒█░░▓   ▒▒   ▓▒█░░▒▓▒ ▒ ▒ ▒ ▒▓▒ ▒ ░
 ░ ▒  ▒  ░ ░  ░ ▒   ▒▒ ░    ░     ▒ ░▒░ ░  ▒   ▒▒ ░ ▒ ░  ▒   ▒▒ ░░░▒░ ░ ░ ░ ░▒  ░ ░
 ░ ░  ░    ░    ░   ▒     ░       ░  ░░ ░  ░   ▒    ▒ ░  ░   ▒    ░░░ ░ ░ ░  ░  ░  
   ░       ░  ░     ░  ░          ░  ░  ░      ░  ░ ░        ░  ░   ░           ░  
 ░                                                                                """
        
        # ASCII Art Label
        ascii_label = tk.Label(main_frame, text=ascii_art, 
                              font=('Courier New', 8), 
                              fg='#00ff00', bg='#1a1a1a',
                              justify=tk.LEFT)
        ascii_label.pack(pady=(0, 10))
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="IDE FC Powered By DeathAIAUS Models",
                              font=('Arial', 14, 'bold'),
                              fg='#ffffff', bg='#1a1a1a')
        title_label.pack(pady=(0, 5))
        
        # Copyright
        copyright_label = tk.Label(main_frame,
                                  text="© DeathAIAUS 2025",
                                  font=('Arial', 10),
                                  fg='#888888', bg='#1a1a1a')
        copyright_label.pack(pady=(0, 20))
        
        # Status label
        self.status_label = tk.Label(main_frame,
                                    text="Initializing...",
                                    font=('Arial', 11),
                                    fg='#ffffff', bg='#1a1a1a')
        self.status_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, 
                                       length=400, 
                                       mode='determinate',
                                       style='TProgressbar')
        self.progress.pack(pady=(0, 20))
        
        # Configure progress bar style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TProgressbar',
                       background='#00ff00',
                       troughcolor='#333333',
                       borderwidth=0,
                       lightcolor='#00ff00',
                       darkcolor='#00ff00')
        
        # Error label (initially hidden)
        self.error_label = tk.Label(main_frame,
                                   text="",
                                   font=('Arial', 10),
                                   fg='#ff4444', bg='#1a1a1a',
                                   wraplength=600)
        self.error_label.pack(pady=(0, 10))
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg='#1a1a1a')
        buttons_frame.pack(pady=(10, 0))
        
        # Retry button (initially hidden)
        self.retry_button = tk.Button(buttons_frame,
                                     text="Retry",
                                     command=self.retry_launch,
                                     bg='#333333',
                                     fg='#ffffff',
                                     font=('Arial', 10),
                                     padx=20,
                                     pady=5,
                                     relief=tk.FLAT)
        
        # Exit button (initially hidden)
        self.exit_button = tk.Button(buttons_frame,
                                    text="Exit",
                                    command=self.root.quit,
                                    bg='#333333',
                                    fg='#ffffff',
                                    font=('Arial', 10),
                                    padx=20,
                                    pady=5,
                                    relief=tk.FLAT)
        
        # Bottom ASCII Art
        bottom_ascii_label = tk.Label(main_frame, text=ascii_art, 
                                     font=('Courier New', 6), 
                                     fg='#00ff00', bg='#1a1a1a',
                                     justify=tk.LEFT)
        bottom_ascii_label.pack(side=tk.BOTTOM, pady=(20, 0))
        
        self.retry_callback = None
    
    def update_status(self, message, progress_value=None):
        """Update status message and progress bar"""
        def update():
            self.status_label.config(text=message)
            if progress_value is not None:
                self.progress['value'] = progress_value
            self.root.update_idletasks()
        
        self.root.after(0, update)
    
    def show_error(self, error_message):
        """Show error message and retry button"""
        def update():
            self.error_label.config(text=error_message)
            self.retry_button.pack(side=tk.LEFT, padx=(0, 10))
            self.exit_button.pack(side=tk.LEFT)
            self.root.update_idletasks()
        
        self.root.after(0, update)
    
    def show_success(self, message):
        """Show success message"""
        def update():
            self.status_label.config(text=message, fg='#00ff00')
            self.progress['value'] = 100
            self.root.update_idletasks()
        
        self.root.after(0, update)
    
    def retry_launch(self):
        """Retry the launch process"""
        if self.retry_callback:
            self.retry_callback()
    
    def close(self):
        """Close the splash screen"""
        def close_window():
            self.root.destroy()
        
        self.root.after(0, close_window)


class BackendManager:
    """Manages DeathAIAUS Python Backend startup"""
    
    def __init__(self, logger):
        self.logger = logger
        self.backend_path = Path("DeathAIAUS_Backend.py")
        
    def check_backend_ready(self):
        """Check if DeathAIAUS Backend is ready"""
        exists = self.backend_path.exists()
        self.logger.info(f"DeathAIAUS_Backend.py exists: {exists}")
        return exists
        
    def check_dependencies(self):
        """Check if required Python dependencies are installed"""
        try:
            import fastapi
            import uvicorn
            import llama_cpp
            self.logger.info("All Python dependencies are installed")
            return True
        except ImportError as e:
            self.logger.error(f"Missing dependency: {e}")
            return False
    
    def start_backend(self, progress_callback):
        """Start DeathAIAUS Python Backend"""
        try:
            self.logger.info("Starting DeathAIAUS Python Backend")
            progress_callback("Starting DeathAIAUS Backend...", 50)
            
            # Kill any existing backend processes
            try:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['cmdline'] and 'DeathAIAUS_Backend.py' in ' '.join(proc.info['cmdline']):
                            self.logger.info(f"Killing existing backend process: {proc.info['pid']}")
                            proc.kill()
                    except:
                        pass
                time.sleep(1)
            except ImportError:
                pass
            
            # Start backend process
            process = subprocess.Popen([
                sys.executable, str(self.backend_path)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.logger.info(f"DeathAIAUS Backend started with PID: {process.pid}")
            progress_callback("Backend starting...", 75)
            
            # Wait for backend to be ready
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                try:
                    response = requests.get("http://localhost:8888/health", timeout=2)
                    if response.status_code == 200:
                        self.logger.info("DeathAIAUS Backend is ready!")
                        progress_callback("Backend ready!", 100)
                        return process, None
                except:
                    continue
            
            # If we get here, backend didn't start properly
            process.terminate()
            return None, "Backend failed to start within 30 seconds"
            
        except Exception as e:
            self.logger.error(f"Failed to start DeathAIAUS Backend: {e}")
            return None, str(e)


class Launcher:
    """Main launcher class"""
    
    def __init__(self):
        self.setup_logging()
        self.splash = LauncherSplash()
        self.backend_manager = BackendManager(self.logger)
        self.backend_process = None
        self.retry_count = 0
        self.max_retries = 3
        
        # Set up retry callback
        self.splash.retry_callback = self.retry_launch
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / "launcher.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def launch_sequence(self):
        """Main launch sequence"""
        try:
            self.logger.info("Starting DeathAIAUS IDE launch sequence")
            
            # Check backend file exists
            self.splash.update_status("Checking DeathAIAUS Backend...", 10)
            if not self.backend_manager.check_backend_ready():
                raise Exception("DeathAIAUS_Backend.py not found")
            
            # Check dependencies
            self.splash.update_status("Checking dependencies...", 20)
            if not self.backend_manager.check_dependencies():
                raise Exception("Missing Python dependencies. Run: pip install llama-cpp-python[server]")
            
            # Start backend
            self.splash.update_status("Starting DeathAIAUS Backend...", 30)
            process, error = self.backend_manager.start_backend(self.splash.update_status)
            
            if process is None:
                raise Exception(f"Failed to start backend: {error}")
            
            self.backend_process = process
            
            # Wait a moment for backend to fully initialize
            time.sleep(2)
            
            # Launch IDE
            self.splash.update_status("Launching DeathAIAUS IDE...", 90)
            self.launch_ide()
            
            # Show success
            self.splash.show_success("DeathAIAUS IDE launched successfully!")
            time.sleep(2)
            
            # Close splash screen
            self.splash.close()
            
        except Exception as e:
            self.logger.error(f"Launch sequence failed: {e}")
            self.splash.show_error(f"Launch failed: {str(e)}")
    
    def launch_ide(self):
        """Launch the DeathAIAUS IDE"""
        try:
            # Try hybrid IDE first, fall back to Tkinter version
            ide_path = Path("deathaius_ide_hybrid.py")
            if not ide_path.exists():
                ide_path = Path("deathaius_ide_fc.py")
            
            if not ide_path.exists():
                raise Exception("IDE not found (tried hybrid and fc versions)")
            
            # Start IDE in separate process
            subprocess.Popen([sys.executable, str(ide_path)], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            self.logger.info("DeathAIAUS IDE launched successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to launch IDE: {e}")
            raise
    
    def retry_launch(self):
        """Retry the launch process"""
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            self.logger.info(f"Retrying launch (attempt {self.retry_count}/{self.max_retries})")
            
            # Hide error elements
            self.splash.error_label.config(text="")
            self.splash.retry_button.pack_forget()
            self.splash.exit_button.pack_forget()
            
            # Start new launch sequence
            launch_thread = threading.Thread(target=self.launch_sequence, daemon=True)
            launch_thread.start()
        else:
            self.splash.show_error("Maximum retry attempts reached. Please check the logs.")
    
    def run(self):
        """Run the launcher"""
        # Start launch sequence in background thread
        launch_thread = threading.Thread(target=self.launch_sequence, daemon=True)
        launch_thread.start()
        
        # Start the GUI main loop
        try:
            self.splash.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            # Clean up backend process
            if self.backend_process:
                try:
                    self.logger.info("Stopping DeathAIAUS Backend process")
                    self.backend_process.terminate()
                    try:
                        self.backend_process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.backend_process.kill()
                        self.backend_process.wait()
                except Exception as e:
                    self.logger.error(f"Error stopping backend: {e}")


def main():
    """Main entry point"""
    try:
        launcher = Launcher()
        launcher.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
