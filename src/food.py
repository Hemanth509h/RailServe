"""
Food & Catering System
Like IRCTC's e-catering service for ordering food on trains
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import and_
from datetime import datetime, timedelta
from .models import (
    Restaurant, MenuItem, FoodOrder, FoodOrderItem, 
    Booking, Station, TrainRoute, UserDietaryPreference,
    FoodReview, GroupFoodOrder, FoodOrderTracking, FoodRecommendation, db
)
from .app import app

food_bp = Blueprint('food', __name__)

@food_bp.route('/restaurants/<int:booking_id>')
@login_required
def restaurants_for_booking(booking_id):
    """Show available restaurants for a specific booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Verify user owns this booking
    if booking.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get stations on the route where food can be delivered
    train_routes = TrainRoute.query.filter_by(
        train_id=booking.train_id
    ).order_by(TrainRoute.sequence).all()
    
    # Find stations between from_station and to_station
    from_sequence = None
    to_sequence = None
    
    for route in train_routes:
        if route.station_id == booking.from_station_id:
            from_sequence = route.sequence
        if route.station_id == booking.to_station_id:
            to_sequence = route.sequence
    
    if from_sequence is None or to_sequence is None:
        flash('Route information not found', 'error')
        return redirect(url_for('booking.booking_history'))
    
    # Get stations between source and destination
    route_stations = TrainRoute.query.filter(
        and_(
            TrainRoute.train_id == booking.train_id,
            TrainRoute.sequence > from_sequence,
            TrainRoute.sequence <= to_sequence
        )
    ).order_by(TrainRoute.sequence).all()
    
    # Get restaurants at these stations
    station_ids = [route.station_id for route in route_stations]
    restaurants = Restaurant.query.filter(
        and_(
            Restaurant.station_id.in_(station_ids),
            Restaurant.active == True
        )
    ).order_by(Restaurant.rating.desc()).all()
    
    return render_template('food/restaurants.html', 
                         booking=booking, 
                         restaurants=restaurants,
                         route_stations=route_stations)

@food_bp.route('/menu/<int:restaurant_id>/<int:booking_id>')
@login_required
def restaurant_menu(restaurant_id, booking_id):
    """Show menu for a specific restaurant"""
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    booking = Booking.query.get_or_404(booking_id)
    
    # Verify user owns this booking
    if booking.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get menu items by category
    menu_items = MenuItem.query.filter(
        and_(
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.available == True
        )
    ).order_by(MenuItem.category, MenuItem.is_popular.desc(), MenuItem.name).all()
    
    # Group items by category
    menu_by_category = {}
    for item in menu_items:
        category = item.category or 'Other'
        if category not in menu_by_category:
            menu_by_category[category] = []
        menu_by_category[category].append(item)
    
    return render_template('food/menu.html',
                         restaurant=restaurant,
                         booking=booking,
                         menu_by_category=menu_by_category)

@food_bp.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    """Add item to food cart (stored in session)"""
    from flask import session
    
    item_id_str = request.form.get('item_id')
    quantity_str = request.form.get('quantity', '1')
    booking_id_str = request.form.get('booking_id')
    restaurant_id_str = request.form.get('restaurant_id')
    
    if not item_id_str or not booking_id_str or not restaurant_id_str:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        item_id = int(item_id_str)
        quantity = int(quantity_str if quantity_str else '1')
        booking_id = int(booking_id_str)
        restaurant_id = int(restaurant_id_str)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid parameter values'}), 400
    
    # Verify booking ownership
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    # Get menu item
    item = MenuItem.query.get_or_404(item_id)
    if not item.available:
        return jsonify({'error': 'Item not available'}), 400
    
    # Initialize cart in session
    if 'food_cart' not in session:
        session['food_cart'] = {}
    
    cart_key = f"{booking_id}_{restaurant_id}"
    if cart_key not in session['food_cart']:
        session['food_cart'][cart_key] = {
            'booking_id': booking_id,
            'restaurant_id': restaurant_id,
            'items': {},
            'total': 0.0
        }
    
    cart = session['food_cart'][cart_key]
    
    # Add or update item in cart
    if str(item_id) in cart['items']:
        cart['items'][str(item_id)]['quantity'] += quantity
    else:
        cart['items'][str(item_id)] = {
            'name': item.name,
            'price': item.price,
            'quantity': quantity,
            'food_type': item.food_type
        }
    
    # Update total
    cart['total'] = sum(
        item_data['price'] * item_data['quantity'] 
        for item_data in cart['items'].values()
    )
    
    session.modified = True
    
    return jsonify({
        'success': True,
        'cart_total': cart['total'],
        'item_count': len(cart['items'])
    })

