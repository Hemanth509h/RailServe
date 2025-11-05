import requests
import os
from typing import Dict, List, Optional, Any

class DatabaseAPIClient:
    """Client for interacting with the database API"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.environ.get('DATABASE_API_URL', 'http://localhost:5000')
        self.session = requests.Session()
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    # User endpoints
    def get_users(self) -> List[Dict]:
        return self._request('GET', '/api/users')
    
    def get_user(self, user_id: int) -> Dict:
        return self._request('GET', f'/api/users/{user_id}')
    
    def get_user_by_username(self, username: str) -> Dict:
        return self._request('GET', f'/api/users/by-username/{username}')
    
    def get_user_by_email(self, email: str) -> Dict:
        return self._request('GET', f'/api/users/by-email/{email}')
    
    def create_user(self, data: Dict) -> Dict:
        return self._request('POST', '/api/users', json=data)
    
    def update_user(self, user_id: int, data: Dict) -> Dict:
        return self._request('PUT', f'/api/users/{user_id}', json=data)
    
    def delete_user(self, user_id: int) -> Dict:
        return self._request('DELETE', f'/api/users/{user_id}')
    
    # Station endpoints
    def get_stations(self) -> List[Dict]:
        return self._request('GET', '/api/stations')
    
    def get_station(self, station_id: int) -> Dict:
        return self._request('GET', f'/api/stations/{station_id}')
    
    def get_station_by_code(self, code: str) -> Dict:
        return self._request('GET', f'/api/stations/code/{code}')
    
    def create_station(self, data: Dict) -> Dict:
        return self._request('POST', '/api/stations', json=data)
    
    def update_station(self, station_id: int, data: Dict) -> Dict:
        return self._request('PUT', f'/api/stations/{station_id}', json=data)
    
    def delete_station(self, station_id: int) -> Dict:
        return self._request('DELETE', f'/api/stations/{station_id}')
    
    # Train endpoints
    def get_trains(self) -> List[Dict]:
        return self._request('GET', '/api/trains')
    
    def get_train(self, train_id: int) -> Dict:
        return self._request('GET', f'/api/trains/{train_id}')
    
    def get_train_by_number(self, number: str) -> Dict:
        return self._request('GET', f'/api/trains/number/{number}')
    
    def create_train(self, data: Dict) -> Dict:
        return self._request('POST', '/api/trains', json=data)
    
    def update_train(self, train_id: int, data: Dict) -> Dict:
        return self._request('PUT', f'/api/trains/{train_id}', json=data)
    
    def delete_train(self, train_id: int) -> Dict:
        return self._request('DELETE', f'/api/trains/{train_id}')
    
    # Train route endpoints
    def get_train_routes(self, train_id: int) -> List[Dict]:
        return self._request('GET', f'/api/routes/train/{train_id}')
    
    def create_route(self, data: Dict) -> Dict:
        return self._request('POST', '/api/routes', json=data)
    
    def update_route(self, route_id: int, data: Dict) -> Dict:
        return self._request('PUT', f'/api/routes/{route_id}', json=data)
    
    def delete_route(self, route_id: int) -> Dict:
        return self._request('DELETE', f'/api/routes/{route_id}')
    
    # Booking endpoints
    def get_bookings(self, user_id: Optional[int] = None) -> List[Dict]:
        params = {'user_id': user_id} if user_id else {}
        return self._request('GET', '/api/bookings', params=params)
    
    def get_booking(self, booking_id: int) -> Dict:
        return self._request('GET', f'/api/bookings/{booking_id}')
    
    def get_booking_by_pnr(self, pnr: str) -> Dict:
        return self._request('GET', f'/api/bookings/pnr/{pnr}')
    
    def create_booking(self, data: Dict) -> Dict:
        return self._request('POST', '/api/bookings', json=data)
    
    def update_booking(self, booking_id: int, data: Dict) -> Dict:
        return self._request('PUT', f'/api/bookings/{booking_id}', json=data)
    
    def get_booking_passengers(self, booking_id: int) -> List[Dict]:
        return self._request('GET', f'/api/bookings/{booking_id}/passengers')
    
    def add_passenger(self, data: Dict) -> Dict:
        booking_id = data.get('booking_id')
        return self._request('POST', f'/api/bookings/{booking_id}/passengers', json=data)
    
    # Payment endpoints
    def get_payments(self) -> List[Dict]:
        return self._request('GET', '/api/payments')
    
    def get_payment(self, payment_id: int) -> Dict:
        return self._request('GET', f'/api/payments/{payment_id}')
    
    def get_payment_by_booking(self, booking_id: int) -> Dict:
        return self._request('GET', f'/api/payments/booking/{booking_id}')
    
    def create_payment(self, data: Dict) -> Dict:
        return self._request('POST', '/api/payments', json=data)
    
    def update_payment(self, payment_id: int, data: Dict) -> Dict:
        return self._request('PUT', f'/api/payments/{payment_id}', json=data)
    
    # Waitlist endpoints
    def get_waitlists(self) -> List[Dict]:
        return self._request('GET', '/api/waitlist')
    
    def get_waitlist_by_booking(self, booking_id: int) -> Dict:
        return self._request('GET', f'/api/waitlist/booking/{booking_id}')
    
    def create_waitlist(self, data: Dict) -> Dict:
        return self._request('POST', '/api/waitlist', json=data)
    
    def update_waitlist(self, waitlist_id: int, data: Dict) -> Dict:
        return self._request('PUT', f'/api/waitlist/{waitlist_id}', json=data)
    
    def delete_waitlist(self, waitlist_id: int) -> Dict:
        return self._request('DELETE', f'/api/waitlist/{waitlist_id}')
    
    # Tatkal endpoints
    def get_tatkal_timeslots(self) -> List[Dict]:
        return self._request('GET', '/api/tatkal/timeslots')
    
    def create_tatkal_timeslot(self, data: Dict) -> Dict:
        return self._request('POST', '/api/tatkal/timeslots', json=data)
    
    def get_tatkal_override(self) -> Dict:
        return self._request('GET', '/api/tatkal/override')
    
    def create_tatkal_override(self, data: Dict) -> Dict:
        return self._request('POST', '/api/tatkal/override', json=data)
    
    # Refund endpoints
    def get_refunds(self) -> List[Dict]:
        return self._request('GET', '/api/refunds')
    
    def get_refund(self, refund_id: int) -> Dict:
        return self._request('GET', f'/api/refunds/{refund_id}')
    
    def create_refund(self, data: Dict) -> Dict:
        return self._request('POST', '/api/refunds', json=data)
    
    def update_refund(self, refund_id: int, data: Dict) -> Dict:
        return self._request('PUT', f'/api/refunds/{refund_id}', json=data)
    
    # Complaint endpoints
    def get_complaints(self) -> List[Dict]:
        return self._request('GET', '/api/complaints')
    
    def get_complaint(self, complaint_id: int) -> Dict:
        return self._request('GET', f'/api/complaints/{complaint_id}')
    
    def create_complaint(self, data: Dict) -> Dict:
        return self._request('POST', '/api/complaints', json=data)
    
    def update_complaint(self, complaint_id: int, data: Dict) -> Dict:
        return self._request('PUT', f'/api/complaints/{complaint_id}', json=data)
    
    # Performance endpoints
    def get_performance_metrics(self) -> List[Dict]:
        return self._request('GET', '/api/performance/metrics')
    
    def create_performance_metrics(self, data: Dict) -> Dict:
        return self._request('POST', '/api/performance/metrics', json=data)
    
    def get_seat_availability(self, train_id: Optional[int] = None, journey_date: Optional[str] = None) -> List[Dict]:
        params = {}
        if train_id:
            params['train_id'] = train_id
        if journey_date:
            params['journey_date'] = journey_date
        return self._request('GET', '/api/performance/availability', params=params)
    
    def create_seat_availability(self, data: Dict) -> Dict:
        return self._request('POST', '/api/performance/availability', json=data)
    
    def get_dynamic_pricing(self) -> List[Dict]:
        return self._request('GET', '/api/performance/pricing')
    
    def create_dynamic_pricing(self, data: Dict) -> Dict:
        return self._request('POST', '/api/performance/pricing', json=data)

# Global instance
db_api = DatabaseAPIClient()
