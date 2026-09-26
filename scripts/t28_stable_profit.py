"""T28_STABLE_PROFIT runner (CEO order O-20260924-1712 north-star convergence
report; ticket T-2026-09-24-28-P1; claim r89 bm-a MSG-20260924-1947).

Prereg FROZEN pre-run: research/T28_STABLE_PROFIT.md (r89, commit 801c6e6 =
lock). Convergence ASSEMBLY batch -- zero new signal families, zero new
engine code (member_run/t27/regime primitives reused verbatim), zero
adoption wiring (GM ratification MSG-20260924-1958 + 7-day veto window
honored; activation = 2026-10-01 month boundary, T-21 co-landing pattern).

20 aggregate judgment cells (prereg s0):
  W-CUR {x1,x2}                  = current-window face 2026-01-05..09-23
  W-SEG 3 classes x {x1,x2}       = v3 regime segment classes (bull/chop/bear)
  W-GRID {deep,legacy} x {6m,12m,24m} x {base,x2} = virtual-timepoint grid
W-GRID assembly domain note (honest disclosure, frozen-grid constraint):
the P5C/t22 grids carry the 6 CE members only (their preregs froze that
membership); PROSPECT sleeves have no registered evidence on the grid axes
(deep 2013-2019 = out of registration domain). The W-GRID blend face =
B_MAXDIV frozen weights RESTRICTED to the grid's 6 CE members, renormalized
to sum 1 (sub-portfolio of the ratified blend, disclosed); per-member rates
disclosed from the grid cells verbatim. W-CUR/W-SEG use the full frozen
28-member weight vector exactly (sleeve domain = 2020+ anchor panel).

Ledger: append_ledger('T28_STABLE_PROFIT', 20, ...) aggregate-caliber note;
W-GRID per-cell N follows the P5C/t22 already-counted ledgers (no recount),
disclosed per unit. Sleeve runs are T-27-machinery reproductions at the live
panel cutoff (o1600 caliber) -- ledger +0 (onboarding precedent).

Subcommands:
  run        full assembly -> results/current_market_stable_profit.json
             + research/T28_STABLE_PROFIT_REPORT.md + ledger + gate_attrition
  selftest   offline fixtures (no network, no engine)
"""
import argparse
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from config import PATHS
from engine import run_backtest
from engine.metrics import max_drawdown
from firm.hr import TRADERS_DIR, load_trader
from live.paper import (SIGNAL_BUILDERS, ExitPatch, build_panels, load_core,
                        self_test_patches, v3_state_series)
from parallel_runner import run_cells_parallel, worker_cap
from p5c_virtual_timepoint import REGIME_MAP, _wilson
from science_gates import (CostPatch, append_ledger, cutoff_meta,
                           ledger_head)

W_CUR_START = pd.Timestamp("2026-01-05")   # prereg s2 (o1600/MSG-1630)
W_CUR_END = pd.Timestamp("2026-09-23")     # prereg s2 (local bars cutoff)
TOURN_JSON = os.path.join(PATHS.results_dir, "portfolio_blend_tournament.json")
P5C_CKPT = os.path.join(PATHS.results_dir, "shortline", "p5c_checkpoint",
                        "legL", "shard_0of1.jsonl")
T22_DIR = os.path.join(PATHS.results_dir, "t22")
OUT_JSON = os.path.join(PATHS.results_dir, "current_market_stable_profit.json")
OUT_REPORT = os.path.join(PATHS.root, "research", "T28_STABLE_PROFIT_REPORT.md")
WINDOWS = {"6m": 126, "12m": 252, "24m": 504}
J_DD_CAP = 0.05          # J1 |maxDD| <= 5% (prereg s4)
J_SEG_FLOOR = -0.05      # J3 segment class cumulative >= -5% (prereg s4)
J_BEAT_LINE = 0.70       # J4 beat-passive line (P-5/P-5B frozen)
N_CELLS = 20             # prereg s0 aggregate judgment cells
GRID_EVIDENCE_CUTOFF = "2026-09-22"   # P5C/t22 grids frozen cutoff


