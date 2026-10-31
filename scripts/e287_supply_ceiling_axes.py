"""E287 -- is the family's published ceiling one ceiling or many, and does any sibling face
already publish a wider multiplier that would reach the rows E285 called extrapolation?

E285 found six rows whose flip sits above the family's published p95 ceiling (2.2963) and called
them extrapolation, not widening headroom. That conclusion is only as good as the assumption that
2.2963 is the WIDEST multiplier anything in the family publishes. Several sibling faces publish a
number called `multiplier` or `multiplier_max`, and if one of them is on the same axis and larger,
one of those six rows would already be reachable without any new measurement.

The catch is that "multiplier" is not one quantity. This face censuses every dated face in the
band family that publishes such a number and signs each reading before comparing anything:

  * AXIS.  A reading is comparable to a row's flip only when it is a BAND-EDGE multiplier, i.e. a
    factor applied to both band edges (the flip multiplier m_flip is exactly b = edge * m). A
    ratio of spreads, a relative tolerance in percent, or an absolute band edge is a different
    quantity and is published as off-axis, never compared.
  * DIRECTION.  A REQUIREMENT (what a row needs, m_flip) is not a SUPPLY (what the family measured
    as obtainable). Only supply readings can bound reach; mixing the two is how a demand gets read
    as headroom.
  * BASIS.  A supply reading published as a central value (median over seeds) and the most extreme
    single seed the same face publishes are two different offers. Both are carried, the verdict is
    declared at the conservative one, and the optimistic one is published beside it -- never
    silently promoted.
  * CIRCULARITY.  E272's published tail ranges are the instrument E285's ceiling was read OFF
    (ceiling == the widest arm's wide.hi). Re-using them as supply would compare the ceiling with
    itself, so they are censused, marked unusable as supply, and the reason is printed.
  * SELF-INCLUSION.  This face never censuses itself or any `*_latest.json` mirror, and the
    discovery pass (any dated band face carrying a multiplier key that the manifest does not
    declare) is published as advisory: a verdict never depends on the live directory.

DECISION RULE, declared before any number is read:

  D1 AXIS   only a band-edge multiplier is comparable to m_flip; everything else is off-axis.
  D2 DIR    requirements and supplies are separate populations; only supplies bound reach.
  D3 BASIS  verdict at the conservative reading; optimistic reading published beside it.
  D4 REACH  a widening row is reached iff flip <= supply cap; shortfall = flip / cap (>1 = short).
  D5 CEIL   the family ceiling is read off the source summary AND asserted equal to the widest
            published arm top, so "one ceiling" is a measurement, not a claim.
  D6 SCOPE  the question is widening reach above the ceiling; the narrowing instrument found on
            the way is censused and its reach against the below-floor rows published, but that
            question belongs to the below-floor card and no verdict is taken on it here.

Verdict vocabulary (frozen):
  published_supply_reaches_a_row_above_the_published_ceiling
  published_supply_reaches_the_gap_rows_only
  no_published_supply_reaches_any_row_beyond_the_published_tails

Usage:  python scripts/e287_supply_ceiling_axes.py run|verify|selftest
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e272_flip_budget_two_tails as e272  # noqa: E402  (ROOT / OUTDIR)
import e_band_family_vintage as vintage    # noqa: E402  (E292: a face is a vintage)

ROOT = e272.ROOT
OUTDIR = e272.OUTDIR

STUDY = "E287_supply_ceiling_axes"
TITLE = ("is the family's published ceiling one ceiling or many -- do any sibling faces publish a "
         "wider band-edge multiplier that would already reach the rows E285 called extrapolation?")
CUTOFF = "2026-10-29"
SRC_GAPCEIL = "BANDGAPCEILING-%s.json" % CUTOFF    # E285: requirement rows + the family ceiling
SRC_WINMULT = "BANDWINMULT-%s.json" % CUTOFF       # E258: per-window draw multiplier (supply)
SRC_TOPFLIP = "BANDTOPFLIP-%s.json" % CUTOFF       # E257: borrowed ladder range (supply)
SRC_BUDGET = "BANDFLIPBUDGET-%s.json" % CUTOFF     # E272: published tail ranges (circular)
SRC_FLOOR = "BANDFLOOR-%s.json" % CUTOFF           # narrowing instrument (other direction)
SRC_DISAGREE = "BANDDISAGREE-%s.json" % CUTOFF     # independent statement of the same flips
SRC_DEFLATE = "BANDDEFLATE-%s.json" % CUTOFF        # degenerate-tail restatement (demand)
SRC_SUBST = "BANDSUBSTITUTE-%s.json" % CUTOFF       # a larger-looking number on another axis
FACE = "BANDSUPPLY-%s.json" % CUTOFF
LATEST = "bandsupply_latest.json"
SELF_FACES = (FACE, LATEST)

TOL = 1e-12
EDGE_AXIS = "band_edge_multiplier"

VERDICT_VOCAB = (
    "published_supply_reaches_a_row_above_the_published_ceiling",
    "published_supply_reaches_the_gap_rows_only",
    "no_published_supply_reaches_any_row_beyond_the_published_tails",
)

NO_BILL = ("measurement only: published faces are re-read and their published multipliers are "
           "compared on one axis. No shuffle stream is drawn, no band rebuilt, no engine runs. A "
           "verdict is a statement about what the family has already published, not about the "
           "market and not about what a bigger draw budget would eventually buy.")

# Which face publishes which quantity, signed before any number is read. A face absent from this
# manifest that carries a multiplier key is reported by the discovery pass, never dropped.
MANIFEST = (
    {"face": SRC_WINMULT,
     "quantity": "edge(top draws) / edge(published draws), per published window x base",
     "axis": EDGE_AXIS, "direction": "widen",
     "usable_as_supply": True,
     "basis_note": "median over seeds is the central reading; multiplier_max/_min are single seeds"},
    {"face": SRC_TOPFLIP,
     "quantity": "E257's borrowed ladder range (same edge multiplier, applied as a range)",
     "axis": EDGE_AXIS, "direction": "widen",
     "usable_as_supply": True,
     "basis_note": "summary median / min / max of the borrowed range"},
    {"face": SRC_BUDGET,
     "quantity": "published p05/p95 tail ranges across cells, in multiplier units",
     "axis": EDGE_AXIS, "direction": "widen",
     "usable_as_supply": False,
     "basis_note": "circular: E285's ceiling IS the widest arm top of this face"},
    {"face": SRC_FLOOR,
     "quantity": "counterfactual 5 pct band's own edge multiplier (lo_top / lo_base)",
     "axis": EDGE_AXIS, "direction": "narrow",
     "usable_as_supply": True,
     "basis_note": "a single published counterfactual, no seed scatter published"},
    {"face": SRC_DISAGREE,
     "quantity": "per-row flip_multiplier (a requirement, restated on another face)",
     "axis": EDGE_AXIS, "direction": "demand",
     "usable_as_supply": False,
     "basis_note": "requirements are the thing being reached, not a supply"},
    {"face": SRC_DEFLATE,
     "quantity": "the degenerate reading's own published tail range (multiplier_min/max)",
     "axis": EDGE_AXIS, "direction": "demand",
     "usable_as_supply": False,
     "basis_note": "a restatement of E272's tail range for the rows where the tail is degenerate; "
                   "it also publishes a relative tolerance in pct, which is off-axis entirely"},
    {"face": SRC_SUBST,
     "quantity": "a normalised-gap threshold in spreads (may_go_as_high_as)",
     "axis": "normalised_gap_threshold", "direction": "none",
     "usable_as_supply": False,
     "basis_note": "not a band-edge multiplier: it is measured in spreads, and comparing it with a "
                   "flip multiplier would be the parametrisation error this study exists to avoid"},
)


# ------------------------------------------------------------------ io
def load(name, outdir=None):
    with io.open(os.path.join(outdir or OUTDIR, name), encoding="utf-8") as fh:
        return json.load(fh)


def _num(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out


# ------------------------------------------------------------------ requirement rows
CLASS_OF_INTEREST = ("above_ceiling", "in_gap", "below_floor")


def requirement_rows(face):
    """E285's own rows, re-read; only the classes that are NOT already reached are carried."""
    out = []
    for block in ("beyond_ceiling", "widening_target", "below_floor"):
        for rec in ((face.get(block) or {}).get("rows") or []):
            cls = rec.get("class")
            if cls not in CLASS_OF_INTEREST:
                continue
            flip = _num(rec.get("flip"))
            if flip is None:
                continue
            out.append({"row_key": rec.get("row_key"), "cell": rec.get("cell"),
                        "class": cls, "flip": flip,
                        "direction": "widen" if flip > 1.0 else "narrow"})
    return out


