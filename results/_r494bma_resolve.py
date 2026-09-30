"""r494 bm-a rebase-conflict resolver (canon skill recipes, classifier 26+5).

Faces: 6 ALL_FACES via scripts/merge_lane_views.py resolve (禁手写 union);
twin-regen-md (daily_report + live_usage): json ts-probe decides side, md
byte-copies same side (r327/r329); js-wrapper couples to dashboard_status.json
side whole-byte (R209); snapshot ts-probe take-new staged blobs (r311 deep
probe, r100 normalize, R350 time-of-day, tie->HEAD r140); append-log x2 line
union (r188); strategy_scorecard host=bm-a writer note (r378).
"""
import json
import re
import subprocess
import sys

TS_RX = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")


def blob(stage, path):
    return subprocess.check_output(["git", "show", f":{stage}:{path}"])


def max_ts(b):
    ts = [m.group(0) for m in TS_RX.finditer(b.decode("utf-8", "replace"))]
    return max(ts) if ts else ""


def write(path, data):
    with open(path, "wb") as fh:
        fh.write(data)


def take_new(path):
    t2, t3 = max_ts(blob(2, path)), max_ts(blob(3, path))
    side = 3 if t3 > t2 else 2  # tie -> HEAD/origin side (r140)
    write(path, blob(side, path))
    json.loads(blob(side, path).decode("utf-8", "replace"))  # parse-verify
    return side, t2, t3


ALL_FACES = [
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/update_status.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
]
log = {"all_faces": {}, "snapshots": {}, "twins": {}, "append_log": {}}

for p in ALL_FACES:
    r = subprocess.run(
        [sys.executable, "scripts/merge_lane_views.py", "resolve", p],
        capture_output=True)
    out = (r.stdout + r.stderr).decode("utf-8", "replace").strip()
    log["all_faces"][p] = {"rc": r.returncode, "out": out[-200:]}
    print("ALLFACE", p, "rc=", r.returncode, out[-120:])

SNAPSHOTS = [
    "results/daily_scorecard.json",
    "results/fundamental_b_layer_filter.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/_attrition_guard_scan.json",
]
for p in SNAPSHOTS:
    side, t2, t3 = take_new(p)
    log["snapshots"][p] = {"side": side, "ts2": t2, "ts3": t3}
    print("SNAP", p, "side=", side, t2, "vs", t3)

# twin-regen-md: json decides, md byte-copies SAME side (r327/r329)
for twin_json, twin_md in [
    ("docs/daily_report/REPORT-2026-09-30.json",
     "docs/daily_report/REPORT-2026-09-30.md"),
    ("docs/live_usage/LIVE-2026-09-30.json",
     "docs/live_usage/LIVE-2026-09-30.md"),
    ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"),
]:
    side, t2, t3 = take_new(twin_json)
    write(twin_md, blob(side, twin_md))
    log["twins"][twin_json] = {"side": side, "md": twin_md, "ts2": t2, "ts3": t3}
    print("TWIN", twin_json, "side=", side, "md-copied", twin_md)

# js-wrapper couples to dashboard_status.json decision (R209 whole-byte)
side, t2, t3 = take_new("results/dashboard_status.json")
write("results/dashboard_status.js", blob(side, "results/dashboard_status.js"))
log["twins"]["results/dashboard_status.json"] = {
    "side": side, "js": "results/dashboard_status.js", "ts2": t2, "ts3": t3}
print("JS-COUPLE side=", side)

# append-log: line-level union zero loss (r188)
p = "results/x2_watch_log.jsonl"
l2 = blob(2, p).decode("utf-8", "replace").splitlines()
l3 = blob(3, p).decode("utf-8", "replace").splitlines()
seen, union = set(), []
for ln in l2 + l3:
    if ln not in seen:
        seen.add(ln)
        union.append(ln)
write(p, ("\n".join(union) + "\n").encode("utf-8"))
log["append_log"][p] = {"origin_lines": len(l2), "local_lines": len(l3),
                        "union_lines": len(union)}
print("X2UNION", len(l2), "+", len(l3), "->", len(union))

json.dump(log, open("results/_r494bma_resolve_log.json", "w",
                    encoding="utf-8"), ensure_ascii=False, indent=1)
print("resolver log -> results/_r494bma_resolve_log.json")
