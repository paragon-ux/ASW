# ASW Phase 8 — Controlled Evaluation & MVP Validation Extension

This package is an **additive extension** to a committed ASW RFC 0001 implementation. It does not reopen the completed ASW core. Its only purpose is to build and execute the controlled comparative evaluation that was not represented as complete by the Windows 11 runtime-qualification record.

## Entry condition

The target repository is expected to already contain committed evidence equivalent to:

- `checklists/MVP_COMPLETION_CHECKLIST.md` with the implementation hard gate complete; and
- `docs/RUNTIME_QUALIFICATION_2026-08-02.md` showing Windows 11 runtime verification for native Windows App SDK delivery, process/job observation, UI Automation/coordinates, GUI journey, agent stream/revocation, and degradation/reconciliation.

The fresh agent should verify those files and a clean committed baseline, then treat them as **accepted prerequisites**, not work to repeat.

## Scope

This extension adds only:

1. a deterministic scenario harness with independent ground truth;
2. executable baseline observers;
3. ASW comparative adapters using the already-implemented public/service surfaces;
4. metrics collection and reproducible run manifests;
5. a small agent-continuation experiment designed to minimize model usage;
6. persisted comparative results;
7. a new evaluation hard gate determining whether the ASW MVP proposition is supported.

## Core protection rule

Do not modify ASW core implementation, existing RFC schemas, or the already-completed implementation checklist during normal extension work.

Preferred additive locations in the target repository are:

```text
evaluation/
  harness/
  baselines/
  consumers/
  scenarios/
  results/
  tests/

docs/
  EVALUATION_RESULTS_<date>.md
checklists/
  MVP_EVALUATION_COMPLETION_CHECKLIST.md
```

If evaluation reveals a reproducible defect in previously completed ASW behavior, record it as an evaluation blocker with a minimal reproducer. Do not silently refactor or reopen the core from this extension.

## Evaluation layers

### Layer A — deterministic systems comparison

Runs without an LLM. It compares ASW with all required baselines using known scenario ground truth and measures detection, latency, observation count, duplicates, misses, and attribution.

### Layer B — bounded agent continuation comparison

Runs only after Layer A passes integrity checks. To control usage, it compares ASW against the **best eligible non-ASW baseline selected by a preregistered deterministic rule from Layer A**, rather than running every model against every baseline.

The agent layer measures whether structured signals reduce continuation/tool cost without reducing correctness.

## Normative order

1. `AGENTS.md`
2. `PHASE-8-EVALUATION.md`
3. `docs/HARNESS_ARCHITECTURE.md`
4. `docs/SCENARIOS.md`
5. `docs/BASELINES.md`
6. `docs/METRICS_AND_THRESHOLDS.md`
7. `docs/RUN_PROTOCOL.md`
8. `schemas/`
9. `fixtures/`
10. `checklists/MVP_EVALUATION_COMPLETION_CHECKLIST.md`
11. `KICKOFF_PROMPT.md`
