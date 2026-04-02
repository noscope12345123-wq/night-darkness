from __future__ import annotations

'''
Manual smoke tests for Student Progress Tracker Pro.

This file checks valid cases, invalid cases, edge cases, CSV export,
searching, sorting, and a small Flask route smoke test.

References used in this file:
- assert statement: https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement
- pathlib.Path: https://docs.python.org/3/library/pathlib.html
- Flask test client basics: https://flask.palletsprojects.com/en/stable/testing/
'''

from pathlib import Path

from core import StudentTracker, TrackerError, ValidationError


def clean_test_files(*paths: Path) -> None:
    '''Delete test files left over from previous runs.'''
    for path in paths:
        if path.exists():
            path.unlink()


def run_core_tests() -> None:
    '''Run core tracker tests against isolated test files.'''
    data_file = Path("test_students_data.json")
    export_file = Path("test_student_report.csv")
    log_file = Path("test_tracker.log")

    clean_test_files(data_file, export_file, log_file)
    tracker = StudentTracker(data_file=data_file, export_file=export_file, log_file=log_file)

    print("TEST 1: add valid student")
    tracker.add_student("P100", "Alice", "alice@example.com", "IY499", 95, "Strong student")
    assert tracker.get_student("P100").name == "Alice"

    print("TEST 2: reject duplicate student ID")
    try:
        tracker.add_student("P100", "Bob", "bob@example.com", "IY499", 70, "Duplicate")
        raise AssertionError("Duplicate ID should have raised TrackerError")
    except TrackerError:
        print("Passed duplicate ID test")

    print("TEST 3: reject invalid email")
    try:
        tracker.add_student("P101", "Bob", "wrong-email", "IY499", 70, "Bad email")
        raise AssertionError("Invalid email should have raised ValidationError")
    except ValidationError:
        print("Passed invalid email test")

    print("TEST 4: add module and weighted assessments")
    tracker.add_module("P100", "Advanced Python", "Dr Stone")
    tracker.add_assessment("P100", "Advanced Python", "Coursework", 80, 60, "Good")
    tracker.add_assessment("P100", "Advanced Python", "Exam", 90, 40, "Very good")
    assert tracker.calculate_student_average(tracker.get_student("P100")) == 84.0

    print("TEST 5: reject assessment weights above 100 total")
    try:
        tracker.add_assessment("P100", "Advanced Python", "Bonus", 70, 10, "Too much weight")
        raise AssertionError("Weight overflow should have raised ValidationError")
    except ValidationError:
        print("Passed weight overflow test")

    print("TEST 6: search algorithm")
    results = tracker.search_students("alice")
    assert len(results) == 1

    print("TEST 7: sort algorithm")
    tracker.add_student("P102", "Zed", "zed@example.com", "IY499", 88, "")
    tracker.add_module("P102", "Advanced Python", "Dr Stone")
    tracker.add_assessment("P102", "Advanced Python", "Exam", 90, 100, "Excellent")
    sorted_students = tracker.sort_students("average")
    assert sorted_students[0].student_id == "P102"

    print("TEST 8: dashboard metrics")
    stats = tracker.dashboard_metrics()
    assert stats["total_students"] == 2
    assert "pass_rate" in stats

    print("TEST 9: export CSV")
    path = tracker.export_csv()
    assert path.exists()

    print("TEST 10: log file created")
    assert log_file.exists()

    print("Core tests completed successfully.")
    clean_test_files(data_file, export_file, log_file)


def run_flask_smoke_test() -> None:
    '''Run a minimal Flask route smoke test if Flask is installed.'''
    try:
        import flask_app
    except ModuleNotFoundError:
        print("Flask is not installed in this environment, so Flask smoke test was skipped.")
        return

    client = flask_app.app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    print("Flask smoke test completed successfully.")


if __name__ == "__main__":
    run_core_tests()
    run_flask_smoke_test()
    print("All tests completed successfully.")
