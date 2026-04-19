import re
from pathlib import Path
from polyglint.checkers.base import BaseChecker, ordinal
from polyglint.violation import Violation, Severity

FUNC_PATTERN = re.compile(
    r'(?:local\s+)?function\s+([a-zA-Z_][a-zA-Z0-9_:.]*)\s*\(([^)]*)\)'
)


def _parse_funcs(lines: list) -> list:
    funcs = []
    for i, line in enumerate(lines, start=1):
        match = FUNC_PATTERN.search(line)
        if not match:
            continue
        name = match.group(1).split(".")[-1].split(":")[-1]
        params = [p.strip() for p in match.group(2).split(",") if p.strip()]
        funcs.append((i, match.start(1) + 1, match.start(2) + 1, name, params))
    return funcs


def _check_func_naming(funcs: list, f: str) -> list[Violation]:
    out = []
    for line, col, _, name, _ in funcs:
        if len(name) < 3:
            out.append(Violation(
                file=f, line=line, col=col, rule="C-F2",
                message="function name too short", severity=Severity.MINOR
            ))
        if not re.match(r'^[a-z][a-z0-9_]*$', name):
            out.append(Violation(
                file=f, line=line, col=col, rule="C-F2",
                message="non-snake-case function name", severity=Severity.MINOR
            ))
    return out


def _check_func_params(funcs: list, f: str) -> list[Violation]:
    out = []
    for line, _, col_p, _, params in funcs:
        for j, _ in enumerate(params[4:], start=5):
            msg = f"{ordinal(j)} parameter in function"
            out.append(Violation(
                file=f, line=line, col=col_p, rule="C-F5",
                message=msg, severity=Severity.MAJOR
            ))
    return out


def _check_func_count(funcs: list, f: str) -> list[Violation]:
    out = []
    for idx, (line, col, _, _, _) in enumerate(funcs, start=1):
        if idx > 10:
            msg = f"{ordinal(idx)} function in the file"
            out.append(Violation(
                file=f, line=line, col=col, rule="C-O3",
                message=msg, severity=Severity.MAJOR
            ))
    return out


class LuaChecker(BaseChecker):
    def _check_language(self, file_path: Path) -> list[Violation]:
        lines = file_path.read_text(encoding="utf-8").splitlines()
        funcs = _parse_funcs(lines)
        f = str(file_path)
        return (
            _check_func_naming(funcs, f)
            + _check_func_params(funcs, f)
            + _check_func_count(funcs, f)
        )
