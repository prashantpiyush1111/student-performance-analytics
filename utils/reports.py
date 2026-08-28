"""
utils/reports.py
-----------------
Turns the Pandas DataFrames from analytics.py into downloadable
CSV / Excel files, saved inside reports_output/.
"""

import os
from datetime import datetime
from utils.analytics import marks_dataframe, attendance_dataframe
from config import Config

os.makedirs(Config.REPORTS_FOLDER, exist_ok=True)


def _timestamped_filename(base_name, extension):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{ts}.{extension}"


def generate_performance_report_csv():
    df = marks_dataframe()
    filename = _timestamped_filename("student_performance_report", "csv")
    path = os.path.join(Config.REPORTS_FOLDER, filename)
    df.to_csv(path, index=False)
    return filename


def generate_performance_report_excel():
    df = marks_dataframe()
    filename = _timestamped_filename("student_performance_report", "xlsx")
    path = os.path.join(Config.REPORTS_FOLDER, filename)
    df.to_excel(path, index=False, sheet_name="Performance")
    return filename


def generate_attendance_report_csv():
    df = attendance_dataframe()
    filename = _timestamped_filename("attendance_report", "csv")
    path = os.path.join(Config.REPORTS_FOLDER, filename)
    df.to_csv(path, index=False)
    return filename
