from polyglint.violation import Violation, Severity

RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[31m"
YELLOW = "\033[33m"
GREEN  = "\033[32m"
WHITE  = "\033[37m"

SEVERITY_COLOR = {
    Severity.FATAL: RED,
    Severity.MAJOR: RED,
    Severity.MINOR: YELLOW,
    Severity.INFO:  WHITE,
}


def report(results: dict[str, list[Violation]]) -> int:
    if not results:
        print(f"{GREEN}No violations found.{RESET}")
        return 0
    counts = _print_violations(results)
    _print_summary(counts, len(results))
    return 1


def _print_violations(results: dict) -> dict:
    counts = {"major": 0, "minor": 0, "info": 0}
    for file, violations in sorted(results.items()):
        print(f"\n{BOLD}{file}{RESET}")
        for v in sorted(violations, key=lambda x: (x.line, x.col)):
            _print_violation(v)
            _increment(counts, v.severity)
    return counts


def _print_violation(v: Violation) -> None:
    color = SEVERITY_COLOR.get(v.severity, WHITE)
    location = f"line {v.line}, col {v.col}"
    print(f"  {location:<22} {color}{BOLD}[{v.rule}]{RESET}  {v.message}")


def _increment(counts: dict, severity: Severity) -> None:
    if severity in (Severity.FATAL, Severity.MAJOR):
        counts["major"] += 1
    elif severity == Severity.MINOR:
        counts["minor"] += 1
    else:
        counts["info"] += 1


def _print_summary(counts: dict, files_count: int) -> None:
    parts = []
    if counts["major"]:
        parts.append(f"{RED}{BOLD}{counts['major']} major{RESET}")
    if counts["minor"]:
        parts.append(f"{YELLOW}{BOLD}{counts['minor']} minor{RESET}")
    if counts["info"]:
        parts.append(f"{WHITE}{BOLD}{counts['info']} info{RESET}")
    files_str = f"{files_count} file{'s' if files_count > 1 else ''}"
    print(f"\n{', '.join(parts)} in {files_str}")
