"""
Initialize database tables for RailServe application
Run this script once to create all necessary database tables
"""

from src.app import app, db

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("Database tables created successfully!")
