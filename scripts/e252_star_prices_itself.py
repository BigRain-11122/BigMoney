#!/usr/bin/env python3
"""E252 -- the star's turnover prices everyone else. Does it price the star?

E251 settled what the star column's residual is (its own lagged turnover, volatility and age
taking nothing) but every one of its fits prices OTHER members' moves: the reading is "the star's
turnover moves the rest of the book". E246/E249 also found the star's own row carries a negative
lead whose sign alternates by era, and E248 published +-0.805 without ever asking whether the
star prices ITSELF. This face runs the same decomposition with the star as the OUTCOME:

  S0  dy_s[t] = a + b_own*dx_s[t] + b_self*dx_s[t-1] + c1*dagg_loo[t-1]
  S1  S0 + b2*|dy_s[t-1]|                       (the star's own lagged move)
  S2  S1 + b3*age_s(t)                          (headline cell only; see identification caveat)
  C   dy_m[t] = a + b_own*dx_m[t] + b_cross*dx_s[t-1] + c1*dagg_loo_m[t-1]   (m != s)

b_self and b_cross are the SAME regressor (the star's lag-1 turnover) against two different
outcomes, fitted by the same estimator (e248._ols, Newey-West) on the same row grid, so they are
comparable in units by construction -- and that is the only comparison this face makes.

Two nulls, both design-shaped rather than distributional:

  * PERMUTATION band: the star's turnover column is shuffled in time and BOTH fits are re-run on
    the same shuffle. A coefficient that does not clear the band its own shuffled column produces
    has not been measured, on that side.
  * PAIRED BLOCK BOOTSTRAP: contiguous blocks of sessions are resampled and both fits are re-run
    on each draw, so the interval on (b_self - b_cross) carries the correlation the two fits share
    through the common regressor. Comparing two separately-built intervals would ignore it.

Verdicts are frozen and recomputable from the published numbers alone. NO BILL, NO ADOPTION, NO
RE-PRICING: a self-coefficient is a channel, not a cost.
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
import e248_star_lag_band as e248  # noqa: E402
import e250_book_turnover_echo as e250  # noqa: E402
import e251_star_own_component as e251  # noqa: E402

ROOT = e222.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
BASKET = e225.BASKET
MIN_SESSIONS = e240.MIN_SESSIONS
STUDY = "E252"

# frozen before the face was read
SELF_DRAWS = 200        # paired permutation draws, headline cell
BOOT_DRAWS = 400        # paired block-bootstrap draws, headline cell
ERA_DRAWS = 60          # era cells corroborate, they do not decide
BOOT_BLOCK = 20         # sessions per block (~one month)
BAND_PCT = (0.0, 100.0)
BAND_MODE = "full_draw_range_%d"
CI_PCT = (2.5, 97.5)
BASESEED = 20261130
SHARE_VOL_STRONG = 0.50
SHARE_VOL_WEAK = 0.35
AGE_TREND_COLLINEAR = 0.98
COUNTED_KINDS = ("headline", "window", "era", "neighbour")

VERDICTS = ("own_row_is_the_same_quantity",
            "own_row_is_a_different_mechanism",
            "self_row_inside_shuffled_band",
            "cross_column_inside_shuffled_band",
            "unresolved_too_few_rows")

CELLS = e245.CELLS


# ---------------------------------------------------------------- series on the row grid
def vol_series(panel, c):
    """|dy_c| lagged one row, aligned to the row grid (e251's helper, reused verbatim)."""
    return e251.vol_series(panel, c)


def age_series(panel, first_date):
    return e251.age_series(panel, first_date)


def _mean(vals):
    vals = [v for v in vals if v is not None]
    return (sum(vals) / float(len(vals))) if vals else None


def _share(before, after):
    return e251._share(before, after)


def _diff_coef(a, b):
    if a is None or b is None:
        return None
    return a - b


# ---------------------------------------------------------------- the two fits
def _rows(n, lag=1):
    return list(range(lag + 1, n))


def fit_self(panel, star, dagg, extras=(), lag=1, x_override=None, rows=None):
    """dy_star on its own contemporaneous turnover, its own lag-1, and the LOO aggregate.

    `rows` lets the block bootstrap re-fit on resampled sessions without re-deriving the columns;
    an extra series whose length disagrees with the panel is refused rather than slid (E250's
    off-by-one trap).
    """
    n = len(panel["dy"][star])
    for ex in extras:
        if len(ex) != n:
            return {"decided": False,
                    "reason": "extra series has %d rows, panel has %d" % (len(ex), n)}
    if len(dagg) != n:
        return {"decided": False, "reason": "aggregate has %d rows, panel has %d" % (len(dagg), n)}
    ts = rows if rows is not None else _rows(n, lag)
    if len(ts) <= 2 * (3 + len(extras)) + 8:
        return {"decided": False, "reason": "too few rows"}
    src = x_override if x_override is not None else panel["dx"][star]
    dy = panel["dy"][star]
    y = [dy[t] for t in ts]
    cols = [[panel["dx"][star][t] for t in ts], [src[t - lag] for t in ts],
            [dagg[t - lag] for t in ts]]
    for ex in extras:
        cols.append([ex[t] for t in ts])
    fit = e248._ols(y, cols)
    if fit is None:
        return {"decided": False, "reason": "HAC fit refused (singular or too few rows)"}
    row = {"decided": True, "rows_used": fit["n"], "r2": fit["r2"],
           "b_own": fit["beta"][1], "b_self": fit["beta"][2], "c1": fit["beta"][3],
           "beta": fit["beta"], "cov": fit["cov"]}
    for j in range(len(extras)):
        row["x%d" % (j + 1)] = fit["beta"][4 + j]
    return row


def fit_cross(panel, syms, star, dagg, extras=(), lag=1, x_override=None, rows=None,
              with_detail=False):
    """E251's design C, re-fit here so both sides can share one `rows` list in the bootstrap.

    Returns the mean over the other members of the star's lag-1 coefficient (b_cross) -- the same
    statistic e251._fit packs -- plus the per-member rows when asked.
    """
    n = len(panel["dy"][syms[0]])
    for ex in extras:
        if len(ex) != n:
            return {"decided": False, "reason": "extra series has %d rows, panel has %d"
                                                % (len(ex), n)}
    if len(dagg) != n:
        return {"decided": False, "reason": "aggregate has %d rows, panel has %d" % (len(dagg), n)}
    ts = rows if rows is not None else _rows(n, lag)
    if len(ts) <= 2 * (3 + len(extras)) + 8:
        return {"decided": False, "reason": "too few rows"}
    src = x_override if x_override is not None else panel["dx"][star]
    per, kept = {}, []
    for m in syms:
        if m == star:
            continue
        dy = panel["dy"][m]
        y = [dy[t] for t in ts]
        cols = [[panel["dx"][m][t] for t in ts], [src[t - lag] for t in ts],
                [dagg[t - lag] for t in ts]]
        for ex in extras:
            cols.append([ex[t] for t in ts])
        fit = e248._ols(y, cols)
        if fit is None:
            continue
        per[m] = {"b_cross": fit["beta"][2], "b_own": fit["beta"][1], "c1": fit["beta"][3],
                  "rows_used": fit["n"]}
        kept.append(fit["beta"][2])
    if not kept:
        return {"decided": False, "reason": "no member outside the star fitted"}
    out = {"decided": True, "b_cross": _mean(kept), "members_fitted": len(kept),
           "b_cross_min": min(kept), "b_cross_max": max(kept),
           "b_cross_spread": max(kept) - min(kept)}
    if with_detail:
        out["per_member"] = per
    return out


# ---------------------------------------------------------------- nulls
def _band(vals, draws_requested, seed):
    return e251._band(vals, draws_requested, seed)


def _outside(val, band):
    return e251._outside(val, band)


def _pct(sorted_vals, p):
    if not sorted_vals:
        return None
    idx = int(math.floor(p / 100.0 * (len(sorted_vals) - 1)))
    return sorted_vals[max(0, min(len(sorted_vals) - 1, idx))]


def permutation_pair(panel, syms, star, dagg, draws, seed):
    """Shuffle the star's turnover in time ONCE per draw and re-run BOTH fits.

    One shuffle for the pair is the point: the two coefficients are then compared under the same
    destroyed signal, exactly as they are compared under the same real one.
    """
    rng = random.Random(seed)
    src = list(panel["dx"][star])
    self_vals, cross_vals = [], []
    for _ in range(draws):
        sh = src[:]
        rng.shuffle(sh)
        a = fit_self(panel, star, dagg, x_override=sh)
        b = fit_cross(panel, syms, star, dagg, x_override=sh)
        if a.get("decided") and a.get("b_self") is not None:
            self_vals.append(a["b_self"])
        if b.get("decided") and b.get("b_cross") is not None:
            cross_vals.append(b["b_cross"])
    return (_band(self_vals, draws, seed), _band(cross_vals, draws, seed))


def _blocks(n_rows, block, rng, n_out):
    """Contiguous session blocks resampled with replacement, keeping time order inside a block."""
    lo = 0
    hi = n_rows - 1
    span = hi - lo + 1
    nb = max(1, int(math.ceil(span / float(block))))
    picked = []
    for _ in range(nb):
        start = rng.randint(lo, max(lo, hi - block + 1))
        picked.extend(range(start, min(hi + 1, start + block)))
    if not picked:
        return []
    # trim/expand to roughly the original length: the estimator needs the rows, not the count
    return picked[:max(1, int(round(n_out)))]


def bootstrap_pair(panel, syms, star, dagg, draws, block, seed):
    """Paired block bootstrap of the two coefficients and of their difference."""
    rng = random.Random(seed)
    n = len(panel["dy"][star])
    base = _rows(n)
    self_vals, cross_vals, diffs = [], [], []
    for _ in range(draws):
        rows = _blocks(len(base), block, rng, len(base))
        if len(rows) < 20:
            continue
        a = fit_self(panel, star, dagg, rows=rows)
        b = fit_cross(panel, syms, star, dagg, rows=rows)
        if a.get("decided") and b.get("decided"):
            self_vals.append(a["b_self"])
            cross_vals.append(b["b_cross"])
            diffs.append(a["b_self"] - b["b_cross"])
    out = {"draws_requested": draws, "draws_used": len(diffs), "block": block, "seed": seed}
    for name, vals in (("self", self_vals), ("cross", cross_vals), ("diff", diffs)):
        if len(vals) < 20:
            out[name] = {"ci": None, "used": len(vals)}
            continue
        s = sorted(vals)
        out[name] = {"ci": [_pct(s, CI_PCT[0]), _pct(s, CI_PCT[1])],
                     "median": s[len(s) // 2], "used": len(vals),
                     "sd": float(np.std(np.asarray(vals, dtype=float)))}
    out["note"] = ("paired: each draw re-fits BOTH rows on the same resampled sessions, so the "
                   "interval on the difference carries the correlation the two fits share")
    return out


# ---------------------------------------------------------------- verdict
def derive_verdict(b_self, b_cross, self_outside, cross_outside, diff_ci):
    """Frozen classification, recomputable from the published numbers alone."""
    if b_self is None or b_cross is None:
        return "unresolved_too_few_rows"
    if self_outside is False:
        return "self_row_inside_shuffled_band"
    if cross_outside is False:
        return "cross_column_inside_shuffled_band"
    if diff_ci is None:
        return "own_row_is_a_different_mechanism"
    if diff_ci[0] <= 0.0 <= diff_ci[1]:
        return "own_row_is_the_same_quantity"
    return "own_row_is_a_different_mechanism"


# ---------------------------------------------------------------- one cell
def cell(per, syms, lo=None, hi=None, label="", kind="window", self_draws=SELF_DRAWS,
         boot_draws=BOOT_DRAWS, star_override=None):
    syms = [s for s in syms if per.get(s) and len(per[s]) > 2]
    out = {"label": label, "kind": kind, "members": list(syms),
           "window_inclusive": [lo, hi],
           "draws": {"permutation": self_draws, "bootstrap": boot_draws,
                     "block": BOOT_BLOCK}}
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
        star = star_override if star_override in syms else star
        star_source = "caller_override"
    out["star"] = star
    out["star_source"] = star_source
    if not star:
        out.update({"decided": False, "verdict": "unresolved_too_few_rows",
                    "reason": "no member was named star in this window (E245 lag-0 rule)"})
        return out

    lvl_dates = sorted(set.intersection(*[set(win[s]) for s in syms]))
    n_rows = len(panel["dy"][syms[0]])
    loo_star = e250.aggregate_moves(win, syms, lvl_dates, exclude=star)
    if len(loo_star) != n_rows:
        out.update({"decided": False, "verdict": "unresolved_too_few_rows",
                    "reason": "LOO aggregate %d rows vs panel %d" % (len(loo_star), n_rows)})
        return out

    vol = vol_series(panel, star)
    first_star = min(per[star])
    age = age_series(panel, first_star)

    s0 = fit_self(panel, star, loo_star)
    s1 = fit_self(panel, star, loo_star, extras=[vol])
    s2 = (fit_self(panel, star, loo_star, extras=[vol, age]) if age is not None else dict(s1))
    c0 = fit_cross(panel, syms, star, loo_star, with_detail=True)
    out["self_row"] = {
        "b_own": s0.get("b_own"), "b_self": s0.get("b_self"), "c1_loo": s0.get("c1"),
        "b_self_with_vol": s1.get("b_self"), "b2_vol": s1.get("x1"),
        "b_self_with_vol_age": s2.get("b_self"), "b3_age": s2.get("x2"),
        "share_taken_by_vol": _share(s0.get("b_self"), s1.get("b_self")),
        "share_taken_by_vol_and_age": _share(s0.get("b_self"), s2.get("b_self")),
        "age_omitted": age is None,
        "rows_used": s0.get("rows_used"), "r2": s0.get("r2"),
        "decided": bool(s0.get("decided") and s1.get("decided") and s2.get("decided")),
        "reason": s0.get("reason") if not s0.get("decided") else None,
    }
    out["cross_row"] = {"b_cross": c0.get("b_cross"),
                        "members_fitted": c0.get("members_fitted"),
                        "min": c0.get("b_cross_min"), "max": c0.get("b_cross_max"),
                        "spread": c0.get("b_cross_spread"),
                        "per_member": c0.get("per_member"),
                        "decided": bool(c0.get("decided")),
                        "reason": c0.get("reason") if not c0.get("decided") else None}

    b_self = s0.get("b_self")
    b_cross = c0.get("b_cross")
    if not (s0.get("decided") and c0.get("decided")) or b_self is None or b_cross is None:
        out.update({"decided": False, "verdict": "unresolved_too_few_rows",
                    "reason": "self %s / cross %s did not fit"
                              % (out["self_row"].get("reason"), out["cross_row"].get("reason"))})
        return out

    band_self, band_cross = permutation_pair(panel, syms, star, loo_star, self_draws,
                                             BASESEED + len(label))
    out["band_self"] = band_self
    out["band_cross"] = band_cross
    out["self_outside_band"] = _outside(b_self, band_self.get("band"))
    out["cross_outside_band"] = _outside(b_cross, band_cross.get("band"))

    boot = bootstrap_pair(panel, syms, star, loo_star, boot_draws, BOOT_BLOCK,
                          BASESEED + 7919 + len(label))
    out["bootstrap"] = boot
    diff_ci = (boot.get("diff") or {}).get("ci")
    out["b_self_minus_b_cross"] = b_self - b_cross
    out["diff_ci"] = diff_ci

    # age inside one window is a monotone function of the row index: say so, per cell
    corr_age = e251._corr(age, range(n_rows)) if age is not None else None
    out["age_corr_with_row_index"] = corr_age
    out["age_identified"] = (None if corr_age is None
                             else bool(abs(corr_age) < AGE_TREND_COLLINEAR))
    out["verdict"] = derive_verdict(b_self, b_cross, out["self_outside_band"],
                                    out["cross_outside_band"], diff_ci)
    out["decided"] = True
    return out


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
    sr = head.get("self_row") or {}
    cr = head.get("cross_row") or {}
    return {"verdict": face["rollup"]["verdict"],
            "headline_verdict": head.get("verdict"),
            "headline_star": head.get("star"),
            "headline_b_self": sr.get("b_self"),
            "headline_b_cross": cr.get("b_cross"),
            "headline_diff": head.get("b_self_minus_b_cross"),
            "headline_diff_ci": head.get("diff_ci"),
            "headline_self_outside_band": head.get("self_outside_band"),
            "headline_cross_outside_band": head.get("cross_outside_band"),
            "headline_band_self": (head.get("band_self") or {}).get("band"),
            "headline_band_cross": (head.get("band_cross") or {}).get("band"),
            "headline_b_own_self": sr.get("b_own"),
            "headline_b_self_with_vol": sr.get("b_self_with_vol"),
            "headline_share_vol": sr.get("share_taken_by_vol"),
            "headline_b2_vol": sr.get("b2_vol"),
            "headline_self_boot_ci": ((head.get("bootstrap") or {}).get("self") or {}).get("ci"),
            "headline_cross_boot_ci": ((head.get("bootstrap") or {}).get("cross") or {}).get("ci"),
            "headline_sessions": head.get("sessions"),
            "headline_cross_per_member": cr.get("per_member"),
            "cells_by_verdict": face["rollup"]["cells_by_verdict"],
            "cells_counted": face["rollup"]["cells_counted"],
            "stable_across_cells": face["rollup"]["stable_across_cells"]}


def run(save=True, per=None, outdir=None, basket=None, self_draws=SELF_DRAWS,
        boot_draws=BOOT_DRAWS, era_draws=ERA_DRAWS, cells=None, star=None):
    per = per if per is not None else e239.panels()
    syms = [s for s in (basket or BASKET) if per.get(s)]
    outdir = outdir or OUTDIR
    out_cells = []
    for label, kind, lo, hi, members in (cells if cells is not None else CELLS):
        these = [s for s in (members or syms) if s in syms]
        out_cells.append(cell(per, these, lo, hi, label=label, kind=kind,
                              self_draws=self_draws if kind == "headline" else era_draws,
                              boot_draws=boot_draws if kind == "headline" else era_draws,
                              star_override=star))
    dates = sorted({d for s in syms for d in per[s]})
    face = {"study": STUDY,
            "title": "the star's turnover prices everyone else -- does it price the star?",
            "generated": datetime.now().isoformat(timespec="seconds"),
            "evidence_cutoff": dates[-1] if dates else None,
            "frozen_spec": {"designs": ["S0 self row: own contemporaneous + own lag-1 + LOO agg",
                                        "S1 S0 + star's own lagged |move|",
                                        "S2 S1 + age in days (headline only)",
                                        "C cross rows: member own + star lag-1 + LOO agg"],
                            "nulls": ["paired time-shuffled permutation band (one shuffle "
                                      "destroys the regressor for both fits)",
                                      "paired block bootstrap on the difference"],
                            "permutation_draws": SELF_DRAWS, "bootstrap_draws": BOOT_DRAWS,
                            "era_draws": ERA_DRAWS, "block_sessions": BOOT_BLOCK,
                            "ci_pct": list(CI_PCT),
                            "band_mode": BAND_MODE % SELF_DRAWS,
                            "share_vol_strong": SHARE_VOL_STRONG,
                            "share_vol_weak": SHARE_VOL_WEAK,
                            "age_trend_collinear": AGE_TREND_COLLINEAR,
                            "verdicts": list(VERDICTS),
                            "base_seed": BASESEED, "min_sessions": MIN_SESSIONS,
                            "reuse": "estimator e248._ols, star rule e250.name_star, LOO "
                                     "aggregate e250.aggregate_moves, band/_outside e251, "
                                     "grid e240/e243"},
            "identification_caveat": "inside one window a member's age is a monotone function of "
                                     "the row index, so age is not separable from any slow trend "
                                     "there; the age extra is fitted and published with "
                                     "age_identified per cell, never used to decide",
            "comparability_note": "b_self and b_cross are the same regressor (the star's lag-1 "
                                  "turnover) against two outcomes under one estimator and one row "
                                  "grid; the difference is read on a paired bootstrap, not on two "
                                  "independently built intervals",
            "members": syms,
            "cells": out_cells,
            "no_bill": "channel identification only: no adoption, no re-pricing, no member billed",
            "written": None}
    face["rollup"] = rollup(out_cells)
    face["summary"] = _summary(face)
    if save:
        face["written"] = _write(face, outdir)
    return face


def _write(face, outdir):
    os.makedirs(outdir, exist_ok=True)
    cutoff = (face.get("evidence_cutoff") or "unknown")
    path = os.path.join(outdir, "STARSELF-%s.json" % cutoff)
    latest = os.path.join(outdir, "starself_latest.json")
    body = json.dumps(face, indent=1, sort_keys=True, ensure_ascii=False)
    for p in (path, latest):
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")
    return {"face": os.path.relpath(path, ROOT), "latest": os.path.relpath(latest, ROOT),
            "bytes": len(body)}


# ---------------------------------------------------------------- selftest fixtures
def _dates(n, start="2020-01-01"):
    from datetime import timedelta
    d0 = datetime.strptime(start, "%Y-%m-%d").date()
    return [(d0 + timedelta(days=i)).isoformat() for i in range(n)]


def _per_from(syms, dates, level, ret):
    return {s: {dates[i]: (ret[s][i], level[s][i]) for i in range(len(dates))} for s in syms}


def _synth(n=340, k=5, own=0.5, self_lead=-0.6, cross_lead=-0.6, seed=31, noise=0.02,
           vol_lead=0.0, link=0.0):
    """One written truth, two levers: self_lead prices the star's own move, cross_lead the others'.

    vol_lead/link add the volatility channel: the star's own move is driven by |dy| and its
    turnover only proxies that driver (link>0), which is the branch S1 has to catch.
    """
    rng = random.Random(seed)
    syms = ["s%d" % i for i in range(k)]
    star = "s0"
    dates = _dates(n)
    lt = {s: [math.log(1000.0)] for s in syms}
    lr = {s: [math.log(0.01)] for s in syms}
    dy = {s: [0.0] for s in syms}
    for t in range(1, n):
        step = {}
        for s in syms:
            if s == star:
                step[s] = link * abs(dy[star][t - 1]) + 0.01 * rng.gauss(0, 1)
            else:
                step[s] = 0.02 + 0.03 * rng.gauss(0, 1)
        star_prev = (lt[star][t - 1] - lt[star][t - 2]) if t >= 2 else 0.0
        for s in syms:
            if s == star:
                move = own * step[s] + self_lead * star_prev \
                    + vol_lead * abs(dy[star][t - 1]) + noise * rng.gauss(0, 1)
            else:
                move = own * step[s] + cross_lead * star_prev + noise * rng.gauss(0, 1)
            lr[s].append(lr[s][-1] + move)
            dy[s].append(move)
            lt[s].append(lt[s][-1] + step[s])
    return _per_from(syms, dates, lt, lr), syms


def _synth_flat(n=340, k=5, seed=37):
    rng = random.Random(seed)
    syms = ["s%d" % i for i in range(k)]
    dates = _dates(n)
    lt = {s: [math.log(1000.0)] for s in syms}
    lr = {s: [math.log(0.01)] for s in syms}
    for _ in range(1, n):
        for s in syms:
            lt[s].append(lt[s][-1] + 0.02 * rng.gauss(0, 1))
            lr[s].append(lr[s][-1] + 0.02 * rng.gauss(0, 1))
    return _per_from(syms, dates, lt, lr), syms


def leg(ok, name, detail=None):
    return {"leg": name, "pass": bool(ok), "detail": detail}


ONE = (("all_five", "headline", None, None, None),)


def selftest():
    legs = []

    # 1. the same quantity on both sides: the difference interval must contain zero
    per, syms = _synth(self_lead=-0.6, cross_lead=-0.6, seed=31)
    f1 = run(save=False, per=per, basket=syms, self_draws=60, boot_draws=120, era_draws=20,
             cells=ONE, star="s0")
    h1 = f1["cells"][0]
    legs.append(leg(h1.get("verdict") == "own_row_is_the_same_quantity",
                    "a written equal lead reads as one quantity",
                    {"verdict": h1.get("verdict"), "b_self": (h1.get("self_row") or {}).get("b_self"),
                     "b_cross": (h1.get("cross_row") or {}).get("b_cross"),
                     "diff": h1.get("b_self_minus_b_cross"), "ci": h1.get("diff_ci")}))
    legs.append(leg(h1.get("self_outside_band") is True and h1.get("cross_outside_band") is True,
                    "both rows clear their own shuffled bands",
                    {"self": h1.get("band_self"), "cross": h1.get("band_cross")}))

    # 2. the star prices itself with a different strength: the difference must exclude zero
    per2, syms2 = _synth(self_lead=-0.9, cross_lead=-0.25, seed=41)
    f2 = run(save=False, per=per2, basket=syms2, self_draws=60, boot_draws=120, era_draws=20,
             cells=ONE, star="s0")
    h2 = f2["cells"][0]
    legs.append(leg(h2.get("verdict") == "own_row_is_a_different_mechanism",
                    "a written unequal lead reads as a different mechanism",
                    {"verdict": h2.get("verdict"),
                     "b_self": (h2.get("self_row") or {}).get("b_self"),
                     "b_cross": (h2.get("cross_row") or {}).get("b_cross"),
                     "ci": h2.get("diff_ci")}))
    legs.append(leg(h2.get("diff_ci") is not None and
                    (h2["diff_ci"][0] > 0.0 or h2["diff_ci"][1] < 0.0),
                    "the difference interval excludes zero on the unequal fixture", h2.get("diff_ci")))

    # 3. a panel with no lead at all keeps BOTH rows inside their bands
    flat, fsyms = _synth_flat()
    f3 = run(save=False, per=flat, basket=fsyms, self_draws=60, boot_draws=120, era_draws=20,
             cells=ONE, star="s0")
    h3 = f3["cells"][0]
    legs.append(leg(h3.get("verdict") == "self_row_inside_shuffled_band",
                    "a flat panel keeps the self row inside its band",
                    {"verdict": h3.get("verdict"), "band": h3.get("band_self"),
                     "b_self": (h3.get("self_row") or {}).get("b_self")}))

    # 4. the volatility branch: the star's own lag is |move| and its turnover only proxies it
    perv, symsv = _synth(self_lead=0.0, cross_lead=-0.4, vol_lead=-0.8, link=0.9, seed=43)
    f4 = run(save=False, per=perv, basket=symsv, self_draws=60, boot_draws=120, era_draws=20,
             cells=ONE, star="s0")
    h4 = f4["cells"][0]
    sr4 = h4.get("self_row") or {}
    legs.append(leg(sr4.get("b_self") is not None and sr4.get("b_self_with_vol") is not None
                    and abs(sr4.get("b_self_with_vol")) < abs(sr4.get("b_self")) or
                    (sr4.get("share_taken_by_vol") or 0.0) > 0.2,
                    "the volatility channel takes part of the self coefficient",
                    {"b_self": sr4.get("b_self"), "with_vol": sr4.get("b_self_with_vol"),
                     "share": sr4.get("share_taken_by_vol"), "b2": sr4.get("b2_vol")}))

    # 5. one shuffle destroys the regressor for BOTH fits (the pairing is real)
    dates, panel = e240.common_increments(per, syms)
    lvl = sorted(set.intersection(*[set(per[s]) for s in syms]))
    loo = e250.aggregate_moves(per, syms, lvl, exclude="s0")
    band_s, band_c = permutation_pair(panel, syms, "s0", loo, 40, BASESEED + 3)
    legs.append(leg(band_s.get("band") is not None and band_c.get("band") is not None,
                    "both permutation bands are produced from the same shuffles",
                    {"self_draws": band_s.get("draws_used"),
                     "cross_draws": band_c.get("draws_used")}))

    # 6. determinism
    d1 = run(save=False, per=per, basket=syms, self_draws=30, boot_draws=60, era_draws=15,
             cells=ONE, star="s0")
    d2 = run(save=False, per=per, basket=syms, self_draws=30, boot_draws=60, era_draws=15,
             cells=ONE, star="s0")
    legs.append(leg(json.dumps(d1["cells"][0].get("bootstrap"), sort_keys=True)
                    == json.dumps(d2["cells"][0].get("bootstrap"), sort_keys=True),
                    "deterministic under a fixed seed"))

    # 7. session floor
    short, ssyms = _synth(n=90, seed=47)
    f5 = run(save=False, per=short, basket=ssyms, self_draws=20, boot_draws=40, era_draws=10,
             cells=ONE, star="s0")
    legs.append(leg(f5["cells"][0].get("verdict") == "unresolved_too_few_rows",
                    "session floor refuses a short grid",
                    {"sessions": f5["cells"][0].get("sessions")}))

    # 8. a misaligned extra series must be refused, not slid by one row
    ref = fit_self(panel, "s0", loo, extras=[[0.0] * (len(panel["dy"]["s0"]) - 1)])
    legs.append(leg(ref.get("decided") is False, "a short extra series is refused", ref))
    refc = fit_cross(panel, syms, "s0", loo, extras=[[0.0] * (len(panel["dy"]["s0"]) - 1)])
    legs.append(leg(refc.get("decided") is False, "the cross fit refuses it too", refc))

    # 9. the cross leg reproduces e251's packed statistic on the same panel (same estimator)
    e251_fit = e251._fit(panel, syms, "s0", loo)
    ours = fit_cross(panel, syms, "s0", loo)
    got, want = ours.get("b_cross"), e251_fit.get("b1")
    legs.append(leg(got is not None and want is not None and abs(got - want) < 1e-12,
                    "the cross coefficient is e251's own statistic, not a re-implementation",
                    {"e252": got, "e251": want}))

    # 10. verdict branches, driven by hand
    legs.append(leg(derive_verdict(-0.6, -0.6, True, True, [-0.05, 0.05])
                    == "own_row_is_the_same_quantity", "verdict: overlapping interval -> same"))
    legs.append(leg(derive_verdict(-0.9, -0.2, True, True, [-0.9, -0.5])
                    == "own_row_is_a_different_mechanism",
                    "verdict: disjoint interval -> different mechanism"))
    legs.append(leg(derive_verdict(-0.6, -0.6, False, True, [-0.05, 0.05])
                    == "self_row_inside_shuffled_band",
                    "verdict: an unmeasured self row outranks the comparison"))
    legs.append(leg(derive_verdict(-0.6, -0.6, True, False, [-0.05, 0.05])
                    == "cross_column_inside_shuffled_band",
                    "verdict: an unmeasured cross column outranks the comparison"))
    legs.append(leg(derive_verdict(None, -0.6, True, True, None) == "unresolved_too_few_rows",
                    "verdict: no coefficient cannot be classified"))

    # 11. the verify mode is a check, not a decoration: it must accept a consistent face and
    # refuse both a flipped verdict and a cross column that drifted off E251's published statistic
    import shutil
    import tempfile
    td = tempfile.mkdtemp(prefix="e252")
    try:
        fv = run(save=True, per=per, basket=syms, outdir=td, self_draws=30, boot_draws=60,
                 era_draws=10, cells=ONE, star="s0")
        hc = (fv["cells"][0].get("cross_row") or {}).get("b_cross")
        _stub(td, {"cells": [{"label": "all_five", "star": "s0",
                              "star_residual": {"b1": hc}}]})
        legs.append(leg(verify(outdir=td)["ok"] is True,
                        "verify accepts a face whose numbers agree with themselves",
                        verify(outdir=td).get("problems")))
        _stub(td, {"cells": [{"label": "all_five", "star": "s0",
                              "star_residual": {"b1": (hc or 0.0) + 0.5}}]})
        vr = verify(outdir=td)
        legs.append(leg(vr["ok"] is False
                        and any("cross coefficient" in p for p in vr["problems"]),
                        "verify refuses a cross column that is not E251's statistic",
                        vr.get("problems")))
        _stub(td, {"cells": [{"label": "all_five", "star": "s0",
                              "star_residual": {"b1": hc}}]})
        face_path = os.path.join(td, "starself_latest.json")
        with open(face_path, encoding="utf-8") as fh:
            tampered = json.load(fh)
        tampered["cells"][0]["verdict"] = "own_row_is_a_different_mechanism"
        with open(face_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(tampered, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
        vr2 = verify(outdir=td)
        legs.append(leg(vr2["ok"] is False
                        and any("re-derive" in p for p in vr2["problems"]),
                        "verify refuses a verdict the published numbers do not produce",
                        vr2.get("problems")))
    finally:
        shutil.rmtree(td, ignore_errors=True)

    return {"legs": legs, "passed": sum(1 for x in legs if x["pass"]), "total": len(legs),
            "ok": all(x["pass"] for x in legs)}


def _stub(outdir, body):
    with open(os.path.join(outdir, "starown_latest.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(json.dumps(body, indent=1, sort_keys=True, ensure_ascii=False) + "\n")


def verify(outdir=None):
    """Re-derive every published cell from the face on disk -- no estimation, no network.

    This is what the S6 chain runs: the full face costs minutes (permutation + bootstrap on six
    cells), and a chain leg that re-burned it every cycle would be a re-measurement, not a check.
    What has to be true every cycle is that the face still says what its own numbers say, and that
    its cross column is still E251's published statistic.
    """
    outdir = outdir or OUTDIR
    path = os.path.join(outdir, "starself_latest.json")
    bad = []
    if not os.path.exists(path):
        return {"ok": False, "problems": ["face missing: %s" % path]}
    with open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    vocab = set((face.get("frozen_spec") or {}).get("verdicts") or ())
    cells = [c for c in (face.get("cells") or []) if c.get("verdict")]
    if not cells:
        bad.append("no cell carries a verdict")
    for c in cells:
        if c["verdict"] not in vocab:
            bad.append("cell %s outside the frozen vocabulary" % c.get("label"))
        sr, cr = c.get("self_row") or {}, c.get("cross_row") or {}
        if sr.get("b_self") is None or cr.get("b_cross") is None:
            continue
        again = derive_verdict(sr["b_self"], cr["b_cross"], c.get("self_outside_band"),
                               c.get("cross_outside_band"), c.get("diff_ci"))
        if again != c["verdict"]:
            bad.append("cell %s publishes %s but its numbers re-derive %s"
                       % (c.get("label"), c["verdict"], again))
        d = c.get("b_self_minus_b_cross")
        if d is None or abs(d - (sr["b_self"] - cr["b_cross"])) > 1e-12:
            bad.append("cell %s publishes a difference its own betas do not produce"
                       % c.get("label"))
        if c["verdict"] == "own_row_is_the_same_quantity":
            ci = c.get("diff_ci")
            if not ci or not (ci[0] <= 0.0 <= ci[1]):
                bad.append("cell %s names one quantity without an interval covering zero"
                           % c.get("label"))
        b, bv = sr.get("b_self"), sr.get("b_self_with_vol")
        if b is not None and bv is not None and abs(b) > 1e-12 and sr.get("share_taken_by_vol") is not None:
            if abs((1.0 - bv / b) - sr["share_taken_by_vol"]) > 1e-9:
                bad.append("cell %s publishes a volatile share its own betas do not produce"
                           % c.get("label"))
    head = next((c for c in cells if c.get("label") == "all_five"), None)
    if head is None:
        bad.append("no headline cell")
    else:
        other = os.path.join(outdir, "starown_latest.json")
        if not os.path.exists(other):
            bad.append("starown face missing, so the cross identity cannot be checked")
        else:
            with open(other, encoding="utf-8") as fh:
                prev = json.load(fh)
            prev_head = next((c for c in (prev.get("cells") or [])
                              if c.get("label") == "all_five"), None)
            if not prev_head or prev_head.get("star") != head.get("star"):
                bad.append("the two faces do not name the same star")
            else:
                want = (prev_head.get("star_residual") or {}).get("b1")
                got = (head.get("cross_row") or {}).get("b_cross")
                if want is None or got is None or abs(want - got) > 1e-9:
                    bad.append("the cross coefficient is not E251's published number "
                               "(%s vs %s)" % (want, got))
    if not face.get("no_bill"):
        bad.append("the face does not carry its no-bill line")
    if not face.get("comparability_note"):
        bad.append("the face does not carry its comparability note")
    s = face.get("summary") or {}
    return {"ok": not bad, "problems": bad, "cells": len(cells),
            "verdict": s.get("verdict"), "star": s.get("headline_star"),
            "b_self": s.get("headline_b_self"), "b_cross": s.get("headline_b_cross"),
            "diff_ci": s.get("headline_diff_ci"), "face": os.path.relpath(path, ROOT)}


def _fmt(face):
    s = face["summary"]
    return ("%s | verdict %s | star %s b_self %s vs b_cross %s | diff %s ci %s | "
            "outside self/cross %s/%s | share_vol %s | cells %s"
            % (face["study"], s["verdict"], s["headline_star"], s["headline_b_self"],
               s["headline_b_cross"], s["headline_diff"], s["headline_diff_ci"],
               s["headline_self_outside_band"], s["headline_cross_outside_band"],
               s["headline_share_vol"], s["cells_by_verdict"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", nargs="?", default="run", choices=("run", "selftest", "verify"))
    ap.add_argument("--draws", type=int, default=None)
    ap.add_argument("--boot", type=int, default=None)
    args = ap.parse_args()
    if args.mode == "verify":
        r = verify()
        for p in r["problems"]:
            print("PROBLEM %s" % p)
        print("verify: cells=%s verdict=%s star=%s b_self=%s b_cross=%s diff_ci=%s -> %s"
              % (r.get("cells"), r.get("verdict"), r.get("star"),
                 None if r.get("b_self") is None else round(r["b_self"], 4),
                 None if r.get("b_cross") is None else round(r["b_cross"], 4),
                 [None if v is None else round(v, 3) for v in (r.get("diff_ci") or [])],
                 "OK" if r["ok"] else "FAIL"))
        return 0 if r["ok"] else 1
    if args.mode == "selftest":
        r = selftest()
        for x in r["legs"]:
            print("%s %s" % ("PASS" if x["pass"] else "FAIL", x["leg"]))
            if not x["pass"]:
                print("   detail: %s" % json.dumps(x.get("detail"), ensure_ascii=False)[:400])
        print("selftest %d/%d" % (r["passed"], r["total"]))
        return 0 if r["ok"] else 1
    face = run(self_draws=args.draws or SELF_DRAWS, boot_draws=args.boot or BOOT_DRAWS)
    print(_fmt(face))
    print("written: %s" % (face.get("written") or {}).get("face"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())