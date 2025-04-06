import csv
import json
import os
import shutil
import tempfile
from unittest.mock import MagicMock, mock_open, patch

import pytest

from business_finder.exporters.csv_exporter import write_to_csv
from business_finder.exporters.json_exporter import write_to_json
from tests.fixtures.mock_responses import MOCK_BUSINESS_DATA


class TestCSVExporter:

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_output.csv")

        # Provide the fixture
        yield

        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def test_write_to_csv_success(self):
        # Test writing to CSV
        result = write_to_csv(MOCK_BUSINESS_DATA, self.test_file)

        # Verify the function returns True
        assert result is True

        # Verify the file was created
        assert os.path.exists(self.test_file)

        # Read the CSV file and verify contents
        with open(self.test_file, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            # Check that we have the right number of rows
            assert len(rows) == 2

            # Verify data in first row
            assert rows[0]["name"] == "Test Business 1"
            assert rows[0]["address"] == "123 Test Street, Test City, TC 12345"
            assert rows[0]["phone"] == "(123) 456-7890"
            assert rows[0]["rating"] == "4.5"

    def test_write_to_csv_empty_data(self):
        # Test with empty business list
        result = write_to_csv([], self.test_file)

        # Verify the function returns False
        assert result is False

        # File should not be created
        assert not os.path.exists(self.test_file)

    @patch("builtins.open")
    def test_write_to_csv_io_error(self, mock_open_func):
        # Mock open to raise IOError
        mock_open_func.side_effect = IOError("Test IO error")

        # Call the function
        result = write_to_csv(MOCK_BUSINESS_DATA, self.test_file)

        # Verify the function returns False
        assert result is False


class TestJSONExporter:

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_output.json")

        # Provide the fixture
        yield

        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def test_write_to_json_success(self):
        # Test writing to JSON
        result = write_to_json(MOCK_BUSINESS_DATA, self.test_file)

        # Verify the function returns True
        assert result is True

        # Verify the file was created
        assert os.path.exists(self.test_file)

        # Read the JSON file and verify contents
        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)

            # Check that we have the right number of entries
            assert len(data) == 2

            # Verify data in entries
            assert data[0]["name"] == "Test Business 1"
            assert data[0]["address"] == "123 Test Street, Test City, TC 12345"
            assert data[1]["name"] == "Test Business 2"
            assert data[1]["website"] == "https://testbusiness2.com"

    def test_write_to_json_empty_data(self):
        # Test with empty business list
        result = write_to_json([], self.test_file)

        # Verify the function returns False
        assert result is False

        # File should not be created
        assert not os.path.exists(self.test_file)

    @patch("builtins.open")
    def test_write_to_json_io_error(self, mock_open_func):
        # Mock open to raise IOError
        mock_open_func.side_effect = IOError("Test IO error")

        # Call the function
        result = write_to_json(MOCK_BUSINESS_DATA, self.test_file)

        # Verify the function returns False
        assert result is False
