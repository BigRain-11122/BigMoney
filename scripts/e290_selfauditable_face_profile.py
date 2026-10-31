"""E290 -- do the few self-auditable faces have a shape worth copying?

E286 measured the date: of 894 unit-named integer counts across 32 dated BAND faces only 27 (3.0 pct)
can be re-derived from the records their name points at, and every one of those 27 counts the unit it
claims.  It could not answer the follow-up a face author actually needs: if I publish a new count the
way those 5 faces do, will my count be checkable?

That question is answerable without drawing anything, because it is a question about SHAPE:

  (1) for every one of the 27 checkable counts, record what sits beside it -- the same-parent list of
      the claimed unit, its length, whether its records are dicts or scalars, how deep the pair sits,
      how many keys its parent carries;
  (2) measure whether that shape is uniform across the 27, and how much of each exemplar face is
      itself checkable (the pattern's own coverage, not just its existence);
  (3) measure the two ways an agreement can be worthless: a count that agrees only because some OTHER
      same-unit list in the same face happens to have the same length (coincidence), and a count whose
      records are scalars so the agreement says nothing about content;
  (4) re-read E286's un-derivable halves as WORK, because they need different fixes: a face that
      already publishes the unit somewhere else needs its count moved into that scope (a naming /
      placement fix, no new data), a face that never publishes the unit at all needs a new record face
      (so no count-naming convention can rescue it).

DECISION RULE, declared before any number is read:

  D1  THE SHAPE IS READ OFF THE PUBLISHED FACE, NOT OFF THE RUNNER.  Every feature is taken from the
      face object as published; the census (which counts are checkable) is imported from E286 rather
      than re-implemented, so this face cannot disagree with the one that defined the question.
  D2  CO-LOCATION IS NOT EVIDENCE; AGREEMENT AND ALTERNATIVES ARE.  A sibling list beside a count
      proves nothing on its own.  Two measurements are published beside every checkable row: does the
      count equal that list's length, and does any OTHER same-unit list in the same face also have
      that length.  A row with an equal-length alternative is published as ambiguous, never as clean.
  D3  RECORD TYPE IS PART OF THE SHAPE, NOT A FOOTNOTE.  A list of dicts carries its own unit
      (one record per row); a list of scalars can carry anything.  The share is published so a reader
      can see whether 'same shape' means the same thing in all 27.
  D4  THE COVERAGE OF THE PATTERN IS MEASURED INSIDE THE EXEMPLARS.  'Follow these five' is only an
      instruction if those five are themselves mostly checkable -- so the per-face checkable share is
      published beside the family-wide 3.0 pct, and a face that is 1-of-40 is not offered as a model.
  D5  THE UN-DERIVABLE HALVES ARE WORK ITEMS WITH DIFFERENT COSTS.  elsewhere-scope (records exist,
      scope does not) and never-published (records absent) are never added into one 'fixable' number.
  D6  NO REBURN.  Published faces are re-read only; no draw stream, no band rebuild, no engine.

Verdict vocabulary (frozen):
  the_checkable_counts_share_a_same_parent_record_list_and_every_agreement_is_unambiguous
  the_checkable_counts_share_a_same_parent_record_list_but_some_agreements_could_be_coincidence
  the_checkable_counts_share_a_same_parent_record_list_but_the_records_are_not_uniformly_typed
  no_count_is_checkable_so_there_is_no_shape_to_copy

Usage:  python scripts/e290_selfauditable_face_profile.py run|verify|selftest
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e286_count_field_scope as e286  # noqa: E402  (the census this face is a profile OF)

ROOT = e286.ROOT
OUTDIR = e286.OUTDIR

STUDY = "E290_selfauditable_face_profile"
TITLE = ("the 27 checkable counts live in 5 faces -- what shape do they share, is that shape uniform, "
         "and if a new face published its counts the same way would the counts be checkable?")
CUTOFF = "2026-10-29"
SRC_FACE = "BANDCOUNTSCOPE-%s.json" % CUTOFF      # E286: the census being profiled
FACE = "BANDSELFAUDIT-%s.json" % CUTOFF
LATEST = "bandselfaudit_latest.json"
SELF_FACES = (FACE, LATEST)

TOL = 1e-12

VERDICT_VOCAB = (
    "the_checkable_counts_share_a_same_parent_record_list_and_every_agreement_is_unambiguous",
    "the_checkable_counts_share_a_same_parent_record_list_but_some_agreements_could_be_coincidence",
    "the_checkable_counts_share_a_same_parent_record_list_but_the_records_are_not_uniformly_typed",
    "no_count_is_checkable_so_there_is_no_shape_to_copy",
)

NO_BILL = ("measurement only: the dated BAND faces are re-read and the counts already published in "
           "E286's census are profiled. No draw stream is drawn, no band rebuilt, no engine runs, no "
           "verdict about the market. A verdict here is a statement about the published numbers, "
           "their names and what sits beside them.")


# ------------------------------------------------------------------ io
def load(name):
    return e286.load(name)


def resolve(obj, path):
    """Resolve a dotted path with [i] indices (as produced by e286.walk_values) to its object."""
    node = obj
    for chunk in str(path).split("."):
        while True:
            head, _, rest = chunk.partition("[")
            if head:
                node = node[head]
            if not rest:
                break
            idx, _, chunk = rest.partition("]")
            node = node[int(idx)]
            chunk = chunk.lstrip(".")
            if not chunk:
                break
    return node


def parent_path(path):
    return str(path).rsplit(".", 1)[0] if "." in str(path) else ""


def face_lists(rec):
    """{unit: [list paths]} from the census record's own list walk."""
    out = {}
    for item in rec.get("unit_lists") or []:
        out.setdefault(item["unit"], []).append(item["path"])
    return out


