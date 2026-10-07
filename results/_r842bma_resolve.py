# -*- coding: utf-8 -*-
"""r842 bm-a manual conflict resolver for non-ALL_FACES UU set:
- docs/live_usage/LIVE-2026-10-07.{json,md} + LIVE-latest.{json,md}: twin-side
  coupling (json deep-probe generated ts take-newer decides side; md faces
  byte-copied from the SAME side blob -- r327/r329 law, no hybrid twins)
- results/fundamental_b_layer_filter.json: snapshot take-new by updated ts
  (deep probe, r311/D-09; probe hardening r100: key normalize + value must
  match 20xx- date; probe STAGED blobs not working tree R350)
- results/_attrition_guard_scan.json: classifier UNKNOWN -> manual adjudication
  by form: per-run evidence snapshot (attrition_ledger_guard scan writes it
  each run); newest scan ts wins whole-doc; disclosed as manual call."""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CREATE_NO_WINDOW = 0x08000000

def stage(path, n):
    r = subprocess.run(["git", "show", ":%d:%s" % (n, path)], capture_output=True,
                       creationflags=CREATE_NO_WINDOW)
    assert r.returncode == 0, (path, n, r.stderr[:200])
    return r.stdout

def deep_ts(obj, _depth=0):
    """deep-scan for newest 20xx-.. ts anywhere in the structure"""
    best = None
    if _depth > 12:
        return None
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = str(k).replace("_", "").replace("-", "").lower()
            if isinstance(v, str) and re.match(r"^20\d{2}-\d{2}-\d{2}", v):
                if "ts" in nk or "time" in nk or "at" in nk or "generated" in nk or "updated" in nk or "scan" in nk:
                    if best is None or v > best:
                        best = v
            sub = deep_ts(v, _depth + 1)
            if sub and (best is None or sub > best):
                best = sub
    elif isinstance(obj, list):
        for v in obj:
            sub = deep_ts(v, _depth + 1)
            if sub and (best is None or sub > best):
                best = sub
    return best

def resolve_twin(pair_json, pair_md):
    b2 = stage(pair_json, 2); b3 = stage(pair_json, 3)
    j2 = json.loads(b2.decode("utf-8")); j3 = json.loads(b3.decode("utf-8"))
    t2 = deep_ts(j2); t3 = deep_ts(j3)
    print(pair_json, "origin-ts", t2, "local-ts", t3)
    assert t2 and t3, (t2, t3)
    if t3 >= t2:
        side, jb, md = 3, b3, stage(pair_md, 3)
    else:
        side, jb, md = 2, b2, stage(pair_md, 2)
    open(pair_json, "wb").write(jb)
    open(pair_md, "wb").write(md)
    json.loads(open(pair_json, "rb").read().decode("utf-8"))  # parse-verify
    print("  -> took side", side, "for both twin faces (coupling law)")

def resolve_snapshot(path):
    b2 = stage(path, 2); b3 = stage(path, 3)
    j2 = json.loads(b2.decode("utf-8")); j3 = json.loads(b3.decode("utf-8"))
    t2 = deep_ts(j2); t3 = deep_ts(j3)
    print(path, "origin-ts", t2, "local-ts", t3)
    assert t2 and t3, (t2, t3)
    win = b3 if t3 >= t2 else b2
    open(path, "wb").write(win)
    json.loads(open(path, "rb").read().decode("utf-8"))
    print("  -> took", "local" if t3 >= t2 else "origin", "whole-doc")

resolve_twin("docs/live_usage/LIVE-2026-10-07.json", "docs/live_usage/LIVE-2026-10-07.md")
resolve_twin("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md")
resolve_snapshot("results/fundamental_b_layer_filter.json")
resolve_snapshot("results/_attrition_guard_scan.json")
print("manual set resolved + parse-verified")
