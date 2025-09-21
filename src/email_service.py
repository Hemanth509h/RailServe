"""
Email Service Module for RailServe
Handles all email notifications including password reset, booking confirmations, etc.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Email configuration - using environment variables for security
        self.smtp_server = os.environ.get('SMTP_SERVER', 'localhost')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_username = os.environ.get('SMTP_USERNAME', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.from_email = os.environ.get('FROM_EMAIL', 'noreply@railserve.com')
        self.company_name = "RailServe"
        
        # Demo mode for development (when no real SMTP configured)
        self.demo_mode = not all([self.smtp_username, self.smtp_password])
        
    def _create_connection(self):
        """Create SMTP connection"""
        if self.demo_mode:
            return None
            
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            return server
        except Exception as e:
            logger.error(f"Failed to create SMTP connection: {e}")
            return None
    
    def _send_email(self, to_email, subject, html_content, text_content=None):
        """Send email with HTML content"""
        try:
            if self.demo_mode:
                # In demo mode, just log the email content
                logger.info(f"DEMO EMAIL - To: {to_email}, Subject: {subject}")
                logger.info(f"HTML Content: {html_content}")
                return True
                
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
                
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            server = self._create_connection()
            if server:
                server.send_message(msg)
                server.quit()
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error("Failed to establish SMTP connection")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_password_reset(self, user_email, user_name, reset_token, reset_url):
        """Send password reset email"""
        subject = f"Password Reset Request - {self.company_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1e40af; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f8f9fa; }}
                .button {{ 
                    display: inline-block; 
                    background: #dc2626; 
                    color: white; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    margin: 20px 0;
                }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{self.company_name}</h1>
                    <p>Password Reset Request</p>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>We received a request to reset your password for your {self.company_name} account.</p>
                    <p>If you made this request, click the button below to reset your password:</p>
                    <a href="{reset_url}" class="button">Reset Password</a>
                    <p>This link will expire in 24 hours for security reasons.</p>
                    <p>If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>
                    <p><strong>Security Tip:</strong> Never share your password reset link with anyone.</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from {self.company_name}. Please do not reply to this email.</p>
                    <p>&copy; {datetime.now().year} {self.company_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset Request - {self.company_name}
        
        Hello {user_name},
        
        We received a request to reset your password for your {self.company_name} account.
        
        If you made this request, visit this link to reset your password:
        {reset_url}
        
        This link will expire in 24 hours for security reasons.
        
        If you didn't request this password reset, please ignore this email.
        
        {self.company_name} Team
        """
        
        return self._send_email(user_email, subject, html_content, text_content)
    
    def send_booking_confirmation(self, user_email, user_name, booking_details):
        """Send booking confirmation email"""
        subject = f"Booking Confirmed - PNR {booking_details['pnr']} - {self.company_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #10b981; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f8f9fa; }}
                .booking-info {{ background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #10b981; }}
                .info-row {{ display: flex; justify-content: space-between; margin: 8px 0; }}
                .label {{ font-weight: bold; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{self.company_name}</h1>
                    <p>✅ Booking Confirmed</p>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>Great news! Your train booking has been confirmed.</p>
                    
                    <div class="booking-info">
                        <h3>Booking Details</h3>
                        <div class="info-row">
                            <span class="label">PNR Number:</span>
                            <span>{booking_details['pnr']}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Train:</span>
                            <span>{booking_details['train_number']} - {booking_details['train_name']}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Journey Date:</span>
                            <span>{booking_details['journey_date']}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">From:</span>
                            <span>{booking_details['from_station']}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">To:</span>
                            <span>{booking_details['to_station']}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Passengers:</span>
                            <span>{booking_details['passengers']}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Total Amount:</span>
                            <span>₹{booking_details['total_amount']:.2f}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Status:</span>
                            <span style="color: #10b981; font-weight: bold;">{booking_details['status'].title()}</span>
                        </div>
                    </div>
                    
                    <h3>Important Instructions:</h3>
                    <ul>
                        <li>Keep this PNR number safe for future reference</li>
                        <li>Carry a valid photo ID proof during travel</li>
                        <li>Check your booking status 4 hours before departure</li>
                        <li>Download your e-ticket from your account</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>Thank you for choosing {self.company_name}!</p>
                    <p>&copy; {datetime.now().year} {self.company_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(user_email, subject, html_content)
    
    def send_waitlist_confirmation(self, user_email, user_name, booking_details, position):
        """Send waitlist confirmation email"""
        subject = f"Waitlist Confirmed - Position {position} - PNR {booking_details['pnr']}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #f59e0b; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f8f9fa; }}
                .waitlist-info {{ background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #f59e0b; }}
                .position {{ background: #f59e0b; color: white; padding: 10px; text-align: center; border-radius: 5px; margin: 15px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{self.company_name}</h1>
                    <p>🕒 Waitlist Booking</p>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>Your booking has been added to the waitlist. We'll notify you immediately if a seat becomes available.</p>
                    
                    <div class="position">
                        <h3>Your Waitlist Position: {position}</h3>
                    </div>
                    
                    <div class="waitlist-info">
                        <h3>Booking Details</h3>
                        <p><strong>PNR:</strong> {booking_details['pnr']}</p>
                        <p><strong>Train:</strong> {booking_details['train_number']} - {booking_details['train_name']}</p>
                        <p><strong>Journey Date:</strong> {booking_details['journey_date']}</p>
                        <p><strong>Passengers:</strong> {booking_details['passengers']}</p>
                    </div>
                    
                    <h3>What happens next?</h3>
                    <ul>
                        <li>You'll be automatically confirmed if seats become available</li>
                        <li>Confirmation typically happens 24-48 hours before travel</li>
                        <li>We'll send you an instant notification if your status changes</li>
                        <li>No additional payment needed - amount already processed</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>Stay tuned for updates on your booking!</p>
                    <p>&copy; {datetime.now().year} {self.company_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(user_email, subject, html_content)

# Global email service instance
email_service = EmailService()