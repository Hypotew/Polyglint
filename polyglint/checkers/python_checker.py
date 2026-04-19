import ast
import re
from pathlib import Path
from polyglint.checkers.base import BaseChecker, ordinal
from polyglint.violation import Violation, Severity


class PythonChecker(BaseChecker):
    def _check_language(self, file_path: Path) -> list[Violation]:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        f = str(file_path)
        return (
            _check_func_naming(tree, f)
            + _check_func_params(tree, f)
            + _check_func_length(tree, f)
            + _check_func_count(tree, f)
        )


def _make(f: str, line: int, col: int, rule: str, msg: str, sev: Severity):
    return Violation(file=f, line=line, col=col, rule=rule, message=msg,
                     severity=sev)


def _check_func_naming(tree: ast.Module, f: str) -> list[Violation]:
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if len(node.name) < 3:
            out.append(_make(f, node.lineno, node.col_offset + 1,
                             "C-F2", "function name too short", Severity.MINOR))
        if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
            out.append(_make(f, node.lineno, node.col_offset + 1,
                             "C-F2", "non-snake-case function name",
                             Severity.MINOR))
    return out


def _check_func_params(tree: ast.Module, f: str) -> list[Violation]:
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for i, param in enumerate(node.args.args[4:], start=5):
            out.append(_make(f, param.lineno, param.col_offset + 1,
                             "C-F5", f"{ordinal(i)} parameter in function",
                             Severity.MAJOR))
    return out


def _check_func_length(tree: ast.Module, f: str) -> list[Violation]:
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        body_start = node.lineno + 1
        for line_num in range(body_start + 20, node.end_lineno + 1):
            out.append(_make(f, line_num, 1, "C-F4",
                             f"{ordinal(line_num - body_start + 1)} line in the function",
                             Severity.MAJOR))
    return out


def _check_func_count(tree: ast.Module, f: str) -> list[Violation]:
    out = []
    func_count = 0
    non_static_count = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        func_count += 1
        if node in tree.body:
            non_static_count += 1
        total_ex = func_count > 10
        ns_ex = non_static_count > 5
        if total_ex and ns_ex:
            msg = (f"{ordinal(non_static_count)} non-static and "
                   f"{ordinal(func_count)} function in the file")
            out.append(_make(f, node.lineno, node.col_offset + 1,
                             "C-O3", msg, Severity.MAJOR))
        elif ns_ex:
            out.append(_make(f, node.lineno, node.col_offset + 1, "C-O3",
                             f"{ordinal(non_static_count)} non-static function in the file",
                             Severity.MAJOR))
        elif total_ex:
            out.append(_make(f, node.lineno, node.col_offset + 1, "C-O3",
                             f"{ordinal(func_count)} function in the file",
                             Severity.MAJOR))
    return out
