# -*- coding: utf-8 -*-
"""_r255bmc_w7_nnl_d6_probe.py -- NNL-BREADTH-P1 freeze-window probe:
theta-face re-verification (prereg s9 step 4) + D6 cells corr face
(prereg s1 table, W6 _r459bma protocol mirror).

Read-only, zero engine/admission/REGIME_GUARD touch. Persists NO
performance metric of the batch cells -- the D6 face uses the return
series only for the preregistered correlation protocol (W6 probe
discipline: "persists no performance metric").

Faces:
  T  theta face     : trailing-500d q10/q90/q50 rolling quantiles of
                      B_t(W20) -- formula re-verification, zero
                      hand-copied constants; ordering invariants
                      (th_lo <= th_re <= th_hi every decidable day),
                      non-degeneracy (strict inequalities live
                      fractions), first/last + extreme-day samples.
  D  D6 cells face  : batch-internal bottom vs dual (expected high --
                      variant face, both cells still burned), vs T33
                      in-book rotation cells (merge clause at
                      |corr| >= 0.7), vs registered six traders
                      (disclose-only per prereg s1). REGIME_GUARD =
                      in-production non-cell: signal face already
                      adjudicated at berth (-0.7757 W20 / -0.6369
                      W60), no cells pair exists -- honest boundary
                      recorded, merge clause cannot trigger against
                      a non-cell.

Output: results/_r255bmc_w7_nnl_d6_probe_facts.json
Exit 0 normal / 2 mechanism fault (honest, no masking).
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "results"))  # probe family imports
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from _r254bmc_w7_nlnl_probe import load_core48, breadth_series  # single-source
from ce_transfer import COST_X1_RATE            # x1 = 13.041bp/side (G2-recorded)

OUT = os.path.join(ROOT, "results", "_r255bmc_w7_nnl_d6_probe_facts.json")
W_MAIN = 20
THETA_TRAIL = 500
D6_REJECT = 0.7
TARGET = "510300"
T33_CELLS_PATH = os.path.join(ROOT, "results", "t33_attack_wave_cells.jsonl")
T33_GATES_PATH = os.path.join(ROOT, "results", "t33_attack_wave_gates.json")
T33_ROT_CELLS = ["slope_r2_rotation_25_top3_r8", "dual_momentum_etf_20_60_top3",
                 "rs_rotation_20", "composite_top5"]
EXTREME_DAYS = ["2021-02-18", "2022-04-26", "2024-02-05",
                "2024-09-24", "2025-01-14"]


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


def variant_positions(b: pd.Series, th_lo: pd.Series, th_hi: pd.Series,
                      th_re: pd.Series, variant: str) -> pd.Series:
    """Persistent hysteresis state machine (prereg s3), pos_end face:
    decided at close of t, effective t+1 (T+1 onset causality, W3/W4/W5
    house convention). Initial state = long at the first decidable day
    (pre-decidable face = passive default; runner freeze next round pins
    the identical convention in selftest).
      bottom: B <= th_lo -> flat; B >= th_re -> long; else maintain.
      dual   : bottom + top leg: B >= th_hi -> flat until B <= th_re
               -> long; else maintain.
    """
    dec = b.notna() & th_lo.notna() & th_re.notna() \
        & (th_hi.notna() if variant == "dual" else True)
    idx = b.index
    pos = pd.Series(np.nan, index=idx, dtype=float)
    state = None
    for t in idx:
        if not bool(dec.loc[t]):
            continue
        bv, lo_, re_ = b.loc[t], th_lo.loc[t], th_re.loc[t]
        hi_ = th_hi.loc[t] if variant == "dual" else None
        if state is None:
            state = 1.0  # initial = long at first decidable day
        if variant == "bottom":
            if bv <= lo_:
                state = 0.0
            elif bv >= re_:
                state = 1.0
        else:  # dual
            if bv <= lo_:
                state = 0.0
            elif bv >= hi_:
                state = 0.0
            elif bv <= re_:
                state = 1.0
        pos.loc[t] = state
    return pos


def cell_returns(pos_end: pd.Series, tgt_ret: pd.Series) -> pd.Series:
    """W5 position_series convention, full window: pos[t] =
    pos_end[t-1]; gross = pos*ret; cost = x1 rate on |dpos| booked to
    the following day. Batch window = [first_decidable+1, end)."""
    lo_idx = pos_end.first_valid_index()
    lo = pos_end.index.get_loc(lo_idx) + 1
    idx = pos_end.index
    n = len(idx)
    pos = pd.Series(0.0, index=idx, dtype=float)
    pos.iloc[lo:] = pos_end.iloc[lo - 1: n - 1].values
    gross = pos * tgt_ret
    flips = pos.diff().abs()
    net = gross - COST_X1_RATE * flips
    return net.iloc[lo:]


def run() -> int:
    closes, syms = load_core48()
    br = breadth_series(closes, W_MAIN)
    b = br["b"]
    panel_dates = closes.index

    # ---- T theta face (prereg s9 step 4, formula re-verification)
    th_lo = b.rolling(THETA_TRAIL, min_periods=THETA_TRAIL).quantile(0.10)
    th_hi = b.rolling(THETA_TRAIL, min_periods=THETA_TRAIL).quantile(0.90)
    th_re = b.rolling(THETA_TRAIL, min_periods=THETA_TRAIL).quantile(0.50)
    dec_mask = b.notna() & th_lo.notna()
    n_dec = int(dec_mask.sum())
    if n_dec <= 0:
        print("FATAL: zero decidable days for theta face")
        return 2
    dec_idx = b.index[dec_mask]
    order_ok = bool((th_lo[dec_mask] <= th_re[dec_mask]).all()
                    and (th_re[dec_mask] <= th_hi[dec_mask]).all())
    strict_lo = float((th_lo[dec_mask] < th_re[dec_mask]).mean())
    strict_re = float((th_re[dec_mask] < th_hi[dec_mask]).mean())
    ext = {}
    for d in EXTREME_DAYS:
        ts = pd.Timestamp(d)
        if ts in b.index and dec_mask.loc[ts]:
            ext[d] = {"b": round(float(b.loc[ts]), 4),
                      "th_lo": round(float(th_lo.loc[ts]), 4),
                      "th_re": round(float(th_re.loc[ts]), 4),
                      "th_hi": round(float(th_hi.loc[ts]), 4)}
        else:
            ext[d] = "absent-or-warmup"
    theta_face = {
        "formula": "trailing-%dd rolling quantile of B_t(W%d), "
                   "min_periods=%d; zero hand-copied constants" % (
                       THETA_TRAIL, W_MAIN, THETA_TRAIL),
        "n_decidable_days": n_dec,
        "first_decidable_date": str(dec_idx[0].date()),
        "last_decidable_date": str(dec_idx[-1].date()),
        "order_invariant_lo_le_re_le_hi": order_ok,
        "strict_frac_lo_lt_re": round(strict_lo, 6),
        "strict_frac_re_lt_hi": round(strict_re, 6),
        "th_lo_range": [round(float(th_lo[dec_mask].min()), 4),
                        round(float(th_lo[dec_mask].max()), 4)],
        "th_re_range": [round(float(th_re[dec_mask].min()), 4),
                        round(float(th_re[dec_mask].max()), 4)],
        "th_hi_range": [round(float(th_hi[dec_mask].min()), 4),
                        round(float(th_hi[dec_mask].max()), 4)],
        "extreme_day_samples": ext,
    }
    if not order_ok:
        print("FATAL: theta ordering invariant violated")
        return 2

    # ---- cell return faces (D6 protocol input only)
    tgt = closes[TARGET].astype(float)
    tgt_ret = tgt.pct_change()
    pos_b = variant_positions(b, th_lo, th_hi, th_re, "bottom")
    pos_d = variant_positions(b, th_lo, th_hi, th_re, "dual")
    ret_b = cell_returns(pos_b, tgt_ret)
    ret_d = cell_returns(pos_d, tgt_ret)

    d6 = {"batch_internal_bottom_vs_dual": None,
          "vs_t33_cells": {}, "merge_clause_applied": [],
          "vs_registered_six": {"max_abs_corr": None, "argmax": None},
          "regime_guard_note":
              "in-production non-cell (T0 authority untouched): signal "
              "face adjudicated at berth pearson -0.7757 W20 / -0.6369 "
              "W60 (r254 facts); no cells pair exists, merge clause "
              "cannot trigger against a non-cell -- honest boundary per "
              "prereg s5.3"}
    d6["batch_internal_bottom_vs_dual"] = round(
        abs(_pearson(ret_b, ret_d)), 4)

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
        cb = round(abs(_pearson(ret_b, t33_rows[cid])), 4)
        cd = round(abs(_pearson(ret_d, t33_rows[cid])), 4)
        d6["vs_t33_cells"][cid] = {"bottom": cb, "dual": cd}
        if max(cb, cd) >= D6_REJECT:
            d6["merge_clause_applied"].append(cid)
    try:
        gates = json.load(open(T33_GATES_PATH, encoding="utf-8"))
        reg_rets = gates.get("registered_rets", {})
        my_idx = closes.index
        best = (0.0, None)
        for rid, rl in reg_rets.items():
            k = min(len(rl), len(my_idx) - 1)
            rs_ = pd.Series(rl[:k], index=my_idx[1:k + 1])
            cb = abs(_pearson(ret_b, rs_))
            cd = abs(_pearson(ret_d, rs_))
            c = max(cb if np.isfinite(cb) else 0.0, cd if np.isfinite(cd) else 0.0)
            if c > best[0]:
                best = (c, rid)
        d6["vs_registered_six"] = {"max_abs_corr": round(best[0], 4),
                                    "argmax": best[1]}
    except FileNotFoundError:
        d6["vs_registered_six"] = {"max_abs_corr": None, "argmax": None,
                                   "note": "t33 gates json absent"}

    state_face = {
        "initial_state_convention": "long at first decidable day "
                                    "(passive default; runner freeze pins "
                                    "identical convention in selftest)",
        "bottom_defensive_days": int((pos_b == 0.0).sum()),
        "bottom_decidable_days": int(pos_b.notna().sum()),
        "dual_defensive_days": int((pos_d == 0.0).sum()),
        "dual_decidable_days": int(pos_d.notna().sum()),
    }

    facts = {
        "probe": "NNL-BREADTH-P1 freeze-window theta + D6 cells probe",
        "machine": "bm-c", "round": "r255",
        "evidence_cutoff": str(closes.index[-1].date()),
        "panel": {"n_symbols": int(closes.shape[1]),
                  "n_dates": int(len(closes.index)),
                  "first_date": str(closes.index[0].date()),
                  "last_date": str(closes.index[-1].date()),
                  "target": TARGET, "w_main": W_MAIN,
                  "theta_trail": THETA_TRAIL},
        "theta_face": theta_face,
        "state_face": state_face,
        "d6_cells_face": d6,
        "cost_face": "ce_transfer.COST_X1_RATE imported (13.041bp/side); "
                     "D6 return series = x1 net convention, no metric "
                     "persisted",
        "merge_clause_threshold": D6_REJECT,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1)
    print("theta face: decidable", n_dec, "| order invariant", order_ok,
          "| strict lo<re", round(strict_lo, 4), "| strict re<hi",
          round(strict_re, 4))
    print("D6 batch internal |corr| =", d6["batch_internal_bottom_vs_dual"],
          "(expected high, variant face -- both cells burn)")
    print("D6 vs T33 cells:", d6["vs_t33_cells"])
    print("D6 merge clause applied:", d6["merge_clause_applied"] or "NONE")
    print("D6 vs registered six max |corr| =",
          d6["vs_registered_six"]["max_abs_corr"],
          "argmax", d6["vs_registered_six"]["argmax"])
    return 0


if __name__ == "__main__":
    sys.exit(run())
