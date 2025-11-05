# RailServe Developer Onboarding Guide

Welcome to the RailServe team! This guide will help you set up your development environment and start contributing.

---

## 🚀 Quick Start (5 minutes)

### **Prerequisites**
- Python 3.11+
- Git
- Text editor (VS Code recommended)
- Supabase account (free tier works)

### **Step 1: Clone the Repository**
```bash
git clone <repository-url>
cd railserve
```

### **Step 2: Set Up Environment Variables**
Create a `.env` file in the project root:

```env
# Required - Supabase PostgreSQL Connection
DATABASE_URL=postgresql://postgres.[YOUR-PROJECT]:

[YOUR-PASSWORD]@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres

# Optional - Session Security (auto-generated in development)
SESSION_SECRET=your-secret-key-here

# Optional - SMTP for Password Reset Emails
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**Get your Supabase credentials:**
1. Go to [supabase.com](https://supabase.com)
2. Create a new project (or use existing)
3. Go to **Settings → Database → Connection string**
4. Copy the **Session Pooler URI** (for IPv4 compatibility with Vercel)
5. Replace `[YOUR-PASSWORD]` with your database password

### **Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 4: Initialize the Database**
```bash
python init_supabase.py
```

This will create:
- ✅ 1,000 Indian railway stations
- ✅ 1,250 trains (Rajdhani, Shatabdi, Duronto, etc.)
- ✅ 12,479 route stops
- ✅ Admin user (username: `admin`, password: `admin123`)
- ✅ Tatkal time slots

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

### **Step 5: Run the Development Server**
```bash
python main.py
```

**Or (recommended for production-like testing):**
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port main:app
```

Open http://localhost:5000 in your browser.

---

## 🏗️ Development Workflow

### **1. Check Your Assignment**
Read `TEAM_ASSIGNMENT.md` to see:
- Your assigned features
- Files you'll be working on
- Your team members

### **2. Create a Feature Branch**
```bash
git checkout dev
git pull origin dev
git checkout -b frontend/your-feature-name
# or
git checkout -b backend/your-feature-name
```

**Branch naming convention:**
- `frontend/landing-page-search`
- `frontend/booking-flow-ui`
- `frontend/admin-dashboard`
- `backend/auth-system`
- `backend/seat-allocation`
- `backend/tatkal-pricing`

### **3. Make Your Changes**
- Follow the file structure in `FILE_STRUCTURE_GUIDE.md`
- Write clean, commented code
- Test your changes locally

### **4. Commit Your Code**
```bash
git add .
git commit -m "feat: add train search functionality"
```

**Commit message format:**
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation update
- `style:` formatting, no code change
- `refactor:` code restructuring
- `test:` adding tests
- `chore:` maintenance

### **5. Push and Create Pull Request**
```bash
git push origin frontend/your-feature-name
```

Then:
1. Go to GitHub
2. Click "New Pull Request"
3. Base: `dev`, Compare: `your-branch`
4. Add description of changes
5. Request review from teammates
6. Address feedback and merge

---

## 📂 Understanding the Codebase

### **Entry Point**
`main.py` → Flask app starts here

### **Application Structure**
```
main.py              # Routes: /, /search_trains, /pnr_enquiry
src/
  app.py             # Flask app factory, config, error handlers
  database.py        # SQLAlchemy db object
  models.py          # Database models (User, Train, Booking, etc.)
  
  # Blueprints (modular route groups)
  auth.py            # /auth/login, /auth/register, /auth/logout
  booking.py         # /booking/book, /booking/history
  payment.py         # /payment/process, /payment/success
  admin.py           # /admin/* (dashboard, reports, etc.)
  pdf_routes.py      # /pdf/ticket/<id>
  
  # Business Logic
  seat_allocation.py # Seat assignment algorithm
  queue_manager.py   # Waitlist management
  route_graph.py     # Train route validation
  utils.py           # Helper functions
  
templates/           # Jinja2 HTML templates
  base.html          # Master template (nav, footer, theme)
  index.html         # Homepage
  book_ticket.html   # Booking form
  admin/             # Admin panel templates
```

### **Database Models**
See `src/models.py` for all models:
- `User` - Authentication
- `Station` - 1,000 stations
- `Train` - 1,250 trains
- `TrainRoute` - Route graph
- `Booking` - Ticket reservations
- `Passenger` - Passenger details
- `Payment` - Transactions
- `Waitlist` - GNWL, RAC queue
- `SeatAvailability` - Real-time availability
- `DynamicPricing` - Surge pricing
- `TatkalTimeSlot` - Tatkal windows

See `DATABASE_SCHEMA.md` for complete schema.

---

## 🧪 Testing Your Changes

### **Manual Testing**
1. Start the server: `python main.py`
2. Open http://localhost:5000
3. Test your feature:
   - Click through the UI
   - Fill out forms
   - Check database changes

### **Admin Panel Access**
- Username: `admin`
- Password: `admin123`
- URL: http://localhost:5000/admin

### **Test User Registration**
1. Go to `/auth/register`
2. Create a test account
3. Login and test booking flow

### **Database Inspection**
```bash
python
>>> from src.app import app, db
>>> from src.models import Train, Station, Booking
>>> with app.app_context():
...     print(Train.query.count())  # Should be 1250
...     print(Station.query.count())  # Should be 1000
```

**Or use Supabase Dashboard:**
1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to **Table Editor**
4. Browse tables

---

## 🐛 Debugging Tips

### **Server Won't Start**
**Error:** `DATABASE_URL environment variable is required`
**Fix:** Add `DATABASE_URL` to `.env` file

**Error:** `ModuleNotFoundError: No module named 'flask'`
**Fix:** Run `pip install -r requirements.txt`

