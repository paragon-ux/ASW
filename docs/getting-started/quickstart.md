# Five-minute first run

This is the shortest useful path through the GUI. It assumes the dependencies are installed as described in [Installation](installation.md).

## 1. Launch

```powershell
Set-Location <repo-root>
.\.venv\Scripts\python.exe scripts\main.py
```

ASW opens on **Activity**. The local service and optional loopback agent endpoint start with the GUI.

## 2. Register an application

Open **Applications**, choose **Register application**, and give the application a stable display name. Application identity is the grouping and subscription key; source registrations can contribute to the same application.

## 3. Authorize observation

Open **Sources & Permissions** and choose **Authorize observation scope**. Pick the smallest scope that answers the use case:

- a filesystem root for settled file transitions;
- a registered executable or job identity for process/job transitions;
- a registered UI Automation process for eligible windows, dialogs, or operations; or
- an explicit application/diagnostic adapter contract.

This is the **Observe** decision. It controls what ASW may collect. It is not a notification preference.

## 4. Choose what to surface

Open **Subscriptions**, select the authorized application and signal categories such as Files, Jobs, Artifacts, Processes, Windows & UI, or Diagnostics, and choose `activity_center` or (where supported) `windows_app_sdk`.

This is the **Subscribe** decision. It filters existing canonical signal history; it cannot expand observation authorization or create a signal.

## 5. Watch Activity

Return to **Activity**. Signals are grouped by application and newest signals appear first. A Windows notification, if enabled and available, is a delivery copy of a canonical signal. Delivery failure does not delete the signal from Activity/history.

## 6. Add an agent only when needed

Open **Agents**, grant an agent the smallest application/category scope that it needs, and copy the local credential once. The [agent integration guide](../guides/agent-integration.md) shows the actual loopback operations and cursor flow. Revoking the grant stops subsequent agent reads and streams at the service boundary.

If an expected signal does not appear, check [Troubleshooting](../guides/troubleshooting.md) and [Known limitations](../reference/limitations.md) before widening authorization.
