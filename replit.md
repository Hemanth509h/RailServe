# RailServe - Modern Railway Reservation System

## Overview

RailServe is a comprehensive railway ticket booking system built with Flask and **Supabase PostgreSQL**. The system provides **1,000 real Indian railway stations**, **1,250 authentic trains** (including Rajdhani, Shatabdi, Duronto Express), advanced booking management, Tatkal (last-minute) booking support, waitlist management, and administrative analytics.

## User Preferences

Preferred communication style: Simple, everyday language.

## Current Status (November 2025)

**Architecture:** Monolithic Flask application with Supabase PostgreSQL database
**Database:** Supabase PostgreSQL (managed, scalable, IPv4-compatible Session Pooler)
**Deployment:** Configured for Vercel Serverless
**Team:** 6 members (3 frontend, 3 backend) - see `docs/TEAM_ASSIGNMENT.md`

**Migration Complete:**
- ✅ Migrated from SQLite to Supabase PostgreSQL
- ✅ Removed database-api microservice (simplified to monolith)
- ✅ All core documentation rewritten and consolidated in `docs/` folder
- ✅ Team documentation created (assignments, onboarding, file guide)
- ✅ Visual diagrams (mind maps, flowcharts) created
- ✅ Vercel deployment configured

**Database Initialization:**
- Run `python init_supabase.py` to populate database with:
  - 1,000 Indian railway stations (Mumbai, Delhi, Chennai, Bangalore, etc.)
  - 1,250 trains (Rajdhani, Shatabdi, Duronto, Mail/Express, Passenger)
  - 12,479 route stops (average 10 stops per train)
  - Admin user (username: `admin`, password: `admin123`)
  - Tatkal time slots (AC: 10:00 AM, Non-AC: 11:00 AM)

## System Architecture

### Technology Stack

**Backend:**
- Flask 3.1+ (Python 3.11+)
- SQLAlchemy 2.0+ (ORM)
- psycopg2-binary 2.9+ (PostgreSQL driver)
- Gunicorn 23.0+ (production WSGI server)

**Database:**
- Supabase PostgreSQL (managed)
- Session Pooler (IPv4-compatible for Vercel)
- Automatic backups and scaling
- Connection via `DATABASE_URL` environment variable

**Frontend:**
- Jinja2 templates
- HTML5/CSS3 (responsive, mobile-first)
- JavaScript (vanilla, inline)
- Dual theme (light/dark) with localStorage

**Document Generation:**
- ReportLab (PDF tickets)
- qrcode[pil] (QR code verification)

**Deployment:**
- Vercel Serverless (autoscale)
- Environment variables managed via Vercel dashboard

### Application Structure

```
Entry Point: main.py
│
├── Blueprints (Modular Routes)
│   ├── main.py - Homepage, search, PNR enquiry
│   ├── src/auth.py - Authentication (login, register, logout)
│   ├── src/booking.py - Booking flow and management
│   ├── src/payment.py - Payment processing
│   ├── src/admin.py - Admin dashboard and controls
│   └── src/pdf_routes.py - PDF ticket generation
│
├── Business Logic
│   ├── src/seat_allocation.py - Seat assignment algorithm
│   ├── src/queue_manager.py - Waitlist management (FIFO)
│   ├── src/route_graph.py - Route validation
│   ├── src/utils.py - Helper functions (PNR gen, fare calc)
│   └── src/pdf_generator.py - PDF ticket creation
│
├── Data Layer
│   ├── src/models.py - SQLAlchemy models (18 tables)
│   ├── src/database.py - Database connection
│   └── init_supabase.py - Database initialization script
│
└── Templates (Jinja2)
    ├── base.html - Master template (nav, footer, themes)
    ├── index.html - Homepage
    ├── book_ticket.html - Booking form
    ├── admin/ - Admin panel templates
    └── 100+ other templates
```

### Database Schema (18 Tables)

**Core Tables:**
- `user` - Authentication with roles (user, admin, super_admin)
- `station` - 1,000 Indian railway stations
- `train` - 1,250 trains with fare information
- `train_route` - 12,479 route stops (graph structure)

**Booking Tables:**
- `booking` - Ticket reservations with PNR
- `passenger` - Individual passenger details
- `payment` - Transaction records
- `seat_availability` - Real-time seat tracking
- `waitlist` - Queue management (GNWL, RAC, PQWL, RLWL, TQWL)

**Feature Tables:**
- `tatkal_time_slot` - Tatkal booking windows
- `tatkal_override` - Admin overrides
- `dynamic_pricing` - Surge pricing rules
- `refund_request` - Cancellation processing
- `complaint_management` - Support tickets

