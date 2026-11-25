#!/usr/bin/env python3
"""
Gemini-Compatible Backend for DeathAIAUS IDE
============================================

A FastAPI backend that mimics the Gemini API so v2 UI works without changes.
Intercepts Gemini API calls and routes them to Death's Pantheon models.

Author: DeathAIAUS
Copyright: DeathAIAUS 2025
"""

import os
import sys
import json
import time
import logging
import threading
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Core dependencies
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
import uvicorn
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/gemini_backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Pydantic Models for Request/Response
class GenerateRequest(BaseModel):
    """Request model for content generation"""
    model: str
    contents: str
    config: Optional[Dict] = {}
    
    @field_validator('contents')
    @classmethod
    def contents_must_be_string(cls, v):
        if not isinstance(v, str):
            raise ValueError('contents must be a string')
        if not v.strip():
            raise ValueError('contents cannot be empty')
        return v
    
    @field_validator('config')
    @classmethod
    def config_must_be_dict(cls, v):
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError('config must be a dict or null')
        return v

class GenerateResponse(BaseModel):
    """Response model for content generation"""
    text: str

class ChatCreateRequest(BaseModel):
    """Request model for chat creation"""
    model: str
    config: Dict = {}
    
    class Config:
        extra = 'forbid'

class ChatCreateResponse(BaseModel):
    """Response model for chat creation"""
    chatId: str
    model: str
    config: Dict

class ChatSendRequest(BaseModel):
    """Request model for sending chat messages"""
    message: str

class ChatSendResponse(BaseModel):
    """Response model for chat messages"""
    text: str
    functionCalls: Optional[List[Dict]] = None

class ChatSession:
    """Manages individual chat sessions"""
    def __init__(self, config: dict):
        self.config = config
        self.messages: List[Dict] = []
        self.created_at = time.time()
        self.last_used = time.time()
        self.system_instruction = config.get('systemInstruction', '')
        self.tools = config.get('tools', [])
    
    def add_message(self, role: str, content: str):
        """Add a message to the chat session"""
        self.messages.append({'role': role, 'content': content})
        self.last_used = time.time()

class ChatSessionManager:
    """Manages all chat sessions"""
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.lock = threading.Lock()
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

