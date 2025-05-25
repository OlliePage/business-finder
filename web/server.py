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

from business_finder.api.places import search_places, get_search_logs
from business_finder.config import get_api_key, get_config

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

def migrate_database(conn, cursor):
    """Apply migrations to the database schema"""
    print("Checking for needed database migrations...")
    
    # Check if sub_radius column exists
    cursor.execute("PRAGMA table_info(searches)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Add sub_radius column if it doesn't exist
    if 'sub_radius' not in columns:
        print("Migrating: Adding sub_radius column to searches table")
        cursor.execute("ALTER TABLE searches ADD COLUMN sub_radius INTEGER DEFAULT 3000")
        conn.commit()
    
    # Add max_workers column if it doesn't exist
    if 'max_workers' not in columns:
        print("Migrating: Adding max_workers column to searches table")
        cursor.execute("ALTER TABLE searches ADD COLUMN max_workers INTEGER DEFAULT 5")
        conn.commit()
    
    # Add adapt_sub_radius column if it doesn't exist
    if 'adapt_sub_radius' not in columns:
        print("Migrating: Adding adapt_sub_radius column to searches table")
        cursor.execute("ALTER TABLE searches ADD COLUMN adapt_sub_radius BOOLEAN DEFAULT 1")
        conn.commit()
    
    # Add filter columns if they don't exist
    if 'min_price' not in columns:
        print("Migrating: Adding min_price column to searches table")
        cursor.execute("ALTER TABLE searches ADD COLUMN min_price INTEGER")
        conn.commit()
    
    if 'max_price' not in columns:
        print("Migrating: Adding max_price column to searches table")
        cursor.execute("ALTER TABLE searches ADD COLUMN max_price INTEGER")
        conn.commit()
    
    if 'open_now' not in columns:
        print("Migrating: Adding open_now column to searches table")
        cursor.execute("ALTER TABLE searches ADD COLUMN open_now BOOLEAN")
        conn.commit()
    
    if 'place_type' not in columns:
        print("Migrating: Adding place_type column to searches table")
        cursor.execute("ALTER TABLE searches ADD COLUMN place_type TEXT")
        conn.commit()
    
    print("Database migration checks completed")


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
        sub_radius INTEGER DEFAULT 3000,
        max_workers INTEGER DEFAULT 5,
        adapt_sub_radius BOOLEAN DEFAULT 1,
        min_price INTEGER,
        max_price INTEGER,
        open_now BOOLEAN,
        place_type TEXT,
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
    
    # Run migrations if database already existed
    if db_exists:
        migrate_database(conn, cursor)
    
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
    # Create a copy of the parameters to modify
    params_copy = params.copy()
    
    # Round latitude and longitude to 1 decimal place for more flexible caching
    if 'latitude' in params_copy and params_copy['latitude'] is not None:
        params_copy['latitude'] = round(float(params_copy['latitude']), 1)
    if 'longitude' in params_copy and params_copy['longitude'] is not None:
        params_copy['longitude'] = round(float(params_copy['longitude']), 1)
    
    # Sort parameters for consistent hashing
    param_string = json.dumps(params_copy, sort_keys=True)
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
            (search_term, latitude, longitude, radius, sub_radius, max_workers, adapt_sub_radius, min_price, max_price, open_now, place_type, created_at, hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                params.get('search_term', ''),
                params.get('latitude', 0),
                params.get('longitude', 0),
                params.get('radius', 0),
                params.get('sub_radius', 3000),
                params.get('max_workers', 5),
                params.get('adapt_sub_radius', True),
                params.get('min_price'),
                params.get('max_price'),
                params.get('open_now'),
                params.get('place_type'),
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
        
        # Log the cache lookup
        rounded_lat = round(float(params.get('latitude', 0)), 1)
        rounded_lng = round(float(params.get('longitude', 0)), 1)
        print(f"Looking for cached results with hash {param_hash} (coords rounded to {rounded_lat}, {rounded_lng})")
        
        # Get the search and results
        cursor.execute('''
        SELECT s.id, s.search_term, s.latitude, s.longitude, s.radius, s.sub_radius, s.max_workers, s.adapt_sub_radius, s.min_price, s.max_price, s.open_now, s.place_type, s.created_at, r.json_data
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
                'sub_radius': result[5],
                'max_workers': result[6],
                'adapt_sub_radius': bool(result[7]),
                'min_price': result[8],
                'max_price': result[9],
                'open_now': bool(result[10]) if result[10] is not None else None,
                'place_type': result[11],
                'created_at': result[12]
            }
            return {
                'search': search_info,
                'results': json.loads(result[13]),
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
        SELECT id, search_term, latitude, longitude, radius, sub_radius, max_workers, adapt_sub_radius, created_at
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
                'sub_radius': row[5],
                'max_workers': row[6],
                'adapt_sub_radius': bool(row[7]),
                'created_at': row[8]
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
        SELECT s.id, s.search_term, s.latitude, s.longitude, s.radius, s.sub_radius, s.max_workers, s.adapt_sub_radius, s.min_price, s.max_price, s.open_now, s.place_type, s.created_at, r.json_data
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
                'sub_radius': result[5],
                'max_workers': result[6],
                'adapt_sub_radius': bool(result[7]),
                'min_price': result[8],
                'max_price': result[9],
                'open_now': bool(result[10]) if result[10] is not None else None,
                'place_type': result[11],
                'created_at': result[12]
            }
            return {
                'search': search_info,
                'results': json.loads(result[13]),
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
        elif self.path == "/api/search_logs":
            self.handle_search_logs()
        elif self.path == "/api/diagnostics":
            self.handle_diagnostics()
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
    
    def handle_search_logs(self):
        """Return the logs from the most recent search operation"""
        try:
            # Get logs from the places API
            logs = get_search_logs()
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(logs).encode())
        except Exception as e:
            print(f"Error getting search logs: {e}")
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
            
    def handle_diagnostics(self):
        """Handle diagnostic requests for debugging database issues"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get table structure
            cursor.execute("PRAGMA table_info(searches)")
            table_info = cursor.fetchall()
            column_names = [column[1] for column in table_info]
            
            # Run migration forcefully
            migrate_database(conn, cursor)
            
            # Test a search insertion
            test_params = {
                'search_term': 'TEST_SEARCH',
                'latitude': 0,
                'longitude': 0,
                'radius': 1000,
                'sub_radius': 3000,
                'max_workers': 5
            }
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            diagnostic_info = {
                "column_names": column_names,
                "migration_applied": True,
                "database_path": DB_PATH
            }
            
            self.wfile.write(json.dumps(diagnostic_info).encode())
            
        except Exception as e:
            print(f"Error running diagnostics: {e}")
            self.send_error(500, f"Diagnostic Error: {str(e)}")

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
            
            # Get defaults from config if not provided
            config = get_config()
            sub_radius = params.get('sub_radius', config['sub_radius'])
            max_workers = params.get('max_workers', config['max_workers'])
            # Default to using adaptive sub-radius and cache
            adapt_sub_radius = params.get('adapt_sub_radius', True)
            use_cache = params.get('use_cache', True)
            # Get output format
            output_format = params.get('output_format', 'csv')
            
            # Get new pre-search filter parameters
            min_price = params.get('min_price')
            max_price = params.get('max_price')
            open_now = params.get('open_now')
            place_type = params.get('place_type')
            
            # Validate price range parameters
            if min_price is not None:
                try:
                    min_price = int(min_price)
                    if not 0 <= min_price <= 4:
                        self.send_error(400, "min_price must be between 0 and 4")
                        return
                except (ValueError, TypeError):
                    self.send_error(400, "min_price must be a valid integer")
                    return
            
            if max_price is not None:
                try:
                    max_price = int(max_price)
                    if not 0 <= max_price <= 4:
                        self.send_error(400, "max_price must be between 0 and 4")
                        return
                except (ValueError, TypeError):
                    self.send_error(400, "max_price must be a valid integer")
                    return
            
            if open_now is not None:
                open_now = bool(open_now)
            
            # Validate parameters
            if not all([search_term, latitude is not None, longitude is not None, radius]):
                self.send_error(400, "Missing required parameters")
                return
            
            # Create search params dict for cache lookup (include filters for cache key)
            search_params = {
                'search_term': search_term,
                'latitude': latitude,
                'longitude': longitude,
                'radius': radius,
                'sub_radius': sub_radius,
                'max_workers': max_workers,
                'adapt_sub_radius': adapt_sub_radius,
                'min_price': min_price,
                'max_price': max_price,
                'open_now': open_now,
                'place_type': place_type
            }
            
            # Log original coordinates before rounding
            print(f"Original search coordinates: {latitude}, {longitude}")
            print(f"Will be rounded to: {round(float(latitude), 1)}, {round(float(longitude), 1)} for caching")
            
            # Check cache first if enabled
            if use_cache:
                cache_result = get_cached_results(search_params)
                if cache_result:
                    cached_lat = cache_result['search']['latitude']
                    cached_lng = cache_result['search']['longitude']
                    
                    # Calculate distance between original and cached coordinates
                    orig_lat_rounded = round(float(latitude), 1)
                    orig_lng_rounded = round(float(longitude), 1)
                    cached_lat_rounded = round(float(cached_lat), 1)
                    cached_lng_rounded = round(float(cached_lng), 1)
                    
                    print(f'Using cached results for "{search_term}" search')
                    print(f'Requested coords (rounded): {orig_lat_rounded}, {orig_lng_rounded}')
                    print(f'Cached coords (rounded): {cached_lat_rounded}, {cached_lng_rounded}')
                    
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
            
            if radius > sub_radius:
                print(f"Using grid search with sub-radius {sub_radius}m and {max_workers} parallel workers")
                
            businesses = search_places(
                api_key, 
                search_term, 
                latitude, 
                longitude, 
                radius, 
                sub_radius=sub_radius, 
                max_workers=max_workers,
                adapt_sub_radius=adapt_sub_radius,
                min_price=min_price,
                max_price=max_price,
                open_now=open_now,
                place_type=place_type
            )
            
            # Save results to data directory
            data_dir = os.path.join(parent_dir, 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Create a snake_case filename from the search term
            search_term_safe = search_term.lower().replace(' ', '_')
            # Remove any characters that aren't alphanumeric or underscore
            search_term_safe = ''.join(c if c.isalnum() or c == '_' else '_' for c in search_term_safe)
            # Remove consecutive underscores
            while '__' in search_term_safe:
                search_term_safe = search_term_safe.replace('__', '_')
            # Remove leading/trailing underscores
            search_term_safe = search_term_safe.strip('_')
            
            # Default to a simple name if the search term is empty or results in an empty string
            if not search_term_safe:
                search_term_safe = "business"
                
            # Add coordinates for more context
            lat_short = round(latitude, 2)
            lng_short = round(longitude, 2)
            
            # Create a descriptive filename
            results_filename = f"{search_term_safe}_at_{lat_short}_{lng_short}.json"
            
            # Save a copy to data directory
            with open(os.path.join(data_dir, results_filename), 'w') as f:
                json.dump(businesses, f, indent=2)
            
            # Cache the results
            cache_result = cache_search_results(search_params, businesses)
            print(f"Cache result: {'Success' if cache_result else 'Failed'}")
            
            # Verify the search was added to the database
            recent_searches = get_recent_searches(5)
            print(f"Recent searches after adding: {len(recent_searches)}")
            for s in recent_searches:
                print(f"  - ID {s['id']}: {s['search_term']} ({s['created_at']})")
            
            # Handle different output formats
            if output_format == 'sheets':
                # For Google Sheets export, we return the sheet URL in JSON format
                spreadsheet_name = params.get('sheets_name', f"Business Finder - {search_term}")
                
                # Get the project root directory
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                print(f"Project root directory: {project_root}")
                
                # Use credentials from project directory by default, unless explicitly specified
                credentials_path = params.get('sheets_credentials')
                if not credentials_path:
                    credentials_path = os.path.join(project_root, 'credentials', 'client_secret.json')
                
                token_path = params.get('sheets_token')
                if not token_path and credentials_path:
                    token_path = os.path.join(os.path.dirname(credentials_path), 'token.json')
                    
                # Verify credentials exist
                if os.path.exists(credentials_path):
                    print(f"Found credentials file at: {credentials_path}")
                    print(f"File size: {os.path.getsize(credentials_path)} bytes")
                else:
                    print(f"WARNING: Credentials file not found at: {credentials_path}")
                    
                # Verify token exists
                if os.path.exists(token_path):
                    print(f"Found token file at: {token_path}")
                    print(f"File size: {os.path.getsize(token_path)} bytes")
                else:
                    print(f"Token file not found at: {token_path} (not an error if first run)")
                
                # Import the export function from business_finder
                from business_finder.exporters.sheets_exporter import export_to_sheets
                
                # When in debug mode, print more info
                print(f"=== SHEETS EXPORT: SERVER DEBUG ===")
                print(f"Businesses count: {len(businesses)}")
                print(f"Spreadsheet name: {spreadsheet_name}")
                print(f"Credentials path: {credentials_path}")
                print(f"Token path: {token_path}")
                print(f"=================================")
                
                try:
                    # Export results to Google Sheets
                    print(f"Exporting to Google Sheets: {len(businesses)} businesses")
                    
                    # Don't create dummy data - if no businesses found, export empty sheet
                    if not businesses:
                        print("WARNING: No businesses found for the search criteria")
                        # Continue with empty list - Google Sheets export will handle this
                    
                    # Try export with verbose error handling
                    print("Calling export_to_sheets function with valid parameters...")
                    
                    # Force using test credentials for debugging
                    from pathlib import Path
                    project_root = Path(__file__).resolve().parent.parent
                    credentials_path = str(project_root / "credentials" / "client_secret.json")
                    token_path = str(project_root / "credentials" / "token.json")
                    
                    print(f"Using fixed credential paths:")
                    print(f"Credentials: {credentials_path} (exists: {os.path.exists(credentials_path)})")
                    print(f"Token: {token_path} (exists: {os.path.exists(token_path)})")
                    
                    sheet_url = export_to_sheets(
                        businesses, 
                        spreadsheet_name=spreadsheet_name,
                        credentials_path=credentials_path,
                        token_path=token_path
                    )
                    
                    print(f"Successfully exported to Google Sheets: {sheet_url}")
                    
                    # Send response with the URL
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')  # Enable CORS
                    self.end_headers()
                    
                    # Send the URL as JSON
                    self.wfile.write(json.dumps({
                        'success': True,
                        'url': sheet_url
                    }).encode())
                except Exception as e:
                    print(f"Error exporting to Google Sheets: {e}")
                    error_message = str(e)
                    
                    # Check for specific API errors
                    if 'Google Drive API has not been used' in error_message:
                        error_message = "Google Drive API is not enabled. Please visit the Google Cloud Console to enable it."
                    elif 'access_denied' in error_message:
                        error_message = "OAuth consent screen access denied. Make sure your email is added as a test user in the Google Cloud Console."
                    
                    # Log detailed error for debugging
                    import traceback
                    print(f"Detailed error: {traceback.format_exc()}")
                    
                    # Return proper error response instead of mock data
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')  # Enable CORS
                    self.end_headers()
                    
                    # Send proper error response
                    self.wfile.write(json.dumps({
                        'success': False,
                        'error': error_message,
                        'fix_instructions': "To fix Google Sheets export issues, please enable both Google Sheets API and Google Drive API in your Google Cloud Console and ensure proper OAuth credentials are configured."
                    }).encode())
            else:
                # For CSV and JSON formats, send the raw data
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