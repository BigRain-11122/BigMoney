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
        "question": ("do the three follow-ups the atlas left behind (buffer k=0.05, cost 5bp, cost 20bp) "
                     "change the reading when they are judged per cell against each cell's own band?"),
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

    print("selftest: %d legs, %d failed" % (CHECKS[0], len(bad)))
    return 0 if not bad else 1


def render_md(p):
    L = []
    L.append("# 三个相位臂：把 r1325 的 buffer REJECT 放回它自己的尺子里重判\n")
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