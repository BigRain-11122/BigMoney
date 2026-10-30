#!/usr/bin/env python3
"""E253 -- the star's self row is unmeasured after 2025: waiting state, or a weaker channel?

E252 published one headline pair (b_self -0.7339 vs b_cross -0.7250, difference CI
[-0.305,+0.299]) and one awkward era: in era_2025_now the self coefficient -0.463 sits INSIDE its
own shuffled band while the cross column stays at -0.911 outside its own, on 408 sessions. Two
readings survive that face: the self row simply has not been measured yet (a short sample), or the
star's self channel genuinely weakened after 2025 (E246's prior is a sign flip by era).

This face does no re-pricing and fits no new coefficient. It reads the published E252 face and
turns each band into a session count, because a shuffled band is the only thing in that design
that says what "measured" means:

  a coefficient is measured iff |b| clears the edge its own shuffled column produces at that n.

Band width shrinks with the session count, so the edge at another sample size is

    edge(n') = edge(n) * (n / n')**gamma        (gamma = 1/2 as frozen below)

which inverts to the sessions a given coefficient needs:

    n'(b) = n * (edge(n) / |b|)**(1/gamma)

Three readings fall out of the same arithmetic and each is reported separately, because they
answer different questions:

  NEEDED     how many sessions the OBSERVED self coefficient would need to clear its own band
             -> is the window still accruing enough sessions to get there?
  FLOOR      the smallest |b| that clears at the CURRENT n (the edge itself)
             -> how far under the line the observation sits today
  PRIOR      how many sessions a channel of the previously published size would have needed
             -> was the window already long enough for that channel to have spoken?

and one distributional reading, which uses the band's own scale rather than its position:

  Z          (b_prior - b_observed) / sd_null, sd_null read off the published band as a
             full-draw range (E252 publishes min/max of 200 shuffles, not percentiles):
             sd_null = (hi - lo) / (2 * E[max|Z|, 200 draws])

Verdicts are frozen and recomputable from the published numbers alone. NO BILL, NO ADOPTION, NO
RE-PRICING: this face schedules a measurement, it does not make one.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

STUDY = "E253"
SOURCE_FACE = os.path.join(OUTDIR, "STARSELF-2026-10-29.json")

# frozen before the face was read
GAMMA = 0.5                    # band half-width ~ n**-gamma under a stable null (iid shuffles)
GAMMAS = (0.35, 0.5, 0.65)     # sensitivity sweep; 0.5 decides
Z_WEAK = 2.0                   # shrinkage is called "weakened" only at/above this many sd_null
MIN_B = 1e-6                   # a coefficient this small needs infinite sessions; reported as None
VERDICTS = ("self_row_resolves_with_more_sessions",
            "self_row_weakened_beyond_small_sample",
            "self_row_unreachable_in_this_window")


# ------------------------------------------------------------------ pure arithmetic
def edge_for(b, lo, hi):
    """The band edge the coefficient has to clear: the side it sits on."""
    if b is None or lo is None or hi is None:
        return None
    return lo if b < 0 else hi


def needed_sessions(n, b, edge, gamma=GAMMA):
    """Sessions at which a coefficient of size |b| clears an edge that scales as n**-gamma."""
    if n is None or n <= 0 or b is None or edge is None:
        return None
    b, edge = abs(float(b)), abs(float(edge))
    if b < MIN_B or edge <= 0.0:
        return None
    return float(n) * (edge / b) ** (1.0 / gamma)


def margin(b, edge):
    """|b| / |edge|: >1 means the coefficient is outside its own band."""
    if b is None or edge is None or abs(float(edge)) < MIN_B:
        return None
    return abs(float(b)) / abs(float(edge))


def emax_abs_z(draws):
    """E[max|Z|] over `draws` standard draws (extremal-value approximation, no table)."""
    d = max(int(draws or 200), 2)
    m = 2.0 * d
    s = math.sqrt(2.0 * math.log(m))
    return s - (math.log(math.log(m)) + math.log(4.0 * math.pi)) / (2.0 * s)


def sd_from_band(lo, hi, draws=200):
    """sd of the null coefficient from a published full-draw-range band."""
    if lo is None or hi is None:
        return None
    width = abs(float(hi) - float(lo))
    if width <= 0.0:
        return None
    return width / (2.0 * emax_abs_z(draws))


def _loglog_slope(points):
    """Least-squares slope of log(y) on log(x); the band exponent gamma = -slope."""
    pts = [(x, y) for x, y in points if x and y and x > 0 and y > 0]
    if len(pts) < 3:
        return None, None
    xs = [math.log(x) for x, _ in pts]
    ys = [math.log(y) for _, y in pts]
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0.0:
        return None, None
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (my + slope * (x - mx))) ** 2 for x, y in zip(xs, ys))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else None
    return slope, r2


def sessions_density(cell):
    """Sessions per calendar day over the cell's own span (the window's own clock)."""
    first, last, n = cell.get("first"), cell.get("last"), cell.get("sessions")
    if not first or not last or not n:
        return None
    try:
        d0 = datetime.strptime(first, "%Y-%m-%d").date()
        d1 = datetime.strptime(last, "%Y-%m-%d").date()
    except ValueError:
        return None
    span = (d1 - d0).days + 1
    if span <= 0:
        return None
    return float(n) / float(span)


def eta_date(cell, sessions_short):
    """Calendar date at which the cell would reach its needed session count."""
    dens = sessions_density(cell)
    if dens is None or sessions_short is None or sessions_short <= 0:
        return None
    days = int(math.ceil(sessions_short / dens))
    try:
        d1 = datetime.strptime(cell["last"], "%Y-%m-%d").date()
    except (KeyError, ValueError):
        return None
    return (d1 + timedelta(days=days)).isoformat()


def row_reading(cell, row, gamma=GAMMA):
    """One row (self|cross) of one cell, as sessions and margins."""
    band = cell.get("band_%s" % row) or {}
    body = band.get("band") or {}
    b = ((cell.get("%s_row" % row) or {}).get("b_%s" % row))
    lo, hi, draws = body.get("lo"), body.get("hi"), body.get("draws")
    edge = edge_for(b, lo, hi)
    n = cell.get("sessions")
    m = margin(b, edge)
    need = needed_sessions(n, b, edge, gamma)
    sd = sd_from_band(lo, hi, draws)
    sd_200 = sd_from_band(lo, hi, 200)
    outside = (edge is not None and b is not None and abs(b) > abs(edge))
    return {"row": row, "b": b, "band_lo": lo, "band_hi": hi, "band_draws": draws,
            "edge": edge, "margin": m, "outside_band": outside,
            "sessions": n, "needed": need, "sd_null": sd, "sd_null_at_200_draws": sd_200}


def cell_reading(cell, prior_b=None, prior_label=None, gamma=GAMMA):
    """Resolution reading for one published cell; undecided cells are reported, not judged."""
    n = cell.get("sessions")
    out = {"label": cell.get("label"), "kind": cell.get("kind"), "star": cell.get("star"),
           "sessions": n, "first": cell.get("first"), "last": cell.get("last"),
           "decided": bool(cell.get("decided")), "reason": cell.get("reason"),
           "verdict_in_source": cell.get("verdict")}
    if not cell.get("decided") or cell.get("star") is None:
        out["status"] = "not_a_star_cell"
        return out

    self_row = row_reading(cell, "self", gamma)
    cross_row = row_reading(cell, "cross", gamma)
    open_window = bool(cell.get("last") and cell.get("last") == cell.get("_cutoff"))

    out["self_row"] = self_row
    out["cross_row"] = cross_row
    out["window_open"] = open_window

    short = None
    if self_row["needed"] is not None and n is not None:
        short = self_row["needed"] - float(n)
    out["sessions_short"] = short
    # a calendar ETA only exists for a window that keeps accruing
    out["eta"] = eta_date(cell, short) if (open_window and (short or 0) > 0) else None

    # reading 3: was the window already long enough for a channel of the prior size?
    prior = None
    if prior_b is not None:
        prior_edge = self_row["edge"]
        prior_need = needed_sessions(n, prior_b, prior_edge, gamma)
        gap = (None if self_row["b"] is None else float(self_row["b"]) - float(prior_b))
        z = z200 = None
        if gap is not None and self_row["sd_null"]:
            z = gap / self_row["sd_null"]
        if gap is not None and self_row["sd_null_at_200_draws"]:
            z200 = gap / self_row["sd_null_at_200_draws"]
        prior = {"label": prior_label, "b_prior": prior_b, "needed": prior_need,
                 "window_long_enough_for_prior": (prior_need is not None and n is not None
                                                  and prior_need <= float(n)),
                 "shortfall": gap,
                 "z_vs_prior": z,
                 "z_vs_prior_200_draws": z200,
                 "z_line_cleared": (z is not None and abs(z) >= Z_WEAK)}
    out["prior"] = prior

    if self_row["outside_band"]:
        out["status"] = "measured_outside"
        out["verdict"] = "measured"
    elif open_window:
        out["status"] = "silent_reachable"
        out["verdict"] = "self_row_resolves_with_more_sessions"
    else:
        out["status"] = "silent_unreachable"
        out["verdict"] = "self_row_unreachable_in_this_window"
    return out


def _cleared_cells(cells):
    """Published cells in which the star's self row actually cleared its band."""
    out = []
    for c in cells:
        if not c.get("decided") or c.get("star") is None:
            continue
        b = (c.get("self_row") or {}).get("b_self")
        band = ((c.get("band_self") or {}).get("band") or {})
        if b is None or band.get("lo") is None:
            continue
        if abs(b) > abs(edge_for(b, band.get("lo"), band.get("hi"))):
            out.append({"label": c.get("label"), "first": c.get("first"),
                        "last": c.get("last"), "b_self": b})
    out.sort(key=lambda x: (x.get("last") or ""))
    return out


