# Running CI Locally

This guide will help you run CI checks locally before pushing to GitHub.

## Prerequisites

- Python 3.9 or higher
- Poetry (for dependency management)
- Git

## Automated CI Check

The easiest way to run all CI checks is to use the provided script:

```bash
# Make the script executable (if it isn't already)
chmod +x scripts/run_ci.sh

# Run the CI checks
./scripts/run_ci.sh
```

This script will:
1. Install dependencies using Poetry
2. Run linting checks (flake8, black, isort)
3. Run unit tests
4. Run coverage analysis

## Manual CI Checks

You can also run each check manually:

### 1. Install dependencies

```bash
poetry install
```

### 2. Run Linting Checks

```bash
# Run flake8
poetry run flake8 business_finder tests

# Run black
poetry run black --check business_finder tests

# Run isort
poetry run isort --check-only --profile black business_finder tests
```

### 3. Run tests

```bash
# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=business_finder --cov-branch --cov-report=term
```

## Fixing Issues

### Formatting Issues

If black or isort checks fail, you can automatically fix them:

```bash
# Format code with black
poetry run black business_finder tests

# Sort imports with isort
poetry run isort business_finder tests
```

### Flake8 Issues

Flake8 issues need to be fixed manually. The error messages will indicate the file, line number, and nature of the problem.

## Pre-commit Hook (Optional)

You can set up a pre-commit hook to run these checks automatically before each commit:

1. Create a file at `.git/hooks/pre-commit`:

```bash
#!/bin/bash
./scripts/run_ci.sh
```

2. Make it executable:

```bash
chmod +x .git/hooks/pre-commit
```

## GitHub Actions

The CI checks that run in GitHub Actions are defined in the `.github/workflows/python-ci.yml` file. This workflow includes:

1. **Linting job**: Runs flake8, black, and isort checks
2. **Test job**: Runs pytest on multiple Python versions and uploads coverage reports

These closely match the local checks described above.