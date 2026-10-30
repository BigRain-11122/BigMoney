#!/usr/bin/env python3
"""E257 -- which published band verdicts change when the band is taken at the top draw count?

The E254/E255/E256 chain established one uncomfortable fact about the shuffled band: its 5%
endpoint is still rising with the permutation draw count at 1920 draws and does not decay, so a
quantile read off a small grid sits INSIDE the true boundary. Every published "outside the band"
verdict in the star family was, however, judged against an edge measured at a few hundred draws.

This face does no new estimation and reads no panel. It takes the band ladder that E256 already
measured (six draw counts, seven session rungs, two families, per-rung edge_self) and asks a single
bookkeeping question of the published faces:

    for each published (coefficient, band) pair, the band is WIDENED by the measured draw
    multiplier edge(top)/edge(published draws); which "outside" verdicts survive, which flip to
    "inside", and which flip only for some rungs or families?

Three design decisions make the answer honest rather than decorative:

  1. THE MULTIPLIER IS A RANGE, NOT A NUMBER. E256 measured the ladder inside era_2025_now in two
     families (head = first n sessions, tail = last n). A published cell is a fixed window, which
     is neither of those. So a cell is re-judged at EVERY multiplier in the 2 families x 7 rungs
     product, and the verdict is "flips" only when it flips at all of them, "survives" only when it
     survives all of them, and "flips_depends_on_measurement" otherwise. No family is nominated as
     the right analogue of a fixed window.
  2. THE PUBLISHED FLAG MUST REPRODUCE FIRST. Before a row is re-judged, its published
     outside/inside flag is recomputed from its own published band; a row whose flag does not
     reproduce from its own numbers is published as `published_flag_not_reproduced` and counted
     separately, never silently re-judged.
  3. THE BAND IS ASYMMETRIC. The multiplier scales both edges, so the published asymmetry survives;
     the comparison stays the published rule (val < lo or val > hi).

NO BILL, NO ADOPTION, NO RE-PRICING, NO PANEL: this is arithmetic on published faces.
"""

from __future__ import annotations

import argparse
import io
import json
import math
import os
import statistics
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

STUDY = "E257_band_at_top_flips"
CUTOFF = "2026-10-29"

FACES = {
    "ladder": "BANDDRAW-2026-10-29-d1920.json",
    "starself": "STARSELF-2026-10-29.json",
    "starown": "STAROWN-2026-10-29.json",
}

DEFAULT_BASE_DRAWS = 200
FAMILIES = ("head", "tail")

VERDICT_VOCAB = (
    "some_published_band_verdicts_flip_at_top_draws",
    "flips_depend_on_the_measurement_only",
    "every_published_band_verdict_survives_top_draws",
    "no_rows_measured",
)

NO_BILL = ("bookkeeping only: every coefficient and band is taken verbatim from a published face; "
           "no re-estimation, no panel read, no adoption, no member billed")


# ------------------------------------------------------------------ io helpers
def _p(name):
    return os.path.join(OUTDIR, name)


