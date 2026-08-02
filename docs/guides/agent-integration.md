# Agent integration

Normal agent use does not require the developer CLI or GUI scraping. The
reference implementation exposes a loopback JSON endpoint at
`POST /v1/agent`. The GUI issues a per-agent bearer token when a user creates a
grant; the service checks the grant and observation authorization again for
every operation that exposes or mutates scoped data. Capabilities metadata is
available without a grant, and `get_access_grant` reports the current grant or
`null`.

The endpoint is local-only. The port is selected at startup and the endpoint
and token are shown by the GUI's agent-grant flow. Examples below use
placeholders, never real credentials.

## Access model

An agent read is limited to the intersection of:

```text
requested agent subscription
    ∩ active user-issued agent access grant
    ∩ user-authorized observation universe
```

The intersection is enforced at the service boundary. An agent cannot create or
broaden observation authorization. Revoking the grant blocks subsequent reads,
streams, and resumes; a replay cursor is a position, not an authorization
token.

## Transport envelope

```http
POST http://127.0.0.1:<port>/v1/agent
Content-Type: application/json

{
  "token": "<TOKEN_FROM_USER_GRANT>",
  "operation": "get_capabilities",
  "payload": {}
}
```

Every successful response is wrapped by the transport as `{ "ok": true,
"result": ... }`. A forbidden request returns HTTP 403; malformed contract
or unsupported payloads return HTTP 400.

## Capabilities and grant

```json
{
  "token": "<TOKEN_FROM_USER_GRANT>",
  "operation": "get_capabilities",
  "payload": {}
}
```

The logical operations are:

`get_capabilities`, `list_applications`, `get_access_grant`,
`list_subscriptions`, `create_subscription`, `update_subscription`,
`delete_subscription`, `list_signals`, `get_signal`, `open_signal_stream`, and
`resume_signal_stream`.

Read the active grant before creating a subscription:

```json
{
  "token": "<TOKEN_FROM_USER_GRANT>",
  "operation": "get_access_grant",
  "payload": {}
}
```

The grant shape is `asw.agent_access.v1` and includes `applications`,
`categories`, `allow_replay`, `enabled`, and optional `expires_at`.

## Create a bounded subscription

The payload shape matches the implementation fixture and schema. Replace every
placeholder with values present in the active grant and authorization scope.

```json
{
  "token": "<TOKEN_FROM_USER_GRANT>",
  "operation": "create_subscription",
  "payload": {
    "subscription": {
      "schema_version": "asw.subscription.v1",
      "subscription_id": "sub_example",
      "subscriber_id": "agent:example",
      "subscriber_kind": "agent",
      "enabled": true,
      "applications": ["app.example"],
      "categories": ["files", "jobs"],
      "event_types": ["file.saved", "job.completed"],
      "destinations": ["agent_stream"],
      "created_at": "<RFC3339_TIMESTAMP>",
      "updated_at": "<RFC3339_TIMESTAMP>"
    }
  }
}
```

Agent subscriptions use `agent_stream`; Windows notification delivery is a
user-subscription destination. The service rejects subscriptions outside the
grant or outside active observation authorization.

## List and read signals

```json
{
  "token": "<TOKEN_FROM_USER_GRANT>",
  "operation": "list_signals",
  "payload": {
    "subscription_id": "sub_example",
    "limit": 100,
    "after": null
  }
}
```

The result contains `schema_version: "asw.agent_response.v1"`, a bounded
`signals` array, and a `replay_cursor`. `get_signal` takes the same
`subscription_id` plus a `signal_id`; it does not allow an agent to read a
signal through another agent's subscription.

## Open and resume a stream

The request is schema-versioned as `asw.agent_stream_request.v1`:

```json
{
  "token": "<TOKEN_FROM_USER_GRANT>",
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

To resume, set `after` to the returned `asw.replay_cursor.v1` object and use
`resume_signal_stream` as the logical operation. The cursor identifies a
durable journal position and frontier metadata; the service re-evaluates the
grant and authorization intersection on every resume.

## Pagination and errors

Limits are integers from 1 through 1000. Cursors may be used for bounded list
and stream pagination. Common outcomes are:

- `200`: response with schema version and, where applicable, replay cursor;
- `400`: invalid JSON, schema, operation, or request envelope;
- `403`: invalid token, missing/expired/revoked grant, out-of-scope
  subscription, disabled subscription, or cursor belonging to another agent;
- `404`: path other than `/v1/agent`;
- `500`: bounded transport failure; the server does not expose internal error
  details.

For normative contracts and operation names, see [RFC 0001 section 18](../rfc/RFC-0001.md#18-agent-interface)
and the [agent reference](../reference/agent-api.md).
