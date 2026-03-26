"""Main routes - landing, dashboard, insights."""
from flask import Blueprint, render_template, redirect, url_for, send_from_directory, request, flash
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func
from app import db
from app.models.certification import Certification
from app.models.event import Event
from app.models.analytics import Analytics
from app.models.career_admin import CareerRole, CertificationTemplate, Report
from app.models.monthly_goal import MonthlyGoal
from app.services.career_engine import (
    get_user_acquired_skills,
    career_gap_analysis,
    deadline_risk_predictor,
    failure_pattern_analyzer,
    effort_vs_outcome_analysis,
    productivity_score,
    certification_path_mapping,
)

main_bp = Blueprint("main", __name__)


def _goal_for_month(user, year, month):
    """Certification goal for a given month: per-month override or user default."""
    row = MonthlyGoal.query.filter_by(user_id=user.id, year=year, month=month).first()
    return row.target if row else (user.monthly_goal or 5)


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
    monthly_goal = _goal_for_month(current_user, now.year, now.month)
    completion_pct = round((completed / total_certs * 100) if total_certs else 0, 1)

    # Monthly completion trend (last 6 months) — each month uses its own goal
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
        goal = _goal_for_month(current_user, y, m)
        monthly_trend.append({"month": m_start.strftime("%b %y"), "count": count, "goal": goal})

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

    # ---- Career Strategy Engine (rule-based, no OpenAI) ----
    certs_list = certs.all()
    completed_certs = [c for c in certs_list if c.status == "completed"]
    active_certs = [c for c in certs_list if c.status in ("upcoming", "in_progress")]
    events_list = Event.query.filter_by(user_id=current_user.id).all()
    analytics_rows = Analytics.query.filter_by(user_id=current_user.id).all()

    acquired_skills = get_user_acquired_skills(completed_certs, events_list)
    certs_missed = certs.filter(Certification.status == "missed").count()
    events_participated = len([e for e in events_list if e.stage and e.stage != "upcoming"])
    deadlines_met = len([c for c in completed_certs if c.completed_date and c.expected_completion and c.completed_date <= c.expected_completion])
    deadlines_missed = len([c for c in completed_certs if c.completed_date and c.expected_completion and c.completed_date > c.expected_completion])

    prod_score = productivity_score(
        len(completed_certs), certs_missed, events_participated, deadlines_met, deadlines_missed
    )
    risk_data = deadline_risk_predictor(active_certs, completed_certs, now)
    failure_pattern = failure_pattern_analyzer(events_list)
    effort_outcome = effort_vs_outcome_analysis(
        analytics_rows,
        len(completed_certs),
        failure_pattern.get("by_status", {}).get("winner", 0),
    )
    templates_by_cat = {}
    for t in CertificationTemplate.query.filter_by(is_active=True).all():
        cat = t.category or "General"
        templates_by_cat.setdefault(cat, []).append(t)
    path_mapping = certification_path_mapping(completed_certs, templates_by_cat)

    # Opportunity reminder: inactive > 7 days
    last_activity = current_user.last_activity_date
    show_inactive_reminder = last_activity and (now - last_activity).days >= 7

    # Default career role for preview
    default_role = CareerRole.query.filter_by(is_active=True).first()
    gap_preview = career_gap_analysis(default_role, acquired_skills) if default_role else None

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
        deadlines=deadlines,
        productivity_score=prod_score,
        deadline_risk=risk_data,
        failure_pattern=failure_pattern,
        effort_outcome=effort_outcome,
        path_mapping=path_mapping,
        show_inactive_reminder=show_inactive_reminder,
        gap_preview=gap_preview,
        default_role=default_role,
    )


@main_bp.route("/insights")
@login_required
def insights():
    """Career Gap Analyzer & Certification Path Mapping with role selection."""
    role_id = request.args.get("role_id", type=int)
    roles = CareerRole.query.filter_by(is_active=True).order_by(CareerRole.name).all()
    selected_role = CareerRole.query.get(role_id) if role_id else (roles[0] if roles else None)

    certs_list = Certification.query.filter_by(user_id=current_user.id).all()
    completed_certs = [c for c in certs_list if c.status == "completed"]
    events_list = Event.query.filter_by(user_id=current_user.id).all()
    acquired_skills = get_user_acquired_skills(completed_certs, events_list)

    gap = career_gap_analysis(selected_role, acquired_skills) if selected_role else None
    templates_by_cat = {}
    for t in CertificationTemplate.query.filter_by(is_active=True).all():
        cat = t.category or "General"
        templates_by_cat.setdefault(cat, []).append(t)
    path_mapping = certification_path_mapping(completed_certs, templates_by_cat)

    # Recommended certs from templates matching gap keywords
    recommended = []
    if gap and selected_role and path_mapping.get("suggested_next"):
        recommended = path_mapping["suggested_next"]
    elif gap and selected_role and gap.get("recommended_keywords"):
        for t in CertificationTemplate.query.filter_by(is_active=True).all():
            name_lower = (t.name or "").lower()
            if any(kw.lower() in name_lower for kw in gap["recommended_keywords"]):
                recommended.append({"category": t.category or "General", "name": t.name, "platform": t.platform or ""})
                if len(recommended) >= 8:
                    break

    return render_template(
        "insights.html",
        roles=roles,
        selected_role=selected_role,
        gap=gap,
        path_mapping=path_mapping,
        recommended=recommended[:10],
    )


