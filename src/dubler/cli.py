"""CLI interface for dubler."""

import argparse
from pathlib import Path

from .config import Config
from .state import StateManager
from .sync import Synchronizer


def get_app_dir() -> Path:
    """Get application directory in home.

    Returns:
        Path to ~/.dubler
    """
    return Path.home() / ".dubler"


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
        help=f"Path to JSON config file (default: {get_app_dir() / 'config.json'})",
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
    config_path = args.config or (get_app_dir() / "config.json")
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
        print("No failed files recorded.")
        return

    print(f"\nFailed files ({len(failed)}):")
    for entry in failed:
        print(f"  - {entry['file']} -> {entry['dest']}")
        print(f"    Error: {entry['error']}")
        print(f"    Time: {entry['timestamp']}")


def main() -> None:
    """Main entry point."""
    args = parse_args()
    app_dir = get_app_dir()
    app_dir.mkdir(parents=True, exist_ok=True)

    state_manager = StateManager(app_dir)

    # Handle --failed flag
    if args.failed:
        show_failed_files(state_manager)
        return

    # Handle --clear-failed flag
    if args.clear_failed:
        state_manager.clear_failed_files()
        print("Cleared failed files from state.")
        return

    # Load configuration
    config = load_config(args)

    if not config.source:
        print("Error: Source directory not specified (use --source or config file)")
        return

    if not config.destinations:
        print("Error: No destination directories specified (use --dest or config file)")
        return

    # Run synchronization
    print(f"Source: {config.source}")
    print(f"Destinations: {[str(d) for d in config.destinations]}")
    if config.dry_run:
        print("DRY RUN mode - no files will be copied")
    print()

    synchronizer = Synchronizer(state_manager, verbose=config.verbose)

    try:
        result = synchronizer.sync(
            source=config.source,
            destinations=config.destinations,
            dry_run=config.dry_run,
        )

        # Print summary
        print("\nSummary:")
        print(f"  Copied: {len(result.copied)}")
        print(f"  Skipped: {len(result.skipped)}")
        print(f"  Failed: {len(result.failed)}")

        if result.failed:
            print(
                f"\n{len(result.failed)} file(s) failed to copy. Run with --failed to see details."
            )

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
