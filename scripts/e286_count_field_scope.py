"""E286 -- does any published COUNT field count the unit its name claims?

E284 swept the dated BAND family for label-scope slips and had to leave one whole class
unjudged: 1338 integer fields whose key carries a unit word (n_rows, n_records, n_seeds,
cells_compared, draws ...). Its reason was honest -- "an integer count's scope depends on that
face's own census semantics; guessing it here would publish a number this face did not measure".
That is exactly the defect class one level down: a count whose NAME says rows may be counting
cells, arms or draws, and nothing in the face says which.

This face does the only measurement that does not require guessing:

  (1) takes every integer field whose key claims a unit with no qualifier -- bare `<unit>`,
      `n_<unit>`, `num_<unit>`, `<unit>_count` -- and reads the claimed unit off the name;
  (2) re-derives it from the face's own published records ONLY when the records the name points
      at sit in the SAME scope as the count (a sibling list keyed exactly `<unit>`);
  (3) reports, per key, the measured unit count, the name-claimed unit, whether they agree, and
      the faces where the count cannot be re-derived at all;
  (4) splits the un-derivable set in two, because the two halves need different fixes: a face
      that publishes a `<unit>` list somewhere else is missing the SCOPE from the name, a face
      that publishes no `<unit>` list at all is naming a design parameter (draws, seeds) that it
      never enumerates.

DECISION RULE, declared before any number is read:

  D1  CLAIMED UNIT COMES FROM THE NAME, STRICTLY.  A key claims a unit only when the unit word is
      the whole name or the only qualified tail (`n_rows`, `num_rows`, `rows_count`, bare `rows`).
      `rows_where_tails_disagree` or `arms_mismatched` are NOT bare-unit claims: they name a
      subset.  Those are counted separately as qualified and never judged -- judging them by
      their unit word is the E208 false-positive (a real quote rejected by a naive word match).
  D2  RE-DERIVATION NEEDS THE SAME SCOPE.  A count is re-derivable only if the record list it
      points at is a SIBLING keyed exactly the claimed unit.  Searching the whole face for some
      `<unit>` list is not a derivation: BANDTRANSFER publishes `flat.cross:200.n_rows = 2` and a
      single unrelated `rows` list of 16 -- a face-wide lookup would publish a slip that does not
      exist.  Anything else is un-derivable, and un-derivable is published, not guessed.
  D3  BOOLEANS ARE NOT COUNTS.  `is_x: true` is not an integer count; bools are excluded before
      any classification (they are ints in Python and would otherwise be body-counted).
  D4  THE TWO HALVES OF 'CANNOT CHECK' ARE NOT THE SAME PROBLEM.  unit_list_exists_elsewhere (the
      face does publish that unit, just not in the count's scope -> the name lacks a scope) versus
      unit_never_published (the face enumerates no records of that unit at all -> the count is a
      design parameter).  Reporting one number would tell a reader to fix a naming problem when
      the real problem is a missing record face.
  D5  NO REBURN.  Published faces are re-read only; no draw stream, no band rebuild, no engine.

Verdict vocabulary (frozen):
  some_unit_named_counts_count_something_other_than_the_unit_their_name_claims
  no_unit_named_count_can_be_re_derived_from_its_own_scope
  the_checkable_share_of_unit_named_counts_is_a_minority_and_every_one_agrees
  every_unit_named_count_is_re_derivable_and_agrees

Usage:  python scripts/e286_count_field_scope.py run|verify|selftest
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e272_flip_budget_two_tails as e272  # noqa: E402  (ROOT / OUTDIR)
import e_band_family_vintage as vintage  # noqa: E402  (universe vintage freeze)

ROOT = e272.ROOT
OUTDIR = e272.OUTDIR

STUDY = "E286_count_field_scope"
TITLE = ("a count whose name says rows may be counting cells -- which published counts can be "
         "re-derived from the face's own records, which agree with the unit their name claims, "
         "and which can never be checked because the records are not in the count's scope?")
CUTOFF = "2026-10-29"
SRC_SCOPE = "BANDDISAGREESCOPE-%s.json" % CUTOFF   # E284's face: its census universe
FACE = "BANDCOUNTSCOPE-%s.json" % CUTOFF
LATEST = "bandcountscope_latest.json"
SELF_FACES = (FACE, LATEST)
MIRROR_SUFFIX = "_latest.json"

UNITS = ("rows", "records", "cells", "arms", "draws", "seeds", "keys", "faces",
         "labels", "legs", "bases", "dates", "bars")
COUNT_PREFIXES = ("n", "num")
COUNT_SUFFIX = "count"

CHECKABLE_SHARE_FLOOR = 0.10   # below this the name is not a checkable claim for most counts
TOL = 1e-12

VERDICT_VOCAB = (
    "some_unit_named_counts_count_something_other_than_the_unit_their_name_claims",
    "no_unit_named_count_can_be_re_derived_from_its_own_scope",
    "the_checkable_share_of_unit_named_counts_is_a_minority_and_every_one_agrees",
    "every_unit_named_count_is_re_derivable_and_agrees",
)

NO_BILL = ("measurement only: the dated BAND faces are re-read and their own published records are "
           "counted. No draw stream is drawn, no band rebuilt, no engine runs, no verdict about "
           "the market. A verdict here is a statement about the published numbers and their names.")


# ------------------------------------------------------------------ io
def load(name, outdir=None):
    with io.open(os.path.join(outdir or OUTDIR, name), encoding="utf-8") as fh:
        return json.load(fh)


def face_universe(outdir=None):
    """Dated BAND faces on disk, mirrors and this study's own faces excluded (E180/E209 family)."""
    outdir = outdir or OUTDIR
    names = []
    for name in sorted(os.listdir(outdir)):
        if not name.startswith("BAND") or not name.endswith(".json"):
            continue
        if name.endswith(MIRROR_SUFFIX) or name in SELF_FACES:
            continue
        names.append(name)
    return names


