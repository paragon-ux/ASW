"""Scenario controller, independent ground truth, and deterministic probes.

The controller is the only component that receives the expected transition
identity and transition timestamp.  Observers receive a public scenario
surface, not a ground-truth object or the private recorder path.
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from ..schema import validate_scenario_semantics


BASELINES = (
    "polling",
    "filesystem_watch",
    "ordinary_notification",
    "repeated_observation",
    "asw",
)


@dataclass(frozen=True)
class ScenarioDefinition:
    schema_version: str
    scenario_id: str
    scenario_class: str
    primary: bool
    application_id: str
    transition_kinds: tuple[str, ...]
    ground_truth_fields: tuple[str, ...]
    applicable_baselines: tuple[str, ...]

    @classmethod
    def from_document(cls, document: dict[str, Any]) -> "ScenarioDefinition":
        validate_scenario_semantics(document)
        return cls(
            schema_version=document["schema_version"],
            scenario_id=document["scenario_id"],
            scenario_class=document["class"],
            primary=document["primary"],
            application_id=document["application_id"],
            transition_kinds=tuple(document["transition_kinds"]),
            ground_truth_fields=tuple(document["ground_truth_fields"]),
            applicable_baselines=tuple(document["applicable_baselines"]),
        )


@dataclass(frozen=True)
class GroundTruth:
    """Controller-owned record persisted separately from observer results."""

    schema_version: str
    run_id: str
    trial_id: str
    scenario_id: str
    scenario_class: str
    repetition: int
    seed: int
    random_delay_ms: int
    transition_ns: int
    transition_kind: str
    application_id: str
    recorded_at: str
    probe: str
    metadata: dict[str, Any]
    layer: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "trial_id": self.trial_id,
            "scenario_id": self.scenario_id,
            "scenario_class": self.scenario_class,
            "repetition": self.repetition,
            "seed": self.seed,
            "random_delay_ms": self.random_delay_ms,
            "transition_ns": self.transition_ns,
            "transition_kind": self.transition_kind,
            "application_id": self.application_id,
            "recorded_at": self.recorded_at,
            "probe": self.probe,
            "metadata": self.metadata,
            "layer": self.layer,
        }


class GroundTruthRecorder:
    """Append-only writer controlled exclusively by :class:`ScenarioController`."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.records: list[GroundTruth] = []

    def record(self, ground_truth: GroundTruth) -> None:
        if any(item.trial_id == ground_truth.trial_id for item in self.records):
            raise ValueError(f"duplicate ground-truth trial id: {ground_truth.trial_id}")
        self.records.append(ground_truth)
        with self.path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(ground_truth.as_dict(), sort_keys=True, separators=(",", ":")) + "\n")


