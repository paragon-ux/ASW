# AGENTS.md — ASW Phase 8 Evaluation Extension Instructions

Implement **ASW Phase 8: Controlled Evaluation Harness & MVP Validation** exactly as specified in this extension package.

This package begins from a **committed, runtime-qualified ASW RFC 0001 core**. The purpose of this task is to determine whether the bounded ASW MVP proposition is empirically supported, not to reopen or redesign the completed product implementation.

## Non-negotiable evaluation architecture

- Treat the committed RFC 0001 core implementation and runtime qualification as **accepted prerequisites**.
- Do not redo Phases 1–7 merely to increase confidence.
- Normal Phase 8 work is additive and MUST NOT modify `asw/` core product modules, existing RFC 0001 schemas, the completed implementation hard-gate checklist, or existing runtime-qualification evidence.
- If a controlled evaluation scenario exposes a reproducible core defect, preserve a minimal reproducer and classify the evaluation `BLOCKED — core defect discovered`. Do not silently repair or refactor the committed core in this task.
- Layer A is a deterministic **model-free systems benchmark**.
- Layer B is a deliberately bounded **agent continuation comparison**.
- Ground truth MUST be produced independently of the observation mechanism being evaluated.
- Baselines MUST run from the same scenario definitions and frozen run profile.
- Thresholds, repetitions, budgets, prompts/templates, polling intervals, seeds, and selection rules MUST be frozen before comparative results are inspected.
- Raw evidence MUST be persisted so aggregation, audits, and reports can be regenerated without rerunning trials.
- The ASW condition MUST use normal committed ASW public/service interfaces. Do not create a benchmark-only ASW implementation.
- The final classification MUST be exactly `SUPPORTED`, `NOT_SUPPORTED`, or `INCONCLUSIVE`.
- `SUPPORTED` MUST NOT be claimed unless every required threshold in `checklists/MVP_EVALUATION_COMPLETION_CHECKLIST.md` passes.

## Protected core boundary

During ordinary evaluation-extension work, do not modify:

- `asw/` product modules;
- existing RFC 0001 schemas;
- the existing RFC 0001 implementation checklist;
- existing runtime-qualification evidence; or
- committed product semantics merely to improve benchmark results.

The fresh agent MAY read those artifacts as evidence or to use public/service interfaces.

If an evaluation failure appears to originate in the core:

1. reproduce it with the smallest controlled scenario possible;
2. verify that the failure is not a harness, baseline, profile, or metric defect;
3. persist the reproducer and supporting evidence;
4. classify the relevant Phase 8 gate as blocked by a core defect; and
5. stop changing benchmark semantics to work around it.

Core repair belongs to a separate explicitly authorized task.

## Naming and claim discipline

Use `ASW`, `Application Signals for Windows`, `signal`, `event`, `scenario`, `condition`, `baseline`, `ground truth`, `trial`, `run`, `profile`, `metric`, and `classification` as defined by this extension and RFC 0001.

Do not reintroduce unrelated project terminology, actor/relevance models, distributed-state abstractions, or claims broader than the bounded RFC 0001 proposition.

Do not describe a threshold miss as a tooling inconvenience. Report negative evidence as negative evidence.

## Model routing and usage discipline

Optimize for the **cheapest model that can satisfy the specification correctly**. This routing policy is intentional and MUST NOT be relaxed merely because the evaluation spans many files or feels important.

Do not escalate because a task is large, long-running, touches many files, or contains many repetitions. Escalate only when the **current reasoning operation** has materially higher risk or the default model has failed once on an important task.

### Default workhorse — Luna Max

Use **Luna Max** for normal Phase 8 work, including:

- controlled harness implementation;
- scenario/probe implementation;
- baseline observer implementation;
- schema and fixture work;
- deterministic ground-truth recording;
- raw-result serialization;
- metric calculation with already-defined formulas;
- aggregation and reporting from frozen results;
- tests and test maintenance;
- documentation;
- mechanical refactors and renames;
- straightforward bug fixes;
- ordinary process/filesystem/UI plumbing after experiment semantics are settled;
- routine run execution;
- conformance and validation work; and
- any broad implementation task whose behavior is already well specified.

A large or cross-cutting implementation phase is still Luna work when the contracts and expected behavior are clear.

### Sol Medium escalation

Use **Sol Medium** only when the current task materially depends on one or more of the following:

- resolving ambiguous or conflicting normative requirements;
- deciding whether a proposed baseline is experimentally fair;
- detecting or preventing ground-truth leakage or contamination;
- reasoning about metric validity, threshold arithmetic, preregistration integrity, or condition comparability;
- deciding whether a result is `SUPPORTED`, `NOT_SUPPORTED`, or `INCONCLUSIVE` when evidence is genuinely ambiguous;
- security or access-control behavior exposed by the evaluation;
- replay, frontier, reducer determinism, reconciliation, or state-authority semantics encountered during evaluation;
- concurrency, ordering, timing, or race-condition reasoning that could invalidate results;
- subtle Windows behavior where experiment correctness depends on platform semantics;
- distinguishing a harness defect from a reproducible ASW core defect; or
- a materially important task that Luna attempted once and did not resolve adequately.

Do not retry the same important reasoning problem repeatedly on Luna before escalating. One clearly inadequate attempt is sufficient.

### Exceptional escalation

Use **Sol High/Max** only as a last-resort recovery path after Sol Medium has failed to resolve a material correctness or experimental-validity problem.

Do not use Sol High/Max for:

- harness implementation;
- running trials;
- fixture generation;
- result aggregation;
- formatting;
- documentation cleanup;
- ordinary testing;
- report generation from already-computed metrics; or
- mechanical refactoring.

### Routing rule

Route by **reasoning risk, not task size, phase number, elapsed time, or token count**.

A broad implementation of five benchmark observers may remain on Luna because the interfaces are explicit. A five-line change to baseline selection, threshold arithmetic, access-control semantics, or ground-truth timing may warrant Sol Medium.

When two approaches both satisfy the extension specification, prefer the one with:

1. less code;
2. less mutable state;
3. fewer dependencies;
4. fewer model calls;
5. fewer benchmark runs;
6. easier deterministic testing; and
7. easier reproduction from persisted raw evidence.

## Review-agent policy

The main agent owns planning, implementation, execution, integration, testing, fixes, aggregation, evidence, and checklist completion. **Do not orchestrate implementation or evaluation through subagents.**

The only permitted delegated review is the repository's existing **review-agent skill**, and it MUST be used efficiently.

Use at most **one review-agent pass per extension phase**:

1. Phase A — harness and baseline integrity;
2. Phase B — frozen profile, execution, metrics, and result integrity;
3. Phase C — evidence, threshold audit, classification, and claim discipline.

For each review:

- select only the **2–3 most critical review categories** for that phase;
- provide a compact packet containing the phase scope, relevant extension/spec pointers, changed files or diff, frozen inputs where applicable, and current test/result summary;
- do not give the reviewer the whole repository when a focused diff and referenced contracts are sufficient;
- use **Sol Medium** for the reviewer only when the selected categories involve experimental validity, fairness, ground-truth contamination, threshold/metric reasoning, architecture, authority/security, replay/determinism, reconciliation, concurrency, or difficult failure analysis;
- otherwise use Luna;
- request only material correctness, experimental-integrity, security, spec-compliance, and false-completion findings;
- do not request style commentary, speculative redesign, or broad future-work suggestions;
- do not ask a second reviewer to verify the first review;
- do not re-run the review-agent after fixes; and
- do not enter a review/fix/review loop.

After the single review:

1. fix material findings supported by the specification or reproducible evidence;
2. fix minor findings only when they are cheap, low-risk, and clearly improve correctness;
3. rerun only affected checks plus the normal phase regression set; and
4. continue immediately if no material unresolved blocker remains.

If the review finds no material issue, continue. Do not spend usage manufacturing more review work merely to increase confidence.

## Token and context efficiency

Treat usage as a constrained engineering resource. Preserve experimental validity and specification fidelity while avoiding unnecessary context, model calls, and reruns.

