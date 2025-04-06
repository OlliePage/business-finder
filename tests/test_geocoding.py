import pytest
from unittest.mock import patch, MagicMock
import requests

from business_finder.api.geocoding import geocode_address


class TestGeocoding:
    
    @patch('business_finder.api.geocoding.requests.get')
    def test_geocode_address_success(self, mock_get):
        # Set up mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "OK",
            "results": [
                {
                    "formatted_address": "San Francisco, CA, USA",
                    "geometry": {
                        "location": {
                            "lat": 37.7749,
                            "lng": -122.4194
                        }
                    }
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Call the function
        result = geocode_address("San Francisco", "test_api_key")
        
        # Verify the result
        assert result is not None
        assert result['latitude'] == 37.7749
        assert result['longitude'] == -122.4194
        assert result['formatted_address'] == "San Francisco, CA, USA"
        
        # Verify request parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs['params']['address'] == 'San Francisco'
        assert kwargs['params']['key'] == 'test_api_key'
    
    @patch('business_finder.api.geocoding.requests.get')
    def test_geocode_address_no_results(self, mock_get):
        # Set up mock response with no results
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "ZERO_RESULTS",
            "results": []
        }
        mock_get.return_value = mock_response
        
        # Call the function
        result = geocode_address("NonexistentPlace12345", "test_api_key")
        
        # Verify the result is None
        assert result is None
    
    @patch('business_finder.api.geocoding.requests.get')
    def test_geocode_address_request_exception(self, mock_get):
        # Set up mock to raise exception
        mock_get.side_effect = requests.exceptions.RequestException("Test error")
        
        # Call the function
        result = geocode_address("San Francisco", "test_api_key")
        
        # Verify result is None
        assert result is None
    
    @patch('business_finder.api.geocoding.requests.get')
    def test_geocode_address_api_error(self, mock_get):
        # Set up mock response with API error
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "REQUEST_DENIED",
            "error_message": "API key not valid"
        }
        mock_get.return_value = mock_response
        
        # Call the function
        result = geocode_address("San Francisco", "invalid_api_key")
        
        # Verify the result is None
        assert result is None