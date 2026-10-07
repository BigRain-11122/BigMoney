# -*- coding: utf-8 -*-
"""r834 bm-a rebase conflict resolver leg-2: snapshot faces (8 files).

Law lineage: bigmoney-conflict-resolve SKILL + r98/r99/r100 (same-day
idempotent regen twins) + r327/r329 (twin-side coupling: json face
probes ts to pick the side, md face byte-copies from the SAME side --
md twins are NOT JSON, json.loads on them crashes; never take
different sides per twin) + r439bmb (LIVE-* twins all take the same
side) + R216 (per-run verdict snapshots take-new) + R350 (ts probe:
staged blobs, not working tree; value must match ^20\\d{2}-).

Faces:
  - docs/daily_report/REPORT-2026-10-07.{json,md}  (coupled pair)
  - docs/live_usage/LIVE-2026-10-07.{json,md} + LIVE-latest.{json,md}
    (coupled quad, same side all four)
  - results/fundamental_b_layer_filter.json (snapshot take-new)
  - results/_attrition_guard_scan.json (classifier UNKNOWN -> manual
    adjudication: attrition guard scan evidence, regenerable by
    `python scripts/attrition_ledger_guard.py scan` each run, single
    face = latest scan wins wholesale = snapshot semantics; probe ts)
"""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

fail = []


def check(cond, msg):
    if not cond:
        fail.append(msg)
        print("FAIL:", msg)


def stage_blob(n, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (n, path)], capture_output=True)
    check(r.returncode == 0, "stage %d blob missing: %s" % (n, path))
    return r.stdout


TS_PAT = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")


def deep_ts(obj, best=""):
    """Deep-scan nested layers for the newest 20xx timestamp (r311 law)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and TS_PAT.match(v) and v > best:
                best = v
            else:
                best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    elif isinstance(obj, str) and TS_PAT.match(obj) and obj > best:
        best = obj
    return best


def resolve_pair(paths, probe_ts=True):
    """Pick ONE side for all twin files of a face, byte-copy every file
    from that side's blob."""
    o2 = stage_blob(2, paths[0])   # origin side
    o3 = stage_blob(3, paths[0])   # our side
    if probe_ts:
        ts2 = deep_ts(json.loads(o2.decode("utf-8", "replace")))
        ts3 = deep_ts(json.loads(o3.decode("utf-8", "replace")))
        check(ts2 and ts3, "ts probe empty for %s: %r vs %r" % (paths[0], ts2, ts3))
        side = 3 if ts3 >= ts2 else 2   # same-second tie -> HEAD/ours (r140)
        print("%s: origin ts=%s ours ts=%s -> side %d" % (paths[0], ts2, ts3, side))
    else:
        side = 3
    for p in paths:
        blob = stage_blob(side, p)
        # json faces must parse before write-back (r185 law)
        if p.endswith(".json"):
            json.loads(blob.decode("utf-8", "replace"))
        open(p, "wb").write(blob)
        print("  wrote %s (%d B, side %d)" % (p, len(blob), side))
    return side


# --- REPORT twins (json probes, both files same side) -------------------
resolve_pair([
    "docs/daily_report/REPORT-2026-10-07.json",
    "docs/daily_report/REPORT-2026-10-07.md",
])

# --- LIVE quad (json probes, all four same side) ------------------------
resolve_pair([
    "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
])

# --- plain snapshots -----------------------------------------------------
resolve_pair(["results/fundamental_b_layer_filter.json"])
resolve_pair(["results/_attrition_guard_scan.json"])

if fail:
    print("RESULT: FAIL (%d) -- DO NOT git add" % len(fail))
    sys.exit(1)
print("resolver leg-2 rc0: 8 snapshot faces resolved (twins same-side, "
      "json parse-verified pre-write)")
