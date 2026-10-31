"""E288 -- the mirror of the widening question: a flip BELOW the published floor of 1.0 needs the
band NARROWED, so "unreachable" must never be published as a single direction of fix.

E285 partitioned the twelve flips of the band family into reachable / in-gap / above-ceiling /
below-floor, and E287 then asked (and answered) the widening half: no published supply reaches a
row above the ceiling. The below-floor class was left to this card because it is the opposite
polarity -- a multiplier below 1 is not a wider band, it is a tighter one, and a reader who files
both classes under "needs more band" buys the wrong instrument.

What this face measures, on published records only (no draw stream, no band rebuild, no engine):

  * DISTANCE. For each below-floor row: how far under the floor it sits, in multiplier units and
    as a percentage of the floor, plus the factor the band must be contracted by.
  * YARDSTICKS. Two references already exist in the family and they are NOT interchangeable.
    E285 publishes a per-row ``distance_below_tight_lo_pct``: its implied reference is recovered
    here (flip / (1 - pct)) and published beside it, because that reference is row-local and can
    itself sit above 1.0 -- i.e. it is a widening instrument being used to measure a narrowing
    demand. The one common yardstick is the narrowing instrument BANDFLOOR actually publishes
    (the counterfactual 5 pct band's own band-edge multiplier).
  * REACH. A below-floor row is reached iff its flip is AT OR BELOW the narrowing cap (mirror of
    E287's D4, where a widening row is reached iff flip <= cap).
  * COST. The same instrument is then scored against ALL twelve rows on each row's own polarity,
    so the price of tightening is visible: an instrument tuned for one polarity gives up the rows
    that need the other.

DECISION RULE, declared before a number is read:

  M1 AXIS     only a band-edge multiplier is comparable to m_flip (b = edge * m); a relative
              tolerance in pct or a spread ratio is off-axis and is never compared.
  M2 POLARITY flip < floor is a NARROWING requirement; it is reached iff flip >= cap, and the
              shortfall is cap / flip (> 1 = the band is still too wide by that factor).
  M3 YARDSTICK the common yardstick is the published narrowing instrument; E285's per-row
              reference is published with its implied value and is never ranked against another
              row's, because it is row-local.
  M4 COST     every row is scored against the narrowing instrument on its own polarity; the cost
              of tightening is the count of rows the instrument does not reach.
  M5 SINGLE   "one instrument serves both polarities" is a claim that must be counted, not
              assumed: the face publishes the two demand sets and whether any single published
              multiplier reaches a row in both.
  M6 NOBILL   published faces are re-read; nothing is drawn, rebuilt or re-burned.

Verdict vocabulary (frozen):
  published_narrowing_instrument_reaches_every_below_floor_row
  published_narrowing_instrument_reaches_its_nearest_below_floor_row
  no_published_narrowing_instrument_reaches_a_below_floor_row

Usage:  python scripts/e288_below_floor_narrowing.py run|verify|selftest
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e272_flip_budget_two_tails as e272  # noqa: E402  (ROOT / OUTDIR)
import e287_supply_ceiling_axes as e287     # noqa: E402  (signed supply census + reach rule)

ROOT = e272.ROOT
OUTDIR = e272.OUTDIR

STUDY = "E288_below_floor_narrowing"
TITLE = ("a flip below the published floor needs the band NARROWED, not widened -- how far below "
         "the floor does each sit, does a narrowing instrument exist, and what does tightening "
         "cost in rows it would give up?")
CUTOFF = "2026-10-29"
SRC_GAPCEIL = e287.SRC_GAPCEIL      # E285: the 12-row partition + per-row distance column
SRC_FLOOR = e287.SRC_FLOOR          # BANDFLOOR: the published narrowing instrument
FACE = "BANDFLOORMIRROR-%s.json" % CUTOFF
LATEST = "bandfloormirror_latest.json"
SELF_FACES = (FACE, LATEST)

TOL = 1e-12
EDGE_AXIS = e287.EDGE_AXIS
FLOOR = 1.0

VERDICT_VOCAB = (
    "published_narrowing_instrument_reaches_every_below_floor_row",
    "published_narrowing_instrument_reaches_its_nearest_below_floor_row",
    "no_published_narrowing_instrument_reaches_a_below_floor_row",
)

NO_BILL = ("measurement only: published faces are re-read and their band-edge multipliers "
           "compared on one axis. No shuffle stream is drawn, no band rebuilt, no engine runs. A "
           "verdict is a statement about what the family has already published, not about what a "
           "tighter percentile band would eventually buy.")


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


# ------------------------------------------------------------------ rows
def all_rows(face):
    """Every flip the source face censused, read off its arms (not only the unreached classes)."""
    out = []
    for arm in (face.get("arms") or []):
        for rec in (arm.get("rows") or []):
            flip = _num(rec.get("flip"))
            if flip is None:
                continue
            out.append({"row_key": rec.get("row_key"), "arm": arm.get("arm"),
                        "cell": rec.get("cell"), "index": rec.get("index"),
                        "flip": flip, "class": rec.get("class"),
                        "distance_below_tight_lo_pct": _num(rec.get("distance_below_tight_lo_pct"))})
    return out


def class_of(flip, ceiling, floor):
    """Polarity, re-derived from the flip and the two published bounds (identity check).

    Only the three POLARITY classes are re-derived: the source face further splits the middle band
    into in_gap / reachable_tight / reachable_wide, which depends on the published intervals and is
    not a restatement of the flip alone.
    """
    if flip < floor - TOL:
        return "below_floor"
    if flip > ceiling + TOL:
        return "above_ceiling"
    return "in_interval"


COLLAPSE = {"below_floor": "below_floor", "above_ceiling": "above_ceiling"}


def mirror_rows(rows, cap):
    """M2: the below-floor rows, measured under the floor and against the narrowing cap."""
    out = []
    for rec in rows:
        if rec["class"] != "below_floor":
            continue
        flip = rec["flip"]
        pct = rec.get("distance_below_tight_lo_pct")
        implied = None
        if pct is not None and abs(1.0 - pct / 100.0) > TOL:
            implied = flip / (1.0 - pct / 100.0)
        entry = {
            "row_key": rec["row_key"], "cell": rec["cell"], "flip": flip,
            "floor": FLOOR,
            "distance_below_floor": round(FLOOR - flip, 12),
            "distance_below_floor_pct": round((FLOOR - flip) / FLOOR * 100.0, 6),
            "contraction_factor_required": round(FLOOR / flip, 12) if flip else None,
            "e285_distance_below_tight_lo_pct": pct,
            "e285_reference_implied": (None if implied is None else round(implied, 12)),
            "e285_reference_is_above_floor": (None if implied is None else implied > FLOOR + TOL),
            "common_yardstick": None,
        }
        if cap is not None:
            reached = flip >= cap - TOL
            entry["common_yardstick"] = {
                "cap": cap, "reached": bool(reached),
                "shortfall_factor": None if reached or not flip else cap / flip,
                "pct_short": None if reached or not flip else (cap / flip - 1.0) * 100.0,
            }
        out.append(entry)
    return sorted(out, key=lambda r: r["flip"])


def cost_block(rows, cap, ceiling):
    """M4: the same instrument scored against every row on that row's own polarity."""
    per_class, reached_keys = {}, []
    for rec in rows:
        cls = rec["class"]
        blk = per_class.setdefault(cls, {"n_rows": 0, "n_reached": 0})
        blk["n_rows"] += 1
        got = None
        if cap is not None:
            # M4: a row is scored on ITS OWN polarity -- a widening row needs cap >= flip, a
            # narrowing row needs cap <= flip
            if rec["flip"] > FLOOR + TOL:
                got = rec["flip"] <= cap + TOL
            elif rec["flip"] < FLOOR - TOL:
                got = rec["flip"] >= cap - TOL
            else:
                got = abs(rec["flip"] - cap) <= TOL
        if got:
            blk["n_reached"] += 1
            reached_keys.append(rec["row_key"])
    n_rows = len(rows)
    n_reached = sum(b["n_reached"] for b in per_class.values())
    return {
        "rows_censused": n_rows,
        "rows_reached_by_the_narrowing_instrument": n_reached,
        "reached_row_keys": reached_keys,
        "by_class": per_class,
        "share_reached": (None if not n_rows else round(n_reached / float(n_rows), 6)),
        "widening_rows_given_up": sum(v.get("n_rows", 0) for k, v in per_class.items()
                                      if k != "below_floor"),
        "statement": ("a single published multiplier is scored against all %d rows; at the "
                      "published narrowing cap it reaches %d" % (n_rows, n_reached)),
    }