@food_bp.route('/cart/<int:booking_id>/<int:restaurant_id>')
@login_required
def view_cart(booking_id, restaurant_id):
    """View food cart for specific booking and restaurant"""
    from flask import session
    
    booking = Booking.query.get_or_404(booking_id)
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    # Verify booking ownership
    if booking.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    cart_key = f"{booking_id}_{restaurant_id}"
    cart = session.get('food_cart', {}).get(cart_key, {'items': {}, 'total': 0.0})
    
    # Calculate delivery charges and taxes
    subtotal = cart['total']
    delivery_charge = restaurant.delivery_charge if subtotal < restaurant.minimum_order else 0.0
    tax_rate = 0.05  # 5% tax
    tax_amount = subtotal * tax_rate
    final_total = subtotal + delivery_charge + tax_amount
    
    return render_template('food/cart.html',
                         booking=booking,
                         restaurant=restaurant,
                         cart=cart,
                         subtotal=subtotal,
                         delivery_charge=delivery_charge,
                         tax_amount=tax_amount,
                         final_total=final_total)

@food_bp.route('/place_order', methods=['POST'])
@login_required
def place_food_order():
    """Place the food order"""
    from flask import session
    
    booking_id_str = request.form.get('booking_id')
    restaurant_id_str = request.form.get('restaurant_id')
    delivery_station_id_str = request.form.get('delivery_station_id')
    
    if not booking_id_str or not restaurant_id_str or not delivery_station_id_str:
        flash('Missing required information', 'error')
        return redirect(url_for('index'))
    
    try:
        booking_id = int(booking_id_str)
        restaurant_id = int(restaurant_id_str)
        delivery_station_id = int(delivery_station_id_str)
    except (ValueError, TypeError):
        flash('Invalid form data', 'error')
        return redirect(url_for('index'))
    contact_number = request.form.get('contact_number')
    coach_number = request.form.get('coach_number')
    seat_number = request.form.get('seat_number')
    special_instructions = request.form.get('special_instructions', '')
    
    # Verify booking ownership
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    # Get cart from session
    cart_key = f"{booking_id}_{restaurant_id}"
    cart = session.get('food_cart', {}).get(cart_key)
    
    if not cart or not cart['items']:
        flash('Cart is empty', 'error')
        return redirect(url_for('food.restaurants_for_booking', booking_id=booking_id))
    
    # Calculate totals
    subtotal = cart['total']
    delivery_charge = restaurant.delivery_charge if subtotal < restaurant.minimum_order else 0.0
    tax_amount = subtotal * 0.05  # 5% tax
    total_amount = subtotal + delivery_charge + tax_amount
    
    try:
        # Create food order
        food_order = FoodOrder(
            booking_id=booking_id,
            user_id=current_user.id,
            restaurant_id=restaurant_id,
            delivery_station_id=delivery_station_id,
            total_amount=total_amount,
            delivery_charge=delivery_charge,
            tax_amount=tax_amount,
            special_instructions=special_instructions,
            contact_number=contact_number,
            coach_number=coach_number,
            seat_number=seat_number,
            status='confirmed',
            payment_status='paid'  # Assuming payment integration
        )
        
        db.session.add(food_order)
        db.session.flush()  # Get the ID
        
        # Add order items
        for item_id, item_data in cart['items'].items():
            menu_item = MenuItem.query.get(int(item_id))
            if menu_item:
                order_item = FoodOrderItem(
                    food_order_id=food_order.id,
                    menu_item_id=int(item_id),
                    quantity=item_data['quantity'],
                    unit_price=item_data['price'],
                    total_price=item_data['price'] * item_data['quantity']
                )
                db.session.add(order_item)
        
        db.session.commit()
        
        # Clear cart
        if 'food_cart' in session and cart_key in session['food_cart']:
            del session['food_cart'][cart_key]
            session.modified = True
        
        flash(f'Food order #{food_order.order_number} placed successfully!', 'success')
        return redirect(url_for('food.order_status', order_id=food_order.id))
        
    except Exception as e:
        db.session.rollback()
        flash('Error placing order. Please try again.', 'error')
        return redirect(url_for('food.view_cart', booking_id=booking_id, restaurant_id=restaurant_id))

@food_bp.route('/order/<int:order_id>')
@login_required
def order_status(order_id):
    """Show food order status"""
    order = FoodOrder.query.get_or_404(order_id)
    
    # Verify user owns this order
    if order.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    return render_template('food/order_status.html', order=order)

