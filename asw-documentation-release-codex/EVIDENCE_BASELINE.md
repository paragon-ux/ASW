# Accepted evidence baseline

Phase 9 MUST treat the following as the accepted evidence baseline unless the repository contains a later explicitly signed-off replacement.

## Core implementation

Accepted core commit:

`7d6e267c6e89cdcd8a71644c67c95d2ab4260330`

The completed core hard gate reports all applicable RFC 0001 implementation items passed, including GUI-first product surfaces, bounded Windows sources, canonical signals, user/agent subscriptions, agent access grants, append-only journal/replay, Windows App SDK delivery, physical-pixel UIA coordinates, and the structured local agent interface.

## Windows runtime qualification

Accepted runtime environment:

- Microsoft Windows 11 Pro
- version `10.0.22000`, build `22000`, 64-bit
- Windows App Runtime `2.3.1`

Runtime evidence includes successful:

- native `AppNotificationManager.Show()`;
- registered process/job success and failure transitions;
- real UI Automation window/dialog/control observations;
- `windows_virtual_screen_physical_px` coordinate evidence;
- five-page GUI smoke journey;
- filesystem → canonical signal → Windows delivery → agent read flow;
- grant revocation returning 403;
- degradation/reconciliation recovery.

## Phase 8 evaluation

Accepted final run:

`asw-mvp-eval-20260802-05`

Final classification:

`SUPPORTED`

Frozen empirical results:

- ASW detection success: `100%`;
- duplicate useful-signal rate: `0%`;
- false-positive useful-signal rate: `0%`;
- application attribution accuracy: `100%` where applicable;
- event-kind accuracy: `100%`;
- Layer A: all `3/3` primary scenario classes passed the efficiency gate;
- Layer A observation reduction: `50%` versus the mechanically selected best non-ASW baseline in each primary class;
- Layer B continuation success: `100%` for ASW and the selected baseline;
- Layer B ASW median observation calls: `1` versus `2` for the selected baseline;
- Layer B ASW median continuation latency: `20 ms` versus `40 ms` for the selected baseline;
- Layer B observation-call improvement: `50%`;
- Layer B continuation-latency improvement: `50%`;
- authorization violations: `0`;
- replay violations: `0`;
- Layer A model calls: `0`;
- final raw trial count: `736`;
- independent ground-truth records: `158`;
- agent-usage records: `36`.

The mechanically selected best non-ASW baseline for all three primary scenario classes was `ordinary_notification`.

## Claim boundary

The supported claim is intentionally bounded:

> Under the preregistered controlled RFC 0001 Windows MVP scenarios, structured ASW signals preserved perfect transition recognition and continuation success while reducing median observation effort by 50% relative to the mechanically selected best non-ASW baseline across all three primary scenario classes; the bounded continuation layer likewise reduced median observation calls and continuation latency by 50% without a success regression.

Phase 9 MUST NOT rewrite this into claims of:

- universal application coverage;
- universal agent benefit;
- general cross-platform superiority;
- statistically established population-level effect outside the controlled MVP scenarios;
- production-scale reliability beyond the tested conditions;
- replacement of accessibility APIs, UI Automation, Windows notifications, or application-native APIs.

## Secondary result to preserve

The secondary `crash-restart` aggregate reports `subject_accuracy: 0.0` for ASW. This was not a primary hard-gate metric and did not invalidate the bounded `SUPPORTED` classification. Public technical documentation SHOULD preserve this as a secondary limitation/result rather than hiding it.
