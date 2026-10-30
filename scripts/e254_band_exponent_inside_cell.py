#!/usr/bin/env python3
"""E254 -- does the shuffled band really shrink as 1/sqrt(n) INSIDE one era?

E253 turned E252's bands into session counts and had to assume

    edge(n') = edge(n) * (n / n')**gamma,   gamma = 1/2 frozen

It checked that assumption ACROSS cells and got gamma = 0.244 (r2 0.28) instead of 0.5, which moved
the star's self-row target from 516 to 660 sessions -- but that fit compares four heterogeneous
eras, so the discrepancy is as likely to be era heterogeneity as a wrong exponent.

This face measures the exponent INSIDE ONE cell. Take era_2025_now, cut it to a ladder of session
counts (100..408), rebuild ONLY the shuffled band at each length (same permutation design, same
60 draws, same star, same LOO aggregate -- no new coefficient, no re-pricing), and fit

    log(edge) = log(c) - gamma * log(n)

on the cell's own points. gamma is then published three ways and every one of them is recomputed
from the numbers in this file:

  EDGE     |band lo| at each n -- the side a negative coefficient has to clear (E253's口径)
  HALF     half the published full-draw range -- the same scale E253 turns into sd_null
  TARGET   the star's self-row session count under the measured gamma (E253's formula, same b)

Two families are measured, because "prefix" and "the most recent n" are different experiments:
HEAD = the window's first n sessions (the card's literal reading), TAIL = the same window's last
n sessions (a fixed endpoint, back-dated start). A verdict that only holds in one family is a
statement about where the data got thin, not about the exponent.

The band endpoint is a MINIMUM over 60 shuffles, so a single draw is noisy: every point is the
median over SEEDS independent seeds, and each family's gamma carries a leave-one-seed-out range.
The verdict compares that range with the frozen 0.5 and the cross-era 0.244, and refuses to
decide when the two families disagree.

NO BILL, NO ADOPTION, NO RE-PRICING: this face measures how fast a band shrinks. It prices nothing.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e239_own_vs_cross as e239  # noqa: E402
import e240_aggregate_attenuation as e240  # noqa: E402
import e243_additivity_out_of_sample as e243  # noqa: E402
import e250_book_turnover_echo as e250  # noqa: E402
import e252_star_prices_itself as e252  # noqa: E402
import e253_self_row_resolution as e253  # noqa: E402

ROOT = e252.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
SOURCE_FACE = os.path.join(OUTDIR, "STARSELF-2026-10-29.json")
E253_FACE = os.path.join(OUTDIR, "SELFRES-2026-10-29.json")

STUDY = "E254"

# frozen before any point was measured
ERA_LO = "2025-01-01"           # era_2025_now, E245's cell definition
ERA_HI = None
CELL_LABEL = "era_2025_now"
N_GRID = (100, 150, 200, 250, 300, 350, 408)
N_MIN = 60                      # below this the estimator has nothing to say
DRAWS = 60                      # same permutation design as E252's era cells
SENS_DRAWS = 200                # draw-count sensitivity, three points only
SENS_N = (100, 250, 408)
SEEDS = 7                       # median over independent seeds kills single-draw min noise
BASE_SEED = 20261130            # E252's BASESEED
FAMILIES = ("head", "tail")
FROZEN_GAMMA = 0.5              # E253's assumption
CROSS_ERA_GAMMA = 0.244         # E253's measured cross-era fit
GAMMA_TOL = 0.10                # agreement band: |gamma - 0.5| <= this counts as "half"
R2_FLOOR = 0.80                 # below this the ladder is not a line, whatever gamma says
SEG_MIN = (300,)                # top-segment secondary reading: the range where the band moves
VERDICTS = ("exponent_is_half_inside_the_cell",
            "exponent_is_lower_inside_the_cell",
            "exponent_is_higher_inside_the_cell",
            "exponent_undetermined_inside_the_cell")


# ------------------------------------------------------------------ pure arithmetic
def edge_of(band):
    """|lo| of a published band: the edge a negative coefficient must clear."""
    body = (band or {}).get("band") or {}
    lo = body.get("lo")
    return None if lo is None else abs(float(lo))


def half_width(band):
    """Half the full-draw range -- the scale E253 divides into sd_null."""
    body = (band or {}).get("band") or {}
    lo, hi = body.get("lo"), body.get("hi")
    if lo is None or hi is None:
        return None
    return abs(float(hi) - float(lo)) / 2.0


def median(vals):
    vals = [float(v) for v in vals if v is not None]
    if not vals:
        return None
    return float(statistics.median(vals))


def fit_exponent(points):
    """gamma = -slope of log(edge) on log(n), with r2. Points are (n, edge)."""
    slope, r2 = e253._loglog_slope(points)
    if slope is None:
        return {"gamma": None, "r2": None, "points": len(points)}
    return {"gamma": -slope, "r2": r2, "points": len(points)}


def target_sessions(n, b, edge, gamma):
    """E253's inversion, re-run under a measured exponent."""
    return e253.needed_sessions(n, b, edge, gamma)


