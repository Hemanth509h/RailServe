# Railway Booking System - Features & Files Documentation

## User Features

### 🎫 **Booking & Reservation**
- **Train Search**: Search trains by number, name, route, or stations
- **Seat Booking**: Book tickets with seat preferences (Lower, Middle, Upper, Window, Aisle)
- **Multiple Classes**: Support for SL, AC3, AC2, AC1, 2S, CC coach classes  
- **Tatkal Booking**: Premium Tatkal quota with time-based availability
- **Group Booking**: Family and corporate group reservations
- **Waitlist Management**: GNWL, RAC, PQWL, RLWL, TQWL queue systems

### 💳 **Payment & Transactions**
- **Multiple Payment Methods**: Card, UPI, Net Banking
- **Secure Payments**: Transaction ID tracking and status management
- **Payment History**: Complete transaction records
- **Refund Management**: TDR (Ticket Deposit Receipt) for cancellations

### 📱 **Tracking & Information**
- **PNR Enquiry**: Real-time booking status checking
- **Booking History**: Complete travel history with detailed passenger info
- **Train Status**: Live train tracking with delay information
- **Seat Details**: Detailed seat allocation with coach information

### 👥 **Group & Social Features**  
- **Group Bookings**: Coordinate family/corporate travel
- **Member Invitations**: Invite others to join group bookings
- **Group Messaging**: Internal communication for travel coordination
- **Split Payments**: Individual payment tracking within groups

### 🏆 **Loyalty & Rewards**
- **Loyalty Program**: Silver, Gold, Platinum, Diamond tiers
- **Points System**: Earn and redeem points for discounts
- **Tier Benefits**: Automatic discounts based on annual spending
- **Membership Numbers**: Unique loyalty program identification

### 🔔 **Notifications & Preferences**
- **Email Alerts**: Booking confirmations and journey reminders
- **SMS Notifications**: Train delay alerts and status updates
- **Push Notifications**: Real-time updates
- **Custom Preferences**: Control notification types

### 👤 **Account Management**
- **User Registration**: Secure account creation
- **Profile Management**: Personal information and preferences
- **Password Reset**: Secure password recovery system
- **Session Management**: Secure login/logout

## Admin Features

### 🚂 **Train Management**
- **Train CRUD**: Create, read, update, delete train information
- **Route Management**: Define train routes with stations and timings
- **Fare Management**: Set base fares and Tatkal premium rates
- **Train Status**: Update live train positions and delays

### 🏢 **Station Management**  
- **Station Database**: Manage 1500+ railway stations across India
- **Station Codes**: Unique 3-4 character station identifiers
- **Geographic Data**: State and city organization
- **Station Status**: Active/inactive station management

### 📊 **Booking Analytics**
- **Booking Reports**: Detailed booking statistics and trends
- **Revenue Analytics**: Financial reporting and insights
- **Passenger Analytics**: Travel pattern analysis
- **Waitlist Management**: Queue position tracking and optimization

### 🎯 **Quota Management**
- **Seat Allocation**: Manage different quota categories
- **Tatkal Settings**: Configure Tatkal time slots and availability
- **Emergency Quota**: Special allocation controls
- **Waitlist Allocation**: Automated confirmation from waitlists

### 👥 **User Management**
- **User Administration**: View and manage all user accounts
- **Role Management**: User, Admin, Super Admin role assignment
- **Account Status**: Activate/deactivate user accounts
- **User Analytics**: User behavior and activity tracking

### ⚙️ **System Administration**
- **Chart Preparation**: Automated seat chart generation
- **Refund Processing**: Handle TDR and refund requests
- **Override Controls**: Emergency booking controls
- **System Monitoring**: Track application performance

## Project Files Structure

### 📁 **Core Application Files**

#### **main.py**
- Main application entry point
- Flask app initialization and route handlers
- Homepage, search, and PNR enquiry endpoints

#### **src/app.py** 
- Flask application factory and configuration
- Database connection and initialization
- Security settings and middleware setup
- Blueprint registration and error handlers

#### **src/models.py**
- Complete database schema definitions (20+ tables)
- User, Station, Train, Booking, Payment models
- Group booking and loyalty program models  
- Relationships and constraints definition

#### **setup_database.py**
- Database initialization script
- Creates all tables and populates test data
- Generates 1500+ stations, 1250+ trains, 1200+ bookings
- Comprehensive seed data for development

### 📁 **Feature Modules (src/)**

#### **auth.py**
- User authentication and authorization
- Registration, login, logout functionality
- Password reset and session management
- Role-based access control

#### **booking.py** 
- Train booking and reservation logic
- Seat allocation and availability checking
- Booking history and status management
- Cancellation and modification handling

#### **payment.py**
- Payment processing integration
- Transaction tracking and status updates
- Payment method management
- Refund and chargeback handling

