# RailServe File Structure Guide

Complete guide to every file in the RailServe project. Use this as a reference to understand what each file does and where to make changes.

---

## 📁 Root Directory

### **Configuration Files**

#### `requirements.txt`
**Purpose:** Python package dependencies  
**Contains:** Flask, SQLAlchemy, psycopg2-binary, reportlab, qrcode, faker, etc.  
**When to edit:** Adding new Python libraries  
**Owner:** Backend team (coordinate changes)

#### `vercel.json`
**Purpose:** Vercel deployment configuration  
**Contains:** Build commands, routes, environment variable settings  
**When to edit:** Changing deployment settings for Vercel  
**Owner:** DevOps/Backend Member 3

#### `.gitignore`
**Purpose:** Files to exclude from git  
**Contains:** `__pycache__/`, `.env`, `*.pyc`, `node_modules/`, `.replit`, etc.  
**When to edit:** Adding new file patterns to ignore  
**Owner:** All team members

---

### **Main Application Files**

#### `main.py` (305 lines)
**Purpose:** Main application entry point and core routes  
**Routes:**
- `/` - Homepage with train listings
- `/search_trains` - Train search between stations
- `/pnr_enquiry` - PNR status lookup
- `/submit_complaint` - Customer complaint submission

**Key Functions:**
- `index()` - Displays homepage with running trains
- `search_trains_route()` - Handles train search form
- `pnr_enquiry()` - PNR status checker
- `submit_complaint()` - Customer support tickets

**Owner:** Frontend Member 1 (UI), Backend Member 2 (search logic)  
**Imports:** `src.app`, `src.models`, `src.utils`

---

### **Database Initialization**

#### `init_supabase.py` (460 lines)
**Purpose:** Initializes Supabase PostgreSQL database with real Indian railway data  
**Creates:**
- 1,000 stations (including Mumbai Central, Delhi, Chennai, etc.)
- 1,250 trains (Rajdhani, Shatabdi, Duronto, Mail/Express, Passenger)
- 12,479 route stops (avg 10 stops per train)
- Admin user (username: admin, password: admin123)
- Tatkal time slots (AC: 10 AM, Non-AC: 11 AM)

**Usage:** `python init_supabase.py`  
**Owner:** Backend Member 3  
**When to run:** First-time setup or database reset

#### `init_db.py` (DEPRECATED)
**Purpose:** Old SQLite initialization script  
**Status:** No longer used (replaced by `init_supabase.py`)  
**Action:** Can be deleted

---

## 📁 `src/` Directory - Core Application Code

### **Application Setup**

#### `src/__init__.py`
**Purpose:** Makes `src` a Python package  
**Contains:** Empty file  
**Owner:** Backend team

#### `src/app.py` (135 lines)
**Purpose:** Flask application factory and configuration  
**Key Configuration:**
- Supabase PostgreSQL connection (via `DATABASE_URL`)
- Session secret key
- CSRF protection
- Security headers
- Error handlers (404, 500, 403)
- Blueprint registration

**Environment Variables:**
- `DATABASE_URL` - Supabase PostgreSQL connection string (required)
- `SESSION_SECRET` - Flask session encryption key (optional, auto-generated in dev)
- `FLASK_ENV` - production or development

**Owner:** Backend Member 3  
**When to edit:** Changing app-wide settings, adding new blueprints

#### `src/database.py` (7 lines)
**Purpose:** SQLAlchemy database object initialization  
**Contains:** `db` object used throughout the app  
**Owner:** Backend Member 3  
**When to edit:** Rarely (only for ORM changes)

---

### **Data Models**