def demand_identity(rows, dis):
    """The same flips, stated by another face -- an identity, not a copy."""
    key = lambda r: "%s|%s|%s" % (r.get("row") or r.get("leg"), r.get("base"), r.get("index"))
    theirs = {}
    for rec in (dis.get("census") or []):
        theirs[key(rec)] = _num(rec.get("flip_multiplier"))
    joined, worst = 0, 0.0
    for rec in rows:
        other = theirs.get(rec["row_key"])
        if other is None:
            continue
        joined += 1
        worst = max(worst, abs(other - rec["flip"]))
    return {"n_joined": joined, "max_abs_diff": worst,
            "agree": bool(joined and worst <= 1e-9),
            "published_by_other_face": len(theirs)}


# ------------------------------------------------------------------ supply readings
def supply_readings(outdir=None):
    """One signed reading per (face, window/base, basis). ``cap`` is the multiplier on offer."""
    out = []

    def push(face, label, direction, basis, cap, quantity, usable=True, note=None):
        cap = _num(cap)
        if cap is None:
            return
        out.append({"face": face, "label": label, "direction": direction, "basis": basis,
                    "cap": cap, "axis": EDGE_AXIS, "quantity": quantity,
                    "usable_as_supply": usable, "note": note})

    # E258 -- a band-edge multiplier measured inside each published window x base
    win = load(SRC_WINMULT, outdir)
    for cell, rec in sorted((win.get("windows") or {}).items()):
        for base, blk in sorted((rec.get("by_base") or {}).items()):
            label = "%s|%s" % (cell, base)
            med = _num(blk.get("multiplier"))
            push(SRC_WINMULT, label, "widen", "central", med,
                 "edge(top)/edge(published), median over seeds")
            push(SRC_WINMULT, label, "widen", "extreme", blk.get("multiplier_max"),
                 "edge(top)/edge(published), single best seed")
            push(SRC_WINMULT, label, "narrow", "extreme", blk.get("multiplier_min"),
                 "edge(top)/edge(published), single weakest seed")

    # E257 -- the borrowed ladder range (a range, so its published ends are the caps)
    top = (load(SRC_TOPFLIP, outdir).get("summary") or {})
    push(SRC_TOPFLIP, "borrowed_range", "widen", "central", top.get("multiplier_median"),
         "borrowed ladder multiplier, median")
    push(SRC_TOPFLIP, "borrowed_range", "widen", "extreme", top.get("multiplier_max"),
         "borrowed ladder multiplier, published top")
    push(SRC_TOPFLIP, "borrowed_range", "narrow", "extreme", top.get("multiplier_min"),
         "borrowed ladder multiplier, published bottom")

    # E272 -- the published tail ranges: censused, but circular as a supply (D5)
    budget = (load(SRC_BUDGET, outdir).get("tail_budget") or {})
    for arm_key, arm in sorted(budget.items()):
        for tail in ("tight", "wide"):
            blk = arm.get("%s_range" % tail) or {}
            push(SRC_BUDGET, "%s|%s" % (arm_key, tail), "widen", "central", blk.get("max"),
                 "published %s range across cells" % ("p05" if tail == "tight" else "p95"),
                 usable=False, note="circular: this is the range E285's ceiling was read off")

    # BANDFLOOR -- the one narrowing instrument the family publishes
    floor = (load(SRC_FLOOR, outdir).get("counterfactual_percentile_band") or {})
    push(SRC_FLOOR, "counterfactual_band", "narrow", "central", floor.get("multiplier"),
         "lo_top / lo_base of the counterfactual 5 pct band")

    # BANDDEFLATE -- the degenerate tail's own range, restated: a demand, never a supply
    for rec in (load(SRC_DEFLATE, outdir).get("degenerate_readings") or []):
        push(SRC_DEFLATE, str(rec.get("row_key")), "widen", "central", rec.get("multiplier_max"),
             "degenerate tail's published range", usable=False,
             note="circular/demand restatement of E272's tail range")
    return out


