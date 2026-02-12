"""User model."""
from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))
    
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
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    certifications = db.relationship("Certification", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    events = db.relationship("Event", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    analytics = db.relationship("Analytics", backref="user", lazy="dynamic", cascade="all, delete-orphan")
