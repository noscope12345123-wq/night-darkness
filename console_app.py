from __future__ import annotations

"""Console interface for Student Progress Tracker Pro Ultra.

References:
- Python tutorial for input/print/loops: https://docs.python.org/3/tutorial/
- colorama package: https://pypi.org/project/colorama/
"""

import sys

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLOR_ENABLED = True
except ImportError:
    COLOR_ENABLED = False

    class _Dummy:
        def __getattr__(self, name: str) -> str:
            return ""

    Fore = Style = _Dummy()

from corepkg import APP_NAME, StudentTracker, TrackerError, ValidationError


def tone(text: str, kind: str = "info") -> str:
    if not COLOR_ENABLED:
        return text
    colours = {
        "title": Fore.CYAN + Style.BRIGHT,
        "ok": Fore.GREEN + Style.BRIGHT,
        "warn": Fore.YELLOW + Style.BRIGHT,
        "bad": Fore.RED + Style.BRIGHT,
        "info": Fore.BLUE + Style.BRIGHT,
    }
    return f"{colours.get(kind, '')}{text}{Style.RESET_ALL}"


def header(title: str) -> None:
    line = "═" * 90
    print("\n" + tone(line, "title"))
    print(tone(title.center(90), "title"))
    print(tone(line, "title"))


def safe_input(prompt: str) -> str:
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print(tone("\nInput cancelled safely.", "warn"))
        return ""


def ask_float(prompt: str, default: float = 0.0) -> float:
    raw = safe_input(prompt).strip()
    if not raw:
        return default
    return float(raw)


def show_dashboard(tracker: StudentTracker) -> None:
    header(APP_NAME + " | Console Dashboard")
    stats = tracker.dashboard_metrics()
    print(f"Total students:  {stats['total_students']}")
    print(f"Graded students: {stats['graded_students']}")
    print(f"Overall average: {stats['overall_average']}")
    print(f"Pass rate:       {stats['pass_rate']}%")
    print(f"At-risk count:   {stats['at_risk_count']}")
    print(f"Top student:     {stats['top_student_name']}")
    print(f"Strongest module:{stats['strongest_module']}")


def list_students(tracker: StudentTracker) -> None:
    header("Student Table")
    sort_by = safe_input("Sort by [name/id/average/attendance/risk]: ").strip().lower() or "name"
    for student in tracker.sort_students(sort_by):
        average = tracker.calculate_student_average(student)
        average_text = f"{average:.2f}" if average is not None else "N/A"
        print(
            f"{student.student_id:10} | {student.name:20} | Avg {average_text:>6} | "
            f"Att {student.attendance:>6.1f}% | Risk {tracker.calculate_risk_score(student):>3}"
        )


def add_student_flow(tracker: StudentTracker) -> None:
    header("Add Student")
    try:
        tracker.add_student(
            safe_input("Student ID: "),
            safe_input("Name: "),
            safe_input("Email: "),
            safe_input("Course: "),
            ask_float("Attendance (0-100): ", 100.0),
            safe_input("Notes: "),
        )
        print(tone("Student added successfully.", "ok"))
    except (ValidationError, TrackerError, ValueError) as exc:
        print(tone(str(exc), "bad"))


def add_module_flow(tracker: StudentTracker) -> None:
    header("Add Module")
    try:
        tracker.add_module(safe_input("Student ID: "), safe_input("Module name: "), safe_input("Lecturer: "))
        print(tone("Module added successfully.", "ok"))
    except (ValidationError, TrackerError) as exc:
        print(tone(str(exc), "bad"))


def add_assessment_flow(tracker: StudentTracker) -> None:
    header("Add Assessment")
    try:
        tracker.add_assessment(
            safe_input("Student ID: "),
            safe_input("Module name: "),
            safe_input("Assessment name: "),
            ask_float("Score: "),
            ask_float("Weight: "),
            safe_input("Feedback: "),
        )
        print(tone("Assessment added successfully.", "ok"))
    except (ValidationError, TrackerError, ValueError) as exc:
        print(tone(str(exc), "bad"))


def search_flow(tracker: StudentTracker) -> None:
    header("Search Students")
    keyword = safe_input("Keyword: ")
    results = tracker.search_students(keyword)
    if not results:
        print(tone("No matching students found.", "warn"))
        return
    for student in results:
        print(
            f"{student.student_id} | {student.name} | {tracker.get_progress_status(student)} | "
            f"Trend: {tracker.calculate_trend(student)}"
        )


def detail_flow(tracker: StudentTracker) -> None:
    header("Student Detail")
    try:
        student = tracker.get_student(safe_input("Student ID: ").strip())
        info = tracker.summary_for_student(student)
        print(f"Name:           {student.name}")
        print(f"Email:          {student.email}")
        print(f"Course:         {student.course}")
        print(f"Attendance:     {student.attendance}%")
        print(f"Average:        {info['average']}")
        print(f"Grade band:     {info['grade_band']}")
        print(f"Status:         {info['status']}")
        print(f"Trend:          {info['trend']}")
        print(f"Risk score:     {info['risk']}")
        print(f"Recommendation: {info['recommendation']}")
        print("Modules:")
        for module in student.modules.values():
            module_avg = tracker.calculate_module_average(module)
            print(f"  - {module.module_name} ({module.lecturer}) | Avg: {module_avg}")
            for assessment in module.assessments:
                print(f"      * {assessment.name}: {assessment.score}% ({assessment.weight}%)")
    except TrackerError as exc:
        print(tone(str(exc), "bad"))


def export_flow(tracker: StudentTracker) -> None:
    header("Export")
    path = tracker.export_csv()
    print(tone(f"CSV exported to {path}", "ok"))


def seed_flow(tracker: StudentTracker) -> None:
    header("Seed Demo Data")
    try:
        tracker.seed_demo_data()
        print(tone("Demo data inserted.", "ok"))
    except TrackerError as exc:
        print(tone(str(exc), "warn"))


def main() -> None:
    tracker = StudentTracker()
    actions = {
        "1": show_dashboard,
        "2": list_students,
        "3": add_student_flow,
        "4": add_module_flow,
        "5": add_assessment_flow,
        "6": search_flow,
        "7": detail_flow,
        "8": export_flow,
        "9": seed_flow,
    }
    while True:
        header(APP_NAME)
        print("1. Dashboard")
        print("2. List students")
        print("3. Add student")
        print("4. Add module")
        print("5. Add assessment")
        print("6. Search students")
        print("7. View student detail")
        print("8. Export CSV")
        print("9. Seed demo data")
        print("0. Exit")
        choice = safe_input("Choose an option: ").strip()
        if choice == "0":
            print(tone("Goodbye.", "info"))
            sys.exit(0)
        action = actions.get(choice)
        if action:
            action(tracker)
            input("\nPress Enter to continue...")
        else:
            print(tone("Invalid choice.", "warn"))


if __name__ == "__main__":
    main()
