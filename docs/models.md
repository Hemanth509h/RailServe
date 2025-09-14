# models.py - Database Models

## Overview
Defines all SQLAlchemy database models for the RailServe railway reservation system, implementing a comprehensive data structure for train bookings, user management, and payment processing. This file contains all database table definitions and their relationships.

## File Location and Dependencies
- **Path**: `src/models.py`
- **Imports from**: `src/app.py` - uses the `db` SQLAlchemy instance and `Base` declarative class
- **Used by**: 
  - `main.py` - imports Train, Station, Booking models
  - `auth.py` - imports User model for authentication
  - `admin.py` - imports all models for administrative operations
  - `booking.py` - imports Train, Station, Booking, Waitlist models
  - `payment.py` - imports Payment and Booking models
  - `utils.py` - imports models for utility functions
  - `populate_database.py` - imports all models for data population

## Database Schema Architecture

### Model Inheritance Structure
```python
from src.app import db, Base

class ModelName(Base):
    __tablename__ = 'table_name'
    # Model definition
```
- **Base Class**: Inherits from `Base` defined in `app.py`
- **SQLAlchemy Integration**: Uses `db` instance from `app.py`
- **Table Creation**: Automatically creates tables via `app.py` initialization

## Database Models

### User Model
- **Purpose**: User account management with role-based access control
- **Roles**: Three-tier system (user, admin, super_admin)
- **Fields**: Username, email, password hash, role, active status, creation timestamp
- **Relationships**: One-to-many with Booking and Payment models
- **Authentication**: Integrates with Flask-Login for session management

### Train Model
- **Purpose**: Train information and service management
- **Fields**: Train number, name, source/destination stations, departure/arrival times
- **Capacity**: Total seats, available seats, fare per kilometer
- **Status**: Active status for operational control
- **Relationships**: One-to-many with Booking, TrainRoute, and Waitlist models

### Station Model
- **Purpose**: Railway station information and network management
- **Fields**: Station code, name, city, state
- **Status**: Active status for operational control
- **Relationships**: Referenced by TrainRoute for train paths

### Booking Model
- **Purpose**: Core booking system with ticket management
- **Fields**: User, train, journey details, passenger count, total amount
- **Status**: Booking status (pending_payment, confirmed, waitlisted, cancelled, completed)
- **PNR**: Auto-generated unique booking reference number
- **Relationships**: Links users, trains, stations, and payments

### Payment Model
- **Purpose**: Payment processing and transaction management
- **Fields**: Booking reference, amount, transaction ID, payment method
- **Status**: Payment status (pending, success, failed)
- **Relationships**: One-to-one with Booking model

### TrainRoute Model
- **Purpose**: Defines train paths and station sequences
- **Fields**: Train, station, sequence order, distance from start
- **Purpose**: Enables route validation and fare calculation
- **Relationships**: Links trains and stations with ordering

### Waitlist Model
- **Purpose**: Queue-based waitlist management system
- **Fields**: Booking reference, train, journey date, queue position
- **Status**: Waitlist status (active, confirmed, cancelled)
- **FIFO**: First-in-first-out queue implementation

## Key Features

### Auto-Generation
- **PNR Numbers**: Automatic generation for booking references
- **Timestamps**: Created/updated timestamps for audit trails
- **Unique Constraints**: Enforced uniqueness for critical fields

### Relationships
- **Foreign Keys**: Proper referential integrity across models
- **Backref**: Bi-directional relationships for easy navigation
- **Cascade**: Appropriate cascade rules for data consistency

### Role-Based Access
- **User Roles**: Hierarchical permission system
- **Admin Methods**: Built-in methods for role checking
- **Security**: Active status controls for user access

## Database Schema
The models implement a normalized relational database schema optimized for railway operations, supporting concurrent bookings, waitlist management, and comprehensive reporting.