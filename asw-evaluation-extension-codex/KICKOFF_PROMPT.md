# ASW Phase 8 — Fresh-Agent Kickoff

You are continuing from a **committed, runtime-qualified ASW RFC 0001 core**. Your task is only **Phase 8: Controlled Evaluation Harness & MVP Validation** using this extension package.

Do not reopen phases 1–7.

## Start

1. Read the target repository `AGENTS.md`.
2. Read this extension's `AGENTS.md`, `BASELINE_ACCEPTANCE.md`, and `PHASE-8-EVALUATION.md`.
3. Read the target repository's committed `checklists/MVP_COMPLETION_CHECKLIST.md` and `docs/RUNTIME_QUALIFICATION_2026-08-02.md` only to verify the accepted baseline exists.
4. Record base commit SHA and clean/dirty status.
5. Read the extension docs/schemas/checklist needed for the evaluation.

If the committed baseline evidence is absent or materially contradicts `BASELINE_ACCEPTANCE.md`, stop and report that prerequisite failure. Otherwise do not rerun broad core implementation work.

## Protected core

Normal Phase 8 work is additive. Do not modify `asw/`, existing RFC schemas, the completed implementation checklist, or existing runtime-qualification evidence.

If the controlled harness exposes a reproducible core defect, persist a minimal reproducer and classify Phase 8 as blocked by that defect. Do not silently repair/refactor the core from this fresh-agent task.

## Implement in three phases

### Extension Phase A — harness + baselines

Implement the controlled scenario controller/probes, independent ground-truth recorder, all baseline observers, ASW adapter, raw-result writer, deterministic aggregator, and extension schema/fixture tests.

Use the exact contracts in:

- `docs/HARNESS_ARCHITECTURE.md`
- `docs/SCENARIOS.md`
- `docs/BASELINES.md`
- `schemas/`

Run focused tests and validate all extension valid/invalid fixtures.

Then use the existing `review-agent` **once** for this phase, focused only on experimental leakage, baseline unfairness, ground-truth contamination, and material harness correctness. Fix material findings, rerun affected tests, and continue. Do not call another reviewer for Phase A.

### Extension Phase B — freeze + execute

Create the frozen profile from `fixtures/valid/evaluation-profile.json`, replacing the placeholder commit/model metadata with the actual fixed values but **not changing the normative thresholds/repetition counts**.

Execute the protocol in `docs/RUN_PROTOCOL.md`:

1. Layer A deterministic systems comparison;
2. integrity checks;
3. preregistered best-baseline selection;
4. bounded Layer B agent continuation comparison.

Layer A must use no model calls. Keep Layer B to the frozen small run count; do not expand it for cosmetic confidence.

Persist raw evidence as you go. Do not tune thresholds, prompts, intervals, or budgets after results become visible except to invalidate and restart the entire run under a newly declared run ID for a genuine technical defect.

Use the existing `review-agent` **once** for Phase B, focused only on profile freeze integrity, metric correctness, run fairness, and result validity. Fix only material methodology/implementation defects. Do not review-loop.

### Extension Phase C — audit + classify

Regenerate the aggregate summary deterministically from raw results. Complete `checklists/MVP_EVALUATION_COMPLETION_CHECKLIST.md` with evidence pointers.

Write `docs/EVALUATION_RESULTS_<date>.md` following `docs/EVIDENCE_REPORTING.md`.

Classification must be exactly:

- `SUPPORTED`
- `NOT_SUPPORTED`
- `INCONCLUSIVE`

Do not call a result supported unless every required threshold passes.

Use the existing `review-agent` **once** for Phase C, focused only on false-completion risk, threshold arithmetic, evidence traceability, and overclaiming. Fix material reporting/audit defects, rerun affected deterministic aggregation/checks, and finish. No review loop.

## Efficiency rules

- Main agent owns all implementation and execution; do not orchestrate subagents.
- Prefer deterministic scripts and local measurement over model calls.
- Layer A must be model-free.
- Do not rerun trials when raw evidence can be reaggregated.
- Use repository search and targeted file reads; do not reread the whole RFC package repeatedly.
- Use focused tests while developing and full extension validation at phase boundaries.
- If two implementations satisfy the protocol, choose less code, less mutable state, fewer dependencies, and easier reproducibility.
- Route hard reasoning according to the repository's existing model-routing policy; routine harness work stays on the economical workhorse model.

## Deliverable

Do not return a plan as the final result. Complete the extension and return:

- harness/baseline implementation summary;
- frozen profile/run ID;
- Layer A and Layer B result summary;
- threshold audit;
- final `SUPPORTED` / `NOT_SUPPORTED` / `INCONCLUSIVE` classification;
- evidence paths;
- any genuine blocker or discovered core defect.
