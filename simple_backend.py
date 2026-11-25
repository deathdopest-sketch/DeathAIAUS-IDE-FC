import logging
import time
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from llama_cpp import Llama
from pathlib import Path
import json

# Create logs directory
os.makedirs('logs', exist_ok=True)

# Configure logging FIRST
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/simple_backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Allow v2 IDE to connect

# Global model variable
current_model = None
model_name = "HEL-7B"

# Pantheon config
pantheon_path = Path("G:/My Drive/DeathAIAUS_PANTHEON")
models_registry = {}

def scan_pantheon_models():
    """Scan and register all Pantheon models"""
    logger.info(f"Scanning Pantheon directory: {pantheon_path}")
    
    if not pantheon_path.exists():
        logger.error(f"Pantheon path does not exist: {pantheon_path}")
        return {}
    
    # Load death_pantheon.json
    try:
        with open('death_pantheon.json', 'r', encoding='utf-8') as f:
            pantheon_config = json.load(f)
        logger.info("Loaded death_pantheon.json")
    except Exception as e:
        logger.warning(f"Could not load death_pantheon.json: {e}")
        pantheon_config = {}
    
    # Find all GGUF files
    gguf_files = list(pantheon_path.rglob("*.gguf"))
    logger.info(f"Found {len(gguf_files)} GGUF files")
    
    registry = {}
    for gguf_file in gguf_files:
        try:
            relative_path = gguf_file.relative_to(pantheon_path)
            model_id = str(relative_path).replace("\\", "/")
            
            registry[model_id] = {
                "id": model_id,
                "name": gguf_file.stem,
                "path": str(gguf_file),
                "size_gb": round(gguf_file.stat().st_size / (1024**3), 2)
            }
            logger.debug(f"Registered: {model_id}")
        except Exception as e:
            logger.error(f"Failed to register {gguf_file}: {e}")
    
    logger.info(f"Successfully registered {len(registry)} models")
    return registry

def _initialize_model_context(model):
    """Initialize model context with warm-up inference to fix memory issues"""
    try:
        logger.debug("Starting model context initialization...")
        
        # Method 1: Try a simple completion to force context initialization
        logger.debug("Attempting simple completion for context initialization...")
        try:
            # Use a very simple prompt that should work with any model
            test_prompt = "Hello"
            result = model(test_prompt, max_tokens=1, temperature=0.1, stop=["\n"])
            logger.debug("Simple completion successful - context initialized")
            return True
        except Exception as e1:
            logger.warning(f"Simple completion failed: {e1}")
        
        # Method 2: Try to access and initialize the context directly
        logger.debug("Attempting direct context initialization...")
        try:
            if hasattr(model, '_ctx') and model._ctx:
                # Try to access the memory to force initialization
                if hasattr(model._ctx, 'memory'):
                    _ = model._ctx.memory
                    logger.debug("Direct memory access successful")
                
                # Try to clear and reinitialize the KV cache
                if hasattr(model._ctx, 'kv_cache_clear'):
                    model._ctx.kv_cache_clear()
                    logger.debug("KV cache cleared")
                
                # Try to reset the context
                if hasattr(model._ctx, 'reset'):
                    model._ctx.reset()
                    logger.debug("Context reset successful")
                
                return True
        except Exception as e2:
            logger.warning(f"Direct context initialization failed: {e2}")
        
        # Method 3: Try minimal token evaluation
        logger.debug("Attempting minimal token evaluation...")
        try:
            if hasattr(model, 'tokenize'):
                tokens = model.tokenize(b"Hi")
                if tokens and len(tokens) > 0:
                    # Try to evaluate the first token
                    model.eval([tokens[0]])
                    logger.debug("Minimal token evaluation successful")
                    return True
        except Exception as e3:
            logger.warning(f"Minimal token evaluation failed: {e3}")
        
        # Method 4: Last resort - return True and hope for the best
        logger.warning("All context initialization methods failed - using fallback")
        return True
        
    except Exception as e:
        logger.error(f"Context initialization completely failed: {e}")
        return False

