"""
Vercel Serverless Function Entry Point for RailServe
This file exports the Flask app for Vercel's serverless platform
"""
import sys
import os

# Add parent directory to path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app
from src.app import app

# Vercel looks for an 'app' variable
# The Flask app is already named 'app' so it will work directly
