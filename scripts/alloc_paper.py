"""ALLOC-* paper account forward-accrual leg (T-2026-09-25-66 s1 · r188 ptr-3).

7 accounts mirror the frozen s2 cells 1:1 (P1/P2/P3/P3B/P4/P5/P6), initial
1,000,000 CNY each (ALLOCATION_RESEARCH.md sec.4). Engine = import alloc_backtest
verbatim (simulate/weights/rules, zero new judgment); canonical cost face =
side_cost_v2 v2_main (identical to s2 cells judgment face). Window = bars beyond
the frozen s2 cutoff (alloc_backtest.CUTOFF); inception trade on the first
forward bar at its close (engine convention, inherited).

Deterministic full-forward recompute per run (aggressive_lab paper precedent):
pure function of the panel, no wall-clock fields, byte-identical re-run when no
new bar. exit 0 = normal/no-op; 2 = mechanical failure. selftest = hermetic.
Data faces: in-repo data/daily + pinned P5_SLOT (510880) + Money0923 repo csv;
repo file tail < forward days -> forward cash legs ffill last rate (engine
load_repo convention, disclosed in output.data_quality).
Lane: bm-b only (R31, MSG-20260925-2330-bm-a crash disclosure) -- non-owner
machines stdout-only no-op exit 0 until the pinned P5 slot is distributed to
all machines via fleet/TRANSFER.md (byte-identical pinned original, not fresh
pull: mirror 1:1 discipline).
"""

import os
import sys
import json

import numpy as np
import pandas as pd

import alloc_backtest as ab

OUT_DIR = os.path.join("results", "alloc_paper")
SCHEMA = "alloc_paper_v1"

MACHINE_JSON = os.path.join("fleet", "machine.json")
LANE_OWNER = "bm-b"   # T-66 claimed by bm-b -> lane owner per R31 (MSG-20260925-2330-bm-a)


def _lane_owner_id(path=MACHINE_JSON) -> str:
    """本机 machine_id；读不到=空串（按非 owner 处理，防御性降级）。"""
    try:
        with open(path, encoding="utf-8-sig") as f:      # BOM-tolerant (bm-c r6 law)
            return str(json.load(f).get("machine_id") or "")
    except Exception:
        return ""

# Mirrors cmd_run cells_spec exactly (mode/p2 wiring frozen with s2 batch).
ARMS = [
    ("ALLOC-P1", lambda: ab.WEIGHTS["ALLOC-P1"], "monthly", False),
    ("ALLOC-P2", None, "monthly", True),
    ("ALLOC-P3", lambda: ab.WEIGHTS["ALLOC-P3"], "monthly", False),
    ("ALLOC-P3B", lambda: ab.WEIGHTS["ALLOC-P3B"], "daily-threshold", False),
    ("ALLOC-P4", lambda: ab.WEIGHTS["ALLOC-P4"], "monthly", False),
    ("ALLOC-P5", lambda: ab.WEIGHTS["ALLOC-P5"], "monthly", False),
    ("ALLOC-P6", lambda: ab.WEIGHTS["ALLOC-P6"], "monthly", False),
]
SYMBOLS = sorted({s for arm in ARMS if arm[1] is not None
                  for s in arm[1]() if s != "CASH"}
                 | set(ab.P2_POOL) | set(ab.P5_SYMS))


def _load_full_csv(path):
    """Like ab.load_symbol_csv but WITHOUT the s2 cutoff lock (forward face)."""
    df = pd.read_csv(path)
    df["date"] = df["date"].astype(str)
    return df.set_index("date")


def _load_panel_forward(symbols):
    px, amt, raw = {}, {}, {}
    for sym in symbols:
        path = (ab.P5_SLOT if sym == "510880" and os.path.exists(ab.P5_SLOT)
                else os.path.join(ab.DATA, f"{sym}.csv"))
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        df = _load_full_csv(path)
        raw[sym] = df["close"]
        px[sym] = df["close"]
        amt[sym] = df["amount"]
    panel = pd.DataFrame(px).sort_index()
    panel = panel[panel.index >= ab.START]
    amounts = pd.DataFrame(amt).reindex(panel.index)
    adv = {sym: amounts[sym].rolling(20).mean() for sym in symbols}
    raw_panel = pd.DataFrame(raw).reindex(panel.index)
    return panel, adv, raw_panel


def _load_repo_forward(panel_index):
    repo = pd.read_csv(ab.REPO)
    repo["date"] = repo["date"].astype(str)
    rs = repo.set_index("date")["rate"].astype(float)
    daily = rs / 100.0 / 252.0
    tail_date = rs.index.max()
    re = daily.reindex(panel_index).ffill().fillna(0.0)
    ffill_days = [d for d in panel_index if d > tail_date]
    return re, tail_date, ffill_days