#### `src/models.py` (649 lines)
**Purpose:** SQLAlchemy ORM models for all database tables  
**Models Defined:**
1. `User` (lines 8-37) - User accounts with roles
2. `Station` (lines 39-53) - Railway stations
3. `Train` (lines 55-73) - Train information
4. `TrainRoute` (lines 75-88) - Station sequences in routes
5. `Booking` (lines 90-121) - Ticket bookings
6. `Passenger` (lines 123-237) - Passenger details with seat allocation
7. `Payment` (lines 239-252) - Payment transactions
8. `Waitlist` (lines 254-277) - Waitlist queue
9. `TatkalTimeSlot` (lines 279-298) - Tatkal booking windows
10. `TatkalOverride` (lines 300-320) - Admin Tatkal overrides
11. `DynamicPricing` (lines 322-352) - Surge pricing rules
12. `SeatAvailability` (lines 369-384) - Real-time seat tracking
13. `ChartPreparation` (lines 386-397) - Chart preparation status
14. `RefundRequest` (lines 399-417) - Cancellation requests
15. `ComplaintManagement` (lines 419-445) - Support tickets
16. `PerformanceMetrics` (lines 447-475) - Train KPIs
17. `LoyaltyProgram` (lines 477-498) - User loyalty points
18. `PlatformManagement` (lines 500-523) - Platform assignments

**Owner:** All backend members (coordinate schema changes)  
**When to edit:** Adding new fields or tables

---

### **Authentication & User Management**

#### `src/auth.py` (230 lines)
**Purpose:** User authentication and account management  
**Routes:**
- `/auth/register` - User registration
- `/auth/login` - User login
- `/auth/logout` - User logout
- `/auth/forgot_password` - Password reset request
- `/auth/reset_password/<token>` - Password reset with token

**Key Functions:**
- `register()` - Create new user account
- `login()` - Authenticate and create session
- `logout()` - Clear user session
- `forgot_password()` - Send password reset email
- `reset_password()` - Update password with valid token

**Owner:** Backend Member 1  
**Templates:** `login.html`, `register.html`, `forgot_password.html`, `reset_password.html`

---

### **Booking System**

#### `src/booking.py` (450+ lines)
**Purpose:** Train booking workflow and ticket management  
**Routes:**
- `/booking/book/<train_id>` - Start booking for a train
- `/booking/seat_selection` - Choose seats and berths
- `/booking/tatkal` - Tatkal booking interface
- `/booking/history` - User's booking history
- `/booking/cancel/<booking_id>` - Cancel booking

**Key Functions:**
- `book_ticket()` - Initialize booking session
- `seat_selection()` - Assign seats to passengers
- `tatkal_booking()` - Handle Tatkal time restrictions
- `booking_history()` - Display user's past bookings
- `cancel_booking()` - Process cancellation and refund

**Owner:** Backend Member 2 (Frontend Member 2 for templates)  
**Templates:** `book_ticket.html`, `seat_selection.html`, `tatkal_booking.html`, `booking_history.html`

#### `src/seat_allocation.py`
**Purpose:** Seat and berth assignment algorithm  
**Key Class:** `SeatAllocator`  
**Functions:**
- `allocate_seats()` - Assign coach, seat number, and berth type
- `get_berth_preference_order()` - Prioritize berth preferences
- `assign_berth()` - Allocate Lower, Middle, Upper, Side Lower, Side Upper

**Owner:** Backend Member 2  
**Algorithm:** Assigns seats respecting user preferences and availability

#### `src/queue_manager.py`
**Purpose:** Waitlist (GNWL, RAC, PQWL, RLWL) management  
**Key Class:** `WaitlistManager`  
**Functions:**
- `add_to_waitlist()` - Add booking to waitlist
- `process_confirmation()` - Auto-confirm when seats available
- `get_current_status()` - Return waitlist position

**Owner:** Backend Member 2  
**Logic:** FIFO queue with auto-promotion to confirmed

---

### **Payment Processing**

#### `src/payment.py` (180 lines)
**Purpose:** Payment gateway integration and transaction tracking  
**Routes:**
- `/payment/process/<booking_id>` - Initiate payment
- `/payment/success` - Payment success callback
- `/payment/failure` - Payment failure handling

**Key Functions:**
- `process_payment()` - Create payment record and redirect to gateway
- `payment_success()` - Confirm booking after successful payment
- `payment_failure()` - Rollback booking on payment failure

