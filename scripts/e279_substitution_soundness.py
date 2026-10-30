"""E279 -- when one tail cannot be read, is reading the OTHER tail sound?

E278 published a minimum-spread policy: a group whose tail spread is exactly 0 is flagged and its
rows stay unmeasured, with "read the other tail" as the substitution. That substitution has never
been tested. Every measured row publishes a reading at each tail, so each row can be asked whether
the two tails agree on the instruction a reader needs.

DECISION RULE, declared before any number is read (E188 / r1319 discipline -- the rule is frozen
here and re-emitted into the face so the face cannot be read against a rule it did not declare):

  D1  DIRECTION IS A ROW PROPERTY. flip_direction and flip_multiplier are fields of the row, not of
      a tail. No substitution can therefore contradict the direction -- if a face claimed it could,
      the face would be reading its own copy instead of the row. This is a structural identity and
      is published as such, not as evidence.
  D2  THE CONCLUSION IS "reachable": the row's flip_multiplier lies inside that tail's published
      multiplier range [multiplier_min, multiplier_max] for the row's (leg, base) group. Re-derived
      here from the published ranges; never copied from E272's boolean.
  D3  STRANDED = the tail publishes spread_pct == 0 AND its multiplier range is degenerate
      (min == max) AND the group has more than one cell. A degenerate range means the tail cannot
      express any movement at all, so it cannot state an instruction.
  D4  SOUND(substitute) = the substitute is measurable (spread > 0 and a normalised gap exists) AND
      it does not deflate the conclusion (substitute.reachable >= stranded.reachable). Deflation is
      the only possible contradiction; inflation is a scope problem, not a contradiction.
  D5  VACUOUS AGREEMENT = the stranded tail agreed because it was mechanically unable to disagree
      (degenerate range, reachable False by construction). Such a row is reported as vacuity and is
      NOT counted as evidence that the substitution is sound.
  D6  FIXED POINT: the face must not claim a calibrated substitution threshold off two rows. The
      scope bracket is an interval with calibrated=False unless the data supports more.

Usage:  python scripts/e279_substitution_soundness.py run|verify|selftest
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e278_spread_floor as e278  # noqa: E402  (OUTDIR / TOL / LEGS / BASE_COUNTS / load)
import e262_p95_transfer_across_windows as e262  # noqa: E402

ROOT = e262.ROOT
OUTDIR = e262.OUTDIR
TOL = e262.TOL
LEGS = e262.LEGS
BASE_COUNTS = e262.BASE_COUNTS

STUDY = "E279_substitution_soundness"
TITLE = ("when one tail cannot be read, is reading the OTHER tail sound -- or does the substitute "
         "ever contradict the instruction?")
CUTOFF = "2026-10-29"
SRC_BUDGET = "BANDFLIPBUDGET-%s.json" % CUTOFF   # E272: per-row, per-tail budget
SRC_FLOOR = "BANDSPREADFLOOR-%s.json" % CUTOFF   # E278: which groups publish a zero spread
FACE = "BANDSUBSTITUTE-%s.json" % CUTOFF
LATEST = "bandsubstitute_latest.json"
SELF_FACES = (FACE, LATEST)

TAILS = ("tight", "wide")
OTHER = {"tight": "wide", "wide": "tight"}
SPREAD_TOL = TOL * 100.0                          # spread_pct is in percent, same as E272/E278

VERDICT_VOCAB = (
    "the_substitute_agrees_only_where_agreement_is_vacuous",
    "the_substitute_contradicts_on_a_row_that_needs_it",
    "the_substitute_moves_the_claim_where_the_pair_disagrees",
    "the_substitute_agrees_where_it_fires",
    "no_stranded_tails_published",
)

NO_BILL = ("measurement only: E272's published per-row tail budget and E278's published zero-spread "
           "census are re-read. No draw stream is drawn, no band rebuilt, no engine runs. A verdict "
           "here is a statement about the published numbers, not about the market.")


# ------------------------------------------------------------------ io
def load(name):
    with io.open(os.path.join(OUTDIR, name), encoding="utf-8") as fh:
        return json.load(fh)


def rows_from(budget):
    """Every published row from every tail_budget block, in a stable order."""
    out = []
    for _key, blk in sorted(((budget.get("tail_budget") or {})).items()):
        for row in (blk or {}).get("rows") or []:
            out.append(row)
    out.sort(key=lambda r: (str(r.get("leg")), str(r.get("base")), r.get("index")))
    return out


# ------------------------------------------------------------------ per-tail reading
def tail_rec(row, tail):
    t = row.get(tail) or {}
    return {"tail": tail,
            "spread_pct": t.get("spread_pct"),
            "normalised_gap": t.get("normalised_gap"),
            "multiplier_min": t.get("multiplier_min"),
            "multiplier_max": t.get("multiplier_max"),
            "published_reachable": t.get("reachable"),
            "published_reachable_strict": t.get("reachable_strict"),
            "n_cells": t.get("n_cells"),
            "gap_pct": t.get("gap_pct")}


def reachable_of(tr, flip):
    """D2: the flip multiplier inside the tail's published range, both ends inclusive."""
    lo, hi = tr.get("multiplier_min"), tr.get("multiplier_max")
    if flip is None or lo is None or hi is None:
        return None
    return bool((float(lo) - TOL) <= float(flip) <= (float(hi) + TOL))


