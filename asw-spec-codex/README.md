# Application Signals for Windows (ASW) — RFC 0001 Codex Package

This package is the implementation contract for **RFC 0001: Application Signals for Windows**. ASW is a GUI-first Windows 11 service that observes user-authorized application activity, normalizes eligible observations into structured **signals**, groups signal history by application, lets both users and agents subscribe to selected applications and signal categories, delivers user subscriptions through the ASW activity UI and optionally Windows App SDK notifications, and exposes agent subscriptions through a bounded local structured stream.

## Package authority

1. `RFC-0001.md` is the normative product and behavior specification.
2. `schemas/` is the normative machine-readable contract surface.
3. `docs/` resolves implementation details intentionally compressed in the RFC.
4. `fixtures/valid/` and `fixtures/invalid/` define schema and fail-closed examples.
5. `fixtures/evaluation/` defines comparative evaluation fixtures.
6. `checklists/MVP_COMPLETION_CHECKLIST.md` is a hard release gate.

If two normative artifacts conflict, implementation MUST stop and the specification MUST be reconciled before behavior is added.

## Product hierarchy

```text
Primary user interface:    Windows GUI
Agent interface:           local structured subscription/read protocol
Developer interface:       optional diagnostic CLI
Persistence:               append-only JSONL journal + rebuildable indexes
Windows notifications:     optional user delivery channel
```

The CLI is not the normal user interface and is not the normal agent interface.

## Windows runtime dependencies

The optional filesystem, process/job, UI Automation, and Windows App SDK
delivery bridges use the packages listed in `requirements-windows.txt`. Install
the Windows App Runtime through the host/application deployment separately (the
installer must provide the Main, Singleton, and DDLM packages); the Python
projection does not include that OS runtime. Process/job observation is limited
to registered executable identities and uses a retained native process handle
for exit status. UI Automation observation is limited to registered process
names and a bounded control tree. If the host cannot bootstrap an installed
runtime, ASW keeps canonical signals and records delivery failure rather than
treating a notification as signal authority.

## Authority model

```text
User-authorized observation scope
            ↓
      source observations
            ↓
   deterministic reduction
            ↓
        signal history
       /              \
user subscriptions   agent subscriptions
       ↓                  ↓
GUI / Windows         structured stream
notifications         + replay cursor
```

A subscription filters delivery or reading. It does **not** create source observations or authorize additional observation. An agent subscription MUST remain within both the user-authorized observation scope and the agent's user-issued access grant.

## Frontier in one sentence

A frontier is the ASW-local replay and ordering boundary for observations and signal reducer outputs. It may cite source-specific cursors, epochs, snapshots, or reconciliation identities, but RFC 0001 does not require CRDT state vectors or distributed shared-state frontiers.

## Suggested implementation order

1. Validate every schema and fixture.
2. Implement append-only JSONL journal and durable `journal_sequence`.
3. Implement frontier, restart, and source-epoch semantics.
4. Implement deterministic event-to-signal reducer and replay.
5. Implement application identity and grouping.
6. Implement user-controlled observation authorization.
7. Implement filesystem adapter plus settle/reconciliation.
8. Implement process/job adapter.
9. Implement registered UI Automation adapter.
10. Implement application/diagnostic adapter contracts.
11. Implement subscriber, subscription, and agent-access enforcement.
12. Implement the GUI activity and subscription surfaces.
13. Implement Windows App SDK notification delivery.
14. Implement the local agent stream/read interface.
15. Add the optional developer CLI only where useful for diagnostics/conformance.
16. Pass the hard MVP gate and comparative evaluation fixtures.
