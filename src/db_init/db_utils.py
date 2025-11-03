"""
Database Utility Functions
===========================
Handles database schema management.
"""

from src.database import db


def reset_database():
    """Drop all tables and recreate schema"""
    print("\n[DATABASE] Resetting database...")
    db.drop_all()
    db.create_all()
    print("✓ All tables created")
