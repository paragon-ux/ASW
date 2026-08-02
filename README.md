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

## Phase 8 evaluation

The additive [`asw-evaluation-extension-codex`](./asw-evaluation-extension-codex/)
package provides the controlled comparative harness that was not included in
the core runtime qualification. It uses independent ground truth, executable
non-ASW baselines, the committed ASW public/service interfaces, frozen run
profiles, deterministic aggregation, and a bounded continuation comparison.

The final Phase 8 MVP evaluation is `SUPPORTED` for the bounded RFC 0001
proposition. The completed [evaluation checklist](./asw-evaluation-extension-codex/checklists/MVP_EVALUATION_COMPLETION_CHECKLIST.md)
and [evidence report](./asw-evaluation-extension-codex/docs/EVALUATION_RESULTS_2026-08-02.md)
document the thresholds, exclusions, raw evidence, and final classification.

To reproduce the extension checks from its package directory:

```powershell
python -m evaluation.validate
python -m unittest discover -s evaluation/tests -q
python -m evaluation.validate --run evaluation/results/asw-mvp-eval-20260802-05
python -m evaluation.aggregate evaluation/results/asw-mvp-eval-20260802-05
```

## Quick verification

From the package directory:

```powershell
python validate_fixtures.py
python -m unittest discover -s tests -q
```

The optional Windows dependencies are listed in
[`requirements-windows.txt`](./asw-spec-codex/requirements-windows.txt). The
Windows App Runtime is installed separately by the host deployment.
