"""E283 -- can the E279 "deflation" contradiction ever fire on a published row?

E279 (BANDSUBSTITUTE) declared D4: a substitution is sound unless the substitute DEFLATES the
conclusion, i.e. the stranded tail reaches the row while the substitute says it cannot. E281 then
found that every stranded tail publishes a degenerate multiplier range (min == max == 1.0), which
means the stranded tail can only "reach" when the row's flip multiplier equals that single value.
If no published row has that shape, the contradiction branch is an untested branch -- and a test
whose failure mode cannot fire is not a test.

DECISION RULE, declared before any number is read (E188 / r1319 discipline -- the rule is frozen
here and re-emitted into the face so the face cannot be read against a rule it did not declare):

  D1  REACHABILITY IS E272's CONTRACT, IMPORTED NOT COPIED. A tail reaches a row when the row's
      flip multiplier sits inside that tail's published multiplier range. For a degenerate range
      [v, v] this reduces to the flip equalling v at the published tolerance, which is the whole
      question this face measures.
  D2  THE BRANCH = E279's deflation: a stranded (D3: spread 0, degenerate range, >1 cell) tail
      reaches while the substitute does not. Only rows carrying a degenerate tail are candidates.
  D3  TOLERANCE BAND. A row needs a relative tolerance tau_r = gap_pct_r / 100 (gap_pct is E272's
      own percent ruler, sign-free). The branch is reachable under tolerance tau iff some candidate
      row has tau_r <= tau, so the band is [min_r tau_r, +infinity). Reachable at the PUBLISHED
      tolerance (TOL percent) iff min_r tau_r <= TOL / 100.
  D4  A BAND IS ONLY A TOLERANCE IF THE INSTRUMENT STILL DISCRIMINATES INSIDE IT. At the band's
      lower end the same loosened test is applied to EVERY published tail reading; if it calls at
      least COLLAPSE_SHARE of them reachable the band is a collapse, not a tolerance, and the
      verdict says so instead of quoting a number that would destroy the reading scheme.
  D5  NO REBURN: published faces are re-read only. No draw stream is drawn, no band rebuilt, no
      engine runs. A verdict here is a statement about the published numbers, not the market.
  D6  SCOPE IS MEASURED. Every dated BAND* face is scanned; <slug>_latest mirrors are dropped BY
      NAME and the drop is published, because counting a face and its mirror censuses the same
      cells twice (E282's first-run defect, r1307).

Verdict vocabulary (frozen):
  no_degenerate_tail_is_published
  the_deflation_branch_fires_on_a_published_row
  the_branch_needs_a_tolerance_that_erases_the_reading
  the_branch_is_unreachable_but_a_narrow_band_would_reach_it

Usage:  python scripts/e283_degenerate_range_reachable.py run|verify|selftest
"""
import glob
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e272_flip_budget_two_tails as e272  # noqa: E402  (gap_to_flip_pct -- one formula)
import e279_substitution_soundness as e279  # noqa: E402  (stranded/degenerate definitions)
import e282_substitution_disagreement_census as e282  # noqa: E402  (scope census)

ROOT = e272.ROOT
OUTDIR = e272.OUTDIR
TOL = e272.TOL
TAILS = ("tight", "wide")
OTHER = {"tight": "wide", "wide": "tight"}

STUDY = "E283_degenerate_range_reachable"
TITLE = ("a degenerate tail can only reach a row when the flip equals its single multiplier -- "
         "does that ever happen, and how loose a tolerance would it take?")
CUTOFF = "2026-10-29"
SRC_BUDGET = "BANDFLIPBUDGET-%s.json" % CUTOFF    # E272: per-row, per-tail range + flip
SRC_SUBST = "BANDSUBSTITUTE-%s.json" % CUTOFF     # E279: stranded-tail census (identity partner)
FACE = "BANDDEFLATE-%s.json" % CUTOFF
LATEST = "banddeflate_latest.json"
SELF_FACES = (FACE, LATEST)

# D4's threshold: the loosened test must leave the instrument with more than half its readings
# still non-reachable, otherwise calling the branch "reachable" describes a different instrument.
COLLAPSE_SHARE = 0.5

