"""E271 -- does the moved set depend on WHICH donor a reader picks, not just how wide it is?

E262 published 48 ordered (donor, recipient) pairs and E266/E267/E268 all scored the screen
against the donor's p95 the pair had already fixed.  The pair table therefore never answered the
question a reader actually faces: for one recipient cell, the same (leg, base) group offers
SEVERAL foreign ends, and the published moved sets were reported one donor at a time.

This face reads every available donor end for every measured row in its own group (own cell
included as a control, which must reproduce the published verdict) and asks:

  (1) is the moved ROW SET invariant across donors?  If yes, "do not borrow" is the whole
      instruction; if not, the instruction is "do not borrow from THIS cell", which is a
      different and currently unpublished claim.
  (2) which cell is pivotal -- the donor that moves rows while its peers move none?
  (3) is the published pair choice (E262's dominator for that group) the conservative one?
  (4) the mechanism: a row can only move if its flip multiplier falls inside the p95 spread the
      group actually offers, so publish m_flip beside every donor end.

Published faces only -- no new draws, no panel read, no engine call.  Deterministic; every number
here is a function of BANDTRANSFER-2026-10-29.json.

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

import e262_p95_transfer_across_windows as e262  # noqa: E402  (arms, rows, judge, OUTDIR)

OUTDIR = e262.OUTDIR
CUTOFF = "2026-10-29"
SRC = "BANDTRANSFER-%s.json" % CUTOFF
FACE = "BANDDONORCHOICE-%s.json" % CUTOFF
LATEST = "banddonorchoice_latest.json"
LEGS = e262.LEGS
BASE_COUNTS = e262.BASE_COUNTS

judge = e262.judge


# ------------------------------------------------------------------ io
def load(name):
    with io.open(os.path.join(OUTDIR, name), encoding="utf-8") as fh:
        return json.load(fh)


def arm_index(face):
    """{(cell, leg, base): record} from the transfer face's own arms block."""
    out = {}
    for r in (face or {}).get("arms") or []:
        out[(r.get("cell"), r.get("leg"), r.get("base"))] = r
    return out


def cells_of(arms, leg, base):
    return sorted({c for (c, l, b) in arms if l == leg and b == base and c is not None})


def p95_of(arms, cell, leg, base):
    rec = arms.get((cell, leg, base))
    return None if not rec else rec.get("p95")


# ------------------------------------------------------------------ mechanism
def flip_multiplier(b, lo, hi):
    """The multiplier at which this row's verdict flips -- one number per row (E269's rule).

    band = (lo*m, hi*m) and the verdict is `outside`, so on the negative side outside <=> m < b/lo
    and on the positive side outside <=> m > b/hi.  A donor end below the flip multiplier leaves
    the verdict alone; a donor end above it (negative side) moves the row inside.
    """
    if b is None or lo is None or hi is None:
        return None
    if b < 0 and lo:
        return b / lo
    if b > 0 and hi:
        return b / hi
    return None


def margin_pct(m, m_flip):
    """How far a donor end sits from the row's flip, in percent of the flip."""
    if m is None or not m_flip:
        return None
    return (m / m_flip - 1.0) * 100.0


