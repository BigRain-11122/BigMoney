#!/usr/bin/env python3
"""E256 -- extend E255's draw ladder until the band endpoint stops moving (or say it does not).

E255 measured the same seven rungs at 60/120/240/480 draws and found that the r2 straightness
floor clears on draws alone while the band ENDPOINT -- a 5% quantile of the permutation sample --
is still rising with the draw count (median +9.8% HEAD / +11.7% TAIL from 240 to 480). A quantile
read off too few draws sits inside the true boundary, so every session target divided by that
edge is a floor that shrinks as the grid grows. The card left one question open:

    at which draw count does NO rung move more than 2% between counts,
    or -- if that count is not reachable -- is the increment per doubling flat?

This face answers exactly that, on the SAME ladder, by stretching the grid to 1920 draws while
keeping the prefix structure E255 established: one draw stream per seed at max(grid) contains
every smaller count as its prefix (``random.Random(seed)`` emits the same shuffle sequence
whatever the loop length), so six draw counts are ONE experiment read six ways, not six
experiments that may disagree for a different reason.

Two published readings per family, both recomputed from the numbers in the file:

  settled_after_draws   the smallest grid point after which every later step moves every rung by
                        at most CONV_PCT (2%, E255's own frozen convergence line); None when no
                        such point exists inside the grid.
  increment_flat        when no point settles: has the per-doubling rise stopped shrinking? A
                        plateau at a positive increment means more draws buy a fixed amount per
                        doubling and the endpoint has no countable stopping point.

The difference is operational: "settles at 960" says the band is measured and E253's target can be
quoted; "flat at +0.9% per doubling" says the band keeps growing and any session target divided by
it is a floor with no ceiling.

NO BILL, NO ADOPTION, NO RE-PRICING, NO BOOTSTRAP: this face re-reads one band ladder. It moves no
coefficient and prices nothing.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e239_own_vs_cross as e239  # noqa: E402
import e250_book_turnover_echo as e250  # noqa: E402
import e252_star_prices_itself as e252  # noqa: E402
import e253_self_row_resolution as e253  # noqa: E402
import e254_band_exponent_inside_cell as e254  # noqa: E402
import e255_band_draw_starvation as e255  # noqa: E402

ROOT = e252.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

STUDY = "E256_band_draw_continuation"
FAMILIES = e255.FAMILIES                 # ("head", "tail") -- fixed start vs fixed end
D_GRID = (60, 120, 240, 480, 960, 1920)  # E255's grid plus two doublings
CONV_PCT = e255.CONV_PCT                 # 2.0%, frozen by E255 -- reused, never re-tuned here
FLAT_REL_TOL = 0.20                      # "flat" = the last doubling kept >= 80% of the previous step
SEEDS = e255.SEEDS
D_BUDGET = max(D_GRID)                   # this face's own measured top, not E255's

VERDICTS = ("endpoint_settles_within_the_grid",
            "increments_do_not_decay_with_draws",
            "endpoint_still_rising_at_the_budget",
            "no_rungs_measured")


def median(vals):
    return e255.median(vals)


def fmt_pct(v):
    return "n/a" if v is None else "%.2f%%" % v


def step_series(rungs, grid):
    """Per consecutive grid pair: how far every rung's edge moved (percent of the lower count)."""
    steps = []
    for a, b in zip(grid, grid[1:]):
        rises = []
        for r in rungs:
            bd = r.get("by_draws") or {}
            ea = (bd.get(str(a)) or {}).get("edge_self")
            eb = (bd.get(str(b)) or {}).get("edge_self")
            if ea and eb:
                rises.append(100.0 * (eb - ea) / ea)
        steps.append({"from": a, "to": b, "is_doubling": b == 2 * a,
                      "rungs": len(rises),
                      "median_rise_pct": median(rises),
                      "max_abs_rise_pct": (max((abs(x) for x in rises), default=None)
                                           if rises else None),
                      "rungs_that_rose": sum(1 for x in rises if x > 0)})
    return steps


