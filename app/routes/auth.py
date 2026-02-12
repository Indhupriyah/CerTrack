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
        if user and check_password(user.password_hash, password):
            login_user(user, remember=bool(request.form.get("remember")))
            next_page = request.args.get("next") or url_for("main.dashboard")
            return redirect(next_page)
        
        flash("Invalid email or password.", "error")
    
    return render_template("auth/login.html")


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
