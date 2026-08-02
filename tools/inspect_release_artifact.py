"""Inspect a built ASW release archive for required and excluded paths."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


REQUIRED_PREFIXES = ("asw/", "tests/", "schemas/", "fixtures/", "evaluation/", "tools/", "scripts/", "docs/", ".github/")
REQUIRED_FILES = {
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CHANGELOG.md",
    "pyproject.toml",
    "requirements-windows-qualified.txt",
    "requirements-dev-qualified.txt",
}
FORBIDDEN_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "build-docs",
    "phase-reports",
    "release-artifacts",
    "venv",
}
FORBIDDEN_SUFFIXES = (".egg-info", ".log", ".pyc", ".pyo", ".tmp", ".zip")


def is_forbidden_member(name: str) -> bool:
    parts = [part.lower() for part in name.rstrip("/").split("/") if part]
    return (
        any(part in FORBIDDEN_PARTS for part in parts)
        or any(part.endswith("-codex") for part in parts)
        or any(part.endswith(FORBIDDEN_SUFFIXES) for part in parts)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    with zipfile.ZipFile(args.archive) as archive:
        names = set(archive.namelist())
    missing = sorted(REQUIRED_FILES - names)
    missing_prefixes = [prefix for prefix in REQUIRED_PREFIXES if not any(name.startswith(prefix) for name in names)]
    forbidden = sorted(name for name in names if is_forbidden_member(name))
    if missing or missing_prefixes or forbidden:
        if missing:
            print(f"missing files: {missing}")
        if missing_prefixes:
            print(f"missing directory content: {missing_prefixes}")
        if forbidden:
            print(f"forbidden members: {forbidden}")
        return 1
    print(f"OK: inspected {len(names)} archive members")
    for name in sorted(names):
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