def settled_at(steps, pct=CONV_PCT):
    """The smallest grid point after which no rung moves more than `pct`% in ANY later step.

    Returning the FIRST such point (rather than the last step's own rise) is the whole point: a
    single quiet step is not convergence, and a count that settles and then jumps again has not
    settled. A step with no measurable rungs cannot establish convergence -- it is skipped over,
    so a grid whose top half is unmeasured cannot report a floor drawn from the measured half.
    """
    if not steps:
        return {"draws": None, "settled": False, "reason": "no steps in the grid",
                "steps_after": 0}
    for i, s in enumerate(steps):
        tail = steps[i:]
        if any(x.get("max_abs_rise_pct") is None for x in tail):
            continue
        if all(x["max_abs_rise_pct"] <= pct for x in tail):
            return {"draws": s["from"], "settled": True,
                    "steps_after": len(tail),
                    "reason": "every rung moves at most %.2f%% per step from %d draws up"
                              % (max(x["max_abs_rise_pct"] for x in tail), s["from"])}
    measurable = [s for s in steps if s.get("max_abs_rise_pct") is not None]
    worst = max((s["max_abs_rise_pct"] for s in measurable), default=None)
    return {"draws": None, "settled": False, "steps_after": 0,
            "worst_step_pct": worst,
            "reason": ("step %d->%d still moves %.2f%%"
                       % (measurable[-1]["from"], measurable[-1]["to"],
                          measurable[-1]["max_abs_rise_pct"]))
                      if measurable else "no step was measurable"}


def decay_increments(steps, rel_tol=FLAT_REL_TOL):
    """Is the per-doubling rise shrinking (so more draws still buy), or is it not decaying?

    Compares the SECOND HALF of the doubling steps against the first half, not the last step
    against the one before it. The single-step comparison in the first cut of this face called a
    sequence of 8.8 / 1.6 / 9.8 / 5.2 / 10.3 a plateau because its last step happened to exceed the
    one before it -- a noisy ladder oscillates, and one pair of steps cannot tell an oscillation
    from a floor. Splitting the sequence in halves asks the question that matters (do later
    doublings add LESS than earlier ones), and the oscillation itself is published beside the
    verdict rather than smoothed away.
    """
    st = [s for s in steps if s.get("is_doubling") and s.get("median_rise_pct") is not None]
    vals = [s["median_rise_pct"] for s in st]
    out = {"no_decay": None, "ratio_second_half_over_first": None,
           "plateau_pct_per_doubling": None, "step_pct": vals,
           "oscillates": None, "reason": "fewer than two doubling steps"}
    if len(st) < 2:
        out["plateau_pct_per_doubling"] = (vals[-1] if vals else None)
        return out
    cut = len(vals) // 2
    first, second = median(vals[:cut]), median(vals[cut:])
    pos = [v for v in vals if v is not None]
    ratio = (second / first) if first else None
    out.update({"first_half_pct": first, "second_half_pct": second,
                "step_sd": (statistics.stdev(pos) if len(pos) > 1 else None),
                "steps_monotone_decreasing": all(b <= a for a, b in zip(vals, vals[1:])),
                "oscillates": (bool(pos) and min(pos) > 0 and max(pos) / min(pos) > 2.0),
                "plateau_pct_per_doubling": second,
                "ratio_second_half_over_first": ratio})
    if ratio is None:
        out["reason"] = "the first half adds zero, so no ratio is defined"
        return out
    out["no_decay"] = bool(ratio >= (1.0 - rel_tol) and second > 0)
    out["reason"] = ("later doublings still add %.2f%% per doubling (%.0f%% of the earlier ones)%s"
                     % (second, 100.0 * ratio,
                        "; the step sequence oscillates rather than trending"
                        if out["oscillates"] else ""))
    return out


