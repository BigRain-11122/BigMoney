"""Three arms of the phase atlas, judged against the ruler the atlas built.

r1350 priced the production cell grid on every decision origin of its own cycle and found the
between-cell spread (5.22pp) sitting inside the median cell band (6.68pp). That face left two
questions the pool holds as ready work (entered by bm-c r1350):

  * E256-PHASE-ATLAS-BUFFER-K05 -- r1325 rejected buffer k=0.05 on ONE decision calendar over
    5 books x 4 phases (-0.145pp median). If a 0.145pp effect cannot be separated from a
    2.8-7.9pp band, that REJECT was never a measurement. Price the same arm where the noise
    was measured: per cell, and report the share of cells that clear their own band.
  * E256-PHASE-ATLAS-COST05 / COST20 -- the cadence conclusion (R10 quotable, R40 not) is a
    path-dependence claim, so it must NOT depend on the toll. Bracketing the production 10bp
    with 5bp and 20bp answers whether "the band" is a property of the decision count or of the
    cost level in disguise.

This module does not re-run any engine. It reads four already-published faces and applies one
frozen rule. The rule is written here, before the first read, and echoed into the payload, so a
later "small adjustment" cannot pass for the same rule (the E188 line).

Usage:
  python scripts/etf_book_phase_atlas_arms.py run
  python scripts/etf_book_phase_atlas_arms.py --check      # gate: published face vs a re-derivation
  python scripts/etf_book_phase_atlas_arms.py --selftest
"""

from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
OUT_JSON = os.path.join(RES, "etf_book_phase_atlas_arms.json")

BASE = os.path.join(RES, "etf_book_phase_atlas.json")
ARMS = {
    "buffer_k05": (os.path.join(RES, "etf_book_phase_atlas_buffer_k05.json"),
                   "buffer k=0.05 on every cell (the r1325 arm, re-priced per phase)"),
    "cost05": (os.path.join(RES, "etf_book_phase_atlas_cost05.json"),
               "5bp/side on the whole grid (half the production toll)"),
    "cost20": (os.path.join(RES, "etf_book_phase_atlas_cost20.json"),
               "20bp/side on the whole grid (double the production toll)"),
    "cost40": (os.path.join(RES, "etf_book_phase_atlas_cost40.json"),
               "40bp/side on the whole grid (4x the production toll -- does 'the cadence is "
               "quotable' have a toll ceiling, and does the ordering vanish first?)"),
    "buffer_k10": (os.path.join(RES, "etf_book_phase_atlas_buffer_k10.json"),
                   "buffer k=0.10 on every cell (the middle of the family r1325 named as a cost "
                   "knob; declared in the pool at r1351 before this face existed)"),
    "buffer_k20": (os.path.join(RES, "etf_book_phase_atlas_buffer_k20.json"),
                   "buffer k=0.20 on every cell (the strongest arm -- if even this stays inside "
                   "every cell's band, the buffer family is unmeasurable on this design, not "
                   "negative)"),
    # r1353: the three rows r1352 stocked, read back by the same rule. The first three buffer
    # arms all landed inside their bands, so 'flat' was a claim about the middle of an axis
    # nobody had measured the ends of.
    "buffer_k02": (os.path.join(RES, "etf_book_phase_atlas_buffer_k02.json"),
                   "buffer k=0.02 on every cell (the near-zero end -- a knob that reads the same "
                   "at 0.02 and at 0.20 is flat, not merely small)"),
    "buffer_k40": (os.path.join(RES, "etf_book_phase_atlas_buffer_k40.json"),
                   "buffer k=0.40 on every cell (8x the r1325 arm -- the far end, where a real "
                   "buffer finally has to hurt)"),
    "buffer_k05_cost20": (os.path.join(RES, "etf_book_phase_atlas_buffer_k05_cost20.json"),
                          "buffer k=0.05 at 20bp/side -- the interaction neither family tested: "
                          "does a buffer that is harmless at 10bp recover any of the -1.41pp the "
                          "20bp toll costs?"),
}

# the knob each arm declares in its own name; the face must carry the same number (a face wired
# to the wrong arm would otherwise publish the other arm's numbers under this name)
DECLARED = {
    "buffer_k05": {"buffer_k": 0.05},
    "buffer_k10": {"buffer_k": 0.10},
    "buffer_k20": {"buffer_k": 0.20},
    "cost05": {"cost": 0.0005},
    "cost20": {"cost": 0.002},
    "cost40": {"cost": 0.004},
    "buffer_k02": {"buffer_k": 0.02},
    "buffer_k40": {"buffer_k": 0.40},
    "buffer_k05_cost20": {"buffer_k": 0.05, "cost": 0.002},
}

# ---- the frozen rule (written before the first read; echoed into the payload) -------------
CRITERIA = {
    "cagr_share_min": 0.8,          # share of cells whose median CAGR is not worse than base
    "cagr_floor_pp": -0.15,         # a cell counts as "not worse" if delta >= this
    "median_delta_floor_pp": -0.05,  # the arm's median per-cell delta must clear this
    "resolvable_share_min": 0.5,    # share of cells whose |delta| exceeds their own band
    "activity_min_cells": 12,       # every grid cell must be judged, else nothing is claimable
    "cadence_ratio_min": 1.0,       # R40 band / R10 band must stay above this at every toll
    "band_shift_tol": 0.25,         # the median band may not move more than this vs baseline
    "frozen": ("constants above were written before the first read of any arm face; the selftest "
               "recomputes every published verdict from the summary by this rule"),
}


