# -*- coding: utf-8 -*-
"""R320 bm-b probe: ts fields of both rebase stages for each UU face."""
import re
import subprocess

UU = [
    "docs/daily_report/REPORT-2026-09-27.json",
    "docs/daily_report/REPORT-2026-09-27.md",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/autofill_state.json",
    "results/compute_audit.json",
    "results/regime_state.json",
]


def stage(p, n):
    r = subprocess.run(["git", "show", f":{n}:{p}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def ts_of(raw):
    if raw is None:
        return None
    t = raw.decode("utf-8-sig", errors="replace")
    m = re.search(
        r'"(?:ts|generated|generated_at|updated|asof)"\s*:\s*"?([0-9T:.\- +/]+)', t)
    return m.group(1)[:19] if m else "?"


for p in UU:
    a, b = stage(p, 2), stage(p, 3)
    print(f"{p}: origin(:2)={ts_of(a)} | mine(:3)={ts_of(b)}")
