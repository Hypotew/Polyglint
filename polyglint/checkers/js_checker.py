import re
from pathlib import Path
from polyglint.checkers.base import BaseChecker, ordinal
from polyglint.violation import Violation, Severity

# function foo(a, b) ou async function foo(a, b)
FUNC_DECL = re.compile(
    r'(?:async\s+)?function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(([^)]*)\)'
)
# const foo = (a, b) => ou const foo = async (a, b) =>
ARROW_FUNC = re.compile(
    r'(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>'
)


class JsChecker(BaseChecker):
    def _check_language(self, file_path: Path) -> list[Violation]:
        violations = []
        lines = file_path.read_text(encoding="utf-8").splitlines()

        func_count = 0

        for i, line in enumerate(lines, start=1):
            for pattern in (FUNC_DECL, ARROW_FUNC):
                match = pattern.search(line)
                if not match:
                    continue

                func_count += 1
                name = match.group(1)
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
                if not re.match(r'^[a-z][a-zA-Z0-9]*$', name):
                    violations.append(Violation(
                        file=str(file_path),
                        line=i,
                        col=match.start(1) + 1,
                        rule="C-F2",
                        message="non-camelCase function name",
                        severity=Severity.MINOR,
                    ))

                for j, _ in enumerate(params[4:], start=5):
                    violations.append(Violation(
                        file=str(file_path),
                        line=i,
                        col=match.start(2) + 1,
                        rule="C-F5",
                        message=f"{ordinal(j)} parameter in function",
                        severity=Severity.MAJOR,
                    ))

                if func_count > 10:
                    violations.append(Violation(
                        file=str(file_path),
                        line=i,
                        col=match.start(1) + 1,
                        rule="C-O3",
                        message=f"{ordinal(func_count)} function in the file",
                        severity=Severity.MAJOR,
                    ))

        return violations


