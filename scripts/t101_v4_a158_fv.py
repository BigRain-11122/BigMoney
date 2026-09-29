"""T-101-V4-A158-FULLVERDICT -- A158 timing accept-13 (cluster-collapsed to 9)
full-verdict batch: window grid {6m,12m,24m} x cost-x2 stress x segments x
dual nulls + G1'v2/G2v2/DSR/PBO (v4 regime-gate-arm tournament judgment face).

Prereg: research/T-101-V4_A158_FULLVERDICT_PREREG.md (FROZEN pre-run, r441 bm-a).
Upstream: GATE-TIMING-PRESCREEN-A158 (bm-c r231, 85 cells -> 13 SURVIVE-D6-ACCEPT)
<- GATE-RECHECK-A158 (bm-a r439, 17-gate RECHECK-CONFIRM library).

Zero reimplementation: execution machinery imported verbatim from
scripts/t101_v4_a2_prescreen.py (tpl) + scripts/a158_tsgate_probe.py (probe);
judgment gates via science_gates shared library (g1_prime_v2 /
g2_registration_v2 / deflated_sharpe_ratio / append_ledger); PBO via
screening/pbo.py cscv_pbo (8 blocks frozen). Cost-x2 stress = template
daily_returns loop mirrored with cost parameterized; selftest asserts
byte-identity at the template's own cost (r366 mirror law).

Trial batch: append_ledger("T-101-V4-A158-FULLVERDICT", 9, ...) at finalize;
marks +0, SEED +2 (t101_v4_a158_fv_scrnull=20313000, t101_v4_a158_fv_unc=20313500,
registered in the freeze commit per R250 one-step law).

Exit contract: 0 = normal; 2 = fail-closed face gates (G-P1 / G-ACCEPT /
G-ANCHOR) -- report verbatim, never mask.
"""
from __future__ import annotations