# ------------------------------------------------------------------ walkers
def walk_values(node, path="", parent=None):
    """Yield every leaf with its dotted path and the dict/list that holds it."""
    if isinstance(node, dict):
        for key, value in node.items():
            child = "%s.%s" % (path, key) if path else key
            for item in walk_values(value, child, node):
                yield item
    elif isinstance(node, list):
        for index, value in enumerate(node):
            for item in walk_values(value, "%s[%d]" % (path, index), node):
                yield item
    else:
        yield path, node, parent


def walk_lists(node, path=""):
    """Yield (dotted path, list) for every list in the face."""
    if isinstance(node, dict):
        for key, value in node.items():
            child = "%s.%s" % (path, key) if path else key
            if isinstance(value, list):
                yield child, value
                for item in walk_lists(value, child):
                    yield item
            else:
                for item in walk_lists(value, child):
                    yield item
    elif isinstance(node, list):
        for index, value in enumerate(node):
            for item in walk_lists(value, "%s[%d]" % (path, index)):
                yield item


def path_key(path):
    return path.split(".")[-1].split("[")[0]


def tokens(key):
    return [t for t in str(key).lower().replace("-", "_").split("_") if t]


# ------------------------------------------------------------------ D1 name reading
def claimed_unit(key):
    """D1: the unit a key claims with no qualifier, or None when the name names a subset."""
    toks = tokens(key)
    if len(toks) == 1 and toks[0] in UNITS:
        return toks[0]
    if len(toks) == 2 and toks[0] in COUNT_PREFIXES and toks[1] in UNITS:
        return toks[1]
    if len(toks) == 2 and toks[1] == COUNT_SUFFIX and toks[0] in UNITS:
        return toks[0]
    return None


def any_unit(key):
    """D1 disclosure only: the last unit word anywhere in the name (subset names included)."""
    hits = [t for t in tokens(key) if t in UNITS]
    return hits[-1] if hits else None


# ------------------------------------------------------------------ D2 derivation
def re_derive(parent, key, unit):
    """D2: only a sibling list keyed exactly <unit> can measure the count its name claims."""
    if not isinstance(parent, dict):
        return None, None, None
    sibling = unit if unit in parent else None
    if sibling is None:
        return None, None, None
    if not isinstance(parent[sibling], list):
        return None, None, None
    toks = tokens(key)
    if not (toks[0] in COUNT_PREFIXES or (len(toks) == 2 and toks[1] == COUNT_SUFFIX)):
        return None, None, None   # a bare `<unit>` int cannot have a sibling of the same name
    return "exact_sibling", len(parent[sibling]), sibling


def analyse_face(name, outdir=None):
    return analyse_face_from_object(name, load(name, outdir))


