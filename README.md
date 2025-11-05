# RailServe - Indian Railway Reservation System

A comprehensive railway ticket booking system with **1,000 real Indian railway stations** and **1,250 trains** including Rajdhani, Shatabdi, and Duronto Express services.

[![Flask](https://img.shields.io/badge/Flask-3.1+-green.svg)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Supabase](https://img.shields.io/badge/Database-Supabase-brightgreen.svg)](https://supabase.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ⚡ Quick Start

```bash
# 1. Clone and setup
git clone <repository-url>
cd railserve

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variable
export DATABASE_URL="your-supabase-connection-string"

# 4. Initialize database
python init_supabase.py

# 5. Run the application
python main.py
```

Open http://localhost:5000

**Admin Access:** `admin` / `admin123`

---

## 🌟 Key Features

### 🎫 For Users
- Search trains across **1,000 Indian railway stations**
- Real-time seat availability for all coach classes
- Multi-passenger booking with berth preferences
- Tatkal (last-minute) booking support
- Waitlist management (GNWL, RAC, PQWL, RLWL)
- PDF tickets with QR code verification
- PNR enquiry and booking history

### 👨‍💼 For Admins
- Comprehensive dashboard with analytics
- Train and station management (1,250 trains)
- Booking reports with CSV export
- Dynamic pricing and surge pricing
- Tatkal time slot configuration
- Complaint and refund management
- Performance metrics tracking

---

## 📊 Real Data

- **1,000 Stations**: Mumbai, Delhi, Chennai, Bangalore, Kolkata, and more
- **1,250 Trains**: Rajdhani, Shatabdi, Duronto, Mail/Express, Passenger
- **12,479 Route Stops**: Realistic multi-station routes
- **Authentic Pricing**: ₹0.30 - ₹3.50 per km based on train type

---

## 🏗️ Technology Stack

- **Backend:** Flask 3.1+, SQLAlchemy 2.0+, Gunicorn
- **Database:** Supabase PostgreSQL (managed, scalable)
- **Frontend:** Jinja2, HTML5/CSS3, JavaScript
- **PDF:** ReportLab, QRCode
- **Deployment:** Vercel Serverless

---

## 📚 Documentation

All documentation is in the `docs/` folder:

### Getting Started
- **[Quick Start Guide](docs/README_PROJECT.md)** - Complete setup instructions
- **[Developer Onboarding](docs/DEVELOPER_ONBOARDING.md)** - For new team members
- **[Team Assignment](docs/TEAM_ASSIGNMENT.md)** - Roles and responsibilities

### Architecture & Design
- **[System Architecture](docs/ARCHITECTURE.md)** - Complete system design
- **[Mind Map](docs/SYSTEM_MINDMAP.md)** - Visual system overview
- **[Booking Flowchart](docs/BOOKING_FLOWCHART.md)** - Process flows
- **[File Structure Guide](docs/FILE_STRUCTURE_GUIDE.md)** - Every file explained

### Database & Deployment
- **[Database Schema](docs/DATABASE_SCHEMA.md)** - All tables and relationships
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Vercel deployment
- **[Project Overview](docs/PROJECT_OVERVIEW.md)** - High-level overview

**→ [Complete Documentation Index](docs/INDEX.md)**

---

## 🎯 For Team Members

This project is designed for a **6-member team** (3 frontend, 3 backend):

1. **Frontend Member 1:** Landing page, search, PNR enquiry
2. **Frontend Member 2:** Booking flow, payments, user profile
3. **Frontend Member 3:** Admin dashboard and reports
4. **Backend Member 1:** Authentication and user management
5. **Backend Member 2:** Booking engine and seat allocation
6. **Backend Member 3:** Data management and system operations

**→ See [TEAM_ASSIGNMENT.md](docs/TEAM_ASSIGNMENT.md) for detailed assignments**

---

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Deploy to Vercel
vercel
```

Set environment variables in Vercel dashboard:
- `DATABASE_URL` - Supabase PostgreSQL connection string
- `SESSION_SECRET` - Random secret key
- `FLASK_ENV` - Set to `production`

**→ See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for details**

---

## 🔐 Environment Variables

Required:
- `DATABASE_URL` - Supabase PostgreSQL connection

Optional:
- `SESSION_SECRET` - Flask session key (auto-generated in dev)
- `SMTP_*` - Email configuration for password resets

---

## 📝 Project Structure

```
railserve/
├── main.py                 # Application entry point
├── init_supabase.py        # Database initialization
├── requirements.txt        # Python dependencies
├── vercel.json            # Vercel deployment config
├── src/                   # Source code
│   ├── app.py             # Flask app factory
│   ├── models.py          # Database models
│   ├── auth.py            # Authentication
│   ├── booking.py         # Booking logic
│   ├── payment.py         # Payment processing
│   ├── admin.py           # Admin panel
│   └── ...
├── templates/             # HTML templates
│   ├── base.html          # Master template
│   ├── index.html         # Homepage
│   ├── admin/             # Admin templates
│   └── ...
└── docs/                  # Documentation
    ├── README_PROJECT.md
    ├── ARCHITECTURE.md
    ├── TEAM_ASSIGNMENT.md
    └── ...
```

---

## 🧪 Testing

```bash
# Run development server
python main.py

# Access application
open http://localhost:5000

# Login as admin
Username: admin
Password: admin123
```

---

## 🤝 Contributing

1. Create a branch from `dev`
2. Make your changes
3. Test locally
4. Create a pull request
5. Request review from teammates

**→ See [DEVELOPER_ONBOARDING.md](docs/DEVELOPER_ONBOARDING.md) for workflow**

---

## 📞 Support

- **Documentation:** Check `docs/` folder
- **Issues:** Create a GitHub issue
- **Team:** Contact your team lead

---

## 📄 License

[Add your license here]

---

## 🙏 Acknowledgments

- Built with Flask, Supabase, and SQLAlchemy
- Inspired by Indian Railways (IRCTC)
- Real train and station data from publicly available sources

---

**Version:** 2.0 (Supabase PostgreSQL)  
**Team Size:** 6 members (3 frontend, 3 backend)  
**Last Updated:** November 2025

---

## 🔗 Quick Links

- [Complete Documentation](docs/INDEX.md)
- [System Architecture](docs/ARCHITECTURE.md)
- [Team Assignment](docs/TEAM_ASSIGNMENT.md)
- [Developer Guide](docs/DEVELOPER_ONBOARDING.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
