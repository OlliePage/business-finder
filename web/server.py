#!/usr/bin/env python3
"""
Simple backend server for the Business Finder web app
This connects the web interface to the CLI tool
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

# Add parent directory to path so we can import from business_finder
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

from business_finder.api.places import search_places
from business_finder.config import get_api_key

# Default port
PORT = 8000

class BusinessFinderHandler(SimpleHTTPRequestHandler):
    """HTTP request handler for Business Finder web app"""

    def do_GET(self):
        """Handle GET requests - serve static files"""
        # Serve static files
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        """Handle POST requests - API endpoints"""
        if self.path == "/api/search":
            self.handle_search()
        else:
            self.send_error(404, "Not Found")

    def handle_search(self):
        """Handle search API requests"""
        # Get request body
        content_length = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            # Parse JSON parameters
            params = json.loads(post_body)
            search_term = params.get('search_term', 'business')
            latitude = params.get('latitude')
            longitude = params.get('longitude')
            radius = params.get('radius', 1000)
            
            # Validate parameters
            if not all([search_term, latitude is not None, longitude is not None, radius]):
                self.send_error(400, "Missing required parameters")
                return
            
            # Get API key from environment
            api_key = get_api_key()
            if not api_key:
                self.send_error(500, "API key not found in environment")
                return
            
            # Call business_finder directly with the parameters
            print(f'Searching for "{search_term}" within {radius}m of coordinates [{latitude}, {longitude}]...')
            businesses = search_places(api_key, search_term, latitude, longitude, radius)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')  # Enable CORS
            self.end_headers()
            
            # Convert to JSON and send
            self.wfile.write(json.dumps(businesses).encode())
            
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            print(f"Error processing request: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")

def run_server(port=PORT):
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, BusinessFinderHandler)
    print(f"Starting Business Finder server on port {port}...")
    print(f"Open http://localhost:{port} in your browser")
    httpd.serve_forever()

if __name__ == "__main__":
    # Get port from command line if provided
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}")
            sys.exit(1)
    else:
        port = PORT
    
    run_server(port)