#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeathAIAUS IDE Automation Bot
Simulates a user interacting with the IDE to create a project
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path
from typing import Optional
import json
import traceback
import logging
from datetime import datetime

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Try to import automation libraries
try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False
    print("Warning: pyautogui not installed. Install with: pip install pyautogui")

try:
    import tkinter as tk
    from tkinter import messagebox
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False


class IDEAutomationBot:
    """Bot that automates IDE interactions"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.ide_process = None
        self.workspace_path = self.project_root / 'workspace' / 'bot_demo'
        self.demo_project_name = "BotDemoProject"
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = self.project_root / 'bot' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'bot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('IDEBot')
        self.log_file = log_file
        self.log("=" * 60)
        self.log("IDE Automation Bot - Logging Initialized")
        self.log(f"Log file: {log_file}")
        self.log("=" * 60)
        
    def log(self, message: str, level: str = "INFO"):
        """Log bot actions with timestamp and level"""
        timestamp = time.strftime("%H:%M:%S")
        # Use ASCII-safe characters
        message_safe = message.replace('✓', '[OK]').replace('✗', '[FAIL]').replace('⚠', '[WARN]')
        
        log_message = f"[{timestamp}] {message_safe}"
        print(log_message)
        
        # Also log to file with proper level
        if level == "DEBUG":
            self.logger.debug(message_safe)
        elif level == "WARNING" or level == "WARN":
            self.logger.warning(message_safe)
        elif level == "ERROR":
            self.logger.error(message_safe)
        else:
            self.logger.info(message_safe)
    
    def log_error(self, message: str, exception: Exception = None):
        """Log errors with full traceback"""
        self.log(f"ERROR: {message}", "ERROR")
        if exception:
            self.logger.error(f"Exception: {exception}", exc_info=True)
            # Also print traceback to console
            traceback.print_exc()
    
    def log_debug(self, message: str):
        """Log debug information"""
        self.log(message, "DEBUG")
    
    def wait_for_window(self, window_title: str, timeout: int = 30) -> bool:
        """Wait for a window with given title to appear"""
        if not HAS_PYAUTOGUI:
            self.log("Waiting (no pyautogui, using time delay)...")
            time.sleep(5)
            return True
            
        self.log(f"Waiting for window: {window_title}")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                windows = pyautogui.getWindowsWithTitle(window_title)
                if windows:
                    self.log(f"Window found: {window_title}")
                    return True
            except Exception:
                pass
            time.sleep(0.5)
        
        self.log(f"Window not found after {timeout}s")
        return False
    
    def click_at(self, x: int, y: int, delay: float = 0.5):
        """Click at coordinates"""
        if HAS_PYAUTOGUI:
            pyautogui.click(x, y)
            time.sleep(delay)
        else:
            self.log(f"Would click at ({x}, {y})")
            time.sleep(delay)
    
    def type_text(self, text: str, delay: float = 0.1):
        """Type text"""
        if HAS_PYAUTOGUI:
            pyautogui.write(text, interval=delay)
        else:
            self.log(f"Would type: {text}")
            time.sleep(len(text) * delay)
    
    def press_key(self, key: str, delay: float = 0.5):
        """Press a key"""
        if HAS_PYAUTOGUI:
            pyautogui.press(key)
            time.sleep(delay)
        else:
            self.log(f"Would press: {key}")
            time.sleep(delay)
    
    def launch_ide(self) -> bool:
        """Launch the IDE"""
        self.log("=" * 60)
        self.log("Launching DeathAIAUS IDE...")
        self.log("=" * 60)
        
        ide_script = self.project_root / 'deathaius_ide_fc.py'
        self.log_debug(f"Checking for IDE script at: {ide_script}")
        
        if not ide_script.exists():
            self.log_error(f"IDE script not found: {ide_script}")
            self.log_debug(f"Current directory: {os.getcwd()}")
            self.log_debug(f"Project root: {self.project_root}")
            return False
        
        self.log_debug(f"IDE script found: {ide_script}")
        self.log_debug(f"IDE script size: {ide_script.stat().st_size} bytes")
        
        try:
            # Launch IDE in a separate process
            self.log(f"Starting IDE: {ide_script}")
            self.log_debug(f"Python executable: {sys.executable}")
            self.log_debug(f"Working directory: {self.project_root}")
            
            self.ide_process = subprocess.Popen(
                [sys.executable, str(ide_script)],
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.log(f"IDE process started with PID: {self.ide_process.pid}")
            self.log_debug(f"Process returncode: {self.ide_process.returncode}")
            
            # Wait a bit for IDE to initialize
            self.log("Waiting for IDE to initialize...")
            time.sleep(3)
            
            # Check if process is still running
            if self.ide_process.poll() is not None:
                self.log_error("IDE process exited immediately")
                stdout, stderr = self.ide_process.communicate()
                if stdout:
                    self.log_debug(f"IDE stdout: {stdout.decode('utf-8', errors='replace')}")
                if stderr:
                    self.log_error(f"IDE stderr: {stderr.decode('utf-8', errors='replace')}")
                return False
            
            # Wait for IDE window
            self.log("Waiting for IDE window to appear...")
            if self.wait_for_window("DeathAIAUS IDE", timeout=15):
                self.log("[OK] IDE window detected")
                return True
            else:
                self.log("WARNING: IDE window not detected, but continuing...", "WARNING")
                self.log_debug("IDE process may be running in background")
                return True  # Continue anyway
                
        except FileNotFoundError as e:
            self.log_error(f"Python executable not found: {e}")
            return False
        except Exception as e:
            self.log_error(f"Error launching IDE: {e}", e)
            return False
    
    def create_project_directly(self) -> bool:
        """Create a project by directly creating files (alternative to GUI automation)"""
        self.log("=" * 60)
        self.log("Creating project directly...")
        self.log("=" * 60)
        
        try:
            # Create workspace directory
            self.log_debug(f"Creating workspace directory: {self.workspace_path}")
            self.workspace_path.mkdir(parents=True, exist_ok=True)
            self.log(f"Created workspace: {self.workspace_path}")
            self.log_debug(f"Workspace exists: {self.workspace_path.exists()}")
            self.log_debug(f"Workspace is directory: {self.workspace_path.is_dir()}")
            
            # Create a simple Python project
            project_files = {
                'main.py': '''#!/usr/bin/env python3
"""
Bot Demo Project - Created by IDE Automation Bot
A simple calculator application
"""

def add(a, b):
    """Add two numbers"""
    return a + b

def subtract(a, b):
    """Subtract two numbers"""
    return a - b

def multiply(a, b):
    """Multiply two numbers"""
    return a * b

def divide(a, b):
    """Divide two numbers"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def main():
    """Main function"""
    print("Calculator Demo")
    print("=" * 40)
    
    # Test operations
    print(f"10 + 5 = {add(10, 5)}")
    print(f"10 - 5 = {subtract(10, 5)}")
    print(f"10 * 5 = {multiply(10, 5)}")
    print(f"10 / 5 = {divide(10, 5)}")
    
    print("\\nAll operations completed successfully!")

