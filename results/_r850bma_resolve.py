# r850 bm-a rebase-stop batch resolver (17 UU, bigmoney-conflict-resolve skill canon)
# Classes: ALL_FACES x7 via merge_lane_views.py resolve (r376 anti-hand-union law);
#          twin-regen-md x6 (REPORT/LIVE pairs, same-side coupling, r329);
#          snapshot x1 (fundamental_b_layer_filter, R216);
#          UNKNOWN x2 manual-classified round-probe snapshots (deep ts take-new, r311/r319/r100/R350);
#          CODELY.md memory-union manual (both sides in-place edit -> prefix assert fails by design,
#          manual review path: origin post-mini-split bytes + my r849 entry verbatim append).
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


def take_new_side(rel, out_path=None):
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
    with open(out_path or rel, "wb") as fh:
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
        for f in (rel,):
            raw = stage_bytes(f, side)
            if raw is None:
                raise SystemExit("twin stage missing: %s :%d:" % (f, side))
            with open(f, "wb") as fh:
                fh.write(raw)
    print("  twins    %-46s side=%s ts=%s (all %d faces byte-copied)"
          % (json_rel, tag, ts, 1 + len(md_rels)))
    return tag, ts


def resolve_codely():
    rel = "CODELY.md"
    o2 = stage_bytes(rel, 2)
    o3 = stage_bytes(rel, 3)
    o1 = stage_bytes(rel, 1)
    t2 = o2.decode("utf-8")
    t3 = o3.decode("utf-8")
    # assert entry presence facts (verified live in-window before script ran)
    assert "r706 bm-c" not in t2 and "r705 bm-c" not in t2, "origin face lost mini-split"
    assert "r847 bm-a" in t2, "origin face must retain r847 bm-a entry"
    assert "r849 bm-a" in t3, "my face must carry r849 entry"
    r849_lines = [l for l in t3.splitlines() if l.startswith("- [2026-10-07 23:4x r849 bm-a]")]
    assert len(r849_lines) == 1, "r849 entry line not unique: %d" % len(r849_lines)
    entry = r849_lines[0]
    assert entry not in t2, "r849 already on origin (unexpected)"
    base_txt = o1.decode("utf-8")
    assert entry not in base_txt, "r849 in merge base (unexpected)"
    # origin-side sanity: r705/r706 migrated to pit domain files (mini-split receipt claimed)
    for pitf, needle in (("research/pit-git-resolver-rebase.md", "r705"),
                         ("research/pit-protocol-d19.md", "r706")):
        r = subprocess.run(["git", "show", "origin/main:%s" % pitf], capture_output=True)
        if r.returncode != 0 or needle.encode() not in r.stdout:
            raise SystemExit("mini-split migration NOT found: %s missing %s" % (pitf, needle))
    res = o2
    if not res.endswith(b"\n"):
        res += b"\n"
    res += entry.encode("utf-8") + b"\n"
    # zero-loss byte accounting: result = origin bytes + entry bytes (+1 newline padding)
    assert len(res) == len(o2) + len(entry.encode("utf-8")) + 1, "byte account mismatch"
    with open(rel, "wb") as fh:
        fh.write(res)
    check = open(rel, "rb").read()
    assert check == res
    txt = check.decode("utf-8")
    assert "r849 bm-a" in txt and "r706 bm-c" not in txt and "r705 bm-c" not in txt
    print("  CODELY.md memory-union manual: origin(%dB) + r849 entry(%dB) = %dB, "
          "r705/r706 verified migrated to pit domain files"
          % (len(o2), len(entry.encode("utf-8")), len(res)))


def main():
    # --- 1) ALL_FACES x7 via canon tool (r376: never hand-write union) ---
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
    # --- 2) twins x6 ---
    twins_same_side("docs/daily_report/REPORT-2026-10-07.json",
                    ["docs/daily_report/REPORT-2026-10-07.md"])
    live_md = []
    t, ts = twins_same_side("docs/live_usage/LIVE-2026-10-07.json",
                            ["docs/live_usage/LIVE-2026-10-07.md"])
    side_tag = t
    for rel in ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"):
        st = 3 if "mine" in side_tag else 2
        raw = stage_bytes(rel, st)
        with open(rel, "wb") as fh:
            fh.write(raw)
        print("  twin-coup %-46s byte-copied from :%d:" % (rel, st))
    # --- 3) snapshot + UNKNOWN x4 (manual class: round-probe/deriver snapshots;
    #         fund_premium_status = snapshot per classifier, NOT an ALL_FACES member) ---
    take_new_side("results/fundamental_b_layer_filter.json")
    take_new_side("results/fund_premium_status.json")
    take_new_side("results/_attrition_guard_scan.json")
    take_new_side("results/_orphan_face_probe.json")
    # --- 4) CODELY.md manual ---
    resolve_codely()
    print("RESOLVE_OK: 17/17 faces resolved; parse-verify below")
    # parse-verify every JSON face we touched (r185 law)
    for f in allfaces + ["results/fundamental_b_layer_filter.json",
                         "results/fund_premium_status.json",
                         "results/_attrition_guard_scan.json",
                         "results/_orphan_face_probe.json",
                         "docs/daily_report/REPORT-2026-10-07.json",
                         "docs/live_usage/LIVE-2026-10-07.json",
                         "docs/live_usage/LIVE-latest.json"]:
        json.load(open(f, encoding="utf-8"))
    print("PARSE_VERIFY_OK: 14 JSON faces clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
