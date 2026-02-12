"""Reminder log - tracks sent notifications to avoid duplicates."""
from app import db
from datetime import datetime


class ReminderLog(db.Model):
    __tablename__ = "reminder_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    certification_id = db.Column(db.Integer, db.ForeignKey("certifications.id"), nullable=True)
    event_id = db.Column(db.Integer, nullable=True)

    reminder_type = db.Column(db.String(50), nullable=False)  # reg_1d, completion_5d, completion_1d, etc.
    target_date = db.Column(db.Date, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
