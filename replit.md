# RailServe - Railway Reservation System

## Overview

RailServe is a comprehensive Flask-based railway reservation system designed to manage train bookings, payments, and user interactions. The system provides a three-tier user access model (User, Admin, Super Admin) with features including train search, ticket booking, waitlist management, payment processing, and administrative controls. The application uses custom HTML/CSS/JavaScript (without Bootstrap) and implements advanced features like queue-based waitlist management and graph-based route modeling.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework Architecture
- **Flask Application Structure**: Modular blueprint-based architecture with separate blueprints for authentication (`auth`), admin operations (`admin`), booking (`booking`), and payment (`payment`)
- **Template System**: Jinja2 templating with a base template system and component-based UI design
- **Static Assets**: Custom CSS and JavaScript implementation without external frameworks like Bootstrap

### Database Architecture
- **ORM**: SQLAlchemy with declarative base model for database operations
- **Connection Management**: PostgreSQL with connection pooling, automatic reconnection, and environment-based configuration
- **Data Models**: Core entities include User, Train, Station, Booking, Payment, TrainRoute, and Waitlist with proper relationships and constraints

### Authentication & Authorization
- **User Management**: Flask-Login integration with custom user loader and session management
- **Role-Based Access Control**: Three-tier system (User, Admin, Super Admin) with decorator-based route protection
- **Security**: Password hashing with Werkzeug security utilities and session-based authentication

### Business Logic Components
- **Queue Management System**: Custom FIFO queue implementation for waitlist management using Python's deque with thread-safe operations
- **Route Graph System**: Graph-based train route modeling using adjacency lists for pathfinding and route validation
- **Fare Calculation**: Distance-based fare calculation system with per-kilometer pricing
- **Seat Management**: Real-time seat availability tracking with automatic updates

### Payment Processing
- **Payment Workflow**: Simulated payment processing with transaction ID generation and status tracking
- **Payment States**: Support for success, failure, and pending payment states with proper error handling
- **Integration Ready**: Architecture designed for easy integration with real payment gateways

### Administrative Features
- **Analytics Dashboard**: Chart.js integration for revenue trends, booking distribution, and performance metrics
- **CRUD Operations**: Complete management interfaces for trains, stations, and users
- **Report Generation**: CSV export functionality for administrative reporting
- **User Management**: User blocking, role management, and activity monitoring

## External Dependencies

### Frontend Libraries
- **Chart.js**: Data visualization library for admin analytics and reporting dashboards
- **Font Awesome**: Icon library for consistent UI iconography across the application

### Python Packages
- **Flask**: Core web framework for application structure and routing
- **Flask-SQLAlchemy**: Database ORM and model management
- **Flask-Login**: User session management and authentication
- **Werkzeug**: Security utilities for password hashing and WSGI middleware
- **psycopg2**: PostgreSQL database adapter (implied by PostgreSQL usage)

### Database
- **PostgreSQL**: Primary database for persistent data storage with connection pooling and environment-based configuration

### Infrastructure
- **ProxyFix Middleware**: WSGI middleware for handling proxy headers in production environments
- **Environment Configuration**: Environment variable-based configuration for database URLs and secret keys

### Development Tools
- **Python Logging**: Built-in logging configuration for debugging and monitoring
- **Threading**: Thread-safe queue management for concurrent waitlist operations