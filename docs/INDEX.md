# RailServe Documentation Index

Complete navigation guide for all project documentation.

---

## 📋 Table of Contents

### 🚀 Getting Started
1. [README (Main)](../README.md) - Project overview and quick start
2. [Developer Onboarding](DEVELOPER_ONBOARDING.md) - Setup guide for new team members
3. [Project Overview](PROJECT_OVERVIEW.md) - High-level project description

### 👥 Team & Organization
4. [Team Assignment](TEAM_ASSIGNMENT.md) - Roles, responsibilities, and file ownership (6 members)
5. [File Structure Guide](FILE_STRUCTURE_GUIDE.md) - Complete file-by-file reference

### 🏗️ Architecture & Design
6. [System Architecture](ARCHITECTURE.md) - Complete architectural overview
7. [Mind Map](SYSTEM_MINDMAP.md) - Visual system overview (ASCII art)
8. [Booking Flowchart](BOOKING_FLOWCHART.md) - Process flow diagrams

### 💾 Database
9. [Database Schema](DATABASE_SCHEMA.md) - All tables, fields, and relationships
10. [init_supabase.py](../init_supabase.py) - Database initialization script

### 🚢 Deployment
11. [Deployment Guide](DEPLOYMENT_GUIDE.md) - Vercel deployment instructions
12. [README (Project)](README_PROJECT.md) - Full project documentation

---

## 📚 Documentation by Role

### For New Developers
**Start here if you're new to the project:**
1. ✅ [README (Main)](../README.md) - Overview
2. ✅ [Developer Onboarding](DEVELOPER_ONBOARDING.md) - Setup environment
3. ✅ [Team Assignment](TEAM_ASSIGNMENT.md) - Find your role
4. ✅ [File Structure Guide](FILE_STRUCTURE_GUIDE.md) - Understand the codebase

### For Frontend Developers
**Your primary documentation:**
1. [Team Assignment](TEAM_ASSIGNMENT.md) - Your assigned files
2. [File Structure Guide](FILE_STRUCTURE_GUIDE.md) - Template files explained
3. [Booking Flowchart](BOOKING_FLOWCHART.md) - User flows
4. [System Architecture](ARCHITECTURE.md) - Frontend layer overview

**Your files to work on:**
- **Member 1:** `templates/index.html`, `search_results.html`, `pnr_enquiry.html`
- **Member 2:** `templates/book_ticket.html`, `payment*.html`, `booking_history.html`
- **Member 3:** `templates/admin/*.html` (all admin templates)

### For Backend Developers
**Your primary documentation:**
1. [Team Assignment](TEAM_ASSIGNMENT.md) - Your assigned modules
2. [Database Schema](DATABASE_SCHEMA.md) - Tables and relationships
3. [System Architecture](ARCHITECTURE.md) - Business logic layer
4. [File Structure Guide](FILE_STRUCTURE_GUIDE.md) - Backend files explained

**Your files to work on:**
- **Member 1:** `src/auth.py`, `src/email_service.py`
- **Member 2:** `src/booking.py`, `src/payment.py`, `src/seat_allocation.py`, `src/queue_manager.py`
- **Member 3:** `src/admin.py`, `src/route_graph.py`, `init_supabase.py`

### For DevOps / Deployment
**Deployment documentation:**
1. [Deployment Guide](DEPLOYMENT_GUIDE.md) - Vercel setup
2. [README (Project)](README_PROJECT.md) - Environment variables
3. [System Architecture](ARCHITECTURE.md) - Deployment architecture section

### For Project Managers
**Management overview:**
1. [Project Overview](PROJECT_OVERVIEW.md) - High-level summary
2. [Team Assignment](TEAM_ASSIGNMENT.md) - Team structure and milestones
3. [Mind Map](SYSTEM_MINDMAP.md) - Visual system overview
4. [System Architecture](ARCHITECTURE.md) - Complete system design

---

## 📖 Documentation by Topic

### Authentication & Security
- [Team Assignment](TEAM_ASSIGNMENT.md) - Backend Member 1 section
- [System Architecture](ARCHITECTURE.md) - Security Architecture section
- [File Structure Guide](FILE_STRUCTURE_GUIDE.md) - `src/auth.py` details

### Booking System
- [Booking Flowchart](BOOKING_FLOWCHART.md) - Complete booking flow
- [Team Assignment](TEAM_ASSIGNMENT.md) - Backend Member 2 section
- [Database Schema](DATABASE_SCHEMA.md) - Booking tables

### Database Setup
- [Developer Onboarding](DEVELOPER_ONBOARDING.md) - Database initialization
- [Database Schema](DATABASE_SCHEMA.md) - Complete schema
- [README (Project)](README_PROJECT.md) - Supabase setup

