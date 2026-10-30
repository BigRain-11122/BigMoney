#!/usr/bin/env python3
"""E248 -- is E246's alternating star lead an oscillation, a decay, or inside a shuffled band?

E246 read the star column as +0.769 / -0.527 / +0.397 at lags 0/1/2 and published the verdict
as a sign flip. Two things were missing from that reading:

  (a) it stopped at lag 2, so a two-session oscillation and a decaying coefficient with noise
      around zero look the same at two points;
  (b) each coefficient was quoted against its own HAC interval, never against an empirical
      null -- on a persistent series, an HAC interval is a model, and the model is what the
      question is about.

This face extends the distributed-lag row to lags 1..5, adds a 200-draw permutation band per
lag (the star's turnover series shuffled in time, same design, same members), and decides with
that band:

  period2_oscillation    lag2 opposes lag1 at >= half its magnitude AND lag3 falls back toward
                         zero AND both lag1/lag2 sit outside the shuffled band
  monotone_decay         lags 1..5 share a sign and shrink every step, lag1 outside the band
  inside_permutation_band  no lag crosses the band -- one column read against a model is not a
                         coefficient
  band_without_shape     something crosses the band but neither shape is met

The row is re-run with the dependent variable as a two-session SUM of increments: if the
alternation is an artifact of overlapping windows (a +b/-c pair on one-session moves cancels
when two sessions are added), the summed row will not reproduce it, and the face says so.

NO BILL, NO ADOPTION, NO RE-PRICING. This face names shape; it prices nothing.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from datetime import datetime

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e222_tom_overlay as e222  # noqa: E402
import e225_state_tilt as e225  # noqa: E402
import e235_charge_granularity as e235  # noqa: E402
import e239_own_vs_cross as e239  # noqa: E402
import e240_aggregate_attenuation as e240  # noqa: E402
import e243_additivity_out_of_sample as e243  # noqa: E402
import e245_pair_slope_matrix as e245  # noqa: E402
import e246_star_direction as e246  # noqa: E402

ROOT = e222.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
BASKET = e225.BASKET
NW_LAG = e225.NW_LAG
Z95 = 1.96
MIN_SESSIONS = e240.MIN_SESSIONS
STUDY = "E248"

# frozen before the face was read
LAGS = (1, 2, 3, 4, 5)                 # the lags the row is extended to (lag 0 is contemporaneous)
PERM_DRAWS = 200                       # shuffled-star draws per cell, per leg
# full range of the draws, not a 2.5/97.5 percentile: five lags are screened at once, and a
# 95% per-lag band crosses on a pure-noise panel roughly one screen in four (measured: lag 5
# crossed with no signal in the fixture). The observed extreme of 200 draws is a pointwise
# p ~ 1/201 line, and five of them are a ~2.5% family-wise screen.
BAND_PCT = (0.0, 100.0)
BAND_MODE = "full_draw_range_200"
OSC_RATIO_MIN = 0.5                    # |lag2| >= half of |lag1|
OSC_FALL_MAX = 0.5                     # |lag3| <= half of |lag2| -- "falls back toward zero"
DECAY_MIN_LAGS = 4                     # a decay must shrink on at least this many steps
DECAY_SHRINK_MAX = 0.95                # each step strictly smaller (|b_k+1| <= this * |b_k|)
COUNTED_KINDS = ("headline", "window", "era", "neighbour")

VERDICTS = ("period2_oscillation",
            "monotone_decay",
            "inside_permutation_band",
            "band_without_shape",
            "unresolved_too_few_rows")

CELLS = e245.CELLS


# ---------------------------------------------------------------- fits
def _ols(y, cols, lag=NW_LAG):
    """Newey-West OLS in numpy, same estimator and same return shape as e235._ols_hac_full.

    The pure-python helper costs seconds per fit at 13k rows and this face needs thousands of
    them (200 shuffled draws x 5 members x 2 rows x 6 cells). A selftest leg pins beta and the
    covariance diagonal against e235's implementation, so the fast path is the same estimator
    rather than a re-estimation.
    """
    n = len(y)
    k = len(cols) + 1
    if n <= k + 2:
        return None
    X = np.empty((n, k), dtype=float)
    X[:, 0] = 1.0
    for j, c in enumerate(cols):
        X[:, j + 1] = c
    diag = np.einsum("ij,ij->j", X, X)
    if (diag <= 0.0).any():
        return None
    sd = np.sqrt(diag)
    corr = (X.T @ X) / np.outer(sd, sd)
    if abs(np.linalg.det(corr)) < 1e-10:
        return None
    xtx = X.T @ X
    try:
        inv = np.linalg.inv(xtx)
    except np.linalg.LinAlgError:
        return None
    beta = inv @ (X.T @ np.asarray(y, dtype=float))
    resid = np.asarray(y, dtype=float) - X @ beta
    meat = np.zeros((k, k), dtype=float)
    for l in range(0, lag + 1):
        w = 1.0 - float(l) / (lag + 1.0)
        if l == 0:
            meat += (X * (resid ** 2)[:, None]).T @ X
        else:
            coef = w * resid[l:] * resid[:-l]
            meat += (X[l:] * coef[:, None]).T @ X[:-l]
    cov = inv @ meat @ inv
    yt = np.asarray(y, dtype=float)
    ss_tot = float(((yt - yt.mean()) ** 2).sum()) if n else 0.0
    ss_res = float((resid ** 2).sum())
    return {"beta": [float(b) for b in beta], "cov": [[float(v) for v in row] for row in cov],
            "n": n, "r2": (1.0 - ss_res / ss_tot) if ss_tot > 0 else None}


def fit_lag_row(panel, syms, star, lag_max=5, two_session_sum=False, stride=1):
    """Each non-star member's move on its own turnover and the star's turnover at lags 0..lag_max.

    One regression per member, so every lag coefficient is a PARTIAL effect against the others
    (a lone lag regressor on a persistent sleeve re-reads the contemporaneous column, measured
    0.51 on a zero-lead fixture in E246). `two_session_sum` swaps the dependent variable for a
    two-session sum of the same increments; `stride=2` keeps those windows DISJOINT, which is
    the version that cannot manufacture structure by overlapping observations.
    """
    others = [s for s in syms if s != star]
    n = len(panel["dy"][star])
    first = lag_max + (1 if two_session_sum else 0)
    ts = list(range(first, n, stride if two_session_sum else 1))
    rows = len(ts)
    if rows <= 2 * (lag_max + 1) + 8:
        return {"rows": 0, "decided": False,
                "reason": "too few rows once %d lags are consumed" % lag_max}
    out = []
    for m in others:
        dy = panel["dy"][m]
        y = [(dy[t] + dy[t - 1]) if two_session_sum else dy[t] for t in ts]
        cols = [[panel["dx"][m][t] for t in ts]]
        for k in range(0, lag_max + 1):
            cols.append([panel["dx"][star][t - k] for t in ts])
        fit = _ols(y, cols)
        if fit is None:
            out.append({"one_of": m, "decided": False, "reason": "HAC fit refused"})
            continue
        beta = fit["beta"]
        sl = [beta[2 + k] for k in range(lag_max + 1)]
        out.append({"one_of": m, "decided": True, "rows_used": fit["n"], "r2": fit["r2"],
                    "b_own": beta[1], "lags": sl})
    return {"rows": rows, "decided": any(r.get("decided") for r in out), "members": out}


def _mean_lags(rows, lag_max=5):
    """The published column: mean over fitted members of each lag's coefficient."""
    ok = [r for r in rows if r.get("decided")]
    if not ok:
        return None
    return [sum(r["lags"][k] for r in ok) / float(len(ok)) for k in range(lag_max + 1)]