def reachable_strict_of(tr, flip):
    lo, hi = tr.get("multiplier_min"), tr.get("multiplier_max")
    if flip is None or lo is None or hi is None:
        return None
    return bool((float(lo) + TOL) < float(flip) < (float(hi) - TOL))


def range_degenerate(tr):
    lo, hi = tr.get("multiplier_min"), tr.get("multiplier_max")
    if lo is None or hi is None:
        return False
    return abs(float(hi) - float(lo)) <= TOL


def is_stranded(tr):
    """D3: spread exactly 0, a degenerate multiplier range, and more than one cell."""
    sp = tr.get("spread_pct")
    if sp is None:
        return False
    return (abs(float(sp)) <= SPREAD_TOL and range_degenerate(tr)
            and (tr.get("n_cells") or 0) > 1)


def is_measurable(tr):
    sp = tr.get("spread_pct")
    ng = tr.get("normalised_gap")
    if sp is None or ng is None:
        return False
    return abs(float(sp)) > SPREAD_TOL


# ------------------------------------------------------------------ substitution
def substitution_record(row, from_tail, rea):
    """One substitution event: the from_tail is stranded, the other tail is the substitute."""
    to_tail = OTHER[from_tail]
    f, t = rea[from_tail], rea[to_tail]
    if f is None or t is None:
        return None
    vacuous = bool(f is False and range_degenerate(row["_tail"][from_tail]))
    return {
        "row": row.get("row"),
        "index": row.get("index"),
        "cell": row.get("cell"),
        "leg": row.get("leg"),
        "base": row.get("base"),
        "direction": row.get("flip_direction"),
        "flip_multiplier": row.get("flip_multiplier"),
        "from_tail": from_tail,
        "to_tail": to_tail,
        "reachable_from": f,
        "reachable_to": t,
        "verdict_agrees": bool(f == t),
        # D4: only a deflation is a contradiction
        "deflating": bool(t is False and f is True),
        "inflating": bool(t is True and f is False),
        # D5: agreement the stranded tail could not have avoided
        "vacuous": vacuous,
        "substitute_measurable": is_measurable(row["_tail"][to_tail]),
        "substitute_normalised_gap": row["_tail"][to_tail].get("normalised_gap"),
        "stranded_raw_gap_pct": row["_tail"][from_tail].get("gap_pct"),
        "stranded_range_degenerate": range_degenerate(row["_tail"][from_tail]),
    }


def swap_pair(row, rea):
    """Diagnostic, not an event: what would change if a reader used the other tail regardless."""
    out = {}
    key = "%s|%s|%s" % (row.get("row"), row.get("cell"), row.get("index"))
    for from_tail in TAILS:
        to_tail = OTHER[from_tail]
        f, t = rea[from_tail], rea[to_tail]
        out[from_tail] = {
            "row_key": key,
            "from": from_tail, "to": to_tail, "reachable_from": f, "reachable_to": t,
            "agrees": bool(f == t) if (f is not None and t is not None) else None,
            "deflates": bool(t is False and f is True),
            "inflates": bool(t is True and f is False),
        }
    return out