def _prior_for(cell, cleared):
    """The most recent clearing cell that ENDED BEFORE this cell began (no overlap, no leakage)."""
    start = cell.get("first") or ""
    best = None
    for c in cleared:
        if c.get("label") == cell.get("label"):
            continue
        if (c.get("last") or "") < start:
            best = c
    return best


def decide(rows, z_line=Z_WEAK):
    """Frozen decision rule: a reachable cell outranks a weakened call, which outranks silence."""
    reachable = [r for r in rows if r.get("status") == "silent_reachable"]
    unreachable = [r for r in rows if r.get("status") == "silent_unreachable"]
    weak = [r for r in reachable
            if (r.get("prior") or {}).get("z_vs_prior") is not None
            and abs(r["prior"]["z_vs_prior"]) >= z_line
            and (r["prior"].get("z_vs_prior_200_draws") is None
                 or abs(r["prior"]["z_vs_prior_200_draws"]) >= z_line)
            and r["prior"].get("window_long_enough_for_prior")]
    if weak:
        return "self_row_weakened_beyond_small_sample", weak
    if reachable:
        return "self_row_resolves_with_more_sessions", reachable
    if unreachable:
        return "self_row_unreachable_in_this_window", unreachable
    return "measured", []


def run(face_path=None, save=True, gamma=GAMMA, outdir=None, prior_b=None):
    face_path = face_path or SOURCE_FACE
    with open(face_path, encoding="utf-8") as fh:
        src = json.load(fh)
    cells = [dict(c, _cutoff=src.get("evidence_cutoff")) for c in src.get("cells") or []]
    cleared = _cleared_cells(cells)

    rows = []
    for c in cells:
        prior = _prior_for(c, cleared)
        rows.append(cell_reading(c, prior_b=(prior_b if prior_b is not None
                                             else (prior or {}).get("b_self")),
                                 prior_label=(("override" if prior_b is not None
                                               else (prior or {}).get("label"))),
                                 gamma=gamma))
    verdict, carriers = decide(rows)

    # the band exponent is checked, not assumed: fit gamma on the published bands themselves
    self_pts = [(r.get("sessions"), abs((r.get("self_row") or {}).get("edge") or 0.0))
                for r in rows if (r.get("self_row") or {}).get("edge")]
    cross_pts = [(r.get("sessions"), abs((r.get("cross_row") or {}).get("edge") or 0.0))
                 for r in rows if (r.get("cross_row") or {}).get("edge")]
    slope_s, r2_s = _loglog_slope(self_pts)
    slope_c, r2_c = _loglog_slope(cross_pts)

    # gamma sensitivity on every reachable cell (needed sessions under each exponent)
    sens = {}
    gamma_fit = (-slope_s) if slope_s else None
    for r in rows:
        if not (r.get("self_row") or {}).get("b"):
            continue
        sr = r["self_row"]
        row_sens = {("%.2f" % g): needed_sessions(r.get("sessions"), sr["b"], sr["edge"], g)
                    for g in GAMMAS}
        if gamma_fit and 0.0 < gamma_fit < 1.5:
            row_sens["fit"] = needed_sessions(r.get("sessions"), sr["b"], sr["edge"], gamma_fit)
        sens[r["label"]] = row_sens

    headline = None
    carrier_labels = [r.get("label") for r in carriers]
    for r in rows:
        if r.get("label") in carrier_labels:
            headline = r
            break
    if headline is None:
        for r in rows:
            if r.get("status") in ("silent_reachable", "silent_unreachable", "measured_outside"):
                headline = r
                break

    out = {
        "study": STUDY,
        "title": "the star's self row is unmeasured after 2025: waiting state, or a weaker channel?",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": src.get("evidence_cutoff"),
        "source_face": os.path.relpath(face_path, ROOT),
        "source_study": src.get("study"),
        "frozen_spec": {
            "design": "resolution arithmetic on the published face only: every number here is a "
                      "band width, a session count or a ratio of the two",
            "band_scaling": "edge(n') = edge(n) * (n/n')**gamma",
            "needed_sessions": "n'(b) = n * (edge(n)/|b|)**(1/gamma)",
            "gamma_default": GAMMA,
            "gamma_sweep": list(GAMMAS),
            "gamma_check": "least-squares slope of log|edge| on log(n) across the published "
                           "cells; gamma = -slope, published with r2 and never used to decide",
            "sd_from_band": "sd_null = (hi-lo)/(2*E[max|Z|]) where E[max|Z|] is the extremal "
                            "approximation over the cell's own draw count (E252 publishes a "
                            "full-draw range, not percentiles; era cells carry 60 draws, the "
                            "headline 200). Both readings are published as "
                            "sd_null / sd_null_at_200_draws and z_vs_prior / z_vs_prior_200_draws",
            "weakened_needs_both_z_readings": "the widened call requires |z| >= z_weak under both "
                                              "sd readings, so a coarse band cannot manufacture it",
            "verdicts": list(VERDICTS),
            "z_weak": Z_WEAK,
            "prior_rule": "the prior channel is the self coefficient of the LAST cell in which the "
                          "self row cleared its band (E252 face order by last date); it is a "
                          "published number, not a refit",
            "decision_rule": "weakened = (z_vs_prior >= z_weak) and (window_long_enough_for_prior); "
                             "otherwise a reachable silence is a waiting state; a closed window "
                             "whose needed sessions exceed its fixed length is unreachable",
            "no_refit": "no panel is read, no coefficient is fitted: the face is arithmetic on "
                        "results/state_tilt/STARSELF-*.json",
            "reuse": "cell/band field names and the outside-band rule from e252_star_prices_itself",
        },
        "prior": {"rule": "per cell: the most recent published star cell that ended before this cell "
                           "began and in which the self row cleared its band (no overlap, so no "
                           "leakage); cells with no such predecessor carry prior=null",
                  "cells_with_prior": [{"cell": r.get("label"),
                                        "prior": (r.get("prior") or {}).get("label"),
                                        "b_prior": (r.get("prior") or {}).get("b_prior")}
                                       for r in rows if (r.get("prior") or {}).get("b_prior")
                                       is not None],
                  "cleared_cells": [{"label": c["label"], "last": c["last"],
                                     "b_self": c["b_self"]} for c in cleared]},
        "gamma_check": {"self_slope": slope_s, "self_gamma": (-slope_s if slope_s else None),
                        "self_r2": r2_s, "cross_slope": slope_c,
                        "cross_gamma": (-slope_c if slope_c else None), "cross_r2": r2_c,
                        "points_self": len(self_pts), "points_cross": len(cross_pts)},
        "gamma_sensitivity": sens,
        "cells": rows,
        "rollup": _rollup(rows, verdict, carriers),
        "no_bill": "scheduling only: no adoption, no re-pricing, no member billed",
        "written": None,
    }
    out["summary"] = _summary(out, headline)
    if save:
        out["written"] = _write(out, outdir or OUTDIR)
    return out


