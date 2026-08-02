# Noncanonical whitepaper drafting aid

The published paper is [`docs/WHITEPAPER.md`](../docs/WHITEPAPER.md). This
template is retained for provenance only; verify all claims against the RFC,
runtime record, and frozen Phase 8 artifacts before reuse.

# Application Signals for Windows: Deterministic Signals for Bounded Asynchronous Desktop Workflows

## Abstract

Desktop applications and developer workflows frequently expose asynchronous transitions—file stabilization, background job completion, generated artifacts, dialogs, and newly available UI operations—that users or software agents otherwise discover by polling or repeated observation. **Application Signals for Windows (ASW)** is a bounded Windows 11 signal layer that converts explicitly authorized application, filesystem, process/job, diagnostic, and UI Automation observations into deterministic canonical signals. Signal creation is independent of subscriber presence; users and agents subscribe to an existing authorized signal history, while agent reads are bounded by explicit user-issued access grants. Windows App SDK notifications are a delivery surface rather than the canonical data model.

We implemented and runtime-qualified RFC 0001 on Windows 11, including native Windows App SDK delivery, registered process/job transitions, real UI Automation window/dialog/control observations with physical-pixel coordinates, deterministic journal replay, source degradation/reconciliation, GUI configuration, and bounded agent list/read/stream/resume behavior. We then evaluated ASW using a preregistered controlled harness with independent monotonic ground truth. Across the three primary scenario classes—job completion, file/artifact transition, and UI transition—ASW achieved 100% detection with 0% duplicate and false-positive useful-signal rates. Relative to the mechanically selected best non-ASW baseline, ordinary notification text, ASW reduced median observation count by 50% in all three primary classes without detection regression. In the bounded continuation layer, both conditions achieved 100% continuation success, while ASW reduced median observation calls from two to one and median continuation latency from 40 ms to 20 ms.

These results support the bounded RFC 0001 MVP proposition: structured deterministic application signals can reduce observation effort while preserving transition recognition and continuation under the controlled Windows scenarios tested. They do not establish universal application coverage, cross-platform behavior, production-scale reliability, or universal benefit for arbitrary agents.

## 1. Motivation

Asynchronous desktop workflows create an information problem rather than only an automation problem. A user or agent may know what operation it started but still need to determine when a build exits, when an output stabilizes, whether a modal appeared, or whether a previously unavailable operation became usable. Polling and repeated observation can recover this information, but at the cost of repeated reads, latency, duplicate interpretation, and additional tool or model usage.

ASW asks a narrower question: **can a local Windows service expose bounded, deterministic, application-associated transition signals that reduce unnecessary observation without embedding task reasoning into the signal layer?**

RFC 0001 deliberately separates observation, signal creation, subscription, and downstream action. This allows ASW to provide environmental evidence without deciding whether a user's broader goal is satisfied.

## 2. Design principles

### 2.1 Bounded observation authority

Users authorize what ASW may observe. Authorization is distinct from subscriptions: subscribing to a signal category cannot expand the underlying observation universe.

### 2.2 Canonical signals, not notification strings

The canonical post-reduction object is a typed signal. Windows App SDK notifications are optional user-facing delivery. Agents consume structured signal history through a local interface.

### 2.3 Deterministic reduction

Raw observations are reduced through a finite, versioned, reject-by-default policy. Unsupported, invalid, unauthorized, hint-only, or degraded facts do not silently become ordinary signals.

### 2.4 Explicit agent bounds

An agent can read only inside the intersection of its requested subscription, active user-issued access grant, and the user-authorized observation universe. Revocation stops subsequent reads/streams.

### 2.5 Replayable local authority

Append-only JSONL journal inputs are authoritative. Indexes and caches are rebuildable. Replay reconstructs ASW state without replaying external side effects.

## 3. System architecture

[Phase 9 agent: derive a concise architecture diagram from the committed implementation/RFC. Do not invent components.]

Explain:

- source adapters;
- observation authorization;
- authoritative journal/frontier;
- deterministic reducer;
- canonical signal history;
- user/agent subscriptions;
- Windows delivery;
- bounded agent API.

## 4. Windows implementation and runtime qualification

The accepted Windows 11 runtime qualification verified native Windows App Runtime 2.3.1 integration and successful `AppNotificationManager.Show()`. Live process/job tests observed success and failure exit transitions from registered processes. Live UI Automation tests observed a real top-level window, modal dialog, and enabled control with `windows_virtual_screen_physical_px` coordinates. An end-to-end run exercised authorized filesystem observation through canonical signal creation, Windows delivery, agent list/read/resume, and grant revocation. Degraded filesystem observation remained fail-closed until reconciliation restored health.

[Phase 9 agent: add exact repository evidence references and distinguish deterministic tests from runtime-qualified behavior.]

## 5. Evaluation methodology

### 5.1 Experimental question

The preregistered hypothesis was that structured ASW signals would reduce unnecessary observation/tool effort while preserving transition recognition and continuation.

### 5.2 Controlled real transitions

