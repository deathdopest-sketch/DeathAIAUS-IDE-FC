# Gemini-Compatible Backend - Error Prevention Guide

## Comprehensive Error Analysis & Solutions

This document details every potential error, its cause, prevention strategy, and testing approach.

---

## Error Category 1: CORS Issues

**Potential Errors:**
```
Access to fetch at 'http://localhost:8888' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Root Cause:** Browser security prevents cross-origin requests

**Prevention Strategy:**
```python
# In gemini_compatible_backend.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Testing:** Open browser console, verify no CORS errors

**Fix if Occurs:** Add specific origin to allow_origins list

---

## Error Category 2: Port Conflicts

**Potential Errors:**
```
OSError: [Errno 48] Address already in use
RuntimeError: Port 8888 is already in use
```

**Root Cause:** Another process using the port

**Prevention Strategy:**
```python
import socket

def find_free_port(start_port: int = 8888) -> int:
    for port in range(start_port, start_port + 100):
        try:
            sock = socket.socket()
            sock.bind(('localhost', port))
            sock.close()
            return port
        except OSError:
            continue
    raise RuntimeError("No free ports found")

# Use it
port = find_free_port(8888)
uvicorn.run(app, host="127.0.0.1", port=port)
```

**Testing:** Start multiple backend instances

**Fix if Occurs:** Kill process on port or use alternative port

---

## Error Category 3: JSON Parsing Failures

**Potential Errors:**
```
JSONDecodeError: Expecting value: line 1 column 1 (char 0)
json.decoder.JSONDecodeError: Extra data
```

**Root Cause:** AI returns text with JSON embedded or malformed JSON

**Prevention Strategy:**
```python
import re
import json

def extract_json_from_response(text: str) -> dict:
    """Extract JSON from AI response with multiple fallback strategies"""
    
    # Strategy 1: Try direct JSON parse
    try:
        return json.loads(text)
    except:
        pass
    
    # Strategy 2: Extract from markdown code blocks
    json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except:
            pass
    
    # Strategy 3: Find first JSON object
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except:
            pass
    
    # Strategy 4: Find JSON array
    json_match = re.search(r'\[.*\]', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except:
            pass
    
    raise ValueError(f"Could not parse JSON from: {text[:200]}...")
```

**Testing:** Test with various AI responses:
- Valid JSON
- JSON in markdown blocks
- JSON with extra text
- Malformed JSON

**Fix if Occurs:** Add more parsing strategies or retry with better prompt

---

## Error Category 4: Model Loading Failures

**Potential Errors:**
```
RuntimeError: Failed to load model: File not found
llama_cpp.LlamaError: Model loading error
MemoryError: Cannot allocate memory
```

**Root Cause:** Model file missing, corrupted, or too large for available RAM

**Prevention Strategy:**
```python
import time
from pathlib import Path

def load_model_with_retry(model_path: str, max_retries: int = 3):
    """Load model with exponential backoff retry"""
    
    # Validate path first
    if not Path(model_path).exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Loading model attempt {attempt + 1}/{max_retries}")
            model = Llama(
                model_path=model_path,
                n_ctx=4096,
                n_gpu_layers=-1,  # Use all GPU
                n_threads=8,
                verbose=False
            )
            logger.info("Model loaded successfully")
            return model
            
        except MemoryError:
            logger.error("Out of memory - cannot retry")
            raise
            
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed after {max_retries} attempts: {e}")
                raise
            
            wait_time = 2 ** attempt
            logger.warning(f"Load failed, retrying in {wait_time}s: {e}")
            time.sleep(wait_time)
```

**Testing:**
- Test with invalid path
- Test with corrupted GGUF file
- Test with model larger than RAM

**Fix if Occurs:**
- Verify model file integrity
- Reduce n_ctx or n_gpu_layers
- Free memory by unloading other models

---

## Error Category 5: Tool Execution Errors

**Potential Errors:**
```
PermissionError: [Errno 13] Permission denied
FileNotFoundError: [Errno 2] No such file or directory
OSError: [Errno 28] No space left on device
```

