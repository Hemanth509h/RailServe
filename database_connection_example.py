"""
Database Connection Example for Replit
========================================

In Replit, you don't need .env files or python-dotenv.
Secrets added through the Replit UI are automatically available as environment variables.

Example: How to connect to PostgreSQL using environment variables
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

# Method 1: Simple connection using DATABASE_URL secret
# Replit automatically loads DATABASE_URL from your secrets
database_url = os.environ.get("DATABASE_URL")

if database_url:
    # Create engine with basic configuration
    engine = create_engine(database_url)
    print("✓ Database engine created successfully")
else:
    print("✗ DATABASE_URL not found in environment variables")
    print("  Please add DATABASE_URL as a secret in Replit")

# Method 2: Advanced connection with pooling disabled
# Useful for serverless/transaction pooler environments like Supabase
if database_url:
    engine_with_no_pool = create_engine(
        database_url,
        poolclass=NullPool  # Disable client-side connection pooling
    )
    print("✓ Engine with NullPool created (recommended for Supabase)")

# Method 3: Connection with SSL requirement
# If your database requires SSL connections
if database_url:
    # Add sslmode parameter if not already in the URL
    if "sslmode" not in database_url:
        separator = "&" if "?" in database_url else "?"
        database_url_with_ssl = f"{database_url}{separator}sslmode=require"
    else:
        database_url_with_ssl = database_url
    
    engine_with_ssl = create_engine(database_url_with_ssl)
    print("✓ Engine with SSL created")

# Test the connection
if database_url:
    try:
        with engine.connect() as connection:
            print("✓ Connection successful!")
            print(f"  Connected to: {database_url.split('@')[1].split('/')[0]}")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")

"""
IMPORTANT NOTES FOR REPLIT:
============================

1. NO .env FILES NEEDED
   - Secrets added in Replit UI are automatically environment variables
   - Just use os.environ.get("SECRET_NAME")

2. URL ENCODING FOR PASSWORDS
   - Special characters in passwords must be URL-encoded:
     # → %23
     @ → %40
     % → %25
     / → %2F
     ? → %3F
     & → %26
   
   Example:
   Password: MyPass#123@
   Encoded:  MyPass%23123%40

3. SUPABASE SPECIFIC
   - Use Transaction Pooler (port 5432) with NullPool
   - Always include sslmode=require
   - Format: postgresql://user:password@host:5432/database?sslmode=require

4. YOUR DATABASE_URL FORMAT
   postgresql://postgres:Htnameh509h%23@db.mapkjzlvyeddjwfkrhud.supabase.co:5432/postgres
   
   Note: The # in your password is encoded as %23
"""
