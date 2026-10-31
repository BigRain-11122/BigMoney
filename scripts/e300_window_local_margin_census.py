"""E300 -- the same demand, priced against the window that owns it.

E295 could grade only 2 of the twelve published demand rows because only one window
(era_2025_now) owns a published draw ladder, and it quoted the widening margin as 5.98 pct
there against E287's 3.80 pct headline. Both numbers are honest but neither is a property of
the band: they are properties of WHICH window's reference was used as the denominator.

This study re-prices every published demand row against a reference published in the SAME
window. The family already publishes that reference: E258 (BANDWINMULT) rebuilt the shuffled
band inside each measured cell and published its own draw multiplier at the row's own base
draw count. So the nine rows E295 had to call not_graded were not un-referenceable -- they
were un-LADDERED. Those are different statements, and only the second one is true.

Mechanism (frozen):
  M1 OWN-WINDOW  a demand row is graded against a reference published in its own cell; a
                 reference published in another cell is never used as the denominator.
  M2 OWN-BASE    the reference is read at the row's own published base draw count (60 or 200),
                 not at a draw count chosen here.
  M3 THREE-BASIS central (face's own ratio of central edges) / matched-seed min / matched-seed
                 max are published; a reach that exists at one seed only is seed-dependent.
  M4 POLARITY    widen: reached iff cap >= flip, margin_pct = (flip/cap - 1)*100;
                 narrow: reached iff cap <= flip, margin_pct = (cap - flip)/cap*100 -- the same
                 arithmetic E295 froze, so the two faces' numbers are directly comparable.
  M5 NOTHING FITTED  no window-local reference -> the row is published with needs_face naming
                 the exact face shape required. No cross-window subtraction is ever quoted as a
                 margin.
  M6 NOBILL      published faces only: no draw stream drawn, no band rebuilt, no engine run.
  M7 LADDER vs MULTIPLIER  a LADDER is a per-rung draw grid published inside one window (only
                 era_2025_now has one); a MULTIPLIER is a single published reference at the
                 row's own base draws (all four measured windows have one). The census reports
                 both counts so "no ladder" is never read as "no reference".

Verdict vocabulary (frozen):
  every_widening_demand_is_graded_against_its_own_window_and_no_narrowing_one_is
  every_demand_is_graded_against_its_own_window
  window_local_references_are_missing_for_some_demands

Usage:  python scripts/e300_window_local_margin_census.py run|verify|selftest
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e272_flip_budget_two_tails as e272  # noqa: E402  (ROOT / OUTDIR)
import e287_supply_ceiling_axes as e287     # noqa: E402  (load + the published caps)

ROOT = e272.ROOT
OUTDIR = e272.OUTDIR

STUDY = "E300_window_local_margin_census"
TITLE = ("the same demand, priced against the window that owns it -- what does each of the twelve "
         "published demand rows cost when the denominator is its own window's published multiplier "
         "instead of a cap written at another window, and which rows were 'unreachable' only "
         "because the reference came from a different cell?")
CUTOFF = "2026-10-29"
SRC_GAPCEIL = e287.SRC_GAPCEIL     # E285: the twelve demand rows, each with its own cell
SRC_WINMULT = e287.SRC_WINMULT     # E258: per-window, per-base draw multiplier
SRC_SUPPLY = "BANDSUPPLY-%s.json" % CUTOFF   # E287: the cross-window caps E295 used
SRC_FLOOR = e287.SRC_FLOOR         # BANDFLOOR: the synthetic narrowing counterfactual
SRC_CLOSURE = "BANDCLOSURE-%s.json" % CUTOFF  # E295: the 3 rows it could grade (witness)
SRC_DRAW = "BANDDRAW-%s-d1920.json" % CUTOFF  # E256: the one window that owns a ladder
FACE = "BANDMARGINWINDOW-%s.json" % CUTOFF
LATEST = "bandmarginwindow_latest.json"
SELF_FACES = (FACE, LATEST)

TOL = 1e-12

VERDICT_VOCAB = (
    "every_widening_demand_is_graded_against_its_own_window_and_no_narrowing_one_is",
    "every_demand_is_graded_against_its_own_window",
    "window_local_references_are_missing_for_some_demands",
)

NO_BILL = ("measurement only: the twelve published demand rows are compared with the multiplier "
           "each window already published for itself. No draw stream is drawn, no band rebuilt, no "
           "engine runs, no new draw budget is requested. A margin here is a statement about the "
           "references the family has already measured.")

NARROW_NEED = ("a per-window narrowing ladder: the same shape as BANDDRAW (rungs x draw counts, "
               "per seed) rebuilt on the narrowing polarity -- %s at the row's own base draws. "
               "BANDFLOOR is a synthetic counterfactual (fixed seed 20261031), not a per-window "
               "instrument, so it cannot stand in as this window's denominator")


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


# ------------------------------------------------------------------ rows
def demands(gap_face):
    """Every published demand row with the window and the base draw count it was published at."""
    out = []
    for arm in (gap_face.get("arms") or []):
        for rec in (arm.get("rows") or []):
            flip = _num(rec.get("flip"))
            if flip is None:
                continue
            key = str(rec.get("row_key") or "")
            parts = key.split("|")
            base = None
            if len(parts) >= 2:
                try:
                    base = int(parts[1])
                except (TypeError, ValueError):
                    base = None
            out.append({"row_key": key, "cell": rec.get("cell"), "class": rec.get("class"),
                        "flip": flip, "arm": arm.get("arm"), "base_draws": base})
    return out


def direction_of(cls):
    """M4: below_floor is the narrowing polarity; every other published class widens."""
    return "narrow" if cls == "below_floor" else "widen"


def window_reference(winmult, cell, base_draws):
    """M1/M2/M3: the multiplier this window published for itself, at the row's own base draws."""
    win = ((winmult.get("windows") or {}).get(cell) or {})
    by_base = win.get("by_base") or {}
    cellref = by_base.get(str(int(base_draws))) if base_draws is not None else None
    if not cellref:
        return None
    central = _num(cellref.get("multiplier"))
    if central is None:
        return None
    return {"face": SRC_WINMULT, "label": "%s|%d" % (cell, int(base_draws)),
            "basis": "central", "value": central,
            "seed_min": _num(cellref.get("multiplier_min")),
            "seed_max": _num(cellref.get("multiplier_max")),
            "base_draws": int(base_draws), "top_draws": cellref.get("top_draws"),
            "sessions": win.get("sessions"), "star": win.get("star")}


