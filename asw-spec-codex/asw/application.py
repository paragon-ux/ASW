"""Application identity and GUI grouping primitives."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

UNKNOWN_APPLICATION_ID = "asw.unknown"
SYSTEM_APPLICATION_ID = "asw.system"


def application_group(application_id: str | None) -> str:
    """Return the required stable group for an absent or unknown identity."""
    return application_id.strip() if isinstance(application_id, str) and application_id.strip() else UNKNOWN_APPLICATION_ID


def normalize_event_application(event: dict[str, Any]) -> dict[str, Any]:
    """Assign unattributed supported facts to the RFC's unknown group."""
    normalized = deepcopy(event)
    normalized["application_id"] = application_group(normalized.get("application_id"))
    return normalized


def system_application(now: str) -> dict[str, Any]:
    return {
        "schema_version": "asw.application.v1",
        "application_id": SYSTEM_APPLICATION_ID,
        "display_name": "ASW system",
        "identity": {"kind": "system"},
        "enabled": True,
        "registered_at": now,
    }