def off_axis_readings(outdir=None):
    """Numbers that LOOK like a wider multiplier and are not one. Publishing them is the point:
    a reader who finds 2.0327 or 63.0 pct must see why neither was compared."""
    out = []

    def push(face, label, value, reason):
        value = _num(value)
        if value is not None:
            out.append({"face": face, "label": label, "value": value, "reason": reason})

    tb = (load(SRC_DEFLATE, outdir).get("tolerance_band") or {})
    push(SRC_DEFLATE, "tolerance_band.lower_pct", tb.get("lower_pct"),
         "a relative tolerance in percent, not a band-edge multiplier: it prices how loose a test "
         "must be before the reading fires, and a looser test is not a wider band")
    spread = (load(SRC_WINMULT, outdir).get("multiplier_spread") or {})
    push(SRC_WINMULT, "multiplier_spread.ratio_max_over_min", spread.get("ratio_max_over_min"),
         "the ratio of two multipliers (how far the multiplier moves across windows), not itself "
         "a multiplier of any band")
    bracket = (load(SRC_SUBST, outdir).get("scope_bracket") or {})
    push(SRC_SUBST, "scope_bracket.may_go_as_high_as", bracket.get("may_go_as_high_as"),
         "a threshold on the normalised gap measured in spreads, not a band-edge multiplier")
    return out


def supply_caps(readings):
    """The two offers per direction: conservative (central readings) and optimistic (any reading)."""
    def pick(direction, usable_only=True, ceiling_basis=None):
        cand = [r["cap"] for r in readings
                if r["direction"] == direction
                and (r["usable_as_supply"] or not usable_only)
                and (ceiling_basis is None or r["basis"] in ceiling_basis)]
        if not cand:
            return None, None
        value = max(cand) if direction == "widen" else min(cand)
        who = [r for r in readings
               if r["direction"] == direction and abs(r["cap"] - value) <= TOL]
        return value, (who[0] if who else None)

    out = {}
    for direction in ("widen", "narrow"):
        cons, cons_at = pick(direction, ceiling_basis=("central",))
        opt, opt_at = pick(direction)
        out[direction] = {
            "conservative": {"cap": cons,
                             "at": None if not cons_at else {"face": cons_at["face"],
                                                             "label": cons_at["label"],
                                                             "basis": cons_at["basis"]}},
            "optimistic": {"cap": opt,
                           "at": None if not opt_at else {"face": opt_at["face"],
                                                          "label": opt_at["label"],
                                                          "basis": opt_at["basis"]}},
            "optimistic_adds": (None if (cons is None or opt is None)
                                else (round(opt - cons, 12) if direction == "widen"
                                      else round(cons - opt, 12))),
        }
    return out


