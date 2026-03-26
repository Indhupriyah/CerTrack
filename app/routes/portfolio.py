"""Portfolio routes - private and public view."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import date
from app import db
from app.models.user import User
from app.models.certification import Certification
from app.models.monthly_goal import MonthlyGoal

portfolio_bp = Blueprint("portfolio", __name__)


@portfolio_bp.route("/")
@login_required
def index():
    certs = Certification.query.filter_by(
        user_id=current_user.id,
        status="completed"
    ).order_by(Certification.completed_date.desc()).all()
    
    # Skill tags aggregation
    skill_counts = {}
    for c in certs:
        if c.skill_tags:
            for tag in [t.strip() for t in c.skill_tags.split(",") if t.strip()]:
                skill_counts[tag] = skill_counts.get(tag, 0) + 1
    
    return render_template("portfolio/index.html", certifications=certs, skill_counts=skill_counts)


def _goal_for_month(user, year, month):
    row = MonthlyGoal.query.filter_by(user_id=user.id, year=year, month=month).first()
    return row.target if row else (user.monthly_goal or 5)


@portfolio_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    now = date.today()
    if request.method == "POST":
        current_user.portfolio_public = bool(request.form.get("portfolio_public"))
        current_user.display_name = request.form.get("display_name", current_user.display_name).strip()
        current_user.email = request.form.get("email", current_user.email).strip()
        current_user.department = request.form.get("department", "").strip()
        current_user.year_of_study = request.form.get("year_of_study", "").strip()
        
        file = request.files.get("profile_picture")
        if file and file.filename:
            import os
            from werkzeug.utils import secure_filename
            from flask import current_app
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(current_app.config.get("UPLOAD_FOLDER", os.path.join(current_app.root_path, "..", "uploads")), "profiles")
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, filename)
            file.save(save_path)
            current_user.profile_picture = f"profiles/{filename}"
            
        default_goal = request.form.get("default_monthly_goal", "5").strip()
        try:
            current_user.monthly_goal = max(1, min(50, int(default_goal)))
        except ValueError:
            current_user.monthly_goal = 5
        current_user.linkedin_url = request.form.get("linkedin_url", "").strip()
        current_user.github_url = request.form.get("github_url", "").strip()
        # Per-month goals: goal_YYYY_MM
        for key, value in request.form.items():
            if key.startswith("goal_") and "_" in key:
                try:
                    parts = key.split("_")
                    if len(parts) == 3:
                        y, m = int(parts[1]), int(parts[2])
                        if 1 <= m <= 12 and 2020 <= y <= 2030:
                            val = value.strip()
                            if not val:
                                MonthlyGoal.query.filter_by(
                                    user_id=current_user.id, year=y, month=m
                                ).delete()
                            else:
                                target = int(val)
                                if 1 <= target <= 50:
                                    existing = MonthlyGoal.query.filter_by(
                                        user_id=current_user.id, year=y, month=m
                                    ).first()
                                    if existing:
                                        existing.target = target
                                    else:
                                        db.session.add(MonthlyGoal(
                                            user_id=current_user.id, year=y, month=m, target=target
                                        ))
                except (ValueError, IndexError):
                    pass
        db.session.commit()
        flash("Settings updated.", "success")
        return redirect(url_for("portfolio.index"))
    
    # Build list of months for per-month goal form: past 2, current, next 9
    months_for_goals = []
    for i in range(-2, 10):
        m = now.month + i
        y = now.year
        while m > 12:
            m -= 12
            y += 1
        while m < 1:
            m += 12
            y -= 1
        months_for_goals.append({
            "year": y, "month": m,
            "label": date(y, m, 1).strftime("%B %Y"),
            "goal": _goal_for_month(current_user, y, m),
        })
    return render_template("portfolio/settings.html", months_for_goals=months_for_goals)


@portfolio_bp.route("/public/<slug>")
def public(slug):
    """Public shareable portfolio - no login required."""
    user = User.query.filter_by(public_slug=slug).first()
    if not user:
        abort(404)
    
    if not user.portfolio_public:
        abort(404)
    
    certs = Certification.query.filter_by(
        user_id=user.id,
        status="completed"
    ).order_by(Certification.completed_date.desc()).all()
    
    skill_counts = {}
    for c in certs:
        if c.skill_tags:
            for tag in [t.strip() for t in c.skill_tags.split(",") if t.strip()]:
                skill_counts[tag] = skill_counts.get(tag, 0) + 1
    
    return render_template("portfolio/public.html", user=user, certifications=certs, skill_counts=skill_counts)