def census(rows):
    """One record per measured row: both tails, re-derived reachability, events and the swap view."""
    out = []
    for row in rows:
        flip = row.get("flip_multiplier")
        rec = {"row": row.get("row"), "index": row.get("index"), "cell": row.get("cell"),
               "leg": row.get("leg"), "base": row.get("base"),
               "flip_direction": row.get("flip_direction"), "flip_multiplier": flip,
               "_tail": {t: tail_rec(row, t) for t in TAILS}}
        rea = {t: reachable_of(rec["_tail"][t], flip) for t in TAILS}
        rec["reachable"] = rea
        rec["reachable_strict"] = {t: reachable_strict_of(rec["_tail"][t], flip) for t in TAILS}
        rec["published"] = {t: rec["_tail"][t].get("published_reachable") for t in TAILS}
        rec["published_agrees"] = {t: (rea[t] == rec["published"][t]) for t in TAILS}
        rec["spread_pct"] = {t: rec["_tail"][t].get("spread_pct") for t in TAILS}
        rec["normalised_gap"] = {t: rec["_tail"][t].get("normalised_gap") for t in TAILS}
        rec["stranded_tails"] = [t for t in TAILS if is_stranded(rec["_tail"][t])]
        rec["usable_tails"] = [t for t in TAILS if is_measurable(rec["_tail"][t])]
        rec["swap"] = swap_pair(rec, rea)
        attempts = []
        for t in rec["stranded_tails"]:
            ev = substitution_record(rec, t, rea)
            if ev is not None:
                attempts.append(ev)
        # a stranded tail whose substitute is ALSO stranded cannot be substituted: E278's rule is
        # that such a row stays unmeasured. The attempt is kept as disclosure, never as an event.
        rec["substitution_attempts"] = attempts
        rec["substitutions"] = [e for e in attempts if e["substitute_measurable"]]
        rec["substitution_blocked"] = [e for e in attempts if not e["substitute_measurable"]]
        rec["substitution_available"] = bool(rec["substitutions"])
        rec["_tail"] = rec["_tail"]  # kept for the event builder; stripped in publish()
        out.append({k: v for k, v in rec.items() if k != "_tail"})
        # the event builder needs the tail records; re-attach them privately for the caller
        out[-1]["_tail_private"] = rec["_tail"]
    return out


def _clean(rec):
    return {k: v for k, v in rec.items() if not k.startswith("_")}


def censused(rows):
    """census() but with the private tail records dropped from the published shape."""
    return [_clean(r) for r in census(rows)]


# ------------------------------------------------------------------ identity
def identity_check(cen, floor_face):
    """Two identities: our reachability re-derives E272's booleans, and our stranded set is E278's."""
    mismatched, checked, notes = [], 0, []
    for rec in cen:
        for t in TAILS:
            pub = rec["published"][t]
            mine = rec["reachable"][t]
            if pub is None and mine is None:
                continue
            checked += 1
            if pub != mine:
                mismatched.append({"row": rec["row"], "cell": rec["cell"], "leg": rec["leg"],
                                   "base": rec["base"], "tail": t, "published": pub, "mine": mine})
    flagged = sorted({f.get("group") for f in
                      ((floor_face.get("minimum_spread_policy") or {}).get("flagged") or [])})
    mine_groups = sorted({"%s:%d" % (rec["leg"], int(rec["base"]))
                          for rec in cen for _t in rec["stranded_tails"]})
    if flagged != mine_groups:
        notes.append("E278 flags %s, this study finds stranding on %s" % (flagged, mine_groups))
    return {"checked": checked, "mismatched": mismatched,
            "stranded_groups_here": mine_groups,
            "stranded_groups_per_e278": flagged,
            "stranding_agrees_with_e278": bool(flagged == mine_groups),
            "notes": notes}


