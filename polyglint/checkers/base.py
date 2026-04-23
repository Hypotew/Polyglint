# Polyglint base checker and generic rule dispatch
from abc import ABC, abstractmethod
from pathlib import Path
from polyglint.violation import Violation, Severity
from polyglint.checkers.generic_checks import (
    _check_empty_lines,
    _check_trailing_whitespace,
    _check_line_endings,
    _check_line_issues,
    _check_indentation,
)
from polyglint.checkers.paren_checks import (
    _check_space_before_paren,
    _check_space_before_comma,
    _check_space_after_comma,
)


_HEADER_STARTS = {
    '.py': ('#',), '.js': ('//', '/*'), '.lua': ('--',),
}


def _check_file_header(lines, f, ext):
    starts = _HEADER_STARTS.get(ext, ())
    if not starts:
        return []
    for line in lines:
        if not line.strip():
            continue
        if not any(line.lstrip().startswith(s) for s in starts):
            return [Violation(f, 1, 1, "C-G1",
                "missing file header comment", Severity.MINOR)]
        return []
    return []


def ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}{['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]}"


class BaseChecker(ABC):
    def check(self, file_path: Path) -> list[Violation]:
        return self._check_generic(file_path) + self._check_language(file_path)

    def _check_generic(self, file_path: Path) -> list[Violation]:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        f = str(file_path)
        ext = file_path.suffix
        return (
            _check_file_header(lines, f, ext)
            + _check_empty_lines(lines, f)
            + _check_trailing_whitespace(lines, f)
            + _check_line_endings(content, f)
            + _check_line_issues(lines, content, f)
            + _check_indentation(lines, f)
            + _check_space_before_paren(lines, f)
            + _check_space_before_comma(lines, f)
            + _check_space_after_comma(lines, f)
        )

    @abstractmethod
    def _check_language(self, file_path: Path) -> list[Violation]:
        ...
