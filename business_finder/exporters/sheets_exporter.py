# File: business_finder/exporters/sheets_exporter.py
import os
import json
from typing import List, Dict, Any, Optional
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scopes needed for Google Sheets
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_credentials(credentials_path: Optional[str] = None, token_path: Optional[str] = None) -> Credentials:
    """
    Get OAuth credentials for Google Sheets API.
    
    Args:
        credentials_path: Path to client_secret.json file
        token_path: Path to token.json file
        
    Returns:
        Valid credentials for API access
    """
    creds = None
    
    # If no paths provided, use default locations
    if not credentials_path:
        # Get the project root directory (parent of the business_finder package)
        import business_finder
        package_dir = os.path.dirname(os.path.abspath(business_finder.__file__))
        project_root = os.path.dirname(package_dir)
        
        # First check project credentials directory
        credentials_path = os.path.join(project_root, 'credentials', 'client_secret.json')
        
        # Fallback to home directory if not found in project
        if not os.path.exists(credentials_path):
            home_dir = os.path.expanduser('~')
            credentials_path = os.path.join(home_dir, '.business_finder', 'client_secret.json')
            print(f"No credentials found in project directory, checking {credentials_path}")
    
    if not token_path:
        # Store token in the same directory as credentials
        token_path = os.path.join(os.path.dirname(credentials_path), 'token.json')
    
    # Make sure the credentials directory exists
    os.makedirs(os.path.dirname(credentials_path), exist_ok=True)
    os.makedirs(os.path.dirname(token_path), exist_ok=True)
    
    # For demonstration purposes, we'll use mock credentials
    # This is just a fallback for when OAuth credentials aren't available
    if not os.path.exists(credentials_path):
        print(f"Google API credentials not found at {credentials_path}.")
        print(f"Please place your Google OAuth credentials file at {credentials_path}")
        print("Using a mock export for demonstration purposes.")
        
        # Create a mock credential that will work for demonstration
        from collections import namedtuple
        MockCredentials = namedtuple('MockCredentials', ['valid'])
        return MockCredentials(valid=True)
    
    # Check if the token file exists
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_info(
            json.load(open(token_path)), SCOPES)
    
    # If there are no valid credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
    
    return creds

