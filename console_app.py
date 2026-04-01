from __future__ import annotations

'''
Console version of Student Progress Tracker Pro.

References used in this file:
- Python tutorial on input/print/control flow: https://docs.python.org/3/tutorial/
- Colorama package page: https://pypi.org/project/colorama/
- Python exception handling tutorial: https://docs.python.org/3/tutorial/errors.html
'''

import sys

try:
    from colorama import Fore, Style, init  # Reference: https://pypi.org/project/colorama/

    init(autoreset=True)
    COLOUR_ENABLED = True
except ImportError:
    COLOUR_ENABLED = False

    class _Dummy:
        def __getattr__(self, _name: str) -> str:
            return ""

    Fore = Style = _Dummy()

from core import APP_NAME, StudentTracker, TrackerError, ValidationError


def colour(text: str, tone: str = "info") -> str:
    '''Return coloured text when colorama is installed.'''
    if not COLOUR_ENABLED:
        return text

    mapping = {
        "title": Fore.CYAN + Style.BRIGHT,
        "success": Fore.GREEN + Style.BRIGHT,
        "warning": Fore.YELLOW + Style.BRIGHT,
        "danger": Fore.RED + Style.BRIGHT,
        "info": Fore.BLUE + Style.BRIGHT,
    }
    return f"{mapping.get(tone, '')}{text}{Style.RESET_ALL}"


def line() -> None:
    '''Print a separator line.'''
    print(colour("=" * 78, "title"))


def heading(title: str) -> None:
    '''Print a styled heading.'''
    line()
    print(colour(title.center(78), "title"))
    line()


def safe_input(prompt: str) -> str:
    '''Wrap input() with safe handling for Ctrl+C and EOF.'''
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print(colour("\nInput cancelled by user.", "warning"))
        return ""
    except EOFError:
        print(colour("\nNo more input available. Program will close safely.", "danger"))
        sys.exit(0)


def ask_float(prompt: str) -> float:
    '''Request a numeric value from the user until it is valid.'''
    while True:
        try:
            return float(safe_input(prompt).strip())
        except ValueError:
            print(colour("Please enter a numeric value.", "warning"))


def print_student(tracker: StudentTracker, student_id: str) -> None:
    '''Print a single student summary to the console.'''
    student = tracker.get_student(student_id)
    data = tracker.serialise_student(student)
    print(f"ID: {data['student_id']}")
    print(f"Name: {data['name']}")
    print(f"Email: {data['email']}")
    print(f"Course: {data['course']}")
    print(f"Attendance: {data['attendance']}%")
    print(f"Average: {data['average']}")
    print(f"Status: {data['status']}")
    print(f"Recommendation: {data['recommendation']}")
    print(f"Notes: {data['notes']}")
    print(f"Updated: {data['updated_at']}")


def list_students(tracker: StudentTracker) -> None:
    '''Show all students sorted by a chosen field.'''
    sort_by = safe_input("Sort by name / id / attendance / average: ").strip().lower() or "name"
    heading("Student List")
    for student in tracker.sort_students(sort_by):
        average = tracker.calculate_student_average(student)
        average_text = "No grades" if average is None else f"{average:.2f}"
        print(f"{student.student_id:10} | {student.name:15} | {student.attendance:6.1f}% | {average_text:8} | {tracker.get_progress_status(student)}")


def search_students(tracker: StudentTracker) -> None:
    '''Run the explicit search algorithm and print results.'''
    keyword = safe_input("Enter keyword to search: ").strip()
    results = tracker.search_students(keyword)
    heading(f"Search Results: {len(results)} found")
    if not results:
        print("No matching students were found.")
        return
    for student in results:
        print(f"{student.student_id} - {student.name} - {tracker.get_progress_status(student)}")


def add_student_menu(tracker: StudentTracker) -> None:
    '''Interactive menu for creating one student.'''
    try:
        tracker.add_student(
            safe_input("Student ID: ").strip(),
            safe_input("Name: ").strip(),
            safe_input("Email: ").strip(),
            safe_input("Course: ").strip(),
            ask_float("Attendance (0-100): "),
            safe_input("Notes: ").strip(),
        )
        print(colour("Student added successfully.", "success"))
    except (ValidationError, TrackerError, ValueError) as exc:
        print(colour(str(exc), "danger"))


