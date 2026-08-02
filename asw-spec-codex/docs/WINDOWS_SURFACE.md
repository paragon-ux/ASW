# Windows Surface

## Product priority

ASW is a Windows GUI product with a structured agent interface. Windows App SDK notifications are a delivery channel. The CLI, if present, is diagnostic tooling.

## Activity

Default home surface. Group signals by application and show newest signals first. Recommended row content:

- application icon/name;
- signal summary;
- category/status;
- relative/absolute time;
- optional subject (file, job, artifact, dialog);
- source reliability only in details unless degraded/important.

## Subscriptions

User-facing categories SHOULD be plain language:

- Files
- Jobs
- Processes
- Artifacts
- Diagnostics
- Windows & UI
- Application operations
- Shared artifacts
- Source health

The UI SHOULD let users choose Activity and Windows notification delivery where applicable.

## Applications

Show each application, observation state, source health, subscription summary, and link to permissions.

## Sources & Permissions

This surface owns observation authorization. It should make it visually clear that selecting a folder/process/UI surface changes what ASW may observe, while changing a subscription only changes what is surfaced.

## Agents

Show connected/registered agents, active access grants, allowed applications/categories, active subscriptions, and a revoke action. Do not let agents silently expand these grants.

## UI Automation coordinates

Coordinates use Windows virtual-screen physical pixels and preserve localization uncertainty. Physical rectangles are evidence, not durable UI identity.
