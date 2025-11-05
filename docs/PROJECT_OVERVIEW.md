# RailServe - Railway Reservation System

## Project Overview

RailServe is a modern railway ticket booking system built with a **microservices architecture**, separating the frontend application from the database API for better scalability, security, and maintainability.

## Architecture

### Two-Application System

```
┌─────────────────────────────────┐
│   Main Application (Frontend)   │
│   - Flask web application       │
│   - User interface              │
│   - Business logic              │
│   - Templates & forms           │
│   - Port: 5000                  │
└────────────┬────────────────────┘
             │
             │ HTTP/REST API
             │
┌────────────▼────────────────────┐
│   Database API (Backend)        │
│   - Flask REST API              │
│   - SQLite database             │
│   - Data management             │
│   - CRUD operations             │
│   - Port: 5000                  │
└─────────────────────────────────┘
```

## Key Features

### User Features
- **Train Search** - Search trains between stations
- **Booking System** - Book tickets with passenger details
- **Tatkal Booking** - Last-minute ticket booking
- **Waitlist Management** - Automatic waitlist processing
- **PNR Enquiry** - Check booking status
- **Payment Integration** - Secure payment processing
- **Ticket PDF** - Download printable tickets
- **Complaint System** - File and track complaints

### Admin Features
- **Dashboard** - System analytics and metrics
- **Train Management** - Add/edit trains and routes
- **Station Management** - Manage railway stations
- **Booking Reports** - View booking analytics
- **Waitlist Control** - Manage waitlists
- **Dynamic Pricing** - Configure fare rules
- **Tatkal Management** - Control Tatkal time slots
- **User Management** - Manage user accounts
- **Performance Metrics** - Track system performance

## Technology Stack

### Main Application
- **Backend**: Flask 3.1.2+
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **Templates**: Jinja2
- **PDF Generation**: ReportLab
- **QR Codes**: qrcode library
- **HTTP Client**: requests (for API calls)

### Database API
- **Backend**: Flask 3.1.2+
- **Database**: SQLite 3
- **ORM**: SQLAlchemy 2.0.43+
- **CORS**: Flask-CORS
- **Deployment**: Vercel-ready

## Database Schema

The database API manages the following entities:

### Core Entities
- **User** - Authentication and user profiles
- **Station** - Railway stations (1,250+)
- **Train** - Train information (1,500+)
- **TrainRoute** - Station sequences for trains

### Booking Entities
- **Booking** - Ticket reservations with PNR
- **Passenger** - Individual passenger details
- **Payment** - Payment transactions
- **Waitlist** - Waitlist queue management

### Advanced Features
- **TatkalTimeSlot** - Tatkal booking windows
- **TatkalOverride** - Admin override controls
- **DynamicPricing** - Surge pricing rules
- **RefundRequest** - TDR and refund processing
- **ComplaintManagement** - Customer support
- **PerformanceMetrics** - KPI tracking
- **SeatAvailability** - Real-time seat tracking

## Deployment

### Database API Deployment
```bash
cd database-api
vercel deploy
```

### Main Application Deployment
Set `DATABASE_API_URL` environment variable and deploy to your preferred platform.

## Development Setup

### 1. Install Dependencies
```bash
# Main application
pip install -r requirements.txt

# Database API
cd database-api
pip install -r requirements.txt
```

### 2. Run Database API
```bash
cd database-api
python app.py
```

### 3. Run Main Application
```bash
export DATABASE_API_URL=http://localhost:5000
python main.py
```

## Environment Variables

### Main Application
- `DATABASE_API_URL` - URL of the database API (required)
- `SESSION_SECRET` - Flask session secret key
- `FLASK_ENV` - Environment (development/production)

### Database API
- `SECRET_KEY` - Flask secret key (optional)

## Project Structure

```
RailServe/
├── main.py                    # Main application entry
├── src/
│   ├── app.py                # Flask app configuration
│   ├── api_client.py         # Database API client
│   ├── auth.py               # Authentication routes
│   ├── booking.py            # Booking routes
│   ├── admin.py              # Admin routes
│   ├── payment.py            # Payment routes
│   ├── pdf_routes.py         # PDF generation
│   └── utils.py              # Utility functions
├── templates/                # HTML templates
├── database-api/             # Separate database API
│   ├── app.py               # API server
│   ├── models/              # Database models
│   ├── routes/              # API endpoints
│   └── requirements.txt     # API dependencies
└── doc/                      # Documentation

```

## Database File

The database API creates a SQLite database file:
- **Location**: `database-api/railway.db`
- **Auto-created**: Yes, on first run
- **Portable**: Yes, single file database
- **Backup**: Simply copy the .db file

## Security Features

- CSRF protection
- Password hashing (Werkzeug)
- Role-based access control
- Secure session management
- API isolation (database not directly exposed)
- HTTPS support (production)

## API Endpoints

The database API provides 50+ REST endpoints. See `database-api/README.md` for complete documentation.

## Documentation Files

- **DATABASE_API_SETUP.md** - Quick start guide
- **ARCHITECTURE.md** - System architecture
- **doc/API_MIGRATION_GUIDE.md** - Migration examples
- **database-api/README.md** - API documentation

## Support & Resources

- Check the documentation files for detailed guides
- Review API endpoints in `database-api/README.md`
- See migration examples in `doc/API_MIGRATION_GUIDE.md`

---

**Version**: 2.0 (API-Based Architecture)  
**Last Updated**: November 2025  
**Database**: SQLite 3  
**License**: Private
