# booking.py - Train Booking System Blueprint

## Overview
Core booking functionality for the RailServe application, handling ticket reservations, seat availability, waitlist management, and booking lifecycle operations.

## Booking Routes

### Book Ticket Form (`/book/<train_id>`)
- **Method**: GET
- **Purpose**: Display booking form for selected train
- **Features**:
  - Train details and route information
  - Station selection from train route
  - Available stations filtering
  - Real-time seat availability display

### Process Booking (`/book/<train_id>`)
- **Method**: POST
- **Purpose**: Process ticket booking request
- **Validation**:
  - Form field completeness
  - Station selection validation
  - Passenger count limits (1-6)
  - Journey date validation (future dates only)
  - Route availability verification

## Booking Process Flow

### Input Validation
- **Station Validation**: Source and destination must be different
- **Date Validation**: Journey date must be in the future
- **Passenger Limits**: Between 1 and 6 passengers allowed
- **Route Verification**: Uses route graph to validate train path

### Fare Calculation
- **Distance-Based**: Calculates fare using route distance
- **Per-Kilometer Pricing**: Uses train's fare rate
- **Passenger Multiplier**: Total fare based on passenger count
- **Service Charges**: Includes applicable fees and taxes

### Seat Allocation Logic
- **Availability Check**: Real-time seat availability verification
- **Immediate Confirmation**: Available seats get immediate confirmation
- **Waitlist Management**: Overbooked requests added to waitlist
- **Seat Reduction**: Confirmed bookings reduce available seat count

## Waitlist System Integration

### Waitlist Queue
- **FIFO Processing**: First-in-first-out queue management
- **Automatic Addition**: Overbooked requests auto-queued
- **Status Tracking**: Waitlist position and status monitoring
- **Confirmation Flow**: Automatic confirmation when seats available

### Queue Management
- **Thread-Safe Operations**: Concurrent booking support
- **Date-Specific Queues**: Separate queues per train and date
- **Position Tracking**: Real-time queue position updates
- **Automatic Processing**: Background confirmation processing

## Booking Management

### Cancel Booking (`/cancel/<booking_id>`)
- **Purpose**: Cancel existing booking
- **Validation**:
  - User ownership verification
  - Cancellation eligibility check
  - Status validation (cannot cancel completed bookings)
- **Actions**:
  - Update booking status to cancelled
  - Seat reallocation
  - Waitlist promotion processing
  - Refund initiation

### Booking Status Management
- **Status Types**: pending_payment, confirmed, waitlisted, cancelled, completed
- **State Transitions**: Controlled status changes
- **Business Rules**: Status change validation
- **Audit Trail**: Status change history tracking

## Integration Components

### Route Graph Integration
- **Path Validation**: Verifies train serves requested route
- **Station Sequence**: Validates station order on train route
- **Route Optimization**: Efficient route checking algorithms
- **Network Analysis**: Complete route network validation

### Payment Integration
- **Payment Redirection**: Automatic redirect to payment processing
- **Booking-Payment Linking**: One-to-one booking-payment relationship
- **Status Synchronization**: Booking status updates based on payment
- **Transaction Tracking**: Complete payment audit trail

### Utility Functions
- **Fare Calculation**: Distance-based fare computation
- **Seat Availability**: Real-time seat checking
- **Date Validation**: Journey date verification
- **Form Processing**: Secure form data handling

## Security Features

### User Authentication
- **Login Required**: All booking operations require authentication
- **User Ownership**: Users can only manage their own bookings
- **Session Validation**: Continuous session checking
- **Access Control**: Route-level access restrictions

### Data Validation
- **Input Sanitization**: Comprehensive form validation
- **Type Checking**: Proper data type enforcement
- **Range Validation**: Passenger count and date range checking
- **Business Rules**: Domain-specific validation logic

## Database Operations

### Transaction Management
- **Atomic Operations**: Consistent booking state updates
- **Rollback Support**: Error recovery with data consistency
- **Concurrent Handling**: Multiple simultaneous booking support
- **Data Integrity**: Foreign key and constraint enforcement

### Relationship Handling
- **User-Booking**: Proper user association
- **Train-Booking**: Train service linking
- **Station-Booking**: Source and destination tracking
- **Payment-Booking**: Financial transaction association

## Error Handling

### User Feedback
- **Flash Messages**: Clear error and success notifications
- **Validation Errors**: Specific field-level error messages
- **Business Logic Errors**: Domain-specific error handling
- **System Errors**: Graceful error recovery

### Logging and Monitoring
- **Booking Events**: Complete booking lifecycle logging
- **Error Tracking**: Comprehensive error logging
- **Performance Monitoring**: Booking operation timing
- **Audit Trail**: Complete user action history

## Blueprint Configuration
Registered as `booking_bp` with `/booking` URL prefix, providing complete ticket booking functionality integrated with the main RailServe application.