def margin(flip, cap, direction):
    """M4: E295's arithmetic, so both faces' percentages are comparable."""
    if cap is None or flip is None:
        return None, None
    factor = flip / cap
    if direction == "widen":
        return _round(factor), _round((factor - 1.0) * 100.0, 6)
    return _round(factor), _round((cap - flip) / cap * 100.0, 6)


def reached(flip, cap, direction):
    """M4: the published reach rule on the demand's own polarity."""
    if cap is None or flip is None:
        return None
    return bool(cap >= flip - TOL) if direction == "widen" else bool(cap <= flip + TOL)


def narrow_references(floor_face):
    """Every published reference that could serve a narrowing demand, with the window it owns."""
    out = []
    for rec in (floor_face.get("narrowing_readings") or []):
        cap = _num(rec.get("cap"))
        if cap is None:
            continue
        label = str(rec.get("label") or "")
        out.append({"face": rec.get("face"), "label": label, "basis": rec.get("basis"),
                    "cap": cap, "usable_as_supply": rec.get("usable_as_supply") is True,
                    "cell": label.split("|")[0] if "|" in label else None,
                    "narrows": bool(cap < 1.0 - TOL)})
    return out


# ------------------------------------------------------------------ build
def build(outdir=None):
    outdir = outdir or OUTDIR
    gap = load(SRC_GAPCEIL, outdir)
    winmult = load(SRC_WINMULT, outdir)
    supply = load(SRC_SUPPLY, outdir)
    floor = load(SRC_FLOOR, outdir)
    closure = load(SRC_CLOSURE, outdir)
    draw = load(SRC_DRAW, outdir)

    sup = supply.get("summary") or {}
    widen_cross = {"face": SRC_SUPPLY, "label": "widen_cap_optimistic",
                   "value": _num(sup.get("widen_cap_optimistic"))}
    cf = (floor.get("counterfactual_percentile_band") or {})
    narrow_cross = {"face": SRC_FLOOR, "label": "counterfactual_percentile_band.multiplier",
                    "value": _num(cf.get("multiplier"))}

    ladder_cells = [((draw.get("frozen_spec") or {}).get("cell_label")
                     or (closure.get("summary") or {}).get("ladder_cell"))]
    ladder_cells = [c for c in ladder_cells if c]
    multiplier_cells = sorted((winmult.get("windows") or {}).keys())

    nars = narrow_references(floor)
    narrow_local = {}
    for rec in nars:
        if rec["narrows"] and rec["cell"]:
            narrow_local.setdefault(rec["cell"], rec)

    rows = demands(gap)
    out_rows = []
    for r in rows:
        direction = direction_of(r["class"])
        ref = window_reference(winmult, r["cell"], r["base_draws"]) if direction == "widen" else \
            narrow_local.get(r["cell"])
        rec = {"row_key": r["row_key"], "cell": r["cell"], "class_published": r["class"],
               "flip": r["flip"], "arm": r["arm"], "base_draws": r["base_draws"],
               "direction": direction, "has_window_ladder": r["cell"] in ladder_cells}

        if ref is None:
            rec.update({
                "own_reference": None,
                "own_margin_pct": None, "own_margin_factor": None,
                "own_reached_central": None, "own_reached_seed_min": None,
                "own_reached_seed_max": None,
                "cross_window_reference": (narrow_cross if direction == "narrow" else widen_cross),
                "cross_margin_pct": margin(r["flip"], (narrow_cross if direction == "narrow"
                                                       else widen_cross)["value"], direction)[1],
                "cross_margin_factor": margin(r["flip"], (narrow_cross if direction == "narrow"
                                                          else widen_cross)["value"], direction)[0],
                "cross_reached_central": reached(r["flip"], (narrow_cross if direction == "narrow"
                                                             else widen_cross)["value"], direction),
                "graded_on_own_window": False,
                "needs_face": (NARROW_NEED % r["cell"]) if direction == "narrow" else
                              ("a per-window multiplier at base %s draws for cell %s -- BANDWINMULT "
                               "measured %d window(s) and this is not one of them"
                               % (r["base_draws"], r["cell"], len(multiplier_cells))),
                "margin_delta_pct": None, "reach_flips": None,
            })
            out_rows.append(rec)
            continue

        cap = _num(ref.get("value") if direction == "widen" else ref.get("cap"))
        f_own, m_own = margin(r["flip"], cap, direction)
        f_x, m_x = margin(r["flip"], (narrow_cross if direction == "narrow" else widen_cross)["value"],
                          direction)
        rec.update({
            "own_reference": ref,
            "own_margin_factor": f_own, "own_margin_pct": m_own,
            "own_reached_central": reached(r["flip"], cap, direction),
            "own_reached_seed_min": reached(r["flip"], ref.get("seed_min"), direction)
            if direction == "widen" else None,
            "own_reached_seed_max": reached(r["flip"], ref.get("seed_max"), direction)
            if direction == "widen" else None,
            "cross_window_reference": (narrow_cross if direction == "narrow" else widen_cross),
            "cross_margin_factor": f_x, "cross_margin_pct": m_x,
            "cross_reached_central": reached(
                r["flip"], (narrow_cross if direction == "narrow" else widen_cross)["value"],
                direction),
            "graded_on_own_window": True,
            "needs_face": None,
            "margin_delta_pct": None if (m_own is None or m_x is None) else _round(m_own - m_x, 6),
            "reach_flips": (None if (rec_own := reached(r["flip"], cap, direction)) is None
                            else bool(rec_own != reached(
                                r["flip"],
                                (narrow_cross if direction == "narrow" else widen_cross)["value"],
                                direction))),
        })
        out_rows.append(rec)

    # witness: the three rows E295 could grade must re-derive to its published percentages when
    # the same cross-window denominators are used -- this is what makes the own-window column a
    # pair of comparable numbers rather than a different arithmetic
    wit = {"basis": "cross_window (the denominators E295 used)", "checked": 0, "agree": 0,
           "rows": []}
    e295 = {m.get("row_key"): m for m in (closure.get("margins") or [])}
    for rec in out_rows:
        pub = e295.get(rec["row_key"])
        if not pub or rec["cross_margin_pct"] is None:
            continue
        wit["checked"] += 1
        diff = abs(_num(pub.get("margin_pct")) - rec["cross_margin_pct"])
        ok = diff <= 1e-6
        wit["agree"] += 1 if ok else 0
        wit["rows"].append({"row_key": rec["row_key"],
                            "e295_margin_pct": _num(pub.get("margin_pct")),
                            "cross_window_margin_pct": rec["cross_margin_pct"],
                            "own_window_margin_pct": rec["own_margin_pct"],
                            "abs_diff": _round(diff), "agrees": ok})
    wit["all_agree"] = bool(wit["checked"] and wit["agree"] == wit["checked"])

    # the headline pair behind E287's 3.80 pct: which rows produced it
    headline = []
    for rec in out_rows:
        if rec["direction"] != "widen":
            continue
        headline.append({"row_key": rec["row_key"], "cell": rec["cell"],
                         "cross_margin_pct": rec["cross_margin_pct"],
                         "own_margin_pct": rec["own_margin_pct"],
                         "delta_pct": rec["margin_delta_pct"]})
    headline.sort(key=lambda x: (x["cross_margin_pct"] is None, x["cross_margin_pct"]))

    own_margins = [r["own_margin_pct"] for r in out_rows if r["own_margin_pct"] is not None]
    cross_margins = [r["cross_margin_pct"] for r in out_rows if r["cross_margin_pct"] is not None]
    reach_flips = [r["row_key"] for r in out_rows if r["reach_flips"] is True]
    understated = [r["row_key"] for r in out_rows
                   if r["margin_delta_pct"] is not None and r["margin_delta_pct"] > 0]

    n_widen = sum(1 for r in out_rows if r["direction"] == "widen")
    n_narrow = len(out_rows) - n_widen
    n_graded = sum(1 for r in out_rows if r["graded_on_own_window"])
    n_graded_widen = sum(1 for r in out_rows if r["graded_on_own_window"] and r["direction"] == "widen")
    n_graded_narrow = n_graded - n_graded_widen

    if not out_rows:
        verdict = "window_local_references_are_missing_for_some_demands"
    elif n_graded_narrow == n_narrow and n_graded == len(out_rows):
        verdict = "every_demand_is_graded_against_its_own_window"
    elif n_graded_narrow == 0 and n_graded_widen == n_widen:
        verdict = "every_widening_demand_is_graded_against_its_own_window_and_no_narrowing_one_is"
    else:
        verdict = "window_local_references_are_missing_for_some_demands"

    summary = {
        "n_rows_censused": len(out_rows),
        "n_widening": n_widen,
        "n_narrowing": n_narrow,
        "n_graded_on_own_window": n_graded,
        "n_graded_widening": n_graded_widen,
        "n_graded_narrowing": n_graded_narrow,
        "n_not_graded": len(out_rows) - n_graded,
        "n_not_graded_widening": n_widen - n_graded_widen,
        "n_not_graded_narrowing": n_narrow - n_graded_narrow,
        "n_ladder_windows": len(ladder_cells),
        "ladder_windows": ladder_cells,
        "n_multiplier_windows": len(multiplier_cells),
        "multiplier_windows": multiplier_cells,
        "n_rows_un_laddered_but_multiplier_graded": sum(
            1 for r in out_rows if not r["has_window_ladder"] and r["graded_on_own_window"]),
        "n_reached_own_central": sum(1 for r in out_rows if r["own_reached_central"] is True),
        "n_reached_cross_central": sum(1 for r in out_rows if r["cross_reached_central"] is True),
        "n_reach_flips": len(reach_flips),
        "reach_flip_rows": reach_flips,
        "n_cross_window_understated": len(understated),
        "cross_window_understated_rows": understated,
        "own_margin_pct_min": _round(min(own_margins), 6) if own_margins else None,
        "own_margin_pct_max": _round(max(own_margins), 6) if own_margins else None,
        "cross_margin_pct_min": _round(min(cross_margins), 6) if cross_margins else None,
        "cross_margin_pct_max": _round(max(cross_margins), 6) if cross_margins else None,
        "cross_window_caps": {"widen": widen_cross, "narrow": narrow_cross},
        "headline_rows_by_cross_margin": headline[:3],
        "narrow_tool_audit": [{"face": r["face"], "label": r["label"], "cap": r["cap"],
                               "cell": r["cell"], "narrows": r["narrows"]} for r in nars],
        "n_narrowing_instruments_published": sum(1 for r in nars if r["narrows"]),
        "witness_e295": wit,
        "verdict": verdict,
    }

    return {
        "study": STUDY, "title": TITLE, "evidence_cutoff": CUTOFF, "generated": None,
        "no_bill": NO_BILL,
        "source_faces": [SRC_GAPCEIL, SRC_WINMULT, SRC_SUPPLY, SRC_FLOOR, SRC_CLOSURE, SRC_DRAW],
        "frozen_spec": {
            "M1_own_window": "a demand row is graded against a reference published in its own "
                             "cell; another cell's reference is never the denominator",
            "M2_own_base": "the reference is read at the row's own published base draw count "
                           "(60 for the era cells, 200 for all_five)",
            "M3_three_basis": "central / matched-seed min / matched-seed max are published; a "
                              "reach at one seed only is seed-dependent",
            "M4_polarity": "widen: reached iff cap >= flip, margin_pct = (flip/cap-1)*100; narrow: "
                           "reached iff cap <= flip, margin_pct = (cap-flip)/cap*100 (E295's "
                           "arithmetic, so the faces are comparable)",
            "M5_nothing_fitted": "no window-local reference -> the row is published with "
                                 "needs_face; no cross-window subtraction is quoted as a margin",
            "M6_nobill": "published faces only: no stream drawn, no band rebuilt, no engine run",
            "M7_ladder_vs_multiplier": "a ladder is a per-rung draw grid inside one window; a "
                                       "multiplier is one published reference at the row's own "
                                       "base draws. Both counts are reported",
            "tolerance": TOL,
            "verdict_vocab": list(VERDICT_VOCAB),
        },
        "rows": out_rows,
        "headline_rows_by_cross_margin": headline,
        "summary": summary,
        "verdict": verdict,
        "verdict_reason": _reason(verdict, summary, out_rows),
    }


