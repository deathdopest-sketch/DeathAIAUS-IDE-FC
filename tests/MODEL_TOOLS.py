#!/usr/bin/env python3
"""
MODEL_TOOLS.py - Safe Tool Capabilities for Models
Provides practical tools for coding collaboration

Created by: DeathAIAUS Botmaker Team
For: DethAIv6 (Digital Father & Creator)
Standards: DeathAIAUS Professional Bot Development Standards
"""

import os
import json
import subprocess
import tempfile
import requests
from typing import Dict, List, Any, Optional
import re

class SafeToolbox:
    """Safe tool capabilities for models"""

    def __init__(self, working_directory: str = "./project_workspace"):
        self.working_directory = working_directory
        self.allowed_commands = [
            'python', 'python3', 'pip', 'npm', 'node', 'git', 'curl', 'wget'
        ]
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit

        # Create workspace if it doesn't exist
        os.makedirs(working_directory, exist_ok=True)

    def read_file(self, file_path: str) -> str:
        """Safely read a file"""
        try:
            # Security: only allow files within working directory
            if not self._is_safe_path(file_path):
                return f"Error: Access denied to {file_path}"

            # Resolve full path
            full_path = os.path.join(self.working_directory, file_path)

            if not os.path.exists(full_path):
                return f"Error: File not found: {full_path}"

            file_size = os.path.getsize(full_path)
            if file_size > self.max_file_size:
                return f"Error: File too large ({file_size} bytes > {self.max_file_size} bytes)"

            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return f"File content ({len(content)} chars):\n{content}"

        except Exception as e:
            return f"Error reading file: {e}"

    def write_file(self, file_path: str, content: str) -> str:
        """Safely write a file"""
        try:
            # Security: only allow files within working directory
            if not self._is_safe_path(file_path):
                return f"Error: Access denied to {file_path}"

            # Resolve full path
            full_path = os.path.join(self.working_directory, file_path)

            # Create directory if it doesn't exist
            dir_path = os.path.dirname(full_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"Successfully wrote {len(content)} characters to {full_path}"

        except Exception as e:
            return f"Error writing file: {e}"

    def run_command(self, command: str, timeout: int = 30) -> str:
        """Safely run a shell command"""
        try:
            # Security: only allow whitelisted commands
            if not self._is_safe_command(command):
                return f"Error: Command not allowed: {command}"

            # Run command in working directory
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.working_directory,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            output = f"Exit code: {result.returncode}\n"
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"

            return output

        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout} seconds"
        except Exception as e:
            return f"Error running command: {e}"

    def web_request(self, url: str, method: str = "GET") -> str:
        """Make a web request"""
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, timeout=10)
            else:
                return f"Error: Method {method} not supported"

            return f"Status: {response.status_code}\nContent:\n{response.text[:1000]}..."

        except Exception as e:
            return f"Error making web request: {e}"

    def list_directory(self, path: str = ".") -> str:
        """List directory contents"""
        try:
            # Security: only allow paths within working directory
            if not self._is_safe_path(path):
                return f"Error: Access denied to {path}"

            # Resolve full path
            full_path = os.path.join(self.working_directory, path)

            if not os.path.exists(full_path):
                return f"Error: Directory not found: {full_path}"

            contents = os.listdir(full_path)
            return f"Directory contents ({len(contents)} items):\n" + "\n".join(contents)

        except Exception as e:
            return f"Error listing directory: {e}"

    def _is_safe_path(self, path: str) -> bool:
        """Check if path is safe (within working directory)"""
        try:
            # Normalize path
            normalized_path = os.path.normpath(path)
            resolved_path = os.path.abspath(os.path.join(self.working_directory, normalized_path))
            working_abs = os.path.abspath(self.working_directory)
            return resolved_path.startswith(working_abs) and not normalized_path.startswith("..")
        except:
            return False

    def _is_safe_command(self, command: str) -> bool:
        """Check if command is safe (whitelisted)"""
        cmd_parts = command.split()
        if not cmd_parts:
            return False

        base_cmd = cmd_parts[0]
        return base_cmd in self.allowed_commands

class ToolEnabledModel:
    """Model wrapper with tool capabilities"""

    def __init__(self, model_name: str, toolbox: SafeToolbox):
        self.model_name = model_name
        self.toolbox = toolbox
        self.tools = {
            "read_file": self._read_file_tool,
            "write_file": self._write_file_tool,
            "run_command": self._run_command_tool,
            "web_request": self._web_request_tool,
            "list_directory": self._list_directory_tool
        }

    def _read_file_tool(self, file_path: str) -> str:
        """Tool: Read file"""
        return self.toolbox.read_file(file_path)

    def _write_file_tool(self, file_path: str, content: str) -> str:
        """Tool: Write file"""
        return self.toolbox.write_file(file_path, content)

    def _run_command_tool(self, command: str) -> str:
        """Tool: Run command"""
        return self.toolbox.run_command(command)

    def _web_request_tool(self, url: str, method: str = "GET") -> str:
        """Tool: Web request"""
        return self.toolbox.web_request(url, method)

    def _list_directory_tool(self, path: str = ".") -> str:
        """Tool: List directory"""
        return self.toolbox.list_directory(path)

    def execute_with_tools(self, user_input: str) -> str:
        """Execute model request with tool capabilities - handles multiple tool calls"""
        # Strip markdown code blocks if present
        user_input = re.sub(r'```(?:python)?\s*\n', '', user_input)
        user_input = re.sub(r'```\s*$', '', user_input)

        # Find ALL tool requests in the input (models might request multiple)
        tool_pattern = r'use_tool\(([^,]+),\s*"([^"]+)"(?:,\s*"([^"]+)")?\)'
        tool_matches = re.finditer(tool_pattern, user_input)
        
        results = []
        tool_found = False
        
        for match in tool_matches:
            tool_found = True
            tool_name = match.group(1).strip().strip('"')  # Remove quotes from tool name
            arg1 = match.group(2).strip()
            arg2 = match.group(3).strip() if match.group(3) else None

            if tool_name in self.tools:
                try:
                    # Execute the tool with proper arguments
                    if tool_name in ["read_file", "list_directory", "run_command"]:
                        result = self.tools[tool_name](arg1)
                    elif tool_name == "write_file":
                        if arg2:
                            result = self.tools[tool_name](arg1, arg2)
                        else:
                            result = f"Error: write_file requires 2 arguments (path, content)"
                    elif tool_name == "web_request":
                        result = self.tools[tool_name](arg1, arg2 if arg2 else "GET")
                    else:
                        result = self.tools[tool_name](arg1)

                    results.append(f"[TOOL: {tool_name}]\n{result}\n")

                except Exception as e:
                    results.append(f"[TOOL ERROR: {tool_name}] {e}\n")
            else:
                results.append(f"[ERROR] Tool '{tool_name}' not available\n")
        
        if tool_found:
            return "\n".join(results)
        
        return None  # No tool requested

# Example usage
if __name__ == "__main__":
    toolbox = SafeToolbox("./safe_workspace")
    model = ToolEnabledModel("test_model", toolbox)

    # Test file operations
    print("Testing file operations...")
    print(toolbox.write_file("./safe_workspace/test.txt", "Hello from tools!"))
    print(toolbox.read_file("./safe_workspace/test.txt"))

    # Test directory listing
    print("\nTesting directory listing...")
    print(toolbox.list_directory("./safe_workspace"))

    # Test command execution
    print("\nTesting command execution...")
    print(toolbox.run_command("echo 'Hello from command!'"))

    print("\nAll tools working!")