# ------------------------------------------------------------------ shape of one checkable count
def profile_row(rec, obj, field, lists_by_unit):
    """D1/D2/D3: what sits beside this count, measured on the published face object."""
    unit = field["claimed_unit"]
    pub = field["published_value"]
    sib_path = "%s.%s" % (parent_path(field["path"]), unit) if parent_path(field["path"]) else unit
    try:
        sibling = resolve(obj, sib_path)
    except (KeyError, IndexError, TypeError, ValueError):
        sibling = None
    if not isinstance(sibling, list):
        sibling = None

    others = [p for p in lists_by_unit.get(unit, []) if p != sib_path]
    alt_equal = []
    for path in others:
        try:
            cand = resolve(obj, path)
        except (KeyError, IndexError, TypeError, ValueError):
            continue
        if isinstance(cand, list) and len(cand) == pub:
            alt_equal.append(path)

    records_length = len(sibling) if sibling is not None else None
    n_dict = 0
    if sibling:
        n_dict = len([x for x in sibling if isinstance(x, dict)])
    parent = field["path"].rsplit(".", 1)[0] if "." in field["path"] else ""
    n_parent_keys = None
    try:
        holder = resolve(obj, parent) if parent else obj
        n_parent_keys = len(holder) if isinstance(holder, dict) else None
    except (KeyError, IndexError, TypeError, ValueError):
        n_parent_keys = None

    return {
        "face": rec["face"],
        "path": field["path"],
        "key": field["key"],
        "claimed_unit": unit,
        "published_value": pub,
        "sibling_path": sib_path,
        "sibling_present_same_parent": sibling is not None,
        "records_length": records_length,
        "agrees": field["agrees"],
        "records_total": len(sibling) if sibling is not None else 0,
        "records_dicts": n_dict,
        "records_are_dicts": (n_dict == len(sibling)) if sibling else None,
        "alternative_same_unit_lists": len(others),
        "alternatives_with_equal_length": len(alt_equal),
        "ambiguous": bool(alt_equal),
        "depth_segments": len(str(field["path"]).split(".")),
        "parent_key_count": n_parent_keys,
    }


