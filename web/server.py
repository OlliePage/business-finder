#!/usr/bin/env python3
"""
Simple backend server for the Business Finder web app
This connects the web interface to the CLI tool
"""

import json
import os
import subprocess
import sys
import sqlite3
import time
import hashlib
from datetime import datetime, timedelta
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

# Database setup
DATA_DIR = os.path.join(parent_dir, 'data')
DB_PATH = os.path.join(DATA_DIR, 'search_cache.db')

# Ensure the database path is in .gitignore to prevent committing large databases
def ensure_in_gitignore():
    """Make sure the database file is in .gitignore"""
    gitignore_path = os.path.join(parent_dir, '.gitignore')
    db_rel_path = os.path.join('data', 'search_cache.db')
    
    # Create gitignore if it doesn't exist
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, 'w') as f:
            f.write(f"# Database files\n{db_rel_path}\n")
        return
    
    # Check if entry exists in gitignore
    with open(gitignore_path, 'r') as f:
        content = f.read()
    
    if db_rel_path not in content:
        with open(gitignore_path, 'a') as f:
            f.write(f"\n# Database files\n{db_rel_path}\n")
            
    # Also ignore the entire data directory if not already ignored
    if 'data/' not in content and '/data/' not in content:
        with open(gitignore_path, 'a') as f:
            f.write("# Ignore data directory contents except for .gitkeep\n")
            f.write("data/*\n")
            f.write("!data/.gitkeep\n")

def init_database():
    """Initialize the SQLite database for caching search results"""
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Create a .gitkeep file to ensure the directory is tracked but contents are ignored
    gitkeep_path = os.path.join(DATA_DIR, '.gitkeep')
    if not os.path.exists(gitkeep_path):
        with open(gitkeep_path, 'w') as f:
            f.write("# This file ensures the data directory is tracked by git\n")
    
    # Ensure the database is in gitignore
    ensure_in_gitignore()
    
    # Check if the database already exists
    db_exists = os.path.exists(DB_PATH)
    
    # Connect to database (creates it if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create searches table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        search_term TEXT,
        latitude REAL,
        longitude REAL,
        radius INTEGER,
        created_at TIMESTAMP,
        hash TEXT UNIQUE
    )
    ''')
    
    # Create results table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        search_id INTEGER,
        json_data TEXT,
        FOREIGN KEY (search_id) REFERENCES searches (id) ON DELETE CASCADE
    )
    ''')
    
    # Enable foreign keys for cascading deletes
    cursor.execute("PRAGMA foreign_keys = ON")
    
    conn.commit()
    conn.close()
    
    # Print appropriate message based on whether DB existed
    if db_exists:
        print(f"Connected to existing database at {DB_PATH}")
    else:
        print(f"Created new database at {DB_PATH}")
        
    # Log the database size
    if os.path.exists(DB_PATH):
        size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
        print(f"Database size: {size_mb:.2f} MB")

def hash_params(params):
    """Create a unique hash for the search parameters"""
    # Sort parameters for consistent hashing
    param_string = json.dumps(params, sort_keys=True)
    return hashlib.md5(param_string.encode()).hexdigest()

