#!/bin/bash

set -e

SHELL_RC=""

if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

echo "Installing Polyglint..."

if ! command -v pipx &> /dev/null; then
    echo "pipx is required but not installed."
    echo "Install it with: sudo apt install pipx"
    exit 1
fi

pipx install .

if [ -n "$SHELL_RC" ]; then
    if ! grep -q 'HOME/.local/bin' "$SHELL_RC"; then
        echo "" >> "$SHELL_RC"
        echo "# Polyglint" >> "$SHELL_RC"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
        echo "PATH updated in $SHELL_RC — restart your shell or run: source $SHELL_RC"
    fi
fi

echo "Done. Run: polyglint ."