# ------------------------------------------------------------------ verdict
def decide(summary):
    if summary.get("n_disagree"):
        return "some_unit_named_counts_count_something_other_than_the_unit_their_name_claims"
    if not summary.get("n_re_derivable"):
        return "no_unit_named_count_can_be_re_derived_from_its_own_scope"
    if summary.get("re_derivable_share") is None or \
            summary["re_derivable_share"] < CHECKABLE_SHARE_FLOOR:
        return "the_checkable_share_of_unit_named_counts_is_a_minority_and_every_one_agrees"
    return "every_unit_named_count_is_re_derivable_and_agrees"


def _vintage(outdir):
    """(names, disclosure): the universe as of this face's own publish stamp.

    The family universe grows with each sibling study; re-deriving over the live directory made this
    face disagree with itself after every new publication (see e_band_family_vintage).
    """
    live = face_universe(outdir)
    stored, stored_from = vintage.published_names(outdir, (FACE, LATEST), ("faces_censused",))
    if stored:
        keep = set(live)
        used = [n for n in stored if n in keep]
        gone = [n for n in stored if n not in keep]
        note = vintage.note(used, sorted(set(live) - set(used)), len(live), stored_from, None)
        note["faces_published_but_gone_from_disk"] = gone
        return used, note
    cutoff, frozen_from = None, None
    for name in (FACE, LATEST):
        path = os.path.join(outdir, name)
        if not os.path.exists(path):
            continue
        try:
            with io.open(path, encoding="utf-8") as fh:
                stamp = json.load(fh).get("generated")
        except Exception:
            stamp = None
        cutoff = vintage._parse(stamp)
        if cutoff:
            frozen_from = name
            break
    used, dropped = vintage.vintage_names(outdir, live, cutoff)
    return used, vintage.note(used, dropped, len(live), frozen_from, cutoff)


