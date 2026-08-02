"""GUI-first Tk desktop surface; all edits delegate to the local service."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import uuid
import re

from .service import utc_now


def grouped_activity(service):
    groups = {}
    for signal in sorted(service.signals, key=lambda item: item["created_at"], reverse=True):
        groups.setdefault(signal["application_id"], []).append(signal)
    return groups


class ASWWindow(ttk.Frame):
    """Five required top-level views, with Activity as the default view."""

    PAGES = ("Activity", "Subscriptions", "Applications", "Sources & Permissions", "Agents")

    def __init__(self, root: tk.Tk, service, agent_server=None) -> None:
        super().__init__(root, padding=12); self.service = service; self.agent_server = agent_server; self.pack(fill="both", expand=True)
        self.title = ttk.Label(self, font=("Segoe UI", 18, "bold")); self.title.pack(anchor="w")
        nav = ttk.Frame(self); nav.pack(fill="x", pady=(8, 12))
        for page in self.PAGES: ttk.Button(nav, text=page, command=lambda page=page: self.show(page)).pack(side="left", padx=(0, 6))
        self.actions = ttk.Frame(self); self.actions.pack(fill="x", pady=(0, 8))
        self.body = ttk.Treeview(self, columns=("application", "category", "status", "summary"), show="headings")
        for col in ("application", "category", "status", "summary"): self.body.heading(col, text=col.title())
        self.body.pack(fill="both", expand=True); self.show("Activity")

    def show(self, page: str) -> None:
        self.title.configure(text=page)
        for child in self.actions.winfo_children(): child.destroy()
        self.body.delete(*self.body.get_children())
        if page == "Activity":
            for application_id, signals in grouped_activity(self.service).items():
                parent = self.body.insert("", "end", iid="group:" + application_id, values=(application_id, "application", "", f"{len(signals)} signal(s)"), open=True)
                for signal in signals:
                    self.body.insert(parent, "end", values=(signal["application_id"], signal["category"], signal["status"], signal["summary"]))
        elif page == "Applications":
            ttk.Button(self.actions, text="Register application", command=self.register_application).pack(side="left")
            for app in self.service.applications.values():
                health = ", ".join(sorted({self.service.source_health.get(source["source_id"], "healthy") for source in self.service.sources.values() if source["application_id"] == app["application_id"]})) or "no source"
                self.body.insert("", "end", values=(app["display_name"], "observation", health, "enabled" if app["enabled"] else "disabled"))
        elif page == "Sources & Permissions":
            ttk.Button(self.actions, text="Authorize observation scope", command=self.authorize_scope).pack(side="left")
            ttk.Button(self.actions, text="Revoke selected authorization", command=self.revoke_authorization).pack(side="left")
            for auth in self.service.authorizations.values():
                self.body.insert("", "end", iid=auth["authorization_id"], values=(auth["authorization_id"], "Observe", "enabled" if auth["enabled"] else "revoked", f"{len(auth['scopes'])} scope(s)"))
        elif page == "Agents":
            ttk.Button(self.actions, text="Grant agent access", command=self.grant_agent).pack(side="left")
            ttk.Button(self.actions, text="Revoke selected grant", command=self.revoke_grant).pack(side="left", padx=(6, 0))
            for grant in self.service.grants.values():
                self.body.insert("", "end", iid=grant["grant_id"], values=(grant["agent_subscriber_id"], "access grant", "enabled" if grant["enabled"] else "revoked", ", ".join(grant["categories"])))
        else:
            ttk.Button(self.actions, text="Create subscription", command=self.create_subscription).pack(side="left")
            ttk.Button(self.actions, text="Disable selected", command=self.disable_subscription).pack(side="left", padx=(6, 0))
            for sub in self.service.subscriptions.values(): self.body.insert("", "end", iid=sub["subscription_id"], values=(sub["subscriber_id"], "subscription", "enabled" if sub["enabled"] else "disabled", ", ".join(sub["categories"]) + " → " + ", ".join(sub["destinations"])))

    def register_application(self) -> None:
        name = simpledialog.askstring("Application", "Display name:", parent=self)
        if not name: return
        app_id = "app." + re.sub(r"[^A-Za-z0-9._-]+", "-", name.lower()).strip("-")
        self.service.record("application", {"schema_version": "asw.application.v1", "application_id": app_id, "display_name": name, "identity": {"kind": "registered"}, "enabled": True, "registered_at": utc_now()})
        self.show("Applications")

    def create_subscription(self) -> None:
        applications = list(self.service.applications)
        if not applications: messagebox.showinfo("Subscriptions", "Register an application first.", parent=self); return
        selected_apps = self._csv_dialog("Applications", applications)
        categories = self._csv_dialog("Categories", ["files", "artifacts", "processes", "jobs", "windows_ui", "application", "diagnostics", "shared_artifacts", "source_health"])
        destinations = self._csv_dialog("Destinations", ["activity_center", "windows_app_sdk"])
        if not selected_apps or not categories or not destinations: return
        self.service.register_subscription({"schema_version": "asw.subscription.v1", "subscription_id": "sub_" + uuid.uuid4().hex, "subscriber_id": "user:local", "subscriber_kind": "user", "enabled": True, "applications": selected_apps, "categories": categories, "event_types": [], "destinations": destinations, "created_at": utc_now(), "updated_at": utc_now()})
        self.show("Subscriptions")

    def _csv_dialog(self, title: str, choices: list[str]) -> list[str]:
        value = simpledialog.askstring(title, "Choose comma-separated values:\n" + ", ".join(choices), parent=self)
        if value is None: return []
        selected = [item.strip() for item in value.split(",") if item.strip()]
        if not selected or any(item not in choices for item in selected):
            messagebox.showerror(title, "Choose only the listed values.", parent=self); return []
        return list(dict.fromkeys(selected))

    def disable_subscription(self) -> None:
        selected = self.body.selection()
        if not selected or selected[0] not in self.service.subscriptions: return
        sub = dict(self.service.subscriptions[selected[0]]); sub["enabled"] = False; sub["updated_at"] = utc_now()
        self.service.register_subscription(sub); self.show("Subscriptions")

    def authorize_scope(self) -> None:
        applications = list(self.service.applications)
        if not applications: messagebox.showinfo("Sources & Permissions", "Register an application first.", parent=self); return
        app = self._csv_dialog("Application", applications)
        if len(app) != 1: return
        source_kind = simpledialog.askstring("Source kind", "filesystem, process_job, uia, application, or diagnostic:", parent=self)
        if source_kind not in {"filesystem", "process_job", "uia", "application", "diagnostic"}: return
        source_id = simpledialog.askstring("Source", "Source id:", parent=self)
        if not source_id: return
        scope = {"application_id": app[0], "source_id": source_id, "source_kind": source_kind, "filesystem_roots": [], "executable_names": [], "job_kinds": [], "uia_process_names": [], "adapter_contract": None}
        configuration = {}
        adapter = "filesystem"
        if source_kind == "filesystem":
            root = simpledialog.askstring("Filesystem root", "Authorized root:", parent=self)
            if not root: return
            scope["filesystem_roots"] = [root]; configuration = {"roots": [root], "recursive": True}
        elif source_kind == "process_job":
            adapter = simpledialog.askstring("Adapter", "process or job:", parent=self) or ""
            if adapter == "process":
                name = simpledialog.askstring("Process", "Executable name:", parent=self)
                if not name: return
                scope["executable_names"] = [name]; configuration = {"executable_names": [name]}
            elif adapter == "job":
                kind = simpledialog.askstring("Job", "Job kind:", parent=self)
                if not kind: return
                executable = simpledialog.askstring("Job process", "Executable name that runs this job:", parent=self)
                if not executable: return
                scope["job_kinds"] = [kind]; scope["executable_names"] = [executable]
                configuration = {"job_kinds": [kind], "executable_names": [executable]}
            else: return
        elif source_kind == "uia":
            name = simpledialog.askstring("UI Automation", "Process name:", parent=self)
            if not name: return
            scope["uia_process_names"] = [name]; configuration = {"uia_process_names": [name]}; adapter = "uia"
        else:
            contract = simpledialog.askstring("Adapter contract", "Explicit contract id:", parent=self)
            if not contract: return
            scope["adapter_contract"] = contract; configuration = {"adapter_contract": contract}; adapter = source_kind
        auth_id = "auth_" + uuid.uuid4().hex
        self.service.record("observation_authorization", {"schema_version": "asw.observation_authorization.v1", "authorization_id": auth_id, "authorized_by": "user:local", "enabled": True, "scopes": [scope], "created_at": utc_now(), "updated_at": utc_now()})
        registration = {"schema_version": "asw.source_registration.v1", "source_id": source_id, "adapter": adapter, "application_id": app[0], "enabled": True, "authorization_id": auth_id, "configuration": configuration, "settle_profile": {"initial_delay_ms": 250, "poll_interval_ms": 100, "required_stable_observations": 2, "maximum_settle_ms": 5000, "stability_mode": "metadata"} if adapter == "filesystem" else None, "registered_at": utc_now()}
        self.service.record("source_registration", registration); self.show("Sources & Permissions")

    def revoke_authorization(self) -> None:
        selected = self.body.selection()
        if not selected: return
        auth = dict(self.service.authorizations[selected[0]]); auth["enabled"] = False; auth["updated_at"] = utc_now()
        self.service.record("observation_authorization", auth); self.show("Sources & Permissions")

    def grant_agent(self) -> None:
        agent = simpledialog.askstring("Agent access", "Agent name:", parent=self)
        if not agent: return
        subscriber_id = "agent:" + agent.replace(" ", "-")
        if subscriber_id not in self.service.subscribers:
            self.service.record("subscriber", {"schema_version": "asw.subscriber.v1", "subscriber_id": subscriber_id, "kind": "agent", "display_name": agent, "enabled": True, "created_at": utc_now()})
        applications = list(self.service.applications)
        if not applications: messagebox.showinfo("Agent access", "Register an application first.", parent=self); return
        authorized_applications = [app for app in applications if self.service.application_authorized(app)]
        selected_apps = self._csv_dialog("Agent applications", authorized_applications)
        selected_categories = self._csv_dialog("Agent categories", ["files", "artifacts", "processes", "jobs", "windows_ui", "application", "diagnostics", "shared_artifacts", "source_health"])
        if not selected_apps or not selected_categories: return
        self.service.record("agent_access", {"schema_version": "asw.agent_access.v1", "grant_id": "grant_" + uuid.uuid4().hex, "agent_subscriber_id": subscriber_id, "enabled": True, "applications": selected_apps, "categories": selected_categories, "allow_replay": True, "created_at": utc_now(), "expires_at": None})
        if self.agent_server is not None:
            token = self.agent_server.issue_token(subscriber_id)
            messagebox.showinfo("Agent access", f"Local endpoint: {self.agent_server.endpoint}\nBearer token (copy now):\n{token}", parent=self)
        self.show("Agents")

    def revoke_grant(self) -> None:
        selected = self.body.selection()
        if not selected: return
        grant = next((dict(item) for item in self.service.grants.values() if item["grant_id"] == selected[0]), None)
        if grant is None: return
        grant["enabled"] = False; self.service.record("agent_access", grant)
        if self.agent_server is not None: self.agent_server.revoke_agent(grant["agent_subscriber_id"])
        self.show("Agents")


def launch(service, agent_server=None) -> None:
    root = tk.Tk(); root.title("Application Signals for Windows")
    ASWWindow(root, service, agent_server); root.mainloop()