def load(name):
    with io.open(_p(name), encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------ the ladder
def ladder_curves(face):
    """{(family, sessions): [(draws, edge_self), ...sorted]} from the E256 rung table."""
    out = {}
    for r in (face.get("rungs") or []):
        fam = r.get("family")
        n = r.get("sessions")
        series = []
        for d, cell in ((r.get("by_draws") or {}).items()):
            e = (cell or {}).get("edge_self")
            if e is not None:
                series.append((int(d), float(e)))
        if series and fam in FAMILIES and n:
            out[(fam, int(n))] = sorted(series)
    return out


def edge_at(series, draws):
    """Log-log interpolation of a rising edge curve; endpoints clamped, never extrapolated."""
    if not series:
        return None
    if draws <= series[0][0]:
        return series[0][1]
    if draws >= series[-1][0]:
        return series[-1][1]
    for i in range(1, len(series)):
        d0, e0 = series[i - 1]
        d1, e1 = series[i]
        if d0 <= draws <= d1:
            if d1 == d0 or e0 <= 0 or e1 <= 0:
                return e0
            w = (math.log(draws) - math.log(d0)) / (math.log(d1) - math.log(d0))
            return e0 * (e1 / e0) ** w
    return series[-1][1]


def multiplier_table(curves, base_draws, top_draws):
    """{(family, rung): edge(top)/edge(base)} plus the range over the whole product."""
    rows, vals = [], []
    for (fam, n), series in sorted(curves.items()):
        e_base = edge_at(series, base_draws)
        e_top = edge_at(series, top_draws)
        if not e_base or e_top is None:
            continue
        m = e_top / e_base
        rows.append({"family": fam, "sessions": n, "edge_at_base": e_base,
                     "edge_at_top": e_top, "multiplier": m})
        vals.append(m)
    return {"rows": rows, "base_draws": base_draws, "top_draws": top_draws,
            "multiplier_min": min(vals) if vals else None,
            "multiplier_max": max(vals) if vals else None,
            "multiplier_median": statistics.median(vals) if vals else None,
            "rung_index": [[fam, n] for (fam, n) in sorted(curves)]}


def outside(val, lo, hi):
    if val is None or lo is None or hi is None:
        return None
    return bool(val < lo or val > hi)


def scale_band(lo, hi, m):
    return (lo * m, hi * m)


# ------------------------------------------------------------------ rows
def _resolver(*candidates):
    for path, val in candidates:
        if val is not None:
            return path, val
    return None, None


def starself_rows(face):
    rows = []
    for cell in (face.get("cells") or []):
        label = cell.get("label")
        n = cell.get("sessions")
        for row in ("self", "cross"):
            bandw = cell.get("band_" + row) or {}
            band = bandw.get("band") or {}
            flag = cell.get("%s_outside_band" % row)
            rowdict = cell.get("%s_row" % row) or {}
            src, b = _resolver(
                ("%s_row.b_%s" % (row, row), rowdict.get("b_" + row)),
                ("%s_row.b" % row, rowdict.get("b")),
                ("cell.b_%s" % row, cell.get("b_" + row)),
            )
            rows.append({
                "source": "E252:STARSELF",
                "cell": label,
                "row": row,
                "sessions": n,
                "b": b,
                "b_source": src,
                "band_lo": band.get("lo"),
                "band_hi": band.get("hi"),
                "band_draws": band.get("draws") or bandw.get("draws_used"),
                "published_outside": flag,
            })
    return rows


def starown_rows(face):
    """E251 publishes one band-bearing value per cell it can read: the star's own lag-1 residual
    (star_residual.b1) against its own time-shuffle band. The vol/age 'additions' are published as
    DROPS, not as coefficients that sit on a band line, so they are not re-judged here."""
    rows = []
    for cell in (face.get("cells") or []):
        bandw = cell.get("band_star_lag1") or {}
        band = bandw.get("band") or {}
        res = cell.get("star_residual") or {}
        b = res.get("b1")
        if band and b is not None:
            rows.append({
                "source": "E251:STAROWN",
                "cell": cell.get("label"),
                "row": "star_lag1_residual",
                "sessions": cell.get("sessions"),
                "b": b,
                "b_source": "star_residual.b1",
                "band_lo": band.get("lo"),
                "band_hi": band.get("hi"),
                "band_draws": band.get("draws") or bandw.get("draws_used"),
                "published_outside": cell.get("star_outside_band"),
            })
    return rows


def rejudge(rows, table, curves, base_default=DEFAULT_BASE_DRAWS):
    out = []
    for r in rows:
        rec = dict(r)
        lo, hi, b = r.get("band_lo"), r.get("band_hi"), r.get("b")
        if b is None or lo is None or hi is None:
            rec.update({"verdict": "unjudgeable", "reason": "row carries no coefficient or no band"})
            out.append(rec)
            continue
        pub = outside(b, lo, hi)
        rec["outside_at_published"] = pub
        rec["edge_published"] = max(abs(lo), abs(hi))
        if r.get("published_outside") is not None and pub != bool(r["published_outside"]):
            rec.update({"verdict": "published_flag_not_reproduced",
                        "reason": "recomputed flag %r != published %r"
                                  % (pub, r["published_outside"])})
            out.append(rec)
            continue
        base = float(r.get("band_draws") or base_default)
        n = r.get("sessions")
        ms = []
        for (fam, rung), series in sorted(curves.items()):
            e_base = edge_at(series, base)
            e_top = edge_at(series, table["top_draws"])
            if e_base and e_top:
                ms.append(e_top / e_base)
        if not ms:
            rec.update({"verdict": "unjudgeable", "reason": "ladder carries no multiplier"})
            out.append(rec)
            continue
        outs = [outside(b, *scale_band(lo, hi, m)) for m in ms]
        margins_top = [abs(b) / (max(abs(lo * m), abs(hi * m))) for m in ms]
        m_med = statistics.median(ms)
        lo_t, hi_t = scale_band(lo, hi, m_med)
        rec.update({
            "multiplier_median": m_med,
            "multiplier_min": min(ms),
            "multiplier_max": max(ms),
            "multiplier_draws_base": base,
            "multiplier_draws_top": table["top_draws"],
            "band_at_top_median": [lo_t, hi_t],
            "edge_at_top_median": max(abs(lo_t), abs(hi_t)),
            "outside_at_top_all_measurements": all(outs),
            "outside_at_top_any_measurement": any(outs),
            "flips_on_any_measurement": any(o != pub for o in outs),
            "flips_on_every_measurement": all(o != pub for o in outs),
            "margin_published": abs(b) / max(abs(lo), abs(hi)),
            "margin_at_top_median": statistics.median(margins_top),
            "distance_in_margins_at_top_median": statistics.median(margins_top) - 1.0,
            "rung_in_ladder": any(n == rung for (_f, rung) in curves),
        })
        if rec["flips_on_every_measurement"]:
            rec["verdict"] = "flips_at_top_draws"
        elif rec["flips_on_any_measurement"]:
            rec["verdict"] = "flips_depends_on_measurement"
        elif pub:
            rec["verdict"] = "survives_outside"
        else:
            rec["verdict"] = "stays_inside"
        out.append(rec)
    return out


# ------------------------------------------------------------------ ladder verdicts
def loglog_fit(points):
    """points = [(n, edge)] -> (gamma, r2) with edge = c * n**(-gamma)."""
    pts = [(float(n), float(e)) for n, e in points if n and e and e > 0]
    if len(pts) < 2:
        return None, None
    xs = [math.log(n) for n, _ in pts]
    ys = [math.log(e) for _, e in pts]
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return None, None
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    intercept = my - slope * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (intercept + slope * x)) ** 2 for x, y in zip(xs, ys))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else None
    return -slope, r2


