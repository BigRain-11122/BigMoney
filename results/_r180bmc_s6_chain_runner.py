# r180 bm-c S6 chain (31 legs, r179 isomorphic; lane-guarded legs self-no-op for bm-c)
import json, subprocess, sys

legs = [
    ("compute_audit",      [sys.executable, "scripts/compute_audit.py"]),
    ("watermark_probe",    [sys.executable, "scripts/py_watermark.py", "probe"]),
    ("update_daily",       [sys.executable, "scripts/update_daily.py"]),
    ("market_regime",      [sys.executable, "scripts/market_regime.py"]),
    ("scorecard",          [sys.executable, "scripts/strategy_scorecard.py"]),
    ("market_clock_call",  [sys.executable, "scripts/market_clock_call.py", "run"]),
    ("update_lhb",         [sys.executable, "scripts/update_lhb.py"]),
    ("update_heat",        [sys.executable, "scripts/update_heat.py"]),
    ("update_futures",     [sys.executable, "scripts/update_futures.py"]),
    ("update_repo",        [sys.executable, "scripts/update_repo.py"]),
    ("update_options",     [sys.executable, "scripts/update_options.py"]),
    ("update_moneyflow",   [sys.executable, "scripts/update_moneyflow.py"]),
    ("update_sina_mf",     [sys.executable, "scripts/update_sina_mf.py"]),
    ("update_astock_daily",[sys.executable, "scripts/update_astock_daily.py"]),
    ("rev_osc_signal",     [sys.executable, "scripts/rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", [sys.executable, "scripts/update_minute_feed.py"]),
    ("update_ths_panel",   [sys.executable, "scripts/update_ths_panel.py"]),
    ("ah_panel",          [sys.executable, "scripts/ah_panel_puller.py"]),
    ("fund_premium",       [sys.executable, "scripts/update_fund_premium.py", "snapshot"]),
    ("fundamental",        [sys.executable, "scripts/update_fundamental.py"]),
    ("b_layer_filter",     [sys.executable, "-m", "firm.risk.b_layer_filter"]),
    ("aggr_paper",         [sys.executable, "scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper",        [sys.executable, "scripts/alloc_paper.py", "run"]),
    ("grid_paper",         [sys.executable, "scripts/grid_paper.py", "run"]),
    ("system_v1_paper",    [sys.executable, "scripts/system_v1_paper.py", "run"]),
    ("t35_paper_export",   [sys.executable, "scripts/t35_paper_export.py", "run"]),
    ("daily_scorecard",    [sys.executable, "scripts/daily_scorecard.py"]),
    ("daily_report",       [sys.executable, "scripts/daily_report.py", "run"]),
    ("ceo_live_usage",     [sys.executable, "scripts/ceo_live_usage.py"]),
    ("build_status",       [sys.executable, "-m", "monitor.build_status"]),
    ("token_meter",        [sys.executable, "scripts/token_meter.py"]),
]

out = {"round": 180, "machine": "bm-c", "legs": []}
fails = []
for name, cmd in legs:
    try:
        rc = subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        rc = 99
    out["legs"].append({"leg": name, "rc": rc})
    if rc != 0:
        fails.append((name, rc))
    print(f"{name}: rc={rc}", flush=True)

with open("results/_r180bmc_s6_chain.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print("FAILS:", fails if fails else "none")
