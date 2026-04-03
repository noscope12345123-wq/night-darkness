from __future__ import annotations

"""Persistence helpers for JSON, CSV, backups, and logging.

References:
- json: https://docs.python.org/3/library/json.html
- csv: https://docs.python.org/3/library/csv.html
- pathlib: https://docs.python.org/3/library/pathlib.html
- built-in open(): https://docs.python.org/3/library/functions.html#open
- shutil.copy2(): https://docs.python.org/3/library/shutil.html
"""

import csv
import json
import shutil
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .models import Assessment, ModuleRecord, Student, DATE_FORMAT


def now_string() -> str:
    """Return a formatted current timestamp."""
    return datetime.now().strftime(DATE_FORMAT)


def log_action(log_file: Path, message: str) -> None:
    """Append a timestamped line to the log file."""
    with open(log_file, 'a', encoding='utf-8') as file:
        file.write(f"[{now_string()}] {message}\n")


def backup_file_if_exists(file_path: Path, log_file: Path) -> None:
    """Create a timestamped backup before overwriting existing storage."""
    if not file_path.exists():
        return
    backup_dir = file_path.parent / 'backups'
    backup_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f"{file_path.stem}_{stamp}{file_path.suffix}"
    shutil.copy2(file_path, backup_path)
    log_action(log_file, f"Backup created: {backup_path}")


def load_students(data_file: Path, log_file: Path) -> Dict[str, Student]:
    """Load tracker data from JSON; return an empty dict on failure."""
    if not data_file.exists():
        return {}
    try:
        with open(data_file, 'r', encoding='utf-8') as file:
            raw_data = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        log_action(log_file, f"Data load failed: {exc}")
        return {}

    students: Dict[str, Student] = {}
    for student_id, student_data in raw_data.items():
        modules: Dict[str, ModuleRecord] = {}
        for module_key, module_data in student_data.get('modules', {}).items():
            assessments = [Assessment(**item) for item in module_data.get('assessments', [])]
            modules[module_key] = ModuleRecord(
                module_name=module_data.get('module_name', module_key),
                lecturer=module_data.get('lecturer', ''),
                assessments=assessments,
            )
        students[student_id] = Student(
            student_id=student_data['student_id'],
            name=student_data['name'],
            email=student_data['email'],
            course=student_data['course'],
            attendance=float(student_data.get('attendance', 100.0)),
            notes=student_data.get('notes', ''),
            modules=modules,
            created_at=student_data.get('created_at', now_string()),
            updated_at=student_data.get('updated_at', now_string()),
        )
    return students


def save_students(students: Dict[str, Student], data_file: Path, log_file: Path) -> None:
    """Persist tracker data to JSON and create a backup when replacing old data."""
    data_file.parent.mkdir(parents=True, exist_ok=True)
    if data_file.exists():
        backup_file_if_exists(data_file, log_file)
    serialisable: Dict[str, Any] = {student_id: asdict(student) for student_id, student in students.items()}
    with open(data_file, 'w', encoding='utf-8') as file:
        json.dump(serialisable, file, indent=4)
    log_action(log_file, f"Saved {len(students)} students to {data_file}")


def export_students_csv(students: Dict[str, Student], export_file: Path, log_file: Path, enrich_row) -> Path:
    """Export a flattened CSV report for all students."""
    export_file.parent.mkdir(parents=True, exist_ok=True)
    with open(export_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'Student ID', 'Name', 'Email', 'Course', 'Attendance', 'Average', 'Grade Band',
            'Status', 'Risk Score', 'Trend', 'Recommendation', 'Modules', 'Notes', 'Updated At'
        ])
        for student in students.values():
            writer.writerow(enrich_row(student))
    log_action(log_file, f"Exported CSV report to {export_file}")
    return export_file
