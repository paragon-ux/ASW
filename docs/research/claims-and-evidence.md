# Claims and evidence matrix

This matrix keeps public claims tied to the normative RFC, shipped code, runtime qualification, or the accepted frozen evaluation. The release claim remains limited to the bounded RFC 0001 MVP proposition.

| Claim | Evidence class | Canonical evidence | Boundary |
|---|---|---|---|
| ASW observes only user-authorized bounded surfaces. | Normative/implemented | [RFC 0001](../rfc/RFC-0001.md#8-observation-authorization-model), [service](../../asw/service.py) | Do not imply arbitrary desktop interception. |
| Signals are canonical structured records; notifications are delivery only. | Normative/implemented | [RFC 0001](../rfc/RFC-0001.md#21-windows-notification-delivery), [reducer](../../asw/reducer.py) | Keep subscriptions and delivery out of signal creation. |
| The reducer is deterministic, versioned, and reject-by-default. | Normative/implemented | [RFC 0001](../rfc/RFC-0001.md#13-deterministic-reducer), [reducer tests](../../tests/test_reducer.py) | Do not claim model-based inference or intent detection. |
| Journal inputs are authoritative and indexes/caches are rebuildable. | Normative/implemented | [RFC 0001](../rfc/RFC-0001.md#16-journal-authority-and-rebuildable-state), [service tests](../../tests/test_service.py) | Replay does not perform external side effects. |
| Agent access is the server-side intersection of subscription, grant, and observation authorization. | Normative/implemented | [RFC 0001](../rfc/RFC-0001.md#9-subscriber-and-access-model), [semantic tests](../../tests/test_semantics.py) | Revocation blocks subsequent reads/streams/resumes. |
| The GUI provides Activity, Subscriptions, Applications, Sources & Permissions, and Agents. | Implemented | [GUI](../../asw/gui.py), [GUI tests](../../tests/test_gui.py) | Describe the shipped five-page journey. |
| The loopback endpoint exposes structured operations without CLI use. | Implemented | [agent API](../../asw/agent_api.py), [agent guide](../guides/agent-integration.md) | Examples use placeholders; tokens are user-issued and local. |
| Filesystem, process/job, UI Automation, Windows delivery, GUI, and end-to-end paths were exercised. | Runtime verified | [runtime qualification](runtime-qualification.md) | Qualified Windows environment only. |
| ASW detection success was 100%, with 0% duplicate and false-positive useful-signal rates. | Empirically supported | [accepted aggregate](../provenance/accepted-aggregate.json), [release evidence summary](../provenance/release-evidence-summary.md) | Say “in the accepted controlled evaluation.” |
| The preregistered Layer A gate is at least 30% reduction in at least 2 of 3 primary classes without more than 2 percentage points of detection regression. | Empirically supported protocol | [evaluation thresholds](evaluation-thresholds.md) | The threshold is not 50%. |
| The accepted run passed all 3 primary classes, each with an observed 50% reduction. | Empirically supported result | [accepted aggregate](../provenance/accepted-aggregate.json) | Keep the observed result separate from the preregistered gate. |
| Layer B used one structured-stream observation versus two notification receipt-and-parsing observations. | Empirically supported protocol | [whitepaper](WHITEPAPER.md#75-layer-b), [reproducibility](reproducibility.md) | The 20 ms and 40 ms values are scripted protocol values, not measured Windows execution latency. |
| The secondary crash/restart ASW `subject_accuracy = 0.0` result is retained. | Limitation/empirical | [evaluation results](evaluation-results.md), [whitepaper](WHITEPAPER.md#10-limitations-and-threats-to-validity) | It did not invalidate the primary hard gate. |

Layer A used zero model calls. No entry in this matrix supports universal application coverage, cross-platform validation, universal agent benefit, or general-purpose desktop understanding.
