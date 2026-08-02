"""Validate and recompute the accepted Phase 8 run without overwriting it."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent
RUN_ID = "asw-mvp-eval-20260802-05"
BASE_COMMIT = "7d6e267c6e89cdcd8a71644c67c95d2ab4260330"
EXPECTED_COUNTS = {"raw-results.jsonl": 736, "ground-truth.jsonl": 158, "agent-usage.jsonl": 36}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def jsonl_count(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def headline(summary: dict) -> dict:
    audit = summary["threshold_audit"]
    efficiency = audit["layer_a_efficiency"]
    continuation = audit["layer_b_continuation"]
    return {
        "classification": summary["classification"],
        "detection": audit["correctness"]["asw_detection_success"],
        "duplicate_rate": audit["correctness"]["asw_duplicate_rate"],
        "false_positive_rate": audit["correctness"]["asw_false_positive_rate"],
        "attribution_accuracy": audit["correctness"]["asw_attribution_accuracy"],
        "kind_accuracy": audit["correctness"]["asw_kind_accuracy"],
        "layer_a_classes": efficiency["classes_passing"],
        "layer_a_reductions": sorted(item["observation_reduction"] for item in efficiency["by_class"].values()),
        "layer_b_success": continuation["asw_success"],
        "layer_b_call_improvement": continuation["observation_call_improvement"],
        "layer_b_latency_improvement": continuation["latency_improvement"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evaluation-root",
        type=Path,
        default=WORKSPACE / "asw-evaluation-extension-codex",
        help="evaluation package root containing evaluation/ and fixtures/",
    )
    parser.add_argument("--run-id", default=RUN_ID)
    args = parser.parse_args()

    evaluation_root = args.evaluation_root.resolve()
    run_dir = evaluation_root / "evaluation" / "results" / args.run_id
    if args.run_id != RUN_ID:
        raise SystemExit(f"refusing non-accepted run: {args.run_id}")
    if not run_dir.is_dir():
        raise SystemExit(f"missing accepted run directory: {run_dir}")

    sys.path.insert(0, str(evaluation_root))
    from evaluation.profile import digest

    profile_path = run_dir / "profile.json"
    manifest_path = run_dir / "run-manifest.json"
    original_aggregate_path = run_dir / "aggregate-summary.json"
    public_aggregate_path = ROOT / "evidence" / "aggregate-summary.json"
    profile = read_json(profile_path)
    manifest = read_json(manifest_path)
    original_aggregate = read_json(original_aggregate_path)
    original_aggregate_hash = sha256(original_aggregate_path)

    subprocess.run(
        [sys.executable, "-m", "evaluation.validate", "--run", str(run_dir)],
        cwd=evaluation_root,
        check=True,
    )

    if profile["run_id"] != RUN_ID or manifest["run_id"] != RUN_ID or original_aggregate["run_id"] != RUN_ID:
        raise SystemExit("run ID mismatch")
    if profile["base_commit"] != BASE_COMMIT or manifest["base_commit"] != BASE_COMMIT or original_aggregate["base_commit"] != BASE_COMMIT:
        raise SystemExit("base commit mismatch")
    if digest(profile) != manifest["profile_digest"]:
        raise SystemExit("profile digest mismatch")
    for filename, expected in EXPECTED_COUNTS.items():
        actual = jsonl_count(run_dir / filename)
        if actual != expected:
            raise SystemExit(f"{filename} count mismatch: expected {expected}, actual {actual}")

    with tempfile.TemporaryDirectory(prefix="asw-frozen-evidence-") as temp_dir:
        isolated_root = Path(temp_dir) / evaluation_root.name
        isolated_run = isolated_root / "evaluation" / "results" / RUN_ID
        isolated_run.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(run_dir, isolated_run)
        shutil.copytree(evaluation_root / "fixtures" / "scenarios", isolated_root / "fixtures" / "scenarios")
        subprocess.run(
            [sys.executable, "-m", "evaluation.aggregate", str(isolated_run)],
            cwd=evaluation_root,
            check=True,
        )
        recomputed_path = isolated_run / "aggregate-summary.json"
        recomputed = read_json(recomputed_path)
        recomputed_hash = sha256(recomputed_path)

    if recomputed_hash != original_aggregate_hash:
        raise SystemExit(
            "recomputed aggregate mismatch: "
            f"expected {original_aggregate_hash}, actual {recomputed_hash}"
        )
    if public_aggregate_path.is_file() and sha256(public_aggregate_path) != original_aggregate_hash:
        raise SystemExit("public aggregate does not match the accepted aggregate")
    if headline(recomputed) != headline(original_aggregate):
        raise SystemExit("recomputed headline metrics differ from the accepted aggregate")
    if sha256(original_aggregate_path) != original_aggregate_hash:
        raise SystemExit("accepted aggregate changed during verification")

    print("OK: accepted Phase 8 frozen-evidence integrity gate passed")
    print(f"run_id={RUN_ID}")
    print(f"base_commit={BASE_COMMIT}")
    print(f"profile_digest={manifest['profile_digest']}")
    print(f"aggregate_sha256={original_aggregate_hash}")
    print("counts=raw-results.jsonl:736,ground-truth.jsonl:158,agent-usage.jsonl:36")
    print(f"headline={json.dumps(headline(recomputed), sort_keys=True)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