def _rollup(rows, verdict, carriers):
    by_status = {}
    for r in rows:
        by_status[r.get("status")] = by_status.get(r.get("status"), 0) + 1
    return {"cells_read": len(rows), "cells_judged": sum(
                1 for r in rows if r.get("status") in
                ("measured_outside", "silent_reachable", "silent_unreachable")),
            "cells_by_status": by_status, "verdict": verdict,
            "carriers": [r.get("label") for r in carriers],
            "self_cleared_cells": [r["label"] for r in rows
                                   if r.get("status") == "measured_outside" and
                                   (r.get("self_row") or {}).get("outside_band")]}


def _summary(face, headline):
    h = headline or {}
    sr = h.get("self_row") or {}
    cr = h.get("cross_row") or {}
    pr = h.get("prior") or {}
    return {"verdict": face["rollup"]["verdict"],
            "headline_cell": h.get("label"),
            "headline_sessions": h.get("sessions"),
            "headline_self_b": sr.get("b"), "headline_self_edge": sr.get("edge"),
            "headline_self_margin": sr.get("margin"),
            "headline_self_sessions_needed": sr.get("needed"),
            "headline_sessions_short": h.get("sessions_short"),
            "headline_eta": h.get("eta"),
            "headline_cross_b": cr.get("b"), "headline_cross_edge": cr.get("edge"),
            "headline_cross_margin": cr.get("margin"),
            "headline_cross_sessions_needed": cr.get("needed"),
            "headline_prior_b": pr.get("b_prior"), "headline_prior_sessions_needed": pr.get("needed"),
            "headline_window_long_enough_for_prior": pr.get("window_long_enough_for_prior"),
            "headline_z_vs_prior": pr.get("z_vs_prior"),
            "headline_sd_null": sr.get("sd_null"),
            "self_cells_measured_outside": face["rollup"]["self_cleared_cells"],
            "gamma_check_self_gamma": face["gamma_check"]["self_gamma"],
            "gamma_check_self_r2": face["gamma_check"]["self_r2"],
            "headline_needed_under_fitted_gamma": (face.get("gamma_sensitivity") or {})
                                                  .get(h.get("label"), {}).get("fit"),
            "headline_sd_null_at_200_draws": sr.get("sd_null_at_200_draws"),
            "headline_z_vs_prior_200_draws": pr.get("z_vs_prior_200_draws")}