def cache_search_results(params, results):
    """Store search results in the cache"""
    print(f"Caching search results for '{params.get('search_term', 'unknown')}' search...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create a hash of parameters for lookup
        param_hash = hash_params(params)
        print(f"Parameter hash: {param_hash}")
        
        # Check if this search already exists
        cursor.execute("SELECT id FROM searches WHERE hash = ?", (param_hash,))
        existing = cursor.fetchone()
        
        if existing:
            search_id = existing[0]
            print(f"Updating existing search with ID {search_id}")
            # Update the timestamp
            cursor.execute("UPDATE searches SET created_at = ? WHERE id = ?", 
                          (datetime.now().isoformat(), search_id))
            print("Timestamp updated")
        else:
            # Insert new search
            print("Creating new search record")
            cursor.execute('''
            INSERT INTO searches 
            (search_term, latitude, longitude, radius, created_at, hash)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                params.get('search_term', ''),
                params.get('latitude', 0),
                params.get('longitude', 0),
                params.get('radius', 0),
                datetime.now().isoformat(),
                param_hash
            ))
            search_id = cursor.lastrowid
            print(f"New search created with ID {search_id}")
            
            # Insert results
            print(f"Inserting {len(results) if isinstance(results, list) else 'non-list'} results")
            cursor.execute('''
            INSERT INTO results (search_id, json_data)
            VALUES (?, ?)
            ''', (search_id, json.dumps(results)))
            print("Results inserted")
        
        conn.commit()
        print("Database changes committed")
        
        # Verify the search was saved
        cursor.execute("SELECT COUNT(*) FROM searches")
        total_searches = cursor.fetchone()[0]
        print(f"Total searches in database: {total_searches}")
        
        return True
    except Exception as e:
        print(f"Error caching search results: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_cached_results(params):
    """Get cached search results if they exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        param_hash = hash_params(params)
        
        # Get the search and results
        cursor.execute('''
        SELECT s.id, s.search_term, s.latitude, s.longitude, s.radius, s.created_at, r.json_data
        FROM searches s
        JOIN results r ON s.id = r.search_id
        WHERE s.hash = ?
        ''', (param_hash,))
        
        result = cursor.fetchone()
        
        if result:
            search_info = {
                'id': result[0],
                'search_term': result[1],
                'latitude': result[2],
                'longitude': result[3],
                'radius': result[4],
                'created_at': result[5]
            }
            return {
                'search': search_info,
                'results': json.loads(result[6]),
                'cached': True
            }
        return None
    except Exception as e:
        print(f"Error retrieving cached results: {e}")
        return None
    finally:
        conn.close()

def get_recent_searches(limit=10):
    """Get a list of recent searches"""
    print(f"Getting recent searches (limit={limit})...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # First check if there are any searches at all
        cursor.execute("SELECT COUNT(*) FROM searches")
        count = cursor.fetchone()[0]
        print(f"Found {count} total searches in database")
        
        # Get the most recent searches
        cursor.execute('''
        SELECT id, search_term, latitude, longitude, radius, created_at
        FROM searches
        ORDER BY created_at DESC
        LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        print(f"Retrieved {len(rows)} recent searches")
        
        searches = []
        for row in rows:
            searches.append({
                'id': row[0],
                'search_term': row[1],
                'latitude': row[2],
                'longitude': row[3],
                'radius': row[4],
                'created_at': row[5]
            })
        
        print(f"Returning {len(searches)} formatted searches")
        return searches
    except Exception as e:
        print(f"Error retrieving recent searches: {e}")
        return []
    finally:
        conn.close()

def get_search_by_id(search_id):
    """Get a specific search and its results by ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get the search and results
        cursor.execute('''
        SELECT s.id, s.search_term, s.latitude, s.longitude, s.radius, s.created_at, r.json_data
        FROM searches s
        JOIN results r ON s.id = r.search_id
        WHERE s.id = ?
        ''', (search_id,))
        
        result = cursor.fetchone()
        
        if result:
            search_info = {
                'id': result[0],
                'search_term': result[1],
                'latitude': result[2],
                'longitude': result[3],
                'radius': result[4],
                'created_at': result[5]
            }
            return {
                'search': search_info,
                'results': json.loads(result[6]),
                'cached': True
            }
        return None
    except Exception as e:
        print(f"Error retrieving search by ID: {e}")
        return None
    finally:
        conn.close()

def delete_search(search_id):
    """Delete a search and its results from the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Enable foreign keys for cascading delete
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Delete the search (results will be deleted via cascade)
        cursor.execute("DELETE FROM searches WHERE id = ?", (search_id,))
        
        # Check if any rows were affected
        rows_affected = cursor.rowcount
        conn.commit()
        return rows_affected > 0
    except Exception as e:
        print(f"Error deleting search {search_id}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def clean_old_searches(days=30):
    """Delete searches older than the specified number of days"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Enable foreign keys for cascading delete
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Calculate the cutoff date
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Find searches to delete
        cursor.execute("SELECT id FROM searches WHERE created_at < ?", (cutoff_date,))
        old_searches = cursor.fetchall()
        
        # Delete old searches
        cursor.execute("DELETE FROM searches WHERE created_at < ?", (cutoff_date,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        
        print(f"Cleaned up {deleted_count} searches older than {days} days")
        return deleted_count
    except Exception as e:
        print(f"Error cleaning old searches: {e}")
        conn.rollback()
        return 0
    finally:
        conn.close()

def get_db_stats():
    """Get database statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get search count
        cursor.execute("SELECT COUNT(*) FROM searches")
        search_count = cursor.fetchone()[0]
        
        # Get result count
        cursor.execute("SELECT COUNT(*) FROM results")
        result_count = cursor.fetchone()[0]
        
        # Get oldest search date
        cursor.execute("SELECT MIN(created_at) FROM searches")
        oldest_date = cursor.fetchone()[0]
        
        # Get newest search date
        cursor.execute("SELECT MAX(created_at) FROM searches")
        newest_date = cursor.fetchone()[0]
        
        # Get database size
        db_size = os.path.getsize(DB_PATH) / (1024 * 1024)  # Size in MB
        
        return {
            'search_count': search_count,
            'result_count': result_count,
            'oldest_date': oldest_date,
            'newest_date': newest_date,
            'db_size_mb': round(db_size, 2)
        }
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return None
    finally:
        conn.close()

class BusinessFinderHandler(SimpleHTTPRequestHandler):
    """HTTP request handler for Business Finder web app"""

    def do_GET(self):
        """Handle GET requests - serve static files"""
        # Redirect root path to index.html
        if self.path == '/':
            self.path = '/index.html'
            
        # Get API key from environment/config
        api_key = get_api_key()
        
        # Special handling for index.html to inject API key
        if self.path.endswith('index.html'):
            if api_key:
                print(f"Using API key: {api_key[:5]}...")
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                # Read the HTML file
                with open(os.path.join(os.getcwd(), 'index.html'), 'r') as file:
                    html_content = file.read()
                
                # Replace the placeholder with the API key
                modified_content = html_content.replace('YOUR_API_KEY_PLACEHOLDER', api_key)
                
                # Send the modified content
                self.wfile.write(modified_content.encode('utf-8'))
                return
            else:
                print("Warning: No API key found, Google Maps will not work correctly")
        
        # Serve static files for all other requests
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        """Handle POST requests - API endpoints"""
        if self.path == "/api/search":
            self.handle_search()
        elif self.path == "/api/recent_searches":
            self.handle_recent_searches()
        elif self.path.startswith("/api/search_by_id/"):
            search_id = self.path.split("/")[-1]
            self.handle_search_by_id(search_id)
        elif self.path.startswith("/api/delete_search/"):
            search_id = self.path.split("/")[-1]
            self.handle_delete_search(search_id)
        elif self.path == "/api/db_stats":
            self.handle_db_stats()
        elif self.path.startswith("/api/clean_old_searches/"):
            days = self.path.split("/")[-1]
            self.handle_clean_old_searches(days)
        else:
            self.send_error(404, "Not Found")
            
    def handle_delete_search(self, search_id):
        """Handle deletion of a search"""
        try:
            search_id = int(search_id)
            success = delete_search(search_id)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Return result
            result = {'success': success, 'id': search_id}
            self.wfile.write(json.dumps(result).encode())
        except ValueError:
            self.send_error(400, "Invalid search ID")
        except Exception as e:
            print(f"Error handling delete search: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
            
    def handle_db_stats(self):
        """Handle database statistics request"""
        try:
            stats = get_db_stats()
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Return result
            self.wfile.write(json.dumps(stats).encode())
        except Exception as e:
            print(f"Error handling database stats: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
            
    def handle_clean_old_searches(self, days_str):
        """Handle cleaning of old searches"""
        try:
            days = int(days_str)
            if days < 1:
                self.send_error(400, "Days must be a positive integer")
                return
                
            deleted_count = clean_old_searches(days)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Return result
            result = {'success': True, 'deleted_count': deleted_count, 'days': days}
            self.wfile.write(json.dumps(result).encode())
        except ValueError:
            self.send_error(400, "Invalid days parameter")
        except Exception as e:
            print(f"Error handling clean old searches: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
            
    def handle_recent_searches(self):
        """Return a list of recent searches"""
        try:
            recent_searches = get_recent_searches(20)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(recent_searches).encode())
        except Exception as e:
            print(f"Error getting recent searches: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def handle_search_by_id(self, search_id):
        """Return results for a specific search ID"""
        try:
            search_id = int(search_id)
            search_data = get_search_by_id(search_id)
            
            if search_data:
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(search_data).encode())
            else:
                self.send_error(404, "Search not found")
        except ValueError:
            self.send_error(400, "Invalid search ID")
        except Exception as e:
            print(f"Error getting search by ID: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")

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
            use_cache = params.get('use_cache', True)  # Default to using cache
            
            # Validate parameters
            if not all([search_term, latitude is not None, longitude is not None, radius]):
                self.send_error(400, "Missing required parameters")
                return
            
            # Create search params dict for cache lookup
            search_params = {
                'search_term': search_term,
                'latitude': latitude,
                'longitude': longitude,
                'radius': radius
            }
            
            # Check cache first if enabled
            if use_cache:
                cache_result = get_cached_results(search_params)
                if cache_result:
                    print(f'Using cached results for "{search_term}" search')
                    
                    # Send response with cache info
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(cache_result['results']).encode())
                    return
            
            # Get API key from environment
            api_key = get_api_key()
            if not api_key:
                self.send_error(500, "API key not found in environment")
                return
            
            # Call business_finder directly with the parameters
            print(f'Searching for "{search_term}" within {radius}m of coordinates [{latitude}, {longitude}]...')
            businesses = search_places(api_key, search_term, latitude, longitude, radius)
            
            # Save results to data directory
            data_dir = os.path.join(parent_dir, 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Save a copy to data directory
            with open(os.path.join(data_dir, 'latest_search_results.json'), 'w') as f:
                json.dump(businesses, f, indent=2)
            
            # Cache the results
            cache_result = cache_search_results(search_params, businesses)
            print(f"Cache result: {'Success' if cache_result else 'Failed'}")
            
            # Verify the search was added to the database
            recent_searches = get_recent_searches(5)
            print(f"Recent searches after adding: {len(recent_searches)}")
            for s in recent_searches:
                print(f"  - ID {s['id']}: {s['search_term']} ({s['created_at']})")
            
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
    # Change to the web directory to serve files from there
    web_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_dir)
    
    # Initialize the database
    init_database()
    
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