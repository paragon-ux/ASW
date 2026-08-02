# Agent API reference

## Principle

Agents consume ASW through a local structured protocol, not by scraping the GUI and not by requiring shell CLI commands.

The reference runtime exposes the logical operations over a loopback HTTP JSON
endpoint at `POST /v1/agent`. The GUI issues a per-agent bearer token when a
grant is created; the token is mapped to the granted subscriber before any
operation reaches the service. The transport is optional and does not become
journal authority.

## Access sequence

1. A user creates an agent subscriber registration and access grant in the GUI.
2. The agent authenticates/identifies to the local service using implementation-defined local credentials.
3. The agent reads its current access grant.
4. The agent creates one or more subscriptions within that grant.
5. The agent reads a bounded snapshot and/or opens a signal stream.
6. The agent resumes using a replay cursor after interruption.

## Required logical operations

- `get_capabilities`
- `list_applications`
- `get_access_grant`
- `list_subscriptions`
- `create_subscription`
- `update_subscription`
- `delete_subscription`
- `list_signals`
- `get_signal`
- `open_signal_stream`
- `resume_signal_stream`

Transport request envelope:

```json
{
  "token": "<user-issued-local-token>",
  "operation": "open_signal_stream",
  "payload": {
    "schema_version": "asw.agent_stream_request.v1",
    "agent_subscriber_id": "agent:example",
    "subscription_ids": ["sub_example"],
    "after": null,
    "limit": 100
  }
}
```

## Access enforcement

For every agent query/stream, the service computes:

```text
requested subscription
∩ active agent access grant
∩ user-authorized observation universe
```

Only signals inside the intersection may be returned. Server-side enforcement is mandatory.

## Boundedness

Snapshot/list operations MUST support a maximum result limit and replay cursor. Stream payloads MUST be schema-versioned and include frontier metadata.