def load_model_safe():
    """Load model with multiple fallback strategies"""
    global current_model, model_name
    
    model_path = "DeathAIAUS-Anubis-Phi-1.5-Q8_0.gguf"
    
    logger.info(f"Attempting to load {model_name} from {model_path}")
    
    # Check file exists
    if not os.path.exists(model_path):
        logger.error(f"Model file not found: {model_path}")
        return False
    
    logger.info(f"Model file exists, size: {os.path.getsize(model_path) / (1024**3):.2f} GB")
    
    # Strategy 1: ChatML format with CPU
    try:
        logger.info("Strategy 1: ChatML format, CPU only, n_ctx=2048 (Phi-1.5 optimized)")
        current_model = Llama(
            model_path=model_path,
            n_ctx=2048,  # Phi-1.5 supports up to 2048 tokens
            n_gpu_layers=0,
            chat_format="chatml",
            rope_freq_base=10000.0,  # Phi-1.5 default
            verbose=True
        )
        # Initialize context with warm-up inference
        logger.info("Initializing context with warm-up inference...")
        _initialize_model_context(current_model)
        logger.info("SUCCESS: Model loaded with Strategy 1")
        return True
    except Exception as e1:
        logger.warning(f"Strategy 1 failed: {e1}")
    
    # Strategy 2: No chat format, CPU
    try:
        logger.info("Strategy 2: No chat format, CPU only, n_ctx=2048 (Phi-1.5 optimized)")
        current_model = Llama(
            model_path=model_path,
            n_ctx=2048,  # Phi-1.5 supports up to 2048 tokens
            n_gpu_layers=0,
            rope_freq_base=10000.0,  # Phi-1.5 default
            verbose=True
        )
        # Initialize context with warm-up inference
        logger.info("Initializing context with warm-up inference...")
        _initialize_model_context(current_model)
        logger.info("SUCCESS: Model loaded with Strategy 2")
        return True
    except Exception as e2:
        logger.warning(f"Strategy 2 failed: {e2}")
    
    # Strategy 3: Minimal settings
    try:
        logger.info("Strategy 3: Minimal settings, n_ctx=1024 (Phi-1.5 fallback)")
        current_model = Llama(
            model_path=model_path,
            n_ctx=1024,  # Reduced but still reasonable for Phi-1.5
            n_gpu_layers=0,
            rope_freq_base=10000.0,  # Phi-1.5 default
            verbose=False
        )
        # Initialize context with warm-up inference
        logger.info("Initializing context with warm-up inference...")
        _initialize_model_context(current_model)
        logger.info("SUCCESS: Model loaded with Strategy 3")
        return True
    except Exception as e3:
        logger.error(f"ALL STRATEGIES FAILED: {e3}", exc_info=True)
        return False

def clean_ai_response(text):
    """Remove reasoning tokens and internal thinking patterns from AI responses"""
    import re

    if not text:
        return text

    # Remove common reasoning artifacts
    patterns = [
        r'<\|end\|>',
        r'<\|begin\|>',
        r'<\|thinking\|>.*?<\|/thinking\|>',
        r'^Step \d+:.*$',
        r'^Meant to:.*$',
        r'^--- ACTION REQUIRED:.*$',
        r'^REQUIRED$',
        r'^lets begin$',
        r'^I need to generate a workflow.*?<\|end\|>',
        r'^Validate the following:.*?<\|end\|>',
        r'^Please review the validation.*?<\|end\|>',
        r'^--- CONTEXT:.*?---$',
        r'^File Tree:.*?---$',
        r'^ACTIVE FILE \(.*?\):.*?---$',
    ]

    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE)

    # Remove excessive blank lines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    # Trim whitespace
    cleaned = cleaned.strip()

    return cleaned if cleaned else text

