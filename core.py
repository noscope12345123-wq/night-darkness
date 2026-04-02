from __future__ import annotations

'''
Shared core logic for Student Progress Tracker Pro.

This file intentionally contains the main business logic so the console,
Tkinter, and Flask versions all reuse the same code.

References used in this file:
- dataclasses: https://docs.python.org/3/library/dataclasses.html
- json: https://docs.python.org/3/library/json.html
- csv: https://docs.python.org/3/library/csv.html
- datetime: https://docs.python.org/3/library/datetime.html
- pathlib: https://docs.python.org/3/library/pathlib.html
- statistics.mean: https://docs.python.org/3/library/statistics.html
- regular expressions: https://docs.python.org/3/library/re.html
- exceptions tutorial: https://docs.python.org/3/tutorial/errors.html
- typing: https://docs.python.org/3/library/typing.html
- built-in open(): https://docs.python.org/3/library/functions.html#open

Important note for marking:
- API/library usage is cited where relevant.
- The business logic, validation rules, analytics, search flow, and tracker
  structure are original work written for this project.
'''

# csv is used for report exporting.
# Reference: https://docs.python.org/3/library/csv.html
import csv

# json is used for persistent file storage.
# Reference: https://docs.python.org/3/library/json.html
import json

# re is used for input validation patterns.
# Reference: https://docs.python.org/3/library/re.html
import re

# dataclass helpers are used to model Student / Module / Assessment objects.
# Reference: https://docs.python.org/3/library/dataclasses.html
from dataclasses import asdict, dataclass, field

# datetime.now() and strftime() are used for timestamps and logs.
# Reference: https://docs.python.org/3/library/datetime.html
from datetime import datetime

# Path is used to manage file paths more safely than raw strings.
# Reference: https://docs.python.org/3/library/pathlib.html
from pathlib import Path

# mean is used for analytics such as overall student averages.
# Reference: https://docs.python.org/3/library/statistics.html
from statistics import mean

# Typing hints improve readability and code quality.
# Reference: https://docs.python.org/3/library/typing.html
from typing import Any, Dict, List, Optional, Tuple

APP_NAME = "Student Progress Tracker Pro"
COURSE_CODE = "IY499"
DEFAULT_DATA_FILE = Path("students_data.json")
DEFAULT_EXPORT_FILE = Path("student_report.csv")
DEFAULT_LOG_FILE = Path("tracker.log")
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
PASS_MARK = 40.0


class ValidationError(Exception):
    '''Raised when user input is invalid.

    Custom exceptions are part of Python error handling.
    Reference: https://docs.python.org/3/tutorial/errors.html
    '''


class TrackerError(Exception):
    '''Raised for tracker workflow problems such as duplicates or missing items.'''


@dataclass
class Assessment:
    '''Represents a single weighted assessment item.'''

    name: str
    score: float
    weight: float
    feedback: str = ""


@dataclass
class ModuleRecord:
    '''Represents one module containing many assessments.'''

    module_name: str
    lecturer: str = ""
    assessments: List[Assessment] = field(default_factory=list)


@dataclass
class Student:
    '''Represents one student profile stored by the tracker.'''

    student_id: str
    name: str
    email: str
    course: str
    attendance: float = 100.0
    notes: str = ""
    modules: Dict[str, ModuleRecord] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().strftime(DATE_FORMAT))
    updated_at: str = field(default_factory=lambda: datetime.now().strftime(DATE_FORMAT))


