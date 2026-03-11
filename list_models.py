"""
Gemini Model Discovery Script
Usage: .\.venv\Scripts\python.exe list_models.py

This script connects to Google AI Studio using your GEMINI_API_KEY 
and lists all models that support 'generateContent'. 
Use this to find the correct model name for your .env file if you get a 404 error.
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file.")
else:
    try:
        genai.configure(api_key=api_key)
        print("Available models that support content generation:")
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                print(f" - {m.name}")
        print("\nTo use one of these, update GEMINI_MODEL in your .env (e.g., GEMINI_MODEL=gemini-2.0-flash)")
    except Exception as e:
        print(f"Failed to list models: {e}")
