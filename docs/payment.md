# payment.py - Payment Processing Blueprint

## Overview
Handles payment processing for train bookings in the RailServe system, providing a simulated payment gateway with transaction management and status tracking.

## Payment Routes

### Payment Page (`/pay/<booking_id>`)
- **Method**: GET
- **Purpose**: Display payment form for booking
- **Security**: User ownership verification
- **Features**:
  - Booking details display
  - Amount confirmation
  - Payment method selection
  - Transaction security information
- **Validation**: Prevents duplicate payments for completed transactions

### Process Payment (`/process/<booking_id>`)
- **Method**: POST
- **Purpose**: Process payment transaction
- **Security**: User ownership verification
- **Flow**:
  - Payment method validation
  - Transaction ID generation
  - Simulated payment processing
  - Status update and confirmation

## Payment Simulation System

### Simulated Gateway
- **Random Success**: 90% success rate simulation
- **Failure Simulation**: 10% random failure for testing
- **Transaction IDs**: Unique alphanumeric transaction identifiers
- **Processing Delay**: Realistic payment processing simulation
- **Status Tracking**: Complete transaction lifecycle management

### Payment Methods
- **Credit Card**: Simulated credit card processing
- **Debit Card**: Simulated debit card transactions
- **Net Banking**: Simulated online banking
- **UPI**: Unified Payments Interface simulation
- **Wallet**: Digital wallet payment simulation

## Transaction Management

### Payment Records
- **Transaction Tracking**: Complete payment history
- **Amount Verification**: Booking amount validation
- **Status Management**: Payment status lifecycle
- **Audit Trail**: Transaction timestamp and details
- **User Association**: Payment-user relationship tracking

### Status Types
- **Pending**: Initial payment state
- **Success**: Completed successful payment
- **Failed**: Failed payment transaction
- **Refunded**: Refunded payment status
- **Cancelled**: Cancelled payment transaction

## Payment Processing Flow

### Pre-Payment Validation
- **Booking Existence**: Validates booking exists
- **User Ownership**: Ensures user owns the booking
- **Payment Status**: Prevents duplicate payments
- **Amount Verification**: Confirms payment amount matches booking
- **Booking Status**: Validates booking is payment-eligible

### Transaction Processing
- **Payment Method**: Validates selected payment method
- **Transaction ID**: Generates unique transaction identifier
- **Gateway Simulation**: Simulates external payment gateway
- **Status Update**: Updates payment and booking status
- **Confirmation**: Provides transaction confirmation

### Post-Payment Actions
- **Booking Confirmation**: Updates booking status on successful payment
- **Seat Allocation**: Finalizes seat reservation
- **Confirmation Email**: Triggers booking confirmation (simulated)
- **Receipt Generation**: Creates payment receipt
- **Redirect**: Returns user to profile with confirmation

## Payment Success Flow

### Successful Payments
- **Booking Confirmation**: Updates booking status to 'confirmed'
- **Seat Allocation**: Reduces available seats on train
- **Payment Record**: Creates successful payment record
- **User Notification**: Success message display
- **Profile Redirect**: Returns to user profile with confirmation

### Waitlist Processing
- **Queue Advancement**: Processes waitlist when seats become available
- **Automatic Confirmation**: Promotes waitlisted bookings
- **Notification System**: Alerts users of waitlist status changes
- **Seat Reallocation**: Manages dynamic seat availability

## Payment Failure Handling

### Failed Payments
- **Status Update**: Marks payment as failed
- **Booking Status**: Maintains booking in pending state
- **Error Messages**: Clear failure reason communication
- **Retry Option**: Allows payment retry attempts
- **Timeout Handling**: Manages payment session timeouts

### Error Recovery
- **Transaction Rollback**: Reverts failed transaction changes
- **Status Consistency**: Maintains consistent payment and booking states
- **User Guidance**: Provides clear next steps for users
- **Support Information**: Offers help and support options

## Security Features

### User Authentication
- **Login Required**: All payment operations require authentication
- **Ownership Verification**: Users can only pay for their own bookings
- **Session Security**: Secure session management during payment
- **CSRF Protection**: Cross-site request forgery prevention

### Transaction Security
- **Unique IDs**: Cryptographically secure transaction identifiers
- **Amount Validation**: Server-side amount verification
- **Status Integrity**: Prevents payment status manipulation
- **Audit Logging**: Complete transaction audit trail

## Integration Features

### Booking Integration
- **Status Synchronization**: Automatic booking status updates
- **Seat Management**: Real-time seat allocation
- **Waitlist Processing**: Automatic queue management
- **Confirmation Flow**: Seamless booking confirmation

### Database Operations
- **Transaction Safety**: Atomic payment operations
- **Relationship Management**: Payment-booking-user associations
- **Data Consistency**: Referential integrity maintenance
- **Audit Trail**: Complete transaction history

### User Experience
- **Clear Interface**: Intuitive payment form design
- **Status Feedback**: Real-time payment status updates
- **Error Handling**: User-friendly error messages
- **Confirmation**: Clear payment confirmation display

## Future Enhancement Ready

### Gateway Integration
- **API Abstraction**: Ready for real payment gateway integration
- **Configuration Management**: Environment-based gateway settings
- **Webhook Support**: Prepared for payment gateway callbacks
- **Multi-Gateway**: Support for multiple payment providers

### Advanced Features
- **Refund Processing**: Framework for automated refunds
- **Partial Payments**: Structure for installment payments
- **Payment Plans**: Foundation for booking payment plans
- **Currency Support**: Multi-currency payment capability

## Blueprint Configuration
Registered as `payment_bp` with `/payment` URL prefix, providing secure payment processing functionality integrated with the RailServe booking system.