# File: business_finder/exporters/json_exporter.py
import json


def write_to_json(businesses, output_file):
    """Write the collected business data to a JSON file"""
    if not businesses:
        print("No businesses to write to JSON.")
        return False

    try:
        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(businesses, jsonfile, indent=2)

        print(f"Successfully exported {len(businesses)} businesses to {output_file}")
        return True

    except IOError as e:
        print(f"Error writing to JSON file: {e}")
        return False