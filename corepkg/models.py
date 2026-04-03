from __future__ import annotations

"""Data models for the tracker.

References:
- dataclasses: https://docs.python.org/3/library/dataclasses.html
- typing annotations: https://docs.python.org/3/library/typing.html
- datetime: https://docs.python.org/3/library/datetime.html
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


@dataclass
class Assessment:
    """One weighted assessment item for a module."""

    name: str
    score: float
    weight: float
    feedback: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().strftime(DATE_FORMAT))


@dataclass
class ModuleRecord:
    """A module containing many assessments."""

    module_name: str
    lecturer: str = ""
    assessments: List[Assessment] = field(default_factory=list)


@dataclass
class Student:
    """Student profile data used across all interfaces."""

    student_id: str
    name: str
    email: str
    course: str
    attendance: float = 100.0
    notes: str = ""
    modules: Dict[str, ModuleRecord] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().strftime(DATE_FORMAT))
    updated_at: str = field(default_factory=lambda: datetime.now().strftime(DATE_FORMAT))
