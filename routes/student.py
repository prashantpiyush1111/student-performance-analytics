"""
routes/student.py
------------------
Everything a Student can see about themselves: profile, marks,
attendance, and performance analysis.
"""

from flask import Blueprint, render_template, session, flash, redirect, url_for
from models import Student
from utils.decorators import role_required
from utils import analytics

student_bp = Blueprint("student", __name__, url_prefix="/student")


def _current_student():
    """Every student route needs to find the Student row for the logged-in user."""
    return Student.query.filter_by(user_id=session["user_id"]).first()


@student_bp.route("/dashboard")
@role_required("student")
def dashboard():
    student = _current_student()
    if not student:
        flash("No student profile found for this account.", "danger")
        return redirect(url_for("auth.login"))

    summary = analytics.student_summary(student.id)
    return render_template("student/dashboard.html", student=student, summary=summary)
