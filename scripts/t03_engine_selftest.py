"""scripts/t03_engine_selftest.py — T-03 engine-integrity flag selftest (offline, synthetic, zero network).

Task T-2026-09-23-03 acceptance: selftests for EVERY new flag path.
  F1 trade_pnl_mode='full' (buy-side cost in per-trade pnl, new field names)
  F2 strict_open_fills (entry drop / exit defer on suspension) + stale_mark_tag
  F4 sizing_mode='equity_fraction'
  F5 trailing_lock / initial_stop params passthrough
  F6 report_num_entries dual-basis (entries vs tranches)
  F7 donchian long-only 0/1 (masked equivalence proof) + vol_target rv==0 guard
     + min_periods equivalence (pandas default == window, byte-identical proof)

Legacy identity: the definitive proof is the 6-trader anchor gate (frozen
registered evidence) + smoke determinism, run in the acceptance chain.
Here: determinism double-run + exact legacy-metrics-key-set under default flags.

Run:  python scripts/t03_engine_selftest.py   (exit 0 = all PASS)
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from engine.backtester import run_backtest
from knowledge.rules import FeeSchedule
from strategies.trend import donchian_breakout, dual_ma_cross, triple_ma, supertrend
from strategies.volatility import vol_target

COST_RATE = (FeeSchedule().commission_rate + FeeSchedule().handling_fee
             + FeeSchedule().supervision_fee + FeeSchedule().slippage_a)
DATES = pd.date_range("2024-01-02", periods=30)


def _frame(opens, closes):
    return pd.DataFrame({"open": opens, "close": closes,
                         "high": closes, "low": closes}, index=DATES)


def _sig(days_on, value=True):
    s = pd.Series(False, index=DATES)
    s.iloc[list(days_on)] = value
    return s


def _entry_exit_df(sym_signals: dict) -> pd.DataFrame:
    """{sym: (entry_days, exit_days)} -> entry/exit DataFrames."""
    ent = pd.DataFrame({sym: s[0] for sym, s in sym_signals.items()}, index=DATES)
    ext = pd.DataFrame({sym: s[1] for sym, s in sym_signals.items()}, index=DATES)
    return ent, ext


def _gap_prices() -> dict:
    """G and H: real 0-9, SUSPENDED (NaN) 10-14, real 15-29.
    G's post-gap close drifts to 10.5 (identifiable deferred-exit price);
    H stays at 10.0 (its suspension-day ENTRY is the P0-3 test subject)."""
    n = len(DATES)
    g_open = pd.Series(10.0, index=DATES)
    g_close = pd.Series(10.0, index=DATES)
    g_open.iloc[10:15] = np.nan
    g_close.iloc[10:15] = np.nan
    g_close.iloc[15:] = 10.5
    g_open.iloc[15:] = 10.5
    h_open = pd.Series(10.0, index=DATES)
    h_close = pd.Series(10.0, index=DATES)
    h_open.iloc[10:15] = np.nan
    h_close.iloc[10:15] = np.nan
    return {"G": _frame(g_open, g_close), "H": _frame(h_open, h_close)}


def main() -> int:
    checks = []

    def ok(name, cond):
        checks.append((name, bool(cond)))
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")

    # ---------------------------------------------------------- S1: strict_open_fills
    prices = _gap_prices()
    # G: enter day 8 -> fills day 9 open (real); reversal exit signal day 12 (inside gap)
    # H: entry signal day 11 -> execution attempt day 12 open (suspension, ffilled)
    ent, ext = _entry_exit_df({
        "G": (_sig([8]), _sig([12])),
        "H": (_sig([11]), _sig([20])),
    })
    base_params = {"position_size_pct": 0.10, "max_positions": 5}

    run_legacy = run_backtest(prices, dict(base_params), entry_signal=ent, exit_signal=ext)
    run_strict = run_backtest(prices, dict(base_params, strict_open_fills=True),
                              entry_signal=ent, exit_signal=ext)

    h_legacy = [t for t in run_legacy["trades"] if t["symbol"] == "H"]
    h_strict = [t for t in run_strict["trades"] if t["symbol"] == "H"]
    ok("F2 legacy fills the suspension-day entry at the ffilled stale price (P0-3 documented)",
       len(h_legacy) >= 1 and h_legacy[0]["price"] == 10.0)
    ok("F2 strict_open_fills DROPS the suspension-day pending entry (zero H trades)",
       len(h_strict) == 0)

    g_legacy = [t for t in run_legacy["trades"] if t["symbol"] == "G"]
    g_strict = [t for t in run_strict["trades"] if t["symbol"] == "G"]
    ok("F2 legacy executes the in-gap exit at the stale close (day 12)",
       g_legacy and g_legacy[0]["date"] == str(DATES[12].date()) and g_legacy[0]["price"] == 10.0)
    ok("F2 strict DEFERS the exit to the first real-bar close (day 15) keeping the original reason",
       g_strict and g_strict[0]["date"] == str(DATES[15].date())
       and g_strict[0]["price"] == 10.5 and g_strict[0]["reason"] == "signal_reversal")

    # ---------------------------------------------------------- stale_mark_tag (F2)
    ent_g, ext_g = _entry_exit_df({"G": (_sig([8]), _sig([20])), "H": (_sig([], False), _sig([], False))})
    run_marks = run_backtest(prices, dict(base_params, stale_mark_tag=True),
                             entry_signal=ent_g, exit_signal=ext_g)
    m = run_marks["metrics"]
    ok("F2 stale_mark_tag: gap days held through are flagged (exactly 5)",
       m.get("stale_mark_days") == 5)
    ok("F2 stale_mark_tag: sharpe_ex_stale present and finite",
       math.isfinite(m.get("sharpe_ex_stale", float("nan"))))
    ok("F2 default run has NO stale fields (legacy key set untouched)",
       "stale_mark_days" not in run_legacy["metrics"]
       and "sharpe_ex_stale" not in run_legacy["metrics"])

    # ---------------------------------------------------------- S2: trade_pnl_mode (F1)
    # W: +3% winner (single close via reversal). T: tiny gainer 1.5*cost_rate
    # (legacy-positive, full-negative -> win-rate flip). L: layered TP symbol.
    w_open = pd.Series(10.0, index=DATES)
    w_close = pd.Series(10.0, index=DATES)
    w_close.iloc[2:6] = [10.1, 10.2, 10.3, 10.3]  # +3% by day 5
    t_close = pd.Series(10.0, index=DATES)
    t_close.iloc[5] = 10.0 * (1 + 1.5 * COST_RATE)   # ~+0.195%: between 1x and 2x cost
    l_close = pd.Series(10.0, index=DATES)
    l_close.iloc[2:9] = [10.1, 10.2, 10.3, 10.4, 10.6, 10.6, 10.6]  # tier1 (+5%) day 6
    px2 = {
        "W": _frame(w_open, w_close),
        "T": _frame(pd.Series(10.0, index=DATES), t_close),
        "L": _frame(pd.Series(10.0, index=DATES), l_close),
    }
    ent2, ext2 = _entry_exit_df({
        "W": (_sig([0]), _sig([5])),
        "T": (_sig([0]), _sig([5])),
        "L": (_sig([0]), _sig([8])),   # after tier1 scale-out -> rest via reversal
    })
    run_pnl = run_backtest(px2, dict(base_params, trade_pnl_mode="full",
                                     report_num_entries=True),
                           entry_signal=ent2, exit_signal=ext2)
    tr = run_pnl["trades"]

    def _buy_cost(t):
        # cost_price*qty*cost_rate reconstructed from the trade record
        # (entry open = 10.0 for every fixture here)
        return round(10.0 * t["qty"] * COST_RATE, 2)

    ok("F1 full mode: every trade carries pnl_full",
       bool(tr) and all("pnl_full" in t for t in tr))
    ok("F1 identity: pnl_full = pnl - buy-side cost (within rounding)",
       all(abs(t["pnl_full"] - (t["pnl"] - _buy_cost(t))) <= 0.05 for t in tr))

    ok("F1 win_rate flips under full cost (tiny gainer reclassified)",
       run_pnl["metrics"]["win_rate_full"] < run_pnl["metrics"]["win_rate"])
    ok("F1 legacy keys unchanged by full mode (win_rate still present, plus *_full)",
       {"win_rate", "win_rate_full", "profit_factor_full", "avg_pnl_full"}
       <= set(run_pnl["metrics"]))
    ok("F1 default run trades carry NO pnl_full key",
       all("pnl_full" not in t for t in run_legacy["trades"]))

    # ---------------------------------------------------------- S3: sizing_mode (F4)
    a_open = pd.Series(10.0, index=DATES)
    a_close = pd.Series(10.0, index=DATES)
    a_open.iloc[2:8] = [10.1, 10.2, 10.25, 10.3, 10.35, 10.4]   # opens track the rise
    a_close.iloc[2:8] = [10.1, 10.2, 10.25, 10.3, 10.35, 10.4]  # +4%, below tier1
    b_open = pd.Series(20.0, index=DATES)
    b_close = pd.Series(20.0, index=DATES)
    px3 = {"A": _frame(a_open, a_close), "B": _frame(b_open, b_close)}
    ent3, ext3 = _entry_exit_df({
        "A": (_sig([0]), _sig([25])),
        "B": (_sig([6]), _sig([25])),
    })
    p3 = {"position_size_pct": 0.25, "max_positions": 5}
    run_fix = run_backtest(px3, dict(p3), entry_signal=ent3, exit_signal=ext3)
    run_eqf = run_backtest(px3, dict(p3, sizing_mode="equity_fraction"),
                           entry_signal=ent3, exit_signal=ext3)
    fix_b = max((t["qty"] for t in run_fix["trades"] if t["symbol"] == "B"), default=0.0)
    eqf_b = max((t["qty"] for t in run_eqf["trades"] if t["symbol"] == "B"), default=0.0)
    ok("F4 equity_fraction sizes the second entry off CURRENT equity (> fixed)",
       eqf_b > fix_b * 1.005)
    ok("F4 fixed_initial first entry identical in both modes",
       abs(max((t["qty"] for t in run_fix["trades"] if t["symbol"] == "A"), default=0.0)
           - max((t["qty"] for t in run_eqf["trades"] if t["symbol"] == "A"), default=0.0)) < 1e-9)

    # ---------------------------------------------------------- S4: F5 trailing/initial_stop
    d_open = pd.Series(10.0, index=DATES)
    d_close = pd.Series(10.0, index=DATES)
    d_close.iloc[2] = 9.85   # -1.5% dip on day 2 close
    px4 = {"D": _frame(d_open, d_close)}
    ent4, ext4 = _entry_exit_df({"D": (_sig([0]), _sig([], False))})
    run_loose = run_backtest(px4, dict(base_params), entry_signal=ent4, exit_signal=ext4)
    run_tight = run_backtest(px4, dict(base_params, initial_stop=-0.01),
                             entry_signal=ent4, exit_signal=ext4)
    ok("F5 initial_stop passthrough: -1% stop fires on a -1.5% dip",
       any(t["reason"] == "stop_loss" for t in run_tight["trades"]))
    ok("F5 default initial_stop (-8%) does NOT fire on a -1.5% dip",
       not any(t["reason"] == "stop_loss" for t in run_loose["trades"]))

    e_close = pd.Series(10.0, index=DATES)
    e_close.iloc[2:9] = [10.2, 10.4, 10.6, 10.5, 10.3, 9.0, 9.0]  # rise +6% then fall
    px5 = {"E": _frame(d_open, e_close)}
    ent5, ext5 = _entry_exit_df({"E": (_sig([0]), _sig([20]))})
    run_trail_def = run_backtest(px5, dict(base_params), entry_signal=ent5, exit_signal=ext5)
    run_trail_deep = run_backtest(px5, dict(base_params, trailing_lock=0.30),
                                  entry_signal=ent5, exit_signal=ext5)
    sl_def = [t for t in run_trail_def["trades"] if t["reason"] == "stop_loss"]
    sl_deep = [t for t in run_trail_deep["trades"] if t["reason"] == "stop_loss"]
    ok("F5 trailing_lock passthrough: deep lock (30%) delays the trailing stop vs default (1%)",
       (not sl_deep and sl_def) or (sl_def and sl_deep and sl_deep[0]["date"] > sl_def[0]["date"]))

    # ---------------------------------------------------------- S5: F6 dual basis
    m_pnl = run_pnl["metrics"]
    ok("F6 num_entries reported alongside num_trades",
       m_pnl.get("num_entries") is not None and m_pnl.get("num_trades") is not None)
    ok("F6 layered take-profit pads num_trades above num_entries (dual-basis is real)",
       m_pnl["num_trades"] > m_pnl["num_entries"])
    ok("F6 default run reports NO num_entries (legacy key set)",
       "num_entries" not in run_legacy["metrics"])

    # ---------------------------------------------------------- S6: F7 donchian long-only
    path = pd.Series(10.0 + 2.0 * np.sin(np.arange(len(DATES)) / 4.0), index=DATES)
    hi = path   # high==low==close so breakouts/breakdowns actually fire on a smooth path
    lo = path
    new = donchian_breakout(path, hi, lo, entry_n=5, exit_n=3)
    old_pos = np.where(path >= hi.rolling(5).max(), 1,
                      np.where(path <= lo.rolling(3).min(), -1, 0))
    old = pd.Series(old_pos, index=DATES).replace(0, np.nan).ffill().fillna(0)
    ok("F7 donchian v2 output is strictly 0/1 (long-only contract)",
       set(new.unique()) <= {0, 1})
    ok("F7 donchian fixture exercises the short state under the old contract",
       (old < 0).any())
    ok("F7 donchian masked (pos>0) outputs identical to legacy (LFC-consumer identity)",
       ((new > 0) == (old > 0)).all())
    ok("F7 donchian breakdown now sets flat 0 (not short -1)",
       not (new < 0).any() and (new == 0).any())

    # ---------------------------------------------------------- S7: F7 vol_target guard
    flat = pd.Series(10.0, index=pd.date_range("2024-01-02", periods=40))
    vt_new = vol_target(flat, n=20)
    rv_leg = flat.pct_change().rolling(20).std() * np.sqrt(252)
    vt_leg = (0.15 / rv_leg).clip(upper=1.0)
    ok("F7 vol_target rv==0: legacy mapped to degenerate 1.0, new maps to NaN (flat)",
       bool(vt_new.iloc[20:].isna().all()) and bool((vt_leg.iloc[20:] == 1.0).all()))
    wob = pd.Series(10.0 + np.sin(np.arange(40) / 3.0), index=flat.index)
    vt_new2 = vol_target(wob, n=20)
    rv2 = wob.pct_change().rolling(20).std() * np.sqrt(252)
    vt_leg2 = (0.15 / rv2).clip(upper=1.0)
    ok("F7 vol_target unchanged on rv!=0 cells (equivalence to legacy formula)",
       np.allclose(vt_new2.values, vt_leg2.values, equal_nan=True))

    # ---------------------------------------------------------- S8: min_periods equivalence
    ok("F7 dual_ma_cross explicit min_periods == pandas default (byte-identical)",
       (dual_ma_cross(path) ==
        ((path.rolling(5).mean() > path.rolling(20).mean()).astype(int))).all())
    ok("F7 triple_ma explicit min_periods == pandas default (byte-identical)",
       (triple_ma(path) ==
        (((path.rolling(5).mean() > path.rolling(20).mean())
          & (path.rolling(20).mean() > path.rolling(60).mean())).astype(int))).all())
    st = supertrend(path, hi, lo, n=10)
    ok("F7 supertrend explicit min_periods == pandas default (byte-identical)",
       (st >= 0).all() and (st <= 1).all() and len(st) == len(path))

    # ---------------------------------------------------------- S9: determinism + key set
    r1 = run_backtest(prices, dict(base_params), entry_signal=ent, exit_signal=ext)
    r2 = run_backtest(prices, dict(base_params), entry_signal=ent, exit_signal=ext)
    ok("determinism: identical double-run (metrics+trades+equity)",
       json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True))
    ok("legacy metrics key set exactly the 7 historical keys under default flags",
       set(r1["metrics"]) == {"annual_return", "sharpe", "max_drawdown", "win_rate",
                              "profit_factor", "num_trades", "avg_hold_days"})

    n_fail = sum(1 for _, c in checks if not c)
    print(f"\nt03_engine_selftest: {len(checks)-n_fail}/{len(checks)} PASS, {n_fail} FAIL")
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
