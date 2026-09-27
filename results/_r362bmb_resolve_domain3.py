# -*- coding: utf-8 -*-
"""r362 bm-b domain-out trio resolver (r133 hand deep-scan recipe; r136 law:
daily_report x2 + fundamental_b_layer_filter are OUTSIDE the merge_lane_views
resolve registry -- fail-closed domain, hand scan is the ONLY canon path).

Stage semantics (rebase, r362 first-storm calibration): :2 = HEAD = origin
side (bm-c r139 d7d73d8a); :3 = my replayed r362 side.

Probes (repr'd, subprocess bytes, no PS redirection -- r209 law):
  fundamental_b_layer_filter.json  updated:  :2 05:54:13 > :3 05:53:24
  REPORT-2026-09-28.json        generated_at:  :2 05:54:43 > :3 05:54:00
  -> take :2 (newer) wholesale for all three; the report md+json are twin
     files and MUST come from the SAME side (pair-consistency law).
"""
import json
import subprocess

FILES = [
    "results/fundamental_b_layer_filter.json",
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/daily_report/REPORT-2026-09-28.md",
]


def blob(rev):
    r = subprocess.run(["git", "show", rev], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"git show {rev} rc={r.returncode}")
    return r.stdout


for path in FILES:
    b2 = blob(f":2:{path}")
    b3 = blob(f":3:{path}")
    if path.endswith(".json"):
        d2, d3 = json.loads(b2), json.loads(b3)
        probe = "updated" if "fundamental" in path else "generated_at"
        print(f"{path}: :2 {probe}={d2.get(probe)} vs :3 {probe}={d3.get(probe)}"
              f" -> take :2 (newer wholesale, R216 snapshot semantics)")
    with open(path, "wb") as fh:
        fh.write(b2)
    subprocess.run(["git", "add", path], check=True)
    print(f"  written + staged: {path} ({len(b2)}B)")

print("RESOLVED: domain-out trio take-:2 wholesale (pair-consistent), staged")
