# RailServe - Modern Railway Reservation System

A comprehensive railway ticket booking system built with a **microservices architecture**, featuring separate frontend and database API applications for better scalability, security, and maintainability.

## 🏗️ Architecture

This project consists of **two separate applications**:

1. **Main Application** - Frontend and business logic
2. **Database API** (`database-api/`) - SQLite database with REST API

```
Main Application  ←→  HTTP/REST  ←→  Database API (SQLite)
```

## 🌟 Key Features

### User Features
- ✅ User registration and secure authentication
- ✅ **Train search with live seat availability across all classes**
- ✅ Seat booking with multiple quotas (General, Ladies, Senior, Tatkal)
- ✅ **Real-time availability display** during booking flow
- ✅ PNR enquiry system with booking status
- ✅ Booking history and management
- ✅ PDF ticket generation with QR code verification
- ✅ Integrated payment processing
- ✅ Complaint submission and tracking
- ✅ Dark theme support with system preference detection

### Admin Features
- ✅ Comprehensive admin dashboard with analytics
- ✅ Train and station management (1500+ trains, 1250+ stations)
- ✅ Route configuration and scheduling
- ✅ Detailed booking reports with CSV export
- ✅ Waitlist management and automatic confirmation
- ✅ Dynamic pricing rules and surge pricing
- ✅ User management with role-based access
- ✅ Complaint management system
- ✅ Platform allocation and chart preparation
- ✅ Tatkal booking configuration

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Vercel account (for database API deployment)
- pip package manager

### 1. Deploy Database API

```bash
cd database-api
vercel deploy
```

Save the deployed URL (e.g., `https://railserve-db-api.vercel.app`)

### 2. Configure Environment Variables

```bash
export DATABASE_API_URL=https://your-database-api-url.vercel.app
export SESSION_SECRET=your-secret-key-here
export FLASK_ENV=production
```

### 3. Install Dependencies & Run

```bash
pip install -r requirements.txt
python main.py
```

### 4. Access the Application

Open your browser: `http://localhost:5000`

## 📚 Documentation

For detailed setup and deployment:

- **DATABASE_API_SETUP.md** - Quick setup guide
- **ARCHITECTURE.md** - System architecture
- **doc/DEPLOYMENT_GUIDE.md** - Deployment instructions
- **doc/DATABASE_SCHEMA.md** - Database documentation
- **doc/API_MIGRATION_GUIDE.md** - Migration guide
- **doc/PROJECT_OVERVIEW.md** - Project overview

## 📊 Database Schema

### Core Tables

**user** - User accounts and authentication
- Stores user credentials, roles (user/admin/super_admin)
- Password hashing with Werkzeug security
- Email validation and unique constraints

**station** - Railway stations (1250 stations)
- Station name, code, city, state
- Active status for enabling/disabling stations
- Indexed for fast lookups

**train** - Train information (1500 trains)
- Train number, name, total seats
- Fare per km, Tatkal configuration
- Active status and timestamps

**train_route** - Train routes and schedules
- Links trains to stations with sequence
- Arrival/departure times
- Distance calculations

**seat_availability** - Real-time seat tracking
- Per train, route segment, date, and coach class
- Tracks available seats, RAC, and waitlist
- Quota-based allocation (general, tatkal, ladies)
- **Updated in real-time** during bookings

**booking** - Ticket bookings
- PNR generation and status tracking
- Links to passengers, payments
- Cancellation and refund support

**passenger** - Passenger details
- Name, age, gender, berth preferences
- Seat number allocation
- Links to bookings

**payment** - Payment transactions
- Payment method, amount, status
- Transaction ID tracking
- Refund information

### Advanced Features Tables

**waitlist** - Waitlist management
- FIFO queue-based system
- Automatic confirmation on cancellations
- Priority handling

**tatkal_time_slot** - Tatkal booking windows
- Time-based availability windows
- Per-class configuration
- Admin-configurable

**dynamic_pricing** - Demand-based pricing
- Surge pricing multipliers
- Event-based pricing
- Per-train and per-date rules

**refund_request** - Cancellation handling
- Refund amount calculation
- Status tracking
- Admin approval workflow

**complaint_management** - Support tickets
- User complaints and queries
- Status tracking and resolution
- Admin response system

**performance_metrics** - KPI tracking
- On-time performance
- Train load factors
- Revenue analytics

## 📝 Environment Variables

### Main Application
| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_API_URL` | Yes | Database API URL |
| `SESSION_SECRET` | Yes | Session encryption key |
| `FLASK_ENV` | No | Environment mode (development/production) |

### Database API
| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | No | Flask secret key (auto-generated if not set) |

## 🏗️ Project Structure

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
    ├── PROJECT_OVERVIEW.md
    ├── DEPLOYMENT_GUIDE.md
    ├── DATABASE_SCHEMA.md
    └── API_MIGRATION_GUIDE.md
```

## 🔒 Security

- **API Isolation**: Database not directly exposed
- **Session Secret**: Required in production
- **Password Hashing**: Werkzeug-based secure storage
- **CSRF Protection**: Enabled via Flask-WTF
- **Role-Based Access**: Admin, Super Admin, User roles
- **HTTPS**: Support for production deployments

## 🗄️ Database

The database API uses **SQLite** stored in `database-api/railway.db`:

- **Portable**: Single file database
- **Auto-created**: On first API startup
- **No external database needed**: No Supabase or PostgreSQL required
- **API-based access**: All operations through REST endpoints

### Database File Location
```
database-api/railway.db
```

The database is automatically created with all required tables when the API starts.

## 🌐 Deployment

### Step 1: Deploy Database API to Vercel

```bash
cd database-api
vercel
```

### Step 2: Configure Main Application

Set environment variables:
```bash
DATABASE_API_URL=https://your-api.vercel.app
SESSION_SECRET=your-secret-key
FLASK_ENV=production
```

### Step 3: Deploy Main Application

Deploy to Vercel, Railway, or any Python hosting platform.

**See doc/DEPLOYMENT_GUIDE.md for detailed instructions**

## 🛠️ Technology Stack

### Main Application
- Flask 3.1.2+
- Flask-Login (authentication)
- Flask-WTF (forms & CSRF)
- ReportLab (PDF generation)
- requests (API client)

### Database API
- Flask 3.1.2+
- SQLite 3
- SQLAlchemy 2.0.43+
- Flask-CORS

## 🛠️ Development

### Running in Development Mode

```bash
export FLASK_ENV=development
python main.py
```

This will:
- Enable debug mode with hot-reload
- Auto-generate a session secret
- Use SQLite database by default
- Show detailed error pages

### Adding New Features

1. **Database Models:** Edit `src/models.py`
2. **Routes:** Add to appropriate blueprint (`src/booking.py`, `src/admin.py`, etc.)
3. **Templates:** Add to `templates/` directory
4. **Utilities:** Add helper functions to `src/utils.py`

### Testing

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest tests/
```

## 📈 Performance

- **Batch Database Operations:** Seat availability uses bulk inserts
- **Indexed Queries:** All foreign keys and lookups are indexed
- **Session Caching:** User data cached in Flask session
- **Optimized Queries:** Eager loading for related data
- **Production Server:** Gunicorn with worker processes

## 📄 License

Private - All rights reserved

## 🆘 Support

For detailed guides:
1. Read `DATABASE_API_SETUP.md` for quick start
2. Check `doc/DEPLOYMENT_GUIDE.md` for deployment help
3. Review `doc/API_MIGRATION_GUIDE.md` for examples

---

**Version**: 2.0 (API-Based Architecture)  
**Database**: SQLite 3  
**Last Updated**: November 2025