def fit_row_zero(panel, syms, m):
    """E246's lag-0 row (own turnover + every counterparty, one HAC per row) on the fast path.

    Same columns, same order, same HAC as e246.fit_row_lag(..., 0); a selftest leg pins the two
    against each other so the star is named by the published rule and not by a lookalike.
    """
    others = [s for s in syms if s != m]
    n = len(panel["dy"][m])
    if n <= 2 * len(others) + 6:
        return {"own_of": m, "decided": False, "reason": "too few rows", "lag": 0}
    y = panel["dy"][m]
    cols = [panel["dx"][m]] + [panel["dx"][j] for j in others]
    fit = _ols(y, cols)
    if fit is None:
        return {"own_of": m, "decided": False, "reason": "HAC fit refused", "lag": 0}
    beta, cov = fit["beta"], fit["cov"]

    def ci(idx):
        var = cov[idx][idx]
        se = math.sqrt(var) if var is not None and var > 0 else None
        return (None if se is None else [beta[idx] - Z95 * se, beta[idx] + Z95 * se],
                (beta[idx] / se) if se else None)

    own_ci, own_t = ci(1)
    cross = []
    for pos, j in enumerate(others):
        c, t = ci(2 + pos)
        cross.append({"one_of": j, "slope": beta[2 + pos], "ci": c, "t_nw": t,
                      "decisive": bool(c and not (c[0] <= 0.0 <= c[1]))})
    return {"own_of": m, "lag": 0, "decided": True, "rows_used": fit["n"], "r2": fit["r2"],
            "b_own": beta[1], "b_own_ci": own_ci, "b_own_t_nw": own_t, "cross": cross,
            "lagged": None}


def own_lag_persistence(panel, syms):
    """Is a member's own turnover move predictable from its own previous move? (disclosure only)"""
    out = {}
    for s in syms:
        x = panel["dx"][s]
        if len(x) < 10:
            out[s] = {"decided": False, "reason": "too few rows"}
            continue
        fit = _ols(x[1:], [x[:-1]])
        if fit is None:
            out[s] = {"decided": False, "reason": "fit refused"}
            continue
        se = math.sqrt(fit["cov"][1][1]) if fit["cov"][1][1] > 0 else None
        out[s] = {"decided": True, "ar1": fit["beta"][1],
                  "t_nw": (fit["beta"][1] / se) if se else None, "rows_used": fit["n"]}
    return out


