"""
RailServe Database Initialization Script
=========================================
This is a thin wrapper around the db_init package for command-line execution.

Usage:
    python init_db_with_fallback.py

The actual initialization logic is in the src/db_init package for better organization.
"""

from src.db_init import initialize_database


if __name__ == '__main__':
    initialize_database()
