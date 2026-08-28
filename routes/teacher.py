"""
routes/teacher.py
------------------
Everything a Teacher can do: view the class list, enter/update marks,
enter/update attendance, and view a student's performance analysis.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Student, Subject, Marks, Attendance
from utils.decorators import role_required
from utils import analytics

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")


@teacher_bp.route("/dashboard")
@role_required("teacher")
def dashboard():
    overview = analytics.class_overview()
    return render_template("teacher/dashboard.html", overview=overview)


@teacher_bp.route("/students")
@role_required("teacher")
def view_students():
    students = Student.query.join(Student.user).all()
    return render_template("teacher/students.html", students=students)


# ---------------------------------------------------------------- Marks
@teacher_bp.route("/marks", methods=["GET", "POST"])
@role_required("teacher")
def enter_marks():
    subjects = Subject.query.all()
    students = Student.query.all()

    if request.method == "POST":
        student_id = request.form.get("student_id", type=int)
        subject_id = request.form.get("subject_id", type=int)
        internal = request.form.get("internal_marks", type=float)
        external = request.form.get("external_marks", type=float)
        subject = Subject.query.get(subject_id)

        # --- Validation: no marks above the subject's maximum ---
        if internal is None or external is None:
            flash("Please enter both internal and external marks.", "danger")
        elif internal < 0 or internal > subject.max_internal:
            flash(f"Internal marks must be between 0 and {subject.max_internal}.", "danger")
        elif external < 0 or external > subject.max_external:
            flash(f"External marks must be between 0 and {subject.max_external}.", "danger")
        else:
            record = Marks.query.filter_by(student_id=student_id, subject_id=subject_id).first()
            if record:
                record.internal_marks = internal
                record.external_marks = external
            else:
                record = Marks(student_id=student_id, subject_id=subject_id,
                                internal_marks=internal, external_marks=external)
                db.session.add(record)
            db.session.commit()
            flash("Marks saved.", "success")
        return redirect(url_for("teacher.enter_marks"))

    existing_marks = Marks.query.all()
    return render_template("teacher/marks.html", subjects=subjects, students=students, existing_marks=existing_marks)


# ---------------------------------------------------------------- Attendance
@teacher_bp.route("/attendance", methods=["GET", "POST"])
@role_required("teacher")
def enter_attendance():
    subjects = Subject.query.all()
    students = Student.query.all()

    if request.method == "POST":
        student_id = request.form.get("student_id", type=int)
        subject_id = request.form.get("subject_id", type=int)
        total = request.form.get("total_classes", type=int)
        attended = request.form.get("attended_classes", type=int)

        # --- Validation: attended can't exceed total, no negatives ---
        if total is None or attended is None or total < 0 or attended < 0:
            flash("Please enter valid class counts.", "danger")
        elif attended > total:
            flash("Attended classes cannot be more than total classes.", "danger")
        else:
            record = Attendance.query.filter_by(student_id=student_id, subject_id=subject_id).first()
            if record:
                record.total_classes = total
                record.attended_classes = attended
            else:
                record = Attendance(student_id=student_id, subject_id=subject_id,
                                     total_classes=total, attended_classes=attended)
                db.session.add(record)
            db.session.commit()
            flash("Attendance saved.", "success")
        return redirect(url_for("teacher.enter_attendance"))

    existing_attendance = Attendance.query.all()
    return render_template("teacher/attendance.html", subjects=subjects, students=students,
                            existing_attendance=existing_attendance)


# ---------------------------------------------------------------- View one student
@teacher_bp.route("/student/<int:student_id>")
@role_required("teacher")
def view_student(student_id):
    student = Student.query.get_or_404(student_id)
    summary = analytics.student_summary(student_id)
    return render_template("teacher/student_detail.html", student=student, summary=summary)