@main_bp.route("/report", methods=["GET", "POST"])
@login_required
def report_issue():
    """User-reported bugs, incorrect data, or abuse."""
    if request.method == "POST":
        report_type = request.form.get("report_type", "other").strip()
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        if not title:
            flash("Title is required.", "error")
            return render_template("report_issue.html")
        r = Report(
            user_id=current_user.id,
            report_type=report_type,
            title=title,
            description=description,
            status="pending",
        )
        db.session.add(r)
        db.session.commit()
        flash("Report submitted. We will review it shortly.", "success")
        return redirect(url_for("main.report_issue"))
        
    user_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).all()
    return render_template("report_issue.html", user_reports=user_reports)

@main_bp.route("/achievements")
@login_required
def achievements():
    """Display completed accomplishments."""
    query = request.args.get("q", "").lower()
    
    # Certifications
    completed_certs = Certification.query.filter_by(user_id=current_user.id, status="completed").all()
    if query:
        completed_certs = [c for c in completed_certs if query in c.name.lower() or (c.platform and query in c.platform.lower())]
        
    # Events
    events = Event.query.filter_by(user_id=current_user.id).filter(Event.stage.in_(["participated", "result_declared"])).all()
    if query:
        events = [e for e in events if query in e.name.lower() or (e.event_type and query in e.event_type.lower())]
        
    return render_template("achievements.html", certs=completed_certs, events=events, query=query)

@main_bp.route("/mentors")
@login_required
def mentors():
    """List of all mentors logic for students."""
    from app.models.user import User
    from app.models.mentor import MentorAssignment
    from datetime import datetime
    
    mentors_list = User.query.filter_by(is_mentor=True).all()
    # Find active assignment if any
    my_assignment = MentorAssignment.query.filter_by(student_id=current_user.id).order_by(MentorAssignment.created_at.desc()).first()
    
    if my_assignment and my_assignment.status == "accepted":
        mentors_list = [m for m in mentors_list if m.id == my_assignment.mentor_id]
        from app.models.mentor import MentorSuggestion
        suggestions = MentorSuggestion.query.filter_by(student_id=current_user.id, status="pending").all()
        suggested_events = [s for s in suggestions if s.suggestion_type == "event"]
        suggested_certs = [s for s in suggestions if s.suggestion_type == "certificate"]
    else:
        suggested_events = []
        suggested_certs = []
    
    can_cancel = False
    if my_assignment and my_assignment.status == "pending":
        if (datetime.utcnow() - my_assignment.created_at).total_seconds() <= 300:
            can_cancel = True
            
    return render_template("mentors.html", mentors=mentors_list, my_assignment=my_assignment, can_cancel=can_cancel, suggested_events=suggested_events, suggested_certs=suggested_certs)

@main_bp.route("/suggestions/accept/<int:sugg_id>", methods=["POST"])
@login_required
def accept_suggestion(sugg_id):
    from app.models.mentor import MentorSuggestion
    sugg = MentorSuggestion.query.get_or_404(sugg_id)
    if sugg.student_id != current_user.id:
        flash("Unauthorized", "error")
        return redirect(url_for("main.mentors"))
    
    sugg.status = "accepted"
    
    # Move suggestion to active tasks list
    if sugg.suggestion_type == "certificate":
        from app.models.certification import Certification
        new_cert = Certification(
            user_id=current_user.id,
            name=sugg.title,
            status="upcoming",
            skill_tags=sugg.skills
        )
        db.session.add(new_cert)
        if sugg.link:
            db.session.flush()
            from app.models.certification import Resource
            res = Resource(
                certification_id=new_cert.id,
                resource_type="url",
                title="Suggested Link",
                url=sugg.link
            )
            db.session.add(res)
    elif sugg.suggestion_type == "event":
        from app.models.event import Event
        new_event = Event(
            user_id=current_user.id,
            name=sugg.title,
            stage="upcoming",
            role=sugg.team_size,
            certificate_link=sugg.link
        )
        db.session.add(new_event)
        
    db.session.commit()
    flash("Suggestion accepted and moving to active tasks.", "success")
    return redirect(url_for("main.mentors"))

