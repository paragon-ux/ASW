"""Bounded, testable source adapters; OS watchers plug into these narrow intake methods."""

from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from collections import defaultdict, deque
from copy import deepcopy
from dataclasses import dataclass
from threading import Event, Lock, Thread
from typing import Any

from .contracts import validate
from .service import utc_now


_PROCESS_SNAPSHOT_LOCK = Lock()
_PROCESS_SNAPSHOT_AT = 0.0
_PROCESS_SNAPSHOT: tuple[dict[str, Any], ...] = ()


def _process_snapshot() -> tuple[dict[str, Any], ...]:
    """Return one short-lived native snapshot shared by process/job sources."""
    global _PROCESS_SNAPSHOT_AT, _PROCESS_SNAPSHOT
    import psutil

    now = time.monotonic()
    with _PROCESS_SNAPSHOT_LOCK:
        if now - _PROCESS_SNAPSHOT_AT < 0.15 and _PROCESS_SNAPSHOT:
            return _PROCESS_SNAPSHOT
        records: list[dict[str, Any]] = []
        try:
            for process in psutil.process_iter(["pid", "name", "ppid", "create_time"]):
                try:
                    info = dict(process.info)
                    if info.get("name") and info.get("create_time"):
                        records.append(info)
                except (psutil.Error, TypeError, ValueError):
                    continue
        except psutil.Error:
            records = []
        _PROCESS_SNAPSHOT = tuple(records)
        _PROCESS_SNAPSHOT_AT = now
        return _PROCESS_SNAPSHOT


@dataclass(frozen=True)
class SettleProfile:
    initial_delay_ms: int = 250
    poll_interval_ms: int = 100
    required_stable_observations: int = 2
    maximum_settle_ms: int = 5000
    stability_mode: str = "metadata"


class FileSettler:
    """Pure settle decision helper; watcher callbacks remain hints until stable."""

    def __init__(self, profile: SettleProfile | None = None) -> None:
        self.profile = profile or SettleProfile()

    def stable(self, observations: list[tuple[Any, ...]], elapsed_ms: int = 0) -> bool:
        required = self.profile.required_stable_observations
        return elapsed_ms <= self.profile.maximum_settle_ms and len(observations) >= required and len(set(observations[-required:])) == 1