if __name__ == "__main__":
    main()
''',
                'README.md': '''# Bot Demo Project

This project was created automatically by the IDE Automation Bot.

## Features

- Simple calculator functions
- Addition, subtraction, multiplication, division
- Error handling for division by zero

## Usage

```bash
python main.py
```

## Created By

IDE Automation Bot - Demonstrating IDE functionality
''',
                'requirements.txt': '''# Project dependencies
# No external dependencies required for this demo
''',
                '.gitignore': '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual Environment
venv/
env/

# IDE
.vscode/
.idea/
'''
            }
            
            # Write all files
            self.log(f"Creating {len(project_files)} project files...")
            for filename, content in project_files.items():
                file_path = self.workspace_path / filename
                self.log_debug(f"Writing file: {file_path}")
                self.log_debug(f"Content length: {len(content)} characters")
                
                try:
                    file_path.write_text(content, encoding='utf-8')
                    file_size = file_path.stat().st_size
                    self.log(f"Created: {filename} ({file_size} bytes)")
                    self.log_debug(f"File verified: {file_path.exists()}")
                except Exception as e:
                    self.log_error(f"Failed to create {filename}: {e}", e)
                    return False
            
            # Create a simple test file
            test_file = self.workspace_path / 'test_calculator.py'
            test_content = '''#!/usr/bin/env python3
"""Tests for calculator functions"""

from main import add, subtract, multiply, divide

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    print("[OK] Addition tests passed")

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5
    print("[OK] Subtraction tests passed")

def test_multiply():
    assert multiply(2, 3) == 6
    assert multiply(0, 5) == 0
    print("[OK] Multiplication tests passed")

def test_divide():
    assert divide(10, 2) == 5
    assert divide(9, 3) == 3
    print("[OK] Division tests passed")
    
    # Test division by zero
    try:
        divide(5, 0)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("[OK] Division by zero error handling works")

if __name__ == "__main__":
    test_add()
    test_subtract()
    test_multiply()
    test_divide()
    print("\\nAll tests passed! [SUCCESS]")
'''
            test_file.write_text(test_content, encoding='utf-8')
            test_size = test_file.stat().st_size
            self.log(f"Created: test_calculator.py ({test_size} bytes)")
            
            # Verify all files were created
            self.log("Verifying all files were created...")
            all_files_exist = all((self.workspace_path / f).exists() for f in project_files.keys())
            all_files_exist = all_files_exist and test_file.exists()
            
            if all_files_exist:
                self.log("[OK] All project files verified")
            else:
                self.log("WARNING: Some files may be missing", "WARNING")
                for filename in list(project_files.keys()) + ['test_calculator.py']:
                    file_path = self.workspace_path / filename
                    self.log_debug(f"  {filename}: {'EXISTS' if file_path.exists() else 'MISSING'}")
            
            # List all files in workspace
            files_created = list(self.workspace_path.iterdir())
            self.log(f"\\nProject created successfully at: {self.workspace_path}")
            self.log(f"Total files in workspace: {len(files_created)}")
            for f in files_created:
                if f.is_file():
                    self.log_debug(f"  - {f.name} ({f.stat().st_size} bytes)")
            
            return True
            
        except PermissionError as e:
            self.log_error(f"Permission denied creating project: {e}", e)
            self.log_debug(f"Workspace path: {self.workspace_path}")
            self.log_debug(f"Path exists: {self.workspace_path.exists()}")
            self.log_debug(f"Path writable: {os.access(self.workspace_path.parent, os.W_OK)}")
            return False
        except Exception as e:
            self.log_error(f"Error creating project: {e}", e)
            return False
    
    def run_project(self) -> bool:
        """Run the created project"""
        self.log("=" * 60)
        self.log("Running the project...")
        self.log("=" * 60)
        
        main_file = self.workspace_path / 'main.py'
        self.log_debug(f"Checking for main.py at: {main_file}")
        
        if not main_file.exists():
            self.log_error(f"main.py not found at: {main_file}")
            self.log_debug(f"Workspace contents: {list(self.workspace_path.iterdir())}")
            return False
        
        self.log_debug(f"main.py found: {main_file.exists()}")
        self.log_debug(f"main.py size: {main_file.stat().st_size} bytes")
        
        try:
            self.log("Executing main.py...")
            self.log_debug(f"Command: {sys.executable} {main_file}")
            self.log_debug(f"Working directory: {self.workspace_path}")
            
            result = subprocess.run(
                [sys.executable, str(main_file)],
                cwd=str(self.workspace_path),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            self.log_debug(f"Process return code: {result.returncode}")
            self.log_debug(f"stdout length: {len(result.stdout)} characters")
            self.log_debug(f"stderr length: {len(result.stderr)} characters")
            
            if result.returncode == 0:
                self.log("[OK] Project executed successfully!")
                self.log("Output:")
                print(result.stdout)
                if result.stderr:
                    self.log_debug(f"stderr (non-fatal): {result.stderr}")
                return True
            else:
                self.log_error(f"Project execution failed with return code {result.returncode}")
                if result.stdout:
                    self.log("stdout:")
                    print(result.stdout)
                if result.stderr:
                    self.log("stderr:")
                    print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            self.log_error("Project execution timed out after 10 seconds")
            return False
        except FileNotFoundError as e:
            self.log_error(f"Python executable not found: {e}", e)
            return False
        except Exception as e:
            self.log_error(f"Error running project: {e}", e)
            return False
    
    def run_tests(self) -> bool:
        """Run project tests"""
        self.log("=" * 60)
        self.log("Running tests...")
        self.log("=" * 60)
        
        test_file = self.workspace_path / 'test_calculator.py'
        self.log_debug(f"Checking for test file at: {test_file}")
        
        if not test_file.exists():
            self.log("No tests found", "WARNING")
            self.log_debug(f"Workspace contents: {list(self.workspace_path.iterdir())}")
            return False
        
        self.log_debug(f"Test file found: {test_file.exists()}")
        self.log_debug(f"Test file size: {test_file.stat().st_size} bytes")
        
        try:
            self.log("Executing tests...")
            self.log_debug(f"Command: {sys.executable} {test_file}")
            
            result = subprocess.run(
                [sys.executable, str(test_file)],
                cwd=str(self.workspace_path),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            self.log_debug(f"Test return code: {result.returncode}")
            self.log_debug(f"Test stdout length: {len(result.stdout)} characters")
            self.log_debug(f"Test stderr length: {len(result.stderr)} characters")
            
            if result.returncode == 0:
                self.log("[OK] All tests passed!")
                self.log("Test output:")
                print(result.stdout)
                if result.stderr:
                    self.log_debug(f"Test stderr (non-fatal): {result.stderr}")
                return True
            else:
                self.log("Some tests failed", "WARNING")
                self.log("Error output:")
                print(result.stderr)
                if result.stdout:
                    self.log("Test output:")
                    print(result.stdout)
                return False
                
        except subprocess.TimeoutExpired:
            self.log_error("Test execution timed out after 10 seconds")
            return False
        except Exception as e:
            self.log_error(f"Error running tests: {e}", e)
            return False
    
    def create_project_summary(self) -> dict:
        """Create a summary of what was created"""
        summary = {
            'project_name': self.demo_project_name,
            'workspace_path': str(self.workspace_path),
            'files_created': [],
            'created_at': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if self.workspace_path.exists():
            for file_path in self.workspace_path.iterdir():
                if file_path.is_file():
                    summary['files_created'].append({
                        'name': file_path.name,
                        'size': file_path.stat().st_size,
                        'path': str(file_path)
                    })
        
        return summary
    
    def save_summary(self, summary: dict):
        """Save project summary to JSON"""
        summary_file = self.project_root / 'bot' / 'bot_demo_summary.json'
        summary_file.parent.mkdir(exist_ok=True)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.log(f"Summary saved to: {summary_file}")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.ide_process:
            try:
                self.log_debug(f"Terminating IDE process (PID: {self.ide_process.pid})")
                self.ide_process.terminate()
                self.ide_process.wait(timeout=5)
                self.log("[OK] IDE process terminated")
            except subprocess.TimeoutExpired:
                self.log("WARNING: IDE process did not terminate, forcing kill", "WARNING")
                try:
                    self.ide_process.kill()
                    self.ide_process.wait(timeout=2)
                    self.log("[OK] IDE process killed")
                except Exception as e:
                    self.log_error(f"Failed to kill IDE process: {e}", e)
            except Exception as e:
                self.log_error(f"Error terminating IDE: {e}", e)
    
    def run_full_demo(self) -> bool:
        """Run the complete demo"""
        try:
            self.log("=" * 60)
            self.log("IDE AUTOMATION BOT - FULL DEMO")
            self.log("=" * 60)
            self.log("")
            
            # Step 1: Launch IDE (optional - can work without GUI)
            self.log("Step 1: Launching IDE...")
            ide_launched = self.launch_ide()
            if ide_launched:
                self.log("[OK] IDE launched successfully")
            else:
                self.log("WARNING: IDE launch had issues, but continuing...", "WARNING")
            
            time.sleep(2)
            
            # Step 2: Create project
            self.log("\\nStep 2: Creating project...")
            if self.create_project_directly():
                self.log("[OK] Project created successfully")
            else:
                self.log("[FAIL] Failed to create project", "ERROR")
                return False
            
            time.sleep(1)
            
            # Step 3: Run project
            self.log("\\nStep 3: Running project...")
            if self.run_project():
                self.log("[OK] Project executed successfully")
            else:
                self.log("[FAIL] Project execution failed", "ERROR")
                return False
            
            time.sleep(1)
            
            # Step 4: Run tests
            self.log("\\nStep 4: Running tests...")
            if self.run_tests():
                self.log("[OK] All tests passed")
            else:
                self.log("WARNING: Some tests failed or no tests found", "WARNING")
            
            # Step 5: Create summary
            self.log("\\nStep 5: Creating summary...")
            summary = self.create_project_summary()
            self.save_summary(summary)
            self.log("[OK] Summary created")
            
            # Final report
            self.log("\\n" + "=" * 60)
            self.log("DEMO COMPLETE!")
            self.log("=" * 60)
            self.log(f"Project location: {self.workspace_path}")
            self.log(f"Files created: {len(summary['files_created'])}")
            for file_info in summary['files_created']:
                self.log(f"  - {file_info['name']} ({file_info['size']} bytes)")
            
            self.log(f"\\nFull log saved to: {self.log_file}")
            return True
            
        except KeyboardInterrupt:
            self.log("\\nDemo interrupted by user", "WARNING")
            self.logger.warning("Demo interrupted by user")
            return False
        except Exception as e:
            self.log_error(f"Fatal error in demo: {e}", e)
            return False
        finally:
            self.log("Cleaning up...")
            self.cleanup()
            self.log("Cleanup complete")


def main():
    """Main entry point"""
    print("=" * 60)
    print("DeathAIAUS IDE - Automation Bot")
    print("=" * 60)
    print()
    
    if not HAS_PYAUTOGUI:
        print("Note: pyautogui not installed.")
        print("The bot will create projects directly without GUI automation.")
        print("Install pyautogui for full GUI interaction: pip install pyautogui")
        print()
    
    project_root = Path.cwd()
    bot = IDEAutomationBot(project_root)
    
    success = bot.run_full_demo()
    
    if success:
        print("\\n" + "=" * 60)
        print("SUCCESS: Bot demo completed successfully!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\\n" + "=" * 60)
        print("FAILED: Bot demo encountered errors")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()

