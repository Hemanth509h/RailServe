import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging based on environment
log_level = logging.INFO if os.environ.get('FLASK_ENV') == 'production' else logging.DEBUG
logging.basicConfig(
    level=log_level,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()

# Create the app with correct template and static paths
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
# Security: Require SESSION_SECRET environment variable - no fallback
session_secret = os.environ.get("SESSION_SECRET")
if not session_secret:
    raise ValueError("SESSION_SECRET environment variable is required for security")
app.secret_key = session_secret
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Production security configuration
if os.environ.get('FLASK_ENV') == 'production':
    app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://postgres:12345678@localhost:5432/railserve")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
csrf.init_app(app)
login_manager.login_view = 'auth.login'  # type: ignore
login_manager.login_message = 'Please log in to access this page.'

# Security headers for all responses
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    if os.environ.get('FLASK_ENV') == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

# Import and register blueprints
from .auth import auth_bp
from .admin import admin_bp
from .booking import booking_bp
from .payment import payment_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(booking_bp, url_prefix='/booking')
app.register_blueprint(payment_bp, url_prefix='/payment')

with app.app_context():
    # Import models to ensure tables are created
    from . import models
    db.create_all()
    
    # Create default admin user if not exists and ADMIN_PASSWORD is set
    from .models import User
    from werkzeug.security import generate_password_hash
    
    admin_password = os.environ.get('ADMIN_PASSWORD')
    if admin_password and not User.query.filter_by(role='super_admin').first():
        admin_user = User(
            username='admin',
            email='admin@railserve.com',
            password_hash=generate_password_hash(admin_password),
            role='super_admin',
            active=True
        )
        db.session.add(admin_user)
        db.session.commit()
        logging.info("Default super admin user created")
    elif not admin_password and not User.query.filter_by(role='super_admin').first():
        logging.warning("No super admin user exists and ADMIN_PASSWORD not set. Create one manually through registration.")
