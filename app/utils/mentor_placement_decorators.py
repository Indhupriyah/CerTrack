"""Mentor-only and Placement-only route decorators."""
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def mentor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in.", "error")
            return redirect(url_for("auth.login"))
        if not getattr(current_user, "is_mentor", False) and not getattr(current_user, "is_admin", False):
            flash("Access denied. Mentor portal only.", "error")
            return redirect(url_for("main.landing"))
        if current_user.deleted_at or current_user.is_suspended:
            flash("Account suspended or deactivated.", "error")
            return redirect(url_for("main.landing"))
        return f(*args, **kwargs)
    return decorated

    return decorated
