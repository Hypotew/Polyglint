# Polyglint file walker and checker runner
import re
from pathlib import Path
from polyglint.checkers import get_checker
from polyglint.violation import Violation

EXCLUDED_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", "tests"
}
_SNAKE = re.compile(r'^[a-z][a-z0-9_]*$')


def run(paths: list[Path]) -> dict[str, list[Violation]]:
    results = {}
    for path in paths:
        if path.is_dir():
            _walk(path, results)
        elif path.is_file():
            _check_file(path, results)
    return results


def _walk(root: Path, results: dict) -> None:
    for item in root.rglob("*"):
        if any(part in EXCLUDED_DIRS for part in item.parts):
            continue
        if item.is_file():
            _check_file(item, results)


def _name_violations(path: Path) -> list:
    stem = path.stem
    if stem.startswith('__') and stem.endswith('__'):
        return []
    if _SNAKE.match(stem):
        return []
    msg = f"non-snake-case file name '{stem}'"
    return [Violation(str(path), 1, 1, "C-O4", msg)]


def _check_file(path: Path, results: dict) -> None:
    checker = get_checker(path)
    if checker is None:
        return
    f = str(path)
    violations = _name_violations(path) + checker.check(path)
    if violations:
        results[f] = violations
