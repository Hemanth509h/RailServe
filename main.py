"""
=================================================================================
RailServe Main Application Entry Point
=================================================================================
This module contains the main application routes for the RailServe railway
reservation system. It handles:
- Homepage and train search
- PNR enquiry functionality
- Universal train search
- User complaint submission

Author: RailServe Team
Last Modified: 2025
=================================================================================
"""

import os
from src.app import app, db
from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from src.models import Train, Station, Booking, TrainRoute, ComplaintManagement
from src.utils import get_running_trains, search_trains, get_all_class_availability
from datetime import datetime
import random

# =============================================================================
# HOMEPAGE AND SEARCH ROUTES
# =============================================================================

@app.route('/')
def index():
    """
    Homepage Route - Displays running trains and search interface
    
    Returns:
        Rendered HTML template with:
        - List of currently running trains
        - All available stations for search dropdowns
    """
    # Fetch all active trains currently running
    running_trains = get_running_trains()
    
    # Fetch all stations for the search form dropdowns
    stations = Station.query.all()
    
    return render_template('index.html', trains=running_trains, stations=stations)

@app.route('/search_trains', methods=['POST'])
def search_trains_route():
    """
    Train Search Route - Searches for trains between two stations
    
    Form Parameters:
        from_station (int): Source station ID
        to_station (int): Destination station ID
        journey_date (str): Date of journey in YYYY-MM-DD format
    
    Returns:
        Rendered template with search results or redirect to homepage with error
    """
    # Extract search parameters from form submission
    from_station = request.form.get('from_station')
    to_station = request.form.get('to_station')
    journey_date = request.form.get('journey_date')
    
    # Validate all required fields are provided
    if not all([from_station, to_station, journey_date]):
        flash('Please fill all search fields', 'error')
        return redirect(url_for('index'))
    
    # Prevent searching for same source and destination
    if from_station == to_station:
        flash('Source and destination cannot be same', 'error')
        return redirect(url_for('index'))
    
    # Search for trains on the specified route
    trains = search_trains(from_station, to_station, journey_date)
    
    # Get seat availability for all coach classes for each train
    trains_availability = {}
    for train in trains:
        trains_availability[train.id] = get_all_class_availability(
            train.id, from_station, to_station, journey_date
        )
    
    # Get all stations again for the search form
    stations = Station.query.all()
    
    # Render results page with search parameters preserved
    return render_template('index.html', 
                         trains=trains, 
                         stations=stations,
                         trains_availability=trains_availability,
                         search_performed=True,
                         from_station=from_station,
                         to_station=to_station,
                         journey_date=journey_date)

# =============================================================================
# PNR ENQUIRY AND UNIVERSAL SEARCH
# =============================================================================

@app.route('/pnr_enquiry', methods=['GET', 'POST'])
def pnr_enquiry():
    """
    PNR Enquiry System - Check booking status using PNR number
    
    Methods:
        GET: Display PNR enquiry form
        POST: Process PNR and display booking details
    
    Returns:
        Rendered template with booking details if PNR found
    """
    booking = None
    
    if request.method == 'POST':
        # Get PNR from form submission
        pnr = request.form.get('pnr')
        
        if pnr:
            # Search for booking by PNR number
            booking = Booking.query.filter_by(pnr=pnr).first()
            
            if not booking:
                flash('PNR not found', 'error')
    
    return render_template('pnr_enquiry.html', booking=booking)

