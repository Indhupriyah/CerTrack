"""Main routes - landing, dashboard."""
from flask import Blueprint, render_template, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func
from app.models.certification import Certification
from app.models.event import Event
from app.models.analytics import Analytics

main_bp = Blueprint("main", __name__)


@main_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    from flask import current_app
    return send_from_directory(current_app.config.get("UPLOAD_FOLDER", "uploads"), filename)


@main_bp.route("/")
def landing():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("landing.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    now = date.today()
    certs = Certification.query.filter_by(user_id=current_user.id)

    # Counts
    total_certs = certs.count()
    upcoming = certs.filter(Certification.status == "upcoming").count()
    in_progress = certs.filter(Certification.status == "in_progress").count()
    completed = certs.filter(Certification.status == "completed").count()
    upcoming_events = Event.query.filter_by(user_id=current_user.id).filter(Event.event_date >= now).count()

    month_start = now.replace(day=1)
    monthly_completed = certs.filter(
        Certification.status == "completed",
        Certification.completed_date >= month_start
    ).count()
    monthly_goal = current_user.monthly_goal or 5
    completion_pct = round((completed / total_certs * 100) if total_certs else 0, 1)

    # Monthly completion trend (last 6 months)
    monthly_trend = []
    for i in range(5, -1, -1):
        m = now.month - i
        y = now.year
        while m <= 0:
            m += 12
            y -= 1
        m_start = date(y, m, 1)
        if m == 12:
            m_end = date(y, 12, 31)
        else:
            m_end = date(y, m + 1, 1) - timedelta(days=1)
        count = certs.filter(
            Certification.status == "completed",
            Certification.completed_date >= m_start,
            Certification.completed_date <= m_end
        ).count()
        monthly_trend.append({"month": m_start.strftime("%b %y"), "count": count})

    # Skill breakdown
    skill_counts = {}
    for c in certs.filter(Certification.status == "completed").all():
        if c.skill_tags:
            for tag in [t.strip() for t in c.skill_tags.split(",") if t.strip()]:
                skill_counts[tag] = skill_counts.get(tag, 0) + 1
    skill_breakdown = sorted(skill_counts.items(), key=lambda x: -x[1])[:6]

    # Upcoming deadlines (next 14 days)
    deadlines = []
    for c in certs.filter(Certification.status.in_(["upcoming", "in_progress"])).all():
        if c.registration_deadline and now <= c.registration_deadline <= now + timedelta(days=14):
            deadlines.append({"name": c.name, "date": c.registration_deadline, "type": "registration"})
        if c.expected_completion and now <= c.expected_completion <= now + timedelta(days=14):
            deadlines.append({"name": c.name, "date": c.expected_completion, "type": "completion"})
    deadlines.sort(key=lambda x: x["date"])
    deadlines = deadlines[:5]

    return render_template(
        "dashboard.html",
        total_certs=total_certs,
        upcoming=upcoming,
        in_progress=in_progress,
        completed=completed,
        upcoming_events=upcoming_events,
        monthly_completed=monthly_completed,
        monthly_goal=monthly_goal,
        completion_pct=completion_pct,
        study_streak=current_user.study_streak or 0,
        monthly_trend=monthly_trend,
        skill_breakdown=skill_breakdown,
        deadlines=deadlines
    )
