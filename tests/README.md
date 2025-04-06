# Business Finder Tests

This directory contains the test suite for the Business Finder application. The tests cover the API interactions, CLI functionality, configuration handling, exporters, and integration tests.

## Test Coverage

The test suite provides around 97% code coverage for the entire application:

- API modules: 100% coverage
- CLI module: 91% coverage
- Config module: 93% coverage
- Exporters: 100% coverage

## Continuous Integration

These tests are automatically run as part of the CI/CD pipeline using GitHub Actions. For each push and pull request, the test suite is executed on multiple Python versions to ensure compatibility. Test coverage is tracked using Codecov, which helps maintain the high code coverage standards.

## Running Tests

### Using pytest

To run all tests:

```bash
# Install pytest if not already installed
pip install pytest pytest-cov

# Run all tests
pytest

# Run a specific test file
pytest tests/test_api.py

# Run a specific test class
pytest tests/test_api.py::TestPlacesAPI

# Run a specific test method
pytest tests/test_api.py::TestPlacesAPI::test_get_place_details_success
```

### Using Coverage

To run tests with coverage analysis:

```bash
# Install pytest-cov if not already installed
pip install pytest-cov

# Run tests with coverage
pytest --cov=business_finder --cov-branch

# Generate detailed coverage report
pytest --cov=business_finder --cov-branch --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=business_finder --cov-branch --cov-report=html
```

The HTML report will be generated in the `htmlcov` directory.

### Continuous Integration

These tests are automatically run via GitHub Actions in the CI/CD pipeline, and coverage is tracked by Codecov.

## Test Structure

- `test_api.py`: Tests for the places and geocoding API functions
- `test_cli.py`: Tests for the command-line interface
- `test_config.py`: Tests for the configuration management
- `test_exporters.py`: Tests for CSV and JSON exporters
- `test_geocoding.py`: Tests for the geocoding functionality
- `test_integration.py`: Integration tests that test multiple components together

## Fixtures

Test fixtures are located in the `fixtures` directory:

- `mock_responses.py`: Contains mock API responses and test data

## Adding New Tests

When adding new functionality to the application, please also add corresponding tests to maintain high test coverage. Follow these guidelines:

1. Create a test class that inherits from `unittest.TestCase`
2. Use descriptive test method names that start with `test_`
3. Use mock objects when testing external API calls
4. Consider adding both unit tests and integration tests