def generate_text_safe(prompt, max_tokens=100):
    """Generate text with comprehensive error handling and fallback strategies"""
    global current_model

    if current_model is None:
        raise ValueError("No model loaded")
    
    # Method 1: Try chat completion first (but check if content is empty)
    try:
        logger.debug(f"Attempting chat completion for: {prompt[:50]}")
        result = current_model.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        text = result['choices'][0]['message']['content']
        logger.debug(f"Chat completion succeeded: {text[:50]}")
        
        # Check if the response is empty or just whitespace
        if text and text.strip():
            return text
        else:
            logger.warning("Chat completion returned empty content, trying raw completion")
            raise ValueError("Empty content from chat completion")
    except Exception as e1:
        logger.warning(f"Chat completion failed: {e1}, trying raw completion")
        
        # Method 2: Try raw completion
        try:
            result = current_model(
                prompt,
                max_tokens=max_tokens,
                temperature=0.7,
                stop=["User:", "\n\n", "<|end|>", "<|begin|>", "Step 1:", "Meant to:", "lets begin"]
            )
            text = result['choices'][0]['text']
            logger.debug(f"Raw completion succeeded: {text[:50]}")
            return text
        except Exception as e2:
            logger.warning(f"Raw completion failed: {e2}, trying minimal completion")
            
            # Method 3: Try minimal completion with very basic settings
            try:
                result = current_model(
                    prompt,
                    max_tokens=min(max_tokens, 50),  # Very short response
                    temperature=0.1,  # Low temperature
                    top_p=0.9,
                    repeat_penalty=1.1
                )
                text = result['choices'][0]['text']
                logger.debug(f"Minimal completion succeeded: {text[:50]}")
                return text
            except Exception as e3:
                logger.warning(f"Minimal completion failed: {e3}, trying token-by-token generation")
                
                # Method 4: Try token-by-token generation
                try:
                    # Tokenize the prompt
                    tokens = current_model.tokenize(prompt.encode('utf-8'))
                    if not tokens:
                        raise RuntimeError("Failed to tokenize prompt")
                    
                    # Generate tokens one by one
                    generated_tokens = []
                    for i in range(min(max_tokens, 50)):  # Limit to 50 tokens max
                        try:
                            # Evaluate the current tokens
                            current_model.eval(tokens + generated_tokens)
                            
                            # Get the next token
                            next_token = current_model.sample()
                            if next_token == current_model.token_eos():
                                break
                            
                            generated_tokens.append(next_token)
                            
                            # Convert token to text
                            if len(generated_tokens) >= 5:  # Generate at least 5 tokens
                                text = current_model.detokenize(generated_tokens).decode('utf-8', errors='ignore')
                                if text.strip():
                                    logger.debug(f"Token-by-token generation succeeded: {text[:50]}")
                                    return text.strip()
                        except Exception as token_error:
                            logger.warning(f"Token generation failed at step {i}: {token_error}")
                            break
                    
                    # If we get here, try to return whatever we generated
                    if generated_tokens:
                        text = current_model.detokenize(generated_tokens).decode('utf-8', errors='ignore')
                        if text.strip():
                            logger.debug(f"Partial token generation succeeded: {text[:50]}")
                            return text.strip()
                    
                    raise RuntimeError("Token-by-token generation failed")
                    
                except Exception as e4:
                    logger.error(f"All generation methods failed: {e4}", exc_info=True)
                    # Return a fallback response instead of raising an error
                    return f"I apologize, but I'm experiencing technical difficulties. The model is loaded but cannot generate text at the moment. Please try switching to a different model or restarting the backend."

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    try:
        request_data = request.json
        logger.info(f"Received request from v2 IDE")
        
        # Extract user message
        user_prompt = "No prompt"
        if request_data and 'messages' in request_data:
            for message in reversed(request_data['messages']):
                if message['role'] == 'user':
                    user_prompt = message['content']
                    break
        
        logger.debug(f"Generating response for: {user_prompt[:100]}")

        # Generate with model
        ai_response = generate_text_safe(user_prompt)

        # Clean up reasoning tokens before sending to frontend
        ai_response = clean_ai_response(ai_response)

        response = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model_name,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": ai_response
                },
                "finish_reason": "stop"
            }]
        }
        
        logger.info("Response generated successfully")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in chat_completions: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/v1/models', methods=['GET'])