def _forward_start(dates, cutoff):
    for i, d in enumerate(dates):
        if d > cutoff:
            return i
    return None


def _account_output(name, weights, mode, p2, res, dates, start_idx,
                    raw_panel, repo_tail, repo_ffill_days, stale_legs):
    eq = res["eq"]
    nav_series = [[d, ab._r6(float(v))] for d, v in eq.items()]
    out = {
        "schema": SCHEMA,
        "account": name,
        "frozen_ref": "ALLOC_LINE_S2_PREREG.md sec.3 (s2 cells 1:1)",
        "engine_ref": "scripts/alloc_backtest.py simulate (import reuse)",
        "cutoff_frozen": ab.CUTOFF,
        "inception_date": dates[start_idx],
        "capital_initial_cny": ab.CAPITAL,
        "cost_face": "v2_main (side_cost_v2, engine default = s2 canonical)",
        "mode": mode,
        "p2": p2,
        "weights_declared": (ab.P2_RULE_LABEL if p2 else weights),
        "p2_inception_note": ("EW warmup at inception per engine convention; "
                              "first month-first applies rolling-126d inv-vol")
                              if p2 else None,
        "nav_series": nav_series,
        "latest_nav_cny": ab._r6(float(eq.iloc[-1])),
        "n_bars": int(len(eq)),
        "n_trades": int(res["trades"]),
        "total_cost_cny": ab._r6(res["total_cost"]),
        "turnover_cny": ab._r6(res["turnover"]),
        "commission_floor_hits": int(res["comm_floor_hits"]),
        "fill_cap_refusals": int(res["fill_refusals"]),
        "data_quality": {
            "stale_leg_days": stale_legs,
            "repo_tail_date": repo_tail,
            "repo_ffill_forward_days": len(repo_ffill_days),
        },
    }
    return out


def _write_if_changed(path, obj):
    data = json.dumps(obj, ensure_ascii=False, indent=1)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            if fh.read() == data:
                return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(data)
    return True


def _stale_leg_days(sym, raw_series, dates, start_idx):
    fwd = dates[start_idx:]
    return int(sum(1 for d in fwd
                   if d in raw_series.index and pd.isna(raw_series.loc[d])))


def run_paper():
    sys.stdout.reconfigure(encoding="utf-8")
    owner = _lane_owner_id()
    if owner != LANE_OWNER:
        # R31 lane guard (MSG-2330, fund_premium precedent): stdout-only, zero
        # shared-state writes; non-owner machines must not hit the bm-b-local
        # pinned P5 slot face at all.
        print(f"no-op: alloc_paper lane owned by {LANE_OWNER}, not this machine ({owner or '?'})")
        return 0
    try:
        panel, adv, raw_panel = _load_panel_forward(SYMBOLS)
    except FileNotFoundError as e:
        # fail-closed (MSG-2330 opt-3): declared exit-2 contract, not raw traceback
        print(f"alloc_paper: mechanical failure, member csv missing: {e} "
              f"(exit 2 honest; P5 slot distribution via TRANSFER.md pending)")
        return 2
    dates = list(panel.index)
    start_idx = _forward_start(dates, ab.CUTOFF)
    if start_idx is None:
        print("no forward bar beyond cutoff", ab.CUTOFF, "-> no-op")
        return 0
    prices = {s: panel[s].ffill().tolist() for s in SYMBOLS}
    adv20_map = {s: adv[s].tolist() for s in SYMBOLS}
    cash_ret, repo_tail, repo_ffill_days = _load_repo_forward(panel.index)
    cash_ret = cash_ret.tolist()
    # disclosure face: count only accrual-window days inheriting the tail rate
    repo_ffill_days = [d for d in repo_ffill_days if d >= dates[start_idx]]

    p5_present = os.path.exists(ab.P5_SLOT)
    written = 0
    for name, wfn, mode, p2 in ARMS:
        if name == "ALLOC-P5" and not p5_present:
            print("ALLOC-P5 skipped: P5 ext-slot missing (honest, disclosed)")
            continue
        weights = None if p2 else wfn()
        syms = (list(ab.P2_POOL) if p2
                else [s for s in weights if s != "CASH"])
        stale = {s: _stale_leg_days(s, raw_panel[s], dates, start_idx)
                 for s in syms}
        res = ab.simulate(dates, prices, adv20_map, cash_ret, weights,
                          ab.CAPITAL, mode=mode, cost_fn=ab.side_cost_v2,
                          p2=p2, start_idx=start_idx)
        out = _account_output(name, weights, mode, p2, res, dates, start_idx,
                              raw_panel, repo_tail, repo_ffill_days, stale)
        path = os.path.join(OUT_DIR, f"{name}.json")
        if _write_if_changed(path, out):
            written += 1
            print(f"{name}: nav {out['latest_nav_cny']:.2f} @ "
                  f"{out['inception_date']}..{dates[-1]} "
                  f"({out['n_bars']} bars, {out['n_trades']} trades) written")
        else:
            print(f"{name}: byte-identical (no new bar / no change), no-op")
    print(f"alloc_paper done: {written} file(s) updated, window "
          f"{dates[start_idx]}..{dates[-1]}")
    return 0