# ------------------------------------------------------------------ reach
def reach_of(row, caps):
    """D4: reached iff the flip is inside what the cap offers; shortfall = the factor still missing."""
    direction = row["direction"]
    block = caps.get(direction) or {}
    flip = row["flip"]
    out = {"row_key": row["row_key"], "class": row["class"], "flip": flip,
           "direction": direction}
    for basis in ("conservative", "optimistic"):
        cap = (block.get(basis) or {}).get("cap")
        if cap is None:
            out[basis] = {"cap": None, "reached": None, "shortfall_factor": None}
            continue
        if direction == "widen":
            reached = flip <= cap + TOL
            factor = None if reached or not cap else flip / cap
        else:
            reached = flip >= cap - TOL
            factor = None if reached or not flip else cap / flip
        out[basis] = {"cap": cap, "reached": reached, "shortfall_factor": factor}
    out["reached_any"] = bool((out["conservative"]["reached"] or out["optimistic"]["reached"]))
    out["reached_conservative"] = bool(out["conservative"]["reached"])
    return out


def by_class(reach_rows, cls):
    return [r for r in reach_rows if r["class"] == cls]


def decide(summary):
    above = summary.get("reach_by_class", {}).get("above_ceiling", {})
    gap = summary.get("reach_by_class", {}).get("in_gap", {})
    if above.get("n_reached_optimistic") or above.get("n_reached_conservative"):
        return "published_supply_reaches_a_row_above_the_published_ceiling"
    if gap.get("n_reached_optimistic") or gap.get("n_reached_conservative"):
        return "published_supply_reaches_the_gap_rows_only"
    return "no_published_supply_reaches_any_row_beyond_the_published_tails"


# ------------------------------------------------------------------ discovery (advisory)
def _walk_multiplier_paths(obj, prefix=""):
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = "%s/%s" % (prefix, key)
            if key in ("multiplier", "multiplier_min", "multiplier_max"):
                yield path
            else:
                for hit in _walk_multiplier_paths(value, path):
                    yield hit
    elif isinstance(obj, list):
        for item in obj:
            for hit in _walk_multiplier_paths(item, prefix + "/[]"):
                yield hit


def discovery(outdir=None):
    """Completeness disclosure, frozen to the census this face publishes (E292: a face is a vintage).

    The declared manifest IS the stored name list, so re-deriving never silently widens the universe
    when a sibling publishes a new multiplier face: that face is disclosed as
    ``faces_excluded_as_later`` and the verdict keeps the reading it published.
    """
    outdir = outdir or OUTDIR
    declared = [m["face"] for m in MANIFEST]
    missing = [f for f in declared if not os.path.exists(os.path.join(outdir, f))]
    used = [f for f in declared if f not in missing]
    scanned, dated, mirrors = 0, [], []
    for name in sorted(os.listdir(outdir)):
        if not name.endswith(".json") or name in SELF_FACES:
            continue
        try:
            with io.open(os.path.join(outdir, name), encoding="utf-8") as fh:
                doc = json.load(fh)
        except (ValueError, IOError):
            continue
        scanned += 1
        if not list(_walk_multiplier_paths(doc)):
            continue
        if name.endswith("_latest.json"):
            mirrors.append(name)
            continue
        dated.append(name)
    excluded = [f for f in dated if f not in declared]
    out = vintage.note(used, excluded, len(dated), FACE, None)
    out.update({
        "faces_scanned": scanned,
        "dated_faces_with_a_multiplier_key": dated,
        "faces_declared": declared,
        "faces_used_names": used,
        "faces_declared_but_missing": missing,
        "mirrors_excluded": mirrors,
        "unclassified_faces": excluded,
        "census_complete": not excluded and not missing,
        "note": "frozen to the declared manifest: a dated face carrying a multiplier key that is "
                "not declared is disclosed as excluded-as-later, never silently added to the caps "
                "and never silently dropped",
    })
    return out