def analyse(rungs, grid):
    """One family's continuation reading, every field derived from `rungs` alone."""
    rows = sorted([r for r in rungs], key=lambda r: r["sessions"])
    steps = step_series(rows, grid)
    settle = settled_at(steps)
    decay = decay_increments(steps)
    top = grid[-1]
    top_edges = [((r.get("by_draws") or {}).get(str(top)) or {}).get("edge_self") for r in rows]
    top_edges = [e for e in top_edges if e]
    biggest = max(rows, key=lambda r: r["sessions"]) if rows else None
    return {"rungs": len(rows),
            "tops": {"draws": top, "rungs_measured": len(top_edges),
                     "edge_at_largest_rung": (top_edges[-1] if top_edges else None),
                     "edge_min": (min(top_edges) if top_edges else None),
                     "edge_max": (max(top_edges) if top_edges else None)},
            "largest_rung_sessions": ((biggest or {}).get("sessions")),
            "steps": steps, "settled": settle, "increment": decay,
            "state": ("unmeasured" if not rows
                      else "settled" if settle["settled"]
                      else "no_decay" if decay.get("no_decay")
                      else "decaying")}


def verdict_from(analysis, top=D_BUDGET):
    """Frozen verdict: the weakest family decides, because the two are different experiments."""
    if not analysis or any(not (analysis.get(k) or {}).get("rungs") for k in FAMILIES):
        return "no_rungs_measured", "a family measured no rungs, so nothing is published"
    states = {k: analysis[k]["state"] for k in FAMILIES}
    if all(v == "settled" for v in states.values()):
        return ("endpoint_settles_within_the_grid",
                "no rung moves more than %.1f%% per step from %s draws up"
                % (CONV_PCT, "/".join(str(analysis[k]["settled"]["draws"]) for k in FAMILIES)))
    if all(v in ("settled", "no_decay") for v in states.values()):
        plateau = {k: (analysis[k].get("increment") or {}).get("plateau_pct_per_doubling")
                   for k in FAMILIES}
        return ("increments_do_not_decay_with_draws",
                "the endpoint never settles, and later doublings add no less than earlier ones "
                "(HEAD %s, TAIL %s percent per doubling): the band has no countable stopping "
                "point inside the measured grid"
                % (fmt_pct(plateau["head"]), fmt_pct(plateau["tail"])))
    return ("endpoint_still_rising_at_the_budget",
            "the endpoint is still rising at %d draws and the per-doubling rise is still "
            "shrinking (states HEAD=%s TAIL=%s), so more draws may still buy a flatter band"
            % (top, states["head"], states["tail"]))


