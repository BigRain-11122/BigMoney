# -*- coding: utf-8 -*-
"""r952 bm-a rebase conflict resolver (bigmoney-conflict-resolve skill recipes).

Hand-resolves the non-ALL_FACES UU set per classifier output:
  - twin-regen (daily_report + live_usage): json deep-ts probe picks the
    side, ALL same-producer twins (incl. .md and LIVE-latest pointers)
    byte-copy from the SAME side (r98/r99/r100/r329 twin-side coupling).
  - hardened-probe snapshots (scorecard_v1, strategy_scorecard, prospect
    summaries, fundamental_b_layer_filter, dashboard_status.json):
    deep-scan wall-clock ts, r100 key-normalize (strip _/-), value must
    be ^20\\d{2}- WITH time-of-day, no key-EXCLUDE lists (R350), probe
    STAGED blobs (:2: origin / :3: local), tie -> :2: (HEAD, r140).
  - js-wrapper-snapshot (dashboard_status.js): whole-byte take-side
    coupled to dashboard_status.json winner (R209 - never re-serialize).
Writes winner-side raw bytes; parse-verifies JSONs before write.
"""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TS_RE = re.compile(r"^20\d{2}-")
TOD_RE = re.compile(r"[T ]\d{2}:\d{2}")
PREFIXES = ("generated", "updated", "asof", "ts", "stateupdated", "clock",
            "last")


def stage_bytes(stage, path):
    r = subprocess.run(["git", "show", ":%s:%s" % (stage, path)],
                       capture_output=True)
    return r.stdout if r.returncode == 0 else None


def deep_wallclock(obj):
    """Max wall-clock ts anywhere under probe-shaped keys (r100/R350)."""
    best = [None]

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                nk = str(k).replace("_", "").replace("-", "").lower()
                if (isinstance(v, str) and TS_RE.match(v)
                        and TOD_RE.search(v)
                        and any(nk.startswith(p) for p in PREFIXES)):
                    if best[0] is None or v > best[0]:
                        best[0] = v
                walk(v)
        elif isinstance(o, list):
            for it in o:
                walk(it)

    walk(obj)
    return best[0]


def probe_side(path):
    """2 = origin, 3 = local; None-probe on a side = no evidence."""
    sides = {}
    for stage in (2, 3):
        raw = stage_bytes(stage, path)
        if raw is None:
            sides[stage] = None
            continue
        try:
            sides[stage] = deep_wallclock(json.loads(raw.decode("utf-8",
                                                   errors="replace")))
        except Exception:
            sides[stage] = None
    if sides[2] and sides[3]:
        return 2 if sides[2] >= sides[3] else 3
    if sides[3] and not sides[2]:
        return 3
    if sides[2] and not sides[3]:
        return 2
    return 2  # tie / no evidence both sides -> HEAD (:2:) per r140


def write_side(path, stage, verify_json=True):
    raw = stage_bytes(stage, path)
    if raw is None:
        raise SystemExit("FATAL: no stage blob for %s" % path)
    if verify_json and path.endswith(".json"):
        json.loads(raw.decode("utf-8", errors="replace"))  # parse gate
    with open(path, "wb") as fh:
        fh.write(raw)
    print("[resolve] %s <- :%d:" % (path, stage))


report = [
    ("docs/daily_report/REPORT-2026-10-10.json",
     "docs/daily_report/REPORT-2026-10-10.md"),
]
for j, m in report:
    s = probe_side(j)
    write_side(j, s)
    write_side(m, s, verify_json=False)

# live_usage family: one producer run wrote dated pair + latest pointers
live = ["docs/live_usage/LIVE-2026-10-10.json",
        "docs/live_usage/LIVE-2026-10-10.md",
        "docs/live_usage/LIVE-latest.json",
        "docs/live_usage/LIVE-latest.md"]
s_live = probe_side(live[0])
s_latest = probe_side(live[2])
if s_live != s_latest:
    print("[WARN] live dated/latest probes disagree (%d vs %d) -- "
          "per-pair winners" % (s_live, s_latest))
write_side(live[0], s_live)
write_side(live[1], s_live, verify_json=False)
write_side(live[2], s_latest)
write_side(live[3], s_latest, verify_json=False)

# js-wrapper + its json twin: coupled side, whole bytes (R209)
dash_json = "results/dashboard_status.json"
s_dash = probe_side(dash_json)
write_side(dash_json, s_dash)
write_side("results/dashboard_status.js", s_dash, verify_json=False)

# hardened-probe snapshots: raw-byte take-new
for p in ("results/fundamental_b_layer_filter.json",
          "results/scorecard_v1.json",
          "results/strategy_scorecard.json",
          "results/prospect_paper/_summary.json",
          "results/prospect_promotion/_summary.json"):
    write_side(p, probe_side(p))

print("resolver done: 13 files")
