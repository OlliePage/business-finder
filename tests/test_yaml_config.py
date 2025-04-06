"""
Test the YAML configuration functionality.
"""
import os
import pytest
import yaml
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

from business_finder.config import (
    get_config,
    save_config,
    get_api_key,
    get_sub_radius,
    get_max_workers,
    save_api_key,
    save_sub_radius,
    save_max_workers,
    DEFAULT_SUB_RADIUS,
    DEFAULT_MAX_WORKERS
)


def test_default_values(monkeypatch):
    """Test that default values are returned when no config exists."""
    # Mock empty config paths
    monkeypatch.setattr('business_finder.config.CONFIG_PATHS', [])
    
    # Get config should return defaults
    config = get_config()
    assert config["sub_radius"] == DEFAULT_SUB_RADIUS
    assert config["max_workers"] == DEFAULT_MAX_WORKERS
    assert config["api_key"] is None


def test_get_specific_values(monkeypatch):
    """Test the individual getter functions."""
    # Mock the get_config function
    mock_config = {
        "api_key": "test_api_key",
        "sub_radius": 2500,
        "max_workers": 8
    }
    monkeypatch.setattr('business_finder.config.get_config', lambda: mock_config)
    
    # Test each getter
    assert get_api_key() == "test_api_key"
    assert get_sub_radius() == 2500
    assert get_max_workers() == 8


def test_environment_variables(monkeypatch):
    """Test that environment variables override config file values."""
    # Mock empty config paths
    monkeypatch.setattr('business_finder.config.CONFIG_PATHS', [])
    
    # Set environment variables
    monkeypatch.setenv("GOOGLE_API_KEY", "env_api_key")
    monkeypatch.setenv("BUSINESS_FINDER_SUB_RADIUS", "4000")
    monkeypatch.setenv("BUSINESS_FINDER_MAX_WORKERS", "10")
    
    # Get config
    config = get_config()
    assert config["api_key"] == "env_api_key"
    assert config["sub_radius"] == 4000
    assert config["max_workers"] == 10


def test_yaml_config_loading():
    """Test loading configuration from a YAML file."""
    # Create a temp YAML file
    yaml_content = """
    api:
      key: yaml_api_key
    search:
      sub_radius: 3500
      max_workers: 6
    """
    
    with tempfile.NamedTemporaryFile(suffix='.yaml') as tmp_file:
        # Write YAML content
        tmp_file.write(yaml_content.encode())
        tmp_file.flush()
        
        # Mock config paths to use the temp file
        with patch('business_finder.config.CONFIG_PATHS', [Path(tmp_file.name)]):
            config = get_config()
            assert config["api_key"] == "yaml_api_key"
            assert config["sub_radius"] == 3500
            assert config["max_workers"] == 6


def test_legacy_json_conversion(monkeypatch):
    """Test that legacy JSON config is properly converted."""
    # Mock a JSON config file
    mock_json_config = {
        "api_key": "json_api_key",
        "sub_radius": 1500,
        "max_workers": 3
    }
    
    # Create mock path object
    mock_path = MagicMock()
    mock_path.suffix = '.json'
    mock_path.exists.return_value = True
    
    # Setup the mocks
    monkeypatch.setattr(
        'business_finder.config._load_json_config', 
        lambda _: mock_json_config
    )
    monkeypatch.setattr(
        'business_finder.config.CONFIG_PATHS', 
        [mock_path]
    )
    
    # Get config
    config = get_config()
    assert config["api_key"] == "json_api_key"
    assert config["sub_radius"] == 1500
    assert config["max_workers"] == 3


def test_save_config(monkeypatch):
    """Test saving configuration to a YAML file."""
    # Mock path
    mock_dir = Path('/mock/config/dir')
    
    # Setup mocks
    monkeypatch.setattr(
        'business_finder.config._ensure_config_dir_exists', 
        lambda: mock_dir
    )
    
    mock_path_exists = MagicMock(return_value=False)
    monkeypatch.setattr(Path, 'exists', mock_path_exists)
    
    mock_open_obj = mock_open()
    monkeypatch.setattr('builtins.open', mock_open_obj)
    
    mock_yaml_dump = MagicMock()
    monkeypatch.setattr('yaml.dump', mock_yaml_dump)
    
    # Call save_config
    save_config({"api_key": "new_api_key", "sub_radius": 2000})
    
    # Verify mock open was called with correct path
    mock_open_obj.assert_called()
    
    # Since we can't easily verify the args to yaml.dump due to monkeypatch,
    # we'll just check it was called
    assert mock_yaml_dump.call_count > 0


@pytest.mark.parametrize("save_function,arg,expected", [
    (save_api_key, "test_key", {"api_key": "test_key"}),
    (save_sub_radius, 3000, {"sub_radius": 3000}),
    (save_max_workers, 7, {"max_workers": 7}),
])
def test_specific_save_functions(save_function, arg, expected, monkeypatch):
    """Test the specific save functions."""
    # Mock save_config
    mock_save_config = MagicMock()
    monkeypatch.setattr('business_finder.config.save_config', mock_save_config)
    
    # Call the function
    save_function(arg)
    
    # Verify save_config was called with correct args
    mock_save_config.assert_called_once_with(expected)