def run(per=None, save=True, outdir=None, seeds=SEEDS, d_grid=D_GRID, n_grid=e254.N_GRID,
        tag=""):
    per = per if per is not None else e239.panels()
    syms = [s for s in e252.BASKET if per.get(s)]
    m = e255.measure(per, syms, seeds=seeds, d_grid=d_grid, n_grid=n_grid)
    tables = e255.build_tables(m)
    analysis = {k: analyse([r for r in m["rungs"] if r["family"] == k], d_grid)
                for k in FAMILIES}
    verdict, why = verdict_from(analysis, top=max(d_grid))
    converged = {}
    for k in FAMILIES:
        rows = sorted(tables[k]["rows"], key=lambda r: r["draws"])
        converged[k] = rows[-1] if rows else {}
    e254_verdict, e254_why = e254.verdict_from(
        {k: converged[k].get("gamma") for k in FAMILIES},
        {k: converged[k].get("r2") for k in FAMILIES})
    gh, gt = converged.get("head", {}).get("gamma"), converged.get("tail", {}).get("gamma")
    pub = e254.read_published()
    targets = {}
    for k in FAMILIES:
        a = analysis[k]
        g = converged[k].get("gamma")
        edge = a["tops"]["edge_at_largest_rung"]
        if not edge or g is None or not pub.get("b_self") or not a["largest_rung_sessions"]:
            targets[k] = None
            continue
        targets[k] = e253.needed_sessions(a["largest_rung_sessions"], pub["b_self"], edge, g)
    secondary = {
        "converged_draws": max(d_grid),
        "conv_pct": CONV_PCT,
        "grid_prefix_nested": (all(b > a for a, b in zip(d_grid, d_grid[1:])),
                               "one stream at max(draw_grid) per seed; every smaller count reads "
                               "its own PREFIX"),
        "e254_verdict_at_top_draws": e254_verdict,
        "e254_reason_at_top_draws": e254_why,
        "family_gamma_gap": (None if (gh is None or gt is None) else abs(gh - gt)),
        "gamma_tol": e255.GAMMA_TOL,
        "target_sessions_at_top_gamma": targets,
        "target_b_self": pub.get("b_self"),
        "target_sessions_available": (m["era_grid"] or {}).get("sessions"),
        "caveats": [
            "the two families are different experiments (fixed start vs fixed end), so a family "
            "that settles while the other does not is a statement that the band is not one object",
            "prefix nesting makes the six columns one experiment, but it also means the smaller "
            "counts are re-read from the same stream: their agreement is not independent evidence",
            "target_sessions_at_top_gamma is a FLOOR whenever the endpoint has not settled",
            "the seed scatter is a 2-degree-of-freedom estimate (3 seeds) and E255 found it did "
            "not fall with draws, so it ships as a flag, not a ratio"]}
    face = {"study": STUDY,
            "title": "at which draw count does the band endpoint stop moving?",
            "generated": datetime.now().isoformat(timespec="seconds"),
            "evidence_cutoff": (m["era_grid"] or {}).get("last") or "unknown",
            "frozen_spec": {"era": [e255.ERA_LO, e255.ERA_HI],
                            "cell_label": e255.CELL_LABEL,
                            "n_grid": list(n_grid), "draw_grid": list(d_grid),
                            "n_min": e254.N_MIN, "seeds": seeds,
                            "base_seed": e255.BASE_SEED,
                            "families": list(FAMILIES),
                            "conv_pct": CONV_PCT, "flat_rel_tol": FLAT_REL_TOL,
                            "r2_floor": e255.R2_FLOOR, "gamma_tol": e255.GAMMA_TOL,
                            "draw_budget": max(d_grid),
                            "verdict_vocabulary": list(VERDICTS),
                            "prefix_nesting": "one draw stream at max(draw_grid) per seed; every "
                                              "smaller draw count reads its own PREFIX",
                            "what_is_not_done": [
                                "no coefficient is re-priced: only the shuffled band is rebuilt",
                                "no bootstrap, no bill, no adoption",
                                "the rung set is identical at every draw count",
                                "E255's frozen 2% convergence line is reused, not re-tuned"]},
            "era": m["era_grid"], "pinned_star": m.get("pinned_star"),
            "pinned_star_source": m.get("pinned_star_source"),
            "rungs": m["rungs"], "rungs_missing": m["rungs_missing"],
            "tables": tables,
            "continuation": analysis,
            "verdict": verdict, "verdict_reason": why,
            "verdict_inputs": {"conv_pct": CONV_PCT, "flat_rel_tol": FLAT_REL_TOL,
                               "draw_grid": list(d_grid)},
            "secondary_reads": secondary}
    face["summary"] = _summary(face)
    if save:
        face["written"] = _write(face, outdir or OUTDIR, tag)
    return face


def _summary(face):
    cont = face["continuation"]
    return {"verdict": face["verdict"], "verdict_reason": face["verdict_reason"],
            "era_sessions": face["era"]["sessions"],
            "draw_grid": face["frozen_spec"]["draw_grid"],
            "settled_after_draws": {k: cont[k]["settled"]["draws"] for k in FAMILIES},
            "family_state": {k: cont[k]["state"] for k in FAMILIES},
            "median_rise_pct_by_step": {
                k: {"%d->%d" % (s["from"], s["to"]): s["median_rise_pct"]
                    for s in cont[k]["steps"]} for k in FAMILIES},
            "max_abs_rise_pct_by_step": {
                k: {"%d->%d" % (s["from"], s["to"]): s["max_abs_rise_pct"]
                    for s in cont[k]["steps"]} for k in FAMILIES},
            "decay_ratio_second_half_over_first": {
                k: cont[k]["increment"]["ratio_second_half_over_first"] for k in FAMILIES},
            "step_oscillates": {k: cont[k]["increment"]["oscillates"] for k in FAMILIES},
            "plateau_pct_per_doubling": {k: cont[k]["increment"]["plateau_pct_per_doubling"]
                                         for k in FAMILIES},
            "edge_at_largest_rung": {k: cont[k]["tops"]["edge_at_largest_rung"]
                                     for k in FAMILIES},
            "gamma_by_draws": {k: {str(r["draws"]): r["gamma"] for r in face["tables"][k]["rows"]}
                               for k in FAMILIES},
            "r2_by_draws": {k: {str(r["draws"]): r["r2"] for r in face["tables"][k]["rows"]}
                            for k in FAMILIES},
            "rungs": {k: cont[k]["rungs"] for k in FAMILIES},
            "secondary_reads": face.get("secondary_reads")}


