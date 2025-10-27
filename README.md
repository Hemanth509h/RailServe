# RailServe - Modern Railway Reservation System

A comprehensive railway ticket booking system built with Flask, featuring advanced booking management, dynamic pricing, and admin analytics.

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- PostgreSQL (or SQLite for development)

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
   
   # Optional: Set to 'production' in production
   export FLASK_ENV="development"
   ```

4. **Initialize database**
   ```bash
   python init_db.py
   ```

5. **Run the application**
   
   **Development:**
   ```bash
   python main.py
   ```
   
   **Production:**
   ```bash
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

6. **Access the application**
   
   Open your browser and navigate to: `http://localhost:5000`

## 📋 Features

### User Features
- ✅ User registration and authentication
- ✅ Train search by route and date
- ✅ Seat booking with multiple quotas (General, Ladies, Senior, Tatkal)
- ✅ PNR enquiry system
- ✅ Booking history and management
- ✅ PDF ticket generation with QR code
- ✅ Payment processing
- ✅ Complaint submission system
- ✅ Dark theme support

### Admin Features
- ✅ Comprehensive admin dashboard
- ✅ Train and station management
- ✅ Route configuration
- ✅ Booking reports and analytics
- ✅ Waitlist management
- ✅ Dynamic pricing rules
- ✅ User management
- ✅ Complaint management
- ✅ Platform allocation
- ✅ Chart preparation

## 🏗️ Project Structure

```
railserve/
├── src/                     # Application source code
│   ├── app.py              # Flask app initialization
│   ├── models.py           # Database models
│   ├── auth.py             # Authentication routes
│   ├── admin.py            # Admin panel routes
│   ├── booking.py          # Booking management
│   ├── payment.py          # Payment processing
│   └── ...
├── templates/              # HTML templates
├── static/                 # CSS, JS, images
├── main.py                # Application entry point
├── init_db.py             # Database initialization
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔒 Security

- **Session Secret:** The application requires a `SESSION_SECRET` environment variable in production
- **Password Hashing:** All passwords are securely hashed using Werkzeug
- **CSRF Protection:** Enabled globally for all forms
- **Secure Cookies:** HTTPOnly and SameSite attributes set
- **SQL Injection Protection:** Using SQLAlchemy ORM

## 🗄️ Database

The application supports both PostgreSQL and SQLite:

- **PostgreSQL (Production):** Set `DATABASE_URL` to your PostgreSQL connection string
- **SQLite (Development):** Automatically uses `local_railway.db` if `DATABASE_URL` is not set

### Database Schema

Key tables:
- `user` - User accounts and authentication
- `station` - Railway stations
- `train` - Train information
- `train_route` - Train routes with stations
- `booking` - Ticket bookings
- `payment` - Payment transactions
- `waitlist` - Waitlist management
- `complaint_management` - User complaints

## 🌐 Running Outside Replit

This application is designed to run anywhere Python is supported:

1. Ensure all environment variables are properly set
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Configure a reverse proxy (Nginx, Apache) if needed
4. Set up SSL/TLS certificates for HTTPS

### Example with Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📚 Documentation

- **Complete Documentation:** See `PROJECT_DOCUMENTATION.dox`
- **Final Review:** See `FINAL_REVIEW.md`
- **Project Notes:** See `replit.md`

## 🛠️ Development

### Running in Development Mode

```bash
export FLASK_ENV=development
python main.py
```

This will:
- Enable debug mode
- Auto-generate a session secret
- Use SQLite database by default
- Enable hot-reload for code changes

### Running Tests

```bash
# Add your test commands here
pytest
```

## 🚢 Deployment

### Heroku

```bash
heroku create railserve
heroku addons:create heroku-postgresql
heroku config:set SESSION_SECRET=$(openssl rand -hex 32)
git push heroku main
```

### Docker

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
```

Build and run:
```bash
docker build -t railserve .
docker run -p 5000:5000 \
  -e DATABASE_URL="postgresql://..." \
  -e SESSION_SECRET="..." \
  railserve
```

## 📝 License

[Add your license here]

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please create an issue in the repository.

---

**Built with ❤️ using Flask and Python**
