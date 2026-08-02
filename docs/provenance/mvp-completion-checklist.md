# MVP Completion Checklist — Hard Gate

RFC 0001 is not complete until **every applicable item below has passing evidence**.

## Product surfaces

- [x] Windows GUI is the primary user surface (`scripts/main.py`, `asw/gui.py`; Tk smoke check).
- [x] Activity groups signal history by application and sorts newest first by default (`tests/test_gui.py`).
- [x] Subscriptions UI lets users select applications/categories and delivery destinations (`asw/gui.py`).
- [x] Applications UI exposes observation state and source health (`asw/gui.py`).
- [x] Sources & Permissions UI controls observation authorization separately from subscriptions (`asw/gui.py`, `tests/test_semantics.py`).
- [x] Agents UI grants/revokes per-agent application/category access (`asw/gui.py`, `tests/test_semantics.py`).
- [x] Normal agent operation does not require the CLI (`tests/test_agent_api.py::test_loopback_agent_server_authenticates_and_dispatches_without_cli`).
- [x] Developer CLI, if present, is diagnostic/conformance tooling only (`scripts/validate_fixtures.py`; no product CLI).

## Observation and sources

- [x] Registered filesystem source emits settled file transitions only inside authorized roots (`tests/test_sources.py::test_filesystem_runtime_emits_from_a_real_authorized_root`, `tests/test_service.py::test_filesystem_event_path_outside_registered_root_fails_closed`).
- [x] Registered process/job source emits started/completed/failed transitions for eligible registrations. **PASS — runtime verified:** the Windows provider filters registered executable identities, retains native process query handles for exit status, and the live qualification test observes `process.started`, `process.completed`, `process.failed`, `job.completed`, and `job.failed` (`asw/sources.py`, `tests/test_sources.py::test_live_process_and_job_providers_emit_start_and_exit_transitions`, `docs/RUNTIME_QUALIFICATION_2026-08-02.md`). Job registrations without an executable binding remain explicitly reported as `provider_requires_executable_names` rather than being guessed.
- [x] Registered UIA source emits window/dialog/control transitions only for eligible authorized surfaces. **PASS — runtime verified:** the Windows provider initializes UIA on its polling thread, filters registered process names, bounds traversal, and the live qualification test observes `window.created`, `dialog.appeared`, and `operation.available` with physical-pixel coordinate evidence (`asw/sources.py`, `tests/test_sources.py::test_live_uia_provider_emits_window_dialog_and_control_coordinates`, `docs/RUNTIME_QUALIFICATION_2026-08-02.md`).
- [x] Explicit application/diagnostic adapters are required for application-specific/diagnostic semantics (`tests/test_sources.py::test_application_and_diagnostic_adapters_require_explicit_contracts`).
- [x] Source degradation triggers reconciliation before returning healthy (`tests/test_sources.py::test_degradation_requires_reconciliation_before_health_restoration`).
- [x] Unstable artifacts never become `artifact.available` (`tests/test_sources.py::test_unstable_artifact_is_not_journaled_or_signaled`, `tests/test_semantics.py::test_artifact_settle_timeout_cannot_emit`).
- [x] `diagnostic.changed` requires an explicit adapter/contract (`tests/test_sources.py::test_application_and_diagnostic_adapters_require_explicit_contracts`).

## Canonical signal model

- [x] Canonical object is `signal`; Windows notification is only a delivery channel (`asw/reducer.py`, `asw/delivery.py`).
- [x] Signals are created independently of subscription existence (`tests/test_semantics.py::test_subscription_presence_does_not_change_signal_history`).
- [x] Application identity is present or the system-defined unknown/system grouping is used (`tests/test_reducer.py::test_unattributed_events_have_required_unknown_group`).
- [x] Reducer is finite, deterministic, versioned, and reject-by-default (`tests/test_reducer.py`).
- [x] Reducer outputs are reproducible from journal inputs, frontier metadata, authorization, registrations, and policy version (`tests/test_service.py::test_journal_replay_and_rebuild_preserve_signals`, `tests/test_service.py::test_policy_versions_are_durable_inputs_for_replay`).
- [x] Invalid, unsupported, unauthorized, hint-only, or degraded facts fail closed for ordinary signals (`tests/test_semantics.py`).

## Subscribers and access

