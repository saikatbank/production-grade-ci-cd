#!/bin/bash
# CI/CD Linting and Formatting Script
# This script will exit with a non-zero status code if any checks fail,
# which will properly fail the CI/CD pipeline.

set -e

echo "Running Black formatting check..."
# black --check fails if files need formatting
black app/ tests/ --check

echo "Running Ruff linting check..."
# ruff check fails if linting errors are found
ruff check app/ tests/

echo "Success! All linting and formatting checks passed."
