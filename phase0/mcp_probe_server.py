#!/usr/bin/env python3
"""Minimal localhost-only MCP probe used by the Phase 0 Doubao audit.

The server intentionally exposes one read-only tool and stores no secrets. It is
not a production connector or state service.
"""

from __future__ import annotations

import argparse
import json
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


SERVER_INFO = {"name": "architectpass-phase0-probe", "version": "0.1.0"}
TOOL = {
    "name": "phase0_ping",
    "description": "Return a fixed localhost capability-audit response.",
    "inputSchema": {
        "type": "object",
        "properties": {"message": {"type": "string"}},
        "additionalProperties": False,
    },
}


class ProbeState:
    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self.lock = threading.Lock()

    def log(self, event: dict[str, Any]) -> None:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **event,
        }
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.lock, self.log_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=False) + "\n")


class ProbeHandler(BaseHTTPRequestHandler):
    server_version = "ArchitectPassPhase0Probe/0.1"

    @property
    def state(self) -> ProbeState:
        return self.server.state  # type: ignore[attr-defined]

    def log_message(self, _format: str, *_args: Any) -> None:
        return

    def _headers(self, status: int, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, Mcp-Session-Id")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._headers(204, "text/plain")

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._headers(200, "application/json; charset=utf-8")
            self.wfile.write(json.dumps({"status": "ok", "server": SERVER_INFO}).encode())
            return
        if self.path == "/mcp":
            self._headers(405, "application/json; charset=utf-8")
            self.wfile.write(json.dumps({"error": "Use MCP Streamable HTTP POST"}).encode())
            return
        self._headers(404, "application/json; charset=utf-8")
        self.wfile.write(json.dumps({"error": "not found"}).encode())

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/mcp":
            self._headers(404, "application/json; charset=utf-8")
            self.wfile.write(json.dumps({"error": "not found"}).encode())
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            request = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError) as exc:
            self._headers(400, "application/json; charset=utf-8")
            self.wfile.write(json.dumps({"error": str(exc)}).encode())
            return

        method = request.get("method")
        request_id = request.get("id")
        self.state.log(
            {
                "method": method,
                "request_id": request_id,
                "user_agent": self.headers.get("User-Agent"),
            }
        )

        if request_id is None:
            self._headers(202, "application/json; charset=utf-8")
            return

        response = {"jsonrpc": "2.0", "id": request_id}
        if method == "initialize":
            requested = request.get("params", {}).get("protocolVersion")
            response["result"] = {
                "protocolVersion": requested or "2025-03-26",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER_INFO,
            }
        elif method == "ping":
            response["result"] = {}
        elif method == "tools/list":
            response["result"] = {"tools": [TOOL]}
        elif method == "tools/call":
            params = request.get("params", {})
            if params.get("name") != TOOL["name"]:
                response["error"] = {"code": -32601, "message": "Unknown tool"}
            else:
                message = params.get("arguments", {}).get("message", "")
                response["result"] = {
                    "content": [
                        {
                            "type": "text",
                            "text": f"LOCALHOST_MCP_OK:{message}" if message else "LOCALHOST_MCP_OK",
                        }
                    ],
                    "isError": False,
                }
        elif method in {"resources/list", "prompts/list"}:
            response["result"] = {"resources" if method == "resources/list" else "prompts": []}
        else:
            response["error"] = {"code": -32601, "message": f"Method not found: {method}"}

        payload = json.dumps(response, ensure_ascii=False)
        if "text/event-stream" in self.headers.get("Accept", ""):
            self._headers(200, "text/event-stream; charset=utf-8")
            self.wfile.write(f"event: message\ndata: {payload}\n\n".encode())
        else:
            self._headers(200, "application/json; charset=utf-8")
            self.wfile.write(payload.encode())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18080)
    parser.add_argument(
        "--log",
        type=Path,
        default=Path("artifacts/doubao-audit-logs/localhost-mcp-probe.jsonl"),
    )
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), ProbeHandler)
    server.state = ProbeState(args.log)  # type: ignore[attr-defined]
    print(f"Listening on http://{args.host}:{args.port}/mcp", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
