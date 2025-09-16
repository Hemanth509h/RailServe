# RailServe Database Schema - ER Diagram

```mermaid
erDiagram
    User ||--o{ Booking : "has many"
    User ||--o{ Payment : "makes"
    
    Train ||--o{ Booking : "has bookings"
    Train ||--o{ TrainRoute : "has routes"
    Train ||--o{ Waitlist : "has waitlist"
    
    Station ||--o{ TrainRoute : "part of routes"
    Station ||--o{ Booking : "from_station"
    Station ||--o{ Booking : "to_station"
    
    Booking ||--o| Payment : "has payment"
    Booking ||--o| Waitlist : "may be waitlisted"
    
    TrainRoute }|--|| Train : "belongs to"
    TrainRoute }|--|| Station : "stops at"
    
    Waitlist }|--|| Booking : "for booking"
    Waitlist }|--|| Train : "for train"
    
    Payment }|--|| Booking : "for booking"
    Payment }|--|| User : "made by"

    User {
        int id PK
        varchar username UK "Unique username"
        varchar email UK "Unique email"
        varchar password_hash "Hashed password"
        varchar role "user, admin, super_admin"
        boolean active "Account status"
        datetime created_at "Account creation"
    }
    
    Train {
        int id PK
        varchar number UK "Train number"
        varchar name "Train name"
        int total_seats "Total capacity"
        int available_seats "Current availability"
        decimal fare_per_km "Base fare rate"
        int tatkal_seats "Tatkal quota seats"
        decimal tatkal_fare_per_km "Tatkal fare rate"
        boolean active "Service status"
    }
    
    Station {
        int id PK
        varchar code UK "Station code (e.g., NDLS)"
        varchar name UK "Station name"
        varchar city "City name"
        varchar state "State name"
        boolean active "Operational status"
    }
    
    TrainRoute {
        int id PK
        int train_id FK "References Train.id"
        int station_id FK "References Station.id"
        int sequence "Stop order (1,2,3...)"
        time arrival_time "Arrival time"
        time departure_time "Departure time"
        int distance_from_start "Distance in km"
    }
    
    Booking {
        int id PK
        varchar pnr UK "Passenger Name Record"
        int user_id FK "References User.id"
        int train_id FK "References Train.id"
        int from_station_id FK "References Station.id"
        int to_station_id FK "References Station.id"
        date journey_date "Travel date"
        int passengers "Number of passengers"
        decimal total_amount "Total fare amount"
        varchar booking_type "general, tatkal"
        varchar quota "general, tatkal, ladies, senior"
        varchar status "confirmed, waitlisted, cancelled, pending_payment"
        datetime booking_date "Booking timestamp"
    }
    
    Payment {
        int id PK
        int booking_id FK "References Booking.id"
        int user_id FK "References User.id"
        decimal amount "Payment amount"
        varchar payment_method "card, upi, netbanking, wallet"
        varchar transaction_id "Gateway transaction ID"
        varchar status "success, failed, pending"
        datetime created_at "Payment initiation"
        datetime completed_at "Payment completion"
    }
    
    Waitlist {
        int id PK
        int booking_id FK "References Booking.id"
        int train_id FK "References Train.id"
        date journey_date "Travel date"
        int position "Queue position"
        datetime created_at "Waitlist timestamp"
    }
```

## Entity Relationships

### Primary Entities

1. **User**: System users with role-based access (user, admin, super_admin)
2. **Train**: Railway services with capacity and fare information
3. **Station**: Railway stations with geographic information
4. **Booking**: Ticket reservations linking users, trains, and stations

### Supporting Entities

1. **TrainRoute**: Defines train paths and schedules between stations
2. **Payment**: Transaction records for completed payments
3. **Waitlist**: FIFO queue management for overbooked trains

### Key Relationships

- **User to Booking**: One-to-many (users can have multiple bookings)
- **Train to Booking**: One-to-many (trains can have multiple bookings)
- **Booking to Payment**: One-to-one (each booking has one payment)
- **Train to TrainRoute**: One-to-many (trains have multiple stops)
- **Station to TrainRoute**: One-to-many (stations serve multiple trains)
- **Booking to Waitlist**: One-to-one optional (only waitlisted bookings)

### Business Rules Enforced

1. **Referential Integrity**: All foreign keys properly reference parent tables
2. **Unique Constraints**: 
   - User usernames and emails must be unique
   - Train numbers must be unique
   - Station codes and names must be unique
   - PNR numbers must be unique
3. **Data Validation**:
   - User roles restricted to defined values
   - Booking status follows defined state transitions
   - Payment status tracks transaction lifecycle
4. **Cascading Rules**:
   - User deactivation preserves booking history
   - Train deactivation preserves historical data
   - Payment deletion cascades from booking deletion

### Index Strategy

```sql
-- Performance indexes for common queries
CREATE INDEX idx_booking_user_id ON booking(user_id);
CREATE INDEX idx_booking_train_journey ON booking(train_id, journey_date);
CREATE INDEX idx_booking_status ON booking(status);
CREATE INDEX idx_train_route_train_sequence ON train_route(train_id, sequence);
CREATE INDEX idx_waitlist_train_journey_position ON waitlist(train_id, journey_date, position);
CREATE INDEX idx_payment_booking ON payment(booking_id);
CREATE INDEX idx_payment_status_created ON payment(status, created_at);
```

### Data Consistency

1. **Seat Allocation**: `Train.available_seats` updated atomically with bookings
2. **Payment Integrity**: Payment amounts match booking amounts
3. **Waitlist Management**: Position numbers maintained in sequence
4. **Route Validation**: Bookings validated against actual train routes