**Owner:** Backend Member 2  
**Templates:** `payment.html`, `payment_success.html`, `payment_failure.html`

---

### **Admin Panel**

#### `src/admin.py` (800+ lines)
**Purpose:** Administrative dashboard and controls  
**Routes:**
- `/admin/` - Dashboard with analytics
- `/admin/trains` - Train management (CRUD)
- `/admin/stations` - Station management
- `/admin/booking_reports` - Booking analytics and CSV export
- `/admin/dynamic_pricing` - Surge pricing configuration
- `/admin/tatkal_management` - Tatkal time slot setup
- `/admin/quota_management` - Quota allocation
- `/admin/complaints` - Customer support tickets
- `/admin/refunds` - Refund request processing
- `/admin/analytics` - Revenue and performance metrics

**Decorators:**
- `@admin_required` - Restricts to admin/super_admin roles
- `@super_admin_required` - Restricts to super_admin only

**Owner:** Backend Member 3 (Frontend Member 3 for templates)  
**Templates:** All files in `templates/admin/`

---

### **PDF Ticket Generation**

#### `src/pdf_generator.py`
**Purpose:** Generate PDF tickets with QR codes  
**Key Class:** `PDFTicketGenerator`  
**Functions:**
- `generate_ticket()` - Create PDF with train, passenger, seat details
- `add_qr_code()` - Embed QR code for verification
- `format_ticket_layout()` - Professional ticket design

**Owner:** Backend Member 2  
**Libraries:** ReportLab, qrcode

#### `src/pdf_routes.py`
**Purpose:** PDF download endpoints  
**Routes:**
- `/pdf/ticket/<booking_id>` - Download ticket PDF

**Owner:** Backend Member 2

---

### **Utility Functions**

#### `src/utils.py` (200+ lines)
**Purpose:** Helper functions used across the app  
**Key Functions:**
- `get_running_trains()` - Fetch active trains
- `search_trains()` - Search trains between stations
- `get_all_class_availability()` - Seat availability by coach class
- `calculate_fare()` - Compute fare based on distance and class
- `generate_pnr()` - Create unique PNR number

**Owner:** Backend Member 2  
**When to edit:** Adding new helper functions

#### `src/route_graph.py`
**Purpose:** Graph-based train route modeling  
**Key Class:** `RouteGraph`  
**Functions:**
- `build_graph()` - Create adjacency list from routes
- `validate_route()` - Check if from/to stations exist on train route
- `calculate_distance()` - Compute km between two stations

**Owner:** Backend Member 3  
**Algorithm:** Directed graph with stations as nodes, routes as edges

#### `src/email_service.py`
**Purpose:** Email sending for password resets and booking confirmations  
**Key Functions:**
- `send_email()` - SMTP email delivery
- `send_password_reset()` - Password reset email template
- `send_booking_confirmation()` - Ticket confirmation email

**Owner:** Backend Member 1  
**Configuration:** SMTP environment variables (optional)

---

## 📁 `templates/` Directory - Frontend Templates

### **Base Template**

#### `templates/base.html` (400+ lines)
**Purpose:** Master template with navigation, footer, theme support  
**Features:**
- Responsive navigation bar
- Dark/light theme toggle
- Flash message display
- Mobile menu
- All CSS and JavaScript inline (no external files)

**Sections:**
- `<head>` - Meta tags, inline CSS
- `<nav>` - Navigation bar with login/logout
- `{% block content %}` - Child template content
- `<footer>` - Site footer
- `<script>` - Theme toggle, mobile menu

**Owner:** Frontend team (coordinate changes)  
**Used by:** All other templates

---

### **Public Pages**

#### `templates/index.html`
**Purpose:** Homepage with train search  
**Features:**
- Search form (from/to stations, date)
- Running trains display
- Seat availability preview

**Owner:** Frontend Member 1

#### `templates/search_results.html`
**Purpose:** Train search results  
**Features:**
- List of matching trains
- Seat availability by class
- "Book Now" buttons

