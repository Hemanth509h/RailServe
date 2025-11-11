# RailServe - Railway Reservation System

## Overview

RailServe is a comprehensive Indian railway ticket booking platform built with Flask and PostgreSQL. The system manages the complete booking lifecycle for 1,000+ real railway stations and 1,250+ trains across India. It provides enterprise-grade features including real-time seat allocation, Tatkal booking, dynamic pricing, waitlist management, refund processing, and administrative controls.

The platform is designed for production use with a modern web interface supporting both light and dark themes, responsive design for mobile devices, and comprehensive user management with role-based access control.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture

**Web Framework**: Flask 3.1+ with Blueprint-based modular architecture
- Core application (`src/app.py`) handles initialization and middleware
- Modular blueprints for authentication, booking, payment, admin, and PDF generation
- Flask-Login for session management with secure cookie handling
- Flask-WTF with CSRF protection enabled
- ProxyFix middleware for deployment behind reverse proxies

**Database Layer**: PostgreSQL with SQLAlchemy 2.0+ ORM
- Connection pooling with pre-ping health checks and 300-second recycling
- Declarative base models with comprehensive relationships
- Support for Supabase-hosted PostgreSQL instances
- Connection string conversion from `postgresql://` to `postgresql+psycopg2://`

**Data Models** (17 core entities):
- **User Management**: User model with role-based access (user, admin, super_admin), password reset tokens
- **Railway Infrastructure**: Station, Train, TrainRoute models for network topology
- **Booking System**: Booking, Passenger, Payment models with PNR generation
- **Advanced Features**: Waitlist, RefundRequest, TatkalTimeSlot, TatkalOverride, DynamicPricing, SeatAvailability
- **Operations**: PlatformManagement, TrainPlatformAssignment, ComplaintManagement, PerformanceMetrics, PNRStatusTracking

**Authentication & Security**:
- Werkzeug password hashing with bcrypt
- Comprehensive input validation via centralized `FormValidator` class
- Username validation (3-50 chars, alphanumeric with underscore/hyphen/dot)
- Email validation using email-validator library
- Password requirements enforced (8-128 chars, mixed case, numbers, special chars)
- CSRF tokens on all state-changing forms
- Secure session cookies (HttpOnly, SameSite=Lax)
- Generic error messages to prevent user enumeration

**Business Logic Components**:

1. **Seat Allocation System** (`src/seat_allocation.py`): 
   - Automated seat/berth assignment for confirmed bookings
   - Coach-specific allocation (SL, AC1, AC2, AC3, 2S, CC)
   - Berth type assignment (Lower, Middle, Upper, Side Lower, Side Upper)
   - Group booking coordination for family travel

2. **Waitlist Queue Manager** (`src/queue_manager.py`):
   - FIFO queue-based waitlist using Python deque
   - Thread-safe operations with lock-based concurrency control
   - Automatic promotion from waitlist to confirmed on cancellations
   - Per-train, per-date queue management

3. **Route Graph System** (`src/route_graph.py`):
   - Graph-based train route modeling using adjacency lists
   - BFS pathfinding to validate station connectivity
   - Distance and timing calculations between stations

4. **Payment Processing**:
   - Simulated payment gateway with mock transaction IDs
   - Session-based pending booking management
   - Payment status tracking (success, failed, pending)
   - Atomic booking confirmation on successful payment

5. **Tatkal Booking System**:
   - Time-slot based booking windows (configurable per coach class)
   - Override mechanism for emergency access
   - Premium pricing with configurable multipliers
   - Separate quota management from general bookings

6. **Dynamic Pricing Engine**:
   - Demand-based fare adjustments
   - Surge pricing for peak seasons/events
   - Train-specific and class-specific multipliers
   - Integration with base fare calculations

7. **Refund Management**:
   - Automated cancellation charge calculation based on time to departure
   - Refund request workflow (pending, approved, rejected)
   - Partial refunds for multi-passenger bookings
   - TDR (Ticket Deposit Receipt) filing for service failures

### Frontend Architecture

**Template Engine**: Jinja2 with base template inheritance
- Base template (`templates/base.html`) provides global layout, navigation, theme switcher
- Page-specific templates extend base with block overrides
- Dark/light theme support via CSS custom properties and localStorage
- FOUC prevention with inline theme initialization script

