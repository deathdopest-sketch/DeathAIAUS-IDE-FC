#!/usr/bin/env python3
"""
DeathAIAUS Backend - Python AI Model Server
===========================================

A high-performance Python backend for DeathAIAUS IDE FC that provides:
- Full GGUF model support (including Qwen2, Mistral, Llama2, etc.)
- OpenAI-compatible API endpoints
- Smart model management with hot-swapping
- GPU acceleration support
- Pantheon model integration

Author: DeathAIAUS
Copyright: DeathAIAUS 2025
"""

import os
import sys
import json
import time
import logging
import threading
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Core dependencies
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# AI Model dependencies
from llama_cpp import Llama

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/deathaiaus_backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

class ModelInfo(BaseModel):
    """Model information structure"""
    id: str
    name: str
    filename: str
    full_path: str
    size: str
    power: str
    role: str
    tier: str
    emoji: str
    loaded: bool = False
    load_time: Optional[float] = None
    use_count: int = 0
    last_used: Optional[datetime] = None

class ChatMessage(BaseModel):
    """Chat message structure"""
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    """Chat completion request structure"""
    model: str
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 4000
    stream: bool = False

class DeathAIAUSBackend:
    """DeathAIAUS Python Backend Server"""
    
    def __init__(self, pantheon_path: str = r"G:\My Drive\DeathAIAUS_PANTHEON"):
        self.pantheon_path = Path(pantheon_path)
        self.models: Dict[str, ModelInfo] = {}
        self.loaded_model: Optional[Llama] = None
        self.current_model_id: Optional[str] = None
        self.model_lock = threading.Lock()
        
        # Load Pantheon configuration
        self.pantheon_config = self._load_pantheon_config()
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="DeathAIAUS Backend",
            description="AI Model Server for DeathAIAUS IDE FC",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self._setup_routes()
        
        # Scan for models
        self._scan_models()
        
        logger.info(f"DeathAIAUS Backend initialized with {len(self.models)} models")
    
    def _load_pantheon_config(self) -> Dict:
        """Load Pantheon configuration from death_pantheon.json"""
        try:
            config_path = Path("death_pantheon.json")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning("death_pantheon.json not found, using default config")
                return {"pantheon": {}}
        except Exception as e:
            logger.error(f"Failed to load Pantheon config: {e}")
            return {"pantheon": {}}
    
    def _scan_models(self):
        """Scan Pantheon directory for available models"""
        if not self.pantheon_path.exists():
            logger.error(f"Pantheon path does not exist: {self.pantheon_path}")
            return
        
        logger.info(f"Scanning Pantheon directory: {self.pantheon_path}")
        
        # Find all .gguf files
        gguf_files = list(self.pantheon_path.rglob("*.gguf"))
        logger.info(f"Found {len(gguf_files)} GGUF files")
        
        for gguf_file in gguf_files:
            try:
                # Get relative path for model ID
                relative_path = gguf_file.relative_to(self.pantheon_path)
                model_id = str(relative_path).replace("\\", "/")
                
                # Get model info from Pantheon config
                pantheon_info = self.pantheon_config.get("pantheon", {}).get(gguf_file.name, {})
                
                # Create model info
                model_info = ModelInfo(
                    id=model_id,
                    name=pantheon_info.get("name", gguf_file.stem),
                    filename=gguf_file.name,
                    full_path=str(gguf_file),
                    size=pantheon_info.get("size", "Unknown"),
                    power=pantheon_info.get("power", "Unknown"),
                    role=pantheon_info.get("role", "General Purpose"),
                    tier=pantheon_info.get("tier", "Unknown"),
                    emoji=pantheon_info.get("emoji", "🤖")
                )
                
                self.models[model_id] = model_info
                logger.info(f"Registered model: {model_info.name} ({model_info.tier}) - {model_info.size}")
                
            except Exception as e:
                logger.error(f"Failed to process model {gguf_file}: {e}")
        
        logger.info(f"Successfully registered {len(self.models)} models")
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "backend": "DeathAIAUS Python Backend",
                "version": "1.0.0",
                "models_available": len(self.models),
                "current_model": self.current_model_id,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/v1/models")
        async def list_models():
            """List available models"""
            model_list = []
            for model_id, model_info in self.models.items():
                model_list.append({
                    "id": model_id,
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "deathaiaus",
                    "name": model_info.name,
                    "filename": model_info.filename,
                    "size": model_info.size,
                    "power": model_info.power,
                    "role": model_info.role,
                    "tier": model_info.tier,
                    "emoji": model_info.emoji,
                    "loaded": model_info.loaded
                })
            
            return {
                "object": "list",
                "data": model_list
            }
        
        @self.app.post("/v1/models/load")
        async def load_model(request: Dict[str, str]):
            """Load a specific model"""
            model_id = request.get("model")
            if not model_id:
                raise HTTPException(status_code=400, detail="Model ID required")
            
            if model_id not in self.models:
                raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
            
            try:
                success = await self._load_model(model_id)
                if success:
                    return {"status": "success", "message": f"Model {model_id} loaded successfully"}
                else:
                    raise HTTPException(status_code=500, detail="Failed to load model")
            except Exception as e:
                logger.error(f"Error loading model {model_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/v1/models/unload")
        async def unload_model():
            """Unload current model"""
            try:
                await self._unload_model()
                return {"status": "success", "message": "Model unloaded successfully"}
            except Exception as e:
                logger.error(f"Error unloading model: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/v1/models/current")
        async def get_current_model():
            """Get currently loaded model"""
            if self.current_model_id:
                return {
                    "model_id": self.current_model_id,
                    "model_info": self.models[self.current_model_id].dict()
                }
            else:
                return {"model_id": None, "message": "No model loaded"}
        
        @self.app.get("/v1/models/status")
        async def get_model_status():
            """Get detailed model status"""
            loaded_models = [model for model in self.models.values() if model.loaded]
            
            return {
                "loaded_count": len(loaded_models),
                "total_models": len(self.models),
                "current_model": self.current_model_id,
                "loaded_models": [
                    {
                        "id": model.id,
                        "name": model.name,
                        "tier": model.tier,
                        "use_count": model.use_count,
                        "last_used": model.last_used.isoformat() if model.last_used else None
                    }
                    for model in loaded_models
                ]
            }
        
        @self.app.post("/v1/chat/completions")
        async def chat_completions(request: ChatCompletionRequest):
            """Chat completions endpoint"""
            if not self.loaded_model:
                raise HTTPException(status_code=400, detail="No model loaded")
            
            try:
                # Convert messages to llama-cpp format
                messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
                
                # Generate response
                response = self.loaded_model.create_chat_completion(
                    messages=messages,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    stream=request.stream
                )
                
                # Update model usage stats
                if self.current_model_id:
                    self.models[self.current_model_id].use_count += 1
                    self.models[self.current_model_id].last_used = datetime.now()
                
                return response
                
            except Exception as e:
                logger.error(f"Error in chat completion: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/pantheon")
        async def get_pantheon_info():
            """Get Pantheon information"""
            return {
                "pantheon": self.pantheon_config.get("pantheon", {}),
                "usage_recommendations": self.pantheon_config.get("usage_recommendations", {}),
                "tiers": self.pantheon_config.get("tiers", {})
            }
    
    async def _load_model(self, model_id: str) -> bool:
        """Load a model into memory"""
        with self.model_lock:
            try:
                # Unload current model if any
                if self.loaded_model:
                    await self._unload_model()
                
                model_info = self.models[model_id]
                logger.info(f"Loading model: {model_info.name} from {model_info.full_path}")
                
                # Check if file exists
                if not Path(model_info.full_path).exists():
                    logger.error(f"Model file not found: {model_info.full_path}")
                    return False
                
                # Load model with llama-cpp-python
                start_time = time.time()
                
                self.loaded_model = Llama(
                    model_path=model_info.full_path,
                    n_ctx=2048,  # Context length
                    n_gpu_layers=-1,  # Use all GPU layers if available
                    verbose=False,
                    n_threads=os.cpu_count() - 1  # Use most CPU cores
                )
                
                load_time = time.time() - start_time
                
                # Update model info
                model_info.loaded = True
                model_info.load_time = load_time
                self.current_model_id = model_id
                
                logger.info(f"Model {model_info.name} loaded successfully in {load_time:.2f}s")
                return True
                
            except Exception as e:
                logger.error(f"Failed to load model {model_id}: {e}")
                return False
    
    async def _unload_model(self):
        """Unload current model from memory"""
        with self.model_lock:
            if self.loaded_model:
                try:
                    # Free model memory
                    del self.loaded_model
                    self.loaded_model = None
                    
                    # Update model info
                    if self.current_model_id and self.current_model_id in self.models:
                        self.models[self.current_model_id].loaded = False
                        self.models[self.current_model_id].load_time = None
                    
                    self.current_model_id = None
                    logger.info("Model unloaded successfully")
                    
                except Exception as e:
                    logger.error(f"Error unloading model: {e}")
    
    def get_recommended_model(self, workflow: str) -> Optional[str]:
        """Get recommended model for a specific workflow"""
        recommendations = self.pantheon_config.get("usage_recommendations", {})
        
        if workflow in recommendations:
            primary_models = recommendations[workflow].get("primary", [])
            for model_name in primary_models:
                # Find model by name
                for model_id, model_info in self.models.items():
                    if model_info.name == model_name:
                        return model_id
        
        # Fallback to smallest model (IZANAMI)
        for model_id, model_info in self.models.items():
            if model_info.name == "IZANAMI":
                return model_id
        
        # Last resort: return first available model
        return list(self.models.keys())[0] if self.models else None
    
    def run(self, host: str = "localhost", port: int = 8888):
        """Run the backend server"""
        logger.info(f"Starting DeathAIAUS Backend on {host}:{port}")
        logger.info(f"Available models: {len(self.models)}")
        
        # Auto-load recommended model for coding
        recommended_model = self.get_recommended_model("coding_projects")
        if recommended_model:
            logger.info(f"Auto-loading recommended model: {self.models[recommended_model].name}")
            asyncio.run(self._load_model(recommended_model))
        
        # Start server
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DeathAIAUS Backend Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8888, help="Port to bind to")
    parser.add_argument("--pantheon-path", default=r"G:\My Drive\DeathAIAUS_PANTHEON", 
                       help="Path to Pantheon models directory")
    
    args = parser.parse_args()
    
    # Create and run backend
    backend = DeathAIAUSBackend(pantheon_path=args.pantheon_path)
    backend.run(host=args.host, port=args.port)

if __name__ == "__main__":
    main()
