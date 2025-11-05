# RailServe System Mind Map

Visual representation of the entire RailServe system architecture and components.

```
                            ┌──────────────────┐
                            │   RAILSERVE      │
                            │ Railway Booking  │
                            │     System       │
                            └────────┬─────────┘
                                     │
                ┌────────────────────┼────────────────────┐
                │                    │                    │
          ┌─────▼─────┐      ┌──────▼──────┐     ┌──────▼──────┐
          │  FRONTEND │      │   BACKEND   │     │  DATABASE   │
          │  (3 devs) │      │  (3 devs)   │     │  (Supabase) │
          └─────┬─────┘      └──────┬──────┘     └──────┬──────┘
                │                   │                    │
      ┌─────────┼─────────┐        │         ┌──────────┼──────────┐
      │         │         │        │         │          │          │
  ┌───▼───┐ ┌──▼───┐ ┌───▼───┐   │    ┌────▼────┐ ┌───▼───┐  ┌───▼────┐
  │Member1│ │Member2│ │Member3│   │    │  Tables │ │Indexes│  │Triggers│
  └───┬───┘ └───┬──┘ └───┬───┘   │    └────┬────┘ └───┬───┘  └───┬────┘
      │         │        │        │         │          │          │
┌─────┼─────┐   │    ┌───┼────┐  │    ┌────┼──────────┼──────────┼────┐
│     │     │   │    │   │    │  │    │    │          │          │    │
▼     ▼     ▼   ▼    ▼   ▼    ▼  │    ▼    ▼          ▼          ▼    ▼
Landing  Booking  Admin │    │   │   user  station   train    booking  │
Search   Flow     Panel │    │   │   (auth)(1000)    (1250)  (dynamic) │
PNR      Payment  Reports│   │   │                                     │
         Profile  Analytics  │   │   train_route  seat_availability    │
         History  Complaints │   │   (12,479)     (calculated)         │
                            │   │                                     │
      ┌─────────────────────┼───┼─────────────────────────────────────┘
      │                     │   │
┌─────▼─────────────┐       │   │
│  BUSINESS LOGIC   │       │   │
│    (6 Modules)    │       │   │
└─────┬─────────────┘       │   │
      │                     │   │
┌─────┼──────┬──────┬───────┼───┼──────┐
│     │      │      │       │   │      │
▼     ▼      ▼      ▼       │   ▼      ▼
Auth  Booking Seat  Waitlist│  Route  Tatkal
System Manager Alloc Queue  │  Graph  Manager
       │            │        │   │      │
       │            │        │   │      │
       └────────────┼────────┼───┘      │
                    │        │          │
              ┌─────▼────────▼──────────▼─────┐
              │      CORE FEATURES            │
              ├───────────────────────────────┤
              │ • 1,000 Stations              │
              │ • 1,250 Trains                │
              │ • Real Indian Railway Data    │
              │ • Multi-passenger Booking     │
              │ • Tatkal Support              │
              │ • Waitlist (GNWL/RAC)         │
              │ • Dynamic Pricing             │
              │ • PDF Tickets with QR         │
              │ • Admin Dashboard             │
              │ • Reports & Analytics         │
              └───────────────────────────────┘
```

---

## Component Breakdown

### Frontend Components (3 Team Members)

```
FRONTEND
│
├── Member 1: Landing & Search
│   ├── Homepage (index.html)
│   ├── Train Search (search_results.html)
│   ├── PNR Enquiry (pnr_enquiry.html)
│   ├── Error Pages (404, 500, 403)
│   └── Complaint Form (submit_complaint.html)
│
├── Member 2: Booking Flow & User
│   ├── Book Ticket (book_ticket.html)
│   ├── Seat Selection (seat_selection.html)
│   ├── Payment Pages (payment*.html)
│   ├── Booking History (booking_history.html)
│   ├── User Profile (profile.html)
│   └── Tatkal Booking (tatkal_booking.html)
│
└── Member 3: Admin Dashboard
    ├── Dashboard (admin/dashboard.html)
    ├── Train Management (admin/trains.html)
    ├── Station Management (admin/stations.html)
    ├── Booking Reports (admin/booking_reports.html)
    ├── Analytics (admin/analytics.html)
    ├── Dynamic Pricing (admin/dynamic_pricing.html)
    ├── Tatkal Management (admin/tatkal_management.html)
    ├── Complaints (admin/complaint_management.html)
    └── Refunds (admin/refund_management.html)
```