**Analytics Tables:**
- `performance_metrics` - Train KPIs (on-time %, load factor)
- `loyalty_program` - User rewards
- `chart_preparation` - Chart preparation tracking
- `platform_management` - Platform allocation

**See `docs/DATABASE_SCHEMA.md` for complete schema.**

### Security Architecture

**Authentication:**
- Password hashing (PBKDF2 via Werkzeug)
- Session management (Flask-Login)
- HTTPOnly cookies (XSS protection)
- Role-based access control

**Authorization:**
- Decorators: `@login_required`, `@admin_required`, `@super_admin_required`
- Route protection
- Template-level access control

**Input Validation:**
- CSRF protection (Flask-WTF)
- Email validation (email-validator)
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (Jinja2 auto-escaping)

**Data Protection:**
- Environment variables for secrets
- Encrypted database connections
- Secure cookies (SameSite)

## External Dependencies

### Database (Required)
- **Supabase PostgreSQL** - Managed PostgreSQL database
- **Connection:** Via `DATABASE_URL` environment variable
- **Format:** `postgresql://postgres.[PROJECT-ID]:[PASSWORD]@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres`
- **No Fallback:** Application requires DATABASE_URL to start

### Python Packages

**Flask Ecosystem:**
- `flask` 3.1+ - Web framework
- `flask-login` - User session management
- `flask-sqlalchemy` - ORM integration
- `flask-wtf` - CSRF protection and forms

**Database:**
- `sqlalchemy` 2.0+ - ORM
- `psycopg2-binary` - PostgreSQL adapter

**Document Generation:**
- `reportlab` - PDF generation
- `qrcode[pil]` - QR codes
- `pillow` - Image processing

**Utilities:**
- `faker` - Test data generation (Indian locale)
- `email-validator` - Email validation
- `python-dotenv` - Environment variable loading
- `requests` - HTTP client

**Server:**
- `gunicorn` - Production WSGI server

### Email Service (Optional)
- SMTP configuration for password reset and confirmations
- Demo mode when SMTP not configured (logs emails)
- Environment variables: `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`

### Environment Variables

**Required:**
- `DATABASE_URL` - Supabase PostgreSQL connection string

**Recommended:**
- `SESSION_SECRET` - Flask session encryption key (auto-generated in dev)
- `FLASK_ENV` - Set to `production` for Vercel

**Optional:**
- SMTP configuration for email functionality

## Initialization & Setup

### Database Initialization Script: `init_supabase.py`

**Populates Supabase with:**

1. **1,000 Indian Railway Stations**
   - Major stations: Mumbai Central, Delhi, Chennai, Bangalore, Kolkata, etc.
   - Real station codes (e.g., BCT, NDLS, MAS, SBC, HWH)
   - City and state information
   - All marked as active

2. **1,250 Trains with Authentic Types**
   - **Rajdhani Express** (~150 trains)
     - Base fare: ₹2.20/km
     - Tatkal multiplier: 1.3x
     - Total seats: 400
   - **Shatabdi Express** (~200 trains)
     - Base fare: ₹2.80/km
     - Tatkal multiplier: 1.3x
     - Total seats: 500
   - **Duronto Express** (~100 trains)
     - Base fare: ₹1.75/km
     - Tatkal multiplier: 1.3x
     - Total seats: 600
   - **Garib Rath** (~100 trains)
     - Base fare: ₹1.20/km
     - Tatkal multiplier: 1.2x
     - Total seats: 700
   - **Humsafar Express** (~80 trains)
     - Base fare: ₹1.60/km
     - Tatkal multiplier: 1.25x
     - Total seats: 450
   - **Vande Bharat** (~20 trains)
     - Base fare: ₹3.50/km
     - Tatkal multiplier: 1.4x
     - Total seats: 400
   - **Tejas Express** (~30 trains)
     - Base fare: ₹3.00/km
     - Tatkal multiplier: 1.35x
     - Total seats: 400
   - **Mail/Express** (~300 trains)
     - Base fare: ₹0.60/km
     - Tatkal multiplier: 1.3x
     - Total seats: 1000
   - **Superfast** (~200 trains)
     - Base fare: ₹0.80/km
     - Tatkal multiplier: 1.3x
     - Total seats: 900
   - **Passenger** (~70 trains)
     - Base fare: ₹0.30/km
     - Tatkal multiplier: 1.1x
     - Total seats: 800

3. **12,479 Route Stops**
   - Average 10 stops per train
   - Realistic multi-city routes
   - Distance calculations
   - Arrival/departure times

4. **Admin User**
   - Username: `admin`
   - Password: `admin123`
   - Role: super_admin
   - **⚠️ Change in production!**

