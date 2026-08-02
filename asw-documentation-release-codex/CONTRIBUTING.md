# Contributing and development

ASW's normative behavior is defined by [RFC 0001](../asw-spec-codex/RFC-0001.md)
and its schemas. Documentation changes must preserve the distinction between
normative semantics, implemented behavior, runtime evidence, empirical
evidence, and limitations.

## Local checks

From `asw-spec-codex`:

```powershell
python validate_fixtures.py
python -m unittest discover -s tests -q
```

From this Phase 9 package:

```powershell
python validate_package.py
```

Review changed Markdown links and release-bound files for machine-specific
paths, tokens, local journals, caches, and generated output before publishing.

## Scope discipline

Do not change reducer semantics, journal/replay behavior, source behavior,
access-control semantics, GUI behavior, agent protocol behavior, or evaluation
thresholds as part of documentation cleanup. If documentation exposes a
reproducible core defect, record a minimal issue/reproducer and mark the
affected release item blocked rather than silently repairing product behavior.

Use the RFC and schemas as the canonical homes for normative details; link to
them instead of creating conflicting duplicate contracts in guides.

## Pull requests and releases

Explain the evidence for every material claim. Keep public examples on
placeholders. A release candidate must pass the [release readiness checklist](checklists/RELEASE_READINESS_CHECKLIST.md)
and must not create or push a tag automatically. The proposed MVP tag is
`v0.2.0`.