# ------------------------------------------------------------------ build
def build():
    # E286's universe excludes E286's own faces; this study's face also starts with BAND, so it is
    # filtered here or the face censuses itself on its second run (E209/E211 family, third sighting).
    names = [n for n in e286.face_universe() if n not in SELF_FACES]
    recs = [e286.analyse_face(n) for n in names]
    objs = {rec["face"]: load(rec["face"]) for rec in recs}

    rows = []
    for rec in recs:
        lists_by_unit = face_lists(rec)
        for field in rec["fields"]:
            if field.get("derivation"):
                rows.append(profile_row(rec, objs[rec["face"]], field, lists_by_unit))

    # per-face: how much of each exemplar is itself checkable (D4)
    per_face = []
    for rec in recs:
        n_total = len(rec["fields"])
        n_check = len([f for f in rec["fields"] if f.get("derivation")])
        why = {}
        for f in rec["fields"]:
            if not f.get("derivation"):
                why[f["why"]] = why.get(f["why"], 0) + 1
        per_face.append({
            "face": rec["face"],
            "unit_named_counts": n_total,
            "checkable": n_check,
            "checkable_share": (float(n_check) / n_total) if n_total else None,
            "un_derivable_elsewhere_scope": why.get("unit_list_exists_elsewhere", 0),
            "un_derivable_never_published": why.get("unit_never_published", 0),
        })

    exemplars = [b for b in per_face if b["checkable"]]
    non_exemplars = [b for b in per_face if not b["checkable"]]

    n_total = sum(b["unit_named_counts"] for b in per_face)
    n_check = len(rows)
    n_agree = len([r for r in rows if r["agrees"]])
    n_ambig = len([r for r in rows if r["ambiguous"]])
    n_dict = len([r for r in rows if r["records_are_dicts"]])
    n_scalar = len([r for r in rows if r["records_are_dicts"] is False])
    n_sib = len([r for r in rows if r["sibling_present_same_parent"]])
    face_cover = sum(b["checkable"] for b in exemplars)
    face_counts = sum(b["unit_named_counts"] for b in exemplars)
    ex_share = (float(face_cover) / face_counts) if face_counts else None

    # D5: the two un-derivable halves are work with different costs, never summed into "fixable"
    elsewhere_rows = [f for rec in recs for f in rec["fields"]
                      if f.get("why") == "unit_list_exists_elsewhere"]
    never_rows = [f for rec in recs for f in rec["fields"]
                  if f.get("why") == "unit_never_published"]
    elsewhere_scopes = sorted({"%s :: %s" % (f["face"], parent_path(f["path"])) for f in elsewhere_rows})
    never_keys = sorted({f["key"] for f in never_rows})

    summary = {
        "faces_censused": len(recs),
        "unit_named_counts": n_total,
        "checkable_counts": n_check,
        "checkable_share_family": (float(n_check) / n_total) if n_total else None,
        "exemplar_faces": [b["face"] for b in exemplars],
        "exemplar_faces_n": len(exemplars),
        "exemplar_unit_named_counts": face_counts,
        "exemplar_checkable_counts": face_cover,
        "exemplar_checkable_share": ex_share,
        "n_agree": n_agree,
        "n_disagree": n_check - n_agree,
        "share_sibling_in_same_parent": (float(n_sib) / n_check) if n_check else None,
        "n_records_are_dicts": n_dict,
        "n_records_are_scalars": n_scalar,
        "n_ambiguous": n_ambig,
        "ambiguous_rows": ["%s :: %s" % (r["face"], r["path"]) for r in rows if r["ambiguous"]],
        "per_face_below_the_pattern_floor": [
            {"face": b["face"], "unit_named_counts": b["unit_named_counts"], "checkable": b["checkable"]}
            for b in exemplars if b["checkable_share"] is not None and b["checkable_share"] < 0.5],
        "un_derivable_elsewhere_scope": {
            "n_rows": len(elsewhere_rows),
            "distinct_scopes": len(elsewhere_scopes),
            "statement": "the face already publishes this unit somewhere else: the fix is to move the "
                         "count into that scope (or name the scope it counts), no new data needed",
        },
        "un_derivable_never_published": {
            "n_rows": len(never_rows),
            "distinct_keys": len(never_keys),
            "top_keys": [[k, len([f for f in never_rows if f["key"] == k])]
                         for k in sorted(never_keys,
                                         key=lambda k: -len([f for f in never_rows if f["key"] == k]))[:10]],
            "statement": "the face enumerates no records of this unit at all (draw / seed budgets are "
                         "design parameters), so no naming or placement convention can make these "
                         "counts checkable -- they need a record face, or they stay un-auditable",
        },
        "faces_without_a_checkable_count": len(non_exemplars),
        "calibrated": False,
    }
    verdict = decide(summary)
    summary["verdict"] = verdict

    identity = {
        "checkable_rows_equal_e286_census": None,   # filled below
        "per_face_checkable_sum": sum(b["checkable"] for b in per_face),
        "rows_partition_by_record_type": n_dict + n_scalar == n_check,
        "ambiguous_rows_are_a_subset_of_checkable": all(r["ambiguous"] in ("", None) or
                                                        r["sibling_present_same_parent"] for r in rows),
        "every_checkable_row_has_its_sibling_in_scope": n_sib == n_check,
        "every_checkable_row_agrees_with_its_own_records": all(
            (r["records_length"] == r["published_value"]) for r in rows if r["agrees"]),
        "exemplar_face_set_matches_rows": sorted({r["face"] for r in rows}) ==
                                          sorted(b["face"] for b in exemplars),
        "self_faces_absent_from_universe": all(n not in names for n in SELF_FACES),
        "source_face_present": SRC_FACE in names,
    }
    try:
        src = load(SRC_FACE)
        src_n = ((src.get("summary") or {}).get("n_re_derivable"))
        identity["checkable_rows_equal_e286_census"] = (src_n == n_check)
        identity["e286_n_re_derivable"] = src_n
        identity["e286_unit_named_int_fields"] = (src.get("summary") or {}).get("unit_named_int_fields")
        identity["e286_faces_censused"] = (src.get("summary") or {}).get("faces_censused")
    except (OSError, ValueError, KeyError):
        identity["e286_join_note"] = "source face unreadable; join against the census not run"

    return {
        "study": STUDY, "title": TITLE, "evidence_cutoff": CUTOFF,
        "generated": None,   # stamped by run
        "no_bill": NO_BILL,
        "source_faces": [SRC_FACE],
        "faces_censused": names,
        "frozen_spec": {
            "D1_shape_from_face_census_from_e286": "features are read off the published face object; "
                                                   "which counts are checkable is imported from "
                                                   "E286, never re-implemented",
            "D2_agreement_and_alternatives": "every checkable row publishes whether it equals its own "
                                             "list AND whether another same-unit list in the same "
                                             "face has that length; an equal-length alternative is "
                                             "an ambiguity, not a clean bill",
            "D3_record_type_is_shape": "a list of dicts carries one record per row; a list of scalars "
                                       "can carry anything, so the share is published",
            "D4_pattern_coverage_inside_exemplars": "per-face checkable share is published beside the "
                                                    "family-wide share so 'follow these faces' is an "
                                                    "instruction only where it holds",
            "D5_two_halves_are_different_work": "elsewhere-scope (move the count) versus "
                                                "never-published (needs a record face) are never "
                                                "summed into one fixable number",
            "D6_no_reburn": "published faces re-read only; no draw stream, no band rebuild, no engine",
            "verdict_vocab": list(VERDICT_VOCAB),
        },
        "checkable_rows": rows,
        "per_face": per_face,
        "identity_check": identity,
        "summary": summary,
        "verdict": verdict,
        "verdict_reason": _reason(verdict, summary),
    }


