"""
utils/analytics.py
-------------------
This is the "brain" of the analytics side of the project.
It pulls raw rows out of the database, loads them into a Pandas
DataFrame, and calculates percentage, grade, attendance %, and risk level.
Keeping this logic in its own file (separate from the Flask routes) makes
it easy to re-use the same calculations on the Admin dashboard, the
Teacher's view, and the Student's own report card.
"""

import pandas as pd
from models import Student, Subject, Marks, Attendance, User


def marks_dataframe():
    """
    Pulls every marks row from the DB and returns a clean Pandas DataFrame
    with one row per (student, subject), including computed totals.
    """
    rows = []
    for m in Marks.query.all():
        max_total = m.subject.max_internal + m.subject.max_external
        total = m.internal_marks + m.external_marks
        percentage = round((total / max_total) * 100, 2) if max_total else 0
        rows.append({
            "student_id": m.student_id,
            "roll_number": m.student.roll_number,
            "student_name": m.student.user.full_name,
            "subject_id": m.subject_id,
            "subject_name": m.subject.subject_name,
            "internal_marks": m.internal_marks,
            "external_marks": m.external_marks,
            "total_marks": total,
            "max_marks": max_total,
            "percentage": percentage,
            "grade": marks_to_grade(percentage),
            "pass_fail": "Pass" if percentage >= 40 else "Fail",
        })
    return pd.DataFrame(rows)


def attendance_dataframe():
    """Same idea as marks_dataframe(), but for attendance records."""
    rows = []
    for a in Attendance.query.all():
        pct = round((a.attended_classes / a.total_classes) * 100, 2) if a.total_classes else 0
        rows.append({
            "student_id": a.student_id,
            "roll_number": a.student.roll_number,
            "subject_id": a.subject_id,
            "subject_name": a.subject.subject_name,
            "total_classes": a.total_classes,
            "attended_classes": a.attended_classes,
            "attendance_percentage": pct,
        })
    return pd.DataFrame(rows)


def marks_to_grade(percentage):
    """Simple percentage -> letter grade rule. Tweak the cutoffs if needed."""
    if percentage >= 85:
        return "A+"
    elif percentage >= 70:
        return "A"
    elif percentage >= 55:
        return "B"
    elif percentage >= 40:
        return "C"
    else:
        return "F"


def risk_level(avg_percentage, avg_attendance):
    """
    Combines academic performance and attendance into one Low/Medium/High
    risk label using simple percentage rules.
    """
    if avg_percentage < 40 or avg_attendance < 60:
        return "High"
    elif avg_percentage < 60 or avg_attendance < 75:
        return "Medium"
    else:
        return "Low"


def student_summary(student_id):
    """
    Builds one full summary dict for a single student:
    per-subject marks, overall percentage, overall attendance, grade,
    rank in their section, and risk level. Used on the student's own
    dashboard and the teacher/admin "view student" page.
    """
    marks_df = marks_dataframe()
    att_df = attendance_dataframe()

    student_marks = marks_df[marks_df["student_id"] == student_id]
    student_att = att_df[att_df["student_id"] == student_id]

    overall_percentage = round(student_marks["percentage"].mean(), 2) if not student_marks.empty else 0
    overall_attendance = round(student_att["attendance_percentage"].mean(), 2) if not student_att.empty else 0

    return {
        "subjects": student_marks.to_dict(orient="records"),
        "attendance": student_att.to_dict(orient="records"),
        "overall_percentage": overall_percentage,
        "overall_attendance": overall_attendance,
        "overall_grade": marks_to_grade(overall_percentage),
        "risk_level": risk_level(overall_percentage, overall_attendance),
    }


def class_overview():
    """
    Produces the numbers shown on the Admin/Teacher dashboard cards:
    total students, average marks, average attendance, and how many
    students currently fall into the "High" risk bucket.
    """
    marks_df = marks_dataframe()
    att_df = attendance_dataframe()

    total_students = Student.query.count()

    avg_marks = round(marks_df["percentage"].mean(), 2) if not marks_df.empty else 0
    avg_attendance = round(att_df["attendance_percentage"].mean(), 2) if not att_df.empty else 0

    # Work out risk per student, then count how many are "High"
    at_risk_count = 0
    if not marks_df.empty:
        per_student_marks = marks_df.groupby("student_id")["percentage"].mean()
        per_student_att = att_df.groupby("student_id")["attendance_percentage"].mean() if not att_df.empty else pd.Series(dtype=float)
        for sid, pct in per_student_marks.items():
            att_pct = per_student_att.get(sid, 0)
            if risk_level(pct, att_pct) == "High":
                at_risk_count += 1

    return {
        "total_students": total_students,
        "avg_marks": avg_marks,
        "avg_attendance": avg_attendance,
        "at_risk_count": at_risk_count,
    }


def grade_distribution():
    """Counts how many subject-results fall into each grade. Used for the bar chart."""
    marks_df = marks_dataframe()
    if marks_df.empty:
        return {}
    return marks_df["grade"].value_counts().to_dict()


def subject_averages():
    """Average percentage per subject. Used for the subject-comparison chart."""
    marks_df = marks_dataframe()
    if marks_df.empty:
        return {}
    return marks_df.groupby("subject_name")["percentage"].mean().round(2).to_dict()


def at_risk_students():
    """Returns a list of every student currently classified as Medium/High risk."""
    marks_df = marks_dataframe()
    att_df = attendance_dataframe()
    if marks_df.empty:
        return []

    per_student_marks = marks_df.groupby(["student_id", "roll_number", "student_name"])["percentage"].mean().reset_index()
    per_student_att = att_df.groupby("student_id")["attendance_percentage"].mean() if not att_df.empty else pd.Series(dtype=float)

    results = []
    for _, row in per_student_marks.iterrows():
        att_pct = per_student_att.get(row["student_id"], 0)
        level = risk_level(row["percentage"], att_pct)
        if level in ("Medium", "High"):
            results.append({
                "student_id": row["student_id"],
                "roll_number": row["roll_number"],
                "student_name": row["student_name"],
                "percentage": round(row["percentage"], 2),
                "attendance": round(att_pct, 2),
                "risk_level": level,
            })
    # Show the worst cases first
    results.sort(key=lambda r: (r["risk_level"] != "High", -r["percentage"]))
    return results
