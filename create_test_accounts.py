#!/usr/bin/env python
"""Create test accounts for mentor and placement portals."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models.user import User
from app.utils.auth import hash_password, generate_slug

app = create_app()

with app.app_context():
    print('Setting up test accounts...\n')
    
    # Create or update mentor account
    mentor = User.query.filter_by(email='mentor@certrack.local').first()
    if not mentor:
        mentor = User(
            email='mentor@certrack.local',
            password_hash=hash_password('mentor123'),
            display_name='Mentor Administrator',
            is_mentor=True,
            public_slug=generate_slug()
        )
        db.session.add(mentor)
        print('✓ Created mentor account')
    else:
        mentor.is_mentor = True
        mentor.password_hash = hash_password('mentor123')
        print('✓ Updated mentor account')
    
    # Create or update placement account
    placement = User.query.filter_by(email='placement@certrack.local').first()
    if not placement:
        placement = User(
            email='placement@certrack.local',
            password_hash=hash_password('placement123'),
            display_name='Placement Cell Administrator',
            is_placement=True,
            public_slug=generate_slug()
        )
        db.session.add(placement)
        print('✓ Created placement account')
    else:
        placement.is_placement = True
        placement.password_hash = hash_password('placement123')
        print('✓ Updated placement account')
    
    # Update existing admin account with password
    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        admin.password_hash = hash_password('admin123')
        print(f'✓ Updated admin account ({admin.email})')
    else:
        # Create admin account only if none exists
        admin = User(
            email='admin@certrack.local',
            password_hash=hash_password('admin123'),
            display_name='Admin Administrator',
            is_admin=True,
            public_slug=generate_slug()
        )
        db.session.add(admin)
        print('✓ Created admin account')
    
    db.session.commit()
    
    print()
    print('✅ Test accounts setup complete!')
    print()
    print('Login Credentials:')
    print('─' * 50)
    print('Mentor:     mentor@certrack.local / mentor123')
    print('Placement:  placement@certrack.local / placement123')
    print('Admin:      admin@certrack.local / admin123')
    print('            (or existing admin email)')
    print('─' * 50)
