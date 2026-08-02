"""The complete RFC 0001 MVP reducer policy."""

from __future__ import annotations

from datetime import datetime, timezone

from .contracts import validate

CATEGORIES = {
    "file.created": "files", "file.modified": "files", "file.deleted": "files", "file.saved": "files",
    "artifact.available": "artifacts", "process.started": "processes", "process.completed": "processes",
    "process.failed": "processes", "process.crashed": "processes", "process.restarted": "processes",
    "job.completed": "jobs", "job.failed": "jobs", "window.created": "windows_ui", "dialog.appeared": "windows_ui",
    "operation.available": "windows_ui", "operation.completed": "application", "diagnostic.changed": "diagnostics",
    "shared_artifact.updated": "shared_artifacts", "source.degraded": "source_health", "source.reconciled": "source_health",
}


def mvp_policy() -> dict:
    rules = []
    for number, (event_type, category) in enumerate(CATEGORIES.items(), 1):
        rules.append({"rule_id": "rule_" + event_type.replace(".", "_"), "priority": 1000 - number,
            "match": {"event_types": [event_type], "reliability": ["authoritative", "observed"], "requires_authorization": True},
            "action": "emit", "emit": {"category": category, "kind_from_event": True,
                "dedupe_key_fields": ["application_id", "type", "subject.value"], "supersession_mode": "none"}})
    policy = {"schema_version": "asw.reducer_policy.v1", "policy_version": "asw.reducer.v1", "default_action": "reject",
              "rules": rules, "created_at": datetime.now(timezone.utc).isoformat()}
    validate("reducer-policy", policy)
    return policy
