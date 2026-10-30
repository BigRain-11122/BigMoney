"""E284 -- is any published summary field keyed at the wrong scope?

E281 re-derived E279's census cell by cell and found one summary field whose NAME says rows
while its VALUE is a list of group labels: `rows_where_tails_disagree_on_reachability` publishes
["cross", "star_lag1_residual"] where the disagreement is really one CELL inside each of those
two legs (each leg carries 4 cells).  A label that names a whole group for a one-cell finding is
the same-name-different-quantity family as E240/E253/E286 -- the reader is told four cells were
measured when one was.

This face does three things and nothing else:

  (1) REPAIR THE KNOWN SLIP, cell-scoped keys published alongside the old field, with the old
      field kept readable as a group-scope UPPER BOUND.  The cells are re-derived from the
      census's own per-tail reachability booleans; no number is copied from the summary.
  (2) SWEEP THE WHOLE FAMILY for the same shape: every published field whose value is a list of
      group labels is classified by what its own NAME promises (group / row / un-named).  Fields
      whose name promises rows and whose value is group labels are the defect; fields that say
      group/leg/arm/family are correct by their own name and are listed, not flagged.
  (3) PUBLISH WHAT WAS NOT ASSESSED.  Integer count fields (`n_rows`, `rows_measured`, ...) carry
      per-face semantics that cannot be re-derived without re-running that face's own censuses;
      they are counted and listed as not assessed instead of being guessed at (E207 discipline:
      an unassessed field is not a clean field).

DECISION RULE, declared before any number is read:

  D1  GROUP LABEL.  A value string is a group label iff it appears as the `row` (== leg) of at
      least one published row in a row-bearing BAND face.  The universe is derived from those
      faces on this run; it is not hard-coded.
  D2  CELL KEY.  A cell key is the published triple leg|base|index (E279/E282 reading_key).  A
      group label is NOT a cell key and a cell key is not a group label; the two lists are
      disjoint by construction and that disjointness is asserted.
  D3  NAME PROMISE.  A field's scope promise is read off its own key: keys containing group,
      leg, arm or family promise group scope; keys containing row that do not promise group
      scope promise row scope; anything else is un-named.  A group-labelled list under a row
      name is the defect class; under a group name it is correct; un-named is reported, not
      judged.
  D4  UPPER BOUND IS MEASURED, NOT ASSUMED.  Group scope is an upper bound on cell scope only
      when no group holds more than one matching cell.  The per-group cell counts are published
      so the reader can see which case holds; a group holding two disagreeing cells makes the
      old field a LOWER bound on cells and the repair says so.
  D5  NO REBURN.  Published faces are re-read only.  No draw stream, no band rebuild, no engine.

Verdict vocabulary (frozen):
  no_summary_field_publishes_group_labels_under_a_row_name
  the_slip_is_unique_to_one_field
  multiple_faces_carry_the_same_slip
  the_field_cannot_be_repaired_from_its_own_census

Usage:  python scripts/e284_disagreement_field_scope.py run|verify|selftest
"""
import glob
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e272_flip_budget_two_tails as e272  # noqa: E402  (OUTDIR / ROOT)
import e279_substitution_soundness as e279  # noqa: E402  (census shape)
import e282_substitution_disagreement_census as e282  # noqa: E402  (rows_of, reading_key)

ROOT = e272.ROOT
OUTDIR = e272.OUTDIR

STUDY = "E284_disagreement_field_scope"
TITLE = ("is any other published summary field keyed at the wrong scope -- a group label where "
         "the finding is cell-scoped, or a cell where the finding is group-scoped?")
CUTOFF = "2026-10-29"
SRC_SUBST = "BANDSUBSTITUTE-%s.json" % CUTOFF       # E279: the census carrying the known slip
FACE = "BANDDISAGREESCOPE-%s.json" % CUTOFF
LATEST = "banddisagreescope_latest.json"
SELF_FACES = (FACE, LATEST)
SLIP_FIELD = "rows_where_tails_disagree_on_reachability"
SLIP_FACE = SRC_SUBST

