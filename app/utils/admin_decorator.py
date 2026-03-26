"""Admin-only route decorator and helpers."""
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def admin_required(f):
    """Restrict route to users with is_admin=True. Excludes suspended/deleted."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in.", "error")
            return redirect(url_for("auth.login"))
        if not getattr(current_user, "is_admin", False) or current_user.is_suspended or current_user.deleted_at:
            flash("Access denied. Admin only.", "error")
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)
    return decorated