# ------------------------------------------------------------------ selftest

def _mk_sim_inputs(prices_map, dates):
    n = len(dates)
    prices = {s: list(v) for s, v in prices_map.items()}
    syms = list(prices_map)
    amounts = pd.DataFrame({s: [1e12] * n for s in syms}, index=dates)
    adv20_map = {s: amounts[s].tolist() for s in syms}
    cash_ret = [0.0] * n
    return prices, adv20_map, cash_ret


def selftest():
    sys.stdout.reconfigure(encoding="utf-8")
    ok = 0
    total = 0

    def check(cond, label):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print(f"[PASS] {label}")
        else:
            print(f"[FAIL] {label}")

    # S1 forward start_idx derivation
    check(_forward_start(["2026-09-21", "2026-09-22", "2026-09-23"],
                         "2026-09-22") == 2, "S1 start_idx first bar > cutoff")
    check(_forward_start(["2026-09-21", "2026-09-22"], "2026-09-22") is None,
          "S1b no forward bar -> None (no-op path)")

    # S3 inception hand-chain: d(nav) == shares * d(price)
    dts = ["2026-09-23", "2026-09-24"]
    prices, adv20, cash = _mk_sim_inputs({"AAA": [10.0, 11.0]}, dts)
    r = ab.simulate(dts, prices, adv20, cash, {"AAA": 1.0}, 1_000_000.0,
                    mode="monthly", cost_fn=ab.side_cost_v2, p2=False,
                    start_idx=0)
    eq = r["eq"]
    shares = (eq.iloc[1] - eq.iloc[0]) / (11.0 - 10.0)
    check(abs(shares - round(shares / 100) * 100) < 1e-9
          and shares > 0 and shares % 100 == 0,
          "S3 share accounting: d(nav)=shares*d(price), 100-lot integer")

    # S4 monthly rebalance fires at month-first (drift BEFORE boundary)
    dts = (["2026-09-2" + str(d) for d in range(3, 10)]
           + ["2026-10-0" + str(d) for d in range(1, 10)])
    prices, adv20, cash = _mk_sim_inputs(
        {"AAA": [10.0] * 5 + [12.0] * 11, "BBB": [10.0] * 16}, dts)
    r_m = ab.simulate(dts, prices, adv20, cash, {"AAA": 0.5, "BBB": 0.5},
                      1_000_000.0, mode="monthly",
                      cost_fn=ab.side_cost_v2, p2=False, start_idx=0)
    check(r_m["trades"] > 2, "S4 monthly mode: month-first rebalance fired")

    # S5 P3B daily-threshold: >=5pp drift fires; flat market does not
    # (50% sleeve +50% move -> 0.5*1.5/1.25 = 60% weight = 10pp drift >= gate)
    prices_t, adv20t, casht = _mk_sim_inputs(
        {"AAA": [10.0] * 8 + [15.0] * 8, "BBB": [10.0] * 16}, dts)
    r_t = ab.simulate(dts, prices_t, adv20t, casht, {"AAA": 0.5, "BBB": 0.5},
                      1_000_000.0, mode="daily-threshold",
                      cost_fn=ab.side_cost_v2, p2=False, start_idx=0)
    flat_prices, adv20f, cashf = _mk_sim_inputs(
        {"AAA": [10.0] * 16, "BBB": [10.0] * 16}, dts)
    r_flat = ab.simulate(dts, flat_prices, adv20f, cashf,
                         {"AAA": 0.5, "BBB": 0.5}, 1_000_000.0,
                         mode="daily-threshold", cost_fn=ab.side_cost_v2,
                         p2=False, start_idx=0)
    check(r_t["trades"] > r_flat["trades"],
          "S5 threshold mode fires on drift, silent on flat (>=5pp law)")

    # S6/S7 determinism + schema lock (exact key set, no wall-clock fields)
    raw_panel = pd.DataFrame({"AAA": [10.0, 11.0]},
                             index=["2026-09-23", "2026-09-24"])
    o1 = _account_output("ALLOC-TEST", {"AAA": 1.0}, "monthly", False, r,
                         ["2026-09-23", "2026-09-24"], 0, raw_panel,
                         "2026-09-21", [], {"AAA": 0})
    o2 = _account_output("ALLOC-TEST", {"AAA": 1.0}, "monthly", False, r,
                         ["2026-09-23", "2026-09-24"], 0, raw_panel,
                         "2026-09-21", [], {"AAA": 0})
    check(json.dumps(o1, sort_keys=True) == json.dumps(o2, sort_keys=True),
          "S6 output builder deterministic")
    expected_keys = {"schema", "account", "frozen_ref", "engine_ref",
                     "cutoff_frozen", "inception_date", "capital_initial_cny",
                     "cost_face", "mode", "p2", "weights_declared",
                     "p2_inception_note", "nav_series", "latest_nav_cny",
                     "n_bars", "n_trades", "total_cost_cny", "turnover_cny",
                     "commission_floor_hits", "fill_cap_refusals",
                     "data_quality"}
    check(set(o1.keys()) == expected_keys,
          "S7 schema lock: exact frozen key set, zero wall-clock fields")

    # S8 write-if-changed semantics
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "x", "A.json")
        check(_write_if_changed(p, o1) is True, "S8a first write happens")
        check(_write_if_changed(p, o1) is False, "S8b byte-identical no-op")
        o1["n_trades"] = o1["n_trades"] + 1
        check(_write_if_changed(p, o1) is True, "S8c change rewrites")

    # S9 repo forward ffill: production call shape (full-range idx with
    # pre-tail dates present, else ffill has no source -> 0.0 r183 lesson)
    idx = pd.Index(["2026-09-18", "2026-09-21", "2026-09-22",
                    "2026-09-23", "2026-09-24"])
    if os.path.exists(ab.REPO):
        re_, tail, ffd = _load_repo_forward(idx)
        expect_ffd = [d for d in idx if d > tail]
        fwd_vals = [float(re_.loc[d]) for d in ffd]
        repo = pd.read_csv(ab.REPO)
        repo["date"] = repo["date"].astype(str)
        tail_rate = float(repo.set_index("date")["rate"].loc[tail])
        check(ffd == expect_ffd and len(set(fwd_vals)) <= 1
              and (not ffd
                   or abs(fwd_vals[-1] - tail_rate / 100.0 / 252.0) < 1e-15),
              "S9 repo ffill: forward days == tail rate, dayset derived")
    else:
        rs = pd.Series({"2026-09-19": 1.475}, dtype=float)
        daily = rs / 100.0 / 252.0
        re2 = daily.reindex(idx).ffill().fillna(0.0)
        check(abs(float(re2.iloc[-1]) - 1.475 / 100.0 / 252.0) < 1e-12,
              "S9b hermetic: forward day inherits tail rate via ffill")

    # S16 lane guard helper (MSG-2330): owner read + defensive degradation
    import tempfile
    fd_tmp, tmp_path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd_tmp, "w", encoding="utf-8") as tf:
        json.dump({"machine_id": "bm-b"}, tf)
    check(_lane_owner_id(tmp_path) == "bm-b", "S16 lane owner read from machine.json face")
    check(_lane_owner_id(tmp_path + ".missing") == "", "S16b unreadable path -> empty (non-owner)")
    os.unlink(tmp_path)
    # S17 fail-closed face: missing member csv raises (run_paper maps to exit 2)
    try:
        _load_panel_forward(["__no_such_symbol__"])
        check(False, "S17 missing member csv raises FileNotFoundError")
    except FileNotFoundError:
        check(True, "S17 missing member csv raises FileNotFoundError")
    # S18 fail-closed mapping at run_paper level (machine-independent: lane id pinned)
    orig_load, orig_lane = _load_panel_forward, _lane_owner_id
    def _boom(symbols):
        raise FileNotFoundError("data/ext_slots/etf_daily/510880.csv (simulated)")
    globals()["_load_panel_forward"] = _boom
    globals()["_lane_owner_id"] = lambda path=None: LANE_OWNER
    try:
        rc_s18 = run_paper()
    finally:
        globals()["_load_panel_forward"] = orig_load
        globals()["_lane_owner_id"] = orig_lane
    check(rc_s18 == 2, "S18 run_paper maps missing-slot FileNotFoundError -> exit 2")

    print(f"selftest: {ok}/{total} PASS")
    return 0 if ok == total else 2


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run":
        sys.exit(run_paper())
    if cmd == "selftest":
        sys.exit(selftest())
    print("usage: alloc_paper.py [run|selftest]")
    sys.exit(2)


if __name__ == "__main__":
    main()