@app.route('/search', methods=['GET', 'POST'])
def universal_search():
    """
    Universal Train Search - Advanced search by train number, name, or route
    
    Parameters:
        search_query (str): The search term entered by user
        search_type (str): Type of search - 'number', 'name', 'route', or 'all'
    
    Returns:
        Rendered template with matching trains (max 50 results)
    """
    trains = []
    search_query = ""
    search_type = ""
    
    # Support both POST and GET methods for flexibility
    if request.method == 'POST' or request.method == 'GET':
        # Extract search parameters from either POST form or GET query string
        search_query = request.form.get('search_query', '') if request.method == 'POST' else request.args.get('search_query', '')
        search_query = search_query.strip()
        search_type = request.form.get('search_type', 'all') if request.method == 'POST' else request.args.get('search_type', 'all')
        
        if search_query:
            # Start with base query for active trains only
            query = Train.query.filter(Train.active == True)
            
            # Apply search filter based on selected search type
            if search_type == 'number':
                # Search by train number (case-insensitive partial match)
                query = query.filter(db.func.lower(Train.number).contains(search_query.lower()))
                
            elif search_type == 'name':
                # Search by train name (case-insensitive partial match)
                query = query.filter(db.func.lower(Train.name).contains(search_query.lower()))
                
            elif search_type == 'route':
                # Search by station name, city, or code in the train's route
                station_trains = db.session.query(Train.id).join(TrainRoute).join(Station).filter(
                    db.func.lower(Station.name).contains(search_query.lower()) | 
                    db.func.lower(Station.city).contains(search_query.lower()) |
                    db.func.lower(Station.code).contains(search_query.lower())
                ).distinct()
                query = query.filter(Train.id.in_(station_trains))
                
            else:  # 'all' - comprehensive search across all fields
                # Find trains with matching stations
                station_trains = db.session.query(Train.id).join(TrainRoute).join(Station).filter(
                    db.func.lower(Station.name).contains(search_query.lower()) | 
                    db.func.lower(Station.city).contains(search_query.lower()) |
                    db.func.lower(Station.code).contains(search_query.lower())
                ).distinct()
                
                # Search across train number, name, and route stations
                query = query.filter(
                    db.or_(
                        db.func.lower(Train.number).contains(search_query.lower()),
                        db.func.lower(Train.name).contains(search_query.lower()),
                        Train.id.in_(station_trains)
                    )
                )
            
            # Execute query with limit to prevent performance issues
            trains = query.order_by(Train.name).limit(50).all()
            
            # Notify user if no results found
            if not trains:
                flash('No trains found matching your search criteria', 'info')
    
    return render_template('search_results.html', 
                         trains=trains, 
                         search_query=search_query,
                         search_type=search_type)


# =============================================================================
# USER COMPLAINT SYSTEM
# =============================================================================

@app.route('/submit-complaint', methods=['GET', 'POST'])
@login_required
def submit_complaint():
    """
    Complaint Submission System - Allows users to submit service complaints
    
    Methods:
        GET: Display complaint submission form
        POST: Process and save complaint to database
    
    Form Fields:
        category (str): Main complaint category
        subcategory (str): Optional subcategory
        priority (str): Priority level (low/medium/high)
        booking_pnr (str): Optional PNR for booking-related complaints
        subject (str): Brief complaint subject
        description (str): Detailed complaint description
    
    Returns:
        Rendered form or redirect after successful submission
    """
    if request.method == 'POST':
        # Extract complaint details from form
        category = request.form.get('category')
        priority = request.form.get('priority', 'medium')
        booking_pnr = request.form.get('booking_pnr')
        subcategory = request.form.get('subcategory')
        subject = request.form.get('subject')
        description = request.form.get('description')
        
        # Validate required fields
        if not all([category, subject, description]):
            flash('Please fill in all required fields', 'error')
            return render_template('submit_complaint.html')
        
        # Link complaint to booking if PNR provided
        booking = None
        if booking_pnr:
            booking = Booking.query.filter_by(pnr=booking_pnr).first()
            if not booking:
                flash('PNR not found, but complaint will be submitted without booking reference', 'warning')
        
        # Create new complaint record
        complaint = ComplaintManagement(
            user_id=current_user.id,
            booking_id=booking.id if booking else None,
            category=category,
            subcategory=subcategory if subcategory else None,
            priority=priority,
            subject=subject,
            description=description,
            status='open'
        )
        
        # Save complaint to database
        db.session.add(complaint)
        db.session.commit()
        
        # Confirm submission with ticket number
        flash(f'Complaint submitted successfully! Your ticket number is {complaint.ticket_number}', 'success')
        return redirect(url_for('submit_complaint'))
    
    return render_template('submit_complaint.html')

# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    """
    Main application entry point for development server
    
    Note: In production, use gunicorn or another WSGI server instead
    """
    # Get environment configuration
    flask_env = os.environ.get('FLASK_ENV', 'development')
    debug_mode = (flask_env != 'production')
    
    # Start development server on all interfaces, port 5000
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)