VERDICT_VOCAB = (
    "no_degenerate_tail_is_published",
    "the_deflation_branch_fires_on_a_published_row",
    "the_branch_needs_a_tolerance_that_erases_the_reading",
    "the_branch_is_unreachable_but_a_narrow_band_would_reach_it",
)

NO_BILL = ("measurement only: E272's published per-row tail ranges and E279's stranded census are "
           "re-read. No draw stream is drawn, no band rebuilt, no engine runs. A verdict here is a "
           "statement about the published numbers, not about the market.")


# ------------------------------------------------------------------ io
def load(name, outdir=None):
    with io.open(os.path.join(outdir or OUTDIR, name), encoding="utf-8") as fh:
        return json.load(fh)


def face_files(outdir=None):
    """Dated BAND* publications; <slug>_latest mirrors and this face dropped by name (D6)."""
    dated, mirrors = [], []
    for path in sorted(glob.glob(os.path.join(outdir or OUTDIR, "BAND*.json"))):
        name = os.path.basename(path)
        if name in SELF_FACES:
            continue
        if name.endswith("_latest.json"):
            mirrors.append(name)
            continue
        dated.append(name)
    return dated, mirrors


def rows_of(face):
    """Rows carrying both tails' published range and the row's flip (same shape E282 censuses)."""
    return e282.rows_of(face)


def scope_census(outdir=None):
    """D6: which dated publications can be censused, and why the others cannot.

    Scanned with THIS face's own excluded-name list: borrowing E282's census would let this
    face's own publication appear in its own scope on the second run (E180/E209 self-inclusion
    family) and the scope block would then never re-derive.
    """
    outdir = outdir or OUTDIR
    dated, mirrors = face_files(outdir)
    qual, excluded = [], []
    for name in mirrors:
        excluded.append({"face": name,
                         "reason": "mirror of a dated face (same rows, censused once via the "
                                   "dated face)"})
    for name in dated:
        try:
            face = load(name, outdir)
        except (IOError, ValueError) as exc:
            excluded.append({"face": name, "reason": "unreadable: %s" % exc})
            continue
        rows = rows_of(face)
        if rows:
            qual.append({"face": name, "rows": len(rows)})
        else:
            excluded.append({"face": name,
                             "reason": "publishes no row carrying both tails' multiplier range "
                                       "and a flip multiplier"})
    return {"files_scanned": len(qual) + len(excluded),
            "faces_qualifying": qual,
            "faces_excluded": excluded,
            "n_qualifying": len(qual),
            "n_excluded": len(excluded),
            "self_faces_excluded": list(SELF_FACES)}


def reading_key(rec):
    return "%s|%d|%d" % (rec.get("leg"), int(rec.get("base") or 0), int(rec.get("index") or 0))


# ------------------------------------------------------------------ per-reading measurement
def reading_record(row, tail):
    """One row's reading against one tail, with the degenerate-range question answered."""
    tr = e279.tail_rec(row, tail)
    flip = row.get("flip_multiplier")
    rec = {"row_key": reading_key(row), "row": row.get("row"), "cell": row.get("cell"),
           "index": row.get("index"), "leg": row.get("leg"), "base": row.get("base"),
           "tail": tail, "flip_multiplier": flip,
           "multiplier_min": tr.get("multiplier_min"),
           "multiplier_max": tr.get("multiplier_max"),
           "spread_pct": tr.get("spread_pct"), "n_cells": tr.get("n_cells"),
           "gap_pct": tr.get("gap_pct"),
           "published_reachable": tr.get("published_reachable")}
    rec["degenerate"] = bool(e279.range_degenerate(tr))
    rec["stranded"] = bool(e279.is_stranded(tr))
    # D1: re-derive reachability from the range, never copy the boolean
    rec["rederived_reachable"] = e279.reachable_of(tr, flip)
    rec["polarity_agrees"] = (rec["rederived_reachable"] == rec["published_reachable"])
    gap = tr.get("gap_pct")
    rec["required_tolerance_pct"] = gap
    rec["required_tolerance_fraction"] = (None if gap is None else float(gap) / 100.0)
    # D3: reachable at the published tolerance means the flip equals the published value
    rec["reachable_at_published_tolerance"] = bool(
        gap is not None and float(gap) <= TOL)
    if rec["degenerate"] and flip and rec["multiplier_min"]:
        rec["flip_to_degenerate_ratio"] = float(flip) / float(rec["multiplier_min"])
    else:
        rec["flip_to_degenerate_ratio"] = None
    return rec


