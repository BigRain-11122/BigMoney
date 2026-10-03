# -*- coding: utf-8 -*-
# r628 bm-b rebase conflict resolver (19 UU, classify_conflicts.py recipe routing)
# Stage mapping during REBASE: stage2 = ours = upstream (bm-a 01302cc2d side),
# stage3 = theirs = my replayed commit. Both read as clean blobs from the index.
import json, re, subprocess, sys

ROLLING = {
    "results/compute_audit.json": ["history"],
    "results/regime_state.json": ["history", "transitions", "launches"],
}
JS_WRAPPER = ["results/dashboard_status.js"]
# everything else = snapshot / regenerated-doc: take side with newest embedded ts
SNAPSHOTS = [
    "docs/daily_report/REPORT-2026-10-03.json",
    "docs/daily_report/REPORT-2026-10-03.md",
    "docs/live_usage/LIVE-2026-10-03.json",
    "docs/live_usage/LIVE-2026-10-03.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.json",
    "results/daily_scorecard.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?")


def stage_bytes(path, stage):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)],
                       capture_output=True)
    if r.returncode != 0:
        sys.exit("STAGE FAIL %s stage %d: %s" % (path, stage,
                                                 r.stderr.decode("utf-8", "replace")[:120]))
    return r.stdout


def newest_ts(blob):
    # full-match extraction (findall with a group would return only the
    # seconds fragment -- r628 self-caught, compare on full timestamps)
    hits = [m.group(0) for m in TS_RE.finditer(blob.decode("utf-8", "replace"))]
    return max(hits) if hits else ""


def union_rows(a, b):
    seen, out = set(), []
    for row in list(a) + list(b):
        key = json.dumps(row, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            out.append(row)
    return out


def resolve():
    report = []
    for path in ROLLING:
        ours = json.loads(stage_bytes(path, 2).decode("utf-8", "replace"))
        theirs = json.loads(stage_bytes(path, 3).decode("utf-8", "replace"))
        base_n = {}
        for key in ROLLING[path]:
            a, b = ours.get(key) or [], theirs.get(key) or []
            merged = union_rows(a, b)
            assert len(merged) >= max(len(a), len(b)), "union shrink %s %s" % (path, key)
            base_n[key] = (len(a), len(b), len(merged))
            ours[key] = merged
        # newest snapshot fields take-new: pick the doc with the newer scalar ts
        pick = theirs if newest_ts(stage_bytes(path, 3)) > newest_ts(stage_bytes(path, 2)) else ours
        for k, v in pick.items():
            if k not in ROLLING[path]:
                ours[k] = v
        merged = json.dumps(ours, ensure_ascii=False, indent=1)
        json.loads(merged)
        open(path, "w", encoding="utf-8", newline="").write(merged + "\n")
        report.append((path, "rolling-ledger union", base_n))

    for path in JS_WRAPPER:
        o, t = stage_bytes(path, 2), stage_bytes(path, 3)
        winner = t if newest_ts(t) > newest_ts(o) else o
        assert b"window.DASH_DATA" in winner, "wrapper missing"
        open(path, "wb").write(winner)
        report.append((path, "js-wrapper whole-byte take-new", None))

    for path in SNAPSHOTS:
        o, t = stage_bytes(path, 2), stage_bytes(path, 3)
        to, tt = newest_ts(o), newest_ts(t)
        winner = t if tt > to else o
        if path.endswith(".json"):
            json.loads(winner.decode("utf-8", "replace"))  # parse check
        open(path, "wb").write(winner)
        report.append((path, "snapshot take-new by ts (ours=%s theirs=%s)" % (to, tt), None))

    for path, recipe, extra in report:
        print("RESOLVED %-46s %s %s" % (path, recipe, extra or ""))


if __name__ == "__main__":
    resolve()
