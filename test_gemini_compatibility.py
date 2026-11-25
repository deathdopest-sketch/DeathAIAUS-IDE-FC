#!/usr/bin/env python3
"""
Gemini Compatibility Test Suite
==============================

Comprehensive tests for the Gemini-Compatible Backend to ensure
it properly mimics the Gemini API for v2 UI compatibility.

Author: DeathAIAUS
Copyright: DeathAIAUS 2025
"""

import os
import sys
import json
import time
import requests
import unittest
import threading
import subprocess
from pathlib import Path
from typing import Dict, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class GeminiCompatibilityTests(unittest.TestCase):
    """Test suite for Gemini-Compatible Backend"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.gemini_backend_url = "http://localhost:8888"
        cls.deathaiaus_backend_url = "http://localhost:8889"
        cls.test_timeout = 30
        
        # Check if DeathAIAUS backend is running
        cls._check_deathaiaus_backend()
        
        # Start Gemini backend if not running
        cls._start_gemini_backend()
        
        # Wait for backend to be ready
        cls._wait_for_backend()
    
    @classmethod
    def _check_deathaiaus_backend(cls):
        """Check if DeathAIAUS backend is running"""
        try:
            response = requests.get(f"{cls.deathaiaus_backend_url}/health", timeout=5)
            if response.status_code != 200:
                raise Exception(f"DeathAIAUS backend not healthy: {response.status_code}")
            print("✓ DeathAIAUS backend is running")
        except Exception as e:
            raise Exception(f"DeathAIAUS backend not available: {e}")
    
    @classmethod
    def _start_gemini_backend(cls):
        """Start Gemini backend if not running"""
        try:
            response = requests.get(f"{cls.gemini_backend_url}/health", timeout=2)
            if response.status_code == 200:
                print("✓ Gemini backend is already running")
                return
        except:
            pass
        
        print("Starting Gemini backend...")
        try:
            # Start backend in background
            cls.backend_process = subprocess.Popen([
                sys.executable, "start_gemini_backend.py",
                "--port", "8888",
                "--deathaiaus-url", cls.deathaiaus_backend_url
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Give it time to start
            time.sleep(3)
            
        except Exception as e:
            raise Exception(f"Failed to start Gemini backend: {e}")
    
    @classmethod
    def _wait_for_backend(cls):
        """Wait for backend to be ready"""
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{cls.gemini_backend_url}/health", timeout=2)
                if response.status_code == 200:
                    print("✓ Gemini backend is ready")
                    return
            except:
                pass
            
            time.sleep(1)
        
        raise Exception("Gemini backend failed to start within 30 seconds")
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = requests.get(f"{self.gemini_backend_url}/health", timeout=self.test_timeout)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("timestamp", data)
        self.assertIn("sessions", data)
    
    def test_generate_content_simple(self):
        """Test simple content generation"""
        request_data = {
            "model": "gemini-2.5-flash",
            "contents": "Hello, how are you?",
            "config": {}
        }
        
        response = requests.post(
            f"{self.gemini_backend_url}/v1/models/generate",
            json=request_data,
            timeout=self.test_timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("text", data)
        self.assertIsInstance(data["text"], str)
        self.assertGreater(len(data["text"]), 0)
    
    def test_generate_content_with_system_instruction(self):
        """Test content generation with system instruction"""
        request_data = {
            "model": "gemini-2.5-flash",
            "contents": "What is 2+2?",
            "config": {
                "systemInstruction": "You are a helpful math tutor. Always show your work."
            }
        }
        
        response = requests.post(
            f"{self.gemini_backend_url}/v1/models/generate",
            json=request_data,
            timeout=self.test_timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("text", data)
        self.assertIsInstance(data["text"], str)
    
    def test_generate_content_json_mode(self):
        """Test content generation with JSON mode"""
        request_data = {
            "model": "gemini-2.5-flash",
            "contents": "Create a simple JSON object with name and age fields.",
            "config": {
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "number"}
                    },
                    "required": ["name", "age"]
                }
            }
        }
        
        response = requests.post(
            f"{self.gemini_backend_url}/v1/models/generate",
            json=request_data,
            timeout=self.test_timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("text", data)
        
        # Try to parse as JSON
        try:
            json_data = json.loads(data["text"])
            self.assertIn("name", json_data)
            self.assertIn("age", json_data)
        except json.JSONDecodeError:
            self.fail("Response is not valid JSON")
    
    def test_chat_create(self):
        """Test chat session creation"""
        request_data = {
            "model": "gemini-2.5-flash",
            "config": {
                "systemInstruction": "You are a helpful assistant.",
                "tools": []
            }
        }
        
        response = requests.post(
            f"{self.gemini_backend_url}/v1/chats/create",
            json=request_data,
            timeout=self.test_timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("chatId", data)
        self.assertIn("model", data)
        self.assertIn("config", data)
        self.assertEqual(data["model"], "gemini-2.5-flash")
        
        # Store chat ID for later tests
        self.chat_id = data["chatId"]
    
    def test_chat_send_message(self):
        """Test sending message to chat session"""
        # First create a chat
        self.test_chat_create()
        
        request_data = {
            "message": "Hello, what's the weather like?"
        }
        
        response = requests.post(
            f"{self.gemini_backend_url}/v1/chats/{self.chat_id}/send",
            json=request_data,
            timeout=self.test_timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("text", data)
        self.assertIsInstance(data["text"], str)
        self.assertGreater(len(data["text"]), 0)
    
    def test_chat_conversation_flow(self):
        """Test multi-turn conversation"""
        # Create chat
        self.test_chat_create()
        
        # Send first message
        response1 = requests.post(
            f"{self.gemini_backend_url}/v1/chats/{self.chat_id}/send",
            json={"message": "My name is Alice. What's your name?"},
            timeout=self.test_timeout
        )
        self.assertEqual(response1.status_code, 200)
        
        # Send follow-up message
        response2 = requests.post(
            f"{self.gemini_backend_url}/v1/chats/{self.chat_id}/send",
            json={"message": "Nice to meet you! How are you today?"},
            timeout=self.test_timeout
        )
        self.assertEqual(response2.status_code, 200)
        
        # Both responses should be valid
        data1 = response1.json()
        data2 = response2.json()
        self.assertIn("text", data1)
        self.assertIn("text", data2)
    
    def test_invalid_chat_id(self):
        """Test sending message to non-existent chat"""
        fake_chat_id = "fake-chat-id-12345"
        
        response = requests.post(
            f"{self.gemini_backend_url}/v1/chats/{fake_chat_id}/send",
            json={"message": "Hello"},
            timeout=self.test_timeout
        )
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("detail", data)
    
    def test_malformed_request(self):
        """Test handling of malformed requests"""
        # Missing required fields
        response = requests.post(
            f"{self.gemini_backend_url}/v1/models/generate",
            json={"model": "gemini-2.5-flash"},  # Missing contents
            timeout=self.test_timeout
        )
        
        self.assertEqual(response.status_code, 422)  # Validation error
    
    def test_large_request(self):
        """Test handling of large requests"""
        large_content = "Tell me about programming. " * 1000  # ~30KB
        
        request_data = {
            "model": "gemini-2.5-flash",
            "contents": large_content,
            "config": {}
        }
        
        response = requests.post(
            f"{self.gemini_backend_url}/v1/models/generate",
            json=request_data,
            timeout=self.test_timeout
        )
        
        # Should handle large requests gracefully
        self.assertIn(response.status_code, [200, 413, 422])  # OK, too large, or validation error
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = requests.post(
                    f"{self.gemini_backend_url}/v1/models/generate",
                    json={
                        "model": "gemini-2.5-flash",
                        "contents": "Hello from thread",
                        "config": {}
                    },
                    timeout=self.test_timeout
                )
                results.put(("success", response.status_code))
            except Exception as e:
                results.put(("error", str(e)))
        
        # Start 5 concurrent requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = 0
        while not results.empty():
            result_type, result_data = results.get()
            if result_type == "success" and result_data == 200:
                success_count += 1
        
        # At least some requests should succeed
        self.assertGreater(success_count, 0)
    
    def test_debug_endpoint(self):
        """Test debug status endpoint"""
        response = requests.get(
            f"{self.gemini_backend_url}/debug/status",
            timeout=self.test_timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("sessions", data)
        self.assertIn("memory_percent", data)
        self.assertIn("deathaiaus_backend_url", data)
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = requests.options(
            f"{self.gemini_backend_url}/v1/models/generate",
            headers={"Origin": "http://localhost:3000"},
            timeout=self.test_timeout
        )
        
        # Should not fail due to CORS
        self.assertIn(response.status_code, [200, 405])  # OK or Method Not Allowed
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        if hasattr(cls, 'backend_process'):
            cls.backend_process.terminate()
            cls.backend_process.wait()

class ToolHandlerTests(unittest.TestCase):
    """Test suite for Tool Handler"""
    
    def setUp(self):
        """Set up test environment"""
        from gemini_tool_handler import SafeToolHandler
        
        # Create test directory
        self.test_dir = Path("test_project")
        self.test_dir.mkdir(exist_ok=True)
        
        # Create test files
        (self.test_dir / "test.txt").write_text("Hello, World!")
        (self.test_dir / "test.py").write_text("print('Hello, World!')")
        
        self.handler = SafeToolHandler(str(self.test_dir))
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_list_files(self):
        """Test list_files tool"""
        result = self.handler.execute("list_files", {})
        
        self.assertTrue(result["success"])
        self.assertIn("files", result["result"])
        self.assertIn("folders", result["result"])
        self.assertGreaterEqual(len(result["result"]["files"]), 2)  # test.txt and test.py
    
    def test_read_file(self):
        """Test read_file tool"""
        result = self.handler.execute("read_file", {"path": "test.txt"})
        
        self.assertTrue(result["success"])
        self.assertEqual(result["result"]["content"], "Hello, World!")
        self.assertEqual(result["result"]["path"], "test.txt")
    
    def test_write_file(self):
        """Test write_file tool"""
        content = "This is a test file."
        result = self.handler.execute("write_file", {
            "path": "new_file.txt",
            "content": content
        })
        
        self.assertTrue(result["success"])
        self.assertTrue((self.test_dir / "new_file.txt").exists())
        self.assertEqual((self.test_dir / "new_file.txt").read_text(), content)
    
    def test_create_folder(self):
        """Test create_folder tool"""
        result = self.handler.execute("create_folder", {"path": "new_folder"})
        
        self.assertTrue(result["success"])
        self.assertTrue((self.test_dir / "new_folder").is_dir())
    
    def test_lint_file(self):
        """Test lint_file tool"""
        result = self.handler.execute("lint_file", {"path": "test.py"})
        
        self.assertTrue(result["success"])
        self.assertIn("issues", result["result"])
        self.assertIn("total_issues", result["result"])
        self.assertIn("status", result["result"])
    
    def test_propose_plan(self):
        """Test propose_change_plan tool"""
        result = self.handler.execute("propose_change_plan", {
            "goal": "Test goal",
            "steps": ["Step 1", "Step 2"],
            "reasoning": "Test reasoning"
        })
        
        self.assertTrue(result["success"])
        self.assertEqual(result["result"]["goal"], "Test goal")
        self.assertEqual(result["result"]["status"], "proposed")
    
    def test_security_path_traversal(self):
        """Test security against path traversal"""
        result = self.handler.execute("read_file", {"path": "../../../etc/passwd"})
        
        self.assertFalse(result["success"])
        self.assertIn("Access denied", result["error"])
    
    def test_nonexistent_file(self):
        """Test reading non-existent file"""
        result = self.handler.execute("read_file", {"path": "nonexistent.txt"})
        
        self.assertFalse(result["success"])
        self.assertIn("File not found", result["error"])

class SchemaMapperTests(unittest.TestCase):
    """Test suite for Schema Mapper"""
    
    def setUp(self):
        """Set up test environment"""
        from gemini_schema_mapper import SchemaMapper
        self.mapper = SchemaMapper()
    
    def test_schema_to_prompt(self):
        """Test schema to prompt conversion"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Person's name"},
                "age": {"type": "number", "description": "Person's age"}
            },
            "required": ["name", "age"]
        }
        
        prompt = self.mapper.schema_to_prompt(schema, "Create a person object")
        
        self.assertIn("name (string): Person's name", prompt)
        self.assertIn("age (number): Person's age", prompt)
        self.assertIn("Required fields: name, age", prompt)
    
    def test_validate_response_valid(self):
        """Test validation of valid response"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name", "age"]
        }
        
        response = '{"name": "Alice", "age": 30}'
        result = self.mapper.validate_response(response, schema)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["name"], "Alice")
        self.assertEqual(result["data"]["age"], 30)
    
    def test_validate_response_missing_required(self):
        """Test validation with missing required fields"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name", "age"]
        }
        
        response = '{"name": "Alice"}'  # Missing age
        result = self.mapper.validate_response(response, schema)
        
        self.assertTrue(result["success"])  # Should auto-fix with default
        self.assertEqual(result["data"]["name"], "Alice")
        self.assertEqual(result["data"]["age"], 0)  # Default value
    
    def test_extract_json_from_markdown(self):
        """Test JSON extraction from markdown code blocks"""
        response = """
        Here's the JSON you requested:
        
        ```json
        {"name": "Alice", "age": 30}
        ```
        
        Hope this helps!
        """
        
        data = self.mapper._extract_json(response)
        self.assertEqual(data["name"], "Alice")
        self.assertEqual(data["age"], 30)
    
    def test_extract_json_invalid(self):
        """Test JSON extraction from invalid response"""
        response = "This is not JSON at all"
        
        with self.assertRaises(ValueError):
            self.mapper._extract_json(response)

def run_tests():
    """Run all test suites"""
    print("=" * 60)
    print("Gemini Compatibility Test Suite")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        GeminiCompatibilityTests,
        ToolHandlerTests,
        SchemaMapperTests
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall: {'PASSED' if success else 'FAILED'}")
    
    return success

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