**UI Design System**:
- Gradient-based modern design (purple/pink gradient backgrounds)
- Glassmorphism effects (backdrop-filter blur with transparency)
- Responsive breakpoints for mobile, tablet, desktop
- CSS custom properties for theming (--bg-primary, --text-primary, --accent-color)
- Font: Poppins from Google Fonts

**JavaScript Functionality**:
- Theme toggle with system preference detection
- Form validation (client-side pre-validation)
- Dynamic seat selection interface
- Real-time search filtering on admin pages
- AJAX-free design (traditional form submissions)

**Key User Interfaces**:
- Homepage with train search (from/to station, date selection)
- Search results with availability display
- Multi-step booking flow (passenger details → payment → confirmation)
- PNR enquiry with real-time status
- User profile with booking history
- PDF ticket download with QR codes

### Administrative System

**Admin Dashboard** (`src/admin.py`):
- Multi-level access control (admin, super_admin)
- Comprehensive analytics (bookings, revenue, user metrics)
- Train and station CRUD operations
- Route management with distance/timing configuration
- Tatkal time slot configuration
- Dynamic pricing rules management
- Platform assignment system
- Complaint resolution workflow
- Refund approval interface
- Emergency quota release
- Performance metrics monitoring

**Reporting & Analytics**:
- Booking reports with CSV export
- Revenue tracking by train, class, booking type
- On-time performance metrics
- Passenger load factor analysis
- Chart preparation for train departures

### Data Seeding & Initialization

**Database Setup** (`setup_supabase_database.py`):
- Automated schema creation from SQLAlchemy models
- Seed data population for 1,000+ stations (Indian railway codes)
- 1,250+ trains with realistic routes and schedules
- Pre-configured Tatkal time slots
- Admin user creation

### External Dependencies

**Database Services**:
- **Supabase PostgreSQL**: Primary data store hosted on AWS (pooler connection)
- Connection details configured via environment variables or hardcoded defaults
- Support for standard PostgreSQL instances

**Python Libraries**:
- **Flask Framework**: flask (3.1.2+), flask-login, flask-sqlalchemy, flask-wtf
- **Database**: psycopg2-binary (2.9.9+), sqlalchemy (2.0.43+)
- **Security**: werkzeug (3.1.3+), email-validator
- **PDF Generation**: reportlab (4.4.4+), qrcode[pil] (8.2+)
- **Data Generation**: faker (37.8.0+) for test data
- **Deployment**: gunicorn (23.0.0+) for production WSGI server
- **Utilities**: python-dotenv, requests, python-docx

**Email Service** (`src/email_service.py`):
- SMTP configuration for notifications (currently in demo mode)
- Password reset email functionality
- Booking confirmation emails (planned)
- Supports localhost SMTP or external providers

**PDF Generation** (`src/pdf_generator.py`):
- ReportLab-based ticket generation
- QR code integration for ticket verification
- Professional layout with railway branding
- Passenger details, journey information, terms & conditions

**API Client** (`src/api_client.py`):
- REST API client for potential external integrations
- Supports CRUD operations on users, stations, trains
- Session-based request handling
- Error handling with exception raising

### Configuration Management

**Environment Variables**:
- `DATABASE_URL`: PostgreSQL connection string (required)
- `SESSION_SECRET`: Flask session encryption key (fallback to hardcoded value)
- Database credentials: `user`, `password`, `host`, `port`, `dbname`

**Application Settings**:
- Session lifetime: 3600 seconds (1 hour)
- Cookie security: HttpOnly enabled, Secure in production, SameSite=Lax
- SQLAlchemy: pool pre-ping enabled, 300-second pool recycle
- CSRF protection enabled globally

### Deployment Considerations

**Production Settings**:
- Gunicorn WSGI server recommended
- Environment-based configuration (SESSION_COOKIE_SECURE based on flask_env)
- Database connection pooling for concurrent requests
- Static file serving (Flask serves from /static in development)
- Template compilation caching

**Security Features**:
- Password hashing with Werkzeug
- CSRF token validation on forms
- SQL injection prevention via SQLAlchemy ORM
- XSS prevention via Jinja2 auto-escaping
- Input sanitization in validators
- Secure session management

**Scalability Design**:
- Thread-safe waitlist manager with locks
- Database connection pooling
- Stateless request handling (session data in cookies/database)
- Blueprint modularization for horizontal scaling