# File: business_finder/api/places.py
import time
import math
import itertools
import concurrent.futures
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import threading

import requests

# Configure logging
logger = logging.getLogger("business_finder")
logger.setLevel(logging.INFO)

# In-memory log capture for web display
class LogCapture:
    def __init__(self):
        self.logs = []
        self.lock = threading.Lock()
        
    def add_log(self, level: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Add a log entry with timestamp, level, message, and optional details"""
        timestamp = datetime.now().isoformat()
        with self.lock:
            self.logs.append({
                "timestamp": timestamp,
                "level": level,
                "message": message,
                "details": details
            })
            
    def get_logs(self) -> List[Dict[str, Any]]:
        """Get all captured logs"""
        with self.lock:
            return self.logs.copy()
            
    def clear_logs(self):
        """Clear all captured logs"""
        with self.lock:
            self.logs.clear()

# Create a global log capture instance
log_capture = LogCapture()


def get_place_details(place_id, api_key):
    """Fetch detailed information about a specific place"""
    try:
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "name,rating,website,formatted_address,formatted_phone_number,opening_hours,user_ratings_total,types,business_status,price_level",
            "key": api_key,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        result = response.json().get("result", {})
        return result

    except requests.exceptions.RequestException as e:
        print(f"Error fetching details for place {place_id}: {e}")
        return None


def generate_grid_points(center_lat, center_lng, radius, sub_radius=5000):
    """
    Generate a grid of points to cover a large radius with smaller sub-radius searches
    
    Args:
        center_lat: Center latitude in decimal degrees
        center_lng: Center longitude in decimal degrees
        radius: The search radius in meters
        sub_radius: The sub-search radius in meters (default: 5000m = 5km)
        
    Returns:
        List of (lat, lng) points forming a grid to cover the search area
    """
    # Earth's radius in meters
    EARTH_RADIUS = 6378137

    # If the radius is small enough, just return the center point
    if radius <= sub_radius:
        return [(center_lat, center_lng)]

    # Calculate grid dimensions
    # We'll create a rectangular grid that covers the circular area
    # The number of grid points needed depends on the ratio of the radius to the sub_radius
    # We multiply by 1.2 to ensure we cover the entire circle
    grid_radius = 1.2 * radius
    grid_size = math.ceil(grid_radius / sub_radius)

    points = []
    
    # Convert meters to degrees (approximate)
    # 1 degree of latitude is approximately 111,111 meters
    lat_offset = sub_radius / 111111
    
    # 1 degree of longitude depends on the latitude
    # cos(lat) * 111,111 meters
    lng_offset = sub_radius / (111111 * math.cos(math.radians(center_lat)))
    
    # Generate grid points
    for i in range(-grid_size, grid_size + 1):
        for j in range(-grid_size, grid_size + 1):
            lat = center_lat + (i * lat_offset)
            lng = center_lng + (j * lng_offset)
            
            # Calculate distance from center to this point
            dx = (lng - center_lng) * 111111 * math.cos(math.radians(center_lat))
            dy = (lat - center_lat) * 111111
            distance = math.sqrt(dx*dx + dy*dy)
            
            # If point is within the original search radius, add it
            if distance <= radius:
                points.append((lat, lng))
    
    # If we didn't generate any points, return at least the center
    if not points:
        points.append((center_lat, center_lng))
        
    return points


def search_places_single(api_key, search_term, latitude, longitude, radius):
    """
    Search for places matching the criteria and fetch their details for a single point
    This is the original search implementation, renamed to be used as a building block
    """
    businesses = []
    page_token = None

    while True:
        try:
            # Set up the request parameters
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": f"{latitude},{longitude}",
                "radius": radius,
                "key": api_key,
            }
            
            # Check if search_term is a place type (contains no spaces and uses underscores)
            # If it looks like a place type, use it as a type parameter instead of keyword
            if search_term and "_" in search_term and " " not in search_term:
                params["type"] = search_term
                print(f"Searching for places with type: {search_term}")
                log_capture.add_log("INFO", f"Searching by place type: {search_term}")
            else:
                # Otherwise, use it as a keyword search
                params["keyword"] = search_term

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

                    # Get primary and secondary types
                    place_types = details.get("types", [])
                    primary_type = place_types[0] if place_types else "N/A"
                    secondary_types = place_types[1:] if len(place_types) > 1 else []
                    
                    # Get business status and price level
                    business_status = details.get("business_status", "N/A")
                    price_level = details.get("price_level", "N/A")
                    
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
                            "primary_type": primary_type,
                            "secondary_types": secondary_types,
                            "business_status": business_status,
                            "price_level": price_level
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


def get_search_logs():
    """Get the captured logs from the most recent search operation"""
    return log_capture.get_logs()


def search_places(api_key, search_term, latitude, longitude, radius, sub_radius=3000, max_workers=5):
    """
    Search for places matching criteria using a grid-based approach for large radii
    
    Args:
        api_key: Google Places API key
        search_term: Keyword to search for
        latitude: Central latitude for the search
        longitude: Central longitude for the search
        radius: Search radius in meters
        sub_radius: Sub-radius to use for each grid point search (default: 3000m)
        max_workers: Maximum number of concurrent searches (default: 5)
        
    Returns:
        List of businesses found in the search area, deduplicated
    """
    # Clear previous logs
    log_capture.clear_logs()
    
    # Log the search start
    search_params = {
        "search_term": search_term,
        "latitude": latitude,
        "longitude": longitude,
        "radius": radius,
        "sub_radius": sub_radius,
        "max_workers": max_workers
    }
    
    log_capture.add_log(
        "INFO", 
        f"Starting search for '{search_term}' within {radius}m of [{latitude}, {longitude}]",
        search_params
    )
    
    logger.info(f"Starting search for '{search_term}' within {radius}m of [{latitude}, {longitude}]")
    start_time = time.time()
    
    # For small radii, just do a regular search
    if radius <= sub_radius:
        log_msg = f"Using standard search with radius {radius}m"
        print(log_msg)
        log_capture.add_log("INFO", log_msg)
        
        results = search_places_single(api_key, search_term, latitude, longitude, radius)
        
        # Log search completion
        duration = time.time() - start_time
        log_capture.add_log(
            "INFO", 
            f"Search completed in {duration:.2f} seconds. Found {len(results)} businesses.",
            {"duration": duration, "count": len(results)}
        )
        
        return results
    
    # For large radii, generate a grid of points and search each one
    grid_points = generate_grid_points(latitude, longitude, radius, sub_radius)
    point_count = len(grid_points)
    
    log_msg = f"Breaking search into {point_count} sub-searches with {sub_radius}m radius each"
    print(log_msg)
    log_capture.add_log(
        "INFO", 
        log_msg,
        {
            "grid_points": point_count,
            "sub_radius": sub_radius,
            "main_radius": radius
        }
    )
    
    # Log grid generation details
    grid_points_data = [{"lat": p[0], "lng": p[1]} for p in grid_points]
    log_capture.add_log(
        "DEBUG", 
        f"Generated {len(grid_points)} grid points",
        {"points": grid_points_data}
    )
    
    # Limit the sub-radius to the maximum allowed by the API (50000m)
    effective_sub_radius = min(sub_radius, 50000)
    
    all_businesses = []
    seen_place_ids = set()
    
    # Log parallel worker information
    log_capture.add_log(
        "INFO", 
        f"Using {max_workers} parallel workers for grid search",
        {"max_workers": max_workers}
    )
    
    # Use ThreadPoolExecutor to run searches in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create a list of future objects
        future_to_point = {
            executor.submit(
                search_places_single, 
                api_key, 
                search_term, 
                point[0], 
                point[1], 
                effective_sub_radius
            ): point for point in grid_points
        }
        
        completed_points = 0
        
        # Process the results as they complete
        for future in concurrent.futures.as_completed(future_to_point):
            point = future_to_point[future]
            completed_points += 1
            progress_pct = (completed_points / point_count) * 100
            
            try:
                sub_results = future.result()
                unique_count_before = len(seen_place_ids)
                
                # Deduplicate based on place_id
                new_results = []
                for business in sub_results:
                    place_id = business.get("place_id")
                    if place_id and place_id not in seen_place_ids:
                        seen_place_ids.add(place_id)
                        all_businesses.append(business)
                        new_results.append(business)
                
                # Calculate how many unique businesses were found
                new_unique = len(seen_place_ids) - unique_count_before
                duplicates = len(sub_results) - new_unique
                
                log_msg = (f"Point {point}: Found {len(sub_results)} results "
                           f"({new_unique} unique, {duplicates} duplicates). "
                           f"Progress: {progress_pct:.1f}%")
                print(log_msg)
                
                log_capture.add_log(
                    "INFO", 
                    log_msg,
                    {
                        "point": {"lat": point[0], "lng": point[1]},
                        "results_found": len(sub_results),
                        "unique_results": new_unique,
                        "duplicates": duplicates,
                        "progress": progress_pct,
                        "completed": completed_points,
                        "total_points": point_count
                    }
                )
            except Exception as e:
                error_msg = f"Error processing point {point}: {e}"
                print(error_msg)
                log_capture.add_log(
                    "ERROR", 
                    error_msg,
                    {"point": {"lat": point[0], "lng": point[1]}, "error": str(e)}
                )
    
    # Log search completion
    duration = time.time() - start_time
    final_msg = f"Total unique businesses found: {len(all_businesses)} in {duration:.2f} seconds"
    print(final_msg)
    
    log_capture.add_log(
        "INFO", 
        final_msg,
        {
            "total_businesses": len(all_businesses),
            "duration": duration,
            "search_params": search_params
        }
    )
    
    return all_businesses
