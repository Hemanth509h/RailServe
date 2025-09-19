#!/usr/bin/env python3
"""
Database Migration Script: Add waitlist_type column to booking table

This script adds the missing waitlist_type column to the booking table
to fix the PostgreSQL error: column booking.waitlist_type does not exist
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def add_waitlist_type_column():
    """Add waitlist_type column to booking table"""
    
    # Database connection string
    database_url = 'postgresql://postgres:12345678@localhost:5432/railserve'
    
    try:
        print("🔌 Connecting to PostgreSQL database...")
        
        # Parse the database URL
        if database_url.startswith('postgresql://'):
            # Extract connection details from URL
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path[1:]  # Remove leading slash
            )
        else:
            conn = psycopg2.connect(database_url)
        
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected successfully")
        
        # Check if the column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='booking' AND column_name='waitlist_type'
        """)
        
        if cursor.fetchone():
            print("ℹ️  Column 'waitlist_type' already exists in booking table")
            return True
        
        print("🔧 Adding waitlist_type column to booking table...")
        
        # Add the waitlist_type column with default value
        cursor.execute("""
            ALTER TABLE booking 
            ADD COLUMN waitlist_type VARCHAR(10) DEFAULT 'GNWL'
        """)
        
        # Update existing records to have a default value
        cursor.execute("""
            UPDATE booking 
            SET waitlist_type = 'GNWL' 
            WHERE waitlist_type IS NULL
        """)
        
        # Add a comment to the column
        cursor.execute("""
            COMMENT ON COLUMN booking.waitlist_type IS 'Waitlist type: GNWL, RAC, PQWL, RLWL, TQWL'
        """)
        
        print("✅ Successfully added waitlist_type column to booking table")
        print("📋 Column details:")
        print("   - Name: waitlist_type")
        print("   - Type: VARCHAR(10)")
        print("   - Default: 'GNWL'")
        print("   - Values: GNWL, RAC, PQWL, RLWL, TQWL")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verify_column_exists():
    """Verify the column was added successfully"""
    
    database_url = 'postgresql://postgres:12345678@localhost:5432/railserve'
    
    try:
        from urllib.parse import urlparse
        parsed = urlparse(database_url)
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:]
        )
        
        cursor = conn.cursor()
        
        # Check column exists and get details
        cursor.execute("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns 
            WHERE table_name='booking' AND column_name='waitlist_type'
        """)
        
        result = cursor.fetchone()
        if result:
            print("✅ Verification successful - Column details:")
            print(f"   - Name: {result[0]}")
            print(f"   - Type: {result[1]}")
            print(f"   - Default: {result[2]}")
            print(f"   - Nullable: {result[3]}")
            return True
        else:
            print("❌ Verification failed - Column not found")
            return False
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    print("🔧 RailServe Database Migration: Add waitlist_type column")
    print("=" * 60)
    
    if add_waitlist_type_column():
        print("\n🔍 Verifying the change...")
        if verify_column_exists():
            print("\n🎉 Migration completed successfully!")
            print("\n📋 What was done:")
            print("   ✓ Added waitlist_type column to booking table")
            print("   ✓ Set default value 'GNWL' for existing records")
            print("   ✓ Added column comment for documentation")
            print("\n🚀 Your RailServe application should now work without errors!")
        else:
            print("\n❌ Migration verification failed")
            sys.exit(1)
    else:
        print("\n❌ Migration failed")
        sys.exit(1)