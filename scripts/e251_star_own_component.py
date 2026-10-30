#!/usr/bin/env python3
"""E251 -- what is left of the star column once the book-wide aggregate is removed?

E250 measured that the book's own lagged aggregate turnover carries the shared negative lead:
the mean leave-one-out share absorbed is 0.91, and every non-star column loses 60-130% of its
lag-1 coefficient once the aggregate is in the row. The star (sh588000) kept 90% of -0.805
(share 0.0998) against 0.10-0.60 everywhere else. That residual is now the whole question, and
the honest answer may be that it is not turnover at all.

Tested as a DECOMPOSITION on the same members / rows / estimator as E250's design C, with the
star's leave-one-out aggregate always in the row:

  D0  dy_m = a + b_own*dx_m[t] + b1*dx_s[t-1] + c1*dagg_loo[t-1]        (E250's readable row)
  D1  D0 + b2*|dy_s[t-1]|                                              (the star's own lagged move)
  D2  D1 + b3*age_s(t)                                                 (member age, in days)

and, per column, b1 published in every model plus the share of the residual each addition takes
(1 - b1_after/b1_before). Two decisions, both against 200-draw shuffled bands (the null is the
DESIGN, not a distribution, exactly as E248/E250):

  * is the residual b1 itself outside the band its own time-shuffled column produces?
  * is the DROP caused by the added regressor outside the band of drops produced when that same
    regressor is shuffled in time? A regressor that "explains" a coefficient without clearing
    that band has explained nothing.

IDENTIFICATION, up front and published rather than assumed: inside the headline cell the member's
age is a monotone function of the row index (one constant age per member per session), so age is
NOT separable from any other slow trend and `age_identified` is published false there. The age
term is still fitted, and the age effect is read where the window makes it measurable -- as a
cross-member gradient inside each era cell (residual_c against the age of member c at that cell's
midpoint, n = len(members), published as descriptive only, never as a decision).

NO BILL, NO ADOPTION, NO RE-PRICING. This face decomposes a channel; it prices nothing.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from datetime import datetime, timedelta

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
import e248_star_lag_band as e248  # noqa: E402
import e250_book_turnover_echo as e250  # noqa: E402

ROOT = e222.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
BASKET = e225.BASKET
MIN_SESSIONS = e240.MIN_SESSIONS
STUDY = "E251"

# frozen before the face was read
STAR_DRAWS = 200        # shuffled own-column draws, headline star cell
ADD_DRAWS = 200         # shuffled additions, headline star cell
ERA_DRAWS = 60          # era cells are corroboration, not the headline
BAND_PCT = (0.0, 100.0)  # full range of the draws (one screened regressor at a time)
BAND_MODE = "full_draw_range_%d"
BASESEED = 20261103
SHARE_VOL_STRONG = 0.50   # an addition must take this much of the residual to own it
SHARE_VOL_WEAK = 0.35     # below this, the addition took nothing that matters
AGE_TREND_COLLINEAR = 0.98  # |corr(age, row index)| above this -> age is not identified
COUNTED_KINDS = ("headline", "window", "era", "neighbour")

VERDICTS = ("residual_is_own_turnover",
            "residual_is_own_volatility",
            "residual_partially_explained",
            "residual_inside_shuffled_band",
            "unresolved_too_few_rows")

CELLS = e245.CELLS


# ---------------------------------------------------------------- series on the row grid
def vol_series(panel, c):
    """|dy_c| lagged one row: the column's own preceding move magnitude, aligned to rows."""
    dy = panel["dy"][c]
    return [0.0] + [abs(dy[t - 1]) for t in range(1, len(dy))]


