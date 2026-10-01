# -*- coding: utf-8 -*-
"""r506 bm-a rebase batch-2 resolver (13 UU: snapshot + twin-regen classes).

bigmoney-conflict-resolve skill recipes:
- snapshot: deep-ts probe take-new (R350: key strip _/-, value ^20\\d{2}-
  +time-of-day, staged blobs not working tree); same-second tie -> :2:
  origin side (r140).
- twin-regen-md (REPORT/LIVE): json face by deep-ts probe; .md byte-copy
  from the SAME side (r327/r329 -- never hybrid twins).
- per-run snapshot (_attrition_guard_scan): take-new by ts.
Zero union, zero data judgment; parse-verify before write-back (r185).
"""
import json
import re
import subprocess
import sys

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}")


def stage_blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"stage {stage} read fail {path}: {r.stderr[:200]}")
    return r.stdout


def deep_ts(obj, best=""):
    """Recursively collect freshest wall-clock string (R350 hardening)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            kk = re.sub(r"[_\-]", "", str(k).lower())
            if isinstance(v, str) and TS_RE.match(v) and any(
                    h in kk for h in ("generated", "updated", "ts", "time",
                                      "scannedat", "closedat")):
                if v > best:
                    best = v
            else:
                best = deep_ts(v, best)
    elif isinstance(obj, list):
        for x in obj:
            best = deep_ts(x, best)
    return best


def pick_side(path):
    b2 = stage_blob(2, path)          # origin side (r351 stage law)
    b3 = stage_blob(3, path)          # local replay side
    t2 = deep_ts(json.loads(b2.decode("utf-8")))
    t3 = deep_ts(json.loads(b3.decode("utf-8")))
    side = 2 if t3 <= t2 else 3       # tie -> origin (r140)
    return b2, b3, side, t2, t3


def resolve_snapshot(path):
    b2, b3, side, t2, t3 = pick_side(path)
    blob = b2 if side == 2 else b3
    json.loads(blob.decode("utf-8"))  # parse-verify before write
    with open(path, "wb") as f:
        f.write(blob)
    print(f"  {path}: take :{side}: (origin={t2 or 'none'} local={t3 or 'none'})")


def resolve_twin(json_path, md_path):
    b2, b3, side, t2, t3 = pick_side(json_path)
    jblob = b2 if side == 2 else b3
    json.loads(jblob.decode("utf-8"))
    with open(json_path, "wb") as f:
        f.write(jblob)
    for m in md_path:
        mblob = stage_blob(side, m)   # SAME side byte-copy (r327/r329)
        with open(m, "wb") as f:
            f.write(mblob)
    print(f"  {json_path}: twin take :{side}: (origin={t2 or 'none'} "
          f"local={t3 or 'none'}) + {len(md_path)} md same-side byte-copy")


snapshots = [
    # 4 ALL_FACES already resolved via merge_lane_views (r376 tool law);
    # fundamental_b_layer_filter is NOT an ALL_FACES face name -> snapshot recipe.
    "results/fundamental_b_layer_filter.json",
    "results/prospect_promotion/_summary.json",
    "results/_attrition_guard_scan.json",
]
for p in snapshots:
    resolve_snapshot(p)

resolve_twin("docs/daily_report/REPORT-2026-10-01.json",
             ["docs/daily_report/REPORT-2026-10-01.md"])
resolve_twin("docs/live_usage/LIVE-2026-10-01.json",
             ["docs/live_usage/LIVE-2026-10-01.md",
              "docs/live_usage/LIVE-latest.json",
              "docs/live_usage/LIVE-latest.md"])
print("resolver done")
