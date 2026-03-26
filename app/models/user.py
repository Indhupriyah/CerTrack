"""User model."""
from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(id):
    u = User.query.get(int(id))
    return u if u and not u.deleted_at else None


class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))
    username = db.Column(db.String(80), unique=True, nullable=True, index=True)  # for admin login
    
    # Profile
    display_name = db.Column(db.String(100))
    profile_picture = db.Column(db.String(500))
    linkedin_url = db.Column(db.String(500))
    github_url = db.Column(db.String(500))
    portfolio_public = db.Column(db.Boolean, default=False)
    public_slug = db.Column(db.String(50), unique=True, index=True)
    
    # Streak & goals
    study_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date)
    monthly_goal = db.Column(db.Integer, default=5)
    
    # Admin & moderation
    is_admin = db.Column(db.Boolean, default=False)
    is_suspended = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)  # soft delete
    
    is_mentor = db.Column(db.Boolean, default=False)
    department = db.Column(db.String(100), nullable=True)
    year_of_study = db.Column(db.String(50), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    certifications = db.relationship("Certification", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    events = db.relationship("Event", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    analytics = db.relationship("Analytics", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    monthly_goals = db.relationship("MonthlyGoal", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    # Mentor: students assigned to this user when is_mentor
    mentored_students = db.relationship(
        "MentorAssignment", foreign_keys="MentorAssignment.mentor_id",
        lazy="dynamic", cascade="all, delete-orphan"
    )