@food_bp.route('/my_orders')
@login_required
def my_food_orders():
    """Show user's food orders"""
    orders = FoodOrder.query.filter_by(user_id=current_user.id)\
                           .order_by(FoodOrder.created_at.desc()).all()
    
    return render_template('food/my_orders.html', orders=orders)

# Admin routes for managing restaurants and menus

@food_bp.route('/admin/restaurants')
@login_required
def admin_restaurants():
    """Admin: Manage restaurants"""
    if not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    restaurants = Restaurant.query.order_by(Restaurant.name).all()
    stations = Station.query.order_by(Station.name).all()
    
    return render_template('food/admin_restaurants.html', 
                         restaurants=restaurants, 
                         stations=stations)

@food_bp.route('/admin/menu/<int:restaurant_id>')
@login_required  
def admin_menu(restaurant_id):
    """Admin: Manage restaurant menu"""
    if not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id)\
                              .order_by(MenuItem.category, MenuItem.name).all()
    
    return render_template('food/admin_menu.html', 
                         restaurant=restaurant, 
                         menu_items=menu_items)

# Enhanced Food Booking Features

@food_bp.route('/dietary_preferences', methods=['GET', 'POST'])
@login_required
def dietary_preferences():
    """Manage user dietary preferences and restrictions"""
    user_prefs = UserDietaryPreference.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        dietary_restrictions = request.form.getlist('dietary_restrictions')
        allergies = request.form.getlist('allergies')
        cuisine_preferences = request.form.getlist('cuisine_preferences')
        spice_level = request.form.get('spice_level', 'Medium')
        special_notes = request.form.get('special_notes', '')
        
        import json
        
        try:
            if user_prefs:
                # Update existing preferences
                user_prefs.dietary_restrictions = json.dumps(dietary_restrictions)
                user_prefs.allergies = json.dumps(allergies)
                user_prefs.cuisine_preferences = json.dumps(cuisine_preferences)
                user_prefs.spice_level = spice_level
                user_prefs.special_notes = special_notes
                user_prefs.updated_at = datetime.utcnow()
            else:
                # Create new preferences
                user_prefs = UserDietaryPreference(
                    user_id=current_user.id,
                    dietary_restrictions=json.dumps(dietary_restrictions),
                    allergies=json.dumps(allergies),
                    cuisine_preferences=json.dumps(cuisine_preferences),
                    spice_level=spice_level,
                    special_notes=special_notes
                )
                db.session.add(user_prefs)
            
            db.session.commit()
            flash('Dietary preferences updated successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating preferences. Please try again.', 'error')
    
    return render_template('food/dietary_preferences.html', user_prefs=user_prefs)

