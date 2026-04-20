from pathlib import Path
from polyglint.violation import Violation, Severity

RESET  = "\033[0m"
RED    = "\033[31m"
YELLOW = "\033[33m"
GREEN  = "\033[32m"
WHITE  = "\033[37m"
PINK   = "\033[95m"
BOLD   = "\033[1m"

SEVERITY_COLOR = {
    Severity.FATAL: RED,
    Severity.MAJOR: RED,
    Severity.MINOR: YELLOW,
    Severity.INFO:  WHITE,
}

SEVERITY_LABEL = {
    Severity.FATAL: "Fatal",
    Severity.MAJOR: "Major",
    Severity.MINOR: "Minor",
    Severity.INFO:  "Info",
}


def report(results: dict[str, list[Violation]]) -> int:
    if not results:
        print(f"{GREEN}No violations found.{RESET}")
        return 0
    total = _print_violations(results)
    _print_summary(total)
    return 1


def _print_violations(results: dict) -> int:
    total = 0
    file_cache = {}
    for file, violations in sorted(results.items()):
        lines = _read_lines(file, file_cache)
        for v in sorted(violations, key=lambda x: (x.line, x.col)):
            _print_violation(v, lines)
            total += 1
    return total


def _read_lines(file: str, cache: dict) -> list:
    if file not in cache:
        try:
            cache[file] = Path(file).read_text(encoding="utf-8").splitlines()
        except OSError:
            cache[file] = []
    return cache[file]


def _print_violation(v: Violation, lines: list) -> None:
    color = SEVERITY_COLOR.get(v.severity, WHITE)
    label = SEVERITY_LABEL.get(v.severity, "Info")
    location = f"{v.file}:{v.line}:{v.col}: "
    rest = f"[Banana] [{label}] {v.message} ({v.rule})"
    print(f"{BOLD}{WHITE}{location}{PINK}warning:{RESET} {BOLD}{WHITE}{rest}{RESET}")
    if 0 < v.line <= len(lines):
        source = lines[v.line - 1]
        pad = " " * len(str(v.line))
        print(f"  {v.line} | {source}")
        print(f"  {pad} | {' ' * (v.col - 1)}{GREEN}^{RESET}" )


def _print_summary(total: int) -> None:
    label = "warning" if total == 1 else "warnings"
    print(f"\n{total} {label} generated.")
