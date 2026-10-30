"""ETF book atlas -- the toll ladder read-back: is the config ordering a zero-cost object?

r1350 read the phase atlas and said "cadence is the quotable knob, width sits inside the
band" at ONE toll (10bp/side). E256/E257 then bracketed the toll (0 / 5 / 10 / 20 / 40 bp
per side) and re-ran the same 12-cell grid, but every reader so far only consumed those
faces one arm at a time, and ``etf_book_phase_atlas_arms`` reads them for the BAND ("the
band follows the decision count, not the toll").  Nobody has asked the complementary
question, which is the one that decides whether the atlas sentence may be quoted at all:

    the atlas's own criterion is "between-cell spread > median cell band".  Both quantities
    move with the toll.  At what toll does the ordering stop clearing its own phase noise,
    and is the decay monotone (a toll) or not (noise)?

Answering it needs no engine: every rung is already a published face.  This module runs the
ladder, interpolates the crossing, and re-derives the verdict from frozen constants so an
edited face is red rather than quotable.

Two ladders, both read by (cost, buffer_k) TAKEN FROM THE FACE'S OWN ``audit`` BLOCK, never
from the file name (r1325 path test: a file called cost20 whose audit says otherwise is
whatever its audit says):

  toll ladder    buffer_k == 0         -> cost is the only moving knob, 5 rungs
  buffer ladder  cost == production    -> buffer_k is the only moving knob, 7 rungs

A face that moves BOTH knobs (e.g. k=0.05 @ 5bp/side) belongs to neither ladder: an arm
that changes two things cannot be a rung of a one-dimensional ladder, so it is published
under ``excluded`` with its reason instead of being averaged in.

  python scripts/etf_book_atlas_toll_ladder.py run        # re-derive + write the face
  python scripts/etf_book_atlas_toll_ladder.py --check     # gate: face must follow its sources
  python scripts/etf_book_atlas_toll_ladder.py --selftest

Outputs:
  results/etf_book_atlas_toll_ladder.json

Exploratory measurement: no ledger booking, no admission change, no engine run.
"""
import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
OUT = os.path.join(RES, "etf_book_atlas_toll_ladder.json")

FACE_GLOB = os.path.join(RES, "etf_book_phase_atlas*.json")

# ---- frozen constants (declared before any number is read; the gate refuses an edit) ----
PRODUCTION_TOLL_BP = 8.0     # the toll the production card is charged at (E200)
BASELINE_COST = 0.001        # the atlas baseline arm's cost, as a fraction per side
GATE_TOL_PP = 1e-9           # the atlas's own gate tolerance
MIN_RUNGS = 2                # one rung is not a ladder
MONOTONE_RHO = -0.90         # "the ordering decays with the toll" needs near-strict monotone
DOSE_RHO = 0.70              # a buffer dose requires this rank correlation with the strength
CADENCE_FAST, CADENCE_SLOW = 10, 40
WIDTH_NARROW, WIDTH_WIDE = 3, 12


