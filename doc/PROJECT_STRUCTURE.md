# RailServe 2025 - Project Structure & Organization

**Last Updated:** October 27, 2025

---

## Project Overview
RailServe is a comprehensive railway reservation system built with Flask, featuring real-time booking, dynamic pricing, waitlist management, and administrative controls.

---

## Project Division: 5 Major Parts

### **PART 1: Frontend - User Interface & Experience** 🎨
**Technology:** HTML5, CSS3, JavaScript, Jinja2 Templates  
**Location:** `templates/`, `static/`

#### Key Components:
- **Homepage & Search (`templates/index.html`)**
  - Hero section with modern gradient design
  - Real-time train search with station selection
  - Popular trains display
  - Features showcase section

- **Authentication Pages**
  - Login (`templates/login.html`)
  - Registration (`templates/register.html`)
  - Password reset (`templates/forgot_password.html`, `templates/reset_password.html`)

- **User Profile & History**
  - Profile management (`templates/profile.html`)
  - Booking history (`templates/booking_history.html`)
  - PNR enquiry (`templates/pnr_enquiry.html`)

#### Styling & Assets:
- **Base Template:** `templates/base.html` - Master layout with navigation, footer, theme support
- **CSS:** 
  - `static/css/animations.css` - Animations and transitions
  - `static/css/dark-theme.css` - Dark mode support
- **JavaScript:**
  - `static/js/animations.js` - Interactive animations
  - `static/js/dark-theme.js` - Theme switching logic

#### Responsive Design:
- Mobile-first approach
- Breakpoints: 480px, 768px, 992px, 1200px
- Touch-optimized navigation
- Adaptive hero sections

---

### **PART 2: Frontend - Booking Flow** 🎫
**Technology:** HTML5, CSS3, JavaScript (Form Validation)  
**Location:** `templates/`

#### Key Components:
- **Search & Results**
  - Train search results (`templates/search_results.html`)
  - Route-based train discovery
  - Available seats display

- **Booking Process**
  - Ticket booking form (`templates/book_ticket.html`)
  - Seat selection interface (`templates/seat_selection.html`)
  - Tatkal booking (`templates/tatkal_booking.html`)

- **Payment Flow**
  - Payment gateway integration (`templates/payment.html`)
  - Payment success confirmation (`templates/payment_success.html`)
  - Payment failure handling (`templates/payment_failure.html`)

- **Post-Booking**
  - TDR filing (`templates/file_tdr.html`)
  - Complaint submission (`templates/submit_complaint.html`)

#### Features:
- Real-time seat availability
- Dynamic fare calculation
- Tatkal time slot validation
- Payment processing workflow
- PDF ticket generation

---

### **PART 3: Frontend - Admin Dashboard** 👨‍💼
**Technology:** HTML5, CSS3, JavaScript (Charts, Data Tables)  
**Location:** `templates/admin/`

#### Admin Pages (20+ pages):
- **Main Dashboard** (`templates/admin/dashboard.html`)
  - System overview
  - Key metrics and statistics
  - Quick actions

- **Train Management**
  - Train listing & CRUD (`templates/admin/trains.html`)
  - Route management (`templates/admin/route_management.html`)
  - Train route details (`templates/admin/train_route_details.html`)
  - Platform management (`templates/admin/platform_management.html`)

- **Station Management** (`templates/admin/stations.html`)
  - Station CRUD operations
  - City and code management

- **Booking & Reservations**
  - Seat allocation (`templates/admin/seat_allocation.html`)
  - Waitlist management (`templates/admin/waitlist_management.html`)
  - Waitlist details (`templates/admin/waitlist_details.html`)
  - Waitlist allocation (`templates/admin/waitlist_allocation.html`)
  - Chart preparation (`templates/admin/chart_preparation.html`)

- **Fare & Pricing**
  - Fare management (`templates/admin/fare_management.html`)
  - Dynamic pricing (`templates/admin/dynamic_pricing.html`)
  - Quota management (`templates/admin/quota_management.html`)
  - Emergency quota (`templates/admin/emergency_quota.html`)

- **Tatkal System**
  - Tatkal management (`templates/admin/tatkal_management.html`)
  - Tatkal time slots (`templates/admin/tatkal_timeslots.html`)
  - **Tatkal override** (`templates/admin/tatkal_override.html`) - Real-time override controls

- **User Management** (`templates/admin/users.html`)
  - User accounts
  - Role management
  - Activity monitoring

