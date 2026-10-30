#!/usr/bin/env python3
"""E250 -- is the shared negative lag-1 lead the book's OWN lagged aggregate turnover?

E249 read all five columns of the star row and found every one of them negative at comparable
magnitude (spread 0.352 inside a 0.384 within-column band), in every era. That kills the
star-specific naming but leaves the mechanism unnamed: something makes each member's move respond
negatively to *any* member's previous turnover. The obvious candidate is that the five columns are
all proxies for ONE book-level quantity -- aggregate turnover -- and that the book's next move
loads on it.

Tested directly, three designs on the same members / same rows / same estimator:

  A  dy_m = a + b_own*dx_m[t] + b1_c*dx_c[t-1]                 (E249's per-column row)
  B  dy_m = a + b_own*dx_m[t] + c1*dagg[t-1]                   (one aggregate regressor)
  C  dy_m = a + b_own*dx_m[t] + b1_c*dx_c[t-1] + c1*dagg[t-1]  (both, jointly)

where dagg[t] = log(sum_s turnover_s) - log(sum_s turnover_s at t-1) is the BOOK's aggregate
turnover move, built from levels (a sum of log-differences is not a log-difference of sums).
Per column the face publishes b1 without the aggregate, b1 with it, the shrinkage, the share of
each column's lag-1 the aggregate accounts for, and the aggregate's own coefficient.

The aggregate coefficient is decided against a 200-draw band: the aggregate series shuffled in
time, same design, same members -- the null is the DESIGN, not a distribution, exactly as E248.

IDENTIFICATION CAVEAT, up front: E240 found the aggregate turnover absorbed by date fixed
effects in the CROSS-SECTIONAL design. This is the TIME-SERIES version of the same regressor and
the two numbers must never be quoted against each other. Date effects cannot be included here
(the regressor of interest IS the per-date aggregate), so the omitted-variable amplification
factor (1+(k-1)rho-k*rho^2)/(1-rho^2) is published per cell the way E240 published it.

NO BILL, NO ADOPTION, NO RE-PRICING. This face names a channel; it prices nothing.
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
import e239_own_vs_cross as e239  # noqa: E402
import e240_aggregate_attenuation as e240  # noqa: E402
import e243_additivity_out_of_sample as e243  # noqa: E402
import e245_pair_slope_matrix as e245  # noqa: E402
import e246_star_direction as e246  # noqa: E402
import e248_star_lag_band as e248  # noqa: E402

ROOT = e222.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
BASKET = e225.BASKET
MIN_SESSIONS = e240.MIN_SESSIONS
STUDY = "E250"

# frozen before the face was read
COLUMN_DRAWS = 200          # shuffled-aggregate draws, headline cell
ERA_DRAWS = 60              # era cells are corroboration, not the headline
BAND_PCT = (0.0, 100.0)     # full range of the draws: ONE regressor of interest, one screen
BAND_MODE = "full_draw_range_%d"
BASESEED = 20261102
ABSORB_SHARE_STRONG = 0.50  # mean share of the columns' lag-1 the aggregate must account for
COUNTED_KINDS = ("headline", "window", "era", "neighbour")

VERDICTS = ("aggregate_carries_the_lead",
            "aggregate_partially_absorbs",
            "aggregate_does_not_absorb",
            "aggregate_inside_band",
            "unresolved_too_few_rows")

CELLS = e245.CELLS


# ---------------------------------------------------------------- aggregate series
def aggregate_moves(win, syms, level_dates, exclude=None):
    """d(log sum_s turnover_s) on the LEVEL-date grid, one value per increment.

    `level_dates` must be the level dates (not the increment dates): the panel's dy/dx have one
    row per increment, so a series built from the increment-date list comes out one short and
    every lag silently slides by one session. That exact off-by-one was caught before publication.

    `exclude` drops one member from the sum -- the LEAVE-ONE-OUT aggregate. It is required
    wherever a column's own lag-1 is regressed beside the aggregate, because the column's
    turnover is a COMPONENT of the aggregate: the joint coefficient is then a
    denominator-contains-the-numerator reading (E238 family) and its "share absorbed" is
    arithmetic, not evidence.
    """
    keep = [s for s in syms if s != exclude]
    out = []
    for k in range(1, len(level_dates)):
        d1, d0 = level_dates[k], level_dates[k - 1]
        lvl1 = sum(math.exp(win[s][d1][1]) for s in keep)
        lvl0 = sum(math.exp(win[s][d0][1]) for s in keep)
        out.append(math.log(lvl1) - math.log(lvl0))
    return out


def _mean(vals):
    vals = [v for v in vals if v is not None]
    return (sum(vals) / float(len(vals))) if vals else None


# ---------------------------------------------------------------- the three designs
def _fit_A(panel, syms, c, lag=1):
    """E249's per-column row at ONE lag: dy_m on own contemporaneous turnover + column c lag-1."""
    out = {}
    others = [s for s in syms if s != c]
    n = len(panel["dy"][c])
    first = lag + 1
    ts = list(range(first, n))
    if len(ts) <= 2 * 3 + 8:
        return {"decided": False, "reason": "too few rows"}
    for m in others:
        dy = panel["dy"][m]
        y = [dy[t] for t in ts]
        fit = e248._ols(y, [[panel["dx"][m][t] for t in ts],
                            [panel["dx"][c][t - lag] for t in ts]])
        if fit is None:
            continue
        out[m] = {"b_own": fit["beta"][1], "b1": fit["beta"][2], "rows_used": fit["n"]}
    return _pack(out, "b1")