# ------------------------------------------------------------------ build
def build(outdir=None):
    outdir = outdir or OUTDIR
    gap = load(SRC_GAPCEIL, outdir)
    src_summary = gap.get("summary") or {}
    ceiling = _num(src_summary.get("published_ceiling"))
    floor = _num(src_summary.get("published_floor"))

    readings = supply_readings(outdir)
    caps = supply_caps(readings)
    rows = requirement_rows(gap)
    reach_rows = [reach_of(r, caps) for r in rows]

    # D5: "one ceiling" is measured, not assumed -- the family ceiling must be the widest
    # published arm top, and every arm top is published beside it.
    budget = (load(SRC_BUDGET, outdir).get("tail_budget") or {})
    arm_tops = {}
    for arm_key, arm in budget.items():
        tops = [_num((arm.get("%s_range" % t) or {}).get("max")) for t in ("tight", "wide")]
        tops = [t for t in tops if t is not None]
        if tops:
            arm_tops[str(arm_key)] = max(tops)
    widest = max(arm_tops.values()) if arm_tops else None

    ident = demand_identity(rows, load(SRC_DISAGREE, outdir))
    ident["ceiling_equals_widest_published_arm_top"] = bool(
        ceiling is not None and widest is not None and abs(ceiling - widest) <= 1e-9)
    ident["ceiling_arms"] = arm_tops
    ident["n_arm_tops_below_the_family_ceiling"] = sum(
        1 for v in arm_tops.values() if v < (ceiling or 0) - TOL)
    ident["rows_are_the_e285_unreached_set"] = bool(
        sorted(r["row_key"] for r in rows) ==
        sorted(list(src_summary.get("above_ceiling_rows") or []) +
               list(src_summary.get("gap_rows") or []) +
               list(src_summary.get("below_floor_rows") or [])))
    ident["no_reading_above_the_ceiling_except_the_circular_one"] = bool(
        all(r["cap"] <= (ceiling or 0) + TOL
            for r in readings if r["direction"] == "widen" and r["usable_as_supply"]))

    grouped = {}
    for cls in CLASS_OF_INTEREST:
        mine = by_class(reach_rows, cls)
        grouped[cls] = {
            "n_rows": len(mine),
            "n_reached_conservative": sum(1 for r in mine if r["reached_conservative"]),
            "n_reached_optimistic": sum(1 for r in mine
                                        if r["optimistic"]["reached"]),
            "rows": [{"row_key": r["row_key"], "flip": r["flip"], "direction": r["direction"],
                      "reached_conservative": r["reached_conservative"],
                      "reached_optimistic": r["optimistic"]["reached"],
                      "shortfall_factor_conservative": r["conservative"]["shortfall_factor"],
                      "shortfall_factor_optimistic": r["optimistic"]["shortfall_factor"]}
                     for r in mine],
        }

    def nearest(cls):
        """The row of a class that the optimistic cap comes closest to reaching, and whether the
        class is closed outright (every row reached at the optimistic cap)."""
        mine = by_class(reach_rows, cls)
        cand = [r for r in mine if r["optimistic"]["shortfall_factor"] is not None]
        if not cand:
            return {"row_key": None, "all_rows_reached_at_optimistic": bool(mine),
                    "n_rows": len(mine), "shortfall_factor_optimistic": None,
                    "pct_short": None}
        best = min(cand, key=lambda r: r["optimistic"]["shortfall_factor"])
        return {"row_key": best["row_key"], "flip": best["flip"],
                "all_rows_reached_at_optimistic": False,
                "n_rows_not_reached_at_optimistic": len(cand),
                "shortfall_factor_optimistic": best["optimistic"]["shortfall_factor"],
                "pct_short": (best["optimistic"]["shortfall_factor"] - 1.0) * 100.0}

    summary = {
        "ceiling": ceiling,
        "floor": floor,
        "n_supply_readings": len(readings),
        "n_supply_readings_used": sum(1 for r in readings if r["usable_as_supply"]),
        "n_supply_readings_rejected": sum(1 for r in readings if not r["usable_as_supply"]),
        "n_off_axis_refused": len(off_axis_readings(outdir)),
        "widen_cap_conservative": caps["widen"]["conservative"]["cap"],
        "widen_cap_optimistic": caps["widen"]["optimistic"]["cap"],
        "widen_cap_conservative_at": caps["widen"]["conservative"]["at"],
        "widen_cap_optimistic_at": caps["widen"]["optimistic"]["at"],
        "narrow_cap_conservative": caps["narrow"]["conservative"]["cap"],
        "narrow_cap_optimistic": caps["narrow"]["optimistic"]["cap"],
        "optimistic_adds_multiplier": caps["widen"]["optimistic_adds"],
        "ceiling_over_optimistic_cap": (None if not (ceiling and caps["widen"]["optimistic"]["cap"])
                                        else ceiling / caps["widen"]["optimistic"]["cap"]),
        "reach_by_class": grouped,
        "nearest_above_ceiling": nearest("above_ceiling"),
        "nearest_gap": nearest("in_gap"),
        "nearest_below_floor": nearest("below_floor"),
        "n_classes_examined": len(CLASS_OF_INTEREST),
    }
    verdict = decide(summary)
    summary["verdict"] = verdict

    return {
        "study": STUDY, "title": TITLE, "evidence_cutoff": CUTOFF, "generated": None,
        "no_bill": NO_BILL,
        "source_faces": [SRC_GAPCEIL, SRC_WINMULT, SRC_TOPFLIP, SRC_BUDGET, SRC_FLOOR,
                         SRC_DISAGREE],
        "frozen_spec": {
            "D1_axis": "only a band-edge multiplier is comparable to m_flip (b = edge * m); a "
                       "spread ratio, a relative tolerance in pct, or an absolute edge is off-axis "
                       "and is never compared",
            "D2_direction": "requirements and supplies are separate populations; only supplies "
                            "bound reach",
            "D3_basis": "the verdict is taken at the conservative (central) supply reading; the "
                        "optimistic (most extreme single seed) reading is published beside it and "
                        "the rows it adds are named",
            "D4_reach": "a widening row is reached iff flip <= cap; shortfall = flip / cap, so a "
                        "factor above 1 is the widening still missing",
            "D5_ceiling": "the family ceiling is read off the source summary AND asserted equal to "
                          "the widest published arm top, so 'one ceiling' is measured",
            "D6_scope": "the question is widening reach above the ceiling; the narrowing "
                        "instrument's reach is published for the below-floor card and no verdict "
                        "is taken on it here",
            "tolerance": TOL,
            "verdict_vocab": list(VERDICT_VOCAB),
        },
        "axis_manifest": [dict(m) for m in MANIFEST],
        "supply_caps": caps,
        "supply_readings": sorted(readings, key=lambda r: (r["direction"], r["face"],
                                                           r["label"], r["basis"])),
        "off_axis_readings": off_axis_readings(outdir),
        "rows": reach_rows,
        "demand_identity": ident,
        "discovery": discovery(outdir),
        "summary": summary,
        "verdict": verdict,
        "verdict_reason": _reason(verdict, summary),
    }