**Owner:** Frontend Member 1

#### `templates/pnr_enquiry.html`
**Purpose:** PNR status lookup  
**Features:**
- PNR input form
- Booking status display (confirmed, waitlisted, RAC)
- Passenger details and seat numbers

**Owner:** Frontend Member 1

---

### **Authentication Pages**

#### `templates/login.html`
**Purpose:** User login form  
**Owner:** Backend Member 1 (Frontend Member 1 for styling)

#### `templates/register.html`
**Purpose:** User registration form  
**Owner:** Backend Member 1 (Frontend Member 1 for styling)

#### `templates/forgot_password.html`
**Purpose:** Password reset request  
**Owner:** Backend Member 1 (Frontend Member 1 for styling)

#### `templates/reset_password.html`
**Purpose:** Password reset with token  
**Owner:** Backend Member 1 (Frontend Member 1 for styling)

---

### **Booking Pages**

#### `templates/book_ticket.html`
**Purpose:** Booking form with passenger details  
**Features:**
- Train and route details
- Passenger information form (name, age, gender, ID proof)
- Coach class selection
- Berth preference

**Owner:** Frontend Member 2

#### `templates/seat_selection.html`
**Purpose:** Seat and berth selection  
**Features:**
- Visual seat map
- Berth preference (Lower, Middle, Upper, etc.)
- Seat number assignment preview

**Owner:** Frontend Member 2

#### `templates/tatkal_booking.html`
**Purpose:** Tatkal (last-minute) booking  
**Features:**
- Tatkal time window validation
- Premium fare display
- Limited availability warning

**Owner:** Frontend Member 2

#### `templates/payment.html`
**Purpose:** Payment interface  
**Owner:** Frontend Member 2

#### `templates/payment_success.html`
**Purpose:** Payment confirmation  
**Features:**
- Booking confirmed message
- PNR display
- Download ticket link

**Owner:** Frontend Member 2

#### `templates/payment_failure.html`
**Purpose:** Payment failure  
**Features:**
- Error message
- Retry payment option

**Owner:** Frontend Member 2

#### `templates/booking_history.html`
**Purpose:** User's past bookings  
**Features:**
- List of all bookings
- Download ticket links
- Cancel booking option

**Owner:** Frontend Member 2

---

### **User Pages**

#### `templates/profile.html`
**Purpose:** User account details  
**Features:**
- User information
- Edit profile form
- Loyalty points display

**Owner:** Frontend Member 2

#### `templates/submit_complaint.html`
**Purpose:** Customer support ticket submission  
**Owner:** Frontend Member 1

#### `templates/file_tdr.html`
**Purpose:** TDR (Ticket Deposit Receipt) filing  
**Owner:** Frontend Member 2

---

### **Admin Pages**

All files in `templates/admin/` are owned by **Frontend Member 3**.

#### `templates/admin/dashboard.html`
**Purpose:** Main admin dashboard  
**Features:**
- Revenue metrics
- Booking statistics
- Active users count
- Charts and graphs

#### `templates/admin/trains.html`
**Purpose:** Train management (CRUD)  
**Features:**
- Train list with edit/delete
- Add new train form
- Train details modal

#### `templates/admin/stations.html`
**Purpose:** Station management  
**Features:**
- Station list
- Add/edit station forms

#### `templates/admin/booking_reports.html`
**Purpose:** Booking analytics  
**Features:**
- Date range filter
- Revenue by train
- CSV export

#### `templates/admin/analytics.html`
**Purpose:** Advanced analytics  
**Features:**
- Revenue charts
- Booking trends
- Performance metrics

#### `templates/admin/dynamic_pricing.html`
**Purpose:** Surge pricing configuration  
**Features:**
- Price multiplier settings
- Special event pricing

#### `templates/admin/tatkal_management.html`
**Purpose:** Tatkal time slot setup  
**Features:**
- AC/Non-AC time slots
- Days before journey setting

#### `templates/admin/quota_management.html`
**Purpose:** Quota allocation (Ladies, Senior, Disability, etc.)

