To use this script, you'll need:

Google Maps API Key:

Create a project in the Google Cloud Console
Enable the Places API
Create an API key with appropriate restrictions
Replace YOUR_GOOGLE_API_KEY in the script

Configure Search Parameters:

Update SEARCH_TERM with your search query (e.g., "restaurants", "dentist", etc.)
Set LATITUDE and LONGITUDE for the center of your search
Adjust RADIUS (in meters, max 50,000m or ~31 miles)

What This Script Does

Searches for businesses matching your criteria within the specified radius
Retrieves detailed information about each business (name, address, website, rating, etc.)
Handles pagination to get up to 60 results (Google's limit)
Respects Google's rate limits with appropriate delays
Exports all data to a CSV file for easy analysis

Important Notes

The Google Places API has usage quotas and billing. Check your Google Cloud Console for pricing details.
The script includes basic error handling and rate limit considerations.
For production use, you might want to add more robust error handling and logging.


Map Selection Widget for Business Search
I've created an interactive map widget that allows users to:

Select a location by clicking anywhere on the map
Adjust the search radius by either:

Dragging the circle's edge to resize it
Using the slider control


Enter a search term for the type of business they want to find
Copy the parameters (latitude, longitude, radius, and search term) to use in your Python script

Setup Instructions
To use this widget:

Replace the API Key:

In the HTML file, replace YOUR_GOOGLE_API_KEY with your Google Maps JavaScript API key
Make sure you have enabled the Maps JavaScript API in your Google Cloud Console


Open the HTML file in a web browser
Use the interface to select your location and radius:

Click on the map to set the center point
Drag the blue circle's edge to adjust the radius visually
Or use the slider to set a precise radius value
Enter your search term in the input field


Click "Copy Parameters" to get the JSON object with your parameters, which you can then use in your Python script

Running the Updated Python Script
The modified Python script can accept parameters from your map widget in several ways:

Direct Command Line Arguments:
bashCopypython business_search.py --api-key YOUR_API_KEY --search-term "coffee shop" --latitude 37.7749 --longitude -122.4194 --radius 1000

JSON Parameters (copy-pasted from the map widget):
bashCopypython business_search.py --api-key YOUR_API_KEY --json-params '{"search_term":"coffee shop","latitude":37.7749,"longitude":-122.4194,"radius":1000}'


Complete Solution
This complete solution now gives you:

An interactive visual map interface for selecting your search area
A radius visualization that can be adjusted by dragging or with a slider
The ability to search for any business term you want
A robust Python script that uses your selected parameters to search the Google Places API
Automatic export to CSV with all the business details you requested

Integration Flow

User selects location on map:

User opens web/index.html in their browser
Selects a point on the map and adjusts the radius
Enters a search term


Parameters are captured:

map-widget.js captures the parameters
User clicks "Copy Parameters" button
Parameters are copied to clipboard as JSON


Python script receives parameters:

User runs the CLI tool with JSON parameters:
bashCopybusiness-finder search --json-params '{"search_term":"coffee shop","latitude":37.7749,"longitude":-122.4194,"radius":1000}'

Or saves parameters to a file and runs:
bashCopybusiness-finder search --params-file location-params.json



Processing and export:

cli.py parses the arguments
Calls functions in places.py to perform the search
Uses csv_exporter.py to save the results

Alternative Integration Options
Web Service Approach
As an alternative to copying/pasting parameters, you could implement a web service:

Create a simple Flask/FastAPI server that receives parameters from the web interface
The JavaScript sends parameters via AJAX/fetch
The server runs the Python script and returns the CSV file for download

Code for this would be in:

web/js/integration.js - Client-side API calls
business_finder/api_server.py - Server implementation

Electron App
For a complete desktop application experience:
