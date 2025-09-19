#!/usr/bin/env python3
"""
Populate sample food data for testing the Food & Catering system
"""
import os
import sys

# Set environment variables
os.environ['SESSION_SECRET'] = 'railway-secret-key-2025-replit'

# Add src to Python path
sys.path.insert(0, 'src')

from src.app import app, db
from src.models import Restaurant, MenuItem, Station
from datetime import datetime

# Sample restaurants data
restaurants_data = [
    {
        'name': 'Rajdhani Foods',
        'station': 'New Delhi',
        'cuisine_type': 'North Indian',
        'rating': 4.5,
        'delivery_time': 25,
        'minimum_order': 100.0,
        'delivery_charge': 20.0
    },
    {
        'name': 'South Express Kitchen',
        'station': 'Chennai Central',
        'cuisine_type': 'South Indian',
        'rating': 4.3,
        'delivery_time': 20,
        'minimum_order': 80.0,
        'delivery_charge': 15.0
    },
    {
        'name': 'Mumbai Tiffin Center',
        'station': 'Chhatrapati Shivaji Terminus',
        'cuisine_type': 'Maharashtrian',
        'rating': 4.4,
        'delivery_time': 30,
        'minimum_order': 120.0,
        'delivery_charge': 25.0
    }
]

# Sample menu items
menu_items_data = {
    'Rajdhani Foods': [
        {'name': 'Dal Makhani', 'category': 'Main Course', 'price': 180.0, 'food_type': 'Vegetarian', 'description': 'Rich and creamy black lentil curry', 'is_popular': True},
        {'name': 'Butter Chicken', 'category': 'Main Course', 'price': 250.0, 'food_type': 'Non-Vegetarian', 'description': 'Tender chicken in tomato-based curry', 'is_popular': True},
        {'name': 'Paneer Butter Masala', 'category': 'Main Course', 'price': 220.0, 'food_type': 'Vegetarian', 'description': 'Cottage cheese in rich tomato gravy'},
        {'name': 'Chicken Biryani', 'category': 'Rice & Biryani', 'price': 280.0, 'food_type': 'Non-Vegetarian', 'description': 'Fragrant basmati rice with spiced chicken', 'is_popular': True},
        {'name': 'Veg Biryani', 'category': 'Rice & Biryani', 'price': 220.0, 'food_type': 'Vegetarian', 'description': 'Aromatic rice with mixed vegetables'},
        {'name': 'Naan Bread', 'category': 'Breads', 'price': 45.0, 'food_type': 'Vegetarian', 'description': 'Soft leavened flatbread'},
        {'name': 'Masala Chai', 'category': 'Beverages', 'price': 30.0, 'food_type': 'Vegetarian', 'description': 'Spiced Indian tea'},
        {'name': 'Gulab Jamun', 'category': 'Desserts', 'price': 60.0, 'food_type': 'Vegetarian', 'description': 'Sweet milk dumplings in syrup'}
    ],
    'South Express Kitchen': [
        {'name': 'Masala Dosa', 'category': 'Breakfast', 'price': 120.0, 'food_type': 'Vegetarian', 'description': 'Crispy crepe with spiced potato filling', 'is_popular': True},
        {'name': 'Idli Sambar', 'category': 'Breakfast', 'price': 80.0, 'food_type': 'Vegetarian', 'description': 'Steamed rice cakes with lentil curry', 'is_popular': True},
        {'name': 'Chicken Chettinad', 'category': 'Main Course', 'price': 280.0, 'food_type': 'Non-Vegetarian', 'description': 'Spicy chicken curry from Tamil Nadu'},
        {'name': 'Fish Curry Rice', 'category': 'Main Course', 'price': 220.0, 'food_type': 'Non-Vegetarian', 'description': 'Traditional fish curry with steamed rice'},
        {'name': 'Sambar Rice', 'category': 'Rice & Curry', 'price': 150.0, 'food_type': 'Vegetarian', 'description': 'Rice with lentil and vegetable curry'},
        {'name': 'Coconut Chutney', 'category': 'Sides', 'price': 25.0, 'food_type': 'Vegetarian', 'description': 'Fresh coconut chutney'},
        {'name': 'Filter Coffee', 'category': 'Beverages', 'price': 40.0, 'food_type': 'Vegetarian', 'description': 'Traditional South Indian coffee', 'is_popular': True},
        {'name': 'Rasmalai', 'category': 'Desserts', 'price': 80.0, 'food_type': 'Vegetarian', 'description': 'Cottage cheese dumplings in sweetened milk'}
    ],
    'Mumbai Tiffin Center': [
        {'name': 'Vada Pav', 'category': 'Snacks', 'price': 40.0, 'food_type': 'Vegetarian', 'description': 'Mumbai\'s famous potato fritter burger', 'is_popular': True},
        {'name': 'Pav Bhaji', 'category': 'Main Course', 'price': 120.0, 'food_type': 'Vegetarian', 'description': 'Spiced vegetable curry with bread rolls', 'is_popular': True},
        {'name': 'Bombay Duck Curry', 'category': 'Main Course', 'price': 200.0, 'food_type': 'Non-Vegetarian', 'description': 'Traditional Mumbai fish curry'},
        {'name': 'Misal Pav', 'category': 'Breakfast', 'price': 100.0, 'food_type': 'Vegetarian', 'description': 'Spicy sprouts curry with bread'},
        {'name': 'Chicken Koliwada', 'category': 'Snacks', 'price': 180.0, 'food_type': 'Non-Vegetarian', 'description': 'Spicy fried chicken pieces'},
        {'name': 'Solkadhi', 'category': 'Beverages', 'price': 50.0, 'food_type': 'Vegetarian', 'description': 'Coconut and kokum drink'},
        {'name': 'Cutting Chai', 'category': 'Beverages', 'price': 20.0, 'food_type': 'Vegetarian', 'description': 'Mumbai style tea'},
        {'name': 'Shrikhand', 'category': 'Desserts', 'price': 70.0, 'food_type': 'Vegetarian', 'description': 'Sweetened yogurt dessert'}
    ]
}

