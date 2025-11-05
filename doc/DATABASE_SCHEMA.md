# Database Schema Documentation

## Overview

The RailServe database uses **SQLite 3** and is managed by the Database API application. All database operations are performed through REST API endpoints.

## Database Location

- **File**: `database-api/railway.db`
- **Type**: SQLite 3
- **Auto-created**: Yes, on first API startup
- **Portable**: Yes, single file

## Core Tables

### User Table
Stores user authentication and profile information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique user identifier |
| username | VARCHAR(64) | UNIQUE, NOT NULL | Username for login |
| email | VARCHAR(120) | UNIQUE, NOT NULL | User email address |
| password_hash | VARCHAR(256) | NOT NULL | Hashed password |
| role | VARCHAR(20) | DEFAULT 'user' | User role (user/admin/super_admin) |
| active | BOOLEAN | DEFAULT TRUE | Account status |
| reset_token | VARCHAR(100) | | Password reset token |
| reset_token_expiry | DATETIME | | Token expiration time |
| created_at | DATETIME | DEFAULT NOW | Account creation timestamp |

**Relationships**:
- One-to-Many with Booking
- One-to-Many with Payment
- One-to-Many with TatkalTimeSlot

### Station Table
Railway stations information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique station identifier |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Station name |
| code | VARCHAR(10) | UNIQUE, NOT NULL | Station code (e.g., NDLS) |
| city | VARCHAR(50) | NOT NULL | City name |
| state | VARCHAR(50) | NOT NULL | State name |
| active | BOOLEAN | DEFAULT TRUE | Station operational status |
| created_at | DATETIME | DEFAULT NOW | Record creation time |

**Relationships**:
- One-to-Many with TrainRoute

### Train Table
Train information and capacity.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique train identifier |
| number | VARCHAR(10) | UNIQUE, NOT NULL | Train number |
| name | VARCHAR(100) | NOT NULL | Train name |
| total_seats | INTEGER | NOT NULL | Total seat capacity |
| available_seats | INTEGER | NOT NULL | Currently available seats |
| fare_per_km | FLOAT | NOT NULL | Base fare per kilometer |
| tatkal_seats | INTEGER | DEFAULT 0 | Tatkal quota seats |
| tatkal_fare_per_km | FLOAT | | Tatkal fare per kilometer |
| active | BOOLEAN | DEFAULT TRUE | Train operational status |
| created_at | DATETIME | DEFAULT NOW | Record creation time |

**Relationships**:
- One-to-Many with TrainRoute
- One-to-Many with Booking

### TrainRoute Table
Station sequences for each train.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique route identifier |
| train_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to train |
| station_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to station |
| sequence | INTEGER | NOT NULL | Station order in route |
| arrival_time | TIME | | Scheduled arrival time |
| departure_time | TIME | | Scheduled departure time |
| distance_from_start | FLOAT | NOT NULL | Distance in kilometers |

**Unique Constraint**: (train_id, sequence)

## Booking Tables

### Booking Table
Ticket reservation records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique booking identifier |
| pnr | VARCHAR(10) | UNIQUE, NOT NULL | 10-digit PNR number |
| user_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to user |
| train_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to train |
| from_station_id | INTEGER | FOREIGN KEY, NOT NULL | Origin station |
| to_station_id | INTEGER | FOREIGN KEY, NOT NULL | Destination station |
| journey_date | DATE | NOT NULL | Date of journey |
| passengers | INTEGER | NOT NULL | Number of passengers |
| total_amount | FLOAT | NOT NULL | Total fare amount |
| booking_type | VARCHAR(10) | DEFAULT 'general' | Booking type |
| quota | VARCHAR(20) | DEFAULT 'general' | Quota type |
| coach_class | VARCHAR(10) | DEFAULT 'SL' | Coach class (AC1/AC2/AC3/SL/2S/CC) |
| status | VARCHAR(20) | DEFAULT 'pending_payment' | Booking status |
| waitlist_type | VARCHAR(10) | DEFAULT 'GNWL' | Waitlist category |
| chart_prepared | BOOLEAN | DEFAULT FALSE | Chart preparation status |
| berth_preference | VARCHAR(20) | DEFAULT 'No Preference' | Preferred berth |
| booking_date | DATETIME | DEFAULT NOW | Booking timestamp |
| cancellation_charges | FLOAT | DEFAULT 0.0 | Cancellation fee |
| loyalty_discount | FLOAT | DEFAULT 0.0 | Loyalty discount applied |

**Status Values**: pending_payment, confirmed, waitlisted, cancelled, rac

### Passenger Table
Individual passenger details for each booking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique passenger identifier |
| booking_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to booking |
| name | VARCHAR(100) | NOT NULL | Passenger name |
| age | INTEGER | NOT NULL | Passenger age |
| gender | VARCHAR(10) | NOT NULL | Gender (Male/Female/Other) |
| id_proof_type | VARCHAR(20) | NOT NULL | ID proof type |
| id_proof_number | VARCHAR(50) | NOT NULL | ID proof number |
| seat_preference | VARCHAR(20) | DEFAULT 'No Preference' | Seat preference |
| coach_class | VARCHAR(10) | DEFAULT 'SL' | Coach class |
| seat_number | VARCHAR(20) | | Assigned seat number |
| berth_type | VARCHAR(20) | | Assigned berth type |

