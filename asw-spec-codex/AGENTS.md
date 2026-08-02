# AGENTS.md — Codex implementation instructions

Implement **RFC 0001: Application Signals for Windows** exactly as specified in this package.

## Non-negotiable architecture

- ASW is **GUI-first**. Do not make a CLI the product's primary user interface.
- Users control observation authorization for applications, files/directories, processes/jobs, and UI Automation surfaces.
- Users and agents may both subscribe to signals.
- Subscriptions filter an existing authorized signal universe. They MUST NOT expand observation scope.
- Agents require a user-issued access grant and MUST NOT receive applications/categories outside that grant.
- The canonical data object exposed after reduction is a **signal**, not a Windows notification.
- Windows App SDK notifications are one optional delivery channel for user subscriptions.
- Agents use the local structured subscription/read protocol; do not require agents to shell out to the diagnostic CLI.
- Signal history is grouped by application in the GUI.
- Authoritative journal inputs are append-only JSONL. Indexes/caches are rebuildable.
- Reducer behavior is deterministic, versioned, and reject-by-default.
- Source degradation requires reconciliation before the source returns healthy.
- Unknown, unsupported, unauthorized, invalid, or degraded facts fail closed.

## Naming

Use `ASW`, `Application Signals for Windows`, `event`, `signal`, `subscriber`, `subscription`, `agent access grant`, `observation authorization`, `application`, `frontier`, and `delivery` as defined by the RFC.

Do not introduce unrelated identity/disposition models, managed-environment abstractions, or distributed shared-state requirements.

## Model routing and usage discipline

Optimize for the **cheapest model that can satisfy the specification correctly**. Do not escalate because a task is large, touches many files, or sounds difficult in the abstract. Escalate only when the current operation has materially higher reasoning risk or the default model has failed once on an important task.

### Default workhorse

Use **Luna Max** for normal implementation work, including:

- well-specified feature implementation;
- schema and fixture work;
- tests and test maintenance;
- documentation;
- mechanical refactors and renames;
- straightforward bug fixes;
- routine Windows/API/UI plumbing after the design is settled; and
- ordinary conformance and validation work.

### Sol Medium escalation

Use **Sol Medium** only when the current task materially depends on one or more of the following:

- resolving ambiguous or conflicting normative requirements;
- changing architecture or authority boundaries;
- security or agent-access enforcement;
- journal authority, replay, frontier, reducer determinism, or reconciliation semantics;
- concurrency, ordering, or race-condition reasoning;
- difficult Windows interop behavior where correctness depends on subtle platform semantics; or
- a materially important task that Luna attempted once and did not resolve adequately.

Do not retry the same task repeatedly on Luna before escalating. One clearly inadequate attempt is sufficient when the task matters.

### Exceptional escalation

Use **Sol High/Max** only as a last-resort recovery path after Sol Medium has failed to resolve a material correctness problem. Do not use it for routine implementation, formatting, documentation cleanup, fixture generation, ordinary testing, or mechanical refactoring.

### Routing rule

Route by **reasoning risk, not task size or token count**. A broad mechanical change may remain on Luna; a five-line change to replay or access-control semantics may warrant Sol Medium. When two approaches both satisfy the RFC, prefer the one with less code, less mutable state, fewer dependencies, and easier deterministic testing.

## Review-agent policy

The main agent owns planning, implementation, integration, testing, fixes, and checklist evidence. **Do not orchestrate implementation through subagents.**

The only permitted delegated review is the repository's existing **review-agent skill**, and it MUST be used efficiently:

- use at most **one review-agent pass per implementation phase**;
- select only the **2–3 most critical review categories** for that phase;
- give the reviewer a compact packet: phase scope, relevant RFC/doc/schema/checklist pointers, changed files or diff, and current test results;
- use **Sol Medium** for the reviewer only when the selected categories involve architecture, authority/security, replay/determinism, reconciliation, concurrency, or difficult failure analysis; otherwise use Luna;
- ask for material correctness, security, spec-compliance, and regression findings—not style commentary or speculative redesign;
- do not enter review loops or ask for a second reviewer pass after fixes; and
- after the single review, fix material findings, rerun the affected tests, and continue when the phase is sufficiently sound.

If the review finds no material issue, continue immediately. Do not spend tokens manufacturing additional review work merely to increase confidence.

## Token and context efficiency

Treat usage as a constrained engineering resource. Preserve specification fidelity while avoiding unnecessary context and repeated work:

- read the authoritative core once, then load phase-specific docs, schemas, fixtures, and checklist sections as needed;
- prefer targeted searches and diffs over repeatedly rereading whole files;
- run focused tests during implementation and broader suites at phase boundaries or when cross-cutting changes justify them;
- avoid restating the specification in plans, review prompts, or implementation notes when a file/section pointer is enough;
- do not produce large speculative plans when the next implementation step is already determined by the RFC; and
- choose simpler compliant implementations over elaborate abstractions that increase code, review, or context cost.

## Testing contract

Before feature work is considered complete:

1. all `fixtures/valid/*.json` MUST validate;
2. all `fixtures/invalid/*.json` MUST fail validation;
3. semantic fail-closed cases in `fixtures/invalid/semantic-cases.md` MUST have tests;
4. journal replay MUST reproduce materially equivalent signal history for the same policy versions; and
5. deleting SQLite or another derived cache MUST NOT alter semantic state.

## GUI implementation priority

Implement the following user surfaces before an end-user CLI:

1. Activity
2. Subscriptions
3. Applications
4. Sources & Permissions
5. Agents

The GUI SHOULD use application-first language. Do not expose source epochs, reducer internals, or replay bookkeeping in ordinary user flows unless the user opens diagnostics/developer details.
