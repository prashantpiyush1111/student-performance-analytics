"""
scripts/seed_data.py
---------------------
Creates all the tables (if they don't already exist) and fills the
database with:
  - one Admin login
  - one Teacher login
  - a few sample Students with marks + attendance

HOW TO RUN (after creating the empty database with schema.sql, or even
without running schema.sql -- this script can create the tables too):
    python scripts/seed_data.py

LOGIN DETAILS CREATED:
    Admin    -> username: admin     password: admin123
    Teacher  -> username: teacher1  password: teacher123
    Students -> username: student1 ... student5   password: student123
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models import User, Student, Teacher, Subject, Marks, Attendance

app = create_app()

with app.app_context():
    db.create_all()  # creates any missing tables based on models.py

    # --- Admin ---
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", role="admin", full_name="System Admin", email="admin@school.edu")
        db.session.add(admin)
    admin.set_password("admin123")

    # --- Teacher ---
    teacher_user = User.query.filter_by(username="teacher1").first()
    if not teacher_user:
        teacher_user = User(username="teacher1", role="teacher", full_name="Mrs. Sharma", email="sharma@school.edu")
        db.session.add(teacher_user)
        db.session.flush()  # so teacher_user.id is available
        db.session.add(Teacher(user_id=teacher_user.id, specialization="Computer Science"))
    teacher_user.set_password("teacher123")

    # --- Subjects ---
    subject_data = [
        ("PY101", "Python Programming", 4),
        ("DBMS201", "DBMS", 4),
        ("WD301", "Web Development", 4),
        ("MA401", "Mathematics", 4),
    ]
    subjects = []
    for code, name, sem in subject_data:
        subj = Subject.query.filter_by(subject_code=code).first()
        if not subj:
            subj = Subject(subject_code=code, subject_name=name, semester=sem)
            db.session.add(subj)
            db.session.flush()
        subjects.append(subj)

    # --- Students + marks + attendance ---
    sample_students = [
        ("student1", "Aarav Sharma", "CS21001"),
        ("student2", "Priya Verma", "CS21002"),
        ("student3", "Rohan Gupta", "CS21003"),
        ("student4", "Isha Patel", "CS21004"),
        ("student5", "Kabir Singh", "CS21005"),
    ]

    import random
    random.seed(1)

    for username, name, roll in sample_students:
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username, role="student", full_name=name, email=f"{username}@school.edu")
            db.session.add(user)
            db.session.flush()
            student = Student(user_id=user.id, roll_number=roll, course="B.Tech CS", semester=4, section="A")
            db.session.add(student)
            db.session.flush()

            for subj in subjects:
                internal = round(random.uniform(10, 30), 1)
                external = round(random.uniform(20, 70), 1)
                total_classes = 60
                attended = random.randint(30, 60)

                db.session.add(Marks(student_id=student.id, subject_id=subj.id,
                                      internal_marks=internal, external_marks=external))
                db.session.add(Attendance(student_id=student.id, subject_id=subj.id,
                                           total_classes=total_classes, attended_classes=attended))
            user.set_password("student123")

    db.session.commit()
    print("Seed data created successfully!")
    print("Login as admin / admin123, teacher1 / teacher123, or student1..5 / student123")
