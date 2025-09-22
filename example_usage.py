#!/usr/bin/env python3
"""
Example Usage of Railway Functions
==================================

This file demonstrates how to use the railway_functions.py in your Flask application.
Run this within your Flask app context or import these functions in your routes.

To use in your Flask routes:
    from railway_functions import book_ticket, tatkal_booking, check_pnr_status

To run this example:
    python example_usage.py
"""

from railway_functions import *

def example_booking_workflow():
    """
    Example workflow showing various railway operations
    """
    print("🚂 Railway Functions Example Usage\n")
    print("=" * 50)
    
    # 1. Create a new user
    print("\n📝 1. Creating a new user...")
    user_result = create_user(
        username="john_doe", 
        email="john@example.com", 
        password="secure123"
    )
    print(f"✅ User Creation: {user_result['message']}")
    
    if user_result['success']:
        user_id = user_result['user_id']
    else:
        user_id = 1  # Use existing user
    
    # 2. Search for available trains
    print("\n🔍 2. Searching for trains...")
    trains = search_trains(
        from_station_id=1, 
        to_station_id=2, 
        journey_date="2025-01-15"
    )
    print(f"✅ Found {trains.get('count', 0)} trains")
    
    # 3. Check seat availability
    print("\n💺 3. Checking seat availability...")
    availability = check_seat_availability(
        train_id=1,
        from_station_id=1,
        to_station_id=2,
        journey_date="2025-01-15",
        coach_class="SL"
    )
    print(f"✅ Availability: {availability.get('status', 'Unknown')}")
    print(f"   Available seats: {availability.get('available_seats', 0)}")
    
    # 4. Book a regular ticket
    print("\n🎫 4. Booking a regular ticket...")
    booking = book_ticket(
        user_id=user_id,
        train_id=1,
        from_station_id=1,
        to_station_id=2,
        journey_date="2025-01-15",
        passengers=2,
        coach_class="SL"
    )
    
    if booking['success']:
        pnr = booking['pnr']
        print(f"✅ Booking Success! PNR: {pnr}")
        print(f"   Amount: ₹{booking['amount']}")
        
        # 5. Check PNR status
        print(f"\n📋 5. Checking PNR status for {pnr}...")
        pnr_status = check_pnr_status(pnr)
        if pnr_status['success']:
            print(f"✅ PNR Status: {pnr_status['status']}")
            print(f"   Train: {pnr_status['train_number']} - {pnr_status['train_name']}")
            print(f"   Journey: {pnr_status['from_station']} → {pnr_status['to_station']}")
            print(f"   Date: {pnr_status['journey_date']}")
        
    else:
        print(f"❌ Booking Failed: {booking['message']}")
    
    # 6. Try Tatkal booking
    print("\n⚡ 6. Attempting Tatkal booking...")
    tatkal = tatkal_booking(
        user_id=user_id,
        train_id=1,
        from_station_id=1,
        to_station_id=2,
        journey_date="2025-01-16",
        passengers=1,
        coach_class="AC3"
    )
    
    if tatkal['success']:
        print(f"✅ Tatkal Booking Success! PNR: {tatkal['pnr']}")
    else:
        print(f"⚠️  Tatkal Booking: {tatkal['message']}")
    
    # 7. Add to waitlist example
    print("\n⏳ 7. Adding to waitlist...")
    waitlist = add_to_waitlist(
        user_id=user_id,
        train_id=1,
        from_station_id=1,
        to_station_id=2,
        journey_date="2025-01-17",
        passengers=1,
        coach_class="AC2"
    )
    
    if waitlist['success']:
        print(f"✅ Added to waitlist! PNR: {waitlist['pnr']}")
        print(f"   Position: {waitlist['waitlist_position']}")
    
    # 8. Get user booking history
    print(f"\n📚 8. Getting booking history for user {user_id}...")
    history = get_user_bookings(user_id, limit=5)
    if history['success']:
        print(f"✅ Found {history['count']} bookings:")
        for booking in history['bookings'][:3]:  # Show first 3
            print(f"   • PNR: {booking['pnr']} | {booking['from_station']} → {booking['to_station']} | Status: {booking['status']}")
    
    # 9. Check train status
    print("\n🚆 9. Checking train status...")
    train_status = check_train_status("12345")
    if train_status['success']:
        print(f"✅ Train Status: {train_status.get('status', 'On Time')}")
    else:
        print(f"ℹ️  {train_status['message']}")
    
    print(f"\n🎉 Demo completed! All railway functions are working.")
    print("=" * 50)


def quick_booking_example():
    """
    Quick example for immediate booking
    """
    print("\n🚀 Quick Booking Example:")
    
    # Quick ticket booking
    result = book_ticket(
        user_id=1,  # Assuming user exists
        train_id=1,  # Assuming train exists
        from_station_id=1,
        to_station_id=2,
        journey_date="2025-02-01",
        passengers=1,
        coach_class="SL"
    )
    
    if result['success']:
        print(f"✅ Quick booking successful!")
        print(f"   PNR: {result['pnr']}")
        print(f"   Amount: ₹{result['amount']}")
        
        # Immediately check status
        status = check_pnr_status(result['pnr'])
        if status['success']:
            print(f"   Status: {status['status']}")
    else:
        print(f"❌ Quick booking failed: {result['message']}")


if __name__ == "__main__":
    # When run directly, show examples
    print("🎯 Railway Functions - Example Usage")
    print("\nNote: Run this within Flask app context for full functionality")
    print("To use in Flask routes:")
    print("  from railway_functions import book_ticket, tatkal_booking")
    print("\nAvailable Functions:")
    print("  • book_ticket() - Regular ticket booking")
    print("  • tatkal_booking() - Premium Tatkal booking")
    print("  • check_pnr_status() - Check PNR status")
    print("  • cancel_ticket() - Cancel existing booking")
    print("  • check_seat_availability() - Check seat availability")
    print("  • search_trains() - Search trains between stations")
    print("  • add_to_waitlist() - Add to waitlist")
    print("  • check_train_status() - Check train running status")
    print("  • create_user() - Create new user account")
    print("  • get_user_bookings() - Get user's booking history")
    
    # Show quick example
    try:
        # Uncomment the next line to run full demo (requires Flask context)
        # example_booking_workflow()
        pass
    except Exception as e:
        print(f"\nNote: {e}")
        print("Import this in your Flask app to use the functions!")