5. **Tatkal Time Slots**
   - AC classes: 10:00 AM (1 day before journey)
   - Non-AC classes: 11:00 AM (1 day before journey)

**Usage:**
```bash
# Make sure DATABASE_URL is set
export DATABASE_URL="your-supabase-connection-string"

# Run initialization
python init_supabase.py
```

**Output:**
```
======================================================================
                  ✓ Initialization Complete!
======================================================================

📊 Database Summary:
  • Stations: 1,000 (including major Indian railway stations)
  • Trains: 1,250 (Rajdhani, Shatabdi, Duronto, etc.)
  • Train Routes: 12,479 route stops (avg 10.0 per train)
  • Seat Availability: Calculated dynamically

🔐 Admin Login:
  • Username: admin
  • Password: admin123
```

## Key Business Logic Modules

### Booking System
**Files:** `src/booking.py`, `src/utils.py`
- Multi-step booking flow (search → select → details → payment)
- Real-time seat availability across route segments
- Tatkal booking with time-window validation
- Automatic waitlist when seats unavailable
- Group booking coordination

### Seat Allocation
**File:** `src/seat_allocation.py`
- Algorithm assigns seats based on preferences
- Coach and berth type coordination
- Seat number generation (e.g., "S1-45", "B2-32")
- Preference handling (Lower, Middle, Upper, Side Lower, Side Upper)

### Waitlist Management
**File:** `src/queue_manager.py`
- FIFO queue implementation
- Auto-confirmation when seats become available
- Waitlist types: GNWL, RAC, PQWL, RLWL, TQWL
- Status tracking and position updates
- Email notifications on confirmation

### Route Validation
**File:** `src/route_graph.py`
- Directed graph of train routes
- Station validation for bookings
- Distance calculation between stations
- Multi-segment route handling

### Tatkal Management
**File:** `src/admin.py`
- Time window enforcement (10 AM AC, 11 AM Non-AC)
- Premium fare calculation (1.1x - 1.4x multipliers)
- Quota management
- Admin override capabilities

### Dynamic Pricing
**File:** `src/admin.py`
- Surge multipliers based on demand
- Special event pricing
- Per-train and per-date rules
- Revenue optimization

### PDF Generation
**File:** `src/pdf_generator.py`
- Professional ticket layout (ReportLab)
- QR code embedding for verification
- Passenger, train, and seat details
- Journey information

## Administrative System

### Access Levels
1. **User** - Book tickets, view history, manage profile
2. **Admin** - Booking reports, complaints, basic train management
3. **Super Admin** - All features + user management, system configuration

### Admin Features
- Real-time analytics dashboard (revenue, bookings, users)
- Train and station CRUD operations
- Route configuration
- Booking reports with CSV export
- Dynamic pricing configuration
- Tatkal time slot management
- Platform allocation
- Refund request processing
- Complaint/ticket system
- Performance metrics and KPI monitoring
- Emergency quota release

## Team Structure (6 Members)

**Frontend Team (3 members):**
- Member 1: Landing page, search, PNR enquiry
- Member 2: Booking flow, payments, user profile
- Member 3: Admin dashboard and reports

**Backend Team (3 members):**
- Member 1: Authentication and user management
- Member 2: Booking engine, seat allocation, payments
- Member 3: Data management, routes, pricing, admin logic

**See `docs/TEAM_ASSIGNMENT.md` for detailed file assignments.**

## Documentation

All documentation is consolidated in the `docs/` folder:

**Getting Started:**
- `README.md` (root) - Quick overview
- `docs/DEVELOPER_ONBOARDING.md` - Setup guide
- `docs/TEAM_ASSIGNMENT.md` - Team roles and files

**Technical:**
- `docs/ARCHITECTURE.md` - System architecture
- `docs/DATABASE_SCHEMA.md` - Database tables
- `docs/FILE_STRUCTURE_GUIDE.md` - File reference
- `docs/DEPLOYMENT_GUIDE.md` - Vercel deployment

**Visual:**
- `docs/SYSTEM_MINDMAP.md` - Visual overview
- `docs/BOOKING_FLOWCHART.md` - Process flows

**Navigation:**
- `docs/INDEX.md` - Complete documentation index

## Deployment (Vercel)

**Configuration:**
- `vercel.json` - Deployment settings
- Serverless function (autoscale)
- Environment variables via Vercel dashboard

**Deploy:**
```bash
vercel
```

**Environment Variables (Vercel Dashboard):**
- `DATABASE_URL` - Supabase connection string
- `SESSION_SECRET` - Random secret key
- `FLASK_ENV` - Set to `production`

