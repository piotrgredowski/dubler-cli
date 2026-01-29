"""CLI interface for dubler."""

import argparse
import logging
from pathlib import Path

from . import __version__
from .config import Config
from .state import StateManager
from .sync import Synchronizer

logger = logging.getLogger(__name__)


def get_config_dir() -> Path:
    """Get configuration directory.

    Returns:
        Path to ~/.config/dubler
    """
    return Path.home() / ".config" / "dubler"


def get_state_dir() -> Path:
    """Get state directory.

    Returns:
        Path to ~/.local/state/dubler
    """
    return Path.home() / ".local" / "state" / "dubler"


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        prog="dubler",
        description="Synchronize files from source to multiple destinations using checksums.",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=__version__,
    )

    parser.add_argument(
        "-s",
        "--source",
        type=Path,
        help="Source directory",
    )
    parser.add_argument(
        "-d",
        "--dest",
        type=Path,
        action="append",
        help="Destination directory (can be specified multiple times)",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        help=f"Path to JSON config file (default: {get_config_dir() / 'config.json'})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without copying files",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--failed",
        action="store_true",
        help="Show previously failed files",
    )
    parser.add_argument(
        "--clear-failed",
        action="store_true",
        help="Clear failed files from state",
    )

    return parser.parse_args()


def load_config(args: argparse.Namespace) -> Config:
    """Load configuration from file and CLI arguments.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Merged configuration.
    """
    config = Config()

    # Load from config file if specified or default exists
    config_path = args.config or (get_config_dir() / "config.json")
    if config_path.exists():
        config = Config.from_file(config_path)

    # Override with CLI arguments
    if args.source:
        config.source = args.source
    if args.dest:
        config.destinations = args.dest
    if args.dry_run:
        config.dry_run = True
    if args.verbose:
        config.verbose = True

    return config


def show_failed_files(state_manager: StateManager) -> None:
    """Show failed files from state.

    Args:
        state_manager: State manager instance.
    """
    failed = state_manager.get_failed_files()

    if not failed:
        logger.info("No failed files recorded.")
        return

    logger.info(f"Failed files ({len(failed)}):")
    for entry in failed:
        logger.info(f"  - {entry['file']} -> {entry['dest']}")
        logger.info(f"    Error: {entry['error']}")
        logger.info(f"    Time: {entry['timestamp']}")


def main() -> None:
    """Main entry point."""
    args = parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        handlers=[logging.StreamHandler()],
    )

    config_dir = get_config_dir()
    state_dir = get_state_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    state_dir.mkdir(parents=True, exist_ok=True)

    state_manager = StateManager(state_dir)

    # Handle --failed flag
    if args.failed:
        show_failed_files(state_manager)
        return

    # Handle --clear-failed flag
    if args.clear_failed:
        state_manager.clear_failed_files()
        logger.info("Cleared failed files from state.")
        return

    # Load configuration
    config = load_config(args)

    if not config.source:
        logger.error("Source directory not specified (use --source or config file)")
        return

    if not config.destinations:
        logger.error("No destination directories specified (use --dest or config file)")
        return

    # Run synchronization
    logger.info(f"Source: {config.source}")
    logger.info(f"Destinations: {[str(d) for d in config.destinations]}")
    if config.dry_run:
        logger.info("DRY RUN mode - no files will be copied")

    synchronizer = Synchronizer(state_manager, verbose=config.verbose)

    try:
        result = synchronizer.sync(
            source=config.source,
            destinations=config.destinations,
            dry_run=config.dry_run,
        )

        # Print summary
        logger.info("")
        logger.info("Summary:")
        logger.info(f"  Copied: {len(result.copied)}")
        logger.info(f"  Skipped: {len(result.skipped)}")
        logger.info(f"  Failed: {len(result.failed)}")

        if result.failed:
            logger.warning(
                f"\n{len(result.failed)} file(s) failed to copy. Run with --failed to see details."
            )

    except Exception as e:
        logger.error(f"{e}")


if __name__ == "__main__":
    main()
