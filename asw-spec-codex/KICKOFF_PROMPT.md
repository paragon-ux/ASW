# ASW RFC 0001 — One-Shot Implementation Kickoff Prompt

You are implementing **ASW — Application Signals for Windows, RFC 0001** in this repository.

Your job is to take the specification package from contracts to a working, reviewed MVP in **one continuous implementation run**. Do not stop after planning, scaffolding, or a partial architecture. Implement, test, perform one targeted review-agent pass per implementation phase, fix material findings, and continue until the hard MVP gate is satisfied or a genuine specification/platform blocker prevents an item from being truthfully completed.

The main agent owns the implementation from start to finish. **Do not orchestrate a team of subagents. Do not delegate planning, implementation, testing, integration, checklist management, or follow-up review to subagents.** The only subagent use permitted by this kickoff is the existing **`review-agent` skill**, used exactly once at the end of each phase as described below.

## 1. Read efficiently, with package authority preserved

Start with the minimum authoritative set needed to understand the whole system:

1. `AGENTS.md` — implementation rules and non-negotiable architecture.
2. `README.md` — package authority, product hierarchy, authority model, and implementation order.
3. `RFC-0001.md` — normative product and behavioral specification.
4. `checklists/MVP_COMPLETION_CHECKLIST.md` — **hard release gate**.
5. `docs/ARCHITECTURE.md` — component boundaries, authority separation, application identity, and trust boundaries.
6. `docs/MVP_SCOPE.md` — exact MVP scope, non-scope, and required user journey.

After that, load schemas, docs, and fixtures **when the current phase needs them**. Do not repeatedly reread the entire package or load every fixture into context when repository search, a schema index, a targeted section, or a focused test can answer the question.

Use these materials phase-locally:

- `schemas/index.json` and the schemas governing the current feature.
- `docs/FRONTIER_MODEL.md` for journal/replay work.
- `docs/REDUCER_POLICY.md` for event-to-signal reduction.
- `docs/WINDOWS_SURFACE.md` for GUI, UIA, coordinates, and Windows notification behavior.
- `docs/AGENT_INTERFACE.md` for agent grants, subscriptions, bounded reads, streams, and replay.
- `docs/EVALUATION_PLAN.md` for the final evaluation phase.
- `fixtures/README.md`, relevant valid/invalid fixtures, and `fixtures/invalid/semantic-cases.md` while implementing the contract they exercise.

Treat package authority exactly as described in `README.md`. Do not replace package terminology or requirements with assumptions from an older design.

If two normative artifacts actually conflict, stop implementation of the conflicting behavior and report the exact files/clauses that must be reconciled. Do not silently choose one. Otherwise, do not ask for routine clarification: choose the simplest implementation that satisfies the normative behavior, document material decisions, and continue.

## 2. Efficiency rule

**Optimize for the cheapest correct implementation that satisfies the specification.** The RFC defines required behavior and authority boundaries; it does not require unnecessary abstraction, ceremony, indirection, or token-heavy analysis.

Prefer, in order:

1. reusing a compliant existing component;
2. a small direct implementation with explicit tests;
3. a new abstraction only when it removes real duplication or is required by a boundary in the spec.

Use repository search and diffs instead of broad rereads. Run focused tests while developing; run broader suites at phase boundaries and the full suite at completion. Avoid speculative refactors, generalized frameworks, duplicate documentation, exhaustive commentary, or optional features that do not advance the MVP hard gate.

If two approaches satisfy the same normative contract, choose the one with less code, less state, fewer dependencies, and easier deterministic testing.

## 3. Product invariants you must preserve

Do not violate these while implementing:

- ASW is **GUI-first**. The Windows GUI is the primary user product surface.
- The canonical post-reduction record is a **signal**, not a Windows notification.
- Windows App SDK notifications are an optional **delivery channel** for user subscriptions.
- Users control **observation authorization** for applications, files/directories, processes/jobs, diagnostics, and UI Automation surfaces.
- Observation authorization, observation, signal creation, subscription, and delivery are distinct stages.
- Users and agents may both subscribe to existing signals.
- A subscription MUST NOT expand observation scope or participate in canonical signal creation.
- An agent MUST be constrained by both the user-authorized observation universe and an active user-issued agent access grant.
- Agents consume the local structured read/subscription/stream interface; normal agent use MUST NOT require the CLI.
- The CLI, if implemented, is developer/diagnostic/conformance tooling only.
- Signal history is grouped by application in the GUI.
- Authoritative journal inputs are append-only JSONL; indexes/caches are rebuildable derived state.
- Reducer behavior is deterministic, finite, versioned, and reject-by-default.
- Unsupported, invalid, unauthorized, hint-only, or degraded facts fail closed for ordinary signal creation.
- Source degradation requires deterministic reconciliation before the source returns healthy.
- Replay reconstructs ASW state; it MUST NOT replay external side effects.
- The frontier is local ASW journal/source ordering metadata as defined in `docs/FRONTIER_MODEL.md`; do not introduce distributed-state requirements.

