# r415 bm-a rebase resolver part 2: snapshot take-new + twin-regen-md faces.
# Laws: r209 (bytes via subprocess, no PS redirect), r311/r319 deep ts probe,
# r100 probe hardening (value must match ^20\d{2}- with time-of-day),
# r327/r329 twin-side coupling (json picks side, md byte-copied from SAME side),
# r140 same-second tie -> base_side (:2: origin, r351 direction in rebase replay).
import json
import re
import subprocess
import sys

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def stage_blob(path, stage):
    p = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if p.returncode != 0:
        return None
    return p.stdout


def deep_ts(obj, best=""):
    """Deep-scan nested layers for the freshest wall-clock ts value (r311)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = str(k).lower().replace("_", "").replace("-", "")
            if isinstance(v, str) and TS_RE.match(v) and ("ts" in nk or "time" in nk
                    or "updated" in nk or "generated" in nk or "cutoff" in nk):
                if v > best:
                    best = v
            else:
                best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    return best


def resolve_snapshot(path, prefer_on_tie=2):
    a = stage_blob(path, 2)  # origin/base side
    b = stage_blob(path, 3)  # local/replay side (mine)
    if a is None and b is None:
        print(f"[{path}] both stages missing -- skip")
        return
    if a is None:
        picked, side = b, 3
    elif b is None:
        picked, side = a, 2
    else:
        ta = deep_ts(json.loads(a))
        tb = deep_ts(json.loads(b))
        if tb > ta:
            picked, side = b, 3
        elif ta > tb:
            picked, side = a, 2
        else:
            picked, side = (a, prefer_on_tie)
            side = prefer_on_tie
        print(f"[{path}] ts probe :2:={ta!r} :3:={tb!r} -> side {side}")
    json.loads(picked)  # parse-verify before write (r185)
    open(path, "wb").write(picked)
    print(f"[{path}] wrote side {side}, {len(picked)} bytes, parse-verified")


def resolve_twins(json_path, md_path):
    a = stage_blob(json_path, 2)
    b = stage_blob(json_path, 3)
    ta = deep_ts(json.loads(a)) if a else ""
    tb = deep_ts(json.loads(b)) if b else ""
    if tb > ta:
        side = 3
    elif ta > tb:
        side = 2
    else:
        side = 2  # r140 same-second tie -> base/origin side
    jb = stage_blob(json_path, side)
    mb = stage_blob(md_path, side)
    json.loads(jb)  # parse-verify json face (md face is not JSON -- raw byte copy, r329)
    open(json_path, "wb").write(jb)
    open(md_path, "wb").write(mb)
    print(f"[twins] {json_path} ts :2:={ta!r} :3:={tb!r} -> side {side}; "
          f"json {len(jb)}B + md {len(mb)}B byte-copied from same side")


if __name__ == "__main__":
    resolve_snapshot("results/fundamental_b_layer_filter.json")
    resolve_twins("docs/daily_report/REPORT-2026-09-29.json",
                  "docs/daily_report/REPORT-2026-09-29.md")
    resolve_twins("docs/live_usage/LIVE-2026-09-29.json",
                  "docs/live_usage/LIVE-2026-09-29.md")
    print("PART2 DONE")
