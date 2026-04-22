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


def _func_body_set(lines: list) -> set:
    body, depth, func_depths = set(), 0, []
    for i, line in enumerate(lines, start=1):
        clean = re.sub('"[^"]*"|\'[^\']*\'', '""', line)
        m = clean.find('//')
        code = clean[:m] if m != -1 else clean
        is_decl = bool(FUNC_DECL.search(code) or ARROW_FUNC.search(code))
        if is_decl:
            func_depths.append(depth)
        depth += code.count('{') - code.count('}')
        func_depths = [d for d in func_depths if depth > d]
        if func_depths and not is_decl:
            body.add(i)
    return body


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


class JsChecker(BaseChecker):
    def _check_language(self, file_path: Path) -> list[Violation]:
        lines = file_path.read_text(encoding="utf-8").splitlines()
        funcs = _parse_funcs(lines)
        f = str(file_path)
        return (
            _check_func_naming(funcs, f)
            + _check_func_params(funcs, f)
            + _check_func_count(funcs, f)
            + self._check_comments(lines, f)
            + self._check_func_length(lines, f)
            + self._check_func_separation(lines, f)
            + self._check_curly_brackets(lines, f)
        )

    def _check_comments(self, lines, f):
        out = []
        body = _func_body_set(lines)
        for i, line in enumerate(lines, start=1):
            if i not in body:
                continue
            clean = re.sub('"[^"]*"|\'[^\']*\'', '""', line)
            idx = clean.find('//')
            if idx != -1:
                out.append(Violation(
                    file=f, line=i, col=idx + 1, rule="C-F8",
                    message="comment inside function",
                    severity=Severity.MINOR
                ))
        return out

    def _check_func_length(self, lines, f):
        out = []
        depth, func_stack, pending = 0, [], []
        for i, line in enumerate(lines, start=1):
            clean = re.sub('"[^"]*"|\'[^\']*\'', '""', line)
            m = clean.find('//')
            code = clean[:m] if m != -1 else clean
            if FUNC_DECL.search(code) or ARROW_FUNC.search(code):
                pending.append(i)
            prev_depth, depth = depth, depth + code.count('{') - code.count('}')
            if depth > prev_depth and pending:
                func_stack += [(s, i + 1, prev_depth) for s in pending]
                pending = []
            closed = [(s, b, d) for s, b, d in func_stack if depth <= d]
            func_stack = [(s, b, d) for s, b, d in func_stack if depth > d]
            for _, body_start, _ in closed:
                for ln in range(body_start + 20, i):
                    n = ln - body_start + 1
                    out.append(Violation(f, ln, 1, "C-F4",
                        f"{ordinal(n)} line in the function", Severity.MAJOR))
        return out

    def _check_func_separation(self, lines, f):
        ranges, depth, func_stack, pending = [], 0, [], []
        for i, line in enumerate(lines, start=1):
            clean = re.sub('"[^"]*"|\'[^\']*\'', '""', line)
            m = clean.find('//')
            code = clean[:m] if m != -1 else clean
            if FUNC_DECL.search(code) or ARROW_FUNC.search(code):
                pending.append(i)
            prev_depth, depth = depth, depth + code.count('{') - code.count('}')
            if depth > prev_depth and pending:
                func_stack += [(s, prev_depth) for s in pending]
                pending = []
            ranges += [(s, i) for s, d in func_stack if depth <= d and d == 0]
            func_stack = [(s, d) for s, d in func_stack if depth > d]
        out = []
        for j in range(len(ranges) - 1):
            end, start = ranges[j][1], ranges[j + 1][0]
            if not any(not l.strip() for l in lines[end:start - 1]):
                out.append(Violation(f, start, 1, "C-G2",
                    "missing empty line between functions"))
        return out

    def _check_curly_brackets(self, lines, f):
        out = []
        for i, line in enumerate(lines, start=1):
            clean = re.sub('"[^"]*"|\'[^\']*\'', '""', line)
            m = clean.find('//')
            code = clean[:m] if m != -1 else clean
            stripped = code.strip()
            if stripped.startswith('}') and stripped != '}':
                rest = stripped[1:].lstrip()
                allowed = ('else', 'catch', 'finally', 'while')
                if not any(rest.startswith(a) for a in allowed):
                    col = line.index('}') + 1
                    out.append(Violation(f, i, col, "C-L4",
                        "closing brace not alone on its line"))
            if FUNC_DECL.search(code) and '{' in code:
                col = code.index('{') + 1
                out.append(Violation(f, i, col, "C-L4",
                    "function opening brace must be on its own line"))
        return out
