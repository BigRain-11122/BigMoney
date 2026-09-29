# -*- coding: utf-8 -*-
"""_r247bmc_icu_w5_probe.py -- INNOVATION-QUOTA-SLOT-5 pre-freeze probe:
zoo #86 icu_ma_timing (param-frozen bm-b r222 digest
DIGEST-20260926-r222-icu-ma-paramfreeze.md, clean-room, zero code copy)
ICU robust-regression MA raw-face facts on the 510300 anchor. NOT results,
NOT a strategy claim. Read-only, deterministic, zero network.

SLOT-5 supply slice per O-20260928-1614 sec.4(d) fill-ladder innovation
quota (>=1 new hypothesis family per idle window; pool ready=1<3 floor
breach at r246 close -- only entry is bm-b-lane W11-JUDGE, bm-c lane empty)
-- bm-c r247 berth round.

Family selection anti-dup face (r247 live-read):
  * rg ICU/siegel/repeated-median over results/ + research/ = only the
    r222 digest + zoo row + one QRS peripheral mention; results/ hits are
    instrument-code false positives (996.ICU709) -- zero prior judgment =
    untried zoo family, lawful open.
  * Param-frozen truth-source available (r222 deep-read complete) =
    fastest legitimate berth; #86 is the LAST param-frozen untried
    single-index timing row (remaining frozen rows are rotation/stock
    domain or data-face-gated).
  * Robust-regression trend endpoint = new estimator face for the quota
    line: burned axes are price/return-derived single readings (VOL ret
    std, AMP range, MOM ret speed, STD dispersion, TSTATE position,
    STREAK runs, GATE thresholds, YANG candle); #96 = volume-native HMA
    ratio (SLOT-4 judged-negative closed); #86 = Siegel RM endpoint
    trend estimate -- estimator novelty, overlap vs MOM/trend axes is the
    honest D6 risk face, quantified below (probe decides, prereg argues).

Construction (r222 digest sec.1 frozen, our-side clean-room):
  ICU(N) = rolling(N) Siegel(1982) Repeated-Median robust regression
  endpoint value intercept + slope*(N-1); scipy.stats.siegelslopes,
  method='hierarchical' (digest truth-source verbatim; scipy 1.16.1 in
  env; manual-numpy RM cross-check on a sample recorded for fidelity).
  Signal face (probe): state = long when close > ICU(N), flat when
  close < ICU(N), maintain on tie (zoo/digest "shangchuan buy / xiachuan
  flat / entangled maintain"). N three-set per digest sec.1 divergence
  disclosure: research-note 5 / skopt Bayesian 120 / differentiable-obj 15
  -- all three enter as judged cells with snooping discount disclosed in
  prereg (channel-selection face, not a tuned-on-results face).

Causal convention (probe face only): state(t) readable at close t;
descriptive forward windows are descriptive, the runner shifts for T+1
(frozen in prereg sec.3). House T+1/conservative-open law supersedes the
digest's same-day-coc narrative (research-report divergence disclosed).

Anchor cutoff = 2026-09-22 (P-5C frozen binding, W4-W12 probe anchor,
cross-family D6 faces align by date).
"""
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import numpy as np
import pandas as pd
from scipy.stats import siegelslopes
import scipy

sys.path.insert(0, os.path.join("results"))
import _r237bmc_stdq90_w11_probe as r237p  # frozen W11 probe faces

CUTOFF = "2026-09-22"
OUT = "results/_r247bmc_icu_w5_probe_facts.json"
PANEL = "data/daily/sh510300.csv"
EXTREME_DAYS = ["2015-07-27", "2016-01-04", "2024-02-28", "2024-09-24",
                "2024-09-30", "2025-04-07", "2026-01-19"]
NS = [5, 120, 15]


def icu_series(close, n):
    """ICU(N): rolling repeated-median regression endpoint value."""
    vals = np.full(len(close), np.nan)
    c = close.values.astype(float)
    for i in range(n - 1, len(c)):
        y = c[i - n + 1:i + 1]
        sl, ic = siegelslopes(y, np.arange(n, dtype=float),
                              method="hierarchical")
        vals[i] = ic + sl * (n - 1)
    return pd.Series(vals, index=close.index)


def manual_rm_endpoint(y):
    """Manual numpy RM (hierarchical) for scipy cross-check."""
    n = len(y)
    xi = np.arange(n, dtype=float)
    dy = y[:, None] - y[None, :]
    dx = xi[:, None] - xi[None, :]
    np.fill_diagonal(dx, 1.0)
    mask = ~np.eye(n, dtype=bool)
    slopes = dy / dx
    row_med = np.array([np.median(slopes[i][mask[i]]) for i in range(n)])
    slope = float(np.median(row_med))
    intercept = float(np.median(y - slope * xi))
    return intercept + slope * (n - 1)


