# File: business_finder/config.py
import json
import os
from pathlib import Path


def get_api_key():
    """Get Google API key from environment or config file"""
    # First check environment variable
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        return api_key

    # Then check config file
    config_file = Path.home() / ".business_finder" / "config.json"
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                return config.get("api_key")
        except (json.JSONDecodeError, IOError):
            pass

    return None


def save_api_key(api_key):
    """Save API key to config file"""
    config_dir = Path.home() / ".business_finder"
    config_file = config_dir / "config.json"

    # Create directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)

    config = {}
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    config["api_key"] = api_key

    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