# ------------------------------------------------------------------ summary
def summary_of(cen, budget, floor_face):
    events = [e for rec in cen for e in rec["substitutions"]]
    deflations = [e for e in events if e["deflating"]]
    inflations = [e for e in events if e["inflating"]]
    vacuous = [e for e in events if e["vacuous"] and e["verdict_agrees"]]
    non_vacuous_agree = [e for e in events if e["verdict_agrees"] and not e["vacuous"]]

    swap = [rec["swap"][t] for rec in cen for t in TAILS]
    swap_inflate = [s for s in swap if s["inflates"]]
    swap_deflate = [s for s in swap if s["deflates"]]
    swap_disagree_rows = sorted({rec["row"] for rec in cen if rec["swap"]["tight"]["agrees"] is False})

    # D1: the direction fields are row properties -- count what the rows actually say
    dirs = {}
    for rec in cen:
        dirs[rec["flip_direction"]] = dirs.get(rec["flip_direction"], 0) + 1

    # the wide tail weakly dominates the tight tail on this population (E272's finding, re-derived)
    dominance_violations = [rec["row"] for rec in cen
                            if rec["reachable"]["wide"] is not None
                            and rec["reachable"]["tight"] is not None
                            and bool(rec["reachable"]["wide"]) < bool(rec["reachable"]["tight"])]

    measured = len(cen)
    reported_rows = (budget.get("summary") or {}).get("rows")
    reported_measured = (budget.get("summary") or {}).get("rows_measured")

    # the substitute's normalised gap on the rows where a substitution actually fires
    event_gaps = [e["substitute_normalised_gap"] for e in events
                  if e.get("substitute_normalised_gap") is not None]
    # the dominant tail's normalised gap on rows where the two tails disagree about reachability
    disagree_gaps = []
    for rec in cen:
        if rec["swap"]["tight"]["agrees"] is False:
            g = rec["normalised_gap"]["wide"]
            if g is not None:
                disagree_gaps.append(g)

    s = {
        "rows_published": reported_rows if reported_rows is not None else len(cen),
        "rows_measured": measured,
        "rows_without_flip": (reported_rows - measured) if reported_rows is not None else None,
        "rows_measured_per_e272": reported_measured,
        "n_groups": len({"%s:%d" % (r["leg"], int(r["base"])) for r in cen}),
        "directions": dirs,
        "rows_with_stranded_tail": sum(1 for r in cen if r["stranded_tails"]),
        "rows_where_substitution_fires": sum(1 for r in cen if r["substitutions"]),
        "rows_where_substitution_fires": sum(1 for r in cen if r["substitutions"]),
        "rows_with_blocked_substitution": sum(1 for r in cen if r["substitution_blocked"]),
        "blocked_substitution_attempts": sum(len(r["substitution_blocked"]) for r in cen),
        "substitution_events": len(events),
        "events_with_deflation": len(deflations),
        "events_with_inflation": len(inflations),
        "events_vacuous_agreement": len(vacuous),
        "events_non_vacuous_agreement": len(non_vacuous_agree),
        "events_substitute_measurable": sum(1 for e in events if e["substitute_measurable"]),
        "swap_inflations_tight_to_wide": len([s2 for s2 in swap_inflate if s2["from"] == "tight"]),
        "swap_deflations_wide_to_tight": len([s2 for s2 in swap_deflate if s2["from"] == "wide"]),
        "swap_inflation_rows": sorted({s2.get("row_key") for s2 in swap_inflate
                                       if s2["from"] == "tight"}),
        "swap_deflation_rows": sorted({s2.get("row_key") for s2 in swap_deflate
                                       if s2["from"] == "wide"}),
        "swap_rows_match": (sorted({s2.get("row_key") for s2 in swap_inflate if s2["from"] == "tight"})
                            == sorted({s2.get("row_key") for s2 in swap_deflate
                                       if s2["from"] == "wide"})),
        "rows_where_tails_disagree_on_reachability": swap_disagree_rows,
        "wide_dominates_tight_violations": dominance_violations,
        "substitute_normalised_gaps_on_events": sorted(event_gaps),
        "dominant_tail_gaps_where_tails_disagree": sorted(disagree_gaps),
        "identity_mismatched": len(identity_check(cen, floor_face)["mismatched"]),
        "stranding_agrees_with_e278": identity_check(cen, floor_face)["stranding_agrees_with_e278"],
    }
    s["scope_bracket"] = scope_bracket(s)
    s["verdict"] = verdict_of(s)
    return s


def scope_bracket(s):
    """D6: an interval, not a calibrated threshold -- and it says so on its face."""
    gaps_agree = s.get("substitute_normalised_gaps_on_events") or []
    gaps_disagree = s.get("dominant_tail_gaps_where_tails_disagree") or []
    lo = max(gaps_disagree) if gaps_disagree else None      # disagreement observed at or below this
    hi = min(gaps_agree) if gaps_agree else None            # agreement observed at or above this
    calibrated = False
    note = ("n=%d substitution event(s) and n=%d disagreeing row(s): this brackets where the "
            "substitute was observed to agree, it does not calibrate a threshold."
            % (len(gaps_agree), len(gaps_disagree)))
    if lo is not None and hi is not None and hi < lo:
        note += (" The observed agreement gap is BELOW the disagreement gap, so no single threshold "
                 "separates them on this population.")
    return {
        "rule": ("substitute only when the other tail's normalised gap exceeds X, where X must sit "
                 "strictly above the disagreement band and at or below the agreement band"),
        "must_exceed_observed": lo,
        "may_go_as_high_as": hi,
        "separated": (None if lo is None or hi is None else bool(hi >= lo)),
        "calibrated": calibrated,
        "note": note,
    }


def verdict_of(s):
    if not s["substitution_events"]:
        return "no_stranded_tails_published"
    if s["events_with_deflation"]:
        return "the_substitute_contradicts_on_a_row_that_needs_it"
    if s["events_vacuous_agreement"] == s["substitution_events"]:
        return "the_substitute_agrees_only_where_agreement_is_vacuous"
    if s["swap_inflations_tight_to_wide"] or s["swap_deflations_wide_to_tight"]:
        return "the_substitute_moves_the_claim_where_the_pair_disagrees"
    return "the_substitute_agrees_where_it_fires"


