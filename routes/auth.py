"""
routes/auth.py
---------------
Handles login, logout, and sending each role to its own dashboard.
We use Flask's built-in `session` (cookie-based) instead of a login
library, so it's easy to follow as a student project.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET"])
def index():
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Save the important bits in the session cookie
            session["user_id"] = user.id
            session["role"] = user.role
            session["full_name"] = user.full_name
            flash(f"Welcome back, {user.full_name}!", "success")
            return redirect(url_for("auth.dashboard_redirect"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/dashboard")
def dashboard_redirect():
    """After login, send the user to the right dashboard for their role."""
    role = session.get("role")
    if role == "admin":
        return redirect(url_for("admin.dashboard"))
    elif role == "teacher":
        return redirect(url_for("teacher.dashboard"))
    elif role == "student":
        return redirect(url_for("student.dashboard"))
    return redirect(url_for("auth.login"))