class ControlledProbe:
    """A deterministic probe with separate truth and public observation APIs."""

    def __init__(self, definition: ScenarioDefinition, *, transition_ns: int, transition_kind: str, delay_ms: int, metadata: dict[str, Any]) -> None:
        self.definition = definition
        self._transition_ns = transition_ns
        self._transition_kind = transition_kind
        self._delay_ms = delay_ms
        self._metadata = dict(metadata)

    def truth_event(self) -> dict[str, Any]:
        return {
            "transition_ns": self._transition_ns,
            "transition_kind": self._transition_kind,
            "application_id": self.definition.application_id,
            "metadata": dict(self._metadata),
        }

    def state_at(self, now_ns: int) -> dict[str, Any]:
        if now_ns < self._transition_ns:
            return {"ready": False, "application_id": self.definition.application_id}
        return {
            "ready": True,
            "application_id": self.definition.application_id,
            "kind": self._transition_kind,
            "subject": self._metadata.get("subject", self.definition.scenario_id),
            "localization": self._metadata.get("localization"),
        }

    def filesystem_events(self, now_ns: int) -> tuple[dict[str, Any], ...]:
        if self.definition.scenario_class not in {"file_artifact_transition", "render_export"}:
            return ()
        if now_ns < self._transition_ns - 120_000_000:
            return ()
        count = int(self._metadata.get("raw_write_count", 4))
        return tuple({"path": self._metadata.get("path", self.definition.scenario_id), "kind": "raw.write", "index": index} for index in range(count))

    def stable_artifact(self, now_ns: int) -> dict[str, Any] | None:
        if self.definition.scenario_class not in {"file_artifact_transition", "render_export"} or now_ns < self._transition_ns:
            return None
        return {
            "path": self._metadata.get("path", self.definition.scenario_id),
            "digest": self._metadata.get("digest", "sha256:controlled-probe"),
            "application_id": self.definition.application_id,
            "kind": self._transition_kind,
            "subject": self._metadata.get("subject", self.definition.scenario_id),
        }

    def ordinary_notification(self, now_ns: int, template: str) -> str | None:
        if now_ns < self._transition_ns:
            return None
        plain_status = {
            "job.completed": "completed", "job.failed": "failed", "artifact.available": "artifact available",
            "file.modified": "file changed", "dialog.appeared": "dialog appeared", "operation.available": "operation available",
            "process.crashed": "crashed", "process.restarted": "restarted",
        }.get(self._transition_kind, "transition observed")
        return template.format(application=self.definition.application_id, plain_status_text=plain_status)

    def notification_delivery(self, deadline_ns: int, template: str) -> tuple[str, int] | None:
        receipt_ns = self._transition_ns
        if receipt_ns > deadline_ns:
            return None
        notification = self.ordinary_notification(receipt_ns, template)
        return (notification, receipt_ns) if notification is not None else None

    def asw_signal(self, now_ns: int) -> dict[str, Any] | None:
        if now_ns < self._transition_ns:
            return None
        return {
            "schema_version": "asw.signal.v1",
            "signal_id": f"signal_{self.definition.scenario_id}_{self._delay_ms}",
            "application_id": self.definition.application_id,
            "kind": self._transition_kind,
            "category": self._transition_kind.split(".", 1)[0],
            "subject": self._metadata.get("subject", self.definition.scenario_id),
            "frontier": {"journal_sequence": self._delay_ms, "runtime_epoch": "controlled-probe"},
        }

    def asw_delivery(self, deadline_ns: int) -> tuple[int, dict[str, Any]] | None:
        received_ns = self._transition_ns
        signal = self.asw_signal(received_ns) if received_ns <= deadline_ns else None
        return (received_ns, signal) if signal is not None else None

    def source_event(self, observed_at: str) -> dict[str, Any]:
        kind = self._transition_kind
        adapter = "filesystem" if self.definition.scenario_class == "file_artifact_transition" else "application"
        if kind.startswith("job."):
            subject = {"kind": "job", "value": {"job_id": f"job:{self.definition.scenario_id}"}}
        elif kind.startswith("process."):
            subject = {"kind": "process", "value": {"pid": 4242, "executable": "controlled-probe.exe"}}
        elif kind in {"dialog.appeared", "operation.available"}:
            subject = {"kind": "ui_element", "value": {"automation_id": f"uia:{self.definition.scenario_id}"}}
        elif kind == "artifact.available":
            subject = {"kind": "artifact", "value": {"path": self._metadata.get("path", self.definition.scenario_id)}}
        else:
            subject = {"kind": "path", "value": {"path": self._metadata.get("path", self.definition.scenario_id)}}
        return {
            "schema_version": "asw.event.v1", "event_id": f"evt_{self.definition.scenario_id}_{self._delay_ms}",
            "type": kind, "application_id": self.definition.application_id, "observed_at": observed_at,
            "source": {"adapter": adapter, "source_id": f"app-source:{self.definition.application_id}", "source_epoch": "controlled-probe-epoch", "source_sequence": 1, "reliability": "authoritative"},
            "subject": subject, "operation": {"operation_id": None, "kind": None, "status": None},
            "payload": {} if adapter == "filesystem" else {"adapter_contract": "controlled-evaluation.v1"},
            "frontier": {"schema_version": "asw.frontier.v1", "journal_sequence": self._delay_ms, "runtime_epoch": "controlled-probe-runtime", "source_frontiers": {}, "reducer_policy_version": "asw.reducer.v1"},
        }


