# Claims and evidence matrix

This matrix is the Phase 9 claim audit. Public prose must use the class and
source shown here; documentation is explanatory and does not become a new
normative contract.

| Public claim | Class | Evidence / canonical home | Boundary or wording rule |
|---|---|---|---|
| ASW observes only user-authorized bounded surfaces. | Normative | [RFC 0001 sections 8 and 10](../../asw-spec-codex/RFC-0001.md#8-observation-authorization-model) | Do not imply arbitrary desktop interception. |
| Signals are canonical structured records; notifications are delivery only. | Normative | [RFC 0001 sections 4, 13, 21](../../asw-spec-codex/RFC-0001.md#21-windows-notification-delivery) | Keep subscriptions and delivery out of signal creation. |
| The reducer is deterministic, versioned, and reject-by-default. | Normative / implemented | [RFC 0001 section 13](../../asw-spec-codex/RFC-0001.md#13-deterministic-reducer), [asw/reducer.py](../../asw-spec-codex/asw/reducer.py), [reducer tests](../../asw-spec-codex/tests/test_reducer.py) | Do not claim model-based inference or intent detection. |
| Journal inputs are authoritative and indexes/caches are rebuildable. | Normative / implemented | [RFC 0001 sections 16-17](../../asw-spec-codex/RFC-0001.md#16-journal-authority-and-rebuildable-state), [service tests](../../asw-spec-codex/tests/test_service.py), [semantic tests](../../asw-spec-codex/tests/test_semantics.py) | Replay does not perform external side effects. |
| Agent access is server-side intersection of subscription, grant, and observation authorization. | Normative / implemented | [RFC 0001 sections 8-9](../../asw-spec-codex/RFC-0001.md#9-subscriber-and-access-model), [asw/service.py](../../asw-spec-codex/asw/service.py), [semantic/API tests](../../asw-spec-codex/tests/test_semantics.py) | Revocation blocks subsequent reads/streams/resumes. |
| The GUI provides Activity, Subscriptions, Applications, Sources & Permissions, and Agents. | Implemented | [asw/gui.py](../../asw-spec-codex/asw/gui.py), [GUI tests](../../asw-spec-codex/tests/test_gui.py), [MVP checklist](../../asw-spec-codex/checklists/MVP_COMPLETION_CHECKLIST.md) | Describe the shipped five-page journey. |
| Loopback `POST /v1/agent` exposes structured operations without CLI use. | Implemented | [asw/agent_api.py](../../asw-spec-codex/asw/agent_api.py), [agent API tests](../../asw-spec-codex/tests/test_agent_api.py), [agent guide](AGENT_INTEGRATION.md) | Use placeholders; token is user-issued and local. |
| Native Windows App SDK delivery, process/job, UIA, GUI, and end-to-end paths were exercised. | Runtime verified | [Runtime qualification](../../asw-spec-codex/docs/RUNTIME_QUALIFICATION_2026-08-02.md) | Qualified Windows environment only. |
| Windows runtime qualification used Windows 11 Pro build 22000 and Windows App Runtime 2.3.1. | Runtime verified | [Evidence baseline](../EVIDENCE_BASELINE.md), runtime record | Do not generalize to all Windows versions. |
| ASW detection success was 100%. | Empirically supported | [Frozen aggregate](../evidence/aggregate-summary.json), accepted report | Say “in the accepted controlled evaluation.” |
| Duplicate and false-positive useful-signal rates were 0%. | Empirically supported | [Frozen aggregate](../evidence/aggregate-summary.json) | Do not imply zero duplicates for every deployment. |
| All 3/3 primary classes passed the preregistered 30% median observation-reduction gate; each observed a 50% reduction. | Empirically supported | Aggregate `threshold_audit.layer_a_efficiency`, report | Baseline was mechanically selected `ordinary_notification`; 50% is the observed result, not the gate. |
| Layer B continuation success was 100% for ASW and the selected baseline; ASW improved calls and latency by 50%. | Empirically supported | Aggregate `layer_b`, report | Bounded deterministic/normalized agent; no external-LLM claim. |
| Layer A used zero model calls. | Empirically supported | Aggregate integrity audit and run manifest | This describes the benchmark layer, not every future integration. |
| The secondary crash/restart ASW subject-accuracy result was 0.0. | Limitation / empirical | [Evidence baseline](../EVIDENCE_BASELINE.md), report, whitepaper | Preserve the result; it did not invalidate the primary hard gate. |
| Invalidated runs were retained and excluded from the final classification. | Empirically supported / reproducibility | [Sanitized evaluation report](../evidence/EVALUATION_RESULTS_2026-08-02.md) | Do not silently delete or rewrite failed attempts. |
| ASW supports universal applications, cross-platform behavior, production-scale reliability, or universal agent benefit. | Unsupported and prohibited | RFC non-goals, evidence boundary | This claim must not appear in release prose. |

## Frozen headline

Use this concise form when a public page needs the result:

> In the preregistered controlled RFC 0001 MVP evaluation, ASW achieved 100%
> transition detection with 0% duplicate and false-positive useful-signal
> rates, and reduced median observation effort by 50% relative to the
> mechanically selected best non-ASW baseline across all three primary
> scenario classes. The bounded continuation layer preserved 100% success while
> reducing median observation calls and continuation latency by 50%.

Place this qualifier nearby:

> These results apply to the bounded controlled Windows MVP scenarios and do
> not establish universal application coverage, cross-platform behavior, or
> universal agent benefit.

## Audit status

The Phase 9 public documents use the claim classes above, retain the negative
secondary result, and link to the normative RFC/evidence rather than inventing
new API or product requirements. Mechanical checks cover links, paths, secrets,
package metadata, and frozen-number consistency.
