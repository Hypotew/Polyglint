import sys
from polyglint.violation import Violation, Severity

RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[31m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
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

    total_major = 0
    total_minor = 0
    total_info  = 0

    for file, violations in sorted(results.items()):
        print(f"\n{BOLD}{file}{RESET}")
        for v in sorted(violations, key=lambda x: (x.line, x.col)):
            color = SEVERITY_COLOR.get(v.severity, WHITE)
            location = f"line {v.line}, col {v.col}"
            print(f"  {location:<22} {color}{BOLD}[{v.rule}]{RESET}  {v.message}")
            if v.severity in (Severity.FATAL, Severity.MAJOR):
                total_major += 1
            elif v.severity == Severity.MINOR:
                total_minor += 1
            else:
                total_info += 1

    parts = []
    if total_major:
        parts.append(f"{RED}{BOLD}{total_major} major{RESET}")
    if total_minor:
        parts.append(f"{YELLOW}{BOLD}{total_minor} minor{RESET}")
    if total_info:
        parts.append(f"{WHITE}{BOLD}{total_info} info{RESET}")

    files_count = len(results)
    files_str = f"{files_count} file{'s' if files_count > 1 else ''}"
    print(f"\n{', '.join(parts)} in {files_str}")

    return 1
