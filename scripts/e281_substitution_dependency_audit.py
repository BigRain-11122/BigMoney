"""E281 -- is E278's substitution policy load-bearing anywhere it was never tested?

E279 scoped the policy to "substitute only to prove a row CAN move, never to conclude it cannot"
after finding that its own two substitution events agreed vacuously. That scoping leaves one
question open: does any ALREADY-PUBLISHED conclusion in the BAND family rest on a stranded tail to
say "cannot"? A family with zero dependent conclusions makes the policy harmless; any dependent
conclusion must be re-read as an upper bound or withdrawn.

DECISION RULE, declared before any number is read (E188 / r1319 discipline -- the rule is frozen
here and re-emitted into the face so the face cannot be read against a rule it did not declare):

  D1  CLAIM UNIT = (face, row, tail). A claim exists only where a face publishes a reachability
      boolean for BOTH tails of a row, i.e. a node carrying two tail blocks with multiplier_min /
      multiplier_max. Extraction is structural (the tail pair), never a bare 'reachable' key: a
      face that says 'cannot' in prose without publishing the pair is disclosure-only and cannot
      be dependency-checked.
  D2  POLARITY = the published 'reachable' boolean, re-derived from the published range (E279 D2)
      and required to agree. A "cannot" is reachable == False.
  D3  DEPENDENT = a "cannot" whose own tail is stranded (E279 D3: spread == 0 AND degenerate range
      AND n_cells > 1). Such a claim is not a measurement of an interval; it is produced by a range
      that cannot express movement.
  D4  LOAD-BEARING = a dependent claim whose face text (verdict + verdict_reason) names that tail
      AND carries a negative marker AND publishes no "can" on that same tail. That is the
      operational form of "a conclusion rests on it".
  D5  SELF-DISCLOSURE = a face that already labels the tail inert / dead by construction /
      untested / "not because ... safe" / "carries no evidence" has pre-empted the dependency. The
      disclosure is recorded verbatim and the claim is NOT counted as needing action.
  D6  VERDICT, in order: if any load-bearing claim has a substitute that would ADD the claim, the
      conclusion is contradicted and must be withdrawn; else if any load-bearing claim is
      undisclosed, it must be re-read as an upper bound; else if every dependent claim is vacuous
      and disclosed the policy is harmless as scoped; else no claim depends on a stranded tail.
  D7  A DEFECT FOUND IN A PUBLISHED FACE IS DISCLOSED AND SEEDED, NEVER REPAIRED IN THE SAME ROUND
      THAT FOUND IT. The finding round must not also be the round that re-burns the face it is
      judging; the repair goes to the pool as its own card so that the repair's verify is a
      different session from the finding.

Usage:  python scripts/e281_substitution_dependency_audit.py run|verify|selftest
"""
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e262_p95_transfer_across_windows as e262  # noqa: E402
import e279_substitution_soundness as e279  # noqa: E402  (tail reading + D2/D3, reused not rewritten)

ROOT = e262.ROOT
OUTDIR = e262.OUTDIR
TOL = e279.TOL
SPREAD_TOL = e279.SPREAD_TOL
TAILS = e279.TAILS
OTHER = e279.OTHER

STUDY = "E281_substitution_dependency_audit"
TITLE = ("does any already-published BAND-family conclusion rest on a stranded tail to say "
         "'cannot' -- i.e. is the substitution policy load-bearing where it was never tested?")
CUTOFF = "2026-10-29"
SRC_BUDGET = "BANDFLIPBUDGET-%s.json" % CUTOFF
FACE = "BANDSUBSTITUTEAUDIT-%s.json" % CUTOFF
LATEST = "bandsubstituteaudit_latest.json"

DATED_RE = re.compile(r"^BAND[A-Z0-9]+-\d{4}-\d{2}-\d{2}(-d\d+)?\.json$")
NEGATIVE_RE = re.compile(r"(cannot|can not|never|unreachable|inert|dead|zero|no row|none)", re.I)
DISCLOSURE_RE = re.compile(
    r"(inert|dead by construction|untested|never publishes|not because[^.]{0,60}safe|"
    r"by construction|carries no evidence|rather than safe)", re.I)
