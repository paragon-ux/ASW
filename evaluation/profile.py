"""Frozen profile loading, hashing, and run-manifest helpers."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .schema import validate_profile_semantics


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPOSITORY_ROOT / "evaluation"
DEFAULT_PROFILE = EVALUATION_ROOT / "fixtures" / "valid" / "evaluation-profile.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(document: Any) -> bytes:
    return (json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def digest(document: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(document)).hexdigest()


def git_root(path: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    )
    return Path(result.stdout.strip())


def base_commit(path: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def core_worktree_status(repo: Path) -> dict[str, Any]:
    """Report the canonical repository worktree status without filtering paths."""

    result = subprocess.run(
        ["git", "-C", str(repo), "status", "--short"],
        check=True,
        capture_output=True,
        text=True,
    )
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return {
        "full_worktree_clean": not lines,
        "core_worktree_clean": not lines,
        "full_status": lines,
        "core_status": lines,
        "extension_status_excluded": [],
    }


def load_profile(path: Path = DEFAULT_PROFILE) -> dict[str, Any]:
    profile = json.loads(path.read_text(encoding="utf-8"))
    validate_profile_semantics(profile)
    return profile


def freeze_profile(
    source: Path,
    destination: Path,
    *,
    repo: Path,
    run_id: str | None = None,
    model: str = "Luna Max",
    frozen_at: str | None = None,
) -> dict[str, Any]:
    """Materialize a profile once, replacing only placeholder metadata.

    Existing destination files are treated as immutable.  A caller may rerun
    aggregation and reporting, but a comparative run cannot silently mutate
    its profile after results exist.
    """

    profile = load_profile(source)
    frozen = dict(profile)
    frozen["run_id"] = run_id or profile["run_id"]
    frozen["base_commit"] = base_commit(repo)
    frozen["frozen_at"] = frozen_at or utc_now()
    frozen["agent"] = dict(profile["agent"])
    frozen["agent"]["model"] = model
    validate_profile_semantics(frozen)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        existing = json.loads(destination.read_text(encoding="utf-8"))
        if existing != frozen:
            raise RuntimeError(f"frozen profile already exists and differs: {destination}")
        return existing
    destination.write_bytes(canonical_json(frozen))
    return frozen


def host_metadata(config_path: Path | None = None) -> dict[str, Any]:
    return {
        "os": platform.platform(),
        "python": platform.python_version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "config_toml": str(config_path) if config_path and config_path.exists() else None,
        "runtime": sys.implementation.name,
    }


def build_manifest(
    profile: dict[str, Any],
    *,
    repo: Path,
    profile_digest: str,
    started_at: str,
    raw_results_path: str,
    ground_truth_path: str,
    config_path: Path | None = None,
) -> dict[str, Any]:
    scenarios = {name: "v1" for name in profile["primary_scenarios"] + profile["secondary_scenarios"]}
    baselines = {name: "v1" for name in profile["baselines"]}
    return {
        "schema_version": "asw.evaluation_run_manifest.v1",
        "run_id": profile["run_id"],
        "base_commit": profile["base_commit"],
        "started_at": started_at,
        "completed_at": None,
        "host": host_metadata(config_path),
        "asw_version": None,
        "profile_digest": profile_digest,
        "scenario_versions": scenarios,
        "baseline_versions": baselines,
        "harness_version": __version__,
        "raw_results_path": raw_results_path,
        "ground_truth_path": ground_truth_path,
        "baseline_verification": core_worktree_status(repo),
    }


def write_json(path: Path, document: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json(document))