def populate_food_data():
    with app.app_context():
        print("🍽️ Populating food & catering data...")
        
        # Clear existing food data
        db.session.query(MenuItem).delete()
        db.session.query(Restaurant).delete()
        db.session.commit()
        
        created_restaurants = 0
        created_items = 0
        
        for restaurant_info in restaurants_data:
            # Find the station
            station = Station.query.filter_by(name=restaurant_info['station']).first()
            if not station:
                print(f"⚠️ Station '{restaurant_info['station']}' not found, skipping...")
                continue
            
            # Create restaurant
            restaurant = Restaurant(
                name=restaurant_info['name'],
                station_id=station.id,
                cuisine_type=restaurant_info['cuisine_type'],
                rating=restaurant_info['rating'],
                delivery_time=restaurant_info['delivery_time'],
                minimum_order=restaurant_info['minimum_order'],
                delivery_charge=restaurant_info['delivery_charge'],
                contact_number='+91-9876543210',
                email=f"{restaurant_info['name'].lower().replace(' ', '')}@food.com"
            )
            
            db.session.add(restaurant)
            db.session.flush()  # Get the ID
            created_restaurants += 1
            
            # Add menu items for this restaurant
            items = menu_items_data.get(restaurant_info['name'], [])
            for item_info in items:
                menu_item = MenuItem(
                    restaurant_id=restaurant.id,
                    name=item_info['name'],
                    category=item_info['category'],
                    price=item_info['price'],
                    food_type=item_info['food_type'],
                    description=item_info['description'],
                    is_popular=item_info.get('is_popular', False),
                    preparation_time=15
                )
                db.session.add(menu_item)
                created_items += 1
        
        db.session.commit()
        
        print(f"✅ Created {created_restaurants} restaurants")
        print(f"✅ Created {created_items} menu items")
        print("🎉 Food data population complete!")

if __name__ == '__main__':
    populate_food_data()