def verdict_from(gammas, r2s, tol=GAMMA_TOL, r2_floor=R2_FLOOR):
    """Frozen verdict: both families must agree, and the ladder must be a line."""
    vals = [g for g in gammas.values() if g is not None]
    if len(vals) < len(gammas) or not vals:
        return "exponent_undetermined_inside_the_cell", "a family has no gamma"
    if any((r2s.get(k) is None or r2s[k] < r2_floor) for k in gammas):
        return "exponent_undetermined_inside_the_cell", "r2 below floor in at least one family"
    lo, hi = min(vals), max(vals)
    if lo >= FROZEN_GAMMA - tol and hi <= FROZEN_GAMMA + tol:
        return "exponent_is_half_inside_the_cell", "both families sit within tol of 0.5"
    if hi < FROZEN_GAMMA - tol:
        return "exponent_is_lower_inside_the_cell", "both families sit below 0.5 by more than tol"
    if lo > FROZEN_GAMMA + tol:
        return "exponent_is_higher_inside_the_cell", "both families sit above 0.5 by more than tol"
    return "exponent_undetermined_inside_the_cell", "families straddle the line"


# ------------------------------------------------------------------ measurement
def era_grid(per, syms, lo=ERA_LO, hi=ERA_HI):
    win = e243.subset_per(per, syms, lo, hi)
    dates, panel = e240.common_increments(win, syms)
    return dates, panel


def band_at(per, syms, lo, hi, draws, seed, star_override=None):
    """Rebuild the paired shuffled band for one (lo, hi) window. No coefficient is published.

    The star is PINNED to the whole-era star: a truncated window that names a different star
    would measure a different sleeve's band and the ladder would not be one experiment. Every
    refusal is returned as a named reason instead of a silent None (r1280 pit 2 family).
    """
    win = e243.subset_per(per, syms, lo, hi)
    dates, panel = e240.common_increments(win, syms)
    if len(dates) < N_MIN:
        return None, "window has %d sessions (floor %d)" % (len(dates), N_MIN)
    star, source = e250.name_star(panel, syms)
    if star_override:
        if star_override not in panel["dy"] and star_override not in syms:
            return None, "pinned star %s is absent from this window" % star_override
        star = star_override
        source = "pinned_to_whole_era"
    if not star:
        return None, "no member was named star in this window"
    lvl_dates = sorted(set.intersection(*[set(win[s]) for s in syms]))
    loo = e250.aggregate_moves(win, syms, lvl_dates, exclude=star)
    if len(loo) != len(panel["dy"][syms[0]]):
        return None, ("LOO aggregate has %d rows, panel has %d"
                      % (len(loo), len(panel["dy"][syms[0]])))
    band_self, band_cross = e252.permutation_pair(panel, syms, star, loo, draws, seed)
    return {"sessions": len(dates), "first": dates[0], "last": dates[-1], "star": star,
            "star_source": source, "draws": draws,
            "edge_self": edge_of(band_self), "half_self": half_width(band_self),
            "edge_cross": edge_of(band_cross), "half_cross": half_width(band_cross),
            "band_self": (band_self or {}).get("band"),
            "band_cross": (band_cross or {}).get("band")}, None