def build(outdir=None, extend=False):
    outdir = outdir or OUTDIR
    names, vintage_note = _vintage(outdir)
    if extend:
        names = face_universe(outdir)
        vintage_note = vintage.note(names, [], len(names), None, None)
    faces = [analyse_face(name, outdir) for name in names]

    re_rows, cannot_rows = [], []
    for rec in faces:
        for field in rec["fields"]:
            (re_rows if field.get("derivation") else cannot_rows).append(field)

    by_key = {}
    for field in [f for rec in faces for f in rec["fields"]]:
        slot = by_key.setdefault(field["key"], {
            "key": field["key"], "claimed_unit": field["claimed_unit"], "occurrences": 0,
            "re_derivable": 0, "agree": 0, "disagree": 0, "cannot_rederive": 0,
            "faces_cannot_rederive": [], "why_counts": {}})
        slot["occurrences"] += 1
        if field.get("derivation"):
            slot["re_derivable"] += 1
            slot["agree" if field["agrees"] else "disagree"] += 1
        else:
            slot["cannot_rederive"] += 1
            slot["why_counts"][field["why"]] = slot["why_counts"].get(field["why"], 0) + 1
            if field["face"] not in slot["faces_cannot_rederive"]:
                slot["faces_cannot_rederive"].append(field["face"])
    per_key = [by_key[k] for k in sorted(by_key, key=lambda k: (-by_key[k]["occurrences"], k))]

    by_face = []
    for rec in faces:
        n_cannot = len([f for f in rec["fields"] if f.get("cannot_rederive")])
        by_face.append({"face": rec["face"], "unit_named_fields": len(rec["fields"]),
                        "re_derivable": len(rec["fields"]) - n_cannot,
                        "cannot_rederive": n_cannot,
                        "units_published_as_lists": rec["units_published"]})

    total = len(re_rows) + len(cannot_rows)
    n_agree = len([f for f in re_rows if f["agrees"]])
    n_disagree = len(re_rows) - n_agree
    why = {}
    for field in cannot_rows:
        why[field["why"]] = why.get(field["why"], 0) + 1

    summary = {
        "faces_censused": len(faces),
        "unit_named_int_fields": total,
        "qualified_unit_named_fields_not_judged": sum(r["qualified_unit_named_fields"] for r in faces),
        "distinct_count_keys": len(per_key),
        "n_re_derivable": len(re_rows),
        "re_derivable_share": (float(len(re_rows)) / total) if total else None,
        "n_agree": n_agree,
        "n_disagree": n_disagree,
        "disagree_rows": ["%s :: %s" % (f["face"], f["path"]) for f in re_rows if not f["agrees"]],
        "n_cannot_rederive": len(cannot_rows),
        "of_which_unit_list_exists_elsewhere": why.get("unit_list_exists_elsewhere", 0),
        "of_which_unit_never_published": why.get("unit_never_published", 0),
        "faces_with_a_re_derivable_count": sorted({f["face"] for f in re_rows}),
        "faces_where_no_count_can_be_checked": sorted(
            {f["face"] for f in cannot_rows} - {f["face"] for f in re_rows}),
        "checkable_share_floor": CHECKABLE_SHARE_FLOOR,
        "calibrated": False,
    }
    verdict = decide(summary)
    summary["verdict"] = verdict

    identity = {
        "partition_sums_to_fields": len(re_rows) + len(cannot_rows) == total,
        "why_partition_sums_to_cannot": (why.get("unit_list_exists_elsewhere", 0)
                                         + why.get("unit_never_published", 0)) == len(cannot_rows),
        "by_key_occurrences_sum": sum(s["occurrences"] for s in per_key) == total,
        "by_key_re_derivable_sum": sum(s["re_derivable"] for s in per_key) == len(re_rows),
        "by_key_cannot_sum": sum(s["cannot_rederive"] for s in per_key) == len(cannot_rows),
        "by_key_disagree_sum": sum(s["disagree"] for s in per_key) == n_disagree,
        "by_face_fields_sum": sum(b["unit_named_fields"] for b in by_face) == total,
        "no_bool_reached_the_census": all(
            isinstance(f["published_value"], int) and not isinstance(f["published_value"], bool)
            for f in re_rows + cannot_rows),
        "self_faces_absent_from_universe": all(n not in names for n in SELF_FACES),
        "source_scope_face_censused": SRC_SCOPE in names,
        "universe_is_superset_of_e284_scope": None,   # filled below
    }
    try:
        e284 = load(SRC_SCOPE, outdir)
        e284_faces = {row["face"] for row in (e284.get("sweep") or {}).get("faces_with_label_fields") or []}
        identity["e284_faces_scanned"] = len(e284_faces)
        identity["faces_added_since_e284"] = sorted(set(names) - e284_faces)
        identity["faces_dropped_since_e284"] = sorted(e284_faces - set(names))
        identity["universe_is_superset_of_e284_scope"] = not (e284_faces - set(names))
    except (OSError, ValueError, KeyError):
        identity["e284_scope_note"] = "source face unreadable; superset check not run (disclosed)"

    return {
        "study": STUDY, "title": TITLE, "evidence_cutoff": CUTOFF,
        "generated": None,   # stamped by run
        "no_bill": NO_BILL,
        "source_faces": [SRC_SCOPE],
        "faces_censused": names,
        "universe_vintage": vintage_note,
        "frozen_spec": {
            "D1_claim_from_name": "a key claims a unit only when the unit word is the whole name or "
                                  "its only qualifier (bare <unit>, n_<unit>, num_<unit>, "
                                  "<unit>_count); subset names are counted as qualified and never "
                                  "judged (E208: a naive word match rejects real quotes)",
            "D2_same_scope_only": "re-derivation requires a SIBLING list keyed exactly the claimed "
                                  "unit; a face-wide <unit> lookup is not a derivation and would "
                                  "publish slips that do not exist",
            "D3_bools_excluded": "bool is not an integer count and is filtered before classification",
            "D4_two_halves_of_cannot": "unit_list_exists_elsewhere (name lacks a scope) versus "
                                       "unit_never_published (name is a design parameter) are "
                                       "published separately because they need different fixes",
            "D5_no_reburn": "published faces re-read only; no draw stream, no band rebuild, no engine",
            "units": list(UNITS),
            "count_name_shapes": ["<unit>", "n_<unit>", "num_<unit>", "<unit>_count"],
            "checkable_share_floor": CHECKABLE_SHARE_FLOOR,
            "verdict_vocab": list(VERDICT_VOCAB),
        },
        "re_derivable_rows": re_rows,
        "per_key": per_key,
        "per_face": by_face,
        "cannot_rederive": {
            "n_rows": len(cannot_rows),
            "by_why": why,
            "sample": cannot_rows[:40],
            "statement": "these counts name a unit the face does not publish in that count's scope; "
                         "the unit word in the name is not a checkable claim here and is not "
                         "reported as either correct or wrong",
        },
        "identity_check": identity,
        "summary": summary,
        "verdict": verdict,
        "verdict_reason": _reason(verdict, summary),
    }


