"""
DeathAIAUS IDE F.C - Hybrid Edition
Python/Tkinter shell + React UI via pywebview
Version 5.0 - Production Ready
"""

import os
import sys
import json
import subprocess
import threading
import time
import socket
import webbrowser
from pathlib import Path
from typing import Optional

import webview
import psutil
from flask import Flask, send_from_directory
from flask_cors import CORS

# Import our bridge
from webview_bridge import WebViewBridge, MemoryMonitor


class HybridIDE:
    """
    Main Hybrid IDE Application
    Combines React UI (v2) with Python backend (current version)
    """
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.flask_port = None
        self.backend_port = 8888
        self.flask_process = None
        self.backend_process = None
        self.webview_window = None
        self.bridge = None
        self.memory_monitor = MemoryMonitor()
        
    def check_prerequisites(self) -> bool:
        """Phase 0: Check all prerequisites"""
        print("=" * 60)
        print("DeathAIAUS IDE Hybrid - Starting Pre-Flight Checks")
        print("=" * 60)
        
        # Check Python version
        if sys.version_info < (3, 8):
            print("ERROR: Python 3.8+ required")
            return False
        print(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor}")
        
        # Check React build
        ui_dist = self.project_root / 'ui' / 'dist'
        if not ui_dist.exists():
            print("[WARN] React build not found. Building now...")
            if not self.build_react():
                return False
        print("[OK] React build found")
        
        # Check WebView2 (Windows)
        if sys.platform == 'win32':
            print("[INFO] WebView2 runtime will be checked by pywebview")
        
        # Check disk space
        usage = psutil.disk_usage(str(self.project_root))
        free_gb = usage.free / (1024 ** 3)
        if free_gb < 2:
            print(f"[WARN] Low disk space: {free_gb:.1f}GB free")
        else:
            print(f"[OK] Disk space: {free_gb:.1f}GB free")
        
        # Check RAM
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024 ** 3)
        if available_gb < 2:
            print(f"[WARN] Low memory: {available_gb:.1f}GB available")
        else:
            print(f"[OK] Memory: {available_gb:.1f}GB available")
        
        return True
    
    def build_react(self) -> bool:
        """Build React UI if needed"""
        try:
            ui_dir = self.project_root / 'ui'
            print("Building React UI...")
            result = subprocess.run(
                ['npm', 'run', 'build'],
                cwd=str(ui_dir),
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("[OK] React build successful")
                return True
            else:
                print(f"[ERROR] React build failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"[ERROR] Could not build React: {e}")
            return False
    
    def find_free_port(self, start_port: int = 5000) -> int:
        """Find available port"""
        port = start_port
        while port < start_port + 100:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('localhost', port))
                sock.close()
                return port
            except OSError:
                port += 1
        raise RuntimeError("No free ports found")
    
    def start_flask_server(self) -> bool:
        """Start Flask server for React UI"""
        try:
            self.flask_port = self.find_free_port(5000)
            print(f"Starting Flask server on port {self.flask_port}...")
            
            # Create Flask app
            app = Flask(__name__, static_folder='ui/dist')
            CORS(app)
            
            @app.route('/')
            def index():
                return send_from_directory('ui/dist', 'index.html')
            
            @app.route('/<path:path>')
            def static_files(path):
                return send_from_directory('ui/dist', path)
            
            # Start Flask in background thread
            def run_flask():
                app.run(port=self.flask_port, debug=False, use_reloader=False)
            
            flask_thread = threading.Thread(target=run_flask, daemon=True)
            flask_thread.start()
            
            # Wait for Flask to start
            time.sleep(2)
            
            print(f"[OK] Flask server running on http://localhost:{self.flask_port}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to start Flask: {e}")
            return False
    
    def start_backend(self) -> bool:
        """Start DeathAIAUS Python Backend"""
        try:
            # Check if backend is already running
            try:
                import requests
                response = requests.get(f'http://localhost:{self.backend_port}/health', timeout=2)
                if response.status_code == 200:
                    print(f"[OK] DeathAIAUS Backend already running on port {self.backend_port}")
                    return True
            except:
                pass
            
            # Start backend
            print(f"Starting DeathAIAUS Backend on port {self.backend_port}...")
            backend_script = self.project_root / 'start_deathaiaus_backend.py'
            
            if not backend_script.exists():
                print("[WARN] Backend script not found. AI features may not work.")
                return True  # Continue anyway
            
            self.backend_process = subprocess.Popen(
                [sys.executable, str(backend_script), '--port', str(self.backend_port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for backend to start
            print("Waiting for backend to initialize...")
            for i in range(30):  # 30 second timeout
                try:
                    import requests
                    response = requests.get(f'http://localhost:{self.backend_port}/health', timeout=1)
                    if response.status_code == 200:
                        print("[OK] DeathAIAUS Backend started successfully")
                        return True
                except:
                    pass
                time.sleep(1)
                if i % 5 == 0:
                    print(f"  Still waiting... ({i+1}s)")
            
            print("[WARN] Backend did not start in time. AI features may not work.")
            return True  # Continue anyway
            
        except Exception as e:
            print(f"[ERROR] Failed to start backend: {e}")
            return True  # Continue anyway
    
    def create_webview(self) -> bool:
        """Create pywebview window with React UI"""
        try:
            print("Creating webview window...")
            
            # Create bridge
            self.bridge = WebViewBridge(self)
            
            # Create window
            self.webview_window = webview.create_window(
                title='DeathAIAUS IDE F.C - Hybrid Edition',
                url=f'http://localhost:{self.flask_port}',
                width=1600,
                height=900,
                resizable=True,
                fullscreen=False,
                min_size=(1024, 768),
                js_api=self.bridge
            )
            
            print("[OK] Webview window created")
            print(f"[DEBUG] Flask URL: http://localhost:{self.flask_port}")
            print(f"[DEBUG] Webview window: {self.webview_window}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to create webview: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def start(self):
        """Main startup sequence"""
        try:
            # Phase 0: Pre-flight checks
            if not self.check_prerequisites():
                print("\nPre-flight checks failed. Exiting.")
                return False
            
            print("\n" + "=" * 60)
            print("Starting DeathAIAUS IDE Hybrid")
            print("=" * 60 + "\n")
            
            # Phase 1: Start Flask
            if not self.start_flask_server():
                print("\nFailed to start Flask server. Exiting.")
                return False
            
            # Phase 2: Start Backend
            if not self.start_backend():
                print("\n[WARN] Backend not started, but continuing...")
            
            # Phase 3: Start Memory Monitor
            self.memory_monitor.start()
            print("[OK] Memory monitor started")
            
            # Phase 4: Create Webview
            if not self.create_webview():
                print("\nFailed to create webview. Exiting.")
                return False
            
            print("\n" + "=" * 60)
            print("READY! Opening DeathAIAUS IDE...")
            print("=" * 60 + "\n")
            
            # Start webview (blocks until window closes)
            print("[DEBUG] Starting webview...")
            webview.start(debug=False)
            print("[DEBUG] Webview closed")
            
            print("\nIDE window closed. Shutting down...")
            return True
            
        except KeyboardInterrupt:
            print("\n\nShutdown requested by user.")
            return True
        except Exception as e:
            print(f"\n[FATAL ERROR] {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        print("\nCleaning up...")
        
        # Stop memory monitor
        if self.memory_monitor:
            self.memory_monitor.stop()
        
        # Stop backend
        if self.backend_process and self.backend_process.poll() is None:
            print("Stopping backend...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        print("Goodbye!")


def main():
    """Entry point"""
    # Set console encoding to handle Unicode
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    # Launcher handles splash screen

# """)
    
    ide = HybridIDE()
    success = ide.start()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