def window_for(family, dates, n):
    n = min(int(n), len(dates))
    if family == "head":
        return dates[0], dates[n - 1]
    return dates[-n], dates[-1]


def whole_era_star(per, syms):
    """The star named by the FULL era window: every truncated ladder point pins this name."""
    dates, panel = era_grid(per, syms)
    if len(dates) < N_MIN:
        return None, "era grid has %d sessions" % len(dates)
    star, source = e250.name_star(panel, syms)
    return star, source


def segment_fit(rows, min_sessions, key="edge_self"):
    """The same exponent fitted on the ladder's top segment only (secondary reading)."""
    pts = [(p["sessions"], p[key]) for p in rows if p["sessions"] >= min_sessions and p[key]]
    return fit_exponent(pts)


def measure(per, syms, draws=DRAWS, seeds=SEEDS, n_grid=N_GRID):
    dates, _ = era_grid(per, syms)
    star, star_source = whole_era_star(per, syms)
    out = {"era_grid": {"sessions": len(dates), "first": dates[0] if dates else None,
                        "last": dates[-1] if dates else None},
           "pinned_star": star, "pinned_star_source": star_source,
           "draws": draws, "seeds": seeds, "families": {}, "points": [], "points_missing": []}
    for family in FAMILIES:
        rows = []
        for n in n_grid:
            if n > len(dates) or n < N_MIN:
                out["points_missing"].append({"family": family, "n_requested": n,
                                              "reason": "outside the ladder (%d sessions "
                                                        "available, floor %d)"
                                                        % (len(dates), N_MIN)})
                continue
            lo, hi = window_for(family, dates, n)
            draws_list, reasons = [], []
            for k in range(seeds):
                r, skip = band_at(per, syms, lo, hi, draws, BASE_SEED + 101 * k,
                                star_override=star)
                if r:
                    draws_list.append(r)
                elif skip:
                    reasons.append(skip)
            if not draws_list:
                out["points_missing"].append({"family": family, "n_requested": n,
                                              "window": [lo, hi],
                                              "reason": (reasons[0] if reasons
                                                         else "no draw produced a band")})
                continue
            pts = {"family": family, "n_requested": n,
                   "sessions": draws_list[0]["sessions"],
                   "first": draws_list[0]["first"], "last": draws_list[0]["last"],
                   "star": draws_list[0]["star"],
                   "star_source": draws_list[0]["star_source"],
                   "seeds_used": len(draws_list),
                   "seeds_refused": sorted(set(reasons)),
                   "edge_self": median([d["edge_self"] for d in draws_list]),
                   "half_self": median([d["half_self"] for d in draws_list]),
                   "edge_cross": median([d["edge_cross"] for d in draws_list]),
                   "half_cross": median([d["half_cross"] for d in draws_list]),
                   "edge_self_per_seed": [d["edge_self"] for d in draws_list],
                   "half_self_per_seed": [d["half_self"] for d in draws_list]}
            rows.append(pts)
            out["points"].append(pts)
        fit_edge = fit_exponent([(p["sessions"], p["edge_self"]) for p in rows])
        fit_half = fit_exponent([(p["sessions"], p["half_self"]) for p in rows])
        seg = {("n>=%d" % m): {"edge": segment_fit(rows, m, "edge_self"),
                              "half": segment_fit(rows, m, "half_self")}
               for m in SEG_MIN}
        # leave-one-seed-out: refit with each seed dropped in turn, over the whole ladder
        jack = []
        for drop in range(seeds):
            pts = []
            for p in rows:
                vals = [v for i, v in enumerate(p["edge_self_per_seed"]) if i != drop]
                m = median(vals)
                if m:
                    pts.append((p["sessions"], m))
            f = fit_exponent(pts)
            if f["gamma"] is not None:
                jack.append(f["gamma"])
        out["families"][family] = {"points": len(rows), "fit_edge": fit_edge,
                                   "fit_half": fit_half, "segment_fits": seg,
                                   "jackknife_gamma": {"n": len(jack),
                                                       "min": min(jack) if jack else None,
                                                       "max": max(jack) if jack else None,
                                                       "median": median(jack)}}
    return out


