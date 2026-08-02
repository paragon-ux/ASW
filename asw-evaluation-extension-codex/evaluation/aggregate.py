"""Regenerate an aggregate summary from immutable raw evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .metrics import aggregate_layer_a, aggregate_layer_a_by_class, aggregate_layer_b, build_summary, derive_integrity, select_best_baselines, threshold_audit
from .profile import digest, write_json
from .scenarios.controller import ScenarioController
from .schema import ValidationError, iter_jsonl, read_and_validate, validate_summary_semantics, validate_trial_semantics


def aggregate_run(run_dir: Path) -> dict:
    profile = read_and_validate(run_dir / "profile.json", "evaluation-profile")
    manifest = read_and_validate(run_dir / "run-manifest.json", "run-manifest")
    if manifest["profile_digest"] != digest(profile):
        raise ValueError("profile digest mismatch")
    definitions = ScenarioController.load_definitions(run_dir.parents[2] / "fixtures" / "scenarios")
    scenarios = {
        definition.scenario_id: {
            "scenario_id": definition.scenario_id,
            "class": definition.scenario_class,
            "primary": definition.primary,
            "applicable_baselines": list(definition.applicable_baselines),
        }
        for definition in definitions
    }
    records = list(iter_jsonl(run_dir / "raw-results.jsonl"))
    for record in records:
        validate_trial_semantics(record)
    ground_truth = list(iter_jsonl(run_dir / "ground-truth.jsonl"))
    usage = list(iter_jsonl(run_dir / "agent-usage.jsonl"))
    layer_a = aggregate_layer_a(records, scenarios)
    groups = aggregate_layer_a_by_class(records, scenarios)
    from .metrics import _rates
    layer_a["__classes__"] = {
        scenario_class: {condition: _rates(items) for condition, items in sorted(groups.get(scenario_class, {}).items())}
        for scenario_class in sorted(profile["primary_scenarios"])
    }
    best = select_best_baselines(records, scenarios, profile)
    layer_b = aggregate_layer_b(records, scenarios)
    integrity = derive_integrity(
        profile=profile,
        definitions=definitions,
        raw_records=records,
        ground_truth_records=ground_truth,
        usage_records=usage,
    )
    audit = threshold_audit(layer_a=layer_a, layer_b=layer_b, best_baselines=best, profile=profile, integrity=integrity)
    summary = build_summary(
        run_id=profile["run_id"], base_commit=profile["base_commit"], generated_at=manifest["completed_at"] or profile["frozen_at"],
        layer_a=layer_a, best_baselines=best, layer_b=layer_b, threshold_audit_result=audit,
    )
    validate_summary_semantics(summary)
    write_json(run_dir / "aggregate-summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    summary = aggregate_run(args.run)
    print(summary["classification"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
