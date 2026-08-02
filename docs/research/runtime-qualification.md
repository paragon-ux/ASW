# ASW Windows 11 runtime qualification — 2026-08-02

This record captures the target-runtime checks performed after the host was
corrected to Windows 11 and the Windows App Runtime was installed. It is
evidence for the MVP checklist; it does not claim an unexecuted comparative
evaluation against third-party build/render/crash applications.

## Host and Windows App Runtime

Command: `Get-CimInstance Win32_OperatingSystem | Select Caption,Version,BuildNumber,OSArchitecture`

Observed:

```text
Caption        : Microsoft Windows 11 Pro
Version        : 10.0.22000
BuildNumber    : 22000
OSArchitecture : 64-bit
```

Current-user AppX enumeration reported these runtime components as `Status: Ok`:

```text
Microsoft.WinAppRuntime.DDLM.2.3.1.0-x6        2.3.1.0  X64
Microsoft.WinAppRuntime.DDLM.2.3.1.0-x8        2.3.1.0  X86
Microsoft.WindowsAppRuntime.2                  2.3.1.0  X64
Microsoft.WindowsAppRuntime.2                  2.3.1.0  X86
MicrosoftCorporationII.WinAppRuntime.Main.2    2.3.1.0  X64
MicrosoftCorporationII.WinAppRuntime.Singleton 8002.3.1.0 X64
```

The elevated `-AllUsers` package query is not permitted in this medium-integrity
desktop session; the current-user package inventory above is the runtime used by
the successful bootstrap and notification smoke.

The Python projections used for this run were:

```text
winui3-Microsoft.Windows.AppNotifications 3.2.1
winrt-runtime                              3.2.1
wasdk-Microsoft.Windows.ApplicationModel.DynamicDependency.Bootstrap 2.1.3
```

## Native Windows App SDK delivery

Command:

```text
python -c "from asw.delivery import WindowsAppSdkSender; ..."
```

Observed:

```text
manager_ready= True reason= None
show=ok
closed=ok
```

The sender initialized the dynamic dependency bootstrap, resolved
`AppNotificationManager`, registered it, and successfully called `Show()` with
an ASW ToastGeneric payload. The checklist item is `PASS — runtime verified`.

## Process/job observation

The live test
`tests/test_sources.py::test_live_process_and_job_providers_emit_start_and_exit_transitions`
copied the current Python executable to a uniquely named registered probe,
launched success and failure instances, and exercised two registered sources.
The provider retained native process query handles and produced all five
required transitions:

```text
process.started
process.completed
process.failed
job.completed
job.failed
```

The focused source suite result was:

```text
Ran 9 tests ... OK
```

The checklist item is `PASS — runtime verified` for eligible registrations. A
job source without an executable binding is reported as
`provider_requires_executable_names`; ASW does not infer an unregistered job
identity.

## UI Automation and physical coordinates

The live test
`tests/test_sources.py::test_live_uia_provider_emits_window_dialog_and_control_coordinates`
launched a registered Tk probe and observed a real top-level window, a native
modal dialog, and its enabled `OK` button:

```text
window.created
dialog.appeared
operation.available
```

The event payloads validated `windows_virtual_screen_physical_px`, a non-empty
virtual-screen rectangle, observed element rectangles, and an ephemeral UIA
runtime-id/window-handle correlation. A separate live run against the current
desktop also reported `explorer.exe` windows and controls. The checklist item is
`PASS — runtime verified`.

## GUI and end-to-end journey

The native Tk smoke instantiated `ASWWindow` and visited every required page:

```text
Activity
Subscriptions
Applications
Sources & Permissions
Agents
gui-smoke=ok
```

A live end-to-end run registered an authorized filesystem source, user and agent
subscriptions, and a user grant. A settled file transition produced a canonical
signal, native Windows delivery, agent list/read, an empty cursor resume, and a
403 after grant revocation:

```text
runtime {'fs:e2e': 'running'} native_sender True None
signals [('file.modified', 'app.e2e')]
deliveries [('delivered', 'windows_app_sdk')]
agent_list_count 1
agent_resume_count 0
agent_after_revoke_status 403
```

The loopback malformed-stream path also returns a bounded HTTP 400 after the
`ContractError` import fix (`tests/test_agent_api.py`).

## Degradation and reconciliation

The live filesystem watcher run observed a settled file before degradation,
blocked ordinary file events while degraded, restored `healthy` only after a
bounded reconciliation snapshot, and observed a subsequent settled file. The
platform-independent source tests additionally cover reconciliation evidence
and fail-closed behavior.

## Checklist classification

- Contract, reducer, journal, replay, authorization, subscription, GUI, agent,
  delivery, coordinate, fixture, and semantic items: `PASS — deterministic/platform-independent evidence` unless the checklist line cites a live runtime test above.
- Filesystem, process/job, UIA, native Windows App SDK, GUI, end-to-end, and
  degradation items exercised in this record: `PASS — runtime verified`.
- Comparative target-application evaluation: `BLOCKED — exact external/environmental reason`: no controlled build/render/export/crash scenario harness is available in this desktop session. The predeclared evaluation profile and fixture tests remain complete; no comparative run is represented as a pass.
- No implementation defect remains open from the target-runtime qualification.