### Payment Table
Payment transaction records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique payment identifier |
| booking_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to booking |
| user_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to user |
| amount | FLOAT | NOT NULL | Payment amount |
| payment_method | VARCHAR(20) | NOT NULL | Payment method (card/upi/netbanking) |
| transaction_id | VARCHAR(50) | | Payment gateway transaction ID |
| status | VARCHAR(20) | DEFAULT 'pending' | Payment status |
| created_at | DATETIME | DEFAULT NOW | Payment initiation time |
| completed_at | DATETIME | | Payment completion time |

**Unique Constraint**: (booking_id, status) to prevent duplicate successful payments

### Waitlist Table
Waitlist queue management.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique waitlist identifier |
| booking_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to booking |
| train_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to train |
| journey_date | DATE | NOT NULL | Journey date |
| position | INTEGER | NOT NULL | Waitlist position |
| waitlist_type | VARCHAR(10) | DEFAULT 'GNWL' | Waitlist type |
| created_at | DATETIME | DEFAULT NOW | Waitlist entry time |

**Waitlist Types**: GNWL (General), RAC, PQWL, RLWL, TQWL

## Advanced Features Tables

### TatkalTimeSlot Table
Configuration for Tatkal booking time windows.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique timeslot identifier |
| name | VARCHAR(100) | NOT NULL | Timeslot name |
| coach_classes | VARCHAR(200) | | Comma-separated coach classes |
| open_time | TIME | NOT NULL | Tatkal opening time |
| close_time | TIME | | Tatkal closing time |
| days_before_journey | INTEGER | DEFAULT 1 | Days before journey |
| active | BOOLEAN | DEFAULT TRUE | Timeslot active status |
| created_at | DATETIME | DEFAULT NOW | Creation timestamp |
| created_by | INTEGER | FOREIGN KEY | Admin who created |

### TatkalOverride Table
Admin override controls for Tatkal restrictions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique override identifier |
| is_enabled | BOOLEAN | DEFAULT FALSE | Override active status |
| enabled_by | INTEGER | FOREIGN KEY, NOT NULL | Admin user ID |
| enabled_at | DATETIME | DEFAULT NOW | Override activation time |
| override_message | VARCHAR(200) | | Override message |
| coach_classes | VARCHAR(200) | | Affected coach classes |
| train_ids | TEXT | | Affected train IDs |
| valid_until | DATETIME | | Override expiry time |

### RefundRequest Table
TDR (Ticket Deposit Receipt) and refund management.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique refund identifier |
| booking_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to booking |
| user_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to user |
| reason | TEXT | NOT NULL | Refund reason |
| amount_paid | FLOAT | NOT NULL | Original amount paid |
| refund_amount | FLOAT | NOT NULL | Refund amount |
| cancellation_charges | FLOAT | DEFAULT 0.0 | Cancellation fee |
| tdr_number | VARCHAR(20) | UNIQUE, NOT NULL | TDR number |
| status | VARCHAR(20) | DEFAULT 'pending' | Refund status |
| filed_at | DATETIME | DEFAULT NOW | TDR filing time |
| processed_at | DATETIME | | Processing completion time |

### SeatAvailability Table
Real-time seat availability tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique availability identifier |
| train_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to train |
| from_station_id | INTEGER | FOREIGN KEY, NOT NULL | Origin station |
| to_station_id | INTEGER | FOREIGN KEY, NOT NULL | Destination station |
| journey_date | DATE | NOT NULL | Journey date |
| coach_class | VARCHAR(10) | NOT NULL | Coach class |
| quota | VARCHAR(20) | DEFAULT 'general' | Quota type |
| available_seats | INTEGER | DEFAULT 0 | Available seats count |
| waiting_list | INTEGER | DEFAULT 0 | Waitlist count |
| rac_seats | INTEGER | DEFAULT 0 | RAC seats count |
| last_updated | DATETIME | DEFAULT NOW | Last update timestamp |

### ComplaintManagement Table
Customer complaint and query management.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique complaint identifier |
| ticket_number | VARCHAR(20) | UNIQUE, NOT NULL | Complaint ticket number |
| user_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to user |
| booking_id | INTEGER | FOREIGN KEY | Related booking (optional) |
| category | VARCHAR(50) | NOT NULL | Complaint category |
| subcategory | VARCHAR(50) | | Complaint subcategory |
| priority | VARCHAR(10) | DEFAULT 'medium' | Priority level |
| subject | VARCHAR(200) | NOT NULL | Complaint subject |
| description | TEXT | NOT NULL | Detailed description |
| status | VARCHAR(20) | DEFAULT 'open' | Complaint status |
| assigned_to | INTEGER | FOREIGN KEY | Assigned admin |
| resolution | TEXT | | Resolution details |
| created_at | DATETIME | DEFAULT NOW | Complaint creation time |
| updated_at | DATETIME | DEFAULT NOW | Last update time |
| resolved_at | DATETIME | | Resolution time |