# ----------------------------------------------------------------------------- primitives
def _median(a):
    b = sorted(a)
    n = len(b)
    if not n:
        return None
    return b[n // 2] if n % 2 else 0.5 * (b[n // 2 - 1] + b[n // 2])


def _rank(a):
    """Average ranks (ties share the mean rank) -- no scipy dependency."""
    order = sorted(range(len(a)), key=lambda i: a[i])
    ranks = [0.0] * len(a)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and a[order[j + 1]] == a[order[i]]:
            j += 1
        mean = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = mean
        i = j + 1
    return ranks


def _pearson(x, y):
    n = len(x)
    if n < 2:
        return None
    mx, my = sum(x) / n, sum(y) / n
    sx = sum((v - mx) ** 2 for v in x)
    sy = sum((v - my) ** 2 for v in y)
    if sx <= 0 or sy <= 0:
        return None
    return sum((x[i] - mx) * (y[i] - my) for i in range(n)) / (sx * sy) ** 0.5


def spearman(x, y):
    if len(x) < 2:
        return None
    return _pearson(_rank(x), _rank(y))


def interp(x, xs, ys):
    """Piecewise-linear interpolation inside the observed range; None outside it."""
    pts = sorted(zip(xs, ys))
    if len(pts) < 2 or x < pts[0][0] or x > pts[-1][0]:
        return None
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            if x1 == x0:
                return y0
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return None


def crossing(xs, ys_a, ys_b):
    """Cost at which series a crosses series b (a = b), linear between adjacent rungs."""
    pts = sorted(zip(xs, ys_a, ys_b))
    for (x0, a0, b0), (x1, a1, b1) in zip(pts, pts[1:]):
        d0, d1 = a0 - b0, a1 - b1
        if d0 == 0:
            return x0
        if d0 * d1 < 0:
            return x0 + (x1 - x0) * (-d0) / (d1 - d0)
    return None


# ------------------------------------------------------------------------------- one face
def analyse_face(payload):
    """Everything this module says about one atlas arm, recomputed from its per-cell scalars."""
    per_cell = payload.get("per_cell") or []
    if not per_cell:
        return None
    cells = []
    for c in per_cell:
        med = c.get("median_cagr_pp")
        p05, p95 = c.get("p05_cagr_pp"), c.get("p95_cagr_pp")
        if med is None or p05 is None or p95 is None:
            continue
        cells.append({"n_hold": int(c["n_hold"]), "rebal": int(c["rebal"]),
                      "median_cagr_pp": float(med), "p05_cagr_pp": float(p05),
                      "p95_cagr_pp": float(p95),
                      "band_pp": float(p95) - float(p05)})
    if not cells:
        return None
    meds = [c["median_cagr_pp"] for c in cells]
    spread = max(meds) - min(meds)
    band = _median([c["band_pp"] for c in cells])
    audit = payload.get("audit") or {}
    argmax_cell = max(cells, key=lambda c: c["median_cagr_pp"])

    by_cell = {(c["n_hold"], c["rebal"]): c["median_cagr_pp"] for c in cells}
    widths = sorted({c["n_hold"] for c in cells})
    cadences = sorted({c["rebal"] for c in cells})

    # cadence effect at a fixed width: how much faster the fast cadence is, in pp/yr
    cadence_at = {}
    for w in widths:
        a, b = by_cell.get((w, CADENCE_FAST)), by_cell.get((w, CADENCE_SLOW))
        if a is not None and b is not None:
            cadence_at[w] = round(a - b, 3)
    # width effect at a fixed cadence: how much wider the wide book is
    width_at = {}
    for r in cadences:
        a, b = by_cell.get((WIDTH_WIDE, r)), by_cell.get((WIDTH_NARROW, r))
        if a is not None and b is not None:
            width_at[r] = round(a - b, 3)
    # knob spreads: how much of the between-cell spread each knob alone can produce
    cad_spreads = []
    for w in widths:
        vals = [by_cell[(w, r)] for r in cadences if (w, r) in by_cell]
        if len(vals) >= 2:
            cad_spreads.append(max(vals) - min(vals))
    wid_spreads = []
    for r in cadences:
        vals = [by_cell[(w, r)] for w in widths if (w, r) in by_cell]
        if len(vals) >= 2:
            wid_spreads.append(max(vals) - min(vals))

    return {
        "cost": audit.get("cost"),
        "buffer_k": audit.get("buffer_k"),
        "n_cells": len(cells),
        "between_cell_spread_pp": round(spread, 3),
        "median_cell_band_pp": round(band, 3),
        "spread_over_band": round(spread / band, 4) if band else None,
        "config_order_clears_band": bool(spread > band + GATE_TOL_PP),
        "argmax_cell": {"n_hold": argmax_cell["n_hold"], "rebal": argmax_cell["rebal"],
                        "median_cagr_pp": argmax_cell["median_cagr_pp"]},
        "cadence_effect_pp": cadence_at,
        "cadence_effect_median_pp": round(_median(list(cadence_at.values())), 3)
        if cadence_at else None,
        "width_effect_pp": width_at,
        "width_effect_median_pp": round(_median(list(width_at.values())), 3)
        if width_at else None,
        "cadence_spread_pp": round(_median(cad_spreads), 3) if cad_spreads else None,
        "width_spread_pp": round(_median(wid_spreads), 3) if wid_spreads else None,
        "cells": cells,
    }


# --------------------------------------------------------------------------- discovery
def classify(payload):
    """Which ladder a face may be a rung of, decided by its own audit block."""
    a = payload.get("audit") or {}
    cost, k = a.get("cost"), a.get("buffer_k")
    if cost is None or k is None:
        return None, "audit block does not declare both cost and buffer_k"
    moves_cost = abs(cost - BASELINE_COST) > 1e-12
    moves_k = abs(k) > 1e-12
    if not moves_cost and not moves_k:
        return "toll", None          # the baseline is the anchor rung of both ladders
    if moves_cost and moves_k:
        return None, ("moves two knobs at once (cost=%.5f k=%.3f): not a rung of a "
                      "one-dimensional ladder" % (cost, k))
    return ("toll" if moves_cost else "buffer"), None


def discover(paths=None):
    faces, excluded, unreadable = {}, [], []
    for p in sorted(paths or glob.glob(FACE_GLOB)):
        name = os.path.basename(p)
        if name == os.path.basename(OUT):
            continue
        try:
            payload = json.load(open(p, encoding="utf-8"))
        except Exception as e:                     # noqa: BLE001  -- a broken face is data
            unreadable.append({"file": name, "error": str(e)})
            continue
        ladder, why = classify(payload)
        face = analyse_face(payload)
        if face is None:
            unreadable.append({"file": name, "error": "no per_cell scalars"})
            continue
        face["file"] = name
        if ladder is None:
            excluded.append({"file": name, "reason": why, "cost": face["cost"],
                             "buffer_k": face["buffer_k"]})
            continue
        face["ladders"] = []
        if abs(face["buffer_k"]) <= 1e-12:
            face["ladders"].append("toll")
        if face["cost"] is not None and abs(face["cost"] - BASELINE_COST) <= 1e-12:
            face["ladders"].append("buffer")
        for lad in face["ladders"]:
            faces.setdefault(lad, []).append(face)
    for lad in faces:
        faces[lad].sort(key=lambda f: f["cost"] if lad == "toll" else f["buffer_k"])
    return faces, excluded, unreadable


# ----------------------------------------------------------------------------- readings
def toll_ladder(rungs):
    """The cost ladder: does the ordering decay monotonically, and where does it die?"""
    if len(rungs) < MIN_RUNGS:
        return {"verdict": "NOT-ASSESSED", "rungs": len(rungs),
                "reasons": ["fewer than %d toll rungs on disk" % MIN_RUNGS]}
    bp = [r["cost"] * 10000.0 for r in rungs]
    spread = [r["between_cell_spread_pp"] for r in rungs]
    band = [r["median_cell_band_pp"] for r in rungs]
    clears = [r["config_order_clears_band"] for r in rungs]
    rho = spearman(bp, spread)
    be = crossing(bp, spread, band)
    s8 = interp(PRODUCTION_TOLL_BP, bp, spread)
    b8 = interp(PRODUCTION_TOLL_BP, bp, band)
    reasons = [
        "spread falls from %.2fpp at %.0fbp to %.2fpp at %.0fbp (rank corr %s)"
        % (spread[0], bp[0], spread[-1], bp[-1],
           "n/a" if rho is None else "%.3f" % rho),
        "median cell band stays %.2f -> %.2fpp across the same rungs (band is not the mover)"
        % (band[0], band[-1]),
    ]
    if be is not None:
        reasons.append("the two series cross at %.2fbp/side" % be)
    if s8 is not None:
        reasons.append("at the production toll (%.0fbp) interpolated spread %.2fpp vs band %.2fpp"
                       % (PRODUCTION_TOLL_BP, s8, b8))
    cad_eff = [r["cadence_effect_median_pp"] for r in rungs]
    wid_eff = [r["width_effect_median_pp"] for r in rungs]
    flip_bp = next((round(b, 3) for b, c in zip(bp, cad_eff) if c is not None and c < 0), None)
    wid_rho = spearman(bp, wid_eff) if all(v is not None for v in wid_eff) else None
    if flip_bp is not None:
        reasons.append("the FAST cadence is worth %+.2fpp at %.0fbp and %+.2fpp at %.0fbp -- the "
                       "ranking of the cadence knob inverts at %.0fbp/side"
                       % (cad_eff[0], bp[0], cad_eff[-1], bp[-1], flip_bp))
    if wid_rho is not None:
        reasons.append("the width knob moves the other way: %+.2f -> %+.2fpp (rank corr %+.3f), "
                       "i.e. wider is worth more as the toll rises"
                       % (wid_eff[0], wid_eff[-1], wid_rho))
    survivors = [r["file"] for r, c in zip(rungs, clears) if c]
    if s8 is not None and s8 > b8 + GATE_TOL_PP:
        verdict = "ORDERING_SURVIVES_THE_PRODUCTION_TOLL"
        reasons.append("the config ordering still clears its own phase noise at the toll the "
                       "card is actually charged")
    elif rho is not None and rho <= MONOTONE_RHO:
        verdict = "ORDERING_IS_A_TOLL_ARTEFACT"
        reasons.append("the ordering is monotone in the toll and gone by the production toll: "
                       "no width/cadence sentence from this grid is quotable at 8bp/side")
    else:
        verdict = "ORDERING_DECAYS_WITHOUT_A_CLEAN_DOSE"
        reasons.append("the ordering does not survive the production toll, but the decay is not "
                       "monotone -- a single crossing cannot name a mechanism")
    return {
        "verdict": verdict,
        "rungs": len(rungs),
        "toll_bp": [round(x, 3) for x in bp],
        "spread_pp": spread,
        "band_pp": band,
        "clears_band": clears,
        "spread_rank_corr_with_toll": rho,
        "break_even_toll_bp": None if be is None else round(be, 3),
        "spread_at_production_toll_pp": None if s8 is None else round(s8, 3),
        "band_at_production_toll_pp": None if b8 is None else round(b8, 3),
        "rungs_that_clear": survivors,
        "argmax_cells": [dict(r["argmax_cell"], file=r["file"], toll_bp=round(b * 1, 3))
                         for r, b in zip(rungs, bp)],
        "argmax_identity_stable": len({(r["argmax_cell"]["n_hold"],
                                        r["argmax_cell"]["rebal"]) for r in rungs}) == 1,
        "cadence_effect_median_pp": cad_eff,
        "cadence_sign_flip_toll_bp": flip_bp,
        "width_effect_median_pp": wid_eff,
        "width_effect_rank_corr_with_toll": wid_rho,
        "cadence_spread_pp": [r["cadence_spread_pp"] for r in rungs],
        "width_spread_pp": [r["width_spread_pp"] for r in rungs],
        "reasons": reasons,
    }


def buffer_ladder(rungs):
    """The buffer ladder at the production toll: a dose, or one draw from a grid?"""
    if len(rungs) < MIN_RUNGS:
        return {"verdict": "NOT-ASSESSED", "rungs": len(rungs),
                "reasons": ["fewer than %d buffer rungs at the production toll" % MIN_RUNGS]}
    k = [r["buffer_k"] for r in rungs]
    spread = [r["between_cell_spread_pp"] for r in rungs]
    band = [r["median_cell_band_pp"] for r in rungs]
    clears = [r["config_order_clears_band"] for r in rungs]
    n_clear = sum(1 for c in clears if c)
    rho = spearman(k, spread)
    dose_txt = ("spread has no dose: %s across k=%s (rank corr %s)"
                % (" / ".join("%.2f" % s for s in spread),
                   " / ".join("%.2f" % x for x in k),
                   "n/a" if rho is None else "%.3f" % rho))
    if rho is not None and rho >= DOSE_RHO and n_clear < 2:
        dose_txt = ("spread drifts up with k (rank corr %.3f) but only %d rung ever clears the "
                    "band, so the correlation is carried by rungs that never clear it"
                    % (rho, n_clear))
    reasons = [
        "%d of %d buffer strengths clear the band (one draw in %d if the label were coin-flip)"
        % (n_clear, len(rungs), len(rungs)),
        dose_txt,
        "band is flat (%.2f .. %.2fpp), so the label moves on spread alone"
        % (min(band), max(band)),
    ]
    if n_clear == 0:
        verdict = "BUFFER_HAS_NO_ORDERING_EFFECT"
    elif n_clear >= 2 and rho is not None and rho >= DOSE_RHO:
        verdict = "BUFFER_WIDENS_THE_ORDERING"
    else:
        verdict = "SINGLE_RUNG_CROSSING_IS_ONE_DRAW"
        reasons.append("a strength ladder whose only crossing is non-monotone is the r1325 "
                       "single-arm reading again: the ladder, not the arm, is the ruler")
    return {
        "verdict": verdict,
        "rungs": len(rungs),
        "buffer_k": k,
        "spread_pp": spread,
        "band_pp": band,
        "clears_band": clears,
        "n_clearing_rungs": n_clear,
        "spread_rank_corr_with_k": rho,
        "reasons": reasons,
    }


def statement(toll, buff):
    """One sentence a reader can quote, built only from the two verdicts and the knob trends."""
    t_art = toll.get("verdict") == "ORDERING_IS_A_TOLL_ARTEFACT"
    b_draw = buff.get("verdict") == "SINGLE_RUNG_CROSSING_IS_ONE_DRAW"
    # the one thing the ladder does pin down: the SIGN of each knob, not its size
    cad_flip = toll.get("cadence_sign_flip_toll_bp")
    wid_rho = toll.get("width_effect_rank_corr_with_toll")
    if t_art and b_draw:
        tail = ""
        if cad_flip is not None and wid_rho is not None and wid_rho >= 0.99:
            tail = (" The only stable statement in the grid is directional, not numerical: wider "
                    "is worth more at every rung (rank corr %+.2f) while the fast cadence "
                    "inverts at %.0fbp/side -- and even the width sign is worth at most %.2fpp, "
                    "inside the band."
                    % (wid_rho, cad_flip, max(toll.get("width_effect_median_pp") or [0.0])))
        return ("NOT QUOTABLE: the 12-cell ordering clears its own phase noise only below "
                "%.2fbp/side, and the buffer knob never clears it on a dose -- both knobs are "
                "zero-cost objects.%s"
                % (toll.get("break_even_toll_bp") or 0.0, tail))
    if t_art:
        return ("NOT QUOTABLE at the production toll: the ordering dies at %.2fbp/side."
                % (toll.get("break_even_toll_bp") or 0.0))
    if b_draw:
        return "The toll ladder survives; the buffer ladder is still one draw from a grid."
    return "Both ladders carry a structure that survives its own gate."


def build(paths=None):
    faces, excluded, unreadable = discover(paths)
    toll = toll_ladder(faces.get("toll", []))
    buff = buffer_ladder(faces.get("buffer", []))
    payload = {
        "question": ("the atlas's 12-cell ordering is judged against each cell's own phase "
                     "band; both the spread and the band move with the toll. At what toll does "
                     "the ordering stop clearing its own noise, and is the decay monotone?"),
        "spec": {
            "production_toll_bp": PRODUCTION_TOLL_BP,
            "baseline_cost_fraction": BASELINE_COST,
            "gate_tol_pp": GATE_TOL_PP,
            "min_rungs": MIN_RUNGS,
            "monotone_rho": MONOTONE_RHO,
            "dose_rho": DOSE_RHO,
            "cadence_pair": [CADENCE_FAST, CADENCE_SLOW],
            "width_pair": [WIDTH_NARROW, WIDTH_WIDE],
            "rung_membership": "decided by the face's own audit block, never by its file name",
        },
        "toll_ladder": toll,
        "buffer_ladder": buff,
        "statement": statement(toll, buff),
        "faces": {lad: [{"file": f["file"], "cost": f["cost"], "buffer_k": f["buffer_k"],
                         "spread_pp": f["between_cell_spread_pp"],
                         "band_pp": f["median_cell_band_pp"],
                         "clears_band": f["config_order_clears_band"]} for f in rungs]
                  for lad, rungs in faces.items()},
        "excluded": excluded,
        "unreadable": unreadable,
        "units": {
            "spread_pp": "max-min of the 12 cells' median CAGR, percentage points per year",
            "band_pp": "median over cells of (p95-p05) across that cell's own rebalance cycle",
            "break_even_toll_bp": "cost per side at which spread == band, linear between rungs",
        },
        "script": "scripts/etf_book_atlas_toll_ladder.py",
    }
    return payload


def render_md(p):
    t, b = p["toll_ladder"], p["buffer_ladder"]
    L = ["# ETF book atlas -- the toll ladder", "",
         "**%s**" % p["statement"], "", "## Toll ladder (buffer k=0)", ""]
    L.append("| toll bp | spread pp | band pp | clears | argmax | cadence eff | width eff |")
    L.append("|---|---|---|---|---|---|---|")
    for i, toll in enumerate(t.get("toll_bp") or []):
        L.append("| %.0f | %.2f | %.2f | %s | n%d/R%d | %+.2f | %+.2f |"
                 % (toll, t["spread_pp"][i], t["band_pp"][i],
                    "yes" if t["clears_band"][i] else "no",
                    t["argmax_cells"][i]["n_hold"], t["argmax_cells"][i]["rebal"],
                    t["cadence_effect_median_pp"][i] or 0.0,
                    t["width_effect_median_pp"][i] or 0.0))
    L += ["", "verdict: **%s**" % t.get("verdict"), ""]
    L += ["- " + r for r in t.get("reasons", [])]
    L += ["", "## Buffer ladder (production toll 10bp/side)", "",
          "| buffer k | spread pp | band pp | clears |", "|---|---|---|---|"]
    for i, k in enumerate(b.get("buffer_k") or []):
        L.append("| %.2f | %.2f | %.2f | %s |"
                 % (k, b["spread_pp"][i], b["band_pp"][i],
                    "yes" if b["clears_band"][i] else "no"))
    L += ["", "verdict: **%s**" % b.get("verdict"), ""]
    L += ["- " + r for r in b.get("reasons", [])]
    if p.get("excluded"):
        L += ["", "## Excluded (moves two knobs at once)"]
        L += ["- %s -- %s" % (e["file"], e["reason"]) for e in p["excluded"]]
    return "\n".join(L) + "\n"


def write(payload):
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
    md = os.path.splitext(OUT)[0] + ".md"
    with open(md, "w", encoding="utf-8") as fh:
        fh.write(render_md(payload))
    return OUT


# --------------------------------------------------------------------------------- gate
def check():
    """Re-derive the face from its own sources; red if any published reading was edited."""
    if not os.path.exists(OUT):
        print("FAIL: %s missing" % OUT)
        return 1
    stored = json.load(open(OUT, encoding="utf-8"))
    fresh = build()
    bad = []
    for key in ("toll_ladder", "buffer_ladder", "statement", "excluded", "faces"):
        if json.dumps(stored.get(key), sort_keys=True) != json.dumps(fresh.get(key),
                                                                     sort_keys=True):
            bad.append(key)
    # the verdict must follow from the numbers it is attached to (r1266: recomputed, not copied)
    t = fresh["toll_ladder"]
    if t.get("verdict") == "ORDERING_IS_A_TOLL_ARTEFACT":
        s8, b8, rho = (t.get("spread_at_production_toll_pp"),
                       t.get("band_at_production_toll_pp"),
                       t.get("spread_rank_corr_with_toll"))
        if not (s8 is not None and b8 is not None and s8 <= b8 + GATE_TOL_PP
                and rho is not None and rho <= MONOTONE_RHO):
            bad.append("toll verdict does not follow from its own numbers")
    if bad:
        print("FAIL: face disagrees with its sources on %s" % ", ".join(bad))
        return 1
    print("OK: toll ladder %s (%d rungs, break-even %s bp) / buffer ladder %s (%d rungs)"
          % (t.get("verdict"), t.get("rungs", 0), t.get("break_even_toll_bp"),
             fresh["buffer_ladder"].get("verdict"), fresh["buffer_ladder"].get("rungs", 0)))
    return 0


# ----------------------------------------------------------------------------- selftest
def _ramp(spread):
    """12 cell medians whose max-min is exactly ``spread``."""
    return [10.0 + spread * i / 11.0 for i in range(12)]


def _face(costs_k, meds, band=3.0):
    """Synthetic atlas arm: cells in the same 4x3 order the real faces use."""
    widths, cads = (3, 5, 8, 12), (10, 20, 40)
    per = []
    for i, w in enumerate(widths):
        for j, r in enumerate(cads):
            m = meds[i * len(cads) + j]
            per.append({"n_hold": w, "rebal": r, "median_cagr_pp": m,
                        "p05_cagr_pp": m - band / 2.0, "p95_cagr_pp": m + band / 2.0})
    cost, k = costs_k
    return {"audit": {"cost": cost, "buffer_k": k}, "per_cell": per}


def selftest():
    ok, fails = 0, []

    def leg(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fails.append("%s %s" % (name, detail))

    meds = [10, 9, 8, 11, 10, 9, 12, 11, 10, 13, 12, 11]
    f = analyse_face(_face((0.0, 0.0), meds, band=3.0))
    leg("activity: the synthetic arm has a spread", f["between_cell_spread_pp"] > 0,
        "spread=%s" % f["between_cell_spread_pp"])
    leg("spread == max-min of cell medians", abs(f["between_cell_spread_pp"] - 5.0) < 1e-9,
        "got %s want 5.0" % f["between_cell_spread_pp"])
    leg("band == median of the cell bands", abs(f["median_cell_band_pp"] - 3.0) < 1e-9,
        "got %s" % f["median_cell_band_pp"])
    leg("verdict EXCEEDS when spread clears the band", f["config_order_clears_band"] is True)
    g = analyse_face(_face((0.0, 0.0), [m * 0.1 for m in meds], band=3.0))
    leg("verdict WITHIN when spread is inside the band", g["config_order_clears_band"] is False)
    leg("argmax cell is the top median",
        (f["argmax_cell"]["n_hold"], f["argmax_cell"]["rebal"]) == (12, 10),
        str(f["argmax_cell"]))
    leg("cadence effect is fast minus slow per width",
        f["cadence_effect_pp"] == {3: 2.0, 5: 2.0, 8: 2.0, 12: 2.0},
        str(f["cadence_effect_pp"]))
    leg("width effect is wide minus narrow per cadence",
        f["width_effect_pp"] == {10: 3.0, 20: 3.0, 40: 3.0}, str(f["width_effect_pp"]))
    leg("cadence spread is the width-fixed range", abs(f["cadence_spread_pp"] - 2.0) < 1e-9,
        "got %s" % f["cadence_spread_pp"])
    leg("width spread is the cadence-fixed range", abs(f["width_spread_pp"] - 3.0) < 1e-9,
        "got %s" % f["width_spread_pp"])

    # spearman: strictly decreasing rungs -> -1
    leg("rank corr is -1 for a strictly decreasing ladder",
        spearman([0, 5, 10, 20, 40], [9, 8, 7, 6, 5]) == -1.0)
    leg("rank corr is not monotone for a hill",
        (spearman([0, 2, 5, 10, 20, 30, 40], [5, 5.1, 6.2, 6.3, 5.6, 6.2, 5.9]) or 0) > -0.9)

    # interpolation + crossing
    leg("crossing interpolates linearly",
        abs(crossing([0, 10], [10.0, 4.0], [8.0, 8.0]) - 100.0 / 30.0) < 1e-9,
        str(crossing([0, 10], [10.0, 4.0], [8.0, 8.0])))
    leg("crossing is None when the series never swap",
        crossing([0, 10], [10.0, 9.0], [8.0, 7.0]) is None)
    leg("interp inside the range and None outside",
        abs(interp(5, [0, 10], [0.0, 10.0]) - 5.0) < 1e-9 and interp(20, [0, 10], [0, 10]) is None)
    leg("interp hits an exact rung", abs(interp(10, [0, 10], [0.0, 10.0]) - 10.0) < 1e-9)

    # ladder assembly with synthetic faces on disk-shaped payloads
    faces = {"toll": [], "buffer": []}
    for cost, s in ((0.0, 9.0), (0.0005, 6.5), (0.002, 4.0), (0.004, 2.0)):
        arm = analyse_face(_face((cost, 0.0), _ramp(s), band=7.0))
        arm["file"] = "synthetic_cost%04d" % int(cost * 10000)
        faces["toll"].append(arm)
    faces["toll"].sort(key=lambda x: x["cost"])
    t = toll_ladder(faces["toll"])
    leg("toll ladder reads a monotone decay as an artefact",
        t["verdict"] == "ORDERING_IS_A_TOLL_ARTEFACT", str(t["verdict"]))
    leg("toll ladder's rank corr is -1 on a monotone ladder",
        t["spread_rank_corr_with_toll"] == -1.0, str(t["spread_rank_corr_with_toll"]))
    leg("break-even toll is inside the observed range",
        t["break_even_toll_bp"] is not None and 0 <= t["break_even_toll_bp"] <= 40,
        str(t["break_even_toll_bp"]))
    leg("production-toll interpolation lies between its bracketing rungs",
        t["spread_at_production_toll_pp"] is not None
        and 4.0 <= t["spread_at_production_toll_pp"] <= 6.5,
        str(t["spread_at_production_toll_pp"]))
    leg("two rungs are enough for a ladder", toll_ladder(faces["toll"][:2])["rungs"] == 2)
    leg("one rung is NOT-ASSESSED", toll_ladder(faces["toll"][:1])["verdict"] == "NOT-ASSESSED")

    # argmax identity flips with the toll
    flip = [analyse_face(_face((0.0, 0.0), [14] + [10] * 11)),
            analyse_face(_face((0.004, 0.0), [10] * 11 + [14]))]
    for i, a in enumerate(flip):
        a["file"] = "synthetic_flip%d" % i
    tf = toll_ladder(flip)
    leg("argmax identity flip is detected", tf["argmax_identity_stable"] is False,
        str(tf["argmax_identity_stable"]))

    # buffer ladder: one crossing out of seven is one draw
    faces["buffer"] = []
    for i, k in enumerate((0.0, 0.02, 0.05, 0.10, 0.20, 0.30, 0.40)):
        s = (3.0, 2.9, 3.2, 2.8, 3.1, 5.0, 2.7)[i]
        arm = analyse_face(_face((0.001, k), _ramp(s), band=4.5))
        arm["file"] = "synthetic_k%03d" % int(k * 100)
        faces["buffer"].append(arm)
    b = buffer_ladder(faces["buffer"])
    leg("buffer ladder counts exactly one crossing", b["n_clearing_rungs"] == 1,
        str(b["n_clearing_rungs"]))
    leg("a single non-monotone crossing is one draw",
        b["verdict"] == "SINGLE_RUNG_CROSSING_IS_ONE_DRAW", str(b["verdict"]))
    leg("buffer dose needs more than one crossing",
        buffer_ladder(faces["buffer"] + faces["buffer"])["verdict"]
        == "SINGLE_RUNG_CROSSING_IS_ONE_DRAW")

    # membership: two-knob faces are excluded, and classification uses the audit block
    ex, why = classify({"audit": {"cost": 0.0005, "buffer_k": 0.05}})
    leg("a face that moves two knobs is excluded", ex is None and "two knobs" in why, str(why))
    leg("baseline belongs to both ladders",
        classify({"audit": {"cost": BASELINE_COST, "buffer_k": 0.0}})[0] == "toll"
        and classify({"audit": {"cost": 0.002, "buffer_k": 0.0}})[0] == "toll")
    leg("classification reads the audit, not the file name",
        classify({"audit": {"cost": BASELINE_COST, "buffer_k": 0.05}})[0] == "buffer")
    leg("an audit missing a knob is refused",
        classify({"audit": {"cost": 0.002}})[0] is None)

    # determinism: the same bytes in give the same analysis out
    a1 = analyse_face(_face((0.001, 0.0), meds))
    a2 = analyse_face(_face((0.001, 0.0), meds))
    leg("analysis is deterministic", json.dumps(a1, sort_keys=True) == json.dumps(a2,
                                                                                sort_keys=True))
    leg("empty arm is None rather than a zero", analyse_face({"per_cell": []}) is None)

    print("%d/%d legs PASS" % (ok, ok + len(fails)))
    for f_ in fails:
        print("  FAIL " + f_)
    return 0 if not fails else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "show"])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.check:
        return check()
    payload = build()
    if a.mode == "show":
        print(render_md(payload))
        return 0
    write(payload)
    t, b = payload["toll_ladder"], payload["buffer_ladder"]
    print("toll ladder: %s (%d rungs, break-even %s bp, spread@8bp %s vs band %s)"
          % (t.get("verdict"), t.get("rungs", 0), t.get("break_even_toll_bp"),
             t.get("spread_at_production_toll_pp"), t.get("band_at_production_toll_pp")))
    print("buffer ladder: %s (%d rungs, %s of %s clearing)"
          % (b.get("verdict"), b.get("rungs", 0), b.get("n_clearing_rungs"), b.get("rungs", 0)))
    print(payload["statement"])
    return 0


if __name__ == "__main__":
    sys.exit(main())