from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EvaluationFixtureTests(unittest.TestCase):
    def test_predeclared_profile_and_scenario_coverage(self) -> None:
        profile = json.loads((ROOT / "fixtures" / "evaluation" / "profile.json").read_text(encoding="utf-8"))
        expected_baselines = {
            "polling",
            "filesystem_watch_only",
            "ordinary_windows_notification",
            "repeated_visual_observation",
            "asw_signals",
        }
        expected_classes = {"build_test", "file_artifact", "dialog_control", "render_export", "process_crash_restart"}
        self.assertEqual(profile["schema_version"], "asw.evaluation_profile.v1")
        self.assertEqual(set(profile["baselines"]), expected_baselines)
        self.assertEqual(set(profile["scenario_classes"]), expected_classes)
        self.assertIsInstance(profile["repetitions"], int)
        self.assertGreater(profile["repetitions"], 0)
        self.assertIn("missed_signal_rate_max", profile["thresholds"])
        self.assertIn("duplicate_signal_rate_max", profile["thresholds"])

        scenarios = [
            json.loads(line)
            for line in (ROOT / "fixtures" / "evaluation" / "scenarios.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(len({scenario["id"] for scenario in scenarios}), len(scenarios))
        self.assertEqual(
            {scenario["transition"] for scenario in scenarios},
            {"job.completed", "file.saved", "dialog.appeared", "process.crashed"},
        )
        self.assertEqual(
            {scenario["expected_category"] for scenario in scenarios},
            {"jobs", "files", "windows_ui", "processes"},
        )


if __name__ == "__main__": unittest.main()