def family_fit_at(curves, family, draws):
    pts = []
    for (fam, n), series in curves.items():
        if fam != family:
            continue
        e = edge_at(series, draws)
        if e:
            pts.append((n, e))
    return loglog_fit(pts)


def draws_needed_for_floor(curves, grid, floor):
    """Smallest draw count at which every family's r2 clears the floor (E255's question)."""
    for d in sorted(grid):
        ok = True
        for fam in FAMILIES:
            _g, r2 = family_fit_at(curves, fam, d)
            if r2 is None or r2 < floor:
                ok = False
                break
        if ok:
            return d
    return None


def e254_rule(gamma_h, gamma_t, r2_h, r2_t, gamma_tol, r2_floor):
    reasons = []
    if r2_h is None or r2_t is None:
        reasons.append("r2_not_measurable")
    else:
        if r2_h < r2_floor:
            reasons.append("r2_below_floor_head")
        if r2_t < r2_floor:
            reasons.append("r2_below_floor_tail")
    gap = None
    if gamma_h is not None and gamma_t is not None:
        gap = abs(gamma_h - gamma_t)
        if gap > gamma_tol:
            reasons.append("family_gap_exceeds_tolerance")
    return ("determined" if not reasons else "undetermined"), reasons, gap


def ladder_verdicts(ladder, curves):
    spec = ladder.get("frozen_spec") or {}
    grid = sorted(int(d) for d in (spec.get("draw_grid") or []))
    gamma_tol = float(spec.get("gamma_tol") or 0.1)
    r2_floor = float(spec.get("r2_floor") or 0.8)
    top = grid[-1] if grid else None
    out = {"gamma_tol": gamma_tol, "r2_floor": r2_floor, "draw_grid": grid, "top_draws": top}
    fits = {}
    for fam in FAMILIES:
        g, r2 = family_fit_at(curves, fam, top)
        fits[fam] = {"gamma": g, "r2": r2}
    out["fit_at_top_draws"] = fits
    if top is None or any(fits[f]["gamma"] is None for f in FAMILIES):
        out["e254"] = {"rejudged": "undetermined", "reasons": ["ladder_not_measurable"]}
        out["e255"] = {"draws_needed": None, "rejudged": "not_measurable"}
        return out
    gh, rt = fits["head"]["gamma"], fits["tail"]["gamma"]
    rh, rr = fits["head"]["r2"], fits["tail"]["r2"]
    verdict, reasons, gap = e254_rule(gh, rt, rh, rr, gamma_tol, r2_floor)
    out["e254"] = {
        "published": "exponent_undetermined_inside_the_cell",
        "published_reason": "r2 below floor in at least one family (at 60 draws)",
        "at_top_draws": verdict,
        "reasons": reasons,
        "family_gap": gap,
        "survives_published_verdict": verdict == "undetermined",
        "note": ("the r2 floor now clears in both families, so the reason moved from the fit to the "
                 "straddle" if verdict == "undetermined" and "r2_below_floor_head" not in reasons
                 and "r2_below_floor_tail" not in reasons else ""),
    }
    dn = draws_needed_for_floor(curves, grid, r2_floor)
    out["e255"] = {
        "question": "is the undetermined exponent starved of draws or of rungs?",
        "draws_needed_for_both_families": dn,
        "rejudged": ("draw_starvation_confirmed" if dn is not None and dn <= top
                     else "no_draw_count_in_the_grid_clears_the_floor"),
        "converged_grid_point_published_by_e255": 480,
    }
    out["e256"] = {
        "published": (ladder.get("verdict")),
        "rejudged": "unchanged",
        "note": ("E256's verdict is about the DRAW axis itself (does the increment per doubling "
                 "decay); taking the top draws does not re-judge it, it is the input to this face."),
    }
    return out


