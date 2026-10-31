"""E295 -- both margins are one step away, or so it looked: price what ONE MORE RUNG of the draw
ladder actually buys, and whether any rung the family already measured is on the other side of
either margin.

E287 measured that the published supplies stop 3.80 pct above the nearest above-ceiling row
(self|200|0 flip 2.331055 vs the optimistic cap 2.245734) and that the narrowing instrument 0.922022
stops 3.67 pct above the nearest below-floor row (self|60|8 flip 0.889387). Both numbers invite the
same follow-up -- "surely one more rung closes that" -- and this face answers it with arithmetic on
published records only.

The draw ladder the family already measured is E256's: 14 rungs (2 families x 7 session counts) x 6
draw counts, one draw stream per seed read as a prefix at every smaller count. Two things can be
priced off it:

  * STEP. What a single grid step buys: edge(d_next) / edge(d_cur) on matched seeds. This is the
    granularity question -- if a median step buys more than the margin, the margin was never a
    resolution problem and grinding the grid finer cannot be the fix.
  * SPAN. What the ladder reaches at all: edge(1920) / edge(60) per rung. This is the headroom
    question -- if the demand sits above every rung of the ladder, then no interpolation is
    legitimate and an extrapolation would be an invention.

Both margins are read against the reference the family publishes for that polarity (E287's caps),
and the crossing test is only run where the demand and the ladder describe the SAME window: E258
measured that a window's multiplier differs from another window's by more than 15 pct, so borrowing
a rung across windows would price a different sleeve's null (its BASIS_WARNING, carried here).

DECISION RULE, declared before a number is read:

  M1 AXIS     only an absolute band-edge multiplier is compared with a demand flip (E287's reach
              rule: a widening demand is reached iff cap >= flip, a narrowing one iff cap <= flip).
              Percentages are used for the margin SIZE and the step GAIN, never as a cap.
  M2 WINDOW   a ladder rung may only be graded against a demand published in the ladder's own
              window; a demand from another window is published as not_graded with that reason and
              is never counted as a crossing or a shortfall.
  M3 STEP     the price of one more rung is the adjacent-grid step multiplier, matched seed for
              seed; the ladder's span is edge(largest draw) / edge(base draw) on the same rung.
  M4 CROSS    a margin is crossed iff some published rung in the same window reaches the demand on
              the demand's own polarity; the count of crossing rungs is published, not just a yes.
  M5 ABORT    when no rung crosses, the residual factor is published and the interpolation is
              declared aborted -- no value between or beyond rungs is fitted, because the next rung
              (a larger draw budget) is a different, billable decision.
  M6 NOBILL   published faces are re-read: no draw stream is drawn, no band rebuilt, no engine run.
  M7 SEEDS    every rung is published on three bases -- central (the face's own ratio of central
              edges), matched-seed MIN and matched-seed MAX -- and a crossing that exists at one
              seed only is published as seed-dependent, never as a crossing verdict.

Verdict vocabulary (frozen):
  published_ladder_crosses_both_margins_on_the_central_basis
  one_margin_is_crossed_by_a_single_seed_rung_only
  no_published_ladder_rung_crosses_a_margin

Usage:  python scripts/e295_supply_gap_closure.py run|verify|selftest
"""
import io
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e272_flip_budget_two_tails as e272  # noqa: E402  (ROOT / OUTDIR)
import e287_supply_ceiling_axes as e287     # noqa: E402  (the published caps + loader)

ROOT = e272.ROOT
OUTDIR = e272.OUTDIR

STUDY = "E295_supply_gap_closure"
TITLE = ("one more rung or none -- what does a single step of the published draw ladder buy, does "
         "any existing rung sit beyond either margin, and how much of each margin is resolution "
         "and how much is headroom?")
CUTOFF = "2026-10-29"
SRC_GAPCEIL = e287.SRC_GAPCEIL      # E285: the twelve demand rows, each with its own cell
SRC_SUPPLY = "BANDSUPPLY-%s.json" % CUTOFF   # E287: the published caps per polarity
SRC_LADDER = "BANDDRAW-%s-d1920.json" % CUTOFF   # E256: rungs x draw counts, one stream per seed
SRC_WINMULT = e287.SRC_WINMULT      # E258: per-window multipliers (reproduction witness)
SRC_TOPFLIP = e287.SRC_TOPFLIP      # E257: per-rung multipliers at the top draw count
SRC_FLOOR = e287.SRC_FLOOR          # BANDFLOOR: the published narrowing instrument
FACE = "BANDCLOSURE-%s.json" % CUTOFF
LATEST = "bandclosure_latest.json"
SELF_FACES = (FACE, LATEST)

