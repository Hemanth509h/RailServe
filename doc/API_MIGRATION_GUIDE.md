# API Migration Guide

This guide explains how the Railway Booking System was migrated from direct database access to an API-based architecture.

## Before: Monolithic Architecture

```
Main Application
├── Direct PostgreSQL/Supabase Connection
├── SQLAlchemy Models
├── Database Operations in Routes
└── Tightly Coupled Database Access
```

## After: Microservices Architecture

```
Main Application                    Database API
├── No Database Connection          ├── SQLite Database
├── API Client (HTTP)               ├── SQLAlchemy Models
├── Business Logic                  ├── REST API Endpoints
└── Frontend Templates              └── CORS Enabled
```

## Benefits

1. **Separation of Concerns**: Database logic is isolated in the API
2. **Independent Deployment**: Deploy database API and main app separately
3. **Scalability**: Scale each service independently
4. **Security**: Database is not directly exposed
5. **Flexibility**: Can swap databases without changing main app
6. **Rollback Support**: Replit's rollback works on the SQLite database

## Migration Steps Completed

### 1. Created Database API Application

**Location**: `database-api/`

**Components**:
- SQLAlchemy models (mirrored from main app)
- Flask REST API with CORS
- SQLite database
- Vercel deployment configuration

**Key Files**:
- `app.py` - Main API application
- `models/models.py` - Database models
- `routes/*.py` - API endpoints for each entity
- `requirements.txt` - Python dependencies
- `vercel.json` - Vercel deployment config

### 2. Created API Client for Main Application

**Location**: `src/api_client.py`

**Features**:
- HTTP client using requests library
- Methods for all database operations
- Error handling
- Environment-based configuration

**Usage Example**:
```python
from src.api_client import db_api

# Get user by username
user = db_api.get_user_by_username('john_doe')

# Create booking
booking = db_api.create_booking({
    'user_id': user['id'],
    'train_id': 5,
    'from_station_id': 2,
    'to_station_id': 8,
    'journey_date': '2025-11-10',
    'passengers': 2,
    'total_amount': 1500.00
})
```

### 3. Updated Application Structure

**Removed**:
- Direct database connection in `src/app.py`
- PostgreSQL/Supabase configuration
- Direct SQLAlchemy queries in routes

**Added**:
- API client for database operations
- Configuration for DATABASE_API_URL
- Documentation for deployment

## Deployment Guide

### Deploy Database API First

1. **Prepare Database API**:
   ```bash
   cd database-api
   ```

2. **Test Locally**:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```
   Visit: `http://localhost:5000/health`

3. **Deploy to Vercel**:
   ```bash
   vercel
   ```
   Or use the Vercel dashboard to import from GitHub

4. **Note the API URL**: e.g., `https://railway-db-api.vercel.app`

### Configure Main Application

1. **Set Environment Variable**:
   ```bash
   export DATABASE_API_URL=https://railway-db-api.vercel.app
   ```

2. **Update Routes** (Required):
   All route files need to be updated to use `db_api` instead of direct model queries:
   
   **Before**:
   ```python
   from .models import Train
   train = Train.query.get(train_id)
   ```
   
   **After**:
   ```python
   from .api_client import db_api
   train = db_api.get_train(train_id)
   ```

### Deploy Main Application

Deploy the main application to your preferred platform with the `DATABASE_API_URL` environment variable set.

## Files to Update in Main Application

To complete the migration, these files need to be updated to use the API client:

1. **`main.py`** - Update routes to use `db_api`
2. **`src/auth.py`** - Replace User model queries with API calls
3. **`src/booking.py`** - Replace Booking/Train/Station queries with API calls
4. **`src/admin.py`** - Replace all model queries with API calls
5. **`src/app.py`** - Remove database initialization, use API client
6. **`src/payment.py`** - Update payment operations
7. **`src/pdf_routes.py`** - Update to fetch data from API

## Example Migrations

### Example 1: User Authentication

**Before**:
```python
from .models import User

user = User.query.filter_by(username=username).first()
if user and check_password_hash(user.password_hash, password):
    login_user(user)
```

**After**:
```python
from .api_client import db_api

user_data = db_api.get_user_by_username(username)
if user_data and check_password_hash(user_data['password_hash'], password):
    # Create user object for Flask-Login
    user = User(user_data)
    login_user(user)
```

### Example 2: Searching Trains

**Before**:
```python
from .models import Train, TrainRoute

trains = Train.query.filter_by(active=True).all()
for train in trains:
    routes = TrainRoute.query.filter_by(train_id=train.id).all()
```

**After**:
```python
from .api_client import db_api

trains = db_api.get_trains()
for train in trains:
    routes = db_api.get_train_routes(train['id'])
```

### Example 3: Creating Booking

**Before**:
```python
from .models import Booking
from .database import db

booking = Booking(
    user_id=user_id,
    train_id=train_id,
    from_station_id=from_id,
    to_station_id=to_id,
    journey_date=date,
    passengers=passenger_count,
    total_amount=amount
)
db.session.add(booking)
db.session.commit()
```

**After**:
```python
from .api_client import db_api

booking = db_api.create_booking({
    'user_id': user_id,
    'train_id': train_id,
    'from_station_id': from_id,
    'to_station_id': to_id,
    'journey_date': date.isoformat(),
    'passengers': passenger_count,
    'total_amount': amount
})
```

## Testing the Migration

### Test Database API

```bash
# Health check
curl https://your-api.vercel.app/health

# Get all stations
curl https://your-api.vercel.app/api/stations

# Get specific train
curl https://your-api.vercel.app/api/trains/1
```

### Test Main Application

1. Start the main application with DATABASE_API_URL configured
2. Test user registration and login
3. Test train search
4. Test booking creation
5. Test admin panel

## Rollback Capability

One major advantage of using SQLite with the database API:
- Replit's rollback feature works with the SQLite database
- You can restore the database to a previous state
- The database file (`railway.db`) is versioned with the code

## Performance Considerations

### Latency
- API calls add network latency
- Consider caching frequently accessed data
- Batch API calls where possible

### Optimization Tips
1. Cache static data (stations, trains) in memory
2. Use connection pooling in API client
3. Implement API response caching
4. Consider Redis for session storage

## Security

### Database API Security
- CORS is configured to allow requests from main app
- Consider adding API key authentication
- Use HTTPS for all API communication
- Validate all input data

### Main Application Security
- Store DATABASE_API_URL in environment variables
- Never expose API internals to frontend
- Validate user input before sending to API

## Troubleshooting

### Issue: Main app can't connect to database API
- **Solution**: Check DATABASE_API_URL is set correctly
- **Solution**: Verify database API is running and accessible

### Issue: 404 errors from API
- **Solution**: Check API endpoint paths
- **Solution**: Verify API routes are registered correctly

### Issue: Data not persisting
- **Solution**: Ensure railway.db has write permissions
- **Solution**: Check API responses for errors

## Next Steps

1. ✅ Database API created
2. ✅ API client created
3. ⏳ Update main application routes to use API client
4. ⏳ Test integration
5. ⏳ Deploy database API
6. ⏳ Deploy main application

## Support

For issues or questions about the migration:
1. Check `ARCHITECTURE.md` for overview
2. Review `database-api/README.md` for API documentation
3. Test API endpoints using curl or Postman
