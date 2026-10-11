# _r912bmc_s6_chain.py -- r912 bm-c S6 maintenance chain driver
# (r895 38-leg precedent reused verbatim; order per iteration-prompt S6 with
# pool_dualrun FIRST law; lane-guarded legs run and print their own
# honest no-op stdout; new-bar-gated legs SKIPPED with disclosed
# reason: last bar 2026-10-09 already processed, Sunday no new bar).
# Log = results/_r912bmc_s6_log.txt (human) + _r912bmc_s6_log.jsonl.

import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r912bmc_s6_log.txt")
LOGL = os.path.join(ROOT, "results", "_r912bmc_s6_log.jsonl")
PY = sys.executable

LEGS = [
    ("pool_dualrun", ["scripts/pool_dualrun_reconcile.py", "run"], 300),
    ("compute_audit", ["scripts/compute_audit.py"], 300),
    ("py_watermark", ["scripts/py_watermark.py", "probe"], 300),
    ("update_daily", ["scripts/update_daily.py"], 300),
    ("market_regime", ["scripts/market_regime.py"], 300),
    ("strategy_scorecard", ["scripts/strategy_scorecard.py"], 600),
    ("market_clock_call", ["scripts/market_clock_call.py", "run"], 300),
    ("update_lhb", ["scripts/update_lhb.py"], 300),
    ("update_zt_pool", ["scripts/update_zt_pool.py"], 300),
    ("update_heat", ["scripts/update_heat.py"], 300),
    ("update_futures", ["scripts/update_futures.py"], 300),
    ("update_repo", ["scripts/update_repo.py"], 300),
    ("update_options", ["scripts/update_options.py"], 300),
    ("update_moneyflow", ["scripts/update_moneyflow.py"], 300),
    ("update_sina_mf", ["scripts/update_sina_mf.py"], 300),
    ("update_astock_daily", ["scripts/update_astock_daily.py"], 300),
    ("update_etf_daily", ["scripts/update_etf_daily.py"], 300),
    ("regime_thermo_build", ["scripts/regime_thermo_build.py"], 300),
    ("regime_gate_dualarm", ["scripts/regime_gate_dualarm.py", "run"], 300),
    ("rev_osc_signal_export", ["scripts/rev_osc_signal_export.py", "run"], 300),
    ("update_minute_feed", ["scripts/update_minute_feed.py"], 300),
    ("update_ths_panel", ["scripts/update_ths_panel.py"], 300),
    ("ah_panel_puller", ["scripts/ah_panel_puller.py"], 300),
    ("update_fund_premium", ["scripts/update_fund_premium.py", "snapshot"], 300),
    ("update_fundamental", ["scripts/update_fundamental.py"], 300),
    ("b_layer_filter", ["-m", "firm.risk.b_layer_filter"], 300),
    ("update_fund_statements", ["scripts/update_fund_statements.py"], 300),
    ("aggressive_lab_paper", ["scripts/aggressive_lab.py", "paper"], 300),
    ("alloc_paper", ["scripts/alloc_paper.py", "run"], 300),
    ("grid_paper", ["scripts/grid_paper.py", "run"], 300),
    ("system_v1_paper", ["scripts/system_v1_paper.py", "run"], 300),
    ("t35_paper_export", ["scripts/t35_paper_export.py", "run"], 300),
    ("daily_scorecard", ["scripts/daily_scorecard.py"], 300),
    ("daily_report", ["scripts/daily_report.py", "run"], 300),
    ("ceo_live_usage", ["scripts/ceo_live_usage.py"], 300),
    ("build_status", ["-m", "monitor.build_status"], 300),
    ("token_meter", ["scripts/token_meter.py"], 300),
    ("queue_seed_gate_scan", ["scripts/queue_seed_gate.py", "scan"], 300),
]

SKIPPED = [
    ("live_paper", "no new bar (Friday 2026-10-09 processed; Monday pre-market 05:5x, new bar 15:30 today)"),
    ("t35_open_fill_verify", "same trigger: no new bar"),
    ("t24_prospect_paper", "same trigger: no new bar"),
    ("t24_prospect_promotion", "same trigger: no new bar"),
    ("science_audit", "monthly first-round leg; 10-12 is not month-first"),
    ("monthly_briefing", "monthly first-round leg"),
    ("self_review", "monthly first-round leg"),
]


def main():
    rows = []
    n_ok = 0
    n_bad = 0
    with open(LOG, "w", encoding="utf-8") as lh, \
            open(LOGL, "w", encoding="utf-8") as jl:
        lh.write("r912 bm-c S6 chain start %s\n"
                 % time.strftime("%Y-%m-%d %H:%M:%S"))
        for name, args, tmo in LEGS:
            t0 = time.time()
            try:
                p = subprocess.run([PY] + args, capture_output=True,
                                  text=True, timeout=tmo, cwd=ROOT,
                                  encoding="utf-8", errors="replace")
                rc = p.returncode
                out = ((p.stdout or "") + (p.stderr or "")).strip()
            except subprocess.TimeoutExpired:
                rc = -9
                out = "TIMEOUT after %ss" % tmo
            tail = out.splitlines()[-1][:200] if out else ""
            dt = round(time.time() - t0, 1)
            bad = rc not in (0,)
            n_bad += 1 if bad else 0
            n_ok += 0 if bad else 1
            lh.write("%-22s rc=%-3s %6.1fs %s\n" % (name, rc, dt, tail))
            lh.flush()
            jl.write(json.dumps({"leg": name, "rc": rc, "sec": dt,
                                 "tail": tail}) + "\n")
            jl.flush()
            print("%s rc=%s %.1fs" % (name, rc, dt), flush=True)
        for name, why in SKIPPED:
            lh.write("%-22s SKIP  %s\n" % (name, why))
            jl.write(json.dumps({"leg": name, "rc": "SKIP",
                                 "why": why}) + "\n")
        lh.write("SUMMARY ok=%d bad=%d skipped=%d\n"
                 % (n_ok, n_bad, len(SKIPPED)))
    print("SUMMARY ok=%d bad=%d skipped=%d" % (n_ok, n_bad, len(SKIPPED)))
    return 0 if n_bad == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
