# r593 bm-b: S6 maintenance chain driver (python argv subprocess per r580
# law; PS loop-runner pitfalls avoided). Prints one line per leg:
# rc + last stdout line. Exit-code contracts (2/3) surface honestly.
import subprocess, sys

PY = sys.executable
LEGS = [
    ("dualrun",    ["scripts/pool_dualrun_reconcile.py", "run"]),
    ("computeaudit", ["scripts/compute_audit.py"]),
    ("watermark",  ["scripts/py_watermark.py", "probe"]),
    ("daily",      ["scripts/update_daily.py"]),
    ("regime",     ["scripts/market_regime.py"]),
    ("scorecard",  ["scripts/strategy_scorecard.py"]),
    ("clockcall",  ["scripts/market_clock_call.py", "run"]),
    ("lhb",        ["scripts/update_lhb.py"]),
    ("heat",       ["scripts/update_heat.py"]),
    ("futures",    ["scripts/update_futures.py"]),
    ("repo",       ["scripts/update_repo.py"]),
    ("options",    ["scripts/update_options.py"]),
    ("moneyflow",  ["scripts/update_moneyflow.py"]),
    ("sinamf",     ["scripts/update_sina_mf.py"]),
    ("astock",     ["scripts/update_astock_daily.py"]),
    ("etf",        ["scripts/update_etf_daily.py"]),
    ("revosc",     ["scripts/rev_osc_signal_export.py", "run"]),
    ("minutefeed", ["scripts/update_minute_feed.py"]),
    ("ths",        ["scripts/update_ths_panel.py"]),
    ("ahpanel",    ["scripts/ah_panel_puller.py"]),
    ("fundprem",   ["scripts/update_fund_premium.py", "snapshot"]),
    ("fundamental", ["scripts/update_fundamental.py"]),
    ("blayer",     ["-m", "firm.risk.b_layer_filter"]),
    ("prosppromo", ["scripts/t24_prospect_promotion.py", "run"]),
    ("aggrpaper",  ["scripts/aggressive_lab.py", "paper"]),
    ("allocpaper", ["scripts/alloc_paper.py", "run"]),
    ("gridpaper",  ["scripts/grid_paper.py", "run"]),
    ("sysv1",      ["scripts/system_v1_paper.py", "run"]),
    ("t35export",  ["scripts/t35_paper_export.py", "run"]),
    ("dscorecard", ["scripts/daily_scorecard.py"]),
    ("dreport",    ["scripts/daily_report.py", "run"]),
    ("liveusage",  ["scripts/ceo_live_usage.py"]),
    ("buildstat",  ["-m", "monitor.build_status"]),
    ("token",      ["scripts/token_meter.py"]),
    ("attrition",  ["scripts/attrition_ledger_guard.py", "scan"]),
]

fails = []
for name, args in LEGS:
    try:
        r = subprocess.run([PY] + args, capture_output=True, timeout=600,
                            encoding="utf-8", errors="replace")
        rc = r.returncode
        out = (r.stdout or "").strip().splitlines()
        last = out[-1][:150] if out else (r.stderr or "").strip()[:150]
    except subprocess.TimeoutExpired:
        rc, last = "TIMEOUT", ">600s"
    print(f"[{name}] rc={rc} :: {last}")
    if rc not in (0,):
        fails.append((name, rc, last))

print(f"LEGS={len(LEGS)} NONZERO={len(fails)}")
for f in fails:
    print("NONZERO:", f[0], "rc=", f[1], "::", f[2][:200])