TAIL_WORD = {
    "tight": re.compile(r"\btight\b|\blower end\b|\bp05\b", re.I),
    "wide": re.compile(r"\bwide\b|\bupper end\b|\bp95\b", re.I),
}

VERDICT_VOCAB = (
    "a_cannot_rests_on_a_substitute_that_contradicts_it",
    "a_cannot_rests_on_a_stranded_tail_without_disclosure",
    "every_dependent_cannot_is_vacuous_and_disclosed",
    "no_cannot_claim_rests_on_a_stranded_tail",
)

NO_BILL = ("measurement only: every dated BAND* face is re-read and each published reachability "
           "boolean is re-derived from its own multiplier range. No draw stream is drawn, no band "
           "rebuilt, no engine runs. A verdict here is a statement about the published numbers, "
           "not about the market.")


# ------------------------------------------------------------------ discovery
def discover_faces(outdir=None):
    """Every dated BAND* face, self faces excluded. _latest twins are not dated and never enter."""
    outdir = outdir or OUTDIR
    names = []
    for path in glob.glob(os.path.join(outdir, "BAND*.json")):
        name = os.path.basename(path)
        if name in (FACE, LATEST) or not DATED_RE.match(name):
            continue
        names.append(name)
    return sorted(names)


def claim_nodes(obj, path="", depth=0, out=None):
    """Structural extraction: nodes carrying both tail blocks with a multiplier range."""
    if out is None:
        out = []
    if depth > 9:
        return out
    if isinstance(obj, dict):
        t, w = obj.get("tight"), obj.get("wide")
        if (isinstance(t, dict) and isinstance(w, dict)
                and "multiplier_min" in t and "multiplier_min" in w):
            out.append((path, obj))
        for k, v in obj.items():
            claim_nodes(v, path + "/" + str(k), depth + 1, out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            claim_nodes(v, path + "/[%d]" % i, depth + 1, out)
    return out


def face_text(face):
    parts = []
    for key in ("title", "verdict", "verdict_reason", "summary"):
        v = face.get(key)
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, (dict, list)):
            parts.append(json.dumps(v, ensure_ascii=False))
    return "\n".join(parts)


# ------------------------------------------------------------------ one claim
def claim_of(row, tail, text, face_cannot_by_tail=None):
    """Classify one (row, tail) reachability claim. Never reads anything but the row and the text."""
    tail_rec = e279.tail_rec(row, tail)
    other = OTHER[tail]
    other_rec = e279.tail_rec(row, other)
    flip = row.get("flip_multiplier")
    derived = e279.reachable_of(tail_rec, flip)
    published = tail_rec.get("published_reachable")
    stranded = e279.is_stranded(tail_rec)
    other_measurable = e279.is_measurable(other_rec)
    other_reach = e279.reachable_of(other_rec, flip)
    cannot = published if published is not None else derived
    dependent = bool(cannot is False and stranded)
    face_cannot_by_tail = face_cannot_by_tail or {}
    named = bool(TAIL_WORD[tail].search(text))
    negative = bool(NEGATIVE_RE.search(text))
    disclosed = bool(DISCLOSURE_RE.search(text))
    no_can_on_tail = not face_cannot_by_tail.get(tail, {}).get("any_can", False)
    load_bearing = bool(dependent and named and negative and no_can_on_tail and not disclosed)
    return {
        "row_key": "%s|%s|%s" % (row.get("row"), row.get("cell"), row.get("index")),
        "leg": row.get("leg"), "base": row.get("base"), "index": row.get("index"),
        "cell": row.get("cell"), "row": row.get("row"),
        "tail": tail,
        "flip_multiplier": flip,
        "stranded": stranded,
        "published_reachable": published,
        "derived_reachable": derived,
        "polarity_agrees": (True if published is None or derived is None else published == derived),
        "cannot": cannot,
        "dependent": dependent,
        "substitute_tail": other,
        "substitute_measurable": other_measurable,
        "substitute_reachable": other_reach,
        # D6 input: the substitute would ADD the claim the stranded tail denied
        "substitute_contradicts": bool(dependent and other_measurable and other_reach is True),
        "substitute_agrees_vacuously": bool(dependent and other_reach is False),
        "tail_named_in_face": named,
        "negative_marker_in_face": negative,
        "face_no_can_on_this_tail": no_can_on_tail,
        "disclosed_in_face": disclosed,
        "load_bearing": load_bearing,
    }