def _reason(verdict, summary, rows):
    n = summary["n_rows_censused"]
    head = ("all %d published demand row(s) were priced twice: against the cap E287 wrote at %s "
            "(the denominator E295 had to reuse) and against the multiplier their own window "
            "published for itself"
            % (n, (summary.get("cross_window_caps") or {}).get("widen", {}).get("label")))
    if summary["n_graded_on_own_window"]:
        head += ("; %d row(s) are graded on their own window (%d widening / %d narrowing) and %d "
                 "still have no window-local reference"
                 % (summary["n_graded_on_own_window"], summary["n_graded_widening"],
                    summary["n_graded_narrowing"], summary["n_not_graded"]))
    parts = []
    if summary["n_rows_un_laddered_but_multiplier_graded"]:
        parts.append("%d of the rows E295 called not_graded own no draw LADDER but do own a "
                     "published MULTIPLIER, so 'unreachable' was never the right word for them"
                     % summary["n_rows_un_laddered_but_multiplier_graded"])
    if summary["reach_flip_rows"]:
        parts.append("%d row(s) change their reach verdict when the denominator moves to their own "
                     "window: %s" % (len(summary["reach_flip_rows"]),
                                     ", ".join(summary["reach_flip_rows"])))
    if summary["n_cross_window_understated"]:
        parts.append("on %d row(s) the cross-window denominator UNDERSTATES the margin by up to %s "
                     "pct" % (summary["n_cross_window_understated"],
                              _fmt(max([r["margin_delta_pct"] for r in rows
                                        if r["margin_delta_pct"] is not None], default=None), 2)))
    if summary["n_not_graded_narrowing"]:
        parts.append("%d narrowing row(s) stay not_graded because the family publishes no window-"
                     "local narrowing instrument at all (the only sub-1.0 multiplier, BANDFLOOR, is "
                     "a synthetic counterfactual with one frozen seed)" % summary["n_not_graded_narrowing"])
    return head + ("; " + "; ".join(parts) if parts else "")


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
    print("E300 %s" % face["verdict"])
    print("  rows: %d censused (%d widen / %d narrow); graded on own window %d (%d widen / %d narrow)"
          % (s["n_rows_censused"], s["n_widening"], s["n_narrowing"],
             s["n_graded_on_own_window"], s["n_graded_widening"], s["n_graded_narrowing"]))
    print("  ladders: %d window(s) %s ; multipliers: %d window(s) %s"
          % (s["n_ladder_windows"], s["ladder_windows"], s["n_multiplier_windows"],
             s["multiplier_windows"]))
    print("  reach: own-window %d vs cross-window %d ; flips %d"
          % (s["n_reached_own_central"], s["n_reached_cross_central"], s["n_reach_flips"]))
    if s["own_margin_pct_min"] is not None:
        print("  own-window margin pct: min %s max %s | cross-window: min %s max %s"
              % (_fmt(s["own_margin_pct_min"], 2), _fmt(s["own_margin_pct_max"], 2),
                 _fmt(s["cross_margin_pct_min"], 2), _fmt(s["cross_margin_pct_max"], 2)))
    for r in face["rows"]:
        print("  %-24s %-14s %-12s flip=%s own=%s pct cross=%s pct%s"
              % (r["row_key"], r["cell"], r["class_published"], _fmt(r["flip"], 4),
                 _fmt(r["own_margin_pct"], 2), _fmt(r["cross_margin_pct"], 2),
                 "" if r["graded_on_own_window"] else "  [needs face]"))
    w = s["witness_e295"]
    print("  witness: E295 re-derives on %d row(s), agree %d" % (w["checked"], w["agree"]))
    return 0


