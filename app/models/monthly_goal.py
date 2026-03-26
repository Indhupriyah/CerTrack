"""Per-month certification goal (customizable per month)."""
from app import db
from datetime import datetime


class MonthlyGoal(db.Model):
    __tablename__ = "monthly_goals"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    target = db.Column(db.Integer, nullable=False, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint("user_id", "year", "month", name="uq_monthly_goal_user_year_month"),)
