import ast
import re
from pathlib import Path
from polyglint.checkers.base import BaseChecker
from polyglint.violation import Violation, Severity


def _ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}{['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]}"


class PythonChecker(BaseChecker):
    def _check_language(self, file_path: Path) -> list[Violation]:
        violations = []
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.name) < 3:  # C-F2 - function name too short
                    violations.append(Violation(
                        file=str(file_path),
                        line=node.lineno,
                        col=node.col_offset + 1,
                        rule="C-F2",
                        message="function name too short",
                        severity=Severity.MINOR,
                    ))
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):  # C-F2 - snake_case
                    violations.append(Violation(
                        file=str(file_path),
                        line=node.lineno,
                        col=node.col_offset + 1,
                        rule="C-F2",
                        message="non-snake-case function name",
                        severity=Severity.MINOR,
                    ))

                body_start = node.lineno + 1  # C-F4 - function too long
                body_end = node.end_lineno
                for line_num in range(body_start + 20, body_end + 1):
                    line_in_func = line_num - body_start + 1
                    violations.append(Violation(
                        file=str(file_path),
                        line=line_num,
                        col=1,
                        rule="C-F4",
                        message=f"{_ordinal(line_in_func)} line in the function",
                        severity=Severity.MAJOR,
                    ))

        return violations