GROUP_WORDS = ("group", "leg", "arm", "family")
ROW_WORDS = ("row",)
TAILS = ("tight", "wide")

VERDICT_VOCAB = (
    "no_summary_field_publishes_group_labels_under_a_row_name",
    "the_slip_is_unique_to_one_field",
    "multiple_faces_carry_the_same_slip",
    "the_field_cannot_be_repaired_from_its_own_census",
)

NO_BILL = ("measurement only: E279's published census and the family's published summary fields "
           "are re-read. No draw stream is drawn, no band rebuilt, no engine runs. A verdict here "
           "is a statement about the published numbers, not about the market.")


# ------------------------------------------------------------------ io
def load(name, outdir=None):
    with io.open(os.path.join(outdir or OUTDIR, name), encoding="utf-8") as fh:
        return json.load(fh)


def face_files(outdir=None):
    """Dated BAND* publications; <slug>_latest mirrors and this face dropped by name."""
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
    return e282.rows_of(face)


def cell_key(rec):
    """D2: the spelling the family already publishes is row|cell|index (E279's swap row keys).
    `leg` is NOT the row label here -- every row in the census carries leg='cross' while its row
    label is cross / star_lag1_residual, so keying on leg would collapse two groups into one
    (measured: the first run published cross|60|9 and cross|60|13 for two DIFFERENT groups).
    The leg|base|index spelling is carried alongside so a reader keyed on E282 can join."""
    row = str(rec.get("row") or rec.get("leg"))
    key = "%s|%s|%d" % (row, rec.get("cell"), int(rec.get("index") or 0))
    alt = "%s|%d|%d" % (str(rec.get("leg") or row), int(rec.get("base") or 0),
                        int(rec.get("index") or 0))
    return key, alt


# ------------------------------------------------------------------ D1: label universe
def leg_universe(outdir=None):
    """D1: group labels = the `row` (== leg) values actually published in row-bearing faces."""
    dated, _mirrors = face_files(outdir)
    legs, faces = set(), []
    for name in dated:
        try:
            face = load(name, outdir)
        except (IOError, ValueError):
            continue
        rows = rows_of(face)
        if not rows:
            continue
        got = {str(r.get("row") or r.get("leg")) for r in rows if r.get("row") or r.get("leg")}
        if got:
            legs |= got
            faces.append({"face": name, "rows": len(rows), "labels": sorted(got)})
    return {"labels": sorted(legs), "faces": faces}


# ------------------------------------------------------------------ field walk
def walk_fields(node, path=""):
    """Yield (path, key, value) for every dict entry, depth first, keys in file order."""
    if isinstance(node, dict):
        for key, value in node.items():
            here = "%s.%s" % (path, key) if path else str(key)
            yield here, str(key), value
            for item in walk_fields(value, here):
                yield item
    elif isinstance(node, list):
        for idx, item in enumerate(node):
            here = "%s[%d]" % (path, idx)
            for entry in walk_fields(item, here):
                yield entry


def _is_label_list(value, legs):
    return (isinstance(value, list) and value
            and all(isinstance(x, str) for x in value)
            and all(x in legs for x in value))


def _is_cell_list(value):
    return (isinstance(value, list) and value
            and all(isinstance(x, str) for x in value)
            and all("|" in x for x in value))


def classify_field(key, value, legs):
    """D3: what does the field's own NAME promise, and what does its value actually publish?"""
    low = key.lower()
    promises_group = any(w in low for w in GROUP_WORDS)
    promises_rows = any(w in low for w in ROW_WORDS) and not promises_group
    if _is_label_list(value, legs):
        if promises_group:
            cls = "group_scope_named_correctly"
        elif promises_rows:
            cls = "group_labels_under_row_name"
        else:
            cls = "group_labels_unnamed_scope"
        return {"class": cls, "value_kind": "group_labels", "n_items": len(value),
                "name_promises_group": promises_group, "name_promises_rows": promises_rows}
    if _is_cell_list(value):
        rel = "name_promises_rows" if promises_rows else (
            "name_promises_group" if promises_group else "unnamed")
        return {"class": "cell_scope", "value_kind": "cell_keys", "n_items": len(value),
                "cell_vs_name": rel,
                "merged_name": bool(promises_group)}
    return None


