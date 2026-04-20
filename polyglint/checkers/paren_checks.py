import re
from polyglint.violation import Violation, Severity

_STRINGS = re.compile('"[^"]*"|\'[^\']*\'')
_COMMENT = re.compile(r'(#|//|--)')


def _check_space_before_paren(lines: list, f: str) -> list[Violation]:
    out = []
    for i, line in enumerate(lines, start=1):
        clean = _STRINGS.sub('""', line)
        m = _COMMENT.search(clean)
        code = clean[:m.start()] if m else clean
        pos = 0
        while True:
            idx = code.find(' )', pos)
            if idx == -1:
                break
            if code[:idx].strip():
                out.append(Violation(
                    file=f, line=i, col=idx + 1, rule="C-L3",
                    message="space before right parenthesis",
                    severity=Severity.MINOR
                ))
            pos = idx + 1
    return out
