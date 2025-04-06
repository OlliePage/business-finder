#!/usr/bin/env python3

import os
import json
from business_finder.exporters.sheets_exporter import export_to_sheets

# Sample business data for testing
test_businesses = [
    {
        "name": "Test Business 1",
        "address": "123 Test St, Testville",
        "phone": "(123) 456-7890",
        "website": "https://example.com/business1",
        "rating": 4.5,
        "total_ratings": 100,
        "place_id": "test_place_id_1",
        "latitude": 51.5074,
        "longitude": -0.1278,
    },
    {
        "name": "Test Business 2",
        "address": "456 Example Ave, Testopolis",
        "phone": "(987) 654-3210",
        "website": "https://example.com/business2",
        "rating": 4.0,
        "total_ratings": 50,
        "place_id": "test_place_id_2",
        "latitude": 51.5075,
        "longitude": -0.1280,
    }
]

def main():
    # Get project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Set up credential paths
    credentials_path = os.path.join(project_root, 'credentials', 'client_secret.json')
    token_path = os.path.join(project_root, 'credentials', 'token.json')
    
    print(f"Project root: {project_root}")
    print(f"Credentials path: {credentials_path}")
    print(f"Token path: {token_path}")
    
    print(f"Credentials exist: {os.path.exists(credentials_path)}")
    print(f"Token exists: {os.path.exists(token_path)}")
    
    # Check what's in the credentials directory
    creds_dir = os.path.join(project_root, 'credentials')
    if os.path.exists(creds_dir):
        print(f"Contents of credentials directory:")
        for file in os.listdir(creds_dir):
            print(f"  - {file}")
            file_path = os.path.join(creds_dir, file)
            print(f"    Size: {os.path.getsize(file_path)} bytes")
            print(f"    Permissions: {oct(os.stat(file_path).st_mode)[-3:]}")
    else:
        print(f"Credentials directory does not exist")
        
    # Try to read the credentials file to verify it's valid
    if os.path.exists(credentials_path):
        try:
            with open(credentials_path, 'r') as f:
                creds_content = f.read()
                print(f"Credentials file successfully read")
                # Just check it's valid JSON
                import json
                json.loads(creds_content)
                print(f"Credentials file is valid JSON")
        except Exception as e:
            print(f"Error reading credentials file: {e}")
    
    try:
        # Try exporting to Google Sheets
        print("\nAttempting to export to Google Sheets...")
        sheet_url = export_to_sheets(
            test_businesses,
            spreadsheet_name="Test Export",
            credentials_path=credentials_path,
            token_path=token_path
        )
        
        print(f"\nExport successful!")
        print(f"Google Sheet URL: {sheet_url}")
        
    except Exception as e:
        print(f"\nError exporting to Google Sheets: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()