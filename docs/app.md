# app.py - Flask Application Core

## Overview
The main Flask application configuration file that serves as the central hub for the RailServe railway reservation system. This file initializes the Flask web application, configures database connections, sets up authentication, and orchestrates the integration of all system components.

## File Location and Role
- **Path**: `src/app.py`
- **Purpose**: Application factory and configuration center
- **Dependencies**: Used by `main.py` as the primary Flask app instance
- **Connects to**: All blueprint files (`auth.py`, `admin.py`, `booking.py`, `payment.py`)

## Code Structure and Implementation

### Imports and Dependencies
```python
import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
```

### Core Components Initialization

#### Database Foundation
```python
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
```
- **DeclarativeBase**: Modern SQLAlchemy 2.0 pattern for model definitions
- **Global db instance**: Used throughout the application for database operations
- **Connected files**: `models.py` (defines all models), all blueprint files (database operations)

#### Authentication Setup
```python
login_manager = LoginManager()
```
- **Purpose**: Manages user sessions and authentication state
- **Integration**: Links with `auth.py` blueprint and `models.py` User model
- **User loader**: Connects to User model for session management

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