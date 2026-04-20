import re
from pathlib import Path
from polyglint.violation import Violation, Severity

RESET  = "\033[0m"
RED    = "\033[31m"
YELLOW = "\033[33m"
GREEN  = "\033[32m"
WHITE  = "\033[37m"
PINK   = "\033[95m"
BOLD   = "\033[1m"
BLUE   = "\033[34m"

_KEYWORDS = {
    ".py":  {
        "def", "class", "if", "elif", "else", "for", "while", "return",
        "import", "from", "as", "with", "try", "except", "finally",
        "raise", "pass", "break", "continue", "and", "or", "not", "in",
        "is", "lambda", "yield", "async", "await", "True", "False", "None",
    },
    ".js":  {
        "function", "const", "let", "var", "if", "else", "for", "while",
        "return", "class", "new", "this", "import", "export", "from",
        "async", "await", "try", "catch", "finally", "throw", "break",
        "continue", "switch", "case", "default", "typeof", "instanceof",
        "true", "false", "null", "undefined",
    },
    ".lua": {
        "function", "local", "if", "then", "else", "elseif", "end",
        "for", "while", "do", "repeat", "until", "return", "break",
        "and", "or", "not", "in", "nil", "true", "false",
    },
}

SEVERITY_COLOR = {
    Severity.FATAL: RED,
    Severity.MAJOR: RED,
    Severity.MINOR: YELLOW,
    Severity.INFO:  WHITE,
}

SEVERITY_LABEL = {
    Severity.FATAL: "Fatal",
    Severity.MAJOR: "Major",
    Severity.MINOR: "Minor",
    Severity.INFO:  "Info",
}


def report(results: dict[str, list[Violation]]) -> int:
    if not results:
        print(f"{GREEN}No violations found.{RESET}")
        return 0
    total = _print_violations(results)
    label = "warning" if total == 1 else "warnings"
    print(f"\n{total} {label} generated.")
    return 1


def _print_violations(results: dict) -> int:
    total = 0
    file_cache = {}
    for file, violations in sorted(results.items()):
        lines = _read_lines(file, file_cache)
        for v in sorted(violations, key=lambda x: (x.line, x.col)):
            _print_violation(v, lines)
            total += 1
    return total


def _read_lines(file: str, cache: dict) -> list:
    if file not in cache:
        try:
            cache[file] = Path(file).read_text(encoding="utf-8").splitlines()
        except OSError:
            cache[file] = []
    return cache[file]


def _highlight_keywords(source: str, ext: str) -> str:
    keywords = _KEYWORDS.get(ext, set())
    if not keywords:
        return source
    pattern = r'\b(' + '|'.join(re.escape(k) for k in keywords) + r')\b'
    return re.sub(pattern, lambda m: f"{BLUE}{m.group()}{WHITE}", source)


def _print_violation(v: Violation, lines: list) -> None:
    label = SEVERITY_LABEL.get(v.severity, "Info")
    location = f"{v.file}:{v.line}:{v.col}: "
    rest = f"[Polyglint] [{label}] {v.message} ({v.rule})"
    prefix = f"{BOLD}{WHITE}{location}{PINK}warning:{RESET} "
    print(f"{prefix}{BOLD}{WHITE}{rest}{RESET}")
    if 0 < v.line <= len(lines):
        source = lines[v.line - 1]
        ext = Path(v.file).suffix
        highlighted = _highlight_keywords(source, ext)
        pad = " " * len(str(v.line))
        print(f"  {v.line} | {WHITE}{highlighted}{RESET}")
        print(f"  {pad} | {' ' * (v.col - 1)}{GREEN}^{RESET}")
