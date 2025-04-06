import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from business_finder.config import get_api_key, save_api_key


class TestConfig:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        # Save current environment variables
        self.original_env = os.environ.copy()

        # Provide the fixture
        yield

        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test_api_key_env"})
    def test_get_api_key_from_env(self):
        # Test getting API key from environment variable
        api_key = get_api_key()
        assert api_key == "test_api_key_env"

    @patch.dict(os.environ, {}, clear=True)  # Clear environment variables
    @patch("business_finder.config.Path.home")
    def test_get_api_key_from_config_file(self, mock_home):
        # Setup mock home directory and config file
        mock_home_dir = Path("/mock/home")
        mock_home.return_value = mock_home_dir

        config_data = {"api_key": "test_api_key_file"}

        # Mock the open function and file operations
        with patch("builtins.open", mock_open(read_data=json.dumps(config_data))) as m:
            # Mock the file exists check
            with patch("business_finder.config.Path.exists", return_value=True):
                api_key = get_api_key()

                assert api_key == "test_api_key_file"
                m.assert_called_once_with(
                    mock_home_dir / ".business_finder" / "config.json", "r"
                )

    @patch.dict(os.environ, {}, clear=True)  # Clear environment variables
    @patch("business_finder.config.Path.home")
    def test_get_api_key_no_config(self, mock_home):
        # Setup mock home directory
        mock_home_dir = Path("/mock/home")
        mock_home.return_value = mock_home_dir

        # Mock the file exists check to return False
        with patch("business_finder.config.Path.exists", return_value=False):
            api_key = get_api_key()
            assert api_key is None

    @patch.dict(os.environ, {}, clear=True)  # Clear environment variables
    @patch("business_finder.config.Path.home")
    def test_get_api_key_invalid_config(self, mock_home):
        # Setup mock home directory
        mock_home_dir = Path("/mock/home")
        mock_home.return_value = mock_home_dir

        # Mock the file exists check
        with patch("business_finder.config.Path.exists", return_value=True):
            # Mock open to raise JSONDecodeError
            with patch("builtins.open", mock_open(read_data="invalid json")):
                api_key = get_api_key()
                assert api_key is None

    @patch("business_finder.config.Path.home")
    def test_save_api_key_new_file(self, mock_home):
        # Setup mock home directory
        mock_home_dir = Path("/mock/home")
        mock_home.return_value = mock_home_dir

        # Mock directory and file operations
        with patch("business_finder.config.Path.mkdir") as mock_mkdir:
            with patch("business_finder.config.Path.exists", return_value=False):
                with patch("builtins.open", mock_open()) as m:
                    save_api_key("new_test_api_key")

                    # Verify directory was created
                    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

                    # Verify file was written
                    handle = m()
                    assert handle.write.called

                    # Check if one of the write calls contains our new key
                    write_args = []
                    for call_obj in handle.write.call_args_list:
                        args = call_obj[0]
                        if args and len(args) > 0:
                            write_args.append(args[0])

                    assert any(
                        "new_test_api_key" in arg
                        for arg in write_args
                        if isinstance(arg, str)
                    )

    @patch("business_finder.config.Path.home")
    def test_save_api_key_existing_file(self, mock_home):
        # Setup mock home directory
        mock_home_dir = Path("/mock/home")
        mock_home.return_value = mock_home_dir

        existing_config = {"api_key": "old_api_key", "other_setting": "value"}

        # Mock directory and file operations
        with patch("business_finder.config.Path.mkdir") as mock_mkdir:
            with patch("business_finder.config.Path.exists", return_value=True):
                # Mock reading existing config
                with patch(
                    "builtins.open", mock_open(read_data=json.dumps(existing_config))
                ) as m:
                    save_api_key("updated_api_key")

                    # Verify directory was created
                    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

                    # Verify file was written
                    handle = m()
                    assert handle.write.called

                    # Check if the write calls contain our key and preserved settings
                    write_args = []
                    for call_obj in handle.write.call_args_list:
                        args = call_obj[0]
                        if args and len(args) > 0:
                            write_args.append(args[0])

                    assert any(
                        "updated_api_key" in arg
                        for arg in write_args
                        if isinstance(arg, str)
                    )
                    assert any(
                        "other_setting" in arg
                        for arg in write_args
                        if isinstance(arg, str)
                    )
