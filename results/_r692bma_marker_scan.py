# r692 marker scan + json reparse proof on all 20 resolved faces
import json, io, re

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
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/runnable_pool.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
bad = []
for p in FACES:
    b = open(p, "rb").read()
    # conflict-marker scan: line-anchored (not substring -- r685 law)
    for ln in b.split(b"\n"):
        if (ln.startswith(b"<<<<<<<") or ln.startswith(b">>>>>>>")
                or ln.startswith(b"=======") and len(ln) <= 10):
            bad.append((p, "marker", ln[:40]))
            break
    if p.endswith(".json"):
        try:
            json.loads(b.decode("utf-8"))
        except Exception as e:
            bad.append((p, "reparse", repr(e)[:60]))
print("faces scanned:", len(FACES), "bad:", len(bad))
for x in bad:
    print("  ", x)
assert not bad, "marker/reparse failures present"
print("MARKER SCAN + REPARSE ALL PASS")