- [x] User and agent subscriber kinds are schema-validated (`scripts/validate_fixtures.py`, `schemas/subscriber.schema.json`).
- [x] Both users and agents can create application/category subscriptions (`tests/test_service.py`, `tests/test_semantics.py`).
- [x] Subscription changes do not alter canonical signal history (`tests/test_service.py::test_subscription_does_not_create_or_remove_signal_history`).
- [x] Agent subscriptions cannot expand observation authorization (`tests/test_service.py::test_administrative_grant_outside_authorization_cannot_read`).
- [x] Every agent read/stream is constrained by an active user-issued access grant (`tests/test_semantics.py::test_revoked_agent_grant_blocks_list_stream_resume_and_read`).
- [x] Agent subscription outside its grant is rejected (`tests/test_service.py::test_agent_subscription_cannot_exceed_grant`).
- [x] Grant revocation stops subsequent agent reads/streams (`tests/test_semantics.py::test_revoked_agent_grant_blocks_list_stream_resume_and_read`).

## Journal, frontier, replay

- [x] Authoritative JSONL journal replays deterministically (`tests/test_service.py::test_journal_replay_and_rebuild_preserve_signals`).
- [x] Durable `journal_sequence` survives restart (`tests/test_service.py::test_journal_replay_and_rebuild_preserve_signals`).
- [x] `runtime_epoch` and source epochs make discontinuities explicit (`asw/service.py`, `asw/sources.py`).
- [x] Replay cursors survive restart (`tests/test_service.py::test_replay_cursor_can_resume_after_service_restart`).
- [x] SQLite/index/cache deletion does not change semantic state (`tests/test_semantics.py::test_rebuilding_deleted_derived_indexes_preserves_signal_history`).
- [x] Replay never mutates files, processes, applications, or UI (`tests/test_service.py::test_replay_cursor_can_resume_after_service_restart`).

## Windows delivery and coordinates

- [x] Windows App SDK user notification delivery works where supported (`asw/delivery.py`; native `WindowsAppSdkSender` smoke showed `manager=True`/`show=ok`, and a service-level smoke recorded `signals=1` plus `deliveries=[('delivered','windows_app_sdk')]` after the Windows App Runtime 2.3.1 installer and `wasdk` bootstrap package were installed; injected transport and failure auditing are covered by `tests/test_agent_api.py`).
- [x] Delivery failure does not delete/invalidate the signal (`tests/test_agent_api.py::test_notification_platform_failure_is_audited_without_signal_mutation`).
- [x] Coordinate payload uses `windows_virtual_screen_physical_px` (`schemas/coordinate-payload.schema.json`, `fixtures/valid/coordinate-payload.json`).
- [x] Localization uncertainty and ephemeral UIA correlation are preserved (`schemas/coordinate-payload.schema.json`, `fixtures/valid/coordinate-payload.json`).

## Agent interface

- [x] Local structured API supports bounded list/read/stream/resume operations (`asw/agent_api.py`, `tests/test_agent_api.py`).
- [x] Responses include schema version and replay cursor/frontier where applicable (`tests/test_agent_api.py`).
- [x] Server-side access enforcement is tested for every agent operation (`tests/test_semantics.py::test_revoked_agent_grant_blocks_list_stream_resume_and_read`).

## Conformance and evaluation

- [x] Every valid fixture validates (`python scripts/validate_fixtures.py`).
- [x] Every invalid JSON fixture fails schema validation (`python scripts/validate_fixtures.py`).
- [x] Semantic fail-closed cases have executable tests (`tests/test_semantics.py`).
- [x] Comparative fixtures cover polling, file watching, ordinary notifications, repeated observation, and ASW signals (`fixtures/evaluation/profile.json`, `tests/test_evaluation.py`).
- [x] Evaluation profile is predeclared before comparative runs (`fixtures/evaluation/profile.json`, `tests/test_evaluation.py`).

## Environment-limited evidence

Comparative runs against real target applications were not executed because this
environment provides no controlled build/render/export/crash scenario harness.
The live Windows qualification did exercise a real registered process/job probe,
a real UIA window/modal/control probe, the filesystem watcher, native Windows App
SDK delivery, the GUI page journey, and the loopback agent grant/stream boundary.
The comparative evaluation fixture remains a predeclared deterministic profile;
no unexecuted target-application comparison is claimed as complete.