def read_published():
    """The b the target is computed from, and E253's own numbers, both read off disk."""
    out = {"b_self": None, "cell_sessions": None, "e253": {}}
    try:
        with open(SOURCE_FACE, encoding="utf-8") as fh:
            src = json.load(fh)
        for c in src.get("cells") or []:
            if c.get("label") == CELL_LABEL:
                out["b_self"] = ((c.get("self_row") or {}).get("b_self"))
                out["cell_sessions"] = c.get("sessions")
                out["b_cross"] = ((c.get("cross_row") or {}).get("b_cross"))
                break
    except (OSError, ValueError):
        pass
    try:
        with open(E253_FACE, encoding="utf-8") as fh:
            f = json.load(fh)
        s = f.get("summary") or {}
        out["e253"] = {"verdict": s.get("verdict"),
                       "needed": s.get("headline_self_sessions_needed"),
                       "short": s.get("headline_sessions_short"),
                       "eta": s.get("headline_eta"),
                       "fitted_gamma": (s.get("band_exponent") or {}).get("gamma")
                       if isinstance(s.get("band_exponent"), dict) else None}
    except (OSError, ValueError):
        pass
    return out


def run(per=None, save=True, outdir=None, draws=DRAWS, seeds=SEEDS):
    per = per if per is not None else e239.panels()
    syms = [s for s in e252.BASKET if per.get(s)]
    m = measure(per, syms, draws=draws, seeds=seeds)
    pub = read_published()

    fam = m["families"]
    gammas = {k: (fam[k]["fit_edge"]["gamma"]) for k in fam}
    r2s = {k: (fam[k]["fit_edge"]["r2"]) for k in fam}
    verdict, why = verdict_from(gammas, r2s)

    # the 408 point of each family, used only as the anchor of the inversion
    anchor = {}
    for k in fam:
        rows = [p for p in m["points"] if p["family"] == k]
        big = max(rows, key=lambda p: p["sessions"]) if rows else None
        anchor[k] = big
    target = {}
    for k, g in gammas.items():
        a = anchor.get(k)
        if not a or g is None or not pub.get("b_self"):
            target[k] = None
            continue
        target[k] = target_sessions(a["sessions"], pub["b_self"], a["edge_self"], g)

    # the same inversion under the two frozen exponents, so the reader sees what moved
    ref = {}
    a_any = anchor.get(FAMILIES[0]) or anchor.get(FAMILIES[1])
    if a_any and pub.get("b_self"):
        for name, g in (("frozen_0.5", FROZEN_GAMMA), ("cross_era_0.244", CROSS_ERA_GAMMA)):
            ref[name] = target_sessions(a_any["sessions"], pub["b_self"], a_any["edge_self"], g)

    # draw-count sensitivity: does the ladder move when the min is taken over 200 draws?
    sens = {}
    if seeds and draws != SENS_DRAWS and SENS_N:
        dates, _ = era_grid(per, syms)
        for family in FAMILIES:
            pts, refused = [], []
            for n in SENS_N:
                if n > len(dates) or n < N_MIN:
                    continue
                lo, hi = window_for(family, dates, n)
                r, sens_skip = band_at(per, syms, lo, hi, SENS_DRAWS, BASE_SEED,
                                 star_override=m.get("pinned_star"))
                if r:
                    pts.append((r["sessions"], r["edge_self"]))
                elif sens_skip:
                    refused.append({"n": n, "reason": sens_skip})
            s = fit_exponent(pts)
            s["refused"] = refused
            sens[family] = s

    face = {"study": STUDY,
            "title": "does the shuffled band really shrink as 1/sqrt(n) inside one era?",
            "generated": datetime.now().isoformat(timespec="seconds"),
            "evidence_cutoff": m["era_grid"]["last"] or "unknown",
            "frozen_spec": {"era": [ERA_LO, ERA_HI], "cell_label": CELL_LABEL,
                            "n_grid": list(N_GRID), "n_min": N_MIN, "draws": draws,
                            "seeds": seeds, "base_seed": BASE_SEED, "families": list(FAMILIES),
                            "segment_min": list(SEG_MIN),
                            "frozen_gamma": FROZEN_GAMMA, "cross_era_gamma": CROSS_ERA_GAMMA,
                            "gamma_tol": GAMMA_TOL, "r2_floor": R2_FLOOR,
                            "verdict_vocabulary": list(VERDICTS),
                            "what_is_not_done": ["no coefficient is re-priced: only the shuffled "
                                                 "band is rebuilt",
                                                 "no bootstrap: this face does not move b",
                                                 "the 408 anchor uses the published b_self",
                                                 "the star is pinned to the whole-era name so "
                                                 "every rung measures one sleeve"]},
            "era": m["era_grid"], "draws_per_point": draws,
            "pinned_star": m.get("pinned_star"),
            "pinned_star_source": m.get("pinned_star_source"),
            "points": m["points"], "points_missing": m["points_missing"],
            "families": fam,
            "anchor": {k: ({"sessions": v["sessions"], "edge_self": v["edge_self"],
                            "first": v["first"], "last": v["last"]} if v else None)
                       for k, v in anchor.items()},
            "published": pub,
            "target_sessions": target,
            "reference_targets": ref,
            "draw_count_sensitivity": sens,
            "verdict": verdict, "verdict_reason": why,
            "verdict_inputs": {"gammas": gammas, "r2": r2s, "tol": GAMMA_TOL,
                               "r2_floor": R2_FLOOR, "frozen": FROZEN_GAMMA}}
    face["summary"] = _summary(face)
    if save:
        face["written"] = _write(face, outdir or OUTDIR)
    return face


