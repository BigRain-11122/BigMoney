#!/usr/bin/env python3
"""E255 -- is E254's undetermined band exponent starved of DRAWS or of RUNGS?

E254 rebuilt the shuffled band inside era_2025_now at seven session counts and could not name an
exponent: the HEAD family fitted gamma with r2 0.67 against a frozen 0.80 floor, and a 3-rung
re-read at 200 draws gave a different HEAD value than 60 draws. Two readings survive, and they
cost very different things:

  DRAWS ARE THE CONSTRAINT  the 5%/95% band endpoint is a quantile of a finite permutation sample,
      so it is noisy. More draws buys a cleaner endpoint, the ladder gets straighter, and the
      0.80 floor is reachable without any more history.

  RUNGS ARE THE CONSTRAINT  seven rungs on 408 sessions cannot identify a slope whatever the draw
      count; only a longer window buys it, and E253's target session count stays a range.

This face settles which, by measuring the SAME ladder at four draw counts (60/120/240/480) with
every point held fixed. The prefix structure does the work: one run of 480 draws from one seed
contains the 60/120/240 runs of that same seed as its prefixes (random.Random(seed) emits the same
shuffle sequence whatever the loop length), so the four ladders are ONE experiment read four ways
rather than four experiments that might disagree for a different reason.

Three things are published per (family, draw count), all recomputed from the numbers in the file:

  edge / gamma / r2     the ladder, the exponent and its straightness
  gamma_sd_seed         the Monte-Carlo contribution -- scatter of gamma over seeds. If draws are
                        the constraint this falls like 1/sqrt(D).
  gamma_sd_fit          the regression's own slope standard error -- the structural scatter of the
                        rungs about the line. Draws cannot move it.

The verdict compares those two: a face whose seed scatter is a small fraction of its fit scatter
cannot be repaired by permutations, because the noise it is complaining about is not there.

NO BILL, NO ADOPTION, NO RE-PRICING, NO BOOTSTRAP: this face re-reads one band ladder. It moves no
coefficient and prices nothing.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import statistics
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e239_own_vs_cross as e239  # noqa: E402
import e250_book_turnover_echo as e250  # noqa: E402
import e251_star_own_component as e251  # noqa: E402
import e252_star_prices_itself as e252  # noqa: E402
import e253_self_row_resolution as e253  # noqa: E402
import e254_band_exponent_inside_cell as e254  # noqa: E402

ROOT = e252.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

STUDY = "E255"
CELL_LABEL = e254.CELL_LABEL
ERA_LO, ERA_HI = e254.ERA_LO, e254.ERA_HI

# frozen before any point was measured
N_GRID = e254.N_GRID              # 100..408, the SAME rungs at every draw count
D_GRID = (60, 120, 240, 480)      # the draw counts the prefix structure gives for free
D_MAIN = D_GRID[0]                # E254's own reading, kept as the reference column
SEEDS = 3                         # seeds, so the Monte-Carlo scatter is measurable
BASE_SEED = e254.BASE_SEED
FAMILIES = e254.FAMILIES
R2_FLOOR = e254.R2_FLOOR          # 0.80, the frozen straightness floor
GAMMA_TOL = e254.GAMMA_TOL
FROZEN_GAMMA = e254.FROZEN_GAMMA

# a draw count is "enough" only if the seed scatter is small beside the fit scatter; the frozen
# fraction is 1/2 -- at that point permutations are no longer the binding noise.
MC_FRACTION_FLOOR = 0.5
# an extrapolation is only offered inside this budget, and is labelled as an extrapolation
D_BUDGET = 2000
# "no rung moved more than this between 240 and the top draw count" = the endpoint has settled
CONV_PCT = 2.0

VERDICTS = ("draws_are_the_constraint",
            "rungs_are_the_constraint",
            "exponent_clears_on_draws_alone",
            "undetermined")


# ------------------------------------------------------------------ pure arithmetic
def prefix_edge(vals, draws, pct=e251.BAND_PCT[0]):
    """|lo| of the band formed by the FIRST `draws` per-draw coefficients (the nested prefix)."""
    vals = [v for v in (vals or [])[:int(draws)] if v is not None]
    if len(vals) < 20:
        return None
    band = e251._band(vals, draws, None)
    body = band.get("band") or {}
    lo = body.get("lo")
    return None if lo is None else abs(float(lo))


def prefix_half(vals, draws):
    """Half the prefix band's full range -- E254's second reading, kept for the identity check."""
    vals = [v for v in (vals or [])[:int(draws)] if v is not None]
    if len(vals) < 20:
        return None
    band = e251._band(vals, draws, None)
    body = band.get("band") or {}
    lo, hi = body.get("lo"), body.get("hi")
    if lo is None or hi is None:
        return None
    return abs(float(hi) - float(lo)) / 2.0


def median(vals):
    vals = [float(v) for v in vals if v is not None]
    return None if not vals else float(statistics.median(vals))


def stdev(vals):
    vals = [float(v) for v in vals if v is not None]
    return None if len(vals) < 2 else float(statistics.stdev(vals))


def fit_ladder(points):
    """gamma = -slope of log(edge) on log(n) plus the slope's own standard error.

    The standard error is the regression residual scaled by the design -- the structural scatter
    that no draw count can touch. None when the ladder is too short or degenerate.
    """
    pts = [(float(n), float(e)) for n, e in points if n and e and e > 0]
    if len(pts) < 3:
        return {"gamma": None, "r2": None, "gamma_se": None, "resid_sd": None,
                "points": len(pts)}
    xs = [math.log(p[0]) for p in pts]
    ys = [math.log(p[1]) for p in pts]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return {"gamma": None, "r2": None, "gamma_se": None, "resid_sd": None,
                "points": len(pts)}
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    inter = my - slope * mx
    resid = [y - (inter + slope * x) for x, y in zip(xs, ys)]
    sst = sum((y - my) ** 2 for y in ys)
    sse = sum(r * r for r in resid)
    r2 = None if sst <= 0 else 1.0 - sse / sst
    # slope SE = sqrt(SSE/(n-2)) / sqrt(SXX)
    se = None
    if len(pts) > 2 and sxx > 0:
        se = math.sqrt(sse / (len(pts) - 2)) / math.sqrt(sxx)
    return {"gamma": -slope, "r2": r2, "gamma_se": se,
            "resid_sd": None if len(pts) < 2 else float(statistics.stdev(resid)),
            "points": len(pts)}


def draws_needed(rows, r2_floor=R2_FLOOR):
    """Smallest draw count in the grid whose r2 clears the floor, or None (no table-reading)."""
    ok = [r["draws"] for r in sorted(rows, key=lambda r: r["draws"])
          if r.get("r2") is not None and r["r2"] >= r2_floor]
    return ok[0] if ok else None


def extrapolate_draws(rows, r2_floor=R2_FLOOR, d_budget=D_BUDGET):
    """A 1/sqrt(D) extrapolation of the r2 trend, offered ONLY as an extrapolation.

    Returns the first power-of-two draw count at which the fitted line would reach the floor, or
    None when the trend points the wrong way (r2 not improving) or the budget runs out.
    """
    rows = sorted([r for r in rows if r.get("r2") is not None and r.get("draws")],
                  key=lambda r: r["draws"])
    if len(rows) < 2:
        return {"reaches_floor": None, "draws": None,
                "reason": "fewer than two draw counts (the 1/D model has one parameter)"}
    last = rows[-1]
    first = rows[0]
    if last["r2"] <= first["r2"]:
        return {"reaches_floor": False, "draws": None,
                "reason": "r2 does not improve with draws (%.4f -> %.4f)"
                          % (first["r2"], last["r2"])}
    if last["r2"] >= r2_floor:
        return {"reaches_floor": True, "draws": last["draws"],
                "reason": "the largest measured draw count already clears the floor"}
    # r2(D) = 1 - k/D  (a variance that falls as 1/D turns into an unexplained fraction that does)
    miss = 1.0 - last["r2"]
    if miss <= 0:
        return {"reaches_floor": True, "draws": last["draws"], "reason": "already clear"}
    # miss(D') = miss(D) * D / D'  ->  need D' = miss*D/(1-floor)
    target_miss = 1.0 - r2_floor
    need = miss * last["draws"] / target_miss
    if need > d_budget:
        return {"reaches_floor": False, "draws": None,
                "reason": "1/D extrapolation needs %.0f draws, beyond the %d budget"
                          % (need, d_budget), "extrapolated_draws": need}
    return {"reaches_floor": True, "draws": int(math.ceil(need)),
            "reason": "1/D extrapolation from the measured trend", "extrapolated_draws": need}


def verdict_from(published):
    """Frozen verdict from the two published families' tables."""
    fam = published or {}
    cleared = {k: draws_needed(v.get("rows") or []) for k, v in fam.items()}
    if not fam or any(k not in fam for k in FAMILIES):
        return "undetermined", "a family is missing"
    if all(cleared.get(k) for k in FAMILIES):
        return ("exponent_clears_on_draws_alone",
                "both families clear the r2 floor inside the measured draw grid")
    # Monte-Carlo scatter vs structural scatter, on the largest draw count each family has
    frac = {}
    for k in FAMILIES:
        rows = sorted(fam[k].get("rows") or [], key=lambda r: r.get("draws") or 0)
        if not rows:
            return "undetermined", "family %s has no rows" % k
        last = rows[-1]
        mc, se = last.get("gamma_sd_seed"), last.get("gamma_se")
        if mc is None or se is None or se <= 0:
            return "undetermined", ("family %s cannot separate seed scatter from fit scatter"
                                    % k)
        frac[k] = mc / se
    if all(v <= MC_FRACTION_FLOOR for v in frac.values()):
        return ("rungs_are_the_constraint",
                "no draw count in the grid clears the r2 floor and seed scatter is at most "
                "%.2fx the fit scatter in both families (floor %.2f)"
                % (max(frac.values()), MC_FRACTION_FLOOR))
    return ("draws_are_the_constraint",
            "no draw count clears the floor yet, but seed scatter is still %.2fx the fit "
            "scatter in at least one family -- the permutations are not converged"
            % max(frac.values()))


