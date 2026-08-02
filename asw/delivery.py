"""Optional Windows notification delivery boundary with canonical-signal isolation."""

from __future__ import annotations

import html
import importlib
from collections.abc import Callable
from typing import Any


class WindowsAppSdkSender:
    """Best-effort production bridge to the Windows App SDK WinRT projection.

    The projection is optional for non-Windows development and test hosts.  If
    it is installed, the sender constructs a bounded ToastGeneric payload and
    invokes the AppNotificationManager.  The callable transport hook keeps the
    same boundary deterministic in integration tests.
    """

    def __init__(self, transport: Callable[[dict[str, Any]], None] | None = None) -> None:
        self._transport = transport
        self._bootstrap_shutdown: Callable[[], None] | None = None
        self._module = None
        self._manager = None
        self._notification_type = None
        self.unavailable_reason: str | None = None
        if transport is not None:
            return
        try:
            # PyWinRT exposes the Windows App SDK bootstrapper separately from
            # each WinRT namespace.  Keep the shutdown handle alive for the
            # sender lifetime so activation of AppNotificationManager remains
            # valid after construction.  The package/runtime are optional on
            # non-Windows and on unpackaged hosts without a resolvable runtime.
            bootstrap = None
            try:
                bootstrap = importlib.import_module(
                    "winui3.microsoft.windows.applicationmodel.dynamicdependency.bootstrap"
                )
            except Exception:
                bootstrap = None
            if bootstrap is not None:
                shutdown = bootstrap.initialize()
                shutdown.__enter__()
                self._bootstrap_shutdown = shutdown.__exit__
            last_error: Exception | None = None
            for module_name in (
                "winui3.microsoft.windows.appnotifications",
                "winrt.microsoft.windows.appnotifications",
                "winrt.windows.appnotifications",
            ):
                try:
                    self._module = importlib.import_module(module_name)
                    break
                except Exception as error:
                    last_error = error
            if self._module is None:
                raise last_error or RuntimeError("AppNotificationManager projection is unavailable")
            manager_type = getattr(self._module, "AppNotificationManager", None)
            self._notification_type = getattr(self._module, "AppNotification", None)
            if manager_type is None or self._notification_type is None:
                raise RuntimeError("AppNotificationManager projection is unavailable")
            supported = getattr(manager_type, "is_supported", None) or getattr(manager_type, "IsSupported", None)
            if callable(supported) and not supported():
                raise RuntimeError("Windows App SDK notifications are not supported")
            default = getattr(manager_type, "default", None) or getattr(manager_type, "Default", None) or getattr(manager_type, "get_default", None)
            self._manager = default() if callable(default) else default
            if self._manager is None:
                raise RuntimeError("AppNotificationManager default is unavailable")
            register = getattr(self._manager, "register", None) or getattr(self._manager, "Register", None)
            if callable(register):
                register()
        except Exception as error:  # import/API shape is platform-dependent
            if self._bootstrap_shutdown is not None:
                try:
                    self._bootstrap_shutdown(None, None, None)
                except Exception:
                    pass
                self._bootstrap_shutdown = None
            self.unavailable_reason = str(error)[:256] or "windows_app_sdk_unavailable"

    def close(self) -> None:
        """Release the optional Windows App SDK dynamic dependency."""
        shutdown, self._bootstrap_shutdown = self._bootstrap_shutdown, None
        if shutdown is not None:
            shutdown(None, None, None)

    def __del__(self) -> None:  # pragma: no cover - interpreter shutdown path
        try:
            self.close()
        except Exception:
            return

    @staticmethod
    def payload(signal: dict[str, Any]) -> dict[str, Any]:
        application_id = str(signal.get("application_id", "asw.unknown"))[:256]
        summary = str(signal.get("summary", signal.get("kind", "ASW signal")))[:2048]
        return {
            "title": application_id,
            "body": summary,
            "signal_id": str(signal.get("signal_id", ""))[:256],
            "application_id": application_id,
        }

    def _xml(self, payload: dict[str, Any]) -> str:
        title = html.escape(payload["title"], quote=False)
        body = html.escape(payload["body"], quote=False)
        launch = html.escape("asw://signal/" + payload["signal_id"], quote=True)
        return f'<toast launch="{launch}"><visual><binding template="ToastGeneric"><text>{title}</text><text>{body}</text></binding></visual></toast>'

    def __call__(self, signal: dict[str, Any]) -> None:
        payload = self.payload(signal)
        if self._transport is not None:
            self._transport(payload)
            return
        if self._manager is None or self._notification_type is None:
            raise RuntimeError("windows_app_sdk_unavailable" + (": " + self.unavailable_reason if self.unavailable_reason else ""))
        try:
            notification = self._notification_type(self._xml(payload))
            show = getattr(self._manager, "show", None) or getattr(self._manager, "Show", None)
            if not callable(show):
                raise RuntimeError("AppNotificationManager.show is unavailable")
            show(notification)
        except Exception as error:
            raise RuntimeError("windows_app_sdk_send_failed: " + str(error)[:256]) from error


class WindowsAppSdkDelivery:
    """Authorize the user subscription before invoking the platform sender."""

    def __init__(self, service, sender: Callable[[dict], None] | None = None) -> None:
        self.service = service
        self.sender = sender if sender is not None else WindowsAppSdkSender()

    def _authorized_subscription(self, signal: dict, subscription: dict) -> tuple[dict, dict] | None:
        canonical = next((item for item in self.service.signals if item["signal_id"] == signal.get("signal_id")), None)
        if canonical is None:
            return None
        authoritative = self.service.subscriptions.get(subscription.get("subscription_id"))
        if not authoritative:
            return None
        if authoritative["subscriber_kind"] != "user" or not authoritative["enabled"]:
            return None
        if "windows_app_sdk" not in authoritative["destinations"]:
            return None
        if not self.service._matches(canonical, authoritative):
            return None
        return canonical, authoritative

    def deliver(self, signal: dict, subscription: dict) -> bool:
        authorized = self._authorized_subscription(signal, subscription)
        if authorized is None:
            return False
        canonical, authoritative = authorized
        try:
            self.sender(canonical)
        except Exception as error:  # platform boundary: failure is recorded, never signal mutation
            self.service.deliver(signal, authoritative, False, str(error)[:512])
            return False
        self.service.deliver(signal, authoritative, True)
        return True
