"""Mentor–student assignment for Faculty portal."""
from app import db
from datetime import datetime


class MentorAssignment(db.Model):
    __tablename__ = "mentor_assignments"
    
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    status = db.Column(db.String(20), default="pending")  # pending, accepted, rejected
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # We do not use a unique constraint here, as a student can request multiple times if rejected.
    # Alternatively, keep unique constraint if we just update the status.
    __table_args__ = (db.UniqueConstraint("mentor_id", "student_id", name="uq_mentor_student"),)
    
    mentor = db.relationship("User", foreign_keys=[mentor_id], overlaps="mentored_students")
    student = db.relationship("User", foreign_keys=[student_id])

class Message(db.Model):
    __tablename__ = "messages"
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=True)
    file_name = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    sender = db.relationship("User", foreign_keys=[sender_id])
    receiver = db.relationship("User", foreign_keys=[receiver_id])

class MentorSuggestion(db.Model):
    __tablename__ = "mentor_suggestions"
    
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    suggestion_type = db.Column(db.String(20), nullable=False) # 'certificate', 'event'
    status = db.Column(db.String(20), default="pending")  # pending, accepted, rejected, completed
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    link = db.Column(db.String(500))
    location = db.Column(db.String(255)) # For events: Online/Offline details
    team_size = db.Column(db.String(50)) # For events
    duration = db.Column(db.String(100)) # For certs
    skills = db.Column(db.String(255)) # For certs
    file_path = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    rejection_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    mentor = db.relationship("User", foreign_keys=[mentor_id])
    student = db.relationship("User", foreign_keys=[student_id])
