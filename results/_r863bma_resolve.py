# -*- coding: utf-8 -*-
"""r863 bm-a S0 rebase-storm manual UU resolver (8 non-ALL_FACES files).

Laws applied:
- twin-regen-md (r327/r329): REPORT/LIVE json+md twins take the SAME side, decided
  by deep ts probe on the json blob; md blob byte-copied from the same side.
- LIVE-latest twins follow the LIVE-2026-10-08 side (latest = same-day copy).
- snapshot take-new (R208/R216): _attrition_guard_scan.json, fundamental_b_layer_filter.json.
- deep-scan ts probe (r311/D-20261002-09), probe existence first (r319);
  wall-clock values require time-of-day (R350); probe STAGED blobs (:2:/:3:), not worktree.
- bytes via subprocess git show (r209: no PS redirect); parse-verify before write (r185).
"""
import json
import re
import subprocess
import sys

WALL = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?")


def blob(stage, path):
    r = subprocess.run(
        ["git", "show", f"{stage}:{path}"],
        capture_output=True,
    )
    if r.returncode != 0:
        raise SystemExit(f"git show {stage}:{path} failed: {r.stderr.decode('utf-8', 'replace')[:300]}")
    return r.stdout


def deep_wallclock(obj, found):
    """Collect all wall-clock-ish values reachable via ts-ish keys AND any key."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            deep_wallclock(v, found)
    elif isinstance(obj, list):
        for v in obj:
            deep_wallclock(v, found)
    elif isinstance(obj, str) and WALL.match(obj):
        found.append(obj)
    return found


def max_ts(b):
    vals = deep_wallclock(json.loads(b), [])
    if not vals:
        return None
    return max(vals)


def take_new(pa, pb):
    """Return 'base' or 'replay' by newest wall-clock ts; tie -> base (:2:) per r140."""
    ta, tb = max_ts(pa), max_ts(pb)
    if ta is None and tb is None:
        return "base"  # both empty: take base side (r140 tie law)
    if tb is None:
        return "base"
    if ta is None:
        return "replay"
    return "replay" if tb > ta else "base"


def write_bytes(path, data):
    with open(path, "wb") as f:
        f.write(data)


def parse_verify(path, data):
    json.loads(data)  # raises on bad json
    print(f"  parse-verified {path}")


def resolve_twin(dated_json, dated_md, probe_label):
    b2, b3 = blob(":2", dated_json), blob(":3", dated_json)
    side = take_new(b2, b3)
    js, md = (b2, blob(":2", dated_md)) if side == "base" else (b3, blob(":3", dated_md))
    print(f"[{probe_label}] side={side} ts_base={max_ts(b2)} ts_replay={max_ts(b3)}")
    write_bytes(dated_json, js)
    write_bytes(dated_md, md)
    parse_verify(dated_json, js)
    return side


def follow_twin(dated_json, dated_md, latest_json, latest_md, side, label):
    st = ":2" if side == "base" else ":3"
    write_bytes(latest_json, blob(st, latest_json))
    write_bytes(latest_md, blob(st, latest_md))
    parse_verify(latest_json, blob(st, latest_json))
    print(f"[{label}] followed side={side}")


def resolve_snapshot(path):
    b2, b3 = blob(":2", path), blob(":3", path)
    side = take_new(b2, b3)
    data = b2 if side == "base" else b3
    print(f"[{path}] side={side} ts_base={max_ts(b2)} ts_replay={max_ts(b3)}")
    write_bytes(path, data)
    parse_verify(path, data)


if __name__ == "__main__":
    # 1) REPORT twin (dated)
    side_r = resolve_twin(
        "docs/daily_report/REPORT-2026-10-08.json",
        "docs/daily_report/REPORT-2026-10-08.md",
        "REPORT-2026-10-08",
    )
    # 2) LIVE dated twin
    side_l = resolve_twin(
        "docs/live_usage/LIVE-2026-10-08.json",
        "docs/live_usage/LIVE-2026-10-08.md",
        "LIVE-2026-10-08",
    )
    # 3) LIVE-latest twins follow the LIVE dated side (same-side coupling)
    follow_twin(
        "docs/live_usage/LIVE-2026-10-08.json",
        "docs/live_usage/LIVE-2026-10-08.md",
        "docs/live_usage/LIVE-latest.json",
        "docs/live_usage/LIVE-latest.md",
        side_l,
        "LIVE-latest",
    )
    # 4) snapshots
    resolve_snapshot("results/_attrition_guard_scan.json")
    resolve_snapshot("results/fundamental_b_layer_filter.json")
    print("MANUAL-RESOLVE-OK")
