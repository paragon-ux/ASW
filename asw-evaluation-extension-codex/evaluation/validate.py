"""Command-line validation for fixtures and persisted run evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .metrics import select_best_baselines
from .profile import digest
from .schema import (
    ROOT,
    ValidationError,
    iter_jsonl,
    read_and_validate,
    validate_fixture_tree,
    validate_summary_semantics,
    validate_trial_semantics,
)


def validate_run(run_dir: Path) -> None:
    profile = read_and_validate(run_dir / "profile.json", "evaluation-profile")
    manifest = read_and_validate(run_dir / "run-manifest.json", "run-manifest")
    if manifest["profile_digest"] != digest(profile):
        raise ValidationError("run manifest profile digest does not match frozen profile")
    raw_records = list(iter_jsonl(run_dir / "raw-results.jsonl"))
    for record in raw_records:
        validate_trial_semantics(record)
    summary = read_and_validate(run_dir / "aggregate-summary.json", "summary")
    validate_summary_semantics(summary)
    if summary["run_id"] != profile["run_id"] or manifest["run_id"] != profile["run_id"]:
        raise ValidationError("run/profile/summary IDs do not agree")
    if summary["base_commit"] != profile["base_commit"] or manifest["base_commit"] != profile["base_commit"]:
        raise ValidationError("run/profile/summary base commits do not agree")
    if summary["classification"] == "SUPPORTED" and not summary["threshold_audit"].get("pass", False):
        raise ValidationError("SUPPORTED summary lacks a passing threshold audit")
    ground_truth = list(iter_jsonl(run_dir / "ground-truth.jsonl"))
    if len({record["trial_id"] for record in ground_truth}) != len(ground_truth):
        raise ValidationError("ground-truth trial IDs are not unique")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, help="validate one persisted run directory")
    args = parser.parse_args()
    try:
        valid, invalid = validate_fixture_tree()
        if args.run:
            validate_run(args.run)
            print(f"validated run: {args.run}")
        print(f"validated fixtures: {len(valid)} valid, {len(invalid)} invalid")
    except ValidationError as exc:
        print(f"FAILED: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

