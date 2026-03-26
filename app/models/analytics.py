"""Analytics model for streaks and activity tracking."""
from app import db
from datetime import datetime, date


class Analytics(db.Model):
    __tablename__ = "analytics"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    
    activity_date = db.Column(db.Date, nullable=False)
    login_count = db.Column(db.Integer, default=1)
    certifications_completed = db.Column(db.Integer, default=0)
    certifications_added = db.Column(db.Integer, default=0)
    study_minutes = db.Column(db.Integer, default=0)  # for effort vs outcome
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