TOL = 1e-12
BASE_DRAWS = 60          # the ladder's own floor draw count (E256 grid)

VERDICT_VOCAB = (
    "published_ladder_crosses_both_margins_on_the_central_basis",
    "one_margin_is_crossed_by_a_single_seed_rung_only",
    "no_published_ladder_rung_crosses_a_margin",
)

NO_BILL = ("measurement only: published faces are re-read and their published multipliers compared "
           "with the published demand rows. No draw stream is drawn, no band rebuilt, no engine "
           "runs. A verdict is a statement about the rungs the family has already measured, not "
           "about what a larger draw budget would buy.")


# ------------------------------------------------------------------ io
def load(name, outdir=None):
    return e287.load(name, outdir)


def _num(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fmt(value, digits=6):
    return "n/a" if value is None else ("%." + str(digits) + "f") % value


def _round(value, digits=12):
    return None if value is None else round(value, digits)


# ------------------------------------------------------------------ ladder
def _draw_cell(rung, draws):
    return (rung.get("by_draws") or {}).get(str(int(draws)))


def matched_seed_mults(base_cell, top_cell):
    """M7/M3: per-seed multiplier, seed for seed. Never max(top)/min(base) -- that splices seeds."""
    b = base_cell.get("edge_self_per_seed") or []
    t = top_cell.get("edge_self_per_seed") or []
    if not b or len(b) != len(t):
        return None
    if any(x is None or y is None for x, y in zip(b, t)):
        return None
    out = []
    for x, y in zip(b, t):
        x = _num(x)
        y = _num(y)
        if not x:
            return None
        out.append(y / x)
    return out


def price_rung(rung, draws, base_draws=BASE_DRAWS):
    """M3/M7: the multiplier one rung buys, on the three published bases."""
    base = _draw_cell(rung, base_draws)
    top = _draw_cell(rung, draws)
    if not base or not top:
        return None
    eb, et = _num(base.get("edge_self")), _num(top.get("edge_self"))
    central = None if (eb is None or not eb) else et / eb
    seeds = matched_seed_mults(base, top)
    return {
        "family": rung.get("family"), "sessions": rung.get("sessions"),
        "base_draws": base_draws, "draws": int(draws),
        "edge_base": eb, "edge_top": et,
        "multiplier_central": _round(central),
        "multiplier_seed_min": None if not seeds else _round(min(seeds)),
        "multiplier_seed_max": None if not seeds else _round(max(seeds)),
        "multiplier_seed_median": None if not seeds else _round(statistics.median(seeds)),
        "n_seeds": None if not seeds else len(seeds),
    }


def ladder_readings(face, base_draws=BASE_DRAWS):
    grid = [int(g) for g in (face.get("frozen_spec") or {}).get("draw_grid") or []]
    out = []
    for rung in (face.get("rungs") or []):
        for draws in grid:
            if draws <= base_draws:
                continue
            rec = price_rung(rung, draws, base_draws)
            if rec:
                out.append(rec)
    return out, grid


def step_readings(face, grid, base_draws=BASE_DRAWS):
    """M3: what a single adjacent grid step buys, matched seed for seed."""
    out = []
    for rung in (face.get("rungs") or []):
        for i in range(len(grid) - 1):
            lo, hi = grid[i], grid[i + 1]
            if lo < base_draws:
                continue
            a, b = _draw_cell(rung, lo), _draw_cell(rung, hi)
            if not a or not b:
                continue
            ea, eb = _num(a.get("edge_self")), _num(b.get("edge_self"))
            seeds = matched_seed_mults(a, b)
            out.append({
                "family": rung.get("family"), "sessions": rung.get("sessions"),
                "from_draws": lo, "to_draws": hi,
                "gain_central": (None if (ea is None or not ea) else _round(eb / ea)),
                "gain_seed_min": None if not seeds else _round(min(seeds)),
                "gain_seed_max": None if not seeds else _round(max(seeds)),
            })
    return sorted(out, key=lambda r: (r["family"], r["sessions"], r["from_draws"]))


def span_block(readings):
    """M3/M5: what the ladder reaches at all, on each basis."""
    scored = [r for r in readings if r.get("multiplier_central") is not None]
    if not scored:
        return {"n_readings": 0, "central_min": None, "central_max": None,
                "seed_max": None, "seed_min": None, "at": None, "seed_at": None,
                "stated": "no rung could be priced"}
    cmax = max(scored, key=lambda r: r["multiplier_central"])
    cmin = min(scored, key=lambda r: r["multiplier_central"])
    seedable = [r for r in scored if r.get("multiplier_seed_max") is not None]
    smax = max(seedable, key=lambda r: r["multiplier_seed_max"]) if seedable else None
    smin = min(seedable, key=lambda r: r["multiplier_seed_min"]) if seedable else None

    def _at(r, key):
        return None if r is None else {"family": r["family"], "sessions": r["sessions"],
                                       "draws": r["draws"], key: r[key]}

    return {
        "n_readings": len(scored),
        "central_min": cmin["multiplier_central"],
        "central_max": cmax["multiplier_central"],
        "seed_min": None if smin is None else smin["multiplier_seed_min"],
        "seed_max": None if smax is None else smax["multiplier_seed_max"],
        "at": _at(cmax, "multiplier_central"),
        "seed_at": _at(smax, "multiplier_seed_max"),
        "stated": ("the ladder spans %s..%s on the central basis and %s..%s across its own seeds"
                   % (_fmt(cmin["multiplier_central"]), _fmt(cmax["multiplier_central"]),
                      _fmt(None if smin is None else smin["multiplier_seed_min"]),
                      _fmt(None if smax is None else smax["multiplier_seed_max"]))),
    }


def step_block(steps, widen_factor=None):
    gains = [s["gain_central"] for s in steps if s.get("gain_central") is not None]
    if not gains:
        return {"n_steps": 0, "median_gain": None, "share_finer_than_the_widening_margin": None,
                "n_below_one": 0, "stated": "no adjacent step could be priced"}
    finer = None
    if widen_factor is not None:
        finer = sum(1 for g in gains if g >= widen_factor)
    return {
        "n_steps": len(gains),
        "min_gain": min(gains),
        "median_gain": _round(statistics.median(gains)),
        "max_gain": max(gains),
        "n_gains_at_or_above_the_widening_margin": finer,
        "share_finer_than_the_widening_margin": (None if finer is None
                                                 else _round(finer / float(len(gains)))),
        "n_below_one": sum(1 for g in gains if g < 1.0),
        "stated": ("%d adjacent step(s) between draw rungs, median gain %s, range %s..%s; %s of them "
                   "buy more than the widening margin on their own"
                   % (len(gains), _fmt(statistics.median(gains)), _fmt(min(gains)),
                      _fmt(max(gains)), "n/a" if finer is None else finer)),
    }


# ------------------------------------------------------------------ margins
def demands(gap_face):
    """Every published demand row, with the window (cell) it was published in."""
    out = []
    for arm in (gap_face.get("arms") or []):
        for rec in (arm.get("rows") or []):
            flip = _num(rec.get("flip"))
            if flip is None:
                continue
            out.append({"row_key": rec.get("row_key"), "cell": rec.get("cell"),
                        "class": rec.get("class"), "flip": flip,
                        "arm": arm.get("arm")})
    return out


def crossing(reading, flip, direction):
    """M1/M4: the published reach rule on the demand's own polarity, per basis."""
    def ok(value):
        if value is None:
            return None
        return bool(value >= flip - TOL) if direction == "widen" else bool(value <= flip + TOL)

    return {"central": ok(reading.get("multiplier_central")),
            "seed_min": ok(reading.get("multiplier_seed_min")),
            "seed_max": ok(reading.get("multiplier_seed_max"))}


def grade_margin(row, readings, span, reference, direction):
    """M2/M4/M5/M7: one demand row graded against the ladder, plus its abort status."""
    flip = row["flip"]
    cap = _num((reference or {}).get("value"))
    basis = "widen" if direction == "widen" else "narrow"
    if cap is None:
        margin_factor = margin_pct = None
    elif basis == "widen":
        margin_factor = flip / cap
        margin_pct = (flip / cap - 1.0) * 100.0
    else:
        margin_factor = flip / cap
        margin_pct = (cap - flip) / cap * 100.0

    scored = []
    for rec in readings:
        c = crossing(rec, flip, basis)
        scored.append({"family": rec["family"], "sessions": rec["sessions"], "draws": rec["draws"],
                       "multiplier_central": rec["multiplier_central"],
                       "multiplier_seed_max": rec["multiplier_seed_max"],
                       "multiplier_seed_min": rec["multiplier_seed_min"],
                       "reaches": c})
    crossed_central = [r for r in scored if r["reaches"]["central"] is True]
    crossed_seed_max = [r for r in scored if r["reaches"]["seed_max"] is True]

    # closest rung on the demand's own polarity (the ladder's own extreme, not a fitted one)
    if basis == "widen":
        closest = max([r for r in scored if r["multiplier_central"] is not None],
                      key=lambda r: r["multiplier_central"]) if scored else None
        residual = (None if closest is None else flip / closest["multiplier_central"])
    else:
        closest = min([r for r in scored if r["multiplier_central"] is not None],
                      key=lambda r: r["multiplier_central"]) if scored else None
        residual = (None if closest is None else closest["multiplier_central"] / flip)

    return {
        "row_key": row["row_key"], "cell": row["cell"], "class": row["class"], "flip": flip,
        "direction": basis,
        "reference": {"face": (reference or {}).get("face"),
                      "label": (reference or {}).get("label"), "value": cap},
        "margin_factor": _round(margin_factor),
        "margin_pct": _round(margin_pct, 6),
        "crossed_central": bool(crossed_central),
        "crossed_at_one_seed": bool(crossed_seed_max),
        "n_rungs_crossing_central": len(crossed_central),
        "n_rungs_crossing_at_one_seed": len(crossed_seed_max),
        "n_rungs_graded": len(scored),
        "closest_rung": None if closest is None else {
            "family": closest["family"], "sessions": closest["sessions"],
            "draws": closest["draws"], "multiplier_central": closest["multiplier_central"]},
        "residual_factor": _round(residual),
        "interpolation_aborted": not crossed_central,
        "abort_statement": (None if crossed_central else
                            "no published rung reaches %s on this polarity; the demand lies outside "
                            "the ladder's measured span by a factor of %s, so nothing between or "
                            "beyond the rungs is interpolated -- a larger draw budget is a "
                            "different, billable decision (M5)" % (_fmt(flip), _fmt(residual))),
    }


def verdict_of(margins):
    graded = [m for m in margins if m]
    if not graded:
        return "no_published_ladder_rung_crosses_a_margin"
    if all(m["crossed_central"] for m in graded):
        return "published_ladder_crosses_both_margins_on_the_central_basis"
    if any(m["crossed_central"] for m in graded):
        return "published_ladder_crosses_both_margins_on_the_central_basis" if len(graded) == 1 \
            else "one_margin_is_crossed_by_a_single_seed_rung_only"
    if any(m["crossed_at_one_seed"] for m in graded):
        return "one_margin_is_crossed_by_a_single_seed_rung_only"
    return "no_published_ladder_rung_crosses_a_margin"


# ------------------------------------------------------------------ build
def build(outdir=None):
    outdir = outdir or OUTDIR
    gap = load(SRC_GAPCEIL, outdir)
    supply = load(SRC_SUPPLY, outdir)
    ladder = load(SRC_LADDER, outdir)
    winmult = load(SRC_WINMULT, outdir)
    floor = load(SRC_FLOOR, outdir)

    cell = (ladder.get("frozen_spec") or {}).get("cell_label")
    base_draws = int(((ladder.get("frozen_spec") or {}).get("draw_grid") or [BASE_DRAWS])[0])

    readings, grid = ladder_readings(ladder, base_draws)
    steps = step_readings(ladder, grid, base_draws)
    span = span_block(readings)

    sup = supply.get("summary") or {}
    widen_ref = {"face": SRC_SUPPLY, "label": "widen_cap_optimistic",
                 "value": _num(sup.get("widen_cap_optimistic"))}
    narrow_ref = {"face": SRC_SUPPLY, "label": "narrow_cap_optimistic",
                  "value": _num(sup.get("narrow_cap_optimistic"))}
    cf = (floor.get("counterfactual_percentile_band") or {})
    narrow_face_ref = {"face": SRC_FLOOR, "label": "counterfactual_percentile_band.multiplier",
                       "value": _num(cf.get("multiplier"))}

    rows = demands(gap)
    in_window = [r for r in rows if r["cell"] == cell]
    out_of_window = [{"row_key": r["row_key"], "cell": r["cell"], "class": r["class"],
                      "flip": r["flip"], "reason": "no published draw ladder for this window"}
                     for r in rows if r["cell"] != cell]

    widen_rows = [r for r in in_window if r["class"] == "above_ceiling"]
    narrow_rows = [r for r in in_window if r["class"] == "below_floor"]
    widen_margins = [grade_margin(r, readings, span, widen_ref, "widen") for r in widen_rows]
    narrow_margins = [grade_margin(r, readings, span, narrow_face_ref, "narrow") for r in narrow_rows]
    margins = widen_margins + narrow_margins
    widen_first = min([m["margin_factor"] for m in widen_margins
                       if m.get("margin_factor") is not None], default=None)
    stepb = step_block(steps, widen_first)

    verdict = verdict_of(margins)

    # reproduction: E258 measured era_2025_now|60 independently; the ladder's widest rung is the
    # same window, same base draw count, so the two must agree to 1e-9 (a witness, not a new claim).
    rep = {"checked": False}
    wm = ((winmult.get("windows") or {}).get(cell) or {}).get("by_base") or {}
    w60 = wm.get(str(base_draws)) or {}
    widest = None
    if readings:
        widest = max(readings, key=lambda r: (r["sessions"], r["draws"]))
        same = [r for r in readings
                if r["sessions"] == widest["sessions"] and r["draws"] == grid[-1]]
        widest = same[0] if same else widest
    if widest and w60.get("multiplier") is not None and widest.get("multiplier_central"):
        diff = abs(_num(w60.get("multiplier")) - widest["multiplier_central"])
        rep = {"checked": True, "window": cell, "base_draws": base_draws,
               "winmult_face": SRC_WINMULT, "winmult_multiplier": _num(w60.get("multiplier")),
               "ladder_rung": {"family": widest["family"], "sessions": widest["sessions"],
                               "draws": widest["draws"],
                               "multiplier": widest["multiplier_central"]},
               "abs_diff": _round(diff), "agrees_at_1e9": bool(diff <= 1e-9),
               "note": ("two producers, same window and same base draw count: E258 rebuilt the "
                        "band per window, E256's ladder reads its own per-rung edges")}

    summary = {
        "ladder_cell": cell,
        "base_draws": base_draws,
        "draw_grid": grid,
        "n_rungs": len(ladder.get("rungs") or []),
        "n_readings": len(readings),
        "n_steps": len(steps),
        "ladder_span": span,
        "step": stepb,
        "n_demand_rows_censused": len(rows),
        "n_demand_rows_in_the_ladder_window": len(in_window),
        "n_demand_rows_not_graded": len(out_of_window),
        "n_gradable_widening": len(widen_margins),
        "n_gradable_narrowing": len(narrow_margins),
        "n_crossed_central": sum(1 for m in margins if m["crossed_central"]),
        "n_crossed_at_one_seed": sum(1 for m in margins if m["crossed_at_one_seed"]),
        "n_interpolations_aborted": sum(1 for m in margins if m["interpolation_aborted"]),
        "widening_reference": widen_ref,
        "narrowing_reference": narrow_face_ref,
        "supply_cap_note": ("the widening reference is E287's optimistic cap, which was written at "
                            "%s; E258 measured per-window multipliers to differ by more than 15 pct, "
                            "so the ladder is graded against the DEMAND and the cap is quoted as the "
                            "margin's denominator, not as a cap the ladder replaces"
                            % ((sup.get("widen_cap_optimistic_at") or {}).get("label"),)),
        "reproduction": rep,
        "verdict": verdict,
    }

    return {
        "study": STUDY, "title": TITLE, "evidence_cutoff": CUTOFF, "generated": None,
        "no_bill": NO_BILL,
        "source_faces": [SRC_GAPCEIL, SRC_SUPPLY, SRC_LADDER, SRC_WINMULT, SRC_TOPFLIP, SRC_FLOOR],
        "frozen_spec": {
            "M1_axis": "only an absolute band-edge multiplier is compared with a demand flip; "
                       "percentages carry the margin size and the step gain, never a cap",
            "M2_window": "a rung is graded only against a demand published in the ladder's own "
                         "window; another window's demand is published as not_graded",
            "M3_step": "one more rung is priced as the adjacent-grid step multiplier on matched "
                       "seeds; the span is edge(largest draw)/edge(base draw) on one rung",
            "M4_cross": "a margin is crossed iff a published rung reaches the demand on the "
                        "demand's own polarity (widen: cap >= flip; narrow: cap <= flip)",
            "M5_abort": "no crossing -> publish the residual factor and declare the interpolation "
                        "aborted; nothing is fitted between or beyond rungs",
            "M6_nobill": "published records only: no stream drawn, no band rebuilt, no engine run",
            "M7_seeds": "central / matched-seed min / matched-seed max are published per rung; a "
                        "crossing at one seed only is published as seed-dependent",
            "tolerance": TOL,
            "base_draws": base_draws,
            "verdict_vocab": list(VERDICT_VOCAB),
        },
        "ladder": {"cell": cell, "grid": grid, "base_draws": base_draws,
                   "n_rungs": len(ladder.get("rungs") or []),
                   "draw_budget": (ladder.get("frozen_spec") or {}).get("draw_budget"),
                   "seeds": (ladder.get("frozen_spec") or {}).get("seeds"),
                   "prefix_nesting": (ladder.get("frozen_spec") or {}).get("prefix_nesting")},
        "readings": readings,
        "steps": steps,
        "ladder_span": span,
        "step": stepb,
        "demand_census": {"in_window": in_window, "not_graded": out_of_window},
        "margins": margins,
        "summary": summary,
        "verdict": verdict,
        "verdict_reason": _reason(verdict, summary, margins),
    }


def _reason(verdict, summary, margins):
    span = summary.get("ladder_span") or {}
    step = summary.get("step") or {}
    head = ("the ladder measured in %s spans %s..%s on the central basis (base %d draws to %s) and "
            "%s across its own seeds; one adjacent step buys a median %s, so %d of %d step(s) clear "
            "the widening margin's size on their own"
            % (summary.get("ladder_cell"), _fmt(span.get("central_min")),
               _fmt(span.get("central_max")), summary.get("base_draws"),
               (span.get("at") or {}).get("draws"), _fmt(span.get("seed_max")),
               _fmt(step.get("median_gain")),
               step.get("n_gains_at_or_above_the_widening_margin") or 0, step.get("n_steps") or 0))
    graded = [m for m in margins if m]
    if not graded:
        return head + "; no demand row was published in this ladder's window, so nothing is graded"
    parts = []
    for m in graded:
        if m["crossed_central"]:
            parts.append("%s (%s) is crossed by %d rung(s) on the central basis"
                         % (m["row_key"], m["direction"], m["n_rungs_crossing_central"]))
            continue
        tail = "%s (%s, flip %s) is not crossed on the central basis: the nearest rung stops at %s, "
        tail += "a residual factor of %s"
        parts.append(tail % (m["row_key"], m["direction"], _fmt(m["flip"]),
                             _fmt((m.get("closest_rung") or {}).get("multiplier_central")),
                             _fmt(m.get("residual_factor"))))
        if m["crossed_at_one_seed"]:
            parts.append("it is crossed only by %d rung(s) at their own widest seed, so the crossing "
                         "is seed-dependent and not a published result"
                         % m["n_rungs_crossing_at_one_seed"])
    if verdict == "one_margin_is_crossed_by_a_single_seed_rung_only":
        tail2 = ("; the margins are inside one step's mileage, so what is missing is not a finer "
                 "grid but a rung the family has not measured -- the interpolation is aborted "
                 "rather than fitted")
    elif verdict == "no_published_ladder_rung_crosses_a_margin":
        tail2 = "; nothing published crosses either margin, and no value is interpolated"
    else:
        tail2 = ""
    return head + "; " + "; ".join(parts) + tail2


# ------------------------------------------------------------------ commands
def write_face(face, outdir=None):
    outdir = outdir or OUTDIR
    text = json.dumps(face, ensure_ascii=False, indent=1) + "\n"
    for name in (FACE, LATEST):
        fh = io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n")
        try:
            fh.write(text)
        finally:
            fh.close()


def cmd_run():
    import datetime
    face = build()
    face["generated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    write_face(face)
    s = face["summary"]
    print("E295 %s" % face["verdict"])
    sp, st = s["ladder_span"], s["step"]
    print("  ladder %s: %d rung(s), %d reading(s), span %s..%s central / %s seed-max"
          % (s["ladder_cell"], s["n_rungs"], s["n_readings"], _fmt(sp.get("central_min")),
             _fmt(sp.get("central_max")), _fmt(sp.get("seed_max"))))
    print("  step: %d step(s), median gain %s, %d clear the widening margin"
          % (st.get("n_steps") or 0, _fmt(st.get("median_gain")),
             st.get("n_gains_at_or_above_the_widening_margin") or 0))
    print("  demands: %d censused, %d in the ladder's window, %d graded (%d widen / %d narrow)"
          % (s["n_demand_rows_censused"], s["n_demand_rows_in_the_ladder_window"],
             s["n_gradable_widening"] + s["n_gradable_narrowing"], s["n_gradable_widening"],
             s["n_gradable_narrowing"]))
    for m in face["margins"]:
        print("  %-26s %-6s flip=%s margin=%s pct | crossed central=%s at one seed=%s | residual %s"
              % (m["row_key"], m["direction"], _fmt(m["flip"]), _fmt(m["margin_pct"], 4),
                 m["crossed_central"], m["crossed_at_one_seed"], _fmt(m["residual_factor"])))
    rp = s.get("reproduction") or {}
    if rp.get("checked"):
        print("  reproduction: E258 %s vs ladder %s, |diff| %s"
              % (_fmt(rp.get("winmult_multiplier")), _fmt((rp.get("ladder_rung") or {}).get(
                  "multiplier")), rp.get("abs_diff")))
    return 0


def cmd_verify():
    stored = load(FACE)
    live = build()
    problems = []
    if stored.get("verdict") != live.get("verdict"):
        problems.append("verdict: stored=%r live=%r" % (stored.get("verdict"), live.get("verdict")))
    if stored.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the frozen set")
    ss, ls = stored.get("summary") or {}, live.get("summary") or {}
    for key in ("ladder_cell", "base_draws", "n_rungs", "n_readings", "n_steps",
                "n_demand_rows_in_the_ladder_window", "n_demand_rows_not_graded",
                "n_crossed_central", "n_crossed_at_one_seed", "n_interpolations_aborted"):
        if ss.get(key) != ls.get(key):
            problems.append("summary.%s does not re-derive" % key)
    if stored.get("margins") != live.get("margins"):
        problems.append("the margin rows do not re-derive")
    if stored.get("ladder_span") != live.get("ladder_span"):
        problems.append("the ladder span does not re-derive")
    if stored.get("step") != live.get("step"):
        problems.append("the step block does not re-derive")
    rep = live["summary"].get("reproduction") or {}
    if not rep.get("checked"):
        problems.append("the same-window reproduction witness was not checked")
    elif not rep.get("agrees_at_1e9"):
        problems.append("the ladder and E258 disagree in the same window: |diff| %s"
                        % rep.get("abs_diff"))
    if live["summary"]["n_demand_rows_in_the_ladder_window"] + \
            live["summary"]["n_demand_rows_not_graded"] != \
            live["summary"]["n_demand_rows_censused"]:
        problems.append("the demand census does not add up")
    print("E295 verify: %d problem(s)" % len(problems))
    for p in problems:
        print("  - %s" % p)
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
def _rung(edges, seeds=None):
    """A synthetic rung: {draws: edge} with optional per-seed edges keyed the same way."""
    by = {}
    for draws, edge in edges.items():
        cell = {"draws": draws, "edge_self": edge}
        if seeds is not None:
            cell["edge_self_per_seed"] = seeds[draws]
        by[str(draws)] = cell
    return {"family": "head", "sessions": 100, "by_draws": by}


def cmd_selftest():
    ok, fail = 0, []

    def leg(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append("%s %s" % (name, detail))

    r = _rung({60: 1.0, 120: 1.5, 240: 1.8},
              seeds={60: [1.0, 1.0, 1.0], 120: [1.2, 1.5, 1.8], 240: [1.5, 1.8, 2.4]})
    # L1 the multiplier a rung buys is top edge over base edge, on the rung's own numbers
    got = price_rung(r, 240, 60)
    leg("L1", abs(got["multiplier_central"] - 1.8) < 1e-12, got)
    # L2 matched seeds are paired index by index -- never max(top)/min(base)
    leg("L2", abs(got["multiplier_seed_max"] - 2.4) < 1e-12
        and abs(got["multiplier_seed_min"] - 1.5) < 1e-12 and got["n_seeds"] == 3, got)
    # L3 a mismatched seed vector is refused rather than spliced
    r_bad = _rung({60: 1.0, 120: 1.2}, seeds={60: [1.0, 1.0], 120: [1.2]})
    leg("L3", price_rung(r_bad, 120, 60)["multiplier_seed_max"] is None)
    # L4 a demand published in another window is not graded (M2)
    d_rows = [{"row_key": "a", "cell": "era_2025_now", "class": "above_ceiling", "flip": 2.4},
              {"row_key": "b", "cell": "all_five", "class": "above_ceiling", "flip": 2.4}]
    in_w = [x for x in d_rows if x["cell"] == "era_2025_now"]
    leg("L4", len(in_w) == 1 and in_w[0]["row_key"] == "a")
    # L5 the widening reach rule is >= the flip, the narrowing one <= the flip
    rec = {"multiplier_central": 2.4, "multiplier_seed_min": 2.4, "multiplier_seed_max": 2.4}
    leg("L5", crossing(rec, 2.4, "widen")["central"] is True
        and crossing(rec, 2.4, "narrow")["central"] is True
        and crossing(rec, 1.0, "narrow")["central"] is False
        and crossing(rec, 3.0, "widen")["central"] is False)
    # L6 an unmeasured basis is unknown, never "reached"
    leg("L6", crossing({"multiplier_central": None, "multiplier_seed_max": None,
                        "multiplier_seed_min": None}, 2.0, "widen")["central"] is None)
    # L7 a single-seed crossing is reported as such and not as a central crossing
    readings = [{"family": "head", "sessions": 100, "draws": 240, "multiplier_central": 1.5,
                 "multiplier_seed_min": 1.0, "multiplier_seed_max": 2.5}]
    g = grade_margin({"row_key": "x", "cell": "c", "class": "above_ceiling", "flip": 2.0},
                     readings, {}, {"value": 1.5, "face": "f", "label": "l"}, "widen")
    leg("L7", g["crossed_central"] is False and g["crossed_at_one_seed"] is True
        and g["n_rungs_crossing_at_one_seed"] == 1, g)
    # L8 the residual factor is demand over the closest rung (how far the ladder still is)
    leg("L8", abs(g["residual_factor"] - (2.0 / 1.5)) < 1e-12, g["residual_factor"])
    # L9 the interpolation is aborted exactly when nothing crosses on the central basis
    leg("L9", g["interpolation_aborted"] is True and g["abort_statement"] is not None)
    # L10 ... and not when it does cross
    readings_ok = [{"family": "head", "sessions": 100, "draws": 240, "multiplier_central": 2.5,
                    "multiplier_seed_min": 2.4, "multiplier_seed_max": 2.6}]
    g2 = grade_margin({"row_key": "y", "cell": "c", "class": "above_ceiling", "flip": 2.0},
                      readings_ok, {}, {"value": 1.9, "face": "f", "label": "l"}, "widen")
    leg("L10", g2["crossed_central"] is True and g2["interpolation_aborted"] is False)
    # L11 the verdict ladder: both central / one seed-only / none
    leg("L11", verdict_of([{"crossed_central": True, "crossed_at_one_seed": True}]) ==
        VERDICT_VOCAB[0]
        and verdict_of([{"crossed_central": False, "crossed_at_one_seed": True}])
        == VERDICT_VOCAB[1]
        and verdict_of([{"crossed_central": False, "crossed_at_one_seed": False}])
        == VERDICT_VOCAB[2] and verdict_of([]) == VERDICT_VOCAB[2])
    # L12 step gains are adjacent-grid ratios, and the share is a share of STEPS not of readings
    r2 = _rung({60: 1.0, 120: 1.1, 240: 1.5})
    st = step_readings({"rungs": [r2]}, [60, 120, 240], 60)
    blk = step_block(st, 1.2)
    leg("L12", len(st) == 2 and abs(blk["median_gain"] - statistics.median([1.1, 1.5 / 1.1])) < 1e-9
        and blk["n_gains_at_or_above_the_widening_margin"] == 1, blk)
    # L13 a ladder that only widens reports no step below one (the narrowing side is structural)
    leg("L13", blk["n_below_one"] == 0)

    live = build()
    s = live["summary"]
    idn = live["demand_census"]
    # L14 on the real face: the demand census partitions and only the ladder's window is graded
    leg("L14", s["n_demand_rows_in_the_ladder_window"] + s["n_demand_rows_not_graded"]
        == s["n_demand_rows_censused"]
        and all(m["cell"] == s["ladder_cell"] for m in live["margins"])
        and s["n_demand_rows_not_graded"] > 0, s["n_demand_rows_not_graded"])
    # L15 on the real face: both polarities are graded, so the face answers both margins
    leg("L15", s["n_gradable_widening"] >= 1 and s["n_gradable_narrowing"] >= 1,
        (s["n_gradable_widening"], s["n_gradable_narrowing"]))
    # L16 on the real face: the ladder's own span is above every step gain's start and finite
    leg("L16", s["ladder_span"]["central_max"] is not None
        and s["ladder_span"]["central_min"] is not None
        and s["ladder_span"]["central_max"] > s["ladder_span"]["central_min"], s["ladder_span"])
    # L17 on the real face: the same-window reproduction witness agrees to 1e-9
    rp = s.get("reproduction") or {}
    leg("L17", rp.get("checked") is True and rp.get("agrees_at_1e9") is True, rp.get("abs_diff"))
    # L18 on the real face: every graded margin names its reference face and label
    leg("L18", all((m["reference"] or {}).get("face") and (m["reference"] or {}).get("label")
                   for m in live["margins"]), live["margins"][:1])
    # L19 on the real face: every aborted interpolation carries a residual factor, never a blank
    leg("L19", all(m["residual_factor"] is not None for m in live["margins"]
                   if m["interpolation_aborted"]))
    # L20 on the real face: the verdict agrees with the margins it summarises
    leg("L20", live["verdict"] == verdict_of(live["margins"]), live["verdict"])
    # L21 on the real face: the reason sentence names a margin, its polarity and the ladder
    reason = live["verdict_reason"]
    leg("L21", "ladder" in reason and ("widen" in reason or "narrow" in reason)
        and "rung" in reason, reason[:80])
    # L22 on the real face: the demand rows that are not graded are published with a reason
    leg("L22", all(x.get("reason") for x in idn["not_graded"]), len(idn["not_graded"]))

    print("E295 selftest: %d/%d" % (ok, ok + len(fail)))
    for f in fail:
        print("  FAIL %s" % f)
    return 0 if not fail else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))