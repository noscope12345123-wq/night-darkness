from __future__ import annotations

"""Analytics helpers for averages, trends, risk, and recommendations.

References:
- statistics.mean: https://docs.python.org/3/library/statistics.html
- built-in sum/max/min/round: https://docs.python.org/3/library/functions.html
"""

from statistics import mean
from typing import List, Optional

from .models import ModuleRecord, Student

PASS_MARK = 40.0


def calculate_module_average(module: ModuleRecord) -> Optional[float]:
    """Return the weighted average for a module or None if unavailable."""
    if not module.assessments:
        return None
    total_weight = sum(item.weight for item in module.assessments)
    if total_weight <= 0:
        return None
    weighted_points = sum(item.score * item.weight for item in module.assessments)
    return round(weighted_points / total_weight, 2)


def calculate_student_average(student: Student) -> Optional[float]:
    """Return mean module average across all completed modules."""
    module_averages = [
        avg for module in student.modules.values()
        if (avg := calculate_module_average(module)) is not None
    ]
    if not module_averages:
        return None
    return round(mean(module_averages), 2)


def get_grade_band(score: float) -> str:
    """Map a numeric score to a grade band label."""
    if score >= 70:
        return "First / Distinction"
    if score >= 60:
        return "Upper Second / Merit"
    if score >= 50:
        return "Lower Second / Pass+"
    if score >= PASS_MARK:
        return "Third / Pass"
    return "Fail"


def get_progress_status(student: Student) -> str:
    """Return a human-readable performance status."""
    average = calculate_student_average(student)
    if average is None:
        return "Insufficient data"
    if average < PASS_MARK or student.attendance < 50:
        return "Critical risk"
    if average < 50 or student.attendance < 70:
        return "Needs support"
    if average >= 70 and student.attendance >= 85:
        return "Excellent"
    return "Stable"


def module_score_timeline(student: Student) -> List[float]:
    """Collect assessment scores in insertion order for trend analysis."""
    timeline: List[float] = []
    for module in student.modules.values():
        for assessment in module.assessments:
            timeline.append(float(assessment.score))
    return timeline


def calculate_trend(student: Student) -> str:
    """Describe whether recent scores appear to improve or decline."""
    scores = module_score_timeline(student)
    if len(scores) < 2:
        return "No trend"
    if scores[-1] > scores[0]:
        return "Improving"
    if scores[-1] < scores[0]:
        return "Declining"
    return "Steady"


def calculate_risk_score(student: Student) -> int:
    """Compute a simple risk score using attendance, average, and trend."""
    risk = 0
    average = calculate_student_average(student)
    if average is None:
        risk += 25
    else:
        if average < 40:
            risk += 50
        elif average < 50:
            risk += 30
        elif average < 60:
            risk += 10
    if student.attendance < 50:
        risk += 35
    elif student.attendance < 70:
        risk += 20
    elif student.attendance < 80:
        risk += 10
    trend = calculate_trend(student)
    if trend == "Declining":
        risk += 15
    elif trend == "Improving":
        risk -= 5
    return max(0, min(100, risk))


def generate_recommendation(student: Student) -> str:
    """Create a pseudo-intelligent recommendation for the student."""
    average = calculate_student_average(student)
    risk = calculate_risk_score(student)
    trend = calculate_trend(student)
    if average is None:
        return "Add module assessments to generate a stronger academic analysis."
    if risk >= 70:
        return "Urgent intervention recommended: schedule tutor support and improve attendance immediately."
    if student.attendance < 70:
        return "Attendance is weakening performance; prioritise class participation and weekly review sessions."
    if trend == "Declining":
        return "Performance trend is declining; revise earlier topics and request feedback from lecturers."
    if average >= 70 and student.attendance >= 85:
        return "Excellent trajectory; maintain your revision routine and aim for distinction-level consistency."
    return "Performance is generally stable; target weaker modules and keep assessments on schedule."