- **Reports & Analytics**
  - Booking reports (`templates/admin/booking_reports.html`)
  - Performance metrics (`templates/admin/performance_metrics.html`)
  - Analytics dashboard (`templates/admin/analytics.html`)

- **Customer Service**
  - PNR inquiry (`templates/admin/pnr_inquiry.html`)
  - Refund management (`templates/admin/refund_management.html`)
  - Complaint management (`templates/admin/complaint_management.html`)

- **Error Pages**
  - 403 Forbidden (`templates/errors/403.html`)
  - 404 Not Found (`templates/errors/404.html`)
  - 500 Server Error (`templates/errors/500.html`)

#### Admin Features:
- Real-time data updates
- Interactive charts and graphs
- Bulk operations
- Export to PDF/CSV
- Search and filter capabilities
- Responsive admin interface

---

### **PART 4: Backend - Core System & Business Logic** ⚙️
**Technology:** Python 3.11, Flask, SQLAlchemy  
**Location:** `src/`

#### Core Modules:

**1. Application Setup (`src/app.py`)**
- Flask app initialization
- Database configuration
- SQLAlchemy setup
- Session management
- ProxyFix middleware
- CSRF protection

**2. Database Models (`src/models.py`)**
- User model with authentication
- Train & TrainRoute models
- Station model
- Booking & BookingPassenger models
- Seat allocation models
- Waitlist models
- Payment models
- Tatkal models
- Complaint management
- Admin models
- Relationship mappings

**3. Authentication & Security (`src/auth.py`)**
- User registration
- Login/logout
- Password hashing (werkzeug)
- Session management
- Password reset via email
- Flask-Login integration
- Role-based access control

**4. Booking Engine (`src/booking.py`)**
- Train search algorithm
- Seat availability checking
- Reservation creation
- Waitlist handling
- Tatkal booking logic
- Quota management
- Berth preference handling

**5. Payment Processing (`src/payment.py`)**
- Payment gateway integration
- Transaction handling
- Payment verification
- Refund processing
- Payment status tracking

**6. Route Graph (`src/route_graph.py`)**
- Graph-based route finding
- Station connectivity
- Distance calculation
- Route optimization

**7. Seat Allocation (`src/seat_allocation.py`)**
- Coach-wise seat allocation
- Berth assignment logic
- RAC handling
- Waitlist to confirmed conversion
- Dynamic seat release

**8. Queue Manager (`src/queue_manager.py`)**
- Waitlist queue management
- Priority handling
- Automatic upgrades
- Cancellation queue

**9. Utilities (`src/utils.py`)**
- Helper functions
- Train filtering
- Date/time utilities
- Fare calculation
- Validation functions

**10. Email Service (`src/email_service.py`)**
- Email notifications
- Booking confirmations
- Password reset emails
- Ticket delivery
- SMS notifications (future)

**11. PDF Generator (`src/pdf_routes.py`, `src/pdf_generator.py`)**
- Ticket PDF generation (ReportLab)
- QR code generation
- Booking receipt
- TDR forms

---

### **PART 5: Backend - Admin Operations** 🔧
**Technology:** Python 3.11, Flask, SQLAlchemy  
**Location:** `src/admin.py`

#### Admin Backend Features:

**Train Management:**
- Create, update, delete trains
- Manage train routes
- Platform assignments
- Schedule management

**Station Management:**
- CRUD operations for stations
- City/code management
- Station routing

**Booking Administration:**
- View all bookings
- Manual seat allocation
- Waitlist approval/rejection
- Chart preparation
- Emergency quota management

**Fare & Pricing:**
- Base fare management
- Dynamic pricing algorithms
- Seasonal adjustments
- Distance-based pricing
- Quota-specific fares

**Tatkal Administration:**
- Tatkal time slot configuration
- Override controls (enable/disable anytime)
- Train-specific overrides
- Class-specific overrides
- Expiry time settings

**User Management:**
- View all users
- Role assignment
- Account activation/deactivation
- Activity logs

**Reports & Analytics:**
- Booking statistics
- Revenue reports
- Occupancy rates
- Performance metrics
- Custom date range reports

**Customer Service:**
- PNR lookup
- Refund approvals
- Complaint resolution
- TDR processing

---

## Database Schema (`src/database.py`)

### Core Tables:
1. **user** - User accounts and authentication
2. **station** - Railway stations
3. **train** - Train information
4. **train_route** - Station sequences for each train
5. **booking** - Reservation records
6. **booking_passenger** - Passenger details
7. **payment** - Payment transactions
8. **waitlist** - Waitlist queue
9. **complaint_management** - User complaints
10. **tatkal_override** - Tatkal time override controls