class GeminiCompatibleBackend:
    """Main Gemini-Compatible Backend Server"""
    
    def __init__(self, deathaiaus_backend_url: str = "http://localhost:8889"):
        self.deathaiaus_backend_url = deathaiaus_backend_url
        self.chat_manager = ChatSessionManager()
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="Gemini-Compatible Backend",
            description="Mimics Gemini API for DeathAIAUS IDE v2",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://localhost:5173"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self._setup_routes()
        
        # Test DeathAIAUS backend connection
        self._test_backend_connection()
    
    def _setup_routes(self):
        """Setup all API routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "sessions": len(self.chat_manager.sessions)
            }
        
        @self.app.post("/v1/models/generate", response_model=GenerateResponse)
        async def generate_content(request: GenerateRequest):
            """Generate content using DeathAIAUS backend"""
            try:
                # Convert to DeathAIAUS backend format
                messages = [{"role": "user", "content": request.contents}]
                
                # Add system instruction if present
                if "systemInstruction" in request.config:
                    messages.insert(0, {
                        "role": "system",
                        "content": request.config["systemInstruction"]
                    })
                
                # Call DeathAIAUS backend
                response = requests.post(
                    f"{self.deathaiaus_backend_url}/v1/chat/completions",
                    json={
                        "model": "NEPHTHYS-DeathAIAUS",  # Use the loaded model
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 4000
                    },
                    timeout=120
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"DeathAIAUS backend error: {response.text}"
                    )
                
                # Convert response to Gemini format
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Handle JSON schema requests
                if "responseMimeType" in request.config and request.config["responseMimeType"] == "application/json":
                    content = self._ensure_json_response(content, request.config.get("responseSchema"))
                
                return GenerateResponse(text=content)
                
            except requests.exceptions.Timeout:
                raise HTTPException(status_code=504, detail="Request timeout")
            except requests.exceptions.ConnectionError:
                raise HTTPException(status_code=503, detail="DeathAIAUS backend unavailable")
            except Exception as e:
                logger.error(f"Generate content error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/v1/chats/create", response_model=ChatCreateResponse)
        async def create_chat(request: ChatCreateRequest):
            """Create a new chat session"""
            try:
                chat_id = self.chat_manager.create_session(request.config)
                return ChatCreateResponse(
                    chatId=chat_id,
                    model=request.model,
                    config=request.config
                )
            except Exception as e:
                logger.error(f"Create chat error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/v1/chats/{chat_id}/send", response_model=ChatSendResponse)
        async def send_chat_message(chat_id: str, request: ChatSendRequest):
            """Send a message to a chat session"""
            try:
                session = self.chat_manager.get_session(chat_id)
                
                # Add user message to session
                session.add_message("user", request.message)
                
                # Prepare messages for DeathAIAUS backend
                messages = []
                
                # Add system instruction if present
                if session.system_instruction:
                    messages.append({
                        "role": "system",
                        "content": session.system_instruction
                    })
                
                # Add conversation history
                messages.extend(session.messages)
                
                # Call DeathAIAUS backend
                response = requests.post(
                    f"{self.deathaiaus_backend_url}/v1/chat/completions",
                    json={
                        "model": "NEPHTHYS-DeathAIAUS",  # Use the loaded model
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 4000
                    },
                    timeout=120
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"DeathAIAUS backend error: {response.text}"
                    )
                
                # Get response
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Add assistant message to session
                session.add_message("assistant", content)
                
                # Check for function calls (if tools are configured)
                function_calls = None
                if session.tools and self._has_function_call(content):
                    function_calls = self._extract_function_calls(content)
                
                return ChatSendResponse(
                    text=content,
                    functionCalls=function_calls
                )
                
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except requests.exceptions.Timeout:
                raise HTTPException(status_code=504, detail="Request timeout")
            except requests.exceptions.ConnectionError:
                raise HTTPException(status_code=503, detail="DeathAIAUS backend unavailable")
            except Exception as e:
                logger.error(f"Send chat message error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/debug/status")
        async def debug_status():
            """Debug endpoint for monitoring"""
            import psutil
            return {
                "sessions": len(self.chat_manager.sessions),
                "memory_percent": psutil.virtual_memory().percent,
                "deathaiaus_backend_url": self.deathaiaus_backend_url,
                "uptime": time.time() - self.start_time if hasattr(self, 'start_time') else 0
            }
    
    def _test_backend_connection(self):
        """Test connection to DeathAIAUS backend"""
        try:
            response = requests.get(f"{self.deathaiaus_backend_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("Successfully connected to DeathAIAUS backend")
            else:
                logger.warning(f"DeathAIAUS backend returned status {response.status_code}")
        except Exception as e:
            logger.error(f"Cannot connect to DeathAIAUS backend: {e}")
            logger.error("Make sure DeathAIAUS backend is running on port 8889")
    
    def _ensure_json_response(self, content: str, schema: Optional[Dict] = None) -> str:
        """Ensure response is valid JSON, with schema validation if provided"""
        try:
            # Try to parse as JSON first
            json.loads(content)
            return content
        except json.JSONDecodeError:
            # If not JSON, try to extract JSON from the response
            import re
            
            # Look for JSON in markdown code blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                try:
                    json.loads(json_match.group(1))
                    return json_match.group(1)
                except:
                    pass
            
            # Look for bare JSON object
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    json.loads(json_match.group(0))
                    return json_match.group(0)
                except:
                    pass
            
            # If still not valid JSON, return a basic JSON response
            logger.warning("Could not extract valid JSON from response")
            return '{"error": "Could not generate valid JSON response"}'
    
    def _has_function_call(self, content: str) -> bool:
        """Check if content contains function calls"""
        # Simple heuristic - look for function call patterns
        return "function_call" in content.lower() or "tool_call" in content.lower()
    
    def _extract_function_calls(self, content: str) -> List[Dict]:
        """Extract function calls from content"""
        # This is a simplified implementation
        # In a real scenario, you'd parse the actual function call format
        return []
    
    def start(self, host: str = "127.0.0.1", port: int = 8888):
        """Start the Gemini-Compatible Backend server"""
        self.start_time = time.time()
        logger.info(f"Starting Gemini-Compatible Backend on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port, log_level="info")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gemini-Compatible Backend for DeathAIAUS IDE")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8888, help="Port to bind to")
    parser.add_argument("--deathaiaus-url", default="http://localhost:8889", 
                       help="URL of DeathAIAUS backend")
    
    args = parser.parse_args()
    
    # Create and start backend
    backend = GeminiCompatibleBackend(args.deathaiaus_url)
    backend.start(args.host, args.port)

if __name__ == "__main__":
    main()