def reason_of(s):
    if s["verdict"] == "the_substitute_agrees_only_where_agreement_is_vacuous":
        return ("all %d substitution event(s) agree, and every one of them agrees vacuously: the "
                "stranded tail publishes a degenerate multiplier range (min == max), so it is "
                "mechanically unable to reach anything and its 'unreachable' is not a reading the "
                "substitute could have contradicted. The substitute reads the row as %s spreads "
                "away. Where the two tails genuinely differ (%d row(s): %s) the tail you read "
                "decides the answer, and the swap view shows it on exactly the same %d row(s) in "
                "both directions (a reversal, not two independent events): reading tight then "
                "substituting wide ADDS the claim on %d of %d measured rows, and the reverse "
                "substitution REMOVES it on the same rows. So the relation is monotone, not "
                "neutral -- substitution is sound as an UPPER BOUND (it can only add a 'can move') "
                "and unproven as a reading (it never establishes that a row cannot move). The %d "
                "row(s) that actually needed it carry no evidence, so the E278 policy should be "
                "scoped to 'substitute only to prove a row CAN move, never to conclude it cannot'."
                % (s["substitution_events"],
                   "/".join("%.2f" % g for g in (s.get("substitute_normalised_gaps_on_events") or [])),
                   len(s["rows_where_tails_disagree_on_reachability"]),
                   ",".join(str(x) for x in s["rows_where_tails_disagree_on_reachability"]),
                   max(s["swap_inflations_tight_to_wide"], s["swap_deflations_wide_to_tight"]),
                   s["swap_inflations_tight_to_wide"], s["rows_measured"],
                   s["rows_with_stranded_tail"]))
    if s["verdict"] == "no_stranded_tails_published":
        return "no published row carries a stranded tail; the substitution rule has nothing to fire on."
    if s["verdict"] == "the_substitute_contradicts_on_a_row_that_needs_it":
        return ("%d substitution event(s) DEFLATE the conclusion: the stranded tail reached the row "
                "and the substitute says it cannot. The substitution rule is unsound on those rows."
                % s["events_with_deflation"])
    return ("the substitute neither contradicts nor is vacuous; it moves the claim on %d row(s) "
            "where the two tails disagree about reachability."
            % len(s["rows_where_tails_disagree_on_reachability"]))


# ------------------------------------------------------------------ build / publish
def build(outdir=None):
    outdir = outdir or OUTDIR
    budget = load(SRC_BUDGET)
    floor_face = load(SRC_FLOOR)
    rows = rows_from(budget)
    cen = censused(rows)
    ident = identity_check(census(rows), floor_face)
    s = summary_of(census(rows), budget, floor_face)
    return {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": CUTOFF,
        "generated": _stamp(),
        "source_faces": [SRC_BUDGET, SRC_FLOOR],
        "frozen_spec": {
            "D1_direction_is_a_row_property":
                "flip_direction / flip_multiplier are row fields; no tail supplies them, so no "
                "substitution can contradict the direction. Structural, not evidence.",
            "D2_conclusion":
                "reachable = flip_multiplier inside that tail's published [multiplier_min, "
                "multiplier_max], both ends inclusive; re-derived here, never copied from E272.",
            "D3_stranded":
                "spread_pct == 0 AND multiplier_min == multiplier_max AND n_cells > 1 (a degenerate "
                "range means the tail cannot express movement).",
            "D4_sound":
                "substitute measurable AND substitute.reachable >= stranded.reachable; only a "
                "deflation is a contradiction, an inflation is a scope problem.",
            "D5_vacuity":
                "agreement produced by a degenerate stranded range is reported as vacuous and is not "
                "counted as evidence.",
            "D6_no_false_precision":
                "the scope bracket is an interval with calibrated=False unless the data supports more.",
            "tolerance": TOL,
            "spread_tolerance": SPREAD_TOL,
        },
        "census": cen,
        "identity_check": ident,
        "scope_bracket": s["scope_bracket"],
        "summary": s,
        "verdict": s["verdict"],
        "verdict_reason": reason_of(s),
        "no_bill": NO_BILL,
    }


def _stamp():
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _write(face, outdir=None, tag=""):
    outdir = outdir or OUTDIR
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    name = FACE if not tag else FACE.replace(".json", "_%s.json" % tag)
    path = os.path.join(outdir, name)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    with io.open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    with io.open(os.path.join(outdir, LATEST), "w", encoding="utf-8") as fh:
        fh.write(body)
    return path


def run(save=True, outdir=None, tag=""):
    face = build(outdir)
    if save:
        face["_written"] = os.path.basename(_write(face, outdir, tag))
    return face


