"""Build and audit the public ASW v0.1.0 source archive."""

from __future__ import annotations

import argparse
import hashlib
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = (
    ".gitignore",
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "PACKAGE.json",
    "pyproject.toml",
    "requirements-windows-qualified.txt",
    "requirements-dev-qualified.txt",
    "THIRD_PARTY_NOTICES.md",
    "main.py",
    "validate_fixtures.py",
    "checklists/FINAL_RELEASE_CHECKLIST.md",
)
ROOT_DIRECTORIES = ("asw", "tests", "schemas", "fixtures", "evaluation", "tools", "docs")
EXCLUDED_DIRECTORY_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "release-artifacts",
    "venv",
}
EXCLUDED_FILE_NAMES = {"@AutomationLog.txt", "validate_package_source.py"}
EXCLUDED_RELATIVE_PATHS = {"docs/ASW-Repo-Release-v0-1-0.md"}
# These shipped process files contain the literal patterns used by the
# release audit itself, or placeholder examples describing the audit. They
# remain packaged, but are checked by the dedicated release validator rather
# than by this content scan.
AUDIT_EXCLUDED_RELATIVE_PATHS = {
    "checklists/FINAL_RELEASE_CHECKLIST.md",
    "tools/build_release_artifact.py",
    "tools/validate_release.py",
}
EXCLUDED_SUFFIXES = {".log", ".pyc", ".pyo"}
TEXT_SUFFIXES = {
    ".cfg", ".csv", ".ini", ".json", ".jsonl", ".md", ".py", ".rst", ".toml", ".txt", ".yaml", ".yml"
}

BACKSLASH = chr(92)
MACHINE_PATH = re.compile(
    rf"(?i)(?:[A-Z]:{re.escape(BACKSLASH)}Users{re.escape(BACKSLASH)}|[A-Z]:/Users/|/Users/|/home/)"
)
CREDENTIAL = re.compile(
    r"(?i)\b(?:bearer\s+[A-Za-z0-9._-]{20,}|(?:token|secret|password)\s*[:=]\s*[A-Za-z0-9+/=_-]{20,})"
)


def _excluded(path: Path) -> bool:
    relative = path.relative_to(ROOT).as_posix()
    return (
        relative in EXCLUDED_RELATIVE_PATHS
        or path.name in EXCLUDED_FILE_NAMES
        or path.suffix.lower() in EXCLUDED_SUFFIXES
        or any(parent.name in EXCLUDED_DIRECTORY_NAMES for parent in path.parents)
    )


def iter_source_files(output: Path):
    for relative in ROOT_FILES:
        path = ROOT / relative
        if not path.is_file():
            raise SystemExit(f"missing required release input: {relative}")
        if not _excluded(path):
            yield path
    for directory in ROOT_DIRECTORIES:
        root = ROOT / directory
        if not root.is_dir():
            raise SystemExit(f"missing required release directory: {directory}")
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.resolve() != output.resolve() and not _excluded(path):
                yield path


def text_for_audit(path: Path) -> str | None:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return None
    data = path.read_bytes()
    if b"\x00" in data[:4096]:
        return None
    return data.decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="destination .zip path")
    parser.add_argument("--manifest", type=Path, help="optional text manifest destination")
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(set(iter_source_files(output)))
    findings: list[str] = []
    members: list[tuple[Path, str]] = []
    for path in files:
        member = path.relative_to(ROOT).as_posix()
        content = text_for_audit(path)
        if content is not None and member not in AUDIT_EXCLUDED_RELATIVE_PATHS:
            if MACHINE_PATH.search(content):
                findings.append(f"machine-specific path: {member}")
            if CREDENTIAL.search(content):
                findings.append(f"credential-shaped text: {member}")
        members.append((path, member))
    if findings:
        raise SystemExit("release archive audit failed:\n" + "\n".join(findings))

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, member in members:
            archive.write(path, member)

    digest = hashlib.sha256(output.read_bytes()).hexdigest().upper()
    if args.manifest:
        manifest = args.manifest.resolve()
        manifest.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"artifact={output.name}", f"sha256={digest}", f"file_count={len(members)}", "", *[member for _, member in members]]
        manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK: public source archive audited ({len(members)} files)")
    print(f"archive={output}")
    print(f"sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
