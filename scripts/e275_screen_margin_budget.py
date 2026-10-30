"""E275 -- is a CLEARED row equally cleared, or does one perturbation spend its whole margin?

E274 turned E271's mechanism into an exact screen: a row moves only if its flip multiplier lands
inside the multiplier range its (leg, base) group actually offers.  That reading is binary.  It
says a cleared row is safe, and nothing about how much room is left.

This face puts a budget on the cleared set, from published numbers only.  For every measured row
of E274's wide axis it publishes

    m_flip          the multiplier at which the row's verdict flips     (E274, re-derived)
    offered range   [lo, hi] the row's group actually offers            (E274, group p95 spread)
    budget_spent    hi / m_flip   -- the share of the way from "no perturbation" (1.0) to the
                                     flip that the group's widest offered multiplier travels
    room_left       1 - budget_spent

and sorts each row into one of five zones, because "cleared" is not one state:

    straddles           the flip sits inside the offered range        (E274: moves)
    spent_by_build      m_flip <= lo -- even the group's TIGHTEST end is already past the flip,
                        so the row is not "nearly spent", it is spent before the budget starts
    spent               budget_spent >= 0.90 -- outside the range but within 10% of the flip
    open                budget_spent <  0.90

The question the card asks is answered by the distribution, not by a flag: if the cleared rows
cluster in one zone the screen's reading is homogeneous; if they spread, a reader who treats
"outside" as one instruction is discarding the room-left number.

The coincidence half is scored against the two other faces that already name near-threshold rows:
BANDNEAR1's near_one_dependent_rows and BANDMARGIN's guard move set.  Both are published sets, so
"the budget names different rows" is a measurement, not a preference.

No draws, no panel, no engine call.

Modes: run | verify | selftest
"""

from __future__ import print_function

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e274_spread_straddle_sweep as e274  # noqa: E402  (flip_multiplier, straddle, OUTDIR)

OUTDIR = e274.OUTDIR
CUTOFF = "2026-10-29"
SRC_SWEEP = "BANDSTRADDLESWEEP-%s.json" % CUTOFF
SRC_NEAR1 = "BANDNEAR1-%s.json" % CUTOFF
SRC_MARGIN = "BANDMARGIN-%s.json" % CUTOFF
FACE = "BANDSCREENBUDGET-%s.json" % CUTOFF
LATEST = "bandscreenbudget_latest.json"

AXIS = "wide_donor"

# A row outside the range but within this share of the flip is "spent": the next perturbation that
# is even slightly wider than anything the group published would move it.  Frozen, not tuned.
SPENT_SHARE = 0.90