def readings(rows):
    out = []
    for row in rows:
        for tail in TAILS:
            out.append(reading_record(row, tail))
    out.sort(key=lambda r: (str(r.get("leg")), int(r.get("base") or 0),
                            int(r.get("index") or 0), r.get("tail")))
    return out


# ------------------------------------------------------------------ branch + band
def candidate_records(recs):
    """D2: rows carrying a degener ate tail. The deflation needs a stranded tail (E279's D3)."""
    return [r for r in recs if r["degenerate"]]


def branch_state(rows, recs):
    """Which candidates could deflate, and whether any of them does at the published tolerance."""
    stranded = {}
    for row in rows:
        for tail in TAILS:
            tr = e279.tail_rec(row, tail)
            if e279.is_stranded(tr):
                stranded[reading_key(row)] = tail
    cands = candidate_records(recs)
    fires = [r for r in cands if r["reachable_at_published_tolerance"]]
    deflatable = []
    for r in cands:
        key = r["row_key"]
        if key not in stranded or stranded[key] != r["tail"]:
            continue                      # degenerate but not stranded: not an E279 D2 candidate
        substitute = [x for x in recs if x["row_key"] == key and x["tail"] == OTHER[r["tail"]]]
        sub = substitute[0] if substitute else None
        deflatable.append({"row_key": key, "tail": r["tail"],
                           "stranded": True,
                           "substitute_tail": OTHER[r["tail"]],
                           "substitute_reachable": (None if sub is None
                                                    else sub["rederived_reachable"]),
                           "substitute_measurable": (None if sub is None
                                                     else bool(sub["spread_pct"])),
                           "flip_multiplier": r["flip_multiplier"],
                           "degenerate_value": r["multiplier_min"],
                           "flip_to_degenerate_ratio": r["flip_to_degenerate_ratio"],
                           "required_tolerance_pct": r["required_tolerance_pct"],
                           "deflates_at_published_tolerance": r["reachable_at_published_tolerance"]})
    deflatable.sort(key=lambda d: (str(d["row_key"]), d["tail"]))
    return {"n_candidate_readings": len(cands),
            "n_stranded_readings": len(stranded),
            "n_deflatable": len(deflatable),
            "deflatable": deflatable,
            "fires": bool(fires),
            "fires_on": sorted({r["row_key"] + "@" + r["tail"] for r in fires})}


def tolerance_band(deflatable):
    """D3: the band of relative tolerances at which the branch becomes reachable."""
    req = [d["required_tolerance_pct"] for d in deflatable
           if d.get("required_tolerance_pct") is not None]
    if not req:
        return {"lower_pct": None, "lower_fraction": None, "upper_pct": None,
                "reachable_at_published_tolerance": False, "statement": "no candidate row"}
    lo = min(float(x) for x in req)
    tight = [d for d in deflatable if d.get("required_tolerance_pct") == lo]
    return {"lower_pct": lo, "lower_fraction": lo / 100.0, "upper_pct": None,
            "band_is_half_open_above": True,
            "reachable_at_published_tolerance": bool(lo <= TOL),
            "published_tolerance_pct": TOL,
            "binding_rows": sorted({d["row_key"] + "@" + d["tail"] for d in tight}),
            "statement": ("the branch becomes reachable only at a relative tolerance of at least "
                          "%.4f pct (%.4f of the flip); every looser test fires it" % (lo, lo / 100.0))}