## Development Workflow

**Branch Strategy:**
- `main` - Production
- `dev` - Development
- Feature branches: `frontend/<feature>`, `backend/<feature>`

**Workflow:**
1. Branch from `dev`
2. Make changes
3. Test locally (`python main.py`)
4. Create pull request to `dev`
5. Request review
6. Merge after approval

**See `docs/DEVELOPER_ONBOARDING.md` for detailed workflow.**

## Recent Changes (November 2025)

✅ **Migration to Supabase PostgreSQL**
- Removed SQLite and database-api microservice
- Simplified to monolithic architecture
- All database operations via SQLAlchemy ORM

✅ **Documentation Overhaul**
- All docs consolidated in `docs/` folder
- Created team assignment guide (6 members)
- Added visual diagrams (mind maps, flowcharts)
- Comprehensive file structure guide
- Developer onboarding documentation

✅ **Database Population**
- 1,000 real Indian railway stations
- 1,250 trains with authentic types and pricing
- 12,479 route stops with realistic routes
- Admin user setup

✅ **Vercel Deployment Ready**
- `vercel.json` configured
- Environment variable management
- Production-ready settings

## Design Decisions

### Monolithic vs Microservices
**Chose:** Monolithic Flask application

**Rationale:**
- Team size (6 members) suits monolith
- Simpler deployment and debugging
- Shared database transactions
- Lower operational complexity

### Supabase vs Self-Hosted PostgreSQL
**Chose:** Supabase PostgreSQL

**Rationale:**
- Managed service (no database admin)
- Built-in connection pooling (Session Pooler)
- IPv4 compatibility with Vercel
- Free tier sufficient for development
- Automatic backups and scaling

### Inline CSS/JS vs External Files
**Chose:** Inline assets in `base.html`

**Rationale:**
- Simplified Vercel deployment (no static file serving)
- Faster page loads (no additional HTTP requests)
- Easier to maintain (single template file)
- No CDN or build step required

### Real Data vs Mock Data
**Chose:** Real Indian Railway data

**Rationale:**
- Production-ready from day one
- Realistic user experience
- No need to replace later
- Authentic testing scenarios

## Key Files

**Entry Point:**
- `main.py` - Application starts here

**Database:**
- `init_supabase.py` - Initialize and populate database
- `src/models.py` - SQLAlchemy models (18 tables)
- `src/database.py` - Database connection

**Blueprints:**
- `src/auth.py` - Authentication
- `src/booking.py` - Booking flow
- `src/payment.py` - Payment processing
- `src/admin.py` - Admin panel
- `src/pdf_routes.py` - PDF generation

**Business Logic:**
- `src/seat_allocation.py` - Seat assignment
- `src/queue_manager.py` - Waitlist management
- `src/route_graph.py` - Route validation
- `src/utils.py` - Helper functions

**Configuration:**
- `vercel.json` - Deployment config
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (local, gitignored)

**Documentation:**
- `docs/` - All documentation files
- `README.md` - Project overview

## Running Locally

```bash
# 1. Clone repository
git clone <repository-url>
cd railserve

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set DATABASE_URL
export DATABASE_URL="postgresql://postgres.[PROJECT-ID]:[PASSWORD]@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres"

# 4. Initialize database
python init_supabase.py

# 5. Run server
python main.py

# Access at http://localhost:5000
# Admin: admin/admin123
```

## Production Deployment

**Vercel:**
1. Connect GitHub repository to Vercel
2. Set environment variables in Vercel dashboard:
   - `DATABASE_URL`
   - `SESSION_SECRET`
   - `FLASK_ENV=production`
3. Deploy: `vercel --prod`
4. Access via Vercel URL

**Post-Deployment:**
1. Change admin password
2. Configure custom domain (optional)
3. Set up monitoring
4. Test all features

## Troubleshooting

**Database Connection Errors:**
- Verify `DATABASE_URL` is set correctly
- Check Supabase project is active
- Ensure Session Pooler URL is used (not Direct Connection)

**Tables Don't Exist:**
- Run `python init_supabase.py`
- Check console output for errors

**Import Errors:**
- Run `pip install -r requirements.txt`
- Verify Python 3.11+ is installed

**Template Not Found:**
- Check file exists in `templates/` folder
- Verify correct path in route

**Admin Can't Login:**
- Run `python init_supabase.py` to create admin user
- Username: `admin`, Password: `admin123`

---

**Last Updated:** November 2025  
**Version:** 2.0 (Supabase PostgreSQL)  
**Team:** 6 members (3 frontend, 3 backend)  
**Status:** Ready for Vercel deployment