### Backend Components (3 Team Members)

```
BACKEND
│
├── Member 1: Authentication & Users
│   ├── User Registration (auth.py)
│   ├── User Login/Logout (auth.py)
│   ├── Password Reset (auth.py)
│   ├── Session Management (Flask-Login)
│   ├── Role-Based Access (decorators)
│   └── Email Service (email_service.py)
│
├── Member 2: Booking Engine & Operations
│   ├── Train Search (utils.py)
│   ├── Booking Creation (booking.py)
│   ├── Seat Allocation (seat_allocation.py)
│   ├── Waitlist Management (queue_manager.py)
│   ├── Payment Processing (payment.py)
│   ├── PDF Generation (pdf_generator.py)
│   ├── Cancellation & Refunds (booking.py)
│   └── PNR Generation (utils.py)
│
└── Member 3: Data & System Management
    ├── Database Init (init_supabase.py)
    ├── Train & Station CRUD (admin.py)
    ├── Route Graph (route_graph.py)
    ├── Tatkal Time Slots (admin.py)
    ├── Dynamic Pricing (admin.py)
    ├── Performance Metrics (admin.py)
    └── Admin Logic (admin.py)
```

### Database Schema (18 Tables)

```
DATABASE (Supabase PostgreSQL)
│
├── Core Tables
│   ├── user (authentication, roles)
│   ├── station (1,000 Indian stations)
│   ├── train (1,250 trains with fares)
│   └── train_route (12,479 route stops)
│
├── Booking Tables
│   ├── booking (PNR, status, amount)
│   ├── passenger (name, age, seat details)
│   ├── payment (transactions)
│   ├── seat_availability (real-time)
│   └── waitlist (queue management)
│
├── Feature Tables
│   ├── tatkal_time_slot (booking windows)
│   ├── tatkal_override (admin overrides)
│   ├── dynamic_pricing (surge rules)
│   ├── refund_request (cancellations)
│   └── complaint_management (support)
│
└── Analytics Tables
    ├── performance_metrics (train KPIs)
    ├── loyalty_program (user points)
    ├── chart_preparation (seat allocation)
    └── platform_management (platform allocation)
```

---

## Data Flow Mind Map

```
USER JOURNEY
│
├── 1. SEARCH
│   ├── Select from_station
│   ├── Select to_station
│   ├── Select date
│   └── Click "Search Trains"
│       │
│       ▼
│   ┌────────────────────┐
│   │ Query: Train.query │
│   │ Filter: routes     │
│   │ Check: availability│
│   └────────┬───────────┘
│            │
│            ▼
│   Display Results:
│   • Train list
│   • Seat availability
│   • Fare information
│
├── 2. BOOK
│   ├── Click "Book Now"
│   ├── Login (if needed)
│   ├── Enter passenger details
│   │   • Name, Age, Gender
│   │   • ID proof
│   │   • Berth preference
│   └── Select coach class
│       │
│       ▼
│   ┌──────────────────────┐
│   │ seat_allocation.py   │
│   │ • Assign coach       │
│   │ • Assign seat number │
│   │ • Assign berth       │
│   └──────────┬───────────┘
│              │
│              ▼
│   Create Records:
│   • Booking (pending)
│   • Passenger(s)
│   • Payment (pending)
│
├── 3. PAY
│   ├── Review booking
│   ├── Proceed to payment
│   └── Payment gateway
│       │
│       ▼
│   ┌──────────────────────┐
│   │ payment.py           │
│   │ • Create Payment     │
│   │ • Gateway redirect   │
│   └──────────┬───────────┘
│              │
│              ▼
│   On Success:
│   • Update Booking → confirmed
│   • Update Payment → success
│   • Update SeatAvailability
│   • Generate PNR
│
└── 4. CONFIRM
    ├── Display PNR
    ├── Download PDF ticket
    ├── Send confirmation email
    └── Add to booking history
```

