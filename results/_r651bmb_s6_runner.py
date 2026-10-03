# -*- coding: utf-8 -*-
# r651 bm-b S6 chain driver (r650 lineage recipe; EVID path bm-b)
import subprocess, sys, os, datetime, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

EVID = os.path.join("results", "_r651bmb_s6_evidence.txt")
PY = sys.executable

def tail(s, n=3):
    ls = [l for l in (s or "").strip().split("\n") if l.strip()]
    return " | ".join(ls[-n:])[:220]

def run_leg(name, args, timeout=240):
    try:
        r = subprocess.run([PY] + args, capture_output=True, encoding="utf-8",
                           errors="replace", timeout=timeout, cwd=os.getcwd())
        rc, out = r.returncode, (r.stdout or "") + (r.stderr or "")
        line = "[%s] %s rc=%d :: %s" % (datetime.datetime.now().strftime("%H:%M:%S"), name, rc, tail(out))
    except subprocess.TimeoutExpired:
        rc, line = 3, "[%s] %s rc=3 TIMEOUT" % (datetime.datetime.now().strftime("%H:%M:%S"), name)
    print(line)
    with open(EVID, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    return rc

LEGS = [
    ("dualrun", ["scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", ["scripts/compute_audit.py"]),
    ("py_watermark", ["scripts/py_watermark.py", "probe"]),
    ("update_daily", ["scripts/update_daily.py"]),
    ("market_regime", ["scripts/market_regime.py"]),
    ("strategy_scorecard", ["scripts/strategy_scorecard.py"]),
    ("market_clock_call", ["scripts/market_clock_call.py", "run"]),
    ("update_lhb", ["scripts/update_lhb.py"]),
    ("update_heat", ["scripts/update_heat.py"]),
    ("update_futures", ["scripts/update_futures.py"]),
    ("update_repo", ["scripts/update_repo.py"]),
    ("update_options", ["scripts/update_options.py"]),
    ("update_moneyflow", ["scripts/update_moneyflow.py"]),
    ("update_sina_mf", ["scripts/update_sina_mf.py"]),
    ("update_astock_daily", ["scripts/update_astock_daily.py"]),
    ("update_etf_daily", ["scripts/update_etf_daily.py"]),
    ("rev_osc_signal_export", ["scripts/rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", ["scripts/update_minute_feed.py"]),
    ("update_ths_panel", ["scripts/update_ths_panel.py"]),
    ("ah_panel_puller", ["scripts/ah_panel_puller.py"]),
    ("update_fund_premium", ["scripts/update_fund_premium.py", "snapshot"]),
    ("update_fundamental", ["scripts/update_fundamental.py"]),
    ("b_layer_filter", ["-m", "firm.risk.b_layer_filter"]),
    ("t24_prospect_promotion", ["scripts/t24_prospect_promotion.py", "run"]),
    ("aggressive_lab", ["scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper", ["scripts/alloc_paper.py", "run"]),
    ("grid_paper", ["scripts/grid_paper.py", "run"]),
    ("system_v1_paper", ["scripts/system_v1_paper.py", "run"]),
    ("t35_paper_export", ["scripts/t35_paper_export.py", "run"]),
    ("daily_scorecard", ["scripts/daily_scorecard.py"]),
    ("daily_report", ["scripts/daily_report.py", "run"]),
    ("ceo_live_usage", ["scripts/ceo_live_usage.py"]),
    ("build_status", ["-m", "monitor.build_status"]),
    ("token_meter", ["scripts/token_meter.py"]),
]

fails = 0
with open(EVID, "a", encoding="utf-8") as f:
    f.write("=== r651 bm-b S6 chain %s ===\n" % datetime.datetime.now().isoformat())

def latest_bar_date():
    try:
        import csv
        p = os.path.join("data", "daily", "sh510300.csv")
        with open(p, encoding="utf-8") as f:
            rows = list(csv.reader(f))
        return rows[-1][0] if rows else "?"
    except Exception as e:
        return "ERR:" + str(e)[:60]

today = datetime.date.today().isoformat()
bar = latest_bar_date()
print("latest 510300 bar:", bar, "| today:", today)
new_bar = (bar == today)
if new_bar:
    os.environ["BIGMONEY_REGIME_GUARD"] = "enforce"
    for nm, args in [("live.paper", ["-m", "live.paper"]),
                     ("t35_open_fill_verify", ["scripts/t35_open_fill_verify.py"]),
                     ("t24_prospect_paper", ["scripts/t24_prospect_paper.py", "run"])]:
        fails += 1 if run_leg(nm, args) not in (0,) else 0
else:
    print("[conditional] live.paper/t35_open_fill_verify/t24_prospect_paper SKIPPED (no new bar; latest=%s)" % bar)
    with open(EVID, "a", encoding="utf-8") as f:
        f.write("conditional trio skipped: no new bar (latest=%s)\n" % bar)

for name, args in LEGS:
    rc = run_leg(name, args)
    if rc != 0:
        fails += 1
print("S6 chain done: %d legs, nonzero_rc=%d" % (len(LEGS) + (3 if new_bar else 0), fails))
sys.exit(1 if fails else 0)