def update_student_menu(tracker: StudentTracker) -> None:
    '''Interactive menu for updating one student.'''
    try:
        tracker.update_student(
            safe_input("Student ID to update: ").strip(),
            safe_input("New name: ").strip(),
            safe_input("New email: ").strip(),
            safe_input("New course: ").strip(),
            ask_float("New attendance: "),
            safe_input("New notes: ").strip(),
        )
        print(colour("Student updated successfully.", "success"))
    except (ValidationError, TrackerError, ValueError) as exc:
        print(colour(str(exc), "danger"))


def add_module_menu(tracker: StudentTracker) -> None:
    '''Interactive menu for adding a module.'''
    try:
        tracker.add_module(
            safe_input("Student ID: ").strip(),
            safe_input("Module name: ").strip(),
            safe_input("Lecturer: ").strip(),
        )
        print(colour("Module added successfully.", "success"))
    except (ValidationError, TrackerError) as exc:
        print(colour(str(exc), "danger"))


def add_assessment_menu(tracker: StudentTracker) -> None:
    '''Interactive menu for adding an assessment.'''
    try:
        tracker.add_assessment(
            safe_input("Student ID: ").strip(),
            safe_input("Module name: ").strip(),
            safe_input("Assessment name: ").strip(),
            ask_float("Score: "),
            ask_float("Weight: "),
            safe_input("Feedback: ").strip(),
        )
        print(colour("Assessment added successfully.", "success"))
    except (ValidationError, TrackerError, ValueError) as exc:
        print(colour(str(exc), "danger"))


def dashboard(tracker: StudentTracker) -> None:
    '''Print dashboard metrics to the console.'''
    stats = tracker.dashboard_metrics()
    heading("Dashboard")
    print(f"Total students: {stats['total_students']}")
    print(f"Average grade: {stats['average_grade']}")
    print(f"Average attendance: {stats['average_attendance']}")
    print(f"At risk count: {stats['at_risk_count']}")
    top_student = stats['top_student']
    if top_student is not None:
        print(f"Top student: {top_student.name}")


def export_csv_menu(tracker: StudentTracker) -> None:
    '''Export CSV and show the saved file path.'''
    path = tracker.export_csv()
    print(colour(f"Exported report to {path}", "success"))


def seed_demo_menu(tracker: StudentTracker) -> None:
    '''Insert demo data into an empty file.'''
    try:
        tracker.seed_demo_data()
        print(colour("Demo data inserted.", "success"))
    except TrackerError as exc:
        print(colour(str(exc), "danger"))


def main() -> None:
    '''Main loop for the console interface.'''
    tracker = StudentTracker()

    while True:
        heading(APP_NAME + " - Console")
        print("1. Add student")
        print("2. Update student")
        print("3. Add module")
        print("4. Add assessment")
        print("5. List students")
        print("6. Search students")
        print("7. Dashboard")
        print("8. Export CSV")
        print("9. Seed demo data")
        print("10. View one student")
        print("0. Exit")

        choice = safe_input("Choose an option: ").strip()

        if choice == "1":
            add_student_menu(tracker)
        elif choice == "2":
            update_student_menu(tracker)
        elif choice == "3":
            add_module_menu(tracker)
        elif choice == "4":
            add_assessment_menu(tracker)
        elif choice == "5":
            list_students(tracker)
        elif choice == "6":
            search_students(tracker)
        elif choice == "7":
            dashboard(tracker)
        elif choice == "8":
            export_csv_menu(tracker)
        elif choice == "9":
            seed_demo_menu(tracker)
        elif choice == "10":
            try:
                print_student(tracker, safe_input("Student ID: ").strip())
            except TrackerError as exc:
                print(colour(str(exc), "danger"))
        elif choice == "0":
            print(colour("Goodbye.", "info"))
            break
        else:
            print(colour("Invalid option. Try again.", "warning"))

        safe_input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