# ------------------------------------------------------------------ verdict
def verdict_from(rows, lad):
    if not rows:
        return "no_rows_measured", "no published row carried a coefficient with a band"
    flips = [r for r in rows if r.get("verdict") == "flips_at_top_draws"]
    dep = [r for r in rows if r.get("verdict") == "flips_depends_on_measurement"]
    surv = [r for r in rows if r.get("verdict") == "survives_outside"]
    e254_v = ((lad or {}).get("e254") or {}).get("at_top_draws")
    if flips:
        return ("some_published_band_verdicts_flip_at_top_draws",
                "%d row(s) flip at every measured multiplier, %d only for some, %d survive; "
                "E254 at top draws reads %s" % (len(flips), len(dep), len(surv), e254_v))
    if dep:
        return ("flips_depend_on_the_measurement_only",
                "no row flips at every multiplier but %d flip for some rung/family combination"
                % len(dep))
    return ("every_published_band_verdict_survives_top_draws",
            "%d published outside-band row(s) stay outside a band widened by every measured "
            "multiplier (%.3f..%.3f)" % (len(surv),
                                         ((lad or {}).get("e257_multipliers") or {})
                                         .get("multiplier_min", 1.0),
                                         ((lad or {}).get("e257_multipliers") or {})
                                         .get("multiplier_max", 1.0)))


# ------------------------------------------------------------------ run
def run(save=True, outdir=None):
    outdir = outdir or OUTDIR
    missing = []
    faces = {}
    for k in ("ladder", "starself", "starown"):
        try:
            faces[k] = load(FACES[k])
        except FileNotFoundError:
            missing.append(k)
    if "ladder" not in faces:
        face = {
            "study": STUDY, "title": "which published verdicts change when the band is taken at "
                                     "the top draw count?",
            "evidence_cutoff": CUTOFF, "generated": datetime.now().isoformat(timespec="seconds"),
            "verdict": "no_rows_measured",
            "verdict_reason": "the E256 top-draw ladder face is absent, so no multiplier exists",
            "faces_missing": missing, "rows": [], "summary": {"rows": 0},
            "frozen_spec": frozen_spec(), "no_bill": NO_BILL,
        }
        if save:
            _write(face, outdir)
        return face

    curves = ladder_curves(faces["ladder"])
    base = DEFAULT_BASE_DRAWS
    table = multiplier_table(curves, base, TOP_OF(faces["ladder"]))
    rows = []
    if "starself" in faces:
        rows += rejudge(starself_rows(faces["starself"]), table, curves)
    if "starown" in faces:
        rows += rejudge(starown_rows(faces["starown"]), table, curves)
    lad = ladder_verdicts(faces["ladder"], curves)
    lad["e257_multipliers"] = {k: table[k] for k in
                               ("multiplier_min", "multiplier_max", "multiplier_median")}
    v, why = verdict_from(rows, lad)
    face = {
        "study": STUDY,
        "title": "which published verdicts change when the band is taken at the top draw count?",
        "evidence_cutoff": CUTOFF,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "frozen_spec": frozen_spec(),
        "source_faces": {k: "results/state_tilt/" + v2 for k, v2 in FACES.items()},
        "faces_missing": missing,
        "multiplier_table": table,
        "ladder_verdicts": lad,
        "rows": rows,
        "verdict": v,
        "verdict_reason": why,
        "no_bill": NO_BILL,
    }
    face["summary"] = _summary(face)
    if save:
        _write(face, outdir)
    return face


def TOP_OF(ladder):
    grid = (ladder.get("frozen_spec") or {}).get("draw_grid") or [60]
    return int(max(int(d) for d in grid))


