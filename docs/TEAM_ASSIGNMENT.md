# RailServe Team Assignment Guide

## Project Overview
RailServe is a comprehensive railway reservation system with **1,000 real Indian railway stations** and **1,250 trains** including Rajdhani, Shatabdi, and Duronto Express services. The system is built with Flask backend and Jinja2 templates, using Supabase PostgreSQL for the database.

## Team Structure (6 Members)

---

## 🎨 FRONTEND TEAM (3 Members)

### **Frontend Member 1: Landing & Search Interface**
**Responsibilities:**
- Homepage and train search functionality
- PNR enquiry interface
- Train listings and search results display
- Responsive navigation and theming

**Files to Work On:**
- `templates/index.html` - Homepage with search form
- `templates/search_results.html` - Train search results
- `templates/pnr_enquiry.html` - PNR status checker
- `templates/base.html` - Base template (coordinate changes with other frontend members)
- `main.py` (lines 30-160) - Homepage and search routes

**Key Features:**
- Train search between 1,000+ stations
- Real-time seat availability display
- Responsive mobile-first design
- Dark/light theme support

---

### **Frontend Member 2: Booking Flow & User Interface**
**Responsibilities:**
- Complete ticket booking user journey
- Seat selection and passenger details forms
- Payment success/failure pages
- User profile and booking history

**Files to Work On:**
- `templates/book_ticket.html` - Booking form
- `templates/seat_selection.html` - Seat/berth selection
- `templates/payment.html` - Payment interface
- `templates/payment_success.html` / `payment_failure.html` - Payment confirmation
- `templates/profile.html` - User profile
- `templates/booking_history.html` - Past bookings
- `src/booking.py` - Booking route logic

**Key Features:**
- Multi-passenger booking support
- Coach class selection (AC1, AC2, AC3, SL, 2S, CC)
- Berth preference (Lower, Middle, Upper, Side Lower, Side Upper)
- Tatkal booking support
- Waitlist management (GNWL, RAC, PQWL, RLWL)

---

### **Frontend Member 3: Admin Dashboard & Analytics**
**Responsibilities:**
- Admin control panel and analytics
- Train and station management interfaces
- Booking reports and revenue tracking
- Complaint management system

**Files to Work On:**
- `templates/admin/dashboard.html` - Main admin dashboard
- `templates/admin/trains.html` - Train management
- `templates/admin/stations.html` - Station management
- `templates/admin/booking_reports.html` - Booking analytics
- `templates/admin/analytics.html` - Revenue and performance metrics
- `templates/admin/complaint_management.html` - Support tickets
- `templates/admin/dynamic_pricing.html` - Fare management
- `templates/admin/tatkal_management.html` - Tatkal slot configuration
- `src/admin.py` - Admin route logic

**Key Features:**
- Real-time analytics dashboard
- Train route management
- Dynamic pricing controls
- Tatkal time slot management
- Complaint/ticket system
- Platform and quota management

---

## ⚙️ BACKEND TEAM (3 Members)

### **Backend Member 1: Authentication & User Management**
**Responsibilities:**
- User registration and login
- Password reset functionality
- Role-based access control (user, admin, super_admin)
- Session management

**Files to Work On:**
- `src/auth.py` - Authentication routes and logic
- `templates/login.html` - Login page
- `templates/register.html` - Registration page
- `templates/forgot_password.html` - Password reset request
- `templates/reset_password.html` - Password reset form
- `src/models.py` (User model, lines 8-37)

**Key Features:**
- Secure password hashing
- Email-based password reset
- CSRF protection
- Role-based dashboard access
- Session security (HTTPOnly cookies, CSRF tokens)

**Database Tables:**
- `user` - User accounts with roles

---

### **Backend Member 2: Booking & Seat Operations**
**Responsibilities:**
- Train search and availability logic
- Booking creation and management
- Seat allocation algorithms
- Waitlist and RAC management
- Payment processing
- PDF ticket generation

**Files to Work On:**
- `src/booking.py` - Booking routes and business logic
- `src/payment.py` - Payment processing
- `src/seat_allocation.py` - Seat assignment algorithm
- `src/queue_manager.py` - Waitlist management
- `src/pdf_generator.py` - Ticket PDF generation
- `src/pdf_routes.py` - PDF download routes
- `src/utils.py` - Helper functions (train search, availability)
- `src/models.py` (Booking, Passenger, SeatAvailability, Waitlist models)

**Key Features:**
- Real-time seat availability across 1,250 trains
- Multi-segment route availability checking
- Waitlist-to-confirmed auto-promotion
- PNR generation and tracking
- Seat number assignment (coach + berth)
- QR code ticket generation
- Cancellation and refund processing

**Database Tables:**
- `booking` - Ticket bookings
- `passenger` - Passenger details
- `seat_availability` - Real-time availability
- `waitlist` - Waitlist queue
- `payment` - Payment transactions
- `refund_request` - Cancellation requests

