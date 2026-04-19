from pathlib import Path
from polyglint.checkers.python_checker import PythonChecker
from polyglint.checkers.lua_checker import LuaChecker

CHECKERS = {
    ".py": PythonChecker,
    ".lua": LuaChecker,
}


def get_checker(path: Path):
    ext = path.suffix.lower()
    cls = CHECKERS.get(ext)
    return cls() if cls else None
