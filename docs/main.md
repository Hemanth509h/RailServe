# main.py - Application Entry Point

## Overview
The main entry point and route handler for the RailServe application, providing core user-facing functionality including homepage, train search, and PNR enquiry services. This file imports the Flask app from `src/app.py` and defines the primary public routes that users interact with.

## File Location and Dependencies
- **Path**: `main.py` (root directory)
- **Primary Import**: `from src.app import app` - imports the configured Flask application
- **Connects to**: 
  - `src/app.py` - imports the main Flask app instance
  - `src/models.py` - imports Train, Station, Booking models for data operations
  - `src/utils.py` - imports utility functions like `get_running_trains()`, `search_trains()`
  - `templates/` - renders HTML templates for user interface

## Code Structure and Implementation

### Key Imports
```python
from src.app import app
from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from src.models import Train, Station, Booking
from src.utils import get_running_trains, search_trains
from datetime import datetime
```

### Integration with Other Files
- **app.py**: Gets the configured Flask application instance
- **models.py**: Uses Train, Station, Booking models for database queries
- **utils.py**: Leverages utility functions for business logic
- **templates/**: Renders HTML templates for user interface
- **auth.py**: Uses Flask-Login decorators and user authentication

## Core Routes and Implementation

### Homepage Route (`/`)
```python
@app.route('/')
def index():
    running_trains = get_running_trains()  # from utils.py
    stations = Station.query.all()         # from models.py
    return render_template('index.html', trains=running_trains, stations=stations)
```
- **Purpose**: Main landing page displaying available trains and search interface
- **Data Flow**:
  - Calls `get_running_trains()` from `utils.py` to get active trains
  - Queries `Station` model from `models.py` to get all stations
  - Renders `templates/index.html` with train and station data
- **Template Connection**: Uses `templates/index.html` for the user interface
- **Features**:
  - Live display of running trains
  - Station dropdown for search functionality
  - Quick access to booking services

### Train Search Route (`/search_trains`)
- **Method**: POST
- **Purpose**: Processes train search requests between stations
- **Validation**:
  - Ensures all search fields are populated
  - Prevents same source and destination selection
  - Validates station selection from available options
- **Search Algorithm**:
  - Uses utility functions for train discovery
  - Filters trains based on route availability
  - Returns relevant trains for specified journey
- **Response**: Renders homepage with search results

### PNR Enquiry Route (`/pnr_enquiry`)
- **Methods**: GET, POST
- **Purpose**: Provides booking status lookup by PNR number
- **Features**:
  - PNR-based booking retrieval
  - Complete booking information display
  - Journey details and status
  - Payment and waitlist status
- **Security**: Public access for booking verification
- **Error Handling**: User-friendly messages for invalid PNRs

## Application Integration

### Blueprint Integration
- **Authentication**: Integrates with auth blueprint for user management
- **Booking System**: Links to booking blueprint for ticket reservations
- **Admin Interface**: Connects to admin blueprint for management
- **Payment Processing**: Integrates with payment blueprint for transactions

### Template Rendering
- **Base Template**: Uses consistent base template system
- **Dynamic Content**: Renders real-time data in templates
- **User Context**: Passes user authentication state to templates
- **Search State**: Maintains search parameters across requests

## Data Flow

### Homepage Data Flow
1. **Running Trains**: Fetches active trains from database
2. **Station List**: Retrieves all active stations for dropdowns
3. **Template Rendering**: Combines data for homepage display
4. **User Context**: Includes authentication state

### Search Processing Flow
1. **Form Validation**: Validates search parameters
2. **Train Discovery**: Uses search algorithms to find relevant trains
3. **Result Filtering**: Applies business rules to results
4. **Template Response**: Renders results with search context

### PNR Enquiry Flow
1. **PNR Input**: Receives PNR number from user
2. **Database Lookup**: Searches booking database
3. **Data Retrieval**: Fetches complete booking information
4. **Status Display**: Shows current booking and payment status

## Security Features

### Input Validation
- **Form Sanitization**: Validates all form inputs
- **SQL Injection Prevention**: Uses parameterized queries
- **XSS Protection**: Escapes user input in templates
- **CSRF Protection**: Implements cross-site request forgery protection

### Access Control
- **Public Routes**: Homepage and search are publicly accessible
- **PNR Privacy**: PNR enquiry shows booking data without authentication
- **Session Management**: Maintains user sessions across requests
- **Authentication Integration**: Seamless integration with login system

## Error Handling

### User-Friendly Messages
- **Search Errors**: Clear messages for invalid search parameters
- **PNR Errors**: Informative messages for invalid or not-found PNRs
- **System Errors**: Graceful handling of system failures
- **Validation Feedback**: Specific feedback for form validation errors

### Graceful Degradation
- **Database Unavailable**: Handles database connectivity issues
- **Service Failures**: Continues operation with reduced functionality
- **Error Recovery**: Provides alternative paths for users
- **Logging**: Comprehensive error logging for debugging

## Performance Considerations

### Database Optimization
- **Efficient Queries**: Optimized database queries for train and station data
- **Connection Pooling**: Leverages SQLAlchemy connection pooling
- **Index Usage**: Designed to use database indexes effectively
- **Query Caching**: Prepared for query result caching

### Response Optimization
- **Template Caching**: Efficient template rendering
- **Static Assets**: Optimized CSS and JavaScript loading
- **Compression**: Prepared for response compression
- **CDN Ready**: Structure supports content delivery networks

## Business Logic

### Search Intelligence
- **Route Validation**: Ensures trains actually serve requested routes
- **Date Filtering**: Filters trains based on operational schedules
- **Availability**: Considers seat availability in search results
- **Sorting**: Intelligent sorting of search results

### User Experience
- **Intuitive Interface**: Simple and user-friendly search interface
- **Quick Access**: Fast access to common operations
- **Mobile Responsive**: Optimized for mobile device usage
- **Accessibility**: Follows web accessibility guidelines

## Integration Points

### External Systems
- **Database Models**: Direct integration with all data models
- **Utility Functions**: Uses utility functions for business logic
- **Authentication System**: Integrates with Flask-Login
- **Session Management**: Uses Flask session management

### Frontend Integration
- **JavaScript**: Client-side enhancements for better UX
- **CSS Framework**: Responsive design with custom CSS
- **AJAX Support**: Prepared for asynchronous operations
- **Progressive Enhancement**: Works with and without JavaScript

## Development Features

### Debug Support
- **Development Mode**: Enhanced debugging in development
- **Error Pages**: Detailed error pages for development
- **Logging**: Comprehensive request and response logging
- **Hot Reload**: Supports development server hot reloading

### Testing Support
- **Test Routes**: Prepared for unit and integration testing
- **Mock Data**: Compatible with test data and mocking
- **Environment Separation**: Supports different environments
- **Coverage**: Designed for test coverage analysis

## Configuration

### Environment Variables
- **Debug Mode**: Configurable debug settings
- **Database URL**: Environment-based database configuration
- **Secret Keys**: Secure configuration management
- **Feature Flags**: Supports feature toggle configuration

### Application Settings
- **Server Configuration**: Host and port configuration
- **Session Settings**: Configurable session parameters
- **Security Settings**: Adjustable security parameters
- **Performance Settings**: Tunable performance parameters

## Usage as Entry Point

### Application Startup
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### Production Deployment
- **WSGI Compatibility**: Ready for production WSGI servers
- **Gunicorn Support**: Optimized for Gunicorn deployment
- **Docker Ready**: Compatible with containerized deployment
- **Cloud Deployment**: Prepared for cloud platform deployment

This main application file serves as the primary user interface for the RailServe system, providing essential functionality for train discovery, booking initiation, and status enquiry while maintaining security, performance, and user experience standards.