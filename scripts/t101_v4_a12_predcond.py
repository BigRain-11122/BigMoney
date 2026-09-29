"""T-101-V4-A12-PREDCOND -- five-member vol/risk-CONDITIONED continuous
position face first test (non-timing non-selection): three frozen conditioners
(c_vtar = sleeve vol-targeted exposure w=clip(TVOL/sig20,0,1), EW member
weights; c_volinv = inverse-20d-vol member weights, always fully invested
zero timing component; c_vtar_volinv = exposure x composition interaction)
-> stride-20 rebalance calendar, T+1 open proxy (shift-1), continuous-weight
|dw| cost (A10/A11 caliber verbatim); 2 universes (U5 frozen five / U4 depth
leg) x 2 costs -> 12 cells; batch-own random-conditioning nulls K=200/cell
(same-shape random conditioner: U(0,1) exposure / Dirichlet(1) composition /
both) + dual nulls (W1 semantics) + G1'v2/G2v2/DSR/PBO (v4 residual
predictor/conditioning subline judgment).

Prereg: research/T-101-V4_A12_PREDCOND_PREREG.md (FROZEN pre-run, r445 bm-a).
Upstream: A11 r443 sec.8 downstream pointer ("输入特征路线残余去向=预测器/
条件化面（vol/风险条件化·非选择非择时）" + state next(a)).

Zero reimplementation: panels/regime/sharpe via tpl; dual nulls + window grid
+ GATES17/ANCHOR_ROWS/CELLS9 face gates via fv; A10-cell D6 source =
t101_v4_a10_regimecombo; A11-cell D6 source = t101_v4_a11_xselect (build_
universe_face/cell_weights/xsection_returns); single-gate A9 source = fv.CELLS9
+ tpl.position_series/daily_returns; judgment gates via science_gates shared
library; PBO via screening/pbo.cscv_pbo (8 blocks frozen).

Dual-nulls base wiring: fv.dual_nulls is W1 semantics verbatim but carries the
fv-batch module base; A10/A11 runners inherited fv's base (20313500) while
their preregs/metadata declared their own registered keys -- statistically
harmless (seed-arbitrary face), disclosed in prereg sec.8. A12 REBINDS
fv.UNC_BASE to its own registered key (20316500) BEFORE any dual_nulls call
so the prereg seed claim is the actual draw base.

Conditioner signals are trailing-only (sigma20 from data <= rebalance date;
TVOL = rolling 252d median min_periods=63 of sigma_ew20, NaN -> w_exp=1.0
full-exposure default at window head, disclosed); weights constant between
stride-20 rebalances; w_eff = w_raw.shift(1).

Trial batch: append_ledger("T-101-V4-A12-PREDCOND", 12, ...) at finalize;
return value MUST land in out["trials_ledger"] (r442 zero-correction law);
marks +0, SEED +2 (t101_v4_a12_predcond_scrnull=20316000 +
t101_v4_a12_predcond_unc=20316500, registered in the freeze commit).

Exit contract: 0 = normal; 2 = fail-closed face gates (G-P1 / G-ACCEPT /
G-ANCHOR / G-WINDOW / G-NULL) -- report verbatim, never mask.
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
import t101_v4_a11_xselect as a11  # noqa: E402
import a158_tsgate_probe as probe  # noqa: E402
from pbo import cscv_pbo  # noqa: E402  (CSCV 8 blocks, frozen)

EVIDENCE_CUTOFF = tpl.EVIDENCE_CUTOFF            # 2026-09-28 (A10/A11 same face)
SPLIT = tpl.SPLIT                                # 2017-01-01
COST_RATE = a10.COST_RATE                        # 0.001 / unit |dw| (frozen)
COST_RATE_X2 = a10.COST_RATE_X2                  # 0.002
NULL_K = tpl.NULL_K                              # 200/cell
MIN_OOS_ENTRIES = tpl.MIN_OOS_ENTRIES            # 15 (frozen parity)
MAXDD_FLOOR = tpl.MAXDD_FLOOR                    # -0.35 descriptive clause
TRADE_EVENT_DW = a10.TRADE_EVENT_DW              # 0.10 (frozen)
STRIDE = 20                                       # stride-20 rebalance (frozen)
VOL_WIN = 20                                      # sigma20 conditioner window
TVOL_WIN = 252                                    # TVOL trailing median window
TVOL_MIN = 63                                     # min_periods for TVOL median
SCRNULL_BASE = sg.SEED_REGISTRY["t101_v4_a12_predcond_scrnull"]   # 20316000
UNC_BASE = sg.SEED_REGISTRY["t101_v4_a12_predcond_unc"]           # 20316500
fv.UNC_BASE = UNC_BASE   # rebind BEFORE any dual_nulls call (see docstring)
GATES17 = fv.GATES17                             # frozen 17-gate table
ANCHOR_ROWS = fv.ANCHOR_ROWS                     # frozen row-count anchors
PBO_N_BLOCKS = fv.PBO_N_BLOCKS                   # 8
RESULTS_JSON = os.path.join(os.path.dirname(HERE), "results",
                            "t101_v4_a12_predcond.json")

UNIVERSES = {"U5": ["510300", "510050", "510500", "512100", "588000"],
             "U4": ["510300", "510050", "510500", "512100"]}
CONDITIONERS = ["c_vtar", "c_volinv", "c_vtar_volinv"]   # frozen (sec.0-X)
COSTS = {"x1": COST_RATE, "x2": COST_RATE_X2}
CELLS12 = [(u, c, ck) for u in ("U5", "U4") for c in CONDITIONERS
           for ck in ("x1", "x2")]
SIG_FLOOR = 1e-8


def _fail(msg: str):
    print("FAIL-CLOSED: %s" % msg)
    raise SystemExit(2)


# -------------------------------------------------- conditioner math (frozen)

def vtar_exposure(tvol: pd.Series, sig_ew: pd.Series) -> pd.Series:
    """w_exp = clip(TVOL / sigma_ew20, 0, 1); NaN TVOL (window head before
    TVOL_MIN obs) -> 1.0 full-exposure default; sigma floored defensively."""
    sig = sig_ew.clip(lower=SIG_FLOOR)
    w = (tvol / sig).clip(0.0, 1.0)
    return w.fillna(1.0)


def invvol_weights(sig_rebal: pd.DataFrame) -> pd.DataFrame:
    """w_i = (1/sigma_i) / sum_j (1/sigma_j) at rebalance dates only;
    rows sum to 1 (always fully invested face)."""
    inv = 1.0 / sig_rebal.clip(lower=SIG_FLOOR)
    return inv.div(inv.sum(axis=1), axis=0)


def expand_rebal(w_rebal: np.ndarray, counts: np.ndarray) -> np.ndarray:
    """(R, n_mem) per-rebalance weights -> (n_days, n_mem) constant between
    rebalances (np.repeat along axis 0; sum(counts) == n_days)."""
    return np.repeat(w_rebal, counts, axis=0)


def cell_weights(cond: str, w_exp_rebal: np.ndarray,
                  invn_rebal: np.ndarray, n_days: int,
                  window, members) -> pd.DataFrame:
    """Frozen conditioner -> raw (pre-shift) weight frame on the window."""
    n_mem = len(members)
    if cond == "c_vtar":
        w_rebal = (w_exp_rebal[:, None] / n_mem) * np.ones((1, n_mem))
    elif cond == "c_volinv":
        w_rebal = invn_rebal
    elif cond == "c_vtar_volinv":
        w_rebal = w_exp_rebal[:, None] * invn_rebal
    else:
        _fail("unknown conditioner %s" % cond)
    counts = np.diff(np.append(np.arange(0, n_days, STRIDE), n_days))
    w = expand_rebal(w_rebal, counts)
    return pd.DataFrame(w, index=window, columns=members)


def xsection_returns(R: pd.DataFrame, w_eff: pd.DataFrame,
                     cost_rate: float) -> pd.Series:
    return a11.xsection_returns(R, w_eff, cost_rate)   # verbatim import


def count_trade_events(w_eff: pd.DataFrame, sel=None) -> int:
    return a11.count_trade_events_x(w_eff, sel)        # verbatim import


def null_sharpes(R: pd.DataFrame, rebal_idx: np.ndarray, cond: str,
                 cost_rate: float, cell_idx: int) -> np.ndarray:
    """K=200 same-shape random-conditioning nulls on the same rebalance
    calendar, same construction/cost: c_vtar -> U(0,1) exposure + EW
    composition; c_volinv -> Dirichlet(1) composition, exposure 1;
    c_vtar_volinv -> both. rng stream = [SCRNULL_BASE, cell_idx] (frozen).
    Vectorized: (K, R, n_mem) -> daily repeat -> shift-1 -> einsum."""
    n_days, n_mem = len(R.index), R.shape[1]
    counts = np.diff(np.append(rebal_idx, n_days))
    n_rebal = len(rebal_idx)
    rng = np.random.default_rng([SCRNULL_BASE, cell_idx])
    if cond in ("c_vtar", "c_vtar_volinv"):
        w_exp_rand = rng.random((NULL_K, n_rebal))    # U(0,1) exposure
    else:
        w_exp_rand = np.ones((NULL_K, n_rebal))
    if cond in ("c_volinv", "c_vtar_volinv"):
        dir_w = rng.dirichlet(np.ones(n_mem),
                              size=(NULL_K, n_rebal))  # (K, R, n_mem)
    else:
        dir_w = np.full((NULL_K, n_rebal, n_mem), 1.0 / n_mem)
    W_rebal = w_exp_rand[:, :, None] * dir_w
    W_daily = np.repeat(W_rebal, counts, axis=1)      # (K, n, n_mem)
    W_eff = np.zeros_like(W_daily)
    W_eff[:, 1:, :] = W_daily[:, :-1, :]
    Rv = R.values
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
    """Vol-conditioner face: master = date intersection; sigma20 computed on
    the FULL master (20d warmup before the window cut, so the window head
    already carries sigma history); window = master[VOL_WIN:]; TVOL =
    trailing 252d median (min_periods=63) of sigma_ew20, NaN -> exposure 1.0.
    Conditioner signals are trailing-only (data <= rebalance date)."""
    master = None
    for m in members:
        d = pd.DatetimeIndex(panels[m]["date"])
        master = d if master is None else master.intersection(d)
    R = pd.DataFrame(index=master)
    for m in members:
        r = panels[m]["close"].pct_change()
        R[m] = pd.Series(r.values, index=pd.DatetimeIndex(panels[m]["date"])
                         ).reindex(master)
    sig_i = R.rolling(VOL_WIN).std()               # per-member sigma20
    ew_ret_full = R.mean(axis=1)
    sig_ew = ew_ret_full.rolling(VOL_WIN).std()    # sleeve sigma20
    tvol = sig_ew.rolling(TVOL_WIN, min_periods=TVOL_MIN).median()
    window = master[VOL_WIN:]
    n_days = len(window)
    if n_days <= STRIDE * 2:
        _fail("G-WINDOW VOID: window %d too short for %s" % (n_days, members))
    rebal_idx = np.arange(0, n_days, STRIDE)
    rebal_dates = window[rebal_idx]
    w_exp_rebal = vtar_exposure(tvol.loc[rebal_dates],
                                sig_ew.loc[rebal_dates]).values
    invn_rebal = invvol_weights(sig_i.loc[rebal_dates]).values
    n_default = int(np.count_nonzero(tvol.loc[rebal_dates].isna().values))
    Rw = R.loc[window].fillna(0.0)
    ew_ret = Rw.mean(axis=1)                        # daily-rebalanced EW
    ew_index = (1.0 + ew_ret).cumprod()
    return {"members": list(members), "window": window, "n_days": int(n_days),
            "start": str(window[0].date()), "R": Rw, "ew_ret": ew_ret,
            "ew_index": ew_index, "rebal_idx": rebal_idx,
            "n_rebal": int(len(rebal_idx)),
            "w_exp_rebal": w_exp_rebal, "invn_rebal": invn_rebal,
            "tvol_default_rebal": n_default}


# ------------------------------------------------------------------ main burn

def run() -> int:
    t0 = time.time()
    g_p1_check()
    g_accept_check()
    panels = load_panels()
    prev_head = sg.ledger_head()
    bm = panels["510300"]
    seg_by_date = pd.Series(tpl.regime_segment(bm).values,
                            index=pd.DatetimeIndex(bm["date"]))

    faces = {u: build_universe_face(panels, m) for u, m in UNIVERSES.items()}
    for u, fc in faces.items():
        print("face %s: window %s.. n=%d rebal=%d tvol_default_rebal=%d"
              % (u, fc["start"], fc["n_days"], fc["n_rebal"],
                 fc["tvol_default_rebal"]))

    # ---- D6 recomputation sources (import-verbatim, A11 pattern)
    date_idx = {code: pd.DatetimeIndex(panels[code]["date"]) for code in panels}
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
            r.values, index=date_idx[code])
    fv_members = sorted({c.split("|")[0] for c in fv.CELLS9})
    sg_returns = {}
    for code in fv_members:
        df = panels[code]
        for g in [c.split("|")[1] for c in fv.CELLS9 if c.startswith(code + "|")]:
            pos = tpl.position_series(gate_masks[code][g][0])
            sg_returns["%s|%s" % (code, g)] = pd.Series(
                tpl.daily_returns(df, pos).values, index=date_idx[code])
    a11_faces = {u: a11.build_universe_face(panels, m)
                 for u, m in a11.UNIVERSES.items()}
    a11_returns = {}
    for (u2, f, k, ck) in a11.CELLS24:
        fc = a11_faces[u2]
        w_raw = a11.cell_weights(fc["scores"][f], f, k, fc["rebal_idx"])
        w_eff = w_raw.shift(1).fillna(0.0)
        r = a11.xsection_returns(fc["R"], w_eff, a11.COSTS[ck])
        a11_returns["%s|%s|top%d|%s" % (u2, f, k, ck)] = r

    # ---- strategy construction for all 12 cells (PBO family input)
    cell_returns, cell_weff = {}, {}
    for cell_idx, (u, c, ck) in enumerate(CELLS12):
        fc = faces[u]
        w_raw = cell_weights(c, fc["w_exp_rebal"], fc["invn_rebal"],
                             fc["n_days"], fc["window"], fc["members"])
        w_eff = w_raw.shift(1).fillna(0.0)
        cell_weff[cell_idx] = (u, c, ck, w_eff)
        cell_returns[cell_idx] = xsection_returns(fc["R"], w_eff, COSTS[ck])

    # ---- PBO family grids per universe: 6 configs (3 conditioners x 2 costs)
    pbo_grids = {}
    for u in UNIVERSES:
        cols = {}
        for cell_idx, (uu, c, ck) in enumerate(CELLS12):
            if uu != u:
                continue
            cols["%s|%s" % (c, ck)] = cell_returns[cell_idx].values
        mat = pd.DataFrame(cols, index=faces[u]["window"])
        pbo_grids[u] = {"pbo": float(cscv_pbo(mat, n_blocks=PBO_N_BLOCKS)["pbo"]),
                        "n_configs": int(mat.shape[1])}

    ew_sharpe = {u: tpl.sharpe(faces[u]["ew_ret"]) for u in UNIVERSES}

    cells, rows, null_values = {}, [], []
    for cell_idx, (u, c, ck) in enumerate(CELLS12):
        fc = faces[u]
        r = cell_returns[cell_idx]
        w_eff = cell_weff[cell_idx][3]
        cost_rate = COSTS[ck]
        members = fc["members"]
        win_dates = fc["window"]
        is_sel = pd.Series(win_dates < SPLIT, index=win_dates)
        oos_sel = ~is_sel
        trades_full = count_trade_events(w_eff)
        oos_trades = count_trade_events(w_eff, oos_sel[oos_sel.values].index)
        ew = fc["ew_ret"]

        base = {"full": {"sharpe": tpl.sharpe(r), "ann_ret": tpl.ann_ret(r),
                         "maxdd": tpl.max_drawdown(r)},
                "oos_excess_vs_ew": tpl.ann_ret(r[oos_sel]) - tpl.ann_ret(ew[oos_sel]),
                "oos_trade_events": oos_trades}

        ns = null_sharpes(fc["R"], fc["rebal_idx"], c, cost_rate, cell_idx)
        null_values.extend(ns.tolist())
        null_face = {"k": NULL_K, "med_sharpe": float(np.nanmedian(ns)),
                     "p95_sharpe": float(np.nanpercentile(ns, 95)),
                     "nan_excluded": int(np.isnan(ns).sum()),
                     "seed": [SCRNULL_BASE, cell_idx]}

        dn = fv.dual_nulls(r.values, cell_idx)

        seg_lookup = seg_by_date.reindex(win_dates).fillna("na")
        wg = fv.window_grid(r, fc["ew_index"], seg_lookup)

        seg_stats = {}
        for segname in ("bear", "bull", "chop"):
            sel = ((seg_lookup == segname) & oos_sel).values
            if sel.sum() >= 30:
                seg_stats[segname] = {"oos_ann_ret": tpl.ann_ret(r[sel]),
                                      "oos_days": int(sel.sum())}

        # D6 faces 1-4 (prereg sec.1 pre-declared)
        sr = pd.Series(r.values, index=win_dates)
        d6_vs_bh, d6_vs_a10, d6_vs_sg, d6_vs_a11 = {}, {}, {}, {}
        for m in members:
            br = pd.Series(panels[m]["close"].pct_change().fillna(0).values,
                           index=date_idx[m])
            common = sr.index.intersection(br.index)
            if len(common) > 250:
                d6_vs_bh[m] = round(float(np.corrcoef(
                    sr.loc[common], br.loc[common])[0, 1]), 4)
        for tag, d6ret, tgt in (("vs_a10", a10_returns, d6_vs_a10),
                                ("vs_singlegate9", sg_returns, d6_vs_sg),
                                ("vs_a11", a11_returns, d6_vs_a11)):
            for c2, rs in d6ret.items():
                common = sr.index.intersection(rs.index)
                if len(common) > 250:
                    tgt[c2] = round(float(np.corrcoef(
                        sr.loc[common], rs.loc[common])[0, 1]), 4)
        maxima = {"vs_bh": max(abs(v) for v in d6_vs_bh.values()),
                  "vs_a10": max((abs(v) for v in d6_vs_a10.values()), default=0.0),
                  "vs_singlegate9": max((abs(v) for v in d6_vs_sg.values()), default=0.0),
                  "vs_a11": max((abs(v) for v in d6_vs_a11.values()), default=0.0)}
        d6_all_max = max(maxima.values())
        d6_verdict = "ACCEPT" if d6_all_max < 0.7 else "REJECT_corr>=0.7"

        exposure = w_eff.values.sum(axis=1)
        cells[cell_idx] = {
            "cell_id": "%s|%s|%s" % (u, c, ck),
            "inst": u, "conditioner": c, "cost": ck,
            "base": base, "null": null_face, "dual_nulls": dn,
            "window_grid": wg, "segments_oos": seg_stats,
            "is_n": int(is_sel.sum()), "oos_n": int(oos_sel.sum()),
            "n_trades_full": trades_full,
            "w_stats": {"mean_exposure": float(exposure.mean()),
                        "min_exposure": float(exposure.min()),
                        "max_exposure": float(exposure.max())},
            "d6": {"vs_bh": d6_vs_bh, "vs_a10": d6_vs_a10,
                   "vs_singlegate9": d6_vs_sg, "vs_a11": d6_vs_a11,
                   "max_abs": maxima, "all_max": d6_all_max,
                   "verdict": d6_verdict},
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
                              "schemas_parsed": ["T-101-V4-A12-PREDCOND "
                                                "same-shape random-conditioning "
                                                "nulls K=200 x 12 cells "
                                                "(batch-own, NaN degenerate "
                                                "draws excluded from stats "
                                                "with count)"],
                              "mu": float(np.mean(valid_vals)),
                              "sigma": float(np.std(valid_vals, ddof=1))}}

    n_trials_dsr = int(prev_head["total"]) + len(CELLS12)  # post-own-append head
    for cell_idx, c in cells.items():
        u, cond, ck = CELLS12[cell_idx]
        r = cell_returns[cell_idx]
        g1 = sg.g1_prime_v2(c["base"]["full"]["sharpe"], list(r.values),
                            batch_cells=len(CELLS12),
                            n_trades=c["n_trades_full"],
                            n_entries=c["base"]["oos_trade_events"],
                            null_pool=null_pool, passive_override=ew_sharpe[u])
        dsr = sg.deflated_sharpe_ratio(list(r.values), n_trials=n_trials_dsr)
        fam_pbo = pbo_grids[u]["pbo"]
        g2 = sg.g2_registration_v2(g1["pass_v2"], dsr, fam_pbo)
        twin_idx = (CELLS12.index((u, cond, "x2")) if ck == "x1"
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

    # in-batch 12x12 |corr| matrix (disclosure only, no in-batch kill)
    corrmat = {}
    for i in range(len(CELLS12)):
        ri = pd.Series(cell_returns[i])
        rowc = {}
        for j in range(len(CELLS12)):
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
        "batch": "T-101-V4-A12-PREDCOND",
        "prereg": "research/T-101-V4_A12_PREDCOND_PREREG.md",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "science_gates": sg.cutoff_meta(EVIDENCE_CUTOFF),
        "universes": {u: {"members": UNIVERSES[u], "start": faces[u]["start"],
                          "n_days": faces[u]["n_days"],
                          "n_rebal": faces[u]["n_rebal"],
                          "tvol_default_rebal": faces[u]["tvol_default_rebal"],
                          "ew_sharpe": ew_sharpe[u]}
                      for u in UNIVERSES},
        "cells_frozen": ["%s|%s|%s" % t for t in CELLS12],
        "conditioners": CONDITIONERS,
        "vol_win": VOL_WIN, "tvol_win": TVOL_WIN, "tvol_min": TVOL_MIN,
        "stride": STRIDE, "cost_rate": COST_RATE, "cost_rate_x2": COST_RATE_X2,
        "split": SPLIT, "null_k": NULL_K,
        "scrnull_seed": SCRNULL_BASE, "unc_seed": UNC_BASE,
        "unc_base_wiring": "fv.UNC_BASE rebound to batch key pre-call "
                          "(A10/A11 inherited fv base 20313500 -- "
                          "disclosure note, seed-arbitrary face)",
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
    out["e_fp_nominal_5pct"] = round(0.05 * len(CELLS12), 2)

    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    # ledger append at finalize (chain-linear; return value MUST land in
    # out["trials_ledger"] -- r442 zero-correction law #2, r434 pitfall face)
    out["trials_ledger"] = sg.append_ledger(
        "T-101-V4-A12-PREDCOND", len(CELLS12),
        os.path.basename(RESULTS_JSON),
        evidence_cutoff=EVIDENCE_CUTOFF,
        note="v4 residual predictor/conditioning face: vol/risk-conditioned "
             "continuous position (c_vtar exposure / c_volinv composition / "
             "interaction); G1'v2/G2v2/DSR/PBO per shared library; batch-own "
             "same-shape random-conditioning nulls")
    out["audit"]["runtime_sec"] = round(time.time() - t0, 1)
    with open(RESULTS_JSON, "w", encoding="utf-8") as f:  # rewrite with ledger
        json.dump(out, f, ensure_ascii=False, indent=1)

    print("predcond verdict: %d/%d FV-PASS (%d D6-REJECT) in %.1fs -> %s"
          % (n_fv_pass, len(CELLS12), n_d6_reject,
             out["audit"]["runtime_sec"], RESULTS_JSON))
    for i in sorted(cells):
        c = cells[i]
        print("  %-22s sharpe=%7.4f oos_exc=%9.6f oos_trades=%4d "
              "null_med=%7.4f d6max=%.4f exp=%.2f %s"
              % (c["cell_id"], c["base"]["full"]["sharpe"],
                 c["base"]["oos_excess_vs_ew"], c["base"]["oos_trade_events"],
                 c["null"]["med_sharpe"], c["d6"]["all_max"],
                 c["w_stats"]["mean_exposure"],
                 c["fv_pass"] and "FV-PASS" or "fail"))
    return 0


# ------------------------------------------------------------------- selftest

def selftest() -> int:
    """Offline self-check (no network, no panel reads):
    (1) vtar exposure formula: clip(TVOL/sig,0,1) + NaN-TVOL -> 1.0;
    (2) inverse-vol weights: sum-to-1 + low-vol member gets more;
    (3) expand_rebal + shift constancy (weights constant between
        rebalances; T+1 shift);
    (4) null determinism per cell + distinctness across cells;
    (5) cells12 grid shape 2x3x2 frozen;
    (6) SEED_REGISTRY live-read both keys;
    (7) trade-event counter hand-calc (via a11 verbatim import);
    (8) cost mirror: first-day entry |dw| cost hand-calc;
    (9) fv.UNC_BASE rebound to batch key (wiring check).
    """
    ok = 0
    idx = pd.date_range("2024-01-01", periods=6, freq="D")
    # (1) vtar exposure
    tvol = pd.Series([np.nan, 0.010, 0.030, 0.005, 0.020, 0.010], index=idx)
    sig = pd.Series([0.010, 0.020, 0.010, 0.010, 0.010, 0.010], index=idx)
    w = vtar_exposure(tvol, sig)
    assert abs(float(w.iloc[0]) - 1.0) < 1e-12, "NaN TVOL must default 1.0"
    assert abs(float(w.iloc[1]) - 0.5) < 1e-12, "TVOL/sig hand-calc"
    assert abs(float(w.iloc[2]) - 1.0) < 1e-12, "clip upper at 1.0"
    assert abs(float(w.iloc[3]) - 0.5) < 1e-12, "clip lower, 0.005/0.010"
    assert abs(float(w.iloc[4]) - 1.0) < 1e-12
    assert abs(float(w.iloc[5]) - 1.0) < 1e-12
    ok += 1
    # (2) inverse-vol weights
    sigf = pd.DataFrame({"a": [0.01, 0.02], "b": [0.02, 0.01]},
                        index=[idx[0], idx[1]])
    iv = invvol_weights(sigf)
    assert abs(float(iv.iloc[0]["a"]) - 2.0 / 3.0) < 1e-12, "invvol a"
    assert abs(float(iv.iloc[1]["a"]) - 1.0 / 3.0) < 1e-12, "invvol flip"
    assert np.allclose(iv.sum(axis=1).values, 1.0), "sum-to-1"
    ok += 1
    # (3) expand + shift constancy: 60 days, STRIDE=20 -> rebal at 0,20,40
    w_exp_r = np.array([0.5, 1.0, 0.8])
    invn_r = np.full((3, 2), 0.5)
    win = pd.date_range("2024-01-01", periods=60, freq="D")
    w_raw = cell_weights("c_vtar", w_exp_r, invn_r, 60, win, ["a", "b"])
    assert (w_raw.iloc[0:20].values == w_raw.iloc[0].values).all()
    assert (w_raw.iloc[20:40].values == w_raw.iloc[20].values).all()
    assert (w_raw.iloc[40:60].values == w_raw.iloc[40].values).all()
    assert abs(float(w_raw.iloc[0].sum()) - 0.5) < 1e-12
    assert abs(float(w_raw.iloc[20].sum()) - 1.0) < 1e-12
    assert abs(float(w_raw.iloc[40].sum()) - 0.8) < 1e-12
    w_eff = w_raw.shift(1).fillna(0.0)
    assert float(w_eff.iloc[0].sum()) == 0.0, "T+1 first day flat"
    ok += 1
    # (4) null determinism + cell distinctness (c_vtar shape, 60d stride-20)
    R = pd.DataFrame({"a": np.tile([0.01, 0.02, -0.01, 0.0], 15),
                      "b": np.tile([0.005, -0.01, 0.02, 0.01], 15)},
                     index=win)
    reb = np.array([0, 20, 40])
    ns_a = null_sharpes(R, reb, "c_vtar", 0.001, 0)
    ns_b = null_sharpes(R, reb, "c_vtar", 0.001, 0)
    assert np.array_equal(ns_a, ns_b, equal_nan=True), "null determinism"
    ns_c = null_sharpes(R, reb, "c_vtar", 0.001, 1)
    assert not np.array_equal(ns_a[:5], ns_c[:5]), "cell_idx changes stream"
    ns_d = null_sharpes(R, reb, "c_volinv", 0.001, 0)
    assert not np.array_equal(ns_a[:5], ns_d[:5]), "cond shape changes draws"
    ok += 1
    # (5) grid shape
    assert len(CELLS12) == 12 and len(UNIVERSES) == 2 and len(CONDITIONERS) == 3
    ok += 1
    # (6) SEED live-read
    assert sg.SEED_REGISTRY["t101_v4_a12_predcond_scrnull"] == 20316000
    assert sg.SEED_REGISTRY["t101_v4_a12_predcond_unc"] == 20316500
    ok += 1
    # (7) trade-event counter: exposure 0 -> 1 day1 = |dw| 1.0 >= 0.10
    w2 = pd.DataFrame({"a": [0.0, 0.5, 0.5, 0.5], "b": [0.0, 0.5, 0.5, 0.5]},
                      index=pd.date_range("2024-02-01", periods=4, freq="D"))
    n_ev = count_trade_events(w2)
    assert n_ev == 1, "trade-event hand-calc mismatch: %d" % n_ev
    ok += 1
    # (8) cost mirror: first-day entry |dw| cost hand-calc (manual w_eff)
    idx3 = pd.date_range("2024-03-01", periods=3, freq="D")
    R3 = pd.DataFrame({"a": [0.01, 0.02, -0.01], "b": [0.005, -0.01, 0.02]},
                      index=idx3)
    w_eff2 = pd.DataFrame({"a": [0.0, 0.25, 0.25], "b": [0.0, 0.25, 0.25]},
                          index=idx3)
    r = xsection_returns(R3, w_eff2, 0.001)
    exp_day1 = 0.25 * 0.02 + 0.25 * (-0.01) - 0.5 * 0.001
    assert abs(float(r.iloc[1]) - exp_day1) < 1e-12, "cost mirror day1"
    ok += 1
    # (9) wiring: fv.UNC_BASE rebound
    assert fv.UNC_BASE == UNC_BASE, "fv.UNC_BASE must be rebound to 20316500"
    ok += 1
    print("selftest: %d/9 PASS" % ok)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        raise SystemExit(selftest())
    if cmd == "run":
        raise SystemExit(run())
    print("usage: t101_v4_a12_predcond.py [run|selftest]")
    raise SystemExit(1)
