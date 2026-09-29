# -*- coding: utf-8 -*-
"""_r459bma_rrg_w6_probe.py -- G-ANCHOR + D6 freeze-window probe for
RRG-ROTATION-P1 (INNOVATION-QUOTA-SLOT-6, zoo #91 rrg_quadrant_rotation,
param-frozen r216 digest clean-room).

r459 bm-a freeze window (berth r458 -> self-freeze mirror of W5 r247->r248).
THIS FILE IS THE CONSTRUCTION FREEZE: the runner (scripts/innovation_quota_w6.py)
verbatim-imports build_rrg_faces / rrg_selection / selection_to_entry
(r456 verbatim-import paradigm -- a158_tsgate_probe lineage; single source,
zero re-implementation drift).

Construction (prereg s3 frozen, r216 digest sec.2 #91 clean-room):
  RS          = member close / pool equal-weight NAV (daily-rebalanced mean
                of member daily returns -- the 48-pool EW benchmark, NOT an
                external index; r216 card: RS-Ratio scale-invariant to the
                benchmark's absolute level)
  RS-Ratio    = MA20(100 * RS / RS.shift(220))     (de Kempenaer ratio
                method, hub 100, NOT the difference method)
  RS-Momentum = MA20(100 * RS-Ratio / RS-Ratio.shift(60))
  quadrant    = leading iff RS-Ratio > 100 AND RS-Momentum > 100 (finite)
  selection   = top-k members by Euclidean distance from hub (100, 100)
                among leading; ties broken by code ascending (deterministic)
  sampling    = month-end close decision, state effective from T+1 (marks
                continuous-hold, engine buys next-day open; T33 gem_entry
                causality precedent)
  carry rule  = zero leading members at a month-end -> maintain previous
                selection (state-machine maintain, frozen determinism)
  variants    = base top-6 (position_size_pct 0.95/6, fleet 0.95
                full-position convention T33/GEM precedent, satisfies prereg
                <=1/6 cap) / unconstrained top-2 (0.95/2 each; freeze-window
                fixed choice, prereg s9 note)

Facts written to results/_r459bma_rrg_w6_probe_facts.json:
  G-PANEL faces, month-end census, per-month-end selection records for BOTH
  variants (the bit-exact runner reconciliation anchor), leading-size/carry
  faces, containment/overlap faces, D6 corr face vs T33 in-book rotation
  cells (merge-clause protocol prereg s1) and vs the registered six
  (disclosure only). NO performance metrics (sharpe/annual/maxdd) are
  persisted -- prereg s7 placeholder discipline: pre-run numbers written =
  fraud. The preregistered D6 corr face needs the two variants' full-window
  x1 daily return series via the REAL engine path (real OHLCV fills).

Usage: python results/_r459bma_rrg_w6_probe.py run
"""
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

CUTOFF = "2026-09-22"                      # P-5C frozen anchor (W-series)
TOP_K = {"base": 6, "unc": 2}
PS = {"base": 0.95 / 6.0, "unc": 0.95 / 2.0}   # fleet 0.95 full-position
D6_REJECT = 0.7                            # prereg s1 merge clause
T33_CELLS_PATH = os.path.join(ROOT, "results", "t33_attack_wave_cells.jsonl")
T33_GATES_PATH = os.path.join(ROOT, "results", "t33_attack_wave_gates.json")
T33_ROT_CELLS = ["slope_r2_rotation_25_top3_r8", "dual_momentum_etf_20_60_top3",
                 "rs_rotation_20", "composite_top5"]
OUT = os.path.join(ROOT, "results", "_r459bma_rrg_w6_probe_facts.json")


# ------------------------------------------------------------- construction
def build_rrg_faces(close: pd.DataFrame):
    """Pool EW NAV + RS-Ratio + RS-Momentum (prereg s3 frozen formulae)."""
    rets = close.pct_change()
    ew_ret = rets.mean(axis=1)             # daily-rebalanced equal weight
    nav = (1.0 + ew_ret.fillna(0.0)).cumprod()
    rs = close.div(nav, axis=0)
    rs_ratio = (100.0 * rs / rs.shift(220)).rolling(20).mean()
    rs_mom = (100.0 * rs_ratio / rs_ratio.shift(60)).rolling(20).mean()
    return nav, rs_ratio, rs_mom


