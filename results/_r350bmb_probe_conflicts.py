# -*- coding: utf-8 -*-
"""r350 S7 push-collision probe: both-side ts keys per UU file (bytes-safe, no PS redirect)."""
import subprocess, json

FILES = [
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/daily_report/REPORT-2026-09-28.md",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

def blob(side, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (side, path)], capture_output=True)
    return r.stdout

TS_KEYS = ["ts", "updated", "updated_at", "generated", "generated_at", "date", "now", "asof", "last_run", "time"]

for p in FILES:
    a, b = blob(2, p), blob(3, p)
    print("=" * 8, p, "ours=%dB theirs=%dB" % (len(a), len(b)))
    for side, raw in (("ours", a), ("theirs", b)):
        head = raw[:400].decode("utf-8", "replace").replace("\n", " ")[:200]
        print("  [%s] head: %s" % (side, head))
    # try JSON parse for ts-ish keys
    for side, raw in (("ours", a), ("theirs", b)):
        try:
            d = json.loads(raw.decode("utf-8-sig"))
            hits = {k: d[k] for k in TS_KEYS if isinstance(d, dict) and k in d}
            for k, v in list(hits.items()):
                hits[k] = str(v)[:40]
            extra = {}
            if isinstance(d, dict):
                for k in ("meta",):
                    if k in d and isinstance(d[k], dict):
                        extra = {kk: str(d[k][kk])[:40] for kk in d[k] if any(t in kk for t in TS_KEYS)}
            print("  [%s] ts-keys: %s %s" % (side, hits, extra))
        except Exception as e:
            print("  [%s] not-json: %s" % (side, type(e).__name__))
