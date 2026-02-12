"""API routes for calendar, reminders placeholder."""
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from datetime import date, timedelta
from app.models.certification import Certification
from app.models.event import Event

api_bp = Blueprint("api", __name__)


@api_bp.route("/calendar/events")
@login_required
def calendar_events():
    """Return certifications and events as calendar events."""
    start = date.today() - timedelta(days=60)
    end = date.today() + timedelta(days=365)
    
    items = []
    
    for c in Certification.query.filter_by(user_id=current_user.id).filter(
        Certification.expected_completion.isnot(None)
    ).all():
        d = c.expected_completion or c.registration_deadline
        if d and start <= d <= end:
            color = "green" if c.status == "completed" else "blue" if c.status == "in_progress" else "yellow"
            if c.registration_deadline and c.registration_deadline < date.today() and c.status != "completed":
                color = "red"
            items.append({
                "id": f"cert-{c.id}",
                "title": c.name,
                "start": d.isoformat(),
                "color": color,
                "type": "certification",
                "url": f"/certifications/{c.id}"
            })
    
    for e in Event.query.filter_by(user_id=current_user.id).filter(
        Event.event_date.isnot(None)
    ).all():
        d = e.event_date
        if start <= d <= end:
            items.append({
                "id": f"event-{e.id}",
                "title": e.name,
                "start": d.isoformat(),
                "color": "purple",
                "type": "event",
                "url": f"/events/{e.id}" if hasattr(e, "id") else "#"
            })
    
    return jsonify(items)
