"""Helpers for Mentor and Placement portals: student metrics, readiness, aggregates."""
from datetime import date, timedelta
from collections import defaultdict

from app import db
from app.models.user import User
from app.models.certification import Certification
from app.models.event import Event
from app.models.analytics import Analytics
from app.models.career_admin import CareerRole, CertificationTemplate
from app.services.career_engine import (
    get_user_acquired_skills,
    career_gap_analysis,
    deadline_risk_predictor,
    failure_pattern_analyzer,
    productivity_score,
    certification_path_mapping,
    career_readiness_score,
)


def get_student_metrics_for_mentor(student_id):
    """Full metrics for one student (mentor view): certs, events, productivity, gap, risks, inactive."""
    user = User.query.get(student_id)
    if not user or user.deleted_at:
        return None
    today = date.today()
    certs = Certification.query.filter_by(user_id=student_id).all()
    certs_list = list(certs)
    completed_certs = [c for c in certs_list if c.status == "completed"]
    active_certs = [c for c in certs_list if c.status in ("upcoming", "in_progress")]
    events_list = Event.query.filter_by(user_id=student_id).all()
    analytics_rows = Analytics.query.filter_by(user_id=student_id).all()
    acquired_skills = get_user_acquired_skills(completed_certs, events_list)
    certs_missed = len([c for c in certs_list if c.status == "missed"])
    events_participated = len([e for e in events_list if e.stage and e.stage != "upcoming"])
    deadlines_met = len([c for c in completed_certs if c.completed_date and c.expected_completion and c.completed_date <= c.expected_completion])
    deadlines_missed = len([c for c in completed_certs if c.completed_date and c.expected_completion and c.completed_date > c.expected_completion])
    prod = productivity_score(
        len(completed_certs), certs_missed, events_participated, deadlines_met, deadlines_missed
    )
    risk_data = deadline_risk_predictor(active_certs, completed_certs, today)
    failure_pattern = failure_pattern_analyzer(events_list)
    default_role = CareerRole.query.filter_by(is_active=True).first()
    gap = career_gap_analysis(default_role, acquired_skills) if default_role else None
    templates_by_cat = {}
    for t in CertificationTemplate.query.filter_by(is_active=True).all():
        cat = t.category or "General"
        templates_by_cat.setdefault(cat, []).append(t)
    path_mapping = certification_path_mapping(completed_certs, templates_by_cat)
    last_activity = user.last_activity_date
    days_inactive = (today - last_activity).days if last_activity else 999
    inactive = days_inactive >= 14
    at_risk = any(r.get("risk") in ("high", "overdue") for r in (risk_data.get("items") or []))
    readiness = career_readiness_score(
        certs_completed=len(completed_certs),
        certs_total=len(certs_list),
        events_participated=events_participated,
        skill_count=len(acquired_skills),
        last_activity_days_ago=days_inactive if days_inactive != 999 else None,
        productivity_score_value=prod,
        deadlines_met=deadlines_met,
        deadlines_missed=deadlines_missed,
    )
    return {
        "user": user,
        "certs_total": len(certs_list),
        "certs_completed": len(completed_certs),
        "certs_active": len(active_certs),
        "events_total": len(events_list),
        "events_participated": events_participated,
        "productivity_score": prod,
        "career_readiness_score": readiness,
        "deadline_risk": risk_data,
        "failure_pattern": failure_pattern,
        "gap": gap,
        "default_role": default_role,
        "path_mapping": path_mapping,
        "inactive": inactive,
        "days_inactive": days_inactive,
        "at_risk": at_risk,
        "acquired_skills": acquired_skills,
        "completed_certs": completed_certs,
        "events_list": events_list,
    }
