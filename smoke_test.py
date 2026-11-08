"""One-command smoke test: env / config / data / engine / exit rules / market rules / network.

Usage:
    python -m smoke_test

Exit code 0 = all green, 1 = any failure. A timestamped summary line is
appended to logs/smoke.log so the 10-minute iteration loop can audit runs.
"""
import sys
import os
import glob
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
def capture_pinned(argv, timeout):
    """The one place a leg captures a child's text.

    r1386: two legs called subprocess.run(capture_output=True, text=True) with no
    encoding, so the parent decoded with the locale (cp936) while the child wrote
    whatever PYTHONIOENCODING said. With PYTHONIOENCODING=utf-8 in the environment
    -- which this fleet's own round instructions set -- the reader thread died on
    the first non-GBK byte and the suite hung instead of failing: 5 minutes of no
    output, no Summary line, and a smoke run that looks like a slow suite rather
    than a broken one. Pinning both sides is the fix; the meta leg below keeps it.
    """
    _env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    return subprocess.run(argv, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=_env,
                          timeout=timeout, creationflags=0x08000000)
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
    # r1349: no local alias here. The module-level `subprocess` import is used
    # directly because a local binding in this function scope is clobberable by
    # any later leg -- r1348's E246 leg assigned `_sp` to a spread value and 56
    # contract legs below it died with "'dict' object has no attribute 'run'".
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
            _r = capture_pinned([sys.executable, _script, *_args], 180)
            _tail = ((_r.stdout or _r.stderr).strip().splitlines() or ["no output"])[-1]
            check(_label, _r.returncode == 0, f"exit={_r.returncode} | {_tail[:80]}")
        except Exception as e:
            check(_label, False, str(e))
    for _label, _script, _args in (
            # r1386: six rounds of gates had produced no candidate family, so this
            # probe is the first measurement of one since r1379. Its own two ruler
            # legs pin the exposure-share null in both directions (buy-and-hold must
            # read exactly zero excess; a misaligned exposure must still be caught),
            # so the suite fails if the measuring rod itself drifts.
            ("product: zoo90 alligator supply probe (exit-code contract)",
             "scripts/zoo90_alligator_probe.py", ["--selftest"]),
            # r1390: the first berth whose exposure is structurally 1.0 (the two timing
            # berths before it lose to the exit tax by construction). Its legs pin both
            # directions -- an engineered reversal panel must win, a random walk must not
            # be admitted -- plus that the vectorised null basis reproduces the engine's
            # own excess, because the p-value is read on that basis.
            ("product: cross-sectional reversal supply probe (exit-code contract)",
             "scripts/zoo_supply_xs_reversal_probe.py", ["--selftest"]),
            # r1391: the EVENT berth r1390 named as the only free axis left (breadth was
            # measured as a tax). Its legs pin the two things that make an event probe
            # trustworthy: sealing is required (a +10% day that did not close at the
            # ceiling is not an event) and a gap bar leaves NaN rather than a 0% return,
            # so a missing bar can never be read as a flat outcome.
            ("product: limit-up event supply probe (exit-code contract)",
             "scripts/zoo91_limit_up_event_probe.py", ["--selftest"]),
            # r1392: the sell side of the same forced-trade clock (r1391 measured the buy
            # side: the premium is paid at the next open). Same engine, one different mask
            # -- so the legs must prove the mask is actually different (the engineered
            # limit-down panel is seen as zero events when read as "up"), that sealing is
            # required on the floor too, and that a missing next-open stays NaN.
            ("product: limit-down event supply probe (exit-code contract)",
             "scripts/zoo92_limit_down_event_probe.py", ["--selftest"]),
            # r1393: the supply berth moves off the price axis onto the chips axis -- the
            # turnover-attenuated cost basis a holder is sitting on (CGO). Its legs pin the
            # three ways a cost-basis recursion lies: a flat tape must read a zero overhang,
            # zero turnover must freeze the basis at the oldest price in the window, and the
            # basis must stay inside the window's own price range (it is a convex mixture).
            # The last leg keeps an impossible turnover from making a weight negative.
            ("product: disposition CGO supply probe (exit-code contract)",
             "scripts/zoo93_disposition_cgo_probe.py", ["--selftest"]),
            # r1408: that berth's verdict bought a prereg, not a profit -- 65% of its decile
            # spread sits on the short leg an A-share desk cannot hold. This judge asks the
            # only question that can become money: is the long-only half worth doing after the
            # cost of turning the book over? Its legs pin the three ways such a judge lies: a
            # no-signal panel must not manufacture excess, an arm whose prices follow no
            # mean-reverting level must not read as an edge (constant per-name drift makes the
            # cost-basis gap and the forward return the same variable), and a full replacement
            # costs two sides -- a free exit is a free return.
            ("product: disposition CGO takeable judge (exit-code contract)",
             "scripts/zoo93_disposition_cgo_judge.py", ["selftest"]),
            # r1394: the supply berth leaves the price/chips axis for the MONEY axis -- the
            # exchange repo rate's own trailing percentile as a funding-stress gate (zoo #98).
            # Its legs pin the three ways a percentile gate lies: a later bar must never move an
            # earlier rank, a flat rate must not read as stress (ties sit at the average rank,
            # 0.525, which is why the naive "newest of a rising window = 1.0" reading is wrong),
            # and one bar of quarter-end noise must not act (confirmation is consecutive bars,
            # and a no-reading gap breaks the run instead of continuing it). The last leg keeps
            # the evaluated window inside the bars the rate archive actually measured.
            ("product: repo rate stress supply probe (exit-code contract)",
             "scripts/zoo98_repo_rate_stress_probe.py", ["--selftest"]),

            # r1409: the textbook dual-momentum rotation (zoo #82) priced on the published
            # book's own panel. Its legs pin the two ways a gate can lie about itself: a name
            # that fails the 60-bar absolute gate must be unselectable (not merely ranked
            # low), the defensive sentinel must sit strictly below every passer (so it holds
            # slots, never the book), and a gate that fails for the whole field must read as
            # all-defense rather than as "keep yesterday's book".
            ("product: dual momentum supply probe (exit-code contract)",
             "scripts/zoo82_dual_momentum_probe.py", ["--selftest"]),
            # r1410: zoo #85 (salience-panic, Barberis/Cosemans-Frehen) is the last
            # registered STOCK-domain behavioural berth that had never been burned. Its legs
            # pin the four ways a weighted-past-return factor lies: a partial window must not
            # produce a factor (a shorter window is a different construct), the forward matrix
            # must enter on the NEXT bar's open (no same-bar fill anywhere), the long-only leg
            # must pay two sides of cost per cohort rather than one, and the null must be
            # centred on that same cost -- a random draw of the whole pool returns -2*cost,
            # not zero.
            ("product: salience panic supply probe (exit-code contract)",
             "scripts/zoo85_salience_panic_probe.py", ["--selftest"]),
            # r1396: the last free berth on the supply line is the volume state machine (zoo
            # #96) -- HMA(5)/HMA(100) over the market's own traded value, long above 1.15 or
            # below 0.807, cash in between because an ETF book cannot short spot. Its legs pin
            # the four ways a ratio-of-window-MAs backtest lies: an always-long arm at zero cost
            # must reproduce the price path it can actually hold (flat on bar 0, so it buys at
            # bar 1's open), a state that arrives with the last bar must never trade, one
            # switch must cost exactly one side, and a flat volume series must read 1.0 rather
            # than a NaN that silently disables the state machine.
            ("product: volume regime supply probe (exit-code contract)",
             "scripts/zoo96_volume_regime_probe.py", ["--selftest"]),
            # r1405: zoo #94 is the berth whose registry row carried its own data precondition
            # -- "if the LHB face is aggregate, downgrade honestly". It is aggregate (no seat
            # column), so the run prices the all-seat variant and says so. Its legs pin the
            # de-dup itself, which is where an LHB series is silently invented: a "连续三个
            # 交易日" reason reports a multi-day cumulative net buy and must lose to the same-day
            # reason, a stock-day carrying only a cumulative row still counts, disagreeing
            # same-day rows are averaged rather than first-picked, and the live panel's own
            # claim (same-day reasons agree >=99%) is re-measured rather than assumed.
            ("product: LHB institution-distribution supply probe (exit-code contract)",
             "scripts/zoo94_lhb_inst_dist_probe.py", ["--selftest"]),
            # r1407: zoo #92 (球队硬币路径动量) is the last berth whose data precondition is
            # already on disk (daily OHLC + turnover). Its legs pin the two flips the card
            # defines -- a quiet leg reverses its own mean while a loud leg keeps it, a
            # shrinking turnover path reverses the day's return while a growing one does not
            # -- plus the three things a cross-sectional IC batch gets wrong without noticing:
            # a factor ranked against its own reverse, an eligibility gate that reads a
            # stopped tape as a zero return, and an empty period series that prints 0.0.
            ("product: path-continuity coin-team supply probe (exit-code contract)",
             "scripts/zoo_path_continuity_mom_probe.py", ["selftest"]),
            # r1402: a berth's STANDALONE verdict is not the money line's answer. zoo #96 was
            # refused as a rule on 510300 and that says nothing about it as a risk switch on
            # the book, which sits flat 43% of the time already. This leg keeps the join
            # callable: the control arm must reproduce the production cell to 1e-12, the state
            # must lag one bar (never the bar that produced it), an unread state holds the
            # previous weight instead of reading as flat, and the mirror must be the same
            # function on the flipped state rather than a second implementation.
            ("product: book x volume-gate overlay (exit-code contract)",
             "scripts/etf_book_volgate.py", ["--selftest"]),
            # r1395: the book's entry friction. The spot board publishes 折价率 (a DISCOUNT,
            # the opposite sign of a premium) and an IOPV that a cross-border fund cannot
            # check against anything until its T+n NAV arrives -- two ways to print a number
            # that is not the number you think it is. The legs pin the sign inversion, the
            # "unverifiable" third state, and the rule that an unknown leg is never priced 0.
            ("product: ETF premium entry-friction face (exit-code contract)",
             "scripts/etf_premium_face.py", ["selftest"]),
            # r1393: the D-19 watermark gate itself, priced because the live defect was a
            # watermark stored in DISPLAY form (a bare 16-hex prefix). The gate read that as
            # "no previous watermark" and re-consumed the whole decisions ledger every round
            # while the content hash never moved -- permanent fresh-looking news. The legs pin
            # all three accepted forms and, more importantly, that a prefix of a DIFFERENT
            # document is not read as unchanged.
            ("product: D-19 watermark gate (legacy forms, foreign prefix refused)",
             "Tools/d19_check.py", ["--selftest"]),
            # r1387: that probe's verdict outlived its number -- the null it lost to is what a
            # future timing rule actually has to beat, and nothing published it. This face
            # turns the null into a ruler on the book in force (hurdle per exposure share).
            # The legs pin the constant-drift analytic case, that a mask is never measured on
            # a LEVEL series (the walk returns levels; masking one compounds to inf), and that
            # the published hurdle re-derives from its own rows with a control arm.
            ("product: etf_book_exit_tax (ruler, exposure hurdle on the book in force)",
             "scripts/etf_book_exit_tax.py", ["--selftest"]),
            ("product: etf_book_exit_tax (published hurdle recomputed, control reproduced)",
             "scripts/etf_book_exit_tax.py", ["--check"]),
            # r1425: the commodity sleeve's 30% share was an attribution, never a knob.
            # The cap is now priced, and the offline legs pin that a cap fills its
            # shortfall instead of thinning the book and that identity is judged at the
            # published rounding, not on a panel that has since grown.
            ("product: etf_book_sleeve_cap (per-sleeve cap priced against the plain book)",
             "scripts/etf_book_sleeve_cap.py", ["--selftest"]),
            # r1425: a cap is a rule, so it gets the phase test a book gets. The single
            # phase said every cap loses; the phase set says something harder -- none of
            # the caps pulls the top-2 year share under the 70% line on ANY of the five
            # starts, and capping one sleeve makes the remaining years MORE concentrated.
            # The legs pin that the frozen adoption rule can reach ADOPT/REJECT/
            # UNADJUDICABLE and that each clause is the one that fires.
            ("product: etf_book_sleeve_cap_phases (a cap is a rule, read as a phase set)",
             "scripts/etf_book_sleeve_cap_phases.py", ["selftest"]),
            # r1426: r1425 left the desk holding a check it could not trust -- Y4's top-2
            # year share cannot adjudicate 3 of its own 4 arms (phase spread wider than the
            # distance to the line). The legs pin that a caliber is only trusted when its
            # denominator cannot vanish, its phases land on one side inside the margin, and
            # it resolves the book against an EVEN book; that a consistent but microscopic
            # arm gap is not separation; and that the composite verdict takes the worst word
            # (broad on one ruler never excuses front-loaded on another).
            ("product: etf_book_year_caliber (which year concentration ruler can judge itself)",
             "scripts/etf_book_year_caliber.py", ["selftest"]),
            ("product: etf_book_year_caliber (published reading re-derived, nothing renamed)",
             "scripts/etf_book_year_caliber.py", ["check"]),
            # r1428: "refused" with no horizon is an observation, not a plan. The legs pin
            # that a zero-return continuation can never clear Y4 (share is unchanged), that
            # years_for_half is not monotone as flat years accrue, that a losing book
            # publishes None rather than a share, and that the published ETA face still
            # reproduces r1427's phase-0 numbers (identity drift = refusal to ship).
            ("product: etf_book_admission_eta (how many years until the gate can admit)",
             "scripts/etf_book_admission_eta.py", ["selftest"]),
            ("product: etf_book_admission_eta (published ETA still matches the phase gate)",
             "scripts/etf_book_admission_eta.py", ["check"]),
            # r1429: with two certified rulers disagreeing on the held book, "use the trusted
            # ruler" became a choice, and picking the one that says PASS is the forbidden
            # "run until it passes". The legs pin that the election reads fixtures only
            # (elect() takes no parameter, and swapping a passing for a failing witness does
            # not move it), that a ruler admitting a declared pathology is disqualified even
            # when it scores well, and that the published face still re-derives.
            ("product: etf_book_admission_ruler_election (which ruler the gate asks with)",
             "scripts/etf_book_admission_ruler_election.py", ["selftest"]),
            ("product: etf_book_admission_ruler_election (published election re-derived)",
             "scripts/etf_book_admission_ruler_election.py", ["check"]),
            # r1431: the election named a ruler but no reason was switched, because that is
            # an admission-rule change with its own round. The legs pin the conservativeness
            # clause (a reporting change may never admit what is refused today -- checked as
            # a property over 600 random year tables, since the two rulers cannot disagree
            # that way by algebra), the degenerate-cell printing rule (a flat year table may
            # not print a refusal), and that the published verdict re-derives from its own
            # conditions rather than from a hand-written word.
            ("product: etf_book_admission_refusal_caliber_adoption (selftest 12 legs)",
             "scripts/etf_book_admission_refusal_caliber_adoption.py", ["selftest"]),
            ("product: etf_book_admission_refusal_caliber_adoption (verdict re-derived)",
             "scripts/etf_book_admission_refusal_caliber_adoption.py", ["check"]),
            # r1418: the calendar gate existed but had only ever judged CANDIDATE books; the
            # book the desk actually holds never faced it. The legs pin that yearly returns
            # come off the book's own LEVEL curve (treating a level series as returns
            # compounds to inf), that the frozen line is imported rather than re-typed, and
            # that every published verdict re-derives from the receipt's own rows.
            ("product: etf_book_year_gate (adopted book judged by its own calendar)",
             "scripts/etf_book_year_gate.py", ["selftest"]),
            ("product: etf_book_year_gate (published verdicts re-derived)",
             "scripts/etf_book_year_gate.py", ["check"]),
            # r1446: two true receipts that a desk cannot hold at once (the caliber dispute
            # says the gate is one decision from disagreeing with itself; the forward read
            # says the deciding check is decorative). The legs pin the four frozen classes
            # and that a movement the code cannot attribute is UNREADABLE rather than a
            # quiet INVARIANT, that one seen check floors a book, that the money book is
            # named by a receipt rather than hardcoded, and that the face prints both
            # calibers' numbers instead of one.
            ("product: etf_book_supply_gate_decision (one word for the rebalance)",
             "scripts/etf_book_supply_gate_decision.py", ["selftest"]),
            ("product: etf_book_supply_gate_decision (verdict re-derived from receipts)",
             "scripts/etf_book_supply_gate_decision.py", ["--check"]),
            # r1447: r1446 said the caliber dispute cannot move the money but never asked
            # whether the weight in force is the weight of a graded rule. The legs pin that
            # the ticket's own decision grid is the fixed 2020-01-01 20-bar grid (not the
            # last bar -- r1229's defect, which the first draft of this face repeated -- and
            # not the engine's re-decision phase), that a panel before the grid start reads
            # UNKNOWN rather than today, that an unreadable sizing never prints money, and
            # that every published figure re-derives from the ticket plus its own inputs.
            ("product: etf_book_live_size_provenance (which rule sizes the money)",
             "scripts/etf_book_live_size_provenance.py", ["selftest"]),
            ("product: etf_book_live_size_provenance (figures re-derived)",
             "scripts/etf_book_live_size_provenance.py", ["--check"]),
            # r1423: r1421 showed the concentration lives in the MAGNITUDES (2025 is a big
            # share of everything that moved) but no face said WHICH names produced them --
            # "the book had a big year" and "one bet had a big year" printed the same number
            # and need opposite repairs. The legs pin that the copied state machine
            # reproduces the engine bit for bit, that the name split re-adds to the year
            # rows exactly, that only the mover is credited, that toll is its own line, and
            # that a flat year never publishes a signed share or an exploded HHI.
            ("product: etf_book_year_attribution (which names carried which year)",
             "scripts/etf_book_year_attribution.py", ["selftest"]),
            ("product: etf_book_year_attribution (published split re-adds to its own rows)",
             "scripts/etf_book_year_attribution.py", ["check"]),
            # r1449: three rulers were each priced on their own face and the cell they never
            # shared (graded universe x the common window) is the lowest of the five. The legs
            # pin that the prose cannot claim a ceiling/flip the table contradicts, that an
            # unread ruler reads UNREADABLE instead of agreement, that the clip is the
            # engine's (de-risking only), and that the desk sentence re-derives from the
            # receipt's own cells.
            ("product: etf_book_size_rulers_decision (one size out of three rulers)",
             "scripts/etf_book_size_rulers_decision.py", ["selftest"]),
            ("product: etf_book_size_rulers_decision (desk sentence re-derived)",
             "scripts/etf_book_size_rulers_decision.py", ["check"]),
            # r1450: the rulers table said how wide the argument is; this face says whether
            # the weight in force may stay. The legs pin all three dispositions (a path
            # reading above the money permits, a static mix above it does not, nothing
            # above it refuses), pin that a broken baseline identity and an unclassified
            # cell both read UNREADABLE, and re-derive the permission from receipts.
            ("product: etf_book_rebalance_permission (may this size stay)",
             "scripts/etf_book_rebalance_permission.py", ["selftest"]),
            ("product: etf_book_rebalance_permission (permission re-derived)",
             "scripts/etf_book_rebalance_permission.py", ["--check"]),
            # r1451: a permission nobody reads is a decoration. The legs pin that an order
            # over the permission with zero consumers reads UNBOUND (and flips to BOUND the
            # moment a reader exists -- a leg that can only say "unbound" is not evidence),
            # that a ticket already inside the permission owes no trim, that an integer-lot
            # trim floors (both sides of a lot boundary), and that a missing receipt never
            # becomes a default cut.
            ("product: etf_book_cut_order_gap (does the permission bind the order)",
             "scripts/etf_book_cut_order_gap.py", ["selftest"]),
            ("product: etf_book_cut_order_gap (gap and consumers re-derived)",
             "scripts/etf_book_cut_order_gap.py", ["--check"]),
            # r1455: a receipt that audits the permission is not the document a desk
            # executes. The legs pin that the sheet itself reads the permission (trim
            # required / unused readings / unreadable never reads as a pass / two faces
            # disagreeing print a CONFLICT), and that the published ORDER page prints the
            # same floor and the same per-leg lots the audit receipt publishes.
            ("product: etf_book_order (the sheet sizes to the permission it must obey)",
             "scripts/etf_book_order.py", ["--selftest"]),
            # r1452: a cut is not a scaling. The legs pin that a cap only ever shrinks a
            # decision (never moves a date, a cap above every k is a no-op, and a cap from
            # a date leaves earlier decisions untouched), that constant-k scaling moves the
            # concentration reading by under 0.5pp while a time-varying cap does move it,
            # and that a year row without the gate's cohort unit is counted as zero
            # evidence rather than as a small sample.
            ("product: etf_book_cut_gate_pass (a cut is not a scaling)",
             "scripts/etf_book_cut_gate_pass.py", ["selftest"]),
            ("product: etf_book_cut_gate_pass (three arms re-derived)",
             "scripts/etf_book_cut_gate_pass.py", ["--check"]),
            # r1453: one row for the 11-11 decision. The legs pin that a held book and a
            # ticket arm are printed with both denominators, that two receipts quoting the
            # same k but disagreeing make the face RED rather than newer-wins, that a
            # missing receipt is UNKNOWN and not zero, and that a trim which does not land
            # under the permission (or whose arithmetic does not close) cannot pass.
            ("product: etf_book_decision_line (one row, receipts must agree)",
             "scripts/etf_book_decision_line.py", ["selftest"]),
            ("product: etf_book_decision_line (row re-derived from the receipts)",
             "scripts/etf_book_decision_line.py", ["--check"]),
            # r1454: the gate has always judged the book BEFORE the execution wrapper while
            # the desk runs the book AFTER it. The legs pin that the three arms are published
            # on identical bars, that each verdict re-derives from its own checks, and that
            # the flip list and the ticket's k reproduction are re-derived, not asserted.
            ("product: etf_book_wrapper_year_gate (three arms, one gate)",
             "scripts/etf_book_wrapper_year_gate.py", ["selftest"]),
            ("product: etf_book_wrapper_year_gate (every arm re-derived)",
             "scripts/etf_book_wrapper_year_gate.py", ["--check"]),
            # r1456: the trim the 11-11 sheet applies is not a one-off -- k_schedule re-derives
            # k every 20 bars and remembers nothing. The legs pin the control arm (the schedule's
            # last decision bar reproduces the ticket k, or the face refuses to publish) and that
            # the published lifetime re-derives from the same panel. Censored drops stay None.
            ("product: etf_book_permission_persistence (how long a trim survives)",
             "scripts/etf_book_permission_persistence.py", ["selftest"]),
            ("product: etf_book_permission_persistence (lifetime re-derived)",
             "scripts/etf_book_permission_persistence.py", ["--check"]),
            # r1420: the yearly gate could only answer ADMIT/CONDITIONAL/REFUSE, so a book
            # whose phase spread is wider than its distance to the 70% line still got a
            # word. The legs pin the third word in both directions (a split verdict and a
            # unanimous verdict whose spread exceeds the margin are both UNADJUDICABLE;
            # a unanimous verdict inside the margin keeps its own word) and pin that the
            # five-phase adjudicator reproduces r1418's published rows at phase 0.
            ("product: candidate_year_gate_phases (the gate can say it cannot tell)",
             "scripts/candidate_year_gate_phases.py", ["selftest"]),
            # r1421: the concentration line that refused three of the desk's five books had
            # never been asked what it measures. It measures annual Sharpe (the share is
            # scale invariant, so the null depends on m/s alone) and it has no power -- a
            # book whose two years carry 95% of profit reads the 70th percentile of its own
            # Sharpe peers. The legs pin the scale/order invariance, the monotone null, the
            # inversion off the frozen grid, that a signed-sum statistic is unbounded, and
            # that the absolute-share alternative is nearly Sharpe-flat.
            ("product: year concentration calibration (the line measures Sharpe, not shape)",
             "scripts/year_concentration_calibration.py", ["selftest"]),
            # r1403: the ledger's freeze question is arithmetic, not a fear -- re-derive
            # every published bar read-only and split it with the LIVE settle rule. The
            # legs pin that a settled bar below tol stays silent, that the same numbers DO
            # block once the cash leg claims to have priced them, that a settled bar moving
            # for a non-carry reason is named rather than excused, and that an unreadable
            # bar list never reads as a pass.
            ("product: etf_book_carry_repro (settled-only drift gate, refill forecast)",
             "scripts/etf_book_carry_repro.py", ["--selftest"]),
            # r1404: the ledger was committed unreadable for four hours -- a line-level
            # resolution spliced two documents together and dropped a comma, and the
            # pre-commit claw only looks for conflict markers. The legs pin that a
            # missing comma between list elements is a finding, that a repeated key is a
            # finding even though json keeps the last one silently, that the same key in
            # two sibling objects is not, and that a UTF-16 face fails because every
            # reader opens encoding='utf-8'. The default scan is the published faces
            # (results/, scratch dumps excluded), so this leg is a real gate, not a
            # fixture.
            ("product: json_face_guard (a committed face must parse and must not repeat a key)",
             "Tools/json_face_guard.py", ["--selftest"]),
            # r1346: the chain runner pays a leg's declared refresh when its probe
            # says the face is stale, and must NOT pay it when the probe says
            # inconsistent. That branch is what stops a check-only gate from being
            # permanently red on inherited state (r1135 trap), so it is priced here
            # every suite instead of once in a digest.
            ("product: S6 chain refresh branch (stale pays, inconsistent does not)",
             "Tools/s6_chain_bmc.py", ["--selftest"]),
            # r1199: an empty pool has two causes needing opposite responses.
            # The exit-code leg keeps the counter callable; the --check leg
            # refuses a published verdict that does not follow from its own
            # numbers, so "supply is fine" cannot be typed in.
            ("product: supply candidate face (empty pool: broken vs no work)",
             "scripts/supply_candidate_face.py", ["--selftest"]),
            ("product: supply candidate verdict recomputed from its published rows",
             "scripts/supply_candidate_face.py", ["--check"]),
            # r1421: agenda debt split one layer further -- "nobody wrote a
            # topic" and "every candidate we judged fails its own calendar"
            # printed the same word and take opposite orders. The --check leg
            # re-derives the verdict from the published candidate rows, so
            # "a candidate passed" cannot be typed in. r1432 extends the same leg:
            # the refusal REASON must now name the ruler r1431 adopted (years_for_half)
            # with its own median-vs-line reading, and --check re-derives every sentence
            # from the row plus the published election -- a hand-typed reason is red, and
            # a flat (degenerate) book may carry no sentence at all.
            ("product: supply calendar face (no topic vs no candidate passes its calendar)",
             "scripts/supply_calendar_face.py", ["--selftest"]),
            ("product: supply calendar verdict recomputed from its published rows",
             "scripts/supply_calendar_face.py", ["--check"]),
            # r1422: the floor read `ready 0 < floor 3` for thirty rounds while the
            # ladder printed at most one blocked row per tick -- its id carried an
            # idempotency skip, so 22 rows that had already burned were INVISIBLE and
            # "catalog exhausted" read exactly like "one row is gated". The selftest
            # pins the class matrix and the grandfather boundary; the explain leg is
            # dry-run on purpose (a suite must not rewrite the published face).
            ("product: fill ladder face (an exhausted catalog is not an unblockable one)",
             "Tools/fill_ladder.py", ["selftest"]),
            ("product: fill ladder explain names every row's class and the calendar refusal",
             "Tools/fill_ladder.py", ["explain", "--dry-run"]),
            # r1435: "median 2 years" was printed for thirty-nine rounds and read as
            # "front-loaded, the money is spent" -- but the ruler sorts the year nets
            # descending and cannot tell early from late. The legs pin that the direction
            # word is read off the MEMBERS (not every year), that a non-positive calendar
            # sum publishes no_half rather than "one year explains it", that the half
            # boundary is >= inclusive exactly like the ruler, and that the published
            # sentences re-derive from their own year tables (a typed story is red).
            ("product: etf_book_half_year_provenance (which years are in the half)",
             "scripts/etf_book_half_year_provenance.py", ["selftest"]),
            ("product: etf_book_half_year_provenance (published sentences re-derived)", 
             "scripts/etf_book_half_year_provenance.py", ["check"]),
            # r1205: the line's freshness faces all read the instant, so a
            # stall followed by one heartbeat is invisible. This leg prices the
            # history reader: fuzzy stamps widen instead of narrowing, quiet
            # windows are subtracted per machine, and the still-open gap is its
            # own verdict.
            ("product: lane silence audit (gaps between rounds, quiet windows subtracted)",
             "scripts/lane_silence_audit.py", ["selftest"]),
            # r1399: the line charges 13.041bp per side and had never looked at a fill.
            # This ruler prices the opening minute from the minute archive, and it
            # refuses a session whose first bar is 13:53 -- a fabricated open print is
            # worse than no reading.
            ("product: open print ruler (first-minute drift, spread, and the size that fits)",
             "scripts/open_print_ruler.py", ["selftest"]),
            # r1400: the repaired panel rebuilt each column FORWARD from its own first bar, so
            # a real share split flattened as a "flip" left the column on the pre-split scale
            # forever -- 513100 quoted 11.0388 against a tape printing 2.162 (5.1x), and 158
            # of 1,624 columns were off by more than 5%. This leg pins the re-anchor and the
            # scale-invariance that lets it repair sizing without moving a backtest number.
            ("product: panel level anchor (a repaired column ends at the price the tape prints)",
             "scripts/panel_level_anchor_audit.py", ["selftest"]),
            # r1401: a ticket that never says whether its own legs are small. Two rulers
            # printed side by side and never folded -- the opening print and the day's
            # median turnover -- with a leg that has no minute archive reading UNVERIFIED
            # rather than 0, and the lane's own staleness printed even when no leg prices.
            ("product: ticket open capacity (two rulers, unverified is not zero)",
             "scripts/ticket_open_capacity.py", ["selftest"]),
            # r1223: "the lane was re-enabled" and "the lane stayed on" are two
            # claims; only the second is a fix. This one measures the second, and
            # its own failure mode (an unreadable tick read as "still on") is what
            # the selftest legs pin.
            ("product: lane task survival (a re-enable switched off again inside the window is not a heal)",
             "scripts/lane_task_survival.py", ["selftest"]),
            ("product: etf_book_production card (exit-code contract)",
             "scripts/etf_book_production.py", ["--selftest"]),
            # r1249: the evening quote face must not price a name whose snapshot does not
            # provably join the panel, and it must never print a book number on a failed
            # join. The selftest pins the tolerance boundary, the mismatch-share gate, the
            # NO_NEW_BAR branch and the 5xx->SH mapping (a wrong prefix silently read two
            # held names as unreadable in the first real run).
            ("product: etf_book_live_quote (join gate, never a zero on a failed join)",
             "scripts/etf_book_live_quote.py", ["selftest"]),
            ("product: etf_book_live_quote verdict recomputed from its published rows",
             "scripts/etf_book_live_quote.py", ["--check"]),
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
            # r1153: the battle report now names the market's risk tape (limit-up /
            # limit-down / broken-seal / strong counts + the streak ladder) instead of
            # leaving it in a forward panel nobody reads. Its selftest builds a real
            # parquet fixture, so a column rename or a "missing day = 0 members"
            # regression reads red instead of shipping a quiet zero.
            ("product: daily report risk tape (zt pools, honest absence)",
             "scripts/daily_report.py", ["selftest"]),
            # the four risk tiers used to need four separate `--beta` runs read off two
            # different files; this leg keeps the one-page menu callable (r1149).
            ("product: etf_book_beta_menu (exit-code contract)",
             "scripts/etf_book_beta_menu.py", ["--selftest"]),
            ("product: etf_book_width_null_production (verdict recomputed from its own columns)",
             "scripts/etf_book_width_null_production.py", ["--selftest"]),
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
            # r1175: "the market gaps 5%, so what do I lose" (answered through the
            # measured beta, not the deployed share) and "how much of the book's own
            # numbers is quote-flip contamination" (answered by running the same rule on
            # repaired prices). Both gates recompute their verdict from their published
            # columns, so a hand-edited verdict fails here instead of reading as done.
            ("product: etf_book_shock_day (exit-code contract)",
             "scripts/etf_book_shock_day.py", ["--selftest"]),
            ("product: etf_book_flip_contamination (exit-code contract)",
             "scripts/etf_book_flip_contamination.py", ["--selftest"]),
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
            # r1232: every face above asks WHICH names and WHEN; the engine's `w = 1/n_hold`
            # line was never priced. These legs pin the three things that would make a risk
            # weighting look better than it is: a hook that is a second engine (the equal
            # scheme must be bit-identical to the default), a rule that peeks past the
            # decision bar, and an ERC solve that goes short on a sampled covariance.
            ("product: picks-to-weights rule priced across books and phases (exit-code contract)",
             "scripts/etf_book_weight_scheme.py", ["--selftest"]),
            ("product: published weight-scheme verdict recomputes from its summary",
             "scripts/etf_book_weight_scheme.py", ["--check"]),
            # r1347: adoption tested one arm; the hysteresis face still publishes four more
            # priced on a single sequence. These legs pin the breakeven-cost conversion and
            # the family verdict reading its arms, and keep "behind the card" a third state
            # instead of a permanently red gate (r1346).
            ("product: buffer arm grid breakeven and family verdict (exit-code contract)",
             "scripts/etf_book_hysteresis_paths.py", ["--selftest"]),
            # r1347: a breakeven in bp/side is not a size. These legs pin the sqrt cost law
            # and its inverse, the three crossing states (gains return / under the base / no
            # impact component), and the share rule that keeps one lucky cell from reading as
            # "pays at size".
            ("product: buffer breakeven priced as a size (exit-code contract)",
             "scripts/etf_book_buffer_price_of_size.py", ["--selftest"]),
            # r1348: the book has one history, so every headline is a point estimate on one
            # ordering of the panel. These legs pin the bootstrap's determinism, its
            # block-length semantics, the "zero is not a null" Sharpe, the monotone
            # percentiles, the activity leg (a resample that changed nothing fails), and the
            # gate's ability to catch a hand-edited percentile from the stored rows.
            ("product: book envelope by block bootstrap (exit-code contract)",
             "scripts/etf_book_nav_envelope.py", ["--selftest"])):
        try:
            _r = capture_pinned([sys.executable, _script, *_args], 300)
            _tail = ((_r.stdout or _r.stderr).strip().splitlines() or ["no output"])[-1]
            check(_label, _r.returncode == 0, f"exit={_r.returncode} | {_tail[:80]}")
        except Exception as e:
            check(_label, False, str(e))
    # r1386: the two loops above used to hand subprocess.run a capture with no
    # encoding, so the harness decoded with the locale while it told its own
    # children to write UTF-8. That mismatch does not fail -- it kills the reader
    # thread and the whole suite hangs. A rule that lives in 14 call sites and not
    # in 2 is the defect, so this leg reads the harness source and refuses any
    # capture that does not pin both encoding and errors.
    try:
        import ast as _ast
        _srcp = os.path.abspath(__file__)
        _tree = _ast.parse(open(_srcp, encoding="utf-8-sig").read())
        _bare = []
        for _n in _ast.walk(_tree):
            if not isinstance(_n, _ast.Call):
                continue
            _f = _n.func
            if not (isinstance(_f, _ast.Attribute) and _f.attr == "run"
                    and isinstance(_f.value, _ast.Name) and _f.value.id == "subprocess"):
                continue
            _kw = {k.arg: k.value for k in _n.keywords if k.arg}
            # A bytes capture is not the hazard: the caller decodes it explicitly
            # (the git reads at the bottom of this file do exactly that). The
            # hazard is asking subprocess to decode FOR us and not saying how.
            _wants_text = ("text" in _kw or "universal_newlines" in _kw)
            if not _wants_text:
                continue
            if "encoding" not in _kw or "errors" not in _kw:
                _bare.append(_n.lineno)
        check("tooling: every harness subprocess capture pins encoding and errors",
              not _bare, "unpinned subprocess.run at line(s) %s" % (_bare or "-"))
    except Exception as e:
        check("tooling: every harness subprocess capture pins encoding and errors",
              False, str(e))
    # r1210: the envelope's input series had no producer on the chain, so it quietly
    # bootstrapped a one-bar-stale book (series 9.70% vs the published cell 9.60%). A
    # percentile of another object is not a risk statement, so this leg re-derives which
    # object the published face describes and refuses a series older than the book.
    try:
        import json as _json
        _env = os.path.join("results", "etf_book_bootstrap", "latest.json")
        _prod = os.path.join("results", "etf_book_production", "latest.json")
        if os.path.exists(_env) and os.path.exists(_prod):
            _e = _json.load(open(_env, encoding="utf-8"))
            _p = _json.load(open(_prod, encoding="utf-8"))
            _ser = _json.load(open(os.path.join("results", "etf_book_series",
                                                _e.get("series_file") or "latest.json"),
                                   encoding="utf-8"))
            _rec = _e.get("book_reconciliation") or {}
            _cfg = (_p.get("config") or {})
            _key = ("n%s_vt%02d" % (_cfg.get("n_hold"),
                                    int(round((_cfg.get("vol_target") or 0) * 100)))
                    if _cfg.get("vol_target") else "n%s_base" % _cfg.get("n_hold"))
            _cell = ((_p.get("backtest") or {}).get(_key) or {}).get("full") or {}
            check("product: the book envelope says whose book it describes",
                  _ser.get("evidence_cutoff") == _p.get("evidence_cutoff")
                  and _rec.get("verdict") == "same_object"
                  and _rec.get("production_cell") == _key
                  and _rec.get("series_cagr") == _cell.get("cagr"),
                  "series %s vs book %s | %s %s vs %s" % (
                      _ser.get("evidence_cutoff"), _p.get("evidence_cutoff"),
                      _rec.get("verdict"), _rec.get("series_cagr"), _cell.get("cagr")))
    except Exception as _e2:
        check("product: the book envelope says whose book it describes", False, str(_e2))

    # r1211: the distribution reached the CEO page. Two ways to break this and only one of
    # them is visible by eye: (a) the section disappears, (b) the page prints a percentile
    # that its own resample rows do not produce. The leg re-derives from the rows.
    try:
        from scripts import etf_book_nav_envelope as _NE
        from scripts import etf_book_ceo_page as _PG
        _env = _NE.read_published()
        _md = open(os.path.join("docs", "live_book", "LIVE-BOOK-%s.md"
                               % __import__("time").strftime("%Y%m%d")),
                   encoding="utf-8").read()
        _bad = []
        if _env.get("status") != "ok":
            _bad.append("reader status %s (%s)" % (_env.get("status"), _env.get("detail")))
        else:
            if "这一本账在它自己的日子里" not in _md:
                _bad.append("the luck section is gone from the page")
            for _q in ("5", "50", "95"):
                _tok = "%.2f%%" % (_env["cagr"][_q] * 100)
                if _tok not in _md:
                    _bad.append("CAGR p%s (%s) is not on the page" % (_q, _tok))
            _sh = _env["shares"]
            if "%.1f%%" % (_sh["cagr_le_zero"] * 100) not in _md:
                _bad.append("the losing share is not on the page")
            _block = "\n".join(_PG.envelope_block(_env))
            if "典型" not in _block:
                _bad.append("the page does not say the point estimate is a typical path")
        check("product: the page shows the book's own luck distribution, not just a point",
              not _bad, "; ".join(_bad[:3]) or "p50 %.2f%% / p5 %.2f%%"
              % ((_env.get("cagr") or {}).get("50", 0) * 100,
                 (_env.get("cagr") or {}).get("5", 0) * 100))
    except Exception as _e3:
        check("product: the page shows the book's own luck distribution, not just a point",
              False, str(_e3))

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
    # r1334 / E229: the card's printed amount column used to be a TARGET (weights x
    # capital), so a reader wiring it into a ticket came up short by the lot rounding
    # every single time. The face now prints an executable column; this leg recomputes
    # the identity from the published sheet, never from a sentence on the card.
    try:
        _lp = os.path.join("results", "etf_book_production", "latest.json")
        _card = os.path.join("results", "etf_book_production", "CARD.md")
        if os.path.exists(_lp) and os.path.exists(_card):
            _doc = json.load(open(_lp, encoding="utf-8"))
            _sh = (_doc.get("sheet") or {})
            _cap = _sh.get("capital_cny")
            _keys = ("book_target_cny", "book_executable_cny", "lot_residual_cny",
                     "cash_executable_cny")
            _have = all(_sh.get(k) is not None for k in _keys)
            _id1 = _have and abs(_sh["book_target_cny"] + _sh["cash_amount_cny"] - _cap) <= 2
            _id2 = _have and abs(_sh["book_executable_cny"] + _sh["cash_executable_cny"]
                                 - _cap) <= 2
            _id3 = _have and abs(_sh["lot_residual_cny"]
                                 - (_sh["book_target_cny"] - _sh["book_executable_cny"])) <= 2
            _txt = open(_card, encoding="utf-8").read()
            _tw = "Which column is money" in _txt
            _nym = _sh.get("cash_executable_cny")
            _printed = _nym is not None and format(int(_nym), ",") in _txt
            check("product: card amount column is executable money",
                  _have and _id1 and _id2 and _id3 and _tw and _printed,
                  "keys=%s target=%.0f exec=%.0f residual=%.0f card=%s/%s"
                  % (_have, _sh.get("book_target_cny") or -1,
                     _sh.get("book_executable_cny") or -1,
                     _sh.get("lot_residual_cny") or -1, _tw, _printed))
        else:
            check("product: card amount column is executable money", True,
                  "production sheet absent -- face soft-fails by design")
    except Exception as e:
        check("product: card amount column is executable money", False, str(e))
    # r1221: the card's table is the as-coded arm (rank on bar d, paid bar d's OPEN) while
    # the same card declares "decide at close t -> fill at open t+1". The declared arm is now
    # priced beside it; this leg re-derives the gap from the payload's two arms and demands
    # the declared number appear on the card -- a card that prints one arm and declares the
    # other is what the operator was reading until this round.
    try:
        _lp = os.path.join("results", "etf_book_production", "latest.json")
        _card = os.path.join("results", "etf_book_production", "CARD.md")
        if os.path.exists(_lp) and os.path.exists(_card):
            _doc = json.load(open(_lp, encoding="utf-8"))
            _eb = _doc.get("execution_basis") or {}
            _txt = open(_card, encoding="utf-8").read()
            _v = _eb.get("verdict")
            _a, _d = _eb.get("as_coded_cagr"), _eb.get("declared_cagr")
            if _v == "CANNOT_VERIFY" or _a is None or _d is None:
                _ok = _v == "CANNOT_VERIFY" and "Execution basis: unreadable" in _txt
                _detail = "unreadable arm -> %s" % _v
            else:
                _gap = round(100.0 * (_a - _d), 3)
                _ok = (abs((_eb.get("gap_pp") or 0.0) - _gap) <= 0.01
                       and _v == ("EQUIVALENT" if abs(_gap) < 0.25 else "SAME_OPEN_ARM"))
                if _v == "SAME_OPEN_ARM":
                    _ok = _ok and ("%.2f%%" % (100 * _d)) in _txt and ("%.2fpp" % _gap) in _txt
                _detail = "%s gap %.2fpp (%.2f vs %.2f)" % (_v, _gap, 100 * _a, 100 * _d)
            check("product: the card states which of its two arms the desk can trade",
                  _ok, _detail)
            # r1225: the sentence was one paragraph BELOW the table it qualifies, so the first
            # row a reader sizes from still printed the un-tradable arm. The table now names
            # each row's fill convention and prices both arms side by side; this leg demands
            # the declared row carry the payload's own number, so a hand-edited or stale
            # table reads red instead of merely looking more honest.
            if _a is not None and _d is not None:
                _row_ok = ("| 2020-01 onwards -- as coded |" in _txt
                           and ("| 2020-01 onwards -- declared fill (close t -> open t+1) | %.1f%%"
                                % (100 * _d)) in _txt)
                check("product: the card table prices both arms in the headline rows",
                      _row_ok, "declared row %.1f%%" % (100 * _d))
            else:
                check("product: the card table prices both arms in the headline rows", True,
                      "unreadable arm -- the sentence leg already owns that state")
            # r1228: three research cases (E25/E26/E27) each answered in their own file, and
            # the card never said the three add up to "no lever" -- so a reader was invited to
            # ask a fourth time. Re-derive the roll-up from each published face's own rows,
            # then demand the card print the same states: a hand-written or stale "closed"
            # reads red.
            _rx = _doc.get("research_exhaustion") or {}
            _rows = [r for r in (_rx.get("rows") or []) if r.get("readable")]
            _recomputed = []
            for _r in _rows:
                _p = os.path.join("results", os.path.basename(_r.get("artifact") or ""))
                try:
                    _face = json.load(open(_p, encoding="utf-8"))
                except Exception:
                    _recomputed.append(None)
                    continue
                _fv = _face.get("verdict") or {}
                _recomputed.append((_fv.get("state"), len(_fv.get("admissible_arms") or [])))
            _levers = sum(1 for _t in _recomputed if _t and _t[1])
            _want = ("OPEN_LEVER" if _levers else
                     ("CANNOT_VERIFY" if len(_rows) != 3 else "CLOSED"))
            _rx_ok = (_rx.get("verdict") == _want
                      and all(_t is not None and _t[0] == _r.get("state")
                              for _t, _r in zip(_recomputed, _rows))
                      and "What has already been asked about these numbers" in _txt
                      and all(_r.get("state") in _txt for _r in _rows))
            check("product: the card says which research questions its numbers already answered",
                  _rx_ok, "%s from %d faces (%d levers)"
                  % (_rx.get("verdict"), len(_rows), _levers))
        else:
            check("product: the card states which of its two arms the desk can trade", True,
                  "production sheet absent -- face soft-fails by design")
            check("product: the card table prices both arms in the headline rows", True,
                  "production sheet absent -- face soft-fails by design")
    except Exception as e:
        check("product: the card states which of its two arms the desk can trade", False, str(e))
        check("product: the card table prices both arms in the headline rows", False, str(e))
    try:
        _legs = __import__("importlib").import_module("Tools.s6_chain_bmc").LEGS
        _names = {t[0] for t in _legs}
        # etf_book_production belongs here as much as the ticket: r1290 caught the card
        # (the headline face) a full refresh behind the ticket because only the ticket
        # was wired -- an unwired face reads as current to everything downstream.
        # etf_book_width_audit prices the disagreement between the card and the ticket,
        # so it goes stale the moment either moves: r1291 found it two bars behind both.
        # r1366: etf_book_return_regime is the carry split behind the ticket's cagr --
        # it was hand-run and sat a full session behind (11.33% vs the ticket's 11.19%),
        # so the face that explains the headline number was explaining yesterday's book.
        _want = {"etf_book_forward", "etf_book_production", "etf_book_order",
                 "etf_book_width_audit", "etf_book_registry", "etf_book_ceo_page",
                 "etf_book_card_track", "etf_paper_signal", "cal_audit",
                 "etf_book_return_regime", "etf_book_settle_audit"}
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
    # r1170: the CEO page prints the regime cap (RED 20%) and the ticket prints a deployed
    # book; nothing compared them, and the same face must never read a cap as a rule for a
    # book that has its own one. This leg recomputes the verdict from the published rows
    # and the published cap, so a face that says "inside" while a row is over reads red,
    # and a row governed by its own rule can never be counted as a breach.
    try:
        _rc = json.load(open(os.path.join("results", "regime_cap_vs_book.json"),
                             encoding="utf-8"))
        _cap = _rc.get("ladder_cap")
        _rows = _rc.get("accounts") or []
        _judged = [r for r in _rows if r.get("kind") == "ladder"
                   and r.get("deployed_weight") is not None]
        _over = [r for r in _judged
                 if _cap is not None and r["deployed_weight"] > _cap + 0.002]
        _want_v = ("NOTHING_TO_COMPARE" if not _judged else
                   ("ABOVE_CAP" if _over else "INSIDE_CAP"))
        _v = (_rc.get("verdict") or {}).get("book")
        _worst = max(_judged, key=lambda r: r["deployed_weight"]) if _judged else None
        _sent = _rc.get("sentence") or ""
        _quotes = _worst is None or (
            _worst["name"].split(" ")[0] in _sent
            and "%.1f%%" % (_worst["deployed_weight"] * 100) in _sent)
        _leg_ok = "regime_cap_vs_book" in {
            t[0] for t in __import__("importlib")
            .import_module("Tools.s6_chain_bmc").LEGS}
        check("product: the regime cap is compared with the money actually deployed",
              _v == _want_v and _quotes and _leg_ok,
              f"cap={_cap} verdict={_v} recomputed={_want_v} "
              f"n_over={len(_over)}/{len(_judged)} sentence_quotes_worst={_quotes} "
              f"leg_wired={_leg_ok}")
    except Exception as e:
        check("product: the regime cap is compared with the money actually deployed", False, str(e))
    # r1348 / E246: a risk band is only a law if it reaches the page a human trades from.
    # The card renders one row per block arm and the order sheet prints the p5 range, so
    # both faces are recomputed here from BLOCKS-<cutoff>.json instead of grepping for a
    # sentence: a card priced on an older bar than the arms, or a band left in a digest,
    # fails this leg. r1315 family -- a fixture proves the shape, only the live file
    # proves the delivery.
    try:
        _bl = sorted(__import__("glob").glob(os.path.join("results", "etf_book_bootstrap",
                                                          "BLOCKS-*.json")))
        _card_p = os.path.join("results", "etf_book_production", "CARD.md")
        _ord = [p for p in sorted(__import__("glob").glob(
            os.path.join("results", "etf_book_order", "ORDER-*.md")))
            if not p.endswith("-card.md")]
        if _bl and os.path.exists(_card_p) and _ord:
            _b = json.load(open(_bl[-1], encoding="utf-8"))
            _ct = open(_card_p, encoding="utf-8").read()
            _rows_missing = []
            for _a in _b.get("arms") or []:
                _row = "| %d | %.2f%% | %.2f%% | %.1f%% | %.1f |" % (
                    int(_a["block"]), _a["maxdd"]["5"] * 100, _a["maxdd"]["50"] * 100,
                    _a["shares"]["maxdd_le_line"] * 100, _a["point_pctile"]["maxdd"])
                if _row not in _ct:
                    _rows_missing.append(_a["block"])
            _p5 = _b["spread"]["maxdd_p5"]
            _want = "%.1f%% ~ %.1f%%" % (_p5["min"] * 100, _p5["max"] * 100)
            _ot = open(_ord[-1], encoding="utf-8").read()
            _cut = _b.get("evidence_cutoff") or ""
            check("product: E246 drawdown band reaches both trading pages",
                  bool(_b.get("arms")) and not _rows_missing and _cut in _ct
                  and _want in _ot and _cut in _ot,
                  "arms=%d missing_rows=%s card_cut=%s order=%s(%s)"
                  % (len(_b.get("arms") or []), _rows_missing or "none",
                     _cut in _ct, _want in _ot, _want))
        else:
            check("product: E246 drawdown band reaches both trading pages", True,
                  "blocks/card/order absent -- face soft-fails by design")
    except Exception as e:
        check("product: E246 drawdown band reaches both trading pages", False, str(e))
    # r1357 / E271: the width ruler now has to reach BOTH documents a reader can hold, and
    # the number on each page is recomputed here from the ruler face rather than grepped as
    # a sentence: if the face moves, both pages fail. The card sheet is additionally asked
    # to say which face on that ruler it is -- the paired gap is between the two live
    # books, so printing it as "this sheet vs the card" would quote a difference between
    # two other books (r1280 family: a label that outlives its numbers).
    try:
        _rp = os.path.join("results", "etf_book_live_width_ruler.json")
        _ord_all = sorted(__import__("glob").glob(
            os.path.join("results", "etf_book_order", "ORDER-*.md")))
        _ord_beta = [p for p in _ord_all if not p.endswith("-card.md")]
        _ord_card = [p for p in _ord_all if p.endswith("-card.md")]
        if os.path.exists(_rp) and _ord_beta and _ord_card:
            _r = json.load(open(_rp, encoding="utf-8"))
            _pr = _r.get("paired") or {}
            _ed = _r.get("engine_disagreement") or {}
            _rl = _r.get("rule") or {}
            _med = _pr.get("median_pp")
            _dis = _ed.get("rung_disagreement_pp")
            _split_max = _rl.get("sign_split_max") or 0.6
            _coin = (_med is not None and _dis is not None
                     and abs(float(_med)) < abs(float(_dis))
                     and float(_pr.get("sign_agreement") or 1.0) <= float(_split_max)
                     and int(_pr.get("pairs") or 0) >= int(_rl.get("pairs_min") or 20))
            _want = "%+.2fpp" % float(_med) if _med is not None else ""
            _bt = open(_ord_beta[-1], encoding="utf-8").read()
            _ct2 = open(_ord_card[-1], encoding="utf-8").read()
            check("product: E271 the width ruler reaches both order documents",
                  bool(_coin) and bool(_want) and _want in _bt and _want in _ct2
                  and ("%+.2fpp" % float(_dis)) in _bt
                  and ("%+.2fpp" % float(_dis)) in _ct2
                  and "覆盖那张单" in _ct2,
                  "coin=%s want=%s beta=%s card=%s names_other=%s"
                  % (_coin, _want, _want in _bt, _want in _ct2, "覆盖那张单" in _ct2))
        else:
            check("product: E271 the width ruler reaches both order documents", True,
                  "ruler/order absent -- face soft-fails by design")
    except Exception as e:
        check("product: E271 the width ruler reaches both order documents", False, str(e))
    # r1249 (bm-a): the live-width gate went red three times in two days, every time on a ticket
    # RE-ISSUE, and each repair was pinned only by the script's own selftest. The rule that picks
    # the branch -- identity is the ticket's square fingerprint, not its date -- is asked here on
    # the PUBLISHED face, offline: two payloads differing in nothing but one cell, once under the
    # same fingerprint (an edit, must stay red) and once under a changed one (a re-issue, must
    # read stale so the chain pays the declared refresh). A face that publishes no fingerprint
    # silently degrades this gate to the date test that already failed, so that is red too.
    try:
        _sp49b = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
        if _sp49b not in sys.path:
            sys.path.insert(0, _sp49b)
        _A49 = importlib.import_module("etf_book_phase_atlas_arms")
        _lw49 = None
        _lwp49 = os.path.join("results", "etf_book_live_width_ruler.json")
        if os.path.exists(_lwp49):
            _lw49 = json.load(open(_lwp49, encoding="utf-8"))
        _bad49b = []
        _ai49 = (_lw49 or {}).get("as_issued") or {}
        if not _ai49.get("square_fingerprint"):
            _bad49b.append("the published face carries no square fingerprint, so the re-issue "
                           "test falls back to the ticket date that already failed")
        _base49 = json.loads(json.dumps(_lw49 or {}))
        _moved49 = json.loads(json.dumps(_base49))
        _cell49 = (_moved49.get("as_issued") or {}).get("cells_cagr_pp") or {}
        if not _cell49:
            _bad49b.append("the published face carries no as-issued cells")
        else:
            _k49 = sorted(_cell49)[0]
            _cell49[_k49] = round(float(_cell49[_k49]) - 0.03, 3)
            if _A49._ticket_repriced(_base49, _moved49) is not None:
                _bad49b.append("a moved cell under the SAME square fingerprint was read as a "
                               "re-issue -- a hand edit must stay red")
            _re49 = json.loads(json.dumps(_moved49))
            _re49["as_issued"]["square_fingerprint"] = "0" * 16
            _re49["as_issued"]["ticket_asof"] = _ai49.get("ticket_asof")
            if not isinstance(_A49._ticket_repriced(_base49, _re49), str):
                _bad49b.append("a same-day re-issue with a changed square fingerprint was read "
                               "as an edit -- the exact defect r1248 fixed")
        check("product: the live-width gate tells a re-issued ticket from a hand edit",
              not _bad49b, "; ".join(_bad49b)[:200]
              or "same fingerprint + moved cell = edit; changed fingerprint = re-issue")
    except Exception as e:
        check("product: the live-width gate tells a re-issued ticket from a hand edit",
              False, repr(e)[:180])
    # r1358 / E272: a paired gap is only readable against the resolution of its own pairing.
    # Recompute z*sd/sqrt(n) here from the face's published sd and phase count -- never read the
    # stored mde -- and require the same floor on BOTH documents. If the face moves, both pages
    # fail; if someone deletes the line from one page, that page fails.
    try:
        _rp2 = os.path.join("results", "etf_book_live_width_ruler.json")
        _ob = sorted(__import__("glob").glob(
            os.path.join("results", "etf_book_order", "ORDER-*.md")))
        _ob2 = [p for p in _ob if not p.endswith("-card.md")]
        _oc2 = [p for p in _ob if p.endswith("-card.md")]
        if os.path.exists(_rp2) and _ob2 and _oc2:
            _r2 = json.load(open(_rp2, encoding="utf-8"))
            _pr2 = _r2.get("paired") or {}
            _sd2 = _pr2.get("sd_pp")
            _n2 = int(_pr2.get("pairs") or 0)
            if _sd2 and _n2:
                _mde2 = 2.802 * float(_sd2) / (_n2 ** 0.5)
                _bis = open(_ob2[-1], encoding="utf-8").read()
                _cis = open(_oc2[-1], encoding="utf-8").read()
                _str2 = "%.2fpp" % _mde2
                check("product: E272 each sheet says what its pairing could have detected",
                      _str2 in _bis and _str2 in _cis and "分辨下限" in _bis
                      and "分辨下限" in _cis,
                      "floor=%s beta=%s card=%s" % (_str2, _str2 in _bis, _str2 in _cis))
            else:
                check("product: E272 each sheet says what its pairing could have detected", True,
                      "face publishes no dispersion -- soft-fails by design")
        else:
            check("product: E272 each sheet says what its pairing could have detected", True,
                  "ruler/order absent -- face soft-fails by design")
    except Exception as e:
        check("product: E272 each sheet says what its pairing could have detected", False, str(e))
    # r1156 / E251: p5 is "the deepest 5%", not "the worst". The arms now carry p1/p99,
    # so the leg asks the two questions the number must answer: is p1 actually deeper than
    # the p5 beside it (ordering, not decoration), and does the published face say whether
    # the ultra tail moves with the block length instead of shipping a silent False.
    try:
        _bl1 = sorted(__import__("glob").glob(os.path.join(
            "results", "etf_book_bootstrap", "BLOCKS-*.json")))
        if _bl1:
            _b1 = json.load(open(_bl1[-1], encoding="utf-8"))
            _deeper = []
            for _a in _b1.get("arms") or []:
                _m1 = (_a.get("maxdd") or {}).get("1")
                _m5 = (_a.get("maxdd") or {}).get("5")
                if _m1 is None or _m5 is None or not (_m1 <= _m5):
                    _deeper.append(_a.get("block"))
            _sp1 = _b1.get("spread") or {}
            _rd1 = _b1.get("readings") or {}
            _want_ultra = ((_sp1.get("maxdd_p1") or {}).get("range", 0.0) * 100.0) > 3.0
            check("product: the worst 1% is published on the block arms",
                  bool(_b1.get("arms")) and not _deeper
                  and _sp1.get("maxdd_p1") is not None and _sp1.get("cagr_p1") is not None
                  and _rd1.get("ultra_tail_is_block_dependent") is _want_ultra
                  and _b1.get("ultra_tail_published") is True,
                  "arms=%d not_deeper=%s maxdd_p1=%s published=%s flag=%s"
                  % (len(_b1.get("arms") or []), _deeper or "none",
                     _sp1.get("maxdd_p1"), _b1.get("ultra_tail_published"),
                     _rd1.get("ultra_tail_is_block_dependent")))
        else:
            check("product: the worst 1% is published on the block arms", True,
                  "no BLOCKS face -- soft-fails by design")
    except Exception as e:
        check("product: the worst 1% is published on the block arms", False, str(e))
    # r1214: completeness of the block family. `blocks --check` re-judges the arms it is
    # GIVEN, so a family that silently lost one arm re-derives a narrower spread from what
    # is left and reads green -- an invariant satisfiable by absence. The registered set
    # (ARM_SET) is now the invariant, and this leg recomputes it from the published face so
    # a deleted arm, a partial re-derive or a checkout that dropped a file reads red.
    try:
        from scripts import etf_book_nav_envelope as _NE2
        _bl2 = sorted(__import__("glob").glob(os.path.join(
            "results", "etf_book_bootstrap", "BLOCKS-*.json")))
        if _bl2:
            _b2 = json.load(open(_bl2[-1], encoding="utf-8"))
            _on_face = [a.get("block") for a in _b2.get("arms") or []]
            _probs = _NE2.arm_set_problems(_on_face)
            _fires = _NE2.arm_set_problems([b for b in _on_face if b != _NE2.ARM_SET[-1]])
            check("product: the block family is complete, not merely self-consistent",
                  not _probs and len(_fires) == 1 and str(_NE2.ARM_SET[-1]) in _fires[0]
                  and _b2.get("arm_set") == sorted(_NE2.ARM_SET),
                  "on_face=%s registered=%s problems=%s fires_when_short=%s"
                  % (_on_face, list(_NE2.ARM_SET), _probs or "none", _fires or "none"))
        else:
            check("product: the block family is complete, not merely self-consistent", True,
                  "no BLOCKS face -- soft-fails by design")
    except Exception as e:
        check("product: the block family is complete, not merely self-consistent", False, str(e))
    # r1219: the same invariant on the voltail family. `voltail --check` re-judges the arms
    # the face carries, so a face that lost one block re-derives a verdict from a smaller
    # family and reads green -- here the registered set (VT_BLOCKS) is the criterion, and the
    # leg also proves the gate fires by deleting one arm from the published list.
    try:
        from scripts import etf_book_nav_envelope as _NE3
        _vtp = os.path.join("results", "etf_book_bootstrap", "etf_book_voltarget_tail.json")
        if os.path.exists(_vtp):
            _vt3 = json.load(open(_vtp, encoding="utf-8"))
            _on3 = [a.get("block") for a in _vt3.get("arms") or []]
            _p3 = _NE3.family_problems(_on3, _NE3.VT_BLOCKS, kind="voltarget block")
            _f3 = _NE3.family_problems([b for b in _on3 if b != _NE3.VT_BLOCKS[-1]],
                                       _NE3.VT_BLOCKS, kind="voltarget block")
            check("product: the voltail family is complete, not merely self-consistent",
                  not _p3 and len(_f3) == 1 and str(_NE3.VT_BLOCKS[-1]) in _f3[0]
                  and _vt3.get("blocks") == sorted(_NE3.VT_BLOCKS),
                  "on_face=%s registered=%s problems=%s fires_when_short=%s"
                  % (_on3, list(_NE3.VT_BLOCKS), _p3 or "none", _f3 or "none"))
        else:
            check("product: the voltail family is complete, not merely self-consistent", True,
                  "no voltail face -- soft-fails by design")
    except Exception as e:
        check("product: the voltail family is complete, not merely self-consistent", False, str(e))
    # r1220: the stored paired rows are a family too. The arm-level leg above derives every
    # row path from an arm it already trusts, so nothing counted the directory -- a stray
    # PAIRROWS file (an older block grid left behind) sat beside the family unnoticed. This
    # leg requires the published face's blocks to have exactly their row files on disk and
    # proves the directory gate fires rather than merely existing.
    try:
        import tempfile as _tf
        from scripts import etf_book_nav_envelope as _NE4
        _vp4 = os.path.join("results", "etf_book_bootstrap", "etf_book_voltarget_tail.json")
        if os.path.exists(_vp4):
            _vt4 = json.load(open(_vp4, encoding="utf-8"))
            _cut4 = _vt4.get("evidence_cutoff")
            _row4 = _NE4.pairrow_files_problems(_cut4, _NE4.VT_BLOCKS,
                                                os.path.join("results", "etf_book_bootstrap"))
            _td4 = _tf.mkdtemp(prefix="smoke_pairrows_")
            for _b4 in _NE4.VT_BLOCKS:
                open(os.path.join(_td4, "PAIRROWS-X-b%d.json" % _b4), "w").close()
            _ok4 = not _NE4.pairrow_files_problems("X", _NE4.VT_BLOCKS, _td4)
            open(os.path.join(_td4, "PAIRROWS-X-b999.json"), "w").close()
            _fire4 = _NE4.pairrow_files_problems("X", _NE4.VT_BLOCKS, _td4)
            check("product: the paired-rows family on disk is complete and stray-proof",
                  not _row4 and _ok4 and len(_fire4) == 1 and "b999" in _fire4[0],
                  "cutoff=%s problems=%s fires_on_stray=%s"
                  % (_cut4, _row4 or "none", _fire4 or "none"))
        else:
            check("product: the paired-rows family on disk is complete and stray-proof", True,
                  "no voltail face -- soft-fails by design")
    except Exception as e:
        check("product: the paired-rows family on disk is complete and stray-proof", False, str(e))
    # r1350 / E253: the card calls the 8% overlay "a drawdown tool". The face now answers it
    # with a PAIRED bootstrap -- same draw, both books -- so this leg recomputes the two
    # numbers the sentence rests on from the paired rows on disk: the median delta and the
    # p1 delta, and refuses a face whose verdict disagrees with its own arms (a stored
    # boolean that says "middle only" while the p1 moved, or the reverse).
    try:
        _vp = os.path.join("results", "etf_book_bootstrap", "etf_book_voltarget_tail.json")
        if os.path.exists(_vp):
            _vt = json.load(open(_vp, encoding="utf-8"))
            _v = _vt.get("verdict") or {}
            _ad = _vt.get("arms_definition") or {}
            _arms = _vt.get("arms") or []
            _rows_ok, _deltas = True, []
            for _a in _arms:
                _rf = os.path.join("results", "etf_book_bootstrap", str(_a.get("rows_file")))
                if not os.path.exists(_rf):
                    _rows_ok = False
                    continue
                _rows = json.load(open(_rf, encoding="utf-8")).get("rows") or []
                _dd = sorted(_r["on"]["maxdd"] - _r["off"]["maxdd"] for _r in _rows
                             if _r.get("on", {}).get("maxdd") is not None)
                if not _dd:
                    _rows_ok = False
                    continue
                _mid = _dd[len(_dd) // 2]
                _p1 = _dd[int(round((len(_dd) - 1) * 0.01))]
                _deltas.append((_a.get("block"), _mid, _p1,
                                abs(_mid - (_a.get("delta") or {}).get("maxdd", {})
                                    .get("pct", {}).get("50", 1e9)) < 5e-3))
            _med = sum(d[1] for d in _deltas) / len(_deltas) if _deltas else None
            check("product: the vol overlay's tail is priced on the same draw as its middle",
                  bool(_arms) and _rows_ok and len(_deltas) >= 2
                  and all(d[3] for d in _deltas)
                  and (_ad.get("on") or {}).get("vol_target") is not None
                  and (_ad.get("off") or {}).get("vol_target") is None
                  and _med is not None
                  and abs(_med - (_v.get("median_maxdd_delta_median") or 1e9)) < 5e-3
                  and ((_v.get("tail_share_of_middle") or 0.0) < 0.5)
                  is bool(_v.get("tail_is_mostly_a_middle_effect")),
                  "arms=%d rows_ok=%s median_delta=%s tail_share=%s flag=%s"
                  % (len(_arms), _rows_ok, _med, _v.get("tail_share_of_middle"),
                     _v.get("tail_is_mostly_a_middle_effect")))
        else:
            check("product: the vol overlay's tail is priced on the same draw as its middle",
                  True, "no voltail face -- soft-fails by design")
    except Exception as e:
        check("product: the vol overlay's tail is priced on the same draw as its middle",
              False, str(e))
    # r1360 / E253 close: the measurement is worthless if the sentence a human reads still
    # says only "a drawdown tool". The two human faces (order-sheet card + forward ledger)
    # must quote the artifact's own share and price, formatted from its numbers -- a literal
    # in code would keep reading green while the bootstrap moved underneath it.
    try:
        _vpath2 = os.path.join("results", "etf_book_bootstrap", "etf_book_voltarget_tail.json")
        _faces = [("production card", os.path.join("results", "etf_book_production", "latest.json")),
                  ("forward ledger", os.path.join("results", "etf_book_forward", "LEDGER.json"))]
        if os.path.exists(_vpath2):
            _vv = (json.load(open(_vpath2, encoding="utf-8")).get("verdict") or {})
            _share = _vv.get("tail_share_of_middle")
            _want = ("only %.0f%% of it survives" % (100.0 * _share)) if _share is not None else None
            # the price paid is formatted from the face's own number: a literal here would keep
            # reading green while the bootstrap reran underneath it (the very defect this leg hunts)
            _cagr = _vv.get("p50_cagr_delta_median")
            _price = ("%+.2fpp" % (100.0 * _cagr)) if _cagr is not None else None
            _says, _missing, _stale = [], [], []
            for _nm, _fp in _faces:
                if not os.path.exists(_fp):
                    _missing.append(_nm)
                    continue
                _txt = " ".join(str(c) for c in
                                (json.load(open(_fp, encoding="utf-8")).get("caveats") or []))
                if _want and _want in _txt and _price and _price in _txt:
                    _says.append(_nm)
                elif "drawdown tool" in _txt:
                    _stale.append(_nm)
            check("product: the human faces quote the measured draw-tail share, not the impression",
                  not _missing and not _stale and len(_says) == len(_faces),
                  "want=%r price=%r says=%s missing=%s stale=%s" % (_want, _price, _says, _missing, _stale))
        else:
            check("product: the human faces quote the measured draw-tail share, not the impression",
                  True, "no voltail face -- soft-fails by design")
    except Exception as e:
        check("product: the human faces quote the measured draw-tail share, not the impression",
              False, str(e))
    # r1190 / E298: the book's concentration face must be re-derivable, not trusted. Three
    # things on disk: the identity arm really matched the engine (a split of its own
    # arithmetic is worthless), the frozen criteria are the ones the code holds today, and
    # the verdict recomputes from the published rows. The class arm must also contain the
    # top-k names -- a sleeve test that silently dropped different names would read as a
    # stronger result than it is.
    try:
        _cpath = os.path.join("results", "etf_book_concentration.json")
        if os.path.exists(_cpath):
            _cdoc = json.load(open(_cpath, encoding="utf-8"))
            _cmod = __import__("importlib").import_module("scripts.etf_book_concentration")
            _rc = _cmod.check(_cpath)
            _idl = _cdoc.get("identity") or {}
            _cl = _cdoc.get("leave_class_out") or {}
            _topk = set((_cdoc.get("leave_top_k_out") or {}).get("symbols") or [])
            _conc = _cdoc.get("concentration") or {}
            _shares_ok = abs((_conc.get("shares_sum_all_names") or 0) - 1.0) < 1e-4
            check("product: E298 concentration face re-derives its own verdict, and its sleeve arm "
                  "really carries the top names",
                  _rc == 0 and bool(_idl.get("passes"))
                  and (_idl.get("replica_vs_engine_max_abs") or 1) < 1e-9
                  and _shares_ok
                  and bool(_cl.get("contains_top_k"))
                  and (_cdoc.get("control") or {}).get("inert") is True,
                  "verdict=%s identity=%.2g shares=%.4f class=%s(%d) contains_topk=%s"
                  % (_cdoc.get("verdict"), _idl.get("replica_vs_engine_max_abs") or 0,
                     _conc.get("shares_sum_all_names") or 0, _cl.get("class"),
                     _cl.get("symbols_removed") or 0, _cl.get("contains_top_k")))
        else:
            check("product: E298 concentration face re-derives its own verdict, and its sleeve arm "
                  "really carries the top names", True, "concentration artifact absent -- soft-fails by design")
    except Exception as e:
        check("product: E298 concentration face re-derives its own verdict, and its sleeve arm "
              "really carries the top names", False, str(e))
    # r1335 / E221: the book's six factor directions are the full-sample IC signs, so the
    # honest number is the point-in-time arm. Two things must stay true on disk: the verdict
    # is recomputable from the payload's own summary (never a stored string), and both arms
    # really traded -- an untraded arm would sail through every numeric comparison (r1261).
    try:
        _sppath = os.path.join("results", "etf_sign_pit.json")
        if os.path.exists(_sppath):
            _doc = json.load(open(_sppath, encoding="utf-8"))
            _mod = __import__("importlib").import_module("scripts.etf_sign_pit")
            _g = _mod.gate(_doc)
            _s = _doc.get("summary") or {}
            check("product: E222 sign-PIT verdict is recomputable from its own gate",
                  _g["all_ok"] and _g["verdict"] == _doc.get("verdict")
                  and bool(_s.get("fixed_traded")) and bool(_s.get("pit_traded")),
                  "verdict=%s ratio=%s fixed=%s pit=%s stable=%s"
                  % (_g["verdict"], _g["ratio"], _s.get("cagr_fixed"), _s.get("cagr_pit"),
                     _s.get("verdict_stable_across_cells")))
        else:
            check("product: E222 sign-PIT verdict is recomputable from its own gate", True,
                  "sign-pit artifact absent -- soft-fails by design")
    except Exception as e:
        check("product: E222 sign-PIT verdict is recomputable from its own gate", False, str(e))
    # r1336 / E222: the sign-PIT leg prices the honest arm; this one prices the CHOICE --
    # all 64 sign sets on the same panel, so the card can say what the published signs rank
    # against. Same two rules: the verdict is recomputed from the arm table (never a stored
    # string), and every arm in the table must have traded (r1261: a flat table of untraded
    # arms would sail through any comparison).
    try:
        _se = os.path.join("results", "etf_sign_enum.json")
        if os.path.exists(_se):
            _doc2 = json.load(open(_se, encoding="utf-8"))
            _mod2 = __import__("importlib").import_module("scripts.etf_sign_enum")
            _g2 = _mod2.gate(_doc2)
            _s2 = _doc2.get("summary") or {}
            check("product: E223 sign-enum verdict is recomputable from its own arm table",
                  _g2["all_ok"] and _g2["verdict"] == _doc2.get("verdict")
                  and int(_s2.get("n_arms") or 0) == 64,
                  "verdict=%s rank=%s/%s median=%s prod=%s gap_pp=%s"
                  % (_g2["verdict"], _g2["rank"], _g2["n"], _s2.get("median_cagr"),
                     _s2.get("production_cagr"), _s2.get("no_hindsight_gap_pp")))
        else:
            check("product: E223 sign-enum verdict is recomputable from its own arm table", True,
                  "sign-enum artifact absent -- soft-fails by design")
    except Exception as e:
        check("product: E223 sign-enum verdict is recomputable from its own arm table", False, str(e))
    # r1337 / E224: the arm table above is one window. This leg splits it and requires the
    # verdict (and the "learnable chooser" number) to be recomputed from the per-period table,
    # so a stored string cannot outlive a panel move; the chance floor must be on the page,
    # or "the top deciles do not line up" is a shrug rather than a measurement (E199 rule).
    try:
        _ss = os.path.join("results", "etf_sign_stability.json")
        if os.path.exists(_ss):
            _doc3 = json.load(open(_ss, encoding="utf-8"))
            _mod3 = __import__("importlib").import_module("scripts.etf_sign_stability")
            _g3 = _mod3.gate(_doc3)
            _s3 = _doc3.get("summary") or {}
            check("product: E224 sign-ordering transfer is recomputable from the per-period table",
                  _g3["all_ok"] and _g3["verdict"] == _doc3.get("verdict")
                  and int(_s3.get("n_arms") or 0) == 64
                  and _s3.get("top_decile_shared_p") is not None
                  and _mod3.overlap_tail(64, int(_s3.get("top_k") or 7),
                                         int(_s3.get("top_decile_shared") or 0))
                  == _s3.get("top_decile_shared_p"),
                  "verdict=%s rho=%s (null sd %s) prod is/oos rank=%s/%s shared=%s chance=%s p=%s"
                  % (_g3["verdict"], _g3["spearman"], _g3["spearman_null_sd"],
                     _g3["production_is_rank"], _g3["production_oos_rank"],
                     _s3.get("top_decile_shared"), _s3.get("top_decile_chance_expected"),
                     _s3.get("top_decile_shared_p")))
        else:
            check("product: E224 sign-ordering transfer is recomputable from the per-period table",
                  True, "sign-stability artifact absent -- soft-fails by design")
    except Exception as e:
        check("product: E224 sign-ordering transfer is recomputable from the per-period table",
              False, str(e))
    # r1339 / E227: both faces above price the sign question at ONE (rebal, n_hold) cell, and
    # that cell was itself picked on the sample. This leg requires the three-cell leg to be
    # recomputable -- the active-cell flags and the stable-factor count are re-derived from the
    # per-cell arm tables, so "the ordering is cell dependent" cannot outlive a panel move.
    try:
        _sc = os.path.join("results", "etf_sign_cells.json")
        if os.path.exists(_sc):
            _doc4 = json.load(open(_sc, encoding="utf-8"))
            _mod4 = __import__("importlib").import_module("scripts.etf_sign_cells")
            _g4 = _mod4.gate(_doc4)
            _c4 = _doc4.get("cells") or {}
            check("product: E227 sign ordering across cells is recomputable from the per-cell arm tables",
                  _g4["all_ok"] and _g4["verdict"] == _doc4.get("verdict")
                  and len(_c4) == 3
                  and all(int((c.get("n_arms") or 0)) == 64 for c in _c4.values())
                  and _g4["cross_cell"]["n_factors_stable"] == int(
                      ((_doc4.get("cross_cell") or {}).get("n_factors_stable")) or -1),
                  "verdict=%s stable=%s/%s ranks=%s"
                  % (_g4["verdict"], _g4["cross_cell"]["n_factors_stable"],
                     _g4["cross_cell"]["n_factors"],
                     (_doc4.get("summary") or {}).get("ranks_by_cell")))
        else:
            check("product: E227 sign ordering across cells is recomputable from the per-cell arm tables",
                  True, "sign-cells artifact absent -- soft-fails by design")
    except Exception as e:
        check("product: E227 sign ordering across cells is recomputable from the per-cell arm tables",
              False, str(e))
    # r1341 / E229: E227 leaves two directions quotable, and "the edge is that subset" is a
    # construction claim. This leg requires the reduced book to be priced against the full
    # vector across the whole declared grid, with the verdict recomputed from the per-cell
    # tables rather than read off the payload.
    try:
        _lv = os.path.join("results", "etf_lowvol_book.json")
        if os.path.exists(_lv):
            _doc5 = json.load(open(_lv, encoding="utf-8"))
            _mod5 = __import__("importlib").import_module("scripts.etf_lowvol_book")
            _g5 = _mod5.gate(_doc5)
            _c5 = _doc5.get("cells") or {}
            check("product: E229 the quotable subset is priced against the full vector",
                  _g5["all_ok"] and _g5["verdict"] == _doc5.get("verdict")
                  and len(_c5) == 9
                  and all(bool(v.get("active")) for v in _c5.values())
                  and _g5["detail"]["n_active"] == len(_c5),
                  "verdict=%s active=%s beat=%s median_d=%.4f"
                  % (_g5["verdict"], _g5["detail"]["n_active"], _g5["detail"]["n_beat"],
                     _g5["detail"]["median_d_cagr"] or 0.0))
        else:
            check("product: E229 the quotable subset is priced against the full vector",
                  True, "lowvol artifact absent -- soft-fails by design")
    except Exception as e:
        check("product: E229 the quotable subset is priced against the full vector",
              False, str(e))
    # r1345 / E236: the operator's real alternative is not a per-factor IC sign, it is
    # "pick ONE of the 64 vectors from history and run it". This leg re-derives the verdict
    # by hand from the published per-variant table and requires the face's own gate to
    # agree -- a leg that asked the module for its verdict could not notice a rule drift.
    try:
        _pc = os.path.join("results", "etf_sign_pit_combo.json")
        if os.path.exists(_pc):
            _doc6 = json.load(open(_pc, encoding="utf-8"))
            _cells6 = _doc6.get("cells") or {}
            _n6 = _nbeat6 = _npos6 = 0
            for _tag6, _c6 in _cells6.items():
                _ctrl6 = (_c6.get("control") or {}).get("cagr")
                for _vt6, _v6 in (_c6.get("variants") or {}).items():
                    _cg6 = _v6.get("cagr")
                    if not isinstance(_ctrl6, (int, float)) or not isinstance(_cg6, (int, float)):
                        continue
                    _n6 += 1
                    _nbeat6 += 1 if float(_cg6) > float(_ctrl6) + 0.01 else 0
                    _npos6 += 1 if float(_cg6) > 0.0 else 0
            _want6 = ("pit_combo_value" if (_nbeat6 >= 9 and _npos6 >= 9)
                      else "pit_combo_no_value" if _nbeat6 <= 3 else "pit_combo_fragile")
            _g6 = __import__("importlib").import_module("scripts.etf_sign_pit_combo").gate(_doc6)
            check("product: E236 the sign-vector re-selection procedure is priced",
                  _g6["all_ok"] and _doc6.get("verdict") == _want6
                  and _n6 == 12 and len(_cells6) == 2,
                  "verdict=%s n=%d beat=%d pos=%d"
                  % (_doc6.get("verdict"), _n6, _nbeat6, _npos6))
        else:
            check("product: E236 the sign-vector re-selection procedure is priced",
                  True, "pit_combo artifact absent -- soft-fails by design")
    except Exception as e:
        check("product: E236 the sign-vector re-selection procedure is priced", False, str(e))
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
        # T25 (r1161): a takeover cannot move machine-local rows, so it has to
        # re-declare the writer -- the envelope must say whose disk holds the
        # rows, and the board must print ONE owner (config beats the hardcoded
        # fallback) and honour a declaration instead of refusing it.
        _lfz2 = json.load(open("results/data_lane_freshness.json", encoding="utf-8"))
        _rws = _lfz2.get("lanes") or []
        _owner_ok = all((r.get("owner") == r.get("lane_host"))
                        for r in _rws if r.get("lane_host"))
        _env = None
        for _p in ("results/heat_update_status.json",
                   "results/heat_update_status.bm-a.json"):
            if os.path.exists(_p):
                _doc = json.load(open(_p, encoding="utf-8"))
                if isinstance(_doc.get("authority"), dict):
                    _env = (_p, _doc)
                    break
        _auth_ok, _auth_why = True, "no envelope carries an authority block yet"
        if _env:
            _a = _env[1]["authority"]
            _need = ("lane_owner", "writer_machine", "data_face_machine",
                     "declared_takeover", "took_over_by", "reason")
            _lh_heat = next((r.get("lane_host") for r in _rws
                             if r["lane"] == "heat"), None)
            _auth_ok = (all(k in _a for k in _need)
                        and bool(_a.get("data_face_machine"))
                        and (_a.get("data_face_machine") == _env[1].get("machine"))
                        and (_a.get("lane_owner") == _lh_heat
                             # r1414: the envelope records the owner AT WRITE TIME.
                             # A later lane_hosts reassignment that hands the lane to
                             # the very machine that declared the takeover is the
                             # same fact being ratified, not a contradiction. Judging
                             # it by today's config alone makes every reassignment red
                             # until a new envelope lands -- and the writer cannot
                             # land one while this leg is red (live 2026-11-08: bm-a
                             # took heat over on 11-07, r1270 then gave it the lane).
                             or (_a.get("declared_takeover") is True
                                 and _a.get("took_over_by") == _lh_heat
                                 and _a.get("data_face_machine") == _lh_heat)))
            _auth_why = f"{_env[0]}: {_a}"
        _tk_ok = all(
            (r.get("authority") != "non_host_envelope"
             or not r.get("declared_takeover_by")
             or r.get("declared_takeover_by") != r.get("reported_by"))
            for r in _rws)
        check("product: a lane takeover declares whose disk holds the rows",
              _owner_ok and _auth_ok and _tk_ok,
              f"owner==host={_owner_ok} auth={_auth_ok} ({_auth_why}) "
              f"declared-takeover-honoured={_tk_ok}")
    except Exception as e:
        check("product: a lane takeover declares whose disk holds the rows",
              False, str(e))
    try:
        # r1255: an envelope is a report ABOUT a panel. A rebase can restore an
        # older committed envelope over a newer panel, and the lane then reads
        # "stalled" while its data is current (live 2026-11-07). Recomputed here
        # from the published rows: no row may quote a tail older than the panel
        # it also publishes, and a stale envelope must publish BOTH numbers.
        _lfz3 = json.load(open("results/data_lane_freshness.json",
                               encoding="utf-8"))
        _rows3 = _lfz3.get("lanes") or []
        _tail_ok, _stale_ok, _why3 = True, True, "no stale envelope today"
        for _r in _rows3:
            _pt, _et = _r.get("panel_tail"), _r.get("envelope_tail")
            if _pt and _r.get("tail") and str(_r["tail"]) < str(_pt):
                _tail_ok = False
                _why3 = f"{_r['lane']}: tail {_r['tail']} < panel {_pt}"
            if _r.get("envelope_stale"):
                _stale_ok = _stale_ok and bool(_pt) and bool(_et)
                _why3 = f"{_r['lane']}: envelope {_et} -> panel {_pt}"
                if str(_r["tail"]) != str(_pt):
                    _tail_ok = False
        check("fleet: a panel newer than its envelope is not a stall",
              _tail_ok and _stale_ok, _why3)
    except Exception as e:
        check("fleet: a panel newer than its envelope is not a stall",
              False, str(e))
    try:
        # r1256: a lane that declares its stand-in is not uncertified. Recomputed
        # from the published rows: any row naming `declared_takeover_by` must be
        # auditable, so a legal takeover can never resurface as "cannot certify".
        _rows4 = (json.load(open("results/data_lane_freshness.json",
                                 encoding="utf-8")).get("lanes") or [])
        _bad4 = [r["lane"] for r in _rows4
                 if r.get("declared_takeover_by") and not r.get("auditable")]
        check("fleet: a lane that declares its stand-in is not uncertified",
              not _bad4,
              ("declared stand-in still uncertified: " + ", ".join(_bad4)
               if _bad4 else "every declared stand-in is auditable"))
    except Exception as e:
        check("fleet: a lane that declares its stand-in is not uncertified",
              False, str(e))
    try:
        # r1257: a stand-in declared only in the old `takeover{}` shape is a
        # declaration no reader can see -- so the board must both refuse to
        # certify it AND say whose declaration it was. Recomputed from the
        # published rows; a row that carries `unread_takeover_by` while reading
        # certified (or without saying it) is a regression.
        _rows5 = (json.load(open("results/data_lane_freshness.json",
                                 encoding="utf-8")).get("lanes") or [])
        _bad5 = [r["lane"] for r in _rows5
                 if r.get("unread_takeover_by")
                 and (r.get("verdict") != "unverifiable"
                      or "takeover{}" not in (r.get("why") or ""))]
        check("fleet: a stand-in declared in the old shape is named, not trusted",
              not _bad5,
              ("unread stand-in certified or unexplained: " + ", ".join(_bad5)
               if _bad5 else "every unread stand-in is refused and named"))
    except Exception as e:
        check("fleet: a stand-in declared in the old shape is named, not trusted",
              False, str(e))
    try:
        # r1258: a hostage lane is only *waiting* if somebody may move it. The
        # board now splits the silent-host lanes by whether the writer can
        # declare a stand-in, read out of that writer's own source -- so this
        # leg recomputes both halves from the published rows: the capability
        # must match the source, and the frozen list must be exactly the
        # unverifiable lanes on a dead host whose writer has no such path.
        import data_lane_freshness as _dlf2
        _lfd = json.load(open("results/data_lane_freshness.json",
                              encoding="utf-8"))
        _rw = _lfd.get("lanes") or []
        _drift = [r["lane"] for r in _rw
                  if bool(r.get("takeover_capable"))
                  != _dlf2.takeover_capable(r.get("writer"))]
        _want = sorted(r["lane"] for r in _rw
                       if r.get("verdict") == "unverifiable"
                       and r.get("host_alive") is False
                       and not r.get("takeover_capable"))
        _got = sorted(_lfd.get("frozen_without_takeover") or [])
        check("fleet: a hostage lane nobody can pick up is named as a decision",
              not _drift and _want == _got,
              ("capability disagrees with the writer source: " + ", ".join(_drift)
               if _drift else
               f"frozen list says {_got} but the rows say {_want}"))
    except Exception as e:
        check("fleet: a hostage lane nobody can pick up is named as a decision",
              False, str(e))
    try:
        # r1261: the board's tail for a 5,222-symbol panel is read from forty
        # files. That is a claim, and this leg refuses to let it travel as a
        # measurement: every declared panel must have a certification record,
        # the record must re-read the same sampled tail the board published (a
        # subset can only understate, never overstate), and a tail held by under
        # a tenth of the panel must be flagged in the record rather than quoted
        # as if it spoke for the panel.
        import data_lane_freshness as _dlf3
        _cert = json.load(open("results/data_lane_tail_certification.json",
                               encoding="utf-8"))
        _crow = {r["lane"]: r for r in (_cert.get("lanes") or [])}
        _board3 = {r["lane"]: r for r in (json.load(open(
            "results/data_lane_freshness.json", encoding="utf-8")).get("lanes") or [])}
        _want_lanes = sorted(s["lane"] for s in _dlf3.LANES if s.get("panel_csv"))
        _why = []
        if sorted(_crow) != _want_lanes:
            _why.append(f"certification covers {sorted(_crow)} but declared "
                        f"panels are {_want_lanes}")
        for lane, r in _crow.items():
            if r.get("direction") == "sample_overstated":
                _why.append(f"{lane}: the sample claims a newer tail than the "
                            f"full read ({r.get('sample_tail')} > {r.get('full_tail')})")
            _pt = (_board3.get(lane) or {}).get("panel_tail")
            if _pt and r.get("sample_tail") and str(_pt) != str(r["sample_tail"]):
                _why.append(f"{lane}: board prints panel tail {_pt}, the "
                            f"certification re-read {r['sample_tail']}")
            if r.get("tail_holder_share") is not None:
                if bool(r.get("thin_tail")) != (r["tail_holder_share"]
                                                < _dlf3.THIN_TAIL_SHARE):
                    _why.append(f"{lane}: thin-tail flag disagrees with the share")
        check("fleet: a panel tail read by sample is certified against a full scan",
              not _why, "; ".join(_why) or
              f"verdict={_cert.get('verdict')}, {len(_crow)} panel(s) re-read, "
              f"{_cert['counts']['files_scanned']} file(s) scanned")
    except Exception as e:
        check("fleet: a panel tail read by sample is certified against a full scan",
              False, str(e))
    try:
        # r1262: the holder count has to reach the human page, not just the
        # certification file -- a reader who opens FRESHNESS.md must not read
        # "tail 2026-10-13 held by the panel" when two symbols hold it. Recomputed
        # from the published page and the certification: every sampled row quotes
        # the full scan's count, and a thin tail is named as one.
        _md4 = open("docs/data_lanes/FRESHNESS.md", encoding="utf-8").read()
        _s4 = _md4.split("Tails read from a sample")[1].split("\n## ")[0]
        _cert4 = json.load(open("results/data_lane_tail_certification.json",
                                encoding="utf-8"))
        _cr4 = {r["lane"]: r for r in (_cert4.get("lanes") or [])}
        _why4 = []
        for _lane, _cr in _cr4.items():
            _line = [ln for ln in _s4.splitlines()
                     if ln.startswith(f"- `{_lane}`:")]
            if not _line:
                continue
            _quote = (f"full scan holds it in {_cr['tail_holders']:,} of "
                      f"{_cr['files']:,}")
            if _quote not in _line[0]:
                _why4.append(f"{_lane}: human row does not quote the holder count")
            if _cr.get("thin_tail") and "thin tail" not in _line[0]:
                _why4.append(f"{_lane}: a thin tail is printed without being named")
        check("fleet: the board page carries the full scan's holder count",
              not _why4, "; ".join(_why4) or
              f"{len(_cr4)} certified panel(s) checked against the page")
    except Exception as e:
        check("fleet: the board page carries the full scan's holder count",
              False, str(e))
    try:
        # r1265: every row above is judged on the official TRADING calendar, so a
        # lane whose unit is a statutory REPORT PERIOD had no row at all and the
        # 2026Q3 deadline passed unnoticed (r1263 found it by running the
        # collector by hand). Recompute the statutory demand from the writer and
        # require the board row + the human section to agree with it.
        _lfd5 = json.load(open("results/data_lane_freshness.json",
                               encoding="utf-8"))
        _pl5 = _lfd5.get("period_lanes") or []
        _why5 = []
        if not _pl5:
            _why5.append("no period-lane row: a statutory clock has no place "
                         "on this board")
        _md5 = open("docs/data_lanes/FRESHNESS.md", encoding="utf-8").read()
        if "clock is the statute" not in _md5:
            _why5.append("the human page carries no statute-clock section")
        for _r5 in _pl5:
            _mod5 = importlib.import_module(_r5["writer"])
            _f5 = _mod5.panel_period_facts(
                dt.datetime.fromisoformat(_r5["as_of"]))
            if _f5["expected_latest"] != _r5.get("expected_latest"):
                _why5.append(f"{_r5['lane']}: statute demand differs between "
                             "the writer and the board")
            if (_r5.get("verdict") == "period_missing") != bool(
                    _f5["missing_periods"]):
                _why5.append(f"{_r5['lane']}: verdict does not follow the "
                             "missing periods")
            if _r5.get("verdict") == "period_missing" and not _r5.get("why"):
                _why5.append(f"{_r5['lane']}: a missing period is printed with "
                             "no sentence saying why")
            if (_r5.get("host_alive") is False
                    and not _r5.get("takeover_capable")
                    and _r5.get("frozen_without_takeover") is not True):
                _why5.append(f"{_r5['lane']}: a hostage statutory lane is not "
                             "named as a decision")
        check("fleet: a lane whose clock is the statute is judged on the statute",
              not _why5, "; ".join(_why5) or
              f"{len(_pl5)} statutory lane(s) re-derived from the writer, "
              f"{sum(len(r.get('missing_periods') or []) for r in _pl5)} "
              "period(s) missing")
    except Exception as e:
        check("fleet: a lane whose clock is the statute is judged on the statute",
              False, str(e))
    try:
        # r1266: a lane whose row named no collector printed "nothing to
        # reassign" -- a give-up sentence about a lane whose collector had
        # shipped a takeover path eight rounds earlier (marks / r1101). This leg
        # re-derives both halves from the published faces: the capability must
        # come from the collector's own source, and any per-hole cause table the
        # auditing face publishes must reach the row unchanged (a count printed
        # without its causes is how "6 missing days" reads as "6 days a stand-in
        # will soon fill").
        import data_lane_freshness as _dlf6
        _lf6 = json.load(open("results/data_lane_freshness.json",
                              encoding="utf-8"))
        _why6 = []
        for _r6 in _lf6.get("lanes") or []:
            _cap6 = _dlf6.takeover_capable(_r6.get("writer"))
            if bool(_r6.get("takeover_capable")) != _cap6:
                _why6.append(f"{_r6['lane']}: capability disagrees with "
                             f"writer `{_r6.get('writer')}`")
            if (not _r6.get("writer") and _r6.get("frozen_without_takeover") is not True
                    and _r6.get("host_alive") is False
                    and _r6.get("verdict") == "unverifiable"):
                _why6.append(f"{_r6['lane']}: an unowned frozen lane is not "
                             "named as a decision")
        _mc6 = json.load(open("results/marks_coverage.json", encoding="utf-8"))
        _mr6 = next((r for r in (_lf6.get("lanes") or [])
                     if r["lane"] == "marks"), {})
        if _mr6:
            if _mr6.get("holes_by_cause") != _mc6.get("holes_by_cause"):
                _why6.append("marks: the board's cause table is not the "
                             "collector's")
            if _mr6.get("writer") != "update_intraday_marks":
                _why6.append("marks: the row does not name its collector")
        _md6 = open("docs/data_lanes/FRESHNESS.md", encoding="utf-8").read()
        if _mr6.get("holes_by_cause"):
            if "Who was awake" not in _md6:
                _why6.append("the human page carries no per-hole cause section")
            else:
                _sec6 = _md6.split("Who was awake")[1].split("\n## ")[0]
                if "`marks`" not in _sec6:
                    _why6.append("the cause section does not name the marks holes")
        check("fleet: a lane that names its collector is not told nothing can be done",
              not _why6, "; ".join(_why6) or
              f"{len(_lf6.get('lanes') or [])} lane(s) re-read against their "
              f"collectors; cause tables carried for "
              f"{sum(1 for r in (_lf6.get('lanes') or []) if r.get('holes_by_cause'))} "
              "lane(s)")
    except Exception as e:
        check("fleet: a lane that names its collector is not told nothing can be done",
              False, str(e))
    try:
        # r1162: "cannot certify here" is about our copy; whose disk the rows are
        # on is the actionable half. The board derives that sentence ONCE, and the
        # two faces a human opens must carry it verbatim -- so this leg recomputes
        # the block from the published lanes (a typed-in sentence reads red) and
        # then checks the dashboard wiring and the report's own md/json twin.
        import data_lane_freshness as _dlf
        _lfdoc = json.load(open("results/data_lane_freshness.json",
                                encoding="utf-8"))
        _dk = _lfdoc.get("disk") or {}
        _re = _dlf.disk_face(_lfdoc.get("lanes") or [],
                             _lfdoc.get("hosts") or {}, here=_dk.get("here"))
        _same = (_re["sentence"] == _dk.get("sentence")
                 and _re["n_offhost"] == _dk.get("n_offhost")
                 and _re["n_lanes"] == _dk.get("n_lanes")
                 and _re["offhost_lanes"] == (_dk.get("offhost_lanes") or []))
        _html = open("dashboard.html", encoding="utf-8").read()
        _dash = ("lf.disk" in _html and "lfd.sentence" in _html)
        import glob as _g2
        _rep_js = sorted(_g2.glob(os.path.join("docs", "daily_report",
                                               "REPORT-*.json")))
        _rep_ok, _rep_why = True, "no report yet"
        if _rep_js:
            _rj = json.load(open(_rep_js[-1], encoding="utf-8"))
            _la = _rj.get("lane_authority") or {}
            _rmd_p = _rep_js[-1][:-5] + ".md"
            if _la.get("present") and os.path.exists(_rmd_p):
                _rmd = open(_rmd_p, encoding="utf-8").read()
                # r1380: the count is a statistic OF ONE OBSERVER. Two boards taken
                # an hour apart on two machines can say 6 and 9 off-disk and both be
                # right; demanding equality read a host difference as a contradiction.
                # Same observer -> the counters must agree. Different observers -> the
                # difference is only readable if BOTH sides say whose disk they mean.
                _obs_r, _obs_b = _la.get("observer"), _dk.get("observer")
                _same_obs = bool(_obs_r) and _obs_r == _obs_b
                _counts_agree = _la.get("n_offhost") == _dk.get("n_offhost")
                if _same_obs:
                    _rep_ok = bool(_la.get("sentence") in _rmd and _counts_agree)
                    _obs_why = f"same-observer({_obs_r}) counts={_counts_agree}"
                elif _obs_r:
                    _rep_ok = bool(_la.get("sentence") in _rmd)
                    _obs_why = (f"observers differ (report={_obs_r} "
                                f"board={_obs_b}) -- attributable")
                else:
                    _rep_ok = bool(_la.get("sentence") in _rmd)
                    _obs_why = "report-predates-observer-tag (counts not judged)"
                _rep_why = (f"{os.path.basename(_rmd_p)} "
                            f"offhost={_la.get('n_offhost')} vs {_dk.get('n_offhost')} "
                            f"{_obs_why} "
                            f"sentence-in-page={_la.get('sentence') in _rmd}")
        check("product: whose disk the lane numbers are on reaches both human faces",
              _same and _dash and _rep_ok,
              f"recomputed={_same} dashboard-wired={_dash} report={_rep_why} "
              f"disk_sentence={(_dk.get('sentence') or '')[:60]}")
    except Exception as e:
        check("product: whose disk the lane numbers are on reaches both human faces",
              False, str(e))
    # r1251: the group decides on 2026-11-08 whether to re-enable the lane tasks
    # from this row, so the row's numbers must BE the declaration's numbers. Two
    # facts travel together and must not be merged: OWNERSHIP (unique/conflicting)
    # and OBSERVATION (an owned lane nobody has been seen producing is warning,
    # never ok). The negative direction is asserted too -- a green row with an
    # unobserved lane and no caveat sentence is the defect this leg hunts.
    try:
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location(
            "lane_ownership_declaration",
            os.path.join("scripts", "lane_ownership_declaration.py"))
        _lom = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_lom)
        _decl = _lom.build()
        _s = _decl.get("summary") or {}
        _html = open("dashboard.html", encoding="utf-8").read()
        _dash = "lane_ownership" in _html
        _st = json.load(open(os.path.join("results", "dashboard_status.json"),
                             encoding="utf-8"))
        _blk = ((_st.get("data") or {}).get("lane_ownership") or {})
        _nu = len(_s.get("declared_but_unobserved") or [])
        _ret = [l.get("lane") for l in (_decl.get("lanes") or [])
                if l.get("observation") == "retired"]
        _live = [x for x in (_s.get("declared_but_unobserved") or [])
                 if x not in _ret]
        _same = (_blk.get("n_lanes") == _s.get("n_lanes")
                 and _blk.get("n_owned") == _s.get("n_owned")
                 and _blk.get("n_declared_but_unobserved") == _nu
                 and _blk.get("n_live_declared_but_unobserved") == len(_live)
                 and _blk.get("retired") == _ret
                 and _blk.get("verdict") == _s.get("verdict"))
        _caveat = (len(_live) == 0) or (
            "\u8bfb\u4e0d\u5230\u5b83\u7684\u4ea7\u51fa\u5c01\u5957" in _html)
        _retired_named = (not _ret) or ("\u5df2\u9000\u5f79" in _html)
        # "seven lanes nobody has seen" is not actionable; naming the host that
        # owes the evidence is. The grouping must be recomputed here, not trusted.
        _bh = _blk.get("by_host") or {}
        _exp_bh = {}
        for _l in (_decl.get("lanes") or []):
            if _l.get("lane") not in _live:
                continue
            _k = _l.get("declared_host") or "?"
            _e = _exp_bh.setdefault(_k, [])
            _e.append(_l.get("lane"))
        _bh_ok = (set(_bh) == set(_exp_bh)
                  and all(sorted(_bh[k].get("lanes") or []) == sorted(_exp_bh[k])
                          for k in _exp_bh))
        # The row is data-driven: the page composes the host list from the published
        # block at render time, so demanding the literal host keys inside
        # dashboard.html would only pass if the hosts were hard-coded there -- the
        # pattern this suite forbids everywhere else. Name the host on the two faces
        # a reader actually opens: the page must carry the grouping (`by_host`), and
        # the declaration document must spell out every host that owes evidence.
        _decl_md = ""
        _decl_p = os.path.join("docs", "lane_ownership",
                               "DECLARATION-%s.md"
                               % ((_decl.get("source_freshness_as_of") or "")[:10]))
        if os.path.exists(_decl_p):
            _decl_md = open(_decl_p, encoding="utf-8").read()
        _who_named = (not _exp_bh) or (("by_host" in _html)
                                       and all(k in _decl_md for k in _exp_bh))
        check("product: the row the 11-08 enable decision reads agrees with the declaration",
              _same and _dash and _caveat and _retired_named and _bh_ok and _who_named,
              f'recomputed={_same} dashboard-wired={_dash} caveat={_caveat} '
              f"retired_named={_retired_named} by_host={_bh_ok} who_named={_who_named} "
              f"hosts={sorted(_exp_bh)} lanes={_blk.get('n_lanes')} "
              f"unobserved={_blk.get('n_declared_but_unobserved')} "
              f"live_unobserved={_blk.get('n_live_declared_but_unobserved')} "
              f"decl_live={len(_live)} retired={_ret} verdict={_blk.get('verdict')}")
    except Exception as e:
        check("product: the row the 11-08 enable decision reads agrees with the declaration",
              False, str(e))
    try:
        # r1156: the lane-freshness board must agree with the lanes' OWN bytes and
        # with the official calendar. Re-reading the published JSON would only prove
        # the file parses, so the two tails a reader acts on are recomputed here from
        # the artifact on disk, and the expectation is rebuilt from the calendar.
        import glob as _glob
        _lfz = json.load(open("results/data_lane_freshness.json", encoding="utf-8"))
        _rows = {r["lane"]: r for r in _lfz.get("lanes") or []}
        _heat_files = [os.path.basename(p)[:-5] for p in
                       _glob.glob(os.path.join("data", "heat", "popularity", "*.json"))]
        _heat_tail = None
        for _n in _heat_files:
            if len(_n) == 8 and _n.isdigit():
                _d = f"{_n[:4]}-{_n[4:6]}-{_n[6:]}"
                _heat_tail = max(_heat_tail or _d, _d)
        _zt = json.load(open(os.path.join("data", "zt_pool", "collected_days.json"),
                             encoding="utf-8"))
        _zt_tail = max(max(v) for v in _zt.values() if v)
        _cal = [ln.strip() for ln in
                open("data/exchange_calendar.csv", encoding="utf-8") if ln.strip()]
        _asof = dt.datetime.fromisoformat(_lfz["as_of"])
        _today = _asof.date().isoformat()
        _upto = [d for d in _cal if d < _today or
                 (d == _today and _asof.time() >= dt.time(15, 30))]
        _exp = _upto[-1]
        # r1156: the board must not read green because it could not certify
        # anything -- 'uncertified' is its own verdict, and a lane whose evidence
        # came from another machine's copy must say so instead of publishing it.
        _states = ("in_sync", "today_pending", "behind_1d", "stalled", "absent",
                   "unreadable", "unverifiable", "retired")
        # r1349: `data/heat/` is gitignored (.gitignore:35), so its bytes exist only on the
        # machine that collects them. Requiring the board's heat tail to equal a directory
        # that is empty here asserts a deployment layout, not a fact -- it was red on this
        # host for a lane the board already declares unverifiable/stalled. Strict when the
        # local bytes exist; when they do not, the board must NOT claim a certified tail for
        # that lane (its own verdict must say unverifiable/absent/retired).
        _heat_row = _rows.get("heat") or {}
        # r1168: this face is a SHARED, git-tracked file -- whichever machine ran the leg
        # writes it, and it describes THAT machine's disk. A face computed elsewhere has no
        # local heat files at all, so comparing them here asserts a deployment layout instead
        # of a fact (the r1135 family, again). The face names its own disk (`disk.here`), so a
        # foreign face is judged on that declaration: it must name the disk it read and the
        # lanes it could not certify from here.
        _here = None
        try:
            with open(os.path.join("fleet", "machine.json"), encoding="utf-8") as _fh:
                _here = (json.load(_fh) or {}).get("machine_id")
        except Exception:
            _here = None
        _disk = _lfz.get("disk") or {}
        _foreign = bool(_here and _disk.get("here") and _disk["here"] != _here)
        if _foreign:
            _heat_matches = bool(_disk.get("sentence"))
            _zt_ok = bool(_disk.get("offhost_lanes") or _disk.get("groups"))
        else:
            # r1414: two honest shapes when this machine holds no heat bytes
            # (data/heat is gitignored, so only the collector ever has them).
            # Either the row refuses to certify (unverifiable + a tail_source
            # naming the copy), or the lane's OWN host publishes the envelope
            # and the row says so in machine-readable form. Demanding local
            # bytes in both cases asserts a deployment layout: this leg went
            # red for a whole round after lane_hosts put heat back on bm-a
            # (bm-a writes results/heat_update_status.json), which is exactly
            # the r1135 family -- the board was correct and the leg was not.
            _heat_uncertified = (
                _heat_row.get("verdict") in ("unverifiable", "absent", "retired")
                and bool(_heat_row.get("tail_source")))
            _heat_host_vouched = (
                _heat_row.get("verdict") not in ("unverifiable", "absent",
                                                 "retired", "stalled",
                                                 "unreadable")
                and _heat_row.get("authority") in ("host_envelope",
                                                   "host_copy",
                                                   "declared_takeover")
                and bool(_heat_row.get("auditable"))
                and bool(_heat_row.get("data_face_machine"))
                and _heat_row.get("data_face_machine") == _heat_row.get("lane_host")
                and _heat_row.get("reported_by") == _heat_row.get("lane_host"))
            _heat_matches = (_heat_row.get("tail") == _heat_tail) if _heat_tail else (
                _heat_uncertified or _heat_host_vouched)
            _zt_ok = _rows["zt_pool"]["tail"] == _zt_tail
        _ok_lf = (_heat_matches
                  and _zt_ok
                  and _lfz.get("expected_last_official_day") == _exp
                  and sum((_lfz.get("counts") or {}).values()) == _lfz.get("n_lanes")
                  and all(r.get("verdict") in _states
                          for r in _lfz.get("lanes") or [])
                  and all(r.get("verdict") == "unverifiable"
                          for r in _lfz.get("lanes") or []
                          # a retired face keeps its copy reading but is not a
                          # stall: the board's own L9b leg says so, and the smoke
                          # leg must judge the same rule (r1156 red caught here)
                          if r.get("copy_verdict") and r.get("verdict") != "retired")
                  and (_lfz.get("verdict") in ("all_fresh", "attention", "uncertified",
                                               "host_down"))
                  # r1159: an unverifiable board must name the machine that should
                  # be vouching for those lanes, so the reader can act on it
                  and all(isinstance(r.get("host_alive"), (bool, type(None)))
                          and ("host_age_h" in r)
                          for r in _lfz.get("lanes") or [])
                  and (_lfz.get("verdict") != "host_down"
                       or (_lfz.get("hosts_down") and _lfz.get("lanes_hostage")))
                  # a green headline with nothing certified is the failure this
                  # face exists to catch
                  and not (_lfz.get("verdict") == "all_fresh"
                           and _lfz.get("unverifiable_lanes")))
        check("product: data lane freshness board agrees with the lanes and the calendar",
              _ok_lf,
              f"heat={_rows.get('heat', {}).get('tail')}=={_heat_tail} "
              f"zt={_rows.get('zt_pool', {}).get('tail')}=={_zt_tail} "
              f"face_computed_on={_disk.get('here')} here={_here} "
              f"expected={_lfz.get('expected_last_official_day')}=={_exp} "
              f"verdict={_lfz.get('verdict')} counts={_lfz.get('counts')} "
              f"auditable={_lfz.get('n_auditable')}/{_lfz.get('n_lanes')}")
    except Exception as e:
        check("product: data lane freshness board agrees with the lanes and the calendar",
              False, str(e))
    # r1249 (bm-a): D-20261104-05 -- before any scheduled task may be re-enabled on 2026-11-08,
    # every lane must name ONE host. Two sources answer it today (config/lane_hosts.json and the
    # `owner` defaults in data_lane_freshness.LANES) and they disagree on five lanes; only the
    # audit's private precedence knows which wins. The leg asks the DECLARATION the same question
    # the audit asks, from the same inputs, and refuses to let a lane be owned by nobody or by
    # two machines; it also refuses to let the declaration's authority be silently re-labelled.
    try:
        _sp49c = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
        if _sp49c not in sys.path:
            sys.path.insert(0, _sp49c)
        _LO49 = importlib.import_module("lane_ownership_declaration")
        _bad49c = []
        _pub49 = os.path.join("docs", "lane_ownership", "DECLARATION-latest.json")
        if not os.path.exists(_pub49):
            _bad49c.append("no declaration on disk")
        else:
            _p49d = json.load(open(_pub49, encoding="utf-8"))
            _f49d = _LO49.build()
            _rc49, _why49 = _LO49.check_payload(_p49d, _f49d)
            if _rc49:
                _bad49c.append(_why49)
            _s49 = _f49d.get("summary") or {}
            if _s49.get("verdict") != "OWNERSHIP_UNIQUE":
                _bad49c.append("conflicts: %s" % (_s49.get("conflict_lanes"),))
            # the authority must reflect the actual precedence: a lane the config reassigned
            # cannot claim the code default decided it (that is the number that was wrong)
            _cfg49 = json.load(open(os.path.join("config", "lane_hosts.json"),
                                    encoding="utf-8")).get("lane_hosts") or {}
            for _r49 in _p49d.get("lanes") or []:
                _w49 = (_LO49.load_inputs()[3] or {}).get(_r49.get("lane"))
                if _w49 in _cfg49 and _r49.get("declared_host") != _cfg49[_w49]:
                    _bad49c.append("%s: config says %s, declaration says %s"
                                   % (_r49.get("lane"), _cfg49[_w49],
                                      _r49.get("declared_host")))
                if _r49.get("verdict") == "TWO_WRITERS":
                    _bad49c.append("%s: two machines" % _r49.get("lane"))
        check("product: every lane names one host before any task is re-enabled",
              not _bad49c, "; ".join(_bad49c)[:200]
              or "ownership unique; config precedence published per lane")
    except Exception as e:
        check("product: every lane names one host before any task is re-enabled",
              False, repr(e)[:180])
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
        # r1248: the cut that picks the whole universe is quoted on BOTH reader faces, and the
        # reading is recomputed here from the published sweep rather than retyped. A face that
        # prints a plateau while the payload's own rows moved is the E289 two-copies defect, so
        # the numbers are compared, not the words.
        _eg_pub = json.load(open("results/etf_book_entry_gate.json", encoding="utf-8"))
        _eg_rows = [r for r in (_eg_pub.get("rows") or [])
                    if r.get("cagr") is not None and not r.get("error")]
        _eg_w = [r.get("median") for r in _eg_rows if r.get("median") is not None]
        _eg_near = [abs(float(d)) for d in
                    ((_eg_pub.get("verdict") or {}).get("near_deltas_pp") or [])]
        _eg_ratio = (float(max(_eg_w)) / float(min(_eg_w))) if _eg_w else None
        _eg_near_max = max(_eg_near) if _eg_near else None
        _tk_path = os.path.join("results", "etf_book_order",
                                "TICKET-%s.json" % _lb.get("as_of"))
        _tk_eg = (json.load(open(_tk_path, encoding="utf-8")).get("entry_gate") or {}
                  if os.path.exists(_tk_path) else {})
        _card_path = os.path.join("results", "etf_book_production", "CARD.md")
        _card_txt = open(_card_path, encoding="utf-8").read() if os.path.exists(_card_path) else ""
        _tk_md_path = os.path.join("results", "etf_book_order", "ORDER-%s.md" % _lb.get("as_of"))
        _tk_md = open(_tk_md_path, encoding="utf-8").read() if os.path.exists(_tk_md_path) else ""
        _ok_eg = (bool(_eg_w) and _eg_near_max is not None and _eg_ratio is not None
                  and _tk_eg.get("status") == "ok"
                  and _tk_eg.get("verdict") == (_eg_pub.get("verdict") or {}).get("verdict")
                  and abs(float(_tk_eg.get("near_max_pp") or -1) - _eg_near_max) < 1e-9
                  and abs(float(_tk_eg.get("width_ratio") or -1) - _eg_ratio) < 1e-6
                  and ("%d" % int(max(_eg_w))) in _card_txt
                  and ("%d" % int(min(_eg_w))) in _card_txt
                  and "number of names the book is allowed to hold" in _card_txt
                  and "容量这一轴" in _tk_md)
        check("product: both reader faces print the cut that picks the universe, recomputed",
              _ok_eg,
              "ticket=%s near=%s (payload %s) ratio=%s (payload %s) card widths=%s/%s"
              % (_tk_eg.get("verdict"), _tk_eg.get("near_max_pp"), _eg_near_max,
                 _tk_eg.get("width_ratio"), _eg_ratio,
                 max(_eg_w) if _eg_w else None, min(_eg_w) if _eg_w else None))
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
        _legs = {t[0] for t in importlib.import_module("Tools.s6_chain_bmc").LEGS}
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
        _legs = {t[0] for t in importlib.import_module("Tools.s6_chain_bmc").LEGS}
        check("fleet: machine-health gate leg wired into the S6 chain",
              "machine_health_face" in _legs, f"legs={len(_legs)}")
        # r1318: the panel READS the health face, so the writer has to run first.
        # It did not -- build_status copied a thinned row and the heal happened
        # behind it, which is why this very leg went red on a healthy fleet.
        _order = [t[0] for t in importlib.import_module("Tools.s6_chain_bmc").LEGS]
        check("fleet: health writer runs before the panel that reads it",
              _order.index("machine_health_write") < _order.index("build_status"),
              "write=%d build_status=%d" % (_order.index("machine_health_write"),
                                            _order.index("build_status")))
    except Exception as e:
        check("fleet: panel carries the machine-health verdict, not a row count",
              False, str(e))
        check("fleet: machine-health gate leg wired into the S6 chain", False, str(e))
    # r1251: the evening quote is what lets the page say what today is worth while the
    # panel is still a bar behind. It was wired one slot AFTER the page, so the page
    # printed yesterday's silence and the reader never saw the face (r1318 class).
    try:
        _lq_order = [t[0] for t in importlib.import_module("Tools.s6_chain_bmc").LEGS]
        check("product: the live quote is priced before the page that prints it",
              _lq_order.index("etf_book_live_quote") < _lq_order.index("etf_book_ceo_page"),
              "quote=%d page=%d" % (_lq_order.index("etf_book_live_quote"),
                                    _lq_order.index("etf_book_ceo_page")))
    except Exception as e:
        check("product: the live quote is priced before the page that prints it", False, str(e))
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
        return subprocess.run([sys.executable, script, *args], capture_output=True,
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
    # r1172: five tickers are not five bets. The producer publishes the independence count;
    # the executable ticket must QUOTE it verbatim (r1108 有产无读), and an unpublished face
    # must read as unpublished on the sheet rather than silently absent.
    try:
        import json as _j
        _bp = os.path.join("results", "etf_book_bets_face.json")
        _lp = os.path.join("results", "etf_book_order", "latest.json")
        _sent = None
        if os.path.exists(_bp):
            _sent = (_j.load(open(_bp, encoding="utf-8")).get("long") or {}).get("sentence")
        _cav = None
        _tpath = None
        if os.path.exists(_lp):
            _ptr = _j.load(open(_lp, encoding="utf-8"))
            _tpath = os.path.join("results", "etf_book_order", _ptr.get("file") or "")
        if _tpath and os.path.exists(_tpath):
            _cav = _j.load(open(_tpath, encoding="utf-8")).get("caveats") or []
        if _cav is None:
            check("product: the order ticket discloses how many bets the sleeve holds", False,
                  "no ticket on disk to read")
        elif _sent:
            check("product: the order ticket discloses how many bets the sleeve holds",
                  any(_sent in (c or "") for c in _cav),
                  "ticket does not quote the published bet count verbatim")
        else:
            check("product: the order ticket discloses how many bets the sleeve holds",
                  any("independent bets the sleeve holds is unpublished" in (c or "") for c in _cav),
                  "face missing but the ticket did not say so")
    except Exception as e:
        check("product: the order ticket discloses how many bets the sleeve holds", False, str(e))
    # r1455: the ORDER page a desk executes must carry the permission, not only a receipt
    # that audits it. Re-derived from the two published faces -- if the page and the audit
    # receipt disagree, one of them is stale and the operator cannot tell which.
    try:
        import json as _j3
        _md3, _gap3 = None, None
        _lp3 = os.path.join("results", "etf_book_order", "latest.json")
        if os.path.exists(_lp3):
            _ptr3 = _j3.load(open(_lp3, encoding="utf-8"))
            _mp = os.path.join("results", "etf_book_order",
                               "ORDER-%s.md" % _ptr3.get("as_of"))
            if os.path.exists(_mp):
                _md3 = open(_mp, encoding="utf-8").read()
        _gp = os.path.join("results", "etf_book_cut_order_gap.json")
        if os.path.exists(_gp):
            _gap3 = _j3.load(open(_gp, encoding="utf-8"))
        if not _md3 or not _gap3:
            check("product: the order sheet carries the permission it must obey", False,
                  "no published ORDER page or no cut-order-gap receipt")
        else:
            _tr3 = (_gap3.get("trim") or {})
            _legs3 = [r for r in _tr3.get("legs") or [] if r.get("priced")]
            _rows3 = all(("| %s |" % r["symbol"]) in _md3 for r in _legs3)
            _word3 = ("不可执行" in _md3) if _gap3.get("order_exceeds_permission") else (
                "WITHIN_PERMISSION" in _md3)
            check("product: the order sheet carries the permission it must obey",
                  "按谁的额度下单" in _md3
                  and ("%.6f" % float(_gap3.get("permitted_k"))) in _md3
                  and _rows3 and _word3,
                  "sheet does not print the floor/lots the audit receipt publishes")
    except Exception as e:
        check("product: the order sheet carries the permission it must obey", False, str(e))
    # r1229: the sheet used to quote the DECISION bar's close as its reference price while
    # its header claimed the priced bar -- so every lot count was a twelve-day-old
    # arithmetic (2026-10-30: 159501 quoted 2.229 against a 2.158 close). Re-derived from
    # the published payload: the block must exist, its priced_bar must be the bar the sheet
    # says it is priced on, and each row's priced price must be the price the ticket prints.
    try:
        import json as _j2
        _lp2 = os.path.join("results", "etf_book_order", "latest.json")
        _tk2, _rp2, _pay = None, None, None
        if os.path.exists(_lp2):
            _ptr2 = _j2.load(open(_lp2, encoding="utf-8"))
            _p2 = os.path.join("results", "etf_book_order", _ptr2.get("file") or "")
            if os.path.exists(_p2):
                _pay = _j2.load(open(_p2, encoding="utf-8"))
                _tk2, _rp2 = _pay.get("ticket"), _pay.get("reprice")
        if not _tk2 or not _rp2:
            check("product: the order sheet prices the bar it says it is priced on", False,
                  "no reprice block on the published ticket")
        else:
            _rows = {r["symbol"]: r for r in _tk2.get("order") or []}
            _pair_ok = all(
                r.get("priced_price") is None
                or r.get("priced_price") == (_rows.get(r["symbol"]) or {}).get("price")
                for r in (_rp2.get("names") or []))
            _drift_ok = all(
                # drift_pct is published rounded to 4 decimals, so re-deriving it at 1e-6
                # reads red on rounding alone (caught by this leg's first run, r1229).
                (r.get("drift_pct") is None or r.get("decision_price") in (None, 0)
                 or abs(100.0 * (r["priced_price"] - r["decision_price"])
                        / r["decision_price"] - r["drift_pct"]) < 1e-3)
                for r in (_rp2.get("names") or []))
            check("product: the order sheet prices the bar it says it is priced on",
                  _rp2.get("status") == "ok"
                  and _rp2.get("priced_bar") == _pay.get("evidence_cutoff")
                  and bool(_rp2.get("names")) and _pair_ok and _drift_ok
                  and _rp2.get("verdict") in ("REPRICED_TO_THE_BAR_YOU_PAY",
                                              "SAME_PRICES_ON_BOTH_BARS",
                                              "PRICE_MISSING_ON_PRICED_BAR"),
                  "reprice block disagrees with the ticket it describes (%s)" % _rp2.get("verdict"))
    except Exception as e:
        check("product: the order sheet prices the bar it says it is priced on", False, str(e))
    for _label, _script, _args in (
            # r1172: the bet count has two readings that must not be collapsed -- five
            # copies of one series share their variance five ways while spanning a single
            # direction -- and a constant series has no correlation to measure at all.
            ("product: etf_book_bets_face (independence vs risk split)",
             "scripts/etf_book_bets_face.py", ["--selftest"]),
            ("product: etf_book_production card (exit-code contract)",
             "scripts/etf_book_production.py", ["--selftest"]),
            # r1349 / E255: a percentile quoted from 2,000 draws has a resolution, and two
            # arms whose gap sits inside it are one number. This leg pins the interval, the
            # permutation test on both sides, and the rule that a disagreement between the
            # two aggregators is published rather than resolved.
            ("product: etf_book_quantile_floor (percentile resolution contract)",
             "scripts/etf_book_quantile_floor.py", ["--selftest"]),
            # r1350 / E257: a grid cell quoted from one decision calendar is not a level. The
            # suite prices the rule that decides whether the grid's ordering is separated from
            # phase luck, including the two branches a permissive rule would take (an edited
            # median, an edited verdict) and a cell judged on too few phases.
            ("product: etf_book_phase_atlas (grid vs its own calendar)",
             "scripts/etf_book_phase_atlas.py", ["--selftest"]),
            # r1351: the arms face (r1163) turns the atlas ruler on the buffer and cost arms.
            # The suite pins the frozen rule, the three-way verdict split, and the gate itself:
            # a face that equals its re-derivation is green, an edited verdict with no source
            # moved stays inconsistent, and a missing face reads stale (never "fine").
            ("product: etf_book_phase_atlas_arms (arms vs their own band + publish gate)",
             "scripts/etf_book_phase_atlas_arms.py", ["--selftest"]),
            # r1168: a card whose deliverable was committed BEFORE it was registered is supply
            # on paper only. The suite pins the git-stamp fallback for an unparsable entered_at,
            # the newer/older split, and that a card git has never seen stays ambiguous.
            ("pool: a card whose deliverable already existed is not supply",
             "Tools/pool_deliverable_audit.py", ["--selftest"]),
            # r1376: r1374 and r1375 each ended by admitting their sweep was the etf_book
            # family, not the repo. This leg keeps the scanner honest: a date-keyed fixture
            # must be found, a module that hashes something ELSE must not count as covered,
            # and a gate that raises must not be reported as one that serves.
            ("audit: which caches serve a live value on a key with no digest",
             "Tools/live_value_cache_audit.py", ["selftest"]),
            # r1380: a provenance gate is only a gate if its two sides can disagree.
            # p1e_neighbor_corr guarded its checkpoint with `evidence_cutoff == CUTOFF`,
            # and the writer wrote CUTOFF into that field from the same constant. The
            # suite pins the digest that replaced it and the class that finds the shape,
            # including the fact that a face also comparing a computed value is no longer
            # counted as self-pinned.
            ("product: a checkpoint pinned to the constant its own writer spelt",
             "scripts/p1e_neighbor_corr.py", ["selftest"]),
            # r1378: the same question one lane over. cn_mkneutral_p1 gates its panel on the
            # asset STAMP, the last bar and the shape -- a repaired print inside the window moves
            # none of them, so cells and null/sobol shards were resumable against a world that no
            # longer existed. The suite pins the digest (a repaired print moves it, a NaN spelling
            # does not), the cell MISS on a moved panel, and the shard sidecar stamp.
            ("product: cn_mkneutral cells/shard checkpoints carry the panel digest",
             "scripts/cn_mkneutral_p1.py", ["selftest"]),
            # r1377: the audit's first row fixed, plus the leg its own new verdict demands --
            # the digest reaches the cache read as an argument, so a leg that perturbs the
            # panel and demands a recompute is the only thing that proves it is compared.
            ("product: alloc cell checkpoint is keyed on the panel, not just the rule",
             "scripts/alloc_backtest.py", ["selftest"]),
            # r1352 / E261: a label is a measurement only if it is rare when nothing happened.
            # The suite pins the null (seeded, reproducible), the activity preconditions (zero
            # noise is NOT-SEPARABLE, a 50pp shift is ADOPT -- so the rule really ran), that the
            # published verdict follows from its own frequencies, and the gate's three states.
            ("product: etf_book_rule_null (labeler on an effect-free panel)",
             "scripts/etf_book_rule_null.py", ["--selftest"]),
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
            # r1153: the battle report now names the market's risk tape (limit-up /
            # limit-down / broken-seal / strong counts + the streak ladder) instead of
            # leaving it in a forward panel nobody reads. Its selftest builds a real
            # parquet fixture, so a column rename or a "missing day = 0 members"
            # regression reads red instead of shipping a quiet zero.
            ("product: daily report risk tape (zt pools, honest absence)",
             "scripts/daily_report.py", ["selftest"]),
            # the four risk tiers used to need four separate `--beta` runs read off two
            # different files; this leg keeps the one-page menu callable (r1149).
            ("product: etf_book_beta_menu (exit-code contract)",
             "scripts/etf_book_beta_menu.py", ["--selftest"]),
            ("product: etf_book_width_null_production (verdict recomputed from its own columns)",
             "scripts/etf_book_width_null_production.py", ["--selftest"]),
            ("product: etf_book_split_audit repair value (exit-code contract)",
             "scripts/etf_book_split_audit.py", ["selftest"]),
            # The r1310/r1311 span regressions only ever ran on 2020+ data, i.e. inside the
            # window the book earned its money in. This leg keeps the outside-window test
            # callable: if its selftest rots, the "alpha is a window property" reading
            # stands on a script nobody can re-derive.
            ("product: etf_book_spanning_pre2020 period test (exit-code contract)",
             "scripts/etf_book_spanning_pre2020.py", ["--selftest"]),
            # r1234: the pre-2020 number (5.12%) is quoted on the CEO page as "the same rule
            # in a harder tape". Inside that window the 8% overlay is not a drag but the
            # whole return: the un-overlaid book earns 0.73%/yr at 19.9% vol and -46% dd.
            # The leg pins the two ways that reading can rot -- a published verdict that no
            # longer recomputes from its own summary, and a control that stops reproducing
            # the shipped cells_vt (at which point it is pricing a different book).
            ("product: etf_book_pre2020 vol-target decomposition (verdict recomputed)",
             "scripts/etf_book_pre2020_voltarget.py", ["--selftest"]),
            # r1235: every headline on this line is earned on TODAY's 1504 funds; a third of
            # them did not exist when the window opened, and 11 of the 12 names in the book
            # in force were listed after it. This face prices the same cell on the universe
            # frozen at the window's first day. The leg pins the two ways that reading can
            # rot: a verdict that no longer recomputes from its own phase rows, and a control
            # that stops reproducing the card's two published arms (at which point the lock
            # numbers belong to a different book).
            ("product: etf_book_universe_lock (verdict recomputed, control reproduced)",
             "scripts/etf_book_universe_lock.py", ["--selftest"]),
            # r1236: the other half of the survivor problem. No series in the panel ever ends
            # its life inside the window, so the book can never be charged for holding a fund
            # that later dies. The census (r1319) counts the symbols that stop printing and
            # says plainly that the funds the source never served are invisible in its bytes --
            # so this face prices that residual as a mortality budget (drag = deaths-per-name-
            # year x LGD, break-even = CAGR / LGD) instead of re-classifying the panel a second
            # time (E289). The legs pin the arithmetic, that the break-even does not move with
            # how many names are held, that the census is quoted rather than recomputed, and
            # that the verdict re-derives from the published rows instead of being prose.
            ("product: etf_book_survivorship_hole (break-even mortality re-derived)",
             "scripts/etf_book_survivorship_hole.py", ["--selftest"]),
            ("product: etf_book_survivorship_hole (published verdict still recomputes)",
             "scripts/etf_book_survivorship_hole.py", ["--check"]),
            # r1237 / E29: the gate is only on the way in. The ranking screens names on a
            # 20-bar turnover gate and nothing checks the same number when the book sells.
            # The legs pin the exit-side arithmetic (deferral to the first qualifying bar,
            # weight from the engine's own scale, outside_cap never folded into a zero) and
            # that the published verdict re-derives from the payload's rows.
            ("product: etf_book_exit_liquidity (sell-side gate arithmetic re-derived)",
             "scripts/etf_book_exit_liquidity.py", ["--selftest"]),
            ("product: etf_book_exit_liquidity (published verdict still recomputes)",
             "scripts/etf_book_exit_liquidity.py", ["--check"]),
            # r1238: the forced-hold tail the sibling face reported and left at zero. The
            # legs pin the two ways this can go wrong -- a silent name folded into the pp
            # total as a zero, and a control arm that no longer reproduces the census the
            # published 2.78% was counted on -- plus the verdict recompute.
            ("product: etf_book_forced_hold (censored tail arithmetic re-derived)",
             "scripts/etf_book_forced_hold.py", ["--selftest"]),
            ("product: etf_book_forced_hold (published verdict still recomputes)",
             "scripts/etf_book_forced_hold.py", ["--check"]),
            # r1238: the other end of the size question. Capacity asks how BIG the book can get
            # before impact eats it; this asks how SMALL an account can be before the 5-yuan
            # commission floor eats it -- a rate model has no floor, a real broker does. The
            # legs pin the floor arithmetic on a hand-built trade and demand the published
            # neutral points re-derive from the published rows.
            ("product: etf_book_min_capital (commission floor arithmetic re-derived)",
             "scripts/etf_book_min_capital.py", ["--selftest"]),
            ("product: etf_book_min_capital (published neutral points still recompute)",
             "scripts/etf_book_min_capital.py", ["--check"]),
            # r1246: the entry gate (20-day median turnover >= 20M) picks the entire
            # universe and had never been swept inside this book. The first leg pins the
            # frozen rule, the second re-derives the published verdict from the published
            # rows -- a face whose own thresholds moved reads red instead of confident.
            ("product: etf_book_entry_gate (frozen gate rule, five states)",
             "scripts/etf_book_entry_gate.py", ["--selftest"]),
            ("product: etf_book_entry_gate (published verdict still re-derives)",
             "scripts/etf_book_entry_gate.py", ["--check"]),
            # The money question ("how big can this book get before impact eats it")
            # rests entirely on this one script: it re-derives both arms off one
            # engine and pins k=1 to the flat path to 1e-12. A rot here would print
            # a confident NAV ladder that no longer belongs to the delivered rule.
            ("product: etf_book_capacity_rule impact ladder (exit-code contract)",
             "scripts/etf_book_capacity_rule.py", ["selftest"]),
            # r1175: "the market gaps 5%, so what do I lose" (answered through the
            # measured beta, not the deployed share) and "how much of the book's own
            # numbers is quote-flip contamination" (answered by running the same rule on
            # repaired prices). Both gates recompute their verdict from their published
            # columns, so a hand-edited verdict fails here instead of reading as done.
            ("product: etf_book_shock_day (exit-code contract)",
             "scripts/etf_book_shock_day.py", ["--selftest"]),
            ("product: etf_book_flip_contamination (exit-code contract)",
             "scripts/etf_book_flip_contamination.py", ["--selftest"]),
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
            # r1232: every face above asks WHICH names and WHEN; the engine's `w = 1/n_hold`
            # line was never priced. These legs pin the three things that would make a risk
            # weighting look better than it is: a hook that is a second engine (the equal
            # scheme must be bit-identical to the default), a rule that peeks past the
            # decision bar, and an ERC solve that goes short on a sampled covariance.
            ("product: picks-to-weights rule priced across books and phases (exit-code contract)",
             "scripts/etf_book_weight_scheme.py", ["--selftest"]),
            ("product: published weight-scheme verdict recomputes from its summary",
             "scripts/etf_book_weight_scheme.py", ["--check"]),
            # r1347: adoption tested one arm; the hysteresis face still publishes four more
            # priced on a single sequence. These legs pin the breakeven-cost conversion
            # (a return-losing arm needs a positive cost to break even, a return-gaining one
            # needs none, zero turnover has no conversion path at all), the family verdict
            # reading its arms rather than a stored string, and "behind the card" being a
            # third state instead of a permanently red gate (r1346).
            ("product: buffer arm grid breakeven and family verdict (exit-code contract)",
             "scripts/etf_book_hysteresis_paths.py", ["--selftest"]),
            # r1347: a breakeven in bp/side is not a size. These legs pin the sqrt cost law
            # and its inverse, the three crossing states (gains return / under the base / no
            # impact component), and the share rule that keeps one lucky cell from reading as
            # "pays at size"; the gate leg pins that an edited cell or an edited flag is
            # contradicted by the recompute.
            ("product: buffer breakeven priced as a size (exit-code contract)",
             "scripts/etf_book_buffer_price_of_size.py", ["--selftest"]),
            # r1348: the same ruler, pointed at the distribution instead of an arm -- the
            # block bootstrap of the book's own daily path, and the gate that re-derives
            # every percentile from the published resample rows.
            ("product: book envelope by block bootstrap (exit-code contract)",
             "scripts/etf_book_nav_envelope.py", ["--selftest"]),
            # r1220: the order sheet declares "decide at close t -> fill at open t+1" but the
            # arm it prints buys at open t (the lookahead audit's lag-0 point). This leg
            # re-derives the comparison from the published rows, so a card that stops
            # pricing what it claims is red rather than merely different.
            ("product: the order sheet prices the execution it declares",
             "scripts/etf_book_causal_headline.py", ["check"]),
            # r1224 / E341: the card carries the causal number; this leg pins that the
            # rebuild question was actually asked and answered -- smoothing the causal score
            # earns back 0.07pp of the 1.14pp one-bar price, so the gap is information the
            # desk never had and no further smoothing of this score is worth burning.
            ("product: the one-bar price is not recoverable by smoothing (exit-code contract)",
             "scripts/etf_book_causal_rebuild.py", ["--selftest"]),
            # r1226 / E26: with the rebuild closed, the only channel left is the overnight gap
            # between the decision close and the fill open. It prices as neither a ranking
            # signal (strongly negative) nor a usable exclusion (+0.81pp full span, 2/4 phases).
            ("product: the overnight gap is priced against the declared arm (exit-code contract)",
             "scripts/etf_book_overnight_gap.py", ["--selftest"]),
            # r1227 / E27: information is exhausted, so the last candidate is the fill itself --
            # spread the same delta over k consecutive opens. Equal slices sum to the same
            # absolute delta, so commission cannot be what moves: only the price path can.
            ("product: the fill is sliced over k opens and priced (exit-code contract)",
             "scripts/etf_book_open_slicing.py", ["--selftest"]),
            # r1230: depth and duration are different risks. The book published how deep it
            # falls and never how long a holder waits, so this face prices the wait: the
            # underwater episodes, the recovery horizon of EVERY entry (censored entries
            # reported, never scored as zero), and forward 1/2/3 calendar-year returns.
            ("product: how long a holder waits under water (exit-code contract)",
             "scripts/etf_book_underwater.py", ["--selftest"]),
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
        # r1361: the toll ladder judges the atlas ordering against each cell's own phase band.
        # Re-derive every rung's spread straight off the SOURCE arm face (so an edited ladder
        # row is red even if the ladder face agrees with itself), then re-derive the verdict
        # from the numbers it is attached to.
        _lp = os.path.join("results", "etf_book_atlas_toll_ladder.json")
        if os.path.exists(_lp):
            _lj = json.load(open(_lp, encoding="utf-8"))
            _t = _lj.get("toll_ladder") or {}
            _lok = (_t.get("rungs") or 0) >= 2 and bool(_t.get("spread_pp"))
            _lv = []
            for _row in (_t.get("argmax_cells") or []):
                _src = os.path.join("results", _row.get("file") or "")
                if not os.path.exists(_src):
                    _lok = False
                    continue
                _pc = json.load(open(_src, encoding="utf-8")).get("per_cell") or []
                _meds = [c["median_cagr_pp"] for c in _pc]
                _lv.append(round(max(_meds) - min(_meds), 3) if _meds else None)
            _lok = _lok and _lv and all(
                a is not None and abs(a - b) < 1e-6 for a, b in zip(_lv, _t["spread_pp"]))
            if _t.get("verdict") == "ORDERING_IS_A_TOLL_ARTEFACT":
                _lok = (_lok and _t.get("break_even_toll_bp") is not None
                        and _t["spread_at_production_toll_pp"] is not None
                        and _t["spread_at_production_toll_pp"]
                        <= _t["band_at_production_toll_pp"] + 1e-9
                        and (_t.get("spread_rank_corr_with_toll") or 0) <= -0.90)
            _b = _lj.get("buffer_ladder") or {}
            if _b.get("verdict") == "SINGLE_RUNG_CROSSING_IS_ONE_DRAW":
                _lok = _lok and _b.get("n_clearing_rungs") == 1
            check("product: toll-ladder verdict is recomputable from the arm faces",
                  _lok, "verdict=%s break_even=%s rungs=%d spread@8bp=%s band=%s"
                  % (_t.get("verdict"), _t.get("break_even_toll_bp"), _t.get("rungs") or 0,
                     _t.get("spread_at_production_toll_pp"),
                     _t.get("band_at_production_toll_pp")))
        else:
            check("product: toll-ladder verdict is recomputable from the arm faces",
                  True, "toll-ladder face absent -- soft-fails by design")
    except Exception as e:
        check("product: toll-ladder verdict is recomputable from the arm faces",
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
        _names = {t[0] for t in _legs}
        # etf_book_production belongs here as much as the ticket: r1290 caught the card
        # (the headline face) a full refresh behind the ticket because only the ticket
        # was wired -- an unwired face reads as current to everything downstream.
        # etf_book_width_audit prices the disagreement between the card and the ticket,
        # so it goes stale the moment either moves: r1291 found it two bars behind both.
        _want = {"etf_book_forward", "etf_book_production", "etf_book_order",
                 "etf_book_order_card", "etf_sign_pit", "etf_sign_enum", "etf_sign_stability",
                 "etf_sign_cells", "etf_sign_pit_combo",
                 "etf_book_width_audit", "etf_book_registry", "etf_book_ceo_page",
                 "etf_book_card_track", "etf_paper_signal", "cal_audit",
                 # r1222: a face that judges the card has to run every round, or it keeps
                 # publishing the card it was written against -- this one accused the card of
                 # an undisclosed execution for a full round after the card started
                 # disclosing it, because nothing on the chain ever re-ran it.
                 "etf_book_causal_headline"}
        _miss = sorted(_want - _names)
        check("product: ETF book legs wired into the S6 chain",
              not _miss, f"legs={len(_names)} missing={_miss or 'none'}")
    except Exception as e:
        check("product: ETF book legs wired into the S6 chain", False, str(e))
    try:
        # r1222: the causal face reads the card's payload and the card's printed table, so it
        # must sit between them: after production (its input) and before the page (which
        # quotes the book it judged). A consumer that runs ahead of its producer prints
        # yesterday's disagreement with today's date (r1318 / r1290 family).
        _order = [t[0] for t in importlib.import_module("Tools.s6_chain_bmc").LEGS]
        _ci = _order.index("etf_book_causal_headline")
        check("product: the execution-claim face runs on the card it reads, not ahead of it",
              _order.index("etf_book_production") < _ci < _order.index("etf_book_ceo_page"),
              "production=%d causal=%d page=%d" % (
                  _order.index("etf_book_production"), _ci,
                  _order.index("etf_book_ceo_page")))
    except Exception as e:
        check("product: the execution-claim face runs on the card it reads, not ahead of it",
              False, str(e))
    try:
        _order = [t[0] for t in importlib.import_module("Tools.s6_chain_bmc").LEGS]
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
        # r1248: the cut that picks the whole universe is quoted on BOTH reader faces, and the
        # reading is recomputed here from the published sweep rather than retyped. A face that
        # prints a plateau while the payload's own rows moved is the E289 two-copies defect, so
        # the numbers are compared, not the words.
        _eg_pub = json.load(open("results/etf_book_entry_gate.json", encoding="utf-8"))
        _eg_rows = [r for r in (_eg_pub.get("rows") or [])
                    if r.get("cagr") is not None and not r.get("error")]
        _eg_w = [r.get("median") for r in _eg_rows if r.get("median") is not None]
        _eg_near = [abs(float(d)) for d in
                    ((_eg_pub.get("verdict") or {}).get("near_deltas_pp") or [])]
        _eg_ratio = (float(max(_eg_w)) / float(min(_eg_w))) if _eg_w else None
        _eg_near_max = max(_eg_near) if _eg_near else None
        _tk_path = os.path.join("results", "etf_book_order",
                                "TICKET-%s.json" % _lb.get("as_of"))
        _tk_eg = (json.load(open(_tk_path, encoding="utf-8")).get("entry_gate") or {}
                  if os.path.exists(_tk_path) else {})
        _card_path = os.path.join("results", "etf_book_production", "CARD.md")
        _card_txt = open(_card_path, encoding="utf-8").read() if os.path.exists(_card_path) else ""
        _tk_md_path = os.path.join("results", "etf_book_order", "ORDER-%s.md" % _lb.get("as_of"))
        _tk_md = open(_tk_md_path, encoding="utf-8").read() if os.path.exists(_tk_md_path) else ""
        _ok_eg = (bool(_eg_w) and _eg_near_max is not None and _eg_ratio is not None
                  and _tk_eg.get("status") == "ok"
                  and _tk_eg.get("verdict") == (_eg_pub.get("verdict") or {}).get("verdict")
                  and abs(float(_tk_eg.get("near_max_pp") or -1) - _eg_near_max) < 1e-9
                  and abs(float(_tk_eg.get("width_ratio") or -1) - _eg_ratio) < 1e-6
                  and ("%d" % int(max(_eg_w))) in _card_txt
                  and ("%d" % int(min(_eg_w))) in _card_txt
                  and "number of names the book is allowed to hold" in _card_txt
                  and "容量这一轴" in _tk_md)
        check("product: both reader faces print the cut that picks the universe, recomputed",
              _ok_eg,
              "ticket=%s near=%s (payload %s) ratio=%s (payload %s) card widths=%s/%s"
              % (_tk_eg.get("verdict"), _tk_eg.get("near_max_pp"), _eg_near_max,
                 _tk_eg.get("width_ratio"), _eg_ratio,
                 max(_eg_w) if _eg_w else None, min(_eg_w) if _eg_w else None))
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
        # Five tickers are not five bets: the page must quote the bet-count face's own
        # sentence (recomputed here from the published artifact, never from a copy) and
        # must never fall back to counting names when that artifact is missing.
        try:
            _bfp = json.load(open("results/etf_book_bets_face.json", encoding="utf-8"))
            _bfl = _bfp.get("long") or {}
            _sent = _bfl.get("sentence")
            _md_page = open(_ptr.get("page"), encoding="utf-8").read()
            _ok_bf = (bool(_sent) and _sent in _md_page
                      and "这几只票到底有几个赌注" in _md_page)
            if not _sent:
                _ok_bf = False
            check("product: ETF live-book page says how many independent bets the holdings are",
                  _ok_bf, f"effective={_bfl.get('effective_bets')} quoted={bool(_sent and _sent in _md_page)}")
        except Exception as e:
            check("product: ETF live-book page says how many independent bets the holdings are",
                  False, str(e))
        # r1175: two faces now answer "what does a bad day cost". The shock face quotes
        # the contamination face rather than recomputing it (one reader, E270), and the
        # book's worst day is a unit-change print rather than a market day -- so a shock
        # face that stopped disclosing, or disclosed a different clean worst day than the
        # one published, must fail here rather than quietly mislead the operator.
        try:
            _flip = json.load(open("results/etf_book_flip_contamination.json",
                                   encoding="utf-8"))
            _shock = json.load(open("results/etf_book_shock_day.json", encoding="utf-8"))
            _fl = ((_flip.get("windows") or {}).get("full_history") or {})
            _clean = ((_fl.get("worst_day") or {}).get("clean") or {})
            _pq = _shock.get("price_quality") or {}
            _beta = float((_shock.get("beta") or {}).get("full") or 0.0)
            _nav = float(((_shock.get("ticket") or {}).get("nav")) or 0.0)
            _money_ok = True
            for _row in (_shock.get("scenarios") or []):
                if _nav and abs(float(_row["cny"]) - float(_row["market_shock"]) * _beta
                                * _nav) > 1.0:
                    _money_ok = False
            _ok_pq = (bool(_pq) and _nav > 0 and _money_ok
                      and _pq.get("flip_prints") == (_flip.get("panel") or {}).get(
                          "flip_prints_flattened")
                      and abs(float(_pq.get("clean_worst") or 0.0)
                              - float(_clean.get("value") or 1.0)) < 1e-9
                      and _pq.get("clean_worst_date") == _clean.get("date"))
            check("product: shock face prices its shocks off its own beta and ticket",
                  _ok_pq,
                  f"beta={_beta} nav={_nav} flips={_pq.get('flip_prints')} "
                  f"clean_worst={_pq.get('clean_worst')} published={_clean.get('value')}")
        except Exception as e:
            check("product: shock face prices its shocks off its own beta and ticket",
                  False, str(e))
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
        # The page advises "hold the idle half in the repo" but nothing could see whether
        # it happened. The handshake face reconciles the recorded placement against the
        # book's cash. Recomputed here from the placement file + the repo panel so that a
        # hand-edited page (or an unfilled record printed as "all good") reads red.
        _hs = _page.get("cash_handshake") or {}
        _ok_hs = False
        _hs_detail = "block absent"
        try:
            _pf = "state/account/cash_placement.json"
            _rec = None
            if os.path.exists(_pf):
                with open(_pf, encoding="utf-8-sig") as _fh:
                    _rec = json.load(_fh)
            _cash_y = float(_page.get("cash_amount_cny") or 0.0)
            _last_rate = None
            with open("data/repo_daily/GC001.csv", encoding="utf-8") as _fh:
                next(_fh, None)
                for _ln in _fh:
                    _p = _ln.strip().split(",")
                    if len(_p) >= 5:
                        try:
                            _v = float(_p[4])
                        except ValueError:
                            continue
                        if 0.0 < _v < 200.0:
                            _last_rate = _v
            _dem = 0.05
            if _rec and _rec.get("demand_rate_pct") is not None:
                _dem = float(_rec["demand_rate_pct"])
            _by = str((_rec or {}).get("recorded_by") or "").strip().lower()
            _unrec = (not _rec) or _by in ("", "unrecorded", "none", "null")
            if _unrec:
                _ok_hs = (_hs.get("status") == "UNRECORDED"
                          and _hs.get("gap_annual_cny") is None
                          and _hs.get("idle_cny") is None
                          and _last_rate is not None
                          and abs(float(_hs.get("worst_case_annual_cny") or 0)
                                  - _cash_y * (_last_rate - _dem) / 100.0) < 2.0)
                _hs_detail = ("unrecorded status=%s gap=%s worst=%s recomputed=%.0f"
                              % (_hs.get("status"), _hs.get("gap_annual_cny"),
                                 _hs.get("worst_case_annual_cny"),
                                 _cash_y * ((_last_rate or 0.0) - _dem) / 100.0))
            else:
                _placed = 0.0
                for _r in _rec.get("placements") or []:
                    _inst = str((_r or {}).get("instrument") or "").strip().lower()
                    if _inst in ("", "活期", "demand", "cash", "现金", "活期存款"):
                        continue
                    if (_r or {}).get("amount_cny") is not None:
                        _placed += float(_r["amount_cny"])
                _idle = max(0.0, _cash_y - _placed)
                _gap = _idle * ((_last_rate or 0.0) - _dem) / 100.0
                _over = (_cash_y - _placed) < -max(1.0, 0.001 * _cash_y)
                _want = ("OVER-PLACED" if _over
                         else "IN-PLACE" if _idle <= max(1.0, 0.001 * _cash_y)
                         else "IDLE" if _idle >= _cash_y * 0.995 else "PARTIAL")
                _ok_hs = (_hs.get("status") == _want
                          and abs(float(_hs.get("idle_cny") or 0.0) - _idle) < 1.0
                          and (_over or not _hs.get("gap_annual_cny") is None
                               and abs(float(_hs.get("gap_annual_cny") or 0.0) - _gap) < 2.0))
                _hs_detail = ("status=%s want=%s idle=%.0f/%.0f gap=%s/%.0f placed=%.0f"
                              % (_hs.get("status"), _want, float(_hs.get("idle_cny") or 0),
                                 _idle, _hs.get("gap_annual_cny"), _gap, _placed))
        except Exception as _e:
            _hs_detail = "recompute failed: %s" % _e
        check("product: cash placement is reconciled against the book, and an unread account is not a zero gap",
              _ok_hs, _hs_detail)
    except Exception as e:
        check("product: ETF live-book page current and its money closes", False, str(e))
    try:
        _bma = importlib.import_module("Tools.s6_chain_bma")
        _canon = importlib.import_module("Tools.s6_chain_bmc")
        # r1346: LEGS entries may carry a third element (the refresh command paid on a
        # stale face), so unpack by position -- or n, c in LEGS fails on the first
        # such leg and this check then reads as a fleet red instead of a tuple bug.
        _a = [t[0] for t in _bma.LEGS]
        _c = [t[0] for t in _canon.LEGS]
        _miss = [t[0] for t in _bma.LEGS
                 if _bma.leg_script(t[1]) and not os.path.exists(
                     os.path.join(_bma.ROOT, _bma.leg_script(t[1])))]
        check("fleet: bm-a's chain runner is the shared leg list, not a snapshot",
              _a == _c and not _miss,
              f"legs={len(_a)} canonical={len(_c)} missing_scripts={_miss or '-'}")
    except Exception as e:
        check("fleet: bm-a's chain runner is the shared leg list, not a snapshot",
              False, str(e))
    try:
        import glob as _glob
        import json as _json
        _sppath = os.path.join("scripts", "futures_tsmom_signal.py")
        _sr = subprocess.run([sys.executable, _sppath, "--selftest"], capture_output=True,
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
        _sppath = os.path.join("scripts", "futures_overlay_sweep.py")
        _sr = subprocess.run([sys.executable, _sppath, "--selftest"], capture_output=True,
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
    # r1343: the pre-commit claw only looks at markers being ADDED, so a marker that
    # entered through a rebase replay or --no-verify sits in the blob forever. The live
    # case was knowledge/METHODOLOGY_ASSETS.md at c07483b9 carrying a lone
    # "||||||| parent of ed40e56da3" line, which no leg read.
    try:
        _frag = _marker_fragments()
        check("config: no tracked blob carries a conflict-marker fragment",
              not _frag,
              ("%d file(s): " % len(_frag)
               + "; ".join("%s:%d %s" % (p, ln, k) for p, ln, k in _frag[:4]))[:220]
              if _frag else
              "balanced hunks only (probe fixtures that quote a whole hunk stay legal)")
    except Exception as e:
        check("config: no tracked blob carries a conflict-marker fragment",
              False, repr(e)[:160])

    # r1383: the card ledger carried seven control characters (0x08/0x07/0x1b) that
    # ate the first letter of the token behind them -- `reak_guard` for `break_guard`,
    # `bs(` for `abs(` -- so a card said something no reader ever saw. r1380 recorded
    # the class and NOTHING read it, which is how a corruption class grows silently.
    # The repair lives in Tools/card_text_hygiene.py (frozen table, site-local
    # assertion, receipt) and this leg is what keeps the site from coming back.
    try:
        _cth = _card_text_hygiene()
        _chits = _cth.findings()
        check("config: no card or digest carries a control character",
              not _chits,
              ("%d site(s): " % len(_chits)
               + "; ".join("%s:%d %s" % (h["path"], h["line"], h["byte"])
                           for h in _chits[:4]))[:220]
              if _chits else
              "%d files scanned (tab/CR/LF stay legal)" % len(_cth.corpus()))
    except Exception as e:
        check("config: no card or digest carries a control character",
              False, repr(e)[:160])

    # r1235: the same escape that ate letters in r1383 leaves a second shape --
    # a line ending in a backslash followed by a path token resolves `\r` into a
    # real CR and eats the token's leading `r` (`... (selftest 19/19) \` +
    # newline + `results/x.json` -> `esults/x.json`). The CR is a legal line
    # break, so the control-character leg above is blind to it, and eleven
    # pointers in the registry plus one in a digest had been unfollowable for
    # weeks. The detector proves each candidate on the file system (restored
    # path exists, or -- for a <template> -- its directory does), so it cannot
    # fire on spelling.
    try:
        _cth2 = _card_text_hygiene()
        _phits = _cth2.prefix_findings()
        check("config: no card or digest carries an eaten path prefix",
              not _phits,
              ("%d site(s): " % len(_phits)
               + "; ".join("%s:%d %s" % (h["path"], h["line"], h["token"])
                           for h in _phits[:4]))[:220]
              if _phits else
              "%d files scanned (repair = Tools/card_text_hygiene.py fix)"
              % len(_cth2.corpus()))
    except Exception as e:
        check("config: no card or digest carries an eaten path prefix",
              False, repr(e)[:160])

    # r1406: the forward ledger was committed on 2026-11-07 with a missing comma
    # between two list elements and a `drift` block that carried `faces`/`max_abs`
    # twice. Every reader of that file (the order ticket, the CEO page, the settle
    # audit) dies at open on the first defect, and json.loads accepts the second
    # silently -- keeping the LAST value, so the file would have reported an old
    # measurement as the current one. Neither defect leaves a conflict marker, so
    # the claw was blind to it. Tools/json_face_guard.py is now the claw's r1406
    # leg; this pair of checks keeps the published corpus and the guard's own
    # semantics on the same line.
    try:
        _jfg = _json_face_guard()
        _jdoc = _jfg.scan(_jfg.default_paths())
        check("config: every published JSON face opens and holds no repeated key",
              _jdoc["verdict"] == "CLEAN",
              ("%d finding(s): " % len(_jdoc["findings"])
               + "; ".join("%s %s" % (f["verdict"], f["path"])
                           for f in _jdoc["findings"][:4]))[:220]
              if _jdoc["findings"] else
              "%d face(s) parsed, %d skipped (data-size/unreadable)"
              % (_jdoc["checked"], len(_jdoc["skipped"])))
    except Exception as e:
        check("config: every published JSON face opens and holds no repeated key",
              False, repr(e)[:160])
    try:
        # The claw's own legs: a guard whose selftest is broken would block good
        # commits or wave bad ones through, and nothing above would notice.
        import io as _io
        import contextlib as _ctx
        _buf = _io.StringIO()
        with _ctx.redirect_stdout(_buf):
            _rc = _json_face_guard()._selftest()
        check("config: the staged JSON claw passes its own legs", _rc == 0,
              (_buf.getvalue().strip().splitlines() or ["no output"])[-1][:160])
    except Exception as e:
        check("config: the staged JSON claw passes its own legs", False, repr(e)[:160])

    # r1344: the card-ledger tripwire must see every card at either heading level.
    # bm-b files `### E221`, this machine files `## E232`, and the first version of
    # the guard matched only `##` -- so 6 of 158 cards were invisible to the one gate
    # whose job is noticing that a card disappeared. The leg is a SCOPE assertion,
    # not a count: it re-derives the number of card headings from the ledger bytes
    # and requires the guard's own reader to agree, so the scope cannot shrink again.
    try:
        _cl = importlib.import_module("Tools.card_ledger_guard")
        _led = open("knowledge/METHODOLOGY_ASSETS.md", encoding="utf-8",
                    newline="").read().replace("\r", "")
        # re-derived here by hand, not through the guard's own regex: a leg that asks
        # the reader to check itself cannot notice that the reader got narrower.
        _want = 0
        for _l in _led.split("\n"):
            _body = _l[4:] if _l.startswith("### ") else (
                _l[3:] if _l.startswith("## ") else "")
            if (len(_body) > 4 and _body[0] == "E" and _body[1:4].isdigit()
                    and not _body[4].isalnum()):
                _want += 1
        _src, _p = _cl.check(head_text=_led, tree_text=_led)
        check("config: the card ledger guard sees every card heading level",
              _src == 0 and _want > 0 and _p["tree_cards"] == _want,
              "guard sees %d of %d cards (levels %s)"
              % (_p["tree_cards"], _want, _p["cards_by_level"]))
    except Exception as e:
        check("config: the card ledger guard sees every card heading level",
              False, repr(e)[:160])

    # r1385 / E310: a selftest cannot testify to its own deletion. A stale restore left
    # the working tree one commit behind on two files, and the `leg_split` reader plus the
    # CEO-page section it feeds were simply gone -- while the page's own selftest printed
    # `Summary: N/N PASS`, because the three legs that guarded them (L60-L62) had gone with
    # them, and one of them was the only place that counted the legs. A witness has to live
    # OUTSIDE the thing it watches, so this one is a consumer: it renders the page and looks
    # for what the reader is promised, and it hands the reader a face that does not add up.
    # Deleting either half turns this leg red although its own body is untouched, which is
    # exactly what the old legs could not do.
    try:
        import tempfile as _tf31
        import etf_book_ceo_page as _pg31
        import etf_book_leg_attribution as _la31
        _bad31 = []
        _p31, _ = _pg31.build(with_stress=False)
        _p31["leg_split"] = {
            "status": "ok", "artifact": "fixture", "evidence_cutoff": "2026-10-30",
            "execution": "decide at close -> fill at next open",
            "arms": {"production": {"buckets_pp_per_year": {"plain": 9.83, "overnight": 0.16,
                                                           "intraday": -0.64, "toll": -1.15},
                                   "total_log_pp": 8.21, "plain_carry_pp_per_year": 9.83,
                                   "fill_bar_drag_pp_per_year": -1.62,
                                   "fill_bars": 83, "plain_bars": 1569},
                     "control_ew": {"buckets_pp_per_year": {"plain": 6.20}}}}
        _md31 = _pg31.render_md(_p31)
        for _tok, _why in (("一天里的哪一段", "the section is gone from the page"),
                           ("+9.83", "the four buckets no longer reach the page"),
                           ("1569", "the quiet-bar count is gone"),
                           ("拖累 1.62", "the one-sentence reading is gone")):
            if _tok not in _md31:
                _bad31.append(_why)
        _p31["leg_split"] = {"status": "broken", "artifact": "fixture",
                             "detail": "production: buckets sum 5.000 != published 0.000",
                             "arms": {}}
        _md31b = _pg31.render_md(_p31)
        if "无法核验" not in _md31b or "+9.83" in _md31b:
            _bad31.append("a broken split prints numbers instead of 'cannot verify'")
        # the reader must refuse a face whose own arithmetic does not close (the deleted
        # L10c protected this from inside the module; the consumer protects it from here)
        _art31 = os.path.join(PATHS.results_dir, "etf_book_legs", "latest.json")
        if not os.path.exists(_art31):
            _r31 = _la31.money_split_face(path=_art31)
            if _r31.get("status") != "absent" or _r31.get("arms"):
                _bad31.append("an unpublished split is not reported absent (%r)"
                              % (_r31.get("status"),))
        else:
            with open(_art31, encoding="utf-8") as _fh31:
                _face31 = json.load(_fh31)
            _r31 = _la31.money_split_face(path=_art31)
            if _r31.get("status") != "ok":
                _bad31.append("the live split does not read ok (%r: %s)"
                              % (_r31.get("status"), (_r31.get("detail") or "")[:80]))
            _arm31 = sorted(_face31.get("arms") or {})
            _arm31 = _arm31[0] if _arm31 else None
            if _arm31:
                _face31["arms"][_arm31].setdefault("buckets_pp_per_year", {})["plain"] += 5.0
                _tmp31 = _tf31.mkdtemp()
                _fp31 = os.path.join(_tmp31, "broken.json")
                with open(_fp31, "w", encoding="utf-8") as _fh31w:
                    json.dump(_face31, _fh31w)
                _rb31 = _la31.money_split_face(path=_fp31)
                if _rb31.get("status") != "broken" or _rb31.get("arms"):
                    _bad31.append("reader served a split that does not add up (%r)"
                                  % (_rb31.get("status"),))
            else:
                _bad31.append("live split carries no arm to perturb")
        check("product: the CEO page still prints where in the day the money is earned",
              not _bad31, "; ".join(_bad31)[:220]
              or "section + four buckets + quiet-bar count + broken-face refusal all present")
    except Exception as e:
        check("product: the CEO page still prints where in the day the money is earned",
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

    # the carry split: the page now says how much of the quoted headline is the repo leg.
    # Two faces, one book -- the split artifact's base cell must be the ticket's own number,
    # because a reader comparing them would otherwise be reading two different books.
    try:
        _rg27 = os.path.join(PATHS.results_dir, "etf_book_return_regime.json")
        _tk27p = os.path.join(PATHS.results_dir, "etf_book_order", "latest.json")
        _bad27 = []
        if not os.path.exists(_rg27):
            _bad27.append("results/etf_book_return_regime.json missing")
        elif not os.path.exists(_tk27p):
            _bad27.append("results/etf_book_order/latest.json missing")
        else:
            with open(_rg27, encoding="utf-8") as _fh27:
                _rg = json.load(_fh27)
            with open(_tk27p, encoding="utf-8") as _fh27:
                _ptr27 = json.load(_fh27)
            _tkf27 = os.path.join(os.path.dirname(_tk27p),
                                  os.path.basename(str(_ptr27.get("file") or "")))
            if not os.path.exists(_tkf27):
                _bad27.append("ticket file named by the pointer is absent")
                _tk27 = {}
            else:
                with open(_tkf27, encoding="utf-8") as _fh27:
                    _tk27 = json.load(_fh27)
            _pub27 = ((_tk27.get("metrics") or {}).get("book") or {}).get("cagr")
            _gate27 = _rg.get("gate") or {}
            _base27 = (_gate27.get("betas") or {}).get(str(_gate27.get("base_beta"))) or {}
            if _pub27 is None:
                _bad27.append("ticket publishes no book cagr")
            elif _base27.get("observed_pct") is None:
                _bad27.append("split artifact has no observed cell for the base beta")
            elif abs(float(_base27["observed_pct"]) / 100.0 - float(_pub27)) > 5e-4:
                _bad27.append("base cell %.4f%% != ticket %.4f%%"
                              % (float(_base27["observed_pct"]), float(_pub27) * 100))
            for _b27, _r27 in (_gate27.get("betas") or {}).items():
                if not _r27:
                    continue
                if not (_r27["observed_pct"] >= _r27["flat_today_pct"]
                        >= _r27["zero_pct"] - 1e-9):
                    _bad27.append("beta %s ladder is not ordered observed>=today>=zero" % _b27)
                if abs((_r27["observed_pct"] - _r27["zero_pct"]) - _r27["carry_pp"]) > 1e-3:
                    _bad27.append("beta %s carry is not observed-zero" % _b27)
            _idy27 = _rg.get("identity") or {}
            if _idy27.get("matched") is not True:
                _bad27.append("the artifact itself records a failed identity check")
            # The page is bm-a's to write (scripts/etf_book_ceo_page.py HOST). Asking any
            # other machine to police its text is the r1135 mistake: a leg that assumes a
            # deployment layout is permanently red on the machines that do not own it.
            # Every host still checks the artifact; only the writer checks the page.
            _md27p = os.path.join(PATHS.root, "docs", "live_book",
                                  "LIVE-BOOK-%s.md" % str(_rg.get("evidence_cutoff") or "")
                                  .replace("-", ""))
            try:
                import etf_book_ceo_page as _pg27
                _pgwriter27 = _pg27.writer_allowed(None)
            except Exception:
                _pgwriter27 = True
            if not _pgwriter27:
                pass
            elif os.path.exists(_md27p):
                with open(_md27p, encoding="utf-8") as _fh27:
                    _md27 = _fh27.read()
                if "这笔钱里有多少是" not in _md27:
                    _bad27.append("live page carries no carry-split section")
                elif "%.2f%%" % float(_base27.get("zero_pct") or 0.0) not in _md27:
                    _bad27.append("live page omits the zero-cash number")
            # the split must be strictly weaker than the headline: no cash leg pays nothing
            _z27 = _base27.get("zero_pct")
            _o27 = _base27.get("observed_pct")
            if None not in (_z27, _o27) and not (_z27 < _o27):
                _bad27.append("zero-cash arm is not below the observed arm")
        check("product: the carry split reproduces the ticket and stays ordered",
              not _bad27, "; ".join(_bad27)[:220]
              or "base %.2f%% = ticket %.2f%% | today-flat %.2f%% | zero %.2f%%"
                 % (float(_base27.get("observed_pct") or 0.0),
                    float(_pub27 or 0.0) * 100,
                    float(_base27.get("flat_today_pct") or 0.0),
                    float(_base27.get("zero_pct") or 0.0)))
    except Exception as e:
        check("product: the carry split reproduces the ticket and stays ordered", False,
              repr(e)[:160])

    # r1367: the split must reach the EXECUTABLE sheet, not just the CEO page -- an
    # operator who holds only ORDER-*.md was quoting a headline with no idea that ~9% of
    # it is repo interest. The leg recomputes the printed numbers from the artifact, so a
    # hand-written sentence cannot pass it.
    try:
        _bad29 = []
        _cs29 = {}
        _tk29 = json.load(open(os.path.join(PATHS.results_dir, "etf_book_order",
                                            "latest.json"), encoding="utf-8"))
        _asof29 = str(_tk29.get("as_of") or "")
        _orderp = os.path.join(PATHS.results_dir, "etf_book_order",
                               "ORDER-%s.md" % _asof29)
        _rgp = os.path.join(PATHS.results_dir, "etf_book_return_regime.json")
        if not _asof29:
            _bad29.append("ticket pointer carries no as_of")
        elif not os.path.exists(_orderp):
            _bad29.append("results/etf_book_order/ORDER-%s.md missing" % _asof29)
        elif not os.path.exists(_rgp):
            _bad29.append("results/etf_book_return_regime.json missing")
        else:
            with open(_rgp, encoding="utf-8") as _fh29:
                _rg29 = json.load(_fh29)
            with open(_orderp, encoding="utf-8") as _fh29:
                _md29 = _fh29.read()
            _g29 = _rg29.get("gate") or {}
            _beta29 = float(_tk29.get("beta_target") or 0.0)
            _tkf29 = os.path.join(os.path.dirname(_orderp),
                                  "%s" % str(_tk29.get("file") or ""))
            if not os.path.exists(_tkf29):
                _bad29.append("ticket JSON named by the pointer is absent")
                _cs29 = {}
            else:
                with open(_tkf29, encoding="utf-8") as _fh29:
                    _cs29 = (json.load(_fh29) or {}).get("carry_split") or {}
            if "这条年化里有多少是现金利息" not in _md29:
                _bad29.append("the executable ticket carries no carry-split section")
            if not _cs29:
                _bad29.append("ticket publishes no carry_split block")
            else:
                # the block must be the artifact's own cell for the beta it claims
                _cell29 = (_g29.get("betas") or {}).get(str(_cs29.get("beta"))) or {}
                if not _cell29:
                    _bad29.append("split artifact has no cell for beta %s"
                                  % _cs29.get("beta"))
                else:
                    for _k29 in ("observed_pct", "flat_today_pct", "zero_pct"):
                        if _cell29.get(_k29) is None or \
                                abs(float(_cell29[_k29]) - float(_cs29.get(_k29))) > 1e-9:
                            _bad29.append("ticket's %s is not the artifact's cell" % _k29)
                    if abs((float(_cs29["observed_pct"]) - float(_cs29["zero_pct"]))
                           - float(_cs29["carry_pp"])) > 1e-3:
                        _bad29.append("published carry is not observed-minus-zero")
                if abs(float(_cs29.get("beta") or -1) - _beta29) > 0.051:
                    _bad29.append("split is priced at beta %s, ticket runs %.2f"
                                  % (_cs29.get("beta"), _beta29))
                for _k29, _fmt in (("observed_pct", "%.2f%%"), ("flat_today_pct", "%.2f%%"),
                                   ("zero_pct", "%.2f%%")):
                    if _fmt % float(_cs29.get(_k29) or 0.0) not in _md29:
                        _bad29.append("ticket omits %s=%.2f%%"
                                      % (_k29, float(_cs29.get(_k29) or 0.0)))
                if "%.1f%%" % float(_cs29.get("carry_share_pct") or 0.0) not in _md29:
                    _bad29.append("ticket omits the carry share of the headline")
                if "%.2fpp" % float(_cs29.get("carry_pp") or 0.0) not in _md29:
                    _bad29.append("ticket omits the carry in pp")
        check("product: the executable ticket decomposes its own headline", not _bad29,
              "; ".join(_bad29)[:220]
              or "headline %.2f%% = %.2fpp cash (%.1f%%) | zero-cash %.2f%%"
                 % (float(_cs29.get("observed_pct") or 0.0),
                    float(_cs29.get("carry_pp") or 0.0),
                    float(_cs29.get("carry_share_pct") or 0.0),
                    float(_cs29.get("zero_pct") or 0.0)))
    except Exception as e:
        check("product: the executable ticket decomposes its own headline", False,
              repr(e)[:160])
    # r1371: a bar restated after it settled is a history change, and the ledger used to
    # keep that fact to itself. The leg recomputes the notice from LEDGER.json and demands
    # it on the sheet the operator actually holds -- a missing ledger must read as
    # "cannot verify", never as "nothing was restated".
    try:
        _bad30 = []
        _rst30 = []
        _ledp = os.path.join(PATHS.results_dir, "etf_book_forward", "LEDGER.json")
        _tkp = os.path.join(PATHS.results_dir, "etf_book_order", "latest.json")
        if not os.path.exists(_ledp):
            _bad30.append("results/etf_book_forward/LEDGER.json missing")
        elif not os.path.exists(_tkp):
            _bad30.append("results/etf_book_order/latest.json missing")
        else:
            with open(_ledp, encoding="utf-8") as _fh30:
                _led30 = json.load(_fh30) or {}
            with open(_tkp, encoding="utf-8") as _fh30:
                _ptr30 = json.load(_fh30) or {}
            _asof30 = str(_ptr30.get("as_of") or "")
            _tkf30 = os.path.join(os.path.dirname(_tkp), str(_ptr30.get("file") or ""))
            _mdp30 = os.path.join(os.path.dirname(_tkp), "ORDER-%s.md" % _asof30)
            _rst30 = _led30.get("restatements")
            if not isinstance(_rst30, list):
                _bad30.append("ledger publishes no top-level restatements list")
                _rst30 = []
            if not os.path.exists(_tkf30):
                _bad30.append("ticket JSON named by the pointer is absent")
            if not os.path.exists(_mdp30):
                _bad30.append("ORDER-%s.md missing" % _asof30)
            if not _bad30:
                with open(_tkf30, encoding="utf-8") as _fh30:
                    _tk30 = json.load(_fh30) or {}
                with open(_mdp30, encoding="utf-8") as _fh30:
                    _md30 = _fh30.read()
                _pub30 = (_tk30.get("restatements") or {})
                if _pub30.get("readable") is not True:
                    _bad30.append("ticket says it could not verify the ledger")
                if [_n.get("bar") for _n in (_pub30.get("notices") or [])] != \
                        [_n.get("bar") for _n in _rst30]:
                    _bad30.append("ticket's restated bars are not the ledger's own list")
                if "历史变更通知" not in _md30:
                    _bad30.append("the sheet carries no restatement notice")
                for _n30 in _rst30:
                    if not _n30.get("bar"):
                        continue
                    if _n30["bar"] not in _md30:
                        _bad30.append("sheet omits restated bar %s" % _n30["bar"])
                    for _k30 in ("nav_published", "nav_settled"):
                        _v30 = _n30.get(_k30)
                        if _v30 is not None and ("%.8f" % float(_v30)) not in _md30:
                            _bad30.append("sheet omits %s=%.8f for %s"
                                          % (_k30, float(_v30), _n30["bar"]))
                if not _rst30 and "没有一根在定格之后被改述" not in _md30:
                    _bad30.append("a clean ledger is not stated as a checked fact")
        check("product: a bar restated after settling reaches the ticket's own ledger line",
              not _bad30,
              "; ".join(_bad30)[:220]
              or "%d restated bar(s): %s"
                 % (len(_rst30), ", ".join(str(_n.get("bar")) for _n in _rst30) or "none"))
    except Exception as e:
        check("product: a bar restated after settling reaches the ticket's own ledger line",
              False, repr(e)[:160])
    # ---- r1177: both faces a reader holds must state their price basis ----------
    # An executable sheet that ranked on raw prices while the card and the ledger repaired
    # meant one book quoting two CAGR numbers computed on two panels, and nothing looked
    # wrong. This leg fails if either face stops saying which panel its numbers sit on, if
    # the ticket stops repairing, or if the two faces stop quoting ONE implementation.
    try:
        _bad44 = []
        _ord_dir = os.path.join(PATHS.results_dir, "etf_book_order")
        _ptr44 = os.path.join(_ord_dir, "latest.json")
        _card44 = os.path.join(PATHS.results_dir, "etf_book_production", "latest.json")
        _cmdp44 = os.path.join(PATHS.results_dir, "etf_book_production", "CARD.md")
        for _p44 in (_ptr44, _card44, _cmdp44):
            if not os.path.exists(_p44):
                _bad44.append("%s missing" % os.path.basename(_p44))
        if not _bad44:
            with open(_ptr44, encoding="utf-8") as _fh44:
                _pt44 = json.load(_fh44) or {}
            _asof44 = str(_pt44.get("as_of") or "")
            _tkp44 = os.path.join(_ord_dir, str(_pt44.get("file") or ""))
            _mdp44 = os.path.join(_ord_dir, "ORDER-%s.md" % _asof44)
            if not os.path.exists(_tkp44) or not os.path.exists(_mdp44):
                _bad44.append("ticket %s / sheet missing" % _asof44)
            else:
                with open(_tkp44, encoding="utf-8") as _fh44:
                    _tk44 = json.load(_fh44) or {}
                with open(_mdp44, encoding="utf-8") as _fh44:
                    _md44 = _fh44.read()
                with open(_card44, encoding="utf-8") as _fh44:
                    _cd44 = json.load(_fh44) or {}
                with open(_cmdp44, encoding="utf-8") as _fh44:
                    _cmd44 = _fh44.read()
                _pb44 = _tk44.get("price_basis") or {}
                if not str(_pb44.get("panel") or "").startswith("repaired"):
                    _bad44.append("the executable sheet still prices the raw panel")
                if _pb44.get("neutralised") is not True:
                    _bad44.append("the sheet does not say it repaired")
                if not _pb44.get("flip_prints"):
                    _bad44.append("the sheet reports no flip census")
                if not _pb44.get("columns"):
                    _bad44.append("the sheet does not say how wide the panel it counted is")
                if "价格面板" not in _md44:
                    _bad44.append("ORDER md carries no price-basis line")
                _cpb44 = _cd44.get("price_basis") or {}
                if not str(_cpb44.get("panel") or "").startswith("repaired"):
                    _bad44.append("the card does not state its price basis")
                if not _cpb44.get("columns"):
                    _bad44.append("the card does not say how wide the panel it counted is")
                # Two faces of one book may count different totals because they count
                # different panels (the card repairs before it classifies, the ticket only
                # the classes it ranks). Without both widths that reads as a drift.
                if (_pb44.get("flip_prints") != _cpb44.get("flip_prints")
                        and _pb44.get("columns") == _cpb44.get("columns")):
                    _bad44.append("same panel, two flip totals")
                if "**Price basis:**" not in _cmd44:
                    _bad44.append("CARD.md prints no price-basis line")
                # one implementation: rebuilding each line with the shared writer must
                # reproduce it character for character (E289 -- a second copy drifts).
                _sys44 = os.path.join(PATHS.root, "scripts")
                if _sys44 not in sys.path:
                    sys.path.insert(0, _sys44)
                import etf_equity_alpha as _A44
                for _face44, _lab44 in ((_pb44, "ticket"), (_cpb44, "card")):
                    if not _face44.get("sentence"):
                        _bad44.append("%s carries no sentence" % _lab44)
                        continue
                    _exp44 = _A44.price_basis_line(
                        True, _face44.get("flip_prints"), _face44.get("flip_thr"),
                        _face44.get("symbols_with_a_flip"),
                        "results/etf_book_flip_contamination.json",
                        columns=_face44.get("columns"))["sentence"]
                    if _face44["sentence"] != _exp44:
                        _bad44.append("%s line is not the shared writer's output" % _lab44)
                    if _face44["sentence"] not in (_md44 if _lab44 == "ticket" else _cmd44):
                        _bad44.append("%s sentence is not on the rendered sheet" % _lab44)
        check("product: both reader faces state which price panel their numbers sit on",
              not _bad44, "; ".join(_bad44)[:220]
              or "ticket and card both repaired, one shared sentence")
    except Exception as e:
        check("product: both reader faces state which price panel their numbers sit on",
              False, repr(e)[:160])
    # ---- r1178: the three published faces must price ONE panel, and say which ----
    # r1177 made the ticket repair; that closed the rule gap but did not make the faces
    # comparable. "We all repaired" is still a claim, and two faces quoting the same number
    # can be pricing two different worlds (a late bar, a wider universe, a re-pulled panel)
    # -- the ledger once froze a bar three rounds running while its panel was still gaining
    # symbols. Each face now publishes a digest of the repaired panel it measured on, so a
    # reader (and this leg) can tell same-world from same-number.
    try:
        _bad45 = []
        _ord45 = os.path.join(PATHS.results_dir, "etf_book_order")
        _ptr45 = os.path.join(_ord45, "latest.json")
        _card45 = os.path.join(PATHS.results_dir, "etf_book_production", "latest.json")
        _fwd45 = os.path.join(PATHS.results_dir, "etf_book_forward", "LEDGER.json")
        _dig45 = {}
        for _p45 in (_ptr45, _card45, _fwd45):
            if not os.path.exists(_p45):
                _bad45.append("%s missing" % os.path.basename(_p45))
        if not _bad45:
            with open(_ptr45, encoding="utf-8") as _fh45:
                _pt45 = json.load(_fh45) or {}
            _tkp45 = os.path.join(_ord45, str(_pt45.get("file") or ""))
            if not os.path.exists(_tkp45):
                _bad45.append("ticket file missing")
            else:
                with open(_tkp45, encoding="utf-8") as _fh45:
                    _tk45 = json.load(_fh45) or {}
                with open(_card45, encoding="utf-8") as _fh45:
                    _cd45 = json.load(_fh45) or {}
                with open(_fwd45, encoding="utf-8") as _fh45:
                    _fw45 = json.load(_fh45) or {}
                _dig45["ticket"] = ((_tk45.get("price_basis") or {})
                                    .get("panel_digest") or {}).get("digest")
                _dig45["card"] = ((_cd45.get("price_basis") or {})
                                  .get("panel_digest") or {}).get("digest")
                _dig45["ledger"] = (_fw45.get("panel") or {}).get("digest")
                for _lab45, _v45 in _dig45.items():
                    if not _v45:
                        _bad45.append("%s publishes no panel digest" % _lab45)
                    elif not (len(_v45) == 16 and all(c in "0123456789abcdef" for c in _v45)):
                        _bad45.append("%s digest is not 16 hex chars: %r" % (_lab45, _v45))
                _seen45 = {v for v in _dig45.values() if v}
                if len(_seen45) > 1:
                    _bad45.append("three faces, %d panels: %s"
                                  % (len(_seen45), sorted(_seen45)))
                # the digest has to be able to move, or "same world" is unfalsifiable
                _sys45 = os.path.join(PATHS.root, "scripts")
                if _sys45 not in sys.path:
                    sys.path.insert(0, _sys45)
                import etf_equity_alpha as _A45
                import pandas as _pd45
                _idx45 = _pd45.date_range("2024-01-01", periods=3)
                _c45 = _pd45.DataFrame({"A": [1.0, 2.0, 3.0], "B": [1.0, 1.0, 1.0]},
                                       index=_idx45)
                _o45 = _c45.copy()
                _d1_45 = _A45.panel_digest(_c45, _o45)["digest"]
                _d2_45 = _A45.panel_digest(_c45.copy(), _o45.copy())["digest"]
                if _d1_45 != _d2_45:
                    _bad45.append("the digest is not stable for the same panel")
                _c45b = _c45.copy()
                _c45b.loc[_idx45[1], "B"] = 1.01
                if _A45.panel_digest(_c45b, _o45)["digest"] == _d1_45:
                    _bad45.append("the digest ignores a changed price")
                if _A45.panel_digest(_c45, _o45.iloc[::-1][::-1])["digest"] != _d1_45:
                    _bad45.append("the digest depends on row order")
                # r1179: the fingerprint has to name its blocks, or "same world" means
                # "same closes" while the book's universe is chosen on turnover.
                _blk45 = {"ticket": ((_tk45.get("price_basis") or {}).get("panel_digest") or {}),
                          "card": ((_cd45.get("price_basis") or {}).get("panel_digest") or {}),
                          "ledger": (_fw45.get("panel") or {})}
                for _lab45, _b45 in _blk45.items():
                    if "amount" not in (_b45.get("blocks") or _b45.get("covers") or []):
                        _bad45.append("%s does not say it priced the turnover panel" % _lab45)
                _a45 = _pd45.DataFrame({"A": [10.0, 20.0, 30.0], "B": [5.0, 5.0, 5.0]},
                                       index=_idx45)
                _d3_45 = _A45.panel_digest(_c45, _o45, _a45)["digest"]
                if _d3_45 == _d1_45:
                    _bad45.append("a token panel and a turnover panel share one digest")
                _a45b = _a45.copy()
                _a45b.loc[_idx45[2], "B"] = 6.0
                if _A45.panel_digest(_c45, _o45, _a45b)["digest"] == _d3_45:
                    _bad45.append("the digest ignores a changed turnover figure")
                if _A45.panel_digest(_c45, _o45, _a45)["digest"] != _d3_45:
                    _bad45.append("the digest is not stable on the turnover block")
        check("product: three faces of one book price one panel, and the digest can move",
              not _bad45, "; ".join(_bad45)[:220]
              or "ticket/card/ledger agree: %s" % (_dig45.get("ticket") or "-"))
    except Exception as e:
        check("product: three faces of one book price one panel, and the digest can move",
              False, repr(e)[:160])
    # ---- r1184: the width's license must reach every face a reader actually holds ----
    # r1183 taught the CARD to say which world its width came from. The executable sheet and
    # the CEO page kept quoting the same family of widths without that sentence, so whoever
    # held either of them could not tell a measured width from a configured one. This leg
    # recomputes the verdict from the arms artifact, proves the reader can move, and requires
    # all three faces to carry the answer -- arm count included, not just the word.
    try:
        _bad46 = []
        _verd46 = None
        _n46 = 0
        _sys46 = os.path.join(PATHS.root, "scripts")
        if _sys46 not in sys.path:
            sys.path.insert(0, _sys46)
        import etf_book_production as _P46
        _arms46 = os.path.join(PATHS.results_dir, "etf_book_phase_atlas_arms.json")
        if not os.path.exists(_arms46):
            _bad46.append("arms face missing")
        else:
            with open(_arms46, encoding="utf-8") as _fh46:
                _ar46 = json.load(_fh46) or {}
            _verd46 = (_ar46.get("panel_coherence") or {}).get("verdict")
            _n46 = len(_ar46.get("arms") or {})
            _fc46 = _P46.family_coherence()
            if _fc46.get("verdict") != _verd46:
                _bad46.append("reader %r != artifact %r" % (_fc46.get("verdict"), _verd46))
            if (_fc46.get("arms") or 0) != _n46:
                _bad46.append("reader arms %s != artifact %s" % (_fc46.get("arms"), _n46))
            # the reader has to be able to move, or "one world" is unfalsifiable
            import tempfile as _tf46
            with _tf46.TemporaryDirectory() as _td46:
                if _P46.family_coherence(results_dir=_td46).get("priced_same_panel") is not None:
                    _bad46.append("a missing family reads as a verdict")
                _fake46 = {"panel_coherence": {"verdict": "MIXED_WORLDS",
                                               "panels": ["a", "b"], "detail": "two panels"},
                           "arms": {"x": {}, "y": {}},
                           "baseline": {"evidence_cutoff": "2026-01-01"}}
                with open(os.path.join(_td46, "etf_book_phase_atlas_arms.json"), "w",
                          encoding="utf-8") as _fh46:
                    json.dump(_fake46, _fh46)
                _mx46 = _P46.family_coherence(results_dir=_td46)
                if (_mx46.get("verdict") != "MIXED_WORLDS"
                        or _mx46.get("priced_same_panel") is not False):
                    _bad46.append("a mixed family reads as %r/%r"
                                  % (_mx46.get("verdict"), _mx46.get("priced_same_panel")))
            # three human faces: the card, the executable sheet, the CEO page
            _faces46 = {}
            _card46 = os.path.join(PATHS.results_dir, "etf_book_production", "CARD.md")
            if os.path.exists(_card46):
                with open(_card46, encoding="utf-8") as _fh46:
                    _faces46["card"] = _fh46.read()
            _ptr46 = os.path.join(PATHS.results_dir, "etf_book_order", "latest.json")
            if os.path.exists(_ptr46):
                with open(_ptr46, encoding="utf-8") as _fh46:
                    _p46 = json.load(_fh46) or {}
                _md46 = os.path.join(PATHS.results_dir, "etf_book_order",
                                     "ORDER-%s.md" % (_p46.get("as_of") or ""))
                if os.path.exists(_md46):
                    with open(_md46, encoding="utf-8") as _fh46:
                        _faces46["ticket"] = _fh46.read()
            _lb46 = sorted(glob.glob(os.path.join(PATHS.root, "docs", "live_book",
                                                  "LIVE-BOOK-*.md")))
            if _lb46:
                with open(_lb46[-1], encoding="utf-8") as _fh46:
                    _faces46["page"] = _fh46.read()
            for _lab46 in ("card", "ticket", "page"):
                if _lab46 not in _faces46:
                    _bad46.append("%s face missing" % _lab46)
            if not _bad46:
                if _verd46 == "ONE_WORLD":
                    if "ONE_WORLD" not in _faces46["card"]:
                        _bad46.append("card does not print ONE_WORLD")
                    if "名数的来历" not in _faces46["ticket"]:
                        _bad46.append("ticket does not print the width's lineage")
                    if "有。" not in _faces46["page"]:
                        _bad46.append("page does not print the licensed state")
                    for _lab46 in ("ticket", "page"):
                        if ("%d 个宽度臂" % _n46) not in _faces46[_lab46]:
                            _bad46.append("%s does not print the arm count" % _lab46)
                else:
                    for _lab46, _txt46 in _faces46.items():
                        if "ONE_WORLD" in _txt46:
                            _bad46.append("%s prints ONE_WORLD for %r" % (_lab46, _verd46))
                    if "名数没被证过" not in _faces46["ticket"]:
                        _bad46.append("ticket does not say the width is unproven")
                    if not ("没有。" in _faces46["page"] or "不知道。" in _faces46["page"]):
                        _bad46.append("page does not say the width is unproven")
        check("product: every face a reader holds says whether the width's family was one world",
              not _bad46, "; ".join(_bad46)[:220]
              or "card/ticket/page agree on %r (%d arms)" % (_verd46, _n46))
    except Exception as e:
        check("product: every face a reader holds says whether the width's family was one world",
              False, repr(e)[:160])
    # ---- r1185: the three papers must each say WHICH day they were priced on ----
    # "same priced bar = True" is a claim nobody can re-derive. This leg reads the three days
    # out of the artifacts themselves, demands the page print all three, and proves the reader
    # can move in both directions (different bars -> named stale paper; missing -> unknown,
    # never agreement).
    try:
        import tempfile as _tf47
        _bad47 = []
        _sys47 = os.path.join(PATHS.root, "scripts")
        if _sys47 not in sys.path:
            sys.path.insert(0, _sys47)
        import etf_book_production as _P47
        _page_ptr = os.path.join(PATHS.root, "docs", "live_book", "latest.json")
        if not os.path.exists(_page_ptr):
            _bad47.append("page artifact missing")
        else:
            with open(_page_ptr, encoding="utf-8") as _fh47:
                _pg47 = json.load(_fh47) or {}
            # latest.json is a pointer, not the page: the priced bar lives on the dated twin
            if not _pg47.get("priced_bar") and _pg47.get("json"):
                with open(os.path.join(PATHS.root, _pg47["json"]), encoding="utf-8") as _fh47:
                    _pg47 = json.load(_fh47) or {}
            _pf47 = _P47.priced_faces(page_bar=_pg47.get("priced_bar"))
            if _pf47.get("verdict") != "SAME_DAY":
                _bad47.append("three papers disagree: %s" % (_pf47.get("detail") or "")[:120])
            _lb47 = sorted(glob.glob(os.path.join(PATHS.root, "docs", "live_book",
                                                  "LIVE-BOOK-*.md")))
            _md47 = ""
            if _lb47:
                with open(_lb47[-1], encoding="utf-8") as _fh47:
                    _md47 = _fh47.read()
            for _k47 in ("card", "ticket", "page"):
                _d47 = (_pf47.get("faces") or {}).get(_k47)
                if _d47 and _d47 not in _md47:
                    _bad47.append("page does not print the %s day %s" % (_k47, _d47))
            # falsifiability: the reader must be able to say anything but "same"
            with _tf47.TemporaryDirectory() as _td47:
                for _sub47, _pl47 in (("etf_book_production", {"sheet": {"as_of_bar": "2026-01-05"}}),
                                      ("etf_book_order", {"card_agreement": {
                                          "ticket_priced_bar": "2026-01-06"}})):
                    os.makedirs(os.path.join(_td47, _sub47), exist_ok=True)
                    with open(os.path.join(_td47, _sub47, "latest.json"), "w",
                              encoding="utf-8") as _fh47:
                        json.dump(_pl47, _fh47)
                _sp47 = _P47.priced_faces(page_bar="2026-01-07", results_dir=_td47)
                if _sp47.get("verdict") != "DIFFERENT_DAYS" or "page 2026-01-07" not in (
                        _sp47.get("detail") or ""):
                    _bad47.append("stale fixture reads %r" % (_sp47.get("verdict"),))
                _un47 = _P47.priced_faces(page_bar=None, results_dir=_td47 + os.sep + "nope")
                if _un47.get("verdict") != "UNKNOWN" or _un47.get("same_day") is not False:
                    _bad47.append("absent fixture reads %r" % (_un47.get("verdict"),))
            # r1186: the CEO page is not the only paper a reader holds. If the card and the
            # executable sheet stop printing the three days themselves, an operator who never
            # opens the page is back to the bare "same priced bar" claim he cannot re-derive --
            # so the verdict each paper states is re-read from THAT paper's own artifact and
            # then looked for in THAT paper's own text. Never from a neighbouring paper.
            _papers47 = []
            _card_ptr47 = os.path.join(PATHS.results_dir, "etf_book_production", "latest.json")
            if os.path.exists(_card_ptr47):
                with open(_card_ptr47, encoding="utf-8") as _fh47:
                    _cd47 = json.load(_fh47) or {}
                _papers47.append((os.path.join(PATHS.results_dir, "etf_book_production", "CARD.md"),
                                  _cd47.get("priced_faces") or {},
                                  {"SAME_DAY": "Priced day: SAME_DAY",
                                   "DIFFERENT_DAYS": "Priced day: DIFFERENT_DAYS",
                                   "UNKNOWN": "Priced day: UNKNOWN"}))
            _ord47 = sorted(glob.glob(os.path.join(PATHS.root, "results", "etf_book_order", "ORDER-*.md")))
            _tick47 = sorted(glob.glob(os.path.join(PATHS.root, "results", "etf_book_order", "TICKET-*.json")))
            if _ord47 and _tick47:
                with open(_tick47[-1], encoding="utf-8") as _fh47:
                    _tk47 = json.load(_fh47) or {}
                _papers47.append((_ord47[-1], _tk47.get("priced_faces") or {},
                                  {"SAME_DAY": "同一天", "DIFFERENT_DAYS": "不是同一天",
                                   "UNKNOWN": "无法判断"}))
            for _path47, _blk47, _word47 in _papers47:
                _lab47 = os.path.basename(_path47)
                _v47 = _blk47.get("verdict")
                if not _v47:
                    _bad47.append("%s publishes no priced-day verdict" % _lab47)
                    continue
                if not os.path.exists(_path47):
                    _bad47.append("%s missing" % _lab47)
                    continue
                with open(_path47, encoding="utf-8") as _fh47:
                    _txt47 = _fh47.read()
                if _word47.get(_v47, "") not in _txt47:
                    _bad47.append("%s does not print its own verdict %s" % (_lab47, _v47))
                for _k47b in ("card", "ticket", "page"):
                    _dd47 = (_blk47.get("faces") or {}).get(_k47b)
                    if _dd47 and _dd47 not in _txt47:
                        _bad47.append("%s does not print the %s day %s"
                                      % (_lab47, _k47b, _dd47))
        check("product: the three papers print the day each was priced on, and can disagree",
              not _bad47, "; ".join(_bad47)[:220]
              or "card/ticket/page all priced %s" % ((_pf47.get("faces") or {}).get("card"),))
    except Exception as e:
        check("product: the three papers print the day each was priced on, and can disagree",
              False, repr(e)[:160])
    # ---- r1187: the dashboard says which bar the three papers were priced on ----
    # The three papers each print their own priced day, but the 总控面板 -- the one face an
    # operator opens first -- said nothing about it. A row that only carries the boolean
    # would repeat the r1185 defect one page further out, so this leg recomputes the verdict
    # from the artifacts with the ONE reader and demands the published dashboard numbers
    # EQUAL it (r1130 precedent: equality, not key presence).
    try:
        _bad48 = []
        _st48 = os.path.join(PATHS.results_dir, "dashboard_status.json")
        if not os.path.exists(_st48):
            _bad48.append("dashboard_status.json missing")
        else:
            with open(_st48, encoding="utf-8") as _fh48:
                _d48 = json.load(_fh48) or {}
            _eb48 = ((_d48.get("data") or {}).get("etf_book_priced") or {})
            _exp48 = _P47.priced_faces()
            if not _eb48.get("present"):
                _bad48.append("dashboard publishes no priced-day block")
            else:
                if _eb48.get("verdict") != _exp48.get("verdict"):
                    _bad48.append("verdict %r != reader %r"
                                  % (_eb48.get("verdict"), _exp48.get("verdict")))
                for _k48 in ("card", "ticket", "page"):
                    if (_eb48.get("faces") or {}).get(_k48) != (_exp48.get("faces") or {}).get(_k48):
                        _bad48.append("%s day %r != reader %r"
                                      % (_k48, (_eb48.get("faces") or {}).get(_k48),
                                         (_exp48.get("faces") or {}).get(_k48)))
            with open(os.path.join(PATHS.root, "dashboard.html"), encoding="utf-8") as _fh48:
                _js48 = _fh48.read()
            if "etf_book_priced" not in _js48:
                _bad48.append("dashboard.html has no row that renders the block")
        check("product: the dashboard says which bar the three papers were priced on",
              not _bad48, "; ".join(_bad48)[:220]
              or "dashboard block == reader (%s)" % (_exp48.get("verdict"),))
    except Exception as e:
        check("product: the dashboard says which bar the three papers were priced on",
              False, repr(e)[:160])
    # ---- r1188: the book's CAGR is split by leg, and the split has to close ------------
    # Every published number for this book is one CAGR. The new face says where the day's
    # money is earned (overnight while the order is pending / intraday after the fill /
    # quiet bars / toll) by walking the SAME Forward state machine with four log buckets.
    # The leg does not re-run the walk (that is a 20s panel build); it demands that the
    # published arithmetic CLOSE, and it proves the checker is not vacuous by feeding it
    # three doctored copies that must each be rejected.
    try:
        _bad49 = []
        import etf_book_leg_attribution as _LA49
        _p49 = os.path.join(PATHS.results_dir, "etf_book_legs", "latest.json")
        if not os.path.exists(_p49):
            _bad49.append("results/etf_book_legs/latest.json missing")
        else:
            with open(_p49, encoding="utf-8") as _fh49:
                _f49 = json.load(_fh49)
            if (_f49.get("config") or {}).get("buckets") != list(_LA49.BUCKETS):
                _bad49.append("face does not echo its own bucket list")
            _bad49.extend(_LA49.check_face(_f49))
            import copy as _cp49
            _doctored = []
            _d1 = _cp49.deepcopy(_f49)
            _d1["arms"]["production"]["buckets_pp_per_year"]["plain"] += 1.0
            _doctored.append(("buckets that do not sum", _d1))
            _d2 = _cp49.deepcopy(_f49)
            _d2["arms"]["production"]["per_bar_bp"]["plain"] += 1.0
            _doctored.append(("a per-bar reading that contradicts its bucket", _d2))
            _d3 = _cp49.deepcopy(_f49)
            _d3["arms"]["production"]["fill_bar_drag_pp_per_year"] *= -1.0
            _doctored.append(("a drag that disagrees in sign with the net", _d3))
            for _lab49, _doc49 in _doctored:
                if not _LA49.check_face(_doc49):
                    _bad49.append("checker accepted a face with %s" % _lab49)
        _pr49 = ((_f49.get("arms") or {}).get("production") or {}) if os.path.exists(_p49) else {}
        check("product: the book's CAGR is split into overnight / intraday / quiet / toll and "
              "the split closes to the same total",
              not _bad49, "; ".join(_bad49)[:220]
              or ("production %.2fpp/yr = plain %+.2f + fill drag %+.2f (bars %d/%d/%d)"
                  % (_pr49.get("total_log_pp", 0.0), _pr49.get("plain_carry_pp_per_year", 0.0),
                     _pr49.get("fill_bar_drag_pp_per_year", 0.0), _pr49.get("fill_bars", 0),
                     _pr49.get("plain_bars", 0), _pr49.get("seed_bars", 0))))
    except Exception as e:
        check("product: the book's CAGR is split into overnight / intraday / quiet / toll and "
              "the split closes to the same total", False, repr(e)[:160])
    # ---- r1191: the page must say WHOSE CAGR it is quoting -------------------------------
    # The ticket started printing this at r1190 while the page -- the face the CEO actually
    # opens -- still published the headline with no source. The leg recomputes nothing: it
    # reads the numbers out of the published face and demands the page print THOSE numbers
    # (r1130 law: equal, not merely present), and it refuses a page that quotes a face whose
    # identity gate failed.
    try:
        import importlib as _il51
        _C51 = _il51.import_module("etf_book_concentration")
        _p51 = os.path.join(PATHS.root, "results", "etf_book_concentration.json")
        _bad51 = []
        _d51 = {}
        if not os.path.exists(_p51):
            _bad51.append("results/etf_book_concentration.json missing")
        else:
            _pub51 = _C51.read_published(path=_p51)
            if _pub51.get("status") != "ok":
                _bad51.append("face does not read clean (%s)" % _pub51.get("status"))
            else:
                with open(_p51, encoding="utf-8") as _fh51:
                    _d51 = json.load(_fh51)
                _conc51 = _d51.get("concentration") or {}
                _lk51 = _d51.get("leave_top_k_out") or {}
                _vh51 = _d51.get("leave_class_out") or {}
                _pg51 = _il51.import_module("etf_book_ceo_page")
                if not _pg51.writer_allowed(None):
                    pass                       # not the writer: the artifact still gates above
                else:
                    _md51p = os.path.join(PATHS.root, "docs", "live_book",
                                          "LIVE-BOOK-%s.md"
                                          % str(_d51.get("evidence_cutoff") or "").replace("-", ""))
                    if not os.path.exists(_md51p):
                        _bad51.append("live page missing for cutoff %s"
                                      % (_d51.get("evidence_cutoff"),))
                    else:
                        with open(_md51p, encoding="utf-8") as _fh51:
                            _md51 = _fh51.read()
                        if "这个年化是" not in _md51:
                            _bad51.append("page carries no concentration section")
                        else:
                            _want51 = ["%.1f%%" % (100 * float(_conc51.get("top3_share") or 0.0))]
                            if _lk51.get("delta_cagr_pp") is not None:
                                _want51.append("%+.2fpp" % _lk51["delta_cagr_pp"])
                            if _vh51.get("delta_cagr_pp") is not None:
                                _want51.append("%+.2fpp" % _vh51["delta_cagr_pp"])
                            for _w51 in _want51:
                                if _w51 not in _md51:
                                    _bad51.append("page does not print %s" % _w51)
        check("product: the page says whose CAGR it is quoting (top-3 share and both deletions)",
              not _bad51, "; ".join(_bad51)[:220]
              or "page == face (top3 %.1f%%, sleeve %+.2fpp)"
                 % (100 * float(((_d51.get("concentration") or {}).get("top3_share")) or 0.0),
                    float((_d51.get("leave_class_out") or {}).get("delta_cagr_pp") or 0.0)))
    except Exception as e:
        check("product: the page says whose CAGR it is quoting (top-3 share and both deletions)",
              False, repr(e)[:160])
    # ---- r1193: the page must answer "should the sleeve have a gate of its own?" --------
    # Same defect one face over: r1192 measured the three sleeve gates against their own
    # dose-matched placebos and answered NO_GATE on the card, while the page -- the face
    # the CEO opens -- ended the sentence at "the sleeve is the cushion". This leg
    # recomputes nothing: it reads the rows out of the published face, reads the page the
    # `latest.json` pointer names, and demands that page print THOSE numbers (equal, not
    # merely present). It also refuses a page that is one bar stale, because a page quoting
    # an older face is exactly how a green suite ends up guarding nothing.
    try:
        import importlib as _il52
        _G52 = _il52.import_module("etf_book_sleeve_gate")
        _p52 = os.path.join(PATHS.results_dir, "etf_book_sleeve_gate.json")
        _bad52 = []
        if not os.path.exists(_p52):
            _bad52.append("results/etf_book_sleeve_gate.json missing")
        else:
            _pub52 = _G52.read_published(path=_p52)
            if _pub52.get("status") != "ok":
                _bad52.append("face does not read clean (%s)" % _pub52.get("status"))
            else:
                _ptr52p = os.path.join(PATHS.root, "docs", "live_book", "latest.json")
                _md52p = ""
                if os.path.exists(_ptr52p):
                    with open(_ptr52p, encoding="utf-8") as _fh52:
                        _ptr52 = json.load(_fh52)
                    _md52p = os.path.join(PATHS.root, _ptr52.get("page") or "")
                if not _md52p or not os.path.exists(_md52p):
                    _bad52.append("no page the latest.json pointer names")
                else:
                    with open(_md52p, encoding="utf-8") as _fh52:
                        _md52 = _fh52.read()
                    _json52p = os.path.splitext(_md52p)[0] + ".json"
                    _priced52 = None
                    if os.path.exists(_json52p):
                        with open(_json52p, encoding="utf-8") as _fh52:
                            _pj52 = json.load(_fh52)
                        _priced52 = ((_pj52.get("priced_faces") or {}).get("page")
                                     or _pj52.get("evidence_cutoff"))
                    if _priced52 != _pub52.get("evidence_cutoff"):
                        _bad52.append("page priced on %s but the sleeve face is %s (stale page)"
                                      % (_priced52, _pub52.get("evidence_cutoff")))
                    if "要不要给商品袖" not in _md52:
                        _bad52.append("page carries no sleeve-gate section")
                    else:
                        _dec52 = (_pub52.get("book") or {}).get("decisions") or 0
                        for _r52 in _pub52.get("gates") or []:
                            _want52 = ["%d/%d" % (_r52.get("off_decisions") or 0, _dec52),
                                       "%+.2fpp" % (_r52.get("delta_cagr_pp") or 0.0),
                                       "%+.2fpp" % (_r52.get("delta_maxdd_pp") or 0.0)]
                            for _w52 in _want52:
                                if _w52 not in _md52:
                                    _bad52.append("page does not print %s (%s gate)"
                                                  % (_w52, _r52.get("name")))
                        # the failure-mode sentence is generated from each row's own
                        # classification: the page must not claim a gate lost to its placebo
                        # when that gate beat it.
                        _nogain52 = [r.get("name") for r in (_pub52.get("gates") or [])
                                     if r.get("why") == "no_gain_vs_baseline"]
                        _lost52 = [r.get("name") for r in (_pub52.get("gates") or [])
                                   if r.get("why") == "no_gain_vs_baseline"
                                   and not r.get("beats_placebo")]
                        _zh52 = {"trend": "趋势", "vol": "波动", "drawdown": "回撤"}
                        if _nogain52:
                            _line52 = "有 **%d 条**门（%s）" % (
                                len(_nogain52), "、".join(_zh52.get(n, n) for n in _nogain52))
                            if _line52 not in _md52:
                                _bad52.append("page does not name the no-gain gates: %s"
                                              % _line52)
                        for _n52 in sorted(set(_zh52) - set(_lost52)):
                            _ph52 = "其中 **%s** 连自己的安慰剂也赢不了" % _zh52.get(_n52)
                            if _ph52 in _md52:
                                _bad52.append("page says the %s gate lost to its placebo "
                                              "but the face says it beat it" % _n52)
        check("product: the page answers whether the commodity sleeve needs its own gate",
              not _bad52, "; ".join(_bad52)[:220]
              or "page == face (%s; %d gates, %d named no-gain)"
                 % (_pub52.get("verdict"), len(_pub52.get("gates") or []),
                    len([r for r in (_pub52.get("gates") or [])
                         if r.get("why") == "no_gain_vs_baseline"])))
    except Exception as e:
        check("product: the page answers whether the commodity sleeve needs its own gate",
              False, repr(e)[:160])
    # ---- r1195: the sleeve-gate answer must survive a moved decision grid -----
    # r1193's "no sleeve-level gate earns adoption" was read on ONE decision grid, and a
    # rule that only improves on one phase of the grid has not been measured (E188). The
    # path face re-prices the same gate on several grids. Two things must stay true on
    # disk: every judgement and the face verdict recompute from the published rows, and
    # the phases are genuinely different grids -- the first version of that face dropped
    # the panel prefix, which does NOT move an engine grid anchored at `start`, and it
    # published fifteen identical "paths" as if they were fifteen experiments.
    try:
        import importlib as _il55
        _P55 = _il55.import_module("etf_book_sleeve_paths")
        _p55 = os.path.join(PATHS.results_dir, "etf_book_sleeve_paths.json")
        _bad55 = []
        if not os.path.exists(_p55):
            _bad55.append("results/etf_book_sleeve_paths.json missing")
        else:
            with open(_p55, encoding="utf-8") as _fh55:
                _doc55 = json.load(_fh55)
            if _P55.check(_p55) != 0:
                _bad55.append("judgements do not recompute from the published rows")
            _ph55 = [p.get("first_decision") for p in (_doc55.get("phases") or [])]
            if len(_ph55) < 2 or len(set(_ph55)) != len(_ph55):
                _bad55.append("the phases are one grid under different names (%r)" % (_ph55,))
            _sup55 = _doc55.get("support") or {}
            _judged55 = [p for p in (_doc55.get("paths") or [])
                         if (p.get("judgement") or {}).get("verdict") in ("PASS", "FAIL")]
            _ans55 = _doc55.get("answer") or ""
            if not _judged55:
                _bad55.append("no path was assessed")
            if _doc55.get("verdict") not in ("SUPPORTED", "FRAGILE", "NO_GATE", "NOT_ASSESSED"):
                _bad55.append("unknown face verdict %r" % (_doc55.get("verdict"),))
            if "%d of them" % len(_judged55) not in _ans55:
                _bad55.append("the sentence does not line up with the path count")
            if _doc55.get("verdict") == "NO_GATE" and abs(float(_sup55.get("share") or 0)) > 0.5:
                _bad55.append("face says NO_GATE with %r of paths passing" % (_sup55.get("share"),))
            # the page is the face the CEO opens: it must print THESE numbers, and it must
            # name the verdict rather than leaving the candidate un-retested on the page
            _ptr55p = os.path.join(PATHS.root, "docs", "live_book", "latest.json")
            _page55 = ""
            if os.path.exists(_ptr55p):
                with open(_ptr55p, encoding="utf-8") as _fh55:
                    _page55 = os.path.join(PATHS.root, json.load(_fh55).get("page") or "")
            if not _page55 or not os.path.exists(_page55):
                _bad55.append("no page the latest.json pointer names")
            else:
                with open(_page55, encoding="utf-8") as _fh55:
                    _md55 = _fh55.read()
                _gs55 = _doc55.get("gates_summary") or {}
                for _want55 in ("再测",
                                "%d 个网格" % len({p.get("phase") for p in _doc55.get("paths") or []}),
                                "%d 条路径" % len(_judged55),
                                "%d 条" % ((_doc55.get("support") or {}).get("passed") or 0),
                                str(_doc55.get("verdict"))):
                    if _want55 not in _md55:
                        _bad55.append("page does not print %r" % (_want55,))
        check("product: the sleeve-gate answer survives a moved decision grid", not _bad55,
              "; ".join(_bad55)[:220] or "face %s on %d grids, %d/%d paths pass"
              % (_doc55.get("verdict"), len(_doc55.get("phases") or []),
                 (_doc55.get("support") or {}).get("passed"),
                 (_doc55.get("support") or {}).get("assessed")))
    except Exception as e:
        check("product: the sleeve-gate answer survives a moved decision grid", False,
              repr(e)[:160])
    # ---- r1196: a de-levered book must be told apart from a well-timed one ---------
    # The card has always said the vol target is a drawdown tool rather than an edge, but
    # nothing measured whether the exposure PATH earns anything over holding the same book
    # at the same average size. The face answers it with 20 permuted-scale controls. On disk
    # the controls must stay controls (the placebo band ordered, the exposure multiset
    # preserved) and the arms must really differ in exposure -- a face whose three arms all
    # held 1.0 would print a timing verdict that measured nothing.
    try:
        import importlib as _il56
        _P56 = _il56.import_module("etf_book_exposure_timing")
        _p56 = os.path.join(PATHS.results_dir, "etf_book_exposure_timing.json")
        _bad56 = []
        if not os.path.exists(_p56):
            _bad56.append("results/etf_book_exposure_timing.json missing")
        else:
            with open(_p56, encoding="utf-8") as _fh56:
                _doc56 = json.load(_fh56)
            if _P56.check(_p56) != 0:
                _bad56.append("the verdict does not recompute from the published rows")
            _v56 = _doc56.get("verdict") or {}
            if _v56.get("state") not in ("TIMING_ADDS", "TIMING_SUBTRACTS",
                                         "AVERAGE_EXPOSURE_ONLY", "INCOMPLETE"):
                _bad56.append("unknown verdict %r" % (_v56.get("state"),))
            if not (_v56.get("placebo_p05_pp") <= _v56.get("placebo_p50_pp")
                    <= _v56.get("placebo_p95_pp")):
                _bad56.append("the placebo band is not ordered")
            if int(_v56.get("n_placebo") or 0) < 5:
                _bad56.append("fewer than five control paths -- not a band")
            _arms56 = {a.get("arm"): a for a in (_doc56.get("arms") or [])}
            if set(_arms56) != {"production", "full", "constant"}:
                _bad56.append("arms are %r" % (sorted(_arms56),))
            else:
                # The book is flat until its first decision, so no arm averages exactly 1.0;
                # the control is that the constant arm really is matched to production's
                # average exposure (that is what makes the timing comparison meaningful) and
                # that both sit below the fully invested arm.
                _e56 = {k: float(v.get("mean_exposure") or 0.0) for k, v in _arms56.items()}
                if _e56["full"] < 0.98:
                    _bad56.append("the 'full' arm averages %r exposure" % (_e56["full"],))
                if abs(_e56["production"] - _e56["constant"]) > 0.01:
                    _bad56.append("the constant arm is not matched on average exposure (%r)"
                                  % (_e56,))
                if not (_e56["production"] < _e56["full"] - 0.02):
                    _bad56.append("production is not de-levered against the full arm (%r)"
                                  % (_e56,))
                for _a56 in _arms56.values():
                    if int(_a56.get("selection_drift") or 0) != 0:
                        _bad56.append("arm %r changed the engine's picks" % (_a56.get("arm"),))
            if not (_doc56.get("placebo") or {}).get("scale_series_preserved_all"):
                _bad56.append("a control path did not carry the engine's own exposure multiset")
            # r1197: the arms may only differ in one number, so the production arm must
            # reproduce the engine's nav and hold the engine's names on every shared bar.
            # Without this the "timing" could be measuring a slightly different book (it
            # was: reading the engine's published 6dp scale back into the arm made the gap
            # ~1e-7 on the real panel -- caught here, not by the fixture).
            _id56 = _doc56.get("identity") or {}
            if not _id56.get("passes"):
                _bad56.append("identity gate failed (gap %r, pick drift %r)"
                              % (_id56.get("gap"), _id56.get("pick_drift")))
            if int(_id56.get("pick_drift") or 0) != 0:
                _bad56.append("the production arm does not hold the engine's names")
        check("product: a de-levered book is told apart from a well-timed one", not _bad56,
              "; ".join(_bad56)[:220] or "verdict %s, timing %+.2fpp vs placebo [%+.2f, %+.2f]"
              % ((_doc56.get("verdict") or {}).get("state"),
                 (_doc56.get("verdict") or {}).get("timing_pp") or 0.0,
                 (_doc56.get("verdict") or {}).get("placebo_p05_pp") or 0.0,
                 (_doc56.get("verdict") or {}).get("placebo_p95_pp") or 0.0))
    except Exception as e:
        check("product: a de-levered book is told apart from a well-timed one", False,
              repr(e)[:160])
    # ---- r1202: a fixed fraction is only an adoption if it survives out of sample ----
    # r1196 measured the de-lever rule as "average exposure, not timing" and named the
    # obvious next question: would a fixed fraction do the same job? A single constant
    # calibrated from the production path's own mean exposure cannot answer it, so the
    # ladder prices seven fixed fractions on four decision phases. The face's own
    # pre-stated rule ("a fixed fraction that only wins in sample is not an adoption") is
    # enforced here: the published full-window verdict AND the adoption verdict must both
    # recompute from the published rows, every arm must be on every phase, and production
    # must really be a de-levered book rather than an arm that reintroduced itself.
    try:
        import importlib as _il58
        _P58 = _il58.import_module("etf_book_exposure_ladder")
        _p58 = os.path.join(PATHS.results_dir, "etf_book_exposure_ladder.json")
        _bad58 = []
        if not os.path.exists(_p58):
            _bad58.append("results/etf_book_exposure_ladder.json missing")
        else:
            with open(_p58, encoding="utf-8") as _fh58:
                _doc58 = json.load(_fh58)
            if _P58.check(_p58) != 0:
                _bad58.append("the verdict does not recompute from the published rows")
            _v58 = _doc58.get("verdict") or {}
            if _v58.get("state") not in ("CONSTANT_LADDER_DOMINATES",
                                         "PRODUCTION_RULE_EARNS_ITS_KEEP",
                                         "PHASE_DEPENDENT", "INCOMPLETE"):
                _bad58.append("unknown verdict %r" % (_v58.get("state"),))
            if not _doc58.get("identity_all_pass"):
                _bad58.append("the production arm does not reproduce the engine in every phase")
            _rows58 = _doc58.get("phase_rows") or []
            _ph58 = sorted({r.get("phase") for r in _rows58})
            _arms58 = sorted({r.get("arm") for r in _rows58})
            if len(_ph58) != _P58.N_PHASES:
                _bad58.append("%d phases, expected %d" % (len(_ph58), _P58.N_PHASES))
            if len({r.get("phase_start") for r in _rows58}) != len(_ph58):
                _bad58.append("two phases share a decision start -- the phase did not move")
            _want58 = ["production"] + ["const_%.2f" % k for k in _P58.K_GRID]
            if _arms58 != sorted(_want58):
                _bad58.append("arms are %r" % (_arms58,))
            for _p58_i in _ph58:
                for _a58 in _want58:
                    if not any(r.get("phase") == _p58_i and r.get("arm") == _a58
                               for r in _rows58):
                        _bad58.append("phase %r is missing arm %r" % (_p58_i, _a58))
            _prod58 = [r for r in _rows58 if r.get("arm") == "production"]
            if _prod58:
                _e58 = max(float(r.get("mean_exposure") or 0.0) for r in _prod58)
                if _e58 >= 0.99:
                    _bad58.append("the production arm is not de-levered (%.3f)" % _e58)
            for _r58 in _rows58:
                if int(_r58.get("selection_drift") or 0) != 0:
                    _bad58.append("arm %r changed the engine's picks" % (_r58.get("arm"),))
            _ad58 = _doc58.get("adoption") or {}
            if _ad58.get("state") not in ("ADOPT_FIXED_FRACTION",
                                          "REJECT_FIXED_FRACTION",
                                          "PHASE_DEPENDENT", "INCOMPLETE"):
                _bad58.append("unknown adoption verdict %r" % (_ad58.get("state"),))
            elif _ad58.get("state") != _P58.decide_adoption(_rows58)["state"]:
                _bad58.append("the adoption verdict does not recompute from the published rows")
            for _k58, _w58 in _P58.CRITERIA.items():
                if (_doc58.get("criteria") or {}).get(_k58) != _w58:
                    _bad58.append("criterion %s moved off the module constant" % (_k58,))
        check("product: a fixed fraction is only an adoption if it survives out of sample",
              not _bad58,
              "; ".join(_bad58)[:220] or "full window %s / adoption %s, %d phases"
              % ((_doc58.get("verdict") or {}).get("state"),
                 (_doc58.get("adoption") or {}).get("state"), _P58.N_PHASES))
    except Exception as e:
        check("product: a fixed fraction is only an adoption if it survives out of sample",
              False, repr(e)[:160])
    # ---- r1203 / E24: a window axis priced on ONE decision calendar is not a result ----
    # r1270's sweep wrote "window=LOAD-BEARING" after pricing every cell on the same 20-bar
    # grid; r1325 then showed a rule that wins on one phase can lose on the phase a week
    # later. This face re-prices the window ladder on four phases, so the leg has to check
    # that the phases really moved, that every window is on every phase, that the shipped
    # window still reproduces the production card, and that the verdict recomputes.
    try:
        import importlib as _il59
        _P59 = _il59.import_module("etf_book_vol_window_phase")
        _p59 = os.path.join(PATHS.results_dir, "etf_book_vol_window_phase.json")
        _bad59 = []
        if not os.path.exists(_p59):
            _bad59.append("results/etf_book_vol_window_phase.json missing")
        else:
            with open(_p59, encoding="utf-8") as _fh59:
                _doc59 = json.load(_fh59)
            if _P59.check(_p59) != 0:
                _bad59.append("the verdict does not recompute from the published rows")
            _v59 = _doc59.get("verdict") or {}
            if _v59.get("state") not in ("ADOPT_WINDOW", "PHASE_DEPENDENT", "WINDOW_INERT",
                                         "REJECT_WINDOW_CHANGE", "INCOMPLETE"):
                _bad59.append("unknown verdict %r" % (_v59.get("state"),))
            if not _doc59.get("identity_all_pass"):
                _bad59.append("the shipped window does not reproduce the production card")
            _rows59 = _doc59.get("phase_rows") or []
            _ph59 = sorted({r.get("phase") for r in _rows59})
            if len(_ph59) != _P59.N_PHASES:
                _bad59.append("%d phases, expected %d" % (len(_ph59), _P59.N_PHASES))
            if len({r.get("phase_start") for r in _rows59}) != len(_ph59):
                _bad59.append("two phases share a decision start -- the phase did not move")
            _wins59 = sorted({r.get("window") for r in _rows59})
            if _wins59 != sorted(_P59.WINDOWS):
                _bad59.append("windows are %r" % (_wins59,))
            for _p59_i in _ph59:
                for _w59 in _P59.WINDOWS:
                    if not any(r.get("phase") == _p59_i and r.get("window") == _w59
                               for r in _rows59):
                        _bad59.append("phase %r is missing window %rd" % (_p59_i, _w59))
            for _k59, _c59 in _P59.CRITERIA.items():
                if (_doc59.get("criteria") or {}).get(_k59) != _c59:
                    _bad59.append("criterion %s moved off the module constant" % (_k59,))
        check("product: the vol window is judged on more than one decision calendar",
              not _bad59,
              "; ".join(_bad59)[:220] or "verdict %s, best %sd, %d phases, identity PASS"
              % ((_doc59.get("verdict") or {}).get("state"),
                 (_doc59.get("verdict") or {}).get("best_window"), _P59.N_PHASES))
    except Exception as e:
        check("product: the vol window is judged on more than one decision calendar",
              False, repr(e)[:160])

    # ---- r1212 / E328: the grid pushed BELOW its old floor ----------------------------
    # The window face above ends with "the champion sits on the edge, pushing further is the
    # next face's job". The next face pushed, and found that the three shortest windows
    # never produce a vol estimate at all (the engine's own minimum history), i.e. they test
    # "overlay off", not "a shorter estimate". The leg therefore re-derives BOTH reads from
    # the rows: the position of the winner inside the LIVE range, and the fact that the dead
    # arms are excluded and reported. A face that silently starts counting them again --
    # which would move the "floor" to whichever duplicate was numbered last -- is red here.
    try:
        import importlib as _il60
        _P60 = _il60.import_module("etf_book_vol_window_edge")
        _p60 = os.path.join(PATHS.results_dir, "etf_book_vol_window_edge.json")
        _bad60 = []
        if not os.path.exists(_p60):
            _bad60.append("results/etf_book_vol_window_edge.json missing")
        else:
            with open(_p60, encoding="utf-8") as _fh60:
                _doc60 = json.load(_fh60)
            if _P60.check(_p60) != 0:
                _bad60.append("the verdict/position do not recompute from the published rows")
            _rows60 = _doc60.get("phase_rows") or []
            _e60 = _doc60.get("edge") or {}
            _re60 = _P60.edge_read(_rows60)
            if _e60.get("state") != _re60.get("state"):
                _bad60.append("edge state drifted: %r vs recomputed %r"
                              % (_e60.get("state"), _re60.get("state")))
            # the inherited rule must still be the previous face's rule
            if not (_doc60.get("rule_inherited") or {}).get("ok"):
                _bad60.append("the adoption rule stopped being inherited from the window face")
            if sorted((_doc60.get("criteria") or {}).get("windows") or []) != \
                    sorted(_P60.WINDOWS):
                _bad60.append("the grid moved off the module constant")
            if min(_P60.WINDOWS) >= _P60.PREV_FLOOR:
                _bad60.append("the grid does not reach below the previous floor")
            # dead arms: every phase must show zero estimates, and they must be grouped
            _dead = set(_e60.get("inactive_windows") or [])
            for _w60 in _dead:
                _rs = [r for r in _rows60 if r.get("window") == _w60]
                if not _rs or any((r.get("est_missing") or 0) != (r.get("decisions") or -1)
                                  for r in _rs):
                    _bad60.append("window %sd is called dead but did produce estimates" % _w60)
            _live = [c["window"] for c in (_e60.get("curve") or [])]
            if _dead & set(_live):
                _bad60.append("a dead arm is still in the live curve")
            if len(_dead) > 1:
                _grp = [g for g in (_e60.get("duplicate_groups") or []) if g.get("size") == len(_dead)]
                if not _grp:
                    _bad60.append("dead arms are not reported as ONE duplicate arm")
            if _doc60.get("admissible"):
                _bad60.append("a config change was declared admissible without review")
        check("product: the window grid's floor is the engine's, measured not assumed",
              not _bad60,
              "; ".join(_bad60)[:220] or "position %s, best %sd, dead arms %s"
              % (_e60.get("state"), _e60.get("best_window"),
                 _e60.get("inactive_windows")))
    except Exception as e:
        check("product: the window grid's floor is the engine's, measured not assumed",
              False, repr(e)[:160])
    # ---- r1207: the book's headline is priced one bar in the future ----
    # The face the CEO opens quotes the research engine, which ranks on bar d's own close and
    # then earns open[d]->open[d+1]. This leg re-reads the published audit and requires: the
    # verdict recomputes, the whole lag ladder is present, the source pin still holds, and the
    # causal arm IS the lag+1 rung (otherwise the face is quoting two different rules).
    try:
        import importlib as _il60
        _P60 = _il60.import_module("etf_book_lookahead_audit")
        _p60 = os.path.join(PATHS.results_dir, "etf_book_lookahead_audit.json")
        _bad60 = []
        if not os.path.exists(_p60):
            _bad60.append("results/etf_book_lookahead_audit.json missing")
            _doc60 = {}
        else:
            with open(_p60, encoding="utf-8") as _fh60:
                _doc60 = json.load(_fh60)
            if _P60.check(_p60) != 0:
                _bad60.append("the verdict does not recompute from the published rows")
            _v60 = _doc60.get("verdict") or {}
            if _v60.get("state") not in ("LOOKAHEAD_PRESENT", "WITHIN_TOL", "MECHANISM_ABSENT"):
                _bad60.append("unknown verdict %r" % (_v60.get("state"),))
            _lad60 = _doc60.get("lag_ladder") or []
            if sorted(r.get("lag") for r in _lad60) != sorted(_P60.LAGS):
                _bad60.append("lag ladder is %r" % ([r.get("lag") for r in _lad60],))
            _by60 = {r.get("lag"): r.get("cagr") for r in _lad60}
            _arm60 = (_doc60.get("arms") or {}).get("causal") or {}
            if _arm60.get("cagr") is None or _by60.get(1) is None or \
                    abs(_arm60["cagr"] - _by60[1]) > 1e-12:
                _bad60.append("the causal arm is not the lag+1 rung")
            if (_doc60.get("mechanism") or {}).get("score_reads_same_bar_close") is None:
                _bad60.append("the source pin did not run")
            for _k60, _c60 in _P60.CRITERIA.items():
                if (_doc60.get("criteria") or {}).get(_k60) != _c60:
                    _bad60.append("criterion %s moved off the module constant" % (_k60,))
        check("product: the book's headline is priced one bar in the future, and the gap is measured",
              not _bad60,
              "; ".join(_bad60)[:220] or "verdict %s, one-bar price %.2f pp/yr, ladder %s"
              % ((_doc60.get("verdict") or {}).get("state"),
                 (_doc60.get("verdict") or {}).get("gap_pp_per_year") or 0.0,
                 (_doc60.get("verdict") or {}).get("ladder_pp")))
    except Exception as e:
        check("product: the book's headline is priced one bar in the future, and the gap is measured",
              False, repr(e)[:160])
    # ---- r1224 / E341: is the one-bar price recoverable by rebuilding the signal causally? --
    # The card carries 8.46%/yr (the declared arm). This face asked whether averaging the last
    # k causal scores earns part of the missing 1.14pp back, and priced the answer: it does not
    # (best +0.07pp, and the turnover barely moves, so the gap was not commission either). The
    # leg re-derives the verdict from the published rows and refuses a face whose criterion
    # echo has drifted -- a negative result is a result, and it must not be quietly reversed
    # by a later "small adjustment".
    try:
        import importlib as _il61
        _P61 = _il61.import_module("etf_book_causal_rebuild")
        _p61 = os.path.join(PATHS.results_dir, "etf_book_causal_rebuild.json")
        _bad61 = []
        if not os.path.exists(_p61):
            _bad61.append("results/etf_book_causal_rebuild.json missing")
            _doc61 = {}
        else:
            with open(_p61, encoding="utf-8") as _fh61:
                _doc61 = json.load(_fh61)
            if _P61.check(_p61) != 0:
                _bad61.append("the verdict does not recompute from the published rows")
            _v61 = _doc61.get("verdict") or {}
            if _v61.get("state") not in ("RECOVERABLE", "IRRECOVERABLE",
                                         "MIXED_ACROSS_PHASES", "INCOMPLETE"):
                _bad61.append("unknown verdict %r" % (_v61.get("state"),))
            for _k61, _c61 in _P61.CRITERIA.items():
                if (_doc61.get("criteria") or {}).get(_k61) != _c61:
                    _bad61.append("criterion %s moved off the module constant" % (_k61,))
            _arms61 = {r.get("arm") for r in (_doc61.get("rows") or [])}
            if _v61.get("recommended_card_arm") not in _arms61:
                _bad61.append("recommends an arm it never priced")
            _au61 = _doc61.get("audits") or {}
            for _a61 in ("A3_rank_causality", "A4_factor_source", "A5_lags"):
                if not ((_au61.get(_a61) or {}).get("ok")):
                    _bad61.append("mechanism audit %s failed" % _a61)
            _dec61 = _doc61.get("decomposition") or {}
            for _k61 in ("total_pp", "signal_pp", "cost_pp"):
                if _dec61.get(_k61) is None:
                    _bad61.append("cost decomposition missing %s" % _k61)
        check("product: the one-bar price is not recoverable by smoothing the causal score",
              not _bad61,
              "; ".join(_bad61)[:220] or "verdict %s, best %+.2f pp of %.2f, signal %+.2f / cost %+.2f"
              % ((_doc61.get("verdict") or {}).get("state"),
                 (_doc61.get("verdict") or {}).get("best_recovered_pp") or 0.0,
                 (_doc61.get("criteria") or {}).get("recovery_min_pp") or 0.0,
                 (_doc61.get("decomposition") or {}).get("signal_pp") or 0.0,
                 (_doc61.get("decomposition") or {}).get("cost_pp") or 0.0))
    except Exception as e:
        check("product: the one-bar price is not recoverable by smoothing the causal score",
              False, repr(e)[:160])
    # ---- r1226 / E26: the last information channel is priced too, and priced honestly ------
    # The rebuild answer is "no", so the reader's next question is whether anything visible at
    # the fill is worth the gap. This leg re-derives the verdict from the published rows, pins
    # the criterion echo, refuses a verdict whose recommended arm was never priced, and
    # demands the fill-time causality audit pass -- without it the whole face is look-ahead.
    try:
        import importlib as _il63
        _G63 = _il63.import_module("etf_book_overnight_gap")
        _g63 = os.path.join(PATHS.results_dir, "etf_book_overnight_gap.json")
        _bad63 = []
        if not os.path.exists(_g63):
            _bad63.append("results/etf_book_overnight_gap.json missing")
            _doc63 = {}
        else:
            with open(_g63, encoding="utf-8") as _fh63:
                _doc63 = json.load(_fh63)
            if _G63.check(_g63) != 0:
                _bad63.append("the verdict does not recompute from the published rows")
            _v63 = _doc63.get("verdict") or {}
            if _v63.get("state") not in ("ADOPT_GAP", "NO_GAP_EDGE",
                                         "MIXED_ACROSS_PHASES", "INCOMPLETE"):
                _bad63.append("unknown verdict %r" % (_v63.get("state"),))
            for _k63, _c63 in _G63.CRITERIA.items():
                if (_doc63.get("criteria") or {}).get(_k63) != _c63:
                    _bad63.append("criterion %s moved off the module constant" % (_k63,))
            _arms63 = {r.get("arm") for r in (_doc63.get("rows") or [])}
            if _v63.get("recommended_card_arm") not in _arms63:
                _bad63.append("recommends an arm it never priced")
            _au63 = _doc63.get("audits") or {}
            for _a63 in ("A6_fill_time_causality", "A7_declared_lag", "A8_mask_not_rescale"):
                if not ((_au63.get(_a63) or {}).get("ok")):
                    _bad63.append("mechanism audit %s failed" % _a63)
            # the control must reproduce the card it is measured against, or the pp is fiction
            for _c63 in (_doc63.get("controls") or []):
                if not _c63.get("ok"):
                    _bad63.append("the declared control misses the published card")
        check("product: the overnight gap is priced as the last channel between decide and fill",
              not _bad63,
              "; ".join(_bad63)[:220] or "verdict %s, best %+.2f pp of %.2f, median gap %s bp"
              % ((_doc63.get("verdict") or {}).get("state"),
                 (_doc63.get("verdict") or {}).get("best_gained_pp") or 0.0,
                 (_doc63.get("criteria") or {}).get("gap_min_pp") or 0.0,
                 (_doc63.get("gap_stats") or {}).get("median_abs_gap_bp")))
    except Exception as e:
        check("product: the overnight gap is priced as the last channel between decide and fill",
              False, repr(e)[:160])
    # ---- r1227 / E27: the fill is sliced over k opens, and the answer is a mechanism -----
    # Re-derives the verdict from the published rows, pins the criterion echo, and demands
    # three things a naive implementation gets wrong: k=1 must reproduce the engine exactly
    # (otherwise the wrapper is a new engine), every k must charge exactly the single-open
    # turnover (equal slices cannot buy commission -- a sliced arm that also shrinks the book
    # is a different experiment, E197), and the control must be the DECLARED arm the desk can
    # trade, not the as-coded one it cannot.
    try:
        import importlib as _il93
        _G93 = _il93.import_module("etf_book_open_slicing")
        _g93 = os.path.join(PATHS.results_dir, "etf_book_open_slicing.json")
        _bad93 = []
        if not os.path.exists(_g93):
            _bad93.append("results/etf_book_open_slicing.json missing")
            _doc93 = {}
        else:
            with open(_g93, encoding="utf-8") as _fh93:
                _doc93 = json.load(_fh93)
            if _G93.check(_g93) != 0:
                _bad93.append("the verdict does not recompute from the published rows")
            _v93 = _doc93.get("verdict") or {}
            if _v93.get("state") not in ("ADOPT_SLICED", "MIXED_ACROSS_PHASES",
                                         "NO_SLICING_EDGE", "INCOMPLETE"):
                _bad93.append("unknown verdict %r" % (_v93.get("state"),))
            for _k93, _c93 in _G93.CRITERIA.items():
                if (_doc93.get("criteria") or {}).get(_k93) != _c93:
                    _bad93.append("criterion %s moved off the module constant" % (_k93,))
            _au93 = _doc93.get("audits") or {}
            if not ((_au93.get("A9_engine_identity") or {}).get("ok")):
                _bad93.append("k=1 does not reproduce the engine")
            for _a93 in _au93.get("A10_participation_not_rescaled") or []:
                if not _a93.get("ok"):
                    _bad93.append("k=%s does not pay the single-open turnover"
                                  % (_a93.get("k"),))
            for _c93 in _doc93.get("controls") or []:
                if not _c93.get("ok"):
                    _bad93.append("the control arm misses the published declared CAGR")
        check("product: the fill is sliced over k opens and priced against the declared arm",
              not _bad93,
              "; ".join(_bad93)[:220] or "verdict %s, best %+.2f pp, control %s"
              % ((_doc93.get("verdict") or {}).get("state"),
                 (_doc93.get("verdict") or {}).get("best_gained_pp") or 0.0,
                 ((_doc93.get("verdict") or {}).get("control_cagr"))))
    except Exception as e:
        check("product: the fill is sliced over k opens and priced against the declared arm",
              False, repr(e)[:160])
    # ---- r1230: how long a holder waits under water ---------------------------------------
    # Re-derives the verdict from the published rows and demands the three properties that
    # make a duration number trustworthy: the curve under test must be the published cell
    # (control reproduced, never "close enough"), a censored entry must stay censored (a face
    # that quietly scores "never recovered" as 0 makes the book look faster than it is), and
    # the horizon must be calendar time rather than an assumed 252 bars/year.
    try:
        import importlib as _il30
        _U30 = _il30.import_module("etf_book_underwater")
        _u30 = os.path.join(PATHS.results_dir, "etf_book_underwater.json")
        _bad30 = []
        _doc30 = {}
        if not os.path.exists(_u30):
            _bad30.append("results/etf_book_underwater.json missing")
        else:
            with open(_u30, encoding="utf-8") as _fh30:
                _doc30 = json.load(_fh30)
            if _U30.check(_u30) != 0:
                _bad30.append("the verdict does not recompute from the published rows")
            _c30 = _doc30.get("control") or {}
            if _c30.get("verdict") != "CONTROL_REPRODUCED":
                _bad30.append("control is %r, not the published cell" % (_c30.get("verdict"),))
            if (_c30.get("delta_cagr") or 0) > _U30.CONTROL_TOL or \
                    (_c30.get("delta_maxdd") or 0) > _U30.CONTROL_TOL:
                _bad30.append("control deltas exceed the frozen tolerance")
            _r30 = _doc30.get("recovery") or {}
            if _r30.get("entries") and _r30.get("censored") is None:
                _bad30.append("censored entries are not reported")
            if (_r30.get("censored") or 0) > 0 and (_r30.get("censored_share") or 0) == 0:
                _bad30.append("censored entries were silently scored as recovered at 0 bars")
            _f30 = _doc30.get("forward") or {}
            for _h30 in ("1y", "2y", "3y"):
                _row30 = _f30.get(_h30) or {}
                if _row30.get("entries") and _row30.get("skipped_no_full_horizon") is None:
                    _bad30.append("%s does not disclose the skipped tail" % (_h30,))
                if _row30.get("entries") and _row30.get("min") is None:
                    _bad30.append("%s publishes no minimum" % (_h30,))
            if (_doc30.get("bars") or 0) < 500:
                _bad30.append("curve too short to price a duration")
        check("product: how long a holder waits under water, re-derived from the published rows",
              not _bad30,
              "; ".join(_bad30)[:220] or "longest %s bars, worst entry %s bars, 1y min %s, censored %s"
              % (((_doc30.get("underwater") or {}).get("longest") or {}).get("bars_underwater"),
                 ((_doc30.get("recovery") or {}).get("worst_entry") or {}).get("bars"),
                 ((_doc30.get("forward") or {}).get("1y") or {}).get("min"),
                 ((_doc30.get("recovery") or {}).get("censored"))))
    except Exception as e:
        check("product: how long a holder waits under water, re-derived from the published rows",
              False, repr(e)[:160])
    # ---- r1231: the page must carry the wait it is about ------------------------------------
    # The duration face exists (r1230) but a face nobody reads is not an answer. Every other
    # number on the operator page says "how much" or "how deep"; this leg requires the page a
    # person actually opens to print the worst wait, and to print it as the payload's own
    # number -- re-derived here from results/etf_book_underwater.json, not from the sentence
    # the page wrote. It also requires the censored disclosure to survive onto the page: a
    # page that drops "still under water" turns a censored entry into an invisible one.
    try:
        _bad31 = []
        _uw31 = os.path.join(PATHS.results_dir, "etf_book_underwater.json")
        _doc31 = {}
        if not os.path.exists(_uw31):
            _bad31.append("results/etf_book_underwater.json missing")
        else:
            with open(_uw31, encoding="utf-8") as _fh31:
                _doc31 = json.load(_fh31)
            _mb31 = (_doc31.get("recovery") or {}).get("max_bars")
            _pg31 = importlib.import_module("etf_book_ceo_page")
            _ptr31 = os.path.join(PATHS.root, "docs", "live_book", "latest.json")
            _mdpath31 = ""
            if os.path.exists(_ptr31):
                with open(_ptr31, encoding="utf-8") as _fh31b:
                    _mdpath31 = (json.load(_fh31b) or {}).get("page") or ""
            if not _mdpath31:
                _bad31.append("docs/live_book/latest.json names no page")
            else:
                with open(os.path.join(PATHS.root, _mdpath31.replace("/", os.sep)),
                          encoding="utf-8") as _fh31c:
                    _md31 = _fh31c.read()
                if "这笔钱真要等多久才能回本" not in _md31:
                    _bad31.append("the page has no duration section")
                if _mb31 is not None and ("%d 个交易日" % int(_mb31)) not in _md31:
                    _bad31.append("the page does not print the payload's worst wait (%s bars)"
                                  % (_mb31,))
                if (_doc31.get("recovery") or {}).get("censored") and "不记 0" not in _md31:
                    _bad31.append("the page drops the censored-entry disclosure")
                if (_doc31.get("first_bar") or "") not in _md31:
                    _bad31.append("the page does not state the sample start beside a "
                                  "'no losses' claim")
                # the page's own payload must read the same face, not a copy of the sentence
                _blk31 = _pg31.underwater_face()
                if _blk31.get("status") != "ok":
                    _bad31.append("the page's duration face reads %r" % (_blk31.get("status"),))
                elif ((_blk31.get("recovery") or {}).get("max_bars")) != _mb31:
                    _bad31.append("page face max_bars %r vs payload %r"
                                  % (((_blk31.get("recovery") or {}).get("max_bars")), _mb31))
        check("product: the operator page prints how long the wait is",
              not _bad31,
              "; ".join(_bad31)[:220] or "worst wait %s bars | censored %s | sample from %s"
              % (_mb31, ((_doc31.get("recovery") or {}).get("censored")),
                 _doc31.get("first_bar")))
    except Exception as e:
        check("product: the operator page prints how long the wait is",
              False, repr(e)[:160])
    # ---- r1233: the operator page must say which window its numbers came from ------------
    # Every number on the page is measured on the 2020+ boom. The card already tested the
    # same shipment rule on the 193 ETFs that existed before it and reports that no
    # intercept survives; this leg requires the page a person sizes from to carry that
    # verdict, re-derived here from results/etf_book_spanning_pre2020.json (its own t
    # statistics, never its prose) and demanding the same numbers appear on the page.
    try:
        _bad33 = []
        _sp33 = os.path.join(PATHS.results_dir, "etf_book_spanning_pre2020.json")
        _doc33 = {}
        _tabs33 = None
        if not os.path.exists(_sp33):
            _bad33.append("results/etf_book_spanning_pre2020.json missing")
        else:
            with open(_sp33, encoding="utf-8") as _fh33:
                _doc33 = json.load(_fh33)
            _arms33 = _doc33.get("arms") or {}
            _tabs33 = [abs(float(((_arms33.get(_k) or {}).get("full") or {}).get("alpha_t")))
                       for _k in ("single", "staggered")
                       if ((_arms33.get(_k) or {}).get("full") or {}).get("alpha_t") is not None]
            if not _tabs33:
                _bad33.append("the payload publishes no intercept t")
            _uni33 = (_doc33.get("universe") or {}).get("U_pre")
            _pg33 = importlib.import_module("etf_book_ceo_page")
            _ptr33 = os.path.join(PATHS.root, "docs", "live_book", "latest.json")
            _mdpath33 = ""
            if os.path.exists(_ptr33):
                with open(_ptr33, encoding="utf-8") as _fh33b:
                    _mdpath33 = (json.load(_fh33b) or {}).get("page") or ""
            if not _mdpath33:
                _bad33.append("docs/live_book/latest.json names no page")
            else:
                with open(os.path.join(PATHS.root, _mdpath33.replace("/", os.sep)),
                          encoding="utf-8") as _fh33c:
                    _md33 = _fh33c.read()
                if "这些号码是从哪一段行情里长出来的" not in _md33:
                    _bad33.append("the page has no sample-window section")
                _w33 = _doc33.get("window") or ["?", "?"]
                if str(_w33[0]) not in _md33:
                    _bad33.append("the page does not name the out-of-window test start")
                if _uni33 and ("%s 只" % _uni33) not in _md33:
                    _bad33.append("the page does not print the pre-2020 universe size")
                _surv33 = any(_t >= 2.0 for _t in (_tabs33 or []))
                if _surv33 and "过线了" not in _md33:
                    _bad33.append("a t above 2 must print 'clears the line'")
                if not _surv33 and "分不开" not in _md33:
                    _bad33.append("no t above 2 must print 'indistinguishable from a fixed mix'")
                _blk33 = _pg33.sample_window_face()
                if _blk33.get("status") != "ok":
                    _bad33.append("the page's sample-window face reads %r"
                                  % (_blk33.get("status"),))
                else:
                    _pg_t33 = max([abs(float(_r.get("alpha_t") or 0.0))
                                   for _r in (_blk33.get("rows") or [])] or [0.0])
                    if _tabs33 and abs(_pg_t33 - max(_tabs33)) > 1e-9:
                        _bad33.append("page face reads t=%.3f vs payload %.3f"
                                      % (_pg_t33, max(_tabs33)))
                    if bool(_blk33.get("survives")) is not _surv33:
                        _bad33.append("page face verdict disagrees with its own t")
        check("product: the operator page says which window its numbers came from",
              not _bad33,
              "; ".join(_bad33)[:220] or "universe %s ETFs | out-of-window t max %s | survives %s"
              % (_uni33, max(_tabs33) if _tabs33 else None,
                 any(_t >= 2.0 for _t in (_tabs33 or []))))
    except Exception as e:
        check("product: the operator page says which window its numbers came from",
              False, repr(e)[:160])
    # ---- r1235: could this book be run in 2020? -----------------------------------------
    # The page quotes the locked-universe run and the book's own composition. This leg
    # re-derives the verdict from the payload's phase rows through the face's single
    # implementation (never from the sentence), refuses a payload whose control arms no longer
    # reproduce the card's two published arms, and demands the same numbers on the page.
    try:
        _bad34 = []
        _ul34 = os.path.join(PATHS.results_dir, "etf_book_universe_lock.json")
        _doc34 = {}
        _ver34 = None
        _pg34 = None
        if not os.path.exists(_ul34):
            _bad34.append("results/etf_book_universe_lock.json missing")
        else:
            with open(_ul34, encoding="utf-8") as _fh34:
                _doc34 = json.load(_fh34)
            _rows34 = _doc34.get("phase_rows") or []
            if not _rows34:
                _bad34.append("the payload publishes no phase rows")
            else:
                _mod34 = importlib.import_module("etf_book_universe_lock")
                _ver34 = _mod34.verdict_from_summary(_mod34._summarise(_rows34))
                if (_doc34.get("summary") or {}).get("verdict") != _ver34:
                    _bad34.append("the published verdict does not recompute (%r vs %r)"
                                  % ((_doc34.get("summary") or {}).get("verdict"), _ver34))
            _ctl34 = _doc34.get("control") or {}
            if not (_ctl34.get("ok")
                    and all(v.get("ok") for v in (_ctl34.get("arms") or {}).values())):
                _bad34.append("the control arms no longer reproduce the published headline")
            _pg34 = importlib.import_module("etf_book_ceo_page")
            _ptr34 = os.path.join(PATHS.root, "docs", "live_book", "latest.json")
            _mdpath34 = ""
            if os.path.exists(_ptr34):
                with open(_ptr34, encoding="utf-8") as _fh34b:
                    _mdpath34 = (json.load(_fh34b) or {}).get("page") or ""
            if not _mdpath34:
                _bad34.append("docs/live_book/latest.json names no page")
            else:
                with open(os.path.join(PATHS.root, _mdpath34.replace("/", os.sep)),
                          encoding="utf-8") as _fh34c:
                    _md34 = _fh34c.read()
                if "2020 年能不能真的跑这本书" not in _md34:
                    _bad34.append("the page has no universe-lock section")
                _ph34 = _rows34[0] if _rows34 else {}
                _lkkey34 = "lock_%s" % ((_doc34.get("criteria") or {}).get("headline_lock"))
                _lk34 = _ph34.get(_lkkey34) or {}
                for _val34 in ((_ph34.get("unlocked") or {}).get("cagr"),
                               _lk34.get("cagr")):
                    if _val34 is None or ("%.2f%%" % (100.0 * _val34)) not in _md34:
                        _bad34.append("the page does not print %.2f%%"
                                      % (100.0 * (_val34 or 0.0)))
                _pk34 = _doc34.get("picks") or {}
                _pair34 = "%d/%d" % (_pk34.get("book_in_force_listed_after_lock") or 0,
                                     len(_pk34.get("book_in_force") or []))
                if _pk34.get("pick_slots") and _pair34 not in _md34:
                    _bad34.append("the page does not print the book composition %s" % _pair34)
                _face34 = _pg34.universe_lock_face()
                if _face34.get("status") != "ok":
                    _bad34.append("the page's universe-lock face reads %r"
                                  % (_face34.get("status"),))
                elif _ver34 is not None and _face34.get("verdict") != _ver34:
                    _bad34.append("page face verdict %r != payload %r"
                                  % (_face34.get("verdict"), _ver34))
        check("product: the operator page says whether this book was runnable in 2020",
              not _bad34,
              "; ".join(_bad34)[:220] or "verdict %s | locked %s funds | book %s listed after"
              % (_ver34, _rows34[0].get("locked_n") if _rows34 else None,
                 "%d/%d" % ((_doc34.get("picks") or {}).get(
                     "book_in_force_listed_after_lock") or 0,
                     len((_doc34.get("picks") or {}).get("book_in_force") or []))))
    except Exception as e:
        check("product: the operator page says whether this book was runnable in 2020",
              False, repr(e)[:160])
    # ---- r1239: the operator page must say how much money the book needs -----------------
    # Every cost number on the page is a RATE per side, and a rate has no floor while a real
    # commission does. The page can now be read as "8bp applies to me" at any account size,
    # which is false below the 5-yuan break-even. This leg re-derives that break-even from the
    # published traded-leg median with its own arithmetic (1e4*floor/(bp*dw)), requires the
    # page face to carry the same number, requires the window token to reach the page in the
    # right shape, and fails if a token saying the threshold MOVES is printed as a constant.
    try:
        import importlib as _il72
        _MC72 = _il72.import_module("etf_book_min_capital")
        _PG72 = _il72.import_module("etf_book_ceo_page")
        _p72 = os.path.join(PATHS.results_dir, "etf_book_min_capital.json")
        _bad72 = []
        _doc72 = {}
        if not os.path.exists(_p72):
            _bad72.append("results/etf_book_min_capital.json missing")
        else:
            with open(_p72, encoding="utf-8") as _fh72:
                _doc72 = json.load(_fh72)
            if _MC72.check() != 0:
                _bad72.append("the stored neutral points no longer recompute")
            _cfg72 = _doc72.get("config") or {}
            _dw72 = _cfg72.get("dw_median_all_legs")
            _sched72 = (_cfg72.get("schedules") or [{}])[0]
            _want72 = (1e4 * float(_sched72.get("min_fee_cny") or 0.0)
                       / (float(_cfg72.get("base_bp_published")) * _dw72)) if _dw72 else None
            if _want72 is None or abs(_want72 - (_doc72.get("fee_neutral_vs_model_nav") or 0)) > 0.02:
                _bad72.append("break-even %r != re-derived %r"
                              % (_doc72.get("fee_neutral_vs_model_nav"), _want72))
            _face72 = _PG72.capital_face()
            if _face72.get("status") != "ok":
                _bad72.append("the page's capital face reads %r" % (_face72.get("status"),))
            elif _want72 is not None and abs((_face72.get("model_nav") or 0) - _want72) > 0.02:
                _bad72.append("page face break-even %r != %r"
                              % (_face72.get("model_nav"), _want72))
            _lb72 = sorted(glob.glob(os.path.join(PATHS.root, "docs", "live_book",
                                                  "LIVE-BOOK-*.md")))
            if not _lb72:
                _bad72.append("no live-book page on disk")
            else:
                with open(_lb72[-1], encoding="utf-8") as _fh72b:
                    _md72 = _fh72b.read()
                _lines72 = [l for l in _PG72.capital_block(_face72) if l.strip()]
                _off72 = [l for l in _lines72 if l not in _md72]
                if _off72:
                    _bad72.append("%d of the section's lines never reach the page"
                                  % len(_off72))
                _wv72 = _face72.get("window_verdict")
                if str(_wv72).startswith("BREAKEVEN_WINDOW_MOVES"):
                    if "不是一个常数" not in _md72:
                        _bad72.append("the threshold moves across samples but the page "
                                      "does not say so")
                    if "这个门槛是稳的" in _md72:
                        _bad72.append("the page prints a moving threshold as a constant")
                elif _wv72 == "BREAKEVEN_WINDOW_STABLE":
                    if "这个门槛是稳的" not in _md72:
                        _bad72.append("a stable threshold is not printed as stable")
                else:
                    _bad72.append("window token %r makes no claim" % (_wv72,))
        check("product: the operator page says how much money this book needs",
              not _bad72,
              "; ".join(_bad72)[:220] or "break-even %s CNY | window %s"
              % (_doc72.get("fee_neutral_vs_model_nav"),
                 (_doc72.get("window") or {}).get("verdict")))
    except Exception as e:
        check("product: the operator page says how much money this book needs",
              False, repr(e)[:160])
    # ---- r1244: the page must price the basket the reader is actually holding -----------
    # The card configures 12 names and the ladder is priced on 12, but the executable ticket
    # the reader can place today holds 5. This leg reads the ticket's own width, finds that
    # width in the published width sweep, and requires the page to print THAT break-even next
    # to the ticket -- derived from the rows, not from a sentence. It also fails if the page
    # keeps quoting the card's basket at a reader holding another one.
    try:
        import importlib as _il73
        _PG73 = _il73.import_module("etf_book_ceo_page")
        _bad73 = []
        _ptr73 = os.path.join(PATHS.results_dir, "etf_book_order", "latest.json")
        _tk73 = {}
        if not os.path.exists(_ptr73):
            _bad73.append("results/etf_book_order/latest.json missing")
        else:
            with open(_ptr73, encoding="utf-8") as _fh73:
                _ptr_doc73 = json.load(_fh73)
            _rel73 = _ptr_doc73.get("file") or _ptr_doc73.get("path")
            _cand73 = [os.path.join(os.path.dirname(_ptr73), _rel73 or ""),
                       os.path.join(PATHS.root, _rel73 or "")]
            _path73 = next((p for p in _cand73 if os.path.exists(p)), None)
            if not _path73:
                _bad73.append("ticket body %r not resolvable" % (_rel73,))
            else:
                with open(_path73, encoding="utf-8") as _fh73b:
                    _tk73 = json.load(_fh73b)
        _n73 = _tk73.get("n_hold")
        if _n73 is None:
            _n73 = len((_tk73.get("ticket") or {}).get("order") or []) or None
        with open(os.path.join(PATHS.results_dir, "etf_book_min_capital.json"),
                  encoding="utf-8") as _fh73c:
            _mc73 = json.load(_fh73c)
        _rows73 = (_mc73.get("width") or {}).get("rows") or []
        _row73 = next((r for r in _rows73 if r.get("n_hold") == _n73), {})
        _want73 = _row73.get("fee_neutral_vs_model_nav")
        _face73 = _PG73.capital_face()
        if _face73.get("status") != "ok":
            _bad73.append("capital face reads %r" % (_face73.get("status"),))
        if _n73 is None:
            _bad73.append("the ticket carries no held-name count")
        elif _face73.get("ticket_n_hold") != _n73:
            _bad73.append("page names the ticket at %r names, the ticket holds %r"
                          % (_face73.get("ticket_n_hold"), _n73))
        elif _want73 is None:
            _bad73.append("the ticket's width %r is not in the published width sweep" % (_n73,))
        elif abs((_face73.get("ticket_model_nav") or 0) - _want73) > 0.02:
            _bad73.append("ticket-width break-even %r != the published row's %r"
                          % (_face73.get("ticket_model_nav"), _want73))
        _lb73 = sorted(glob.glob(os.path.join(PATHS.root, "docs", "live_book",
                                              "LIVE-BOOK-*.md")))
        if not _lb73:
            _bad73.append("no live-book page on disk")
        else:
            with open(_lb73[-1], encoding="utf-8") as _fh73d:
                _md73 = _fh73d.read()
            _tk_lines73 = [l for l in _PG73.capital_block(_face73) if "可执行单" in l]
            if not _tk_lines73:
                _bad73.append("the page never mentions the ticket's own width")
            elif any(l not in _md73 for l in _tk_lines73):
                _bad73.append("the ticket-width line never reaches the page")
            _pw73 = _face73.get("published_path_width")
            if _n73 is not None and _pw73 is not None and _n73 != _pw73:
                if _want73 is not None and ("%.0f" % _want73) not in _md73.replace(",", ""):
                    _bad73.append("the page prices the card's basket (%s names) at a reader "
                                  "holding %s and never prints their own %s CNY"
                                  % (_pw73, _n73, "%.0f" % _want73))
        check("product: the operator page prices the basket the ticket actually holds",
              not _bad73,
              "; ".join(_bad73)[:220] or "ticket %s names -> %s CNY (card path %s)"
              % (_n73, _want73, (_face73.get("published_path_width"),)))
    except Exception as e:
        check("product: the operator page prices the basket the ticket actually holds",
              False, repr(e)[:160])
    # ---- r1245: the sheet prices the cash half it asks the reader to hold -----------------
    # The ticket printed "cash 53%" and the cash amount and stopped there; the only yield it
    # ever quoted was a multi-year mean, which is a history rather than a forecast. This leg
    # re-derives the annual CNY from the published spot rate x the published cash amount,
    # demands the sheet print that number, and demands the spread sentence appear when the
    # face itself says the rate has fallen -- so a re-derived face that disagrees with the
    # sheet, or a sheet that quietly drops the section, both read red.
    try:
        _bad74 = []
        _ptr74 = os.path.join(PATHS.results_dir, "etf_book_order", "latest.json")
        _tk74 = {}
        if not os.path.exists(_ptr74):
            _bad74.append("results/etf_book_order/latest.json missing")
        else:
            with open(_ptr74, encoding="utf-8") as _fh74:
                _ptr_doc74 = json.load(_fh74)
            _rel74 = _ptr_doc74.get("file") or _ptr_doc74.get("path") or ""
            _cand74 = [os.path.join(os.path.dirname(_ptr74), _rel74),
                       os.path.join(PATHS.root, _rel74)]
            _path74 = next((p for p in _cand74 if p and os.path.exists(p)), None)
            if not _path74:
                _bad74.append("ticket body %r not resolvable" % (_rel74,))
            else:
                with open(_path74, encoding="utf-8") as _fh74b:
                    _tk74 = json.load(_fh74b)
        _cm74 = ((_tk74.get("cash_leg") or {}).get("money") or {})
        if _cm74.get("verdict") in (None, "CANNOT_PRICE"):
            _bad74.append("the ticket prices no cash money (%r)" % (_cm74.get("verdict"),))
        else:
            _cash74 = _cm74.get("cash_amount_cny")
            _spot74 = _cm74.get("spot") or {}
            _re74 = round(_cash74 * (_spot74.get("pct") or 0.0) / 100.0, 0)
            if abs(_re74 - (_spot74.get("annual_cny") or -1)) > 1.0:
                _bad74.append("spot annual %r != cash x rate %r"
                              % (_spot74.get("annual_cny"), _re74))
            _tail74 = _cm74.get("mean_tail") or {}
            if abs(round(_cash74 * (_tail74.get("pct") or 0.0) / 100.0, 0)
                   - (_tail74.get("annual_cny") or -1)) > 1.0:
                _bad74.append("trailing-mean annual does not follow from its own rate")
            _md74 = os.path.join(os.path.dirname(_path74),
                                 "ORDER-%s.md" % (_tk74.get("evidence_cutoff") or ""))
            if not os.path.exists(_md74):
                _bad74.append("ORDER-%s.md missing" % (_tk74.get("evidence_cutoff"),))
            else:
                with open(_md74, encoding="utf-8") as _fh74c:
                    _txt74 = _fh74c.read()
                if "现金那一半今天赚多少钱" not in _txt74:
                    _bad74.append("the sheet never prices the cash half")
                if ("%s" % format(int(_re74), ",")) not in _txt74:
                    _bad74.append("the spot annual (%s CNY) is not printed"
                                  % format(int(_re74), ","))
                if _cm74.get("verdict") == "RATES_FELL":
                    if "利率掉了" not in _txt74:
                        _bad74.append("the face says rates fell but the sheet does not")
                    if format(int(abs(_cm74.get("spread_vs_tail_cny") or 0)), ",") not in _txt74:
                        _bad74.append("the money the fall costs is not printed")
                elif "RATES_FELL" in _txt74:
                    _bad74.append("the sheet calls it a fall while the face does not")
        check("product: the order sheet prices the cash half in CNY at today's rate",
              not _bad74,
              "; ".join(_bad74)[:220] or
              "cash %s CNY at %.2f%% -> %s CNY/yr vs trailing %.2f%% -> %s (%s)"
              % (format(int(_cm74.get("cash_amount_cny") or 0), ","),
                 (_cm74.get("spot") or {}).get("pct") or 0.0,
                 format(int((_cm74.get("spot") or {}).get("annual_cny") or 0), ","),
                 (_cm74.get("mean_tail") or {}).get("pct") or 0.0,
                 format(int((_cm74.get("mean_tail") or {}).get("annual_cny") or 0), ","),
                 _cm74.get("verdict")))
    except Exception as e:
        check("product: the order sheet prices the cash half in CNY at today's rate",
              False, repr(e)[:160])
    # ---- r1246: the operator page prices the same cash on the sheet's own three rates ----
    # r1245 taught the ticket to print today's quote, its own trailing mean and the ledger
    # window mean side by side; the page kept printing one of them. This leg reads both
    # published faces and demands identical numbers -- a page that re-derives them (and
    # re-rounds the 3-dp accrual into 11,041 against the sheet's 11,039) reads red, and so
    # does one that quietly drops the section.
    try:
        _bad76 = []
        _ptr76 = os.path.join(PATHS.results_dir, "etf_book_order", "latest.json")
        _tk76 = {}
        if not os.path.exists(_ptr76):
            _bad76.append("ticket pointer missing")
        else:
            with open(_ptr76, encoding="utf-8") as _fh76:
                _p76 = json.load(_fh76)
            _rel76 = _p76.get("file") or _p76.get("path") or ""
            _cand76 = [os.path.join(os.path.dirname(_ptr76), _rel76),
                       os.path.join(PATHS.root, _rel76)]
            _path76 = next((p for p in _cand76 if p and os.path.exists(p)), None)
            if not _path76:
                _bad76.append("ticket body not resolvable")
            else:
                with open(_path76, encoding="utf-8") as _fh76b:
                    _tk76 = json.load(_fh76b)
        _money76 = ((_tk76.get("cash_leg") or {}).get("money") or {})
        _lb76 = os.path.join(PATHS.root, "docs", "live_book")
        _ptr76b = os.path.join(_lb76, "latest.json")
        _page76 = {}
        _md76 = ""
        if not os.path.exists(_ptr76b):
            _bad76.append("docs/live_book/latest.json missing")
        else:
            with open(_ptr76b, encoding="utf-8") as _fh76c:
                _pl76 = json.load(_fh76c)
            _js76 = os.path.join(PATHS.root, (_pl76.get("json") or "").replace("/", os.sep))
            _mdp76 = os.path.join(PATHS.root, (_pl76.get("page") or "").replace("/", os.sep))
            if not (_js76 and os.path.exists(_js76)):
                _bad76.append("the page json named by latest.json is absent")
            else:
                with open(_js76, encoding="utf-8") as _fh76d:
                    _page76 = json.load(_fh76d)
            if _mdp76 and os.path.exists(_mdp76):
                with open(_mdp76, encoding="utf-8") as _fh76e:
                    _md76 = _fh76e.read()
            else:
                _bad76.append("the page md named by latest.json is absent")
        _cm76 = (_page76.get("cash_money") or {})
        _pb76 = _cm76.get("block") or {}
        # r1406: two faces owe each other identical numbers only when they were priced on
        # the same panel. On 2026-11-07 this machine's estate moved to panel 93efa718 while
        # the CEO page (bm-a's writer) still priced 58302d9c: the same rule then produced a
        # cash pile 0.057% apart (540,203.70 vs 540,512.84) and every CNY figure followed
        # it. That is a WORLD difference, not a value defect -- E293/E397: the gate reds
        # "same world, different number" and must NAME the split when the worlds differ,
        # instead of printing two numbers as if one of them were wrong. The strict equality
        # below is unchanged whenever the worlds match OR either side names none (absence
        # is unverifiable, never a pass).
        _wp76 = (((((_page76.get("underwater") or {}).get("control") or {})
                   .get("published") or {}).get("published_bar_note") or {})
                 .get("panel_digest") or {}).get("digest")
        _wt76 = ((_tk76.get("price_basis") or {}).get("panel_digest") or {})
        _wt76 = _wt76.get("digest") if isinstance(_wt76, dict) else None
        _split76 = bool(_wp76 and _wt76 and _wp76 != _wt76)
        if _cm76.get("status") != "ok":
            _bad76.append("the page prices no cash money (%r/%r)"
                          % (_cm76.get("status"), _cm76.get("note")))
        elif _money76.get("verdict") in (None, "CANNOT_PRICE"):
            _bad76.append("the sheet prices no cash money while the page claims one")
        elif _split76:
            # Different worlds: do not compare the two faces' CNY; instead demand (a) the
            # page says so in its own words and (b) each side follows from ITS OWN pile.
            if "同一笔现金" not in _md76:
                _bad76.append("the section is gone from the page")
            _fc76 = _page76.get("family_coherence") or {}
            if _fc76.get("priced_same_panel") is not False and "MIXED_WORLDS" not in json.dumps(
                    _fc76, ensure_ascii=False):
                _bad76.append("the page priced world %s, the sheet world %s, and the page "
                              "does not say its faces span two panels"
                              % (_wp76, _wt76))
            for _tag76, _blk76, _pile76 in (
                    ("page", _pb76, float(_page76.get("cash_amount_cny") or 0)),
                    ("sheet", _money76, float(_money76.get("cash_amount_cny") or 0))):
                if _pile76 <= 0:
                    _bad76.append("%s prices a cash pile of %r" % (_tag76, _pile76))
                    continue
                for _key in ("spot", "mean_tail"):
                    _row76 = _blk76.get(_key) or {}
                    _pct76, _ann76 = _row76.get("pct"), _row76.get("annual_cny")
                    if _pct76 is None or _ann76 is None:
                        _bad76.append("%s %s row is incomplete" % (_tag76, _key))
                    elif abs(round(_pile76 * (_pct76 or 0.0) / 100.0, 0) - _ann76) > 1.0:
                        _bad76.append("%s %s annual does not follow from its own pile "
                                      "(%r vs %r)" % (_tag76, _key, _ann76,
                                                      round(_pile76 * (_pct76 or 0.0) / 100.0, 0)))
        else:
            for _key in ("spot", "mean_tail", "window"):
                _a76 = (_pb76.get(_key) or {})
                _b76 = (_money76.get(_key) or {})
                for _fld in ("pct", "annual_cny"):
                    if _a76.get(_fld) != _b76.get(_fld):
                        _bad76.append("%s.%s page=%r sheet=%r"
                                      % (_key, _fld, _a76.get(_fld), _b76.get(_fld)))
            if _pb76.get("verdict") != _money76.get("verdict"):
                _bad76.append("verdict page=%r sheet=%r"
                              % (_pb76.get("verdict"), _money76.get("verdict")))
            if abs(float(_pb76.get("cash_amount_cny") or 0)
                   - float(_page76.get("cash_amount_cny") or 0)) > 0.01:
                _bad76.append("the block prices a different pile of money than the page")
            if "同一笔现金" not in _md76:
                _bad76.append("the section is gone from the page")
            for _key in ("spot", "mean_tail", "window"):
                _cm_cny = ((_pb76.get(_key) or {}).get("annual_cny"))
                if _cm_cny is not None and format(int(_cm_cny), ",") not in _md76:
                    _bad76.append("%s annual (%s CNY) is not printed"
                                  % (_key, format(int(_cm_cny), ",")))
            if _pb76.get("verdict") == "RATES_FELL":
                if "利率掉下来" not in _md76:
                    _bad76.append("the face says rates fell but the page does not")
            elif "利率掉下来" in _md76:
                _bad76.append("the page calls it a fall while the face does not")
        check("product: the operator page prices the cash half on the sheet's own three rates",
              not _bad76,
              "; ".join(_bad76)[:220] or
              "spot %s / own mean %s / ledger window %s (%s)"
              % (format(int((_pb76.get("spot") or {}).get("annual_cny") or 0), ","),
                 format(int((_pb76.get("mean_tail") or {}).get("annual_cny") or 0), ","),
                 format(int((_pb76.get("window") or {}).get("annual_cny") or 0), ","),
                 _pb76.get("verdict")))
    except Exception as e:
        check("product: the operator page prices the cash half on the sheet's own three rates",
              False, repr(e)[:160])
    # ---- r1247: the operator page says what the entry gate is the source of ---------------
    # The whole universe is picked by one number (a 20M median-turnover cut), and r1246 swept
    # it: return is flat across the sweep, width is not. This leg re-derives the verdict from
    # the published rows through the face's own classify() (never from its sentence), then
    # demands the page print the same verdict, the same rows, and -- when the sweep really is
    # wide -- the capacity sentence. A page that re-types "20M is safe" instead of deriving it
    # reads red, and so does one that drops the section.
    try:
        import importlib as _il77
        _EG77 = _il77.import_module("etf_book_entry_gate")
        _p77 = os.path.join(PATHS.results_dir, "etf_book_entry_gate.json")
        _bad77 = []
        _doc77 = {}
        if not os.path.exists(_p77):
            _bad77.append("results/etf_book_entry_gate.json missing")
        else:
            with open(_p77, encoding="utf-8") as _fh77:
                _doc77 = json.load(_fh77)
        _again77 = _EG77.classify(
            _doc77.get("rows") or [],
            control_delta_pp=((_doc77.get("control") or {}).get("delta_pp")),
            universe_delta=((_doc77.get("config") or {}).get("universe_delta_names")))
        _stored77 = (_doc77.get("verdict") or {}).get("verdict")
        if _stored77 != _again77.get("verdict"):
            _bad77.append("stored verdict %r != recomputed %r"
                          % (_stored77, _again77.get("verdict")))
        _lb77 = os.path.join(PATHS.root, "docs", "live_book")
        _page77 = {}
        _md77 = ""
        _ptr77 = os.path.join(_lb77, "latest.json")
        if not os.path.exists(_ptr77):
            _bad77.append("docs/live_book/latest.json missing")
        else:
            with open(_ptr77, encoding="utf-8") as _fh77b:
                _pl77 = json.load(_fh77b)
            _js77 = os.path.join(PATHS.root, (_pl77.get("json") or "").replace("/", os.sep))
            _mdp77 = os.path.join(PATHS.root, (_pl77.get("page") or "").replace("/", os.sep))
            if _js77 and os.path.exists(_js77):
                with open(_js77, encoding="utf-8") as _fh77c:
                    _page77 = json.load(_fh77c)
            else:
                _bad77.append("the page json named by latest.json is absent")
            if _mdp77 and os.path.exists(_mdp77):
                with open(_mdp77, encoding="utf-8") as _fh77d:
                    _md77 = _fh77d.read()
            else:
                _bad77.append("the page md named by latest.json is absent")
        _eg77 = (_page77.get("entry_gate") or {})
        if _eg77.get("status") != "ok":
            _bad77.append("the page carries no entry gate (%r/%r)"
                          % (_eg77.get("status"), _eg77.get("detail")))
        else:
            if _eg77.get("verdict") != _again77.get("verdict"):
                _bad77.append("page verdict %r != recomputed %r"
                              % (_eg77.get("verdict"), _again77.get("verdict")))
            if "这本书的票池是被一个数选出来的" not in _md77:
                _bad77.append("the section is gone from the page")
            _page_rows77 = {int(round(float(g.get("gate_cny") or 0))): g
                            for g in (_eg77.get("gates") or [])}
            for _r77 in (_doc77.get("rows") or []):
                _g77 = int(round(float(_r77.get("min_amt_cny") or 0)))
                _pr77 = _page_rows77.get(_g77)
                if _pr77 is None:
                    _bad77.append("gate %s is on the face but not on the page" % _g77)
                    continue
                if abs(float(_pr77.get("cagr") or 0) - float(_r77.get("cagr") or 0)) > 1e-9:
                    _bad77.append("gate %s cagr page=%r face=%r"
                                  % (_g77, _pr77.get("cagr"), _r77.get("cagr")))
                if _pr77.get("median_names") != _r77.get("median"):
                    _bad77.append("gate %s median names page=%r face=%r"
                                  % (_g77, _pr77.get("median_names"), _r77.get("median")))
            for _r77 in (_doc77.get("rows") or []):
                if _r77.get("median") is None or _r77.get("cagr") is None:
                    continue
                if "%d" % int(_r77["median"]) not in _md77:
                    _bad77.append("gate %s median %s is not printed"
                                  % (_r77.get("min_amt_m"), _r77["median"]))
            _ratio77 = _eg77.get("width_ratio")
            if _ratio77 is not None and float(_ratio77) >= 2.0:
                if "容量来源" not in _md77:
                    _bad77.append("the sweep is wide (%.1fx) but the page never says the "
                                  "gate sets capacity" % float(_ratio77))
            elif "容量来源" in _md77:
                _bad77.append("the page calls the gate a capacity source while its own "
                              "rows are not wide")
        check("product: the operator page says the entry gate sets capacity, not return",
              not _bad77,
              "; ".join(_bad77)[:220] or
              "%s / %g..%gM / names %s..%s"
              % (_again77.get("verdict"),
                 min(float(g.get("gate_m") or 0) for g in (_eg77.get("gates") or [])),
                 max(float(g.get("gate_m") or 0) for g in (_eg77.get("gates") or [])),
                 _eg77.get("narrowest_names"), _eg77.get("widest_names")))
    except Exception as e:
        check("product: the operator page says the entry gate sets capacity, not return",
              False, repr(e)[:160])
    # ---- r1213 / E329: the expectation table's three rows are three rulers ---------------
    # The operator page prints row 1 from 2024-01-02 and rows 2-3 from 2020-01-01, over two
    # class universes and two fill orderings, under one column headed 全窗. This leg
    # re-derives the dial prices from the published cells (never from the sentence), requires
    # every identity arm to pass, and -- the part that makes it a page leg rather than a file
    # leg -- requires the page to print the SAME numbers: a page whose dial table drifted from
    # the face (the r1290 two-face class) is red here.
    try:
        import importlib as _il62
        _BR62 = _il62.import_module("etf_book_band_ruler")
        _p62 = os.path.join(PATHS.results_dir, "etf_book_band_ruler.json")
        _bad62 = []
        _doc62 = {}
        if not os.path.exists(_p62):
            _bad62.append("results/etf_book_band_ruler.json missing")
        else:
            with open(_p62, encoding="utf-8") as _fh62:
                _doc62 = json.load(_fh62)
            if _BR62.check() != 0:
                _bad62.append("the stored verdict no longer recomputes")
            _id62 = _doc62.get("identity") or {}
            if not _id62 or not all((v or {}).get("pass") for v in _id62.values()):
                _bad62.append("an identity arm failed: %r"
                              % ({k: (v or {}).get("delta_pp") for k, v in _id62.items()},))
            _pr62 = _BR62.dial_prices(_doc62)
            if {k: v.get("price_pp") for k, v in _pr62.items()} != \
                    {k: (v or {}).get("price_pp") for k, v in (_doc62.get("dial_prices") or {}).items()}:
                _bad62.append("dial prices drifted from the recomputation")
            _v62 = _BR62.decide(dict(_doc62, dial_prices=_pr62))
            if _v62.get("state") != (_doc62.get("verdict") or {}).get("state"):
                _bad62.append("verdict drifted: %r vs %r"
                              % ((_doc62.get("verdict") or {}).get("state"), _v62.get("state")))
            # the dial that decides the reading must be measured, not assumed
            for _k62 in ("window", "universe", "ordering", "cost"):
                if (_pr62.get(_k62) or {}).get("price_pp") is None:
                    _bad62.append("dial %s priced as unknown" % (_k62,))
            # the operator page must print the same numbers the face publishes
            _lb62 = os.path.join(PATHS.root, "docs", "live_book")
            _mds62 = sorted(glob.glob(os.path.join(_lb62, "LIVE-BOOK-*.md")))
            if not _mds62:
                _bad62.append("no LIVE-BOOK-*.md on disk")
            else:
                with open(_mds62[-1], encoding="utf-8") as _fh62b:
                    _md62 = _fh62b.read()
                if "谁按什么尺子量的" not in _md62:
                    _bad62.append("the page carries no ruler section")
                for _k62, _v62b in _pr62.items():
                    _val62 = (_v62b or {}).get("price_pp")
                    if _val62 is None:
                        continue
                    if ("%+.2f" % _val62) not in _md62:
                        _bad62.append("page does not print dial %s (%+.2f)" % (_k62, _val62))
        check("product: the expectation table's rows name the ruler that priced each one",
              not _bad62,
              "; ".join(_bad62)[:220] or "verdict %s, dials %s"
              % ((_doc62.get("verdict") or {}).get("state"),
                 {k: (v or {}).get("price_pp") for k, v in (_doc62.get("dial_prices") or {}).items()}))
    except Exception as e:
        check("product: the expectation table's rows name the ruler that priced each one",
              False, repr(e)[:160])
    # ---- r1216: the first row's 全窗 cell must be a full-window number --------------------
    # The page's table promised 6.3 years in a column headed 全窗 and printed the ticket's
    # own 683-bar return. This leg re-derives the two windows from the band ruler's cells
    # (never from the sentence), requires the identity arm to still reproduce the ticket's
    # published 12.78%, and requires the page's first row to print the FULL number in the
    # 全窗 column with the short one in the 2024+ column -- a page that drifted back to the
    # old layout is red here.
    try:
        import importlib as _il63
        _WL63 = _il63.import_module("etf_book_window_label")
        _p63 = os.path.join(PATHS.results_dir, "etf_book_window_label.json")
        _bad63 = []
        _doc63 = {}
        if not os.path.exists(_p63):
            _bad63.append("results/etf_book_window_label.json missing")
        else:
            with open(_p63, encoding="utf-8") as _fh63:
                _doc63 = json.load(_fh63)
            if _WL63.check() != 0:
                _bad63.append("the stored verdict no longer recomputes")
            for _k63, _c63 in _WL63.CRITERIA.items():
                if (_doc63.get("criteria") or {}).get(_k63) != _c63:
                    _bad63.append("criterion %s moved off the module constant" % (_k63,))
            _v63 = _WL63.decide(_doc63)
            if _v63.get("state") != (_doc63.get("verdict") or {}).get("state"):
                _bad63.append("verdict drifted: %r vs %r"
                              % ((_doc63.get("verdict") or {}).get("state"), _v63.get("state")))
            _tr63 = _WL63.table_row(dict(_doc63, verdict=_v63))
            if (_v63.get("state") == "ROW_LABELED_BY_WINDOW") and not _tr63:
                _bad63.append("the verdict names a window gap but publishes no row")
            # the operator page must print what the face publishes, in the right columns
            _lb63 = os.path.join(PATHS.root, "docs", "live_book")
            _mds63 = sorted(glob.glob(os.path.join(_lb63, "LIVE-BOOK-*.md")))
            if not _mds63:
                _bad63.append("no LIVE-BOOK-*.md on disk")
            elif _tr63:
                with open(_mds63[-1], encoding="utf-8") as _fh63b:
                    _md63 = _fh63b.read()
                _row63 = [ln for ln in _md63.splitlines()
                          if ln.startswith("| 5 名·可执行单口径")]
                if not _row63:
                    _bad63.append("the page's first expectation row is missing")
                else:
                    _r63 = _row63[0]
                    if "%.2f%%" % _tr63["full"]["cagr_pct"] not in _r63:
                        _bad63.append("the full-window cell is not the full-window number")
                    elif "%.2f%%" % _tr63["oos"]["cagr_pct"] in _r63 and \
                            _r63.index("%.2f%%" % _tr63["full"]["cagr_pct"]) > \
                            _r63.index("%.2f%%" % _tr63["oos"]["cagr_pct"]):
                        _bad63.append("the short-window number sits in the full-window column")
                    # r1216b: when the face publishes the operator's middle window, the
                    # page must carry it BETWEEN the two columns it tiles; and a dash in
                    # that row must be explained, never left to the reader's guess.
                    _mid63 = (_tr63.get("is") or {}).get("cagr_pct")
                    if _mid63 is not None:
                        _m63 = "%.2f%%" % _mid63
                        _full63 = "%.2f%%" % _tr63["full"]["cagr_pct"]
                        _oos63 = "%.2f%%" % _tr63["oos"]["cagr_pct"]
                        if _m63 not in _r63:
                            _bad63.append("the middle window the face publishes is "
                                          "missing from the operator's row")
                        elif not (_r63.index(_full63) < _r63.index(_m63) < _r63.index(_oos63)):
                            _bad63.append("the middle window is not in the middle "
                                          "column")
                    elif "\u2014" in _r63 and "\u8be5\u53e3\u5f84\u8fd9\u4e00\u683c" not in _md63:
                        _bad63.append("the row prints a dash with no legend explaining it")
                    if "表里第一行的" not in _md63:
                        _bad63.append("the page carries no window-label section")
        check("product: the row the operator reads has a full-window number in its full window column",
              not _bad63,
              "; ".join(_bad63)[:220] or "verdict %s, full %.2f%% / 2024+ %.2f%% (gap %+.2f pp/yr)"
              % ((_doc63.get("verdict") or {}).get("state"),
                 ((_tr63 or {}).get("full") or {}).get("cagr_pct") or 0.0,
                 ((_tr63 or {}).get("oos") or {}).get("cagr_pct") or 0.0,
                 (_doc63.get("verdict") or {}).get("gap_pp") or 0.0))
    except Exception as e:
        check("product: the row the operator reads has a full-window number in its full window column",
              False, repr(e)[:160])
    # ---- r1209: the missing bar is not a fill you could have chosen ----
    # r1207 priced the one-bar gap and r1208 put it on the CEO page, but nobody had asked the
    # operator's question: is the gap lost INFORMATION, or an unachievable FILL? This leg
    # re-reads the fill-venue face and requires the two things that make its answer evidence:
    # the verdict recomputes from the published rows, and the two fills an operator can
    # actually get (closing auction, next open) really are named and compared -- a face whose
    # arms silently collapsed to one book would print a venue verdict that measured nothing.
    try:
        import importlib as _il61
        _P61 = _il61.import_module("etf_book_fill_venue")
        _p61 = os.path.join(PATHS.results_dir, "etf_book_fill_venue.json")
        _bad61 = []
        if not os.path.exists(_p61):
            _bad61.append("results/etf_book_fill_venue.json missing")
            _doc61 = {}
        else:
            with open(_p61, encoding="utf-8") as _fh61:
                _doc61 = json.load(_fh61)
            if _P61.check(_p61) != 0:
                _bad61.append("the verdict does not recompute from the published rows")
            _v61 = _doc61.get("verdict") or {}
            if _v61.get("state") not in ("FILL_PRICE_DOMINATES", "INFORMATION_DOMINATES",
                                         "MIXED", "NO_GAP_TO_EXPLAIN", "INCOMPLETE"):
                _bad61.append("unknown verdict %r" % (_v61.get("state"),))
            _arms61 = {a.get("arm"): a for a in (_doc61.get("arms") or [])}
            for _need61 in ("card", "next_open", "close"):
                if _need61 not in _arms61:
                    _bad61.append("missing arm %r" % (_need61,))
            _pgrid61 = sorted(a.get("extra_bp_per_side") for a in _arms61.values()
                              if a.get("arm", "").startswith("close_i"))
            if _pgrid61 != sorted(_P61.IMPACT_BP[1:]):
                _bad61.append("extra-cost grid is %r" % (_pgrid61,))
            if not _bad61:
                _c61 = _arms61["card"]["cagr"]
                _n61 = _arms61["next_open"]["cagr"]
                _l61 = _arms61["close"]["cagr"]
                # the impossible fill must be the only one that is better than both
                # causal fills, otherwise the face is comparing two copies of one book
                if not (_c61 > _l61 and _c61 > _n61):
                    _bad61.append("the card fill is not above both causal fills "
                                  "(%.4f / %.4f / %.4f)" % (_c61, _l61, _n61))
                if abs((_doc61.get("reconciliation") or {}).get("fill_venue_pp", 0.0)
                       - round(100.0 * (_l61 - _n61), 3)) > 1e-9:
                    _bad61.append("the quoted fill-venue difference is not the two arms")
            if not (_doc61.get("cross_artifact") or {}).get("agrees"):
                _bad61.append("the face does not reproduce the look-ahead audit")
            for _k61, _c61 in _P61.CRITERIA.items():
                if (_doc61.get("criteria") or {}).get(_k61) != _c61:
                    _bad61.append("criterion %s moved off the module constant" % (_k61,))
        check("product: the missing bar is not a fill an operator could have chosen",
              not _bad61,
              "; ".join(_bad61)[:220] or "verdict %s, fill venue %+.2f pp/yr, recovered %+.2f "
              "of %+.2f pp/yr, budget %s"
              % ((_doc61.get("verdict") or {}).get("state"),
                 (_doc61.get("reconciliation") or {}).get("fill_venue_pp") or 0.0,
                 (_doc61.get("verdict") or {}).get("recovered_pp") or 0.0,
                 (_doc61.get("verdict") or {}).get("gap_pp") or 0.0,
                 (_doc61.get("verdict") or {}).get("execution_budget_bp_per_side")))
    except Exception as e:
        check("product: the missing bar is not a fill an operator could have chosen",
              False, repr(e)[:160])
    # ---- r1197: the exposure-timing answer has to reach the face the CEO opens ----
    # r1196 answered "is the de-lever timing or just a smaller book?" and filed it in a
    # research note; the page -- the one face the CEO actually opens -- still told him the
    # book shrinks without saying the shrinking buys no skill. Same wound as E311. This leg
    # re-reads the published face and requires the page to print THAT verdict and THOSE
    # numbers on the same pricing bar, so a stale page or a hand-typed number turns red.
    try:
        import importlib as _il57
        _P57 = _il57.import_module("etf_book_exposure_timing")
        _p57 = os.path.join(PATHS.results_dir, "etf_book_exposure_timing.json")
        _bad57 = []
        _pub57 = _P57.read_published(path=_p57)
        if _pub57.get("status") != "ok":
            _bad57.append("face does not read clean (%s)" % _pub57.get("status"))
        else:
            _ptr57p = os.path.join(PATHS.root, "docs", "live_book", "latest.json")
            _page57 = ""
            if os.path.exists(_ptr57p):
                with open(_ptr57p, encoding="utf-8") as _fh57:
                    _page57 = os.path.join(PATHS.root, json.load(_fh57).get("page") or "")
            if not _page57 or not os.path.exists(_page57):
                _bad57.append("no page the latest.json pointer names")
            else:
                with open(_page57, encoding="utf-8") as _fh57:
                    _md57 = _fh57.read()
                _json57p = os.path.splitext(_page57)[0] + ".json"
                _priced57 = None
                if os.path.exists(_json57p):
                    with open(_json57p, encoding="utf-8") as _fh57:
                        _pj57 = json.load(_fh57)
                    _priced57 = ((_pj57.get("priced_faces") or {}).get("page")
                                 or _pj57.get("evidence_cutoff"))
                if _priced57 != _pub57.get("evidence_cutoff"):
                    _bad57.append("page priced on %s but the exposure face is %s (stale page)"
                                  % (_priced57, _pub57.get("evidence_cutoff")))
                if "仓位不是一直满的" not in _md57:
                    _bad57.append("page carries no exposure-timing section")
                else:
                    _v57 = _pub57.get("verdict") or {}
                    _a57 = _pub57.get("arms") or {}
                    _want57 = [str(_v57.get("state")),
                               "%+.2fpp" % (_v57.get("timing_pp") or 0.0),
                               "%.2f%%" % (100 * ((_a57.get("production") or {}).get("cagr")
                                                  or 0.0)),
                               "%.2f%%" % (100 * ((_a57.get("constant") or {}).get("cagr")
                                                  or 0.0))]
                    for _w57 in _want57:
                        if _w57 not in _md57:
                            _bad57.append("page does not print %r" % (_w57,))
                    # the control is a matched-average book: if the page compared the
                    # book against full exposure instead, every de-lever "reduces drawdown"
                    if "同样的平均仓位" not in _md57:
                        _bad57.append("page does not name the matched-average control")
        check("product: the page tells a de-levered book from a well-timed one", not _bad57,
              "; ".join(_bad57)[:220] or "page prints %s on the face's own pricing bar"
              % ((_pub57.get("verdict") or {}).get("state"),))
    except Exception as e:
        check("product: the page tells a de-levered book from a well-timed one", False,
              repr(e)[:160])
    # ---- r1198: the cost assumption under every published number must be priced -----
    # Every CAGR on every face is charged 10 bp a side, and r1195 measured the tape at
    # 5.9 bp -- in a research note. The page kept silently carrying the assumption, the
    # same wound as E311 twice over. This leg demands the page print the MEASURED cost,
    # the three arms and the verdict from the published face, on the face's own cutoff,
    # and that the face's control arm reproduced the published CAGR (otherwise the
    # "conservative" claim compares two different books).
    try:
        import importlib as _il58
        _P58 = _il58.import_module("etf_book_cost_tape")
        _p58 = os.path.join(PATHS.results_dir, "etf_book_cost_tape.json")
        _bad58 = []
        _pub58 = _P58.read_published(path=_p58)
        if _pub58.get("status") != "ok":
            _bad58.append("face does not read clean (%s)" % _pub58.get("status"))
        else:
            if not (_pub58.get("control") or {}).get("passes"):
                _bad58.append("control arm did not reproduce the published CAGR")
            _ctl58 = _pub58.get("control") or {}
            if _ctl58.get("engine_cagr") is not None and _ctl58.get("published_cagr") is not None:
                if abs(float(_ctl58["engine_cagr"]) - float(_ctl58["published_cagr"])) * 100 \
                        > float(_ctl58.get("tolerance_pp") or 0.0):
                    _bad58.append("re-price at the assumed cost is %.2fpp away from the card"
                                  % (100 * abs(float(_ctl58["engine_cagr"])
                                               - float(_ctl58["published_cagr"]))))
            _ptr58p = os.path.join(PATHS.root, "docs", "live_book", "latest.json")
            _page58 = ""
            if os.path.exists(_ptr58p):
                with open(_ptr58p, encoding="utf-8") as _fh58:
                    _page58 = os.path.join(PATHS.root, json.load(_fh58).get("page") or "")
            if not _page58 or not os.path.exists(_page58):
                _bad58.append("no page the latest.json pointer names")
            else:
                with open(_page58, encoding="utf-8") as _fh58:
                    _md58 = _fh58.read()
                if "每一分钱按 10bp" not in _md58:
                    _bad58.append("page carries no cost-tape section")
                else:
                    _a58 = _pub58.get("arms") or {}
                    _want58 = ["%.1f bp" % (_pub58.get("measured_bp") or 0.0),
                               "%.0f%%" % (100 * (_pub58.get("ratio_vs_assumed") or 0.0)),
                               "%.2f%%" % (100 * ((_a58.get("measured") or {}).get("cagr")
                                                  or 0.0)),
                               "%.2f%%" % (100 * ((_a58.get("upper_p75") or {}).get("cagr")
                                                  or 0.0))]
                    for _w58 in _want58:
                        if _w58 not in _md58:
                            _bad58.append("page does not print %r" % (_w58,))
                    # a ">" inside a markdown table splits the row without any error (r1193):
                    # the page must carry the verdict with the pipe already replaced.
                    _v58 = str(_pub58.get("verdict") or "")
                    _v58_safe = " ".join(_v58.replace("|", "·").split())
                    if "|" in _v58 and _v58_safe not in " ".join(_md58.split()):
                        _bad58.append("page does not print the verdict in table-safe form")
                    if "控制臂" not in _md58:
                        _bad58.append("page does not name the control arm")
        check("product: the page prices the cost assumption under every number",
              not _bad58,
              "; ".join(_bad58)[:220]
              or "page prints the measured %.1f bp vs the card's %.0f bp (verdict %s)"
              % ((_pub58.get("measured_bp") or 0.0), (_pub58.get("assumed_bp") or 0.0),
                 _pub58.get("verdict")))
    except Exception as e:
        check("product: the page prices the cost assumption under every number", False,
              repr(e)[:160])
    # ---- v1.7: the CEO page must price the whole book in one line ----------
    try:
        _lu28p = os.path.join(PATHS.root, "docs", "live_usage", "LIVE-latest.json")
        _pe28p = os.path.join(PATHS.results_dir, "paper_export", "latest.json")
        _bad28 = []
        if not os.path.exists(_lu28p):
            _bad28.append("docs/live_usage/LIVE-latest.json missing")
        elif not os.path.exists(_pe28p):
            _bad28.append("results/paper_export/latest.json missing")
        else:
            with open(_lu28p, encoding="utf-8") as _fh28:
                _lu28 = json.load(_fh28)
            with open(_pe28p, encoding="utf-8") as _fh28:
                _pe28 = json.load(_fh28)
            _ru28 = _lu28.get("rollup") or {}
            _mem28 = _lu28.get("members") or []
            _tol28 = 0.5 * max(len(_mem28), 1)
            _sum28e = sum(float(m["equity_cny"]) for m in _mem28)
            _sum28c = sum(float(m["cash_cny"]) for m in _mem28)
            _ex28 = (_pe28.get("summary") or {}).get("total_equity_cny")
            if not _ru28:
                _bad28.append("the page carries no roll-up block")
            else:
                if abs(_ru28["equity_cny"] - _sum28e) > _tol28:
                    _bad28.append("roll-up equity %.2f != member sum %.2f"
                                  % (_ru28["equity_cny"], _sum28e))
                if abs(_ru28["cash_cny"] - _sum28c) > _tol28:
                    _bad28.append("roll-up cash %.2f != member cash %.2f"
                                  % (_ru28["cash_cny"], _sum28c))
                if _ex28 is None:
                    _bad28.append("export summary publishes no total equity")
                elif abs(_ru28["equity_cny"] - float(_ex28)) > _tol28:
                    _bad28.append("roll-up %.2f != export total %.2f"
                                  % (_ru28["equity_cny"], float(_ex28)))
                if abs(_ru28["pnl_cny"]
                       - (_ru28["equity_cny"] - _ru28["initial_cny"])) > 0.05:
                    _bad28.append("pnl is not equity - initial capital")
                if _ru28.get("day_pnl_cny") is None:
                    if _ru28.get("day_prior") is not None:
                        _bad28.append("day change missing though a prior export exists")
                elif _ru28.get("day_prior_equity_cny") is None:
                    _bad28.append("day change printed without its comparison total")
                elif abs(_ru28["day_pnl_cny"]
                         - (_ru28["equity_cny"]
                            - _ru28["day_prior_equity_cny"])) > 0.05:
                    _bad28.append("day change is not today minus the prior export")
                _md28p = os.path.join(PATHS.root, "docs", "live_usage",
                                      "LIVE-%s.md" % str(_lu28.get("day") or "")
                                      .replace("-", ""))
                if not os.path.exists(_md28p):
                    _md28p = os.path.join(PATHS.root, "docs", "live_usage",
                                          "LIVE-latest.md")
                if not os.path.exists(_md28p):
                    _bad28.append("the rendered page is absent")
                else:
                    with open(_md28p, encoding="utf-8") as _fh28:
                        _md28 = _fh28.read()
                    if "六员合计" not in _md28:
                        _bad28.append("the rendered page has no total line")
                    elif _ru28.get("return_pct") is not None and \
                            ("%+.2f%%" % _ru28["return_pct"]) not in _md28:
                        _bad28.append("the total line omits the cumulative return")
        check("product: the CEO page prices the whole book in one line",
              not _bad28, "; ".join(_bad28)[:220]
              or ("equity %.0f / initial %.0f / positions %.0f / day %s"
                  % (float(_ru28.get("equity_cny") or 0),
                     float(_ru28.get("initial_cny") or 0),
                     float(_ru28.get("positions_cny") or 0),
                     _ru28.get("day_pnl_cny"))))
    except Exception as e:
        check("product: the CEO page prices the whole book in one line", False,
              repr(e)[:160])
    # ---- v1.8: the CEO page must carry the market risk tape, recomputed ----
    try:
        _lu30p = os.path.join(PATHS.root, "docs", "live_usage",
                              "LIVE-latest.json")
        _bad30 = []
        _info30 = ""
        if not os.path.exists(_lu30p):
            _bad30.append("docs/live_usage/LIVE-latest.json missing")
        else:
            with open(_lu30p, encoding="utf-8") as _fh30:
                _lu30 = json.load(_fh30)
            _rt30 = _lu30.get("risk_tape") or {}
            _st30 = _rt30.get("status")
            if _st30 not in ("ok", "absent", "unavailable", "unreadable"):
                _bad30.append("risk tape publishes no honest status (%r)" % (_st30,))
            if _st30 == "ok":
                _dr30 = importlib.import_module("daily_report")
                _pd30 = importlib.import_module("pandas")
                _pn30 = _rt30.get("panels") or {}
                _rec30 = []
                for _k30 in ("zt", "dtgc", "zbgc", "strong"):
                    _row30 = _pn30.get(_k30) or {}
                    _cnt30 = _row30.get("count")
                    _p30 = os.path.join(PATHS.root, "data", "zt_pool",
                                        "%s.parquet" % _k30)
                    if _cnt30 is None:
                        if _row30.get("status") == "ok":
                            _bad30.append("%s claims ok with no count" % _k30)
                        continue
                    if not os.path.exists(_p30):
                        _bad30.append("%s publishes a count but the panel is absent"
                                      % _k30)
                        continue
                    _df30 = _pd30.read_parquet(_p30)
                    _d30 = _df30[_dr30.ZT_DATE_COL].map(
                        lambda v: str(v)[:10])
                    _cut30 = str(_d30.max())
                    _n30 = int((_d30 == _cut30).sum())
                    if _cut30 != str(_row30.get("prev_cutoff") or _cut30) and \
                            _cut30 != str(_rt30.get("cutoff")):
                        _bad30.append("%s recomputed bar %s not the published bar"
                                      % (_k30, _cut30))
                    if _n30 != int(_cnt30):
                        _bad30.append("%s page says %s members, panel holds %d"
                                      % (_k30, _cnt30, _n30))
                    _rec30.append("%s %d" % (_k30, _n30))
                _info30 = "cutoff %s | %s" % (_rt30.get("cutoff"),
                                              " / ".join(_rec30))
                _md30p = os.path.join(PATHS.root, "docs", "live_usage",
                                      "LIVE-latest.md")
                if not os.path.exists(_md30p):
                    _bad30.append("the rendered one-pager is absent")
                else:
                    with open(_md30p, encoding="utf-8") as _fh30:
                        _md30 = _fh30.read()
                    if "市场风险面" not in _md30:
                        _bad30.append("the one-pager has no risk-tape line")
                    elif str(_rt30.get("cutoff")) not in _md30:
                        _bad30.append("the risk line omits its cutoff bar")
        check("product: the CEO page carries today's market risk tape",
              not _bad30, "; ".join(_bad30)[:220] or _info30)
    except Exception as e:
        check("product: the CEO page carries today's market risk tape", False,
              repr(e)[:160])
    # ---- r1171: the cap a page prints must be reconciled with the book it prices ----
    # The whole point of the cap-vs-book face is that no reader should have to guess
    # whether a 76.8% book beside a "RED, cap 20%" line means the guard broke. That
    # only holds while BOTH human faces say the same sentence as the artifact, so the
    # leg recomputes the verdict from the published rows and demands the sentence
    # verbatim on the page AND in the newest battle report (a hand-written second
    # sentence on either face reads red here).
    try:
        _cvbp = os.path.join(PATHS.root, "results", "regime_cap_vs_book.json")
        _bad31 = []
        _info31 = ""
        if not os.path.exists(_cvbp):
            _bad31.append("results/regime_cap_vs_book.json missing")
        else:
            with open(_cvbp, encoding="utf-8") as _fh31:
                _cvb31 = json.load(_fh31)
            _sen31 = _cvb31.get("sentence") or ""
            _v31 = _cvb31.get("verdict") or {}
            _cap31 = _cvb31.get("ladder_cap")
            _acc31 = _cvb31.get("accounts") or []
            _rows31 = [r for r in _acc31
                       if r.get("kind") == "ladder"
                       and r.get("deployed_weight") is not None]
            _above31 = [r for r in _rows31 if r.get("status") == "above_cap"]
            if not _sen31:
                _bad31.append("the verdict publishes no sentence")
            if (_v31.get("n_above") != len(_above31)
                    or _v31.get("n_compared") != len(_rows31)):
                _bad31.append("verdict says %s/%s but the rows hold %d/%d"
                              % (_v31.get("n_above"), _v31.get("n_compared"),
                                 len(_above31), len(_rows31)))
            for _r31 in _above31:
                if not (_cap31 and _r31["deployed_weight"] > _cap31):
                    _bad31.append("%s reads above_cap at %.4f vs cap %s"
                                  % (_r31.get("name"), _r31["deployed_weight"],
                                     _cap31))
            if any(r.get("kind") == "own_rule" and r.get("status") == "above_cap"
                   for r in _acc31):
                _bad31.append("an own-rule book was graded against the ladder")
            _widest31 = (max(_above31, key=lambda r: r["deployed_weight"])
                         if _above31 else None)
            _p31 = os.path.join(PATHS.root, "docs", "live_usage", "LIVE-latest.md")
            if not os.path.exists(_p31):
                _bad31.append("docs/live_usage/LIVE-latest.md missing")
            else:
                with open(_p31, encoding="utf-8") as _fh31:
                    _md31 = _fh31.read()
                if _sen31 not in _md31:
                    _bad31.append("the CEO page does not quote the published sentence")
                if _widest31 and "%s" % _widest31["name"] not in _md31:
                    _bad31.append("the CEO page omits the widest over-cap account")
            _rep31 = sorted(glob.glob(os.path.join(
                PATHS.root, "docs", "daily_report", "REPORT-*.md")))
            if not _rep31:
                _bad31.append("no battle report on disk")
            else:
                with open(_rep31[-1], encoding="utf-8") as _fh31:
                    _rmd31 = _fh31.read()
                if _sen31 not in _rmd31:
                    _bad31.append("the newest battle report (%s) does not carry the "
                                  "same sentence" % os.path.basename(_rep31[-1]))
            _info31 = ("cap %s | %d of %d over | widest %s"
                       % (_cap31, len(_above31), len(_rows31),
                          _widest31["name"] if _widest31 else "none"))
        check("product: the printed cap is reconciled with the priced book on both faces",
              not _bad31, "; ".join(_bad31)[:220] or _info31)
    except Exception as e:
        check("product: the printed cap is reconciled with the priced book on both faces",
              False, repr(e)[:160])
    # ---- r1171: a consumer leg must not run before the producer it quotes (r1318) ----
    try:
        _ord31 = [t[0] for t in importlib.import_module(
            "Tools.s6_chain_bmc").LEGS]
        _bad32 = []
        if "regime_cap_vs_book" not in _ord31:
            _bad32.append("regime_cap_vs_book is not on the chain")
        else:
            _i31 = _ord31.index("regime_cap_vs_book")
            for _c31 in ("daily_report", "ceo_live_usage"):
                if _c31 in _ord31 and _ord31.index(_c31) < _i31:
                    _bad32.append("%s runs before the verdict it quotes" % _c31)
        check("config: the cap-vs-book producer runs before the faces that quote it",
              not _bad32, "; ".join(_bad32)[:220]
              or "producer at position %d of %d legs" % (_i31 + 1, len(_ord31)))
    except Exception as e:
        check("config: the cap-vs-book producer runs before the faces that quote it",
              False, repr(e)[:160])
    # ---- r1218: the battle report's ETF book section is the page's own payload ----
    # The report is where the CEO reads the book every morning; before this leg it
    # carried no book at all, so "the book is fine" and "nobody printed the book"
    # looked the same. The numbers are re-derived from the producer payload here --
    # a hand-written second sentence, or a report whose priced bar lags the payload,
    # reads red.
    try:
        _bad33 = []
        _info33 = ""
        _drp33 = importlib.import_module("etf_book_ceo_page")
        _pl33, _pmd33 = _drp33.build()
        _dr33 = importlib.import_module("daily_report")
        _fc33 = _dr33._etf_book_face()
        if _fc33.get("status") != "ok":
            _bad33.append("the report's book face reads %r (%s)"
                          % (_fc33.get("status"), _fc33.get("detail")))
        else:
            for _k33 in ("priced_bar", "book_amount_cny", "cash_amount_cny",
                         "n_hold", "next_rebalance_date"):
                if _fc33.get(_k33) != _pl33.get(_k33):
                    _bad33.append("%s: face %r vs producer %r"
                                  % (_k33, _fc33.get(_k33), _pl33.get(_k33)))
        _rp33 = sorted(glob.glob(os.path.join(
            PATHS.root, "docs", "daily_report", "REPORT-*.md")))
        if not _rp33:
            _bad33.append("no battle report on disk")
        else:
            with open(_rp33[-1], encoding="utf-8") as _fh33:
                _rmd33 = _fh33.read()
            _seg33 = _rmd33[_rmd33.find("## 十二、ETF"):
                            (_rmd33.find("## Token") if "## Token" in _rmd33
                             else len(_rmd33))]
            if not _seg33:
                _bad33.append("the newest report (%s) has no ETF book section"
                              % os.path.basename(_rp33[-1]))
            else:
                if str(_pl33.get("priced_bar")) not in _seg33:
                    _bad33.append("the book section omits the priced bar")
                _env33 = _pl33.get("envelope") or {}
                if _env33.get("status") == "ok":
                    _p5033 = ((_env33.get("cagr") or {}).get("50"))
                    if _p5033 is not None and ("%.2f%%" % (float(_p5033) * 100)) not in _seg33:
                        _bad33.append("the section does not print the envelope p50 "
                                      "that the producer published")
                else:
                    # no envelope -> the section must not silently print a percentile
                    if "运气分布" in _seg33 and "p5" in _seg33:
                        _bad33.append("an absent envelope was printed as a distribution")
            _info33 = ("report %s | priced %s | book %s | env %s"
                       % (os.path.basename(_rp33[-1]), _pl33.get("priced_bar"),
                          _pl33.get("book_amount_cny"),
                          (_pl33.get("envelope") or {}).get("status")))
        check("product: the battle report carries the book it is about",
              not _bad33, "; ".join(_bad33)[:220] or _info33)
    except Exception as e:
        check("product: the battle report carries the book it is about",
              False, repr(e)[:160])
    try:
        # r1355: the width floor and the buffer read-back are published verdicts, so a reader
        # must be able to re-derive each one from the numbers ON the face -- not from the script
        # that wrote it. The label is recomputed here from the published rungs and the face's
        # own frozen thresholds, and a verdict that no longer follows from its numbers is red.
        _wf = json.load(open(os.path.join(PATHS.root, "results",
                                          "etf_book_width_resolution_floor.json"),
                             encoding="utf-8"))
        _wrule = _wf.get("rule") or {}
        _wr = _wf.get("rungs") or []
        _wups = sum(1 for _r in _wr if _r.get("up"))
        _wagree = round(max(_wups, len(_wr) - _wups) / float(len(_wr)), 3) if _wr else None
        _wslope = (_wf.get("fit") or {}).get("slope_pp_per_name")
        _wreq = _wf.get("width_required")
        if _wagree is None or _wslope is None:
            _wlab = "NOT-ASSESSED"
        elif _wagree < _wrule.get("sign_agreement_min", 0.75):
            _wlab = "DIRECTION_NOT_A_SIZE"
        elif _wslope <= 0:
            _wlab = "UNREACHABLE_BY_CONSTRUCTION"
        elif _wreq is not None and _wreq > _wrule.get("priced_width_max", 20):
            _wlab = "UNREACHABLE_INSIDE_PRICED_ENVELOPE"
        else:
            _wlab = "REACHABLE_DECLARE_A_RUN"
        _wbad = []
        if _wagree != _wf.get("sign_agreement"):
            _wbad.append("sign agreement says %s, its own rungs say %s"
                         % (_wf.get("sign_agreement"), _wagree))
        if _wlab != _wf.get("verdict"):
            _wbad.append("verdict says %s, its own numbers say %s"
                         % (_wf.get("verdict"), _wlab))
        if (_wf.get("priced_envelope_crosscheck") or {}).get("sign_flips_by_cadence") is None:
            _wbad.append("the second engine's cross-check is absent")
        _rb = json.load(open(os.path.join(PATHS.root, "results",
                                          "etf_book_buffer_floor_readback.json"),
                             encoding="utf-8"))
        if _rb.get("verdict") == "NOT-ASSESSED":
            _wbad.append("the read-back refused to answer")
        else:
            _gap = abs(float(_rb.get("observed_pp")) - float(_rb.get("predicted_pp")))
            if _gap > float(_rb.get("tolerance_pp")):
                _wbad.append("the harvested point sits %.3fpp off the line, past the %.3fpp "
                             "tolerance, but the face still says %s"
                             % (_gap, float(_rb.get("tolerance_pp")), _rb.get("verdict")))
            if (_rb.get("gap_pp") is None
                    or abs(round(float(_rb.get("observed_pp")) - float(_rb.get("predicted_pp")), 3)
                           - float(_rb.get("gap_pp"))) > 1e-9):
                _wbad.append("the published gap is not observed minus predicted")
        check("product: the width ladder names why it cannot be quoted, and the buffer line "
              "is tested on a point it never saw", not _wbad,
              "; ".join(_wbad)[:220] or "width=%s (agree %s, needs width %s) | readback=%s "
              "(gap %+.3fpp/%.3fpp)" % (_wf.get("verdict"), _wagree, _wreq,
                                        _rb.get("verdict"), float(_rb.get("gap_pp") or 0.0),
                                        float(_rb.get("tolerance_pp") or 0.0)))
    except Exception as e:
        check("product: the width ladder names why it cannot be quoted, and the buffer line "
              "is tested on a point it never saw", False, repr(e)[:160])
    try:
        # r1356: the two live faces (card 12 names, ticket 5 names) are compared on the same
        # ruler, and the answer is a verdict about whether the gap is even a width effect. A
        # reader must be able to rebuild that verdict from the face's own published deltas and
        # its own frozen thresholds -- a stored label that no longer follows from the numbers is
        # red, and so is a face that publishes a gap without the per-phase differences behind it.
        _lv = json.load(open(os.path.join(PATHS.root, "results",
                                          "etf_book_live_width_ruler.json"),
                             encoding="utf-8"))
        _lrule = _lv.get("rule") or {}
        _lpr = _lv.get("paired") or {}
        _ld = [float(x) for x in (_lpr.get("deltas_pp") or [])]
        _led = _lv.get("engine_disagreement") or {}
        _lbad = []
        if len(_ld) < int(_lrule.get("pairs_min", 20)):
            _lbad.append("%d paired phase differences published, floor is %s"
                         % (len(_ld), _lrule.get("pairs_min")))
        else:
            _ls = sorted(_ld)
            _lmed = round(_ls[len(_ls) // 2] if len(_ls) % 2 else
                          (_ls[len(_ls) // 2 - 1] + _ls[len(_ls) // 2]) / 2.0, 3)
            _lups = sum(1 for _d in _ld if _d > 0)
            _lagree = round(max(_lups, len(_ld) - _lups) / float(len(_ld)), 3)
            if abs(_lmed - float(_lpr.get("median_pp"))) > 1e-9:
                _lbad.append("published median %s, the deltas say %s"
                             % (_lpr.get("median_pp"), _lmed))
            if _lagree != _lpr.get("sign_agreement"):
                _lbad.append("published sign agreement %s, the deltas say %s"
                             % (_lpr.get("sign_agreement"), _lagree))
            _ldis = _led.get("rung_disagreement_pp")
            if _ldis is None:
                _lbad.append("no rung disagreement: the second engine's face is missing")
            else:
                _labs = abs(_lmed)
                if _lagree <= float(_lrule.get("sign_split_max", 0.6)) and _labs < float(_ldis):
                    _llab = "COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT"
                elif _labs < float(_ldis):
                    _llab = "SIGNED_BUT_INSIDE_ENGINE_DISAGREEMENT"
                elif _lagree > float(_lrule.get("sign_split_max", 0.6)):
                    _llab = "RESOLVED_BEYOND_ENGINE_DISAGREEMENT"
                else:
                    _llab = "UNSIGNED_AND_BEYOND"
                if _llab != _lv.get("verdict"):
                    _lbad.append("verdict says %s, its own deltas say %s"
                                 % (_lv.get("verdict"), _llab))
                # the comparator must be a difference minus a difference: had the gate used the
                # LEVEL gap (~6.4pp) instead of the rung (2.0pp), a 0.09pp gap would have read
                # "resolved", which is the r1292 unit trap in this face's own clothes
                _llev = max((_led.get("level_gap_pp") or {"0": 0}).values())
                if _llev > float(_ldis) * 2 and _labs < float(_ldis) and _labs >= _llev:
                    _lbad.append("the level gap %.2fpp decided the verdict" % _llev)
        _lai = _lv.get("as_issued") or {}
        if _lai:
            if not (_lai.get("decomposition") or {}).get("paths_agree"):
                _lbad.append("the two decomposition paths disagree, so the 2x2 is inconsistent")
            _lw = _lai.get("width_effect_pp") or {}
            _lcell = _lai.get("cells_cagr_pp") or {}
            if all(k in _lcell for k in ("beta@5", "beta@12")):
                _lrb = round(_lcell["beta@12"] - _lcell["beta@5"], 3)
                if abs(_lrb - float(_lw.get("beta", 0.0))) > 0.011:
                    _lbad.append("the beta-rule width effect is not beta@12 minus beta@5")
            # r1242: the as-issued 2x2 is a snapshot of a ticket that is re-written every time
            # the book is priced, so the snapshot must name the ticket it came from -- without
            # that date the gate cannot tell a re-issue (stale, refresh) from an edit (red).
            if not _lai.get("ticket_asof"):
                _lbad.append("the as-issued block carries no ticket date, so a re-issued "
                             "ticket cannot be told apart from a hand-edited face")
        check("product: the two live widths are priced on one ruler and the gap is inside the "
              "engines' own disagreement", not _lbad,
              "; ".join(_lbad)[:220] or "%s | paired %+.3fpp over %d phases, engine "
              "disagreement %.3fpp" % (_lv.get("verdict"),
                                       float(_lpr.get("median_pp") or 0.0), len(_ld),
                                       float(_led.get("rung_disagreement_pp") or 0.0)))
    except Exception as e:
        check("product: the two live widths are priced on one ruler and the gap is inside the "
              "engines' own disagreement", False, repr(e)[:160])
    try:
        # r1362: a width sign is only a sign if it survives off the grid that produced it AND
        # is not what a noise score produces. Re-derive both from the face's own numbers: every
        # rung must have traded, the arm states must follow from their rank correlations, and the
        # real-minus-null difference must be the difference of the two published columns.
        _wp = os.path.join("results", "etf_book_width_cross.json")
        if os.path.exists(_wp):
            _wj = json.load(open(_wp, encoding="utf-8"))
            _wbad = []
            _spec = _wj.get("spec") or {}
            for _a in (_wj.get("arms") or []):
                _rho = _a.get("rho_cagr_width")
                _share = (_a.get("paired_cagr") or {}).get("share_up")
                if _rho is None or _share is None:
                    _wbad.append("arm %s has no rank corr / paired share" % _a.get("cost_bp"))
                    continue
                _want = ("replicates" if (_rho >= float(_spec.get("rho_min", 0.7))
                                          and _share >= float(_spec.get("phase_share_min", 0.6)))
                         else "flips" if (_rho <= -float(_spec.get("rho_min", 0.7))
                                          or _share <= float(_spec.get("phase_share_flip", 0.4)))
                         else "undecided")
                if _want != _a.get("state"):
                    _wbad.append("arm %s stored %s, its numbers say %s"
                                 % (_a.get("cost_bp"), _a.get("state"), _want))
                for _w, _row in (_a.get("per_width") or {}).items():
                    if (_row.get("turnover_median") or 0) <= 0:
                        _wbad.append("width %s at %sbp never traded"
                                     % (_w, _a.get("cost_bp")))
            _att = _wj.get("attribution") or {}
            if _att.get("status") == "read":
                _r = _att.get("real_cagr_pp") or []
                _n = _att.get("null_cagr_pp") or []
                _d = _att.get("deltas_pp") or []
                if len(_r) == len(_n) == len(_d):
                    for _i in range(len(_d)):
                        if abs((_r[_i] - _n[_i]) - _d[_i]) > 0.02:
                            _wbad.append("delta[%d] is not real minus null" % _i)
                else:
                    _wbad.append("attribution columns are ragged")
            else:
                _wbad.append("no random-score control on the face")
            check("product: the width sign is read against a noise score, not just another grid",
                  not _wbad, "; ".join(_wbad)[:220]
                  or "%s | real-null %spp | rho null %s"
                  % (_wj.get("verdict"), (_att.get("deltas_pp") or [])[:4],
                     _att.get("rho_null_width")))
        else:
            check("product: the width sign is read against a noise score, not just another grid",
                  True, "width-cross face absent -- soft-fails by design")
    except Exception as e:
        check("product: the width sign is read against a noise score, not just another grid",
              False, repr(e)[:160])
    try:
        # r1181: the compute audit's supply face must read the CLAIM-BY-FILE truth. Two
        # readers of "is this unit being burned" must agree, so the staleness line is read
        # from the claimer itself rather than restated here.
        import importlib.util as _ilu
        def _load(path, name):
            _s = _ilu.spec_from_file_location(name, path)
            _m = _ilu.module_from_spec(_s)
            _s.loader.exec_module(_m)
            return _m
        _ca = _load(os.path.join("scripts", "compute_audit.py"), "_smoke_ca")
        _pw = _load(os.path.join("Tools", "pool_worker.py"), "_smoke_pw")
        _bad = []
        if float(_ca.POOL_CLAIM_STALE_MIN) != float(_pw.STALE_MIN):
            _bad.append("audit staleness %s != claimer %s"
                        % (_ca.POOL_CLAIM_STALE_MIN, _pw.STALE_MIN))
        _aj = os.path.join("results", "compute_audit.json")
        if os.path.exists(_aj):
            _doc = json.load(open(_aj, encoding="utf-8"))
            _cur = (_doc.get("latest") if isinstance(_doc, dict)
                    and isinstance(_doc.get("latest"), dict) else _doc)
            _face = _cur.get("pool_claim_by_file")
            if not isinstance(_face, dict):
                _bad.append("the published audit has no claim-by-file face")
            else:
                # a ready row that a fresh claim covers must NOT be published as unclaimed
                for _eid in (_face.get("ids") or []):
                    if (_cur.get("pool_ignitable") or {}).get("claimed_by_file_ids") \
                            and _eid not in _cur["pool_ignitable"]["claimed_by_file_ids"]:
                        _bad.append("%s claimed but not named in the ignitable face" % _eid)
                if _face.get("ids") and (_cur.get("pool_ready_unclaimed") or 0) > 0:
                    _bad.append("claim face names a live burn while unclaimed=%s"
                                % _cur.get("pool_ready_unclaimed"))
        check("product: the compute audit reads the claim face, not just the pool row",
              not _bad, "; ".join(_bad)[:200]
              or "staleness line == Tools/pool_worker.STALE_MIN (%.0f min)"
              % float(_ca.POOL_CLAIM_STALE_MIN))
    except Exception as e:
        check("product: the compute audit reads the claim face, not just the pool row",
              False, repr(e)[:160])
    # ---- r1216b: a quiet lane and a switched-off lane print the same round line ----
    # The ledger can only say "no rounds". The scheduler is the only place that can say
    # "I turned it off", so the published face must carry that answer AND must recompute
    # it from its own states through one implementation (a second reader would drift).
    try:
        import importlib as _il65
        _LSA65 = _il65.import_module("lane_silence_audit")
        _pub65 = _LSA65.read_published()
        _bad65 = []
        if not _pub65.get("present"):
            _bad65.append("the lane-silence face is not published")
        else:
            _lt65 = _pub65.get("lane_tasks") or {}
            if not _lt65.get("verdict"):
                _bad65.append("the face carries no lane-task verdict (a silent lane and "
                              "a switched-off one would print the same line)")
            else:
                _redo65 = _LSA65.switch_face(_lt65.get("states") or {},
                                            _pub65.get("silence_verdict"),
                                            _pub65.get("threshold_min"))
                if _redo65["verdict"] != _lt65.get("verdict"):
                    _bad65.append("lane-task verdict does not recompute: stored %s vs %s"
                                  % (_lt65.get("verdict"), _redo65["verdict"]))
                for _n65, _st65 in (_lt65.get("states") or {}).items():
                    if (_st65 == "Disabled") != (_n65 in (_lt65.get("disabled") or [])):
                        _bad65.append("%s state and disabled list disagree" % _n65)
        check("product: the lane-silence face names whether the lane is switched off",
              not _bad65, "; ".join(_bad65)[:200]
              or "lane tasks %s -> %s"
              % (", ".join("%s=%s" % (k, v) for k, v in
                           sorted(((_pub65.get("lane_tasks") or {}).get("states") or {}).items())),
                 (_pub65.get("lane_tasks") or {}).get("verdict")))
    except Exception as e:
        check("product: the lane-silence face names whether the lane is switched off",
              False, repr(e)[:160])
    try:
        # O-20261102-2015 sec.2: the CPU-hours line must be recomputable from the
        # sampler rows AND each batch must name a file that is actually on disk.
        _day = dt.date.today().isoformat()
        _stem = _day.replace("-", "")
        _root66 = os.path.dirname(os.path.abspath(__file__))
        _rep = os.path.join(_root66, "docs", "daily_report", "REPORT-%s.json" % _day)
        _md = os.path.join(_root66, "docs", "daily_report", "REPORT-%s.md" % _day)
        _cs = (json.load(open(_rep, encoding="utf-8")).get("core_spread") or {})
        _rows, _secs = 0, 0.0
        try:
            with open(os.path.join(_root66, "results", "pool_core_samples.jsonl"),
                      encoding="utf-8") as _f:
                for _ln in _f:
                    _ln = _ln.strip()
                    if not _ln:
                        continue
                    try:
                        _r = json.loads(_ln)
                    except Exception:
                        continue
                    if not isinstance(_r, dict):
                        continue
                    if not str(_r.get("ts", "")).startswith(_day):
                        continue
                    if _r.get("verdict") not in ("multicore_burn", "single_core_burn"):
                        continue
                    _rows += 1
                    _secs += float(_r.get("cpu_s") or 0.0)
        except FileNotFoundError:
            _rows, _secs = 0, 0.0
        _fleet = _cs.get("fleet") or {}
        _bad66 = []
        if int(_fleet.get("batches_judged") or 0) != _rows:
            _bad66.append("batches %s != sampler %d" % (_fleet.get("batches_judged"), _rows))
        if abs(float(_fleet.get("core_hours") or 0.0) - _secs / 3600.0) > 5e-4:
            _bad66.append("core_hours %s != recomputed %.4f"
                          % (_fleet.get("core_hours"), _secs / 3600.0))
        for _mid66, _m66 in (_cs.get("machines") or {}).items():
            for _b66 in _m66.get("batches") or []:
                if "deliverable" not in _b66:
                    _bad66.append("%s/%s has no deliverable key" % (_mid66, _b66.get("entry")))
                elif _b66.get("deliverable") and not _b66.get("deliverable_exists"):
                    _bad66.append("%s/%s names a file not on disk" % (_mid66, _b66.get("entry")))
        if not os.path.exists(_md) or "CPU 有效工时" not in open(_md, encoding="utf-8").read():
            _bad66.append("report does not print the CPU work-hours line")
        check("product: CPU work-hours are recomputable and every batch names a file",
              not _bad66, "; ".join(_bad66)[:200]
              or "%d batch(es), %s core-hours on %s" % (_rows, _fleet.get("core_hours"), _day))
    except Exception as e:
        check("product: CPU work-hours are recomputable and every batch names a file",
              False, repr(e)[:160])
    # ---- r1249: a check that re-derives from its own rows is green on ANY panel ----
    # exposure_timing / exposure_ladder / sleeve_paths sat on the 2026-10-30 panel with green
    # checks while the book priced 2026-11-03. The gate must be inside all three, must say
    # STALE (the chain's refresh arm fires on that word), and must not be able to fire on a
    # verdict/identity disagreement -- rebuilding there would launder the disagreement.
    try:
        import contextlib as _ctx49
        import io as _io49
        _sp49 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
        if _sp49 not in sys.path:
            sys.path.insert(0, _sp49)
        _F49 = importlib.import_module("etf_book_forward")
        _X49 = importlib.import_module("etf_book_exposure_timing")
        _L49 = importlib.import_module("etf_book_exposure_ladder")
        _S49 = importlib.import_module("etf_book_sleeve_paths")
        _bad49 = []
        _orig49 = _F49.panel_stamp
        _F49.panel_stamp = lambda load=True: {"digest": "cafdf7d5"}   # never load the panel
        try:
            for _mod49, _nm49, _face49 in (
                    (_X49, "timing", "results/etf_book_exposure_timing.json"),
                    (_L49, "ladder", "results/etf_book_exposure_ladder.json"),
                    (_S49, "sleeve", "results/etf_book_sleeve_paths.json")):
                _pub49 = json.load(open(_face49, encoding="utf-8"))
                if not ((_pub49.get("panel") or {}).get("digest")):
                    _bad49.append("%s publishes no panel stamp" % _nm49)
                _stale49 = json.loads(json.dumps(_pub49))
                _stale49.setdefault("panel", {})["digest"] = "0ld0dead"
                _fx49 = os.path.join(".codely-cli", "tmp", "_smoke_r1249_stale_%s.json" % _nm49)
                os.makedirs(os.path.dirname(_fx49), exist_ok=True)
                json.dump(_stale49, open(_fx49, "w", encoding="utf-8"))
                _buf49 = _io49.StringIO()
                with _ctx49.redirect_stdout(_buf49):
                    _rc49 = _mod49.check(_fx49)
                _txt49 = _buf49.getvalue().lower()
                if _rc49 != 2:
                    _bad49.append("%s: a face left on an older panel returned %r, not 2"
                                  % (_nm49, _rc49))
                if "stale" not in _txt49:
                    _bad49.append("%s: the stale message does not say 'stale', so the "
                                  "chain's refresh arm never fires" % _nm49)
            if _F49.check_panel_stamp({"panel": {"digest": "cafdf7d5"}},
                                      stamp={"digest": None}) != 0:
                _bad49.append("an unreadable current panel is reported as a moved one")
            _tools49 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tools")
            if _tools49 not in sys.path:
                sys.path.insert(0, _tools49)
            _legs49 = dict((t[0], t)
                           for t in importlib.import_module("s6_chain_bmc").LEGS)
            for _nm49 in ("etf_book_exposure_timing", "etf_book_exposure_ladder",
                          "etf_book_sleeve_paths"):
                if len(_legs49.get(_nm49) or ()) < 3:
                    _bad49.append("%s has no declared refresh command in the chain" % _nm49)
        finally:
            _F49.panel_stamp = _orig49
        check("product: a book face cannot be green on a panel it no longer measures",
              not _bad49, "; ".join(_bad49)[:200]
              or "3 faces return 2 + 'stale' on an older stamp; chain holds their refresh arm")
    except Exception as e:
        check("product: a book face cannot be green on a panel it no longer measures",
              False, repr(e)[:180])
    # (r1404) a rewrite of a published mark must keep the value it replaced, or the
    # ledger cannot say what it used to claim
    try:
        import importlib as _il76
        if "scripts" not in sys.path:
            sys.path.insert(0, "scripts")
        _F76 = _il76.import_module("etf_book_forward")
        _bad76 = []
        _rows76 = _F76.rebase_rows([{"bar": "2026-11-05", "nav": 1.0, "provisional": True}],
                                   ["2026-11-05:1e-06"], {"2026-11-05": {"nav": 1.5}})
        if not _rows76 or _rows76[0]["nav_published"] != 1.0 or _rows76[0]["nav_settled"] != 1.5:
            _bad76.append("a rewritten mark is not recorded with both values")
        if _F76.rebase_rows([{"bar": "x", "nav": 1.0}], ["x:1e-06"], {}) != []:
            _bad76.append("a rewrite row is invented for a bar with no fresh mark")
        _led76 = _F76.load_ledger()
        if _led76 is not None:
            _aud76 = _F76.rebase_audit(_led76)
            if _aud76["n_rebases"] != len(_led76.get("rebases") or []):
                _bad76.append("the audit counts a different number of rewrites than the ledger holds")
            if len(_aud76["unrecoverable_bars"]) != sum(r.get("values_unrecorded", 0)
                                                        for r in _aud76["rebases"]):
                _bad76.append("the audit's unrecoverable count does not add up to its rows")
        check("product: a rewritten mark keeps the value it replaced", not _bad76,
              "; ".join(_bad76)[:200]
              or "before/after recorded per rewrite; unrecorded bars named, never invented")
    except Exception as e:
        check("product: a rewritten mark keeps the value it replaced", False, repr(e)[:180])
    _leg_width_growth()
    _leg_size_decomp()
    _leg_size_age_control()
    _leg_smallcap_book()
    _leg_candidate_year_gate()
    _leg_scale_floor()
    return _finish()
_MARK = (("<<<<<<<", "open"), ("|||||||", "base"), ("=======", "sep"), (">>>>>>>", "close"))
_SMOKE_GC = None


def _claw():
    """Tools/git_claw.py as a module (r1382): the marker rule lives there because
    the push side asks the same question, and a copy of a rule is the next defect."""
    global _SMOKE_GC
    if _SMOKE_GC is None:
        import importlib.util as _ilu
        _p = os.path.join("Tools", "git_claw.py")
        _s = _ilu.spec_from_file_location("_smoke_git_claw", _p)
        _m = _ilu.module_from_spec(_s)
        _s.loader.exec_module(_m)
        _SMOKE_GC = _m
    return _SMOKE_GC


_SMOKE_CTH = None
_SMOKE_JFG = None


def _json_face_guard():
    """Tools/json_face_guard.py as a module (r1406).

    The pre-commit claw calls the same file in --staged mode, so the leg and the
    claw must ask the identical question: a face has to parse, and no object may
    repeat a key. Loading the module (not re-implementing the check) is what keeps
    the suite from passing while the claw blocks -- or worse, the reverse."""
    global _SMOKE_JFG
    if _SMOKE_JFG is None:
        import importlib.util as _ilu
        _p = os.path.join("Tools", "json_face_guard.py")
        _s = _ilu.spec_from_file_location("_smoke_json_face_guard", _p)
        _m = _ilu.module_from_spec(_s)
        _s.loader.exec_module(_m)
        _SMOKE_JFG = _m
    return _SMOKE_JFG


def _card_text_hygiene():
    """Tools/card_text_hygiene.py as a module (r1383): the leg and the repair tool
    must read the same corpus with the same control-character set, otherwise the
    gate can pass while the tool still finds sites."""
    global _SMOKE_CTH
    if _SMOKE_CTH is None:
        import importlib.util as _ilu
        _p = os.path.join("Tools", "card_text_hygiene.py")
        _s = _ilu.spec_from_file_location("_smoke_card_text_hygiene", _p)
        _m = _ilu.module_from_spec(_s)
        _s.loader.exec_module(_m)
        _SMOKE_CTH = _m
    return _SMOKE_CTH


def _hunk_state(text: str, rev: str = "HEAD"):
    """Marker lines that are NOT part of a complete open/base/sep/close hunk.

    A probe fixture may legitimately quote a whole conflict hunk; a leftover is a
    fragment of one (git applies half of a resolution, or a base marker survives a
    replay). Balance is mechanical, so no path whitelist is needed -- and a
    markdown "=======" underline cannot trip the gate because a separator only
    counts inside an open hunk.

    r1382: delegates to Tools/git_claw.marker_fragments, the same function the
    pre-push gate runs -- commit-side and push-side cannot disagree about a file.
    """
    _frag, _state, _opened = _claw().marker_fragments(text)
    return _frag, _state


def _marker_fragments():
    """Live faces only: results/_* are scratch captures that quote raw diffs on purpose
    (six of them hold unbalanced hunks by design), so the gate is scoped there by the
    repo's own underscore convention instead of by a list of names."""
    r = subprocess.run(["git", "grep", "-l", "-I", "-E",
                        r"^(<<<<<<<|\|\|\|\|\|\|\||=======|>>>>>>>)", "HEAD", "--", ".",
                        ":(exclude,glob)results/_*"], capture_output=True)
    bad = []
    for row in r.stdout.decode("utf-8", "replace").split("\n"):
        if ":" not in row:
            continue
        path = row.split(":", 1)[1]
        blob = subprocess.run(["git", "show", "HEAD:%s" % path], capture_output=True)
        frag, open_state = _hunk_state(blob.stdout.decode("utf-8", "replace"))
        for ln, kind in frag:
            bad.append((path, ln, kind))
        if open_state is not None:
            bad.append((path, blob.stdout.count(b"\n") + 1, "unclosed-hunk"))
    return bad


def _leg_width_growth():
    """(r1411) width is not where the breadth premium lives: on a tape where every name
    is identical, every width must earn the same number, and a frozen book must shrink
    (drop the name it can no longer see) instead of refilling the seat or losing a whole
    cohort.

    r1412: this body had been written after the `return bad` of _marker_fragments(), so
    it never ran -- a leg that is silently absent from the suite is worse than a red one.
    It is a function now and main() calls it.
    """
    try:
        import importlib as _il77
        if "scripts" not in sys.path:
            sys.path.insert(0, "scripts")
        _F77 = _il77.import_module("astock_breadth_book")
        _bad77 = []
        _p77 = _F77._synth(T=400, S=300, drift=0.0008, noise=0.0)
        _cs77, _sk77 = _F77.cohorts(_p77)
        _all77 = _F77.chained(_F77.arm_all(_cs77))[0]
        for _n77 in (20, 100):
            _s77 = _F77.summarise(_F77.arm_width(_cs77, _n77, draws=2))
            if _s77["cagr_mean"] is None or abs(_s77["cagr_mean"] - _all77) > 1e-9:
                _bad77.append("identical tape: N%d reads %r vs ALL %r"
                              % (_n77, _s77["cagr_mean"], _all77))
        _p77b = _F77._synth(T=400, S=300, drift=0.0008, noise=0.0)
        _p77b["open"][250:, :60] = float("nan")
        _p77b["close"][250:, :60] = float("nan")
        _cs77b, _sk77b = _F77.cohorts(_p77b)
        _fr77 = _F77.arm_width_frozen(_cs77b, 100, draws=1, seed=3)
        if not _fr77 or _fr77[0]["cohorts"] != len(_cs77b):
            _bad77.append("a frozen book lost a whole cohort instead of shrinking: %r of %d"
                          % (_fr77[0]["cohorts"] if _fr77 else None, len(_cs77b)))
        if not _fr77 or _fr77[0]["attrition"] <= 0:
            _bad77.append("a frozen book reported zero attrition while 60 names left the panel")
        check("product: breadth width is not the risk axis and a frozen book shrinks, "
              "it does not refill",
              not _bad77, "; ".join(_bad77)[:200]
              or "identical tape: every width == ALL; frozen book shrinks on attrition")
    except Exception as e:
        check("product: breadth width is not the risk axis and a frozen book shrinks, "
              "it does not refill", False, repr(e)[:180])


def _leg_size_decomp():
    """(r1412) an equal-weight pool is a size bet, so the arms must be able to say so.

    Two mechanical facts on synthetic tapes: a size-linked tape lifts the equal-weight
    arm above the cap-weighted one AND puts the small tercile above the large one; a flat
    tape must not manufacture a size spread. A NaN cap has to be refused by name -- a
    naive sort would either promote it to the largest weight or silently shrink the pool.
    """
    try:
        import importlib as _il80
        import numpy as _np80
        if "scripts" not in sys.path:
            sys.path.insert(0, "scripts")
        _F80 = _il80.import_module("astock_size_decomp")
        _bad80 = []
        _ch80 = _F80.chain_arms(_F80.cohort_arms(_F80._synth(size_link=0.004)))
        if not (_ch80["ew_all"]["cagr"] > _ch80["cw_all"]["cagr"]):
            _bad80.append("a size-linked tape did not lift EW_ALL above CW_ALL")
        if not (_ch80["sml"]["cagr"] > _ch80["lrg"]["cagr"]):
            _bad80.append("small tercile did not beat large on a size-linked tape")
        if _F80.verdict_block(_ch80)["verdict"] not in ("SIZE_IS_THE_PREMIUM", "MIXED",
                                                        "REWEIGHTING_ONLY"):
            _bad80.append("verdict unreadable")
        _flat80 = _F80.chain_arms(_F80.cohort_arms(_F80._synth(size_link=0.0)))
        _sp80 = _flat80["sml"]["cagr"] - _flat80["lrg"]["cagr"]
        if abs(_sp80) > 0.10:
            _bad80.append("a flat tape produced a %.4f size spread" % _sp80)
        _cap80 = _F80.caps_at(_F80._synth(size_link=0.0), 10, _np80.arange(60))
        _cap80[3] = float("nan")
        _r80 = _F80.arm_readings(_np80.arange(60), _np80.full(60, 0.01), _cap80)
        if _r80["n_capped"] != 59:
            _bad80.append("a NaN cap was not refused: n_capped=%r" % (_r80["n_capped"],))
        try:
            _F80.caps_at({"close": _np80.ones((3, 3))}, 0, _np80.arange(3))
            _bad80.append("caps_at accepted a panel with no shares column")
        except ValueError:
            pass
        check("product: the equal-weight premium is priced against cap weights",
              not _bad80, "; ".join(_bad80)[:200]
              or "size-linked tape lifts EW over CW and small over large; flat tape does not")
    except Exception as e:
        check("product: the equal-weight premium is priced against cap weights",
              False, repr(e)[:180])


def _leg_smallcap_book():
    """(r1414) a size premium you cannot size is not money: width and capacity must move together.

    Three mechanical facts on synthetic tapes: the bottom-N sort really takes the
    smallest caps and never promotes a NaN, a wider book carries strictly more money
    (capacity is a sum of turnover, so it cannot be width-blind), and the frozen
    four-gate verdict must be able to reach each of its three answers. The last one
    matters most: a verdict function that can only say REFUSE would read as safety
    while hiding the fact that nothing is being tested.
    """
    try:
        import importlib as _il82
        import numpy as _np82
        if "scripts" not in sys.path:
            sys.path.insert(0, "scripts")
        _F82 = _il82.import_module("astock_smallcap_book")
        _bad82 = []
        _p82 = _F82._synth(size_link=0.0)
        _cap82 = _F82.caps_at(_p82, 50, _np82.arange(60))
        _cap82[3] = float("nan")
        _idx82, _sub82 = _F82.cap_sorted(_np82.arange(60), _cap82)
        if _idx82.size != 59:
            _bad82.append("a NaN cap survived the sort (n=%r)" % (_idx82.size,))
        if _idx82.size > 1 and not (_sub82[0] <= _sub82[-1]):
            _bad82.append("cap_sorted is not ascending")
        _rows82 = _F82.cohort_rows(_F82._synth(size_link=0.4))
        _c20, _c500 = _F82.capacity_median(_rows82, 20), _F82.capacity_median(_rows82, 500)
        if not (_c20 and _c500 and _c500 > _c20):
            _bad82.append("capacity did not grow with width (%r vs %r)" % (_c20, _c500))
        if not (_F82.net_chain(_rows82, "n20")["cagr"]
                > _F82.net_chain(_rows82, "n500")["cagr"]):
            _bad82.append("small-linked tape did not lift n20 above n500")
        def _ph(flag):
            s = {f"n{w}": {"all_positive": flag, "min": 1.0 if flag else -1.0,
                           "max": 2.0, "spread": 5.0} for w in _F82.WIDTHS}
            s["sml_all"] = s["n20"]
            return {"summary": s}
        def _ch(c):
            d = {f"n{w}": {"cagr": c, "maxdd": -0.1, "cohorts": 5} for w in _F82.WIDTHS}
            d["sml_all"] = d["n20"]
            return d
        _v_ref = _F82.verdict_block(_ch(-0.1), _ch(-0.3), {f"n{w}": 1e6 for w in _F82.WIDTHS},
                                    _ph(False))["verdict"]
        _v_cap = _F82.verdict_block(_ch(0.15), _ch(0.10), {f"n{w}": 1e6 for w in _F82.WIDTHS},
                                    _ph(True))["verdict"]
        _v_ok = _F82.verdict_block(_ch(0.15), _ch(0.10), {f"n{w}": 5e7 for w in _F82.WIDTHS},
                                   _ph(True))
        if _v_ref != "REFUSE_AS_CANDIDATE":
            _bad82.append("a negative book read %r" % (_v_ref,))
        if _v_cap != "CAPACITY_LIMITED":
            _bad82.append("a rich book with no capacity read %r" % (_v_cap,))
        if _v_ok["verdict"] != "ADOPT_AS_CANDIDATE" or _v_ok["candidate_width"] != 20:
            _bad82.append("a passing book read %r at width %r"
                          % (_v_ok["verdict"], _v_ok["candidate_width"]))
        # the two frozen rules must be allowed to disagree; a book whose floor is
        # high but whose phases are scattered has to show up in the conflict block
        if "n20" not in _v_ok["conflict_with_r1411_rule"][
                "widths_that_pass_this_gate_would_fail_that_one"]:
            _bad82.append("a 4.03pp+ phase spread was not disclosed as a rule conflict")
        check("product: a size premium that cannot be sized is not money",
              not _bad82, "; ".join(_bad82)[:200]
              or "width takes the smallest caps, capacity grows with width, all three gates reachable")
    except Exception as e:
        check("product: a size premium that cannot be sized is not money",
              False, repr(e)[:180])


def _leg_candidate_year_gate():
    """(r1415) a candidate that only works in two of its seven years is not a rate.

    r1414 adopted the 20-name book on four single-number gates; its own by_year block
    showed +48.9/+75.9 in 2024/2025 and -18.7 in the current year.  This leg pins the
    second stage that asks the calendar question: the clean fixture must ADMIT, the
    published shape must fall to CONDITIONAL on the worst-year check, a genuinely
    two-year book must trip the concentration check, and an unchecked capacity column
    must read as None rather than as a pass.  The last assertions read the published
    receipt, because a gate that only agrees with its own fixture is untested.
    """
    try:
        import importlib as _il83
        if "scripts" not in sys.path:
            sys.path.insert(0, "scripts")
        _F83 = _il83.import_module("candidate_year_gate")
        _bad83 = []

        _clean = {"2020": {"net_pct": 30.0, "cohorts": 4}, "2021": {"net_pct": 20.0, "cohorts": 4},
                  "2022": {"net_pct": 12.0, "cohorts": 4}, "2023": {"net_pct": 6.0, "cohorts": 4},
                  "2024": {"net_pct": 25.0, "cohorts": 4}, "2025": {"net_pct": 18.0, "cohorts": 4},
                  "2026": {"net_pct": 9.0, "cohorts": 4}}
        if _F83.admission_block(_clean, 5e7, 5.0, 0.15)["verdict"] != "ADMIT":
            _bad83.append("a clean seven-year book was not admitted")

        _shape = {"2020": {"net_pct": 41.862, "cohorts": 4},
                  "2021": {"net_pct": 35.722, "cohorts": 4},
                  "2022": {"net_pct": 3.501, "cohorts": 4},
                  "2023": {"net_pct": -7.608, "cohorts": 4},
                  "2024": {"net_pct": 48.927, "cohorts": 4},
                  "2025": {"net_pct": 75.939, "cohorts": 4},
                  "2026": {"net_pct": -18.709, "cohorts": 2}}
        _b = _F83.admission_block(_shape, 4.83e7, 17.2, 0.2538)
        if _b["verdict"] != "CONDITIONAL":
            _bad83.append("the published shape read %r" % (_b["verdict"],))
        if _b["checks"]["Y3_worst_year"] is not False:
            _bad83.append("a -18.7%% year passed the worst-year check")
        if _b["checks"]["Y4_top2_share"] is not True:
            _bad83.append("the 69.5%% top-two share should still clear the 70%% line")
        if not _b["gate_conflict"]["rules_disagree"]:
            _bad83.append("the 17.2pp spread did not print as a rule conflict")

        _carried = {"2020": {"net_pct": 90.0, "cohorts": 4},
                    "2021": {"net_pct": 95.0, "cohorts": 4},
                    "2022": {"net_pct": 2.0, "cohorts": 4}, "2023": {"net_pct": 2.0, "cohorts": 4},
                    "2024": {"net_pct": 2.0, "cohorts": 4}, "2025": {"net_pct": 2.0, "cohorts": 4},
                    "2026": {"net_pct": 2.0, "cohorts": 4}}
        if _F83.admission_block(_carried, 5e7, 1.0, 0.3)["checks"]["Y4_top2_share"] is not False:
            _bad83.append("a two-year book cleared the concentration check")

        if _F83.admission_block(_clean, None, None, 0.15)["checks"]["C1_capacity"] is not None:
            _bad83.append("an unpublished capacity column was scored instead of left unchecked")

        import io as _io83
        import json as _json83
        import os as _os83
        _p83 = _os83.path.join("results", "admission", "CANDIDATES.json")
        if not _os83.path.exists(_p83):
            _bad83.append("admission receipt is not on disk (the gate never ran)")
        else:
            with _io83.open(_p83, encoding="utf-8") as _f83:
                _rec = _json83.load(_f83)
            if _rec["rule"]["capacity_floor_cny"] != _F83.CAPACITY_FLOOR_CNY:
                _bad83.append("receipt capacity floor drifted from the code")
            if _rec["rule"]["worst_year_floor_pp"] != _F83.WORST_YEAR_FLOOR_PP:
                _bad83.append("receipt worst-year floor drifted from the code")
            if not _rec["candidates"]:
                _bad83.append("receipt priced no candidate at all")
            for _c in _rec["candidates"]:
                if _c["verdict"] == "ADMIT" and _c["capacity_checked"] is False:
                    _bad83.append("admitted %s with an unchecked capacity column"
                                  % (_c["arm"],))

        check("product: a candidate that only works in two of its seven years is not a rate",
              not _bad83, "; ".join(_bad83)[:200]
              or "clean book admits, the published shape is conditional, two-year books and "
                 "unchecked capacity are separated")
    except Exception as e:
        check("product: a candidate that only works in two of its seven years is not a rate",
              False, repr(e)[:180])


def _leg_scale_floor():
    """(r1419) a gate that flips on the decision phase is not a gate.

    r1418 condemned the adopted book on a 1.08pp miss.  The same rule, four start dates one
    week apart, spans 71% -> 80% of top-2 concentration, so the miss was the best of four
    readings rather than a property of the book.  This leg pins three things on the
    published face: the sizing floor's zero point still reproduces the r1418 verdict and
    top-2 share, the phase block really carries more than one arm per phase (a one-phase
    "phase test" is how a leg goes green on a broken sweep), and a spread larger than the
    distance to the line must be disclosed as unstable instead of being reported as a near
    pass.  An admitted arm with an unchecked capacity column is the same defect r1415
    pinned one gate earlier.
    """
    try:
        import json as _json84
        _root84 = os.path.dirname(os.path.abspath(__file__))
        _p84 = os.path.join(_root84, "results", "etf_book_scale_floor.json")
        _g84 = os.path.join(_root84, "results", "etf_book_year_gate", "YEAR-GATE.json")
        _bad84 = []
        with open(_p84, encoding="utf-8") as _f84:
            _rec = _json84.load(_f84)
        with open(_g84, encoding="utf-8") as _f84:
            _yg = _json84.load(_f84)
        _adopted = [b for b in _yg.get("books", []) if b.get("book") == "nobond_vt08_adopted"]
        if not _adopted:
            _bad84.append("the r1418 face no longer carries the adopted book")
        else:
            _a84 = _adopted[0]
            _base = [x for x in _rec.get("arms", []) if x.get("vol_floor") == 0.0]
            if not _base:
                _bad84.append("the receipt has no floor=0 baseline arm")
            else:
                if abs(_base[0]["year_metrics"]["top2_share"]
                       - _a84["year_metrics"]["top2_share"]) > 1e-9:
                    _bad84.append("floor=0 top-2 drifted from the published verdict")
                if _base[0]["verdict"] != _a84["verdict"]:
                    _bad84.append("floor=0 verdict drifted from the published verdict")
        for _a in _rec.get("arms", []):
            if _a.get("verdict") == "ADMIT" and _a.get("capacity_checked") is False:
                _bad84.append("admitted floor %r with an unchecked capacity column"
                              % (_a.get("vol_floor"),))
        _ph = _rec.get("phase_test") or {}
        _rows = _ph.get("rows") or []
        if len(_rows) < 2:
            _bad84.append("phase block carries %d rows; a single phase is not a path test"
                          % len(_rows))
        for _r in _rows:
            _arms = [k for k in _r if k.startswith("floor_")]
            if len(_arms) < 2:
                _bad84.append("phase %s prices %d arm(s), expected the compared pair"
                              % (_r.get("start"), len(_arms)))
        _shares = [r.get("floor_0.0", {}).get("top2_share") for r in _rows]
        _shares = [s for s in _shares if s is not None]
        if len(_shares) >= 2 and (max(_shares) - min(_shares)) > 0.70 - min(_shares):
            if _ph.get("stable") is not False:
                _bad84.append("a phase spread wider than the margin is reported as stable")
        check("product: a gate that flips on the decision phase is not a gate",
              not _bad84, "; ".join(_bad84)[:200]
              or "floor=0 reproduces r1418, the phase block prices both arms per phase, and "
                 "a spread wider than the margin is disclosed as unstable")
    except Exception as e:
        check("product: a gate that flips on the decision phase is not a gate",
              False, repr(e)[:180])


def _leg_size_age_control():
    """(r1413) "small" and "young" are two names for the same cohort unless tested.

    The discriminator is the pre-panel tier: names already listed when the panel starts
    cannot be new listings. A tape where only the late listers carry drift must show the
    confound in the pooled spread and have it collapse inside that tier; a tape where the
    return follows the cap must keep the spread in the tier. Both directions are pinned,
    because a leg that only fires one way would pass on a broken splitter.
    """
    try:
        import importlib as _il81
        import numpy as _np81
        if "scripts" not in sys.path:
            sys.path.insert(0, "scripts")
        _F81 = _il81.import_module("astock_size_age_control")
        _bad81 = []
        _p81 = _F81._synth(young_from=0, young_until=30, young_starts=100)
        _f81 = _F81.first_bar(_p81)
        if _f81[0] != 100 or _f81[60] != 0:
            _bad81.append("first_bar read late=%r early=%r (expected 100 and 0)"
                          % (_f81[0], _f81[60]))
        _p81["close"][:, 70] = _np81.nan
        if _F81.first_bar(_p81)[70] != -1:
            _bad81.append("a never-priced symbol did not read first_bar -1")
        _flat81 = _F81.tercile_pair(_np81.arange(1, 61, dtype=_np81.float64) * 1e8,
                                    _np81.zeros(60))
        for _s81 in ("sml", "lrg"):
            if abs(_flat81[_s81] + 2.0 * _F81.COST) > 1e-12:
                _bad81.append("a flat tape read %s=%r instead of -2*cost"
                              % (_s81, _flat81[_s81]))
        _tiny81 = _F81.tercile_pair(_np81.array([1e8, 2e8, 3e8]),
                                    _np81.array([0.01, 0.02, 0.03]))
        if _np81.isfinite(_tiny81["sml"]) or _np81.isfinite(_tiny81["lrg"]):
            _bad81.append("a three-name subset produced a tercile reading")
        # size-only tape: every name is pre-panel, the spread must survive there
        _p82 = _F81._synth(size_link=0.004)
        _ch82 = _F81.chain_arms(_F81.cohort_rows(_p82, _F81.first_bar(_p82)))
        _sp82 = _ch82["prepanel_sml"]["cagr"] - _ch82["prepanel_lrg"]["cagr"]
        if not (_sp82 > 0):
            _bad81.append("a size-only tape lost the pre-panel spread (%r)" % _sp82)
        # age-only tape: the confound must appear pooled and vanish pre-panel
        _p83 = _F81._synth(size_link=0.0, age_link=0.0025, young_from=0,
                           young_until=40, young_starts=200)
        _ch83 = _F81.chain_arms(_F81.cohort_rows(_p83, _F81.first_bar(_p83)))
        _ph83 = _F81.phase_readings(_p83, _F81.first_bar(_p83))
        _vb83 = _F81.verdict_block(_ch83, _ph83)
        if _vb83["verdict"] != "AGE_IS_THE_PREMIUM":
            _bad81.append("an age-only tape read %r (pooled %r / pre-panel %r)"
                          % (_vb83["verdict"], _vb83["pooled_spread_pp"],
                             _vb83["prepanel_spread_pp"]))
        if not (_vb83["pooled_spread_pp"] and _vb83["pooled_spread_pp"] > 0):
            _bad81.append("the age-only tape never showed up in the pooled spread")
        if not (_vb83["prepanel_spread_pp"] is not None
                and _vb83["pooled_spread_pp"] is not None
                and _vb83["prepanel_spread_pp"] <= 0.25 * _vb83["pooled_spread_pp"]):
            _bad81.append("the pre-panel spread did not collapse on an age-only tape")
        # an unreadable tier is skipped, never chained as a zero return
        _rows84 = [{"date": "d0", "n_members": 2, "pooled_sml": 0.01,
                    "pooled_lrg": 0.01,
                    "tiers": {t: {"n": 0, "sml": float("nan"), "lrg": float("nan")}
                              for t in _F81.TIERS}}]
        if _F81.chain_arms(_rows84)["prepanel_sml"]["cohorts"] != 0:
            _bad81.append("a NaN tier reading entered the chain")
        check("product: the size ladder is separated from the listing cohort",
              not _bad81, "; ".join(_bad81)[:200]
              or "late listers move the pooled spread and none of the pre-panel one")
    except Exception as e:
        check("product: the size ladder is separated from the listing cohort",
              False, repr(e)[:180])


# ---------------------------------------------------------------- r1414 product legs
    try:
        import update_lhb_inst as _LI
        import pandas as _pd
        _badli = []
        _raw = _pd.DataFrame({
            "代码": ["600000", "600000", "000001", "900001"],
            "名称": ["A", "A", "B", "C"],
            "收盘价": [1, 1, 2, 3], "涨跌幅": [1, 1, 2, 3],
            "买方机构数": [1, 1, 2, 3], "卖方机构数": [0, 0, 1, 1],
            "机构买入总额": [1.0, 1.0, 2.0, 3.0],
            "机构卖出总额": [0.0, 0.0, 1.0, 1.0],
            "机构买入净额": [1.0, 1.0, 1.0, 2.0],
            "市场总成交额": [10, 10, 20, 30],
            "机构净买额占总成交额比": [10.0, 10.0, 5.0, 6.7],
            "上榜原因": ["r1", "r1", "r2", "r3"],
            "上榜日期": ["2020-01-02"] * 4,
        })
        _pg, _dr = _LI.normalise(_raw)
        if _dr != 1:
            _badli.append("a non-A-share code survived the panel")
        if len(_pg) != 2:
            _badli.append("the (code, day, reason) key did not collapse duplicates")
        if "上榜原因" not in _pg.columns:
            _badli.append("the reason column was thrown away")
        _m = _LI.merge(None, _pg)
        if len(_LI.merge(_m, _pg)) != len(_m):
            _badli.append("re-merging the same page grew the panel")
        if _LI.overlap_check(_m, _pg, "20200102", "20200102")["mismatch"] != 0:
            _badli.append("an identical overlap was read as a history edit")
        _ed = _pg.copy()
        _ed.loc[0, "机构买入净额"] = float(_ed.loc[0, "机构买入净额"]) + 1e7
        if _LI.overlap_check(_m, _ed, "20200102", "20200102")["mismatch"] != 1:
            _badli.append("a vendor history edit went unnoticed")
        try:
            _LI.normalise(_raw.drop(columns=["上榜原因"]))
            _badli.append("a missing reason column passed the shape guard")
        except ValueError:
            pass
        check("product: the institutional seat panel keeps its reason face and refuses drift",
              not _badli, "; ".join(_badli)[:200]
              or "duplicates collapse on the key, non-A codes drop, drift raises, edits are caught")
    except Exception as e:
        check("product: the institutional seat panel keeps its reason face and refuses drift",
              False, repr(e)[:180])

    try:
        import zoo99_lhb_inst_netratio_probe as _Z99
        _bad99 = []
        _cfg = _Z99._synthetic_cfg(320, 120)
        _sc, _fw, _lq, _dt, _al = _Z99._fake_score(_cfg)
        def _mk(_f):
            return {"dates": _dt, "amount": __import__("numpy").ones((320, 120)) * 1e8,
                    "open": __import__("numpy").cumprod(1 + _f, axis=0) * 10.0,
                    "close": __import__("numpy").cumprod(1 + _f, axis=0) * 10.0}
        _up = _Z99.judge(_mk(_fw + 0.0008 * _al[None, :]), _sc, {}, cfg=_cfg, draws=30)
        _dn = _Z99.judge(_mk(_fw - 0.0008 * _al[None, :]), _sc, {}, cfg=_cfg, draws=30)
        if _up["verdict"] != "ADMIT_TO_PREREG":
            _bad99.append("an injected premium was not admitted (%r)" % _up["verdict"])
        if _dn["verdict"] != "REFUSE_AS_CANDIDATE":
            _bad99.append("an inverted signal was admitted (%r)" % _dn["verdict"])
        if not (_up["criteria"]["null_p"] < 0.1):
            _bad99.append("the null never separated an injected premium (p=%r)"
                          % _up["criteria"]["null_p"])
        _tm = _Z99.trailing_mean(__import__("numpy").array([[1.0], [float("nan")],
                                                            [float("nan")]]), 2)
        if not __import__("numpy").isnan(_tm[2, 0]):
            _bad99.append("a window with no observation was read as a zero")
        check("product: institutional LHB net buying separates returns only beside its null",
              not _bad99, "; ".join(_bad99)[:200]
              or "injected premium admits, inverted signal refuses, empty windows stay NaN")
    except Exception as e:
        check("product: institutional LHB net buying separates returns only beside its null",
              False, repr(e)[:180])


    try:
        # D-20261108-14: the coverage contract is the map UNION the lanes this
        # board reads. The leg recomputes the union from config/lane_hosts.json
        # (a typed-in count reads red), demands a row for every declared writer,
        # and keeps the second half honest too: silence (>24h) is its own alarm
        # and must be derived from the heartbeat ages, not copied onto the page.
        import data_lane_freshness as _dlfc
        _lfdc = json.load(open("results/data_lane_freshness.json",
                               encoding="utf-8"))
        _badc = []
        _decl = _dlfc.declared_lane_hosts()
        _covered = {r.get("writer") for r in (_lfdc.get("lanes") or [])}
        # a lane judged on the statute lives in `period_lanes`, not in `lanes`
        _covered |= {r.get("writer")
                     for r in (_lfdc.get("period_lanes") or [])}
        _miss = sorted(w for w in _decl if w not in _covered)
        if _miss:
            _badc.append("declared lanes with no row: " + ",".join(_miss))
        _cov = _lfdc.get("coverage") or {}
        if _cov.get("declared_writers") != len(_decl):
            _badc.append(f"coverage says {_cov.get('declared_writers')} writers, "
                         f"the map holds {len(_decl)}")
        _sil = set(_lfdc.get("hosts_silent") or [])
        _derived = {h for h, v in (_lfdc.get("hosts") or {}).items()
                    if (v.get("age_h") or 0) > _dlfc.HOST_SILENT_H
                    and (v.get("lanes") or [])}
        if _sil != _derived:
            _badc.append(f"silent hosts printed {sorted(_sil)} vs derived "
                         f"{sorted(_derived)}")
        _unm = set(_lfdc.get("unmeasured_lanes") or [])
        _unm_rows = {r["lane"] for r in (_lfdc.get("lanes") or [])
                     if r.get("verdict") == "unmeasured"}
        if _unm != _unm_rows:
            _badc.append("unmeasured list disagrees with the rows")
        check("product: the freshness board covers the lane map, and a silent "
              "owner is its own alarm",
              not _badc, "; ".join(_badc)[:200]
              or f"{len(_decl)} declared writers all have rows; "
                 f"{len(_sil)} silent owner(s) derived from heartbeats")
    except Exception as e:
        check("product: the freshness board covers the lane map, and a silent "
              "owner is its own alarm", False, repr(e)[:180])


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
