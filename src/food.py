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
    Booking, Station, TrainRoute, db
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