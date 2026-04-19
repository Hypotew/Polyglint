import re
from pathlib import Path
from polyglint.checkers.base import BaseChecker
from polyglint.violation import Violation, Severity

FUNC_PATTERN = re.compile(
    r'(?:local\s+)?function\s+([a-zA-Z_][a-zA-Z0-9_:.]*)\s*\(([^)]*)\)'
)


class LuaChecker(BaseChecker):
    def _check_language(self, file_path: Path) -> list[Violation]:
        violations = []
        lines = file_path.read_text(encoding="utf-8").splitlines()

        func_count = 0

        for i, line in enumerate(lines, start=1):
            match = FUNC_PATTERN.search(line)
            if not match:
                continue

            func_count += 1
            name = match.group(1).split(".")[-1].split(":")[-1]
            params = [p.strip() for p in match.group(2).split(",") if p.strip()]

            if len(name) < 3:
                violations.append(Violation(
                    file=str(file_path),
                    line=i,
                    col=match.start(1) + 1,
                    rule="C-F2",
                    message="function name too short",
                    severity=Severity.MINOR,
                ))
            if not re.match(r'^[a-z][a-z0-9_]*$', name):
                violations.append(Violation(
                    file=str(file_path),
                    line=i,
                    col=match.start(1) + 1,
                    rule="C-F2",
                    message="non-snake-case function name",
                    severity=Severity.MINOR,
                ))

            for j, _ in enumerate(params[4:], start=5):
                violations.append(Violation(
                    file=str(file_path),
                    line=i,
                    col=match.start(2) + 1,
                    rule="C-F5",
                    message=f"{_ordinal(j)} parameter in function",
                    severity=Severity.MAJOR,
                ))

            if func_count > 10:
                violations.append(Violation(
                    file=str(file_path),
                    line=i,
                    col=match.start(1) + 1,
                    rule="C-O3",
                    message=f"{_ordinal(func_count)} function in the file",
                    severity=Severity.MAJOR,
                ))

        return violations


def _ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}{['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]}"