import json
import math
import os
import sys
import tempfile
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (HERE, os.path.join(os.path.dirname(HERE), "screening")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import science_gates as sg  # noqa: E402
import t101_v4_a2_prescreen as tpl  # noqa: E402  (r433 template machinery)
import a158_tsgate_probe as probe  # noqa: E402  (frozen factor/gate single source)
from pbo import cscv_pbo  # noqa: E402  (CSCV 8 blocks, frozen)

EVIDENCE_CUTOFF = tpl.EVIDENCE_CUTOFF            # 2026-09-28 (upstream same face)
UNIVERSE = tpl.UNIVERSE                          # five-member frozen O-1555
SPLIT = tpl.SPLIT                                # 2017-01-01
COST_LEG = tpl.COST_LEG                          # 0.0005 base (0.1% RT)
COST_LEG_X2 = COST_LEG * 2.0                     # 0.001 stress (0.2% RT)
NULL_K = tpl.NULL_K                              # 200/cell
MIN_OOS_ENTRIES = tpl.MIN_OOS_ENTRIES            # 15 (upstream parity, descriptive)
MAXDD_FLOOR = tpl.MAXDD_FLOOR                    # -0.35 descriptive clause
SCRNULL_BASE = sg.SEED_REGISTRY["t101_v4_a158_fv_scrnull"]   # 20313000
UNC_BASE = sg.SEED_REGISTRY["t101_v4_a158_fv_unc"]           # 20313500
WINDOWS = {"6m": 126, "12m": 252, "24m": 504}    # trading-day holding horizons
WARMUP_END = 120                                 # first decidable bar idx 119 -> pos from 120
DUAL_NULL_B, DUAL_NULL_BLOCK, DUAL_NULL_P = 2000, 20, 2000   # W1 _dual_nulls semantics
PBO_N_BLOCKS = 8

GATES17 = ["CNTD5_q90", "CNTN20_q10", "MAX30_q10", "RANK30_q90", "RESI60_q90",
           "RSQR10_q90", "RSQR20_q90", "RSQR5_q90", "STD10_q90", "STD20_q90",
           "SUMD30_q90", "SUMD5_q90", "SUMN10_q10", "SUMN20_q10",
           "VSUMD10_q90", "VSUMD20_q90", "VSUMD30_q90"]

# frozen SURVIVE-D6-ACCEPT 13 (prereg sec.0-G-ACCEPT; live-read assert target)
ACCEPT13 = [
    "510300|RANK30_q90", "510300|STD20_q90",
    "510500|CNTN20_q10", "510500|RANK30_q90", "510500|RSQR10_q90", "510500|SUMN10_q10",
    "588000|RESI60_q90", "588000|STD10_q90", "588000|STD20_q90", "588000|SUMN10_q10",
    "588000|VSUMD10_q90", "588000|VSUMD20_q90", "588000|VSUMD30_q90",
]
# frozen cluster-collapsed 9 (prereg sec.0-C; live-read re-derive assert target)
CELLS9 = [
    "510300|RANK30_q90", "510300|STD20_q90",
    "510500|CNTN20_q10", "510500|RANK30_q90", "510500|RSQR10_q90", "510500|SUMN10_q10",
    "588000|STD10_q90", "588000|STD20_q90", "588000|VSUMD30_q90",
]

ANCHOR_ROWS = {"510300": 3486, "510050": 5251, "510500": 3289,
               "512100": 2405, "588000": 1425}

RESULTS_DIR = os.path.join(os.path.dirname(HERE), "results")
RECHECK_JSON = os.path.join(RESULTS_DIR, "gate_recheck_a158.json")
TSGATE_JSON = os.path.join(RESULTS_DIR, "a158_tsgate_p1.json")
PRESCREEN_JSON = os.path.join(RESULTS_DIR, "gate_timing_prescreen_a158.json")


def _fail(msg, code=2):
    print("[a158_fv] %s" % msg, flush=True)
    raise SystemExit(code)


# ------------------------------------------------------------------ machinery

def daily_returns_cost(df: pd.DataFrame, pos: pd.Series, cost_leg: float) -> pd.Series:
    """tpl.daily_returns loop VERBATIM with cost parameterized (r366 mirror law;
    selftest asserts byte-identity at cost=tpl.COST_LEG)."""
    o, c = df["open"].values, df["close"].values
    close_prev = np.roll(c, 1)
    close_prev[0] = np.nan
    ret = np.full(len(c), np.nan)
    p = pos.values
    for i in range(1, len(c)):
        if p[i] and p[i - 1]:
            ret[i] = c[i] / c[i - 1] - 1
        elif p[i] and not p[i - 1]:
            ret[i] = c[i] / o[i] - 1 - cost_leg
        elif not p[i] and p[i - 1]:
            ret[i] = o[i] / c[i - 1] - 1 - cost_leg
        else:
            ret[i] = 0.0
    return pd.Series(ret, index=df.index).fillna(0.0)


def cluster_collapse(accept_cells, prescreen):
    """Prereg sec.0-C frozen rule: per member, connected components over
    |corr|>=0.7 edges (intra_library_disclosure face) among accept cells;
    keep 1 per component = highest oos_excess_vs_bh, tie -> lowest gate name.
    Returns sorted surviving cell list."""
    by_member: dict = {}
    for cell in accept_cells:
        m, g = cell.split("|")
        by_member.setdefault(m, []).append(g)
    survivors = []
    for m, gates in by_member.items():
        pairs = prescreen["d6"]["intra_library_disclosure"][m]["pairs"]
        adj = {g: set() for g in gates}
        for key, corr in pairs.items():
            a, b = key.split("|")
            if a in adj and b in adj and abs(float(corr)) >= 0.7:
                adj[a].add(b)
                adj[b].add(a)
        seen = set()
        for g in gates:                      # connected components
            if g in seen:
                continue
            comp, stack = [], [g]
            seen.add(g)
            while stack:
                x = stack.pop()
                comp.append(x)
                for y in adj[x]:
                    if y not in seen:
                        seen.add(y)
                        stack.append(y)
            best = max(comp, key=lambda x: (
                float(prescreen["cells"]["%s|%s" % (m, x)]["oos_excess_vs_bh"]),
                [-ord(ch) for ch in x]))   # tie -> lexicographically lowest name
            survivors.append("%s|%s" % (m, best))
    return sorted(survivors)


def dual_nulls(returns, cell_idx):
    """W1 _dual_nulls semantics verbatim: circular block bootstrap B=2000
    (block=20) CI on the mean + sign-flip P=2000 two-sided p; seed
    [UNC_BASE, cell_idx]."""
    rng = np.random.default_rng([UNC_BASE, cell_idx])
    r = np.asarray(returns, dtype=float)
    n = len(r)
    mu = float(r.mean())
    B, block = DUAL_NULL_B, DUAL_NULL_BLOCK
    n_blocks = int(math.ceil(n / block))
    idx0 = rng.integers(0, max(1, n), size=(B, n_blocks))
    offs = np.arange(block)[None, None, :]
    gather = (idx0[:, :, None] + offs) % n
    boots = r[gather].reshape(B, -1)[:, :n].mean(axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    signs = rng.choice([-1.0, 1.0], size=(DUAL_NULL_P, n))
    perms = (r[None, :] * signs).mean(axis=1)
    p_two = float((np.abs(perms) >= abs(mu)).mean())
    return {"bootstrap_ci": [round(float(lo), 8), round(float(hi), 8)],
            "ci_lower_positive": bool(lo > 0),
            "signflip_p": round(p_two, 6),
            "B": B, "P": DUAL_NULL_P, "block": block}


def window_grid(r: pd.Series, close: pd.Series, seg_lookup: pd.Series):
    """{6m,12m,24m} virtual start windows, daily starts p in [WARMUP_END, n-w];
    beat = strategy window return > own-member B&H window return; segments by
    510300-MA200 regime at start (na bucket for undefined). W1 caliber."""
    eq = (1.0 + r).cumprod().values
    c = close.values
    n = len(eq)
    segs = {"bear": 0, "bull": 0, "chop": 0, "na": 0}
    beat = {}
    for wname, w in WINDOWS.items():
        k = tot = 0
        for p in range(WARMUP_END, n - w + 1):
            tot += 1
            cret = float(eq[p + w - 1] / eq[p] - 1.0)
            pret = float(c[p + w - 1] / c[p] - 1.0)
            if cret > pret:
                k += 1
            d = seg_lookup.iloc[p]
            segs[d if d in ("bear", "bull", "chop") else "na"] += 1
        beat[wname] = {"k": k, "n": tot,
                       "rate": round(k / tot, 6) if tot else 0.0}
    n_eff = sum(segs[s] for s in ("bear", "bull", "chop"))
    sufficient = bool(n_eff >= 500 and all(segs[s] >= 100
                                           for s in ("bear", "bull", "chop")))
    return {"beat": beat, "segments_start_windows": segs,
            "n_eff_start_windows": n_eff, "sample_sufficient": sufficient}


# ------------------------------------------------------------------ face gates

def g_p1_check():
    if not os.path.exists(RECHECK_JSON):
        _fail("G-P1 VOID: results/gate_recheck_a158.json absent")
    if not os.path.exists(TSGATE_JSON):
        _fail("G-P1 VOID: results/a158_tsgate_p1.json absent")
    with open(RECHECK_JSON, encoding="utf-8") as f:
        lib = json.load(f).get("library_entries")
    if sorted(lib or []) != sorted(GATES17):
        _fail("G-P1 VOID: recheck library_entries != frozen 17-gate table")
    with open(TSGATE_JSON, encoding="utf-8") as f:
        res = json.load(f)["results"]
    pass48 = {k for k, v in res.items() if v.get("verdict") == "PASS"}
    missing = [g for g in GATES17 if g not in pass48]
    if missing:
        _fail("G-P1 VOID: gates not in TSGATE PASS-48: %s" % missing)
    return lib


def g_accept_check():
    """Live-read upstream prescreen -> accept-13 == frozen table; re-derive
    cluster collapse == frozen 9. Fail-closed on any drift."""
    if not os.path.exists(PRESCREEN_JSON):
        _fail("G-ACCEPT VOID: results/gate_timing_prescreen_a158.json absent")
    with open(PRESCREEN_JSON, encoding="utf-8") as f:
        prescreen = json.load(f)
    if prescreen.get("evidence_cutoff") != EVIDENCE_CUTOFF:
        _fail("G-ACCEPT VOID: upstream evidence_cutoff drift")
    live13 = sorted(k for k, c in prescreen["cells"].items()
                    if c.get("verdict") == "SURVIVE"
                    and "ACCEPT" in str(c.get("d6", {}).get("verdict", "")))
    if live13 != sorted(ACCEPT13):
        _fail("G-ACCEPT VOID: live accept-13 != frozen table (upstream drift): "
              "live=%s" % live13)
    collapsed = cluster_collapse(ACCEPT13, prescreen)
    if collapsed != sorted(CELLS9):
        _fail("G-ACCEPT VOID: re-derived collapse != frozen 9: got=%s" % collapsed)
    return prescreen


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

def run():
    t0 = time.time()
    g_p1_check()
    prescreen = g_accept_check()
    panels = load_panels()
    prev_head = sg.ledger_head()
    bm = panels["510300"]
    seg_by_date = pd.Series(tpl.regime_segment(bm).values, index=bm["date"].values)

    # factors + gate masks per judged member (3 members carry the 9 cells)
    members = sorted({c.split("|")[0] for c in CELLS9})
    gate_masks = {}
    for code in members:
        F = probe.alpha158_factors(panels[code])
        if len(F) != probe.N_FACTORS:
            _fail("G-FACTORS VOID: %s factor table %d != %d"
                  % (code, len(F), probe.N_FACTORS))
        gates = {g[0]: (g[1], g[2]) for g in probe.gate_universe(F)}
        miss = [g for g in GATES17 if g not in gates]
        if miss:
            _fail("G-FACTORS VOID: gates absent from gate_universe: %s" % miss)
        gate_masks[code] = gates

    # PBO family grids: per member, 17 tried gate configs (canonical CSCV over
    # the full tried universe, prereg sec.3; own-calendar complete matrix)
    strat_daily17 = {}
    pbo_grids = {}
    for code in members:
        df = panels[code]
        cols = {}
        for g in GATES17:
            pos = tpl.position_series(gate_masks[code][g][0])
            cols[g] = tpl.daily_returns(df, pos).values
        mat = pd.DataFrame(cols, index=df["date"].values)
        strat_daily17[code] = mat
        pbo_grids[code] = cscv_pbo(mat, n_blocks=PBO_N_BLOCKS)

    # per-member passive (own B&H full Sharpe) for the REPO_CALENDAR_P2 face
    bh_sharpe = {m: tpl.sharpe(panels[m]["close"].pct_change().fillna(0.0))
                 for m in members}

    cells, rows, null_values, cell_returns = {}, [], [], {}
    for cell_idx, cell in enumerate(CELLS9):
        code, gate = cell.split("|")
        df = panels[code]
        mask = gate_masks[code][gate][0]
        pos = tpl.position_series(mask)
        r = tpl.daily_returns(df, pos)                      # base cost
        cell_returns[cell] = r
        r_x2 = daily_returns_cost(df, pos, COST_LEG_X2)    # x2 stress
        bh_ret = df["close"].pct_change().fillna(0.0)
        is_sel = df["date"] < SPLIT
        oos_sel = ~is_sel
        entries_full = tpl.count_entries(pos, pd.Series(True, index=df.index))
        oos_entries = tpl.count_entries(pos, oos_sel)

        base = {"full": {"sharpe": tpl.sharpe(r), "ann_ret": tpl.ann_ret(r),
                         "maxdd": tpl.max_drawdown(r)},
                "oos_excess_vs_bh": tpl.ann_ret(r[oos_sel]) - tpl.ann_ret(bh_ret[oos_sel]),
                "oos_entries": oos_entries}
        x2 = {"full": {"sharpe": tpl.sharpe(r_x2), "ann_ret": tpl.ann_ret(r_x2),
                       "maxdd": tpl.max_drawdown(r_x2)},
              "oos_excess_vs_bh": tpl.ann_ret(r_x2[oos_sel]) - tpl.ann_ret(bh_ret[oos_sel])}

        # same-mask circular-shift nulls K=200 (template semantics, batch seed)
        rng = np.random.default_rng(SCRNULL_BASE)
        pos_arr = pos.values.astype(int)
        cell_null_sharpes = []
        for _ in range(NULL_K):
            shift = int(rng.integers(1, len(pos_arr) - 1))
            r_null = tpl.daily_returns(df, pd.Series(
                np.roll(pos_arr, shift).astype(bool), index=df.index))
            cell_null_sharpes.append(tpl.sharpe(r_null))
        null_values.extend(cell_null_sharpes)
        null_face = {"k": NULL_K,
                     "med_sharpe": float(np.nanmedian(cell_null_sharpes)),
                     "p95_sharpe": float(np.nanpercentile(cell_null_sharpes, 95))}

        # dual nulls on full-period base daily returns (W1 semantics)
        dn = dual_nulls(r.values, cell_idx)

        # window grid vs own-member B&H
        seg_lookup = seg_by_date.reindex(df["date"].values).fillna("na")
        wg = window_grid(r, df["close"], seg_lookup)

        # OOS segments (descriptive, template caliber)
        seg_stats = {}
        for segname in ("bear", "bull", "chop"):
            sel = ((seg_lookup == segname) & (df["date"].values >= SPLIT)).values
            if sel.sum() >= 30:
                seg_stats[segname] = {"oos_ann_ret": tpl.ann_ret(r[sel]),
                                      "oos_days": int(sel.sum())}

        # D6 re-verification vs five-member B&H (pairwise intersection, pit-115)
        sr = pd.Series(r.values, index=df["date"].values)
        d6_vs_bh = {}
        for bc in UNIVERSE:
            br = pd.Series(panels[bc]["close"].pct_change().fillna(0).values,
                           index=panels[bc]["date"].values)
            common = sr.index.intersection(br.index)
            if len(common) > 250:
                d6_vs_bh[bc] = round(float(np.corrcoef(
                    sr.loc[common], br.loc[common])[0, 1]), 4)
        d6_max = max(abs(v) for v in d6_vs_bh.values())
        d6_verdict = "REJECT_corr>=0.7" if d6_max >= 0.7 else "ACCEPT"

        cells[cell] = {
            "inst": code, "gate": gate,
            "base": base, "cost_x2": x2,
            "cost_x2_stress_ok": bool(x2["oos_excess_vs_bh"] > 0),
            "null": null_face, "dual_nulls": dn,
            "window_grid": wg, "segments_oos": seg_stats,
            "is_n": int(is_sel.sum()), "oos_n": int(oos_sel.sum()),
            "n_entries_full": entries_full,
            "d6_recheck": {"vs_bh": d6_vs_bh, "max_abs": d6_max,
                           "verdict": d6_verdict},
        }
        rows.append({"cell": cell,
                     "sharpe_full": round(base["full"]["sharpe"], 4),
                     "oos_excess": round(base["oos_excess_vs_bh"], 6),
                     "x2_excess": round(x2["oos_excess_vs_bh"], 6),
                     "full_maxdd": round(base["full"]["maxdd"], 4),
                     "oos_entries": oos_entries,
                     "null_med": round(null_face["med_sharpe"], 4),
                     "dn_ci_lower_positive": dn["ci_lower_positive"],
                     "dn_signflip_p": dn["signflip_p"],
                     "beat6m": wg["beat"]["6m"]["rate"],
                     "beat12m": wg["beat"]["12m"]["rate"],
                     "beat24m": wg["beat"]["24m"]["rate"],
                     "n_eff_start_windows": wg["n_eff_start_windows"],
                     "sample_sufficient": wg["sample_sufficient"],
                     "d6_recheck_max": d6_max})

    # batch-own null pool (P4_EXT_TILT face) + G1'/DSR/G2 per cell
    null_pool = {"values": [float(v) for v in null_values],
                 "coverage": {"n_values": len(null_values),
                              "schemas_parsed": ["T-101-V4-A158-FULLVERDICT "
                                                 "same-mask circular-shift nulls "
                                                 "K=200 x 9 cells (batch-own)"],
                              "mu": float(np.mean(null_values)),
                              "sigma": float(np.std(null_values, ddof=1))}}
    n_trials_dsr = int(prev_head["total"]) + len(CELLS9)   # post-own-append head
    for cell_idx, cell in enumerate(CELLS9):
        c = cells[cell]
        code = c["inst"]
        r = cell_returns[cell]
        g1 = sg.g1_prime_v2(c["base"]["full"]["sharpe"], list(r.values),
                            batch_cells=len(CELLS9),
                            n_trades=c["n_entries_full"], n_entries=c["n_entries_full"],
                            null_pool=null_pool, passive_override=bh_sharpe[code])
        dsr = sg.deflated_sharpe_ratio(list(r.values), n_trials=n_trials_dsr)
        member_pbo = float(pbo_grids[code]["pbo"])
        g2 = sg.g2_registration_v2(g1["pass_v2"], dsr, member_pbo)
        c["g1_prime_v2"] = g1
        c["dsr"] = dsr
        c["g2_registration_v2"] = g2
        c["fv_pass"] = bool(g1["pass_v2"] and dsr["dsr"] >= 0.95
                            and c["cost_x2_stress_ok"] and g2["eligible_v2"])
        c["fv_fail_reasons"] = [name for name, ok in (
            ("g1_prime_v2", g1["pass_v2"]),
            ("dsr>=0.95", dsr["dsr"] >= 0.95),
            ("cost_x2_excess>0", c["cost_x2_stress_ok"]),
            ("g2_eligible", g2["eligible_v2"])) if not ok]

    n_fv_pass = sum(1 for c in cells.values() if c["fv_pass"])
    out = {
        "batch": "T-101-V4-A158-FULLVERDICT",
        "prereg": "research/T-101-V4_A158_FULLVERDICT_PREREG.md",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "science_gates": sg.cutoff_meta(EVIDENCE_CUTOFF),
        "universe": UNIVERSE, "cells_frozen": CELLS9,
        "accept13_frozen": ACCEPT13,
        "collapse_rule": "connected components |corr|>=0.7 per member on "
                         "prescreen intra_library_disclosure; keep highest "
                         "oos_excess_vs_bh, tie lowest gate name (prereg sec.0-C)",
        "collapsed_out": sorted(set(ACCEPT13) - set(CELLS9)),
        "split": SPLIT, "cost_leg": COST_LEG, "cost_leg_x2": COST_LEG_X2,
        "null_k": NULL_K, "scrnull_seed": SCRNULL_BASE, "unc_seed": UNC_BASE,
        "windows": WINDOWS,
        "null_pool_batch_own": null_pool,
        "pbo_face": {
            "family": "A158 quantile-gate timing module, 17 tried configs per "
                      "member (canonical CSCV over full tried universe; n=17>=8; "
                      "own-calendar complete matrix)",
            "grids": {m: {"pbo": pbo_grids[m]["pbo"], "n_trials": 17,
                          "n_rows": pbo_grids[m]["n_rows"],
                          "verdict": pbo_grids[m]["verdict"]}
                      for m in members},
            "judged_subgrids_insufficient": {
                "510300": 2, "510500": 4, "588000": 3},
            "note": "judged-cell sub-grids <8 per W10 frozen law -> insufficient "
                    "disclosure rows, NOT the G2 input (prereg sec.3)"},
        "e_fp_nominal_5pct": round(0.05 * len(CELLS9), 4),
        "dsr_n_trials": n_trials_dsr,
        "ledger_prev_head": prev_head,
        "cells": cells,
        "verdict_counts": {
            "n_cells": len(CELLS9),
            "g1_pass": sum(1 for c in cells.values() if c["g1_prime_v2"]["pass_v2"]),
            "dsr_ok": sum(1 for c in cells.values() if c["dsr"]["dsr"] >= 0.95),
            "cost_x2_ok": sum(1 for c in cells.values() if c["cost_x2_stress_ok"]),
            "g2_eligible": sum(1 for c in cells.values()
                               if c["g2_registration_v2"]["eligible_v2"]),
            "fv_pass": n_fv_pass,
        },
        "consumes": {"upstream": "results/gate_timing_prescreen_a158.json "
                                "(bm-c r231 accept-13) + results/gate_recheck_a158.json "
                                "(bm-a r439 17-gate library)",
                     "mechanism": "scripts/t101_v4_a2_prescreen.py + "
                                  "scripts/a158_tsgate_probe.py + science_gates + "
                                  "screening/pbo.py (import single-source)"},
        "audit": {"elapsed_sec": round(time.time() - t0, 1), "host": "bm-a",
                  "lane": "lane-free (five-member local panel, pure pandas)",
                  "workers": 1, "in_round_legal": "O-2100 trivial compute"},
    }

    # ledger append at finalize (chain-linear; live prev_total read inside)
    out["trials_ledger"] = sg.append_ledger(
        "T-101-V4-A158-FULLVERDICT", len(CELLS9), "t101_v4_a158_fv.json",
        evidence_cutoff=EVIDENCE_CUTOFF,
        note="v4 regime-gate arm full verdict: accept-13 cluster-collapsed to "
             "9; G1'v2/G2v2/DSR/PBO per shared library")

    with open(os.path.join(RESULTS_DIR, "t101_v4_a158_fv.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS_DIR, "t101_v4_a158_fv.csv"),
                              index=False)
    vc = out["verdict_counts"]
    print("elapsed=%ss cells=%d g1_pass=%d dsr_ok=%d cost_x2_ok=%d "
          "g2_eligible=%d FV_PASS=%d" % (
              out["audit"]["elapsed_sec"], vc["n_cells"], vc["g1_pass"],
              vc["dsr_ok"], vc["cost_x2_ok"], vc["g2_eligible"], vc["fv_pass"]))
    for row in rows:
        c = cells[row["cell"]]
        print("%-22s sharpe=%+.3f oos_exc=%+.4f x2_exc=%+.4f dn_ci+%s p=%.3f "
              "beat6m=%.3f n_eff=%d suff=%s g1=%s dsr=%.3f pbo=%.4f %s" % (
                  row["cell"], row["sharpe_full"], row["oos_excess"],
                  row["x2_excess"], row["dn_ci_lower_positive"],
                  row["dn_signflip_p"], row["beat6m"],
                  row["n_eff_start_windows"], row["sample_sufficient"],
                  c["g1_prime_v2"]["pass_v2"], c["dsr"]["dsr"],
                  out["pbo_face"]["grids"][c["inst"]]["pbo"],
                  ";".join(c["fv_fail_reasons"])))
    return 0


# ------------------------------------------------------------------ selftest

def selftest():
    """Hermetic offline selftest -- synth fixtures, zero repo pool writes."""
    tmp = tempfile.mkdtemp(prefix="a158_fv_selftest_")
    try:
        n = 500
        df = pd.DataFrame({
            "date": ["2020-01-%02d" % (d + 1) if d < 30 else "2020-02-%02d" % (d - 29)
                     for d in range(n)],
            "open": np.linspace(1, 2, n) + np.sin(np.arange(n) * .3) * .01,
            "close": np.linspace(1, 2, n),
            "high": np.linspace(1, 2, n) * 1.01,
            "low": np.linspace(1, 2, n) * 0.99,
            "volume": np.ones(n) * 1000.0})
        pos = pd.Series((np.arange(n) % 5 == 0), index=df.index)

        # (a) cost-mirror identity at template cost (r366 mirror law)
        a = daily_returns_cost(df, pos, tpl.COST_LEG).values
        b = tpl.daily_returns(df, pos).values
        assert np.allclose(a, b, equal_nan=True), "cost-mirror identity broken"

        # (b) cluster collapse rule: 2-component synthetic accept set
        prescreen = {"cells": {
            "M|A": {"oos_excess_vs_bh": 0.01}, "M|B": {"oos_excess_vs_bh": 0.03},
            "M|C": {"oos_excess_vs_bh": 0.02}, "M|D": {"oos_excess_vs_bh": 0.005}},
            "d6": {"intra_library_disclosure": {"M": {"pairs": {
                "A|B": 0.9, "B|C": 0.8, "A|C": 0.72, "A|D": 0.2,
                "B|D": 0.3, "C|D": 0.4}}}}}
        got = cluster_collapse(["M|A", "M|B", "M|C", "M|D"], prescreen)
        assert got == ["M|B", "M|D"], got   # {A,B,C}->B (max excess); D alone

        # (c) dual nulls determinism (same seed -> same CI/p)
        synth_r = np.sin(np.arange(n) * .05) * .01
        d1 = dual_nulls(synth_r, cell_idx=3)
        d2 = dual_nulls(synth_r, cell_idx=3)
        assert d1 == d2, "dual-nulls determinism broken"
        d3 = dual_nulls(synth_r, cell_idx=4)
        assert d3 != d1, "cell_idx must enter the seed"

        # (d) window-grid arithmetic on a hand-checkable tiny frame
        r = pd.Series(np.full(300, 0.001), index=range(300))
        close = pd.Series(np.linspace(1, 1.2, 300), index=range(300))
        seg = pd.Series("bull", index=range(300))
        wg = window_grid(r, close, seg)
        # n=300: 6m starts range(120, 175) -> 55; 12m/24m start ranges empty
        assert wg["beat"]["6m"]["n"] == 55, wg["beat"]["6m"]["n"]
        assert wg["beat"]["12m"]["n"] == 0 and wg["beat"]["24m"]["n"] == 0
        assert wg["segments_start_windows"]["bull"] == 55
        assert wg["n_eff_start_windows"] == 55   # below W1 sufficiency caliber
        assert wg["sample_sufficient"] is False   # 55 < 500 -> insufficient

        # (e) G-ACCEPT refusal: mismatched upstream -> exit 2 (hermetic file)
        bad = os.path.join(tmp, "bad_prescreen.json")
        with open(bad, "w", encoding="utf-8") as f:
            json.dump({"evidence_cutoff": EVIDENCE_CUTOFF,
                       "cells": {"510300|RANK30_q90": {
                           "verdict": "SURVIVE",
                           "d6": {"verdict": "ACCEPT"}}}}, f)
        global PRESCREEN_JSON
        saved = PRESCREEN_JSON
        try:
            PRESCREEN_JSON = bad
            try:
                g_accept_check()
                raise AssertionError("G-ACCEPT mismatch not refused")
            except SystemExit as e:
                assert e.code == 2
        finally:
            PRESCREEN_JSON = saved

        # (f) PBO grid sanity on synthetic 17-col matrix
        rng = np.random.default_rng(7)
        mat = pd.DataFrame(rng.normal(0.0005, 0.01, (400, 17)),
                           columns=GATES17,
                           index=pd.date_range("2020-01-01", periods=400, freq="B"))
        pbo_out = cscv_pbo(mat, n_blocks=PBO_N_BLOCKS)
        assert 0.0 <= pbo_out["pbo"] <= 1.0 and pbo_out["n_combinations"] == 70

        # (g) frozen tables: 9 subset of 13, no dups, sorted
        assert set(CELLS9) <= set(ACCEPT13)
        assert len(CELLS9) == len(set(CELLS9)) == 9
        assert len(ACCEPT13) == len(set(ACCEPT13)) == 13
        assert CELLS9 == sorted(CELLS9) and ACCEPT13 == sorted(ACCEPT13)
        assert ANCHOR_ROWS.keys() == set(UNIVERSE)
        print("selftest: all assertions PASS (cost-mirror identity / collapse "
              "rule / dual-nulls determinism / window-grid arithmetic / "
              "G-ACCEPT refusal / PBO grid / frozen tables)")
        return 0
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    args = sys.argv[1:]
    if args and args[0] == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