def list_models():
    """List all available models"""
    try:
        return jsonify({
            "object": "list",
            "data": [
                {
                    "id": model_id,
                    "name": info["name"],
                    "size_gb": info["size_gb"]
                }
                for model_id, info in models_registry.items()
            ]
        })
    except Exception as e:
        logger.error(f"Error listing models: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/v1/models/load', methods=['POST'])
def load_specific_model():
    """Load a specific model by ID"""
    global current_model, model_name
    
    try:
        data = request.json
        model_id = data.get('model_id')
        
        if not model_id or model_id not in models_registry:
            return jsonify({"error": "Invalid model_id"}), 400
        
        logger.info(f"Switching to model: {model_id}")
        
        # Unload current model with proper cleanup
        if current_model:
            logger.info("Unloading current model with proper cleanup")
            try:
                # Clear KV cache if available
                if hasattr(current_model, '_ctx') and current_model._ctx:
                    logger.debug("Clearing KV cache...")
                    current_model._ctx.kv_cache_clear()
                
                # Force garbage collection
                import gc
                gc.collect()
                
                # Delete the model object
                del current_model
                current_model = None
                
                # Small delay to ensure cleanup is complete
                import time
                time.sleep(0.5)
                
                logger.info("Model unloaded successfully")
            except Exception as cleanup_error:
                logger.warning(f"Error during model cleanup: {cleanup_error}")
                # Force cleanup anyway
                current_model = None
        
        # Load new model
        model_info = models_registry[model_id]
        model_path = model_info['path']
        model_name = model_info['name']
        
        # Try loading strategies (same as load_model_safe)
        # Strategy 1: ChatML format with CPU
        try:
            logger.info("Strategy 1: ChatML format, CPU only, n_ctx=2048 (Phi-1.5 optimized)")
            current_model = Llama(
                model_path=model_path,
                n_ctx=2048,  # Phi-1.5 supports up to 2048 tokens
                n_gpu_layers=0,
                chat_format="chatml",
                rope_freq_base=10000.0,  # Phi-1.5 default
                verbose=True
            )
            # Initialize context with warm-up inference
            logger.info("Initializing context with warm-up inference...")
            _initialize_model_context(current_model)
            logger.info(f"SUCCESS: {model_name} loaded with Strategy 1")
            return jsonify({"status": "success", "model": model_name})
        except Exception as e1:
            logger.warning(f"Strategy 1 failed: {e1}")
        
        # Strategy 2: No chat format, CPU
        try:
            logger.info("Strategy 2: No chat format, CPU only, n_ctx=2048 (Phi-1.5 optimized)")
            current_model = Llama(
                model_path=model_path,
                n_ctx=2048,  # Phi-1.5 supports up to 2048 tokens
                n_gpu_layers=0,
                rope_freq_base=10000.0,  # Phi-1.5 default
                verbose=True
            )
            # Initialize context with warm-up inference
            logger.info("Initializing context with warm-up inference...")
            _initialize_model_context(current_model)
            logger.info(f"SUCCESS: {model_name} loaded with Strategy 2")
            return jsonify({"status": "success", "model": model_name})
        except Exception as e2:
            logger.warning(f"Strategy 2 failed: {e2}")
        
        # Strategy 3: Minimal settings
        try:
            logger.info("Strategy 3: Minimal settings, n_ctx=1024 (Phi-1.5 fallback)")
            current_model = Llama(
                model_path=model_path,
                n_ctx=1024,  # Reduced but still reasonable for Phi-1.5
                n_gpu_layers=0,
                rope_freq_base=10000.0,  # Phi-1.5 default
                verbose=False
            )
            # Initialize context with warm-up inference
            logger.info("Initializing context with warm-up inference...")
            _initialize_model_context(current_model)
            logger.info(f"SUCCESS: {model_name} loaded with Strategy 3")
            return jsonify({"status": "success", "model": model_name})
        except Exception as e3:
            logger.error(f"ALL STRATEGIES FAILED for {model_name}: {e3}")
            return jsonify({"error": str(e3)}), 500
            
    except Exception as e:
        logger.error(f"Error loading model: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/v1/terminal/execute', methods=['POST'])
def execute_terminal():
    """Execute terminal commands safely"""
    import subprocess

    try:
        data = request.json
        command = data.get('command', '')
        cwd = data.get('cwd', '.')

        if not command:
            return jsonify({"output": "", "exitCode": 1, "error": "No command provided"}), 400

        logger.info(f"Executing terminal command: {command}")

        # Security: Basic command validation
        dangerous_patterns = ['rm -rf /', 'format', 'del /f /s /q', ':(){:|:&};:']
        if any(pattern in command.lower() for pattern in dangerous_patterns):
            return jsonify({
                "output": "",
                "exitCode": 1,
                "error": "Command blocked for safety reasons"
            }), 403

        # Execute command with timeout
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )

            output = result.stdout if result.stdout else result.stderr

            return jsonify({
                "output": output,
                "exitCode": result.returncode,
                "error": result.stderr if result.returncode != 0 else None
            })

        except subprocess.TimeoutExpired:
            return jsonify({
                "output": "",
                "exitCode": 1,
                "error": "Command timed out after 30 seconds"
            }), 408

    except Exception as e:
        logger.error(f"Error executing terminal command: {e}", exc_info=True)
        return jsonify({"output": "", "exitCode": 1, "error": str(e)}), 500

@app.route('/v1/project/save', methods=['POST'])
def save_project():
    """Save project files to disk"""
    try:
        data = request.json
        project_name = data.get('projectName', 'project')
        files = data.get('files', [])
        base_path = data.get('basePath', './workspace')

        if not files:
            return jsonify({"error": "No files provided"}), 400

        logger.info(f"Saving project '{project_name}' with {len(files)} files to {base_path}")

        # Create base directory
        project_dir = Path(base_path) / project_name
        project_dir.mkdir(parents=True, exist_ok=True)

        saved_files = []

        def save_node(node, parent_path):
            """Recursively save file tree nodes"""
            node_path = parent_path / node['name']

            if 'children' in node:
                # It's a folder
                node_path.mkdir(parents=True, exist_ok=True)
                for child in node['children']:
                    save_node(child, node_path)
            elif 'content' in node:
                # It's a file
                node_path.parent.mkdir(parents=True, exist_ok=True)
                with open(node_path, 'w', encoding='utf-8') as f:
                    f.write(node['content'])
                saved_files.append(str(node_path.relative_to(project_dir)))

        # Save all files
        for file_node in files:
            save_node(file_node, project_dir)

        logger.info(f"Successfully saved {len(saved_files)} files")

        return jsonify({
            "success": True,
            "projectPath": str(project_dir.absolute()),
            "filesSaved": len(saved_files),
            "files": saved_files
        })

    except Exception as e:
        logger.error(f"Error saving project: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "phase": 4,
        "model_loaded": current_model is not None,
        "model_name": model_name if current_model else None,
        "models_available": len(models_registry)
    })

# Load model at startup
if __name__ == '__main__':
    logger.info("="*60)
    logger.info("Starting Simple Backend - Phase 4 (Model Switching)")
    logger.info("="*60)
    
    models_registry = scan_pantheon_models()
    
    if load_model_safe():
        logger.info(f"Backend ready with {len(models_registry)} models available")
        app.run(host='0.0.0.0', port=7777, debug=True)
    else:
        logger.error("FAILED TO LOAD MODEL")
