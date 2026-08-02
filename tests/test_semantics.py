from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from asw.agent_api import AgentAPI
from asw.contracts import ContractError
from asw.defaults import mvp_policy
from asw.service import ASWService
from asw.sources import SourceAdapter

ROOT = Path(__file__).resolve().parents[1]


def fixture(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / "valid" / name).read_text(encoding="utf-8"))


class SemanticFailClosedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.policy = mvp_policy()
        self.service = ASWService(Path(self.temp.name) / "journal.jsonl", self.policy)
        auth = fixture("observation-authorization.json")
        auth["scopes"] = [auth["scopes"][0]]
        auth["scopes"][0]["source_id"] = "fs:semantic"
        auth["scopes"][0]["filesystem_roots"] = ["C:\\workspace"]
        self.service.record("observation_authorization", auth)
        source = fixture("source-registration.filesystem.json")
        source["source_id"] = "fs:semantic"
        source["configuration"]["roots"] = ["C:\\workspace"]
        self.service.record("source_registration", source)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def event(self, event_id: str = "evt_semantic", path: str = "C:\\workspace\\main.txt") -> dict:
        event = fixture("event.file-saved.json")
        event["event_id"] = event_id
        event["source"]["adapter"] = "filesystem"
        event["source"]["source_id"] = "fs:semantic"
        event["subject"]["value"]["path"] = path
        return event

    def grant_and_subscription(self) -> dict:
        self.service.record("agent_access", fixture("agent-access.json"))
        subscription = fixture("subscription.agent.json")
        self.service.register_subscription(subscription)
        return subscription

    def test_agent_subscription_exceeding_grant_is_rejected(self) -> None:
        self.service.record("agent_access", fixture("agent-access.json"))
        subscription = fixture("subscription.agent.json")
        subscription["categories"] = ["processes"]
        with self.assertRaises(PermissionError): self.service.register_subscription(subscription)

    def test_constructor_only_policy_cannot_authorize_replay(self) -> None:
        newer = mvp_policy()
        newer["policy_version"] = "asw.reducer.v2"
        event = self.event("evt_unjournaled_policy")
        event["frontier"] = dict(event["frontier"])
        event["frontier"]["reducer_policy_version"] = "asw.reducer.v2"
        restarted = ASWService(self.service.journal.path, newer)
        restarted.emit_event(event)
        self.assertEqual(restarted.signals, [])

    def test_raw_process_event_cannot_claim_unregistered_executable(self) -> None:
        expanded = fixture("observation-authorization.json")
        expanded["scopes"] = [expanded["scopes"][0], {
            "application_id": "app.visual-studio", "source_id": "proc:semantic", "source_kind": "process_job",
            "filesystem_roots": [], "executable_names": ["allowed.exe"], "job_kinds": [], "uia_process_names": [], "adapter_contract": None,
        }]
        expanded["scopes"][0]["source_id"] = "fs:semantic"
        expanded["scopes"][0]["filesystem_roots"] = ["C:\\workspace"]
        self.service.record("observation_authorization", expanded)
        self.service.record("source_registration", {
            "schema_version": "asw.source_registration.v1", "source_id": "proc:semantic", "adapter": "process",
            "application_id": "app.visual-studio", "enabled": True, "authorization_id": "auth_vs",
            "configuration": {"executable_names": ["allowed.exe"]}, "settle_profile": None, "registered_at": "2026-08-01T12:10:00-04:00",
        })
        event = self.event("evt_evil_process")
        event["type"] = "process.started"
        event["source"] = dict(event["source"]); event["source"]["adapter"] = "process"; event["source"]["source_id"] = "proc:semantic"
        event["subject"] = {"kind": "process", "value": {"id": "p1"}}
        event["payload"] = {"executable_name": "evil.exe"}
        self.service.emit_event(event)
        self.assertFalse(self.service.signals)

    def test_administrative_grant_cannot_read_outside_authorization(self) -> None:
        grant = fixture("agent-access.json")
        grant["applications"] = ["app.outside"]
        self.service.record("agent_access", grant)
        self.assertIsNotNone(self.service.get_agent_grant("agent:codex-1"))
        self.assertFalse(self.service.application_authorized("app.outside"))

    def test_stream_request_owned_by_another_subscriber_is_rejected(self) -> None:
        self.grant_and_subscription()
        request = fixture("agent-stream-request.json")
        request["after"] = None
        request["subscription_ids"] = ["sub_other"]
        with self.assertRaises(PermissionError): AgentAPI(self.service, "agent:codex-1").handle("open_signal_stream", request)

    def test_windows_delivery_is_user_only(self) -> None:
        user = fixture("subscription.user.json")
        self.service.register_subscription(user)
        agent = self.grant_and_subscription()
        self.assertIn("windows_app_sdk", user["destinations"])
        self.assertNotIn("windows_app_sdk", agent["destinations"])
        invalid_agent = dict(agent)
        invalid_agent["destinations"] = ["windows_app_sdk"]
        with self.assertRaises(ContractError): self.service.register_subscription(invalid_agent)

    def test_subscription_presence_does_not_change_signal_history(self) -> None:
        self.service.emit_event(self.event())
        before = list(self.service.signals)
        self.service.register_subscription(fixture("subscription.user.json"))
        self.assertEqual(before, self.service.signals)

    def test_revoked_observation_authorization_blocks_future_signals(self) -> None:
        self.service.emit_event(self.event("evt_before"))
        revoked = fixture("observation-authorization.json")
        revoked["scopes"] = [revoked["scopes"][0]]
        revoked["scopes"][0]["source_id"] = "fs:semantic"
        revoked["scopes"][0]["filesystem_roots"] = ["C:\\workspace"]
        revoked["enabled"] = False
        self.service.record("observation_authorization", revoked)
        self.service.emit_event(self.event("evt_after", "C:\\workspace\\after.txt"))
        self.assertEqual(len(self.service.signals), 1)

    def test_revoked_agent_grant_blocks_list_stream_resume_and_read(self) -> None:
        self.service.emit_event(self.event())
        subscription = self.grant_and_subscription()
        api = AgentAPI(self.service, "agent:codex-1")
        self.assertEqual(len(api.list_signals(subscription["subscription_id"])["signals"]), 1)
        revoked = fixture("agent-access.json")
        revoked["enabled"] = False
        self.service.record("agent_access", revoked)
        for operation in (
            lambda: api.list_applications(),
            lambda: api.list_subscriptions(),
            lambda: api.list_signals(subscription["subscription_id"]),
            lambda: api.open_signal_stream(subscription["subscription_id"]),
            lambda: api.resume_signal_stream(subscription["subscription_id"], None),
            lambda: api.get_signal(subscription["subscription_id"], self.service.signals[0]["signal_id"]),
        ):
            with self.assertRaises(PermissionError): operation()

    def test_hint_and_degraded_facts_do_not_become_ordinary_signals(self) -> None:
        hint = self.event("evt_hint")
        hint["source"]["reliability"] = "hint"
        self.service.emit_event(hint)
        self.assertEqual(self.service.signals, [])
        degraded = self.event("evt_degraded")
        degraded["type"] = "source.degraded"
        degraded["subject"] = {"kind": "source", "value": {"reason": "overflow"}}
        self.service.emit_event(degraded)
        ordinary = self.event("evt_blocked", "C:\\workspace\\blocked.txt")
        self.service.emit_event(ordinary)
        self.assertFalse(any(signal["kind"] == "file.saved" for signal in self.service.signals))

    def test_artifact_settle_timeout_cannot_emit(self) -> None:
        adapter = SourceAdapter(self.service, "fs:semantic", "app.visual-studio", "filesystem")
        before = len(self.service.journal.records())
        adapter.filesystem("artifact.available", "C:\\workspace\\out.bin", observations=[(1, 1), (1, 1)], elapsed_ms=6001, artifact=True)
        self.assertEqual(before, len(self.service.journal.records()))
        self.assertFalse(self.service.signals)

    def test_degraded_source_requires_reconciliation_evidence(self) -> None:
        degraded = self.event("evt_degraded")
        degraded["type"] = "source.degraded"
        degraded["subject"] = {"kind": "source", "value": {"reason": "overflow"}}
        self.service.emit_event(degraded)
        bad = self.event("evt_reconcile_bad")
        bad["type"] = "source.reconciled"
        bad["subject"] = {"kind": "source", "value": {}}
        bad["payload"] = {}
        bad["frontier"] = dict(bad["frontier"])
        bad["frontier"]["source_frontiers"] = {"fs:semantic": {"source_epoch": "source-1", "source_sequence": 2}}
        self.service.emit_event(bad)
        self.assertEqual(self.service.source_health["fs:semantic"], "degraded")
        good = self.event("evt_reconcile_good")
        good["type"] = "source.reconciled"
        good["subject"] = {"kind": "source", "value": {}}
        good["payload"] = {"snapshot_digest": "sha256:semantic"}
        self.service.emit_event(good)
        self.assertEqual(self.service.source_health["fs:semantic"], "healthy")

    def test_restart_replays_same_authoritative_inputs(self) -> None:
        self.service.emit_event(self.event())
        restarted = ASWService(self.service.journal.path, self.policy)
        self.assertEqual(self.service.signals, restarted.signals)

    def test_rebuilding_deleted_derived_indexes_preserves_signal_history(self) -> None:
        self.service.emit_event(self.event("evt_one"))
        self.service.emit_event(self.event("evt_two", "C:\\workspace\\two.txt"))
        expected = list(self.service.signals)
        self.service.signals.clear()
        self.service.signal_sequences.clear()
        self.service.rebuild()
        self.assertEqual(expected, self.service.signals)


if __name__ == "__main__": unittest.main()
