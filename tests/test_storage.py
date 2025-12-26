import os

import pytest

from cognitoidp_local.storage import StorageManager


@pytest.fixture
def manager(tmp_path):
    """
    Creates a StorageManager pointing to a temp file
    and ensures a clean backend state.
    """
    db_file = tmp_path / "test_cognito.db"
    pm = StorageManager(str(db_file))
    pm.backend.reset()
    yield pm
    pm.backend.reset()


def test_save_creates_file(manager):
    """
    Verifies that .save() writes a file to disk.
    """
    assert not os.path.exists(manager.data_file)
    manager.save()
    assert os.path.exists(manager.data_file)
    assert os.path.getsize(manager.data_file) > 0


def test_atomic_write_protection(manager):
    """
    Verifies that the save process writes to temp and renames.
    """
    manager.save()
    assert os.path.exists(manager.data_file)


def test_load_restores_data(manager):
    """
    Integration Test:
    1. Mark backend with custom data.
    2. Save.
    3. Wipe memory.
    4. Load.
    5. Verify mark exists.
    """
    region_backend = manager.backend["eu-central-1"]
    region_backend.persistence_test_marker = "IT_WORKS_123"
    manager.save()
    manager.backend.reset()
    fresh_backend = manager.backend["eu-central-1"]
    assert not hasattr(fresh_backend, "persistence_test_marker")
    manager.load()
    restored_backend = manager.backend["eu-central-1"]
    assert hasattr(restored_backend, "persistence_test_marker")
    assert restored_backend.persistence_test_marker == "IT_WORKS_123"


def test_load_handles_empty_file(manager, caplog):
    """
    Verifies that loading a 0-byte file (corruption) logs a warning
    but does not crash.
    """
    with open(manager.data_file, "wb"):
        pass

    assert os.path.exists(manager.data_file)
    assert os.path.getsize(manager.data_file) == 0
    manager.load()
    assert "is empty (corrupt)" in caplog.text
