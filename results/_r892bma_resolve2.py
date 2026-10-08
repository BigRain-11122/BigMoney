# -*- coding: utf-8 -*-
"""r892 bm-a rebase-race resolver, part 2: twin-regen-md + snapshot faces.

13-UU batch vs bm-c r778 (push-rejection race, exception face per conflict
skill trigger sec.1). Part 1 (6 ALL_FACES members) already resolved via
merge_lane_views.py resolve (union recipes, parse-verified). This part:

  REPORT-2026-10-08 json+md twin  -> snapshot same-side: json deep-probes
      generated ts per side, newer side wins; md byte-copied from the SAME
      side (r327/r329 law: md is not JSON, no hybrid twins).
  LIVE-2026-10-08 + LIVE-latest (json+md, 4 files) -> all LIVE-* take the
      SAME side by generated ts (r439bmb law).
  fundamental_b_layer_filter.json -> snapshot take-new by updated ts (R216).

Stage orientation per r351 pin: :2: = origin side (bm-c), :3: = local side
(bm-a, this machine). Bytes read via subprocess (zero PS pipe, r209).
Parse-verify before write-back (r185). Same-second tie -> stage2/origin side
(r140 law).
"""
import json
import re
import subprocess
import sys

GIT = r"C:\Program Files\Git\cmd\git.exe"


def stage_blob(stage, path):
    r = subprocess.run([GIT, "show", f"{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"stage {stage} read fail {path}: {r.stderr[:200]}")
    return r.stdout


TS_KEY_RE = re.compile(r"^(generated_at|generated|updated|updated_at|ts|asof)$")
TS_VAL_RE = re.compile(r"^20\d{2}-")


def deep_ts(obj, best=""):
    """Deep-scan for the max ts-looking value (r311 deep probe)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if TS_KEY_RE.match(str(k)) and isinstance(v, str) and TS_VAL_RE.match(v):
                if v > best:
                    best = v
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for it in obj:
            best = deep_ts(it, best)
    return best


def resolve_snapshot(path, side_hint=None):
    b2 = stage_blob(":2", path)
    b3 = stage_blob(":3", path)
    t2 = deep_ts(json.loads(b2.decode("utf-8")))
    t3 = deep_ts(json.loads(b3.decode("utf-8")))
    if t3 > t2:
        side, blob = ":3", b3
    else:
        side, blob = ":2", b2   # tie or older local -> origin side (r140)
    with open(path, "wb") as f:
        f.write(blob)
    # parse-verify (r185)
    json.loads(open(path, "rb").read().decode("utf-8"))
    print(f"[resolve] {path}: side={side} (ts origin={t2!r} local={t3!r}) -> {len(blob)}B parse-verified")
    return side


def twin_pair(json_path, md_path):
    side = resolve_snapshot(json_path)
    stage = ":3" if side == ":3" else ":2"
    bmd = stage_blob(stage, md_path)
    with open(md_path, "wb") as f:
        f.write(bmd)
    print(f"[resolve] {md_path}: byte-copied from SAME side {stage} ({len(bmd)}B)")


# --- REPORT twin ---
twin_pair("docs/daily_report/REPORT-2026-10-08.json", "docs/daily_report/REPORT-2026-10-08.md")

# --- LIVE quad: side decided ONCE on the dated json, applied to all 4 ---
side = resolve_snapshot("docs/live_usage/LIVE-2026-10-08.json")
stage = ":3" if side == ":3" else ":2"
for p in ("docs/live_usage/LIVE-2026-10-08.md",
          "docs/live_usage/LIVE-latest.json",
          "docs/live_usage/LIVE-latest.md"):
    b = stage_blob(stage, p)
    with open(p, "wb") as f:
        f.write(b)
    if p.endswith(".json"):
        json.loads(open(p, "rb").read().decode("utf-8"))
    print(f"[resolve] {p}: byte-copied from SAME side {stage} ({len(b)}B)")

# --- fundamental_b_layer_filter snapshot ---
resolve_snapshot("results/fundamental_b_layer_filter.json")

print("part-2 resolver done: 7/13 faces written parse-verified")