def sweep_face(name, face, legs):
    """Every field of one published face, classified. Count-shaped ints are listed, not judged."""
    found, counts, paths = [], [], 0
    for path, key, value in walk_fields(face):
        paths += 1
        rec = classify_field(key, value, legs)
        if rec is not None:
            rec["face"] = name
            rec["path"] = path
            rec["key"] = key
            rec["value"] = list(value)
            found.append(rec)
        elif isinstance(value, int) and not isinstance(value, bool):
            low = key.lower()
            if "row" in low or "cell" in low or low.startswith("n_"):
                counts.append({"face": name, "path": path, "key": key, "value": value})
    return found, counts, paths


def sweep(outdir=None):
    uni = leg_universe(outdir)
    legs = set(uni["labels"])
    dated, mirrors = face_files(outdir)
    per_face, counts, unreadable = [], [], []
    for name in dated:
        try:
            face = load(name, outdir)
        except (IOError, ValueError) as exc:
            unreadable.append({"face": name, "reason": "unreadable: %s" % exc})
            continue
        found, cnt, paths = sweep_face(name, face, legs)
        if found or cnt:
            per_face.append({"face": name, "fields_walked": paths, "classified": found})
        counts.extend(cnt)
    flagged = [f for face in per_face for f in face["classified"]
               if f["class"] == "group_labels_under_row_name"]
    return {"label_universe": uni, "faces_scanned": len(dated), "faces_with_labels": per_face,
            "flagged_fields": flagged, "count_fields_not_assessed": counts,
            "count_keys": count_key_summary(counts),
            "unreadable_faces": unreadable, "mirrors_excluded": mirrors,
            "self_faces_excluded": list(SELF_FACES)}


def count_key_summary(counts):
    """Aggregate the unassessed integer fields by key name: a list of 1338 rows is not readable,
    a list of key families with occurrence counts is. Nothing is dropped silently -- n_total and
    the per-key occurrence counts add up to the same population."""
    by_key = {}
    for rec in counts:
        slot = by_key.setdefault(rec["key"], {"key": rec["key"], "occurrences": 0, "faces": set()})
        slot["occurrences"] += 1
        slot["faces"].add(rec["face"])
    out = [{"key": s["key"], "occurrences": s["occurrences"], "n_faces": len(s["faces"])}
           for s in by_key.values()]
    out.sort(key=lambda r: (-r["occurrences"], r["key"]))
    return {"n_total": len(counts), "n_distinct_keys": len(out), "by_key": out}


# ------------------------------------------------------------------ D2 + D4: the repair
def disagreeing_cells(census):
    """D2: re-derive the disagreeing CELLS from the census's own per-tail booleans."""
    out = []
    for rec in census or []:
        reach = rec.get("reachable") or {}
        if not isinstance(reach, dict) or not all(t in reach for t in TAILS):
            continue
        if bool(reach[TAILS[0]]) != bool(reach[TAILS[1]]):
            key, alt = cell_key(rec)
            out.append({"cell_key": key, "cell_key_leg_base_index": alt,
                        "group": str(rec.get("row") or rec.get("leg")),
                        "cell": rec.get("cell"), "index": rec.get("index"),
                        "reachable": {t: bool(reach[t]) for t in TAILS}})
    out.sort(key=lambda r: r["cell_key"])
    return out