def frozen_spec():
    return {
        "design": "arithmetic on published faces only: no panel, no refit, no bootstrap",
        "multiplier": "m = edge(top_draws) / edge(published band draws), read off E256's per-rung "
                      "edge_self ladder with log-log interpolation in the draw count",
        "multiplier_is_a_range": "every row is re-judged at all (family x rung) multipliers; the "
                                 "cells are fixed windows and neither E256 family is their "
                                 "analogue, so no family is nominated",
        "rejudge_rule": "the published rule, unchanged: outside = value < lo or value > hi, applied "
                        "to a band whose two edges are both scaled by m",
        "reproduction_gate": "a row whose published outside/inside flag does not reproduce from its "
                             "own published band is published as published_flag_not_reproduced and "
                             "counted separately, never silently re-judged",
        "band_draws_base": "each row's own published band draw count (200 in these faces), not 60",
        "top_draws": "the largest draw count the ladder measured",
        "tolerance_units": "distance_in_margins = |b|/|edge_top| - 1; zero is the line, negative is "
                           "inside",
        "what_is_not_done": ["no coefficient is re-priced", "no panel is read",
                            "no adoption, no bill", "no verdict in the source faces is rewritten"],
    }


def _summary(face):
    rows = face.get("rows") or []
    buckets = {}
    for r in rows:
        buckets[r.get("verdict")] = buckets.get(r.get("verdict"), 0) + 1
    outside_pub = [r for r in rows if r.get("outside_at_published") is True]
    flipped = [r for r in rows if r.get("verdict") == "flips_at_top_draws"]
    dep = [r for r in rows if r.get("verdict") == "flips_depends_on_measurement"]
    surv = [r for r in rows if r.get("verdict") == "survives_outside"]
    m = face.get("multiplier_table") or {}
    # Two faces may publish the SAME coefficient (E251's star_lag1 residual and E252's cross row
    # are the same number), so a row count over-states how many distinct verdicts moved. Publish
    # the distinct-coefficient count beside the row count.
    moving = flipped + dep
    distinct = len({round(r.get("b"), 10) for r in moving if r.get("b") is not None})
    return {
        "rows": len(rows),
        "rows_by_verdict": buckets,
        "rows_outside_at_published": len(outside_pub),
        "rows_flip_every_measurement": len(flipped),
        "rows_flip_for_some_measurement": len(dep),
        "rows_survive_outside": len(surv),
        "distinct_coefficients_moving": distinct,
        "row_to_coefficient_note": ("rows are (face, cell, row) triples; the same coefficient can be "
                                    "published by two faces, so distinct_coefficients_moving is the "
                                    "honest count of verdicts that moved"),
        "flipped_ids": ["%s/%s/%s" % (r.get("source"), r.get("cell"), r.get("row")) for r in flipped],
        "depends_ids": ["%s/%s/%s" % (r.get("source"), r.get("cell"), r.get("row")) for r in dep],
        "multiplier_min": m.get("multiplier_min"),
        "multiplier_max": m.get("multiplier_max"),
        "multiplier_median": m.get("multiplier_median"),
        "tightest_survivor_margin_at_top": min(
            [r.get("margin_at_top_median") for r in surv
             if r.get("margin_at_top_median") is not None] or [None]) if surv else None,
        "rows_counts_add_up": sum(buckets.values()) == len(rows),
        "rungs_in_ladder": sorted({n for (_f, n) in ((face.get("multiplier_table") or {})
                                                     .get("rung_index") or [])}),
    }