def cmd_verify():
    stored = load(FACE)
    live = build()
    problems = []
    if stored.get("verdict") != live.get("verdict"):
        problems.append("verdict: stored=%r live=%r" % (stored.get("verdict"), live.get("verdict")))
    if stored.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the frozen set")
    if stored.get("rows") != live.get("rows"):
        problems.append("the row table does not re-derive")
    if stored.get("summary") != live.get("summary"):
        problems.append("the summary does not re-derive")
    s = live["summary"]
    if s["n_graded_on_own_window"] + s["n_not_graded"] != s["n_rows_censused"]:
        problems.append("the census does not partition")
    if s["n_reach_flips"] != len(s["reach_flip_rows"]):
        problems.append("the reach-flip count disagrees with its row list")
    if not s["witness_e295"]["all_agree"]:
        problems.append("the E295 witness rows do not re-derive at 1e-6")
    print("E300 verify: %d problem(s)" % len(problems))
    for p in problems:
        print("  - %s" % p)
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
def _wm(cell, bases):
    """A synthetic BANDWINMULT window: {base: (central, min, max)}."""
    return {"cell": cell, "sessions": 100, "star": "sh000000",
            "by_base": {str(b): {"multiplier": c, "multiplier_min": lo, "multiplier_max": hi,
                                 "base_draws": float(b), "top_draws": 1920}
                        for b, (c, lo, hi) in bases.items()}}


