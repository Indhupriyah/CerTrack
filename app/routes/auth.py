"""Authentication routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.utils.auth import hash_password, check_password, generate_slug

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        
        user = User.query.filter_by(email=email).first()
        if not user or not check_password(user.password_hash, password):
            flash("Invalid email or password.", "error")
        elif user.deleted_at or user.is_suspended:
            flash("This account is suspended or deactivated.", "error")
        else:
            login_user(user, remember=bool(request.form.get("remember")))
            next_page = request.args.get("next")
            if not next_page:
                if getattr(user, "is_placement", False):
                    next_page = url_for("placement.dashboard")
                elif getattr(user, "is_mentor", False):
                    next_page = url_for("mentor.dashboard")
                else:
                    next_page = url_for("main.dashboard")
            else:
                if "mentor" in next_page and not getattr(user, "is_mentor", False):
                    next_page = url_for("main.dashboard")
                    flash("You do not have mentor access.", "info")
                elif "placement" in next_page and not getattr(user, "is_placement", False):
                    next_page = url_for("main.dashboard")
                    flash("You do not have placement cell access.", "info")
            return redirect(next_page)
    
    return render_template("auth/login.html")


@auth_bp.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    """Admin sign-in: username + password only. Redirects to /admin after login."""
    if current_user.is_authenticated and getattr(current_user, "is_admin", False):
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = None
        if username:
            from sqlalchemy import or_
            user = User.query.filter(
                or_(User.username == username, User.email == username.lower())
            ).first()
        if not user or not check_password(user.password_hash, password):
            flash("Invalid username or password.", "error")
        elif user.deleted_at or user.is_suspended:
            flash("This account is suspended or deactivated.", "error")
        elif not getattr(user, "is_admin", False):
            flash("This account does not have admin access.", "error")
        else:
            login_user(user, remember=bool(request.form.get("remember")))
            return redirect(url_for("admin.dashboard"))
    return render_template("auth/admin_login.html")


@auth_bp.route("/mentor-login", methods=["GET", "POST"])
def mentor_login():
    """Mentor sign-in: email + password. Redirects to /mentor after login."""
    if current_user.is_authenticated and getattr(current_user, "is_mentor", False):
        return redirect(url_for("mentor.dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password(user.password_hash, password):
            flash("Invalid email or password.", "error")
        elif user.deleted_at or user.is_suspended:
            flash("This account is suspended or deactivated.", "error")
        elif not getattr(user, "is_mentor", False):
            flash("This account does not have mentor access.", "error")
        else:
            login_user(user, remember=bool(request.form.get("remember")))
            return redirect(url_for("mentor.dashboard"))
    return render_template("auth/mentor_login.html")


@auth_bp.route("/placement-login", methods=["GET", "POST"])
def placement_login():
    """Placement cell sign-in: email + password. Redirects to /placement after login."""
    if current_user.is_authenticated and getattr(current_user, "is_placement", False):
        return redirect(url_for("placement.dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password(user.password_hash, password):
            flash("Invalid email or password.", "error")
        elif user.deleted_at or user.is_suspended:
            flash("This account is suspended or deactivated.", "error")
        elif not getattr(user, "is_placement", False):
            flash("This account does not have placement cell access.", "error")
        else:
            login_user(user, remember=bool(request.form.get("remember")))
            return redirect(url_for("placement.dashboard"))
    return render_template("auth/placement_login.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        display_name = request.form.get("display_name", "").strip()
        
        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("auth/signup.html")
        
        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "error")
            return render_template("auth/signup.html")
        
        user = User(
            email=email,
            password_hash=hash_password(password),
            display_name=display_name or email.split("@")[0],
            public_slug=generate_slug()
        )
        db.session.add(user)
        db.session.commit()
        
        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("auth/signup.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.landing"))


# OAuth placeholders - implement with Authlib or similar when credentials are set
@auth_bp.route("/google")
def google_login():
    flash("Google login not configured. Use email/password.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/github")
def github_login():
    flash("GitHub login not configured. Use email/password.", "info")
    return redirect(url_for("auth.login"))