# ------------------------------------------------------------------ measurement
def per_draw_pair(panel, syms, star, dagg, draws, seed):
    """The per-draw coefficients, NOT aggregated: one shuffle feeds both fits (E252's design)."""
    rng = random.Random(seed)
    src = list(panel["dx"][star])
    self_vals, cross_vals = [], []
    for _ in range(int(draws)):
        sh = src[:]
        rng.shuffle(sh)
        a = e252.fit_self(panel, star, dagg, x_override=sh)
        b = e252.fit_cross(panel, syms, star, dagg, x_override=sh)
        self_vals.append(a.get("b_self") if a.get("decided") else None)
        cross_vals.append(b.get("b_cross") if b.get("decided") else None)
    return self_vals, cross_vals


def measure_window(per, syms, lo, hi, star, seeds=SEEDS, d_grid=D_GRID, n_min=e254.N_MIN):
    """One rung: per-seed draw streams at max(d_grid), read back at every draw count."""
    win = e254.e243.subset_per(per, syms, lo, hi)
    dates, panel = e254.e240.common_increments(win, syms)
    if len(dates) < n_min:
        return None, "window has %d sessions (floor %d)" % (len(dates), n_min)
    st, source = e250.name_star(panel, syms)
    if star:
        if star not in panel["dy"]:
            return None, "pinned star %s is absent from this window" % star
        st, source = star, "pinned_to_whole_era"
    if not st:
        return None, "no member was named star in this window"
    lvl_dates = sorted(set.intersection(*[set(win[s]) for s in syms]))
    loo = e250.aggregate_moves(win, syms, lvl_dates, exclude=st)
    if len(loo) != len(panel["dy"][syms[0]]):
        return None, "LOO aggregate has %d rows, panel has %d" % (len(loo),
                                                                 len(panel["dy"][syms[0]]))
    d_max = max(d_grid)
    streams = []
    for k in range(seeds):
        s_vals, c_vals = per_draw_pair(panel, syms, st, loo, d_max, BASE_SEED + 101 * k)
        streams.append({"self": s_vals, "cross": c_vals})
    out = {"sessions": len(dates), "first": dates[0], "last": dates[-1], "star": st,
           "star_source": source, "seeds": len(streams), "by_draws": {}}
    for d in d_grid:
        rec = {"draws": d}
        for leg in ("self", "cross"):
            vals = [prefix_edge(st["%s" % leg], d) for st in streams]
            half = [prefix_half(st["%s" % leg], d) for st in streams]
            rec["edge_%s" % leg] = median(vals)
            rec["edge_%s_seed_spread" % leg] = (max([v for v in vals if v is not None])
                                                - min([v for v in vals if v is not None])
                                                if len([v for v in vals if v is not None]) > 1
                                                else None)
            rec["edge_%s_per_seed" % leg] = vals
            rec["half_%s" % leg] = median(half)
        out["by_draws"][str(d)] = rec
    return out, None


