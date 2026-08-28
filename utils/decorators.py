"""
utils/decorators.py
--------------------
Small reusable decorators that protect routes:
  @login_required        -> user must be logged in (any role)
  @role_required("admin")-> user must be logged in AND have that role
"""

from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)
    return wrapped


def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("auth.login"))
            if session.get("role") != role:
                flash("You don't have permission to view that page.", "danger")
                return redirect(url_for("auth.dashboard_redirect"))
            return view_func(*args, **kwargs)
        return wrapped
    return decorator
