# File: business_finder/api/geocoding.py
import requests


def geocode_address(address, api_key):
    """
    Convert a street address or location name to geographic coordinates
    
    Args:
        address (str): The address or location name to geocode
        api_key (str): Google Maps API key
        
    Returns:
        dict: Dictionary containing latitude and longitude, or None if geocoding failed
    """
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': address,
            'key': api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] == 'OK' and len(data['results']) > 0:
            location = data['results'][0]['geometry']['location']
            return {
                'latitude': location['lat'],
                'longitude': location['lng'],
                'formatted_address': data['results'][0]['formatted_address']
            }
        else:
            print(f"Geocoding failed with status: {data['status']}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error during geocoding: {e}")
        return None