# MVP Scope

## In scope

- Windows 11 desktop.
- GUI-first management and activity experience.
- Explicit application registration/discovery.
- User-authorized filesystem roots.
- Registered process/job observation.
- Registered UI Automation windows/dialogs/controls.
- Explicit application and diagnostic adapter contracts.
- Deterministic event-to-signal reduction.
- Signal history grouped by application.
- User subscriptions by application/category/event type.
- Agent access grants plus agent subscriptions.
- Local structured agent read/stream/replay interface.
- Windows App SDK notification delivery for user subscriptions.
- Append-only JSONL journal plus rebuildable caches.

## Out of scope

- Global desktop interception.
- Unbounded filesystem/process watching.
- General GUI automation.
- Screenshot semantic inference.
- Remote/multi-machine replication.
- Agent-created observation permissions.
- Requirement satisfaction or recommendations.
- Mandatory end-user or agent CLI.

## MVP user journey

1. User opens Applications and enables an application.
2. User authorizes relevant files/processes/UI sources in Sources & Permissions.
3. Activity begins showing canonical signals grouped under that application.
4. User creates a subscription for Windows notifications and/or Activity emphasis.
5. User grants an agent access to selected applications/categories.
6. Agent creates a narrower subscription and reads/resumes the structured stream.