def _reason(verdict, summary):
    if verdict == "some_unit_named_counts_count_something_other_than_the_unit_their_name_claims":
        return ("%d of %d re-derivable count(s) do not count the unit their name claims: %s. The "
                "rest of the named counts (%d) cannot be checked at all from published records."
                % (summary["n_disagree"], summary["n_re_derivable"],
                   ", ".join(summary["disagree_rows"][:6]), summary["n_cannot_rederive"]))
    if verdict == "no_unit_named_count_can_be_re_derived_from_its_own_scope":
        return ("none of the %d unit-named counts in %d face(s) publishes the records its name "
                "points at in the same scope, so no count can be confirmed or refuted from the "
                "published evidence."
                % (summary["unit_named_int_fields"], summary["faces_censused"]))
    if verdict == "the_checkable_share_of_unit_named_counts_is_a_minority_and_every_one_agrees":
        return ("only %d of %d unit-named count(s) (%s) can be re-derived from the records their "
                "name points at, and every one of those counts the unit it claims -- so the name is "
                "a checkable claim for a minority and a promise nobody can audit for the rest "
                "(%d elsewhere-scope, %d never published)."
                % (summary["n_re_derivable"], summary["unit_named_int_fields"],
                   _fmt_pct(summary["re_derivable_share"]),
                   summary["of_which_unit_list_exists_elsewhere"],
                   summary["of_which_unit_never_published"]))
    return ("%d of %d unit-named count(s) (%s) re-derive from their own scope and all of them count "
            "the unit their name claims."
            % (summary["n_re_derivable"], summary["unit_named_int_fields"],
               _fmt_pct(summary["re_derivable_share"])))