def decide(summary):
    if not summary.get("checkable_counts"):
        return VERDICT_VOCAB[3]
    if summary.get("n_ambiguous"):
        return VERDICT_VOCAB[1]
    if summary.get("n_records_are_scalars"):
        return VERDICT_VOCAB[2]
    return VERDICT_VOCAB[0]


def _fmt_pct(value):
    return "n/a" if value is None else "%.1f pct" % (value * 100.0)


def _reason(verdict, summary):
    if verdict == VERDICT_VOCAB[3]:
        return ("none of the %d unit-named counts in %d face(s) can be re-derived, so there is no "
                "checkable shape in this family to copy."
                % (summary["unit_named_counts"], summary["faces_censused"]))
    head = ("all %d checkable count(s) sit beside a same-parent list of exactly the unit their name "
            "claims (%s), in %d of %d face(s)"
            % (summary["checkable_counts"], _fmt_pct(summary["share_sibling_in_same_parent"]),
               summary["exemplar_faces_n"], summary["faces_censused"]))
    tail = ("following the pattern pays inside the exemplars (%d of %d unit-named counts = %s "
            "checkable) against %s family-wide; the %d un-derivable counts are two different jobs -- "
            "%d rows across %d scopes already publish the unit elsewhere (move the count), %d rows "
            "across %d keys publish no records of that unit at all (a naming convention cannot "
            "rescue them)"
            % (summary["exemplar_checkable_counts"], summary["exemplar_unit_named_counts"],
               _fmt_pct(summary["exemplar_checkable_share"]),
               _fmt_pct(summary["checkable_share_family"]),
               summary["un_derivable_elsewhere_scope"]["n_rows"]
               + summary["un_derivable_never_published"]["n_rows"],
               summary["un_derivable_elsewhere_scope"]["n_rows"],
               summary["un_derivable_elsewhere_scope"]["distinct_scopes"],
               summary["un_derivable_never_published"]["n_rows"],
               summary["un_derivable_never_published"]["distinct_keys"]))
    if verdict == VERDICT_VOCAB[0]:
        return ("%s, every one of them equals its own records, and no other same-unit list in the same "
                "face has that length, so no agreement here can be coincidence. %s." % (head, tail))
    if verdict == VERDICT_VOCAB[1]:
        return ("%s, but %d of them carry an equal-length alternative list of the same unit in the "
                "same face (%s), so those agreements cannot be told from coincidence. %s."
                % (head, summary["n_ambiguous"],
                   ", ".join(summary["ambiguous_rows"][:4]), tail))
    return ("%s, but %d of them sit beside scalar records, so the agreement is about list length and "
            "not about content. %s." % (head, summary["n_records_are_scalars"], tail))


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
    print("E290 %s" % face["verdict"])
    print("  checkable=%d of %d (%s) in %d face(s); agree=%d disagree=%d ambiguous=%d"
          % (s["checkable_counts"], s["unit_named_counts"], _fmt_pct(s["checkable_share_family"]),
             s["exemplar_faces_n"], s["n_agree"], s["n_disagree"], s["n_ambiguous"]))
    print("  sibling_same_parent=%s records: dicts=%d scalars=%d"
          % (_fmt_pct(s["share_sibling_in_same_parent"]), s["n_records_are_dicts"],
             s["n_records_are_scalars"]))
    print("  exemplar coverage: %d of %d = %s (family-wide %s)"
          % (s["exemplar_checkable_counts"], s["exemplar_unit_named_counts"],
             _fmt_pct(s["exemplar_checkable_share"]), _fmt_pct(s["checkable_share_family"])))
    print("  un-derivable: elsewhere=%d rows / %d scopes | never_published=%d rows / %d keys"
          % (s["un_derivable_elsewhere_scope"]["n_rows"],
             s["un_derivable_elsewhere_scope"]["distinct_scopes"],
             s["un_derivable_never_published"]["n_rows"],
             s["un_derivable_never_published"]["distinct_keys"]))
    print("  identity=%s" % face["identity_check"]["checkable_rows_equal_e286_census"])
    return 0