@food_bp.route('/enhanced_restaurants/<int:booking_id>')
@login_required
def enhanced_restaurants(booking_id):
    """Enhanced restaurant browsing with search and filtering"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Verify user owns this booking
    if booking.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get search and filter parameters
    search_query = request.args.get('search', '')
    cuisine_filter = request.args.get('cuisine', '')
    min_rating = request.args.get('min_rating', 0, type=float)
    dietary_filter = request.args.get('dietary', '')
    sort_by = request.args.get('sort', 'rating')  # rating, delivery_time, popularity
    
    # Get user dietary preferences
    user_prefs = UserDietaryPreference.query.filter_by(user_id=current_user.id).first()
    user_dietary_restrictions = user_prefs.get_dietary_restrictions() if user_prefs else []
    
    # Get route stations and restaurants (same logic as original)
    train_routes = TrainRoute.query.filter_by(train_id=booking.train_id).order_by(TrainRoute.sequence).all()
    from_sequence = to_sequence = None
    
    for route in train_routes:
        if route.station_id == booking.from_station_id:
            from_sequence = route.sequence
        if route.station_id == booking.to_station_id:
            to_sequence = route.sequence
    
    if from_sequence is None or to_sequence is None:
        flash('Route information not found', 'error')
        return redirect(url_for('booking.booking_history'))
    
    route_stations = TrainRoute.query.filter(
        and_(
            TrainRoute.train_id == booking.train_id,
            TrainRoute.sequence > from_sequence,
            TrainRoute.sequence <= to_sequence
        )
    ).order_by(TrainRoute.sequence).all()
    
    station_ids = [route.station_id for route in route_stations]
    
    # Build query with filters
    query = Restaurant.query.filter(
        and_(
            Restaurant.station_id.in_(station_ids),
            Restaurant.active == True
        )
    )
    
    # Apply filters
    if search_query:
        query = query.filter(Restaurant.name.contains(search_query))
    if cuisine_filter:
        query = query.filter(Restaurant.cuisine_type.contains(cuisine_filter))
    if min_rating > 0:
        query = query.filter(Restaurant.rating >= min_rating)
    
    # Apply sorting
    if sort_by == 'rating':
        query = query.order_by(Restaurant.rating.desc())
    elif sort_by == 'delivery_time':
        query = query.order_by(Restaurant.delivery_time.asc())
    else:
        query = query.order_by(Restaurant.rating.desc())
    
    restaurants = query.all()
    
    # Get recommendations for this user
    recommendations = get_smart_recommendations(current_user.id, booking_id)
    
    return render_template('food/enhanced_restaurants.html', 
                         booking=booking, 
                         restaurants=restaurants,
                         route_stations=route_stations,
                         recommendations=recommendations,
                         user_dietary_restrictions=user_dietary_restrictions)

@food_bp.route('/smart_menu/<int:restaurant_id>/<int:booking_id>')
@login_required
def smart_menu(restaurant_id, booking_id):
    """Enhanced menu with smart recommendations and dietary filtering"""
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    booking = Booking.query.get_or_404(booking_id)
    
    # Verify user owns this booking
    if booking.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get user dietary preferences
    user_prefs = UserDietaryPreference.query.filter_by(user_id=current_user.id).first()
    dietary_restrictions = user_prefs.get_dietary_restrictions() if user_prefs else []
    
    # Get menu items with filtering
    dietary_filter = request.args.get('dietary_filter', 'all')
    category_filter = request.args.get('category', '')
    
    query = MenuItem.query.filter(
        and_(
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.available == True
        )
    )
    
    if category_filter:
        query = query.filter(MenuItem.category == category_filter)
    
    menu_items = query.order_by(MenuItem.category, MenuItem.is_popular.desc(), MenuItem.name).all()
    
    # Filter by dietary preferences if requested
    if dietary_filter == 'compatible' and dietary_restrictions:
        menu_items = [item for item in menu_items if item.matches_dietary_preferences(dietary_restrictions)]
    
    # Group items by category and add recommendations
    menu_by_category = {}
    current_time = datetime.now()
    
    for item in menu_items:
        category = item.category or 'Other'
        if category not in menu_by_category:
            menu_by_category[category] = []
        
        # Add recommendation score
        item.recommendation_score = item.get_recommendation_score(current_time)
        item.average_rating = item.get_average_rating()
        item.dietary_tags = item.get_dietary_tags()
        
        menu_by_category[category].append(item)
    
    # Sort items within each category by recommendation score
    for category in menu_by_category:
        menu_by_category[category].sort(key=lambda x: x.recommendation_score, reverse=True)
    
    return render_template('food/smart_menu.html',
                         restaurant=restaurant,
                         booking=booking,
                         menu_by_category=menu_by_category,
                         user_dietary_restrictions=dietary_restrictions)

@food_bp.route('/group_food_order/<int:group_booking_id>', methods=['GET', 'POST'])
@login_required
def group_food_order(group_booking_id):
    """Coordinate food orders for group bookings"""
    from .models import GroupBooking
    
    group_booking = GroupBooking.query.get_or_404(group_booking_id)
    
    # Verify access
    is_member = any(booking.user_id == current_user.id for booking in group_booking.individual_bookings)
    if group_booking.group_leader_id != current_user.id and not is_member:
        flash('Access denied', 'error')
        return redirect(url_for('groups.my_groups'))
    
    if request.method == 'POST':
        restaurant_id = request.form.get('restaurant_id')
        delivery_station_id = request.form.get('delivery_station_id')
        special_instructions = request.form.get('special_instructions', '')
        deadline_hours = request.form.get('deadline_hours', 2, type=int)
        
        if not restaurant_id or not delivery_station_id:
            flash('Please select restaurant and delivery station', 'error')
            return redirect(request.url)
        
        try:
            # Create group food order
            deadline = datetime.utcnow() + timedelta(hours=deadline_hours)
            
            group_food_order = GroupFoodOrder(
                group_booking_id=group_booking_id,
                coordinator_id=current_user.id,
                restaurant_id=int(restaurant_id),
                delivery_station_id=int(delivery_station_id),
                deadline_for_orders=deadline,
                special_instructions=special_instructions
            )
            
            db.session.add(group_food_order)
            db.session.commit()
            
            flash(f'Group food order #{group_food_order.group_order_number} created! Deadline: {deadline.strftime("%Y-%m-%d %H:%M")}', 'success')
            return redirect(url_for('food.manage_group_food_order', group_order_id=group_food_order.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error creating group food order. Please try again.', 'error')
    
    # Get available restaurants and stations
    restaurants = Restaurant.query.filter_by(active=True).order_by(Restaurant.rating.desc()).all()
    stations = Station.query.order_by(Station.name).all()
    
    return render_template('food/group_food_order.html',
                         group_booking=group_booking,
                         restaurants=restaurants,
                         stations=stations)

@food_bp.route('/enhanced_tracking/<int:order_id>')
@login_required
def enhanced_tracking(order_id):
    """Enhanced real-time order tracking"""
    order = FoodOrder.query.get_or_404(order_id)
    
    # Verify user owns this order
    if order.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get detailed tracking updates
    tracking_updates = FoodOrderTracking.query.filter_by(food_order_id=order_id)\
                                               .order_by(FoodOrderTracking.created_at.desc()).all()
    
    # Calculate progress percentage
    status_progress = {
        'pending': 10,
        'confirmed': 25,
        'preparing': 50,
        'dispatched': 75,
        'delivered': 100,
        'cancelled': 0
    }
    
    progress_percentage = status_progress.get(order.status, 0)
    
    return render_template('food/enhanced_tracking.html',
                         order=order,
                         tracking_updates=tracking_updates,
                         progress_percentage=progress_percentage)

@food_bp.route('/review_order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def review_order(order_id):
    """Submit review and rating for completed food order"""
    order = FoodOrder.query.get_or_404(order_id)
    
    # Verify user owns this order and it's completed
    if order.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if order.status != 'delivered':
        flash('You can only review completed orders', 'error')
        return redirect(url_for('food.order_status', order_id=order_id))
    
    # Check if already reviewed
    existing_review = FoodReview.query.filter_by(food_order_id=order_id).first()
    if existing_review:
        flash('You have already reviewed this order', 'info')
        return redirect(url_for('food.order_status', order_id=order_id))
    
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        review_text = request.form.get('review_text', '')
        food_quality = request.form.get('food_quality', type=int)
        delivery_speed = request.form.get('delivery_speed', type=int)
        packaging_quality = request.form.get('packaging_quality', type=int)
        would_recommend = request.form.get('would_recommend') == 'on'
        
        if not rating or rating < 1 or rating > 5:
            flash('Please provide a valid rating (1-5 stars)', 'error')
            return render_template('food/review_order.html', order=order)
        
        try:
            review = FoodReview(
                user_id=current_user.id,
                restaurant_id=order.restaurant_id,
                food_order_id=order_id,
                rating=rating,
                review_text=review_text,
                food_quality=food_quality,
                delivery_speed=delivery_speed,
                packaging_quality=packaging_quality,
                would_recommend=would_recommend
            )
            
            db.session.add(review)
            db.session.commit()
            
            flash('Thank you for your review!', 'success')
            return redirect(url_for('food.order_status', order_id=order_id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error submitting review. Please try again.', 'error')
    
    return render_template('food/review_order.html', order=order)

def get_smart_recommendations(user_id, booking_id):
    """Generate smart food recommendations for user"""
    current_time = datetime.now()
    
    # Get user preferences
    user_prefs = UserDietaryPreference.query.filter_by(user_id=user_id).first()
    dietary_restrictions = user_prefs.get_dietary_restrictions() if user_prefs else []
    
    # Get popular items from user's past orders
    past_orders = FoodOrder.query.filter_by(user_id=user_id).all()
    past_item_ids = []
    for order in past_orders:
        past_item_ids.extend([item.menu_item_id for item in order.items])
    
    # Get menu items that match dietary preferences and have high recommendation scores
    recommendations = []
    
    # Time-based recommendations
    hour = current_time.hour
    if 6 <= hour <= 10:
        category_filter = 'Breakfast'
    elif 11 <= hour <= 15:
        category_filter = 'Lunch'
    elif 18 <= hour <= 22:
        category_filter = 'Dinner'
    else:
        category_filter = 'Snacks'
    
    # Get top-rated items in appropriate category
    menu_items = MenuItem.query.filter(
        and_(
            MenuItem.category == category_filter,
            MenuItem.available == True
        )
    ).limit(5).all()
    
    for item in menu_items:
        if item.matches_dietary_preferences(dietary_restrictions):
            score = item.get_recommendation_score(current_time)
            
            # Boost score if user hasn't tried this item
            if item.id not in past_item_ids:
                score += 1
            
            recommendations.append({
                'item': item,
                'score': score,
                'reason': f'Perfect for {category_filter.lower()} time!'
            })
    
    # Sort by score and return top 3
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations[:3]