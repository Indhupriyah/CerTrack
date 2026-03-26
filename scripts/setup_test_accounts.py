"""Setup script to create test mentor and placement accounts."""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from app import create_app, db
from app.models.user import User
from app.utils.auth import hash_password

app = create_app()

with app.app_context():
    # Check and create mentor account
    mentor_email = "mentor@certrack.local"
    existing_mentor = User.query.filter_by(email=mentor_email).first()
    
    if not existing_mentor:
        mentor = User(
            email=mentor_email,
            password_hash=hash_password("mentor123"),
            username="mentor",
            display_name="Mentor Administrator",
            is_mentor=True
        )
        db.session.add(mentor)
        print(f"✓ Created mentor account: {mentor_email}")
    else:
        existing_mentor.is_mentor = True
        existing_mentor.password_hash = hash_password("mentor123")
        print(f"✓ Updated mentor account: {mentor_email}")
    
    # Check and create placement account
    placement_email = "placement@certrack.local"
    existing_placement = User.query.filter_by(email=placement_email).first()
    
    if not existing_placement:
        placement = User(
            email=placement_email,
            password_hash=hash_password("placement123"),
            username="placement",
            display_name="Placement Cell Administrator",
            is_placement=True
        )
        db.session.add(placement)
        print(f"✓ Created placement account: {placement_email}")
    else:
        existing_placement.is_placement = True
        existing_placement.password_hash = hash_password("placement123")
        print(f"✓ Updated placement account: {placement_email}")
    
    # Update admin password if needed
    admin_email = "admin@certrack.local"
    admin = User.query.filter_by(email=admin_email).first()
    
    if admin:
        admin.is_admin = True
        admin.password_hash = hash_password("admin123")
        print(f"✓ Updated admin account: {admin_email}")
    else:
        admin = User(
            email=admin_email,
            password_hash=hash_password("admin123"),
            username="admin",
            display_name="Admin Administrator",
            is_admin=True
        )
        db.session.add(admin)
        print(f"✓ Created admin account: {admin_email}")
    
    db.session.commit()
    print("\n✓ Test accounts setup complete!")
    print("\nTest Credentials:")
    print("─" * 50)
    print("Mentor Login:     mentor@certrack.local / mentor123")
    print("Placement Login:  placement@certrack.local / placement123")
    print("Admin Login:      admin@certrack.local / admin123")
    print("─" * 50)