#### `templates/admin/complaint_management.html`
**Purpose:** Customer support ticket system  
**Features:**
- Complaint list
- Status updates (pending, resolved)
- Admin responses

#### `templates/admin/refund_management.html`
**Purpose:** Refund request processing

#### `templates/admin/waitlist_management.html`
**Purpose:** Waitlist monitoring

#### `templates/admin/platform_management.html`
**Purpose:** Platform assignments for trains

#### `templates/admin/route_management.html`
**Purpose:** Train route editing

#### `templates/admin/performance_metrics.html`
**Purpose:** Train KPIs (on-time %, load factor)

---

### **Error Pages**

#### `templates/errors/404.html`
**Purpose:** Page not found  
**Owner:** Frontend Member 1

#### `templates/errors/500.html`
**Purpose:** Internal server error  
**Owner:** Frontend Member 1

#### `templates/errors/403.html`
**Purpose:** Forbidden (access denied)  
**Owner:** Frontend Member 1

---

## 📁 `src/db_init/` Directory - Database Initialization Scripts

**Purpose:** Modular scripts for populating database (used by `init_db.py`, deprecated)  
**Status:** Legacy code, replaced by `init_supabase.py`  
**Action:** Can be archived or deleted

Files:
- `__init__.py`
- `admin.py` - Create admin user
- `stations.py` - Populate stations
- `trains.py` - Populate trains
- `routes.py` - Create train routes
- `availability.py` - Seed seat availability
- `orchestrator.py` - Coordinate initialization
- `constants.py` - Configuration constants
- `db_utils.py` - Database utilities

---

## 📁 `doc/` Directory - Project Documentation

#### `doc/PROJECT_OVERVIEW.md`
**Purpose:** High-level project description  
**Owner:** All team members (update as needed)

#### `doc/DATABASE_SCHEMA.md`
**Purpose:** Complete database table schemas  
**Owner:** Backend Member 3

#### `doc/API_MIGRATION_GUIDE.md`
**Purpose:** Guide for migrating to new APIs  
**Status:** May be outdated

#### `doc/DEPLOYMENT_GUIDE.md`
**Purpose:** Vercel deployment instructions  
**Owner:** Backend Member 3

---

## 📁 `instance/` Directory

**Purpose:** SQLite database storage (deprecated)  
**Contents:** `railway.db` (deleted)  
**Status:** No longer used with Supabase PostgreSQL

---

## 📋 Summary by Team Member

### **Frontend Member 1:**
- `templates/index.html`, `search_results.html`, `pnr_enquiry.html`
- `templates/errors/` (all)
- `templates/submit_complaint.html`
- `main.py` (UI-related changes)

### **Frontend Member 2:**
- `templates/book_ticket.html`, `seat_selection.html`, `tatkal_booking.html`
- `templates/payment*.html`, `booking_history.html`, `profile.html`
- `src/booking.py` (UI integration)

### **Frontend Member 3:**
- `templates/admin/` (all files)
- `src/admin.py` (UI integration)

### **Backend Member 1:**
- `src/auth.py`
- `templates/login.html`, `register.html`, `forgot_password.html`, `reset_password.html`
- `src/email_service.py`
- `src/models.py` (User model)

### **Backend Member 2:**
- `src/booking.py`, `src/payment.py`
- `src/seat_allocation.py`, `src/queue_manager.py`
- `src/pdf_generator.py`, `src/pdf_routes.py`
- `src/utils.py`
- `src/models.py` (Booking, Passenger, Payment, Waitlist, SeatAvailability models)

### **Backend Member 3:**
- `src/app.py`, `src/database.py`
- `init_supabase.py`
- `src/route_graph.py`
- `src/admin.py` (admin logic)
- `src/models.py` (Train, Station, TrainRoute, TatkalTimeSlot, DynamicPricing, PerformanceMetrics models)
- `vercel.json`

---

**Last Updated:** November 2025  
**Total Files:** 100+  
**Lines of Code:** ~15,000+
