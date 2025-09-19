#!/usr/bin/env python3
"""
Initialize RailServe application with minimal setup
"""
import os
import sys

# Set required environment variables
os.environ['SESSION_SECRET'] = 'railway-secret-key-2025-replit'
os.environ['FLASK_ENV'] = 'development'

# Add src to Python path
sys.path.insert(0, 'src')

# Import and initialize the Flask app
from src.app import app, db
import main  # This imports the routes from main.py

if __name__ == '__main__':
    with app.app_context():
        # Create database tables
        print("Creating database tables...")
        db.create_all()
        
        # Create a simple admin user if none exists
        from src.models import User
        from werkzeug.security import generate_password_hash
        
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(
                username='admin',
                email='admin@railserve.com', 
                password_hash=generate_password_hash('admin123'),
                role='super_admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created (admin/admin123)")
        
        print("✅ App initialized successfully")
    
    # Start the development server
    app.run(host='0.0.0.0', port=5000, debug=True)