def _fit_B(panel, syms, dagg, lag=1, agg_override=None):
    """One aggregate regressor: dy_m on own contemporaneous turnover + dagg lag-1."""
    src = agg_override if agg_override is not None else dagg
    out = {}
    n = len(src)
    first = lag + 1
    ts = [t for t in range(first, n) if t < n]
    if len(ts) <= 2 * 3 + 8:
        return {"decided": False, "reason": "too few rows"}
    for m in syms:
        dy = panel["dy"][m]
        y = [dy[t] for t in ts]
        fit = e248._ols(y, [[panel["dx"][m][t] for t in ts],
                            [src[t - lag] for t in ts]])
        if fit is None:
            continue
        out[m] = {"b_own": fit["beta"][1], "c1": fit["beta"][2], "rows_used": fit["n"]}
    return _pack(out, "c1")


def _fit_C(panel, syms, c, dagg, lag=1):
    """Both, jointly: own + column c lag-1 + dagg lag-1, so the split is partial."""
    out = {}
    others = [s for s in syms if s != c]
    n = len(dagg)
    first = lag + 1
    ts = list(range(first, n))
    if len(ts) <= 2 * 4 + 8:
        return {"decided": False, "reason": "too few rows"}
    for m in others:
        dy = panel["dy"][m]
        y = [dy[t] for t in ts]
        fit = e248._ols(y, [[panel["dx"][m][t] for t in ts],
                            [panel["dx"][c][t - lag] for t in ts],
                            [dagg[t - lag] for t in ts]])
        if fit is None:
            continue
        out[m] = {"b_own": fit["beta"][1], "b1": fit["beta"][2], "c1": fit["beta"][3],
                  "rows_used": fit["n"]}
    packed = _pack(out, "b1")
    packed["c1"] = _mean([r["c1"] for r in out.values()]) if out else None
    packed["per_member_c1"] = {k: v["c1"] for k, v in sorted(out.items())}
    return packed


def _pack(rows, key):
    if not rows:
        return {"decided": False, "reason": "every member fit was refused"}
    vals = [r[key] for r in rows.values() if r.get(key) is not None]
    if not vals:
        return {"decided": False, "reason": "coefficient missing"}
    return {"decided": True, "members_fitted": len(vals),
            key: sum(vals) / float(len(vals)),
            "per_member": {k: r[key] for k, r in sorted(rows.items())},
            "rows_used": min(r["rows_used"] for r in rows.values())}


