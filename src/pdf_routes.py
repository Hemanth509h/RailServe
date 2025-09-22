from flask import Blueprint, send_file, flash, redirect, url_for, request
from flask_login import login_required, current_user
from .models import Booking, Passenger
from .pdf_generator import TicketPDFGenerator
from datetime import datetime
import io

pdf_bp = Blueprint('pdf', __name__)

@pdf_bp.route('/download-ticket/<int:booking_id>')
@login_required
def download_ticket(booking_id):
    """Download PDF ticket for a specific booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user owns the booking
    if booking.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('auth.profile'))
    
    # Check if booking is confirmed
    if booking.status not in ['confirmed', 'rac']:
        flash('Ticket can only be downloaded for confirmed or RAC bookings', 'error')
        return redirect(url_for('auth.profile'))
    
    try:
        # Get passenger details
        passengers = Passenger.query.filter_by(booking_id=booking_id).all()
        
        if not passengers:
            flash('No passenger details found for this booking', 'error')
            return redirect(url_for('auth.profile'))
        
        # Generate PDF
        generator = TicketPDFGenerator()
        pdf_buffer = generator.generate_ticket_pdf(booking, passengers)
        
        # Create filename
        filename = f"RailServe_Ticket_{booking.pnr}_{booking.journey_date.strftime('%d%m%Y')}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'error')
        return redirect(url_for('auth.profile'))

@pdf_bp.route('/download-booking-summary')
@login_required
def download_booking_summary():
    """Download PDF summary of user's bookings"""
    try:
        # Get user's confirmed bookings from last 6 months
        from datetime import date, timedelta
        start_date = date.today() - timedelta(days=180)
        
        bookings = Booking.query.filter(
            Booking.user_id == current_user.id,
            Booking.booking_date >= start_date,
            Booking.status.in_(['confirmed', 'cancelled', 'waitlisted'])
        ).order_by(Booking.booking_date.desc()).all()
        
        if not bookings:
            flash('No bookings found to generate summary', 'info')
            return redirect(url_for('auth.profile'))
        
        # Generate PDF
        generator = TicketPDFGenerator()
        pdf_buffer = generator.generate_booking_summary_pdf(bookings)
        
        # Create filename
        filename = f"RailServe_BookingSummary_{current_user.username}_{date.today().strftime('%d%m%Y')}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f'Error generating booking summary: {str(e)}', 'error')
        return redirect(url_for('auth.profile'))

# Bulk download functionality removed as requested