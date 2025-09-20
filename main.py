import os
from src.app import app, db
from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from src.models import Train, Station, Booking, TrainRoute
from src.utils import get_running_trains, search_trains
from datetime import datetime

@app.route('/')
def index():
    """Homepage showing running trains and search functionality"""
    running_trains = get_running_trains()
    stations = Station.query.all()
    return render_template('index.html', trains=running_trains, stations=stations)

@app.route('/search_trains', methods=['POST'])
def search_trains_route():
    """Search trains between stations"""
    from_station = request.form.get('from_station')
    to_station = request.form.get('to_station')
    journey_date = request.form.get('journey_date')
    
    if not all([from_station, to_station, journey_date]):
        flash('Please fill all search fields', 'error')
        return redirect(url_for('index'))
    
    if from_station == to_station:
        flash('Source and destination cannot be same', 'error')
        return redirect(url_for('index'))
    
    trains = search_trains(from_station, to_station, journey_date)
    stations = Station.query.all()
    
    return render_template('index.html', 
                         trains=trains, 
                         stations=stations,
                         search_performed=True,
                         from_station=from_station,
                         to_station=to_station,
                         journey_date=journey_date)

@app.route('/pnr_enquiry', methods=['GET', 'POST'])
def pnr_enquiry():
    """PNR enquiry system"""
    booking = None
    if request.method == 'POST':
        pnr = request.form.get('pnr')
        if pnr:
            booking = Booking.query.filter_by(pnr=pnr).first()
            if not booking:
                flash('PNR not found', 'error')
    
    return render_template('pnr_enquiry.html', booking=booking)

@app.route('/search', methods=['GET', 'POST'])
def universal_search():
    """Universal search for trains by name, number, ID, or route"""
    trains = []
    search_query = ""
    search_type = ""
    
    if request.method == 'POST':
        search_query = request.form.get('search_query', '').strip()
        search_type = request.form.get('search_type', 'all')
        
        if search_query:
            query = Train.query.filter(Train.active == True)
            
            if search_type == 'number':
                query = query.filter(Train.number.ilike(f'%{search_query}%'))
            elif search_type == 'name':
                query = query.filter(Train.name.ilike(f'%{search_query}%'))
            elif search_type == 'route':
                # Search by stations in route
                station_trains = db.session.query(Train.id).join(TrainRoute).join(Station).filter(
                    Station.name.ilike(f'%{search_query}%') | 
                    Station.city.ilike(f'%{search_query}%') |
                    Station.code.ilike(f'%{search_query}%')
                ).distinct()
                query = query.filter(Train.id.in_(station_trains))
            else:  # 'all' - search everything
                station_trains = db.session.query(Train.id).join(TrainRoute).join(Station).filter(
                    Station.name.ilike(f'%{search_query}%') | 
                    Station.city.ilike(f'%{search_query}%') |
                    Station.code.ilike(f'%{search_query}%')
                ).distinct()
                
                query = query.filter(
                    db.or_(
                        Train.number.ilike(f'%{search_query}%'),
                        Train.name.ilike(f'%{search_query}%'),
                        Train.id.in_(station_trains)
                    )
                )
            
            trains = query.order_by(Train.name).limit(50).all()
            
            if not trains:
                flash('No trains found matching your search criteria', 'info')
    
    return render_template('search_results.html', 
                         trains=trains, 
                         search_query=search_query,
                         search_type=search_type)


if __name__ == '__main__':
    # Development server settings
    flask_env = os.environ.get('FLASK_ENV', 'development')
    debug_mode = (flask_env != 'production')
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)