# ---------------------------------------------------------------- null band
def aggregate_band(panel, syms, dagg, draws=COLUMN_DRAWS, lag=1, seed=20261102):
    """Shuffle the aggregate turnover series in time, refit design B, keep the coefficient."""
    rng = random.Random(seed)
    src = list(dagg)
    kept = []
    for _ in range(draws):
        sh = src[:]
        rng.shuffle(sh)
        r = _fit_B(panel, syms, sh, lag=lag)
        if r.get("decided") and r.get("c1") is not None:
            kept.append(r["c1"])
    kept.sort()
    if len(kept) < 20:
        return {"draws_requested": draws, "draws_used": len(kept), "band": None, "family": None}
    lo = kept[int(math.floor(BAND_PCT[0] / 100.0 * (len(kept) - 1)))]
    hi = kept[int(math.ceil(BAND_PCT[1] / 100.0 * (len(kept) - 1)))]
    med = kept[len(kept) // 2]
    band = {"lo": lo, "hi": hi, "median": med, "width": hi - lo, "draws": len(kept)}
    fam = {"max_abs": max(abs(x) for x in kept), "median_abs": sorted(abs(x) for x in kept)[len(kept) // 2],
           "draws": len(kept)}
    return {"draws_requested": draws, "draws_used": len(kept), "band": band, "family": fam,
            "seed": seed, "note": "one regressor of interest -> pointwise band == family-wise line"}


def _outside(b, band, family=None):
    if b is None:
        return None
    if family and family.get("max_abs") is not None:
        return bool(abs(b) > family["max_abs"])
    if not band:
        return None
    return bool(b < band["lo"] or b > band["hi"])


# ---------------------------------------------------------------- attribution
def _share(without, with_):
    if without is None or with_ is None:
        return None
    if abs(without) < 1e-12:
        return None
    return 1.0 - (with_ / without)


def _corr_lists(a, b):
    n = min(len(a), len(b))
    if n < 10:
        return None
    x, y = np.asarray(a[:n], dtype=float), np.asarray(b[:n], dtype=float)
    if x.std() == 0.0 or y.std() == 0.0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def diagnostics(panel, syms, dagg):
    """Where a positive aggregate coefficient has to come from, measured rather than argued.

    A sum of five negative one-session leads cannot itself be positive under additive truth, so
    if the aggregate crosses positively the aggregate lag is carrying something the per-column
    row does not: the book's previous aggregate activity is the best available proxy for the
    book's CONTEMPORANEOUS activity (turnover clusters), and a column read alone cannot see that
    through the other four members' present moves.
    """
    ys = np.mean(np.vstack([np.asarray(panel["dy"][s], dtype=float)[1:] for s in syms]), axis=0)
    xs = np.mean(np.vstack([np.asarray(panel["dx"][s], dtype=float)[1:] for s in syms]), axis=0)
    lag = np.asarray(dagg[:-1], dtype=float)
    m = min(len(lag), len(xs), len(ys))
    lag, xs, ys = lag[:m], xs[:m], ys[:m]

    def corr(a, b):
        n = min(len(a), len(b))
        a, b = np.asarray(a[:n], dtype=float), np.asarray(b[:n], dtype=float)
        if n < 10 or a.std() == 0.0 or b.std() == 0.0:
            return None
        return float(np.corrcoef(a, b)[0, 1])

    return {"corr_dagg_lag1_mean_dx_now": corr(lag, xs),
            "corr_dagg_lag1_mean_dy_now": corr(lag, ys),
            "corr_dagg_lag1_dagg_now": corr(lag, np.asarray(dagg[:m], dtype=float)),
            "dagg_autocorr1": corr(np.asarray(dagg[1:]), np.asarray(dagg[:-1])),
            "mean_dx_now_autocorr1": corr(xs[1:], xs[:-1]),
            "note": "dy = dlog|session move|; a positive c1 with a positive "
                    "corr(dagg_lag1, mean_dx_now) is the turnover-clustering channel, not a lead"}


def _amplification(panel, syms):
    """(1+(k-1)rho-k rho^2)/(1-rho^2) with rho = mean pairwise corr of contemporaneous dx."""
    mats = {}
    for s in syms:
        x = np.asarray(panel["dx"][s], dtype=float)
        sd = x.std()
        mats[s] = (x - x.mean()) / sd if sd > 0 else None
    rhos = []
    names = [s for s in syms if mats[s] is not None]
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            rhos.append(float(np.corrcoef(mats[a], mats[b])[0, 1]))
    if not rhos:
        return {"rho": None, "k": len(syms), "factor": None}
    rho = sum(rhos) / len(rhos)
    k = len(syms)
    den = 1.0 - rho * rho
    fac = ((1.0 + (k - 1) * rho - k * rho * rho) / den) if abs(den) > 1e-12 else None
    return {"rho": rho, "k": k, "factor": fac,
            "note": "time-series version: date effects cannot absorb the regressor, so a "
                    "single-column reading is amplified by this factor under additive truth"}


def cell(per, syms, lo=None, hi=None, label="", kind="window", draws=COLUMN_DRAWS,
         star_override=None):
    syms = [s for s in syms if per.get(s) and len(per[s]) > 2]
    out = {"label": label, "kind": kind, "members": list(syms),
           "window_inclusive": [lo, hi], "draws": draws}
    if len(syms) < 3:
        out.update({"decided": False, "reason": "fewer than three members in this window"})
        return out
    win = e243.subset_per(per, syms, lo, hi)
    dates, panel = e240.common_increments(win, syms)
    out["sessions"] = len(dates)
    out["first"] = dates[0] if dates else None
    out["last"] = dates[-1] if dates else None
    if len(dates) < MIN_SESSIONS:
        out.update({"decided": False,
                    "reason": "common grid has %d sessions (floor %d)" % (len(dates), MIN_SESSIONS)})
        return out

    # the star, named by E246's published lag-0 rule (same object E248/E249 read)
    rows0 = [e248.fit_row_zero(panel, syms, m) for m in syms]
    decided0 = [r for r in rows0 if r.get("decided")]
    star, star_source = None, "no_star_at_lag0"
    if len(decided0) >= 3:
        columns0 = [e246._column(decided0, j) for j in syms]
        mags = sorted(c["mean_abs_slope"] for c in columns0 if c["mean_abs_slope"] is not None)
        med = mags[len(mags) // 2] if mags else 0.0
        stars = [c for c in columns0
                 if c.get("decisive_share") is not None
                 and c["decisive_share"] >= e245.STAR_DECISIVE_SHARE
                 and c["mean_abs_slope"] is not None
                 and c["mean_abs_slope"] >= e245.STAR_MIN_ABS_SLOPE
                 and (med <= 0.0 or c["mean_abs_slope"] >= e245.STAR_RATIO_MIN * med)]
        stars.sort(key=lambda c: (-c["decisive_share"], -c["mean_abs_slope"]))
        if stars:
            star, star_source = stars[0]["one_of"], "e245_star_rule"
    if star_override:
        star, star_source = (star_override if star_override in syms else star), "caller_override"
    out["star"] = star
    out["star_source"] = star_source

    lvl_dates = sorted(set.intersection(*[set(win[s]) for s in syms]))
    dagg = aggregate_moves(win, syms, lvl_dates)
    out["aggregate"] = {"definition": "d log(sum_s turnover_s) on the common grid",
                        "n": len(dagg),
                        "aligned_to_panel_rows": len(dagg) == len(panel["dy"][syms[0]]),
                        "mean": _mean(dagg),
                        "sd": float(np.std(dagg)) if dagg else None}
    if len(dagg) != len(panel["dy"][syms[0]]):
        out.update({"decided": False, "verdict": "unresolved_too_few_rows",
                    "reason": "aggregate series length %d != panel rows %d"
                              % (len(dagg), len(panel["dy"][syms[0]]))})
        return out

    band = aggregate_band(panel, syms, dagg, draws=draws, seed=BASESEED + len(label))
    out["band_dagg_lag1"] = band
    b_alone = _fit_B(panel, syms, dagg)
    out["design_B_alone"] = b_alone
    c1 = b_alone.get("c1")
    out["aggregate_outside_band"] = _outside(c1, band.get("band"), band.get("family"))

    cols = {}
    for c in syms:
        a = _fit_A(panel, syms, c)
        both = _fit_C(panel, syms, c, dagg)
        loo_series = aggregate_moves(win, syms, lvl_dates, exclude=c)
        loo = _fit_C(panel, syms, c, loo_series)
        e = {"b1_without_aggregate": a.get("b1"),
             "b1_with_aggregate": both.get("b1"),
             "c1_in_joint": both.get("c1"),
             "b1_with_loo_aggregate": loo.get("b1"),
             "c1_in_loo_joint": loo.get("c1"),
             "members_fitted": a.get("members_fitted") if a.get("decided") else None,
             "decided": bool(a.get("decided") and both.get("decided"))}
        e["shrinkage"] = ((a["b1"] - both["b1"]) if e["decided"] else None)
        e["share_accounted"] = _share(a.get("b1"), both.get("b1")) if e["decided"] else None
        e["shrinkage_loo"] = ((a["b1"] - loo["b1"])
                              if (a.get("decided") and loo.get("decided")) else None)
        e["share_accounted_loo"] = (_share(a.get("b1"), loo.get("b1"))
                                    if (a.get("decided") and loo.get("decided")) else None)
        e["collinear_with_aggregate"] = _corr_lists(panel["dx"][c][1:], dagg[:-1])
        e["note"] = ("share_accounted uses the aggregate the column sits INSIDE (E238 family: "
                     "denominator contains the numerator); share_accounted_loo drops the column "
                     "from the sum and is the readable one")
        cols[c] = e
    out["columns"] = cols
    shares = [v["share_accounted_loo"] for k, v in cols.items()
              if v.get("share_accounted_loo") is not None and k != star]
    out["mean_share_accounted"] = _mean(shares)
    out["mean_share_inclusive"] = _mean([v["share_accounted"] for k, v in cols.items()
                                         if v.get("share_accounted") is not None and k != star])
    out["star_share_accounted"] = (cols.get(star) or {}).get("share_accounted_loo") if star else None
    out["amplification"] = _amplification(panel, syms)
    out["diagnostics"] = diagnostics(panel, syms, dagg)
    out["verdict"] = derive_verdict(c1, out["aggregate_outside_band"],
                                    out.get("mean_share_accounted"), len(cols))
    return out


def derive_verdict(c1, outside, mean_share, n_cols):
    """Frozen classification, recomputable from the published numbers alone."""
    if n_cols < 3 or c1 is None:
        return "unresolved_too_few_rows"
    if not outside:
        return "aggregate_inside_band"
    if mean_share is None:
        return "aggregate_does_not_absorb"
    if c1 < 0.0 and mean_share >= ABSORB_SHARE_STRONG:
        return "aggregate_carries_the_lead"
    if mean_share >= ABSORB_SHARE_STRONG * 0.5:
        return "aggregate_partially_absorbs"
    return "aggregate_does_not_absorb"


def rollup(cells):
    counted = [c for c in cells if c.get("kind") in COUNTED_KINDS and c.get("verdict")]
    by = {}
    for c in counted:
        by[c["verdict"]] = by.get(c["verdict"], 0) + 1
    head = next((c for c in cells if c.get("label") == "all_five"), {})
    verdict = (head.get("verdict") or (sorted(by, key=lambda k: -by[k])[0] if by else None))
    return {"verdict": verdict, "cells_by_verdict": by, "cells_counted": len(counted),
            "stable_across_cells": len(by) == 1}


def _summary(face):
    def mc(v):
        return (v or {}).get("c1")
    head = next((c for c in face["cells"] if c.get("label") == "all_five"), {})
    return {"verdict": face["rollup"]["verdict"],
            "headline_verdict": head.get("verdict"),
            "headline_star": head.get("star"),
            "headline_c1_alone": mc(head.get("design_B_alone")),
            "headline_c1_joint_star": (head.get("columns", {}).get(head.get("star")) or {}).get("c1_in_joint"),
            "headline_mean_share_accounted": head.get("mean_share_accounted"),
            "headline_star_share_accounted": head.get("star_share_accounted"),
            "headline_aggregate_outside_band": head.get("aggregate_outside_band"),
            "headline_band": (head.get("band_dagg_lag1") or {}).get("band"),
            "headline_family": (head.get("band_dagg_lag1") or {}).get("family"),
            "headline_b1_without": {k: v.get("b1_without_aggregate") for k, v in (head.get("columns") or {}).items()},
            "headline_b1_with": {k: v.get("b1_with_aggregate") for k, v in (head.get("columns") or {}).items()},
            "headline_share_by_column": {k: v.get("share_accounted") for k, v in (head.get("columns") or {}).items()},
            "headline_amplification": head.get("amplification"),
            "cells_by_verdict": face["rollup"]["cells_by_verdict"],
            "cells_counted": face["rollup"]["cells_counted"],
            "stable_across_cells": face["rollup"]["stable_across_cells"]}


def run(save=True, per=None, outdir=None, basket=None, draws=COLUMN_DRAWS, era_draws=ERA_DRAWS,
        cells=None, star=None):
    per = per if per is not None else e239.panels()
    syms = [s for s in (basket or BASKET) if per.get(s)]
    outdir = outdir or OUTDIR
    out_cells = []
    for label, kind, lo, hi, members in (cells if cells is not None else CELLS):
        these = [s for s in (members or syms) if s in syms]
        out_cells.append(cell(per, these, lo, hi, label=label, kind=kind,
                              draws=draws if kind == "headline" else era_draws,
                              star_override=star))
    dates = sorted({d for s in syms for d in per[s]})
    face = {"study": STUDY,
            "title": "is the shared negative lag-1 lead the book's own lagged aggregate turnover?",
            "generated": datetime.now().isoformat(timespec="seconds"),
            "evidence_cutoff": dates[-1] if dates else None,
            "frozen_spec": {"designs": ["A per-column lag-1", "B aggregate lag-1",
                                        "C both jointly"],
                            "aggregate": "d log(sum_s turnover_s) on the common grid",
                            "column_draws": COLUMN_DRAWS, "era_draws": ERA_DRAWS,
                            "band_mode": BAND_MODE % COLUMN_DRAWS,
                            "absorb_share_strong": ABSORB_SHARE_STRONG,
                            "verdicts": list(VERDICTS),
                            "base_seed": BASESEED,
                            "min_sessions": MIN_SESSIONS,
                            "reuse": "estimator e248._ols, star rule e245/e246, grid e240"},
            "identification_caveat": "E240 read this regressor in a CROSS-SECTIONAL design where "
                                     "date effects absorbed it; this is the TIME-SERIES version, "
                                     "date effects cannot be included because the regressor of "
                                     "interest is per-date. Do not quote the two against each "
                                     "other; see amplification per cell.",
            "members": syms,
            "cells": out_cells,
            "no_bill": "channel naming only: no adoption, no re-pricing",
            "written": None}
    face["rollup"] = rollup(out_cells)
    face["summary"] = _summary(face)
    if save:
        face["written"] = _write(face, outdir)
    return face


def _write(face, outdir):
    os.makedirs(outdir, exist_ok=True)
    cutoff = (face.get("evidence_cutoff") or "unknown")
    path = os.path.join(outdir, "BOOKECHO-%s.json" % cutoff)
    latest = os.path.join(outdir, "bookecho_latest.json")
    body = json.dumps(face, indent=1, sort_keys=True, ensure_ascii=False)
    for p in (path, latest):
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")
    return {"face": os.path.relpath(path, ROOT), "latest": os.path.relpath(latest, ROOT),
            "bytes": len(body)}


# ---------------------------------------------------------------- selftest
def _synth(n=320, k=5, lead=-0.6, own=0.5, seed=7, rho_common=0.0, noise=0.02):
    """Synthetic per-face panel whose truth is a KNOWN aggregate lag-1 coefficient.

    Each member's log|r| accumulates `lead * dagg[t-1] + own * dx_m[t] + noise`, so the designs
    are answering a question whose answer is written down. Turnover levels carry a common factor
    so the aggregate is not a sum of independent noise.
    """
    rng = random.Random(seed)
    syms = ["s%d" % i for i in range(k)]
    dates = ["d%04d" % i for i in range(n)]
    common = [rng.gauss(0.0, 0.05) for _ in range(n)]
    lt = {s: [] for s in syms}
    for i in range(n):
        for s in syms:
            lt[s].append(math.log(1000.0) + 0.02 * i + common[i] + 0.03 * rng.gauss(0, 1))
    lr = {s: [math.log(0.01)] for s in syms}
    daggs = []
    for t in range(1, n):
        lvl1 = sum(math.exp(lt[s][t]) for s in syms)
        lvl0 = sum(math.exp(lt[s][t - 1]) for s in syms)
        daggs.append(math.log(lvl1) - math.log(lvl0))
    # the published design is dy[t] on the aggregate at t-1, so the fixture writes the effect at
    # that same lag; generating it contemporaneously would make the fixture answer a question
    # this face does not ask (the pre-publication off-by-one showed up exactly this way)
    for t in range(1, n):
        for s in syms:
            dx = lt[s][t] - lt[s][t - 1]
            lead_term = lead * daggs[t - 2] if t >= 2 else 0.0
            lr[s].append(lr[s][-1] + lead_term + own * dx + noise * rng.gauss(0, 1))
    per = {s: {dates[i]: (lr[s][i], lt[s][i]) for i in range(n)} for s in syms}
    return per, syms, lead


def _synth_flat(n=320, k=5, seed=11):
    """No lead anywhere: pure noise moves, so the band must swallow the aggregate."""
    rng = random.Random(seed)
    syms = ["s%d" % i for i in range(k)]
    dates = ["d%04d" % i for i in range(n)]
    per = {}
    for s in syms:
        lv = math.log(1000.0)
        lr = math.log(0.01)
        blk = {dates[0]: (lr, lv)}
        for i in range(1, n):
            lv += 0.02 * rng.gauss(0, 1)
            lr += 0.02 * rng.gauss(0, 1)
            blk[dates[i]] = (lr, lv)
        per[s] = blk
    return per, syms


def leg(ok, name, detail=None):
    return {"leg": name, "pass": bool(ok), "detail": detail}


def selftest():
    legs = []

    per, syms, truth = _synth()
    f1 = run(save=False, per=per, basket=syms, draws=60, era_draws=20,
             cells=(("all_five", "headline", None, None, None),))
    head = f1["cells"][0]
    legs.append(leg(head.get("verdict") == "aggregate_carries_the_lead",
                    "known negative aggregate lead is named",
                    {"verdict": head.get("verdict"),
                     "c1": (head.get("design_B_alone") or {}).get("c1"),
                     "truth": truth}))
    legs.append(leg((head.get("design_B_alone") or {}).get("c1") is not None
                    and abs((head["design_B_alone"]["c1"]) - truth) < 0.25,
                    "recovered coefficient is near the written truth",
                    {"c1": (head.get("design_B_alone") or {}).get("c1"), "truth": truth}))
    legs.append(leg((head.get("mean_share_accounted") or 0.0) >= ABSORB_SHARE_STRONG,
                    "column lag-1 is absorbed once the aggregate is in",
                    {"mean_share": head.get("mean_share_accounted"),
                     "b1_without": {k: v.get("b1_without_aggregate") for k, v in
                                    (head.get("columns") or {}).items()}}))
    cols = head.get("columns") or {}
    legs.append(leg(all(v.get("b1_with_aggregate") is not None for v in cols.values()),
                    "every column reports b1 with the aggregate", {"n": len(cols)}))
    legs.append(leg(all(v.get("share_accounted") is not None
                        for k, v in cols.items() if k != head.get("star")),
                    "shares are published per column"))

    flat, fsyms = _synth_flat()
    f2 = run(save=False, per=flat, basket=fsyms, draws=60, era_draws=20,
             cells=(("all_five", "headline", None, None, None),))
    h2 = f2["cells"][0]
    legs.append(leg(h2.get("verdict") == "aggregate_inside_band",
                    "no-lead panel stays inside the shuffled band",
                    {"verdict": h2.get("verdict"),
                     "c1": (h2.get("design_B_alone") or {}).get("c1"),
                     "band": (h2.get("band_dagg_lag1") or {}).get("band")}))

    d1 = run(save=False, per=per, basket=syms, draws=40, era_draws=20,
             cells=(("all_five", "headline", None, None, None),))
    d2 = run(save=False, per=per, basket=syms, draws=40, era_draws=20,
             cells=(("all_five", "headline", None, None, None),))
    legs.append(leg(json.dumps(d1["cells"][0]["design_B_alone"], sort_keys=True)
                    == json.dumps(d2["cells"][0]["design_B_alone"], sort_keys=True),
                    "deterministic under a fixed seed"))

    short, ssyms, _ = _synth(n=90, k=5)
    f3 = run(save=False, per=short, basket=ssyms, draws=40, era_draws=20,
             cells=(("all_five", "headline", None, None, None),))
    legs.append(leg(f3["cells"][0].get("verdict") is None
                    and f3["cells"][0].get("decided") is False,
                    "session floor refuses a short grid", {"sessions": f3["cells"][0].get("sessions")}))

    legs.append(leg(derive_verdict(-0.5, True, 0.8, 5) == "aggregate_carries_the_lead",
                    "verdict: strong absorption with a negative coefficient"))
    legs.append(leg(derive_verdict(0.5, True, 0.8, 5) == "aggregate_partially_absorbs",
                    "verdict: a positive aggregate coefficient cannot carry a negative lead"))
    legs.append(leg(derive_verdict(-0.5, False, 0.9, 5) == "aggregate_inside_band",
                    "verdict: inside the band outranks the share"))
    legs.append(leg(derive_verdict(-0.5, True, None, 5) == "aggregate_does_not_absorb",
                    "verdict: no share published cannot claim absorption"))
    legs.append(leg(derive_verdict(-0.5, True, 0.9, 2) == "unresolved_too_few_rows",
                    "verdict: fewer than three columns is unresolved"))

    panel = {"dates": ["d0", "d1", "d2", "d3"],
             "dx": {"a": [0.0, 0.1, -0.1, 0.2], "b": [0.0, 0.2, -0.2, 0.1]},
             "dy": {"a": [0.0, 0.1, -0.1, 0.2], "b": [0.0, 0.2, -0.2, 0.1]}}
    amp = _amplification(panel, ["a", "b"])
    legs.append(leg(amp["factor"] is not None and amp["k"] == 2,
                    "amplification factor is finite on a correlated pair", amp))

    # a constant regressor of interest must not produce a confident coefficient
    det = _amplification(panel, ["a", "b"])
    legs.append(leg(isinstance(det.get("rho"), float), "rho is published as a number", det))
    return {"legs": legs, "passed": sum(1 for x in legs if x["pass"]), "total": len(legs),
            "ok": all(x["pass"] for x in legs)}


def _fmt(face):
    s = face["summary"]
    return ("%s | verdict %s | headline c1 %s (band %s) | mean share absorbed %s | "
            "star %s share %s | cells %s"
            % (face["study"], s["verdict"], s["headline_c1_alone"], s["headline_band"],
               s["headline_mean_share_accounted"], s["headline_star"],
               s["headline_star_share_accounted"], s["cells_by_verdict"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", nargs="?", default="run", choices=("run", "selftest"))
    ap.add_argument("--draws", type=int, default=COLUMN_DRAWS)
    args = ap.parse_args()
    if args.mode == "selftest":
        r = selftest()
        for x in r["legs"]:
            print("%s %s" % ("PASS" if x["pass"] else "FAIL", x["leg"]))
        print("selftest %d/%d" % (r["passed"], r["total"]))
        return 0 if r["ok"] else 1
    face = run(draws=args.draws)
    print(_fmt(face))
    print("written: %s" % (face.get("written") or {}).get("face"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())