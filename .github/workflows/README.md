# GitHub Actions Workflows

This directory contains GitHub Actions workflow configurations for continuous integration and delivery (CI/CD) of the Business Finder project.

## Workflow Files

### `python-tests.yml`

This workflow runs the test suite on multiple Python versions to ensure compatibility.

**Triggered by:**
- Push to `master` branch
- Pull requests to `master` branch

**Jobs:**
- **test**: Runs the test suite on Python 3.9, 3.10, and 3.11
  - Installs Poetry
  - Installs dependencies
  - Runs unittest
  - Runs coverage analysis
  - Uploads coverage data to Codecov

### `python-lint.yml`

This workflow runs code quality checks to maintain consistent style and detect issues.

**Triggered by:**
- Push to `master` branch
- Pull requests to `master` branch

**Jobs:**
- **lint**: Runs various code quality tools
  - flake8: Checks for syntax errors and code smells
  - black: Verifies that code is formatted according to the project's style
  - isort: Checks that imports are properly organized

### `python-publish.yml`

This workflow builds and publishes the package to PyPI when a new release is created.

**Triggered by:**
- Creating a new release in GitHub

**Jobs:**
- **deploy**: Publishes the package
  - Runs tests to verify the package
  - Builds the package with Poetry
  - Publishes to PyPI using the provided token

## Setting Up Secrets

For the publish workflow to work, you need to set up a PyPI API token as a GitHub secret:

1. Create an API token on PyPI (https://pypi.org/manage/account/token/)
2. Go to your GitHub repository settings
3. Navigate to Secrets and Variables > Actions
4. Create a new repository secret named `PYPI_TOKEN` with your PyPI token as the value

## Badge Status

You can add the following badges to your README to show the status of your CI/CD workflows:

```markdown
[![Python Tests](https://github.com/user/business-finder/actions/workflows/python-tests.yml/badge.svg)](https://github.com/user/business-finder/actions/workflows/python-tests.yml)
[![Python Linting](https://github.com/user/business-finder/actions/workflows/python-lint.yml/badge.svg)](https://github.com/user/business-finder/actions/workflows/python-lint.yml)
[![codecov](https://codecov.io/gh/user/business-finder/branch/master/graph/badge.svg)](https://codecov.io/gh/user/business-finder)
```

## Customizing Workflows

To customize these workflows:

1. Edit the respective YAML file
2. Commit and push the changes to GitHub
3. GitHub will automatically use the updated workflow configuration

For more information on GitHub Actions, see the [official documentation](https://docs.github.com/en/actions).