### **Database Errors**
**Error:** `relation "train" does not exist`
**Fix:** Run `python init_supabase.py` to create tables

**Error:** `duplicate key value violates unique constraint`
**Fix:** Database already initialized. Drop tables and re-run:
```bash
python
>>> from src.app import app, db
>>> with app.app_context():
...     db.drop_all()
...     db.create_all()
>>> exit()
python init_supabase.py
```

### **Template Not Updating**
**Issue:** HTML changes not reflecting
**Fix:** Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)

**Issue:** CSS/JS changes not showing
**Fix:** Clear browser cache or use incognito mode

### **Check Logs**
```bash
# Run with debug mode
FLASK_ENV=development python main.py
```

---

## 📝 Code Style Guidelines

### **Python**
```python
# Good
def book_ticket(train_id, user_id, passengers):
    """
    Create a new booking for a train.
    
    Args:
        train_id: Train ID
        user_id: User ID
        passengers: List of passenger dicts
    
    Returns:
        Booking object or None
    """
    booking = Booking(...)
    db.session.add(booking)
    db.session.commit()
    return booking

# Bad (no docstring, unclear names)
def bt(t, u, p):
    b = Booking(...)
    db.session.add(b)
    db.session.commit()
    return b
```

### **HTML/Jinja2**
```html
<!-- Good: Semantic HTML, clear structure -->
<div class="booking-form">
    <h2>Book Your Ticket</h2>
    <form method="POST" action="/booking/process">
        {{ form.hidden_tag() }}
        <div class="form-group">
            <label for="name">Passenger Name</label>
            <input type="text" id="name" name="name" required>
        </div>
        <button type="submit">Book Now</button>
    </form>
</div>

<!-- Bad: No structure, poor naming -->
<div class="d1">
    <form method="POST">
        <input type="text" name="n">
        <button>Submit</button>
    </form>
</div>
```

### **CSS** (Inline in `base.html`)
```css
/* Good: Mobile-first, clear naming */
.booking-form {
    padding: 1rem;
    background: white;
    border-radius: 8px;
}

@media (min-width: 768px) {
    .booking-form {
        padding: 2rem;
        max-width: 600px;
        margin: 0 auto;
    }
}

/* Bad: Desktop-first, unclear names */
.bf {
    padding: 40px;
}
```

---

## 🤝 Team Collaboration

### **Daily Standups**
- **Time:** 10:00 AM
- **Format:**
  - What I did yesterday
  - What I'm doing today
  - Any blockers

### **Code Reviews**
When reviewing PRs:
- ✅ Does it follow code style?
- ✅ Are there tests?
- ✅ Does it work as expected?
- ✅ Is the documentation updated?
- ✅ Are there any security issues?

### **Communication**
- **Slack:** #railserve-dev for questions
- **GitHub Issues:** Bug reports and feature requests
- **Pull Requests:** Code reviews and discussions

---

## 🔐 Security Best Practices

### **Never Commit Secrets**
```bash
# Bad - DON'T DO THIS
git add .env
git commit -m "add config"

# Good
# .env is in .gitignore
```

### **Use Environment Variables**
```python
# Good
db_password = os.environ.get('DATABASE_URL')

# Bad
db_password = 'hardcoded-password'
```

### **CSRF Protection**
```html
<!-- Good: Always include CSRF token in forms -->
<form method="POST">
    {{ form.hidden_tag() }}
    <!-- form fields -->
</form>

<!-- Bad: No CSRF protection -->
<form method="POST">
    <!-- form fields -->
</form>
```

### **SQL Injection Prevention**
```python
# Good: Use SQLAlchemy ORM
train = Train.query.filter_by(id=train_id).first()

# Bad: Raw SQL with string formatting
query = f"SELECT * FROM train WHERE id = {train_id}"
```

---

## 📚 Helpful Resources

### **Documentation**
- [Flask Docs](https://flask.palletsprojects.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Jinja2 Docs](https://jinja.palletsprojects.com/)
- [Supabase Docs](https://supabase.com/docs)
- [Python Docs](https://docs.python.org/3/)

### **Internal Docs**
- `TEAM_ASSIGNMENT.md` - Your role and files
- `FILE_STRUCTURE_GUIDE.md` - Complete file reference
- `ARCHITECTURE.md` - System design
- `DATABASE_SCHEMA.md` - Database tables
- `README.md` - Project overview

### **Sample Data**
After running `init_supabase.py`, you can:
- Login as admin (admin/admin123)
- Search trains between stations
- Test booking flow with real data
- View 1,000 stations in dropdowns
- See 1,250 trains in search results

---

## 🎯 Your First Task

**Frontend Members:**
1. Read `TEAM_ASSIGNMENT.md` for your assignment
2. Open your assigned template files
3. Understand the current UI structure
4. Make a small improvement (e.g., add a loading spinner)
5. Create a PR and get it reviewed

**Backend Members:**
1. Read `TEAM_ASSIGNMENT.md` for your assignment
2. Study `src/models.py` for relevant models
3. Understand the database schema
4. Write a simple helper function
5. Create a PR and get it reviewed

---

## ❓ Need Help?

### **Stuck on Setup?**
- Check `.env` file is configured correctly
- Verify `pip install -r requirements.txt` ran successfully
- Ensure Supabase project is active

### **Code Questions?**
- Read `FILE_STRUCTURE_GUIDE.md` for file explanations
- Check existing code for patterns
- Ask in #railserve-dev Slack channel

### **Git Issues?**
- `git status` to see current state
- `git log` to view commit history
- Ask team lead for help

---

**Welcome to the team! Happy coding! 🚀**

---

**Last Updated:** November 2025  
**Maintainers:** RailServe Team  
**Contact:** #railserve-dev on Slack
