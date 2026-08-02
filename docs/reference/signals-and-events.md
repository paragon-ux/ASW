# Reducer Policy

## Purpose

The reducer converts authorized, sufficiently reliable events into canonical signals. It is deterministic, finite, and versioned.

## Inputs

```text
event
+ observation authorization
+ application registration
+ source health/reliability
+ prior signal state
+ reducer policy version
```

Subscriptions and agent access grants are **not reducer inputs**. They are post-reduction read/delivery filters.

## Default behavior

`default_action` MUST be `reject`. Unknown event types, unsupported versions, invalid payloads, unauthorized sources, degraded facts, and unmatched rules fail closed.

## Signal emission

A rule may emit a signal only from reliable eligible facts. The emitted signal keeps source reliability and provenance. Rules may define deterministic dedupe/supersession keys.

## Prohibited behavior

The reducer MUST NOT:

- call an LLM/model;
- use stochastic classification;
- infer subscriber interest;
- infer task success beyond the source's narrow declared fact;
- infer workflow blocking or next actions;
- inspect subscription state to decide whether canonical history exists.

## Versioning

Policy changes require a new `policy_version`. Replay that aims to reproduce historical outputs MUST use the policy version recorded in the relevant frontier/journal inputs.
