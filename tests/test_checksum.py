"""Tests for checksum module."""

import hashlib
from pathlib import Path

from dubler.checksum import calculate_sha256


def test_calculate_sha256(tmp_path: Path) -> None:
    """Test SHA256 checksum calculation."""
    # Create a test file
    test_file = tmp_path / "test.txt"
    content = b"Hello, World!"
    test_file.write_bytes(content)

    # Calculate expected checksum
    expected = hashlib.sha256(content).hexdigest()

    # Test
    result = calculate_sha256(test_file)
    assert result == expected


def test_calculate_sha256_different_files(tmp_path: Path) -> None:
    """Test that different files have different checksums."""
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"

    file1.write_bytes(b"content1")
    file2.write_bytes(b"content2")

    checksum1 = calculate_sha256(file1)
    checksum2 = calculate_sha256(file2)

    assert checksum1 != checksum2


def test_calculate_sha256_same_content(tmp_path: Path) -> None:
    """Test that files with same content have same checksum."""
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"

    content = b"same content"
    file1.write_bytes(content)
    file2.write_bytes(content)

    checksum1 = calculate_sha256(file1)
    checksum2 = calculate_sha256(file2)

    assert checksum1 == checksum2