### PerformanceMetrics Table
Performance tracking for trains and routes.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique metric identifier |
| train_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to train |
| journey_date | DATE | NOT NULL | Journey date |
| on_time_percentage | FLOAT | DEFAULT 0.0 | On-time performance % |
| average_delay_minutes | INTEGER | DEFAULT 0 | Average delay in minutes |
| total_passengers | INTEGER | DEFAULT 0 | Total passenger count |
| revenue_generated | FLOAT | DEFAULT 0.0 | Revenue generated |
| cancellations | INTEGER | DEFAULT 0 | Cancellation count |
| waitlist_confirmed | INTEGER | DEFAULT 0 | Waitlist confirmations |
| created_at | DATETIME | DEFAULT NOW | Metric creation time |

### DynamicPricing Table
Dynamic pricing rules for demand-based fares.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique pricing identifier |
| train_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to train |
| coach_class | VARCHAR(10) | NOT NULL | Coach class |
| base_fare_multiplier | FLOAT | DEFAULT 1.0 | Base fare multiplier |
| surge_pricing_enabled | BOOLEAN | DEFAULT FALSE | Surge pricing status |
| demand_threshold_high | INTEGER | DEFAULT 80 | High demand threshold % |
| demand_threshold_medium | INTEGER | DEFAULT 50 | Medium demand threshold % |
| high_demand_multiplier | FLOAT | DEFAULT 1.5 | High demand multiplier |
| medium_demand_multiplier | FLOAT | DEFAULT 1.2 | Medium demand multiplier |
| active | BOOLEAN | DEFAULT TRUE | Pricing rule active status |
| created_at | DATETIME | DEFAULT NOW | Creation timestamp |

### PlatformManagement Table
Platform and track assignment management.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique platform identifier |
| station_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to station |
| platform_number | VARCHAR(10) | NOT NULL | Platform number |
| track_number | VARCHAR(10) | | Track number |
| platform_length | INTEGER | | Platform length (meters) |
| electrified | BOOLEAN | DEFAULT TRUE | Electrification status |
| status | VARCHAR(20) | DEFAULT 'active' | Platform status |
| facilities | TEXT | | Available facilities |
| wheelchair_accessible | BOOLEAN | DEFAULT FALSE | Accessibility status |
| created_at | DATETIME | DEFAULT NOW | Creation timestamp |

### LoyaltyProgram Table
Frequent traveler loyalty program.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique loyalty identifier |
| user_id | INTEGER | FOREIGN KEY, UNIQUE, NOT NULL | Reference to user |
| membership_number | VARCHAR(20) | UNIQUE, NOT NULL | Membership number |
| tier | VARCHAR(20) | DEFAULT 'Silver' | Membership tier |
| points_earned | INTEGER | DEFAULT 0 | Total points earned |
| points_redeemed | INTEGER | DEFAULT 0 | Points redeemed |
| total_journeys | INTEGER | DEFAULT 0 | Total journey count |
| total_distance | FLOAT | DEFAULT 0.0 | Total distance traveled |
| total_spent | FLOAT | DEFAULT 0.0 | Total amount spent |
| tier_valid_until | DATE | | Tier validity date |
| benefits_active | BOOLEAN | DEFAULT TRUE | Benefits active status |
| joined_date | DATETIME | DEFAULT NOW | Program join date |
| last_activity | DATETIME | DEFAULT NOW | Last activity timestamp |

**Tiers**: Silver, Gold, Platinum, Diamond

## Indexes

Recommended indexes for optimal performance:

```sql
CREATE INDEX idx_booking_pnr ON booking(pnr);
CREATE INDEX idx_booking_user ON booking(user_id);
CREATE INDEX idx_booking_journey_date ON booking(journey_date);
CREATE INDEX idx_train_number ON train(number);
CREATE INDEX idx_station_code ON station(code);
CREATE INDEX idx_user_username ON user(username);
CREATE INDEX idx_user_email ON user(email);
```

## Database Access

All database operations are performed through the REST API. Direct database access is not available.

### API Base URL
```
https://your-database-api.vercel.app/api
```

### Example Queries

**Get all stations**:
```
GET /api/stations
```

**Create booking**:
```
POST /api/bookings
{
  "user_id": 1,
  "train_id": 5,
  "from_station_id": 2,
  "to_station_id": 8,
  "journey_date": "2025-11-10",
  "passengers": 2,
  "total_amount": 1500.00
}
```

## Database Maintenance

### Backup
```bash
# Copy the database file
cp database-api/railway.db backup/railway_$(date +%Y%m%d).db
```

### Restore
```bash
# Replace current database with backup
cp backup/railway_20251105.db database-api/railway.db
```

### Size Monitoring
```bash
# Check database file size
ls -lh database-api/railway.db
```

## Migration Notes

- Database is auto-created on first API startup
- All tables are created using SQLAlchemy models
- No manual SQL migrations required
- Schema updates require API redeployment

---

**Database Type**: SQLite 3  
**ORM**: SQLAlchemy 2.0.43+  
**Access Method**: REST API Only  
**Auto-backup**: Via Git (if tracked)
