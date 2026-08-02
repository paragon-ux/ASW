"""Verify the accepted Phase 8 run from canonical public release evidence.

The accepted raw/profile/aggregate/ground-truth/agent-usage files are promoted
byte-for-byte into ``evaluation/results``. The historical source manifest is
not promoted because it contains workstation metadata; the public run
manifest is a schema-valid sanitized equivalent derived from the existing
sanitized provenance manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "asw-mvp-eval-20260802-05"
BASE_COMMIT = "7d6e267c6e89cdcd8a71644c67c95d2ab4260330"
EXPECTED_AGGREGATE = "80566B8C3BBC2DD7B4E729D243A1DE09E3BD68855E62C262A5C2232FBFDA527C"
EXPECTED_COUNTS = {"raw-results.jsonl": 736, "ground-truth.jsonl": 158, "agent-usage.jsonl": 36}
EXPECTED_EVIDENCE_SHA256 = {
    "agent-usage.jsonl": "558F3CD6FB43716FA8C6FFAAEEC7B52D2A2B2D95F178CDEEF449E937D7BA8A98",
    "aggregate-summary.json": EXPECTED_AGGREGATE,
    "ground-truth.jsonl": "950A0BD234FB30AE4B9CAF5563369A83DB9BB37C3488609F9D6E82AB78463B83",
    "profile.json": "9C38BD41057E1933CDA9C54C26FA143F775D7E6BBB5CD2848423CCD7CEBEB1C7",
    "raw-results.jsonl": "CED42D998760DB5FABEEB5C59C38F133BFABFC1BDC7E3759BB9FA1BEB0B52DE6",
}


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
    argparse.ArgumentParser(description=__doc__).parse_args()
    run_dir = ROOT / "evaluation" / "results" / RUN_ID
    if not run_dir.is_dir():
        raise SystemExit(f"missing accepted run directory: {run_dir}")

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from evaluation.profile import digest

    profile_path = run_dir / "profile.json"
    manifest_path = run_dir / "run-manifest.json"
    aggregate_path = run_dir / "aggregate-summary.json"
    public_aggregate_path = ROOT / "docs" / "provenance" / "accepted-aggregate.json"
    profile = read_json(profile_path)
    manifest = read_json(manifest_path)
    original_aggregate = read_json(aggregate_path)
    original_aggregate_hash = sha256(aggregate_path)

    subprocess.run(
        [sys.executable, "-m", "evaluation.validate", "--run", str(run_dir)],
        cwd=ROOT,
        check=True,
    )

    if profile["run_id"] != RUN_ID or manifest["run_id"] != RUN_ID or original_aggregate["run_id"] != RUN_ID:
        raise SystemExit("run ID mismatch")
    if profile["base_commit"] != BASE_COMMIT or manifest["base_commit"] != BASE_COMMIT or original_aggregate["base_commit"] != BASE_COMMIT:
        raise SystemExit("base commit mismatch")
    if digest(profile) != manifest["profile_digest"]:
        raise SystemExit("profile digest mismatch")
    for filename, expected in EXPECTED_EVIDENCE_SHA256.items():
        actual = sha256(run_dir / filename)
        if actual != expected:
            raise SystemExit(f"public evidence hash mismatch for {filename}: expected {expected}, actual {actual}")
    for filename, expected in EXPECTED_COUNTS.items():
        actual = jsonl_count(run_dir / filename)
        if actual != expected:
            raise SystemExit(f"{filename} count mismatch: expected {expected}, actual {actual}")
    if original_aggregate_hash != EXPECTED_AGGREGATE:
        raise SystemExit(f"accepted aggregate hash mismatch: {original_aggregate_hash}")

    with tempfile.TemporaryDirectory(prefix="asw-frozen-evidence-") as temp_dir:
        isolated_root = Path(temp_dir) / ROOT.name
        isolated_run = isolated_root / "evaluation" / "results" / RUN_ID
        isolated_run.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(run_dir, isolated_run)
        shutil.copytree(ROOT / "evaluation" / "scenarios", isolated_root / "evaluation" / "scenarios")
        subprocess.run(
            [sys.executable, "-m", "evaluation.aggregate", str(isolated_run)],
            cwd=ROOT,
            check=True,
        )
        recomputed_path = isolated_run / "aggregate-summary.json"
        recomputed = read_json(recomputed_path)
        recomputed_hash = sha256(recomputed_path)

    if recomputed_hash != original_aggregate_hash:
        raise SystemExit(f"recomputed aggregate mismatch: expected {original_aggregate_hash}, actual {recomputed_hash}")
    if public_aggregate_path.is_file() and sha256(public_aggregate_path) != original_aggregate_hash:
        raise SystemExit("public aggregate does not match the accepted aggregate")
    if headline(recomputed) != headline(original_aggregate):
        raise SystemExit("recomputed headline metrics differ from the accepted aggregate")

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
