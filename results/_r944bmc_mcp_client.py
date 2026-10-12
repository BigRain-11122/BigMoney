# -*- coding: utf-8 -*-
"""r944 bm-c: minimal MCP HTTP client for TJGenerators (tools/list probe).
Purpose: give the loop session the file_upload/CDN channel for O-20261012-2305
clip uploads (video files forbidden in git -> CDN + URL rows)."""
import json, urllib.request, sys, uuid

URL = "https://ai-generator.tuanjie.cn/mcp"

def rpc(body, session=None, timeout=60):
    headers = {"Content-Type": "application/json",
               "Accept": "application/json, text/event-stream",
               "mcp-protocol-version": "2025-06-18"}
    if session:
        headers["Mcp-Session-Id"] = session
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        sid = r.headers.get("Mcp-Session-Id")
        raw = r.read().decode("utf-8", "replace")
        # streamable http may return one JSON per line or an SSE stream
        for line in raw.splitlines():
            if line.startswith("data:"):
                raw = line[5:].strip(); break
        try:
            return sid, json.loads(raw)
        except Exception:
            return sid, raw[:400]

if __name__ == "__main__":
    sid, init = rpc({"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": "initialize",
                     "params": {"protocolVersion": "2025-06-18",
                                "capabilities": {},
                                "clientInfo": {"name": "bmc-loop", "version": "1.0"}}})
    print("SESSION:", sid)
    print("INIT:", json.dumps(init)[:300])
    if sid:
        rpc({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid)
        s2, tools = rpc({"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": "tools/list"}, sid)
        names = []
        t = tools.get("result", {}).get("tools", []) if isinstance(tools, dict) else []
        for x in t:
            names.append(x.get("name"))
        print("TOOLS:", names)
