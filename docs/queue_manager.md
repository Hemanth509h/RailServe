# queue_manager.py - Waitlist Queue Management System

## Overview
Implements a sophisticated FIFO (First-In-First-Out) queue-based waitlist management system for handling train booking waitlists with thread-safe operations and automatic confirmation processing.

## Core Classes

### WaitlistManager
- **Purpose**: Central manager for all waitlist operations
- **Design Pattern**: Singleton-like behavior with centralized queue management
- **Thread Safety**: Thread-safe operations for concurrent booking scenarios
- **Persistence**: Database-backed queue state with memory optimization

## Queue Management

### Queue Architecture
- **FIFO Implementation**: Uses Python's deque for efficient queue operations
- **Key-Based Queues**: Separate queues per train and journey date combination
- **Memory Management**: Lazy loading of queues from database
- **Thread Locking**: Prevents race conditions in concurrent environments

### Queue Operations

#### add_to_waitlist(booking_id, train_id, journey_date)
- **Purpose**: Adds booking to appropriate waitlist queue
- **Process**:
  - Generates unique queue key from train ID and date
  - Acquires thread lock for safe operation
  - Adds booking to memory queue
  - Persists waitlist entry to database
  - Assigns queue position automatically
- **Returns**: Queue position for user notification

#### process_waitlist_confirmations(train_id, journey_date, available_seats)
- **Purpose**: Automatically confirms waitlisted bookings when seats become available
- **Algorithm**:
  - Retrieves queue for specified train and date
  - Processes bookings in FIFO order
  - Confirms bookings while seats are available
  - Updates booking and train seat availability
  - Removes confirmed bookings from queue
- **Atomicity**: Database transactions ensure data consistency

#### get_queue_position(booking_id, train_id, journey_date)
- **Purpose**: Retrieves current queue position for a booking
- **Features**:
  - Real-time position calculation
  - Database synchronization
  - User notification support
- **Returns**: Current position in queue (1-based indexing)

#### remove_from_waitlist(booking_id, train_id, journey_date)
- **Purpose**: Removes booking from waitlist (cancellation scenarios)
- **Process**:
  - Locates booking in appropriate queue
  - Removes from memory queue
  - Updates database waitlist status
  - Recalculates positions for remaining bookings
- **Consistency**: Maintains queue integrity after removal

## Database Integration

### Persistence Layer
- **Waitlist Model**: Database table for queue persistence
- **Position Tracking**: Maintains queue order across application restarts
- **Status Management**: Tracks waitlist entry status (active, confirmed, cancelled)
- **Audit Trail**: Complete history of waitlist operations

### Synchronization
- **Memory-Database Sync**: Ensures consistency between memory queues and database
- **Lazy Loading**: Loads queue data only when needed
- **Automatic Persistence**: All queue operations automatically persist to database
- **Recovery**: Can rebuild memory queues from database state

## Thread Safety

### Concurrency Control
- **Threading.Lock**: Prevents concurrent modification of queues
- **Atomic Operations**: Database transactions ensure consistency
- **Race Condition Prevention**: Proper locking around critical sections
- **Deadlock Avoidance**: Careful lock acquisition and release patterns

### Scalability Features
- **Multiple Queues**: Separate queues prevent cross-train blocking
- **Efficient Locking**: Minimal lock holding time
- **Concurrent Processing**: Multiple trains can process waitlists simultaneously
- **Performance Optimization**: O(1) queue operations with deque

## Business Logic

### Confirmation Rules
- **FIFO Processing**: Strict first-in-first-out confirmation order
- **Seat Availability**: Only confirms when seats are actually available
- **Automatic Processing**: Triggered by cancellations and seat releases
- **Batch Processing**: Can process multiple confirmations in single operation

### Status Management
- **Waitlist Status**: Tracks active, confirmed, cancelled states
- **Booking Integration**: Synchronizes with main booking system
- **Position Updates**: Real-time position recalculation
- **Notification Ready**: Provides data for user notifications

## Advanced Features

### Queue Analytics
- **Queue Length**: Real-time queue size tracking
- **Average Wait Time**: Statistical analysis of confirmation times
- **Confirmation Rate**: Success rate analysis
- **Performance Metrics**: Queue processing performance data

### Error Handling
- **Database Failures**: Graceful handling of database connectivity issues
- **Consistency Checks**: Validates queue state integrity
- **Recovery Mechanisms**: Automatic recovery from inconsistent states
- **Error Logging**: Comprehensive logging for debugging

## Integration Points

### Booking System Integration
- **Automatic Addition**: Overbooked requests automatically added to waitlist
- **Status Synchronization**: Booking status updates reflect waitlist changes
- **Seat Coordination**: Coordinates with seat availability system
- **User Experience**: Seamless integration with booking workflow

### Payment System Integration
- **Payment Holding**: Coordinates with payment processing
- **Confirmation Flow**: Triggers payment processing upon confirmation
- **Refund Processing**: Handles refunds for cancelled waitlist entries
- **Transaction Integrity**: Maintains payment-booking consistency

## Monitoring and Maintenance

### Health Checks
- **Queue Integrity**: Validates queue consistency
- **Database Sync**: Checks memory-database synchronization
- **Performance Monitoring**: Tracks queue operation performance
- **Capacity Planning**: Monitors queue sizes and growth patterns

### Maintenance Operations
- **Queue Cleanup**: Removes old or invalid queue entries
- **Position Recalculation**: Corrects position inconsistencies
- **Database Optimization**: Maintains optimal database performance
- **Archive Operations**: Archives completed waitlist entries

## Configuration and Tuning

### Performance Tuning
- **Queue Size Limits**: Configurable maximum queue sizes
- **Batch Processing**: Configurable batch confirmation sizes
- **Timeout Settings**: Configurable operation timeouts
- **Memory Management**: Configurable queue memory limits

### Business Rules
- **Confirmation Timeout**: Maximum time in queue before expiry
- **Priority Rules**: Potential for priority-based queue processing
- **Capacity Limits**: Maximum waitlist size per train
- **Processing Intervals**: Automatic processing frequency

## Usage Examples

### Adding to Waitlist
```python
manager = WaitlistManager()
position = manager.add_to_waitlist(booking_id=123, train_id=101, journey_date=date(2025, 9, 10))
```

### Processing Confirmations
```python
confirmed_count = manager.process_waitlist_confirmations(
    train_id=101, 
    journey_date=date(2025, 9, 10), 
    available_seats=3
)
```

### Checking Position
```python
position = manager.get_queue_position(booking_id=123, train_id=101, journey_date=date(2025, 9, 10))
```

This queue management system provides robust, scalable waitlist functionality essential for handling high-demand train bookings while maintaining fairness and system reliability.