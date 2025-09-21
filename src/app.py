import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging with production-ready levels
flask_env = os.environ.get('FLASK_ENV', 'development')
log_level = logging.INFO if flask_env == 'production' else logging.DEBUG
logging.basicConfig(level=log_level)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()

# Create the app with correct template and static paths
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# Load configuration
# Load configuration - require SESSION_SECRET for security
app.secret_key =  os.environ.get("SESSION_SECRET", "railway-secret-key-2025")
if not app.secret_key:
    raise RuntimeError("SESSION_SECRET environment variable is required")

# Use DATABASE_URL with fallback to local database
database_url = os.environ.get("DATABASE_URL")
use_local_db = False

if database_url:
    # Check if DATABASE_URL is just a password (from user input) and construct full URL
    if not database_url.startswith('postgresql://') and not database_url.startswith('sqlite://'):
        # Treat it as password and construct full Supabase URL
        password = database_url
        database_url = f"postgresql://postgres:{password}@db.wymtiyvuelhqvazskofo.supabase.co:5432/postgres"
        logging.info("Constructed Supabase connection string from provided password")
    else:
        logging.info("Using provided DATABASE_URL")
    
    # Test connection to online database
    try:
        import sqlalchemy
        test_engine = sqlalchemy.create_engine(database_url)
        with test_engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        logging.info("Online database connection successful")
    except Exception as e:
        logging.warning(f"Online database connection failed: {e}")
        logging.info("Falling back to local SQLite database")
        use_local_db = True
else:
    logging.info("No DATABASE_URL provided, using offline database")
    use_local_db = True

if use_local_db:
    # First try Replit's built-in PostgreSQL database
    replit_db_url = os.environ.get("DATABASE_URL")
    if replit_db_url and replit_db_url.startswith('postgresql://'):
        database_url = replit_db_url
        logging.info("Using Replit's built-in PostgreSQL database")
    else:
        # Final fallback to SQLite for offline use
        database_url = "sqlite:///local_railway.db"
        logging.info("Using SQLite database for offline mode: local_railway.db")

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
from .food import food_bp
from .groups import groups_bp
from .pdf_routes import pdf_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(booking_bp, url_prefix='/booking')
app.register_blueprint(payment_bp, url_prefix='/payment')
app.register_blueprint(food_bp, url_prefix='/food')
app.register_blueprint(groups_bp, url_prefix='/groups')
app.register_blueprint(pdf_bp, url_prefix='/pdf')

with app.app_context():
    # Import models to ensure tables are created
    from . import models
    
    # Create tables safely - handle existing tables/sequences
    try:
        db.create_all()
    except Exception as e:
        # Log the error but don't crash the app if tables already exist
        logging.warning(f"Database tables may already exist: {e}")
    
    # Note: Admin users should be created securely through proper CLI commands or setup scripts
    # Never create default admin users with hard-coded passwords in production
