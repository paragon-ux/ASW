"""Finite, deterministic, reject-by-default event-to-signal reduction."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Iterable

from .contracts import ContractError, validate

AuthorizationCheck = Callable[[dict[str, Any]], bool]


@dataclass(frozen=True)
class Reduction:
    """A pure reducer result; subscriptions deliberately do not appear here."""

    signal: dict[str, Any] | None
    superseded_signal_ids: tuple[str, ...] = ()
    reason: str | None = None


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _field(event: dict[str, Any], dotted: str) -> Any:
    value: Any = event
    for part in dotted.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _summary(event: dict[str, Any]) -> str:
    subject = event["subject"]
    value = subject["value"]
    if isinstance(value, dict):
        label = value.get("path") or value.get("name") or value.get("id") or subject["kind"]
    else:
        label = str(value)
    return f"{label} - {event['type']}"[:2048]


class Reducer:
    """Apply a versioned policy without time, random, IO, or subscriber state."""

    def __init__(self, policy: dict[str, Any]) -> None:
        validate("reducer-policy", policy)
        if policy["default_action"] != "reject":
            raise ContractError("ASW reducer policy must reject by default")
        if any(rule["action"] == "emit" and rule["emit"] is None for rule in policy["rules"]):
            raise ContractError("emitting reducer rules must define an emit contract")
        self.policy = deepcopy(policy)
        self._rules = tuple(sorted(self.policy["rules"], key=lambda rule: (-rule["priority"], rule["rule_id"])))

    def reduce(
        self,
        event: dict[str, Any],
        *,
        is_authorized: AuthorizationCheck,
        prior_signals: Iterable[dict[str, Any]] = (),
    ) -> Reduction:
        """Reduce one authorized reliable event to at most one canonical signal."""
        try:
            validate("event", event)
        except ContractError as error:
            return Reduction(None, reason=str(error))
        if event["source"]["reliability"] not in {"authoritative", "observed"}:
            return Reduction(None, reason="source reliability is not eligible for ordinary signal creation")
        if not is_authorized(event):
            return Reduction(None, reason="event is outside user observation authorization")

        if event["frontier"]["reducer_policy_version"] != self.policy["policy_version"]:
            return Reduction(None, reason="event frontier policy version does not match reducer policy")

        rule = self._matching_rule(event)
        if rule is None or rule["action"] != "emit":
            return Reduction(None, reason="no eligible reducer rule")
        emit = rule["emit"]
        assert emit is not None
        prior = tuple(prior_signals)
        dedupe_key = tuple(_canonical(_field(event, field)) for field in emit["dedupe_key_fields"])
        signal_id = "sig_" + hashlib.sha256(
            _canonical([self.policy["policy_version"], rule["rule_id"], dedupe_key]).encode()
        ).hexdigest()[:24]
        for existing in prior:
            if existing.get("signal_id") == signal_id:
                return Reduction(None, reason="duplicate authoritative event")
        frontier = dict(event["frontier"])
        frontier["reducer_policy_version"] = self.policy["policy_version"]
        signal = {
            "schema_version": "asw.signal.v1",
            "signal_id": signal_id,
            "derived_from": [event["event_id"]],
            "application_id": event["application_id"],
            "category": emit["category"],
            "kind": event["type"],
            "status": "current",
            "summary": _summary(event),
            "subject": event["subject"],
            "source_reliability": event["source"]["reliability"],
            "created_at": event["observed_at"],
            "frontier": frontier,
        }
        validate("signal", signal)
        superseded = self._superseded(signal, prior, emit["supersession_mode"])
        return Reduction(signal, superseded)

    def _matching_rule(self, event: dict[str, Any]) -> dict[str, Any] | None:
        for rule in self._rules:
            match = rule["match"]
            if event["type"] in match["event_types"] and event["source"]["reliability"] in match["reliability"]:
                return rule
        return None

    @staticmethod
    def _superseded(signal: dict[str, Any], prior_signals: Iterable[dict[str, Any]], mode: str) -> tuple[str, ...]:
        if mode != "same_subject_newer":
            return ()
        return tuple(
            prior["signal_id"]
            for prior in prior_signals
            if prior.get("status") == "current"
            and prior.get("application_id") == signal["application_id"]
            and prior.get("kind") == signal["kind"]
            and _canonical(prior.get("subject")) == _canonical(signal["subject"])
        )
