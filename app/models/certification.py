"""Certification and Resource models."""
from app import db
from datetime import datetime
import uuid


class Certification(db.Model):
    __tablename__ = "certifications"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    
    name = db.Column(db.String(255), nullable=False)
    platform = db.Column(db.String(100))
    status = db.Column(db.String(50), default="upcoming")  # upcoming, in_progress, completed, missed
    skill_tags = db.Column(db.Text)  # JSON or comma-separated: Cloud,AWS,Python,Security,UI/UX
    
    registration_deadline = db.Column(db.Date)
    expected_completion = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    certificate_file = db.Column(db.String(500))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    resources = db.relationship("Resource", backref="certification", lazy="dynamic", cascade="all, delete-orphan")


class Resource(db.Model):
    __tablename__ = "resources"
    
    id = db.Column(db.Integer, primary_key=True)
    certification_id = db.Column(db.Integer, db.ForeignKey("certifications.id"), nullable=False, index=True)
    
    resource_type = db.Column(db.String(50))  # youtube, documentation, notes, pdf
    title = db.Column(db.String(255))
    url = db.Column(db.String(1000))
    file_path = db.Column(db.String(500))
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