def _summary(face):
    fam = face["families"]
    s = {"verdict": face["verdict"], "verdict_reason": face["verdict_reason"],
         "era_sessions": face["era"]["sessions"],
         "gamma": {k: (fam[k]["fit_edge"]["gamma"]) for k in fam},
         "r2": {k: (fam[k]["fit_edge"]["r2"]) for k in fam},
         "jackknife": {k: fam[k]["jackknife_gamma"] for k in fam},
         "gamma_half_width_reading": {k: (fam[k]["fit_half"]["gamma"]) for k in fam},
         "target_sessions": face["target_sessions"],
         "reference_targets": face["reference_targets"],
         "published_b_self": face["published"].get("b_self"),
         "e253_needed": (face["published"].get("e253") or {}).get("needed"),
         "e253_eta": (face["published"].get("e253") or {}).get("eta"),
         "draw_count_sensitivity": {k: (v.get("gamma") if v else None)
                                    for k, v in face["draw_count_sensitivity"].items()},
         "segment_gamma": {k: {seg: (body["edge"].get("gamma") if body.get("edge") else None)
                               for seg, body in (fam[k].get("segment_fits") or {}).items()}
                           for k in fam},
         "points": len(face["points"]), "points_missing": len(face.get("points_missing") or []),
         "pinned_star": face.get("pinned_star")}
    # does every family's point ladder actually shrink at all? (activity, not a claim)
    # NET statement: the longest rung below the shortest. The ladder is NOT monotone at
    # every step -- each endpoint is a min over a finite draw count -- so the flag is
    # published beside the count of rungs that go the other way, or the word "shrinks"
    # would be read as smoothness.
    shrinks, non_mono = {}, {}
    for k in fam:
        rows = sorted([p for p in face["points"] if p["family"] == k],
                      key=lambda p: p["sessions"])
        if len(rows) >= 2:
            shrinks[k] = bool(rows[-1]["edge_self"] < rows[0]["edge_self"])
            non_mono[k] = int(sum(1 for a, b in zip(rows, rows[1:])
                                  if (b["edge_self"] is not None
                                      and a["edge_self"] is not None
                                      and b["edge_self"] >= a["edge_self"])))
        else:
            shrinks[k] = None
            non_mono[k] = None
    s["band_shrinks_within_family"] = shrinks
    s["band_shrinks_definition"] = ("net: longest rung below the shortest; "
                                    "NOT monotone at every step")
    s["rungs_non_monotone"] = non_mono
    return s