# ------------------------------------------------------------- sleeve layer
def _sleeve_worker(tid, mult, prices, cutoff):
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass
    P = build_panels(prices)
    idx = P["close"].index
    t = load_trader(tid)
    entry = SIGNAL_BUILDERS[t["params"]["entry"]](P)
    params = {k: v for k, v in t["params"].items() if k != "entry"}
    from contextlib import nullcontext
    cctx = CostPatch(mult) if mult else nullcontext()
    with cctx, ExitPatch(t.get("exit_overrides")):
        res = run_backtest(prices, params, entry_signal=entry,
                           exit_signal=(entry <= 0),
                           dd_control=t.get("dd_control"))
    eq = pd.Series(res["equity_curve"],
                   index=idx[:len(res["equity_curve"])])
    eq = eq[eq.index <= cutoff]
    return {"tid": tid, "mult": mult or 1,
            "dates": [str(d.date()) for d in eq.index],
            "eq": [float(v) for v in eq],
            "n_trades": int(res["metrics"]["num_trades"]),
            "oos_trades": int(sum(1 for tr in res["trades"]
                                  if str(tr["date"]) >= "2025-01-01"))}


def _blend_daily_ret(sleeves, weights):
    """Daily-rebalanced portfolio return (t27 _frame_returns static_w)."""
    eqs = pd.concat({tid: sleeves[tid]["eq_s"] / sleeves[tid]["eq_s"].iloc[0]
                     for tid in sleeves}, axis=1, join="inner").dropna()
    R = eqs.pct_change().dropna()
    cols = set(R.columns)
    if set(weights) != cols:
        raise ValueError(f"weight/roster mismatch: {sorted(set(weights) ^ cols)}")
    return (R * pd.DataFrame([weights] * len(R), index=R.index,
                             columns=list(R.columns))).sum(axis=1)


def _window_face(port_ret, start, end):
    w = port_ret[(port_ret.index >= start) & (port_ret.index <= end)]
    eq = (1.0 + w).cumprod()
    return {"n_days": int(len(w)),
            "ret": round(float(eq.iloc[-1] - 1.0), 6),
            "dd": round(float(max_drawdown(eq)), 6)}


def _seg_classes(port_ret, states):
    """Per mapped class cumulative net contribution (prereg s4 J3).
    states = raw v3 series (GREEN/YELLOW/ORANGE/RED) -> mapped classes."""
    s = states.reindex(port_ret.index, method="ffill").map(REGIME_MAP)
    out = {}
    for cls in ("bull", "chop", "bear"):
        w = port_ret[s == cls]
        eq = (1.0 + w).cumprod()
        out[cls] = {"n_days": int(len(w)),
                    "cum_ret": (round(float(eq.iloc[-1] - 1.0), 6)
                                if len(w) else None)}
    return out


