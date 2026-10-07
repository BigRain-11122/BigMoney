# -*- coding: utf-8 -*-
import io
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for p in ["docs/live_usage/LIVE-2026-10-08.md", "docs/live_usage/LIVE-2026-10-08.json",
          "docs/live_usage/LIVE-latest.md", "docs/live_usage/LIVE-latest.json"]:
    r = subprocess.run(["git", "show", ":3:" + p], capture_output=True)
    assert r.returncode == 0, (p, r.returncode)
    assert b"<<<<<<<" not in r.stdout and b">>>>>>>" not in r.stdout, p
    if p.endswith(".json"):
        json.loads(r.stdout.decode("utf-8"))
    io.open(p, "wb").write(r.stdout)
    print("LIVE face -> stage3 (mine, auto-gen 07:09:41, newer-wins r440):", p)
# verify the md carries my ts
md = io.open("docs/live_usage/LIVE-2026-10-08.md", encoding="utf-8").read()
assert "2026-10-08T07:09:41" in md, "LIVE md ts drift"
print("LIVE md ts verified: 2026-10-08T07:09:41")