def _write(face, outdir, tag=""):
    """Write the face. `tag` names a VARIANT so a re-read can never overwrite another variant."""
    os.makedirs(outdir, exist_ok=True)
    cutoff = face.get("evidence_cutoff") or "unknown"
    face["path"] = None
    latest = os.path.join(outdir, "banddraw%s_latest.json" % tag)
    head = os.path.join(outdir, "BANDDRAW-%s%s.json" % (cutoff, tag or "-d%d" % D_BUDGET))
    payload = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    with open(head, "w", encoding="utf-8") as fh:
        fh.write(payload + "\n")
    with open(latest, "w", encoding="utf-8") as fh:
        fh.write(payload + "\n")
    return {"face": os.path.relpath(head, ROOT).replace("\\", "/"),
            "latest": os.path.relpath(latest, ROOT).replace("\\", "/"),
            "bytes": len(payload)}


def _r(v, n=4):
    return None if v is None else round(float(v), n)


def _fmt(face):
    s = face["summary"]
    steps = {k: {kk: _r(vv, 3) for kk, vv in v.items()}
             for k, v in s["median_rise_pct_by_step"].items()}
    return ("%s | verdict %s (%s) | settled after %s | state %s | rise/doubling %s | "
            "edge@%d head %s tail %s"
            % (face["study"], s["verdict"], s["verdict_reason"],
               s["settled_after_draws"], s["family_state"], steps,
               face["frozen_spec"]["draw_grid"][-1],
               _r(s["edge_at_largest_rung"].get("head"), 4),
               _r(s["edge_at_largest_rung"].get("tail"), 4)))


def verify(outdir=None, tag=""):
    """Re-read the face and recompute every published continuation number from its own rungs."""
    outdir = outdir or OUTDIR
    problems = []
    suffix = tag or "-d%d" % D_BUDGET
    latest = os.path.join(outdir, "banddraw%s_latest.json" % suffix)
    if not os.path.exists(latest):
        head = sorted([p for p in os.listdir(outdir)
                       if p.startswith("BANDDRAW-") and p.endswith("%s.json" % suffix)])
        if head:
            latest = os.path.join(outdir, head[-1])
    if not os.path.exists(latest):
        return {"ok": False, "problems": ["no face at %s" % latest]}
    with open(latest, encoding="utf-8") as fh:
        face = json.load(fh)
    grid = face.get("frozen_spec", {}).get("draw_grid") or []
    if len(grid) < 2:
        problems.append("draw grid has %d points" % len(grid))
    analysis = {}
    for k in FAMILIES:
        rungs = [r for r in face.get("rungs") or [] if r.get("family") == k]
        analysis[k] = analyse(rungs, grid)
        pub = (face.get("continuation") or {}).get(k) or {}
        if pub.get("state") != analysis[k]["state"]:
            problems.append("family %s state %s != recomputed %s"
                            % (k, pub.get("state"), analysis[k]["state"]))
        if (pub.get("settled") or {}).get("draws") != analysis[k]["settled"]["draws"]:
            problems.append("family %s settled_after_draws does not reproduce" % k)
        pub_steps = pub.get("steps") or []
        if len(pub_steps) != len(analysis[k]["steps"]):
            problems.append("family %s publishes %d steps, grid implies %d"
                            % (k, len(pub_steps), len(analysis[k]["steps"])))
        for a, b in zip(pub_steps, analysis[k]["steps"]):
            if a.get("median_rise_pct") is None or b.get("median_rise_pct") is None:
                continue
            if abs(a["median_rise_pct"] - b["median_rise_pct"]) > 1e-9:
                problems.append("family %s step %s->%s median does not reproduce"
                                % (k, a.get("from"), a.get("to")))
    want, _why = verdict_from(analysis, top=max(grid))
    if face.get("verdict") != want:
        problems.append("verdict %s != recomputed %s" % (face.get("verdict"), want))
    if face.get("verdict") not in VERDICTS:
        problems.append("verdict %s is not in the frozen vocabulary" % face.get("verdict"))
    # the rung SET must be identical at every draw count -- the experiment's premise
    for k in FAMILIES:
        seen = set()
        for r in face.get("rungs") or []:
            if r.get("family") == k:
                seen.add(str(sorted((r.get("by_draws") or {}).keys())))
        if len(seen) > 1:
            problems.append("family %s does not carry the same draw grid at every rung" % k)
    if not face.get("evidence_cutoff"):
        problems.append("evidence_cutoff missing")
    if (face.get("summary") or {}).get("settled_after_draws") != {
            k: analysis[k]["settled"]["draws"] for k in FAMILIES}:
        problems.append("summary.settled_after_draws does not match the continuation block")
    return {"ok": not problems, "problems": problems, "verdict": face.get("verdict"),
            "draws": grid, "rungs": len(face.get("rungs") or [])}