---

## Technology Stack Mind Map

```
TECHNOLOGY STACK
│
├── BACKEND
│   ├── Framework: Flask 3.1+
│   ├── ORM: SQLAlchemy 2.0+
│   ├── Database Driver: psycopg2-binary
│   ├── Server: Gunicorn 23.0+
│   ├── Auth: Flask-Login 0.6+
│   ├── Security: Flask-WTF (CSRF)
│   └── PDF: ReportLab, qrcode
│
├── FRONTEND
│   ├── Templates: Jinja2
│   ├── HTML5/CSS3 (responsive)
│   ├── JavaScript (vanilla)
│   └── Themes: Light/Dark
│
├── DATABASE
│   ├── Provider: Supabase
│   ├── Type: PostgreSQL
│   ├── Pooler: Session Pooler (IPv4)
│   ├── Backup: Automatic
│   └── Scaling: Managed
│
└── DEPLOYMENT
    ├── Platform: Vercel
    ├── Type: Serverless
    ├── CDN: Edge Network
    ├── SSL: Automatic
    └── Scaling: Auto
```

---

## Security Mind Map

```
SECURITY LAYERS
│
├── AUTHENTICATION
│   ├── Password Hashing (PBKDF2)
│   ├── Session Cookies (HTTPOnly)
│   ├── Token-based Reset
│   └── Role-Based Access
│
├── AUTHORIZATION
│   ├── Decorators (@login_required)
│   ├── Roles (user, admin, super_admin)
│   └── Route Protection
│
├── INPUT VALIDATION
│   ├── CSRF Tokens (Flask-WTF)
│   ├── Email Validation
│   ├── SQL Injection Prevention (ORM)
│   └── XSS Protection (Jinja2)
│
├── DATA PROTECTION
│   ├── Environment Variables
│   ├── Encrypted Connections
│   ├── Secure Cookies
│   └── SameSite Cookies
│
└── DATABASE SECURITY
    ├── Supabase RLS (available)
    ├── Connection Pooling
    └── Encrypted in Transit
```

---

## Feature Mind Map

```
CORE FEATURES
│
├── USER FEATURES
│   ├── Search (1,000 stations)
│   ├── Book (multi-passenger)
│   ├── Tatkal (last-minute)
│   ├── Waitlist (GNWL, RAC)
│   ├── PNR Enquiry
│   ├── Download Tickets (PDF + QR)
│   ├── Booking History
│   ├── Profile Management
│   └── Complaint Submission
│
├── ADMIN FEATURES
│   ├── Dashboard (analytics)
│   ├── Train CRUD
│   ├── Station CRUD
│   ├── Route Management
│   ├── Booking Reports (CSV)
│   ├── Dynamic Pricing
│   ├── Tatkal Management
│   ├── Quota Management
│   ├── Complaint Management
│   ├── Refund Processing
│   ├── Performance Metrics
│   └── Platform Allocation
│
└── SYSTEM FEATURES
    ├── Real Data (1,000 + 1,250)
    ├── Real-time Availability
    ├── Auto Waitlist Confirmation
    ├── Seat Allocation Algorithm
    ├── Distance Calculation
    ├── Fare Calculation
    ├── PNR Generation
    └── Email Notifications
```

---

**Last Updated:** November 2025  
**Purpose:** Visual system overview for team understanding  
**Format:** ASCII art mind map