- Read this extension's authoritative core once, then load phase-specific docs, schemas, fixtures, and checklist sections as needed.
- Read the committed RFC/core evidence only when a Phase 8 question actually depends on it.
- Prefer targeted repository search, diffs, test names, schema pointers, and evidence paths over repeatedly rereading whole files.
- Do not restate large portions of the specification in plans, review prompts, reports, or comments when a file/section pointer is sufficient.
- Do not produce large speculative plans when the next step is already fixed by `PHASE-8-EVALUATION.md` or `KICKOFF_PROMPT.md`.
- Prefer deterministic scripts over model reasoning whenever a script can answer the question.
- **Layer A MUST use no model/LLM calls.**
- Keep Layer B to the frozen repetitions and conditions. Do not increase runs for cosmetic confidence.
- Persist raw results immediately so aggregation and reports can be regenerated without rerunning trials.
- Do not rerun a valid trial merely because the aggregate result is surprising or unfavorable.
- Invalidate and rerun only when there is a documented technical defect in the trial or harness.
- Use focused tests during implementation and broader suites at phase boundaries.
- Avoid full repository regression runs when an extension-local test set provides equivalent evidence; run the required final regression/audit once at completion.
- Prefer direct, testable implementations over abstractions that increase code, context, review cost, or experimental degrees of freedom.
- Do not use a harder model to summarize data that deterministic aggregation already computed.

## Experimental-integrity contract

Before comparative execution is considered valid:

1. the base commit SHA and worktree state MUST be recorded;
2. extension fixtures and schemas MUST validate;
3. primary scenario probes MUST produce independent ground truth;
4. all required baseline implementations MUST be executable or explicitly `not_applicable` under declared rules;
5. the evaluation profile MUST be frozen before the first comparative result is inspected;
6. profile digest, seeds, repetitions, deadlines, intervals, templates/prompts, budgets, model/tool configuration, metrics, thresholds, and selection rules MUST be persisted;
7. Layer A MUST be model-free;
8. Layer B MUST compare ASW only against the mechanically selected best non-ASW baseline for each primary scenario;
9. compared Layer B conditions MUST use identical agent/model/tool configuration except for the observation condition itself; and
10. no post-result tuning may favor one condition.

If a genuine technical defect requires changing frozen parameters after execution begins, invalidate that run, create a new run ID/profile digest, document the reason, and restart the affected comparative run. Do not edit the old run into compliance.

## Testing contract

Before Phase 8 is considered complete:

1. all extension `fixtures/valid/*.json` MUST validate;
2. all extension `fixtures/invalid/*.json` MUST fail validation;
3. harness and baseline implementations MUST have deterministic tests for their key contracts;
4. ground-truth generation MUST be tested independently from observers;
5. raw trial records MUST validate against the trial-result schema;
6. deterministic aggregation MUST reproduce the same summary from the same raw results;
7. threshold calculations MUST have direct tests at boundary values;
8. best-baseline selection MUST be deterministic and preregistered;
9. invalid or incomplete evidence MUST fail closed rather than produce `SUPPORTED`;
10. no replay/access/authorization violation may occur during evaluation; and
11. every item in `checklists/MVP_EVALUATION_COMPLETION_CHECKLIST.md` MUST have concrete evidence before `SUPPORTED` may be claimed.

## Phase priority

Implement and execute in this order:

1. **Phase A — Harness + Baselines**
   - controlled probes;
   - independent ground truth;
   - polling/file-watch/ordinary-notification/repeated-observation observers;
   - ASW adapter using committed public/service interfaces;
   - raw evidence writer;
   - deterministic aggregation primitives;
   - schema/fixture/tests.

2. **Phase B — Freeze + Execute**
   - freeze profile and digest;
   - run Layer A;
   - perform integrity checks;
   - mechanically select best baseline;
   - run bounded Layer B;
   - persist all raw evidence.

3. **Phase C — Audit + Classify**
   - regenerate aggregates from raw evidence;
   - execute threshold audit;
   - complete evaluation hard-gate checklist;
   - write evidence report;
   - classify exactly `SUPPORTED`, `NOT_SUPPORTED`, or `INCONCLUSIVE`.

Do not start release packaging, version tagging, licensing cleanup, or unrelated repository polish inside Phase 8. Those belong to a later release-readiness task after the evaluation classification is known.

## Completion discipline

Phase 8 is not complete because the harness runs or because ASW appears favorable in a few trials.

It is complete only when:

- the controlled evaluation protocol has executed as frozen;
- raw evidence and deterministic aggregates are persisted;
- the extension checklist is fully audited;
- the one permitted review-agent pass for each phase has been addressed without review loops;
- the final classification is supported by the declared thresholds; and
- no known experimental-integrity or specification violation remains unresolved.

If results fail the thresholds, report `NOT_SUPPORTED`. If evidence cannot validly decide the proposition, report `INCONCLUSIVE`. Do not alter the benchmark or core product simply to obtain `SUPPORTED`.