def _fmt(value):
    return "n/a" if value is None else "%.6f" % value


def _reason(verdict, summary):
    cons = summary["widen_cap_conservative"]
    opt = summary["widen_cap_optimistic"]
    ceil = summary["ceiling"]
    above = summary["reach_by_class"]["above_ceiling"]
    gap = summary["reach_by_class"]["in_gap"]
    near = summary["nearest_above_ceiling"] or {}
    floor_near = summary["nearest_below_floor"] or {}
    tail = ""
    if near.get("row_key"):
        tail = ("; the nearest above-ceiling row (%s, flip %s) is still %s pct short of the "
                "optimistic cap" % (near["row_key"], _fmt(near["flip"]),
                                    _fmt(near.get("pct_short"))))
    if floor_near.get("row_key"):
        tail += ("; on the opposite polarity the published narrowing instrument (%s) is %s pct "
                 "short of the nearest below-floor row (%s, flip %s), so neither margin is closed "
                 "by anything already published"
                 % (_fmt(summary["narrow_cap_optimistic"]), _fmt(floor_near.get("pct_short")),
                    floor_near["row_key"], _fmt(floor_near["flip"])))
    if verdict == "published_supply_reaches_a_row_above_the_published_ceiling":
        return ("a published band-edge multiplier reaches at least one of the %d row(s) above the "
                "ceiling %s, so E285's extrapolation label needs narrowing" %
                (above["n_rows"], _fmt(ceil)) + tail)
    if verdict == "published_supply_reaches_the_gap_rows_only":
        return ("no sibling publishes a band-edge multiplier above the family ceiling %s "
                "(supply top: %s central / %s at a single seed), so none of the %d above-ceiling "
                "row(s) is reachable by anything already published%s; the published supplies do "
                "reach %d of %d gap row(s) -- %d at the conservative cap, %d only at the single "
                "best seed -- so the gap is the one place existing supply could pay." %
                (_fmt(ceil), _fmt(cons), _fmt(opt), above["n_rows"], tail,
                 gap["n_reached_optimistic"], gap["n_rows"],
                 gap["n_reached_conservative"], gap["n_reached_optimistic"]))
    return ("no published band-edge multiplier reaches any row beyond the published tails: the "
            "ceiling %s stands above every supply reading (%s central / %s at a single seed), the "
            "%d above-ceiling row(s) and the %d gap row(s) are all short" %
            (_fmt(ceil), _fmt(cons), _fmt(opt), above["n_rows"], gap["n_rows"]) + tail)


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
    print("E287 %s" % face["verdict"])
    print("  ceiling=%s | widen cap %s (central) / %s (single seed) | narrow cap %s"
          % (_fmt(s["ceiling"]), _fmt(s["widen_cap_conservative"]),
             _fmt(s["widen_cap_optimistic"]), _fmt(s["narrow_cap_conservative"])))
    for cls in CLASS_OF_INTEREST:
        g = s["reach_by_class"][cls]
        print("  %-14s rows=%d reached central=%d optimistic=%d"
              % (cls, g["n_rows"], g["n_reached_conservative"], g["n_reached_optimistic"]))
    near = s["nearest_above_ceiling"]
    if near:
        print("  nearest above-ceiling %s flip=%s short=%s pct"
              % (near["row_key"], _fmt(near["flip"]), _fmt(near["pct_short"])))
    print("  readings=%d used=%d rejected=%d | census_complete=%s"
          % (s["n_supply_readings"], s["n_supply_readings_used"],
             s["n_supply_readings_rejected"], face["discovery"]["census_complete"]))
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
    for key in ("ceiling", "widen_cap_conservative", "widen_cap_optimistic",
                "narrow_cap_conservative", "nearest_above_ceiling"):
        if ss.get(key) != ls.get(key):
            problems.append("summary.%s does not re-derive" % key)
    for cls in CLASS_OF_INTEREST:
        a = (ss.get("reach_by_class") or {}).get(cls) or {}
        b = (ls.get("reach_by_class") or {}).get(cls) or {}
        if a.get("n_reached_optimistic") != b.get("n_reached_optimistic") or \
                a.get("n_reached_conservative") != b.get("n_reached_conservative"):
            problems.append("reach for %s does not re-derive" % cls)
    ic = live["demand_identity"]
    if not ic["agree"]:
        problems.append("the flips do not match the other face that publishes them (D1 identity)")
    if not ic["ceiling_equals_widest_published_arm_top"]:
        problems.append("the family ceiling is not the widest published arm top (D5)")
    if not ic["rows_are_the_e285_unreached_set"]:
        problems.append("the requirement rows are not E285's unreached set")
    if not ic["no_reading_above_the_ceiling_except_the_circular_one"]:
        problems.append("a usable supply reading exceeds the ceiling: the verdict must be revisited")
    if not stored.get("discovery", {}).get("census_complete"):
        problems.append("the multiplier census has an unclassified face")
    if live["discovery"].get("faces_declared_but_missing"):
        problems.append("a declared source face is missing from the disk")
    print("E287 verify: %d problem(s)" % len(problems))
    for p in problems:
        print("  - %s" % p)
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
def _caps(widen_cons, widen_opt, narrow_cons=None, narrow_opt=None):
    return {"widen": {"conservative": {"cap": widen_cons, "at": None},
                      "optimistic": {"cap": widen_opt, "at": None}},
            "narrow": {"conservative": {"cap": narrow_cons, "at": None},
                       "optimistic": {"cap": narrow_opt, "at": None}}}


