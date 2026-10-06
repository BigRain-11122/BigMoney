# -*- coding: utf-8 -*-
"""S6 chain driver (r764 bm-a; bloodline=r756 verbatim 29 legs + the 9
new-bar-triggered paper/live legs per the round-spec chain): sequential
legs, honest per-leg rc capture.
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
    ("live_paper", ["python", "-m", "live.paper"]),
    ("t35_open_fill_verify", ["python", "scripts/t35_open_fill_verify.py"]),
    ("t24_prospect_paper", ["python", "scripts/t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", ["python", "scripts/t24_prospect_promotion.py", "run"]),
    ("aggressive_lab", ["python", "scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper", ["python", "scripts/alloc_paper.py", "run"]),
    ("grid_paper", ["python", "scripts/grid_paper.py", "run"]),
    ("system_v1_paper", ["python", "scripts/system_v1_paper.py", "run"]),
    ("t35_paper_export", ["python", "scripts/t35_paper_export.py", "run"]),
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
            tailerr = (p.stderr or "").strip().splitlines()[-1:] or [""]
        except subprocess.TimeoutExpired:
            rc = 99
            tail = ["TIMEOUT 600s"]
            tailerr = [""]
        dt = time.time() - t1
        results.append((name, rc, dt, tail[0][:160], tailerr[0][:160]))
        print(f"[{name}] rc={rc} {dt:.1f}s :: {tail[0][:140]}")
        sys.stdout.flush()
    fails = [(n, rc) for n, rc, *_ in results if rc not in (0,)]
    print(f"\nS6 chain summary: {len(results)} legs, "
          f"{sum(1 for _, rc, *_ in results if rc == 0)} rc0, "
          f"{len(fails)} non-zero: {fails}")
    print(f"total {time.time() - t0:.1f}s")
    import json
    json.dump([{"leg": n, "rc": rc, "sec": round(dt, 1), "tail": t, "err": e}
               for n, rc, dt, t, e in results],
              open("results/_r764bma_s6_facts.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
