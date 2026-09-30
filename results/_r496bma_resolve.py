# r496 bm-a rebase collision resolver (adoption commit 4b21be39d vs origin bm-c r294 S6 faces)
# Canon: bigmoney-conflict-resolve SKILL. Classifier: 17 classified + 7 UNKNOWN (monthly trio + crash_fuse).
# Resolution table (evidence logged to _log.json):
#  - ALL_FACES 7 (compute_audit/regime_state/update_status/lhb/futures/token_usage/crash_fuse): merge_lane_views resolve (done separately)
#  - snapshot twins (origin newer everywhere: bm-c r294 00:30-00:35 > local r496 00:21-00:22):
#      daily_report REPORT-2026-10-01 json+md, live_usage LIVE-2026-10-01 json+md + LIVE-latest json+md,
#      dashboard_status.json + dashboard_status.js (js = whole-byte take, no re-serialize),
#      fundamental_b_layer_filter.json, scorecard_v1.json, strategy_scorecard.json,
#      briefing_status.json + BRIEF-202609.md, SELF-REVIEW-202609.json + .md  -> take :2 (origin)
#  - science_audit.json: history union by 'generated' key (both machine runs kept), current from :2 (newest)
#  - self_review_ledger.json: same-month idempotent regen face -> take :2 (newest regen 00:35:38 vs 00:22:55)
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def blob(stage_n, path):
    return subprocess.check_output(["git", "show", f":{stage_n}:{path}"])


def write(path, data):
    fp = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    mode = "wb" if isinstance(data, bytes) else "w"
    with open(fp, mode, **({} if mode == "wb" else {"encoding": "utf-8", "newline": ""})) as f:
        f.write(data)


TAKE_ORIGIN = [
    "docs/daily_report/REPORT-2026-10-01.json",
    "docs/daily_report/REPORT-2026-10-01.md",
    "docs/live_usage/LIVE-2026-10-01.json",
    "docs/live_usage/LIVE-2026-10-01.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/fundamental_b_layer_filter.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/briefings/briefing_status.json",
    "results/briefings/BRIEF-202609.md",
    "results/self_review/SELF-REVIEW-202609.json",
    "results/self_review/SELF-REVIEW-202609.md",
    "results/self_review/self_review_ledger.json",
]

log = {"take_origin": [], "union": {}, "skipped": []}
for p in TAKE_ORIGIN:
    b = blob(2, p)
    write(p, b)
    log["take_origin"].append(p)

# science_audit.json: history union by 'generated' key; current from :2
sa_o = json.loads(blob(2, "results/science_audit.json").decode("utf-8"))
sa_t = json.loads(blob(3, "results/science_audit.json").decode("utf-8"))
key = lambda r: r.get("generated")
by = {}
for r in sa_t["history"]:
    by[key(r)] = r
for r in sa_o["history"]:
    k = key(r)
    if k in by and json.dumps(by[k], sort_keys=True) != json.dumps(r, sort_keys=True):
        log["union"].setdefault("science_audit_key_collisions", []).append(k)
    by[k] = r  # origin wins on same-key content divergence (state face)
merged = sa_o.copy()
merged["history"] = [by[k] for k in sorted(by.keys())]
log["union"]["science_audit"] = {
    "origin_rows": len(sa_o["history"]),
    "local_rows": len(sa_t["history"]),
    "union_rows": len(merged["history"]),
    "current_side": "origin",
}
write("results/science_audit.json", json.dumps(merged, ensure_ascii=False, indent=2))
json.loads(open(os.path.join(ROOT, "results/science_audit.json"), encoding="utf-8").read())

# parse-verify all resolved json files
for p in TAKE_ORIGIN + ["results/science_audit.json"]:
    if p.endswith(".json"):
        json.loads(open(os.path.join(ROOT, p), encoding="utf-8").read())

write("results/_r496bma_resolve_log.json", json.dumps(log, ensure_ascii=False, indent=2))
print(json.dumps(log["union"], ensure_ascii=False))
print("resolver done: %d take-origin, science_audit union, parse-verified" % len(TAKE_ORIGIN))
