"""Transport-neutral local structured agent protocol facade."""

from __future__ import annotations

import json
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Any

from .contracts import ContractError, validate


class AgentAPI:
    """Expose the RFC's logical agent operations over a bounded local API.

    The service remains the authority.  This facade only shapes responses and
    validates the normative stream request envelope before dispatch.
    """

    def __init__(self, service, agent_id: str) -> None:
        self.service, self.agent_id = service, agent_id

    def get_capabilities(self) -> dict[str, Any]:
        return {
            "schema_version": "asw.agent_response.v1",
            "operations": [
                "list_applications",
                "get_access_grant",
                "list_subscriptions",
                "create_subscription",
                "update_subscription",
                "delete_subscription",
                "list_signals",
                "get_signal",
                "open_signal_stream",
                "resume_signal_stream",
            ],
        }

    @staticmethod
    def _bounded_limit(limit: int) -> int:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        return limit

    def _validate_after(self, after: dict[str, Any] | None) -> int:
        if after is None:
            return -1
        validate("replay-cursor", after)
        if after["subscriber_id"] not in {None, self.agent_id}:
            raise PermissionError("cursor belongs to another subscriber")
        return after["frontier"]["journal_sequence"]

    def _snapshot_response(self, key: str, record_kind: str, values: list[dict[str, Any]], limit: int, after: dict[str, Any] | None) -> dict[str, Any]:
        self._bounded_limit(limit)
        # A snapshot cursor is a durable position, not an authorization token.
        # The next call re-evaluates the grant and authorization intersection.
        after_sequence = self._validate_after(after)
        sequences = self.service.projection_sequences[record_kind]
        visible = sorted(
            (item for item in values if sequences.get(item["application_id"] if record_kind == "application" else item["subscription_id"], -1) > after_sequence),
            key=lambda item: (sequences.get(item["application_id"] if record_kind == "application" else item["subscription_id"], -1), item.get("application_id", item.get("subscription_id", ""))),
        )[:limit]
        cursor_sequence = sequences.get(
            visible[-1]["application_id"] if record_kind == "application" else visible[-1]["subscription_id"],
            after_sequence,
        ) if visible else (self.service.journal.sequence if after is None else max(after_sequence, 0))
        return {
            "schema_version": "asw.agent_response.v1",
            key: visible,
            "replay_cursor": self.service.cursor(self.agent_id, cursor_sequence),
        }

    def list_applications(self, limit: int = 100, after: dict[str, Any] | None = None) -> dict[str, Any]:
        grant = self.service.get_agent_grant(self.agent_id)
        if grant is None:
            raise PermissionError("active agent access grant required")
        applications = sorted(
            (
                app
                for app in self.service.applications.values()
                if app["application_id"] in grant["applications"]
                and self.service.application_authorized(app["application_id"])
            ),
            key=lambda app: app["application_id"],
        )
        return self._snapshot_response("applications", "application", applications, limit, after)

    def get_access_grant(self) -> dict[str, Any] | None:
        return self.service.get_agent_grant(self.agent_id)

    def list_subscriptions(self, limit: int = 100, after: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.service.get_agent_grant(self.agent_id) is None:
            raise PermissionError("active agent access grant required")
        subscriptions: list[dict[str, Any]] = []
        for subscription in sorted(self.service.subscriptions.values(), key=lambda item: item["subscription_id"]):
            if subscription["subscriber_id"] != self.agent_id or not subscription["enabled"]:
                continue
            try:
                self.service._enforce_agent_scope(self.agent_id, subscription)
            except PermissionError:
                # A grant can be narrowed after a subscription was created.  Do
                # not leak that now-out-of-scope subscription in a snapshot.
                continue
            subscriptions.append(subscription)
        return self._snapshot_response("subscriptions", "subscription", subscriptions, limit, after)

    def _owned_subscription(self, subscription: dict[str, Any]) -> dict[str, Any]:
        if subscription.get("subscriber_id") != self.agent_id or subscription.get("subscriber_kind") != "agent":
            raise PermissionError("agent may mutate only its own subscription")
        return subscription

    def create_subscription(self, subscription: dict[str, Any]) -> dict[str, Any]:
        self.service.register_subscription(self._owned_subscription(subscription))
        return subscription

    def update_subscription(self, subscription: dict[str, Any]) -> dict[str, Any]:
        current = self.service.subscriptions.get(subscription.get("subscription_id"))
        if not current or current["subscriber_id"] != self.agent_id:
            raise PermissionError("agent may mutate only its own subscription")
        self.service.register_subscription(self._owned_subscription(subscription))
        return subscription

    def delete_subscription(self, subscription_id: str) -> None:
        subscription = self.service.subscriptions.get(subscription_id)
        if not subscription or subscription["subscriber_id"] != self.agent_id:
            raise PermissionError("agent may delete only its own subscription")
        disabled = dict(subscription)
        disabled["enabled"] = False
        self.service.register_subscription(disabled)

    def list_signals(self, subscription_id: str, limit: int = 100, after: dict[str, Any] | int | None = None) -> dict[str, Any]:
        return self.service.agent_signals(self.agent_id, subscription_id, limit, after)

    def get_signal(self, subscription_id: str, signal_id: str) -> dict[str, Any] | None:
        subscription = self.service.subscriptions.get(subscription_id)
        if not subscription or subscription["subscriber_id"] != self.agent_id or subscription["subscriber_kind"] != "agent":
            raise PermissionError("agent may access only its own subscription")
        if not subscription["enabled"]:
            raise PermissionError("subscription is disabled")
        self.service._enforce_agent_scope(self.agent_id, subscription)
        for signal in self.service.signals:
            if (
                signal["signal_id"] == signal_id
                and self.service._matches(signal, subscription)
                and self.service.application_authorized(signal["application_id"])
            ):
                return signal
        return None

    def open_signal_stream(self, subscription_id: str, limit: int = 100) -> dict[str, Any]:
        return self.list_signals(subscription_id, limit)

    def resume_signal_stream(self, subscription_id: str, after: dict[str, Any] | int, limit: int = 100) -> dict[str, Any]:
        return self.list_signals(subscription_id, limit, after)

    def _stream_request(self, request: dict[str, Any]) -> dict[str, Any]:
        validate("agent-stream-request", request)
        if request["agent_subscriber_id"] != self.agent_id:
            raise PermissionError("stream request belongs to another agent")
        limit = request["limit"]
        after = request["after"]
        combined: dict[str, dict[str, Any]] = {}
        for subscription_id in request["subscription_ids"]:
            response = self.list_signals(subscription_id, limit, after)
            for signal in response["signals"]:
                combined[signal["signal_id"]] = signal
        signals = sorted(
            combined.values(),
            key=lambda signal: self.service.signal_sequences.get(signal["signal_id"], -1),
        )[:limit]
        if signals:
            cursor_sequence = self.service.signal_sequences[signals[-1]["signal_id"]]
        elif after is None:
            cursor_sequence = 0
        else:
            cursor_sequence = after["frontier"]["journal_sequence"]
        return {
            "schema_version": "asw.agent_response.v1",
            "signals": signals,
            "replay_cursor": self.service.cursor(self.agent_id, cursor_sequence),
        }

    def handle(self, operation: str, payload: dict[str, Any] | None = None) -> Any:
        """Dispatch the transport-neutral logical operations from RFC 0001."""
        payload = payload or {}
        if operation in {"open_signal_stream", "resume_signal_stream"}:
            return self._stream_request(payload)
        if operation == "get_capabilities":
            return self.get_capabilities()
        if operation == "list_applications":
            return self.list_applications(payload.get("limit", 100), payload.get("after"))
        if operation == "get_access_grant":
            return self.get_access_grant()
        if operation == "list_subscriptions":
            return self.list_subscriptions(payload.get("limit", 100), payload.get("after"))
        if operation == "create_subscription":
            return self.create_subscription(payload["subscription"])
        if operation == "update_subscription":
            return self.update_subscription(payload["subscription"])
        if operation == "delete_subscription":
            return self.delete_subscription(payload["subscription_id"])
        if operation == "list_signals":
            return self.list_signals(payload["subscription_id"], payload.get("limit", 100), payload.get("after"))
        if operation == "get_signal":
            return self.get_signal(payload["subscription_id"], payload["signal_id"])
        raise ValueError("unsupported agent operation")


class LocalAgentServer:
    """Loopback JSON transport for the structured agent facade.

    The bearer token is issued by the user-facing grant flow and maps to one
    agent subscriber.  Every request is dispatched through a fresh
    :class:`AgentAPI`, so grant, subscription, and authorization checks remain
    at the service boundary rather than in the transport.
    """

    def __init__(self, service, host: str = "127.0.0.1", port: int = 0) -> None:
        if host not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("agent server must bind to loopback")
        self.service, self.host, self.port = service, host, port
        self._tokens: dict[str, str] = {}
        self._server: ThreadingHTTPServer | None = None
        self._thread: Thread | None = None

    @property
    def endpoint(self) -> str | None:
        if self._server is None:
            return None
        address, port = self._server.server_address[:2]
        host = "127.0.0.1" if address in {"0.0.0.0", "::", "localhost"} else address
        return f"http://{host}:{port}"

    def issue_token(self, agent_id: str) -> str:
        subscriber = self.service.subscribers.get(agent_id)
        if not subscriber or subscriber.get("kind") != "agent":
            raise PermissionError("agent subscriber registration required")
        self.revoke_agent(agent_id)
        token = secrets.token_urlsafe(32)
        self._tokens[token] = agent_id
        return token

    def revoke_agent(self, agent_id: str) -> None:
        self._tokens = {token: owner for token, owner in self._tokens.items() if owner != agent_id}

    def dispatch(self, token: str, operation: str, payload: dict[str, Any] | None = None) -> Any:
        agent_id = self._tokens.get(token)
        if not agent_id:
            raise PermissionError("invalid local agent credential")
        return AgentAPI(self.service, agent_id).handle(operation, payload or {})

    def start(self) -> str:
        if self._server is not None:
            return self.endpoint or ""
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802 - stdlib handler contract
                if self.path != "/v1/agent":
                    self._write(404, {"error": "not_found"})
                    return
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    if length < 0 or length > 1024 * 1024:
                        raise ValueError("request body too large")
                    request = json.loads(self.rfile.read(length).decode("utf-8"))
                    if not isinstance(request, dict) or not isinstance(request.get("token"), str) or not isinstance(request.get("operation"), str):
                        raise ValueError("token and operation are required")
                    payload = request.get("payload", {})
                    if not isinstance(payload, dict):
                        raise ValueError("payload must be an object")
                    result = owner.dispatch(request["token"], request["operation"], payload)
                    self._write(200, {"ok": True, "result": result})
                except PermissionError as error:
                    self._write(403, {"ok": False, "error": str(error)[:256]})
                except (ContractError, ValueError, KeyError, json.JSONDecodeError) as error:
                    self._write(400, {"ok": False, "error": str(error)[:256]})
                except Exception:
                    self._write(500, {"ok": False, "error": "agent_request_failed"})

            def _write(self, status: int, body: dict[str, Any]) -> None:
                encoded = json.dumps(body, separators=(",", ":")).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

            def log_message(self, *_args: Any) -> None:
                return

        self._server = ThreadingHTTPServer((self.host, self.port), Handler)
        self._server.daemon_threads = True
        self._thread = Thread(target=self._server.serve_forever, name="asw-agent-server", daemon=True)
        self._thread.start()
        return self.endpoint or ""

    def stop(self) -> None:
        if self._server is None:
            return
        self._server.shutdown()
        self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=2)
        self._server = None
        self._thread = None