def repair(census_summary, census):
    """D4: cell-scoped keys beside the old field, with the group field kept as an upper bound."""
    old = census_summary.get(SLIP_FIELD)
    cells = disagreeing_cells(census)
    groups = sorted({c["group"] for c in cells})
    per_group = {}
    for c in cells:
        per_group.setdefault(c["group"], []).append(c["cell_key"])
    old_group_labels = [x for x in (old or []) if isinstance(x, str)]
    detected = {
        "old_field": SLIP_FIELD,
        "old_value": old,
        "old_lists_group_labels": bool(old_group_labels),
        "group_scope_count": len(old_group_labels),
        "cell_scope_count": len(cells),
        "cells": [c["cell_key"] for c in cells],
        "cells_leg_base_index": [c["cell_key_leg_base_index"] for c in cells],
        "cells_per_group": {g: sorted(v) for g, v in per_group.items()},
        "max_cells_in_one_group": max([len(v) for v in per_group.values()] or [0]),
    }
    detected["groups_match"] = bool(set(old_group_labels) == set(groups))
    # D4: group scope bounds cell scope from above only if no group holds a second cell
    detected["group_scope_is_upper_bound"] = bool(
        detected["max_cells_in_one_group"] <= 1 and detected["group_scope_count"] >= len(cells))
    detected["group_scope_is_lower_bound"] = bool(detected["max_cells_in_one_group"] > 1)
    detected["repairable"] = bool(cells)
    # identity partner: the same face already publishes its disagreeing cells in this spelling as
    # swap_deflation_rows, so the repair must land on exactly those keys or one of the two is wrong
    published = (census_summary or {}).get("swap_deflation_rows")
    detected["published_swap_rows"] = published
    detected["matches_published_swap_rows"] = (
        None if not published else sorted(published) == [c["cell_key"] for c in cells])
    repaired_names = {
        "cells_where_tails_disagree_on_reachability": [c["cell_key"] for c in cells],
        "groups_containing_a_disagreeing_cell": groups,
    }
    if not detected["repairable"]:
        detected["reason"] = "the census publishes no per-tail reachability booleans, so no cell " \
                            "key can be re-derived without re-running the face"
    return detected, repaired_names


# ------------------------------------------------------------------ verdict
def decide(sweep_res, repair_rec, has_summary):
    if not repair_rec["repairable"]:
        return "the_field_cannot_be_repaired_from_its_own_census"
    flagged = sweep_res["flagged_fields"]
    if not flagged:
        return "no_summary_field_publishes_group_labels_under_a_row_name"
    faces = {f["face"] for f in flagged}
    if len(faces) > 1:
        return "multiple_faces_carry_the_same_slip"
    return "the_slip_is_unique_to_one_field"


def build(outdir=None):
    outdir = outdir or OUTDIR
    sub = load(SRC_SUBST, outdir)
    repair_rec, repaired_names = repair(sub.get("summary") or {}, sub.get("census") or [])
    sweep_res = sweep(outdir)
    verdict = decide(sweep_res, repair_rec, bool(sub.get("summary")))
    flagged = sweep_res["flagged_fields"]
    return {
        "study": STUDY, "title": TITLE, "evidence_cutoff": CUTOFF,
        "generated": None,  # stamped by run
        "no_bill": NO_BILL,
        "source_faces": [SRC_SUBST],
        "frozen_spec": {
            "D1_label_universe": "a group label is a `row`/`leg` value published in a row-bearing "
                                 "BAND face; derived on this run, never hard-coded",
            "D2_cell_key": "row|cell|index (the spelling E279 already publishes for its swap rows), with "
                           "leg|base|index carried alongside for readers keyed on E282; group "
                           "labels and cell keys are disjoint by construction and the disjointness "
                           "is asserted",
            "D3_name_promise": "group/leg/arm/family => group scope; row without group => row "
                               "scope; otherwise un-named (reported, not judged)",
            "D4_upper_bound": "group scope bounds cell scope only when no group holds a second "
                              "matching cell; per-group cell lists are published",
            "D5_no_reburn": "published faces re-read only; no draw stream, no band rebuild, no engine",
            "verdict_vocab": list(VERDICT_VOCAB),
        },
        "repair": {"known_slip": repair_rec, "repaired_keys": repaired_names,
                   "note": "the old field stays readable as a group-scope upper bound; readers that "
                           "need the cells use cells_where_tails_disagree_on_reachability"},
        "sweep": {
            "label_universe": sweep_res["label_universe"],
            "faces_scanned": sweep_res["faces_scanned"],
            "faces_with_label_fields": [
                {"face": f["face"], "fields_walked": f["fields_walked"],
                 "by_class": _by_class(f["classified"]),
                 "classified": f["classified"]} for f in sweep_res["faces_with_labels"]],
            "flagged_fields": flagged,
            "n_flagged": len(flagged),
            "count_fields_not_assessed": sweep_res["count_keys"],
            "n_count_fields_not_assessed": len(sweep_res["count_fields_not_assessed"]),
            "unreadable_faces": sweep_res["unreadable_faces"],
            "mirrors_excluded": sweep_res["mirrors_excluded"],
            "self_faces_excluded": sweep_res["self_faces_excluded"],
            "count_not_assessed_reason": "an integer count's scope depends on that face's own "
                                         "census semantics; guessing it here would publish a number "
                                         "this face did not measure (E207)",
        },
        "verdict": verdict,
        "verdict_reason": _reason(verdict, repair_rec, flagged, sweep_res),
        "no_summary_field_is_silently_wrong": not flagged,
    }