def measure(per, syms, seeds=SEEDS, d_grid=D_GRID, n_grid=N_GRID):
    dates, _ = e254.era_grid(per, syms)
    star, star_source = e254.whole_era_star(per, syms)
    out = {"era_grid": {"sessions": len(dates), "first": dates[0] if dates else None,
                        "last": dates[-1] if dates else None},
           "pinned_star": star, "pinned_star_source": star_source,
           "seeds": seeds, "draw_grid": list(d_grid), "rungs": [], "rungs_missing": []}
    for family in FAMILIES:
        for n in n_grid:
            if n > len(dates) or n < e254.N_MIN:
                out["rungs_missing"].append({"family": family, "n_requested": n,
                                             "reason": "outside the ladder"})
                continue
            lo, hi = e254.window_for(family, dates, n)
            r, why = measure_window(per, syms, lo, hi, star, seeds=seeds, d_grid=d_grid)
            if r is None:
                out["rungs_missing"].append({"family": family, "n_requested": n,
                                             "window": [lo, hi], "reason": why})
                continue
            r["family"] = family
            r["n_requested"] = n
            out["rungs"].append(r)
    return out


def build_tables(m):
    """Per family and draw count: the ladder, gamma, r2, and the two scatter sources."""
    tables = {}
    for family in FAMILIES:
        rungs = sorted([r for r in m["rungs"] if r["family"] == family],
                       key=lambda r: r["sessions"])
        rows = []
        for d in m["draw_grid"]:
            edge_pts, per_seed_edge = [], {}
            for r in rungs:
                rec = (r["by_draws"] or {}).get(str(d)) or {}
                e = rec.get("edge_self")
                if e:
                    edge_pts.append((r["sessions"], e))
                per_seed = rec.get("edge_self_per_seed") or []
                for k, v in enumerate(per_seed):
                    if v:
                        per_seed_edge.setdefault(k, []).append((r["sessions"], v))
            fit = fit_ladder(edge_pts)
            seed_gammas = [fit_ladder(pts)["gamma"] for pts in per_seed_edge.values()]
            row = {"draws": d, "rungs": len(edge_pts),
                   "gamma": fit["gamma"], "r2": fit["r2"], "gamma_se": fit["gamma_se"],
                   "resid_sd": fit["resid_sd"],
                   "gamma_sd_seed": stdev(seed_gammas),
                   "gamma_per_seed": seed_gammas,
                   "edge_lo": min((p[1] for p in edge_pts), default=None),
                   "edge_hi": max((p[1] for p in edge_pts), default=None)}
            rows.append(row)
        tables[family] = {"rows": rows,
                          "draws_needed": draws_needed(rows),
                          "extrapolation": extrapolate_draws(rows),
                          "gamma_at_main": (rows[0].get("gamma") if rows else None),
                          "r2_at_main": (rows[0].get("r2") if rows else None)}
    return tables


