import ast
import re
from pathlib import Path
from polyglint.checkers.base import BaseChecker, ordinal
from polyglint.violation import Violation, Severity


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

                for i, param in enumerate(node.args.args[4:], start=5):  # C-F5 - too many parameters
                    violations.append(Violation(
                        file=str(file_path),
                        line=param.lineno,
                        col=param.col_offset + 1,
                        rule="C-F5",
                        message=f"{ordinal(i)} parameter in function",
                        severity=Severity.MAJOR,
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
                        message=f"{ordinal(line_in_func)} line in the function",
                        severity=Severity.MAJOR,
                    ))

        func_count = 0  # C-O3 - too many functions
        non_static_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_count += 1
                if node in tree.body:
                    non_static_count += 1
                total_exceeded = func_count > 10
                non_static_exceeded = non_static_count > 5
                if total_exceeded and non_static_exceeded:
                    violations.append(Violation(
                        file=str(file_path),
                        line=node.lineno,
                        col=node.col_offset + 1,
                        rule="C-O3",
                        message=f"{ordinal(non_static_count)} non-static and {ordinal(func_count)} function in the file",
                        severity=Severity.MAJOR,
                    ))
                elif non_static_exceeded:
                    violations.append(Violation(
                        file=str(file_path),
                        line=node.lineno,
                        col=node.col_offset + 1,
                        rule="C-O3",
                        message=f"{ordinal(non_static_count)} non-static function in the file",
                        severity=Severity.MAJOR,
                    ))
                elif total_exceeded:
                    violations.append(Violation(
                        file=str(file_path),
                        line=node.lineno,
                        col=node.col_offset + 1,
                        rule="C-O3",
                        message=f"{ordinal(func_count)} function in the file",
                        severity=Severity.MAJOR,
                    ))

        return violations