def month_end_days(idx: pd.DatetimeIndex) -> pd.DatetimeIndex:
    pos = pd.Series(np.arange(len(idx)), index=idx)
    return pos.groupby(idx.to_period("M")).tail(1).index


def rrg_selection(rs_ratio: pd.DataFrame, rs_mom: pd.DataFrame,
                  top_k: int) -> dict:
    """Month-end decision timeline: me_day -> tuple(selected codes).

    Leading = RS-Ratio > 100 AND RS-Momentum > 100 (both finite); rank by
    Euclidean distance from hub (100,100) desc, code asc tie-break; zero
    leading -> carry previous (state-machine maintain)."""
    me_days = month_end_days(rs_ratio.index)
    sel, prev = {}, ()
    for d in me_days:
        rsr = rs_ratio.loc[d]
        rsm = rs_mom.loc[d]
        ok = rsr.notna() & rsm.notna()
        lead = ok & (rsr > 100.0) & (rsm > 100.0)
        if bool(lead.any()):
            dist = np.hypot(rsr - 100.0, rsm - 100.0)
            cand = [(float(dist[m]), m) for m in rsr.index[lead]]
            cand.sort(key=lambda x: (-x[0], x[1]))
            prev = tuple(m for _, m in cand[:top_k])
        sel[d] = prev                        # carry when not lead.any()
    return sel


def selection_to_entry(sel: dict, close: pd.DataFrame) -> pd.DataFrame:
    """Continuous-hold marks with month-end T+1 causality (gem_entry
    pattern: old selection marked through month-end close, new selection
    marks from the next bar -> engine buys next-day open)."""
    idx = close.index
    entry = pd.DataFrame(0, index=idx, columns=close.columns, dtype=int)
    me_set = set(sel.keys())
    cur = ()
    for d in idx:
        for m in cur:
            entry.at[d, m] = 1
        if d in me_set:
            cur = sel[d]
    return entry


# ------------------------------------------------------------------- panel
def load_panel():
    """Real engine path: load_core OHLCV frames truncated to cutoff +
    build_panels close face (T33 sec.2 same-face)."""
    from live.paper import load_core, build_panels
    prices_full = load_core()
    if len(prices_full) != 48:
        raise SystemExit(f"G-PANEL refuse: core48 members {len(prices_full)} != 48")
    ps = pd.Timestamp(CUTOFF)
    prices = {s: df[df.index <= ps] for s, df in prices_full.items()}
    end = max(df.index[-1] for df in prices.values())
    if str(end.date()) != CUTOFF:
        raise SystemExit(f"G-PANEL refuse: panel end {end} != cutoff {CUTOFF}")
    P = build_panels(prices)
    return P["close"], prices


def variant_cell(close: pd.DataFrame, prices: dict, variant: str,
                 cost_mult: float = 1.0):
    """One (variant, cost-face) cell via the REAL engine path. Returns
    (daily-return series, n_trades, full metrics dict). The probe uses the
    return series ONLY for the preregistered D6 corr face and persists no
    performance metric."""
    from engine import run_backtest
    sel = rrg_selection(*build_rrg_faces(close)[1:], TOP_K[variant])
    entry = selection_to_entry(sel, close)
    params = {"max_positions": TOP_K[variant],
              "position_size_pct": PS[variant],
              "report_num_entries": True}
    if cost_mult != 1.0:
        from science_gates import CostPatch
        with CostPatch(cost_mult):
            res = run_backtest(prices, params, entry_signal=entry,
                               exit_signal=(entry <= 0))
    else:
        res = run_backtest(prices, params, entry_signal=entry,
                           exit_signal=(entry <= 0))
    eq = pd.Series(res["equity_curve"],
                   index=close.index[:len(res["equity_curve"])])
    return eq.pct_change().dropna(), int(res["metrics"]["num_trades"]), res["metrics"]


