"""Generate the human-readable Phase 8 evidence report from persisted JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _pct(value: object) -> str:
    return "n/a" if value is None else f"{float(value) * 100:.1f}%"


def _num(value: object) -> str:
    return "n/a" if value is None else f"{float(value):.2f}"


def generate_report(run_dir: Path, destination: Path) -> Path:
    profile = json.loads((run_dir / "profile.json").read_text(encoding="utf-8"))
    manifest = json.loads((run_dir / "run-manifest.json").read_text(encoding="utf-8"))
    summary = json.loads((run_dir / "aggregate-summary.json").read_text(encoding="utf-8"))
    audit = summary["threshold_audit"]
    lines = [
        f"# ASW Phase 8 Evaluation Results — {run_dir.name}",
        "",
        f"Final classification: {summary['classification']}",
        "",
        "This report is derived from the frozen profile, independent ground-truth JSONL, raw trial JSONL, and deterministic aggregate. It supports only the bounded RFC 0001 MVP proposition.",
        "",
        "## Repository and environment",
        "",
        f"- Base commit: {profile['base_commit']}",
        f"- Profile digest: {manifest['profile_digest']}",
        f"- Frozen at: {profile['frozen_at']}",
        f"- Completed at: {manifest['completed_at']}",
        f"- Harness version: {manifest['harness_version']}",
        f"- Host: {manifest['host'].get('os')} / Python {manifest['host'].get('python')}",
        "- Accepted runtime qualification: Windows 11 Pro build 22000 (Python reports the compatible Windows build string above).",
        f"- Core baseline status: {manifest.get('baseline_verification', {}).get('core_worktree_clean', 'not recorded')}",
        "",
        "## Hypothesis and frozen inputs",
        "",
        "The hypothesis is that structured ASW signals reduce unnecessary observation/tool effort while preserving transition recognition and continuation. Layer A is model-free. Layer B uses exactly the preregistered three repetitions per primary scenario and the same normalized deterministic continuation-agent configuration in both conditions; no post-result prompt, budget, interval, or threshold tuning occurred. The bounded continuation agent is deterministic and normalized; this run makes no external LLM-call claim.",
        "",
        f"- Primary repetitions: {profile['layer_a_repetitions_primary']}; secondary repetitions: {profile['layer_a_repetitions_secondary']}; Layer B repetitions: {profile['layer_b_repetitions']}",
        f"- Poll interval/deadline: {profile['poll_interval_ms']} ms / {profile['scenario_deadline_ms']} ms",
        f"- Random delay range and seed: {profile['random_delay_ms']} / {profile['seed']}",
        f"- Ordinary notification template: {profile['ordinary_notification_template']}",
        "",
        "## Scenario and baseline implementations",
        "",
        "Controlled probes cover job success/failure, stable external file/artifact transitions, UI modal/control transitions, render/export-style output, and crash/restart. Ground truth is recorded by the controller before each condition and is not passed to observers. Polling, filesystem-watch-only, ordinary plain-text notification, repeated observation, and ASW conditions use the same scenario timeline; non-applicable pairs are persisted explicitly.",
        "",
        "## Layer A results",
        "",
        "| Scenario | Condition | Trials | Detection | Median observations | Median latency (ms) | Kind accuracy | Attribution |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for scenario_id, conditions in sorted(summary["layer_a"].items()):
        if scenario_id == "__classes__":
            continue
        for condition, stats in sorted(conditions.items()):
            lines.append(
                f"| {scenario_id} | {condition} | {stats['trials']} | {_pct(stats['detected'])} | {_num(stats['median_observation_count'])} | {_num(stats['median_detection_latency_ms'])} | {_pct(stats['kind_accuracy'])} | {_pct(stats['application_attribution_accuracy'])} |"
            )
    lines.extend(["", "### Best-baseline selection", "", "The preregistered rule (highest detection, then lowest misses, then median observations, then median latency, then lexical ID) selected:", ""])
    for scenario_class, baseline in sorted(summary["best_non_asw_baseline_by_scenario"].items()):
        lines.append(f"- {scenario_class} -> {baseline}")
    lines.extend(["", "## Layer B continuation results", "", "| Scenario class | Condition | Trials | Continuation success | Median observation calls | Median continuation latency (ms) |", "|---|---|---:|---:|---:|---:|"])
    for scenario_class, conditions in sorted(summary["layer_b"].items()):
        if scenario_class == "__combined__":
            continue
        for condition, stats in sorted(conditions.items()):
            lines.append(f"| {scenario_class} | {condition} | {stats['trials']} | {_pct(stats['continuation_success'])} | {_num(stats['median_agent_observation_calls'])} | {_num(stats['median_continuation_latency_ms'])} |")
    lines.extend([
        "",
        "## Failures, exclusions, and integrity",
        "",
        f"- Ground-truth records: {audit['integrity'].get('ground_truth_records')}; unique IDs: {audit['integrity'].get('ground_truth_unique_trial_ids')}; completeness: {audit['integrity'].get('ground_truth_completeness_pass')}.",
        f"- Agent-usage records: {audit['integrity'].get('agent_usage_records')}; completeness/configuration: {audit['integrity'].get('agent_usage_completeness_pass')}.",
        f"- Layer A model calls: {audit['integrity'].get('layer_a_model_calls')}.",
        f"- Authorization violations: {audit['integrity'].get('authorization_violations')}; replay violations: {audit['integrity'].get('replay_violations')}.",
        "- Invalidated runs are retained separately and excluded from this classification; their persisted invalidation records are listed below.",
        "",
        "## Threshold audit",
        "",
        f"- Detection success: {_pct(audit['correctness']['asw_detection_success'])} vs minimum {_pct(audit['correctness']['detection_success_min'])} — {'PASS' if audit['correctness']['detection_pass'] else 'FAIL'}",
        f"- Duplicate useful-signal rate: {_pct(audit['correctness']['asw_duplicate_rate'])} vs maximum {_pct(audit['correctness']['duplicate_rate_max'])} — {'PASS' if audit['correctness']['duplicate_pass'] else 'FAIL'}",
        f"- False-positive useful-signal rate: {_pct(audit['correctness']['asw_false_positive_rate'])} vs maximum {_pct(audit['correctness']['false_positive_rate_max'])} — {'PASS' if audit['correctness']['false_positive_pass'] else 'FAIL'}",
        f"- Attribution accuracy: {_pct(audit['correctness']['asw_attribution_accuracy'])} vs minimum {_pct(audit['correctness']['attribution_accuracy_min'])} — {'PASS' if audit['correctness']['attribution_pass'] else 'FAIL'}",
        f"- Kind accuracy: {_pct(audit['correctness']['asw_kind_accuracy'])} vs minimum {_pct(audit['correctness']['kind_accuracy_min'])} — {'PASS' if audit['correctness']['kind_pass'] else 'FAIL'}",
        f"- Layer A observation reduction: {audit['layer_a_efficiency']['classes_passing']} classes pass; required {audit['layer_a_efficiency']['required_classes']} — {'PASS' if audit['layer_a_efficiency']['pass'] else 'FAIL'}",
        f"- Layer B continuation non-inferiority: delta {_pct(audit['layer_b_continuation']['success_delta_baseline_minus_asw'])} vs maximum {_pct(audit['layer_b_continuation']['success_noninferiority_pp'])} — {'PASS' if audit['layer_b_continuation']['success_pass'] else 'FAIL'}",
        f"- Layer B efficiency: call improvement {_pct(audit['layer_b_continuation']['observation_call_improvement'])}, latency improvement {_pct(audit['layer_b_continuation']['latency_improvement'])}; minimum {_pct(audit['layer_b_continuation']['efficiency_improvement_min'])} — {'PASS' if audit['layer_b_continuation']['efficiency_pass'] else 'FAIL'}",
        f"- Integrity gate: {'PASS' if audit['integrity'].get('pass') else 'FAIL'}",
        f"- Final threshold gate: {'PASS' if audit.get('pass') else 'FAIL'}",
        "",
        "## Evidence paths",
        "",
        f"- Frozen profile: {run_dir / 'profile.json'}",
        f"- Run manifest: {run_dir / 'run-manifest.json'}",
        f"- Ground truth: {run_dir / 'ground-truth.jsonl'}",
        f"- Raw trial results: {run_dir / 'raw-results.jsonl'}",
        f"- Agent usage: {run_dir / 'agent-usage.jsonl'}",
        f"- Aggregate summary: {run_dir / 'aggregate-summary.json'}",
        "",
        "## Reproducibility",
        "",
        f"    python -m evaluation.validate --run {run_dir}",
        f"    python -m evaluation.aggregate {run_dir}",
        "",
        "A SUPPORTED result here is limited to this bounded controlled RFC 0001 MVP proposition; it does not establish universal application coverage, cross-platform behavior, or universal agent benefit.",
        "",
    ])
    invalidated = sorted(run_dir.parent.glob("*/INVALIDATED.md"))
    lines.insert(-1, "")
    if invalidated:
        lines.insert(-1, "- Invalidation records: " + "; ".join(str(path) for path in invalidated) + ".")
    core_defect = audit["integrity"].get("core_defect_discovered")
    lines.insert(-1, f"- Core-defect audit: {'a reproducible core defect was recorded' if core_defect else 'no reproducible core defect was recorded'}.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "docs" / "research" / "evaluation-results.md")
    args = parser.parse_args()
    print(generate_report(args.run, args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
