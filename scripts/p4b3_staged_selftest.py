"""scripts/p4b3_staged_selftest.py — P4-B3 staged_entry flag selftest
(offline, synthetic, zero network).

Ticket T-2026-09-25-42 acceptance: the four hard gates from the frozen spec
research/shortline/P4_BATCH3_DCA_SPEC.md section 2, plus behavior gates:
  G1  flag-off byte identity: explicit staged_entry=None run == run without
      the param, byte-identical JSON (same-input full-run diff); legacy
      metrics key set carries NO staged keys.
  G2  VWAP accounting: hand-synthesized 3-tranche example verified
      per-share (quantity, VWAP cost_price, no-reset high_watermark, tranche-0
      budget split, trigger timing day-by-day).
  G3  trigger causality: truncate-and-compare -- all add decisions made
      before the truncation point are unchanged by future data.
  G4  redline refusal: grid_fracs sum > 1.0 / non-positive frac / trigger
      misalignment all refuse to run (ValueError before any data work).
  G5  keyset discipline: staged keys ONLY when the flag is ON; the 7 legacy
      metric keys intact in both modes.
  G6  fill-guard drop + level re-queue: a blocked add open drops that
      tranche (counted in num_adds_dropped, NOT in fill_guard_buy_dropped)
      and the still-live level re-queues at the next close.
  G7  stop follows the VWAP (redline c liveness): staged stop fires one day
      LATER than the single-shot stop on the same tape (stop line moved down
      with the average -- the disclosed cost of averaging down), and still
      fires (never disabled).
  G8  window-end orphan: an add queued at the final close never executes
      and is counted as an honest drop.

Run:  python scripts/p4b3_staged_selftest.py   (exit 0 = all PASS)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from engine.backtester import run_backtest

N = 24
DATES = pd.date_range("2024-01-02", periods=N)
STAGED = {"grid_fracs": (0.4, 0.3, 0.3), "add_triggers": (0.0, -0.05, -0.10)}
# exits neutered for hold-through fixtures: TP unreachable, no time-decay.
# P5 loss_time_stop (8d) / P6 hard limit (25d) stay live BY DESIGN -- the
# fixtures are built to stay clear of them (see hold-day accounting below).
HOLD_PARAMS = {"position_size_pct": 0.10, "max_positions": 5,
               "take_profit_levels": (0.50,), "time_decay_period": 999}


def _panel(open_over, close_over, n=N, base=10.0):
    idx = pd.date_range("2024-01-02", periods=n)
    o = pd.Series(base, index=idx)
    c = pd.Series(base, index=idx)
    for d, v in open_over.items():
        o.iloc[d] = v
    for d, v in close_over.items():
        c.iloc[d] = v
    return {"S": pd.DataFrame({"open": o, "close": c, "high": c, "low": c},
                               index=idx)}


def _sig(days, n=N, value=True):
    s = pd.Series(False, index=pd.date_range("2024-01-02", periods=n))
    s.iloc[list(days)] = value
    return s


def _signals(entry_days, exit_days=(), n=N):
    idx = pd.date_range("2024-01-02", periods=n)
    ent = pd.DataFrame({"S": _sig(entry_days, n)}, index=idx)
    ext = pd.DataFrame({"S": _sig(list(exit_days), n)}, index=idx)
    return ent, ext


def _rng(start, n, value):
    """Override dict covering every day from `start` to the window end
    (fixture values are set at SERIES-BUILD time -- pandas 3.0 CoW makes
    post-hoc chained assignment silently no-op, so no .iloc writes)."""
    return {d: value for d in range(start, n)}


def _wave_panel(n=120):
    idx = pd.date_range("2023-01-02", periods=n)
    out = {}
    for j, (b, a) in enumerate([(10.0, 1.5), (20.0, 2.5), (5.0, 0.8)]):
        s = pd.Series(b + a * np.sin(np.arange(n) / 18.0 + j * 1.3)
                      + 0.02 * np.arange(n), index=idx)
        out[f"SYM{j}"] = pd.DataFrame({"open": s, "close": s,
                                       "high": s, "low": s}, index=idx)
    return out


def main() -> int:
    checks = []

    def ok(name, cond):
        checks.append((name, bool(cond)))
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")

    # ------------------------------------------------ G1: flag-off byte identity
    waves = _wave_panel()
    p1 = {"position_size_pct": 0.10, "max_positions": 5}
    r_none = run_backtest(waves, dict(p1))                       # param absent
    r_off = run_backtest(waves, dict(p1), staged_entry=None)     # flag OFF
    ok("G1 flag-off run is byte-identical to the param-absent run",
       json.dumps(r_none, sort_keys=True) == json.dumps(r_off, sort_keys=True))
    ok("G1 fixture is non-vacuous (real trades on the wave panel)",
       r_none["metrics"]["num_trades"] >= 1)
    ok("G1 determinism double-run identical",
       json.dumps(run_backtest(waves, dict(p1)), sort_keys=True)
       == json.dumps(r_none, sort_keys=True))
    staged_keys = {"num_adds_filled", "num_adds_dropped", "avg_cost_first",
                   "avg_cost_end", "adds_per_entry"}
    ok("G1 legacy metrics key set carries NO staged keys",
       not (staged_keys & set(r_none["metrics"])))

    # ------------------------------------------------ G2: VWAP hand-synthesis
    # tape: fill day1 open 10.0 (tranche0 40k -> 4000 sh); day1 close 9.4
    # queues k=1 (<=9.5); day2 open 9.0 fills 30k -> 3333.33 sh; day2 close
    # 8.9 queues k=2 (<=9.0); day3 open 8.8 fills 30k -> 3409.09 sh; VWAP
    # = 100000/10742.42 = 9.3085; stop lines stay clear every day.
    px2 = _panel({1: 10.0, 2: 9.0, 3: 8.8, **_rng(4, N, 9.35)},
                 {1: 9.4, 2: 8.9, 3: 9.0, **_rng(4, N, 9.35)})
    ent2, ext2 = _signals([0])
    r2 = run_backtest(px2, dict(HOLD_PARAMS), entry_signal=ent2,
                      exit_signal=ext2, staged_entry=STAGED)
    exp_qty = 4000.0 + 30000.0 / 9.0 + 30000.0 / 8.8
    exp_vwap = 100000.0 / exp_qty
    op = r2.get("open_positions", [])
    ok("G2 staged position held to window end (open_positions present)",
       len(op) == 1 and op[0]["symbol"] == "S")
    ok("G2 quantity == hand-synthesized 3-tranche sum",
       abs(op[0]["quantity"] - round(exp_qty, 2)) <= 0.01)
    ok("G2 cost_price == hand-synthesized VWAP",
       abs(op[0]["cost_price"] - round(exp_vwap, 4)) <= 5e-4)
    ok("G2 high_watermark keeps the first-fill max 10.0 (never reset)",
       op[0]["high_watermark"] == 10.0)
    m2 = r2["metrics"]
    ok("G2 tranche-0 budget split is real (first fill 4000 sh, not 10000)",
       abs(op[0]["quantity"] - 10000.0) > 100.0)
    ok("G2 num_adds_filled == 2, num_adds_dropped == 0, adds_per_entry == 2.0",
       m2["num_adds_filled"] == 2 and m2["num_adds_dropped"] == 0
       and m2["adds_per_entry"] == 2.0)
    ok("G2 avg_cost_first == first fill 10.0",
       m2["avg_cost_first"] == 10.0)
    ok("G2 avg_cost_end == final VWAP",
       abs(m2["avg_cost_end"] - round(exp_vwap, 4)) <= 5e-4)
    ok("G2 no exit trades fired while averaging (stop lines respected)",
       r2["trades"] == [])

    # ------------------------------------------------ G3: trigger causality
    px3 = _panel({1: 10.0, 2: 9.0, 3: 8.8, **_rng(4, N, 9.35)},
                 {1: 9.4, 2: 8.9, 3: 9.0, **_rng(4, N, 9.35)})
    ent3, ext3 = _signals([0])
    r3full = run_backtest(px3, dict(HOLD_PARAMS), entry_signal=ent3,
                          exit_signal=ext3, staged_entry=STAGED)
    cut = 7  # all adds filled by day 3 open; days 0..6 kept
    px3t = {"S": px3["S"].iloc[:cut].copy()}
    ent3t, ext3t = _signals([0], n=cut)
    r3trunc = run_backtest(px3t, dict(HOLD_PARAMS), entry_signal=ent3t,
                           exit_signal=ext3t, staged_entry=STAGED)
    ok("G3 truncation leaves every pre-cut add decision unchanged (qty)",
       abs(r3full["open_positions"][0]["quantity"]
           - r3trunc["open_positions"][0]["quantity"]) <= 0.01)
    ok("G3 truncation leaves every pre-cut add decision unchanged (VWAP)",
       abs(r3full["open_positions"][0]["cost_price"]
           - r3trunc["open_positions"][0]["cost_price"]) <= 5e-4)
    ok("G3 num_adds_filled identical pre/post truncation",
       r3full["metrics"]["num_adds_filled"]
       == r3trunc["metrics"]["num_adds_filled"] == 2)

    # ------------------------------------------------ G4: redline refusal
    def _raises(kwargs):
        try:
            run_backtest(px2, dict(HOLD_PARAMS), entry_signal=ent2,
                         exit_signal=ext2, **kwargs)
            return False
        except ValueError:
            return True

    ok("G4 redline: grid_fracs sum > 1.0 refuses to run",
       _raises({"staged_entry": {"grid_fracs": (0.5, 0.6),
                                 "add_triggers": (0.0, -0.05)}}))
    ok("G4 redline: non-positive frac refuses to run",
       _raises({"staged_entry": {"grid_fracs": (0.4, -0.1, 0.3),
                                 "add_triggers": (0.0, -0.05, -0.10)}}))
    ok("G4 redline: trigger/frac misalignment refuses to run",
       _raises({"staged_entry": {"grid_fracs": (0.4, 0.3, 0.3),
                                 "add_triggers": (0.0, -0.05)}}))
    ok("G4 redline: fracs sum == 1.0 exactly is legal (boundary)",
       not _raises({"staged_entry": {"grid_fracs": (0.5, 0.5),
                                     "add_triggers": (0.0, -0.05)}}))

    # ------------------------------------------------ G5: keyset discipline
    ok("G5 legacy 7-key metric set intact under the staged flag",
       {"annual_return", "sharpe", "max_drawdown", "win_rate",
        "profit_factor", "num_trades", "avg_hold_days"} <= set(m2))
    ok("G5 all 5 staged keys present when flag ON",
       staged_keys <= set(m2))

    # ------------------------------------------------ G6: guard drop + re-queue
    # tape constraint: with the day-2 add guard-blocked the cost stays 10.0
    # -> stop 9.2, so the day-2 close must sit ABOVE 9.2 (else the position
    # stop-losses out before any re-queue) yet below the k=1 trigger 9.5:
    # close day2 = 9.3.  k=1 re-queues, fills day3 open 8.8 (VWAP 9.4470,
    # stop 8.69); day3 close 8.95 clears the stop AND trips the k=2 level
    # (<=9.0) -> fills day4 open 8.7 (VWAP 9.2104); days 5+ hold at 9.35.
    idx24 = pd.date_range("2024-01-02", periods=N)
    buy_block = pd.Series(True, index=idx24)
    buy_block.iloc[2] = False          # day-2 open sealed: the add can't fill
    guard = {"buy": pd.DataFrame({"S": buy_block}, index=idx24)}
    px6 = _panel({1: 10.0, 3: 8.8, 4: 8.7, **_rng(5, N, 9.35)},
                 {1: 9.4, 2: 9.3, 3: 8.95, 4: 9.0, **_rng(5, N, 9.35)})
    r6 = run_backtest(px6, dict(HOLD_PARAMS), entry_signal=ent2,
                      exit_signal=ext2, fill_guard=guard, staged_entry=STAGED)
    m6 = r6["metrics"]
    exp_qty6 = 4000.0 + 30000.0 / 8.8 + 30000.0 / 8.7
    ok("G6 guard-blocked add open drops the tranche (num_adds_dropped == 1)",
       m6["num_adds_dropped"] == 1)
    ok("G6 the still-live level re-queues: both tranches end up filled",
       m6["num_adds_filled"] == 2)
    ok("G6 add drops are NOT entry drops (fill_guard_buy_dropped == 0)",
       m6.get("fill_guard_buy_dropped") == 0)
    ok("G6 re-queued adds filled at day3/day4 opens (hand-synthesized qty)",
       abs(r6["open_positions"][0]["quantity"] - round(exp_qty6, 2)) <= 0.01)

    # ------------------------------------------------ G7: stop follows the VWAP
    # staged: fill 5000 sh @10.0; add 5555.56 sh @9.0 -> VWAP 9.4737,
    # stop 8.7158 -> survives the day-2 close 8.9 (single-shot stop 9.2 would
    # NOT), stops at the day-3 close 8.6.  single-shot stops at day 2.
    px7 = _panel({1: 10.0, 2: 9.0},
                 {1: 9.4, 2: 8.9, 3: 8.6})
    staged2 = {"grid_fracs": (0.5, 0.5), "add_triggers": (0.0, -0.05)}
    r7s = run_backtest(px7, dict(HOLD_PARAMS), entry_signal=ent2,
                       exit_signal=ext2, staged_entry=staged2)
    r7l = run_backtest(px7, dict(HOLD_PARAMS), entry_signal=ent2,
                       exit_signal=ext2,
                       staged_entry={"grid_fracs": (1.0,),
                                     "add_triggers": (0.0,)})
    t7s = [t for t in r7s["trades"] if t["reason"] == "stop_loss"]
    t7l = [t for t in r7l["trades"] if t["reason"] == "stop_loss"]
    exp_vwap7 = 100000.0 / (5000.0 + 50000.0 / 9.0)
    exp_qty7 = 5000.0 + 50000.0 / 9.0
    ok("G7 staged stop fires (still live after averaging down)",
       len(t7s) == 1)
    ok("G7 staged stop fires ONE DAY LATER than single-shot (line moved to VWAP)",
       t7s and t7l and t7s[0]["date"] == str(DATES[3].date())
       and t7l[0]["date"] == str(DATES[2].date()))
    ok("G7 staged stop liquidates the FULL averaged position",
       t7s and abs(t7s[0]["qty"] - round(exp_qty7, 2)) <= 0.01)
    ok("G7 single-shot degenerate (fracs == (1.0,)) == legacy sizing, no adds",
       t7l and r7l["metrics"]["num_adds_filled"] == 0
       and abs(t7l[0]["qty"] - 10000.0) <= 0.01)
    ok("G7 staged exit pnl is measured against the VWAP (hand-synthesized)",
       t7s and abs(t7s[0]["pnl_rate"]
                   - round((8.6 - exp_vwap7) / exp_vwap7, 4)) <= 1e-3)

    # ------------------------------------------------ G8: window-end orphan
    # entry fills day22 open; the k=1 trigger fires at the FINAL close ->
    # queued with no tomorrow to fill -> honest drop.
    ent8, ext8 = _signals([21])
    px8 = _panel({}, {22: 9.6, 23: 9.4})
    r8 = run_backtest(px8, dict(HOLD_PARAMS), entry_signal=ent8,
                      exit_signal=ext8, staged_entry=STAGED)
    m8 = r8["metrics"]
    ok("G8 add queued at the final close never executes (honest drop)",
       m8["num_adds_dropped"] == 1 and m8["num_adds_filled"] == 0
       and m8["adds_per_entry"] == 0.0)
    ok("G8 the position itself survives to the window end",
       len(r8.get("open_positions", [])) == 1)

    n_fail = sum(1 for _, c in checks if not c)
    print(f"\np4b3_staged_selftest: {len(checks)-n_fail}/{len(checks)} PASS, "
          f"{n_fail} FAIL")
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