def verify(outdir=None, tag=""):
    """Re-derive from the published faces and compare; never trust this face's own summary."""
    problems = []
    disk = load(FACE if not tag else FACE.replace(".json", "_%s.json" % tag))
    fresh = build(outdir)
    for key in ("census", "identity_check", "scope_bracket", "summary"):
        if fresh.get(key) != disk.get(key):
            problems.append("%s does not re-derive" % key)
    if fresh.get("verdict") != disk.get("verdict"):
        problems.append("verdict does not re-derive")
    if (fresh.get("summary") or {}).get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict is outside the frozen vocabulary")
    if (fresh.get("identity_check") or {}).get("mismatched"):
        problems.append("our reachability disagrees with E272's published boolean")
    if not (fresh.get("identity_check") or {}).get("stranding_agrees_with_e278"):
        problems.append("our stranded set disagrees with E278's flagged groups")
    if any(e.get("deflating") for rec in fresh.get("census") or []
           for e in rec.get("substitutions") or []):
        problems.append("a substitution deflates a reaching conclusion")
    return {"ok": not problems, "problems": problems,
            "verdict": (disk.get("summary") or {}).get("verdict")}


# ------------------------------------------------------------------ selftest
def _row(index, direction, flip, tight, wide, cell="c0", leg="cross", base=60, row="cross"):
    """tight/wide = (spread_pct, normalised_gap, multiplier_min, multiplier_max)."""
    def blk(t, spec):
        return {"tail": t, "spread_pct": spec[0], "normalised_gap": spec[1],
                "multiplier_min": spec[2], "multiplier_max": spec[3],
                "reachable": (None if (flip is None or spec[2] is None)
                              else bool(spec[2] - TOL <= flip <= spec[3] + TOL)),
                "n_cells": 4, "gap_pct": 10.0}
    return {"row": row, "index": index, "cell": cell, "leg": leg, "base": base,
            "flip_direction": direction, "flip_multiplier": flip,
            "tight": blk("tight", tight), "wide": blk("wide", wide)}


def _one(rows):
    return censused(rows)