def _summary(face):
    tables = face["tables"]
    s = {"verdict": face["verdict"], "verdict_reason": face["verdict_reason"],
         "era_sessions": face["era"]["sessions"],
         "gamma_by_draws": {k: {str(r["draws"]): r["gamma"] for r in tables[k]["rows"]}
                            for k in FAMILIES},
         "r2_by_draws": {k: {str(r["draws"]): r["r2"] for r in tables[k]["rows"]}
                         for k in FAMILIES},
         "seed_scatter_by_draws": {k: {str(r["draws"]): r["gamma_sd_seed"]
                                       for r in tables[k]["rows"]} for k in FAMILIES},
         "fit_scatter_by_draws": {k: {str(r["draws"]): r["gamma_se"]
                                      for r in tables[k]["rows"]} for k in FAMILIES},
         "mc_over_fit": {k: (lambda last: (None if (last.get("gamma_sd_seed") is None
                                                    or not last.get("gamma_se"))
                                           else last["gamma_sd_seed"] / last["gamma_se"]))
                            (sorted(tables[k]["rows"], key=lambda r: r["draws"])[-1])
                         for k in FAMILIES},
         "draws_needed": {k: tables[k]["draws_needed"] for k in FAMILIES},
         "extrapolation": {k: tables[k]["extrapolation"] for k in FAMILIES},
         "r2_floor": R2_FLOOR, "mc_fraction_floor": MC_FRACTION_FLOOR,
         "rungs": {k: len([r for r in face["rungs"] if r["family"] == k]) for k in FAMILIES},
         "rungs_missing": len(face.get("rungs_missing") or []),
         "pinned_star": face.get("pinned_star"),
         "secondary_reads": face.get("secondary_reads")}
    return s


