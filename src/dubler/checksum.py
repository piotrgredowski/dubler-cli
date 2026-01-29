"""File checksum calculation."""

import hashlib
from pathlib import Path


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 checksum of a file.

    Args:
        file_path: Path to the file.

    Returns:
        Hexadecimal SHA256 checksum string.
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()
