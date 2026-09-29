"""T-101-V4-A10-REGIMECOMBO -- regime-gate "combination / input-feature" usage
first test: two frozen equal-weight combiners (C1 = member accept-gate-family
mean; C2 = 17-gate RECHECK library mean) -> continuous position w_t in [0,1],
T+1 open proxy, continuous-weight cost |dw|*cost_rate; window grid {6m,12m,24m}
x cost-x2 stress x segments x batch-own random-gate-combo nulls + dual nulls
+ G1'v2/G2v2/DSR/PBO (v4 regime-gate-arm combination subline judgment face).

Prereg: research/T-101-V4_A10_REGIMECOMBO_PREREG.md (FROZEN pre-run, r442 bm-a).
Upstream: GATE-TIMING-PRESCREEN-A158 (bm-c r231, 85 cells -> 13 SURVIVE-D6-ACCEPT)
-> T-101-V4-A158-FULLVERDICT (bm-a r441, 9-cell single-gate full verdict 0/9,
naming the combination/input-feature route + 588000|VSUMD30_q90 evidence face).

Zero reimplementation: execution machinery imported verbatim from
scripts/t101_v4_a158_fv.py (fv: dual_nulls/window_grid/g_p1/g_accept/cluster
machinery + template imports) + scripts/t101_v4_a2_prescreen.py (tpl) +
scripts/a158_tsgate_probe.py (probe frozen factor/gate single source);
judgment gates via science_gates shared library; PBO via screening/pbo.py
cscv_pbo (8 blocks frozen).

Trial batch: append_ledger("T-101-V4-A10-REGIMECOMBO", 16, ...) at finalize;
marks +0, SEED +2 (t101_v4_a10_combo_scrnull=20314000 +
t101_v4_a10_combo_unc=20314500, registered in the freeze commit per R250).

Exit contract: 0 = normal; 2 = fail-closed face gates (G-P1 / G-ACCEPT /
G-ANCHOR) -- report verbatim, never mask.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (HERE, os.path.join(os.path.dirname(HERE), "screening")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import science_gates as sg  # noqa: E402
import t101_v4_a2_prescreen as tpl  # noqa: E402  (r433 template machinery)
import t101_v4_a158_fv as fv  # noqa: E402  (r441 combinatorial-line mirror source)
import a158_tsgate_probe as probe  # noqa: E402  (frozen factor/gate single source)
from pbo import cscv_pbo  # noqa: E402  (CSCV 8 blocks, frozen)

EVIDENCE_CUTOFF = tpl.EVIDENCE_CUTOFF            # 2026-09-28 (upstream same face)
UNIVERSE = tpl.UNIVERSE                          # five-member frozen O-1555
SPLIT = tpl.SPLIT                                # 2017-01-01
COST_RATE = 0.001        # 0.1% per unit |dw| (conservative: 2x the 0/1-gate
COST_RATE_X2 = 0.002     # per-leg-equivalent; prereg sec.3 frozen definition)
NULL_K = tpl.NULL_K                              # 200/cell
MIN_OOS_TRADE_EVENTS = tpl.MIN_OOS_ENTRIES       # 15 (frozen trade-gate parity)
TRADE_EVENT_DW = 0.10                            # |dw|>=0.10 = trade event (frozen)
MAXDD_FLOOR = tpl.MAXDD_FLOOR                    # -0.35 descriptive clause
SCRNULL_BASE = sg.SEED_REGISTRY["t101_v4_a10_combo_scrnull"]   # 20314000
UNC_BASE = sg.SEED_REGISTRY["t101_v4_a10_combo_unc"]           # 20314500
WINDOWS = fv.WINDOWS                             # {6m:126, 12m:252, 24m:504}
WARMUP_END = fv.WARMUP_END                       # 120
PBO_N_BLOCKS = fv.PBO_N_BLOCKS                   # 8
RECHECK_JSON = fv.RECHECK_JSON                   # results/gate_recheck_a158.json
TSGATE_JSON = fv.TSGATE_JSON                     # results/a158_tsgate_p1.json
PRESCREEN_JSON = fv.PRESCREEN_JSON               # results/gate_timing_prescreen_a158.json
GATES17 = fv.GATES17                             # frozen 17-gate RECHECK table
ANCHOR_ROWS = fv.ANCHOR_ROWS                     # frozen row-count anchors
ACCEPT13 = fv.ACCEPT13                           # frozen 13 accept table
CELLS9 = fv.CELLS9                               # frozen collapsed 9 table
RESULTS_JSON = os.path.join(os.path.dirname(HERE), "results",
                            "t101_v4_a10_regimecombo.json")

# frozen C1 member->accept-gate-family map (r441 sec.0-C collapsed table
# regrouped by member; C1 = arithmetic mean of those gate open states)
C1_FAMILY = {
    "510300": ["RANK30_q90", "STD20_q90"],
    "510500": ["CNTN20_q10", "RANK30_q90", "RSQR10_q90", "SUMN10_q10"],
    "588000": ["STD10_q90", "STD20_q90", "VSUMD30_q90"],
}
C1_MEMBERS = sorted(C1_FAMILY)
COSTS = {"x1": COST_RATE, "x2": COST_RATE_X2}
CELLS16 = ([("C1", m, ck) for m in C1_MEMBERS for ck in COSTS]
           + [("C2", m, ck) for m in UNIVERSE for ck in COSTS])


def _fail(msg: str):
    print("FAIL-CLOSED: %s" % msg)
    raise SystemExit(2)


# ------------------------------------------------------- continuous-weight engine

def combo_position(gate_states: pd.DataFrame) -> pd.Series:
    """w_raw = equal-weight mean of pool gate open states (t-day state);
    w_eff = w_raw.shift(1) (T+1 open proxy, tpl.position_series semantics);
    warmup NaN -> 0. Zero search: equal weights frozen (prereg sec.0-C1)."""
    w_raw = gate_states.mean(axis=1).astype(float)
    w_eff = w_raw.shift(1).fillna(0.0)
    return w_eff


def combo_returns(df: pd.DataFrame, w_eff: pd.Series, cost_rate: float) -> pd.Series:
    """r_t = w_eff * close_ret - |dw_eff| * cost_rate (prereg sec.3 frozen
    continuous-weight cost caliber)."""
    r = df["close"].pct_change().fillna(0.0)
    dw = w_eff.diff().abs()
    if len(dw):
        dw.iloc[0] = abs(float(w_eff.iloc[0]))
    return (w_eff * r - dw.fillna(0.0) * cost_rate).fillna(0.0)


def count_trade_events(w_eff: pd.Series, sel: pd.Series | None = None) -> int:
    """|dw|>=0.10 trade events (frozen definition, prereg sec.3)."""
    dw = w_eff.diff().abs()
    if len(dw):
        dw.iloc[0] = abs(float(w_eff.iloc[0]))
    if sel is not None:
        dw = dw[sel]
    return int((dw >= TRADE_EVENT_DW).sum())


# ------------------------------------------------------------------ face gates

def g_p1_check():
    return fv.g_p1_check()


def g_accept_check():
    return fv.g_accept_check()


def load_panels():
    panels = {}
    for code in UNIVERSE:
        df = tpl.load_panel(code)   # FACE-MISMATCH VOID on tail != cutoff
        if len(df) != ANCHOR_ROWS[code]:
            _fail("G-ANCHOR VOID: %s rows %d != frozen anchor %d"
                  % (code, len(df), ANCHOR_ROWS[code]))
        panels[code] = df
    return panels


# ------------------------------------------------------------------ main burn

def run() -> int:
    t0 = time.time()
    g_p1_check()
    prescreen = g_accept_check()
    panels = load_panels()
    prev_head = sg.ledger_head()
    bm = panels["510300"]
    seg_by_date = pd.Series(tpl.regime_segment(bm).values, index=bm["date"].values)

    # frozen factor + gate masks per member (C2 needs all five; C1 needs 3)
    gate_masks = {}
    for code in UNIVERSE:
        F = probe.alpha158_factors(panels[code])
        if len(F) != probe.N_FACTORS:
            _fail("G-FACTORS VOID: %s factor table %d != %d"
                  % (code, len(F), probe.N_FACTORS))
        gates = {g[0]: (g[1], g[2]) for g in probe.gate_universe(F)}
        miss = [g for g in GATES17 if g not in gates]
        if miss:
            _fail("G-FACTORS VOID: gates absent from gate_universe: %s" % miss)
        gate_masks[code] = gates

    # gate-state frames per member per combiner pool
    pool_states = {}
    for code in UNIVERSE:
        c1_gates = C1_FAMILY.get(code)
        if c1_gates:
            pool_states[(code, "C1")] = pd.DataFrame(
                {g: gate_masks[code][g][0].astype(float)
                 for g in c1_gates}, index=panels[code].index)
        pool_states[(code, "C2")] = pd.DataFrame(
            {g: gate_masks[code][g][0].astype(float)
             for g in GATES17}, index=panels[code].index)

    # single-gate 9-cell daily returns (D6 same-source comparison face,
    # r441 construction verbatim) for the members that carry CELLS9
    fv_members = sorted({c.split("|")[0] for c in CELLS9})
    singlegate_returns = {}
    for code in fv_members:
        df = panels[code]
        for g in [c.split("|")[1] for c in CELLS9 if c.startswith(code + "|")]:
            pos = tpl.position_series(gate_masks[code][g][0])
            singlegate_returns["%s|%s" % (code, g)] = pd.Series(
                tpl.daily_returns(df, pos).values, index=df["date"].values)

    # PBO family grids per member: 17 single-gate configs + C1 + C2 combos
    # = same-gate-source tried-config universe (prereg sec.3 frozen family)
    pbo_grids = {}
    for code in UNIVERSE:
        df = panels[code]
        cols = {}
        for g in GATES17:
            pos = tpl.position_series(gate_masks[code][g][0])
            cols["SG|" + g] = tpl.daily_returns(df, pos).values
        for comb in ("C1", "C2"):
            key = (code, comb)
            if key not in pool_states:
                continue
            w = combo_position(pool_states[key])
            cols[comb] = combo_returns(df, w, COST_RATE).values
        mat = pd.DataFrame(cols, index=df["date"].values)
        if mat.shape[1] >= 8:
            pbo_grids[code] = {"pbo": float(cscv_pbo(mat, n_blocks=PBO_N_BLOCKS)["pbo"]),
                               "n_configs": int(mat.shape[1])}
        else:
            pbo_grids[code] = {"pbo": None, "n_configs": int(mat.shape[1]),
                               "note": "insufficient (<8) -- not a G2 input"}

    # per-member passive (own B&H full Sharpe) for the REPO_CALENDAR_P2 face
    bh_sharpe = {m: tpl.sharpe(panels[m]["close"].pct_change().fillna(0.0))
                 for m in UNIVERSE}

    cells, rows, null_values, cell_returns = {}, [], [], {}
    for cell_idx, (comb, code, ck) in enumerate(CELLS16):
        df = panels[code]
        cost_rate = COSTS[ck]
        w_eff = combo_position(pool_states[(code, comb)])
        r = combo_returns(df, w_eff, cost_rate)
        cell_id = "%s|%s|%s" % (comb, code, ck)
        cell_returns[cell_id] = r
        bh_ret = df["close"].pct_change().fillna(0.0)
        is_sel = df["date"] < SPLIT
        oos_sel = ~is_sel
        trades_full = count_trade_events(w_eff)
        oos_trades = count_trade_events(w_eff, oos_sel)

        base = {"full": {"sharpe": tpl.sharpe(r), "ann_ret": tpl.ann_ret(r),
                         "maxdd": tpl.max_drawdown(r)},
                "oos_excess_vs_bh": tpl.ann_ret(r[oos_sel]) - tpl.ann_ret(bh_ret[oos_sel]),
                "oos_trade_events": oos_trades}

        # random-gate-combo nulls K=200 (batch-own family pool; prereg sec.3):
        # each null = equal-weight mean of K_gates random gates drawn from the
        # member's own 314-gate universe, same construction / same cost.
        k_gates = len(C1_FAMILY[code]) if comb == "C1" else len(GATES17)
        rng = np.random.default_rng([SCRNULL_BASE, cell_idx])
        universe_names = np.array(sorted(gate_masks[code].keys()))
        cell_null_sharpes = []
        for _ in range(NULL_K):
            pick = rng.choice(universe_names, size=k_gates, replace=False)
            st = pd.DataFrame({g: gate_masks[code][g][0].astype(float)
                               for g in pick}, index=df.index)
            w_null = combo_position(st)
            cell_null_sharpes.append(tpl.sharpe(combo_returns(df, w_null, cost_rate)))
        null_values.extend(cell_null_sharpes)
        null_face = {"k": NULL_K, "k_gates": int(k_gates),
                     "med_sharpe": float(np.nanmedian(cell_null_sharpes)),
                     "p95_sharpe": float(np.nanpercentile(cell_null_sharpes, 95)),
                     "seed": [SCRNULL_BASE, cell_idx]}

        # dual nulls on full-period base daily returns (W1 semantics)
        dn = fv.dual_nulls(r.values, cell_idx)

        # window grid vs own-member B&H (r441 caliber)
        seg_lookup = seg_by_date.reindex(df["date"].values).fillna("na")
        wg = fv.window_grid(r, df["close"], seg_lookup)

        # OOS segments (descriptive)
        seg_stats = {}
        for segname in ("bear", "bull", "chop"):
            sel = ((seg_lookup == segname) & (df["date"].values >= SPLIT)).values
            if sel.sum() >= 30:
                seg_stats[segname] = {"oos_ann_ret": tpl.ann_ret(r[sel]),
                                      "oos_days": int(sel.sum())}

        # D6 face 1: vs five-member B&H (pairwise intersection, pit-115)
        sr = pd.Series(r.values, index=df["date"].values)
        d6_vs_bh = {}
        for bc in UNIVERSE:
            br = pd.Series(panels[bc]["close"].pct_change().fillna(0).values,
                           index=panels[bc]["date"].values)
            common = sr.index.intersection(br.index)
            if len(common) > 250:
                d6_vs_bh[bc] = round(float(np.corrcoef(
                    sr.loc[common], br.loc[common])[0, 1]), 4)
        d6_max_bh = max(abs(v) for v in d6_vs_bh.values())

        # D6 face 2 (prereg sec.1 pre-declared): vs r441 single-gate 9-cell
        # daily returns -- same gate-state source = beta same-source family;
        # max|corr|>=0.7 -> REJECT (beta duplicate, not an independent arm).
        d6_vs_sg = {}
        if code in fv_members:
            for sg_cell, sgr in singlegate_returns.items():
                if not sg_cell.startswith(code + "|"):
                    continue  # pairwise intersection within same member only
                common = sr.index.intersection(sgr.index)
                if len(common) > 250:
                    d6_vs_sg[sg_cell] = round(float(np.corrcoef(
                        sr.loc[common], sgr.loc[common])[0, 1]), 4)
        d6_max_sg = max((abs(v) for v in d6_vs_sg.values()), default=0.0)
        d6_verdict = ("REJECT_corr>=0.7" if d6_max_sg >= 0.7
                      else ("ACCEPT" if d6_max_bh < 0.7 else "REJECT_corr>=0.7_vs_bh"))

        cells[cell_id] = {
            "inst": code, "combiner": comb, "cost": ck,
            "base": base,
            "oos_excess_cost_x2_ref": None,  # x2 is its own cell (16-grid)
            "null": null_face, "dual_nulls": dn,
            "window_grid": wg, "segments_oos": seg_stats,
            "is_n": int(is_sel.sum()), "oos_n": int(oos_sel.sum()),
            "n_trades_full": trades_full,
            "w_stats": {"mean": float(w_eff.mean()), "std": float(w_eff.std()),
                        "min": float(w_eff.min()), "max": float(w_eff.max())},
            "d6": {"vs_bh": d6_vs_bh, "vs_singlegate9": d6_vs_sg,
                   "max_abs_vs_sg": d6_max_sg, "max_abs_vs_bh": d6_max_bh,
                   "verdict": d6_verdict},
        }
        rows.append({"cell": cell_id,
                     "sharpe_full": round(base["full"]["sharpe"], 4),
                     "oos_excess": round(base["oos_excess_vs_bh"], 6),
                     "full_maxdd": round(base["full"]["maxdd"], 4),
                     "oos_trades": oos_trades,
                     "null_med": round(null_face["med_sharpe"], 4),
                     "dn_ci_lower_positive": dn["ci_lower_positive"],
                     "dn_signflip_p": dn["signflip_p"],
                     "beat6m": wg["beat"]["6m"]["rate"],
                     "beat12m": wg["beat"]["12m"]["rate"],
                     "beat24m": wg["beat"]["24m"]["rate"],
                     "w_mean": round(float(w_eff.mean()), 4),
                     "d6_max_vs_sg": d6_max_sg})

    # batch-own null pool (P4_EXT_TILT face) + G1'/DSR/G2 per cell
    # (r442 zero-correction: NaN-safe coverage stats -- a random all-closed
    # gate combo yields a constant zero return series -> tpl.sharpe NaN;
    # 1/3200 in burn #1, its bare np.mean/np.std poisoned mu/sigma -> NaN ->
    # skill_line_v2 null_term NaN -> line degenerated to the passive floor
    # -> C1|510300|x1 pseudo g1_pass. Fix = stats over the valid subset with
    # nan_count disclosure, judgment NOT a criteria change.)
    null_arr = np.asarray(null_values, dtype=float)
    nan_count = int(np.isnan(null_arr).sum())
    valid_vals = null_arr[~np.isnan(null_arr)]
    null_pool = {"values": [float(v) for v in valid_vals],
                 "coverage": {"n_values": int(valid_vals.size),
                              "nan_excluded": nan_count,
                              "n_drawn": int(null_arr.size),
                              "schemas_parsed": ["T-101-V4-A10-REGIMECOMBO "
                                                 "random-gate-combo nulls "
                                                 "K=200 x 16 cells (batch-own, "
                                                 "NaN all-closed combos excluded "
                                                 "from stats with count)"],
                              "mu": float(np.mean(valid_vals)),
                              "sigma": float(np.std(valid_vals, ddof=1))}}
    n_trials_dsr = int(prev_head["total"]) + len(CELLS16)  # post-own-append head
    for cell_idx, cell_id in enumerate(list(cells.keys())):
        c = cells[cell_id]
        code = c["inst"]
        r = cell_returns[cell_id]
        g1 = sg.g1_prime_v2(c["base"]["full"]["sharpe"], list(r.values),
                            batch_cells=len(CELLS16),
                            n_trades=c["n_trades_full"],
                            n_entries=c["base"]["oos_trade_events"],
                            null_pool=null_pool, passive_override=bh_sharpe[code])
        dsr = sg.deflated_sharpe_ratio(list(r.values), n_trials=n_trials_dsr)
        member_pbo = pbo_grids[code]["pbo"]
        g2 = sg.g2_registration_v2(g1["pass_v2"], dsr, member_pbo)
        c["g1_prime_v2"] = g1
        c["dsr"] = dsr
        c["g2_registration_v2"] = g2
        c["member_family_pbo"] = pbo_grids[code]
        # FV-PASS four-clause conjunction (prereg sec.4); D6 REJECT blocks
        # registration eligibility (beta-duplicate pre-declaration).
        c["fv_pass"] = bool(g1["pass_v2"] and dsr["dsr"] >= 0.95
                            and g2["eligible_v2"]
                            and c["d6"]["verdict"] == "ACCEPT")
        c["fv_fail_reasons"] = [name for name, ok in (
            ("g1_prime_v2", g1["pass_v2"]),
            ("dsr>=0.95", dsr["dsr"] >= 0.95),
            ("g2_eligible", g2["eligible_v2"]),
            ("d6_accept", c["d6"]["verdict"] == "ACCEPT")) if not ok]
        if c["d6"]["verdict"] == "ACCEPT" and not (
                g1["pass_v2"] and dsr["dsr"] >= 0.95 and g2["eligible_v2"]):
            pass  # reasons already listed; D6-clean but gate-failed

    n_fv_pass = sum(1 for c in cells.values() if c["fv_pass"])
    n_d6_reject = sum(1 for c in cells.values()
                      if c["d6"]["verdict"].startswith("REJECT"))
    out = {
        "batch": "T-101-V4-A10-REGIMECOMBO",
        "prereg": "research/T-101-V4_A10_REGIMECOMBO_PREREG.md",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "science_gates": sg.cutoff_meta(EVIDENCE_CUTOFF),
        "universe": UNIVERSE, "cells_frozen": ["%s|%s|%s" % t for t in CELLS16],
        "combiners": {"C1": {"form": "accept-family equal-weight mean",
                             "member_map": C1_FAMILY},
                      "C2": {"form": "17-gate RECHECK library equal-weight mean",
                             "gates": GATES17}},
        "accept13_frozen": ACCEPT13, "cells9_frozen": CELLS9,
        "cost_rate": COST_RATE, "cost_rate_x2": COST_RATE_X2,
        "split": SPLIT, "windows": WINDOWS,
        "null_k": NULL_K, "scrnull_seed": SCRNULL_BASE, "unc_seed": UNC_BASE,
        "null_pool_batch_own": null_pool,
        "pbo_family_grids": pbo_grids,
        "n_fv_pass": n_fv_pass, "n_d6_reject": n_d6_reject,
        "cells": cells, "rows": rows,
        "audit": {"runtime_sec": None, "prev_head": prev_head,
                  "cpu_env": "single-process in-round (O-2100 trivial compute)"},
    }

    # descriptive batch clauses (prereg sec.4 disclosure lines)
    desc = []
    for cell_id, c in cells.items():
        if c["base"]["full"]["maxdd"] < MAXDD_FLOOR:
            desc.append("%s maxdd %.4f breaches -35%% floor" % (
                cell_id, c["base"]["full"]["maxdd"]))
    out["descriptive_breaches"] = desc
    out["e_fp_nominal_5pct"] = round(0.05 * len(CELLS16), 2)

    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    # ledger append at finalize (chain-linear; live prev_total read inside;
    # r442 zero-correction #2: return value MUST land in out["trials_ledger"]
    # -- dropping it = ledger silent no-op, r434 bm-a pitfall relapse caught
    # in-window by self-check before any commit of results)
    out["trials_ledger"] = sg.append_ledger(
        "T-101-V4-A10-REGIMECOMBO", len(CELLS16),
        os.path.basename(RESULTS_JSON),
        evidence_cutoff=EVIDENCE_CUTOFF,
        note="v4 regime-gate arm combination/input-feature subline: C1 "
             "accept-family mean + C2 17-gate library mean -> continuous "
             "weight; G1'v2/G2v2/DSR/PBO per shared library; zero-correction "
             "burn #2 (NaN-safe null coverage + trials_ledger landed)")
    out["audit"]["runtime_sec"] = round(time.time() - t0, 1)
    with open(RESULTS_JSON, "w", encoding="utf-8") as f:  # rewrite with ledger
        json.dump(out, f, ensure_ascii=False, indent=1)

    print("combo verdict: %d/%d FV-PASS (%d D6-REJECT) in %.1fs -> %s"
          % (n_fv_pass, len(CELLS16), n_d6_reject,
             out["audit"]["runtime_sec"], RESULTS_JSON))
    for row in rows:
        print("  %-16s sharpe=%7.4f oos_exc=%9.6f oos_trades=%4d "
              "null_med=%7.4f d6_sg=%.4f %s"
              % (row["cell"], row["sharpe_full"], row["oos_excess"],
                 row["oos_trades"], row["null_med"], row["d6_max_vs_sg"],
                 cells[row["cell"]]["fv_pass"] and "FV-PASS" or "fail"))
    return 0


# ------------------------------------------------------------------- selftest

def selftest() -> int:
    """Offline self-check (no network, no panel writes):
    (1) combo_position T+1 semantics -- signal day t does not move day t;
    (2) combo_returns cost mirror -- single-gate 0/1 pool reduces to
        |dw|-cost hand-calc;
    (3) random-gate null determinism -- same seed -> same draw sequence;
    (4) dual_nulls determinism (fv verbatim inherits);
    (5) trade-event counter hand-calc;
    (6) cells16 grid shape -- 16 = 3*2 + 5*2 frozen;
    (7) SEED_REGISTRY live-read -- both keys resolve to frozen bases.
    """
    ok = 0
    # (1) T+1 shift semantics: w_eff[0]=0 (no prior state), w_eff[t]=w_raw[t-1]
    idx = pd.RangeIndex(6)
    st = pd.DataFrame({"a": [0, 1, 1, 0, 0, 1], "b": [1, 1, 0, 0, 1, 1]},
                      dtype=float)
    w = combo_position(st)
    # w_raw = [0.5, 1.0, 0.5, 0.0, 0.5, 1.0] -> w_eff = [0, 0.5, 1.0, 0.5, 0.0, 0.5]
    assert abs(float(w.iloc[0]) - 0.0) < 1e-12, "day0 must be 0 (no prior state)"
    assert abs(float(w.iloc[1]) - 0.5) < 1e-12, "day1 w must equal day0 gate mean"
    assert abs(float(w.iloc[2]) - 1.0) < 1e-12, "day2 w must equal day1 gate mean"
    ok += 1
    # (2) cost mirror on a synthetic frame: single-gate pool -> |dw| costs
    df = pd.DataFrame({"close": [100.0, 101.0, 99.0, 102.0, 102.0]})
    w2 = pd.Series([0.0, 0.0, 1.0, 1.0, 0.0])
    r2 = combo_returns(df, w2, 0.001)
    # day1: w0->w1 no move, ret 1% * 0 = 0 ; day2: dw=1 -> cost 0.001, ret -1.98%*1
    assert abs(float(r2.iloc[1]) - 0.0) < 1e-12
    expect_d2 = (99.0 / 101.0 - 1.0) - 0.001
    assert abs(float(r2.iloc[2]) - expect_d2) < 1e-12, "cost mirror broken"
    ok += 1
    # (3) null determinism
    rng_a = np.random.default_rng([SCRNULL_BASE, 0])
    rng_b = np.random.default_rng([SCRNULL_BASE, 0])
    names = np.array(["g%03d" % i for i in range(314)])
    for _ in range(3):
        assert (rng_a.choice(names, size=17, replace=False)
                == rng_b.choice(names, size=17, replace=False)).all()
    ok += 1
    # (4) dual_nulls determinism (fv semantics verbatim)
    synth = np.random.default_rng(7).normal(0.0, 0.01, 500)
    d1 = fv.dual_nulls(synth, cell_idx=3)
    d2 = fv.dual_nulls(synth, cell_idx=3)
    assert d1 == d2, "dual-nulls determinism broken"
    d3 = fv.dual_nulls(synth, cell_idx=4)
    assert d3 != d1, "cell_idx must change the stream"
    ok += 1
    # (5) trade-event counter
    w5 = pd.Series([0.0, 0.05, 0.2, 0.25, 0.0, 0.11])
    n5 = count_trade_events(w5)   # dw: .05,.15,.05,.25,.11 -> >=0.10 -> 3
    assert n5 == 3, "trade-event hand-calc mismatch: %d" % n5
    ok += 1
    # (6) grid shape
    assert len(CELLS16) == 16, "cells16 shape must be 16"
    assert len([c for c in CELLS16 if c[0] == "C1"]) == 6
    assert len([c for c in CELLS16 if c[0] == "C2"]) == 10
    ok += 1
    # (7) SEED live-read
    assert sg.SEED_REGISTRY["t101_v4_a10_combo_scrnull"] == 20314000
    assert sg.SEED_REGISTRY["t101_v4_a10_combo_unc"] == 20314500
    ok += 1
    print("selftest: %d/7 PASS" % ok)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        raise SystemExit(selftest())
    if cmd == "run":
        raise SystemExit(run())
    print("usage: t101_v4_a10_regimecombo.py [run|selftest]")
    raise SystemExit(1)