### Admin Features
- [Team Assignment](TEAM_ASSIGNMENT.md) - Frontend Member 3 & Backend Member 3
- [File Structure Guide](FILE_STRUCTURE_GUIDE.md) - Admin files
- [System Architecture](ARCHITECTURE.md) - Admin layer

### Train & Station Data
- [Database Schema](DATABASE_SCHEMA.md) - Station and Train tables
- [README (Project)](README_PROJECT.md) - Real data section
- `init_supabase.py` - Data population script

### Payment Processing
- [Booking Flowchart](BOOKING_FLOWCHART.md) - Payment flow
- [Team Assignment](TEAM_ASSIGNMENT.md) - Backend Member 2
- [File Structure Guide](FILE_STRUCTURE_GUIDE.md) - `src/payment.py`

### Seat Allocation
- [Booking Flowchart](BOOKING_FLOWCHART.md) - Seat allocation algorithm
- [Team Assignment](TEAM_ASSIGNMENT.md) - Backend Member 2
- [System Architecture](ARCHITECTURE.md) - Business logic layer

### Waitlist Management
- [Booking Flowchart](BOOKING_FLOWCHART.md) - Waitlist auto-confirmation
- [Database Schema](DATABASE_SCHEMA.md) - Waitlist table
- [File Structure Guide](FILE_STRUCTURE_GUIDE.md) - `src/queue_manager.py`

### Tatkal Booking
- [Booking Flowchart](BOOKING_FLOWCHART.md) - Tatkal flow
- [Database Schema](DATABASE_SCHEMA.md) - TatkalTimeSlot table
- [Team Assignment](TEAM_ASSIGNMENT.md) - Backend Member 3

### Dynamic Pricing
- [System Architecture](ARCHITECTURE.md) - Dynamic pricing section
- [Database Schema](DATABASE_SCHEMA.md) - DynamicPricing table
- [Team Assignment](TEAM_ASSIGNMENT.md) - Backend Member 3

---

## 🔍 Quick Reference

### File Locations
- **Source Code:** `src/` directory
- **Templates:** `templates/` directory
- **Documentation:** `docs/` directory (this folder)
- **Database Init:** `init_supabase.py` (root)
- **Main Entry:** `main.py` (root)

### Common Tasks
- **Setup Environment:** [Developer Onboarding](DEVELOPER_ONBOARDING.md)
- **Initialize Database:** Run `python init_supabase.py`
- **Find Your Files:** [Team Assignment](TEAM_ASSIGNMENT.md)
- **Understand a File:** [File Structure Guide](FILE_STRUCTURE_GUIDE.md)
- **Deploy:** [Deployment Guide](DEPLOYMENT_GUIDE.md)

### Database Info
- **Tables:** 18 total (see [Database Schema](DATABASE_SCHEMA.md))
- **Stations:** 1,000 Indian railway stations
- **Trains:** 1,250 trains with real routes
- **Route Stops:** 12,479 stops (avg 10 per train)

### Team Info
- **Total Members:** 6 (3 frontend, 3 backend)
- **Assignments:** [Team Assignment](TEAM_ASSIGNMENT.md)
- **Workflow:** [Developer Onboarding](DEVELOPER_ONBOARDING.md) - Development Workflow section

---

## 📊 Documentation Statistics

- **Total Documentation Files:** 12
- **Total Words:** ~50,000+
- **Code Files Documented:** 100+
- **Database Tables Documented:** 18
- **Team Member Assignments:** 6

---

## 🔗 External Resources

### Flask Documentation
- [Flask Docs](https://flask.palletsprojects.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Jinja2 Docs](https://jinja.palletsprojects.com/)

### Database
- [Supabase Docs](https://supabase.com/docs)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

### Deployment
- [Vercel Docs](https://vercel.com/docs)

---

## ❓ Need Help?

### Can't Find What You Need?
1. Use browser search (Ctrl+F / Cmd+F) within documentation files
2. Check the [File Structure Guide](FILE_STRUCTURE_GUIDE.md) for file-specific info
3. Ask in team chat or create a GitHub issue

### Quick Answer Guide
- **"How do I set up the project?"** → [Developer Onboarding](DEVELOPER_ONBOARDING.md)
- **"What files do I work on?"** → [Team Assignment](TEAM_ASSIGNMENT.md)
- **"How does booking work?"** → [Booking Flowchart](BOOKING_FLOWCHART.md)
- **"What's the database structure?"** → [Database Schema](DATABASE_SCHEMA.md)
- **"How do I deploy?"** → [Deployment Guide](DEPLOYMENT_GUIDE.md)
- **"Where is this file?"** → [File Structure Guide](FILE_STRUCTURE_GUIDE.md)

---

**Last Updated:** November 2025  
**Maintained By:** RailServe Team  
**Total Pages:** 12 documentation files
