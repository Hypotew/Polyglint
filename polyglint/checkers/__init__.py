from pathlib import Path
from polyglint.checkers.python_checker import PythonChecker

CHECKERS = {
    ".py": PythonChecker,
}


def get_checker(path: Path):
    ext = path.suffix.lower()
    cls = CHECKERS.get(ext)
    return cls() if cls else None
