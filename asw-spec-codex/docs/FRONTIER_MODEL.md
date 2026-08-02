# Frontier Model

## Definition

A frontier is the **ASW-local replay and ordering boundary** for observations and signal reducer outputs. It may cite source-specific cursors, epochs, snapshots, or reconciliation identities, but RFC 0001 does not require distributed shared-state frontiers.

The frontier is intentionally local and implementation-neutral. It exists to answer: "up to what durable ASW journal position and source state has this observation/reduction/read been processed?"

## Canonical fields

```json
{
  "journal_sequence": 9188,
  "runtime_epoch": "uuid-runtime-1",
  "source_frontiers": {
    "fs:workspace": {
      "source_epoch": "uuid-fs-3",
      "source_sequence": 42,
      "snapshot_digest": "sha256:optional"
    }
  },
  "reducer_policy_version": "asw.reducer.v1"
}
```

- `journal_sequence` is durable and monotonically increasing within one journal.
- `runtime_epoch` identifies a service runtime instance; it changes on restart.
- `source_epoch` changes after discontinuity/reconciliation when needed.
- `source_sequence` is source-local provenance, not the global order.
- `snapshot_digest` is optional reconciliation identity.
- `reducer_policy_version` pins deterministic replay semantics.

## Replay cursor

A replay cursor wraps a frontier and subscriber context where needed. Durable replay is keyed primarily by `journal_sequence`; runtime/source epochs make discontinuities explicit rather than ambiguous.

## Reducer invariant

Every signal reducer output MUST be reproducible from authoritative journal inputs, source frontier metadata, observation authorization, application registrations, and the exact reducer-policy version.
