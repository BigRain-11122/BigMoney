"""r456 bm-c S6 chain driver: 38 standing legs (canon Tools/_r433bmc_s6.py
byte-equivalent leg list, parity-checked at start), full log to
results/_r456bmc_s6_log.txt. Per-round file form (r442-r455 lineage): canon
Tools driver untouched, zero adapt->restore surgery needed. env identical to
r450 live run (enforce flag + PYTHONUTF8=1 r425 fix). Golden-week no-new-bar
face (last bar 2026-09-30): new-bar legs no-op/veto honestly per r448 caliber."""
import datetime
import importlib.util
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r456bmc_s6_log.txt")
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
    ("update_fund_statements", [PY, "scripts/update_fund_statements.py"]),
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


def parity_check():
    spec = importlib.util.spec_from_file_location(
        "canon_s6", os.path.join(ROOT, "Tools", "_r433bmc_s6.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    canon = [(n, a[1:]) for n, a in mod.LEGS]  # strip canon PY placeholder
    mine = [(n, a[1:]) for n, a in LEGS]
    assert canon == mine, "PARITY FAIL vs canon Tools/_r433bmc_s6.py"
    return len(LEGS)


def main():
    n = parity_check()
    print(f"PARITY PASS {n} legs == canon", flush=True)
    env = dict(os.environ)
    env["BIGMONEY_REGIME_GUARD"] = "enforce"   # r450 live-proven env face
    env["PYTHONUTF8"] = "1"   # r425 leg-8 GBK console crash fix, persisted
    bad = []
    with open(LOG, "w", encoding="utf-8") as log:
        log.write(f"S6 chain r456 bm-c start {datetime.datetime.now().isoformat()}\n")
        log.flush()
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
            if rc != 0:
                bad.append((name, rc))
            tail = out.strip().splitlines()[-3:] if out.strip() else ["(no output)"]
            log.write(f"\n=== {name} rc={rc} {dt:.1f}s\n{out}\n")
            log.flush()
            print(f"{name}: rc={rc} ({dt:.0f}s) | {' | '.join(tail)[:150]}", flush=True)
        log.write(f"\nS6 chain end {datetime.datetime.now().isoformat()} "
                  f"bad={bad}\n")
    print(f"\nNON-ZERO LEGS: {bad if bad else 'none'}")


if __name__ == "__main__":
    main()
