import os
from unittest import mock

from cognitoidp_local import main


def test_get_data_file_path_env_var():
    """Priority 1: Should use DATA_FILE env var if set."""
    with mock.patch.dict(os.environ, {"DATA_FILE": "/custom/path.db"}):
        path = main.get_data_file_path()
        assert path == "/custom/path.db"


def test_get_data_file_path_docker_volume():
    """Priority 2: Should use /data/cognito.db if /data exists and is writable."""
    with mock.patch.dict(os.environ, {}, clear=True):
        # Mock os.path.exists and os.access
        with (
            mock.patch("os.path.exists") as mock_exists,
            mock.patch("os.access") as mock_access,
        ):
            # Simulate /data exists
            def exists_side_effect(path):
                return path == "/data"

            mock_exists.side_effect = exists_side_effect

            # Simulate /data is writable
            mock_access.return_value = True

            path = main.get_data_file_path()
            assert path == "/data/cognito.db"


def test_get_data_file_path_fallback():
    """Priority 3: Should fall back to a local file if /data doesn't exist."""
    with mock.patch.dict(os.environ, {}, clear=True):
        with mock.patch("os.path.exists") as mock_exists:
            # Simulate /data does NOT exist
            mock_exists.return_value = False

            path = main.get_data_file_path()
            assert path == "./cognito.db"