**Root Cause:** File system permissions, missing files, or disk space issues

**Prevention Strategy:**
```python
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import os

class SafeToolHandler:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.executor = ThreadPoolExecutor(max_workers=4)
    
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
```

**Testing:**
- Test with read-only directories
- Test with invalid paths
- Test with very large files
- Test concurrent tool executions

**Fix if Occurs:**
- Check file permissions
- Verify disk space available
- Validate path exists before operation

---

## Error Category 6: Schema Validation Failures

**Potential Errors:**
```
ValidationError: Field required: feasibility_score
KeyError: 'red_flags'
TypeError: 'NoneType' object is not iterable
```

**Root Cause:** AI doesn't return all required fields or returns wrong types

**Prevention Strategy:**
```python
from typing import Any

def validate_and_fix_schema(data: dict, schema: dict) -> dict:
    """Validate and auto-fix common schema issues"""
    fixed_data = {}
    
    # Process each field in schema
    for field, field_info in schema['properties'].items():
        if field in data and data[field] is not None:
            # Field exists, validate type
            fixed_data[field] = data[field]
        elif field in schema.get('required', []):
            # Required field missing, add default
            field_type = field_info['type']
            
            if field_type == 'array':
                fixed_data[field] = []
                logger.warning(f"Added default empty array for: {field}")
            elif field_type == 'string':
                fixed_data[field] = ''
                logger.warning(f"Added default empty string for: {field}")
            elif field_type == 'number':
                fixed_data[field] = 0
                logger.warning(f"Added default 0 for: {field}")
            elif field_type == 'object':
                fixed_data[field] = {}
                logger.warning(f"Added default empty object for: {field}")
            else:
                logger.error(f"Cannot auto-fix missing required field: {field}")
                raise ValidationError(f"Missing required field: {field}")
        else:
            # Optional field, skip
            pass
    
    return fixed_data

def retry_with_schema_fix(func, max_retries=3):
    """Retry function with increasingly specific schema prompts"""
    for attempt in range(max_retries):
        try:
            result = func()
            return result
        except (ValidationError, JSONDecodeError, KeyError) as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Schema validation failed (attempt {attempt + 1}): {e}")
            # Add more specific instructions to prompt
            # This would be implemented in the calling function
```

**Testing:**
- Test with incomplete JSON responses
- Test with wrong field types
- Test with extra fields
- Test with null values

**Fix if Occurs:**
- Use auto-fix with defaults
- Retry with more specific prompt
- Log and use fallback values

---

## Error Category 7: Memory/Resource Exhaustion

**Potential Errors:**
```
MemoryError: Unable to allocate array
RuntimeError: CUDA out of memory
OSError: [Errno 12] Cannot allocate memory
```

**Root Cause:** Too many models loaded or large model doesn't fit in memory

**Prevention Strategy:**
```python
import psutil
import gc

class ResourceMonitor:
    def __init__(self, max_memory_percent=85, max_gpu_memory_percent=90):
        self.max_memory_percent = max_memory_percent
        self.max_gpu_memory_percent = max_gpu_memory_percent
        self.monitoring = True
    
    def check_memory(self) -> bool:
        """Check if memory usage is acceptable"""
        memory = psutil.virtual_memory()
        
        if memory.percent > self.max_memory_percent:
            logger.warning(f"High memory usage: {memory.percent}%")
            return False
        
        return True
    
    def free_memory(self):
        """Attempt to free memory"""
        logger.info("Attempting to free memory")
        
        # Force garbage collection
        gc.collect()
        
        # Unload model if loaded
        if hasattr(self, 'loaded_model') and self.loaded_model:
            del self.loaded_model
            self.loaded_model = None
            gc.collect()
            logger.info("Unloaded model to free memory")
    
    def safe_load_model(self, model_path: str):
        """Load model with memory check"""
        if not self.check_memory():
            self.free_memory()
            
            # Check again
            if not self.check_memory():
                raise MemoryError("Not enough memory to load model")
        
        return Llama(model_path=model_path, n_ctx=4096)
```