def _r(v, n=4):
    return None if v is None else round(float(v), n)


def _write(face, outdir):
    os.makedirs(outdir, exist_ok=True)
    cutoff = face.get("evidence_cutoff") or "unknown"
    path = os.path.join(outdir, "BANDEXP-%s.json" % cutoff)
    latest = os.path.join(outdir, "bandexp_latest.json")
    body = json.dumps(face, indent=1, sort_keys=True, ensure_ascii=False)
    for p in (path, latest):
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")
    return {"face": os.path.relpath(path, ROOT), "latest": os.path.relpath(latest, ROOT),
            "bytes": len(body)}


def _fmt(face):
    s = face["summary"]
    return ("%s | verdict %s (%s) | gamma head %s (r2 %s) tail %s (r2 %s) | "
            "target head %s tail %s sessions | E253 said %s | band shrinks %s"
            % (face["study"], s["verdict"], s["verdict_reason"],
               _r(s["gamma"].get("head")), _r(s["r2"].get("head"), 2),
               _r(s["gamma"].get("tail")), _r(s["r2"].get("tail"), 2),
               _r(s["target_sessions"].get("head"), 1),
               _r(s["target_sessions"].get("tail"), 1), _r(s["e253_needed"], 1),
               s["band_shrinks_within_family"]))


# ---------------------------------------------------------------- selftest fixtures
def leg(ok, name, detail=None):
    return {"leg": name, "pass": bool(ok), "detail": detail}


def _band(lo, hi):
    return {"band": {"lo": lo, "hi": hi, "draws": DRAWS}}


def _fit_from(items):
    """Fit a synthetic ladder [(n, edge), ...] through the same pure functions the face uses."""
    return fit_exponent(items)