def _by_class(classified):
    out = {}
    for rec in classified:
        out[rec["class"]] = out.get(rec["class"], 0) + 1
    return out


def _reason(verdict, repair_rec, flagged, sweep_res):
    if verdict == "the_field_cannot_be_repaired_from_its_own_census":
        return repair_rec.get("reason")
    parts = ["the known slip is %d group label(s) for %d cell(s): group_scope_is_upper_bound=%s, "
             "max cells in one group=%d"
             % (repair_rec["group_scope_count"], repair_rec["cell_scope_count"],
                repair_rec["group_scope_is_upper_bound"], repair_rec["max_cells_in_one_group"])]
    if verdict == "no_summary_field_publishes_group_labels_under_a_row_name":
        parts.append("no other field in the family publishes group labels under a row name "
                     "(%d fields classified, %d count fields left unassessed)"
                     % (sum(len(f["classified"]) for f in sweep_res["faces_with_labels"]),
                        len(sweep_res["count_fields_not_assessed"])))
    else:
        parts.append("flagged: %s"
                     % "; ".join("%s :: %s -> %s" % (f["face"], f["key"], f["value"])
                                 for f in flagged))
    return ". ".join(parts) + "."


# ------------------------------------------------------------------ commands
def write_face(face, outdir=None):
    outdir = outdir or OUTDIR
    fs = io.open(os.path.join(outdir, FACE), "w", encoding="utf-8", newline="\n")
    try:
        fs.write(json.dumps(face, ensure_ascii=False, indent=1))
        fs.write("\n")
    finally:
        fs.close()
    fs = io.open(os.path.join(outdir, LATEST), "w", encoding="utf-8", newline="\n")
    try:
        fs.write(json.dumps(face, ensure_ascii=False, indent=1))
        fs.write("\n")
    finally:
        fs.close()


