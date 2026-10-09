# -*- coding: utf-8 -*-
"""Probe the 3 unresolved faces: compute_audit.json + 3 md files' ts."""
import json
import re
import subprocess


def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


for f in ("results/compute_audit.json",):
    for st in (2, 3):
        b = blob(st, f)
        o = json.loads(b)
        print(f, "stage", st, "top keys:", sorted(o.keys())[:10])
        for k in ("ts", "generated", "asof", "audit"):
            if k in o:
                print("  ", k, "=", str(o[k])[:60])

for f in ("docs/daily_report/REPORT-2026-10-06.md",
          "docs/live_usage/LIVE-2026-10-06.md",
          "docs/live_usage/LIVE-latest.md"):
    for st in (2, 3):
        b = blob(st, f)
        m = re.search(rb"20[0-9]{2}-[0-9]{2}-[0-9]{2}[ T][0-9:]{8}", b[:6000])
        print(f, "stage", st, "first-ts:", m.group(0).decode() if m else None)