#### **admin.py**
- Administrative interface and controls
- Train and station management
- User administration and analytics
- System configuration and monitoring

#### **groups.py**
- Group booking functionality
- Member invitation and management
- Group messaging and coordination
- Split payment and cost sharing

#### **pdf_routes.py** & **pdf_generator.py**
- Ticket PDF generation
- QR code creation for tickets
- Booking confirmation documents
- Printable travel receipts

#### **email_service.py**
- Email notification system
- Booking confirmations and reminders
- Password reset emails
- System alerts and communications

#### **utils.py**
- Utility functions and helpers
- Train search algorithms
- Date/time manipulation
- Data validation functions

#### **queue_manager.py**
- Waitlist queue management
- Automatic confirmation processing
- Position tracking and updates
- Queue optimization algorithms

#### **seat_allocation.py**
- Intelligent seat assignment
- Preference-based allocation
- Coach and berth optimization
- Family group seating coordination

#### **route_graph.py**
- Train route optimization
- Station connectivity mapping
- Distance calculations
- Journey planning algorithms

### 📁 **Templates (templates/)**

#### **Base Templates**
- **base.html**: Master template with navigation and common elements
- **index.html**: Homepage with train search functionality
- **login.html** & **register.html**: Authentication pages

#### **Booking Templates**
- **book_ticket.html**: Ticket booking interface
- **booking_history.html**: User booking history display
- **seat_selection.html**: Interactive seat selection
- **tatkal_booking.html**: Tatkal-specific booking interface

#### **Information Templates**
- **pnr_enquiry.html**: PNR status checking
- **search_results.html**: Train search results display
- **profile.html**: User profile management

#### **Payment Templates**  
- **payment.html**: Payment processing interface
- **payment_success.html** & **payment_failure.html**: Transaction status pages

#### **Admin Templates (templates/admin/)**
- **dashboard.html**: Admin control panel
- **trains.html** & **stations.html**: Train and station management
- **booking_reports.html**: Analytics and reporting
- **users.html**: User administration interface
- **analytics.html**: System performance metrics

#### **Group Templates (templates/groups/)**
- **create.html**: Group booking creation
- **manage.html**: Group coordination interface
- **my_groups.html**: User's group booking history

#### **Error Templates (templates/errors/)**
- **404.html**, **403.html**, **500.html**: Error page handling

### 📁 **Static Assets (static/)**

#### **CSS Stylesheets (static/css/)**
- **style.css**: Global application styles
- **index.css**: Homepage-specific styling
- **booking_history.css**: Booking history page styles
- **admin.css**: Administrative interface styling
- **login.css** & **register.css**: Authentication page styles

#### **JavaScript Files (static/js/)**
- **main.js**: Core application JavaScript
- **train_search.js**: Search functionality
- **booking_history.js**: Booking history interactivity
- **admin_dashboard.js**: Admin panel functionality
- **three-hero.js**: 3D homepage animations

### 📁 **Configuration Files**

#### **requirements.txt**
- Python package dependencies
- Flask, SQLAlchemy, Gunicorn, etc.
- Version specifications for reproducible builds

#### **pyproject.toml** 
- Modern Python project configuration
- Dependency management with version constraints
- Build system specifications

#### **replit.md**
- Project documentation and setup instructions
- Feature descriptions and development guidelines
- User preferences and coding standards

### 📁 **Database Files**

#### **local_railway.db**
- SQLite development database
- Contains all application data
- Used for offline development

### 📁 **Additional Files**

#### **uv.lock**
- Lock file for dependency versions
- Ensures consistent package installations
- Automatically generated by uv package manager

## Database Schema Overview

### Core Tables (20+ tables)
1. **users** - User accounts and authentication
2. **stations** - Railway station information  
3. **trains** - Train details and configurations
4. **train_routes** - Station sequences and timings
5. **bookings** - Ticket reservations and status
6. **passengers** - Individual passenger details
7. **payments** - Transaction records
8. **waitlists** - Queue management
9. **group_bookings** - Multi-passenger reservations
10. **loyalty_programs** - Frequent traveler benefits
11. **notification_preferences** - User alert settings
12. **tatkal_time_slots** - Tatkal booking schedules
13. **refund_requests** - TDR and cancellations
14. **train_status** - Live tracking information
15. **seat_availability** - Real-time capacity data
16. **chart_preparation** - Automated seat allocation
17. **group_member_invitations** - Group coordination
18. **group_member_payments** - Split payment tracking
19. **group_messages** - Internal communication
20. **tatkal_override** - Admin emergency controls

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with Font Awesome icons
- **3D Graphics**: Three.js for homepage animations
- **Authentication**: Flask-Login with role-based access
- **Security**: CSRF protection, secure sessions
- **PDF Generation**: ReportLab for ticket generation
- **QR Codes**: Python qrcode library
- **Email**: Integrated email service for notifications
- **Deployment**: Gunicorn WSGI server