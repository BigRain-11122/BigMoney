"""r643 bm-a push-rejection conflict resolver: snapshot + twin-regen faces.
Canon: bigmoney-conflict-resolve SKILL (classifier output), twin-side coupling
r329 (md byte-copy from same side, never json.loads on md), deep ts probe
r311/D-20260927-09, parse-verify before write r185. ALL_FACES members already
resolved via merge_lane_views.py resolve (禁手写 union); this script handles
the remaining: snapshots (fundamental_b_layer_filter, _attrition_guard_scan)
+ twin-regen families (REPORT/LIVE)."""
import json
import re
import subprocess
import sys

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"


def stage_blob(path, stage):
    r = subprocess.run(["git", "-C", ROOT, "show", ":%d:%s" % (stage, path)],
                       capture_output=True)
    if r.returncode != 0:
        raise SystemExit("stage %d read fail for %s: %s" % (stage, path, r.stderr[:200]))
    return r.stdout


def find_ts(obj, depth=0):
    """Deep-scan for the newest wall-clock ts string in nested layers (r311)."""
    best = None
    if depth > 8:
        return None
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = str(k).replace("_", "").replace("-", "").lower()
            if isinstance(v, str) and re.match(r"^20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}", v):
                if ("ts" in nk or "time" in nk or "generated" in nk or "updated" in nk
                        or "date" in nk or "when" in nk or "seen" in nk or "scan" in nk):
                    if best is None or v > best:
                        best = v
            sub = find_ts(v, depth + 1)
            if sub and (best is None or sub > best):
                best = sub
    elif isinstance(obj, list):
        for v in obj:
            sub = find_ts(v, depth + 1)
            if sub and (best is None or sub > best):
                best = sub
    return best


def take_new_snapshot(path):
    o = stage_blob(path, 2)
    m = stage_blob(path, 3)
    try:
        oj = json.loads(o.decode("utf-8"))
        mj = json.loads(m.decode("utf-8"))
    except Exception as e:
        print("[%s] parse fail -> cannot ts-adjudicate: %s" % (path, e))
        return None
    to, tm = find_ts(oj), find_ts(mj)
    side = None
    if to and tm:
        side = 2 if to > tm else (3 if tm > to else 2)  # tie -> HEAD-side origin? tie=2 per r140 (HEAD at rebase = origin side)
    elif tm:
        side = 3
    elif to:
        side = 2
    print("[%s] origin_ts=%s local_ts=%s -> side=%s" % (path, to, tm, side))
    if side is None:
        return None
    blob = o if side == 2 else m
    with open(ROOT + "\\" + path.replace("/", "\\"), "wb") as f:
        f.write(blob)
    json.loads(blob.decode("utf-8"))  # parse-verify the written bytes
    return side


def twin_family(json_path, md_paths):
    """json decides the side by top-level generated_at (authoritative regen
    clock; inner face ts may tie across sides), every twin byte-copies same
    side; fallback to deep max-ts probe only if generated_at absent."""
    o = stage_blob(json_path, 2)
    m = stage_blob(json_path, 3)
    oj, mj = json.loads(o.decode("utf-8")), json.loads(m.decode("utf-8"))
    go, gm = oj.get("generated_at"), mj.get("generated_at")
    if go and gm and go != gm:
        side = 3 if gm > go else 2
        print("[%s] generated_at origin=%s local=%s -> side=%d" % (json_path, go, gm, side))
    else:
        to, tm = find_ts(oj), find_ts(mj)
        side = 2 if (to or "") >= (tm or "") else 3  # tie -> origin (first-landed keeps berth)
        print("[%s] deep-probe origin_ts=%s local_ts=%s -> side=%d" % (json_path, to, tm, side))
    for p in [json_path] + md_paths:
        blob = stage_blob(p, side)
        with open(ROOT + "\\" + p.replace("/", "\\"), "wb") as f:
            f.write(blob)
        if p.endswith(".json"):
            json.loads(blob.decode("utf-8"))  # parse-verify
    return side


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "snap"):
        for p in ("results/fundamental_b_layer_filter.json",
                  "results/_attrition_guard_scan.json"):
            if take_new_snapshot(p) is None:
                raise SystemExit("FAIL: %s needs manual adjudication" % p)
    if what in ("all", "twins"):
        twin_family("docs/daily_report/REPORT-2026-10-03.json",
                    ["docs/daily_report/REPORT-2026-10-03.md"])
        twin_family("docs/live_usage/LIVE-2026-10-03.json",
                    ["docs/live_usage/LIVE-2026-10-03.md",
                     "docs/live_usage/LIVE-latest.json",
                     "docs/live_usage/LIVE-latest.md"])
    print("resolver done")
