import csv
import random

MAJOR_STATIONS = [
    ("New Delhi", "NDLS", "New Delhi", "Delhi"),
    ("Old Delhi", "DLI", "Delhi", "Delhi"),
    ("Hazrat Nizamuddin", "NZM", "New Delhi", "Delhi"),
    ("Anand Vihar Terminal", "ANVT", "New Delhi", "Delhi"),
    ("Sarai Rohilla", "DEE", "New Delhi", "Delhi"),
    ("Chhatrapati Shivaji Maharaj Terminus", "CSTM", "Mumbai", "Maharashtra"),
    ("Mumbai Central", "BCT", "Mumbai", "Maharashtra"),
    ("Bandra Terminus", "BDTS", "Mumbai", "Maharashtra"),
    ("Lokmanya Tilak Terminus", "LTT", "Mumbai", "Maharashtra"),
    ("Dadar Western", "DDR", "Mumbai", "Maharashtra"),
    ("Howrah Junction", "HWH", "Kolkata", "West Bengal"),
    ("Sealdah", "SDAH", "Kolkata", "West Bengal"),
    ("Kolkata", "KOAA", "Kolkata", "West Bengal"),
    ("Chennai Central", "MAS", "Chennai", "Tamil Nadu"),
    ("Chennai Egmore", "MS", "Chennai", "Tamil Nadu"),
    ("KSR Bengaluru", "SBC", "Bangalore", "Karnataka"),
    ("Yesvantpur Junction", "YPR", "Bangalore", "Karnataka"),
    ("Bangalore Cantonment", "BNC", "Bangalore", "Karnataka"),
    ("Krishnarajapuram", "KJM", "Bangalore", "Karnataka"),
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
]

INDIAN_CITIES = [
    ("Mumbai", "Maharashtra"), ("Delhi", "Delhi"), ("Bangalore", "Karnataka"),
    ("Hyderabad", "Telangana"), ("Ahmedabad", "Gujarat"), ("Chennai", "Tamil Nadu"),
    ("Kolkata", "West Bengal"), ("Pune", "Maharashtra"), ("Jaipur", "Rajasthan"),
    ("Lucknow", "Uttar Pradesh"), ("Kanpur", "Uttar Pradesh"), ("Nagpur", "Maharashtra"),
    ("Indore", "Madhya Pradesh"), ("Thane", "Maharashtra"), ("Bhopal", "Madhya Pradesh"),
    ("Visakhapatnam", "Andhra Pradesh"), ("Patna", "Bihar"), ("Vadodara", "Gujarat"),
    ("Ghaziabad", "Uttar Pradesh"), ("Ludhiana", "Punjab"), ("Agra", "Uttar Pradesh"),
    ("Nashik", "Maharashtra"), ("Faridabad", "Haryana"), ("Meerut", "Uttar Pradesh"),
    ("Rajkot", "Gujarat"), ("Varanasi", "Uttar Pradesh"), ("Srinagar", "Jammu and Kashmir"),
    ("Aurangabad", "Maharashtra"), ("Dhanbad", "Jharkhand"), ("Amritsar", "Punjab"),
    ("Allahabad", "Uttar Pradesh"), ("Ranchi", "Jharkhand"), ("Howrah", "West Bengal"),
    ("Coimbatore", "Tamil Nadu"), ("Jabalpur", "Madhya Pradesh"), ("Gwalior", "Madhya Pradesh"),
    ("Vijayawada", "Andhra Pradesh"), ("Jodhpur", "Rajasthan"), ("Madurai", "Tamil Nadu"),
    ("Raipur", "Chhattisgarh"), ("Kota", "Rajasthan"), ("Chandigarh", "Chandigarh"),
    ("Guwahati", "Assam"), ("Solapur", "Maharashtra"), ("Tiruchirappalli", "Tamil Nadu"),
    ("Bareilly", "Uttar Pradesh"), ("Mysore", "Karnataka"), ("Tiruppur", "Tamil Nadu"),
    ("Gurgaon", "Haryana"), ("Aligarh", "Uttar Pradesh"), ("Jalandhar", "Punjab"),
    ("Bhubaneswar", "Odisha"), ("Salem", "Tamil Nadu"), ("Warangal", "Telangana"),
    ("Guntur", "Andhra Pradesh"), ("Saharanpur", "Uttar Pradesh"), ("Gorakhpur", "Uttar Pradesh"),
    ("Bikaner", "Rajasthan"), ("Amravati", "Maharashtra"), ("Noida", "Uttar Pradesh"),
    ("Jamshedpur", "Jharkhand"), ("Bhilai", "Chhattisgarh"), ("Cuttack", "Odisha"),
    ("Firozabad", "Uttar Pradesh"), ("Kochi", "Kerala"), ("Bhavnagar", "Gujarat"),
    ("Dehradun", "Uttarakhand"), ("Durgapur", "West Bengal"), ("Asansol", "West Bengal"),
    ("Nanded", "Maharashtra"), ("Kolhapur", "Maharashtra"), ("Ajmer", "Rajasthan"),
    ("Jamnagar", "Gujarat"), ("Ujjain", "Madhya Pradesh"), ("Siliguri", "West Bengal"),
    ("Jhansi", "Uttar Pradesh"), ("Jammu", "Jammu and Kashmir"), ("Mangalore", "Karnataka"),
    ("Erode", "Tamil Nadu"), ("Belgaum", "Karnataka"), ("Tirunelveli", "Tamil Nadu"),
    ("Gaya", "Bihar"), ("Udaipur", "Rajasthan"), ("Kozhikode", "Kerala"),
    ("Kurnool", "Andhra Pradesh"), ("Rajahmundry", "Andhra Pradesh"), ("Bokaro", "Jharkhand"),
    ("Agartala", "Tripura"), ("Bhagalpur", "Bihar"), ("Latur", "Maharashtra"),
    ("Dhule", "Maharashtra"), ("Rohtak", "Haryana"), ("Korba", "Chhattisgarh"),
    ("Bhilwara", "Rajasthan"), ("Muzaffarpur", "Bihar"), ("Mathura", "Uttar Pradesh"),
    ("Kollam", "Kerala"), ("Bilaspur", "Chhattisgarh"), ("Shahjahanpur", "Uttar Pradesh"),
    ("Satara", "Maharashtra"), ("Rampur", "Uttar Pradesh"), ("Alwar", "Rajasthan"),
    ("Khammam", "Telangana"), ("Darbhanga", "Bihar"), ("Panipat", "Haryana"),
    ("Karnal", "Haryana"), ("Bathinda", "Punjab"), ("Jalna", "Maharashtra"),
    ("Purnia", "Bihar"), ("Satna", "Madhya Pradesh"), ("Sonipat", "Haryana"),
    ("Durg", "Chhattisgarh"), ("Imphal", "Manipur"), ("Ratlam", "Madhya Pradesh"),
]

