# Mock response data for tests

MOCK_PLACE_SEARCH_RESPONSE = {
    "results": [
        {
            "name": "Test Business 1",
            "place_id": "place123",
            "vicinity": "123 Test Street"
        },
        {
            "name": "Test Business 2",
            "place_id": "place456",
            "vicinity": "456 Test Avenue"
        }
    ],
    "status": "OK"
}

MOCK_PLACE_DETAILS_RESPONSE = {
    "result": {
        "name": "Test Business 1",
        "place_id": "place123",
        "formatted_address": "123 Test Street, Test City, TC 12345",
        "formatted_phone_number": "(123) 456-7890",
        "website": "https://testbusiness1.com",
        "rating": 4.5,
        "user_ratings_total": 100,
        "opening_hours": {
            "open_now": True
        }
    },
    "status": "OK"
}

MOCK_BUSINESS_DATA = [
    {
        "name": "Test Business 1",
        "address": "123 Test Street, Test City, TC 12345",
        "phone": "(123) 456-7890",
        "website": "https://testbusiness1.com",
        "rating": 4.5,
        "total_ratings": 100,
        "is_open_now": "Yes",
        "place_id": "place123"
    },
    {
        "name": "Test Business 2",
        "address": "456 Test Avenue, Test City, TC 12345",
        "phone": "(987) 654-3210",
        "website": "https://testbusiness2.com",
        "rating": 3.8,
        "total_ratings": 50,
        "is_open_now": "No",
        "place_id": "place456"
    }
]