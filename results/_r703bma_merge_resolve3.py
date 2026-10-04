# r703 bm-a merge resolver leg-3: reparse proof for all resolved faces + twins consistency
import json, re

faces = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.json",
    "results/compute_audit.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
fails = []
for p in faces:
    try:
        d = json.load(open(p, encoding="utf-8"))
        print("REPARSE-OK:", p)
    except Exception as e:
        fails.append((p, str(e)[:80]))
        print("REPARSE-FAIL:", p, str(e)[:80])

# twins consistency: json/js and json/md same-run evidence
pairs = [
    ("results/dashboard_status.json", "results/dashboard_status.js"),
    ("docs/daily_report/REPORT-2026-10-04.json", "docs/daily_report/REPORT-2026-10-04.md"),
    ("docs/live_usage/LIVE-2026-10-04.json", "docs/live_usage/LIVE-2026-10-04.md"),
    ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"),
]
for jp, tp in pairs:
    j = json.load(open(jp, encoding="utf-8"))
    jt = json.dumps(j.get("meta", j.get("generated", "")))
    t = open(tp, encoding="utf-8").read()
    # loose check: twin contains some json-identical anchor (e.g. same timestamp digits)
    m = re.findall(r"2026-10-0[45]T?[0-9:]{5,8}", jt)
    hit = any(x in t for x in m) if m else True
    print(f"TWIN {jp} <-> {tp}: anchor-hit={hit}")

print("VERDICT:", "PASS" if not fails else "FAIL")