class StudentTracker:
    '''Main engine used by the console, Tkinter, and Flask interfaces.

    The goal of this class is to keep the user-interface files smaller by
    centralising validation, file handling, analytics, searching, sorting,
    reporting, and status logic in one place.
    '''

    def __init__(
        self,
        data_file: Path = DEFAULT_DATA_FILE,
        export_file: Path = DEFAULT_EXPORT_FILE,
        log_file: Path = DEFAULT_LOG_FILE,
    ) -> None:
        self.data_file = Path(data_file)
        self.export_file = Path(export_file)
        self.log_file = Path(log_file)
        self.students: Dict[str, Student] = self.load_data()

    def now_string(self) -> str:
        '''Return the current date and time as a string.

        datetime.now() and strftime() reference:
        https://docs.python.org/3/library/datetime.html
        '''
        return datetime.now().strftime(DATE_FORMAT)

    def log_action(self, message: str) -> None:
        '''Append a timestamped line to the log file.

        File handling methods used:
        - open(): https://docs.python.org/3/library/functions.html#open
        - write(): file object method in Python I/O docs
          https://docs.python.org/3/tutorial/inputoutput.html
        '''
        timestamp = self.now_string()
        with open(self.log_file, "a", encoding="utf-8") as file:
            file.write(f"[{timestamp}] {message}\n")

    def touch_student(self, student: Student) -> None:
        '''Update the last-modified timestamp after changes.''' 
        student.updated_at = self.now_string()

    def validate_student_id(self, student_id: str) -> str:
        '''Validate a student ID with a regular expression.

        re.fullmatch() reference:
        https://docs.python.org/3/library/re.html
        '''
        clean_value = student_id.strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]{3,20}", clean_value):
            raise ValidationError(
                "Student ID must be 3-20 characters and contain only letters, numbers, _ or -."
            )
        return clean_value

    def validate_name(self, name: str) -> str:
        '''Validate that the name is not empty.''' 
        clean_value = name.strip()
        if not clean_value:
            raise ValidationError("Name cannot be empty.")
        return clean_value

    def validate_email(self, email: str) -> str:
        '''Validate a simple email format with a regex.

        The pattern is intentionally simple for coursework-level validation.
        Reference: https://docs.python.org/3/library/re.html
        '''
        clean_value = email.strip()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", clean_value):
            raise ValidationError("Please enter a valid email address.")
        return clean_value

    def validate_course(self, course: str) -> str:
        '''Validate that the course field is not empty.''' 
        clean_value = course.strip()
        if not clean_value:
            raise ValidationError("Course cannot be empty.")
        return clean_value

    def validate_attendance(self, attendance: float) -> float:
        '''Validate attendance as a 0-100 value.''' 
        value = float(attendance)
        if value < 0 or value > 100:
            raise ValidationError("Attendance must be between 0 and 100.")
        return round(value, 2)

    def validate_score_or_weight(self, value: float, field_name: str) -> float:
        '''Validate score or weight as a 0-100 value.''' 
        clean_value = float(value)
        if clean_value < 0 or clean_value > 100:
            raise ValidationError(f"{field_name} must be between 0 and 100.")
        return round(clean_value, 2)

    def load_data(self) -> Dict[str, Student]:
        '''Load students from JSON storage.

        References:
        - open(): https://docs.python.org/3/library/functions.html#open
        - json.load(): https://docs.python.org/3/library/json.html
        - try/except: https://docs.python.org/3/tutorial/errors.html
        '''
        if not self.data_file.exists():
            return {}

        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                raw_data = json.load(file)
        except (OSError, json.JSONDecodeError) as exc:
            self.log_action(f"Could not load data file: {exc}")
            return {}

        students: Dict[str, Student] = {}
        for student_id, student_data in raw_data.items():
            modules: Dict[str, ModuleRecord] = {}
            for module_key, module_data in student_data.get("modules", {}).items():
                assessments: List[Assessment] = []
                for item in module_data.get("assessments", []):
                    assessments.append(Assessment(**item))
                modules[module_key] = ModuleRecord(
                    module_name=module_data.get("module_name", module_key),
                    lecturer=module_data.get("lecturer", ""),
                    assessments=assessments,
                )
            students[student_id] = Student(
                student_id=student_data["student_id"],
                name=student_data["name"],
                email=student_data["email"],
                course=student_data["course"],
                attendance=float(student_data.get("attendance", 100.0)),
                notes=student_data.get("notes", ""),
                modules=modules,
                created_at=student_data.get("created_at", self.now_string()),
                updated_at=student_data.get("updated_at", self.now_string()),
            )
        return students

    def save_data(self) -> None:
        '''Save the in-memory student dictionary to JSON.

        References:
        - asdict(): https://docs.python.org/3/library/dataclasses.html
        - json.dump(): https://docs.python.org/3/library/json.html
        '''
        serialisable: Dict[str, Any] = {}
        for student_id, student in self.students.items():
            serialisable[student_id] = asdict(student)

        with open(self.data_file, "w", encoding="utf-8") as file:
            json.dump(serialisable, file, indent=4)

        self.log_action(f"Saved {len(self.students)} students to JSON.")

    def get_student(self, student_id: str) -> Student:
        '''Return a student object or raise a tracker error.''' 
        if student_id not in self.students:
            raise TrackerError(f"Student '{student_id}' was not found.")
        return self.students[student_id]

    def add_student(
        self,
        student_id: str,
        name: str,
        email: str,
        course: str,
        attendance: float = 100.0,
        notes: str = "",
    ) -> Student:
        '''Create a new student profile after validation.''' 
        clean_student_id = self.validate_student_id(student_id)
        clean_name = self.validate_name(name)
        clean_email = self.validate_email(email)
        clean_course = self.validate_course(course)
        clean_attendance = self.validate_attendance(attendance)

        if clean_student_id in self.students:
            raise TrackerError(f"Student ID '{clean_student_id}' already exists.")

        student = Student(
            student_id=clean_student_id,
            name=clean_name,
            email=clean_email,
            course=clean_course,
            attendance=clean_attendance,
            notes=notes.strip(),
        )
        self.students[clean_student_id] = student
        self.save_data()
        self.log_action(f"Added student {clean_student_id} - {clean_name}.")
        return student

    def update_student(
        self,
        student_id: str,
        name: str,
        email: str,
        course: str,
        attendance: float,
        notes: str,
    ) -> Student:
        '''Update an existing student profile.''' 
        student = self.get_student(student_id)
        student.name = self.validate_name(name)
        student.email = self.validate_email(email)
        student.course = self.validate_course(course)
        student.attendance = self.validate_attendance(attendance)
        student.notes = notes.strip()
        self.touch_student(student)
        self.save_data()
        self.log_action(f"Updated student {student_id}.")
        return student

    def delete_student(self, student_id: str) -> None:
        '''Delete one student from the tracker.''' 
        student = self.get_student(student_id)
        del self.students[student.student_id]
        self.save_data()
        self.log_action(f"Deleted student {student.student_id}.")

    def add_module(self, student_id: str, module_name: str, lecturer: str = "") -> ModuleRecord:
        '''Add a module to a chosen student.''' 
        student = self.get_student(student_id)
        clean_module_name = module_name.strip()
        if not clean_module_name:
            raise ValidationError("Module name cannot be empty.")
        key = clean_module_name.lower()
        if key in student.modules:
            raise TrackerError("This module already exists for the selected student.")
        module = ModuleRecord(module_name=clean_module_name, lecturer=lecturer.strip())
        student.modules[key] = module
        self.touch_student(student)
        self.save_data()
        self.log_action(f"Added module {clean_module_name} to {student_id}.")
        return module

    def get_module(self, student: Student, module_name: str) -> ModuleRecord:
        '''Return a module by name from a student profile.''' 
        key = module_name.strip().lower()
        if key not in student.modules:
            raise TrackerError(f"Module '{module_name}' was not found for {student.name}.")
        return student.modules[key]

    def current_module_weight(self, module: ModuleRecord) -> float:
        '''Return the current total weight inside a module.

        sum() reference: https://docs.python.org/3/library/functions.html#sum
        '''
        return round(sum(item.weight for item in module.assessments), 2)

    def add_assessment(
        self,
        student_id: str,
        module_name: str,
        assessment_name: str,
        score: float,
        weight: float,
        feedback: str = "",
    ) -> Assessment:
        '''Add a weighted assessment to a module.

        Extra robustness: this method prevents total module weight from
        exceeding 100 because assessment weighting above 100 would usually be
        invalid in a grading system.
        '''
        student = self.get_student(student_id)
        module = self.get_module(student, module_name)
        clean_name = assessment_name.strip()
        if not clean_name:
            raise ValidationError("Assessment name cannot be empty.")

        clean_score = self.validate_score_or_weight(score, "Score")
        clean_weight = self.validate_score_or_weight(weight, "Weight")
        new_total_weight = self.current_module_weight(module) + clean_weight
        if new_total_weight > 100:
            raise ValidationError(
                f"Total module weight cannot exceed 100. Current total is {self.current_module_weight(module)}."
            )

        assessment = Assessment(
            name=clean_name,
            score=clean_score,
            weight=clean_weight,
            feedback=feedback.strip(),
        )
        module.assessments.append(assessment)
        self.touch_student(student)
        self.save_data()
        self.log_action(f"Added assessment {clean_name} to {student_id}/{module.module_name}.")
        return assessment

    def calculate_module_average(self, module: ModuleRecord) -> Optional[float]:
        '''Calculate the weighted average for a single module.''' 
        if not module.assessments:
            return None

        total_weight = 0.0
        weighted_total = 0.0
        for assessment in module.assessments:
            total_weight += assessment.weight
            weighted_total += assessment.score * assessment.weight

        if total_weight == 0:
            return None

        return round(weighted_total / total_weight, 2)

    def calculate_student_average(self, student: Student) -> Optional[float]:
        '''Calculate the mean of all module averages for one student.''' 
        module_averages: List[float] = []
        for module in student.modules.values():
            module_average = self.calculate_module_average(module)
            if module_average is not None:
                module_averages.append(module_average)

        if not module_averages:
            return None

        return round(mean(module_averages), 2)

    def get_grade_band(self, score: float) -> str:
        '''Convert a numeric score into a simple grade band.''' 
        if score >= 70:
            return "First / Distinction"
        if score >= 60:
            return "Upper Second / Merit"
        if score >= 50:
            return "Lower Second / Pass+"
        if score >= PASS_MARK:
            return "Third / Pass"
        return "Fail"

    def get_progress_status(self, student: Student) -> str:
        '''Return an overall academic status label.''' 
        average = self.calculate_student_average(student)
        if average is None:
            return "Insufficient data"
        if average < PASS_MARK or student.attendance < 50:
            return "Critical risk"
        if average < 50 or student.attendance < 70:
            return "Needs support"
        if average >= 70 and student.attendance >= 85:
            return "Excellent"
        return "Stable"

    def get_recommendation(self, student: Student) -> str:
        '''Return a recommendation string derived from status.''' 
        status = self.get_progress_status(student)
        if status == "Critical risk":
            return "Urgent tutor intervention and attendance review are recommended."
        if status == "Needs support":
            return "Target weak modules and improve attendance consistency."
        if status == "Excellent":
            return "Maintain strong performance and consider advanced stretch work."
        if status == "Stable":
            return "Keep revision habits consistent and monitor progress regularly."
        return "Add grades and modules to unlock analytics."

    def linear_search_students(self, keyword: str) -> List[Student]:
        '''Explicit linear search algorithm.

        The assignment asks for a search algorithm. This implementation checks
        each student one by one and matches against a combined searchable text.

        References for string operations used in this method:
        - strip(): https://docs.python.org/3/library/stdtypes.html#str.strip
        - lower(): https://docs.python.org/3/library/stdtypes.html#str.lower
        - join(): https://docs.python.org/3/library/stdtypes.html#str.join
        '''
        clean_keyword = keyword.strip().lower()
        results: List[Student] = []
        if not clean_keyword:
            return results

        for student in self.students.values():
            searchable_text = " ".join([
                student.student_id,
                student.name,
                student.email,
                student.course,
                student.notes,
                self.get_progress_status(student),
                " ".join(module.module_name for module in student.modules.values()),
                " ".join(module.lecturer for module in student.modules.values()),
                " ".join(
                    assessment.name
                    for module in student.modules.values()
                    for assessment in module.assessments
                ),
            ]).lower()

            if clean_keyword in searchable_text:
                results.append(student)

        return results

    def bubble_sort_students(self, students: List[Student], sort_by: str = "name") -> List[Student]:
        '''Explicit bubble sort algorithm.

        The brief mentions bubble sorting as evidence of algorithm use.
        This method intentionally uses bubble sort instead of sorted().
        '''
        items = students[:]
        n = len(items)

        def key_value(student: Student) -> Any:
            '''Return the field currently used for sorting.''' 
            if sort_by == "id":
                return student.student_id.lower()
            if sort_by == "attendance":
                return student.attendance
            if sort_by == "average":
                average = self.calculate_student_average(student)
                return -1 if average is None else average
            return student.name.lower()

        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                left = key_value(items[j])
                right = key_value(items[j + 1])

                if sort_by in ("attendance", "average"):
                    should_swap = left < right
                else:
                    should_swap = left > right

                if should_swap:
                    items[j], items[j + 1] = items[j + 1], items[j]
                    swapped = True
            if not swapped:
                break

        return items

    def search_students(self, keyword: str) -> List[Student]:
        '''Public wrapper around the explicit linear search.''' 
        return self.linear_search_students(keyword)

    def sort_students(self, sort_by: str = "name") -> List[Student]:
        '''Public wrapper around the explicit bubble sort.''' 
        return self.bubble_sort_students(list(self.students.values()), sort_by)

    def identify_at_risk_students(self) -> List[Tuple[str, str, float, float]]:
        '''Return a list of students below safe thresholds.

        tuple usage reference: https://docs.python.org/3/library/stdtypes.html#tuple
        '''
        at_risk: List[Tuple[str, str, float, float]] = []
        for student in self.students.values():
            average = self.calculate_student_average(student)
            if average is not None and (average < PASS_MARK or student.attendance < 70):
                at_risk.append((student.student_id, student.name, average, student.attendance))
        return at_risk

    def find_top_student(self) -> Optional[Student]:
        '''Return the student with the highest average.''' 
        best_student: Optional[Student] = None
        best_average = -1.0

        for student in self.students.values():
            average = self.calculate_student_average(student)
            if average is not None and average > best_average:
                best_average = average
                best_student = student

        return best_student

    def dashboard_metrics(self) -> Dict[str, Any]:
        '''Return summary statistics for GUI and web dashboards.''' 
        student_count = len(self.students)
        average_values: List[float] = []
        attendance_values: List[float] = []
        status_counts: Dict[str, int] = {
            "Excellent": 0,
            "Stable": 0,
            "Needs support": 0,
            "Critical risk": 0,
            "Insufficient data": 0,
        }

        for student in self.students.values():
            attendance_values.append(student.attendance)
            status_counts[self.get_progress_status(student)] += 1
            student_average = self.calculate_student_average(student)
            if student_average is not None:
                average_values.append(student_average)

        top_student = self.find_top_student()
        pass_count = 0
        for student in self.students.values():
            student_average = self.calculate_student_average(student)
            if student_average is not None and student_average >= PASS_MARK:
                pass_count += 1

        return {
            "total_students": student_count,
            "average_grade": round(mean(average_values), 2) if average_values else None,
            "average_attendance": round(mean(attendance_values), 2) if attendance_values else None,
            "at_risk_count": len(self.identify_at_risk_students()),
            "pass_rate": round((pass_count / student_count) * 100, 2) if student_count else 0.0,
            "status_counts": status_counts,
            "top_student": top_student,
        }

    def serialise_student(self, student: Student) -> Dict[str, Any]:
        '''Convert a student object into a plain dictionary.''' 
        average = self.calculate_student_average(student)
        return {
            "student_id": student.student_id,
            "name": student.name,
            "email": student.email,
            "course": student.course,
            "attendance": student.attendance,
            "status": self.get_progress_status(student),
            "average": average,
            "grade_band": None if average is None else self.get_grade_band(average),
            "recommendation": self.get_recommendation(student),
            "notes": student.notes,
            "created_at": student.created_at,
            "updated_at": student.updated_at,
        }

    def export_csv(self) -> Path:
        '''Export a CSV report to disk.

        References:
        - csv.writer(): https://docs.python.org/3/library/csv.html
        - newline='' for csv writing: csv docs above
        '''
        with open(self.export_file, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Student ID",
                "Name",
                "Email",
                "Course",
                "Attendance",
                "Average",
                "Grade Band",
                "Status",
                "Recommendation",
                "Module Count",
                "Updated At",
            ])
            for student in self.sort_students("name"):
                average = self.calculate_student_average(student)
                writer.writerow([
                    student.student_id,
                    student.name,
                    student.email,
                    student.course,
                    student.attendance,
                    "" if average is None else average,
                    "" if average is None else self.get_grade_band(average),
                    self.get_progress_status(student),
                    self.get_recommendation(student),
                    len(student.modules),
                    student.updated_at,
                ])
        self.log_action(f"Exported CSV report to {self.export_file}.")
        return self.export_file

    def seed_demo_data(self) -> None:
        '''Insert starter data for screenshots, demos, and testing.''' 
        if self.students:
            raise TrackerError("Demo data can only be inserted into an empty dataset.")

        self.add_student("P476432", "Night", "night@example.com", COURSE_CODE, 91, "Project owner and main test account.")
        self.add_student("P476433", "Luna", "luna@example.com", COURSE_CODE, 66, "Attendance needs improvement.")
        self.add_student("P476434", "Orion", "orion@example.com", COURSE_CODE, 48, "Requires urgent support.")

        self.add_module("P476432", "Advanced Python", "Dr Stone")
        self.add_module("P476432", "Software Design", "Prof Lin")
        self.add_assessment("P476432", "Advanced Python", "Coursework", 88, 60, "Very strong coding.")
        self.add_assessment("P476432", "Advanced Python", "Exam", 82, 40, "Good exam technique.")
        self.add_assessment("P476432", "Software Design", "Prototype", 93, 50, "Excellent design thinking.")
        self.add_assessment("P476432", "Software Design", "Report", 86, 50, "Clear technical writing.")

        self.add_module("P476433", "Advanced Python", "Dr Stone")
        self.add_module("P476433", "Databases", "Dr Ada")
        self.add_assessment("P476433", "Advanced Python", "Coursework", 58, 60, "Needs cleaner structure.")
        self.add_assessment("P476433", "Advanced Python", "Exam", 61, 40, "Acceptable progress.")
        self.add_assessment("P476433", "Databases", "CW1", 54, 50, "Can improve testing.")
        self.add_assessment("P476433", "Databases", "CW2", 46, 50, "Review joins and constraints.")

        self.add_module("P476434", "Advanced Python", "Dr Stone")
        self.add_module("P476434", "Networks", "Dr Neo")
        self.add_assessment("P476434", "Advanced Python", "Coursework", 34, 60, "Missing key requirements.")
        self.add_assessment("P476434", "Advanced Python", "Exam", 39, 40, "Weak exam result.")
        self.add_assessment("P476434", "Networks", "Lab", 41, 40, "Basic pass.")
        self.add_assessment("P476434", "Networks", "Test", 29, 60, "High risk profile.")
