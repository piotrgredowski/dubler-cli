#!/usr/bin/env python3
"""Release automation script."""

import subprocess
import sys


def get_current_version() -> str:
    try:
        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-c",
                "from setuptools_scm import get_version; print(get_version())",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "0.0.0"


def get_next_version(current: str, bump: str = "patch") -> str:
    # Handle dev versions (e.g., "0.1.0.dev5+g1234567")
    base_version = current.split(".dev")[0].split("+")[0]
    parts = base_version.split(".")[:3]
    major, minor, patch = [int(p) for p in parts]

    if bump == "major":
        return f"{major + 1}.0.0"
    elif bump == "minor":
        return f"{major}.{minor + 1}.0"
    else:
        return f"{major}.{minor}.{patch + 1}"


def create_tag(version: str) -> None:
    tag = f"v{version}"

    result = subprocess.run(["git", "tag", "-l", tag], capture_output=True, text=True)
    if result.stdout.strip():
        print(f"Error: Tag {tag} already exists!")
        sys.exit(1)

    subprocess.run(["git", "tag", "-a", tag, "-m", f"Release {version}"], check=True)
    print(f"Created tag: {tag}")

    subprocess.run(["git", "push", "origin", tag], check=True)
    print(f"Pushed tag: {tag}")
    print(
        "\nRelease workflow will create the release automatically and publish to PyPI."
    )
    print("See: https://github.com/YOUR_ORG/dubler/releases")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Create a new release")
    parser.add_argument(
        "bump", choices=["major", "minor", "patch"], help="Version bump type"
    )
    parser.add_argument("--version", help="Specific version (overrides bump)")

    args = parser.parse_args()

    if args.version:
        version = args.version
    else:
        current = get_current_version()
        version = get_next_version(current, args.bump)

    print(f"Creating release: {version}")
    confirm = input("Continue? [y/N] ")
    if confirm.lower() != "y":
        print("Aborted")
        sys.exit(0)

    create_tag(version)


if __name__ == "__main__":
    main()
