# ASW whitepaper specification

## Working title

**Application Signals for Windows: Deterministic Signals for Bounded Asynchronous Desktop Workflows**

Alternative subtitle:

**Design and Controlled Evaluation of a Local Windows Signal Layer for Users and Agents**

## Audience

- systems/agent researchers;
- developer-tool and desktop-platform engineers;
- agent infrastructure builders;
- accessibility/automation researchers interested in structured environmental evidence.

## Paper type

A concise systems/empirical whitepaper. Target roughly 6,000–9,000 words, excluding appendices/references. Do not inflate length merely to appear academic.

## Canonical artifact

The published paper is [`WHITEPAPER.md`](WHITEPAPER.md). This file is the
Phase 9 writing specification and is not itself a public research result.

## Core contribution framing

The paper should present three contributions:

1. **A deterministic signal architecture:** bounded Windows observations are reduced into canonical application signals independently of subscriptions and delivery.
2. **An explicit authority model:** users authorize observation; users and agents subscribe separately; agent access is bounded by user-issued grants and authorized observation scope.
3. **A controlled empirical result:** under preregistered RFC 0001 scenarios, ASW preserved correctness while materially reducing observation/continuation effort versus the mechanically selected best non-ASW baseline.

## Required methodology detail

Explain:

- controlled deterministic probe transition timelines versus direct
  canonical-signal injection; live OS behavior comes from runtime
  qualification;
- independent monotonic ground truth;
- frozen profile/digest and preregistration;
- primary scenario classes: job completion, file/artifact transition, UI transition;
- secondary render/export and crash/restart probes;
- conditions: polling, filesystem watch where applicable, ordinary notification, repeated observation, ASW;
- mechanical best-baseline selection;
- Layer A zero-model-call systems benchmark;
- Layer B bounded continuation comparison;
- invalidated runs and why retaining them matters;
- deterministic aggregation/reproducibility.

## Required result tables

At minimum:

### Primary headline table

| Metric | ASW result |
|---|---:|
| Detection | 100% |
| Duplicate useful-signal rate | 0% |
| False-positive useful-signal rate | 0% |
| Attribution accuracy | 100% |
| Kind accuracy | 100% |
| Primary classes meeting efficiency gate | 3/3 |
| Median observation reduction vs selected baseline | 50% |
| Layer B continuation success | 100% |
| Layer B observation-call improvement | 50% |
| Layer B continuation-latency improvement | 50% |

### Primary class comparison

Show ASW vs the selected `ordinary_notification` baseline for the three primary classes.

## Limitations/threats to validity

Must include:

- bounded Windows 11 MVP scope;
- controlled probes rather than broad third-party application population;
- small bounded Layer B continuation agent;
- no external-LLM generalization claim;
- no cross-platform claim;
- selected baseline behavior depends on the frozen contracts and budgets;
- secondary crash/restart subject-accuracy weakness;
- production-scale workload/long-duration behavior not established by this experiment.

## References

Use RFC 0001 and repository artifacts as primary internal references. For external Windows API claims, prefer official Microsoft documentation and add external references only when needed for technical background.
