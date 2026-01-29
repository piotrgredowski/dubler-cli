# Dubler

Directory synchronization tool.

> **Note:** The name "dubler" comes from Polish, where it means "a person replacing an actor in film or theater" (stunt double / stand-in). Just as a dubler stands in for an actor, this tool creates backup copies that can stand in for your original files — if something happens to the original, the backup is ready to take its place.

## Features

- **Checksum-based comparison**: Files are compared using SHA256 hashes
- **Multiple destinations**: Sync to multiple directories at once
- **Idempotent**: Running multiple times is safe - only copies missing or changed files
- **Failure tracking**: Tracks failed files and allows re-running
- **Dry run mode**: Preview changes before copying
- **JSON configuration**: Store sync settings in a config file
- **Zero dependencies**: Uses Python standard library only

## Installation

```bash
uv install
```

## Usage

### Command Line

```bash
# Basic sync
dubler --source /path/to/source --dest /path/to/dest1 --dest /path/to/dest2

# Dry run (preview without copying)
dubler -s /path/to/source -d /path/to/dest --dry-run

# Verbose output
dubler -s /path/to/source -d /path/to/dest -v

# Show failed files from previous runs
dubler --failed

# Clear failed files from state
dubler --clear-failed
```

### Configuration File

Create a JSON config file (default: `~/.config/dubler/config.json`):

```json
{
  "source": "/path/to/source",
  "destinations": [
    "/path/to/dest1",
    "/path/to/dest2"
  ],
  "dry_run": false,
  "verbose": false
}
```

Then run without arguments:

```bash
dubler
```

Or specify a custom config file:

```bash
dubler --config /path/to/config.json
```

## How It Works

1. Scans the source directory recursively
2. For each destination:
   - Compares files using SHA256 checksums
   - Copies files that don't exist or have different checksums
   - Tracks any failures in `~/.local/state/dubler/state.json`
3. Displays summary of copied, skipped, and failed files

## State

The application stores data in standard XDG Base Directory locations:

- `~/.config/dubler/config.json`: Configuration file (optional)
- `~/.local/state/dubler/state.json`: Failed files from previous runs

## Examples

```bash
# Sync photos to multiple backup drives
dubler -s ~/Pictures -d /Volumes/Backup1/Photos -d /Volumes/Backup2/Photos

# Preview what would be synced
dubler -s ~/Documents -d ~/Backup/Documents --dry-run -v

# After a failed run, see what failed
dubler --failed

# Fix the issue and run again (idempotent)
dubler -s ~/Documents -d ~/Backup/Documents
```

## Releasing

To create a new release:

```bash
# Tag the release (semantic versioning)
git tag v1.0.0

# Push the tag to trigger the release workflow
git push origin v1.0.0
```

This will automatically create a draft release on GitHub with auto-generated release notes. Review and publish the release when ready.

## Conventional Commits

This project uses conventional commit messages. See [AGENTS.md](AGENTS.md) for guidelines.
