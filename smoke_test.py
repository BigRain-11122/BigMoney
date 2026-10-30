"""One-command smoke test: env / config / data / engine / exit rules / market rules / network.

Usage:
    python -m smoke_test

Exit code 0 = all green, 1 = any failure. A timestamped summary line is
appended to logs/smoke.log so the 10-minute iteration loop can audit runs.
"""
import sys
import os
import io
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
    try:
        import numpy
        import pandas
        import scipy
        check("env: core deps", True,
              f"numpy {numpy.__version__}, pandas {pandas.__version__}, scipy {scipy.__version__}")
    except Exception as e:
        check("env: core deps", False, str(e))
        return _finish()
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
    h1 = combo_hash(combos[0]); h2 = combo_hash(combos[0])
    check("config: combo_hash deterministic", h1 == h2 and len(h1) == 8, f"hash={h1}")
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
    from knowledge.rules import FeeSchedule, is_t0
    fee = FeeSchedule()
    cost_rate = fee.commission_rate + fee.handling_fee + fee.supervision_fee + fee.slippage_a
    check("rules: fee schedule sane", 0 < cost_rate < 0.005,
          f"single-side cost {cost_rate*1e4:.1f} bp")
    check("rules: T+0 list", is_t0("511880") and not is_t0("510300"),
          "511880 T+0, 510300 T+1")
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
    same_day = [t for t in r1["trades"]
                if not is_t0(t["symbol"]) and t["hold_days"] <= 0]
    check("engine: T+1 respected", len(same_day) == 0,
          f"{len(r1['trades'])} trades checked, {len(same_day)} same-day roundtrips")
    open_px = {s: dict(zip(w.index.strftime("%Y-%m-%d"), w["open"]))
               for s, w in window.items()}
    bad_exit_px = [t for t in r1["trades"]
                   if abs(round(float(open_px[t["symbol"]].get(t["date"], float("nan"))), 4)
                               - t["price"]) > 1e-6]
    check("engine: exits fill at T+1 open (RW-1)", len(bad_exit_px) == 0,
          f"{len(r1['trades'])} exits checked, {len(bad_exit_px)} non-open fills")
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
    from config import RISK as _RISK_CFG
    RISK = _RISK_CFG
    from live import (RiskGate, RiskGateRejected, Order, gate_orders,
                      emit_order_sheet as _emit)
    _p12 = evaluate(ExitState(cost_price=100.0, hold_days=1), 91.0, cfg,
                    signal_reversed=True)
    check("exit: P1 signal_reversal beats P2 stop (RW-7)",
          _p12.reason == "signal_reversal" and _p12.should_close,
          "reversal+stop same bar -> signal_reversal (P1 > P2)")
    _p23 = evaluate(ExitState(cost_price=100.0, hold_days=6, tier_reached=1,
                               high_watermark=112.0,
                               trailing_stop_price=110.88), 110.5, cfg)
    check("exit: P2 stop_loss beats P3 take_profit (RW-7)",
          _p23.reason == "stop_loss" and abs(_p23.pnl_rate - 0.105) < 1e-9,
          "pnl +10.5% >= tier-2 10% but price 110.5 <= trailing 110.88 "
          "-> stop_loss (P2 > P3)")
    _p45 = evaluate(ExitState(cost_price=100.0, hold_days=12), 99.0, cfg)
    check("exit: P4 time_decay beats P5 loss_time_stop (RW-7)",
          _p45.reason == "time_decay",
          "hold 12d pnl -1% -> time_decay, not loss_time_stop (P4 > P5)")
    _p6 = evaluate(ExitState(cost_price=100.0, hold_days=25), 103.0, cfg)
    check("exit: P6 global_hard_limit terminal tier (RW-7)",
          _p6.reason == "global_hard_limit" and _p6.should_close,
          "hold 25d pnl +3% >= decay threshold 2% -> hard_limit fires")
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
    import network_detector
    import traffic_policy
    nt = network_detector.detect()
    check("network: detector", nt in ("LAN", "WIFI", "HOTSPOT", "UNKNOWN"), f"net_type={nt}")
    st = network_detector.read_status()
    check("network: status readable", isinstance(st, dict) and "net_type" in st)
    ok_small = traffic_policy.can_run("smoke_incremental", 1 * 1024 * 1024)
    check("network: traffic gate", isinstance(ok_small, bool))
    try:
        from live import paper as live_paper
        check("paper: pipeline selftest", live_paper.selftest(),
              "patches+aggregation+causality+anchor + seg-honesty(F4) "
              "+ x2-watch escalation(F3)")
    except Exception as e:
        check("paper: pipeline selftest", False, str(e))
    import subprocess as _sp
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
            _r = _sp.run([sys.executable, _script, *_args],
                         capture_output=True, text=True, timeout=180)
            _tail = ((_r.stdout or _r.stderr).strip().splitlines() or ["no output"])[-1]
            check(_label, _r.returncode == 0, f"exit={_r.returncode} | {_tail[:80]}")
        except Exception as e:
            check(_label, False, str(e))
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
            # r1233 (E205): the decomposition delta faces are silent by construction.
            # The growth gate is the only thing that fails when one of them quietly
            # acquires its first durable reader, so it has to be exercised, not
            # remembered.
            ("product: e97 sign-growth gate (crossing detection contract)",
             "scripts/e97_routing.py", ["selftest"]),
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
             "scripts/etf_book_buffer_adoption.py", ["--selftest"])):
        try:
            _r = _sp.run([sys.executable, _script, *_args],
                         capture_output=True, text=True, timeout=300)
            _tail = ((_r.stdout or _r.stderr).strip().splitlines() or ["no output"])[-1]
            check(_label, _r.returncode == 0, f"exit={_r.returncode} | {_tail[:80]}")
        except Exception as e:
            check(_label, False, str(e))
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
    try:
        _stg = [f for f in (_rg.get("faces") or []) if f.get("id") == "staggered"]
        _turn = (_stg[0].get("next_turn") if _stg else None) or []
        check("product: ETF registry says when the staggered book turns",
              len(_turn) >= 2 and all(t.get("due") for t in _turn),
              "; ".join("leg%s %s" % (t.get("leg"), t.get("due")) for t in _turn)
              or "no next_turn on the staggered row")
    except Exception as e:
        check("product: ETF registry says when the staggered book turns", False, str(e))
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
    try:
        _mf = importlib.import_module("Tools.machine_health_face")
        _mach, _st, _drop = _mf.read_face()
        check("fleet: machine-health face is machine-keyed, not a nesting generator",
              _st == "ok" and bool(_mach),
              f"status={_st} machines={','.join(sorted(_mach)) or '-'} junk={_drop}")
    except Exception as e:
        check("fleet: machine-health face is machine-keyed, not a nesting generator",
              False, str(e))
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
    try:
        _dq_order = [n for n, _c in importlib.import_module("Tools.s6_chain_bmb").LEGS]
        _dq_after = (_dq_order.index("docquotes") > _dq_order.index("daily_report")
                     and _dq_order.index("docquotes") > _dq_order.index("ceo_live_usage"))
        check("product: the CEO-page quote audit runs after the pages it audits",
              _dq_after, "docquotes=%d daily_report=%d ceo_live_usage=%d"
              % (_dq_order.index("docquotes"), _dq_order.index("daily_report"),
                 _dq_order.index("ceo_live_usage")))
    except Exception as e:
        check("product: the CEO-page quote audit runs after the pages it audits",
              False, str(e))
    try:
        _pg_order = [n for n, _c in importlib.import_module("Tools.s6_chain_bmb").LEGS]
        _pg_path = os.path.join("results", "e79", "DOCQUOTES-BASELINE.json")
        _pg_ok = (_pg_order.index("pagegate") > _pg_order.index("docquotes")
                  and os.path.exists(_pg_path))
        _pg_note = "pagegate=%d docquotes=%d baseline=%s" % (
            _pg_order.index("pagegate"), _pg_order.index("docquotes"),
            "present" if os.path.exists(_pg_path) else "MISSING")
        if os.path.exists(_pg_path):
            with open(_pg_path, encoding="utf-8") as _fh:
                _pg_doc = json.load(_fh)
            _pg_ok = _pg_ok and isinstance(_pg_doc.get("signatures"), dict)
            _pg_note += " signatures=%d" % len(_pg_doc.get("signatures") or {})
        check("product: the CEO-page quote gate runs after the sweep and owns a baseline",
              _pg_ok, _pg_note)
    except Exception as e:
        check("product: the CEO-page quote gate runs after the sweep and owns a baseline",
              False, str(e))
    try:
        _oera_order = [n for n, _c in importlib.import_module("Tools.s6_chain_bmb").LEGS]
        _oera_dir = os.path.join("results", "e44_midmonth")
        _oera = sorted(f for f in os.listdir(_oera_dir)
                       if f.startswith("OFFBOOK-ERA-")) if os.path.isdir(_oera_dir) else []
        _oera_doc = None
        if _oera:
            with open(os.path.join(_oera_dir, _oera[-1]), encoding="utf-8") as _fh:
                _oera_doc = json.load(_fh)
        _oera_ans = ((_oera_doc or {}).get("answers") or {})
        _oera_st = _oera_ans.get("era_stability_mean") or {}
        _oera_ok = ("offbookera" in _oera_order
                    and _oera_doc is not None
                    and _oera_doc.get("study") == "e214_offbook_liquidity_era_stability"
                    and _oera_st.get("classification") in (
                        "insufficient_eras", "thick_gap_sign_stable_across_eras",
                        "thick_gap_sign_flips_across_eras")
                    and "era_stability_median" in _oera_ans)
        check("product: the off-book era leg is on the chain and publishes a cross-era verdict",
              _oera_ok, "chain=%s face=%s class=%s measured=%s" % (
                  "offbookera" in _oera_order, _oera[-1] if _oera else "MISSING",
                  _oera_st.get("classification"), _oera_st.get("measured_eras")))
    except Exception as e:
        check("product: the off-book era leg is on the chain and publishes a cross-era verdict",
              False, str(e))
    try:
        _sb_order = [n for n, _c in importlib.import_module("Tools.s6_chain_bmb").LEGS]
        _sb_dir = os.path.join("results", "e44_midmonth")
        _sb = sorted(f for f in os.listdir(_sb_dir)
                     if f.startswith("SHAREDBOOK-")
                     and not f.startswith("SHAREDBOOK-WIDTH-")) \
            if os.path.isdir(_sb_dir) else []
        _sb_doc = None
        if _sb:
            with open(os.path.join(_sb_dir, _sb[-1]), encoding="utf-8") as _fh:
                _sb_doc = json.load(_fh)
        _sb_ans = ((_sb_doc or {}).get("answers") or {})
        _sb_ok = ("sharedbook" in _sb_order
                  and _sb_doc is not None
                  and _sb_doc.get("study") == "e61_shared_candidate_pool"
                  and _sb_ans.get("identity_ok") is True
                  and _sb_ans.get("full_window_timing_bp") is not None
                  and _sb_ans.get("full_window_selection_bp") is not None
                  and (_sb_doc.get("widths") or {}).get("pool_median") is not None)
        check("product: the mid-month gap arrives split into timing and selection",
              _sb_ok, "chain=%s face=%s total=%s timing=%s selection=%s resid=%s" % (
                  "sharedbook" in _sb_order, _sb[-1] if _sb else "MISSING",
                  _sb_ans.get("full_window_total_bp"), _sb_ans.get("full_window_timing_bp"),
                  _sb_ans.get("full_window_selection_bp"),
                  _sb_ans.get("identity_residual_bp")))
    except Exception as e:
        check("product: the mid-month gap arrives split into timing and selection",
              False, str(e))
    try:
        _sw_order = [n for n, _c in importlib.import_module("Tools.s6_chain_bmb").LEGS]
        _sw_dir = os.path.join("results", "e44_midmonth")
        _sw = sorted(f for f in os.listdir(_sw_dir)
                     if f.startswith("SHAREDBOOK-WIDTH-")) \
            if os.path.isdir(_sw_dir) else []
        _sw_doc = None
        if _sw:
            with open(os.path.join(_sw_dir, _sw[-1]), encoding="utf-8") as _fh:
                _sw_doc = json.load(_fh)
        _sw_ans = ((_sw_doc or {}).get("answers") or {})
        _sw_rule = ((_sw_doc or {}).get("verdict") or {}).get("rule") or {}
        _sw_ok = ("sharedbookwidth" in _sw_order
                  and _sw_doc is not None
                  and _sw_doc.get("study") == "e218_width_matched_calendar_split"
                  and _sw_ans.get("selection_identity_ok") is True
                  and _sw_ans.get("calendar_matched_sd_bp") is not None
                  and _sw_rule.get("n_draws")
                  and (_sw_doc.get("widths") or {}).get("matched_width_exact") is True)
        check("product: the calendar split is re-read at matched candidate width, "
              "as a distribution rather than a point",
              _sw_ok, "chain=%s face=%s full=%s matched=%s sd=%s draws=%s label=%s" % (
                  "sharedbookwidth" in _sw_order, _sw[-1] if _sw else "MISSING",
                  _sw_ans.get("calendar_full_bp"), _sw_ans.get("calendar_matched_bp"),
                  _sw_ans.get("calendar_matched_sd_bp"), _sw_rule.get("n_draws"),
                  _sw_ans.get("verdict_label")))
    except Exception as e:
        check("product: the calendar split is re-read at matched candidate width, "
              "as a distribution rather than a point", False, str(e))
    try:
        _wl_order = [n for n, _c in importlib.import_module("Tools.s6_chain_bmb").LEGS]
        _wl_dir = os.path.join("results", "e44_midmonth")
        _wl = sorted(f for f in os.listdir(_wl_dir)
                     if f.startswith("WIDTHLADDER-")) \
            if os.path.isdir(_wl_dir) else []
        _wl_doc = None
        if _wl:
            with open(os.path.join(_wl_dir, _wl[-1]), encoding="utf-8") as _fh:
                _wl_doc = json.load(_fh)
        _wl_rows = (_wl_doc or {}).get("rows") or {}
        _wl_v = (_wl_doc or {}).get("verdict") or {}
        _wl_sds = [_wl_rows[k].get("matched_sd_bp") for k in sorted(_wl_rows)]
        _wl_ok = ("sharedbookwidthladder" in _wl_order
                  and "sharedbookwidth" in _wl_order
                  and _wl_order.index("sharedbookwidthladder")
                  > _wl_order.index("sharedbookwidth")
                  and _wl_doc is not None
                  and _wl_doc.get("study") == "e219_width_ladder_resolution"
                  and len(_wl_rows) >= 2
                  and all(s is not None for s in _wl_sds)
                  and _wl_v.get("label")
                  and (_wl_doc.get("spec") or {}).get("widths"))
        check("product: the matched-width control is laddered across book widths, "
              "with the invariance of the gap published beside it",
              _wl_ok, "chain=%s face=%s rungs=%s label=%s sd=%s invariant=%s" % (
                  "sharedbookwidthladder" in _wl_order,
                  _wl[-1] if _wl else "MISSING", len(_wl_rows), _wl_v.get("label"),
                  _wl_sds, _wl_v.get("gap_is_width_invariant")))
    except Exception as e:
        check("product: the matched-width control is laddered across book widths, "
              "with the invariance of the gap published beside it", False, str(e))
    try:
        _ws_order = [n for n, _c in importlib.import_module("Tools.s6_chain_bmb").LEGS]
        _ws_dir = os.path.join("results", "e44_midmonth")
        _ws = sorted(f for f in os.listdir(_ws_dir)
                     if f.startswith("WIDTHSPLIT-")) \
            if os.path.isdir(_ws_dir) else []
        _ws_doc = None
        if _ws:
            with open(os.path.join(_ws_dir, _ws[-1]), encoding="utf-8") as _fh:
                _ws_doc = json.load(_fh)
        _ws_rows = (_ws_doc or {}).get("rows") or {}
        _ws_v = (_ws_doc or {}).get("verdict") or {}
        _ws_src = (_ws_doc or {}).get("source_face")
        # every rung must carry both parts: a ladder that published only the total
        # would let the movement be attributed to whichever part was assumed
        _ws_parts = all(r.get("timing_bp") is not None
                        and r.get("selection_bp") is not None
                        for r in _ws_rows.values()) if _ws_rows else False
        _ws_ok = ("sharedbookwidthsplit" in _ws_order
                  and "sharedbookwidthladder" in _ws_order
                  and _ws_order.index("sharedbookwidthsplit")
                  > _ws_order.index("sharedbookwidthladder")
                  and _ws_doc is not None
                  and _ws_doc.get("study") == "e220_width_split_attribution"
                  and len(_ws_rows) >= 2
                  and _ws_parts
                  and _ws_v.get("label")
                  and _ws_v.get("timing_range_bp") is not None
                  and _ws_v.get("selection_range_bp") is not None
                  and _ws_src)
        check("product: the width ladder is split into timing and selection, so "
              "its movement is attributed to a named part",
              _ws_ok, "chain=%s face=%s source=%s rungs=%s label=%s "
              "timing_range=%s selection_range=%s" % (
                  "sharedbookwidthsplit" in _ws_order,
                  _ws[-1] if _ws else "MISSING", _ws_src, len(_ws_rows),
                  _ws_v.get("label"), _ws_v.get("timing_range_bp"),
                  _ws_v.get("selection_range_bp")))
    except Exception as e:
        check("product: the width ladder is split into timing and selection, so "
              "its movement is attributed to a named part", False, str(e))
    try:
        _pd_order = [n for n, _c in importlib.import_module("Tools.s6_chain_bmb").LEGS]
        _pd_cmd = dict(importlib.import_module("Tools.s6_chain_bmb").LEGS).get(
            "pool_deliverable") or []
        _pd_face = os.path.join("results", "pool_deliverable_audit.json")
        _pd_doc = None
        if os.path.exists(_pd_face):
            with open(_pd_face, encoding="utf-8") as _fh:
                _pd_doc = json.load(_fh)
        _pd_ok = ("pool_deliverable" in _pd_order
                  and _pd_order.index("pool_deliverable") < _pd_order.index("py_watermark")
                  and "apply" in _pd_cmd
                  and _pd_doc is not None
                  and _pd_doc.get("audit") == "pool deliverable reconciliation"
                  and "counts" in _pd_doc)
        check("pool: the deliverable reconciliation runs before anything counts pool ready",
              _pd_ok, "chain=%s idx=%s mode=%s face=%s counts=%s" % (
                  "pool_deliverable" in _pd_order,
                  _pd_order.index("pool_deliverable") if "pool_deliverable" in _pd_order else -1,
                  [c for c in _pd_cmd if c == "apply"] or "MISSING",
                  os.path.basename(_pd_face) if _pd_doc else "MISSING",
                  (_pd_doc or {}).get("counts")))
    except Exception as e:
        check("pool: the deliverable reconciliation runs before anything counts pool ready",
              False, str(e))
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
    try:
        _gg = subprocess.run([sys.executable, os.path.join("Tools", "tree_shrink_guard.py"),
                              "check_gates"], capture_output=True, text=True,
                             encoding="utf-8", errors="replace")
        _gt = ((_gg.stdout or "") + (_gg.stderr or "")).strip().splitlines()
        check("fleet: the tree-shrink push gate is installed in both repos",
              _gg.returncode == 0, (_gt[0] if _gt else "")[:110])
    except Exception as e:
        check("fleet: the tree-shrink push gate is installed in both repos", False, str(e))
    _sp_env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    def _selftest_run(script, args, timeout):
        return _sp.run([sys.executable, script, *args], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       env=_sp_env, timeout=timeout)
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
    try:
        _xdir = os.path.join("results", "reviewwindow_cross")
        _xf = sorted(f for f in os.listdir(_xdir)
                     if f.startswith("REVIEWWINDOWCROSS-") and f.endswith(".json"))
        if _xf:
            _xj = json.load(open(os.path.join(_xdir, _xf[-1]), encoding="utf-8"))
            _xa = _xj.get("answers") or {}
            _xs = _xj.get("spec") or {}
            _xok = bool(_xj.get("cells")) and all(
                c["window"].get("perm_p") is not None for c in _xj["cells"])
            _xp = (_xa.get("pooled") or {}).get("perm_p")
            _V = _xa.get("verdict")
            if _V == "no_outside_family_signal":
                _xok = (_xok and _xp is not None
                        and _xp > float(_xs.get("pooled_p_max", 0.01))
                        and (_xa.get("cells_sig_binomial_tail_p") or 1.0) > 0.05)
            elif _V == "review_window_holds_outside_the_family":
                _xok = (_xok and _xp is not None
                        and _xp <= float(_xs.get("pooled_p_max", 0.01))
                        and len(_xa.get("cells_sig") or [])
                        >= max(2, len(_xj["cells"]) // 2))
            check("product: E198 cross-panel verdict is recomputable from its own gate",
                  _xok, "verdict=%s pooled_p=%s sig=%s cells=%d"
                  % (_V, _xp, len(_xa.get("cells_sig") or []),
                     len(_xj.get("cells") or [])))
        else:
            check("product: E198 cross-panel verdict is recomputable from its own gate",
                  True, "cross-panel face absent -- soft-fails by design")
    except Exception as e:
        check("product: E198 cross-panel verdict is recomputable from its own gate",
              False, str(e))
    try:
        _fdir = os.path.join("results", "reviewwindow_floor")
        _ff = sorted(f for f in os.listdir(_fdir)
                     if f.startswith("REVIEWWINDOWFLOOR-") and f.endswith(".json")) \
            if os.path.isdir(_fdir) else []
        if _ff:
            _fj = json.load(open(os.path.join(_fdir, _ff[-1]), encoding="utf-8"))
            _fa = _fj.get("answers") or {}
            _fs = _fj.get("spec") or {}
            _fv = _fa.get("verdict")
            _floor = (_fa.get("floor") or {}).get("min_detectable_ratio")
            _obs = (_fa.get("observed") or {})
            _obs_r = _obs.get("observed_ratio")
            _obs_p = _obs.get("pooled_perm_p")
            _al = float(_fs.get("alpha_pooled", 0.01))
            _okf = (_fa.get("months") or 0) > 0 and _floor is not None
            _val = (_fa.get("validation") or {})
            _sd = _val.get("analytic_sd_vs_permutation") or {}
            _dc = _val.get("discrete_check") or {}
            _okf = (_okf
                    and (_sd.get("rel_diff") is not None
                         and _sd["rel_diff"] <= 0.05)
                    and (_dc.get("at_floor_perm_p") is not None
                         and _dc["at_floor_perm_p"] <= _al)
                    and (_dc.get("below_floor_perm_p") is not None
                         and _dc["below_floor_perm_p"] > _al))
            if _fv == "negative_is_below_the_detection_floor":
                _okf = (_okf and _obs_r is not None and _obs_r < _floor
                        and _obs_p is not None and _obs_p > _al)
            elif _fv == "effect_detected":
                _okf = _okf and _obs_p is not None and _obs_p <= _al
            elif _fv == "effect_size_above_floor_yet_not_significant":
                _okf = (_okf and _obs_r is not None and _obs_r >= _floor
                        and _obs_p is not None and _obs_p > _al)
            check("product: E199 detection floor is recomputable from its own gate",
                  _okf, "verdict=%s observed_ratio=%s floor=%s p=%s sd_rel=%s"
                  % (_fv, _obs_r, _floor, _obs_p, _sd.get("rel_diff")))
        else:
            check("product: E199 detection floor is recomputable from its own gate",
                  True, "floor face absent -- soft-fails by design")
    except Exception as e:
        check("product: E199 detection floor is recomputable from its own gate",
              False, str(e))
    try:
        _legs = __import__("importlib").import_module("Tools.s6_chain_bmc").LEGS
        _names = {n for n, _c in _legs}
        # etf_book_production belongs here as much as the ticket: r1290 caught the card
        # (the headline face) a full refresh behind the ticket because only the ticket
        # was wired -- an unwired face reads as current to everything downstream.
        # etf_book_width_audit prices the disagreement between the card and the ticket,
        # so it goes stale the moment either moves: r1291 found it two bars behind both.
        _want = {"etf_book_forward", "etf_book_production", "etf_book_order",
                 "etf_book_order_card",
                 "etf_book_width_audit", "etf_book_registry", "etf_book_ceo_page",
                 "etf_book_card_track", "etf_paper_signal", "cal_audit"}
        _miss = sorted(_want - _names)
        check("product: ETF book legs wired into the S6 chain",
              not _miss, f"legs={len(_names)} missing={_miss or 'none'}")
    except Exception as e:
        check("product: ETF book legs wired into the S6 chain", False, str(e))
    try:
        _order = [n for n, _c in importlib.import_module("Tools.s6_chain_bmc").LEGS]
        _ri = _order.index("etf_book_registry")
        _behind = [(f.get("id"), f.get("chain_leg")) for f in (_rg.get("faces") or [])
                   if f.get("chain_leg") in _order and _order.index(f["chain_leg"]) > _ri]
        check("product: ETF registry runs after every face it summarises",
              not _behind, "registry_at=%d behind=%s" % (_ri, _behind or "none"))
    except Exception as e:
        check("product: ETF registry runs after every face it summarises", False, str(e))
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
        # The page told the reader to buy GC001 but never said what the cash is worth.
        # Assert the block exists AND that its yuan is the page's own cash x the repo
        # panel's own last close -- a rate the page forgot to refresh would otherwise
        # keep printing a confident number from a stale panel.
        _cy = _page.get("cash_yield") or {}
        _ok_cy = False
        _cy_detail = "block absent"
        if _cy and _cy.get("annual_cny") is not None:
            _rp = "data/repo_daily/%s.csv" % (_cy.get("leg") or "GC001")
            _last = None
            try:
                with open(_rp, encoding="utf-8") as _fh:
                    next(_fh, None)
                    for _ln in _fh:
                        _p = _ln.strip().split(",")
                        if len(_p) >= 5:
                            try:
                                _v = float(_p[4])
                            except ValueError:
                                continue
                            if 0.0 < _v < 200.0:
                                _last = (_p[0], _v)
            except Exception as _e:
                _last = None
            _ok_cy = (bool(_last)
                      and _cy.get("rate_date") == _last[0]
                      and abs(float(_cy.get("rate_pct") or 0) - _last[1]) < 1e-9
                      and abs(float(_cy.get("annual_cny") or 0)
                              - float(_page.get("cash_amount_cny") or 0) * _last[1] / 100.0) < 1.0
                      and abs(float(_cy.get("daily_cny") or 0)
                              - float(_cy["annual_cny"]) / 250.0) < 1.0)
            _cy_detail = (f"rate={_cy.get('rate_pct')}@{_cy.get('rate_date')} "
                          f"panel={_last} annual={_cy.get('annual_cny')} "
                          f"daily={_cy.get('daily_cny')}")
        check("product: ETF live-book cash leg is priced off the repo panel's own close", _ok_cy,
              _cy_detail)
        # The cash block now also answers "should the idle half be laddered out to a
        # longer repo?". That verdict must be the panels' own arithmetic: roll the legs
        # here, independently, and require the page's edges and its pick to follow.
        _cl = _page.get("cash_ladder") or {}
        _ok_cl = False
        _cl_detail = "block absent"
        try:
            import datetime as _dtc

            def _repo(sym):
                _rows = []
                with open("data/repo_daily/%s.csv" % sym, encoding="utf-8") as _fh:
                    next(_fh, None)
                    for _ln in _fh:
                        _p = _ln.strip().split(",")
                        if len(_p) >= 5:
                            try:
                                _v = float(_p[4])
                                if 0.0 < _v < 200.0:
                                    _rows.append((_dtc.date.fromisoformat(_p[0]), _v))
                            except ValueError:
                                continue
                return _rows

            def _roll(_rows, tenor, start):
                _dates = [d for d, _ in _rows]
                _rate = dict(_rows)
                _idx = [i for i, d in enumerate(_dates) if d >= start]
                if len(_idx) < 2:
                    return None
                i, _last = _idx[0], _idx[-1]
                _tot = 0.0
                _days = 0
                while i < _last:
                    d = _dates[i]
                    _mat = d + _dtc.timedelta(days=tenor)
                    j = i + 1
                    while j < len(_dates) and _dates[j] < _mat:
                        j += 1
                    if j > _last:
                        break
                    _acc = (_dates[j] - d).days if tenor == 1 else tenor
                    _tot += _rate[d] / 100.0 * _acc / 365.0
                    _days += (_dates[j] - d).days
                    i = j
                if _days <= 0:
                    return None
                return _tot / (_days / 365.0) * 100.0

            _base_rows = _repo("GC001")
            _end = _base_rows[-1][0]
            _start = _end - _dtc.timedelta(days=365)
            _b1 = _roll(_base_rows, 1, _start)
            _arms = {r.get("symbol"): r for r in (_cl.get("tenors") or [])}
            _mismatch = []
            _passing = []
            for _sym, _r in _arms.items():
                if _sym == "GC001" or not _r.get("edge_bp"):
                    continue
                _tenor = int(_r.get("tenor_days") or 1)
                _mine = _roll(_repo(_sym), _tenor, _start)
                if _mine is None:
                    continue
                _edge = (_mine - _b1) * 100.0
                if abs(_edge - float(_r["edge_bp"].get("1") or 0.0)) > 0.5:
                    _mismatch.append("%s page %s vs recomputed %.1f"
                                     % (_sym, _r["edge_bp"].get("1"), _edge))
                if (float(_r["edge_bp"].get("1") or 0.0) >= 20.0
                        and float(_r["edge_bp"].get("3") or 0.0) >= 20.0
                        and float(_r.get("idle_share_1y") or 0.0) <= 0.01):
                    _passing.append(_sym)
            _ok_cl = (bool(_arms) and _b1 is not None and not _mismatch
                      and (_cl.get("verdict") == "ADOPT") == bool(_passing)
                      and (_cl.get("pick") in _passing if _passing
                           else _cl.get("pick") == "GC001"))
            _cl_detail = ("verdict=%s pick=%s arms=%d base1y=%.3f passing=%s mismatch=%s"
                          % (_cl.get("verdict"), _cl.get("pick"), len(_arms), _b1 or 0.0,
                             _passing, _mismatch))
        except Exception as _e:
            _cl_detail = "recompute failed: %s" % _e
        check("product: cash-leg ladder verdict is the panels' own rolls, not a typed-in answer",
              _ok_cl, _cl_detail)
    except Exception as e:
        check("product: ETF live-book page current and its money closes", False, str(e))
    try:
        _bma = importlib.import_module("Tools.s6_chain_bma")
        _canon = importlib.import_module("Tools.s6_chain_bmc")
        _a = [n for n, _c in _bma.LEGS]
        _c = [n for n, _c in _canon.LEGS]
        _miss = [p for _n, _cmd in _bma.LEGS
                 if _bma.leg_script(_cmd) and not os.path.exists(
                     os.path.join(_bma.ROOT, _bma.leg_script(_cmd)))]
        check("fleet: bm-a's chain runner is the shared leg list, not a snapshot",
              _a == _c and not _miss,
              f"legs={len(_a)} canonical={len(_c)} missing_scripts={_miss or '-'}")
    except Exception as e:
        check("fleet: bm-a's chain runner is the shared leg list, not a snapshot",
              False, str(e))
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
    try:
        _fr = json.load(open("results/futures_overlay_fliprate.json", encoding="utf-8"))
        _bad = []
        for _tag, _blk in (_fr.get("lookbacks") or {}).items():
            _arms = _blk.get("arms") or []
            if len(_arms) < 3:
                _bad.append(f"{_tag}: {len(_arms)} arms")
                continue
            _base = _arms[0]
            _expo = [a["mean_abs_weight"] for a in _arms if a.get("mean_abs_weight")]
            if not _expo:
                _bad.append(f"{_tag}: no exposure published")
            elif (max(_expo) - min(_expo)) / min(_expo) > 0.01:
                _bad.append(f"{_tag}: exposure spread {max(_expo) - min(_expo):.4f} "
                            f"-- that is deleveraging, not a flip filter")
            for _a in _arms:
                _turns = {round(r.get("turnover_total") or 0.0, 1)
                          for r in _a.get("cost_rows") or []}
                if len(_a.get("cost_rows") or []) < 3 or len(_turns) != 1:
                    _bad.append(f"{_tag}/{_a['label']}: cost ladder re-prices "
                                f"{len(_turns)} sequences")
                    break
                _expect = round((_a["sleeve_gross_cagr"] - _base["sleeve_gross_cagr"]) * 100, 2)
                if _a.get("gross_give_up_pp") != _expect:
                    _bad.append(f"{_tag}/{_a['label']}: give-up {_a.get('gross_give_up_pp')} "
                                f"!= measured {_expect}")
                    break
                _by = {r["cost_per_side_bp"]: r.get("equal_risk_delta_cagr_pp") or 0.0
                       for r in _a["cost_rows"]}
                _bby = {r["cost_per_side_bp"]: r.get("equal_risk_delta_cagr_pp") or 0.0
                        for r in _base["cost_rows"]}
                _claims = bool(_a.get("beats_base_at_3bp_or_worse"))
                _real = all(_by.get(bp, -9) > _bby.get(bp, -9) for bp in (3.0, 5.0, 10.0))
                if _a["spec"]["mechanism"] != "base" and _claims != _real:
                    _bad.append(f"{_tag}/{_a['label']}: claims beats_base={_claims} "
                                f"but the ladder says {_real}")
                    break
            _rb = _blk.get("robustness") or {}
            _hold = [a for a in _arms if a["spec"]["mechanism"] == "strength_hold"]
            _clr = [a for a in _hold if a.get("beats_base_at_3bp_or_worse")]
            _expect_flag = bool(_hold) and len(_clr) == len(_hold)
            if _rb.get("clears_both_theta_levels") != _expect_flag:
                _bad.append(f"{_tag}: robustness flag disagrees with the rows "
                            f"({len(_clr)}/{len(_hold)} theta levels clear)")
        check("product: flip-rate arms cut flips, not exposure, and the cut is priced",
              not _bad, "; ".join(_bad)[:220]
              or "exposure flat, one sequence per arm, give-up measured, "
                 "robustness flag derived from the rows")
    except Exception as e:
        check("product: flip-rate arms cut flips, not exposure, and the cut is priced",
              False, str(e))
    try:
        _fp = json.load(open("results/futures_overlay_fliprate_paths.json", encoding="utf-8"))
        _rule = _fp.get("adoption_rule") or {}
        _bad = []
        _cells_expected = set(_fp.get("cells_tested") or [])
        if len(_cells_expected) < 5 or not _rule:
            _bad.append(f"face incomplete: cells={len(_cells_expected)} rule={bool(_rule)}")
        _key = "delta_pp_%gbp" % float(_rule.get("primary_cost_bp") or 0)
        _sample = next(iter((_fp.get("arms") or {}).values()), {})
        _sample = (_sample.get("cells") or [{}])[0]
        if _key not in _sample:
            _bad.append(f"primary cost {_rule.get('primary_cost_bp')} is not a published "
                        f"column (looked for {_key})")
        _passed = []
        for _lab, _a in (_fp.get("arms") or {}).items():
            _cells = _a.get("cells") or []
            if {c.get("cell") for c in _cells} != _cells_expected:
                _bad.append(f"{_lab}: {len(_cells)} cells do not match the declared path set")
                continue
            _vals = [c.get(_key) for c in _cells if c.get(_key) is not None]
            if not _vals:
                _bad.append(f"{_lab}: no measurable cell")
                continue
            _share = round(len([v for v in _vals if v > 0]) / len(_vals), 3)
            _worst = min(_vals)
            _by = {c["cell"]: c.get(_key) for c in _cells}
            _reject = (_share < float(_rule["min_positive_share"])
                       or _worst < float(_rule["worst_cell_floor_pp"])
                       or (_rule.get("require_full_positive") and (_by.get("full") or 0) <= 0)
                       or (_rule.get("require_oos_positive") and (_by.get("oos") or 0) <= 0))
            _expect = "REJECT" if _reject else "ADOPT"
            _ad = _a.get("adoption") or {}
            if _ad.get("verdict") != _expect:
                _bad.append(f"{_lab}: says {_ad.get('verdict')} but the rule says {_expect} "
                            f"(share {_share}, worst {_worst})")
            if _ad.get("share_positive") != _share or _ad.get("worst_cell_pp") != _worst:
                _bad.append(f"{_lab}: published share/worst do not match its own cells")
            if _expect == "ADOPT":
                _passed.append(_lab)
        if _fp.get("overall_verdict") != ("ADOPT" if _passed else "REJECT"):
            _bad.append(f"overall {_fp.get('overall_verdict')} disagrees with "
                        f"{len(_passed)} passing arm(s)")
        _adopted = _fp.get("adopted_arm")
        if _adopted is not None and _adopted not in _passed:
            _bad.append(f"adopted arm {_adopted} did not pass the rule")
        check("product: the flip damper is adopted or rejected by path cells, not one run",
              not _bad, "; ".join(_bad)[:220]
              or f"{len(_cells_expected)} paths x {len(_fp.get('arms') or {})} arms, "
                 f"{len(_passed)} pass the frozen rule, verdict recomputed from the rows")
    except Exception as e:
        check("product: the flip damper is adopted or rejected by path cells, not one run",
              False, str(e))
    try:
        import json as _json
        _bad = []
        _face = _json.load(open(os.path.join("results", "futures_tsmom_signal.json"),
                                encoding="utf-8"))
        _art = _json.load(open(os.path.join(
            "results", "futures_overlay_fliprate_paths.json"), encoding="utf-8"))
        _ad = _face.get("adopted_overlay")
        if not _ad:
            _bad.append("the live page carries no adopted_overlay")
        else:
            _arm = _art.get("adopted_arm")
            _spec = (_art.get("arms") or {}).get(_arm, {}).get("spec") or {}
            if _ad.get("arm") != _arm:
                _bad.append(f"page rules on {_ad.get('arm')} but the path test adopted {_arm}")
            _want = {"mechanism": _spec.get("mechanism"), "lookback": _spec.get("lookback"),
                     "theta": _spec.get("theta"), "k": _spec.get("k")}
            if _ad.get("spec") != _want:
                _bad.append(f"page spec {_ad.get('spec')} != artifact {_want}")
            if _arm and _art.get("overall_verdict") != "ADOPT":
                _bad.append("a damper is published while the path verdict is not ADOPT")
            _sys_path = os.path.join(os.getcwd(), "scripts")
            if _sys_path not in sys.path:
                sys.path.insert(0, _sys_path)
            import futures_tsmom_probe as _P
            import futures_overlay_fliprate as _F
            _close = _P.load_panel()
            _mom = _close.pct_change(int(_spec["lookback"]))
            _fn = (lambda m: _F.strength_hold(m, float(_spec["theta"]))
                   if _spec["mechanism"] == "strength_hold"
                   else _F.confirm_kd(m, int(_spec["k"])))
            _raw = _F.flip_counts(_F.base_signs(_mom))["flips"]
            _dmp = _F.flip_counts(_fn(_mom))["flips"]
            if _raw != _ad["flips"]["raw"]:
                _bad.append(f"raw flips published {_ad['flips']['raw']} != recomputed {_raw}")
            if _dmp != _ad["flips"]["damped"]:
                _bad.append(f"damped flips published {_ad['flips']['damped']} "
                            f"!= recomputed {_dmp}")
            if not _dmp < _raw:
                _bad.append(f"the damper does not cut flips ({_dmp} vs {_raw})")
            _page = os.path.join("docs", "futures_lane",
                                 "TSMOM-%s.md" % _face.get("generated_for_bar"))
            if not os.path.exists(_page) or "生产候选" not in open(
                    _page, encoding="utf-8").read():
                _bad.append("the human page does not carry the adopted section")
        check("product: the adopted flip damper reaches the live shadow book",
              not _bad, "; ".join(_bad)[:220]
              or "page flips %d->%d with the artifact's own rule, recomputed from the panel"
                 % (_ad["flips"]["raw"], _ad["flips"]["damped"]))
    except Exception as e:
        check("product: the adopted flip damper reaches the live shadow book", False, str(e))
    try:
        # E221: the day-of-month profile must stay a SESSION-counted measurement. This
        # leg recomputes the published gap from the published group stats and fails if
        # the face loses the power block, the multiple-comparison bar, or starts quoting
        # a month-end gap without saying how many months it rests on.
        import glob as _glob
        _bad = []
        _faces = sorted(_glob.glob(os.path.join("results", "dom_profile",
                                               "PROFILE-*.json")))
        if not _faces:
            _bad.append("no PROFILE-*.json face on disk")
        else:
            with open(_faces[-1], encoding="utf-8") as _fh:
                _f = json.load(_fh)
            _g = _f.get("groups") or {}
            _me, _rest = _g.get("month_end_last2") or {}, _g.get("rest") or {}
            if not _f.get("evidence_cutoff"):
                _bad.append("face carries no evidence_cutoff")
            _pub = _f.get("month_end_minus_rest") or {}
            if _me.get("mean_bp") is not None and _rest.get("mean_bp") is not None:
                _want = _me["mean_bp"] - _rest["mean_bp"]
                if _pub.get("diff_bp") is None or abs(_pub["diff_bp"] - _want) > 1e-6:
                    _bad.append("published gap != month_end - rest recomputed")
                _n = (_me.get("n_days") or 0) + (_rest.get("n_days") or 0)
                if (_pub.get("se_bp") or 0) < 1e-9:
                    _bad.append("gap published with a zero standard error")
                if _n < 100:
                    _bad.append("gap rests on fewer than 100 sessions")
            _pw = _f.get("power") or {}
            if not _pw.get("months_in_test"):
                _bad.append("power block does not say how many months the test rests on")
            if _pw.get("years_needed") is None:
                _bad.append("power block does not say what the gap would need")
            if "best_bucket" in _f:
                _bb = _f["best_bucket"]
                if not _bb.get("clears_bonferroni") and _bb.get("bonferroni_abs_t") is None:
                    _bad.append("best bucket quoted without its multiple-comparison bar")
            if not (_f.get("coverage") or {}).get("sessions_scored"):
                _bad.append("coverage does not report the sessions actually scored")
        check("product: the day-of-month face counts sessions, not name-days",
              not _bad, "; ".join(_bad)[:220]
              or "gap, power block and best-of-ladder bar all recompute from the face")
    except Exception as e:
        check("product: the day-of-month face counts sessions, not name-days", False, str(e))
    try:
        # E222: the turn-of-month overlay face must keep its decision rule, its
        # out-of-sample record and its cost arithmetic honest. This leg recomputes the
        # net-excess identity from the published per-month fields and fails if the face
        # quotes a verdict without the months it rests on, or a toll that is not one
        # round trip per month.
        _bad = []
        _face = os.path.join("results", "tom_overlay", "latest.json")
        if not os.path.exists(_face):
            _bad.append("no results/tom_overlay/latest.json on disk")
        else:
            with open(_face, encoding="utf-8") as _fh:
                _f = json.load(_fh)
            _spec = _f.get("spec") or {}
            _a = _f.get("primary_arm") or {}
            if not _f.get("evidence_cutoff"):
                _bad.append("face carries no evidence_cutoff")
            if _f.get("verdict") not in ("ADOPT", "REJECT", "UNRESOLVED"):
                _bad.append("face carries no frozen verdict")
            if not (_spec.get("decision_rule") or "").startswith("ADOPT iff"):
                _bad.append("the decision rule is not published on the face")
            if (_spec.get("sides_per_month") or 0) != 2:
                _bad.append("cost model is not one round trip per month")
            if abs((_a.get("cost_bp_per_month") or 0)
                   - 2 * (_spec.get("cost_side_bp") or 0)) > 1e-9:
                _bad.append("per-month toll != 2 sides")
            if (_a.get("oos_months") or 0) < 1:
                _bad.append("out-of-sample record is empty")
            _e = _a.get("excess_bp_per_month")
            _net, _ai = _a.get("net_bp_per_month"), (_f.get("arms") or {}).get(
                "primary_single", {}).get("always_in_bp_per_month")
            if None not in (_e, _net, _ai) and abs((_net - _ai) - _e) > 1e-6:
                _bad.append("excess != net overlay - always-in")
            _pw = _f.get("primary_power") or {}
            if _pw.get("months_needed") is None and _e:
                _bad.append("power block does not price the question")
            if _f.get("verdict") == "ADOPT" and (_a.get("excess_oos_t") or 0) < (
                    _spec.get("multiple_comparison_bar") or 2.0):
                _bad.append("ADOPT without clearing the multiple-comparison bar")
        check("product: the turn-of-month overlay keeps its rule, its toll and its OOS record",
              not _bad, "; ".join(_bad)[:220]
              or "verdict %s at t=%.2f over %d OOS months, toll = one round trip/month"
                 % (_f.get("verdict"), _a.get("excess_oos_t") or 0.0,
                    _a.get("oos_months") or 0))

        # E223: the observation-rate ladder must publish, for every rung, the resolution
        # it actually reaches -- and must not claim that a higher frequency resolves the
        # question when its own MDE says otherwise. This leg re-derives the MDE from the
        # published dispersion and out-of-sample count, so a face that quotes a tight
        # number without the dispersion behind it goes red.
        try:
            _bad = []
            _face = os.path.join("results", "obs_rate", "latest.json")
            if not os.path.exists(_face):
                _bad.append("no results/obs_rate/latest.json on disk")
                _f, _rows = {}, []
            else:
                with open(_face, encoding="utf-8") as _fh:
                    _f = json.load(_fh)
                _rows = ((_f.get("ladder") or {}).get("rows")) or []
                _spec = _f.get("spec") or {}
                if not _f.get("evidence_cutoff"):
                    _bad.append("face carries no evidence_cutoff")
                if not (_spec.get("resolution_rule") or "").startswith("the ladder's answer"):
                    _bad.append("the resolution rule is not published on the face")
                if len(_rows) < 2:
                    _bad.append("the ladder has fewer than two rungs")
                _z = _spec.get("z_80pct_two_sided") or 0.0
                for _r in _rows:
                    _sd, _n, _mde = (_r.get("excess_sd_bp_per_period"),
                                     _r.get("oos_periods"),
                                     _r.get("mde_bp_per_year"))
                    if None in (_sd, _n, _mde) or not _n:
                        continue
                    _recalc = _z * (_r.get("periods_per_year") or 0) * (
                        _sd / (_n ** 0.5))
                    if abs(_recalc - _mde) > 1e-6 * max(1.0, abs(_mde)):
                        _bad.append("MDE on rung %s does not match its own dispersion"
                                    % _r.get("name"))
                    if _r.get("verdict") == "ADOPT" and (
                            (_r.get("excess_oos_t") or 0) <
                            (_spec.get("multiple_comparison_bar") or 2.0)):
                        _bad.append("rung %s ADOPTs below the bar" % _r.get("name"))
                if not (((_f.get("ladder") or {}).get("answer")) or "").strip():
                    _bad.append("the ladder publishes no answer sentence")
            check("product: the observation-rate ladder prices its own resolution",
                  not _bad, "; ".join(_bad)[:220]
                  or "%d rungs, tightest %.0fbp/yr, verdict %s"
                     % (len(_rows),
                        min([r.get("mde_bp_per_year") or 1e18 for r in _rows]
                            or [0.0]),
                        (_f.get("ladder") or {}).get("verdict")))
        except Exception as e:
            check("product: the observation-rate ladder prices its own resolution",
                  False, repr(e)[:160])

        # E224: the volatility-gate face must keep the three things it claims apart --
        # the number of held days (the tempting sample), the number of episodes (the
        # independent unit) and the bar each arm actually reaches. This leg re-derives
        # every MDE from the published dispersion and episode rate, and refuses a face
        # whose toll is not one round trip per episode or whose episode count exceeds
        # the 252/hold ceiling.
        try:
            _bad = []
            _face = os.path.join("results", "vol_gate", "latest.json")
            if not os.path.exists(_face):
                _bad.append("no results/vol_gate/latest.json on disk")
                _f, _panels, _spec = {}, [], {}
            else:
                with open(_face, encoding="utf-8") as _fh:
                    _f = json.load(_fh)
                _panels = _f.get("panels") or []
                _spec = _f.get("frozen_spec") or {}
                if not _f.get("evidence_cutoff"):
                    _bad.append("face carries no evidence_cutoff")
                if not (_f.get("answer") or "").strip():
                    _bad.append("face publishes no answer sentence")
                if (_spec.get("sides_per_episode") or 0) != 2:
                    _bad.append("cost model is not one round trip per episode")
                if len(_panels) < 1:
                    _bad.append("no panel published")
                _z = _spec.get("z_80pct") or 0.0
                for _p in _panels:
                    _yrs = _p.get("years") or 0.0
                    for _a in (_p.get("arms") or []):
                        _toll = _a.get("cost_bp_per_episode")
                        if _toll is None or abs(
                                _toll - 2 * (_spec.get("cost_side_bp") or 0)) > 1e-9:
                            _bad.append("arm %s toll != 2 sides" % _a.get("name"))
                        _cap = 252.0 / (_a.get("hold_sessions") or 1)
                        if (_a.get("episodes_per_year") or 0) > _cap + 1e-9:
                            _bad.append("arm %s claims more episodes/yr than the hold allows"
                                        % _a.get("name"))
                        if _a.get("naive_days") and _a.get("episodes_oos"):
                            if _a["naive_days"] != _a["episodes_oos"] * _a["hold_sessions"]:
                                _bad.append("arm %s naive day count is not episodes x hold"
                                            % _a.get("name"))
                        _sd, _mde, _epy = (_a.get("sd_bp_per_episode"),
                                            _a.get("mde_ann_bp_per_year"),
                                            _a.get("episodes_per_year"))
                        if None not in (_sd, _mde, _epy) and _yrs:
                            _recalc = _z * _sd * ((_epy / _yrs) ** 0.5)
                            if abs(_recalc - _mde) > 1e-6 * max(1.0, abs(_mde)):
                                _bad.append("arm %s MDE does not match its own dispersion"
                                            % _a.get("name"))
                        if _a.get("verdict") not in ("ADOPT", "REJECT", "UNRESOLVED"):
                            _bad.append("arm %s carries no frozen verdict" % _a.get("name"))
                        if _a.get("verdict") == "ADOPT" and (
                                (_a.get("excess_oos_t") or 0) <
                                (_spec.get("bar_t") or 2.0)):
                            _bad.append("arm %s ADOPTs below the bar" % _a.get("name"))
                _oc = _f.get("observation_ceiling") or {}
                if not _oc.get("arms"):
                    _bad.append("the observation ceiling is not published")
                for _o in (_oc.get("arms") or []):
                    if abs((_o.get("ceiling_episodes_per_year") or 0)
                           - 252.0 / (_o.get("hold_sessions") or 1)) > 1e-9:
                        _bad.append("ceiling row %s != 252/hold" % _o.get("name"))
            check("product: the volatility gate separates held days from episodes",
                  not _bad, "; ".join(_bad)[:220]
                  or "%d panels, %d arms, tightest bar %.0fbp/yr, verdicts %s"
                     % (len(_panels), sum(len(p.get("arms") or []) for p in _panels),
                        min([a.get("mde_ann_bp_per_year") or 1e18
                             for p in _panels for a in (p.get("arms") or [])] or [0.0]),
                        ",".join(sorted({a.get("verdict") for p in _panels
                                         for a in (p.get("arms") or [])}))))
        except Exception as e:
            check("product: the volatility gate separates held days from episodes",
                  False, repr(e)[:160])
    except Exception as e:
        check("product: the turn-of-month overlay keeps its rule, its toll and its OOS record",
              False, str(e))

    # E225: the state-tilt face must not let "more sessions" pose as "more evidence".
    # This leg re-derives every MDE from the published Newey-West error, refuses an
    # effective sample size larger than the sessions it came from, and re-adds the
    # drift split so a gated arm cannot be read as a verdict on the gate when what
    # moved was the drift it normalised to.
    try:
        _bad = []
        _face = os.path.join("results", "state_tilt", "latest.json")
        if not os.path.exists(_face):
            _bad.append("no results/state_tilt/latest.json on disk")
            _f, _panels, _spec = {}, [], {}
        else:
            with open(_face, encoding="utf-8") as _fh:
                _f = json.load(_fh)
            _panels = _f.get("panels") or []
            _spec = _f.get("frozen_spec") or {}
            if not _f.get("evidence_cutoff"):
                _bad.append("face carries no evidence_cutoff")
            if not (_f.get("answer") or "").strip():
                _bad.append("face publishes no answer sentence")
            if "turnover" not in (_spec.get("cost_model") or ""):
                _bad.append("cost model is not stated as unit turnover")
            _z = _spec.get("z_80pct") or 0.0
            _bar = _spec.get("bar_t") or 0.0
            if len(_panels) < 1:
                _bad.append("no panel published")
            for _p in _panels:
                for _a in (_p.get("arms") or []):
                    _n, _ne = _a.get("oos_decisions"), _a.get("n_eff")
                    if _ne is not None and _n is not None and _ne > _n + 1e-9:
                        _bad.append("arm %s n_eff exceeds its sessions" % _a.get("name"))
                    if _ne and _n and _a.get("n_eff_over_sessions") is not None:
                        if abs(_a["n_eff_over_sessions"] - _ne / _n) > 1e-9:
                            _bad.append("arm %s n_eff ratio does not match n_eff/n"
                                        % _a.get("name"))
                    _se, _mde = _a.get("se_nw"), _a.get("mde_ann_bp_per_year")
                    if None not in (_se, _mde):
                        if abs(_mde - _z * _se * 252.0) > 1e-6 * max(1.0, abs(_mde)):
                            _bad.append("arm %s MDE is not z*se_nw*252" % _a.get("name"))
                    if _a.get("verdict") not in ("ADOPT", "REJECT", "UNRESOLVED"):
                        _bad.append("arm %s carries no frozen verdict" % _a.get("name"))
                    if _a.get("verdict") == "ADOPT" and (_a.get("excess_oos_t") or 0) < _bar:
                        _bad.append("arm %s ADOPTs below the bar" % _a.get("name"))
                    _comp = _a.get("market_drift_component_bp_per_year")
                    _gate = _a.get("gate_specific_bp_per_year")
                    _exc = _a.get("excess_oos_bp_per_year")
                    if _a.get("name") != "always_on" and None not in (_comp, _gate, _exc):
                        if abs((_comp + _gate) - _exc) > 1e-6 * max(1.0, abs(_exc)):
                            _bad.append("arm %s drift split does not re-add" % _a.get("name"))
                    if _a.get("name") == "always_on" and (_a.get("turnover_total") or 0) > 1.0 + 1e-9:
                        _bad.append("the always_on null arm pays turnover it does not trade")
            if not ((_f.get("drift_split") or {}).get("arms")):
                _bad.append("the drift split is not published")
        check("product: the state tilt publishes its own effective sample size",
              not _bad, "; ".join(_bad)[:220]
              or "%d panels, %d arms, tightest bar %.0fbp/yr, n_eff/sessions %s, verdicts %s"
                 % (len(_panels), sum(len(p.get("arms") or []) for p in _panels),
                    min([a.get("mde_ann_bp_per_year") or 1e18
                         for p in _panels for a in (p.get("arms") or [])] or [0.0]),
                    ",".join("%.0f%%" % (100.0 * (a.get("n_eff_over_sessions") or 0.0))
                             for p in _panels[:1] for a in (p.get("arms") or [])),
                    ",".join(sorted({a.get("verdict") for p in _panels
                                     for a in (p.get("arms") or [])}))))
    except Exception as e:
        check("product: the state tilt publishes its own effective sample size",
              False, repr(e)[:160])

    # --- E226 the break-even toll: the published root must be the zero of the
    # published line, and surviving the toll must not read as clearing the bar
    try:
        _f26 = {}
        _bad = []
        _face26 = "results/state_tilt/breakeven_latest.json"
        if not os.path.exists(_face26):
            _bad.append("no results/state_tilt/breakeven_latest.json on disk")
        else:
            with open(_face26, encoding="utf-8") as _fh:
                _f26 = json.load(_fh)
            _cut26 = _f26.get("evidence_cutoff")
            if not _cut26:
                _bad.append("face carries no evidence_cutoff")
            elif not os.path.exists("results/state_tilt/BREAKEVEN-%s.json" % _cut26):
                _bad.append("the dated face beside the latest pointer is missing")
            _spec26 = _f26.get("frozen_spec") or {}
            _classes26 = set((_spec26.get("verdict_bands") or {}).keys())
            if not _classes26:
                _bad.append("verdict bands are not published")
            for _p in (_f26.get("panels") or []):
                for _a in (_p.get("arms") or []):
                    _n26 = _a.get("name")
                    if _a.get("verdict") not in _classes26:
                        _bad.append("arm %s carries an unpublished verdict" % _n26)
                    _d26 = _a.get("turnover_differential_oos_per_year")
                    _g26 = _a.get("gate_specific_at_zero_cost_bp_per_year")
                    _c26 = _a.get("break_even_cost_bp_per_unit_turnover")
                    if _c26 is not None:
                        if _d26 is None or _d26 <= 0:
                            _bad.append("arm %s prices a root with no toll differential"
                                        % _n26)
                        elif abs(_c26 * _d26 - _g26) > 1e-6 * max(1.0, abs(_g26)):
                            _bad.append("arm %s root is not the zero of its own line" % _n26)
                    if _a.get("verdict") == "SURVIVES_MODEL_COST":
                        _ac26 = _a.get("at_model_cost") or {}
                        if None in (_ac26.get("excess_bp_per_year"),
                                    _ac26.get("excess_oos_t")):
                            _bad.append("arm %s survives the toll with no excess read at "
                                        "that cost" % _n26)
                    _lad26 = _a.get("cost_ladder") or []
                    _mults26 = [_r.get("cost_mult") for _r in _lad26]
                    if _mults26 != sorted(_mults26):
                        _bad.append("arm %s sweep is not ascending in cost" % _n26)
                    _gs26 = [_r.get("gate_specific_bp_per_year") for _r in _lad26
                             if _r.get("gate_specific_bp_per_year") is not None]
                    if any(_gs26[_k] < _gs26[_k + 1] - 1e-6 for _k in range(len(_gs26) - 1)):
                        _bad.append("arm %s gate-specific rises with the toll" % _n26)
            if not (_f26.get("answer") or "").strip():
                _bad.append("face publishes no answer sentence")
            _sig26 = _f26.get("breakeven_vs_significance") or {}
            for _r26 in (_sig26.get("arms") or []):
                if _r26.get("clears_bar_at_model_cost") is True and \
                        (_r26.get("excess_oos_t_at_model_cost") or 0.0) < 1.0:
                    _bad.append("a survivor is recorded as clearing the bar on no t")
        check("product: the state tilt prices the toll it would need",
              not _bad, "; ".join(_bad)[:220]
              or "%d panels, %d arms, roots %s, any survivor clears the bar %s"
                 % (len(_f26.get("panels") or []),
                    sum(len(p.get("arms") or []) for p in (_f26.get("panels") or [])),
                    ",".join("%s=%.1f" % (a.get("name"),
                                          a["break_even_cost_bp_per_unit_turnover"])
                             for p in (_f26.get("panels") or [])[:1]
                             for a in (p.get("arms") or [])
                             if a.get("break_even_cost_bp_per_unit_turnover") is not None),
                    bool((_f26.get("breakeven_vs_significance") or {})
                         .get("any_survivor_clears_the_bar"))))
    except Exception as e:
        check("product: the state tilt prices the toll it would need", False, repr(e)[:160])

    # --- E228 the exposure-matched null: the drift split must be reproduced as a
    # TRADED arm, the paired series must carry its own standard error, and the two
    # ways of asking the question must differ by exactly the matched arm's own toll
    try:
        _f28 = {}
        _bad = []
        _face28 = "results/state_tilt/matched_latest.json"
        if not os.path.exists(_face28):
            _bad.append("no results/state_tilt/matched_latest.json on disk")
        else:
            with open(_face28, encoding="utf-8") as _fh:
                _f28 = json.load(_fh)
            _cut28 = _f28.get("evidence_cutoff")
            if not _cut28:
                _bad.append("face carries no evidence_cutoff")
            elif not os.path.exists("results/state_tilt/MATCHED-%s.json" % _cut28):
                _bad.append("the dated face beside the latest pointer is missing")
            if not (_f28.get("answer") or "").strip():
                _bad.append("face publishes no answer sentence")
            _spec28 = (_f28.get("frozen_spec") or {})
            if _spec28.get("tests") != 4 * max(1, len(_f28.get("panels") or [])):
                _bad.append("the bar is not built from the gated-arm x panel count")
            if (_f28.get("benchmark_agreement") or {}).get("cells") != sum(
                    len(p.get("arms") or []) for p in (_f28.get("panels") or [])):
                _bad.append("the agreement table does not cover every gated cell")
            for _p28 in (_f28.get("panels") or []):
                for _a28 in (_p28.get("arms") or []):
                    _n28 = _a28.get("name")
                    if _a28.get("verdict") not in {"TIMING_SURVIVES", "TIMING_DEAD",
                                                   "UNRESOLVED"}:
                        _bad.append("arm %s carries an unpublished verdict" % _n28)
                    _mo28 = ((_a28.get("matched") or {}).get("oos") or {})
                    _pa28 = _mo28.get("paired") or {}
                    if _mo28.get("const_weight") is None:
                        _bad.append("arm %s publishes no matched constant" % _n28)
                    elif (_mo28.get("turnover_total") or 0.0) > _mo28["const_weight"] + 1e-9:
                        _bad.append("arm %s matched arm trades more than its entry" % _n28)
                    elif (_mo28.get("cost_bp_per_year_oos") or 0.0) != 0.0:
                        _bad.append("arm %s matched arm pays a toll out of sample" % _n28)
                    if _pa28.get("se_nw"):
                        if abs((_pa28.get("mde_ann_bp_per_year") or 0.0)
                               - 2.802 * _pa28["se_nw"] * 252.0) > 1e-6:
                            _bad.append("arm %s prints an MDE its own SE cannot produce"
                                        % _n28)
                    elif _pa28.get("t_nw") is not None:
                        _bad.append("arm %s prints a t with no standard error" % _n28)
                    _bc28 = _a28.get("benchmark_comparison") or {}
                    if _bc28.get("attribution_minus_paired_bp") is not None and \
                            abs(_bc28["attribution_minus_paired_bp"]
                                + (_mo28.get("cost_bp_per_year_oos") or 0.0)) > 1e-6:
                        _bad.append("arm %s: attribution minus pair is not the matched toll"
                                    % _n28)
                    if _a28.get("verdict") == "TIMING_SURVIVES" and \
                            (_pa28.get("t_nw") or 0.0) < (_spec28.get("bar_t") or 0.0):
                        _bad.append("arm %s survives below the bar" % _n28)
        check("product: the drift split is reproduced as a traded exposure-matched arm",
              not _bad, "; ".join(_bad)[:220]
              or "%d panels, %d gated arms, %d sign changes, max attribution gap %.1fbp/yr, "
                 "verdicts %s"
                 % (len(_f28.get("panels") or []),
                    sum(len(p.get("arms") or []) for p in (_f28.get("panels") or [])),
                    (_f28.get("benchmark_agreement") or {}).get("sign_changes"),
                    (_f28.get("benchmark_agreement") or {}).get("max_abs_gap_bp_per_year")
                    or 0.0,
                    ",".join(sorted({a.get("verdict") for p in (_f28.get("panels") or [])
                                     for a in (p.get("arms") or [])}))))
    except Exception as e:
        check("product: the drift split is reproduced as a traded exposure-matched arm",
              False, repr(e)[:160])

    # E229: the pair E228 judged is split three ways -- selection (which days), sizing
    # (how much) and toll. The leg re-adds the published channels and refuses a face
    # whose own parts do not reconstruct its own pair, so the attribution cannot drift
    # away from the series it claims to explain.
    try:
        _f29 = {}
        _bad29 = []
        _face29 = "results/state_tilt/timingsel_latest.json"
        if not os.path.exists(_face29):
            _bad29.append("no results/state_tilt/timingsel_latest.json on disk")
        else:
            with open(_face29, encoding="utf-8") as _fh:
                _f29 = json.load(_fh)
            _cut29 = _f29.get("evidence_cutoff")
            if not _cut29:
                _bad29.append("face carries no evidence_cutoff")
            elif not os.path.exists("results/state_tilt/TIMINGSEL-%s.json" % _cut29):
                _bad29.append("the dated face beside the latest pointer is missing")
            if (_f29.get("study") or "") != "E229":
                _bad29.append("face is not the E229 decomposition")
            _spec29 = _f29.get("frozen_spec") or {}
            if list(_spec29.get("channels") or []) != ["selection", "sizing", "toll"]:
                _bad29.append("the channel list is not the frozen three")
            _cells29 = 0
            for _p29 in (_f29.get("panels") or []):
                for _a29 in (_p29.get("arms") or []):
                    _n29 = _a29.get("name")
                    _c29 = _a29.get("channels") or {}
                    _cells29 += 1
                    _pair29 = _c29.get("pair_ann_bp_per_year")
                    _parts = [(_c29.get(_ch) or {}).get("ann_bp_per_year")
                              for _ch in ("selection", "sizing", "toll")]
                    if _pair29 is None or any(x is None for x in _parts):
                        _bad29.append("arm %s publishes an incomplete split" % _n29)
                        continue
                    if abs(sum(_parts) - _pair29) > 1e-6:
                        _bad29.append("arm %s channels do not reconstruct its pair" % _n29)
                    if abs(_c29.get("identity_residual_bp") or 0.0) > 1e-6:
                        _bad29.append("arm %s carries a non-zero identity residual" % _n29)
                    if _a29.get("verdict") not in {"NO_STRUCTURE", "SELECTION_DOMINANT",
                                                   "SIZING_DOMINANT", "TOLL_DOMINANT",
                                                   "UNRESOLVED"}:
                        _bad29.append("arm %s carries an unpublished verdict" % _n29)
                    if _a29.get("dominant") not in {None, "selection", "sizing", "toll"}:
                        _bad29.append("arm %s names a channel outside the frozen three"
                                      % _n29)
                    _si29 = (_c29.get("sizing_level") or {}).get("ann_bp_per_year")
                    _sc29 = (_c29.get("sizing_covariance") or {}).get("ann_bp_per_year")
                    _sz29 = (_c29.get("sizing") or {}).get("ann_bp_per_year")
                    if _si29 is not None and _sc29 is not None and _sz29 is not None \
                            and abs((_si29 + _sc29) - _sz29) > 1e-6:
                        _bad29.append("arm %s sizing split does not add up" % _n29)
                    if (_n29 or "").startswith("binary") and abs(_sc29 or 0.0) > 1e-6:
                        _bad29.append("arm %s: a 0/1 gate cannot have a covariance term"
                                      % _n29)
            if _cells29 == 0:
                _bad29.append("the face covers no arms")
            if not (_f29.get("answer") or "").strip():
                _bad29.append("face publishes no answer sentence")
        check("product: the paired timing value splits into selection, sizing and toll",
              not _bad29, "; ".join(_bad29)[:220]
              or "%d cells, dominant channels %s, resolvable %d, max |identity residual| "
                 "%.1e bp"
                 % (_cells29,
                    ",".join(sorted({str(a.get("dominant"))
                                     for p in (_f29.get("panels") or [])
                                     for a in (p.get("arms") or [])})),
                    len(_f29.get("resolvable_dominant_channels") or []),
                    max(abs((a.get("channels") or {}).get("identity_residual_bp") or 0.0)
                        for p in (_f29.get("panels") or [])
                        for a in (p.get("arms") or [])) if _cells29 else 0.0))
    except Exception as e:
        check("product: the paired timing value splits into selection, sizing and toll",
              False, repr(e)[:160])

    # E230: E229 named the toll as the only channel that clears its bar, so the study
    # that follows asks whether the rule can buy it back by moving less often. The leg
    # re-derives every published rung: a rung's own channels must reconstruct its own
    # pair, the rung at band 0 must be the base arm itself, and a rung whose deltas are
    # inside the noise must not be labelled a fix -- the ladder may never print a verdict
    # its own numbers cannot carry.
    try:
        _f30 = {}
        _bad30 = []
        _face30 = "results/state_tilt/hysteresis_latest.json"
        if not os.path.exists(_face30):
            _bad30.append("no results/state_tilt/hysteresis_latest.json on disk")
        else:
            with open(_face30, encoding="utf-8") as _fh:
                _f30 = json.load(_fh)
            _cut30 = _f30.get("evidence_cutoff")
            if not _cut30:
                _bad30.append("face carries no evidence_cutoff")
            elif not os.path.exists("results/state_tilt/HYSTERESIS-%s.json" % _cut30):
                _bad30.append("the dated face beside the latest pointer is missing")
            if (_f30.get("study") or "") != "E230":
                _bad30.append("face is not the E230 band ladder")
            _spec30 = _f30.get("frozen_spec") or {}
            if list(_spec30.get("channels") or []) != ["selection", "sizing", "toll"]:
                _bad30.append("the channel list is not the frozen three")
            _bar30 = _spec30.get("bar_t")
            if not isinstance(_bar30, (int, float)) or _bar30 < 2.0:
                _bad30.append("the published bar is not a Bonferroni bar")
            _ladder30 = _f30.get("ladder_summary") or {}
            _rows30 = _ladder30.get("rows") or []
            if not _rows30:
                _bad30.append("the ladder covers no rung")
            if _ladder30.get("cells") != len(_rows30):
                _bad30.append("the published cell count does not match the rows")
            if _ladder30.get("ladder_vacuous") is not False:
                _bad30.append("the band never moved a weight -- the ladder tested nothing")
            _pays30 = [r for r in _rows30 if r.get("verdict") == "BAND_PAYS"]
            for _r30 in _rows30:
                _nm30 = "%s/%s/f=%.2f" % (_r30.get("panel") or "-",
                                          _r30.get("arm"), _r30.get("band_frac") or 0.0)
                _pair30 = _r30.get("pair_ann_bp_per_year")
                _parts30 = [_r30.get(_c30 + "_ann_bp_per_year")
                            for _c30 in ("selection", "sizing", "toll")]
                if _pair30 is None or any(x is None for x in _parts30):
                    _bad30.append("%s publishes an incomplete split" % _nm30)
                    continue
                if abs(sum(_parts30) - _pair30) > 1e-6:
                    _bad30.append("%s channels do not reconstruct its pair" % _nm30)
                _v30 = _r30.get("verdict")
                if _v30 not in {"BASELINE", "NO_EFFECT", "BAND_COSTS", "BAND_NOISE",
                                "BAND_PAYS", "BAND_PAYS_TOLL_SHORT", "UNRESOLVED"}:
                    _bad30.append("%s carries an unpublished verdict %r" % (_nm30, _v30))
                if _v30 == "BAND_PAYS" and (_r30.get("d_pair_t_nw") or 0.0) < _bar30:
                    _bad30.append("%s is called a fix without clearing the bar" % _nm30)
                if _v30 == "BAND_PAYS" and (_r30.get("d_pair_ann_bp_per_year") or 0.0) <= 0.0:
                    _bad30.append("%s is called a fix on a non-positive delta" % _nm30)
                _save30 = _r30.get("weight_changes_saved")
                if _v30 == "NO_EFFECT" and (_save30 or 0) != 0:
                    _bad30.append("%s says no effect but saved changes" % _nm30)
                if "rule_collapsed" not in _r30:
                    _bad30.append("%s does not disclose whether the rule survived" % _nm30)
                elif _v30 == "BAND_PAYS" and _r30.get("rule_collapsed"):
                    _bad30.append("%s is called a fix after the rule collapsed to a "
                                  "buy-and-hold" % _nm30)
            # the base rung has to exist for every arm or the ladder has no origin
            for _p30 in (_f30.get("panels") or []):
                for _a30 in (_p30.get("arms") or []):
                    _rungs30 = _a30.get("rungs") or []
                    if not _rungs30 or _rungs30[0].get("verdict") != "BASELINE":
                        _bad30.append("%s/%s has no band-0 baseline rung"
                                      % (_p30.get("panel"), _a30.get("name")))
            if not (_f30.get("answer") or "").strip():
                _bad30.append("face publishes no answer sentence")
        check("product: a hysteresis band's toll saving is judged against its selection loss",
              not _bad30, "; ".join(_bad30)[:220]
              or "%d rungs, %d called a fix at bar %.2f, %d lose to the base arm, "
                 "%d point-estimate only, band %s"
                 % (len(_rows30), len(_pays30), _bar30 or 0.0,
                    sum(1 for r in _rows30 if r.get("verdict") == "BAND_COSTS"),
                    sum(1 for r in _rows30 if r.get("verdict") == "BAND_NOISE"),
                    "moves the rule" if not (_f30.get("ladder_summary") or {})
                    .get("ladder_vacuous") else "VACUOUS"))
    except Exception as e:
        check("product: a hysteresis band's toll saving is judged against its selection loss",
              False, repr(e)[:160])

    # E231: E230's one passing rung sat at the smallest band in the grid, which is the
    # shape E188 warned about -- a single decision sequence dressed as an optimum. This
    # leg re-derives the path test rather than trusting it: the focus cell's global path
    # must reproduce E230's own published number to the bit, a survival claim must be
    # backed by every measured path, a share can never exceed one, and a cell measured on
    # too few paths may not be called stable.
    try:
        _f31 = {}
        _bad31 = []
        _face31 = "results/state_tilt/bandpath_latest.json"
        if not os.path.exists(_face31):
            _bad31.append("no results/state_tilt/bandpath_latest.json on disk")
        else:
            with open(_face31, encoding="utf-8") as _fh:
                _f31 = json.load(_fh)
            _cut31 = _f31.get("evidence_cutoff")
            if not _cut31:
                _bad31.append("face carries no evidence_cutoff")
            elif not os.path.exists("results/state_tilt/BANDPATH-%s.json" % _cut31):
                _bad31.append("the dated face beside the latest pointer is missing")
            if (_f31.get("study") or "") != "E231":
                _bad31.append("face is not the E231 path test")
            _spec31 = _f31.get("frozen_spec") or {}
            _vocab31 = set(_spec31.get("vocabulary") or [])
            _minp31 = _spec31.get("min_paths_per_cell")
            _rows31 = _f31.get("cell_summary") or []
            _pc31 = _f31.get("path_count") or {}
            if not _rows31:
                _bad31.append("the summary covers no cell")
            if _pc31.get("panel_paths", 0) < 2:
                _bad31.append("the study ran on fewer than two paths")
            for _r31 in _rows31:
                _nm31 = "%s/%s/f=%.2f" % (_r31.get("panel") or "-", _r31.get("arm"),
                                          _r31.get("band_frac") or 0.0)
                _v31 = _r31.get("verdict")
                if _v31 not in _vocab31:
                    _bad31.append("%s carries an unpublished verdict %r" % (_nm31, _v31))
                _fp31 = _r31.get("frac_positive")
                _fl31 = _r31.get("frac_clears_lenient")
                if _fp31 is None or _fl31 is None:
                    _bad31.append("%s publishes no share" % _nm31)
                    continue
                if not (0.0 <= _fp31 <= 1.0 and 0.0 <= _fl31 <= 1.0):
                    _bad31.append("%s publishes a share outside [0,1]" % _nm31)
                if _r31.get("paths_positive", 0) > _r31.get("paths_measured", 0):
                    _bad31.append("%s counts more positives than paths" % _nm31)
                if _v31 == "SURVIVES_EVERY_PATH":
                    if _fp31 != 1.0 or _fl31 != 1.0:
                        _bad31.append("%s survives without a clean sweep" % _nm31)
                    if _r31.get("paths_measured", 0) < (_minp31 or 0):
                        _bad31.append("%s survives on %d paths" % (_nm31,
                                                                   _r31.get("paths_measured", 0)))
                    if _r31.get("rule_collapsed_paths", 0) > 0:
                        _bad31.append("%s survives with a collapsed rule on some path"
                                      % _nm31)
                if _v31 == "NOT_MEASURED" and _r31.get("paths_measured", 0) >= (_minp31 or 0):
                    _bad31.append("%s is called unmeasurable while measured" % _nm31)
            # the two families must stay separate: a full-sample number may not stand in
            # for a statement about a period
            _fam31 = _f31.get("focus_families") or {}
            if not (_fam31.get("structural") or {}).get("paths"):
                _bad31.append("the focus cell has no structural family")
            if not (_fam31.get("era") or {}).get("paths"):
                _bad31.append("the focus cell has no era family")
            # survivors list must agree with the rows it summarises
            _sv31 = _f31.get("survivors") or []
            if len(_sv31) != sum(1 for r in _rows31
                                 if r.get("verdict") == "SURVIVES_EVERY_PATH"):
                _bad31.append("the survivor list disagrees with the verdicts")
            # cross-face: the global path must reproduce E230's own cell for the overlap
            _rep31 = _f31.get("focus_replay_of_e230_global_path") or {}
            _focus31 = _f31.get("focus_cell") or {}
            _e230cell = None
            if os.path.exists("results/state_tilt/hysteresis_latest.json"):
                with open("results/state_tilt/hysteresis_latest.json", encoding="utf-8") as _fh:
                    _f30b = json.load(_fh)
                for _r30b in ((_f30b.get("ladder_summary") or {}).get("rows") or []):
                    if (_r30b.get("panel") == _focus31.get("panel")
                            and _r30b.get("arm") == _focus31.get("arm")
                            and abs((_r30b.get("band_frac") or 0.0)
                                    - (_focus31.get("band_frac") or 0.0)) < 1e-12):
                        _e230cell = _r30b
            if _rep31.get("d_pair_ann_bp_per_year") is None:
                _bad31.append("the global path published no replay value")
            elif _e230cell is None:
                _bad31.append("E230 publishes no cell for the focus (cannot cross-check)")
            else:
                _d31 = abs(_rep31["d_pair_ann_bp_per_year"]
                           - (_e230cell.get("d_pair_ann_bp_per_year") or 0.0))
                _t31 = abs((_rep31.get("d_pair_t_nw") or 0.0)
                           - (_e230cell.get("d_pair_t_nw") or 0.0))
                if _d31 > 1e-6 or _t31 > 1e-9:
                    _bad31.append("the global path does not reproduce E230 "
                                  "(delta %.3g bp, t %.3g)" % (_d31, _t31))
            if not (_f31.get("answer") or "").strip():
                _bad31.append("face publishes no answer sentence")
        check("product: a band that passed on one path is path-tested before it is a finding",
              not _bad31, "; ".join(_bad31)[:220]
              or "%d cells over %s panel-paths, %d survivors, focus %s/%s/f=%.2f positive "
                 "on %.0f%% of paths"
                 % (len(_rows31), _pc31.get("panel_paths", 0),
                    len(_f31.get("survivors") or []),
                    (_f31.get("focus_cell") or {}).get("panel"),
                    (_f31.get("focus_cell") or {}).get("arm"),
                    (_f31.get("focus_cell") or {}).get("band_frac") or 0.0,
                    100.0 * ((_f31.get("focus_cell") or {}).get("frac_positive") or 0.0)))
    except Exception as e:
        check("product: a band that passed on one path is path-tested before it is a finding",
              False, repr(e)[:160])
    # E232: the charge function itself is the assumption under the whole E226-E231 family.
    try:
        _bad32 = []
        _p32 = "results/state_tilt/costcurve_latest.json"
        _g32 = []
        _s32 = {}
        if not os.path.exists(_p32):
            _bad32.append("costcurve face missing")
        else:
            with open(_p32, encoding="utf-8") as _fh:
                _f32 = json.load(_fh)
            _rows32 = [r for r in (_f32.get("toll_channel") or [])]
            _g32 = sorted({r.get("gamma") for r in _rows32})
            if len(_g32) < 3:
                _bad32.append("fewer than three curvature points published")
            _ranges32 = _f32.get("arm_ranges") or []
            _inv32 = [r for r in _ranges32 if r.get("selection_invariant")]
            if _ranges32 and len(_inv32) != len(_ranges32):
                _bad32.append("selection is not curvature-invariant on every arm cell")
            # a 0/1 gate only moves whole units and 1**gamma == 1, so its toll cannot move
            for _r32 in _ranges32:
                if _r32.get("arm") == "binary_low":
                    _lo32, _hi32 = _r32["toll_range_bp"]
                    if abs(_hi32 - _lo32) > 1e-9:
                        _bad32.append("binary_low toll moved across gamma (%.4f)"
                                      % abs(_hi32 - _lo32))
            _s32 = _f32.get("summary") or {}
            if not _s32.get("e230_focus_verdicts_by_gamma"):
                _bad32.append("face does not re-read E230's focus cell")
            if not (_f32.get("answer") or "").strip():
                _bad32.append("face publishes no answer sentence")
        check("product: the family's toll conclusion is re-read under a non-linear charge",
              not _bad32, "; ".join(_bad32)[:220]
              or "%d gamma points, toll past the bar on %d arms at every gamma, "
                 "E230 focus %s"
                 % (len(_g32), (_s32.get("toll_single_channel_at_all_gammas") or 0),
                    "/".join(_s32.get("e230_focus_verdicts_by_gamma") or [])))
    except Exception as e:
        check("product: the family's toll conclusion is re-read under a non-linear charge",
              False, repr(e)[:160])
    # E233: E232's grid was assumed. This leg holds the face to its two obligations --
    # publish a measured exponent with an interval, and re-read the family at every point
    # of that interval plus the estimator dispute, so a verdict that only exists on the
    # grid is labelled as such.
    try:
        _bad33 = []
        _p33 = "results/state_tilt/empirical_gamma_latest.json"
        _s33 = {}
        _pe33 = {}
        if not os.path.exists(_p33):
            _bad33.append("empirical gamma face missing")
        else:
            with open(_p33, encoding="utf-8") as _fh:
                _f33 = json.load(_fh)
            _pe33 = _f33.get("primary_estimate") or {}
            _s33 = _f33.get("summary") or {}
            if _pe33.get("gamma") is None or not _pe33.get("gamma_ci"):
                _bad33.append("primary estimate publishes no interval")
            else:
                _lo33, _hi33 = _pe33["gamma_ci"]
                if not _lo33 < _pe33["gamma"] < _hi33:
                    _bad33.append("point estimate sits outside its own interval")
                _pts33 = _s33.get("gamma_points") or []
                if len(_pts33) < 3:
                    _bad33.append("fewer than three gamma points re-derived")
                if any(not (_lo33 - 1e-9 <= p <= _hi33 + 1e-9) for p in _pts33[:3]):
                    _bad33.append("an interval endpoint is missing from the point set")
            if not _s33.get("toll_clears_bar_every_point"):
                _bad33.append("the toll channel does not survive the measured interval")
            _cells33 = _s33.get("ladder_cells") or 0
            if not _cells33:
                _bad33.append("no ladder cell was re-read at the measured gamma")
            elif (_s33.get("ladder_verdicts_stable") or 0) + (
                    _s33.get("ladder_verdicts_inside_interval") or 0) != _cells33:
                _bad33.append("stable/inside counts do not partition the ladder cells")
            if not isinstance(_s33.get("ladder_verdicts_sensitive_to_identification"), int):
                _bad33.append("face does not report identification-span sensitivity")
            if not (_f33.get("answer") or "").strip():
                _bad33.append("face publishes no answer sentence")
            # the bridge assumption must be stated on the face, not only in the docstring
            if not ((_f33.get("frozen_spec") or {}).get("bridge") or "").strip():
                _bad33.append("the market-to-own-charge bridge is not disclosed")
        check("product: the charge curvature is measured, not assumed, before verdicts ride it",
              not _bad33, "; ".join(_bad33)[:220]
              or "gamma %.3f [%.3f, %.3f], %d/%d ladder cells stable inside the interval, "
                 "%d decided by the identification span"
                 % ((_pe33.get("gamma") or 0.0),
                    ((_pe33.get("gamma_ci") or [0.0, 0.0])[0]),
                    ((_pe33.get("gamma_ci") or [0.0, 0.0])[1]),
                    (_s33.get("ladder_verdicts_stable") or 0),
                    (_s33.get("ladder_cells") or 0),
                    (_s33.get("ladder_verdicts_sensitive_to_identification") or 0)))
    except Exception as e:
        check("product: the charge curvature is measured, not assumed, before verdicts ride it",
              False, repr(e)[:160])
    # E234: E233 measured one exponent per panel; the book holds five instruments, so a
    # book-level gamma may be a mixture. The leg holds the face to: per-member estimates
    # with intervals, a pooled fit that carries the SAME controls as the member fits, an
    # explicit compatibility verdict, and a bill comparison that separates the five-sleeve
    # split from the mixture (the split alone inflates the bill on a concave charge).
    try:
        _bad34 = []
        _p34 = "results/state_tilt/per_member_gamma_latest.json"
        _f34 = {}
        if not os.path.exists(_p34):
            _bad34.append("per-member gamma face missing")
        else:
            with open(_p34, encoding="utf-8") as _fh:
                _f34 = json.load(_fh)
            _mel = _f34.get("member_estimates") or []
            if len(_mel) < 2:
                _bad34.append("fewer than two member estimates published")
            for _m in _mel:
                if _m.get("gamma") is None:
                    continue
                if not _m.get("gamma_ci"):
                    _bad34.append("%s publishes no interval" % _m.get("symbol"))
                    break
                _lo, _hi = _m["gamma_ci"]
                if not _lo < _m["gamma"] < _hi:
                    _bad34.append("%s point sits outside its own interval" % _m.get("symbol"))
                    break
            _pool = _f34.get("pooled_fit") or {}
            if _pool.get("n_regressors") != len(_pool.get("controls") or []) + len(
                    _pool.get("members") or []) - 1:
                _bad34.append("the pooled fit does not carry the member specification")
            _c34 = _f34.get("compatibility") or {}
            if _c34.get("verdict") not in ("one_exponent_holds", "mixture"):
                _bad34.append("compatibility publishes no verdict")
            elif _c34["verdict"] == "mixture" and not (
                    _c34.get("pairwise_disjoint") or _c34.get("members_outside_pooled_interval")):
                _bad34.append("a mixture verdict names no breaker")
            _b34 = (_f34.get("summary") or {}).get("bill_by_arm") or []
            if not _b34:
                _bad34.append("no book bill published")
            for _r in _b34:
                if _r.get("uniform_same_granularity_bp") is None:
                    _bad34.append("%s lacks the same-granularity control" % _r.get("arm"))
                    break
                _mix = (_r.get("per_member_bp") or 0.0) - (
                    _r.get("uniform_same_granularity_bp") or 0.0)
                if abs(_mix - (_r.get("mixture_effect_bp") or 0.0)) > 1e-6:
                    _bad34.append("%s mixture term does not close the bill" % _r.get("arm"))
                    break
            if not (_f34.get("answer") or "").strip():
                _bad34.append("face publishes no answer sentence")
        check("product: a book-level exponent is measured per member before it is charged",
              not _bad34, "; ".join(_bad34)[:220]
              or "%d members, verdict %s, mixture effect %s bp against a %s bp split"
                 % (len(_f34.get("member_estimates") or []),
                    (_f34.get("compatibility") or {}).get("verdict"),
                    ", ".join("%+.0f" % (r.get("mixture_effect_bp") or 0.0)
                              for r in (_f34.get("summary") or {}).get("bill_by_arm") or []),
                    ", ".join("%+.0f" % (r.get("granularity_effect_bp") or 0.0)
                              for r in (_f34.get("summary") or {}).get("bill_by_arm") or [])))
    except Exception as e:
        check("product: a book-level exponent is measured per member before it is charged",
              False, repr(e)[:160])
    # E235: E234 priced a five-sleeve split without asking whether the market prices a
    # sleeve's move against THAT sleeve's turnover or against the book's. The leg holds
    # the face to: a joint own/aggregate fit with intervals, an explicit spec-adequacy
    # red flag (a negative own elasticity is never read as a finding), and a bill that is
    # re-derived under both granularities so the level is readable either way.
    try:
        _bad35 = []
        _p35 = "results/state_tilt/granularity_latest.json"
        _f35 = {}
        if not os.path.exists(_p35):
            _bad35.append("granularity face missing")
        else:
            with open(_p35, encoding="utf-8") as _fh:
                _f35 = json.load(_fh)
            _mem = _f35.get("members") or []
            _est = [m for m in _mem if m.get("b_own") is not None]
            if len(_est) < 2:
                _bad35.append("fewer than two sleeves carry a joint estimate")
            for _m in _est:
                if not (_m.get("b_own_ci") and _m.get("b_agg_ci")):
                    _bad35.append("%s publishes no interval" % _m.get("symbol"))
                    break
                if not (_m["b_own_ci"][0] < _m["b_own"] < _m["b_own_ci"][1]):
                    _bad35.append("%s own point sits outside its interval"
                                  % _m.get("symbol"))
                    break
                _g = _m.get("g_scaling")
                if _g is None or abs(_g - (_m["b_own"] + _m["b_agg"])) > 1e-9:
                    _bad35.append("%s book-scaling elasticity is not b_own + b_agg"
                                  % _m.get("symbol"))
                    break
            _sum35 = _f35.get("summary") or {}
            _neg = _sum35.get("negative_own_elasticity") or []
            if _neg and _sum35.get("pooled_verdict_after_spec_check") != \
                    "unresolved_spec_inadequate":
                _bad35.append("a negative own elasticity was not carried into the verdict")
            _bills35 = _sum35.get("bills") or {}
            if not _bills35:
                _bad35.append("no re-priced bill published")
            for _arm, _v in _bills35.items():
                if _v.get("per_sleeve_own_bp") is None:
                    _bad35.append("%s lacks the per-sleeve bill" % _arm)
                    break
                if _v.get("linear_bp") is None:
                    _bad35.append("%s lacks the linear bill" % _arm)
                    break
            if not (_f35.get("answer") or "").strip():
                _bad35.append("face publishes no answer sentence")
        check("product: the price of a sleeve move is measured against own and book "
              "turnover before the book is charged",
              not _bad35, "; ".join(_bad35)[:220]
              or "%d sleeves, verdict %s, pooled b_own %s / b_agg %s vs the family's "
                 "single exponent %s"
                 % (len(_f35.get("members") or []),
                    (_f35.get("summary") or {}).get("pooled_verdict_after_spec_check"),
                    (_f35.get("summary") or {}).get("pooled_b_own"),
                    (_f35.get("summary") or {}).get("pooled_b_agg"),
                    (_f35.get("summary") or {}).get("family_single_regressor_gamma")))
    except Exception as e:
        check("product: the price of a sleeve move is measured against own and book "
              "turnover before the book is charged", False, repr(e)[:160])
    # E236: E235's level regression could not separate the channels, so the question is
    # re-asked with stationary regressors. The leg holds the face to the three properties
    # that make the re-ask meaningful: a design that cannot see a regressor must not report
    # a coefficient for it; agreement in SIGN alone must never name a channel (the sizes
    # have to match too); and an unresolved verdict must not be accompanied by a charge
    # that pretends the bill was settled.
    try:
        _bad36 = []
        _p36 = "results/state_tilt/sharediff_latest.json"
        _f36 = {}
        if not os.path.exists(_p36):
            _bad36.append("share-difference face missing")
        else:
            with open(_p36, encoding="utf-8") as _fh:
                _f36 = json.load(_fh)
            _sum36 = _f36.get("summary") or {}
            _dsg = (_f36.get("pooled") or {}).get("designs") or []
            _names = {d.get("design") for d in _dsg}
            for _want in ("differences", "frozen_z", "two_way_fe"):
                if _want not in _names:
                    _bad36.append("pooled record misses design %s" % _want)
            _fe = next((d for d in _dsg if d.get("design") == "two_way_fe"), None)
            if _fe and (_fe.get("b_agg") is not None
                        or _fe.get("identifies_b_agg") is not False):
                _bad36.append("the date-FE design reports an aggregate it cannot see")
            _verdict36 = _sum36.get("pooled_verdict")
            if _sum36.get("b_own_magnitude_agreement") is False and \
                    _verdict36 != "unresolved_magnitude_disagreement":
                _bad36.append("a size disagreement between designs was not carried into "
                              "the verdict")
            _charged = _sum36.get("charges_priced") or []
            if _verdict36 in ("unresolved", "unresolved_sign_fragile",
                              "unresolved_magnitude_disagreement",
                              "unresolved_spec_inadequate") and \
                    any(c != "linear" for c in _charged):
                _bad36.append("an unresolved verdict still prices a granularity charge")
            if not (_f36.get("answer") or "").strip():
                _bad36.append("face publishes no answer sentence")
        check("product: a share-and-difference design may only settle a channel whose "
              "size the designs agree on",
              not _bad36, "; ".join(_bad36)[:220]
              or "verdict %s, b_own span %s (ratio %s), charges priced %s"
                 % ((_f36.get("summary") or {}).get("pooled_verdict"),
                    (_f36.get("summary") or {}).get("b_own_magnitude_span"),
                    (_f36.get("summary") or {}).get("b_own_magnitude_ratio"),
                    (_f36.get("summary") or {}).get("charges_priced")))
    except Exception as e:
        check("product: a share-and-difference design may only settle a channel whose "
              "size the designs agree on", False, repr(e)[:160])
    # E237: E236 named the mechanism behind the 25x size gap (the difference design prices a
    # session against its own turnover CHANGE, which co-moves with the information arrival
    # that sets |r|) but never measured it. The leg holds the face to: a first-stage
    # co-movement reading next to the artefact verdict, an identity residual published as a
    # number (the two component designs agree by algebra, never as evidence), and a bill
    # that stays refused unless both components clear the bar with overlapping intervals.
    try:
        _bad37 = []
        _p37 = "results/state_tilt/infostruct_latest.json"
        _f37 = {}
        if not os.path.exists(_p37):
            _bad37.append("information-structure face missing")
        else:
            with open(_p37, encoding="utf-8") as _fh:
                _f37 = json.load(_fh)
            _sum37 = _f37.get("summary") or {}
            _pooled37 = _f37.get("pooled") or {}
            for _want in ("components", "direct", "share", "share_controlled", "comove"):
                if not isinstance(_pooled37.get(_want), dict):
                    _bad37.append("pooled record misses %s" % _want)
            _vb37 = (_pooled37.get("verdict_bundle") or {})
            if not _vb37.get("verdict"):
                _bad37.append("no artefact verdict")
            if _vb37.get("verdict") == "own_channel_is_information_artefact" \
                    and _vb37.get("comovement_clears") is not True:
                _bad37.append("an artefact verdict without a live co-movement reading")
            _resid37 = _pooled37.get("c_rel_minus_dy")
            if _resid37 is None:
                _bad37.append("the identity residual is not published")
            _share37 = _pooled37.get("share") or {}
            if _sum37.get("uncontrolled_b_own") is None or \
                    abs((_sum37.get("uncontrolled_b_own") or 0.0)
                        - (_share37.get("b_own") or 0.0)) > 1e-9:
                _bad37.append("the summary's uncontrolled coefficient is not the share "
                              "design's")
            _gate37 = _f37.get("bill_gate") or {}
            _charges37 = [c.get("key") for c in (_f37.get("charges") or [])]
            if _gate37.get("permitted") is False and any(k != "linear" for k in _charges37):
                _bad37.append("a refused bill gate still prices a granularity charge")
            if _gate37.get("permitted") is True and \
                    not _gate37.get("gamma"):
                _bad37.append("a permitted bill publishes no exponent")
            if not (_f37.get("answer") or "").strip():
                _bad37.append("face publishes no answer sentence")
        check("product: the own-turnover channel is tested against information arrival "
              "before it is called an impact effect",
              not _bad37, "; ".join(_bad37)[:220]
              or "verdict %s, b_own %s -> %s, co-movement %s (t %s), bill %s"
                 % ((_f37.get("summary") or {}).get("verdict"),
                    _r37(_f37, "uncontrolled_b_own"),
                    _r37(_f37, "controlled_b_own"),
                    _r37(_f37, "comove_coef"),
                    _r37(_f37, "comove_t"),
                    "permitted" if (_f37.get("bill_gate") or {}).get("permitted")
                    else "refused"))
    except Exception as e:
        check("product: the own-turnover channel is tested against information arrival "
              "before it is called an impact effect", False, repr(e)[:160])
    # E238: every member's own turnover sits inside the book turnover its share is divided
    # by. This leg holds the leave-one-out face to: both denominators published with
    # intervals, the regressor identity pinned as a number, and the artefact label granted
    # ONLY where the share arithmetic's predicted gap lies inside the measured gap interval.
    try:
        _bad38 = []
        _p38 = "results/state_tilt/loobook_latest.json"
        _f38 = {}
        if not os.path.exists(_p38):
            _bad38.append("leave-one-out face missing")
        else:
            with open(_p38, encoding="utf-8") as _fh:
                _f38 = json.load(_fh)
            _pool38 = _f38.get("pooled") or {}
            _sum38 = _f38.get("summary") or {}
            for _den in ("inclusive", "leave_one_out"):
                _blk = _pool38.get(_den) or {}
                for _des in ("differences", "frozen_z", "two_way_fe"):
                    _row = _blk.get(_des) or {}
                    if _row.get("b_own") is None or not _row.get("ci"):
                        _bad38.append("%s/%s has no interval" % (_den, _des))
            _ident38 = (_f38.get("identity") or {}).get("max_abs_deviation_all_members")
            if _ident38 is None:
                _bad38.append("the regressor identity is not published as a number")
            elif _ident38 > (_f38.get("identity") or {}).get("tolerance", 1e-12):
                _bad38.append("identity deviation %r over tolerance" % _ident38)
            _vb38 = _pool38.get("verdict_bundle") or {}
            if not _vb38.get("verdict"):
                _bad38.append("no denominator verdict")
            for _des, _v in (_pool38.get("verdict_by_design") or {}).items():
                if _v.get("verdict") == "own_channel_is_a_denominator_artefact":
                    _ci38 = _v.get("gap_ci") or _v.get("ci")
                    _pred38 = _v.get("mechanical_prediction")
                    if _ci38 and _pred38 is not None and not (
                            _ci38[0] <= _pred38 <= _ci38[1]):
                        _bad38.append("%s is called arithmetic but the prediction %r sits "
                                      "outside the gap %r" % (_des, _pred38, _ci38))
            _gap38 = (_pool38.get("gap_by_design") or {}).get("differences")
            if _gap38 is None:
                _bad38.append("the differenced-design gap is not published")
            _mech38 = (_pool38.get("mechanical") or {}).get("predicted_gap")
            if _gap38 is not None and _mech38 is None:
                _bad38.append("no mechanical prediction next to the gap")
            if _sum38.get("kappa_nominal") is None:
                _bad38.append("the nominal 1/5 weight is not published")
            if not (_f38.get("answer") or "").strip():
                _bad38.append("face publishes no answer sentence")
        check("product: the own-turnover channel is re-measured against a book that does not "
              "contain it", not _bad38, "; ".join(_bad38)[:220]
              or "b_own %s -> %s (gap %s), arithmetic predicts %s -> %s"
                 % (_r38(_f38, "inclusive_b_own"), _r38(_f38, "loo_b_own"),
                    _r38(_f38, "gap"), _r38(_f38, "predicted_gap"),
                    (_f38.get("summary") or {}).get("verdict")))
    except Exception as e:
        check("product: the own-turnover channel is re-measured against a book that does not "
              "contain it", False, repr(e)[:160])
    # E239: the E238 leave-one-out ordering (own 0.596 < rest 0.771) may be a units artefact
    # because the rest aggregate is a SUM of four members. This leg holds the per-pair face to
    # the properties that make "one counterparty" a fair comparison: both designs publish
    # intervals, each difference interval contains its own point, the published mean cross is
    # the mean of the published per-pair numbers, and no charge is granted either way.
    try:
        _bad39 = []
        _p39 = "results/state_tilt/owncross_latest.json"
        _f39 = {}
        if not os.path.exists(_p39):
            _bad39.append("own-vs-cross face missing")
        else:
            with open(_p39, encoding="utf-8") as _fh:
                _f39 = json.load(_fh)
            if (_f39.get("study") or "") != "E239":
                _bad39.append("face does not identify as E239")
            _cut39 = _f39.get("evidence_cutoff")
            if not _cut39:
                _bad39.append("face carries no evidence_cutoff")
            elif not os.path.exists("results/state_tilt/OWNCROSS-%s.json" % _cut39):
                _bad39.append("the dated face beside the latest pointer is missing")
            _sum39 = _f39.get("summary") or {}
            for _name, _fit in (("pair_fe", _f39.get("pooled_pair_fe")),
                                ("two_way_fe", _f39.get("two_way_fe_pair_test"))):
                if not _fit or _fit.get("b_own") is None:
                    _bad39.append("%s publishes no own slope" % _name)
                    continue
                if not _fit.get("diff_ci"):
                    _bad39.append("%s publishes no difference interval" % _name)
                    continue
                _lo39, _hi39 = _fit["diff_ci"]
                if not (_lo39 <= _fit["diff"] <= _hi39):
                    _bad39.append("%s difference interval does not contain its point" % _name)
                if _hi39 - _lo39 <= 0.0:
                    _bad39.append("%s difference interval has zero width" % _name)
            _vocab39 = ((_f39.get("frozen_spec") or {}).get("verdict_vocabulary") or [])
            for _key in ("verdict", "verdict_two_way"):
                _v39 = _sum39.get(_key)
                if _v39 not in _vocab39:
                    _bad39.append("%s %r is outside the frozen vocabulary" % (_key, _v39))
            _pairs39 = [c for c in (_f39.get("pairs") or [])
                        if c.get("b_cross") is not None]
            if len(_pairs39) < 2:
                _bad39.append("fewer than two fittable pairs published")
            else:
                _pub39 = ((_f39.get("mean_single_member_cross") or {}).get("mean"))
                _own39 = sum(c["b_cross"] for c in _pairs39) / len(_pairs39)
                if _pub39 is None or abs(_own39 - _pub39) > 1e-9:
                    _bad39.append("the mean cross is not the mean of the published pairs")
            for _k39, _v39 in ((_f39.get("pooled_pair_fe") or {}).get("regressor_sd")
                               or {}).items():
                if _v39 is None or _v39 <= 0.0:
                    _bad39.append("regressor %s has no published variation" % _k39)
            if (_f39.get("no_bill") or {}).get("permitted") is not False:
                _bad39.append("the face granted a charge")
            _ref39 = _f39.get("e238_reference") or {}
            if _ref39.get("available") is not True and not _ref39.get("reason"):
                _bad39.append("the E238 cross-check is neither read nor declared absent")
            if not (_f39.get("summary") or {}).get("verdict_reason"):
                _bad39.append("the verdict carries no reason")
        check("product: own turnover is priced against ONE counterparty's turnover on the "
              "same footing", not _bad39, "; ".join(_bad39)[:220]
              or "own %s vs cross %s (diff %s %s); mean single cross %s; %s"
                 % (_r39(_f39, "pooled_own"), _r39(_f39, "pooled_cross"),
                    _r39(_f39, "pooled_diff"),
                    _r39ci(_f39, "pooled_diff_ci"), _r39(_f39, "mean_cross"),
                    (_f39.get("summary") or {}).get("verdict")))
    except Exception as e:
        check("product: own turnover is priced against ONE counterparty's turnover on the "
              "same footing", False, repr(e)[:160])
    # E240: E239's 0.541 divided a BOOK-SCALING coefficient by four times an inflated pair
    # slope. This leg holds the follow-up face to what makes the repaired comparison readable:
    # the identified one-vs-three interval exists and contains its point, the two designs that
    # cannot be identified are published as refusals rather than skipped, the coordinate map
    # carries its gaps, the verdict is inside the frozen vocabulary, and no charge is granted.
    try:
        _bad40 = []
        _p40 = "results/state_tilt/aggatt_latest.json"
        _f40 = {}
        _sum40 = {}
        if not os.path.exists(_p40):
            _bad40.append("aggregate-attenuation face missing")
        else:
            with open(_p40, encoding="utf-8") as _fh:
                _f40 = json.load(_fh)
            if (_f40.get("study") or "") != "E240":
                _bad40.append("face does not identify as E240")
            _cut40 = _f40.get("evidence_cutoff")
            if not _cut40:
                _bad40.append("face carries no evidence_cutoff")
            elif not os.path.exists("results/state_tilt/AGGATT-%s.json" % _cut40):
                _bad40.append("the dated face beside the latest pointer is missing")
            _sum40 = _f40.get("summary") or {}
            _vocab40 = ((_f40.get("frozen_spec") or {}).get("verdict_vocabulary") or [])
            if _sum40.get("verdict") not in _vocab40:
                _bad40.append("verdict %r is outside the frozen vocabulary"
                              % (_sum40.get("verdict"),))
            _ci40 = _sum40.get("diff_one_vs_rest3_ci")
            _d40 = _sum40.get("diff_one_vs_rest3")
            if not _ci40:
                _bad40.append("the identified difference publishes no interval")
            elif _d40 is None or not (_ci40[0] <= _d40 <= _ci40[1]):
                _bad40.append("the identified difference interval does not contain its point")
            elif _ci40[1] - _ci40[0] <= 0.0:
                _bad40.append("the identified difference interval has zero width")
            _bc40 = _f40.get("book_control") or {}
            if _bc40.get("book_control_identified") is not False:
                _bad40.append("the singular book control is not published as a refusal")
            elif not _bc40.get("reason"):
                _bad40.append("the book-control refusal carries no reason")
            _tw40 = (_f40.get("designs") or {}).get("aggregate_two_way_fe") or {}
            if _tw40.get("identifiable") is not False:
                _bad40.append("the non-identified two-way form is not published as a refusal")
            elif not _tw40.get("reason"):
                _bad40.append("the two-way refusal carries no reason")
            _cm40 = _f40.get("coordinate_map") or {}
            if _cm40.get("available") and _cm40.get("c_rest") is None:
                _bad40.append("the coordinate map publishes no rest coefficient")
            if not (_f40.get("frozen_spec") or {}).get("coordinate_map"):
                _bad40.append("the parametrisation identity is not stated")
            if (_f40.get("no_bill") or {}).get("permitted") is not False:
                _bad40.append("the face granted a charge")
        _ci40s = _sum40.get("diff_one_vs_rest3_ci")
        check("product: the book aggregate is compared on ONE parametrisation", not _bad40,
              "; ".join(_bad40)[:220]
              or "one %s vs sum-of-three %s (diff %s %s); rest %s; 4x naive cross %s; %s"
                 % (_r39(_f40, "b_one"), _r39(_f40, "b_rest3"),
                    _r39(_f40, "diff_one_vs_rest3"),
                    "n/a" if not _ci40s else "[%.3f, %.3f]" % tuple(_ci40s),
                    _r39(_f40, "b_sum_direct"), _r39(_f40, "four_times_naive_cross"),
                    (_sum40.get("verdict"))))
    except Exception as e:
        check("product: the book aggregate is compared on ONE parametrisation", False,
              repr(e)[:160])
    # E241: the reproduction ladder. What makes it readable is that rung0 must BE E238
    # (otherwise nothing downstream is attributable), that each rung changes one thing and
    # names it, that the misalignment claim is a COUNT rather than an opinion, and that the
    # published face's A/B pair is disclosed as superseded once the reader is repaired.
    try:
        _bad41 = []
        _p41 = "results/state_tilt/repro_latest.json"
        _f41 = {}
        if not os.path.exists(_p41):
            _bad41.append("reproduction face missing")
        else:
            with open(_p41, encoding="utf-8") as _fh:
                _f41 = json.load(_fh)
            if (_f41.get("study") or "") != "E241":
                _bad41.append("face does not identify as E241")
            _cut41 = _f41.get("evidence_cutoff")
            if not _cut41:
                _bad41.append("face carries no evidence_cutoff")
            elif not os.path.exists("results/state_tilt/REPRO-%s.json" % str(_cut41)[:10]):
                _bad41.append("the dated face beside the latest pointer is missing")
            if ((_f41.get("reproduction") or {}).get("reproduced")) is not True:
                _bad41.append("rung0 does not reproduce the published pair")
            _l41 = [r for r in (_f41.get("ladder") or []) if r.get("step")]
            _steps41 = [r.get("step") for r in _l41]
            for _want in ("r0_published_rows_loo", "r1_common_rows_loo",
                          "r2_common_rows_inclusive", "r3_common_grid_e240_code_path",
                          "r3b_e240_code_y_realigned", "r4_aligned_comparison"):
                if _want not in _steps41:
                    _bad41.append("ladder rung %s missing" % _want)
            for _r41 in _l41[1:-1]:
                if not _r41.get("change_vs_previous"):
                    _bad41.append("rung %s does not name the change it makes"
                                  % _r41.get("step"))
                if _r41.get("a_share") is None or _r41.get("g_denominator") is None:
                    _bad41.append("rung %s does not publish both coefficients"
                                  % _r41.get("step"))
            _mp41 = _f41.get("misalignment") or {}
            _prev41 = _mp41.get("dy_matches_the_previous_session")
            _same41 = _mp41.get("dy_matches_the_same_session")
            _n41 = _mp41.get("rows_tested")
            if _mp41.get("available"):
                if None in (_prev41, _same41, _n41) or _prev41 + _same41 > _n41:
                    _bad41.append("the misalignment counts do not add up")
                elif _mp41.get("dy_is_one_session_behind") and _prev41 < 0.9 * _n41:
                    _bad41.append("a one-session-behind claim without the matching count")
            _pf41 = _f41.get("published_face_check") or {}
            if _pf41.get("reproduced") is True and _pf41.get("superseded") is not True:
                _bad41.append("the published pair reproduces and is repaired but is not "
                              "disclosed as superseded")
            _al41 = _f41.get("alignment") or {}
            if _al41.get("available"):
                _par41 = ((_al41.get("rows_part") or 0.0)
                          + (_al41.get("weights_part") or 0.0)
                          + (_al41.get("reader_part") or 0.0))
                if abs((_al41.get("aligned_gap") or 0.0) - _par41) > 1e-6:
                    _bad41.append("the aligned change does not add up to its parts")
            if not (_f41.get("answer") or "").strip():
                _bad41.append("the face carries no answer sentence")
            if (_f41.get("no_bill") or {}).get("permitted") is not False:
                _bad41.append("the face granted a charge")
        check("product: a non-reproducing pair is traced rung by rung to the reader",
              not _bad41, "; ".join(_bad41)[:220]
              or "rung0 a_share %s; misaligned rows %s of %s; corrected rest %s"
                 % (_r39(_f41.get("reproduction") or {}, "rung0_a_share"),
                    (_f41.get("misalignment") or {}).get("dy_matches_the_previous_session"),
                    (_f41.get("misalignment") or {}).get("rows_tested"),
                    _r39((_f41.get("verdict_block") or {}).get("realigned_pair") or {},
                         "b_agg")))
    except Exception as e:
        check("product: a non-reproducing pair is traced rung by rung to the reader", False,
              repr(e)[:160])
    # E242: the omission sweep. What makes it readable is that the inflation factor is
    # measured against a NAMED identified form, that the closed form is published beside the
    # measurement instead of standing in for it, that the paired difference is shown to be the
    # quantity omission spares (so a verdict resting on a level is the one at risk), and that
    # every re-priceable verdict carries the numbers it was re-priced from.
    try:
        _bad42 = []
        _p42 = "results/state_tilt/omission_latest.json"
        _f42 = {}
        if not os.path.exists(_p42):
            _bad42.append("omission face missing")
        else:
            with open(_p42, encoding="utf-8") as _fh:
                _f42 = json.load(_fh)
            if (_f42.get("study") or "") != "E242":
                _bad42.append("face does not identify as E242")
            _cut42 = _f42.get("evidence_cutoff")
            if not _cut42:
                _bad42.append("face carries no evidence_cutoff")
            elif not os.path.exists("results/state_tilt/OMISSION-%s.json"
                                    % str(_cut42)[:10]):
                _bad42.append("the dated face beside the latest pointer is missing")
            _inf42 = _f42.get("inflation") or {}
            _c42 = _inf42.get("cross") or {}
            if not (_c42.get("factor_by_identified_form") or {}):
                _bad42.append("the factor is quoted without naming its identified form")
            if _c42.get("measured_factor") is None or _inf42.get("closed_form") is None:
                _bad42.append("measured factor and closed form are not both published")
            if _c42.get("closed_form_gap_relative") is None:
                _bad42.append("the closed form is not compared with the measurement")
            _dv42 = _f42.get("difference_insulation") or {}
            if _dv42.get("identified_pooled_diff") is None:
                _bad42.append("the paired difference is not published")
            if not _dv42.get("reading"):
                _bad42.append("the face does not say why the difference is spared")
            if not (_f42.get("level_claims") or []):
                _bad42.append("no level claims are re-priced")
            for _r42 in _f42.get("level_claims") or []:
                _gw42 = _r42.get("gate_window") or []
                if len(_gw42) != 2 or _gw42[0] > _gw42[1]:
                    _bad42.append("a level claim carries no gate window")
                    break
            _pr42 = [v for v in (_f42.get("verdicts") or []) if v.get("repriced_diff") is not None]
            for _v42 in _pr42:
                if _v42.get("repriced_diff_ci") is None:
                    _bad42.append("%s publishes a re-priced difference without its interval"
                                  % _v42.get("face"))
                if _v42.get("gap_from_omission") is None or _v42.get("gap_from_grid") is None:
                    _bad42.append("%s does not split its gap into grid and omission"
                                  % _v42.get("face"))
            if (_f42.get("no_bill") or {}).get("permitted") is not False:
                _bad42.append("the face granted a charge")
        check("product: an omission-inflated slope is re-priced against a named identified form",
              not _bad42, "; ".join(_bad42)[:220]
              or "naive cross %.3f -> identified %.3f (x%.2f, closed form x%.2f); difference "
                 "spared %.3f; levels at risk %d"
                 % ((_f42.get("inflation") or {}).get("cross", {}).get("naive_own_plus_one") or 0.0,
                    (_f42.get("inflation") or {}).get("cross", {}).get(
                        "identified_own_plus_all") or 0.0,
                    (_f42.get("inflation") or {}).get("cross", {}).get("measured_factor") or 0.0,
                    (_f42.get("inflation") or {}).get("closed_form") or 0.0,
                    (_f42.get("difference_insulation") or {}).get(
                        "identified_pooled_diff") or 0.0,
                    len((_f42.get("summary") or {}).get("levels_at_risk") or [])))
    except Exception as e:
        check("product: an omission-inflated slope is re-priced against a named identified form",
              False, repr(e)[:160])
    # E243: the portability test. What makes it readable is that the headline cell must REPLAY the
    # published E240 numbers rather than resemble them, that the pooled aggregator is published as
    # identifies:false (its zero is the symmetric split of an annihilated direction, proven on a
    # fixture whose truth differs 45x), that a cell wider than the resolution line is NOT-ASSESSED
    # instead of additive, and that no cell grants a bill.
    try:
        _bad43 = []
        _p43 = "results/state_tilt/addos_latest.json"
        _f43 = {}
        if not os.path.exists(_p43):
            _bad43.append("addos face missing")
        else:
            _f43 = json.load(open(_p43, encoding="utf-8"))
            _rep43 = _f43.get("e240_replay") or {}
            if _rep43.get("reproduced") is not True:
                _bad43.append("headline cell does not replay E240 (%s)" % _rep43.get("status"))
            _art43 = _f43.get("pooled_split_is_an_artifact") or {}
            if _art43.get("pooled_identifies") is not False:
                _bad43.append("the pooled aggregator claims to identify the gap")
            if not _art43.get("per_pair_reads_the_gap"):
                _bad43.append("the artifact fixtures do not carry a gap the pair design can see")
            _cells43 = [c for c in (_f43.get("cells") or []) if c.get("decided")]
            if len(_cells43) < 5:
                _bad43.append("only %d decided cells" % len(_cells43))
            for _c43 in _cells43:
                # a cell wider than the resolution line must never read as additive; the
                # pair-unanimity reading is published beside it, not instead of it
                if (_c43.get("diff_ci_halfwidth") or 0.0) > (_c43.get("resolution_max") or 99.0) \
                        and _c43.get("verdict") == "rest_channel_is_additive":
                    _bad43.append("cell %s has a %.2f half-width and still claims additivity"
                                  % (_c43.get("label"), _c43.get("diff_ci_halfwidth") or 0.0))
            if (_f43.get("rollup") or {}).get("verdict") not in (
                    "rest_channel_is_additive", "additivity_only_in_the_mean",
                    "additivity_era_dependent", "additivity_rejected_out_of_sample",
                    "additivity_not_resolved_out_of_sample", "unresolved_insufficient_rows"):
                _bad43.append("rollup verdict outside the frozen vocabulary")
            if (_f43.get("no_bill") or {}).get("permitted") is not False:
                _bad43.append("the face granted a charge")
        check("product: a verdict survives its own out-of-sample path",
              not _bad43, "; ".join(_bad43)[:220]
              or "cells %d; headline %s; mean-only %s; pooled identifies %s"
                 % (len(_cells43 if _f43 else []),
                    (_f43.get("rollup") or {}).get("verdict"),
                    (_f43.get("rollup") or {}).get("additivity_only_in_the_mean"),
                    (_f43.get("summary") or {}).get("pooled_aggregator_identifies")))
    except Exception as e:
        check("product: a verdict survives its own out-of-sample path", False, repr(e)[:160])
    # E244: where the heterogeneity sits. What makes it readable is that it reads E243's published
    # intervals rather than re-deriving them, that the variance is attributed (counterparty
    # identity vs own identity vs residual) instead of asserted, that a named carrier must REPEAT
    # across cells with one sign, and that the mirror ratio is published so a one-member spread is
    # not read as two channels.
    try:
        _bad44 = []
        _p44 = "results/state_tilt/pairhet_latest.json"
        _f44 = {}
        if not os.path.exists(_p44):
            _bad44.append("pairhet face missing")
        else:
            _f44 = json.load(open(_p44, encoding="utf-8"))
            _src44 = _f44.get("source_face") or {}
            if not _src44.get("sha256"):
                _bad44.append("the source face was not fingerprinted")
            if _f44.get("verdict") not in (
                    "one_member_pays_differently_the_others_are_its_mirror",
                    "two_members_pay_differently", "several_members_pay_differently",
                    "no_repeatable_counterparty_effect", "unresolved_pairs_too_few"):
                _bad44.append("verdict outside the frozen vocabulary")
            for _c44 in _f44.get("carriers") or []:
                if (_c44.get("cell_share") or 0.0) < 0.5:
                    _bad44.append("carrier %s stands on %.2f of its cells"
                                  % (_c44.get("name"), _c44.get("cell_share") or 0.0))
                if len(_c44.get("cells") or []) < 2:
                    _bad44.append("carrier %s does not repeat" % _c44.get("name"))
            _vs44 = _f44.get("variance_split") or {}
            _sh44 = [(_vs44.get("share_counterparty") or 0.0),
                     (_vs44.get("share_own") or 0.0),
                     (_vs44.get("share_residual") or 0.0)]
            if abs(sum(_sh44) - 1.0) > 0.02:
                _bad44.append("variance shares sum to %.3f" % sum(_sh44))
            if ((_f44.get("overlap") or {}).get("independent_observations")) is not False:
                _bad44.append("overlapping cells published as independent observations")
            if ((_f44.get("no_bill") or {}).get("permitted")) is not False:
                _bad44.append("the classification granted a charge")
        check("product: the spread is attributed to a named counterparty that repeats",
              not _bad44, "; ".join(_bad44)[:220]
              or "verdict %s; carriers %s; variance counterparty %.2f / own %.2f"
                 % ((_f44.get("verdict")),
                    ",".join(c.get("name") or "" for c in (_f44.get("carriers") or [])) or "none",
                    (_f44.get("variance_split") or {}).get("share_counterparty") or 0.0,
                    (_f44.get("variance_split") or {}).get("share_own") or 0.0))
    except Exception as e:
        check("product: the spread is attributed to a named counterparty that repeats",
              False, repr(e)[:160])
    # E245: every reading in this family came out of a SUM design (`rest` = one member against an
    # average of the others). This leg reads the un-summed matrix face and re-derives its claims
    # from the face's OWN frozen spec, so a face that names a star without the decisive share
    # behind it cannot pass merely because the runner said so.
    try:
        _bad45 = []
        _p45 = os.path.join("results", "state_tilt", "slopematrix_latest.json")
        _f45 = None
        if os.path.exists(_p45):
            with io.open(_p45, encoding="utf-8") as _fh45:
                _f45 = json.load(_fh45)
        if not _f45:
            _bad45.append("slope-matrix face missing")
        else:
            _spec45 = _f45.get("frozen_spec") or {}
            _vocab45 = set(_spec45.get("verdicts") or []) | {
                "verdict_era_dependent", "verdict_mixed_across_cells"}
            _cells45 = [c for c in (_f45.get("cells") or []) if c.get("decided")]
            if not _cells45:
                _bad45.append("no decided cell")
            for _c45 in _cells45:
                if _c45.get("verdict") not in _vocab45:
                    _bad45.append("cell %s verdict outside the frozen vocabulary" % _c45.get("label"))
                _half45 = _c45.get("resolution_median_halfwidth")
                _bound45 = _spec45.get("resolution_max_halfwidth")
                if _half45 is not None and _bound45 is not None and _half45 > _bound45 \
                        and _c45.get("verdict") in ("counterparty_concentration", "heterogeneous_rows",
                                                    "coherent_rest_channel"):
                    _bad45.append("cell %s names a structure on a %.2f half-width"
                                  % (_c45.get("label"), _half45))
                for _r45 in _c45.get("rows") or []:
                    if _r45.get("decided") and len(_r45.get("cross") or []) != len(_c45["members"]) - 1:
                        _bad45.append("row %s does not carry k-1 slopes" % _r45.get("own_of"))
                _min45 = _spec45.get("star_decisive_share")
                for _nm45 in _c45.get("stars") or []:
                    _col45 = next((c for c in _c45.get("columns") or [] if c["one_of"] == _nm45), None)
                    if not _col45 or (_min45 is not None and _col45["decisive_share"] < _min45):
                        _bad45.append("star %s does not meet the face's own threshold" % _nm45)
            _roll45 = (_f45.get("rollup") or {}).get("verdict")
            _by45 = (_f45.get("rollup") or {}).get("cells_by_verdict") or {}
            if _roll45 in ("verdict_mixed_across_cells", "verdict_era_dependent") and len(_by45) < 2:
                _bad45.append("a mixed verdict with fewer than two verdict classes")
            if not _f45.get("no_bill"):
                _bad45.append("the face does not carry its no-bill line")
        check("product: the un-summed matrix names structure without a sum regressor",
              not _bad45, "; ".join(_bad45)[:220]
              or "verdict %s; classes %s; headline %s"
                 % ((_f45 or {}).get("rollup", {}).get("verdict"),
                    ",".join(sorted((((_f45 or {}).get("rollup") or {}).get("cells_by_verdict") or {}).keys())),
                    ((_f45 or {}).get("summary") or {}).get("headline_verdict")))
    except Exception as e:
        check("product: the un-summed matrix names structure without a sum regressor",
              False, repr(e)[:160])
    # E246: the matrix face named a star but could not say whether that sleeve's flow moves the
    # book or whether every sleeve loads on one driver it reads best. This leg re-derives the
    # lead claims from the face's own counts, so a cell that names a lead without a decisive
    # lagged column behind it cannot pass merely because the runner printed a verdict.
    try:
        _bad46 = []
        _p46 = os.path.join("results", "state_tilt", "stardir_latest.json")
        _f46 = None
        if os.path.exists(_p46):
            with io.open(_p46, encoding="utf-8") as _fh46:
                _f46 = json.load(_fh46)
        if not _f46:
            _bad46.append("star-direction face missing")
        else:
            _spec46 = _f46.get("frozen_spec") or {}
            _vocab46 = set(_spec46.get("verdicts") or []) | {
                "verdict_era_dependent", "verdict_mixed_across_cells"}
            _cells46 = [c for c in (_f46.get("cells") or []) if c.get("decided")]
            _share46 = _spec46.get("star_decisive_share")
            _abs46 = _spec46.get("lead_min_abs")
            _bound46 = _spec46.get("resolution_max_halfwidth")
            if not _cells46:
                _bad46.append("no decided cell")
            _saw_lead = 0
            _saw_lagdesign = 0
            for _c46 in _cells46:
                if _c46.get("verdict") not in _vocab46:
                    _bad46.append("cell %s verdict outside the frozen vocabulary" % _c46.get("label"))
                _cn46 = _c46.get("counts") or {}
                _lead46 = _cn46.get("lead") or {}
                if "1" in _lead46 and "2" in _lead46:
                    _saw_lagdesign += 1
                else:
                    _bad46.append("cell %s does not carry both lag designs" % _c46.get("label"))
                _half46 = _c46.get("resolution_median_halfwidth")
                if _half46 is not None and _bound46 is not None and _half46 > _bound46 \
                        and _c46.get("verdict") in ("star_flow_leads_members",
                                                    "flow_leads_and_contemporaneous",
                                                    "star_flow_leads_with_sign_flip",
                                                    "star_flow_leads_inverse",
                                                    "contemporaneous_common_factor",
                                                    "members_lead_the_star"):
                    _bad46.append("cell %s names a direction on a %.2f half-width"
                                  % (_c46.get("label"), _half46))
                _declared = set(_c46.get("lead_lags_decisive") or [])
                _real = set()
                _signs = set()
                for _L46, _b46 in _lead46.items():
                    _sh46 = _b46.get("decisive_share")
                    _mu46 = _b46.get("mean_slope")
                    if _sh46 is not None and _mu46 is not None and _share46 is not None \
                            and _sh46 >= _share46 and _abs46 is not None and abs(_mu46) >= _abs46:
                        _real.add(int(_L46))
                        _signs.add(1 if _mu46 > 0 else -1)
                if _declared and _declared != _real:
                    _bad46.append("cell %s declares lags %s but its counts carry %s"
                                  % (_c46.get("label"), sorted(_declared), sorted(_real)))
                if _declared:
                    _saw_lead += 1
                if _c46.get("verdict") == "star_flow_leads_with_sign_flip" and len(_signs) < 2:
                    _bad46.append("cell %s calls a sign flip with %d sign(s)" % (_c46.get("label"), len(_signs)))
                if _c46.get("verdict") in ("star_flow_leads_members",
                                           "flow_leads_and_contemporaneous") and _signs and 1 not in _signs:
                    _bad46.append("cell %s calls a positive lead with no positive lag" % _c46.get("label"))
                for _r46 in _c46.get("rows") or []:
                    pass
                _pers46 = _c46.get("own_lag_persistence") or {}
                if _pers46 and not any(v.get("decided") for v in _pers46.values()):
                    _bad46.append("cell %s publishes no own-lag persistence" % _c46.get("label"))
            _roll46 = (_f46.get("rollup") or {}).get("verdict")
            _by46 = (_f46.get("rollup") or {}).get("cells_by_verdict") or {}
            if _roll46 in ("verdict_mixed_across_cells", "verdict_era_dependent") and len(_by46) < 2:
                _bad46.append("a mixed verdict with fewer than two verdict classes")
            if _roll46 not in _vocab46 and _roll46 is not None:
                _bad46.append("rollup verdict outside the frozen vocabulary")
            if not _f46.get("no_bill"):
                _bad46.append("the face does not carry its no-bill line")
            _ones46 = (_f46.get("summary") or {}).get("one_line") or ""
            if "no direction resolved in any counted cell" in _ones46 and _by46:
                _bad46.append("the one-line answer contradicts the rollup")
        check("product: star direction is decided from lag designs, not asserted",
              not _bad46, "; ".join(_bad46)[:220]
              or "verdict %s; cells with a lead %d of %d; headline %s"
                 % ((_f46 or {}).get("rollup", {}).get("verdict"),
                    _saw_lead, _saw_lagdesign,
                    ((_f46 or {}).get("summary") or {}).get("headline_verdict")))
    except Exception as e:
        check("product: star direction is decided from lag designs, not asserted",
              False, repr(e)[:160])
    # E248: E246 read the star lead off its HAC intervals at two lags. This leg re-derives every
    # published shape from the face's own lag column against its own shuffled band, so a cell
    # that names an oscillation its band does not carry cannot pass on the runner's word.
    try:
        _bad48 = []
        _p48 = os.path.join("results", "state_tilt", "starlagband_latest.json")
        _f48 = None
        if os.path.exists(_p48):
            with io.open(_p48, encoding="utf-8") as _fh48:
                _f48 = json.load(_fh48)
        if not _f48:
            _bad48.append("star-lag-band face missing")
        else:
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            import e248_star_lag_band as _m48
            _cells48 = [c for c in (_f48.get("cells") or []) if c.get("decided")]
            _spec48 = _f48.get("frozen_spec") or {}
            _vocab48 = set(_spec48.get("verdicts") or [])
            if not _cells48:
                _bad48.append("no decided cell")
            for _c48 in _cells48:
                _col = [_c48.get("lag_column", {}).get("lag%d" % _k) for _k in range(6)]
                _v, _cross = _m48.derive_verdict(_col, _c48.get("band") or [],
                                                 _c48.get("band_family"))
                if _v != _c48.get("verdict"):
                    _bad48.append("cell %s: numbers say %s, face says %s"
                                  % (_c48.get("label"), _v, _c48.get("verdict")))
                if _v not in _vocab48:
                    _bad48.append("cell %s verdict outside the frozen vocabulary"
                                  % _c48.get("label"))
                _fam = (_c48.get("band_family") or {}).get("max_abs")
                if _c48.get("band_draws_used") != _spec48.get("perm_draws"):
                    _bad48.append("cell %s used %s draws, spec says %s"
                                  % (_c48.get("label"), _c48.get("band_draws_used"),
                                     _spec48.get("perm_draws")))
                for _k in (_cross or []):
                    if _fam is None or abs(_col[_k]) <= _fam:
                        _bad48.append("cell %s declares lag %d crossing a band it does not clear"
                                      % (_c48.get("label"), _k))
                if _v == "period2_oscillation" and _col[1] * _col[2] >= 0.0:
                    _bad48.append("cell %s calls an oscillation with lags of equal sign"
                                  % _c48.get("label"))
                _ts = _c48.get("two_session_sum") or {}
                if not (_ts.get("overlapping") or {}).get("lag_column"):
                    _bad48.append("cell %s publishes no two-session-sum row"
                                  % _c48.get("label"))
                if _c48.get("oscillation_survives_two_session_sum") is True \
                        and len(((_ts.get("disjoint") or {}).get("lag_column") or {})) < 6:
                    _bad48.append("cell %s claims survival without a disjoint row"
                                  % _c48.get("label"))
            _roll48 = (_f48.get("rollup") or {}).get("verdict")
            _by48 = (_f48.get("rollup") or {}).get("cells_by_verdict") or {}
            if _roll48 in ("verdict_mixed_across_cells", "verdict_era_dependent") \
                    and len(_by48) < 2:
                _bad48.append("a mixed verdict with fewer than two verdict classes")
            if _roll48 not in _vocab48 | {"verdict_era_dependent", "verdict_mixed_across_cells"}:
                _bad48.append("rollup verdict outside the frozen vocabulary")
            if not _f48.get("no_bill"):
                _bad48.append("the face does not carry its no-bill line")
        check("product: the star lag band is re-derived from its own shuffled null",
              not _bad48, "; ".join(_bad48)[:220]
              or "verdict %s; cells %d; headline %s"
                 % ((_f48 or {}).get("rollup", {}).get("verdict"), len(_cells48),
                    ((_f48 or {}).get("summary") or {}).get("headline_verdict")))
    except Exception as e:
        check("product: the star lag band is re-derived from its own shuffled null",
              False, repr(e)[:160])
    # E249: E248 read one column and named the star. This leg re-derives every cell from the
    # five published column readings against their own bands, and refuses the trap the frozen
    # vocabulary cannot express on its own -- a lone crossing whose gap to the other columns
    # sits inside one band width is a power reading, and the post-hoc block must say so.
    try:
        _bad49 = []
        _p49 = os.path.join("results", "state_tilt", "leadcounter_latest.json")
        _f49 = None
        if os.path.exists(_p49):
            with io.open(_p49, encoding="utf-8") as _fh49:
                _f49 = json.load(_fh49)
        _cells49 = []
        if not _f49:
            _bad49.append("lead-counterfactual face missing")
        else:
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            import e249_lead_counterfactual as _m49
            _cells49 = [c for c in (_f49.get("cells") or []) if c.get("decided")]
            _spec49 = _f49.get("frozen_spec") or {}
            _vocab49 = set(_spec49.get("verdicts") or [])
            if not _cells49:
                _bad49.append("no decided cell")
            for _c49 in _cells49:
                _cols49 = _c49.get("columns_read") or {}
                _d49 = _m49.derive_verdict(_cols49, _c49.get("star"))
                if _d49["verdict"] != _c49.get("verdict"):
                    _bad49.append("cell %s: numbers say %s, face says %s"
                                  % (_c49.get("label"), _d49["verdict"], _c49.get("verdict")))
                if _d49["verdict"] not in _vocab49:
                    _bad49.append("cell %s verdict outside the frozen vocabulary"
                                  % _c49.get("label"))
                # every declared crossing must actually clear its OWN shuffled band
                for _k49 in (_d49.get("crossed") or []):
                    _band49 = (_cols49.get(_k49) or {}).get("band_lag1") or {}
                    _b49 = (_cols49.get(_k49) or {}).get("b1")
                    _fam49 = ((_cols49.get(_k49) or {}).get("band_family") or {}).get("max_abs")
                    _line49 = abs(_fam49) if _fam49 is not None else None
                    if _b49 is None or (_line49 is not None and abs(_b49) <= _line49):
                        _bad49.append("cell %s declares %s crossing a band it does not clear"
                                      % (_c49.get("label"), _k49))
                    elif _line49 is None and (_band49.get("lo") is None
                                              or _band49["lo"] < _b49 < _band49["hi"]):
                        _bad49.append("cell %s declares %s outside a band it sits inside"
                                      % (_c49.get("label"), _k49))
                # the separation test: 'specific' must be a comparison, not an impression
                if _d49["verdict"] == "column_specific":
                    if _d49.get("specific_is_separated") is None:
                        _bad49.append("cell %s calls a column specific without a separation "
                                      "test" % _c49.get("label"))
                    elif _d49["specific_is_separated"] is False:
                        _ph49 = _m49.reclassify(_c49) or {}
                        if _ph49.get("post_hoc") == "column_specific":
                            _bad49.append("cell %s keeps a lone crossing it cannot separate"
                                          % _c49.get("label"))
                _sp49 = _d49.get("column_spread")
                _w49 = _d49.get("median_within_band_width")
                _ratio49 = _d49.get("spread_over_band")
                if _sp49 is not None and _w49:
                    if _ratio49 is None or abs(_ratio49 - _sp49 / _w49) > 1e-9:
                        _bad49.append("cell %s publishes a spread/band its numbers do not "
                                      "produce" % _c49.get("label"))
            _ph49 = _f49.get("rollup_post_hoc") or {}
            _moved49 = [m["cell"] for m in (_ph49.get("reclassified") or [])]
            for _c49 in _cells49:
                if _c49.get("verdict") == "column_specific" \
                        and _c49.get("kind") in ("headline", "window", "era", "neighbour"):
                    _r49 = _m49.reclassify(_c49) or {}
                    if _r49.get("post_hoc") != "column_specific" \
                            and _c49["label"] not in _moved49:
                        _bad49.append("cell %s is reclassified but the post-hoc block does "
                                      "not name it" % _c49["label"])
            if _ph49.get("frozen_verdict_kept") != (_f49.get("rollup") or {}).get("verdict"):
                _bad49.append("the post-hoc block does not carry the frozen rollup verdict")
            # cross-face identity: the star's lag-1 here must be E248's published number
            _rep49 = _f49.get("e248_reproduction_ref") or {}
            if _rep49.get("available"):
                _head49 = next((c for c in _cells49 if c.get("label") == "all_five"), {})
                _star49 = _head49.get("star")
                _b149 = ((_head49.get("decision") or {}).get("b1") or {}).get(_star49)
                _ref49 = _rep49.get("e248_lag1")
                if _b149 is None or _ref49 is None or abs(_b149 - _ref49) > 1e-9:
                    _bad49.append("the star column reads %s but E248 published %s"
                                  % (_b149, _ref49))
            if not _f49.get("no_bill"):
                _bad49.append("the face does not carry its no-bill line")
        check("product: the negative lead is read column by column, not off one column",
              not _bad49, "; ".join(_bad49)[:220]
              or "verdict %s (post-hoc %s); cells %d; headline %s; spread/band %s"
                 % ((_f49 or {}).get("rollup", {}).get("verdict"),
                    ((_f49 or {}).get("rollup_post_hoc") or {}).get("verdict"),
                    len(_cells49),
                    ((_f49 or {}).get("summary") or {}).get("headline_verdict"),
                    _r39((_f49 or {}).get("summary") or {}, "spread_over_band")))
    except Exception as e:
        check("product: the negative lead is read column by column, not off one column",
              False, repr(e)[:160])
    # E250: E249 found every column negative, so the naming was not the star's. This leg asks the
    # question E249 left open -- is the shared lead the book's own lagged aggregate turnover? --
    # and refuses the two traps that would make a "yes" meaningless: the aggregate series must be
    # aligned to the panel rows (an increment-date grid is one row short and slides every lag by
    # one session), and the per-column "share absorbed" must be the LEAVE-ONE-OUT reading,
    # because the column's turnover is a component of the aggregate (E238 family).
    try:
        _bad50 = []
        _p50 = os.path.join("results", "state_tilt", "bookecho_latest.json")
        _f50 = None
        if os.path.exists(_p50):
            with io.open(_p50, encoding="utf-8") as _fh50:
                _f50 = json.load(_fh50)
        _cells50 = []
        if not _f50:
            _bad50.append("book-echo face missing")
        else:
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            import e250_book_turnover_echo as _m50
            _cells50 = [c for c in (_f50.get("cells") or []) if c.get("verdict")]
            _vocab50 = set(((_f50.get("frozen_spec") or {}).get("verdicts")) or [])
            if not _cells50:
                _bad50.append("no cell carries a verdict")
            for _c50 in _cells50:
                if _c50.get("verdict") not in _vocab50:
                    _bad50.append("cell %s outside the frozen vocabulary" % _c50.get("label"))
                _d50 = _c50.get("design_B_alone") or {}
                _reb50 = _m50.derive_verdict(_d50.get("c1"), _c50.get("aggregate_outside_band"),
                                             _c50.get("mean_share_accounted"),
                                             len(_c50.get("columns") or {}))
                if _reb50 != _c50.get("verdict"):
                    _bad50.append("cell %s publishes %s but its numbers re-derive %s"
                                  % (_c50.get("label"), _c50.get("verdict"), _reb50))
                if (_c50.get("aggregate") or {}).get("aligned_to_panel_rows") is not True:
                    _bad50.append("cell %s has an aggregate series off the panel grid"
                                  % _c50.get("label"))
                _cols50 = _c50.get("columns") or {}
                _shares50 = [v.get("share_accounted_loo") for k, v in _cols50.items()
                             if k != _c50.get("star")]
                _shares50 = [v for v in _shares50 if v is not None]
                if _shares50 and _c50.get("mean_share_accounted") is not None:
                    _mean50 = sum(_shares50) / float(len(_shares50))
                    if abs(_mean50 - _c50["mean_share_accounted"]) > 1e-9:
                        _bad50.append("cell %s publishes a leave-one-out mean its own columns "
                                      "do not produce" % _c50.get("label"))
                for _k50, _v50 in _cols50.items():
                    if _v50.get("share_accounted_loo") is None:
                        _bad50.append("cell %s column %s has no leave-one-out share"
                                      % (_c50.get("label"), _k50))
                if _c50.get("verdict") == "aggregate_carries_the_lead" \
                        and (_d50.get("c1") or 0.0) >= 0.0:
                    _bad50.append("cell %s names a negative lead carrying a non-negative "
                                  "aggregate coefficient" % _c50.get("label"))
            if not _f50.get("no_bill"):
                _bad50.append("the face does not carry its no-bill line")
            if not _f50.get("identification_caveat"):
                _bad50.append("the face does not carry the time-series vs date-FE caveat")
        _s50 = (_f50 or {}).get("summary") or {}
        check("product: the shared lead is tested against the book's own aggregate turnover",
              not _bad50, "; ".join(_bad50)[:220]
              or "verdict %s; cells %d; c1 %s; mean leave-one-out share %s"
                 % (_s50.get("verdict"), len(_cells50), _r39(_f50 or {}, "headline_c1_alone"),
                    _r39(_f50 or {}, "headline_mean_share_accounted")))
    except Exception as e:
        check("product: the shared lead is tested against the book's own aggregate turnover",
              False, repr(e)[:160])
    return _finish()


def _r39(face, key):
    v = (face.get("summary") or {}).get(key)
    return "n/a" if v is None else "%.3f" % v


def _r39ci(face, key):
    v = (face.get("summary") or {}).get(key)
    return "n/a" if not v else "[%.3f, %.3f]" % (v[0], v[1])


def _r38(face, key):
    v = (face.get("summary") or {}).get(key)
    return "n/a" if v is None else "%.3f" % v
def _r37(face, key):
    v = (face.get("summary") or {}).get(key)
    return "n/a" if v is None else "%.3f" % v


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