---

## Entry Points

### Main Application
- **`main.py`** - Application entry point
  - Homepage route
  - Train search
  - PNR enquiry
  - Universal search
  - Complaint submission

### Database Initialization
- **`init_db.py`** - Database seeding script
  - Creates sample stations
  - Creates sample trains
  - Sets up routes
  - Creates admin user

---

## Configuration Files

- **`requirements.txt`** - Python dependencies
- **`pyproject.toml`** - Project metadata (UV package manager)
- **`uv.lock`** - Dependency lock file
- **`.gitignore`** - Git exclusions
- **`replit.md`** - Project documentation

---

## Key Technologies & Libraries

### Backend:
- **Flask** (3.1.2) - Web framework
- **Flask-SQLAlchemy** (3.1.1) - ORM
- **Flask-Login** (0.6.3) - Authentication
- **Flask-WTF** (1.2.2) - Form handling & CSRF
- **Gunicorn** (23.0.0) - Production server
- **psycopg2-binary** (2.9.10) - PostgreSQL adapter
- **ReportLab** (4.4.4) - PDF generation
- **QRCode** (8.2) - QR code generation
- **Werkzeug** (3.1.3) - Security utilities

### Frontend:
- **Bootstrap** - UI framework (via CDN)
- **Font Awesome** - Icons (via CDN)
- **Chart.js** - Data visualization (via CDN)
- **Feather Icons** - SVG icons (via CDN)

### Database:
- **PostgreSQL** (via Replit database)
- **SQLAlchemy** - ORM and query building

---

## Development Workflow

1. **Frontend Development:**
   - Edit templates in `templates/`
   - Modify styles in `static/css/`
   - Add interactions in `static/js/`

2. **Backend Development:**
   - Add routes in respective modules (`src/`)
   - Create/modify models in `src/models.py`
   - Update business logic in domain modules

3. **Database Changes:**
   - Modify models in `src/models.py`
   - Run database initialization: `python init_db.py`

4. **Testing:**
   - Start server: `gunicorn --bind 0.0.0.0:5000 main:app`
   - Access via browser
   - Check logs for errors

---

## API Structure

### Public Routes (No auth required):
- `/` - Homepage
- `/search_trains` - Train search
- `/pnr_enquiry` - PNR status
- `/search` - Universal train search
- `/auth/login` - User login
- `/auth/register` - User registration

### Protected Routes (Login required):
- `/booking/*` - Booking flow
- `/payment/*` - Payment processing
- `/profile` - User profile
- `/submit-complaint` - Complaint form

### Admin Routes (Admin role required):
- `/admin/*` - All admin pages
- `/admin/dashboard` - Admin dashboard
- `/admin/trains` - Train management
- `/admin/tatkal-override` - Tatkal override controls

---

## Security Features

- **Password Hashing:** Werkzeug security
- **CSRF Protection:** Flask-WTF
- **Session Management:** Flask-Login
- **Role-Based Access:** Custom decorators
- **SQL Injection Prevention:** SQLAlchemy ORM
- **XSS Protection:** Jinja2 auto-escaping

---

## Responsive Design Breakpoints

```css
/* Mobile Portrait */
@media (max-width: 480px) { ... }

/* Mobile Landscape / Small Tablets */
@media (max-width: 768px) { ... }

/* Tablets */
@media (max-width: 992px) { ... }

/* Large Screens */
@media (min-width: 1200px) { ... }
```

---

## Future Enhancements

1. **Real-time Features:**
   - WebSocket for live seat updates
   - Live train tracking

2. **Mobile App:**
   - React Native companion app
   - Progressive Web App (PWA)

3. **Advanced Analytics:**
   - ML-based demand forecasting
   - Revenue optimization

4. **Integration:**
   - SMS notifications (Twilio)
   - WhatsApp booking
   - Google Maps integration

---

## Project Statistics

- **Total Templates:** 40+
- **Backend Modules:** 11
- **Database Tables:** 10+
- **Admin Pages:** 20+
- **Lines of Code:** ~15,000+
- **Routes:** 50+

---

## Deployment

**Development Server:**
```bash
gunicorn --bind 0.0.0.0:5000 --reload main:app
```

**Production Server:**
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
```

---

## Support & Documentation

- **Main Documentation:** `PROJECT_DOCUMENTATION.dox`
- **File Documentation:** `PROJECT_FILE_DOCUMENTATION.md`
- **Final Review:** `FINAL_REVIEW.md`
- **README:** `README.md`

---

**End of Project Structure Document**
