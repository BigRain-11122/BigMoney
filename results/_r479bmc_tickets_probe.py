# -*- coding: utf-8 -*-
"""r479 bm-c ticket health probe: T-157..164 (CEO O-1440 audit face) + 165..169.
Read-only. ASCII stdout."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
OUT = []
for n in (155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169):
    p = r"fleet\tasks\T-2026-10-03-%d-P1.json" % n
    if n >= 165:
        p = r"fleet\tasks\T-2026-10-04-%d-P1.json" % n
    if n == 156:
        p = r"fleet\tasks\T-2026-10-03-156-P0.json"
    if not os.path.exists(p):
        OUT.append({"n": n, "missing": True})
        continue
    with open(p, encoding="utf-8") as f:
        t = json.load(f)
    OUT.append({
        "n": n,
        "status": t.get("status"),
        "title": str(t.get("title", t.get("spec", "")))[:80],
        "claimed_by": t.get("claimed_by"),
        "claimed_at": t.get("claimed_at"),
        "immediate": t.get("immediate"),
        "progress_head": str(t.get("progress", ""))[:200],
    })
print(json.dumps(OUT, indent=1, ensure_ascii=True))