def _write(face, outdir):
    os.makedirs(outdir, exist_ok=True)
    cutoff = face.get("evidence_cutoff") or "unknown"
    path = os.path.join(outdir, "SELFRES-%s.json" % cutoff)
    latest = os.path.join(outdir, "selfres_latest.json")
    body = json.dumps(face, indent=1, sort_keys=True, ensure_ascii=False)
    for p in (path, latest):
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")
    return {"face": os.path.relpath(path, ROOT), "latest": os.path.relpath(latest, ROOT),
            "bytes": len(body)}


def _fmt(face):
    s = face["summary"]
    return ("%s | verdict %s | cell %s n=%s | self b=%s edge=%s needs %s sessions "
            "(short %s, eta %s) | cross b=%s edge=%s needs %s | prior %s needs %s z=%s"
            % (face["study"], s["verdict"], s["headline_cell"], s["headline_sessions"],
               _r(s["headline_self_b"]), _r(s["headline_self_edge"]),
               _r(s["headline_self_sessions_needed"], 1), _r(s["headline_sessions_short"], 1),
               s["headline_eta"], _r(s["headline_cross_b"]), _r(s["headline_cross_edge"]),
               _r(s["headline_cross_sessions_needed"], 1), _r(s["headline_prior_b"]),
               _r(s["headline_prior_sessions_needed"], 1), _r(s["headline_z_vs_prior"], 2)))


