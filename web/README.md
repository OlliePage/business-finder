# Business Finder Web Interface

This web interface provides a user-friendly way to search for businesses using Google Places API and the Business Finder tool.

## Features

- Interactive map to select search location
- Location search with Google Places autocomplete
- Current location detection
- Adjustable search radius (via slider or direct input)
- Display search results in a table
- CSV export of all results or visible/selected results
- Pagination for large result sets

## Getting Started

### Prerequisites

- Python 3.6+
- Business Finder package installed (from parent directory)
- Google API key configured in your environment
- Google Maps JavaScript API key

### Running the Web Interface

1. Start the server:

```bash
# From the web directory
python server.py

# Optionally specify a port
python server.py 8080
```

2. Open your browser and navigate to:

```
http://localhost:8000
```

### Using the Web Interface

1. Set your search location:
   - Click directly on the map
   - Use the "Current Location" button
   - Search for a location using the search bar

2. Adjust the search radius:
   - Drag the circle on the map
   - Use the slider control
   - Enter a precise value in the input field

3. Enter your search term (e.g., "coffee shop", "restaurant")

4. Click "Search Businesses" to find matching businesses

5. View results:
   - Results are displayed in a table
   - Use the dropdown to control how many results are visible per page
   - Navigate through pages with the pagination controls

6. Export results:
   - "Download as CSV" exports all search results
   - "Download Visible Results" exports only the currently visible results

## Debug Mode

The web interface includes a debug mode that shows additional information:

- Press Ctrl+Shift+D to toggle debug mode
- Add `?debug=true` to the URL to enable debug mode on page load
- Click the "Toggle Debug" button in the debug section

In debug mode, you can see:
- The equivalent CLI command for your current search
- API response details
- Error information if the server request fails

## Backend Implementation

The backend server (`server.py`) provides:

1. Static file serving for the web interface
2. A `/api/search` endpoint that connects to the Business Finder CLI
3. Direct integration with the Business Finder Python package

The server handles JSON requests from the frontend and returns business search results in JSON format.

## Troubleshooting

- If you see mock data instead of real results, make sure:
  - The server is running
  - Your Google API key is correctly configured
  - Your search parameters are valid

- If the map doesn't load, check that your Google Maps JavaScript API key is valid and has the required permissions