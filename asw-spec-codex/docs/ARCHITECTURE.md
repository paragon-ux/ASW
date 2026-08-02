# Architecture

## Layers

```text
┌───────────────────────────────────────────┐
│ Windows GUI                               │
│ Activity · Subscriptions · Applications   │
│ Sources & Permissions · Agents            │
└──────────────────────┬────────────────────┘
                       │
┌──────────────────────▼────────────────────┐
│ Subscription/access service               │
│ user subscriptions · agent grants         │
│ agent subscriptions · delivery matching   │
└──────────────────────┬────────────────────┘
                       │
┌──────────────────────▼────────────────────┐
│ Canonical signal service                  │
│ deterministic reducer · correlation       │
│ dedupe · supersession · replay            │
└──────────────────────┬────────────────────┘
                       │
┌──────────────────────▼────────────────────┐
│ Observation service                       │
│ user authorization · source adapters      │
│ settle · health · reconciliation           │
└──────────────────────┬────────────────────┘
                       │
┌──────────────────────▼────────────────────┐
│ Journal                                   │
│ append-only authoritative JSONL inputs    │
│ rebuildable indexes/projections           │
└───────────────────────────────────────────┘
```

## Critical separation

Observation authorization and subscriptions are different state machines.

- **Authorization** answers: may ASW observe this surface?
- **Signal reduction** answers: does this valid authorized observation become a canonical signal?
- **Subscription matching** answers: should this existing signal be delivered/read for this subscriber?

No subscription may expand authorization. No subscription participates in canonical signal existence.

## Application identity

Application identity is the primary GUI grouping and subscription key. Sources may be many-to-one with an application. System/source-health facts that have no normal application may use the system-defined `asw.system` identity; other unattributed facts use `unknown`.

## Trust boundaries

1. Source adapters are trusted only for narrow registered facts.
2. Reducer policy is deterministic and versioned.
3. User observation authorization is authoritative.
4. Agent access grants are authoritative access boundaries.
5. GUI and agent streams are projections over canonical history, not competing histories.