def generate_station_code(city_name, existing_codes):
    base_code = ''.join([c[0] for c in city_name.split()[:3]]).upper()
    if len(base_code) < 3:
        base_code = city_name[:3].upper()
    
    code = base_code[:4]
    counter = 1
    while code in existing_codes:
        code = base_code[:3] + str(counter)
        counter += 1
    
    return code

def create_stations_csv():
    stations = []
    existing_codes = set()
    existing_names = set()
    
    for name, code, city, state in MAJOR_STATIONS:
        stations.append({
            'name': name,
            'code': code,
            'city': city,
            'state': state,
            'active': True
        })
        existing_codes.add(code)
        existing_names.add(name)
    
    station_types = ['Junction', 'Central', 'Terminal', 'City', 'Cantonment', 'Road', 'Station']
    
    for city, state in INDIAN_CITIES:
        for stype in station_types:
            if len(stations) >= 1000:
                break
            station_name = f"{city} {stype}"
            if station_name in existing_names:
                continue
            code = generate_station_code(f"{city}{stype}", existing_codes)
            stations.append({
                'name': station_name,
                'code': code,
                'city': city,
                'state': state,
                'active': True
            })
            existing_codes.add(code)
            existing_names.add(station_name)
        if len(stations) >= 1000:
            break
    
    with open('data/stations.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'code', 'city', 'state', 'active'])
        writer.writeheader()
        writer.writerows(stations)
    
    print(f"Created {len(stations)} stations")
    return stations

def create_trains_csv():
    trains = []
    
    train_types = [
        {"name": "Rajdhani Express", "prefix": "12", "total_seats": 900, "fare": 1.8, "tatkal_pct": 0.1},
        {"name": "Shatabdi Express", "prefix": "12", "total_seats": 600, "fare": 2.0, "tatkal_pct": 0.1},
        {"name": "Duronto Express", "prefix": "22", "total_seats": 950, "fare": 1.7, "tatkal_pct": 0.1},
        {"name": "Vande Bharat Express", "prefix": "22", "total_seats": 530, "fare": 2.5, "tatkal_pct": 0.1},
        {"name": "Humsafar Express", "prefix": "22", "total_seats": 850, "fare": 1.5, "tatkal_pct": 0.1},
        {"name": "Tejas Express", "prefix": "22", "total_seats": 580, "fare": 2.3, "tatkal_pct": 0.1},
        {"name": "Garib Rath", "prefix": "12", "total_seats": 1100, "fare": 1.2, "tatkal_pct": 0.1},
        {"name": "Jan Shatabdi", "prefix": "12", "total_seats": 650, "fare": 1.4, "tatkal_pct": 0.1},
        {"name": "Superfast Express", "prefix": "12", "total_seats": 1200, "fare": 1.0, "tatkal_pct": 0.1},
        {"name": "Express", "prefix": "1", "total_seats": 1400, "fare": 0.8, "tatkal_pct": 0.1},
        {"name": "Mail", "prefix": "1", "total_seats": 1350, "fare": 0.85, "tatkal_pct": 0.1},
        {"name": "Passenger", "prefix": "5", "total_seats": 1600, "fare": 0.6, "tatkal_pct": 0.05},
    ]
    
    train_number = 10001
    
    for _ in range(1500):
        train_type = random.choice(train_types)
        source = random.choice(MAJOR_STATIONS[:20])
        dest = random.choice([s for s in MAJOR_STATIONS[:30] if s != source])
        
        number = f"{train_type['prefix']}{train_number % 10000:04d}"
        name = f"{source[2]}-{dest[2]} {train_type['name']}"
        total_seats = train_type['total_seats'] + random.randint(-100, 100)
        tatkal_seats = int(total_seats * train_type['tatkal_pct'])
        fare = train_type['fare'] + random.uniform(-0.2, 0.2)
        tatkal_fare = fare * random.uniform(1.5, 2.0)
        
        trains.append({
            'number': number,
            'name': name,
            'total_seats': total_seats,
            'fare_per_km': round(fare, 2),
            'tatkal_seats': tatkal_seats,
            'tatkal_fare_per_km': round(tatkal_fare, 2),
            'active': True
        })
        
        train_number += 1
    
    with open('data/trains.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['number', 'name', 'total_seats', 'fare_per_km', 'tatkal_seats', 'tatkal_fare_per_km', 'active'])
        writer.writeheader()
        writer.writerows(trains)
    
    print(f"Created {len(trains)} trains")
    return trains

if __name__ == '__main__':
    print("Generating CSV files...")
    create_stations_csv()
    create_trains_csv()
    print("Done!")
