"""
Database Initialization Constants
==================================
Contains all static data used for database seeding.
"""

from datetime import time

COACH_CLASSES = ['AC1', 'AC2', 'AC3', 'SL', '2S', 'CC']

MAJOR_STATIONS = [
    ("New Delhi", "NDLS", "New Delhi", "Delhi"),
    ("Old Delhi", "DLI", "Delhi", "Delhi"),
    ("Hazrat Nizamuddin", "NZM", "New Delhi", "Delhi"),
    ("Anand Vihar Terminal", "ANVT", "New Delhi", "Delhi"),
    ("Chhatrapati Shivaji Maharaj Terminus", "CSTM", "Mumbai", "Maharashtra"),
    ("Mumbai Central", "BCT", "Mumbai", "Maharashtra"),
    ("Bandra Terminus", "BDTS", "Mumbai", "Maharashtra"),
    ("Lokmanya Tilak Terminus", "LTT", "Mumbai", "Maharashtra"),
    ("Howrah Junction", "HWH", "Kolkata", "West Bengal"),
    ("Sealdah", "SDAH", "Kolkata", "West Bengal"),
    ("Chennai Central", "MAS", "Chennai", "Tamil Nadu"),
    ("Chennai Egmore", "MS", "Chennai", "Tamil Nadu"),
    ("KSR Bengaluru", "SBC", "Bangalore", "Karnataka"),
    ("Yesvantpur Junction", "YPR", "Bangalore", "Karnataka"),
    ("Agra Cantonment", "AGC", "Agra", "Uttar Pradesh"),
    ("Ahmedabad Junction", "ADI", "Ahmedabad", "Gujarat"),
    ("Ambala Cantonment", "UMB", "Ambala", "Haryana"),
    ("Amritsar Junction", "ASR", "Amritsar", "Punjab"),
    ("Bhopal Junction", "BPL", "Bhopal", "Madhya Pradesh"),
    ("Chandigarh", "CDG", "Chandigarh", "Chandigarh"),
    ("Guwahati", "GHY", "Guwahati", "Assam"),
    ("Hyderabad Deccan", "HYB", "Hyderabad", "Telangana"),
    ("Jaipur Junction", "JP", "Jaipur", "Rajasthan"),
    ("Kanpur Central", "CNB", "Kanpur", "Uttar Pradesh"),
    ("Lucknow", "LKO", "Lucknow", "Uttar Pradesh"),
    ("Madurai Junction", "MDU", "Madurai", "Tamil Nadu"),
    ("Nagpur Junction", "NGP", "Nagpur", "Maharashtra"),
    ("Patna Junction", "PNBE", "Patna", "Bihar"),
    ("Pune Junction", "PUNE", "Pune", "Maharashtra"),
    ("Secunderabad Junction", "SC", "Secunderabad", "Telangana"),
    ("Thiruvananthapuram Central", "TVC", "Thiruvananthapuram", "Kerala"),
    ("Varanasi Junction", "BSB", "Varanasi", "Uttar Pradesh"),
    ("Vijayawada Junction", "BZA", "Vijayawada", "Andhra Pradesh"),
    ("Indore Junction", "INDB", "Indore", "Madhya Pradesh"),
    ("Surat", "ST", "Surat", "Gujarat"),
    ("Vadodara Junction", "BRC", "Vadodara", "Gujarat"),
    ("Rajkot Junction", "RJT", "Rajkot", "Gujarat"),
    ("Coimbatore Junction", "CBE", "Coimbatore", "Tamil Nadu"),
    ("Mysore Junction", "MYS", "Mysore", "Karnataka"),
    ("Jodhpur Junction", "JU", "Jodhpur", "Rajasthan")
]

INDIAN_CITIES = [
    ("Mumbai", "Maharashtra"), ("Delhi", "Delhi"), ("Bangalore", "Karnataka"),
    ("Hyderabad", "Telangana"), ("Ahmedabad", "Gujarat"), ("Chennai", "Tamil Nadu"),
    ("Kolkata", "West Bengal"), ("Pune", "Maharashtra"), ("Jaipur", "Rajasthan"),
    ("Lucknow", "Uttar Pradesh"), ("Kanpur", "Uttar Pradesh"), ("Nagpur", "Maharashtra"),
    ("Indore", "Madhya Pradesh"), ("Bhopal", "Madhya Pradesh"), ("Patna", "Bihar"),
    ("Vadodara", "Gujarat"), ("Ludhiana", "Punjab"), ("Agra", "Uttar Pradesh"),
    ("Nashik", "Maharashtra"), ("Meerut", "Uttar Pradesh"), ("Rajkot", "Gujarat"),
    ("Varanasi", "Uttar Pradesh"), ("Aurangabad", "Maharashtra"), ("Amritsar", "Punjab"),
    ("Allahabad", "Uttar Pradesh"), ("Ranchi", "Jharkhand"), ("Coimbatore", "Tamil Nadu"),
]

TRAIN_TYPES = [
    {
        "name": "Rajdhani Express", 
        "prefix": "12", 
        "total_seats": 900, 
        "base_fare": 2.20,
        "tatkal_multiplier": 1.30,
        "tatkal_pct": 0.10
    },
    {
        "name": "Shatabdi Express", 
        "prefix": "12", 
        "total_seats": 600, 
        "base_fare": 2.80,
        "tatkal_multiplier": 1.30,
        "tatkal_pct": 0.10
    },
    {
        "name": "Duronto Express", 
        "prefix": "22", 
        "total_seats": 950, 
        "base_fare": 1.75,
        "tatkal_multiplier": 1.30,
        "tatkal_pct": 0.10
    },
    {
        "name": "Mail/Express", 
        "prefix": "1", 
        "total_seats": 1400, 
        "base_fare": 0.60,
        "tatkal_multiplier": 1.30,
        "tatkal_pct": 0.10
    },
    {
        "name": "Passenger", 
        "prefix": "5", 
        "total_seats": 1600, 
        "base_fare": 0.30,
        "tatkal_multiplier": 1.10,
        "tatkal_pct": 0.05
    },
]

CLASS_CAPACITY_PERCENTAGES = {
    'AC1': 0.05,
    'AC2': 0.15,
    'AC3': 0.25,
    'SL': 0.35,
    '2S': 0.15,
    'CC': 0.05
}
