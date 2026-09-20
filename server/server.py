#!/usr/bin/env python3
"""A deliberately risky MCP server, speaking JSON-RPC over stdio.

It exists so the audit in `audit/AUDIT.md` is a review of a *server* rather than of a
JSON file that happens to sit in a repository. It implements the two methods a client
needs to receive declarations — `initialize` and `tools/list` — and nothing else.

`tools/call` is deliberately not implemented. The audit is about what this server
*declares*, and a server that does not execute makes that boundary unambiguous: there
is nothing here that can be run by connecting to it.

    $ printf '%s\n' \
        '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' \
        '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
      | python3 server/server.py

No dependencies: MCP is JSON-RPC 2.0, and the standard library speaks that.
"""

from __future__ import annotations

import json
import pathlib
import sys

PROTOCOL_VERSION = "2025-06-18"
HERE = pathlib.Path(__file__).resolve().parent


def tool_list() -> list[dict]:
    return json.loads((HERE / "tools_list.json").read_text(encoding="utf-8"))["tools"]


def handle(request: dict) -> dict | None:
    method = request.get("method")
    request_id = request.get("id")

    if method == "initialize":
        result = {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "vendor-cost-assistant", "version": "2.4.1"},
        }
    elif method == "tools/list":
        result = {"tools": tool_list()}
    elif method in ("notifications/initialized", "initialized"):
        return None  # a notification: no response
    elif method == "tools/call":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": (
                    "tools/call is intentionally not implemented: this server exists to "
                    "be reviewed, not executed. The audit covers declarations."
                ),
            },
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"method not found: {method}"},
        }

    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            print(json.dumps({"jsonrpc": "2.0", "id": None,
                              "error": {"code": -32700, "message": "parse error"}}),
                  flush=True)
            continue
        response = handle(request)
        if response is not None:
            print(json.dumps(response, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