---

### **Backend Member 3: Data Management & Integrations**
**Responsibilities:**
- Train and station data management
- Route graph and distance calculations
- Tatkal booking time slot logic
- Dynamic pricing engine
- Performance metrics tracking
- Database initialization and migrations

**Files to Work On:**
- `src/route_graph.py` - Train route graph logic
- `init_supabase.py` - Database initialization script
- `src/models.py` (Station, Train, TrainRoute, TatkalTimeSlot, DynamicPricing models)
- `src/db_init/` folder (all files) - Database population scripts

**Key Features:**
- Graph-based route validation
- Distance calculation between stations
- Tatkal time window enforcement (AC: 10 AM, Non-AC: 11 AM)
- Surge pricing during peak demand
- Train performance tracking (on-time %, load factor)
- Real-time fare adjustments

**Database Tables:**
- `station` - 1,000 railway stations
- `train` - 1,250 trains with fares
- `train_route` - 12,479 route stops
- `tatkal_time_slot` - Tatkal booking windows
- `dynamic_pricing` - Fare surge rules
- `performance_metrics` - Train KPIs

---

## 🗂️ Shared Responsibilities

### **All Team Members:**
1. **Code Reviews:** Review pull requests from teammates
2. **Testing:** Write tests for your features
3. **Documentation:** Update documentation when making changes
4. **Communication:** Daily standups and progress updates
5. **Git Practices:** Follow branching strategy (see below)

---

## 🔄 Development Workflow

### **Branch Strategy:**
```
main (production-ready code)
 ├─ dev (integration branch)
     ├─ frontend/landing (Frontend Member 1)
     ├─ frontend/booking (Frontend Member 2)
     ├─ frontend/admin (Frontend Member 3)
     ├─ backend/auth (Backend Member 1)
     ├─ backend/booking (Backend Member 2)
     └─ backend/data (Backend Member 3)
```

### **Pull Request Process:**
1. Create feature branch from `dev`
2. Commit changes with clear messages
3. Push to your branch
4. Create PR to `dev` branch
5. Request review from at least 1 teammate
6. Address review comments
7. Merge after approval

---

## 📦 Database Schema Overview

**Core Tables:**
- `user` (authentication)
- `station` (1,000 stations)
- `train` (1,250 trains)
- `train_route` (12,479 stops)
- `booking` (ticket reservations)
- `passenger` (passenger details)
- `seat_availability` (real-time availability)
- `waitlist` (waiting list queue)
- `payment` (transactions)
- `refund_request` (cancellations)
- `tatkal_time_slot` (Tatkal windows)
- `dynamic_pricing` (surge pricing)
- `complaint_management` (support tickets)
- `performance_metrics` (train KPIs)

**See `DATABASE_SCHEMA.md` for complete schema details.**

---

## 🎯 Delivery Milestones

### **Week 1: Setup & Core Features**
- Frontend 1: Homepage + Search
- Frontend 2: Booking form UI
- Frontend 3: Admin dashboard layout
- Backend 1: Authentication complete
- Backend 2: Basic booking creation
- Backend 3: Database fully populated

### **Week 2: Integration & Advanced Features**
- Frontend 1-3: Connect all UIs to APIs
- Backend 1: Role-based access working
- Backend 2: Seat allocation + waitlist
- Backend 3: Tatkal + dynamic pricing

### **Week 3: Testing & Polish**
- All: Integration testing
- All: Bug fixes and UI polish
- All: Performance optimization
- All: Documentation complete

---

## 📞 Team Communication

### **Daily Standups:**
- **Time:** 10:00 AM
- **Duration:** 15 minutes
- **Format:** Yesterday's work, today's plan, blockers

### **Weekly Sprint Review:**
- **Time:** Friday 4:00 PM
- **Duration:** 1 hour
- **Format:** Demo features, retrospective, next sprint planning

### **Communication Channels:**
- **Slack:** #railserve-dev (general), #frontend, #backend
- **GitHub:** Issues and Pull Requests
- **Documentation:** This folder

---

## 🚀 Getting Started

1. **Read** `DEVELOPER_ONBOARDING.md` first
2. **Set up** your local environment
3. **Review** your assigned files
4. **Create** your feature branch
5. **Start** coding!

Need help? Contact the team lead or ask in #railserve-dev Slack channel.

---

## 📚 Key Documentation Files

- `DEVELOPER_ONBOARDING.md` - Setup guide
- `FILE_STRUCTURE_GUIDE.md` - Complete file explanations
- `ARCHITECTURE.md` - System architecture
- `DATABASE_SCHEMA.md` - Database design
- `README.md` - Project overview

---

**Last Updated:** November 2025  
**Project Status:** Active Development  
**Tech Stack:** Flask 3.1+, Supabase PostgreSQL, Jinja2, SQLAlchemy 2.0+
