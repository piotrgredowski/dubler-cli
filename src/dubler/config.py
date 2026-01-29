"""Configuration file handling."""

import json
from pathlib import Path


class Config:
    """Configuration for dubler."""

    def __init__(
        self,
        source: Path | None = None,
        destinations: list[Path] | None = None,
        dry_run: bool = False,
        verbose: bool = False,
    ):
        """Initialize configuration.

        Args:
            source: Source directory path.
            destinations: List of destination directory paths.
            dry_run: Preview changes without copying.
            verbose: Enable verbose output.
        """
        self.source = source
        self.destinations = destinations or []
        self.dry_run = dry_run
        self.verbose = verbose

    @classmethod
    def from_file(cls, config_path: Path) -> "Config":
        """Load configuration from JSON file.

        Args:
            config_path: Path to config file.

        Returns:
            Config instance.
        """
        with open(config_path, "r") as f:
            data = json.load(f)

        return cls(
            source=Path(data["source"]) if data.get("source") else None,
            destinations=[Path(d) for d in data.get("destinations", [])],
            dry_run=data.get("dry_run", False),
            verbose=data.get("verbose", False),
        )

    def to_dict(self) -> dict:
        """Convert config to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "source": str(self.source) if self.source else None,
            "destinations": [str(d) for d in self.destinations],
            "dry_run": self.dry_run,
            "verbose": self.verbose,
        }

    def save(self, config_path: Path) -> None:
        """Save configuration to JSON file.

        Args:
            config_path: Path to save config.
        """
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