def polarity_block(rows, caps):
    """M5: the two demand sets, and whether any single published multiplier reaches both."""
    widen = [r["flip"] for r in rows if r["flip"] > FLOOR + TOL]
    narrow = [r["flip"] for r in rows if r["flip"] < FLOOR - TOL]
    wcap = ((caps.get("widen") or {}).get("optimistic") or {}).get("cap")
    ncap = ((caps.get("narrow") or {}).get("optimistic") or {}).get("cap")
    both = None
    if wcap is not None and ncap is not None:
        # one multiplier cannot be at once >= every widening demand and <= every narrowing one
        both = bool(min(widen or [None]) is not None and ncap >= max(narrow) and
                    wcap <= min(widen))
    return {
        "n_widening_demands": len(widen),
        "n_narrowing_demands": len(narrow),
        "widening_demand_range": [min(widen), max(widen)] if widen else [],
        "narrowing_demand_range": [min(narrow), max(narrow)] if narrow else [],
        "widening_cap_optimistic": wcap,
        "narrowing_cap_optimistic": ncap,
        "one_instrument_serves_both_polarities": both,
        "gap_between_the_caps": (None if (wcap is None or ncap is None)
                                 else round(wcap - ncap, 12)),
        "statement": ("a widening row needs a multiplier at or above its flip and a narrowing row "
                      "one at or below its flip; the family publishes %d widening and %d "
                      "narrowing demand(s), so 'unreachable' is always a statement about one "
                      "polarity" % (len(widen), len(narrow))),
    }


