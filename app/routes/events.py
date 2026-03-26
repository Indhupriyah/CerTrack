"""Events routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, date
from app import db
from app.models.event import Event

events_bp = Blueprint("events", __name__)


EVENT_TYPES = ["hackathon", "workshop", "coding_contest", "paper_presentation", "symposium", "technical_competition", "other"]
STAGES = ["upcoming", "registered", "participated", "result_declared", "archived"]
RESULT_STATUSES = ["round_cleared", "finalist", "winner", "participated_only", "not_selected"]


@events_bp.route("/")
@login_required
def list_view():
    events = Event.query.filter_by(user_id=current_user.id).order_by(
        Event.event_date.asc().nullslast()
    ).all()
    
    return render_template("events/list.html", events=events)


@events_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        event_type = request.form.get("event_type", "")
        organizer = request.form.get("organizer", "").strip()
        mode = request.form.get("participation_mode", "online")
        location = request.form.get("location", "").strip() if mode == "offline" else None
        stage = request.form.get("stage", "upcoming")
        result_status = request.form.get("result_status")
        notes = request.form.get("personal_notes", "").strip()
        
        reg = request.form.get("registration_deadline")
        ev_date = request.form.get("event_date")
        res_date = request.form.get("result_date")
        
        event = Event(
            user_id=current_user.id,
            name=name,
            event_type=event_type,
            organizer=organizer,
            participation_mode=mode,
            location=location,
            stage=stage,
            result_status=result_status,
            personal_notes=notes,
            registration_deadline=datetime.strptime(reg, "%Y-%m-%d").date() if reg else None,
            event_date=datetime.strptime(ev_date, "%Y-%m-%d").date() if ev_date else None,
            result_date=datetime.strptime(res_date, "%Y-%m-%d").date() if res_date else None
        )
        db.session.add(event)
        db.session.commit()
        
        flash("Event added successfully.", "success")
        return redirect(url_for("events.list_view"))
    
    return render_template("events/form.html", event=None, event_types=EVENT_TYPES, stages=STAGES, result_statuses=RESULT_STATUSES)


@events_bp.route("/<int:id>")
@login_required
def detail(id):
    event = Event.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template("events/detail.html", event=event)


@events_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    event = Event.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if request.method == "POST":
        event.name = request.form.get("name", event.name).strip()
        event.event_type = request.form.get("event_type", event.event_type)
        event.organizer = request.form.get("organizer", event.organizer).strip()
        mode = request.form.get("participation_mode", event.participation_mode)
        event.participation_mode = mode
        event.location = request.form.get("location", "").strip() if mode == "offline" else None
        event.stage = request.form.get("stage", event.stage)
        event.result_status = request.form.get("result_status")
        event.personal_notes = request.form.get("personal_notes", event.personal_notes).strip()
        
        reg = request.form.get("registration_deadline")
        ev_date = request.form.get("event_date")
        res_date = request.form.get("result_date")
        
        event.registration_deadline = datetime.strptime(reg, "%Y-%m-%d").date() if reg else None
        event.event_date = datetime.strptime(ev_date, "%Y-%m-%d").date() if ev_date else None
        event.result_date = datetime.strptime(res_date, "%Y-%m-%d").date() if res_date else None
        
        # Check if completed/participated
        if event.stage in ["participated", "result_declared"]:
            from app.models.mentor import MentorSuggestion, Message
            sugg = MentorSuggestion.query.filter_by(
                student_id=current_user.id, 
                suggestion_type="event", 
                title=event.name,
                status="accepted"
            ).first()
            if sugg:
                sugg.status = "completed"
                msg = Message(
                    sender_id=current_user.id,
                    receiver_id=sugg.mentor_id,
                    content=f"I have successfully participated in the event you suggested: '{sugg.title}'!"
                )
                db.session.add(msg)
        
        db.session.commit()
        flash("Event updated.", "success")
        return redirect(url_for("events.list_view"))
    
    return render_template("events/form.html", event=event, event_types=EVENT_TYPES, stages=STAGES, result_statuses=RESULT_STATUSES)


@events_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    event = Event.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(event)
    db.session.commit()
    flash("Event removed.", "info")
    return redirect(url_for("events.list_view"))
