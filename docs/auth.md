# auth.py - Authentication Blueprint

## Overview
Handles user authentication, registration, and session management for the RailServe application using Flask-Login and secure password hashing.

## Routes and Functionality

### Login Route (`/login`)
- **Methods**: GET, POST
- **Purpose**: User authentication and session creation
- **Features**:
  - Username/password validation
  - Password hash verification using Werkzeug
  - Remember me functionality
  - Admin redirect logic
  - Next page redirection support
- **Security**: Active user verification and secure password checking

### Register Route (`/register`)
- **Methods**: GET, POST
- **Purpose**: New user account creation
- **Validation**:
  - All required fields presence
  - Password confirmation matching
  - Minimum password length (6 characters)
  - Username and email uniqueness
- **Security**: Password hashing before storage

### Logout Route (`/logout`)
- **Methods**: GET
- **Purpose**: User session termination
- **Requirements**: Login required
- **Functionality**: Clears user session and redirects to homepage

### Profile Route (`/profile`)
- **Methods**: GET
- **Purpose**: User dashboard with booking history
- **Requirements**: Login required
- **Features**:
  - Display user bookings
  - Show payment history
  - Personal account information

## Security Features

### Password Security
- **Hashing**: Uses Werkzeug's secure password hashing
- **Verification**: Constant-time password comparison
- **No Storage**: Plain text passwords never stored

### Session Management
- **Flask-Login**: Secure session handling
- **Remember Me**: Optional persistent sessions
- **Active Users**: Only active users can login

### Access Control
- **Login Required**: Protected routes require authentication
- **Admin Detection**: Automatic admin user redirection
- **Next Page**: Preserves intended destination after login

## Form Validation

### Input Sanitization
- **None Checking**: Prevents None value processing
- **Type Validation**: Ensures proper data types
- **Length Validation**: Enforces minimum password requirements

### User Feedback
- **Flash Messages**: User-friendly error and success messages
- **Error Handling**: Comprehensive validation feedback
- **Redirect Logic**: Proper page flow after operations

## Integration
- **User Model**: Direct integration with User database model
- **Main App**: Registered as blueprint with Flask application
- **Templates**: Uses Jinja2 templates for form rendering
- **Database**: Uses SQLAlchemy for user operations

## Blueprint Configuration
Registered as `auth_bp` blueprint, providing modular authentication functionality that can be easily integrated into the main Flask application.