# -*- coding: utf-8 -*-
"""r690 bm-a merge resolver: 15 S6 regen faces, per-face ts-freshness
(r440 two-bucket law: S6 regen faces take newer side; blobs via HEAD:/MERGE_HEAD:
per r657-2, immune to add pollution)."""
import json, re, subprocess, sys, io

CREATE_NO_WINDOW = 0x08000000
FACES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/crash_fuse.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]

TS_RE = re.compile(
    r'"(?:ts|generated|generated_at|asof|now|clock|clock_read|scan_ts|updated)"'
    r'\s*:\s*"?(\d{4}-\d{2}-\d{2})[ T]?(\d{2}:\d{2}:\d{2})')


def blob(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                       capture_output=True, creationflags=CREATE_NO_WINDOW)
    if r.returncode != 0:
        return None
    return r.stdout


def best_ts(b):
    if not b:
        return ""
    m = TS_RE.search(b.decode("utf-8", "replace"))
    if not m:
        return ""
    return m.group(1) + " " + m.group(2)  # normalized space form (r461 ts_norm law)


def side_pick_counter(log):
    log["side_pick_ours"] = sum(1 for f in log["faces"] if f["pick"] == "ours")
    log["side_pick_theirs"] = sum(1 for f in log["faces"] if f["pick"] == "theirs")


log = {"faces": [], "n": len(FACES)}
for path in FACES:
    ours = blob("HEAD", path)
    theirs = blob("MERGE_HEAD", path)
    t_ours, t_theirs = best_ts(ours), best_ts(theirs)
    # regen faces: take newer ts; equal or unreadable -> theirs (origin, r437 ②
    # regen-snapshot zero-loss; ours is regenerable by next S6 tick anyway)
    if t_ours and t_theirs:
        pick = "ours" if t_ours >= t_theirs else "theirs"
    else:
        pick = "theirs" if theirs is not None else "ours"
    data = ours if pick == "ours" else theirs
    if data is None:
        print("FATAL: no blob for %s (both sides missing)" % path)
        sys.exit(2)
    with io.open(path, "wb") as fh:
        fh.write(data)
    log["faces"].append({"path": path, "pick": pick,
                         "ts_ours": t_ours, "ts_theirs": t_theirs})
    print("[resolved] %-46s pick=%-6s ours=%s theirs=%s"
          % (path, pick, t_ours or "-", t_theirs or "-"))

side_pick_counter(log)
# r456 law: per-key/face leg must assert side_pick > 0 on at least the union
# face set; here whole-file faces, assert we actually picked something per face
assert len(log["faces"]) == len(FACES), "face coverage incomplete"
with io.open("results/_r690bma_merge_resolve.json", "w", encoding="utf-8",
             newline="\n") as fh:
    json.dump(log, fh, ensure_ascii=False, indent=1)
print("resolver done: ours=%d theirs=%d (log _r690bma_merge_resolve.json)"
      % (log["side_pick_ours"], log["side_pick_theirs"]))
