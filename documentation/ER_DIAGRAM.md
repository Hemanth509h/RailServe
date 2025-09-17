# RailServe - Entity Relationship Diagram

## Database Schema Overview

```
                                    RAILSERVE RAILWAY RESERVATION SYSTEM
                                           Entity Relationship Diagram

    ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
    │      USER       │         │     STATION     │         │      TRAIN      │
    ├─────────────────┤         ├─────────────────┤         ├─────────────────┤
    │ 🔑 id (PK)      │         │ 🔑 id (PK)      │         │ 🔑 id (PK)      │
    │ username        │         │ code            │         │ number          │
    │ email           │         │ name            │         │ name            │
    │ password_hash   │         │ city            │         │ total_seats     │
    │ role            │         │ state           │         │ available_seats │
    │ active          │         │ active          │         │ fare_per_km     │
    │ created_at      │         │ created_at      │         │ tatkal_seats    │
    └─────────────────┘         └─────────────────┘         │ tatkal_fare_km  │
             │                           │                   │ active          │
             │                           │                   │ created_at      │
             │                           │                   └─────────────────┘
             │                           │                            │
             │                           │                            │
             │            ┌─────────────────────────────────────────────┘
             │            │                              │
             │            │               ┌─────────────────┐
             │            │               │  TRAIN_ROUTE    │
             │            │               ├─────────────────┤
             │            │               │ 🔑 id (PK)      │
             │            │               │ 🔗 train_id(FK) │
             │            └──────────────▶│ 🔗 station_id   │
             │                            │ sequence        │
             │                            │ arrival_time    │
             │                            │ departure_time  │
             │                            │ distance_start  │
             │                            └─────────────────┘
             │
             │
             │          ┌─────────────────┐                  ┌─────────────────┐
             │          │    BOOKING      │                  │    PASSENGER    │
             │          ├─────────────────┤                  ├─────────────────┤
             │          │ 🔑 id (PK)      │                  │ 🔑 id (PK)      │
             │          │ pnr             │◄─────────────────┤ 🔗 booking_id   │
             └─────────▶│ 🔗 user_id (FK) │                  │ name            │
                        │ 🔗 train_id     │                  │ age             │
                        │ 🔗 from_stn_id  │                  │ gender          │
                        │ 🔗 to_stn_id    │                  │ id_proof_type   │
                        │ journey_date    │                  │ id_proof_number │
                        │ passengers      │                  │ seat_preference │
                        │ total_amount    │                  └─────────────────┘
                        │ booking_type    │
                        │ quota           │
                        │ status          │          ┌─────────────────┐
                        │ booking_date    │          │    PAYMENT      │
                        └─────────────────┘          ├─────────────────┤
                                 │                   │ 🔑 id (PK)      │
                                 │                   │ 🔗 booking_id   │
                                 └──────────────────▶│ 🔗 user_id      │
                                                     │ amount          │
                                                     │ payment_method  │
                                                     │ transaction_id  │
                                                     │ status          │
                                                     │ created_at      │
                                                     │ completed_at    │
                                                     └─────────────────┘

                        ┌─────────────────┐
                        │    WAITLIST     │
                        ├─────────────────┤
                        │ 🔑 id (PK)      │
                        │ 🔗 booking_id   │
                        │ 🔗 train_id     │
                        │ journey_date    │
                        │ position        │
                        │ created_at      │
                        └─────────────────┘
```

## Table Relationships

### **Primary Relationships**

1. **USER → BOOKING** (1:M)
   - One user can have multiple bookings
   - Cascade: ON DELETE RESTRICT (preserve booking history)

2. **TRAIN → BOOKING** (1:M)
   - One train can have multiple bookings
   - Cascade: ON DELETE RESTRICT (data integrity)

3. **STATION → BOOKING** (1:M)
   - One station can be source/destination for multiple bookings
   - Foreign Keys: from_station_id, to_station_id

4. **BOOKING → PASSENGER** (1:M)
   - One booking can have multiple passengers
   - Cascade: ON DELETE CASCADE (remove passengers with booking)

5. **BOOKING → PAYMENT** (1:1)
   - One booking has one payment record
   - Cascade: ON DELETE CASCADE

6. **BOOKING → WAITLIST** (1:1)
   - One booking may have one waitlist entry
   - Cascade: ON DELETE CASCADE

### **Route Relationships**

7. **TRAIN → TRAIN_ROUTE** (1:M)
   - One train has multiple route stations
   - Cascade: ON DELETE CASCADE

8. **STATION → TRAIN_ROUTE** (1:M)
   - One station appears in multiple train routes
   - Cascade: ON DELETE RESTRICT

## Data Types & Constraints

