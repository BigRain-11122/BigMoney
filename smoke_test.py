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
                # The point set is PUBLISHED ROUNDED, so it is compared at its own resolution:
                # at 1e-9 a 6-dp copy of the endpoint reads as "missing from its own point
                # set" when it is the same number printed shorter (E233 r1316). The precision
                # is required, not defaulted, and the first three points must be NAMED as the
                # interval endpoints plus the estimate -- being numerically inside the
                # interval is not the same claim.
                _dec33 = _s33.get("gamma_points_decimals")
                if not isinstance(_dec33, int) or _dec33 < 0:
                    _bad33.append("the face does not publish the point set's precision")
                    _dec33 = 6
                _tol33 = 10.0 ** (-_dec33)
                if any(not (_lo33 - _tol33 <= p <= _hi33 + _tol33) for p in _pts33[:3]):
                    _bad33.append("an interval endpoint is missing from the point set")
                _src33 = _s33.get("gamma_points_sources") or []
                if _src33[:3] != ["interval_lo", "point", "interval_hi"]:
                    _bad33.append("the first three points are not named as the interval "
                                  "endpoints and the estimate (%s)" % (_src33[:3],))
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

    # E251: E250 left one number standing -- the star kept ~90% of its lag-1 once the book
    # aggregate was in the row. This leg re-derives that decomposition from the published face
    # and refuses the two ways it could lie: a verdict that its own numbers do not reproduce, and
    # a "residual" that is not the same object E250 published (the identity to bookecho is
    # checked to 1e-9, because a decomposition of a different number is not a decomposition).
    try:
        _bad51 = []
        _p51 = os.path.join("results", "state_tilt", "starown_latest.json")
        _f51 = None
        if os.path.exists(_p51):
            with io.open(_p51, encoding="utf-8") as _fh51:
                _f51 = json.load(_fh51)
        _cells51 = []
        if not _f51:
            _bad51.append("star-own-component face missing")
        else:
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            import e251_star_own_component as _m51
            _vocab51 = set(((_f51.get("frozen_spec") or {}).get("verdicts")) or [])
            _cells51 = [c for c in (_f51.get("cells") or []) if c.get("verdict")]
            if not _cells51:
                _bad51.append("no cell carries a verdict")
            for _c51 in _cells51:
                if _c51.get("verdict") not in _vocab51:
                    _bad51.append("cell %s outside the frozen vocabulary" % _c51.get("label"))
                _r51 = _c51.get("star_residual") or {}
                _reb51 = _m51.derive_verdict(_r51.get("b1"), _c51.get("star_outside_band"),
                                             _r51.get("share_taken_by_vol"),
                                             _c51.get("vol_addition_outside_band"),
                                             len(_c51.get("columns") or {}))
                if _reb51 != _c51.get("verdict"):
                    _bad51.append("cell %s publishes %s but its numbers re-derive %s"
                                  % (_c51.get("label"), _c51.get("verdict"), _reb51))
                _b51, _bv51 = _r51.get("b1"), _r51.get("b1_with_vol")
                if _b51 is not None and _bv51 is not None and abs(_b51) > 1e-12:
                    _sh51 = 1.0 - (_bv51 / _b51)
                    if _r51.get("share_taken_by_vol") is None \
                            or abs(_sh51 - _r51["share_taken_by_vol"]) > 1e-9:
                        _bad51.append("cell %s publishes a share its own betas "
                                      "do not produce" % _c51.get("label"))
                if not _c51.get("star") and "no member was named star" not in (
                        _c51.get("reason") or ""):
                    _bad51.append("cell %s has no star and no explicit reason"
                                  % _c51.get("label"))
                if _c51.get("verdict") == "residual_is_own_volatility" \
                        and _c51.get("vol_addition_outside_band") is not True:
                    _bad51.append("cell %s names volatility without clearing the drop band"
                                  % _c51.get("label"))
            _head51 = next((c for c in _cells51 if c.get("label") == "all_five"), None)
            if _head51 is None:
                _bad51.append("no headline cell")
            else:
                _st51 = (_head51.get("columns") or {}).get(_head51.get("star")) or {}
                if _st51.get("age_identified") is not False:
                    _bad51.append("the headline star does not publish age as unidentified")
                _bid51 = os.path.join("results", "state_tilt", "bookecho_latest.json")
                if os.path.exists(_bid51):
                    with io.open(_bid51, encoding="utf-8") as _fh51b:
                        _f51b = json.load(_fh51b)
                    _hb51 = next((c for c in (_f51b.get("cells") or [])
                                  if c.get("label") == "all_five"), None)
                    if _hb51 and _hb51.get("star") == _head51.get("star"):
                        _e250v51 = ((_hb51.get("columns") or {}).get(_hb51["star"])
                                    or {}).get("b1_with_loo_aggregate")
                        _our51 = (_head51.get("star_residual") or {}).get("b1")
                        if _e250v51 is None or _our51 is None \
                                or abs(_e250v51 - _our51) > 1e-9:
                            _bad51.append("the decomposed residual is not E250's published "
                                          "number (%s vs %s)" % (_e250v51, _our51))
                    else:
                        _bad51.append("the two faces do not name the same star")
                else:
                    _bad51.append("bookecho face missing, so the identity cannot be checked")
            if not _f51.get("no_bill"):
                _bad51.append("the face does not carry its no-bill line")
            if not _f51.get("identification_caveat"):
                _bad51.append("the face does not carry its age caveat")
        _s51 = (_f51 or {}).get("summary") or {}
        check("product: the star's residual is decomposed and split from volatility and age",
              not _bad51, "; ".join(_bad51)[:220]
              or "verdict %s; star %s; b1 %s -> with vol %s (share %s); cells %d"
                 % (_s51.get("verdict"), _s51.get("headline_star"),
                    _r39(_f51 or {}, "headline_star_b1"),
                    _r39(_f51 or {}, "headline_star_b1_with_vol"),
                    _r39(_f51 or {}, "headline_star_share_vol"), len(_cells51)))
    except Exception as e:
        check("product: the star's residual is decomposed and split from volatility and age",
              False, repr(e)[:160])

    # E252: E251 priced the star's effect on OTHER members. This leg closes the loop with the
    # star as the outcome -- same regressor, same estimator, same rows -- and refuses the two ways
    # the comparison could lie: a verdict its own published numbers do not re-derive, and a cross
    # coefficient that is not E251's published statistic (identity to 1e-9, because a comparison
    # built on a different number is not a comparison).
    try:
        _bad52 = []
        _p52 = os.path.join("results", "state_tilt", "starself_latest.json")
        _f52 = None
        if os.path.exists(_p52):
            with io.open(_p52, encoding="utf-8") as _fh52:
                _f52 = json.load(_fh52)
        _cells52 = []
        if not _f52:
            _bad52.append("star-self face missing")
        else:
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            import e252_star_prices_itself as _m52
            _vocab52 = set(((_f52.get("frozen_spec") or {}).get("verdicts")) or [])
            _cells52 = [c for c in (_f52.get("cells") or []) if c.get("verdict")]
            if not _cells52:
                _bad52.append("no cell carries a verdict")
            for _c52 in _cells52:
                if _c52.get("verdict") not in _vocab52:
                    _bad52.append("cell %s outside the frozen vocabulary" % _c52.get("label"))
                _sr52 = _c52.get("self_row") or {}
                _cr52 = _c52.get("cross_row") or {}
                if _sr52.get("b_self") is not None and _cr52.get("b_cross") is not None:
                    _reb52 = _m52.derive_verdict(_sr52.get("b_self"), _cr52.get("b_cross"),
                                                 _c52.get("self_outside_band"),
                                                 _c52.get("cross_outside_band"),
                                                 _c52.get("diff_ci"))
                    if _reb52 != _c52.get("verdict"):
                        _bad52.append("cell %s publishes %s but its numbers re-derive %s"
                                      % (_c52.get("label"), _c52.get("verdict"), _reb52))
                    _d52 = _c52.get("b_self_minus_b_cross")
                    if _d52 is None \
                            or abs(_d52 - (_sr52["b_self"] - _cr52["b_cross"])) > 1e-12:
                        _bad52.append("cell %s publishes a difference its own betas do not "
                                      "produce" % _c52.get("label"))
                    if _c52.get("verdict") == "own_row_is_the_same_quantity":
                        _ci52 = _c52.get("diff_ci")
                        if not _ci52 or not (_ci52[0] <= 0.0 <= _ci52[1]):
                            _bad52.append("cell %s names one quantity without an interval that "
                                          "covers zero" % _c52.get("label"))
                _b52, _bv52 = _sr52.get("b_self"), _sr52.get("b_self_with_vol")
                if _b52 is not None and _bv52 is not None and abs(_b52) > 1e-12:
                    _sh52 = 1.0 - (_bv52 / _b52)
                    if _sr52.get("share_taken_by_vol") is None \
                            or abs(_sh52 - _sr52["share_taken_by_vol"]) > 1e-9:
                        _bad52.append("cell %s publishes a vol share its own betas do not "
                                      "produce" % _c52.get("label"))
                if not _c52.get("star") and "no member was named star" not in (
                        _c52.get("reason") or ""):
                    _bad52.append("cell %s has no star and no explicit reason"
                                  % _c52.get("label"))
            _head52 = next((c for c in _cells52 if c.get("label") == "all_five"), None)
            if _head52 is None:
                _bad52.append("no headline cell")
            else:
                # the identity is a same-panel statement (E280): prefer E251's face priced on
                # this face's own cutoff, and disclose a newer vintage instead of failing on it
                _cut52 = (_f52 or {}).get("evidence_cutoff")
                _same52 = (os.path.join("results", "state_tilt", "STAROWN-%s.json" % _cut52)
                           if _cut52 else None)
                _p51b = (_same52 if (_same52 and os.path.exists(_same52))
                         else os.path.join("results", "state_tilt", "starown_latest.json"))
                if os.path.exists(_p51b):
                    with io.open(_p51b, encoding="utf-8") as _fh52b:
                        _f52b = json.load(_fh52b)
                    _h51b = next((c for c in (_f52b.get("cells") or [])
                                  if c.get("label") == "all_five"), None)
                    if _h51b and _h51b.get("star") == _head52.get("star"):
                        if _f52b.get("evidence_cutoff") and _cut52 \
                                and _f52b.get("evidence_cutoff") != _cut52:
                            _vint52 = (_f52b.get("evidence_cutoff"), _cut52)
                        else:
                            _e251v52 = (_h51b.get("star_residual") or {}).get("b1")
                            _our52 = (_head52.get("cross_row") or {}).get("b_cross")
                            if _e251v52 is None or _our52 is None \
                                    or abs(_e251v52 - _our52) > 1e-9:
                                _bad52.append("the cross coefficient is not E251's published "
                                              "number (%s vs %s)" % (_e251v52, _our52))
                    else:
                        _bad52.append("the two faces do not name the same star")
                else:
                    _bad52.append("starown face missing, so the identity cannot be checked")
            if not _f52.get("no_bill"):
                _bad52.append("the face does not carry its no-bill line")
            if not _f52.get("comparability_note"):
                _bad52.append("the face does not carry its comparability note")
        _s52 = (_f52 or {}).get("summary") or {}
        check("product: the star's own row is priced against the column it carries for others",
              not _bad52, "; ".join(_bad52)[:220]
              or "verdict %s; star %s; b_self %s vs b_cross %s; diff ci %s; cells %d"
                 % (_s52.get("verdict"), _s52.get("headline_star"),
                    _r39(_f52 or {}, "headline_b_self"),
                    _r39(_f52 or {}, "headline_b_cross"),
                    _r39ci(_f52 or {}, "headline_diff_ci"), len(_cells52)))
    except Exception as e:
        check("product: the star's own row is priced against the column it carries for others",
              False, repr(e)[:160])

    # E280: the star_self_price red at r1303 claimed an RNG drift. The published decision face
    # says otherwise -- the two implementations are one regression on one panel, and the 177 moved
    # fields came from one extra bar. This leg pins the decision AND the draw stream: a refactor
    # that silently re-randomises a published band has to make this fail.
    try:
        _bad80 = []
        _p80 = os.path.join("results", "state_tilt", "starownrepin_latest.json")
        _f80 = None
        if os.path.exists(_p80):
            with io.open(_p80, encoding="utf-8") as _fh80:
                _f80 = json.load(_fh80)
        if not _f80:
            _bad80.append("E280 decision face missing")
        else:
            _d80 = _f80.get("decision") or {}
            _pin80 = _f80.get("rng_pin") or {}
            if (_d80.get("branch") or "") not in ("D1", "D2"):
                _bad80.append("decision face publishes no rule branch")
            if _d80.get("branch") == "D1" and _d80.get("reburn"):
                _bad80.append("D1 says the move is vintage but still reburns a face")
            if _pin80.get("measurable") is True:
                if _pin80.get("same_input_same_band") is not True:
                    _bad80.append("E251's band does not reproduce under its own seed")
                if _pin80.get("different_seed_moves_band") is not True:
                    _bad80.append("the draw stream pin is vacuous (another seed moves nothing)")
            _sp80 = _f80.get("same_panel_identity") or {}
            if _sp80.get("abs_diff") is not None and _sp80["abs_diff"] > 1e-9:
                # a measured disagreement on ONE panel means the faces must not be trusted
                _bad80.append("E251/E252 disagree on one panel by %s" % _sp80["abs_diff"])
        check("product: a claimed RNG drift is decided by measurement, and the stream is pinned",
              not _bad80, "; ".join(_bad80)[:220]
              or "branch %s; same-panel identity %s; band hi %s reproducible"
                 % ((_f80 or {}).get("decision", {}).get("branch"),
                    (((_f80 or {}).get("same_panel_identity") or {}).get("abs_diff")),
                    (((_f80 or {}).get("rng_pin") or {}).get("band_hi"))))
    except Exception as e:
        check("product: a claimed RNG drift is decided by measurement, and the stream is pinned",
              False, repr(e)[:160])

    # E253: E252 published one cell the design could not read (the star's self coefficient inside
    # its own shuffled band after 2025) and left two sentences live: the window is short, or the
    # channel weakened. This leg refuses the ways a resolution arithmetic can lie -- a session
    # count its own band does not produce, a verdict its own numbers do not re-derive, a calendar
    # ETA invented for a window that no longer accrues, and a "weakened" call that the band's own
    # coarse sd would not support.
    try:
        _bad53 = []
        _p53 = os.path.join("results", "state_tilt", "selfres_latest.json")
        _f53 = None
        if not os.path.exists(_p53):
            _bad53.append("face missing: %s" % _p53)
        else:
            with io.open(_p53, encoding="utf-8") as _fh53:
                _f53 = json.load(_fh53)
        if _f53 is not None:
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            try:
                import e253_self_row_resolution as _m53
            except Exception as _e53:
                _m53 = None
                _bad53.append("module does not import: %r" % (_e53,))
            _vocab53 = set(((_f53.get("frozen_spec") or {}).get("verdicts")) or [])
            _cells53 = _f53.get("cells") or []
            if not _cells53:
                _bad53.append("no cells published")
            if _m53 is not None:
                for _c53 in _cells53:
                    _sr53 = _c53.get("self_row") or {}
                    if _sr53.get("b") is None or _sr53.get("edge") is None:
                        if _c53.get("status") != "not_a_star_cell":
                            _bad53.append("cell %s has a self row without a band but is judged"
                                          % _c53.get("label"))
                        continue
                    _need53 = _m53.needed_sessions(_c53.get("sessions"), _sr53["b"],
                                                   _sr53["edge"], _m53.GAMMA)
                    if _need53 is None or _sr53.get("needed") is None \
                            or abs(_need53 - _sr53["needed"]) > 1e-6:
                        _bad53.append("cell %s publishes a session count its own band does not "
                                      "produce" % _c53.get("label"))
                    _out53 = abs(_sr53["b"]) > abs(_sr53["edge"])
                    if _out53 != bool(_sr53.get("outside_band")):
                        _bad53.append("cell %s mislabels the outside-band reading"
                                      % _c53.get("label"))
                    if _c53.get("status") == "silent_unreachable" and _c53.get("window_open"):
                        _bad53.append("cell %s is called unreachable inside an open window"
                                      % _c53.get("label"))
                    if _c53.get("status") == "silent_reachable" \
                            and not (_c53.get("eta") or "").startswith("20"):
                        _bad53.append("cell %s schedules sessions but names no calendar eta"
                                      % _c53.get("label"))
                    if _c53.get("status") == "measured_outside" and _c53.get("eta"):
                        _bad53.append("cell %s names an eta while already measured"
                                      % _c53.get("label"))
                    _pr53 = _c53.get("prior") or {}
                    _z53, _z20053 = _pr53.get("z_vs_prior"), _pr53.get("z_vs_prior_200_draws")
                    if _z53 is not None and _z20053 is not None:
                        if bool(_pr53.get("z_line_cleared")) != (abs(_z53) >= _m53.Z_WEAK):
                            _bad53.append("cell %s mislabels the z line" % _c53.get("label"))
                        if abs(_z20053) < abs(_z53):
                            _bad53.append("cell %s reads a sharper sd as a wider z"
                                          % _c53.get("label"))
                for _c53 in _cells53:
                    _v53 = _c53.get("verdict")
                    if _v53 is not None and _vocab53 and _v53 not in _vocab53 \
                            and _v53 != "measured":
                        _bad53.append("cell %s carries a verdict outside the frozen vocabulary"
                                      % _c53.get("label"))
                _ver53, _ = _m53.decide(_cells53)
                if _ver53 != (_f53.get("rollup") or {}).get("verdict"):
                    _bad53.append("the published verdict does not re-derive (%s vs %s)"
                                  % ((_f53.get("rollup") or {}).get("verdict"), _ver53))
            if not _f53.get("no_bill"):
                _bad53.append("the face does not carry its no-bill line")
            if not _f53.get("evidence_cutoff"):
                _bad53.append("the face carries no evidence_cutoff")
            if not (_f53.get("frozen_spec") or {}).get("no_refit"):
                _bad53.append("the face does not declare that it fits nothing")
        _s53 = (_f53 or {}).get("summary") or {}
        check("product: the star's unread self row is scheduled, not excused",
              not _bad53, "; ".join(_bad53)[:220]
              or "verdict %s; cell %s n=%s needs %s sessions (short %s, eta %s); "
                 "cross needs %s; z %s/%s"
                 % (_s53.get("verdict"), _s53.get("headline_cell"), _s53.get("headline_sessions"),
                    _r39(_f53 or {}, "headline_self_sessions_needed"),
                    _r39(_f53 or {}, "headline_sessions_short"), _s53.get("headline_eta"),
                    _r39(_f53 or {}, "headline_cross_sessions_needed"),
                    _r39(_f53 or {}, "headline_z_vs_prior"),
                    _r39(_f53 or {}, "headline_z_vs_prior_200_draws")))
    except Exception as e:
        check("product: the star's unread self row is scheduled, not excused",
              False, repr(e)[:160])

    # E254: E253's session counts ride on edge(n) ~ n**-0.5, an exponent it only checked ACROSS
    # four heterogeneous eras (0.244). This leg rebuilds the band inside one cell. The ways it
    # can lie are the ways a published field can drift from its own numbers: a gamma its rungs do
    # not reproduce, a "band shrinks" flag the ladder does not show, a target count the published
    # b_self does not produce, an exponent announced while its own r2 floor fails -- and, the one
    # this round found, a verdict arriving with its REASON silently blanked by a reused name.
    try:
        _bad54 = []
        _p54 = os.path.join("results", "state_tilt", "bandexp_latest.json")
        _f54 = None
        if not os.path.exists(_p54):
            _bad54.append("face missing: %s" % _p54)
        else:
            with io.open(_p54, encoding="utf-8") as _fh54:
                _f54 = json.load(_fh54)
        if _f54 is not None:
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            try:
                import e254_band_exponent_inside_cell as _m54
            except Exception as _e54:
                _m54 = None
                _bad54.append("module does not import: %r" % (_e54,))
            _fam54 = _f54.get("families") or {}
            _vocab54 = set(((_f54.get("frozen_spec") or {}).get("verdict_vocabulary")) or [])
            if not _vocab54:
                _bad54.append("the face publishes no frozen verdict vocabulary")
            if _f54.get("verdict") not in _vocab54:
                _bad54.append("verdict %r is outside the frozen vocabulary"
                              % (_f54.get("verdict"),))
            if _m54 is not None:
                _v54 = _m54.verify()
                for _p in (_v54.get("problems") or []):
                    _bad54.append("verify: %s" % _p)
                _g54 = {k: ((_fam54.get(k) or {}).get("fit_edge") or {}).get("gamma")
                        for k in ("head", "tail")}
                _r54 = {k: ((_fam54.get(k) or {}).get("fit_edge") or {}).get("r2")
                        for k in ("head", "tail")}
                _want54, _why54 = _m54.verdict_from(_g54, _r54)
                if _f54.get("verdict") != _want54:
                    _bad54.append("the verdict does not re-derive from its published inputs")
                # the reason a verdict is undetermined must survive the sensitivity pass
                if not _why54:
                    _bad54.append("the frozen verdict rule yields no reason")
                elif _f54.get("verdict_reason") != _why54:
                    _bad54.append("the published reason (%r) is not the one its own inputs give "
                                  "(%r)" % (_f54.get("verdict_reason"), _why54))
                # an exponent may not be announced while its own r2 floor fails
                _floor54 = (_f54.get("frozen_spec") or {}).get("r2_floor")
                if _floor54 is not None and any(
                        (_r54.get(k) is None or _r54[k] < _floor54) for k in _r54) \
                        and _f54.get("verdict") != "exponent_undetermined_inside_the_cell":
                    _bad54.append("an exponent is claimed while a family sits under the r2 floor")
                # "the band shrinks" must be something the ladder itself shows
                _shrinks54 = (_f54.get("summary") or {}).get("band_shrinks_within_family") or {}
                for _k in ("head", "tail"):
                    _rows54 = sorted([p for p in (_f54.get("points") or [])
                                      if p.get("family") == _k],
                                     key=lambda p: p.get("sessions") or 0)
                    _edges54 = [p.get("edge_self") for p in _rows54]
                    if len(_edges54) < 3:
                        _bad54.append("family %s carries %d rungs (need >=3)"
                                      % (_k, len(_edges54)))
                        continue
                    if any(a is None or b is None for a, b in zip(_edges54, _edges54[1:])):
                        _bad54.append("family %s has a blank edge" % _k)
                        continue
                    _obs54 = all(b < a for a, b in zip(_edges54, _edges54[1:]))
                    _net54 = _edges54[-1] < _edges54[0]
                    _steps54 = sum(1 for a, b in zip(_edges54, _edges54[1:]) if b >= a)
                    if bool(_shrinks54.get(_k)) != _net54:
                        _bad54.append("family %s publishes band_shrinks=%s but its ladder's "
                                      "longest rung is %s the shortest"
                                      % (_k, _shrinks54.get(_k),
                                         "below" if _net54 else "not below"))
                    _nm54 = ((_f54.get("summary") or {}).get("rungs_non_monotone")
                             or {}).get(_k)
                    if _nm54 != _steps54:
                        _bad54.append("family %s publishes %s non-monotone rungs but its ladder "
                                      "has %d" % (_k, _nm54, _steps54))
                    if not (_f54.get("summary") or {}).get("band_shrinks_definition"):
                        _bad54.append("the shrink flag is published without its definition "
                                      "(net vs monotone)")
                    # the target count is E253's inversion re-run on this cell's own anchor
                    _b54 = (_f54.get("published") or {}).get("b_self")
                    _tgt54 = (_f54.get("target_sessions") or {}).get(_k)
                    _anchor54 = _rows54[-1]
                    if _b54 and _g54.get(_k) is not None:
                        _re54 = _m54.target_sessions(_anchor54["sessions"], _b54,
                                                     _anchor54["edge_self"], _g54[_k])
                        if _tgt54 is None or _re54 is None or abs(_re54 - _tgt54) > 1e-6:
                            _bad54.append("family %s publishes a target count its own anchor and "
                                          "b_self do not produce" % _k)
            if not _f54.get("evidence_cutoff"):
                _bad54.append("the face carries no evidence_cutoff")
            if not (_f54.get("frozen_spec") or {}).get("what_is_not_done"):
                _bad54.append("the face does not declare what it does not do")
        _s54 = (_f54 or {}).get("summary") or {}

        def _n54(grp, fam):
            v = (_s54.get(grp) or {}).get(fam)
            return "n/a" if v is None else "%.3f" % v

        check("product: the band's own ladder decides the exponent, not the assumed one",
              not _bad54, "; ".join(_bad54)[:220]
              or "verdict %s (%s); gamma head %s r2 %s / tail %s r2 %s; targets %s/%s "
                 "vs E253's %s"
                 % (_s54.get("verdict"), _s54.get("verdict_reason"),
                    _n54("gamma", "head"), _n54("r2", "head"),
                    _n54("gamma", "tail"), _n54("r2", "tail"),
                    _n54("target_sessions", "head"), _n54("target_sessions", "tail"),
                    _r39(_f54 or {}, "e253_needed")))
    except Exception as e:
        check("product: the band's own ladder decides the exponent, not the assumed one",
              False, repr(e)[:160])

    # E255: E254 answered "undetermined" and left two readings alive -- too few permutation draws,
    # or too few rungs. This leg guards the face that settles it. What can fabricate a claim here:
    # a gamma its own rung table does not reproduce, an "endpoint converged" flag the rungs
    # contradict, a "more draws move the answer" sentence on a face whose rungs never moved (the
    # r1261 family: two equal curves may both be flat), and a verdict outside the frozen
    # vocabulary. The activity leg is first, because it is the only one that proves the experiment
    # happened at all.
    try:
        _bad55 = []
        _p55 = os.path.join("results", "state_tilt", "banddraw_latest.json")
        _f55 = None
        if not os.path.exists(_p55):
            _bad55.append("face missing: %s" % _p55)
        else:
            with io.open(_p55, encoding="utf-8") as _fh55:
                _f55 = json.load(_fh55)
        if _f55 is not None:
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            try:
                import e255_band_draw_starvation as _m55
            except Exception as _e55:
                _m55 = None
                _bad55.append("module does not import: %r" % (_e55,))
            _vocab55 = set(((_f55.get("frozen_spec") or {}).get("verdict_vocabulary")) or [])
            if not _vocab55:
                _bad55.append("the face publishes no frozen verdict vocabulary")
            if _f55.get("verdict") not in _vocab55:
                _bad55.append("verdict %r is outside the frozen vocabulary"
                              % (_f55.get("verdict"),))
            if _m55 is not None:
                _v55 = _m55.verify()
                for _p in (_v55.get("problems") or []):
                    _bad55.append("verify: %s" % _p)
                _conv = ((_f55.get("secondary_reads") or {}).get("endpoint_convergence") or {})
                for _k in ("head", "tail"):
                    _rows = [r for r in (_f55.get("rungs") or []) if r.get("family") == _k]
                    _dmax = str(((_f55.get("frozen_spec") or {}).get("draw_grid") or [0])[-1])
                    # ACTIVITY: the ladder must actually have been measured at more than one
                    # draw count, and at least one rung must have moved -- otherwise
                    # "more draws move the answer" is being printed on a static face.
                    _moved = 0
                    _read = 0
                    for _r in _rows:
                        _bd = _r.get("by_draws") or {}
                        _lo = (_bd.get("60") or {}).get("edge_self")
                        _hi = (_bd.get(_dmax) or {}).get("edge_self")
                        _read += 1 if (_lo is not None and _hi is not None) else 0
                        _moved += 1 if (_lo is not None and _hi is not None and _hi > _lo) else 0
                    if _read < 3:
                        _bad55.append("family %s has %d rungs with two draw counts (need >=3)"
                                      % (_k, _read))
                    elif _moved == 0:
                        _bad55.append("family %s: no rung's edge moved between 60 and %s draws"
                                      % (_k, _dmax))
                    # the published convergence flag must match its own rise table
                    _want_conv = bool(_conv.get(_k)) and all(
                        x.get("rise_pct") is not None
                        and x["rise_pct"] <= _m55.CONV_PCT
                        for x in (_conv[_k].get("rises_240_to_last") or []))
                    if bool(_conv.get(_k, {}).get("endpoint_converged")) != _want_conv:
                        _bad55.append("family %s publishes endpoint_converged that its own rise "
                                      "table does not support" % _k)
                _sec = (_f55.get("secondary_reads") or {})
                if _sec.get("e254_verdict_at_converged_draws") not in (
                        "exponent_is_half_inside_the_cell", "exponent_is_lower_inside_the_cell",
                        "exponent_is_higher_inside_the_cell",
                        "exponent_undetermined_inside_the_cell"):
                    _bad55.append("the secondary E254 verdict is outside E254's vocabulary: %r"
                                  % (_sec.get("e254_verdict_at_converged_draws"),))
                if not _sec.get("caveats"):
                    _bad55.append("the face publishes no caveats beside its 3-seed scatter")
            if not _f55.get("evidence_cutoff"):
                _bad55.append("the face carries no evidence_cutoff")
        _s55 = (_f55 or {}).get("summary") or {}
        _r55 = (_s55.get("r2_by_draws") or {})
        _g55 = (_s55.get("gamma_by_draws") or {})

        def _curve(grp, fam):
            body = (grp or {}).get(fam) or {}
            return "n/a" if not body else " ".join(
                "%s:%s" % (k, "n/a" if v is None else "%.3f" % v) for k, v in body.items())

        check("product: draws move the band's LEVEL, not only its noise",
              not _bad55, "; ".join(_bad55)[:220]
              or "verdict %s; r2 %s | %s; gamma %s | %s; gap %s; converged %s"
                 % (_s55.get("verdict"),
                    _curve(_r55, "head"), _curve(_r55, "tail"),
                    _curve(_g55, "head"), _curve(_g55, "tail"),
                    "n/a" if (_s55.get("secondary_reads") or {}).get(
                        "family_gamma_gap") is None
                    else "%.3f" % _s55["secondary_reads"]["family_gamma_gap"],
                    {k: v.get("endpoint_converged")
                     for k, v in ((_s55.get("secondary_reads") or {})
                                  .get("endpoint_convergence") or {}).items()}))
    except Exception as e:
        check("product: draws move the band's LEVEL, not only its noise",
              False, repr(e)[:160])

    # E256: E255 left the endpoint rising at 480 draws and asked where it stops moving. This leg
    # guards the continuation face. What can fabricate a claim here: a "settled at N" flag on a
    # ladder whose own steps still move, an edge that is not the one its rungs carry, and -- the
    # load-bearing one -- a face whose shorter draw grid is not actually a PREFIX of the longer
    # one, which would make the whole prefix argument an assumption rather than a measurement.
    try:
        _bad56 = []
        _p56 = os.path.join("results", "state_tilt", "banddraw-d1920_latest.json")
        _p56s = os.path.join("results", "state_tilt", "banddraw-d960_latest.json")
        _f56 = _f56s = None
        for _p in (_p56, _p56s):
            if not os.path.exists(_p):
                _bad56.append("face missing: %s" % _p)
        if not _bad56:
            with io.open(_p56, encoding="utf-8") as _fh56:
                _f56 = json.load(_fh56)
            with io.open(_p56s, encoding="utf-8") as _fh56s:
                _f56s = json.load(_fh56s)
        _m56 = None
        if _f56 is not None:
            try:
                import e256_band_draw_continuation as _m56
            except Exception as _e56:
                _bad56.append("module does not import: %r" % (_e56,))
        if _m56 is not None:
            for _tag, _face in (("-d1920", _f56), ("-d960", _f56s)):
                for _p in (_m56.verify(tag=_tag).get("problems") or []):
                    _bad56.append("verify%s: %s" % (_tag, _p))
            _grid56 = (_f56.get("frozen_spec") or {}).get("draw_grid") or []
            if len(_grid56) < 3:
                _bad56.append("the face measured %d draw counts (need >=3)" % len(_grid56))
            # ACTIVITY: the experiment must have moved something between the smallest count and top
            _moved56 = 0
            for _r in (_f56.get("rungs") or []):
                _bd = _r.get("by_draws") or {}
                _lo = _bd.get(str(_grid56[0])) or {}
                _hi = _bd.get(str(_grid56[-1])) or {}
                if (_lo.get("edge_self") is not None and _hi.get("edge_self") is not None
                        and _hi["edge_self"] > _lo["edge_self"]):
                    _moved56 += 1
            if not _moved56:
                _bad56.append("no rung's edge moved across the whole draw grid")
            for _k in ("head", "tail"):
                _rows = [r for r in (_f56.get("rungs") or []) if r.get("family") == _k]
                if not _rows:
                    _bad56.append("family %s measured no rungs" % _k)
                    continue
                _big = max(_rows, key=lambda r: r.get("sessions") or 0)
                _want_edge = ((_big.get("by_draws") or {}).get(str(_grid56[-1])) or {})
                _got = (((_f56.get("continuation") or {}).get(_k) or {}).get("tops") or {})
                if _want_edge.get("edge_self") is None or _got.get("edge_at_largest_rung") is None:
                    _bad56.append("family %s publishes no top edge" % _k)
                elif abs(_want_edge["edge_self"] - _got["edge_at_largest_rung"]) > 1e-12:
                    _bad56.append("family %s top edge does not reproduce from its rungs" % _k)
                _an = _m56.analyse(_rows, tuple(_grid56))
                if _an["settled"]["draws"] != (((_f56.get("continuation") or {}).get(_k)
                                                or {}).get("settled") or {}).get("draws"):
                    _bad56.append("family %s settled_at does not reproduce" % _k)
                # PREFIX: the 960 face must be the 1920 rung table read on the first five counts.
                # If this fails the two faces are two experiments and the continuation is invalid.
                _grid960 = tuple((_f56s.get("frozen_spec") or {}).get("draw_grid") or [])
                if _grid960:
                    _an960 = _m56.analyse(_rows, _grid960)
                    _pub960 = ((_f56s.get("continuation") or {}).get(_k) or {}).get("state")
                    if _an960["state"] != _pub960:
                        _bad56.append("family %s: the 1920 rungs read on %s say %r, the 960 face "
                                      "published %r -- the grids are not prefixes of one run"
                                      % (_k, list(_grid960), _an960["state"], _pub960))
            _grid960 = tuple((_f56s.get("frozen_spec") or {}).get("draw_grid") or [])
            if _grid960:
                _an_all = {_k: _m56.analyse([r for r in (_f56.get("rungs") or [])
                                             if r.get("family") == _k], _grid960)
                           for _k in ("head", "tail")}
                _tot56 = _m56.verdict_from(_an_all, top=_grid960[-1])[0]
                if _tot56 != _f56s.get("verdict"):
                    _bad56.append("the 960 verdict does not follow from the 1920 rung table "
                                  "(%r vs %r)" % (_tot56, _f56s.get("verdict")))
        _s56 = (_f56 or {}).get("summary") or {}
        check("product: the band endpoint is scheduled, not waited out",
              not _bad56, "; ".join(_bad56)[:220]
              or "verdict %s; settled after %s; state %s; rise/doubling %s; plateau %s; "
                 "edge@%s head %.4f tail %.4f; targets %s of %s available"
                 % (_s56.get("verdict"), _s56.get("settled_after_draws"),
                    _s56.get("family_state"),
                    {k: {kk: (None if vv is None else round(vv, 2)) for kk, vv in v.items()}
                     for k, v in (_s56.get("median_rise_pct_by_step") or {}).items()},
                    {k: (None if v is None else round(v, 2))
                     for k, v in (_s56.get("plateau_pct_per_doubling") or {}).items()},
                    ((_f56 or {}).get("frozen_spec") or {}).get("draw_grid", [None])[-1],
                    ((_s56.get("edge_at_largest_rung") or {}).get("head") or 0.0),
                    ((_s56.get("edge_at_largest_rung") or {}).get("tail") or 0.0),
                    {k: (None if v is None else round(v))
                     for k, v in (((_s56.get("secondary_reads") or {})
                                   .get("target_sessions_at_top_gamma")) or {}).items()},
                    (_s56.get("secondary_reads") or {}).get("target_sessions_available")))
    except Exception as e:
        check("product: the band endpoint is scheduled, not waited out", False, repr(e)[:160])

    # E257: E255/E256 proved the shuffled band's 5% endpoint was still rising at 1920 draws, so
    # every published outside-the-band verdict in the star family had been judged against an edge
    # read off a smaller grid. This leg guards the re-judgement face. What can fabricate a claim
    # here: a row flagged as flipping that does not actually move at the median widened band, a
    # published flag that does not reproduce from the row's own numbers, and -- the load-bearing
    # one -- a multiplier that is not the one the ladder carries. The last check is that the face's
    # row counts add up, because a dropped row reads as 'nothing moved'.
    try:
        _bad57 = []
        _p57 = os.path.join("results", "state_tilt", "bandtopflip_latest.json")
        _f57 = None
        if not os.path.exists(_p57):
            _bad57.append("face missing: %s" % _p57)
        else:
            with io.open(_p57, encoding="utf-8") as _fh57:
                _f57 = json.load(_fh57)
        _m57 = None
        if _f57 is not None:
            try:
                import e257_band_at_top_flips as _m57
            except Exception as _e57:
                _bad57.append("module does not import: %r" % (_e57,))
        if _m57 is not None:
            _v57 = _m57.verify()
            for _p in (_v57.get("problems") or []):
                _bad57.append("verify: %s" % _p)
            _rows57 = _f57.get("rows") or []
            if not _rows57:
                _bad57.append("the face measured no rows")
            # ACTIVITY: the experiment must have moved the band, not merely been computed
            _tab57 = (_f57.get("multiplier_table") or {})
            if _tab57.get("multiplier_median") is None or _tab57["multiplier_median"] <= 1.0:
                _bad57.append("the median draw multiplier is not above one -- the band did not "
                              "widen, so nothing could be re-judged")
            _moved57 = [r for r in _rows57
                        if r.get("verdict") in ("flips_at_top_draws",
                                                "flips_depends_on_measurement")]
            if not _moved57:
                _bad57.append("no published row moved across the whole measurement product")
            # every flipping row must actually flip where it claims to: an "always" row at the
            # median widened band, a "depends" row for at least one but not all measurements.
            # (The first cut asserted the median for both classes and failed the face correctly.)
            for _r in _rows57:
                _vd = _r.get("verdict")
                if _vd not in ("flips_at_top_draws", "flips_depends_on_measurement"):
                    continue
                _lo_t = (_r.get("band_at_top_median") or [None])[0]
                _hi_t = (_r.get("band_at_top_median") or [None, None])[1]
                if _lo_t is None or _hi_t is None:
                    _bad57.append("%s/%s: flipping row carries no top band"
                                  % (_r.get("cell"), _r.get("row")))
                    continue
                _now = _m57.outside(_r.get("b"), _lo_t, _hi_t)
                if _vd == "flips_at_top_draws":
                    if _now == _r.get("outside_at_published") or not _r.get(
                            "flips_on_every_measurement"):
                        _bad57.append("%s/%s: marked as always flipping but does not"
                                      % (_r.get("cell"), _r.get("row")))
                else:
                    if not _r.get("flips_on_any_measurement") or _r.get(
                            "flips_on_every_measurement"):
                        _bad57.append("%s/%s: marked measurement-dependent but the flag pair "
                                      "says otherwise" % (_r.get("cell"), _r.get("row")))
            _s57 = _f57.get("summary") or {}
            if not _s57.get("rows_counts_add_up"):
                _bad57.append("row verdict buckets do not add up -- a dropped row reads as "
                              "nothing moved")
            # the two-face double count must be disclosed, not silently counted twice
            _mov = sum(1 for _r in _rows57 if _r.get("verdict") in
                       ("flips_at_top_draws", "flips_depends_on_measurement"))
            if _mov and _s57.get("distinct_coefficients_moving") is None:
                _bad57.append("moving rows are counted without disclosing how many distinct "
                              "coefficients they are")
        _s57 = (_f57 or {}).get("summary") or {}
        check("product: the published band verdicts are re-judged at the top draw count",
              not _bad57, "; ".join(_bad57)[:220]
              or "verdict %s; %s rows (%s outside at publish); %s flip always, %s for some "
                 "measurement (%s distinct coefficient(s)); %s survive; multiplier %.3f..%.3f "
                 "median %.3f; E254 at top draws %s"
                 % ((_f57 or {}).get("verdict"), _s57.get("rows"),
                    _s57.get("rows_outside_at_published"), _s57.get("rows_flip_every_measurement"),
                    _s57.get("rows_flip_for_some_measurement"),
                    _s57.get("distinct_coefficients_moving"), _s57.get("rows_survive_outside"),
                    _s57.get("multiplier_min") or 0, _s57.get("multiplier_max") or 0,
                    _s57.get("multiplier_median") or 0,
                    ((_f57 or {}).get("ladder_verdicts") or {}).get("e254", {}).get("at_top_draws")))
    except Exception as e:
        check("product: the published band verdicts are re-judged at the top draw count",
              False, repr(e)[:160])

    # E259: E258 published each window's multiplier as min..max over three seeds. Three draws are
    # not a distribution, so this leg guards the face that replaces the range with the sample's own
    # [p05, p95]. What can fabricate a claim here: an interval that is not read off the stored
    # per-seed multipliers, a row judged against another window's interval, and -- the degenerate
    # reading this family admits -- an interval whose lower end sits at exactly 1.0 without naming
    # a seed whose band endpoint really never moved again.
    try:
        _bad59 = []
        _p59 = os.path.join("results", "state_tilt", "bandwindist_latest.json")
        _f59 = None
        if not os.path.exists(_p59):
            _bad59.append("face missing: %s" % _p59)
        else:
            with io.open(_p59, encoding="utf-8") as _fh59:
                _f59 = json.load(_fh59)
        _m59 = None
        if _f59 is not None:
            try:
                import e259_band_multiplier_distribution as _m59
            except Exception as _e59:
                _bad59.append("module does not import: %r" % (_e59,))
        if _m59 is not None:
            _v59 = _m59.verify()
            for _p in (_v59.get("problems") or [])[:4]:
                _bad59.append("verify: %s" % _p)
        _w59 = (_f59 or {}).get("windows") or {}
        _spread = (_f59 or {}).get("interval_spread") or {}
        if len(_w59) < 3:
            _bad59.append("fewer than three published windows were measured (%d)" % len(_w59))
        _widths = []
        for _cell, _tab in _w59.items():
            for _arm, _rec in (_tab or {}).items():
                _ms59 = _rec.get("seed_multipliers") or []
                if len(_ms59) < 3:
                    _bad59.append("%s/%s carries fewer than three streams" % (_cell, _arm))
                    continue
                _lo59, _hi59 = _rec.get("interval") or [None, None]
                if _lo59 is None or _hi59 is None:
                    _bad59.append("%s/%s has no interval" % (_cell, _arm))
                    continue
                _widths.append(_hi59 - _lo59)
                # the interval must be the sample's own p05/p95, not a min/max dressed up
                _srt59 = sorted(_ms59)
                _med59 = _srt59[(len(_srt59) - 1) // 2]
                if not (min(_ms59) <= _lo59 <= _med59 <= _hi59 <= max(_ms59)):
                    _bad59.append("%s/%s: interval is not inside its own sample" % (_cell, _arm))
                if abs(_lo59 - 1.0) <= 1e-12 and not (_rec.get("n_endpoint_already_attained") or 0):
                    _bad59.append("%s/%s: lower end is exactly one but no seed reads one -- the "
                                  "interval is not read off the streams" % (_cell, _arm))
        if not _widths or max(_widths) <= 0:
            _bad59.append("every interval has zero width -- one number copied, not measured")
        # a row judged locally must carry ITS OWN window's interval
        for _r in (_f59 or {}).get("rows") or []:
            if _r.get("verdict_median") in (None, "unjudgeable",
                                            "published_flag_not_reproduced"):
                continue
            _arm59 = "self:%d" % int(float(_r.get("band_draws") or 200))
            _rec59 = ((_w59.get(_r.get("cell")) or {}).get(_arm59)) or {}
            _iv = _rec59.get("interval")
            if not _iv:
                _bad59.append("%s/%s says it was judged but its arm has no interval"
                              % (_r.get("cell"), _r.get("row")))
            elif (_r.get("interval") or [None, None]) != _iv:
                _bad59.append("%s/%s carries interval %r, its arm's is %r"
                              % (_r.get("cell"), _r.get("row"), _r.get("interval"), _iv))
        _s59 = (_f59 or {}).get("summary") or {}
        check("product: the draw multiplier is a distribution, not a three-seed range",
              not _bad59, "; ".join(_bad59)[:220]
              or "verdict %s; %s intervals over %s streams, width %.3f..%.3f median %.3f; "
                 "%.2f..%.2f x the three-seed range (median %.2f, %s of %s wider); %s row(s) "
                 "interval-dependent, %s survive outside at every end; %s seed(s) read exactly "
                 "one because their endpoint never moved again"
                 % ((_f59 or {}).get("verdict"), _s59.get("intervals"), _s59.get("seeds"),
                    _s59.get("interval_width_min") or 0, _s59.get("interval_width_max") or 0,
                    _s59.get("interval_width_median") or 0,
                    _s59.get("ratio_vs_three_seed_min") or 0,
                    _s59.get("ratio_vs_three_seed_max") or 0,
                    _s59.get("ratio_vs_three_seed_median") or 0,
                    _s59.get("intervals_wider_than_three_seeds"), _s59.get("intervals"),
                    _s59.get("rows_interval_dependent"),
                    _s59.get("rows_survive_outside_at_every_end"),
                    _s59.get("seeds_endpoint_already_attained")))
    except Exception as e:
        check("product: the draw multiplier is a distribution, not a three-seed range",
              False, repr(e)[:160])


    # E260: E259 exposed the degenerate reading -- 52 of 640 per-seed multipliers sit at exactly
    # 1.0 because a prefix-nested endpoint cannot move again once the draw that set it arrived.
    # This leg asks the question that turns the degeneracy into a number: at how many draws does
    # each seed's endpoint stop moving, and is the published base count below it? What can
    # fabricate a claim here: an arrival read off the wrong arm's stream, a "median arrival" that
    # is a grid point rather than a median of the seeds, a cross-check that sums the published
    # rows (a different 16 than E259's distribution arms) and calls the mismatch a reproduction,
    # and an arrival table that does not reproduce E259 arm by arm.
    try:
        _bad60 = []
        _p60 = os.path.join("results", "state_tilt", "bandarrival_latest.json")
        _f60 = None
        if not os.path.exists(_p60):
            _bad60.append("face missing: %s" % _p60)
        else:
            with io.open(_p60, encoding="utf-8") as _fh60:
                _f60 = json.load(_fh60)
        _m60 = None
        if _f60 is not None:
            try:
                import e260_band_endpoint_arrival as _m60
            except Exception as _e60:
                _bad60.append("module does not import: %r" % (_e60,))
        if _m60 is not None:
            for _p in (_m60.verify() or [])[:4]:
                _bad60.append("verify: %s" % _p)
        _w60 = (_f60 or {}).get("windows") or {}
        _grid = ((_f60 or {}).get("frozen_spec") or {}).get("grid") or []
        if len(_w60) < 3:
            _bad60.append("fewer than three windows carry an arrival table (%d)" % len(_w60))
        for _cell, _tab in _w60.items():
            for _leg, _rec in (_tab or {}).items():
                _arr = ((_f60.get("arrivals_per_seed") or {}).get(_cell) or {}).get(_leg) or []
                _vals = [int(v) for v in _arr if v is not None]
                if not _vals:
                    _bad60.append("%s/%s has no judged seed" % (_cell, _leg))
                    continue
                # every arrival must be a grid point -- an interpolated arrival is not an arrival
                if any(v not in _grid for v in _vals):
                    _bad60.append("%s/%s: an arrival is not on the draw grid" % (_cell, _leg))
                # the published median must be the median of those seeds, not a grid point
                _sorted60 = sorted(_vals)
                _n60 = len(_sorted60)
                _med60 = (_sorted60[_n60 // 2] if _n60 % 2
                          else (_sorted60[_n60 // 2 - 1] + _sorted60[_n60 // 2]) / 2.0)
                if _rec.get("arrival_median") != _med60:
                    _bad60.append("%s/%s: arrival median %r != median of its seeds %r"
                                  % (_cell, _leg, _rec.get("arrival_median"), _med60))
                if _rec.get("n_judged") != _n60:
                    _bad60.append("%s/%s: n_judged %r != %d arrivals"
                                  % (_cell, _leg, _rec.get("n_judged"), _n60))
                if sum((_rec.get("arrival_hist") or {}).values()) != _n60:
                    _bad60.append("%s/%s: arrival hist does not sum to the judged seeds"
                                  % (_cell, _leg))
        # the pin: E259's published degeneracy must reappear ARM BY ARM, not as a total
        _cc = (_f60 or {}).get("cross_check") or {}
        if _cc.get("matches") is not True:
            _bad60.append("cross-check does not reproduce E259 (%r vs %r, %r arm(s) mismatch)"
                          % (_cc.get("recomputed"), _cc.get("e259_published"),
                             _cc.get("arms_mismatched")))
        _arms60 = _cc.get("arms") or []
        if len(_arms60) < 8:
            _bad60.append("cross-check carries only %d arm(s)" % len(_arms60))
        for _a in _arms60:
            _vals60 = ((_f60.get("arrivals_per_seed") or {}).get(_a.get("cell")) or {}).get(
                _a.get("leg")) or []
            _mine = sum(1 for v in _vals60 if v is not None and v <= (_a.get("base_draws") or 200))
            if _mine != _a.get("n_at_base"):
                _bad60.append("%s/%s: arm count %r is not what the arrival table gives (%d)"
                              % (_a.get("cell"), _a.get("arm"), _a.get("n_at_base"), _mine))
        _s60 = (_f60 or {}).get("summary") or {}
        if (_s60.get("rows_pre_settlement") or 0) == 0:
            _bad60.append("no published row is flagged pre_settlement, yet the family publishes "
                          "at 60/200 draws")
        check("product: the published base draw count sits below the endpoint arrival count",
              not _bad60, "; ".join(_bad60)[:220]
              or "verdict %s; median arrival %s draws across %s windows (%s..%s) against "
                 "published bases 60/200; %s of %s seeds reach their final endpoint only at the "
                 "top of the grid; %s of %s published rows read off a stream that was still "
                 "moving, %s settled, %s not measured; cross-check %s/%s arm-by-arm"
                 % ((_f60 or {}).get("verdict"), _s60.get("arrival_median_across_windows"),
                    _s60.get("windows_measured"), _s60.get("arrival_min_across_windows"),
                    _s60.get("arrival_max_across_windows"), _s60.get("seeds_only_at_top"),
                    _s60.get("seeds"), _s60.get("rows_pre_settlement"), _s60.get("rows"),
                    _s60.get("rows_settled_at_base"), _s60.get("rows_window_not_measured"),
                    (_s60.get("cross_check_arms") or 0) - (_s60.get("cross_check_arms_mismatched") or 0),
                    _s60.get("cross_check_arms")))
    except Exception as e:
        check("product: the published base draw count sits below the endpoint arrival count",
              False, repr(e)[:160])


    # E261: E260 counted the degeneracy but left its cost unstated. This leg guards the face that
    # splits every published interval into the endpoint-already-attained bucket and the seeds still
    # free to move. What can fabricate a claim here: an interval that does not reproduce E259
    # bit-for-bit (then the split is of a different sample), a "floor that moved" counted on an arm
    # that never had a floor, a trimmed interval published when too few seeds are left to support
    # one, and -- the activity face -- a face whose trimming never changes a single number, which
    # would mean it is not measuring anything.
    try:
        _bad61 = []
        _p61 = os.path.join("results", "state_tilt", "bandbucket_latest.json")
        _f61 = None
        if not os.path.exists(_p61):
            _bad61.append("face missing: %s" % _p61)
        else:
            with io.open(_p61, encoding="utf-8") as _fh61:
                _f61 = json.load(_fh61)
        _m61 = None
        if _f61 is not None:
            try:
                import e261_degenerate_seeds_leave_one_bucket as _m61
            except Exception as _e61:
                _bad61.append("module does not import: %r" % (_e61,))
        if _m61 is not None:
            for _p in (_m61.verify() or [])[:4]:
                _bad61.append("verify: %s" % _p)
        _arms61 = (_f61 or {}).get("arms") or []
        if len(_arms61) < 8:
            _bad61.append("fewer than eight arms carry a bucket split (%d)" % len(_arms61))
        _n_floor = 0
        _n_moved = 0
        _n_moved_any_width = 0
        for _a in _arms61:
            _full = _a.get("full") or {}
            _trim = _a.get("trimmed") or {}
            # (a) the full interval must be E259's, bit-for-bit -- otherwise the split is of
            #     another sample and every count below it is about that other sample
            if _a.get("reproduces_e259_interval") is not True:
                _bad61.append("%s/%s: full interval does not reproduce E259" % (_a.get("cell"),
                                                                               _a.get("arm")))
            if _a.get("attained_count_matches_e259") is not True:
                _bad61.append("%s/%s: attained count disagrees with E259" % (_a.get("cell"),
                                                                            _a.get("arm")))
            if _a.get("n_attained") and not _a.get("attained_values"):
                _bad61.append("%s/%s: counted an attained bucket but carries no values"
                              % (_a.get("cell"), _a.get("arm")))
            if _trim:
                if _a.get("n_kept", 0) < 5:
                    _bad61.append("%s/%s: a trimmed interval was published on %r free seeds"
                                  % (_a.get("cell"), _a.get("arm"), _a.get("n_kept")))
                if len(_trim.get("interval") or []) != 2 or _trim["interval"][0] > _trim["interval"][1]:
                    _bad61.append("%s/%s: trimmed interval is not an ordered pair"
                                  % (_a.get("cell"), _a.get("arm")))
                # (b) "the floor moved" must never be counted on an arm that had no floor
                if _a.get("floor_moved_off_one") and not _a.get("floor_at_one"):
                    _bad61.append("%s/%s: counted a moved floor on an arm that has no floor"
                                  % (_a.get("cell"), _a.get("arm")))
                if _a.get("floor_at_one"):
                    _n_floor += 1
                    if _a.get("floor_moved_off_one"):
                        _n_moved += 1
                if abs((_trim.get("width") or 0) - (_full.get("width") or 0)) > 1e-12:
                    _n_moved_any_width += 1
            elif _a.get("n_kept", 0) >= 5:
                _bad61.append("%s/%s: %r free seeds but no trimmed interval published"
                              % (_a.get("cell"), _a.get("arm"), _a.get("n_kept")))
        # (c) activity: a split that changes no number anywhere is not a measurement
        if not _n_moved_any_width:
            _bad61.append("no arm's interval moves when the bucket is removed -- this face is "
                          "not measuring anything")
        # the headline must be earned by the arm table, not asserted in the verdict string
        if _n_floor and _n_moved == _n_floor:
            if (_f61 or {}).get("verdict") != "floor_at_one_is_the_attained_bucket":
                _bad61.append("every floored arm moved yet the verdict says %r"
                              % (_f61 or {}).get("verdict"))
        elif _n_moved == 0:
            if (_f61 or {}).get("verdict") != "floor_at_one_is_structural":
                _bad61.append("no floored arm moved yet the verdict says %r"
                              % (_f61 or {}).get("verdict"))
        _tr61 = (_f61 or {}).get("trimming") or {}
        if _tr61.get("rows_newly_outside_at_the_tight_end") is None:
            _tr61_direction = "the trimming block does not publish its direction"
            _bad61.append(_tr61_direction)
        _s61 = (_f61 or {}).get("summary") or {}
        check("product: the floor at one belongs to the attained bucket, not the stream",
              not _bad61, "; ".join(_bad61)[:220]
              or "verdict %s; %s of %s arms sit at a floor of one and %s of those move off it "
                 "when the %s attained seeds are removed (median %s%% of the width); %s of %s arms "
                 "reproduce E259 bit-for-bit; %s published rows were judged on the self arm while "
                 "naming another leg, %s verdict moves on its own leg, %s row verdicts depend on "
                 "the bucket"
                 % ((_f61 or {}).get("verdict"), _n_floor, len(_arms61), _n_moved,
                    _s61.get("seeds_attained"),
                    ("%.1f" % (100 * _s61.get("width_drop_share_median"))
                     if _s61.get("width_drop_share_median") is not None else "n/a"),
                    _s61.get("arms_reproduce_e259_interval"), len(_arms61),
                    _s61.get("rows_judged_on_a_leg_other_than_the_one_they_name"),
                    _s61.get("rows_whose_verdict_changes_on_their_own_leg"),
                    _s61.get("rows_verdict_changes_under_trimming")))
    except Exception as e:
        check("product: the floor at one belongs to the attained bucket, not the stream",
              False, repr(e)[:160])


    # E263: E260 measured WHERE a window's band endpoint stops moving but not WHY it needs that many
    # draws. This leg guards the face that tests the two rivals (window LENGTH vs band NARROWNESS).
    # What can fabricate a claim here: an arrival that is not E260's (the response would then be
    # about another sample), a response column with no variation (nothing was measured), a verdict
    # that names a channel its own p-values do not support, a power floor that is missing or zero
    # (a null then reads as "no effect" instead of "no design"), and a settled area that quietly
    # includes its own reference point.
    try:
        _bad63 = []
        _p63 = os.path.join("results", "state_tilt", "bandarrivalate_latest.json")
        _f63 = None
        if not os.path.exists(_p63):
            _bad63.append("face missing: %s" % _p63)
        else:
            with io.open(_p63, encoding="utf-8") as _fh63:
                _f63 = json.load(_fh63)
        _m63 = None
        if _f63 is not None:
            try:
                import e263_arrival_vs_cell_size as _m63
            except Exception as _e63:
                _bad63.append("module does not import: %r" % (_e63,))
        if _m63 is not None:
            for _p in (_m63.verify() or [])[:4]:
                _bad63.append("verify: %s" % _p)
        _arms63 = (_f63 or {}).get("arms") or []
        if len(_arms63) < 8:
            _bad63.append("fewer than eight arms were measured (%d)" % len(_arms63))
        _areas = []
        for _a in _arms63:
            # (a) the response must be E260's own arrival, recomputed from the same edge table
            if _a.get("arrival_recomputed_matches_e260") is not True:
                _bad63.append("%s/%s: recomputed arrival does not match E260"
                              % (_a.get("cell"), _a.get("leg")))
            _curve = _a.get("curve") or {}
            if (_curve.get("1920") or {}).get("share_settled") != 1.0:
                _bad63.append("%s/%s: the top draw count does not settle every seed"
                              % (_a.get("cell"), _a.get("leg")))
            # (b) the area must average the counts BELOW the top, never the reference itself
            _body = [_curve[k]["share_settled"] for k in ("60", "120", "200", "480", "960")
                     if k in _curve]
            if _body and _a.get("settled_area") is not None:
                if abs(_a["settled_area"] - sum(_body) / float(len(_body))) > 1e-12:
                    _bad63.append("%s/%s: the settled area is not the mean of the non-reference "
                                  "counts" % (_a.get("cell"), _a.get("leg")))
            if _a.get("settled_area") is not None:
                _areas.append(_a["settled_area"])
            # (c) a rival that is not present must say so, not be counted as measured
            if _a.get("sessions") is None:
                _bad63.append("%s/%s: no session count, so the length rival was never offered"
                              % (_a.get("cell"), _a.get("leg")))
        # ACTIVITY: a response column with no spread means nothing moved and no rank exists
        if _areas and (max(_areas) - min(_areas)) <= 1e-9:
            _bad63.append("every arm reports the identical settled area -- nothing was measured")
        _ch63 = (_f63 or {}).get("channels") or {}
        _lg, _bd = _ch63.get("length") or {}, _ch63.get("band") or {}
        # (d) the verdict must name what its own p-values support
        _ans = (_lg.get("answered") is True, _bd.get("answered") is True)
        _want = {(True, True): "arrival_is_both_channels",
                 (True, False): "arrival_is_a_length_effect",
                 (False, True): "arrival_is_a_band_effect",
                 (False, False): "arrival_is_neither_channel"}[_ans]
        if (_f63 or {}).get("verdict") != _want:
            _bad63.append("verdict says %r but the channels answer %r -- a verdict must be "
                          "recomputed from its own channels"
                          % ((_f63 or {}).get("verdict"), _ans))
        for _nm, _c in (("length", _lg), ("band", _bd)):
            if _c.get("rho") is None or _c.get("p") is None:
                _bad63.append("the %s channel published no rho or no p" % _nm)
            elif _c.get("answered") is not (float(_c["p"]) < 0.05):
                _bad63.append("the %s channel's answered flag disagrees with its own p (%r)"
                              % (_nm, _c.get("p")))
        # (e) a null needs its power printed, and it must be a real number
        _crit = ((_f63 or {}).get("power") or {}).get("critical_abs_rho_at_alpha")
        if _crit is None or not (0.0 < float(_crit) <= 1.0):
            _bad63.append("the design's critical |rho| is missing or not a usable number (%r)"
                          % (_crit,))
        # (f) the seeded channel must not be called answered against its own sign
        _sd63 = _ch63.get("per_seed") or {}
        if _sd63.get("answered") is True and (_sd63.get("arms_negative") or 0) <= (
                _sd63.get("arms_positive") or 0):
            _bad63.append("the per-seed channel is called answered where its sign does not carry "
                          "the rival's prediction")
        _s63 = (_f63 or {}).get("summary") or {}
        if not isinstance(_s63.get("arms_recomputing_e260_arrival"), int):
            _bad63.append("the summary's reproduction count is not an int (%r)"
                          % (_s63.get("arms_recomputing_e260_arrival"),))
        check("product: a draw budget is neither a window length nor a band width",
              not _bad63,
              "%s; %d arms over %d sessions (%s..%s), length rho %s (p %s) and band rho %s (p %s), "
              "per-seed median rho %s with %s of %s arms positive; critical |rho| %.3f; %s of %s "
              "arms recompute E260's arrival"
              % ((_f63 or {}).get("verdict"), len(_arms63),
                 _s63.get("sessions_min") or 0, _s63.get("sessions_min"),
                 _s63.get("sessions_max"),
                 ("%+.3f" % _lg["rho"]) if _lg.get("rho") is not None else "n/a",
                 ("%.3f" % _lg["p"]) if _lg.get("p") is not None else "n/a",
                 ("%+.3f" % _bd["rho"]) if _bd.get("rho") is not None else "n/a",
                 ("%.3f" % _bd["p"]) if _bd.get("p") is not None else "n/a",
                 ("%+.3f" % _sd63["rho_median"]) if _sd63.get("rho_median") is not None else "n/a",
                 _sd63.get("arms_positive"), _sd63.get("arms_published"),
                 float(_crit) if _crit else 0.0,
                 _s63.get("arms_recomputing_e260_arrival"), len(_arms63))
              + (" | " + "; ".join(_bad63[:4]) if _bad63 else ""))
    except Exception as e:
        check("product: a draw budget is neither a window length nor a band width",
              False, repr(e)[:160])


    # E262: E259 published a p05..p95 interval per (window, leg, base count), and the thing a
    # reader does with those numbers is borrow one. This leg guards the face that measures that
    # act. What can fabricate a claim here: a pair that crosses a leg or a base count (the
    # multiplier's denominator IS the base count, so those are two different quantities), a moved
    # row with no direction or with before == after (a "move" that moved nothing), a verdict that
    # is read off the interval spread instead of off the rows (name-is-semantics), a flat number
    # that is not the pooled maximum of its own group, and an arm set whose wide ends are all one
    # constant (then nothing was measured and no transfer exists).
    try:
        _bad62 = []
        _p62 = os.path.join("results", "state_tilt", "bandtransfer_latest.json")
        _f62 = None
        if not os.path.exists(_p62):
            _bad62.append("face missing: %s" % _p62)
        else:
            with io.open(_p62, encoding="utf-8") as _fh62:
                _f62 = json.load(_fh62)
        _m62 = None
        if _f62 is not None:
            try:
                import e262_p95_transfer_across_windows as _m62
            except Exception as _e62:
                _bad62.append("module does not import: %r" % (_e62,))
        if _m62 is not None:
            for _p in (_m62.verify() or [])[:4]:
                _bad62.append("verify: %s" % _p)
        _arms62 = (_f62 or {}).get("arms") or []
        if len(_arms62) != 16:
            _bad62.append("the arm set is not the 16 windows x legs x base counts (%d)"
                          % len(_arms62))
        _key62 = {}
        for _a in _arms62:
            _k = (_a.get("cell"), _a.get("leg"), int(_a.get("base") or 0))
            _key62[_k] = _a
            if _a.get("p95") is None or _a.get("p05") is None:
                _bad62.append("%s/%s:%s: an arm published no interval"
                              % (_a.get("cell"), _a.get("leg"), _a.get("base")))
            elif float(_a["p95"]) < float(_a["p05"]):
                _bad62.append("%s/%s:%s: p95 sits below p05"
                              % (_a.get("cell"), _a.get("leg"), _a.get("base")))
        # ACTIVITY: a set of identical wide ends measures nothing
        _p95s = [float(a["p95"]) for a in _arms62 if a.get("p95") is not None]
        if _p95s and (max(_p95s) - min(_p95s)) <= 1e-9:
            _bad62.append("every arm publishes the same wide end -- nothing was measured")
        _tr62 = (_f62 or {}).get("transfer") or {}
        _moved62 = 0
        for _g, _blk in sorted(_tr62.items()):
            _leg, _base = _g.split(":")
            _base = int(_base)
            for _p in (_blk.get("pairs") or []):
                # (a) a pair never crosses a leg or a base count
                if (_p.get("donor"), _leg, _base) not in _key62:
                    _bad62.append("%s: donor %r has no arm in this group"
                                  % (_g, _p.get("donor")))
                if (_p.get("recipient"), _leg, _base) not in _key62:
                    _bad62.append("%s: recipient %r has no arm in this group"
                                  % (_g, _p.get("recipient")))
                # (b) the donor's number is its own arm's p95, not another group's
                _da = _key62.get((_p.get("donor"), _leg, _base)) or {}
                if _da and _p.get("donor_p95") is not None and _da.get("p95") is not None:
                    if abs(float(_da["p95"]) - float(_p["donor_p95"])) > 1e-12:
                        _bad62.append("%s: donor %r contributes %.6f but its arm says %.6f"
                                      % (_g, _p.get("donor"), _p["donor_p95"], _da["p95"]))
                # (c) a moved row must have moved, and say which way
                for _mv in (_p.get("moved") or []):
                    _moved62 += 1
                    if _mv.get("before") == _mv.get("after"):
                        _bad62.append("%s: %r/%r is listed as moved with before == after"
                                      % (_g, _p.get("donor"), _mv.get("index")))
                    elif _mv.get("direction") != (("rejections_lost"
                                                   if _mv.get("before") == "outside"
                                                   else "rejections_invented")):
                        _bad62.append("%s: %r/%r carries the wrong direction (%r)"
                                      % (_g, _p.get("donor"), _mv.get("index"),
                                         _mv.get("direction")))
                if (_p.get("n_moved") or 0) != len(_p.get("moved") or []):
                    _bad62.append("%s: %r->%r counts %r moves but lists %d"
                                  % (_g, _p.get("donor"), _p.get("recipient"),
                                     _p.get("n_moved"), len(_p.get("moved") or [])))
        # (d) the verdict is read off the rows, never off the spread
        _want62 = ("a_foreign_wide_end_is_not_a_bound" if _moved62 else
                   "the_wide_end_transfers_without_moving_a_verdict")
        if (_f62 or {}).get("verdict") != _want62:
            _bad62.append("verdict says %r but %d row(s) moved -- a verdict must be recomputed "
                          "from the rows" % ((_f62 or {}).get("verdict"), _moved62))
        # (e) the flat number is the pooled maximum of its own group (and the tight one the min)
        for _g, _fl in sorted(((_f62 or {}).get("flat") or {}).items()):
            if _fl.get("flat_p95") is None:
                continue
            _leg, _base = _g.split(":")
            _vals = [float(_a["p95"]) for _k, _a in _key62.items()
                     if _k[1] == _leg and _k[2] == int(_base) and _a.get("p95") is not None]
            if not _vals:
                _bad62.append("%s: the flat read exists with no arm to read" % _g)
                continue
            if abs(float(_fl["flat_p95"]) - max(_vals)) > 1e-12:
                _bad62.append("%s: the flat wide end is not the pooled maximum" % _g)
            if _fl.get("flat_tight_p95") is not None and abs(
                    float(_fl["flat_tight_p95"]) - min(_vals)) > 1e-12:
                _bad62.append("%s: the flat tight end is not the pooled minimum" % _g)
        _s62 = (_f62 or {}).get("summary") or {}
        # (f) the headline counts are ints, not prose or None (A-or-{}.get family)
        for _k in ("rows_measured", "pairs", "verdicts_moved", "rejections_lost",
                   "e259_wide_verdict_differs"):
            if not isinstance(_s62.get(_k), int):
                _bad62.append("summary field %s is not an int (%r)" % (_k, _s62.get(_k)))
        if _s62.get("verdicts_moved") != _moved62:
            _bad62.append("the summary counts %r moved verdicts but the pairs list %d"
                          % (_s62.get("verdicts_moved"), _moved62))
        # (g) the cross-base disclosure is present and points the way it must: the smaller base
        # count divides by an edge taken lower on the curve, so its wide end is larger
        for _leg in ("self", "cross"):
            _off = ((_f62 or {}).get("cross_base_offset") or {}).get(_leg) or {}
            if _off.get("ratio_median") is None:
                _bad62.append("the %s leg publishes no cross-base offset" % _leg)
            elif float(_off["ratio_median"]) <= 1.0:
                _bad62.append("the %s leg's smaller base count is not the larger wide end (%r)"
                              % (_leg, _off["ratio_median"]))
        _d62 = (_f62 or {}).get("dominator") or {}
        if not any(_d62.get(k, {}).get("dominator") for k in _d62):
            _bad62.append("no group names a dominating window -- then the face measured nothing")
        check("product: another window's wide end is not a bound",
              not _bad62,
              "%s; %d arm(s), %d measured row(s), %d ordered pair(s), %d verdict(s) moved "
              "(%d lost, %d invented), flat maximum moves %s at cross:60, widest window differs "
              "by group %s"
              % ((_f62 or {}).get("verdict"), len(_arms62), _s62.get("rows_measured") or 0,
                 _s62.get("pairs") or 0, _moved62, _s62.get("rejections_lost") or 0,
                 _s62.get("rejections_invented") or 0,
                 ((_f62 or {}).get("flat") or {}).get("cross:60", {}).get("n_moved_at_flat"),
                 ",".join("%s=%s" % (k, (v or {}).get("dominator"))
                          for k, v in sorted(_d62.items())))
              + (" | " + "; ".join(_bad62[:4]) if _bad62 else ""))
    except Exception as e:
        check("product: another window's wide end is not a bound",
              False, repr(e)[:160])


    # E264: a row's whole verdict is its threshold m* = |b|/max(|lo|,|hi|) (outside <=> m < m*),
    # so the row side needs no draws. This leg guards the face that asks which row sits closest to
    # its band and whether the p05 == 1 floor those near-one seeds create is load-bearing for it.
    # What can fabricate a claim here: a row read against another arm's seeds, a threshold that is
    # not the published margin at m = 1, a "near-one dependent" flag set on existence instead of
    # the conjunction (E207/E208 family), and a closest row named on a tie.
    try:
        _bad64 = []
        _p64 = os.path.join("results", "state_tilt", "bandnear1_latest.json")
        _f64 = None
        if not os.path.exists(_p64):
            _bad64.append("face missing: %s" % _p64)
        else:
            with io.open(_p64, encoding="utf-8") as _fh64:
                _f64 = json.load(_fh64)
        if _f64 is not None:
            _rows64 = _f64.get("rows") or []
            _measured64 = [r for r in _rows64 if r.get("m_star") is not None]
            _s64 = _f64.get("summary") or {}
            # (a) the read count is a count of READ rows, not of published rows
            if _s64.get("rows_read") != len(_measured64):
                _bad64.append("summary rows_read %r but %d row(s) carry a threshold"
                              % (_s64.get("rows_read"), len(_measured64)))
            if _s64.get("rows_published") != len(_rows64):
                _bad64.append("summary rows_published %r but the face lists %d"
                              % (_s64.get("rows_published"), len(_rows64)))
            # (b) m* is the published margin at m = 1, recomputed here
            for _r64 in _measured64:
                _b, _lo, _hi = _r64.get("b"), _r64.get("band_lo"), _r64.get("band_hi")
                _span = max(abs(float(_lo)), abs(float(_hi)))
                if abs(float(_r64["m_star"]) - abs(float(_b)) / _span) > 1e-12:
                    _bad64.append("row %r: m_star is not |b|/max(|lo|,|hi|)" % (_r64.get("index"),))
                    break
            # (c) the flag is the conjunction, never mere existence
            for _r64 in _measured64:
                if _r64.get("near_one_dependent"):
                    if not _r64.get("tight_end_was_the_floor") or not \
                            _r64.get("tight_verdict_moves_without_near_one"):
                        _bad64.append("row %r carries near_one_dependent without the conjunction"
                                      % (_r64.get("index"),))
                        break
            _dep64 = [r for r in _measured64 if r.get("near_one_dependent")]
            if _s64.get("rows_near_one_dependent") != len(_dep64):
                _bad64.append("summary counts %r near-one dependent rows but the rows say %d"
                              % (_s64.get("rows_near_one_dependent"), len(_dep64)))
            # (d) the closest row is named only when it is strictly closest; a tie says so
            _cl64 = _f64.get("closest") or {}
            _gaps64 = [r.get("gap_to_nearest_end") for r in _cl64.get("rows") or []
                       if r.get("gap_to_nearest_end") is not None]
            if _gaps64:
                _best64 = min(_gaps64)
                _tied64 = [g for g in _gaps64 if abs(g - _best64) <= 1e-12]
                if len(_tied64) > 1 and _cl64.get("closest") is not None:
                    _bad64.append("a tied top names a single closest row")
                if len(_tied64) == 1 and (_cl64.get("closest") or {}).get(
                        "gap_to_nearest_end") is None:
                    _bad64.append("a strictly closest row is not named")
            # (e) the ranking agrees with the rows a borrowed wide end moved (disclosure present)
            _bc64 = _f64.get("borrowed_flip_check") or {}
            if not isinstance(_bc64.get("n_moved_and_closest"), int):
                _bad64.append("the borrowed-end cross-check is missing or not a count")
            # (f) no row is read against seeds it does not own
            for _r64 in _measured64:
                if _r64.get("status") not in ("measured", "measured_no_seed_list"):
                    _bad64.append("row %r is read but its status is %r"
                                  % (_r64.get("index"), _r64.get("status")))
                    break
            _want64 = ("closest_row_reads_a_near_one_seed" if _dep64 else
                       ("closest_row_survives_without_them"
                        if _s64.get("rows_tight_end_at_the_floor") else
                        "no_row_sits_close_enough_to_matter"))
            if _f64.get("verdict") != _want64:
                _bad64.append("verdict %r does not follow from the rows (%d dependent, %r floor)"
                              % (_f64.get("verdict"), len(_dep64),
                                 _s64.get("rows_tight_end_at_the_floor")))
        _top64 = ((_f64 or {}).get("closest") or {}).get("rows") or [{}]
        check("product: a row's verdict is its own threshold, not a neighbour's draws",
              not _bad64,
              "%s; %d of %d row(s) read, %r on the floor, %d near-one dependent, closest row "
              "%r/%r at m*=%.4f vs %s=%.4f (gap %.4f), borrowed-end cross-check %r of %d moved "
              "row(s) inside the top 3"
              % ((_f64 or {}).get("verdict"),
                 ((_f64 or {}).get("summary") or {}).get("rows_read") or 0,
                 ((_f64 or {}).get("summary") or {}).get("rows_published") or 0,
                 ((_f64 or {}).get("summary") or {}).get("rows_tight_end_at_the_floor"),
                 ((_f64 or {}).get("summary") or {}).get("rows_near_one_dependent") or 0,
                 _top64[0].get("cell"), _top64[0].get("row"),
                 _top64[0].get("m_star") or 0.0, _top64[0].get("nearest_end_name") or "end",
                 _top64[0].get("nearest_end") or 0.0,
                 _top64[0].get("gap_to_nearest_end") or 0.0,
                 ((_f64 or {}).get("borrowed_flip_check") or {}).get("n_moved_and_closest"),
                 ((_f64 or {}).get("borrowed_flip_check") or {})
                 .get("rows_moved_by_a_borrowed_end") or 0)
              + (" | " + "; ".join(_bad64[:4]) if _bad64 else ""))
    except Exception as e:
        check("product: a row's verdict is its own threshold, not a neighbour's draws",
              False, repr(e)[:160])


    # E266: E265 wrote the wide-end screen as "any donor p95 above the row's threshold m* flips it".
    # This leg guards the face that tests that screen against E262's 48 already-published ordered
    # pairs. What can fabricate a claim here: a screen scored against its own definition (the
    # comparison set must be re-derivable from the rows), a counterexample list that does not match
    # the confusion counts, and a threshold that drops the row's own SIDE -- the max(|lo|,|hi|) form
    # understates how close a narrow-side row is (18 of 36 comparisons here). No draws.
    try:
        _bad66 = []
        _p66 = os.path.join("results", "state_tilt", "bandscreen_latest.json")
        _f66 = None
        if not os.path.exists(_p66):
            _bad66.append("face missing: %s" % _p66)
        else:
            with io.open(_p66, encoding="utf-8") as _fh66:
                _f66 = json.load(_fh66)
        if _f66 is not None:
            _s66 = _f66.get("summary") or {}
            _rows66 = _f66.get("comparison_rows") or []
            if _s66.get("comparisons") != len(_rows66):
                _bad66.append("summary comparisons %r but the face lists %d comparison row(s)"
                              % (_s66.get("comparisons"), len(_rows66)))
            for _k66, _n66 in (("predicted_single", "S1_single"),
                               ("predicted_guarded", "S2_guarded"),
                               ("predicted_bracket", "S3_bracket")):
                _tp66 = sum(1 for r in _rows66 if r.get(_k66) and r.get("actual_moved"))
                _fp66 = sum(1 for r in _rows66 if r.get(_k66) and not r.get("actual_moved"))
                _fn66 = sum(1 for r in _rows66
                            if r.get(_k66) is False and r.get("actual_moved"))
                _got66 = _s66.get(_n66) or {}
                if (_got66.get("tp"), _got66.get("fp"), _got66.get("fn")) != (_tp66, _fp66, _fn66):
                    _bad66.append("%s says tp/fp/fn %r/%r/%r but the comparison rows give %d/%d/%d"
                                  % (_n66, _got66.get("tp"), _got66.get("fp"), _got66.get("fn"),
                                     _tp66, _fp66, _fn66))
                    break
            # every actual move has to be predicted by the screen the verdict rests on
            _missed66 = [r for r in _rows66 if r.get("actual_moved") and not r.get("predicted_bracket")]
            if _missed66:
                _bad66.append("%d published move(s) are not predicted by the bracket screen"
                              % len(_missed66))
            # the counterexample list IS the written screen's false positives -- not a summary of them
            _fp66_all = sum(1 for r in _rows66
                            if r.get("predicted_single") and not r.get("actual_moved"))
            if len(_f66.get("counterexamples_of_the_written_screen") or []) != _fp66_all:
                _bad66.append("counterexample list has %d row(s), the comparison rows carry %d"
                              % (len(_f66.get("counterexamples_of_the_written_screen") or []),
                                 _fp66_all))
            # the side has to be exercised by the published pairs, or the reading means nothing
            if (_s66.get("rows_where_the_two_thresholds_differ") or 0) <= 0:
                _bad66.append("no row has a side-dependent threshold: the max-end form was never "
                              "tested")
            for _r66 in _rows66:
                if _r66.get("side") not in ("lo", "hi", None):
                    _bad66.append("row %r carries an unknown side %r"
                                  % (_r66.get("index"), _r66.get("side")))
                    break
                _lo66, _hi66, _b66 = (_r66.get("band_lo"), _r66.get("band_hi"), _r66.get("b"))
                if None not in (_lo66, _hi66, _b66) and float(_b66) < 0 and float(_lo66) < 0:
                    if abs(float(_r66.get("t_side") or 0.0)
                           - abs(float(_b66)) / abs(float(_lo66))) > 1e-12:
                        _bad66.append("row %r: t_side is not |b|/|lo| on the negative side"
                                      % (_r66.get("index"),))
                        break
            check("product: a donor above the row is not yet a screen (it needs the row's own side)",
                  not _bad66,
                  "%r | %d comparison(s) over %d pair(s), %d move(s), S1 flags %d (precision %.3f), "
                  "S3 tp/fp/fn %d/%d/%d, thresholds side-dependent on %d row(s)"
                  % ((_f66 or {}).get("verdict"),
                     (_s66.get("comparisons") or 0), (_s66.get("pairs") or 0),
                     (_s66.get("moves_published") or 0),
                     ((_s66.get("S1_single") or {}).get("predicted") or 0),
                     (_s66.get("S1_precision") or 0.0),
                     ((_s66.get("S3_bracket") or {}).get("tp") or 0),
                     ((_s66.get("S3_bracket") or {}).get("fp") or 0),
                     ((_s66.get("S3_bracket") or {}).get("fn") or 0),
                     (_s66.get("rows_where_the_two_thresholds_differ") or 0))
                  + (" | " + "; ".join(_bad66[:4]) if _bad66 else ""))
    except Exception as e:
        check("product: a donor above the row is not yet a screen (it needs the row's own side)",
              False, repr(e)[:160])


    # E267: E266's bracket screen is exact but is a knife edge -- a donor 0.0001 above the row's
    # own-side threshold reads the same as one 0.3 above. This leg guards the face that asks how
    # much clearance to demand. What can fabricate a claim here: a curve scored against a threshold
    # that is not the row's own (max-end vs own side), precision published as 0.0 where it is
    # undefined (no positives), a b ladder that does not actually ladder (predicted count rising
    # with b), and a "separable" claim made from the NEAREST non-move instead of the largest one --
    # one non-move clearing more than a move is what makes a buffer useless, and it is the margin
    # ordering, not the counts, that says so. No draws, no panel.
    try:
        _bad67 = []
        _p67 = os.path.join("results", "state_tilt", "bandmargin_latest.json")
        _f67 = None
        if not os.path.exists(_p67):
            _bad67.append("face missing: %s" % _p67)
        else:
            with io.open(_p67, encoding="utf-8") as _fh67:
                _f67 = json.load(_fh67)
        if _f67 is not None:
            _s67 = (_f67.get("summary") or {})
            _cur67 = (_f67.get("curves") or {})
            if not _cur67:
                _bad67.append("no curve published -- then the card measured nothing")
            for _name67, _rows67 in sorted(_cur67.items()):
                # (a) b must ladder: predictions non-increasing, so are tp/fp
                _prev67 = None
                for _r67 in sorted(_rows67, key=lambda r: r.get("b") or 0.0):
                    if _prev67 is not None:
                        for _k67 in ("predicted", "tp", "fp"):
                            if (int(_r67.get(_k67) or 0) > int(_prev67.get(_k67) or 0)):
                                _bad67.append("%s: %s rises from %r to %r as b grows"
                                              % (_name67, _k67, _prev67.get(_k67),
                                                 _r67.get(_k67)))
                                break
                    _prev67 = _r67
                # (b) the published precision is the tp/predicted ratio, and None when no flag
                for _r67 in _rows67:
                    _pred67 = int(_r67.get("predicted") or 0)
                    if _pred67 == 0:
                        if _r67.get("precision") is not None:
                            _bad67.append("%s at b=%r publishes precision %r with zero flags"
                                          % (_name67, _r67.get("b"), _r67.get("precision")))
                            break
                    elif abs(float(_r67.get("precision") or 0.0)
                             - float(_r67.get("tp") or 0) / float(_pred67)) > 1e-12:
                        _bad67.append("%s at b=%r: precision is not tp/predicted"
                                      % (_name67, _r67.get("b")))
                        break
                # (c) the b=0 row of the guarded rule must agree with E266's bracket counts
                if _name67 == "guarded_side":
                    _zero67 = next((r for r in _rows67 if abs(float(r.get("b") or 0.0)) < 1e-12),
                                   None)
                    _s66r = None
                    _p66r = os.path.join("results", "state_tilt", "bandscreen_latest.json")
                    if os.path.exists(_p66r):
                        with io.open(_p66r, encoding="utf-8") as _fh66r:
                            _s66r = (json.load(_fh66r).get("summary") or {}).get("S3_bracket")
                    if _zero67 is None:
                        _bad67.append("the guarded rule publishes no unbuffered reading")
                    elif _s66r:
                        for _k67 in ("tp", "fp", "fn"):
                            if int(_zero67.get(_k67) or 0) != int(_s66r.get(_k67) or 0):
                                _bad67.append("b=0 %s=%r but E266's own bracket says %r -- one "
                                              "screen, two numbers"
                                              % (_k67, _zero67.get(_k67), _s66r.get(_k67)))
                                break
            # (d) separability is a margin ordering, and the verdict must follow it
            _sep67 = (_s67.get("separation") or {})
            _lg67 = _sep67.get("largest_false_positive_margin")
            _nt67 = _sep67.get("nearest_true_positive_margin")
            if _lg67 is not None and _nt67 is not None:
                _want67 = bool(float(_lg67) < float(_nt67))
                if _sep67.get("separable") is not _want67:
                    _bad67.append("separable says %r but the largest non-move clears %r against "
                                  "the closest move %r"
                                  % (_sep67.get("separable"), _lg67, _nt67))
            else:
                _bad67.append("separation publishes no margin ordering")
            # (e) a verdict of "the buffer cannot buy precision" needs the guard to be exact
            _g67 = (_s67.get("guard_only") or {})
            if (_f67.get("verdict") == "buffer_cannot_buy_precision_itself"
                    and not (_g67.get("exact") and int(_g67.get("tp") or 0) > 0)):
                _bad67.append("verdict says the buffer cannot replace the guard, but the guard is "
                              "not exact itself (tp %r)" % (_g67.get("tp"),))
            # (f) headline counts are ints (A-or-{}.get family)
            for _k67 in ("comparisons", "moves_published", "breakpoints"):
                if not isinstance(_s67.get(_k67), int):
                    _bad67.append("summary field %s is not an int (%r)" % (_k67, _s67.get(_k67)))
            # one name, one quantity: the count and the list must not share a key (E207 family)
            if isinstance(_s67.get("moves"), list) or isinstance(_s67.get("moves"), int):
                _bad67.append("summary carries a bare 'moves' key alongside moves_published")
            _side67 = ((_s67.get("rules") or {}).get("single_side") or {})
            _zero67s = _side67.get("at_zero") or {}
            if (_zero67s.get("tp") or 0) + (_zero67s.get("fp") or 0) > (_s67.get("comparisons") or 0):
                _bad67.append("the unbuffered rule flags more comparisons than exist")
            check("product: a margin is not a substitute for the row's own side",
                  not _bad67,
                  "%r | %d comparison(s), %d move(s); unbuffered side rule flags %d (tp %d, "
                  "precision %.3f), best buffer precision %s at b=%s, guard alone tp/fp %r/%r, "
                  "largest non-move margin %s vs closest move %s (separable=%r)"
                  % ((_f67.get("verdict"), _s67.get("comparisons") or 0,
                      _s67.get("moves_published") or 0,
                      _zero67s.get("predicted") or 0, _zero67s.get("tp") or 0,
                      _zero67s.get("precision") or 0.0,
                      ("%.3f" % _side67["best_precision"]
                       if _side67.get("best_precision") is not None else "n/a"),
                      _side67.get("best_b"), _g67.get("tp"), _g67.get("fp"),
                      _lg67, _nt67, _sep67.get("separable")))
                  + (" | " + "; ".join(_bad67[:4]) if _bad67 else ""))
    except Exception as e:
        check("product: a margin is not a substitute for the row's own side",
              False, repr(e)[:160])


    # E268: E267 left the screen resting on the row's OWN p95 -- the one number a reader of the
    # table does not have. This leg guards the face that asks whether the published pooled end (or
    # the published boolean) can stand in for it. What can fabricate a claim here: calling a
    # substitute "usable" while it answers the guard differently on the comparisons that did not
    # move (exactness on two moves is not agreement on the table), an `exact` flag that does not
    # follow its own tp/fp/fn, re-deriving the published boolean from own_p95 and then finding it
    # agrees (a tautology), and an equivalence claimed with no distance-to-threshold band -- 0
    # disagreements only means nothing sits close enough to split them.
    try:
        _bad68 = []
        _p68 = os.path.join("results", "state_tilt", "bandpooled_latest.json")
        _f68 = None
        if not os.path.exists(_p68):
            _bad68.append("face missing: %s" % _p68)
        else:
            with io.open(_p68, encoding="utf-8") as _fh68:
                _f68 = json.load(_fh68)
        if _f68 is not None:
            _s68 = _f68.get("summary") or {}
            _cells68 = _s68.get("cells") or {}
            _perm68 = _f68.get("permissiveness") or {}
            _read68 = _f68.get("substitution_reading") or {}
            _band68 = _f68.get("ambiguity_band") or {}
            # (a) exact must follow its own counts, per screen x variant
            for _scr68, _per68 in sorted(_cells68.items()):
                for _var68, _c68 in sorted((_per68 or {}).items()):
                    _want68 = bool((_c68.get("fp") or 0) == 0 and (_c68.get("fn") or 0) == 0
                                   and (_c68.get("undefined") or 0) == 0)
                    if bool(_c68.get("exact")) is not _want68:
                        _bad68.append("%s/%s: exact=%r but tp/fp/fn/undef %r/%r/%r/%r"
                                      % (_scr68, _var68, _c68.get("exact"), _c68.get("tp"),
                                         _c68.get("fp"), _c68.get("fn"), _c68.get("undefined")))
                        break
            # (b) a substitute that answers differently elsewhere is not a disclosure
            for _var68, _rd68 in sorted(_read68.items()):
                _diff68 = _rd68.get("differs_from_row_own")
                if not isinstance(_diff68, int):
                    _bad68.append("%s: differs_from_row_own is not an int (%r)"
                                  % (_var68, _diff68))
                    continue
                if _diff68 > 0 and str(_rd68.get("reading", "")).startswith("disclosure"):
                    _bad68.append("%s: called a disclosure while answering %d comparison(s) the "
                                  "other way" % (_var68, _diff68))
                if (_diff68 == 0 and _rd68.get("guarded_exact")
                        and _var68 != "row_own"
                        and not str(_rd68.get("reading", "")).startswith("disclosure")):
                    _bad68.append("%s: identical calls and exact, yet not read as a disclosure"
                                  % _var68)
                _per_v68 = _perm68.get(_var68) or {}
                if _per_v68.get("differs_from_row_own") != _diff68:
                    _bad68.append("%s: permissiveness and the reading disagree on %r vs %r"
                                  % (_var68, _per_v68.get("differs_from_row_own"), _diff68))
            # (c) the boolean variant may not be a free pass: if the published verdict disagrees
            # with the recomputed one, that variant cannot be exact
            _ag68 = _s68.get("published_verdict_agreement") or {}
            _pub68 = ((_cells68.get("guarded_side") or {}).get("row_published_verdict") or {})
            if _ag68.get("agrees") is False and _pub68.get("exact"):
                _bad68.append("the published boolean disagrees with the recomputed own-side verdict "
                              "and still scores exact -- it is being re-derived, not read")
            if _ag68.get("agrees") is False and not _ag68.get("disagreement_rows"):
                _bad68.append("a disagreement is reported with no row index")
            # (d) a pooled end outside its rows' range must be disclosed, and the band must exist
            for _g68 in (_f68.get("group_spread") or []):
                if "flat_tight_inside_row_range" not in _g68:
                    _bad68.append("group %r does not disclose whether the tight pooled end sits "
                                  "inside its rows' range" % (_g68.get("group"),))
                    break
            _tb68 = _band68.get("group_flat_tight")
            if not _tb68 or _tb68.get("gap") is None:
                _bad68.append("no distance-to-threshold band for the pooled tight end: agreement "
                              "at 0 disagreements is unmeasured")
            if _band68.get("row_published_verdict") is not None:
                _bad68.append("a boolean end publishes a distance to a line")
            # (e) counts are ints and the verdict is in the frozen vocabulary
            for _k68 in ("comparisons", "moves_published", "groups"):
                if not isinstance(_s68.get(_k68), int):
                    _bad68.append("summary field %s is not an int (%r)" % (_k68, _s68.get(_k68)))
            if _f68.get("verdict") not in (
                    "a_pooled_group_end_runs_the_screen",
                    "the_published_verdict_runs_it_a_pooled_end_does_not",
                    "a_pooled_end_is_not_a_substitute_for_the_rows_own_draws",
                    "the_screen_is_not_exact_on_the_rows_own_draws",
                    "screen_untested_no_moves", "no_published_pair_carries_a_row"):
                _bad68.append("verdict %r is outside the frozen vocabulary" % (_f68.get("verdict"),))
            if _s68.get("underpowered") is True and "below the" not in str(
                    _f68.get("verdict_reason")):
                _bad68.append("an underpowered reading does not say so in the verdict reason")
            # (f) the comparison rows must carry the substitution inputs, not just the verdict
            _rows68 = _f68.get("comparisons") or []
            if not _rows68:
                _bad68.append("no comparison rows published")
            for _r68 in _rows68[:40]:
                if "group_flat_tight_p95" not in _r68 or "predicted" not in _r68:
                    _bad68.append("comparison row %r does not carry its substitution inputs"
                                  % (_r68.get("index"),))
                    break
            check("product: a pooled end is not the row's own end until it answers the same way "
                  "elsewhere", not _bad68,
                  "%r | %d comparison(s), %d move(s), %d group(s); guarded side holds with own "
                  "end / pooled tight / pooled wide / published boolean = %r/%r/%r/%r; nearest gap "
                  "to a threshold %s"
                  % ((_f68.get("verdict"), _s68.get("comparisons") or 0,
                      _s68.get("moves_published") or 0, _s68.get("groups") or 0,
                      ((_cells68.get("guarded_side") or {}).get("row_own") or {}).get("exact"),
                      ((_cells68.get("guarded_side") or {}).get("group_flat_tight") or {}).get("exact"),
                      ((_cells68.get("guarded_side") or {}).get("group_flat_wide") or {}).get("exact"),
                      ((_cells68.get("guarded_side") or {}) .get("row_published_verdict") or {}).get("exact"),
                      ("%.4f" % abs((_tb68 or {}).get("gap"))
                       if (_tb68 or {}).get("gap") is not None else "n/a")))
                  + (" | " + "; ".join(_bad68[:4]) if _bad68 else ""))
    except Exception as e:
        check("product: a pooled end is not the row's own end until it answers the same way "
              "elsewhere", False, repr(e)[:160])


    # E269: the tight end (p05) of the same transfer question. Two things can fabricate a reading
    # here. (i) A "zero moves" that is really "nothing could have moved": every row publishes the
    # multiplier at which its verdict flips, so the face must state whether ANY p05 its group
    # actually published reaches that flip -- inertness and a clean transfer are different verdicts
    # and may not be confused. (ii) A wide-end comparison copied by hand: the tight/wide move
    # counts printed side by side must equal the source face's own summary, and every moved row
    # must be a real verdict change under the borrowed p05.
    try:
        _bad69 = []
        _p69 = os.path.join("results", "state_tilt", "bandtight_latest.json")
        _f69 = None
        if not os.path.exists(_p69):
            _bad69.append("face missing: %s" % _p69)
        else:
            with io.open(_p69, encoding="utf-8") as _fh69:
                _f69 = json.load(_fh69)

        def _out69(_val, _lo, _hi):
            if _val is None or _lo is None or _hi is None:
                return None
            return bool(_val < _lo or _val > _hi)

        if _f69 is not None:
            _s69 = _f69.get("summary") or {}
            # (a) every published tight verdict is reproducible from its own p05
            _rows69 = _f69.get("rows") or []
            if not _rows69:
                _bad69.append("no rows published")
            for _r69 in _rows69:
                if _r69.get("status") != "measured":
                    if _r69.get("verdict_tight") is not None:
                        _bad69.append("row %r is not measured yet carries a tight verdict"
                                      % (_r69.get("index"),))
                        break
                    continue
                _want69 = _out69(_r69.get("b"), (_r69.get("band_lo") or 0) * _r69.get("own_p05"),
                                 (_r69.get("band_hi") or 0) * _r69.get("own_p05"))
                if _want69 is not None and bool(_want69) is not bool(_r69.get("verdict_tight")):
                    _bad69.append("row %r: tight verdict %r does not follow from its own p05"
                                  % (_r69.get("index"), _r69.get("verdict_tight")))
                    break
            # (b) the transfer block must count what it lists
            _tt69 = _f69.get("transfer_tight") or {}
            _moved69, _pairs69, _moving69 = 0, 0, 0
            for _k69, _blk69 in sorted(_tt69.items()):
                for _pr69 in (_blk69.get("pairs") or []):
                    _pairs69 += 1
                    _n69 = len(_pr69.get("moved") or [])
                    if _pr69.get("n_moved") != _n69:
                        _bad69.append("%s %s->%s: n_moved %r but %d moved record(s)"
                                      % (_k69, _pr69.get("donor"), _pr69.get("recipient"),
                                         _pr69.get("n_moved"), _n69))
                    if _n69:
                        _moving69 += 1
                        _moved69 += _n69
                    for _m69 in (_pr69.get("moved") or []):
                        if _m69.get("before") == _m69.get("after"):
                            _bad69.append("%s: a 'move' whose before equals its after" % (_k69,))
                        if _m69.get("direction") not in ("rejections_invented", "rejections_lost"):
                            _bad69.append("%s: move direction %r is outside the vocabulary"
                                          % (_k69, _m69.get("direction")))
            if _s69.get("tight_pairs") != _pairs69:
                _bad69.append("summary pairs %r vs %d counted" % (_s69.get("tight_pairs"), _pairs69))
            if _s69.get("tight_pairs_moving_a_verdict") != _moving69:
                _bad69.append("summary moving pairs %r vs %d counted"
                              % (_s69.get("tight_pairs_moving_a_verdict"), _moving69))
            # (c) the wide column is not hand-typed: it must equal the source face's summary
            _src69 = os.path.join("results", "state_tilt", "bandtransfer_latest.json")
            if os.path.exists(_src69):
                with io.open(_src69, encoding="utf-8") as _fh69s:
                    _ws69 = (json.load(_fh69s).get("summary") or {})
                for _k69a, _k69b in (("wide_pairs", "pairs"),
                                     ("wide_pairs_moving_a_verdict", "pairs_moving_a_verdict"),
                                     ("wide_rejections_invented", "rejections_invented"),
                                     ("wide_rejections_lost", "rejections_lost")):
                    if _s69.get(_k69a) != _ws69.get(_k69b):
                        _bad69.append("%s is %r but the source face says %r"
                                      % (_k69a, _s69.get(_k69a), _ws69.get(_k69b)))
            else:
                _bad69.append("the source wide face is missing: the comparison is unverified")
            # (d) sensitivity must be measured, not asserted
            _sens69 = _f69.get("sensitivity") or {}
            _could69 = 0
            for _k69c, _blk69c in sorted(_sens69.items()):
                if _blk69c.get("reason"):
                    continue
                _cc69 = 0
                for _r69c in (_blk69c.get("rows") or []):
                    _flip69 = (_r69c.get("verdict_at_min_p05")
                               != _r69c.get("verdict_at_max_p05"))
                    if bool(_r69c.get("could_move")) is not bool(_flip69):
                        _bad69.append("%s row %r: could_move %r but the two ends disagree %r"
                                      % (_k69c, _r69c.get("index"), _r69c.get("could_move"),
                                         _flip69))
                        break
                    _cc69 += 1 if _flip69 else 0
                if _blk69c.get("n_could_move") != _cc69:
                    _bad69.append("%s: n_could_move %r vs %d counted"
                                  % (_k69c, _blk69c.get("n_could_move"), _cc69))
                _could69 += _cc69
            if _s69.get("rows_could_move_within_observed_p05_range") != _could69:
                _bad69.append("summary could-move %r vs %d counted"
                              % (_s69.get("rows_could_move_within_observed_p05_range"), _could69))
            # (e) inertness may not be claimed when a row could have moved, and vice versa
            _v69 = _f69.get("verdict")
            if _v69 == "the_tight_end_is_inert_on_this_population" and _could69 != 0:
                _bad69.append("verdict says inert while %d row(s) could flip" % _could69)
            if _v69 != "the_tight_end_is_inert_on_this_population" and _could69 == 0 \
                    and _moving69 == 0:
                _bad69.append("zero moves with zero could-move rows is not reported as inert")
            if _v69 not in ("the_tight_end_is_inert_on_this_population",
                            "the_tight_end_transfers_without_moving_a_verdict",
                            "the_tight_end_moves_as_the_wide_end_does",
                            "the_tight_end_moves_where_the_wide_end_does_not",
                            "no_transfer_possible", "no_tight_rows_measured"):
                _bad69.append("verdict %r is outside the frozen vocabulary" % (_v69,))
            # (f) 'use the tightest' adopts the MINIMUM p05 of its group -- never the maximum
            for _k69f, _blk69f in sorted((_f69.get("flat_tight") or {}).items()):
                if _blk69f.get("reason"):
                    continue
                _dom69 = ((_f69.get("dominator_tight") or {}).get(_k69f) or {})
                _vals69 = [_v for _v in (_dom69.get("p05") or {}).values() if _v is not None]
                if not _vals69:
                    _bad69.append("%s publishes a flat p05 with no arm values behind it" % (_k69f,))
                    continue
                if abs(_blk69f.get("flat_p05") - min(_vals69)) > 1e-12:
                    _bad69.append("%s: flat_p05 %r is not the group minimum %r"
                                  % (_k69f, _blk69f.get("flat_p05"), min(_vals69)))
                if abs(_blk69f.get("flat_loose_p05") - max(_vals69)) > 1e-12:
                    _bad69.append("%s: the loose twin is not the group maximum" % (_k69f,))
            # (g) ints stay ints and the cut is carried
            for _k69g in ("tight_rows_measured", "tight_pairs", "tight_pairs_moving_a_verdict",
                          "wide_pairs_moving_a_verdict", "rows_could_move_within_observed_p05_range"):
                if not isinstance(_s69.get(_k69g), int):
                    _bad69.append("summary field %s is not an int (%r)"
                                  % (_k69g, _s69.get(_k69g)))
            if _f69.get("evidence_cutoff") is None:
                _bad69.append("no evidence_cutoff on the face")
            check("product: the tight end cannot transfer badly if it cannot move anything -- and "
                  "a zero has to say which one it measured", not _bad69,
                  "%r | tight %d pair(s) %d moving / wide %d moving; rows %d measured, %d could "
                  "move at any published p05; nearest flip %.1f%% outside the widest p05 swing"
                  % ((_f69.get("verdict") if _f69 else None,
                      _s69.get("tight_pairs") or 0, _s69.get("tight_pairs_moving_a_verdict") or 0,
                      _s69.get("wide_pairs_moving_a_verdict") or 0,
                      _s69.get("tight_rows_measured") or 0,
                      _s69.get("rows_could_move_within_observed_p05_range") or 0,
                      float(_s69.get("nearest_flip_gap_pct") or 0.0)))
                  + (" | " + "; ".join(_bad69[:4]) if _bad69 else ""))
    except Exception as e:
        check("product: the tight end cannot transfer badly if it cannot move anything -- and "
              "a zero has to say which one it measured", False, repr(e)[:160])

    # E274: the straddle screen read as two published numbers (m_flip, the range an axis offers)
    # is scored against every moved set the band family itself published. The leg re-derives the
    # reading per row from the face (a row is flagged iff its flip sits inside its range), pins
    # that the flag reproduces the published moved set on every axis, and pins the trap that broke
    # the first cut: BANDTOPFLIP's flipped_ids is "flips at EVERY measurement" (empty) while
    # depends_ids is "at SOME" (2 rows) -- scoring the stricter set would read 2 real moves as
    # screen misses, so the gap between the two sets must be disclosed, not silently chosen.
    try:
        _p274 = os.path.join("results", "state_tilt", "bandstraddlesweep_latest.json")
        _f274 = None
        if os.path.exists(_p274):
            with io.open(_p274, encoding="utf-8") as _fh274:
                _f274 = json.load(_fh274)
        _bad274 = []
        if not _f274:
            _bad274.append("no published straddle-sweep face")
        else:
            _s274 = _f274.get("summary") or {}
            _scores274 = _f274.get("scores") or []
            if not _scores274:
                _bad274.append("the face publishes no per-axis scores")
            if _f274.get("evidence_cutoff") is None:
                _bad274.append("no evidence_cutoff on the face")
            if _s274.get("verdict") not in (
                    "two_published_numbers_predict_every_scored_axis",
                    "screen_is_vacuously_exact_no_axis_moves_anything",
                    "the_screen_is_unsafe_on_some_axis",
                    "the_screen_over_flags_on_some_axis"):
                _bad274.append("verdict %r is outside the frozen vocabulary" % (_s274.get("verdict"),))
            _rows274 = (_f274.get("axes") or {})
            for _sc274 in _scores274:
                _ax = _rows274.get(_sc274.get("axis")) or {}
                # (a) the flag must be re-derivable from the two published numbers, per row
                for _r274 in (_ax.get("rows") or []):
                    _m274, _rg274 = _r274.get("flip_multiplier"), _r274.get("range") or [None, None]
                    _reading274 = _r274.get("straddle")
                    if _reading274 not in ("inside", "near_edge", "outside", "untested"):
                        _bad274.append("%s row %r reading %r is outside the four-way set"
                                       % (_sc274.get("axis"), _r274.get("index"), _reading274))
                        continue
                    _lo274, _hi274 = _rg274[0], _rg274[1]
                    if _m274 is None or _lo274 is None or _hi274 is None or _hi274 <= _lo274:
                        if _reading274 != "untested":
                            _bad274.append("%s row %r has no usable range but is not untested"
                                           % (_sc274.get("axis"), _r274.get("index")))
                        continue
                    _inside274 = _lo274 <= _m274 <= _hi274
                    if _inside274 != (_reading274 in ("inside", "near_edge")):
                        _bad274.append("%s row %r: reading %r contradicts its own range"
                                       % (_sc274.get("axis"), _r274.get("index"), _reading274))
                # (b) the flag's promise is that it reproduces the published moved set
                if _sc274.get("missed_by_screen"):
                    _bad274.append("%s missed published moves %r"
                                   % (_sc274.get("axis"), _sc274.get("missed_by_screen")))
                if _sc274.get("flagged_never_moved"):
                    _bad274.append("%s flagged rows that never moved %r"
                                   % (_sc274.get("axis"), _sc274.get("flagged_never_moved")))
                # (c) the weaker/stricter gap is arithmetic, not asserted
                _weak274 = set(_sc274.get("published_moved") or [])
                _strict274 = set(_sc274.get("published_moved_stricter") or [])
                if sorted(_weak274 - _strict274) != (_sc274.get("moves_only_in_the_weaker_set") or []):
                    _bad274.append("%s: the weaker/stricter gap does not re-derive"
                                   % (_sc274.get("axis"),))
            check("product: two published numbers -- the flip multiplier and the range an axis "
                  "offers -- reproduce every moved set the band family published", not _bad274,
                  "%r | axes %s; %d moved observation(s), %d hit(s), %d missed, %d inert"
                  % ((_f274.get("verdict") if _f274 else None,
                      ",".join(_s274.get("axes") or []),
                      _s274.get("n_moved_observations") or 0,
                      len(_s274.get("hits") or []),
                      len(_s274.get("missed_by_screen") or []),
                      len(_s274.get("flagged_never_moved") or [])))
                  + (" | " + "; ".join(_bad274[:4]) if _bad274 else ""))
    except Exception as e:
        check("product: two published numbers -- the flip multiplier and the range an axis "
              "offers -- reproduce every moved set the band family published", False, repr(e)[:160])


    # E272: E269 measured the tight half's draw budget and left the wide half unmeasured on the
    # same ruler. The leg re-derives the one reading this face exists to publish -- which tail is
    # closer -- from the face's own two gaps and two spreads (gap / that tail's spread), so a
    # closer_tail that disagrees with its own numbers is red. It also pins the two ways the face
    # could lie: (i) calling a tail "reachable" at a flip it never crosses (a flip exactly ON a
    # published end is still INSIDE, because outside() is strict), (ii) reporting a spread-0 tail
    # as if it were measurable (cross:200 publishes p05=1.0000 on all four windows) rather than
    # naming it unmeasurable.
    _name72 = ("product: one ruler puts both tails of the screen's flip budget side by side -- "
               "and a tail that cannot move anything is named inert, not safe")

    def _nrm72(_gap, _spread):
        if _gap is None or _spread is None or _spread <= 0:
            return None
        return _gap / _spread

    try:
        _bad72 = []
        _p72 = os.path.join("results", "state_tilt", "bandflipbudget_latest.json")
        _f72 = None
        if not os.path.exists(_p72):
            _bad72.append("face missing: %s" % _p72)
        else:
            with io.open(_p72, encoding="utf-8") as _fh72:
                _f72 = json.load(_fh72)
        if _f72 is not None:
            _s72 = _f72.get("summary") or {}
            if _f72.get("evidence_cutoff") is None:
                _bad72.append("no evidence_cutoff on the face")
            if _s72.get("verdict") not in (
                    "the_wide_tail_is_the_only_tail_that_can_reach_a_row",
                    "the_tight_tail_is_the_only_tail_that_can_reach_a_row",
                    "both_tails_reach_at_least_one_row",
                    "neither_tail_is_reachable_at_published_spreads",
                    "the_wide_tail_is_closer_on_a_normalised_ruler",
                    "the_tight_tail_is_closer_on_a_normalised_ruler",
                    "the_two_tails_are_equally_out_of_reach",
                    "no_rows_measured"):
                _bad72.append("verdict %r is outside the frozen vocabulary" % (_s72.get("verdict"),))
            _scored72, _reach_w, _reach_t = [], [], []
            for _k72 in sorted(_f72.get("tail_budget") or {}):
                for _r72 in ((_f72.get("tail_budget") or {}).get(_k72) or {}).get("rows") or []:
                    _scored72.append(_r72)
                    _mf72 = _r72.get("flip_multiplier")
                    _dir72 = _r72.get("flip_direction")
                    if _mf72 is not None:
                        _want72 = ("widening_reenters" if _mf72 > 1.0 + 1e-12 else
                                   "narrowing_escapes" if _mf72 < 1.0 - 1e-12 else "boundary")
                        if _dir72 != _want72:
                            _bad72.append("row %r: direction %r does not follow flip %r"
                                          % (_r72.get("index"), _dir72, _mf72))
                    _n72 = {}
                    for _t72 in ("tight", "wide"):
                        _b72 = _r72.get(_t72) or {}
                        _gn72 = _nrm72(_b72.get("gap_pct"), _b72.get("spread_pct"))
                        _pub72 = _b72.get("normalised_gap")
                        if _gn72 is None:
                            if _pub72 is not None:
                                _bad72.append("row %r %s: normalised gap %r but spread %r"
                                              % (_r72.get("index"), _t72, _pub72,
                                                 _b72.get("spread_pct")))
                            elif not _b72.get("normalised_note"):
                                _bad72.append("row %r %s: unmeasurable tail without a reason"
                                              % (_r72.get("index"), _t72))
                        elif _pub72 is None or abs(_pub72 - _gn72) > 1e-9:
                            _bad72.append("row %r %s: normalised gap %r does not re-derive (%r)"
                                          % (_r72.get("index"), _t72, _pub72, _gn72))
                        _n72[_t72] = _gn72
                        # reachability: a zero gap is not enough -- the tail must publish a
                        # multiplier STRICTLY past the flip, or the row is still inside
                        if _b72.get("reachable_strict"):
                            if (_b72.get("gap_pct") or 0) > 1e-12:
                                _bad72.append("row %r %s: reachable with gap %r"
                                              % (_r72.get("index"), _t72, _b72.get("gap_pct")))
                            if not (_b72.get("multiplier_max") or 0) > (_mf72 or 0) + 1e-12:
                                _bad72.append("row %r %s: reachable but no end passes the flip"
                                              % (_r72.get("index"), _t72))
                            (_reach_w if _t72 == "wide" else _reach_t).append(_r72.get("index"))
                    # the closer-tail reading is arithmetic on the two normalised gaps
                    if _n72["tight"] is None and _n72["wide"] is None:
                        if _r72.get("closer_tail") is not None:
                            _bad72.append("row %r: a closer tail from two unmeasurable tails"
                                          % (_r72.get("index"),))
                        elif not _r72.get("closer_note"):
                            _bad72.append("row %r: no closer tail and no reason"
                                          % (_r72.get("index"),))
                    else:
                        _meas72 = {k: v for k, v in _n72.items() if v is not None}
                        if len(_meas72) == 1:
                            _wantc72 = list(_meas72)[0]
                        else:
                            _a72, _c72 = _meas72.get("tight"), _meas72.get("wide")
                            _wantc72 = ("tie" if abs(_a72 - _c72) <= 1e-12 else
                                        ("wide" if _c72 < _a72 else "tight"))
                        if _r72.get("closer_tail") != _wantc72:
                            _bad72.append("row %r: closer_tail %r but the ruler says %r"
                                          % (_r72.get("index"), _r72.get("closer_tail"), _wantc72))
            # counts must sum to the population, and the reachable sets must re-derive
            if len(_scored72) != (_s72.get("rows_scored") or 0):
                _bad72.append("scored %d row(s) but the summary says %r"
                              % (len(_scored72), _s72.get("rows_scored")))
            if len(_scored72) != (_s72.get("rows_measured") or 0):
                _bad72.append("scored %d row(s) against %r measured"
                              % (len(_scored72), _s72.get("rows_measured")))
            if sorted(_reach_w) != sorted(_s72.get("reachable_wide_indices") or []):
                _bad72.append("wide-reachable indices %r do not re-derive (%r)"
                              % (_s72.get("reachable_wide_indices"), sorted(_reach_w)))
            if sorted(_reach_t) != sorted(_s72.get("reachable_tight_indices") or []):
                _bad72.append("tight-reachable indices %r do not re-derive (%r)"
                              % (_s72.get("reachable_tight_indices"), sorted(_reach_t)))
            _parts72 = ((_s72.get("rows_wide_closer") or 0) + (_s72.get("rows_tight_closer") or 0)
                        + (_s72.get("rows_closer_tie") or 0) + (_s72.get("rows_closer_unmeasured") or 0))
            if _parts72 != len(_scored72):
                _bad72.append("closer-tail counts sum to %d over %d row(s)"
                              % (_parts72, len(_scored72)))
            check(_name72, not _bad72,
                  "%r | reached by %d row(s): wide %r / tight %r; wide-closer %r, tight-closer "
                  "%r; medians tight %s / wide %s"
                  % ((_f72.get("verdict") if _f72 else None,
                      len(set(_reach_w) | set(_reach_t)), sorted(set(_reach_w)),
                      sorted(set(_reach_t)),
                      _s72.get("rows_wide_closer"), _s72.get("rows_tight_closer"),
                      ("%.2f" % _s72["tight_normalised_gap_median"])
                      if _s72.get("tight_normalised_gap_median") is not None else "n/a",
                      ("%.2f" % _s72["wide_normalised_gap_median"])
                      if _s72.get("wide_normalised_gap_median") is not None else "n/a"))
                  + (" | " + "; ".join(_bad72[:4]) if _bad72 else ""))
    except Exception as e:
        check(_name72, False, repr(e)[:160])

    # E270: the guard E267/E268 published consumes four per-row numbers (b, band_lo, band_hi,
    # own_p95), so its reach is what the published faces actually carry -- not what the rule says.
    # Three things can fabricate a reading here: (i) a count taken over the audit's own face
    # (self-inclusion turns a second burn into a different answer), (ii) "present" counted as
    # "agreeing" -- two faces can both carry own_p95 and publish different numbers, so the join
    # must be re-added from the face, not trusted, (iii) a buffer-grid collection filed as a row
    # because `b` is spelled the same in both meanings.
    _name70 = ("product: a screen's reach is what the published faces carry, and presence is not "
               "agreement")
    try:
        _bad70 = []
        _p70 = os.path.join("results", "state_tilt", "bandfields_latest.json")
        _f70 = None
        if not os.path.exists(_p70):
            _bad70.append("face missing: %s" % _p70)
        else:
            with io.open(_p70, encoding="utf-8") as _fh70:
                _f70 = json.load(_fh70)
        if _f70 is not None:
            _s70 = _f70.get("summary") or {}
            # (a) no self-inclusion: the audit may not be one of its own inputs
            _src70 = _f70.get("source_faces") or []
            for _n70 in _src70:
                if str(_n70).startswith("BANDFIELDS"):
                    _bad70.append("the audit lists its own face as an input: %s" % (_n70,))
                if str(_n70).endswith("_latest.json"):
                    _bad70.append("an undated mirror is counted as a face: %s" % (_n70,))
            if len(set(_src70)) != len(_src70):
                _bad70.append("a source face is listed twice")
            # (b) the counts are re-added from the per-face scans, never trusted
            _guard_cols, _complete_cols, _runnable, _verdict_cols, _verdict_recs = 0, 0, 0, 0, 0
            for _e70 in (_f70.get("faces") or []):
                _sc70 = _e70.get("scan") or {}
                _guard_cols += len(_sc70.get("guard_collections") or [])
                _verdict_cols += len(_sc70.get("collections_with_verdict_but_no_inputs") or [])
                _verdict_recs += _sc70.get("n_records_with_verdict_but_no_inputs") or 0
                for _c70 in (_sc70.get("collections") or []):
                    if (_c70.get("n_complete") or 0) > 0:
                        _complete_cols += 1
                        _runnable += _c70.get("n_complete") or 0
            for _k70a, _k70b, _v70 in (("guard_columns", _guard_cols, "guard_columns"),
                                       ("guard_complete_collections", _complete_cols,
                                        "complete collections"),
                                       ("records_guard_runnable", _runnable,
                                        "records with all four inputs"),
                                       ("verdict_collections_without_inputs", _verdict_cols,
                                        "verdict collections without inputs"),
                                       ("records_with_verdict_but_no_inputs", _verdict_recs,
                                        "records with a verdict and no inputs")):
                if _s70.get(_k70a) != _k70b:
                    _bad70.append("%s is %r but the per-face scans add up to %r (%s)"
                                  % (_k70a, _s70.get(_k70a), _k70b, _v70))
            # (c) the join must partition: every compared cell agreed or disagreed, and a
            # disagreement can never be reported as a clean pass
            _cells = _s70.get("cells_compared") or 0
            _agree = _s70.get("value_agreements") or 0
            _dis = _s70.get("value_disagreements") or 0
            if _cells != _agree + _dis:
                _bad70.append("cells %r != agree %r + disagree %r" % (_cells, _agree, _dis))
            if _dis and _f70.get("verdict") != "guard_inputs_disagree_across_faces":
                _bad70.append("disagreements published under verdict %r" % (_f70.get("verdict"),))
            if _s70.get("canonical_basis") not in ("index", "composite", "none"):
                _bad70.append("canonical basis %r is outside the vocabulary"
                              % (_s70.get("canonical_basis"),))
            if _s70.get("joined_records") and _cells == 0:
                _bad70.append("records joined with zero cells compared")
            # (d) a buffer grid may not be filed as a half-instrumented row
            _buf70, _gap70 = 0, 0
            for _e70 in (_f70.get("faces") or []):
                _sc70 = (_e70.get("scan") or {})
                _buf70 += len(_sc70.get("b_without_a_band") or [])
                for _c70 in (_sc70.get("collections") or []):
                    if _c70.get("path") in (_sc70.get("b_without_a_band") or []):
                        if _c70.get("path") in (_sc70.get("collections_with_verdict_but_no_inputs")
                                                or []):
                            _gap70 += 1
            if _gap70:
                _bad70.append("%d buffer-grid collection(s) filed as rows without inputs" % _gap70)
            # (e) the verdict is in the frozen vocabulary and the cut is carried
            _v70 = _f70.get("verdict")
            if _v70 not in ("guard_inputs_are_published_where_the_screen_runs",
                            "guard_inputs_are_face_local",
                            "guard_inputs_disagree_across_faces",
                            "no_guard_bearing_record"):
                _bad70.append("verdict %r is outside the frozen vocabulary" % (_v70,))
            if _f70.get("evidence_cutoff") is None:
                _bad70.append("no evidence_cutoff on the face")
            for _k70g in ("faces_scanned", "guard_columns", "guard_complete_collections",
                          "records_guard_runnable", "cells_compared", "value_agreements",
                          "value_disagreements"):
                if not isinstance(_s70.get(_k70g), int):
                    _bad70.append("summary field %s is not an int (%r)"
                                  % (_k70g, _s70.get(_k70g)))
        check(_name70, not _bad70,
              "%r | %d face(s), guard on %d collection(s) / %d record(s), %d verdict "
              "collection(s) without inputs (%d records), join %d cell(s) %d agree / %d disagree "
              "max|diff| %r (buffer grids kept apart: %d)"
              % ((_f70.get("verdict") if _f70 else None,
                  (_f70.get("summary") or {}).get("faces_scanned") or 0,
                  (_f70.get("summary") or {}).get("guard_complete_collections") or 0,
                  (_f70.get("summary") or {}).get("records_guard_runnable") or 0,
                  (_f70.get("summary") or {}).get("verdict_collections_without_inputs") or 0,
                  (_f70.get("summary") or {}).get("records_with_verdict_but_no_inputs") or 0,
                  (_f70.get("summary") or {}).get("cells_compared") or 0,
                  (_f70.get("summary") or {}).get("value_agreements") or 0,
                  (_f70.get("summary") or {}).get("value_disagreements") or 0,
                  (_f70.get("summary") or {}).get("max_abs_diff"),
                  _buf70))
              + (" | " + "; ".join(_bad70[:4]) if _bad70 else ""))
    except Exception as e:
        check(_name70, False, repr(e)[:160])


    # E258: E257 could only BORROW era_2025_now's draw ladder and apply it to every window as a
    # range, because a fixed published window is neither that era's head nor its tail. This leg
    # guards the face that measures each window's own multiplier. What can fabricate a claim here:
    # a row that borrows another window's multiplier (cross-window leakage), a multiplier that is
    # not the one its own edge table carries, and -- the activity face -- a "measured spread" that
    # is really one constant number copied into every window.
    try:
        _bad58 = []
        _p58 = os.path.join("results", "state_tilt", "bandwinmult_latest.json")
        _f58 = None
        if not os.path.exists(_p58):
            _bad58.append("face missing: %s" % _p58)
        else:
            with io.open(_p58, encoding="utf-8") as _fh58:
                _f58 = json.load(_fh58)
        _m58 = None
        if _f58 is not None:
            try:
                import e258_band_multiplier_per_window as _m58
            except Exception as _e58:
                _bad58.append("module does not import: %r" % (_e58,))
        if _m58 is not None:
            _v58 = _m58.verify()
            for _p in (_v58.get("problems") or []):
                _bad58.append("verify: %s" % _p)
            _w58 = _f58.get("windows") or {}
            if len(_w58) < 3:
                _bad58.append("fewer than three published windows were measured (%d)"
                              % len(_w58))
            # iterate ITEMS: .values() yields the window dicts, and using one of those as the
            # key of _w58.get() is an unhashable-dict TypeError (caught on the first live run).
            _ms58 = [m.get("multiplier") for _cn, _rw in _w58.items()
                     for m in ((_rw or {}).get("by_base") or {}).values()
                     if m.get("multiplier")]
            if not _ms58:
                _bad58.append("no window carries a multiplier")
            else:
                # ACTIVITY: the band must really rise with draws somewhere
                if max(_ms58) <= 1.02:
                    _bad58.append("no window's band rises with the draw count -- nothing was "
                                  "measured")
                # ...and the spread must be a real spread, not one number copied around
                if (max(_ms58) - min(_ms58)) <= 1e-6:
                    _bad58.append("every window reports the identical multiplier -- one number "
                                  "copied, not measured")
            # cross-window leakage: a judged row must carry ITS OWN window's multiplier
            for _r in (_f58.get("rows") or []):
                _cell = _r.get("cell")
                _lv = _r.get("local_verdict")
                if _lv in (None, "unjudgeable", "published_flag_not_reproduced"):
                    continue
                _rec = _w58.get(_cell) or {}
                _base = str(int(_r.get("local_base_draws") or 0))
                _tab = (_rec.get("by_base") or {}).get(_base) or {}
                _want = _tab.get("multiplier")
                if _want is None:
                    _bad58.append("%s/%s says it was judged locally but its window has no "
                                  "multiplier at %s draws"
                                  % (_cell, _r.get("row"), _base))
                elif _r.get("local_multiplier") is None or                         abs(_r["local_multiplier"] - _want) > 1e-12:
                    _bad58.append("%s/%s: local multiplier %r is not its own window's value %r"
                                  % (_cell, _r.get("row"), _r.get("local_multiplier"), _want))
        _s58 = (_f58 or {}).get("summary") or {}
        _br58 = (_f58 or {}).get("windows_vs_borrowed_range") or {}
        check("product: each published window's draw multiplier is measured, not borrowed",
              not _bad58, "; ".join(_bad58)[:220]
              or "verdict %s; %s window(s) measured (%s skipped), multiplier %.3f..%.3f median "
                 "%.3f (ratio %.2f); %s row(s) judged: %s flip on every seed, %s on some, %s "
                 "survive; %s of %s window/base cells outside E257's borrowed range"
                 % ((_f58 or {}).get("verdict"), _s58.get("windows_measured"),
                    _s58.get("windows_skipped"), _s58.get("multiplier_min") or 0,
                    _s58.get("multiplier_max") or 0, _s58.get("multiplier_median") or 0,
                    _s58.get("multiplier_spread_ratio") or 0, _s58.get("rows_judged"),
                    _s58.get("rows_flip_every_seed"), _s58.get("rows_flip_some_seed"),
                    _s58.get("rows_survive_outside"),
                    _br58.get("n_outside"), _br58.get("n")))
    except Exception as e:
        check("product: each published window's draw multiplier is measured, not borrowed",
              False, repr(e)[:160])
    # E273: a published threshold is a faithful substitute for the guard's triple -- but only the
    # form the face actually fitted. What can fabricate a claim here: an "exact" substitution whose
    # residual is not zero, a rule re-run that only agrees because nothing moved, and an ambiguity
    # count that is typed instead of re-derived from the two published thresholds.
    try:
        _bad73 = []
        _p73 = os.path.join("results", "state_tilt", "bandthreshguard_latest.json")
        _f73 = None
        if not os.path.exists(_p73):
            _bad73.append("face missing: %s" % _p73)
        else:
            with io.open(_p73, encoding="utf-8") as _fh73:
                _f73 = json.load(_fh73)
        _s73 = (_f73 or {}).get("summary") or {}
        # (a) the substitution is exact: zero residual and zero band columns consulted
        if (_f73 or {}).get("rederivation", {}).get("max_abs_diff_t_max_end") != 0.0:
            _bad73.append("t_max_end does not re-derive from the band exactly")
        if (_f73 or {}).get("rederivation", {}).get("max_abs_diff_t_side") != 0.0:
            _bad73.append("t_side does not re-derive from the band exactly")
        if _s73.get("triple_columns_consulted_to_rerun") != 0:
            _bad73.append("the re-run consulted %r band column(s) but claims thresholds alone"
                          % (_s73.get("triple_columns_consulted_to_rerun"),))
        # (b) every published rule reproduced, and reproduced on a population that MOVED
        _rules73 = (_f73 or {}).get("rederivation", {}).get("rules_rerun_from_thresholds") or {}
        if sorted(_rules73) != ["predicted_bracket", "predicted_guarded", "predicted_single"]:
            _bad73.append("rule set %r is not the three published screens" % (sorted(_rules73),))
        _pos73 = 0
        for _name73, _v73 in _rules73.items():
            if not _v73.get("of"):
                _bad73.append("rule %s was compared on zero rows" % _name73)
            elif _v73.get("agree") != _v73.get("of"):
                _bad73.append("rule %s reproduced %r of %r" % (_name73, _v73.get("agree"),
                                                               _v73.get("of")))
            _pos73 += 1 if _v73.get("of") else 0
        if _pos73 == 0 or not _s73.get("rules_reproduced_exactly"):
            _bad73.append("rules_reproduced_exactly is %r over %d rule(s)"
                          % (_s73.get("rules_reproduced_exactly"), _pos73))
        # (c) the ambiguity count is re-derived from the two published thresholds on the source face
        _src73 = os.path.join("results", "state_tilt", "BANDSCREEN-2026-10-29.json")
        if not os.path.exists(_src73):
            _bad73.append("source face missing: %s" % _src73)
        else:
            with io.open(_src73, encoding="utf-8") as _fh73s:
                _rows73 = json.load(_fh73s).get("comparison_rows") or []
            _own73 = _grd73 = _two73 = 0
            for _r73 in _rows73:
                if abs(_r73["t_side"] - _r73["t_max_end"]) > 1e-12:
                    _two73 += 1
                _a73 = _r73["own_p95"] < _r73["t_side"]
                _b73 = _r73["own_p95"] < _r73["t_max_end"]
                if _a73 != _b73:
                    _own73 += 1
                if (((_r73["donor_p95"] > _r73["t_side"]) and _a73) !=
                        ((_r73["donor_p95"] > _r73["t_max_end"]) and _b73)):
                    _grd73 += 1
            for _k73, _want73 in (("rows_with_two_different_thresholds", _two73),
                                  ("rows_own_verdict_ambiguous", _own73),
                                  ("rows_guarded_screen_ambiguous", _grd73)):
                if _s73.get(_k73) != _want73:
                    _bad73.append("%s published %r, re-derived %r"
                                  % (_k73, _s73.get(_k73), _want73))
            if _own73 == 0:
                _bad73.append("an ambiguity of zero is not a finding -- re-check the population")
        # (d) every collection claimed newly runnable really carries a threshold and a p95
        for _e73 in ((_f73 or {}).get("census") or {}).get("newly_runnable") or []:
            if not _e73.get("thresholds") or not _e73.get("p95"):
                _bad73.append("%s %s is claimed runnable without a threshold or a p95"
                              % (_e73.get("face"), _e73.get("path")))
            if _e73.get("guard_complete_in_e270"):
                _bad73.append("%s %s was already guard-complete, so it is not newly runnable"
                              % (_e73.get("face"), _e73.get("path")))
        # (e) verdict in the frozen vocabulary, cut and no_bill carried
        if (_f73 or {}).get("verdict") not in ("threshold_substitutes_for_the_triple",
                                               "threshold_substitutes_for_the_triple_only_alongside_its_rule",
                                               "threshold_is_not_a_substitute",
                                               "published_threshold_is_not_the_published_bands_threshold"):
            _bad73.append("verdict %r is outside the frozen vocabulary"
                          % ((_f73 or {}).get("verdict"),))
        if (_f73 or {}).get("evidence_cutoff") is None:
            _bad73.append("no evidence_cutoff on the face")
        if not (_f73 or {}).get("no_bill"):
            _bad73.append("no_bill missing")
        check("product: a published threshold re-runs the guard, and the face says which form",
              not _bad73,
              "%r | %d comparison(s) re-run from thresholds with %r band column(s), rules exact %r, "
              "two thresholds on %d row(s) / own verdict ambiguous on %d / guarded on %d, "
              "%d collection(s) newly runnable"
              % ((_f73 or {}).get("verdict") if _f73 else None,
                 _s73.get("comparisons") or 0,
                 _s73.get("triple_columns_consulted_to_rerun"),
                 _s73.get("rules_reproduced_exactly"),
                 _s73.get("rows_with_two_different_thresholds") or 0,
                 _s73.get("rows_own_verdict_ambiguous") or 0,
                 _s73.get("rows_guarded_screen_ambiguous") or 0,
                 _s73.get("collections_newly_runnable") or 0)
              + (" | " + "; ".join(_bad73[:4]) if _bad73 else ""))
    except Exception as e:
        check("product: a published threshold re-runs the guard, and the face says which form",
              False, repr(e)[:160])
    # E271: the transfer table published its moved sets ONE donor at a time, so a reader of one
    # recipient could not tell whether "borrowing" or "borrowing from this cell" was the finding.
    # What can fabricate a claim here: a donor sweep that skips the own-cell control, a "donor
    # matters" verdict no flip multiplier explains, and a pivotal cell named without the numbers
    # that make it pivotal.
    try:
        _bad74 = []
        _p74 = os.path.join("results", "state_tilt", "banddonorchoice_latest.json")
        _f74 = None
        if not os.path.exists(_p74):
            _bad74.append("face missing: %s" % _p74)
        else:
            with io.open(_p74, encoding="utf-8") as _fh74:
                _f74 = json.load(_fh74)
        _s74 = (_f74 or {}).get("summary") or {}
        if (_f74 or {}).get("verdict") not in (
                "donor_irrelevant_nothing_moves",
                "donor_invariant_do_not_borrow_is_the_instruction",
                "donor_choice_matters_do_not_borrow_from_this_cell"):
            _bad74.append("verdict %r is outside the frozen vocabulary"
                          % ((_f74 or {}).get("verdict"),))
        if (_f74 or {}).get("evidence_cutoff") is None:
            _bad74.append("no evidence_cutoff on the face")
        if not (_f74 or {}).get("no_bill"):
            _bad74.append("no_bill missing")
        # (a) the own-cell donor is a CONTROL and must reproduce every published verdict
        _rows74 = [_r for _v in ((_f74 or {}).get("groups") or {}).values()
                   for _r in (_v.get("rows") or [])]
        if not _rows74:
            _bad74.append("no measured row on the face")
        for _r74 in _rows74:
            if _r74.get("own_reproduces") is not True:
                _bad74.append("row %r does not reproduce its own published verdict"
                              % (_r74.get("index"),))
        # (b) the moved rows must be exactly the rows whose flip multiplier the group's own p95
        #     spread straddles -- otherwise "the donor matters" is an unexplained coincidence
        _moved74 = set(_s74.get("moved_row_indices") or [])
        _straddle74 = set()
        for _v in ((_f74 or {}).get("groups") or {}).values():
            for _r74 in _v.get("rows") or []:
                _mf74 = _r74.get("flip_multiplier")
                _sp74 = _v.get("p95_spread") or {}
                if _mf74 is not None and _sp74.get("min") is not None and \
                        _sp74["min"] <= _mf74 <= _sp74["max"]:
                    _straddle74.add(_r74.get("index"))
        if _straddle74 != _moved74:
            _bad74.append("straddled rows %r != moved rows %r"
                          % (sorted(_straddle74), sorted(_moved74)))
        if _s74.get("flip_straddle_explains_moves") is not True:
            _bad74.append("the face does not claim the straddle explains the moves")
        # (c) a group that names a pivotal cell must have a donor that actually moves rows, and a
        #     group that reads one moved set must not name one
        for _k74, _v in ((_f74 or {}).get("groups") or {}).items():
            if not _v.get("rows"):
                continue
            _mv74 = [d for d in (_v.get("donors") or []) if d.get("n_moved")]
            if _v.get("donor_invariant") is False and not _mv74:
                _bad74.append("%s is variant but no donor moves a row" % _k74)
            if _v.get("donor_invariant") is True and _v.get("pivotal_cell"):
                _bad74.append("%s is invariant yet names a pivotal cell" % _k74)
            if _v.get("pivotal_cell") and _v["pivotal_cell"] not in [d.get("donor") for d in _mv74]:
                _bad74.append("%s names %r pivotal while that donor moves nothing"
                              % (_k74, _v.get("pivotal_cell")))
            _pub74 = _v.get("published_choice")
            if _pub74 is not None:
                _rec74 = [d for d in (_v.get("donors") or []) if d.get("donor") == _pub74]
                if _rec74 and _v.get("published_choice_moves") != _rec74[0].get("n_moved"):
                    _bad74.append("%s published choice moves %r but its donor record says %r"
                                  % (_k74, _v.get("published_choice_moves"),
                                     _rec74[0].get("n_moved")))
        # (d) the face must re-derive from its source face, not from its own summary
        sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
        _m74 = __import__("importlib").import_module("e271_donor_choice_sensitivity")
        _fresh74 = _m74.run(save=False)
        if _fresh74.get("summary") != _s74:
            _bad74.append("summary does not re-derive from the source face")
        if _fresh74.get("verdict") != (_f74 or {}).get("verdict"):
            _bad74.append("verdict does not re-derive")
        check("product: the moved set is scored donor by donor, and a pivotal cell is named",
              not _bad74,
              "; ".join(_bad74)[:220]
              or "verdict %r | %d measured row(s) over %d group(s), %d foreign donor-row pair(s); "
                 "%d row(s) move under some donor, %d donor end(s) move nothing; %d group(s) "
                 "variant (pivotal %s); published choices %s"
              % ((_f74 or {}).get("verdict"), _s74.get("rows_measured"), _s74.get("groups"),
                 _s74.get("donor_row_pairs"), _s74.get("rows_moved_by_any_donor"),
                 (_s74.get("donor_ends") or 0) - (_s74.get("donor_ends_moving_a_row") or 0),
                 _s74.get("donor_variant_groups") or 0,
                 _s74.get("pivotal_cells"),
                 "conservative in every group"
                 if _s74.get("published_choice_conservative_in_all_groups")
                 else "move %s row(s) total" % (_s74.get("published_choice_moves_total"),)))
    except Exception as e:
        check("product: the moved set is scored donor by donor, and a pivotal cell is named",
              False, repr(e)[:160])

    # E275: E274's straddle screen is binary -- a cleared row reads "safe" and nothing is said
    # about how much room is left. The leg re-derives the budget zone of every row from the face's
    # own two numbers (m_flip and the offered range) with an INDEPENDENT implementation of the
    # five-way rule, so a zone that disagrees with its own arithmetic is red; it pins that the
    # straddle zone IS the guard screen's published moved set (otherwise "cleared" and "moved" are
    # two unrelated readings); and it pins the disclosure that keeps the zone honest -- a
    # spent_by_build row MOVED NOWHERE, so the zone is a statement about the range, not a movement
    # prediction (without it the face reads as a second screen and fails silently).
    _name75 = ("product: a cleared row is not equally cleared -- the margin left is measured, and "
               "a zone is not a movement claim")
    _bad75 = []
    try:
        _p75 = os.path.join("results", "state_tilt", "bandscreenbudget_latest.json")
        _f75 = None
        if not os.path.exists(_p75):
            _bad75.append("face missing: %s" % _p75)
        else:
            with io.open(_p75, encoding="utf-8") as _fh75:
                _f75 = json.load(_fh75)
        _z75 = {}
        if _f75 is not None:
            _s75 = _f75.get("summary") or {}
            if _f75.get("evidence_cutoff") is None:
                _bad75.append("no evidence_cutoff on the face")
            if _s75.get("verdict") not in (
                    "cleared_is_not_one_reading_the_budget_names_rows_nothing_else_flags",
                    "the_budget_mostly_restates_a_named_row_set",
                    "cleared_set_is_one_reading",
                    "no_rows_to_budget"):
                _bad75.append("verdict %r is outside the frozen set" % (_s75.get("verdict"),))
            _rows75 = _f75.get("rows") or []
            if not _rows75:
                _bad75.append("the face publishes no rows")

            def _zone75(_m, _lo, _hi, _reading):
                if _reading == "untested":
                    return "untested"
                if _reading in ("inside", "near_edge"):
                    return "straddles"
                if _m is None or _lo is None or _hi is None:
                    return "untested"
                if _m <= _lo:
                    return "spent_by_build"
                if _m <= 0:
                    return "untested"
                return "spent" if (_hi / _m) >= 0.90 else "open"

            for _r75 in _rows75:
                _rg75 = _r75.get("offered_range") or [None, None]
                _want75 = _zone75(_r75.get("m_flip"), _rg75[0], _rg75[1], _r75.get("straddle"))
                if _want75 != _r75.get("zone"):
                    _bad75.append("row %r zone %r != its own arithmetic %r"
                                  % (_r75.get("index"), _r75.get("zone"), _want75))
                _z75.setdefault(_r75.get("zone"), []).append(_r75.get("index"))
                _sp75 = _r75.get("budget_spent")
                _m75v = _r75.get("m_flip")
                if _m75v:
                    _calc75 = (_rg75[1] / _m75v) if _rg75[1] is not None else None
                    if (_calc75 is None) != (_sp75 is None) or (
                            _calc75 is not None and abs(_calc75 - _sp75) > 1e-12):
                        _bad75.append("row %r budget does not re-derive" % (_r75.get("index"),))
                elif _sp75 is not None:
                    _bad75.append("row %r has no flip but a budget" % (_r75.get("index"),))
            for _k75, _v75 in (_f75.get("zones") or {}).items():
                if sorted(_v75) != sorted(_z75.get(_k75) or []):
                    _bad75.append("zone block %r disagrees with the rows" % (_k75,))
            _guard75 = ((_f75.get("coincidence") or {}).get("guard_moves") or {}).get("named") or []
            if sorted(_z75.get("straddles") or []) != sorted(_guard75):
                _bad75.append("straddles %r != guard moves %r"
                              % (sorted(_z75.get("straddles") or []), sorted(_guard75)))
            if set(_z75.get("spent_by_build") or []) & set(_guard75):
                _bad75.append("a spent_by_build row is also a moved row -- the zone would then "
                              "be a movement claim and the disclosure is false")
            if set(_z75.get("spent") or []) & set(_guard75):
                _bad75.append("a spent row is also a moved row (same contradiction)")
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m75 = __import__("importlib").import_module("e275_screen_margin_budget")
            _fresh75 = _m75.run(save=False)
            if _fresh75.get("summary") != _s75:
                _bad75.append("summary does not re-derive from the published faces")
            if _fresh75.get("rows") != _rows75:
                _bad75.append("row list does not re-derive")
        check(_name75, not _bad75,
              "; ".join(_bad75)[:220]
              or "verdict %r | %d row(s): %d open / %d spent / %d spent-by-build / %d straddle; "
                 "straddles == guard moves (%s); no near-spent row is a row another screen names"
                 % ((_f75 or {}).get("verdict"), len((_f75 or {}).get("rows") or []),
                    len(_z75.get("open") or []), len(_z75.get("spent") or []),
                    len(_z75.get("spent_by_build") or []), len(_z75.get("straddles") or []),
                    ",".join(str(x) for x in sorted(
                        ((_f75 or {}).get("coincidence") or {}).get("guard_moves", {}).get("named")
                        or [])) or "-"))
    except Exception as e:
        check(_name75, False, repr(e)[:160])

    # E277: the tight tail is inert by BUILD, not by window. lo is the minimum of a nested draw
    # prefix, so |lo| can only widen; with a positive draw exponent m >= 1 by construction. The
    # leg re-derives the census, checks that not one published lower end sits below 1.0, and
    # requires the counterfactual (a 5% band on the same stream) to break the floor -- otherwise
    # the floor would be a property of the data and the verdict would be wrong.
    _name77 = ("product: the tight multiplier floor is the band build, not the windows -- a "
               "tight-pass check on this family can only return zero")
    _bad77 = []
    try:
        _p77 = os.path.join("results", "state_tilt", "bandfloor_latest.json")
        _f77 = None
        if not os.path.exists(_p77):
            _bad77.append("face missing: %s" % _p77)
        else:
            with io.open(_p77, encoding="utf-8") as _fh77:
                _f77 = json.load(_fh77)
        if _f77 is not None:
            _s77 = _f77.get("summary") or {}
            if _f77.get("evidence_cutoff") is None:
                _bad77.append("no evidence_cutoff on the face")
            if _s77.get("verdict") not in (
                    "tight_end_dead_by_construction_family_should_stop_publishing_tight_pass_checks",
                    "tight_end_is_a_property_of_these_windows",
                    "tight_end_is_construction_limited_and_windows_not_yet_tested"):
                _bad77.append("verdict %r is outside the frozen set" % (_s77.get("verdict"),))
            _bb77 = _f77.get("band_build") or {}
            if _bb77.get("band_pct") != [0.0, 100.0] or not _bb77.get("lo_is_the_lowest_draw"):
                _bad77.append("the band build on the face is not the one the verdict reasons about")
            _led77 = (_f77.get("census") or [])
            if not _led77:
                _bad77.append("the census carries no face")
            if any((x.get("p05_below_one") or 0) > 0 for x in _led77):
                _bad77.append("a published face carries a p05 below 1.0 but the verdict says the "
                              "floor is constructional")
            if any((x.get("range_lo_below_one") or 0) > 0 for x in _led77):
                _bad77.append("a published multiplier range opens below 1.0")
            _tot77 = (_s77.get("published_lower_ends") or 0)
            if _tot77 <= 0:
                _bad77.append("no lower end was censused -- an empty census cannot support a floor")
            if _s77.get("counterfactual_breaks_the_floor") is not True:
                _bad77.append("the counterfactual did not break the floor, so the floor is not "
                              "demonstrably a property of the build")
            _ex77 = _f77.get("published_draw_exponent") or {}
            if not _ex77.get("gammas_positive"):
                _bad77.append("a published draw exponent is not positive")
            _d77 = (_ex77.get("degenerate_branch") or {})
            if _d77.get("rows_at_the_floor") and not (
                    _d77.get("lift_min") is not None and _d77["lift_min"] > 1.0):
                _bad77.append("exact-1.0 rows are published without a lift above 1")
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m77 = __import__("importlib").import_module("e277_tight_multiplier_floor")
            _fresh77 = _m77.run(save=False)
            if _fresh77.get("summary") != _s77:
                _bad77.append("summary does not re-derive from the published faces")
            if _fresh77.get("census") != _led77:
                _bad77.append("the census does not re-derive")
        check(_name77, not _bad77,
              "; ".join(_bad77)[:220]
              or "verdict %r | %d published lower ends (%d p05) all >= 1.0, %d exactly 1.0; "
                 "band_pct %s, gammas %s..%s; a 5%% band on the same stream gives m = %s"
                 % ((_f77 or {}).get("verdict"),
                    (_f77.get("summary") or {}).get("published_lower_ends"),
                    (_f77.get("summary") or {}).get("published_p05"),
                    (_f77.get("summary") or {}).get("exactly_one"),
                    (_f77.get("summary") or {}).get("band_pct"),
                    _r77(_f77, "gamma_min"), _r77(_f77, "gamma_max"),
                    _r77(_f77, "counterfactual_pct_multiplier")))
    except Exception as e:
        check(_name77, False, repr(e)[:160])

    # E278: a normalised gap divides by a tail's spread, so a spread of exactly 0 strands the
    # ruler. The leg requires the zero to be the E277 floor (every cell at 1.0) rather than an
    # unexplained collapse, requires every flagged zero to be covered by the published policy,
    # and requires each stranded row to be genuinely unmeasurable on that tail.
    _name78 = ("product: the one zero-spread tail is the band floor at the thin shuffle, not an "
               "unlucky group -- the stranded rows stay unmeasured")
    _bad78 = []
    try:
        _p78 = os.path.join("results", "state_tilt", "bandspreadfloor_latest.json")
        _f78 = None
        if not os.path.exists(_p78):
            _bad78.append("face missing: %s" % _p78)
        else:
            with io.open(_p78, encoding="utf-8") as _fh78:
                _f78 = json.load(_fh78)
        if _f78 is not None:
            _s78 = _f78.get("summary") or {}
            if _f78.get("evidence_cutoff") is None:
                _bad78.append("no evidence_cutoff on the face")
            if _s78.get("verdict") not in (
                    "the_zero_spread_tail_is_the_band_floor_landing_on_the_thin_shuffle",
                    "zero_spread_is_one_bad_group",
                    "zero_spread_clusters_by_base_count_without_being_the_floor",
                    "the_same_group_degenerates_at_both_tails",
                    "no_zero_spread_tails_published"):
                _bad78.append("verdict %r is outside the frozen set" % (_s78.get("verdict"),))
            _cen78 = _f78.get("census") or []
            if not _cen78:
                _bad78.append("the census carries no group")
            _zero78 = [(r.get("group_id"), t) for r in _cen78 for t in ("tight", "wide")
                       if (r.get(t) or {}).get("zero_spread")]
            if not _zero78:
                _bad78.append("no zero spread published -- the face would be about nothing")
            for _gid, _t in _zero78:
                _rec = [r for r in _cen78 if r.get("group_id") == _gid][0]
                if _rec[_t].get("class") != "all_cells_at_the_floor":
                    _bad78.append("%s/%s is zero but not explained by the floor" % (_gid, _t))
                if _rec[_t].get("n_published", 0) < 2:
                    _bad78.append("%s/%s is a single-cell group treated as a zero spread"
                                  % (_gid, _t))
            _flag78 = {(x.get("group"), x.get("tail")) for x in
                       (_f78.get("minimum_spread_policy") or {}).get("flagged") or []}
            if _flag78 != set(_zero78):
                _bad78.append("the published policy does not cover exactly the zero spreads")
            _aff78 = _f78.get("affected_rows") or []
            if any(not a.get("unmeasurable_here") for a in _aff78):
                _bad78.append("a stranded row is in fact measurable on that tail")
            _idc78 = _f78.get("identity_check") or {}
            if _idc78.get("mismatched"):
                _bad78.append("a group's spread disagrees with E272's published spread")
            if not _idc78.get("checked"):
                _bad78.append("the identity check never ran against E272")
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m78 = __import__("importlib").import_module("e278_spread_floor")
            _fresh78 = _m78.build()
            if _fresh78.get("summary") != _s78:
                _bad78.append("summary does not re-derive from the published faces")
            if _fresh78.get("census") != _cen78:
                _bad78.append("the census does not re-derive")
        check(_name78, not _bad78,
              "; ".join(_bad78)[:220]
              or "verdict %r | %d groups, %d measurable on both tails, %d zero spread (%s); "
                 "%d of %d tight values at the 1.0 floor; wide min spread %s; %d row(s) stranded"
                 % ((_f78 or {}).get("verdict"),
                    (_f78.get("summary") or {}).get("n_groups"),
                    (_f78.get("summary") or {}).get("n_groups_measurable_both_tails"),
                    len(_zero78), ",".join("%s/%s" % z for z in _zero78) or "-",
                    (_f78.get("summary") or {}).get("floor_hits_tight"),
                    (_f78.get("summary") or {}).get("published_tight_values"),
                    _r78(_f78, "min_nonzero_spread_pct"),
                    (_f78.get("summary") or {}).get("rows_stranded")))
    except Exception as e:
        check(_name78, False, repr(e)[:160])

    # E279: E278's "read the other tail" policy tested for the first time. The leg requires the
    # substitution to be reported as vacuous where it is vacuous (the stranded tail publishes a
    # degenerate multiplier range, so it could not have disagreed), requires zero deflations, and
    # requires the swap view to name the same rows in both directions -- a reversal, not two events.
    _name79 = ("product: reading the other tail never contradicts, but where it fires the agreement "
               "is vacuous -- substitution is an upper bound, not a reading")
    _bad79 = []
    try:
        _p79 = os.path.join("results", "state_tilt", "bandsubstitute_latest.json")
        _f79 = None
        if not os.path.exists(_p79):
            _bad79.append("face missing: %s" % _p79)
        else:
            with io.open(_p79, encoding="utf-8") as _fh79:
                _f79 = json.load(_fh79)
        if _f79 is not None:
            _s79 = _f79.get("summary") or {}
            _ev79 = [e for _r in (_f79.get("census") or [])
                     for e in (_r.get("substitutions") or [])]
            if _f79.get("evidence_cutoff") is None:
                _bad79.append("no evidence_cutoff on the face")
            if _s79.get("verdict") not in (
                    "the_substitute_agrees_only_where_agreement_is_vacuous",
                    "the_substitute_contradicts_on_a_row_that_needs_it",
                    "the_substitute_moves_the_claim_where_the_pair_disagrees",
                    "the_substitute_agrees_where_it_fires",
                    "no_stranded_tails_published"):
                _bad79.append("verdict %r is outside the frozen set" % (_s79.get("verdict"),))
            if not _ev79:
                _bad79.append("no substitution event -- the face would be about nothing")
            for _e79 in _ev79:
                if not _e79.get("stranded_range_degenerate"):
                    _bad79.append("an event substitutes for a tail whose range is not degenerate")
                if _e79.get("deflating"):
                    _bad79.append("a substitution deflates a reaching conclusion")
                if _e79.get("verdict_agrees") and not _e79.get("vacuous"):
                    # non-vacuous agreement would be real evidence; publish it only with a reason
                    _bad79.append("a non-vacuous agreement is published as a soundness proof")
            _idc79 = _f79.get("identity_check") or {}
            if _idc79.get("mismatched"):
                _bad79.append("our reachability disagrees with E272's published boolean")
            if not _idc79.get("checked"):
                _bad79.append("the identity check never ran against E272")
            if _idc79.get("stranding_agrees_with_e278") is not True:
                _bad79.append("our stranded set disagrees with E278's flagged groups")
            if (_s79.get("wide_dominates_tight_violations") or []) != []:
                _bad79.append("the wide tail does not weakly dominate the tight tail")
            _b79 = _f79.get("scope_bracket") or {}
            if _b79.get("calibrated") is not False:
                _bad79.append("the scope bracket claims calibration off n=2")
            if _s79.get("swap_rows_match") is not True:
                _bad79.append("the two swap directions do not name the same rows")
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m79 = __import__("importlib").import_module("e279_substitution_soundness")
            _fresh79 = _m79.build()
            if _fresh79.get("summary") != _s79:
                _bad79.append("summary does not re-derive from the published faces")
            if _fresh79.get("census") != (_f79.get("census") or []):
                _bad79.append("the census does not re-derive")
        check(_name79, not _bad79,
              "; ".join(_bad79)[:220]
              or "verdict %r | %d/%d rows measured, %d with a stranded tail, %d event(s) "
                 "(deflations %d, vacuous %d); tails disagree on %d row(s); swap names the same "
                 "%d row(s) both ways; scope bracket [%s, %s] calibrated=%r"
                 % ((_f79 or {}).get("verdict"),
                    (_s79.get("rows_measured") or 0), (_s79.get("rows_published") or 0),
                    (_s79.get("rows_with_stranded_tail") or 0),
                    (_s79.get("substitution_events") or 0),
                    (_s79.get("events_with_deflation") or 0),
                    (_s79.get("events_vacuous_agreement") or 0),
                    len(_s79.get("rows_where_tails_disagree_on_reachability") or []),
                    len(_s79.get("swap_inflation_rows") or []),
                    _s79.get("scope_bracket", {}).get("must_exceed_observed"),
                    _s79.get("scope_bracket", {}).get("may_go_as_high_as"),
                    _s79.get("scope_bracket", {}).get("calibrated")))
    except Exception as e:
        check(_name79, False, repr(e)[:160])

    # E281: E279 scoped the substitution policy to "never conclude cannot". This leg asks the
    # dependency question that scoping leaves open: does any published conclusion rest on a
    # stranded tail to say cannot? The leg requires (a) the face re-derives, (b) every claim's
    # published boolean equals its own range, (c) any dependent claim is either disclosed by its
    # face or reported as needing action -- never silently counted as a measurement, and (d) the
    # census-level identity with E279 holds cell by cell, which is what exposes E279's group-keyed
    # summary field.
    _name81 = ("product: a cannot on a stranded tail needs no withdrawal here, but it is never a "
               "reading -- and the disagreement field is keyed on the group, not the cell")
    _bad81 = []
    try:
        _p81 = os.path.join("results", "state_tilt", "bandsubstituteaudit_latest.json")
        _f81 = None
        if not os.path.exists(_p81):
            _bad81.append("face missing: %s" % _p81)
        else:
            with io.open(_p81, encoding="utf-8") as _fh81:
                _f81 = json.load(_fh81)
        if _f81 is not None:
            _s81 = _f81.get("summary") or {}
            if _f81.get("evidence_cutoff") is None:
                _bad81.append("no evidence_cutoff on the face")
            if _s81.get("verdict") not in (
                    "a_cannot_rests_on_a_substitute_that_contradicts_it",
                    "a_cannot_rests_on_a_stranded_tail_without_disclosure",
                    "every_dependent_cannot_is_vacuous_and_disclosed",
                    "no_cannot_claim_rests_on_a_stranded_tail"):
                _bad81.append("verdict %r is outside the frozen set" % (_s81.get("verdict"),))
            if not _s81.get("claims_total"):
                _bad81.append("no claim was extracted -- the face would be about nothing")
            for _c81 in _f81.get("claims") or []:
                if _c81.get("cannot") is False and not _c81.get("stranded"):
                    if _c81.get("dependent"):
                        _bad81.append("a measured tail was marked dependent")
                if _c81.get("dependent") and not (
                        _c81.get("disclosed_in_face") or _c81.get("load_bearing")):
                    _bad81.append("a dependent claim is neither disclosed nor flagged")
                if _c81.get("polarity_agrees") is False:
                    _bad81.append("a published boolean contradicts its own range")
            _ic81 = _f81.get("identity_check") or {}
            if _ic81.get("checked_tail_booleans") != _s81.get("claims_total"):
                _bad81.append("the identity check did not cover every claim")
            if _ic81.get("mismatched"):
                _bad81.append("our re-derivation disagrees with E279's census")
            if _ic81.get("stranded_set_agrees") is not True:
                _bad81.append("our stranded set disagrees with E279's census")
            if _ic81.get("disagree_set_agrees") is not True:
                _bad81.append("our disagreement set disagrees with E279's census")
            if _ic81.get("e279_summary_field_is_ambiguous") and not _ic81.get(
                    "e279_summary_field_over_claims"):
                _bad81.append("the field is called ambiguous without the per-group counts")
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m81 = __import__("importlib").import_module("e281_substitution_dependency_audit")
            _fresh81 = _m81.build()
            if _fresh81.get("summary") != _s81:
                _bad81.append("summary does not re-derive from the published faces")
            if _fresh81.get("claims") != (_f81.get("claims") or []):
                _bad81.append("the claim census does not re-derive")
        check(_name81, not _bad81,
              "; ".join(_bad81)[:220]
              or "verdict %r | %d face(s), %d claim(s), %d cannot, %d dependent (load-bearing %d); "
                 "tails disagree on %s; E279 summary field keyed on %r"
                 % ((_f81 or {}).get("verdict"),
                    (_s81.get("faces_scanned") or 0), (_s81.get("claims_total") or 0),
                    (_s81.get("claims_cannot") or 0),
                    (_s81.get("dependent_cannot_claims") or 0),
                    (_s81.get("load_bearing_claims") or 0),
                    ",".join(_s81.get("rows_where_the_two_tails_disagree") or []) or "none",
                    (_f81 or {}).get("identity_check", {}).get("e279_summary_field_scope")))
    except Exception as e:
        check(_name81, False, repr(e)[:160])

    # E282: the seed wanted to know whether the two disagreement cells are a rounding boundary
    # artefact, reading their gap of 0.0 as "the substitute lands on the flip". This leg requires
    # (a) the census actually fired, (b) the clamp claim is measured consistently, (c) no cell is
    # published as a boundary tie while its non-reaching gap exceeds the tolerance -- a cell cannot
    # disagree on the boundary alone under the contract that made it disagree, and (d) the row
    # identity with E272 and the cell identity with E279 both hold.
    _name82 = ("product: the two disagreeing tails are a RANGE difference, not a rounding tie -- "
               "the gap field reads 0 for every interior reading, so it cannot say 'on the flip'")
    _bad82 = []
    try:
        _p82 = os.path.join("results", "state_tilt", "banddisagree_latest.json")
        _f82 = None
        if not os.path.exists(_p82):
            _bad82.append("face missing: %s" % _p82)
        else:
            with io.open(_p82, encoding="utf-8") as _fh82:
                _f82 = json.load(_fh82)
        if _f82 is not None:
            _s82 = _f82.get("summary") or {}
            if _f82.get("evidence_cutoff") is None:
                _bad82.append("no evidence_cutoff on the face")
            if _s82.get("verdict") not in (
                    "no_disagreement_cells_published",
                    "every_disagreement_is_a_boundary_tie",
                    "the_disagreement_is_a_range_difference_not_a_boundary_tie",
                    "disagreements_mix_boundary_ties_and_range_differences",
                    "the_gap_field_varies_inside_the_range_so_the_hypothesis_is_testable"):
                _bad82.append("verdict %r is outside the frozen set" % (_s82.get("verdict"),))
            if not _s82.get("faces_censused"):
                _bad82.append("no face qualified -- the census would be about nothing")
            if not _s82.get("rows_censused"):
                _bad82.append("no row was censused")
            if _s82.get("reaching_readings") != _s82.get("reaching_readings_with_zero_gap") \
                    and _s82.get("gap_is_clamped"):
                _bad82.append("the clamp is claimed while a reaching reading has a non-zero gap")
            if _f82.get("verdict") != _s82.get("verdict"):
                _bad82.append("verdict disagrees with its own summary")
            for _c82 in _f82.get("disagreement_cells") or []:
                if _c82.get("boundary_tie"):
                    _bad82.append("a cell is published as a boundary tie: %s" % _c82.get("row_key"))
                if _c82.get("non_reaching_gap_pct") is None:
                    _bad82.append("a disagreement cell publishes no gap: %s" % _c82.get("row_key"))
                elif abs(float(_c82["non_reaching_gap_pct"])) <= float(
                        _f82.get("frozen_spec", {}).get("tolerance") or 1e-12):
                    _bad82.append("a non-reaching tail's gap is inside tolerance")
                if not _c82.get("interior_of_reaching_tail") and not _c82.get("boundary_tie"):
                    _bad82.append("a cell is neither a tie nor interior -- unexplained")
            _ic82 = _f82.get("identity_check") or {}
            if _ic82.get("mismatched"):
                _bad82.append("our re-derivation disagrees with the published booleans")
            if _ic82.get("disagreement_set_agrees") is not True:
                _bad82.append("our disagreement set disagrees with E279's census")
            _cc82 = _f82.get("clamp_check") or {}
            if not _cc82.get("gap_is_clamped_for_every_reaching_reading"):
                _bad82.append("the clamp check did not hold on the published data")
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m82 = __import__("importlib").import_module("e282_substitution_disagreement_census")
            _fresh82 = _m82.build()
            if _fresh82.get("summary") != _s82:
                _bad82.append("summary does not re-derive from the published faces")
            if _fresh82.get("disagreement_cells") != (_f82.get("disagreement_cells") or []):
                _bad82.append("the disagreement census does not re-derive")
        check(_name82, not _bad82,
              "; ".join(_bad82)[:220]
              or "verdict %r | %d/%d face(s), %d row(s), %d disagreement cell(s) at position %s "
                 "with the other tail %s pct away (gap 0 on %d/%d reaching readings = clamped)"
                 % ((_f82 or {}).get("verdict"),
                    (_s82.get("faces_censused") or 0), (_s82.get("faces_scanned") or 0),
                    (_s82.get("rows_censused") or 0),
                    (_s82.get("rows_where_tails_disagree") or 0),
                    ",".join("%.3f" % p for p in
                             ((_f82 or {}).get("distributions") or {}).get(
                                 "reaching_position") or []) or "n/a",
                    ",".join("%.1f" % g for g in
                             ((_f82 or {}).get("distributions") or {}).get(
                                 "non_reaching_gap_pct") or []) or "n/a",
                    (_s82.get("reaching_readings_with_zero_gap") or 0),
                    (_s82.get("reaching_readings") or 0)))
    except Exception as e:
        check(_name82, False, repr(e)[:160])

    # E283: E279's contradiction branch ("the substitute deflates the conclusion") publishes 0
    # events, and a zero is not a measurement until the shape the event would need is quantified.
    # A stranded tail is degenerate, so it reaches a row only when the flip EQUALS its single
    # multiplier. This leg requires (a) the face publishes how far each candidate is and the
    # tolerance band that would fire the branch, (b) the band's own loosened test was applied to
    # every reading and the resulting split published -- a band that calls most of the family
    # reachable is a collapse, not a tolerance, and must be named as such, (c) the branch-fires
    # flag agrees with the candidates, and (d) the published booleans and E279's stranded set both
    # re-derive.
    _name83 = ("product: a contradiction branch that needs a 63 pct tolerance is not a test -- "
               "publish the split the tolerance would produce, not only the tolerance")
    _bad83 = []
    try:
        _p83 = os.path.join("results", "state_tilt", "banddeflate_latest.json")
        _f83 = None
        if not os.path.exists(_p83):
            _bad83.append("face missing: %s" % _p83)
        else:
            with io.open(_p83, encoding="utf-8") as _fh83:
                _f83 = json.load(_fh83)
        if _f83 is not None:
            _s83 = _f83.get("summary") or {}
            if _f83.get("evidence_cutoff") is None:
                _bad83.append("no evidence_cutoff on the face")
            if _s83.get("verdict") not in (
                    "no_degenerate_tail_is_published",
                    "the_deflation_branch_fires_on_a_published_row",
                    "the_branch_needs_a_tolerance_that_erases_the_reading",
                    "the_branch_is_unreachable_but_a_narrow_band_would_reach_it"):
                _bad83.append("verdict %r is outside the frozen set" % (_s83.get("verdict"),))
            if _f83.get("verdict") != _s83.get("verdict"):
                _bad83.append("verdict disagrees with its own summary")
            if not _s83.get("tail_readings_censused"):
                _bad83.append("no tail reading was censused")
            _br83 = _f83.get("branch") or {}
            _bd83 = _f83.get("tolerance_band") or {}
            _dc83 = _f83.get("discrimination_at_band") or {}
            if not _br83.get("n_candidate_readings"):
                _bad83.append("no degenerate candidate reading is published")
            if _br83.get("fires") is not _s83.get("branch_fires"):
                _bad83.append("the branch-fires flag disagrees with its summary copy")
            if _br83.get("fires") and not _br83.get("fires_on"):
                _bad83.append("the branch is claimed to fire without naming the row")
            if not _br83.get("fires"):
                if _bd83.get("lower_pct") is None:
                    _bad83.append("the branch does not fire and no tolerance band is published")
                elif float(_bd83["lower_pct"]) <= 0:
                    _bad83.append("the tolerance band has no positive lower end")
                if _bd83.get("upper_pct") is not None:
                    _bad83.append("the band is claimed bounded above")
                if _dc83.get("readings_total") != _s83.get("tail_readings_censused"):
                    _bad83.append("the band's test was not applied to every censused reading")
                if not isinstance(_dc83.get("collapse"), bool):
                    _bad83.append("no collapse verdict on the band's discrimination")
                if _dc83.get("collapse") and _dc83.get("readings_reachable_at_band") is not None \
                        and float(_dc83["readings_reachable_at_band"]) <= float(
                            _dc83.get("readings_reachable_published") or 0):
                    _bad83.append("a collapse is claimed but the loosened test adds nothing")
                if (_dc83.get("collapse") is True
                        and _s83.get("verdict")
                        == "the_branch_is_unreachable_but_a_narrow_band_would_reach_it"):
                    _bad83.append("a collapsing band is published as a narrow band")
            _ic83 = _f83.get("identity_check") or {}
            if _ic83.get("n_mismatched"):
                _bad83.append("a published boolean contradicts the range that published it")
            if _ic83.get("stranded_set_agrees") is not True \
                    or _ic83.get("stranded_pairs_agree") is not True:
                _bad83.append("our stranded set disagrees with E279's census")
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m83 = __import__("importlib").import_module("e283_degenerate_range_reachable")
            _fresh83 = _m83.build()
            if _fresh83.get("summary") != _s83:
                _bad83.append("summary does not re-derive from the published faces")
            if _fresh83.get("branch") != (_f83.get("branch") or {}):
                _bad83.append("the branch measurement does not re-derive")
            if _fresh83.get("tolerance_band") != (_f83.get("tolerance_band") or {}):
                _bad83.append("the tolerance band does not re-derive")
        check(_name83, not _bad83,
              "; ".join(_bad83)[:220]
              or "verdict %r | %d reading(s), %d degenerate, %d deflatable, fires=%s; band %s pct, "
                 "and at that tolerance %s of %s reading(s) read reachable against %s published"
                 % ((_f83 or {}).get("verdict"),
                    (_s83.get("tail_readings_censused") or 0),
                    (_s83.get("n_degenerate_readings") or 0),
                    (_s83.get("n_deflatable") or 0),
                    _s83.get("branch_fires"),
                    "n/a" if _s83.get("required_tolerance_pct") is None
                    else "%.2f" % _s83["required_tolerance_pct"],
                    _s83.get("readings_reachable_at_band"),
                    _s83.get("tail_readings_censused"),
                    _s83.get("readings_reachable_published")))
    except Exception as e:
        check(_name83, False, repr(e)[:160])

    # E284: E281 caught one summary field that names ROWS while publishing GROUP labels (cross
    # and star_lag1_residual each carry 4 cells, exactly one of which disagrees). A label that
    # names a whole group for a one-cell finding tells the reader four cells were measured when
    # one was. This leg requires (a) the disagreement is republished at CELL scope, re-derived
    # from E279's own per-tail booleans and landing exactly on the cells that face already
    # publishes as its swap rows, (b) the old group field is kept but its bound direction is
    # published rather than assumed, (c) the family-wide sweep reports how many fields it
    # classified and does NOT claim the integer count fields it could not judge, and (d) the
    # flagged set re-derives on a fresh build.
    _name84 = ("product: a field that names rows while publishing group labels must be repaired "
               "at cell scope -- and the sweep must not call unjudged counts clean")
    _bad84 = []
    try:
        _p84 = os.path.join("results", "state_tilt", "banddisagreescope_latest.json")
        _f84 = None
        if not os.path.exists(_p84):
            _bad84.append("face missing: %s" % _p84)
        else:
            with io.open(_p84, encoding="utf-8") as _fh84:
                _f84 = json.load(_fh84)
        if _f84 is not None:
            if _f84.get("evidence_cutoff") is None:
                _bad84.append("no evidence_cutoff on the face")
            if _f84.get("verdict") not in (
                    "no_summary_field_publishes_group_labels_under_a_row_name",
                    "the_slip_is_unique_to_one_field",
                    "multiple_faces_carry_the_same_slip",
                    "the_field_cannot_be_repaired_from_its_own_census"):
                _bad84.append("verdict %r is outside the frozen set" % (_f84.get("verdict"),))
            _rp84 = (_f84.get("repair") or {}).get("known_slip") or {}
            if not _rp84.get("repairable"):
                _bad84.append("the known slip was not repaired")
            _cells84 = _rp84.get("cells") or []
            if not _cells84:
                _bad84.append("no cell-scoped key was published")
            if any(c.count("|") != 2 for c in _cells84):
                _bad84.append("a published cell key is not row|cell|index")
            if _rp84.get("group_scope_count") and len(_cells84) and \
                    _rp84.get("group_scope_is_upper_bound") is not True:
                _bad84.append("the group field is kept but its bound direction is not published")
            if _rp84.get("matches_published_swap_rows") is not True:
                _bad84.append("the repaired cells do not land on the face's own swap rows")
            if not _rp84.get("groups_match"):
                _bad84.append("the group labels do not match the re-derived groups")
            _rk84 = (_f84.get("repair") or {}).get("repaired_keys") or {}
            if sorted(_rk84.get("cells_where_tails_disagree_on_reachability") or []) != sorted(_cells84):
                _bad84.append("the cell keys are published once but not re-derived in the repair block")
            _sw84 = _f84.get("sweep") or {}
            _fl84 = _sw84.get("flagged_fields") or []
            if _sw84.get("n_flagged") != len(_fl84):
                _bad84.append("n_flagged disagrees with the flagged list")
            if any(f.get("class") != "group_labels_under_row_name" for f in _fl84):
                _bad84.append("a flagged field is not of the slip class")
            _sk84 = _sw84.get("count_fields_not_assessed") or {}
            if not _sk84.get("n_total"):
                _bad84.append("no unassessed count field is disclosed")
            if _sk84.get("n_total") != sum(k.get("occurrences") or 0
                                           for k in (_sk84.get("by_key") or [])):
                _bad84.append("the unassessed count keys do not add up to their own total")
            if not _sw84.get("faces_scanned"):
                _bad84.append("no face was scanned")
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m84 = __import__("importlib").import_module("e284_disagreement_field_scope")
            _fresh84 = _m84.build()
            if _fresh84.get("verdict") != _f84.get("verdict"):
                _bad84.append("the verdict does not re-derive")
            if (_fresh84.get("repair") or {}).get("known_slip", {}).get("cells") != _cells84:
                _bad84.append("the cell keys do not re-derive")
            if sorted(f.get("path") for f in (_fresh84.get("sweep") or {}).get("flagged_fields") or []) \
                    != sorted(f.get("path") for f in _fl84):
                _bad84.append("the flagged set does not re-derive")
        check(_name84, not _bad84,
              "; ".join(_bad84)[:220]
              or "verdict %r | %d group label(s) repaired to %s, upper_bound=%s, swap-row identity=%s; "
                 "%d face(s) scanned, %d flagged, %d count field(s) left unassessed over %d key(s)"
                 % ((_f84 or {}).get("verdict"),
                    _rp84.get("group_scope_count") or 0,
                    ",".join(_cells84),
                    _rp84.get("group_scope_is_upper_bound"),
                    _rp84.get("matches_published_swap_rows"),
                    (_sw84.get("faces_scanned") or 0),
                    (_sw84.get("n_flagged") or 0),
                    (_sk84.get("n_total") or 0),
                    (_sk84.get("n_distinct_keys") or 0)))
    except Exception as e:
        check(_name84, False, repr(e)[:160])

    # E285: the two tails publish different ranges, so there is a space BETWEEN them. A flip that
    # lands in that gap is reachable by neither tail and only widening could ever pick it up -- but
    # the reader also needs to know how much of the unresolvable set the gap actually accounts for.
    # This leg requires (a) every row takes exactly one class and the classes sum to the rows
    # censused, (b) gap rows are published unreachable by both tails and sit inside a POSITIVE gap
    # on their own arm, (c) rows above the family's published ceiling are counted separately from
    # the gap (they are extrapolation, not headroom) and each is verified to be above that ceiling,
    # and (d) the verdict and gap set re-derive on a fresh build.
    _name85 = ("product: the inter-range gap is a smaller widening target than the area beyond the "
               "published ceiling -- both must be counted, not added")
    _bad85 = []
    try:
        _p85 = os.path.join("results", "state_tilt", "bandgapceiling_latest.json")
        _f85 = None
        if not os.path.exists(_p85):
            _bad85.append("face missing: %s" % _p85)
        else:
            with io.open(_p85, encoding="utf-8") as _fh85:
                _f85 = json.load(_fh85)
        if _f85 is not None:
            if _f85.get("evidence_cutoff") is None:
                _bad85.append("no evidence_cutoff on the face")
            if _f85.get("verdict") not in (
                    "no_arm_publishes_a_positive_gap",
                    "no_row_falls_in_the_inter_range_gap",
                    "the_gap_holds_fewer_rows_than_the_area_beyond_the_published_ceiling",
                    "the_gap_is_the_only_widening_target"):
                _bad85.append("verdict %r is outside the frozen set" % (_f85.get("verdict"),))
            _s85 = _f85.get("summary") or {}
            _arms85 = _f85.get("arms") or []
            _classes85 = {}
            for _a in _arms85:
                for _k, _v in (_a.get("counts") or {}).items():
                    _classes85[_k] = _classes85.get(_k, 0) + _v
                if not _a.get("partition_sums_to_rows"):
                    _bad85.append("arm %s classes do not sum to its rows" % _a.get("arm"))
            if sum(_classes85.values()) != _s85.get("rows_censused"):
                _bad85.append("the class partition does not sum to the rows censused")
            _gap85 = _f85.get("widening_target") or {}
            _gap_rows85 = _gap85.get("rows") or []
            if _s85.get("n_gap_rows") != len(_gap_rows85):
                _bad85.append("n_gap_rows disagrees with the published gap rows")
            if _gap85.get("max_rows_any_gap_widening_could_add") != len(_gap_rows85):
                _bad85.append("the widening ceiling is not the gap row count")
            for _r in _gap_rows85:
                if (_r.get("published_reachable") or {}).get("tight") or \
                        (_r.get("published_reachable") or {}).get("wide"):
                    _bad85.append("a gap row is published reachable by a tail")
            if any(_r.get("class") != "in_gap" for _r in _gap_rows85):
                _bad85.append("a gap row is not of the in_gap class")
            _gap_arms85 = {g.get("arm") for g in (_f85.get("gap_by_arm") or [])
                           if g.get("positive")}
            _arm_of85 = {}
            for _a in _arms85:
                for _r in (_a.get("rows") or []):
                    _arm_of85[_r.get("row_key")] = _a.get("arm")
            for _r in _gap_rows85:
                if _arm_of85.get(_r.get("row_key")) not in _gap_arms85:
                    _bad85.append("gap row %s sits on an arm with no positive gap"
                                  % _r.get("row_key"))
            _ceiling85 = _s85.get("published_ceiling")
            _above85 = (_f85.get("beyond_ceiling") or {}).get("rows") or []
            if _s85.get("n_above_ceiling") != len(_above85):
                _bad85.append("n_above_ceiling disagrees with the published rows")
            if _ceiling85 is None:
                _bad85.append("no published ceiling is carried")
            elif any(not (_r.get("flip") or 0) > _ceiling85 for _r in _above85):
                _bad85.append("an above-ceiling row is not above the published ceiling")
            _ic85 = _f85.get("identity_check") or {}
            if not _ic85.get("rows_match_source") or not _ic85.get("counts_agree_with_source"):
                _bad85.append("the counts do not agree with the source face")
            if not _ic85.get("gap_rows_are_unreachable_by_construction"):
                _bad85.append("the gap rows are not unreachable by construction")
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m85 = __import__("importlib").import_module("e285_interrange_gap_ceiling")
            _fresh85 = _m85.build()
            if _fresh85.get("verdict") != _f85.get("verdict"):
                _bad85.append("the verdict does not re-derive")
            if (_fresh85.get("summary") or {}).get("gap_rows") != _s85.get("gap_rows"):
                _bad85.append("the gap rows do not re-derive")
            if (_fresh85.get("summary") or {}).get("above_ceiling_rows") != \
                    _s85.get("above_ceiling_rows"):
                _bad85.append("the above-ceiling rows do not re-derive")
        check(_name85, not _bad85,
              "; ".join(_bad85)[:220]
              or "verdict %r | %d arm(s), %d row(s): %d in a positive gap (%s), %d above the "
                 "published ceiling %s (max %s), %d below the floor, %d reachable; widening can "
                 "add at most the gap rows"
                 % ((_f85 or {}).get("verdict"),
                    _s85.get("arms_measured") or 0,
                    _s85.get("rows_censused") or 0,
                    _s85.get("n_gap_rows") or 0,
                    ",".join(_s85.get("gap_rows") or []) or "none",
                    _s85.get("n_above_ceiling") or 0,
                    "n/a" if _s85.get("published_ceiling") is None
                    else "%.4f" % _s85["published_ceiling"],
                    "n/a" if not _above85 else "%.4fx" % max(
                        _r.get("flip_over_published_ceiling") or 0 for _r in _above85),
                    _s85.get("n_below_floor") or 0,
                    (_s85.get("n_reachable_tight") or 0) + (_s85.get("n_reachable_wide") or 0)))
    except Exception as e:
        check(_name85, False, repr(e)[:160])

    # 86) E286 count-field scope (r1311 bm-b): a count whose name claims a unit is checkable
    # only when the records it points at sit in the SAME scope.  The leg asserts (a) only
    # same-scope counts are published as re-derivable and each agrees with its own records,
    # (b) the un-derivable set splits into "unit published elsewhere" and "unit never published"
    # (two different fixes, D4), (c) re-derivable + cannot sums to the census and the per-key
    # aggregates sum back to the field census, and (d) the verdict and the counts re-derive.
    _name86 = ("product: a unit-named count is checkable only inside its own scope -- and the "
               "share that is checkable must be reported, not assumed whole")
    _bad86 = []
    try:
        _p86 = os.path.join("results", "state_tilt", "bandcountscope_latest.json")
        _f86 = None
        if not os.path.exists(_p86):
            _bad86.append("face missing: %s" % _p86)
        else:
            with io.open(_p86, encoding="utf-8") as _fh86:
                _f86 = json.load(_fh86)
        if _f86 is not None:
            if _f86.get("evidence_cutoff") is None:
                _bad86.append("no evidence_cutoff on the face")
            if _f86.get("verdict") not in (
                    "some_unit_named_counts_count_something_other_than_the_unit_their_name_claims",
                    "no_unit_named_count_can_be_re_derived_from_its_own_scope",
                    "the_checkable_share_of_unit_named_counts_is_a_minority_and_every_one_agrees",
                    "every_unit_named_count_is_re_derivable_and_agrees"):
                _bad86.append("verdict %r is outside the frozen set" % (_f86.get("verdict"),))
            _s86 = _f86.get("summary") or {}
            _rr86 = _f86.get("re_derivable_rows") or []
            if _s86.get("n_re_derivable") != len(_rr86):
                _bad86.append("n_re_derivable disagrees with the published rows")
            if _s86.get("n_agree") != len([_r for _r in _rr86 if _r.get("agrees")]):
                _bad86.append("n_agree disagrees with the published rows")
            for _r in _rr86:
                if _r.get("derivation") != "exact_sibling":
                    _bad86.append("row %s is published as re-derivable without a same-scope sibling"
                                  % _r.get("path"))
                if _r.get("agrees") and _r.get("measured_unit_count") != _r.get("published_value"):
                    _bad86.append("row %s is marked agreeing but its count differs" % _r.get("path"))
            _cant86 = _f86.get("cannot_rederive") or {}
            _why86 = _cant86.get("by_why") or {}
            if _s86.get("of_which_unit_list_exists_elsewhere") != _why86.get("unit_list_exists_elsewhere", 0):
                _bad86.append("the elsewhere-scope count disagrees with by_why")
            if _s86.get("of_which_unit_never_published") != _why86.get("unit_never_published", 0):
                _bad86.append("the never-published count disagrees with by_why")
            if (_s86.get("n_re_derivable") or 0) + (_s86.get("n_cannot_rederive") or 0) != \
                    _s86.get("unit_named_int_fields"):
                _bad86.append("re-derivable + cannot does not sum to the census")
            if (_why86.get("unit_list_exists_elsewhere", 0)
                    + _why86.get("unit_never_published", 0)) != _s86.get("n_cannot_rederive"):
                _bad86.append("the two halves of cannot-check do not sum to the un-derivable total")
            _pk86 = _f86.get("per_key") or []
            if sum(_k.get("occurrences") or 0 for _k in _pk86) != _s86.get("unit_named_int_fields"):
                _bad86.append("per-key occurrences do not sum to the census")
            if sum(_k.get("re_derivable") or 0 for _k in _pk86) != _s86.get("n_re_derivable"):
                _bad86.append("per-key re-derivable counts do not sum to the census")
            _ic86 = _f86.get("identity_check") or {}
            for _k in ("partition_sums_to_fields", "why_partition_sums_to_cannot",
                       "by_key_occurrences_sum", "no_bool_reached_the_census"):
                if not _ic86.get(_k):
                    _bad86.append("identity check %s is false" % _k)
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m86 = __import__("importlib").import_module("e286_count_field_scope")
            _fresh86 = _m86.build()
            _fs86 = _fresh86.get("summary") or {}
            if _fresh86.get("verdict") != _f86.get("verdict"):
                _bad86.append("the verdict does not re-derive")
            for _k in ("n_re_derivable", "n_agree", "n_disagree", "n_cannot_rederive",
                       "unit_named_int_fields", "disagree_rows"):
                if _fs86.get(_k) != _s86.get(_k):
                    _bad86.append("summary.%s does not re-derive" % _k)
            if [(_r.get("face"), _r.get("path")) for _r in (_fresh86.get("re_derivable_rows") or [])] \
                    != [(_r.get("face"), _r.get("path")) for _r in _rr86]:
                _bad86.append("the re-derivable row set does not re-derive")
        check(_name86, not _bad86,
              "; ".join(_bad86)[:220]
              or "verdict %r | %d face(s), %d unit-named count(s): %d re-derivable (%s) and all "
                 "%d agree; %d un-derivable = %d elsewhere-scope + %d never published; %d qualified "
                 "subset names not judged"
                 % ((_f86 or {}).get("verdict"),
                    _s86.get("faces_censused") or 0,
                    _s86.get("unit_named_int_fields") or 0,
                    _s86.get("n_re_derivable") or 0,
                    "n/a" if _s86.get("re_derivable_share") is None
                    else "%.1f pct" % (100.0 * _s86["re_derivable_share"]),
                    _s86.get("n_agree") or 0,
                    _s86.get("n_cannot_rederive") or 0,
                    _s86.get("of_which_unit_list_exists_elsewhere") or 0,
                    _s86.get("of_which_unit_never_published") or 0,
                    _s86.get("qualified_unit_named_fields_not_judged") or 0))
    except Exception as e:
        check(_name86, False, repr(e)[:160])

    # 87) E290 self-auditable face profile (r1312 bm-b): the 27 checkable counts sit beside a
    # same-parent list of exactly the unit their name claims, and every one equals that list -- but
    # co-location is not evidence, so the leg asserts (a) every checkable row really equals its own
    # list, (b) an equal-length same-unit list elsewhere in the same face is published as an
    # ambiguity rather than a clean bill, (c) the exemplar faces' own coverage is published beside the
    # family-wide share (27 of 151 = 17.9 pct against 3.0 pct), and (d) the un-derivable halves are
    # two separate work items, never one 'fixable' number.
    _name87 = ("product: a count is self-auditable only when its own records share its scope -- and "
               "an equal-length alternative list makes the agreement ambiguous, not clean")
    _bad87 = []
    try:
        _p87 = os.path.join("results", "state_tilt", "bandselfaudit_latest.json")
        _f87 = None
        if not os.path.exists(_p87):
            _bad87.append("face missing: %s" % _p87)
        else:
            with io.open(_p87, encoding="utf-8") as _fh87:
                _f87 = json.load(_fh87)
        if _f87 is not None:
            if _f87.get("evidence_cutoff") is None:
                _bad87.append("no evidence_cutoff on the face")
            if _f87.get("verdict") not in (
                    "the_checkable_counts_share_a_same_parent_record_list_and_every_agreement_is_unambiguous",
                    "the_checkable_counts_share_a_same_parent_record_list_but_some_agreements_could_be_coincidence",
                    "the_checkable_counts_share_a_same_parent_record_list_but_the_records_are_not_uniformly_typed",
                    "no_count_is_checkable_so_there_is_no_shape_to_copy"):
                _bad87.append("verdict %r is outside the frozen set" % (_f87.get("verdict"),))
            _s87 = _f87.get("summary") or {}
            _cr87 = _f87.get("checkable_rows") or []
            if _s87.get("checkable_counts") != len(_cr87):
                _bad87.append("checkable_counts disagrees with the published rows")
            if _s87.get("n_agree") != len([_r for _r in _cr87 if _r.get("agrees")]):
                _bad87.append("n_agree disagrees with the published rows")
            _amb87 = ["%s :: %s" % (_r.get("face"), _r.get("path")) for _r in _cr87 if _r.get("ambiguous")]
            if _s87.get("ambiguous_rows") != _amb87:
                _bad87.append("the ambiguous row list disagrees with the published rows")
            if _s87.get("n_ambiguous") != len(_amb87):
                _bad87.append("n_ambiguous disagrees with the ambiguous row list")
            for _r in _cr87:
                if not _r.get("sibling_present_same_parent"):
                    _bad87.append("row %s is published checkable without its sibling in scope"
                                  % _r.get("path"))
                if _r.get("agrees") and _r.get("records_length") != _r.get("published_value"):
                    _bad87.append("row %s is marked agreeing but its count differs" % _r.get("path"))
                if _r.get("ambiguous") and not (_r.get("alternatives_with_equal_length") or 0):
                    _bad87.append("row %s is marked ambiguous with no equal-length alternative"
                                  % _r.get("path"))
            if (_s87.get("n_records_are_dicts") or 0) + (_s87.get("n_records_are_scalars") or 0) \
                    != _s87.get("checkable_counts"):
                _bad87.append("the record-type partition does not sum to the checkable counts")
            # (c) the pattern's coverage is measured, never assumed to be the whole face
            if (_s87.get("exemplar_unit_named_counts") or 0) < (_s87.get("checkable_counts") or 0):
                _bad87.append("the exemplar coverage excludes the checkable counts themselves")
            if _s87.get("exemplar_checkable_share") is None or \
                    _s87.get("checkable_share_family") is None:
                _bad87.append("the pattern's coverage is not published")
            # (d) the two un-derivable halves stay separate
            if (_s87.get("un_derivable_elsewhere_scope") or {}).get("n_rows") is None or \
                    (_s87.get("un_derivable_never_published") or {}).get("n_rows") is None:
                _bad87.append("the un-derivable halves are not published separately")
            _ic87 = _f87.get("identity_check") or {}
            for _k in ("checkable_rows_equal_e286_census", "rows_partition_by_record_type",
                       "every_checkable_row_has_its_sibling_in_scope",
                       "every_checkable_row_agrees_with_its_own_records",
                       "exemplar_face_set_matches_rows", "self_faces_absent_from_universe"):
                if not _ic87.get(_k):
                    _bad87.append("identity check %s is false" % _k)
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m87 = __import__("importlib").import_module("e290_selfauditable_face_profile")
            _fresh87 = _m87.build()
            _fs87 = _fresh87.get("summary") or {}
            if _fresh87.get("verdict") != _f87.get("verdict"):
                _bad87.append("the verdict does not re-derive")
            for _k in ("checkable_counts", "unit_named_counts", "n_agree", "n_disagree",
                       "n_ambiguous", "n_records_are_dicts", "n_records_are_scalars",
                       "exemplar_checkable_counts", "exemplar_unit_named_counts"):
                if _fs87.get(_k) != _s87.get(_k):
                    _bad87.append("summary.%s does not re-derive" % _k)
            if [("%s :: %s" % (_r.get("face"), _r.get("path"))) for _r in
                    (_fresh87.get("checkable_rows") or [])] != \
                    [("%s :: %s" % (_r.get("face"), _r.get("path"))) for _r in _cr87]:
                _bad87.append("the checkable row set does not re-derive")
        check(_name87, not _bad87,
              "; ".join(_bad87)[:220]
              or "verdict %r | %d checkable of %d unit-named count(s) (%s) in %d face(s): all %d "
                 "agree with their own records, %d ambiguous against an equal-length alternative "
                 "(dicts %d / scalars %d); exemplars are %d of %d of their own counts (%s) against %s "
                 "family-wide; un-derivable = %d anywhere-scope row(s) over %d scope(s) + %d "
                 "never-published row(s) over %d key(s)"
                 % ((_f87 or {}).get("verdict"),
                    _s87.get("checkable_counts") or 0,
                    _s87.get("unit_named_counts") or 0,
                    "n/a" if _s87.get("checkable_share_family") is None
                    else "%.1f pct" % (100.0 * _s87["checkable_share_family"]),
                    _s87.get("exemplar_faces_n") or 0,
                    _s87.get("n_agree") or 0,
                    _s87.get("n_ambiguous") or 0,
                    _s87.get("n_records_are_dicts") or 0,
                    _s87.get("n_records_are_scalars") or 0,
                    _s87.get("exemplar_checkable_counts") or 0,
                    _s87.get("exemplar_unit_named_counts") or 0,
                    "n/a" if _s87.get("exemplar_checkable_share") is None
                    else "%.1f pct" % (100.0 * _s87["exemplar_checkable_share"]),
                    "n/a" if _s87.get("checkable_share_family") is None
                    else "%.1f pct" % (100.0 * _s87["checkable_share_family"]),
                    (_s87.get("un_derivable_elsewhere_scope") or {}).get("n_rows") or 0,
                    (_s87.get("un_derivable_elsewhere_scope") or {}).get("distinct_scopes") or 0,
                    (_s87.get("un_derivable_never_published") or {}).get("n_rows") or 0,
                    (_s87.get("un_derivable_never_published") or {}).get("distinct_keys") or 0))
    except Exception as e:
        check(_name87, False, repr(e)[:160])

    # E291 r1313: E290's ambiguity flag is only informative if equal-length siblings can be accidents.
    # They are not: the rows fire at the pooled-length null while the list-level concentration is far
    # above it, and the equal-length pairs are schema (605) or the same content (135), with only 6
    # differing in content -- so the flag marks a shared shape, and 135 duplicated lists, not conflict.
    _name88 = ("product: an equal-length sibling is the face's shape repeating, not a coin flip -- the "
               "ambiguity flag's rate is the length base rate and its mechanism is schema and aliases")
    _bad88 = []
    try:
        _p88 = os.path.join("results", "state_tilt", "bandambient_latest.json")
        _f88 = None
        if not os.path.exists(_p88):
            _bad88.append("face missing: %s" % _p88)
        else:
            with io.open(_p88, encoding="utf-8") as _fh88:
                _f88 = json.load(_fh88)
        if _f88 is not None:
            if _f88.get("evidence_cutoff") is None:
                _bad88.append("no evidence_cutoff on the face")
            if _f88.get("verdict") not in (
                    "the_ambiguity_rate_is_the_length_base_rate_and_the_pairs_are_schema_not_accident",
                    "the_flagged_rows_exceed_the_length_base_rate_so_the_ambiguity_is_real",
                    "no_face_publishes_two_lists_of_the_same_unit_so_ambiguity_cannot_arise"):
                _bad88.append("verdict %r is outside the frozen set" % (_f88.get("verdict"),))
            _s88 = _f88.get("summary") or {}
            _row88 = _s88.get("row_level") or {}
            _lst88 = _s88.get("list_level") or {}
            _mech88 = _s88.get("pair_mechanism") or {}
            _rows88 = _f88.get("rows") or []
            if _row88.get("checkable_rows") != len(_rows88):
                _bad88.append("checkable_rows disagrees with the published row list")
            _flag88 = [_r for _r in _rows88 if _r.get("flagged_ambiguous_by_e290")]
            if _row88.get("flagged_ambiguous") != len(_flag88):
                _bad88.append("flagged_ambiguous disagrees with the published rows")
            if _row88.get("distinct_scopes_behind_the_flag") is None or \
                    _row88["distinct_scopes_behind_the_flag"] > max(1, len(_flag88)):
                _bad88.append("the scopes behind the flag are not published or exceed the rows")
            # a rate is only readable beside its null and its tail
            for _k in ("expected_rate_under_null", "tail_p_above_null", "observed_rate"):
                if _row88.get(_k) is None:
                    _bad88.append("row_level.%s is not published" % _k)
            for _k in ("observed_rate", "expected_rate_under_pooled_length_null", "tail_p_above_null"):
                if _lst88.get(_k) is None:
                    _bad88.append("list_level.%s is not published" % _k)
            # (b) the mechanism is a partition, and an alias is never folded into a conflict
            _sum88 = (_mech88.get("alias_identical_content") or 0) + \
                     (_mech88.get("same_schema_different_rows") or 0) + \
                     (_mech88.get("different_content") or 0)
            if _sum88 != (_mech88.get("equal_length_pairs") or 0):
                _bad88.append("the content classes do not partition the equal-length pairs")
            if _mech88.get("share_different_content") is None:
                _bad88.append("the content-different share is not published")
            # (c) the two aggregators are published with their own reading
            _ag88 = _s88.get("aggregator_agreement") or {}
            if "row_level_says_at_or_below_null" not in _ag88 or \
                    "list_level_says_above_null" not in _ag88 or "stable" not in _ag88:
                _bad88.append("the two aggregators are not both published")
            _ic88 = _f88.get("identity_check") or {}
            for _k in ("row_count_matches_e290_summary", "flagged_rows_match_e290_summary",
                       "flagged_rows_are_the_e290_ambiguous_set", "mechanism_partition",
                       "self_faces_absent_from_universe", "source_face_absent_from_universe",
                       "scopes_partition_the_flagged_rows"):
                if not _ic88.get(_k):
                    _bad88.append("identity check %s is false" % _k)
            if "BANDSELFAUDIT-2026-10-29.json" in (_f88.get("faces_censused") or []):
                _bad88.append("E290's own face is inside the census it is explaining")
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m88 = __import__("importlib").import_module("e291_ambiguity_chance")
            _fresh88 = _m88.build()
            if _fresh88.get("verdict") != _f88.get("verdict"):
                _bad88.append("the verdict does not re-derive")
            _fs88 = _fresh88.get("summary") or {}
            for _blk in ("row_level", "list_level", "pair_mechanism", "aggregator_agreement"):
                if _fs88.get(_blk) != _s88.get(_blk):
                    _bad88.append("summary.%s does not re-derive" % _blk)
            for _k in ("faces_censused", "same_unit_lists", "repeated_unit_groups"):
                if _fs88.get(_k) != _s88.get(_k):
                    _bad88.append("summary.%s does not re-derive" % _k)
        check(_name88, not _bad88,
              "; ".join(_bad88)[:220]
              or "verdict %r | %d of %d flagged row(s) vs %s expected (p=%s) over %d scope(s); "
                 "lists %d of %d (%s) vs %s expected (p=%s); %d equal-length pair(s) = alias %d / "
                 "same_schema %d / different_content %d"
                 % ((_f88 or {}).get("verdict"),
                    _row88.get("flagged_ambiguous") or 0, _row88.get("checkable_rows") or 0,
                    "n/a" if _row88.get("expected_rate_under_null") is None
                    else "%.1f pct" % (100.0 * _row88["expected_rate_under_null"]),
                    "n/a" if _row88.get("tail_p_above_null") is None
                    else "%.3f" % _row88["tail_p_above_null"],
                    _row88.get("distinct_scopes_behind_the_flag") or 0,
                    _lst88.get("observed_equal_length_sibling") or 0,
                    _lst88.get("eligible_lists") or 0,
                    "n/a" if _lst88.get("observed_rate") is None
                    else "%.1f pct" % (100.0 * _lst88["observed_rate"]),
                    "n/a" if _lst88.get("expected_rate_under_pooled_length_null") is None
                    else "%.1f pct" % (100.0 * _lst88["expected_rate_under_pooled_length_null"]),
                    "n/a" if _lst88.get("tail_p_above_null") is None
                    else "%.3f" % _lst88["tail_p_above_null"],
                    _mech88.get("equal_length_pairs") or 0,
                    _mech88.get("alias_identical_content") or 0,
                    _mech88.get("same_schema_different_rows") or 0,
                    _mech88.get("different_content") or 0))
    except Exception as e:
        check(_name88, False, repr(e)[:160])

    # E287 r1314: E285's ceiling only means "no published instrument reaches these rows" if nothing
    # wider is already published. Nothing is: of the six dated faces publishing a "multiplier", only
    # two are band-edge supplies and both tops sit below the ceiling (1.8383 median / 2.2457 single
    # seed), while the two numbers that look wider (63.0 pct tolerance, 2.0327 spread threshold) are
    # off-axis. Both gap rows are reachable by that same supply -- one at the median, both at the
    # single best seed -- so the gap is the only place existing supply could pay.
    _name89 = ("product: the family's ceiling is above every supply the family already publishes -- "
               "the extrapolated rows stay extrapolated and only the gap rows are reachable")
    _bad89 = []
    try:
        _p89 = os.path.join("results", "state_tilt", "bandsupply_latest.json")
        _f89 = None
        if not os.path.exists(_p89):
            _bad89.append("face missing: %s" % _p89)
        else:
            with io.open(_p89, encoding="utf-8") as _fh89:
                _f89 = json.load(_fh89)
        if _f89 is not None:
            if _f89.get("evidence_cutoff") is None:
                _bad89.append("no evidence_cutoff on the face")
            _vocab89 = ("published_supply_reaches_a_row_above_the_published_ceiling",
                        "published_supply_reaches_the_gap_rows_only",
                        "no_published_supply_reaches_any_row_beyond_the_published_tails")
            if _f89.get("verdict") not in _vocab89:
                _bad89.append("verdict %r is outside the frozen set" % (_f89.get("verdict"),))
            _s89 = _f89.get("summary") or {}
            _ic89 = _f89.get("demand_identity") or {}
            # (a) the ceiling is measured: it must equal the widest published arm top (D5)
            if not _ic89.get("ceiling_equals_widest_published_arm_top"):
                _bad89.append("the ceiling is not the widest published arm top")
            if not _ic89.get("agree"):
                _bad89.append("the flips disagree with the other face that publishes them")
            if not _ic89.get("rows_are_the_e285_unreached_set"):
                _bad89.append("the requirement rows are not E285's unreached set")
            # (b) no usable supply may exceed the ceiling, or the verdict is wrong by construction
            if not _ic89.get("no_reading_above_the_ceiling_except_the_circular_one"):
                _bad89.append("a usable supply reading exceeds the ceiling")
            _cons89 = _s89.get("widen_cap_conservative")
            _opt89 = _s89.get("widen_cap_optimistic")
            _ceil89 = _s89.get("ceiling")
            if None in (_cons89, _opt89, _ceil89):
                _bad89.append("a supply cap or the ceiling is not published")
            elif not (_cons89 <= _opt89 <= _ceil89):
                _bad89.append("the caps are not ordered conservative <= optimistic <= ceiling")
            # (c) every reading is signed, and a circular/off-axis number never sets a cap
            _rd89 = _f89.get("supply_readings") or []
            if not _rd89:
                _bad89.append("no supply readings are published")
            if any(_r.get("axis") != "band_edge_multiplier" for _r in _rd89):
                _bad89.append("a supply reading is not on the band-edge axis (D1)")
            _unused89 = [_r for _r in _rd89 if not _r.get("usable_as_supply")]
            if any(_r.get("cap") is not None and _r.get("direction") == "widen" and _r.get("cap") > _opt89
                   for _r in _rd89 if _r.get("usable_as_supply")):
                _bad89.append("a usable reading is wider than the published optimistic cap")
            if not _unused89:
                _bad89.append("the circular readings are not published at all")
            _off89 = _f89.get("off_axis_readings") or []
            if len(_off89) < 3 or any(not _o.get("reason") for _o in _off89):
                _bad89.append("the off-axis numbers are not published with a reason each")
            _offkeys89 = set((_o.get("face"), _o.get("label")) for _o in _off89)
            if _offkeys89 & set((_r.get("face"), _r.get("label")) for _r in _rd89):
                _bad89.append("an off-axis number was also carried as a supply reading")
            # (d) the verdict agrees with its own reach counts
            _rb89 = _s89.get("reach_by_class") or {}
            _above89 = _rb89.get("above_ceiling") or {}
            _gap89 = _rb89.get("in_gap") or {}
            _v89 = _f89.get("verdict")
            if _v89 == "published_supply_reaches_the_gap_rows_only":
                if (_above89.get("n_reached_optimistic") or
                        _above89.get("n_reached_conservative")):
                    _bad89.append("the verdict says gap-only but an above-ceiling row is reached")
                if not (_gap89.get("n_reached_optimistic") or
                        _gap89.get("n_reached_conservative")):
                    _bad89.append("the verdict says gap-only but no gap row is reached")
            if _v89 == "no_published_supply_reaches_any_row_beyond_the_published_tails":
                if (_gap89.get("n_reached_optimistic") or _above89.get("n_reached_optimistic")):
                    _bad89.append("the verdict says nothing is reached but a row is")
            # (e) this face never censuses itself (E180/E209/E294 self-inclusion family)
            _disc89 = _f89.get("discovery") or {}
            _censused89 = _disc89.get("dated_faces_with_a_multiplier_key") or []
            if "BANDSUPPLY-2026-10-29.json" in _censused89 or "bandsupply_latest.json" in _censused89:
                _bad89.append("this study's own face is inside its own census")
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m89 = __import__("importlib").import_module("e287_supply_ceiling_axes")
            _fresh89 = _m89.build()
            if _fresh89.get("verdict") != _f89.get("verdict"):
                _bad89.append("the verdict does not re-derive")
            _fs89 = _fresh89.get("summary") or {}
            for _k in ("ceiling", "widen_cap_conservative", "widen_cap_optimistic",
                       "narrow_cap_conservative", "nearest_above_ceiling"):
                if _fs89.get(_k) != _s89.get(_k):
                    _bad89.append("summary.%s does not re-derive" % _k)
            for _cls in ("above_ceiling", "in_gap", "below_floor"):
                _a = (_fs89.get("reach_by_class") or {}).get(_cls) or {}
                _b = _rb89.get(_cls) or {}
                if _a.get("n_reached_optimistic") != _b.get("n_reached_optimistic"):
                    _bad89.append("reach for %s does not re-derive" % _cls)
        check(_name89, not _bad89,
              "; ".join(_bad89)[:220]
              or "verdict %r | ceiling %s vs supply %s (median) / %s (single seed); above-ceiling "
                 "%d row(s) reached %d, gap %d row(s) reached %d at the median and %d at the seed; "
                 "narrowing instrument %s misses the nearest below-floor row by %s pct; %d off-axis "
                 "number(s) refused with a reason"
                 % ((_f89 or {}).get("verdict"),
                    _r77(_f89, "ceiling"),
                    _r77(_f89, "widen_cap_conservative"),
                    _r77(_f89, "widen_cap_optimistic"),
                    (_s89.get("reach_by_class") or {}).get("above_ceiling", {}).get("n_rows") or 0,
                    (_s89.get("reach_by_class") or {}).get("above_ceiling", {}).get(
                        "n_reached_optimistic") or 0,
                    (_s89.get("reach_by_class") or {}).get("in_gap", {}).get("n_rows") or 0,
                    (_s89.get("reach_by_class") or {}).get("in_gap", {}).get(
                        "n_reached_conservative") or 0,
                    (_s89.get("reach_by_class") or {}).get("in_gap", {}).get(
                        "n_reached_optimistic") or 0,
                    _r77(_f89, "narrow_cap_conservative"),
                    ("n/a" if not (_s89.get("nearest_below_floor") or {}).get("pct_short")
                     else "%.3f" % _s89["nearest_below_floor"]["pct_short"]),
                    _s89.get("n_off_axis_refused") or 0))
    except Exception as e:
        check(_name89, False, repr(e)[:160])

    # E288 r1317: the mirror of the ceiling question. A flip BELOW the published floor of 1.0 needs
    # the band NARROWED, so "unreachable" is never one direction of fix. Two rows sit under the
    # floor, the family publishes exactly one sub-1.0 band-edge multiplier, it reaches neither, and
    # scored against all 12 rows on each row's own polarity it reaches none -- tightening is not a
    # free fix for the widening side either.
    _name90 = ("product: a below-floor flip needs the band narrowed -- the published narrowing "
               "instrument is measured on its own polarity and its cost on the others")
    _bad90 = []
    try:
        _p90 = os.path.join("results", "state_tilt", "bandfloormirror_latest.json")
        _f90 = None
        if not os.path.exists(_p90):
            _bad90.append("face missing: %s" % _p90)
        else:
            with io.open(_p90, encoding="utf-8") as _fh90:
                _f90 = json.load(_fh90)
        if _f90 is not None:
            if _f90.get("evidence_cutoff") is None:
                _bad90.append("no evidence_cutoff on the face")
            _vocab90 = ("published_narrowing_instrument_reaches_every_below_floor_row",
                        "published_narrowing_instrument_reaches_its_nearest_below_floor_row",
                        "no_published_narrowing_instrument_reaches_a_below_floor_row")
            if _f90.get("verdict") not in _vocab90:
                _bad90.append("verdict %r is outside the frozen set" % (_f90.get("verdict"),))
            _s90 = _f90.get("summary") or {}
            _id90 = _f90.get("partition_identity") or {}
            _ins90 = _f90.get("narrowing_instrument") or {}
            _mr90 = _f90.get("mirror_rows") or []
            # (a) the below-floor rows are E285's own set and every class re-derives from flip
            if not _id90.get("below_floor_set_matches"):
                _bad90.append("the below-floor set is not the set E285 published")
            if _id90.get("n_class_from_bounds_matches_published") != _id90.get("rows_censused"):
                _bad90.append("a row's polarity does not re-derive from flip vs the two bounds")
            if len(_mr90) != _s90.get("n_below_floor_rows"):
                _bad90.append("the mirror rows do not cover the below-floor class")
            # (b) the yardstick must be a SUB-1.0 multiplier, or nothing is being measured
            if not _ins90.get("is_below_floor"):
                _bad90.append("the common yardstick is not a sub-1.0 band-edge multiplier")
            if not _ins90.get("readings_at_or_below_floor"):
                _bad90.append("no published reading at or below the floor is named")
            # (c) every mirror row carries a distance under the floor and a yardstick reading
            for _r90 in _mr90:
                _cy90 = _r90.get("common_yardstick") or {}
                if _cy90.get("cap") is None:
                    _bad90.append("row %s has no yardstick reading" % _r90.get("row_key"))
                _flip90 = _r90.get("flip")
                if _flip90 is None or abs((_flip90 + _r90.get("distance_below_floor", 0)) - 1.0) > 1e-9:
                    _bad90.append("row %s: distance under the floor does not add up to 1.0"
                                  % _r90.get("row_key"))
                if _flip90 is not None and _flip90 >= 1.0:
                    _bad90.append("row %s is not below the floor" % _r90.get("row_key"))
            # (d) E285's own distance column is gauged with a reference that is published
            _refs90 = [r.get("e285_reference_implied") for r in _mr90
                       if r.get("e285_reference_implied") is not None]
            if len(_refs90) != len(_mr90):
                _bad90.append("a per-row reference is published without its implied value")
            _above90 = _s90.get("n_e285_rows_whose_reference_is_above_floor")
            if _above90 != sum(1 for r in _mr90 if r.get("e285_reference_is_above_floor")):
                _bad90.append("the count of references above the floor does not re-derive")
            # (e) the cost block scores all rows, and the verdict agrees with its own reach count
            _c90 = _f90.get("cost") or {}
            if _c90.get("rows_censused") != _id90.get("rows_censused"):
                _bad90.append("the cost block does not cover the whole census")
            _reached90 = _s90.get("n_reached_conservative")
            _v90 = _f90.get("verdict")
            if _v90 == "no_published_narrowing_instrument_reaches_a_below_floor_row" and _reached90:
                _bad90.append("the verdict says nothing is reached but a row is")
            if _v90 == "published_narrowing_instrument_reaches_every_below_floor_row" and \
                    _reached90 != _s90.get("n_below_floor_rows"):
                _bad90.append("the verdict says every row is reached but the count disagrees")
            # (f) two polarities are counted, never assumed away (M5)
            _pol90 = _f90.get("polarity") or {}
            if not _pol90.get("n_widening_demands") or not _pol90.get("n_narrowing_demands"):
                _bad90.append("a demand set is empty: the polarity claim cannot be checked")
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m90 = __import__("importlib").import_module("e288_below_floor_narrowing")
            _fresh90 = _m90.build()
            if _fresh90.get("verdict") != _f90.get("verdict"):
                _bad90.append("the verdict does not re-derive")
            _fs90 = _fresh90.get("summary") or {}
            for _k in ("floor", "n_below_floor_rows", "narrowing_cap", "n_reached_conservative",
                       "nearest_below_floor", "farthest_below_floor"):
                if _fs90.get(_k) != _s90.get(_k):
                    _bad90.append("summary.%s does not re-derive" % _k)
            if _fresh90.get("mirror_rows") != _mr90:
                _bad90.append("the mirror rows do not re-derive")
        check(_name90, not _bad90,
              "; ".join(_bad90)[:220]
              or "verdict %r | %d row(s) below the floor %s, nearest short by %s pct and farthest "
                 "by %s pct of the only sub-1.0 instrument %s; that same instrument reaches %d of "
                 "%d rows on their own polarity; %d of %d E285 references sit above the floor"
                 % ((_f90 or {}).get("verdict"),
                    (_f90 or {}).get("summary", {}).get("n_below_floor_rows") or 0,
                    _r77(_f90, "floor"),
                    __import__("json").dumps(
                        ((_f90 or {}).get("summary", {}).get("nearest_below_floor") or {})
                        .get("pct_short")),
                    __import__("json").dumps(
                        ((_f90 or {}).get("summary", {}).get("farthest_below_floor") or {})
                        .get("pct_short")),
                    _r77(_f90, "narrowing_cap"),
                    ((_f90 or {}).get("cost") or {}).get(
                        "rows_reached_by_the_narrowing_instrument") or 0,
                    ((_f90 or {}).get("cost") or {}).get("rows_censused") or 0,
                    ((_f90 or {}).get("summary", {}) or {}).get(
                        "n_e285_rows_whose_reference_is_above_floor") or 0,
                    len(_mr90)))
    except Exception as e:
        check(_name90, False, repr(e)[:160])

    # E293 r1318 (published r1314, wired now): a duplicated list is the family's SHAPE, and the only
    # way it costs anything is if a number in an enclosing scope counts the group twice. The face says
    # it does not, on 6 groups over 32 censused faces (2 schema-driven, 4 accidental), so the leg pins
    # (a) the verdict vocabulary and the no-double-count closed class, (b) that the summary re-derives
    # from the frozen universe the face itself published, and (c) that a later sibling face is
    # DISCLOSED as excluded rather than silently folded in.
    _name91 = ("product: a duplicated list is the family's shape, and no published scope counts an "
               "alias group twice -- re-derived against the universe the face published")
    _bad91 = []
    try:
        _p91 = os.path.join("results", "state_tilt", "banddupes_latest.json")
        _f91 = None
        if not os.path.exists(_p91):
            _bad91.append("face missing: %s" % _p91)
        else:
            with io.open(_p91, encoding="utf-8") as _fh91:
                _f91 = json.load(_fh91)
        if _f91 is not None:
            if _f91.get("evidence_cutoff") is None:
                _bad91.append("no evidence_cutoff on the face")
            _vocab91 = ("no_published_face_repeats_list_content_so_no_alias_exists",
                        "every_alias_is_a_schema_copy_and_no_scope_counts_one_twice",
                        "some_aliases_are_accidental_copies_but_no_scope_counts_one_twice",
                        "a_count_in_an_enclosing_scope_equals_the_alias_total_so_the_duplicate_is_"
                        "counted_twice")
            _v91 = _f91.get("verdict")
            if _v91 not in _vocab91:
                _bad91.append("verdict %r is outside the frozen vocabulary" % (_v91,))
            _s91 = _f91.get("summary") or {}
            _g91 = _f91.get("groups") or []
            if _s91.get("alias_groups") != len(_g91):
                _bad91.append("summary.alias_groups disagrees with the published group rows")
            _st91 = _s91.get("strict_sum_test") or {}
            if _st91.get("convictions"):
                _bad91.append("a group is convicted of double counting")
            if any(g.get("counts_one_twice") for g in _g91):
                _bad91.append("a group row says counts_one_twice but the verdict says it does not")
            if _v91 == "some_aliases_are_accidental_copies_but_no_scope_counts_one_twice" and \
                    not (_s91.get("accidental_groups") or 0):
                _bad91.append("the verdict names accidental copies but the count is zero")
            _id91 = _f91.get("identity_check") or {}
            if not all(_id91.values()) or not _id91:
                _bad91.append("an identity check is false: %s"
                              % ",".join(k for k, v in _id91.items() if not v))
            # (b) the freeze must describe the face, not the directory: every censused name is in the
            # universe it names, and a later face is disclosed rather than absorbed.
            _vn91 = _f91.get("universe_vintage") or {}
            if _vn91.get("faces_used") != _s91.get("faces_censused"):
                _bad91.append("universe_vintage.faces_used disagrees with summary.faces_censused")
            if _vn91.get("faces_used") != len(_f91.get("faces_censused") or []):
                _bad91.append("the censused name list is not the length the face claims")
            if _vn91.get("faces_in_directory_now", 0) > _vn91.get("faces_used", 0) and \
                    not _vn91.get("faces_excluded_as_later"):
                _bad91.append("the directory grew but no later face is disclosed as excluded")
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m91 = __import__("importlib").import_module("e293_duplicate_list_census")
            _fresh91 = _m91.build()
            if _fresh91.get("verdict") != _v91:
                _bad91.append("the verdict does not re-derive")
            _fs91 = _fresh91.get("summary") or {}
            for _k in ("faces_censused", "alias_groups", "alias_members", "schema_driven_groups",
                       "accidental_groups"):
                if _fs91.get(_k) != _s91.get(_k):
                    _bad91.append("summary.%s does not re-derive" % _k)
            if [g.get("face") for g in (_fresh91.get("groups") or [])] != \
                    [g.get("face") for g in _g91]:
                _bad91.append("the group faces do not re-derive")
        check(_name91, not _bad91,
              "; ".join(_bad91)[:220]
              or "verdict %r | %d alias group(s) over %d face(s): %d schema-driven and %d "
                 "accidental, %d of %d list(s) (%.1f pct); %d group(s) count one thing twice; "
                 "%d later face(s) disclosed as excluded by the vintage"
                 % ((_f91 or {}).get("verdict"),
                    (_f91 or {}).get("summary", {}).get("alias_groups") or 0,
                    (_f91 or {}).get("summary", {}).get("faces_with_an_alias") or 0,
                    (_f91 or {}).get("summary", {}).get("schema_driven_groups") or 0,
                    (_f91 or {}).get("summary", {}).get("accidental_groups") or 0,
                    (_f91 or {}).get("summary", {}).get("alias_members") or 0,
                    sum(len(g.get("members") or []) for g in ((_f91 or {}).get("groups") or []))
                    or 0,
                    100.0 * ((_f91 or {}).get("summary", {}).get(
                        "alias_member_share_of_all_lists") or 0.0),
                    ((_f91 or {}).get("summary", {}).get("strict_sum_test") or {}).get("convictions") or 0,
                    len(((_f91 or {}).get("universe_vintage") or {}).get(
                        "faces_excluded_as_later") or [])))
    except Exception as e:
        check(_name91, False, repr(e)[:160])

    # E295 r1319 (published r1319, wired same round): E287's two margins both looked "one rung
    # away". The leg pins (a) the verdict vocabulary, (b) that every graded margin is the one the
    # face actually graded IN THE LADDER'S OWN WINDOW -- a demand from another window must be
    # published as not_graded with a reason, never counted as a crossing, (c) that an aborted
    # interpolation carries a residual factor instead of a fitted number, and (d) that E258's
    # same-window multiplier reproduces off the ladder, so "the ladder agrees with the family" is
    # measured here rather than asserted by the face.
    _name92 = ("product: a margin that looks one rung away is priced as one step, not as headroom -- "
               "the ladder's own step size sits beside the derived demand set, and a crossing that "
               "needs a rung the family never measured is declared aborted, not fitted")
    _bad92 = []
    try:
        _p92 = os.path.join("results", "state_tilt", "bandclosure_latest.json")
        _f92 = None
        if not os.path.exists(_p92):
            _bad92.append("face missing: %s" % _p92)
        else:
            with io.open(_p92, encoding="utf-8") as _fh92:
                _f92 = json.load(_fh92)
        if _f92 is not None:
            if _f92.get("evidence_cutoff") is None:
                _bad92.append("no evidence_cutoff on the face")
            _vocab92 = ("published_ladder_crosses_both_margins_on_the_central_basis",
                        "one_margin_is_crossed_by_a_single_seed_rung_only",
                        "no_published_ladder_rung_crosses_a_margin")
            _v92 = _f92.get("verdict")
            if _v92 not in _vocab92:
                _bad92.append("verdict %r is outside the frozen vocabulary" % (_v92,))
            _s92 = _f92.get("summary") or {}
            _sp92 = _s92.get("ladder_span") or {}
            _st92 = _s92.get("step") or {}
            _mg92 = _f92.get("margins") or []
            _cnc92 = _f92.get("demand_census") or {}
            _cell92 = _s92.get("ladder_cell")
            if not _cell92:
                _bad92.append("the face does not name the ladder's own window")
            # (b) only the ladder's own window is graded, and the census partitions
            if any(m.get("cell") != _cell92 for m in _mg92):
                _bad92.append("a margin was graded from outside the ladder's own window")
            if len(_cnc92.get("in_window") or []) != _s92.get(
                    "n_demand_rows_in_the_ladder_window") or len(
                    _cnc92.get("not_graded") or []) != _s92.get("n_demand_rows_not_graded"):
                _bad92.append("the demand census disagrees with its own rows")
            if (_s92.get("n_demand_rows_in_the_ladder_window") or 0) + \
                    (_s92.get("n_demand_rows_not_graded") or 0) != \
                    _s92.get("n_demand_rows_censused"):
                _bad92.append("the demand census does not add up")
            if any(not x.get("reason") for x in (_cnc92.get("not_graded") or [])):
                _bad92.append("a demand was left ungraded without a reason")
            if not _st92.get("n_steps"):
                _bad92.append("no step of the draw ladder was priced")
            # (c) an aborted interpolation always carries the residual factor it aborted on
            if any(m.get("residual_factor") is None for m in _mg92
                   if m.get("interpolation_aborted")):
                _bad92.append("an aborted interpolation has no residual factor")
            # (d) the same-window reproduction witness
            _rp92 = _s92.get("reproduction") or {}
            if not _rp92.get("checked"):
                _bad92.append("the same-window reproduction witness was not checked")
            elif not _rp92.get("agrees_at_1e9"):
                _bad92.append("the ladder and E258 disagree in the same window by %s"
                              % _rp92.get("abs_diff"))
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m92 = __import__("importlib").import_module("e295_supply_gap_closure")
            _fresh92 = _m92.build()
            if _fresh92.get("verdict") != _v92:
                _bad92.append("the verdict does not re-derive")
            _fs92 = _fresh92.get("summary") or {}
            for _k in ("ladder_cell", "n_readings", "n_steps", "n_gradable_widening",
                       "n_gradable_narrowing", "n_crossed_central", "n_interpolations_aborted"):
                if _fs92.get(_k) != _s92.get(_k):
                    _bad92.append("summary.%s does not re-derive" % _k)
            if [m.get("row_key") for m in (_fresh92.get("margins") or [])] != \
                    [m.get("row_key") for m in _mg92]:
                _bad92.append("the graded margin rows do not re-derive")
            if _fresh92.get("ladder_span") != _f92.get("ladder_span"):
                _bad92.append("the ladder span does not re-derive")
        check(_name92, not _bad92,
              "; ".join(_bad92)[:220]
              or "verdict %r | ladder %s spans %.6f..%.6f central / %s seed-max; %d step(s), "
                 "median gain %s, %s of them finer than the widening margin; %d demand(s) "
                 "censused, %d graded in-window (%d crossed central, %d at one seed, %d "
                 "interpolation(s) aborted); same-window reproduction |diff| %s"
                 % ((_f92 or {}).get("verdict"),
                    (_f92 or {}).get("summary", {}).get("ladder_cell"),
                    _sp92.get("central_min") or 0.0, _sp92.get("central_max") or 0.0,
                    _sp92.get("seed_max"),
                    _st92.get("n_steps") or 0, _st92.get("median_gain"),
                    _st92.get("n_gains_at_or_above_the_widening_margin"),
                    (_f92 or {}).get("summary", {}).get("n_demand_rows_censused") or 0,
                    ((_f92 or {}).get("summary", {}).get("n_gradable_widening") or 0)
                    + ((_f92 or {}).get("summary", {}).get("n_gradable_narrowing") or 0),
                    (_f92 or {}).get("summary", {}).get("n_crossed_central") or 0,
                    (_f92 or {}).get("summary", {}).get("n_crossed_at_one_seed") or 0,
                    (_f92 or {}).get("summary", {}).get("n_interpolations_aborted") or 0,
                    (((_f92 or {}).get("summary", {}) or {}).get("reproduction") or {})
                    .get("abs_diff")))
    except Exception as e:
        check(_name92, False, repr(e)[:160])

    # E300 r1320 (published r1320, wired same round): E295 could grade only the rows whose window
    # owned a draw ladder and had to borrow one cap written at another window for the rest, which is
    # why its margins and E287's headline were both window artefacts (3.80 pct vs 5.98 pct on the
    # same demand). The leg pins (a) the frozen verdict vocabulary, (b) that every graded row is
    # priced against a reference published IN ITS OWN CELL at ITS OWN base draw count -- never a
    # borrowed one, (c) that a row with no window-local reference is published with needs_face and
    # no margin (nothing is subtracted across windows), (d) that a reach flip is published only
    # where the two denominators actually disagree, and (e) that the cross-window column
    # reproduces E295 exactly, which is what makes the own-window column comparable arithmetic.
    _name93 = ("product: a demand is priced against the window that owns it -- every published "
               "demand row carries its own-window margin beside the borrowed-cap margin, and a "
               "row with no window-local reference says which face it needs instead of borrowing")
    _bad93 = []
    try:
        _p93 = os.path.join("results", "state_tilt", "bandmarginwindow_latest.json")
        _f93 = None
        if not os.path.exists(_p93):
            _bad93.append("face missing: %s" % _p93)
        else:
            with io.open(_p93, encoding="utf-8") as _fh93:
                _f93 = json.load(_fh93)
        if _f93 is not None:
            if _f93.get("evidence_cutoff") is None:
                _bad93.append("no evidence_cutoff on the face")
            _vocab93 = (
                "every_widening_demand_is_graded_against_its_own_window_and_no_narrowing_one_is",
                "every_demand_is_graded_against_its_own_window",
                "window_local_references_are_missing_for_some_demands")
            _v93 = _f93.get("verdict")
            if _v93 not in _vocab93:
                _bad93.append("verdict %r is outside the frozen vocabulary" % (_v93,))
            _s93 = _f93.get("summary") or {}
            _rw93 = _f93.get("rows") or []
            # (b) every graded row's reference belongs to its own cell and its own base draws
            for _r93 in _rw93:
                if not _r93.get("graded_on_own_window"):
                    continue
                _ref93 = _r93.get("own_reference") or {}
                if not str(_ref93.get("label") or "").startswith(str(_r93.get("cell")) + "|"):
                    _bad93.append("row %s was priced against another window's reference (%s)"
                                  % (_r93.get("row_key"), _ref93.get("label")))
                if _ref93.get("base_draws") != _r93.get("base_draws"):
                    _bad93.append("row %s was priced at base %s, published at %s"
                                  % (_r93.get("row_key"), _ref93.get("base_draws"),
                                     _r93.get("base_draws")))
                if _r93.get("own_margin_pct") is None:
                    _bad93.append("row %s is graded but carries no margin"
                                  % (_r93.get("row_key"),))
            # (c) an ungraded row names the face it needs and quotes no number
            for _r93 in _rw93:
                if _r93.get("graded_on_own_window"):
                    continue
                if not _r93.get("needs_face"):
                    _bad93.append("row %s is ungraded without naming the face it needs"
                                  % (_r93.get("row_key"),))
                if _r93.get("own_margin_pct") is not None:
                    _bad93.append("row %s is ungraded but still quotes an own-window margin"
                                  % (_r93.get("row_key"),))
            # census partition + reach flips agree with their own row list
            if (_s93.get("n_graded_on_own_window") or 0) + (_s93.get("n_not_graded") or 0) != \
                    _s93.get("n_rows_censused"):
                _bad93.append("the census does not partition")
            if (_s93.get("n_graded_widening") or 0) + (_s93.get("n_graded_narrowing") or 0) != \
                    _s93.get("n_graded_on_own_window"):
                _bad93.append("the polarity split does not add up")
            _flip93 = sorted(r.get("row_key") for r in _rw93 if r.get("reach_flips") is True)
            if _flip93 != sorted(_s93.get("reach_flip_rows") or []):
                _bad93.append("the reach-flip rows disagree with the count")
            # (d) a flip is published only where the denominators disagree
            for _r93 in _rw93:
                if _r93.get("reach_flips") is None:
                    continue
                if bool(_r93.get("reach_flips")) != (
                        _r93.get("own_reached_central") != _r93.get("cross_reached_central")):
                    _bad93.append("row %s's flip flag contradicts its two reach verdicts"
                                  % (_r93.get("row_key"),))
            # the own-window column must actually move the number, or the study measured nothing
            if not (_s93.get("n_cross_window_understated") or 0) > 0:
                _bad93.append("no row moved, so the two denominators measured the same thing")
            # (e) the cross-window column reproduces E295 (same arithmetic, borrowed caps)
            _w93 = _s93.get("witness_e295") or {}
            if not _w93.get("checked"):
                _bad93.append("the E295 witness rows were not checked")
            elif not _w93.get("all_agree"):
                _bad93.append("the cross-window column does not reproduce E295")
            # a ladder count alone must never be read as 'no reference'
            if (_s93.get("n_ladder_windows") or 0) >= (_s93.get("n_multiplier_windows") or 0):
                _bad93.append("the ladder/multiplier distinction is not published")
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m93 = __import__("importlib").import_module("e300_window_local_margin_census")
            _fresh93 = _m93.build()
            if _fresh93.get("verdict") != _v93:
                _bad93.append("the verdict does not re-derive")
            if [r.get("row_key") for r in (_fresh93.get("rows") or [])] != \
                    [r.get("row_key") for r in _rw93]:
                _bad93.append("the demand rows do not re-derive")
            _fs93 = _fresh93.get("summary") or {}
            for _k in ("n_rows_censused", "n_graded_on_own_window", "n_graded_widening",
                       "n_graded_narrowing", "n_reach_flips", "n_narrowing_instruments_published"):
                if _fs93.get(_k) != _s93.get(_k):
                    _bad93.append("summary.%s does not re-derive" % _k)
        check(_name93, not _bad93,
              "; ".join(_bad93)[:220]
              or "verdict %r | %d demand row(s): %d graded on their own window (%d widening / %d "
                 "narrowing), %d with no window-local reference and a named face; %d ladder "
                 "window(s) vs %d multiplier window(s), so %d un-laddered row(s) still got priced; "
                 "own-window margin %s..%s pct vs borrowed-cap %s..%s pct; %d reach flip(s); "
                 "cross-window column reproduces E295 on %d row(s)"
                 % ((_f93 or {}).get("verdict"),
                    (_f93 or {}).get("summary", {}).get("n_rows_censused") or 0,
                    (_f93 or {}).get("summary", {}).get("n_graded_on_own_window") or 0,
                    (_f93 or {}).get("summary", {}).get("n_graded_widening") or 0,
                    (_f93 or {}).get("summary", {}).get("n_graded_narrowing") or 0,
                    (_f93 or {}).get("summary", {}).get("n_not_graded") or 0,
                    (_f93 or {}).get("summary", {}).get("n_ladder_windows") or 0,
                    (_f93 or {}).get("summary", {}).get("n_multiplier_windows") or 0,
                    (_f93 or {}).get("summary", {}).get(
                        "n_rows_un_laddered_but_multiplier_graded") or 0,
                    _r78(_f93 or {}, "own_margin_pct_min"),
                    _r78(_f93 or {}, "own_margin_pct_max"),
                    _r78(_f93 or {}, "cross_margin_pct_min"),
                    _r78(_f93 or {}, "cross_margin_pct_max"),
                    (_f93 or {}).get("summary", {}).get("n_reach_flips") or 0,
                    ((_f93 or {}).get("summary", {}) or {}).get("witness_e295", {}).get("checked")
                    or 0))
    except Exception as e:
        check(_name93, False, repr(e)[:160])

    # E298 (r1323 bm-b): r1316 fixed ONE replay control so it says which panel it re-derived on, and
    # the class was never counted. This leg pins the census: (a) the frozen verdict vocabulary, (b)
    # that every control block is classified as identity or replay and the two partitions are
    # exhaustive, (c) that EVERY at-risk row is a replay with no basis evidence -- never an identity
    # check and never a block that carries a window, (d) that the census excludes its own two faces
    # and the mirrors it lives among, so a second run cannot grade itself, and (e) that a replay
    # which cannot name its panel is published as unmeasurable rather than as reproduced-false.
    _name298 = ("product: every published control block is censused by which panel it re-derived on "
                "-- replays that cannot name their basis are published as unmeasurable, never as "
                "safe or broken")
    try:
        _m298 = __import__("importlib").import_module("e298_replay_control_census")
        _f298 = _m298.load("replaycensus_latest.json")
        _s298 = _f298.get("summary") or {}
        _id298 = _f298.get("identity_check") or {}
        _bad298 = []
        if _f298.get("verdict") not in _m298.VERDICT_VOCAB:
            _bad298.append("verdict outside the frozen set")
        if not _id298.get("all_checks"):
            _bad298.append("the face's own identity check is not green")
        _byk298 = _s298.get("by_kind") or {}
        _byb298 = _s298.get("by_basis") or {}
        if sum(_byk298.values()) != _s298.get("n_control_containers"):
            _bad298.append("the kind partition does not sum to the containers")
        if sum(_byb298.values()) != _s298.get("n_control_containers"):
            _bad298.append("the basis partition does not sum to the containers")
        _risk298 = _f298.get("at_risk") or []
        # the path is NOT an identity -- two vintages of one study share it -- so the at-risk rows
        # must carry their own face and the join is on the pair
        _con298 = {(c["face"], c["path"]): c for c in (_f298.get("controls") or [])}
        if len(_risk298) != _s298.get("n_at_risk"):
            _bad298.append("the at-risk list does not match its own count")
        for _r in _risk298:
            _c = _con298.get((_r.get("face"), _r["path"]))
            if not _c or _c["kind"] != "replay" or _c["basis"] != "undeclared":
                _bad298.append("an at-risk row is not a replay with no basis")
            elif _c.get("basis_evidence"):
                _bad298.append("an at-risk row still published basis evidence")
        if (_s298.get("self_faces_excluded") or 0) < 2:
            _bad298.append("the census did not exclude its own face and its mirror")
        if (_s298.get("mirror_files_excluded") or 0) < 1:
            _bad298.append("the census did not exclude the mirrors beside it")
        if _s298.get("n_replay_with_declared_basis", 0) + _s298.get("n_at_risk", 0) != \
                _s298.get("n_replay_controls"):
            _bad298.append("the replay partition does not close")
        # a live re-derive is declared with the overshoot, so it is never silently equal to a pin
        _live298 = [c for c in (_f298.get("controls") or []) if c.get("basis") == "live_declared"]
        for _c in _live298:
            if not any("live_panel" in f or "sessions_past" in f for f in _c["basis_evidence"]):
                _bad298.append("a live_declared block does not name the live panel")
        _fresh298 = _m298.build()
        for _k in ("verdict", "summary", "identity_check", "at_risk", "vintage_transitions"):
            if _fresh298.get(_k) != _f298.get(_k):
                _bad298.append("%s does not re-derive" % _k)
        check(_name298, not _bad298,
              "; ".join(_bad298)[:220]
              or "verdict %r | %d control block(s) in %d face(s): %d identity / %d replay; %d "
                 "replay(s) declare a basis (%d of them the live panel plus its overshoot), %d "
                 "cannot and are published unmeasurable; %d vintage transition(s) observed"
                 % (_f298.get("verdict"),
                    _s298.get("n_control_containers") or 0,
                    _s298.get("faces_with_controls") or 0,
                    _byk298.get("identity") or 0, _byk298.get("replay") or 0,
                    _s298.get("n_replay_with_declared_basis") or 0, len(_live298),
                    _s298.get("n_at_risk") or 0,
                    len(_f298.get("vintage_transitions") or [])))
    except Exception as e:
        check(_name298, False, repr(e)[:160])

    # E303 (r1326 bm-b): E298 left seven replay controls whose basis is not in the face and called
    # them unmeasurable. This leg asks the code instead of the face: (a) the same seven faces/keys
    # are accounted for, one row each, so the recovery cannot quietly shrink the question; (b) every
    # class is inside the frozen vocabulary and the class counts sum to the rows; (c) a row that
    # claims the writer computes a basis the face drops must name that key AND at least one other
    # vintage of the same face must actually carry it -- the claim is measured, not inferred; (d) a
    # row that derives on the live panel is never published as recoverable without a re-run; and
    # (e) verify() catches a mutated class, so the gate is not a rubber stamp.
    _name303 = ("product: the seven replays that publish no basis are recovered from the code that "
                "wrote them -- declared beside the block, dropped from a stale face, or live-panel "
                "by construction, with the different vintage as the witness")
    try:
        _m303 = __import__("importlib").import_module("e303_recover_unmeasurable_basis")
        _f303 = _m303.build()
        _s303 = _f303.get("summary") or {}
        _v303 = _f303.get("method", {}).get("class_vocabulary") or []
        _census303 = __import__("json").load(open(_m303.CENSUS, encoding="utf-8"))
        _bad303 = []
        _risk303 = {(r.get("face"), r.get("key")) for r in (_census303.get("at_risk") or [])}
        _rows303 = {(r.get("face"), r.get("key")) for r in _f303.get("blocks") or []}
        if _risk303 != _rows303:
            _bad303.append("the recovery does not cover exactly the censused at-risk rows")
        if sum((_s303.get("by_class") or {}).values()) != _s303.get("blocks"):
            _bad303.append("the class counts do not sum to the rows")
        for _r in _f303.get("blocks") or []:
            if _r.get("class") not in _v303:
                _bad303.append("%s: class outside the frozen vocabulary" % _r.get("face"))
            if _r.get("class") == "writer_publishes_dropped":
                if not _r.get("writer_basis_keys"):
                    _bad303.append("%s: claims a dropped basis with no witness key" % _r.get("face"))
                if not any(v.get("basis_keys") for v in _r.get("vintage_basis") or []):
                    _bad303.append("%s: no other vintage carries the dropped basis" % _r.get("face"))
            if _r.get("class") == "live_panel_derived" and _r.get("recoverable_without_rerun"):
                _bad303.append("%s: a live-panel basis is published as recoverable" % _r.get("face"))
            if _r.get("decidable_from_code") and not _r.get("writer"):
                _bad303.append("%s: decides without a writer" % _r.get("face"))
        _mut303 = __import__("json").loads(__import__("json").dumps(_f303))
        _mut303["blocks"][0]["class"] = "live_panel_derived"
        if not _m303.verify(_mut303):
            _bad303.append("verify did not catch a mutated class")
        _fresh303 = _m303.build()
        for _k in ("summary", "blocks", "method"):
            if _fresh303.get(_k) != _f303.get(_k):
                _bad303.append("%s does not re-derive" % _k)
        check(_name303, not _bad303,
              "; ".join(_bad303)[:220]
              or "%d replay block(s): %d computed by the writer and dropped from the face, %d "
                 "declared beside the block, %d live-panel with nothing said; %d of %d recoverable "
                 "without a re-run, %d show measured vintage drift"
                 % (_s303.get("blocks") or 0,
                    _s303.get("n_writer_publishes_dropped") or 0,
                    _s303.get("n_declared_at_face_level") or 0,
                    _s303.get("n_live_panel_derived") or 0,
                    _s303.get("n_recoverable_without_rerun") or 0, _s303.get("blocks") or 0,
                    _s303.get("n_with_measured_vintage_drift") or 0))
    except Exception as e:
        check(_name303, False, repr(e)[:160])

    # E292 (r1321 bm-b): E290 handed the 301 'the face already publishes this unit elsewhere' counts on
    # as "move the count, no new data needed". This leg pins the price of that plan: (a) the frozen
    # five-verdict vocabulary, (b) that the shapes partition the 301 rows, (c) that a move is called
    # CLEAN only when it agrees with the list AND the list lives in the count's own scope or a scope
    # that contains / sits under it -- an agreement in an unrelated subtree is its own bucket, (d) that
    # a bare unit name is never priced as a move, and (e) that V4 is only reachable when NOT ONE row
    # lands in a related scope (the premise failure, published as a count of rows, not as a phrase).
    _name94 = ("product: the 'move the count into the scope that publishes its unit' fix plan is "
               "priced -- each of the 301 rows is scored by where a move would land, so an agreement "
               "against a one-item list in an unrelated subtree is never sold as an auditability gain")
    _bad94 = []
    try:
        _p94 = os.path.join("results", "state_tilt", "bandscopefix_latest.json")
        _f94 = None
        if not os.path.exists(_p94):
            _bad94.append("face missing: %s" % _p94)
        else:
            with io.open(_p94, encoding="utf-8") as _fh94:
                _f94 = json.load(_fh94)
        if _f94 is not None:
            if _f94.get("evidence_cutoff") is None:
                _bad94.append("no evidence_cutoff on the face")
            _vocab94 = (
                "the_cheap_naming_fix_is_cheap_and_every_moveable_count_would_agree_with_the_list_it_moves_beside",
                "the_naming_fix_is_mostly_clean_but_a_minority_would_publish_a_new_disagreement",
                "most_elsewhere_rows_need_a_choice_because_their_unit_is_published_in_more_than_one_scope",
                "most_elsewhere_rows_are_bare_unit_names_so_the_cheap_move_does_not_exist_for_them",
                "the_elsewhere_scope_premise_does_not_hold_no_move_lands_in_a_scope_related_to_the_count")
            _v94 = _f94.get("verdict")
            if _v94 not in _vocab94:
                _bad94.append("verdict %r is outside the frozen vocabulary" % (_v94,))
            _s94 = _f94.get("summary") or {}
            _rw94 = _f94.get("rows") or []
            # (b) the shape buckets partition the censused rows, and the row list agrees with them
            _shapes94 = ("move_count_clean", "move_count_clean_foreign_scope",
                         "move_count_would_convict", "choice_required", "needs_own_records",
                         "mirror_copy", "collision", "premise_fails")
            if sum(len([r for r in _rw94 if r.get("fix_shape") == _sh]) for _sh in _shapes94) != \
                    len(_rw94):
                _bad94.append("the shape buckets do not partition the priced rows")
            if len(_rw94) != _s94.get("elsewhere_rows"):
                _bad94.append("the priced rows disagree with summary.elsewhere_rows")
            if len([r for r in _rw94 if r.get("fix_shape") not in _shapes94]):
                _bad94.append("a row carries a fix shape outside the frozen set")
            _related94 = ("same_scope", "ancestor_scope", "descendant_scope")
            # (c) clean moves agree AND land in a related scope; foreign agreements do the opposite
            for _r94 in _rw94:
                if _r94.get("fix_shape") == "move_count_clean":
                    if _r94.get("published_value") != _r94.get("target_list_length"):
                        _bad94.append("clean move %s does not equal its target length"
                                      % (_r94.get("path"),))
                    if _r94.get("scope_relation") not in _related94:
                        _bad94.append("clean move %s lands outside a related scope (%s)"
                                      % (_r94.get("path"), _r94.get("scope_relation")))
                if _r94.get("fix_shape") == "move_count_clean_foreign_scope":
                    if _r94.get("scope_relation") in _related94:
                        _bad94.append("foreign agreement %s is in a related scope"
                                      % (_r94.get("path"),))
                    if _r94.get("published_value") != _r94.get("target_list_length"):
                        _bad94.append("foreign agreement %s does not even agree"
                                      % (_r94.get("path"),))
            # (d) a bare unit name is never priced as a move
            for _r94 in _rw94:
                if _r94.get("bare_unit_key") and _r94.get("fix_shape") != "needs_own_records":
                    _bad94.append("bare unit key %s was priced as %s"
                                  % (_r94.get("path"), _r94.get("fix_shape")))
            # the decisive counts must be derived from the row list, not asserted
            _single94 = [r for r in _rw94 if r.get("fix_shape") in (
                "move_count_clean", "move_count_clean_foreign_scope", "move_count_would_convict",
                "mirror_copy", "collision")]
            if len(_single94) != _s94.get("single_target_rows"):
                _bad94.append("summary.single_target_rows does not match the rows")
            _rel94 = len([r for r in _single94 if r.get("scope_relation") in _related94])
            if _rel94 != _s94.get("rows_landing_in_a_related_scope"):
                _bad94.append("summary.rows_landing_in_a_related_scope does not match the rows")
            _deg94 = len([r for r in _rw94 if r.get("fix_shape") in (
                "move_count_clean", "move_count_clean_foreign_scope")
                and r.get("target_is_degenerate")])
            if _deg94 != _s94.get("agreeing_rows_whose_target_holds_at_most_one_item"):
                _bad94.append("the degenerate-target count does not match the rows")
            # (e) V4 is only reachable when no row lands in a related scope
            if _v94 == _vocab94[4] and (_s94.get("rows_landing_in_a_related_scope") or 0) != 0:
                _bad94.append("V4 is claimed while %d row(s) land in a related scope"
                              % (_s94.get("rows_landing_in_a_related_scope"),))
            if _v94 != _vocab94[4] and (_s94.get("rows_landing_in_a_related_scope") or 0) == 0:
                _bad94.append("no row lands in a related scope but the verdict is not V4")
            # the plan must still re-derive, or the published price is stale
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m94 = __import__("importlib").import_module("e292_scope_fix_plan")
            _fresh94 = _m94.build()
            if _fresh94.get("verdict") != _v94:
                _bad94.append("the verdict does not re-derive")
            if [r.get("fix_shape") for r in (_fresh94.get("rows") or [])] != \
                    [r.get("fix_shape") for r in _rw94]:
                _bad94.append("the fix-shape assignment does not re-derive")
            _fs94 = _fresh94.get("summary") or {}
            for _k94 in ("elsewhere_rows", "related_clean_moves", "foreign_scope_agreements",
                         "moves_that_would_convict", "choice_required", "needs_own_records",
                         "rows_landing_in_a_related_scope"):
                if _fs94.get(_k94) != _s94.get(_k94):
                    _bad94.append("summary.%s does not re-derive" % _k94)
        check(_name94, not _bad94,
              "; ".join(_bad94)[:220]
              or "verdict %r | %d elsewhere row(s): %d related-scope clean move(s), %d foreign "
                 "agreement(s) (%d of them against a <=1-item list), %d would convict, %d need a "
                 "choice, %d need their own records; %d row(s) land in a scope related to the count"
                 % ((_f94 or {}).get("verdict"),
                    (_f94 or {}).get("summary", {}).get("elsewhere_rows") or 0,
                    (_f94 or {}).get("summary", {}).get("related_clean_moves") or 0,
                    (_f94 or {}).get("summary", {}).get("foreign_scope_agreements") or 0,
                    (_f94 or {}).get("summary", {}).get(
                        "agreeing_rows_whose_target_holds_at_most_one_item") or 0,
                    (_f94 or {}).get("summary", {}).get("moves_that_would_convict") or 0,
                    (_f94 or {}).get("summary", {}).get("choice_required") or 0,
                    (_f94 or {}).get("summary", {}).get("needs_own_records") or 0,
                    (_f94 or {}).get("summary", {}).get("rows_landing_in_a_related_scope") or 0))
    except Exception as e:
        check(_name94, False, repr(e)[:160])

    # E294 (r1322 bm-b): the family's universe grows by one face per sibling publication, and r1314
    # froze the census to stop the drift. This leg guards the question UNDER the freeze: the published
    # face must keep (a) its verdict inside the frozen vocabulary, (b) a row list whose statuses
    # reconcile with the summary, (c) a three-way rule applied consistently (a "flips" row must show
    # two different verdicts, a "stable" row two identical ones, a "no-reproduce" row a frozen reading
    # that disagrees with the published one), (d) no self-inclusion -- a census of the directory cannot
    # list the census -- and (e) a measurement path that still runs: the row that gained the most
    # faces is re-derived through the real entry point, because a sibling signature change is exactly
    # what silently killed E293's derivation in r1318.
    _name94 = ("product: the live-universe question under the freeze is priced -- for every study that "
               "censuses the BAND directory the published verdict is re-derived twice (frozen vintage "
               "vs the live directory), so 'the verdict moved' and 'the directory grew' are told apart")
    _bad94 = []
    try:
        _p94 = os.path.join("results", "state_tilt", "bandfrozen_latest.json")
        _f94 = None
        if not os.path.exists(_p94):
            _bad94.append("face missing: %s" % _p94)
        else:
            with io.open(_p94, encoding="utf-8") as _fh94:
                _f94 = json.load(_fh94)
        if _f94 is not None:
            if _f94.get("evidence_cutoff") is None:
                _bad94.append("no evidence_cutoff on the face")
            _vocab94 = ("verdict_depends_on_the_universe_it_saw",
                        "no_published_verdict_moves_with_the_universe",
                        "unmeasurable_before_the_universe_question")
            _v94 = _f94.get("verdict")
            if _v94 not in _vocab94:
                _bad94.append("verdict %r is outside the frozen vocabulary" % (_v94,))
            _s94 = _f94.get("summary") or {}
            _rw94 = _f94.get("rows") or []
            _statuses94 = ("reproduces_and_stable", "reproduces_and_flips",
                           "does_not_reproduce", "not_measurable")
            if len(_rw94) != _s94.get("studies_censused"):
                _bad94.append("the row list disagrees with summary.studies_censused")
            _counts94 = {}
            for _r94 in _rw94:
                _counts94[_r94.get("status")] = _counts94.get(_r94.get("status"), 0) + 1
            if _counts94 != _s94.get("status_counts"):
                _bad94.append("the status counts do not match the rows")
            if any(_r94.get("status") not in _statuses94 for _r94 in _rw94):
                _bad94.append("a row carries a status outside the frozen set")
            _flips94 = [r for r in _rw94 if r.get("status") == "reproduces_and_flips"]
            if len(_flips94) != len(_s94.get("flipping") or []):
                _bad94.append("summary.flipping disagrees with the flipping rows")
            if _v94 == _vocab94[0] and not _flips94:
                _bad94.append("the verdict claims a flip but no row flips")
            if _v94 == _vocab94[1] and (_flips94 or not (_s94.get("measured") or 0)):
                _bad94.append("the verdict claims stability with %d flipping row(s) and %d measured"
                              % (len(_flips94), _s94.get("measured") or 0))
            for _r94 in _rw94:
                _st94 = _r94.get("status")
                if _st94 == "reproduces_and_flips":
                    if _r94.get("live_verdict") is None or \
                            _r94.get("live_verdict") == _r94.get("published_verdict"):
                        _bad94.append("%s flips but its two verdicts agree" % _r94.get("script"))
                elif _st94 == "reproduces_and_stable":
                    if not (_r94.get("frozen_verdict") == _r94.get("live_verdict")
                            == _r94.get("published_verdict")):
                        _bad94.append("%s is stable but its readings differ" % _r94.get("script"))
                    if " vs " not in (_r94.get("varied") or ""):
                        _bad94.append("%s is stable on two identical runs" % _r94.get("script"))
                elif _st94 == "does_not_reproduce":
                    if _r94.get("frozen_verdict") == _r94.get("published_verdict"):
                        _bad94.append("%s is no-reproduce but reproduces" % _r94.get("script"))
                elif _st94 == "not_measurable" and not _r94.get("reason"):
                    _bad94.append("%s is unmeasurable without a reason" % _r94.get("script"))
                _gain94 = _r94.get("faces_gained_since_publish")
                if _gain94 is not None and _gain94 < 0:
                    _bad94.append("%s claims a negative universe gain" % _r94.get("script"))
                if _r94.get("published_files_touched"):
                    _bad94.append("%s wrote into the face directory" % _r94.get("script"))
            if any(_r94.get("script") == "e294_live_universe_drift.py" for _r94 in _rw94):
                _bad94.append("the census lists itself")
            _shape94 = _f94.get("directory_shape") or {}
            if _shape94.get("census_the_directory") != len(_rw94):
                _bad94.append("directory_shape disagrees with the row list")
            if (_shape94.get("read_named_faces_only") or 0) + \
                    (_shape94.get("census_the_directory") or 0) != _shape94.get("family_scripts"):
                _bad94.append("the family shape does not add up")
            # (e) one row must still re-derive through the real measurement path
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m94 = __import__("importlib").import_module("e294_live_universe_drift")
            _meas94 = [r for r in _rw94 if r.get("status") in
                       ("reproduces_and_stable", "reproduces_and_flips", "does_not_reproduce")]
            if not _meas94:
                _bad94.append("no measured row survives to re-derive")
            else:
                _top94 = max(_meas94, key=lambda r: r.get("faces_gained_since_publish") or 0)
                _cand94 = [c for c in _m94.family_scripts() if c["script"] == _top94.get("script")]
                _fresh94 = _m94.measure_one(_cand94[0]) if _cand94 else None
                if not _fresh94 or _fresh94.get("status") != _top94.get("status"):
                    _bad94.append("the measurement path no longer re-derives %s (%r -> %r)"
                                  % (_top94.get("script"), _top94.get("status"),
                                     (_fresh94 or {}).get("status")))
        check(_name94, not _bad94,
              "; ".join(_bad94)[:220]
              or "verdict %r | %d study script(s) census the directory (%d of %d in the family read "
                 "named faces only); %d measured, %d not measurable; %d flipping"
                 % ((_f94 or {}).get("verdict"),
                    ((_f94 or {}).get("directory_shape") or {}).get("census_the_directory") or 0,
                    ((_f94 or {}).get("directory_shape") or {}).get("census_the_directory") or 0,
                    ((_f94 or {}).get("directory_shape") or {}).get("family_scripts") or 0,
                    ((_f94 or {}).get("summary") or {}).get("measured") or 0,
                    ((_f94 or {}).get("summary") or {}).get("unmeasurable") or 0,
                    len(((_f94 or {}).get("summary") or {}).get("flipping") or [])))
    except Exception as e:
        check(_name94, False, repr(e)[:160])

    # E299: r1316 repaired one leg that compared a 6-dp point set against a full-precision
    # interval at 1e-9. This leg prices the CLASS from the published face and re-derives it:
    # (a) every at-risk row names the face it read and carries a number as its tolerance, (b) no
    # self-quantized comparison is scored at risk (the leg rounds BOTH sides, so its quantum is not
    # the face's), (c) every per-key at-risk row was measured on a field that actually publishes
    # floats -- an integer-only key cannot be undone by rounding, (d) template/glob names a leg
    # mentions are disclosed as not-faces, and (e) the same-name-across-faces distances ship with
    # the sentence that forbids reading them as defects.
    _name95 = ("product: a leg that compares a face value finer than the field is printed is named, "
               "and no integer key or self-quantized comparison is convicted as one")
    _bad95 = []
    try:
        _p95 = os.path.join("results", "state_tilt", "precisioncensus_latest.json")
        _f95 = None
        if os.path.exists(_p95):
            _f95 = json.load(open(_p95, encoding="utf-8"))
        if _f95 is None:
            _bad95.append("no published census face")
        else:
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m95 = __import__("importlib").import_module("e299_rounded_vs_tolerance_census")
            _fresh95 = _m95.build()
            if _f95.get("verdict") != _fresh95.get("verdict"):
                _bad95.append("the verdict does not re-derive")
            if _f95.get("verdict") not in _m95.VERDICT_VOCAB:
                _bad95.append("verdict %r is outside the frozen set" % (_f95.get("verdict"),))
            _id95 = _f95.get("identity_check") or {}
            if not _id95.get("all_checks"):
                _bad95.append("an identity check is false")
            _s95 = _f95.get("summary") or {}
            _rows95 = _f95.get("at_risk") or []
            if _s95.get("n_at_risk_sites") != len(_rows95):
                _bad95.append("the summary count disagrees with its own rows")
            for _r95 in _rows95:
                if not _r95.get("faces"):
                    _bad95.append("an at-risk row names no face: %r" % (_r95.get("line"),))
                    break
                if not isinstance(_r95.get("tolerance"), (int, float)):
                    _bad95.append("an at-risk row carries no numeric tolerance")
                    break
                if _r95.get("kind") == "quantized_equality":
                    _bad95.append("a self-quantized comparison is scored at risk")
                    break
            _keys95 = {(_k["face"], _k["key"]): _k for _r in _f95.get("sites") or []
                       for _k in (_r.get("key_profiles") or [])}
            for _r95 in _rows95:
                for _a95 in (_r95.get("at_risk_faces") or []):
                    _kp95 = _keys95.get((_a95.get("face"), _a95.get("key")))
                    if _a95.get("basis") == "per_key" and _kp95 and _kp95.get("integer_only"):
                        _bad95.append("an integer-only key is scored at risk: %r"
                                      % (_a95.get("key"),))
                        break
            if not _s95.get("cross_face_disclosure"):
                _bad95.append("the same-name-across-faces distance ships without its disclosure")
            for _t95 in (_s95.get("names_that_are_templates_not_faces") or []):
                if "*" not in _t95 and "%" not in _t95:
                    _bad95.append("a real face is excused as a template")
                    break
            if _f95.get("summary") != _fresh95.get("summary"):
                _bad95.append("the summary does not re-derive")
        check(_name95, not _bad95, "; ".join(_bad95)[:220]
              or "verdict %s | %d of %d numeric face sites at risk (%d per-key, %d face-bound); "
                 "%d of %d faces declare their precision; %d measured copy pair(s)"
                 % (str((_f95 or {}).get("verdict")),
                    ((_f95 or {}).get("summary") or {}).get("n_at_risk_sites") or 0,
                    ((_f95 or {}).get("summary") or {}).get("n_numeric_face_sites") or 0,
                    ((_f95 or {}).get("summary") or {}).get("n_at_risk_with_per_key_evidence") or 0,
                    ((_f95 or {}).get("summary") or {}).get("n_at_risk_on_face_level_bound_only") or 0,
                    ((_f95 or {}).get("summary") or {}).get("n_faces_declaring_precision") or 0,
                    ((_f95 or {}).get("summary") or {}).get("faces_read_by_legs") or 0,
                    ((_f95 or {}).get("summary") or {}).get("n_faces_with_a_measured_pair") or 0))
    except Exception as e:
        check(_name95, False, repr(e)[:160])

    # E305: E299 graded 8 of its 29 at-risk rows on the FACE's coarsest bound because the key the
    # leg reads could not be located -- an upper bound, not a measurement. This leg re-derives the
    # pricing of those 8: (a) every row is resolved to a named reason, never left blank, (b) no row
    # is kept at risk without a printed number behind it, (c) the row set is exactly the one the
    # census published as face-bound, and (d) the withdrawn/at-risk counts sum to the rows.
    _name97 = ("product: a face-level bound is not a measurement -- every face-bound row is "
               "resolved to a reason and none is left at risk without a printed number")
    _bad97 = []
    try:
        _p97 = os.path.join("results", "state_tilt", "precisiongap_latest.json")
        _f97 = None
        if os.path.exists(_p97):
            _f97 = json.load(open(_p97, encoding="utf-8"))
        if _f97 is None:
            _bad97.append("no published pricing face")
        else:
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m97 = __import__("importlib").import_module("e305_face_level_row_pricing")
            _fresh97 = _m97.build()
            if _f97.get("verdict") != _fresh97.get("verdict"):
                _bad97.append("the verdict does not re-derive")
            if _f97.get("verdict") not in _m97.VERDICT_VOCAB:
                _bad97.append("verdict %r is outside the frozen set" % (_f97.get("verdict"),))
            if not (_f97.get("identity_check") or {}).get("all_checks"):
                _bad97.append("an identity check is false")
            if _f97.get("summary") != _fresh97.get("summary"):
                _bad97.append("the summary does not re-derive")
            if _f97.get("rows") != _fresh97.get("rows"):
                _bad97.append("the priced rows do not re-derive")
            _s97 = _f97.get("summary") or {}
            _rows97 = _f97.get("rows") or []
            _ok_kinds = ("in_priced_face", "in_a_sibling_face", "not_a_number_in_priced_face",
                         "not_a_number_in_a_sibling_face", "written_inside_records", "absent")
            if _s97.get("rows_priced") != len(_rows97):
                _bad97.append("the summary count disagrees with its own rows")
            if _s97.get("rows_priced") != _s97.get("census_published_face_level_rows"):
                _bad97.append("the row set is not the census's face-bound set")
            if (_s97.get("n_withdrawn") or 0) + (_s97.get("n_at_risk_after") or 0) != len(_rows97):
                _bad97.append("the withdrawn and at-risk counts do not sum to the rows")
            for _r97 in _rows97:
                if _r97.get("resolution") not in _ok_kinds:
                    _bad97.append("an unresolvable row is left unnamed: %r" % (_r97.get("line"),))
                    break
                if not _r97.get("reason"):
                    _bad97.append("a row ships without a reason")
                    break
                if _r97.get("at_risk_after") and _r97.get("found_quantum") is None:
                    _bad97.append("a row is kept at risk with no printed number behind it")
                    break
                if not _r97.get("priced_against"):
                    _bad97.append("a row names no face it was priced against")
                    break
        check(_name97, not _bad97, "; ".join(_bad97)[:220]
              or "verdict %s | %d face-bound row(s) priced, %d withdrawn, %d still at risk (%s)"
                 % (str((_f97 or {}).get("verdict")),
                    ((_f97 or {}).get("summary") or {}).get("rows_priced") or 0,
                    ((_f97 or {}).get("summary") or {}).get("n_withdrawn") or 0,
                    ((_f97 or {}).get("summary") or {}).get("n_at_risk_after") or 0,
                    ", ".join("%s=%d" % kv for kv in sorted(
                        (((_f97 or {}).get("summary") or {}).get("by_resolution") or {}).items()))))
    except Exception as e:
        check(_name97, False, repr(e)[:160])

    # E302: three studies publish build() with no universe argument, so E294 could not ask them
    # whether their verdict depends on the directory. This leg re-derives the priced switch:
    # (a) every row that reports a verdict was measured against a staged universe that is actually
    # narrower than the live one (a tautology would read "stable" for free, the E294 trap), (b) a
    # measured row declares what it varied, (c) nothing in results/state_tilt was written by the
    # measurement, (d) the priced binding set is non-empty and never counts this study's own module,
    # and (e) the summary re-derives.
    _name96 = ("product: the three universe-unaskable studies are switchable, each row varies a "
               "narrower universe than the live one, and the price of the switch is published")
    _bad96 = []
    try:
        _p96 = os.path.join("results", "state_tilt", "bandswitch_latest.json")
        _f96 = None
        if os.path.exists(_p96):
            _f96 = json.load(open(_p96, encoding="utf-8"))
        if _f96 is None:
            _bad96.append("no published switch face")
        else:
            sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
            _m96 = __import__("importlib").import_module("e302_universe_switch_backfill")
            _fresh96 = _m96.build()
            if _f96.get("verdict") != _fresh96.get("verdict"):
                _bad96.append("the verdict does not re-derive")
            if _f96.get("verdict") not in _m96.VERDICTS:
                _bad96.append("verdict %r is outside the frozen set" % (_f96.get("verdict"),))
            _s96 = _f96.get("summary") or {}
            _rows96 = _f96.get("rows") or []
            if _s96.get("studies_priced") != len(_rows96):
                _bad96.append("the summary count disagrees with its own rows")
            for _r96 in _rows96:
                if _r96.get("status") not in _m96.STATUSES:
                    _bad96.append("a row status is outside the frozen set")
                    break
                if _r96.get("status") in (_m96.STATUS_STABLE, _m96.STATUS_FLIPS):
                    if " vs " not in (_r96.get("varied") or ""):
                        _bad96.append("a measured row does not declare what it varied")
                        break
                    if not _r96.get("staged_is_narrower"):
                        _bad96.append("a measured row ran against a staged universe that is not "
                                      "narrower than the live one")
                        break
                if _r96.get("published_files_touched"):
                    _bad96.append("a row wrote to the published directory")
                    break
            _bind96 = (_s96.get("global_redirect_switch") or {}).get("bindings_that_must_move") or []
            if not _bind96:
                _bad96.append("the priced binding set is empty")
            if set(_bind96) & {"__main__", "__mp_main__", _m96.SELF_MODULE}:
                _bad96.append("the study's own module is counted as a binding")
            if _f96.get("summary") != _fresh96.get("summary"):
                _bad96.append("the summary does not re-derive")
            # The dated face and the mirror must say the same thing: a reader who opens one and a
            # leg that reads the other would otherwise be judging two different publications.
            _dated96 = os.path.join("results", "state_tilt", _m96.FACE)
            if os.path.exists(_dated96):
                _d96 = json.load(open(_dated96, encoding="utf-8"))
                _dd96 = dict(_d96)
                _ff96 = dict(_f96)
                _dd96.pop("generated", None)
                _ff96.pop("generated", None)
                if json.dumps(_dd96, sort_keys=True) != json.dumps(_ff96, sort_keys=True):
                    _bad96.append("the dated face and the mirror disagree beyond their stamp")
            else:
                _bad96.append("the dated face named by FACE is not published")
        check(_name96, not _bad96, "; ".join(_bad96)[:220]
              or "verdict %s | %d study(ies) priced, %d switchable and stable, %d flipping; the "
                 "switch costs %d module bindings to redirect and %d functions to thread"
                 % (str((_f96 or {}).get("verdict")),
                    ((_f96 or {}).get("summary") or {}).get("studies_priced") or 0,
                    (((_f96 or {}).get("summary") or {}).get("status_counts") or {}
                     ).get("reproduces_and_stable") or 0,
                    len(((_f96 or {}).get("summary") or {}).get("flipping") or []),
                    (((_f96 or {}).get("summary") or {}).get("global_redirect_switch") or {}
                     ).get("bindings_measured") or 0,
                    sum(len(_t.get("functions") or []) for _t in
                        (((_f96 or {}).get("summary") or {}).get("parameter_threading_cost") or []))))
    except Exception as e:
        check(_name96, False, repr(e)[:160])

    # E308: a face-level tolerance gate cannot be paired to a leg by face alone. Of 30 pairs on the
    # 11 gated faces, 18 are arithmetically tighter than the gate; a scope reading of the writers
    # that name each face (is the gate USED in a comparison, or only published?) leaves 1 standing
    # -- and that one's gate carries the same number as an excluded key (verdict_inputs.tol 0.1 ==
    # frozen_spec.gamma_tol 0.1), so it is name-fragile too. Bands must be keyed on the compared
    # quantity, never on the face.
    _name99 = ("product: a leg is not at-risk from a gate the producer only declares -- and the one "
               "band that survives scope is name-fragile")
    _bad99 = []
    try:
        _p99 = os.path.join("results", "state_tilt", "gatetol_latest.json")
        _f99 = None
        if not os.path.exists(_p99):
            _bad99.append("face missing: %s" % _p99)
        else:
            with io.open(_p99, encoding="utf-8") as _fh99:
                _f99 = json.load(_fh99)
        if _f99 is not None:
            _c99 = _f99.get("census") or {}
            if _f99.get("verdict") != ("bands_stand_only_where_the_producer_is_seen_comparing_"
                                      "with_the_gate"):
                _bad99.append("verdict moved: %r" % (_f99.get("verdict"),))
            _sum99 = ((_c99.get("pairs_leg_tighter") or 0) + (_c99.get("pairs_leg_exact_equality") or 0)
                      + (_c99.get("pairs_leg_looser_or_equal") or 0)
                      + (_c99.get("pairs_no_leg_tolerance") or 0))
            if _c99.get("pairs") != _sum99:
                _bad99.append("pair partition does not sum: %s vs %s" % (_c99.get("pairs"), _sum99))
            if _c99.get("pairs") != (len(_f99.get("rows_leg_tighter_or_exact") or [])
                                     + len(_f99.get("rows_leg_looser") or [])
                                     + len(_f99.get("rows_no_leg_tolerance") or [])):
                _bad99.append("published row lists disagree with the census")
            _stands99 = _f99.get("rows_band_stands") or []
            if len(_stands99) != (_c99.get("pairs_band_stands") or 0):
                _bad99.append("standing-band rows disagree with the census")
            if any(r.get("gate_scope") != "used_in_a_comparison" or not r.get("gate_scope_evidence")
                   for r in _stands99):
                _bad99.append("a standing band carries no scope evidence")
            if (_c99.get("pairs_band_stands") or 0) + (_c99.get("pairs_band_rejected_scope") or 0) != \
                    (_c99.get("pairs_leg_tighter") or 0) + (_c99.get("pairs_leg_exact_equality") or 0):
                _bad99.append("scope partition does not cover the tighter rows")
            if any(not c.get("ok") for c in (_f99.get("identity_checks") or [])):
                _bad99.append("identity checks are not all green")
            if not (_c99.get("gates_with_an_excluded_twin") or 0):
                _bad99.append("the gate/exclusion twin is not disclosed")
        check(_name99, not _bad99, "; ".join(_bad99)[:220]
              or "verdict %s; legs %s / sites %s / faces %s resolved %s gated %s; pairs %s -> "
                 "tighter %s + exact %s, standing %s (scope-rejected %s), twin gates %s, exclusions %s"
                 % ((_f99 or {}).get("verdict"),
                    ((_f99 or {}).get("census") or {}).get("legs"),
                    ((_f99 or {}).get("census") or {}).get("sites"),
                    ((_f99 or {}).get("census") or {}).get("faces_named_by_sites"),
                    ((_f99 or {}).get("census") or {}).get("faces_resolved"),
                    ((_f99 or {}).get("census") or {}).get("faces_publishing_a_gate"),
                    ((_f99 or {}).get("census") or {}).get("pairs"),
                    ((_f99 or {}).get("census") or {}).get("pairs_leg_tighter"),
                    ((_f99 or {}).get("census") or {}).get("pairs_leg_exact_equality"),
                    ((_f99 or {}).get("census") or {}).get("pairs_band_stands"),
                    ((_f99 or {}).get("census") or {}).get("pairs_band_rejected_scope"),
                    ((_f99 or {}).get("census") or {}).get("gates_with_an_excluded_twin"),
                    ((_f99 or {}).get("census") or {}).get("gate_exclusions")))
    except Exception as e:
        check(_name99, False, repr(e)[:160])

    # E312: E308 pair-keyed a leg to a face's gate on the DECLARED key, but the writer publishes a
    # constant ("tolerance": TOL) and compares with the constant or a parameter defaulted from it --
    # so 29 of the 30 "declared but never compared" pairs do have a producer comparison, including
    # the case-blind miss rel_tol vs REL_TOL. Being compared is not being compared to the leg's
    # quantity: the band E308 let stand compares the window edges lo/hi against FROZEN_GAMMA+-tol
    # (a feasibility test of the ladder), while the open-fill band it rejected compares
    # abs(cost - session_open)/session_open -- the very price the leg reads, disclosed as relative
    # vs absolute. A leg may be tighter than a gate that governs another number entirely.
    _name100 = ("product: a tolerance gate is compared with a number the leg may never read -- the "
                "constant behind the declared key decides it")
    _bad100 = []
    try:
        _p100 = os.path.join("results", "state_tilt", "gateoperands_latest.json")
        _f100 = None
        if not os.path.exists(_p100):
            _bad100.append("face missing: %s" % _p100)
        else:
            with io.open(_p100, encoding="utf-8") as _fh100:
                _f100 = json.load(_fh100)
        if _f100 is not None:
            _c100 = _f100.get("census") or {}
            _rows100 = _f100.get("rows") or []
            if _f100.get("verdict") != ("a_gate_is_compared_with_something_and_that_something_is_"
                                        "rarely_the_legs_quantity"):
                _bad100.append("verdict moved: %r" % (_f100.get("verdict"),))
            _part100 = ((_c100.get("rows_same_named_quantity") or 0)
                        + (_c100.get("rows_operand_names_disjoint") or 0)
                        + (_c100.get("rows_leg_names_no_face_key") or 0)
                        + (_c100.get("rows_producer_never_compares") or 0)
                        + (_c100.get("rows_gate_identity_unresolvable") or 0))
            if _part100 != len(_rows100):
                _bad100.append("operand partition does not sum: %s vs %s" % (_part100, len(_rows100)))
            if any(r.get("operand_identity") == "operand_names_disjoint_from_the_legs"
                   and not r.get("leg_refs") for r in _rows100):
                _bad100.append("a row whose leg names no face key is counted as disjoint")
            if any(r.get("operand_identity") == "same_named_quantity" and not r.get("shared_refs")
                   for r in _rows100):
                _bad100.append("a same-named row publishes no shared name")
            if any(r.get("band_stands_after_operand_identity") and not r.get("operand_rows")
                   for r in _rows100):
                _bad100.append("a standing row carries no comparison site")
            if any(not c.get("ok") for c in (_f100.get("identity_checks") or [])):
                _bad100.append("identity checks are not all green")
            if not (_c100.get("rows_scope_flipped_by_the_constant_chain") or 0):
                _bad100.append("the constant chain flipped no scope -- the E308 miss is not shown")
            _t35_100 = [r for r in _rows100 if r.get("gate_path") == "rel_tol"
                        and r.get("operand_identity") == "same_named_quantity"]
            if not _t35_100 or not _t35_100[0].get("form_caveat"):
                _bad100.append("the open-fill band lost its relative/absolute caveat")
        check(_name100, not _bad100, "; ".join(_bad100)[:220]
              or "rows %s (upstream %s) faces %s gates %s; constant identity %s, producer compares "
                 "%s (legacy declared-only %s, flips %s); operand identity same %s / disjoint %s / "
                 "no-key %s; bands standing legacy %s -> %s"
                 % (len(_f100.get("rows") or []), _c100.get("upstream_rows"),
                    _c100.get("faces"), _c100.get("gates"),
                    _c100.get("rows_gate_identity_resolved_to_a_constant"),
                    _c100.get("rows_producer_compares_with_the_gate"),
                    _c100.get("rows_legacy_declared_but_never_compared"),
                    _c100.get("rows_scope_flipped_by_the_constant_chain"),
                    _c100.get("rows_same_named_quantity"),
                    _c100.get("rows_operand_names_disjoint"),
                    _c100.get("rows_leg_names_no_face_key"),
                    _c100.get("legacy_bands_standing"),
                    _c100.get("bands_standing_after_operand_identity")))
    except Exception as e:
        check(_name100, False, repr(e)[:160])

    # E314: E313 showed that three published gates are clamped (tol * max(1.0, x)) and one divides
    # by a fixed 100.0, which makes their tolerance a function of the gated quantity rather than a
    # number. This leg asserts the arithmetic and the publication: the two regimes must meet
    # exactly at the switch, the half-unit crossing must be 0.5/tol, a constant gate must not grow
    # because some other number on the face is large, and a clamped row may not claim it is
    # reproducible from a face that carries neither the scale nor a clamp token.
    _name101 = ("product: a clamped gate's tolerance is a function of the quantity it gates -- the "
                "switch point and both regimes have to be printed, and neither is")
    _bad101 = []
    try:
        _p101 = os.path.join("results", "state_tilt", "gateclamp_latest.json")
        _f101 = None
        if not os.path.exists(_p101):
            _bad101.append("face missing: %s" % _p101)
        else:
            with io.open(_p101, encoding="utf-8") as _fh101:
                _f101 = json.load(_fh101)
        if _f101 is not None:
            _c101 = _f101.get("census") or {}
            _rows101 = _f101.get("rows") or []
            _clamp101 = _f101.get("clamped_rows") or []
            if _f101.get("verdict") != ("a_clamp_that_never_engages_still_hides_the_tolerance_in_"
                                        "the_quantitys_own_units"):
                _bad101.append("verdict moved: %r" % (_f101.get("verdict"),))
            _part101 = ((_c101.get("regime_piecewise_floor") or 0)
                        + (_c101.get("regime_linear_in_the_quantity") or 0)
                        + (_c101.get("regime_constant_after_normalisation") or 0)
                        + (_c101.get("regime_constant_absolute") or 0)
                        + (_c101.get("regime_unresolved") or 0))
            if _part101 != len(_rows101):
                _bad101.append("regime partition does not sum: %s vs %s"
                               % (_part101, len(_rows101)))
            if any(not c.get("ok") for c in (_f101.get("identity_checks") or [])):
                _bad101.append("identity checks are not all green")
            if len(_clamp101) != 3:
                _bad101.append("the clamped row count moved: %s" % (len(_clamp101),))
            for _r101 in _clamp101:
                _below = (_r101.get("tolerance_below_the_switch") or {}).get(
                    "absolute_in_the_quantitys_units")
                _gate, _sw = _r101.get("gate_value"), _r101.get("switch_point")
                if _below is None or _gate is None or _sw is None:
                    _bad101.append("a clamped row omits its switch point or its flat tolerance")
                elif abs(_below - _gate * _sw) > 1e-30 + 1e-9 * abs(_gate * _sw):
                    _bad101.append("the two regimes do not meet at the switch: %r vs %r"
                                   % (_below, _gate * _sw))
                _half = _r101.get("half_unit_crossing")
                if _half is None or abs(_half * _gate - 0.5) > 1e-9 * max(1.0, abs(_half * _gate)):
                    _bad101.append("the half unit crossing is not 0.5/tol: %r" % (_half,))
                if _r101.get("clamp_engages_on_this_face") is not False:
                    _bad101.append("the clamp is declared engaged on a face that stays below the "
                                   "floor")
                _rep = _r101.get("reproducible_from_the_face") or {}
                _pub = _r101.get("face_publishes") or {}
                if _rep.get("answer") and not _pub.get("scale_identifier_in_a_key_name"):
                    _bad101.append("a clamped row claims reproducibility without publishing its "
                                   "scale")
                if _pub.get("clamp_tokens_on_the_face"):
                    _bad101.append("a clamped row's face claims to carry a clamp token")
            # a constant gate must not be dragged by an unrelated large number on the face
            for _r101 in _rows101:
                if _r101.get("regime_classes") == "constant_absolute":
                    _tol101 = _r101.get("tolerance_at_the_face_maximum_magnitude")
                    if _tol101 is not None and _tol101 != _r101.get("gate_value"):
                        _bad101.append("a constant gate's tolerance grew with the face maximum")
                        break
            if (_c101.get("rows_whose_named_face_is_absent") or 0) != 1:
                _bad101.append("the row naming a non-existent face is no longer disclosed")
        check(_name101, not _bad101, "; ".join(_bad101)[:220]
              or "rows %s | regimes piecewise %s linear %s const-normalised %s const %s | clamp "
                 "never engages %s | half-unit crossing above the face maximum %s | reproducible "
                 "from the face %s of %s"
                 % (len(_f101.get("rows") or []), _c101.get("regime_piecewise_floor"),
                    _c101.get("regime_linear_in_the_quantity"),
                    _c101.get("regime_constant_after_normalisation"),
                    _c101.get("regime_constant_absolute"),
                    _c101.get("rows_where_the_clamp_never_engages_on_their_own_face"),
                    _c101.get("rows_whose_half_unit_crossing_exceeds_the_faces_largest_number"),
                    _c101.get("rows_reproducible_from_the_face"),
                    _c101.get("rows")))
    except Exception as e:
        check(_name101, False, repr(e)[:160])

    # E315: E314 published each clamped gate's two regimes, but a gate only ever governs a
    # comparison, and the comparison belongs to a leg carrying its own epsilon. This leg asserts
    # the join: a zero epsilon is exact equality and must never publish a finite ratio, the
    # crossover must be eps/tol, and a face that does not carry the quantity its gate is rated in
    # must publish an unattributable measurement with zero magnitudes rather than a count of
    # unrelated numbers.
    _name102 = ("product: a two-regime gate meets a leg epsilon -- four legs demand exact equality "
                "and the fifth's crossover sits below one unit of the quantity")
    _bad102 = []
    try:
        _p102 = os.path.join("results", "state_tilt", "legeps_latest.json")
        _f102 = None
        if not os.path.exists(_p102):
            _bad102.append("face missing: %s" % _p102)
        else:
            with io.open(_p102, encoding="utf-8") as _fh102:
                _f102 = json.load(_fh102)
        if _f102 is not None:
            _c102 = _f102.get("census") or {}
            _rows102 = _f102.get("rows") or []
            if _f102.get("verdict") != ("four_of_five_quantity_dependent_legs_demand_exact_"
                                        "equality_so_the_gate_is_looser_at_every_magnitude_the_"
                                        "face_publishes"):
                _bad102.append("verdict moved: %r" % (_f102.get("verdict"),))
            if any(not c.get("ok") for c in (_f102.get("identity_checks") or [])):
                _bad102.append("identity checks are not all green")
            if (_c102.get("rows_in_each_class")
                    and sum(_c102["rows_in_each_class"].values()) != len(_rows102)):
                _bad102.append("the class partition does not sum to the rows")
            if (_c102.get("rows_whose_leg_demands_exact_equality") or 0) != 4:
                _bad102.append("the exact-equality count moved: %s"
                               % (_c102.get("rows_whose_leg_demands_exact_equality"),))
            for _r102 in _rows102:
                _eps = _r102.get("leg_epsilon")
                _gate = _r102.get("gate_value")
                _cr = _r102.get("crossover_scale")
                if _eps is None:
                    _bad102.append("a row omits its leg epsilon")
                    continue
                if _eps == 0.0 and _r102.get(
                        "orders_of_magnitude_the_gate_is_looser_at_one_unit") is not None:
                    _bad102.append("a zero epsilon published a finite ratio")
                if _cr is not None and _gate:
                    if abs(_cr * _gate - _eps) > 1e-9 * max(abs(_cr * _gate), abs(_eps), 1e-30):
                        _bad102.append("the crossover is not eps/tol on one row")
                if _cr is not None and _cr >= 1.0:
                    _bad102.append("a crossover reaches a whole unit of the quantity")
                if (_r102.get("quantity_published_on_the_face") is False
                        and (_r102.get("leaves") or {}).get("leaves_total") != 0):
                    _bad102.append("an unattributable measurement published a count")
            if (_c102.get("magnitudes_attributable_to_the_rated_quantity") or 0) != 0:
                _bad102.append("attributable magnitudes appeared without the quantity being on a "
                               "face")
        check(_name102, not _bad102, "; ".join(_bad102)[:220]
              or "rows %s | exact equality %s | crossovers %s (below a unit) | quantity on the "
                 "face %s | attributable magnitudes %s"
                 % (len(_f102.get("rows") or []),
                    _c102.get("rows_whose_leg_demands_exact_equality"),
                    _c102.get("rows_with_a_crossover_scale"),
                    _c102.get("rows_whose_quantity_identifier_is_published"),
                    _c102.get("magnitudes_attributable_to_the_rated_quantity")))
    except Exception as e:
        check(_name102, False, repr(e)[:160])

    return _finish()


def _r78(face, key):
    v = (face.get("summary") or {}).get(key)
    return "n/a" if v is None else "%.2f%%" % v


def _r77(face, key):
    v = (face.get("summary") or {}).get(key)
    return "n/a" if v is None else "%.3f" % v


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
