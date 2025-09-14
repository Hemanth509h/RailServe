# route_graph.py - Train Route Graph System

## Overview
Implements a sophisticated graph-based train route modeling system using adjacency lists for efficient pathfinding, route validation, and network analysis in the RailServe railway system.

## Core Classes

### RouteGraph
- **Purpose**: Graph-based representation of train route networks
- **Data Structure**: Adjacency list implementation for efficient traversal
- **Initialization**: Lazy loading with automatic graph building
- **Performance**: Optimized for route queries and pathfinding operations

## Graph Architecture

### Graph Structure
- **Adjacency Lists**: Each train has its own adjacency list representation
- **Node Representation**: Stations as graph nodes
- **Edge Representation**: Direct connections between consecutive stations
- **Weighted Edges**: Distance and sequence information stored with edges
- **Directed Graph**: Maintains directional route information

### Data Organization
```
graph = {
    train_id: {
        station_id: {
            'next': next_station_id,
            'prev': previous_station_id,
            'sequence': station_sequence,
            'distance': distance_from_start
        }
    }
}
```

## Core Operations

### Graph Building

#### _build_graph()
- **Purpose**: Constructs graph from database route information
- **Process**:
  - Queries all train routes from database
  - Groups routes by train ID
  - Sorts routes by sequence number
  - Builds adjacency lists for each train
  - Establishes bidirectional connections
- **Optimization**: Single database query with in-memory processing

#### _ensure_initialized()
- **Purpose**: Lazy initialization of graph structure
- **Benefits**:
  - Reduces memory usage when graph not needed
  - Allows for fresh data loading when required
  - Improves application startup time
- **Thread Safety**: Safe for concurrent access

### Route Validation

#### has_route(train_id, from_station_id, to_station_id)
- **Purpose**: Validates if a route exists between two stations on a train
- **Algorithm**:
  - Checks if train exists in graph
  - Verifies both stations exist on train route
  - Uses breadth-first search for path existence
  - Validates route direction and connectivity
- **Returns**: Boolean indicating route availability

#### get_route_distance(train_id, from_station_id, to_station_id)
- **Purpose**: Calculates distance between two stations on a train route
- **Method**:
  - Retrieves distance information from graph nodes
  - Calculates absolute difference between station distances
  - Validates route existence before calculation
- **Returns**: Distance in kilometers or 0 if route invalid

### Pathfinding Algorithms

#### find_shortest_path(train_id, from_station_id, to_station_id)
- **Purpose**: Finds optimal path between stations
- **Algorithm**: Breadth-First Search (BFS) implementation
- **Features**:
  - Guaranteed shortest path in unweighted graph
  - Efficient O(V + E) time complexity
  - Returns complete path with intermediate stations
- **Returns**: List of station IDs representing the path

#### get_all_stations_on_route(train_id, from_station_id, to_station_id)
- **Purpose**: Returns all intermediate stations between source and destination
- **Usage**: Display complete journey information to users
- **Ordering**: Maintains correct sequence order
- **Returns**: Ordered list of station IDs on the route

## Advanced Features

### Route Analysis

#### get_train_network_stats(train_id)
- **Purpose**: Provides comprehensive network statistics for a train
- **Metrics**:
  - Total number of stations
  - Total route distance
  - Average inter-station distance
  - Network connectivity degree
- **Usage**: Analytics and route optimization

#### find_alternative_routes(from_station_id, to_station_id)
- **Purpose**: Discovers alternative train options between stations
- **Algorithm**:
  - Searches across all train graphs
  - Identifies trains serving both stations
  - Ranks alternatives by distance and connections
- **Returns**: List of alternative train options

### Network Connectivity

#### get_connected_stations(train_id, station_id)
- **Purpose**: Returns all stations reachable from given station
- **Algorithm**: Depth-First Search traversal
- **Applications**:
  - Route planning assistance
  - Network coverage analysis
  - Connectivity validation
- **Returns**: Set of reachable station IDs

#### validate_network_integrity(train_id)
- **Purpose**: Validates train route network consistency
- **Checks**:
  - Ensures all stations are properly connected
  - Validates sequence number consistency
  - Checks for orphaned stations
  - Verifies distance calculations
- **Returns**: Validation report with any inconsistencies

## Performance Optimizations

### Memory Efficiency
- **Lazy Loading**: Graph built only when needed
- **Efficient Storage**: Adjacency lists minimize memory usage
- **Selective Loading**: Can load specific train graphs only
- **Cache Friendly**: Data structure optimized for CPU cache

### Query Optimization
- **O(1) Lookups**: Direct station access in adjacency lists
- **BFS Efficiency**: Optimal pathfinding algorithm choice
- **Early Termination**: Algorithms terminate as soon as solution found
- **Index Usage**: Leverages database indexes for initial data loading

## Integration Features

### Database Integration
- **Model Synchronization**: Automatically syncs with TrainRoute database model
- **Fresh Data**: Can rebuild graph from current database state
- **Relationship Handling**: Properly handles train-station relationships
- **Data Integrity**: Validates database consistency during graph building

### Application Integration
- **Booking System**: Validates routes during booking process
- **Search System**: Powers train search between stations
- **Fare Calculation**: Provides distance data for fare computation
- **Admin Interface**: Supports route management operations

## Error Handling

### Robustness Features
- **Invalid Input Handling**: Graceful handling of non-existent trains/stations
- **Database Errors**: Continues operation with cached data during DB issues
- **Consistency Checks**: Validates graph integrity during operations
- **Fallback Mechanisms**: Alternative approaches when primary methods fail

### Logging and Monitoring
- **Operation Logging**: Logs graph building and query operations
- **Performance Metrics**: Tracks query response times
- **Error Tracking**: Comprehensive error logging for debugging
- **Usage Statistics**: Monitors graph usage patterns

## Configuration and Tuning

### Performance Tuning
- **Graph Caching**: Configurable graph cache duration
- **Batch Loading**: Optimized database query batching
- **Memory Limits**: Configurable memory usage limits
- **Query Optimization**: Tunable algorithm parameters

### Business Rules
- **Route Validation**: Configurable route validation rules
- **Distance Calculation**: Customizable distance computation methods
- **Network Constraints**: Configurable network topology rules
- **Update Frequency**: Configurable graph refresh intervals

## Global Instance

### get_route_graph()
- **Purpose**: Provides singleton access to route graph instance
- **Benefits**:
  - Ensures single graph instance across application
  - Reduces memory usage and initialization overhead
  - Provides consistent graph state
- **Usage**: Used throughout application for route operations

## Usage Examples

### Route Validation
```python
graph = get_route_graph()
has_route = graph.has_route(train_id=101, from_station_id=1, to_station_id=5)
```

### Distance Calculation
```python
distance = graph.get_route_distance(train_id=101, from_station_id=1, to_station_id=5)
```

### Pathfinding
```python
path = graph.find_shortest_path(train_id=101, from_station_id=1, to_station_id=5)
```

This route graph system provides the foundational infrastructure for all route-related operations in the RailServe application, ensuring efficient and accurate train network navigation and validation.