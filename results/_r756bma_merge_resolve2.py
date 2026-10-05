# -*- coding: utf-8 -*-
"""r756 bm-a merge-conflict resolver ROUND 2 (bm-c r594 same-window batch).

Differences from round 1 (_r756bma_merge_resolve.py):
- normalized ts comparison (mixed 'T'+offset vs ' ' separator poison healed
  in-session round 1; round 2 uses the healed comparator from the start)
- dashboard_status.json/.js = host=bm-a single-writer faces (r378 law) ->
  take LOCAL side whole-byte; the origin-side write by bm-c r594 is disclosed
  in the round report as a lane-violation suspicion (host guard should have
  stdout-skipped on bm-c)
- snapshots: deep-ts probe (normalized), fresher side wins
- twins: json face probes the side (normalized), md/jsonl pointers byte-copy
  from the SAME side
"""
import json
import re
import subprocess
from datetime import datetime

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def norm_ts(s):
    s = s.replace(" ", "T")
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y%m%d%H%M%S")
        except ValueError:
            continue
    return None


def staged_bytes(path, stage):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def deep_ts(obj):
    best = None

    def walk(x):
        nonlocal best
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str) and TS_RE.match(x):
            n = norm_ts(x)
            if n and (best is None or n > best):
                best = n

    walk(obj)
    return best


def take_new_snapshot(path):
    a = staged_bytes(path, 2)
    b = staged_bytes(path, 3)
    if a is None and b is None:
        print(f"{path}: NO STAGED SIDES, skip")
        return False
    if a is None:
        open(path, "wb").write(b)
        print(f"{path}: origin missing -> local taken")
        return True
    if b is None:
        open(path, "wb").write(a)
        print(f"{path}: local missing -> origin taken")
        return True
    ta = deep_ts(json.loads(a.decode("utf-8")))
    tb = deep_ts(json.loads(b.decode("utf-8")))
    if ta is None and tb is None:
        print(f"{path}: NO ts either side -> FAIL-CLOSED manual")
        return False
    win, side, ts = (b, "local", tb) if (tb is not None and (ta is None or tb >= ta)) else (a, "origin", ta)
    open(path, "wb").write(win)
    json.loads(open(path, "rb").read().decode("utf-8"))
    print(f"{path}: take-new -> {side} (ts={ts})")
    return True


def take_local(path):
    b = staged_bytes(path, 3)
    if b is None:
        print(f"{path}: local staged side missing, SKIP")
        return False
    open(path, "wb").write(b)
    if path.endswith(".json"):
        json.loads(open(path, "rb").read().decode("utf-8"))
    print(f"{path}: take LOCAL (host=bm-a single-writer r378)")


def twin_resolve(json_path, md_paths):
    a = staged_bytes(json_path, 2)
    b = staged_bytes(json_path, 3)
    ta = deep_ts(json.loads(a.decode("utf-8")))
    tb = deep_ts(json.loads(b.decode("utf-8")))
    stage, side = (3, "local") if (tb is not None and (ta is None or tb >= ta)) else (2, "origin")
    open(json_path, "wb").write(staged_bytes(json_path, stage))
    json.loads(open(json_path, "rb").read().decode("utf-8"))
    print(f"{json_path}: twin side -> {side} (origin_ts={ta} local_ts={tb})")
    for md in md_paths:
        mb = staged_bytes(md, stage)
        if mb is None:
            print(f"{md}: staged side missing, SKIP (manual)")
            return False
        open(md, "wb").write(mb)
        print(f"{md}: byte-copied from {side} side")


ok = True
for f in [
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
]:
    ok = take_new_snapshot(f) and ok

for f in ["results/dashboard_status.json", "results/dashboard_status.js"]:
    take_local(f)

twin_resolve(
    "docs/daily_report/REPORT-2026-10-06.json",
    ["docs/daily_report/REPORT-2026-10-06.md"],
)
twin_resolve(
    "docs/live_usage/LIVE-2026-10-06.json",
    ["docs/live_usage/LIVE-2026-10-06.md",
     "docs/live_usage/LIVE-latest.json",
     "docs/live_usage/LIVE-latest.md"],
)
print("round2 resolver done")
