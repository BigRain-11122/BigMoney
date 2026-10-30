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