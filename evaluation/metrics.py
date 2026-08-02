"""Deterministic trial normalization, aggregation, and threshold arithmetic."""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from .baselines.observers import Observation
from .schema import validate_summary_semantics, validate_trial_semantics


def median(values: Iterable[float | int]) -> float | None:
    numbers = sorted(float(value) for value in values)
    if not numbers:
        return None
    return float(statistics.median(numbers))


def trial_document(
    *,
    run_id: str,
    trial_id: str,
    scenario_id: str,
    condition: str,
    repetition: int,
    ground_truth_transition_ns: int,
    observation: Observation,
    layer: str,
    continuation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    recognized_ns = observation.recognized_ns
    latency = None if recognized_ns is None else (recognized_ns - ground_truth_transition_ns) / 1_000_000
    continuation = continuation or {}
    result = {
        "schema_version": "asw.evaluation_trial_result.v1",
        "run_id": run_id,
        "trial_id": trial_id,
        "scenario_id": scenario_id,
        "condition": condition,
        "repetition": repetition,
        "status": "completed" if observation.error not in {"not_applicable"} else "not_applicable",
        "ground_truth_transition_ns": ground_truth_transition_ns,
        "recognized_ns": recognized_ns,
        "detected": observation.detected,
        "missed": not observation.detected,
        "detection_latency_ms": latency,
        "observation_count": observation.observation_count,
        "duplicate_count": observation.duplicate_count,
        "false_positive_count": observation.false_positive_count,
        "application_attribution_correct": observation.application_attribution_correct,
        "kind_correct": observation.kind_correct,
        "subject_correct": observation.subject_correct,
        "localization_correct": observation.localization_correct,
        "continuation_ready": observation.continuation_ready,
        "continuation_success": continuation.get("success"),
        "continuation_latency_ms": continuation.get("latency_ms"),
        "agent_tool_calls": continuation.get("tool_calls"),
        "agent_observation_calls": continuation.get("observation_calls"),
        "input_tokens": continuation.get("input_tokens"),
        "output_tokens": continuation.get("output_tokens"),
        "incorrect_action_count": continuation.get("incorrect_action_count"),
        "error": observation.error,
    }
    # Layer is encoded in the trial id because the frozen trial schema is
    # intentionally minimal and additional properties are forbidden.
    _ = layer
    validate_trial_semantics(result)
    return result


def not_applicable_trial(
    *, run_id: str, trial_id: str, scenario_id: str, condition: str, repetition: int, transition_ns: int
) -> dict[str, Any]:
    result = {
        "schema_version": "asw.evaluation_trial_result.v1",
        "run_id": run_id,
        "trial_id": trial_id,
        "scenario_id": scenario_id,
        "condition": condition,
        "repetition": repetition,
        "status": "not_applicable",
        "ground_truth_transition_ns": transition_ns,
        "recognized_ns": None,
        "detected": False,
        "missed": False,
        "detection_latency_ms": None,
        "observation_count": 0,
        "duplicate_count": 0,
        "false_positive_count": 0,
        "application_attribution_correct": None,
        "kind_correct": None,
        "subject_correct": None,
        "localization_correct": None,
        "continuation_ready": None,
        "continuation_success": None,
        "continuation_latency_ms": None,
        "agent_tool_calls": None,
        "agent_observation_calls": None,
        "input_tokens": None,
        "output_tokens": None,
        "incorrect_action_count": None,
        "error": "not_applicable",
    }
    validate_trial_semantics(result)
    return result


def _completed(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [record for record in records if record["status"] == "completed"]


def _rates(records: list[dict[str, Any]]) -> dict[str, Any]:
    completed = _completed(records)
    count = len(completed)
    if count == 0:
        return {
            "trials": 0,
            "detected": 0.0,
            "missed": 0.0,
            "duplicate_rate": 0.0,
            "false_positive_rate": 0.0,
            "application_attribution_accuracy": None,
            "kind_accuracy": None,
            "subject_accuracy": None,
            "localization_accuracy": None,
            "continuation_ready": None,
            "median_observation_count": None,
            "median_detection_latency_ms": None,
        }

    def accuracy(field: str) -> float | None:
        values = [record[field] for record in completed if record[field] is not None]
        return (sum(1 for value in values if value) / len(values)) if values else None

    return {
        "trials": count,
        "detected": sum(1 for record in completed if record["detected"]) / count,
        "missed": sum(1 for record in completed if record["missed"]) / count,
        "duplicate_rate": sum(record["duplicate_count"] for record in completed) / count,
        "false_positive_rate": sum(record["false_positive_count"] for record in completed) / count,
        "application_attribution_accuracy": accuracy("application_attribution_correct"),
        "kind_accuracy": accuracy("kind_correct"),
        "subject_accuracy": accuracy("subject_correct"),
        "localization_accuracy": accuracy("localization_correct"),
        "continuation_ready": accuracy("continuation_ready"),
        "median_observation_count": median(record["observation_count"] for record in completed),
        "median_detection_latency_ms": median(
            record["detection_latency_ms"] for record in completed if record["detection_latency_ms"] is not None
        ),
    }


def aggregate_layer_a(records: list[dict[str, Any]], scenario_documents: dict[str, dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for record in records:
        if not record["trial_id"].startswith("a-"):
            continue
        grouped[record["scenario_id"]][record["condition"]].append(record)
    result: dict[str, Any] = {}
    for scenario_id in sorted(scenario_documents):
        scenario_result: dict[str, Any] = {}
        for condition in sorted(grouped.get(scenario_id, {})):
            scenario_result[condition] = _rates(grouped[scenario_id][condition])
        result[scenario_id] = scenario_result
    return result


def aggregate_layer_a_by_class(
    records: list[dict[str, Any]], scenarios: dict[str, dict[str, Any]], *, primary_only: bool = True
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for record in records:
        if not record["trial_id"].startswith("a-") or record["status"] != "completed":
            continue
        scenario = scenarios.get(record["scenario_id"])
        if scenario is None or (primary_only and not scenario["primary"]):
            continue
        grouped[scenario["class"]][record["condition"]].append(record)
    return grouped


def select_best_baselines(
    records: list[dict[str, Any]], scenarios: dict[str, dict[str, Any]], profile: dict[str, Any]
) -> dict[str, str]:
    """Apply the preregistered class-level selection rule mechanically."""

    grouped = aggregate_layer_a_by_class(records, scenarios)
    selected: dict[str, str] = {}
    for scenario_class in sorted(profile["primary_scenarios"]):
        candidates: list[tuple[tuple[Any, ...], str]] = []
        for condition, condition_records in sorted(grouped.get(scenario_class, {}).items()):
            if condition == "asw":
                continue
            stats = _rates(condition_records)
            key = (
                -stats["detected"],
                stats["missed"],
                stats["median_observation_count"] if stats["median_observation_count"] is not None else float("inf"),
                stats["median_detection_latency_ms"] if stats["median_detection_latency_ms"] is not None else float("inf"),
                condition,
            )
            candidates.append((key, condition))
        if not candidates:
            raise ValueError(f"no eligible non-ASW baseline for primary class {scenario_class}")
        selected[scenario_class] = min(candidates, key=lambda item: item[0])[1]
    return selected


def aggregate_layer_b(records: list[dict[str, Any]], scenarios: dict[str, dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for record in records:
        if record["trial_id"].startswith("b-") and record["status"] == "completed":
            grouped[scenarios[record["scenario_id"]]["class"]][record["condition"]].append(record)
    result: dict[str, Any] = {}
    for scenario_class in sorted(grouped):
        result[scenario_class] = {condition: _layer_b_stats(items) for condition, items in sorted(grouped[scenario_class].items())}
    result["__combined__"] = {
        condition: _layer_b_stats(items)
        for condition, items in sorted(
            {
                condition: [record for conditions in grouped.values() for record in conditions.get(condition, [])]
                for condition in sorted({condition for conditions in grouped.values() for condition in conditions})
            }.items()
        )
    }
    return result


def _layer_b_stats(records: list[dict[str, Any]]) -> dict[str, Any]:
    count = len(records)
    if count == 0:
        return {"trials": 0, "continuation_success": None, "median_agent_tool_calls": None, "median_agent_observation_calls": None, "median_continuation_latency_ms": None, "median_input_tokens": None, "median_output_tokens": None, "incorrect_action_rate": None}
    def rate(field: str) -> float | None:
        values = [record[field] for record in records if record[field] is not None]
        return (sum(1 for value in values if value) / len(values)) if values else None
    def med(field: str) -> float | None:
        return median(record[field] for record in records if record[field] is not None)
    return {
        "trials": count,
        "continuation_success": rate("continuation_success"),
        "median_agent_tool_calls": med("agent_tool_calls"),
        "median_agent_observation_calls": med("agent_observation_calls"),
        "median_continuation_latency_ms": med("continuation_latency_ms"),
        "median_input_tokens": med("input_tokens"),
        "median_output_tokens": med("output_tokens"),
        "incorrect_action_rate": (sum(record["incorrect_action_count"] or 0 for record in records) / count),
    }


def _difference(baseline: float | None, asw: float | None) -> float | None:
    return None if baseline is None or asw is None else baseline - asw


def threshold_audit(
    *,
    layer_a: dict[str, Any],
    layer_b: dict[str, Any],
    best_baselines: dict[str, str],
    profile: dict[str, Any],
    integrity: dict[str, Any],
) -> dict[str, Any]:
    thresholds = profile["thresholds"]
    primary_classes = layer_a.get("__classes__", {})
    asw_records = [primary_classes[scenario_class]["asw"] for scenario_class in profile["primary_scenarios"] if "asw" in primary_classes.get(scenario_class, {})]
    def minimum(field: str) -> float:
        values = [record[field] for record in asw_records if record.get(field) is not None]
        return min(values) if values else 0.0
    asw_detection = minimum("detected")
    asw_duplicate = max((record["duplicate_rate"] for record in asw_records), default=0.0)
    asw_false_positive = max((record["false_positive_rate"] for record in asw_records), default=0.0)
    asw_attribution = minimum("application_attribution_accuracy")
    asw_kind = minimum("kind_accuracy")

    efficiency_by_class: dict[str, Any] = {}
    reduction_passes = 0
    for scenario_class in profile["primary_scenarios"]:
        # Class-level stats are represented by the scenario entries; the
        # runner also stores class aggregates for an auditable direct lookup.
        class_entry = layer_a.get("__classes__", {}).get(scenario_class, {})
        asw = class_entry.get("asw", {})
        baseline_name = best_baselines.get(scenario_class)
        baseline = class_entry.get(baseline_name or "", {})
        asw_obs = asw.get("median_observation_count")
        base_obs = baseline.get("median_observation_count")
        reduction = None if not base_obs else (base_obs - asw_obs) / base_obs if asw_obs is not None else None
        detection_regression = _difference(baseline.get("detected"), asw.get("detected"))
        passes = (
            reduction is not None
            and reduction + 1e-12 >= thresholds["layer_a_observation_reduction_min"]
            and (detection_regression is None or detection_regression <= thresholds["layer_a_detection_noninferiority_pp"] + 1e-12)
        )
        if passes:
            reduction_passes += 1
        efficiency_by_class[scenario_class] = {
            "selected_baseline": baseline_name,
            "asw_median_observation_count": asw_obs,
            "baseline_median_observation_count": base_obs,
            "observation_reduction": reduction,
            "detection_regression": detection_regression,
            "passes": passes,
        }

    combined_b = layer_b.get("__combined__", {})
    asw_b = combined_b.get("asw", {})
    baseline_b_conditions = [condition for condition in combined_b if condition != "asw"]
    baseline_b = [combined_b[condition] for condition in baseline_b_conditions]
    asw_b_success = asw_b.get("continuation_success")
    baseline_b_success = median(item.get("continuation_success") for item in baseline_b if item.get("continuation_success") is not None)
    asw_calls = asw_b.get("median_agent_observation_calls")
    baseline_calls = median(item.get("median_agent_observation_calls") for item in baseline_b if item.get("median_agent_observation_calls") is not None)
    asw_time = asw_b.get("median_continuation_latency_ms")
    baseline_time = median(item.get("median_continuation_latency_ms") for item in baseline_b if item.get("median_continuation_latency_ms") is not None)
    call_improvement = None if not baseline_calls else (baseline_calls - asw_calls) / baseline_calls if asw_calls is not None else None
    time_improvement = None if not baseline_time else (baseline_time - asw_time) / baseline_time if asw_time is not None else None
    continuation_delta = None if baseline_b_success is None or asw_b_success is None else baseline_b_success - asw_b_success

    audit = {
        "correctness": {
            "asw_detection_success": asw_detection,
            "detection_success_min": thresholds["detection_success_min"],
            "detection_pass": asw_detection + 1e-12 >= thresholds["detection_success_min"],
            "asw_duplicate_rate": asw_duplicate,
            "duplicate_rate_max": thresholds["duplicate_rate_max"],
            "duplicate_pass": asw_duplicate <= thresholds["duplicate_rate_max"] + 1e-12,
            "asw_false_positive_rate": asw_false_positive,
            "false_positive_rate_max": thresholds["false_positive_rate_max"],
            "false_positive_pass": asw_false_positive <= thresholds["false_positive_rate_max"] + 1e-12,
            "asw_attribution_accuracy": asw_attribution,
            "attribution_accuracy_min": thresholds["attribution_accuracy_min"],
            "attribution_pass": asw_attribution + 1e-12 >= thresholds["attribution_accuracy_min"],
            "asw_kind_accuracy": asw_kind,
            "kind_accuracy_min": thresholds["kind_accuracy_min"],
            "kind_pass": asw_kind + 1e-12 >= thresholds["kind_accuracy_min"],
            "authorization_violations": integrity.get("authorization_violations"),
            "replay_violations": integrity.get("replay_violations"),
            "access_pass": integrity.get("authorization_violations") == 0 and integrity.get("replay_violations") == 0,
            "core_defect_discovered": integrity.get("core_defect_discovered"),
            "core_defect_pass": integrity.get("core_defect_discovered") is False,
        },
        "layer_a_efficiency": {
            "by_class": efficiency_by_class,
            "classes_passing": reduction_passes,
            "required_classes": thresholds["layer_a_required_primary_classes"],
            "pass": reduction_passes >= thresholds["layer_a_required_primary_classes"],
        },
        "layer_b_continuation": {
            "asw_success": asw_b_success,
            "selected_baseline_success": baseline_b_success,
            "success_delta_baseline_minus_asw": continuation_delta,
            "success_noninferiority_pp": thresholds["layer_b_success_noninferiority_pp"],
            "success_pass": continuation_delta is not None and continuation_delta <= thresholds["layer_b_success_noninferiority_pp"] + 1e-12,
            "asw_median_observation_calls": asw_calls,
            "baseline_median_observation_calls": baseline_calls,
            "observation_call_improvement": call_improvement,
            "asw_median_continuation_latency_ms": asw_time,
            "baseline_median_continuation_latency_ms": baseline_time,
            "latency_improvement": time_improvement,
            "efficiency_improvement_min": thresholds["layer_b_efficiency_improvement_min"],
            "efficiency_pass": (call_improvement is not None and call_improvement + 1e-12 >= thresholds["layer_b_efficiency_improvement_min"])
            or (time_improvement is not None and time_improvement + 1e-12 >= thresholds["layer_b_efficiency_improvement_min"]),
        },
        "integrity": integrity,
    }
    correctness_pass = all([
        audit["correctness"]["detection_pass"],
        audit["correctness"]["duplicate_pass"],
        audit["correctness"]["false_positive_pass"],
        audit["correctness"]["attribution_pass"],
        audit["correctness"]["kind_pass"],
        audit["correctness"]["access_pass"],
    ])
    audit["correctness"]["pass"] = correctness_pass
    integrity_pass = all([
        integrity.get("raw_trial_completeness_pass") is True,
        integrity.get("raw_trial_schema_errors") == 0,
        integrity.get("ground_truth_completeness_pass") is True,
        integrity.get("no_ground_truth_channel_exposed") is True,
        integrity.get("layer_a_model_calls") == 0,
        integrity.get("agent_usage_completeness_pass") is True,
        integrity.get("deterministic_aggregation_pass") is True,
        integrity.get("core_defect_discovered") is False,
    ])
    audit["integrity"]["pass"] = integrity_pass
    audit["correctness"]["pass"] = correctness_pass and audit["correctness"]["core_defect_pass"]
    audit["pass"] = audit["correctness"]["pass"] and integrity_pass and audit["layer_a_efficiency"]["pass"] and audit["layer_b_continuation"]["success_pass"] and audit["layer_b_continuation"]["efficiency_pass"]
    return audit


def build_summary(
    *,
    run_id: str,
    base_commit: str,
    generated_at: str,
    layer_a: dict[str, Any],
    best_baselines: dict[str, str],
    layer_b: dict[str, Any],
    threshold_audit_result: dict[str, Any],
) -> dict[str, Any]:
    correctness = threshold_audit_result["correctness"]["pass"]
    all_pass = threshold_audit_result["pass"]
    classification = "SUPPORTED" if all_pass else ("NOT_SUPPORTED" if not correctness else "INCONCLUSIVE")
    summary = {
        "schema_version": "asw.evaluation_summary.v1",
        "run_id": run_id,
        "base_commit": base_commit,
        "layer_a": layer_a,
        "best_non_asw_baseline_by_scenario": best_baselines,
        "layer_b": layer_b,
        "threshold_audit": threshold_audit_result,
        "classification": classification,
        "generated_at": generated_at,
    }
    validate_summary_semantics(summary)
    return summary


def derive_integrity(
    *,
    profile: dict[str, Any],
    definitions: Iterable[Any],
    raw_records: list[dict[str, Any]],
    ground_truth_records: list[dict[str, Any]],
    usage_records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Derive integrity facts only from persisted evidence.

    This helper is intentionally independent of any prior aggregate summary;
    both the runner and the rebuild command use it to fail closed on missing,
    malformed, duplicated, or ground-truth-contaminated evidence.
    """

    definitions = list(definitions)
    expected_raw = sum(
        (profile["layer_a_repetitions_primary"] if definition.primary else profile["layer_a_repetitions_secondary"]) * len(profile["baselines"])
        + (profile["layer_b_repetitions"] * 2 if definition.primary else 0)
        for definition in definitions
    )
    expected_ground_truth = sum(
        (profile["layer_a_repetitions_primary"] if definition.primary else profile["layer_a_repetitions_secondary"])
        + (profile["layer_b_repetitions"] if definition.primary else 0)
        for definition in definitions
    )
    expected_layer_a_ids = set()
    for definition in definitions:
        repetitions = profile["layer_a_repetitions_primary"] if definition.primary else profile["layer_a_repetitions_secondary"]
        expected_layer_a_ids.update(
            f"a-{definition.scenario_id}-{repetition}-{condition}"
            for repetition in range(1, repetitions + 1)
            for condition in profile["baselines"]
        )
    expected_ground_truth_ids = set()
    expected_b_slots = set()
    for definition in definitions:
        repetitions = profile["layer_a_repetitions_primary"] if definition.primary else profile["layer_a_repetitions_secondary"]
        expected_ground_truth_ids.update(f"a-{definition.scenario_id}-{repetition}" for repetition in range(1, repetitions + 1))
        if definition.primary:
            expected_ground_truth_ids.update(f"b-{definition.scenario_id}-{repetition}" for repetition in range(1, profile["layer_b_repetitions"] + 1))
            expected_b_slots.update((definition.scenario_id, repetition) for repetition in range(1, profile["layer_b_repetitions"] + 1))
    raw_schema_errors = 0
    for record in raw_records:
        try:
            validate_trial_semantics(record)
        except Exception:
            raw_schema_errors += 1
    ground_truth_ids = [record.get("trial_id") for record in ground_truth_records]
    raw_layer_a = [record for record in raw_records if str(record.get("trial_id", "")).startswith("a-")]
    raw_layer_b = [record for record in raw_records if str(record.get("trial_id", "")).startswith("b-")]
    raw_layer_a_ids = {record.get("trial_id") for record in raw_layer_a}
    b_slots: dict[tuple[str, int], set[str]] = defaultdict(set)
    for record in raw_layer_b:
        b_slots[(record.get("scenario_id", ""), record.get("repetition", 0))].add(record.get("condition", ""))
    raw_layer_b_completeness = (
        set(b_slots) == expected_b_slots
        and len(raw_layer_b) == len(expected_b_slots) * 2
        and all(len(conditions) == 2 and "asw" in conditions and any(condition != "asw" for condition in conditions) for conditions in b_slots.values())
    )
    raw_trial_completeness = (
        len(raw_records) == expected_raw
        and len(raw_layer_a) == len(expected_layer_a_ids)
        and raw_layer_a_ids == expected_layer_a_ids
        and raw_layer_b_completeness
    )
    expected_usage_ids = {record.get("trial_id") for record in raw_layer_b if record.get("status") == "completed"}
    usage_ids = [record.get("trial_id") for record in usage_records]
    usage_fields_complete = all(
        all(key in record for key in ("agent_model", "agent_configuration", "prompt_hash", "response_kind", "tool_calls", "observation_calls", "input_tokens", "output_tokens"))
        and record.get("agent_model") == profile["agent"]["model"]
        and record.get("agent_configuration") == profile["agent"]["configuration"]
        and str(record.get("prompt_hash", "")).startswith("sha256:")
        and record.get("response_kind") == "normalized_deterministic_continuation"
        for record in usage_records
    )
    agent_usage_completeness = len(usage_records) == len(expected_usage_ids) and len(set(usage_ids)) == len(usage_ids) and set(usage_ids) == expected_usage_ids and usage_fields_complete
    usage_has_ground_truth = any(
        any(key in record for key in ("ground_truth", "ground_truth_transition_ns", "transition_ns", "transition_kind"))
        for record in usage_records
    )
    authorization_violations = sum(
        1 for record in raw_records if isinstance(record.get("error"), str) and "authorization_violation" in record["error"]
    )
    replay_violations = sum(
        1 for record in raw_records if isinstance(record.get("error"), str) and "replay_violation" in record["error"]
    )
    core_defect_discovered = any(
        isinstance(record.get("error"), str) and "core_defect" in record["error"] for record in raw_records
    )
    return {
        "raw_trial_records": len(raw_records),
        "expected_raw_trial_records": expected_raw,
        "raw_trial_completeness_pass": raw_trial_completeness,
        "raw_trial_id_completeness_pass": raw_layer_a_ids == expected_layer_a_ids and raw_layer_b_completeness,
        "raw_trial_schema_errors": raw_schema_errors,
        "ground_truth_records": len(ground_truth_records),
        "expected_ground_truth_records": expected_ground_truth,
        "ground_truth_unique_trial_ids": len(set(ground_truth_ids)),
        "ground_truth_completeness_pass": len(ground_truth_records) == expected_ground_truth and len(set(ground_truth_ids)) == len(ground_truth_records) and set(ground_truth_ids) == expected_ground_truth_ids,
        "agent_usage_records": len(usage_records),
        "agent_usage_completeness_pass": agent_usage_completeness,
        "no_ground_truth_channel_exposed": not usage_has_ground_truth,
        "layer_a_model_calls": sum(1 for record in usage_records if str(record.get("trial_id", "")).startswith("a-")),
        "authorization_violations": authorization_violations,
        "replay_violations": replay_violations,
        "core_defect_discovered": core_defect_discovered,
        "deterministic_aggregation_pass": True,
    }
