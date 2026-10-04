# -*- coding: utf-8 -*-
# r656 bm-b merge resolver v2: 19 UU faces of the origin r452 wave merge
# (same recipes as _r656bmb_merge_resolve.py; post_review pair auto-merged
# this round and is zero-loss-verified separately, not re-resolved here).
TOOL_FACES = [
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
    "results/token_usage.json",
]
SNAP_JSON = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/update_status.json",
]
TWIN_OF = {
    "docs/daily_report/REPORT-2026-10-04.md": "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md": "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}
JSONL_UNION = []
OWN_PROBE_MD = []

exec(open("results/_r656bmb_merge_resolve.py", encoding="utf-8").read()
     .replace("JSONL_UNION = [\"results/post_review.jsonl\"]", "JSONL_UNION = []")
     .replace("OWN_PROBE_MD = [\"results/post_review/REPORT-20261004.md\"]", "OWN_PROBE_MD = []"))
