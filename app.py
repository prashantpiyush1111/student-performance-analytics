"""
app.py
------
This is the file you actually run:  python app.py

It creates the Flask app, connects it to MySQL, registers all the
blueprints (auth/admin/teacher/student route groups), and starts the
development server.
"""

from flask import Flask
from sqlalchemy import text
from dotenv import load_dotenv
from config import Config
from extensions import db

load_dotenv()

# Import models so SQLAlchemy knows about every table before create_all()
import models  # noqa: F401


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY environment variable must be set")

    db.init_app(app)

    # --- Register route blueprints ---
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.teacher import teacher_bp
    from routes.student import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)

    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        result = db.session.execute(
            text("SELECT COUNT(*) FROM students")
        )
        print("Total students:", result.scalar())

    # debug=True auto-reloads the server whenever you save a file --
    # very handy while you're building/demoing the project.
    app.run(debug=True)