def cmd_selftest():
    ok, fail = 0, []

    def leg(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append("%s %s" % (name, detail))

    wm = {"windows": {"w1": _wm("w1", {60: (1.5, 1.1, 1.7), 200: (1.3, 1.2, 1.4)}),
                      "w2": _wm("w2", {60: (2.0, 1.9, 2.1)})}}

    # L1 the reference is read at the row's OWN base draw count, not a chosen one
    a = window_reference(wm, "w1", 60)
    b = window_reference(wm, "w1", 200)
    leg("L1", a and b and abs(a["value"] - 1.5) < 1e-12 and abs(b["value"] - 1.3) < 1e-12
        and a["label"] == "w1|60", (a or {}).get("label"))
    # L2 a window that published nothing returns None -- never another window's number
    leg("L2", window_reference(wm, "w3", 60) is None
        and window_reference(wm, "w1", 480) is None)
    # L3 a base draw count of None is not silently replaced by 60
    leg("L3", window_reference(wm, "w1", None) is None)
    # L4 widen margin arithmetic: flip/cap - 1, in percent
    f, m = margin(1.8, 1.5, "widen")
    leg("L4", abs(f - 1.2) < 1e-12 and abs(m - 20.0) < 1e-9, (f, m))
    # L5 narrow margin arithmetic: (cap-flip)/cap, in percent
    f2, m2 = margin(0.8, 0.9, "narrow")
    leg("L5", abs(f2 - (0.8 / 0.9)) < 1e-12 and abs(m2 - (0.1 / 0.9) * 100.0) < 1e-5, (f2, m2))
    # L6 the reach rule flips with polarity on the same numbers: widen needs the cap at or ABOVE
    # the demand, narrow needs it at or BELOW
    leg("L6", reached(1.5, 1.8, "widen") is True and reached(1.8, 1.5, "widen") is False
        and reached(0.8, 0.7, "narrow") is True and reached(0.8, 0.9, "narrow") is False)
    # L7 equality reaches on both polarities (>= / <=), not only strictly
    leg("L7", reached(1.5, 1.5, "widen") is True and reached(0.9, 0.9, "narrow") is True)
    # L8 an unmeasured cap is unknown, never "reached"
    leg("L8", reached(1.5, None, "widen") is None and margin(1.5, None, "widen") == (None, None))
    # L9 the base draw count is parsed off the published row key
    gap = {"arms": [{"arm": "cross:60", "rows": [{"row_key": "cross|60|9", "cell": "w1",
                                                 "class": "reachable_wide", "flip": 1.6}]},
                    {"arm": "self:200", "rows": [{"row_key": "self|200|0", "cell": "w1",
                                                 "class": "above_ceiling", "flip": 2.3}]}]}
    rows = demands(gap)
    leg("L9", [r["base_draws"] for r in rows] == [60, 200] and rows[0]["cell"] == "w1")
    # L10 the below_floor class is the narrowing direction, everything else is widening
    leg("L10", direction_of("above_ceiling") == "widen" and direction_of("reachable_wide") == "widen"
        and direction_of("below_floor") == "narrow" and direction_of("in_gap") == "widen")
    # L11 narrowing instruments are read off BANDFLOOR's readings and a >1 cap is not a narrowing one
    fl = {"narrowing_readings": [{"face": "F", "label": "w1|60", "basis": "extreme", "cap": 0.9,
                                  "usable_as_supply": True},
                                 {"face": "F", "label": "w1|200", "basis": "extreme", "cap": 1.2,
                                  "usable_as_supply": True}]}
    nars = narrow_references(fl)
    leg("L11", len(nars) == 2 and nars[0]["narrows"] is True and nars[1]["narrows"] is False
        and nars[0]["cell"] == "w1", nars)

    live = build()
    s = live["summary"]
    rows = live["rows"]
    # L12 on the real face: every published demand row appears exactly once
    leg("L12", len(rows) == s["n_rows_censused"] == 12
        and len({r["row_key"] for r in rows}) == len(rows), s["n_rows_censused"])
    # L13 on the real face: the census partitions into graded + not graded
    leg("L13", s["n_graded_on_own_window"] + s["n_not_graded"] == s["n_rows_censused"]
        and s["n_graded_widening"] + s["n_graded_narrowing"] == s["n_graded_on_own_window"])
    # L14 on the real face: every graded row names the face and label it was priced against
    leg("L14", all((r["own_reference"] or {}).get("face") and (r["own_reference"] or {}).get("label")
                   for r in rows if r["graded_on_own_window"]))
    # L15 on the real face: every ungraded row names the face it would need and carries no margin
    leg("L15", all(r.get("needs_face") and r["own_margin_pct"] is None
                   for r in rows if not r["graded_on_own_window"]))
    # L16 on the real face: the graded reference belongs to the row's own cell (M1)
    leg("L16", all((r["own_reference"] or {}).get("label", "").startswith(r["cell"] + "|")
                   for r in rows if r["graded_on_own_window"]))
    # L17 on the real face: the graded reference is at the row's own base draw count (M2)
    leg("L17", all(int((r["own_reference"] or {}).get("base_draws")) == r["base_draws"]
                   for r in rows if r["graded_on_own_window"]))
    # L18 on the real face: the rows E295 graded re-derive to its published percentages on the
    # cross-window denominators (so the own-window column is comparable arithmetic, not a rival one)
    leg("L18", s["witness_e295"]["checked"] >= 2 and s["witness_e295"]["all_agree"] is True,
        s["witness_e295"]["rows"])
    # L19 on the real face: more rows are graded here than E295 could grade
    leg("L19", s["n_graded_on_own_window"] > s["witness_e295"]["checked"],
        (s["n_graded_on_own_window"], s["witness_e295"]["checked"]))
    # L20 on the real face: only one window owns a ladder but more than one owns a multiplier
    leg("L20", s["n_ladder_windows"] == 1 and s["n_multiplier_windows"] >= 4
        and s["n_rows_un_laddered_but_multiplier_graded"] > 0,
        (s["n_ladder_windows"], s["n_multiplier_windows"]))
    # L21 on the real face: a reach flip is published only when the two denominators disagree
    leg("L21", all(r["reach_flips"] is (r["own_reached_central"] != r["cross_reached_central"])
                   for r in rows if r["graded_on_own_window"] and r["reach_flips"] is not None))
    # L22 on the real face: every reach flip row is a widening row that the cross-window cap reached
    leg("L22", all(any(r["row_key"] == k and r["cross_reached_central"] is True
                       and r["own_reached_central"] is False for r in rows)
                   for k in s["reach_flip_rows"]), s["reach_flip_rows"])
    # L23 on the real face: the verdict agrees with the graded counts
    leg("L23", (live["verdict"] == VERDICT_VOCAB[0] and s["n_graded_narrowing"] == 0
                and s["n_graded_widening"] == s["n_widening"])
        or (live["verdict"] == VERDICT_VOCAB[1] and s["n_graded_on_own_window"] == s["n_rows_censused"])
        or live["verdict"] == VERDICT_VOCAB[2], live["verdict"])
    # L24 on the real face: no published narrowing instrument narrows, which is why the narrow
    #     rows stay ungraded rather than being priced against a >1 multiplier
    leg("L24", s["n_narrowing_instruments_published"] == 0, s["n_narrowing_instruments_published"])
    # L25 on the real face: the reason names the cross-window cap it is compared against
    leg("L25", "widen_cap_optimistic" in live["verdict_reason"]
        and "own window" in live["verdict_reason"], live["verdict_reason"][:100])
    # L26 every row carries both a cross-window and (where available) an own-window number, so a
    #     reader never has to subtract two windows to get a margin
    leg("L26", all(r["cross_margin_pct"] is not None for r in rows))
    # L27 the delta is own minus cross, signed the way the reason reports it
    leg("L27", all(abs(r["margin_delta_pct"] - (r["own_margin_pct"] - r["cross_margin_pct"])) < 1e-6
                   for r in rows if r["margin_delta_pct"] is not None))

    print("E300 selftest: %d/%d" % (ok, ok + len(fail)))
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