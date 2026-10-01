"""r534 bm-a S6 chain driver: 38 standing legs, full log to
results/_r534bma_s6_log.txt, compact per-leg rc summary to stdout.
Pattern credit: Tools/_r483bmb_s6.py (bm-b r483)."""
import datetime
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r534bma_s6_log.txt")
PY = sys.executable

LEGS = [
    ("pool_dualrun_reconcile", [PY, "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", [PY, "scripts/compute_audit.py"]),
    ("py_watermark", [PY, "scripts/py_watermark.py", "probe"]),
    ("update_daily", [PY, "scripts/update_daily.py"]),
    ("market_regime", [PY, "scripts/market_regime.py"]),
    ("strategy_scorecard", [PY, "scripts/strategy_scorecard.py"]),
    ("market_clock_call", [PY, "scripts/market_clock_call.py", "run"]),
    ("update_lhb", [PY, "scripts/update_lhb.py"]),
    ("update_heat", [PY, "scripts/update_heat.py"]),
    ("update_futures", [PY, "scripts/update_futures.py"]),
    ("update_repo", [PY, "scripts/update_repo.py"]),
    ("update_options", [PY, "scripts/update_options.py"]),
    ("update_moneyflow", [PY, "scripts/update_moneyflow.py"]),
    ("update_sina_mf", [PY, "scripts/update_sina_mf.py"]),
    ("update_astock_daily", [PY, "scripts/update_astock_daily.py"]),
    ("update_etf_daily", [PY, "scripts/update_etf_daily.py"]),
    ("rev_osc_signal_export", [PY, "scripts/rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", [PY, "scripts/update_minute_feed.py"]),
    ("update_ths_panel", [PY, "scripts/update_ths_panel.py"]),
    ("ah_panel_puller", [PY, "scripts/ah_panel_puller.py"]),
    ("update_fund_premium", [PY, "scripts/update_fund_premium.py", "snapshot"]),
    ("update_fundamental", [PY, "scripts/update_fundamental.py"]),
    ("b_layer_filter", [PY, "-m", "firm.risk.b_layer_filter"]),
    ("live_paper", [PY, "-m", "live.paper"]),
    ("t35_open_fill_verify", [PY, "scripts/t35_open_fill_verify.py"]),
    ("t24_prospect_paper", [PY, "scripts/t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", [PY, "scripts/t24_prospect_promotion.py", "run"]),
    ("aggressive_lab", [PY, "scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper", [PY, "scripts/alloc_paper.py", "run"]),
    ("grid_paper", [PY, "scripts/grid_paper.py", "run"]),
    ("system_v1_paper", [PY, "scripts/system_v1_paper.py", "run"]),
    ("t35_paper_export", [PY, "scripts/t35_paper_export.py", "run"]),
    ("daily_scorecard", [PY, "scripts/daily_scorecard.py"]),
    ("daily_report", [PY, "scripts/daily_report.py", "run"]),
    ("ceo_live_usage", [PY, "scripts/ceo_live_usage.py"]),
    ("build_status", [PY, "-m", "monitor.build_status"]),
    ("token_meter", [PY, "scripts/token_meter.py"]),
]


def main():
    env = dict(os.environ)
    env["BIGMONEY_REGIME_GUARD"] = "enforce"   # 10-01 date gate open -> v3 live request
    env["PYTHONIOENCODING"] = "utf-8"
    bad = []
    with open(LOG, "w", encoding="utf-8") as log:
        log.write(f"S6 chain r534 bm-a start {datetime.datetime.now().isoformat()}\n")
        for name, args in LEGS:
            t0 = datetime.datetime.now()
            try:
                r = subprocess.run(args, cwd=ROOT, env=env, capture_output=True,
                                   text=True, encoding="utf-8", errors="replace",
                                   timeout=600)
                rc = r.returncode
                out = (r.stdout or "") + (r.stderr or "")
            except subprocess.TimeoutExpired:
                rc, out = 99, "TIMEOUT 600s"
            dt = (datetime.datetime.now() - t0).total_seconds()
            tail = out.strip().splitlines()[-3:] if out.strip() else ["(no output)"]
            log.write(f"\n=== {name} rc={rc} {dt:.1f}s\n{out}\n")
            print(f"{name}: rc={rc} ({dt:.0f}s) | {' | '.join(tail)[:150]}")
            if rc != 0:
                bad.append((name, rc))
        log.write(f"\nS6 chain end {datetime.datetime.now().isoformat()} "
                  f"bad={bad}\n")
    print(f"\nNON-ZERO LEGS: {bad if bad else 'none'}")


if __name__ == "__main__":
    main()
