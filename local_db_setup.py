#!/usr/bin/env python3
"""
Local Database Setup Script for RailServe
This script connects to your local PostgreSQL database and sets up everything.

Usage:
    python local_db_setup.py

Make sure PostgreSQL is running on localhost:5432 with:
- Username: postgres
- Password: 12345678
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Set environment variables for the app
os.environ['DATABASE_URL'] = 'postgresql://postgres:12345678@localhost:5432/railserve'
os.environ['SESSION_SECRET'] = 'railway-secret-key-2025'
os.environ['ADMIN_INITIAL_PASSWORD'] = 'admin123'

def create_database_if_not_exists():
    """Create the railserve database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (without database)
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='12345678'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'railserve'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Creating 'railserve' database...")
            cursor.execute('CREATE DATABASE railserve')
            print("✅ Database 'railserve' created successfully")
        else:
            print("📄 Database 'railserve' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        print("Make sure PostgreSQL is running on localhost:5432")
        print("Username: postgres, Password: 12345678")
        return False

def main():
    """Main setup function"""
    print("🚂 RailServe Local Database Setup")
    print("=" * 40)
    
    # Step 1: Create database if needed
    if not create_database_if_not_exists():
        sys.exit(1)
    
    # Step 2: Run the main database setup script
    print("\n🏗️  Setting up tables and data...")
    try:
        # Import and run the main setup script
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from database_setup import main as setup_main
        setup_main()
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)
    
    print("\n🎉 Local database setup completed!")
    print("You can now run the Flask app with: python main.py")
    print("Admin login: admin / admin123")

if __name__ == '__main__':
    main()