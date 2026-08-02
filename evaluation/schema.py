"""Schema and semantic validation for the evaluation extension.

The extension deliberately keeps schema validation separate from the run
engine.  A profile or result is never accepted merely because it is JSON; it
must satisfy the frozen contract and the small set of cross-record invariants
that JSON Schema cannot express.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPOSITORY_ROOT / "evaluation"
ROOT = REPOSITORY_ROOT
SCHEMA_DIR = EVALUATION_ROOT / "schemas"
SCHEMA_FILES = {
    "evaluation-profile": "evaluation-profile.schema.json",
    "scenario": "scenario.schema.json",
    "trial-result": "trial-result.schema.json",
    "run-manifest": "run-manifest.schema.json",
    "summary": "summary.schema.json",
}


def _load_schemas() -> tuple[dict[str, dict[str, Any]], Registry]:
    schemas: dict[str, dict[str, Any]] = {}
    registry = Registry()
    for filename in SCHEMA_FILES.values():
        document = json.loads((SCHEMA_DIR / filename).read_text(encoding="utf-8"))
        schemas[filename] = document
        registry = registry.with_resource(document["$id"], Resource.from_contents(document))
    return schemas, registry


SCHEMAS, REGISTRY = _load_schemas()


class ValidationError(ValueError):
    """Raised when a document fails schema or extension semantic validation."""


def schema_for(kind: str) -> dict[str, Any]:
    try:
        return SCHEMAS[SCHEMA_FILES[kind]]
    except KeyError as exc:
        raise ValidationError(f"unknown evaluation document kind: {kind}") from exc


def validate_document(document: Any, kind: str) -> None:
    validator = Draft202012Validator(
        schema_for(kind), registry=REGISTRY, format_checker=FormatChecker()
    )
    errors = sorted(validator.iter_errors(document), key=lambda error: list(error.path))
    if errors:
        error = errors[0]
        location = "".join(f"[{part!r}]" for part in error.path)
        raise ValidationError(f"{kind}{location}: {error.message}")


def read_and_validate(path: Path, kind: str) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read {path}: {exc}") from exc
    validate_document(document, kind)
    return document


def validate_scenario_semantics(scenario: dict[str, Any]) -> None:
    """Validate invariants shared by all controlled scenario manifests."""

    validate_document(scenario, "scenario")
    applicable = set(scenario["applicable_baselines"])
    if "asw" not in applicable:
        raise ValidationError(f"{scenario['scenario_id']}: ASW must be applicable")
    if len(applicable) < 2:
        raise ValidationError(f"{scenario['scenario_id']}: at least two conditions are required")
    if scenario["primary"] and scenario["class"] not in {
        "job_completion",
        "file_artifact_transition",
        "ui_transition",
    }:
        raise ValidationError(f"{scenario['scenario_id']}: unknown primary class")
    if not scenario["primary"] and scenario["class"] not in {
        "render_export",
        "process_crash_restart",
    }:
        raise ValidationError(f"{scenario['scenario_id']}: secondary class must be declared")


def validate_profile_semantics(profile: dict[str, Any]) -> None:
    """Reject profiles that are structurally valid but not the preregistration."""

    validate_document(profile, "evaluation-profile")
    if profile["random_delay_ms"]["min"] >= profile["random_delay_ms"]["max"]:
        raise ValidationError("randomized delay range must have min < max")
    if set(profile["primary_scenarios"]) != {
        "job_completion",
        "file_artifact_transition",
        "ui_transition",
    }:
        raise ValidationError("profile must contain exactly the three primary scenario classes")
    if set(profile["baselines"]) != {
        "polling",
        "filesystem_watch",
        "ordinary_notification",
        "repeated_observation",
        "asw",
    }:
        raise ValidationError("profile must contain every declared baseline")


def validate_trial_semantics(trial: dict[str, Any]) -> None:
    validate_document(trial, "trial-result")
    if trial["status"] == "not_applicable":
        if trial["error"] != "not_applicable":
            raise ValidationError(f"{trial['trial_id']}: not_applicable result needs a fixed reason")
        if trial["recognized_ns"] is not None or trial["detection_latency_ms"] is not None:
            raise ValidationError(f"{trial['trial_id']}: not_applicable result cannot be recognized")
    if trial["status"] == "completed" and trial["missed"] != (not trial["detected"]):
        raise ValidationError(f"{trial['trial_id']}: missed must be the complement of detected")
    if trial["detected"] and trial["recognized_ns"] is None:
        raise ValidationError(f"{trial['trial_id']}: detected result needs recognized_ns")
    if not trial["detected"] and trial["recognized_ns"] is not None:
        raise ValidationError(f"{trial['trial_id']}: missed result cannot have recognized_ns")


def validate_summary_semantics(summary: dict[str, Any]) -> None:
    validate_document(summary, "summary")
    if summary["classification"] not in {"SUPPORTED", "NOT_SUPPORTED", "INCONCLUSIVE"}:
        raise ValidationError("summary classification is outside the frozen vocabulary")


def validate_fixture_tree() -> tuple[list[Path], list[Path]]:
    """Validate all valid/invalid JSON and scenario manifests."""

    valid: list[Path] = []
    invalid: list[Path] = []
    valid_dir = EVALUATION_ROOT / "fixtures" / "valid"
    invalid_dir = EVALUATION_ROOT / "fixtures" / "invalid"
    for path in sorted(valid_dir.glob("*.json")):
        kind = path.name.split(".")[0]
        document = read_and_validate(path, kind)
        if kind == "evaluation-profile":
            validate_profile_semantics(document)
        valid.append(path)
    for path in sorted(invalid_dir.glob("*.json")):
        kind = path.name.split(".")[0]
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
            validate_document(document, kind)
        except (ValidationError, json.JSONDecodeError):
            invalid.append(path)
            continue
        raise ValidationError(f"invalid fixture unexpectedly validates: {path}")
    for path in sorted((EVALUATION_ROOT / "scenarios").glob("*.json")):
        validate_scenario_semantics(read_and_validate(path, "scenario"))
        valid.append(path)
    return valid, invalid


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValidationError(f"{path}:{line_number}: JSONL record must be an object")
        yield value
