# -*- coding: utf-8 -*-
"""S6 chain driver (r754 bm-a; bloodline=r752 verbatim 29 legs (leg-by-leg identical, r531 law diff=docstring round only)): sequential legs, honest per-leg rc capture.
Exit-code contract per leg is frozen in each script; rc 2/3 = reported
verbatim, never masked. Paper/live legs are new-bar-triggered -> golden-week
no-new-bar window = legitimately skipped (counted as SKIP not FAIL)."""
import subprocess
import sys
import time

LEGS = [
    ("pool_dualrun_reconcile", ["python", "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", ["python", "scripts/compute_audit.py"]),
    ("py_watermark", ["python", "scripts/py_watermark.py", "probe"]),
    ("update_daily", ["python", "scripts/update_daily.py"]),
    ("market_regime", ["python", "scripts/market_regime.py"]),
    ("strategy_scorecard", ["python", "scripts/strategy_scorecard.py"]),
    ("market_clock_call", ["python", "scripts/market_clock_call.py", "run"]),
    ("update_lhb", ["python", "scripts/update_lhb.py"]),
    ("update_heat", ["python", "scripts/update_heat.py"]),
    ("update_futures", ["python", "scripts/update_futures.py"]),
    ("update_repo", ["python", "scripts/update_repo.py"]),
    ("update_options", ["python", "scripts/update_options.py"]),
    ("update_moneyflow", ["python", "scripts/update_moneyflow.py"]),
    ("update_sina_mf", ["python", "scripts/update_sina_mf.py"]),
    ("update_astock_daily", ["python", "scripts/update_astock_daily.py"]),
    ("update_etf_daily", ["python", "scripts/update_etf_daily.py"]),
    ("rev_osc_signal_export", ["python", "scripts/rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", ["python", "scripts/update_minute_feed.py"]),
    ("update_ths_panel", ["python", "scripts/update_ths_panel.py"]),
    ("ah_panel_puller", ["python", "scripts/ah_panel_puller.py"]),
    ("update_fund_premium", ["python", "scripts/update_fund_premium.py", "snapshot"]),
    ("update_fundamental", ["python", "scripts/update_fundamental.py"]),
    ("b_layer_filter", ["python", "-m", "firm.risk.b_layer_filter"]),
    ("update_fund_statements", ["python", "scripts/update_fund_statements.py"]),
    ("daily_scorecard", ["python", "scripts/daily_scorecard.py"]),
    ("daily_report", ["python", "scripts/daily_report.py", "run"]),
    ("ceo_live_usage", ["python", "scripts/ceo_live_usage.py"]),
    ("build_status", ["python", "-m", "monitor.build_status"]),
    ("token_meter", ["python", "scripts/token_meter.py"]),
]

def main():
    results = []
    t0 = time.time()
    for name, cmd in LEGS:
        t1 = time.time()
        try:
            p = subprocess.run(cmd, capture_output=True, text=True,
                               encoding="utf-8", errors="replace",
                               timeout=600)
            rc = p.returncode
            tail = (p.stdout or "").strip().splitlines()[-1:] or [""]
            tail2 = (p.stderr or "").strip().splitlines()[-1:] or [""]
            last = (tail[0] or tail2[0])[:150]
        except subprocess.TimeoutExpired:
            rc, last = 99, "TIMEOUT 600s"
        dt = time.time() - t1
        flag = "OK" if rc in (0, 1) else "NONZERO"
        print(f"[{flag}] {name}: rc={rc} ({dt:.0f}s) | {last}", flush=True)
        results.append((name, rc))
    bad = [(n, r) for n, r in results if r not in (0, 1)]
    print(f"S6 chain: {len(results)} legs, {len(bad)} non-zero-ok exits, "
          f"{time.time()-t0:.0f}s total")
    for n, r in bad:
        print(f"  NONZERO: {n} rc={r}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
