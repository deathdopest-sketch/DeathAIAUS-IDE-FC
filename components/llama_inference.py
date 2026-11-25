"""
Llama.cpp Inference Engine
Lightweight inference engine using llama.cpp backend
"""
import os
import subprocess
import threading
import queue
import json
import platform


class LlamaCppEngine:
    """Inference engine using llama.cpp"""

    def __init__(self, model_path, config=None):
        self.model_path = model_path
        self.config = config or {}
        self.process = None
        self.output_queue = queue.Queue()
        self.is_loaded = False

        # llama.cpp executable path
        self.llama_cpp_path = self._find_llama_cpp()

    def _find_llama_cpp(self):
        """Find llama.cpp executable"""
        # Check bundled version first
        bundled_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'bin',
            'llama-server.exe' if platform.system() == 'Windows' else 'llama-server'
        )

        if os.path.exists(bundled_path):
            return bundled_path

        # Check system PATH
        import shutil
        system_path = shutil.which('llama-server')
        if system_path:
            return system_path

        return None

    def load_model(self):
        """Load model into memory"""
        if not self.llama_cpp_path:
            return False, "llama.cpp not found. Please install or provide executable."

        if not os.path.exists(self.model_path):
            return False, "Model file not found"

        self.is_loaded = True
        return True, "Model loaded (using Python fallback)"

    def generate(self, prompt, max_tokens=512, temperature=0.7, stop_tokens=None):
        """Generate text from prompt"""
        if not self.is_loaded:
            return "Error: Model not loaded"

        # Use llama-cpp-python if available
        try:
            from llama_cpp import Llama

            # Load with llama-cpp-python
            llm = Llama(
                model_path=self.model_path,
                n_ctx=self.config.get('context_length', 4096),
                n_threads=self.config.get('threads', 4),
                n_gpu_layers=self.config.get('gpu_layers', 0)
            )

            # Generate
            output = llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop_tokens or [],
                echo=False
            )

            return output['choices'][0]['text']

        except ImportError:
            # Fallback: use subprocess to call llama.cpp
            return self._generate_subprocess(prompt, max_tokens, temperature)

    def _generate_subprocess(self, prompt, max_tokens, temperature):
        """Generate using llama.cpp subprocess"""
        if not self.llama_cpp_path:
            return "[llama.cpp not available - install llama-cpp-python or provide llama-server executable]"

        try:
            # Build command
            cmd = [
                self.llama_cpp_path,
                '-m', self.model_path,
                '-p', prompt,
                '-n', str(max_tokens),
                '--temp', str(temperature),
                '-t', str(self.config.get('threads', 4)),
                '--ctx-size', str(self.config.get('context_length', 4096))
            ]

            # Run
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            return result.stdout

        except Exception as e:
            return f"[Inference error: {e}]"

    def stream_generate(self, prompt, callback, max_tokens=512, temperature=0.7):
        """Generate with streaming output"""

        def stream_thread():
            try:
                from llama_cpp import Llama

                llm = Llama(
                    model_path=self.model_path,
                    n_ctx=self.config.get('context_length', 4096),
                    n_threads=self.config.get('threads', 4),
                    n_gpu_layers=self.config.get('gpu_layers', 0)
                )

                # Stream
                for output in llm(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=True
                ):
                    token = output['choices'][0]['text']
                    callback(token)

            except ImportError:
                # Fallback: generate all at once and simulate streaming
                result = self._generate_subprocess(prompt, max_tokens, temperature)

                # Simulate streaming
                import time
                for char in result:
                    callback(char)
                    time.sleep(0.01)

            except Exception as e:
                callback(f"\n[Error: {e}]")

        threading.Thread(target=stream_thread, daemon=True).start()

    def unload(self):
        """Unload model from memory"""
        if self.process:
            self.process.terminate()
            self.process = None

        self.is_loaded = False


class SimplePythonInference:
    """Simple Python-based inference (no external dependencies)"""

    def __init__(self, model_path):
        self.model_path = model_path
        self.is_loaded = False

    def load_model(self):
        """Placeholder load"""
        if not os.path.exists(self.model_path):
            return False, "Model file not found"

        self.is_loaded = True
        return True, "Using Python inference fallback"

    def generate(self, prompt, max_tokens=512, temperature=0.7):
        """Simple template-based generation (fallback)"""
        if not self.is_loaded:
            return "Error: Model not loaded"

        # This is a simple fallback for when llama.cpp is not available
        # It provides basic code completion templates

        templates = self._get_code_templates(prompt)

        if templates:
            return templates[0]

        return f"# Code generation for: {prompt[:50]}...\n# Install llama-cpp-python for full AI capabilities"

    def _get_code_templates(self, prompt):
        """Get code templates based on prompt"""
        prompt_lower = prompt.lower()

        templates = []

        # Function template
        if 'function' in prompt_lower or 'def ' in prompt_lower:
            templates.append("""def function_name(param1, param2):
    \"\"\"
    Function description

    Args:
        param1: Description
        param2: Description

    Returns:
        Description
    \"\"\"
    # Implementation here
    pass""")

        # Class template
        if 'class' in prompt_lower:
            templates.append("""class ClassName:
    \"\"\"Class description\"\"\"

    def __init__(self):
        \"\"\"Initialize the class\"\"\"
        pass

    def method_name(self):
        \"\"\"Method description\"\"\"
        pass""")

        # For loop
        if 'for' in prompt_lower or 'loop' in prompt_lower:
            templates.append("""for item in collection:
    # Process item
    pass""")

        # If statement
        if 'if' in prompt_lower or 'condition' in prompt_lower:
            templates.append("""if condition:
    # True case
    pass
else:
    # False case
    pass""")

        # Try-except
        if 'try' in prompt_lower or 'exception' in prompt_lower or 'error' in prompt_lower:
            templates.append("""try:
    # Code that might raise exception
    pass
except Exception as e:
    # Handle exception
    print(f"Error: {e}")""")

        # API request
        if 'api' in prompt_lower or 'request' in prompt_lower or 'http' in prompt_lower:
            templates.append("""import requests

response = requests.get('https://api.example.com/endpoint')
if response.status_code == 200:
    data = response.json()
    # Process data
else:
    print(f"Error: {response.status_code}")""")

        # File I/O
        if 'file' in prompt_lower or 'read' in prompt_lower or 'write' in prompt_lower:
            templates.append("""with open('filename.txt', 'r') as f:
    content = f.read()
    # Process content

with open('output.txt', 'w') as f:
    f.write('data')""")

        return templates

    def stream_generate(self, prompt, callback, max_tokens=512, temperature=0.7):
        """Stream generate (simulated)"""
        result = self.generate(prompt, max_tokens, temperature)

        # Simulate streaming
        import time
        for char in result:
            callback(char)
            time.sleep(0.01)


class InferenceEngineFactory:
    """Factory for creating appropriate inference engine"""

    @staticmethod
    def create_engine(model_path, config=None):
        """Create best available inference engine"""

        # Try llama-cpp-python first
        try:
            import llama_cpp
            return LlamaCppEngine(model_path, config)
        except ImportError:
            pass

        # Check for llama.cpp executable
        engine = LlamaCppEngine(model_path, config)
        if engine.llama_cpp_path:
            return engine

        # Fallback to simple Python inference
        return SimplePythonInference(model_path)
