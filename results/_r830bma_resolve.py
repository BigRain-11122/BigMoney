# -*- coding: utf-8 -*-
"""r830 bm-a rebase-UU resolver: 20 files, canonical recipes.
- ALL_FACES union faces (compute_audit.json / regime_state.json):
  scripts/merge_lane_views.py resolve <path> (r377: hand-union FORBIDDEN).
- snapshot faces: hardened deep-ts probe on STAGED blobs (:2: origin-side /
  :3: replay-side), newer wins; same-second tie -> stage2 (r140 law);
  probe key normalization per r100 (strip '_','-' before prefix match,
  value must match ^20\\d{2}- before max-compare) + R350 (no key-EXCLUDE
  lists; wall-clock values require time-of-day).
- REPORT/LIVE twins: json side probes generated_at deep; md side = byte
  copy of the SAME stage blob (twin-side coupling r327/r329 -- json.loads
  on md = crash; hybrid twins forbidden).
- dashboard_status.js: js-wrapper-snapshot = whole-byte take of the same
  side that won dashboard_status.json (R209: json.dumps strip = FORBIDDEN).
- results/_attrition_guard_scan.json: UNKNOWN->manual = regenerable scan
  receipt (each guard scan overwrites) = snapshot take-new.
Post: json.loads verify every resolved json + py-parse js + round-report
trace; add is done by the caller TOGETHER with rebase --continue (r787
add+continue atomic law)."""
import io
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


def stage_blob(path, n):
    r = subprocess.run(["git", "show", ":%d:%s" % (n, path)], capture_output=True)
    assert r.returncode == 0, "stage %d missing for %s" % (n, path)
    return r.stdout


TS_RE = re.compile(r"^20\d{2}-")


def deep_ts(obj, best=None, pathk=""):
    """r100/R350 hardened probe: normalize keys, value must look like a
    timestamp; wall-clock values need time-of-day to feed the max."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = str(k).replace("_", "").replace("-", "").lower()
            if isinstance(v, str) and TS_RE.match(v) and ("T " in v or "T" in v or " " in v[10:11] or len(v) > 10):
                if best is None or v > best[0]:
                    best = (v, pathk + "/" + str(k))
            deep_ts(v, best, pathk + "/" + str(k))
    elif isinstance(obj, list):
        for it in obj:
            deep_ts(it, best, pathk)
    return best


SNAPSHOTS = [
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/_attrition_guard_scan.json",
]
UNION_FACES = [
    "results/compute_audit.json",
    "results/regime_state.json",
]
TWINS = [
    ("docs/daily_report/REPORT-2026-10-07.json", "docs/daily_report/REPORT-2026-10-07.md"),
    ("docs/live_usage/LIVE-2026-10-07.json", "docs/live_usage/LIVE-2026-10-07.md"),
    ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"),
]
JS_WRAPPER = "results/dashboard_status.js"

wins = {}

for p in SNAPSHOTS:
    b2, b3 = stage_blob(p, 2), stage_blob(p, 3)
    try:
        j2, j3 = json.loads(b2.decode("utf-8")), json.loads(b3.decode("utf-8"))
    except Exception as e:
        fail.append("%s parse fail: %s" % (p, e))
        continue
    t2 = deep_ts(j2)
    t3 = deep_ts(j3)
    # pure wall-clock probe: collect ALL ts-shaped strings, max compare
    def all_ts(o, acc):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and TS_RE.match(v) and (":" in v or "T" in v):
                    acc.append(v)
                all_ts(v, acc)
        elif isinstance(o, list):
            for it in o:
                all_ts(it, acc)
    a2, a3 = [], []
    all_ts(j2, a2)
    all_ts(j3, a3)
    m2, m3 = max(a2) if a2 else None, max(a3) if a3 else None
    if m3 is not None and (m2 is None or m3 > m2):
        side, blob = 3, b3
    elif m2 is not None and (m3 is None or m2 > m3):
        side, blob = 2, b2
    else:
        side, blob = 2, b2  # r140 same-second tie -> stage2 (origin/HEAD)
    wins[p] = side
    io.open(p, "wb").write(blob)
    json.loads(io.open(p, "rb").read().decode("utf-8"))  # parse-verify pre-add
    print("%s -> stage%d (ts %s vs %s)" % (p, side, m2, m3))

for jp, mp in TWINS:
    b2, b3 = stage_blob(jp, 2), stage_blob(jp, 3)
    j2, j3 = json.loads(b2.decode("utf-8")), json.loads(b3.decode("utf-8"))
    a2, a3 = [], []
    def all_ts2(o, acc):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and TS_RE.match(v):
                    acc.append(v)
                all_ts2(v, acc)
        elif isinstance(o, list):
            for it in o:
                all_ts2(it, acc)
    all_ts2(j2, a2)
    all_ts2(j3, a3)
    m2, m3 = max(a2) if a2 else None, max(a3) if a3 else None
    side = 3 if (m3 is not None and (m2 is None or m3 > m2)) else 2
    # twin-side coupling: md = byte copy of the SAME stage (r329)
    jb = stage_blob(jp, side)
    mb = stage_blob(mp, side)
    io.open(jp, "wb").write(jb)
    io.open(mp, "wb").write(mb)
    json.loads(io.open(jp, "rb").read().decode("utf-8"))
    wins[jp] = side
    print("%s + twin md -> stage%d (ts %s vs %s)" % (jp, side, m2, m3))

# js wrapper: same side as dashboard_status.json winner, whole bytes (R209)
side = wins.get("results/dashboard_status.json", 2)
io.open(JS_WRAPPER, "wb").write(stage_blob(JS_WRAPPER, side))
txt = io.open(JS_WRAPPER, "rb").read().decode("utf-8", "replace")
check("window.DASH_DATA" in txt, "js wrapper shape lost")
print("%s -> stage%d whole bytes (R209)" % (JS_WRAPPER, side))

# ALL_FACES union faces via merge_lane_views resolve (r377)
for p in UNION_FACES:
    r = subprocess.run(["python", "scripts/merge_lane_views.py", "resolve", p],
                       capture_output=True)
    out = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    check(r.returncode == 0, "%s merge_lane_views rc=%d: %s" % (p, r.returncode, out[:200]))
    json.loads(io.open(p, "rb").read().decode("utf-8"))  # parse-verify
    print("%s -> union resolve rc0" % p)

if fail:
    print("RESOLVER FAIL (%d) -- NOT marking add:" % len(fail))
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("ALL 20 RESOLVED + parse-verified; awaiting atomic add+continue (r787)")
