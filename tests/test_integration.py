import pytest
import os
import tempfile
import shutil
import json
from unittest.mock import patch, MagicMock
import requests

from business_finder.api.places import search_places, get_place_details
from business_finder.exporters.csv_exporter import write_to_csv
from business_finder.exporters.json_exporter import write_to_json
from tests.fixtures.mock_responses import MOCK_PLACE_SEARCH_RESPONSE, MOCK_PLACE_DETAILS_RESPONSE, MOCK_BUSINESS_DATA


class TestIntegration:
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        # Create a temporary directory for test output files
        self.test_dir = tempfile.mkdtemp()
        self.csv_file = os.path.join(self.test_dir, 'test_businesses.csv')
        self.json_file = os.path.join(self.test_dir, 'test_businesses.json')
        
        # Provide the fixture
        yield
        
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)
    
    @patch('business_finder.api.places.time.sleep')  # Mock sleep to speed up tests
    @patch('business_finder.api.places.requests.get')
    def test_search_and_export_workflow(self, mock_get, mock_sleep):
        # Setup mock responses for search and details
        search_response = MagicMock()
        search_response.json.return_value = MOCK_PLACE_SEARCH_RESPONSE
        
        details_response = MagicMock()
        details_response.json.return_value = MOCK_PLACE_DETAILS_RESPONSE
        
        # Configure mock to return different responses based on URL
        def mock_get_side_effect(url, **kwargs):
            if 'nearbysearch' in url:
                return search_response
            elif 'details' in url:
                return details_response
            return MagicMock()
        
        mock_get.side_effect = mock_get_side_effect
        
        # 1. Search for businesses
        businesses = search_places('test_api_key', 'cafe', 37.7749, -122.4194, 1000)
        
        # Verify we got some results
        assert len(businesses) > 0
        assert businesses[0]['name'] == 'Test Business 1'
        
        # 2. Export to CSV
        csv_result = write_to_csv(businesses, self.csv_file)
        assert csv_result is True
        assert os.path.exists(self.csv_file)
        
        # 3. Export to JSON
        json_result = write_to_json(businesses, self.json_file)
        assert json_result is True
        assert os.path.exists(self.json_file)
        
        # Verify content of the JSON file
        with open(self.json_file, 'r') as f:
            data = json.load(f)
            assert data[0]['name'] == 'Test Business 1'
    
    @patch('business_finder.api.places.requests.get')
    def test_error_handling_workflow(self, mock_get):
        # Test error handling in the search workflow
        
        # 1. Test connection error
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        businesses = search_places('test_api_key', 'cafe', 37.7749, -122.4194, 1000)
        assert businesses == []
        
        # 2. Test HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.side_effect = None
        mock_get.return_value = mock_response
        
        businesses = search_places('test_api_key', 'cafe', 37.7749, -122.4194, 1000)
        assert businesses == []
        
        # 3. Test empty response
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = None
        mock_response.json.return_value = {"status": "ZERO_RESULTS", "results": []}
        mock_get.return_value = mock_response
        
        businesses = search_places('test_api_key', 'cafe', 37.7749, -122.4194, 1000)
        assert businesses == []