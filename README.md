# Business Finder

A tool for finding and exporting business data within a specified geographic area using Google Maps API.

## Repository Structure

```
business-finder/
│
├── README.md                   # Project documentation
├── LICENSE                     # License file (e.g., MIT)
├── requirements.txt            # Python dependencies
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
├── web/                        # Web interface files
│   ├── index.html              # Map selection widget HTML
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
    ├── test_api.py             # API tests
    ├── test_exporters.py       # Exporter tests
    └── fixtures/               # Test fixtures
```

## Key Components

### Python Package (`business_finder/`)

The core Python package contains all the functionality for interacting with the Google Places API, processing data, and exporting results.

- **api/places.py**: Contains the functions for searching places and getting place details
- **cli.py**: Provides a command-line interface for using the tool
- **exporters/**: Modules for exporting data in different formats

### Web Interface (`web/`)

The web folder contains all files for the interactive map widget.

- **index.html**: The main HTML file for the map widget
- **js/map-widget.js**: JavaScript code for the map functionality
- **js/integration.js**: Code for integrating with the Python backend

### Installation and Setup

1. Install the package: (#TODO change this to poetry)
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

2. Set up your Google API key:
   ```bash
   export GOOGLE_API_KEY="your_api_key"
   ```
   Or use a configuration file.

### Usage Examples

#### Command-line Usage
```bash
# Basic search
business-finder search --term "coffee shop" --location "San Francisco" --radius 1000

# Search using coordinates from map widget
business-finder search --json-params '{"search_term":"coffee shop","latitude":37.7749,"longitude":-122.4194,"radius":1000}'
```

#### Web Interface
Open the `web/index.html` file in a browser, select a location and radius, then copy the parameters to use with the command-line tool.