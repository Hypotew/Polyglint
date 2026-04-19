from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path
from polyglint.violation import Violation, Severity

MAX_LINE_LENGTH = 80


def ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}{['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]}"


def _find_all(content: str, substring: str) -> Iterator[int]:
    pos = content.find(substring)
    while pos != -1:
        yield pos
        pos = content.find(substring, pos + 1)


def _make(file: str, line: int, col: int, rule: str, msg: str, sev: Severity):
    return Violation(file=file, line=line, col=col, rule=rule, message=msg,
                    severity=sev)


class BaseChecker(ABC):
    def check(self, file_path: Path) -> list[Violation]:
        return self._check_generic(file_path) + self._check_language(file_path)

    def _check_generic(self, file_path: Path) -> list[Violation]:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        f = str(file_path)
        return (
            _check_leading(lines, f)
            + _check_trailing(lines, f)
            + _check_trailing_whitespace(lines, f)
            + _check_line_endings(content, f)
            + _check_line_length(lines, f)
            + _check_newline_eof(content, lines, f)
            + _check_indentation(lines, f)
        )

    @abstractmethod
    def _check_language(self, file_path: Path) -> list[Violation]:
        ...


def _check_leading(lines: list, f: str) -> list[Violation]:
    out = []
    for i, line in enumerate(lines, start=1):
        if line.strip() == "":
            out.append(_make(f, i, 1, "C-G8", "leading empty line", Severity.MINOR))
        else:
            break
    return out


def _check_trailing(lines: list, f: str) -> list[Violation]:
    out = []
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "":
            out.append(_make(f, i + 1, 1, "C-G8", "trailing empty line",
                            Severity.MINOR))
        else:
            break
    return out


def _check_trailing_whitespace(lines: list, f: str) -> list[Violation]:
    out = []
    for i, line in enumerate(lines, start=1):
        trailing = len(line) - len(line.rstrip(" \t"))
        if trailing > 0:
            msg = "trailing space" if trailing == 1 else f"{trailing} trailing spaces"
            out.append(_make(f, i, len(line.rstrip(" \t")) + 1, "C-G7", msg,
                            Severity.MINOR))
    return out


def _check_line_endings(content: str, f: str) -> list[Violation]:
    out = []
    for pos in _find_all(content, "\r"):
        line_num = content[:pos].count("\n") + 1
        out.append(_make(f, line_num, pos, "C-G6", "\\r-style line ending",
                        Severity.MINOR))
    return out


def _check_line_length(lines: list, f: str) -> list[Violation]:
    out = []
    for i, line in enumerate(lines, start=1):
        if len(line) > MAX_LINE_LENGTH:
            out.append(_make(f, i, MAX_LINE_LENGTH + 1, "C-F3",
                            f"{len(line)}-character line", Severity.MAJOR))
    return out


def _check_newline_eof(content: str, lines: list, f: str) -> list[Violation]:
    if content and not content.endswith("\n"):
        return [_make(f, len(lines), len(lines[-1]) + 1, "C-A3",
                    "file not ending with a newline", Severity.INFO)]
    return []


def _check_indentation(lines: list, f: str) -> list[Violation]:
    out = []
    for i, line in enumerate(lines, start=1):
        indent = line[:len(line) - len(line.lstrip(" \t"))]
        if "\t" in indent:
            out.append(_make(f, i, indent.index("\t") + 1, "C-L2",
                            "tab used for indentation", Severity.MINOR))
        elif len(indent) % 4 != 0:
            out.append(_make(f, i, 1, "C-L2",
                            "indentation not done with groups of 4 spaces",
                            Severity.MINOR))
    return out
