from pathlib import Path
from polyglint.checkers import get_checker
from polyglint.violation import Violation

EXCLUDED_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", "tests"
}


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


def _check_file(path: Path, results: dict) -> None:
    checker = get_checker(path)
    if checker is None:
        return
    violations = checker.check(path)
    if violations:
        results[str(path)] = violations
