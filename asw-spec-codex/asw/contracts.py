"""Schema-backed contracts used at ASW's authoritative boundaries."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "schemas"

SCHEMA_BY_PREFIX = {
    "agent-access": "agent-access.schema.json",
    "agent-stream-request": "agent-stream-request.schema.json",
    "application": "application.schema.json",
    "coordinate-payload": "coordinate-payload.schema.json",
    "delivery": "delivery.schema.json",
    "event": "event.schema.json",
    "frontier": "frontier.schema.json",
    "journal-record": "journal-record.schema.json",
    "observation-authorization": "observation-authorization.schema.json",
    "reducer-policy": "reducer-policy.schema.json",
    "replay-cursor": "replay-cursor.schema.json",
    "signal": "signal.schema.json",
    "source-registration": "source-registration.schema.json",
    "subscriber": "subscriber.schema.json",
    "subscription": "subscription.schema.json",
}


class ContractError(ValueError):
    """An object at an ASW contract boundary is invalid."""


@lru_cache(maxsize=1)
def _schemas() -> tuple[dict[str, dict[str, Any]], Registry]:
    schemas: dict[str, dict[str, Any]] = {}
    registry = Registry()
    for path in SCHEMA_ROOT.glob("*.schema.json"):
        schema = json.loads(path.read_text(encoding="utf-8"))
        schemas[path.name] = schema
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    return schemas, registry


def validate(kind: str, instance: dict[str, Any]) -> None:
    """Validate an instance or raise one concise, stable boundary error."""
    schema_name = SCHEMA_BY_PREFIX.get(kind)
    if schema_name is None:
        raise ContractError(f"unknown ASW contract kind: {kind}")
    schemas, registry = _schemas()
    validator = Draft202012Validator(
        schemas[schema_name], registry=registry, format_checker=Draft202012Validator.FORMAT_CHECKER
    )
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.absolute_path))
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "root"
        raise ContractError(f"invalid {kind} at {location}: {error.message}")


def contract_kind_for_schema_version(schema_version: str) -> str:
    """Map a schema version to its public contract kind, fail-closed otherwise."""
    prefix = schema_version.removeprefix("asw.").split(".v", 1)[0]
    return prefix if prefix in SCHEMA_BY_PREFIX else ""
