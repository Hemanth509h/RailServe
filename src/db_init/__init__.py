"""
Database Initialization Package
================================
This package handles database seeding for the RailServe application.

Usage:
    from src.db_init import initialize_database
    initialize_database()
"""

from .orchestrator import initialize_database

__all__ = ['initialize_database']
