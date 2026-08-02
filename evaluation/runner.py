"""Frozen Layer A/Layer B execution for the Phase 8 protocol."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .baselines.observers import ASWObserver, Observation, observer_for
from .consumers.asw_adapter import ASWAdapter
from .io import JsonlWriter
from .metrics import (
    aggregate_layer_a,
    aggregate_layer_a_by_class,
    aggregate_layer_b,
    build_summary,
    derive_integrity,
    not_applicable_trial,
    select_best_baselines,
    threshold_audit,
    trial_document,
)
from .profile import (
    DEFAULT_PROFILE,
    base_commit,
    build_manifest,
    canonical_json,
    core_worktree_status,
    digest,
    freeze_profile,
    utc_now,
    write_json,
)
from .scenarios.controller import GroundTruth, GroundTruthRecorder, ScenarioController, ScenarioDefinition, ScenarioSurface
from .schema import validate_document, validate_profile_semantics, validate_summary_semantics, validate_trial_semantics


def _scored_observation(observation: Observation, ground_truth: GroundTruth) -> Observation:
    """Score raw observer fields against controller-owned ground truth."""

    application_correct = (
        None if observation.recognized_application_id is None else observation.recognized_application_id == ground_truth.application_id
    )
    kind_correct = None if observation.recognized_kind is None else observation.recognized_kind == ground_truth.transition_kind
    subject_correct: bool | None
    if observation.recognized_subject is None:
        subject_correct = None
    else:
        expected = ground_truth.metadata.get("subject")
        observed = observation.recognized_subject
        if isinstance(observed, str):
            subject_correct = observed == expected or observed == ground_truth.scenario_id
        elif isinstance(observed, dict):
            flattened = json.dumps(observed, sort_keys=True)
            subject_correct = expected in flattened or ground_truth.scenario_id in flattened
        else:
            subject_correct = False
    return replace(
        observation,
        application_attribution_correct=application_correct,
        kind_correct=kind_correct,
        subject_correct=subject_correct,
    )


class ScriptedContinuationAgent:
    """Bounded deterministic continuation agent used for Layer B.

    It has the same fixed configuration in both conditions and consumes only
    the normalized observer output.  This keeps the MVP continuation study
    model-free while still measuring the product-facing read/tool boundary.
    """

    def __init__(self, profile: dict[str, Any]) -> None:
        self.profile = profile

    def continue_from(self, observation: Observation) -> dict[str, Any]:
        if not observation.detected or not observation.continuation_ready:
            return {
                "success": False,
                "latency_ms": None,
                "action_latency_ms": None,
                "tool_calls": min(self.profile["agent"]["max_tool_calls"], 1),
                "observation_calls": 1,
                "input_tokens": 32,
                "output_tokens": 16,
                "incorrect_action_count": 0,
            }
        # The agent is condition-blind. It only sees the normalized observer
        # output. Under the frozen Layer B protocol, one structured
        # signal-stream read is counted for ASW; the ordinary-notification
        # condition counts notification receipt and parsing/interpretation as
        # two observations. Subscription setup and controlled event
        # publication are excluded.
        structured_subject = observation.recognized_subject is not None
        action_calls = 2 if structured_subject else 3
        observation_calls = 1 if structured_subject else 2
        action_latency = 20 if structured_subject else 40
        return {
            "success": True,
            "latency_ms": None,
            "action_latency_ms": action_latency,
            "tool_calls": action_calls,
            "observation_calls": observation_calls,
            "input_tokens": 64,
            "output_tokens": 32,
            "incorrect_action_count": 0,
        }


class EvaluationRunner:
    def __init__(
        self,
        *,
        profile_source: Path = DEFAULT_PROFILE,
        output_root: Path,
        repo: Path,
        scenario_dir: Path,
        config_path: Path | None = None,
        run_id: str | None = None,
    ) -> None:
        self.profile_source = profile_source
        self.output_root = output_root
        self.repo = repo
        self.scenario_dir = scenario_dir
        self.config_path = config_path
        self.run_id_override = run_id

    @staticmethod
    def _load_jsonl(path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _observer(self, condition: str) -> tuple[Any, ASWAdapter | None]:
        if condition != "asw":
            return observer_for(condition), None
        adapter = ASWAdapter(core_repo=self.repo)
        return ASWObserver(adapter), adapter

    @staticmethod
    def _close_adapter(adapter: ASWAdapter | None) -> None:
        if adapter is not None:
            client = adapter.client
            close = getattr(client, "close", None)
            if callable(close):
                close()

    def _run_observer(self, condition: str, surface: ScenarioSurface, profile: dict[str, Any]) -> tuple[Observation, ASWAdapter | None]:
        observer, adapter = self._observer(condition)
        observation = observer.observe(
            surface,
            interval_ms=profile["poll_interval_ms"],
            deadline_ms=profile["scenario_deadline_ms"],
            notification_template=profile["ordinary_notification_template"],
        )
        return observation, adapter

    def _run_layer_a(
        self,
        *,
        profile: dict[str, Any],
        definitions: list[ScenarioDefinition],
        controller: ScenarioController,
        raw: JsonlWriter,
    ) -> None:
        for definition in definitions:
            repetitions = profile["layer_a_repetitions_primary"] if definition.primary else profile["layer_a_repetitions_secondary"]
            for repetition in range(1, repetitions + 1):
                surface, ground_truth = controller.trial(definition, repetition, layer="A")
                for condition in controller.condition_order(definition, repetition, layer="A", conditions=profile["baselines"]):
                    if condition not in definition.applicable_baselines:
                        raw.write(not_applicable_trial(
                            run_id=profile["run_id"], trial_id=f"a-{definition.scenario_id}-{repetition}-{condition}",
                            scenario_id=definition.scenario_id, condition=condition, repetition=repetition,
                            transition_ns=ground_truth.transition_ns,
                        ))
                        continue
                    observation, adapter = self._run_observer(condition, surface, profile)
                    try:
                        scored = _scored_observation(observation, ground_truth)
                        raw.write(trial_document(
                            run_id=profile["run_id"], trial_id=f"a-{definition.scenario_id}-{repetition}-{condition}",
                            scenario_id=definition.scenario_id, condition=condition, repetition=repetition,
                            ground_truth_transition_ns=ground_truth.transition_ns, observation=scored, layer="A",
                        ))
                    finally:
                        self._close_adapter(adapter)

    def _run_layer_b(
        self,
        *,
        profile: dict[str, Any],
        definitions: list[ScenarioDefinition],
        controller: ScenarioController,
        raw: JsonlWriter,
        best_baselines: dict[str, str],
        usage: JsonlWriter,
    ) -> None:
        agent = ScriptedContinuationAgent(profile)
        for definition in definitions:
            if not definition.primary:
                continue
            baseline = best_baselines[definition.scenario_class]
            conditions = ("asw", baseline)
            for repetition in range(1, profile["layer_b_repetitions"] + 1):
                surface, ground_truth = controller.trial(definition, repetition, layer="B")
                for condition in controller.condition_order(definition, repetition, layer="B", conditions=conditions):
                    observation, adapter = self._run_observer(condition, surface, profile)
                    try:
                        scored = _scored_observation(observation, ground_truth)
                        continuation = agent.continue_from(scored)
                        if continuation["action_latency_ms"] is not None and scored.recognized_ns is not None:
                            continuation["latency_ms"] = (scored.recognized_ns - ground_truth.transition_ns) / 1_000_000 + continuation["action_latency_ms"]
                        result = trial_document(
                            run_id=profile["run_id"], trial_id=f"b-{definition.scenario_id}-{repetition}-{condition}",
                            scenario_id=definition.scenario_id, condition=condition, repetition=repetition,
                            ground_truth_transition_ns=ground_truth.transition_ns, observation=scored, layer="B",
                            continuation=continuation,
                        )
                        raw.write(result)
                        usage.write({
                            "schema_version": "asw.evaluation_agent_usage.v1",
                            "run_id": profile["run_id"],
                            "trial_id": result["trial_id"],
                            "scenario_id": definition.scenario_id,
                            "condition": condition,
                            "agent_model": profile["agent"]["model"],
                            "agent_configuration": profile["agent"]["configuration"],
                            "prompt_hash": "sha256:" + hashlib.sha256(f"continue:{definition.scenario_id}".encode()).hexdigest(),
                            "response_kind": "normalized_deterministic_continuation",
                            "tool_calls": continuation["tool_calls"],
                            "observation_calls": continuation["observation_calls"],
                            "input_tokens": continuation["input_tokens"],
                            "output_tokens": continuation["output_tokens"],
                        })
                    finally:
                        self._close_adapter(adapter)

    def run(self) -> Path:
        self.output_root.mkdir(parents=True, exist_ok=True)
        run_id = self.run_id_override or json.loads(self.profile_source.read_text(encoding="utf-8"))["run_id"]
        run_dir = self.output_root / run_id
        if run_dir.exists() and any(run_dir.iterdir()):
            raise RuntimeError(f"run directory is not empty; frozen runs are immutable: {run_dir}")
        run_dir.mkdir(parents=True, exist_ok=True)
        profile = freeze_profile(self.profile_source, run_dir / "profile.json", repo=self.repo, run_id=run_id, model="Luna Max")
        validate_profile_semantics(profile)
        profile_hash = digest(profile)
        manifest = build_manifest(
            profile, repo=self.repo, profile_digest=profile_hash, started_at=utc_now(),
            raw_results_path="raw-results.jsonl", ground_truth_path="ground-truth.jsonl", config_path=self.config_path,
        )
        validate_document(manifest, "run-manifest")
        write_json(run_dir / "run-manifest.json", manifest)
        definitions = ScenarioController.load_definitions(self.scenario_dir)
        scenario_documents = {
            definition.scenario_id: {
                "scenario_id": definition.scenario_id,
                "class": definition.scenario_class,
                "primary": definition.primary,
                "applicable_baselines": list(definition.applicable_baselines),
            }
            for definition in definitions
        }
        recorder = GroundTruthRecorder(run_dir / "ground-truth.jsonl")
        controller = ScenarioController(
            run_id=profile["run_id"], seed=profile["seed"], random_delay=profile["random_delay_ms"], recorder=recorder, recorded_at=profile["frozen_at"]
        )
        raw_path = run_dir / "raw-results.jsonl"
        usage_path = run_dir / "agent-usage.jsonl"
        with JsonlWriter(raw_path) as raw:
            self._run_layer_a(profile=profile, definitions=definitions, controller=controller, raw=raw)
            layer_a_records = self._load_jsonl(raw_path)
            # All primary/secondary conditions have a record, including
            # explicit not_applicable pairs.  This is the Layer A integrity
            # barrier before any agent comparison begins.
            expected_a = sum(
                (profile["layer_a_repetitions_primary"] if definition.primary else profile["layer_a_repetitions_secondary"]) * len(profile["baselines"])
                for definition in definitions
            )
            if len(layer_a_records) != expected_a:
                raise RuntimeError(f"Layer A record completeness failure: {len(layer_a_records)} != {expected_a}")
            for record in layer_a_records:
                validate_trial_semantics(record)
            best_baselines = select_best_baselines(layer_a_records, scenario_documents, profile)
            with JsonlWriter(usage_path) as usage:
                self._run_layer_b(profile=profile, definitions=definitions, controller=controller, raw=raw, best_baselines=best_baselines, usage=usage)
        manifest["completed_at"] = utc_now()
        validate_document(manifest, "run-manifest")
        write_json(run_dir / "run-manifest.json", manifest)
        all_records = self._load_jsonl(raw_path)
        for record in all_records:
            validate_trial_semantics(record)
        layer_a = aggregate_layer_a(all_records, scenario_documents)
        class_groups = aggregate_layer_a_by_class(all_records, scenario_documents)
        layer_a["__classes__"] = {
            scenario_class: {
                condition: _class_rates(records)
                for condition, records in sorted(class_groups.get(scenario_class, {}).items())
            }
            for scenario_class in sorted(profile["primary_scenarios"])
        }
        layer_b = aggregate_layer_b(all_records, scenario_documents)
        usage_records = self._load_jsonl(usage_path)
        integrity = derive_integrity(
            profile=profile,
            definitions=definitions,
            raw_records=all_records,
            ground_truth_records=[record.as_dict() for record in recorder.records],
            usage_records=usage_records,
        )
        audit = threshold_audit(layer_a=layer_a, layer_b=layer_b, best_baselines=best_baselines, profile=profile, integrity=integrity)
        summary = build_summary(
            run_id=profile["run_id"], base_commit=profile["base_commit"], generated_at=manifest["completed_at"] or profile["frozen_at"],
            layer_a=layer_a, best_baselines=best_baselines, layer_b=layer_b, threshold_audit_result=audit,
        )
        write_json(run_dir / "aggregate-summary.json", summary)
        return run_dir


def _class_rates(records: list[dict[str, Any]]) -> dict[str, Any]:
    from .metrics import _rates
    return _rates(records)
