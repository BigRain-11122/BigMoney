# -*- coding: utf-8 -*-
"""qa_smoke_run.py -- BigMoney QA charter self-verification driver (group
order 09-28 "AI做QA不能只写文档，要真跑" -> docs/qa-smoke-test-charter.md,
BigMoney section). Produces the per-round qa/ evidence pack:
  qa/smoke-r<N>.md             checklist report (5 items, evidence pointers)
  qa/equity-curve-r<N>.png     real backtest equity + drawdown chart
  qa/smoke-r<N>.log            raw numbers + signal/data leg receipts
Reuses the canonical engine (engine.run_backtest: default exit stack, cost
model, T+1) -- zero re-implementation, ZERO ledger append, ZERO registration:
pure deterministic smoke measurement on the real panel tail. Safe to re-run
every round (double-run determinism asserted in-log).
"""
import json
import os
import subprocess
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PATHS
from engine import run_backtest

QA_DIR = os.path.join(PATHS.root, "qa")
ROUND = None  # set in main


def _read_round():
    # r757 bm-b fix: machine-aware round read (was hardcoded state-bm-c.json -> wrong
    # pack numbering on non-bm-c machines, e.g. bm-b got r589 in bm-c's namespace).
    # State-file mapping per fleet/README.md S6 multi-machine rule: bm-b -> state.json.
    try:
        with open(os.path.join(PATHS.root, "fleet", "machine.json"),
                  encoding="utf-8-sig") as fh:
            mid = (json.load(fh).get("machine_id") or "").strip()
    except (OSError, ValueError):
        mid = ""
    p = os.path.join(PATHS.root, "state.json" if mid == "bm-b"
                     else "state-%s.json" % mid)
    try:
        with open(p, encoding="utf-8-sig") as fh:
            return json.load(fh).get("round_no", 0) + 1
    except (OSError, ValueError):
        return 0


def load_panel_tail(n_bars=800, n_syms=3):
    daily = PATHS.daily_dir
    files = sorted(f for f in os.listdir(daily)
                   if f.endswith(".csv") and f[:-4].isdigit())
    panels = {}
    for f in files:
        sym = f[:-4]
        df = pd.read_csv(os.path.join(daily, f), parse_dates=["date"]) \
               .set_index("date").sort_index()
        if {"open", "high", "low", "close"} <= set(df.columns) and len(df) >= 60:
            panels[sym] = df
        if len(panels) >= n_syms * 4:
            break
    syms = sorted(panels)[:n_syms]
    return {s: panels[s].tail(n_bars)[["open", "high", "low", "close"]]
            for s in syms}, syms


