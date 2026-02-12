"""Event model."""
from app import db
from datetime import datetime


class Event(db.Model):
    __tablename__ = "events"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    
    name = db.Column(db.String(255), nullable=False)
    event_type = db.Column(db.String(100))  # hackathon, workshop, coding_contest, paper_presentation, etc.
    organizer = db.Column(db.String(255))
    participation_mode = db.Column(db.String(50))  # online, offline
    location = db.Column(db.String(500))  # venue/address for offline events
    
    registration_deadline = db.Column(db.Date)
    event_date = db.Column(db.Date)
    result_date = db.Column(db.Date)
    
    stage = db.Column(db.String(50), default="upcoming")  # upcoming, registered, participated, result_declared, archived
    result_status = db.Column(db.String(50))  # round_cleared, finalist, winner, participated_only, not_selected
    team_members = db.Column(db.Text)  # JSON or comma-separated
    attempt_history = db.Column(db.Text)  # JSON
    personal_notes = db.Column(db.Text)  # problem statements, approaches, mistakes, feedback
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