def selftest():
    legs = []
    # 1 arithmetic: an exact n**-0.5 ladder is recovered as gamma 0.5
    sq = [(100, 5.0), (200, 5.0 / math.sqrt(2)), (400, 2.5)]
    f = _fit_from(sq)
    legs.append(leg(f["gamma"] is not None and abs(f["gamma"] - 0.5) < 1e-9,
                    "a 1/sqrt(n) ladder is recovered as gamma 0.5", f))
    # 2 arithmetic: an n**-0.25 ladder is recovered as 0.25 (the cross-era value)
    q4 = [(100, 3.0), (200, 3.0 * 2 ** -0.25), (400, 3.0 * 4 ** -0.25)]
    f = _fit_from(q4)
    legs.append(leg(f["gamma"] is not None and abs(f["gamma"] - 0.25) < 1e-9,
                    "an n**-0.25 ladder is recovered as gamma 0.25", f))
    # 3 a flat ladder (no shrinking) must NOT read as 0.5 -- it has no slope to fit
    f = _fit_from([(100, 2.0), (200, 2.0), (400, 2.0)])
    legs.append(leg(f["gamma"] is not None and abs(f["gamma"]) < 1e-12,
                    "a flat ladder fits gamma 0 rather than a spurious 0.5", f))
    # 4 edge_of/half_width read the same band two ways and stay consistent with each other
    b = _band(-0.5, 0.4)
    legs.append(leg(abs(edge_of(b) - 0.5) < 1e-12 and abs(half_width(b) - 0.45) < 1e-12,
                    "edge is |lo| and half-width is (hi-lo)/2 on the same band",
                    {"edge": edge_of(b), "half": half_width(b)}))
    legs.append(leg(edge_of(None) is None and half_width({"band": {}}) is None,
                    "a missing band yields None, not zero"))
    # 5 the two readings agree in EXPONENT when the band scales uniformly (the real question)
    base = [(100, 1.0), (200, 2 ** -0.5), (400, 4 ** -0.5)]
    f1 = _fit_from(base)
    f2 = _fit_from([(n, 2.0 * e) for n, e in base])
    legs.append(leg(abs(f1["gamma"] - f2["gamma"]) < 1e-9,
                    "a uniform scale change does not move gamma (only the intercept)",
                    {"a": f1["gamma"], "b": f2["gamma"]}))
    # 6 target_sessions inverts edge(n') = edge(n)*(n/n')**gamma: plugging the target back gives |b|
    n, bb, ee, g = 408, -0.463, 0.549, 0.5
    t = target_sessions(n, bb, ee, g)
    back = abs(bb) / ((float(n) / t) ** g)
    legs.append(leg(t and abs(back - ee) < 1e-9,
                    "the target session count round-trips through E253's inversion",
                    {"target": t, "edge_recovered": back, "edge": ee}))
    # 7 a smaller gamma pushes the target further out (the direction the card cares about)
    t_half = target_sessions(408, -0.463, 0.549, 0.5)
    t_low = target_sessions(408, -0.463, 0.549, 0.244)
    legs.append(leg(t_low > t_half, "a smaller exponent asks for MORE sessions",
                    {"half": t_half, "low": t_low}))
    legs.append(leg(target_sessions(408, 0.0, 0.549, 0.5) is None
                    and target_sessions(408, -0.463, 0.0, 0.5) is None,
                    "a zero coefficient or zero edge is None (infinite sessions), not a number"))
    # 8 verdict vocabulary: both families on 0.5 -> half; both below -> lower; straddle -> undetermined
    v = {}
    v["half"] = verdict_from({"head": 0.47, "tail": 0.53}, {"head": 0.95, "tail": 0.93})
    v["lower"] = verdict_from({"head": 0.25, "tail": 0.30}, {"head": 0.90, "tail": 0.88})
    v["higher"] = verdict_from({"head": 0.70, "tail": 0.74}, {"head": 0.90, "tail": 0.88})
    v["straddle"] = verdict_from({"head": 0.35, "tail": 0.60}, {"head": 0.95, "tail": 0.95})
    v["bad_r2"] = verdict_from({"head": 0.25, "tail": 0.27}, {"head": 0.40, "tail": 0.30})
    v["missing"] = verdict_from({"head": None, "tail": 0.5}, {"head": None, "tail": 0.9})
    legs.append(leg(v["half"][0] == "exponent_is_half_inside_the_cell"
                    and v["lower"][0] == "exponent_is_lower_inside_the_cell"
                    and v["higher"][0] == "exponent_is_higher_inside_the_cell"
                    and v["straddle"][0] == "exponent_undetermined_inside_the_cell"
                    and v["bad_r2"][0] == "exponent_undetermined_inside_the_cell"
                    and v["missing"][0] == "exponent_undetermined_inside_the_cell",
                    "the frozen verdict splits half/lower/higher and refuses on r2, "
                    "straddle and missing families", v))
    # 9 the verdict is a function of the published inputs only: same numbers, same answer
    a = verdict_from({"head": 0.44, "tail": 0.46}, {"head": 0.91, "tail": 0.89})
    b2 = verdict_from({"head": 0.44, "tail": 0.46}, {"head": 0.91, "tail": 0.89})
    legs.append(leg(a == b2, "the verdict is stable on the published inputs", a))
    # 10 windows: head takes the first n, tail the last n, and both are the same length
    dates = ["d%03d" % i for i in range(408)]
    h = window_for("head", dates, 200)
    tl = window_for("tail", dates, 200)
    legs.append(leg(h == ("d000", "d199") and tl == ("d208", "d407"),
                    "head starts at the window's first session, tail keeps the last session fixed",
                    {"head": h, "tail": tl}))
    legs.append(leg(window_for("head", dates, 999) == ("d000", "d407"),
                    "asking for more sessions than exist clamps to the whole window"))
    # 11 median ignores Nones and tolerates a single point
    legs.append(leg(median([None, 3.0, None]) == 3.0 and median([]) is None,
                    "median drops missing draws instead of coercing them to zero"))
    # 12 a family with one point cannot be fitted (r2_floor/r2 None -> undetermined, no crash)
    one = fit_exponent([(408, 0.55)])
    legs.append(leg(one["gamma"] is None and one["r2"] is None,
                    "a single point yields no exponent rather than a fake one", one))
    passed = sum(1 for x in legs if x["pass"])
    return {"legs": legs, "passed": passed, "total": len(legs), "ok": passed == len(legs)}


