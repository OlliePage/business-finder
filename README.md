# Business Finder
[![Python CI](https://github.com/OlliePage/business-finder/actions/workflows/python-ci.yml/badge.svg)](https://github.com/OlliePage/business-finder/actions/workflows/python-ci.yml)
[![codecov](https://codecov.io/gh/OlliePage/business-finder/graph/badge.svg?token=1A2QDJVKO5)](https://codecov.io/gh/OlliePage/business-finder)

## Overview

Business Finder is a tool that combines a visual map interface with the power of the Google Places API to help you find and export business data. Whether you're conducting market research, planning business outreach, or analyzing competition, this tool makes it easy to:

1. Visually select a geographic area on a map
2. Set a precise search radius
3. Search for specific business types
4. Filter results based on ratings, review counts, and contact information
5. Export complete business details to CSV or JSON

## Features

- **Interactive Map Interface**: Select any location worldwide with a simple click
- **Visual Radius Selection**: Adjust your search radius by dragging or using a slider
- **Flexible Search Terms**: Find any type of business (restaurants, hotels, retail, etc.)
- **Place Type Search**: Search directly by place type categories (e.g., restaurant, cafe, etc.)
- **Enhanced Categorization**: Leverage Google's hierarchical categorization with primary and secondary types
- **Advanced Filtering**: Filter results by rating, review count, type, price level, business status and more
- **Sortable Results**: Sort business listings by name, type, rating, price level, etc.
- **Comprehensive Data Export**: Get business names, addresses, phone numbers, websites, ratings, types, and more
- **Multiple Export Formats**: Save results as CSV, JSON, or Google Sheets
- **Command-Line Interface**: Run searches programmatically or from scripts
- **Web Server Mode**: Run as a local server for a complete web application experience

## Installation

### Prerequisites

- Python 3.7+
- Google Maps API key (with Places API enabled)

### Install from Source

```bash
# Install dependencies and package with Poetry
poetry install

# Activate the virtual environment
poetry shell
```

## Testing

The project has a comprehensive test suite with over 90% code coverage. To run the tests:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run tests with coverage
pytest --cov=business_finder --cov-branch --cov-report=term
```

For more detailed information about testing, see the [tests/README.md](tests/README.md) file.

## Continuous Integration

This project uses GitHub Actions for continuous integration and delivery:

- **Python CI**: A combined workflow that runs:
  - **Linting**: Checks code quality with flake8, black, and isort
  - **Tests**: Runs the test suite on multiple Python versions (3.9, 3.10, 3.11)
- **Python Publish**: Builds and publishes the package to PyPI when a new release is created

These CI workflows ensure that:
- All tests pass on every push and pull request
- Code follows consistent style guidelines
- Test coverage remains high
- Package releases are tested before publishing

For detailed instructions on running CI checks locally before pushing, see [CI_GUIDE.md](CI_GUIDE.md).

## Quick Start

### 1. Using the Makefile (Recommended)

The project includes a Makefile with simple commands to get you started quickly:

```bash
# View all available commands
make help

# Set up the Poetry environment
make setup

# Configure your Google API key
make configure

# Run the web server
make run-server
```

### 2. Manual Setup

#### Configure Your API Key

```bash
# Set your Google API key 
business-finder config --set-api-key "YOUR_GOOGLE_API_KEY"
```

#### Use the Web Interface

You can use Business Finder in two ways:

##### Option A: Standalone HTML page
Open `web/index.html` in your browser (add your API key to the URL):
```
file:///path/to/business-finder/web/index.html?key=YOUR_GOOGLE_API_KEY
```

##### Option B: Run the built-in web server
```bash
# Start the web server
python web/server.py

# Open in your browser
# http://localhost:8000
```

The web server automatically injects your API key from your configuration, so you don't need to manually add it to the HTML file.

### 3. Using the Web Interface

Follow these steps:
1. Click anywhere on the map to set your search center
2. Adjust the circle radius by dragging or using the slider
3. Enter your search term (e.g., "coffee shop") or place type (e.g., "restaurant", "cafe")
   - Click the "Place Types" button to see a list of available place types
   - Select a place type from the dropdown to search by category
4. Click "Search Businesses" to see results
5. Filter and sort results:
   - Filter by minimum rating, review count, place type, price level, etc.
   - Sort by clicking on column headers (name, type, rating, etc.)
6. Download results as CSV or click "Copy Parameters" to get the command-line version

### 4. Run the Search

```bash
# Using parameters copied from the web interface
business-finder search --json-params '{"search_term":"coffee shop","latitude":37.7749,"longitude":-122.4194,"radius":1000}'

# Or save parameters to a file and use that
business-finder search --params-file location.json
```

### 4. View Results

Results will be saved to the `data/` directory by default. You can specify a different output file:

```bash
business-finder search --json-params '...' --output data/my_results.csv
```

When using the web interface, results are displayed directly in the browser and can be:
- Filtered by minimum rating, minimum review count, or contact information
- Sorted by clicking on any column header
- Downloaded as CSV for the complete set or just the filtered view

## Command-Line Reference

### Search for Businesses

```bash
business-finder search [OPTIONS]
```

Options:
- `--api-key KEY` - Your Google API Key (if not configured already)
- `--search-term TERM` - Search term (e.g., "coffee shop")
- `--latitude LAT` - Center latitude
- `--longitude LNG` - Center longitude
- `--radius METERS` - Search radius in meters (large radii will be split into sub-searches)
- `--sub-radius METERS` - Sub-search radius for grid-based searches (default: from config)
- `--max-workers N` - Maximum number of parallel searches for grid-based searches (default: from config)
- `--adaptive-radius` - Dynamically adjust sub-radius based on result density (enabled by default)
- `--no-adaptive-radius` - Disable dynamic sub-radius adjustment
- `--verbose` - Enable verbose output with detailed search logs
- `--output FILE` - Output filename
- `--format FORMAT` - Output format (csv or json)
- `--json-params JSON` - JSON string with all parameters
- `--params-file FILE` - JSON file with all parameters

### Configure Settings

```bash
business-finder config [OPTIONS]
```

Options:
- `--set-api-key KEY` - Set Google API Key
- `--set-sub-radius METERS` - Set default sub-radius for grid searches (in meters)
- `--set-max-workers N` - Set default maximum parallel workers for grid searches
- `--show` - Show current configuration
- `--export-config FILE` - Export configuration to a YAML file

## Examples

### Basic Search

```bash
# Search for coffee shops in San Francisco
business-finder search --search-term "coffee shop" --latitude 37.7749 --longitude -122.4194 --radius 1000

# Search by place type (using Google Places API types)
business-finder search --search-term "restaurant" --latitude 37.7749 --longitude -122.4194 --radius 1000
```

### Advanced Usage

```bash
# Search for restaurants within 2km, export as JSON
business-finder search --search-term "restaurant" --latitude 40.7128 --longitude -74.0060 --radius 2000 --format json --output nyc_restaurants.json

# Using place types for more precise categorization
business-finder search --search-term "cafe" --latitude 51.5074 --longitude -0.1278 --radius 1500

# More specific place types
business-finder search --search-term "pharmacy" --latitude 34.0522 --longitude -118.2437 --radius 2000
business-finder search --search-term "tourist_attraction" --latitude 48.8566 --longitude 2.3522 --radius 3000
```

### Grid-Based Search Example

```bash
# Search for hotels in a large 10km radius around London
# Breaking it into smaller 2km sub-searches with 10 parallel workers
business-finder search --search-term "hotel" --latitude 51.5074 --longitude -0.1278 --radius 10000 --sub-radius 2000 --max-workers 10 --output london_hotels.csv
```

## Integration Options

### Programmatic Usage

You can use the package directly in your Python code:

```python
from business_finder.api.places import search_places
from business_finder.exporters.csv_exporter import write_to_csv

# Basic search (single API call)
businesses = search_places(
    api_key="YOUR_API_KEY",
    search_term="gym",
    latitude=34.0522,
    longitude=-118.2437,
    radius=1500
)

# Grid-based search for larger radius (multiple API calls in parallel)
businesses_large_area = search_places(
    api_key="YOUR_API_KEY",
    search_term="gym",
    latitude=34.0522,
    longitude=-118.2437,
    radius=10000,        # Large radius that will be split into smaller searches
    sub_radius=2500,     # Each sub-search will use this radius
    max_workers=8        # Number of parallel searches
)

# Export results
write_to_csv(businesses_large_area, "los_angeles_gyms.csv")
```

### Web Service Integration

For a complete web service, check out the [business-finder-service](https://github.com/yourusername/business-finder-service) repository, which adds:

- REST API endpoints
- Direct file downloads
- User authentication
- Search history

## Grid-Based Search for Large Areas

Business Finder includes an advanced grid-based search feature that overcomes the Google Places API's limitation of 60 results per search:

### How It Works

1. When a large radius is specified, the area is automatically divided into a grid of smaller sub-areas
2. Each sub-area is searched independently (in parallel)
3. The results are combined and deduplicated
4. The final set is returned to the user

This approach allows you to search much larger areas and get more comprehensive results than would be possible with a single API call.

### Configuration

You can configure the grid search parameters using either the CLI or YAML configuration files:

#### CLI Configuration

```bash
# Set the sub-radius (in meters) for grid searches
business-finder config --set-sub-radius 3000

# Set the maximum number of concurrent searches
business-finder config --set-max-workers 8

# View current configuration
business-finder config --show

# Export configuration to a YAML file
business-finder config --export-config ~/my-business-finder-config.yaml
```

#### YAML Configuration

Business Finder also supports YAML configuration files for more flexibility. Create or edit a YAML file with the following structure:

```yaml
# API Configuration
api:
  key: YOUR_API_KEY_HERE

# Search Configuration
search:
  # Sub-radius in meters for grid-based searches
  sub_radius: 3000
  
  # Maximum number of concurrent searches
  max_workers: 5
```

Configuration files are searched in the following order of precedence:
1. `~/.business_finder/config.yaml` (global user configuration)
2. `./config.yaml` (project directory configuration)
3. `~/.business_finder/config.json` (legacy configuration)

A sample configuration file is provided at `config.yaml.example` in the project root.

You can also specify these parameters for individual searches:

```bash
# Override default sub-radius and max workers for this search
business-finder search --search-term "restaurant" --latitude 40.7128 --longitude -74.0060 --radius 10000 --sub-radius 2500 --max-workers 10
```

### Performance Considerations

- Using smaller sub-radii will result in more comprehensive results but will make more API calls
- Increasing max-workers speeds up searches but uses more concurrent connections
- API usage costs and rate limits should be considered when adjusting these parameters

### Adaptive Sub-Radius

Business Finder includes a smart density detection system that automatically adjusts the search grid density based on location popularity:

1. Before starting the full grid search, a "smoke test" is performed at the center point
2. If the initial search returns close to the API limit of results (60 results), the sub-radius is automatically halved
3. This process continues recursively until either:
   - Results are below the threshold (meaning we're using an appropriate sub-radius), or
   - The minimum sub-radius is reached (to prevent excessive API calls)

This adaptive approach ensures:
- In dense urban areas like NYC, the search automatically uses a tighter grid for more comprehensive coverage
- In sparse rural areas, the default larger sub-radius is maintained for efficiency
- Every business gets a fair and equitable chance at being shown to the user

You can control this feature with:
- Web UI: "Adapt search density automatically" checkbox in Advanced Options
- CLI: `--adaptive-radius` flag (enabled by default) or `--no-adaptive-radius` to disable it

### Search Logs and Debugging

Business Finder provides a detailed logging system for grid-based searches, allowing you to see exactly what's happening in the background:

- **Grid Generation**: See how the search area is divided into smaller sub-areas
- **Search Progress**: Track the progress of each sub-search in real-time
- **Result Deduplication**: View statistics on duplicate results that are filtered out
- **Performance Metrics**: Get timing information for each search operation

To access search logs:

1. **In the Web UI**:
   - Click "Toggle Debug Mode" to enable debugging features
   - After performing a search, the logs will be automatically displayed
   - Or click "Show Search Logs" to view logs from the most recent search
   - Filter logs by level (INFO, WARNING, ERROR, DEBUG)

2. **In the CLI**:
   - Search logs are printed to the standard output during searches
   - Use the `--verbose` flag for additional debug information:
     ```bash
     business-finder search --search-term "restaurant" --latitude 51.5074 --longitude -0.1278 --radius 10000 --verbose
     ```

## Enhanced Place Categorization

Business Finder now leverages the enhanced categorization features from the Google Places API:

### Place Types

Every business is categorized with:
- **Primary Type**: The main category (e.g., restaurant, cafe, pharmacy)
- **Secondary Types**: Additional categories that apply (e.g., food, point_of_interest)

You can:
1. **Search directly by type**: Enter a place type like `restaurant` or `coffee_shop` in the search field or use the place type dropdown
2. **Filter by type**: After searching, filter the results by any place type present in the results
3. **Export type data**: Type information is included in CSV and JSON exports

### Business Status

Business status information shows whether a place is:
- **OPERATIONAL**: Currently open for business
- **CLOSED_TEMPORARILY**: Temporarily closed
- **CLOSED_PERMANENTLY**: Permanently closed

### Price Level

Price level data (when available) ranges from 0 to 4:
- **0**: Free or inexpensive
- **1**: £
- **2**: ££
- **3**: £££
- **4**: ££££

These enhanced categorization features make it easier to find exactly what you're looking for without relying solely on business names or keywords.

## Limitations

- Even with grid-based search, the Google Places API has rate limits that may affect very large searches
- API usage is subject to Google's pricing and quota limits
- Very dense areas may still not return all possible results
- Not all place types are supported by Google in all regions

## Debugging Tools

Business Finder includes several debugging tools to help diagnose and fix issues:

### Debug Mode

To access debugging tools:
1. Click the "🐞 Debug" button in the toolbar
2. Debug mode will be enabled, revealing additional tools and information

In debug mode, you can:
- View detailed API responses
- See internal system logs
- Access database maintenance tools

### Database Migrations

If you encounter database errors after updating to a new version, you can fix them using:

1. Enable Debug Mode by clicking the "🐞 Debug" button
2. Click the "🔧 Fix DB" button that appears in the toolbar
3. Follow the on-screen prompts to update your database schema
4. Refresh the page after the fix is complete

This will automatically update your database schema to be compatible with the current version of Business Finder.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Make sure all tests pass (see [Testing](#testing))
6. Ensure your code follows style guidelines by running linting tools:
   ```bash
   pip install flake8 black isort
   flake8 .
   black business_finder tests
   isort business_finder tests
   ```
7. Open a Pull Request

When you open a pull request, the CI/CD workflows will automatically run to verify that:
- All tests pass across multiple Python versions
- Code style meets the project's guidelines
- Test coverage remains high

The PR will show the status of these checks, and it should be ready to merge once all checks pass.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google Maps Platform for providing the Places API
- All contributors who have helped improve this project

## Repository Structure

```
business-finder/
│
├── README.md                   # Project documentation
├── LICENSE                     # License file (e.g., MIT)
├── CLAUDE.md                   # Instructions for Claude Code AI
├── Makefile                    # Makefile with common commands
├── pyproject.toml              # Poetry configuration
├── poetry.lock                 # Poetry locked dependencies  
├── setup.py                    # Package installation script
│
├── business_finder/            # Main Python package
│   ├── __init__.py             # Package initialization
│   ├── api/                    # API interaction modules
│   │   ├── __init__.py
│   │   ├── places.py           # Google Places API interaction
│   │   └── geocoding.py        # Geocoding helper functions
│   │
│   ├── cli.py                  # Command-line interface
│   ├── config.py               # Configuration handling
│   └── exporters/              # Data export modules
│       ├── __init__.py
│       ├── csv_exporter.py     # CSV export functionality
│       └── json_exporter.py    # JSON export functionality
│
├── data/                       # Storage directory for exported data
│
├── web/                        # Web interface files
│   ├── index.html              # Interactive web interface
│   ├── server.py               # Built-in web server
│   ├── css/                    # CSS styles
│   │   └── style.css           # Main stylesheet
│   ├── js/                     # JavaScript files
│   │   ├── map-widget.js       # Map widget functionality
│   │   └── integration.js      # Integration with Python script
│   └── assets/                 # Static assets like images
│
├── examples/                   # Example scripts and use cases
│   ├── basic_search.py         # Basic search example
│   ├── advanced_search.py      # Advanced search example
│   └── sample_data/            # Sample data files
│
└── tests/                      # Test suite
    ├── __init__.py
    ├── README.md               # Test documentation
    ├── test_api.py             # API tests
    ├── test_cli.py             # CLI tests
    ├── test_config.py          # Configuration tests
    ├── test_exporters.py       # Exporter tests
    ├── test_geocoding.py       # Geocoding tests
    ├── test_integration.py     # Integration tests
    └── fixtures/               # Test fixtures
        ├── __init__.py
        └── mock_responses.py   # Mock API responses
```

## Key Components

### Python Package (`business_finder/`)

The core Python package contains all the functionality for interacting with the Google Places API, processing data, and exporting results.

- **api/places.py**: Contains the functions for searching places and getting place details
- **cli.py**: Provides a command-line interface for using the tool
- **exporters/**: Modules for exporting data in different formats

### Web Interface (`web/`)

The web folder contains all files for the interactive web application.

- **index.html**: The main HTML file with interactive map and results table
- **server.py**: A built-in web server that connects the front-end to the Business Finder API
- **js/map-widget.js**: JavaScript code for the map functionality
- **js/integration.js**: Code for integrating with the Python backend

### Installation and Setup

1. Install the package with Poetry:
   ```bash
   # Install Poetry if you don't have it already
   # See https://python-poetry.org/docs/#installation
   
   # Install the package and dependencies
   poetry install
   
   # Activate the virtual environment
   poetry shell
   ```

2. Set up your Google API key:
   ```bash
   export GOOGLE_API_KEY="your_api_key"
   ```
   Or use the configuration command:
   ```bash
   business-finder config --set-api-key "your_api_key"
   ```

### Usage Examples

#### Command-line Usage
```bash
# Basic search
business-finder search --term "coffee shop" --location "San Francisco" --radius 1000

# Search using coordinates from map widget
business-finder search --json-params '{"search_term":"coffee shop","latitude":37.7749,"longitude":-122.4194,"radius":1000}'
```

#### Web Interface

Option 1: Start the web server and access the full web application:
```bash
# Start the web server
python web/server.py

# Open in your browser
# http://localhost:8000
```

Option 2: Open the `web/index.html` file directly in a browser.

## Google Sheets Integration

Business Finder includes functionality to export search results directly to Google Sheets:

1. **Direct Export**: Export results to a new or existing Google Sheet
2. **Formatted Output**: Data is formatted with proper headers, hyperlinks, and column sizing
3. **OAuth Authentication**: Secure authentication with Google's API

### Setup Google Sheets Integration

To use the Google Sheets export functionality, you need OAuth credentials:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the "Google Sheets API" and "Google Drive API"
4. Create OAuth 2.0 credentials (OAuth client ID, type: Desktop application)
5. Download the credentials JSON file
6. Place the file in the `credentials` directory as `client_secret.json`:
   ```
   mkdir -p credentials
   cp ~/Downloads/client_secret_XXXX.json credentials/client_secret.json
   ```

When you first use the Google Sheets export, it will open a browser window for authentication. The authentication token will be stored in the same directory as your credentials.

### Using Google Sheets Export

From the command line:
```bash
# Export search results to Google Sheets
business-finder search --latitude 51.485097 --longitude -2.601889 --search-term "coffee" --format sheets
```

From the web interface:
1. Perform a search
2. Click the "Export to Google Sheets" button in the results section

With the web interface, you can:
1. Search for businesses visually using the map
2. View results in a sortable, filterable table
3. Download results to CSV files (stored in the `data/` directory)
4. Generate and copy the equivalent command-line command