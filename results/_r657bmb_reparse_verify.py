import json, os

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_FACES = [
    "results/compute_audit.json",
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
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
fail = 0
for p in JSON_FACES:
    fp = os.path.join(R, p)
    try:
        with open(fp, "rb") as f:
            raw = f.read()
        json.loads(raw.decode("utf-8"))
        assert b"<<<<<<<" not in raw and b"=======" not in raw and b">>>>>>>" not in raw, "marker residue"
        print("PASS %s (%d bytes)" % (p, len(raw)))
    except Exception as e:
        fail += 1
        print("FAIL %s: %s" % (p, e))
print("REPARSE_VERIFY fail=%d" % fail)