def run(per=None, save=True, outdir=None, seeds=SEEDS, d_grid=D_GRID, n_grid=N_GRID, tag=""):
    per = per if per is not None else e239.panels()
    syms = [s for s in e252.BASKET if per.get(s)]
    m = measure(per, syms, seeds=seeds, d_grid=d_grid, n_grid=n_grid)
    tables = build_tables(m)
    verdict, why = verdict_from(tables)
    # secondary reads, both DERIVED from the converged (largest-draw) ladder:
    #  - E254's own frozen rule applied to it, which says whether its "undetermined" was a
    #    straightness problem or a family-split problem;
    #  - the gap between the two families' gamma, which a straddling pair must publish.
    converged = {}
    for k in FAMILIES:
        rows = sorted(tables[k]["rows"], key=lambda r: r["draws"])
        converged[k] = rows[-1] if rows else {}
    e254_verdict, e254_why = e254.verdict_from(
        {k: converged[k].get("gamma") for k in FAMILIES},
        {k: converged[k].get("r2") for k in FAMILIES})
    g_head, g_tail = converged.get("head", {}).get("gamma"), converged.get("tail", {}).get("gamma")
    secondary = {"e254_verdict_at_converged_draws": e254_verdict,
                 "e254_reason_at_converged_draws": e254_why,
                 "converged_draws": max(D_GRID),
                 "gamma_head": g_head, "gamma_tail": g_tail,
                 "family_gamma_gap": (None if (g_head is None or g_tail is None)
                                      else abs(g_head - g_tail)),
                 "gamma_tol": GAMMA_TOL}
    # E253's inversion, re-run at each family's converged exponent and its own 408-session edge:
    # the deliverable there was a RANGE, and this says how wide the exponent alone makes it.
    pub = e254.read_published()
    targets = {}
    for k in FAMILIES:
        rows = [r for r in m["rungs"] if r["family"] == k]
        big = max(rows, key=lambda r: r["sessions"]) if rows else None
        edge = (((big or {}).get("by_draws") or {}).get(str(max(D_GRID))) or {}).get("edge_self")
        g = converged[k].get("gamma")
        if not big or not edge or g is None or not pub.get("b_self"):
            targets[k] = None
            continue
        targets[k] = e253.needed_sessions(big["sessions"], pub["b_self"], edge, g)
    secondary["target_sessions_at_converged_gamma"] = targets
    secondary["target_b_self"] = pub.get("b_self")
    secondary["target_sessions_available"] = (m["era_grid"] or {}).get("sessions")
    # CONVERGENCE of the endpoint itself: the band's lo is a 5% quantile, and a quantile read off
    # too few draws sits INSIDE the true boundary. So the question is not only "is the ladder
    # straight" but "has the endpoint stopped moving" -- every rung's rise from 240 to 480 is
    # published, and the family is called converged only if no rung moves more than CONV_PCT.
    conv = {}
    for k in FAMILIES:
        rows = sorted([r for r in m["rungs"] if r["family"] == k],
                      key=lambda r: r["sessions"])
        rises = []
        for r in rows:
            bd = r.get("by_draws") or {}
            lo_e = (bd.get("240") or {}).get("edge_self")
            hi_e = (bd.get(str(max(D_GRID))) or {}).get("edge_self")
            if lo_e and hi_e:
                rises.append({"n": r["sessions"], "edge_240": lo_e, "edge_last": hi_e,
                              "rise_pct": 100.0 * (hi_e - lo_e) / lo_e})
        total = [({"n": r["sessions"],
                   "rise_pct": 100.0 * ((((r.get("by_draws") or {}).get(str(max(D_GRID))) or {})
                                         .get("edge_self") or 0.0)
                                        - (((r.get("by_draws") or {}).get("60") or {})
                                           .get("edge_self") or 0.0))
                   / ((((r.get("by_draws") or {}).get("60") or {}).get("edge_self") or 1.0))})
                 for r in rows]
        conv[k] = {"rungs": len(rises), "rises_240_to_last": rises,
                   "median_rise_pct": median([x["rise_pct"] for x in rises]),
                   "min_rise_pct": min([x["rise_pct"] for x in rises], default=None),
                   "rungs_that_rose": sum(1 for x in rises if x["rise_pct"] > 0),
                   "median_rise_pct_vs_60": median([x["rise_pct"] for x in total]),
                   "endpoint_converged": bool(rises) and all(
                       x["rise_pct"] <= CONV_PCT for x in rises)}
        conv[k]["verdict_note"] = ("endpoint still moving: the 5% quantile under-reads the "
                                   "boundary at small draw counts"
                                   if not conv[k]["endpoint_converged"]
                                   else "no rung moved more than %.1f%% from 240 to %d draws"
                                        % (CONV_PCT, max(D_GRID)))
    secondary["endpoint_convergence"] = conv
    secondary["caveats"] = [
        "the seed scatter is a 2-degree-of-freedom estimate (3 seeds) and it did NOT fall with "
        "more draws, so mc_over_fit is published as a flag, not as a precise ratio",
        "draw counts above %d were not measured" % max(D_GRID),
        "the two families are different experiments (fixed start vs fixed end), so a gamma gap "
        "is a statement that the ladder is not one object, not a measurement error",
        "target_sessions_at_converged_gamma is a FLOOR while endpoint_converged is false: the "
        "endpoint is still rising with draws, and a larger edge asks for more sessions"]
    face = {"study": STUDY,
            "title": "is the undetermined band exponent starved of draws or of rungs?",
            "generated": datetime.now().isoformat(timespec="seconds"),
            "evidence_cutoff": (m["era_grid"] or {}).get("last") or "unknown",
            "frozen_spec": {"era": [ERA_LO, ERA_HI], "cell_label": CELL_LABEL,
                            "n_grid": list(n_grid), "draw_grid": list(d_grid),
                            "n_min": e254.N_MIN, "seeds": seeds, "base_seed": BASE_SEED,
                            "families": list(FAMILIES), "r2_floor": R2_FLOOR,
                            "gamma_tol": GAMMA_TOL, "frozen_gamma": FROZEN_GAMMA,
                            "mc_fraction_floor": MC_FRACTION_FLOOR,
                            "draw_budget": D_BUDGET,
                            "verdict_vocabulary": list(VERDICTS),
                            "prefix_nesting": ("one draw stream at max(draw_grid) per seed; every "
                                               "smaller draw count reads its own PREFIX, so the "
                                               "four ladders are one experiment read four ways"),
                            "what_is_not_done": ["no coefficient is re-priced: only the shuffled "
                                                 "band is rebuilt",
                                                 "no bootstrap, no bill, no adoption",
                                                 "the rung set is identical at every draw count"]},
            "era": m["era_grid"], "pinned_star": m.get("pinned_star"),
            "pinned_star_source": m.get("pinned_star_source"),
            "rungs": m["rungs"], "rungs_missing": m["rungs_missing"],
            "tables": tables,
            "verdict": verdict, "verdict_reason": why,
            "secondary_reads": secondary,
            "verdict_inputs": {"draws_needed": {k: tables[k]["draws_needed"] for k in FAMILIES},
                               "r2_floor": R2_FLOOR,
                               "mc_fraction_floor": MC_FRACTION_FLOOR}}
    face["summary"] = _summary(face)
    if save:
        face["written"] = _write(face, outdir or OUTDIR, tag)
    return face


