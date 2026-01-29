"""Integration tests for dubler synchronization."""

from pathlib import Path

import pytest

from dubler.config import Config
from dubler.state import StateManager
from dubler.sync import Synchronizer


class TestSyncIntegration:
    """Integration tests for synchronization functionality."""

    def test_sync_new_files_to_empty_destination(self, tmp_path: Path) -> None:
        """Test syncing new files to an empty destination."""
        # Setup source with nested directories and files
        source = tmp_path / "source"
        dest = tmp_path / "dest"

        source.mkdir()
        (source / "file1.txt").write_text("Hello, World!")
        (source / "file2.txt").write_text("Another file")
        (source / "subdir").mkdir()
        (source / "subdir" / "file3.txt").write_text("Nested file")

        # Sync
        state_dir = tmp_path / "state"
        state_manager = StateManager(state_dir)
        synchronizer = Synchronizer(state_manager)

        result = synchronizer.sync(source, [dest])

        # Verify
        assert len(result.copied) == 3
        assert len(result.skipped) == 0
        assert len(result.failed) == 0

        # Check files exist with correct content
        assert (dest / "file1.txt").exists()
        assert (dest / "file1.txt").read_text() == "Hello, World!"
        assert (dest / "file2.txt").read_text() == "Another file"
        assert (dest / "subdir" / "file3.txt").read_text() == "Nested file"

    def test_sync_skips_existing_files_with_same_content(self, tmp_path: Path) -> None:
        """Test that files with same checksum are skipped."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"

        source.mkdir()
        dest.mkdir()

        # Create identical files in both
        content = "Same content"
        (source / "file.txt").write_text(content)
        (dest / "file.txt").write_text(content)

        # Sync
        state_dir = tmp_path / "state"
        state_manager = StateManager(state_dir)
        synchronizer = Synchronizer(state_manager)

        result = synchronizer.sync(source, [dest])

        # Verify file was skipped
        assert len(result.copied) == 0
        assert len(result.skipped) == 1
        assert len(result.failed) == 0
        assert result.skipped[0] == (Path("file.txt"), str(dest))

    def test_sync_updates_files_with_different_content(self, tmp_path: Path) -> None:
        """Test that files with different checksums are updated."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"

        source.mkdir()
        dest.mkdir()

        # Create files with different content
        (source / "file.txt").write_text("New content")
        (dest / "file.txt").write_text("Old content")

        # Sync
        state_dir = tmp_path / "state"
        state_manager = StateManager(state_dir)
        synchronizer = Synchronizer(state_manager)

        result = synchronizer.sync(source, [dest])

        # Verify file was updated
        assert len(result.copied) == 1
        assert len(result.skipped) == 0
        assert len(result.failed) == 0
        assert (dest / "file.txt").read_text() == "New content"

    def test_sync_to_multiple_destinations(self, tmp_path: Path) -> None:
        """Test syncing to multiple destinations."""
        source = tmp_path / "source"
        dest1 = tmp_path / "dest1"
        dest2 = tmp_path / "dest2"

        source.mkdir()
        (source / "file.txt").write_text("Multi-dest file")

        # Sync to both destinations
        state_dir = tmp_path / "state"
        state_manager = StateManager(state_dir)
        synchronizer = Synchronizer(state_manager)

        result = synchronizer.sync(source, [dest1, dest2])

        # Verify both destinations received the file
        assert len(result.copied) == 2
        assert (dest1 / "file.txt").read_text() == "Multi-dest file"
        assert (dest2 / "file.txt").read_text() == "Multi-dest file"

    def test_sync_dry_run_does_not_copy(self, tmp_path: Path) -> None:
        """Test that dry run doesn't actually copy files."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"

        source.mkdir()
        (source / "file.txt").write_text("Dry run test")

        # Sync with dry run
        state_dir = tmp_path / "state"
        state_manager = StateManager(state_dir)
        synchronizer = Synchronizer(state_manager)

        result = synchronizer.sync(source, [dest], dry_run=True)

        # Verify file was marked as copied but doesn't exist
        assert len(result.copied) == 1
        assert not (dest / "file.txt").exists()

    def test_sync_dry_run_does_not_create_dest_directory(self, tmp_path: Path) -> None:
        """Test that dry run doesn't create destination directory."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"

        source.mkdir()
        (source / "file.txt").write_text("Dry run test")

        # Sync with dry run
        state_dir = tmp_path / "state"
        state_manager = StateManager(state_dir)
        synchronizer = Synchronizer(state_manager)

        synchronizer.sync(source, [dest], dry_run=True)

        assert not dest.exists()

    def test_sync_creates_nested_directories(self, tmp_path: Path) -> None:
        """Test that sync creates nested directory structure."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"

        source.mkdir()
        (source / "level1").mkdir()
        (source / "level1" / "level2").mkdir()
        (source / "level1" / "level2" / "file.txt").write_text("Deep nested")

        # Sync
        state_dir = tmp_path / "state"
        state_manager = StateManager(state_dir)
        synchronizer = Synchronizer(state_manager)

        result = synchronizer.sync(source, [dest])

        # Verify nested structure was created
        assert len(result.copied) == 1
        assert (dest / "level1" / "level2" / "file.txt").exists()
        assert (dest / "level1" / "level2" / "file.txt").read_text() == "Deep nested"

    def test_sync_with_binary_files(self, tmp_path: Path) -> None:
        """Test syncing binary files."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"

        source.mkdir()
        binary_content = bytes(range(256))  # All possible byte values
        (source / "binary.dat").write_bytes(binary_content)

        # Sync
        state_dir = tmp_path / "state"
        state_manager = StateManager(state_dir)
        synchronizer = Synchronizer(state_manager)

        result = synchronizer.sync(source, [dest])

        # Verify binary file was copied correctly
        assert len(result.copied) == 1
        assert (dest / "binary.dat").read_bytes() == binary_content

    def test_sync_idempotent(self, tmp_path: Path) -> None:
        """Test that running sync multiple times is idempotent."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"

        source.mkdir()
        (source / "file.txt").write_text("Test content")

        # Sync twice
        state_dir = tmp_path / "state"
        state_manager = StateManager(state_dir)
        synchronizer = Synchronizer(state_manager)

        result1 = synchronizer.sync(source, [dest])
        result2 = synchronizer.sync(source, [dest])

        # First run copies, second run skips
        assert len(result1.copied) == 1
        assert len(result1.skipped) == 0
        assert len(result2.copied) == 0
        assert len(result2.skipped) == 1

    def test_sync_source_does_not_exist(self, tmp_path: Path) -> None:
        """Test that sync raises error when source doesn't exist."""
        source = tmp_path / "nonexistent"
        dest = tmp_path / "dest"

        state_dir = tmp_path / "state"
        state_manager = StateManager(state_dir)
        synchronizer = Synchronizer(state_manager)

        with pytest.raises(ValueError, match="Source directory does not exist"):
            synchronizer.sync(source, [dest])

    def test_sync_with_empty_source(self, tmp_path: Path) -> None:
        """Test syncing from an empty source directory."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"

        source.mkdir()

        state_dir = tmp_path / "state"
        state_manager = StateManager(state_dir)
        synchronizer = Synchronizer(state_manager)

        result = synchronizer.sync(source, [dest])

        # No files to copy
        assert len(result.copied) == 0
        assert len(result.skipped) == 0
        assert len(result.failed) == 0


class TestStateManagement:
    """Integration tests for state management."""

    def test_add_and_retrieve_failed_files(self, tmp_path: Path) -> None:
        """Test adding and retrieving failed files from state."""
        state_dir = tmp_path / "state"
        state_manager = StateManager(state_dir)

        # Add failed files
        state_manager.add_failed_file("file1.txt", "/dest", "Permission denied")
        state_manager.add_failed_file("file2.txt", "/dest", "Disk full")

        # Retrieve
        failed = state_manager.get_failed_files()

        assert len(failed) == 2
        assert failed[0]["file"] == "file1.txt"
        assert failed[0]["dest"] == "/dest"
        assert failed[0]["error"] == "Permission denied"
        assert "timestamp" in failed[0]

    def test_clear_failed_files(self, tmp_path: Path) -> None:
        """Test clearing failed files from state."""
        state_dir = tmp_path / "state"
        state_manager = StateManager(state_dir)

        # Add failed files
        state_manager.add_failed_file("file.txt", "/dest", "Error")

        # Clear
        state_manager.clear_failed_files()

        # Verify cleared
        failed = state_manager.get_failed_files()
        assert len(failed) == 0

    def test_state_persists_across_instances(self, tmp_path: Path) -> None:
        """Test that state persists across StateManager instances."""
        state_dir = tmp_path / "state"

        # First instance
        sm1 = StateManager(state_dir)
        sm1.add_failed_file("file.txt", "/dest", "Error")

        # Second instance
        sm2 = StateManager(state_dir)
        failed = sm2.get_failed_files()

        assert len(failed) == 1
        assert failed[0]["file"] == "file.txt"

    def test_empty_state_initialization(self, tmp_path: Path) -> None:
        """Test that new state manager starts with empty failed files."""
        state_dir = tmp_path / "state"
        state_manager = StateManager(state_dir)

        failed = state_manager.get_failed_files()
        assert failed == []


class TestConfig:
    """Integration tests for configuration."""

    def test_config_to_dict_and_back(self, tmp_path: Path) -> None:
        """Test converting config to dict and creating from dict."""
        config = Config(
            source=Path("/source"),
            destinations=[Path("/dest1"), Path("/dest2")],
            dry_run=True,
            verbose=True,
        )

        config_dict = config.to_dict()

        assert config_dict["source"] == "/source"
        assert config_dict["destinations"] == ["/dest1", "/dest2"]
        assert config_dict["dry_run"] is True
        assert config_dict["verbose"] is True

    def test_config_save_and_load(self, tmp_path: Path) -> None:
        """Test saving config to file and loading it back."""
        config_path = tmp_path / "config.json"

        # Save config
        original = Config(
            source=Path("/source"),
            destinations=[Path("/dest1"), Path("/dest2")],
            dry_run=True,
            verbose=False,
        )
        original.save(config_path)

        # Load config
        loaded = Config.from_file(config_path)

        assert str(loaded.source) == "/source"
        assert [str(d) for d in loaded.destinations] == ["/dest1", "/dest2"]
        assert loaded.dry_run is True
        assert loaded.verbose is False

    def test_config_defaults(self) -> None:
        """Test that config has sensible defaults."""
        config = Config()

        assert config.source is None
        assert config.destinations == []
        assert config.dry_run is False
        assert config.verbose is False

    def test_config_from_file_creates_directories(self, tmp_path: Path) -> None:
        """Test that config save creates parent directories."""
        config_path = tmp_path / "nested" / "dir" / "config.json"

        config = Config(source=Path("/source"), destinations=[Path("/dest")])
        config.save(config_path)

        assert config_path.exists()
        assert config_path.parent.is_dir()


class TestEndToEndWorkflows:
    """End-to-end integration tests for complete workflows."""

    def test_full_sync_workflow_with_changes(self, tmp_path: Path) -> None:
        """Test complete workflow: initial sync, modify, re-sync."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"
        state_dir = tmp_path / "state"

        # Initial setup
        source.mkdir()
        (source / "file1.txt").write_text("Initial content")

        # Initial sync
        state_manager = StateManager(state_dir)
        synchronizer = Synchronizer(state_manager)
        result1 = synchronizer.sync(source, [dest])

        assert len(result1.copied) == 1
        assert (dest / "file1.txt").read_text() == "Initial content"

        # Modify source file
        (source / "file1.txt").write_text("Updated content")

        # Re-sync
        result2 = synchronizer.sync(source, [dest])

        assert len(result2.copied) == 1
        assert (dest / "file1.txt").read_text() == "Updated content"

    def test_partial_sync_with_multiple_files(self, tmp_path: Path) -> None:
        """Test syncing when some files exist and some don't."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"
        state_dir = tmp_path / "state"

        source.mkdir()
        dest.mkdir()

        # Create source files
        (source / "new_file.txt").write_text("New")
        (source / "existing_file.txt").write_text("Existing")

        # Create one existing file with same content
        (dest / "existing_file.txt").write_text("Existing")

        # Sync
        state_manager = StateManager(state_dir)
        synchronizer = Synchronizer(state_manager)
        result = synchronizer.sync(source, [dest])

        # One copied, one skipped
        assert len(result.copied) == 1
        assert len(result.skipped) == 1
        assert result.copied[0][0] == Path("new_file.txt")
        assert result.skipped[0][0] == Path("existing_file.txt")

    def test_config_based_sync_workflow(self, tmp_path: Path) -> None:
        """Test workflow using config file."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"
        config_path = tmp_path / "config.json"
        state_dir = tmp_path / "state"

        # Setup source
        source.mkdir()
        (source / "file.txt").write_text("Config-based sync")

        # Create and save config
        config = Config(
            source=source,
            destinations=[dest],
            dry_run=False,
        )
        config.save(config_path)

        # Load config and sync
        loaded_config = Config.from_file(config_path)
        state_manager = StateManager(state_dir)
        synchronizer = Synchronizer(state_manager)

        assert loaded_config.source is not None
        result = synchronizer.sync(
            loaded_config.source,
            loaded_config.destinations,
            loaded_config.dry_run,
        )

        assert len(result.copied) == 1
        assert (dest / "file.txt").read_text() == "Config-based sync"

    def test_large_directory_structure(self, tmp_path: Path) -> None:
        """Test syncing a larger directory structure."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"
        state_dir = tmp_path / "state"

        # Create complex structure
        source.mkdir()
        for i in range(5):
            subdir = source / f"dir{i}"
            subdir.mkdir()
            for j in range(3):
                file_path = subdir / f"file{j}.txt"
                file_path.write_text(f"Content {i}-{j}")

        # Add some files at root
        (source / "root1.txt").write_text("Root file 1")
        (source / "root2.txt").write_text("Root file 2")

        # Sync
        state_manager = StateManager(state_dir)
        synchronizer = Synchronizer(state_manager)
        result = synchronizer.sync(source, [dest])

        # Should copy all 17 files (5*3 + 2)
        assert len(result.copied) == 17

        # Verify structure
        for i in range(5):
            for j in range(3):
                file_path = dest / f"dir{i}" / f"file{j}.txt"
                assert file_path.exists()
                assert file_path.read_text() == f"Content {i}-{j}"

        assert (dest / "root1.txt").read_text() == "Root file 1"
        assert (dest / "root2.txt").read_text() == "Root file 2"

    def test_workflow_with_failed_files(self, tmp_path: Path) -> None:
        """Test workflow when some files fail to sync."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"
        state_dir = tmp_path / "state"

        source.mkdir()

        # Create a file
        (source / "file.txt").write_text("Test")

        # Make destination read-only to simulate failure
        dest.mkdir()
        dest_file = dest / "file.txt"
        dest_file.write_text("Existing")
        dest_file.chmod(0o444)  # Read-only

        # Try to sync (will fail)
        state_manager = StateManager(state_dir)
        synchronizer = Synchronizer(state_manager)

        result = synchronizer.sync(source, [dest])

        # Should have failed entry
        assert len(result.failed) > 0

        # Check failed files in state
        failed = state_manager.get_failed_files()
        assert len(failed) > 0
        assert failed[0]["file"] == "file.txt"
        assert failed[0]["dest"] == str(dest)

        # Clean up: restore permissions
        dest_file.chmod(0o644)
