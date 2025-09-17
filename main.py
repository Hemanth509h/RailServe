import os
from src.app import app
from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from src.models import Train, Station, Booking
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


if __name__ == '__main__':
    # Development server settingspopulate_db.py
    app.run(host='0.0.0.0', port=5000, debug=True)