@main_bp.route("/suggestions/reject/<int:sugg_id>", methods=["POST"])
@login_required
def reject_suggestion(sugg_id):
    from app.models.mentor import MentorSuggestion
    sugg = MentorSuggestion.query.get_or_404(sugg_id)
    if sugg.student_id != current_user.id:
        flash("Unauthorized", "error")
        return redirect(url_for("main.mentors"))
    reason = request.form.get("reason", "").strip()
    if not reason:
        flash("Reason is required to reject a suggestion.", "error")
        return redirect(url_for("main.mentors"))
    sugg.status = "rejected"
    sugg.rejection_reason = reason
    
    # Send automated message
    from app.models.mentor import Message
    msg = Message(
        sender_id=current_user.id,
        receiver_id=sugg.mentor_id,
        content=f"I have rejected your {sugg.suggestion_type} suggestion '{sugg.title}'. Reason: {reason}"
    )
    db.session.add(msg)
    db.session.commit()
    flash("Suggestion rejected.", "info")
    return redirect(url_for("main.mentors"))


@main_bp.route("/mentors/request/<int:mentor_id>", methods=["POST"])
@login_required
def request_mentor(mentor_id):
    from app.models.user import User
    from app.models.mentor import MentorAssignment
    
    mentor = User.query.get_or_404(mentor_id)
    if not mentor.is_mentor:
        flash("User is not a mentor.", "error")
        return redirect(url_for("main.mentors"))
        
    assignment = MentorAssignment.query.filter_by(mentor_id=mentor.id, student_id=current_user.id).first()
    if assignment:
        if assignment.status == "rejected":
            assignment.status = "pending"
            db.session.commit()
            flash("Mentor request sent again.", "success")
        else:
            flash(f"You already have a {assignment.status} request with this mentor.", "info")
    else:
        new_assignment = MentorAssignment(mentor_id=mentor.id, student_id=current_user.id, status="pending")
        db.session.add(new_assignment)
        db.session.commit()
        flash("Mentor request sent.", "success")
        
    return redirect(url_for("main.mentors"))

@main_bp.route("/mentors/cancel/<int:mentor_id>", methods=["POST"])
@login_required
def cancel_mentor(mentor_id):
    from app.models.mentor import MentorAssignment
    from datetime import datetime
    
    assignment = MentorAssignment.query.filter_by(mentor_id=mentor_id, student_id=current_user.id, status="pending").first()
    if assignment:
        if (datetime.utcnow() - assignment.created_at).total_seconds() <= 300:
            db.session.delete(assignment)
            db.session.commit()
            flash("Mentor request cancelled.", "success")
        else:
            flash("Request cancellation window (5 minutes) has expired.", "error")
    
    return redirect(url_for("main.mentors"))

@main_bp.route("/mentors/messages/<int:mentor_id>", methods=["GET", "POST"])
@login_required
def mentor_messages(mentor_id):
    from app.models.user import User
    from app.models.mentor import MentorAssignment, Message
    
    mentor = User.query.get_or_404(mentor_id)
    assignment = MentorAssignment.query.filter_by(mentor_id=mentor.id, student_id=current_user.id, status="accepted").first()
    
    if not assignment:
        flash("You can only message mentors who have accepted your request.", "error")
        return redirect(url_for("main.mentors"))
        
    if request.method == "POST":
        content = request.form.get("content", "").strip()
        file = request.files.get("attachment")
        file_path = None
        file_name = None
        
        if file and file.filename:
            import os
            from werkzeug.utils import secure_filename
            from flask import current_app
            
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(current_app.config.get("UPLOAD_FOLDER", os.path.join(current_app.root_path, "..", "uploads")), "messages")
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, filename)
            file.save(save_path)
            
            file_path = f"messages/{filename}" # path relative to UPLOAD_FOLDER
            file_name = filename
            
        if content or file_name:
            msg = Message(sender_id=current_user.id, receiver_id=mentor.id, content=content,
                          file_path=file_path, file_name=file_name)
            db.session.add(msg)
            db.session.commit()
            return redirect(url_for("main.mentor_messages", mentor_id=mentor.id))
            
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == mentor.id)) |
        ((Message.sender_id == mentor.id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()
    
    # Mark incoming as read
    unread = [m for m in messages if m.receiver_id == current_user.id and not m.is_read]
    for m in unread:
        m.is_read = True
    if unread:
        db.session.commit()
    
    return render_template("messages.html", other_user=mentor, messages=messages)
