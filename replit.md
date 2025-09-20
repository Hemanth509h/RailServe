# RailServe - Railway Reservation System

## Overview
RailServe is a comprehensive railway reservation system built with Flask and PostgreSQL. It provides a complete platform for railway ticket booking, management, and various related services.

## Recent Changes (September 20, 2025)
- Successfully imported and configured the project for Replit environment
- Fixed database setup script to handle duplicate station entries 
- Fixed decimal/float multiplication error in food ordering system
- Configured proper Flask application to run on port 5000 with webview
- Set up PostgreSQL database with comprehensive test data
- Configured deployment settings for production use

## Project Architecture

### Core Technologies
- **Backend**: Python Flask framework
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Flask-Login for user management
- **Frontend**: HTML templates with CSS/JavaScript
- **Static Assets**: Bootstrap, custom CSS and JavaScript

### Key Components
1. **Authentication System** (`src/auth.py`) - User registration, login, session management
2. **Booking System** (`src/booking.py`) - Train search, ticket booking, seat allocation
3. **Admin Panel** (`src/admin.py`) - Comprehensive admin dashboard and management
4. **Payment System** (`src/payment.py`) - Payment processing and transaction management
5. **Food Ordering** (`src/food.py`) - Restaurant integration and food delivery to trains
6. **PDF Generation** (`src/pdf_generator.py`, `src/pdf_routes.py`) - Ticket and document generation
7. **Group Bookings** (`src/groups.py`) - Family and corporate group booking management

### Database Schema
- **Users**: Authentication and profile management
- **Stations**: 1500+ railway stations across India
- **Trains**: 1000+ trains with routes and schedules
- **Bookings**: Comprehensive booking system with waitlist, tatkal, and quota management
- **Food System**: Restaurants, menus, and order management
- **Payment Tracking**: Complete payment and transaction history

### Features
- Real-time train search and booking
- Seat allocation and availability management
- Waitlist and RAC (Reservation Against Cancellation) handling
- Tatkal booking system with time slots
- Food ordering during journey
- Group bookings for families/corporate
- Admin dashboard with analytics
- PDF ticket generation with QR codes
- PNR status enquiry
- Loyalty program management

## Project Structure
```
/
├── src/                    # Main application source
│   ├── app.py             # Flask application setup
│   ├── models.py          # Database models
│   ├── auth.py            # Authentication blueprint
│   ├── booking.py         # Booking system
│   ├── admin.py           # Admin panel
│   ├── payment.py         # Payment processing
│   ├── food.py            # Food ordering
│   ├── groups.py          # Group bookings
│   ├── pdf_*.py           # PDF generation
│   └── utils.py           # Utility functions
├── templates/             # HTML templates
├── static/               # CSS, JS, and static assets
├── main.py              # Application entry point
├── setup_database.py    # Database initialization script
└── pyproject.toml       # Python dependencies
```

## Configuration
- **Port**: 5000 (configured for Replit environment)
- **Host**: 0.0.0.0 (allows external access)
- **Database**: PostgreSQL with connection pooling
- **Session Management**: Secure cookie-based sessions
- **CSRF**: Disabled per project requirements
- **Environment**: Development mode enabled with debug logging

## Deployment
- **Target**: Autoscale deployment for stateless web application
- **Production Server**: Gunicorn WSGI server
- **Database**: PostgreSQL with environment variable configuration
- **Static Files**: Served through Flask in development, external CDN recommended for production

## Database Setup
Run `python setup_database.py` to initialize the database with comprehensive test data including:
- Admin and test users
- 1500+ railway stations
- 1000+ trains with realistic routes
- Sample bookings and transactions
- Food restaurants and menus
- Complete system data for testing

## User Preferences
- Project follows Flask best practices
- Uses SQLAlchemy for database operations
- Implements proper error handling and logging
- Maintains security through environment variables
- Follows MVC architecture with blueprints