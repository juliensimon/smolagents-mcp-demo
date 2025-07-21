#!/bin/bash

# Setup script for pre-commit hooks

echo "Installing pre-commit hooks..."

# Install pre-commit
pip install pre-commit

# Install the git hook scripts
pre-commit install

# Run pre-commit on all files to ensure they're formatted correctly
echo "Running pre-commit on all files..."
pre-commit run --all-files

echo "Pre-commit setup complete!"
echo ""
echo "The following hooks are now active:"
echo "- trailing-whitespace: Removes trailing whitespace"
echo "- end-of-file-fixer: Ensures files end with a newline"
echo "- check-yaml: Validates YAML files"
echo "- check-added-large-files: Prevents large files from being committed"
echo "- check-merge-conflict: Detects merge conflict markers"
echo "- debug-statements: Finds debug statements (pdb, etc.)"
echo "- black: Formats Python code"
echo "- isort: Sorts Python imports"
echo "- flake8: Lints Python code"
echo "- mypy: Type checks Python code"
echo ""
echo "These hooks will run automatically on every commit."
