# User guide

ASW has five top-level GUI surfaces. The normal journey is:

`Observe -> event -> signal -> Subscribe -> deliver/read`

The words are intentionally different: authorization controls collection;
subscriptions control presentation; a canonical signal is created by the
deterministic service from eligible authorized observations.

## Activity

Activity is the default view. It groups canonical signal history by
application and shows newest signals first. A row can include the category,
status, summary, and subject such as a path, job, artifact, dialog, or
operation.

Activity is a projection over signal history. It is not the journal itself, and
the absence of a matching subscription does not prevent an authorized signal
from being created.

## Subscriptions

Subscriptions choose which existing signals a subscriber wants to see. A user
subscription can select:

- one or more applications;
- categories such as `files`, `artifacts`, `processes`, `jobs`, `windows_ui`,
  `application`, `diagnostics`, `shared_artifacts`, or `source_health`;
- user destinations such as `activity_center` and `windows_app_sdk`.

The current GUI writes an empty `event_types` filter. The structured agent
contract supports optional event-type filters; see [Agent integration](AGENT_INTEGRATION.md)
for an example.

Changing a subscription does not change observation authorization or canonical
signal history.

## Applications

Applications are the primary grouping identity. This view shows registered
applications, observation status, and source health, and provides the
**Register application** action. Use the top-level **Sources & Permissions**
and **Subscriptions** pages for those separate workflows. A source can be
registered to an application; ASW does not guess application-specific semantics
from arbitrary text.

## Sources & Permissions

This view controls **observation authorization**. Authorize only the sources
needed for the workflow. The MVP supports bounded authorization for:

- filesystem roots;
- registered executable/process and job identities;
- eligible UI Automation process surfaces;
- explicit application adapter contracts; and
- explicit diagnostic adapter contracts.

Filesystem activity is a hint until settling/reconciliation completes. An
unstable artifact does not become `artifact.available`. A degraded source must
reconcile before it returns healthy. Revoking authorization stops future
ordinary observations in that scope; historical signals may remain according
to retention policy.

## Agents

Agents are optional subscribers. A user first grants an agent a set of
applications and categories. The agent can then create or manage its own
subscriptions only inside that grant and the user-authorized observation
universe.

The **Agents** view displays the grant and provides revoke. Revocation is
enforced server-side and blocks later list, read, stream, and resume operations.
Data already returned to an agent cannot be recalled.

## Notifications and delivery

Windows App SDK notifications are an optional user delivery channel. They are
not the source of truth and do not replace Activity/history. If a platform
send fails, ASW records the delivery result while retaining the canonical
signal.

## Permissions in plain language

- **Observe:** what ASW may collect from a bounded source.
- **Signal:** the deterministic canonical record ASW creates from eligible
  observations.
- **Subscribe:** which application/category/event selections a user or agent
  wants to receive or read.
- **Deliver/read:** Activity, an optional Windows notification, or the bounded
  local agent interface.

For normative semantics, use [RFC 0001](../../asw-spec-codex/RFC-0001.md). For
privacy and authority boundaries, see [Security and privacy](SECURITY_AND_PRIVACY.md).