## 4. Implementation objective

Deliver the complete RFC 0001 MVP, including:

- contract/schema validation and conformance fixtures;
- authoritative append-only journal and rebuildable indexes;
- durable journal sequence, runtime/source epochs, frontier, and replay cursors;
- deterministic versioned event-to-signal reducer;
- application identity and application-grouped signal history;
- user-controlled observation authorization;
- filesystem observation with deterministic settling, artifact stability, degradation, and reconciliation;
- registered process/job observation;
- eligible registered UI Automation window/dialog/control observation;
- explicit application/diagnostic adapter contracts;
- user and agent subscriber registrations and subscriptions;
- user-issued agent access grants with server-side enforcement;
- GUI surfaces: **Activity, Subscriptions, Applications, Sources & Permissions, Agents**;
- Windows App SDK user notification delivery where supported;
- local bounded agent list/read/stream/resume interface;
- optional diagnostic CLI only if useful after the primary GUI and agent interfaces are complete;
- conformance tests, semantic fail-closed tests, replay/rebuild tests, and evaluation fixtures;
- evidence for every applicable item in `checklists/MVP_COMPLETION_CHECKLIST.md`.

Do not treat placeholder pages, no-op adapters, unchecked TODOs, or mocks with no contract tests as completed features.

## 5. Work in implementation phases

Use these phases unless the existing repository makes a small reordering clearly safer. Keep each phase cohesive enough that its review can reason about the important boundaries without reviewing unrelated work.

### Phase 1 — Contracts and deterministic core

Implement:

- schema and fixture validation;
- journal record contracts;
- canonical event/signal contracts;
- deterministic reducer policy representation;
- application identity/grouping primitives.

Primary pointers:

- `RFC-0001.md`
- `schemas/`
- `fixtures/`
- `docs/REDUCER_POLICY.md`
- checklist sections covering contracts and canonical signal behavior.

Critical review categories: **contract conformance**, **determinism/fail-closed correctness**, **test adequacy**.

### Phase 2 — Journal, frontier, restart, indexes, and replay

Implement:

- append-only authoritative journal;
- durable `journal_sequence`;
- runtime/source epochs and source-local cursors;
- rebuildable derived indexes/caches;
- replay cursors and deterministic replay/rebuild behavior.

Primary pointers:

- `docs/ARCHITECTURE.md`
- `docs/FRONTIER_MODEL.md`
- relevant journal/frontier/replay schemas and fixtures;
- checklist “Journal, frontier, replay”.

Critical review categories: **state authority/replay**, **restart and ordering correctness**, **test adequacy**.

### Phase 3 — Observation authorization, subscribers, subscriptions, and agent access

Implement:

- user-controlled observation authorization;
- source registrations bounded by that authorization;
- user and agent subscribers/subscriptions;
- user-issued agent access grants;
- server-side enforcement of the effective agent scope.

The effective agent scope MUST remain:

`requested subscription ∩ active agent access grant ∩ user-authorized observation universe`

Primary pointers:

- `docs/ARCHITECTURE.md`
- `docs/AGENT_INTERFACE.md`
- observation-authorization, source-registration, subscriber, subscription, and agent-access schemas;
- relevant semantic invalid cases;
- checklist “Subscribers and access”.

Critical review categories: **authority/security**, **contract semantics**, **fail-closed tests**.

### Phase 4 — Windows observation sources

Implement:

- filesystem adapter and deterministic settle policy;
- artifact stability and `artifact.available` rules;
- filesystem degradation and deterministic reconciliation;
- registered process/job observation;
- explicit application/diagnostic adapter behavior;
- eligible registered UI Automation window/dialog/control observation;
- physical-pixel coordinate payloads and localization uncertainty.

Primary pointers:

- `RFC-0001.md`
- `docs/MVP_SCOPE.md`
- `docs/WINDOWS_SURFACE.md`
- source/event/coordinate/path-policy schemas;
- relevant source fixtures;
- checklist “Observation and sources” and Windows coordinate requirements.

Critical review categories: **source correctness/degradation**, **Windows boundary correctness**, **fail-closed behavior**.

### Phase 5 — GUI product surface

Implement the GUI-first MVP:

- **Activity**;
- **Subscriptions**;
- **Applications**;
- **Sources & Permissions**;
- **Agents**.

Primary pointers:

- `docs/WINDOWS_SURFACE.md`
- `docs/MVP_SCOPE.md`
- `docs/ARCHITECTURE.md`
- checklist “Product surfaces”.

Critical review categories: **UX against the required user journey**, **authorization/subscription clarity**, **Windows integration correctness**.

### Phase 6 — Delivery and agent interface

Implement:

- Windows App SDK notification delivery;
- delivery failure recording without invalidating the canonical signal;
- local bounded agent list/read/stream/resume interface;
- grant revocation enforcement;
- optional diagnostic/conformance CLI only if it materially helps validation or operations.

Primary pointers:

- `docs/WINDOWS_SURFACE.md`
- `docs/AGENT_INTERFACE.md`
- delivery/subscription/replay schemas;
- relevant semantic invalid cases;
- checklist “Agent interface” and Windows delivery requirements.

Critical review categories: **agent access/security**, **stream/replay correctness**, **delivery semantics**.

### Phase 7 — End-to-end conformance, evaluation, and hard gate

Complete:

- cross-feature integration;
- conformance and semantic invalid cases;
- replay/rebuild/restart verification;
- evaluation fixtures supported by the current environment;
- hard-gate evidence and final polish.

Primary pointers:

- `docs/EVALUATION_PLAN.md`
- `fixtures/evaluation/`
- `fixtures/invalid/semantic-cases.md`
- `checklists/MVP_COMPLETION_CHECKLIST.md`
- the RFC and all docs implicated by any remaining checklist item.

Critical review categories: **spec/checklist gaps**, **cross-feature correctness**, **false-completion risk**.

## 6. One-review-agent rule — exactly one targeted subagent review per phase

At the end of each phase, after the phase implementation and focused tests are complete, invoke the existing **`review-agent` skill exactly once**.

This is the only subagent review for that phase.

**Do not:**

- spawn multiple reviewers for different categories;
- run reviewers in parallel;
- ask a subagent to implement fixes;
- ask a subagent to plan the next phase;
- ask a second reviewer to verify the first review;
- re-run the review-agent after fixes;
- enter a review/fix/review loop.

The main agent remains responsible for deciding what to fix, applying fixes, running tests, and continuing.

### Make the one review count

Give the review-agent a tight, high-signal packet rather than the whole repository when unnecessary:

- the current phase name and completed scope;
- the relevant spec/doc/schema/checklist pointers from the phase above;
- the changed files or diff for the phase;
- concise test results and any known limitations;
- only the **critical review categories** listed for that phase;
- any specific area where the main agent has uncertainty.

Ask the review-agent to prioritize **material, actionable findings** only:

1. spec or contract violations;
2. correctness/fail-closed defects;
3. security/authority boundary violations;
4. replay/state corruption risk;
5. Windows integration mistakes that invalidate the feature;
6. missing tests that could conceal one of the above.

Do not spend the review budget on stylistic preferences, speculative architecture, broad refactors, documentation restatement, or optional polish unless it creates a material MVP risk.

Request a compact result: a short prioritized list with evidence and an explicit **PASS / PASS WITH MINOR FINDINGS / MATERIAL FINDINGS** assessment. A clean review should be allowed to say simply that no material issue was found.

### After the one review

- Fix **material** findings that are supported by the spec or demonstrable correctness/security concerns.
- Fix minor findings only when the change is cheap, low-risk, and clearly improves conformance.
- Do not chase subjective polish or diminishing-return refactors.
- Run the focused tests affected by the fixes and the normal phase regression set.
- **Do not call the review-agent again for that phase.**
- If tests pass and no unresolved material blocker remains, continue to the next phase.

If a review finding conflicts with the normative package, follow package authority, note why the finding was not applied, and continue. If it exposes a genuine normative conflict or a blocker that makes truthful completion impossible, record the blocker rather than inventing behavior.

## 7. Lightweight main-agent checks inside each phase

Do not wait for the subagent to catch obvious issues. For each feature as it is implemented, perform a brief local check sufficient to keep the phase healthy:

- confirm the governing schema/doc/checklist pointer;
- run the smallest useful tests;
- inspect the diff for accidental scope expansion or unsafe defaults;
- keep authoritative vs derived state explicit where relevant;
- confirm invalid/unauthorized/degraded input fails closed where required.

This is **not** a second exhaustive review process. Keep it short. The single phase-end `review-agent` pass is the independent review.

## 8. Test and validation requirements

At minimum, before declaring the MVP complete:

- Run `python validate_fixtures.py` and require every valid fixture to pass and every invalid JSON fixture to fail as intended.
- Implement executable tests for every case in `fixtures/invalid/semantic-cases.md`.
- Verify reducer determinism for identical authoritative inputs and policy versions.
- Verify replay produces materially equivalent canonical signal history.
- Verify replay does not mutate external files, processes, applications, or UI.
- Verify durable `journal_sequence` survives restart and replay cursors resume correctly.
- Verify index/cache deletion followed by rebuild preserves semantic state.
- Verify agent grant revocation prevents subsequent reads/streams.
- Verify out-of-grant and out-of-authorization subscriptions/reads are rejected server-side.
- Verify subscription changes do not create, delete, or rewrite canonical signal history.
- Verify unstable artifacts never become `artifact.available`.
- Verify degraded sources reconcile before returning healthy.
- Verify Windows notification delivery failure does not delete or invalidate the underlying signal.
- Verify UIA coordinate payloads use `windows_virtual_screen_physical_px` and preserve localization uncertainty.
- Exercise the comparative evaluation fixtures defined under `fixtures/evaluation/` when the environment supports the required scenarios.

Use focused tests during implementation. Avoid repeatedly running the entire suite when a narrow test set provides equivalent evidence. Run the complete applicable suite at the end of Phase 7.

If the current environment cannot execute a Windows-only runtime path, still implement the real Windows integration behind a testable boundary, run all platform-independent tests, and record the exact Windows runtime verification that remains. **Do not claim a hard-gate item passed without evidence.**

## 9. GUI-first acceptance expectations

The GUI must be usable as the primary configuration and activity surface. Prioritize this user journey:

1. User opens **Applications** and enables/registers an application.
2. User opens **Sources & Permissions** and authorizes the relevant files, processes/jobs, diagnostics, and/or UI surfaces.
3. **Activity** begins showing canonical signals grouped by application, newest first.
4. User creates a **Subscription** for selected applications/categories and chooses Activity and/or Windows notification delivery where applicable.
5. User opens **Agents**, grants an agent access to selected applications/categories, and can revoke that access.
6. The agent creates a narrower subscription and reads/resumes its bounded structured stream without using the CLI.

The GUI must not make users manage source epochs, reducer policy internals, journal offsets, or replay bookkeeping in normal flows.

## 10. Implementation discipline

- Prefer the simplest implementation that fully satisfies the contracts.
- Do not add speculative cross-platform, distributed, cloud, visual-reasoning, or general GUI-automation architecture.
- Do not introduce recommendations, task-success reasoning, or inferred “next actions.”
- Do not use subscription state as a reducer input.
- Do not broaden observation automatically based on agent requests.
- Do not make a derived database/cache authoritative.
- Do not weaken schemas merely to make implementation easier.
- Do not rename package concepts without changing the RFC/contracts first.
- Do not leave critical failure handling as TODOs.
- Keep changes coherent and testable even though the overall run is one-shot.
- Do not generate extra reports, architectural essays, or duplicated docs unless they are required evidence for the checklist.
- Do not spend tokens proving obvious facts repeatedly. Use executable evidence where possible.

## 11. Completion procedure

When Phase 7 implementation and its **single review-agent pass** are complete:

1. Run the complete schema/fixture suite.
2. Run all applicable unit/integration/end-to-end tests available in the environment.
3. Check every item in `checklists/MVP_COMPLETION_CHECKLIST.md` against concrete evidence.
4. Fix any remaining issue exposed by those tests/checklist checks that is implementable in the current environment.
5. Re-run only the affected tests plus the final regression suite needed to establish confidence. Do not start another subagent review cycle.
6. Produce one concise final implementation report containing:
   - features completed;
   - material implementation decisions made within the RFC's allowed freedom;
   - tests and validation run, with results;
   - checklist items satisfied, with evidence pointers;
   - checklist items not satisfied, with the exact blocker and no false claim of completion;
   - known RFC-0001 limitations rather than speculative future work;
   - files/modules a human maintainer should review first.

## 12. Definition of done

The task is not done because the project builds, the GUI launches, or a reviewer says “looks good.”

It is done when the implementation satisfies the hard gate in `checklists/MVP_COMPLETION_CHECKLIST.md` to the extent verifiable in the current environment, all applicable tests pass, the single targeted review-agent pass for each phase has been addressed without entering review loops, and no known spec violation remains unfixed.

Begin by reading the minimum authoritative set in Section 1, then implement continuously through the phases. **Do not return a plan as the deliverable. Do not orchestrate subagents. Use one targeted `review-agent` pass per phase, fix material findings, and keep moving.**