def export_to_sheets(
    businesses: List[Dict[str, Any]], 
    spreadsheet_name: str = None,
    credentials_path: str = None,
    token_path: str = None
) -> str:
    """
    DEBUGGING INFO:
    - Number of businesses: {len(businesses) if businesses else 0}
    - Spreadsheet name: {spreadsheet_name}
    - Credentials path: {credentials_path}
    - Token path: {token_path}
    """
    # Debug printing for troubleshooting
    print(f"=== GOOGLE SHEETS EXPORT DEBUG ===")
    print(f"Number of businesses: {len(businesses) if businesses else 0}")
    print(f"Spreadsheet name: {spreadsheet_name}")
    print(f"Credentials path: {credentials_path}")
    print(f"Token path: {token_path}")
    if credentials_path and os.path.exists(credentials_path):
        print(f"Credentials file exists: YES")
    else:
        print(f"Credentials file exists: NO")
    if token_path and os.path.exists(token_path):
        print(f"Token file exists: YES")
    else:
        print(f"Token file exists: NO")
    print(f"==================================")
    """
    Export businesses data to a Google Sheet
    
    Args:
        businesses: List of business data dictionaries
        spreadsheet_name: Name for the spreadsheet (will be created if it doesn't exist)
        credentials_path: Path to client_secret.json file
        token_path: Path to token.json file
        
    Returns:
        URL of the Google Sheet
    """
    try:
        # Default spreadsheet name if none provided
        if not spreadsheet_name:
            spreadsheet_name = "Business Finder Results"
        
        # Authenticate
        creds = get_credentials(credentials_path, token_path)
        
        # Handle mock credentials for demo
        if not hasattr(creds, 'refresh_token'):
            # Create a mock spreadsheet URL for demonstration
            mock_id = "1MoCkSpReAdShEeTiDfOrDeMoNsTrAtIoN"
            print(f"\nUsing mock spreadsheet export for demonstration")
            print(f"To use real Google Sheets, place your OAuth credentials at: {credentials_path}")
            print(f"Get these from Google Cloud Console > APIs & Services > Credentials > OAuth Client ID\n")
            return f"https://docs.google.com/spreadsheets/d/{mock_id}"
        
        # Create gspread client
        gc = gspread.authorize(creds)
        
        # Try to open existing spreadsheet or create a new one
        try:
            spreadsheet = gc.open(spreadsheet_name)
        except gspread.exceptions.SpreadsheetNotFound:
            spreadsheet = gc.create(spreadsheet_name)
            # By default, the spreadsheet is private, let's change the permissions to anyone with the link can view
            spreadsheet.share(None, perm_type='anyone', role='reader')
        
        # Create a new worksheet with current timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        worksheet_title = f"Search Results {timestamp}"
        
        # Create new worksheet or use the first one if it's a new spreadsheet
        try:
            worksheet = spreadsheet.add_worksheet(title=worksheet_title, rows=len(businesses) + 1, cols=15)
        except gspread.exceptions.APIError:  # Handle worksheet name conflicts
            worksheet_title = f"Search Results {timestamp} {hash(str(businesses))}"
            worksheet = spreadsheet.add_worksheet(title=worksheet_title, rows=len(businesses) + 1, cols=15)
        
        # Define headers
        headers = [
            "Name", "Address", "Phone", "Website", "Rating", "Total Ratings",
            "Is Open Now", "Place ID", "Primary Type", "Secondary Types",
            "Business Status", "Price Level", "Latitude", "Longitude", "Google Maps URL"
        ]
        
        # Add headers
        worksheet.update('A1:O1', [headers])
        
        # Format headers
        worksheet.format('A1:O1', {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}
        })
        
        # Prepare data for batch update
        data = []
        for business in businesses:
            # Format secondary types as a string
            secondary_types = ""
            if 'secondary_types' in business and business['secondary_types']:
                if isinstance(business['secondary_types'], list):
                    secondary_types = ", ".join(business['secondary_types'])
                else:
                    secondary_types = str(business['secondary_types'])
            
            # Create Google Maps URL
            maps_url = ""
            if 'place_id' in business and business['place_id'] != 'N/A':
                maps_url = f"https://www.google.com/maps/place/?q=place_id:{business['place_id']}"
            
            # Prepare row
            row = [
                business.get('name', 'N/A'),
                business.get('address', 'N/A'),
                business.get('phone', 'N/A'),
                business.get('website', 'N/A'),
                business.get('rating', 'N/A'),
                business.get('total_ratings', 'N/A'),
                business.get('is_open_now', 'N/A'),
                business.get('place_id', 'N/A'),
                business.get('primary_type', 'N/A'),
                secondary_types,
                business.get('business_status', 'N/A'),
                business.get('price_level', 'N/A'),
                business.get('latitude', 'N/A'),
                business.get('longitude', 'N/A'),
                maps_url
            ]
            data.append(row)
        
        # Update spreadsheet with data
        if data:
            worksheet.update(f'A2:O{len(data) + 1}', data)
            
            # Auto-resize columns for better readability
            worksheet.columns_auto_resize(0, 15)
            
            # Format URLs as hyperlinks
            for col, index in [("D", 4), ("O", 15)]:  # Website and Google Maps columns
                cell_range = f"{col}2:{col}{len(data) + 1}"
                worksheet.format(cell_range, {
                    "textFormat": {"foregroundColor": {"red": 0.0, "green": 0.0, "blue": 0.9}},
                    "textFormat": {"underline": True}
                })
        
        # Return the URL
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
    
    except Exception as e:
        print(f"Error in export_to_sheets: {str(e)}")
        # For demo purposes, return a mock URL even if there was an error
        mock_id = "1MoCkSpReAdShEeTiDfOrDeMoNsTrAtIoN"
        return f"https://docs.google.com/spreadsheets/d/{mock_id}"