### **Key Fields**
```sql
-- Primary Keys
id: INTEGER PRIMARY KEY AUTO_INCREMENT

-- Foreign Keys
user_id: INTEGER REFERENCES user(id)
train_id: INTEGER REFERENCES train(id)
station_id: INTEGER REFERENCES station(id)
booking_id: INTEGER REFERENCES booking(id)

-- Unique Constraints
username: VARCHAR(64) UNIQUE NOT NULL
email: VARCHAR(120) UNIQUE NOT NULL
pnr: VARCHAR(10) UNIQUE NOT NULL
train_number: VARCHAR(10) UNIQUE NOT NULL
station_code: VARCHAR(10) UNIQUE NOT NULL
```

### **Business Logic Constraints**
```sql
-- Booking Constraints
passengers: INTEGER CHECK (passengers >= 1 AND passengers <= 6)
total_amount: DECIMAL(10,2) CHECK (total_amount >= 0)
journey_date: DATE CHECK (journey_date >= CURRENT_DATE)

-- Train Constraints  
total_seats: INTEGER CHECK (total_seats > 0)
tatkal_seats: INTEGER CHECK (tatkal_seats >= 0 AND tatkal_seats <= total_seats)
fare_per_km: DECIMAL(8,2) CHECK (fare_per_km > 0)

-- User Constraints
role: ENUM('user', 'admin', 'super_admin') DEFAULT 'user'
active: BOOLEAN DEFAULT TRUE

-- Status Constraints
booking_status: ENUM('pending_payment', 'confirmed', 'waitlisted', 'cancelled')
payment_status: ENUM('pending', 'success', 'failed', 'refunded')
```

## Indexes for Performance

### **Primary Indexes**
```sql
-- Search Performance
CREATE INDEX idx_booking_user_date ON booking(user_id, journey_date);
CREATE INDEX idx_booking_train_date ON booking(train_id, journey_date);
CREATE INDEX idx_booking_pnr ON booking(pnr);

-- Route Performance
CREATE INDEX idx_train_route_train ON train_route(train_id, sequence);
CREATE INDEX idx_train_route_station ON train_route(station_id);

-- Waitlist Performance
CREATE INDEX idx_waitlist_train_date ON waitlist(train_id, journey_date, position);

-- Authentication Performance
CREATE INDEX idx_user_email ON user(email);
CREATE INDEX idx_user_username ON user(username);
```

## Data Integrity Rules

### **Referential Integrity**
1. **Booking Dependencies**: Bookings must reference valid users, trains, and stations
2. **Route Dependencies**: Train routes must reference valid trains and stations
3. **Passenger Dependencies**: Passengers must belong to valid bookings
4. **Payment Dependencies**: Payments must belong to valid bookings and users

### **Business Rules**
1. **Seat Allocation**: Available seats cannot be negative
2. **Tatkal Quota**: Tatkal seats cannot exceed total seats
3. **Passenger Limit**: Maximum 6 passengers per booking
4. **Date Validation**: Journey date must be in the future
5. **Unique Constraints**: PNR, train numbers, station codes must be unique

### **Cascade Rules**
1. **User Deletion**: RESTRICT (preserve booking history)
2. **Train Deletion**: RESTRICT (preserve booking data)
3. **Station Deletion**: RESTRICT (preserve route data)
4. **Booking Deletion**: CASCADE passengers, payments, waitlist
5. **Route Deletion**: CASCADE when train is deleted

## Tatkal-Specific Schema

### **Enhanced Train Configuration**
```sql
-- Tatkal Configuration in TRAIN table
tatkal_seats: INTEGER DEFAULT 0         -- Reserved Tatkal quota
tatkal_fare_per_km: DECIMAL(8,2)       -- Premium Tatkal pricing

-- Tatkal Booking Types
booking_type: ENUM('general', 'tatkal') DEFAULT 'general'
quota: ENUM('general', 'ladies', 'senior', 'disability', 'tatkal')
```

### **Availability Calculation**
```sql
-- General Quota Availability
SELECT (t.total_seats - COALESCE(t.tatkal_seats, 0)) - 
       COALESCE(SUM(b.passengers), 0) as general_available
FROM train t
LEFT JOIN booking b ON t.id = b.train_id 
    AND b.journey_date = ? 
    AND b.booking_type = 'general' 
    AND b.status = 'confirmed'
WHERE t.id = ?

-- Tatkal Quota Availability  
SELECT COALESCE(t.tatkal_seats, 0) - 
       COALESCE(SUM(b.passengers), 0) as tatkal_available
FROM train t
LEFT JOIN booking b ON t.id = b.train_id 
    AND b.journey_date = ? 
    AND b.booking_type = 'tatkal' 
    AND b.status = 'confirmed'
WHERE t.id = ?
```

---

**Legend:**
- 🔑 Primary Key
- 🔗 Foreign Key  
- PK: Primary Key
- FK: Foreign Key
- M: Many, 1: One

*This ER diagram represents the complete RailServe database schema with all relationships, constraints, and business logic rules.*