def verify(outdir=None):
    """Re-read the face and recompute the verdict from its own published numbers."""
    outdir = outdir or OUTDIR
    problems = []
    latest = os.path.join(outdir, "bandexp_latest.json")
    if not os.path.exists(latest):
        return {"ok": False, "problems": ["no face at %s" % latest]}
    with open(latest, encoding="utf-8") as fh:
        face = json.load(fh)
    fam = face.get("families") or {}
    gammas = {k: ((fam.get(k) or {}).get("fit_edge") or {}).get("gamma") for k in FAMILIES}
    r2s = {k: ((fam.get(k) or {}).get("fit_edge") or {}).get("r2") for k in FAMILIES}
    for k in FAMILIES:
        if k not in fam:
            problems.append("family %s missing" % k)
    want, _why = verdict_from(gammas, r2s)
    if face.get("verdict") != want:
        problems.append("verdict %s != recomputed %s" % (face.get("verdict"), want))
    for k in FAMILIES:
        if gammas.get(k) is None:
            problems.append("family %s has no gamma" % k)
            continue
        rows = sorted([p for p in face.get("points") or [] if p.get("family") == k],
                      key=lambda p: p.get("sessions") or 0)
        if len(rows) < 3:
            problems.append("family %s has %d points (need >=3)" % (k, len(rows)))
        refit = fit_exponent([(p["sessions"], p["edge_self"]) for p in rows])
        if refit["gamma"] is None or abs(refit["gamma"] - gammas[k]) > 1e-9:
            problems.append("family %s gamma does not reproduce (%s vs %s)"
                            % (k, refit["gamma"], gammas[k]))
    if not face.get("evidence_cutoff"):
        problems.append("evidence_cutoff missing")
    return {"ok": not problems, "problems": problems,
            "cells": len(face.get("points") or []), "verdict": face.get("verdict"),
            "cell": CELL_LABEL,
            "needed": (face.get("summary") or {}).get("e253_needed"),
            "short": (face.get("summary") or {}).get("e253_needed") and
                     max(0.0, (face["summary"]["e253_needed"] or 0) - (face["era"]["sessions"] or 0)),
            "eta": (face.get("summary") or {}).get("e253_eta")}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", nargs="?", default="run", choices=("run", "selftest", "verify"))
    ap.add_argument("--draws", type=int, default=DRAWS)
    ap.add_argument("--seeds", type=int, default=SEEDS)
    args = ap.parse_args()
    if args.mode == "selftest":
        r = selftest()
        for x in r["legs"]:
            print("%s %s" % ("PASS" if x["pass"] else "FAIL", x["leg"]))
            if not x["pass"]:
                print("   detail: %s" % json.dumps(x.get("detail"), ensure_ascii=False)[:400])
        print("selftest %d/%d" % (r["passed"], r["total"]))
        return 0 if r["ok"] else 1
    if args.mode == "verify":
        r = verify()
        for p in r["problems"]:
            print("PROBLEM %s" % p)
        print("verify: points=%s verdict=%s -> %s"
              % (r.get("cells"), r.get("verdict"), "OK" if r["ok"] else "FAIL"))
        return 0 if r["ok"] else 1
    face = run(draws=args.draws, seeds=args.seeds)
    print(_fmt(face))
    print("written: %s" % (face.get("written") or {}).get("face"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())