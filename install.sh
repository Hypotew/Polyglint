#!/bin/bash

set -e

VENV_DIR=".venv"
SHELL_RC=""

if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

echo "Installing Polyglint..."

python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install -e . --quiet

POLYGLINT_BIN="$(pwd)/$VENV_DIR/bin/polyglint"

if [ -n "$SHELL_RC" ]; then
    if ! grep -q "polyglint" "$SHELL_RC"; then
        echo "" >> "$SHELL_RC"
        echo "# Polyglint" >> "$SHELL_RC"
        echo "alias polyglint='$POLYGLINT_BIN'" >> "$SHELL_RC"
        echo "Alias added to $SHELL_RC — restart your shell or run: source $SHELL_RC"
    fi
fi

echo "Done. Run: polyglint ."
