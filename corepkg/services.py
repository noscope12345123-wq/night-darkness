from __future__ import annotations

"""Main service layer for Student Progress Tracker Pro.

References:
- Regular expressions: https://docs.python.org/3/library/re.html
- Python tutorial on classes and methods: https://docs.python.org/3/tutorial/classes.html
- Built-in sorted()/enumerate()/len(): https://docs.python.org/3/library/functions.html
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .analytics import (
    PASS_MARK,
    calculate_module_average,
    calculate_risk_score,
    calculate_student_average,
    calculate_trend,
    generate_recommendation,
    get_grade_band,
    get_progress_status,
)
from .errors import TrackerError, ValidationError
from .models import Assessment, ModuleRecord, Student, DATE_FORMAT
from .storage import export_students_csv, load_students, log_action, now_string, save_students

APP_NAME = 'Student Progress Tracker Pro Ultra'
COURSE_CODE = 'IY499'
DEFAULT_DATA_FILE = Path('students_data.json')
DEFAULT_EXPORT_FILE = Path('student_report.csv')
DEFAULT_LOG_FILE = Path('tracker.log')


class StudentTracker:
    """Shared business logic for console, Tkinter, and Flask interfaces."""

    def __init__(self, data_file: Path = DEFAULT_DATA_FILE, export_file: Path = DEFAULT_EXPORT_FILE, log_file: Path = DEFAULT_LOG_FILE) -> None:
        self.data_file = Path(data_file)
        self.export_file = Path(export_file)
        self.log_file = Path(log_file)
        self.students: Dict[str, Student] = load_students(self.data_file, self.log_file)

    def save(self) -> None:
        """Persist all current students to disk."""
        save_students(self.students, self.data_file, self.log_file)

    def log(self, message: str) -> None:
        """Write a log message."""
        log_action(self.log_file, message)

    def touch_student(self, student: Student) -> None:
        """Update a student's modified timestamp after changes."""
        student.updated_at = now_string()

    def validate_student_id(self, student_id: str) -> str:
        """Validate a student identifier using re.fullmatch()."""
        clean = student_id.strip()
        if not re.fullmatch(r'[A-Za-z0-9_-]{3,20}', clean):
            raise ValidationError('Student ID must be 3-20 characters and contain only letters, numbers, _ or -.')
        return clean

    def validate_name(self, name: str) -> str:
        """Validate non-empty names."""
        clean = name.strip()
        if not clean:
            raise ValidationError('Name cannot be empty.')
        return clean

    def validate_email(self, email: str) -> str:
        """Validate email text using a simple coursework regex."""
        clean = email.strip()
        if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', clean):
            raise ValidationError('Please enter a valid email address.')
        return clean

    def validate_course(self, course: str) -> str:
        """Validate non-empty course text."""
        clean = course.strip()
        if not clean:
            raise ValidationError('Course cannot be empty.')
        return clean

    def validate_percentage(self, value: float, field_name: str) -> float:
        """Validate values such as attendance, score, and weight."""
        number = float(value)
        if number < 0 or number > 100:
            raise ValidationError(f'{field_name} must be between 0 and 100.')
        return round(number, 2)

    def get_student(self, student_id: str) -> Student:
        """Return a student by ID or raise TrackerError."""
        try:
            return self.students[student_id]
        except KeyError as exc:
            raise TrackerError(f'Student {student_id} was not found.') from exc

    def add_student(self, student_id: str, name: str, email: str, course: str, attendance: float = 100.0, notes: str = '') -> Student:
        """Create and store a validated student profile."""
        student_id = self.validate_student_id(student_id)
        if student_id in self.students:
            raise TrackerError('Student ID already exists.')
        student = Student(
            student_id=student_id,
            name=self.validate_name(name),
            email=self.validate_email(email),
            course=self.validate_course(course),
            attendance=self.validate_percentage(attendance, 'Attendance'),
            notes=notes.strip(),
        )
        self.students[student.student_id] = student
        self.save()
        self.log(f'Added student {student.student_id}')
        return student

    def update_student(self, student_id: str, name: str, email: str, course: str, attendance: float, notes: str) -> Student:
        """Update an existing student profile."""
        student = self.get_student(student_id)
        student.name = self.validate_name(name)
        student.email = self.validate_email(email)
        student.course = self.validate_course(course)
        student.attendance = self.validate_percentage(attendance, 'Attendance')
        student.notes = notes.strip()
        self.touch_student(student)
        self.save()
        self.log(f'Updated student {student_id}')
        return student

    def delete_student(self, student_id: str) -> None:
        """Delete a student from storage."""
        if student_id not in self.students:
            raise TrackerError(f'Student {student_id} was not found.')
        del self.students[student_id]
        self.save()
        self.log(f'Deleted student {student_id}')

    def add_module(self, student_id: str, module_name: str, lecturer: str = '') -> ModuleRecord:
        """Attach a module to a student record."""
        student = self.get_student(student_id)
        module_key = module_name.strip()
        if not module_key:
            raise ValidationError('Module name cannot be empty.')
        if module_key in student.modules:
            raise TrackerError('This module already exists for the student.')
        module = ModuleRecord(module_name=module_key, lecturer=lecturer.strip())
        student.modules[module_key] = module
        self.touch_student(student)
        self.save()
        self.log(f'Added module {module_key} to {student_id}')
        return module

    def add_assessment(self, student_id: str, module_name: str, assessment_name: str, score: float, weight: float, feedback: str = '') -> Assessment:
        """Add a weighted assessment and protect total weight from exceeding 100."""
        student = self.get_student(student_id)
        module_key = module_name.strip()
        if module_key not in student.modules:
            raise TrackerError('Module not found for this student.')
        clean_name = assessment_name.strip()
        if not clean_name:
            raise ValidationError('Assessment name cannot be empty.')
        score = self.validate_percentage(score, 'Score')
        weight = self.validate_percentage(weight, 'Weight')
        module = student.modules[module_key]
        used_weight = sum(item.weight for item in module.assessments)
        if used_weight + weight > 100:
            raise ValidationError(f'Total assessment weight would exceed 100. Current total: {used_weight}')
        assessment = Assessment(name=clean_name, score=score, weight=weight, feedback=feedback.strip())
        module.assessments.append(assessment)
        self.touch_student(student)
        self.save()
        self.log(f'Added assessment {clean_name} to {student_id}/{module_key}')
        return assessment

    def linear_search_students(self, keyword: str) -> List[Student]:
        """Explicit linear search algorithm used for coursework evidence."""
        text = keyword.lower().strip()
        results: List[Student] = []
        for student in self.students.values():
            blob = ' '.join([
                student.student_id,
                student.name,
                student.email,
                student.course,
                student.notes,
                get_progress_status(student),
                calculate_trend(student),
                generate_recommendation(student),
            ]).lower()
            module_blob = ' '.join(module.module_name.lower() for module in student.modules.values())
            if text in blob or text in module_blob:
                results.append(student)
        return results

    def search_students(self, keyword: str) -> List[Student]:
        """Public wrapper around the explicit linear search method."""
        if not keyword.strip():
            return list(self.students.values())
        return self.linear_search_students(keyword)

    def bubble_sort_students(self, students: List[Student], sort_by: str = 'name', reverse: bool = False) -> List[Student]:
        """Explicit bubble sort used to satisfy coursework sorting requirements."""
        items = students[:]

        def key(student: Student):
            if sort_by == 'id':
                return student.student_id.lower()
            if sort_by == 'average':
                avg = calculate_student_average(student)
                return avg if avg is not None else -1
            if sort_by == 'attendance':
                return student.attendance
            if sort_by == 'risk':
                return calculate_risk_score(student)
            return student.name.lower()

        n = len(items)
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                left = key(items[j])
                right = key(items[j + 1])
                condition = left < right if reverse else left > right
                if condition:
                    items[j], items[j + 1] = items[j + 1], items[j]
                    swapped = True
            if not swapped:
                break
        return items

    def sort_students(self, sort_by: str = 'name') -> List[Student]:
        """Return sorted students using the explicit bubble sort algorithm."""
        reverse = sort_by in {'average', 'attendance', 'risk'}
        return self.bubble_sort_students(list(self.students.values()), sort_by=sort_by, reverse=reverse)

    def calculate_module_average(self, module: ModuleRecord) -> Optional[float]:
        return calculate_module_average(module)

    def calculate_student_average(self, student: Student) -> Optional[float]:
        return calculate_student_average(student)

    def get_grade_band(self, score: float) -> str:
        return get_grade_band(score)

    def get_progress_status(self, student: Student) -> str:
        return get_progress_status(student)

    def calculate_trend(self, student: Student) -> str:
        return calculate_trend(student)

    def calculate_risk_score(self, student: Student) -> int:
        return calculate_risk_score(student)

    def generate_recommendation(self, student: Student) -> str:
        return generate_recommendation(student)

    def identify_at_risk_students(self) -> List[Tuple[str, str, float, float, int]]:
        """Return students who need support, ordered by greatest risk first."""
        rows: List[Tuple[str, str, float, float, int]] = []
        for student in self.students.values():
            average = self.calculate_student_average(student)
            risk = self.calculate_risk_score(student)
            if average is None or average < PASS_MARK or student.attendance < 70 or risk >= 50:
                rows.append((student.student_id, student.name, average if average is not None else -1.0, student.attendance, risk))
        rows.sort(key=lambda row: (row[4], -row[2], -row[3]), reverse=True)
        return rows

    def find_top_student(self) -> Optional[Student]:
        """Return the highest-performing student with valid grade data."""
        graded = [student for student in self.students.values() if self.calculate_student_average(student) is not None]
        if not graded:
            return None
        return max(graded, key=lambda student: self.calculate_student_average(student) or -1)

    def dashboard_metrics(self) -> Dict[str, object]:
        """Compute dashboard KPIs for GUI and web views."""
        total = len(self.students)
        averages = [self.calculate_student_average(student) for student in self.students.values()]
        valid_averages = [avg for avg in averages if avg is not None]
        at_risk = self.identify_at_risk_students()
        pass_count = sum(1 for avg in valid_averages if avg >= PASS_MARK)
        pass_rate = round((pass_count / len(valid_averages)) * 100, 2) if valid_averages else 0.0
        top_student = self.find_top_student()
        strongest_module = self.find_strongest_module_name()
        return {
            'total_students': total,
            'graded_students': len(valid_averages),
            'overall_average': round(sum(valid_averages) / len(valid_averages), 2) if valid_averages else None,
            'pass_rate': pass_rate,
            'at_risk_count': len(at_risk),
            'top_student_name': top_student.name if top_student else 'N/A',
            'top_student_average': self.calculate_student_average(top_student) if top_student else None,
            'strongest_module': strongest_module or 'N/A',
        }

    def find_strongest_module_name(self) -> Optional[str]:
        """Find the module name with the highest average across students."""
        buckets: Dict[str, List[float]] = {}
        for student in self.students.values():
            for name, module in student.modules.items():
                avg = self.calculate_module_average(module)
                if avg is not None:
                    buckets.setdefault(name, []).append(avg)
        if not buckets:
            return None
        return max(buckets, key=lambda name: sum(buckets[name]) / len(buckets[name]))

    def export_csv(self) -> Path:
        """Export a flattened report to CSV."""
        def build_row(student: Student):
            average = self.calculate_student_average(student)
            return [
                student.student_id,
                student.name,
                student.email,
                student.course,
                student.attendance,
                average if average is not None else 'N/A',
                self.get_grade_band(average) if average is not None else 'N/A',
                self.get_progress_status(student),
                self.calculate_risk_score(student),
                self.calculate_trend(student),
                self.generate_recommendation(student),
                ', '.join(student.modules.keys()),
                student.notes,
                student.updated_at,
            ]
        return export_students_csv(self.students, self.export_file, self.log_file, build_row)

    def seed_demo_data(self) -> None:
        """Insert a strong demo dataset into an empty tracker."""
        if self.students:
            raise TrackerError('Seed demo data only on an empty tracker.')
        self.add_student('P476432', 'Night', 'night@example.com', COURSE_CODE, 92, 'High ambition student profile.')
        self.add_module('P476432', 'Advanced Python', 'Dr Ada')
        self.add_assessment('P476432', 'Advanced Python', 'Coursework', 88, 40, 'Excellent logic.')
        self.add_assessment('P476432', 'Advanced Python', 'Exam', 91, 60, 'Strong final performance.')

        self.add_student('P400100', 'Ava Stone', 'ava@example.com', COURSE_CODE, 78, 'Needs extra revision for exams.')
        self.add_module('P400100', 'Data Analytics', 'Dr Turing')
        self.add_assessment('P400100', 'Data Analytics', 'Report', 62, 50, 'Solid work.')
        self.add_assessment('P400100', 'Data Analytics', 'Exam', 55, 50, 'Could improve time management.')

        self.add_student('P400200', 'Leo Quinn', 'leo@example.com', COURSE_CODE, 58, 'Attendance risk.')
        self.add_module('P400200', 'Software Design', 'Dr Hopper')
        self.add_assessment('P400200', 'Software Design', 'Prototype', 46, 50, 'Basic requirements met.')
        self.add_assessment('P400200', 'Software Design', 'Exam', 34, 50, 'Urgent support required.')

    def summary_for_student(self, student: Student) -> Dict[str, object]:
        """Prepare enriched student details for the GUI and web interfaces."""
        average = self.calculate_student_average(student)
        return {
            'student': student,
            'average': average,
            'grade_band': self.get_grade_band(average) if average is not None else 'N/A',
            'status': self.get_progress_status(student),
            'risk': self.calculate_risk_score(student),
            'trend': self.calculate_trend(student),
            'recommendation': self.generate_recommendation(student),
        }
