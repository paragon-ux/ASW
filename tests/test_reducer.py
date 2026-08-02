from __future__ import annotations

import json
import unittest
from pathlib import Path

from asw.application import UNKNOWN_APPLICATION_ID, application_group
from asw.contracts import ContractError
from asw.reducer import Reducer

ROOT = Path(__file__).resolve().parents[1]


def fixture(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / "valid" / name).read_text(encoding="utf-8"))


class ReducerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.reducer = Reducer(fixture("reducer-policy.json"))
        self.event = fixture("event.file-saved.json")

    def test_authorized_event_has_reproducible_signal(self) -> None:
        first = self.reducer.reduce(self.event, is_authorized=lambda _: True)
        second = self.reducer.reduce(self.event, is_authorized=lambda _: True)
        self.assertIsNotNone(first.signal)
        self.assertEqual(first.signal, second.signal)
        self.assertEqual(first.signal["kind"], "file.saved")

    def test_unreliable_and_unauthorized_events_fail_closed(self) -> None:
        hint = json.loads(json.dumps(self.event))
        hint["source"]["reliability"] = "hint"
        self.assertIsNone(self.reducer.reduce(hint, is_authorized=lambda _: True).signal)
        self.assertIsNone(self.reducer.reduce(self.event, is_authorized=lambda _: False).signal)

    def test_invalid_unattributed_event_fails_closed(self) -> None:
        invalid = json.loads(json.dumps(self.event))
        invalid["application_id"] = ""
        self.assertIsNone(self.reducer.reduce(invalid, is_authorized=lambda _: True).signal)

    def test_duplicate_event_does_not_create_second_signal(self) -> None:
        first = self.reducer.reduce(self.event, is_authorized=lambda _: True)
        duplicate = self.reducer.reduce(self.event, is_authorized=lambda _: True, prior_signals=[first.signal])
        self.assertIsNone(duplicate.signal)

    def test_distinct_events_with_same_policy_dedupe_key_do_not_duplicate_history(self) -> None:
        first = self.reducer.reduce(self.event, is_authorized=lambda _: True)
        duplicate_event = json.loads(json.dumps(self.event))
        duplicate_event["event_id"] = "evt_save_2"
        duplicate_event["source"]["source_sequence"] = 4
        duplicate = self.reducer.reduce(duplicate_event, is_authorized=lambda _: True, prior_signals=[first.signal])
        self.assertIsNone(duplicate.signal)

    def test_frontier_policy_mismatch_fails_closed(self) -> None:
        mismatched = json.loads(json.dumps(self.event))
        mismatched["frontier"]["reducer_policy_version"] = "asw.reducer.v2"
        self.assertIsNone(self.reducer.reduce(mismatched, is_authorized=lambda _: True).signal)

    def test_generator_prior_state_keeps_supersession_information(self) -> None:
        first_event = json.loads(json.dumps(self.event))
        first_event["event_id"] = "evt_save_old"
        first_event["source"]["source_sequence"] = 1
        first = self.reducer.reduce(first_event, is_authorized=lambda _: True)
        changed_policy = fixture("reducer-policy.json")
        changed_policy["policy_version"] = "asw.reducer.v2"
        changed_policy["rules"][0]["emit"]["dedupe_key_fields"] = ["application_id", "source.source_id"]
        reducer = Reducer(changed_policy)
        later_event = json.loads(json.dumps(self.event))
        later_event["event_id"] = "evt_save_new"
        later_event["source"]["source_id"] = "app:other"
        later_event["frontier"]["reducer_policy_version"] = "asw.reducer.v2"
        later = reducer.reduce(later_event, is_authorized=lambda _: True, prior_signals=(item for item in [first.signal]))
        self.assertEqual(later.superseded_signal_ids, (first.signal["signal_id"],))

    def test_invalid_emitting_policy_is_rejected(self) -> None:
        invalid_policy = fixture("reducer-policy.json")
        invalid_policy["rules"][0]["emit"] = None
        with self.assertRaises(ContractError):
            Reducer(invalid_policy)

    def test_policy_is_immutable_after_reducer_construction(self) -> None:
        policy = fixture("reducer-policy.json")
        reducer = Reducer(policy)
        policy["rules"][0]["action"] = "reject"
        self.assertIsNotNone(reducer.reduce(self.event, is_authorized=lambda _: True).signal)

    def test_long_subject_summary_is_bounded(self) -> None:
        long_subject = json.loads(json.dumps(self.event))
        long_subject["subject"]["value"]["path"] = "C:\\" + "x" * 3000
        signal = self.reducer.reduce(long_subject, is_authorized=lambda _: True).signal
        self.assertIsNotNone(signal)
        self.assertLessEqual(len(signal["summary"]), 2048)

    def test_subscriptions_are_not_reducer_inputs(self) -> None:
        self.assertNotIn("subscription", self.reducer.reduce.__annotations__)

    def test_unattributed_events_have_required_unknown_group(self) -> None:
        self.assertEqual(application_group(None), UNKNOWN_APPLICATION_ID)
        self.assertEqual(application_group(""), UNKNOWN_APPLICATION_ID)


if __name__ == "__main__":
    unittest.main()
