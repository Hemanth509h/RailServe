# RailServe - Modern Railway Reservation System

A comprehensive railway ticket booking system built with Flask and Supabase PostgreSQL, featuring **1,000 real Indian railway stations** and **1,250 trains** including Rajdhani, Shatabdi, and Duronto Express services.

---

## 🌟 Key Features

### 🎫 User Features
- ✅ Train search across 1,000+ Indian railway stations (Mumbai, Delhi, Chennai, Bangalore, etc.)
- ✅ Real-time seat availability for all coach classes (AC1, AC2, AC3, SL, 2S, CC)
- ✅ Multi-passenger booking with berth preferences (Lower, Middle, Upper, Side Lower, Side Upper)
- ✅ Tatkal (last-minute) booking with time window enforcement
- ✅ Waitlist management (GNWL, RAC, PQWL, RLWL, TQWL)
- ✅ PNR enquiry and booking status tracking
- ✅ PDF ticket generation with QR code verification
- ✅ Secure payment processing
- ✅ User profile and booking history
- ✅ Complaint submission system
- ✅ Dark/light theme support with system preference detection

### 👨‍💼 Admin Features
- ✅ Comprehensive dashboard with revenue analytics
- ✅ Train and station management (1,250 trains, 1,000 stations)
- ✅ Route configuration with 12,479 route stops
- ✅ Booking reports with CSV export
- ✅ Dynamic pricing and surge pricing rules
- ✅ Tatkal time slot management (AC: 10 AM, Non-AC: 11 AM)
- ✅ Quota management (General, Ladies, Senior, Disability, Tatkal)
- ✅ Waitlist monitoring and chart preparation
- ✅ Complaint and refund management
- ✅ Performance metrics (on-time %, load factor, revenue)
- ✅ Platform allocation
- ✅ Role-based access control (user, admin, super_admin)

---

## 🏗️ Architecture

### Technology Stack
- **Backend:** Flask 3.1+ (Python 3.11+)
- **Database:** Supabase PostgreSQL (with Session Pooler for IPv4 compatibility)
- **ORM:** SQLAlchemy 2.0+
- **Frontend:** Jinja2 templates with inline CSS/JS
- **PDF Generation:** ReportLab + QRCode
- **Deployment:** Vercel (autoscale)

### System Design
```
┌──────────────────────────────────────────────────┐
│            Flask Application (main.py)            │
│                                                   │
│  ┌────────────┐  ┌──────────┐  ┌─────────────┐ │
│  │   Routes   │  │ Business │  │  Templates  │ │
│  │            │  │  Logic   │  │  (Jinja2)   │ │
│  │ main.py    │  │ booking  │  │             │ │
│  │ auth.py    │  │ payment  │  │ 100+ HTML   │ │
│  │ booking.py │  │ admin    │  │ templates   │ │
│  │ admin.py   │  │ pdf      │  │             │ │
│  └────────────┘  └──────────┘  └─────────────┘ │
│                                                   │
│              SQLAlchemy ORM (models.py)          │
│                       ↓                          │
└───────────────────────┼──────────────────────────┘
                        │
                        │ psycopg2 (PostgreSQL driver)
                        ↓
┌──────────────────────────────────────────────────┐
│         Supabase PostgreSQL Database             │
│                                                   │
│  • 1,000 stations (Mumbai, Delhi, Chennai...)    │
│  • 1,250 trains (Rajdhani, Shatabdi, Duronto)    │
│  • 12,479 route stops                            │
│  • Real-time booking and availability            │
│  • Transactions, constraints, indexes            │
└──────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Supabase account (free tier works)
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd railserve
```

### 2. Set Up Supabase Database

