#!/bin/bash

# IZA OS CLI Alias Setup Script
# This script sets up convenient aliases for the IZA OS CLI

IZA_HOME="/Users/divinejohns/memU/iza-os-production"
SHELL_RC=""

# Detect shell
if [[ $SHELL == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ $SHELL == *"bash"* ]]; then
    SHELL_RC="$HOME/.bashrc"
else
    echo "Unsupported shell. Please add the alias manually."
    exit 1
fi

echo "🧠 Setting up IZA OS CLI aliases..."

# Create the alias command
ALIAS_CMD="alias iza='cd $IZA_HOME && PYTHONPATH=$IZA_HOME python src/cli.py'"

# Check if alias already exists
if grep -q "alias iza=" "$SHELL_RC" 2>/dev/null; then
    echo "⚠️  IZA alias already exists in $SHELL_RC"
    echo "Please check your shell configuration file manually."
else
    echo "# IZA OS CLI Alias" >> "$SHELL_RC"
    echo "$ALIAS_CMD" >> "$SHELL_RC"
    echo "✅ Added IZA alias to $SHELL_RC"
fi

echo ""
echo "🚀 Setup complete! To use IZA OS:"
echo "1. Restart your terminal or run: source $SHELL_RC"
echo "2. Then you can use:"
echo "   iza                  # Show help"
echo "   iza start           # Start IZA OS"
echo "   iza tui             # Launch interactive dashboard"
echo "   iza brief           # Get daily executive brief"
echo "   iza scan            # Scan for problems"
echo "   iza venture list    # List ventures"
echo ""
echo "🧠 Your AI CEO is ready to build your empire!"
