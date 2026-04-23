# Polyglint violation data model
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    FATAL = "fatal"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"


@dataclass
class Violation:
    file: str
    line: int
    col: int
    rule: str
    message: str
    severity: Severity = Severity.MINOR
