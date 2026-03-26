#!/usr/bin/env python
"""Quick setup for mentor and placement flags."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    mentor = User.query.filter_by(email='mentor@certrack.local').first()
    if mentor:
        mentor.is_mentor = True
        print('✓ Mentor user updated')
    
    placement = User.query.filter_by(email='placement@certrack.local').first()
    if placement:
        placement.is_placement = True
        print('✓ Placement user updated')
    
    db.session.commit()
    print('\n✓ Setup complete!')
