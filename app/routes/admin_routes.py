"""Admin hub: dashboard, user management, cert templates, reports, file storage, action log."""
import os
from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models.user import User
from app.models.certification import Certification, Resource
from app.models.event import Event
from app.models.analytics import Analytics
from app.models.career_admin import CareerRole, CertificationTemplate, Report, AdminActionLog
from app.models.mentor import MentorAssignment
from app.utils.admin_decorator import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _log_action(action, target_type=None, target_id=None, details=None):
    log = AdminActionLog(
        admin_id=current_user.id,
        action=action,
        target_type=target_type,
        target_id=str(target_id) if target_id is not None else None,
        details=details,
    )
    db.session.add(log)
    db.session.commit()


def _active_users_query():
    return User.query.filter(User.deleted_at.is_(None))


# ---------- Dashboard ----------
@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    now = date.today()
    week_ago = now - timedelta(days=7)
    users = _active_users_query()
    total_users = users.count()
    active_7d = users.filter(User.updated_at >= datetime.combine(week_ago, datetime.min.time())).count()
    total_certs = Certification.query.count()
    total_events = Event.query.count()
    deleted_users = User.query.filter(User.deleted_at.isnot(None)).count()
    # File storage: sum of certificate files
    certs_with_file = Certification.query.filter(Certification.certificate_file.isnot(None)).count()
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
    storage_mb = 0.0
    file_count = 0
    if os.path.isdir(upload_dir):
        for root, _, files in os.walk(upload_dir):
            for f in files:
                fp = os.path.join(root, f)
                if os.path.isfile(fp):
                    storage_mb += os.path.getsize(fp) / (1024 * 1024)
                    file_count += 1
    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        active_7d=active_7d,
        total_certs=total_certs,
        total_events=total_events,
        deleted_count=deleted_users,
        file_count=file_count,
        storage_mb=round(storage_mb, 2),
    )


# ---------- User Management ----------
@admin_bp.route("/users")
@login_required
@admin_required
def user_list():
    q = _active_users_query()
    search = request.args.get("q", "").strip()
    if search:
        q = q.filter(
            db.or_(
                User.email.ilike(f"%{search}%"),
                User.display_name.ilike(f"%{search}%"),
            )
        )
    users = q.order_by(User.created_at.desc()).limit(100).all()
    return render_template("admin/users.html", users=users, search=search)


@admin_bp.route("/users/<int:user_id>")
@login_required
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    cert_count = Certification.query.filter_by(user_id=user_id).count()
    event_count = Event.query.filter_by(user_id=user_id).count()
    return render_template("admin/user_detail.html", user=user, cert_count=cert_count, event_count=event_count)


