from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
import qrcode
from datetime import datetime
import os

class TicketPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles for the ticket"""
        self.styles.add(ParagraphStyle(
            name='TicketHeader',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='TicketSubHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='TicketInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            alignment=TA_LEFT,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            name='ImportantInfo',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.darkred,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))

    def generate_ticket_pdf(self, booking, passengers):
        """Generate PDF ticket for a booking"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        # Build the document
        story = []
        
        # Header
        story.append(Paragraph("INDIAN RAILWAYS - E-TICKET", self.styles['TicketHeader']))
        story.append(Paragraph("RailServe Booking System", self.styles['TicketSubHeader']))
        story.append(Spacer(1, 12))
        
        # Booking Information Table
        booking_data = [
            ['PNR Number:', booking.pnr, 'Booking Date:', booking.booking_date.strftime('%d-%m-%Y')],
            ['Train Number:', f"{booking.train.number} - {booking.train.name}", 'Journey Date:', booking.journey_date.strftime('%d-%m-%Y')],
            ['From Station:', booking.from_station.name, 'To Station:', booking.to_station.name],
            ['Coach Class:', booking.coach_class, 'Quota:', booking.quota.title()],
            ['Booking Type:', booking.booking_type.title(), 'Status:', booking.status.title()],
            ['Total Passengers:', str(booking.passengers), 'Total Amount:', f"₹{booking.total_amount:.2f}"]
        ]
        
        booking_table = Table(booking_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        booking_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        story.append(booking_table)
        story.append(Spacer(1, 20))
        
        # Passenger Details
        story.append(Paragraph("PASSENGER DETAILS", self.styles['TicketSubHeader']))
        
        passenger_headers = ['S.No.', 'Name', 'Age', 'Gender', 'Seat Number', 'Berth Type']
        passenger_data = [passenger_headers]
        
        for i, passenger in enumerate(passengers):
            # Show actual allocated seat or status
            seat_info = passenger.seat_number if passenger.seat_number else "To be allocated"
            berth_info = passenger.berth_type if passenger.berth_type else "Pending"
            
            passenger_data.append([
                str(i + 1),
                passenger.name,
                str(passenger.age),
                passenger.gender,
                seat_info,
                berth_info
            ])
        
        passenger_table = Table(passenger_data, colWidths=[0.5*inch, 2*inch, 0.7*inch, 0.8*inch, 1.2*inch, 1*inch])
        passenger_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        story.append(passenger_table)
        story.append(Spacer(1, 20))
        
        # Generate QR Code for PNR
        try:
            import qrcode as qr_module
            qr = qr_module.QRCode(version=1, box_size=10, border=5)
            qr.add_data(f"PNR: {booking.pnr}")
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Save QR code temporarily
            qr_path = f"/tmp/qr_{booking.pnr}.png"
            qr_img.save(qr_path)
            
            # Add QR code to PDF
            qr_image = Image(qr_path, width=1.5*inch, height=1.5*inch)
            story.append(Paragraph("QR Code for Mobile Verification:", self.styles['TicketInfo']))
            story.append(qr_image)
            story.append(Spacer(1, 20))
            
            # Clean up flag
            qr_generated = True
        except Exception as e:
            # If QR code generation fails, continue without it
            story.append(Paragraph("QR Code generation failed - ticket is still valid", self.styles['TicketInfo']))
            qr_generated = False
            qr_path = None
        
        # Important Instructions
        instructions = [
            "IMPORTANT INSTRUCTIONS:",
            "1. Please carry a valid photo ID proof during journey",
            "2. Passengers should report at station 30 minutes before departure",
            "3. E-ticket must be carried in printed form or shown on mobile",
            "4. Chart preparation happens 4 hours before departure",
            "5. No refund for confirmed Tatkal tickets",
            "6. For any queries, call Railway Enquiry: 139"
        ]
        
        for instruction in instructions:
            if instruction.startswith("IMPORTANT"):
                story.append(Paragraph(instruction, self.styles['ImportantInfo']))
            else:
                story.append(Paragraph(instruction, self.styles['TicketInfo']))
        
        story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", 
                             self.styles['TicketInfo']))
        story.append(Paragraph("This is a computer generated ticket", self.styles['TicketInfo']))
        
        # Build PDF
        doc.build(story)
        
        # Clean up QR code file
        if qr_generated and qr_path and os.path.exists(qr_path):
            os.remove(qr_path)
        
        buffer.seek(0)
        return buffer

    def generate_booking_summary_pdf(self, bookings):
        """Generate PDF summary of multiple bookings"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        story = []
        
        # Header
        story.append(Paragraph("BOOKING SUMMARY REPORT", self.styles['TicketHeader']))
        story.append(Spacer(1, 20))
        
        # Summary table
        summary_data = [['PNR', 'Train', 'Journey Date', 'Status', 'Amount']]
        
        total_amount = 0
        for booking in bookings:
            summary_data.append([
                booking.pnr,
                f"{booking.train.number}",
                booking.journey_date.strftime('%d-%m-%Y'),
                booking.status.title(),
                f"₹{booking.total_amount:.2f}"
            ])
            if booking.status == 'confirmed':
                total_amount += booking.total_amount
        
        # Add total row
        summary_data.append(['', '', '', 'Total:', f"₹{total_amount:.2f}"])
        
        summary_table = Table(summary_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (-2, -1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph(f"Report generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", 
                             self.styles['TicketInfo']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer