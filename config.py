"""
config.py
---------
All the settings for the app live here in one place.
Edit MYSQL_USER / MYSQL_PASSWORD / MYSQL_DB to match your own MySQL setup.
"""

import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


class Config:
    # --- Change these to match your MySQL installation ---
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
    MYSQL_DB = os.environ.get("MYSQL_DB", "student_analytics_db")

    # SQLAlchemy connection string (uses the PyMySQL driver)
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{quote_plus(MYSQL_PASSWORD)}@{MYSQL_HOST}:"
        f"{MYSQL_PORT}/{MYSQL_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key is required explicitly so deployments cannot silently use
    # a predictable, publicly known fallback value.
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # Where generated reports (CSV/Excel) and chart images get saved
    REPORTS_FOLDER = os.path.join(os.path.dirname(__file__), "reports_output")
