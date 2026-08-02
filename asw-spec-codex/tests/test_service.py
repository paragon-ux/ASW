from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from asw.service import ASWService

ROOT = Path(__file__).resolve().parents[1]


def fixture(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / "valid" / name).read_text(encoding="utf-8"))


class ServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.policy = fixture("reducer-policy.json")
        self.service = ASWService(Path(self.temp.name) / "journal.jsonl", self.policy)
        self.authorization = fixture("observation-authorization.json")
        self.authorization["scopes"][0]["source_id"] = "fs:vs"
        self.authorization["scopes"] = self.authorization["scopes"][:1]
        self.service.record("observation_authorization", self.authorization)
        source = fixture("source-registration.filesystem.json")
        source["source_id"] = "fs:vs"
        self.service.record("source_registration", source)

    def tearDown(self) -> None: self.temp.cleanup()

    def event(self) -> dict:
        event = fixture("event.file-saved.json")
        event["source"]["adapter"] = "filesystem"
        event["source"]["source_id"] = "fs:vs"
        return event

    def test_journal_replay_and_rebuild_preserve_signals(self) -> None:
        self.service.emit_event(self.event())
        original = list(self.service.signals)
        restarted = ASWService(self.service.journal.path, self.policy)
        self.assertEqual(original, restarted.signals)
        self.assertEqual(restarted.journal.sequence, 3)

    def test_replay_cursor_can_resume_after_service_restart(self) -> None:
        self.service.emit_event(self.event())
        self.service.record("agent_access", fixture("agent-access.json"))
        subscription = fixture("subscription.agent.json")
        self.service.register_subscription(subscription)
        cursor = self.service.agent_signals("agent:codex-1", subscription["subscription_id"])["replay_cursor"]
        external = Path(self.temp.name) / "external-state.txt"
        external.write_text("must not be touched", encoding="utf-8")
        restarted = ASWService(self.service.journal.path, self.policy)
        resumed = restarted.agent_signals("agent:codex-1", subscription["subscription_id"], after=cursor)
        self.assertEqual(resumed["signals"], [])
        self.assertNotEqual(cursor["frontier"]["runtime_epoch"], resumed["replay_cursor"]["frontier"]["runtime_epoch"])
        self.assertEqual(external.read_text(encoding="utf-8"), "must not be touched")

    def test_policy_versions_are_durable_inputs_for_replay(self) -> None:
        newer = fixture("reducer-policy.json")
        newer["policy_version"] = "asw.reducer.v2"
        newer["rules"][0]["rule_id"] = "rule_file_saved_v2"
        self.service.record_policy_change(newer)
        event = self.event()
        event["event_id"] = "evt_v2"
        event["frontier"]["reducer_policy_version"] = "asw.reducer.v2"
        self.service.emit_event(event)
        restarted = ASWService(self.service.journal.path, newer)
        self.assertEqual(self.service.signals, restarted.signals)

    def test_source_health_requires_registered_source_and_reconciliation_evidence(self) -> None:
        source = fixture("source-registration.filesystem.json")
        source["source_id"] = "fs:vs"
        self.service.record("source_registration", source)
        adapter_event = self.event()
        adapter_event["type"] = "source.degraded"
        adapter_event["event_id"] = "evt_degraded"
        adapter_event["source"]["source_id"] = "fs:vs"
        self.service.emit_event(adapter_event)
        self.assertEqual(self.service.source_health["fs:vs"], "degraded")
        bad = dict(adapter_event); bad["type"] = "source.reconciled"; bad["event_id"] = "evt_reconciled_bad"; bad["payload"] = {}; bad["frontier"] = dict(adapter_event["frontier"]); bad["frontier"]["source_frontiers"] = {"app:vs": {"source_epoch": "source-1", "source_sequence": 3}}
        self.service.emit_event(bad)
        self.assertEqual(self.service.source_health["fs:vs"], "degraded")
        good = dict(bad); good["event_id"] = "evt_reconciled_good"; good["payload"] = {"snapshot_digest": "sha256:reconciled"}
        self.service.emit_event(good)
        self.assertEqual(self.service.source_health["fs:vs"], "healthy")

    def test_subscription_does_not_create_or_remove_signal_history(self) -> None:
        self.service.emit_event(self.event()); before = list(self.service.signals)
        sub = fixture("subscription.user.json")
        self.service.register_subscription(sub)
        self.assertEqual(before, self.service.signals)

    def test_agent_grant_and_revocation_are_enforced(self) -> None:
        self.service.emit_event(self.event())
        self.service.record("agent_access", fixture("agent-access.json"))
        sub = fixture("subscription.agent.json"); self.service.register_subscription(sub)
        response = self.service.agent_signals("agent:codex-1", sub["subscription_id"])
        self.assertEqual(len(response["signals"]), 1)
        self.assertTrue(response["replay_cursor"]["cursor_id"].startswith("cursor_"))
        self.assertEqual(self.service.agent_signals("agent:codex-1", sub["subscription_id"], after=response["replay_cursor"])["signals"], [])
        revoked = fixture("agent-access.json"); revoked["enabled"] = False
        self.service.record("agent_access", revoked)
        with self.assertRaises(PermissionError): self.service.agent_signals("agent:codex-1", sub["subscription_id"])

    def test_agent_subscription_cannot_exceed_grant(self) -> None:
        self.service.record("agent_access", fixture("agent-access.json"))
        sub = fixture("subscription.agent.json"); sub["applications"] = ["app.outside"]
        with self.assertRaises(PermissionError): self.service.register_subscription(sub)

    def test_source_registration_cannot_exceed_authorization(self) -> None:
        source = fixture("source-registration.filesystem.json")
        source["source_id"] = "fs:vs"
        source["configuration"]["roots"] = ["C:\\secret"]
        with self.assertRaises(PermissionError): self.service.record("source_registration", source)

    def test_unregistered_or_mismatched_source_events_fail_closed(self) -> None:
        event = self.event()
        event["source"]["source_id"] = "fs:unregistered"
        self.service.emit_event(event)
        self.assertEqual(self.service.signals, [])

    def test_filesystem_event_path_outside_registered_root_fails_closed(self) -> None:
        event = self.event()
        event["subject"]["value"]["path"] = "C:\\secret\\x.txt"
        self.service.emit_event(event)
        self.assertEqual(self.service.signals, [])

    def test_expired_grant_cannot_create_subscription_or_read(self) -> None:
        grant = fixture("agent-access.json")
        grant["expires_at"] = "2020-01-01T00:00:00Z"
        self.service.record("agent_access", grant)
        with self.assertRaises(PermissionError): self.service.register_subscription(fixture("subscription.agent.json"))

    def test_disabled_subscription_cannot_read(self) -> None:
        self.service.emit_event(self.event())
        self.service.record("agent_access", fixture("agent-access.json"))
        sub = fixture("subscription.agent.json")
        self.service.register_subscription(sub)
        disabled = dict(sub); disabled["enabled"] = False
        self.service.register_subscription(disabled)
        with self.assertRaises(PermissionError): self.service.agent_signals("agent:codex-1", sub["subscription_id"])

    def test_administrative_grant_outside_authorization_cannot_read(self) -> None:
        grant = fixture("agent-access.json")
        grant["applications"] = ["app.outside"]
        self.service.record("agent_access", grant)
        sub = fixture("subscription.agent.json")
        sub["applications"] = ["app.outside"]
        with self.assertRaises(PermissionError): self.service.register_subscription(sub)

    def test_delivery_failure_is_audit_only_and_keeps_signal(self) -> None:
        self.service.emit_event(self.event()); signal = self.service.signals[0]
        sub = fixture("subscription.user.json")
        sub["categories"] = ["files"]
        sub["event_types"] = ["file.saved"]
        self.service.register_subscription(sub)
        self.service.deliver(signal, sub, False, "toast unavailable")
        self.assertEqual(self.service.signals[0], signal)
        self.assertEqual(self.service.deliveries[-1]["status"], "failed")


if __name__ == "__main__": unittest.main()
