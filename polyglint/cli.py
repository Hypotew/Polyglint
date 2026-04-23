# Polyglint CLI
import argparse
import sys
from pathlib import Path
from polyglint.runner import run
from polyglint.reporter import report


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="polyglint",
        description="Universal code style enforcer"
        " for Python, JavaScript, and Lua",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Files or directories to check (default: current directory)",
    )

    args = parser.parse_args()
    paths = [Path(p) for p in args.paths]
    results = run(paths)
    sys.exit(report(results))
