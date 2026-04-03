"""Custom exceptions for Student Progress Tracker Pro.

References:
- Python exceptions tutorial: https://docs.python.org/3/tutorial/errors.html
- Exception base class: https://docs.python.org/3/library/exceptions.html
"""


class ValidationError(Exception):
    """Raised when user input fails validation rules."""


class TrackerError(Exception):
    """Raised for logical workflow errors in the tracker."""