def tstats(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    if len(a) < 3 or len(b) < 3:
        return {"n_a": len(a), "n_b": len(b), "t": None}
    va, vb = a.var(ddof=1), b.var(ddof=1)
    se = np.sqrt(va / len(a) + vb / len(b))
    if se == 0:
        return {"n_a": len(a), "n_b": len(b), "t": None}
    t = (a.mean() - b.mean()) / se
    return {"n_a": len(a), "n_b": len(b), "t": round(float(t), 3),
            "mean_a": round(float(a.mean()), 6),
            "mean_b": round(float(b.mean()), 6)}


def rate(mask_in, gate, dec):
    both = int((mask_in & gate).sum())
    base = int((mask_in & dec).sum())
    return round(100.0 * both / base, 2) if base else float("nan")


def main() -> int:
    df = pd.read_csv(PANEL)
    df["date"] = df["date"].astype(str)
    df = df[df["date"] <= CUTOFF].reset_index(drop=True)
    assert len(df) == 3483, "G-PANEL rows %d != 3483" % len(df)
    assert df["date"].iloc[0] == "2012-05-28"
    assert df["date"].iloc[-1] == CUTOFF

    close, vol = df["close"], df["volume"]
    o, h, l = df["open"], df["high"], df["low"]
    ret = close.pct_change()

    di = pd.DataFrame({"open": o, "high": h, "low": l, "close": close,
                       "volume": vol}, index=df.index)
    std20, _q90s20, std20_open, dec_s20 = r237p.std_faces(di, 20)
    _amp, _medamp, amp_wide = r237p.amp_faces(di)
    st_state = r237p.streak_faces(di)
    mad_q10, rsv_low, _dec_ts, _rsv60 = r237p.tstate_faces(di)
    _roc20, _q10m, mom_open, dec_mom = r237p.mom_faces(di)
    tstate_open = (mad_q10.fillna(False) | rsv_low.fillna(False))
    streak_up = st_state == 1.0

    vol20 = ret.rolling(20, min_periods=20).std(ddof=1)
    med500 = vol20.rolling(500, min_periods=500).median()
    calm, wild = vol20 <= med500, vol20 > med500
    med20v = vol.rolling(20, min_periods=20).median()
    surge = vol > med20v

    fwd5 = close.pct_change(5).shift(-5)
    fwd20 = close.pct_change(20).shift(-20)

    facts = {"probe": "INNOVATION-QUOTA-SLOT-5 icu_ma_timing pre-freeze "
                      "facts (zoo #86, r222 frozen params)",
             "anchor": PANEL, "cutoff": CUTOFF,
             "scipy_version": scipy.__version__,
             "panel": {"rows": int(len(df)), "first": df["date"].iloc[0],
                       "last": df["date"].iloc[-1]},
             "construction": {"estimator": "scipy.stats.siegelslopes "
                              "method=hierarchical (r222 digest truth-source "
                              "verbatim); endpoint = intercept + slope*(N-1)",
                              "signal": "long close>ICU(N); flat close<ICU(N); "
                              "maintain on tie; probe face = strict side",
                              "n_three_set": {"5": "research-note channel",
                                              "120": "skopt Bayesian channel",
                                              "15": "differentiable-obj channel"},
                              "house_divergence": "runner T+1 conservative "
                              "onset supersedes digest same-day-coc narrative"},
             "cells": {}}

    for n in NS:
        icu = icu_series(close, n)
        dec = icu.notna()
        first_dec = int(np.argmax(dec.values))
        above = close > icu
        below = close < icu
        tie = close == icu
        long_open = above

        d = {"decidable": int(dec.sum()), "first_decidable_bar_idx": first_dec,
             "long_open": int(long_open.sum()),
             "flat_open": int(below.sum()),
             "tie_maintain_days": int((tie & dec).sum()),
             "open_rate": round(float(long_open.sum() / dec.sum()), 6)}

        d["fwd5_long_open_vs_decidable"] = tstats(fwd5[long_open & dec],
                                                  fwd5[dec])
        d["fwd20_long_open_vs_decidable"] = tstats(fwd20[long_open & dec],
                                                    fwd20[dec])
        d["fwd5_long_vs_calm"] = tstats(fwd5[long_open & calm.fillna(False)],
                                        fwd5[calm.fillna(False)])
        d["fwd5_long_vs_wild"] = tstats(fwd5[long_open & wild.fillna(False)],
                                        fwd5[wild.fillna(False)])

        ext = {}
        for day in EXTREME_DAYS:
            idx = df.index[df["date"] == day]
            if len(idx) == 0:
                ext[day] = "absent"
                continue
            i = int(idx[0])
            v_i = float(icu.iloc[i]) if dec.iloc[i] else None
            st = ("long_above" if above.iloc[i] else
                  "flat_below" if below.iloc[i] else
                  "tie" if tie.iloc[i] else "warmup")
            ext[day] = {"state": st, "icu": None if v_i is None
                        else round(v_i, 4),
                        "close": round(float(close.iloc[i]), 4)}
        d["extreme_days"] = ext
        d["extreme_open_count"] = int(sum(
            1 for v in ext.values()
            if isinstance(v, dict) and v["state"] == "long_above"))

        def cell(a_mask, a_dec, b_mask, b_dec):
            both = a_dec & b_dec
            return {"both": int((a_mask & b_mask & both).sum()),
                    "a_only": int((a_mask & ~b_mask & both).sum()),
                    "b_only": int((~a_mask & b_mask & both).sum()),
                    "neither": int((~a_mask & ~b_mask & both).sum()),
                    "a_in_b": round(float((a_mask & b_mask).sum()) /
                                    float(a_mask.sum()), 4) if a_mask.sum() else None}

        lo_dec = long_open & dec
        d["d6"] = {
            "vs_w10_mom_open": cell(lo_dec, dec, mom_open.fillna(False),
                                    dec & dec_mom),
            "vs_w11_std20_open": cell(lo_dec, dec, std20_open.fillna(False),
                                      dec & dec_s20),
            "vs_w9_amp_wide": cell(lo_dec, dec, (amp_wide == 1).fillna(False),
                                   dec),
            "vs_w7_streak_up": cell(lo_dec, dec, streak_up.fillna(False), dec),
            "vs_w8_tstate_open": cell(lo_dec, dec, tstate_open, dec),
            "vs_w4_calm": cell(lo_dec, dec, calm.fillna(False),
                               dec & med500.notna()),
            "vs_w4_wild": cell(lo_dec, dec, wild.fillna(False),
                               dec & med500.notna()),
            "vs_vconf_surge": cell(lo_dec, dec, surge.fillna(False),
                                   dec & med20v.notna()),
        }
        d["regime_rates"] = {
            "pct_long_when_calm": rate(calm.fillna(False), lo_dec,
                                        dec & med500.notna()),
            "pct_long_when_wild": rate(wild.fillna(False), lo_dec,
                                       dec & med500.notna()),
            "pct_long_when_surge": rate(surge.fillna(False), lo_dec,
                                        dec & med20v.notna()),
        }
        facts["cells"]["N%d" % n] = d

    # intra-family pairwise overlaps (axis-variant disclosure)
    intra = {}
    icus = {n: icu_series(close, n) for n in NS}
    for a in NS:
        for b in NS:
            if a >= b:
                continue
            ia, ib = icus[a], icus[b]
            la = (close > ia) & ia.notna()
            lb = (close > ib) & ib.notna()
            both = ia.notna() & ib.notna()
            intra["N%d_vs_N%d" % (a, b)] = {
                "both_dec": int(both.sum()),
                "both_long": int((la & lb & both).sum()),
                "a_in_b": round(float((la & lb).sum()) / float(la.sum()), 4)
                if la.sum() else None,
                "b_in_a": round(float((la & lb).sum()) / float(lb.sum()), 4)
                if lb.sum() else None}
    facts["intra_family"] = intra

    # scipy-vs-manual RM cross-check (fidelity face, first 50 decidable
    # windows of N=15)
    ic15 = icus[15]
    idxs = np.where(ic15.notna().values)[0][:50]
    agree = 0
    maxdiff = 0.0
    for i in idxs:
        y = close.values.astype(float)[i - 14:i + 1]
        diff = abs(manual_rm_endpoint(y) - float(ic15.iloc[i]))
        maxdiff = max(maxdiff, diff)
        if diff <= 1e-9 * max(1.0, abs(float(ic15.iloc[i]))):
            agree += 1
    facts["rm_cross_check"] = {"n_windows": int(len(idxs)),
                               "agree_tol_1e-9rel": int(agree),
                               "max_abs_diff": round(float(maxdiff), 12)}

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=1)
    print("facts ->", OUT)
    for n, d in facts["cells"].items():
        print("%s: decidable=%d first_decidable=%d long_open=%d "
              "open_rate=%s tie=%d extreme_long=%d fwd5_t=%s fwd20_t=%s" % (
                  n, d["decidable"], d["first_decidable_bar_idx"],
                  d["long_open"], d["open_rate"], d["tie_maintain_days"],
                  d["extreme_open_count"],
                  d["fwd5_long_open_vs_decidable"].get("t"),
                  d["fwd20_long_open_vs_decidable"].get("t")))
    print("intra:", {k: v["a_in_b"] for k, v in intra.items()})
    mom_face = facts["cells"]["N15"]["d6"]["vs_w10_mom_open"]
    print("D6 N15 vs mom_open a_in_b:", mom_face["a_in_b"],
          "mom_in_long b_only:", mom_face["b_only"])
    print("rm_cross_check:", facts["rm_cross_check"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
