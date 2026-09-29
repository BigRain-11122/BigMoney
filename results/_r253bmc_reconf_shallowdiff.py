#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r253 bm-c: shallow-diff ours(origin) vs theirs(r252) for conflicted JSON faces."""
import json, subprocess, sys, io, difflib

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

JSONS = [
    "docs/daily_report/REPORT-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.json",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/dashboard_status.json",
]

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    return r.stdout

def shallow_diff(o, t, prefix=""):
    out = []
    if isinstance(o, dict) and isinstance(t, dict):
        for k in sorted(set(o) | set(t)):
            if k not in o: out.append(prefix + k + " ONLY-IN-THEIRS")
            elif k not in t: out.append(prefix + k + " ONLY-IN-OURS")
            elif o[k] != t[k]:
                if isinstance(o[k], (dict, list)) and isinstance(t[k], (dict, list)):
                    if isinstance(o[k], list) and isinstance(t[k], list):
                        out.append(prefix + k + " list ours=%d theirs=%d" % (len(o[k]), len(t[k])))
                    else:
                        out.extend(shallow_diff(o[k], t[k], prefix + k + "."))
                else:
                    so, st = json.dumps(o[k], ensure_ascii=False), json.dumps(t[k], ensure_ascii=False)
                    if len(so) > 90: so = so[:90] + "..."
                    if len(st) > 90: st = st[:90] + "..."
                    out.append(prefix + k + "  ours=%s  theirs=%s" % (so, st))
    return out

for p in JSONS:
    try:
        o = json.loads(blob(2, p).decode("utf-8"))
        t = json.loads(blob(3, p).decode("utf-8"))
    except Exception as e:
        print("== %s PARSE-FAIL %s" % (p, e)); continue
    print("== %s" % p)
    d = shallow_diff(o, t)
    if not d:
        print("   parsed-equal")
    for line in d[:25]:
        print("   " + line)
    if len(d) > 25:
        print("   ... %d more diff paths" % (len(d) - 25))