def discrimination(recs, band):
    """D4: apply the band's own loosened test to EVERY reading and count what it now calls reachable."""
    if band.get("lower_pct") is None:
        return {"tolerance_pct": None, "readings_total": len(recs),
                "readings_reachable_at_band": None, "readings_reachable_published": None,
                "collapse": None}
    tau = float(band["lower_pct"])
    at_band = [r for r in recs
               if r.get("gap_pct") is not None and float(r["gap_pct"]) <= tau]
    published = [r for r in recs if r.get("published_reachable") is True]
    share = (float(len(at_band)) / len(recs)) if recs else None
    return {"tolerance_pct": tau,
            "tolerance_fraction": tau / 100.0,
            "readings_total": len(recs),
            "readings_reachable_at_band": len(at_band),
            "readings_reachable_published": len(published),
            "share_reachable_at_band": share,
            "collapse_share_frozen": COLLAPSE_SHARE,
            "collapse": bool(share is not None and share >= COLLAPSE_SHARE),
            "newly_reachable_at_band": sorted(
                r["row_key"] + "@" + r["tail"] for r in at_band
                if r.get("published_reachable") is not True)}


def verdict_of(branch, band, disc):
    if not branch["n_candidate_readings"]:
        return "no_degenerate_tail_is_published"
    if branch["fires"]:
        return "the_deflation_branch_fires_on_a_published_row"
    if disc.get("collapse"):
        return "the_branch_needs_a_tolerance_that_erases_the_reading"
    return "the_branch_is_unreachable_but_a_narrow_band_would_reach_it"


def reason_of(verdict, branch, band, disc):
    if verdict == "no_degenerate_tail_is_published":
        return "no published row carries a degenerate multiplier range, so D4's deflation cannot arise."
    if verdict == "the_deflation_branch_fires_on_a_published_row":
        return ("%d candidate reading(s) already reach at the published tolerance; the branch is live."
                % len(branch["fires_on"]))
    if verdict == "the_branch_needs_a_tolerance_that_erases_the_reading":
        return ("0 of %d candidate readings reach at the published tolerance; the nearest needs a "
                "relative tolerance of %.4f pct (a flip %.3fx its degenerate value), and at that "
                "tolerance %d of %d published tail readings -- %.1f pct, against %d published -- "
                "would read reachable, so the test that fires the branch is not the test that "
                "published the family."
                % (branch["n_candidate_readings"], band["lower_pct"],
                   (float(branch["deflatable"][0]["flip_to_degenerate_ratio"]) if
                    branch["deflatable"] and branch["deflatable"][0].get("flip_to_degenerate_ratio")
                    else float("nan")),
                   disc["readings_reachable_at_band"], disc["readings_total"],
                   100.0 * (disc["share_reachable_at_band"] or 0.0),
                   disc["readings_reachable_published"]))
    return ("0 candidate readings reach at the published tolerance, but the band that would reach "
            "them (%.4f pct) still leaves %d of %d readings non-reachable."
            % (band["lower_pct"], disc["readings_total"] - disc["readings_reachable_at_band"],
               disc["readings_total"]))


# ------------------------------------------------------------------ identity
def identity_check(recs, subst, rows):
    """Re-derive E272's booleans and E279's stranded census; never copy either."""
    mismatched = [r["row_key"] + "@" + r["tail"] for r in recs if not r["polarity_agrees"]]
    mine = sorted({r["row_key"] for r in recs if r["stranded"]})
    theirs = sorted({reading_key(c) for c in (subst.get("census") or [])
                     if c.get("stranded_tails")})
    e279_summary = set()
    for c in (subst.get("census") or []):
        for t in c.get("stranded_tails") or []:
            e279_summary.add((reading_key(c), t))
    mine_pairs = sorted((r["row_key"], r["tail"]) for r in recs if r["stranded"])
    return {"readings_checked": len(recs),
            "mismatched": mismatched,
            "n_mismatched": len(mismatched),
            "stranded_rows_mine": mine,
            "stranded_rows_per_e279": theirs,
            "stranded_set_agrees": mine == theirs,
            "stranded_pairs_agree": mine_pairs == sorted(e279_summary),
            "rows_censused_per_e272": len(rows)}


