"""T-101-V4-A11-XSELECT -- five-member input-feature CROSS-SECTIONAL selector
combinator first test (non-timing face): three frozen features (RSV30 raw
ascending / 17-gate library open-mean descending / ROC20 raw descending) ->
stride-20 top-k equal-weight member selection, ALWAYS fully invested
(sum w = 1 every effective day, zero market-timing component), T+1 open
proxy (shift-1), continuous-weight |dw| cost (A10 caliber verbatim);
2 universes (U5 frozen five / U4 depth leg) x 2 costs -> 24 cells;
batch-own random-top-k-selection nulls K=200/cell + dual nulls (W1 semantics)
+ G1'v2/G2v2/DSR/PBO (v4 input-feature-arm cross-sectional subline judgment).

Prereg: research/T-101-V4_A11_XSELECT_PREREG.md (FROZEN pre-run, r443 bm-a).
Upstream: A10 r442 sec.8 downstream pointer ("C1 输入特征面=588000 门族供
T-101 v4 后续「输入特征组合器」（非择时面）消费；择时臂面勿再立项").

Zero reimplementation: panels/factors/gates via tpl + probe; dual nulls +
window grid + GATES17/ANCHOR_ROWS via fv; A10-cell D6 recomputation source =
t101_v4_a10_regimecombo (combo_position/combo_returns/C1_FAMILY verbatim);
judgment gates via science_gates shared library; PBO via screening/pbo.cscv_pbo
(8 blocks frozen). Common decidable window = first master date with ALL
members (RSV30 & ROC20 notna AND 17-gate decidable) -- structural cost of
cross-sectional membership, disclosed (U5 ~= 2021-05+, U4 ~= 2017-05+, both
post-SPLIT -> IS face structurally empty, disclosed in prereg sec.2).

Trial batch: append_ledger("T-101-V4-A11-XSELECT", 24, ...) at finalize;
return value MUST land in out["trials_ledger"] (r442 zero-correction law);
marks +0, SEED +2 (t101_v4_a11_xsel_scrnull=20315000 +
t101_v4_a11_xsel_unc=20315500, registered in the freeze commit per R250).

Exit contract: 0 = normal; 2 = fail-closed face gates (G-P1 / G-ACCEPT /
G-ANCHOR / G-FACTORS) -- report verbatim, never mask.
"""
from __future__ import annotations

import json
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
import t101_v4_a2_prescreen as tpl  # noqa: E402
import t101_v4_a158_fv as fv  # noqa: E402
import t101_v4_a10_regimecombo as a10  # noqa: E402
import a158_tsgate_probe as probe  # noqa: E402
from pbo import cscv_pbo  # noqa: E402  (CSCV 8 blocks, frozen)

EVIDENCE_CUTOFF = tpl.EVIDENCE_CUTOFF            # 2026-09-28 (A10 same face)
SPLIT = tpl.SPLIT                                # 2017-01-01
COST_RATE = a10.COST_RATE                        # 0.001 / unit |dw| (frozen)
COST_RATE_X2 = a10.COST_RATE_X2                  # 0.002
NULL_K = tpl.NULL_K                              # 200/cell
MIN_OOS_ENTRIES = tpl.MIN_OOS_ENTRIES            # 15 (frozen parity)
MAXDD_FLOOR = tpl.MAXDD_FLOOR                    # -0.35 descriptive clause
TRADE_EVENT_DW = a10.TRADE_EVENT_DW              # 0.10 (frozen)
STRIDE = 20                                       # stride-20 rebalance (frozen)
SCRNULL_BASE = sg.SEED_REGISTRY["t101_v4_a11_xsel_scrnull"]   # 20315000
UNC_BASE = sg.SEED_REGISTRY["t101_v4_a11_xsel_unc"]           # 20315500
GATES17 = fv.GATES17                             # frozen 17-gate table
ANCHOR_ROWS = fv.ANCHOR_ROWS                     # frozen row-count anchors
PBO_N_BLOCKS = fv.PBO_N_BLOCKS                   # 8
RESULTS_JSON = os.path.join(os.path.dirname(HERE), "results",
                            "t101_v4_a11_xselect.json")