class JobProbe(ControlledProbe):
    pass


class FileProbe(ControlledProbe):
    pass


class UIProbe(ControlledProbe):
    pass


class RenderExportProbe(FileProbe):
    pass


class CrashRestartProbe(ControlledProbe):
    pass


class ScenarioSurface:
    """Public observer surface for one deterministic scenario timeline.

    Its methods expose only the observations permitted by a baseline contract.
    The transition time and expected kind are intentionally not public
    attributes; they become observable only through the normal surface after
    the controlled transition occurs.
    """

    __slots__ = (
        "_definition", "_probe", "_application_id",
    )

    def __init__(
        self,
        definition: ScenarioDefinition,
        *, probe: ControlledProbe,
    ) -> None:
        self._definition = definition
        self._probe = probe
        self._application_id = definition.application_id

    @property
    def scenario_id(self) -> str:
        return self._definition.scenario_id

    @property
    def scenario_class(self) -> str:
        return self._definition.scenario_class

    @property
    def application_id(self) -> str:
        return self._application_id

    @property
    def applicable_baselines(self) -> tuple[str, ...]:
        return self._definition.applicable_baselines

    @property
    def transition_kinds(self) -> tuple[str, ...]:
        return self._definition.transition_kinds

    @property
    def probe_name(self) -> str:
        return self._probe.__class__.__name__

    def query_state(self, now_ns: int) -> dict[str, Any]:
        """Polling/repeated-observation contract for process/file/UI state."""

        return self._probe.state_at(now_ns)

    def filesystem_events(self, now_ns: int) -> tuple[dict[str, Any], ...]:
        """Raw watcher contract; stable useful recognition follows the burst."""

        return self._probe.filesystem_events(now_ns)

    def stable_artifact(self, now_ns: int) -> dict[str, Any] | None:
        return self._probe.stable_artifact(now_ns)

    def ordinary_notification(self, now_ns: int, template: str) -> str | None:
        """Frozen plain-text notification with no structured ASW metadata."""

        return self._probe.ordinary_notification(now_ns, template)

    def notification_delivery(self, deadline_ns: int, template: str) -> tuple[str, int] | None:
        """Wait on the ordinary notification channel and return receipt time."""

        return self._probe.notification_delivery(deadline_ns, template)

    def asw_signal(self, now_ns: int) -> dict[str, Any] | None:
        """Structured signal exposed through the adapter's public interface."""

        return self._probe.asw_signal(now_ns)

    def asw_delivery(self, deadline_ns: int) -> tuple[int, dict[str, Any]] | None:
        """Wait on the structured public signal stream without exposing GT."""

        return self._probe.asw_delivery(deadline_ns)

    def source_event(self, observed_at: str) -> dict[str, Any]:
        """Build the controlled probe event delivered through a public ASW source.

        This is probe output, not the independent ground-truth record.  The
        controller can therefore feed the same transition into the committed
        ASW service without giving observers access to the recorder.
        """

        return self._probe.source_event(observed_at)

    def continuation_target(self) -> dict[str, Any]:
        """Target metadata consumed by the scripted continuation agent."""

        return {
            "application_id": self._application_id,
            "subject": f"subject:{self.scenario_id}",
        }