# ------------------------------------------------------------------ build
def build(outdir=None):
    outdir = outdir or OUTDIR
    budget = load(SRC_BUDGET, outdir)
    subst = load(SRC_SUBST, outdir)
    rows = e279.rows_from(budget)
    recs = readings(rows)
    scope = scope_census(outdir)
    dated, mirrors = face_files(outdir)
    branch = branch_state(rows, recs)
    band = tolerance_band(branch["deflatable"])
    disc = discrimination(recs, band)
    verdict = verdict_of(branch, band, disc)
    ident = identity_check(recs, subst, rows)
    deg = [r for r in recs if r["degenerate"]]
    face = {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": CUTOFF,
        "generated": _stamp(),
        "decision_rule": {
            "D1": "reachability is E272's published contract (flip inside the tail's published "
                  "multiplier range), imported from e272, not copied",
            "D2": "the branch is E279's deflation: a stranded tail reaches while the substitute "
                  "does not; only rows carrying a degenerate range are candidates",
            "D3": "a row needs relative tolerance tau_r = gap_pct_r / 100, so the band is "
                  "[min tau_r, +infinity); reachable at the published tolerance iff "
                  "min tau_r <= TOL/100",
            "D4": "the band is only a tolerance if the instrument still discriminates inside it: "
                  "at the band's lower end the same test is applied to every reading and a share "
                  ">= %r counts as a collapse" % COLLAPSE_SHARE,
            "D5": "no reburn: published faces re-read only, no draw, no band rebuilt, no engine",
            "D6": "scope is measured; <slug>_latest mirrors are dropped by name and the drop is "
                  "published",
        },
        "source_faces": [SRC_BUDGET, SRC_SUBST],
        "scope": dict(scope, mirrors_dropped=len(mirrors), mirrors=mirrors,
                      dated_faces_scanned=len(dated),
                      rows_censused=len(rows), tail_readings_censused=len(recs)),
        "degenerate_readings": deg,
        "n_degenerate_readings": len(deg),
        "branch": branch,
        "tolerance_band": band,
        "discrimination_at_band": disc,
        "identity_check": ident,
        "verdict": verdict,
        "verdict_reason": reason_of(verdict, branch, band, disc),
        "summary": {"verdict": verdict,
                    "rows_censused": len(rows),
                    "tail_readings_censused": len(recs),
                    "n_degenerate_readings": len(deg),
                    "n_deflatable": branch["n_deflatable"],
                    "branch_fires": branch["fires"],
                    "required_tolerance_pct": band.get("lower_pct"),
                    "reachable_at_published_tolerance": band.get(
                        "reachable_at_published_tolerance"),
                    "readings_reachable_published": disc.get("readings_reachable_published"),
                    "readings_reachable_at_band": disc.get("readings_reachable_at_band"),
                    "collapse_at_band": disc.get("collapse"),
                    "identity_mismatched": ident["n_mismatched"]},
        "no_bill": NO_BILL,
    }
    return face


def _stamp():
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _write(face, outdir=None):
    outdir = outdir or OUTDIR
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    path = os.path.join(outdir, FACE)
    with io.open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    with io.open(os.path.join(outdir, LATEST), "w", encoding="utf-8") as fh:
        fh.write(body)
    return path


def run(save=True, outdir=None):
    face = build(outdir)
    if save:
        face["_written"] = _write(face, outdir)
    return face


def verify(outdir=None):
    """Re-derive from the sources and compare; never trust this face's own summary."""
    outdir = outdir or OUTDIR
    problems = []
    with io.open(os.path.join(outdir, FACE), encoding="utf-8") as fh:
        disk = json.load(fh)
    fresh = build(outdir)
    for key in ("scope", "degenerate_readings", "branch", "tolerance_band",
                "discrimination_at_band", "identity_check", "summary", "verdict",
                "verdict_reason"):
        if fresh.get(key) != disk.get(key):
            problems.append("%s does not re-derive" % key)
    if (fresh.get("summary") or {}).get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict is outside the frozen vocabulary")
    ident = fresh.get("identity_check") or {}
    if ident.get("n_mismatched"):
        problems.append("a published boolean contradicts the range that published it")
    if not ident.get("stranded_set_agrees"):
        problems.append("our stranded set disagrees with E279's census")
    if not ident.get("stranded_pairs_agree"):
        problems.append("our stranded pairs disagree with E279's census")
    if (fresh.get("scope") or {}).get("n_qualifying") != 1:
        problems.append("the qualifying-face count changed without a scope note")
    return {"ok": not problems, "problems": problems,
            "verdict": (disk.get("summary") or {}).get("verdict")}