UNIVERSES = {"U5": ["510300", "510050", "510500", "512100", "588000"],
             "U4": ["510300", "510050", "510500", "512100"]}
FEATURES = ["f_rsv30", "f_c2", "f_roc20"]        # frozen (prereg sec.0-X)
RANK_ASCENDING = {"f_rsv30": True,               # most oversold first
                  "f_c2": False,                 # most gates open first
                  "f_roc20": False}              # strongest momentum first
TOPK = [1, 2]
COSTS = {"x1": COST_RATE, "x2": COST_RATE_X2}
CELLS24 = [(u, f, k, ck) for u in ("U5", "U4") for f in FEATURES
           for k in TOPK for ck in COSTS]


def _fail(msg: str):
    print("FAIL-CLOSED: %s" % msg)
    raise SystemExit(2)


# ---------------------------------------------------- cross-sectional engine

def expand_rebal(sel_rebal: np.ndarray, counts: np.ndarray) -> np.ndarray:
    """(R, n_mem) per-rebal weights -> (n_days, n_mem) constant between
    rebalances (np.repeat along axis 0; sum(counts) == n_days)."""
    return np.repeat(sel_rebal, counts, axis=0)


def selection_weights(scores: pd.DataFrame, k: int,
                       rebal_idx: np.ndarray) -> pd.DataFrame:
    """Frozen cross-sectional selector: rank members at rebalance dates only
    (method='first' ties by member column order = code-ascending, frozen),
    top-k equal weight, constant between rebalances. scores = (n_days, n_mem)
    frame on the window; returns raw (pre-shift) weight frame."""
    n_days = len(scores)
    members = list(scores.columns)
    w = pd.DataFrame(0.0, index=scores.index, columns=members)
    sub = scores.iloc[rebal_idx]
    ranks = sub.rank(axis=1, method="first",
                     ascending=bool(RANK_ASCENDING[_CURRENT_FEATURE]))
    sel = (ranks <= k).astype(float) / k
    counts = np.diff(np.append(rebal_idx, n_days))
    w.loc[:] = expand_rebal(sel.values, counts)
    return w


# _CURRENT_FEATURE carries the frozen direction per cell (module-level to
# keep selection_weights signature frozen; set before each cell construction)
_CURRENT_FEATURE = FEATURES[0]


def cell_weights(scores: pd.DataFrame, feature: str, k: int,
                 rebal_idx: np.ndarray) -> pd.DataFrame:
    global _CURRENT_FEATURE
    _CURRENT_FEATURE = feature
    return selection_weights(scores, k, rebal_idx)


def xsection_returns(R: pd.DataFrame, w_eff: pd.DataFrame,
                     cost_rate: float) -> pd.Series:
    """r_t = sum_i w_eff,i,t * r_i,t - sum_i |dw_eff,i,t| * cost_rate
    (A10 combo_returns caliber extended cross-sectionally; first-day
    |dw| = own entry from zero, frozen)."""
    gross = (w_eff * R).sum(axis=1)
    dw = w_eff.diff().abs().sum(axis=1)
    if len(dw):
        dw.iloc[0] = float(w_eff.iloc[0].abs().sum())
    return (gross - dw.fillna(0.0) * cost_rate).fillna(0.0)


def count_trade_events_x(w_eff: pd.DataFrame, sel=None) -> int:
    """sum_i |dw_i| >= 0.10 trade events (frozen; top-1 switch = 2.0,
    top-2 one-member switch = 1.0 -> all membership changes counted)."""
    dw = w_eff.diff().abs().sum(axis=1)
    if len(dw):
        dw.iloc[0] = float(w_eff.iloc[0].abs().sum())
    if sel is not None:
        dw = dw[sel]
    return int((dw >= TRADE_EVENT_DW).sum())


