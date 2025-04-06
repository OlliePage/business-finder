# File: business_finder/api/places.py
import time

import requests


def get_place_details(place_id, api_key):
    """Fetch detailed information about a specific place"""
    try:
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "name,rating,website,formatted_address,formatted_phone_number,opening_hours,user_ratings_total",
            "key": api_key,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        result = response.json().get("result", {})
        return result

    except requests.exceptions.RequestException as e:
        print(f"Error fetching details for place {place_id}: {e}")
        return None


def search_places(api_key, search_term, latitude, longitude, radius):
    """Search for places matching the criteria and fetch their details"""
    businesses = []
    page_token = None

    while True:
        try:
            # Set up the request parameters
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": f"{latitude},{longitude}",
                "radius": radius,
                "keyword": search_term,
                "type": "business",
                "key": api_key,
            }

            # Add page token if we have one
            if page_token:
                params["pagetoken"] = page_token

            # Make the request
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Process results
            results = data.get("results", [])

            # Get details for each place
            for place in results:
                print(f"Fetching details for {place.get('name')}...")
                details = get_place_details(place.get("place_id"), api_key)

                if details:
                    # Extract opening hours if available
                    is_open_now = "N/A"
                    if (
                        "opening_hours" in details
                        and "open_now" in details["opening_hours"]
                    ):
                        is_open_now = (
                            "Yes" if details["opening_hours"]["open_now"] else "No"
                        )

                    businesses.append(
                        {
                            "name": details.get("name", place.get("name", "N/A")),
                            "address": details.get("formatted_address", "N/A"),
                            "phone": details.get("formatted_phone_number", "N/A"),
                            "website": details.get("website", "N/A"),
                            "rating": details.get("rating", "N/A"),
                            "total_ratings": details.get("user_ratings_total", "N/A"),
                            "is_open_now": is_open_now,
                            "place_id": place.get("place_id", "N/A"),
                        }
                    )

                # Respect rate limits - sleep between requests
                time.sleep(0.2)

            # Check if there are more pages of results
            page_token = data.get("next_page_token")

            # If no more results, exit loop
            if not page_token:
                break

            # If we have a page token, wait before making the next request
            time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching places: {e}")
            break

    return businesses