# ---------------------------------------------------------------- selftest fixtures
def leg(ok, name, detail=None):
    return {"leg": name, "pass": bool(ok), "detail": detail}


def _fake_rungs(series_by_rung, grid):
    """series_by_rung: {sessions: [edge at each grid point]} -> rung dicts like measure() emits."""
    out = []
    for n, series in series_by_rung.items():
        by = {}
        for d, e in zip(grid, series):
            by[str(d)] = {"draws": d, "edge_self": e}
        out.append({"family": "head", "sessions": n, "n_requested": n, "by_draws": by})
    return out


def selftest():
    legs = []
    grid = (60, 120, 240, 480)

    # 1 step_series reads the same rung twice: a flat series has zero rise at every step
    flat = _fake_rungs({200: [0.5, 0.5, 0.5, 0.5]}, grid)
    st = step_series(flat, grid)
    legs.append(leg(len(st) == 3 and all(abs(s["median_rise_pct"]) < 1e-12 for s in st),
                    "a flat ladder publishes zero rise at every step", st))

    # 2 a rung that rises 10% then 5% publishes both, relative to its own previous count
    rises = _fake_rungs({200: [1.0, 1.1, 1.155, 1.155]}, grid)
    st = step_series(rises, grid)
    legs.append(leg(abs(st[0]["median_rise_pct"] - 10.0) < 1e-9
                    and abs(st[1]["median_rise_pct"] - 5.0) < 1e-9
                    and abs(st[2]["median_rise_pct"]) < 1e-9,
                    "rises are percent of the lower draw count", st))

    # 3 settled_at returns the FIRST point after which everything is inside the line, and it must
    #   be that point and not the last step: a single quiet step is not convergence
    quiet_top = _fake_rungs({200: [1.0, 1.20, 1.21, 1.215]}, grid)
    s1 = settled_at(step_series(quiet_top, grid))
    legs.append(leg(s1["settled"] is True and s1["draws"] == 120,
                    "settled_at names the first grid point of the quiet tail, not the last step",
                    s1))

    # 4 a ladder that rises 5% at every step never settles
    all_rise = _fake_rungs({200: [1.0, 1.05, 1.1025, 1.157625]}, grid)
    s2 = settled_at(step_series(all_rise, grid))
    legs.append(leg(s2["settled"] is False and s2["draws"] is None,
                    "a ladder that keeps rising never settles", s2))

    # 5 the 2% line is inclusive: a max rise of exactly 2.0% counts as settled
    exact = _fake_rungs({200: [1.0, 1.02, 1.0404, 1.061208]}, grid)
    s3 = settled_at(step_series(exact, grid))
    legs.append(leg(s3["settled"] is True,
                    "the frozen convergence line is inclusive (<= 2.0%)", s3))

    # 6 one rung inside the line and one outside is NOT settled -- the rule is every rung
    mixed = _fake_rungs({200: [1.0, 1.02, 1.04, 1.06], 300: [1.0, 1.20, 1.50, 1.60]}, grid)
    s4 = settled_at(step_series(mixed, grid))
    legs.append(leg(s4["settled"] is False,
                    "a single rung still moving keeps the family unsettled", s4))

    # 7 a step with no measurable rungs cannot establish convergence
    missing = _fake_rungs({200: [1.0, 1.02, None, None]}, grid)
    s5 = settled_at(step_series(missing, grid))
    legs.append(leg(s5["settled"] is False,
                    "an unmeasured step cannot be read as a quiet step", s5))

    # 8 a constant per-doubling rise does not decay: later doublings add the same as earlier ones
    plateau = _fake_rungs({200: [1.0, 1.1, 1.21, 1.331]}, grid)
    f1 = decay_increments(step_series(plateau, grid))
    legs.append(leg(f1["no_decay"] is True and abs(f1["ratio_second_half_over_first"] - 1.0) < 0.05,
                    "a constant per-doubling rise is published as no-decay", f1))

    # 9 shrinking increments: 10% then 2.5% means more draws may still buy a flatter band
    shrink = _fake_rungs({200: [1.0, 1.10, 1.1275, 1.13]}, grid)
    f2 = decay_increments(step_series(shrink, grid))
    legs.append(leg(f2["no_decay"] is False,
                    "a decaying per-doubling rise is published as decaying", f2))

    # 10 THE r1283 DEFECT, pinned: the single-pair rule called 8.8/1.6/9.8/5.2/10.3 a plateau
    #    because its last step exceeded the one before it. One pair cannot tell an oscillation
    #    from a floor, so the half split must report no-decay AND flag the oscillation.
    osc_grid = (60, 120, 240, 480, 960, 1920)
    series, acc = [1.0], 1.0
    for pct in (8.8, 1.6, 9.8, 5.2, 10.3):
        acc *= (1.0 + pct / 100.0)
        series.append(acc)
    f_osc = decay_increments(step_series(_fake_rungs({200: series}, osc_grid), osc_grid))
    pairs = [s["median_rise_pct"] for s in step_series(_fake_rungs({200: series}, osc_grid),
                                                       osc_grid)]
    old_rule_ratio = pairs[-1] / pairs[-2] if pairs[-2] else None
    legs.append(leg(f_osc["no_decay"] is True and f_osc["oscillates"] is True
                    and f_osc["steps_monotone_decreasing"] is False
                    and old_rule_ratio is not None and old_rule_ratio > 1.0,
                    "an oscillating step sequence is published no-decay WITH the oscillation "
                    "flag (the one-pair ratio reads as a rise, which is why one pair is not a test)",
                    {"osc": f_osc, "old_rule_lastpair_ratio": old_rule_ratio}))

    # 11 one doubling step is not enough to compare a ratio
    f4 = decay_increments(step_series(_fake_rungs({200: [1.0, 1.1]}, (60, 120)), (60, 120)))
    legs.append(leg(f4["no_decay"] is None and "fewer than two" in f4["reason"],
                    "no-decay needs two doubling steps", f4))

    # 12 a second half that turns NEGATIVE is not a positive plateau whatever the ratio says
    decline = _fake_rungs({200: [1.0, 1.10, 1.21, 1.20]}, grid)
    f3 = decay_increments(step_series(decline, grid))
    legs.append(leg(f3["no_decay"] is False,
                    "a step that turns negative is not published as a positive plateau", f3))

    # 13 a first half that adds nothing leaves the ratio undefined rather than infinite
    zero_first = decay_increments([{"is_doubling": True, "median_rise_pct": 0.0},
                                   {"is_doubling": True, "median_rise_pct": 5.0},
                                   {"is_doubling": True, "median_rise_pct": 5.0}])
    legs.append(leg(zero_first["no_decay"] is None
                    and "zero" in zero_first["reason"],
                    "a zero first half publishes no ratio instead of dividing by zero",
                    zero_first))

    # 12 analyse on a settled family says 'settled' and carries the top edge
    a = analyse(_fake_rungs({200: [1.0, 1.20, 1.21, 1.215]}, grid), grid)
    legs.append(leg(a["state"] == "settled" and a["rungs"] == 1
                    and abs(a["tops"]["edge_at_largest_rung"] - 1.215) < 1e-12,
                    "analyse publishes state, rungs and the top edge together", a))

    # 13 analyse on no rungs is 'unmeasured', not a vacuous 'settled'
    a2 = analyse([], grid)
    legs.append(leg(a2["state"] == "unmeasured" and a2["settled"]["settled"] is False,
                    "an empty family is unmeasured, never settled", a2))

    # 14 the verdict is the weakest family: one settled + one DECAYING is not 'settles'
    one = {"head": {"rungs": 1, "state": "settled"},
           "tail": {"rungs": 1, "state": "decaying"}}
    legs.append(leg(verdict_from(one)[0] == "endpoint_still_rising_at_the_budget",
                    "the verdict is the weakest family", verdict_from(one)))

    # 15 settled + no-decay is the plateau verdict: no countable stopping point in the grid
    two = {"head": {"rungs": 1, "state": "settled"},
           "tail": {"rungs": 1, "state": "no_decay"}}
    legs.append(leg(verdict_from(two)[0] == "increments_do_not_decay_with_draws",
                    "settled plus no-decay is published as the plateau verdict", verdict_from(two)))

    # 16 an empty family blocks every positive verdict
    three = {"head": {"rungs": 0, "state": "unmeasured"},
             "tail": {"rungs": 1, "state": "settled"}}
    legs.append(leg(verdict_from(three)[0] == "no_rungs_measured",
                    "a family with no rungs publishes no_rungs_measured", verdict_from(three)))

    # 17 the verdict function is total over its frozen vocabulary
    produced = {verdict_from(one)[0], verdict_from(two)[0], verdict_from(three)[0]}
    legs.append(leg(produced.issubset(set(VERDICTS)),
                    "every produced verdict is in the frozen vocabulary", sorted(produced)))

    # 18 grid ordering: a non-increasing grid cannot be prefix-nested, so the face must say so
    bad = step_series(_fake_rungs({200: [1.0, 1.1]}, (240, 120)), (240, 120))
    legs.append(leg(bad[0]["is_doubling"] is False,
                    "a step that is not a doubling is flagged rather than assumed", bad[0]))

    # 19 identity: the log-increments of a series sum to log(top/bottom)
    series = [1.0, 1.234, 1.4, 1.41]
    prod = 1.0
    for s in step_series(_fake_rungs({200: series}, grid), grid):
        prod *= (1.0 + s["median_rise_pct"] / 100.0)
    legs.append(leg(abs(prod - series[-1] / series[0]) < 1e-9,
                    "chained steps reconstruct the total rise", {"product": prod}))

    passed = sum(1 for x in legs if x["pass"])
    return {"legs": legs, "passed": passed, "total": len(legs), "ok": passed == len(legs)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", nargs="?", default="run", choices=("run", "selftest", "verify"))
    ap.add_argument("--seeds", type=int, default=SEEDS)
    ap.add_argument("--grid", default="",
                    help="comma-separated draw grid (must be strictly increasing)")
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
        r = verify(tag=args.tag)
        for p in r["problems"]:
            print("PROBLEM %s" % p)
        print("verify[%s]: grid=%s verdict=%s -> %s"
              % (args.tag or "base", r.get("draws"), r.get("verdict"),
                 "OK" if r["ok"] else "FAIL"))
        return 0 if r["ok"] else 1
    grid = D_GRID
    if args.grid:
        grid = tuple(int(x) for x in args.grid.split(",") if x.strip())
        if list(grid) != sorted(set(grid)):
            raise SystemExit("--grid must be strictly increasing")
    face = run(seeds=args.seeds, d_grid=grid, tag=args.tag)
    print(_fmt(face))
    print("written: %s" % (face.get("written") or {}).get("face"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())