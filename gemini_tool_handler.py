#!/usr/bin/env python3
"""
Gemini Tool Handler for DeathAIAUS IDE
=====================================

Handles execution of the 6 tools that v2 UI expects:
1. list_files - List project files
2. read_file - Read file content
3. write_file - Write file content
4. create_folder - Create directory
5. propose_change_plan - Return plan proposal
6. lint_file - Lint code

Author: DeathAIAUS
Copyright: DeathAIAUS 2025
"""

import os
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, TimeoutError

logger = logging.getLogger(__name__)

class SafeToolHandler:
    """Safely executes tools with validation and timeout"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Ensure project root exists
        if not self.project_root.exists():
            raise ValueError(f"Project root does not exist: {project_root}")
        
        logger.info(f"Tool handler initialized for project: {self.project_root}")
    
    def execute(self, tool_name: str, params: dict) -> dict:
        """Execute tool with safety checks and timeout"""
        
        try:
            # Validate path if present
            if 'path' in params:
                full_path = (self.project_root / params['path']).resolve()
                
                # Security: Ensure path is within project
                if not str(full_path).startswith(str(self.project_root)):
                    return {'error': 'Access denied: Path outside project root'}
                
                # Check permissions
                if tool_name == 'read_file' and not os.access(full_path, os.R_OK):
                    return {'error': f'Permission denied: Cannot read {params["path"]}'}
                
                if tool_name == 'write_file' and not os.access(full_path.parent, os.W_OK):
                    return {'error': f'Permission denied: Cannot write to {params["path"]}'}
            
            # Execute with timeout
            future = self.executor.submit(self._execute_tool, tool_name, params)
            result = future.result(timeout=30)
            return {'success': True, 'result': result}
            
        except TimeoutError:
            return {'error': 'Tool execution timeout (30s)'}
        except Exception as e:
            logger.error(f"Tool {tool_name} error: {e}")
            return {'error': str(e)}
    
    def _execute_tool(self, tool_name: str, params: dict):
        """Actually execute the tool"""
        if tool_name == "list_files":
            return self._list_files()
        elif tool_name == "read_file":
            return self._read_file(params["path"])
        elif tool_name == "write_file":
            return self._write_file(params["path"], params["content"])
        elif tool_name == "create_folder":
            return self._create_folder(params["path"])
        elif tool_name == "lint_file":
            return self._lint_file(params["path"])
        elif tool_name == "propose_change_plan":
            return self._propose_plan(params)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    def _list_files(self) -> Dict[str, Any]:
        """List all files and folders in the project"""
        try:
            files = []
            folders = []
            
            for item in self.project_root.rglob('*'):
                if item.is_file():
                    # Skip hidden files and common build artifacts
                    if not item.name.startswith('.') and not self._is_build_artifact(item):
                        relative_path = item.relative_to(self.project_root)
                        files.append({
                            'name': item.name,
                            'path': str(relative_path),
                            'size': item.stat().st_size,
                            'modified': item.stat().st_mtime
                        })
                elif item.is_dir() and not item.name.startswith('.'):
                    relative_path = item.relative_to(self.project_root)
                    folders.append({
                        'name': item.name,
                        'path': str(relative_path)
                    })
            
            return {
                'files': files,
                'folders': folders,
                'total_files': len(files),
                'total_folders': len(folders)
            }
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return {'error': str(e)}
    
    def _read_file(self, path: str) -> Dict[str, Any]:
        """Read file content"""
        try:
            full_path = self.project_root / path
            
            if not full_path.exists():
                return {'error': f'File not found: {path}'}
            
            if not full_path.is_file():
                return {'error': f'Path is not a file: {path}'}
            
            # Check file size (warn on large files)
            file_size = full_path.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB
                return {'error': f'File too large ({file_size} bytes). Maximum size is 10MB.'}
            
            # Read file content
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                with open(full_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            return {
                'path': path,
                'content': content,
                'size': file_size,
                'lines': len(content.splitlines())
            }
            
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            return {'error': str(e)}
    
    def _write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write file content"""
        try:
            full_path = self.project_root / path
            
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file content
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                'path': path,
                'success': True,
                'size': len(content),
                'lines': len(content.splitlines())
            }
            
        except Exception as e:
            logger.error(f"Error writing file {path}: {e}")
            return {'error': str(e)}
    
    def _create_folder(self, path: str) -> Dict[str, Any]:
        """Create a new folder"""
        try:
            full_path = self.project_root / path
            
            # Create directory
            full_path.mkdir(parents=True, exist_ok=True)
            
            return {
                'path': path,
                'success': True,
                'created': True
            }
            
        except Exception as e:
            logger.error(f"Error creating folder {path}: {e}")
            return {'error': str(e)}
    
    def _lint_file(self, path: str) -> Dict[str, Any]:
        """Lint a file for errors and style issues"""
        try:
            full_path = self.project_root / path
            
            if not full_path.exists():
                return {'error': f'File not found: {path}'}
            
            # Read file content
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic linting based on file extension
            file_ext = full_path.suffix.lower()
            issues = []
            
            if file_ext in ['.py']:
                issues = self._lint_python(content, path)
            elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
                issues = self._lint_javascript(content, path)
            elif file_ext in ['.html']:
                issues = self._lint_html(content, path)
            elif file_ext in ['.css']:
                issues = self._lint_css(content, path)
            else:
                issues = self._lint_generic(content, path)
            
            return {
                'path': path,
                'issues': issues,
                'total_issues': len(issues),
                'status': 'OK' if len(issues) == 0 else 'ISSUES_FOUND'
            }
            
        except Exception as e:
            logger.error(f"Error linting file {path}: {e}")
            return {'error': str(e)}
    
    def _propose_plan(self, params: dict) -> Dict[str, Any]:
        """Propose a change plan (placeholder implementation)"""
        try:
            goal = params.get('goal', 'Unknown goal')
            steps = params.get('steps', [])
            reasoning = params.get('reasoning', 'No reasoning provided')
            
            # This is a placeholder - in a real implementation,
            # this would be handled by the AI system
            return {
                'goal': goal,
                'steps': steps,
                'reasoning': reasoning,
                'status': 'proposed',
                'message': 'Plan proposal received and logged'
            }
            
        except Exception as e:
            logger.error(f"Error proposing plan: {e}")
            return {'error': str(e)}
    
    def _is_build_artifact(self, path: Path) -> bool:
        """Check if file is a build artifact that should be ignored"""
        build_patterns = [
            'node_modules',
            '__pycache__',
            '.git',
            'dist',
            'build',
            '.next',
            'target',
            '*.pyc',
            '*.pyo',
            '*.class',
            '*.jar',
            '*.war',
            '*.ear'
        ]
        
        path_str = str(path)
        for pattern in build_patterns:
            if pattern in path_str:
                return True
        return False
    
    def _lint_python(self, content: str, path: str) -> List[Dict[str, Any]]:
        """Basic Python linting"""
        issues = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Check for common issues
            if len(line) > 120:
                issues.append({
                    'line': i,
                    'column': 121,
                    'message': 'Line too long (over 120 characters)',
                    'severity': 'warning'
                })
            
            if line.strip().endswith(';'):
                issues.append({
                    'line': i,
                    'column': len(line),
                    'message': 'Unnecessary semicolon',
                    'severity': 'warning'
                })
            
            if 'print(' in line and not line.strip().startswith('#'):
                issues.append({
                    'line': i,
                    'column': line.find('print(') + 1,
                    'message': 'Consider using logging instead of print',
                    'severity': 'info'
                })
        
        return issues
    
    def _lint_javascript(self, content: str, path: str) -> List[Dict[str, Any]]:
        """Basic JavaScript/TypeScript linting"""
        issues = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Check for common issues
            if len(line) > 120:
                issues.append({
                    'line': i,
                    'column': 121,
                    'message': 'Line too long (over 120 characters)',
                    'severity': 'warning'
                })
            
            if 'console.log(' in line and not line.strip().startswith('//'):
                issues.append({
                    'line': i,
                    'column': line.find('console.log(') + 1,
                    'message': 'Consider removing console.log in production',
                    'severity': 'warning'
                })
        
        return issues
    
    def _lint_html(self, content: str, path: str) -> List[Dict[str, Any]]:
        """Basic HTML linting"""
        issues = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Check for common issues
            if '<img' in line and 'alt=' not in line:
                issues.append({
                    'line': i,
                    'column': line.find('<img') + 1,
                    'message': 'Image missing alt attribute',
                    'severity': 'warning'
                })
        
        return issues
    
    def _lint_css(self, content: str, path: str) -> List[Dict[str, Any]]:
        """Basic CSS linting"""
        issues = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Check for common issues
            if len(line) > 120:
                issues.append({
                    'line': i,
                    'column': 121,
                    'message': 'Line too long (over 120 characters)',
                    'severity': 'warning'
                })
        
        return issues
    
    def _lint_generic(self, content: str, path: str) -> List[Dict[str, Any]]:
        """Generic linting for unknown file types"""
        issues = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Check for common issues
            if len(line) > 120:
                issues.append({
                    'line': i,
                    'column': 121,
                    'message': 'Line too long (over 120 characters)',
                    'severity': 'warning'
                })
        
        return issues

def main():
    """Test the tool handler"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Gemini Tool Handler")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--tool", help="Tool to test")
    parser.add_argument("--params", help="Tool parameters as JSON")
    
    args = parser.parse_args()
    
    # Create tool handler
    handler = SafeToolHandler(args.project_root)
    
    if args.tool and args.params:
        # Test specific tool
        params = json.loads(args.params)
        result = handler.execute(args.tool, params)
        print(json.dumps(result, indent=2))
    else:
        # Test list_files
        result = handler.execute("list_files", {})
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