# ------------------------------------------------------------------ census
def census(faces=None, outdir=None):
    outdir = outdir or OUTDIR
    faces = faces if faces is not None else discover_faces(outdir)
    e279_name = "BANDSUBSTITUTE-%s.json" % CUTOFF
    e279_face = {}
    e279_path = os.path.join(outdir, e279_name)
    if os.path.isfile(e279_path):
        with io.open(e279_path, encoding="utf-8") as fh:
            e279_face = json.load(fh)
    per_face, claims = [], []
    for name in faces:
        path = os.path.join(outdir, name)
        with io.open(path, encoding="utf-8") as fh:
            face = json.load(fh)
        text = face_text(face)
        nodes = claim_nodes(face)
        if not nodes:
            per_face.append({"face": name, "claim_nodes": 0, "claims": 0, "dependent": 0,
                             "load_bearing": 0, "disclosed": None,
                             "verdict": face.get("verdict")})
            continue
        # face-level: does this tail ever publish a "can" on this face?
        by_tail = {}
        for _p, node in nodes:
            for t in TAILS:
                for row in [node]:
                    r = e279.tail_rec(row, t)
                    reach = e279.reachable_of(r, row.get("flip_multiplier"))
                    slot = by_tail.setdefault(t, {"any_can": False, "any_cannot": False})
                    if reach is True:
                        slot["any_can"] = True
                    elif reach is False:
                        slot["any_cannot"] = True
        face_claims = []
        for p, node in nodes:
            row = dict(node)
            for t in TAILS:
                rec = claim_of(row, t, text, by_tail)
                rec["face"] = name
                rec["node_path"] = p
                claims.append(rec)
                face_claims.append(rec)
        per_face.append({
            "face": name,
            "claim_nodes": len(nodes),
            "claims": len(face_claims),
            "dependent": sum(1 for c in face_claims if c["dependent"]),
            "load_bearing": sum(1 for c in face_claims if c["load_bearing"]),
            "disclosed": bool(DISCLOSURE_RE.search(text)),
            "verdict": face.get("verdict"),
        })
    return {"faces": per_face, "claims": claims,
            "identity_check": identity_check({"claims": claims}, e279_face)}


def summary_of(cen):
    claims = cen["claims"]
    dep = [c for c in claims if c["dependent"]]
    lb = [c for c in claims if c["load_bearing"]]
    contra = [c for c in lb if c["substitute_contradicts"]]
    undisclosed = [c for c in lb if not c["disclosed_in_face"]]
    flip_rows = sorted({c["row_key"] for c in claims
                        if _pair_disagrees(claims, c["row_key"])})
    dep_faces = sorted({c["face"] for c in dep})
    s = {
        "faces_scanned": len(cen["faces"]),
        "faces_with_claim_nodes": sum(1 for f in cen["faces"] if f["claim_nodes"]),
        "faces_prose_only": sum(1 for f in cen["faces"]
                                if not f["claim_nodes"] and DISCLOSURE_RE.search(
                                    json.dumps(f.get("verdict") or "", ensure_ascii=False))),
        "claims_total": len(claims),
        "claims_cannot": sum(1 for c in claims if c["cannot"] is False),
        "claims_can": sum(1 for c in claims if c["cannot"] is True),
        "claims_without_polarity": sum(1 for c in claims if c["cannot"] is None),
        "polarity_mismatches": [
            {"face": c["face"], "row_key": c["row_key"], "tail": c["tail"],
             "published": c["published_reachable"], "derived": c["derived_reachable"]}
            for c in claims if not c["polarity_agrees"]],
        "dependent_cannot_claims": len(dep),
        "dependent_faces": dep_faces,
        "dependent_with_measurable_substitute": sum(
            1 for c in dep if c["substitute_measurable"]),
        "dependent_substitute_would_add": [c["row_key"] + "|" + c["tail"]
                                           for c in dep if c["substitute_contradicts"]],
        "dependent_substitute_agrees_vacuously": sum(
            1 for c in dep if c["substitute_agrees_vacuously"]),
        "load_bearing_claims": len(lb),
        "load_bearing_details": [
            {"face": c["face"], "row_key": c["row_key"], "tail": c["tail"],
             "disclosed": c["disclosed_in_face"]} for c in lb],
        "load_bearing_contradicted": len(contra),
        "load_bearing_undisclosed": len(undisclosed),
        "rows_where_the_two_tails_disagree": flip_rows,
        "identity_stranded_set_agrees": (cen.get("identity_check") or {}).get(
            "stranded_set_agrees"),
        "identity_disagree_set_agrees": (cen.get("identity_check") or {}).get(
            "disagree_set_agrees"),
        "identity_mismatched": len((cen.get("identity_check") or {}).get("mismatched") or []),
        "e279_summary_field_is_ambiguous": (cen.get("identity_check") or {}).get(
            "e279_summary_field_is_ambiguous"),
        "e278_policy_load_bearing": bool(lb),
    }
    s["verdict"] = verdict_of(s)
    return s


