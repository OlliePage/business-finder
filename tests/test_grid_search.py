"""
Test the grid-based search functionality in the places module.
"""
import pytest
from unittest.mock import patch, MagicMock

from business_finder.api.places import (
    generate_grid_points,
    search_places,
    search_places_single,
    get_search_logs
)


def test_generate_grid_points():
    """Test grid point generation."""
    # Test with small radius (should return just the center point)
    center_lat, center_lng = 51.5074, -0.1278
    small_radius = 1000
    sub_radius = 2000
    
    points = generate_grid_points(center_lat, center_lng, small_radius, sub_radius)
    assert len(points) == 1
    assert points[0] == (center_lat, center_lng)
    
    # Test with large radius (should return multiple points)
    large_radius = 10000
    points = generate_grid_points(center_lat, center_lng, large_radius, sub_radius)
    assert len(points) > 1
    
    # Verify all points are within the search radius
    for point in points:
        lat, lng = point
        # Very rough distance calculation for testing purposes
        lat_diff = abs(lat - center_lat) * 111111  # 1 degree ≈ 111,111 meters
        lng_diff = abs(lng - center_lng) * 111111 * 0.7  # Approximate at this latitude
        distance = (lat_diff**2 + lng_diff**2)**0.5
        assert distance <= large_radius * 1.01  # Allow for small rounding errors
        

@pytest.mark.parametrize("radius,sub_radius,expected_calls", [
    (2000, 3000, 1),   # Small radius, no grid
    (10000, 3000, ">1"),  # Large radius, grid search
])
def test_search_places_radius_comparison(radius, sub_radius, expected_calls, monkeypatch):
    """Test search_places with different radius scenarios."""
    # Setup mock
    mock_search_single = MagicMock()
    mock_search_single.return_value = [{"name": "Test Business", "place_id": "test123"}]
    monkeypatch.setattr('business_finder.api.places.search_places_single', mock_search_single)
    
    # Call search_places
    result = search_places(
        api_key="test_api_key",
        search_term="test",
        latitude=51.5074,
        longitude=-0.1278,
        radius=radius,
        sub_radius=sub_radius,
        max_workers=2
    )
    
    # Verify correct number of calls
    if expected_calls == 1:
        assert mock_search_single.call_count == 1
    else:
        assert mock_search_single.call_count > 1
        
    # Verify we get results
    assert len(result) > 0


def test_search_places_large_radius(monkeypatch):
    """Test search_places with a large radius (grid search)."""
    # Setup mock to return different results for different points
    mock_search_single = MagicMock()
    
    def side_effect(*args, **kwargs):
        lat, lng = args[2], args[3]
        return [{"name": f"Business at {lat:.4f},{lng:.4f}", "place_id": f"id_{lat:.4f}_{lng:.4f}"}]
        
    mock_search_single.side_effect = side_effect
    monkeypatch.setattr('business_finder.api.places.search_places_single', mock_search_single)
    
    # Call with radius larger than sub_radius
    result = search_places(
        api_key="test_api_key",
        search_term="test",
        latitude=51.5074,
        longitude=-0.1278,
        radius=10000,
        sub_radius=3000,
        max_workers=2
    )
    
    # Verify multiple searches were performed
    assert mock_search_single.call_count > 1
    assert len(result) > 1


def test_deduplication(monkeypatch):
    """Test that duplicate results are removed."""
    # Setup mock to return some duplicate place_ids
    mock_search_single = MagicMock()
    calls = 0
    
    def side_effect(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls % 2 == 0:
            # Even calls return a duplicate ID
            return [{"name": "Duplicate", "place_id": "same_id"}]
        else:
            # Odd calls return unique IDs
            return [{"name": f"Unique {calls}", "place_id": f"id_{calls}"}]
        
    mock_search_single.side_effect = side_effect
    monkeypatch.setattr('business_finder.api.places.search_places_single', mock_search_single)
    
    # Call with radius larger than sub_radius to trigger grid search
    result = search_places(
        api_key="test_api_key",
        search_term="test",
        latitude=51.5074,
        longitude=-0.1278,
        radius=10000,
        sub_radius=3000,
        max_workers=2
    )
    
    # Count unique place_ids in the result
    place_ids = [business["place_id"] for business in result]
    unique_ids = set(place_ids)
    
    # Verify no duplicates in results
    assert len(place_ids) == len(unique_ids)
    assert "same_id" in unique_ids  # Verify the duplicate ID is still included once


def test_logging(monkeypatch):
    """Test that search operations are properly logged."""
    # Setup mock
    mock_search_single = MagicMock()
    mock_search_single.return_value = [{"name": "Test", "place_id": "test123"}]
    monkeypatch.setattr('business_finder.api.places.search_places_single', mock_search_single)
    
    # Perform a search
    search_places(
        api_key="test_api_key",
        search_term="test",
        latitude=51.5074,
        longitude=-0.1278,
        radius=10000,
        sub_radius=3000
    )
    
    # Get logs
    logs = get_search_logs()
    
    # Verify logs contain expected entries
    assert len(logs) > 0
    
    # Check for specific log messages
    log_messages = [log["message"] for log in logs]
    assert any("Starting search for" in msg for msg in log_messages)
    assert any("Breaking search into" in msg for msg in log_messages)
    assert any("Total unique businesses found" in msg for msg in log_messages)