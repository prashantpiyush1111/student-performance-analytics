"""
routes/admin.py
----------------
Everything the Admin can do:
  - dashboard with overview cards + charts
  - add/view students, teachers, subjects
  - view at-risk students
  - download reports (CSV/Excel)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from extensions import db
from models import User, Student, Teacher, Subject
from utils.decorators import role_required
from utils import analytics, charts, reports
from config import Config

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@role_required("admin")
def dashboard():
    overview = analytics.class_overview()
    chart_paths = charts.generate_all_charts()
    return render_template("admin/dashboard.html", overview=overview, charts=chart_paths)


# ---------------------------------------------------------------- Students
@admin_bp.route("/students", methods=["GET", "POST"])
@role_required("admin")
def manage_students():
    if request.method == "POST":
        username = request.form["username"].strip()
        full_name = request.form["full_name"].strip()
        roll_number = request.form["roll_number"].strip()
        course = request.form.get("course", "").strip()
        semester = request.form.get("semester", type=int)
        section = request.form.get("section", "").strip()
        password = request.form.get("password") or "student123"

        if User.query.filter_by(username=username).first():
            flash("That username is already taken.", "danger")
        elif Student.query.filter_by(roll_number=roll_number).first():
            flash("That roll number already exists.", "danger")
        else:
            user = User(username=username, role="student", full_name=full_name)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()  # gets user.id before commit

            student = Student(user_id=user.id, roll_number=roll_number,
                               course=course, semester=semester, section=section)
            db.session.add(student)
            db.session.commit()
            flash(f"Student {full_name} added. Default password: {password}", "success")
        return redirect(url_for("admin.manage_students"))

    students = Student.query.join(User).all()
    return render_template("admin/students.html", students=students)


@admin_bp.route("/students/delete/<int:student_id>", methods=["POST"])
@role_required("admin")
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    user = User.query.get(student.user_id)
    db.session.delete(student)
    if user:
        db.session.delete(user)  # cascades to marks/attendance via FK
    db.session.commit()
    flash("Student removed.", "info")
    return redirect(url_for("admin.manage_students"))


# ---------------------------------------------------------------- Teachers
@admin_bp.route("/teachers", methods=["GET", "POST"])
@role_required("admin")
def manage_teachers():
    if request.method == "POST":
        username = request.form["username"].strip()
        full_name = request.form["full_name"].strip()
        specialization = request.form.get("specialization", "").strip()
        password = request.form.get("password") or "teacher123"

        if User.query.filter_by(username=username).first():
            flash("That username is already taken.", "danger")
        else:
            user = User(username=username, role="teacher", full_name=full_name)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            db.session.add(Teacher(user_id=user.id, specialization=specialization))
            db.session.commit()
            flash(f"Teacher {full_name} added. Default password: {password}", "success")
        return redirect(url_for("admin.manage_teachers"))

    teachers = Teacher.query.join(User).all()
    return render_template("admin/teachers.html", teachers=teachers)


# ---------------------------------------------------------------- Subjects
@admin_bp.route("/subjects", methods=["GET", "POST"])
@role_required("admin")
def manage_subjects():
    if request.method == "POST":
        code = request.form["subject_code"].strip()
        name = request.form["subject_name"].strip()
        semester = request.form.get("semester", type=int)
        max_internal = request.form.get("max_internal", type=int) or 30
        max_external = request.form.get("max_external", type=int) or 70

        # --- Validation (rule from the synopsis: no silently-bad data) ---
        if Subject.query.filter_by(subject_code=code).first():
            flash("Subject code already exists.", "danger")
        elif max_internal + max_external != 100:
            flash("Max internal + max external marks must add up to 100.", "danger")
        else:
            db.session.add(Subject(subject_code=code, subject_name=name, semester=semester,
                                    max_internal=max_internal, max_external=max_external))
            db.session.commit()
            flash(f"Subject {name} added.", "success")
        return redirect(url_for("admin.manage_subjects"))

    subjects = Subject.query.all()
    return render_template("admin/subjects.html", subjects=subjects)


# ---------------------------------------------------------------- Analytics / Risk
@admin_bp.route("/at-risk")
@role_required("admin")
def at_risk():
    risky = analytics.at_risk_students()
    return render_template("admin/at_risk.html", students=risky)


# ---------------------------------------------------------------- Reports
@admin_bp.route("/reports")
@role_required("admin")
def reports_page():
    return render_template("admin/reports.html")


@admin_bp.route("/reports/generate/<report_type>")
@role_required("admin")
def generate_report(report_type):
    if report_type == "performance_csv":
        filename = reports.generate_performance_report_csv()
    elif report_type == "performance_excel":
        filename = reports.generate_performance_report_excel()
    elif report_type == "attendance_csv":
        filename = reports.generate_attendance_report_csv()
    else:
        flash("Unknown report type.", "danger")
        return redirect(url_for("admin.reports_page"))

    return redirect(url_for("admin.download_report", filename=filename))


@admin_bp.route("/reports/download/<filename>")
@role_required("admin")
def download_report(filename):
    return send_from_directory(Config.REPORTS_FOLDER, filename, as_attachment=True)
