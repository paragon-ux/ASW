"""Authoritative JSONL runtime, access boundary, source intake, and replay projection."""

from __future__ import annotations

import json
import ntpath
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Callable, Iterable

from .application import application_group
from .contracts import ContractError, validate
from .reducer import Reducer


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Journal:
    """The sole durable authority; projections are intentionally reconstructible."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.sequence = max((item["journal_sequence"] for item in self.records()), default=-1)

    def records(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def append(self, record_kind: str, record: dict[str, Any]) -> dict[str, Any]:
        self.sequence += 1
        item = {"schema_version": "asw.journal_record.v1", "journal_sequence": self.sequence,
                "recorded_at": utc_now(), "record_kind": record_kind, "record": record}
        validate("journal-record", item)
        with self.path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n")
        return item


class ASWService:
    """Small service core: journal is authority; all fields below are rebuildable projections."""

    def __init__(self, journal_path: str | Path, policy: dict[str, Any], clock: Callable[[], datetime] | None = None) -> None:
        self.journal = Journal(Path(journal_path))
        self._lock = RLock()
        self.reducer = Reducer(policy)
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.policies: dict[str, dict[str, Any]] = {policy["policy_version"]: policy}
        self.runtime_epoch = str(uuid.uuid4())
        self.applications: dict[str, dict[str, Any]] = {}
        self.projection_sequences: dict[str, dict[str, int]] = {"application": {}, "subscription": {}}
        self.authorizations: dict[str, dict[str, Any]] = {}
        self.sources: dict[str, dict[str, Any]] = {}
        self.subscribers: dict[str, dict[str, Any]] = {}
        self.grants: dict[str, dict[str, Any]] = {}
        self.subscriptions: dict[str, dict[str, Any]] = {}
        self.signals: list[dict[str, Any]] = []
        self.signal_sequences: dict[str, int] = {}
        self.source_health: dict[str, str] = {}
        self.deliveries: list[dict[str, Any]] = []
        # Optional runtime boundary installed by the GUI/bootstrap.  It is not
        # journal authority and is deliberately absent during replay/tests.
        self.windows_delivery = None
        if not self.journal.records():
            self.journal.append("policy_change", {"policy": policy})
        self.rebuild()

    def rebuild(self) -> None:
        with self._lock:
            self.applications.clear(); self.authorizations.clear(); self.sources.clear(); self.subscribers.clear()
            self.grants.clear(); self.subscriptions.clear(); self.signals.clear(); self.signal_sequences.clear(); self.source_health.clear(); self.deliveries.clear(); self.policies.clear()
            for sequences in self.projection_sequences.values(): sequences.clear()
            for item in self.journal.records():
                self._project(item["record_kind"], item["record"], replaying=True, sequence=item["journal_sequence"])

    def record(self, kind: str, value: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            schema_kind = {"application": "application", "observation_authorization": "observation-authorization",
                "source_registration": "source-registration", "subscriber": "subscriber", "agent_access": "agent-access",
                "subscription": "subscription", "delivery": "delivery", "event": "event"}.get(kind)
            if schema_kind: validate(schema_kind, value)
            if kind == "source_registration": self._validate_source_registration(value)
            if kind == "agent_access":
                subscriber = self.subscribers.get(value["agent_subscriber_id"])
                if subscriber is not None and subscriber.get("kind") != "agent": raise PermissionError("agent grant requires an agent subscriber")
            item = self.journal.append(kind, value)
            self._project(kind, value, replaying=False, sequence=item["journal_sequence"])
            return item

    def _validate_source_registration(self, source: dict[str, Any]) -> None:
        authorization = self.authorizations.get(source["authorization_id"])
        if not authorization or not authorization["enabled"]: raise PermissionError("source requires active observation authorization")
        source_kind = "process_job" if source["adapter"] in {"process", "job"} else source["adapter"]
        scopes = [scope for scope in authorization["scopes"] if scope["application_id"] == source["application_id"]
                  and scope["source_id"] == source["source_id"] and scope["source_kind"] == source_kind]
        if not scopes:
            raise PermissionError("source registration exceeds observation authorization")
        config = source["configuration"]
        if source_kind == "filesystem":
            roots = config.get("roots", [])
            authorized_roots = [root for scope in scopes for root in scope.get("filesystem_roots", [])]
            if not roots or not authorized_roots or not all(any(self._path_within(path, root) for root in authorized_roots) for path in roots):
                raise PermissionError("filesystem source roots exceed observation authorization")
        if source["adapter"] == "process":
            values = {item.casefold() for item in config.get("executable_names", [])}
            allowed = {item.casefold() for scope in scopes for item in scope.get("executable_names", [])}
            if not values or not values.issubset(allowed): raise PermissionError("process source identities exceed observation authorization")
        if source["adapter"] == "job":
            values = set(config.get("job_kinds", [])); allowed = {item for scope in scopes for item in scope.get("job_kinds", [])}
            if not values or not values.issubset(allowed): raise PermissionError("job source kinds exceed observation authorization")
            executable_values = {item.casefold() for item in config.get("executable_names", [])}
            executable_allowed = {item.casefold() for scope in scopes for item in scope.get("executable_names", [])}
            if not executable_values.issubset(executable_allowed): raise PermissionError("job executable identities exceed observation authorization")
        if source["adapter"] == "uia":
            values = {item.casefold() for item in config.get("uia_process_names", [])}
            allowed = {item.casefold() for scope in scopes for item in scope.get("uia_process_names", [])}
            if not values or not values.issubset(allowed): raise PermissionError("UI Automation process scope exceeds observation authorization")
        if source["adapter"] in {"application", "diagnostic"}:
            contract = config.get("adapter_contract")
            allowed_contracts = {scope.get("adapter_contract") for scope in scopes if scope.get("adapter_contract")}
            if not contract or contract not in allowed_contracts: raise PermissionError("source adapter contract does not match observation authorization")

    @staticmethod
    def _path_within(path: str, root: str) -> bool:
        if not ntpath.isabs(path) or not ntpath.isabs(root): return False
        normalized_path = ntpath.normcase(ntpath.normpath(path)).rstrip("\\")
        normalized_root = ntpath.normcase(ntpath.normpath(root)).rstrip("\\")
        return normalized_path == normalized_root or normalized_path.startswith(normalized_root + "\\")

    def _project(self, kind: str, value: dict[str, Any], replaying: bool, sequence: int) -> None:
        if kind == "policy_change":
            policy = value.get("policy")
            if not isinstance(policy, dict): raise ContractError("policy_change requires a policy")
            validate("reducer-policy", policy); self.policies[policy["policy_version"]] = policy; self.reducer = Reducer(policy)
        elif kind == "application":
            self.applications[value["application_id"]] = value
            self.projection_sequences["application"][value["application_id"]] = sequence
        elif kind == "observation_authorization": self.authorizations[value["authorization_id"]] = value
        elif kind == "source_registration": self.sources[value["source_id"]] = value
        elif kind == "subscriber": self.subscribers[value["subscriber_id"]] = value
        elif kind == "agent_access": self.grants[value["agent_subscriber_id"]] = value
        elif kind == "subscription":
            self.subscriptions[value["subscription_id"]] = value
            self.projection_sequences["subscription"][value["subscription_id"]] = sequence
        elif kind == "delivery": self.deliveries.append(value)
        elif kind == "event":
            version = value["frontier"]["reducer_policy_version"]
            policy = self.policies.get(version)
            if policy is None: return
            result = Reducer(policy).reduce(value, is_authorized=self.event_authorized, prior_signals=self.signals)
            if result.signal:
                for signal in self.signals:
                    if signal["signal_id"] in result.superseded_signal_ids: signal["status"] = "superseded"
                self.signals.append(result.signal)
                self.signal_sequences[result.signal["signal_id"]] = sequence
            source_id = value["source"]["source_id"]
            if value["type"] == "source.degraded" and source_id in self.sources and self.event_authorized(value):
                self.source_health[source_id] = "degraded"
            elif value["type"] == "source.reconciled" and source_id in self.sources and self.source_health.get(source_id) == "degraded" and self.event_authorized(value) and self._has_reconciliation_evidence(value):
                self.source_health[source_id] = "healthy"

    @staticmethod
    def _has_reconciliation_evidence(event: dict[str, Any]) -> bool:
        payload = event.get("payload") or {}
        frontier = event.get("frontier") or {}
        for source in frontier.get("source_frontiers", {}).values():
            if source.get("reconciliation_id"):
                return True
        return bool(payload.get("snapshot_digest") or payload.get("reconciliation_id"))

    def event_authorized(self, event: dict[str, Any]) -> bool:
        source_id = event["source"]["source_id"]
        source = self.sources.get(source_id)
        if not source or not source["enabled"] or source["adapter"] != event["source"]["adapter"] or source["application_id"] != event["application_id"]:
            return False
        if self.source_health.get(source_id) == "degraded" and event["type"] not in {"source.degraded", "source.reconciled"}:
            return False
        authorization = self.authorizations.get(source["authorization_id"])
        if not authorization or not authorization["enabled"]: return False
        try:
            self._validate_source_registration(source)
        except PermissionError:
            return False
        if not self._event_source_scope_allowed(event, source):
            return False
        return True

    @staticmethod
    def _event_source_scope_allowed(event: dict[str, Any], source: dict[str, Any]) -> bool:
        """Re-check adapter identity/scope at the authoritative event boundary.

        SourceAdapter helpers validate their own calls, but journal/event input
        can also arrive from another local producer or during replay.  The
        service therefore never trusts adapter-side filtering alone.
        """
        event_type = event.get("type")
        if event_type in {"source.degraded", "source.reconciled"}:
            return True
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        adapter = source["adapter"]
        if adapter == "filesystem":
            if event_type not in {"file.created", "file.modified", "file.deleted", "file.saved", "artifact.available"}:
                return False
        elif adapter == "process":
            if event_type not in {"process.started", "process.completed", "process.failed", "process.crashed", "process.restarted"}:
                return False
            executable_name = payload.get("executable_name")
            allowed = {item.casefold() for item in source["configuration"].get("executable_names", [])}
            if not isinstance(executable_name, str) or executable_name.casefold() not in allowed:
                return False
        elif adapter == "job":
            if event_type not in {"job.completed", "job.failed"}:
                return False
            job_kind = payload.get("job_kind")
            allowed_kinds = set(source["configuration"].get("job_kinds", []))
            if not isinstance(job_kind, str) or job_kind not in allowed_kinds:
                return False
            configured_executables = {item.casefold() for item in source["configuration"].get("executable_names", [])}
            if configured_executables:
                executable_name = payload.get("executable_name")
                if not isinstance(executable_name, str) or executable_name.casefold() not in configured_executables:
                    return False
        elif adapter == "uia":
            if event_type not in {"window.created", "dialog.appeared", "operation.available"}:
                return False
            process_name = payload.get("process_name")
            allowed_processes = {item.casefold() for item in source["configuration"].get("uia_process_names", [])}
            if not isinstance(process_name, str) or process_name.casefold() not in allowed_processes:
                return False
            coordinates = payload.get("coordinates")
            if not isinstance(coordinates, dict):
                return False
            try:
                validate("coordinate-payload", coordinates)
            except ContractError:
                return False
        elif adapter == "application":
            if event_type not in {
                "file.saved", "artifact.available", "process.crashed", "process.restarted",
                "job.completed", "job.failed", "dialog.appeared", "operation.available",
                "operation.completed", "diagnostic.changed", "shared_artifact.updated",
            }:
                return False
        elif adapter == "diagnostic":
            if event_type != "diagnostic.changed":
                return False
        else:
            return False
        if adapter in {"application", "diagnostic"}:
            return payload.get("adapter_contract") == source["configuration"].get("adapter_contract")
        source_kind = "process_job" if source["adapter"] in {"process", "job"} else source["adapter"]
        if source_kind == "filesystem":
            subject_value = event.get("subject", {}).get("value", {})
            path = subject_value.get("path") if isinstance(subject_value, dict) else None
            return bool(path and any(ASWService._path_within(path, root) for root in source["configuration"].get("roots", [])))
        return True

    def application_authorized(self, application_id: str) -> bool:
        return any(auth["enabled"] and any(scope["application_id"] == application_id for scope in auth["scopes"])
                   for auth in self.authorizations.values())

    def emit_event(self, event: dict[str, Any]) -> None:
        with self._lock:
            event = dict(event); event["application_id"] = application_group(event.get("application_id"))
            prior_signal_ids = {signal["signal_id"] for signal in self.signals}
            self.record("event", event)
            if self.windows_delivery is not None:
                for signal in self.signals:
                    if signal["signal_id"] in prior_signal_ids:
                        continue
                    for subscription in list(self.subscriptions.values()):
                        if subscription["subscriber_kind"] == "user" and "windows_app_sdk" in subscription["destinations"] and self._matches(signal, subscription):
                            self.windows_delivery.deliver(signal, subscription)

    def record_policy_change(self, policy: dict[str, Any]) -> None:
        validate("reducer-policy", policy)
        self.record("policy_change", {"policy": policy})

    def register_subscription(self, subscription: dict[str, Any]) -> None:
        if subscription["subscriber_kind"] == "agent":
            self._enforce_agent_scope(subscription["subscriber_id"], subscription)
        self.record("subscription", subscription)

    def _enforce_agent_scope(self, agent_id: str, requested: dict[str, Any]) -> dict[str, Any]:
        grant = self.grants.get(agent_id)
        if not grant or not grant["enabled"] or self._grant_expired(grant): raise PermissionError("active agent access grant required")
        if not set(requested["applications"]).issubset(grant["applications"]) or not set(requested["categories"]).issubset(grant["categories"]):
            raise PermissionError("requested subscription exceeds active agent access grant")
        if not all(self.application_authorized(app) for app in requested["applications"]):
            raise PermissionError("requested subscription exceeds user-authorized observation universe")
        return grant

    def _grant_expired(self, grant: dict[str, Any]) -> bool:
        if grant.get("expires_at") is None: return False
        try:
            expires = datetime.fromisoformat(grant["expires_at"].replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return True
        return expires <= self.clock()

    def get_agent_grant(self, agent_id: str) -> dict[str, Any] | None:
        grant = self.grants.get(agent_id)
        if not grant or not grant["enabled"] or self._grant_expired(grant): return None
        return grant

    def _matches(self, signal: dict[str, Any], selection: dict[str, Any]) -> bool:
        return (selection.get("enabled", False) and signal["application_id"] in selection["applications"] and signal["category"] in selection["categories"]
                and (not selection["event_types"] or signal["kind"] in selection["event_types"]))

    def agent_signals(self, agent_id: str, subscription_id: str, limit: int = 100, after: dict[str, Any] | int | None = None) -> dict[str, Any]:
        with self._lock:
            if not 1 <= limit <= 1000: raise ValueError("limit must be between 1 and 1000")
            sub = self.subscriptions.get(subscription_id)
            if not sub or sub["subscriber_id"] != agent_id or sub["subscriber_kind"] != "agent": raise PermissionError("agent may access only its own subscription")
            if not sub["enabled"]: raise PermissionError("subscription is disabled")
            self._enforce_agent_scope(agent_id, sub)
            visible = [signal for signal in self.signals if self._matches(signal, sub) and self.application_authorized(signal["application_id"])]
            if isinstance(after, dict):
                validate("replay-cursor", after)
                if after["subscriber_id"] not in {None, agent_id}: raise PermissionError("cursor belongs to another subscriber")
                after_sequence = after["frontier"]["journal_sequence"]
            else:
                after_sequence = -1 if after is None else after
            visible = [s for s in visible if self.signal_sequences.get(s["signal_id"], -1) > after_sequence][:limit]
            cursor_sequence = self.signal_sequences.get(visible[-1]["signal_id"], after_sequence) if visible else max(after_sequence, 0)
            return {"schema_version": "asw.agent_response.v1", "signals": visible, "replay_cursor": self.cursor(agent_id, cursor_sequence)}

    def cursor(self, subscriber_id: str, journal_sequence: int | None = None) -> dict[str, Any]:
        with self._lock:
            cursor = {"schema_version": "asw.replay_cursor.v1", "cursor_id": "cursor_" + uuid.uuid4().hex, "subscriber_id": subscriber_id, "frontier": {
                "schema_version": "asw.frontier.v1", "journal_sequence": self.journal.sequence if journal_sequence is None else max(0, journal_sequence), "runtime_epoch": self.runtime_epoch,
                "source_frontiers": {}, "reducer_policy_version": self.reducer.policy["policy_version"]}, "issued_at": utc_now()}
            validate("replay-cursor", cursor)
            return cursor

    def deliver(self, signal: dict[str, Any], subscription: dict[str, Any], success: bool, error: str | None = None) -> None:
        with self._lock:
            canonical = next((item for item in self.signals if item["signal_id"] == signal.get("signal_id")), None)
            if canonical is None:
                return
            signal = canonical
            authoritative = self.subscriptions.get(subscription["subscription_id"])
            if not authoritative or not self._matches(signal, authoritative): return
            if authoritative["subscriber_kind"] != "user" or "windows_app_sdk" not in authoritative["destinations"]: return
            self.record("delivery", {"schema_version": "asw.delivery.v1", "delivery_id": "delivery_" + uuid.uuid4().hex,
                "signal_id": signal["signal_id"], "subscription_id": authoritative["subscription_id"], "subscriber_id": authoritative["subscriber_id"],
                "destination": "windows_app_sdk", "status": "delivered" if success else "failed", "attempted_at": utc_now(),
                "completed_at": utc_now(), "error_code": None if success else "windows_delivery_failed", "error_summary": error,
                "frontier": signal["frontier"]})
