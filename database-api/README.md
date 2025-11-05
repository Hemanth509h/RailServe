# Railway Database API

This is the database API for the Railway Booking System. It uses SQLite as the database and provides REST API endpoints for all database operations.

## Features

- SQLite database (railway.db)
- RESTful API endpoints
- CORS enabled for cross-origin requests
- Ready for Vercel deployment

## API Endpoints

### Users
- `GET /api/users` - Get all users
- `GET /api/users/<id>` - Get user by ID
- `GET /api/users/by-username/<username>` - Get user by username
- `GET /api/users/by-email/<email>` - Get user by email
- `POST /api/users` - Create new user
- `PUT /api/users/<id>` - Update user
- `DELETE /api/users/<id>` - Delete user

### Stations
- `GET /api/stations` - Get all stations
- `GET /api/stations/<id>` - Get station by ID
- `GET /api/stations/code/<code>` - Get station by code
- `POST /api/stations` - Create new station
- `PUT /api/stations/<id>` - Update station
- `DELETE /api/stations/<id>` - Delete station

### Trains
- `GET /api/trains` - Get all trains
- `GET /api/trains/<id>` - Get train by ID
- `GET /api/trains/number/<number>` - Get train by number
- `POST /api/trains` - Create new train
- `PUT /api/trains/<id>` - Update train
- `DELETE /api/trains/<id>` - Delete train

### Routes
- `GET /api/routes/train/<train_id>` - Get all routes for a train
- `POST /api/routes` - Create new route
- `PUT /api/routes/<id>` - Update route
- `DELETE /api/routes/<id>` - Delete route

### Bookings
- `GET /api/bookings` - Get all bookings
- `GET /api/bookings/<id>` - Get booking by ID
- `GET /api/bookings/pnr/<pnr>` - Get booking by PNR
- `POST /api/bookings` - Create new booking
- `PUT /api/bookings/<id>` - Update booking
- `GET /api/bookings/<id>/passengers` - Get passengers for booking
- `POST /api/bookings/<id>/passengers` - Add passenger to booking

### Payments
- `GET /api/payments` - Get all payments
- `GET /api/payments/<id>` - Get payment by ID
- `GET /api/payments/booking/<booking_id>` - Get payment by booking ID
- `POST /api/payments` - Create new payment
- `PUT /api/payments/<id>` - Update payment

### Waitlist
- `GET /api/waitlist` - Get all waitlist entries
- `GET /api/waitlist/booking/<booking_id>` - Get waitlist by booking ID
- `POST /api/waitlist` - Create new waitlist entry
- `PUT /api/waitlist/<id>` - Update waitlist entry
- `DELETE /api/waitlist/<id>` - Delete waitlist entry

### Tatkal
- `GET /api/tatkal/timeslots` - Get all tatkal timeslots
- `POST /api/tatkal/timeslots` - Create new tatkal timeslot
- `GET /api/tatkal/override` - Get tatkal override status
- `POST /api/tatkal/override` - Create tatkal override

### Refunds
- `GET /api/refunds` - Get all refunds
- `GET /api/refunds/<id>` - Get refund by ID
- `POST /api/refunds` - Create new refund request
- `PUT /api/refunds/<id>` - Update refund

### Complaints
- `GET /api/complaints` - Get all complaints
- `GET /api/complaints/<id>` - Get complaint by ID
- `POST /api/complaints` - Create new complaint
- `PUT /api/complaints/<id>` - Update complaint

### Performance
- `GET /api/performance/metrics` - Get performance metrics
- `POST /api/performance/metrics` - Create performance metrics
- `GET /api/performance/availability` - Get seat availability
- `POST /api/performance/availability` - Create seat availability
- `GET /api/performance/pricing` - Get dynamic pricing
- `POST /api/performance/pricing` - Create dynamic pricing

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Deployment to Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
vercel
```

## Database

The application uses SQLite database stored in `railway.db`. The database is automatically created on first run with all required tables.

## Environment Variables

- `SECRET_KEY` - Secret key for Flask (optional, defaults to 'database-api-secret-key-2025')
