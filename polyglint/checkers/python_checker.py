import ast
import re
from pathlib import Path
from polyglint.checkers.base import BaseChecker, ordinal
from polyglint.violation import Violation, Severity


class PythonChecker(BaseChecker):
    def _check_language(self, file_path: Path) -> list[Violation]:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        lines = source.splitlines()
        f = str(file_path)
        return (
            _check_func_naming(tree, f)
            + _check_func_params(tree, f)
            + _check_func_length(tree, f)
            + _check_func_count(tree, f)
            + self._check_comments(tree, lines, f)
            + self._check_func_separation(tree, lines, f)
        )

    def _check_func_separation(self, tree, lines, f):
        types = (ast.FunctionDef, ast.AsyncFunctionDef)
        funcs = sorted(
            [n for n in tree.body if isinstance(n, types)],
            key=lambda n: n.lineno
        )
        out = []
        for i in range(len(funcs) - 1):
            end = funcs[i].end_lineno
            start = funcs[i + 1].lineno
            has_gap = any(not l.strip() for l in lines[end:start - 1])
            if not has_gap:
                out.append(Violation(
                    file=f, line=start, col=1, rule="C-G2",
                    message="missing empty line between functions",
                    severity=Severity.MINOR
                ))
        return out

    def _check_comments(self, tree, lines, f):
        out = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for ln in range(node.lineno + 1, node.end_lineno + 1):
                src = lines[ln - 1] if ln <= len(lines) else ""
                clean = re.sub('"[^"]*"|\'[^\']*\'', '""', src)
                idx = clean.find('#')
                if idx != -1:
                    out.append(Violation(
                        file=f, line=ln, col=idx + 1, rule="C-F8",
                        message="comment inside function",
                        severity=Severity.MINOR
                    ))
        return out


def _check_func_naming(tree: ast.Module, f: str) -> list[Violation]:
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        col = node.col_offset + 1
        if len(node.name) < 3:
            out.append(Violation(
                file=f, line=node.lineno, col=col, rule="C-F2",
                message="function name too short", severity=Severity.MINOR
            ))
        if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
            out.append(Violation(
                file=f, line=node.lineno, col=col, rule="C-F2",
                message="non-snake-case function name", severity=Severity.MINOR
            ))
    return out


def _check_func_params(tree: ast.Module, f: str) -> list[Violation]:
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for i, param in enumerate(node.args.args[4:], start=5):
            msg = f"{ordinal(i)} parameter in function"
            out.append(Violation(
                file=f, line=param.lineno, col=param.col_offset + 1,
                rule="C-F5", message=msg, severity=Severity.MAJOR
            ))
    return out


def _check_func_length(tree: ast.Module, f: str) -> list[Violation]:
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body_start = node.lineno + 1
        for line_num in range(body_start + 20, node.end_lineno + 1):
            n = line_num - body_start + 1
            msg = f"{ordinal(n)} line in the function"
            out.append(Violation(
                file=f, line=line_num, col=1, rule="C-F4",
                message=msg, severity=Severity.MAJOR
            ))
    return out


def _func_count_violation(f, node, func_count, non_static_count):
    col = node.col_offset + 1
    ns = ordinal(non_static_count)
    total = ordinal(func_count)
    if func_count > 10 and non_static_count > 5:
        msg = f"{ns} non-static and {total} function in the file"
    elif non_static_count > 5:
        msg = f"{ns} non-static function in the file"
    else:
        msg = f"{total} function in the file"
    return Violation(
        file=f, line=node.lineno, col=col, rule="C-O3",
        message=msg, severity=Severity.MAJOR
    )


def _check_func_count(tree: ast.Module, f: str) -> list[Violation]:
    out = []
    func_count = 0
    non_static_count = 0
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        func_count += 1
        if node in tree.body:
            non_static_count += 1
        if func_count > 10 or non_static_count > 5:
            v = _func_count_violation(f, node, func_count, non_static_count)
            out.append(v)
    return out
