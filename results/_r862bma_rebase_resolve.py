# r862 bm-a rebase-stop batch resolver (14 UU, bigmoney-conflict-resolve skill canon,
# r850 bloodline verbatim adaptation: ALL_FACES x6 via merge_lane_views resolve (r376);
# twin-regen-md REPORT/LIVE-2026-10-08 + LIVE-latest same-side coupling (r329);
# snapshot fundamental_b_layer_filter (R216); UNKNOWN->manual round-probe snapshot
# _attrition_guard_scan (deep ts take-new, r311/r319/r100/R350). No CODELY face this batch.
import json
import re
import subprocess
import sys

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")


def stage_bytes(rel, st):
    r = subprocess.run(["git", "show", ":%d:%s" % (st, rel)], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def deep_max_ts(obj):
    """r311 deep-scan + R350: wall-clock values need time-of-day; recursive."""
    best = None

    def walk(o):
        nonlocal best
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, str) and TS_RE.match(o):
            if best is None or o > best:
                best = o
    walk(obj)
    return best


def take_new_side(rel):
    """Deep-ts probe both rebase stages, take newer; tie -> :2: origin (r140)."""
    o2, o3 = stage_bytes(rel, 2), stage_bytes(rel, 3)
    t2 = t3 = None
    try:
        t2 = deep_max_ts(json.loads(o2.decode("utf-8")))
    except Exception:
        t2 = None
    try:
        t3 = deep_max_ts(json.loads(o3.decode("utf-8")))
    except Exception:
        t3 = None
    if t3 is not None and (t2 is None or t3 > t2):
        side, tag, ts = o3, ":3: mine", t3
    elif t2 is not None:
        side, tag, ts = o2, ":2: origin", t2
    else:
        side, tag, ts = o2, ":2: origin (no-ts fail-safe)", None
    with open(rel, "wb") as fh:
        fh.write(side)
    print("  take-new %-46s side=%s ts=%s" % (rel, tag, ts))
    return tag, ts


def twins_same_side(json_rel, md_rels):
    """Pick side ONCE from the json face, copy all twins byte-wise (r329)."""
    o2, o3 = stage_bytes(json_rel, 2), stage_bytes(json_rel, 3)
    t2 = t3 = None
    try:
        t2 = deep_max_ts(json.loads(o2.decode("utf-8")))
    except Exception:
        pass
    try:
        t3 = deep_max_ts(json.loads(o3.decode("utf-8")))
    except Exception:
        pass
    if t3 is not None and (t2 is None or t3 > t2):
        side, tag, ts = 3, ":3: mine", t3
    else:
        side, tag, ts = 2, ":2: origin", t2
    for rel in [json_rel] + md_rels:
        raw = stage_bytes(rel, side)
        if raw is None:
            raise SystemExit("twin stage missing: %s :%d:" % (rel, side))
        with open(rel, "wb") as fh:
            fh.write(raw)
    print("  twins    %-46s side=%s ts=%s (all %d faces byte-copied)"
          % (json_rel, tag, ts, 1 + len(md_rels)))
    return tag, ts


def main():
    # --- 1) ALL_FACES x6 via canon tool (r376: never hand-write union) ---
    allfaces = ["results/compute_audit.json", "results/regime_state.json",
                "results/update_status.json", "results/lhb_update_status.json",
                "results/futures_update_status.json",
                "results/token_usage.json"]
    for f in allfaces:
        r = subprocess.run([sys.executable, "scripts/merge_lane_views.py",
                            "resolve", f], capture_output=True, text=True)
        print("  resolve  %-46s rc=%d %s" % (f, r.returncode, (r.stdout or r.stderr).strip()[:120]))
        if r.returncode != 0:
            raise SystemExit("merge_lane_views resolve FAILED for %s" % f)
    # --- 2) twins: REPORT pair + LIVE pair + LIVE-latest pointer pair ---
    twins_same_side("docs/daily_report/REPORT-2026-10-08.json",
                    ["docs/daily_report/REPORT-2026-10-08.md"])
    side_tag, ts = twins_same_side("docs/live_usage/LIVE-2026-10-08.json",
                                   ["docs/live_usage/LIVE-2026-10-08.md"])
    st = 3 if "mine" in side_tag else 2
    for rel in ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"):
        raw = stage_bytes(rel, st)
        if raw is None:
            raise SystemExit("twin stage missing: %s :%d:" % (rel, st))
        with open(rel, "wb") as fh:
            fh.write(raw)
        print("  twin-coup %-46s byte-copied from :%d:" % (rel, st))
    # --- 3) snapshot + UNKNOWN->manual class (round-probe/deriver snapshots) ---
    take_new_side("results/fundamental_b_layer_filter.json")
    take_new_side("results/_attrition_guard_scan.json")
    print("RESOLVE_OK: 14/14 faces resolved; parse-verify below")
    # parse-verify every JSON face we touched (r185 law)
    for f in allfaces + ["results/fundamental_b_layer_filter.json",
                         "results/_attrition_guard_scan.json",
                         "docs/daily_report/REPORT-2026-10-08.json",
                         "docs/live_usage/LIVE-2026-10-08.json",
                         "docs/live_usage/LIVE-latest.json"]:
        json.load(open(f, encoding="utf-8"))
    print("PARSE_VERIFY_OK: 11 JSON faces clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