1. **Create Supabase Project:**
   - Go to [supabase.com](https://supabase.com)
   - Create a new project
   - Set a database password
   - Select a region (closest to your users)

2. **Get Database URL:**
   - Go to **Settings → Database → Connection string**
   - Copy the **Session Pooler** URI (for IPv4 compatibility)
   - It looks like:
     ```
     postgresql://postgres.[PROJECT-ID]:[PASSWORD]@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres
     ```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Required - Supabase PostgreSQL Connection
DATABASE_URL=postgresql://postgres.[YOUR-PROJECT]:[YOUR-PASSWORD]@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres

# Optional - Session Security (auto-generated in development)
SESSION_SECRET=your-secret-key-here

# Optional - SMTP for Password Reset Emails
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Initialize the Database
```bash
python init_supabase.py
```

**This creates:**
- ✅ 1,000 Indian railway stations
- ✅ 1,250 trains (Rajdhani, Shatabdi, Duronto, Mail/Express, Passenger)
- ✅ 12,479 route stops (avg 10 stops per train)
- ✅ Admin user (username: `admin`, password: `admin123`)
- ✅ Tatkal time slots (AC: 10:00 AM, Non-AC: 11:00 AM)

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

### 6. Run the Application
```bash
python main.py
```

**Or (recommended for production-like testing):**
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port main:app
```

Open http://localhost:5000 in your browser.

---

## 📦 Database Schema

### Core Tables

**user** - User accounts  
- Roles: user, admin, super_admin  
- Password hashing with Werkzeug  
- Email validation  

**station** - 1,000 railway stations  
- Name, code (e.g., "Mumbai Central", "BCT")  
- City, state  
- Active status  

**train** - 1,250 trains  
- Number, name (e.g., "12001", "Mumbai-Delhi Rajdhani Express")  
- Fare per km (₹0.30 - ₹3.50)  
- Tatkal fare multiplier (1.1x - 1.4x)  
- Total seats (400 - 1000 depending on train type)  

**train_route** - 12,479 route stops  
- Train-station relationships  
- Sequence, arrival/departure times  
- Distance from start (km)  

**booking** - Ticket reservations  
- PNR (unique 10-digit number)  
- Status: confirmed, waitlisted, RAC, cancelled  
- Coach class, quota, berth preference  
- Chart prepared flag  

**passenger** - Passenger details  
- Name, age, gender, ID proof  
- Seat number (e.g., "S1-45", "B2-32")  
- Berth type (Lower, Middle, Upper, Side Lower, Side Upper)  

**seat_availability** - Real-time availability  
- Per train route segment  
- Coach class and quota  
- Available seats, waitlist, RAC  

**waitlist** - Waitlist queue  
- Waitlist type (GNWL, RAC, PQWL, RLWL, TQWL)  
- Current status, position  
- Auto-confirmation when seats available  

**payment** - Transactions  
- Status: pending, success, failed  
- Amount, payment method  

**tatkal_time_slot** - Tatkal booking windows  
- AC classes: 10:00 AM  
- Non-AC classes: 11:00 AM  
- Days before journey: 1 day  

**dynamic_pricing** - Surge pricing  
- Multipliers based on demand  
- Special event pricing  

**complaint_management** - Support tickets  
- Status: pending, resolved  
- Admin responses  

**performance_metrics** - Train KPIs  
- On-time percentage  
- Load factor  
- Revenue tracking  

See `doc/DATABASE_SCHEMA.md` for complete schema with all fields and relationships.

---

## 📊 Real Data

### Trains by Type (1,250 total)

| Train Type       | Count | Base Fare (₹/km) | Tatkal Multiplier | Total Seats |
|------------------|-------|------------------|-------------------|-------------|
| Rajdhani Express | ~150  | 2.20             | 1.3x              | 400         |
| Shatabdi Express | ~200  | 2.80             | 1.3x              | 500         |
| Duronto Express  | ~100  | 1.75             | 1.3x              | 600         |
| Garib Rath       | ~100  | 1.20             | 1.2x              | 700         |
| Humsafar Express | ~80   | 1.60             | 1.25x             | 450         |
| Vande Bharat     | ~20   | 3.50             | 1.4x              | 400         |
| Tejas Express    | ~30   | 3.00             | 1.35x             | 400         |
| Mail/Express     | ~300  | 0.60             | 1.3x              | 1000        |
| Superfast        | ~200  | 0.80             | 1.3x              | 900         |
| Passenger        | ~70   | 0.30             | 1.1x              | 800         |

### Major Stations (93 of 1,000)
- **Mumbai:** Mumbai Central (BCT), Chhatrapati Shivaji Terminus (CSMT)
- **Delhi:** New Delhi (NDLS), Old Delhi (DLI)
- **Chennai:** Chennai Central (MAS)
- **Kolkata:** Howrah Junction (HWH)
- **Bangalore:** Bangalore City (SBC)
- **Hyderabad:** Hyderabad Deccan (HYB), Secunderabad (SC)
- **Pune:** Pune Junction (PUNE)
- **Ahmedabad:** Ahmedabad Junction (ADI)
- **And 83 more major stations + 907 additional stations**

---

## 🎨 Team Structure

This project is designed for a **6-member team** (3 frontend, 3 backend). See detailed assignments in:
- `TEAM_ASSIGNMENT.md` - Role responsibilities and file ownership
- `FILE_STRUCTURE_GUIDE.md` - Complete file reference
- `DEVELOPER_ONBOARDING.md` - Setup and development workflow

---

## 📚 Documentation

### Getting Started
- `README.md` (this file) - Project overview and quick start
- `DEVELOPER_ONBOARDING.md` - Setup guide for new developers
- `TEAM_ASSIGNMENT.md` - Team roles and responsibilities

### Technical Documentation
- `ARCHITECTURE.md` - System architecture and design decisions
- `FILE_STRUCTURE_GUIDE.md` - Complete file-by-file reference
- `doc/DATABASE_SCHEMA.md` - Database schema with all tables
- `doc/DEPLOYMENT_GUIDE.md` - Vercel deployment instructions

### Database
- `init_supabase.py` - Database initialization script
- Run `python init_supabase.py` to populate the database

---

## 🔐 Default Admin Access

After running `init_supabase.py`:
- **Username:** admin
- **Password:** admin123
- **URL:** http://localhost:5000/admin

**⚠️ Change this password in production!**

---

## 🛠️ Tech Stack Details

### Backend
- **Flask 3.1+** - Web framework
- **SQLAlchemy 2.0+** - ORM
- **psycopg2-binary** - PostgreSQL driver
- **Flask-Login** - Session management
- **Flask-WTF** - Forms and CSRF protection
- **Werkzeug** - Password hashing
- **Gunicorn** - Production WSGI server

### Frontend
- **Jinja2** - Template engine
- **HTML5/CSS3** - Modern, responsive UI
- **JavaScript** - Theme toggle, form validation
- **Inline Assets** - All CSS/JS embedded (no external files)

### Document Generation
- **ReportLab** - PDF generation
- **qrcode[pil]** - QR code creation
- **Pillow** - Image processing

### Utilities
- **Faker** - Test data generation
- **email-validator** - Email validation
- **requests** - HTTP client
- **python-dotenv** - Environment variables

---

## 🚀 Deployment (Vercel)

### Configure Deployment
The project includes `vercel.json` with deployment configuration:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python",
      "config": { "maxLambdaSize": "15mb" }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

### Deploy to Vercel
```bash
vercel
```

### Environment Variables in Vercel
Set these in Vercel dashboard → Settings → Environment Variables:
- `DATABASE_URL` - Your Supabase PostgreSQL connection string
- `SESSION_SECRET` - Random secret key for sessions
- `FLASK_ENV` - Set to `production`
- (Optional) SMTP variables for emails

---

## 📞 Support

### Admin Dashboard
Access at `/admin` after logging in as admin

### Troubleshooting
See `DEVELOPER_ONBOARDING.md` for common issues and solutions

### Database Issues
- **Tables don't exist:** Run `python init_supabase.py`
- **Duplicate data:** Drop tables and re-initialize
- **Connection errors:** Check `DATABASE_URL` in `.env`

---

## 🔄 Development Workflow

1. **Branch from `dev`:**
   ```bash
   git checkout dev
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and test:**
   ```bash
   python main.py
   ```

3. **Create Pull Request to `dev`:**
   - Request review from teammates
   - Address feedback
   - Merge after approval

See `DEVELOPER_ONBOARDING.md` for detailed workflow.

---

## 📝 License

[Add your license here]

---

## 🙏 Acknowledgments

- Built with Flask, Supabase, and SQLAlchemy
- Inspired by Indian Railways (IRCTC)
- Real train and station data from publicly available sources

---

**Last Updated:** November 2025  
**Version:** 2.0 (Supabase PostgreSQL)  
**Team Size:** 6 members (3 frontend, 3 backend)  
**Lines of Code:** ~15,000+
