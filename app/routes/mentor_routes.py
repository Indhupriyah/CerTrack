"""Faculty / Mentor portal: monitor assigned students, progress, gaps, at-risk."""
from flask import Blueprint, render_template, redirect, url_for, abort, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.mentor import MentorAssignment
from app.services.mentor_placement_helpers import get_student_metrics_for_mentor
from app.utils.mentor_placement_decorators import mentor_required

mentor_bp = Blueprint("mentor", __name__, url_prefix="/mentor")


@mentor_bp.route("/settings", methods=["GET", "POST"])
@login_required
@mentor_required
def settings():
    if request.method == "POST":
        current_user.display_name = request.form.get("display_name", current_user.display_name).strip()
        current_user.department = request.form.get("department", "").strip()
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("mentor.dashboard"))
    return render_template("mentor/settings.html")


@mentor_bp.route("/")
@login_required
@mentor_required
def dashboard():
    assignments = MentorAssignment.query.filter_by(mentor_id=current_user.id).all()
    requests = []
    students = []
    
    for a in assignments:
        student = User.query.get(a.student_id)
        if not student or student.deleted_at:
            continue
            
        if a.status == "pending":
            requests.append({
                "assignment": a,
                "student": student
            })
        elif a.status == "accepted":
            m = get_student_metrics_for_mentor(student.id)
            if m:
                students.append({
                    "assignment": a,
                    "student": student,
                    "metrics": m,
                })
                
    inactive = [s for s in students if s["metrics"]["inactive"]]
    at_risk = [s for s in students if s["metrics"]["at_risk"]]
    
    return render_template(
        "mentor/dashboard.html",
        students=students,
        requests=requests,
        inactive=inactive,
        at_risk=at_risk,
    )

@mentor_bp.route("/accept/<int:assignment_id>", methods=["POST"])
@login_required
@mentor_required
def accept_request(assignment_id):
    assignment = MentorAssignment.query.get_or_404(assignment_id)
    if assignment.mentor_id != current_user.id:
        abort(403)
    assignment.status = "accepted"
    db.session.commit()
    return redirect(url_for("mentor.dashboard"))

@mentor_bp.route("/reject/<int:assignment_id>", methods=["POST"])
@login_required
@mentor_required
def reject_request(assignment_id):
    assignment = MentorAssignment.query.get_or_404(assignment_id)
    if assignment.mentor_id != current_user.id:
        abort(403)
    assignment.status = "rejected"
    db.session.commit()
    return redirect(url_for("mentor.dashboard"))

@mentor_bp.route("/remove/<int:student_id>", methods=["POST"])
@login_required
@mentor_required
def remove_student(student_id):
    assignment = MentorAssignment.query.filter_by(mentor_id=current_user.id, student_id=student_id).first()
    if assignment:
        db.session.delete(assignment)
        db.session.commit()
        flash("Student removed successfully.", "success")
    return redirect(url_for("mentor.dashboard"))

@mentor_bp.route("/student/<int:student_id>")
@login_required
@mentor_required
def student_detail(student_id):
    assignment = MentorAssignment.query.filter_by(mentor_id=current_user.id, student_id=student_id).first()
    if not assignment or assignment.status != "accepted":
        if not current_user.is_admin:
            abort(403)
    m = get_student_metrics_for_mentor(student_id)
    if not m:
        abort(404)
    return render_template("mentor/student_detail.html", metrics=m)

@mentor_bp.route("/messages/<int:student_id>", methods=["GET", "POST"])
@login_required
@mentor_required
def mentor_messages(student_id):
    from app.models.mentor import Message
    student = User.query.get_or_404(student_id)
    assignment = MentorAssignment.query.filter_by(mentor_id=current_user.id, student_id=student_id, status="accepted").first()
    
    if not assignment:
        abort(403)
        
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
            
            # Use relative path internally for static serving or download
            file_path = f"messages/{filename}"
            file_name = filename
            
        if content or file_name:
            msg = Message(sender_id=current_user.id, receiver_id=student_id, content=content,
                          file_path=file_path, file_name=file_name)
            db.session.add(msg)
            db.session.commit()
            return redirect(url_for("mentor.mentor_messages", student_id=student_id))
            
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == student_id)) |
        ((Message.sender_id == student_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()
    
    # Mark incoming as read
    unread = [m for m in messages if m.receiver_id == current_user.id and not m.is_read]
    for m in unread:
        m.is_read = True
    if unread:
        db.session.commit()
    
    return render_template("mentor/messages.html", other_user=student, messages=messages)

@mentor_bp.route("/suggestions")
@login_required
@mentor_required
def track_suggestions():
    from app.models.mentor import MentorSuggestion
    suggestions = MentorSuggestion.query.filter_by(mentor_id=current_user.id).order_by(MentorSuggestion.created_at.desc()).all()
    
    accepted = [s for s in suggestions if s.status in ("accepted", "completed")]
    rejected = [s for s in suggestions if s.status == "rejected"]
    
    return render_template("mentor/suggestions.html", accepted_suggestions=accepted, rejected_suggestions=rejected)

@mentor_bp.route("/suggest/certificate", methods=["GET", "POST"])
@login_required
@mentor_required
def suggest_certificate():
    from app.models.mentor import MentorAssignment, MentorSuggestion
    if request.method == "POST":
        title = request.form.get("title")
        duration = request.form.get("duration")
        link = request.form.get("link")
        skills = request.form.get("skills")
        
        assignments = MentorAssignment.query.filter_by(mentor_id=current_user.id, status="accepted").all()
        for a in assignments:
            sugg = MentorSuggestion(
                mentor_id=current_user.id,
                student_id=a.student_id,
                suggestion_type="certificate",
                title=title,
                duration=duration,
                link=link,
                skills=skills
            )
            db.session.add(sugg)
        db.session.commit()
        flash("Certificate suggested to all mentees.", "success")
        return redirect(url_for("mentor.track_suggestions"))
    return render_template("mentor/suggest_certificate.html")

@mentor_bp.route("/suggest/event", methods=["GET", "POST"])
@login_required
@mentor_required
def suggest_event():
    from app.models.mentor import MentorAssignment, MentorSuggestion
    if request.method == "POST":
        title = request.form.get("title")
        location = request.form.get("location")
        offline_location = request.form.get("offline_location")
        team_size = request.form.get("team_size")
        description = request.form.get("description")
        
        file = request.files.get("file")
        file_path = None
        if file and file.filename:
            import os
            from werkzeug.utils import secure_filename
            from flask import current_app
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(current_app.config.get("UPLOAD_FOLDER", os.path.join(current_app.root_path, "..", "uploads")), "suggestions")
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, filename)
            file.save(save_path)
            file_path = f"suggestions/{filename}"
            
        if location == "Offline" and offline_location:
            location = f"Offline: {offline_location}"
            
        assignments = MentorAssignment.query.filter_by(mentor_id=current_user.id, status="accepted").all()
        for a in assignments:
            sugg = MentorSuggestion(
                mentor_id=current_user.id,
                student_id=a.student_id,
                suggestion_type="event",
                title=title,
                description=description,
                location=location,
                team_size=team_size,
                file_path=file_path
            )
            db.session.add(sugg)
        db.session.commit()
        flash("Event suggested to all mentees.", "success")
        return redirect(url_for("mentor.track_suggestions"))
    return render_template("mentor/suggest_event.html")

