"""Fair baseline observers for deterministic Layer A and Layer B runs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from ..consumers.asw_adapter import ASWAdapter
from ..scenarios.controller import ScenarioSurface


@dataclass(frozen=True)
class Observation:
    detected: bool
    recognized_ns: int | None
    observation_count: int
    duplicate_count: int
    false_positive_count: int
    application_attribution_correct: bool | None
    kind_correct: bool | None
    subject_correct: bool | None
    localization_correct: bool | None
    continuation_ready: bool | None
    recognized_kind: str | None = None
    recognized_application_id: str | None = None
    recognized_subject: Any = None
    error: str | None = None


class Observer:
    condition = ""

    def observe(self, surface: ScenarioSurface, *, interval_ms: int, deadline_ms: int, notification_template: str) -> Observation:
        raise NotImplementedError

    @staticmethod
    def _missed(observation_count: int, *, error: str | None = None) -> Observation:
        return Observation(
            detected=False,
            recognized_ns=None,
            observation_count=observation_count,
            duplicate_count=0,
            false_positive_count=0,
            application_attribution_correct=None,
            kind_correct=None,
            subject_correct=None,
            localization_correct=None,
            continuation_ready=False,
            error=error,
        )

    @staticmethod
    def _recognized(
        *,
        surface: ScenarioSurface,
        now_ns: int,
        observation_count: int,
        state: dict[str, Any],
        localization_correct: bool | None,
    ) -> Observation:
        kind = state.get("kind")
        application_id = state.get("application_id")
        return Observation(
            detected=True,
            recognized_ns=now_ns,
            observation_count=observation_count,
            duplicate_count=0,
            false_positive_count=0,
            # Correctness is scored by the controller against the independent
            # ground-truth record, never by an observer using its own success
            # condition.  The observer reports raw recognition fields only.
            application_attribution_correct=None,
            kind_correct=None,
            subject_correct=None,
            localization_correct=localization_correct,
            continuation_ready=bool(kind and application_id),
            recognized_kind=kind,
            recognized_application_id=application_id,
            recognized_subject=state.get("subject"),
        )


class PollingObserver(Observer):
    condition = "polling"

    def observe(self, surface: ScenarioSurface, *, interval_ms: int, deadline_ms: int, notification_template: str) -> Observation:
        count = 0
        interval_ns = interval_ms * 1_000_000
        deadline_ns = deadline_ms * 1_000_000
        now_ns = interval_ns
        while now_ns <= deadline_ns:
            count += 1
            state = surface.query_state(now_ns)
            if state.get("ready"):
                return self._recognized(surface=surface, now_ns=now_ns, observation_count=count, state=state, localization_correct=None)
            now_ns += interval_ns
        return self._missed(count, error="deadline_exceeded")


class RepeatedObservationObserver(Observer):
    condition = "repeated_observation"

    def observe(self, surface: ScenarioSurface, *, interval_ms: int, deadline_ms: int, notification_template: str) -> Observation:
        count = 0
        # The frozen profile declares one observation interval.  Repeated
        # observation differs by its explicit recheck contract, not by a
        # silently changed cadence.
        interval_ns = interval_ms * 1_000_000
        deadline_ns = deadline_ms * 1_000_000
        now_ns = interval_ns
        while now_ns <= deadline_ns:
            count += 1
            state = surface.query_state(now_ns)
            if state.get("ready"):
                return self._recognized(surface=surface, now_ns=now_ns, observation_count=count, state=state, localization_correct=None)
            now_ns += interval_ns
        return self._missed(count, error="deadline_exceeded")


class FilesystemWatchObserver(Observer):
    condition = "filesystem_watch"

    def observe(self, surface: ScenarioSurface, *, interval_ms: int, deadline_ms: int, notification_template: str) -> Observation:
        # A raw watcher is event driven, but it must wait for the stable event
        # rather than turning every burst write into a useful transition.
        count = 1
        event_time_ns = 0
        step_ns = max(interval_ms, 50) * 1_000_000
        deadline_ns = deadline_ms * 1_000_000
        while event_time_ns <= deadline_ns:
            events = surface.filesystem_events(event_time_ns)
            if events:
                count = len(events)
                stable = surface.stable_artifact(event_time_ns)
                if stable is not None:
                    return self._recognized(
                        surface=surface,
                        now_ns=event_time_ns,
                        observation_count=count,
                        state=stable,
                        localization_correct=None,
                    )
            event_time_ns += step_ns
        return self._missed(count, error="deadline_exceeded")


class OrdinaryNotificationObserver(Observer):
    condition = "ordinary_notification"

    _status_to_kind = {
        "completed": "job.completed",
        "failed": "job.failed",
        "artifact available": "artifact.available",
        "file changed": "file.modified",
        "dialog appeared": "dialog.appeared",
        "operation available": "operation.available",
        "crashed": "process.crashed",
        "restarted": "process.restarted",
    }

    def observe(self, surface: ScenarioSurface, *, interval_ms: int, deadline_ms: int, notification_template: str) -> Observation:
        delivery = surface.notification_delivery(deadline_ms * 1_000_000, notification_template)
        if delivery is None:
            return self._missed(1, error="deadline_exceeded")
        notification, received_ns = delivery
        if ": " not in notification:
            return self._missed(1, error="malformed_notification")
        application_id, plain_status = notification.split(": ", 1)
        kind = self._status_to_kind.get(plain_status)
        if kind is None:
            return self._missed(2, error="unrecognized_plain_status")
        state = {"kind": kind, "application_id": application_id, "subject": None}
        # The frozen protocol counts two observations: (1) notification
        # receipt and (2) parsing/interpretation. No structured ASW metadata,
        # replay cursor, or private ground truth is consulted.
        return self._recognized(surface=surface, now_ns=received_ns, observation_count=2, state=state, localization_correct=None)


class ASWObserver(Observer):
    condition = "asw"

    def __init__(self, adapter: ASWAdapter | None = None) -> None:
        self.adapter = adapter or ASWAdapter()

    def observe(self, surface: ScenarioSurface, *, interval_ms: int, deadline_ms: int, notification_template: str) -> Observation:
        try:
            subscription_id = self.adapter.subscribe(surface)
            # The public stream is checked at the first fixed signal delivery
            # opportunity.  A real client may block/wake; the synthetic client
            # models that same public boundary without sleeping.
            delivery = surface.asw_delivery(deadline_ms * 1_000_000)
            if delivery is None:
                return self._missed(1, error="deadline_exceeded")
            now_ns, _ = delivery
            received_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            signals = self.adapter.read_or_stream(subscription_id, surface, received_at=received_at)
        except PermissionError as exc:
            return self._missed(1, error=f"authorization_violation:{exc}")
        if not signals:
            return self._missed(1, error="deadline_exceeded")
        signal = signals[0]
        return self._recognized(
            surface=surface,
            now_ns=now_ns,
            observation_count=1,
            state=signal,
            # Canonical ASW signals carry the structured subject/frontier; UI
            # coordinate localization is a source payload concern and is not
            # fabricated by the adapter when the public signal omits it.
            localization_correct=None,
        )


def observer_for(condition: str, *, asw_adapter: ASWAdapter | None = None) -> Observer:
    observers: dict[str, Observer] = {
        "polling": PollingObserver(),
        "filesystem_watch": FilesystemWatchObserver(),
        "ordinary_notification": OrdinaryNotificationObserver(),
        "repeated_observation": RepeatedObservationObserver(),
        "asw": ASWObserver(asw_adapter),
    }
    try:
        return observers[condition]
    except KeyError as exc:
        raise ValueError(f"unknown baseline condition: {condition}") from exc
