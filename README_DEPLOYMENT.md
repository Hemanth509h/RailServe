# RailServe - Railway Reservation System

## Quick Start Guide

### Local Development
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Initialize database:
   ```bash
   python init_db.py
   ```

3. Run the application:
   ```bash
   python main.py
   ```

4. Access the application at: `http://localhost:5000`

---

## Deployment Options

### ✅ Option 1: Replit (Recommended - Already Configured)
Your app is already configured to run on Replit with automatic PostgreSQL database support.

**Steps:**
1. Click the **Run** button in Replit
2. Database will be created automatically
3. Initialize database: `python init_db.py` in the Shell
4. Your app is live!

**To publish:**
- Click the **Publish** button in Replit to deploy to production

---

### 🚀 Option 2: Vercel (Serverless Deployment)

#### Prerequisites
- Vercel account (free): https://vercel.com
- PostgreSQL database (or use SQLite fallback)

#### Deployment Steps

**Via Vercel CLI:**
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel

# Set environment variables in Vercel dashboard:
# - DATABASE_URL (PostgreSQL connection string)
# - SESSION_SECRET (random secret key)
# - FLASK_ENV=production

# Deploy to production
vercel --prod

# Initialize database (run locally with production DATABASE_URL)
python init_db.py
```

**Via GitHub:**
1. Push code to GitHub
2. Import project in Vercel dashboard
3. Add environment variables
4. Deploy
5. Initialize database

📖 **Full Vercel deployment guide:** See `VERCEL_DEPLOYMENT_GUIDE.md`

---

## Database Configuration

### Automatic Fallback System
The app has built-in database fallback:
```
PostgreSQL (DATABASE_URL) → SQLite (if connection fails)
```

### Database Options

**1. PostgreSQL (Recommended for Production)**
- Replit built-in database (automatic)
- Neon (https://neon.tech) - Free tier
- Supabase (https://supabase.com) - Free tier
- Railway (https://railway.app) - Free tier

Set `DATABASE_URL` environment variable with your connection string.

**2. SQLite (Development/Fallback)**
- Automatically used if no DATABASE_URL is set
- File: `local_railway.db`
- Perfect for local development

### Database Initialization

After deployment, run:
```bash
python init_db.py
```

Or use the fallback-safe version:
```bash
python init_db_with_fallback.py
```

This creates:
- ✅ 1,000 railway stations
- ✅ 1,500 trains
- ✅ Train routes
- ✅ Seat availability data
- ✅ Admin user (username: `admin`, password: `admin123`)

---

## Environment Variables

Required for production:
```
DATABASE_URL=postgresql://user:pass@host:port/dbname
SESSION_SECRET=your-random-secret-key-here
FLASK_ENV=production
```

Optional:
```
FLASK_DEBUG=False
```

---

## Admin Access

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin123`

⚠️ **Change the password immediately after first login!**

Admin panel: `/admin`

---

## Features

- 🔍 Train search and booking
- 🎫 PNR enquiry
- 💳 Payment integration ready
- 📱 Responsive design
- 🌙 Dark mode support
- 🔐 Secure authentication
- 📊 Admin dashboard
- 📄 PDF ticket generation
- ⏰ Tatkal booking support
- 💺 Seat allocation system
- 📝 Complaint management

---

## Project Structure

```
railserve/
├── src/
│   ├── app.py              # Flask application
│   ├── models.py           # Database models
│   ├── auth.py             # Authentication
│   ├── booking.py          # Booking system
│   ├── admin.py            # Admin panel
│   └── ...
├── templates/              # HTML templates
├── static/                 # CSS, JS, images
├── main.py                 # Entry point
├── init_db.py              # Database initialization
├── init_db_with_fallback.py # DB init with fallback
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel configuration
└── README_DEPLOYMENT.md    # This file
```

---

## Troubleshooting

**App shows 500 error:**
- Check database connection
- Verify environment variables
- Check logs for specific errors

**Database connection timeout:**
- App will automatically fall back to SQLite
- Verify PostgreSQL connection string

**Database tables don't exist:**
- Run `python init_db.py`

**Static files not loading:**
- Check `vercel.json` configuration
- Verify static folder structure

---

## Support

- 📖 Full Vercel guide: `VERCEL_DEPLOYMENT_GUIDE.md`
- 🐛 Issues: Check application logs
- 💬 Questions: Review the documentation

---

## License

This project is for educational and demonstration purposes.

---

**Happy deploying! 🚂**