def _write(face, outdir, tag=""):
    """Write the face. `tag` names a VARIANT (e.g. a longer draw grid) so a re-read can never
    overwrite the base face -- r1135's pit: a variant run whose filename does not carry the
    variant key silently replaces the base face and the next reader quotes the wrong ladder.
    """
    os.makedirs(outdir, exist_ok=True)
    cutoff = face.get("evidence_cutoff") or "unknown"
    path = os.path.join(outdir, "BANDDRAW-%s%s.json" % (cutoff, tag))
    latest = os.path.join(outdir, "banddraw%s_latest.json" % tag)
    body = json.dumps(face, indent=1, sort_keys=True, ensure_ascii=False)
    for p in (path, latest):
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")
    return {"face": os.path.relpath(path, ROOT), "latest": os.path.relpath(latest, ROOT),
            "bytes": len(body)}


def _r(v, n=4):
    return None if v is None else round(float(v), n)


def _fmt(face):
    s = face["summary"]
    return ("%s | verdict %s (%s) | r2 by draws head %s tail %s | gamma head %s tail %s | "
            "mc/fit head %s tail %s | draws needed %s"
            % (face["study"], s["verdict"], s["verdict_reason"],
               {k: _r(v, 3) for k, v in s["r2_by_draws"]["head"].items()},
               {k: _r(v, 3) for k, v in s["r2_by_draws"]["tail"].items()},
               {k: _r(v, 4) for k, v in s["gamma_by_draws"]["head"].items()},
               {k: _r(v, 4) for k, v in s["gamma_by_draws"]["tail"].items()},
               _r(s["mc_over_fit"].get("head"), 3),
               _r(s["mc_over_fit"].get("tail"), 3),
               s["draws_needed"]))


def verify(outdir=None):
    """Re-read the face and recompute every published number from its own ladder."""
    outdir = outdir or OUTDIR
    problems = []
    latest = os.path.join(outdir, "banddraw_latest.json")
    if not os.path.exists(latest):
        return {"ok": False, "problems": ["no face at %s" % latest]}
    with open(latest, encoding="utf-8") as fh:
        face = json.load(fh)
    tables = face.get("tables") or {}
    for k in FAMILIES:
        if k not in tables:
            problems.append("family %s missing" % k)
            continue
        rows = tables[k].get("rows") or []
        if len(rows) < 3:
            problems.append("family %s has %d draw counts (need >=3)" % (k, len(rows)))
        rungs = sorted([r for r in face.get("rungs") or [] if r.get("family") == k],
                       key=lambda r: r["sessions"])
        for row in rows:
            pts = []
            for r in rungs:
                e = ((r.get("by_draws") or {}).get(str(row["draws"])) or {}).get("edge_self")
                if e:
                    pts.append((r["sessions"], e))
            refit = fit_ladder(pts)
            if refit["gamma"] is None or row.get("gamma") is None:
                problems.append("family %s draws=%s has no gamma" % (k, row["draws"]))
                continue
            if abs(refit["gamma"] - row["gamma"]) > 1e-9:
                problems.append("family %s draws=%s gamma does not reproduce (%s vs %s)"
                                % (k, row["draws"], refit["gamma"], row["gamma"]))
            if row.get("r2") is not None and abs(refit["r2"] - row["r2"]) > 1e-9:
                problems.append("family %s draws=%s r2 does not reproduce" % (k, row["draws"]))
    want, _why = verdict_from(tables)
    if face.get("verdict") != want:
        problems.append("verdict %s != recomputed %s" % (face.get("verdict"), want))
    # the secondary read is a derived sentence: recompute it from the converged ladder
    converged = {}
    for k in FAMILIES:
        rows = sorted((tables.get(k) or {}).get("rows") or [], key=lambda r: r["draws"])
        converged[k] = rows[-1] if rows else {}
    sec_verdict, _sec_why = e254.verdict_from(
        {k: converged[k].get("gamma") for k in FAMILIES},
        {k: converged[k].get("r2") for k in FAMILIES})
    pub_sec = (face.get("secondary_reads") or {}).get("e254_verdict_at_converged_draws")
    if pub_sec != sec_verdict:
        problems.append("secondary e254 verdict %s != recomputed %s" % (pub_sec, sec_verdict))
    if not face.get("evidence_cutoff"):
        problems.append("evidence_cutoff missing")
    # the rung SET must be identical at every draw count (the experiment's premise)
    for k in FAMILIES:
        seen = {}
        for r in face.get("rungs") or []:
            if r.get("family") != k:
                continue
            keys = sorted((r.get("by_draws") or {}).keys())
            seen[str(keys)] = seen.get(str(keys), 0) + 1
        if len(seen) > 1:
            problems.append("family %s does not carry the same draw grid at every rung" % k)
    return {"ok": not problems, "problems": problems, "verdict": face.get("verdict"),
            "draws": len(face.get("frozen_spec", {}).get("draw_grid") or []),
            "rungs": len(face.get("rungs") or [])}


