"""
extensions.py
-------------
We create the SQLAlchemy "db" object here (separately from app.py) to avoid
circular-import problems: models.py needs "db", and app.py needs both
models.py and "db". Everyone imports it from this one neutral file.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
