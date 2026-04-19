from polyglint.violation import Violation, Severity

MAX_LINE_LENGTH = 80


def _check_empty_lines(lines: list, f: str) -> list[Violation]:
    out = []
    for i, line in enumerate(lines, start=1):
        if line.strip() == "":
            out.append(Violation(
                file=f, line=i, col=1, rule="C-G8",
                message="leading empty line", severity=Severity.MINOR
            ))
        else:
            break
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "":
            out.append(Violation(
                file=f, line=i + 1, col=1, rule="C-G8",
                message="trailing empty line", severity=Severity.MINOR
            ))
        else:
            break
    return out


def _check_trailing_whitespace(lines: list, f: str) -> list[Violation]:
    out = []
    for i, line in enumerate(lines, start=1):
        trailing = len(line) - len(line.rstrip(" \t"))
        if trailing > 0:
            if trailing == 1:
                msg = "trailing space"
            else:
                msg = f"{trailing} trailing spaces"
            out.append(Violation(
                file=f, line=i, col=len(line.rstrip(" \t")) + 1,
                rule="C-G7", message=msg, severity=Severity.MINOR
            ))
    return out


def _check_line_endings(content: str, f: str) -> list[Violation]:
    out = []
    pos = content.find("\r")
    while pos != -1:
        line_num = content[:pos].count("\n") + 1
        out.append(Violation(
            file=f, line=line_num, col=pos, rule="C-G6",
            message="\\r-style line ending", severity=Severity.MINOR
        ))
        pos = content.find("\r", pos + 1)
    return out


def _check_line_issues(lines: list, content: str, f: str) -> list[Violation]:
    out = []
    for i, line in enumerate(lines, start=1):
        if len(line) > MAX_LINE_LENGTH:
            out.append(Violation(
                file=f, line=i, col=MAX_LINE_LENGTH + 1, rule="C-F3",
                message=f"{len(line)}-character line", severity=Severity.MAJOR
            ))
    if content and not content.endswith("\n"):
        out.append(Violation(
            file=f, line=len(lines), col=len(lines[-1]) + 1, rule="C-A3",
            message="file not ending with a newline", severity=Severity.INFO
        ))
    return out


def _check_indentation(lines: list, f: str) -> list[Violation]:
    out = []
    for i, line in enumerate(lines, start=1):
        indent = line[:len(line) - len(line.lstrip(" \t"))]
        if "\t" in indent:
            out.append(Violation(
                file=f, line=i, col=indent.index("\t") + 1,
                rule="C-L2", message="tab used for indentation",
                severity=Severity.MINOR
            ))
        elif len(indent) % 4 != 0:
            out.append(Violation(
                file=f, line=i, col=1, rule="C-L2",
                message="indentation not done with groups of 4 spaces",
                severity=Severity.MINOR
            ))
    return out
