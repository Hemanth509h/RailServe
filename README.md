# RailServe - Professional Railway Reservation System

A comprehensive railway ticket booking system built with Flask, featuring **real-time seat availability displays** matching professional booking websites like IRCTC, advanced booking management, dynamic pricing, waitlist handling, and admin analytics.

## 🌟 Key Features

### Real-Time Seat Availability (NEW!)
- **Professional IRCTC-style seat availability tables** showing all coach classes
- Color-coded availability status (Available, RAC, Waitlist)
- Live updates for AC1, AC2, AC3, Sleeper, 2S, and Chair Car
- Detailed fare multipliers for each coach class
- Visual indicators matching real railway booking websites

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
- PostgreSQL database (or SQLite for development)
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd railserve
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   # Required for production
   export SESSION_SECRET="your-secure-random-key-here"
   export DATABASE_URL="postgresql://user:password@localhost:5432/railserve"
   
   # Optional: Set to 'production' in production environment
   export FLASK_ENV="development"
   ```

4. **Initialize database with 1500 trains and 1250 stations**
   ```bash
   python init_db.py
   ```
   
   This will create:
   - 1,250 railway stations across India
   - 1,500 trains with complete routes
   - Seat availability data for next 30 days
   - All 6 coach classes (AC1, AC2, AC3, SL, 2S, CC)
   - Admin user (username: `admin`, password: `admin123`)

5. **Run the application**
   
   **Development:**
   ```bash
   python main.py
   ```
   
   **Production:**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
   ```

6. **Access the application**
   
   Open your browser and navigate to: `http://localhost:5000`
   
   **Admin login:** `admin` / `admin123`

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

## 🎨 Professional Seat Availability Display

RailServe features a professional seat availability system matching real railway booking websites:

### Features
- **Table-based layout** with headers for Class, Type, Fare, and Availability
- **Color-coded rows**: Green (Available), Yellow (RAC), Red (Waitlist)
- **Formatted status badges**: AVAILABLE-###, RAC-##, WL-##
- **Real-time updates** as seats are booked
- **All coach classes** shown in one view
- **Legend footer** explaining the color codes

### Coach Classes
| Class | Name | Description |
|-------|------|-------------|
| AC1 | First AC | Premium air-conditioned class |
| AC2 | AC 2 Tier | Two-tier air-conditioned sleeper |
| AC3 | AC 3 Tier | Three-tier air-conditioned sleeper |
| SL | Sleeper | Non-AC sleeper class |
| 2S | 2nd Sitting | Second-class seating |
| CC | Chair Car | AC seating class |

## 🏗️ Project Structure

```
railserve/
├── src/                     # Application source code
│   ├── app.py              # Flask app initialization & database config
│   ├── models.py           # SQLAlchemy database models
│   ├── utils.py            # Utility functions (seat availability, etc)
│   ├── auth.py             # Authentication routes
│   ├── admin.py            # Admin panel routes
│   ├── booking.py          # Booking management
│   ├── payment.py          # Payment processing
│   ├── pdf_routes.py       # PDF ticket generation
│   └── pdf_generator.py    # PDF creation utilities
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Base template with navigation
│   ├── index.html          # Homepage with seat availability tables
│   ├── book_ticket.html    # Booking page with live availability
│   ├── search_results.html # Search results
│   └── ...
├── static/                 # Static assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Images and icons
├── doc/                    # Documentation
│   ├── PROJECT_DOCUMENTATION.dox
│   ├── PROJECT_STRUCTURE.md
│   ├── FINAL_REVIEW.md
│   └── PROJECT_FILE_DOCUMENTATION.md
├── main.py                # Application entry point
├── init_db.py             # Database initialization (1500 trains, 1250 stations)
├── requirements.txt       # Python dependencies
├── replit.md              # Project memory and preferences
└── README.md             # This file
```

## 🔒 Security

- **Session Secret:** Requires `SESSION_SECRET` environment variable in production
- **Password Hashing:** Bcrypt-based secure password storage
- **CSRF Protection:** Enabled globally for all forms via Flask-WTF
- **Secure Cookies:** HTTPOnly and SameSite attributes
- **SQL Injection Protection:** SQLAlchemy ORM with parameterized queries
- **Role-Based Access Control:** Admin, Super Admin, and User roles
- **Generic Error Messages:** Prevents user enumeration attacks

## 🗄️ Database Support

The application supports both PostgreSQL and SQLite:

- **PostgreSQL (Production):** Set `DATABASE_URL` environment variable
  ```bash
  export DATABASE_URL="postgresql://username:password@host:port/database"
  ```

- **SQLite (Development):** Automatically uses `local_railway.db` if no `DATABASE_URL` is set

### Database Initialization

The `init_db.py` script populates the database with realistic Indian railway data:

- **1,250 stations** across all major and minor cities
- **1,500 trains** with diverse types (Rajdhani, Shatabdi, Duronto, Express, etc.)
- **Routes** connecting major cities
- **30 days** of seat availability data
- **All 6 coach classes** with realistic capacity
- **Admin user** for immediate system access

## 🌐 Deployment

### Environment Setup

1. **Production environment variables:**
   ```bash
   export FLASK_ENV=production
   export SESSION_SECRET=$(openssl rand -hex 32)
   export DATABASE_URL="postgresql://..."
   ```

2. **Use production server:**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 main:app
   ```

### Deployment Platforms

#### Heroku
```bash
heroku create railserve
heroku addons:create heroku-postgresql
heroku config:set SESSION_SECRET=$(openssl rand -hex 32)
git push heroku main
heroku run python init_db.py
```

#### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "main:app"]
```

Build and run:
```bash
docker build -t railserve .
docker run -p 5000:5000 \
  -e DATABASE_URL="postgresql://..." \
  -e SESSION_SECRET="..." \
  railserve
```

#### Replit

This project is optimized for Replit:
1. Fork/import the repository
2. Set environment secrets in Replit
3. Click "Run" - the workflow is pre-configured
4. Database initializes automatically on first run

## 📚 Documentation

- **Complete API Documentation:** See `doc/PROJECT_DOCUMENTATION.dox`
- **Architecture Details:** See `doc/PROJECT_STRUCTURE.md`
- **Implementation Review:** See `doc/FINAL_REVIEW.md`
- **File Documentation:** See `doc/PROJECT_FILE_DOCUMENTATION.md`
- **Project Memory:** See `replit.md`

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

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📝 License

[Add your license here]

## 📧 Support

For issues and questions:
- Create an issue in the repository
- Check the documentation in the `doc/` folder
- Review the `replit.md` for project-specific details

---

**Built with ❤️ using Flask, SQLAlchemy, and Python**

### Recent Updates (October 2025)
- ✨ Added professional IRCTC-style seat availability tables
- ✨ Implemented real-time seat tracking across all coach classes
- ✨ Enhanced UI with color-coded availability indicators
- ✨ Expanded database to 1500 trains and 1250 stations
- ✨ Optimized database initialization with batch commits
- ✨ Added visual legends and improved booking flow