def null_sharpes(R: pd.DataFrame, rebal_idx: np.ndarray, k: int,
                 cost_rate: float, cell_idx: int) -> np.ndarray:
    """K=200 random-top-k-selection nulls, same rebalance calendar, same
    construction/cost, zero timing component by construction. rng stream =
    [SCRNULL_BASE, cell_idx] (frozen). Vectorized: (K, R, n_mem) one-hot/k
    -> daily repeat -> shift-1 -> einsum returns."""
    n_days, n_mem = len(R.index), R.shape[1]
    counts = np.diff(np.append(rebal_idx, n_days))
    rng = np.random.default_rng([SCRNULL_BASE, cell_idx])
    n_rebal = len(rebal_idx)
    perm = rng.random((NULL_K, n_rebal, n_mem))
    pick = perm.argsort(axis=2)[:, :, :k]                 # (K, R, k)
    W_rebal = np.zeros((NULL_K, n_rebal, n_mem))
    for j in range(NULL_K):
        W_rebal[j, np.arange(n_rebal)[None, :], pick[j]] = 1.0 / k
    W_daily = np.repeat(W_rebal, counts, axis=1)         # (K, n, n_mem)
    W_eff = np.zeros_like(W_daily)
    W_eff[:, 1:, :] = W_daily[:, :-1, :]
    Rv = R.values                                        # (n, n_mem)
    gross = np.einsum("kdm,dm->kd", W_eff, Rv)
    dw = np.abs(np.diff(W_eff, axis=1, prepend=0.0)).sum(axis=2)
    net = gross - dw * cost_rate
    mu = net.mean(axis=1)
    sd = net.std(axis=1, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where(sd > 0, mu / sd * np.sqrt(252.0), np.nan)
    return out


# ------------------------------------------------------------------ face gates

def g_p1_check():
    return fv.g_p1_check()


def g_accept_check():
    return fv.g_accept_check()


def load_panels():
    panels = {}
    for code in sorted({c for m in UNIVERSES.values() for c in m}):
        df = tpl.load_panel(code)   # FACE-MISMATCH VOID on tail != cutoff
        if len(df) != ANCHOR_ROWS[code]:
            _fail("G-ANCHOR VOID: %s rows %d != frozen anchor %d"
                  % (code, len(df), ANCHOR_ROWS[code]))
        panels[code] = df
    return panels


def build_universe_face(panels, members):
    """Common decidable window + feature score frames + return matrix +
    EW passive (daily-rebalanced synthetic index, disclosed construction)."""
    master = None
    for m in members:
        d = pd.DatetimeIndex(panels[m]["date"])
        master = d if master is None else master.intersection(d)
    feats = {f: pd.DataFrame(index=master) for f in FEATURES}
    decidable = pd.Series(False, index=master)
    R = pd.DataFrame(index=master)
    for m in members:
        df = panels[m]
        F = probe.alpha158_factors(df)
        if len(F) != probe.N_FACTORS:
            _fail("G-FACTORS VOID: %s factor table %d != %d"
                  % (m, len(F), probe.N_FACTORS))
        gates = {g[0]: (g[1], g[2]) for g in probe.gate_universe(F)}
        miss = [g for g in GATES17 if g not in gates]
        if miss:
            _fail("G-FACTORS VOID: gates absent from gate_universe: %s" % miss)
        c2 = pd.concat([gates[g][0].astype(float) for g in GATES17],
                       axis=1).mean(axis=1)
        c2dec = pd.Series(True, index=df.index)
        for g in GATES17:
            c2dec = c2dec & gates[g][1]
        dec_m = (F["RSV30"].notna() & F["ROC20"].notna() & c2dec)
        feats["f_rsv30"][m] = F["RSV30"].reindex(master)
        feats["f_c2"][m] = c2.reindex(master)
        feats["f_roc20"][m] = F["ROC20"].reindex(master)
        decidable = decidable | dec_m.reindex(master).fillna(False).values
        r = df["close"].pct_change()
        R[m] = r.reindex(master)
    first = decidable[decidable].index
    if not len(first):
        _fail("G-WINDOW VOID: no common decidable date for %s" % members)
    start = first[0]
    window = master[master >= start]
    scores = {f: feats[f].loc[window] for f in FEATURES}
    Rw = R.loc[window].fillna(0.0)
    ew_ret = Rw.mean(axis=1)                      # daily-rebalanced EW
    ew_index = (1.0 + ew_ret).cumprod()
    n = len(window)
    rebal_idx = np.arange(0, n, STRIDE)
    return {"members": list(members), "window": window, "n_days": int(n),
            "start": str(window[0].date()), "scores": scores, "R": Rw,
            "ew_ret": ew_ret, "ew_index": ew_index, "rebal_idx": rebal_idx,
            "n_rebal": int(len(rebal_idx))}


# ------------------------------------------------------------------ main burn

def run() -> int:
    t0 = time.time()
    g_p1_check()
    g_accept_check()
    panels = load_panels()
    prev_head = sg.ledger_head()
    bm = panels["510300"]
    seg_by_date = pd.Series(tpl.regime_segment(bm).values, index=bm["date"].values)

    faces = {u: build_universe_face(panels, m) for u, m in UNIVERSES.items()}
    for u, fc in faces.items():
        print("face %s: window %s.. n=%d rebal=%d"
              % (u, fc["start"], fc["n_days"], fc["n_rebal"]))

    # ---- A10 16-cell + A9 9-cell D6 recomputation (import-verbatim source)
    gate_masks = {}
    for code in sorted({c for m in UNIVERSES.values() for c in m}):
        F = probe.alpha158_factors(panels[code])
        gate_masks[code] = {g[0]: (g[1], g[2]) for g in probe.gate_universe(F)}
    a10_returns = {}
    for comb, code, ck in a10.CELLS16:
        states = None
        if comb == "C1":
            states = pd.DataFrame({g: gate_masks[code][g][0].astype(float)
                                    for g in a10.C1_FAMILY[code]},
                                   index=panels[code].index)
        else:
            states = pd.DataFrame({g: gate_masks[code][g][0].astype(float)
                                    for g in GATES17},
                                   index=panels[code].index)
        w_eff = a10.combo_position(states)
        r = a10.combo_returns(panels[code], w_eff, a10.COST_RATE)
        a10_returns["%s|%s|%s" % (comb, code, ck)] = pd.Series(
            r.values, index=panels[code]["date"].values)
    fv_members = sorted({c.split("|")[0] for c in fv.CELLS9})
    sg_returns = {}
    for code in fv_members:
        df = panels[code]
        for g in [c.split("|")[1] for c in fv.CELLS9 if c.startswith(code + "|")]:
            pos = tpl.position_series(gate_masks[code][g][0])
            sg_returns["%s|%s" % (code, g)] = pd.Series(
                tpl.daily_returns(df, pos).values, index=df["date"].values)

    # ---- strategy construction for all 24 cells (PBO family input)
    cell_returns, cell_weff = {}, {}
    for cell_idx, (u, f, k, ck) in enumerate(CELLS24):
        fc = faces[u]
        w_raw = cell_weights(fc["scores"][f], f, k, fc["rebal_idx"])
        w_eff = w_raw.shift(1).fillna(0.0)
        cell_weff[cell_idx] = (u, f, k, ck, w_eff)
        cell_returns[cell_idx] = xsection_returns(fc["R"], w_eff, COSTS[ck])

    # ---- PBO family grids per universe: 12 configs (3 features x 2 topk x 2 costs)
    pbo_grids = {}
    for u in UNIVERSES:
        cols = {}
        for cell_idx, (uu, f, k, ck) in enumerate(CELLS24):
            if uu != u:
                continue
            cols["%s|top%d|%s" % (f, k, ck)] = cell_returns[cell_idx].values
        mat = pd.DataFrame(cols, index=faces[u]["window"])
        pbo_grids[u] = {"pbo": float(cscv_pbo(mat, n_blocks=PBO_N_BLOCKS)["pbo"]),
                        "n_configs": int(mat.shape[1])}

    # per-universe EW passive Sharpe (passive_override face)
    ew_sharpe = {u: tpl.sharpe(faces[u]["ew_ret"]) for u in UNIVERSES}

    cells, rows, null_values = {}, [], []
    for cell_idx, (u, f, k, ck) in enumerate(CELLS24):
        fc = faces[u]
        r = cell_returns[cell_idx]
        w_eff = cell_weff[cell_idx][4]
        cost_rate = COSTS[ck]
        members = fc["members"]
        win_dates = fc["window"]
        is_sel = pd.Series(win_dates < SPLIT, index=win_dates)
        oos_sel = ~is_sel
        trades_full = count_trade_events_x(w_eff)
        oos_trades = count_trade_events_x(w_eff, oos_sel[oos_sel.values].index)
        ew = fc["ew_ret"]

        base = {"full": {"sharpe": tpl.sharpe(r), "ann_ret": tpl.ann_ret(r),
                         "maxdd": tpl.max_drawdown(r)},
                "oos_excess_vs_ew": tpl.ann_ret(r[oos_sel]) - tpl.ann_ret(ew[oos_sel]),
                "oos_trade_events": oos_trades}

        # random-selection nulls K=200 (batch-own pool, nan-safe r442 law)
        ns = null_sharpes(fc["R"], fc["rebal_idx"], k, cost_rate, cell_idx)
        null_values.extend(ns.tolist())
        null_face = {"k": NULL_K, "med_sharpe": float(np.nanmedian(ns)),
                     "p95_sharpe": float(np.nanpercentile(ns, 95)),
                     "nan_excluded": int(np.isnan(ns).sum()),
                     "seed": [SCRNULL_BASE, cell_idx]}

        # dual nulls on cell returns (W1 semantics verbatim)
        dn = fv.dual_nulls(r.values, cell_idx)

        # window grid vs EW synthetic index (per-cell batch-own passive)
        seg_lookup = seg_by_date.reindex(win_dates).fillna("na")
        wg = fv.window_grid(r, fc["ew_index"], seg_lookup)

        # OOS segments (descriptive)
        seg_stats = {}
        for segname in ("bear", "bull", "chop"):
            sel = ((seg_lookup == segname) & oos_sel).values
            if sel.sum() >= 30:
                seg_stats[segname] = {"oos_ann_ret": tpl.ann_ret(r[sel]),
                                      "oos_days": int(sel.sum())}

        # D6 faces 1-3 (prereg sec.1 pre-declared)
        sr = pd.Series(r.values, index=win_dates)
        d6_vs_bh, d6_vs_a10, d6_vs_sg = {}, {}, {}
        for m in members:
            br = pd.Series(panels[m]["close"].pct_change().fillna(0).values,
                           index=panels[m]["date"].values)
            common = sr.index.intersection(br.index)
            if len(common) > 250:
                d6_vs_bh[m] = round(float(np.corrcoef(
                    sr.loc[common], br.loc[common])[0, 1]), 4)
        for tag, d6ret in (("vs_a10", a10_returns), ("vs_singlegate9", sg_returns)):
            tgt = d6_vs_a10 if tag == "vs_a10" else d6_vs_sg
            for c2, rs in d6ret.items():
                common = sr.index.intersection(rs.index)
                if len(common) > 250:
                    tgt[c2] = round(float(np.corrcoef(
                        sr.loc[common], rs.loc[common])[0, 1]), 4)
        maxima = {"vs_bh": max(abs(v) for v in d6_vs_bh.values()),
                  "vs_a10": max((abs(v) for v in d6_vs_a10.values()), default=0.0),
                  "vs_singlegate9": max((abs(v) for v in d6_vs_sg.values()), default=0.0)}
        d6_all_max = max(maxima.values())
        d6_verdict = "ACCEPT" if d6_all_max < 0.7 else "REJECT_corr>=0.7"

        cells[cell_idx] = {
            "cell_id": "%s|%s|top%d|%s" % (u, f, k, ck),
            "inst": u, "feature": f, "topk": k, "cost": ck,
            "base": base, "null": null_face, "dual_nulls": dn,
            "window_grid": wg, "segments_oos": seg_stats,
            "is_n": int(is_sel.sum()), "oos_n": int(oos_sel.sum()),
            "n_trades_full": trades_full,
            "w_stats": {"mean": float(w_eff.values.sum(axis=1).mean()),
                        "min_sum": float(w_eff.values.sum(axis=1).min()),
                        "max_sum": float(w_eff.values.sum(axis=1).max())},
            "d6": {"vs_bh": d6_vs_bh, "vs_a10": d6_vs_a10,
                   "vs_singlegate9": d6_vs_sg, "max_abs": maxima,
                   "all_max": d6_all_max, "verdict": d6_verdict},
        }

    # batch-own null pool (nan-safe coverage stats, r442 zero-correction law)
    null_arr = np.asarray(null_values, dtype=float)
    nan_count = int(np.isnan(null_arr).sum())
    valid_vals = null_arr[~np.isnan(null_arr)]
    if valid_vals.size < 10:
        _fail("G-NULL VOID: valid null pool %d < 10" % valid_vals.size)
    null_pool = {"values": [float(v) for v in valid_vals],
                 "coverage": {"n_values": int(valid_vals.size),
                              "nan_excluded": nan_count,
                              "n_drawn": int(null_arr.size),
                              "schemas_parsed": ["T-101-V4-A11-XSELECT "
                                                 "random-top-k-selection nulls "
                                                 "K=200 x 24 cells (batch-own, "
                                                 "NaN degenerate draws excluded "
                                                 "from stats with count)"],
                              "mu": float(np.mean(valid_vals)),
                              "sigma": float(np.std(valid_vals, ddof=1))}}

    n_trials_dsr = int(prev_head["total"]) + len(CELLS24)  # post-own-append head
    for cell_idx, c in cells.items():
        u, f, k, ck = CELLS24[cell_idx]
        r = cell_returns[cell_idx]
        g1 = sg.g1_prime_v2(c["base"]["full"]["sharpe"], list(r.values),
                            batch_cells=len(CELLS24),
                            n_trades=c["n_trades_full"],
                            n_entries=c["base"]["oos_trade_events"],
                            null_pool=null_pool, passive_override=ew_sharpe[u])
        dsr = sg.deflated_sharpe_ratio(list(r.values), n_trials=n_trials_dsr)
        fam_pbo = pbo_grids[u]["pbo"]
        g2 = sg.g2_registration_v2(g1["pass_v2"], dsr, fam_pbo)
        # clause 3 (prereg sec.4): x2-stress OOS excess > 0 -- an x1 cell reads
        # its frozen x2 twin; an x2 cell reads itself.
        twin_idx = (CELLS24.index((u, f, k, "x2")) if ck == "x1"
                    else cell_idx)
        clause3 = cells[twin_idx]["base"]["oos_excess_vs_ew"] > 0.0
        c["g1_prime_v2"] = g1
        c["dsr"] = dsr
        c["g2_registration_v2"] = g2
        c["member_family_pbo"] = pbo_grids[u]
        c["x2_oos_excess_clause"] = bool(clause3)
        c["fv_pass"] = bool(g1["pass_v2"] and dsr["dsr"] >= 0.95
                            and g2["eligible_v2"]
                            and clause3
                            and c["d6"]["verdict"] == "ACCEPT")
        c["fv_fail_reasons"] = [name for name, ok in (
            ("g1_prime_v2", g1["pass_v2"]),
            ("dsr>=0.95", dsr["dsr"] >= 0.95),
            ("g2_eligible", g2["eligible_v2"]),
            ("x2_oos_excess>0", clause3),
            ("d6_accept", c["d6"]["verdict"] == "ACCEPT")) if not ok]

    # in-batch 24x24 |corr| matrix (disclosure only, no in-batch kill)
    corrmat = {}
    for i in range(len(CELLS24)):
        ri = pd.Series(cell_returns[i])
        rowc = {}
        for j in range(len(CELLS24)):
            if i == j:
                rowc[j] = 1.0
                continue
            common = ri.index.intersection(pd.Series(cell_returns[j]).index)
            if len(common) > 250:
                rowc[j] = round(float(np.corrcoef(
                    ri.loc[common], pd.Series(cell_returns[j]).loc[common])[0, 1]), 4)
            else:
                rowc[j] = None
        corrmat[i] = rowc

    n_fv_pass = sum(1 for c in cells.values() if c["fv_pass"])
    n_d6_reject = sum(1 for c in cells.values()
                      if c["d6"]["verdict"].startswith("REJECT"))
    out = {
        "batch": "T-101-V4-A11-XSELECT",
        "prereg": "research/T-101-V4_A11_XSELECT_PREREG.md",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "science_gates": sg.cutoff_meta(EVIDENCE_CUTOFF),
        "universes": {u: {"members": UNIVERSES[u], "start": faces[u]["start"],
                          "n_days": faces[u]["n_days"],
                          "n_rebal": faces[u]["n_rebal"],
                          "ew_sharpe": ew_sharpe[u]}
                      for u in UNIVERSES},
        "cells_frozen": ["%s|%s|top%d|%s" % t for t in CELLS24],
        "rank_direction": RANK_ASCENDING,
        "stride": STRIDE, "cost_rate": COST_RATE, "cost_rate_x2": COST_RATE_X2,
        "split": SPLIT, "null_k": NULL_K,
        "scrnull_seed": SCRNULL_BASE, "unc_seed": UNC_BASE,
        "null_pool_batch_own": null_pool,
        "pbo_family_grids": pbo_grids,
        "n_fv_pass": n_fv_pass, "n_d6_reject": n_d6_reject,
        "cells": {str(i): cells[i] for i in cells},
        "in_batch_corr_matrix": corrmat,
        "audit": {"runtime_sec": None, "prev_head": prev_head,
                  "cpu_env": "single-process in-round (O-2100 trivial compute)"},
    }
    desc = []
    for i, c in cells.items():
        if c["base"]["full"]["maxdd"] < MAXDD_FLOOR:
            desc.append("%s maxdd %.4f breaches -35%% floor" % (
                c["cell_id"], c["base"]["full"]["maxdd"]))
    out["descriptive_breaches"] = desc
    out["e_fp_nominal_5pct"] = round(0.05 * len(CELLS24), 2)

    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    # ledger append at finalize (chain-linear; return value MUST land in
    # out["trials_ledger"] -- r442 zero-correction law #2, r434 pitfall face)
    out["trials_ledger"] = sg.append_ledger(
        "T-101-V4-A11-XSELECT", len(CELLS24),
        os.path.basename(RESULTS_JSON),
        evidence_cutoff=EVIDENCE_CUTOFF,
        note="v4 input-feature-arm cross-sectional selection subline: three "
             "frozen features -> stride-20 top-k always-invested selector; "
             "G1'v2/G2v2/DSR/PBO per shared library; batch-own "
             "random-selection nulls")
    out["audit"]["runtime_sec"] = round(time.time() - t0, 1)
    with open(RESULTS_JSON, "w", encoding="utf-8") as f:  # rewrite with ledger
        json.dump(out, f, ensure_ascii=False, indent=1)

    print("xselect verdict: %d/%d FV-PASS (%d D6-REJECT) in %.1fs -> %s"
          % (n_fv_pass, len(CELLS24), n_d6_reject,
             out["audit"]["runtime_sec"], RESULTS_JSON))
    for i in sorted(cells):
        c = cells[i]
        print("  %-22s sharpe=%7.4f oos_exc=%9.6f oos_trades=%4d "
              "null_med=%7.4f d6max=%.4f %s"
              % (c["cell_id"], c["base"]["full"]["sharpe"],
                 c["base"]["oos_excess_vs_ew"], c["base"]["oos_trade_events"],
                 c["null"]["med_sharpe"], c["d6"]["all_max"],
                 c["fv_pass"] and "FV-PASS" or "fail"))
    return 0


# ------------------------------------------------------------------- selftest

def selftest() -> int:
    """Offline self-check (no network, no panel writes):
    (1) T+1 shift + repeat-expansion constancy -- selection at t moves t+1
        only and weights are constant between rebalances (merged leg);
    (2) cross-sectional cost mirror -- membership entry |dw| hand-calc;
    (3) always-fully-invested invariant post first effective day;
    (4) random-selection null determinism (same seed -> same draws);
    (5) cells24 grid shape -- 2x3x2x2 frozen;
    (6) SEED_REGISTRY live-read -- both keys resolve to frozen bases;
    (7) trade-event counter hand-calc (top-1 switch = 2.0 >= 0.10).
    """
    global _CURRENT_FEATURE
    ok = 0
    idx = pd.date_range("2024-01-01", periods=8, freq="D")
    scores = pd.DataFrame({"a": [3.0, 1.0, 1.0, 2.0, 2.0, 1.0, 3.0, 3.0],
                           "b": [1.0, 3.0, 3.0, 1.0, 1.0, 3.0, 1.0, 1.0]},
                          index=idx)
    # (1)+(4): rebal at 0 and 5 (stride-5), top-1 ascending on scores
    _CURRENT_FEATURE = "f_rsv30"
    reb = np.array([0, 5])
    w = selection_weights(scores, 1, reb)
    # day0 scores: a=3,b=1 -> ascending top1 = b -> w_raw day0 = b
    assert abs(float(w.iloc[0]["b"]) - 1.0) < 1e-12, "day0 selection must be b"
    assert float(w.iloc[0]["a"]) == 0.0
    # constancy between rebalances: rows 0-4 identical, rows 5-7 identical
    assert (w.iloc[0:5].values == w.iloc[0].values).all(), "constancy broken"
    assert (w.iloc[5:8].values == w.iloc[5].values).all(), "constancy broken"
    ok += 1
    # (2) cost mirror: R frame, w_eff = shift of w
    R = pd.DataFrame({"a": [0.01, 0.02, -0.01, 0.0, 0.01, 0.0, 0.0, 0.0],
                     "b": [0.005, -0.01, 0.02, 0.01, 0.0, 0.01, 0.0, 0.0]},
                    index=idx)
    w_eff = w.shift(1).fillna(0.0)
    r = xsection_returns(R, w_eff, 0.001)
    # day0: w_eff=0 -> r=0 ; day1: w_eff=b -> gross=-0.01, dw=1 -> cost .001
    assert abs(float(r.iloc[0]) - 0.0) < 1e-12
    assert abs(float(r.iloc[1]) - (-0.01 - 0.001)) < 1e-12, "cost mirror broken"
    ok += 1
    # (3) always-fully-invested invariant (effective days)
    sums = w_eff.values.sum(axis=1)
    assert abs(sums[1:].min() - 1.0) < 1e-12 and abs(sums[1:].max() - 1.0) < 1e-12
    ok += 1
    # (5) null determinism + distinctness across cells
    ns_a = null_sharpes(R, reb, 1, 0.001, 0)
    ns_b = null_sharpes(R, reb, 1, 0.001, 0)
    assert np.array_equal(ns_a, ns_b, equal_nan=True), "null determinism"
    ns_c = null_sharpes(R, reb, 1, 0.001, 1)
    assert not np.array_equal(ns_a[:5], ns_c[:5]), "cell_idx must change stream"
    ok += 1
    # (6) grid shape
    assert len(CELLS24) == 24 and len(UNIVERSES) == 2 and len(FEATURES) == 3
    ok += 1
    # (7) SEED live-read
    assert sg.SEED_REGISTRY["t101_v4_a11_xsel_scrnull"] == 20315000
    assert sg.SEED_REGISTRY["t101_v4_a11_xsel_unc"] == 20315500
    ok += 1
    # (8) trade-event counter: top-1 membership switch |dw|=2.0
    idx2 = pd.date_range("2024-02-01", periods=4, freq="D")
    w2 = pd.DataFrame({"a": [0.0, 1.0, 0.0, 0.0], "b": [0.0, 0.0, 1.0, 1.0]},
                      index=idx2)
    n_ev = count_trade_events_x(w2)   # day1 entry |dw|=1, day2 switch |dw|=2
    assert n_ev == 2, "trade-event hand-calc mismatch: %d" % n_ev
    ok += 1
    print("selftest: %d/7 PASS" % ok)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        raise SystemExit(selftest())
    if cmd == "run":
        raise SystemExit(run())
    print("usage: t101_v4_a11_xselect.py [run|selftest]")
    raise SystemExit(1)
