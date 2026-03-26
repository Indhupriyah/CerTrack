"""Certification routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from app import db
from app.models.certification import Certification, Resource
import json
import os

cert_bp = Blueprint("certifications", __name__)


@cert_bp.route("/")
@login_required
def list_view():
    """Kanban list view."""
    certs = Certification.query.filter_by(user_id=current_user.id).order_by(
        Certification.expected_completion.asc().nullslast()
    ).all()
    
    today = date.today()
    upcoming = [c for c in certs if c.status == "upcoming"]
    in_progress = [c for c in certs if c.status == "in_progress"]
    completed = [c for c in certs if c.status == "completed"]
    
    return render_template(
        "certifications/list.html",
        upcoming=upcoming,
        in_progress=in_progress,
        completed=completed,
        today=today
    )


@cert_bp.route("/calendar")
@login_required
def calendar_view():
    """Calendar view."""
    return render_template("certifications/calendar.html")


@cert_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        platform = request.form.get("platform", "").strip()
        status = request.form.get("status", "upcoming")
        skill_tags = request.form.get("skill_tags", "").strip()
        
        reg_deadline = request.form.get("registration_deadline")
        exp_completion = request.form.get("expected_completion")
        
        reg = datetime.strptime(reg_deadline, "%Y-%m-%d").date() if reg_deadline else None
        exp = datetime.strptime(exp_completion, "%Y-%m-%d").date() if exp_completion else None
        
        cert = Certification(
            user_id=current_user.id,
            name=name,
            platform=platform,
            status=status,
            skill_tags=skill_tags,
            registration_deadline=reg,
            expected_completion=exp
        )
        db.session.add(cert)
        db.session.commit()
        
        flash("Certification added successfully.", "success")
        return redirect(url_for("certifications.list_view"))
    
    return render_template("certifications/form.html", certification=None)


@cert_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    cert = Certification.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if request.method == "POST":
        cert.name = request.form.get("name", cert.name).strip()
        cert.platform = request.form.get("platform", cert.platform).strip()
        cert.status = request.form.get("status", cert.status)
        cert.skill_tags = request.form.get("skill_tags", cert.skill_tags).strip()
        
        reg = request.form.get("registration_deadline")
        exp = request.form.get("expected_completion")
        comp = request.form.get("completed_date")
        
        cert.registration_deadline = datetime.strptime(reg, "%Y-%m-%d").date() if reg else None
        cert.expected_completion = datetime.strptime(exp, "%Y-%m-%d").date() if exp else None
        cert.completed_date = datetime.strptime(comp, "%Y-%m-%d").date() if comp else None
        
        if cert.status == "completed":
            from app.models.mentor import MentorSuggestion, Message
            sugg = MentorSuggestion.query.filter_by(
                student_id=current_user.id, 
                suggestion_type="certificate", 
                title=cert.name,
                status="accepted"
            ).first()
            if sugg:
                sugg.status = "completed"
                msg = Message(
                    sender_id=current_user.id,
                    receiver_id=sugg.mentor_id,
                    content=f"I have successfully completed the certificate you suggested: '{sugg.title}'!"
                )
                db.session.add(msg)
        
        db.session.commit()
        flash("Certification updated.", "success")
        return redirect(url_for("certifications.list_view"))
    
    return render_template("certifications/form.html", certification=cert)


@cert_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    cert = Certification.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(cert)
    db.session.commit()
    flash("Certification removed.", "info")
    return redirect(url_for("certifications.list_view"))


def _days_remaining(d):
    if not d:
        return None
    delta = (d - date.today()).days
    return delta


@cert_bp.route("/<int:id>")
@login_required
def detail(id):
    cert = Certification.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    resources = cert.resources.all()
    today = date.today()
    days_reg = _days_remaining(cert.registration_deadline) if cert.registration_deadline and cert.registration_deadline >= today else None
    days_completion = _days_remaining(cert.expected_completion) if cert.expected_completion and cert.expected_completion >= today else None
    return render_template(
        "certifications/detail.html",
        certification=cert,
        resources=resources,
        days_until_reg=days_reg,
        days_until_completion=days_completion
    )


@cert_bp.route("/<int:id>/upload-certificate", methods=["POST"])
@login_required
def upload_certificate(id):
    from flask import current_app
    cert = Certification.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    file = request.files.get("certificate")
    if file and file.filename:
        ext = file.filename.rsplit(".", 1)[-1].lower()
        if ext in {"pdf", "png", "jpg", "jpeg"}:
            upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "certificates")
            os.makedirs(upload_dir, exist_ok=True)
            filename = f"{current_user.id}_{cert.id}_{datetime.utcnow().strftime('%Y%m%d%H%M')}.{ext}"
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            cert.certificate_file = f"certificates/{filename}"
            cert.status = "completed"
            cert.completed_date = date.today()
            
            from app.models.mentor import MentorSuggestion, Message
            sugg = MentorSuggestion.query.filter_by(
                student_id=current_user.id, 
                suggestion_type="certificate", 
                title=cert.name,
                status="accepted"
            ).first()
            if sugg:
                sugg.status = "completed"
                msg = Message(
                    sender_id=current_user.id,
                    receiver_id=sugg.mentor_id,
                    content=f"I have successfully completed the certificate you suggested: '{sugg.title}'!"
                )
                db.session.add(msg)
                
            db.session.commit()
            flash("Certificate uploaded successfully.", "success")
        else:
            flash("Invalid file type. Use PDF, PNG, or JPG.", "error")
    else:
        flash("No file selected.", "error")
    
    return redirect(url_for("certifications.detail", id=id))


@cert_bp.route("/<int:id>/delete-certificate", methods=["POST"])
@login_required
def delete_certificate(id):
    cert = Certification.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    cert.certificate_file = None
    cert.status = "in_progress"
    cert.completed_date = None
    db.session.commit()
    flash("Certificate removed.", "info")
    return redirect(url_for("certifications.detail", id=id))


@cert_bp.route("/<int:id>/resources/add", methods=["POST"])
@login_required
def add_resource(id):
    cert = Certification.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    rtype = request.form.get("resource_type", "url")
    title = request.form.get("title", "").strip()
    url = request.form.get("url", "").strip()
    notes = request.form.get("notes", "").strip()
    
    res = Resource(certification_id=cert.id, resource_type=rtype, title=title, url=url, notes=notes)
    db.session.add(res)
    db.session.commit()
    flash("Resource added.", "success")
    return redirect(url_for("certifications.detail", id=id))


@cert_bp.route("/<int:id>/resources/<int:rid>/delete", methods=["POST"])
@login_required
def delete_resource(id, rid):
    cert = Certification.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    res = Resource.query.filter_by(id=rid, certification_id=cert.id).first_or_404()
    db.session.delete(res)
    db.session.commit()
    flash("Resource removed.", "info")
    return redirect(url_for("certifications.detail", id=id))


# API for Kanban drag-drop status update (updates status, analytics, and calendar data)
@cert_bp.route("/api/<int:id>/status", methods=["PATCH", "POST"])
@login_required
def update_status(id):
    cert = Certification.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    data = request.get_json() or request.form
    status = data.get("status")
    if status in ("upcoming", "in_progress", "completed"):
        old_status = cert.status
        cert.status = status
        if status == "completed":
            cert.completed_date = cert.completed_date or date.today()

        # Sync analytics: record completion when moving to completed
        if status == "completed" and old_status != "completed":
            today = date.today()
            from app.models.analytics import Analytics
            from app.models.mentor import MentorSuggestion, Message
            
            rec = Analytics.query.filter_by(
                user_id=current_user.id,
                activity_date=today
            ).first()
            if rec:
                rec.certifications_completed = (rec.certifications_completed or 0) + 1
            else:
                rec = Analytics(
                    user_id=current_user.id,
                    activity_date=today,
                    certifications_completed=1
                )
                db.session.add(rec)
                
            sugg = MentorSuggestion.query.filter_by(
                student_id=current_user.id, 
                suggestion_type="certificate", 
                title=cert.name,
                status="accepted"
            ).first()
            if sugg:
                sugg.status = "completed"
                msg = Message(
                    sender_id=current_user.id,
                    receiver_id=sugg.mentor_id,
                    content=f"I have successfully completed the certificate you suggested: '{sugg.title}'!"
                )
                db.session.add(msg)

        db.session.commit()
        return jsonify({"ok": True, "status": cert.status})
    return jsonify({"ok": False}, 400)
