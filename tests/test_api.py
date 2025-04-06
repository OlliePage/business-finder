import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from business_finder.api.places import get_place_details, search_places
from tests.fixtures.mock_responses import (
    MOCK_PLACE_DETAILS_RESPONSE,
    MOCK_PLACE_SEARCH_RESPONSE,
)


class TestPlacesAPI:

    @patch("business_finder.api.places.requests.get")
    def test_get_place_details_success(self, mock_get):
        # Set up mock response
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_PLACE_DETAILS_RESPONSE
        mock_get.return_value = mock_response

        # Call the function
        result = get_place_details("place123", "test_api_key")

        # Verify the result
        assert result == MOCK_PLACE_DETAILS_RESPONSE["result"]

        # Verify request parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["place_id"] == "place123"
        assert kwargs["params"]["key"] == "test_api_key"

    @patch("business_finder.api.places.requests.get")
    def test_get_place_details_request_exception(self, mock_get):
        # Set up mock to raise exception
        mock_get.side_effect = requests.exceptions.RequestException("Test error")

        # Call the function
        result = get_place_details("place123", "test_api_key")

        # Verify result is None
        assert result is None

    @patch("business_finder.api.places.time.sleep")  # Mock sleep to speed up tests
    @patch("business_finder.api.places.get_place_details")
    @patch("business_finder.api.places.requests.get")
    def test_search_places_success(self, mock_get, mock_get_details, mock_sleep):
        # Set up mock responses
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_PLACE_SEARCH_RESPONSE
        mock_get.return_value = mock_response

        # Setup mock for get_place_details
        mock_get_details.side_effect = [
            {
                "name": "Test Business 1",
                "formatted_address": "123 Test Street, Test City, TC 12345",
                "formatted_phone_number": "(123) 456-7890",
                "website": "https://testbusiness1.com",
                "rating": 4.5,
                "user_ratings_total": 100,
                "opening_hours": {"open_now": True},
            },
            {
                "name": "Test Business 2",
                "formatted_address": "456 Test Avenue, Test City, TC 12345",
                "formatted_phone_number": "(987) 654-3210",
                "website": "https://testbusiness2.com",
                "rating": 3.8,
                "user_ratings_total": 50,
                "opening_hours": {"open_now": False},
            },
        ]

        # Call the function
        result = search_places("test_api_key", "cafe", 37.7749, -122.4194, 1000)

        # Verify the result contains the expected business data
        assert len(result) == 2
        assert result[0]["name"] == "Test Business 1"
        assert result[1]["name"] == "Test Business 2"

        # Verify request parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["location"] == "37.7749,-122.4194"
        assert kwargs["params"]["radius"] == 1000
        assert kwargs["params"]["keyword"] == "cafe"
        assert kwargs["params"]["key"] == "test_api_key"

    @patch("business_finder.api.places.time.sleep")  # Mock sleep to speed up tests
    @patch("business_finder.api.places.requests.get")
    def test_search_places_request_exception(self, mock_get, mock_sleep):
        # Set up mock to raise exception
        mock_get.side_effect = requests.exceptions.RequestException("Test error")

        # Call the function
        result = search_places("test_api_key", "cafe", 37.7749, -122.4194, 1000)

        # Verify result is empty list
        assert result == []

    @patch("business_finder.api.places.time.sleep")  # Mock sleep to speed up tests
    @patch("business_finder.api.places.get_place_details")
    @patch("business_finder.api.places.requests.get")
    def test_search_places_multiple_pages(self, mock_get, mock_get_details, mock_sleep):
        # Create responses for pagination
        first_response = {
            "results": [{"name": "Test Business 1", "place_id": "place123"}],
            "next_page_token": "test_token",
        }
        second_response = {
            "results": [{"name": "Test Business 2", "place_id": "place456"}],
            "status": "OK",
        }

        # Set up mock to return different responses for each call
        mock_response1 = MagicMock()
        mock_response1.json.return_value = first_response

        mock_response2 = MagicMock()
        mock_response2.json.return_value = second_response

        mock_get.side_effect = [mock_response1, mock_response2]

        # Mock place details
        mock_get_details.return_value = {
            "name": "Test Business",
            "formatted_address": "Test Address",
            "rating": 4.0,
        }

        # Call the function
        result = search_places("test_api_key", "cafe", 37.7749, -122.4194, 1000)

        # Verify both pages were processed
        assert len(result) == 2
        assert mock_get.call_count == 2

        # Verify second call included page token
        args, kwargs = mock_get.call_args_list[1]
        assert kwargs["params"]["pagetoken"] == "test_token"
