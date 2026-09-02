"""HTTP entry point for the issue triage Copilot plugin."""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from .triage import triage_issue

MAX_BODY_BYTES = 1_000_000

OPENAPI_YAML = """openapi: 3.0.3
info:
  title: Issue Triager Plugin
  version: 1.0.0
  description: Suggest labels, priority, and type for GitHub issues.
paths:
  /triage:
    post:
      operationId: triageIssue
      summary: Triage a GitHub issue
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - title
              properties:
                title:
                  type: string
                body:
                  type: string
      responses:
        '200':
          description: Triage suggestions
          content:
            application/json:
              schema:
                type: object
                properties:
                  labels:
                    type: array
                    items:
                      type: string
                  priority:
                    type: string
                    enum: [low, medium, high]
                  type:
                    type: string
                  summary:
                    type: string
                  rationale:
                    type: array
                    items:
                      type: string
"""


class TriagerHandler(BaseHTTPRequestHandler):
    """Serve plugin metadata and issue triage requests."""

    server_version = "TriagerPlugin/1.0"

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            self._send_json({"status": "ok"})
        elif path == "/.well-known/ai-plugin.json":
            self._send_json(self._plugin_manifest())
        elif path == "/openapi.yaml":
            self._send_text(OPENAPI_YAML, "application/yaml")
        else:
            self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/triage":
            self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            return

        try:
            payload = self._read_json_body()
        except ValueError as error:
            self._send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return

        title = payload.get("title")
        body = payload.get("body", "")
        if not isinstance(title, str) or not title.strip():
            self._send_json({"error": "title must be a non-empty string"}, HTTPStatus.BAD_REQUEST)
            return
        if not isinstance(body, str):
            self._send_json({"error": "body must be a string"}, HTTPStatus.BAD_REQUEST)
            return

        self._send_json(triage_issue(title, body))

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _read_json_body(self) -> dict[str, Any]:
        content_length = self.headers.get("Content-Length")
        if content_length is None:
            raise ValueError("missing Content-Length header")

        try:
            length = int(content_length)
        except ValueError as exc:
            raise ValueError("invalid Content-Length header") from exc

        if length > MAX_BODY_BYTES:
            raise ValueError("request body is too large")

        raw_body = self.rfile.read(length)
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("request body must be valid JSON") from exc

        if not isinstance(payload, dict):
            raise ValueError("request body must be a JSON object")
        return payload

    def _plugin_manifest(self) -> dict[str, object]:
        scheme = "https" if self.headers.get("X-Forwarded-Proto") == "https" else "http"
        host = self.headers.get("Host", "localhost")
        base_url = f"{scheme}://{host}"
        return {
            "schema_version": "v1",
            "name_for_human": "Issue Triager",
            "name_for_model": "issue_triager",
            "description_for_human": "Suggests labels, priority, and type for GitHub issues.",
            "description_for_model": "Use this plugin to triage GitHub issues from their title and body.",
            "auth": {"type": "none"},
            "api": {"type": "openapi", "url": f"{base_url}/openapi.yaml"},
            "logo_url": f"{base_url}/logo.png",
            "contact_email": "support@example.com",
            "legal_info_url": f"{base_url}/legal",
        }

    def _send_json(self, payload: dict[str, object], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, body: str, content_type: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run the plugin server until interrupted."""

    server = ThreadingHTTPServer((host, port), TriagerHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the issue triager Copilot plugin")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()
    run(args.host, args.port)


if __name__ == "__main__":
    main()
