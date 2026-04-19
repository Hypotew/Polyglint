# Polyglint

Universal code style enforcer for Python, JavaScript, and Lua — inspired by Epitech's Banana checker.

Polyglint enforces a consistent set of style rules across all your files and reports violations in a unified, readable format.

---

## Installation

```bash
git clone https://github.com/Hypotew/Polyglint.git
cd Polyglint
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
# Check current directory
polyglint .

# Check specific files or directories
polyglint src/ main.py
```

## Output

```
src/main.py
  line 3,  col 1    [C-G8]  leading empty line
  line 42, col 81   [C-F3]  95-character line
  line 78, col 1    [C-F2]  non-snake-case function name

2 major, 1 minor in 1 file
```

---

## Rules enforced

### Generic — all languages

| Code | Description | Severity |
|------|-------------|----------|
| C-G6 | No `\r` line endings | Minor |
| C-G7 | No trailing whitespace | Minor |
| C-G8 | No leading or trailing empty lines | Minor |
| C-F3 | Max 80 columns per line | Major |
| C-L2 | Indentation must use 4 spaces, no tabs | Minor |
| C-A3 | File must end with a newline | Info |

### Python

| Code | Description | Severity |
|------|-------------|----------|
| C-F2 | Function names must be `snake_case` and at least 3 characters | Minor |
| C-F4 | Function body must not exceed 20 lines | Major |
| C-F5 | Functions must not have more than 4 parameters | Major |
| C-O3 | Max 10 functions per file (max 5 non-static) | Major |

---

## License

Apache License 2.0
