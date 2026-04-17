# Polyglint

Universal code style enforcer for Python, JavaScript, and Lua — inspired by Epitech's [Banana](https://github.com/Epitech/banana-vera) checker.

Polyglint enforces a consistent set of style rules across all your files, whatever the language, and reports violations in a unified, readable format.

---

## Rules enforced

Rules are categorized by severity: **major**, **minor**, and **info**.

### Generic (all languages)

| Code | Description | Severity |
|------|-------------|----------|
| C-G6 | No `\r` line endings | Minor |
| C-G7 | No trailing whitespace | Minor |
| C-G8 | No leading empty lines / no trailing empty lines | Minor |
| C-F3 | Max 80 columns per line | Major |
| C-L2 | Indentation must use 4 spaces — no tabs | Minor |
| C-A3 | File must end with a newline | Info |

### Python

| Code | Description | Severity |
|------|-------------|----------|
| C-F2 | Function names must be in `snake_case` and at least 3 characters | Minor |
| C-F4 | Function body must not exceed 20 lines | Major |
| C-F5 | Functions must not have more than 4 parameters | Major |

---

## Installation

```bash
git clone https://github.com/Hypotew/Polyglint.git
cd Polyglint
pip install -e .
```

## Usage

```bash
# Check a directory
polyglint .

# Check specific files
polyglint src/main.py src/utils.js
```

## Output

```
src/main.py
  line 3,  col 1   [C-G8]   leading empty line
  line 42, col 81  [C-F3]   95-character line
  line 78, col 1   [C-F2]   non-snake-case function name

2 major, 1 minor in 1 file
```

---

## License

Apache License 2.0
