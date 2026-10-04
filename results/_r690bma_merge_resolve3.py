# -*- coding: utf-8 -*-
"""r690 bm-a merge resolver leg-3: 13 S6 regen faces (bm-c r488 wave, ts
18:27:5x-18:28:0x), per-face ts-freshness (r440/r461 canon); LIVE md twins
aligned to their json pick (twin consistency)."""
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
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
]
TS_RE = re.compile(
    r'"(?:ts|generated|generated_at|asof|now|clock|clock_read|scan_ts|updated)"'
    r'\s*:\s*"?(\d{4}-\d{2}-\d{2})[ T]?(\d{2}:\d{2}:\d{2})')


def blob(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                       capture_output=True, creationflags=CREATE_NO_WINDOW)
    return r.stdout if r.returncode == 0 else None


def best_ts(b):
    if not b:
        return ""
    m = TS_RE.search(b.decode("utf-8", "replace"))
    return (m.group(1) + " " + m.group(2)) if m else ""


log = {"faces": [], "n": len(FACES)}
picks = {}
for path in FACES:
    ours, theirs = blob("HEAD", path), blob("MERGE_HEAD", path)
    t_o, t_t = best_ts(ours), best_ts(theirs)
    if t_o and t_t:
        pick = "ours" if t_o >= t_t else "theirs"
    else:
        pick = "theirs" if theirs is not None else "ours"
    picks[path] = pick
    log["faces"].append({"path": path, "pick": pick, "ts_ours": t_o,
                         "ts_theirs": t_t})
    print("[resolved] %-44s pick=%-6s ours=%s theirs=%s"
          % (path, pick, t_o or "-", t_t or "-"))

# twin consistency: LIVE-*.md follows LIVE-*.json pick (daily_report md/json too)
for md, js in [("docs/live_usage/LIVE-2026-10-04.md",
                "docs/live_usage/LIVE-2026-10-04.json"),
               ("docs/live_usage/LIVE-latest.md",
                "docs/live_usage/LIVE-latest.json"),
               ("docs/daily_report/REPORT-2026-10-04.md",
                "docs/daily_report/REPORT-2026-10-04.json")]:
    if picks.get(md) != picks.get(js):
        picks[md] = picks[js]
        for rec in log["faces"]:
            if rec["path"] == md:
                rec["pick"] = picks[js]
                rec["twin_aligned"] = True
        print("[twin-align] %s -> %s (follows json)" % (md, picks[js]))

for path in FACES:
    data = blob("HEAD", path) if picks[path] == "ours" else blob("MERGE_HEAD", path)
    if data is None:
        print("FATAL no blob:", path)
        sys.exit(2)
    # reparse proof for json faces (r645 tail-comma family guard)
    if path.endswith(".json"):
        json.loads(data.decode("utf-8", "replace"))
    with io.open(path, "wb") as fh:
        fh.write(data)

n_ours = sum(1 for p in picks.values() if p == "ours")
log["side_pick_ours"] = n_ours
log["side_pick_theirs"] = len(picks) - n_ours
assert log["side_pick_ours"] + log["side_pick_theirs"] == len(FACES)
with io.open("results/_r690bma_merge_resolve3.json", "w", encoding="utf-8",
             newline="\n") as fh:
    json.dump(log, fh, ensure_ascii=False, indent=1)
print("resolver leg-3 done: ours=%d theirs=%d" % (n_ours, len(picks) - n_ours))
