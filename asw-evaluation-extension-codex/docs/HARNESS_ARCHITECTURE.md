# Harness Architecture

## Components

```text
Scenario Controller
    ├─ Ground-truth recorder
    ├─ Probe process / UI / filesystem actor
    └─ Condition launcher
             ├─ polling observer
             ├─ filesystem-watch observer
             ├─ ordinary-notification observer
             ├─ repeated-observation observer
             └─ ASW observer
                    ↓
             normalized TrialResult
                    ↓
             immutable raw JSONL
                    ↓
             deterministic aggregator
```

## Scenario controller

The controller owns scenario state and timestamps. Use a monotonic high-resolution clock for latency calculations and wall-clock timestamps only for human traceability.

Every trial receives a unique seed/id. Randomized delays MAY be used to prevent fixed-timing shortcuts, but the seed and generated delay MUST be recorded.

## Probe applications

Prefer tiny controlled Windows probes over third-party apps:

- `job_probe`: success/failure exit and optional artifact output;
- `file_probe`: burst writes then stable transition;
- `ui_probe`: window + delayed modal/control availability;
- `crash_probe`: normal start followed by controlled abnormal termination/restart.

The probe writes ground truth to a controller-owned channel that benchmark observers cannot access.

## ASW adapter

Use the existing ASW service/agent interfaces. Do not call reducer internals or read the authoritative journal directly if normal consumers would not.

## Raw results

Raw trial output is append-only JSONL. Aggregated CSV/JSON/Markdown are derived and rebuildable.
