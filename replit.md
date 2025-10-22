# RailServe - Railway Reservation System

## Overview

RailServe is a comprehensive, modern railway reservation system built with Flask and designed for production use. The system provides complete booking functionality with enterprise-grade security, real-time seat allocation, and advanced administrative controls. It includes features like Tatkal booking, waitlist management, and TDR (Ticket Deposit Receipt) system. The platform is designed to handle large-scale railway operations with intelligent seat allocation, automated chart preparation, and comprehensive reporting capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Technology Stack**: HTML5, CSS3, JavaScript (ES6+) with progressive enhancement
- **Design Philosophy**: Mobile-first responsive design with WCAG 2.1 accessibility compliance
- **Styling**: Modular CSS architecture with theme support and component-based styling
- **User Experience**: Sub-2 second load times with optimized asset delivery and interactive elements

### Backend Architecture
- **Framework**: Python Flask 3.1.2 with Blueprint-based modular architecture
- **Database ORM**: SQLAlchemy 2.0+ with advanced relationship mapping and connection pooling
- **Authentication**: Flask-Login with Werkzeug password hashing and role-based access control
- **Security**: CSRF protection, secure session management, and multi-layered security implementation
- **API Design**: RESTful endpoints with consistent error handling and response formatting

### Database Design
- **Primary Database**: PostgreSQL with advanced indexing and query optimization
- **Schema**: Comprehensive entity-relationship model covering users, trains, stations, bookings, payments, and administrative functions
- **Key Entities**: User (with role-based access), Train/Station management, Booking workflow, Payment processing, Waitlist management, and TDR system
- **Data Integrity**: Foreign key constraints, transaction management, and automated backup mechanisms

### Core System Components

#### Booking Engine
- **Seat Allocation**: Intelligent seat assignment with preference-based allocation
- **Waitlist Management**: FIFO queue system with automatic confirmation processing
- **Tatkal System**: Time-based premium booking with specialized availability windows

#### Payment Processing
- **Multiple Methods**: Support for card, UPI, and net banking payments
- **Transaction Management**: Secure transaction handling with status tracking
- **Refund System**: TDR-based refund processing with automated charge calculations

#### Administrative System
- **Dashboard**: Real-time metrics, booking analytics, and revenue reporting
- **Train Management**: Complete CRUD operations for trains, routes, and schedules
- **User Administration**: Role-based user management with activity tracking
- **Chart Preparation**: Automated railway chart generation with manual override capabilities

### Security Architecture
- **Authentication**: Multi-factor authentication support with secure password policies
- **Authorization**: Role-based access control (user, admin, super_admin)
- **Data Protection**: CSRF protection, secure session management, and input validation
- **Anti-Bot Measures**: Captcha integration for Tatkal bookings and sensitive operations

### Performance Optimization
- **Database**: Connection pooling and query optimization for concurrent users
- **Caching**: Strategic caching for frequently accessed data
- **Scalability**: Architecture designed for horizontal scaling with read replicas
- **Load Handling**: Optimized for high-volume concurrent booking operations

## External Dependencies

### Core Framework Dependencies
- **Flask 3.1.2**: Web application framework with Blueprint support
- **SQLAlchemy 2.0+**: Database ORM with advanced relationship mapping
- **Flask-Login 0.6.3**: User session management and authentication
- **Flask-WTF 1.2.2**: Form handling with CSRF protection
- **Werkzeug 3.1.3**: Security utilities and password hashing

### Database Connectivity
- **psycopg2-binary 2.9.10**: PostgreSQL database adapter
- **SQLite**: Fallback database support for development environments

### Additional Functionality
- **email-validator**: Email address validation for user registration
- **Faker 37.8.0**: Test data generation for development and testing
- **ReportLab 4.4.4**: PDF generation for tickets and reports
- **QRCode[PIL] 8.2**: QR code generation for tickets and verification
- **Gunicorn 23.0.0**: Production WSGI server for deployment

### Development and Testing
- **Environment Variables**: Configuration management for database connections and API keys
- **CSRF Protection**: Built-in security for form submissions
- **Session Management**: Secure cookie-based sessions with configurable timeouts

### Third-Party Service Integration
- **Email Services**: SMTP integration for notifications and password reset functionality
- **Payment Gateways**: Framework prepared for integration with payment processors
- **SMS Services**: Infrastructure ready for SMS notifications and OTP verification
- **Cloud Storage**: Architecture supports integration with cloud storage for document management

## Recent Changes

### October 22, 2025 - Group Booking Features Removed
- **Simplified System**: Removed all group booking features to streamline the application
- **Database Cleanup**: Removed GroupBooking, GroupMemberInvitation, GroupMemberPayment, and GroupMessage models
- **Modern Group System**: Deleted src/modern_group_models.py and all associated modern group functionality
- **Blueprint Cleanup**: Removed groups blueprint from application registration
- **Template Cleanup**: Deleted templates/modern_groups/ folder
- **Setup Script**: Rewrote setup_database.py without any group booking functionality
- **Focus**: Application now focuses on core individual booking features

### September 27, 2025 - Complete Replit Environment Setup
- **Project Import**: Successfully imported RailServe from GitHub to Replit environment
- **Dependencies**: Installed all Python dependencies using packager tool (Flask, SQLAlchemy, etc.)
- **Database Setup**: Created PostgreSQL database, configured environment variables, and initialized all tables with sample data
- **Flask Configuration**: Updated Flask app configuration for Replit proxy environment with proper host settings
- **Workflow Configuration**: Set up Railway Web Application workflow on port 5000 with webview output
- **CSRF Fix**: Resolved CSRF token issues in tatkal override admin functionality
- **Database Population**: Successfully created 52 stations, 20 trains, 88 route entries, and admin accounts
- **Deployment Configuration**: Configured autoscale deployment with Gunicorn WSGI server for production
- **Testing**: Verified application functionality including homepage, navigation, search functionality, and admin features
- **Environment Ready**: Application is fully functional in Replit environment with proper proxy configuration, database connectivity, and deployment setup

### Application Access
- **Development Server**: Running on port 5000 with Flask debug mode
- **Admin Access**: Username: admin, Password: admin123
- **Test User**: Username: testuser, Password: user123
- **Database**: PostgreSQL with comprehensive railway data (25 stations, 16 trains)