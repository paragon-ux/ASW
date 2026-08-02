# Application Signals for Windows (ASW)

ASW is a GUI-first Windows 11 MVP that turns explicitly user-authorized
application observations into deterministic, structured signals. Users decide
what may be observed; subscriptions decide which existing signals are shown or
read; Windows notifications and the local agent endpoint are delivery surfaces,
not signal authority.

This directory is the Phase 9 publication and release surface staged beside
the normative implementation package. The implementation and schemas remain in
[`asw-spec-codex`](../asw-spec-codex/); the controlled evaluation remains in
[`asw-evaluation-extension-codex`](../asw-evaluation-extension-codex/).

## Status and evidence

The RFC 0001 MVP is MIT-licensed release candidate `0.2.0`. The accepted core commit is
`7d6e267c6e89cdcd8a71644c67c95d2ab4260330`; the accepted Phase 8 run is
`asw-mvp-eval-20260802-05`, classified `SUPPORTED`.

In the preregistered controlled RFC 0001 Windows MVP evaluation, ASW achieved
100% transition detection with 0% duplicate and false-positive useful-signal
rates. It reduced median observation effort by 50% versus the mechanically
selected `ordinary_notification` baseline in all three primary scenario
classes. The bounded continuation comparison retained 100% success and reduced
median observation calls and continuation latency by 50%.

These results apply only to the bounded controlled Windows MVP scenarios. They
do not establish universal application coverage, cross-platform behavior,
production-scale reliability, or universal benefit for arbitrary agents.

See the [Phase 8 report](evidence/EVALUATION_RESULTS_2026-08-02.md),
[runtime qualification](../asw-spec-codex/docs/RUNTIME_QUALIFICATION_2026-08-02.md),
and [normative RFC 0001](../asw-spec-codex/RFC-0001.md).

## How ASW works

```text
Observe (user authorization)
        -> observations/events
        -> deterministic canonical signals
        -> user or agent subscriptions
        -> Activity, Windows delivery, or bounded agent reads
```

The reducer is finite, versioned, deterministic, and reject-by-default.
Unsupported, unauthorized, invalid, hint-only, or degraded facts do not become
ordinary signals. An append-only JSONL journal is authoritative; indexes and
views are rebuildable projections.

## Requirements and installation

The tested runtime is Windows 11 Pro build 22000, 64-bit, with Python 3.11.9.
The Windows App Runtime 2.3.1 is installed separately by the host deployment.
Install the optional Python observation and delivery dependencies from
[`requirements-windows.txt`](../asw-spec-codex/requirements-windows.txt), then
follow [Installation](docs/INSTALLATION.md).

```powershell
Set-Location ..\asw-spec-codex
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-windows.txt
.\.venv\Scripts\python.exe main.py
```

The normal user surface is the GUI. The optional developer CLI is diagnostic
and conformance tooling; normal agent operation does not require it.

## First run

1. Open **Applications** and register the application identity you intend to
   observe.
2. Open **Sources & Permissions** and authorize the relevant folder,
   executable/job identity, UI Automation process, or explicit adapter
   contract.
3. Open **Subscriptions** and choose applications, categories, and user
   destinations. The current GUI leaves the optional `event_types` filter
   empty; agents may use that schema field through the structured API.
4. Watch **Activity** for signals grouped by application.
5. Use **Agents** only when a user-issued grant and bounded agent access are
   required.

The [quickstart](docs/QUICKSTART.md) and [user guide](docs/USER_GUIDE.md)
explain this journey in application-first language.

## Choose a guide

- New user: [installation](docs/INSTALLATION.md), [quickstart](docs/QUICKSTART.md),
  [user guide](docs/USER_GUIDE.md), and [known limitations](docs/KNOWN_LIMITATIONS.md).
- Agent integrator: [agent integration](docs/AGENT_INTEGRATION.md).
- Maintainer: [architecture](docs/ARCHITECTURE_OVERVIEW.md),
  [contributor guide](CONTRIBUTING.md), and [reproducibility](docs/EVALUATION_REPRODUCIBILITY.md).
- Security/privacy reviewer: [security and privacy](docs/SECURITY_AND_PRIVACY.md)
  and [SECURITY.md](SECURITY.md).
- Research reader: [whitepaper](docs/WHITEPAPER.md) and [claims/evidence matrix](docs/CLAIMS_AND_EVIDENCE.md).

## What ASW is not

ASW is not a cloud authorization service, remote multi-user access-control
system, general desktop sandbox, arbitrary screen interceptor, replacement for
UI Automation or application-native APIs, or a universal asynchronous-workflow
solution. It does not infer user intent or use a model in the deterministic
reducer. The secondary crash/restart probe recorded ASW `subject_accuracy =
0.0`; this is retained as a limitation rather than hidden.

## Development and release references

- [RFC 0001 implementation package](../asw-spec-codex/README.md)
- [MVP completion checklist](../asw-spec-codex/checklists/MVP_COMPLETION_CHECKLIST.md)
- [Phase 8 evaluation package](../asw-evaluation-extension-codex/README.md)
- [Phase 9 release checklist](checklists/RELEASE_READINESS_CHECKLIST.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Release and packaging audit](docs/RELEASE_AND_PACKAGING.md)
- [Changelog](CHANGELOG.md)
- [MIT License](LICENSE)
