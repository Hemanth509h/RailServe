# RailServe - Modern Railway Reservation System

## Overview

RailServe is a comprehensive railway ticket booking system built with Flask that provides advanced booking management, dynamic pricing, Tatkal (last-minute) booking support, waitlist management, and administrative analytics. The system handles train schedules, seat allocation, payments, refunds, and real-time PNR tracking across 1250+ railway stations and 1500+ trains.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology Stack:** HTML5, CSS3, JavaScript, Jinja2 templating
- **Responsive Design:** Mobile-first approach with breakpoints at 480px, 768px, 992px, 1200px
- **Theming System:** Dual theme support (light/dark) with localStorage persistence and system preference detection
- **Design Pattern:** Modern gradient-based UI with glassmorphism effects and animations
- **Template Inheritance:** Base template (`base.html`) provides consistent navigation, footer, and theme support across all pages
- **Component Organization:** Separated CSS for animations and dark theme to maintain modularity

**Key Design Decisions:**
- Gradient backgrounds for visual appeal and modern aesthetics
- Glass-effect cards with backdrop blur for depth
- Inline critical CSS to prevent FOUC (Flash of Unstyled Content)
- Touch-optimized navigation for mobile devices

### Backend Architecture

**Framework:** Flask 3.1.2+ with Gunicorn WSGI server

**Application Structure:**
- **Entry Point:** `main.py` - Homepage, search, PNR enquiry, complaints
- **Modular Blueprints:**
  - `auth.py` - User authentication (login, register, password reset)
  - `booking.py` - Ticket booking flow and management
  - `payment.py` - Payment processing and confirmation
  - `admin.py` - Administrative dashboard and controls
  - `pdf_routes.py` - PDF ticket generation

**Key Architectural Decisions:**
- **Blueprint Pattern:** Separates concerns by feature area for maintainability
- **Decorator-based Authorization:** `@admin_required` and `@super_admin_required` decorators for role-based access control
- **Session-based Workflow:** Booking data stored in session during multi-step booking process before database commit

**Security Features:**
- CSRF protection via Flask-WTF
- Password hashing with Werkzeug
- Generic error messages to prevent user enumeration
- Environment-based configuration for secrets

### Data Architecture

**ORM:** SQLAlchemy 2.0.43+ with Flask-SQLAlchemy integration

**Database Schema Design:**

**Core Entities:**
- `User` - Authentication with role-based access (user, admin, super_admin)
- `Station` - Railway stations with city/state/code
- `Train` - Train information with routes and schedules
- `TrainRoute` - Graph-based route modeling with sequence ordering
- `Booking` - Ticket bookings with PNR, status, and relationships
- `Passenger` - Individual passenger details linked to bookings
- `Payment` - Payment transactions with status tracking

**Advanced Features:**
- `SeatAvailability` - Real-time seat tracking per coach class
- `Waitlist` - FIFO queue-based waitlist management
- `TatkalTimeSlot` - Time-windowed Tatkal (last-minute) booking rules
- `TatkalOverride` - Admin overrides for Tatkal restrictions
- `DynamicPricing` - Surge pricing and demand-based fare adjustments
- `RefundRequest` - Cancellation and refund processing
- `ComplaintManagement` - Customer support ticket system
- `PerformanceMetrics` - KPI tracking (on-time, load, revenue)

**Design Patterns:**
- **Graph-based Routing:** `RouteGraph` class uses adjacency list to model train routes and validate station sequences
- **Queue Manager:** `WaitlistManager` implements FIFO waitlist with automatic confirmation on seat availability
- **Seat Allocator:** `SeatAllocator` handles seat number assignment with berth type coordination
- **Concurrency Control:** Database-level locking for booking operations to prevent double-booking

### Business Logic Modules

**Booking System (`booking.py`, `utils.py`):**
- Multi-step booking flow: search → select → passenger details → payment
- Real-time seat availability checking across route segments
- Tatkal booking with time-window validation
- Automatic waitlist assignment when seats unavailable
- Group booking coordination with seat allocation

**Payment Processing (`payment.py`):**
- Session-based payment flow to handle payment gateway integration
- Payment status tracking (pending, success, failed)
- Automatic booking confirmation on successful payment
- Rollback mechanism for failed transactions

**PDF Generation (`pdf_generator.py`):**
- ReportLab-based ticket generation
- QR code integration for digital verification
- Professional ticket layout with train/passenger/journey details

**Dynamic Pricing (`src/admin.py`):**
- Surge multipliers based on demand
- Special event pricing
- Per-train and per-date pricing rules
- Admin controls for pricing adjustments

### Administrative System

**Multi-level Access Control:**
- Regular Admin: Booking reports, complaints, basic train management
- Super Admin: All admin features plus user management, system configuration

**Key Admin Features:**
- Real-time analytics dashboard with revenue, bookings, user metrics
- Tatkal management and override controls
- Dynamic pricing configuration
- Platform and route management
- Refund request processing
- Complaint/ticket system
- Performance metrics and KPI monitoring
- Emergency quota release

**Reporting & Analytics:**
- Booking reports with CSV export
- Revenue tracking by time period
- Train utilization metrics
- On-time performance monitoring

## External Dependencies

### Database
- **PostgreSQL** (production) - Configured via `DATABASE_URL` environment variable
- **SQLite** (development fallback) - Local file-based database at `local_railway.db`
- **Connection Strategy:** Validates DATABASE_URL format and tests connection, falls back to SQLite on failure

### Python Packages
- **Flask Ecosystem:**
  - `flask-login` - User session management
  - `flask-sqlalchemy` - ORM integration
  - `flask-wtf` - Form handling and CSRF protection
  
- **Database:**
  - `psycopg2-binary` - PostgreSQL adapter
  
- **Document Generation:**
  - `reportlab` - PDF generation
  - `qrcode[pil]` - QR code creation for tickets
  
- **Utilities:**
  - `faker` - Test data generation (used in `init_db.py`)
  - `email-validator` - Email format validation
  - `requests` - HTTP client for external API calls
  
- **Server:**
  - `gunicorn` - Production WSGI server with autoscale deployment

### Email Service (Optional)
- SMTP configuration via environment variables: `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`
- Demo mode when SMTP not configured (logs emails instead of sending)
- Used for password reset and booking confirmations

### Environment Variables
**Required:**
- `SESSION_SECRET` - Flask session encryption key (required in production)
- `DATABASE_URL` - Database connection string

**Optional:**
- `FLASK_ENV` - Environment mode (development/production)
- `ADMIN_PASSWORD` - Initial admin user password
- SMTP configuration variables for email functionality

### Initialization & Setup
- `init_db.py` - Database initialization script that populates 1250 stations, 1500 trains, routes, and sample admin user
- `setup_database.py` - Alternative initialization with 52 major stations and 20 popular trains
- Scripts use Faker library to generate realistic Indian railway data (cities, names, etc.)