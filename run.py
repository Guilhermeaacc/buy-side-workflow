#!/usr/bin/env python3
import uvicorn
import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

if __name__ == "__main__":
    print("Starting PDF Text Extractor...")
    
    # Use Railway's PORT environment variable if available, otherwise default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Server will be available at: http://0.0.0.0:{port}")
    print("Make sure to set your OPENAI_API_KEY in the .env file")
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=False,  # Disable reload for production
        app_dir="app"
    )