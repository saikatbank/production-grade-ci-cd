#!/bin/bash
# Auto-format and auto-fix script for local development

set -e

echo "Running Black formatting..."
black app/ tests/

echo "Running Ruff autofix..."
ruff check app/ tests/ --fix

echo "Success! All files formatted and linted."
