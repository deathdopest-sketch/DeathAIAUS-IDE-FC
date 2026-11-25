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
import shutil
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
            # Try ICO files (better for Windows)
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
                        # PNG fallback
                        icon = tk.PhotoImage(file=str(icon_path))
                        self.root.iconphoto(True, icon)
                    break
        except Exception as e:
            # Icon loading failed, continue without it
            pass
        
        # Dark theme
        self.root.configure(bg='#2b2b2b')
        
        # ASCII Logo
        self.ascii_logo = """▓█████▄ ▓█████  ▄▄▄      ▄▄▄█████▓ ██░ ██  ▄▄▄       ██▓ ▄▄▄       █    ██   ██████ 
▒██▀ ██▌▓█   ▀ ▒████▄    ▓  ██▒ ▓▒▓██░ ██▒▒████▄    ▓██▒▒████▄     ██  ▓██▒▒██    ▒ 
░██   █▌▒███   ▒██  ▀█▄  ▒ ▓██░ ▒░▒██▀▀██░▒██  ▀█▄  ▒██▒▒██  ▀█▄  ▓██  ▒██░░ ▓██▄   
░▓█▄   ▌▒▓█  ▄ ░██▄▄▄▄██ ░ ▓██▓ ░ ░▓█ ░██ ░██▄▄▄▄██ ░██░░██▄▄▄▄██ ▓▓█  ░██░  ▒   ██▒
░▒████▓ ░▒████▒ ▓█   ▓██▒  ▒██▒ ░ ░▓█▒░██▓ ▓█   ▓██▒░██░ ▓█   ▓██▒▒▒█████▓ ▒██████▒▒
 ▒▒▓  ▒ ░░ ▒░ ░ ▒▒   ▓▒█░  ▒ ░░    ▒ ░░▒░▒ ▒▒   ▓▒█░░▓   ▒▒   ▓▒█░░▒▓▒ ▒ ▒ ▒ ▒▓▒ ▒ ░
 ░ ▒  ▒  ░ ░  ░  ▒   ▒▒ ░    ░     ▒ ░▒░ ░  ▒   ▒▒ ░ ▒ ░  ▒   ▒▒ ░░░▒░ ░ ░ ░ ░▒  ░ ░
 ░ ░  ░    ░     ░   ▒     ░       ░  ░░ ░  ░   ▒    ▒ ░  ░   ▒    ░░░ ░ ░ ░  ░  ░  
   ░       ░  ░      ░  ░          ░  ░  ░      ░  ░ ░        ░  ░   ░           ░  
 ░                                                                                  """
        
        self.setup_ui()
        self.progress_value = 0
        self.error_state = False
        
    def setup_ui(self):
        """Setup the UI components"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # ASCII Logo
        logo_frame = tk.Frame(main_frame, bg='#2b2b2b')
        logo_frame.pack(pady=(0, 10))
        
        logo_label = tk.Label(logo_frame, text=self.ascii_logo, 
                             font=('Courier New', 7), fg='#00ffff', bg='#2b2b2b')
        logo_label.pack()
        
        # IDE FC text
        ide_label = tk.Label(main_frame, text="IDE FC", 
                            font=('Arial', 16, 'bold'), fg='#00ffff', bg='#2b2b2b')
        ide_label.pack(pady=(0, 5))
        
        # Powered by text
        powered_label = tk.Label(main_frame, text="Powered By DeathAIAUS Models", 
                                font=('Arial', 10), fg='#e0e0e0', bg='#2b2b2b')
        powered_label.pack(pady=(0, 20))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, length=500, mode='determinate')
        self.progress.pack(pady=(0, 10))
        
        # Status label
        self.status_label = tk.Label(main_frame, text="Initializing...", 
                                    font=('Arial', 10), fg='#ffffff', bg='#2b2b2b')
        self.status_label.pack(pady=(0, 20))
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#2b2b2b')
        button_frame.pack(pady=(0, 20))
        
        # Retry button (hidden by default)
        self.retry_button = tk.Button(button_frame, text="Retry", 
                                     command=self.on_retry, state=tk.DISABLED,
                                     bg='#4a4a4a', fg='#ffffff', font=('Arial', 10))
        self.retry_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        self.cancel_button = tk.Button(button_frame, text="Cancel", 
                                      command=self.on_cancel,
                                      bg='#4a4a4a', fg='#ffffff', font=('Arial', 10))
        self.cancel_button.pack(side=tk.LEFT)
        
        # Copyright
        copyright_label = tk.Label(main_frame, text="© DeathAIAUS 2025", 
                                  font=('Arial', 9), fg='#a0a0a0', bg='#2b2b2b')
        copyright_label.pack(side=tk.BOTTOM)
        
    def update_status(self, message, progress=None):
        """Update status message and progress bar"""
        # Ensure GUI updates happen on main thread
        def update():
            self.status_label.config(text=message)
            if progress is not None:
                self.progress['value'] = progress
                self.progress_value = progress
            self.root.update_idletasks()
        
        # Schedule update on main thread
        self.root.after(0, update)
        
    def show_error(self, message, allow_retry=True):
        """Show error message and enable retry button"""
        def update():
            self.error_state = True
            self.status_label.config(text=message, fg='#ff4444')
            if allow_retry:
                self.retry_button.config(state=tk.NORMAL)
            self.root.update_idletasks()
        
        # Schedule update on main thread
        self.root.after(0, update)
        
    def show_success(self, message):
        """Show success message"""
        def update():
            self.status_label.config(text=message, fg='#00ff00')
            self.progress['value'] = 100
            self.root.update_idletasks()
        
        # Schedule update on main thread
        self.root.after(0, update)
        
    def on_retry(self):
        """Handle retry button click"""
        self.error_state = False
        self.retry_button.config(state=tk.DISABLED)
        self.status_label.config(fg='#ffffff')
        self.progress['value'] = 0
        self.progress_value = 0
        # Signal to restart launch sequence
        self.retry_requested = True
        # Schedule retry in main thread
        self.root.after(100, self.handle_retry)
        
    def on_cancel(self):
        """Handle cancel button click"""
        self.root.quit()
        
    def handle_retry(self):
        """Handle retry request from main thread"""
        if hasattr(self, 'retry_callback'):
            self.retry_callback()
        
    def close(self):
        """Close the splash screen"""
        def close_window():
            self.root.destroy()
        
        # Schedule close on main thread
        self.root.after(0, close_window)


class BackendManager:
    """Manages DeathAIAUS Python Backend startup"""
    
    def __init__(self, logger):
        self.logger = logger
        self.backend_path = Path("DeathAIAUS_Backend.py")
        self.backend_script = self.backend_path
        
    def check_backend_ready(self):
        """Check if DeathAIAUS Backend is ready"""
        exists = self.backend_script.exists()
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
                import psutil
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
                sys.executable, str(self.backend_script)
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
        """Check if required MinGW DLLs are present"""
        required_dlls = [
            'libwinpthread-1.dll',
            'libstdc++-6.dll',
            'libgcc_s_seh-1.dll'
        ]
        
        missing = []
        for dll in required_dlls:
            dll_path = self.reapgate_path / dll
            if not dll_path.exists():
                missing.append(dll)
        
        return missing
        
    def copy_mingw_dlls(self):
        """Copy required MinGW DLLs to ReapGate directory"""
        mingw_paths = [
            Path("C:/mingw64/mingw64/bin"),
            Path("C:/mingw64/bin"),
            Path("C:/msys64/mingw64/bin")
        ]
        
        required_dlls = [
            'libwinpthread-1.dll',
            'libstdc++-6.dll',
            'libgcc_s_seh-1.dll'
        ]
        
        # Find MinGW installation
        mingw_bin = None
        for path in mingw_paths:
            if path.exists():
                mingw_bin = path
                break
        
        if not mingw_bin:
            return False, "MinGW installation not found"
        
        # Copy DLLs
        for dll in required_dlls:
            src = mingw_bin / dll
            dst = self.reapgate_path / dll
            if src.exists():
                shutil.copy2(src, dst)
                self.logger.info(f"Copied {dll} to ReapGate directory")
            else:
                return False, f"Required DLL not found: {dll}"
        
        return True, None
        
    def build_reapgate(self, progress_callback):
        """Build ReapGate from source"""
        try:
            self.logger.info("Starting ReapGate build process")
            progress_callback("Checking Go installation...", 10)
            
            # Check Go installation
            result = subprocess.run(['go', 'version'], capture_output=True, text=True)
            if result.returncode != 0:
                return False, "Go compiler not found. Please install Go from https://go.dev/dl/"
            
            self.logger.info(f"Go version: {result.stdout.strip()}")
            progress_callback("Tidying dependencies...", 25)
            
            # Change to ReapGate directory
            original_dir = os.getcwd()
            os.chdir(self.reapgate_path)
            
            try:
                # Run go mod tidy
                result = subprocess.run(['go', 'mod', 'tidy'], capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.error(f"go mod tidy failed: {result.stderr}")
                    return False, f"Failed to tidy dependencies: {result.stderr}"
                
                progress_callback("Downloading dependencies...", 50)
                
                # Run go mod download
                result = subprocess.run(['go', 'mod', 'download'], capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.error(f"go mod download failed: {result.stderr}")
                    return False, f"Failed to download dependencies: {result.stderr}"
                
                progress_callback("Building ReapGate...", 75)
                
                # Build ReapGate
                result = subprocess.run(['go', 'build', '-o', 'reapgate.exe'], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.error(f"Build failed: {result.stderr}")
                    return False, f"Build failed: {result.stderr}"
                
                self.logger.info("ReapGate built successfully")
                progress_callback("Build complete!", 100)
                return True, None
                
            finally:
                os.chdir(original_dir)
                
        except Exception as e:
            self.logger.error(f"Build error: {e}")
            return False, f"Build error: {e}"
            
    def start_reapgate(self, progress_callback):
        """Start ReapGate process"""
        try:
            # Kill any existing ReapGate processes first
            try:
                import psutil
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if 'reapgate' in proc.info['name'].lower():
                            self.logger.info(f"Killing existing ReapGate process: {proc.info['pid']}")
                            proc.kill()
                    except:
                        pass
                time.sleep(1)  # Wait for processes to die
            except ImportError:
                # Fallback to taskkill if psutil not available
                try:
                    subprocess.run(['taskkill', '/f', '/im', 'reapgate.exe'], 
                                 capture_output=True, check=False)
                    time.sleep(1)
                except:
                    pass
            
            self.logger.info("Starting ReapGate process")
            progress_callback("Starting ReapGate backend...", 0)
            
            # Change to ReapGate directory
            original_dir = os.getcwd()
            os.chdir(self.reapgate_path)
            
            try:
                # Start ReapGate process
                process = subprocess.Popen(['./reapgate.exe'], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE,
                                         text=True)
                
                self.logger.info(f"ReapGate started with PID: {process.pid}")
                
                # Wait a moment and check if it crashed immediately
                time.sleep(0.5)
                if process.poll() is not None:
                    # Process exited immediately - likely DLL error
                    stderr = process.stderr.read()
                    raise Exception(f"ReapGate crashed immediately. Check for missing DLLs. Error: {stderr}")
                
                return process
                
            finally:
                os.chdir(original_dir)
                
        except Exception as e:
            self.logger.error(f"Failed to start ReapGate: {e}")
            raise
            
    def wait_for_reapgate_ready(self, timeout=30, progress_callback=None):
        """Wait for ReapGate to be ready"""
        self.logger.info("Waiting for ReapGate to be ready")
        
        for i in range(timeout):
            try:
                response = requests.get("http://localhost:7777/health", timeout=1)
                if response.status_code == 200:
                    self.logger.info("ReapGate is ready!")
                    if progress_callback:
                        progress_callback("ReapGate ready!", 100)
                    return True
            except:
                pass
            
            if progress_callback:
                progress_callback(f"Waiting for ReapGate... ({i+1}/{timeout}s)", 
                                int((i+1) / timeout * 100))
            
            time.sleep(1)
            
        self.logger.error("ReapGate timeout - not ready after 30 seconds")
        return False
        
    def stop_reapgate(self, process):
        """Stop ReapGate process"""
        if process and process.poll() is None:
            self.logger.info("Stopping ReapGate process")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


class Launcher:
    """Main launcher class"""
    
    def __init__(self):
        self.setup_logging()
        self.splash = LauncherSplash()
        self.reapgate_manager = ReapGateManager(self.logger)
        self.reapgate_process = None
        self.retry_count = 0
        self.max_retries = 3
        
        # Set up retry callback
        self.splash.retry_callback = self.handle_retry_request
        
    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"launcher_{timestamp}.log"
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Launcher started")
        
    def handle_retry_request(self):
        """Handle retry request from splash screen"""
        self.retry_count += 1
        
        if self.retry_count > self.max_retries:
            self.splash.show_error("Maximum retries exceeded. Please check logs.", 
                                 allow_retry=False)
        else:
            # Stop ReapGate if running
            if self.reapgate_process:
                self.reapgate_manager.stop_reapgate(self.reapgate_process)
                self.reapgate_process = None
            
            # Restart launch sequence
            launch_thread = threading.Thread(target=self.launch_sequence, daemon=True)
            launch_thread.start()
        
    def launch_sequence(self):
        """Main launch sequence"""
        try:
            self.logger.info("Starting launch sequence")
            
            # Step 1: Check if ReapGate is built
            if not self.reapgate_manager.check_reapgate_built():
                self.splash.update_status("Building ReapGate...", 0)
                success, error = self.reapgate_manager.build_reapgate(
                    self.splash.update_status)
                if not success:
                    self.splash.show_error(f"Build failed: {error}")
                    return
            else:
                self.splash.update_status("ReapGate already built", 20)
                
            # Step 1.5: Check for required DLLs
            missing_dlls = self.reapgate_manager.check_required_dlls()
            if missing_dlls:
                self.splash.update_status("Copying required DLLs...", 25)
                success, error = self.reapgate_manager.copy_mingw_dlls()
                if not success:
                    self.splash.show_error(f"Failed to copy DLLs: {error}")
                    return
                
            # Step 2: Start ReapGate
            self.splash.update_status("Starting ReapGate backend...", 30)
            self.reapgate_process = self.reapgate_manager.start_reapgate(
                self.splash.update_status)
            
            # Step 3: Wait for ReapGate to be ready
            if not self.reapgate_manager.wait_for_reapgate_ready(
                progress_callback=self.splash.update_status):
                self.splash.show_error("ReapGate didn't respond within 30 seconds. "
                                     "It may be loading a large model.")
                return
                
            # Step 4: Launch IDE
            self.splash.update_status("Launching DeathAIAUS IDE...", 90)
            self.launch_ide()
            
            # Success
            self.splash.show_success("IDE launched successfully!")
            time.sleep(2)  # Give user time to see success message
            self.splash.close()
            
        except Exception as e:
            self.logger.error(f"Launch sequence error: {e}")
            self.splash.show_error(f"Launch error: {e}")
            
    def launch_ide(self):
        """Launch the DeathAIAUS IDE"""
        try:
            # Start IDE process
            process = subprocess.Popen(['pythonw', 'deathaius_ide_fc.py'])
            self.logger.info(f"IDE started with PID: {process.pid}")
            
            # Wait a moment to ensure it started
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is not None:
                raise Exception("IDE process exited immediately")
                
        except Exception as e:
            self.logger.error(f"Failed to launch IDE: {e}")
            raise
            
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
            # Don't stop ReapGate - let it keep running for the IDE
            # The IDE will manage ReapGate lifecycle
            pass


def main():
    """Main entry point"""
    try:
        launcher = Launcher()
        launcher.run()
    except KeyboardInterrupt:
        print("\nLauncher interrupted by user")
    except Exception as e:
        print(f"Launcher error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
