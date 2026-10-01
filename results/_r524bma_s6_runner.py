# r524 bm-a: S6 maintenance chain, compact rc-per-leg runner.
# Lane guards honored (bm-a lanes act; bm-b/bm-c lanes honest no-op).
import subprocess
import sys

LEGS = [
    ("dualrun", [sys.executable, "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", [sys.executable, "scripts/compute_audit.py"]),
    ("watermark", [sys.executable, "scripts/py_watermark.py", "probe"]),
    ("update_daily", [sys.executable, "scripts/update_daily.py"]),
    ("regime", [sys.executable, "scripts/market_regime.py"]),
    ("scorecard", [sys.executable, "scripts/strategy_scorecard.py"]),
    ("clock_call", [sys.executable, "scripts/market_clock_call.py", "run"]),
    ("lhb", [sys.executable, "scripts/update_lhb.py"]),
    ("heat", [sys.executable, "scripts/update_heat.py"]),
    ("futures", [sys.executable, "scripts/update_futures.py"]),
    ("repo", [sys.executable, "scripts/update_repo.py"]),
    ("options", [sys.executable, "scripts/update_options.py"]),
    ("moneyflow", [sys.executable, "scripts/update_moneyflow.py"]),
    ("sina_mf", [sys.executable, "scripts/update_sina_mf.py"]),
    ("astock", [sys.executable, "scripts/update_astock_daily.py"]),      # bm-b lane
    ("etf_daily", [sys.executable, "scripts/update_etf_daily.py"]),       # bm-b lane
    ("rev_osc", [sys.executable, "scripts/rev_osc_signal_export.py", "run"]),  # bm-b lane
    ("minute_feed", [sys.executable, "scripts/update_minute_feed.py"]),   # bm-b lane
    ("ths_panel", [sys.executable, "scripts/update_ths_panel.py"]),
    ("ah_panel", [sys.executable, "scripts/ah_panel_puller.py"]),
    ("fund_prem", [sys.executable, "scripts/update_fund_premium.py", "snapshot"]),  # bm-c lane
    ("fundamental", [sys.executable, "scripts/update_fundamental.py"]),
    ("b_layer", [sys.executable, "-m", "firm.risk.b_layer_filter"]),
    ("aggr_paper", [sys.executable, "scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper", [sys.executable, "scripts/alloc_paper.py", "run"]),
    ("grid_paper", [sys.executable, "scripts/grid_paper.py", "run"]),
    ("sysv1_paper", [sys.executable, "scripts/system_v1_paper.py", "run"]),
    ("t35_export", [sys.executable, "scripts/t35_paper_export.py", "run"]),
    ("daily_score", [sys.executable, "scripts/daily_scorecard.py"]),
    ("daily_report", [sys.executable, "scripts/daily_report.py", "run"]),
    ("ceo_live", [sys.executable, "scripts/ceo_live_usage.py"]),
    ("build_status", [sys.executable, "-m", "monitor.build_status"]),
    ("token_meter", [sys.executable, "scripts/token_meter.py"]),
]

bad = []
for name, cmd in LEGS:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=600)
        rc = p.returncode
        tail = (p.stdout or "").strip().splitlines()[-1:] or [""]
        tail2 = (p.stderr or "").strip().splitlines()[-1:] or [""]
        print(f"[{name}] rc={rc} | {tail[0][:150]}")
        if rc not in (0,):
            print(f"         stderr-tail: {tail2[0][:150]}")
            bad.append((name, rc))
    except subprocess.TimeoutExpired:
        print(f"[{name}] TIMEOUT 600s")
        bad.append((name, "timeout"))
print("SUMMARY:", "ALL rc0" if not bad else f"NONZERO: {bad}")