def permutation_band(panel, syms, star, draws=PERM_DRAWS, lag_max=5, seed=20261030,
                     two_session_sum=False, stride=1):
    """Shuffle the star's turnover series in time, refit the same design, keep the column.

    The null is the design, not a distribution: whatever serial structure the star carries is
    destroyed while the own column and the row count stay identical, so a coefficient inside
    this band is a coefficient a shuffled series would also have produced.
    """
    rng = random.Random(seed)
    src = list(panel["dx"][star])
    n = len(src)
    fake = {"dy": panel["dy"], "dx": dict(panel["dx"])}
    per_lag = [[] for _ in range(lag_max + 1)]
    kept = 0
    for _ in range(draws):
        sh = src[:]
        rng.shuffle(sh)
        fake["dx"][star] = sh
        res = fit_lag_row(fake, syms, star, lag_max=lag_max,
                          two_session_sum=two_session_sum, stride=stride)
        col = _mean_lags(res["members"], lag_max)
        if col is None:
            continue
        kept += 1
        for k, v in enumerate(col):
            per_lag[k].append(v)
    bands = []
    for k in range(lag_max + 1):
        xs = sorted(per_lag[k])
        if len(xs) < 20:
            bands.append(None)
            continue
        lo = xs[int(math.floor(BAND_PCT[0] / 100.0 * (len(xs) - 1)))]
        hi = xs[int(math.ceil(BAND_PCT[1] / 100.0 * (len(xs) - 1)))]
        med = xs[len(xs) // 2]
        bands.append({"lo": lo, "hi": hi, "median": med, "draws": len(xs),
                      "width": hi - lo})
    # FAMILY-WISE line: five lags are screened at once, so the decision is taken against the
    # largest |coefficient| a SHUFFLED series produced anywhere in lags 1..5 on the same design.
    # A lag must beat every one of the draws' best lags, which is a ~1/201 family-wise line and
    # cannot be inflated by screening five columns (measured: a pure-noise panel crossed a
    # per-lag 95% band at lag 5 in one fixture screen out of four).
    fam = None
    if kept >= 20:
        maxima = []
        for i in range(kept):
            maxima.append(max(abs(per_lag[k][i]) for k in LAGS if i < len(per_lag[k])))
        maxima.sort()
        fam = {"max_abs": maxima[-1], "median_max_abs": maxima[len(maxima) // 2],
               "draws": len(maxima)}
    return {"draws_requested": draws, "draws_used": kept, "bands": bands, "family": fam,
            "n_sessions": n, "seed": seed}


def _outside(b, band, family=None):
    if b is None:
        return None
    if family and family.get("max_abs") is not None:
        return bool(abs(b) > family["max_abs"])
    if not band:
        return None
    return bool(b < band["lo"] or b > band["hi"])


def derive_verdict(col, bands, family=None):
    """The whole classification, recomputable from the published column and band alone.

    Frozen before the face was read; the smoke leg re-runs this against the face's own numbers
    so a cell cannot carry a shape its numbers do not produce.
    """
    if not col or not bands or any(b is None for b in bands[1:6]):
        return "unresolved_too_few_rows", []
    b = {k: col[k] for k in LAGS}
    out = {k: _outside(b[k], bands[k], family) for k in LAGS}
    crossing = [k for k in LAGS if out[k]]
    if not crossing:
        return "inside_permutation_band", []
    # period-2 oscillation: lag2 opposes lag1 at >= half its size, lag3 back toward zero,
    # and the opposing pair is not band noise
    if (b[1] * b[2] < 0.0
            and abs(b[2]) >= OSC_RATIO_MIN * abs(b[1])
            and abs(b[3]) <= OSC_FALL_MAX * abs(b[2])
            and out[1] and out[2]):
        return "period2_oscillation", crossing
    # monotone decay: one sign, shrinking every step
    signs = {1 if b[k] > 0 else -1 for k in LAGS}
    steps = [abs(b[k + 1]) <= DECAY_SHRINK_MAX * abs(b[k]) for k in LAGS[:-1]]
    if len(signs) == 1 and all(steps) and sum(steps) >= DECAY_MIN_LAGS - 1 and out[1]:
        return "monotone_decay", crossing
    return "band_without_shape", crossing


def _cell(per, syms, lo=None, hi=None, label="", kind="window", note=None,
          star_override=None, draws=PERM_DRAWS):
    syms = [s for s in syms if per.get(s) and len(per[s]) > 2]
    out = {"label": label, "kind": kind, "members": list(syms),
           "window_inclusive": [lo, hi], "note": note}
    if len(syms) < 3:
        out.update({"decided": False,
                    "reason": "fewer than three members have a panel in this window"})
        return out
    win = e243.subset_per(per, syms, lo, hi)
    _, panel = e240.common_increments(win, syms)
    dates = panel.get("dates") or []
    out["sessions"] = len(dates)
    out["first"] = dates[0] if dates else None
    out["last"] = dates[-1] if dates else None
    if len(dates) < MIN_SESSIONS:
        out.update({"decided": False,
                    "reason": "common grid has %d sessions (floor %d)"
                              % (len(dates), MIN_SESSIONS)})
        return out

    # the star is named by E245/E246's own rule at lag 0 -- the same object E246 published
    rows0 = [fit_row_zero(panel, syms, m) for m in syms]
    decided0 = [r for r in rows0 if r.get("decided")]
    if len(decided0) < 3:
        out.update({"decided": False,
                    "reason": "only %d of %d rows could be fitted at lag 0"
                              % (len(decided0), len(syms))})
        return out
    columns0 = [e246._column(decided0, j) for j in syms]
    mags = sorted(c["mean_abs_slope"] for c in columns0 if c["mean_abs_slope"] is not None)
    median_mag = mags[len(mags) // 2] if mags else 0.0
    stars = [c for c in columns0
             if c.get("decisive_share") is not None
             and c["decisive_share"] >= e245.STAR_DECISIVE_SHARE
             and c["mean_abs_slope"] is not None
             and c["mean_abs_slope"] >= e245.STAR_MIN_ABS_SLOPE
             and (median_mag <= 0.0 or c["mean_abs_slope"] >= e245.STAR_RATIO_MIN * median_mag)]
    stars.sort(key=lambda c: (-c["decisive_share"], -c["mean_abs_slope"]))
    star = stars[0]["one_of"] if stars else None
    star_source = "e245_star_rule" if star else "no_star_at_lag0"
    if star is None:
        best = max((c for c in columns0 if c.get("mean_abs_slope") is not None),
                   key=lambda c: c["mean_abs_slope"], default=None)
        star = best["one_of"] if best else None
        star_source = "max_mean_abs_slope_disclosure_only"
    if star_override:
        star = star_override if star_override in syms else star
        star_source = "caller_override"
    if star is None:
        out.update({"decided": False, "reason": "no member could be named a star"})
        return out

    row = fit_lag_row(panel, syms, star)
    if not row.get("decided"):
        out.update({"decided": False, "star": star, "star_source": star_source,
                    "reason": "distributed-lag row refused (%s)" % row.get("reason")})
        return out
    col = _mean_lags(row["members"])
    band = permutation_band(panel, syms, star, draws=draws)
    verdict, crossing = derive_verdict(col, band["bands"], band.get("family"))

    # does the alternation survive a two-session sum of the same increments? read twice: the
    # overlapping windows (stride 1) and the DISJOINT windows (stride 2) that cannot manufacture
    # structure by counting each session twice
    row2 = fit_lag_row(panel, syms, star, two_session_sum=True)
    col2 = _mean_lags(row2["members"]) if row2.get("decided") else None
    row3 = fit_lag_row(panel, syms, star, two_session_sum=True, stride=2)
    col3 = _mean_lags(row3["members"]) if row3.get("decided") else None
    band3 = permutation_band(panel, syms, star, draws=draws, seed=20261031,
                             two_session_sum=True, stride=2) if col3 is not None \
        else {"bands": None}
    verdict3, crossing3 = derive_verdict(col3, band3.get("bands"),
                                         band3.get("family")) if col3 is not None \
        else (None, [])
    # an oscillation summed over two sessions shows up one step further out (lag 1 and lag 3
    # carry the opposing pair); "survives" means that shifted pair is still outside the band
    surviving = None
    if col3 is not None:
        signs = {k: (1 if col3[k] > 0 else -1) for k in crossing3}
        surviving = bool(len(crossing3) >= 2
                         and len({signs[k] for k in crossing3}) == 2)

    # post-hoc descriptive reading, published beside the frozen verdict and never in its place:
    # a lead that is entirely confined to lag 1 with every further lag inside the band is a
    # shape the frozen four-name vocabulary does not carry (it is neither an oscillation nor a
    # monotone decay), and it is worth naming without pretending it was pre-registered
    desc = None
    if crossing == [1] and all(not out.get(k) for k in (2, 3, 4, 5)):
        desc = "single_lag_lead_no_rebound"
    elif crossing:
        desc = "multi_lag_crossing"

    out.update({"decided": True, "star": star, "star_source": star_source,
                "lag_column": {"lag%d" % k: col[k] for k in range(len(col))},
                "band": band["bands"],
                "band_family": band.get("family"),
                "band_mode": BAND_MODE,
                "band_draws_used": band["draws_used"],
                "outside_band": {str(k): _outside(col[k], band["bands"][k], band.get("family"))
                                 for k in LAGS},
                "verdict": verdict, "crossing_lags": crossing,
                "descriptive_pattern": desc,
                "descriptive_pattern_note": "post-hoc reading of the crossing set, NOT a "
                                            "pre-registered verdict; the verdict above is the "
                                            "frozen four-name vocabulary",
                "two_session_sum": {"overlapping": {"lag_column": ({"lag%d" % k: col2[k]
                                                                    for k in range(len(col2))}
                                                                   if col2 else None)},
                                    "disjoint": {"lag_column": ({"lag%d" % k: col3[k]
                                                                 for k in range(len(col3))}
                                                                if col3 else None),
                                                 "band": band3.get("bands"),
                                                 "verdict": verdict3,
                                                 "crossing_lags": crossing3}},
                "oscillation_survives_two_session_sum": surviving,
                "own_lag_persistence": own_lag_persistence(panel, syms),
                "resolution_median_halfwidth": (
                    sorted(abs(c["ci"][1] - c["ci"][0]) / 2.0
                           for r in decided0 for c in r["cross"] if c["ci"]) or [None]
                )[len([c for r in decided0 for c in r["cross"] if c["ci"]]) // 2]
                if any(c["ci"] for r in decided0 for c in r["cross"]) else None})
    return out


def rollup(cells):
    counted = [c for c in cells if c.get("decided") and c.get("kind") in COUNTED_KINDS]
    by = {}
    for c in counted:
        by.setdefault(c["verdict"], []).append(c["label"])
    head = next((c for c in cells if c["label"] == "all_five"), {})
    if not counted:
        verdict = "unresolved_too_few_rows"
    elif len(by) == 1:
        verdict = counted[0]["verdict"]
    else:
        era_v = {c["verdict"] for c in counted if c["kind"] == "era"}
        verdict = "verdict_era_dependent" if len(era_v) > 1 else "verdict_mixed_across_cells"
    return {"cells_counted": len(counted), "cells_by_verdict": by, "verdict": verdict,
            "headline_verdict": head.get("verdict"),
            "headline_star": head.get("star"),
            "headline_crossing_lags": head.get("crossing_lags"),
            "headline_descriptive_pattern": head.get("descriptive_pattern"),
            "cells_descriptive": {c["label"]: c.get("descriptive_pattern")
                                  for c in counted},
            "stable_across_cells": len(by) == 1,
            "overlapping_cells_note": "the era cells overlap in time, so a verdict that repeats "
                                      "is corroboration, not replication (E244 caveat)"}


def _answer(face):
    roll = face["rollup"]
    head = next((c for c in face["cells"] if c["label"] == "all_five"), {})
    star = head.get("star") or "the star"
    v = roll["verdict"]
    col = head.get("lag_column") or {}
    cross = roll.get("headline_crossing_lags") or []
    def sig(k):
        x = col.get("lag%d" % k)
        return "n/a" if x is None else "%+.3f" % x
    if v == "period2_oscillation":
        return ("%s's lead is a PERIOD-2 OSCILLATION: lag1 %s, lag2 %s (opposing, >= half the "
                "size), lag3 %s back toward zero, with lag1/lag2 outside a %d-draw shuffled "
                "star band -- the sign flip is a shape in time, not a coefficient a sleeve "
                "carries" % (star, sig(1), sig(2), sig(3), PERM_DRAWS))
    if v == "monotone_decay":
        return ("%s's lead MONOTONE-DECAYS across lags 1..5 (%s); lag1 sits outside the "
                "shuffled band, so the lead is real but it dies rather than flips"
                % (star, ", ".join(sig(k) for k in LAGS)))
    if v == "inside_permutation_band":
        return ("nothing crosses the %d-draw shuffled-star band at lags 1..5 (%s): E246's "
                "alternating pair is a coefficient read against a MODEL, not against the "
                "design's own null" % (PERM_DRAWS, ", ".join(sig(k) for k in LAGS)))
    if v == "band_without_shape":
        return ("lags %s cross the shuffled band but neither an oscillation nor a monotone "
                "decay is met -- the crossing is real and its shape is not named"
                % (", ".join(map(str, cross)) or "none"))
    if v in ("verdict_mixed_across_cells", "verdict_era_dependent"):
        parts = ["%s=%d" % (k, len(labels)) for k, labels in sorted(
            roll["cells_by_verdict"].items())]
        return ("the cells do not read the same way (%s): %s" % (
            ", ".join(parts),
            "the eras disagree" if v == "verdict_era_dependent"
            else "the cell families disagree"))
    return ("no shape resolved in any counted cell (%d counted)" % roll["cells_counted"])


def _summary(face):
    roll = face["rollup"]
    head = next((c for c in face["cells"] if c["label"] == "all_five"), {})
    return {"verdict": roll["verdict"],
            "headline_verdict": head.get("verdict"),
            "headline_star": head.get("star"),
            "headline_star_source": head.get("star_source"),
            "lag_column": head.get("lag_column"),
            "band": head.get("band"),
            "band_family": head.get("band_family"),
            "band_mode": head.get("band_mode"),
            "outside_band": head.get("outside_band"),
            "crossing_lags": head.get("crossing_lags"),
            "two_session_sum_verdict": ((head.get("two_session_sum") or {})
                                        .get("disjoint") or {}).get("verdict"),
            "two_session_sum_crossing": ((head.get("two_session_sum") or {})
                                         .get("disjoint") or {}).get("crossing_lags"),
            "oscillation_survives_two_session_sum":
                head.get("oscillation_survives_two_session_sum"),
            "band_draws_used": head.get("band_draws_used"),
            "cells_counted": roll["cells_counted"],
            "stable_across_cells": roll["stable_across_cells"],
            "cells_by_verdict": roll["cells_by_verdict"],
            "one_line": _answer(face)}


def run(save=True, per=None, outdir=None, basket=None, panels=None, star=None,
        draws=PERM_DRAWS, cells=None):
    per = per if per is not None else e239.panels(panels)
    syms = [s for s in (basket or BASKET) if per.get(s)]
    outdir = outdir or OUTDIR
    out_cells = []
    for label, kind, lo, hi, members in (cells if cells is not None else CELLS):
        these = [s for s in (members or syms) if s in syms]
        out_cells.append(_cell(per, these, lo, hi, label=label, kind=kind,
                               star_override=star, draws=draws))
    dates = sorted({d for s in syms for d in per[s]})
    face = {"study": STUDY,
            "title": "oscillation or coefficient band: the star lead against a shuffled null",
            "generated": datetime.now().isoformat(timespec="seconds"),
            "evidence_cutoff": dates[-1] if dates else None,
            "frozen_spec": {"lags": list(LAGS),
                            "perm_draws": PERM_DRAWS,
                            "band_pct": list(BAND_PCT),
                            "band_mode": BAND_MODE,
                            "family_wise_line": "a lag must exceed the largest |coefficient| any "
                                                "shuffled draw produced anywhere in lags 1..5",
                            "osc_ratio_min": OSC_RATIO_MIN,
                            "osc_fall_max": OSC_FALL_MAX,
                            "decay_min_lags": DECAY_MIN_LAGS,
                            "decay_shrink_max": DECAY_SHRINK_MAX,
                            "min_sessions": MIN_SESSIONS,
                            "nw_lag": NW_LAG,
                            "perm_seed": 20261030,
                            "verdicts": list(VERDICTS)},
            "members": syms,
            "cells": out_cells,
            "no_bill": "shape only: no adoption, no re-pricing, and a period-2 oscillation may "
                       "not be billed to the star as a one-way flow"}
    face["rollup"] = rollup(out_cells)
    face["summary"] = _summary(face)
    if save:
        face["written"] = _write(face, outdir)
    return face


def _write(face, outdir):
    os.makedirs(outdir, exist_ok=True)
    name = "STARLAGBAND-" + str(face.get("evidence_cutoff") or "unknown") + ".json"
    for fn in (name, "starlagband_latest.json"):
        with open(os.path.join(outdir, fn), "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
    return name


# ---------------------------------------------------------------- fixtures
def _dates(n, start="2019-01-01"):
    import datetime as _dt
    y, mth, d = [int(x) for x in start.split("-")]
    cur = _dt.date(y, mth, d)
    out = []
    while len(out) < n:
        out.append(cur.isoformat())
        cur = cur + _dt.timedelta(days=1)
    return out


def synth(n=600, own=0.30, lead=None, noise=0.40, members=5, seed=7, star_ar=0.0,
          start="2019-01-01"):
    """Panels whose increments obey the design: `lead` is {(member, star, lag): slope}."""
    def norm(d):
        out = {}
        for (m, j, k), v in (d or {}).items():
            out[("S%d" % m if isinstance(m, int) else m,
                 "S%d" % j if isinstance(j, int) else j, int(k))] = v
        return out
    lead = norm(lead)
    dates = _dates(n, start)
    rng = random.Random(seed)
    syms = ["S%d" % i for i in range(members)]
    dl = {s: [rng.gauss(0.0, 1.0) for _ in dates] for s in syms}
    if star_ar:
        base = dl[syms[0]]
        for t in range(1, len(base)):
            base[t] = star_ar * base[t - 1] + math.sqrt(max(1e-9, 1.0 - star_ar ** 2)) * base[t]
    per = {}
    for m in syms:
        y, lvl = [0.0], [0.0]
        for t in range(1, len(dates)):
            v = own * dl[m][t]
            for (mm, j, k), b in lead.items():
                if mm == m and t - k >= 0:
                    v += b * dl[j][t - k]
            y.append(y[-1] + v + rng.gauss(0.0, noise))
            lvl.append(lvl[-1] + dl[m][t])
        per[m] = {dates[t]: (y[t], lvl[t]) for t in range(len(dates))}
    return per


SMALL_CELLS = (("all_five", "headline", None, None, None),)


def _run(per, star="S0", draws=40):
    return run(save=False, per=per, basket=sorted(per), star=star, draws=draws,
               cells=SMALL_CELLS)


def _head(face, label="all_five"):
    return next((c for c in face["cells"] if c["label"] == label), {})


# ---------------------------------------------------------------- selftest
def selftest():
    legs = []

    def leg(name, fn):
        try:
            ok, detail = fn()
        except Exception as exc:  # noqa: BLE001 - a leg that raises is a red leg
            ok, detail = False, "%s: %s" % (type(exc).__name__, exc)
        legs.append({"leg": name, "ok": bool(ok), "detail": detail})

    def gate_shapes():
        # the vocabulary is part of the frozen gate: an oscillating column, a decaying column,
        # and a column fully inside its band must not collapse into one label
        bands = [{"lo": -0.2, "hi": 0.2}] * 6
        osc = derive_verdict([0.0, 0.60, -0.55, 0.10, 0.02, 0.01], bands)
        dec = derive_verdict([0.0, 0.60, 0.40, 0.20, 0.08, 0.03], bands)
        inb = derive_verdict([0.0, 0.10, -0.05, 0.02, 0.01, 0.00], bands)
        ok = (osc[0] == "period2_oscillation" and dec[0] == "monotone_decay"
              and inb[0] == "inside_permutation_band")
        return ok, "%s / %s / %s" % (osc[0], dec[0], inb[0])

    def oscillation_detected():
        # activity first: the fixture must actually carry the +0.6/-0.55 alternation
        per = synth(lead={(m, 0, 1): 0.6 for m in range(1, 5)}
                    | {(m, 0, 2): -0.55 for m in range(1, 5)}
                    | {(m, 0, 3): 0.10 for m in range(1, 5)})
        head = _head(_run(per))
        col = head.get("lag_column") or {}
        ok = (abs((col.get("lag1") or 0.0) - 0.60) < 0.12
              and abs((col.get("lag2") or 0.0) + 0.55) < 0.12
              and head.get("verdict") == "period2_oscillation")
        return ok, "lag1=%s lag2=%s verdict=%s" % (_f(col.get("lag1")), _f(col.get("lag2")),
                                                   head.get("verdict"))

    def oscillation_survives_sum():
        per = synth(n=700, lead={(m, 0, 1): 0.6 for m in range(1, 5)}
                    | {(m, 0, 2): -0.55 for m in range(1, 5)}
                    | {(m, 0, 3): 0.10 for m in range(1, 5)})
        head = _head(_run(per))
        dis = ((head.get("two_session_sum") or {}).get("disjoint") or {})
        return head.get("oscillation_survives_two_session_sum") is True, \
            "disjoint crossing=%s verdict=%s" % (dis.get("crossing_lags"), dis.get("verdict"))

    def sum_does_not_fabricate_alternation():
        # control for the leg above: on a panel with no lead the DISJOINT summed row must not
        # produce an opposing pair of crossings either, or "survives" is a statement about
        # arithmetic rather than about the data
        head = _head(_run(synth(n=700)))
        return head.get("oscillation_survives_two_session_sum") is False, \
            "crossing=%s" % (((head.get("two_session_sum") or {}).get("disjoint") or {})
                             .get("crossing_lags"))

    def monotone_detected():
        per = synth(lead={(m, 0, k): 0.6 * (0.6 ** (k - 1)) for k in (1, 2, 3, 4, 5)
                          for m in range(1, 5)})
        head = _head(_run(per))
        return head.get("verdict") == "monotone_decay", \
            "verdict=%s col=%s" % (head.get("verdict"), head.get("lag_column"))

    def no_signal_inside_band():
        per = synth()
        head = _head(_run(per))
        return head.get("verdict") == "inside_permutation_band", \
            "verdict=%s crossing=%s" % (head.get("verdict"), head.get("crossing_lags"))

    def band_is_wide_not_degenerate():
        # an empty-permutation band would put every coefficient "outside" and the gate would
        # read as a discovery machine (r1261 family: prove the mechanism moved before trusting it)
        per = synth()
        head = _head(_run(per))
        bands = head.get("band") or []
        widths = [b["width"] for b in bands[1:6] if b]
        return (len(widths) == 5 and min(widths) > 0.005 and head.get("band_draws_used", 0) >= 20,
                "min width %.4f draws %s" % (min(widths) if widths else -1,
                                             head.get("band_draws_used")))

    def gate_recomputes():
        face = _run(synth(lead={(m, 0, 1): 0.6 for m in range(1, 5)}
                          | {(m, 0, 2): -0.55 for m in range(1, 5)}
                          | {(m, 0, 3): 0.10 for m in range(1, 5)}))
        bad = []
        for c in [x for x in face["cells"] if x.get("decided")]:
            v, _ = derive_verdict([(c.get("lag_column") or {}).get("lag%d" % k)
                                   for k in range(6)], c.get("band") or [],
                                  c.get("band_family"))
            if v != c.get("verdict"):
                bad.append("%s: numbers say %s, face says %s"
                           % (c["label"], v, c.get("verdict")))
        tampered = [0.0, 0.05, -0.03, 0.02, 0.01, 0.00]
        refute, _ = derive_verdict(tampered, [{"lo": -0.2, "hi": 0.2}] * 6)
        if refute != "inside_permutation_band":
            bad.append("gate accepted an oscillation its numbers do not carry (%s)" % refute)
        return not bad, "; ".join(bad) or "all cells recompute"

    def too_few_sessions():
        head = _head(_run(synth(n=60, members=4)))
        return (head.get("decided") is False and "sessions" in (head.get("reason") or "")), \
            head.get("reason")

    def deterministic():
        per = synth(n=320, lead={(1, 0, 1): 0.4}, members=4)
        a, b = _run(per), _run(per)
        return _head(a).get("lag_column") == _head(b).get("lag_column"), \
            "identical=%s" % (_head(a).get("lag_column") == _head(b).get("lag_column"))

    def member_order_invariant():
        per = synth(n=340, lead={(1, 0, 1): 0.4}, members=4)
        a = run(save=False, per=per, basket=["S0", "S1", "S2", "S3"], draws=30, cells=SMALL_CELLS)
        b = run(save=False, per=per, basket=["S3", "S2", "S1", "S0"], draws=30, cells=SMALL_CELLS)
        ca, cb = _head(a).get("lag_column") or {}, _head(b).get("lag_column") or {}
        ok = all(abs(ca[k] - cb[k]) < 1e-12 for k in ca)
        return ok, "invariant=%s" % ok

    def own_lag_disclosed():
        per = synth(members=4, star_ar=0.6)
        head = _head(_run(per))
        pers = head.get("own_lag_persistence") or {}
        ar = (pers.get("S0") or {}).get("ar1")
        others = [(pers.get("S%d" % i) or {}).get("ar1") or 0.0 for i in (1, 2, 3)]
        return (ar is not None and ar > 0.3 and max(others) < 0.2), \
            "ar S0=%s others=%s" % (ar, others)

    def fast_path_is_the_same_estimator():
        # the numpy HAC must be e235's estimator, not a lookalike: beta and the covariance
        # diagonal are compared on a fixture small enough for the pure-python path
        per = synth(n=260, lead={(1, 0, 1): 0.4}, members=4)
        _, panel = e240.common_increments(per, ["S0", "S1", "S2", "S3"])
        y = panel["dy"]["S1"]
        cols = [panel["dx"]["S1"], panel["dx"]["S0"], panel["dx"]["S2"]]
        a = _ols(y, cols)
        b = e235._ols_hac_full(y, cols, NW_LAG)
        db = max(abs(x - z) for x, z in zip(a["beta"], b["beta"]))
        dc = max(abs(a["cov"][i][i] - b["cov"][i][i]) for i in range(len(a["beta"])))
        return (db < 1e-9 and dc < 1e-9), "beta %.2e cov %.2e" % (db, dc)

    def star_row_matches_e246():
        # the star is named by E246's published lag-0 row; the fast copy must reproduce it
        per = synth(n=300, lead={(1, 0, 1): 0.4}, members=4)
        _, panel = e240.common_increments(per, ["S0", "S1", "S2", "S3"])
        syms = ["S0", "S1", "S2", "S3"]
        mine = fit_row_zero(panel, syms, "S0")
        ref = e246.fit_row_lag(panel, syms, "S0", 0)
        d = [abs(mine["b_own"] - ref["b_own"])]
        d += [abs(x["slope"] - z["slope"]) for x, z in zip(mine["cross"], ref["cross"])]
        return max(d) < 1e-9, "max diff %.2e" % max(d)

    leg("the numpy HAC is the same estimator as the shared pure-python fit", fast_path_is_the_same_estimator)
    leg("the lag-0 star row is identical to E246's published row", star_row_matches_e246)
    leg("the shape vocabulary separates oscillation, decay and inside-band", gate_shapes)
    leg("a real +0.6/-0.55 alternation is detected with the right magnitudes", oscillation_detected)
    leg("the alternation survives a two-session sum of the same increments",
        oscillation_survives_sum)
    leg("the disjoint summed row does not fabricate an alternating pair", sum_does_not_fabricate_alternation)
    leg("a decaying lead is classified as monotone, not oscillating", monotone_detected)
    leg("a panel with no lead lands inside the shuffled band", no_signal_inside_band)
    leg("the permutation band is wide, populated, and not degenerate", band_is_wide_not_degenerate)
    leg("the gate recomputes every verdict and refuses an unsupported oscillation", gate_recomputes)
    leg("too few sessions is undecided, not empty-green", too_few_sessions)
    leg("same input publishes the same lag column", deterministic)
    leg("member order does not change the lag column", member_order_invariant)
    leg("own-lag persistence is measured, not assumed", own_lag_disclosed)

    n_ok = sum(1 for l in legs if l["ok"])
    print("selftest: %d/%d" % (n_ok, len(legs)))
    for l in legs:
        print(("  PASS " if l["ok"] else "  FAIL ") + l["leg"] + " :: " + str(l["detail"])[:220])
    return 0 if n_ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="E248 star lag band")
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "selftest"))
    ap.add_argument("--draws", type=int, default=PERM_DRAWS)
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    face = run(save=True, draws=args.draws)
    s = face["summary"]
    print("verdict: %s (headline %s)" % (s["verdict"], s["headline_verdict"]))
    print("star: %s [%s] draws used: %s" % (s["headline_star"], s["headline_star_source"],
                                            s["band_draws_used"]))
    print("lag column: %s" % s["lag_column"])
    print("outside band: %s crossing: %s" % (s["outside_band"], s["crossing_lags"]))
    print("two-session-sum verdict: %s" % s["two_session_sum_verdict"])
    print(s["one_line"])
    print("written: %s" % face.get("written"))
    return 0


def _f(v):
    return "n/a" if v is None else "%.3f" % v


if __name__ == "__main__":
    sys.exit(main())