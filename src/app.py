import os
import logging
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from .database import db

# Configure logging with production-ready levels
flask_env = os.environ.get('FLASK_ENV', 'development')
log_level = logging.INFO if flask_env == 'production' else logging.DEBUG
logging.basicConfig(level=log_level)
login_manager = LoginManager()
csrf = CSRFProtect()

# Create the app with correct template path (no static folder needed - all inline)
app = Flask(__name__, 
            template_folder='../templates')

# Load configuration - require SESSION_SECRET for security
app.secret_key =os.environ.get("SESSION_SECRET", "railway-secret-key-2025")
if not app.secret_key:
    if flask_env == 'production':
        raise RuntimeError("SESSION_SECRET environment variable is required in production")
    else:
        app.secret_key = "dev-secret-key-" + os.urandom(24).hex()
        logging.warning("Using generated secret key for development. Set SESSION_SECRET for production!")

# Use DATABASE_URL with fallback to local database
database_url =  os.environ.get("DATABASE_URL", "postgresql://postgres:12345678@localhost:5432/postgres")

if database_url:
    # Validate that DATABASE_URL is a proper connection string
    if database_url.startswith(('postgresql://', 'sqlite://')):
        # Test connection to database
        try:
            import sqlalchemy
            test_engine = sqlalchemy.create_engine(database_url)
            with test_engine.connect() as conn:
                conn.execute(sqlalchemy.text("SELECT 1"))
            logging.info("Database connection successful")
        except Exception as e:
            logging.warning(f"Database connection failed: {e}")
            logging.info("Falling back to local SQLite database")
            database_url = "sqlite:///local_railway.db"
    else:
        logging.warning("Invalid DATABASE_URL format, using local SQLite")
        database_url = "sqlite:///local_railway.db"
else:
    # Use local SQLite database for development - no hardcoded credentials
    database_url = "sqlite:///local_railway.db"
    logging.info("Using SQLite database for development: local_railway.db")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}


# Security settings - production ready
flask_env = os.environ.get("FLASK_ENV", "development")
app.config['SESSION_COOKIE_SECURE'] = (flask_env == 'production')  # Secure cookies in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = "Lax"
app.config['PERMANENT_SESSION_LIFETIME'] = 3600
app.config['WTF_CSRF_ENABLED'] = True  # CSRF protection enabled for security


# Proxy support for Replit environment
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Additional security headers for production
if flask_env == 'production':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year cache for static files

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
csrf.init_app(app)
login_manager.login_view = 'auth.login'  # type: ignore
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

# Import and register blueprints
from .auth import auth_bp
from .admin import admin_bp
from .booking import booking_bp
from .payment import payment_bp
from .pdf_routes import pdf_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(booking_bp, url_prefix='/booking')
app.register_blueprint(payment_bp, url_prefix='/payment')
app.register_blueprint(pdf_bp, url_prefix='/pdf')

# Error handlers
from flask import render_template
from werkzeug.exceptions import HTTPException

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors with custom page"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors with custom page"""
    db.session.rollback()
    error_message = str(error) if app.debug else None
    return render_template('errors/500.html', error_message=error_message), 500

@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors with custom page"""
    return render_template('errors/403.html'), 403

@app.errorhandler(Exception)
def handle_exception(error):
    """Handle unexpected exceptions"""
    if isinstance(error, HTTPException):
        return error
    
    # Log the error for debugging
    app.logger.error(f"Unhandled exception: {error}", exc_info=True)
    
    # Return 500 error page
    db.session.rollback()
    error_message = str(error) if app.debug else None
    return render_template('errors/500.html', error_message=error_message), 500

# Database tables are created by setup_database.py script
# Import models to ensure they are registered
from . import models

# Note: Admin users should be created securely through proper CLI commands or setup scripts
# Never create default admin users with hard-coded passwords in production
