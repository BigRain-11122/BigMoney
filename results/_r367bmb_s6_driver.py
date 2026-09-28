"""r367 bm-b S6 maintenance-chain driver: run legs sequentially, print rc+tail per leg.
Monday 2026-09-28 pre-market, bars_present=false cutoff 09-24 -> paper-trigger legs (live.paper/t35_open_fill/t24 pair) lawful skip per bm-c r145 precedent (bm-b lineage).
Lane guards are in-script (host=bm-a/bm-c legs print honest no-op; bm-b lanes = astock_daily + rev_osc active)."""
import subprocess, sys

LEGS = [
 ("compute_audit",  [sys.executable,"scripts/compute_audit.py"]),
 ("py_watermark",   [sys.executable,"scripts/py_watermark.py","probe"]),
 ("update_daily",   [sys.executable,"scripts/update_daily.py"]),
 ("market_regime",  [sys.executable,"scripts/market_regime.py"]),
 ("scorecard",      [sys.executable,"scripts/strategy_scorecard.py"]),
 ("clock_call",     [sys.executable,"scripts/market_clock_call.py","run"]),
 ("lhb",            [sys.executable,"scripts/update_lhb.py"]),
 ("heat",           [sys.executable,"scripts/update_heat.py"]),
 ("futures",        [sys.executable,"scripts/update_futures.py"]),
 ("repo",           [sys.executable,"scripts/update_repo.py"]),
 ("options",        [sys.executable,"scripts/update_options.py"]),
 ("moneyflow",      [sys.executable,"scripts/update_moneyflow.py"]),
 ("sina_mf",        [sys.executable,"scripts/update_sina_mf.py"]),
 ("astock_daily",   [sys.executable,"scripts/update_astock_daily.py"]),
 ("rev_osc",        [sys.executable,"scripts/rev_osc_signal_export.py","run"]),
 ("ths_panel",      [sys.executable,"scripts/update_ths_panel.py"]),
 ("ah_panel",       [sys.executable,"scripts/ah_panel_puller.py"]),
 ("fund_premium",   [sys.executable,"scripts/update_fund_premium.py","snapshot"]),
 ("fundamental",    [sys.executable,"scripts/update_fundamental.py"]),
 ("b_layer",        [sys.executable,"-m","firm.risk.b_layer_filter"]),
 ("aggr_paper",     [sys.executable,"scripts/aggressive_lab.py","paper"]),
 ("alloc_paper",    [sys.executable,"scripts/alloc_paper.py","run"]),
 ("grid_paper",     [sys.executable,"scripts/grid_paper.py","run"]),
 ("sysv1_paper",    [sys.executable,"scripts/system_v1_paper.py","run"]),
 ("t35_export",     [sys.executable,"scripts/t35_paper_export.py","run"]),
 ("daily_scorecard",[sys.executable,"scripts/daily_scorecard.py"]),
 ("daily_report",   [sys.executable,"scripts/daily_report.py","run"]),
 ("build_status",   [sys.executable,"-m","monitor.build_status"]),
 ("token_meter",    [sys.executable,"scripts/token_meter.py"]),
]

rcs = {}
for name, cmd in LEGS:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900,
                       env=None, cwd=".")
    out = (r.stdout or "").strip().splitlines()
    tail = out[-1][:150] if out else (r.stderr or "").strip().splitlines()[-1][:150] if (r.stderr or "").strip() else ""
    rcs[name] = r.returncode
    print("%-15s rc=%d %s" % (name, r.returncode, tail))
bad = {k:v for k,v in rcs.items() if v not in (0,)}
print("S6 DRIVER SUMMARY: %d legs, nonzero=%r" % (len(LEGS), bad))
