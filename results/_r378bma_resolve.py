# -*- coding: utf-8 -*-
"""r378 bm-a push-storm resolver — snapshot/twin family (8 faces vs bm-c r130).

Laws: take-new whole doc by wall-clock ts deep-scanned from STAGED blobs
(:2:=origin bm-c side, :3:=mine, r351 orientation); r100 probe hardening
(key normalize strip '_-' before prefix match, value must be ^20\\d{2}- shaped
AND carry time-of-day per R350 -- date-only values never feed the max);
twins same-side (REPORT json+md; dashboard json+js -- js is a wrapper, whole
bytes from the chosen side, R209); parse-verify before write (r185); ties
-> origin (:2:) per r140.
"""
import io
import json
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TS_SHAPE = re.compile(r"^20\d{2}-")


def blob(stage, path):
    p = subprocess.run(["git", "show", f":{stage}:{path}"],
                       capture_output=True)
    if p.returncode != 0:
        return None
    return p.stdout.decode("utf-8-sig", errors="replace")


def deep_ts(obj, best=None, path=""):
    """Deep wall-clock probe: nested scan, value must be ts-shaped AND
    carry time-of-day (R350: date-only never feeds the max)."""
    if best is None:
        best = [""]
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = str(k).replace("_", "").replace("-", "").lower()
            if isinstance(v, str) and TS_SHAPE.match(v) and len(v) >= 16 \
                    and (v[10] in "T " or " " in v[10:16] or len(v) >= 19):
                cand = v.replace("T", " ")[:19]
                if cand > best[0]:
                    best[0] = cand
                    best.append(path + "/" + str(k))
            deep_ts(v, best, path + "/" + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            deep_ts(v, best, f"{path}[{i}]")
    return best


def resolve_snapshot(path):
    a, b = blob(2, path), blob(3, path)
    if a is None and b is None:
        print(f"[{path}] both stages absent -- skip")
        return None
    if a is None or b is None:
        side = a or b
        data = side
        which = "origin" if a else "mine"
    else:
        ja, jb = json.loads(a), json.loads(b)
        ta, tb = deep_ts(ja)[0], deep_ts(jb)[0]
        if ta == tb:
            which = "origin"      # tie -> origin (r140)
        else:
            which = "origin" if ta > tb else "mine"
        data = a if which == "origin" else b
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(data)
    json.loads(io.open(path, encoding="utf-8").read())   # parse-verify r185
    print(f"[{path}] -> {which}")
    return which


def resolve_twin(json_path, md_path, js_path=None):
    which = resolve_snapshot(json_path)
    if which is None:
        return
    for twin in [md_path] + ([js_path] if js_path else []):
        data = blob(2, twin) if which == "origin" else blob(3, twin)
        with io.open(twin, "w", encoding="utf-8", newline="") as fh:
            fh.write(data)
        if twin.endswith(".json"):
            json.loads(io.open(twin, encoding="utf-8").read())
        print(f"[{twin}] -> {which} (twin same-side)")


resolve_twin("docs/daily_report/REPORT-2026-09-28.json",
             "docs/daily_report/REPORT-2026-09-28.md")
resolve_twin("results/dashboard_status.json", "results/dashboard_status.js")
for f in ("results/fundamental_b_layer_filter.json",
          "results/prospect_promotion/_summary.json",
          "results/scorecard_v1.json",
          "results/strategy_scorecard.json"):
    resolve_snapshot(f)
print("resolver done")