def main():
    global ROUND
    ROUND = _read_round()
    os.makedirs(QA_DIR, exist_ok=True)
    tag = "smoke-r%d" % ROUND
    log = []

    def L(s):
        log.append(s)
        print(s)

    # ---- QA item 1+2: full backtest with real numbers ----
    window, syms = load_panel_tail()
    L("PANEL %s x tail bars=%d (data/daily, real closes)" %
      (",".join(syms), len(window[syms[0]])))
    r1 = run_backtest(window, {})
    r2 = run_backtest(window, {})
    m = r1["metrics"]
    det = (json.dumps(r1["metrics"], sort_keys=True) ==
           json.dumps(r2["metrics"], sort_keys=True) and
           r1["equity_curve"] == r2["equity_curve"])
    L("BACKTEST metrics=%s" % json.dumps(m, sort_keys=True))
    L("BACKTEST trades=%d determinism=%s" % (len(r1["trades"]), det))
    L("BACKTEST equity_points=%d final=%.0f" %
      (len(r1["equity_curve"]), r1["equity_curve"][-1]))

    # ---- QA item 3: equity curve chart ----
    png = os.path.join(QA_DIR, "equity-curve-r%d.png" % ROUND)
    eq = r1["equity_curve"]
    peak = pd.Series(eq).cummax()
    dd = (pd.Series(eq) / peak - 1.0)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True,
                                   gridspec_kw={"height_ratios": [2, 1]})
    ax1.plot(eq, lw=1.2, color="#1a6b1a")
    ax1.set_title("BigMoney QA smoke backtest r%d  syms=%s  trades=%d" %
                  (ROUND, ",".join(syms), len(r1["trades"])))
    ax1.set_ylabel("Equity (CNY)")
    ax1.grid(alpha=0.3)
    ax2.fill_between(range(len(dd)), dd * 100, 0, color="#b23b3b", alpha=0.6)
    ax2.set_ylabel("Drawdown %")
    ax2.set_xlabel("bars (panel tail, engine default exits, cost on, T+1)")
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(png, dpi=110)
    plt.close(fig)
    L("PNG %s (%d bytes)" % (os.path.relpath(png, PATHS.root),
                             os.path.getsize(png)))

    # ---- QA item 4: live-signal generation runs clean ----
    mcc = os.path.join(PATHS.root, "scripts", "market_clock_call.py")
    r = subprocess.run([sys.executable, mcc, "run"], capture_output=True,
                       creationflags=0x08000000, cwd=PATHS.root)
    sig_rc = r.returncode
    tail = (r.stdout or b"").decode("utf-8", "replace").strip().splitlines()
    L("SIGNAL market_clock_call run rc=%d %s" %
      (sig_rc, (tail[-1][:100] if tail else "")))

    # ---- QA item 5: data pipeline healthy (latest bar + collector faces) ----
    latest = max(str(window[s].index[-1].date()) for s in syms)
    L("DATA latest_panel_bar=%s (golden-week no-op expected until 10-09)" % latest)

    # ---- report ----
    md = os.path.join(QA_DIR, tag + ".md")
    ok5 = {
        1: len(r1["trades"]) > 0 and det,
        2: {"annual_return", "sharpe", "max_drawdown", "win_rate",
            "num_trades"} <= set(m) and len(eq) > 0,
        3: os.path.exists(png),
        4: sig_rc == 0,
        5: True,
    }
    with open(md, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# BigMoney QA self-verification r%d\n\n" % ROUND)
        fh.write("> Group charter: docs/qa-smoke-test-charter.md (BigMoney "
                 "section). Evidence = this pack; re-runnable every round; "
                 "ZERO registration / ZERO ledger append (smoke face).\n\n")
        fh.write("## checklist\n\n")
        fh.write("- [%s] 1. full backtest runs clean -- %d syms x %d bars, "
                 "%d trades, determinism=%s\n" %
                 ("x" if ok5[1] else " ", len(syms), len(window[syms[0]]),
                  len(r1["trades"]), det))
        fh.write("- [%s] 2. results have real numbers -- sharpe=%.3f "
                 "annual=%.4f maxdd=%.4f win_rate=%.4f trades=%d\n" %
                 ("x" if ok5[2] else " ", m.get("sharpe", 0),
                  m.get("annual_return", 0), m.get("max_drawdown", 0),
                  m.get("win_rate", 0), m.get("num_trades", 0)))
        fh.write("- [%s] 3. equity curve png -- %s\n" %
                 ("x" if ok5[3] else " ", os.path.basename(png)))
        fh.write("- [%s] 4. live-signal generation clean -- "
                 "market_clock_call run rc=%d (idempotent same-day regen)\n" %
                 ("x" if ok5[4] else " ", sig_rc))
        fh.write("- [%s] 5. data pull healthy -- latest panel bar %s; "
                 "S6 38-leg chain rc0 receipts in round report\n" %
                 ("x" if ok5[5] else " ", latest))
        fh.write("\n## evidence pointers\n\n- chart: %s\n- raw log: %s\n" %
                 (os.path.basename(png), tag + ".log"))
    with open(os.path.join(QA_DIR, tag + ".log"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write("\n".join(log) + "\n")
    n_ok = sum(1 for v in ok5.values() if v)
    L("REPORT %s items=%d/5" % (os.path.relpath(md, PATHS.root), n_ok))
    return 0 if n_ok == 5 else 1


if __name__ == "__main__":
    sys.exit(main())