def selftest():
    legs = []

    def leg(ok, name, detail=""):
        legs.append({"ok": bool(ok), "name": name, "detail": detail})

    # L1: D3 -- stranding needs a zero spread AND a degenerate range AND >1 cell
    tr = {"spread_pct": 0.0, "multiplier_min": 1.0, "multiplier_max": 1.0, "n_cells": 4}
    leg(is_stranded(tr) is True, "L1 stranded: zero + degenerate + multi-cell")
    tr1 = dict(tr, n_cells=1)
    leg(is_stranded(tr1) is False, "L1b single cell is not stranded", str(is_stranded(tr1)))
    tr2 = {"spread_pct": 0.0, "multiplier_min": 1.0, "multiplier_max": 1.1, "n_cells": 4}
    leg(is_stranded(tr2) is False, "L1c zero spread with a live range is not stranded")
    tr3 = {"spread_pct": 10.0, "multiplier_min": 1.0, "multiplier_max": 1.0, "n_cells": 4}
    leg(is_stranded(tr3) is False, "L1d degenerate range with a spread is not stranded")

    # L2: D2 -- reachability re-derivation, both ends inclusive, strict excluded
    tr = {"multiplier_min": 1.5, "multiplier_max": 2.0}
    leg(reachable_of(tr, 1.5) is True and reachable_strict_of(tr, 1.5) is False,
        "L2 inclusive ends feed reachable, not strict")
    leg(reachable_of(tr, 2.0) is True and reachable_of(tr, 2.0000001) is False,
        "L2b just outside the range is not reachable")
    leg(reachable_of(tr, None) is None, "L2c no flip is not a verdict")

    # L3: D4 -- a deflation needs a stranded tail that DOES reach (flip == the degenerate value)
    cen = _one([_row(0, "widening_reenters", 2.0,
                     (0.0, None, 2.0, 2.0),            # stranded, but reachable: flip == 2.0
                     (16.0, 0.4, 5.0, 6.0))])          # substitute says no
    ev = cen[0]["substitutions"][0]
    leg(ev["reachable_from"] is True and ev["deflating"] is True,
        "L3 deflation: stranded reaches, substitute does not",
        "from=%r to=%r deflating=%r" % (ev["reachable_from"], ev["reachable_to"],
                                        ev["deflating"]))
    # the common shape: the stranded tail cannot reach and the substitute can. That is a widening,
    # not a contradiction, and must never be reported as one.
    cen = _one([_row(0, "widening_reenters", 3.0,
                     (0.0, None, 1.0, 1.0),
                     (16.0, 0.4, 2.5, 3.5))])
    ev = cen[0]["substitutions"][0]
    leg(ev["inflating"] is True and ev["deflating"] is False,
        "L3b inflation is not a contradiction",
        "inflating=%r deflating=%r" % (ev["inflating"], ev["deflating"]))
    cen = _one([_row(0, "widening_reenters", 9.0,
                     (0.0, None, 1.0, 1.0),
                     (16.0, 0.4, 2.5, 3.5))])
    leg(cen[0]["substitutions"][0]["deflating"] is False,
        "L3c no deflation when the substitute also says no")

    # L4: D5 -- vacuity is claimed only when the agreement came from a degenerate range
    ev = _one([_row(0, "widening_reenters", 9.0, (0.0, None, 1.0, 1.0),
                    (16.0, 2.0, 2.5, 3.5))])[0]["substitutions"][0]
    leg(ev["vacuous"] is True and ev["verdict_agrees"] is True,
        "L4 degenerate agree is vacuous",
        "agrees=%r vacuous=%r" % (ev["verdict_agrees"], ev["vacuous"]))
    # a stranded tail whose range is NOT degenerate cannot happen under D3, so build the record
    # directly: agreement there would be evidence, not vacuity
    fake = {"_tail": {"tight": {"multiplier_min": 1.0, "multiplier_max": 2.0, "n_cells": 4,
                                "spread_pct": 0.0, "normalised_gap": None, "gap_pct": 10.0},
                      "wide": {"multiplier_min": 2.5, "multiplier_max": 3.5, "n_cells": 4,
                               "spread_pct": 16.0, "normalised_gap": 0.4, "gap_pct": 20.0}},
            "row": "x", "index": 0, "cell": "c", "leg": "self", "base": 60,
            "flip_direction": "widening_reenters", "flip_multiplier": 3.0}
    rec = substitution_record(fake, "tight", {"tight": False, "wide": True})
    leg(rec["vacuous"] is False, "L4b non-degenerate agreement is evidence, not vacuity")

    # L5: D1 -- the direction fields come from the row, untouched by any tail choice
    r = _row(0, "narrowing_escapes", 0.63, (9.6, 6.2, 1.0, 1.1), (9.6, 22.2, 1.98, 2.18))
    cen = _one([r])
    leg(cen[0]["flip_direction"] == "narrowing_escapes"
        and cen[0]["substitutions"] == [], "L5 direction is carried by the row")
    leg(cen[0]["swap"]["tight"]["to"] == "wide" and cen[0]["swap"]["wide"]["to"] == "tight",
        "L5b the swap view is symmetric by construction")

    # L6: both tails stranded -> no usable event, the attempt is disclosed and the row stays unmeasured
    cen = _one([_row(0, "widening_reenters", 3.0, (0.0, None, 1.0, 1.0),
                     (0.0, None, 1.0, 1.0))])
    leg(cen[0]["substitutions"] == [] and cen[0]["substitution_available"] is False
        and len(cen[0]["substitution_blocked"]) == 2,
        "L6 both tails stranded leaves the row unmeasured",
        "blocked=%d" % len(cen[0]["substitution_blocked"]))

    # L7: a healthy pair produces no event at all
    cen = _one([_row(0, "widening_reenters", 1.55, (10.0, 5.0, 1.0, 1.1),
                     (9.0, 1.2, 1.5, 1.6))])
    leg(cen[0]["substitutions"] == [] and cen[0]["substitution_available"] is False
        and cen[0]["usable_tails"] == ["tight", "wide"], "L7 healthy pair has nothing to substitute")

    # L8: the real census shape -- 4 groups, 12 measured rows, 4 without a flip
    face = load(FACE) if os.path.exists(os.path.join(OUTDIR, FACE)) else None
    if face is not None:
        s = face.get("summary") or {}
        cen = face.get("census") or []
        leg(s.get("rows_measured") == 12 and s.get("rows_published") == 16
            and s.get("rows_without_flip") == 4 and s.get("n_groups") == 4
            and len(cen) == 12, "L8 real census shape",
            "measured=%s published=%s without=%s groups=%s rows=%s"
            % (s.get("rows_measured"), s.get("rows_published"), s.get("rows_without_flip"),
               s.get("n_groups"), len(cen)))
        leg(s.get("rows_measured_per_e272") == s.get("rows_measured"),
            "L8b the row count agrees with E272's own summary",
            "%s vs %s" % (s.get("rows_measured_per_e272"), s.get("rows_measured")))
    else:
        leg(False, "L8 real census shape", "face missing")

    # L9: identity -- published booleans re-derive, and the stranded set is E278's
    if face is not None:
        idc = face.get("identity_check") or {}
        leg(idc.get("checked") == 24 and not idc.get("mismatched"), "L9 identity to E272",
            "checked=%s mismatched=%s" % (idc.get("checked"), len(idc.get("mismatched") or [])))
        leg(idc.get("stranding_agrees_with_e278") is True
            and idc.get("stranded_groups_here") == idc.get("stranded_groups_per_e278"),
            "L9b stranding agrees with E278",
            "%s vs %s" % (idc.get("stranded_groups_here"), idc.get("stranded_groups_per_e278")))
    else:
        leg(False, "L9 identity to E272", "face missing")
        leg(False, "L9b stranding agrees with E278", "face missing")

    # L10: the wide tail weakly dominates the tight tail -- zero violations
    if face is not None:
        viol = (face.get("summary") or {}).get("wide_dominates_tight_violations")
        leg(viol == [], "L10 wide weakly dominates tight", repr(viol))
    else:
        leg(False, "L10 wide weakly dominates tight", "face missing")

    # L11: the scope bracket is an interval and does not claim calibration
    if face is not None:
        b = face.get("scope_bracket") or {}
        leg(b.get("calibrated") is False and b.get("may_go_as_high_as") is not None
            and b.get("must_exceed_observed") is not None, "L11 scope bracket is an interval",
            "lo=%r hi=%r calibrated=%r" % (b.get("must_exceed_observed"),
                                           b.get("may_go_as_high_as"), b.get("calibrated")))
    else:
        leg(False, "L11 scope bracket is an interval", "face missing")

    # L12: every inflating swap is real, and the inflations land on E272's reachable-wide rows
    if face is not None:
        try:
            e272 = load(SRC_BUDGET)
            pub = sorted((e272.get("summary") or {}).get("reachable_wide_indices") or [])
        except (IOError, ValueError):
            pub = None
        mine = sorted({rec["index"] for rec in face.get("census") or []
                       if rec["swap"]["tight"]["inflates"]})
        leg(pub is not None and mine == pub, "L12 inflations land on E272's reachable-wide rows",
            "mine=%s e272=%s" % (mine, pub))
    else:
        leg(False, "L12 inflations land on E272's reachable-wide rows", "face missing")

    # L13: no event both deflates and is vacuous; the two flags are exclusive readings
    if face is not None:
        bad = [e for rec in face.get("census") or [] for e in rec.get("substitutions") or []
               if e["deflating"] and e["vacuous"]]
        leg(bad == [], "L13 deflation and vacuity never co-occur", "%d" % len(bad))
    else:
        leg(False, "L13 deflation and vacuity never co-occur", "face missing")

    # L15: the two swap directions name the SAME rows -- a reversal, not two separate events
    if face is not None:
        s = face.get("summary") or {}
        ir = s.get("swap_inflation_rows") or []
        dr = s.get("swap_deflation_rows") or []
        leg(s.get("swap_rows_match") is True and ir == dr and len(ir) == len(set(ir))
            and len(ir) == s.get("swap_inflations_tight_to_wide"),
            "L15 swap directions name the same rows", "inflate=%s deflate=%s" % (ir, dr))
    else:
        leg(False, "L15 swap directions name the same rows", "face missing")

    # L14: verdict is inside the vocabulary and matches the summary's own reasoning
    if face is not None:
        s = face.get("summary") or {}
        leg(s.get("verdict") in VERDICT_VOCAB and face.get("verdict") == s.get("verdict"),
            "L14 verdict in vocabulary and consistent", str(s.get("verdict")))
    else:
        leg(False, "L14 verdict in vocabulary and consistent", "face missing")

    ok = sum(1 for l in legs if l["ok"])
    return {"legs": legs, "passed": ok, "total": len(legs), "ok": ok == len(legs)}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = run()
        s = face["summary"]
        print("verdict=%s events=%d deflations=%d vacuous=%d stranded_rows=%d disagree_rows=%s"
              % (s["verdict"], s["substitution_events"], s["events_with_deflation"],
                 s["events_vacuous_agreement"], s["rows_with_stranded_tail"],
                 s["rows_where_tails_disagree_on_reachability"]))
        print("written results/state_tilt/%s" % FACE)
        return 0
    if cmd == "verify":
        r = verify()
        print(json.dumps(r, ensure_ascii=False))
        return 0 if r["ok"] else 1
    if cmd == "selftest":
        r = selftest()
        for l in r["legs"]:
            print("%s %s  %s" % ("PASS" if l["ok"] else "FAIL", l["name"], l["detail"]))
        print("%d/%d" % (r["passed"], r["total"]))
        return 0 if r["ok"] else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())