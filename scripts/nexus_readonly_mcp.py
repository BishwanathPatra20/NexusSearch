#!/usr/bin/env python3
"""
Read-only MCP-style bridge for Cursor / Claude Code (original NexusSearch code).

Calls local FastAPI /agent-tools/* — no third-party repo code vendored.
Configure in Cursor MCP: command = python, args = [this script path]
Env: KNOWLEDGEPILOT_API_URL (default http://127.0.0.1:8000/api/v1)
Optional: KNOWLEDGEPILOT_API_KEY → sent as Bearer on each request.
"""

from __future__ import annotations

import json
import os
import sys
from urllib.parse import quote

import httpx

API_BASE = os.environ.get("KNOWLEDGEPILOT_API_URL", "http://127.0.0.1:8000/api/v1").rstrip("/")
API_KEY = os.environ.get("KNOWLEDGEPILOT_API_KEY", "").strip()

TOOLS = [
    {
        "name": "search_knowledge",
        "description": "Search local corpus + live Confluence (PAT). Read-only.",
        "inputSchema": {
            "type": "object",
            "properties": {"q": {"type": "string"}},
            "required": ["q"],
        },
    },
    {
        "name": "list_documents",
        "description": "List recently indexed documents (read-only).",
        "inputSchema": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 25}},
        },
    },
    {
        "name": "get_lineage",
        "description": "Full governance lineage for a review_item_id (read-only).",
        "inputSchema": {
            "type": "object",
            "properties": {"review_item_id": {"type": "integer"}},
            "required": ["review_item_id"],
        },
    },
]


def _headers() -> Dict[str, str]:
    h = {"Accept": "application/json"}
    if API_KEY:
        h["Authorization"] = f"Bearer {API_KEY}"
    return h


def _call_tool(name: str, arguments: Dict[str, Any]) -> str:
    with httpx.Client(timeout=120.0, headers=_headers()) as client:
        if name == "search_knowledge":
            q = str(arguments.get("q", "")).strip()
            r = client.get(f"{API_BASE}/agent-tools/search", params={"q": q, "limit": 10})
            r.raise_for_status()
            return json.dumps(r.json(), indent=2, default=str)
        if name == "list_documents":
            limit = int(arguments.get("limit") or 25)
            r = client.get(f"{API_BASE}/agent-tools/documents", params={"limit": limit})
            r.raise_for_status()
            return json.dumps(r.json(), indent=2, default=str)
        if name == "get_lineage":
            rid = int(arguments["review_item_id"])
            r = client.get(f"{API_BASE}/agent-tools/lineage/{rid}")
            r.raise_for_status()
            return json.dumps(r.json(), indent=2, default=str)
    raise ValueError(f"Unknown tool: {name}")


def _respond(msg_id: Any, result: Any) -> None:
    print(json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": result}), flush=True)


def _error(msg_id: Any, code: int, message: str) -> None:
    print(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": code, "message": message},
            }
        ),
        flush=True,
    )


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg_id = msg.get("id")
        method = msg.get("method")
        params = msg.get("params") or {}

        if method == "initialize":
            _respond(
                msg_id,
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "nexussearch-readonly", "version": "1.1.0"},
                },
            )
        elif method == "tools/list":
            _respond(msg_id, {"tools": TOOLS})
        elif method == "tools/call":
            try:
                name = params.get("name")
                args = params.get("arguments") or {}
                text = _call_tool(str(name), args)
                _respond(msg_id, {"content": [{"type": "text", "text": text}]})
            except Exception as exc:
                _respond(msg_id, {"content": [{"type": "text", "text": f"Error: {exc}"}], "isError": True})
        elif method == "notifications/initialized":
            pass
        elif msg_id is not None:
            _error(msg_id, -32601, f"Method not found: {method}")


if __name__ == "__main__":
    main()
