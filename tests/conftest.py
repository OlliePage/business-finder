"""
Pytest configuration file for shared fixtures and configuration.
"""

import pytest


def pytest_configure(config):
    """Configure pytest for our project."""
    # Add project-specific markers here if needed
    config.addinivalue_line(
        "markers", "integration: mark a test as an integration test"
    )
    config.addinivalue_line("markers", "api: mark a test that uses external APIs")


@pytest.fixture
def mock_api_key():
    """Return a mock API key for testing."""
    return "test_api_key_12345"
