#!/usr/bin/env python3
"""
Simple test of DeathAIAUS Backend
"""

try:
    from DeathAIAUS_Backend import DeathAIAUSBackend
    print("Import successful")
    
    # Create backend instance
    backend = DeathAIAUSBackend()
    print("Backend created")
    
    # Check models
    print(f"Found {len(backend.models)} models")
    
    # Try to start server (but don't run it)
    print("Backend ready to start")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
