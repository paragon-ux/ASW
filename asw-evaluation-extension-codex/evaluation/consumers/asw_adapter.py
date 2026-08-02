"""ASW condition adapter constrained to committed public/service interfaces.

The default path imports the accepted ASW core from the sibling target
repository, registers a real user-authorized source and agent grant, publishes
the controlled probe event through ``ASWService.emit_event``, and reads the
canonical signal through ``AgentAPI.open_signal_stream``.  No reducer, journal,
cache, or private service field is read by the adapter.
"""

from __future__ import annotations

import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol


class PublicASWClient(Protocol):
    def subscribe(self, application_id: str, event_kind: str, category: str) -> str: ...

    def publish_probe_event(self, surface: Any, observed_at: str) -> None: ...

    def open_signal_stream(self, subscription_id: str) -> list[dict[str, Any]]: ...


class CoreASWPublicClient:
    """Small harness adapter over the committed ASW public/service boundary."""

    def __init__(self, core_repo: Path) -> None:
        self.core_repo = core_repo
        if not (core_repo / "asw" / "service.py").exists():
            raise RuntimeError(f"accepted ASW core not found at {core_repo}")
        core_text = str(core_repo)
        if core_text not in sys.path:
            sys.path.insert(0, core_text)
        from asw.agent_api import AgentAPI
        from asw.defaults import mvp_policy
        from asw.service import ASWService

        self._AgentAPI = AgentAPI
        self._temp = tempfile.TemporaryDirectory(prefix="asw-eval-core-")
        self.service = ASWService(Path(self._temp.name) / "journal.jsonl", mvp_policy())
        self.agent_id = "agent:evaluation"
        self._api = None
        self._subscriptions: dict[str, str] = {}
        self._application_ids: set[str] = set()
        # The adapter owns these lifecycle flags.  It must not inspect the
        # core's projection dictionaries to decide whether public records
        # have already been registered.
        self._subscriber_registered = False
        self._grant_registered = False

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _ensure_application(self, application_id: str, source_id: str, adapter: str) -> None:
        if application_id in self._application_ids:
            return
        now = self._now()
        source_kind = "filesystem" if adapter == "filesystem" else "application"
        scope = {
            "application_id": application_id,
            "source_id": source_id,
            "source_kind": source_kind,
            "filesystem_roots": [r"C:\ASW-Evaluation"] if source_kind == "filesystem" else [],
            "executable_names": [],
            "job_kinds": [],
            "uia_process_names": [],
            "adapter_contract": "controlled-evaluation.v1" if source_kind == "application" else None,
        }
        authorization = {
            "schema_version": "asw.observation_authorization.v1",
            "authorization_id": f"auth_eval_{len(self._application_ids)}",
            "authorized_by": "user:local",
            "enabled": True,
            "scopes": [scope],
            "created_at": now,
            "updated_at": now,
        }
        source = {
            "schema_version": "asw.source_registration.v1",
            "source_id": source_id,
            "adapter": adapter,
            "application_id": application_id,
            "enabled": True,
            "authorization_id": authorization["authorization_id"],
            "configuration": {"roots": [r"C:\ASW-Evaluation"]} if adapter == "filesystem" else {"adapter_contract": "controlled-evaluation.v1"},
            "settle_profile": None,
            "registered_at": now,
        }
        subscriber = {
            "schema_version": "asw.subscriber.v1",
            "subscriber_id": self.agent_id,
            "kind": "agent",
            "display_name": "Phase 8 controlled continuation agent",
            "enabled": True,
            "created_at": now,
        }
        grant = {
            "schema_version": "asw.agent_access.v1",
            "grant_id": f"grant_eval_{len(self._application_ids)}",
            "agent_subscriber_id": self.agent_id,
            "enabled": True,
            "applications": [application_id],
            "categories": ["files", "artifacts", "jobs", "processes", "windows_ui", "application"],
            "allow_replay": True,
            "created_at": now,
            "expires_at": None,
        }
        self.service.record("observation_authorization", authorization)
        self.service.record("source_registration", source)
        if not self._subscriber_registered:
            self.service.record("subscriber", subscriber)
            self._subscriber_registered = True
        if not self._grant_registered:
            self.service.record("agent_access", grant)
            self._grant_registered = True
        self._application_ids.add(application_id)

    def subscribe(self, application_id: str, event_kind: str, category: str) -> str:
        source_id = f"app-source:{application_id}"
        adapter = "filesystem" if event_kind in {"file.created", "file.modified", "file.deleted", "file.saved", "artifact.available"} else "application"
        self._ensure_application(application_id, source_id, adapter)
        now = self._now()
        subscription_id = f"sub_eval_{len(self._subscriptions)}"
        subscription = {
            "schema_version": "asw.subscription.v1",
            "subscription_id": subscription_id,
            "subscriber_id": self.agent_id,
            "subscriber_kind": "agent",
            "enabled": True,
            "applications": [application_id],
            "categories": [category],
            "event_types": [event_kind],
            "destinations": ["agent_stream"],
            "created_at": now,
            "updated_at": now,
        }
        self.service.register_subscription(subscription)
        self._subscriptions[subscription_id] = application_id
        self._api = self._AgentAPI(self.service, self.agent_id)
        return subscription_id

    def publish_probe_event(self, surface: Any, observed_at: str) -> None:
        # emit_event is the service's public producer boundary; the adapter
        # never reaches into the journal or reducer projections.
        self.service.emit_event(surface.source_event(observed_at))

    def open_signal_stream(self, subscription_id: str) -> list[dict[str, Any]]:
        if self._api is None:
            raise PermissionError("public ASW subscription is not initialized")
        response = self._api.open_signal_stream(subscription_id, limit=1)
        return list(response.get("signals", []))

    def close(self) -> None:
        self._temp.cleanup()


class ASWAdapter:
    """Thin consumer adapter using public subscribe, emit, and stream APIs."""

    def __init__(self, *, client: PublicASWClient | None = None, core_repo: Path | None = None) -> None:
        if client is None:
            default_repo = core_repo or Path(__file__).resolve().parents[3] / "asw-spec-codex"
            client = CoreASWPublicClient(default_repo)
        self.client = client
        self.authorization_violations = 0
        self.replay_violations = 0

    def subscribe(self, surface: Any) -> str:
        kind = surface.transition_kinds[0]
        category = {
            "file.created": "files", "file.modified": "files", "file.deleted": "files", "file.saved": "files",
            "artifact.available": "artifacts", "process.started": "processes", "process.completed": "processes",
            "process.failed": "processes", "process.crashed": "processes", "process.restarted": "processes",
            "job.completed": "jobs", "job.failed": "jobs", "window.created": "windows_ui",
            "dialog.appeared": "windows_ui", "operation.available": "windows_ui", "operation.completed": "application",
            "diagnostic.changed": "diagnostics", "shared_artifact.updated": "shared_artifacts",
        }.get(kind)
        if category is None:
            raise ValueError(f"unsupported ASW event kind: {kind}")
        return self.client.subscribe(surface.application_id, kind, category)

    def read_or_stream(self, subscription_id: str, surface: Any, *, received_at: str) -> list[dict[str, Any]]:
        try:
            self.client.publish_probe_event(surface, received_at)
            return self.client.open_signal_stream(subscription_id)
        except PermissionError:
            self.authorization_violations += 1
            raise
