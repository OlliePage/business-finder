# File: business_finder/cli.py
import argparse
import json
import sys
from pathlib import Path

from business_finder.api.places import search_places
from business_finder.exporters.csv_exporter import write_to_csv
from business_finder.exporters.json_exporter import write_to_json
from business_finder.config import get_api_key, save_api_key


def main():
    parser = argparse.ArgumentParser(description='Search for businesses using Google Places API')

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for businesses')
    search_parser.add_argument('--api-key', help='Your Google API Key')
    search_parser.add_argument('--search-term', default='business', help='Search term (e.g., "coffee shop")')
    search_parser.add_argument('--latitude', type=float, help='Center latitude')
    search_parser.add_argument('--longitude', type=float, help='Center longitude')
    search_parser.add_argument('--location', help='Location name (will be geocoded)')
    search_parser.add_argument('--radius', type=int, default=1000, help='Search radius in meters (max 50000)')
    search_parser.add_argument('--output', default='business_results.csv', help='Output filename')
    search_parser.add_argument('--format', choices=['csv', 'json'], default='csv', help='Output format')
    search_parser.add_argument('--json-params', help='JSON string with all parameters')
    search_parser.add_argument('--params-file', help='JSON file with all parameters')

    # Config command
    config_parser = subparsers.add_parser('config', help='Configure settings')
    config_parser.add_argument('--set-api-key', help='Set Google API Key')

    args = parser.parse_args()

    # If no command is specified, show help
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Handle config command
    if args.command == 'config':
        if args.set_api_key:
            save_api_key(args.set_api_key)
            print(f"API key saved successfully.")
        sys.exit(0)

    # For search command, get parameters
    search_term = args.search_term
    latitude = args.latitude
    longitude = args.longitude
    radius = args.radius

    # Handle JSON parameters (from clipboard or file)
    if args.json_params:
        try:
            params = json.loads(args.json_params)
            if 'search_term' in params:
                search_term = params['search_term']
            if 'latitude' in params:
                latitude = params['latitude']
            if 'longitude' in params:
                longitude = params['longitude']
            if 'radius' in params:
                radius = params['radius']
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON parameters: {e}")
            sys.exit(1)

    # Handle parameters from file
    if args.params_file:
        try:
            with open(args.params_file, 'r') as f:
                params = json.load(f)
                if 'search_term' in params:
                    search_term = params['search_term']
                if 'latitude' in params:
                    latitude = params['latitude']
                if 'longitude' in params:
                    longitude = params['longitude']
                if 'radius' in params:
                    radius = params['radius']
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading parameters file: {e}")
            sys.exit(1)

    # Validate parameters
    if latitude is None or longitude is None:
        print("Error: Latitude and longitude are required.")
        sys.exit(1)

    # Get API key
    api_key = args.api_key or get_api_key()
    if not api_key:
        print("Error: API key is required. Set it with --api-key or configure it with 'business-finder config --set-api-key YOUR_KEY'")
        sys.exit(1)

    # Perform search
    print(f'Searching for "{search_term}" within {radius}m of coordinates [{latitude}, {longitude}]...')
    businesses = search_places(api_key, search_term, latitude, longitude, radius)

    print(f"Found {len(businesses)} businesses matching criteria.")

    # Export results
    if businesses:
        if args.format == 'csv':
            write_to_csv(businesses, args.output)
        else:
            write_to_json(businesses, args.output)


if __name__ == "__main__":
    main()