def decide(mirror, cost):
    if not mirror:
        return "no_published_narrowing_instrument_reaches_a_below_floor_row"
    reached = [r for r in mirror if (r.get("common_yardstick") or {}).get("reached")]
    if len(reached) == len(mirror):
        return "published_narrowing_instrument_reaches_every_below_floor_row"
    if reached:
        return "published_narrowing_instrument_reaches_its_nearest_below_floor_row"
    return "no_published_narrowing_instrument_reaches_a_below_floor_row"


# ------------------------------------------------------------------ build
def build(outdir=None):
    outdir = outdir or OUTDIR
    gap = load(SRC_GAPCEIL, outdir)
    src_summary = gap.get("summary") or {}
    ceiling = _num(src_summary.get("published_ceiling"))
    floor = _num(src_summary.get("published_floor"))
    floor = FLOOR if floor is None else floor

    readings = e287.supply_readings(outdir)
    caps = e287.supply_caps(readings)
    narrow_readings = [r for r in readings
                       if r["direction"] == "narrow" and r["usable_as_supply"]]
    cap = ((caps.get("narrow") or {}).get("optimistic") or {}).get("cap")

    rows = all_rows(gap)
    mirror = mirror_rows(rows, cap)
    cost = cost_block(rows, cap, ceiling)
    polarity = polarity_block(rows, caps)

    # partition identity: the class is a restatement of flip vs the two published bounds
    rederived = {r["row_key"]: class_of(r["flip"], ceiling, floor) for r in rows}
    collapsed = {r["row_key"]: COLLAPSE.get(r["class"], "in_interval") for r in rows}
    identity = {
        "rows_censused": len(rows),
        "classes_published": sorted({r["class"] for r in rows}),
        "n_class_from_bounds_matches_published": sum(
            1 for r in rows if collapsed[r["row_key"]] == rederived[r["row_key"]]),
        "below_floor_rows_published": sorted(src_summary.get("below_floor_rows") or []),
        "below_floor_rows_rederived": sorted(k for k, v in rederived.items()
                                             if v == "below_floor"),
        "partition_sums_to_rows": (sum(1 for r in rows if r["class"] == "below_floor")
                                   == len(src_summary.get("below_floor_rows") or [])),
        "n_below_floor": len(mirror),
        "n_rows_by_class": {c: sum(1 for r in rows if r["class"] == c)
                            for c in sorted({r["class"] for r in rows})},
    }
    identity["below_floor_set_matches"] = bool(
        identity["below_floor_rows_published"] == identity["below_floor_rows_rederived"])

    # the published narrowing instrument, quoted from its own face (not re-derived here)
    cf = (load(SRC_FLOOR, outdir).get("counterfactual_percentile_band") or {})
    instrument = {
        "face": SRC_FLOOR,
        "multiplier": _num(cf.get("multiplier")),
        "band_pct": cf.get("band_pct"),
        "lo_base": _num(cf.get("lo_base")),
        "lo_top": _num(cf.get("lo_top")),
        "is_below_floor": (None if cf.get("multiplier") is None
                           else _num(cf.get("multiplier")) < FLOOR),
        "n_narrowing_readings_published": len(narrow_readings),
        "readings_at_or_below_floor": [r["cap"] for r in narrow_readings
                                       if r["cap"] is not None and r["cap"] < FLOOR],
        "note": ("the only sub-1.0 band-edge multiplier the family publishes is this "
                 "counterfactual band; every other 'narrow' reading in E287's census is a "
                 "per-seed minimum of a WIDENING ratio and sits above 1.0"),
    }

    nearest = None
    cand = [r for r in mirror if (r.get("common_yardstick") or {}).get("shortfall_factor")]
    if cand:
        best = min(cand, key=lambda r: r["common_yardstick"]["shortfall_factor"])
        nearest = {"row_key": best["row_key"], "flip": best["flip"],
                   "shortfall_factor": best["common_yardstick"]["shortfall_factor"],
                   "pct_short": best["common_yardstick"]["pct_short"]}
    farthest = None
    if cand:
        worst = max(cand, key=lambda r: r["common_yardstick"]["shortfall_factor"])
        farthest = {"row_key": worst["row_key"], "flip": worst["flip"],
                    "shortfall_factor": worst["common_yardstick"]["shortfall_factor"],
                    "pct_short": worst["common_yardstick"]["pct_short"]}

    verdict = decide(mirror, cost)
    summary = {
        "floor": floor,
        "ceiling": ceiling,
        "n_below_floor_rows": len(mirror),
        "narrowing_cap": cap,
        "narrowing_cap_at": (caps.get("narrow") or {}).get("optimistic", {}).get("at"),
        "n_narrowing_readings": len(narrow_readings),
        "n_sub_floor_readings": len(instrument["readings_at_or_below_floor"]),
        "n_reached_conservative": sum(1 for r in mirror
                                      if (r.get("common_yardstick") or {}).get("reached")),
        "deepest_below_floor": mirror[0]["row_key"] if mirror else None,
        "nearest_below_floor": nearest,
        "farthest_below_floor": farthest,
        "cost": cost,
        "polarity": polarity,
        "n_e285_rows_whose_reference_is_above_floor": sum(
            1 for r in mirror if r.get("e285_reference_is_above_floor")),
        "verdict": verdict,
    }

    return {
        "study": STUDY, "title": TITLE, "evidence_cutoff": CUTOFF, "generated": None,
        "no_bill": NO_BILL,
        "source_faces": [SRC_GAPCEIL, SRC_FLOOR],
        "frozen_spec": {
            "M1_axis": "only a band-edge multiplier is comparable to m_flip (b = edge * m); a "
                       "relative tolerance in pct or a spread ratio is off-axis",
            "M2_polarity": "flip < floor is a NARROWING requirement, reached iff flip >= cap; "
                           "shortfall = cap / flip",
            "M3_yardstick": "the common yardstick is the published narrowing instrument; E285's "
                            "per-row reference is published with its implied value and never "
                            "ranked against another row's",
            "M4_cost": "every row is scored against the narrowing instrument on its own polarity; "
                       "the cost of tightening is the count of rows it does not reach",
            "M5_single": "'one instrument serves both polarities' is counted, not assumed",
            "M6_nobill": "published records only: no stream drawn, no band rebuilt, no engine run",
            "tolerance": TOL,
            "verdict_vocab": list(VERDICT_VOCAB),
        },
        "narrowing_instrument": instrument,
        "narrowing_readings": sorted(narrow_readings, key=lambda r: (r["face"], r["label"])),
        "mirror_rows": mirror,
        "partition_identity": identity,
        "cost": cost,
        "polarity": polarity,
        "summary": summary,
        "verdict": verdict,
        "verdict_reason": _reason(verdict, summary),
    }


