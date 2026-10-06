# -*- coding: utf-8 -*-
"""S6 chain driver (r790 bm-a; bloodline = r788 verbatim 38 legs; W162 finalize round;
W162 freeze+ignition round). Sequential legs, honest per-leg rc capture.
Exit-code contract per leg frozen in each script; rc 2/3 reported verbatim,
never masked. Paper/live legs new-bar-triggered -> golden-week no-new-bar
window = legitimately skipped (SKIP not FAIL)."""
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
        except subprocess.TimeoutExpired:
            rc, tail = 124, ["TIMEOUT 600s"]
        results.append((name, rc, tail[-1][:120], round(time.time() - t1, 1)))
        print(f"[{rc}] {name} ({results[-1][3]}s) {tail[-1][:120]}", flush=True)
    dt = round(time.time() - t0, 1)
    bad = [(n, rc, tl) for n, rc, tl, _ in results if rc not in (0, 3)]
    # rc 3 (no-new-bar/skip family on some legs) is honest-skip per contract
    import json
    facts = {"round": 790, "machine": "bm-a", "legs": len(results),
             "elapsed_sec": dt, "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
             "bad": bad, "results": [
                 {"leg": n, "rc": rc, "tail": tl, "sec": s} for n, rc, tl, s in results]}
    open("results/_r790bma_s6_facts.json", "w", encoding="utf-8").write(
        json.dumps(facts, ensure_ascii=False, indent=1))
    print(f"--- S6 chain done in {dt}s: {len(results)} legs, "
          f"rc0={sum(1 for _,r,_,_ in results if r==0)}, bad={len(bad)} ---")


if __name__ == "__main__":
    main()
