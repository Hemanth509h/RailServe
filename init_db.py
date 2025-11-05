#!/usr/bin/env python3
"""
Database Initialization Script
Populates railway.db with 1000 stations and 1250 trains
"""

if __name__ == '__main__':
    from src.db_init.orchestrator import initialize_database
    initialize_database()
