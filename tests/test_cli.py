import pytest
from unittest.mock import patch, MagicMock
import sys
import json
import tempfile
import os

from business_finder.cli import main
from tests.fixtures.mock_responses import MOCK_BUSINESS_DATA


class TestCLI:
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        # Create a temporary file for tests
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        
        # Save original sys.argv
        self.original_argv = sys.argv
        
        # Provide the fixture
        yield
        
        # Cleanup
        # Remove temporary file
        os.unlink(self.temp_file.name)
        
        # Restore original sys.argv
        sys.argv = self.original_argv
    
    @patch('business_finder.cli.search_places')
    @patch('business_finder.cli.get_api_key')
    @patch('business_finder.cli.write_to_csv')
    def test_search_command_csv(self, mock_write_csv, mock_get_api_key, mock_search):
        # Set up mocks
        mock_get_api_key.return_value = 'test_api_key'
        mock_search.return_value = MOCK_BUSINESS_DATA
        
        # Set up command line args
        sys.argv = [
            'business-finder', 
            'search', 
            '--search-term', 'cafe', 
            '--latitude', '37.7749', 
            '--longitude', '-122.4194', 
            '--radius', '1000',
            '--output', self.temp_file.name
        ]
        
        # Call the main function
        main()
        
        # Verify search_places was called with correct arguments
        mock_search.assert_called_once_with(
            'test_api_key', 'cafe', 37.7749, -122.4194, 1000
        )
        
        # Verify CSV writer was called with the right arguments
        mock_write_csv.assert_called_once_with(MOCK_BUSINESS_DATA, self.temp_file.name)
    
    @patch('business_finder.cli.search_places')
    @patch('business_finder.cli.get_api_key')
    @patch('business_finder.cli.write_to_json')
    def test_search_command_json(self, mock_write_json, mock_get_api_key, mock_search):
        # Set up mocks
        mock_get_api_key.return_value = 'test_api_key'
        mock_search.return_value = MOCK_BUSINESS_DATA
        
        # Set up command line args
        sys.argv = [
            'business-finder', 
            'search', 
            '--search-term', 'cafe', 
            '--latitude', '37.7749', 
            '--longitude', '-122.4194',
            '--format', 'json',
            '--output', self.temp_file.name
        ]
        
        # Call the main function
        main()
        
        # Verify search_places was called with correct arguments
        mock_search.assert_called_once()
        
        # Verify JSON writer was called with the right arguments
        mock_write_json.assert_called_once_with(MOCK_BUSINESS_DATA, self.temp_file.name)
    
    @patch('business_finder.cli.save_api_key')
    def test_config_command(self, mock_save_api_key):
        # Set up command line args
        sys.argv = [
            'business-finder', 
            'config', 
            '--set-api-key', 'new_api_key'
        ]
        
        # Call the main function
        with pytest.raises(SystemExit) as cm:
            main()
        
        # Verify exit code is 0 (success)
        assert cm.value.code == 0
        
        # Verify save_api_key was called with the right argument
        mock_save_api_key.assert_called_once_with('new_api_key')
    
    def test_no_command(self):
        # Set up command line args without a command
        sys.argv = ['business-finder']
        
        # Call the main function
        with pytest.raises(SystemExit) as cm:
            main()
        
        # Verify exit code is 1 (error)
        assert cm.value.code == 1
    
    @patch('business_finder.cli.get_api_key')
    def test_no_api_key(self, mock_get_api_key, capsys):
        # Set up mock to return None (no API key)
        mock_get_api_key.return_value = None
        
        # Set up command line args
        sys.argv = [
            'business-finder', 
            'search', 
            '--latitude', '37.7749', 
            '--longitude', '-122.4194'
        ]
        
        # Call the main function
        with pytest.raises(SystemExit) as cm:
            main()
        
        # Verify exit code is 1 (error)
        assert cm.value.code == 1
        
        # Verify error message is printed
        captured = capsys.readouterr()
        assert 'API key is required' in captured.out
    
    def test_missing_coordinates(self, capsys):
        # Set up command line args without coordinates
        sys.argv = [
            'business-finder', 
            'search', 
            '--api-key', 'test_api_key'
        ]
        
        # Call the main function
        with pytest.raises(SystemExit) as cm:
            main()
        
        # Verify exit code is 1 (error)
        assert cm.value.code == 1
        
        # Verify error message is printed
        captured = capsys.readouterr()
        assert 'Latitude and longitude are required' in captured.out
    
    @patch('business_finder.cli.search_places')
    @patch('business_finder.cli.get_api_key')
    def test_json_params(self, mock_get_api_key, mock_search):
        # Set up mocks
        mock_get_api_key.return_value = 'test_api_key'
        mock_search.return_value = []
        
        # Set up JSON params
        json_params = json.dumps({
            'search_term': 'restaurant',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'radius': 2000
        })
        
        # Set up command line args
        sys.argv = [
            'business-finder', 
            'search', 
            '--json-params', json_params
        ]
        
        # Call the main function
        main()
        
        # Verify search_places was called with params from JSON
        mock_search.assert_called_once_with(
            'test_api_key', 'restaurant', 40.7128, -74.0060, 2000
        )
    
    @patch('business_finder.cli.search_places')
    @patch('business_finder.cli.get_api_key')
    def test_params_file(self, mock_get_api_key, mock_search):
        # Set up mocks
        mock_get_api_key.return_value = 'test_api_key'
        mock_search.return_value = []
        
        # Create a params file
        params = {
            'search_term': 'hotel',
            'latitude': 51.5074,
            'longitude': -0.1278,
            'radius': 5000
        }
        
        with open(self.temp_file.name, 'w') as f:
            json.dump(params, f)
        
        # Set up command line args
        sys.argv = [
            'business-finder', 
            'search', 
            '--params-file', self.temp_file.name
        ]
        
        # Call the main function
        main()
        
        # Verify search_places was called with params from file
        mock_search.assert_called_once_with(
            'test_api_key', 'hotel', 51.5074, -0.1278, 5000
        )