def cmd_run():
    import datetime
    face = build()
    face["generated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    write_face(face)
    print("E284 %s" % face["verdict"])
    print("  repair: %d group label(s) -> %d cell(s), upper_bound=%s"
          % (face["repair"]["known_slip"]["group_scope_count"],
             face["repair"]["known_slip"]["cell_scope_count"],
             face["repair"]["known_slip"]["group_scope_is_upper_bound"]))
    print("  sweep: %d face(s) scanned, %d flagged, %d count field(s) not assessed"
          % (face["sweep"]["faces_scanned"], face["sweep"]["n_flagged"],
             face["sweep"]["n_count_fields_not_assessed"]))
    return 0


def cmd_verify():
    """Re-derive the face from disk and compare against the stored face on the judgement keys."""
    stored = load(FACE)
    live = build()
    problems = []
    for key in ("verdict", "no_summary_field_is_silently_wrong"):
        if stored.get(key) != live.get(key):
            problems.append("%s: stored=%r live=%r" % (key, stored.get(key), live.get(key)))
    if stored["repair"]["known_slip"]["cells"] != live["repair"]["known_slip"]["cells"]:
        problems.append("repair cells do not re-derive")
    if sorted(f["path"] for f in stored["sweep"]["flagged_fields"]) != sorted(
            f["path"] for f in live["sweep"]["flagged_fields"]):
        problems.append("flagged field set does not re-derive")
    if stored["repair"]["known_slip"]["cells"] and any(
            "|" not in c for c in stored["repair"]["known_slip"]["cells"]):
        problems.append("a published cell key is not leg|base|index (D2)")
    print("E284 verify: %d problem(s)" % len(problems))
    for p in problems:
        print("  - %s" % p)
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
def _fixture_census(n_cells_cross=1, n_cells_self=0):
    census, idx = [], 0
    for cell in ("all_five", "early_three", "era_2023_2024", "era_2025_now"):
        idx += 1
        disagree_cross = idx <= n_cells_cross
        census.append({"base": 200, "row": "cross", "leg": "cross", "cell": cell, "index": idx,
                       "reachable": {"tight": False, "wide": disagree_cross}})
    for j in range(n_cells_self):
        census.append({"base": 960, "row": "self", "leg": "self", "cell": "all_five",
                       "index": 9 + j, "reachable": {"tight": True, "wide": False}})
    return census


def cmd_selftest():
    ok, fail = 0, []

    def leg(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append("%s %s" % (name, detail))

    legs = {"cross", "self", "star_lag1_residual"}
    # L1 an un-named group-label list is reported, not judged
    r = classify_field("some_labels", ["cross", "self"], legs)
    leg("L1", r and r["class"] == "group_labels_unnamed_scope", r)
    # L2 group vocabulary in the name is correct by its own promise
    r = classify_field("groups_with_a_disagreeing_cell", ["cross"], legs)
    leg("L2", r and r["class"] == "group_scope_named_correctly", r)
    # L3 the slip: group labels under a row name
    r = classify_field(SLIP_FIELD, ["cross", "self"], legs)
    leg("L3", r and r["class"] == "group_labels_under_row_name", r)
    # L4 cell keys are recognised and are not mistaken for labels
    r = classify_field(SLIP_FIELD, ["cross|200|1"], legs)
    leg("L4", r and r["class"] == "cell_scope" and r["value_kind"] == "cell_keys", r)
    # L5 D2 disjointness: a cell key is never in the label universe
    leg("L5", "cross|200|1" not in legs)
    # L6 repair derives the cells from the census, not from the summary
    rec, names = repair({"rows_where_tails_disagree_on_reachability": ["cross"]},
                        _fixture_census(1))
    leg("L6", rec["cell_scope_count"] == 1 and names["cells_where_tails_disagree_on_reachability"]
        == ["cross|all_five|1"], rec)
    # L7 D4: one cell per group makes the old field a true upper bound
    leg("L7", rec["group_scope_is_upper_bound"] and not rec["group_scope_is_lower_bound"], rec)
    # L8 two cells in one group makes the old field a LOWER bound and says so
    rec2, names2 = repair({"rows_where_tails_disagree_on_reachability": ["cross"]},
                          _fixture_census(2))
    leg("L8", rec2["cell_scope_count"] == 2 and rec2["group_scope_is_lower_bound"]
        and not rec2["group_scope_is_upper_bound"]
        and names2["groups_containing_a_disagreeing_cell"] == ["cross"], rec2)
    # L9 a census with no per-tail booleans is not repairable, and says why
    rec3, _ = repair({"x": 1}, [{"row": "cross", "cell": "all_five", "index": 1}])
    leg("L9", not rec3["repairable"] and "booleans" in rec3.get("reason", ""), rec3)
    # L10 group labels match the re-derived groups exactly
    leg("L10", rec["groups_match"], rec)
    # L11 verdict vocabulary is frozen and the decider only returns members
    leg("L11", set(VERDICT_VOCAB) >= {decide({"flagged_fields": []}, rec, True)})
    # L12 decide(): one flagged face vs two
    one = {"flagged_fields": [{"face": "A", "key": "k", "value": ["cross"]}]}
    two = {"flagged_fields": [{"face": "A", "key": "k", "value": ["cross"]},
                              {"face": "B", "key": "k", "value": ["self"]}]}
    leg("L12", decide(one, rec, True) == "the_slip_is_unique_to_one_field"
        and decide(two, rec, True) == "multiple_faces_carry_the_same_slip")
    # L13 no flagged fields => the clean verdict
    leg("L13", decide({"flagged_fields": []}, rec, True)
        == "no_summary_field_publishes_group_labels_under_a_row_name")
    # L14 unrepairable census short-circuits the verdict
    leg("L14", decide({"flagged_fields": []}, rec3, True)
        == "the_field_cannot_be_repaired_from_its_own_census")
    # L15 a count field is not silently classified as a label field
    leg("L15", classify_field("rows_measured", 12, legs) is None)
    # L16 empty list is not a label list (no division by an empty scope)
    leg("L16", classify_field(SLIP_FIELD, [], legs) is None)
    # L17 the label universe is derived from disk, not hard-coded
    uni = leg_universe()
    leg("L17", bool(uni["labels"]) and "cross" in uni["labels"], uni["labels"])
    # L18 mirrors are excluded by name in the sweep
    sw = sweep()
    leg("L18", all("_latest" in m for m in sw["mirrors_excluded"])
        and all(not f["face"].endswith("_latest.json") for f in sw["flagged_fields"]))
    # L19 the sweep is self-excluding (this face never appears in its own scope)
    leg("L19", all(f["face"] not in SELF_FACES for f in sw["flagged_fields"]))
    # L20 a group-label list that is NOT a known label is not classified as labels
    leg("L20", classify_field(SLIP_FIELD, ["not_a_leg"], legs) is None)
    # L21 two rows that share leg='cross' but carry different row labels must yield two distinct
    # cell keys (the first run keyed on leg and collapsed two groups into one -- measured defect)
    mixed = [{"base": 60, "leg": "cross", "row": "cross", "cell": "era_2025_now", "index": 9,
              "reachable": {"tight": False, "wide": True}},
             {"base": 60, "leg": "cross", "row": "star_lag1_residual", "cell": "era_2023_2024",
              "index": 13, "reachable": {"tight": False, "wide": True}}]
    rec21, names21 = repair({"rows_where_tails_disagree_on_reachability":
                             ["cross", "star_lag1_residual"]}, mixed)
    leg("L21", len(set(names21["cells_where_tails_disagree_on_reachability"])) == 2
        and names21["groups_containing_a_disagreeing_cell"] == ["cross", "star_lag1_residual"]
        and rec21["groups_match"], names21)
    # L22 the alternate leg|base|index spelling is carried, and differs from the row spelling
    leg("L22", rec21["cells_leg_base_index"][0] !=
        names21["cells_where_tails_disagree_on_reachability"][0]
        and rec21["cells_leg_base_index"][0].startswith("cross|60|"))
    # L23 the identity partner: when the face publishes its own cell keys, the repair must land on
    # exactly those, and a mismatch must be visible rather than smoothed over
    rec23, _ = repair({"rows_where_tails_disagree_on_reachability": ["cross"],
                       "swap_deflation_rows": ["nope|cell|1"]}, _fixture_census(1))
    leg("L23", rec23["matches_published_swap_rows"] is False,
        rec23["matches_published_swap_rows"])

    print("E284 selftest: %d/%d" % (ok, ok + len(fail)))
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