def _pair_disagrees(claims, row_key):
    by = {}
    for c in claims:
        if c["row_key"] == row_key:
            by[c["tail"]] = c["derived_reachable"]
    if len(by) < 2:
        return False
    vals = list(by.values())
    return any(v is None for v in vals) is False and vals[0] != vals[1]


def identity_check(cen, e279_face):
    """Our re-derivation must equal E279's published census, row by row, on all three faces.

    The summary field is checked SEPARATELY and at its own scope: E279 keyed it on the group
    label, so a group whose cells mostly agree is published as a disagreeing ROW."""
    mismatched, checked, stranded_mismatch = [], 0, []
    mine = {}
    for c in cen["claims"]:
        mine.setdefault(c["row_key"], {})[c["tail"]] = c
    for rec in e279_face.get("census") or []:
        key = "%s|%s|%s" % (rec.get("row"), rec.get("cell"), rec.get("index"))
        got = mine.get(key)
        if got is None:
            mismatched.append({"row_key": key, "why": "absent from this audit"})
            continue
        for t in TAILS:
            checked += 1
            if got[t]["derived_reachable"] != (rec.get("reachable") or {}).get(t):
                mismatched.append({"row_key": key, "tail": t,
                                   "e279": (rec.get("reachable") or {}).get(t),
                                   "here": got[t]["derived_reachable"]})
        if sorted(rec.get("stranded_tails") or []) != sorted(
                [t for t in TAILS if got[t]["stranded"]]):
            stranded_mismatch.append(key)

    disagree_here = sorted({k for k in mine if _pair_disagrees(cen["claims"], k)})
    disagree_e279 = sorted(
        "%s|%s|%s" % (rec.get("row"), rec.get("cell"), rec.get("index"))
        for rec in (e279_face.get("census") or [])
        if ((rec.get("swap") or {}).get("tight") or {}).get("agrees") is False)
    published_field = (e279_face.get("summary") or {}).get(
        "rows_where_tails_disagree_on_reachability")
    # group-scope over-claim: the published value names groups; a group is named whole even when
    # only one of its cells disagrees, so the field claims more cells than the census supports.
    by_group = {}
    for rec in e279_face.get("census") or []:
        g = rec.get("row")
        slot = by_group.setdefault(g, {"cells": 0, "disagreeing_cells": 0, "published": False})
        slot["cells"] += 1
        if ((rec.get("swap") or {}).get("tight") or {}).get("agrees") is False:
            slot["disagreeing_cells"] += 1
    for g in published_field or []:
        if g in by_group:
            by_group[g]["published"] = True
    overclaimed = {g: v for g, v in by_group.items()
                   if v["published"] and v["disagreeing_cells"] < v["cells"]}
    return {
        "checked_tail_booleans": checked,
        "mismatched": mismatched,
        "stranded_set_mismatches": stranded_mismatch,
        "stranded_set_agrees": not stranded_mismatch,
        "disagree_rows_here": disagree_here,
        "disagree_rows_per_e279_census": disagree_e279,
        "disagree_set_agrees": disagree_here == disagree_e279,
        "e279_summary_field": published_field,
        "e279_summary_field_scope": "group label",
        "e279_summary_field_over_claims": overclaimed,
        "e279_summary_field_is_ambiguous":
            bool(overclaimed) and set(published_field or [])
            == {g for g, v in by_group.items() if v["disagreeing_cells"]},
        "note": ("the field is not wrong about which groups contain a disagreement; it is keyed "
                 "on the group, so a group with 1 disagreeing cell out of N is published whole"),
    }


