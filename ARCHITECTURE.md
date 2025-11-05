# Railway Booking System - API-Based Architecture

## Overview

This railway booking system has been restructured into two separate applications:

1. **Main Application** (Current directory) - Frontend and business logic
2. **Database API** (`database-api/` folder) - SQLite database with REST API

## Architecture

```
┌─────────────────────┐
│  Main Application   │
│  (Flask Frontend)   │
│  Port: 5000        │
└──────────┬──────────┘
           │
           │ HTTP Requests
           │
           ▼
┌─────────────────────┐
│   Database API      │
│  (Flask REST API)   │
│  SQLite Database    │
│  Port: 5000        │
└─────────────────────┘
```

## Deployment Steps

### Step 1: Deploy Database API to Vercel

1. Navigate to the `database-api` folder
2. Deploy to Vercel:
   ```bash
   cd database-api
   vercel
   ```
3. Note the deployed URL (e.g., `https://your-api.vercel.app`)

### Step 2: Configure Main Application

1. Set the `DATABASE_API_URL` environment variable in your main application:
   ```
   DATABASE_API_URL=https://your-api.vercel.app
   ```

2. The main application will use the API client (`src/api_client.py`) to communicate with the database API

### Step 3: Deploy Main Application

Deploy the main application to your preferred hosting platform (Vercel, Railway, etc.)

## API Client Usage

The API client (`src/api_client.py`) provides methods to interact with the database API:

```python
from src.api_client import db_api

# Example: Get all trains
trains = db_api.get_trains()

# Example: Create a booking
booking_data = {
    'user_id': 1,
    'train_id': 5,
    'from_station_id': 2,
    'to_station_id': 8,
    'journey_date': '2025-11-10',
    'passengers': 2,
    'total_amount': 1500.00
}
booking = db_api.create_booking(booking_data)
```

## Database API Endpoints

See `database-api/README.md` for a complete list of available API endpoints.

## Development

### Local Development (Both Applications)

1. **Start Database API:**
   ```bash
   cd database-api
   pip install -r requirements.txt
   python app.py
   ```
   The API will run on `http://localhost:5000`

2. **Start Main Application (on different port):**
   ```bash
   # Set environment variable to point to local API
   export DATABASE_API_URL=http://localhost:5000
   
   # Run main app on different port
   python main.py
   ```

### Local Development (API Only)

If you only want to develop the database API:
```bash
cd database-api
pip install -r requirements.txt
python app.py
```

Test endpoints:
```bash
curl http://localhost:5000/health
curl http://localhost:5000/api/trains
```

## Migration Notes

### What Changed

1. **Database Connection Removed**: The main application no longer connects directly to PostgreSQL/Supabase
2. **Models Removed from Main App**: Database models are now only in the database API
3. **API Client Added**: New client (`src/api_client.py`) handles all database operations via HTTP
4. **SQLite Database**: The database API uses SQLite (stored in `railway.db`) instead of PostgreSQL

### Files Structure

**Main Application:**
- `src/api_client.py` - Client for database API communication
- `src/app.py` - Flask app (database config removed)
- `main.py` - Application entry point
- Routes: `src/auth.py`, `src/booking.py`, `src/admin.py` (need to be updated to use API client)

**Database API:**
- `database-api/app.py` - Flask API server
- `database-api/models/` - Database models
- `database-api/routes/` - API endpoints
- `database-api/railway.db` - SQLite database file

## Next Steps

1. Deploy the database API to Vercel
2. Update main application routes to use `db_api` client instead of direct model queries
3. Configure environment variables
4. Test the integration
5. Deploy the main application

## Environment Variables

### Database API
- `SECRET_KEY` - Flask secret key (optional)

### Main Application
- `DATABASE_API_URL` - URL of the deployed database API
- `SESSION_SECRET` - Flask session secret key

## Important Notes

- The database API uses SQLite, which is suitable for development and small-scale applications
- For production with high traffic, consider using PostgreSQL with the database API
- The `railway.db` file is created automatically when the API starts
- CORS is enabled on the database API to allow requests from the main application