The evaluation controller caused real bounded transitions through the normal Windows/process/filesystem/UI surfaces. It did not establish primary evidence by directly injecting benchmark-only canonical signals. Independent monotonic ground truth was recorded separately and was inaccessible to observation mechanisms under test.

### 5.3 Scenarios

Primary scenario classes:

- job completion/failure;
- stable external file/artifact transition;
- UI modal/operation-availability transition.

Secondary probes covered render/export-style output and crash/restart.

### 5.4 Conditions

The systems layer compared:

- polling;
- filesystem watching where applicable;
- ordinary notification text;
- repeated observation;
- ASW signals.

The best non-ASW baseline for each primary class was chosen mechanically using the preregistered rule. `ordinary_notification` was selected for all three primary classes.

### 5.5 Layer A

Layer A was model-free (`0` model calls) and measured detection, latency, observation count, misses, duplicates, false positives, attribution, event-kind accuracy, subject accuracy where applicable, and continuation readiness.

### 5.6 Layer B

Layer B compared ASW only against the mechanically selected best non-ASW baseline using the frozen small repetition count. The continuation agent/configuration was normalized and deterministic for the benchmark. Therefore Layer B supports the bounded continuation result but should not be generalized to arbitrary external LLM agents.

### 5.7 Integrity

The final accepted run persisted 736 raw trial records, 158 independent ground-truth records, and 36 agent-usage records. Authorization and replay violation counts were zero. Technical invalidated runs were retained separately rather than rewritten into the accepted dataset.

## 6. Results

### 6.1 Correctness

| Metric | Result |
|---|---:|
| Detection success | 100% |
| Duplicate useful-signal rate | 0% |
| False-positive useful-signal rate | 0% |
| Application attribution accuracy | 100% |
| Event-kind accuracy | 100% |

All preregistered correctness thresholds passed.

### 6.2 Layer A efficiency

For each of the three primary scenario classes, the mechanically selected non-ASW baseline was ordinary notification text. ASW required a median of one observation versus two for the selected baseline, a 50% reduction, with no detection regression.

| Primary class | ASW median observations | Selected baseline | Baseline median observations | Reduction |
|---|---:|---|---:|---:|
| File/artifact transition | 1 | Ordinary notification | 2 | 50% |
| Job completion | 1 | Ordinary notification | 2 | 50% |
| UI transition | 1 | Ordinary notification | 2 | 50% |

### 6.3 Layer B continuation

| Condition | Continuation success | Median observation calls | Median continuation latency |
|---|---:|---:|---:|
| ASW | 100% | 1 | 20 ms |
| Ordinary notification | 100% | 2 | 40 ms |

ASW therefore met the preregistered non-inferiority condition while improving both bounded continuation-efficiency measures by 50%.

## 7. Interpretation

The experiment does not show that applications cannot expose equivalent information through native APIs, nor that ordinary notifications are ineffective. In fact, ordinary notification text became the strongest non-ASW comparator under the preregistered selection rule. The result instead supports a narrower architectural proposition: when asynchronous transitions are represented as structured, application-associated signals with deterministic semantics and bounded replay/access, a consumer can require fewer observations to reach the same correct continuation state in the tested workflows.

The observed advantage was therefore primarily **information structure and access efficiency**, not higher raw detection success: the selected baseline also achieved perfect continuation success in Layer B.

## 8. Limitations and threats to validity

- The evaluation is bounded to controlled Windows MVP scenarios rather than a broad population of third-party applications.
- Results do not establish cross-platform behavior.
- Layer B uses a bounded deterministic/normalized continuation agent and does not establish general external-LLM benefit.
- Frozen polling intervals, deadlines, notification text contract, and baseline definitions affect comparative results.
- The benchmark establishes short controlled-run behavior, not production-scale long-duration reliability.
- The secondary ASW crash/restart result recorded `subject_accuracy = 0.0`; this did not affect the preregistered primary hard gate but should motivate follow-up work.
- The experiment supports RFC 0001's bounded proposition and should not be read as evidence for universal desktop perception or general GUI automation.

## 9. Reproducibility

Accepted run: `asw-mvp-eval-20260802-05`

Base core commit: `7d6e267c6e89cdcd8a71644c67c95d2ab4260330`

Profile digest: `sha256:9c38bd41057e1933cda9c54c26fa143f775d7e6bbb5cd2848423ccd7cebeb1c7`

The repository should retain the frozen profile, run manifest, independent ground truth, raw trial results, agent usage, deterministic aggregate summary, invalidation records, and the documented validation/aggregation commands.

## 10. Conclusion

ASW RFC 0001 demonstrates a local Windows architecture for turning bounded authorized observations into deterministic application signals that can be consumed by users and agents without making subscriptions or delivery channels authoritative. The completed Windows runtime qualification established that the MVP operates across real filesystem, process/job, UI Automation, GUI, Windows notification, and agent-access boundaries. The preregistered controlled evaluation then met every hard-gate threshold and classified the bounded MVP proposition as `SUPPORTED`.

Within the tested scenarios, the main empirical advantage was not a gain in correctness over every baseline, but a reduction in observation and continuation effort while preserving correctness. That is the appropriate scope of the current evidence and the starting point for broader application and agent studies.
