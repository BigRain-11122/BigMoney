"""r756 bm-a merge-conflict resolver (canonical recipes, skill bigmoney-conflict-resolve).

Faces handled here (ALL_FACES already resolved via merge_lane_views.py resolve):
- snapshot take-new by hardened deep-ts probe: fundamental_b_layer_filter /
  scorecard_v1 / strategy_scorecard / _attrition_guard_scan (UNKNOWN manual
  adjudication: per-scan regenerated receipt, whole-doc regen face)
- twin-regen-md: docs/daily_report/REPORT-2026-10-06.{json,md} and
  docs/live_usage/LIVE-2026-10-06.{json,md} + LIVE-latest.{json,md}
  (json face probes the side, md face byte-copies the SAME side blob)

Probe laws applied: r100 (normalize key strip '_-' before prefix match; value
must be ts-shaped ^20\\d{2}- before max-compare), R350 (wall-clock values
require time-of-day [T ]HH:MM; no key-EXCLUDE lists; ambiguity by value shape),
probe STAGED blobs (:2: origin side / :3: local side), never the working tree.
"""
import json
import re
import subprocess
import sys
from datetime import datetime

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")

# r756 in-session probe heal: mixed "T"+offset vs " " separator strings break
# lexicographic max (space 0x20 < 'T' 0x54 -> a 04:03 space-format generated
# key loses to a 03:56 T-format data key). Normalize before compare.


def norm_ts(s):
    s = s.replace(" ", "T")
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y%m%d%H%M%S") + s[-6:] if (fmt.endswith("z") and s[-6] in "+-") else datetime.strptime(s, fmt).strftime("%Y%m%d%H%M%S")
        except ValueError:
            continue
    return None


def staged_bytes(path, stage):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def deep_ts(obj):
    """Deep-collect max wall-clock ts from all nested layers (R350: time-of-day mandatory; normalized compare)."""
    best = None

    def walk(x):
        nonlocal best
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str):
            if TS_RE.match(x):
                n = norm_ts(x)
                if n and (best is None or n > best):
                    best = n

    walk(obj)
    return best


def take_new_snapshot(path):
    a = staged_bytes(path, 2)  # origin side
    b = staged_bytes(path, 3)  # local side
    if a is None and b is None:
        print(f"{path}: NO STAGED SIDES, skip")
        return False
    if a is None:
        open(path, "wb").write(b)
        print(f"{path}: origin side missing -> local taken")
        return True
    if b is None:
        open(path, "wb").write(a)
        print(f"{path}: local side missing -> origin taken")
        return True
    ta = deep_ts(json.loads(a.decode("utf-8")))
    tb = deep_ts(json.loads(b.decode("utf-8")))
    if ta is None and tb is None:
        print(f"{path}: NO ts on either side -> FAIL-CLOSED, manual")
        return False
    if tb is None or (ta is not None and ta >= tb):
        win, side, ts = a, "origin", ta
    else:
        win, side, ts = b, "local", tb
    open(path, "wb").write(win)
    json.loads(open(path, "rb").read().decode("utf-8"))  # parse-verify before add (r185)
    print(f"{path}: take-new -> {side} (ts={ts})")
    return True


def twin_resolve(json_path, md_paths):
    a = staged_bytes(json_path, 2)
    b = staged_bytes(json_path, 3)
    ta = deep_ts(json.loads(a.decode("utf-8"))) if a else None
    tb = deep_ts(json.loads(b.decode("utf-8"))) if b else None
    if tb is None or (ta is not None and ta >= tb):
        stage, side, ts = 2, "origin", ta
    else:
        stage, side, ts = 3, "local", tb
    jb = staged_bytes(json_path, stage)
    open(json_path, "wb").write(jb)
    json.loads(open(json_path, "rb").read().decode("utf-8"))
    print(f"{json_path}: twin side -> {side} (ts={ts})")
    for md in md_paths:
        mb = staged_bytes(md, stage)
        if mb is None:
            print(f"{md}: staged side missing, SKIP (manual)")
            return False
        open(md, "wb").write(mb)  # byte-copy from the SAME side (r327/r329)
        print(f"{md}: byte-copied from {side} side")


ok = True
for f in [
    "results/fundamental_b_layer_filter.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/_attrition_guard_scan.json",
]:
    ok = take_new_snapshot(f) and ok

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
sys.exit(0 if ok else 2)