# ------------------------------------------------------------------ io
def load(name):
    with io.open(os.path.join(OUTDIR, name), encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------ one row's budget
def budget_spent(m_flip, lo, hi):
    """Share of the flip threshold the group's widest offered multiplier eats.  None if untestable."""
    if m_flip is None or hi is None:
        return None
    if m_flip <= 0:
        # a flip at or below zero is reached by any positive multiplier: no budget to measure
        return None
    return hi / m_flip


def zone_of(m_flip, lo, hi, straddle_reading, spent_share=SPENT_SHARE):
    """Five-way classification.  A cleared row is never a bare 'ok'."""
    if straddle_reading == "untested":
        return "untested"
    if straddle_reading in ("inside", "near_edge"):
        return "straddles"
    if m_flip is None or lo is None or hi is None:
        return "untested"
    if m_flip <= lo:
        # the group's tightest offered multiplier already passes the flip, so the row is not
        # "nearly spent" -- it is spent before the budget is measured
        return "spent_by_build"
    spent = budget_spent(m_flip, lo, hi)
    if spent is None:
        return "untested"
    return "spent" if spent >= spent_share else "open"


def room_left(m_flip, lo, hi):
    """Signed room above the widest offered multiplier, as a share of the flip (negative = spent)."""
    if m_flip is None or hi is None or m_flip <= 0:
        return None
    return 1.0 - hi / m_flip


# ------------------------------------------------------------------ face assembly
def rows_of(sweep):
    axis = ((sweep or {}).get("axes") or {}).get(AXIS) or {}
    out = []
    for r in axis.get("rows") or []:
        lo, hi = (r.get("range") or [None, None])[:2]
        reading = r.get("straddle")
        m = r.get("flip_multiplier")
        out.append({
            "index": r.get("index"),
            "row": r.get("row"),
            "cell": r.get("cell"),
            "leg": r.get("leg"),
            "base": r.get("base"),
            "m_flip": m,
            "offered_range": [lo, hi],
            "straddle": reading,
            "budget_spent": budget_spent(m, lo, hi),
            "room_left": room_left(m, lo, hi),
            "zone": zone_of(m, lo, hi, reading),
        })
    return out


def named_sets(near1, margin):
    near = sorted((near1 or {}).get("near_one_dependent_rows") or [])
    guard = sorted({d.get("index") for d in
                    (((margin or {}).get("summary") or {}).get("moves_detail") or [])
                    if d.get("index") is not None})
    return {"near_one_dependent": near, "guard_moves": guard}


def zones(rows):
    out = {"straddles": [], "spent_by_build": [], "spent": [], "open": [], "untested": []}
    for r in rows:
        out.setdefault(r["zone"], []).append(r["index"])
    return out


def coincidence(rows, sets):
    """Which named rows land in which budget zone -- disjointness is published, not assumed."""
    by_index = {r["index"]: r for r in rows if r["index"] is not None}
    out = {}
    for name, ids in sets.items():
        rec = {"named": sorted(ids), "zones": {}, "not_in_face": []}
        for i in ids:
            r = by_index.get(i)
            if r is None:
                rec["not_in_face"].append(i)
                continue
            rec["zones"].setdefault(r["zone"], []).append(i)
        out[name] = rec
    near_spent = sorted(zones(rows)["spent"] + zones(rows)["spent_by_build"] +
                        zones(rows)["straddles"])
    out["budget_named"] = {"named": near_spent,
                           "zones": {z: ids for z, ids in zones(rows).items() if ids}}
    out["budget_names_nothing_else_does"] = sorted(
        set(near_spent) - set(sets.get("near_one_dependent") or []) -
        set(sets.get("guard_moves") or []))
    return out


def summary_of(rows, coin):
    z = zones(rows)
    spent_rows = [r for r in rows if r["zone"] in ("spent", "spent_by_build")]
    shares = [r["budget_spent"] for r in rows
              if r["zone"] == "open" and r["budget_spent"] is not None]
    moved = [r["index"] for r in rows if r["zone"] == "straddles"]
    return {
        "rows": len(rows),
        "zones": z,
        "n_straddles": len(z["straddles"]),
        "n_spent": len(z["spent"]),
        "n_spent_by_build": len(z["spent_by_build"]),
        "n_open": len(z["open"]),
        "n_untested": len(z["untested"]),
        "spent_rows": [r["index"] for r in spent_rows],
        "open_budget_min": min(shares) if shares else None,
        "open_budget_max": max(shares) if shares else None,
        "cleared_rows": [r["index"] for r in rows if r["zone"] != "straddles"
                         and r["zone"] != "untested"],
        "cleared_but_not_open": [r["index"] for r in rows
                                 if r["zone"] in ("spent", "spent_by_build")],
        "budget_names_nothing_else_does": coin.get("budget_names_nothing_else_does") or [],
        "coincides_with_near_one": bool(set(spent_rows and [r["index"] for r in spent_rows]) &
                                        set((coin.get("near_one_dependent") or {}).get("named")
                                            or [])),
        "coincides_with_guard_moves": bool(set(r["index"] for r in spent_rows) &
                                           set((coin.get("guard_moves") or {}).get("named") or [])),
        "moved_here": moved,
    }


def verdict_of(s):
    if s["rows"] == 0:
        return ("no_rows_to_budget", "the wide axis published no measured row, so nothing is scored")
    if s["n_open"] == 0 and s["n_spent"] == 0:
        return ("cleared_set_is_one_reading",
                "every measured row either straddles or sits past the group's tightest end, so the "
                "budget adds no distinction to the binary screen on this population")
    if not s["coincides_with_guard_moves"] and not s["coincides_with_near_one"]:
        return ("cleared_is_not_one_reading_the_budget_names_rows_nothing_else_flags",
                "%d of %d measured rows straddle%s -- exactly the rows the guard screen publishes "
                "as moved; of the remaining %d cleared rows %d sit past the group's tightest "
                "offered multiplier and %d are within %.0f%% of the flip, while the %d open rows "
                "have already spent %.1f%%..%.1f%% of their own threshold. No near-spent row is a "
                "row the near-one screen or the guard screen names, so 'outside the range' is one "
                "reading with room left and another with almost none%s"
                % (s["n_straddles"], s["rows"],
                   "" if s["n_straddles"] == 1 else "s",
                   len(s["cleared_rows"]), s["n_spent_by_build"], s["n_spent"],
                   SPENT_SHARE * 100.0, s["n_open"],
                   (s["open_budget_min"] or 0.0) * 100.0, (s["open_budget_max"] or 0.0) * 100.0,
                   "; the zone is a statement about the published range, not a movement "
                   "prediction -- none of the spent_by_build rows moved in the published sweep"))
    return ("the_budget_mostly_restates_a_named_row_set",
            "the near-spent rows overlap a set another face already names (%d by the guard "
            "screen, %d by the near-one screen), so the budget is a second reading of the same "
            "instruction rather than a new one"
            % (1 if s["coincides_with_guard_moves"] else 0,
               1 if s["coincides_with_near_one"] else 0))


# ------------------------------------------------------------------ run
def _stamp():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")


def run(save=True, outdir=None):
    sweep = load(SRC_SWEEP)
    near1 = load(SRC_NEAR1)
    margin = load(SRC_MARGIN)
    rows = rows_of(sweep)
    sets = named_sets(near1, margin)
    coin = coincidence(rows, sets)
    s = summary_of(rows, coin)
    verdict, why = verdict_of(s)
    s["verdict"] = verdict
    out = {
        "study": "e275_screen_margin_budget",
        "title": "is a cleared row equally cleared, or does one perturbation spend its whole margin?",
        "evidence_cutoff": CUTOFF,
        "generated": _stamp(),
        "source_faces": [SRC_SWEEP, SRC_NEAR1, SRC_MARGIN],
        "frozen_spec": {
            "design": ("for every measured row of E274's wide axis publish the flip multiplier, "
                       "the multiplier range its group offers, the share of the threshold the "
                       "widest offered multiplier eats and a five-way zone"),
            "no_new_draws": "no shuffle stream is drawn; every number is a function of published faces",
            "spent_share": ("a cleared row whose widest offered multiplier reaches >= %.2f of its "
                            "flip is 'spent'; the cut is frozen here, not tuned on the output"
                            % SPENT_SHARE),
            "spent_by_build": ("a row whose flip sits at or below the group's TIGHTEST end is not "
                               "nearly spent, it is spent before the budget starts; published "
                               "apart from 'spent' because the two mean opposite things about "
                               "the next perturbation"),
            "coincidence": ("scored against BANDNEAR1.near_one_dependent_rows and BANDMARGIN's "
                            "guard move indices; disjointness is measured, not assumed"),
            "m_flip_provenance": ("imported from e274 (which re-derives it from the published b and "
                                  "band edges) rather than retyped, so the two faces cannot drift"),
        },
        "axis": AXIS,
        "rows": rows,
        "zones": zones(rows),
        "named_sets": sets,
        "coincidence": coin,
        "summary": s,
        "verdict": verdict,
        "verdict_reason": why,
        "no_bill": "descriptive census over published faces; no trial, no ledger booking",
    }
    if save:
        _write(out, outdir)
    return out


def _write(face, outdir):
    outdir = outdir or OUTDIR
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in ("BANDSCREENBUDGET-%s.json" % face.get("evidence_cutoff"), LATEST):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")


def verify(outdir=None):
    outdir = outdir or OUTDIR
    path = os.path.join(outdir, "BANDSCREENBUDGET-%s.json" % CUTOFF)
    if not os.path.exists(path):
        return ["no published face at %s" % path]
    with io.open(path, encoding="utf-8") as fh:
        got = json.load(fh)
    fresh = run(save=False)
    problems = []
    for key in sorted(set(got) | set(fresh)):
        if key == "generated":
            continue
        if got.get(key) != fresh.get(key):
            problems.append("%s does not re-derive" % key)
    return problems


# ------------------------------------------------------------------ selftest
def _leg(ok, name, detail=None):
    return {"leg": name, "ok": bool(ok), "detail": detail}


def _row(index, m, lo, hi, reading):
    return {"index": index, "m_flip": m, "offered_range": [lo, hi], "straddle": reading,
            "budget_spent": budget_spent(m, lo, hi), "room_left": room_left(m, lo, hi),
            "zone": zone_of(m, lo, hi, reading), "row": "r%s" % index, "cell": "a"}


def selftest():
    legs = []

    # --- the budget is a ratio against the flip, both sides ------------------------------
    legs.append(_leg(abs(budget_spent(2.0, 1.0, 1.5) - 0.75) < 1e-12,
                     "spent = widest offered / flip", budget_spent(2.0, 1.0, 1.5)))
    legs.append(_leg(budget_spent(None, 1.0, 1.5) is None, "no flip -> no budget, not zero"))
    legs.append(_leg(budget_spent(0.0, 1.0, 1.5) is None,
                     "a flip at zero has no threshold to fill (guarded, not div-by-zero)"))
    legs.append(_leg(abs(room_left(2.0, 1.0, 1.5) - 0.25) < 1e-12,
                     "room left is 1 - spent", room_left(2.0, 1.0, 1.5)))
    legs.append(_leg(room_left(1.2, 1.0, 1.5) < 0,
                     "a flip below the widest end has negative room (signed, never clipped)",
                     room_left(1.2, 1.0, 1.5)))

    # --- the five zones, including the two that mean opposite things ---------------------
    legs.append(_leg(_row(0, 3.0, 1.9, 2.0, "outside")["zone"] == "open",
                     "a flip well above the range is open", _row(0, 3.0, 1.9, 2.0, "outside")))
    legs.append(_leg(_row(1, 2.05, 1.9, 2.0, "outside")["zone"] == "spent",
                     "a flip within 10% of the widest end is spent (2.0/2.05 = 0.976)",
                     _row(1, 2.05, 1.9, 2.0, "outside")))
    legs.append(_leg(_row(2, 1.95, 2.0, 2.2, "outside")["zone"] == "spent_by_build",
                     "a flip below the TIGHTEST end is spent before the budget starts",
                     _row(2, 1.95, 2.0, 2.2, "outside")))
    legs.append(_leg(_row(3, 2.1, 2.0, 2.2, "inside")["zone"] == "straddles",
                     "a flip inside the range is a straddle, not 'spent 0.95'"))
    legs.append(_leg(_row(4, None, 2.0, 2.2, "untested")["zone"] == "untested",
                     "an untested row stays untested"))
    # the two neighbouring zones must not collapse: same spent value, opposite instructions
    by_build = _row(5, 1.99, 2.0, 2.2, "outside")
    spent = _row(6, 2.32, 2.0, 2.3, "outside")
    legs.append(_leg(by_build["zone"] != spent["zone"],
                     "spent_by_build and spent are different zones", (by_build["zone"],
                                                                     spent["zone"])))

    # --- summary counts ----------------------------------------------------------------
    rows = [_row(0, 3.0, 1.9, 2.0, "outside"), _row(1, 2.05, 1.9, 2.0, "outside"),
            _row(2, 1.95, 2.0, 2.2, "outside"), _row(3, 2.1, 2.0, 2.2, "inside")]
    coin = {"near_one_dependent": {"named": []}, "guard_moves": {"named": [3]},
            "budget_names_nothing_else_does": [0, 1, 2]}
    s = summary_of(rows, coin)
    legs.append(_leg(s["n_straddles"] == 1 and s["n_spent"] == 1 and s["n_spent_by_build"] == 1
                     and s["n_open"] == 1, "the four zones count separately", s["zones"]))
    legs.append(_leg(s["cleared_rows"] == [0, 1, 2],
                     "cleared = everything but straddle/untested", s["cleared_rows"]))
    legs.append(_leg(s["coincides_with_guard_moves"] is False,
                     "no near-spent row is a guard-named row here", s["spent_rows"]))

    # --- coincidence is measured, not assumed -------------------------------------------
    c = coincidence(rows, {"near_one_dependent": [], "guard_moves": [3, 99]})
    legs.append(_leg(c["guard_moves"]["not_in_face"] == [99],
                     "a named row missing from the face is disclosed, not dropped",
                     c["guard_moves"]))
    legs.append(_leg(c["guard_moves"]["zones"] == {"straddles": [3]},
                     "a named row lands in its zone", c["guard_moves"]["zones"]))

    # --- verdict rule -------------------------------------------------------------------
    s_zero = summary_of([], {})
    legs.append(_leg(verdict_of(s_zero)[0] == "no_rows_to_budget",
                     "no rows reads as nothing to budget, not as a clean pass"))
    s_one = summary_of([_row(0, 2.1, 2.0, 2.2, "inside"), _row(1, 1.99, 2.0, 2.2, "outside")],
                       {"near_one_dependent": {"named": []}, "guard_moves": {"named": []},
                        "budget_names_nothing_else_does": [1]})
    legs.append(_leg(verdict_of(s_one)[0] == "cleared_set_is_one_reading",
                     "no open and no spent reads as one reading", s_one["zones"]))
    legs.append(_leg(verdict_of(s)["0"] if False else
                     verdict_of(s)[0] ==
                     "cleared_is_not_one_reading_the_budget_names_rows_nothing_else_flags",
                     "a spread with no named overlap names the budget reading", verdict_of(s)[0]))
    s_overlap = summary_of(rows, {"near_one_dependent": {"named": [1]},
                                  "guard_moves": {"named": []},
                                  "budget_names_nothing_else_does": [0, 2]})
    legs.append(_leg(verdict_of(s_overlap)[0] == "the_budget_mostly_restates_a_named_row_set",
                     "an overlapping set is published as a restatement", verdict_of(s_overlap)[0]))

    # --- live legs ----------------------------------------------------------------------
    faces = all(os.path.exists(os.path.join(OUTDIR, n))
                for n in (SRC_SWEEP, SRC_NEAR1, SRC_MARGIN))
    legs.append(_leg(faces, "all three source faces are on disk"))
    if faces:
        live = run(save=False)
        z = live["summary"]["zones"]
        legs.append(_leg(sorted(z["straddles"]) == sorted(live["coincidence"]["guard_moves"]
                                                          ["named"]),
                         "live: the straddle set IS the guard screen's moved set",
                         (z["straddles"], live["coincidence"]["guard_moves"]["named"])))
        legs.append(_leg(all(r["zone"] in ("straddles", "spent_by_build", "spent", "open",
                                          "untested") for r in live["rows"]),
                         "live: every row carries one of the five zones"))
        legs.append(_leg(all((r["budget_spent"] is None) == (r["m_flip"] is None or
                                                            r["m_flip"] <= 0)
                             for r in live["rows"]),
                         "live: a missing budget is always a missing flip, never a silent zero"))
        legs.append(_leg(live["summary"]["rows"] == len(live["rows"]),
                         "live: the summary counts what the row list carries"))

    ok = all(x["ok"] for x in legs)
    print("selftest %d/%d %s" % (sum(1 for x in legs if x["ok"]), len(legs),
                                 "PASS" if ok else "FAIL"))
    for x in legs:
        if not x["ok"]:
            print("  FAIL %s %s" % (x["leg"], x.get("detail")))
    return 0 if ok else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        if problems:
            print("verify %d problem(s)" % len(problems))
            for p in problems:
                print("  -", p)
            return 1
        print("verify 0 problems")
        return 0
    if cmd == "run":
        face = run()
        s = face["summary"]
        print("%s: %s" % (face["verdict"], face["verdict_reason"]))
        print("  zones: " + " ".join("%s=%d" % (k, len(v)) for k, v in sorted(s["zones"].items())))
        for r in face["rows"]:
            print("  %-3s %-13s %-15s m=%-8s range=%-22s spent=%-6s %s"
                  % (r["index"], r.get("leg"), r.get("cell"),
                     ("%.4f" % r["m_flip"]) if r["m_flip"] is not None else "-",
                     ("[%.4f,%.4f]" % tuple(r["offered_range"]))
                     if None not in r["offered_range"] else "-",
                     ("%.4f" % r["budget_spent"]) if r["budget_spent"] is not None else "-",
                     r["zone"]))
        return 0
    print("usage: e275_screen_margin_budget.py [run|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())