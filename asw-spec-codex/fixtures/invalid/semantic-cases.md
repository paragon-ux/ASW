# Semantic fail-closed cases

These constraints span multiple records and therefore are not fully expressible by one JSON Schema. The implementation MUST test them explicitly.

1. Agent subscription applications/categories exceed the active agent access grant → reject the subscription.
2. Agent access grant includes an application that is not currently user-authorized → grant may exist administratively, but no signal outside active observation authorization may be read/delivered.
3. Agent stream requests a subscription owned by another subscriber → reject.
4. User subscription is allowed to choose Windows delivery; agent subscription is not.
5. Subscription existence or absence does not change whether an authorized event becomes canonical signal history.
6. Revoked observation authorization stops future ordinary source signals for that scope.
7. Revoked agent grant stops subsequent agent list/stream/resume access.
8. Degraded/hint event cannot become an ordinary final signal.
9. Artifact settle timeout cannot become `artifact.available`.
10. Source cannot return healthy after degradation until deterministic reconciliation succeeds.
11. Replay with the same authoritative inputs and reducer policy reproduces materially equivalent signals.
12. Deleting derived indexes/caches does not alter signal history semantics.
