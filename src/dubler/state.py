"""State management for tracking failed files."""

import json
from datetime import datetime
from pathlib import Path


class StateManager:
    """Manages application state for failed files."""

    def __init__(self, state_dir: Path):
        """Initialize state manager.

        Args:
            state_dir: Path to state directory (typically ~/.local/state/dubler).
        """
        self.state_dir = state_dir
        self.state_file = state_dir / "state.json"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def load_state(self) -> dict:
        """Load state from file.

        Returns:
            State dictionary with failed_files list.
        """
        if not self.state_file.exists():
            return {"failed_files": []}

        with open(self.state_file, "r") as f:
            return json.load(f)

    def save_state(self, state: dict) -> None:
        """Save state to file.

        Args:
            state: State dictionary to save.
        """
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def add_failed_file(self, file_path: str, dest: str, error: str) -> None:
        """Add a failed file to state.

        Args:
            file_path: Source file path.
            dest: Destination path.
            error: Error message.
        """
        state = self.load_state()
        state["failed_files"].append(
            {
                "file": file_path,
                "dest": dest,
                "error": error,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self.save_state(state)

    def clear_failed_files(self) -> None:
        """Clear all failed files from state."""
        state = self.load_state()
        state["failed_files"] = []
        self.save_state(state)

    def get_failed_files(self) -> list[dict]:
        """Get list of failed files.

        Returns:
            List of failed file entries.
        """
        state = self.load_state()
        return state["failed_files"]
