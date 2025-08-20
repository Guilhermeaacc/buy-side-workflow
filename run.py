#!/usr/bin/env python3
import uvicorn
import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

if __name__ == "__main__":
    print("Starting PDF Text Extractor...")
    print("Server will be available at: http://localhost:8000")
    print("Make sure to set your OPENAI_API_KEY in the .env file")
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        app_dir="app"
    )