# ------------------------------------------------------------- grid layer
def _load_legacy_grid():
    """P5C leg-L checkpoint cells -> unified per-window rows."""
    rows = []      # (face, window) -> {start: {trader: ret,...}} built below
    passive = {}   # start -> {window: ret}
    tret = {}      # (trader, face, start) -> {window: (ret, dd, trades, regime)}
    with open(P5C_CKPT, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("trader") == "PASSIVE":
                passive[r["start"]] = {w: float(m["ret"])
                                       for w, m in r["windows"].items()}
            else:
                tret[(r["trader"], r["face"], r["start"])] = {
                    w: (float(m["ret"]), float(m.get("dd", 0.0)),
                        int(m.get("trades", 0)),
                        REGIME_MAP.get(r.get("regime_state_start"), "na"))
                    for w, m in r["windows"].items()}
    return tret, passive


def _load_deep_grid():
    """t22 deep-axis cells -> unified shape (base face == x1 caliber)."""
    import glob
    seen, tret, passive = set(), {}, {}
    for path in sorted(glob.glob(os.path.join(T22_DIR, "cells_deep_*.jsonl"))):
        face = "x2" if "x2" in os.path.basename(path) else "x1"
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                k = (r["trader"], r["pos"], face)
                if k in seen:
                    continue              # dprobe reproductions -> dedupe
                seen.add(k)
                start = str(r["start"])
                tret[(r["trader"], face, start)] = {}
                for w, retk, pk, trk, partk in (
                        ("6m", "ret_6m", "p_ret_6m", "trades_6m", None),
                        ("12m", "ret_12m", "p_ret_12m", "trades_12m",
                         "partial_12m"),
                        ("24m", "ret_24m", "p_ret_24m", "trades_24m",
                         "partial_24m")):
                    if retk not in r or r[retk] is None:
                        continue
                    if partk and r.get(partk):
                        continue          # partial windows excluded (complete only)
                    tret[(r["trader"], face, start)][w] = (
                        float(r[retk]), None, int(r.get(trk, 0)),
                        str(r.get("regime", "na")))
                    passive.setdefault(start, {})[w] = float(r[pk])
    return tret, passive


def _grid_unit(tret, passive, w_ce, traders, window, face):
    """One W-GRID unit: static CE-6 blend per start + beat stats + D7."""
    cells = []
    for sdate, pw in passive.items():
        if window not in pw:
            continue
        rets, ok = {}, True
        for t in traders:
            e = tret.get((t, face, sdate), {}).get(window)
            if e is None:
                ok = False
                break
            rets[t] = e
        if not ok:
            continue
        blend = sum(w_ce[t] * rets[t][0] for t in traders)
        cells.append({"start": sdate, "blend_ret": blend, "passive": pw[window],
                      "trades": sum(rets[t][2] for t in traders),
                      "segment": rets[traders[0]][3]})
    n = len(cells)
    k = sum(1 for c in cells if c["blend_ret"] > c["passive"])
    rate = k / n if n else None
    lo, hi = _wilson(k, n)
    starts = sorted(pd.Timestamp(c["start"]) for c in cells)
    n_reg, last = 0, None
    for c in sorted(cells, key=lambda c: c["start"]):
        if c["segment"] != last:
            n_reg += 1
            last = c["segment"]
    per_member = {}
    for t in traders:
        mk = mn = 0
        for sdate, pw in passive.items():
            if window not in pw:
                continue
            e = tret.get((t, face, sdate), {}).get(window)
            if e is None:
                continue
            mn += 1
            mk += int(e[0] > pw[window])
        per_member[t] = {"n": mn, "beat_rate": round(mk / mn, 4) if mn else None}
    return {"n": n, "beats": k,
            "beat_rate": round(rate, 4) if rate is not None else None,
            "member_cells_N": n * len(traders),
            "oos_trades_pooled": int(sum(c["trades"] for c in cells)),
            "covered_years": (round((starts[-1] - starts[0]).days / 365.25, 2)
                              if starts else None),
            "independent_regime_windows": n_reg,
            "ci95_width": round(hi - lo, 4),
            "per_member_beat_rate": per_member}


# ------------------------------------------------------------------ run
def cmd_run(rerun=False):
    t0 = time.time()
    print("=== T28_STABLE_PROFIT assembly (prereg r89 frozen) ===")
    if not self_test_patches():
        print("T28-GATE FAIL: patch self-test")
        return 2

    # -- frozen weights (sha recorded; x2 face same source, prereg s3)
    with open(TOURN_JSON, encoding="utf-8") as fh:
        tour = json.load(fh)
    w_full = tour["weights"]["B_MAXDIV"]["weights"]
    w_sha = hashlib.sha256(
        json.dumps(w_full, sort_keys=True).encode()).hexdigest()[:16]
    print(f"B_MAXDIV frozen weights sha256[:16]={w_sha} "
          f"({len(w_full)} members)")

    roster = sorted(p.stem for p in TRADERS_DIR.glob("*.json")
                    if not p.name.startswith("_"))
    if set(roster) != set(w_full):
        print(f"T28-GATE FAIL: roster/weights mismatch "
              f"{sorted(set(roster) ^ set(w_full))}")
        return 2

    # -- sleeves: 28 members x {x1, x2} on live panel (o1600 caliber)
    prices_full = load_core()
    cutoff = max(df.index.max() for df in prices_full.values())
    print(f"live panel cutoff: {cutoff.date()} (prereg W-CUR end 09-23)")
    if cutoff < W_CUR_END:
        print(f"T28-GATE FAIL: panel cutoff {cutoff.date()} < prereg end "
              f"09-23 -- bars missing")
        return 2
    prices = {s: df[df.index <= W_CUR_END] for s, df in prices_full.items()}
    jobs = [(tid, mult, prices, W_CUR_END)
            for tid in roster for mult in (None, 2.0)]
    res = run_cells_parallel(
        [(f"{a[0]}|{a[1] or 'x1'}", _sleeve_worker, a) for a in jobs],
        workers=min(worker_cap(), 25), desc="t28-sleeves")
    sleeves = {}
    for tid in roster:
        r1, r2 = res[f"{tid}|x1"], res[f"{tid}|2.0"]
        for r in (r1, r2):
            r["eq_s"] = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
        sleeves[tid] = {"x1": r1, "x2": r2}
    print(f"sleeves: {len(sleeves)} members x 2 faces "
          f"({time.time()-t0:.0f}s)")

    # -- W-CUR (2 cells): per-face daily-rebalanced blend series
    pr1 = _blend_daily_ret({t: sleeves[t]["x1"] for t in roster}, w_full)
    pr2 = _blend_daily_ret({t: sleeves[t]["x2"] for t in roster}, w_full)
    wcur = {"x1": _window_face(pr1, W_CUR_START, W_CUR_END),
            "x2": _window_face(pr2, W_CUR_START, W_CUR_END)}

    # -- W-SEG (6 cells): v3 states single source (import-replay)
    states = v3_state_series()
    wseg = {}
    for face, pr in (("x1", pr1), ("x2", pr2)):
        wseg[face] = _seg_classes(pr, states)

    # -- W-GRID (12 cells)
    traders6 = sorted(t for t in w_full if t in (
        "COMPOSITE-CE-01", "COMPOSITE-CE-02", "VOLATILITY-CE-01",
        "ENGULF-CE-01", "NEEDLE-DE-01", "DROUGHT-CE-01"))
    w_ce_sum = sum(w_full[t] for t in traders6)
    w_ce = {t: round(w_full[t] / w_ce_sum, 8) for t in traders6}
    print(f"W-GRID CE-6 restricted weights (renorm, sum={sum(w_ce.values()):.6f}): "
          f"{w_ce}")
    lt, lp = _load_legacy_grid()
    dt, dp = _load_deep_grid()
    wgrid = {}
    for axis, tret, passive in (("legacy", lt, lp), ("deep", dt, dp)):
        for window in WINDOWS:
            for face in ("x1", "x2"):
                wgrid[f"{axis}|{window}|{face}"] = _grid_unit(
                    tret, passive, w_ce, traders6, window, face)
    n_12m = (wgrid["legacy|12m|x1"]["n"] + wgrid["deep|12m|x1"]["n"])
    k_12m = (wgrid["legacy|12m|x1"]["beats"] + wgrid["deep|12m|x1"]["beats"])

    # -- judgments (prereg s4, frozen)
    j1 = bool(wcur["x1"]["ret"] > 0 and abs(wcur["x1"]["dd"]) <= J_DD_CAP)
    j2 = bool(wcur["x2"]["ret"] > 0)
    j3 = all((wseg[f][c]["cum_ret"] is not None
              and wseg[f][c]["cum_ret"] >= J_SEG_FLOOR)
             for f in ("x1", "x2") for c in ("bull", "chop", "bear"))
    j4 = bool(n_12m and k_12m / n_12m >= J_BEAT_LINE)
    verdict = ("STABLE-PROFIT-DEMONSTRATED" if (j1 and j2 and j3 and j4)
               else "NOT-DEMONSTRATED (honest negative, all faces disclosed)")
    print(f"J1={j1} J2={j2} J3={j3} J4={j4} -> {verdict}")

    # -- ledger (aggregate caliber; W-GRID per-cell N follows P5C/t22 counts)
    # rerun mode (J18 engineering repair, criteria untouched): the 20 cells
    # were already counted once in the run#1 ledger entry -> no recount.
    head = ledger_head()
    if rerun:
        prev = head["total"] - N_CELLS
        led = {"prev_total": prev, "batch_trials": N_CELLS,
               "total": head["total"], "batch": "T28_STABLE_PROFIT",
               "file": os.path.basename(OUT_JSON),
               "note": "engineering re-run of run#1 (W-SEG face VOID: v3 raw "
                       "states unmapped -> zero segment days, J3 judged on "
                       "broken face; J18 fix implementation only); 20 cells "
                       "already counted in run#1 entry, ledger +0",
               "evidence_cutoff": str(W_CUR_END.date())}
        print(f"ledger (rerun): cells already counted -> total stays "
              f"{head['total']}")
    else:
        prev = max(head["total"], 22157)
        led = append_ledger("T28_STABLE_PROFIT", N_CELLS,
                            os.path.basename(OUT_JSON),
                            note="20 aggregate judgment cells (W-CUR 2 + "
                                 "W-SEG 6 + W-GRID 12); W-GRID per-cell N "
                                 "follows P5C/t22 already-counted ledgers no "
                                 "recount; 56 sleeve runs = T-27-machinery "
                                 "reproductions at live-panel o1600 caliber, "
                                 "ledger +0",
                            evidence_cutoff=str(W_CUR_END.date()),
                            prev_total=prev)
        print(f"ledger: prev={prev} +{N_CELLS} -> {led['total']}")

    # -- gate_attrition row (prereg s8)
    ga_path = os.path.join(PATHS.results_dir, "gate_attrition.json")
    try:
        ga = json.load(open(ga_path, encoding="utf-8"))
        ga["entries"].append({
            "batch": "T28_STABLE_PROFIT",
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "measurement",
            "cells_ledger_delta": 0 if rerun else N_CELLS,
            "ledger_total_after": led["total"],
            "gates": {"J1_current_window": j1, "J2_x2_survival": j2,
                      "J3_regime_segments": j3,
                      "J4_grid_beat_12m_pooled":
                          round(k_12m / n_12m, 4) if n_12m else None},
            "eliminated": None,
            "refs": {"results": OUT_JSON,
                     "prereg": "research/T28_STABLE_PROFIT.md"}})
        with open(ga_path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(ga, fh, ensure_ascii=False, indent=1)
    except FileNotFoundError:
        print("gate_attrition.json absent -- skipped (disclosed)")

    out = cutoff_meta(str(W_CUR_END.date()))
    out.update({
        "batch": "T28_STABLE_PROFIT", "verdict": verdict,
        "judgments": {"J1_current_window_profit": j1,
                      "J2_x2_survival": j2, "J3_regime_segment_stability": j3,
                      "J4_grid_beat_rate_12m": j4,
                      "rule": "J1-J4 all pass = STABLE-PROFIT-DEMONSTRATED "
                              "(prereg s4, honest negative otherwise)"},
        "weights": {"source": TOURN_JSON, "method": "B_MAXDIV",
                    "sha256_first16": w_sha, "n_members": len(w_full),
                    "grid_ce6_restricted": w_ce,
                    "grid_restriction_note":
                        "grid preregs froze 6-CE membership; W-GRID blend = "
                        "frozen weights restricted to CE-6 renormalized "
                        "(sub-portfolio face, disclosed); W-CUR/W-SEG use "
                        "the full 28-member vector exactly"},
        "w_cur": wcur, "w_seg": wseg, "w_grid": wgrid,
        "w_grid_meta": {
            "evidence_cutoff": GRID_EVIDENCE_CUTOFF,
            "assembly": "static initial-capital blend of member window "
                        "returns (pure cell arithmetic, no rebalance "
                        "inference); per-member rates from grid cells",
            "pooled_12m": {"n": n_12m, "beats": k_12m,
                           "rate": round(k_12m / n_12m, 4) if n_12m else None},
            "legacy_counts": {w: {"n_x1": wgrid[f"legacy|{w}|x1"]["n"],
                                  "member_cells": wgrid[
                                      f"legacy|{w}|x1"]["member_cells_N"]}
                              for w in WINDOWS},
            "deep_counts": {w: {"n_x1": wgrid[f"deep|{w}|x1"]["n"],
                                "member_cells": wgrid[
                                    f"deep|{w}|x1"]["member_cells_N"]}
                            for w in WINDOWS}},
        "trials_ledger": led,
        "adoption": "ZERO wiring this batch (veto window 09-24..10-01 "
                    "honored; activation 10-01 month boundary per GM "
                    "MSG-20260924-1958)",
        "audit": {"runtime_sec": round(time.time() - t0, 1),
                  "machine": "bm-a",
                  "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                  "sleeve_cutoff": str(W_CUR_END.date()),
                  "rerun_void_repair": bool(rerun)},
    })
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=float)
    print(f"outputs: {OUT_JSON}")

    # -- one-page CEO report (prereg s6)
    seg_txt = "; ".join(
        f"{f}/{c}={wseg[f][c]['cum_ret']}"
        for f in ("x1", "x2") for c in ("bull", "chop", "bear"))
    grid_txt = "; ".join(
        f"{a}|{w}|{f}={wgrid[f'{a}|{w}|{f}']['beat_rate']}(n={wgrid[f'{a}|{w}|{f}']['n']})"
        for a in ("legacy", "deep") for w in WINDOWS for f in ("x1", "x2"))
    rep = f"""# T28 稳定盈利报告（当前市场·B_MAXDIV 冠军装配面）

- 判定：**{verdict}**（J1={j1} J2={j2} J3={j3} J4={j4}；判据跑前冻结 research/T28_STABLE_PROFIT.md §4）
- 收益（W-CUR 2026-01-05→09-23）：x1 净收益 {wcur['x1']['ret']} / maxDD {wcur['x1']['dd']}；x2 净收益 {wcur['x2']['ret']}（成本加倍面）
- 政体段稳健（累计净贡献，≥−5% 界）：{seg_txt}
- 大规模时点通过率（W-GRID 静态装配，12m 主判 pooled={round(k_12m/n_12m, 4) if n_12m else None}≥0.70）：{grid_txt}
- 验证链：权重 sha {w_sha}（T-27 正典件）；56 sleeve=T-27 机件 o1600 口径复现（账本 +0）；W-GRID=网格冻结域纯装配（per-cell N 沿用 P5C/t22 已计账本，逐员率全披露）；账本 {led['prev_total']}+{N_CELLS}={led['total']}；evidence_cutoff {W_CUR_END.date()}（网格面 09-22）
- 边界：本报告=证据面非生产面；采纳零接线（否决窗 2026-09-24→10-01；激活=10-01 月界与 IV6/月界 enforce 同日）
"""
    with open(OUT_REPORT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(rep)
    print(f"report: {OUT_REPORT}")
    return 0


# -------------------------------------------------------------- selftest
def cmd_selftest():
    ok_n, fails = 0, 0

    def ok(name, cond):
        nonlocal ok_n, fails
        ok_n += 1
        if not cond:
            fails += 1
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")
        return cond

    # 1) static blend assembly arithmetic
    w = {"A": 0.6, "B": 0.4}
    rets = {"A": 0.10, "B": -0.05}
    ok("static blend = weighted sum of window returns",
       abs(sum(w[t] * rets[t] for t in w) - 0.04) < 1e-12)

    # 2) renormalized restriction
    full = {"A": 0.1, "B": 0.3, "C": 0.6}
    rest = {k: full[k] / 0.4 for k in ("A", "B")}
    ok("restriction renorm sums to 1", abs(sum(rest.values()) - 1.0) < 1e-12)

    # 3) daily-rebalanced blend vs hand value
    R = pd.DataFrame({"A": [0.01, 0.02], "B": [0.0, -0.01]},
                     index=pd.bdate_range("2026-01-05", periods=2))
    pr = (R * pd.DataFrame([w] * len(R), index=R.index,
                           columns=list(R.columns))).sum(axis=1)
    eq = (1.0 + pr).cumprod()
    hand = (1 + 0.6 * 0.01 + 0.4 * 0.0) * (1 + 0.6 * 0.02 + 0.4 * -0.01) - 1
    ok("daily-rebalanced blend compounding",
       abs(float(eq.iloc[-1] - 1.0) - hand) < 1e-12)

    # 4) window face ret/dd shape (ret rounded 6dp -> 1e-6 tolerance)
    pr = pd.Series([0.01, -0.02, 0.03, 0.01],
                   index=pd.bdate_range("2026-01-05", periods=4))
    f = _window_face(pr, pr.index[0], pr.index[-1])
    ok("window face: ret + dd",
       abs(f["ret"] - ((1.01 * 0.98 * 1.03 * 1.01) - 1)) < 1e-6
       and f["dd"] < 0)

    # 5) segment classes cumulative (raw v3 states mapped via REGIME_MAP)
    states = pd.Series(["GREEN", "GREEN", "RED", "RED"],
                       index=pd.bdate_range("2026-01-05", periods=4))
    pr = pd.Series([0.01, 0.01, -0.01, -0.01], index=states.index)
    seg = _seg_classes(pr, states)
    ok("seg classes: raw-state mapping + per-class compounding",
       abs(seg["bull"]["cum_ret"] - (1.01 * 1.01 - 1)) < 1e-9
       and abs(seg["bear"]["cum_ret"] - (0.99 * 0.99 - 1)) < 1e-9
       and seg["chop"]["cum_ret"] is None)

    # 6) grid unit stats + D7 shape
    tret = {("T1", "x1", "2021-01-15"): {"6m": (0.02, -0.05, 7, "bull")},
            ("T2", "x1", "2021-01-15"): {"6m": (-0.01, -0.02, 3, "bull")},
            ("T1", "x1", "2021-01-18"): {"6m": (-0.01, -0.03, 5, "bear")},
            ("T2", "x1", "2021-01-18"): {"6m": (-0.005, -0.01, 2, "bear")}}
    passive = {"2021-01-15": {"6m": 0.01}, "2021-01-18": {"6m": -0.02}}
    w6 = {"T1": 0.5, "T2": 0.5}
    u = _grid_unit(tret, passive, w6, ["T1", "T2"], "6m", "x1")
    ok("grid unit: blend beats + rate + member N",
       u["n"] == 2 and u["beats"] == 1 and u["beat_rate"] == 0.5
       and u["member_cells_N"] == 4
       and u["oos_trades_pooled"] == 17
       and u["independent_regime_windows"] == 2
       and u["per_member_beat_rate"]["T1"]["beat_rate"] == 1.0
       and u["per_member_beat_rate"]["T2"]["beat_rate"] == 0.5
       and u["ci95_width"] > 0)

    # 7) Wilson reuse (shared primitive; k=1,n=1 -> classic [0.2065, 1.0])
    lo, hi = _wilson(1, 1)
    ok("wilson import reuse", 0 < lo < 0.5 and abs(hi - 1.0) < 1e-9)

    print(f"selftest: {ok_n - fails}/{ok_n} checks "
          f"{'ALL PASS' if not fails else 'FAIL'}")
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--rerun", action="store_true",
                   help="J18 engineering re-run: ledger +0 (cells counted "
                        "in run#1), W-SEG face repair disclosure")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "run":
        return cmd_run(rerun=a.rerun)
    return cmd_selftest()


if __name__ == "__main__":
    sys.exit(main())