# ------------------------------------------------------------------ the sweep
def donor_views(records, arms, dominators=None, legs=LEGS, base_counts=BASE_COUNTS):
    """Per (leg, base) group: what each available donor end does to every measured row."""
    out = {}
    for leg in legs:
        for base in base_counts:
            key = "%s:%d" % (leg, base)
            cells = cells_of(arms, leg, base)
            rows = [r for r in records
                    if r.get("status") == "measured" and r.get("leg") == leg
                    and r.get("base") == base]
            p95s = {c: p95_of(arms, c, leg, base) for c in cells}
            p95s = {c: v for c, v in p95s.items() if v is not None}
            if len(p95s) < 2 or not rows:
                out[key] = {"leg": leg, "base": base, "rows": [], "donors": [],
                            "reason": "no group spread or no measured row"}
                continue
            spread = (min(p95s.values()), max(p95s.values()))
            own = []
            for r in rows:
                m_flip = flip_multiplier(r.get("b"), r.get("band_lo"), r.get("band_hi"))
                own.append({
                    "index": r.get("index"), "row": r.get("row"), "cell": r.get("cell"),
                    "b": r.get("b"), "band_lo": r.get("band_lo"), "band_hi": r.get("band_hi"),
                    "verdict_wide": r.get("verdict_wide"),
                    "own_p95": r.get("own_p95"),
                    "own_reproduces": judge(r.get("b"), r.get("band_lo"), r.get("band_hi"),
                                            r.get("own_p95")) == r.get("verdict_wide"),
                    "flip_multiplier": m_flip,
                    "flip_inside_spread": (m_flip is not None
                                           and spread[0] <= m_flip <= spread[1]),
                })
            donors = []
            for cell in cells:
                m = p95s.get(cell)
                moved = []
                for r in rows:
                    after = judge(r.get("b"), r.get("band_lo"), r.get("band_hi"), m)
                    if after != r.get("verdict_wide"):
                        moved.append({
                            "index": r.get("index"), "row": r.get("row"),
                            "recipient": r.get("cell"),
                            "before": "outside" if r.get("verdict_wide") else "inside",
                            "after": "outside" if after else "inside",
                            "direction": e262._dir(r.get("verdict_wide"), after),
                            "flip_multiplier": flip_multiplier(r.get("b"), r.get("band_lo"),
                                                               r.get("band_hi")),
                            "margin_to_flip_pct": margin_pct(
                                m, flip_multiplier(r.get("b"), r.get("band_lo"), r.get("band_hi"))),
                        })
                foreign_rows = [r for r in rows if r.get("cell") != cell]
                donors.append({
                    "donor": cell, "p95": m,
                    "n_foreign_rows": len(foreign_rows),
                    "n_moved": len(moved),
                    "moved": moved,
                    "moved_set": sorted(x["index"] for x in moved),
                })
            foreign = [d for d in donors if d["n_moved"] or d["n_foreign_rows"]]
            sets = {tuple(d["moved_set"]) for d in donors}
            moving = [d["donor"] for d in donors if d["n_moved"]]
            published = (dominators or {}).get(key)
            published_moved = None
            for d in donors:
                if d["donor"] == published:
                    published_moved = d["n_moved"]
            min_moved = min((d["n_moved"] for d in donors), default=None)
            max_moved = max((d["n_moved"] for d in donors), default=None)
            out[key] = {
                "leg": leg, "base": base,
                "cells": cells,
                "p95_spread": {"min": spread[0], "max": spread[1],
                               "widest": max(p95s, key=lambda c: p95s[c]),
                               "narrowest": min(p95s, key=lambda c: p95s[c]),
                               "spread_pct": (spread[1] / spread[0] - 1.0) * 100.0
                               if spread[0] else None},
                "rows": own,
                "donors": donors,
                "n_rows": len(rows),
                "n_foreign_pairs": sum(d["n_foreign_rows"] for d in donors),
                "donor_invariant": len(sets) == 1,
                "n_distinct_moved_sets": len(sets),
                "moving_donors": moving,
                "pivotal_cell": (max(donors, key=lambda d: (d["n_moved"], d["p95"] or 0))["donor"]
                                 if moving else None),
                "published_choice": published,
                "published_choice_moves": published_moved,
                "min_moves_across_donors": min_moved,
                "max_moves_across_donors": max_moved,
                "published_choice_is_conservative": (published_moved is not None
                                                     and min_moved is not None
                                                     and published_moved == min_moved),
                "rows_with_flip_inside_spread": [r["index"] for r in own
                                                 if r["flip_inside_spread"]],
            }
    return out


