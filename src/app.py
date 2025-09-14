import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create the app with correct template and static paths
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
app.secret_key = os.environ.get("SESSION_SECRET", "railway-secret-key-2025")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://postgres:12345678@localhost:5432/railserve")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
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

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(booking_bp, url_prefix='/booking')
app.register_blueprint(payment_bp, url_prefix='/payment')

with app.app_context():
    # Import models to ensure tables are created
    from . import models
    db.create_all()
    
    # Create default admin user if not exists
    from .models import User
    from werkzeug.security import generate_password_hash
    
    if not User.query.filter_by(role='super_admin').first():
        admin_user = User(
            username='admin',
            email='admin@railserve.com',
            password_hash=generate_password_hash('admin123'),
            role='super_admin',
            active=True
        )
        db.session.add(admin_user)
        db.session.commit()
        logging.info("Default super admin user created")