def _as_date(d):
    """The panel carries ISO date strings (e233.load_ohlc reads them off the csv verbatim)."""
    try:
        return datetime.strptime(str(d)[:10], "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def age_series(panel, first_date):
    """Calendar days since the member's first printed session, one value per row.

    Returns None when the grid is not ISO-dated: a fallback that silently used the row index
    would publish a trend dressed as an age, which is the one thing this face must not do.
    """
    f = _as_date(first_date)
    if f is None:
        return None
    out = []
    for d in panel["dates"]:
        dd = _as_date(d)
        if dd is None:
            return None
        out.append(float((dd - f).days))
    return out


def _mean(vals):
    vals = [v for v in vals if v is not None]
    return (sum(vals) / float(len(vals))) if vals else None


def _corr(a, b):
    n = min(len(a), len(b))
    if n < 4:
        return None
    x, y = np.asarray(a[:n], dtype=float), np.asarray(b[:n], dtype=float)
    if x.std() == 0.0 or y.std() == 0.0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def _share(before, after):
    if before is None or after is None:
        return None
    if abs(before) < 1e-12:
        return None
    return 1.0 - (after / before)


# ---------------------------------------------------------------- the nested designs
def _fit(panel, syms, c, dagg, extras=(), lag=1, x_override=None):
    """dy_m on own contemporaneous turnover + column c lag-1 + LOO aggregate lag-1 (+ extras).

    `extras` are full-length series already aligned to the row grid, appended in order, so the
    caller cannot hand in a list that is one short and slide the fit (E250's off-by-one trap).
    """
    out = {}
    xsrc = x_override if x_override is not None else panel["dx"][c]
    n = len(panel["dy"][syms[0]])
    for ex in extras:
        if len(ex) != n:
            return {"decided": False,
                    "reason": "extra series has %d rows, panel has %d" % (len(ex), n)}
    if len(dagg) != n:
        return {"decided": False, "reason": "aggregate has %d rows, panel has %d" % (len(dagg), n)}
    ts = list(range(lag + 1, n))
    if len(ts) <= 2 * (3 + len(extras)) + 8:
        return {"decided": False, "reason": "too few rows"}
    for m in syms:
        if m == c:
            continue
        dy = panel["dy"][m]
        y = [dy[t] for t in ts]
        cols = [[panel["dx"][m][t] for t in ts], [xsrc[t - lag] for t in ts],
                [dagg[t - lag] for t in ts]]
        for ex in extras:
            cols.append([ex[t] for t in ts])
        fit = e248._ols(y, cols)
        if fit is None:
            continue
        row = {"b_own": fit["beta"][1], "b1": fit["beta"][2], "c1": fit["beta"][3],
               "rows_used": fit["n"]}
        for j in range(len(extras)):
            row["x%d" % (j + 1)] = fit["beta"][4 + j]
        out[m] = row
    packed = e250._pack(out, "b1")
    if packed.get("decided"):
        packed["c1"] = _mean([r["c1"] for r in out.values()])
        for j in range(len(extras)):
            packed["x%d" % (j + 1)] = _mean([r["x%d" % (j + 1)] for r in out.values()])
    return packed


# ---------------------------------------------------------------- null bands
def _band(vals, draws_requested, seed):
    vals = sorted(vals)
    if len(vals) < 20:
        return {"draws_requested": draws_requested, "draws_used": len(vals), "band": None,
                "family": None}
    lo = vals[int(math.floor(BAND_PCT[0] / 100.0 * (len(vals) - 1)))]
    hi = vals[int(math.ceil(BAND_PCT[1] / 100.0 * (len(vals) - 1)))]
    med = vals[len(vals) // 2]
    return {"draws_requested": draws_requested, "draws_used": len(vals), "seed": seed,
            "band": {"lo": lo, "hi": hi, "median": med, "width": hi - lo, "draws": len(vals)},
            "family": {"max_abs": max(abs(x) for x in vals),
                       "median_abs": sorted(abs(x) for x in vals)[len(vals) // 2],
                       "draws": len(vals)},
            "note": "one screened regressor at a time -> pointwise band == family-wise line"}


def own_column_band(panel, syms, c, dagg, draws, seed):
    """Shuffle the column's own turnover in time; refit D0; keep b1."""
    rng = random.Random(seed)
    src = list(panel["dx"][c])
    kept = []
    for _ in range(draws):
        sh = src[:]
        rng.shuffle(sh)
        r = _fit(panel, syms, c, dagg, x_override=sh)
        if r.get("decided") and r.get("b1") is not None:
            kept.append(r["b1"])
    return _band(kept, draws, seed)


def addition_band(panel, syms, c, dagg, extras, which, base_b1, draws, seed):
    """Shuffle the added regressor in time; keep the DROP it produces (b1_shuffled - b1_base).

    This is the band the observed drop has to clear: an addition that moves b1 no more than its
    own time-shuffle does has not taken anything -- it has just been fitted.
    """
    rng = random.Random(seed)
    kept = []
    for _ in range(draws):
        trial = list(extras)
        sh = list(trial[which])
        rng.shuffle(sh)
        trial[which] = sh
        r = _fit(panel, syms, c, dagg, extras=trial)
        if r.get("decided") and r.get("b1") is not None and base_b1 is not None:
            kept.append(r["b1"] - base_b1)
    return _band(kept, draws, seed)


def _outside(val, band):
    if val is None or not band:
        return None
    return bool(val < band["lo"] or val > band["hi"])


# ---------------------------------------------------------------- one cell
def cell(per, syms, lo=None, hi=None, label="", kind="window", star_draws=STAR_DRAWS,
         add_draws=ADD_DRAWS, star_override=None):
    syms = [s for s in syms if per.get(s) and len(per[s]) > 2]
    out = {"label": label, "kind": kind, "members": list(syms),
           "window_inclusive": [lo, hi], "draws": {"star": star_draws, "addition": add_draws}}
    if len(syms) < 3:
        out.update({"decided": False, "verdict": "unresolved_too_few_rows",
                    "reason": "fewer than three members in this window"})
        return out
    win = e243.subset_per(per, syms, lo, hi)
    dates, panel = e240.common_increments(win, syms)
    out["sessions"] = len(dates)
    out["first"] = dates[0] if dates else None
    out["last"] = dates[-1] if dates else None
    if len(dates) < MIN_SESSIONS:
        out.update({"decided": False, "verdict": "unresolved_too_few_rows",
                    "reason": "common grid has %d sessions (floor %d)"
                              % (len(dates), MIN_SESSIONS)})
        return out

    star, star_source = e250.name_star(panel, syms)
    if star_override:
        star, star_source = (star_override if star_override in syms else star), "caller_override"
    out["star"] = star
    out["star_source"] = star_source

    lvl_dates = sorted(set.intersection(*[set(win[s]) for s in syms]))
    n_rows = len(panel["dy"][syms[0]])
    mid = _as_date(dates[len(dates) // 2])

    columns, residuals, ages_mid = {}, {}, {}
    for c in syms:
        loo = e250.aggregate_moves(win, syms, lvl_dates, exclude=c)
        if len(loo) != n_rows:
            columns[c] = {"decided": False,
                          "reason": "LOO aggregate %d rows vs panel %d" % (len(loo), n_rows)}
            continue
        vol = vol_series(panel, c)
        first_c = min(per[c])
        age = age_series(panel, first_c)
        base = _fit(panel, syms, c, loo)
        with_vol = _fit(panel, syms, c, loo, extras=[vol])
        # without a usable age series D2 is D1 and the face says so rather than fitting a trend
        with_both = (_fit(panel, syms, c, loo, extras=[vol, age]) if age is not None
                     else dict(with_vol))
        e = {"b1_base": base.get("b1"),
             "b1_with_vol": with_vol.get("b1"),
             "b1_with_vol_age": with_both.get("b1"),
             "b2_vol": with_vol.get("x1"),
             "b3_age": with_both.get("x2"),
             "c1_loo": base.get("c1"),
             "age_omitted": age is None,
             "members_fitted": base.get("members_fitted") if base.get("decided") else None,
             "decided": bool(base.get("decided") and with_vol.get("decided")
                             and with_both.get("decided"))}
        e["share_taken_by_vol"] = _share(base.get("b1"), with_vol.get("b1"))
        e["share_taken_by_vol_and_age"] = _share(base.get("b1"), with_both.get("b1"))
        e["age_corr_with_row_index"] = _corr(age, range(n_rows)) if age is not None else None
        e["age_identified"] = (None if e["age_corr_with_row_index"] is None
                               else bool(abs(e["age_corr_with_row_index"]) < AGE_TREND_COLLINEAR))
        fd = _as_date(first_c)
        e["age_days_at_mid"] = (float((mid - fd).days) if (mid and fd) else None)
        columns[c] = e
        if e.get("b1_base") is not None:
            residuals[c] = e["b1_base"]
            if e["age_days_at_mid"] is not None:
                ages_mid[c] = e["age_days_at_mid"]
    out["columns"] = columns

    # age read where it is measurable: a cross-member gradient, n = len(members), descriptive
    grad = None
    if len(residuals) >= 3:
        grad = _corr([residuals[k] for k in residuals], [ages_mid[k] for k in residuals])
    out["age_gradient_across_members"] = {
        "corr_residual_vs_age_at_mid": grad, "n": len(residuals),
        "decided": False,
        "note": "n = number of members; descriptive only, never a decision (age and identity "
                "are one object inside a window)"}

    if not star:
        # naming is E245's rule, not this face's: a window where no member is decisive has no
        # star to decompose, and saying "the star column did not fit" would blame the estimator
        out.update({"decided": False, "verdict": "unresolved_too_few_rows",
                    "reason": "no member was named star in this window (E245 lag-0 rule)"})
        return out

    st = columns.get(star) or {}
    b1 = st.get("b1_base")
    out["star_residual"] = {"b1": b1,
                            "b1_with_vol": st.get("b1_with_vol"),
                            "b1_with_vol_age": st.get("b1_with_vol_age"),
                            "share_taken_by_vol": st.get("share_taken_by_vol"),
                            "share_taken_by_vol_and_age": st.get("share_taken_by_vol_and_age"),
                            "age_identified": st.get("age_identified")}
    if not st.get("decided") or b1 is None:
        out.update({"decided": False, "verdict": "unresolved_too_few_rows",
                    "reason": "star column did not fit"})
        return out

    loo_star = e250.aggregate_moves(win, syms, lvl_dates, exclude=star)
    band_own = own_column_band(panel, syms, star, loo_star, star_draws, BASESEED + len(label))
    out["band_star_lag1"] = band_own
    out["star_outside_band"] = _outside(b1, band_own.get("band"))

    vol_star = vol_series(panel, star)
    age_star = age_series(panel, min(per[star]))
    out["age_series_available"] = age_star is not None
    obs_drop_vol = (st.get("b1_with_vol") - b1) if st.get("b1_with_vol") is not None else None
    band_vol = addition_band(panel, syms, star, loo_star, [vol_star], 0, b1, add_draws,
                             BASESEED + 7919 + len(label))
    out["band_vol_addition"] = band_vol
    out["vol_drop"] = obs_drop_vol
    out["vol_addition_outside_band"] = _outside(obs_drop_vol, band_vol.get("band"))

    if kind == "headline" and age_star is not None:
        obs_drop_age = (st.get("b1_with_vol_age") - st.get("b1_with_vol")
                        if st.get("b1_with_vol_age") is not None
                        and st.get("b1_with_vol") is not None else None)
        band_age = addition_band(panel, syms, star, loo_star, [vol_star, age_star], 1,
                                 st.get("b1_with_vol"), add_draws, BASESEED + 104729)
        out["band_age_addition"] = band_age
        out["age_drop"] = obs_drop_age
        out["age_addition_outside_band"] = _outside(obs_drop_age, band_age.get("band"))
    elif kind == "headline":
        out["band_age_addition"] = None
        out["age_drop"] = None
        out["age_addition_outside_band"] = None
        out["age_omitted_reason"] = "the common grid is not ISO-dated, so no age series exists"
    out["verdict"] = derive_verdict(b1, out["star_outside_band"],
                                    st.get("share_taken_by_vol"),
                                    out["vol_addition_outside_band"],
                                    len(columns))
    return out


def derive_verdict(b1, outside, share_vol, vol_outside, n_cols):
    """Frozen classification, recomputable from the published numbers alone."""
    if b1 is None or n_cols < 3:
        return "unresolved_too_few_rows"
    if not outside:
        return "residual_inside_shuffled_band"
    if vol_outside and share_vol is not None and share_vol >= SHARE_VOL_STRONG:
        return "residual_is_own_volatility"
    if share_vol is None or share_vol < SHARE_VOL_WEAK:
        return "residual_is_own_turnover"
    return "residual_partially_explained"


def rollup(cells):
    counted = [c for c in cells if c.get("kind") in COUNTED_KINDS and c.get("verdict")]
    by = {}
    for c in counted:
        by[c["verdict"]] = by.get(c["verdict"], 0) + 1
    head = next((c for c in cells if c.get("label") == "all_five"), {})
    verdict = (head.get("verdict")
               or (sorted(by, key=lambda k: -by[k])[0] if by else None))
    return {"verdict": verdict, "cells_by_verdict": by, "cells_counted": len(counted),
            "stable_across_cells": len(by) == 1}


def _summary(face):
    head = next((c for c in face["cells"] if c.get("label") == "all_five"), {})
    cols = head.get("columns") or {}
    return {"verdict": face["rollup"]["verdict"],
            "headline_verdict": head.get("verdict"),
            "headline_star": head.get("star"),
            "headline_star_b1": (head.get("star_residual") or {}).get("b1"),
            "headline_star_b1_with_vol": (head.get("star_residual") or {}).get("b1_with_vol"),
            "headline_star_b1_with_vol_age":
                (head.get("star_residual") or {}).get("b1_with_vol_age"),
            "headline_star_share_vol": (head.get("star_residual") or {}).get("share_taken_by_vol"),
            "headline_star_share_all":
                (head.get("star_residual") or {}).get("share_taken_by_vol_and_age"),
            "headline_star_outside_band": head.get("star_outside_band"),
            "headline_band_star_lag1": (head.get("band_star_lag1") or {}).get("band"),
            "headline_vol_drop": head.get("vol_drop"),
            "headline_band_vol_addition": (head.get("band_vol_addition") or {}).get("band"),
            "headline_vol_addition_outside_band": head.get("vol_addition_outside_band"),
            "headline_age_drop": head.get("age_drop"),
            "headline_age_addition_outside_band": head.get("age_addition_outside_band"),
            "headline_star_age_identified":
                (head.get("star_residual") or {}).get("age_identified"),
            "headline_b1_base_by_column": {k: v.get("b1_base") for k, v in cols.items()},
            "headline_b1_with_vol_by_column": {k: v.get("b1_with_vol") for k, v in cols.items()},
            "headline_b2_vol_by_column": {k: v.get("b2_vol") for k, v in cols.items()},
            "headline_share_vol_by_column": {k: v.get("share_taken_by_vol")
                                             for k, v in cols.items()},
            "headline_age_gradient": head.get("age_gradient_across_members"),
            "cells_by_verdict": face["rollup"]["cells_by_verdict"],
            "cells_counted": face["rollup"]["cells_counted"],
            "stable_across_cells": face["rollup"]["stable_across_cells"]}


def run(save=True, per=None, outdir=None, basket=None, star_draws=STAR_DRAWS,
        add_draws=ADD_DRAWS, era_draws=ERA_DRAWS, cells=None, star=None):
    per = per if per is not None else e239.panels()
    syms = [s for s in (basket or BASKET) if per.get(s)]
    outdir = outdir or OUTDIR
    out_cells = []
    for label, kind, lo, hi, members in (cells if cells is not None else CELLS):
        these = [s for s in (members or syms) if s in syms]
        out_cells.append(cell(per, these, lo, hi, label=label, kind=kind,
                              star_draws=star_draws if kind == "headline" else era_draws,
                              add_draws=add_draws if kind == "headline" else era_draws,
                              star_override=star))
    dates = sorted({d for s in syms for d in per[s]})
    face = {"study": STUDY,
            "title": "what is left of the star column once the book-wide aggregate is removed?",
            "generated": datetime.now().isoformat(timespec="seconds"),
            "evidence_cutoff": dates[-1] if dates else None,
            "frozen_spec": {"designs": ["D0 base (LOO aggregate in the row)",
                                        "D1 base + star's own lagged |move|",
                                        "D2 D1 + member age in days"],
                            "statistics": ["b1 per model", "share taken by each addition",
                                           "(1 - b1_after/b1_before)"],
                            "star_draws": STAR_DRAWS, "addition_draws": ADD_DRAWS,
                            "era_draws": ERA_DRAWS,
                            "band_mode": BAND_MODE % STAR_DRAWS,
                            "share_vol_strong": SHARE_VOL_STRONG,
                            "share_vol_weak": SHARE_VOL_WEAK,
                            "age_trend_collinear": AGE_TREND_COLLINEAR,
                            "verdicts": list(VERDICTS),
                            "base_seed": BASESEED,
                            "min_sessions": MIN_SESSIONS,
                            "reuse": "estimator e248._ols, star rule e250.name_star, "
                                     "LOO aggregate e250.aggregate_moves, grid e240"},
            "identification_caveat": "inside one window a member's age is a monotone function "
                                     "of the row index, so age cannot be separated from any other "
                                     "slow trend there (age_identified is published per column); "
                                     "the age effect is read only as a cross-member gradient in "
                                     "the era cells, and that gradient is descriptive (n = "
                                     "members), never a decision",
            "members": syms,
            "cells": out_cells,
            "no_bill": "decomposition only: no adoption, no re-pricing, no member billed",
            "written": None}
    face["rollup"] = rollup(out_cells)
    face["summary"] = _summary(face)
    if save:
        face["written"] = _write(face, outdir)
    return face


def _write(face, outdir):
    os.makedirs(outdir, exist_ok=True)
    cutoff = (face.get("evidence_cutoff") or "unknown")
    path = os.path.join(outdir, "STAROWN-%s.json" % cutoff)
    latest = os.path.join(outdir, "starown_latest.json")
    body = json.dumps(face, indent=1, sort_keys=True, ensure_ascii=False)
    for p in (path, latest):
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")
    return {"face": os.path.relpath(path, ROOT), "latest": os.path.relpath(latest, ROOT),
            "bytes": len(body)}


# ---------------------------------------------------------------- selftest fixtures
def _iso_dates(n, start="2020-01-01"):
    """ISO session labels for the fixtures: the age series refuses anything else, by design."""
    d0 = datetime.strptime(start, "%Y-%m-%d").date()
    return [(d0 + timedelta(days=i)).isoformat() for i in range(n)]


def _synth_turnover(n=320, k=5, b1=-0.7, own=0.5, seed=13, noise=0.02):
    """The column's own lag-1 turnover IS the driver: share taken by volatility must be ~0."""
    rng = random.Random(seed)
    syms = ["s%d" % i for i in range(k)]
    dates = _iso_dates(n)
    lt = {s: [math.log(1000.0) + 0.02 * i + 0.03 * rng.gauss(0, 1) for i in range(n)]
          for s in syms}
    lr = {s: [math.log(0.01)] for s in syms}
    for t in range(1, n):
        for s in syms:
            dx = lt[s][t] - lt[s][t - 1]
            lead = b1 * (lt["s0"][t - 1] - lt["s0"][t - 2]) if t >= 2 else 0.0
            lr[s].append(lr[s][-1] + lead + own * dx + noise * rng.gauss(0, 1))
    return {s: {dates[i]: (lr[s][i], lt[s][i]) for i in range(n)} for s in syms}, syms


def _synth_vol(n=320, k=5, lead=-0.7, own=0.5, seed=17, noise=0.02, link=0.6):
    """The driver is the star's lagged |move|, and the star's turnover only PROXIES it.

    Written down as truth: dy_m[t] = own*dx_m[t] + lead*|dy_s0[t-1]| + noise, with the star's
    own move series exogenous and its turnover built as link*|dy_s0[t]| + noise. So D0 prices the
    star's turnover (it proxies the real driver), and adding the real driver takes that away --
    the volatility branch. The link parameter is what makes the proxy real; at link=0 the base
    coefficient collapses and the face must say inside_band instead, which the flat fixture pins.
    """
    rng = random.Random(seed)
    syms = ["s%d" % i for i in range(k)]
    dates = _iso_dates(n)
    star = "s0"
    dy0 = [0.0] + [0.02 * rng.gauss(0, 1) for _ in range(n - 1)]
    lt = {}
    for s in syms:
        lv = math.log(1000.0)
        walk = [lv]
        for t in range(1, n):
            if s == star:
                step = link * abs(dy0[t]) + 0.01 * rng.gauss(0, 1)
            else:
                step = 0.02 + 0.03 * rng.gauss(0, 1)
            lv += step
            walk.append(lv)
        lt[s] = walk
    lr = {}
    for s in syms:
        vals = [math.log(0.01)]
        if s == star:
            # the star's own move is exogenous: its dy IS the written dy0
            for t in range(1, n):
                vals.append(vals[-1] + dy0[t])
        else:
            for t in range(1, n):
                dx = lt[s][t] - lt[s][t - 1]
                vals.append(vals[-1] + lead * abs(dy0[t - 1]) + own * dx
                            + noise * rng.gauss(0, 1))
        lr[s] = vals
    return {s: {dates[i]: (lr[s][i], lt[s][i]) for i in range(n)} for s in syms}, syms


def _synth_flat(n=320, k=5, seed=23):
    rng = random.Random(seed)
    syms = ["s%d" % i for i in range(k)]
    dates = _iso_dates(n)
    per = {}
    for s in syms:
        lv, lr = math.log(1000.0), math.log(0.01)
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
    one = (("all_five", "headline", None, None, None),)

    per, syms = _synth_turnover()
    f1 = run(save=False, per=per, basket=syms, star_draws=60, add_draws=60, era_draws=20,
             cells=one, star="s0")
    h1 = f1["cells"][0]
    legs.append(leg(h1.get("verdict") == "residual_is_own_turnover",
                    "a written turnover lead stays turnover (volatility takes almost nothing)",
                    {"verdict": h1.get("verdict"),
                     "b1": (h1.get("star_residual") or {}).get("b1"),
                     "share_vol": (h1.get("star_residual") or {}).get("share_taken_by_vol")}))
    legs.append(leg(h1.get("star_outside_band") is True,
                    "the residual clears its own shuffled band", h1.get("band_star_lag1")))
    legs.append(leg(h1.get("vol_addition_outside_band") is False,
                    "an inert addition does not clear the drop band",
                    {"drop": h1.get("vol_drop"),
                     "band": (h1.get("band_vol_addition") or {}).get("band")}))

    perv, symsv = _synth_vol()
    f2 = run(save=False, per=perv, basket=symsv, star_draws=60, add_draws=60, era_draws=20,
             cells=one, star="s0")
    h2 = f2["cells"][0]
    legs.append(leg(h2.get("verdict") == "residual_is_own_volatility",
                    "when the star's lagged |move| is the driver, the residual is volatility",
                    {"verdict": h2.get("verdict"),
                     "b1": (h2.get("star_residual") or {}).get("b1"),
                     "b1_with_vol": (h2.get("star_residual") or {}).get("b1_with_vol"),
                     "share_vol": (h2.get("star_residual") or {}).get("share_taken_by_vol")}))
    legs.append(leg(h2.get("vol_addition_outside_band") is True,
                    "the real driver's drop clears its own shuffled band",
                    {"drop": h2.get("vol_drop"),
                     "band": (h2.get("band_vol_addition") or {}).get("band")}))

    flat, fsyms = _synth_flat()
    f3 = run(save=False, per=flat, basket=fsyms, star_draws=60, add_draws=60, era_draws=20,
             cells=one, star="s0")
    h3 = f3["cells"][0]
    legs.append(leg(h3.get("verdict") == "residual_inside_shuffled_band",
                    "a no-lead panel keeps the residual inside its own band",
                    {"verdict": h3.get("verdict"), "band": h3.get("band_star_lag1")}))

    # age is a monotone function of the row index inside one window: the flag must say so
    st = (h1.get("columns") or {}).get("s0") or {}
    legs.append(leg(st.get("age_identified") is False,
                    "age is published as not identified inside one window",
                    {"corr": st.get("age_corr_with_row_index"),
                     "identified": st.get("age_identified")}))
    legs.append(leg(h1.get("age_gradient_across_members", {}).get("decided") is False,
                    "the cross-member age gradient is published as descriptive",
                    h1.get("age_gradient_across_members")))

    f5 = run(save=False, per=flat, basket=fsyms, star_draws=30, add_draws=30, era_draws=15,
             cells=one)
    h5 = f5["cells"][0]
    legs.append(leg(h5.get("decided") is False and h5.get("star") is None
                    and "no member was named star" in (h5.get("reason") or ""),
                    "a window with no named star says so, and does not blame the estimator",
                    {"star": h5.get("star"), "reason": h5.get("reason")}))

    d1 = run(save=False, per=per, basket=syms, star_draws=40, add_draws=40, era_draws=20,
             cells=one, star="s0")
    d2 = run(save=False, per=per, basket=syms, star_draws=40, add_draws=40, era_draws=20,
             cells=one, star="s0")
    legs.append(leg(json.dumps(d1["cells"][0].get("star_residual"), sort_keys=True)
                    == json.dumps(d2["cells"][0].get("star_residual"), sort_keys=True),
                    "deterministic under a fixed seed"))

    short, ssyms = _synth_turnover(n=90)
    f4 = run(save=False, per=short, basket=ssyms, star_draws=20, add_draws=20, era_draws=10,
             cells=one, star="s0")
    legs.append(leg(f4["cells"][0].get("decided") is False
                    and f4["cells"][0].get("verdict") == "unresolved_too_few_rows",
                    "session floor refuses a short grid",
                    {"sessions": f4["cells"][0].get("sessions")}))

    legs.append(leg(derive_verdict(-0.7, True, 0.05, False, 5) == "residual_is_own_turnover",
                    "verdict: nothing taken -> own turnover"))
    legs.append(leg(derive_verdict(-0.7, True, 0.9, True, 5) == "residual_is_own_volatility",
                    "verdict: the mover clears its band -> volatility"))
    legs.append(leg(derive_verdict(-0.7, True, 0.9, False, 5) == "residual_partially_explained",
                    "verdict: a big share without a clear band explains nothing"))
    legs.append(leg(derive_verdict(-0.7, False, 0.05, True, 5) == "residual_inside_shuffled_band",
                    "verdict: inside the band outranks the share"))
    legs.append(leg(derive_verdict(None, True, 0.0, True, 5) == "unresolved_too_few_rows",
                    "verdict: no coefficient cannot be classified"))
    legs.append(leg(derive_verdict(-0.7, True, 0.05, False, 2) == "unresolved_too_few_rows",
                    "verdict: fewer than three columns is unresolved"))

    # a misaligned extra series must be refused, not silently slid by one row
    dates, panel = e240.common_increments(per, syms)
    ref = _fit(panel, syms, "s0", [0.0] * len(panel["dy"]["s0"]),
               extras=[[0.0] * (len(panel["dy"]["s0"]) - 1)])
    legs.append(leg(ref.get("decided") is False, "a short extra series is refused", ref))
    return {"legs": legs, "passed": sum(1 for x in legs if x["pass"]), "total": len(legs),
            "ok": all(x["pass"] for x in legs)}


def _fmt(face):
    s = face["summary"]
    return ("%s | verdict %s | star %s b1 %s -> vol %s (share %s) -> vol+age %s | "
            "outside band %s | vol drop %s (%s) | cells %s"
            % (face["study"], s["verdict"], s["headline_star"], s["headline_star_b1"],
               s["headline_star_b1_with_vol"], s["headline_star_share_vol"],
               s["headline_star_b1_with_vol_age"], s["headline_star_outside_band"],
               s["headline_vol_drop"], s["headline_vol_addition_outside_band"],
               s["cells_by_verdict"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", nargs="?", default="run", choices=("run", "selftest"))
    ap.add_argument("--draws", type=int, default=STAR_DRAWS)
    args = ap.parse_args()
    if args.mode == "selftest":
        r = selftest()
        for x in r["legs"]:
            print("%s %s" % ("PASS" if x["pass"] else "FAIL", x["leg"]))
        print("selftest %d/%d" % (r["passed"], r["total"]))
        return 0 if r["ok"] else 1
    face = run(star_draws=args.draws, add_draws=args.draws)
    print(_fmt(face))
    print("written: %s" % (face.get("written") or {}).get("face"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())