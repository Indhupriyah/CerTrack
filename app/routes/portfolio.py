"""Portfolio routes - private and public view."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.certification import Certification

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


@portfolio_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        current_user.portfolio_public = bool(request.form.get("portfolio_public"))
        current_user.display_name = request.form.get("display_name", current_user.display_name).strip()
        mg = request.form.get("monthly_goal", "5").strip()
        try:
            current_user.monthly_goal = max(1, min(50, int(mg)))
        except ValueError:
            current_user.monthly_goal = 5
        current_user.linkedin_url = request.form.get("linkedin_url", "").strip()
        current_user.github_url = request.form.get("github_url", "").strip()
        db.session.commit()
        flash("Portfolio settings updated.", "success")
        return redirect(url_for("portfolio.index"))
    
    return render_template("portfolio/settings.html")


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