def _r(v, n=4):
    return None if v is None else round(float(v), n)


# ---------------------------------------------------------------- selftest fixtures
def leg(ok, name, detail=None):
    return {"leg": name, "pass": bool(ok), "detail": detail}


def _cell(label="c", n=400, b_self=-0.46, lo=-0.52, hi=0.45, b_cross=-0.91, clo=-0.41, chi=0.46,
          first="2025-01-02", last="2026-10-29", star="s0", decided=True, kind="era",
          cutoff="2026-10-29"):
    return {"label": label, "kind": kind, "star": star, "sessions": n, "first": first,
            "last": last, "decided": decided, "reason": None, "verdict": "x",
            "_cutoff": cutoff,
            "self_row": {"b_self": b_self},
            "cross_row": {"b_cross": b_cross},
            "band_self": {"band": {"lo": lo, "hi": hi, "draws": 200}},
            "band_cross": {"band": {"lo": clo, "hi": chi, "draws": 200}}}


def _face(cells, cutoff="2026-10-29"):
    return {"study": "E252", "evidence_cutoff": cutoff, "cells": cells}


def _run_cells(cells, prior_b=None, gamma=GAMMA, cutoff="2026-10-29"):
    """Run the reader on a fixture face without touching disk."""
    import tempfile
    fd, p = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(_face(cells, cutoff), fh)
        return run(face_path=p, save=False, gamma=gamma, prior_b=prior_b)
    finally:
        try:
            os.unlink(p)
        except OSError:
            pass