def _reason(verdict, summary):
    near = summary.get("nearest_below_floor") or {}
    far = summary.get("farthest_below_floor") or {}
    cost = summary.get("cost") or {}
    base = ("%d row(s) sit below the published floor %s; the tightest narrowing instrument the "
            "family publishes is %s" % (summary["n_below_floor_rows"], _fmt(summary["floor"]),
                                        _fmt(summary["narrowing_cap"])))
    if not near:
        return base + "; no below-floor row is gaugeable against a published instrument"
    short = ("the nearest (%s, flip %s) is %s pct short of it and the farthest (%s, flip %s) is "
             "%s pct short" % (near["row_key"], _fmt(near["flip"]), _fmt(near["pct_short"]),
                               far["row_key"], _fmt(far["flip"]), _fmt(far["pct_short"])))
    tail = ("; scored against all %d rows on their own polarity the same instrument reaches %d, so "
            "tightening is not free on the widening side either" %
            (cost.get("rows_censused"), cost.get("rows_reached_by_the_narrowing_instrument")))
    if verdict == "published_narrowing_instrument_reaches_every_below_floor_row":
        return base + "; it reaches every below-floor row" + tail
    if verdict == "published_narrowing_instrument_reaches_its_nearest_below_floor_row":
        return base + "; it reaches only the nearest one -- " + short + tail
    return base + "; it reaches none -- " + short + tail


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
    print("E288 %s" % face["verdict"])
    print("  floor=%s | narrowing cap=%s (%s readings, %d sub-1.0)"
          % (_fmt(s["floor"]), _fmt(s["narrowing_cap"]), s["n_narrowing_readings"],
             s["n_sub_floor_readings"]))
    for rec in face["mirror_rows"]:
        cy = rec.get("common_yardstick") or {}
        print("  %-14s flip=%s below floor %s pct | short %s pct | e285 ref implied %s"
              % (rec["row_key"], _fmt(rec["flip"]), _fmt(rec["distance_below_floor_pct"]),
                 _fmt(cy.get("pct_short")), _fmt(rec.get("e285_reference_implied"))))
    c = face["cost"]
    print("  cost: reaches %d of %d rows (share %s)"
          % (c["rows_reached_by_the_narrowing_instrument"], c["rows_censused"],
             _fmt(c["share_reached"], 4)))
    print("  polarity: %d widening / %d narrowing demand(s), one instrument serves both=%s"
          % (face["polarity"]["n_widening_demands"], face["polarity"]["n_narrowing_demands"],
             face["polarity"]["one_instrument_serves_both_polarities"]))
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
    for key in ("floor", "n_below_floor_rows", "narrowing_cap", "n_reached_conservative",
                "nearest_below_floor", "farthest_below_floor"):
        if ss.get(key) != ls.get(key):
            problems.append("summary.%s does not re-derive" % key)
    if (ss.get("cost") or {}).get("rows_reached_by_the_narrowing_instrument") != \
            (ls.get("cost") or {}).get("rows_reached_by_the_narrowing_instrument"):
        problems.append("the cost block does not re-derive")
    idn = live["partition_identity"]
    if not idn["below_floor_set_matches"]:
        problems.append("the below-floor set is not the set E285 published")
    if idn["n_class_from_bounds_matches_published"] != idn["rows_censused"]:
        problems.append("a row's class does not re-derive from flip vs the published bounds")
    if not live["narrowing_instrument"]["is_below_floor"]:
        problems.append("the common yardstick is not a sub-1.0 multiplier")
    if stored.get("mirror_rows") != live["mirror_rows"]:
        problems.append("the mirror rows do not re-derive")
    print("E288 verify: %d problem(s)" % len(problems))
    for p in problems:
        print("  - %s" % p)
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
def cmd_selftest():
    ok, fail = 0, []

    def leg(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append("%s %s" % (name, detail))

    # L1 the class is a restatement of flip vs the published bounds
    leg("L1", class_of(0.9, 2.0, 1.0) == "below_floor"
        and class_of(1.0, 2.0, 1.0) == "in_interval"
        and class_of(2.1, 2.0, 1.0) == "above_ceiling")
    # L2 ... including exactly at each bound (inclusive on both sides)
    leg("L2", class_of(2.0, 2.0, 1.0) == "in_interval"
        and class_of(1.0 + 1e-12, 2.0, 1.0) == "in_interval")
    # L3 a below-floor row is reached when the flip is AT the cap (mirror polarity, inclusive)
    rows = [{"row_key": "r1", "cell": "c", "flip": 0.92, "class": "below_floor",
             "distance_below_tight_lo_pct": None}]
    got = mirror_rows(rows, 0.92)
    leg("L3", got[0]["common_yardstick"]["reached"] is True, got[0])
    # L4 one step above the cap is short, and the shortfall is cap / flip (the band is too WIDE)
    rows2 = [{"row_key": "r1", "cell": "c", "flip": 0.80, "class": "below_floor",
              "distance_below_tight_lo_pct": None}]
    got2 = mirror_rows(rows2, 0.92)[0]["common_yardstick"]
    leg("L4", got2["reached"] is False and abs(got2["shortfall_factor"] - 1.15) < 1e-12, got2)
    # L5 an unknown cap is unknown -- never "reached", never a fabricated factor
    got3 = mirror_rows(rows2, None)[0]
    leg("L5", got3["common_yardstick"] is None, got3)
    # L6 E285's per-row reference is recovered from its own percentage and is NOT assumed to be 1.0
    rows4 = [{"row_key": "r", "cell": "c", "flip": 0.889387, "class": "below_floor",
              "distance_below_tight_lo_pct": 13.505487}]
    e = mirror_rows(rows4, 1.0)[0]
    leg("L6", abs(e["e285_reference_implied"] - 0.889387 / (1.0 - 0.13505487)) < 1e-12
        and e["e285_reference_is_above_floor"] is True, e["e285_reference_implied"])
    # L7 a reference that IS the floor is reported as such, not as above it
    rows5 = [{"row_key": "r", "cell": "c", "flip": 0.9, "class": "below_floor",
              "distance_below_tight_lo_pct": 10.0}]
    leg("L7", mirror_rows(rows5, 1.0)[0]["e285_reference_is_above_floor"] is False)
    # L8 cost counts a widening row as reached by the WIDENING rule, not by the narrow one
    mix = [{"row_key": "w", "cell": "c", "flip": 2.0, "class": "above_ceiling"},
           {"row_key": "b", "cell": "c", "flip": 0.90, "class": "below_floor"}]
    c = cost_block(mix, 0.922, 2.3)
    leg("L8", c["rows_reached_by_the_narrowing_instrument"] == 0
        and c["by_class"]["above_ceiling"]["n_reached"] == 0, c)
    # L9 a widening row below the cap WOULD be reached -- the rule is not "narrow lost nothing"
    mix2 = [{"row_key": "w", "cell": "c", "flip": 1.5, "class": "in_gap"}]
    c2 = cost_block(mix2, 1.9, 2.3)
    leg("L9", c2["rows_reached_by_the_narrowing_instrument"] == 1, c2)
    # L10 the cost block's share is a share of the rows censused, and an empty census is None
    leg("L10", abs(c2["share_reached"] - 1.0) < 1e-12 and cost_block([], 0.9, 2.0)["share_reached"]
        is None)
    # L11 two polarities are never certified as served by one instrument when the demands cross
    caps = {"widen": {"optimistic": {"cap": 2.2}}, "narrow": {"optimistic": {"cap": 0.92}}}
    blk = polarity_block([{"row_key": "w", "flip": 1.5}, {"row_key": "b", "flip": 0.89}], caps)
    leg("L11", blk["one_instrument_serves_both_polarities"] is False
        and abs(blk["gap_between_the_caps"] - 1.28) < 1e-12, blk)
    # L12 a row reached at the cap is "nearest", an empty class is not a verdict of success
    leg("L12", decide([], cost_block([], 1.0, 2.0))
        == "no_published_narrowing_instrument_reaches_a_below_floor_row")
    # L13 the verdict ladder: all reached / some reached / none reached
    leg("L13", decide([{"common_yardstick": {"reached": True}},
                       {"common_yardstick": {"reached": True}}], {})
        == "published_narrowing_instrument_reaches_every_below_floor_row")
    leg("L14", decide([{"common_yardstick": {"reached": True}},
                       {"common_yardstick": {"reached": False}}], {})
        == "published_narrowing_instrument_reaches_its_nearest_below_floor_row")
    leg("L15", decide([{"common_yardstick": {"reached": False}}], {})
        == "no_published_narrowing_instrument_reaches_a_below_floor_row")
    # L16 on the real face: the below-floor set is E285's own set and every class re-derives
    live = build()
    idn = live["partition_identity"]
    leg("L16", idn["below_floor_set_matches"] and
        idn["n_class_from_bounds_matches_published"] == idn["rows_censused"], idn)
    # L17 on the real face: the common yardstick is sub-1.0 and the cost block covers all rows
    leg("L17", live["narrowing_instrument"]["is_below_floor"] is True
        and live["cost"]["rows_censused"] == idn["rows_censused"], live["cost"])
    # L18 on the real face: every mirror row carries a yardstick reading (no silent blanks)
    leg("L18", all(r.get("common_yardstick") is not None for r in live["mirror_rows"])
        and len(live["mirror_rows"]) == live["summary"]["n_below_floor_rows"],
        live["summary"]["n_below_floor_rows"])
    # L19 on the real face: the reason sentence names the polarity of every number it quotes
    reason = live["verdict_reason"]
    leg("L19", "below" in reason and "reaches" in reason and "pct short" in reason, reason[:80])

    print("E288 selftest: %d/%d" % (ok, ok + len(fail)))
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