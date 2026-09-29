#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r253 bm-c rebase-conflict triage: dump per-file side sizes + JSON top-level face."""
import json, subprocess, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

FILES = [
    "CODELY.md",
    "docs/daily_report/REPORT-2026-09-30.json",
    "docs/daily_report/REPORT-2026-09-30.md",
    "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "research/memory-archive/202609.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)],
                       capture_output=True)
    return r.stdout

def face(b):
    if not b:
        return "EMPTY"
    try:
        j = json.loads(b.decode("utf-8"))
    except Exception as e:
        return "non-json(%s)" % type(e).__name__
    if isinstance(j, dict):
        return "dict keys=" + ",".join(sorted(j.keys())[:12])
    if isinstance(j, list):
        return "list len=%d" % len(j)
    return type(j).__name__

for p in FILES:
    o = blob(2, p); t = blob(3, p)
    same = "SAME" if o == t else "DIFF"
    print("== %s [%s] ours(origin)=%dB theirs(r252)=%dB" % (p, same, len(o), len(t)))
    print("   ours  : %s" % face(o))
    print("   theirs: %s" % face(t))
