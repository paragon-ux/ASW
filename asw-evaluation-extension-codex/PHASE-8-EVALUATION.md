# Phase 8 — Controlled Evaluation Harness & MVP Validation

**Status:** Required extension gate before claiming the ASW MVP proposition is empirically supported.

## 1. Purpose

Phase 8 tests the proposition that ASW's structured application signals improve handling of asynchronous Windows application activity over obvious alternatives, especially by reducing repeated observation while preserving correct transition detection and continuation.

It is not a second implementation RFC. It does not redefine ASW semantics.

## 2. Primary hypothesis

Under controlled asynchronous Windows scenarios, ASW SHOULD reduce unnecessary observation/tool effort while maintaining or improving correct transition recognition and continuation compared with the strongest eligible non-ASW baseline.

## 3. Required scenario classes

The hard gate uses three primary classes:

1. registered background job completion/failure, optionally followed by artifact availability;
2. external file/artifact transition requiring recognition of a stable useful change;
3. registered UI transition: dialog/modal appearance or previously unavailable operation becoming available.

Two secondary coverage classes SHOULD also run if inexpensive:

4. render/export-style artifact production using the controlled job/artifact probe;
5. process crash/restart.

Synthetic probes are valid and preferred for the MVP because they provide controlled independent ground truth. Third-party applications are not required for the Phase 8 hard gate.

## 4. Evaluation layers

### 4.1 Layer A — deterministic systems benchmark

No model calls.

For every required scenario, execute each applicable baseline under the same scenario definition and ground-truth timeline. Record raw trial results.

### 4.2 Layer B — agent continuation benchmark

Use the fixed small run count in the frozen profile.

Compare ASW against exactly one non-ASW condition: the best eligible non-ASW baseline selected using the preregistered selection rule from Layer A.

This avoids spending model usage across baselines already shown to be inferior by deterministic measurement while still testing the product's agent-continuation purpose.

## 5. Independent ground truth

The scenario controller owns ground truth and MUST record transition identity and monotonic transition time independently of ASW and every baseline observer.

An observer MUST NOT define its own success condition.

## 6. Fairness

For a scenario run:

- all conditions receive the same task/scenario semantics;
- observers begin before the transition;
- polling/repeated-observation intervals are fixed in the profile;
- observation/tool budgets are fixed in the profile;
- ordinary notification text may contain only the information declared in the baseline contract;
- the ASW condition may consume only normal ASW signal/subscription interfaces;
- no condition reads another condition's private ground-truth log.

## 7. Required outputs

Persist:

- frozen evaluation profile;
- run manifest with software versions and commit SHA;
- scenario ground-truth records;
- raw per-trial results;
- aggregate summary;
- agent prompts/responses or normalized usage records where policy permits;
- final evidence report stating supported, unsupported, or inconclusive hypotheses.

## 8. Completion semantics

The Phase 8 checklist is a hard gate.

Passing the gate means the controlled experiment supports the declared MVP proposition at the preregistered thresholds.

Failing a threshold is a valid experimental result. Do not alter thresholds after seeing comparative results.
