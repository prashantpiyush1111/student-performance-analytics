"""
utils/charts.py
----------------
Generates PNG chart images with Matplotlib + Seaborn and saves them into
static/charts/ so the dashboard's <img> tags can display them.

We save to disk (instead of trying to stream images directly) because
that's the simplest, most "student friendly" approach to get charts
showing up in an HTML page.
"""

import os
import matplotlib
matplotlib.use("Agg")  # no GUI window needed, just save files
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from utils.analytics import marks_dataframe, attendance_dataframe

CHART_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "charts")
os.makedirs(CHART_FOLDER, exist_ok=True)

sns.set_theme(style="whitegrid")


def generate_grade_distribution_chart():
    """Bar chart: how many results fall into each grade (A+, A, B, C, F)."""
    df = marks_dataframe()
    path = os.path.join(CHART_FOLDER, "grade_distribution.png")

    plt.figure(figsize=(6, 4))
    if not df.empty:
        order = ["A+", "A", "B", "C", "F"]
        sns.countplot(data=df, x="grade", order=order, hue="grade", palette="viridis", legend=False)
    plt.title("Grade Distribution")
    plt.xlabel("Grade")
    plt.ylabel("Number of Results")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return "charts/grade_distribution.png"


def generate_subject_average_chart():
    """Bar chart: average percentage per subject."""
    df = marks_dataframe()
    path = os.path.join(CHART_FOLDER, "subject_averages.png")

    plt.figure(figsize=(6, 4))
    if not df.empty:
        avg = df.groupby("subject_name")["percentage"].mean().reset_index()
        sns.barplot(data=avg, x="subject_name", y="percentage", hue="subject_name", palette="mako", legend=False)
        plt.xticks(rotation=30, ha="right")
    plt.title("Average Percentage by Subject")
    plt.xlabel("Subject")
    plt.ylabel("Average %")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return "charts/subject_averages.png"


def generate_attendance_vs_performance_chart():
    """Scatter plot: does attendance % relate to marks %?"""
    marks_df = marks_dataframe()
    att_df = attendance_dataframe()
    path = os.path.join(CHART_FOLDER, "attendance_vs_performance.png")

    plt.figure(figsize=(6, 4))
    if not marks_df.empty and not att_df.empty:
        m = marks_df.groupby("student_id")["percentage"].mean().reset_index()
        a = att_df.groupby("student_id")["attendance_percentage"].mean().reset_index()
        merged = pd.merge(m, a, on="student_id")
        sns.scatterplot(data=merged, x="attendance_percentage", y="percentage", s=80, color="teal")
    plt.title("Attendance % vs Marks %")
    plt.xlabel("Attendance %")
    plt.ylabel("Marks %")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return "charts/attendance_vs_performance.png"


def generate_all_charts():
    """Convenience function the dashboard route calls to refresh every chart at once."""
    return {
        "grade_distribution": generate_grade_distribution_chart(),
        "subject_averages": generate_subject_average_chart(),
        "attendance_vs_performance": generate_attendance_vs_performance_chart(),
    }