**Testing:**
- Load multiple large models
- Run memory-intensive operations
- Simulate low memory conditions

**Fix if Occurs:**
- Unload current model
- Force garbage collection
- Reduce model context size
- Use smaller quantization

---

## Error Category 8: Request Timeout

**Potential Errors:**
```
TimeoutError: Request took too long
ReadTimeout: HTTPConnectionPool read timed out
asyncio.TimeoutError
```

**Root Cause:** Slow model inference or complex prompt

**Prevention Strategy:**
```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import asyncio

class TimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            # 5 minute timeout for AI requests
            return await asyncio.wait_for(call_next(request), timeout=300)
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=504,
                content={
                    "error": "Request timeout after 5 minutes",
                    "detail": "Model inference took too long. Try a simpler prompt."
                }
            )

app.add_middleware(TimeoutMiddleware)

# Also set timeout on HTTP client
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_http_session(timeout=120):
    """Create HTTP session with timeout and retry logic"""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    # Set default timeout
    original_request = session.request
    def request_with_timeout(*args, **kwargs):
        kwargs.setdefault('timeout', timeout)
        return original_request(*args, **kwargs)
    session.request = request_with_timeout
    
    return session
```

**Testing:**
- Send very complex prompts
- Test with large context windows
- Simulate slow model

**Fix if Occurs:**
- Increase timeout values
- Reduce prompt complexity
- Use smaller/faster model

---

## Error Category 9: Type Mismatches

**Potential Errors:**
```
TypeError: expected str, bytes or os.PathLike object, not NoneType
ValidationError: value is not a valid dict
AttributeError: 'str' object has no attribute 'get'
```

**Root Cause:** Incorrect type passed to function or API

**Prevention Strategy:**
```python
from pydantic import BaseModel, validator, Field
from typing import Optional, Dict, List

class GeminiGenerateRequest(BaseModel):
    """Strict type validation for all inputs"""
    model: str = Field(..., min_length=1)
    contents: str = Field(..., min_length=1)
    config: Optional[Dict] = Field(default_factory=dict)
    
    @validator('contents')
    def contents_must_be_string(cls, v):
        if not isinstance(v, str):
            raise ValueError('contents must be a string')
        if not v.strip():
            raise ValueError('contents cannot be empty')
        return v
    
    @validator('config')
    def config_must_be_dict(cls, v):
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError('config must be a dict or null')
        return v
    
    @validator('model')
    def model_must_be_valid(cls, v):
        valid_models = ['gemini-2.5-flash', 'gemini-pro']
        if v not in valid_models:
            # Accept any model name for compatibility
            pass
        return v

class ChatCreateRequest(BaseModel):
    model: str
    config: Dict = Field(default_factory=dict)
    
    class Config:
        extra = 'forbid'  # Reject extra fields

# Use everywhere
@app.post("/v1/models/generate")
async def generate_content(request: GeminiGenerateRequest):
    # Type is guaranteed to be correct
    ...
```

**Testing:**
- Send requests with wrong types
- Send null values
- Send empty strings
- Send extra fields

**Fix if Occurs:**
- Use Pydantic models everywhere
- Add type hints to all functions
- Validate inputs explicitly

---

## Error Category 10: Chat State Management

**Potential Errors:**
```
KeyError: 'chat_id'
RuntimeError: Chat session expired
ValueError: Chat session not found
```

**Root Cause:** Chat sessions not tracked properly or expired