def cmd_verify():
    stored = load(FACE)
    live = build()
    problems = []
    if stored.get("verdict") != live.get("verdict"):
        problems.append("verdict: stored=%r live=%r" % (stored.get("verdict"), live.get("verdict")))
    s_stored, s_live = stored.get("summary") or {}, live.get("summary") or {}
    for key in ("checkable_counts", "unit_named_counts", "n_agree", "n_disagree", "n_ambiguous",
                "n_records_are_dicts", "n_records_are_scalars", "exemplar_checkable_counts",
                "exemplar_unit_named_counts", "ambiguous_rows"):
        if s_stored.get(key) != s_live.get(key):
            problems.append("summary.%s does not re-derive" % key)
    if [("%s :: %s" % (r["face"], r["path"])) for r in (stored.get("checkable_rows") or [])] != \
            [("%s :: %s" % (r["face"], r["path"])) for r in live["checkable_rows"]]:
        problems.append("the checkable row set does not re-derive")
    ic = live["identity_check"]
    for key in ("every_checkable_row_has_its_sibling_in_scope",
                "every_checkable_row_agrees_with_its_own_records",
                "rows_partition_by_record_type", "exemplar_face_set_matches_rows",
                "self_faces_absent_from_universe"):
        if not ic.get(key):
            problems.append("identity check %s is false" % key)
    if not ic.get("checkable_rows_equal_e286_census"):
        problems.append("this face's checkable rows do not join E286's census")
    if s_stored.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the frozen set")
    print("E290 verify: %d problem(s)" % len(problems))
    for problem in problems:
        print("  - %s" % problem)
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
def _fixture():
    return {
        "summary": {"n_rows": 2, "rows": [{"a": 1}, {"a": 2}], "n_cells": 3,
                    "cells": [1, 2, 3], "n_rows_where_x": 9},
        "arms": [{"n_rows": 2, "rows": [{"x": 1}, {"x": 2}], "n_seeds": 5, "seeds": [1, 2]}],
        "tags": {"n_labels": 2, "labels": ["a", "b"], "other": {"labels": ["a", "b"]}},
        "flat": {"cross:200": {"n_rows": 2, "cells": [1, 2, 3]}},
    }


