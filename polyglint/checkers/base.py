from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path
from polyglint.violation import Violation, Severity

def _find_all(content: str, substring: str) -> Iterator[int]:
    pos = content.find(substring)
    while pos != -1:
        yield pos
        pos = content.find(substring, pos + 1)


class BaseChecker(ABC):
    def check(self, file_path: Path) -> list[Violation]:
        return self._check_generic(file_path) + self._check_language(file_path)

    def _check_generic(self, file_path: Path) -> list[Violation]:
        violations = []
        lines = file_path.read_text(encoding="utf-8").splitlines()

        for i, line in enumerate(lines, start=1): # C-G8 - leading empty lines
            if line.strip() == "":
                violations.append(Violation(
                    file=str(file_path),
                    line=i,
                    col=1,
                    rule="C-G8",
                    message="leading empty line",
                    severity=Severity.MINOR,
                ))
            else:
                break

        for i in range(len(lines) - 1, -1, -1): # C-G8 - trailing empty lines
            if lines[i].strip() == "":
                violations.append(Violation(
                    file=str(file_path),
                    line=i + 1,
                    col=1,
                    rule="C-G8",
                    message="trailing empty line",
                    severity=Severity.MINOR,
                ))
            else:
                break

        for i, line in enumerate(lines, start=1): # C-G7 - Trailing whitespace
            trailing = len(line) - len(line.rstrip(" \t"))
            if trailing > 0:
                message = "trailing space" if trailing == 1 else f"{trailing} trailing spaces"
                violations.append(Violation(
                    file=str(file_path),
                    line=i,
                    col=len(line.rstrip(" \t")) + 1,
                    rule="C-G7",
                    message=message,
                    severity=Severity.MINOR,
                ))

        content = file_path.read_text(encoding="utf-8") # C-G6 - Line endings
        for i, pos in enumerate(_find_all(content, "\r"), start=1):
            line_num = content[:pos].count("\n") + 1
            violations.append(Violation(
                file=str(file_path),
                line=line_num,
                col=pos,
                rule="C-G6",
                message="\\r-style line ending",
                severity=Severity.MINOR,
            ))
            
        for i, line in enumerate(lines, start=1): # C-L2 - Indentation
            indent = line[:len(line) - len(line.lstrip(" \t"))]
            if "\t" in indent:
                violations.append(Violation(
                    file=str(file_path),
                    line=i,
                    col=indent.index("\t") + 1,
                    rule="C-L2",
                    message="tab used for indentation",
                    severity=Severity.MINOR,
                ))
            elif len(indent) % 4 != 0:
                violations.append(Violation(
                    file=str(file_path),
                    line=i,
                    col=1,
                    rule="C-L2",
                    message="indentation not done with groups of 4 spaces",
                    severity=Severity.MINOR,
                ))

        return violations

    def _check_language(self, file_path: Path) -> list[Violation]:
        ...