# ------------------------------------------------------------------ selftest
def _blk(tail, spread, lo, hi, cells=4, gap=10.0, reachable=None):
    return {"tail": tail, "spread_pct": spread, "normalised_gap": None,
            "multiplier_min": lo, "multiplier_max": hi, "n_cells": cells, "gap_pct": gap,
            "reachable": reachable}


def _row(flip, tight, wide, index=0, leg="cross", base=200, cell="c0", row="cross"):
    rec = {"row": row, "index": index, "cell": cell, "leg": leg, "base": base,
           "flip_direction": "widening_reenters", "flip_multiplier": flip,
           "tight": tight, "wide": wide}
    for tail in TAILS:
        blk = rec[tail]
        blk["gap_pct"] = e272.gap_to_flip_pct(flip, blk["multiplier_min"], blk["multiplier_max"])
        blk["reachable"] = e279.reachable_of(blk, flip)
    return rec


def selftest():
    legs = []

    def leg(ok, name, detail=""):
        legs.append({"ok": bool(ok), "name": name, "detail": detail})

    # L1: D1 -- a degenerate range reaches only at the published value
    r = reading_record(_row(2.0, _blk("tight", 0.0, 1.0, 1.0), _blk("wide", 10.0, 1.5, 2.5)),
                       "tight")
    leg(r["degenerate"] and r["stranded"] and not r["reachable_at_published_tolerance"]
        and r["required_tolerance_pct"] >= 50.0 - 1e-9,
        "L1 a degenerate tail does not reach a flip far from its value", str(r["gap_pct"]))
    r2 = reading_record(_row(1.0, _blk("tight", 0.0, 1.0, 1.0), _blk("wide", 10.0, 1.5, 2.5)),
                        "tight")
    leg(r2["reachable_at_published_tolerance"] is True,
        "L1b a flip equal to the degenerate value does reach", str(r2["gap_pct"]))

    # L2: the ratio is flip/value and the required tolerance is gap/100
    leg(abs(r["flip_to_degenerate_ratio"] - 2.0) < 1e-12
        and abs(r["required_tolerance_fraction"] - r["required_tolerance_pct"] / 100.0) < 1e-15,
        "L2 ratio and tolerance fraction are the declared quantities")

    # L3: a degenerate tail with ONE cell is degenerate but not stranded (E279's D3)
    r3 = reading_record(_row(2.0, _blk("tight", 0.0, 1.0, 1.0, cells=1),
                             _blk("wide", 10.0, 1.5, 2.5)), "tight")
    leg(r3["degenerate"] is True and r3["stranded"] is False,
        "L3 degenerate is not the same claim as stranded")

    # L4: branch -- only stranded candidates are deflatable, and a firing row is reported
    rows = [_row(3.0, _blk("tight", 0.0, 1.0, 1.0), _blk("wide", 10.0, 1.5, 2.5), index=1),
            _row(1.0, _blk("tight", 0.0, 1.0, 1.0), _blk("wide", 10.0, 1.5, 2.5), index=2),
            _row(2.0, _blk("tight", 5.0, 1.0, 1.2), _blk("wide", 10.0, 1.5, 2.5), index=3)]
    recs = readings(rows)
    br = branch_state(rows, recs)
    leg(br["n_candidate_readings"] == 2 and br["n_deflatable"] == 2,
        "L4 only rows carrying a degenerate range are candidates",
        json.dumps({"cand": br["n_candidate_readings"], "def": br["n_deflatable"]}))
    leg(br["fires"] is True and br["fires_on"] == ["cross|200|2@tight"],
        "L4b a row whose flip equals the degenerate value fires the branch", str(br["fires_on"]))

    # L5: band -- lower end is the tightest candidate, and it is half-open above
    rows2 = [_row(3.0, _blk("tight", 0.0, 1.0, 1.0), _blk("wide", 10.0, 1.5, 3.5), index=1),
             _row(2.0, _blk("tight", 0.0, 1.0, 1.0), _blk("wide", 10.0, 1.5, 2.5), index=2)]
    recs2 = readings(rows2)
    br2 = branch_state(rows2, recs2)
    band2 = tolerance_band(br2["deflatable"])
    leg(br2["fires"] is False
        and abs(band2["lower_pct"] - 50.0) < 1e-9
        and band2["upper_pct"] is None
        and band2["binding_rows"] == ["cross|200|2@tight"],
        "L5 the band's lower end is the tightest candidate row", json.dumps(band2))

    # L6: D4 -- the loosened test must be applied to EVERY reading, and a collapse is named
    disc2 = discrimination(recs2, band2)
    leg(disc2["readings_total"] == 4 and disc2["readings_reachable_at_band"] >= 2
        and disc2["collapse"] is True,
        "L6 the band's own test is applied to every reading and collapses it"
        if disc2["collapse"] else "L6 measured",
        json.dumps({k: disc2[k] for k in ("readings_total", "readings_reachable_at_band",
                                          "share_reachable_at_band", "collapse")}))

    # L7: verdict order
    leg(verdict_of({"n_candidate_readings": 0}, {}, {}) == "no_degenerate_tail_is_published",
        "L7 no candidates")
    leg(verdict_of({"n_candidate_readings": 2, "fires": True}, {}, {})
        == "the_deflation_branch_fires_on_a_published_row", "L7b fires")
    leg(verdict_of({"n_candidate_readings": 2, "fires": False},
                   {"lower_pct": 5.0}, {"collapse": True})
        == "the_branch_needs_a_tolerance_that_erases_the_reading", "L7c collapse")
    leg(verdict_of({"n_candidate_readings": 2, "fires": False},
                   {"lower_pct": 0.5}, {"collapse": False})
        == "the_branch_is_unreachable_but_a_narrow_band_would_reach_it", "L7d narrow band")

    # L8: scope -- mirrors are dropped by name, never counted (r1307's first-run defect)
    dated, mirrors = face_files()
    leg(all(n.endswith(".json") and not n.endswith("_latest.json") and n not in SELF_FACES
            for n in dated) and all(n.endswith("_latest.json") for n in mirrors)
        and not (set(dated) & set(mirrors)),
        "L8 dated faces and mirrors never overlap", "%d dated / %d mirrors"
        % (len(dated), len(mirrors)))

    # L9: the live face re-derives, its identity holds, and its verdict is in the vocabulary
    face = build()
    ident = face["identity_check"]
    leg(ident["n_mismatched"] == 0 and ident["stranded_set_agrees"]
        and ident["stranded_pairs_agree"],
        "L9 live identity: published booleans and E279's stranded set both reproduce",
        "%d readings" % ident["readings_checked"])
    leg(face["verdict"] in VERDICT_VOCAB
        and face["summary"]["verdict"] == face["verdict"],
        "L9b live verdict is inside the frozen vocabulary", face["verdict"])

    # L10: the live band, if it exists, is bounded below and its discrimination is published
    band = face["tolerance_band"]
    disc = face["discrimination_at_band"]
    leg(band["lower_pct"] is None or (band["lower_pct"] > 0 and band["upper_pct"] is None
                                      and disc["readings_total"] > 0
                                      and isinstance(disc["collapse"], bool)),
        "L10 the band is half-open above and its discrimination is measured",
        json.dumps({"lo": band["lower_pct"], "collapse": disc.get("collapse")}))

    ok = sum(1 for l in legs if l["ok"])
    return {"legs": legs, "passed": ok, "total": len(legs), "ok": ok == len(legs)}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = run()
        s = face["summary"]
        print("verdict=%s rows=%d readings=%d degenerate=%d deflatable=%d fires=%s "
              "tolerance_pct=%s collapse=%s"
              % (s["verdict"], s["rows_censused"], s["tail_readings_censused"],
                 s["n_degenerate_readings"], s["n_deflatable"], s["branch_fires"],
                 s["required_tolerance_pct"], s["collapse_at_band"]))
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