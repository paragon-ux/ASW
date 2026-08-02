# Application Signals for Windows

This workspace contains the RFC 0001 MVP for **Application Signals for
Windows (ASW)**, a GUI-first Windows 11 service for observing authorized
application activity, reducing observations into canonical signals, and
exposing bounded user and agent subscriptions.

## Project package

The implementation package is [`asw-spec-codex`](./asw-spec-codex/), including
the RFC, schemas, fixtures, source adapters, GUI, agent interface, and
qualification evidence.

See the package [README](./asw-spec-codex/README.md) and the
[MVP completion checklist](./asw-spec-codex/checklists/MVP_COMPLETION_CHECKLIST.md)
for implementation details and verification status.

## Quick verification

From the package directory:

```powershell
python validate_fixtures.py
python -m unittest discover -s tests -q
```

The optional Windows dependencies are listed in
[`requirements-windows.txt`](./asw-spec-codex/requirements-windows.txt). The
Windows App Runtime is installed separately by the host deployment.
