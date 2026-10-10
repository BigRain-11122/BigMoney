"""r956 bm-a rebase-conflict manual resolver (r185 receipt law).

Scope: faces NOT covered by merge_lane_views resolve ALL_FACES:
  - snapshot take-new: fundamental_b_layer_filter / _attrition_guard_scan / queue_head_collision_probe
  - same-day regen twins: docs/daily_report/REPORT-2026-10-10.{json,md}
                         docs/live_usage/LIVE-2026-10-10.{json,md} + LIVE-latest.{json,md}
Rebase stage law (r351): :2: = origin side (ours during rebase), :3: = local side.
Twin law (r327/r329/r439bmb): json face deep-ts probe decides side; md face = byte-copy
from the SAME side stage blob (md is not JSON; never json-dump md).
Probe law (R350): deep-scan nested layers, values must look like wall-clock stamps.
All JSON outputs parse-verified before write-back (r185).
"""
import json
import re
import subprocess
import sys

GIT = r"C:\Program Files\Git\cmd\git.exe"
TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")


def stage_blob(stage: str, path: str) -> bytes:
    out = subprocess.run([GIT, "show", f":{stage}:{path}"], capture_output=True, check=False)
    if out.returncode != 0:
        raise RuntimeError(f"stage {stage} read fail for {path}: {out.stderr[:200]!r}")
    return out.stdout


def has_stages(path: str) -> bool:
    """A file only has :2:/:3: stages while unmerged; skip clean-replayed files."""
    for s in ("2", "3"):
        r = subprocess.run([GIT, "show", f":{s}:{path}"], capture_output=True, check=False)
        if r.returncode != 0:
            return False
    return True


def deep_ts_probe(obj, found):
    if isinstance(obj, dict):
        for v in obj.values():
            deep_ts_probe(v, found)
    elif isinstance(obj, list):
        for v in obj:
            deep_ts_probe(v, found)
    elif isinstance(obj, str) and TS_RE.match(obj):
        found.append(obj)
    return found


def pick_side(path):
    b2 = stage_blob("2", path)
    b3 = stage_blob("3", path)
    j2 = json.loads(b2.decode("utf-8"))
    j3 = json.loads(b3.decode("utf-8"))
    t2 = max(deep_ts_probe(j2, []), default="")
    t3 = max(deep_ts_probe(j3, []), default="")
    if t2 == t3:
        # same-second tie -> HEAD/origin side (r140 law)
        side = 2 if t2 else 2
        reason = f"tie {t2!r} -> origin(:2:)"
    else:
        side = 3 if t3 > t2 else 2
        reason = f"origin(:2:)={t2} local(:3:)={t3} -> :{side}:"
    return side, b2, b3, reason


def write_bytes(path, data):
    with open(path, "wb") as f:
        f.write(data)


def main():
    decisions = []

    # --- snapshot take-new faces (json only) ---
    for p in [
        "results/fundamental_b_layer_filter.json",
        "results/_attrition_guard_scan.json",
        "results/queue_head_collision_probe.json",
    ]:
        if not has_stages(p):
            decisions.append(f"SKIP {p}: not unmerged (clean replay)")
            continue
        side, b2, b3, reason = pick_side(p)
        chosen = b2 if side == 2 else b3
        json.loads(chosen.decode("utf-8"))  # parse-verify before write
        write_bytes(p, chosen)
        decisions.append(f"SNAPSHOT {p}: {reason}")

    # --- twin families: json decides, md byte-copies same side ---
    for family in [
        ["docs/daily_report/REPORT-2026-10-10.json", "docs/daily_report/REPORT-2026-10-10.md"],
        [
            "docs/live_usage/LIVE-2026-10-10.json",
            "docs/live_usage/LIVE-2026-10-10.md",
            "docs/live_usage/LIVE-latest.json",
            "docs/live_usage/LIVE-latest.md",
        ],
    ]:
        anchor = family[0]
        if not has_stages(anchor):
            decisions.append(f"SKIP family {anchor}: not unmerged (clean replay)")
            continue
        side, b2, b3, reason = pick_side(anchor)
        for p in family:
            b2 = stage_blob("2", p)
            b3 = stage_blob("3", p)
            chosen = b2 if side == 2 else b3
            if p.endswith(".json"):
                json.loads(chosen.decode("utf-8"))  # parse-verify
            write_bytes(p, chosen)
            decisions.append(f"TWIN {p}: side=:{side}: ({reason} via anchor {anchor})")

    for d in decisions:
        print(d)
    return 0


if __name__ == "__main__":
    sys.exit(main())