def verdict_of(s):
    if s["load_bearing_contradicted"]:
        return "a_cannot_rests_on_a_substitute_that_contradicts_it"
    if s["load_bearing_undisclosed"]:
        return "a_cannot_rests_on_a_stranded_tail_without_disclosure"
    if s["dependent_cannot_claims"]:
        return "every_dependent_cannot_is_vacuous_and_disclosed"
    return "no_cannot_claim_rests_on_a_stranded_tail"


def reason_of(s):
    v = s["verdict"]
    if v == "a_cannot_rests_on_a_substitute_that_contradicts_it":
        return ("%d load-bearing 'cannot' claim(s) are contradicted by their own substitute (%s): "
                "reading the other tail would ADD the claim the stranded tail denied, so those "
                "conclusions must be withdrawn or re-read as upper bounds."
                % (s["load_bearing_contradicted"], ", ".join(s["dependent_substitute_would_add"])))
    if v == "a_cannot_rests_on_a_stranded_tail_without_disclosure":
        return ("%d of %d load-bearing 'cannot' claim(s) rest on a stranded tail and their face "
                "does not disclose it: %s. They must be re-read as upper bounds."
                % (s["load_bearing_undisclosed"], s["load_bearing_claims"],
                   json.dumps([d for d in s["load_bearing_details"] if not d["disclosed"]],
                              ensure_ascii=False)))
    if v == "every_dependent_cannot_is_vacuous_and_disclosed":
        return ("%d of %d claims are 'cannot' on a stranded tail, in %d face(s) (%s), and every one "
                "of them sits in a face that already labels the tail inert/dead by construction/"
                "untested rather than safe. %d dependent claim(s) have a measurable substitute; %d "
                "of those would agree vacuously and none would add the claim. So the policy is "
                "load-bearing only where the family already says the claim is vacuous -- no "
                "published conclusion needs to be withdrawn, but no 'cannot' on a stranded tail may "
                "ever be read as a measurement. Where the two tails genuinely disagree (%d row(s): "
                "%s) the tail you read decides the answer, exactly as E279 published."
                % (s["dependent_cannot_claims"], s["claims_cannot"],
                   len(s["dependent_faces"]), ",".join(s["dependent_faces"]),
                   s["dependent_with_measurable_substitute"],
                   s["dependent_substitute_agrees_vacuously"],
                   len(s["rows_where_the_two_tails_disagree"]),
                   ",".join(s["rows_where_the_two_tails_disagree"])))
    return ("no claim in %d scanned face(s) states 'cannot' from a stranded tail; the substitution "
            "policy has no dependent conclusion to be load-bearing on."
            % s["faces_scanned"])


