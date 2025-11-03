"""
Admin and Tatkal Setup
=======================
Creates admin user and Tatkal time slots.
"""

from datetime import time
from werkzeug.security import generate_password_hash
from src.database import db
from src.models import User, TatkalTimeSlot


def create_admin_and_tatkal():
    """Create admin user and Tatkal time slots"""
    print("\n[ADMIN & TATKAL] Creating admin user and Tatkal slots...")
    
    existing_admin = User.query.filter_by(username='admin').first()
    if existing_admin:
        print("✓ Admin user already exists")
        admin = existing_admin
    else:
        admin = User(
            username='admin',
            email='admin@railserve.com',
            password_hash=generate_password_hash('admin123'),
            role='super_admin',
            active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin user created")
    
    if not TatkalTimeSlot.query.first():
        ac_slot = TatkalTimeSlot(
            name='AC Classes Tatkal',
            coach_classes='AC1,AC2,AC3,CC',
            open_time=time(10, 0),
            close_time=time(23, 59),
            days_before_journey=1,
            active=True,
            created_by=admin.id
        )
        
        non_ac_slot = TatkalTimeSlot(
            name='Non-AC Classes Tatkal',
            coach_classes='SL,2S',
            open_time=time(11, 0),
            close_time=time(23, 59),
            days_before_journey=1,
            active=True,
            created_by=admin.id
        )
        
        db.session.add(ac_slot)
        db.session.add(non_ac_slot)
        db.session.commit()
        print("✓ Tatkal slots created")
    else:
        print("✓ Tatkal slots already exist")
