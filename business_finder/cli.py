# File: business_finder/cli.py
import argparse
import json
import sys
from pathlib import Path

from business_finder.api.places import search_places
import yaml
from business_finder.config import (
    get_api_key, save_api_key, 
    get_config, save_sub_radius, save_max_workers,
    DEFAULT_SUB_RADIUS, DEFAULT_MAX_WORKERS,
    DEFAULT_CONFIG, CONFIG_PATHS
)
from business_finder.exporters.csv_exporter import write_to_csv
from business_finder.exporters.json_exporter import write_to_json


def main():
    parser = argparse.ArgumentParser(
        description="Search for businesses using Google Places API",
        epilog=f"""
For large radius searches, the tool uses a grid-based approach to overcome the 
Google Places API limit of 60 results. The search area is automatically divided 
into smaller sub-areas that are searched independently and then combined.

Default sub-radius: {DEFAULT_SUB_RADIUS} meters
Default max workers: {DEFAULT_MAX_WORKERS}

Configure these settings with 'business-finder config --set-sub-radius VALUE'
"""
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for businesses")
    search_parser.add_argument("--api-key", help="Your Google API Key")
    search_parser.add_argument(
        "--search-term", default="business", help='Search term (e.g., "coffee shop")'
    )
    search_parser.add_argument("--latitude", type=float, help="Center latitude")
    search_parser.add_argument("--longitude", type=float, help="Center longitude")
    search_parser.add_argument("--location", help="Location name (will be geocoded)")
    search_parser.add_argument(
        "--radius", type=int, default=1000, help="Search radius in meters (larger radii will be split into smaller sub-searches)"
    )
    search_parser.add_argument(
        "--sub-radius", type=int, help=f"Sub-search radius in meters for large area searches (default: configured value, currently {DEFAULT_SUB_RADIUS})"
    )
    search_parser.add_argument(
        "--max-workers", type=int, help=f"Maximum number of parallel searches for large area searches (default: configured value, currently {DEFAULT_MAX_WORKERS})"
    )
    search_parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose output with detailed search logs"
    )
    search_parser.add_argument(
        "--output", default="business_results.csv", help="Output filename"
    )
    search_parser.add_argument(
        "--format", choices=["csv", "json"], default="csv", help="Output format"
    )
    search_parser.add_argument("--json-params", help="JSON string with all parameters")
    search_parser.add_argument("--params-file", help="JSON file with all parameters")

    # Config command
    config_parser = subparsers.add_parser("config", help="Configure settings")
    config_parser.add_argument("--set-api-key", help="Set Google API Key")
    config_parser.add_argument("--set-sub-radius", type=int, help="Set default sub-radius for grid searches (in meters)")
    config_parser.add_argument("--set-max-workers", type=int, help="Set default maximum parallel workers for grid searches")
    config_parser.add_argument("--show", action="store_true", help="Show current configuration")
    config_parser.add_argument("--export-config", help="Export configuration to a specified YAML file")

    args = parser.parse_args()

    # If no command is specified, show help
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Handle config command
    if args.command == "config":
        config_changed = False
        
        if args.set_api_key:
            save_api_key(args.set_api_key)
            print("API key saved successfully.")
            config_changed = True
            
        if args.set_sub_radius is not None:
            if args.set_sub_radius <= 0:
                print("Error: Sub-radius must be a positive number")
                sys.exit(1)
            save_sub_radius(args.set_sub_radius)
            print(f"Default sub-radius set to {args.set_sub_radius} meters.")
            config_changed = True
            
        if args.set_max_workers is not None:
            if args.set_max_workers <= 0:
                print("Error: Max workers must be a positive number")
                sys.exit(1)
            save_max_workers(args.set_max_workers)
            print(f"Default max workers set to {args.set_max_workers}.")
            config_changed = True
            
        if args.export_config:
            # Export config to specified file
            config_file = Path(args.export_config)
            
            # Create a hierarchical config structure
            export_config = DEFAULT_CONFIG.copy()
            flat_config = get_config()
            
            # Update with current values
            export_config["api"]["key"] = flat_config["api_key"]
            export_config["search"]["sub_radius"] = flat_config["sub_radius"]
            export_config["search"]["max_workers"] = flat_config["max_workers"]
            
            # Write to file with helpful comments
            try:
                with open(config_file, "w") as f:
                    f.write("# Business Finder Configuration\n")
                    f.write("# This file can be edited manually and placed in any of these locations (in order of precedence):\n")
                    for path in CONFIG_PATHS:
                        f.write(f"# - {path}\n")
                    f.write("\n")
                    yaml.dump(export_config, f, default_flow_style=False, sort_keys=False)
                print(f"Configuration exported to {config_file}")
                config_changed = True
            except (IOError, OSError) as e:
                print(f"Error exporting configuration: {e}")
                sys.exit(1)
            
        if args.show or not config_changed:
            # Get the flat config for backwards compatibility
            flat_config = get_config()
            
            # Show current configuration in both flat and hierarchical format
            print("\nCurrent Configuration:")
            print("=" * 50)
            
            # Display the hierarchical format
            print("Config files (in order of precedence):")
            for path in CONFIG_PATHS:
                exists = "✓" if path.exists() else "✗"
                print(f"  {exists} {path}")
            print()
            
            # Create hierarchical view for display
            display_config = {
                "api": {
                    "key": f"{'*' * 8 + flat_config['api_key'][-4:] if flat_config['api_key'] else 'Not set'}"
                },
                "search": {
                    "sub_radius": f"{flat_config['sub_radius']} meters (default: {DEFAULT_SUB_RADIUS})",
                    "max_workers": f"{flat_config['max_workers']} (default: {DEFAULT_MAX_WORKERS})"
                }
            }
            
            # Convert to YAML for pretty display
            print("Configuration values:")
            print(yaml.dump(display_config, default_flow_style=False, sort_keys=False))
            
            print("You can edit this configuration with:")
            print("  business-finder config --set-api-key YOUR_API_KEY")
            print("  business-finder config --set-sub-radius 3000")
            print("  business-finder config --set-max-workers 8")
            print("  business-finder config --export-config path/to/config.yaml")
            print("=" * 50)
            
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
            if "search_term" in params:
                search_term = params["search_term"]
            if "latitude" in params:
                latitude = params["latitude"]
            if "longitude" in params:
                longitude = params["longitude"]
            if "radius" in params:
                radius = params["radius"]
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON parameters: {e}")
            sys.exit(1)

    # Handle parameters from file
    if args.params_file:
        try:
            with open(args.params_file, "r") as f:
                params = json.load(f)
                if "search_term" in params:
                    search_term = params["search_term"]
                if "latitude" in params:
                    latitude = params["latitude"]
                if "longitude" in params:
                    longitude = params["longitude"]
                if "radius" in params:
                    radius = params["radius"]
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
        print(
            "Error: API key is required. Set it with --api-key or configure it with"
            " 'business-finder config --set-api-key YOUR_KEY'"
        )
        sys.exit(1)

    # Perform search
    # Get the additional parameters for grid search
    # Use command line arguments if provided, otherwise get from config
    config = get_config()
    sub_radius = args.sub_radius if args.sub_radius is not None else config["sub_radius"]
    max_workers = args.max_workers if args.max_workers is not None else config["max_workers"]
    
    print(
        f'Searching for "{search_term}" within {radius}m of coordinates [{latitude}, {longitude}]...'
    )
    
    if radius > sub_radius:
        print(f"Using grid search with sub-radius {sub_radius}m and {max_workers} parallel workers")
        
    # Set verbose flag for detailed logging
    verbose = args.verbose
    
    businesses = search_places(
        api_key, 
        search_term, 
        latitude, 
        longitude, 
        radius, 
        sub_radius=sub_radius, 
        max_workers=max_workers
    )
    
    # Display detailed logs if verbose mode is enabled
    if verbose:
        from business_finder.api.places import get_search_logs
        logs = get_search_logs()
        
        print("\n===== SEARCH LOGS =====")
        for log in logs:
            timestamp = log.get("timestamp", "").split("T")[1].split(".")[0] if "T" in log.get("timestamp", "") else ""
            level = log.get("level", "INFO")
            message = log.get("message", "")
            
            # Format the log entry
            print(f"[{timestamp}] {level}: {message}")
            
            # Print details for important log entries or in debug level
            if level == "DEBUG" or "Breaking search into" in message or "Total unique businesses" in message:
                details = log.get("details", {})
                if details:
                    for key, value in details.items():
                        if key != "points":  # Skip the detailed points array
                            print(f"  {key}: {value}")
                    print("")
        print("======================\n")

    print(f"Found {len(businesses)} businesses matching criteria.")

    # Export results
    if businesses:
        if args.format == "csv":
            write_to_csv(businesses, args.output)
        else:
            write_to_json(businesses, args.output)


if __name__ == "__main__":
    main()
