# -*- coding: utf-8 -*-
"""r375 bm-b S6 maintenance-chain driver: runs the standing chain legs
sequentially, logs rc + tail line per leg to results/_r375bmb_s6.log
(UTF-8, no PS redirection encoding traps per r209 law). Monday 10:2x
expected family: idempotent no-ops (panel cutoff 2026-09-24, next bar
Mon 09-28 15:30). r359 paradigm zero-rewrite."""
import io
import subprocess
import sys
import time

LEGS = [
    ("compute_audit", [sys.executable, "scripts/compute_audit.py"]),
    ("py_watermark_probe", [sys.executable, "scripts/py_watermark.py", "probe"]),
    ("update_daily", [sys.executable, "scripts/update_daily.py"]),
    ("market_regime", [sys.executable, "scripts/market_regime.py"]),
    ("strategy_scorecard", [sys.executable, "scripts/strategy_scorecard.py"]),
    ("market_clock_call", [sys.executable, "scripts/market_clock_call.py", "run"]),
    ("update_lhb", [sys.executable, "scripts/update_lhb.py"]),
    ("update_heat", [sys.executable, "scripts/update_heat.py"]),
    ("update_futures", [sys.executable, "scripts/update_futures.py"]),
    ("update_repo", [sys.executable, "scripts/update_repo.py"]),
    ("update_options", [sys.executable, "scripts/update_options.py"]),
    ("update_moneyflow", [sys.executable, "scripts/update_moneyflow.py"]),
    ("update_sina_mf", [sys.executable, "scripts/update_sina_mf.py"]),
    ("update_astock_daily", [sys.executable, "scripts/update_astock_daily.py"]),
    ("rev_osc_signal_export", [sys.executable, "scripts/rev_osc_signal_export.py", "run"]),
    ("update_ths_panel", [sys.executable, "scripts/update_ths_panel.py"]),
    ("ah_panel_puller", [sys.executable, "scripts/ah_panel_puller.py"]),
    ("update_fund_premium", [sys.executable, "scripts/update_fund_premium.py", "snapshot"]),
    ("update_fundamental", [sys.executable, "scripts/update_fundamental.py"]),
    ("b_layer_filter", [sys.executable, "-m", "firm.risk.b_layer_filter"]),
    # new-bar-gated trio (live.paper / t35_open_fill_verify / t24_prospect_paper)
    # SKIPPED this round: no new bar (pre-market Monday, panel cutoff
    # 2026-09-24, next bar = Mon 09-28 15:30) -- same legal-skip family
    # as r338/r339/r352/r359.
    ("t24_prospect_promotion", [sys.executable, "scripts/t24_prospect_promotion.py", "run"]),
    ("aggressive_lab_paper", [sys.executable, "scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper", [sys.executable, "scripts/alloc_paper.py", "run"]),
    ("grid_paper", [sys.executable, "scripts/grid_paper.py", "run"]),
    ("system_v1_paper", [sys.executable, "scripts/system_v1_paper.py", "run"]),
    ("t35_paper_export", [sys.executable, "scripts/t35_paper_export.py", "run"]),
    ("daily_scorecard", [sys.executable, "scripts/daily_scorecard.py"]),
    ("daily_report", [sys.executable, "scripts/daily_report.py", "run"]),
    ("build_status", [sys.executable, "-m", "monitor.build_status"]),
    ("token_meter", [sys.executable, "scripts/token_meter.py"]),
]

GATED_SKIP = ["live.paper", "t35_open_fill_verify", "t24_prospect_paper"]

log = io.open("results/_r375bmb_s6.log", "w", encoding="utf-8", newline="\n")


def w(s):
    log.write(s + "\n")
    log.flush()
    print(s)


def main():
    t0 = time.time()
    w(f"r375 bm-b S6 chain start {time.strftime('%Y-%m-%d %H:%M:%S')}")
    w("gated-skip (no new bar, pre-market Monday): " + ", ".join(GATED_SKIP))
    fails = []
    for name, cmd in LEGS:
        t1 = time.time()
        try:
            p = subprocess.run(cmd, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=900)
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
    w(f"r375 S6 chain done: {len(LEGS)} legs, {len(fails)} nonzero "
      f"({', '.join(f'{n}={r}' for n, r in fails) if fails else 'all rc=0'}) "
      f"+ {len(GATED_SKIP)} new-bar-gated legal skips, "
      f"elapsed {round(time.time() - t0, 1)}s")
    log.close()
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
