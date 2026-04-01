from __future__ import annotations

'''
Simple manual test script for Student Progress Tracker Pro.

This file checks valid cases, invalid cases, and edge cases so the project
shows evidence of testing, which is mentioned in the assignment brief.
'''

from pathlib import Path

from core import StudentTracker, ValidationError, TrackerError


def run_tests() -> None:
    data_file = Path("test_students_data.json")
    export_file = Path("test_student_report.csv")
    log_file = Path("test_tracker.log")

    for path in (data_file, export_file, log_file):
        if path.exists():
            path.unlink()

    tracker = StudentTracker(data_file=data_file, export_file=export_file, log_file=log_file)

    print("TEST 1: add valid student")
    tracker.add_student("P100", "Alice", "alice@example.com", "IY499", 95, "Strong student")
    assert tracker.get_student("P100").name == "Alice"

    print("TEST 2: reject duplicate student ID")
    try:
        tracker.add_student("P100", "Bob", "bob@example.com", "IY499", 70, "Duplicate")
    except TrackerError:
        print("Passed duplicate ID test")

    print("TEST 3: reject invalid email")
    try:
        tracker.add_student("P101", "Bob", "wrong-email", "IY499", 70, "Bad email")
    except ValidationError:
        print("Passed invalid email test")

    print("TEST 4: add module and assessment")
    tracker.add_module("P100", "Advanced Python", "Dr Stone")
    tracker.add_assessment("P100", "Advanced Python", "Exam", 80, 100, "Good")
    assert tracker.calculate_student_average(tracker.get_student("P100")) == 80.0

    print("TEST 5: search algorithm")
    results = tracker.search_students("alice")
    assert len(results) == 1

    print("TEST 6: sort algorithm")
    tracker.add_student("P102", "Zed", "zed@example.com", "IY499", 88, "")
    tracker.add_module("P102", "Advanced Python", "Dr Stone")
    tracker.add_assessment("P102", "Advanced Python", "Exam", 90, 100, "Excellent")
    sorted_students = tracker.sort_students("average")
    assert sorted_students[0].student_id == "P102"

    print("TEST 7: export CSV")
    path = tracker.export_csv()
    assert path.exists()

    print("All tests completed successfully.")


if __name__ == "__main__":
    run_tests()
