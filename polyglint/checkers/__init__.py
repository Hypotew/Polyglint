# Polyglint checker registry
from pathlib import Path
from polyglint.checkers.python_checker import PythonChecker
from polyglint.checkers.lua_checker import LuaChecker
from polyglint.checkers.js_checker import JsChecker

CHECKERS = {
    ".py": PythonChecker,
    ".lua": LuaChecker,
    ".js": JsChecker,
    ".mjs": JsChecker,
}


def get_checker(path: Path):
    ext = path.suffix.lower()
    cls = CHECKERS.get(ext)
    return cls() if cls else None
