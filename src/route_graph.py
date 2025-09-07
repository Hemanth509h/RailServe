from collections import defaultdict, deque
from .models import Train, Station, TrainRoute
from .app import db

class RouteGraph:
    """Graph-based train route modeling using adjacency list"""
    
    def __init__(self):
        self.graph = defaultdict(dict)  # train_id -> {station_id: {neighbors}}
        self._initialized = False
    
    def _ensure_initialized(self):
        """Ensure the graph is initialized"""
        if not self._initialized:
            self._build_graph()
            self._initialized = True
    
    def _build_graph(self):
        """Build graph from database"""
        # Get all train routes
        routes = TrainRoute.query.order_by(TrainRoute.train_id, TrainRoute.sequence).all()
        
        # Group by train
        train_routes = defaultdict(list)
        for route in routes:
            train_routes[route.train_id].append(route)
        
        # Build adjacency list for each train
        for train_id, train_route_list in train_routes.items():
            if train_id not in self.graph:
                self.graph[train_id] = defaultdict(dict)
            
            # Sort by sequence
            train_route_list.sort(key=lambda x: x.sequence)
            
            # Create connections between consecutive stations
            for i in range(len(train_route_list) - 1):
                current_station = train_route_list[i].station_id
                next_station = train_route_list[i + 1].station_id
                
                # Add edge with route information
                self.graph[train_id][current_station][next_station] = {
                    'distance': train_route_list[i + 1].distance_from_start - train_route_list[i].distance_from_start,
                    'sequence_from': train_route_list[i].sequence,
                    'sequence_to': train_route_list[i + 1].sequence,
                    'arrival_time': train_route_list[i + 1].arrival_time,
                    'departure_time': train_route_list[i].departure_time
                }
    
    def has_route(self, train_id, from_station_id, to_station_id):
        """Check if route exists between stations for a train"""
        self._ensure_initialized()
        if train_id not in self.graph:
            return False
        
        return self._bfs_route_exists(train_id, from_station_id, to_station_id)
    
    def _bfs_route_exists(self, train_id, start_station, end_station):
        """BFS to check if route exists"""
        if start_station == end_station:
            return True
        
        train_graph = self.graph[train_id]
        if start_station not in train_graph:
            return False
        
        visited = set()
        queue = deque([start_station])
        visited.add(start_station)
        
        while queue:
            current_station = queue.popleft()
            
            if current_station == end_station:
                return True
            
            # Add neighbors to queue
            for neighbor in train_graph.get(current_station, {}):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return False
    
    def get_route_path(self, train_id, from_station_id, to_station_id):
        """Get the path between stations"""
        self._ensure_initialized()
        if train_id not in self.graph:
            return None
        
        path = self._bfs_path(train_id, from_station_id, to_station_id)
        if not path:
            return None
        
        # Get route details
        route_details = []
        train_graph = self.graph[train_id]
        
        for i in range(len(path) - 1):
            current = path[i]
            next_station = path[i + 1]
            
            if next_station in train_graph.get(current, {}):
                route_info = train_graph[current][next_station]
                route_details.append({
                    'from_station_id': current,
                    'to_station_id': next_station,
                    'distance': route_info['distance'],
                    'sequence_from': route_info['sequence_from'],
                    'sequence_to': route_info['sequence_to']
                })
        
        return route_details
    
    def _bfs_path(self, train_id, start_station, end_station):
        """BFS to find path between stations"""
        if start_station == end_station:
            return [start_station]
        
        train_graph = self.graph[train_id]
        if start_station not in train_graph:
            return None
        
        visited = set()
        queue = deque([(start_station, [start_station])])
        visited.add(start_station)
        
        while queue:
            current_station, path = queue.popleft()
            
            # Add neighbors to queue
            for neighbor in train_graph.get(current_station, {}):
                if neighbor == end_station:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def get_total_distance(self, train_id, from_station_id, to_station_id):
        """Get total distance between stations"""
        self._ensure_initialized()
        route_path = self.get_route_path(train_id, from_station_id, to_station_id)
        if not route_path:
            return 0
        
        total_distance = sum(segment['distance'] for segment in route_path)
        return total_distance
    
    def get_intermediate_stations(self, train_id, from_station_id, to_station_id):
        """Get intermediate stations between source and destination"""
        path = self._bfs_path(train_id, from_station_id, to_station_id)
        if not path or len(path) < 3:
            return []
        
        # Return intermediate stations (exclude first and last)
        intermediate_ids = path[1:-1]
        
        # Get station details
        stations = Station.query.filter(Station.id.in_(intermediate_ids)).all()
        station_dict = {station.id: station for station in stations}
        
        # Return in order
        intermediate_stations = []
        for station_id in intermediate_ids:
            if station_id in station_dict:
                intermediate_stations.append(station_dict[station_id])
        
        return intermediate_stations
    
    def get_train_stations(self, train_id):
        """Get all stations for a train in sequence"""
        if train_id not in self.graph:
            return []
        
        # Get all routes for the train
        routes = TrainRoute.query.filter_by(train_id=train_id).order_by(TrainRoute.sequence).all()
        
        station_ids = [route.station_id for route in routes]
        stations = Station.query.filter(Station.id.in_(station_ids)).all()
        station_dict = {station.id: station for station in stations}
        
        # Return stations in sequence order
        ordered_stations = []
        for route in routes:
            if route.station_id in station_dict:
                station = station_dict[route.station_id]
                station.route_info = {
                    'sequence': route.sequence,
                    'arrival_time': route.arrival_time,
                    'departure_time': route.departure_time,
                    'distance_from_start': route.distance_from_start
                }
                ordered_stations.append(station)
        
        return ordered_stations
    
    def find_connecting_trains(self, from_station_id, to_station_id):
        """Find all trains that connect two stations"""
        connecting_trains = []
        
        for train_id in self.graph:
            if self.has_route(train_id, from_station_id, to_station_id):
                train = Train.query.get(train_id)
                if train and train.active:
                    connecting_trains.append(train)
        
        return connecting_trains
    
    def get_route_statistics(self):
        """Get statistics about routes"""
        total_trains = len(self.graph)
        total_routes = 0
        total_stations = set()
        
        for train_id, train_graph in self.graph.items():
            for station_id, neighbors in train_graph.items():
                total_stations.add(station_id)
                total_routes += len(neighbors)
        
        return {
            'total_trains': total_trains,
            'total_routes': total_routes,
            'total_stations': len(total_stations),
            'avg_routes_per_train': total_routes / total_trains if total_trains > 0 else 0
        }
    
    def rebuild_graph(self):
        """Rebuild graph from database (call after route updates)"""
        self.graph.clear()
        self._build_graph()
    
    def add_route(self, train_id, from_station_id, to_station_id, route_info):
        """Add new route to graph"""
        if train_id not in self.graph:
            self.graph[train_id] = defaultdict(dict)
        
        self.graph[train_id][from_station_id][to_station_id] = route_info
    
    def remove_route(self, train_id, from_station_id, to_station_id):
        """Remove route from graph"""
        if train_id in self.graph and from_station_id in self.graph[train_id]:
            if to_station_id in self.graph[train_id][from_station_id]:
                del self.graph[train_id][from_station_id][to_station_id]

# Global instance - lazy initialization
_route_graph_instance = None

def get_route_graph():
    """Get the global route graph instance with lazy initialization"""
    global _route_graph_instance
    if _route_graph_instance is None:
        _route_graph_instance = RouteGraph()
    return _route_graph_instance
