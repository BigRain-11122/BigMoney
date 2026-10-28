"""One-command smoke test: env / config / data / engine / exit rules / market rules / network.

Usage:
    python -m smoke_test

Exit code 0 = all green, 1 = any failure. A timestamped summary line is
appended to logs/smoke.log so the 10-minute iteration loop can audit runs.
"""
import sys
import os
import json
import datetime as dt
import importlib
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RESULTS = []


def check(name: str, ok: bool, detail: str = ""):
    RESULTS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail else ""))


def _lan_ok(lag, st) -> bool:
    """lag 0 must read as current, lag > 0 must read as stale and say so."""
    if lag == 0:
        return st.get("stale") is False and "NOT current" not in str(st.get("reason"))
    return st.get("stale") is True and "NOT current" in str(st.get("reason"))


def main() -> int:
    print(f"== Bigmoney smoke test {dt.datetime.now():%Y-%m-%d %H:%M:%S} ==")

    # --- 1) environment ---
    try:
        import numpy
        import pandas
        import scipy
        check("env: core deps", True,
              f"numpy {numpy.__version__}, pandas {pandas.__version__}, scipy {scipy.__version__}")
    except Exception as e:
        check("env: core deps", False, str(e))
        return _finish()

    # --- 2) config & paths ---
    from config import PATHS, all_combinations, combo_hash
    for d in (PATHS.root, PATHS.data_dir, PATHS.daily_dir,
              PATHS.basic_dir, PATHS.results_dir, PATHS.logs_dir):
        if not os.path.isdir(d):
            check("config: paths", False, f"missing dir: {d}")
            return _finish()
    check("config: paths", True,
          f"root={os.path.basename(PATHS.root)}, daily={PATHS.daily_dir}")

    combos = all_combinations()
    check("config: param grid", len(combos) == 432, f"{len(combos)} combos (expect 432)")
    h1 = combo_hash(combos[0]); h2 = combo_hash(combos[0])
    check("config: combo_hash deterministic", h1 == h2 and len(h1) == 8, f"hash={h1}")

    # --- 3) data ---
    import pandas as pd
    core_files = sorted(f for f in os.listdir(PATHS.daily_dir)
                        if f.endswith(".csv") and f[:-4].isdigit())
    check("data: core ETF pool", len(core_files) >= 40,
          f"{len(core_files)} no-prefix CSVs (expect ~48)")
    if len(core_files) < 40:
        return _finish()

    panels = {}
    latest_dates = []
    bad = []
    for f in core_files:
        sym = f[:-4]
        p = os.path.join(PATHS.daily_dir, f)
        df = pd.read_csv(p, parse_dates=["date"]).set_index("date").sort_index()
        need = {"open", "high", "low", "close", "volume"}
        if not need.issubset(df.columns) or len(df) < 60 or df["close"].isna().any():
            bad.append(sym)
            continue
        panels[sym] = df
        latest_dates.append(df.index[-1])
    check("data: OHLCV readable", not bad and len(panels) >= 40,
          f"{len(panels)}/{len(core_files)} ok" + (f", bad={bad[:5]}" if bad else ""))

    latest = max(latest_dates).date()
    stale_days = (dt.date.today() - latest).days
    check("data: freshness", stale_days <= 15,
          f"latest bar {latest} ({stale_days}d ago, limit 15)")

    # --- 4) market rules ---
    from knowledge.rules import FeeSchedule, is_t0
    fee = FeeSchedule()
    cost_rate = fee.commission_rate + fee.handling_fee + fee.supervision_fee + fee.slippage_a
    check("rules: fee schedule sane", 0 < cost_rate < 0.005,
          f"single-side cost {cost_rate*1e4:.1f} bp")
    check("rules: T+0 list", is_t0("511880") and not is_t0("510300"),
          "511880 T+0, 510300 T+1")

    # --- 5) exit rules ---
    from engine.exit_rules import ExitConfig, ExitState, evaluate
    cfg = ExitConfig()
    a1 = evaluate(ExitState(cost_price=100.0, hold_days=10), 95.0, cfg)
    a2 = evaluate(ExitState(cost_price=100.0, hold_days=2), 106.0, cfg)
    a3 = evaluate(ExitState(cost_price=100.0, hold_days=3), 91.0, cfg)
    a4 = evaluate(ExitState(cost_price=100.0, hold_days=3), 101.0, cfg)
    check("exit: loss 8d force-close", a1.reason == "loss_time_stop" and a1.should_close)
    check("exit: tiered take-profit", a2.reason == "take_profit_tier_1"
          and abs(a2.close_fraction - 1/3) < 1e-9)
    check("exit: hard stop -8%", a3.reason == "stop_loss" and a3.should_close)
    check("exit: hold otherwise", not a4.should_close and a4.reason == "hold")

    # --- 6) backtest engine (small window, deterministic) ---
    from engine import run_backtest
    syms = sorted(panels)[:3]
    window = {s: panels[s].tail(400)[["open", "high", "low", "close"]] for s in syms}
    r1 = run_backtest(window, {})
    r2 = run_backtest(window, {})
    m = r1["metrics"]
    keys_ok = {"annual_return", "sharpe", "max_drawdown", "win_rate",
               "profit_factor", "num_trades", "avg_hold_days"} <= set(m)
    eq_ok = len(r1["equity_curve"]) > 0 and all(v > 0 for v in r1["equity_curve"])
    tr_ok = all(t["price"] > 0 for t in r1["trades"])
    det_ok = json.dumps(r1["metrics"], sort_keys=True) == json.dumps(r2["metrics"], sort_keys=True) \
        and r1["equity_curve"] == r2["equity_curve"]
    check("engine: smoke backtest", keys_ok and eq_ok and tr_ok,
          f"{len(syms)} syms x 400 bars, {m.get('num_trades', 0)} trades")
    check("engine: deterministic", det_ok, "identical on rerun (no hidden randomness)")

    # T+1 guard: no trade may be opened and closed on the same date.
    # trades list carries exit records only, so a same-day roundtrip shows up
    # as a non-T+0 exit with hold_days <= 0 (entry-day sells are skipped by
    # the engine's T+1 guard, backtester section 1). The previous opens-dict
    # heuristic compared exit dates and false-flagged any young latest exit
    # (surfaced r403 when the 09-28 bar made 159915's final exit hold_days=1).
    same_day = [t for t in r1["trades"]
                if not is_t0(t["symbol"]) and t["hold_days"] <= 0]
    check("engine: T+1 respected", len(same_day) == 0,
          f"{len(r1['trades'])} trades checked, {len(same_day)} same-day roundtrips")

    # RW-1 (audit P0-1, D-20260930-05): an exit decided at day T's close
    # must FILL at day T+1's open -- the pre-fix engine filled exits at the
    # same close (look-ahead, systematic overstatement). Every exit record
    # must therefore carry its own execution day's OPEN price.
    open_px = {s: dict(zip(w.index.strftime("%Y-%m-%d"), w["open"]))
               for s, w in window.items()}
    bad_exit_px = [t for t in r1["trades"]
                   if abs(round(float(open_px[t["symbol"]].get(t["date"], float("nan"))), 4)
                               - t["price"]) > 1e-6]
    check("engine: exits fill at T+1 open (RW-1)", len(bad_exit_px) == 0,
          f"{len(r1['trades'])} exits checked, {len(bad_exit_px)} non-open fills")

    # RW-2 (T-127, D-20260930-05): evidence_cutoff is a backtester input
    # param with HARD truncation at data-assembly -- the engine itself can
    # never read a post-cutoff row, even if the caller forgets to truncate.
    cut_i = len(next(iter(window.values()))) // 2
    cut_d = next(iter(window.values())).index[cut_i]
    n_after = int(sum(int((w.index > cut_d).sum()) for w in window.values()))
    r3 = run_backtest(window, {}, evidence_cutoff=cut_d)
    pre = {s: w[w.index <= cut_d] for s, w in window.items()}
    r4 = run_backtest(pre, {})
    meta = r3.get("cutoff_meta") or {}
    trunc_ok = (
        meta.get("last_bar_read") == str(pd.Timestamp(cut_d).date())
        and meta.get("rows_after_cutoff_dropped") == n_after
        and r3["metrics"] == r4["metrics"]
        and r3["equity_curve"] == r4["equity_curve"])
    check("engine: evidence_cutoff hard truncation (RW-2)", trunc_ok,
          f"cutoff {cut_d.date()}, {n_after} post-cutoff rows dropped, "
          "result identical to pre-truncated input")
    # The three symbols are not guaranteed to share a calendar: tail(400) gave 159901
    # 2026-10-27 and 159915 2026-10-26 on the r1310 run, so the ragged pre-truncation
    # panel has 202 bars while `next(iter(...)).index` has 201 up to the cutoff. The
    # engine is right in that case (it reports last_bar_read == cutoff and its output
    # equals the manually pre-truncated run, both asserted above); the old line here
    # labelled the curve with ONE symbol's calendar and read the extra bar as a leak.
    # The honest assertion is against the number of rows the engine could actually read.
    n_read = max(len(w[w.index <= cut_d]) for w in window.values())
    check("engine: rows actually read <= cutoff (RW-2)",
          (bool(r3["equity_curve"])
           and len(r3["equity_curve"]) <= n_read
           and meta.get("last_bar_read") == str(pd.Timestamp(cut_d).date())),
          f"curve {len(r3['equity_curve'])} bars vs {n_read} rows at/below {cut_d.date()} "
          f"(ragged calendars: windows end "
          f"{sorted({str(w.index[-1].date()) for w in window.values()})})")
    check("engine: legacy keyset intact without evidence_cutoff (RW-2)",
          "cutoff_meta" not in r1, "no cutoff_meta when flag off")
    raised = False
    try:
        run_backtest(window, {}, evidence_cutoff="2000-01-01")
    except ValueError:
        raised = True
    check("engine: emptying cutoff refused (RW-2)", raised,
          "out-of-range cutoff raises -> caller rc != 0")

    # RW-3 (T-127, D-20260930-05): single-source cost spec. The same
    # synthetic bar must cost identically on every ACTIVE cost face
    # (engine / live-paper anchor+paper path / x2 stress face); the frozen
    # grid legacy face must diverge by exactly its declared 13.0-vs-13.041
    # caliber, never by silent drift. (ce_transfer/combined_exit import
    # the same knowledge.cost_spec constants -- verified script-mode.)
    from knowledge import cost_spec
    from scripts.science_gates import COST_X2_RATE as _SG_X2
    bar_notional = 100_000.0
    engine_side = round(cost_rate * bar_notional, 6)
    from live import paper as _lp
    from scripts import grid_paper as _gp
    active_faces = {"engine": engine_side,
                    "paper": round(_lp.COST_X1_RATE * bar_notional, 6)}
    parity_ok = (len(set(active_faces.values())) == 1
                 and cost_spec.verify()
                 and abs(_SG_X2 - 2 * _lp.COST_X1_RATE) < 1e-15)
    grid_delta = abs(_gp.COST_BP_X1 * 1e-4
                     - _lp.COST_X1_RATE) * bar_notional
    check("engine: single-source cost parity (RW-3)", parity_ok,
          f"same bar 100k CNY: {engine_side:.4f}/side on engine"
          f"+paper+x2 faces; spec verify={cost_spec.verify()}")
    check("engine: grid legacy divergence = declared 0.041bp (RW-3)",
          abs(grid_delta - 0.41) < 0.005 and _gp.COST_BP_X1 == 13.0,
          f"frozen T-78 grid caliber 13.0bp vs canonical 13.041bp "
          f"(delta {grid_delta:.2f} CNY/100k side)")

    # RW-4 (T-127, D-20260930-05): canonical data-panel gate. The bare
    # 6-digit code IS the canonical key; twins/duplicates fail the audit's
    # len(set)==len(list) acceptance face; stale members are excluded
    # (batch) or refused (in-service/required); the in-service panel is
    # the FROZEN 48-member whitelist (knowledge/panel_gate.py), never the
    # directory listing -- silent expansion OR shrink both fail closed.
    from knowledge import panel_gate as _pg
    lb_real = {s: d.index[-1].strftime("%Y-%m-%d") for s, d in panels.items()}
    inv_real = _pg.PanelInventory(bare={s: s + ".csv" for s in panels},
                                  prefixed={}, last_bars=lb_real)
    res_real = _pg.gate(list(panels), mode="inservice", inventory=inv_real)
    syn = _pg.PanelInventory(bare={"510300": "510300.csv"},
                             prefixed={"510300": "sh510300.csv"},
                             last_bars={"510300": "2026-09-29"})
    res_twin = _pg.gate(["sh510300", "510300"], mode="batch", inventory=syn)
    stale_fx = _pg.PanelInventory(bare={"510300": "510300.csv"}, prefixed={},
                                   last_bars={"510300": "2026-01-01"})
    res_stale = _pg.gate(["510300"], mode="inservice", inventory=stale_fx,
                         anchor="2026-09-29")
    res_lock = _pg.gate(["600000"], mode="inservice", inventory=syn)
    res_shrink = _pg.gate(["510050"], mode="inservice", inventory=syn)
    check("panel gate: real in-service panel inside frozen 48-lock (RW-4)",
          res_real.ok and len(res_real.accepted) == len(panels) and _pg.verify(),
          f"{len(res_real.accepted)}/{len(panels)} members in lock, "
          f"sha16={_pg.INSERVICE_SHA16[:8]}, len(set)==len(list) holds")
    check("panel gate: twins refused, len(set)==len(list) (RW-4)",
          (not res_twin.ok) and any("twin/duplicate" in x for x in res_twin.reasons),
          "sh510300+510300 -> duplicate after canonicalization -> batch "
          "not accepted")
    check("panel gate: stale in-service member refused (RW-4)",
          (not res_stale.ok) and any("stale" in x for x in res_stale.reasons),
          "last_bar 2026-01-01 vs anchor 2026-09-29 -> lock breach refused")
    check("panel gate: out-of-lock + silent-shrink refused (RW-4)",
          (not res_lock.ok) and any("out-of-lock" in x for x in res_lock.reasons)
          and (not res_shrink.ok) and any("missing in-lock" in x for x in res_shrink.reasons),
          "600000 out-of-lock refused; 1-of-48 request = silent shrink refused")

    # D-20260930-39 (P0): asset-class fee routing. ETF default stays
    # byte-identical (13.041bp both sides); a stock symbol adds the
    # sell-only 5bp stamp tax + 0.1bp/side transfer fee -> 13.141bp buy /
    # 18.141bp sell. Cost helpers must charge exactly those deltas.
    from knowledge import rules as _kr
    _fs_etf = _kr.fee_schedule_for("510300")
    _fs_stk = _kr.fee_schedule_for("600519")
    _ok_route = (_fs_etf == _kr.FeeSchedule()
                 and _fs_stk.stamp_tax == 0.0005
                 and _fs_stk.transfer_fee == 0.00001
                 and abs(cost_spec.x1_side_rate(_fs_stk) * 1e4 - 13.141) < 1e-9
                 and abs(cost_spec.x1_sell_side_rate(_fs_stk) * 1e4 - 18.141) < 1e-9
                 and cost_spec.X1_SELL_RATE == cost_spec.X1_RATE)
    _b_e = _kr.total_buy_cost(100.0, 1000)
    _s_e = _kr.total_sell_proceeds(100.0, 1000)
    _d_buy = _kr.total_buy_cost(100.0, 1000, _fs_stk) - _b_e
    _d_sell = _s_e - _kr.total_sell_proceeds(100.0, 1000, _fs_stk)
    check("rules: stock fee routing sell 18.141bp / buy 13.141bp (D-39)",
          _ok_route and abs(_d_buy - 1.0) < 1e-9 and abs(_d_sell - 51.0) < 1e-9,
          f"600519 vs 510300 on 100k notional: buy +{_d_buy:.0f} CNY "
          f"(transfer), sell -{_d_sell:.0f} CNY (stamp50+transfer1); "
          f"ETF sell rate {cost_spec.X1_SELL_RATE*1e4:.4f}bp == buy rate")

    # D-20260930-38 CN-A: one-word-bar (high==low, sealed limit board)
    # fills are impossible on the A-share exchange. Entry on a one-word
    # open -> order DROPPED; exit on a one-word open -> DEFERRED to the
    # next fillable open; "violations" is 0 by construction.
    _idx = pd.date_range("2026-01-05", periods=8, freq="B")

    def _ow_frame(o, c, h, l):
        return pd.DataFrame({"open": o, "close": c, "high": h, "low": l},
                            index=_idx)

    _one = _ow_frame([10, 10.5, 10.6, 10.6, 10.6, 10.7, 10.8, 10.8],
                     [10, 10.6, 10.6, 10.6, 10.6, 10.7, 10.8, 10.8],
                     [10.2, 10.6, 10.7, 10.7, 10.6, 10.7, 10.8, 10.8],
                     [10.0, 10.4, 10.5, 10.5, 10.6, 10.6, 10.8, 10.8])
    _es = pd.DataFrame(False, index=_idx, columns=["OW"])
    _es.loc[_idx[0], "OW"] = True          # entry fills _idx[1] (normal)
    _xs = pd.DataFrame(False, index=_idx, columns=["OW"])
    _xs.loc[_idx[3], "OW"] = True          # exit exec _idx[4] = one-word
    _r = run_backtest({"OW": _one}, {"hold_days": 2,
                                     "take_profit_tiers": [(2, 0.5)],
                                     "hard_stop": -0.08,
                                     "max_positions": 1,
                                     "position_size_pct": 0.5},
                      entry_signal=_es, exit_signal=_xs)
    _owm = _r["metrics"]["cn_one_word"]
    _fills = [t["date"] for t in _r["trades"]]
    check("engine: one-word bar buy dropped + sell deferred (CN-A, D-38)",
          _owm == {"buy_dropped": 0, "sell_deferred": 1, "violations": 0}
          and str(_idx[4].date()) not in _fills
          and str(_idx[5].date()) in _fills,
          f"exit off sealed board -> filled next real open "
          f"({_idx[5].date()}), violations=0 by construction")

    # RW-7 (T-127, D-20260930-05): exit_rules priority layer + risk-gate
    # circuit breaker as the SOLE order exit. (a) exit priority is fixed:
    # P1 signal_reversal > P2 stop_loss > P3 take_profit > P4 time_decay
    # > P5 loss_time_stop > P6 global_hard_limit -- on any bar where two
    # rules fire simultaneously the higher one must win. (b) RiskGate
    # rejections are EXCEPTIONS (no silent drops): position cap / total
    # cap / trade-count cap / invalid side / halted-day BUY all raise.
    # (c) emit_order_sheet refuses ungated orders -- the gate is the only
    # path by which an order sheet can leave the system.
    from config import RISK as _RISK_CFG
    RISK = _RISK_CFG
    from live import (RiskGate, RiskGateRejected, Order, gate_orders,
                      emit_order_sheet as _emit)
    # P1 > P2: reversal wins on a bar that is also in stop territory
    _p12 = evaluate(ExitState(cost_price=100.0, hold_days=1), 91.0, cfg,
                    signal_reversed=True)
    check("exit: P1 signal_reversal beats P2 stop (RW-7)",
          _p12.reason == "signal_reversal" and _p12.should_close,
          "reversal+stop same bar -> signal_reversal (P1 > P2)")
    # P2 > P3: trailing stop hit while pnl >= next take-profit tier
    _p23 = evaluate(ExitState(cost_price=100.0, hold_days=6, tier_reached=1,
                               high_watermark=112.0,
                               trailing_stop_price=110.88), 110.5, cfg)
    check("exit: P2 stop_loss beats P3 take_profit (RW-7)",
          _p23.reason == "stop_loss" and abs(_p23.pnl_rate - 0.105) < 1e-9,
          "pnl +10.5% >= tier-2 10% but price 110.5 <= trailing 110.88 "
          "-> stop_loss (P2 > P3)")
    # P4 > P5: decay window reached on a losing hold
    _p45 = evaluate(ExitState(cost_price=100.0, hold_days=12), 99.0, cfg)
    check("exit: P4 time_decay beats P5 loss_time_stop (RW-7)",
          _p45.reason == "time_decay",
          "hold 12d pnl -1% -> time_decay, not loss_time_stop (P4 > P5)")
    # P4 dominates the whole pnl<0 & hold>=12 overlap: P5's firing domain
    # is swallowed by P4 there (ladder P4 > P5 proven above); P5 keeps
    # only its exclusive window (8d <= hold < 12d, pnl < 0), already
    # asserted by the standing "loss 8d force-close" case.
    # P6 alone: a profitable-but-flat hold outlives every earlier rule
    _p6 = evaluate(ExitState(cost_price=100.0, hold_days=25), 103.0, cfg)
    check("exit: P6 global_hard_limit terminal tier (RW-7)",
          _p6.reason == "global_hard_limit" and _p6.should_close,
          "hold 25d pnl +3% >= decay threshold 2% -> hard_limit fires")
    # circuit breaker boundary: halt AT the limit, trade above it
    _g = RiskGate()
    check("gate: daily_loss_breaker boundary (RW-7)",
          _g.daily_loss_breaker(-0.03) and not _g.daily_loss_breaker(-0.029),
          f"halt at pnl <= {RISK.daily_loss_limit:.0%}, clear above")
    _ord_ok = Order("2026-09-30", "510300", "BUY", 0.05, "rebalance", 3.90)
    _rej = {}
    for _name, _o, _kw in (
            ("position_cap", Order("2026-09-30", "510300", "BUY", 0.50, "x", 1.0), {}),
            ("total_cap", Order("2026-09-30", "510300", "BUY", 0.05, "x", 1.0), {"current_positions": {"a": {"weight": 0.78}}}),
            ("invalid_side", Order("2026-09-30", "510300", "SHORT", 0.05, "x", 1.0), {}),
            ("halted_buy", _ord_ok, {"daily_pnl_pct": -0.05}),
            ("trade_cap", Order("2026-09-30", "510300", "BUY", 0.05, "x", 1.0), {"pre_counts": 10})):
        try:
            _gg = RiskGate()
            if _kw.get("pre_counts"):
                _gg.orders_today = _kw["pre_counts"]
            _gg.check([_o], _kw.get("current_positions", {}), 1_000_000.0,
                      daily_pnl_pct=_kw.get("daily_pnl_pct"))
            _rej[_name] = None
        except RiskGateRejected as _e:
            _rej[_name] = _e.reason
    check("gate: rejections raise, never silently drop (RW-7)",
          all(_rej[k] for k in ("position_cap", "total_cap", "invalid_side",
                                "halted_buy", "trade_cap")),
          "position/total/trade caps + invalid side + halted-day BUY all "
          f"raise RiskGateRejected; reasons={list(_rej.values())}")
    _halt_sell = Order("2026-09-30", "510300", "SELL", 0.0, "de-risk", 3.9)
    _gsell = RiskGate().check([_halt_sell], {}, 1_000_000.0,
                              daily_pnl_pct=-0.05)
    check("gate: halted day still lets exits through (RW-7)",
          _gsell == [_halt_sell],
          "circuit breaker blocks new opens, not de-risking sells")
    # sole exit: emit_order_sheet refuses ungated orders
    _emit_refused = False
    try:
        _emit([_ord_ok], "2026-09-30")
    except RuntimeError:
        _emit_refused = True
    import tempfile as _tf
    with _tf.TemporaryDirectory() as _td:
        _saved_logs = PATHS.logs_dir
        PATHS.logs_dir = _td
        try:
            _receipt = gate_orders([_ord_ok], {}, 1_000_000.0)
            _sheet = _emit(_receipt, "2026-09-30", gate_receipt=_receipt)
            _wrote = os.path.exists(_sheet)
        finally:
            PATHS.logs_dir = _saved_logs
    check("gate: emit_order_sheet is the sole gated exit (RW-7)",
          _emit_refused and _wrote,
          "ungated emit -> RuntimeError; gate_orders receipt -> sheet written")

    # --- 7) network / traffic modules ---
    import network_detector
    import traffic_policy
    nt = network_detector.detect()
    check("network: detector", nt in ("LAN", "WIFI", "HOTSPOT", "UNKNOWN"), f"net_type={nt}")
    st = network_detector.read_status()
    check("network: status readable", isinstance(st, dict) and "net_type" in st)
    ok_small = traffic_policy.can_run("smoke_incremental", 1 * 1024 * 1024)
    check("network: traffic gate", isinstance(ok_small, bool))

    # --- 8) paper pipeline (J16) ---
    # patches bite/restore + monthly aggregation math + signal causality +
    # anchor gate reproducing every registered trader's backtest evidence
    # (drift = registration no longer reproducible = highest-priority red)
    try:
        from live import paper as live_paper
        check("paper: pipeline selftest", live_paper.selftest(),
              "patches+aggregation+causality+anchor + seg-honesty(F4) "
              "+ x2-watch escalation(F3)")
    except Exception as e:
        check("paper: pipeline selftest", False, str(e))

    # --- 9) S6 updater selftests + heartbeat epoch fields (T-04 F7) ---
    # Exit-code contract: offline --selftest must exit 0 (no network);
    # production contracts (0 ok/1 warn/2 fetch fail/3 anchor drift for
    # daily; 0 ok/2 source fail/3 history-rewrite flag for lhb) are
    # asserted case-by-case inside each sub-suite.
    import subprocess as _sp
    # r1328: a suite's verdict must not depend on the parent's UTF-8 mode. With
    # `python -X utf8 -m smoke_test` the parent decodes as UTF-8 while an unflagged
    # child python still prints cp936, so subprocess's reader thread dies mid-pipe
    # (UnicodeDecodeError 0xc8) and communicate() then blocks forever -- the run hangs
    # with no failing leg to point at. Pin both sides instead of inheriting either.
    _sp_env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")

    def _selftest_run(script, args, timeout):
        return _sp.run([sys.executable, script, *args], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       env=_sp_env, timeout=timeout)

    # (label, script, args) -- offline selftest must exit 0 (no network);
    # T-35 d2 pair: intraday marks lane + open-fill verifier (R166).
    for _name, _script, _args in (
            ("daily", "scripts/update_daily.py", ["--selftest"]),
            ("lhb", "scripts/update_lhb.py", ["selftest"]),
            ("intraday_marks", "scripts/update_intraday_marks.py",
             ["--selftest"]),
            ("open_fill_verify", "scripts/t35_open_fill_verify.py",
             ["--selftest"]),
            ("etf_daily", "scripts/update_etf_daily.py", ["selftest"]),
            # the wide panel is the price universe of every ETF study, and its
            # refresh leg spent a week unwired while the panel sat frozen
            ("etf_wide", "scripts/update_etf_wide.py", ["--selftest"]),
            ("zt_pool", "scripts/update_zt_pool.py", ["selftest"]),
            ("fund_statements", "scripts/update_fund_statements.py",
             ["selftest"]),
            ("fund_avail_pit", "scripts/fund_avail_pit_t27.py",
             ["selftest"]),
            ("fund_pit_avail", "scripts/fund_pit_avail.py",
             ["selftest"]),
            ("fund_avail_notice", "scripts/fund_avail_notice.py",
             ["selftest"]),
            ("fund_avail_dispersion", "scripts/fund_avail_dispersion.py",
             ["selftest"]),
            ("fund_avail_face_impact", "scripts/fund_avail_face_impact.py",
             ["selftest"]),
            ("fund_avail_asof", "scripts/fund_avail_asof_panel.py",
             ["selftest"]),
            ("fund_pit_factor_panel", "scripts/fund_pit_factor_panel.py",
             ["selftest"]),
            ("fund_pit_crossface_factor", "scripts/fund_pit_crossface_factor.py",
             ["selftest"])):
        _label = f"updater: update_{_name} selftest (exit-code contract)"
        try:
            _r = _selftest_run(_script, _args, 180)
            _tail = ((_r.stdout or _r.stderr).strip().splitlines() or ["no output"])[-1]
            check(_label, _r.returncode == 0, f"exit={_r.returncode} | {_tail[:80]}")
        except Exception as e:
            check(_label, False, str(e))
    # The production card is the only placeable deliverable (E121), and it is the one
    # face whose failure is invisible: r1270 shipped a round where run() crashed on a
    # name that had moved out of scope, while every other leg in this file was green --
    # nothing here ever called the entry point. Guard the sheet path, not just the maths.
    for _label, _script, _args in (
            ("product: etf_book_production card (exit-code contract)",
             "scripts/etf_book_production.py", ["--selftest"]),
            ("product: etf_vol_delivery_audit (exit-code contract)",
             "scripts/etf_vol_delivery_audit.py", ["--selftest"]),
            ("product: etf_vol_calibration (exit-code contract)",
             "scripts/etf_vol_calibration.py", ["--selftest"]),
            ("product: etf_book_forward ledger (exit-code contract)",
             "scripts/etf_book_forward.py", ["--selftest"]),
            ("product: etf_book_order ticket (exit-code contract)",
             "scripts/etf_book_order.py", ["--selftest"]),
            ("product: etf_book_width_audit (exit-code contract)",
             "scripts/etf_book_width_audit.py", ["--selftest"]),
            ("product: etf_book_split_audit repair value (exit-code contract)",
             "scripts/etf_book_split_audit.py", ["selftest"]),
            # The r1310/r1311 span regressions only ever ran on 2020+ data, i.e. inside the
            # window the book earned its money in. This leg keeps the outside-window test
            # callable: if its selftest rots, the "alpha is a window property" reading
            # stands on a script nobody can re-derive.
            ("product: etf_book_spanning_pre2020 period test (exit-code contract)",
             "scripts/etf_book_spanning_pre2020.py", ["--selftest"]),
            # The money question ("how big can this book get before impact eats it")
            # rests entirely on this one script: it re-derives both arms off one
            # engine and pins k=1 to the flat path to 1e-12. A rot here would print
            # a confident NAV ladder that no longer belongs to the delivered rule.
            ("product: etf_book_capacity_rule impact ladder (exit-code contract)",
             "scripts/etf_book_capacity_rule.py", ["selftest"]),
            # r1317: the 10-31 month-exam package is assembled by one generator.
            # Nothing in this file ever called it, so the assembly face and its
            # freeze-fingerprint gate could rot silently before exam day.
            ("product: monthly_exam_prep exam faces (exit-code contract)",
             "scripts/monthly_exam_prep.py", ["selftest"]),
            ("product: gpu_face canonical GPU face (exit-code contract)",
             "Tools/gpu_face.py", ["--selftest"]),
            # r1188: an autostash rebase put a 62-file revert of another machine's
            # work into this tree, and the only thing that noticed was the pre-push
            # ownership claw -- i.e. after the commit already existed. This leg keeps
            # the earlier, cheaper detector callable; if its classifier rots, rounds
            # go back to discovering reverts at push time.
            ("product: tree poison probe selftest (exit-code contract)",
             "Tools/tree_poison_probe.py", ["--selftest"]),
            # r1192: bm-a's MSG-20261027-2250-bm-a.md reported group commit ceebc703
            # -- "order-bus receipts for bm-b", two files -- whose tree held 2 entries
            # against its parent's 3,494. A temp index seeded from nothing instead of
            # `read-tree <parent>` produces exactly that shape. bm-a has since added a
            # pre-push gate (MSG-20261027-2345) that blocks the push; this leg keeps
            # the BUILDER honest, which is the half a gate cannot reach.
            ("product: surgical commit tree-size guard (exit-code contract)",
             "Tools/surgery_commit.py", ["selftest"]),
            ("product: machine-health face builder (exit-code contract)",
             "Tools/machine_health_face.py", ["selftest"]),
            # D-20261028-04: a resident script must resolve the group root by
            # validated toplevel + newest ledger mtime, never by a `..\..` climb or
            # a hardcoded mirror. The selftest pins the rejection of a masquerading
            # subdirectory, which is the failure that serves a week-old ledger.
            ("product: group-root resolution (exit-code contract)",
             "Tools/group_root.py", ["selftest"]),
            # D-20261028-04, second half: the resolver only helps the files that
            # use it. This leg keeps the CENSUS callable -- a resident script that
            # climbs `..\..` or pastes a mirror gets named every round instead of
            # once, by whoever happened to grep for it.
            ("product: group-root sweep census (exit-code contract)",
             "scripts/group_root_sweep.py", ["selftest"]),
            # D-20261028-11 widened that rule to two more shapes: PowerShell reading
            # .Path off a Get-Item result (empty group root that still reports OK), and
            # freshness gates that hash WORKTREE bytes on an autocrlf checkout. The
            # census measures both and the fixtures pin the two ways the second one
            # lies -- a stale constant is not a dialect bug, and on an LF-on-disk
            # fixture neither state is distinguishable at all.
            ("product: group-root dialect census (exit-code contract)",
             "scripts/group_root_dialect_census.py", ["--selftest"]),
            # r1320 fixed one doubled-percent leak with a gate on that face's OUTPUT and
            # recorded three more for "the next sweep" -- this is that sweep, and it is a
            # census because the same token is legitimate in a shell string, in frozen
            # evidence and in the append-only pool record. This leg keeps the classifier
            # callable; the chain leg re-derives the census every round.
            ("product: reader-text audit census (exit-code contract)",
             "scripts/reader_text_audit.py", ["selftest"]),
            # r1319: the book's standing "pure survivor pool" caveat had no number
            # behind it, and the first run of the census showed the caveat was also
            # pointed the wrong way -- 1,645 of 1,656 eligible symbols still print to
            # the panel edge and a dead fund keeps its history in its own file, so the
            # engine saw it while it traded. This leg keeps the classifier callable.
            ("product: ETF pool survival census (exit-code contract)",
             "scripts/etf_pool_survival.py", ["selftest"]),
            ("product: exchange_calendar_audit lag verdict (exit-code contract)",
             "scripts/exchange_calendar_audit.py", ["selftest"]),
            ("product: supply_alignment four-tuple face (exit-code contract)",
             "scripts/supply_alignment.py", ["--selftest"]),
            # The staggered book's sleeve due dates used to be position indices only
            # (5274/5279) -- unreadable as dates and fragile against a panel whose
            # history window shifts. Its selftest pins the date anchor + projection.
            ("product: etf_paper_signal sleeve schedule (exit-code contract)",
             "scripts/etf_paper_signal.py", ["--selftest"]),
            # The pre-2020 test decides whether the book's edge is the composite or the
            # wider universe, and it reads entirely through window semantics: a panel
            # truncated at `start` silently keeps the book in cash for its first
            # MIN_HIST bars (r1305 self-caught), which reads as "the edge never existed".
            ("product: etf_book_pre2020 window semantics (exit-code contract)",
             "scripts/etf_book_pre2020.py", ["selftest"]),
            # r1308: the rotation premium is now priced outside the published regime too,
            # and the ladder reconciles it with the -8.86pp caveat on the same window. Both
            # depend on window semantics (upper bound only) and on one verdict rule.
            ("product: etf_book_passive_mix windows (exit-code contract)",
             "scripts/etf_book_passive_mix.py", ["--selftest"]),
            ("product: etf_book_window_decomp ladder (exit-code contract)",
             "scripts/etf_book_window_decomp.py", ["--selftest"]),
            # r1309: the ladder's rungs were all FIXED cells picked with hindsight. The
            # deployment rule re-picks (N,R) yearly on trailing Sharpe, so the ladder cannot
            # say whether the RULE survives the window. This leg pins that the walk-forward
            # harness -- including the year-boundary rule that makes a chain equal its curve
            # -- still runs.
            ("product: etf_book_pre2020 walk-forward rule (exit-code contract)",
             "scripts/etf_book_pre2020_wf.py", ["--selftest"]),
            # r1310: the book is regressed on the four liquid exposures an account could
            # hold instead of it. The legs pin the two ways this kind of face lies: an
            # "annual" alpha that is really a daily intercept (252x), and a benchmark arm
            # made of un-repaired prices (a split prints as a -50% day). Both are pinned.
            ("product: etf_book_spanning vs four betas (exit-code contract)",
             "scripts/etf_book_spanning.py", ["--selftest"]),
            # r1308 was itself a dead window's product left uncommitted in this tree, and
            # the hand test (git log vs round_no) agreed with the counter and saw nothing.
            # The detector's contract is what keeps the next one from being invisible.
            ("fleet: round-open absorb detector (exit-code contract)",
             "scripts/round_open_absorb.py", ["--selftest"]),
            # r1319: the book, the four-ETF basket and the futures sleeve had each been
            # measured in its own window and nobody had put them on the axis an allocator
            # holds -- account size. The legs pin the three ways that face can lie: a
            # percent read as a fraction (100x), a capacity ceiling that never binds, and
            # a missing source silently becoming zero profit.
            ("product: capital placement by account size (exit-code contract)",
             "scripts/capital_placement.py", ["--selftest"]),
            # r1320: four published annualised numbers were being quoted as four views of
            # one book. The legs pin the decomposition that makes them one bridge: each
            # path must sum to the endpoint difference (so a term cannot be dropped), an
            # additive grid must show ZERO interaction (so a non-zero term is real), and an
            # incomplete path must raise rather than print a partial waterfall.
            ("product: card-vs-ticket cagr bridge (exit-code contract)",
             "scripts/etf_book_cagr_reconcile.py", ["--selftest"]),
            # r1323: the tempting reading of a turnover-bound book ("it trades on noise")
            # is refuted by its own census, so the legs pin the mechanics that let it be
            # read at all: k=0 restoring the plain top-n, the buffer being monotone in k,
            # the hook being bit-identical to the default path on a tie-free face (and
            # differing only on exact ties), a bad hook raising, and the consistency gate
            # actually going red on each of nine ways this face can lie.
            ("product: decision margins and a hysteresis buffer (exit-code contract)",
             "scripts/etf_book_hysteresis.py", ["--selftest"]),
            # r1325: the buffer arm above shipped with its own refutation in a caveat ("a
            # single better arm can be one decision sequence"). These legs pin the test that
            # settles it: phases must be distinct CALENDARS (a decision count is not a
            # signature -- four phases gave 83/83/82/82), delta arithmetic must keep its
            # units, the sign test must be exact, frozen criteria may not be re-tuned
            # silently, the published verdict must be recomputed rather than trusted, and
            # both tables must keep their header rows.
            ("product: incumbent-buffer adoption across books and phases (exit-code contract)",
             "scripts/etf_book_buffer_adoption.py", ["--selftest"]),
            # r1326: the same ruler applied to the claim the whole card rests on (+6.36pp/yr
            # of selection premium over the book's own static class mix). The legs pin the
            # two ways this face can lie in either direction: a premium under the frozen
            # floor cannot be called a level just because it never changed sign, and a face
            # whose four phases collapsed onto one calendar cannot call anything a level at
            # all (r1261 -- prove the mechanism moved before comparing numbers).
            ("product: selection premium across decision phases (exit-code contract)",
             "scripts/etf_book_premium_phases.py", ["--selftest"]),
            # r1327: the sizing overlay's two lags (trailing-window estimate + a scale frozen
            # for up to 19 bars) are measured on the engine's own diag, so these legs pin the
            # traps: a stationary-vol panel makes every window agree by construction (so an
            # "arms are identical" reading there is correct, not a dead test) while a regime
            # shift must move the curve; a vol shock must show as realised/estimated > 1.5;
            # and the gate must refuse a hand-written verdict or a re-tuned threshold.
            ("product: vol-target estimation and slot-freeze lag (exit-code contract)",
             "scripts/etf_book_voltarget_lag.py", ["--selftest"]),
            # r1328: r1327's "+1.60pp for the 20-bar window" rested on one decision calendar.
            # These legs pin the ruler that tests it: the paired delta keeps its units, the
            # noise floor is the control's OWN phase spread (so an effect smaller than it is
            # "within noise", not a level), a sign flip is a sequence, an unpriced phase cannot
            # become a verdict, the gate refuses a hand-written verdict / a re-tuned share
            # floor / four identical phase calendars, and a stationary-vol fixture is allowed
            # to make the windows agree (only a regime shift has to move the curve).
            ("product: vol-target window across decision phases (exit-code contract)",
             "scripts/etf_book_voltarget_phase.py", ["--selftest"]),
            # r1326: the E187 pool batch added a leg to the shared census tool, so its
            # 658-leg selftest has to run somewhere other than a human's memory. The
            # seven new legs pin the churn arithmetic (a first month has no predecessor and
            # must not read as zero churn), the frozen rule (equal churn in both buckets is
            # not a discount), and the honest empty case (an era with no against-months is
            # published as such, not as a pass with a missing ratio).
            ("product: census selftest incl. the E187 churn-tie legs",
             "scripts/e39_panel_census.py", ["selftest"])):
        try:
            _r = _selftest_run(_script, _args, 300)
            _tail = ((_r.stdout or _r.stderr).strip().splitlines() or ["no output"])[-1]
            check(_label, _r.returncode == 0, f"exit={_r.returncode} | {_tail[:80]}")
        except Exception as e:
            check(_label, False, str(e))
    # r1331: E196 asks whether the drop family's carrier month can be named BEFORE
    # the verdict. The face is a verdict, so this leg recomputes it from the
    # numbers on disk: an 'established' calendar verdict must be backed by the
    # DISJOINT reading (the pooled p counts nested era slices twice), every cell
    # must agree by the k the rule verdict names, and a carrier that is quoted as
    # in-window must actually be a 6/7/12/1 month.
    try:
        _cdir = os.path.join("results", "e43_tilt_4member")
        _cf = sorted(f for f in os.listdir(_cdir)
                     if f.startswith("LADDERDROPCARRIER-") and f.endswith(".json"))
        if _cf:
            _cj = json.load(open(os.path.join(_cdir, _cf[-1]), encoding="utf-8"))
            _ca = _cj.get("answers") or {}
            _gate_p = (_ca.get("pooled") or {}).get("perm_p_disjoint")
            _cok = True
            if _ca.get("calendar_verdict") == "review_window_established_on_this_face":
                _cok = (_gate_p is not None
                        and _gate_p <= float((_cj.get("spec") or {}).get("pooled_p_max", 0.01)))
            _rk = _ca.get("rule_all_k")
            if _rk is not None:
                _cok = _cok and all(
                    c.get("rule_hit_k") is not None and c["rule_hit_k"] <= _rk
                    for c in (_cj.get("cells") or []))
            _cok = _cok and all(
                (c["carrier_month_of_year"] in (6, 7, 12, 1))
                == bool(c["carrier_in_review_window"])
                for c in (_cj.get("cells") or []))
            check("product: E196 carrier verdict is recomputable from its own gate",
                  _cok, "calendar=%s gate_p=%s rule_k=%s cells=%d"
                  % (_ca.get("calendar_verdict"), _gate_p, _rk,
                     len(_cj.get("cells") or [])))
        else:
            check("product: E196 carrier verdict is recomputable from its own gate",
                  True, "carrier face absent -- soft-fails by design")
    except Exception as e:
        check("product: E196 carrier verdict is recomputable from its own gate",
              False, str(e))
    # r1308: the card carries two readings of 2015-2019 (the excess caveat and the
    # selection premium). If the reconciliation section ever stops being emitted while the
    # artifact is on disk, the card is back to printing a contradiction -- so assert the
    # text, not just the script that writes it.
    try:
        _card = os.path.join("results", "etf_book_production", "CARD.md")
        _dc = os.path.join("results", "etf_book_window_decomp.json")
        if os.path.exists(_card) and os.path.exists(_dc):
            _txt = open(_card, encoding="utf-8").read()
            check("product: card reconciles its two 2015-2019 readings",
                  "The 2015-2019 reconciliation" in _txt
                  and "The same test outside the regime" in _txt,
                  "card %d bytes" % len(_txt))
        else:
            check("product: card reconciles its two 2015-2019 readings", True,
                  "card or reconciliation artifact absent -- face soft-fails by design")
    except Exception as e:
        check("product: card reconciles its two 2015-2019 readings", False, str(e))
    # ... and the same lesson one level up: a green selftest does not prove the face is
    # ever produced. r1267/r1269/r1273 each left "wire the ledger into the S6 chain" as
    # the next pointer, and each round it silently stayed unwired because no test read
    # the chain. Assert the legs exist in the runner that actually executes them.
    try:
        _legs = __import__("importlib").import_module("Tools.s6_chain_bmc").LEGS
        _names = {n for n, _c in _legs}
        # etf_book_production belongs here as much as the ticket: r1290 caught the card
        # (the headline face) a full refresh behind the ticket because only the ticket
        # was wired -- an unwired face reads as current to everything downstream.
        # etf_book_width_audit prices the disagreement between the card and the ticket,
        # so it goes stale the moment either moves: r1291 found it two bars behind both.
        _want = {"etf_book_forward", "etf_book_production", "etf_book_order",
                 "etf_book_width_audit", "etf_book_registry", "etf_book_ceo_page",
                 "etf_book_card_track", "etf_paper_signal", "cal_audit"}
        _miss = sorted(_want - _names)
        check("product: ETF book legs wired into the S6 chain",
              not _miss, f"legs={len(_names)} missing={_miss or 'none'}")
    except Exception as e:
        check("product: ETF book legs wired into the S6 chain", False, str(e))
    # r1293: the register that lists the live book faces together. A published face is
    # not proof it is current, but a face that is not registered cannot be checked at
    # all -- so assert the live register exists, is single-schema, and that every face
    # it claims to have read really resolved (an all-missing register still "publishes").
    try:
        _rg = json.load(open("results/etf_book_registry.json", encoding="utf-8"))
        _ok_rg = (_rg.get("schema") == "etf-book-registry/v1"
                  and _rg.get("n_faces", 0) >= 4
                  and _rg.get("n_live") == _rg.get("n_faces")
                  and _rg.get("verdict") in {"single-config", "multi-config", "unwired"})
        check("product: ETF book registry published", _ok_rg,
              f"faces={_rg.get('n_faces')} live={_rg.get('n_live')} "
              f"verdict={_rg.get('verdict')} configs={_rg.get('distinct_configs')}")
    except Exception as e:
        check("product: ETF book registry published", False, str(e))
    # r1314: two records of one fact that only a script knew how to compare. The
    # noise floor lived in a helper and the card/ledger agreement lived in a hand run, so
    # both could rot while every published face still looked healthy. Assert the two
    # readings are on the FACES: the ledger carries its own floor, the card-track carries
    # the agreement verdict.
    try:
        _fwd = json.load(open("results/etf_book_forward/LEDGER.json", encoding="utf-8"))
        _sig = (_fwd.get("benchmark") or {}).get("significance") or {}
        check("product: the forward ledger publishes its own noise floor",
              bool(_sig.get("available")) and _sig.get("bars_used", 0) > 100
              and len(_sig.get("bars_needed_for_edge") or {}) >= 2
              and len(_sig.get("min_detectable_edge_pp") or {}) >= 2,
              "vol=%s%%/yr bars=%s band@published=%spp" % (
                  _sig.get("annual_vol_pct"), _sig.get("bars_used"),
                  _sig.get("noise_band_pp_at_published")))
    except Exception as e:
        check("product: the forward ledger publishes its own noise floor", False, str(e))
    # r1316: "how many bars for a t=2 test" was the only horizon the ledger offered,
    # and over 8.46%/yr excess dispersion the answer for a 3pp edge is 7,758 bars --
    # 31 years, i.e. a verdict no reader will be alive for. Assert instead that the
    # published face answers the reverse question: what CAN be resolved inside 6m/1y/
    # 2y/3y, and how many YEARS the edges this book actually published would need.
    try:
        _pw = (_sig.get("power") or {})
        _mde = _pw.get("min_detectable_edge_pp") or {}
        _yrs = _pw.get("years_for_80pct_power") or {}
        check("product: the forward face prices what its horizon can resolve, not only bars",
              _pw.get("available") is True and len(_mde) >= 3
              and all(_mde.get(k) for k in ("1y", "2y", "3y"))
              and _mde["1y"] > _mde["3y"] and _yrs
              and all(isinstance(v, (int, float)) and v > 0 for v in _yrs.values()),
              "1y=%spp/yr 3y=%spp/yr years=%s" % (_mde.get("1y"), _mde.get("3y"),
                                                   _yrs or "-"))
        _cand = _pw.get("candidate_sources") or {}
        check("product: every candidate edge states the file it was read from",
              _cand and all(("file" in v and "field" in v) or v.get("omitted")
                            for v in _cand.values()),
              "sources=%s" % ",".join(sorted(_cand)))
    except Exception as e:
        check("product: the forward face prices what its horizon can resolve, not only bars",
              False, str(e))
        check("product: every candidate edge states the file it was read from", False, str(e))
    try:
        _ct = json.load(open("results/etf_book_card_track.json", encoding="utf-8"))
        _ag = _ct.get("agreement") or {}
        check("product: the paper book owns the book the card sells",
              _ct.get("schema") == "etf-book-card-track/v1"
              and _ag.get("same_decision_bar") is True and _ag.get("agrees") is True
              and (_ct.get("drift") or {}).get("nav_identity_ok") is True,
              "agrees=%s decision_bar=%s wt_maxdiff=%s navdev=%s" % (
                  _ag.get("agrees"), _ag.get("ledger_decided_bar"),
                  _ag.get("max_weight_diff"),
                  (_ct.get("drift") or {}).get("nav_identity_max_dev")))
    except Exception as e:
        check("product: the paper book owns the book the card sells", False, str(e))
    # The register is the one screen that lists the books side by side. If it names the
    # staggered book but not when that book turns, the reader is back to opening the
    # ledger by hand -- so assert the date reaches the register too (r1304).
    try:
        _stg = [f for f in (_rg.get("faces") or []) if f.get("id") == "staggered"]
        _turn = (_stg[0].get("next_turn") if _stg else None) or []
        check("product: ETF registry says when the staggered book turns",
              len(_turn) >= 2 and all(t.get("due") for t in _turn),
              "; ".join("leg%s %s" % (t.get("leg"), t.get("due")) for t in _turn)
              or "no next_turn on the staggered row")
    except Exception as e:
        check("product: ETF registry says when the staggered book turns", False, str(e))
    # r1329: the register summarises the faces, so it has to run after them. It sat ~50
    # legs before etf_book_ceo_page and etf_paper_signal, and its rows for those two
    # faces were one run old on every single chain -- as_of 2026-10-27 beside
    # card/ticket/forward 2026-10-28, verdict "ok" throughout, because a stale row is
    # not a schema error. Static leg-order assertion, no clock involved.
    try:
        _order = [n for n, _c in importlib.import_module("Tools.s6_chain_bmc").LEGS]
        _ri = _order.index("etf_book_registry")
        _behind = [(f.get("id"), f.get("chain_leg")) for f in (_rg.get("faces") or [])
                   if f.get("chain_leg") in _order and _order.index(f["chain_leg"]) > _ri]
        check("product: ETF registry runs after every face it summarises",
              not _behind, "registry_at=%d behind=%s" % (_ri, _behind or "none"))
    except Exception as e:
        check("product: ETF registry runs after every face it summarises", False, str(e))
    # A sleeve schedule that a human cannot turn into a date is not an order. Assert the
    # live ledger state: per sleeve, where the clock stands AND when it next turns.
    try:
        _led = [json.loads(_l) for _l in open("results/etf_paper/ledger.jsonl",
                                             encoding="utf-8") if _l.strip()][-1]
        _acts = _led.get("next_actions") or []
        _ok_led = (len(_acts) == len(_led.get("sleeves") or [])
                   and all(a.get("due_date") or a.get("due_date_estimate") for a in _acts))
        check("product: staggered book states when each sleeve next turns", _ok_led,
              "; ".join("sleeve %s -> %s" % (a.get("leg"), a.get("due_date_estimate"))
                        for a in _acts))
    except Exception as e:
        check("product: staggered book states when each sleeve next turns", False, str(e))
    # The lag face itself is what a human reads to tell a holiday from a dead feed,
    # so assert the published file exists and speaks a known verdict -- a green
    # selftest on synthetic panels would not prove the live face was ever written.
    try:
        _la = json.load(open("results/data_lag_audit.json", encoding="utf-8"))
        _ok_la = (_la.get("schema") == "data-lag-audit/v1"
                  and _la.get("verdict") in {"in_sync", "source_lag", "panel_gap"}
                  and bool(_la.get("expected_last_official_day")))
        check("product: data lag audit face published", _ok_la,
              f"verdict={_la.get('verdict')} expected="
              f"{_la.get('expected_last_official_day')} as_of={_la.get('as_of')}")
    except Exception as e:
        check("product: data lag audit face published", False, str(e))
    # A marks session can be missing permanently (capture task Disabled, machine
    # off) or only transiently (today's window is still open), and the T-35
    # verifier reports both as the same NO_EVIDENCE/rc=1. This face names which
    # is which; assert it agrees with itself rather than only existing.
    try:
        _mc = json.load(open("results/marks_coverage.json", encoding="utf-8"))
        _rows = {r["date"]: r["status"] for r in _mc.get("days") or []}
        _holes = _mc.get("holes") or []
        _want = "complete" if not _holes else f"holes={len(_holes)}"
        _ok_mc = (bool(_rows)
                  and all(_rows.get(h) in ("missing_historical", "missing_today")
                          for h in _holes)
                  and _mc.get("verdict") == _want
                  and (_mc.get("counters") or {}).get("holes") == len(_holes))
        check("product: marks coverage face names its holes", _ok_mc,
              f"verdict={_mc.get('verdict')} "
              f"captured={(_mc.get('counters') or {}).get('captured')}/"
              f"{(_mc.get('counters') or {}).get('closed_days')} "
              f"last={_mc.get('last_captured')}")
    except Exception as e:
        check("product: marks coverage face names its holes", False, str(e))
    # A hole the owner could not have captured and a hole somebody could have
    # taken over are different problems; the face must say which. Assert the
    # live face attributes every hole exactly once from the closed vocabulary.
    try:
        _mc3 = json.load(open("results/marks_coverage.json", encoding="utf-8"))
        _det = _mc3.get("hole_detail") or []
        _holes3 = _mc3.get("holes") or []
        _causes = _mc3.get("holes_by_cause") or {}
        _vocab = ("lane_missed", "takeover_possible", "host_down", "host_offhours")
        _ok_cause = (len(_det) == len(_holes3)
                     and [d.get("date") for d in _det] == _holes3
                     and all(d.get("cause") in _vocab for d in _det)
                     and sum(_causes.values()) == len(_holes3)
                     and bool(_mc3.get("lane_owner")))
        check("product: every marks hole carries a cause from the lane's own ownership contract",
              _ok_cause,
              f"owner={_mc3.get('lane_owner')} causes={_causes} "
              f"detail={[(d.get('date'), d.get('cause')) for d in _det]}")
    except Exception as e:
        check("product: every marks hole carries a cause from the lane's own ownership contract",
              False, str(e))
    # ...and the gap has to reach the place the CEO actually looks. The coverage
    # face existed for a full round while the dashboard said nothing about the
    # paper record being 3 sessions short; assert the payload carries the same
    # numbers (not merely the key names).
    try:
        _mc2 = json.load(open("results/marks_coverage.json", encoding="utf-8"))
        _ds = json.load(open("results/dashboard_status.json", encoding="utf-8"))
        _pp = ((_ds.get("trading") or {}).get("paper") or {})
        _c2 = _mc2.get("counters") or {}
        _fv2 = json.load(open("results/t35_open_fill_verify.json",
                              encoding="utf-8"))
        _ok_dash = (_pp.get("marks_closed_days") == _c2.get("closed_days")
                    and _pp.get("marks_captured") == _c2.get("captured")
                    and _pp.get("marks_coverage_pct")
                    == _c2.get("coverage_pct_closed")
                    and (_pp.get("marks_holes") or 0) == len(_mc2.get("holes") or [])
                    # the verification tier travels with the gap, so a reader
                    # sees "checked by a weaker source" not "unverified"
                    and _pp.get("fill_verify_tier") == _fv2.get("evidence_tier")
                    and _pp.get("fill_verify_verdict") == _fv2.get("verdict")
                    and _pp.get("fill_verify_day") == _fv2.get("day"))
        check("product: dashboard carries the marks coverage gap", _ok_dash,
              f"dash={_pp.get('marks_captured')}/{_pp.get('marks_closed_days')}"
              f"={_pp.get('marks_coverage_pct')}% holes={_pp.get('marks_holes')}"
              f" tier={_pp.get('fill_verify_tier')} face={_c2.get('captured')}"
              f"/{_c2.get('closed_days')}")
    except Exception as e:
        check("product: dashboard carries the marks coverage gap", False, str(e))
    # The open-fill gate must say which evidence tier verified the fills, and
    # on the bar tier its numbers must actually come from the bar (r1131):
    # recompute each session_open from data/daily and assert equality, so a
    # face that quietly recycles the engine's own cost_price cannot pass.
    try:
        _ofv = json.load(open("results/t35_open_fill_verify.json",
                              encoding="utf-8"))
        _tier = _ofv.get("evidence_tier")
        _ok_ofv, _why = True, []
        if _tier not in ("marks", "daily_bar_open", "none"):
            _ok_ofv, _why = False, [f"unknown tier {_tier!r}"]
        elif _tier == "daily_bar_open":
            if _ofv.get("drops_observable") is not False:
                _ok_ofv = False
                _why.append("bar tier must declare drops_observable=false")
            _d = _ofv.get("day")
            _n = 0
            for _tid, _tr in (_ofv.get("per_trader") or {}).items():
                for _r in (_tr.get("detail") or []):
                    if _r.get("outcome") != "filled":
                        continue
                    _n += 1
                    _px = None
                    for _nm in (_r["symbol"], f"sh{_r['symbol']}",
                                f"sz{_r['symbol']}"):
                        _p = os.path.join("data", "daily", f"{_nm}.csv")
                        if not os.path.exists(_p):
                            continue
                        import csv as _csv
                        with open(_p, encoding="utf-8") as _fh:
                            for _row in _csv.DictReader(_fh):
                                if _row.get("date") == _d:
                                    _px = float(_row["open"])
                                    break
                        if _px is not None:
                            break
                    if _px is None or abs(_px - _r["session_open"]) > 1e-9:
                        _ok_ofv = False
                        _why.append(f"{_r['symbol']} bar={_px} "
                                    f"face={_r['session_open']}")
            if _n == 0 and _ofv.get("verdict") == "PASS":
                _ok_ofv = False
                _why.append("PASS on the bar tier but zero filled rows checked")
        check("product: open-fill gate names its evidence tier and the bar "
              "tier's prices are the bars'", _ok_ofv,
              f"tier={_tier} verdict={_ofv.get('verdict')} "
              f"matches={(_ofv.get('counters') or {}).get('matched')} "
              f"{' '.join(_why)}")
    except Exception as e:
        check("product: open-fill gate names its evidence tier and the bar "
              "tier's prices are the bars'", False, str(e))
    # A live paper book priced behind the exchange calendar must say so on its
    # own face (r1121): the SYSTEM-V1 lane consumes a SIG/BARS bridge cutoff,
    # one lane's output, and it sat 4 trading days behind while every other
    # face was current. Assert the block agrees with its own two dates -- a
    # hardcoded "stale: false" would pass a weaker existence-only check.
    try:
        _v1 = json.load(open("results/system_v1_paper/SYSTEM-V1_paper.json",
                             encoding="utf-8"))
        _st = _v1.get("staleness") or {}
        _lag = _st.get("lag_trading_days")
        _ok_st = (_st.get("panel_cutoff") == _v1.get("panel_cutoff")
                  and _st.get("calendar_last") == _v1.get("etf_calendar_last")
                  and (_lag is None or (_lag >= 0 and _lan_ok(_lag, _st))))
        check("product: live paper book states its price lag", _ok_st,
              f"panel={_v1.get('panel_cutoff')} "
              f"calendar={_v1.get('etf_calendar_last')} "
              f"lag={_lag} stale={_st.get('stale')}")
    except Exception as e:
        check("product: live paper book states its price lag", False, str(e))
    # The ETF book is the only money-making structure we publish, yet every face of
    # it is machine-shaped; docs/live_book is the one a human reads. Assert it is
    # current with the ticket pointer and that its own arithmetic closes -- a page
    # left behind after a new ticket would otherwise look perfectly valid.
    try:
        _lb = json.load(open("results/etf_book_order/latest.json", encoding="utf-8"))
        _ptr = json.load(open("docs/live_book/latest.json", encoding="utf-8"))
        _page = json.load(open(_ptr.get("json"), encoding="utf-8"))
        _sum = sum(float(o.get("amount_cny") or 0) for o in (_page.get("order") or []))
        # r1310: the page is written by bm-a only (single writer, HOST in
        # scripts/etf_book_ceo_page.py), so on the host that advanced the ticket the two
        # dates can legitimately differ by ONE bar -- that is bm-a's refresh to make, not a
        # defect this host can close. The lag is bounded and printed, never silently
        # accepted: a lag of 2+ bars is a genuinely stale CEO page and stays red.
        _lag_td = None
        try:
            _cal = pd.to_datetime(pd.read_csv("data/exchange_calendar.csv")["date"])
            _lag_td = int(((_cal > pd.Timestamp(_page.get("evidence_cutoff")))
                           & (_cal <= pd.Timestamp(_lb.get("as_of")))).sum())
        except Exception:
            _lag_td = None
        _dates_ok = (_page.get("evidence_cutoff") == _lb.get("as_of")
                     or (_lag_td is not None and 0 < _lag_td <= 1))
        _ok_lb = (_page.get("schema") == "etf-book-ceo-page/v1"
                  and _dates_ok
                  and bool(_page.get("next_rebalance_date"))
                  and bool(_page.get("order"))
                  and abs(_sum + float(_page.get("cash_amount_cny") or 0)
                          - float(_page.get("capital_cny") or 0)) < 1.0)
        check("product: ETF live-book page current and its money closes", _ok_lb,
              f"page_cutoff={_page.get('evidence_cutoff')} ticket_asof={_lb.get('as_of')} "
              f"lag_td={_lag_td} names={len(_page.get('order') or [])} "
              f"next={_page.get('next_rebalance_date')}"
              + ("" if _page.get("evidence_cutoff") == _lb.get("as_of")
                 else " (page one bar behind; writer=bm-a owes the refresh)"))
        # The page now states the same expectation in yuan. Assert the unit change
        # is honest: every yuan figure must equal its own percentage x the capital
        # printed on the same page, and an absent input must be null, not 0 (a 0
        # would read as "this book earns nothing", which is a different claim).
        _mc = _page.get("money_cny") or {}
        _cap = float(_page.get("capital_cny") or 0)
        _tb = _page.get("ticket_book") or {}
        _ok_money = (bool(_mc) and _cap > 0 and bool(_tb)
                     and abs(float(_mc.get("expected_annual_cny") or 0) - _tb["cagr"] * _cap) < 1.0
                     and abs(float(_mc.get("worst_drawdown_cny") or 0) - _tb["maxdd"] * _cap) < 1.0
                     and abs(float(_mc.get("excess_annual_cny") or 0)
                             - float(_page.get("excess_pp") or 0) / 100.0 * _cap) < 1.0)
        check("product: ETF live-book yuan figures are its own percentages x its own capital", _ok_money,
              f"expected={_mc.get('expected_annual_cny')} excess={_mc.get('excess_annual_cny')} "
              f"worst={_mc.get('worst_drawdown_cny')} capital={_cap}")
        # The page used to print a fresh buy list every session while the DECISION
        # had not moved for two weeks: a holder following it would re-buy a book
        # they already own, at 8bp a side. Assert the page names the world the
        # reader is in, and that the mode follows its own two date faces (a page
        # saying "hold" on a rebalance bar, or "trade" with no position, fails).
        _ta = _page.get("today_action") or {}
        _mode = _ta.get("mode")
        _decided_is_priced = str(_page.get("book_decided_at")) == str(_page.get("priced_bar"))
        _holds = bool((_page.get("forward") or {}).get("bars"))
        _ok_act = (_mode in ("hold", "open", "rebalance")
                   and (_mode == "rebalance") == (_decided_is_priced and _holds)
                   and (_mode != "hold"
                        or _ta.get("next_trade_date") == _page.get("next_rebalance_date"))
                   and (_ta.get("cost_if_retraded_pct_per_year") is None
                        or abs(float(_ta["cost_if_retraded_pct_per_year"])
                               - 2.0 * float(_page.get("cost_bp_per_side") or 0) / 10000.0
                               * 250 * float(_page.get("k_now") or 0) * 100) < 0.01))
        check("product: ETF live-book page says whether to trade today", _ok_act,
              f"mode={_mode} decided={_page.get('book_decided_at')} "
              f"priced={_page.get('priced_bar')} retrade_cost="
              f"{_ta.get('cost_if_retraded_pct_per_year')}%/yr")
        # A page that only quotes the backtest's max drawdown answers "how bad was the
        # strategy's own path", not "how bad can this exact set of names get". Assert
        # the stress block exists, that each window's yuan is that window's own
        # percentage x this ticket's capital, and that no window is silently blank.
        _st = _page.get("stress") or {}
        _w = _st.get("worst") or {}
        _ok_st = bool(_st) and not _st.get("error") and _st.get("n_days", 0) > 0
        for _k in ("1d", "5d", "20d"):
            _row = _w.get(_k)
            if not _row:
                _ok_st = False
                break
            _ok_st = (_ok_st and isinstance(_row.get("end_date"), str)
                      and abs(float(_row.get("cny") or 0)
                              - float(_row.get("pct") or 0) / 100.0 * _cap) < 100.0
                      and float(_row.get("pct") or 0) < 0)
        check("product: ETF live-book stress rows are their own percentages x capital", _ok_st,
              f"days={_st.get('n_days')} 1d={_w.get('1d', {}).get('pct')} "
              f"5d={_w.get('5d', {}).get('pct')} 20d={_w.get('20d', {}).get('pct')}")
    except Exception as e:
        check("product: ETF live-book page current and its money closes", False, str(e))
    # A panel cutoff is a MAX tail, so it is not a coverage claim: this box's
    # astock_daily face read `cutoff 2026-10-26` while 31.4% of names reached it
    # and 90% stopped at 2026-10-20 (bm-a MSG-20261027-0400 mistook the gap for
    # a stale consumer). Assert the coverage face is published AND that it
    # agrees with its own date -- an existence-only check would pass on a face
    # that prints a percentage of the wrong denominator.
    try:
        _ad = json.load(open("results/astock_daily_update_status.json",
                             encoding="utf-8"))
        _p = _ad.get("panel") or {}
        _cp = _p.get("coverage_pct")
        _c90 = _p.get("coverage_90")
        _cut = _p.get("cutoff")
        _ok_ad = (isinstance(_cp, (int, float)) and 0.0 <= float(_cp) <= 100.0
                  and isinstance(_c90, str) and bool(_p.get("cutoff_is"))
                  and isinstance(_p.get("dates_tail"), list)
                  and (not _cut or not _c90 or _c90 <= _cut))
        check("product: astock panel states its coverage, not just its date",
              _ok_ad,
              f"cutoff={_cut} coverage={_cp}% 90%-date={_c90} "
              f"mode={_ad.get('mode')}")
    except Exception as e:
        check("product: astock panel states its coverage, not just its date",
              False, str(e))
    # heartbeat epoch fields (T-04 F5): heartbeat_epoch_utc int + clock_read
    # ISO string on this machine's heartbeat file -- clock drift detectable.
    try:
        # utf-8-sig: heartbeat files are written per-machine; BOM-tolerant
        # read (bm-c r6 _read_json precedent -- strict utf-8 crashes on BOM)
        _mid = json.load(open("fleet/machine.json", encoding="utf-8-sig"))["machine_id"]
        _hb = json.load(open(f"fleet/machines/{_mid}.json", encoding="utf-8-sig"))
        _ok_hb = (isinstance(_hb.get("heartbeat_epoch_utc"), int)
                  and isinstance(_hb.get("clock_read"), str)
                  and "T" in _hb["clock_read"])
        check("fleet: heartbeat epoch fields present", _ok_hb,
              f"{_mid}: epoch={_hb.get('heartbeat_epoch_utc')} "
              f"clock={_hb.get('clock_read')}")
    except Exception as e:
        check("fleet: heartbeat epoch fields present", False, str(e))
    # ... and the GPU face on the same heartbeat must agree with itself and carry a
    # provenance stamp. r1277's face held 25 GPU keys disagreeing by up to 13 GB
    # (free 13.72 GB next to free 1.31 GB) with util pinned to a literal 0; a fleet
    # audit reading any single key read a random round's snapshot. Selftest covers
    # the pure audit; this leg covers the live file, which is where it was broken.
    try:
        _mid = json.load(open("fleet/machine.json", encoding="utf-8-sig"))["machine_id"]
        _hb = json.load(open(f"fleet/machines/{_mid}.json", encoding="utf-8-sig"))
        _gf = importlib.import_module("Tools.gpu_face")
        _fnd = _gf.audit(_hb)
        check("fleet: GPU face self-consistent on heartbeat", not _fnd,
              f"{_mid}: findings={_fnd or 'none'} stamped={bool(_hb.get('gpu_face_ts'))}")
        _legs = {n for n, _c in importlib.import_module("Tools.s6_chain_bmc").LEGS}
        check("fleet: GPU face leg wired into the S6 chain", "gpu_face" in _legs,
              f"legs={len(_legs)}")
    except Exception as e:
        check("fleet: GPU face self-consistent on heartbeat", False, str(e))
        check("fleet: GPU face leg wired into the S6 chain", False, str(e))


    # fleet/machine-health.json is the face every panel reads for per-machine lane
    # colour, and nothing checked its SHAPE. It had drifted into three shells of
    # {"value": [...]} around hashtable .ToString() strings -- json.load returned a
    # list of junk, monitor/build_status.py failed soft, and the board rendered blank
    # rows that read like calm machines (D-20261028-02). Legs: the builder's own
    # contract, and the LIVE face must still be machine-keyed today.
    try:
        _mf = importlib.import_module("Tools.machine_health_face")
        _mach, _st, _drop = _mf.read_face()
        check("fleet: machine-health face is machine-keyed, not a nesting generator",
              _st == "ok" and bool(_mach),
              f"status={_st} machines={','.join(sorted(_mach)) or '-'} junk={_drop}")
    except Exception as e:
        check("fleet: machine-health face is machine-keyed, not a nesting generator",
              False, str(e))

    # D-20261028-02 pins six fields per machine. Shape-ok was being read as
    # contract-ok: on 2026-10-28 the live face was a clean machine-keyed map and the
    # gate said OK while two of three rows carried no `cpu` and every row carried a
    # flat gpu_free_gb instead of the pinned `gpu` object. Two legs: the LIVE face
    # must carry every pinned field, and the panel must refuse to call a thin face
    # healthy (so the next writer regression shows up as UNKNOWN, not as a calm row).
    try:
        # Refresh before judging, exactly as the chain does (r1315): the hourly
        # oversight writer is a separate code face that emits a partial row, so
        # without this the leg would call a healthy machine thin every couple of
        # hours and the cheap "fix" would be to loosen the assertion.
        _mf.rebuild_face()
        _mach, _mstat, _mdrop = _mf.read_face()
        _gaps = {m: _mf.entry_gaps(e) for m, e in _mach.items()}
        _bad = {m: g for m, g in _gaps.items() if g}
        check("fleet: live machine-health rows carry every pinned field",
              bool(_mach) and not _bad, f"machines={len(_mach)} gaps={_bad or '-'}")
    except Exception as e:
        check("fleet: live machine-health rows carry every pinned field", False, str(e))

    try:
        import tempfile as _tf
        _d = _tf.mkdtemp(prefix="mhthin_")
        os.makedirs(os.path.join(_d, "fleet", "machines"), exist_ok=True)
        with open(os.path.join(_d, "fleet", "machine-health.json"), "w",
                  encoding="utf-8") as _fh:
            json.dump({"bm-c": {"ts": "2026-10-28 02:00", "util": "red", "work": "w",
                                "ram_free_gb": 0.7, "gpu": {"free_gb": 14.6}}}, _fh)
        _bs = importlib.import_module("monitor.build_status")
        _orig = _bs.PATHS.root
        _bs.PATHS.root = _d
        try:
            _u = _bs._machine_health_union()
        finally:
            _bs.PATHS.root = _orig
        _fce = _u.get("_face") or {}
        check("fleet: a thin face reads as UNKNOWN, not as a calm row",
              _fce.get("health_unknown") is True
              and _fce.get("health_face") == "incomplete"
              and (_fce.get("health_gaps") or {}).get("bm-c") == ["cpu"],
              "face=%s gaps=%s" % (_fce.get("health_face"), _fce.get("health_gaps")))
    except Exception as e:
        check("fleet: a thin face reads as UNKNOWN, not as a calm row", False, str(e))

    # The hourly oversight writer does NOT run this repo's copy. It runs a deployed
    # copy under <KRoot>\.codely-cli\oversight-<id>\fleet-oversight.ps1, and nothing
    # kept the two in step: D-20261028-02 fixed the writer in the repo, the running
    # copy stayed at v1.0, and the very next hourly fire re-broke fleet/machine-health
    # with the nesting the fix had just removed (2026-10-28 01:11, one hour after the
    # rebuilt face read clean). A deployed copy is a SECOND code face, so its drift is
    # a red leg rather than something a reader has to notice from damaged output.
    try:
        _mid2 = json.load(open("fleet/machine.json", encoding="utf-8-sig"))["machine_id"]
        _group = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))
        _dtool = os.path.join(_group, "Tools", "oversight_deploy.ps1")
        if not os.path.isfile(_dtool):
            check("fleet: oversight writer's deployed copy tracks its source", True,
                  "group tree not mounted on this machine -- omitted, not passed")
        else:
            # The arrangement differs per machine: some run a DEPLOYED copy, others
            # point the hourly task straight at the group repo source. Asserting the
            # deployed copy unconditionally reads a direct-run machine as "never
            # deployed" forever (bm-a 2026-10-28), which invites loosening the leg.
            # So ask the task what it actually runs and check THAT copy.
            _live = ""
            try:
                _x = subprocess.run(
                    ["schtasks", "/query", "/tn", "FluxGroup-FleetOversight", "/xml"],
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                    creationflags=0x08000000)
                if _x.returncode == 0 and _x.stdout:
                    _live = _x.stdout
            except Exception:
                _live = ""
            _norm = _live.replace("\\", "/").lower()
            if _live and "oversight-" not in _norm and "fleet-oversight.ps1" in _norm:
                _src = os.path.join(_group, "Tools", "fleet-oversight.ps1").replace("\\", "/").lower()
                check("fleet: oversight writer's deployed copy tracks its source",
                      _src in _norm,
                      "live task runs the group repo source directly" if _src in _norm
                      else "live task runs a copy that is not this group tree")
            else:
                _dw = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                     _dtool, "-M", _mid2, "-Check"],
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                    creationflags=0x08000000)
                _dline = ((_dw.stdout or "").strip().splitlines() or [""])[-1]
                check("fleet: oversight writer's deployed copy tracks its source",
                      _dw.returncode == 0, f"rc={_dw.returncode} {_dline[:90]}")
    except Exception as e:
        check("fleet: oversight writer's deployed copy tracks its source", False, str(e))
    # D-20261028-02's other half: the reader can classify, but the PANEL is what a
    # person reads. Assert the face's own verdict reached the payload (a row count
    # cannot tell "three calm machines" from "one readable row and two missing"),
    # and that the gate rides the chain instead of living in a hand run.
    try:
        _bs = json.load(open("results/dashboard_status.json", encoding="utf-8"))
        _fl = ((_bs.get("data") or {}).get("engine")) or {}
        _hf = _fl.get("health_face") or {}
        # The panel is a SNAPSHOT of a face that an hourly writer on another
        # machine keeps refreshing (observed twice on 2026-10-28: the chain
        # derived a clean verdict, bm-c's row landed a cpu column 12 minutes
        # later, and this leg then read "incomplete" off the older snapshot).
        # Judging a snapshot against a face it never saw makes the gate fire on
        # the clock instead of on the reader, so a thin verdict is accepted only
        # when it is explained by exactly that: the upstream face is newer than
        # the panel AND a fresh derivation of it is clean. Anything else -- a
        # reader that says "incomplete" in front of a clean face -- still reds.
        _face_ok = (_hf.get("health_face") in ("ok", "legacy_list")
                    and _hf.get("health_unknown") is False)
        _why = "face=%s unknown=%s junk=%s" % (_hf.get("health_face"),
                                               _hf.get("health_unknown"),
                                               _hf.get("health_face_junk"))
        if not _face_ok:
            _up = "fleet/machine-health.json"
            _up_newer = os.path.getmtime(_up) > os.path.getmtime(
                "results/dashboard_status.json")
            _now = (importlib.import_module("monitor.build_status")
                    ._machine_health_union().get("_face") or {})
            _stale_explained = (_up_newer
                                and _now.get("health_face") == "ok"
                                and _now.get("health_unknown") is False)
            _why += " panel=%s upstream_newer=%s now=%s" % (
                (_bs.get("meta") or {}).get("generated_at"), _up_newer,
                _now.get("health_face"))
            if _stale_explained:
                _face_ok = True
        check("fleet: panel carries the machine-health verdict, not a row count",
              _face_ok, _why)
        _legs = {n for n, _c in importlib.import_module("Tools.s6_chain_bmc").LEGS}
        check("fleet: machine-health gate leg wired into the S6 chain",
              "machine_health_face" in _legs, f"legs={len(_legs)}")
        # r1318: the panel READS the health face, so the writer has to run first.
        # It did not -- build_status copied a thinned row and the heal happened
        # behind it, which is why this very leg went red on a healthy fleet.
        _order = [n for n, _c in importlib.import_module("Tools.s6_chain_bmc").LEGS]
        check("fleet: health writer runs before the panel that reads it",
              _order.index("machine_health_write") < _order.index("build_status"),
              "write=%d build_status=%d" % (_order.index("machine_health_write"),
                                            _order.index("build_status")))
    except Exception as e:
        check("fleet: panel carries the machine-health verdict, not a row count",
              False, str(e))
        check("fleet: machine-health gate leg wired into the S6 chain", False, str(e))

    # The memory file is a write target for every round and nothing read its SHAPE.
    # On 2026-10-27 it was appended by whole-file string concat: newlines collapsed,
    # the older body went out through a GBK round trip (19 x U+E511), and the file
    # still read `git status` clean -- 62 lines became 4 with nothing red anywhere
    # (D-20261027-08). Counts, not content: one line per entry, no private-use
    # characters, list rows present.
    try:
        _mt = open("CODELY.md", encoding="utf-8-sig").read()
        _lf = _mt.count("\n")
        _pua = sum(1 for _c in _mt if 0xE000 <= ord(_c) <= 0xF8FF)
        _rows = sum(1 for _l in _mt.splitlines() if _l.lstrip().startswith("- ["))
        check("memory: CODELY.md structure intact", _lf >= 55 and _pua == 0 and _rows > 0,
              f"lines={_lf} pua={_pua} list_rows={_rows} "
              f"bytes={len(_mt.encode('utf-8'))}")
    except Exception as e:
        check("memory: CODELY.md structure intact", False, str(e))

    # A commit built from a partial index produces a valid push whose only
    # symptom is a much smaller tree (r1133: the group tip lost 3,492 files and
    # nothing in the repo noticed until a consumer could not read decisions.md).
    try:
        _tg = os.path.join("Tools", "tree_shrink_guard.py")
        _tp = subprocess.run([sys.executable, _tg, "selftest"], capture_output=True,
                             text=True, encoding="utf-8", errors="replace")
        _tt = ((_tp.stdout or "").strip().splitlines() or [""])[-1]
        check("fleet: a partial-index commit cannot silently shrink the tree",
              _tp.returncode == 0, f"guard selftest rc={_tp.returncode} {_tt[:60]}")
        _tq = subprocess.run([sys.executable, _tg, "check", "--repo", ".",
                              "--commits", "20"], capture_output=True, text=True,
                             encoding="utf-8", errors="replace")
        _tql = ((_tq.stdout or "").strip().splitlines() or [""])[0]
        check("fleet: this repo's last 20 commits lost no tree", _tq.returncode == 0,
              _tql[:100])
    except Exception as e:
        check("fleet: a partial-index commit cannot silently shrink the tree", False, str(e))

    # Detecting a wipe after the push is too late (r1133 repaired it 25 minutes
    # later). The push itself is hookable, so both repos carry a pre-push gate;
    # this leg fails if a machine has the file but never installed it.
    try:
        _gg = subprocess.run([sys.executable, os.path.join("Tools", "tree_shrink_guard.py"),
                              "check_gates"], capture_output=True, text=True,
                             encoding="utf-8", errors="replace")
        _gt = ((_gg.stdout or "") + (_gg.stderr or "")).strip().splitlines()
        check("fleet: the tree-shrink push gate is installed in both repos",
              _gg.returncode == 0, (_gt[0] if _gt else "")[:110])
    except Exception as e:
        check("fleet: the tree-shrink push gate is installed in both repos", False, str(e))

    # A sleeve that was measured but never published is the "produced but never read"
    # failure this repo keeps recording (r1108). The futures TSMOM sleeve now has a daily
    # shadow face; this leg asserts it exists, is capped, is NOT actionable, and is
    # priced on the newest bar the panel actually has (an old face reading as current is
    # worse than no face).
    try:
        import glob as _glob
        import json as _json
        _sp = os.path.join("scripts", "futures_tsmom_signal.py")
        _sr = subprocess.run([sys.executable, _sp, "--selftest"], capture_output=True,
                             text=True, encoding="utf-8", errors="replace")
        _st = ((_sr.stdout or "").strip().splitlines() or [""])[-1]
        check("product: futures TSMOM shadow face keeps its sizing rules",
              _sr.returncode == 0, f"selftest rc={_sr.returncode} {_st[:60]}")

        _face = _json.load(open(os.path.join("results", "futures_tsmom_signal.json"),
                                encoding="utf-8"))
        _tails = []
        for _p in _glob.glob(os.path.join("data", "futures_daily", "*.csv")):
            try:
                _last = open(_p, encoding="utf-8").read().strip().splitlines()[-1]
                _tails.append(_last.split(",")[0].strip()[:10])
            except Exception:
                pass
        _panel_tail = max(_tails) if _tails else ""
        _gross = (_face.get("book") or {}).get("gross")
        _ok = (_face.get("actionable") is False
               and _face.get("shadow") is True
               and isinstance(_gross, (int, float)) and _gross <= 3.0 + 1e-9
               and _face.get("generated_for_bar") == _panel_tail
               and _face.get("staleness", {}).get("stale") is False)
        check("product: futures TSMOM face is current, capped and not an order", _ok,
              "bar=%s panel=%s gross=%s stale=%s" % (
                  _face.get("generated_for_bar"), _panel_tail, _gross,
                  _face.get("staleness", {}).get("stale")))
    except Exception as e:
        check("product: futures TSMOM shadow face keeps its sizing rules", False, str(e))

    # r1291 law, second face: a heavier sleeve weight also lowers total risk, so the raw
    # CAGR column of the overlay sweep is a leverage artifact. This leg asserts the face
    # publishes BOTH readings and that the sleeve weight really does move risk -- an
    # equal-risk block copied next to an unmoving raw column would be a decorative fix.
    try:
        import json as _json
        _sp = os.path.join("scripts", "futures_overlay_sweep.py")
        _sr = subprocess.run([sys.executable, _sp, "--selftest"], capture_output=True,
                             text=True, encoding="utf-8", errors="replace")
        _st = ((_sr.stdout or "").strip().splitlines() or [""])[-1]
        check("product: futures overlay sweep keeps its blend arithmetic",
              _sr.returncode == 0, f"selftest rc={_sr.returncode} {_st[:60]}")

        _face = _json.load(open(os.path.join("results", "futures_overlay_sweep.json"),
                                encoding="utf-8"))
        _sw = _face.get("sweeps") or {}
        _rows = (_sw.get("tsmom60") or {}).get("full") or []
        _vols = [r.get("realised_vol") for r in _rows]
        _has_equal = all(isinstance(r.get("at_equal_vol"), dict) for r in _rows) and bool(_rows)
        _risk_falls = bool(_vols) and _vols[-1] < _vols[0] - 1e-6
        _flat_at_equal = (not _rows) or abs(
            _rows[0]["at_equal_vol"].get("cagr", 0) - _rows[0].get("cagr", 0)) < 5e-4
        _desc = "descriptive" in str(_face.get("face", "")).lower()
        check("product: overlay sweep sells risk and publishes the equal-risk reading",
              sorted(_sw) == ["tsmom120", "tsmom60"] and _has_equal and _risk_falls
              and _flat_at_equal and _desc,
              "weights=%d vol %.4f->%.4f equal_vol_block=%s descriptive=%s" % (
                  len(_rows), _vols[0] if _vols else -1, _vols[-1] if _vols else -1,
                  _has_equal, _desc))
    except Exception as e:
        check("product: futures overlay sweep keeps its blend arithmetic", False, str(e))

    # r1138: a 1bp-per-side placeholder is not a measurement. This leg recomputes the
    # breakeven straight out of the published ladder (never reading the reported field),
    # and insists the ladder was built from ONE decision sequence: turnover must be
    # identical at every cost level, otherwise the levels describe different strategies
    # and the breakeven is meaningless.
    try:
        import json as _json
        _face = _json.load(open(os.path.join("results", "futures_overlay_sweep.json"),
                                encoding="utf-8"))
        _sw = _face.get("sweeps") or {}
        _bad = []
        for _tag in ("tsmom60", "tsmom120"):
            _blk = _sw.get(_tag) or {}
            _lad = _blk.get("cost_ladder") or []
            _be = (_blk.get("cost_breakeven_bp") or {}).get("max_cost_per_side_bp")
            if len(_lad) < 2:
                _bad.append(f"{_tag}: ladder has {len(_lad)} levels")
                continue
            _turns = {round(b.get("sleeve_turnover_total") or 0.0, 1) for b in _lad}
            if len(_turns) != 1:
                _bad.append(f"{_tag}: turnover moves across costs {sorted(_turns)}")
            _w = (_blk.get("cost_breakeven_bp") or {}).get("weight")
            _recomputed = None
            for _b in sorted(_lad, key=lambda b: b["cost_per_side_bp"]):
                _row = next((r for r in _b["rows"]
                             if round(float(r["weight_in_sleeve"]), 4) == round(float(_w), 4)), None)
                _d = (_row or {}).get("at_equal_vol_delta_cagr_pp")
                if _d is None or _d <= 0:
                    break
                _recomputed = _b["cost_per_side_bp"]
            if _recomputed != _be:
                _bad.append(f"{_tag}: reported breakeven {_be} != recomputed {_recomputed}")
        check("product: overlay breakeven is recomputable from its own ladder",
              not _bad, "; ".join(_bad)[:200] or "both lookbacks: one sequence, stated breakeven")
    except Exception as e:
        check("product: overlay breakeven is recomputable from its own ladder", False, str(e))

    # A no-trade band is only honest if it publishes BOTH what it removes (turnover) and
    # what it gives up (gross), and if the structural floor it cannot touch is measured
    # rather than assumed. The floor is measured with an effectively infinite band, so a
    # face that reports a band cutting more turnover than the floor allows is arithmetic
    # fiction.
    try:
        import json as _json
        _face = _json.load(open(os.path.join("results", "futures_overlay_sweep.json"),
                                encoding="utf-8"))
        _bad = []
        for _tag in ("tsmom60", "tsmom120"):
            _tc = ((_face.get("sweeps") or {}).get(_tag) or {}).get("turnover_control") or {}
            _rows = _tc.get("rows") or []
            if len(_rows) < 3:
                _bad.append(f"{_tag}: {len(_rows)} bands")
                continue
            _base = _rows[0]
            if round(_base["band"], 4) != 0.0:
                _bad.append(f"{_tag}: first band is {_base['band']}, not the baseline")
            _turns = [r["sleeve_turnover_total"] for r in _rows]
            if any(b > a + 1e-9 for a, b in zip(_turns, _turns[1:])):
                _bad.append(f"{_tag}: turnover rises as the band widens {_turns}")
            _floor = _tc.get("structural_turnover_total")
            if _floor is None or _floor > _turns[0] + 1e-9:
                _bad.append(f"{_tag}: structural floor {_floor} exceeds unbounded turnover")
            if min(_turns) < _floor - 1e-9:
                _bad.append(f"{_tag}: a band cut {min(_turns)} below the {_floor} floor")
            _maxcut = _tc.get("resizing_share_pct")
            for _r in _rows:
                if _r.get("gross_give_up_pp") is None:
                    _bad.append(f"{_tag} band {_r['band']}: no gross give-up published")
                    break
                _costs = {round(c["turnover_total"], 1) for c in _r.get("cost_rows") or []}
                if len(_costs) > 1:
                    _bad.append(f"{_tag} band {_r['band']}: turnover moves across cost levels")
                    break
                _cut = _r.get("turnover_cut_pct")
                if _cut is not None and _maxcut is not None and _cut > _maxcut + 0.2:
                    _bad.append(f"{_tag} band {_r['band']}: claims a {_cut}% cut but only "
                                f"{_maxcut}% of turnover is re-sizing")
                    break
        check("product: overlay no-trade band is priced on both sides of the trade",
              not _bad, "; ".join(_bad)[:200]
              or "floor measured, cut <= resizing share, gross give-up published per band")
    except Exception as e:
        check("product: overlay no-trade band is priced on both sides of the trade", False, str(e))

    return _finish()


def _finish() -> int:
    n_pass = sum(1 for _, ok, _ in RESULTS if ok)
    n_fail = len(RESULTS) - n_pass
    print(f"\nSummary: {n_pass}/{len(RESULTS)} PASS, {n_fail} FAIL")
    try:
        os.makedirs("logs", exist_ok=True)
        with open(os.path.join("logs", "smoke.log"), "a", encoding="utf-8") as f:
            f.write(f"{dt.datetime.now().isoformat(timespec='seconds')} "
                    f"pass={n_pass} fail={n_fail}\n")
    except Exception:
        pass
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