class SourceAdapter:
    def __init__(self, service, source_id: str, application_id: str, adapter: str, contract: str | None = None) -> None:
        self.service, self.source_id, self.application_id, self.adapter = service, source_id, application_id, adapter
        registration = service.sources.get(source_id)
        if not registration or not registration["enabled"] or registration["application_id"] != application_id or registration["adapter"] != adapter:
            raise PermissionError("source adapter requires a matching enabled registration")
        if adapter in {"application", "diagnostic"} and not contract: raise ValueError("explicit adapter contract required")
        self.contract = contract
        profile = registration.get("settle_profile") or {}
        self.settler = FileSettler(SettleProfile(**{key: profile[key] for key in ("initial_delay_ms", "poll_interval_ms", "required_stable_observations", "maximum_settle_ms", "stability_mode") if key in profile}))
        self.registration = registration
        self.last_stable_snapshot: dict[str, Any] | None = None
        self.epoch, self.sequence = str(uuid.uuid4()), 0

    def _event(self, event_type: str, subject: dict[str, Any], reliability: str = "observed", payload: dict[str, Any] | None = None, reconciliation_id: str | None = None) -> dict[str, Any]:
        self.sequence += 1
        source_frontier = {"source_epoch": self.epoch, "source_sequence": self.sequence}
        if reconciliation_id: source_frontier["reconciliation_id"] = reconciliation_id
        return {"schema_version": "asw.event.v1", "event_id": "evt_" + uuid.uuid4().hex, "type": event_type,
            "application_id": self.application_id, "observed_at": utc_now(),
            "source": {"adapter": self.adapter, "source_id": self.source_id, "source_epoch": self.epoch,
                       "source_sequence": self.sequence, "reliability": reliability}, "subject": subject,
            "operation": {"operation_id": None, "kind": None, "status": None}, "payload": {**(payload or {}), **({"adapter_contract": self.contract} if self.contract else {})},
            "frontier": {"schema_version": "asw.frontier.v1", "journal_sequence": self.service.journal.sequence + 1,
                         "runtime_epoch": self.service.runtime_epoch, "source_frontiers": {self.source_id: source_frontier},
                         "reducer_policy_version": self.service.reducer.policy["policy_version"]}}

    def filesystem(self, event_type: str, path: str, *, observations: list[tuple[Any, ...]] | None = None, elapsed_ms: int = 0, settled: bool | None = None, artifact: bool = False) -> None:
        allowed = {"file.created", "file.modified", "file.deleted", "file.saved", "artifact.available"}
        if event_type not in allowed or artifact != (event_type == "artifact.available"): raise ValueError("invalid filesystem event type")
        if observations is None: return  # callers must provide the settle evidence; a boolean cannot bypass policy.
        if not self.settler.stable(observations, elapsed_ms): return
        self.service.emit_event(self._event(event_type, {"kind": "artifact" if artifact else "path", "value": {"path": path}}, "observed"))

    def degrade(self, reason: str) -> None:
        self.service.emit_event(self._event("source.degraded", {"kind": "source", "value": {"reason": reason}}, "observed"))

    def reconcile(self, snapshot: dict[str, Any]) -> None:
        if self.service.source_health.get(self.source_id) != "degraded": raise RuntimeError("source must be degraded before reconciliation")
        if not isinstance(snapshot, dict): raise TypeError("reconciliation requires a bounded source snapshot")
        digest = "sha256:" + hashlib.sha256(json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        reconciliation_id = "recon_" + hashlib.sha256((digest + self.source_id).encode()).hexdigest()[:24]
        previous = self.last_stable_snapshot or {}
        changes = sorted(set(previous) ^ set(snapshot))
        self.last_stable_snapshot = deepcopy(snapshot)
        self.epoch = str(uuid.uuid4())
        self.service.emit_event(self._event("source.reconciled", {"kind": "source", "value": {"snapshot_digest": digest}}, "observed", {"snapshot_digest": digest, "reconciliation_id": reconciliation_id, "changed_keys": changes}, reconciliation_id))

    def process_job(self, event_type: str, identifier: str, *, executable_name: str | None = None, job_kind: str | None = None, exit_code: int | None = None) -> None:
        if self.adapter not in {"process", "job"}: raise ValueError("process_job requires a process or job adapter")
        allowed = {"process.started", "process.completed", "process.failed", "process.crashed", "process.restarted"} if self.adapter == "process" else {"job.completed", "job.failed"}
        if event_type not in allowed: raise ValueError("invalid process/job event type")
        config = self.registration["configuration"]
        if self.adapter == "process" and (not executable_name or executable_name.casefold() not in {item.casefold() for item in config.get("executable_names", [])}): raise PermissionError("process identity is outside registration")
        if self.adapter == "job" and (not job_kind or job_kind not in config.get("job_kinds", [])): raise PermissionError("job kind is outside registration")
        payload = {"identifier": identifier}
        if executable_name: payload["executable_name"] = executable_name
        if job_kind: payload["job_kind"] = job_kind
        if exit_code is not None: payload["exit_code"] = exit_code
        self.service.emit_event(self._event(event_type, {"kind": "process" if self.adapter == "process" else "job", "value": {"id": identifier}}, "observed", payload))

    def application(self, event_type: str, operation_id: str, *, status: str = "completed") -> None:
        if self.adapter != "application": raise ValueError("application events require an application adapter")
        if event_type not in {"file.saved", "artifact.available", "process.crashed", "process.restarted", "job.completed", "job.failed", "dialog.appeared", "operation.available", "operation.completed", "diagnostic.changed", "shared_artifact.updated"}: raise ValueError("invalid application event type")
        if self.contract != self.registration["configuration"].get("adapter_contract"): raise PermissionError("application adapter contract does not match registration")
        event = self._event(event_type, {"kind": "operation", "value": {"operation_id": operation_id}}, "authoritative", {"operation_id": operation_id})
        event["operation"] = {"operation_id": operation_id, "kind": "application_operation", "status": status}
        self.service.emit_event(event)

    def diagnostic(self, diagnostic_id: str) -> None:
        if self.adapter != "diagnostic": raise ValueError("diagnostic events require a diagnostic adapter")
        if self.contract != self.registration["configuration"].get("adapter_contract"): raise PermissionError("diagnostic adapter contract does not match registration")
        self.service.emit_event(self._event("diagnostic.changed", {"kind": "diagnostic_set", "value": {"id": diagnostic_id}}, "authoritative"))

    def uia(self, event_type: str, subject: dict[str, Any], coordinates: dict[str, Any], *, process_name: str | None = None) -> None:
        if event_type not in {"window.created", "dialog.appeared", "operation.available"}: raise ValueError("invalid UI Automation event type")
        allowed_processes = {item.casefold() for item in self.registration["configuration"].get("uia_process_names", [])}
        if not process_name or process_name.casefold() not in allowed_processes: raise PermissionError("UI Automation process is outside registration")
        event = self._event(event_type, subject, "observed", {"coordinates": dict(coordinates), "process_name": process_name})
        # A live provider can omit the frontier while constructing a physical
        # coordinate payload.  Bind it to the exact event frontier before the
        # contract check so the coordinate evidence cannot drift from the
        # authoritative journal record.
        event["payload"]["coordinates"].setdefault("observed_frontier", event["frontier"])
        validate("coordinate-payload", event["payload"]["coordinates"])
        self.service.emit_event(event)


class _FilesystemWatchHandler:
    """Small watchdog callback adapter; callbacks remain hints until settled."""

    def __init__(self, adapter: SourceAdapter) -> None:
        self.adapter = adapter
        self.profile = adapter.settler.profile
        self._observations: dict[str, deque[tuple[Any, ...]]] = defaultdict(lambda: deque(maxlen=self.profile.required_stable_observations))
        self._first_seen: dict[str, float] = {}
        self._lock = Lock()

    def _observe(self, event_type: str, path: str) -> None:
        if not path or os.path.isdir(path):
            return
        try:
            stat = os.stat(path)
            observation = (stat.st_size, stat.st_mtime_ns)
        except OSError:
            observation = (None, None)
        now = time.monotonic()
        with self._lock:
            self._first_seen.setdefault(path, now)
            history = self._observations[path]
            history.append(observation)
            elapsed_ms = int((now - self._first_seen[path]) * 1000)
            observations = list(history)
        try:
            self.adapter.filesystem(event_type, path, observations=observations, elapsed_ms=elapsed_ms)
        except Exception:
            # A watcher callback must not take down the observer thread.  The
            # source remains fail-closed; the next explicit health event can
            # trigger reconciliation.
            try:
                self.adapter.degrade("watcher_callback_failed")
            except Exception:
                return

    def on_created(self, event) -> None:
        self._observe("file.created", event.src_path)

    def on_modified(self, event) -> None:
        self._observe("file.modified", event.src_path)

    def on_deleted(self, event) -> None:
        self._observe("file.deleted", event.src_path)


class _NativeProcessHandle:
    """Small ctypes boundary that keeps an observed process queryable at exit."""

    _WAIT_OBJECT_0 = 0
    _SYNCHRONIZE = 0x00100000
    _PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

    def __init__(self, pid: int) -> None:
        self.handle = None
        self._kernel32 = None
        if os.name != "nt":
            return
        try:
            import ctypes
            from ctypes import wintypes

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
            kernel32.OpenProcess.restype = wintypes.HANDLE
            kernel32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
            kernel32.GetExitCodeProcess.restype = wintypes.BOOL
            kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
            kernel32.WaitForSingleObject.restype = wintypes.DWORD
            kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
            kernel32.CloseHandle.restype = wintypes.BOOL
            self._kernel32 = kernel32
            self.handle = kernel32.OpenProcess(self._SYNCHRONIZE | self._PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        except Exception:
            self.handle = None
            self._kernel32 = None

    @property
    def available(self) -> bool:
        return self.handle is not None and self._kernel32 is not None

    def exit_code(self) -> int | None:
        if not self.available:
            return None
        import ctypes
        from ctypes import wintypes

        if self._kernel32.WaitForSingleObject(self.handle, 0) != self._WAIT_OBJECT_0:
            return None
        value = wintypes.DWORD()
        if not self._kernel32.GetExitCodeProcess(self.handle, ctypes.byref(value)):
            return None
        return int(value.value)

    def close(self) -> None:
        if self.available:
            try:
                self._kernel32.CloseHandle(self.handle)
            except Exception:
                pass
        self.handle = None


class _ProcessObservationProvider:
    """Poll only registered executable identities and retain real exit handles."""

    def __init__(self, runtime: "WindowsObservationRuntime", source: dict[str, Any]) -> None:
        self.runtime = runtime
        self.service = runtime.service
        self.source = source
        self.adapter = SourceAdapter(self.service, source["source_id"], source["application_id"], source["adapter"])
        self.stop_event = Event()
        self.thread: Thread | None = None
        self.last_error: str | None = None
        self.seen: dict[tuple[int, float], dict[str, Any]] = {}
        self.executable_names = {str(item).casefold() for item in source["configuration"].get("executable_names", [])}
        self.job_kinds = [str(item) for item in source["configuration"].get("job_kinds", [])]
        self.poll_interval = max(0.05, float(source["configuration"].get("poll_interval_ms", 200)) / 1000)

    @staticmethod
    def _identifier(pid: int, create_time: float) -> str:
        return f"pid:{pid}:{create_time:.6f}"

    def start(self) -> None:
        try:
            import psutil
        except Exception as error:
            raise RuntimeError("psutil_unavailable") from error
        if os.name != "nt":
            raise RuntimeError("windows_process_provider_requires_windows")
        self.thread = Thread(target=self._run, name=f"asw-{self.source['source_id']}", daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=2)
        for record in self.seen.values():
            record["handle"].close()
        self.seen.clear()

    def _snapshot(self) -> dict[tuple[int, float], dict[str, Any]]:
        current: dict[tuple[int, float], dict[str, Any]] = {}
        for info in _process_snapshot():
            try:
                name = str(info.get("name") or "")
                create_time = float(info.get("create_time") or 0.0)
                pid = int(info["pid"])
            except (KeyError, TypeError, ValueError):
                continue
            if not name or name.casefold() not in self.executable_names or not create_time:
                continue
            key = (pid, create_time)
            current[key] = {"pid": pid, "create_time": create_time, "name": name,
                            "ppid": info.get("ppid"), "handle": None}
        return current

    def poll_once(self) -> None:
        current = self._snapshot()
        for key, info in current.items():
            if key in self.seen:
                continue
            handle = _NativeProcessHandle(info["pid"])
            if not handle.available:
                self.runtime.status[self.source["source_id"]] = "provider_degraded"
                continue
            info["handle"] = handle
            self.seen[key] = info
            identifier = self._identifier(info["pid"], info["create_time"])
            if self.source["adapter"] == "process":
                self.adapter.process_job("process.started", identifier, executable_name=info["name"])

        for key in list(self.seen):
            if key in current:
                continue
            info = self.seen[key]
            exit_code = info["handle"].exit_code()
            if exit_code is None:
                # A transient process-table miss is not an exit fact.  Keep
                # the handle and wait for a confirmed signalled process.
                continue
            self.seen.pop(key, None)
            info["handle"].close()
            identifier = self._identifier(info["pid"], info["create_time"])
            if self.source["adapter"] == "process":
                self.adapter.process_job("process.completed" if exit_code == 0 else "process.failed", identifier,
                                         executable_name=info["name"], exit_code=exit_code)
            elif len(self.job_kinds) == 1:
                self.adapter.process_job("job.completed" if exit_code == 0 else "job.failed", identifier,
                                         executable_name=info["name"], job_kind=self.job_kinds[0], exit_code=exit_code)

    def _run(self) -> None:
        try:
            while not self.stop_event.is_set():
                try:
                    self.poll_once()
                except Exception as error:
                    self.last_error = f"{type(error).__name__}: {error}"[:256]
                    self.runtime.status[self.source["source_id"]] = "provider_degraded"
                self.stop_event.wait(self.poll_interval)
        finally:
            for record in self.seen.values():
                record["handle"].close()
            self.seen.clear()


class _UIAObservationProvider:
    """Bounded UIA polling with process filters and physical-pixel evidence."""

    def __init__(self, runtime: "WindowsObservationRuntime", source: dict[str, Any]) -> None:
        self.runtime = runtime
        self.service = runtime.service
        self.source = source
        self.adapter = SourceAdapter(self.service, source["source_id"], source["application_id"], "uia")
        config = source["configuration"]
        self.process_names = {str(item).casefold() for item in config.get("uia_process_names", [])}
        self.operation_names = {str(item).casefold() for item in config.get("uia_operation_names", [])}
        self.max_elements = max(1, min(512, int(config.get("max_elements", 256))))
        self.max_depth = max(1, min(8, int(config.get("max_depth", 4))))
        self.poll_interval = max(0.1, float(config.get("poll_interval_ms", 500)) / 1000)
        self.stop_event = Event()
        self.thread: Thread | None = None
        self.last_error: str | None = None
        self.seen_windows: dict[str, dict[str, Any]] = {}
        self.seen_controls: dict[str, dict[str, Any]] = {}

    def start(self) -> None:
        try:
            import uiautomation  # noqa: F401
        except Exception as error:
            raise RuntimeError("uiautomation_unavailable") from error
        if os.name != "nt":
            raise RuntimeError("windows_uia_provider_requires_windows")
        self.thread = Thread(target=self._run, name=f"asw-{self.source['source_id']}", daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=2)
        self.seen_windows.clear()
        self.seen_controls.clear()

    @staticmethod
    def _safe(control: Any, attribute: str, default: Any = None) -> Any:
        try:
            value = getattr(control, attribute)
            return value() if callable(value) else value
        except Exception:
            return default

    @classmethod
    def _rect(cls, control: Any) -> dict[str, int] | None:
        rect = cls._safe(control, "BoundingRectangle")
        if rect is None:
            return None
        try:
            left, top, right, bottom = int(rect.left), int(rect.top), int(rect.right), int(rect.bottom)
            return {"x": left, "y": top, "width": max(0, right - left), "height": max(0, bottom - top)}
        except Exception:
            return None

    @staticmethod
    def _process_name(pid: int) -> str | None:
        try:
            import psutil
            return psutil.Process(pid).name()
        except Exception:
            return None

    @staticmethod
    def _correlation(control: Any) -> tuple[str, str | None, int | None]:
        runtime_id = _UIAObservationProvider._safe(control, "GetRuntimeId")
        runtime = ".".join(str(item) for item in runtime_id) if runtime_id else None
        hwnd = _UIAObservationProvider._safe(control, "NativeWindowHandle")
        hwnd_text = hex(int(hwnd)) if hwnd else None
        pid = _UIAObservationProvider._safe(control, "ProcessId")
        return runtime or ("hwnd:" + hwnd_text if hwnd_text else "control:" + str(id(control))), hwnd_text, pid

    @staticmethod
    def _virtual_screen() -> dict[str, int]:
        import ctypes
        user32 = ctypes.windll.user32
        return {"x": int(user32.GetSystemMetrics(76)), "y": int(user32.GetSystemMetrics(77)),
                "width": int(user32.GetSystemMetrics(78)), "height": int(user32.GetSystemMetrics(79))}

    @classmethod
    def _coordinates(cls, window: Any, element: Any) -> dict[str, Any]:
        window_rect = cls._rect(window)
        element_rect = cls._rect(element)
        hwnd = cls._safe(window, "NativeWindowHandle") or cls._safe(element, "NativeWindowHandle")
        dpi = None
        if hwnd:
            try:
                import ctypes
                dpi = float(ctypes.windll.user32.GetDpiForWindow(int(hwnd))) / 96.0
            except Exception:
                dpi = None
        visibility = "unknown"
        offscreen = cls._safe(element, "IsOffscreen")
        if offscreen is True:
            visibility = "offscreen"
        elif offscreen is False:
            visibility = "visible"
        return {
            "schema_version": "asw.coordinate_payload.v1",
            "coordinate_frame": "windows_virtual_screen_physical_px",
            "monitor_id": None,
            "dpi_scale": dpi,
            "virtual_screen_rect": cls._virtual_screen(),
            "monitor_rect": None,
            "window_rect": window_rect,
            "element_rect": element_rect,
            "visibility": visibility,
            "enabled": cls._safe(element, "IsEnabled"),
            "focusable": cls._safe(element, "IsKeyboardFocusable"),
            "localization_confidence": "observed" if element_rect is not None else "partial",
            "ephemeral_correlation": {
                "uia_runtime_id": cls._correlation(element)[0],
                "hwnd": cls._correlation(element)[1],
            },
        }

    def _children(self, control: Any) -> list[Any]:
        try:
            return list(control.GetChildren())
        except Exception:
            return []

    def _walk(self, root: Any) -> list[tuple[Any, int]]:
        result: list[tuple[Any, int]] = []
        queue = [(root, 0)]
        while queue and len(result) < self.max_elements:
            control, depth = queue.pop(0)
            result.append((control, depth))
            if depth >= self.max_depth:
                continue
            queue.extend((child, depth + 1) for child in self._children(control)[: self.max_elements - len(result)])
        return result

    def poll_once(self) -> None:
        import uiautomation

        current_windows: dict[str, dict[str, Any]] = {}
        current_controls: dict[str, dict[str, Any]] = {}
        root = uiautomation.GetRootControl()
        for window in self._children(root):
            pid = self._safe(window, "ProcessId")
            process_name = self._process_name(int(pid)) if pid else None
            if not process_name or process_name.casefold() not in self.process_names:
                continue
            window_key, window_hwnd, _ = self._correlation(window)
            window_name = str(self._safe(window, "Name", ""))[:256]
            window_class = str(self._safe(window, "ClassName", ""))
            window_record = {"control": window, "process_name": process_name, "pid": pid, "name": window_name, "hwnd": window_hwnd}
            current_windows[window_key] = window_record
            if window_key not in self.seen_windows:
                window_event = "dialog.appeared" if window_class == "#32770" else "window.created"
                self.adapter.uia(window_event, {"kind": "window", "value": {"name": window_name, "process_id": pid, "hwnd": window_hwnd}},
                                  self._coordinates(window, window), process_name=process_name)
            for control, depth in self._walk(window):
                if control is window:
                    continue
                key, control_hwnd, control_pid = self._correlation(control)
                control_name = str(self._safe(control, "Name", ""))[:256]
                control_type = str(self._safe(control, "ControlTypeName", ""))[:128]
                control_record = {"control": control, "window": window, "process_name": process_name, "pid": control_pid or pid,
                                  "name": control_name, "control_type": control_type, "enabled": self._safe(control, "IsEnabled"),
                                  "hwnd": control_hwnd}
                current_controls[key] = control_record
                if control_type == "WindowControl" and key not in self.seen_controls and str(self._safe(control, "ClassName", "")) == "#32770":
                    self.adapter.uia("dialog.appeared", {"kind": "window", "value": {"name": control_name, "process_id": pid, "hwnd": control_hwnd}},
                                      self._coordinates(window, control), process_name=process_name)
                eligible_operation = bool(self.operation_names and control_name.casefold() in self.operation_names)
                if not self.operation_names:
                    eligible_operation = control_type in {"ButtonControl", "HyperlinkControl", "MenuItemControl"} and bool(self._safe(control, "AutomationId", ""))
                was_enabled = self.seen_controls.get(key, {}).get("enabled")
                if eligible_operation and bool(control_record["enabled"]) and (key not in self.seen_controls or was_enabled is False):
                    self.adapter.uia("operation.available", {"kind": "ui_element", "value": {"name": control_name, "control_type": control_type,
                                                                                              "automation_id": str(self._safe(control, "AutomationId", ""))[:256], "process_id": pid}},
                                      self._coordinates(window, control), process_name=process_name)
        self.seen_windows = current_windows
        self.seen_controls = current_controls

    def _run(self) -> None:
        initializer = None
        try:
            import uiautomation
            # UIA's COM apartment must be initialized on the polling thread;
            # using the package helper avoids cross-thread COM failures while
            # leaving the provider optional on non-Windows hosts.
            initializer = uiautomation.UIAutomationInitializerInThread()
            while not self.stop_event.is_set():
                try:
                    self.poll_once()
                except Exception as error:
                    self.last_error = f"{type(error).__name__}: {error}"[:256]
                    self.runtime.status[self.source["source_id"]] = "provider_degraded"
                self.stop_event.wait(self.poll_interval)
        finally:
            if initializer is not None:
                try:
                    initializer.Uninitialize()
                except Exception:
                    pass
            self.seen_windows.clear()
            self.seen_controls.clear()


class WindowsObservationRuntime:
    """Optional OS-provider runtime wired by the Windows bootstrap.

    Every provider is bounded by its persisted source registration.  The
    process/job provider uses a polling snapshot only to discover registered
    executable identities, then holds a native query handle until exit so the
    completion/failure fact is based on the actual exit code.  UIA is likewise
    a bounded polling provider over explicitly authorized process names and a
    capped control tree; it never broadens observation to arbitrary windows.
    """

    def __init__(self, service) -> None:
        self.service = service
        self.observers: list[Any] = []
        self.providers: list[Any] = []
        self.status: dict[str, str] = {}
        self._started = False

    def start(self) -> dict[str, str]:
        if self._started:
            return dict(self.status)
        self._started = True
        for source in self.service.sources.values():
            if not source["enabled"]:
                continue
            if source["adapter"] in {"process", "job"}:
                config = source["configuration"]
                executable_names = config.get("executable_names", [])
                job_kinds = config.get("job_kinds", [])
                if not executable_names:
                    self.status[source["source_id"]] = "provider_requires_executable_names"
                    continue
                if source["adapter"] == "job" and len(job_kinds) != 1:
                    self.status[source["source_id"]] = "provider_requires_single_job_kind"
                    continue
                try:
                    provider = _ProcessObservationProvider(self, source)
                    provider.start()
                    self.providers.append(provider)
                    self.status[source["source_id"]] = "running"
                except Exception as error:
                    self.status[source["source_id"]] = str(error)[:128] or "process_provider_unavailable"
            elif source["adapter"] == "uia":
                try:
                    provider = _UIAObservationProvider(self, source)
                    provider.start()
                    self.providers.append(provider)
                    self.status[source["source_id"]] = "running"
                except Exception as error:
                    self.status[source["source_id"]] = str(error)[:128] or "uia_provider_unavailable"
        try:
            from watchdog.observers import Observer
        except Exception:
            for source in self.service.sources.values():
                if source["adapter"] == "filesystem" and source["enabled"]:
                    self.status[source["source_id"]] = "watchdog_unavailable"
            return dict(self.status)
        try:
            from watchdog.events import FileSystemEventHandler
        except Exception:
            for source in self.service.sources.values():
                if source["adapter"] == "filesystem" and source["enabled"]:
                    self.status[source["source_id"]] = "watchdog_unavailable"
            return dict(self.status)

        class Handler(FileSystemEventHandler, _FilesystemWatchHandler):
            def __init__(self, adapter: SourceAdapter) -> None:
                _FilesystemWatchHandler.__init__(self, adapter)

            def on_created(self, event) -> None:
                _FilesystemWatchHandler.on_created(self, event)

            def on_modified(self, event) -> None:
                _FilesystemWatchHandler.on_modified(self, event)

            def on_deleted(self, event) -> None:
                _FilesystemWatchHandler.on_deleted(self, event)

        for source in list(self.service.sources.values()):
            if source["adapter"] != "filesystem" or not source["enabled"]:
                continue
            try:
                adapter = SourceAdapter(self.service, source["source_id"], source["application_id"], "filesystem")
                observer = Observer()
                scheduled = 0
                for root in source["configuration"].get("roots", []):
                    if os.path.isdir(root):
                        observer.schedule(Handler(adapter), root, recursive=bool(source["configuration"].get("recursive", True)))
                        scheduled += 1
                if not scheduled:
                    self.status[source["source_id"]] = "no_existing_authorized_root"
                    continue
                observer.start()
                self.observers.append(observer)
                self.status[source["source_id"]] = "running"
            except Exception:
                self.status[source["source_id"]] = "watcher_start_failed"
        return dict(self.status)

    def stop(self) -> None:
        for provider in self.providers:
            try:
                provider.stop()
            except Exception:
                continue
        self.providers.clear()
        for observer in self.observers:
            try:
                observer.stop()
            except Exception:
                continue
        for observer in self.observers:
            try:
                observer.join(timeout=2)
            except Exception:
                continue
        self.observers.clear()
        self._started = False
