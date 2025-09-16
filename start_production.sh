#!/bin/bash

# Production startup script for RailServe
# This script starts the application using Gunicorn with proper production settings

# Set production environment
export FLASK_ENV=production

# Check for required environment variables
if [ -z "$SESSION_SECRET" ]; then
    echo "Error: SESSION_SECRET environment variable is required"
    exit 1
fi

if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL environment variable is required"
    exit 1
fi

echo "Starting RailServe in production mode..."
echo "Workers: $(python -c 'import multiprocessing; print(multiprocessing.cpu_count() * 2 + 1)')"
echo "Listening on: 0.0.0.0:5000"

# Start Gunicorn with configuration file
exec gunicorn --config gunicorn.conf.py main:app