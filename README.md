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

**No installation required!** You can run dubler directly with `uvx`:

```bash
uvx dubler --help
```

If you prefer to install:

```bash
# From PyPI
pip install dubler
# or with uv
uv pip install dubler

# From source
uv install
```

## Usage

### Command Line

```bash
# Basic sync
uvx dubler --source /path/to/source --dest /path/to/dest1 --dest /path/to/dest2

# Dry run (preview without copying)
uvx dubler -s /path/to/source -d /path/to/dest --dry-run

# Verbose output
uvx dubler -s /path/to/source -d /path/to/dest -v

# Show failed files from previous runs
uvx dubler --failed

# Clear failed files from state
uvx dubler --clear-failed
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
uvx dubler
```

Or specify a custom config file:

```bash
uvx dubler --config /path/to/config.json
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
uvx dubler -s ~/Pictures -d /Volumes/Backup1/Photos -d /Volumes/Backup2/Photos

# Preview what would be synced
uvx dubler -s ~/Documents -d ~/Backup/Documents --dry-run -v

# After a failed run, see what failed
uvx dubler --failed

# Fix the issue and run again (idempotent)
uvx dubler -s ~/Documents -d ~/Backup/Documents
```

## Releasing

The project uses automatic versioning based on git tags via `setuptools_scm`.

### Creating a Release

Use the release helper script:

```bash
# Bump patch version (bug fixes)
uv run python scripts/release.py patch

# Bump minor version (new features)
uv run python scripts/release.py minor

# Bump major version (breaking changes)
uv run python scripts/release.py major

# Or specify exact version
uv run python scripts/release.py patch --version 1.2.3
```

This will:
1. Create and push a git tag (e.g., `v1.0.0`)
2. Trigger the GitHub Actions release workflow
3. Automatically create a published release with:
   - Release notes from commits
   - Installation instructions
   - Full changelog link
4. Publish to PyPI

### Manual Release (Alternative)

```bash
# Create and push tag manually
git tag v1.0.0
git push origin v1.0.0
```

### Version Format

Tags must follow semantic versioning: `vX.Y.Z`
- `X` = Major version (breaking changes)
- `Y` = Minor version (new features, backwards compatible)
- `Z` = Patch version (bug fixes, backwards compatible)

## Conventional Commits

This project uses conventional commit messages. See [AGENTS.md](AGENTS.md) for guidelines.