def _stable_trial_seed(run_seed: int, scenario_id: str, repetition: int, layer: str) -> int:
    material = f"{run_seed}:{scenario_id}:{repetition}:{layer}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def _probe_for(definition: ScenarioDefinition, *, transition_ns: int, delay_ms: int) -> tuple[str, dict[str, Any], ControlledProbe]:
    probe_by_class = {
        "job_completion": "job_probe",
        "file_artifact_transition": "file_probe",
        "ui_transition": "ui_probe",
        "render_export": "job_probe:render_export",
        "process_crash_restart": "crash_probe",
    }
    metadata: dict[str, Any] = {
        "subject": f"subject:{definition.scenario_id}",
        "raw_write_count": 4 if definition.scenario_class in {"file_artifact_transition", "render_export"} else 0,
    }
    if definition.scenario_class in {"file_artifact_transition", "render_export"}:
        metadata["path"] = f"C:/ASW-Evaluation/{definition.scenario_id}.artifact"
        metadata["digest"] = f"sha256:{definition.scenario_id}"
    if definition.scenario_class == "ui_transition":
        metadata["localization"] = {
            "coordinate_space": "windows_virtual_screen_physical_px",
            "rectangle": {"left": 100, "top": 100, "right": 300, "bottom": 180},
            "runtime_id": [1, 2, 3],
        }
    probe_type = {
        "job_completion": JobProbe,
        "file_artifact_transition": FileProbe,
        "ui_transition": UIProbe,
        "render_export": RenderExportProbe,
        "process_crash_restart": CrashRestartProbe,
    }[definition.scenario_class]
    return probe_by_class[definition.scenario_class], metadata, probe_type(
        definition, transition_ns=transition_ns, transition_kind=definition.transition_kinds[0], delay_ms=delay_ms, metadata=metadata
    )


class ScenarioController:
    """Build fair, seeded trial timelines and record ground truth independently."""

    def __init__(self, *, run_id: str, seed: int, random_delay: dict[str, int], recorder: GroundTruthRecorder, recorded_at: str) -> None:
        self.run_id = run_id
        self.seed = seed
        self.random_delay = random_delay
        self.recorder = recorder
        self.recorded_at = recorded_at

    @staticmethod
    def load_definitions(directory: Path) -> list[ScenarioDefinition]:
        definitions: list[ScenarioDefinition] = []
        for path in sorted(directory.glob("*.json")):
            definitions.append(ScenarioDefinition.from_document(json.loads(path.read_text(encoding="utf-8"))))
        if not definitions:
            raise ValueError(f"no scenario manifests found in {directory}")
        return definitions

    def trial(self, definition: ScenarioDefinition, repetition: int, *, layer: str) -> tuple[ScenarioSurface, GroundTruth]:
        trial_seed = _stable_trial_seed(self.seed, definition.scenario_id, repetition, layer)
        rng = random.Random(trial_seed)
        delay_ms = rng.randint(self.random_delay["min"], self.random_delay["max"] - 1)
        transition_ns = delay_ms * 1_000_000
        probe, metadata, controlled_probe = _probe_for(definition, transition_ns=transition_ns, delay_ms=delay_ms)
        trial_id = f"{layer.lower()}-{definition.scenario_id}-{repetition}"
        ground_truth = GroundTruth(
            schema_version="asw.evaluation_ground_truth.v1",
            run_id=self.run_id,
            trial_id=trial_id,
            scenario_id=definition.scenario_id,
            scenario_class=definition.scenario_class,
            repetition=repetition,
            seed=trial_seed,
            random_delay_ms=delay_ms,
            transition_ns=controlled_probe.truth_event()["transition_ns"],
            transition_kind=controlled_probe.truth_event()["transition_kind"],
            application_id=definition.application_id,
            recorded_at=self.recorded_at,
            probe=probe,
            metadata=controlled_probe.truth_event()["metadata"],
            layer=layer,
        )
        self.recorder.record(ground_truth)
        surface = ScenarioSurface(
            definition, probe=controlled_probe,
        )
        return surface, ground_truth

    def condition_order(self, definition: ScenarioDefinition, repetition: int, *, layer: str, conditions: Iterable[str]) -> list[str]:
        order = list(conditions)
        rng = random.Random(_stable_trial_seed(self.seed, definition.scenario_id, repetition, layer) + 1)
        rng.shuffle(order)
        return order
