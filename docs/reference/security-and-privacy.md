# Security, privacy, and authority boundaries

ASW is a local Windows MVP. It is not a cloud authorization service, remote
multi-user access-control system, general sandbox, or arbitrary desktop
interceptor. The security boundary is the combination of explicit local user
authorization, deterministic reduction, and server-side agent scope checks.

## Observation authority

Users authorize the application, folder, executable/job identity, UI Automation
surface, or explicit adapter contract that ASW may observe. Authorization is
persisted separately from source health and subscriptions. A subscription
cannot add a root, process, UI surface, application, or adapter contract.

Source adapters are bounded to registered scopes. Filesystem events are hints
until settle/reconciliation; unsupported, unauthorized, invalid, hint-only, or
degraded facts fail closed for ordinary signal creation. UI Automation is
limited to eligible authorized registered surfaces. Process/job observation is
limited to registered executable identities.

## Agent authority

An agent must have a user-issued access grant. Its effective scope is:

```text
requested subscription
    ∩ active user-issued grant
    ∩ user-authorized observation universe
```

This intersection is enforced by the service for application and subscription
listings, subscription mutation, signal list/read, stream, and resume
operations. `get_capabilities` is unscoped operation metadata, and
`get_access_grant` returns the current grant or `null`; neither operation
exposes signal data. Grant revocation or expiry blocks subsequent scoped data
access at the service boundary. Previously returned data cannot be recalled.

The reference agent transport binds to loopback (`127.0.0.1`, `localhost`, or
`::1`) and uses a bearer token issued by the user grant flow. Protect the token
like a local credential and never place a real token in documentation, tests,
issues, or logs.

## Journal and local data

The append-only JSONL journal is authoritative for local replay. It may contain
filesystem paths, application identifiers, process/job metadata, UI metadata,
source health, and delivery audit records. Protect the journal using ordinary
local account and filesystem controls. Do not publish raw journals or local
evaluation output unless they have been scanned for secrets and machine-specific
paths.

Indexes and caches are derived. Replay reconstructs ASW state and does not
rewrite files, launch processes, manipulate applications, or replay UI actions.

## Delivery and failure behavior

Windows App SDK notification delivery is a user-facing channel, not signal
authority. Delivery failure is recorded separately and does not delete or
invalidate the canonical signal. A source that cannot guarantee completeness
remains degraded until reconciliation succeeds.

## Out of scope

The MVP does not provide remote agent authorization, cloud isolation, arbitrary
screen capture, universal application semantics, a replacement for UI
Automation or native application APIs, or a claim that every Windows
application is observable. Those are non-goals, not implied protections.

For the complete normative boundary, see [RFC 0001](../rfc/RFC-0001.md)
and the [agent integration guide](../guides/agent-integration.md).