@admin_bp.route("/users/<int:user_id>/suspend", methods=["POST"])
@login_required
@admin_required
def user_suspend(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot suspend yourself.", "error")
        return redirect(url_for("admin.user_detail", user_id=user_id))
    user.is_suspended = True
    db.session.commit()
    _log_action("suspend_user", "user", user_id, f"email={user.email}")
    flash(f"User {user.email} suspended.", "success")
    return redirect(url_for("admin.user_detail", user_id=user_id))


@admin_bp.route("/users/<int:user_id>/unsuspend", methods=["POST"])
@login_required
@admin_required
def user_unsuspend(user_id):
    user = User.query.get_or_404(user_id)
    user.is_suspended = False
    db.session.commit()
    _log_action("unsuspend_user", "user", user_id, f"email={user.email}")
    flash(f"User {user.email} unsuspended.", "success")
    return redirect(url_for("admin.user_detail", user_id=user_id))


@admin_bp.route("/users/<int:user_id>/delete", methods=["GET", "POST"])
@login_required
@admin_required
def user_delete(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete your own account.", "error")
        return redirect(url_for("admin.user_list"))
    if request.method == "POST" and request.form.get("confirm") == "yes":
        user.deleted_at = datetime.utcnow()
        db.session.commit()
        _log_action("soft_delete_user", "user", user_id, f"email={user.email}")
        flash("User deactivated (soft delete).", "success")
        return redirect(url_for("admin.user_list"))
    return render_template("admin/user_confirm_delete.html", user=user)


@admin_bp.route("/users/<int:user_id>/set-mentor", methods=["POST"])
@login_required
@admin_required
def user_set_mentor(user_id):
    user = User.query.get_or_404(user_id)
    user.is_mentor = not user.is_mentor
    db.session.commit()
    _log_action("set_mentor" if user.is_mentor else "unset_mentor", "user", user_id, user.email)
    flash("Mentor role updated.", "success")
    return redirect(url_for("admin.user_detail", user_id=user_id))


@admin_bp.route("/users/<int:user_id>/reset-password", methods=["POST"])
@login_required
@admin_required
def user_reset_password(user_id):
    from app.utils.auth import hash_password
    user = User.query.get_or_404(user_id)
    new_password = request.form.get("new_password", "").strip()
    if not new_password or len(new_password) < 6:
        flash("Password must be at least 6 characters.", "error")
        return redirect(url_for("admin.user_detail", user_id=user_id))
    user.password_hash = hash_password(new_password)
    db.session.commit()
    _log_action("reset_password", "user", user_id, "password reset by admin")
    flash("Password reset successfully.", "success")
    return redirect(url_for("admin.user_detail", user_id=user_id))


# ---------- Certification Templates ----------
@admin_bp.route("/cert-templates")
@login_required
@admin_required
def cert_templates():
    templates = CertificationTemplate.query.filter_by(is_active=True).order_by(CertificationTemplate.name).all()
    return render_template("admin/cert_templates.html", templates=templates)


@admin_bp.route("/cert-templates/new", methods=["GET", "POST"])
@login_required
@admin_required
def cert_template_new():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        platform = request.form.get("platform", "").strip()
        category = request.form.get("category", "").strip()
        skill_tags = request.form.get("skill_tags", "").strip()
        if not name:
            flash("Name is required.", "error")
            return render_template("admin/cert_template_form.html", template=None)
        t = CertificationTemplate(name=name, platform=platform or None, category=category or None, skill_tags=skill_tags or None)
        db.session.add(t)
        db.session.commit()
        _log_action("create_cert_template", "certification_template", t.id, name)
        flash("Template created.", "success")
        return redirect(url_for("admin.cert_templates"))
    return render_template("admin/cert_template_form.html", template=None)


@admin_bp.route("/cert-templates/<int:tid>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def cert_template_edit(tid):
    t = CertificationTemplate.query.get_or_404(tid)
    if request.method == "POST":
        t.name = request.form.get("name", "").strip() or t.name
        t.platform = request.form.get("platform", "").strip() or None
        t.category = request.form.get("category", "").strip() or None
        t.skill_tags = request.form.get("skill_tags", "").strip() or None
        db.session.commit()
        _log_action("update_cert_template", "certification_template", tid, t.name)
        flash("Template updated.", "success")
        return redirect(url_for("admin.cert_templates"))
    return render_template("admin/cert_template_form.html", template=t)


@admin_bp.route("/cert-templates/<int:tid>/delete", methods=["POST"])
@login_required
@admin_required
def cert_template_delete(tid):
    t = CertificationTemplate.query.get_or_404(tid)
    t.is_active = False
    db.session.commit()
    _log_action("delete_cert_template", "certification_template", tid, t.name)
    flash("Template deactivated.", "success")
    return redirect(url_for("admin.cert_templates"))


# ---------- Reports & Issues ----------
@admin_bp.route("/reports")
@login_required
@admin_required
def reports():
    status_filter = request.args.get("status", "")
    q = Report.query
    if status_filter:
        q = q.filter_by(status=status_filter)
    reports_list = q.order_by(Report.created_at.desc()).limit(100).all()
    return render_template("admin/reports.html", reports=reports_list, status_filter=status_filter)


@admin_bp.route("/reports/<int:rid>/resolve", methods=["GET", "POST"])
@login_required
@admin_required
def report_resolve(rid):
    r = Report.query.get_or_404(rid)
    if request.method == "POST":
        r.status = "resolved"
        r.admin_notes = request.form.get("admin_notes", "").strip()
        r.resolved_at = datetime.utcnow()
        r.resolved_by_id = current_user.id
        db.session.commit()
        _log_action("resolve_report", "report", rid, r.title)
        flash("Report marked resolved.", "success")
        return redirect(url_for("admin.reports"))
    return render_template("admin/report_resolve.html", report=r)


# ---------- File Storage ----------
@admin_bp.route("/storage")
@login_required
@admin_required
def storage():
    certs = Certification.query.filter(Certification.certificate_file.isnot(None)).all()
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
    files_info = []
    for c in certs:
        path = c.certificate_file
        if path and not path.startswith("/"):
            full = os.path.join(root, path)
        else:
            full = path
        size = 0
        if full and os.path.isfile(full):
            size = os.path.getsize(full)
        files_info.append({"cert": c, "path": path, "size_mb": round(size / (1024 * 1024), 4)})
    files_info.sort(key=lambda x: -x["size_mb"])
    total_mb = sum(x["size_mb"] for x in files_info)
    return render_template("admin/storage.html", files_info=files_info, total_mb=round(total_mb, 2))


@admin_bp.route("/storage/remove/<int:cert_id>", methods=["POST"])
@login_required
@admin_required
def storage_remove_file(cert_id):
    c = Certification.query.get_or_404(cert_id)
    path = c.certificate_file
    if path:
        root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
        full = os.path.join(root, path) if not path.startswith("/") else path
        if os.path.isfile(full):
            try:
                os.remove(full)
            except OSError:
                pass
        c.certificate_file = None
        db.session.commit()
        _log_action("remove_certificate_file", "certification", cert_id, path)
        flash("File removed from record.", "success")
    return redirect(url_for("admin.storage"))


# ---------- Action Log ----------
@admin_bp.route("/action-log")
@login_required
@admin_required
def action_log():
    logs = AdminActionLog.query.order_by(AdminActionLog.created_at.desc()).limit(200).all()
    return render_template("admin/action_log.html", logs=logs)


# ---------- Mentor assignments (Faculty portal) ----------
@admin_bp.route("/mentors")
@login_required
@admin_required
def mentor_assignments():
    mentors = User.query.filter(User.deleted_at.is_(None), User.is_mentor == True).order_by(User.display_name).all()
    assignments = MentorAssignment.query.order_by(MentorAssignment.mentor_id).all()
    by_mentor = {}
    for a in assignments:
        by_mentor.setdefault(a.mentor_id, []).append(a)
    students = User.query.filter(
        User.deleted_at.is_(None),
        User.is_mentor == False,
    ).filter(db.or_(User.is_admin == False, User.is_admin.is_(None))).order_by(User.display_name).all()
    return render_template("admin/mentor_assignments.html", mentors=mentors, by_mentor=by_mentor, students=students)


@admin_bp.route("/mentors/assign", methods=["POST"])
@login_required
@admin_required
def mentor_assign_add():
    mentor_id = request.form.get("mentor_id", type=int)
    student_id = request.form.get("student_id", type=int)
    if mentor_id and student_id:
        if not MentorAssignment.query.filter_by(mentor_id=mentor_id, student_id=student_id).first():
            db.session.add(MentorAssignment(mentor_id=mentor_id, student_id=student_id))
            db.session.commit()
            _log_action("mentor_assign", "mentor", mentor_id, f"student_id={student_id}")
            flash("Student assigned to mentor.", "success")
    return redirect(url_for("admin.mentor_assignments"))


@admin_bp.route("/mentors/unassign/<int:aid>", methods=["POST"])
@login_required
@admin_required
def mentor_assign_remove(aid):
    a = MentorAssignment.query.get_or_404(aid)
    db.session.delete(a)
    db.session.commit()
    _log_action("mentor_unassign", "mentor", a.mentor_id, f"student_id={a.student_id}")
    flash("Assignment removed.", "success")
    return redirect(url_for("admin.mentor_assignments"))


# ---------- Career roles (admin can manage for gap analyzer) ----------
@admin_bp.route("/career-roles")
@login_required
@admin_required
def career_roles():
    roles = CareerRole.query.filter_by(is_active=True).order_by(CareerRole.name).all()
    return render_template("admin/career_roles.html", roles=roles)


@admin_bp.route("/career-roles/new", methods=["GET", "POST"])
@login_required
@admin_required
def career_role_new():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        required_skills = request.form.get("required_skills", "").strip()
        recommended_cert_keywords = request.form.get("recommended_cert_keywords", "").strip()
        if not name or not required_skills:
            flash("Name and required skills are required.", "error")
            return render_template("admin/career_role_form.html", role=None)
        r = CareerRole(name=name, required_skills=required_skills, recommended_cert_keywords=recommended_cert_keywords or None)
        db.session.add(r)
        db.session.commit()
        _log_action("create_career_role", "career_role", r.id, name)
        flash("Career role created.", "success")
        return redirect(url_for("admin.career_roles"))
    return render_template("admin/career_role_form.html", role=None)


@admin_bp.route("/career-roles/<int:rid>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def career_role_edit(rid):
    role = CareerRole.query.get_or_404(rid)
    if request.method == "POST":
        role.name = request.form.get("name", "").strip() or role.name
        role.required_skills = request.form.get("required_skills", "").strip() or role.required_skills
        role.recommended_cert_keywords = request.form.get("recommended_cert_keywords", "").strip() or None
        db.session.commit()
        _log_action("update_career_role", "career_role", rid, role.name)
        flash("Career role updated.", "success")
        return redirect(url_for("admin.career_roles"))
    return render_template("admin/career_role_form.html", role=role)
