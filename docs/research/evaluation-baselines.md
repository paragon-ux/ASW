# Baseline Contracts

All baseline outputs normalize to the same trial-result envelope, but each observer may use only the information allowed below.

## B1 — Polling

Periodically query scenario-appropriate observable state at the fixed `poll_interval_ms` from the frozen profile.

Examples: process existence/exit status where ordinarily queryable, file metadata/content state, UI state query.

Each query increments `observation_count`.

## B2 — Filesystem watching alone

Use a raw filesystem watcher without ASW reducer/application/job/UI semantics.

It is applicable to file/artifact scenarios. For non-filesystem scenarios, record `not_applicable` rather than inventing equivalent semantics.

## B3 — Ordinary notification text

The scenario emits a human-oriented text notification containing only the predeclared text fields. It does not include ASW structured event type, frontier, structured subject, application grouping metadata, or replay cursor unless that information is literally part of the ordinary message contract.

The plain text template MUST be frozen before runs.

Under the frozen Layer B protocol, the ordinary-notification condition counts
two observations: (1) notification receipt and (2) parsing/interpretation.
Subscription setup and controlled event publication are excluded.

## B4 — Repeated observation

Repeatedly inspect the relevant application/environment surface using the same bounded observation interval/budget declared in the profile. It represents explicit rechecking rather than event subscription.

## B5 — ASW

Consume only public ASW subscription/list/stream interfaces under normal authorization/grant semantics. Do not read reducer internals or the authoritative journal as a shortcut.

## Best-baseline selection for Layer B

For each primary scenario class, select the non-ASW baseline with:

1. highest detection success rate;
2. then lowest miss rate;
3. then lowest median observation count;
4. then lowest median detection latency.

Ties are resolved by fixed baseline ID lexical order.

The rule is applied mechanically after Layer A; it MUST NOT be changed after inspecting agent results.
