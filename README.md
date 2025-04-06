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
- **Advanced Filtering**: Filter results by rating, review count, and contact information availability
- **Sortable Results**: Sort business listings by name, address, rating, or review count
- **Comprehensive Data Export**: Get business names, addresses, phone numbers, websites, ratings, and more
- **Multiple Export Formats**: Save results as CSV or JSON
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

### 1. Configure Your API Key

```bash
# Set your Google API key 
business-finder config --set-api-key "YOUR_GOOGLE_API_KEY"
```

### 2. Use the Web Interface

You can use Business Finder in two ways:

#### Option A: Standalone HTML page
Open `web/index.html` in your browser (add your API key to the URL):
```
file:///path/to/business-finder/web/index.html?key=YOUR_GOOGLE_API_KEY
```

#### Option B: Run the built-in web server (Recommended)
```bash
# Start the web server
python web/server.py

# Open in your browser
# http://localhost:8000
```

The web server automatically injects your API key from your configuration, so you don't need to manually add it to the HTML file.

Follow these steps:
1. Click anywhere on the map to set your search center
2. Adjust the circle radius by dragging or using the slider
3. Enter your search term (e.g., "coffee shop")
4. Click "Search Businesses" to see results
5. Filter and sort results as needed
6. Download results as CSV or click "Copy Parameters" to get the command-line version

### 3. Run the Search

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
- `--radius METERS` - Search radius in meters (max 50000)
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

## Examples

### Basic Search

```bash
# Search for coffee shops in San Francisco
business-finder search --search-term "coffee shop" --latitude 37.7749 --longitude -122.4194 --radius 1000
```

### Advanced Usage

```bash
# Search for restaurants within 2km, export as JSON
business-finder search --search-term "restaurant" --latitude 40.7128 --longitude -74.0060 --radius 2000 --format json --output nyc_restaurants.json
```

## Integration Options

### Programmatic Usage

You can use the package directly in your Python code:

```python
from business_finder.api.places import search_places
from business_finder.exporters.csv_exporter import write_to_csv

# Search for businesses
businesses = search_places(
    api_key="YOUR_API_KEY",
    search_term="gym",
    latitude=34.0522,
    longitude=-118.2437,
    radius=1500
)

# Export results
write_to_csv(businesses, "los_angeles_gyms.csv")
```

### Web Service Integration

For a complete web service, check out the [business-finder-service](https://github.com/yourusername/business-finder-service) repository, which adds:

- REST API endpoints
- Direct file downloads
- User authentication
- Search history

## Limitations

- The Google Places API has a limit of returning up to 60 results per search (20 results per page, max 3 pages)
- API usage is subject to Google's pricing and quota limits
- Large radius searches in dense areas may hit result limits

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

With the web interface, you can:
1. Search for businesses visually using the map
2. View results in a sortable, filterable table
3. Download results to CSV files (stored in the `data/` directory)
4. Generate and copy the equivalent command-line command