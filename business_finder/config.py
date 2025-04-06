# File: business_finder/config.py
import json
import os
import yaml
from pathlib import Path

# Default configuration values
DEFAULT_SUB_RADIUS = 3000  # 3 km in meters
DEFAULT_MAX_WORKERS = 5    # 5 parallel searches

# Default config structure
DEFAULT_CONFIG = {
    "api": {
        "key": None
    },
    "search": {
        "sub_radius": DEFAULT_SUB_RADIUS,
        "max_workers": DEFAULT_MAX_WORKERS
    },
    "export": {
        "default_format": "csv",
        "default_output_dir": "data"
    }
}

# Config file locations
CONFIG_PATHS = [
    # Global config
    Path.home() / ".business_finder" / "config.yaml",
    # Local config (project directory)
    Path(__file__).resolve().parent.parent / "config.yaml",
    # Legacy JSON config (for backwards compatibility)
    Path.home() / ".business_finder" / "config.json"
]

def _ensure_config_dir_exists():
    """Ensure the config directory exists"""
    config_dir = Path.home() / ".business_finder"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def _load_yaml_config(file_path):
    """Load configuration from YAML file"""
    try:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except (yaml.YAMLError, IOError, OSError):
        return None

def _load_json_config(file_path):
    """Load configuration from JSON file (legacy)"""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError, OSError):
        return None

def _convert_legacy_config(legacy_config):
    """Convert legacy flat config to new hierarchical format"""
    if not legacy_config:
        return {}
        
    new_config = {}
    
    # Convert API key
    if "api_key" in legacy_config:
        new_config.setdefault("api", {})["key"] = legacy_config["api_key"]
        
    # Convert search settings
    search_config = {}
    if "sub_radius" in legacy_config:
        search_config["sub_radius"] = legacy_config["sub_radius"]
    if "max_workers" in legacy_config:
        search_config["max_workers"] = legacy_config["max_workers"]
        
    if search_config:
        new_config["search"] = search_config
        
    return new_config

def _apply_env_vars(config):
    """Apply environment variables to config"""
    # API key from environment
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        config.setdefault("api", {})["key"] = api_key
        
    # Sub-radius from environment
    sub_radius = os.environ.get("BUSINESS_FINDER_SUB_RADIUS")
    if sub_radius:
        try:
            config.setdefault("search", {})["sub_radius"] = int(sub_radius)
        except ValueError:
            pass
            
    # Max workers from environment
    max_workers = os.environ.get("BUSINESS_FINDER_MAX_WORKERS")
    if max_workers:
        try:
            config.setdefault("search", {})["max_workers"] = int(max_workers)
        except ValueError:
            pass
            
    return config

def get_config():
    """Get configuration from environment, YAML config files and legacy JSON config"""
    # Start with default config
    config = DEFAULT_CONFIG.copy()
    
    # Try to load from config files in order of precedence
    for config_path in CONFIG_PATHS:
        if not config_path.exists():
            continue
            
        # Load based on file extension
        if config_path.suffix.lower() == '.yaml':
            file_config = _load_yaml_config(config_path)
        elif config_path.suffix.lower() == '.json':
            # If JSON, convert from legacy format
            legacy_config = _load_json_config(config_path)
            file_config = _convert_legacy_config(legacy_config)
        else:
            continue
            
        if not file_config:
            continue
            
        # Deep merge with current config
        _deep_merge(config, file_config)
    
    # Apply environment variables (highest precedence)
    config = _apply_env_vars(config)
    
    # Convert to old flat format for backwards compatibility with current code
    flat_config = {
        "api_key": config.get("api", {}).get("key"),
        "sub_radius": config.get("search", {}).get("sub_radius", DEFAULT_SUB_RADIUS),
        "max_workers": config.get("search", {}).get("max_workers", DEFAULT_MAX_WORKERS)
    }
    
    return flat_config

def _deep_merge(target, source):
    """Deep merge two dictionaries"""
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_merge(target[key], value)
        else:
            target[key] = value
    return target

def save_config(flat_config):
    """Save configuration to YAML config file"""
    # Convert from flat config to hierarchical
    hierarchical_config = {}
    
    if "api_key" in flat_config:
        hierarchical_config.setdefault("api", {})["key"] = flat_config["api_key"]
        
    if "sub_radius" in flat_config:
        hierarchical_config.setdefault("search", {})["sub_radius"] = flat_config["sub_radius"]
        
    if "max_workers" in flat_config:
        hierarchical_config.setdefault("search", {})["max_workers"] = flat_config["max_workers"]
    
    # Ensure config directory exists
    config_dir = _ensure_config_dir_exists()
    config_file = config_dir / "config.yaml"
    
    # Load existing config if it exists
    existing_config = {}
    if config_file.exists():
        existing_config = _load_yaml_config(config_file) or {}
    
    # Merge with existing config
    _deep_merge(existing_config, hierarchical_config)
    
    # Write back to file with helpful comments
    with open(config_file, "w") as f:
        f.write("# Business Finder Configuration\n")
        f.write("# This file is automatically generated and can be edited manually\n\n")
        
        yaml.dump(existing_config, f, default_flow_style=False, sort_keys=False)
        
    # For backwards compatibility, also update the JSON config
    legacy_file = config_dir / "config.json"
    if legacy_file.exists():
        try:
            with open(legacy_file, "r") as f:
                legacy_config = json.load(f)
        except (json.JSONDecodeError, IOError):
            legacy_config = {}
            
        # Update legacy config
        legacy_config.update(flat_config)
        
        # Write back to legacy file
        with open(legacy_file, "w") as f:
            json.dump(legacy_config, f, indent=2)
            

def get_api_key():
    """Get Google API key from environment or config file"""
    return get_config()["api_key"]


def get_sub_radius():
    """Get sub-radius for search grid from environment or config file"""
    return get_config()["sub_radius"]


def get_max_workers():
    """Get maximum number of concurrent workers from environment or config file"""
    return get_config()["max_workers"]


def save_api_key(api_key):
    """Save API key to config file"""
    save_config({"api_key": api_key})


def save_sub_radius(sub_radius):
    """Save sub-radius to config file"""
    save_config({"sub_radius": int(sub_radius)})


def save_max_workers(max_workers):
    """Save max workers to config file"""
    save_config({"max_workers": int(max_workers)})