# ------------------------------------------------------------------ build / publish
def build(outdir=None):
    outdir = outdir or OUTDIR
    cen = census(outdir=outdir)
    s = summary_of(cen)
    return {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": CUTOFF,
        "generated": _stamp(),
        "source_faces": discover_faces(outdir),
        "source_pointer": SRC_BUDGET,
        "frozen_spec": {
            "D1_claim_unit":
                "(face, row, tail) where a face publishes a reachability boolean for BOTH tails; "
                "extraction is structural on the tail pair, never on a bare 'reachable' key.",
            "D2_polarity":
                "the published boolean, re-derived from the published multiplier range (E279 D2) "
                "and required to agree; a 'cannot' is reachable == False.",
            "D3_dependent":
                "a 'cannot' whose own tail is stranded per E279 D3 (spread == 0 AND degenerate "
                "range AND n_cells > 1).",
            "D4_load_bearing":
                "the face text names that tail AND carries a negative marker AND publishes no "
                "'can' on that same tail.",
            "D5_self_disclosure":
                "a face that already labels the tail inert/dead by construction/untested/not-safe "
                "pre-empts the dependency; the claim is recorded but needs no action.",
            "D6_verdict_order":
                "contradicted > undisclosed > vacuous-but-disclosed > no dependency.",
            "tolerance": TOL,
            "spread_tolerance": SPREAD_TOL,
        },
        "faces": cen["faces"],
        "claims": cen["claims"],
        "identity_check": cen["identity_check"],
        "summary": s,
        "verdict": s["verdict"],
        "verdict_reason": reason_of(s),
        "no_bill": NO_BILL,
    }


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
        face["_written"] = os.path.basename(_write(face, outdir))
    return face


def verify(outdir=None):
    """Re-derive from the sources and compare; never trust this face's own summary."""
    outdir = outdir or OUTDIR
    problems = []
    with io.open(os.path.join(outdir, FACE), encoding="utf-8") as fh:
        disk = json.load(fh)
    fresh = build(outdir)
    for key in ("faces", "claims", "identity_check", "summary"):
        if fresh.get(key) != disk.get(key):
            problems.append("%s does not re-derive" % key)
    if fresh.get("verdict") != disk.get("verdict"):
        problems.append("verdict does not re-derive")
    if (fresh.get("summary") or {}).get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict is outside the frozen vocabulary")
    if (fresh.get("summary") or {}).get("polarity_mismatches"):
        problems.append("a face's published boolean contradicts its own range")
    ic = fresh.get("identity_check") or {}
    if ic.get("mismatched"):
        problems.append("our re-derivation disagrees with E279's published census")
    if not ic.get("stranded_set_agrees"):
        problems.append("our stranded set disagrees with E279's census")
    if not ic.get("disagree_set_agrees"):
        problems.append("our disagreement set disagrees with E279's census")
    if (fresh.get("summary") or {}).get("rows_where_the_two_tails_disagree") is None:
        problems.append("the disagreement set is not reported")
    return {"ok": not problems, "problems": problems,
            "verdict": (disk.get("summary") or {}).get("verdict")}


# ------------------------------------------------------------------ selftest
def _row(tight, wide, flip, index=0, leg="cross", base=200, cell="c0", row="cross"):
    """tight/wide = (spread_pct, normalised_gap, multiplier_min, multiplier_max)."""
    def blk(t, spec):
        rec = {"tail": t, "spread_pct": spec[0], "normalised_gap": spec[1],
               "multiplier_min": spec[2], "multiplier_max": spec[3], "n_cells": 4, "gap_pct": 10.0}
        rec["reachable"] = (None if flip is None else e279.reachable_of(rec, flip))
        return rec
    return {"row": row, "index": index, "cell": cell, "leg": leg, "base": base,
            "flip_direction": "widening_reenters", "flip_multiplier": flip,
            "tight": blk("tight", tight), "wide": blk("wide", wide)}


