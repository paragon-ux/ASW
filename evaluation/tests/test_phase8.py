from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from evaluation import run as evaluation_run
from evaluation.baselines.observers import PollingObserver, RepeatedObservationObserver
from evaluation.consumers.asw_adapter import ASWAdapter
from evaluation.metrics import aggregate_layer_b, derive_integrity, select_best_baselines, threshold_audit
from evaluation.profile import DEFAULT_PROFILE, core_worktree_status
from evaluation.scenarios.controller import GroundTruthRecorder, ScenarioController
from evaluation.schema import validate_fixture_tree


ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = ROOT / "evaluation" / "scenarios"


class Phase8ContractTests(unittest.TestCase):
    def test_evaluation_defaults_use_the_canonical_repository_root(self) -> None:
        args = evaluation_run.build_parser().parse_args([])
        self.assertEqual(args.repo, ROOT)
        adapter = ASWAdapter()
        try:
            self.assertEqual(adapter.client.core_repo, ROOT)
        finally:
            adapter.client.close()

    def test_manifest_status_does_not_filter_the_canonical_evaluation_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repository = Path(temp)
            subprocess.run(["git", "init", "--quiet", str(repository)], check=True)
            (repository / "untracked.txt").write_text("fixture\n", encoding="utf-8")
            status = core_worktree_status(repository)
            self.assertEqual(status["core_status"], status["full_status"])
            self.assertEqual(status["extension_status_excluded"], [])

    def test_all_extension_fixtures_and_scenarios_validate(self) -> None:
        valid, invalid = validate_fixture_tree()
        self.assertGreaterEqual(len(valid), 13)
        self.assertEqual(len(invalid), 5)

    def test_ground_truth_is_independent_from_observer_surface(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            recorder = GroundTruthRecorder(Path(temp) / "ground-truth.jsonl")
            profile = json.loads(DEFAULT_PROFILE.read_text(encoding="utf-8"))
            definition = ScenarioController.load_definitions(SCENARIO_DIR)[0]
            controller = ScenarioController(
                run_id="test-run",
                seed=profile["seed"],
                random_delay=profile["random_delay_ms"],
                recorder=recorder,
                recorded_at=profile["frozen_at"],
            )
            surface, truth = controller.trial(definition, 1, layer="A")
            self.assertFalse(hasattr(surface, "ground_truth"))
            self.assertFalse(hasattr(surface, "transition_ns"))
            observation = PollingObserver().observe(
                surface,
                interval_ms=250,
                deadline_ms=15000,
                notification_template=profile["ordinary_notification_template"],
            )
            self.assertTrue(observation.detected)
            self.assertEqual(len(recorder.records), 1)
            self.assertEqual(recorder.records[0].trial_id, truth.trial_id)

    def test_repeated_observation_uses_the_frozen_interval(self) -> None:
        profile = json.loads(DEFAULT_PROFILE.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temp:
            recorder = GroundTruthRecorder(Path(temp) / "gt.jsonl")
            definition = ScenarioController.load_definitions(SCENARIO_DIR)[0]
            controller = ScenarioController(
                run_id="test-run",
                seed=profile["seed"],
                random_delay=profile["random_delay_ms"],
                recorder=recorder,
                recorded_at=profile["frozen_at"],
            )
            surface, _ = controller.trial(definition, 1, layer="A")
            polling = PollingObserver().observe(
                surface,
                interval_ms=250,
                deadline_ms=15000,
                notification_template=profile["ordinary_notification_template"],
            )
            repeated = RepeatedObservationObserver().observe(
                surface,
                interval_ms=250,
                deadline_ms=15000,
                notification_template=profile["ordinary_notification_template"],
            )
            self.assertEqual(polling.observation_count, repeated.observation_count)

    def test_best_baseline_selection_prefers_high_detection_then_lexical_tie_break(self) -> None:
        profile = json.loads(DEFAULT_PROFILE.read_text(encoding="utf-8"))
        scenarios = {
            "job": {"class": "job_completion", "primary": True},
            "file": {"class": "file_artifact_transition", "primary": True},
            "ui": {"class": "ui_transition", "primary": True},
        }

        def record(scenario_id: str, condition: str) -> dict:
            return {
                "trial_id": f"a-{scenario_id}-{condition}",
                "scenario_id": scenario_id,
                "condition": condition,
                "status": "completed",
                "detected": True,
                "missed": False,
                "duplicate_count": 0,
                "false_positive_count": 0,
                "application_attribution_correct": True,
                "kind_correct": True,
                "subject_correct": True,
                "localization_correct": None,
                "continuation_ready": True,
                "observation_count": 2,
                "detection_latency_ms": 10,
                "recognized_ns": 10,
                "ground_truth_transition_ns": 0,
            }

        records = [record(scenario_id, condition) for scenario_id in scenarios for condition in ("polling", "ordinary_notification")]
        selection = select_best_baselines(records, scenarios, profile)
        self.assertEqual(selection["job_completion"], "ordinary_notification")

    def test_threshold_boundary_values_pass(self) -> None:
        profile = json.loads(DEFAULT_PROFILE.read_text(encoding="utf-8"))
        asw = {
            "detected": 0.98,
            "missed": 0.02,
            "duplicate_rate": 0.02,
            "false_positive_rate": 0.02,
            "application_attribution_accuracy": 0.98,
            "kind_accuracy": 0.98,
            "median_observation_count": 7.0,
            "median_detection_latency_ms": 10.0,
        }
        baseline = {**asw, "detected": 1.0, "missed": 0.0, "median_observation_count": 10.0}
        layer_a = {
            "job_completion": {"asw": asw, "ordinary_notification": baseline},
            "file_artifact_transition": {"asw": asw, "ordinary_notification": baseline},
            "ui_transition": {"asw": asw, "ordinary_notification": baseline},
            "__classes__": {
                "job_completion": {"asw": asw, "ordinary_notification": baseline},
                "file_artifact_transition": {"asw": asw, "ordinary_notification": baseline},
                "ui_transition": {"asw": asw, "ordinary_notification": baseline},
            },
        }
        layer_b = {
            name: {
                "asw": {
                    "continuation_success": 0.95,
                    "median_agent_observation_calls": 8.0,
                    "median_continuation_latency_ms": 80.0,
                },
                "ordinary_notification": {
                    "continuation_success": 1.0,
                    "median_agent_observation_calls": 10.0,
                    "median_continuation_latency_ms": 100.0,
                },
            }
            for name in profile["primary_scenarios"]
        }
        layer_b["__combined__"] = {
            "asw": {
                "continuation_success": 0.95,
                "median_agent_observation_calls": 8.0,
                "median_continuation_latency_ms": 80.0,
            },
            "ordinary_notification": {
                "continuation_success": 1.0,
                "median_agent_observation_calls": 10.0,
                "median_continuation_latency_ms": 100.0,
            },
        }
        audit = threshold_audit(
            layer_a=layer_a,
            layer_b=layer_b,
            best_baselines={name: "ordinary_notification" for name in profile["primary_scenarios"]},
            profile=profile,
            integrity={
                "authorization_violations": 0,
                "replay_violations": 0,
                "raw_trial_completeness_pass": True,
                "raw_trial_schema_errors": 0,
                "ground_truth_completeness_pass": True,
                "no_ground_truth_channel_exposed": True,
                "layer_a_model_calls": 0,
                "agent_usage_completeness_pass": True,
                "deterministic_aggregation_pass": True,
                "core_defect_discovered": False,
            },
        )
        self.assertTrue(audit["correctness"]["pass"])
        self.assertTrue(audit["layer_a_efficiency"]["pass"])
        self.assertTrue(audit["layer_b_continuation"]["success_pass"])

    def test_layer_b_combined_median_is_pooled_across_primary_records(self) -> None:
        scenarios = {
            "job": {"class": "job_completion"},
            "file": {"class": "file_artifact_transition"},
            "ui": {"class": "ui_transition"},
        }

        def record(scenario_id: str, condition: str, observation_calls: int, index: int) -> dict:
            return {
                "trial_id": f"b-{scenario_id}-{index}-{condition}",
                "scenario_id": scenario_id,
                "condition": condition,
                "status": "completed",
                "continuation_success": True,
                "agent_tool_calls": 1,
                "agent_observation_calls": observation_calls,
                "continuation_latency_ms": float(observation_calls),
                "input_tokens": 1,
                "output_tokens": 1,
                "incorrect_action_count": 0,
            }

        records = []
        class_values = {
            "job": [0, 0, 0, 0, 0, 0],
            "file": [0, 0, 0, 1, 1, 1],
            "ui": [0, 0, 0, 1, 1, 1],
        }
        for scenario_id, values in class_values.items():
            records.extend(record(scenario_id, "asw", value, index) for index, value in enumerate(values, 1))
        combined = aggregate_layer_b(records, scenarios)["__combined__"]["asw"]
        self.assertEqual(combined["median_agent_observation_calls"], 0.0)

    def test_integrity_derivation_fails_closed_on_agent_ground_truth_contamination(self) -> None:
        profile = json.loads(DEFAULT_PROFILE.read_text(encoding="utf-8"))
        definitions = ScenarioController.load_definitions(SCENARIO_DIR)
        integrity = derive_integrity(
            profile=profile,
            definitions=definitions,
            raw_records=[],
            ground_truth_records=[],
            usage_records=[{"trial_id": "b-one", "ground_truth_transition_ns": 1}],
        )
        self.assertFalse(integrity["no_ground_truth_channel_exposed"])
        audit = threshold_audit(
            layer_a={"__classes__": {}, "job_completion": {}},
            layer_b={},
            best_baselines={},
            profile=profile,
            integrity={},
        )
        self.assertFalse(audit["correctness"]["access_pass"])
        self.assertFalse(audit["pass"])


if __name__ == "__main__":
    unittest.main()
