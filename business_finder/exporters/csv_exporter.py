# File: business_finder/exporters/csv_exporter.py
import csv


def write_to_csv(businesses, output_file):
    """Write the collected business data to a CSV file"""
    if not businesses:
        print("No businesses to write to CSV.")
        return False

    try:
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "name",
                "address",
                "phone",
                "website",
                "rating",
                "total_ratings",
                "is_open_now",
                "place_id",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for business in businesses:
                writer.writerow(business)

        print(f"Successfully exported {len(businesses)} businesses to {output_file}")
        return True

    except IOError as e:
        print(f"Error writing to CSV file: {e}")
        return False
