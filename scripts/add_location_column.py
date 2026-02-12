#!/usr/bin/env python3
"""Add location column to events table if it doesn't exist."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

app = create_app()
with app.app_context():
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    cols = [c["name"] for c in inspector.get_columns("events")]
    if "location" not in cols:
        db.session.execute(db.text("ALTER TABLE events ADD COLUMN location VARCHAR(500)"))
        db.session.commit()
        print("Added location column to events table.")
    else:
        print("Location column already exists.")