def cmd_selftest():
    ok, fail = 0, []

    def leg(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append("%s %s" % (name, detail))

    fx = _fixture()
    rec = e286.analyse_face_from_object("FIXTURE.json", fx)
    lists_by_unit = face_lists(rec)
    checkable = [f for f in rec["fields"] if f.get("derivation")]

    # L1 the census import is the only source of "checkable" (D1): the fixture's checkable set
    leg("L1", sorted(f["key"] for f in checkable)
        == ["n_cells", "n_labels", "n_rows", "n_rows", "n_seeds"],
        sorted(f["key"] for f in checkable))

    rows = [profile_row(rec, fx, f, lists_by_unit) for f in checkable]
    by_path = {r["path"]: r for r in rows}

    # L2 a same-parent sibling is found and its length is published
    leg("L2", by_path["summary.n_rows"]["sibling_present_same_parent"] is True
        and by_path["summary.n_rows"]["records_length"] == 2
        and by_path["summary.n_rows"]["agrees"] is True)

    # L3 D2: a second same-unit list of the same length is an ambiguity, not a clean bill
    leg("L3", by_path["tags.n_labels"]["ambiguous"] is True
        and by_path["tags.n_labels"]["alternatives_with_equal_length"] >= 1,
        by_path["tags.n_labels"])

    # L4 an alternative elsewhere in the SAME face with the same length is an ambiguity (D2), and the
    # count of alternatives is published rather than silently collapsed to a boolean
    leg("L4", by_path["arms[0].n_rows"]["ambiguous"] is True
        and by_path["arms[0].n_rows"]["alternative_same_unit_lists"] == 1,
        by_path["arms[0].n_rows"])

    # L5 D3: dict records and scalar records are distinguished
    leg("L5", by_path["summary.n_rows"]["records_are_dicts"] is True
        and by_path["tags.n_labels"]["records_are_dicts"] is False,
        (by_path["summary.n_rows"]["records_are_dicts"],
         by_path["tags.n_labels"]["records_are_dicts"]))

    # L6 a count whose sibling is a DIFFERENT unit is never profiled as checkable
    leg("L6", "flat.cross:200.n_rows" not in by_path, sorted(by_path))

    # L7 D4: per-face coverage counts every unit-named count, checkable or not
    face_row = {"face": "FIXTURE.json",
                "unit_named_counts": len(rec["fields"]),
                "checkable": len(checkable)}
    face_row["checkable_share"] = float(face_row["checkable"]) / face_row["unit_named_counts"]
    leg("L7", face_row["checkable"] < face_row["unit_named_counts"] and 0.0 < face_row["checkable_share"] < 1.0,
        face_row)

    # L8 D5 / verdicts: every frozen verdict is reachable and none is silently skipped
    leg("L8", decide({"checkable_counts": 0}) == VERDICT_VOCAB[3]
        and decide({"checkable_counts": 3, "n_ambiguous": 1}) == VERDICT_VOCAB[1]
        and decide({"checkable_counts": 3, "n_ambiguous": 0, "n_records_are_scalars": 2})
        == VERDICT_VOCAB[2]
        and decide({"checkable_counts": 3, "n_ambiguous": 0, "n_records_are_scalars": 0})
        == VERDICT_VOCAB[0])

    # L9 an ambiguous row is only possible when the sibling is present (identity, not decoration)
    leg("L9", all((not r["ambiguous"]) or r["sibling_present_same_parent"] for r in rows))

    # L10 resolve() walks dotted paths with indices
    leg("L10", resolve(fx, "arms[0].rows") == [{"x": 1}, {"x": 2}]
        and resolve(fx, "flat") is fx["flat"])

    # L11 parent_path() never returns a trailing dot
    leg("L11", parent_path("summary.n_rows") == "summary" and parent_path("rows") == ""
        and parent_path("arms[0].n_rows") == "arms[0]")

    # L12 the live face re-derives twice on its decisive keys and stays inside the vocabulary
    a, b = build(), build()
    keys = ("checkable_counts", "n_agree", "n_disagree", "n_ambiguous", "n_records_are_dicts",
            "n_records_are_scalars", "unit_named_counts")
    leg("L12", all(a["summary"][k] == b["summary"][k] for k in keys)
        and a["verdict"] == b["verdict"] and a["verdict"] in VERDICT_VOCAB)

    # L13 the live identity checks hold (join to E286, partition, sibling-in-scope, exemplars)
    ic = a["identity_check"]
    leg("L13", ic["checkable_rows_equal_e286_census"] and ic["rows_partition_by_record_type"]
        and ic["every_checkable_row_has_its_sibling_in_scope"]
        and ic["every_checkable_row_agrees_with_its_own_records"]
        and ic["exemplar_face_set_matches_rows"] and ic["self_faces_absent_from_universe"], ic)

    # L14 every published as-agreeing row really equals its own list's length
    leg("L14", all(r["records_length"] == r["published_value"]
                   for r in a["checkable_rows"] if r["agrees"]))

    # L15 the exemplar coverage is measured, never assumed to be the whole face
    s = a["summary"]
    leg("L15", s["exemplar_checkable_counts"] == s["checkable_counts"]
        and s["exemplar_unit_named_counts"] >= s["checkable_counts"])

    print("E290 selftest: %d/%d" % (ok, ok + len(fail)))
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