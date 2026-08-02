from __future__ import annotations

import json
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from asw.contracts import ContractError
from asw.defaults import mvp_policy
from asw.service import ASWService
from asw.sources import FileSettler, SettleProfile, SourceAdapter, WindowsObservationRuntime

ROOT = Path(__file__).resolve().parents[1]


def fixture(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / "valid" / name).read_text(encoding="utf-8"))


class SourceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.service = ASWService(Path(self.temp.name) / "journal.jsonl", mvp_policy())
        auth = fixture("observation-authorization.json")
        auth["scopes"] = [
            {"application_id": "app.visual-studio", "source_id": "fs:source", "source_kind": "filesystem", "filesystem_roots": ["C:\\workspace"], "executable_names": [], "job_kinds": [], "uia_process_names": [], "adapter_contract": None},
            {"application_id": "app.visual-studio", "source_id": "proc:source", "source_kind": "process_job", "filesystem_roots": [], "executable_names": ["worker.exe"], "job_kinds": [], "uia_process_names": [], "adapter_contract": None},
            {"application_id": "app.visual-studio", "source_id": "job:source", "source_kind": "process_job", "filesystem_roots": [], "executable_names": [], "job_kinds": ["build"], "uia_process_names": [], "adapter_contract": None},
            {"application_id": "app.visual-studio", "source_id": "uia:source", "source_kind": "uia", "filesystem_roots": [], "executable_names": [], "job_kinds": [], "uia_process_names": ["app.exe"], "adapter_contract": None},
            {"application_id": "app.visual-studio", "source_id": "app:source", "source_kind": "application", "filesystem_roots": [], "executable_names": [], "job_kinds": [], "uia_process_names": [], "adapter_contract": "contract.app"},
            {"application_id": "app.visual-studio", "source_id": "diag:source", "source_kind": "diagnostic", "filesystem_roots": [], "executable_names": [], "job_kinds": [], "uia_process_names": [], "adapter_contract": "contract.diag"},
        ]
        self.service.record("observation_authorization", auth)
        self._register("fs:source", "filesystem", {"roots": ["C:\\workspace\\project"], "recursive": True})
        self._register("proc:source", "process", {"executable_names": ["WORKER.EXE"]})
        self._register("job:source", "job", {"job_kinds": ["build"]})
        self._register("uia:source", "uia", {"uia_process_names": ["APP.EXE"]})
        self._register("app:source", "application", {"adapter_contract": "contract.app"})
        self._register("diag:source", "diagnostic", {"adapter_contract": "contract.diag"})

    def tearDown(self) -> None: self.temp.cleanup()

    def _register(self, source_id: str, adapter: str, configuration: dict) -> None:
        self.service.record("source_registration", {"schema_version": "asw.source_registration.v1", "source_id": source_id, "adapter": adapter, "application_id": "app.visual-studio", "enabled": True, "authorization_id": "auth_vs", "configuration": configuration, "settle_profile": None, "registered_at": "2026-08-01T12:10:00-04:00"})

    def test_settler_requires_repeated_identical_observations(self) -> None:
        settler = FileSettler(SettleProfile(required_stable_observations=2))
        self.assertFalse(settler.stable([(1, 1), (2, 2)]))
        self.assertTrue(settler.stable([(1, 1), (1, 1)]))

    def test_unstable_artifact_is_not_journaled_or_signaled(self) -> None:
        adapter = SourceAdapter(self.service, "fs:source", "app.visual-studio", "filesystem")
        before = len(self.service.journal.records())
        adapter.filesystem("artifact.available", "C:\\workspace\\project\\out.bin", observations=[(1, 1)], artifact=True)
        self.assertEqual(len(self.service.journal.records()), before)
        adapter.filesystem("artifact.available", "C:\\workspace\\project\\out.bin", observations=[(1, 1), (1, 1)], artifact=True)
        self.assertEqual(len(self.service.journal.records()), before + 1)

    def test_degradation_requires_reconciliation_before_health_restoration(self) -> None:
        adapter = SourceAdapter(self.service, "fs:source", "app.visual-studio", "filesystem")
        adapter.degrade("overflow")
        self.assertEqual(self.service.source_health["fs:source"], "degraded")
        adapter.reconcile({"C:\\workspace\\project\\out.bin": {"size": 1}})
        self.assertEqual(self.service.source_health["fs:source"], "healthy")

    def test_process_job_and_uia_sources_are_bounded(self) -> None:
        SourceAdapter(self.service, "proc:source", "app.visual-studio", "process").process_job("process.started", "p1", executable_name="worker.exe")
        SourceAdapter(self.service, "job:source", "app.visual-studio", "job").process_job("job.completed", "j1", job_kind="build")
        coordinates = fixture("coordinate-payload.json")
        SourceAdapter(self.service, "uia:source", "app.visual-studio", "uia").uia("window.created", {"kind": "window", "value": {"name": "Editor"}}, coordinates, process_name="app.exe")
        invalid = dict(coordinates); invalid["coordinate_frame"] = "logical_pixels"
        with self.assertRaises(ContractError): SourceAdapter(self.service, "uia:source", "app.visual-studio", "uia").uia("window.created", {"kind": "window", "value": {}}, invalid, process_name="app.exe")

    def test_application_and_diagnostic_adapters_require_explicit_contracts(self) -> None:
        with self.assertRaises(ValueError):
            SourceAdapter(self.service, "app:source", "app.visual-studio", "application")
        with self.assertRaises(PermissionError):
            SourceAdapter(self.service, "app:source", "app.visual-studio", "application", "contract.other").application("file.saved", "op-1")
        SourceAdapter(self.service, "app:source", "app.visual-studio", "application", "contract.app").application("file.saved", "op-1")
        with self.assertRaises(ValueError):
            SourceAdapter(self.service, "diag:source", "app.visual-studio", "diagnostic")
        SourceAdapter(self.service, "diag:source", "app.visual-studio", "diagnostic", "contract.diag").diagnostic("diag-1")

    def test_windows_observation_runtime_is_wired_through_optional_provider_boundary(self) -> None:
        runtime = WindowsObservationRuntime(self.service)
        status = runtime.start()
        self.assertIn(status["fs:source"], {"no_existing_authorized_root", "running", "watchdog_unavailable", "watcher_start_failed"})
        self.assertIn(status["proc:source"], {"running", "provider_degraded", "process_provider_unavailable", "windows_process_provider_requires_windows"})
        self.assertIn(status["job:source"], {"provider_requires_executable_names", "running", "provider_degraded", "process_provider_unavailable", "windows_process_provider_requires_windows"})
        self.assertIn(status["uia:source"], {"running", "provider_degraded", "uiautomation_unavailable", "windows_uia_provider_requires_windows"})
        self.assertEqual(status, runtime.start())
        runtime.stop()

    @unittest.skipUnless(importlib.util.find_spec("psutil"), "psutil is optional")
    def test_live_process_and_job_providers_emit_start_and_exit_transitions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            probe = root / "asw_probe.exe"
            shutil.copyfile(sys.executable, probe)
            service = ASWService(root / "journal.jsonl", mvp_policy())
            authorization = fixture("observation-authorization.json")
            authorization["scopes"] = [
                {"application_id": "app.runtime", "source_id": "proc:live", "source_kind": "process_job", "filesystem_roots": [], "executable_names": [probe.name], "job_kinds": [], "uia_process_names": [], "adapter_contract": None},
                {"application_id": "app.runtime", "source_id": "job:live", "source_kind": "process_job", "filesystem_roots": [], "executable_names": [probe.name], "job_kinds": ["build"], "uia_process_names": [], "adapter_contract": None},
            ]
            service.record("observation_authorization", authorization)
            for source_id, adapter, configuration in (
                ("proc:live", "process", {"executable_names": [probe.name], "poll_interval_ms": 50}),
                ("job:live", "job", {"job_kinds": ["build"], "executable_names": [probe.name], "poll_interval_ms": 50}),
            ):
                service.record("source_registration", {
                    "schema_version": "asw.source_registration.v1", "source_id": source_id, "adapter": adapter,
                    "application_id": "app.runtime", "enabled": True, "authorization_id": authorization["authorization_id"],
                    "configuration": configuration, "settle_profile": None, "registered_at": "2026-08-02T00:00:00Z",
                })
            runtime = WindowsObservationRuntime(service)
            try:
                self.assertEqual(runtime.start()["proc:live"], "running")
                self.assertEqual(runtime.status["job:live"], "running")
                time.sleep(2.0)
                first = subprocess.Popen([str(probe), "-c", "import time; time.sleep(5.0); raise SystemExit(0)"])
                first.wait()
                second = subprocess.Popen([str(probe), "-c", "import time; time.sleep(5.0); raise SystemExit(7)"])
                second.wait()
                deadline = time.monotonic() + 6
                kinds = set()
                while time.monotonic() < deadline:
                    kinds.update(signal["kind"] for signal in service.signals)
                    if {"process.started", "process.completed", "process.failed", "job.completed", "job.failed"}.issubset(kinds):
                        break
                    time.sleep(0.05)
                self.assertTrue({"process.started", "process.completed", "process.failed"}.issubset(kinds), kinds)
                self.assertTrue({"job.completed", "job.failed"}.issubset(kinds), kinds)
            finally:
                runtime.stop()

    @unittest.skipUnless(os.name == "nt" and importlib.util.find_spec("uiautomation"), "Windows UIA runtime is optional")
    def test_live_uia_provider_emits_window_dialog_and_control_coordinates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            probe = root / "asw_uia_probe.exe"
            shutil.copyfile(sys.executable, probe)
            service = ASWService(root / "journal.jsonl", mvp_policy())
            authorization = fixture("observation-authorization.json")
            authorization["scopes"] = [{"application_id": "app.uia.runtime", "source_id": "uia:live", "source_kind": "uia", "filesystem_roots": [], "executable_names": [], "job_kinds": [], "uia_process_names": [probe.name], "adapter_contract": None}]
            service.record("observation_authorization", authorization)
            service.record("source_registration", {
                "schema_version": "asw.source_registration.v1", "source_id": "uia:live", "adapter": "uia",
                "application_id": "app.uia.runtime", "enabled": True, "authorization_id": authorization["authorization_id"],
                "configuration": {"uia_process_names": [probe.name], "uia_operation_names": ["ASW Button", "OK"], "poll_interval_ms": 200, "max_elements": 128, "max_depth": 4},
                "settle_profile": None, "registered_at": "2026-08-02T00:00:00Z",
            })
            runtime = WindowsObservationRuntime(service)
            code = 'import tkinter as tk; from tkinter import messagebox; root=tk.Tk(); root.title("ASW UIA Qualification"); b=tk.Button(root,text="ASW Button"); b.pack(); root.after(1200,lambda:messagebox.showinfo("ASW Dialog","qualification")); root.after(6500,root.destroy); root.mainloop()'
            child = None
            try:
                self.assertEqual(runtime.start()["uia:live"], "running")
                child = subprocess.Popen([str(probe), "-c", code])
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline:
                    kinds = {signal["kind"] for signal in service.signals}
                    if {"window.created", "dialog.appeared", "operation.available"}.issubset(kinds):
                        break
                    time.sleep(0.1)
                self.assertTrue({"window.created", "dialog.appeared", "operation.available"}.issubset(kinds), kinds)
                events = [item["record"] for item in service.journal.records() if item["record_kind"] == "event"]
                coordinates = [event["payload"]["coordinates"] for event in events if event["type"] in {"window.created", "dialog.appeared", "operation.available"}]
                self.assertTrue(coordinates)
                self.assertTrue(all(item["coordinate_frame"] == "windows_virtual_screen_physical_px" for item in coordinates))
                self.assertTrue(all(item["virtual_screen_rect"]["width"] > 0 and item["virtual_screen_rect"]["height"] > 0 for item in coordinates))
                self.assertTrue(all(item["ephemeral_correlation"]["uia_runtime_id"] or item["ephemeral_correlation"]["hwnd"] for item in coordinates))
            finally:
                if child is not None:
                    child.terminate()
                    try:
                        child.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        child.kill()
                runtime.stop()

    @unittest.skipUnless(importlib.util.find_spec("watchdog"), "watchdog is optional")
    def test_filesystem_runtime_emits_from_a_real_authorized_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            service = ASWService(root / "journal.jsonl", mvp_policy())
            authorization = fixture("observation-authorization.json")
            authorization["scopes"] = [authorization["scopes"][0]]
            authorization["scopes"][0]["source_id"] = "fs:live"
            authorization["scopes"][0]["filesystem_roots"] = [str(root)]
            service.record("observation_authorization", authorization)
            service.record("source_registration", {
                "schema_version": "asw.source_registration.v1",
                "source_id": "fs:live",
                "adapter": "filesystem",
                "application_id": "app.visual-studio",
                "enabled": True,
                "authorization_id": authorization["authorization_id"],
                "configuration": {"roots": [str(root)], "recursive": True},
                "settle_profile": {
                    "initial_delay_ms": 0,
                    "poll_interval_ms": 50,
                    "required_stable_observations": 2,
                    "maximum_settle_ms": 3000,
                    "stability_mode": "metadata",
                },
                "registered_at": "2026-08-02T00:00:00Z",
            })
            runtime = WindowsObservationRuntime(service)
            try:
                self.assertEqual(runtime.start()["fs:live"], "running")
                (root / "observed.txt").write_text("settled", encoding="utf-8")
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline and not service.signals:
                    time.sleep(0.05)
                self.assertTrue(service.signals)
                self.assertIn(service.signals[0]["kind"], {"file.created", "file.modified"})
            finally:
                runtime.stop()


if __name__ == "__main__": unittest.main()
