# app.py - Flask Application Core

## Overview
The main Flask application configuration file that sets up the web application, database connections, and integrates all components of the RailServe railway reservation system.

## Key Components

### Flask Application Setup
- **Flask Instance**: Creates the main Flask web application
- **Secret Key**: Configures session security using environment variables
- **Proxy Fix**: WSGI middleware for handling proxy headers in production

### Database Configuration
- **SQLAlchemy Setup**: Configures PostgreSQL database connection
- **Connection Pooling**: Implements pool recycling and pre-ping for reliability
- **Database URL**: Uses environment variable for database connection string

### Authentication System
- **Login Manager**: Configures Flask-Login for user session management
- **User Loader**: Defines how users are loaded from the database
- **Login View**: Sets the default login route for authentication

### Blueprint Registration
- **Authentication Blueprint**: Handles login, logout, and registration
- **Admin Blueprint**: Admin panel functionality with `/admin` prefix
- **Booking Blueprint**: Train booking functionality with `/booking` prefix
- **Payment Blueprint**: Payment processing with `/payment` prefix

### Database Initialization
- **Table Creation**: Automatically creates all database tables
- **Default Admin**: Creates a default super admin user if none exists
- **Model Import**: Ensures all models are loaded for table creation

## Dependencies
- Flask web framework
- Flask-SQLAlchemy for database ORM
- Flask-Login for authentication
- Werkzeug for WSGI utilities and security

## Environment Variables
- `SESSION_SECRET`: Secret key for session security
- `DATABASE_URL`: PostgreSQL database connection string

## Usage
This file serves as the application factory and is imported by `main.py` to start the web server.