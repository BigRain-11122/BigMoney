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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RESULTS = []


def check(name: str, ok: bool, detail: str = ""):
    RESULTS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail else ""))


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

    # T+1 guard: no trade may be opened and closed on the same date
    opens = {t["symbol"]: t["date"] for t in r1["trades"]}
    same_day = [t for t in r1["trades"] if opens.get(t["symbol"]) == t["date"]
                and not is_t0(t["symbol"]) and t["hold_days"] <= 1]
    check("engine: T+1 respected", len(same_day) == 0,
          f"{len(r1['trades'])} trades checked, 0 same-day roundtrips")

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
    for _name, _args in (("daily", ["--selftest"]), ("lhb", ["selftest"])):
        _label = f"updater: update_{_name} selftest (exit-code contract)"
        try:
            _r = _sp.run([sys.executable, f"scripts/update_{_name}.py", *_args],
                         capture_output=True, text=True, timeout=180)
            _tail = ((_r.stdout or _r.stderr).strip().splitlines() or ["no output"])[-1]
            check(_label, _r.returncode == 0, f"exit={_r.returncode} | {_tail[:80]}")
        except Exception as e:
            check(_label, False, str(e))
    # heartbeat epoch fields (T-04 F5): heartbeat_epoch_utc int + clock_read
    # ISO string on this machine's heartbeat file -- clock drift detectable.
    try:
        _mid = json.load(open("fleet/machine.json", encoding="utf-8"))["machine_id"]
        _hb = json.load(open(f"fleet/machines/{_mid}.json", encoding="utf-8"))
        _ok_hb = (isinstance(_hb.get("heartbeat_epoch_utc"), int)
                  and isinstance(_hb.get("clock_read"), str)
                  and "T" in _hb["clock_read"])
        check("fleet: heartbeat epoch fields present", _ok_hb,
              f"{_mid}: epoch={_hb.get('heartbeat_epoch_utc')} "
              f"clock={_hb.get('clock_read')}")
    except Exception as e:
        check("fleet: heartbeat epoch fields present", False, str(e))

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
