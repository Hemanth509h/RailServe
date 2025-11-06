"""
Vercel Serverless Function Entry Point for RailServe
This file exports the Flask app for Vercel's serverless platform
"""
import sys
import os

# Add parent directory to path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import main module which registers all routes and returns the configured app
# This ensures all routes from main.py are registered
import main

# Export the app for Vercel
app = main.app
