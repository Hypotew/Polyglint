# Polyglint

Universal code style enforcer for Python, JavaScript, and Lua — inspired by Epitech's Banana checker.

Polyglint enforces a consistent set of style rules across all your files and reports violations in a unified, readable format.

---

## Installation

Install `pipx` if not already present, then download the latest release from the [Releases page](https://github.com/Hypotew/Polyglint/releases) and run the installer:

```bash
sudo apt install pipx
tar -xzf polyglint-*.tar.gz
cd polyglint-*/
./install.sh
source ~/.zshrc  # or ~/.bashrc — then polyglint is available globally
```

## Usage

```bash
# Check current directory
polyglint .

# Check specific files or directories
polyglint src/ main.py
```

> The `tests/` directory is excluded from checks by default, along with `.git`, `__pycache__`, `node_modules`, and `.venv`.

## Output

```
src/main.py:3:1: warning: [Polyglint] [Minor] leading empty line (C-G8)
  3 |
    | ^
src/main.py:42:81: warning: [Polyglint] [Major] 95-character line (C-F3)
  42 | x = some_very_long_line...
     |                                                                                 ^

2 warnings generated.
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
| C-F8 | No inline comments inside functions | Minor |
| C-L2 | Indentation must use 4 spaces, no tabs | Minor |
| C-L3 | No space before closing parenthesis | Minor |
| C-A3 | File must end with a newline | Info |

### Python

| Code | Description | Severity |
|------|-------------|----------|
| C-F2 | Function names must be `snake_case` and at least 3 characters | Minor |
| C-F4 | Function body must not exceed 20 lines | Major |
| C-F5 | Functions must not have more than 4 parameters | Major |
| C-O3 | Max 10 functions per file (max 5 non-static) | Major |

### JavaScript

| Code | Description | Severity |
|------|-------------|----------|
| C-F2 | Function names must be `snake_case` and at least 3 characters | Minor |
| C-F5 | Functions must not have more than 4 parameters | Major |
| C-O3 | Max 10 functions per file | Major |

### Lua

| Code | Description | Severity |
|------|-------------|----------|
| C-F2 | Function names must be `snake_case` and at least 3 characters | Minor |
| C-F5 | Functions must not have more than 4 parameters | Major |
| C-O3 | Max 10 functions per file | Major |

---

## Uninstall

```bash
pipx uninstall polyglint
```

---

## License

Apache License 2.0