def _write(face, outdir, tag=""):
    os.makedirs(outdir, exist_ok=True)
    name = "BANDTOPFLIP-%s%s.json" % (CUTOFF, tag)
    path = os.path.join(outdir, name)
    with io.open(path, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    latest = os.path.join(outdir, "bandtopflip_latest.json")
    with io.open(latest, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    face["written"] = os.path.relpath(path, ROOT)
    return path


def _r(v, n=4):
    return "n/a" if v is None else ("%." + str(n) + "f") % v


def _fmt(face):
    s = face.get("summary") or {}
    lad = face.get("ladder_verdicts") or {}
    e = lad.get("e254") or {}
    lines = [
        "E257 band at top draws -- %s" % face.get("study"),
        "verdict: %s" % face.get("verdict"),
        "  %s" % face.get("verdict_reason"),
        "rows %s  outside@publish %s  flip-always %s  flip-some %s  survive %s"
        % (s.get("rows"), s.get("rows_outside_at_published"), s.get("rows_flip_every_measurement"),
           s.get("rows_flip_for_some_measurement"), s.get("rows_survive_outside")),
        "multiplier (edge_top/edge_published) %.4f .. %.4f median %.4f"
        % (s.get("multiplier_min") or 0, s.get("multiplier_max") or 0,
           s.get("multiplier_median") or 0),
        "E254 at top draws: %s (gap %s, tol %s) reasons %s"
        % (e.get("at_top_draws"), _r(e.get("family_gap"), 3), lad.get("gamma_tol"),
           e.get("reasons")),
        "E255 at top draws: %s (draws needed %s of %s)"
        % ((lad.get("e255") or {}).get("rejudged"),
           (lad.get("e255") or {}).get("draws_needed_for_both_families"), lad.get("top_draws")),
    ]
    for r in (face.get("rows") or []):
        if r.get("verdict") in ("flips_at_top_draws", "flips_depends_on_measurement"):
            lines.append("  %-10s %-14s %-20s b=%s edge_pub=%s edge_top=%s margin_top=%s"
                         % (r.get("source"), r.get("cell"), r.get("row"), _r(r.get("b"), 4),
                            _r(r.get("edge_published"), 4), _r(r.get("edge_at_top_median"), 4),
                            _r(r.get("margin_at_top_median"), 3)))
    return "\n".join(lines)


# ------------------------------------------------------------------ verify
def verify(outdir=None, tag=""):
    outdir = outdir or OUTDIR
    path = os.path.join(outdir, "BANDTOPFLIP-%s%s.json" % (CUTOFF, tag))
    problems = []
    if not os.path.exists(path):
        return {"ok": False, "problems": ["face missing: %s" % path]}
    with io.open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    ladder = load(FACES["ladder"])
    curves = ladder_curves(ladder)
    table = face.get("multiplier_table") or {}
    rows = face.get("rows") or []
    # every row's published flag must reproduce, and every flipped row must actually flip
    for r in rows:
        if r.get("verdict") in (None, "unjudgeable", "published_flag_not_reproduced"):
            continue
        b, lo, hi = r.get("b"), r.get("band_lo"), r.get("band_hi")
        if outside(b, lo, hi) != r.get("outside_at_published"):
            problems.append("%s/%s/%s: outside_at_published does not reproduce"
                            % (r.get("source"), r.get("cell"), r.get("row")))
        lo_t = (r.get("band_at_top_median") or [None])[0]
        hi_t = (r.get("band_at_top_median") or [None, None])[1]
        if lo_t is not None and hi_t is not None:
            want = outside(b, lo_t, hi_t)
            flips = r.get("verdict") == "flips_at_top_draws"
            if flips and want == r.get("outside_at_published"):
                problems.append("%s/%s/%s: marked flip but does not flip at the median band"
                                % (r.get("source"), r.get("cell"), r.get("row")))
    # the multiplier table must reproduce from the ladder
    for row in (table.get("rows") or []):
        key = (row.get("family"), int(row.get("sessions")))
        series = curves.get(key)
        if not series:
            problems.append("multiplier row %r has no ladder rung" % (key,))
            continue
        want_top = edge_at(series, table.get("top_draws"))
        if row.get("edge_at_top") is None or abs(row["edge_at_top"] - want_top) > 1e-12:
            problems.append("multiplier row %r edge_at_top does not reproduce" % (key,))
    # the summary must agree with the rows
    s = face.get("summary") or {}
    if s.get("rows") != len(rows):
        problems.append("summary.rows %r != len(rows) %d" % (s.get("rows"), len(rows)))
    if not s.get("rows_counts_add_up"):
        problems.append("row verdict buckets do not add up to the row count")
    # ladder verdicts must follow from the rung table
    lad = ladder_verdicts(ladder, curves)
    got = face.get("ladder_verdicts") or {}
    if (got.get("e254") or {}).get("at_top_draws") != (lad.get("e254") or {}).get("at_top_draws"):
        problems.append("E254 re-judgement does not follow from the ladder")
    if ((got.get("e255") or {}).get("draws_needed_for_both_families")
            != (lad.get("e255") or {}).get("draws_needed_for_both_families")):
        problems.append("E255 draws-needed does not follow from the ladder")
    # the verdict must follow from the rows
    v, _why = verdict_from(rows, got)
    if v != face.get("verdict"):
        problems.append("verdict %r does not follow from the rows (%r)" % (face.get("verdict"), v))
    return {"ok": not problems, "problems": problems, "rows": len(rows)}


# ------------------------------------------------------------------ selftest
_LEGS = []


def leg(ok, name, detail=None):
    _LEGS.append({"ok": bool(ok), "name": name, "detail": detail})
    return ok


def selftest():
    del _LEGS[:]
    # 1 log-log interpolation of the edge curve
    series = [(60, 0.40), (120, 0.50), (240, 0.625)]
    e120 = edge_at(series, 120)
    e_mid = edge_at(series, math.sqrt(60 * 240) and 120.0)
    leg(abs(e120 - 0.50) < 1e-12, "edge_at returns a grid point exactly", repr(e120))
    e_geom = edge_at(series, 120)
    leg(edge_at(series, 10) == 0.40 and edge_at(series, 1e9) == 0.625,
        "edge_at clamps at both ends instead of extrapolating")
    leg(abs(edge_at([(60, 0.4), (240, 0.8)], 120) - 0.4 * 2 ** 0.5) < 1e-12,
        "edge_at interpolates log-log between two draws")

    # 2 multiplier: rising ladder gives m > 1 (activity, not just arithmetic)
    tab = multiplier_table({("head", 100): [(60, 0.40), (240, 0.50), (1920, 0.80)]}, 200, 1920)
    m = tab["rows"][0]["multiplier"]
    leg(m > 1.0, "a rising edge gives a multiplier above one", "m=%.4f" % m)
    leg(abs(m - (0.80 / edge_at([(60, 0.40), (240, 0.50), (1920, 0.80)], 200))) < 1e-12,
        "the multiplier divides the top edge by the edge at the published draw count")

    # 3 the three flip outcomes
    base_rows = [{"source": "T", "cell": "c", "row": "r", "sessions": 200, "b": 0.62,
                  "band_lo": -0.55, "band_hi": 0.55, "band_draws": 200,
                  "published_outside": True, "b_source": "fixture"}]
    curves = {("head", 200): [(60, 0.40), (240, 0.50), (1920, 0.80)],
              ("tail", 200): [(60, 0.40), (240, 0.50), (1920, 0.70)]}
    tbl = multiplier_table(curves, 200, 1920)
    got = rejudge(base_rows, tbl, curves)[0]
    leg(got["verdict"] == "flips_at_top_draws",
        "a value just outside the published band flips when the band widens at every measurement",
        "%s m=%s" % (got["verdict"], got.get("multiplier_median")))
    leg(got["distance_in_margins_at_top_median"] < 0,
        "a flipped row reports a negative distance in margin units")

    wide = dict(base_rows[0], b=0.95, published_outside=True)
    leg(rejudge([wide], tbl, curves)[0]["verdict"] == "survives_outside",
        "a value far outside survives a band widened at every measurement")

    mixed = dict(base_rows[0], b=0.66, published_outside=True)
    # head m = 0.8/0.4xx ~ 1.9 -> edge 1.05 ; tail m = 1.7 -> edge 0.94; 0.66 inside both.
    split = {("head", 200): [(60, 0.40), (240, 0.50), (1920, 0.80)],
             ("tail", 200): [(60, 0.40), (240, 0.50), (1920, 0.49)]}
    tbl2 = multiplier_table(split, 200, 1920)
    res2 = rejudge([mixed], tbl2, split)[0]
    leg(res2["verdict"] == "flips_depends_on_measurement",
        "a value that flips for one family and not the other is published as measurement-dependent",
        res2["verdict"])

    inside = dict(base_rows[0], b=0.10, published_outside=False)
    leg(rejudge([inside], tbl, curves)[0]["verdict"] == "stays_inside",
        "an inside value stays inside when the band widens")

    # 4 a published flag that does not reproduce is not silently re-judged
    lie = dict(base_rows[0], b=0.10, published_outside=True)
    got = rejudge([lie], tbl, curves)[0]
    leg(got["verdict"] == "published_flag_not_reproduced",
        "a row whose published flag contradicts its own numbers is quarantined, not re-judged",
        got.get("reason"))

    # 5 unjudgeable rows are counted, never dropped
    ho = rejudge([{"source": "T", "cell": "c", "row": "r", "b": None, "band_lo": -1.0,
                   "band_hi": 1.0, "band_draws": 200, "published_outside": None}], tbl, curves)[0]
    leg(ho["verdict"] == "unjudgeable", "a row without a coefficient is unjudgeable, not dropped")

    # 6 loglog fit recovers a known exponent
    g, r2 = loglog_fit([(100, 1.0 * 100 ** -0.5), (200, 200 ** -0.5), (400, 400 ** -0.5)])
    leg(g is not None and abs(g - 0.5) < 1e-9 and r2 > 0.999,
        "loglog_fit recovers a known exponent", "gamma=%r r2=%r" % (g, r2))

    # 7 E254's rule and E255's floor
    v1 = e254_rule(0.30, 0.57, 0.90, 0.93, 0.1, 0.8)
    leg(v1[0] == "undetermined" and "family_gap_exceeds_tolerance" in v1[1],
        "the exponent stays undetermined on the family gap even when both fits clear the floor",
        repr(v1[1]))
    v2 = e254_rule(0.50, 0.51, 0.90, 0.93, 0.1, 0.8)
    leg(v2[0] == "determined", "a small family gap determines the exponent", repr(v2))
    v3 = e254_rule(0.50, 0.51, 0.50, 0.93, 0.1, 0.8)
    leg(v3[0] == "undetermined" and "r2_below_floor_head" in v3[1],
        "an r2 below the floor keeps the exponent undetermined")

    # 8 verdict totality
    leg(verdict_from([], {})[0] == "no_rows_measured", "verdict_from is total on an empty row list")
    leg(verdict_from(None, None)[0] == "no_rows_measured", "verdict_from is total on None inputs")

    # 9 the real ladder must have MOVED between the smallest and top draw count
    try:
        ladder = load(FACES["ladder"])
    except FileNotFoundError:
        ladder = None
    if ladder is not None:
        curves_r = ladder_curves(ladder)
        moved = 0
        for key, series in curves_r.items():
            if len(series) >= 2 and series[-1][1] > series[0][1]:
                moved += 1
        leg(moved >= len(curves_r) // 2 and moved > 0,
            "ACTIVITY: the ladder's top edge exceeds its smallest edge on most rungs",
            "moved %d of %d" % (moved, len(curves_r)))
        tab_r = multiplier_table(curves_r, DEFAULT_BASE_DRAWS, TOP_OF(ladder))
        leg(tab_r["multiplier_min"] is not None and tab_r["multiplier_min"] > 1.0,
            "every measured multiplier on the real ladder is above one",
            "min %r max %r" % (tab_r["multiplier_min"], tab_r["multiplier_max"]))
        # 10 published rows must reproduce their own flags against the real faces
        try:
            ss = starself_rows(load(FACES["starself"]))
        except FileNotFoundError:
            ss = []
        rej = rejudge(ss, tab_r, curves_r)
        shout = [r for r in rej if r.get("verdict") == "published_flag_not_reproduced"]
        leg(not shout, "every E252 row reproduces its own published outside/inside flag",
            "%d mismatch" % len(shout))
        leg(len([r for r in rej if r.get("verdict") == "unjudgeable"]) == 4,
            "exactly the four rows of the two band-less windows are unjudgeable")
    else:
        leg(False, "ACTIVITY: the ladder face is present", "missing")

    # 11 no panel/model library is imported by this face (inspect import statements only, so the
    # assertion's own prose cannot trip it -- the first cut failed on its own needle)
    import re as _re
    src = io.open(os.path.abspath(__file__), encoding="utf-8").read()
    imports = [ln.strip() for ln in src.splitlines()
               if _re.match(r"^\s*(import|from)\s+\w", ln)]
    banned = ("pan" + "das", "num" + "py", "poly" + "gon", "ak" + "share")
    hits = [ln for ln in imports if any(b in ln for b in banned)]
    leg(not hits, "the face imports no panel or market-data library", repr(hits)[:100])

    ok = sum(1 for l in _LEGS if l["ok"])
    return {"ok": ok == len(_LEGS), "passed": ok, "total": len(_LEGS), "legs": _LEGS}


# ------------------------------------------------------------------ main
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(description=STUDY)
    sub = ap.add_subparsers(dest="cmd")
    p_run = sub.add_parser("run")
    p_run.add_argument("--no-save", action="store_true")
    sub.add_parser("selftest")
    p_v = sub.add_parser("verify")
    p_v.add_argument("--tag", default="")
    p_pr = sub.add_parser("print")
    args = ap.parse_args(argv)
    if args.cmd == "run":
        face = run(save=not args.no_save)
        print(_fmt(face))
        return 0
    if args.cmd == "selftest":
        res = selftest()
        for l in res["legs"]:
            print(("PASS " if l["ok"] else "FAIL ") + l["name"] +
                  ("" if l["detail"] in (None, "") else "  [%s]" % (l["detail"],)))
        print("%d/%d legs" % (res["passed"], res["total"]))
        return 0 if res["ok"] else 1
    if args.cmd == "verify":
        res = verify(tag=args.tag)
        for p in res["problems"]:
            print("PROBLEM " + p)
        print("verify %s (%d rows)" % ("OK" if res["ok"] else "FAILED", res.get("rows", 0)))
        return 0 if res["ok"] else 1
    if args.cmd == "print":
        print(_fmt(load("BANDTOPFLIP-%s.json" % CUTOFF)))
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())