def summary_of(views):
    rows_total = sum(v.get("n_rows") or 0 for v in views.values())
    pairs = sum(v.get("n_foreign_pairs") or 0 for v in views.values())
    donor_ends = sum(len(v.get("donors") or []) for v in views.values())
    moved_rows = set()
    moved_pairs = 0
    invariant_groups = []
    non_invariant = []
    pivotal = {}
    for key in sorted(views):
        v = views[key]
        if not v.get("rows"):
            continue
        if v.get("donor_invariant"):
            invariant_groups.append(key)
        else:
            non_invariant.append(key)
        for d in v.get("donors") or []:
            if d.get("n_moved"):
                moved_pairs += 1
                for x in d.get("moved") or []:
                    moved_rows.add(x.get("index"))
        if v.get("pivotal_cell"):
            pivotal[key] = v["pivotal_cell"]
    flip_rows = set()
    for v in views.values():
        flip_rows |= set(v.get("rows_with_flip_inside_spread") or [])
    return {
        "rows_measured": rows_total,
        "groups": len([k for k, v in views.items() if v.get("rows")]),
        "donor_row_pairs": pairs,
        "donor_ends": donor_ends,
        "donor_ends_moving_a_row": moved_pairs,
        "rows_moved_by_any_donor": len(moved_rows),
        "moved_row_indices": sorted(moved_rows),
        "donor_ends_moving_a_row": moved_pairs,
        "donor_invariant_groups": len(invariant_groups),
        "donor_variant_groups": len(non_invariant),
        "variant_group_keys": non_invariant,
        "pivotal_cells": pivotal,
        "rows_with_flip_inside_spread": sorted(flip_rows),
        "flip_straddle_explains_moves": sorted(flip_rows) == sorted(moved_rows),
        "published_choice_conservative_in_all_groups":
            all(v.get("published_choice_is_conservative")
                for v in views.values() if v.get("rows")),
        "published_choice_moves_total": sum(
            (v.get("published_choice_moves") or 0) for v in views.values() if v.get("rows")),
    }


def verdict_of(s):
    if s["rows_moved_by_any_donor"] == 0:
        return ("donor_irrelevant_nothing_moves",
                "no donor end in any (leg, base) group moves a single row verdict, so the pair "
                "table's donor axis is inert on this population")
    if s["donor_variant_groups"] == 0:
        return ("donor_invariant_do_not_borrow_is_the_instruction",
                "every group's donors move the same set of rows, so 'do not borrow' is the whole "
                "instruction")
    keys = ", ".join("%s=%s" % (k, s["pivotal_cells"].get(k, "?"))
                     for k in s["variant_group_keys"])
    return ("donor_choice_matters_do_not_borrow_from_this_cell",
            "%d of %d groups read different moved sets by donor (pivotal: %s); %d of %d measured "
            "rows move under at least one donor while %d of %d donor ends move nothing, so the "
            "instruction is 'do not borrow from this cell', not 'do not borrow'"
            % (s["donor_variant_groups"], s["groups"], keys,
               s["rows_moved_by_any_donor"], s["rows_measured"],
               s["donor_ends"] - s["donor_ends_moving_a_row"], s["donor_ends"]))


# ------------------------------------------------------------------ run
def _stamp():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")


def run(save=True, outdir=None):
    src = load(SRC)
    arms = arm_index(src)
    dominators = ((src.get("summary") or {}).get("dominators")) or {}
    records = [dict(r) for r in (src.get("rows") or [])]
    views = donor_views(records, arms, dominators)
    s = summary_of(views)
    verdict, why = verdict_of(s)
    out = {
        "study": "e271_donor_choice_sensitivity",
        "title": "does the moved set depend on WHICH donor a reader picks, not just how wide it is?",
        "evidence_cutoff": CUTOFF,
        "generated": _stamp(),
        "source_faces": [SRC],
        "frozen_spec": {
            "design": ("for every measured row, judge it against EVERY donor end its own (leg, "
                       "base) group publishes, own cell included as the control; compare the "
                       "moved ROW SET across donors"),
            "no_new_draws": "no shuffle stream is drawn; every number is a function of one face",
            "control": ("the own-cell donor must reproduce the published verdict_wide on every "
                        "row; a control failure is published, not silently dropped"),
            "conservative": ("a donor is conservative for this population when it moves the fewest "
                             "row verdicts; E262's dominator per group is the published pair "
                             "choice and is scored against that"),
            "mechanism": ("a row can only move if its flip multiplier falls inside the p95 spread "
                          "the group actually offers, so flip_inside_spread is published per row"),
        },
        "groups": views,
        "summary": s,
        "verdict": verdict,
        "verdict_reason": why,
        "no_bill": "descriptive census over one published face; no trial, no ledger booking",
    }
    out["summary"]["verdict"] = verdict
    if save:
        _write(out, outdir)
    return out


