#!/usr/bin/env python3
"""
Local Database Creation Script for RailServe
This script creates the railserve database and populates it with data.

STEP 1: First run this script to create the database
STEP 2: Then run main.py to start the application

Usage:
    python create_local_database.py
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    """Create the railserve database if it doesn't exist"""
    try:
        print("🔌 Connecting to PostgreSQL server...")
        # Connect to PostgreSQL server (to postgres database)
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='12345678',
            database='postgres'  # Connect to default postgres database first
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if railserve database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'railserve'")
        exists = cursor.fetchone()
        
        if not exists:
            print("🗄️  Creating 'railserve' database...")
            cursor.execute('CREATE DATABASE railserve')
            print("✅ Database 'railserve' created successfully")
        else:
            print("📄 Database 'railserve' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Make sure:")
        print("   - PostgreSQL is running on localhost:5432")
        print("   - Username: postgres")
        print("   - Password: 12345678")
        print("   - You can connect to the 'postgres' database")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def populate_database():
    """Populate the database with tables and data"""
    try:
        print("\n🏗️  Setting up tables and populating data...")
        
        # Set environment variables for the setup script
        os.environ['DATABASE_URL'] = 'postgresql://postgres:12345678@localhost:5432/railserve'
        os.environ['SESSION_SECRET'] = 'railway-secret-key-2025'
        os.environ['ADMIN_INITIAL_PASSWORD'] = 'admin123'
        
        # Add current directory to path for imports
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Import the database setup class directly
        from database_setup import RailwayDatabaseSetup
        
        # Create setup instance with local database URL
        db_url = 'postgresql://postgres:12345678@localhost:5432/railserve'
        setup = RailwayDatabaseSetup(db_url)
        
        # Verify connection
        if not setup.verify_connection():
            return False
        
        # Create tables
        if not setup.create_tables():
            return False
        
        # Clear existing data (if any)
        if not setup.reset_data():
            return False
            
        # Populate stations (1000 stations)
        if not setup.populate_stations():
            return False
            
        # Populate trains (1000 trains)  
        if not setup.populate_trains():
            return False
            
        # Create train routes
        if not setup.create_train_routes():
            return False
            
        # Create admin user
        if not setup.create_admin_user():
            return False
            
        # Create sample users
        if not setup.create_sample_users():
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database population failed: {e}")
        return False

def main():
    """Main function"""
    print("🚂 RailServe Local Database Setup")
    print("=" * 50)
    
    # Step 1: Create database
    if not create_database():
        print("\n❌ Failed to create database. Please check your PostgreSQL connection.")
        sys.exit(1)
    
    # Step 2: Populate database
    if not populate_database():
        print("\n❌ Failed to populate database.")
        sys.exit(1)
    
    print("\n🎉 SUCCESS! Your RailServe database is ready!")
    print("\n📋 Next Steps:")
    print("   1. Run: python main.py")
    print("   2. Open: http://localhost:5000")
    print("   3. Login as admin: admin / admin123")
    print("\n🚂 Your railway booking system has:")
    print("   ✅ 1000 railway stations")
    print("   ✅ 1000 trains with routes")
    print("   ✅ Complete booking system")
    print("   ✅ Admin dashboard")
    print("   ✅ Payment processing")

if __name__ == '__main__':
    main()