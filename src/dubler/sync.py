"""Core synchronization logic."""

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from .checksum import calculate_sha256
from .state import StateManager

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Result of synchronization operation."""

    copied: list[tuple[Path, str]]  # (file, destination)
    skipped: list[tuple[Path, str]]  # (file, destination)
    failed: list[tuple[Path, str, str]]  # (file, destination, error)


class Synchronizer:
    """Handles directory synchronization."""

    def __init__(self, state_manager: StateManager, verbose: bool = False):
        """Initialize synchronizer.

        Args:
            state_manager: State manager instance.
            verbose: Enable verbose output.
        """
        self.state_manager = state_manager
        self.verbose = verbose

    def sync(
        self,
        source: Path,
        destinations: list[Path],
        dry_run: bool = False,
    ) -> SyncResult:
        """Synchronize source to multiple destinations.

        Args:
            source: Source directory.
            destinations: List of destination directories.
            dry_run: Preview without copying.

        Returns:
            SyncResult with statistics.
        """
        result = SyncResult(copied=[], skipped=[], failed=[])

        if not source.exists():
            raise ValueError(f"Source directory does not exist: {source}")

        # Get all files in source (relative paths)
        source_files = self._get_files(source)

        for dest in destinations:
            dest = dest.expanduser().resolve()
            if not dry_run:
                dest.mkdir(parents=True, exist_ok=True)

            for rel_path in source_files:
                src_file = source / rel_path
                dest_file = dest / rel_path

                try:
                    if self._should_copy(src_file, dest_file):
                        if not dry_run:
                            dest_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(src_file, dest_file)

                            # Verify copy was successful
                            if not dest_file.exists():
                                raise IOError("Copy failed - file not created")

                        result.copied.append((rel_path, str(dest)))
                        logger.debug(
                            f"  {'[DRY RUN] ' if dry_run else ''}COPIED: {rel_path} -> {dest}"
                        )
                    else:
                        result.skipped.append((rel_path, str(dest)))
                        logger.debug(f"  SKIPPED: {rel_path} (already exists)")

                except Exception as e:
                    error_msg = str(e)
                    result.failed.append((rel_path, str(dest), error_msg))
                    self.state_manager.add_failed_file(
                        str(rel_path), str(dest), error_msg
                    )
                    logger.error(f"  FAILED: {rel_path} -> {dest}: {error_msg}")

        return result

    def _get_files(self, directory: Path) -> list[Path]:
        """Get all files in directory recursively.

        Args:
            directory: Directory to scan.

        Returns:
            List of relative file paths.
        """
        files = []
        for item in directory.rglob("*"):
            if item.is_file():
                files.append(item.relative_to(directory))
        return files

    def _should_copy(self, src_file: Path, dest_file: Path) -> bool:
        """Check if file should be copied.

        Args:
            src_file: Source file path.
            dest_file: Destination file path.

        Returns:
            True if file should be copied, False otherwise.
        """
        if not dest_file.exists():
            return True

        # Compare checksums
        src_checksum = calculate_sha256(src_file)
        dest_checksum = calculate_sha256(dest_file)

        return src_checksum != dest_checksum