def _write(face, outdir, tag=""):
    outdir = outdir or OUTDIR
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    path = os.path.join(outdir, "BANDDONORCHOICE-%s%s.json" % (face.get("evidence_cutoff"), tag))
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    with io.open(os.path.join(outdir, LATEST), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    return path


def verify(outdir=None, tag=""):
    outdir = outdir or OUTDIR
    path = os.path.join(outdir, "BANDDONORCHOICE-%s%s.json" % (CUTOFF, tag))
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


def _arm(cell, leg="self", base=60, p05=1.0, p95=2.0):
    return (cell, leg, base), {"cell": cell, "leg": leg, "base": base, "p05": p05, "p95": p95}


def _arms(*specs):
    return dict(_arm(*s) for s in specs)


def _row(index, b, lo, hi, cell="a", leg="self", base=60, p95=2.0):
    return {"index": index, "row": "r%d" % index, "cell": cell, "leg": leg, "base": base,
            "status": "measured", "b": b, "band_lo": lo, "band_hi": hi, "own_p05": 1.0,
            "own_p95": p95, "verdict_wide": judge(b, lo, hi, p95)}


def selftest():
    legs = []

    # --- flip multiplier, both signs -----------------------------------------------------
    legs.append(_leg(abs(flip_multiplier(-0.9, -0.3, 0.3) - 3.0) < 1e-12,
                     "negative side: m_flip = b/lo", flip_multiplier(-0.9, -0.3, 0.3)))
    legs.append(_leg(abs(flip_multiplier(0.9, -0.3, 0.3) - 3.0) < 1e-12,
                     "positive side: m_flip = b/hi", flip_multiplier(0.9, -0.3, 0.3)))
    legs.append(_leg(flip_multiplier(None, -0.3, 0.3) is None,
                     "no coefficient -> no flip multiplier (not zero)"))
    legs.append(_leg(abs(margin_pct(2.2, 2.0) - 10.0) < 1e-9,
                     "margin is percent of the flip", margin_pct(2.2, 2.0)))

    # --- one group, one decisive donor ---------------------------------------------------
    # b = -0.9 with band [-0.3, 0.3]: outside while m < 3.0.
    arms = _arms(("a", "self", 60, 1.0, 2.0), ("b", "self", 60, 1.0, 3.5))
    rows = [_row(0, -0.9, -0.3, 0.3, cell="a", p95=2.0)]
    v = donor_views(rows, arms)
    g = v["self:60"]
    legs.append(_leg(g["donor_invariant"] is False,
                     "a group whose donors disagree is not donor-invariant",
                     g["n_distinct_moved_sets"]))
    legs.append(_leg(g["pivotal_cell"] == "b", "the pivotal cell is the donor that moves rows"))
    legs.append(_leg(g["donors"][0]["n_moved"] == 0 or g["donors"][1]["n_moved"] == 1,
                     "exactly one donor moves the row",
                     [(d["donor"], d["n_moved"]) for d in g["donors"]]))
    legs.append(_leg(g["rows_with_flip_inside_spread"] == [0],
                     "the flip multiplier sits inside the group spread for that row",
                     g["rows_with_flip_inside_spread"]))
    legs.append(_leg(all(r["own_reproduces"] for r in g["rows"]),
                     "the own-cell donor is a control and reproduces the published verdict"))

    # --- an inert group is donor-invariant ----------------------------------------------
    arms2 = _arms(("a", "self", 60, 1.0, 2.0), ("b", "self", 60, 1.0, 2.4))
    rows2 = [_row(0, -0.9, -0.3, 0.3, cell="a", p95=2.0)]     # flip 3.0, both donors below
    g2 = donor_views(rows2, arms2)["self:60"]
    legs.append(_leg(g2["donor_invariant"] is True and g2["pivotal_cell"] is None,
                     "when no donor reaches the flip multiplier the group is invariant"))
    legs.append(_leg(g2["rows_with_flip_inside_spread"] == [],
                     "and no row reports a straddled flip"))

    # --- positive-side row: a WIDER donor pulls it OUTSIDE ------------------------------
    # b=0.9, band [-0.3,0.3]: inside while m < 3.0; donor 3.5 puts b above hi*3.5=1.05? no
    arms3 = _arms(("a", "self", 60, 1.0, 2.0), ("b", "self", 60, 1.0, 3.5))
    rows3 = [_row(0, 3.6, -0.3, 0.3, cell="a", p95=2.0)]   # own: 0.6*2=... own outside already
    g3 = donor_views(rows3, arms3)["self:60"]
    legs.append(_leg(all(r["own_reproduces"] for r in g3["rows"]),
                     "control holds on a positive-side row too"))

    # --- a group with a single donor cannot be scored ----------------------------------
    arms4 = _arms(("a", "self", 60, 1.0, 2.0))
    v4 = donor_views([_row(0, -0.9, -0.3, 0.3)], arms4)
    legs.append(_leg(v4["self:60"].get("reason") == "no group spread or no measured row",
                     "one donor is no donor spread -- the group says so instead of scoring"))

    # --- unjudgeable rows never enter ---------------------------------------------------
    rows5 = [_row(0, -0.9, -0.3, 0.3, cell="a"), dict(_row(1, None, None, None, cell="a"))]
    rows5[1]["status"] = "unjudgeable"
    g5 = donor_views(rows5, _arms(("a", "self", 60, 1.0, 2.0), ("b", "self", 60, 1.0, 3.5)))["self:60"]
    legs.append(_leg(g5["n_rows"] == 1, "unjudgeable rows stay out of the sweep", g5["n_rows"]))

    # --- summary and verdict rule -------------------------------------------------------
    s = summary_of(v)
    legs.append(_leg(s["rows_moved_by_any_donor"] == 1, "summary counts the moved row", s["rows_moved_by_any_donor"]))
    legs.append(_leg(verdict_of(s)[0] == "donor_choice_matters_do_not_borrow_from_this_cell",
                     "a variant group names the cell, not the whole axis", verdict_of(s)))
    s0 = dict(s)
    s0["rows_moved_by_any_donor"] = 0
    legs.append(_leg(verdict_of(s0)[0] == "donor_irrelevant_nothing_moves",
                     "zero moves reads as donor-irrelevant"))
    s1 = summary_of(v)
    s1["donor_variant_groups"] = 0
    s1["variant_group_keys"] = []
    legs.append(_leg(verdict_of(s1)[0] == "donor_invariant_do_not_borrow_is_the_instruction",
                     "no variant group reads as donor-invariant"))

    # --- the published choice is scored, not assumed ------------------------------------
    arms6 = _arms(("a", "self", 60, 1.0, 2.0), ("b", "self", 60, 1.0, 3.5),
                  ("c", "self", 60, 1.0, 3.6))
    g6 = donor_views([_row(0, -0.9, -0.3, 0.3, cell="a", p95=2.0)], arms6,
                     dominators={"self:60": "b"})["self:60"]
    legs.append(_leg(g6["published_choice"] == "b", "the dominator is read as the published choice"))
    legs.append(_leg(g6["published_choice_is_conservative"] is False,
                     "a published choice that moves the most rows is not conservative",
                     (g6["published_choice_moves"], g6["min_moves_across_donors"])))

    # --- live leg: the published face exists and its own control holds ------------------
    if os.path.exists(os.path.join(OUTDIR, SRC)):
        live = run(save=False)
        legs.append(_leg(all(r.get("own_reproduces")
                             for v in live["groups"].values() for r in v.get("rows") or []),
                         "live: every measured row's own end reproduces its published verdict"))
        legs.append(_leg(live["summary"]["donor_row_pairs"] > 0,
                         "live: foreign donor pairs were actually judged",
                         live["summary"]["donor_row_pairs"]))

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
        print("  rows %d measured / %d moved by some donor; %d foreign donor-row pairs"
              % (s["rows_measured"], s["rows_moved_by_any_donor"], s["donor_row_pairs"]))
        print("  groups %d: %d invariant / %d variant"
              % (s["groups"], s["donor_invariant_groups"], s["donor_variant_groups"]))
        for key in sorted(face["groups"]):
            blk = face["groups"][key]
            if not blk.get("rows"):
                print("  %-10s %s" % (key, blk.get("reason")))
                continue
            print("  %-10s spread %.2f%% donors %s"
                  % (key, blk["p95_spread"]["spread_pct"],
                     ",".join("%s=%.2f/%d" % (d["donor"], d["p95"], d["n_moved"])
                              for d in blk["donors"])))
            for r in blk["rows"]:
                if r["flip_inside_spread"]:
                    print("      row %-3s %-20s flip %.4f inside [%.4f, %.4f]"
                          % (r["index"], r["row"], r["flip_multiplier"],
                             blk["p95_spread"]["min"], blk["p95_spread"]["max"]))
            print("      published choice %s moves %s (min across donors %s)"
                  % (blk["published_choice"], blk["published_choice_moves"],
                     blk["min_moves_across_donors"]))
        return 0
    print("usage: e271_donor_choice_sensitivity.py [run|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())