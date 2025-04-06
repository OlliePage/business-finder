#!/bin/bash
# This script runs the CI checks locally to ensure they'll pass in the CI pipeline

set -e  # Exit on error

# Create directory if it doesn't exist
mkdir -p $(dirname "$0")

echo "===> Setting up virtual environment..."
poetry install

echo "===> Running linters..."
echo "==> Flake8..."
poetry run flake8 business_finder tests --count --select=E9,F63,F7,F82 --show-source --statistics
poetry run flake8 business_finder tests --count --max-complexity=10 --max-line-length=120 --statistics

echo "==> Black..."
poetry run black --check business_finder tests

echo "==> isort..."
poetry run isort --check-only --profile black business_finder tests

echo "===> Running tests..."
poetry run pytest

echo "===> Running test coverage..."
poetry run pytest --cov=business_finder --cov-branch --cov-report=term

echo "===> All CI checks passed! 🎉"