def face(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def cells_of(f):
    out = {}
    for c in f["per_cell"]:
        out[(c["n_hold"], c["rebal"])] = c
    return out


def band_pp(c):
    return c["p95_cagr_pp"] - c["p05_cagr_pp"]


def band_by_cadence(f):
    """Median band per rebalance cadence -- the quantity the cost arms are actually about."""
    groups = {}
    for c in f["per_cell"]:
        groups.setdefault(c["rebal"], []).append(band_pp(c))

    def med(a):
        a = sorted(a)
        return a[len(a) // 2] if len(a) % 2 else (a[len(a) // 2 - 1] + a[len(a) // 2]) / 2.0

    return {k: round(med(v), 3) for k, v in sorted(groups.items())}


def judge_bands(arm_bands, base_bands):
    """Frozen rule for the cost arms: the band is a property of the decision count, not the toll.

    Two things must hold at every cost level: the long cadence must carry the wider band
    (R40/R10 ratio > 1), and the median band must not move by more than the tolerance against
    the baseline. A wipeout of either is the toll talking, not path dependence.
    """
    r10 = arm_bands.get(10)
    r40 = arm_bands.get(40)
    if r10 is None or r40 is None:
        return "NOT-ASSESSED", ["a cost arm is missing an R10 or R40 cadence"]
    ratio = r40 / r10 if r10 else 0.0
    base_all = sorted([base_bands[10], base_bands[20], base_bands[40]])[1]
    arm_all = sorted([arm_bands[10], arm_bands[20], arm_bands[40]])[1]
    shift = (arm_all - base_all) / base_all if base_all else 0.0
    reasons = [
        "R40/R10 band ratio %.3f (must exceed %.2f)" % (ratio, CRITERIA["cadence_ratio_min"]),
        "median band %+.2fpp vs baseline (%+.1f%%, tolerance %.0f%%)" % (
            arm_all - base_all, 100 * shift, 100 * CRITERIA["band_shift_tol"]),
    ]
    if ratio <= CRITERIA["cadence_ratio_min"] or abs(shift) > CRITERIA["band_shift_tol"]:
        return "BAND_FOLLOWS_THE_TOLL", reasons
    return "CADENCE_BAND_SURVIVES_THE_TOLL", reasons


def judge(rows):
    """The frozen decision rule. Returns (label, reasons)."""
    n = len(rows)
    worse = [r for r in rows if r["delta_pp"] < CRITERIA["cagr_floor_pp"]]
    share = (n - len(worse)) / n if n else 0.0
    deltas = sorted(r["delta_pp"] for r in rows)
    med = deltas[len(deltas) // 2] if len(deltas) % 2 else (
        deltas[len(deltas) // 2 - 1] + deltas[len(deltas) // 2]) / 2.0 if deltas else 0.0
    resolvable = [r for r in rows if abs(r["delta_pp"]) > r["band_pp"]]
    res_share = len(resolvable) / n if n else 0.0
    reasons = [
        "cells %d/%d judged" % (n, CRITERIA["activity_min_cells"]),
        "not-worse share %.3f (floor %.2f, cell floor %.2fpp)" % (
            share, CRITERIA["cagr_share_min"], CRITERIA["cagr_floor_pp"]),
        "median per-cell delta %+.3fpp (floor %+.2fpp)" % (med, CRITERIA["median_delta_floor_pp"]),
        "resolvable share %.3f (|delta| > the cell's own band; floor %.2f)" % (
            res_share, CRITERIA["resolvable_share_min"]),
    ]
    if n < CRITERIA["activity_min_cells"]:
        return "NOT-ASSESSED", reasons
    if share < CRITERIA["cagr_share_min"] or med < CRITERIA["median_delta_floor_pp"]:
        return "REJECT", reasons
    if res_share < CRITERIA["resolvable_share_min"]:
        # the arm is not worse, but its effect is inside the design's own noise: that is a
        # statement about the ruler, not an adoption licence
        return "NOT-SEPARABLE", reasons
    return "ADOPT", reasons


def build():
    base = face(BASE)
    bcells = cells_of(base)
    base_bands = band_by_cadence(base)
    payload = {
        "script": "scripts/etf_book_phase_atlas_arms.py",
        "question": ("do the follow-ups the atlas left behind (buffer k=0.05 / 0.10 / 0.20, cost "
                     "5bp / 20bp / 40bp) change the reading when they are judged per cell against "
                     "each cell's own band?"),
        "units": {"delta_pp": "percentage points of median CAGR, arm minus the SAME cell at the "
                              "baseline (10bp/side, buffer k=0)",
                  "band_pp": "p95-p05 of a cell's CAGR over its own decision origins"},
        "criteria": CRITERIA,
        "baseline": {"face": base["face"], "evidence_cutoff": base["evidence_cutoff"],
                     "audit": base["audit"], "grid_between_cell_spread_pp":
                         base["grid"]["between_cell_spread_pp"],
                     "median_cell_band_pp": base["grid"]["median_cell_band_pp"]},
        "arms": {},
    }
    for name, (path, desc) in ARMS.items():
        f = face(path)
        rows = []
        for (nh, rb), c in sorted(cells_of(f).items()):
            b = bcells[(nh, rb)]
            rows.append({
                "n_hold": nh, "rebal": rb,
                "median_cagr_pp": c["median_cagr_pp"],
                "baseline_cagr_pp": b["median_cagr_pp"],
                "delta_pp": round(c["median_cagr_pp"] - b["median_cagr_pp"], 3),
                "band_pp": round(band_pp(c), 3),
                "baseline_band_pp": round(band_pp(b), 3),
                "median_sharpe": c["median_sharpe"],
                "baseline_sharpe": b["median_sharpe"],
                "phases": c["phases"],
            })
        label, reasons = judge(rows)
        bands = sorted(r["band_pp"] for r in rows)
        arm_bands = band_by_cadence(f)
        entry = {
            "description": desc,
            "face": os.path.relpath(path, ROOT).replace("\\", "/"),
            "evidence_cutoff": f["evidence_cutoff"],
            "audit": f["audit"],
            "rows": rows,
            "median_band_pp": round(bands[len(bands) // 2], 3),
            "band_by_cadence": arm_bands,
            "verdict": label,
            "verdict_reasons": reasons,
        }
        if name.startswith("cost"):
            # the cost arms are about the band, not about beating the baseline's returns
            band_label, band_reasons = judge_bands(arm_bands, base_bands)
            entry["band_verdict"] = band_label
            entry["band_verdict_reasons"] = band_reasons
        payload["arms"][name] = entry
    return payload


# ---- r1354: the resolution floor of the buffer axis -- a size, not a direction ------------
FLOOR_OUT = os.path.join(RES, "etf_book_buffer_resolution_floor.json")
BUFFER_ARMS = {"buffer_k02": 0.02, "buffer_k05": 0.05, "buffer_k10": 0.10,
               "buffer_k20": 0.20, "buffer_k40": 0.40}
FLOOR_RULE = {
    # buffer k is the share of a target weight change the book trades per rebalance, so the
    # axis ENDS at 1.0 ("trade the whole move the moment the signal moves") and k>1.0 has no
    # meaning. A requirement past that end is unreachable by construction, not untested --
    # which is the difference between "we have not looked" and "there is nothing there".
    "degenerate_k": 1.0,
    "min_points": 4,
    "sweep_band_share_max": 0.25,   # the whole axis should span a small share of the ruler
    "frozen": ("written before the first read of the floor: the axis is fitted linearly on the "
               "published medians and the answer is a k, which only means anything inside [0,1]"),
}


def _median(a):
    a = sorted(a)
    n = len(a)
    return a[n // 2] if n % 2 else (a[n // 2 - 1] + a[n // 2]) / 2.0


def _ols(points):
    """Least squares y = intercept + slope*x -> (slope, intercept, r2). Pure function."""
    n = len(points)
    mx = sum(p[0] for p in points) / n
    my = sum(p[1] for p in points) / n
    sxx = sum((p[0] - mx) ** 2 for p in points)
    sxy = sum((p[0] - mx) * (p[1] - my) for p in points)
    slope = sxy / sxx if sxx else 0.0
    inter = my - slope * mx
    ss_tot = sum((p[1] - my) ** 2 for p in points)
    ss_res = sum((p[1] - (inter + slope * p[0])) ** 2 for p in points)
    return slope, inter, (1.0 - ss_res / ss_tot if ss_tot else 0.0)


def floor_of(payload):
    """How strong would k have to be for THIS design's ruler to register it? Pure function.

    The five buffer arms are five settings of one knob, so the published medians are a curve
    and the curve has a slope. The ruler is the baseline grid's median cell band (the atlas
    already showed the band follows the decision count, not the toll). The answer is the k at
    which the median effect would equal the band -- and a k above 1.0 is not a big buffer, it
    is refusing to trade at all.
    """
    base_band = payload["baseline"]["median_cell_band_pp"]
    pts, arms = [], {}
    for name, k in sorted(BUFFER_ARMS.items(), key=lambda kv: kv[1]):
        a = payload["arms"].get(name)
        if not a:
            continue
        rows = a["rows"]
        d = _median([r["delta_pp"] for r in rows])
        res = sum(1 for r in rows if abs(r["delta_pp"]) > r["band_pp"]) / float(len(rows))
        arms[name] = {"buffer_k": k, "median_delta_pp": round(d, 3),
                      "median_band_pp": a["median_band_pp"],
                      "resolvable_share": round(res, 3), "verdict": a["verdict"]}
        pts.append((k, d))
    out = {"script": "scripts/etf_book_phase_atlas_arms.py --floor",
           "question": ("the buffer family retired as 'unmeasurable at every strength'. Turn that "
                        "direction into a size: how strong would k have to be for this ruler to "
                        "register it, and is that strength still a buffer?"),
           "units": {"k": "share of a target weight change traded per rebalance (1.0 = trade the "
                          "whole move at once, the axis end)",
                     "slope_pp_per_k": "pp of median CAGR per unit k",
                     "ruler_pp": "the baseline grid's median per-cell band (p95-p05)"},
           "evidence_cutoff": payload["baseline"]["evidence_cutoff"],
           "rule": FLOOR_RULE, "ruler_pp": base_band, "arms": arms}
    reasons = ["%d buffer arms on the axis (need >= %d, or the slope is one point)"
               % (len(pts), FLOOR_RULE["min_points"])]
    if len(pts) < FLOOR_RULE["min_points"]:
        out.update({"fit": None, "k_required": None, "verdict": "NOT-ASSESSED",
                    "verdict_reasons": reasons})
        return out
    # the k=0 point is the baseline itself, whose median delta is zero BY DEFINITION: an
    # identity anchor, not a sixth experiment, and it is named as one wherever it is used
    slope, inter, r2 = _ols([(0.0, 0.0)] + pts)
    k_req = (base_band - inter) / slope if slope > 0 else None
    sweep = pts[-1][1] - pts[0][1]
    share = sweep / base_band if base_band else 0.0
    reasons = [
        "slope %+.3fpp per unit k, r2 %.3f on %d arms + the k=0 identity"
        % (slope, r2, len(pts)),
        "ruler = baseline median cell band %.2fpp (a median effect that size is the floor)"
        % base_band,
        "k required to reach the floor = %s"
        % ("n/a (the axis does not rise)" if k_req is None else "%.2f" % k_req),
        "the whole axis spans %.3fpp = %.3f of the ruler (flag if >= %.2f)"
        % (sweep, share, FLOOR_RULE["sweep_band_share_max"]),
    ]
    if k_req is None:
        label = "UNREACHABLE_BY_CONSTRUCTION"
        reasons.append("no measured strength rises with k, so no strength reaches the ruler")
    elif k_req > FLOOR_RULE["degenerate_k"]:
        label = "UNREACHABLE_BY_CONSTRUCTION"
        reasons.append("k=%.2f sits past k=%.0f, which is 'never trade': this design cannot "
                       "resolve the axis at any setting that is still a buffer"
                       % (k_req, FLOOR_RULE["degenerate_k"]))
    else:
        label = "REACHABLE_DECLARE_A_RUN"
        reasons.append("k=%.2f is inside the axis: declare a run there instead of extrapolating "
                       "into it" % k_req)
    out.update({"fit": {"slope_pp_per_k": round(slope, 4), "intercept_pp": round(inter, 4),
                        "r2": round(r2, 4), "n_points": len(pts) + 1,
                        "anchor": "k=0 (identity: the baseline's own delta is 0.0)"},
                "k_required": None if k_req is None else round(k_req, 3),
                "sweep_span_pp": round(sweep, 3),
                "sweep_share_of_ruler": round(share, 4),
                "verdict": label, "verdict_reasons": reasons})
    return out


def build_floor():
    return floor_of(build())


def floor_check():
    """Gate: the published floor must equal a re-derivation. Same two red states as check()."""
    if not os.path.exists(FLOOR_OUT):
        print("floor is stale: no published floor face at %s" % _rel(FLOOR_OUT))
        return 2
    pub = face(FLOOR_OUT)
    if pub.get("rule") != FLOOR_RULE:
        print("floor is inconsistent: the published rule is not the rule in this file")
        return 1
    rebuilt = json.loads(json.dumps(build_floor()))
    drift = _diff(pub, rebuilt)
    if not drift:
        print("floor face matches its own sources on cutoff %s: %s (k required %s)"
              % (rebuilt["evidence_cutoff"], rebuilt["verdict"], rebuilt["k_required"]))
        return 0
    src = [BASE] + [p for p, _ in ARMS.values()]
    try:
        face_mtime = os.path.getmtime(FLOOR_OUT)
    except OSError:
        face_mtime = 0.0
    newer = [os.path.basename(p) for p in src if os.path.getmtime(p) > face_mtime + 1.0]
    if newer:
        print("floor is stale: priced on cutoff %r while its sources moved (%s)"
              % (pub.get("evidence_cutoff"), ",".join(sorted(newer))[:160]))
        return 2
    print("floor is inconsistent: %d field(s) disagree with a re-derivation and no source moved: %s"
          % (len(drift), "; ".join(drift)[:300]))
    return 1


def render_floor_md(p):
    L = ["# Buffer axis resolution floor (r1354 bm-c)\n",
         "Face: `results/etf_book_buffer_resolution_floor.json`; script: "
         "`scripts/etf_book_phase_atlas_arms.py --floor`; cutoff %s.\n" % p["evidence_cutoff"],
         "The family retired as 'unmeasurable at every strength'. This face is the size of that "
         "sentence.\n",
         "| arm | k | median delta | median band | resolvable share | label |",
         "|---|---|---|---|---|---|"]
    for name, a in p["arms"].items():
        L.append("| %s | %.2f | %+.3fpp | %.3fpp | %.3f | %s |"
                 % (name, a["buffer_k"], a["median_delta_pp"], a["median_band_pp"],
                    a["resolvable_share"], a["verdict"]))
    L.append("")
    if p.get("fit"):
        L.append("Fit (through the k=0 identity): **%+.3fpp per unit k**, r2 %.3f, %d points. "
                 "Ruler = **%.2fpp**. k needed to reach the ruler = **%s**."
                 % (p["fit"]["slope_pp_per_k"], p["fit"]["r2"], p["fit"]["n_points"],
                    p["ruler_pp"], p["k_required"]))
        L.append("\nVerdict: **%s**\n" % p["verdict"])
    for x in p["verdict_reasons"]:
        L.append("- %s" % x)
    return "\n".join(L) + "\n"


# ---- r1355: the resolution floor of the WIDTH axis ----------------------------------------
# r1354 asked the buffer axis for a size and got one (k=7.79, past the end of the axis). The
# width axis is the other knob r1350 refused to quote ("the cadence is quotable and the width
# is not"), and it is a different animal: k is a continuous share with a defined end (1.0 =
# never trade), while names are integers whose only hard end is the universe. So the size
# question has to be answered against the width anyone has actually PRICED, not a mathematical
# limit -- results/etf_capacity_frontier.json carries rungs N5..N20, and past N20 the capacity
# story (E162 family) says the book cannot be sized at 1% ADV without shrinking CAGR anyway.
WIDTH_OUT = os.path.join(RES, "etf_book_width_resolution_floor.json")
# the second engine that prices the same ladder: the capacity face's cells are N5..N20 on its
# own universe, so it can falsify a hill instead of confirming it
CAPACITY_FACE = os.path.join(RES, "etf_capacity_frontier.json")
WIDTH_RULE = {
    # a rung is one adjacent pair of widths inside one cadence; the axis is a "size" only if
    # the rungs agree on their sign. This is deliberately tested BEFORE the slope: a line
    # through a hill has a slope and the slope means nothing.
    "min_rungs": 4,
    "sign_agreement_min": 0.75,
    # the widest rung anyone has priced on this design (cell names in
    # results/etf_capacity_frontier.json run N5..N20); past it the answer is not "untested",
    # it is "outside the envelope the book has been shown to hold".
    "priced_width_max": 20,
    "frozen": ("written before the first read of the width floor: the axis is the published "
               "baseline grid's own medians, the ruler is the same baseline median cell band "
               "the buffer floor used, and the sign test runs before the slope"),
}


def width_of(payload, capacity=None):
    """Does width buy a size or only a direction? Pure function over a baseline atlas face."""
    cells = payload["per_cell"]
    ruler = _median([c["p95_cagr_pp"] - c["p05_cagr_pp"] for c in cells])
    by_w, rungs, per_cad = {}, [], {}
    for c in cells:
        by_w.setdefault(c["n_hold"], []).append(c)
        per_cad.setdefault(c["rebal"], {})[c["n_hold"]] = c["median_cagr_pp"]
    widths = {}
    for n in sorted(by_w):
        rows = by_w[n]
        widths[str(n)] = {"n_hold": n, "cadences": len(rows),
                          "median_cagr_pp": round(_median([r["median_cagr_pp"] for r in rows]), 3),
                          "by_cadence": {str(c["rebal"]): c["median_cagr_pp"] for c in rows}}
    for cad, m in sorted(per_cad.items()):
        ns = sorted(m)
        for a, b in zip(ns, ns[1:]):
            rungs.append({"rebal": cad, "from": a, "to": b,
                          "step_pp": round(m[b] - m[a], 3), "up": m[b] > m[a]})
    ups = sum(1 for r in rungs if r["up"])
    agree = max(ups, len(rungs) - ups) / float(len(rungs)) if rungs else 0.0
    peak_n = max(widths.values(), key=lambda w: w["median_cagr_pp"])["n_hold"] if widths else None
    out = {"script": "scripts/etf_book_phase_atlas_arms.py --width",
           "question": ("the width ladder was retired as 'not quotable'. Turn that direction into "
                        "a size: how many more names would the median have to clear for this "
                        "ruler to register a width move, and is that width still a book?"),
           "units": {"step_pp": "pp of median CAGR per one-name step inside one cadence",
                     "slope_pp_per_name": "pp of median CAGR per additional name",
                     "ruler_pp": "the baseline grid's median per-cell band (p95-p05)"},
           "evidence_cutoff": payload.get("evidence_cutoff"),
           "rule": WIDTH_RULE, "ruler_pp": round(ruler, 3),
           "widths": widths, "rungs": rungs,
           "sign_agreement": round(agree, 3),
           "peak_width": peak_n,
           "turnover_inside_grid": bool(peak_n is not None
                                        and max(widths) and peak_n < max(int(k) for k in widths))}
    if capacity is not None:
        out["priced_envelope_crosscheck"] = width_crosscheck(capacity)
    reasons = ["%d rungs over %d widths (need >= %d)"
               % (len(rungs), len(widths), WIDTH_RULE["min_rungs"])]
    if len(rungs) < WIDTH_RULE["min_rungs"] or len(widths) < 2:
        out.update({"fit": None, "dn_required": None, "width_required": None,
                    "verdict": "NOT-ASSESSED", "verdict_reasons": reasons})
        return out
    pts = [(w["n_hold"], w["median_cagr_pp"]) for w in widths.values()]
    slope, inter, r2 = _ols(pts)
    nmin = min(pts)[0]
    dn = ruler / slope if slope > 0 else None
    n_req = nmin + dn if dn is not None else None
    out.update({"fit": {"slope_pp_per_name": round(slope, 4), "intercept_pp": round(inter, 4),
                        "r2": round(r2, 4), "n_points": len(pts)},
                "dn_required": None if dn is None else round(dn, 2),
                "width_required": None if n_req is None else round(n_req, 2),
                "sweep_span_pp": round(max(pts)[1] - min(pts)[1], 3),
                "sweep_share_of_ruler": round((max(pts)[1] - min(pts)[1]) / ruler, 4)
                if ruler else None})
    ups = sum(1 for r in rungs if r["up"])
    reasons += [
        "%d of %d rungs point up (sign agreement %.3f; floor %.2f) -- a line through a hill "
        "has a slope, so the sign test runs first"
        % (ups, len(rungs), agree, WIDTH_RULE["sign_agreement_min"]),
        "peak width %s with turnover inside the tested grid = %s"
        % (peak_n, out["turnover_inside_grid"]),
        "slope %+.4fpp per name, r2 %.3f on %d widths" % (slope, r2, len(pts)),
        "ruler = median cell band %.2fpp; names of runway required = %s"
        % (ruler, "n/a" if dn is None else "%.2f" % dn),
        "width required = %s (thinnest tested %d + runway; widest PRICED rung = %d)"
        % ("n/a" if n_req is None else "%.1f" % n_req, nmin, WIDTH_RULE["priced_width_max"]),
        "the whole ladder spans %.3fpp = %.3f of the ruler"
        % (out["sweep_span_pp"], out["sweep_share_of_ruler"] or 0.0),
    ]
    if agree < WIDTH_RULE["sign_agreement_min"]:
        label = "DIRECTION_NOT_A_SIZE"
        reasons.append("the rungs disagree about the sign, so no single number of names buys the "
                       "ruler: width is a trade (CAGR against capacity), not a resolution knob")
    elif slope <= 0:
        label = "UNREACHABLE_BY_CONSTRUCTION"
        reasons.append("no tested width earns more than a thinner one, so no width reaches it")
    elif n_req > WIDTH_RULE["priced_width_max"]:
        label = "UNREACHABLE_INSIDE_PRICED_ENVELOPE"
        reasons.append("the fitted width %.1f sits past the widest rung anyone priced (%d): the "
                       "answer is outside the envelope, not missing from it"
                       % (n_req, WIDTH_RULE["priced_width_max"]))
    else:
        label = "REACHABLE_DECLARE_A_RUN"
        reasons.append("width %.1f is inside the priced envelope: declare a run there instead of "
                       "extrapolating into it" % n_req)
    out.update({"verdict": label, "verdict_reasons": reasons})
    cc = out.get("priced_envelope_crosscheck")
    if cc:
        out["verdict_reasons"].append(
            "cross-check on the capacity face's own engine (%d rungs, %s up): sign flips "
            "between cadences = %s -- a hill that a second engine cannot reproduce is a panel "
            "artefact, not a property of width"
            % (len(cc["rungs"]), cc["up_direction_share"], cc["sign_flips_by_cadence"]))
    return out


def width_crosscheck(cap):
    """The same ladder on the capacity face's own engine: does the hill reproduce?

    Nothing here feeds the verdict -- it is the cheap falsifier. If the atlas's descent past
    N=8 is a property of width, a second published engine on a second universe should descend
    too; if it is a property of one panel, the second engine will disagree, and that must be
    visible next to the verdict rather than discovered by a reader who happens to own both.
    """
    per = {}
    for c in cap["cells"]:
        m = re.match(r"N(\d+)_R(\d+)", c["cell"])
        if not m:
            continue
        per.setdefault(int(m.group(2)), {})[int(m.group(1))] = round(100.0 * c["cagr"], 3)
    rungs, agree = [], []
    for cad in sorted(per):
        ns = sorted(per[cad])
        for a, b in zip(ns, ns[1:]):
            rungs.append({"rebal": cad, "from": a, "to": b,
                          "step_pp": round(per[cad][b] - per[cad][a], 3)})
            agree.append(per[cad][b] > per[cad][a])
    ups = sum(1 for x in agree if x)
    return {"source": os.path.basename(CAPACITY_FACE),
            "evidence_cutoff": cap.get("evidence_cutoff"),
            "by_cadence": {str(k): v for k, v in sorted(per.items())},
            "rungs": rungs,
            "up_direction_share": round(ups / float(len(agree)), 3) if agree else None,
            "sign_flips_by_cadence": len({(r["step_pp"] > 0) for r in rungs}) > 1
            if rungs else None}


def build_width():
    cap = face(CAPACITY_FACE) if os.path.exists(CAPACITY_FACE) else None
    return width_of(face(BASE), cap)


def width_check():
    """Gate: the published width face must equal a re-derivation from the baseline grid."""
    if not os.path.exists(WIDTH_OUT):
        print("width face is stale: no published width face at %s" % _rel(WIDTH_OUT))
        return 2
    pub = face(WIDTH_OUT)
    if pub.get("rule") != WIDTH_RULE:
        print("width face is inconsistent: the published frozen rule is not the rule in this file")
        return 1
    rebuilt = json.loads(json.dumps(build_width()))
    drift = _diff(pub, rebuilt)
    if not drift:
        print("width face matches its own sources on cutoff %s: %s (width required %s)"
              % (rebuilt["evidence_cutoff"], rebuilt["verdict"], rebuilt["width_required"]))
        return 0
    try:
        face_mtime = os.path.getmtime(WIDTH_OUT)
    except OSError:
        face_mtime = 0.0
    if os.path.getmtime(BASE) > face_mtime + 1.0:
        print("width face is stale: priced on cutoff %r while the baseline grid moved"
              % pub.get("evidence_cutoff"))
        return 2
    print("width face is inconsistent: %d field(s) disagree with a re-derivation and no source "
          "moved: %s" % (len(drift), "; ".join(drift)[:300]))
    return 1


def render_width_md(p):
    L = ["# Width axis resolution floor (r1355 bm-c)\n",
         "Face: `results/etf_book_width_resolution_floor.json`; script: "
         "`scripts/etf_book_phase_atlas_arms.py --width`; source face "
         "`results/etf_book_phase_atlas.json`; cutoff %s.\n" % p["evidence_cutoff"],
         "r1350 could quote the cadence and not the width. This is how big a width move would "
         "have to be to be quotable.\n",
         "| width | cadences | median CAGR | by cadence |", "|---|---|---|---|"]
    for k, w in p["widths"].items():
        L.append("| %s | %d | %+.3fpp | %s |"
                 % (k, w["cadences"], w["median_cagr_pp"],
                    ", ".join("R%s %+.2f" % (r, v) for r, v in w["by_cadence"].items())))
    L.append("")
    if p.get("fit"):
        L.append("Fit: **%+.4fpp per name**, r2 %.3f over %d widths. Ruler = **%.2fpp**. "
                 "Names of runway needed = **%s**, i.e. width **%s** (widest priced rung %d)."
                 % (p["fit"]["slope_pp_per_name"], p["fit"]["r2"], p["fit"]["n_points"],
                    p["ruler_pp"], p["dn_required"], p["width_required"],
                    p["rule"]["priced_width_max"]))
    L.append("\nVerdict: **%s**\n" % p["verdict"])
    L.append("| cadence | rung | step | up |")
    L.append("|---|---|---|---|")
    for r in p["rungs"]:
        L.append("| R%s | %d -> %d | %+.3fpp | %s |"
                 % (r["rebal"], r["from"], r["to"], r["step_pp"], "yes" if r["up"] else "no"))
    L.append("")
    cc = p.get("priced_envelope_crosscheck")
    if cc:
        L.append("Cross-check on `%s` (its own engine, its own universe, cutoff %s): "
                 "sign flips between cadences = **%s**.\n"
                 % (cc["source"], cc.get("evidence_cutoff"), cc["sign_flips_by_cadence"]))
        L.append("| cadence | ladder (median CAGR %) |")
        L.append("|---|---|")
        for cad, m in cc["by_cadence"].items():
            L.append("| R%s | %s |" % (cad, ", ".join("N%s %+.2f" % (k, v) for k, v in m.items())))
        L.append("")
    for x in p["verdict_reasons"]:
        L.append("- %s" % x)
    return "\n".join(L) + "\n"


# ---- r1355: the floor's first out-of-sample point ----------------------------------------
# The floor extrapolates k=7.79 by continuing a 5-point line. The pool row stocked at r1354
# (buffer k=0.30, the midpoint of the widest fitted gap 0.20->0.40) was harvested by the
# autofill tick during this round, so the line now has a point it never saw.
READBACK_OUT = os.path.join(RES, "etf_book_buffer_floor_readback.json")
READBACK_K = 0.30
READBACK_FACE = os.path.join(RES, "etf_book_phase_atlas_buffer_k30.json")
READBACK_RULE = {
    # an unfitted point gets a WIDER band than a fitted one, not a tighter one: the tolerance
    # is three times the fit's own largest in-sample residual, and the residual is recomputed
    # here rather than quoted from the round that wrote the line.
    "tol_multiple": 3.0,
    "tol_floor_pp": 0.05,
    "frozen": ("declared before reading the k=0.30 face: the reading holds if the observed "
               "median delta is within tol of slope*k+intercept and carries the same sign"),
}


# ---- r1356: the two LIVE widths on the same ruler -----------------------------------------
# r1355 turned the width ladder into a resolution floor and found the axis is a direction, not a
# size. That answers the ladder; it does not answer the two faces a reader actually sees. The
# production card runs 12 names (8% vol target) and the executable ticket runs 5 names (beta 0.20
# with a cash leg), and the ticket's own card_agreement block says the five are a PREFIX of the
# twelve -- so "two live widths" is one book truncated, not two books. r1355 already published
# that the two engines disagree about the direction of the 5->12 rung; the only question left
# for somebody holding the ticket is whether the gap between the two live faces is inside that
# disagreement, i.e. whether any part of it may be read as a width effect at all.
LIVE_OUT = os.path.join(RES, "etf_book_live_width_ruler.json")
TICKET_DIR = os.path.join(RES, "etf_book_order")
TICKET_LATEST = os.path.join(TICKET_DIR, "latest.json")
LIVE_RULE = {
    # one complete R20 rebalance cycle: the atlas carries one row per decision origin, so a
    # paired comparison must pair EVERY origin of the cycle rather than sample it
    "pairs_min": 20,
    # a rung whose direction splits more evenly than this is a coin flip and no magnitude
    # rescues it -- the sign test runs before the magnitude test, as it did at r1355
    "sign_split_max": 0.60,
    # two published numbers closer than this are reported as a collision between two different
    # quantities (the r1292 family) rather than allowed to pass for agreement
    "coincidence_tol_pp": 0.005,
    "frozen": ("written before the first read of the two live faces: the comparator is the "
               "difference-of-differences (this rung on the atlas engine vs the same rung on "
               "the capacity engine), never a level gap, because a level gap and a difference "
               "are different units"),
}


def _pp(x):
    return 100.0 * x


def _live_rows(payload, n_hold, rebal):
    """One row per decision origin of the cycle, keyed by phase offset."""
    return {r["phase_offset"]: r for r in payload.get("rows", [])
            if r["n_hold"] == n_hold and r["rebal"] == rebal}


def _cap_ladder(cap, rebal):
    """The capacity engine's own median CAGR per width, on its own universe."""
    out = {}
    for c in (cap or {}).get("cells", []):
        m = re.match(r"N(\d+)_R(\d+)", c.get("cell", ""))
        if m and int(m.group(2)) == rebal:
            out[int(m.group(1))] = round(_pp(c["cagr"]), 3)
    return out


def _ticket_payload():
    """The executable ticket the operator is actually holding (resolve latest -> dated file)."""
    if not os.path.exists(TICKET_LATEST):
        return None
    latest = face(TICKET_LATEST)
    name = latest.get("file")
    if not name:
        return None
    path = os.path.join(TICKET_DIR, name)
    return face(path) if os.path.exists(path) else None


def live_width_of(payload, capacity, ticket):
    """Is the gap between the two live widths inside the two engines' disagreement?

    Three quantities, deliberately never mixed:
      * the PAIRED gap -- card minus ticket CAGR at every decision origin of one complete R20
        cycle, on the atlas engine (one book, two widths, same phases);
      * the RUNG DISAGREEMENT -- the same 5->12 rung priced by the capacity engine, compared as
        a difference to a difference (the only comparator with matching units);
      * the AS-ISSUED diagonal -- what the two live faces actually print, which also moves the
        rule (vol target vs beta) and therefore is not a width number at all.
    """
    cards = payload.get("authoritative_cells") or {}
    card = cards.get("production_card")
    tick = cards.get("executable_ticket")
    out = {"script": "scripts/etf_book_phase_atlas_arms.py --live-widths",
           "question": ("the production card runs 12 names and the executable ticket runs 5. "
                        "Put both live widths on the same ruler and say whether the gap between "
                        "them is inside the disagreement between the two published engines."),
           "units": {"gap_pp": "pp of CAGR, card width minus ticket width, paired by phase",
                     "rung_disagreement_pp": "|atlas 5->12 rung - capacity 5->12 rung| (a "
                                             "difference minus a difference)",
                     "level_gap_pp": "|atlas cell - capacity cell| at the same width: reported, "
                                     "never used as the gate, because a level is not a rung"},
           "rule": LIVE_RULE,
           "evidence_cutoff": payload.get("evidence_cutoff")}
    if not card or not tick or not capacity:
        out.update({"verdict": "NOT-ASSESSED",
                    "verdict_reasons": ["a live cell or the second engine's face is missing"]})
        return out
    cad = card["rebal"]
    A = _live_rows(payload, card["n_hold"], cad)
    B = _live_rows(payload, tick["n_hold"], cad)
    keys = sorted(set(A) & set(B))
    deltas = [round(_pp(A[k]["cagr"]) - _pp(B[k]["cagr"]), 3) for k in keys]
    n = len(deltas)
    ups = sum(1 for d in deltas if d > 0)
    sign_agree = max(ups, n - ups) / float(n) if n else 0.0
    med_paired = round(_median(deltas), 3) if deltas else None
    dif_medians = round(card["median_cagr_pp"] - tick["median_cagr_pp"], 3)
    ladder = _cap_ladder(capacity, cad)
    w_small, w_big = tick["n_hold"], card["n_hold"]
    cap_rung = (round(ladder[w_big] - ladder[w_small], 3)
                if w_big in ladder and w_small in ladder else None)
    atlas_rung = dif_medians
    out.update({
        "live_faces": {
            "card": {"n_hold": w_big, "rebal": cad, "rule": "vol_target",
                     "median_cagr_pp": card["median_cagr_pp"], "band_pp": card["band_pp"],
                     "phases": card.get("phases"), "min_pp": card.get("min_cagr_pp"),
                     "max_pp": card.get("max_cagr_pp")},
            "ticket": {"n_hold": w_small, "rebal": cad, "rule": "beta",
                       "median_cagr_pp": tick["median_cagr_pp"], "band_pp": tick["band_pp"],
                       "phases": tick.get("phases"), "min_pp": tick.get("min_cagr_pp"),
                       "max_pp": tick.get("max_cagr_pp")},
        },
        "paired": {
            "pairs": n, "median_pp": med_paired,
            "mean_pp": round(sum(deltas) / n, 3) if n else None,
            "min_pp": min(deltas) if deltas else None,
            "max_pp": max(deltas) if deltas else None,
            "spread_pp": round(max(deltas) - min(deltas), 3) if deltas else None,
            "sd_pp": round(_sd(deltas), 3) if deltas else None,
            "positive": ups, "sign_agreement": round(sign_agree, 3),
            "phase_offsets": keys,
            # published so a reader (and the smoke leg) can rebuild every number above from the
            # face itself instead of from the script that wrote it
            "deltas_pp": deltas,
        },
        "aggregation": {
            "difference_of_medians_pp": dif_medians,
            "median_of_differences_pp": med_paired,
            "shrink_pp": (None if med_paired is None
                          else round(abs(dif_medians) - abs(med_paired), 3)),
            "ratio": (None if not med_paired else round(dif_medians / med_paired, 3)),
            "note": ("the ladder's rung is a difference of two medians; the same rung taken "
                     "across paired phases is a different number, and the gap between the two "
                     "is the aggregation, not the book"),
        },
        "rulers": {
            "atlas_ruler_pp": round(_median([c["p95_cagr_pp"] - c["p05_cagr_pp"]
                                             for c in payload["per_cell"]]), 3),
            "card_band_pp": card["band_pp"], "ticket_band_pp": tick["band_pp"],
        },
        "engine_disagreement": {
            "atlas_rung_pp": atlas_rung, "capacity_rung_pp": cap_rung,
            "rung_disagreement_pp": (None if cap_rung is None
                                     else round(abs(atlas_rung - cap_rung), 3)),
            "sign_flips": (None if cap_rung is None
                           else bool((atlas_rung > 0) != (cap_rung > 0))),
            "level_gap_pp": {str(w): round(abs(ladder[w] -
                                               [c["median_cagr_pp"] for c in payload["per_cell"]
                                                if c["n_hold"] == w and c["rebal"] == cad][0]), 3)
                             for w in (w_small, w_big) if w in ladder},
            "capacity_evidence_cutoff": capacity.get("evidence_cutoff"),
        },
    })
    as_issued = None
    if ticket and ticket.get("width_disclosure"):
        as_issued = _as_issued_block(ticket["width_disclosure"], out, LIVE_RULE)
        out["as_issued"] = as_issued
    reasons = ["%d paired phases of one R%d cycle (need >= %d)"
               % (n, cad, LIVE_RULE["pairs_min"])]
    if n < LIVE_RULE["pairs_min"] or med_paired is None or cap_rung is None:
        out.update({"verdict": "NOT-ASSESSED", "verdict_reasons": reasons})
        return out
    dis = out["engine_disagreement"]["rung_disagreement_pp"]
    abs_gap = abs(med_paired)
    reasons += [
        "paired gap %+.3fpp (median of %d phase differences; range %+.3f..%+.3f, sd %.3f)"
        % (med_paired, n, out["paired"]["min_pp"], out["paired"]["max_pp"],
           out["paired"]["sd_pp"]),
        "direction splits %d/%d (sign agreement %.3f; floor %.2f)"
        % (ups, n - ups, sign_agree, LIVE_RULE["sign_split_max"]),
        "the same rung costs %+.3fpp on the atlas engine and %+.3fpp on the capacity engine, a "
        "disagreement of %.3fpp with the sign flipping = %s"
        % (atlas_rung, cap_rung, dis, out["engine_disagreement"]["sign_flips"]),
        "difference of medians %+.3fpp vs median of differences %+.3fpp: the ladder's rung is "
        "%.0f%% aggregation"
        % (dif_medians, med_paired,
           0.0 if not med_paired else 100.0 * abs(dif_medians - med_paired) / abs(dif_medians)),
        "gap is %.1f%% of the engine disagreement and %.1f%% of the atlas ruler %.2fpp"
        % (100.0 * abs_gap / dis if dis else float("nan"),
           100.0 * abs_gap / out["rulers"]["atlas_ruler_pp"]
           if out["rulers"]["atlas_ruler_pp"] else float("nan"),
           out["rulers"]["atlas_ruler_pp"]),
    ]
    if sign_agree <= LIVE_RULE["sign_split_max"] and abs_gap < dis:
        label = "COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT"
        reasons.append("the two live widths are not separated by their own phases AND the "
                       "engine disagreement on the same rung is wider than the gap: no part of "
                       "the difference between card and ticket is quotable as a width effect")
    elif abs_gap < dis:
        label = "SIGNED_BUT_INSIDE_ENGINE_DISAGREEMENT"
        reasons.append("the direction is stable but the rung is narrower than what the two "
                       "engines disagree about on the same rung -- second engine wins nothing")
    elif sign_agree > LIVE_RULE["sign_split_max"]:
        label = "RESOLVED_BEYOND_ENGINE_DISAGREEMENT"
        reasons.append("the gap is wider than the engines' own disagreement on this rung and "
                       "its direction is stable across the cycle")
    else:
        label = "UNSIGNED_AND_BEYOND"
        reasons.append("the magnitude clears the engines but the direction is a coin flip: a "
                       "magnitude without a sign is not an effect")
    if as_issued:
        reasons.append(
            "as issued the two faces print %.2fpp vs %.2fpp (%+.2fpp diagonal), but the 2x2 "
            "moves two knobs at once: width effect %+.2fpp under the beta rule and %+.2fpp "
            "under the vol rule, with an interaction of %+.2fpp (bigger than both width "
            "effects = %s)"
            % (as_issued["card_cagr_pp"], as_issued["ticket_cagr_pp"], as_issued["diagonal_pp"],
               as_issued["width_effect_pp"]["beta"], as_issued["width_effect_pp"]["vol"],
               as_issued["interaction_pp"],
               as_issued["interaction_exceeds_both_width_effects"]))
        for c in as_issued.get("coincidences", []):
            reasons.append("COINCIDENCE, not agreement: %s" % c["note"])
    out.update({"verdict": label, "verdict_reasons": reasons})
    return out


def _sd(a):
    if not a:
        return 0.0
    m = sum(a) / float(len(a))
    return (sum((x - m) ** 2 for x in a) / float(len(a))) ** 0.5


def _as_issued_block(wd, ctx, rule):
    """Re-derive the ticket's own 2x2 from its four cells instead of trusting its summaries."""
    sq = ((wd.get("square") or {}).get("cells") or {})
    need = ("beta@5", "beta@12", "vol@5", "vol@12")
    if not all(k in sq for k in need):
        return None
    g = {k: round(_pp(sq[k]["cagr"]), 3) for k in need}
    width = {"beta": round(g["beta@12"] - g["beta@5"], 3),
             "vol": round(g["vol@12"] - g["vol@5"], 3)}
    rulef = {"n5": round(g["vol@5"] - g["beta@5"], 3),
             "n12": round(g["vol@12"] - g["beta@12"], 3)}
    diag = round(g["vol@12"] - g["beta@5"], 3)
    path_width_first = round(width["beta"] + rulef["n12"], 3)
    path_rule_first = round(rulef["n5"] + width["vol"], 3)
    inter = round(width["vol"] - width["beta"], 3)
    coincidences = []
    cap = ctx["engine_disagreement"]["capacity_rung_pp"]
    atlas = ctx["engine_disagreement"]["atlas_rung_pp"]
    for name, val in (("capacity engine's 5->12 rung", cap),
                      ("atlas engine's 5->12 rung", atlas)):
        if val is not None and abs(abs(width["beta"]) - abs(val)) <= rule["coincidence_tol_pp"]:
            coincidences.append({
                "value_pp": width["beta"], "same_as": name,
                "note": ("the beta-rule width effect (%+.3fpp) equals the %s (%+.3fpp) to the "
                         "basis point. They are different quantities on different windows -- "
                         "one is a live 2x2 cell difference, the other a second engine's rung. "
                         "Recording the collision so nobody reads it as confirmation"
                         % (width["beta"], name, val)),
            })
    return {
        "source": "results/etf_book_order/TICKET-*.json width_disclosure.square",
        "cells_cagr_pp": g,
        "card_cagr_pp": g["vol@12"], "ticket_cagr_pp": g["beta@5"],
        "diagonal_pp": diag,
        "width_effect_pp": width, "rule_effect_pp": rulef, "interaction_pp": inter,
        "decomposition": {"width_first": path_width_first, "rule_first": path_rule_first,
                          "paths_agree": abs(path_width_first - path_rule_first) <= 0.011},
        "interaction_exceeds_both_width_effects": bool(
            abs(inter) > abs(width["beta"]) and abs(inter) > abs(width["vol"])),
        "coincidences": coincidences,
        "window": "ticket inception 2024-01-02, 682 bars (not the atlas window)",
        "rules_differ": bool(wd.get("rules_differ")),
    }


def build_live_widths():
    cap = face(CAPACITY_FACE) if os.path.exists(CAPACITY_FACE) else None
    return live_width_of(face(BASE), cap, _ticket_payload())


def live_width_check():
    """Gate: the published live-width face must equal a re-derivation from three faces."""
    if not os.path.exists(LIVE_OUT):
        print("live-width face is stale: no published face at %s" % _rel(LIVE_OUT))
        return 2
    pub = face(LIVE_OUT)
    if pub.get("rule") != LIVE_RULE:
        print("live-width face is inconsistent: published frozen rule is not the rule in this file")
        return 1
    rebuilt = json.loads(json.dumps(build_live_widths()))
    drift = _diff(pub, rebuilt)
    if not drift:
        print("live-width face matches its own sources on cutoff %s: %s (paired gap %spp, "
              "engine disagreement %spp)"
              % (rebuilt["evidence_cutoff"], rebuilt["verdict"],
                 rebuilt["paired"]["median_pp"],
                 rebuilt["engine_disagreement"]["rung_disagreement_pp"]))
        return 0
    try:
        face_mtime = os.path.getmtime(LIVE_OUT)
    except OSError:
        face_mtime = 0.0
    src = [BASE, CAPACITY_FACE, TICKET_LATEST]
    newer = [os.path.basename(p) for p in src
             if os.path.exists(p) and os.path.getmtime(p) > face_mtime + 1.0]
    if newer:
        print("live-width face is stale: sourced before %s moved; drift=%s"
              % (",".join(sorted(newer)), "; ".join(drift)[:200]))
        return 2
    print("live-width face is inconsistent: %d field(s) disagree with a re-derivation and no "
          "source moved: %s" % (len(drift), "; ".join(drift)[:300]))
    return 1


def render_live_widths_md(p):
    L = ["# 两个活宽度放同一把尺子（r1356 bm-c）\n",
         "面：`results/etf_book_live_width_ruler.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py "
         "--live-widths`｜源面：`results/etf_book_phase_atlas.json` + "
         "`results/etf_capacity_frontier.json` + `results/etf_book_order/TICKET-*.json`｜cutoff %s\n"
         % p["evidence_cutoff"]]
    if p["verdict"] == "NOT-ASSESSED":
        L.append("未评估：%s" % "; ".join(p["verdict_reasons"]))
        return "\n".join(L) + "\n"
    f = p["live_faces"]
    L.append("生产卡跑 %d 名（%s），可执行单跑 %d 名（%s），都是 R%s。\n"
             % (f["card"]["n_hold"], f["card"]["rule"], f["ticket"]["n_hold"],
                f["ticket"]["rule"], f["card"]["rebal"]))
    L.append("| 面 | 名数 | 规则 | 中位 CAGR | 本格 band | 相位 |")
    L.append("|---|---|---|---|---|---|")
    for k in ("card", "ticket"):
        L.append("| %s | %d | %s | %+.2fpp | %.2fpp | %s |"
                 % (k, f[k]["n_hold"], f[k]["rule"], f[k]["median_cagr_pp"],
                    f[k]["band_pp"], f[k]["phases"]))
    L.append("")
    pr = p["paired"]
    L.append("## 一、逐相位配对（同一台引擎、同一批 %d 个决策起点）\n" % pr["pairs"])
    L.append("中位差 **%+.3fpp**，均值 %+.3fpp，区间 %+.3f..%+.3fpp（跨度 %.3f，sd %.3f），"
             "方向 %d 上 / %d 下。\n"
             % (pr["median_pp"], pr["mean_pp"], pr["min_pp"], pr["max_pp"], pr["spread_pp"],
                pr["sd_pp"], pr["positive"], pr["pairs"] - pr["positive"]))
    ag = p["aggregation"]
    L.append("**聚合假象**：阶梯上的这一格是「两个中位数相减」= %+.3fpp，同一件事按逐相位配对取中位数 "
             "= %+.3fpp —— 差的 %.3fpp（%.0f%%）是聚合方式，不是书。\n"
             % (ag["difference_of_medians_pp"], ag["median_of_differences_pp"],
                abs(ag["difference_of_medians_pp"] - ag["median_of_differences_pp"]),
                0.0 if not ag["median_of_differences_pp"]
                else 100.0 * abs(ag["difference_of_medians_pp"] - ag["median_of_differences_pp"])
                / abs(ag["difference_of_medians_pp"])))
    ed = p["engine_disagreement"]
    L.append("## 二、两台引擎在同一级上的分歧（唯一可比的量：差减差）\n")
    L.append("| 引擎 | 5 -> 12 这一级 |")
    L.append("|---|---|")
    L.append("| atlas（相位图，vol 规则） | %+.3fpp |" % ed["atlas_rung_pp"])
    L.append("| capacity（容量面，自有宇宙） | %+.3fpp |" % ed["capacity_rung_pp"])
    L.append("")
    L.append("分歧 **%.3fpp**，符号相反 = %s。两面对同一条阶梯连方向都不一致，所以这一级本身不可裁决。\n"
             % (ed["rung_disagreement_pp"], ed["sign_flips"]))
    L.append("同宽度的**水平差**（%s）只作披露、不作判据：水平差与「级差」不是同一个单位，"
             "拿 6pp 的水平差去卡 0.1pp 的级差就是 r1292 那一族。\n"
             % ", ".join("N%s %.2fpp" % (k, v) for k, v in sorted(ed["level_gap_pp"].items())))
    ai = p.get("as_issued")
    if ai:
        L.append("## 三、两张面「照发出去的样子」（同时动了两个旋钮，不是宽度）\n")
        L.append("| 规则 \\ 名数 | 5 | 12 |")
        L.append("|---|---|---|")
        L.append("| beta | %+.2fpp | %+.2fpp |"
                 % (ai["cells_cagr_pp"]["beta@5"], ai["cells_cagr_pp"]["beta@12"]))
        L.append("| vol | %+.2fpp | %+.2fpp |"
                 % (ai["cells_cagr_pp"]["vol@5"], ai["cells_cagr_pp"]["vol@12"]))
        L.append("")
        L.append("对角差 %+.2fpp，但宽度效应在 beta 规则下是 %+.2fpp、在 vol 规则下是 %+.2fpp，"
                 "交互项 %+.2fpp %s。两条分解路径分别得 %+.2f / %+.2f（一致 = %s）。\n"
                 % (ai["diagonal_pp"], ai["width_effect_pp"]["beta"],
                    ai["width_effect_pp"]["vol"], ai["interaction_pp"],
                    "大于任一主效应" if ai["interaction_exceeds_both_width_effects"] else "小于主效应",
                    ai["decomposition"]["width_first"], ai["decomposition"]["rule_first"],
                    ai["decomposition"]["paths_agree"]))
        for c in ai.get("coincidences", []):
            L.append("> 巧合而告：%s\n" % c["note"])
    L.append("\nVerdict: **%s**\n" % p["verdict"])
    for x in p["verdict_reasons"]:
        L.append("- %s" % x)
    return "\n".join(L) + "\n"


def readback_of(floor, arm, base):
    """Did the fit predict the point it never saw? Pure function over three published faces."""
    k_arm = (arm.get("audit") or {}).get("buffer_k")
    reasons = []
    if k_arm is None or abs(k_arm - READBACK_K) > 1e-9:
        return {"script": "scripts/etf_book_phase_atlas_arms.py --readback",
                "verdict": "NOT-ASSESSED",
                "verdict_reasons": ["the harvested face does not declare k=%s (audit says %r): a "
                                    "face wired to the wrong arm would answer a different "
                                    "question" % (READBACK_K, k_arm)]}
    slope = floor["fit"]["slope_pp_per_k"]
    inter = floor["fit"]["intercept_pp"]
    resid = [abs(a["median_delta_pp"] - (inter + slope * a["buffer_k"]))
             for a in floor["arms"].values()]
    tol = max(READBACK_RULE["tol_floor_pp"], READBACK_RULE["tol_multiple"] * max(resid))
    bc = {(c["n_hold"], c["rebal"]): c["median_cagr_pp"] for c in base["per_cell"]}
    rows = []
    for c in arm["per_cell"]:
        key = (c["n_hold"], c["rebal"])
        if key not in bc:
            continue
        rows.append({"n_hold": key[0], "rebal": key[1], "median_cagr_pp": c["median_cagr_pp"],
                     "baseline_cagr_pp": bc[key],
                     "delta_pp": round(c["median_cagr_pp"] - bc[key], 3)})
    if not rows:
        return {"script": "scripts/etf_book_phase_atlas_arms.py --readback",
                "verdict": "NOT-ASSESSED",
                "verdict_reasons": ["the harvested face shares no cell with the baseline grid"]}
    obs = _median([r["delta_pp"] for r in rows])
    pred = inter + slope * READBACK_K
    gap = obs - pred
    reasons += [
        "the fit says %+.3fpp at k=%.2f (slope %+.3f, intercept %+.3f)"
        % (pred, READBACK_K, slope, inter),
        "the harvested arm's own 12 cells say %+.3fpp (median)" % obs,
        "gap %+.3fpp against tolerance %.3fpp = %.1fx the fit's largest in-sample residual "
        "(%.3fpp, floored at %.2f)"
        % (gap, tol, READBACK_RULE["tol_multiple"], max(resid), READBACK_RULE["tol_floor_pp"]),
        "cell spread of the same arm: %+.3f .. %+.3fpp (%d cells), i.e. the median is not the "
        "book" % (min(r["delta_pp"] for r in rows), max(r["delta_pp"] for r in rows), len(rows)),
    ]
    if abs(gap) > tol:
        label = "REFUTED"
        reasons.append("the line misses the point it never saw by more than its own residual "
                       "band: the k the floor reports is an extrapolation with no support")
    elif obs * pred < 0:
        label = "REFUTED"
        reasons.append("the point lands on the wrong side of zero (%+.3f observed against a "
                       "prediction of %+.3f)" % (obs, pred))
    else:
        label = "HOLDS"
        reasons.append("the line predicts a point it never saw, on the widest gap it spans -- "
                       "the extrapolated k is a continuation of a measured slope, not a guess")
    return {"script": "scripts/etf_book_phase_atlas_arms.py --readback",
            "question": ("the buffer floor answers k=7.79 by continuing a line past its last "
                         "arm. Price the midpoint of its widest gap and ask whether the line "
                         "still holds there."),
            "evidence_cutoff": arm.get("evidence_cutoff"),
            "rule": READBACK_RULE, "buffer_k": READBACK_K,
            "floor_face": os.path.basename(FLOOR_OUT), "arm_face": os.path.basename(READBACK_FACE),
            "predicted_pp": round(pred, 3), "observed_pp": round(obs, 3),
            "gap_pp": round(gap, 3), "tolerance_pp": round(tol, 3),
            "max_in_sample_residual_pp": round(max(resid), 3),
            "cells": rows, "verdict": label, "verdict_reasons": reasons}


def build_readback():
    if not (os.path.exists(FLOOR_OUT) and os.path.exists(READBACK_FACE)):
        return None
    return readback_of(face(FLOOR_OUT), face(READBACK_FACE), face(BASE))


def readback_check():
    if not os.path.exists(READBACK_OUT):
        print("readback is stale: no published readback face at %s" % _rel(READBACK_OUT))
        return 2
    pub = face(READBACK_OUT)
    if pub.get("rule") != READBACK_RULE:
        print("readback is inconsistent: the published rule is not the rule in this file")
        return 1
    rebuilt = json.loads(json.dumps(build_readback()))
    if rebuilt is None:
        print("readback is stale: a source face is missing")
        return 2
    drift = _diff(pub, rebuilt)
    if not drift:
        print("readback matches its own sources: %s (predicted %+.3f, observed %+.3f)"
              % (rebuilt["verdict"], rebuilt["predicted_pp"], rebuilt["observed_pp"]))
        return 0
    src = [FLOOR_OUT, READBACK_FACE, BASE]
    face_mtime = os.path.getmtime(READBACK_OUT)
    if any(os.path.getmtime(p) > face_mtime + 1.0 for p in src):
        print("readback is stale: a source face moved after it was written")
        return 2
    print("readback is inconsistent: %d field(s) disagree: %s"
          % (len(drift), "; ".join(drift)[:300]))
    return 1


def render_readback_md(p):
    L = ["# 缓冲轴的第一个样本外点（r1355 bm-c）\n",
         "面：`results/etf_book_buffer_floor_readback.json`｜脚本："
         "`scripts/etf_book_phase_atlas_arms.py --readback`｜臂面 `%s`｜cutoff %s\n"
         % (p["arm_face"], p["evidence_cutoff"]),
         "r1354 用五个臂拟合出 **%+.3fpp / 单位 k**，再沿这条线外推到 k=7.79。本轮任务池交给"
         "自动续批器的第一张票正是 k=0.30——拟合区间 0.20→0.40 的中点，这条线从没见过的点。\n",
         "| 读数 | 值 |", "|---|---|",
         "| 拟合预测 (k=0.30) | %+.3fpp |" % p["predicted_pp"],
         "| 实测中位 | %+.3fpp |" % p["observed_pp"],
         "| 差 | %+.3fpp (容差 %.3fpp) |" % (p["gap_pp"], p["tolerance_pp"]),
         "| 拟合自身最大样本内残差 | %.3fpp |" % p["max_in_sample_residual_pp"],
         "", "判决：**%s**\n" % p["verdict"], "| n | R | 中位 CAGR | 基线 | Δ |", "|---|---|---|---|---|"]
    for r in p["cells"]:
        L.append("| %d | %d | %+.2fpp | %+.2fpp | %+.3fpp |"
                 % (r["n_hold"], r["rebal"], r["median_cagr_pp"], r["baseline_cagr_pp"],
                    r["delta_pp"]))
    L.append("")
    for x in p["verdict_reasons"]:
        L.append("- %s" % x)
    return "\n".join(L) + "\n"


def _selftest():
    bad = []
    CHECKS = [0]

    def chk(ok, msg):
        CHECKS[0] += 1
        print(("[PASS] " if ok else "[FAIL] ") + msg)
        if not ok:
            bad.append(msg)

    for path, _ in ARMS.values():
        chk(os.path.exists(path), "arm face exists: %s" % os.path.basename(path))
    if bad:
        return 1

    p = build()
    base = face(BASE)

    # L1 every arm judges the same 12 cells
    for name, a in p["arms"].items():
        chk(len(a["rows"]) == 12, "%s judges all 12 grid cells" % name)
    # L2 cutoffs identical across faces (a face priced on another panel must not compare)
    cut = {a["evidence_cutoff"] for a in p["arms"].values()} | {base["evidence_cutoff"]}
    chk(len(cut) == 1, "every face is priced on the same evidence cutoff (%s)" % sorted(cut))
    # L3 the baseline path is reproduced, not re-implemented: N5/R20 median must be the
    # published production number
    n5r20 = [r for r in p["arms"]["cost05"]["rows"] if (r["n_hold"], r["rebal"]) == (5, 20)][0]
    chk(abs(n5r20["baseline_cagr_pp"] - 9.13) < 0.02,
        "baseline N5/R20 median reproduces the published 9.13pp (got %.3fpp)" % n5r20["baseline_cagr_pp"])
    # L4 the arms really are different experiments (activity precondition, r1261 lesson)
    chk(p["arms"]["cost05"]["median_band_pp"] != p["arms"]["cost20"]["median_band_pp"],
        "the two cost arms do not produce an identical band (they are distinct runs)")
    # L4b each face carries the knob its own name declares -- a face wired to the wrong arm
    # would publish another arm's numbers under this name and nothing else would notice
    for name, a in p["arms"].items():
        decl = DECLARED.get(name) or {}
        audit = a["audit"]
        bad_knobs = [k for k, v in decl.items() if abs(audit.get(k, -1.0) - v) > 1e-9]
        chk(not bad_knobs, "%s face carries its declared knob %r (audit says %r)"
            % (name, decl, {k: audit.get(k) for k in decl}))
    # L4c the buffer arms are three different runs of the same knob axis, not one face read
    # three times (the median per-cell delta must differ between k=0.05 and k=0.20)
    meds = {}
    for name in ("buffer_k05", "buffer_k10", "buffer_k20"):
        rows = p["arms"][name]["rows"]
        meds[name] = round(sum(r["delta_pp"] for r in rows) / len(rows), 6)
    chk(len(set(meds.values())) == 3, "the three buffer arms are distinct runs (mean deltas %r)"
        % meds)
    # L5 more toll never pays more: every cell's median must fall from 5bp to 20bp
    c05 = {(r["n_hold"], r["rebal"]): r["median_cagr_pp"] for r in p["arms"]["cost05"]["rows"]}
    c20 = {(r["n_hold"], r["rebal"]): r["median_cagr_pp"] for r in p["arms"]["cost20"]["rows"]}
    chk(all(c20[k] < c05[k] for k in c05), "every cell earns less at 20bp than at 5bp")
    # L6 the rule is recomputable: a published verdict must follow from its own rows
    for name, a in p["arms"].items():
        label, _ = judge(a["rows"])
        chk(label == a["verdict"], "%s verdict follows from its own rows (%s)" % (name, label))
    # L7 a hand-made arm that clears every threshold reads ADOPT, one that loses reads REJECT
    good = [{"delta_pp": 1.0, "band_pp": 0.2} for _ in range(12)]
    chk(judge(good)[0] == "ADOPT", "a uniformly improving, resolvable arm reads ADOPT")
    lose = [{"delta_pp": -0.5, "band_pp": 0.2} for _ in range(12)]
    chk(judge(lose)[0] == "REJECT", "an arm that loses more than the cell floor reads REJECT")
    innoise = [{"delta_pp": 0.05, "band_pp": 3.0} for _ in range(12)]
    chk(judge(innoise)[0] == "NOT-SEPARABLE", "an arm inside its own band is not separable")
    short = [{"delta_pp": 1.0, "band_pp": 0.2} for _ in range(3)]
    chk(judge(short)[0] == "NOT-ASSESSED", "a partial grid is not assessed")
    # L8 the cost arms' own rule: a wide-cadence band that stays wide reads SURVIVES, and a
    # band that collapses under the toll reads FOLLOWS_THE_TOLL
    ok_bands = {10: 3.0, 20: 6.0, 40: 9.0}
    chk(judge_bands(ok_bands, {10: 3.0, 20: 6.0, 40: 9.0})[0] == "CADENCE_BAND_SURVIVES_THE_TOLL",
        "an unchanged band structure survives the toll")
    squeezed = {10: 3.0, 20: 3.0, 40: 3.0}
    chk(judge_bands(squeezed, {10: 3.0, 20: 6.0, 40: 9.0})[0] == "BAND_FOLLOWS_THE_TOLL",
        "a band that collapses with the toll is the toll talking")

    # L9-L11 the gate itself: a face that equals its re-derivation is green, an edited face is
    # inconsistent (stays red), a missing face is stale (the chain pays the refresh).
    global OUT_JSON
    keep = OUT_JSON
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tmp = os.path.join(td, "arms.json")
        try:
            p2 = build()
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(p2, f, ensure_ascii=False, indent=1)
            # far future mtime: the source faces can never look "newer" than it
            os.utime(tmp, (os.path.getmtime(tmp) + 3600, os.path.getmtime(tmp) + 3600))
            OUT_JSON = tmp
            rc = check()
            chk(rc == 0, "a face that equals its re-derivation passes the gate (rc=%r)" % rc)
            p2["arms"]["cost05"]["verdict"] = "ADOPT"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(p2, f, ensure_ascii=False, indent=1)
            os.utime(tmp, (os.path.getmtime(tmp) + 3600, os.path.getmtime(tmp) + 3600))
            rc = check()
            chk(rc == 1, "an edited verdict with no source moved stays inconsistent (rc=%r)" % rc)
            OUT_JSON = os.path.join(td, "missing.json")
            rc = check()
            chk(rc == 2, "a missing face is stale, not inconsistent (rc=%r)" % rc)
        finally:
            OUT_JSON = keep

    # L12-L17 the resolution floor: a size needs the same guards a direction does. Every leg
    # below re-derives from the published medians, then moves ONE thing in a fixture.
    fl = floor_of(p)
    chk(fl["fit"] is not None and fl["k_required"] is not None,
        "the floor fits a k from %d buffer arms (k required %r)" % (len(fl["arms"]),
                                                                   fl["k_required"]))
    # L12 fit reproduces each published arm median to the rounding it publishes
    worst = 0.0
    for name, a in fl["arms"].items():
        rows = p["arms"][name]["rows"]
        worst = max(worst, abs(a["median_delta_pp"] - round(_median([r["delta_pp"] for r in rows]), 3)))
    chk(worst < 1e-9, "every arm median in the floor equals the arm face's own rows (max %r)" % worst)
    # L13 the fitted line passes through the k=0 identity: at k=0 the effect must be zero-ish
    chk(abs(fl["fit"]["intercept_pp"]) < 0.15,
        "the fit's intercept stays near the k=0 identity (%+.3fpp)" % fl["fit"]["intercept_pp"])
    # L14 the published reading: the whole axis spans a small share of the ruler. This is the
    # sentence the family retires on, so it is asserted rather than narrated.
    chk(fl["sweep_share_of_ruler"] < FLOOR_RULE["sweep_band_share_max"],
        "the full 20x sweep spans %.3f of the ruler (flag at %.2f)"
        % (fl["sweep_share_of_ruler"], FLOOR_RULE["sweep_band_share_max"]))
    # L15 direction test on fixtures: a steep axis is reachable, a flat one is not
    def _fix(slope):
        f = json.loads(json.dumps(p))
        for name, k in BUFFER_ARMS.items():
            for r in f["arms"][name]["rows"]:
                r["delta_pp"] = slope * k
        return f
    reach = floor_of(_fix(60.0))     # 60pp per unit k: k ~ 0.11 clears a 6.68pp ruler
    chk(reach["verdict"] == "REACHABLE_DECLARE_A_RUN",
        "a steep axis is reachable by a real k (%s, k=%r)" % (reach["verdict"],
                                                             reach["k_required"]))
    flat = floor_of(_fix(1.0))
    chk(flat["verdict"] == "UNREACHABLE_BY_CONSTRUCTION",
        "a shallow axis stays unreachable (%s, k=%r)" % (flat["verdict"], flat["k_required"]))
    # L16 a short axis is not assessed, not zero-sloped
    thin = json.loads(json.dumps(p))
    for name in ("buffer_k02", "buffer_k40"):
        thin["arms"].pop(name, None)
    chk(floor_of(thin)["verdict"] == "NOT-ASSESSED",
        "three arms is not a slope (NOT-ASSESSED, not a verdict)")
    # L17 the floor gate has the same three states as the arms gate
    global FLOOR_OUT
    keepf = FLOOR_OUT
    with tempfile.TemporaryDirectory() as td:
        try:
            ftmp = os.path.join(td, "floor.json")
            with open(ftmp, "w", encoding="utf-8") as f:
                json.dump(build_floor(), f, ensure_ascii=False, indent=1)
            os.utime(ftmp, (os.path.getmtime(ftmp) + 3600, os.path.getmtime(ftmp) + 3600))
            FLOOR_OUT = ftmp
            rc = floor_check()
            chk(rc == 0, "an unedited floor passes its gate (rc=%r)" % rc)
            d2 = json.loads(json.dumps(build_floor()))
            d2["k_required"] = 0.5
            with open(ftmp, "w", encoding="utf-8") as f:
                json.dump(d2, f, ensure_ascii=False, indent=1)
            os.utime(ftmp, (os.path.getmtime(ftmp) + 3600, os.path.getmtime(ftmp) + 3600))
            rc = floor_check()
            chk(rc == 1, "an edited k with no source moved stays inconsistent (rc=%r)" % rc)
            FLOOR_OUT = os.path.join(td, "missing.json")
            chk(floor_check() == 2, "a missing floor is stale, not inconsistent")
        finally:
            FLOOR_OUT = keepf

    # L18-L23 the width floor: the same shape of guard, on the axis where the knob cannot be
    # pushed past its end, so the envelope has to be a PRICED one rather than an algebraic one.
    wf = width_of(base)
    chk(wf["fit"] is not None and len(wf["widths"]) == 4,
        "the width floor fits %d widths (%s)" % (len(wf["widths"]), sorted(wf["widths"])))
    # L18 the rung count is the grid's own: (widths-1) rungs per cadence
    chk(len(wf["rungs"]) == 9, "every adjacent width pair inside every cadence is a rung (%d)"
        % len(wf["rungs"]))
    # L19 the published reading is recomputable from the rungs it publishes
    ups = sum(1 for r in wf["rungs"] if r["up"])
    chk(abs(wf["sign_agreement"] - round(max(ups, len(wf["rungs"]) - ups) / float(len(wf["rungs"])), 3)) < 1e-9,
        "sign agreement follows from the published rungs (%d of %d up)"
        % (ups, len(wf["rungs"])))
    # L20 a width ladder that rises monotonically must NOT read DIRECTION_NOT_A_SIZE -- the
    # sign test must be able to pass, or it is a rule that only ever says no
    mono = json.loads(json.dumps(base))
    for c in mono["per_cell"]:
        c["median_cagr_pp"] = 8.0 + 0.5 * c["n_hold"]
    m = width_of(mono)
    chk(m["verdict"] == "REACHABLE_DECLARE_A_RUN",
        "a monotone, steep-enough ladder reaches a width inside the priced envelope (%s, width %r)"
        % (m["verdict"], m["width_required"]))
    # L21 a monotone but flat ladder is unreachable inside the envelope, by a size not by noise
    flatw = json.loads(json.dumps(base))
    for c in flatw["per_cell"]:
        c["median_cagr_pp"] = 8.0 + 0.02 * c["n_hold"]
    f = width_of(flatw)
    chk(f["verdict"] == "UNREACHABLE_INSIDE_PRICED_ENVELOPE" and f["width_required"] > 20,
        "a flat ladder needs a width past the widest priced rung (%s, width %r)"
        % (f["verdict"], f["width_required"]))
    # L22 a hill (up then down) reads DIRECTION_NOT_A_SIZE even though its slope is positive
    hill = json.loads(json.dumps(base))
    for c in hill["per_cell"]:
        c["median_cagr_pp"] = 8.0 + (1.0 if c["n_hold"] in (5, 8) else 0.0)
    h = width_of(hill)
    chk(h["verdict"] == "DIRECTION_NOT_A_SIZE",
        "a ladder whose rungs change sign is a direction, not a size (%s)" % h["verdict"])
    # L24 the cross-check is a falsifier, not a rubber stamp: a capacity face whose ladder points
    # one way everywhere must read sign_flips=False, and a saw-tooth must read True
    def _cap(steps):
        cells = []
        for cad, ns in ((10, {5: 1.0, 8: 1.0 + steps[0]}),
                        (20, {5: 1.0, 8: 1.0 + steps[1]})):
            for n, v in ns.items():
                cells.append({"cell": "N%d_R%d" % (n, cad), "cagr": v / 100.0})
        return {"cells": cells, "evidence_cutoff": "fixture"}
    one_way = width_crosscheck(_cap((0.5, 0.5)))
    chk(one_way["sign_flips_by_cadence"] is False and one_way["up_direction_share"] == 1.0,
        "a ladder that points one way everywhere does not read as a flip")
    saw = width_crosscheck(_cap((0.5, -0.5)))
    chk(saw["sign_flips_by_cadence"] is True and saw["up_direction_share"] == 0.5,
        "a ladder that disagrees between cadences reads as a flip")

    # L25-L27 the read-back: the fit must be able to FAIL the point it never saw, and a face
    # wired to the wrong arm must refuse to answer at all
    def _fx(observed, declared_k=0.30):
        fl = {"fit": {"slope_pp_per_k": 1.0, "intercept_pp": 0.0},
              "arms": {"a": {"buffer_k": 0.0, "median_delta_pp": 0.0},
                       "b": {"buffer_k": 0.5, "median_delta_pp": 0.5}}}
        am = {"audit": {"buffer_k": declared_k}, "evidence_cutoff": "fixture",
              "per_cell": [{"n_hold": 5, "rebal": 20, "median_cagr_pp": 10.0 + observed},
                           {"n_hold": 8, "rebal": 20, "median_cagr_pp": 10.0 + observed}]}
        bs = {"per_cell": [{"n_hold": 5, "rebal": 20, "median_cagr_pp": 10.0},
                           {"n_hold": 8, "rebal": 20, "median_cagr_pp": 10.0}]}
        return readback_of(fl, am, bs)
    chk(_fx(0.30)["verdict"] == "HOLDS", "a point on the line holds (%s)" % _fx(0.30)["verdict"])
    chk(_fx(0.90)["verdict"] == "REFUTED",
        "a point far off the line is refuted, not rounded into agreement (%s)"
        % _fx(0.90)["verdict"])
    chk(_fx(0.30, declared_k=0.20)["verdict"] == "NOT-ASSESSED",
        "a face declaring another arm's knob is not assessed")

    # L23 the width gate has the same three states as the other two gates
    global WIDTH_OUT
    keepw = WIDTH_OUT
    with tempfile.TemporaryDirectory() as td:
        try:
            wtmp = os.path.join(td, "width.json")
            with open(wtmp, "w", encoding="utf-8") as fh:
                json.dump(build_width(), fh, ensure_ascii=False, indent=1)
            os.utime(wtmp, (os.path.getmtime(wtmp) + 3600, os.path.getmtime(wtmp) + 3600))
            WIDTH_OUT = wtmp
            chk(width_check() == 0, "an unedited width face passes its gate")
            w2 = json.loads(json.dumps(build_width()))
            w2["verdict"] = "REACHABLE_DECLARE_A_RUN"
            with open(wtmp, "w", encoding="utf-8") as fh:
                json.dump(w2, fh, ensure_ascii=False, indent=1)
            os.utime(wtmp, (os.path.getmtime(wtmp) + 3600, os.path.getmtime(wtmp) + 3600))
            chk(width_check() == 1, "an edited width verdict stays inconsistent")
            WIDTH_OUT = os.path.join(td, "missing.json")
            chk(width_check() == 2, "a missing width face is stale, not inconsistent")
        finally:
            WIDTH_OUT = keepw

    # L24 the live-width face separates "difference of medians" from "median of differences"
    def _lw_fix(card_vals, tick_vals, cap5, cap12, ticket=None):
        """Fixture: two live widths over one cycle plus a second engine's rung."""
        rows = []
        for i, (c, t) in enumerate(zip(card_vals, tick_vals)):
            rows.append({"n_hold": 5, "rebal": 20, "phase_offset": i, "cagr": t / 100.0})
            rows.append({"n_hold": 12, "rebal": 20, "phase_offset": i, "cagr": c / 100.0})

        def cell(n, vals):
            med = _median(vals)
            lo, hi = min(vals), max(vals)
            return {"n_hold": n, "rebal": 20, "median_cagr_pp": med, "band_pp": 6.0,
                    "phases": len(vals), "min_cagr_pp": lo, "max_cagr_pp": hi,
                    "p05_cagr_pp": med - 3.0, "p95_cagr_pp": med + 3.0}

        payload = {"evidence_cutoff": "fixture", "rows": rows,
                   "per_cell": [cell(5, tick_vals), cell(12, card_vals)],
                   "authoritative_cells": {"production_card": cell(12, card_vals),
                                           "executable_ticket": cell(5, tick_vals)}}
        cap = {"evidence_cutoff": "fixture",
               "cells": [{"cell": "N5_R20", "cagr": cap5 / 100.0},
                         {"cell": "N12_R20", "cagr": cap12 / 100.0}]}
        return payload, cap, ticket

    # a pairing where the two aggregations provably disagree: 21 points, medians 14 vs 5 (+9)
    # while 11 of the 21 paired differences are exactly zero (median 0)
    _card = [5.0] + [14.0] * 20
    _tick = [5.0] * 11 + [14.0] * 10
    f_pay, f_cap, _ = _lw_fix(_card, _tick, 10.0, 11.0)
    lw = live_width_of(f_pay, f_cap, None)
    chk(abs(lw["aggregation"]["difference_of_medians_pp"] - 9.0) < 1e-9,
        "fixture reproduces the ladder's rung as a difference of medians (%+.3fpp)"
        % lw["aggregation"]["difference_of_medians_pp"])
    chk(abs(lw["aggregation"]["median_of_differences_pp"]) < 1e-9,
        "the same rung paired across phases is a different number (%+.3fpp)"
        % lw["aggregation"]["median_of_differences_pp"])
    chk(lw["verdict"] == "COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT",
        "a rung that is aggregation is published as a coin flip (%s)" % lw["verdict"])

    # L25 the sign test runs before the magnitude test
    p_stable = live_width_of(*_lw_fix([10.5] * 20, [10.0] * 20, 10.5, 10.0)[:2], None)
    chk(p_stable["verdict"] == "SIGNED_BUT_INSIDE_ENGINE_DISAGREEMENT",
        "a small rung with a stable sign is named as signed-but-inside (%s)"
        % p_stable["verdict"])
    p_big = live_width_of(*_lw_fix([13.0] * 20, [10.0] * 20, 10.0, 11.0)[:2], None)
    chk(p_big["verdict"] == "RESOLVED_BEYOND_ENGINE_DISAGREEMENT",
        "a rung past the engines' disagreement with a stable sign is resolved (%s)"
        % p_big["verdict"])

    # L26 a LEVEL gap is never the gate: 10pp of level disagreement must not swallow a rung
    p_level = live_width_of(*_lw_fix([13.0] * 20, [10.0] * 20, 20.0, 21.0)[:2], None)
    chk(max(p_level["engine_disagreement"]["level_gap_pp"].values()) > 9.0,
        "fixture carries a %.1fpp level gap (so a level-based gate would swallow the rung)"
        % max(p_level["engine_disagreement"]["level_gap_pp"].values()))
    chk(p_level["verdict"] == "RESOLVED_BEYOND_ENGINE_DISAGREEMENT",
        "the rung, not the level gap, decides (%s)" % p_level["verdict"])

    # L27 the as-issued 2x2 is re-derived from its four cells, and a lying summary is ignored
    _sq = {"cells": {"beta@5": {"cagr": 0.1000}, "beta@12": {"cagr": 0.0847},
                     "vol@5": {"cagr": 0.1086}, "vol@12": {"cagr": 0.1118}},
           "width_effect_pp": {"beta": 999.0, "vol": 999.0}, "rules_differ": True}
    ai = _as_issued_block({"square": _sq}, lw, LIVE_RULE)
    chk(abs(ai["width_effect_pp"]["beta"] + 1.53) < 0.011,
        "as-issued width effect recomputed from cells (%+.3fpp), not read off the summary"
        % ai["width_effect_pp"]["beta"])
    chk(abs(ai["diagonal_pp"] - 1.18) < 0.011 and ai["decomposition"]["paths_agree"],
        "the two decomposition paths both reproduce the diagonal (%+.3f | %+.3f)"
        % (ai["decomposition"]["width_first"], ai["decomposition"]["rule_first"]))
    chk(ai["interaction_exceeds_both_width_effects"],
        "the fixture's interaction exceeds both width effects, so the diagonal is not a width")

    # L28 two different quantities landing on the same basis point are reported, not merged
    pay2, cap2, _ = _lw_fix([10.0] * 20, [10.0] * 20, 15.56, 14.03)
    lw2 = live_width_of(pay2, cap2, {"width_disclosure": {"square": _sq, "rules_differ": True}})
    chk(len(lw2["as_issued"]["coincidences"]) >= 1,
        "the beta-rule width effect and the capacity rung collision is published as a "
        "coincidence (%d found)" % len(lw2["as_issued"]["coincidences"]))

    # L29 the live-width gate has the same three states as the other gates
    global LIVE_OUT
    keepl = LIVE_OUT
    with tempfile.TemporaryDirectory() as td:
        try:
            ltmp = os.path.join(td, "live.json")
            with open(ltmp, "w", encoding="utf-8") as fh:
                json.dump(build_live_widths(), fh, ensure_ascii=False, indent=1)
            os.utime(ltmp, (os.path.getmtime(ltmp) + 3600, os.path.getmtime(ltmp) + 3600))
            LIVE_OUT = ltmp
            chk(live_width_check() == 0, "an unedited live-width face passes its gate")
            l2 = json.loads(json.dumps(build_live_widths()))
            l2["verdict"] = "RESOLVED_BEYOND_ENGINE_DISAGREEMENT"
            with open(ltmp, "w", encoding="utf-8") as fh:
                json.dump(l2, fh, ensure_ascii=False, indent=1)
            os.utime(ltmp, (os.path.getmtime(ltmp) + 3600, os.path.getmtime(ltmp) + 3600))
            chk(live_width_check() == 1, "an edited live-width verdict stays inconsistent")
            LIVE_OUT = os.path.join(td, "missing.json")
            chk(live_width_check() == 2, "a missing live-width face is stale, not inconsistent")
        finally:
            LIVE_OUT = keepl

    print("selftest: %d legs, %d failed" % (CHECKS[0], len(bad)))
    return 0 if not bad else 1


def _rel(path):
    """Path relative to the repo, or the bare name when it lives outside it (a test fixture)."""
    try:
        return os.path.relpath(path, ROOT)
    except ValueError:
        return os.path.basename(path)


def _diff(a, b, path="", out=None, limit=8):
    """Structural diff of two payloads; returns up to `limit` leaf paths that differ."""
    if out is None:
        out = []
    if len(out) >= limit:
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if len(out) >= limit:
                break
            if k not in a or k not in b:
                out.append("%s.%s (only on one side)" % (path, k))
            else:
                _diff(a[k], b[k], "%s.%s" % (path, k), out, limit)
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append("%s (len %d vs %d)" % (path, len(a), len(b)))
            return out
        for i, (x, y) in enumerate(zip(a, b)):
            if len(out) >= limit:
                break
            _diff(x, y, "%s[%d]" % (path, i), out, limit)
        return out
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        if abs(a - b) > 1e-9:
            out.append("%s (%r vs %r)" % (path, a, b))
    elif a != b:
        out.append("%s (%r vs %r)" % (path, a, b))
    return out


def check():
    """Gate: the published face must equal a re-derivation from the four arm faces.

    Two red states, and the difference matters (r1346): a face whose SOURCE has advanced past
    it is 'stale' and the chain pays the declared refresh; a face that disagrees with its own
    sources while the sources have not moved is 'inconsistent' and stays red, because that is a
    hand-edited or half-written face and re-deriving it would launder the edit.
    """
    if not os.path.exists(OUT_JSON):
        print("face is stale: no published arms face at %s" % _rel(OUT_JSON))
        return 2
    pub = face(OUT_JSON)
    if pub.get("criteria") != CRITERIA:
        print("face is inconsistent: the published frozen rule is not the rule in this file")
        return 1
    rebuilt = json.loads(json.dumps(build()))   # compare what a reader sees, not Python types
    drift = _diff(pub, rebuilt)
    if not drift:
        verdicts = " | ".join("%s=%s" % (k, v["verdict"]) for k, v in rebuilt["arms"].items())
        print("arms face matches its own sources on cutoff %s: %s"
              % (rebuilt["baseline"]["evidence_cutoff"], verdicts))
        return 0
    src = [BASE] + [p for p, _ in ARMS.values()]
    try:
        face_mtime = os.path.getmtime(OUT_JSON)
    except OSError:
        face_mtime = 0.0
    newer = [os.path.basename(p) for p in src if os.path.getmtime(p) > face_mtime + 1.0]
    if newer:
        print("face is stale: priced on cutoff %r while its sources moved (%s); drift=%s"
              % (pub.get("baseline", {}).get("evidence_cutoff"), ",".join(sorted(newer))[:160],
                 "; ".join(drift)[:300]))
        return 2
    print("face is inconsistent: %d field(s) disagree with a re-derivation and no source moved: %s"
          % (len(drift), "; ".join(drift)[:400]))
    return 1


def render_md(p):
    L = []
    L.append("# 相位臂：把 r1325 的 buffer REJECT 与成本档放回它们自己的尺子里重判\n")
    L.append("面：`results/etf_book_phase_atlas_arms.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py`｜"
             "基线面：`%s`（cutoff %s）\n" % (p["baseline"]["face"], p["baseline"]["evidence_cutoff"]))
    L.append("同日基线网格：格间 spread %.2fpp，格内 band 中位 %.2fpp。\n" % (
        p["baseline"]["grid_between_cell_spread_pp"], p["baseline"]["median_cell_band_pp"]))
    for name, a in p["arms"].items():
        L.append("## %s — **%s**\n" % (name, a["verdict"]))
        L.append(a["description"] + "\n")
        L.append("| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |")
        L.append("|---|---|---|---|---|---|")
        for r in a["rows"]:
            L.append("| %d | %d | %+.2fpp | %+.2fpp | %+.3fpp | %.2fpp |" % (
                r["n_hold"], r["rebal"], r["median_cagr_pp"], r["baseline_cagr_pp"],
                r["delta_pp"], r["band_pp"]))
        L.append("")
        for x in a["verdict_reasons"]:
            L.append("- %s" % x)
        L.append("")
    return "\n".join(L) + "\n"


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    if "--check" in argv:
        return check()
    if "--floor-check" in argv:
        return floor_check()
    if "--width-check" in argv:
        return width_check()
    if "--live-widths-check" in argv:
        return live_width_check()
    if "--live-widths" in argv:
        lv = build_live_widths()
        with open(LIVE_OUT, "w", encoding="utf-8") as fh:
            json.dump(lv, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        md = os.path.join(ROOT, "research", "ETF_BOOK_LIVE_WIDTH_RULER.md")
        with open(md, "w", encoding="utf-8") as fh:
            fh.write(render_live_widths_md(lv))
        print("%s: paired gap %spp on %s phases, engine disagreement %spp"
              % (lv["verdict"], lv.get("paired", {}).get("median_pp"),
                 lv.get("paired", {}).get("pairs"),
                 lv.get("engine_disagreement", {}).get("rung_disagreement_pp")))
        print("wrote", os.path.relpath(LIVE_OUT, ROOT),
              "and research/ETF_BOOK_LIVE_WIDTH_RULER.md")
        return 0
    if "--readback-check" in argv:
        return readback_check()
    if "--readback" in argv:
        rb = build_readback()
        if rb is None:
            print("readback not assessed: a source face is missing")
            return 2
        with open(READBACK_OUT, "w", encoding="utf-8") as fh:
            json.dump(rb, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        md = os.path.join(ROOT, "research", "ETF_BOOK_BUFFER_FLOOR_READBACK.md")
        with open(md, "w", encoding="utf-8") as fh:
            fh.write(render_readback_md(rb))
        print("%s: predicted %+.3fpp vs observed %+.3fpp at k=%.2f (gap %+.3fpp)"
              % (rb["verdict"], rb.get("predicted_pp", 0.0), rb.get("observed_pp", 0.0),
                 READBACK_K, rb.get("gap_pp", 0.0)))
        print("wrote", os.path.relpath(READBACK_OUT, ROOT),
              "and research/ETF_BOOK_BUFFER_FLOOR_READBACK.md")
        return 0
    if "--width" in argv:
        w = build_width()
        with open(WIDTH_OUT, "w", encoding="utf-8") as fh:
            json.dump(w, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        md = os.path.join(ROOT, "research", "ETF_BOOK_WIDTH_RESOLUTION_FLOOR.md")
        with open(md, "w", encoding="utf-8") as fh:
            fh.write(render_width_md(w))
        print("%s: width required %s (widest priced %d), sign agreement %.3f, ruler %.2fpp"
              % (w["verdict"], w["width_required"], WIDTH_RULE["priced_width_max"],
                 w["sign_agreement"], w["ruler_pp"]))
        print("wrote", os.path.relpath(WIDTH_OUT, ROOT),
              "and research/ETF_BOOK_WIDTH_RESOLUTION_FLOOR.md")
        return 0
    if "--floor" in argv:
        f = build_floor()
        with open(FLOOR_OUT, "w", encoding="utf-8") as fh:
            json.dump(f, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        md = os.path.join(ROOT, "research", "ETF_BOOK_BUFFER_RESOLUTION_FLOOR.md")
        with open(md, "w", encoding="utf-8") as fh:
            fh.write(render_floor_md(f))
        print("%s: k required %s, ruler %.2fpp, sweep share %.3f"
              % (f["verdict"], f["k_required"], f["ruler_pp"],
                 f.get("sweep_share_of_ruler") or 0.0))
        print("wrote", os.path.relpath(FLOOR_OUT, ROOT),
              "and research/ETF_BOOK_BUFFER_RESOLUTION_FLOOR.md")
        return 0
    p = build()
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=1)
        f.write("\n")
    md = os.path.join(ROOT, "research", "ETF_BOOK_PHASE_ATLAS_ARMS.md")
    with open(md, "w", encoding="utf-8") as f:
        f.write(render_md(p))
    for name, a in p["arms"].items():
        print("%-10s %-14s median_band %.2fpp" % (name, a["verdict"], a["median_band_pp"]))
    print("wrote", os.path.relpath(OUT_JSON, ROOT), "and research/ETF_BOOK_PHASE_ATLAS_ARMS.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))