# ---------------------------------------------------------------- selftest fixtures
def leg(ok, name, detail=None):
    return {"leg": name, "pass": bool(ok), "detail": detail}


def _fake_stream(truth, draws, noise, seed):
    """A nesting fixture: draw i gets a deterministic 'coefficient' around a truth."""
    rng = random.Random(seed)
    return [truth + noise * rng.gauss(0, 1) for _ in range(draws)]


def selftest():
    legs = []
    # 1 prefix nesting: the prefix of a max-length stream IS the short-count stream
    full = _fake_stream(-0.55, 480, 0.05, 7)
    short = _fake_stream(-0.55, 60, 0.05, 7)
    legs.append(leg(full[:60] == short,
                    "a 480-draw stream's first 60 equal the 60-draw stream of the same seed",
                    {"max_abs_diff": max(abs(a - b) for a, b in zip(full[:60], short))}))
    # 2 the quantile endpoint converges: the 60-draw and 480-draw edges sit close together
    e60, e480 = prefix_edge(full, 60), prefix_edge(full, 480)
    legs.append(leg(e60 is not None and e480 is not None and abs(e60 - e480) < 0.12,
                    "the prefix edge is a stable statistic, not a one-draw accident",
                    {"edge60": e60, "edge480": e480}))
    # 3 threshold: fewer than 20 kept draws yields None rather than a fake band
    legs.append(leg(prefix_edge(full[:10], 60) is None and prefix_edge([], 60) is None,
                    "a stream shorter than the band's floor yields None"))
    # 4 ladder arithmetic: an exact n**-0.5 ladder fits gamma 0.5 with r2 1
    sq = [(100, 5.0), (200, 5.0 / math.sqrt(2)), (400, 2.5)]
    f = fit_ladder(sq)
    legs.append(leg(abs(f["gamma"] - 0.5) < 1e-9 and abs(f["r2"] - 1.0) < 1e-9,
                    "an exact 1/sqrt(n) ladder fits gamma 0.5, r2 1", f))
    # 5 a uniform scale change leaves gamma and r2 alone (no draw count may move them)
    f2 = fit_ladder([(n, 3.0 * e) for n, e in sq])
    legs.append(leg(abs(f2["gamma"] - f["gamma"]) < 1e-9
                    and abs(f2["r2"] - f["r2"]) < 1e-9,
                    "uniform rescaling moves neither gamma nor r2", {"a": f, "b": f2}))
    # 6 noise floor: gamma_se is finite and smaller when the ladder is exactly straight
    noisy = [(n, e * (1.0 + 0.06 * ((-1) ** i))) for i, (n, e) in enumerate(sq)]
    fn = fit_ladder(noisy)
    legs.append(leg(f["gamma_se"] is not None and fn["gamma_se"] is not None
                    and fn["gamma_se"] > f["gamma_se"],
                    "the slope SE is zero-to-small on a straight ladder and larger on a bent one",
                    {"straight": f["gamma_se"], "bent": fn["gamma_se"]}))
    # 7 draws_needed reads the table, and none is reported as None rather than as zero draws
    legs.append(leg(draws_needed([{"draws": 60, "r2": 0.5}, {"draws": 120, "r2": 0.85}]) == 120
                    and draws_needed([{"draws": 60, "r2": 0.5}]) is None,
                    "draws_needed returns the first clearing count or None"))
    # 8 extrapolation refuses a flat/falling trend (the honest 'more draws will not help')
    flat = [{"draws": 60, "r2": 0.60}, {"draws": 240, "r2": 0.60}]
    ex = extrapolate_draws(flat)
    legs.append(leg(ex["reaches_floor"] is False and ex["draws"] is None,
                    "a flat r2 trend extrapolates to 'no draw count helps'", ex))
    # 9 extrapolation reaches on a 1/D trend inside the budget
    trend = [{"draws": 60, "r2": 0.50}, {"draws": 240, "r2": 0.75}]
    ex2 = extrapolate_draws(trend)
    legs.append(leg(ex2["reaches_floor"] is True and 240 < (ex2["draws"] or 0) <= D_BUDGET,
                    "a 1/D trend extrapolates to a concrete draw count inside the budget", ex2))
    # 10 the budget closes the extrapolation line when it lands outside
    ex3 = extrapolate_draws([{"draws": 60, "r2": 0.10}, {"draws": 480, "r2": 0.12}])
    legs.append(leg(ex3["reaches_floor"] is False,
                    "an extrapolation beyond the budget is refused, not published as a number",
                    ex3))
    # 11 verdict vocabulary: all four branches reachable on synthetic tables
    def _table(r2s, mc, se):
        return {"rows": [{"draws": d, "r2": r2s[d], "gamma_sd_seed": mc, "gamma_se": se}
                         for d in sorted(r2s)]}
    v = {}
    v["clears"] = verdict_from({"head": _table({60: 0.9, 480: 0.9}, 0.01, 0.1),
                               "tail": _table({60: 0.9, 480: 0.9}, 0.01, 0.1)})[0]
    v["rungs"] = verdict_from({"head": _table({60: 0.6, 480: 0.65}, 0.01, 0.1),
                              "tail": _table({60: 0.5, 480: 0.62}, 0.02, 0.1)})[0]
    v["draws"] = verdict_from({"head": _table({60: 0.6, 480: 0.65}, 0.30, 0.1),
                              "tail": _table({60: 0.5, 480: 0.62}, 0.30, 0.1)})[0]
    v["missing"] = verdict_from({"head": _table({60: 0.6, 480: 0.65}, 0.01, 0.0),
                                "tail": _table({60: 0.5, 480: 0.62}, 0.01, 0.1)})[0]
    legs.append(leg(v["clears"] == "exponent_clears_on_draws_alone"
                    and v["rungs"] == "rungs_are_the_constraint"
                    and v["draws"] == "draws_are_the_constraint"
                    and v["missing"] == "undetermined",
                    "the frozen verdict splits clear/rungs/draws/undetermined", v))
    # 12 mc/fit is the ratio of the two scatter sources (a published number, so pin the arithmetic)
    t = _table({480: 0.5}, 0.02, 0.08)
    ratio = t["rows"][-1]["gamma_sd_seed"] / t["rows"][-1]["gamma_se"]
    legs.append(leg(abs(ratio - 0.25) < 1e-12,
                    "mc_over_fit is seed scatter divided by fit scatter", {"ratio": ratio}))
    # 13 stdev/median refuse singletons instead of inventing a spread
    legs.append(leg(stdev([1.0]) is None and stdev([1.0, 3.0]) == math.sqrt(2.0)
                    and median([None, 2.0]) == 2.0,
                    "stdev of one value is None and median drops Nones"))
    # 14 half-width and edge come from the same prefix band (two readings, one sample)
    legs.append(leg(prefix_half(full, 480) is not None and prefix_edge(full, 480) is not None,
                    "both readings are computable on the same nested prefix"))
    # 15 the secondary read really is E254's rule: a straddling pair is undetermined even when
    #    both ladders are perfectly straight, so 'straight' must never be published as 'settled'
    sec = e254.verdict_from({"head": 0.32, "tail": 0.59}, {"head": 0.95, "tail": 0.95})
    legs.append(leg(sec[0] == "exponent_undetermined_inside_the_cell",
                    "a straight ladder with a family split is still undetermined under E254's rule",
                    sec))
    passed = sum(1 for x in legs if x["pass"])
    return {"legs": legs, "passed": passed, "total": len(legs), "ok": passed == len(legs)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", nargs="?", default="run", choices=("run", "selftest", "verify"))
    ap.add_argument("--seeds", type=int, default=SEEDS)
    ap.add_argument("--draws", type=int, default=0,
                    help="override the draw grid's top (single-value grid when given)")
    ap.add_argument("--tag", default="",
                    help="suffix for the face filename, so a variant never overwrites the base")
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
        print("verify: rungs=%s verdict=%s -> %s"
              % (r.get("rungs"), r.get("verdict"), "OK" if r["ok"] else "FAIL"))
        return 0 if r["ok"] else 1
    grid = D_GRID if not args.draws else (args.draws,)
    face = run(seeds=args.seeds, d_grid=grid, tag=args.tag)
    print(_fmt(face))
    print("written: %s" % (face.get("written") or {}).get("face"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())