def selftest():
    legs = []

    # 1. the inversion is exact at its own fixed point: a coefficient sitting on the edge needs n
    legs.append(leg(abs(needed_sessions(400, 0.52, -0.52) - 400.0) < 1e-9,
                    "a coefficient exactly on its edge needs the same n it was measured at",
                    {"needed": needed_sessions(400, 0.52, -0.52)}))

    # 2. doubling the coefficient quarters the sessions (gamma=1/2)
    legs.append(leg(abs(needed_sessions(400, 1.04, -0.52) - 100.0) < 1e-9,
                    "twice the coefficient needs a quarter of the sessions",
                    {"needed": needed_sessions(400, 1.04, -0.52)}))

    # 3. the edge is chosen on the side the coefficient sits, not always lo
    legs.append(leg(edge_for(-0.4, -0.5, 0.3) == -0.5 and edge_for(0.4, -0.5, 0.3) == 0.3,
                    "edge selection follows the sign of the coefficient",
                    {"neg": edge_for(-0.4, -0.5, 0.3), "pos": edge_for(0.4, -0.5, 0.3)}))

    # 4. an outside coefficient is measured, never scheduled
    f = _run_cells([_cell(b_self=-0.73, lo=-0.32, hi=0.23)])
    c = f["cells"][0]
    legs.append(leg(c["status"] == "measured_outside" and c["self_row"]["outside_band"] is True,
                    "a coefficient outside its band reads as measured",
                    {"status": c["status"], "margin": c["self_row"]["margin"]}))

    # 5. an inside coefficient in a window that runs to the data edge is reachable, with an eta
    c = _run_cells([_cell()])["cells"][0]
    legs.append(leg(c["status"] == "silent_reachable" and c["sessions_short"] > 0
                    and c["eta"] and c["eta"] > "2026-10-29",
                    "an open window schedules the sessions it still needs",
                    {"status": c["status"], "short": c["sessions_short"], "eta": c["eta"]}))

    # 6. the same numbers in a window that stops well before the cutoff are unreachable
    c = _run_cells([_cell(first="2013-03-18", last="2016-11-03", n=831)])["cells"][0]
    legs.append(leg(c["status"] == "silent_unreachable",
                    "a closed window cannot be scheduled even when the arithmetic asks for more",
                    {"status": c["status"], "window_open": c["window_open"],
                     "needed": c["self_row"]["needed"]}))

    # 7. a cell with no star is reported, not judged
    c = _run_cells([_cell(star=None, decided=False)])["cells"][0]
    legs.append(leg(c["status"] == "not_a_star_cell" and "self_row" not in c,
                    "a cell without a star is listed with its reason and not judged",
                    {"status": c["status"]}))

    # 8. gamma is recovered when the bands really do scale as n**-0.5
    cells = [_cell(label="a", n=400, lo=-0.52, hi=0.50), _cell(label="b", n=800, lo=-0.52 / 2 ** 0.5,
                                                              hi=0.50 / 2 ** 0.5),
             _cell(label="c", n=1600, lo=-0.52 / 2.0, hi=0.50 / 2.0)]
    g = _run_cells(cells)["gamma_check"]
    legs.append(leg(g["self_gamma"] is not None and abs(g["self_gamma"] - 0.5) < 1e-6
                    and abs((g["self_r2"] or 0.0) - 1.0) < 1e-9,
                    "the exponent check recovers a written 1/sqrt(n) band",
                    {"gamma": g["self_gamma"], "r2": g["self_r2"]}))

    # 9. a weaker scaling asks for fewer sessions (monotone in gamma)
    a = needed_sessions(400, 0.46, -0.52, 0.35)
    b = needed_sessions(400, 0.46, -0.52, 0.65)
    legs.append(leg(a > needed_sessions(400, 0.46, -0.52, 0.5) > b,
                    "the gamma sweep is monotone: a flatter band needs fewer sessions",
                    {"g0.35": a, "g0.65": b}))

    # 10. the sd read off a full-draw range is the range over twice E[max|Z|]
    sd = sd_from_band(-1.0, 1.0, 200)
    legs.append(leg(abs(sd - (2.0 / (2.0 * emax_abs_z(200)))) < 1e-12
                    and emax_abs_z(60) < emax_abs_z(200) < 3.0,
                    "sd_from_band divides the full range by 2*E[max|Z|] and the factor grows "
                    "with the draw count",
                    {"sd": sd, "emax60": emax_abs_z(60), "emax200": emax_abs_z(200)}))

    # 11. a prior of the published size is detected in fewer sessions than the window has
    c = _run_cells([_cell()], prior_b=-0.80)["cells"][0]
    legs.append(leg(c["prior"]["needed"] < c["sessions"]
                    and c["prior"]["window_long_enough_for_prior"] is True,
                    "a prior-size channel would have cleared inside this window",
                    {"prior_needed": c["prior"]["needed"], "n": c["sessions"],
                     "z": c["prior"]["z_vs_prior"]}))

    # 12. the prior is not called weakened unless it clears the frozen z line AND the window was
    # long enough for it; a small prior is not "weakened", it is simply out of reach
    rows = _run_cells([_cell()], prior_b=-0.80)["cells"]
    v_soft = decide(rows, z_line=2.0)[0]
    rows_hard = _run_cells([_cell()], prior_b=-1.05)["cells"]
    v_hard = decide(rows_hard, z_line=2.0)[0]
    rows_small = _run_cells([_cell()], prior_b=-0.20)["cells"]
    v_small = decide(rows_small, z_line=2.0)[0]
    legs.append(leg(v_soft == "self_row_resolves_with_more_sessions"
                    and v_hard == "self_row_weakened_beyond_small_sample"
                    and v_small == "self_row_resolves_with_more_sessions",
                    "the z line decides waiting vs weakened and nothing else does",
                    {"soft": v_soft, "hard": v_hard, "small_prior": v_small}))

    # 13. a zero coefficient is never scheduled (no division by zero, no fake infinity)
    legs.append(leg(needed_sessions(400, 0.0, -0.52) is None,
                    "a zero coefficient reports None rather than an infinite session count",
                    {"needed": needed_sessions(400, 0.0, -0.52)}))

    # 14. a missing band is reported, never guessed
    c = _run_cells([_cell()])["cells"][0]
    bad = {"label": "x", "kind": "era", "star": "s0", "sessions": 400, "first": "2025-01-02",
           "last": "2026-10-29", "decided": True, "self_row": {"b_self": -0.4},
           "cross_row": {"b_cross": -0.9}, "_cutoff": "2026-10-29"}
    rr = row_reading(bad, "self")
    legs.append(leg(c["self_row"]["needed"] is not None and rr["needed"] is None
                    and rr["outside_band"] is False,
                    "a row without a published band asks for no sessions",
                    {"with_band": c["self_row"]["needed"], "without_band": rr["needed"]}))

    # 15. determinism: two reads of the same face agree on every computed number
    d1 = _run_cells([_cell()], prior_b=-0.80)
    d2 = _run_cells([_cell()], prior_b=-0.80)
    legs.append(leg(json.dumps(d1["cells"], sort_keys=True) == json.dumps(d2["cells"],
                                                                          sort_keys=True),
                    "two reads of one face agree cell for cell", None))

    # 16. the face's own verdict table covers the cells it judged, and the summary matches it
    f = _run_cells([_cell(label="open"), _cell(label="closed", first="2013-03-18",
                                               last="2016-11-03", n=831)])
    legs.append(leg(f["rollup"]["cells_judged"] == 2
                    and f["summary"]["verdict"] == f["rollup"]["verdict"]
                    and f["summary"]["headline_cell"] == "open",
                    "rollup counts every judged cell and the summary mirrors it",
                    {"rollup": f["rollup"], "headline": f["summary"]["headline_cell"]}))

    return {"legs": legs, "passed": sum(1 for x in legs if x["pass"]), "total": len(legs),
            "ok": all(x["pass"] for x in legs)}


