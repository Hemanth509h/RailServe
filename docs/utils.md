# utils.py - Utility Functions

## Overview
Collection of utility functions providing core business logic for the RailServe application, including train operations, fare calculations, seat management, and reporting functionality.

## Train Operations

### get_running_trains()
- **Purpose**: Retrieves list of currently active trains
- **Returns**: Query result of all trains with active status
- **Usage**: Homepage train display and search functionality
- **Performance**: Optimized query for active train filtering

### search_trains(from_station_id, to_station_id, journey_date)
- **Purpose**: Advanced train search between stations
- **Parameters**:
  - Source station ID
  - Destination station ID
  - Journey date for search
- **Algorithm**:
  - Intersection query to find trains serving both stations
  - Route sequence validation
  - Time and date filtering
- **Returns**: List of valid trains for the specified route

## Fare Calculation System

### calculate_fare(train_id, from_station_id, to_station_id, passengers)
- **Purpose**: Computes journey fare based on distance and passengers
- **Calculation Method**:
  - Distance calculation using route sequences
  - Per-kilometer rate from train configuration
  - Passenger count multiplication
  - Service charge addition (10%)
- **Returns**: Total fare amount rounded to 2 decimal places
- **Error Handling**: Returns 0 for invalid routes or missing data

## Seat Management

### check_seat_availability(train_id, journey_date)
- **Purpose**: Real-time seat availability checking
- **Algorithm**:
  - Counts confirmed and waitlisted bookings for specific date
  - Calculates available seats from train capacity
  - Returns maximum of 0 or available count
- **Database Query**: Aggregates passenger count from bookings
- **Performance**: Optimized for concurrent booking operations

## Reporting Functions

### generate_booking_report(start_date, end_date)
- **Purpose**: Generate comprehensive booking reports
- **Parameters**: Date range for report generation
- **Returns**: List of bookings within specified period
- **Features**:
  - Flexible date range filtering
  - Complete booking information
  - Status-based filtering capability
- **Usage**: Administrative reporting and analytics

### get_popular_routes()
- **Purpose**: Analyze and return most popular travel routes
- **Algorithm**:
  - Aggregates booking counts by route
  - Groups by source and destination stations
  - Orders by booking frequency
  - Limits to top 10 routes
- **Returns**: Popular routes with booking statistics
- **Usage**: Analytics dashboard and route optimization

## Data Validation

### Route Validation
- **Station Existence**: Verifies station IDs exist in database
- **Route Sequence**: Validates station order on train routes
- **Distance Calculation**: Ensures proper distance computation
- **Business Rules**: Enforces railway operational constraints

### Date and Time Handling
- **Journey Date**: Validates future date requirements
- **Time Zones**: Handles time zone considerations
- **Date Formatting**: Consistent date format processing
- **Business Hours**: Validates booking within operational hours

## Performance Optimizations

### Database Queries
- **Index Usage**: Optimized queries for indexed fields
- **Join Optimization**: Efficient table joins for complex queries
- **Aggregation**: Proper use of database aggregation functions
- **Caching Ready**: Structure prepared for query result caching

### Memory Management
- **Efficient Algorithms**: Optimized computational complexity
- **Resource Usage**: Minimal memory footprint
- **Scalability**: Designed for high-volume operations
- **Concurrent Safety**: Thread-safe operations where needed

## Error Handling

### Graceful Degradation
- **Default Returns**: Safe default values for error conditions
- **Null Handling**: Proper None value processing
- **Exception Management**: Controlled exception handling
- **Logging**: Comprehensive error logging for debugging

### Data Integrity
- **Input Validation**: Comprehensive parameter validation
- **Type Checking**: Proper data type enforcement
- **Range Validation**: Boundary condition checking
- **Consistency Checks**: Cross-reference validation

## Integration Features

### Model Integration
- **SQLAlchemy ORM**: Direct integration with database models
- **Relationship Handling**: Proper foreign key relationship usage
- **Transaction Support**: Database transaction compatibility
- **Query Optimization**: Efficient database query patterns

### Business Logic
- **Railway Rules**: Implementation of railway business rules
- **Pricing Logic**: Comprehensive fare calculation system
- **Capacity Management**: Seat allocation and availability logic
- **Route Management**: Train route and network logic

## Extensibility

### Modular Design
- **Function Separation**: Clear separation of concerns
- **Parameter Flexibility**: Configurable function parameters
- **Return Standards**: Consistent return value patterns
- **Documentation**: Comprehensive function documentation

### Future Enhancements
- **Caching Layer**: Ready for caching implementation
- **API Integration**: Prepared for external API integration
- **Configuration**: Environment-based configuration support
- **Monitoring**: Ready for performance monitoring integration

## Dependencies

### Database Models
- **Train Model**: Train information and configuration
- **Station Model**: Station network and information
- **Booking Model**: Booking and reservation data
- **TrainRoute Model**: Route and sequence information

### External Libraries
- **SQLAlchemy**: Database ORM and query operations
- **DateTime**: Date and time manipulation
- **Python Standard Library**: Core Python functionality

## Usage Examples

### Train Search
```python
trains = search_trains(from_station=1, to_station=5, journey_date="2025-09-10")
```

### Fare Calculation
```python
fare = calculate_fare(train_id=101, from_station_id=1, to_station_id=5, passengers=2)
```

### Seat Availability
```python
available_seats = check_seat_availability(train_id=101, journey_date=date(2025, 9, 10))
```

This utility module provides the essential business logic foundation for the entire RailServe application, ensuring consistent and reliable operations across all system components.