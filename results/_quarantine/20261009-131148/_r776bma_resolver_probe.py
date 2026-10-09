# -*- coding: utf-8 -*-
"""r776 push-race resolver: 14 shared daily-regen UU faces.
Rebase semantics: :2: = upstream (bm-c r621), :3: = ours (bm-a r776 replay).
Per-face disposition: normalized-ts take-newer for snapshot faces
(r756 normalization law: space->T + parse, never raw string compare);
token_usage.json inspected separately (possible per-machine union face).
"""
import datetime
import json
import subprocess
import sys


def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def norm_ts(s):
    if not s:
        return None
    s = str(s).strip().replace(" ", "T")
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S",
               "%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            return datetime.datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def probe_ts(obj, depth=0):
    """Find timestamp-ish field in a JSON doc (shallow)."""
    if depth > 2 or not isinstance(obj, dict):
        return None
    for key in ("ts", "generated", "generated_at", "asof", "updated",
                "last_run", "time"):
        if key in obj:
            v = norm_ts(obj[key])
            if v is not None:
                return v
    for k in ("generated", "ts", "meta", "audit"):
        if k in obj and isinstance(obj[k], dict):
            v = probe_ts(obj[k], depth + 1)
            if v is not None:
                return v
    return None


FILES = [
    "docs/daily_report/REPORT-2026-10-06.json",
    "docs/daily_report/REPORT-2026-10-06.md",
    "docs/live_usage/LIVE-2026-10-06.json",
    "docs/live_usage/LIVE-2026-10-06.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]

# md files: first 'generated/ts' line probe
import re

for f in FILES:
    b2, b3 = blob(2, f), blob(3, f)
    if b2 is None or b3 is None:
        print(f, "STAGE-MISSING", len(b2 or b""), len(b3 or b""))
        continue
    t2 = t3 = None
    if f.endswith(".json"):
        try:
            o2, o3 = json.loads(b2), json.loads(b3)
            t2, t3 = probe_ts(o2), probe_ts(o3)
        except Exception as e:
            print(f, "JSON-PARSE-ERR", e)
            continue
        if f == "results/token_usage.json":
            print(f, "top keys ours:", sorted(o3.keys())[:12])
            print(f, "top keys theirs:", sorted(o2.keys())[:12])
    else:
        m2 = re.search(rb"(?:generated|ts|asof)[:=][ '\"]*([0-9T:\-\.+]+)",
                       b2[:3000])
        m3 = re.search(rb"(?:generated|ts|asof)[:=][ '\"]*([0-9T:\-\.+]+)",
                       b3[:3000])
        t2 = norm_ts(m2.group(1).decode()) if m2 else None
        t3 = norm_ts(m3.group(1).decode()) if m3 else None
    winner = "?"
    if t2 and t3:
        winner = "theirs(bm-c)" if t2 > t3 else "ours(bm-a)"
    elif t3:
        winner = "ours(bm-a)"
    elif t2:
        winner = "theirs(bm-c)"
    print(f"{f} | stage2(bm-c)={t2} | stage3(bm-a)={t3} -> {winner}")
