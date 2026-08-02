from __future__ import annotations

import json
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from pathlib import Path

from asw.agent_api import AgentAPI
from asw.contracts import ContractError
from asw.defaults import mvp_policy
from asw.delivery import WindowsAppSdkDelivery, WindowsAppSdkSender
from asw.service import ASWService

ROOT = Path(__file__).resolve().parents[1]


def fixture(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / "valid" / name).read_text(encoding="utf-8"))


class AgentApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.service = ASWService(Path(self.temp.name) / "journal.jsonl", mvp_policy())
        auth = fixture("observation-authorization.json"); auth["scopes"] = [auth["scopes"][0]]; auth["scopes"][0]["source_id"] = "fs:api"
        self.service.record("observation_authorization", auth)
        source = fixture("source-registration.filesystem.json"); source["source_id"] = "fs:api"; self.service.record("source_registration", source)
        self.service.emit_event(self.event())
        self.service.record("subscriber", fixture("subscriber.agent.json"))
        self.service.record("agent_access", fixture("agent-access.json"))
        self.subscription = fixture("subscription.agent.json"); self.service.register_subscription(self.subscription)

    def tearDown(self) -> None: self.temp.cleanup()

    def event(self):
        event = fixture("event.file-saved.json"); event["source"]["adapter"] = "filesystem"; event["source"]["source_id"] = "fs:api"; return event

    def test_logical_operations_are_bounded_and_owned(self) -> None:
        api = AgentAPI(self.service, "agent:codex-1")
        self.assertIn("list_signals", api.get_capabilities()["operations"])
        applications = api.list_applications(limit=1)
        self.assertEqual(applications["applications"], [])  # no application registration, only authorized source
        self.assertIn("replay_cursor", applications)
        self.assertEqual(len(api.list_subscriptions(limit=1)["subscriptions"]), 1)
        self.assertEqual(len(api.handle("list_signals", {"subscription_id": self.subscription["subscription_id"]})["signals"]), 1)
        other = dict(self.subscription); other["subscriber_id"] = "agent:other"
        with self.assertRaises(PermissionError): api.update_subscription(other)

    def test_normative_stream_request_is_schema_validated_and_plural(self) -> None:
        api = AgentAPI(self.service, "agent:codex-1")
        request = fixture("agent-stream-request.json")
        request["after"] = None
        response = api.handle("open_signal_stream", request)
        self.assertEqual(len(response["signals"]), 1)
        self.assertIn("replay_cursor", response)
        invalid = dict(request)
        invalid.pop("schema_version")
        with self.assertRaises(ContractError): api.handle("open_signal_stream", invalid)

    def test_snapshot_cursor_advances_bounded_subscription_pages(self) -> None:
        second = dict(self.subscription)
        second["subscription_id"] = "sub_agent_two"
        self.service.register_subscription(second)
        api = AgentAPI(self.service, "agent:codex-1")
        first = api.list_subscriptions(limit=1)
        self.assertEqual(len(first["subscriptions"]), 1)
        next_page = api.list_subscriptions(limit=1, after=first["replay_cursor"])
        self.assertEqual(len(next_page["subscriptions"]), 1)
        self.assertNotEqual(first["subscriptions"][0]["subscription_id"], next_page["subscriptions"][0]["subscription_id"])

    def test_cursor_tracks_last_returned_signal_and_get_is_not_page_capped(self) -> None:
        second = self.event()
        second["event_id"] = "evt_api_second"
        second["subject"] = {"kind": "path", "value": {"path": "C:\\src\\project\\second.txt"}}
        self.service.emit_event(second)
        api = AgentAPI(self.service, "agent:codex-1")
        first_page = api.list_signals(self.subscription["subscription_id"], limit=1)
        self.assertEqual(len(first_page["signals"]), 1)
        first_id = first_page["signals"][0]["signal_id"]
        self.assertEqual(first_page["replay_cursor"]["frontier"]["journal_sequence"], self.service.signal_sequences[first_id])
        second_page = api.resume_signal_stream(self.subscription["subscription_id"], first_page["replay_cursor"], limit=1)
        self.assertEqual(len(second_page["signals"]), 1)
        self.assertNotEqual(second_page["signals"][0]["signal_id"], first_id)
        self.assertEqual(api.get_signal(self.subscription["subscription_id"], second_page["signals"][0]["signal_id"]), second_page["signals"][0])

    def test_notification_platform_failure_is_audited_without_signal_mutation(self) -> None:
        user = fixture("subscription.user.json"); user["categories"] = ["files"]; user["event_types"] = ["file.saved"]; self.service.register_subscription(user)
        signal = self.service.signals[0]
        delivery = WindowsAppSdkDelivery(self.service, lambda _: (_ for _ in ()).throw(RuntimeError("toast unavailable")))
        self.assertFalse(delivery.deliver(signal, user)); self.assertEqual(signal, self.service.signals[0]); self.assertEqual(self.service.deliveries[-1]["status"], "failed")

    def test_delivery_authorizes_before_sender(self) -> None:
        calls = []
        delivery = WindowsAppSdkDelivery(self.service, calls.append)
        signal = self.service.signals[0]
        self.assertFalse(delivery.deliver(signal, self.subscription))
        self.assertEqual(calls, [])
        self.assertEqual(self.service.deliveries, [])

    def test_windows_sender_transport_is_bounded_and_delivery_uses_canonical_signal(self) -> None:
        user = fixture("subscription.user.json"); user["categories"] = ["files"]; user["event_types"] = ["file.saved"]; self.service.register_subscription(user)
        signal = self.service.signals[0]
        captured = []
        sender = WindowsAppSdkSender(captured.append)
        forged = dict(signal); forged["summary"] = "forged"
        self.assertTrue(WindowsAppSdkDelivery(self.service, sender).deliver(forged, user))
        self.assertEqual(captured[0]["body"], signal["summary"])
        self.assertLessEqual(len(captured[0]["body"]), 2048)

    def test_loopback_agent_server_authenticates_and_dispatches_without_cli(self) -> None:
        from asw.agent_api import LocalAgentServer

        server = LocalAgentServer(self.service)
        endpoint = server.start()
        token = server.issue_token("agent:codex-1")
        self.assertTrue(endpoint.startswith("http://127.0.0.1:"))
        response = server.dispatch(token, "list_signals", {"subscription_id": self.subscription["subscription_id"], "limit": 1})
        self.assertEqual(len(response["signals"]), 1)
        request = Request(
            endpoint + "/v1/agent",
            data=json.dumps({"token": token, "operation": "get_access_grant", "payload": {}}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=2) as stream:
            self.assertTrue(json.loads(stream.read())["ok"])
        invalid_request = Request(
            endpoint + "/v1/agent",
            data=json.dumps({"token": token, "operation": "open_signal_stream", "payload": {}}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with self.assertRaises(HTTPError) as error:
            urlopen(invalid_request, timeout=2)
        self.assertEqual(error.exception.code, 400)
        self.assertIn("schema_version", json.loads(error.exception.read())["error"])
        with self.assertRaises(PermissionError): server.dispatch("invalid", "get_access_grant", {})
        server.revoke_agent("agent:codex-1")
        with self.assertRaises(PermissionError): server.dispatch(token, "get_access_grant", {})
        server.stop()


if __name__ == "__main__": unittest.main()
