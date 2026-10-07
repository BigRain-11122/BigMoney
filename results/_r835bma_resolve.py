# -*- coding: utf-8 -*-
"""r835 bm-a rebase UU resolver: snapshot/twin/js-wrapper faces (r188/R208/R209/r311/r319/r327/r329/r98-r100/R350 recipes).

Rebase stage law: :2: = ours = base-side (origin/main, bm-c r692 newer);
:3: = theirs = replay-side (bm-a r834 being replayed).

Snapshot family = deep-ts probe take-new whole blob (bytes verbatim).
Twin family (json+md, dated+latest) = ALL twins take the SAME side; md = byte copy from chosen side blob.
js-wrapper = take-side whole bytes, side must match dashboard_status.json choice.
_attrition_guard_scan.json = manual UNKNOWN adjudication: per-run verdict snapshot -> take-new by ts.
"""
import json
import re
import subprocess

TS_RE = re.compile(r"^20\d{2}-")
WALL_RE = re.compile(r"[T ]\d{2}:\d{2}")
PROBE_KEYS = ("asof", "updated", "generated", "scanned", "checked", "ts", "cutoff")


def stage_blob(path, stage):
    # stage 1=base 2=ours(origin) 3=theirs(replay)
    out = subprocess.run(
        ["git", "show", ":%d:%s" % (stage, path)],
        capture_output=True,
    )
    if out.returncode != 0:
        return None
    return out.stdout


def norm(k):
    return k.replace("_", "").replace("-", "").lower()


def deep_ts(obj):
    """Return max wall-clock ts found (R350: value must carry time-of-day)."""
    best = None
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = norm(k)
            if isinstance(v, str) and TS_RE.match(v) and WALL_RE.search(v):
                if any(nk.startswith(pk) for pk in PROBE_KEYS):
                    if best is None or v > best:
                        best = v
            sub = deep_ts(v)
            if sub and (best is None or sub > best):
                best = sub
    elif isinstance(obj, list):
        for v in obj:
            sub = deep_ts(v)
            if sub and (best is None or sub > best):
                best = sub
    return best


def probe_side(path):
    ours = deep_ts(json.loads(stage_blob(path, 2).decode("utf-8")))
    theirs = deep_ts(json.loads(stage_blob(path, 3).decode("utf-8")))
    return 2 if (ours or "") >= (theirs or "") else 3, ours, theirs


def copy_side(path, side):
    blob = stage_blob(path, side)
    if blob is None:
        raise SystemExit("stage blob missing %s side %d" % (path, side))
    with open(path, "wb") as f:
        f.write(blob)
    if path.endswith(".json"):
        json.loads(blob.decode("utf-8"))  # parse-verify before add (r185)
    print("RESOLVED %s -> side %d" % (path, side))


def main():
    sides = {}
    # daily_report twins: json decides, md byte-copies same side (r327/r329)
    s, o, t = probe_side("docs/daily_report/REPORT-2026-10-07.json")
    print("daily_report probe origin=%s replay=%s -> side %d" % (o, t, s))
    copy_side("docs/daily_report/REPORT-2026-10-07.json", s)
    copy_side("docs/daily_report/REPORT-2026-10-07.md", s)
    sides["daily_report"] = s
    # live_usage family: dated + latest all same side (r439bmb)
    s, o, t = probe_side("docs/live_usage/LIVE-2026-10-07.json")
    print("live_usage probe origin=%s replay=%s -> side %d" % (o, t, s))
    for p in [
        "docs/live_usage/LIVE-2026-10-07.json",
        "docs/live_usage/LIVE-2026-10-07.md",
        "docs/live_usage/LIVE-latest.json",
        "docs/live_usage/LIVE-latest.md",
    ]:
        copy_side(p, s)
    sides["live_usage"] = s
    # plain snapshots (UNKNOWN _attrition_guard_scan = per-run verdict snapshot, take-new by ts)
    for p in [
        "results/_attrition_guard_scan.json",
        "results/dashboard_status.json",
        "results/scorecard_v1.json",
        "results/strategy_scorecard.json",
        "results/fundamental_b_layer_filter.json",
    ]:
        s, o, t = probe_side(p)
        print("%s probe origin=%s replay=%s -> side %d" % (p, o, t, s))
        copy_side(p, s)
        sides[p] = s
    # js wrapper: whole bytes from the SAME side chosen for dashboard_status.json (R209)
    js_side = sides["results/dashboard_status.json"]
    copy_side("results/dashboard_status.js", js_side)
    print("ALL_SIDES %s" % json.dumps(sides, sort_keys=True))


if __name__ == "__main__":
    main()