def _pearson(a: pd.Series, b: pd.Series) -> float:
    j = pd.concat([a, b], axis=1, join="inner").dropna()
    if len(j) < 20:
        return float("nan")
    c = np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1]
    return float(c) if np.isfinite(c) else float("nan")


def _panel_calendar_union(cutoff: str) -> pd.DatetimeIndex:
    from live.paper import load_core
    ps = pd.Timestamp(cutoff)
    all_idx = set()
    for df in load_core().values():
        all_idx.update(df.index[df.index <= ps])
    return pd.DatetimeIndex(sorted(all_idx))


def run() -> int:
    close, prices = load_panel()
    nav, rs_ratio, rs_mom = build_rrg_faces(close)
    me_days = month_end_days(close.index)
    sels = {v: rrg_selection(rs_ratio, rs_mom, TOP_K[v]) for v in TOP_K}

    # idempotence self-check: re-derivation must be identical
    sels2 = {v: rrg_selection(rs_ratio, rs_mom, TOP_K[v]) for v in TOP_K}
    assert all(list(sels2[v].values()) == list(sels[v].values()) for v in TOP_K), \
        "selection re-derivation drift (idempotence)"

    # ---- month-end census + selection records (bit-exact anchor)
    recs = {v: {} for v in TOP_K}
    lead_sizes, no_decidable, zero_lead, carry_while_decidable = [], 0, 0, 0
    decidable_mes = []
    for d in me_days:
        rsr, rsm = rs_ratio.loc[d], rs_mom.loc[d]
        ok = rsr.notna() & rsm.notna()
        lead = ok & (rsr > 100.0) & (rsm > 100.0)
        decidable = bool(ok.any())
        if decidable:
            decidable_mes.append(d)
        if not decidable:
            no_decidable += 1
        elif not bool(lead.any()):
            zero_lead += 1
        else:
            lead_sizes.append(int(lead.sum()))
        # carry face: decidable members exist but selection empty (state
        # machine carried an empty pre-first-selection or post-clear state)
        if decidable and not sels["base"][d]:
            carry_while_decidable += 1
        for v in TOP_K:
            recs[v][str(d.date())] = list(sels[v][d])
    first_decidable = str(decidable_mes[0].date()) if decidable_mes else None

    # containment: unc top-2 within base top-6 on the same month-end
    contain_n = contain_hit = 0
    for d in me_days:
        b, u = set(sels["base"][d]), set(sels["unc"][d])
        if u:
            contain_n += 1
            contain_hit += int(u.issubset(b))

    def _jac(a, b):
        A, B = set(a), set(b)
        if not A and not B:
            return 1.0
        return len(A & B) / len(A | B)

    jac = {v: [] for v in TOP_K}
    for v in TOP_K:
        vals = list(sels[v].values())
        for a, b in zip(vals, vals[1:]):
            jac[v].append(_jac(a, b))

    # ---- D6 corr face (engine x1 base series, preregistered protocol)
    rets, ntr = {}, {}
    for v in TOP_K:
        r, n_trades, _m = variant_cell(close, prices, v)
        rets[v], ntr[v] = r, n_trades
    d6 = {"batch_internal_base_vs_unc": round(abs(_pearson(rets["base"], rets["unc"])), 4),
          "vs_t33_cells": {}, "merge_clause_applied": [],
          "vs_registered_six": {"max_abs_corr": None, "argmax": None}}
    t33_idx = _panel_calendar_union("2026-09-24")     # T33 own cutoff face
    t33_rows = {}
    with open(T33_CELLS_PATH, encoding="utf-8") as fh:
        for ln in fh.read().splitlines():
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            if r.get("status") == "ok" and r.get("face") == "base" \
                    and r.get("cand") in T33_ROT_CELLS and "rets" in r:
                t33_rows[r["cand"]] = pd.Series(
                    r["rets"], index=t33_idx[1:len(r["rets"]) + 1])
    for cid in T33_ROT_CELLS:
        if cid not in t33_rows:
            d6["vs_t33_cells"][cid] = None
            continue
        cc = round(abs(_pearson(rets["base"], t33_rows[cid])), 4)
        cu = round(abs(_pearson(rets["unc"], t33_rows[cid])), 4)
        d6["vs_t33_cells"][cid] = {"base": cc, "unc": cu}
        if max(cc, cu) >= D6_REJECT:
            d6["merge_clause_applied"].append(cid)
    try:
        gates = json.load(open(T33_GATES_PATH, encoding="utf-8"))
        reg_rets = gates.get("registered_rets", {})
        my_idx = close.index
        best = (0.0, None)
        for rid, rl in reg_rets.items():
            k = min(len(rl), len(my_idx) - 1)
            rs_ = pd.Series(rl[:k], index=my_idx[1:k + 1])
            cc = abs(_pearson(rets["base"], rs_))
            if np.isfinite(cc) and cc > best[0]:
                best = (cc, rid)
        d6["vs_registered_six"] = {"max_abs_corr": round(best[0], 4),
                                   "argmax": best[1]}
    except FileNotFoundError:
        d6["vs_registered_six"] = {"max_abs_corr": None, "argmax": None,
                                   "note": "t33 gates json absent"}

    ls = np.asarray(lead_sizes, dtype=int)
    facts = {
        "probe": "RRG-ROTATION-P1 G-ANCHOR + D6 freeze probe",
        "frozen_by": "r459 bm-a (berth r458 -> self-freeze, W5 r247->r248 mirror)",
        "construction_ref": "prereg s3 frozen (r216 digest clean-room); runner "
                            "verbatim-imports this file (r456 paradigm)",
        "cutoff": CUTOFF,
        "g_panel": {"n_syms": int(close.shape[1]),
                    "panel_first": str(close.index[0].date()),
                    "panel_last": str(close.index[-1].date()),
                    "n_days": int(len(close.index)),
                    "member_row_min": int(close.notna().sum().min()),
                    "member_row_max": int(close.notna().sum().max())},
        "nav_anchor": {"nav_first": round(float(nav.iloc[0]), 6),
                       "nav_last": round(float(nav.iloc[-1]), 6)},
        "month_end_census": {"n_month_ends": int(len(me_days)),
                             "first_decidable_me": first_decidable,
                             "n_decidable_me": int(len(decidable_mes)),
                             "n_me_no_decidable_member": int(no_decidable),
                             "n_me_zero_leading": int(zero_lead),
                             "n_me_carry_while_decidable": int(carry_while_decidable),
                             "leading_size_min": int(ls.min()) if len(ls) else None,
                             "leading_size_median": float(np.median(ls)) if len(ls) else None,
                             "leading_size_max": int(ls.max()) if len(ls) else None},
        "variants": {
            "base": {"top_k": 6, "position_size_pct": round(PS["base"], 6),
                     "n_trades_engine_face": int(ntr["base"]),
                     "mean_consecutive_jaccard": round(float(np.mean(jac["base"])), 4)},
            "unc": {"top_k": 2, "position_size_pct": round(PS["unc"], 6),
                    "n_trades_engine_face": int(ntr["unc"]),
                    "mean_consecutive_jaccard": round(float(np.mean(jac["unc"])), 4)},
            "unc_in_base_rate": round(contain_hit / contain_n, 4) if contain_n else None,
            "unc_in_base_n": int(contain_n)},
        "selection_records": recs,
        "d6": d6,
        "no_performance_metrics_persisted": True,
        "s7_discipline": "prereg s7 placeholder holds; probe persists only "
                        "structural faces + preregistered D6 corr",
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1)
    blob = json.dumps(facts)
    for bad in ("sharpe", "annual_return", "max_drawdown", "annual_ret"):
        assert bad not in blob, f"performance metric leaked into facts: {bad}"
    print("facts written:", OUT)
    print("month-ends:", facts["month_end_census"]["n_month_ends"],
          "| decidable:", facts["month_end_census"]["n_decidable_me"],
          "| leading min/med/max:",
          facts["month_end_census"]["leading_size_min"],
          facts["month_end_census"]["leading_size_median"],
          facts["month_end_census"]["leading_size_max"])
    print("d6:", json.dumps(d6, ensure_ascii=False)[:500])
    return 0


if __name__ == "__main__":
    sys.exit(run())