def selftest():
    legs = []

    def leg(ok, name, detail=""):
        legs.append({"ok": bool(ok), "name": name, "detail": detail})

    # L1: a measured tail's 'cannot' is not dependent on substitution
    row = _row((10.0, 2.0, 1.5, 2.0), (16.0, 2.5, 1.5, 2.0), flip=3.0)
    c = claim_of(row, "tight", "the tight end is used")
    leg(c["dependent"] is False and c["cannot"] is False,
        "L1 measured tail's cannot is not dependent", str(c["dependent"]))

    # L2: stranded tail + measurable substitute that would ADD the claim -> contradicted
    row = _row((0.0, None, 1.0, 1.0), (16.0, 2.0, 1.5, 2.0), flip=1.7)
    c = claim_of(row, "tight", "the tight end is inert and no row can re-enter")
    leg(c["dependent"] is True and c["substitute_measurable"] is True
        and c["substitute_contradicts"] is True,
        "L2 stranded cannot with an adding substitute", json.dumps({
            "dependent": c["dependent"], "contra": c["substitute_contradicts"]}))

    # L3: stranded tail + substitute that also says cannot -> vacuous agreement
    row = _row((0.0, None, 1.0, 1.0), (16.0, 2.0, 1.5, 2.0), flip=3.0)
    c = claim_of(row, "tight", "the tight end is inert")
    leg(c["dependent"] is True and c["substitute_contradicts"] is False
        and c["substitute_agrees_vacuously"] is True,
        "L3 stranded cannot with a vacuous agreement")

    # L4: a face that publishes a 'can' on the same tail is not load-bearing
    row = _row((0.0, None, 1.0, 1.0), (16.0, 2.0, 1.5, 2.0), flip=1.7)
    c = claim_of(row, "tight", "the tight end is inert", {"tight": {"any_can": True}})
    leg(c["dependent"] is True and c["load_bearing"] is False,
        "L4 a face with a can on the tail is not load-bearing")

    # L5: self-disclosure drops the load-bearing flag
    row = _row((0.0, None, 1.0, 1.0), (16.0, 2.0, 1.5, 2.0), flip=3.0)
    plain = claim_of(row, "tight", "no row can re-enter at the tight end")
    disclosed = claim_of(row, "tight",
                         "no row can re-enter at the tight end; the tight end is inert by "
                         "construction, untested rather than safe")
    leg(plain["load_bearing"] is True and disclosed["load_bearing"] is False,
        "L5 disclosure in the face text clears the load-bearing flag",
        "%s/%s" % (plain["load_bearing"], disclosed["load_bearing"]))

    # L6: polarity mismatch is reported, not hidden (published boolean vs re-derivation)
    row = _row((0.0, None, 1.0, 1.0), (16.0, 2.0, 1.5, 2.0), flip=1.7)
    row["tight"]["reachable"] = False  # the range says True (1.7 is outside [1,1]) -- so flip it
    row2 = _row((0.0, None, 1.0, 1.0), (16.0, 2.0, 1.5, 2.0), flip=1.0)
    row2["tight"]["reachable"] = True
    leg(claim_of(row2, "tight", "")["polarity_agrees"] is True,
        "L6 matching polarity is silent")
    bad = _row((0.0, None, 1.0, 1.0), (16.0, 2.0, 1.5, 2.0), flip=1.0)
    bad["tight"]["reachable"] = False
    leg(claim_of(bad, "tight", "")["polarity_agrees"] is False,
        "L6b a published boolean that contradicts its range is caught")

    # L7: verdict order -- contradiction beats undisclosed beats vacuous-disclosed
    base = {"load_bearing_contradicted": 0, "load_bearing_undisclosed": 0,
            "dependent_cannot_claims": 3}
    leg(verdict_of(dict(base)) == "every_dependent_cannot_is_vacuous_and_disclosed",
        "L7 all-vacuous branch")
    leg(verdict_of(dict(base, load_bearing_undisclosed=1))
        == "a_cannot_rests_on_a_stranded_tail_without_disclosure", "L7b undisclosed branch")
    leg(verdict_of(dict(base, load_bearing_undisclosed=1, load_bearing_contradicted=1))
        == "a_cannot_rests_on_a_substitute_that_contradicts_it", "L7c contradiction branch")
    leg(verdict_of(dict(base, dependent_cannot_claims=0))
        == "no_cannot_claim_rests_on_a_stranded_tail", "L7d empty branch")

    # L8: discovery excludes self faces and _latest twins, and keeps dated faces only
    names = ["BANDFLIPBUDGET-2026-10-29.json", "bandflipbudget_latest.json",
             FACE, LATEST, "BANDFLOOR-2026-10-30.json", "notes.json"]
    kept = [n for n in names if DATED_RE.match(n) and n not in (FACE, LATEST)]
    leg(kept == ["BANDFLIPBUDGET-2026-10-29.json", "BANDFLOOR-2026-10-30.json"],
        "L8 dated-face filter drops self and latest twins", ",".join(kept))

    # L9: structural extraction does not fire on a bare 'reachable' key
    bare = {"verdict": "cannot", "rows": [{"reachable": False, "row": "x"}]}
    leg(claim_nodes(bare) == [], "L9 a bare reachable key is not a claim node")
    pair = {"rows": [_row((0.0, None, 1.0, 1.0), (16.0, 2.0, 1.5, 2.0), flip=1.7)]}
    leg(len(claim_nodes(pair)) == 1, "L9b the tail pair is a claim node")

    # L10: a stranded 'can' is not a dependent claim (only 'cannot' can be dependent)
    row = _row((0.0, None, 1.0, 1.0), (16.0, 2.0, 1.5, 2.0), flip=1.0)
    leg(claim_of(row, "tight", "")["dependent"] is False,
        "L10 a stranded tail that reaches is not a dependent cannot")

    # L11: identity -- a group-keyed summary field that names a whole group for one cell is
    # reported as an over-claim, and the census-level sets are compared cell by cell
    rows = [_row((0.0, None, 1.0, 1.0), (16.0, 2.0, 2.5, 3.0), flip=1.7, index=1,
                 cell="all_five", row="cross"),
            _row((10.0, 2.0, 1.5, 2.0), (16.0, 2.0, 1.5, 3.0), flip=2.5, index=9,
                 cell="era_2025_now", row="cross"),
            _row((10.0, 2.0, 1.5, 2.0), (16.0, 2.0, 1.5, 3.0), flip=4.0, index=11,
                 cell="early_three", row="cross")]
    fake_claims = []
    for r in rows:
        for t in TAILS:
            fake_claims.append(claim_of(r, t, ""))
    fake_e279 = {
        "census": [dict(r, reachable={t: e279.reachable_of(e279.tail_rec(r, t),
                                                           r["flip_multiplier"]) for t in TAILS},
                        stranded_tails=[t for t in TAILS
                                        if e279.is_stranded(e279.tail_rec(r, t))],
                        swap={"tight": {"agrees": (e279.reachable_of(e279.tail_rec(r, "tight"),
                                                                    r["flip_multiplier"])
                                                   == e279.reachable_of(e279.tail_rec(r, "wide"),
                                                                        r["flip_multiplier"]))}})
                    for r in rows],
        "summary": {"rows_where_tails_disagree_on_reachability": ["cross"]},
    }
    ic = identity_check({"claims": fake_claims}, fake_e279)
    leg(ic["stranded_set_agrees"] and ic["disagree_set_agrees"] and not ic["mismatched"],
        "L11 identity agrees with a matching census")
    leg(ic["e279_summary_field_is_ambiguous"] is True
        and ic["e279_summary_field_over_claims"].get("cross", {}).get("disagreeing_cells") == 1,
        "L11b a group named whole for one cell is an over-claim",
        json.dumps(ic["e279_summary_field_over_claims"]))

    # L12: identity must catch a census record that disagrees with this audit's re-derivation
    broken = json.loads(json.dumps(fake_e279))
    broken["census"][0]["reachable"]["tight"] = True
    ic2 = identity_check({"claims": fake_claims}, broken)
    leg(len(ic2["mismatched"]) == 1, "L12 identity catches a contradicted boolean")

    ok = sum(1 for l in legs if l["ok"])
    return {"legs": legs, "passed": ok, "total": len(legs), "ok": ok == len(legs)}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = run()
        s = face["summary"]
        print("verdict=%s faces=%d claims=%d cannot=%d dependent=%d load_bearing=%d disagree_rows=%s"
              % (s["verdict"], s["faces_scanned"], s["claims_total"], s["claims_cannot"],
                 s["dependent_cannot_claims"], s["load_bearing_claims"],
                 s["rows_where_the_two_tails_disagree"]))
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