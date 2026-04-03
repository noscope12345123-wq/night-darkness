from __future__ import annotations

"""Test scenarios for Student Progress Tracker Pro Ultra.

References:
- assert statement: https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement
- pathlib: https://docs.python.org/3/library/pathlib.html
- Flask testing: https://flask.palletsprojects.com/en/stable/testing/
"""

from pathlib import Path

from corepkg import StudentTracker, TrackerError, ValidationError


def clean(*paths: Path) -> None:
    for path in paths:
        if path.exists():
            path.unlink()
    backup_dir = Path('backups')
    if backup_dir.exists() and backup_dir.is_dir():
        for item in backup_dir.glob('*'):
            item.unlink()
        backup_dir.rmdir()


def run_core_tests() -> None:
    data_file = Path('test_students_data.json')
    export_file = Path('test_student_report.csv')
    log_file = Path('test_tracker.log')
    clean(data_file, export_file, log_file)

    tracker = StudentTracker(data_file=data_file, export_file=export_file, log_file=log_file)

    print('TEST 1: add valid student')
    tracker.add_student('P100', 'Alice', 'alice@example.com', 'IY499', 95, 'Strong student')
    assert tracker.get_student('P100').name == 'Alice'

    print('TEST 2: duplicate student rejection')
    try:
        tracker.add_student('P100', 'Bob', 'bob@example.com', 'IY499', 80, '')
        raise AssertionError('Expected duplicate ID rejection.')
    except TrackerError:
        pass

    print('TEST 3: invalid email rejection')
    try:
        tracker.add_student('P101', 'Bad Email', 'wrong-email', 'IY499', 80, '')
        raise AssertionError('Expected invalid email rejection.')
    except ValidationError:
        pass

    print('TEST 4: module and weighted assessment average')
    tracker.add_module('P100', 'Advanced Python', 'Dr Ada')
    tracker.add_assessment('P100', 'Advanced Python', 'CW', 80, 60, 'Good')
    tracker.add_assessment('P100', 'Advanced Python', 'Exam', 90, 40, 'Very good')
    assert tracker.calculate_student_average(tracker.get_student('P100')) == 84.0

    print('TEST 5: weight overflow rejection')
    try:
        tracker.add_assessment('P100', 'Advanced Python', 'Bonus', 50, 10, 'Too much')
        raise AssertionError('Expected weight overflow rejection.')
    except ValidationError:
        pass

    print('TEST 6: trend and risk analytics')
    student = tracker.get_student('P100')
    assert tracker.calculate_trend(student) == 'Improving'
    assert isinstance(tracker.calculate_risk_score(student), int)

    print('TEST 7: linear search')
    assert len(tracker.search_students('alice')) == 1
    assert len(tracker.search_students('Advanced Python')) == 1

    print('TEST 8: bubble sort')
    tracker.add_student('P102', 'Zed', 'zed@example.com', 'IY499', 55, 'Needs help')
    tracker.add_module('P102', 'Advanced Python', 'Dr Ada')
    tracker.add_assessment('P102', 'Advanced Python', 'Exam', 30, 100, 'Weak')
    sorted_by_average = tracker.sort_students('average')
    assert sorted_by_average[0].student_id == 'P100'

    print('TEST 9: dashboard metrics and at-risk list')
    stats = tracker.dashboard_metrics()
    assert stats['total_students'] == 2
    assert 'pass_rate' in stats
    assert len(tracker.identify_at_risk_students()) >= 1

    print('TEST 10: CSV export and log creation')
    csv_path = tracker.export_csv()
    assert csv_path.exists()
    assert log_file.exists()

    print('TEST 11: persistence reload')
    tracker_reloaded = StudentTracker(data_file=data_file, export_file=export_file, log_file=log_file)
    assert tracker_reloaded.get_student('P100').name == 'Alice'

    print('TEST 12: backup created on overwrite save')
    tracker_reloaded.update_student('P100', 'Alice', 'alice@example.com', 'IY499', 96, 'Updated')
    backup_dir = Path('backups')
    assert backup_dir.exists()
    assert any(backup_dir.iterdir())

    print('Core tests completed successfully.')
    clean(data_file, export_file, log_file)


def run_flask_smoke_test() -> None:
    try:
        import flask_app
    except ModuleNotFoundError:
        print('Flask is not installed in this environment, so Flask smoke test was skipped.')
        return
    client = flask_app.app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    print('Flask smoke test completed successfully.')


if __name__ == '__main__':
    run_core_tests()
    run_flask_smoke_test()
    print('All tests completed successfully.')
