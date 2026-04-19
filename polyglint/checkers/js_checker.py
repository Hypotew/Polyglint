import re
from pathlib import Path
from polyglint.checkers.base import BaseChecker, ordinal
from polyglint.violation import Violation, Severity

FUNC_DECL = re.compile(
    r'(?:async\s+)?function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(([^)]*)\)'
)
ARROW_FUNC = re.compile(
    r'(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*='
    r'\s*(?:async\s*)?\(([^)]*)\)\s*=>'
)


def _make(f, line, col, rule, msg, sev):
    return Violation(
        file=f, line=line, col=col, rule=rule, message=msg, severity=sev
    )


def _parse_funcs(lines: list) -> list:
    funcs = []
    for i, line in enumerate(lines, start=1):
        for pattern in (FUNC_DECL, ARROW_FUNC):
            match = pattern.search(line)
            if not match:
                continue
            name = match.group(1)
            params = [p.strip() for p in match.group(2).split(",") if p.strip()]
            entry = (i, match.start(1) + 1, match.start(2) + 1, name, params)
            funcs.append(entry)
    return funcs


def _check_func_naming(funcs: list, f: str) -> list[Violation]:
    out = []
    for line, col, _, name, _ in funcs:
        if len(name) < 3:
            out.append(_make(f, line, col, "C-F2",
                "function name too short", Severity.MINOR))
        if not re.match(r'^[a-z][a-zA-Z0-9]*$', name):
            out.append(_make(f, line, col, "C-F2",
                "non-camelCase function name", Severity.MINOR))
    return out


def _check_func_params(funcs: list, f: str) -> list[Violation]:
    out = []
    for line, _, col_p, _, params in funcs:
        for j, _ in enumerate(params[4:], start=5):
            msg = f"{ordinal(j)} parameter in function"
            out.append(_make(f, line, col_p, "C-F5", msg, Severity.MAJOR))
    return out


def _check_func_count(funcs: list, f: str) -> list[Violation]:
    out = []
    for idx, (line, col, _, _, _) in enumerate(funcs, start=1):
        if idx > 10:
            msg = f"{ordinal(idx)} function in the file"
            out.append(_make(f, line, col, "C-O3", msg, Severity.MAJOR))
    return out


class JsChecker(BaseChecker):
    def _check_language(self, file_path: Path) -> list[Violation]:
        lines = file_path.read_text(encoding="utf-8").splitlines()
        funcs = _parse_funcs(lines)
        f = str(file_path)
        return (
            _check_func_naming(funcs, f)
            + _check_func_params(funcs, f)
            + _check_func_count(funcs, f)
        )
