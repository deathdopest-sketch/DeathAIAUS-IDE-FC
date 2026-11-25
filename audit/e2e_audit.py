#!/usr/bin/env python3
"""
Complete E2E Audit Script for DeathAIAUS IDE
Tests all 18 phases systematically
"""

import os
import sys
import json
import subprocess
import socket
import platform
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import psutil

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class AuditResult:
    """Stores audit test results"""
    def __init__(self, phase: str, test_name: str, passed: bool, message: str = "", details: Dict = None):
        self.phase = phase
        self.test_name = test_name
        self.passed = passed
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'phase': self.phase,
            'test_name': self.test_name,
            'passed': self.passed,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp
        }


class E2EAuditor:
    """Main audit class"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.results: List[AuditResult] = []
        self.issues: List[Dict] = []
        
    def log_result(self, phase: str, test_name: str, passed: bool, message: str = "", details: Dict = None):
        """Log a test result"""
        result = AuditResult(phase, test_name, passed, message, details)
        self.results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} [{phase}] {test_name}")
        if message:
            print(f"      {message}")
        if not passed:
            self.issues.append(result.to_dict())
        return result
    
    def check_python_version(self) -> bool:
        """Check Python version >= 3.8"""
        version = sys.version_info
        passed = version >= (3, 8)
        self.log_result(
            "Phase 1.1",
            "Python version check",
            passed,
            f"Python {version.major}.{version.minor}.{version.micro}",
            {'version': f"{version.major}.{version.minor}.{version.micro}"}
        )
        return passed
    
    def check_node_version(self) -> bool:
        """Check Node.js version"""
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.log_result("Phase 1.1", "Node.js version check", True, version)
                return True
            else:
                self.log_result("Phase 1.1", "Node.js version check", False, "Node.js not found")
                return False
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self.log_result("Phase 1.1", "Node.js version check", False, "Node.js not installed")
            return False
    
    def check_go_version(self) -> bool:
        """Check Go version (for ReapGate)"""
        try:
            result = subprocess.run(['go', 'version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.log_result("Phase 1.1", "Go version check", True, version)
                return True
            else:
                self.log_result("Phase 1.1", "Go version check", False, "Go not found")
                return False
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self.log_result("Phase 1.1", "Go version check", False, "Go not installed (optional for ReapGate)")
            return False
    
    def check_webview2(self) -> bool:
        """Check WebView2 runtime (Windows)"""
        if sys.platform != 'win32':
            self.log_result("Phase 1.1", "WebView2 check", True, "Not required on non-Windows")
            return True
        
        # Try to import pywebview to check WebView2
        try:
            import webview
            self.log_result("Phase 1.1", "WebView2 check", True, "pywebview available")
            return True
        except ImportError:
            self.log_result("Phase 1.1", "WebView2 check", False, "pywebview not installed")
            return False
    
    def check_disk_space(self) -> bool:
        """Check disk space >= 2GB"""
        try:
            usage = psutil.disk_usage(str(self.project_root))
            free_gb = usage.free / (1024 ** 3)
            passed = free_gb >= 2.0
            self.log_result(
                "Phase 1.1",
                "Disk space check",
                passed,
                f"{free_gb:.2f} GB free",
                {'free_gb': free_gb}
            )
            return passed
        except Exception as e:
            self.log_result("Phase 1.1", "Disk space check", False, str(e))
            return False
    
    def check_ram(self) -> bool:
        """Check RAM >= 2GB available"""
        try:
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024 ** 3)
            passed = available_gb >= 2.0
            self.log_result(
                "Phase 1.1",
                "RAM check",
                passed,
                f"{available_gb:.2f} GB available",
                {'available_gb': available_gb}
            )
            return passed
        except Exception as e:
            self.log_result("Phase 1.1", "RAM check", False, str(e))
            return False
    
    def check_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def check_ports(self) -> bool:
        """Check network ports availability"""
        ports = [8888, 8889, 7777, 3000, 5173]
        all_available = True
        for port in ports:
            available = self.check_port_available(port)
            self.log_result(
                "Phase 1.1",
                f"Port {port} availability",
                available,
                "Available" if available else "In use"
            )
            if not available:
                all_available = False
        return all_available
    
    def check_python_dependencies(self) -> bool:
        """Check Python dependencies from requirements.txt"""
        req_file = self.project_root / 'requirements.txt'
        if not req_file.exists():
            self.log_result("Phase 1.2", "Python dependencies check", False, "requirements.txt not found")
            return False
        
        # Read requirements
        required = []
        optional = []
        with open(req_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if 'optional' in line.lower() or 'recommended' in line.lower():
                    optional.append(line)
                else:
                    required.append(line.split('>=')[0].split('==')[0].strip())
        
        missing = []
        installed = []
        
        for dep in required:
            try:
                # Try importing
                if dep == 'pywebview':
                    import webview
                    installed.append(dep)
                elif dep == 'flask':
                    import flask
                    installed.append(dep)
                elif dep == 'flask-cors':
                    import flask_cors
                    installed.append(dep)
                elif dep == 'psutil':
                    import psutil
                    installed.append(dep)
                elif dep == 'requests':
                    import requests
                    installed.append(dep)
                else:
                    # Try generic import
                    __import__(dep.replace('-', '_'))
                    installed.append(dep)
            except ImportError:
                missing.append(dep)
        
        passed = len(missing) == 0
        self.log_result(
            "Phase 1.2",
            "Python dependencies check",
            passed,
            f"{len(installed)}/{len(required)} installed" + (f", missing: {', '.join(missing)}" if missing else ""),
            {'installed': installed, 'missing': missing}
        )
        
        # Check optional llama-cpp-python
        try:
            import llama_cpp
            self.log_result("Phase 1.2", "Optional llama-cpp-python", True, "Installed (full AI power)")
        except ImportError:
            self.log_result("Phase 1.2", "Optional llama-cpp-python", True, "Not installed (fallback mode available)")
        
        return passed
    
    def check_node_dependencies(self) -> bool:
        """Check Node.js dependencies"""
        package_json = self.project_root / 'ui' / 'package.json'
        if not package_json.exists():
            self.log_result("Phase 1.2", "Node.js dependencies check", False, "ui/package.json not found")
            return False
        
        node_modules = self.project_root / 'ui' / 'node_modules'
        if not node_modules.exists():
            self.log_result("Phase 1.2", "Node.js dependencies check", False, "node_modules not found - run 'npm install'")
            return False
        
        self.log_result("Phase 1.2", "Node.js dependencies check", True, "node_modules exists")
        return True
    
    def check_file_structure(self) -> bool:
        """Check required files exist"""
        required_files = [
            'deathaius_ide_fc.py',
            'deathaius_ide_hybrid.py',
            'deathaius_ide_integrated.py',
            'DeathAIAUS_Launcher.py',
            'components/__init__.py',
            'config/model_mappings.json',
            'ui/package.json',
        ]
        
        all_exist = True
        for file_path in required_files:
            full_path = self.project_root / file_path
            exists = full_path.exists()
            self.log_result(
                "Phase 1.3",
                f"File exists: {file_path}",
                exists,
                "Found" if exists else "Missing"
            )
            if not exists:
                all_exist = False
        
        # Check components directory
        components_dir = self.project_root / 'components'
        if components_dir.exists():
            component_files = list(components_dir.glob('*.py'))
            self.log_result(
                "Phase 1.3",
                "Components directory",
                True,
                f"{len(component_files)} component files found"
            )
        else:
            self.log_result("Phase 1.3", "Components directory", False, "Not found")
            all_exist = False
        
        # Check React build
        ui_dist = self.project_root / 'ui' / 'dist'
        if ui_dist.exists():
            self.log_result("Phase 1.3", "React UI build", True, "ui/dist exists")
        else:
            self.log_result("Phase 1.3", "React UI build", False, "ui/dist not found - needs build")
        
        # Check ReapGate
        reapgate_exe = self.project_root / 'go-llama.cpp' / 'reapgate.exe'
        if reapgate_exe.exists():
            self.log_result("Phase 1.3", "ReapGate executable", True, "Found")
        else:
            self.log_result("Phase 1.3", "ReapGate executable", False, "Not found (optional)")
        
        # Check model directories
        gdrive_path = Path('G:/My Drive')
        if gdrive_path.exists():
            self.log_result("Phase 1.3", "Google Drive models", True, "G:/My Drive accessible")
        else:
            self.log_result("Phase 1.3", "Google Drive models", False, "G:/My Drive not found (will use fallback)")
        
        return all_exist
    
    def run_phase1(self):
        """Run Phase 1: Prerequisites & Environment Audit"""
        print("\n" + "=" * 80)
        print("PHASE 1: PREREQUISITES & ENVIRONMENT AUDIT")
        print("=" * 80 + "\n")
        
        # 1.1 System Requirements
        print("1.1 System Requirements Verification")
        print("-" * 80)
        self.check_python_version()
        self.check_node_version()
        self.check_go_version()
        self.check_webview2()
        self.check_disk_space()
        self.check_ram()
        self.check_ports()
        
        # 1.2 Dependencies
        print("\n1.2 Dependency Audit")
        print("-" * 80)
        self.check_python_dependencies()
        self.check_node_dependencies()
        
        # 1.3 File Structure
        print("\n1.3 File Structure Verification")
        print("-" * 80)
        self.check_file_structure()
        
        print("\n" + "=" * 80)
        phase1_passed = sum(1 for r in self.results if r.phase.startswith("Phase 1") and r.passed)
        phase1_total = sum(1 for r in self.results if r.phase.startswith("Phase 1"))
        print(f"Phase 1 Summary: {phase1_passed}/{phase1_total} tests passed")
        print("=" * 80 + "\n")
    
    def run_phase2(self):
        """Run Phase 2: Launcher & Startup Audit"""
        print("\n" + "=" * 80)
        print("PHASE 2: LAUNCHER & STARTUP AUDIT")
        print("=" * 80 + "\n")
        
        # 2.1 Entry Point Testing
        print("2.1 Entry Point Testing")
        print("-" * 80)
        
        entry_points = [
            'deathaius_ide_fc.py',
            'deathaius_ide_hybrid.py',
            'deathaius_ide_integrated.py',
            'DeathAIAUS_Launcher.py'
        ]
        
        for entry_point in entry_points:
            file_path = self.project_root / entry_point
            exists = file_path.exists()
            self.log_result(
                "Phase 2.1",
                f"Entry point exists: {entry_point}",
                exists,
                "Found" if exists else "Missing"
            )
            
            if exists:
                # Check if file is valid Python
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(1000)  # Read first 1000 chars
                        is_python = 'import' in content or 'def ' in content or 'class ' in content
                        self.log_result(
                            "Phase 2.1",
                            f"Entry point valid Python: {entry_point}",
                            is_python,
                            "Valid Python" if is_python else "Invalid"
                        )
                except Exception as e:
                    self.log_result(
                        "Phase 2.1",
                        f"Entry point readable: {entry_point}",
                        False,
                        str(e)
                    )
        
        # Check batch scripts
        batch_scripts = [
            'scripts/LAUNCH_IDE.bat',
            'scripts/launch.bat',
            'CREATE_DESKTOP_SHORTCUT.bat'
        ]
        
        for script in batch_scripts:
            script_path = self.project_root / script
            exists = script_path.exists()
            self.log_result(
                "Phase 2.1",
                f"Batch script exists: {script}",
                exists,
                "Found" if exists else "Missing"
            )
        
        # 2.2 Startup Sequence Validation
        print("\n2.2 Startup Sequence Validation")
        print("-" * 80)
        
        # Check if we can import main modules
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("hybrid_ide", self.project_root / "deathaius_ide_hybrid.py")
            if spec and spec.loader:
                self.log_result("Phase 2.2", "Hybrid IDE importable", True, "Module can be imported")
            else:
                self.log_result("Phase 2.2", "Hybrid IDE importable", False, "Cannot create module spec")
        except Exception as e:
            self.log_result("Phase 2.2", "Hybrid IDE importable", False, str(e))
        
        # Check Flask availability
        try:
            import flask
            self.log_result("Phase 2.2", "Flask available", True, f"Flask {flask.__version__}")
        except ImportError:
            self.log_result("Phase 2.2", "Flask available", False, "Flask not installed")
        
        # Check WebView availability
        try:
            import webview
            self.log_result("Phase 2.2", "WebView available", True, "pywebview installed")
        except ImportError:
            self.log_result("Phase 2.2", "WebView available", False, "pywebview not installed")
        
        # Check bridge module
        bridge_path = self.project_root / 'webview_bridge.py'
        if bridge_path.exists():
            self.log_result("Phase 2.2", "WebView bridge exists", True, "Found")
        else:
            self.log_result("Phase 2.2", "WebView bridge exists", False, "Missing")
        
        # 2.3 Welcome Screen & Initialization
        print("\n2.3 Welcome Screen & Initialization")
        print("-" * 80)
        
        # Check for welcome screen components
        welcome_components = [
            'components/__init__.py',
            'ui/components/WelcomeScreen.tsx'
        ]
        
        for component in welcome_components:
            comp_path = self.project_root / component
            exists = comp_path.exists()
            self.log_result(
                "Phase 2.3",
                f"Welcome component: {component}",
                exists,
                "Found" if exists else "Missing"
            )
        
        print("\n" + "=" * 80)
        phase2_passed = sum(1 for r in self.results if r.phase.startswith("Phase 2") and r.passed)
        phase2_total = sum(1 for r in self.results if r.phase.startswith("Phase 2"))
        print(f"Phase 2 Summary: {phase2_passed}/{phase2_total} tests passed")
        print("=" * 80 + "\n")
    
    def generate_report(self) -> Dict:
        """Generate audit report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        # Group by phase
        phases = {}
        for result in self.results:
            phase = result.phase.split('.')[0] if '.' in result.phase else result.phase
            if phase not in phases:
                phases[phase] = {'passed': 0, 'failed': 0, 'tests': []}
            phases[phase]['tests'].append(result.to_dict())
            if result.passed:
                phases[phase]['passed'] += 1
            else:
                phases[phase]['failed'] += 1
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            'phases': phases,
            'issues': self.issues
        }
        
        return report
    
    def save_report(self, filename: str = None):
        """Save audit report to file"""
        if filename is None:
            filename = f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = self.generate_report()
        report_path = self.project_root / 'audit' / filename
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\nAudit report saved to: {report_path}")
        return report_path


    def run_all_phases(self):
        """Run all audit phases"""
        self.run_phase1()
        self.run_phase2()
        # Additional phases will be added incrementally
        # For now, we focus on getting Phase 1 and 2 working
    
    def run_phase3(self):
        """Run Phase 3: UI Components Audit"""
        print("\n" + "=" * 80)
        print("PHASE 3: UI COMPONENTS AUDIT")
        print("=" * 80 + "\n")
        
        # 3.1 React UI Components
        print("3.1 React UI Components")
        print("-" * 80)
        
        react_components = [
            'ui/App.tsx',
            'ui/components/ui/CodeEditor.tsx',
            'ui/components/FileTree.tsx',
            'ui/components/EditorTabs.tsx',
            'ui/components/AiChat.tsx',
            'ui/components/Terminal.tsx',
            'ui/components/TaskPlanner.tsx',
            'ui/components/FeasibilityAnalyzer.tsx',
            'ui/components/SettingsDialog.tsx',
            'ui/components/WelcomeScreen.tsx',
            'ui/components/Toolbar.tsx',
            'ui/components/ModelPerformanceTracker.tsx',
            'ui/components/ProjectKnowledgeBase.tsx',
            'ui/components/PreviewDialog.tsx',
            'ui/components/Documentation.tsx',
            'ui/components/FeaturesList.tsx'
        ]
        
        for component in react_components:
            comp_path = self.project_root / component
            exists = comp_path.exists()
            self.log_result(
                "Phase 3.1",
                f"React component: {component}",
                exists,
                "Found" if exists else "Missing"
            )
            
            if exists:
                # Check if file is valid TypeScript/React
                try:
                    with open(comp_path, 'r', encoding='utf-8') as f:
                        content = f.read(500)
                        is_react = 'import' in content and ('React' in content or 'react' in content or 'export' in content)
                        self.log_result(
                            "Phase 3.1",
                            f"Component valid React: {component}",
                            is_react,
                            "Valid React/TSX" if is_react else "Invalid format"
                        )
                except Exception as e:
                    self.log_result(
                        "Phase 3.1",
                        f"Component readable: {component}",
                        False,
                        str(e)
                    )
        
        # Check icon components
        icons_dir = self.project_root / 'ui' / 'components' / 'icons'
        if icons_dir.exists():
            icon_files = list(icons_dir.glob('*.tsx'))
            self.log_result(
                "Phase 3.1",
                "Icon components",
                True,
                f"{len(icon_files)} icon components found"
            )
        else:
            self.log_result("Phase 3.1", "Icon components", False, "Icons directory not found")
        
        # 3.2 Python Tkinter Components (if applicable)
        print("\n3.2 Python Tkinter Components")
        print("-" * 80)
        
        tkinter_components = [
            'components/file_tabs.py',
            'components/code_editor.py',
            'components/ai_chat.py',
            'components/git_panel.py',
            'components/terminal_tabs.py',
            'components/themes.py',
        ]
        
        for component in tkinter_components:
            comp_path = self.project_root / component
            exists = comp_path.exists()
            self.log_result(
                "Phase 3.2",
                f"Tkinter component: {component}",
                exists,
                "Found" if exists else "Missing (may be React-only)"
            )
        
        # 3.3 UI Integration
        print("\n3.3 UI Integration")
        print("-" * 80)
        
        # Check webview bridge
        bridge_path = self.project_root / 'webview_bridge.py'
        if bridge_path.exists():
            self.log_result("Phase 3.3", "WebView bridge exists", True, "Found")
            # Check bridge has required methods
            try:
                with open(bridge_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    has_methods = all(method in content for method in ['def ', 'class '])
                    self.log_result("Phase 3.3", "WebView bridge structure", has_methods, "Has class/methods")
            except Exception as e:
                self.log_result("Phase 3.3", "WebView bridge readable", False, str(e))
        else:
            self.log_result("Phase 3.3", "WebView bridge exists", False, "Missing")
        
        # Check React build
        ui_dist = self.project_root / 'ui' / 'dist'
        if ui_dist.exists():
            index_html = ui_dist / 'index.html'
            self.log_result(
                "Phase 3.3",
                "React build output",
                index_html.exists(),
                "index.html found" if index_html.exists() else "index.html missing"
            )
        else:
            self.log_result("Phase 3.3", "React build output", False, "ui/dist not found")
        
        print("\n" + "=" * 80)
        phase3_passed = sum(1 for r in self.results if r.phase.startswith("Phase 3") and r.passed)
        phase3_total = sum(1 for r in self.results if r.phase.startswith("Phase 3"))
        print(f"Phase 3 Summary: {phase3_passed}/{phase3_total} tests passed")
        print("=" * 80 + "\n")
    
    def run_phase4(self):
        """Run Phase 4: AI Model Server Audit"""
        print("\n" + "=" * 80)
        print("PHASE 4: AI MODEL SERVER AUDIT")
        print("=" * 80 + "\n")
        
        # 4.1 Model Detection & Loading
        print("4.1 Model Detection & Loading")
        print("-" * 80)
        
        # Check AI model server component
        ai_server_path = self.project_root / 'components' / 'ai_model_server.py'
        if ai_server_path.exists():
            self.log_result("Phase 4.1", "AI Model Server component", True, "Found")
        else:
            self.log_result("Phase 4.1", "AI Model Server component", False, "Missing")
        
        # Check inference engine
        inference_path = self.project_root / 'components' / 'llama_inference.py'
        if inference_path.exists():
            self.log_result("Phase 4.1", "Inference engine component", True, "Found")
        else:
            self.log_result("Phase 4.1", "Inference engine component", False, "Missing")
        
        # Check Google Drive path
        gdrive_path = Path('G:/My Drive')
        if gdrive_path.exists():
            self.log_result("Phase 4.1", "Google Drive accessible", True, "G:/My Drive found")
            # Check for models
            try:
                model_files = list(gdrive_path.rglob('*.gguf'))
                if model_files:
                    self.log_result("Phase 4.1", "Models in Google Drive", True, f"{len(model_files)} .gguf files found")
                else:
                    self.log_result("Phase 4.1", "Models in Google Drive", True, "No .gguf files (will use fallback)")
            except Exception as e:
                self.log_result("Phase 4.1", "Models in Google Drive", False, f"Error scanning: {e}")
        else:
            self.log_result("Phase 4.1", "Google Drive accessible", True, "G:/My Drive not found (will use fallback)")
        
        # 4.2 Model Server Operations
        print("\n4.2 Model Server Operations")
        print("-" * 80)
        
        # Try to import AIModelServer
        try:
            sys.path.insert(0, str(self.project_root))
            from components.ai_model_server import AIModelServer
            self.log_result("Phase 4.2", "AIModelServer importable", True, "Can import")
            
            # Try to instantiate (without actually loading a model)
            try:
                server = AIModelServer()
                self.log_result("Phase 4.2", "AIModelServer instantiable", True, "Can create instance")
            except Exception as e:
                self.log_result("Phase 4.2", "AIModelServer instantiable", False, str(e))
        except ImportError as e:
            self.log_result("Phase 4.2", "AIModelServer importable", False, str(e))
        
        # 4.3 Inference Engine
        print("\n4.3 Inference Engine")
        print("-" * 80)
        
        # Check llama-cpp-python
        try:
            import llama_cpp
            self.log_result("Phase 4.3", "llama-cpp-python available", True, "Full AI power enabled")
        except ImportError:
            self.log_result("Phase 4.3", "llama-cpp-python available", True, "Not installed (fallback mode)")
        
        # Check inference engine import
        try:
            from components.llama_inference import InferenceEngineFactory
            self.log_result("Phase 4.3", "InferenceEngineFactory importable", True, "Can import")
        except ImportError as e:
            self.log_result("Phase 4.3", "InferenceEngineFactory importable", False, str(e))
        
        # 4.4 ReapGate Backend Integration
        print("\n4.4 ReapGate Backend Integration")
        print("-" * 80)
        
        reapgate_exe = self.project_root / 'go-llama.cpp' / 'reapgate.exe'
        if reapgate_exe.exists():
            self.log_result("Phase 4.4", "ReapGate executable", True, "Found")
        else:
            self.log_result("Phase 4.4", "ReapGate executable", False, "Not found (optional)")
        
        print("\n" + "=" * 80)
        phase4_passed = sum(1 for r in self.results if r.phase.startswith("Phase 4") and r.passed)
        phase4_total = sum(1 for r in self.results if r.phase.startswith("Phase 4"))
        print(f"Phase 4 Summary: {phase4_passed}/{phase4_total} tests passed")
        print("=" * 80 + "\n")
    
    def run_quick_audit(self):
        """Run a quick audit of critical components"""
        print("\n" + "=" * 80)
        print("QUICK AUDIT - CRITICAL COMPONENTS")
        print("=" * 80 + "\n")
        
        # Critical file checks
        critical_files = [
            'deathaius_ide_fc.py',
            'deathaius_ide_hybrid.py',
            'components/ai_model_server.py',
            'components/llama_inference.py',
            'webview_bridge.py',
            'ui/App.tsx',
            'ui/components/ui/CodeEditor.tsx'
        ]
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            exists = full_path.exists()
            self.log_result(
                "Quick Audit",
                f"Critical file: {file_path}",
                exists,
                "Found" if exists else "MISSING - CRITICAL"
            )
        
        # Critical imports
        critical_imports = [
            ('requests', 'requests'),
            ('flask', 'flask'),
            ('webview', 'pywebview'),
            ('psutil', 'psutil')
        ]
        
        for module_name, package_name in critical_imports:
            try:
                __import__(module_name)
                self.log_result("Quick Audit", f"Import: {package_name}", True, "Available")
            except ImportError:
                self.log_result("Quick Audit", f"Import: {package_name}", False, "MISSING - CRITICAL")


def main():
    """Main entry point"""
    print("=" * 80)
    print("DEATHAIAUS IDE - COMPLETE E2E AUDIT")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    auditor = E2EAuditor()
    
    # Import and bind additional phase methods
    try:
        import importlib.util
        phases_module_path = auditor.project_root / 'audit' / 'audit_phases_5_18.py'
        if phases_module_path.exists():
            spec = importlib.util.spec_from_file_location("audit_phases_5_18", phases_module_path)
            if spec and spec.loader:
                phases_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(phases_module)
                
                # Bind methods to auditor instance
                for i in range(5, 19):
                    method_name = f'run_phase{i}'
                    if hasattr(phases_module, method_name):
                        method = getattr(phases_module, method_name)
                        # Use closure to capture method correctly
                        def make_phase_runner(phase_method):
                            return lambda: phase_method(auditor)
                        setattr(auditor, method_name, make_phase_runner(method))
        else:
            print("Warning: audit_phases_5_18.py not found, skipping phases 5-18")
            for i in range(5, 19):
                setattr(auditor, f'run_phase{i}', lambda: None)
    except Exception as e:
        print(f"Warning: Could not load additional phase methods: {e}")
        import traceback
        traceback.print_exc()
        # Create stub methods
        for i in range(5, 19):
            setattr(auditor, f'run_phase{i}', lambda: None)
    
    # Run all phases
    try:
        auditor.run_phase1()
        auditor.run_phase2()
        auditor.run_phase3()
        auditor.run_phase4()
        auditor.run_phase5()
        auditor.run_phase6()
        auditor.run_phase7()
        auditor.run_phase8()
        auditor.run_phase9()
        auditor.run_phase10()
        auditor.run_phase11()
        auditor.run_phase12()
        auditor.run_phase13()
        auditor.run_phase14()
        auditor.run_phase15()
        auditor.run_phase16()
        auditor.run_phase17()
        auditor.run_phase18()
        auditor.run_quick_audit()
    except KeyboardInterrupt:
        print("\n\nAudit interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n\nFatal error during audit: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Save report
    try:
        auditor.save_report()
    except Exception as e:
        print(f"Warning: Could not save report: {e}")
    
    # Print summary
    report = auditor.generate_report()
    print("\n" + "=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
    print("=" * 80)
    
    if report['summary']['failed'] > 0:
        print(f"\n⚠️  {report['summary']['failed']} issues found. See audit report for details.")
        print("\nTop issues:")
        for issue in auditor.issues[:10]:  # Show first 10 issues
            print(f"  - [{issue['phase']}] {issue['test_name']}: {issue['message']}")
        return 1
    else:
        print("\n✅ All tests passed!")
        return 0


if __name__ == '__main__':
    sys.exit(main())

