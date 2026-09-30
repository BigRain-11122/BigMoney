#!/usr/bin/env python
"""r464 bm-a rebase conflict resolver (finish batch after merge_lane_views
ALL_FACES resolved 8: compute_audit/regime_state/update_status/lhb/futures/
token_usage/crash_fuse + update_status).  Remaining 13:
  - snapshot take-new by deep-scanned wall-clock ts (R350: time-of-day
    required for max-compare; date-only fallback only if no wall-clock):
    results/fundamental_b_layer_filter.json, results/_attrition_guard_scan.json,
    results/dashboard_status.json, results/scorecard_v1.json,
    results/strategy_scorecard.json, results/prospect_paper/_summary.json,
    results/prospect_promotion/_summary.json
  - js-wrapper side-coupled to dashboard_status.json pick (same producer run,
    whole-bytes, R209): results/dashboard_status.js
  - twin-regen same-day pairs (md+json SAME side, r327/r329):
    docs/daily_report/REPORT-2026-09-30.{json,md},
    docs/live_usage/LIVE-2026-09-30.{json,md}, docs/live_usage/LIVE-latest.{json,md}
Rebase stage law r351: :2: = origin side, :3: = local (bm-a) side.
"""
import json
import re
import subprocess
import sys

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"


def stage_blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], cwd=ROOT,
                        capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def _scan_ts(obj, wall, date):
    if isinstance(obj, dict):
        for v in obj.values():
            wall, date = _scan_ts(v, wall, date)
    elif isinstance(obj, list):
        for v in obj:
            wall, date = _scan_ts(v, wall, date)
    elif isinstance(obj, str):
        if re.match(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:", obj):
            if obj > wall:
                wall = obj
        elif re.match(r"^20\d{2}-\d{2}-\d{2}$", obj):
            if obj > date:
                date = obj
    return wall, date


def deep_ts(obj):
    """R350-hardened: wall-clock values win max-compare; date-only only if
    neither side has wall-clock (existence-first r319 handled by caller)."""
    wall, date = _scan_ts(obj, "", "")
    return wall or date


def resolve_snapshot(path):
    a, b = stage_blob(2, path), stage_blob(3, path)
    ja, jb = json.loads(a), json.loads(b)
    ta, tb = deep_ts(ja), deep_ts(jb)
    if not ta or not tb:
        side = 3 if tb else 2
        print(f"[snapshot] {path}: probe miss one side "
              f"(origin={ta!r} local={tb!r}) -> take "
              f"{'local' if side == 3 else 'origin'} (r319)")
    else:
        side = 3 if tb > ta else 2
        print(f"[snapshot] {path}: origin_ts={ta!r} local_ts={tb!r} -> "
              f"take {'local' if side == 3 else 'origin'}")
    raw = stage_blob(side, path)
    json.loads(raw)
    with open(path, "wb") as fh:
        fh.write(raw)
    json.load(open(path, encoding="utf-8"))
    print("  wrote + parse-verified")


def resolve_dash_pair(json_path, js_path):
    """dashboard_status.json picks the side; .js copies the SAME side whole
    bytes (same producer run -- R209: never json.dumps the wrapper)."""
    ja = json.loads(stage_blob(2, json_path))
    jb = json.loads(stage_blob(3, json_path))
    ta, tb = deep_ts(ja), deep_ts(jb)
    side = 3 if (tb or "") > (ta or "") else 2
    print(f"[dash-pair] json origin_ts={ta!r} local_ts={tb!r} -> take "
          f"{'local' if side == 3 else 'origin'} BOTH faces")
    for p in (json_path, js_path):
        raw = stage_blob(side, p)
        if raw is None:
            print(f"  !! stage {side} missing for {p}")
            continue
        with open(p, "wb") as fh:
            fh.write(raw)
        if p.endswith(".json"):
            json.load(open(p, encoding="utf-8"))
        else:
            assert b"window.DASH_DATA" in raw, "js wrapper missing"
        print(f"  wrote {p}")


def resolve_twin(json_path, md_path):
    ja = json.loads(stage_blob(2, json_path))
    jb = json.loads(stage_blob(3, json_path))
    ta, tb = deep_ts(ja), deep_ts(jb)
    side = 3 if (tb or "") > (ta or "") else 2
    print(f"[twin] {json_path}: origin_ts={ta!r} local_ts={tb!r} -> take "
          f"{'local' if side == 3 else 'origin'} BOTH twins")
    for p in (json_path, md_path):
        raw = stage_blob(side, p)
        if raw is None:
            print(f"  !! stage {side} missing for {p}")
            continue
        with open(p, "wb") as fh:
            fh.write(raw)
        if p.endswith(".json"):
            json.load(open(p, encoding="utf-8"))
        print(f"  wrote {p}")


if __name__ == "__main__":
    import sys as _sys
    storm2 = "--storm2" in _sys.argv
    paths = ["results/fundamental_b_layer_filter.json",
             "results/_attrition_guard_scan.json",
             "results/scorecard_v1.json",
             "results/strategy_scorecard.json"]
    if not storm2:
        paths += ["results/prospect_paper/_summary.json",
                  "results/prospect_promotion/_summary.json"]
    for p in paths:
        resolve_snapshot(p)
    resolve_dash_pair("results/dashboard_status.json",
                      "results/dashboard_status.js")
    resolve_twin("docs/daily_report/REPORT-2026-09-30.json",
                 "docs/daily_report/REPORT-2026-09-30.md")
    resolve_twin("docs/live_usage/LIVE-2026-09-30.json",
                 "docs/live_usage/LIVE-2026-09-30.md")
    resolve_twin("docs/live_usage/LIVE-latest.json",
                 "docs/live_usage/LIVE-latest.md")
    print("RESOLVER DONE")
