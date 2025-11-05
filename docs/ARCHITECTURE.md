# RailServe System Architecture

Complete architectural overview of the RailServe railway reservation system built with Flask and Supabase PostgreSQL.

---

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture Diagram](#architecture-diagram)
4. [Application Layers](#application-layers)
5. [Database Design](#database-design)
6. [Security Architecture](#security-architecture)
7. [Deployment Architecture](#deployment-architecture)
8. [Data Flow](#data-flow)
9. [Key Design Decisions](#key-design-decisions)

---

## System Overview

RailServe is a monolithic Flask application with Supabase PostgreSQL database, designed for **team collaboration** with clear separation of concerns between frontend and backend responsibilities.

### Key Characteristics
- **Architecture Pattern:** Monolithic with Blueprint-based modularity
- **Database:** Supabase PostgreSQL (managed, scalable)
- **Deployment:** Vercel Serverless (autoscale)
- **Team Structure:** 6 members (3 frontend, 3 backend)
- **Scale:** 1,000 stations, 1,250 trains, 12,479 route stops

---

## Technology Stack

### Backend Framework
- **Flask 3.1+** - Python web framework
- **SQLAlchemy 2.0+** - ORM for database operations
- **psycopg2-binary 2.9+** - PostgreSQL adapter
- **Gunicorn 23.0+** - Production WSGI server

### Database
- **Supabase PostgreSQL** - Managed PostgreSQL database
- **Session Pooler** - IPv4-compatible connection pooling for Vercel
- **Transactions** - ACID compliance for booking operations
- **Indexes** - Optimized for search and availability queries

### Authentication & Security
- **Flask-Login 0.6+** - Session management
- **Flask-WTF 1.2+** - CSRF protection
- **Werkzeug 3.1+** - Password hashing (PBKDF2)
- **HTTPOnly Cookies** - XSS protection
- **SameSite Cookies** - CSRF protection

### Frontend
- **Jinja2** - Template engine
- **HTML5/CSS3** - Responsive, mobile-first design
- **JavaScript (Vanilla)** - Theme toggle, form validation
- **No External Assets** - All CSS/JS inline for simplified deployment

### Document Generation
- **ReportLab 4.4+** - PDF ticket generation
- **qrcode[pil] 8.2+** - QR code for ticket verification
- **Pillow** - Image processing

### Development Tools
- **Faker 37.8+** - Realistic test data (Indian locale)
- **email-validator 2.3+** - Email validation
- **python-dotenv 1.0+** - Environment variable management

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                             │
│                    (Desktop / Mobile)                           │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     VERCEL EDGE NETWORK                         │
│                  (CDN, SSL, DDoS Protection)                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FLASK APPLICATION (main.py)                    │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    PRESENTATION LAYER                      │ │
│  │                                                            │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │ │
│  │  │  Templates  │  │   Static    │  │  Error Handlers │  │ │
│  │  │  (Jinja2)   │  │  (Inline)   │  │   (404/500)     │  │ │
│  │  │             │  │             │  │                 │  │ │
│  │  │ • base.html │  │ • CSS       │  │ • Custom pages  │  │ │
│  │  │ • index     │  │ • JavaScript│  │ • Logging       │  │ │
│  │  │ • booking   │  │ • Themes    │  │                 │  │ │
│  │  │ • admin     │  │             │  │                 │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                     ROUTING LAYER                          │ │
│  │                                                            │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │ │
│  │  │   Main      │  │    Auth     │  │     Booking     │  │ │
│  │  │   Routes    │  │  Blueprint  │  │    Blueprint    │  │ │
│  │  │             │  │             │  │                 │  │ │
│  │  │ main.py     │  │ auth.py     │  │ booking.py      │  │ │
│  │  │ • /         │  │ • /login    │  │ • /book         │  │ │
│  │  │ • /search   │  │ • /register │  │ • /history      │  │ │
│  │  │ • /pnr      │  │ • /logout   │  │ • /cancel       │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │ │
│  │                                                            │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │ │
│  │  │   Payment   │  │    Admin    │  │       PDF       │  │ │
│  │  │  Blueprint  │  │  Blueprint  │  │    Blueprint    │  │ │
│  │  │             │  │             │  │                 │  │ │
│  │  │ payment.py  │  │ admin.py    │  │ pdf_routes.py   │  │ │
│  │  │ • /process  │  │ • /dashboard│  │ • /ticket/<id>  │  │ │
│  │  │ • /success  │  │ • /reports  │  │                 │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                   BUSINESS LOGIC LAYER                     │ │
│  │                                                            │ │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │ │
│  │  │   Booking   │  │     Seat     │  │    Waitlist    │  │ │
│  │  │   Manager   │  │  Allocation  │  │     Queue      │  │ │
│  │  │             │  │              │  │                │  │ │
│  │  │ • Search    │  │ • Algorithm  │  │ • FIFO         │  │ │
│  │  │ • Create    │  │ • Preferences│  │ • Auto-confirm │  │ │
│  │  │ • Cancel    │  │ • Coach/Berth│  │ • Status track │  │ │
│  │  └─────────────┘  └──────────────┘  └────────────────┘  │ │
│  │                                                            │ │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │ │
│  │  │    Route    │  │    Tatkal    │  │    Dynamic     │  │ │
│  │  │    Graph    │  │   Manager    │  │    Pricing     │  │ │
│  │  │             │  │              │  │                │  │ │
│  │  │ • Validate  │  │ • Time check │  │ • Surge rules  │  │ │
│  │  │ • Distance  │  │ • Quota      │  │ • Multipliers  │  │ │
│  │  │ • Paths     │  │ • Premium    │  │ • Events       │  │ │
│  │  └─────────────┘  └──────────────┘  └────────────────┘  │ │
│  │                                                            │ │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │ │
│  │  │     PDF     │  │    Email     │  │     Utils      │  │ │
│  │  │  Generator  │  │   Service    │  │   Functions    │  │ │
│  │  │             │  │              │  │                │  │ │
│  │  │ • Tickets   │  │ • SMTP       │  │ • PNR gen      │  │ │
│  │  │ • QR codes  │  │ • Reset pwd  │  │ • Fare calc    │  │ │
│  │  │ • Layout    │  │ • Confirm    │  │ • Helpers      │  │ │
│  │  └─────────────┘  └──────────────┘  └────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                   DATA ACCESS LAYER (ORM)                  │ │
│  │                                                            │ │
│  │                   SQLAlchemy Models (models.py)            │ │
│  │                                                            │ │
│  │  User │ Station │ Train │ TrainRoute │ Booking │          │ │
│  │  Passenger │ Payment │ Waitlist │ SeatAvailability        │ │
│  │  TatkalTimeSlot │ DynamicPricing │ RefundRequest          │ │
│  │  ComplaintManagement │ PerformanceMetrics                 │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│                          SQLAlchemy ORM                         │
│                               ▼                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │ psycopg2 (PostgreSQL Driver)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              SUPABASE POSTGRESQL DATABASE                       │
│                (Session Pooler - IPv4 Compatible)               │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                      DATA LAYER                            │ │
│  │                                                            │ │
│  │  📊 Tables (18 total):                                    │ │
│  │  • user (authentication)                                  │ │
│  │  • station (1,000 records)                                │ │
│  │  • train (1,250 records)                                  │ │
│  │  • train_route (12,479 records)                           │ │
│  │  • booking (dynamic)                                      │ │
│  │  • passenger (dynamic)                                    │ │
│  │  • payment (dynamic)                                      │ │
│  │  • waitlist (dynamic)                                     │ │
│  │  • seat_availability (calculated)                         │ │
│  │  • tatkal_time_slot (2 records)                           │ │
│  │  • dynamic_pricing (dynamic)                              │ │
│  │  • refund_request (dynamic)                               │ │
│  │  • complaint_management (dynamic)                         │ │
│  │  • performance_metrics (dynamic)                          │ │
│  │  + 4 more tables                                          │ │
│  │                                                            │ │
│  │  🔒 Constraints:                                          │ │
│  │  • Primary keys, foreign keys                             │ │
│  │  • Unique constraints (PNR, train numbers, codes)         │ │
│  │  • Check constraints (age > 0, seats >= 0)                │ │
│  │                                                            │ │
│  │  📈 Indexes:                                              │ │
│  │  • Station code, name                                     │ │
│  │  • Train number                                           │ │
│  │  • Booking PNR, user_id, status                           │ │
│  │  • Composite indexes for route queries                    │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Application Layers

### 1. Presentation Layer
**Responsibility:** User interface and user interaction

**Components:**
- **Templates:** Jinja2 HTML templates (100+ files)
- **Static Assets:** CSS and JavaScript (inline in `base.html`)
- **Error Handlers:** Custom 404, 500, 403 pages
- **Themes:** Light/dark mode with localStorage persistence

**Key Files:**
- `templates/base.html` - Master template
- `templates/index.html` - Homepage
- `templates/admin/dashboard.html` - Admin interface

---

### 2. Routing Layer (Flask Blueprints)
**Responsibility:** Request routing and HTTP handling

**Blueprints:**
1. **Main Routes** (`main.py`)
   - `/` - Homepage with train listings
   - `/search_trains` - Train search
   - `/pnr_enquiry` - PNR status
   - `/submit_complaint` - Customer support

2. **Auth Blueprint** (`src/auth.py`)
   - `/auth/register` - User registration
   - `/auth/login` - User login
   - `/auth/logout` - Session termination
   - `/auth/forgot_password` - Password reset

3. **Booking Blueprint** (`src/booking.py`)
   - `/booking/book/<train_id>` - Start booking
   - `/booking/seat_selection` - Seat assignment
   - `/booking/tatkal` - Tatkal booking
   - `/booking/history` - Booking history
   - `/booking/cancel/<id>` - Cancellation

4. **Payment Blueprint** (`src/payment.py`)
   - `/payment/process/<id>` - Payment initiation
   - `/payment/success` - Payment confirmation
   - `/payment/failure` - Payment error handling

5. **Admin Blueprint** (`src/admin.py`)
   - `/admin/` - Dashboard with analytics
   - `/admin/trains` - Train CRUD
   - `/admin/booking_reports` - Reports & CSV export
   - `/admin/dynamic_pricing` - Surge pricing
   - `/admin/tatkal_management` - Tatkal configuration
   - `/admin/complaints` - Support tickets

6. **PDF Blueprint** (`src/pdf_routes.py`)
   - `/pdf/ticket/<id>` - Download ticket PDF

---

### 3. Business Logic Layer
**Responsibility:** Core application logic and algorithms

**Modules:**

#### Booking Manager (`src/booking.py`)
- Train search with availability
- Multi-passenger booking creation
- Cancellation and refund processing
- PNR generation

#### Seat Allocation (`src/seat_allocation.py`)
- Algorithm: Assign seats based on preferences
- Coach and berth type assignment
- Seat number generation (e.g., "S1-45")
- Preference handling (Lower, Middle, Upper, etc.)

#### Waitlist Queue (`src/queue_manager.py`)
- FIFO waitlist management
- Auto-confirmation when seats available
- Waitlist types: GNWL, RAC, PQWL, RLWL, TQWL
- Status tracking and position updates

#### Route Graph (`src/route_graph.py`)
- Directed graph of train routes
- Station validation for booking
- Distance calculation between stations
- Path finding for multi-segment routes

#### Tatkal Manager (`src/admin.py`)
- Time window enforcement (AC: 10 AM, Non-AC: 11 AM)
- Premium fare calculation (1.1x - 1.4x multiplier)
- Quota management
- Admin overrides

#### Dynamic Pricing (`src/admin.py`)
- Surge multipliers based on demand
- Special event pricing
- Per-train and per-date rules
- Revenue optimization

#### PDF Generator (`src/pdf_generator.py`)
- Ticket layout with ReportLab
- QR code embedding for verification
- Passenger, train, and seat details
- Professional design

#### Email Service (`src/email_service.py`)
- SMTP integration (optional)
- Password reset emails
- Booking confirmation emails
- Template-based messages

#### Utilities (`src/utils.py`)
- PNR generation (10-digit unique)
- Fare calculation (distance × fare_per_km)
- Running trains query
- Helper functions

---

### 4. Data Access Layer (ORM)
**Responsibility:** Database operations

**SQLAlchemy Models** (`src/models.py`):
- **User** - Authentication with roles
- **Station** - 1,000 stations
- **Train** - 1,250 trains
- **TrainRoute** - Route graph (12,479 stops)
- **Booking** - Ticket reservations
- **Passenger** - Passenger details with seats
- **Payment** - Transaction records
- **Waitlist** - Waitlist queue
- **SeatAvailability** - Real-time availability
- **TatkalTimeSlot** - Tatkal windows
- **DynamicPricing** - Surge pricing rules
- **RefundRequest** - Cancellation requests
- **ComplaintManagement** - Support tickets
- **PerformanceMetrics** - Train KPIs
- **+ 4 more models**

**Operations:**
- **CRUD:** Create, Read, Update, Delete
- **Transactions:** ACID compliance for bookings
- **Relationships:** Foreign keys, joins, eager loading
- **Queries:** Filtered, paginated, sorted

---

## Database Design

### Entity-Relationship Overview

```
User (1) ──────< (N) Booking (N) >────── (1) Train
                       │                        │
                       │                        │
                       ▼                        ▼
                  Passenger (N)          TrainRoute (N) >──── (1) Station
                       │
                       │
                       ▼
                 SeatAvailability
```

### Key Relationships
- **User** has many **Bookings**
- **Booking** has many **Passengers**
- **Booking** has one **Payment**
- **Booking** may have one **Waitlist** entry
- **Train** has many **TrainRoutes**
- **TrainRoute** belongs to **Station** and **Train**
- **Train** has many **SeatAvailability** records

### Normalization
- **3NF (Third Normal Form)** for most tables
- Denormalization for performance in **SeatAvailability**
- Calculated fields cached for speed

### Indexes
- **Primary:** id on all tables
- **Unique:** PNR, train numbers, station codes
- **Foreign:** All foreign keys indexed
- **Composite:** (train_id, journey_date, coach_class) for availability

---

## Security Architecture

### Authentication
- **Password Hashing:** PBKDF2 with salt (Werkzeug)
- **Session Management:** Flask-Login with secure cookies
- **Role-Based Access:** user, admin, super_admin

### Authorization
- **Decorators:** `@login_required`, `@admin_required`, `@super_admin_required`
- **Template Checks:** `{% if current_user.is_admin() %}`
- **Route Protection:** Redirect to login if unauthorized

### CSRF Protection
- **Flask-WTF:** Automatic CSRF token generation
- **Forms:** `{{ form.hidden_tag() }}` in all POST forms
- **Validation:** Server-side token verification

### Input Validation
- **Email:** email-validator library
- **SQLAlchemy:** ORM prevents SQL injection
- **Forms:** WTForms validation
- **Sanitization:** Jinja2 auto-escaping

### Cookie Security
- **HTTPOnly:** Prevents JavaScript access
- **Secure:** HTTPS-only in production
- **SameSite:** Lax (CSRF protection)
- **Session Timeout:** 1 hour

### Database Security
- **Supabase:** Row Level Security (RLS) available
- **Environment Variables:** Secrets never in code
- **Connection Pooling:** Session Pooler with encryption

---

## Deployment Architecture

### Vercel Serverless

```
┌──────────────────────────────────────────────┐
│            Vercel Edge Network               │
│  (Global CDN, SSL/TLS, DDoS Protection)      │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│        Vercel Serverless Functions           │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │   Flask App (Gunicorn WSGI)            │ │
│  │   • Auto-scaling                       │ │
│  │   • Cold start optimization            │ │
│  │   • Stateless execution                │ │
│  └────────────────────────────────────────┘ │
└──────────────────┬───────────────────────────┘
                   │ psycopg2
                   ▼
┌──────────────────────────────────────────────┐
│    Supabase PostgreSQL (Session Pooler)      │
│  • IPv4 connection pooling                   │
│  • Auto-scaling                              │
│  • Managed backups                           │
│  • High availability                         │
└──────────────────────────────────────────────┘
```

### Key Features
- **Auto-scaling:** Handles traffic spikes automatically
- **Global CDN:** Low latency worldwide
- **SSL/TLS:** Automatic HTTPS
- **Environment Variables:** Secure secret management
- **Zero-downtime Deploys:** Blue-green deployment

---

## Data Flow

### Booking Flow Example

```
1. User searches trains
   ┌─────────────────────────────────────────┐
   │ GET /search_trains                      │
   │ from_station=1, to_station=50, date=... │
   └─────────────────┬───────────────────────┘
                     │
                     ▼
   ┌─────────────────────────────────────────┐
   │ search_trains() in utils.py             │
   │ • Query trains with route validation    │
   │ • Calculate availability per class       │
   └─────────────────┬───────────────────────┘
                     │
                     ▼
   ┌─────────────────────────────────────────┐
   │ Render search_results.html              │
   │ • Display matching trains                │
   │ • Show seat availability                 │
   │ • "Book Now" buttons                     │
   └─────────────────────────────────────────┘

2. User clicks "Book Now"
   ┌─────────────────────────────────────────┐
   │ GET /booking/book/<train_id>            │
   └─────────────────┬───────────────────────┘
                     │
                     ▼
   ┌─────────────────────────────────────────┐
   │ book_ticket() in booking.py             │
   │ • Store in session                       │
   │ • Render booking form                    │
   └─────────────────┬───────────────────────┘
                     │
                     ▼
   ┌─────────────────────────────────────────┐
   │ User fills passenger details            │
   │ POST /booking/seat_selection            │
   └─────────────────┬───────────────────────┘
                     │
                     ▼
   ┌─────────────────────────────────────────┐
   │ seat_selection() in booking.py          │
   │ • Call SeatAllocator.allocate_seats()   │
   │ • Assign coach + seat + berth           │
   │ • Create Booking (status=pending)       │
   │ • Create Passenger records              │
   └─────────────────┬───────────────────────┘
                     │
                     ▼
   ┌─────────────────────────────────────────┐
   │ Redirect to /payment/process/<id>       │
   └─────────────────┬───────────────────────┘
                     │
                     ▼
   ┌─────────────────────────────────────────┐
   │ process_payment() in payment.py         │
   │ • Create Payment record                  │
   │ • Simulate gateway                       │
   └─────────────────┬───────────────────────┘
                     │
                     ▼
   ┌─────────────────────────────────────────┐
   │ Payment success callback                │
   │ POST /payment/success                    │
   └─────────────────┬───────────────────────┘
                     │
                     ▼
   ┌─────────────────────────────────────────┐
   │ payment_success() in payment.py         │
   │ • Update Booking status=confirmed        │
   │ • Update Payment status=success          │
   │ • Update SeatAvailability (-passengers)  │
   │ • Commit transaction                     │
   └─────────────────┬───────────────────────┘
                     │
                     ▼
   ┌─────────────────────────────────────────┐
   │ Render payment_success.html             │
   │ • Display PNR                            │
   │ • Download ticket link                   │
   └─────────────────────────────────────────┘
```

---

## Key Design Decisions

### 1. Monolithic vs Microservices
**Decision:** Monolithic Flask application

**Rationale:**
- Team size (6 members) suits monolith
- Simpler deployment and debugging
- Shared ORM models reduce duplication
- Lower operational complexity

**Trade-offs:**
- ✅ Easier to develop and test
- ✅ Shared database transactions
- ❌ Entire app must scale together
- ❌ Tighter coupling between modules

---

### 2. Supabase PostgreSQL
**Decision:** Managed PostgreSQL via Supabase

**Rationale:**
- Fully managed (no database admin overhead)
- Built-in connection pooling (Session Pooler)
- IPv4 compatibility with Vercel
- Free tier sufficient for development

**Trade-offs:**
- ✅ No database maintenance
- ✅ Automatic backups and scaling
- ✅ SQL client built-in
- ❌ Vendor lock-in
- ❌ Free tier limits (500 MB, 1 GB bandwidth)

---

### 3. Inline CSS/JS
**Decision:** All assets inline in `base.html`

**Rationale:**
- Simplified Vercel deployment (no static file serving)
- Faster page loads (no additional HTTP requests)
- Easier to maintain (one template file)

**Trade-offs:**
- ✅ Simpler deployment
- ✅ Faster initial load
- ❌ Larger HTML payload
- ❌ No browser caching of CSS/JS

---

### 4. Blueprint Architecture
**Decision:** Modular blueprints for routes

**Rationale:**
- Clear separation of concerns
- Team members can work independently
- Easier testing and debugging

**Blueprints:**
- `main.py` - Homepage, search
- `auth.py` - Authentication
- `booking.py` - Booking flow
- `payment.py` - Payments
- `admin.py` - Admin panel
- `pdf_routes.py` - PDF generation

---

### 5. Real Data in Database
**Decision:** 1,000 stations, 1,250 trains pre-populated

**Rationale:**
- Realistic user experience
- Production-ready from day one
- No need for mock data

**Implementation:**
- `init_supabase.py` script
- Real Indian Railway station names
- Authentic train types (Rajdhani, Shatabdi, etc.)
- Realistic fares (₹0.30 - ₹3.50 per km)

---

### 6. Session-Based Booking
**Decision:** Multi-step booking stored in Flask session

**Rationale:**
- Simple implementation
- No database writes until payment
- Easy to abandon without cleanup

**Flow:**
1. Search → Store in session
2. Select train → Store in session
3. Enter passengers → Store in session
4. Payment → Write to database

---

### 7. Waitlist Auto-Confirmation
**Decision:** Automatic promotion from waitlist to confirmed

**Rationale:**
- Matches real-world railway systems
- Better user experience
- Maximizes seat utilization

**Implementation:**
- `WaitlistManager` checks on every cancellation
- FIFO queue ensures fairness
- Email notification on confirmation

---

## Performance Considerations

### Database Optimization
- **Indexes:** On frequently queried columns
- **Connection Pooling:** Supabase Session Pooler
- **Query Optimization:** Eager loading, select only needed fields
- **Caching:** Session caching for multi-step flows

### Application Optimization
- **Lazy Loading:** SQLAlchemy relationships
- **Pagination:** Admin reports and listings
- **Background Jobs:** None (all synchronous for simplicity)

### Frontend Optimization
- **Inline Assets:** Single HTTP request
- **Minification:** Compressed CSS/JS (optional)
- **Responsive Images:** Adaptive sizing
- **Theme Caching:** localStorage for theme preference

---

## Scalability

### Current Limits
- **Trains:** 1,250 (extendable)
- **Stations:** 1,000 (extendable)
- **Concurrent Users:** Limited by Vercel plan (free: ~100 req/hour)
- **Database:** Supabase free tier (500 MB, upgrade available)

### Scaling Strategies
1. **Horizontal:** Vercel auto-scales serverless functions
2. **Database:** Upgrade Supabase plan for more connections
3. **Caching:** Add Redis for seat availability (future)
4. **CDN:** Vercel Edge Network handles static content

---

## Team Architecture

### Frontend Team (3 members)
- **Member 1:** Landing, search, PNR enquiry
- **Member 2:** Booking flow, payments, user profile
- **Member 3:** Admin dashboard, reports, analytics

### Backend Team (3 members)
- **Member 1:** Authentication, user management
- **Member 2:** Booking engine, seat allocation, payments
- **Member 3:** Data management, routes, pricing, admin logic

**See `TEAM_ASSIGNMENT.md` for detailed responsibilities.**

---

## Future Enhancements

### Potential Improvements
1. **Caching Layer:** Redis for availability queries
2. **Async Processing:** Celery for email and PDF generation
3. **Real Payment Gateway:** Razorpay, Stripe integration
4. **Mobile App:** React Native or Flutter
5. **Analytics:** Google Analytics, custom dashboards
6. **Notifications:** Push notifications for chart preparation
7. **Multi-language:** i18n support for regional languages
8. **Accessibility:** WCAG 2.1 AA compliance

---

**Last Updated:** November 2025  
**Version:** 2.0 (Supabase PostgreSQL)  
**Maintained By:** RailServe Team (6 members)
