from abc import ABC, abstractmethod
from pathlib import Path
from polyglint.violation import Violation
from polyglint.checkers.generic_checks import (
    _check_empty_lines,
    _check_trailing_whitespace,
    _check_line_endings,
    _check_line_issues,
    _check_indentation,
)


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
        return (
            _check_empty_lines(lines, f)
            + _check_trailing_whitespace(lines, f)
            + _check_line_endings(content, f)
            + _check_line_issues(lines, content, f)
            + _check_indentation(lines, f)
        )

    @abstractmethod
    def _check_language(self, file_path: Path) -> list[Violation]:
        ...