**Prevention Strategy:**
```python
import uuid
import time
from threading import Lock
from typing import Dict, Optional

class ChatSession:
    def __init__(self, config: dict):
        self.config = config
        self.messages: List[Dict] = []
        self.created_at = time.time()
        self.last_used = time.time()
        self.system_instruction = config.get('systemInstruction', '')
        self.tools = config.get('tools', [])
    
    def add_message(self, role: str, content: str):
        self.messages.append({'role': role, 'content': content})
        self.last_used = time.time()

class ChatSessionManager:
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.lock = Lock()
        self.max_sessions = 100
        self.session_timeout = 3600  # 1 hour
    
    def create_session(self, config: dict) -> str:
        """Create new chat session with cleanup"""
        with self.lock:
            # Clean expired sessions
            self._cleanup_expired()
            
            # Check limit
            if len(self.sessions) >= self.max_sessions:
                # Remove oldest session
                oldest = min(
                    self.sessions.items(),
                    key=lambda x: x[1].last_used
                )
                del self.sessions[oldest[0]]
                logger.info(f"Removed oldest session to stay under limit")
            
            # Create new session
            chat_id = str(uuid.uuid4())
            self.sessions[chat_id] = ChatSession(config)
            logger.info(f"Created chat session: {chat_id}")
            return chat_id
    
    def get_session(self, chat_id: str) -> ChatSession:
        """Get session with validation"""
        with self.lock:
            if chat_id not in self.sessions:
                raise ValueError(f"Chat session not found: {chat_id}")
            
            session = self.sessions[chat_id]
            
            # Check if expired
            if time.time() - session.last_used > self.session_timeout:
                del self.sessions[chat_id]
                raise ValueError(f"Chat session expired: {chat_id}")
            
            return session
    
    def _cleanup_expired(self):
        """Remove expired sessions"""
        now = time.time()
        expired = [
            cid for cid, session in self.sessions.items()
            if now - session.last_used > self.session_timeout
        ]
        for cid in expired:
            del self.sessions[cid]
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")
```

**Testing:**
- Create many sessions
- Test session expiry
- Test concurrent session access
- Test invalid session IDs

**Fix if Occurs:**
- Implement session persistence (database)
- Increase timeout
- Add session renewal mechanism

---

## Pre-Flight Checklist

Before starting implementation:

- [ ] **Port Check:** 8888, 8889, 3000 are available
- [ ] **Backend Running:** DeathAIAUS Backend on port 8889
- [ ] **Models Available:** All 20 Pantheon models accessible
- [ ] **Python Deps:** FastAPI, uvicorn, pydantic, llama-cpp-python installed
- [ ] **Node Deps:** npm packages in v2 installed
- [ ] **Disk Space:** At least 10GB free
- [ ] **Memory:** At least 16GB RAM available
- [ ] **Backup:** v2 UI backed up
- [ ] **Git:** Current state committed
- [ ] **Logs Dir:** `logs/` directory exists

---

## Testing Strategy

### Phase 1: Unit Tests
- Test each error handler individually
- Test JSON parsing with malformed data
- Test schema validation with incomplete data

### Phase 2: Integration Tests
- Start backend, send requests from curl
- Test CORS from browser console
- Test tool execution with various paths

### Phase 3: End-to-End Tests
- Start all services
- Open v2 UI in browser
- Test each feature:
  - AI Chat
  - Task Planner
  - Feasibility Analyzer
  - Project Creation
  - Knowledge Base

---

## Rollback Strategy

If critical errors occur:

1. **Stop all services**
   ```bash
   # Kill all Python processes
   pkill -f gemini_compatible_backend
   pkill -f DeathAIAUS_Backend
   ```

2. **Restore v2 UI**
   ```bash
   cp -r C:/Users/Death/Desktop/DeathAIAUSIDEFCv2_BACKUP/* C:/Users/Death/Desktop/DeathAIAUSIDEFCv2/
   ```

3. **Use original Gemini** (if needed)
   - Restore original geminiService.ts
   - Use Gemini API key

---

## Monitoring & Debugging

### Enable Debug Logging
```python
logging.basicConfig(level=logging.DEBUG)
```

### Key Metrics to Monitor
- Request latency
- Memory usage
- Model load/unload frequency
- Error rates by type
- Session count

### Debug Endpoints
```python
@app.get("/debug/status")
async def debug_status():
    return {
        "sessions": len(chat_manager.sessions),
        "memory_percent": psutil.virtual_memory().percent,
        "model_loaded": current_model_id is not None,
        "uptime": time.time() - start_time
    }
```

---

## Ready to Build

All potential errors identified ✅  
Prevention strategies in place ✅  
Testing approach defined ✅  
Rollback plan ready ✅

**Type "build" to start implementation!**

