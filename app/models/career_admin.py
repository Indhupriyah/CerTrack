"""Career roles, certification templates, reports, and admin audit."""
from app import db
from datetime import datetime


class CareerRole(db.Model):
    """Target role with required skills for gap analysis (rule-based, no AI)."""
    __tablename__ = "career_roles"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    required_skills = db.Column(db.Text, nullable=False)  # comma-separated: Python,SQL,Statistics
    recommended_cert_keywords = db.Column(db.Text)  # optional: AWS,Data,Analytics
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CertificationTemplate(db.Model):
    """Admin-defined certification templates for structured user selection."""
    __tablename__ = "certification_templates"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    platform = db.Column(db.String(100))
    category = db.Column(db.String(100))  # e.g. Cloud, Security, Data
    skill_tags = db.Column(db.Text)  # comma-separated
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Report(db.Model):
    """User-reported bugs, incorrect data, or abuse."""
    __tablename__ = "reports"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    report_type = db.Column(db.String(50))  # bug, incorrect_data, abuse, other
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    status = db.Column(db.String(30), default="pending")  # pending, resolved
    admin_notes = db.Column(db.Text)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolved_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AdminActionLog(db.Model):
    """Audit log for admin actions."""
    __tablename__ = "admin_action_logs"
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50))  # user, certification, event, report, file
    target_id = db.Column(db.String(50))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