def verify(outdir=None):
    """Re-derive the published verdict from the saved face's own numbers."""
    outdir = outdir or OUTDIR
    latest = os.path.join(outdir, "selfres_latest.json")
    with open(latest, encoding="utf-8") as fh:
        face = json.load(fh)
    bad = []
    rows = face.get("cells") or []
    verdict, _ = decide(rows)
    if verdict != (face.get("rollup") or {}).get("verdict"):
        bad.append("verdict_stale")
    for r in rows:
        sr = r.get("self_row") or {}
        if sr.get("b") is None or sr.get("edge") is None:
            continue
        outside = abs(sr["b"]) > abs(sr["edge"])
        if outside != bool(sr.get("outside_band")):
            bad.append("outside_band@%s" % r.get("label"))
        need = needed_sessions(r.get("sessions"), sr["b"], sr["edge"], GAMMA)
        if need is None and sr.get("needed") is not None:
            bad.append("needed_none@%s" % r.get("label"))
        elif need is not None and sr.get("needed") is not None and \
                abs(need - sr["needed"]) > 1e-6:
            bad.append("needed_drift@%s" % r.get("label"))
    if not face.get("evidence_cutoff"):
        bad.append("no_evidence_cutoff")
    s = face.get("summary") or {}
    return {"ok": not bad, "problems": bad, "cells": len(rows), "verdict": s.get("verdict"),
            "cell": s.get("headline_cell"), "needed": s.get("headline_self_sessions_needed"),
            "short": s.get("headline_sessions_short"), "eta": s.get("headline_eta"),
            "face": os.path.relpath(latest, ROOT)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", nargs="?", default="run", choices=("run", "selftest", "verify"))
    ap.add_argument("--face", default=None)
    ap.add_argument("--gamma", type=float, default=GAMMA)
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
        print("verify: cells=%s verdict=%s cell=%s needed=%s short=%s eta=%s -> %s"
              % (r.get("cells"), r.get("verdict"), r.get("cell"), _r(r.get("needed"), 1),
                 _r(r.get("short"), 1), r.get("eta"), "OK" if r["ok"] else "FAIL"))
        return 0 if r["ok"] else 1
    face = run(face_path=args.face, gamma=args.gamma)
    print(_fmt(face))
    print("written: %s" % (face.get("written") or {}).get("face"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())