def cmd_selftest():
    ok, fail = 0, []

    def leg(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append("%s %s" % (name, detail))

    # L1 a widening row is reached exactly at the cap (inclusive), not only below it
    caps = _caps(2.0, 2.2)
    leg("L1", reach_of({"row_key": "a", "class": "above_ceiling", "flip": 2.0,
                        "direction": "widen"}, caps)["reached_conservative"])
    # L2 one step above the cap is short, and the shortfall is flip/cap
    r = reach_of({"row_key": "a", "class": "above_ceiling", "flip": 2.2, "direction": "widen"},
                 caps)
    leg("L2", not r["reached_conservative"] and abs(r["conservative"]["shortfall_factor"] - 1.1) < 1e-12,
        r["conservative"])
    # L3 the optimistic cap can reach a row the conservative one does not -- and that is published
    r2 = reach_of({"row_key": "g", "class": "in_gap", "flip": 2.1, "direction": "widen"}, caps)
    leg("L3", (not r2["reached_conservative"]) and r2["optimistic"]["reached"]
        and r2["reached_any"], r2)
    # L4 a narrowing row is reached when the flip is AT OR BELOW the cap (opposite polarity)
    ncaps = _caps(2.0, 2.2, 0.9, 0.9)
    r3 = reach_of({"row_key": "b", "class": "below_floor", "flip": 0.89, "direction": "narrow"}, ncaps)
    leg("L4", r3["reached_conservative"] is False
        and abs(r3["conservative"]["shortfall_factor"] - 0.9 / 0.89) < 1e-12, r3["conservative"])
    # L5 a missing cap is unknown, never "reached" and never a fabricated factor
    r4 = reach_of({"row_key": "c", "class": "above_ceiling", "flip": 2.0, "direction": "widen"},
                  _caps(None, None))
    leg("L5", r4["conservative"]["reached"] is None and r4["conservative"]["shortfall_factor"] is None
        and r4["reached_any"] is False, r4["conservative"])
    # L6 verdict: an above-ceiling row reached anywhere outranks a gap row
    leg("L6", decide({"reach_by_class": {"above_ceiling": {"n_reached_optimistic": 1},
                                         "in_gap": {"n_reached_optimistic": 2}}})
        == "published_supply_reaches_a_row_above_the_published_ceiling")
    # L7 verdict: gap rows only is its own sentence
    leg("L7", decide({"reach_by_class": {"above_ceiling": {"n_reached_optimistic": 0},
                                         "in_gap": {"n_reached_optimistic": 2},
                                         "below_floor": {"n_reached_optimistic": 2}}})
        == "published_supply_reaches_the_gap_rows_only")
    # L8 verdict: nothing reached is honest, even when the narrowing side is reached
    leg("L8", decide({"reach_by_class": {"above_ceiling": {"n_reached_optimistic": 0},
                                         "in_gap": {"n_reached_optimistic": 0},
                                         "below_floor": {"n_reached_optimistic": 2}}})
        == "no_published_supply_reaches_any_row_beyond_the_published_tails")
    # L9 the caps pick the widest usable widening offer and the tightest narrowing one
    readings = [
        {"face": "f", "label": "a", "direction": "widen", "basis": "central", "cap": 1.5,
         "axis": EDGE_AXIS, "quantity": "q", "usable_as_supply": True, "note": None},
        {"face": "f", "label": "b", "direction": "widen", "basis": "extreme", "cap": 1.9,
         "axis": EDGE_AXIS, "quantity": "q", "usable_as_supply": True, "note": None},
        {"face": "f", "label": "c", "direction": "widen", "basis": "central", "cap": 9.9,
         "axis": EDGE_AXIS, "quantity": "q", "usable_as_supply": False, "note": "circular"},
        {"face": "f", "label": "d", "direction": "narrow", "basis": "central", "cap": 0.8,
         "axis": EDGE_AXIS, "quantity": "q", "usable_as_supply": True, "note": None},
        {"face": "f", "label": "e", "direction": "narrow", "basis": "extreme", "cap": 0.7,
         "axis": EDGE_AXIS, "quantity": "q", "usable_as_supply": True, "note": None},
    ]
    got = supply_caps(readings)
    leg("L9", abs(got["widen"]["conservative"]["cap"] - 1.5) < 1e-12
        and abs(got["widen"]["optimistic"]["cap"] - 1.9) < 1e-12
        and abs(got["narrow"]["conservative"]["cap"] - 0.8) < 1e-12
        and abs(got["narrow"]["optimistic"]["cap"] - 0.7) < 1e-12, got)
    # L10 a circular reading (9.9) is NOT usable as supply, so it never sets the cap
    leg("L10", got["widen"]["optimistic"]["cap"] < 9.9, got["widen"]["optimistic"])
    # L11 the optimistic-minus-conservative gap is published, so a reader can see what it bought
    leg("L11", abs(got["widen"]["optimistic_adds"] - 0.4) < 1e-12, got["widen"]["optimistic_adds"])
    # L12 requirement rows carry only the unreached classes and take their direction from the flip
    fake = {"beyond_ceiling": {"rows": [{"row_key": "x", "flip": 3.0, "class": "above_ceiling"}]},
            "widening_target": {"rows": [{"row_key": "y", "flip": 1.5, "class": "in_gap"}]},
            "below_floor": {"rows": [{"row_key": "z", "flip": 0.6, "class": "below_floor"}]},
            "arms": []}
    rows = requirement_rows(fake)
    leg("L12", [r["direction"] for r in rows] == ["widen", "widen", "narrow"]
        and len(rows) == 3, rows)
    # L13 an already-reached class is not a requirement
    fake2 = dict(fake)
    fake2["widening_target"] = {"rows": [{"row_key": "y", "flip": 1.5, "class": "reachable_wide"}]}
    leg("L13", len(requirement_rows(fake2)) == 2)
    # L14 the demand identity joins on the row key and reports the worst disagreement
    dis = {"census": [{"row": "x", "base": None, "index": None, "flip_multiplier": 3.0}]}
    idn = demand_identity([{"row_key": "x|None|None", "flip": 3.0}], dis)
    leg("L14", idn["agree"] and idn["n_joined"] == 1 and idn["max_abs_diff"] == 0.0, idn)
    # L15 ... and a disagreement is not smoothed away
    idn2 = demand_identity([{"row_key": "x|None|None", "flip": 3.5}], dis)
    leg("L15", idn2["agree"] is False and abs(idn2["max_abs_diff"] - 0.5) < 1e-12, idn2)
    # L16 a row that the other face does not publish is not counted as joined
    leg("L16", demand_identity([{"row_key": "q|1|2", "flip": 1.0}], dis)["n_joined"] == 0)
    # L17 on the real face: the census is complete, the ceiling is the widest arm top, and no
    # usable supply exceeds it
    live = build()
    ic = live["demand_identity"]
    leg("L17", ic["agree"] and ic["ceiling_equals_widest_published_arm_top"]
        and ic["no_reading_above_the_ceiling_except_the_circular_one"], ic)
    # L18 the real face censuses its own rows from E285, not a restatement
    leg("L18", ic["rows_are_the_e285_unreached_set"] and ic["n_joined"] >= 8, ic)
    # L19 this face never censuses itself (E180/E209/E294 self-inclusion family)
    leg("L19", all(f not in live["discovery"]["dated_faces_with_a_multiplier_key"]
                   for f in SELF_FACES), live["discovery"]["dated_faces_with_a_multiplier_key"])
    # L20 E292: the census is frozen to the declared manifest, so a re-derivation cannot silently
    # widen the universe -- only every declared face actually present is used
    disc = live["discovery"]
    leg("L20", set(disc["faces_declared"]) == set(m["face"] for m in MANIFEST)
        and set(disc["faces_used_names"]) <= set(disc["faces_declared"])
        and disc["faces_used"] == len(disc["faces_used_names"])
        and not disc["faces_declared_but_missing"]
        and disc["faces_excluded_as_later"] == disc["unclassified_faces"], disc["faces_used"])
    # L21 the two polarities partition cleanly on the real face: every widening reading is at or
    # above 1.0 and at least one narrowing instrument sits below it
    narrow = [r for r in live["supply_readings"] if r["direction"] == "narrow"]
    widen = [r for r in live["supply_readings"] if r["direction"] == "widen"]
    leg("L21", bool(narrow) and all(r["cap"] >= 1.0 for r in widen)
        and any(r["cap"] < 1.0 for r in narrow) and len(widen) > len(narrow),
        {"widen_min": min(r["cap"] for r in widen), "narrow": [r["cap"] for r in narrow]})
    # L22 every reading is signed (axis present) so an off-axis number cannot slip into the caps
    leg("L22", all(r.get("axis") == EDGE_AXIS for r in live["supply_readings"]))

    print("E287 selftest: %d/%d" % (ok, ok + len(fail)))
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