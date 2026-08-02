"""Build and audit the public ASW 0.2.0 source archive.

The public archive contains the core and documentation packages only. The
evaluation extension is a separate reproducibility input because its raw run
records and generated report require an independent path/secret audit.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import zipfile
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parent.parent
PUBLIC_ROOTS = ("asw-spec-codex", "asw-documentation-release-codex")
EXCLUDED_DIRECTORY_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "venv",
}
EXCLUDED_FILE_NAMES = {"@AutomationLog.txt"}
EXCLUDED_SUFFIXES = {".log", ".pyc"}
TEXT_SUFFIXES = {
    ".cfg",
    ".csv",
    ".ini",
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".rst",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

BACKSLASH = chr(92)
ESCAPED_BACKSLASH = re.escape(BACKSLASH)
USER_SEGMENT = "Users"
HOME_SEGMENT = "home"
MACHINE_PATH = re.compile(
    rf"(?i)(?:[A-Z]:{ESCAPED_BACKSLASH}{USER_SEGMENT}{ESCAPED_BACKSLASH}|[A-Z]:/{USER_SEGMENT}/|/{USER_SEGMENT}/|/{HOME_SEGMENT}/)"
)
CREDENTIAL = re.compile(
    r"(?i)\b(?:bearer\s+[A-Za-z0-9._-]{20,}|(?:token|secret|password)\s*[:=]\s*[A-Za-z0-9+/=_-]{20,})"
)


def iter_source_files(output: Path):
    output = output.resolve()
    for root_name in PUBLIC_ROOTS:
        root = WORKSPACE / root_name
        if not root.is_dir():
            raise SystemExit(f"missing public source root: {root}")
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.resolve() == output:
                continue
            if any(parent.name in EXCLUDED_DIRECTORY_NAMES for parent in path.parents):
                continue
            if path.name in EXCLUDED_FILE_NAMES or path.suffix.lower() in EXCLUDED_SUFFIXES:
                continue
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
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    files = list(iter_source_files(output))
    findings: list[str] = []
    members: list[tuple[Path, str]] = []
    for path in files:
        member = path.relative_to(WORKSPACE).as_posix()
        content = text_for_audit(path)
        if content is not None:
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

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(f"OK: public source archive audited ({len(members)} files)")
    print(f"archive={output}")
    print(f"sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