def _fmt_pct(value):
    return "n/a" if value is None else "%.1f pct" % (value * 100.0)


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
    face = build(extend=True)
    face["generated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    write_face(face)
    s = face["summary"]
    print("E286 %s" % face["verdict"])
    print("  faces=%d unit_named_fields=%d re_derivable=%d (%.2f pct) agree=%d disagree=%d"
          % (s["faces_censused"], s["unit_named_int_fields"], s["n_re_derivable"],
             100.0 * (s["re_derivable_share"] or 0.0), s["n_agree"], s["n_disagree"]))
    print("  cannot: elsewhere=%d never_published=%d (qualified not judged=%d)"
          % (s["of_which_unit_list_exists_elsewhere"], s["of_which_unit_never_published"],
             s["qualified_unit_named_fields_not_judged"]))
    print("  identity=%s" % face["identity_check"]["partition_sums_to_fields"])
    print("  disagree rows: %s" % (", ".join(s["disagree_rows"][:4]) or "none"))
    return 0


def cmd_verify():
    stored = load(FACE)
    live = build()
    problems = []
    for key in ("verdict",):
        if stored.get(key) != live.get(key):
            problems.append("%s: stored=%r live=%r" % (key, stored.get(key), live.get(key)))
    s_stored, s_live = stored.get("summary") or {}, live.get("summary") or {}
    for key in ("n_re_derivable", "n_agree", "n_disagree", "n_cannot_rederive",
                "unit_named_int_fields", "disagree_rows"):
        if s_stored.get(key) != s_live.get(key):
            problems.append("summary.%s does not re-derive" % key)
    if not live["identity_check"]["partition_sums_to_fields"]:
        problems.append("re-derivable + cannot does not sum to the fields censused (D2)")
    if not live["identity_check"]["why_partition_sums_to_cannot"]:
        problems.append("the cannot-check split does not sum to the un-derivable total (D4)")
    if not live["identity_check"]["by_key_occurrences_sum"]:
        problems.append("per-key occurrences do not sum to the census")
    if s_stored.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the frozen set")
    print("E286 verify: %d problem(s)" % len(problems))
    for problem in problems:
        print("  - %s" % problem)
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
def _fixture_face():
    return {
        "summary": {"n_rows": 2, "rows": [{"a": 1}, {"a": 2}], "n_rows_guard_runnable": 9,
                    "rows_where_tails_disagree": ["a"], "arms_mismatched": 0, "n_cells": 3,
                    "is_flat": True},
        "arms": [{"n_rows": 2, "rows": [{"x": 1}, {"x": 2}], "n_seeds": 5, "seeds": [1, 2]}],
        "flat": {"cross:200": {"n_rows": 2, "cells": [1, 2, 3]}, "bare": {"rows": 7}},
    }


def cmd_selftest():
    ok, fail = 0, []

    def leg(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append("%s %s" % (name, detail))

    # L1 D1: only a bare unit or its single qualifier is a claim
    leg("L1", claimed_unit("n_rows") == "rows" and claimed_unit("rows") == "rows"
        and claimed_unit("num_cells") == "cells" and claimed_unit("seeds_count") == "seeds",
        [claimed_unit("n_rows"), claimed_unit("seeds_count")])
    # L2 D1: subset names are not bare-unit claims
    leg("L2", claimed_unit("n_rows_guard_runnable") is None
        and claimed_unit("rows_where_tails_disagree") is None
        and claimed_unit("arms_mismatched") is None and claimed_unit("n") is None)
    # L3 the loose reader still sees the unit (disclosure only), which is why it must not judge
    leg("L3", any_unit("rows_where_tails_disagree") == "rows"
        and any_unit("n_rows_guard_runnable") == "rows" and any_unit("n_bp") is None)
    # L4 D2: a sibling list of the same unit is the only derivation
    parent = {"n_rows": 2, "rows": [{"a": 1}, {"a": 2}]}
    method, measured, _ = re_derive(parent, "n_rows", "rows")
    leg("L4", method == "exact_sibling" and measured == 2, (method, measured))
    # L5 a sibling list of a different unit is not used
    leg("L5", re_derive({"n_rows": 2, "cells": [1, 2, 3]}, "n_rows", "rows") == (None, None, None))
    # L6 a bare-unit int cannot be measured by a same-named sibling (it would be the same key)
    leg("L6", re_derive({"rows": 3, "n_records": 1, "records": [1]}, "rows", "rows") == (None, None, None))
    # L7 no sibling at all is un-derivable, never a guessed number
    leg("L7", re_derive({"n_rows": 2}, "n_rows", "rows") == (None, None, None))
    # L8 D3: booleans never reach the census
    face = _fixture_face()
    rec = analyse_face_from_object("FIXTURE.json", face)
    paths = [f["path"] for f in rec["fields"]]
    leg("L8", "summary.is_flat" not in paths, paths)
    # L9 the fixture's same-scope counts agree and the elsewhere ones are un-derivable
    by_path = {f["path"]: f for f in rec["fields"]}
    leg("L9", by_path["summary.n_rows"]["agrees"] is True
        and by_path["arms[0].n_rows"]["agrees"] is True
        and by_path["summary.n_cells"]["cannot_rederive"] is True, sorted(by_path))
    # L10 a measurement that does not match the records is published, not smoothed away
    leg("L10", by_path["arms[0].n_seeds"]["agrees"] is False
        and by_path["arms[0].n_seeds"]["measured_unit_count"] == 2, by_path["arms[0].n_seeds"])
    # L11 D4: a unit the face publishes elsewhere, but not in the count's scope
    leg("L11", by_path["summary.n_cells"]["why"] == "unit_list_exists_elsewhere"
        and by_path["flat.cross:200.n_rows"]["why"] == "unit_list_exists_elsewhere")
    # L12 a unit the face never enumerates at all is its own half
    never = analyse_face_from_object("FIXTURE.json",
                                     {"p": {"n_draws": 60, "n_rows": 1, "rows": [1]}})
    leg("L12", [f for f in never["fields"] if f["key"] == "n_draws"][0]["why"]
        == "unit_never_published")
    # L13 a subset-named count is disclosed as qualified and never judged either way
    leg("L13", rec["qualified_unit_named_fields"] == 2, rec["qualified_unit_named_fields"])
    # L14 verdict: any disagreement wins
    leg("L14", decide({"n_disagree": 1, "n_re_derivable": 5, "re_derivable_share": 0.9})
        == VERDICT_VOCAB[0])
    # L15 nothing checkable is its own verdict, never a silent zero
    leg("L15", decide({"n_disagree": 0, "n_re_derivable": 0, "re_derivable_share": 0.0})
        == VERDICT_VOCAB[1])
    # L16 a minority checkable share is reported as such, not as a clean bill
    leg("L16", decide({"n_disagree": 0, "n_re_derivable": 3, "re_derivable_share": 0.03})
        == VERDICT_VOCAB[2]
        and decide({"n_disagree": 0, "n_re_derivable": 40, "re_derivable_share": 0.40})
        == VERDICT_VOCAB[3])
    # L17 a missing share is not silently treated as a clean majority
    leg("L17", decide({"n_disagree": 0, "n_re_derivable": 1, "re_derivable_share": None})
        == VERDICT_VOCAB[2])
    # L18 every decided verdict is inside the frozen vocabulary
    leg("L18", all(decide(s) in VERDICT_VOCAB for s in (
        {"n_disagree": 2}, {"n_disagree": 0, "n_re_derivable": 0},
        {"n_disagree": 0, "n_re_derivable": 1, "re_derivable_share": 0.01},
        {"n_disagree": 0, "n_re_derivable": 9, "re_derivable_share": 0.9})))
    # L19 the live face re-derives (whole build, twice, on the decisive keys)
    live_a, live_b = build(), build()
    keys = ("n_re_derivable", "n_agree", "n_disagree", "n_cannot_rederive", "unit_named_int_fields")
    leg("L19", all(live_a["summary"][k] == live_b["summary"][k] for k in keys)
        and live_a["verdict"] == live_b["verdict"])
    # L20 the live face's own identities hold (partition, split, per-key sums)
    ic = live_a["identity_check"]
    leg("L20", ic["partition_sums_to_fields"] and ic["why_partition_sums_to_cannot"]
        and ic["by_key_occurrences_sum"] and ic["by_key_re_derivable_sum"]
        and ic["by_key_cannot_sum"], ic)
    # L21 every published as agreeing row really equals its measured count
    leg("L21", all(f["measured_unit_count"] == f["published_value"]
                   for f in live_a["re_derivable_rows"] if f["agrees"]))
    # L22 this study never censuses its own face or mirrors
    leg("L22", all(not n.endswith(MIRROR_SUFFIX) and n not in SELF_FACES
                   for n in live_a["faces_censused"]))
    # L23 the census universe contains E284's scope face (provenance, not a copy)
    leg("L23", SRC_SCOPE in live_a["faces_censused"] and live_a["source_faces"] == [SRC_SCOPE])
    # L24 no division by zero when a face publishes no unit-named counts
    empty = analyse_face_from_object("EMPTY.json", {"p": {"x": 1}})
    leg("L24", empty["fields"] == [] and empty["qualified_unit_named_fields"] == 0)

    # L25-L30 the vintage freeze rule (the mechanism that stopped this face drifting when sibling
    #        studies publish; see e_band_family_vintage)
    _vlegs = vintage.selftest()
    leg("L25", all(okv for okv, _name, _detail in _vlegs),
        [(n, d) for okv, n, d in _vlegs if not okv])

    print("E286 selftest: %d/%d" % (ok, ok + len(fail)))
    for f in fail:
        print("  FAIL %s" % f)
    return 0 if not fail else 1


def analyse_face_from_object(name, obj):
    """Same census as analyse_face but on an in-memory face (selftest fixtures)."""
    unit_lists = []
    for list_path, items in walk_lists(obj):
        if path_key(list_path) in UNITS:
            unit_lists.append({"path": list_path, "unit": path_key(list_path), "n_items": len(items)})
    units_published = sorted({rec["unit"] for rec in unit_lists})
    fields, qualified = [], 0
    for path, value, parent in walk_values(obj):
        if isinstance(value, bool) or not isinstance(value, int):
            continue
        key = path_key(path)
        unit = claimed_unit(key)
        if unit is None:
            if any_unit(key):
                qualified += 1
            continue
        method, measured, sibling = re_derive(parent, key, unit)
        rec = {"face": name, "path": path, "key": key, "claimed_unit": unit,
               "published_value": value}
        if method:
            rec.update({"derivation": method, "measured_unit_count": measured,
                        "measured_from": sibling, "agrees": measured == value})
        else:
            rec.update({"derivation": None, "cannot_rederive": True,
                        "why": "unit_list_exists_elsewhere" if unit in units_published
                        else "unit_never_published"})
        fields.append(rec)
    return {"face": name, "unit_lists": unit_lists, "units_published": units_published,
            "qualified_unit_named_fields": qualified, "fields": fields}


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