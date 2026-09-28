# -*- coding: utf-8 -*-
"""r389 bm-b S6 maintenance-chain driver: runs the standing chain legs
sequentially, logs rc + tail line per leg to results/_r389bmb_s6.log
(UTF-8, no PS redirection encoding traps per r209 law). Pre-15:30 Monday
(no new bar yet; next bar = today 15:30): collectors no-op / gate-honest.
live.paper trio included per r384 precedent (anchor verify + REGIME_GUARD
enforce request -> date-gate 2026-10-01 honest shadow downgrade).
r385 paradigm zero-rewrite; bm-a stale -> lane_io auto stale-takeover."""
import io
import os
import subprocess
import sys
import time

LEGS = [
    ("compute_audit", [sys.executable, "scripts/compute_audit.py"], None),
    ("py_watermark_probe", [sys.executable, "scripts/py_watermark.py", "probe"], None),
    ("update_daily", [sys.executable, "scripts/update_daily.py"], None),
    ("market_regime", [sys.executable, "scripts/market_regime.py"], None),
    ("strategy_scorecard", [sys.executable, "scripts/strategy_scorecard.py"], None),
    ("market_clock_call", [sys.executable, "scripts/market_clock_call.py", "run"], None),
    ("update_lhb", [sys.executable, "scripts/update_lhb.py"], None),
    ("update_heat", [sys.executable, "scripts/update_heat.py"], None),
    ("update_futures", [sys.executable, "scripts/update_futures.py"], None),
    ("update_repo", [sys.executable, "scripts/update_repo.py"], None),
    ("update_options", [sys.executable, "scripts/update_options.py"], None),
    ("update_moneyflow", [sys.executable, "scripts/update_moneyflow.py"], None),
    ("update_sina_mf", [sys.executable, "scripts/update_sina_mf.py"], None),
    ("update_astock_daily", [sys.executable, "scripts/update_astock_daily.py"], None),
    ("rev_osc_signal_export", [sys.executable, "scripts/rev_osc_signal_export.py", "run"], None),
    ("update_ths_panel", [sys.executable, "scripts/update_ths_panel.py"], None),
    ("ah_panel_puller", [sys.executable, "scripts/ah_panel_puller.py"], None),
    ("update_fund_premium", [sys.executable, "scripts/update_fund_premium.py", "snapshot"], None),
    ("update_fundamental", [sys.executable, "scripts/update_fundamental.py"], None),
    ("b_layer_filter", [sys.executable, "-m", "firm.risk.b_layer_filter"], None),
    ("live_paper", [sys.executable, "-m", "live.paper"], {"BIGMONEY_REGIME_GUARD": "enforce"}),
    ("t35_open_fill_verify", [sys.executable, "scripts/t35_open_fill_verify.py"], None),
    ("t24_prospect_paper", [sys.executable, "scripts/t24_prospect_paper.py", "run"], None),
    ("t24_prospect_promotion", [sys.executable, "scripts/t24_prospect_promotion.py", "run"], None),
    ("aggressive_lab_paper", [sys.executable, "scripts/aggressive_lab.py", "paper"], None),
    ("alloc_paper", [sys.executable, "scripts/alloc_paper.py", "run"], None),
    ("grid_paper", [sys.executable, "scripts/grid_paper.py", "run"], None),
    ("system_v1_paper", [sys.executable, "scripts/system_v1_paper.py", "run"], None),
    ("t35_paper_export", [sys.executable, "scripts/t35_paper_export.py", "run"], None),
    ("daily_scorecard", [sys.executable, "scripts/daily_scorecard.py"], None),
    ("daily_report", [sys.executable, "scripts/daily_report.py", "run"], None),
    ("build_status", [sys.executable, "-m", "monitor.build_status"], None),
    ("token_meter", [sys.executable, "scripts/token_meter.py"], None),
]

log = io.open("results/_r389bmb_s6.log", "w", encoding="utf-8", newline="\n")


def w(s):
    log.write(s + "\n")
    log.flush()
    print(s)


def main():
    t0 = time.time()
    w(f"r389 bm-b S6 chain start {time.strftime('%Y-%m-%d %H:%M:%S')}")
    fails = []
    for name, cmd, extra_env in LEGS:
        t1 = time.time()
        env = dict(os.environ)
        if extra_env:
            env.update(extra_env)
        try:
            p = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=900,
                              env=env)
            rc = p.returncode
            out = (p.stdout or "").strip().splitlines()
            err = (p.stderr or "").strip().splitlines()
            tail = out[-1] if out else (err[-1] if err else "(no output)")
        except subprocess.TimeoutExpired:
            rc, tail = -99, "TIMEOUT-900s"
        dt = round(time.time() - t1, 1)
        w(f"[{name}] rc={rc} {dt}s | {tail[:220]}")
        if rc != 0:
            fails.append((name, rc))
    w(f"r389 S6 chain done: {len(LEGS)} legs, {len(fails)} nonzero "
      f"({', '.join(f'{n}={r}' for n, r in fails) if fails else 'all rc=0'}) "
      f"elapsed {round(time.time() - t0, 1)}s")
    log.close()
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
