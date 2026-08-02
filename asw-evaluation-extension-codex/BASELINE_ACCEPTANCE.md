# Accepted ASW Core Baseline

This extension begins **after** the ASW RFC 0001 implementation hard gate and Windows 11 runtime qualification.

The fresh agent must verify that the committed target repository contains its corresponding baseline evidence files before running this extension. Once verified, the following areas are accepted and are not part of Phase 8 implementation work:

- GUI-first product surfaces;
- filesystem observation and settling;
- process/job runtime transitions;
- UI Automation window/dialog/control transitions and physical-pixel coordinates;
- application/diagnostic adapter constraints;
- deterministic canonical signal reduction;
- subscriber/access semantics;
- append-only journal, frontier, replay, and rebuild behavior;
- native Windows App SDK delivery;
- bounded local agent API, stream/resume, grant enforcement/revocation;
- degradation/reconciliation;
- valid/invalid contract fixtures and semantic fail-closed coverage.

The prior runtime qualification explicitly did **not** claim a comparative target-application evaluation. That unexecuted comparison is the reason this package exists.

## Baseline verification only

At startup, record:

- repository commit SHA;
- clean/dirty worktree status;
- path to the committed MVP checklist;
- path to the committed Windows runtime qualification record;
- ASW package/application version if available.

Do not rerun the entire core qualification unless an evaluation scenario itself exposes a contradiction.
