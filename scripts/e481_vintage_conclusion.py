"""E481 -- do the vintages that differ from their twin also state a different answer?

E478 measured how far a dated vintage is from its family's `*_latest` twin once the frozen clock
names are removed: 145 of the 571 member files still differ.  A byte hash charges a vintage full
price for a changed timestamp; a field-level diff charges it for a changed *row*.  Neither says
whether the two files reach the same conclusion.  That is the retention question this card takes
up: if a vintage states its twin's answer, the bytes are a second writing of one measurement; if
it states a different answer, the bytes are a second measurement and must be kept.

Population: E478's `vintageclock_latest.json` rows classed
`differs_beyond_the_top_level_clock_fields`.  The twin is the reference, never a member.

Primary arm -- the frozen conclusion vocabulary.  A vintage is compared with its twin on every
top-level field the *twin* states whose name is in ``CONCLUSION_NAMES``.  Each vintage lands in
exactly one class:

  same_conclusion_in_different_rows   twin states >=1 conclusion field and every one agrees
  states_a_different_conclusion       twin states >=1 conclusion field and one of them disagrees
  twin_states_no_conclusion_field     the twin states no field in the frozen vocabulary -- the
                                      question cannot be answered for this row, published as
                                      unmeasured, never as a negative
  unreadable_pair                     the member or the twin is missing / does not parse
  twin_not_on_disk                    E478 resolves a twin name that is no longer on disk

Secondary arm -- every top-level scalar the twin states (the card's second clause).  This arm is
published beside the first, never folded into it: it is wider (it compares `study`, `title`,
`path_count`, `evidence_cutoff` ... as well), so it answers "does anything at the surface move",
not "is the conclusion the same".  Where the two arms disagree the primary arm is the verdict and
the secondary arm is the reason a reader should not delete on a scalar-only match alone.

Excluded from both arms: the frozen clock names E478 already forgave, and non-scalar values (a
`rows` list that gained one element is a row difference, which E478 already charged).

Delivered numbers: ``same_conclusion_in_different_rows`` and its share of the comparable set, plus
``bytes_holding_the_same_conclusion`` -- the bytes a conclusion-based retention rule may collapse.
This is a retention estimate under the frozen vocabulary, not a licence to delete: E479 owns
whether a twin is read at all.

CLI: run | check | verify | selftest
"""

import argparse
import io
import json
import os
import re
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "vintageconc_latest.json"
DATED_PREFIX = "VINTAGECONC"
CARD = "E481-DO-THE-VINTAGES-THAT-DIFFER-FROM-THEIR-TWIN-ALSO-STATE-A-DIFFERENT-ANSWER"
PARENT_FACE = "vintageclock_latest.json"      # E478: the 145 differing vintages
SIBLING_FACE = "vintageretire_latest.json"    # E477: the byte-identity floor this refines
POPULATION_CLASS = "differs_beyond_the_top_level_clock_fields"

# Frozen by the card text ("verdict/answer/decision fields").  The face publishes the tuple and a
# per-name histogram of how often each word actually fired, so a reader can see whether the
# vocabulary is measuring anything (E207 family: a name must measure what it counts).
CONCLUSION_NAMES = ("answer", "verdict", "decision", "conclusion", "recommendation", "call",
                    "status", "findings")

# E478's frozen clock names: already forgiven, so they are not a conclusion difference either.
CLOCK_FIELDS = ("generated", "ts", "timestamp", "elapsed_sec")

# Date-shaped names are compared (they are real top-level scalars) but tagged, because a payload
# republished a day later differs on `evidence_cutoff` alone without stating a different answer.
DATE_SHAPED_NOT_A_CONCLUSION = ("evidence_cutoff",)

C_SAME = "same_conclusion_in_different_rows"
C_DIFFERENT = "states_a_different_conclusion"
C_NO_CONCL = "twin_states_no_conclusion_field"
C_UNREADABLE = "unreadable_pair"
C_MISSING_TWIN = "twin_not_on_disk"
COMPARABLE = (C_SAME, C_DIFFERENT)
NOT_COMPARABLE = (C_NO_CONCL, C_UNREADABLE, C_MISSING_TWIN)
CLASSES = COMPARABLE + NOT_COMPARABLE

S_SAME = "every_twin_stated_scalar_agrees"
S_DIFFERENT = "at_least_one_twin_stated_scalar_disagrees"
S_NONE = "the_twin_states_no_scalar"
S_UNREADABLE = "unreadable_pair"
SCALAR_CLASSES = (S_SAME, S_DIFFERENT, S_NONE, S_UNREADABLE)

V_EMPTY = "no_differing_vintage_carries_a_comparable_conclusion"
V_ALL_SAME = "every_differing_vintage_states_its_twins_conclusion_in_different_rows"
V_NONE_SAME = "none_of_the_differing_vintages_states_its_twins_conclusion"
V_MOST_SAME = "most_differing_vintages_state_their_twins_conclusion_and_a_minority_state_a_different_one"
V_SOME_SAME = "some_differing_vintages_state_their_twins_conclusion_and_the_majority_state_a_different_one"
VERDICT_VOCAB = (V_EMPTY, V_ALL_SAME, V_NONE_SAME, V_MOST_SAME, V_SOME_SAME)

TOL = 1e-9


# ----------------------------------------------------------------------------- helpers


def _rel(path, root=None):
    return os.path.relpath(path, root or ROOT).replace("\\", "/")


def _norm(value):
    """A deterministic JSON identity for a scalar (used for exact equality)."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def is_conclusion_name(name):
    return name in CONCLUSION_NAMES


def is_date_shaped(name):
    return name in DATE_SHAPED_NOT_A_CONCLUSION


def is_scalar(value):
    return isinstance(value, (str, int, float, bool)) or value is None


def scalar_kind(name):
    if is_conclusion_name(name):
        return "conclusion_vocabulary"
    if is_date_shaped(name):
        return "date_shaped"
    if name in ("study", "title", "card"):
        return "identity"
    return "other"


def equal_within_tolerance(a, b, tol=TOL):
    """Numeric near-equality, for the robustness block only -- never for the class."""
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if a == b:
            return True
        scale = max(abs(float(a)), abs(float(b)))
        return abs(float(a) - float(b)) <= tol * scale if scale else abs(float(a) - float(b)) <= tol
    return _norm(a) == _norm(b)


MISSING = "<absent in member>"

# A conclusion written as prose usually carries its numbers inside the sentence.  Two vintages can
# say the same thing about the same mechanism and still differ on every digit because the panel
# moved.  The numeric-shape arm is published beside the verdict (never folded into it) so a reader
# can see how much of a "different answer" is a different number rather than a different finding.
_NUM_RE = re.compile(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")


def numeric_shape(text):
    return _NUM_RE.sub("#", text)


def compare_conclusion(member, twin):
    """The primary arm: every frozen-vocabulary field the twin states."""
    fields = []
    for name in sorted(twin):
        if not is_conclusion_name(name):
            continue
        tv = twin[name]
        present = name in member
        mv = member.get(name, MISSING)
        exact = present and _norm(mv) == _norm(tv)
        shape_equal = (bool(present) and isinstance(mv, str) and isinstance(tv, str)
                       and numeric_shape(mv) == numeric_shape(tv))
        fields.append({
            "name": name,
            "member_present": present,
            "equal": exact,
            "equal_within_tolerance": bool(present) and equal_within_tolerance(mv, tv),
            "equal_after_numeric_shape_collapse": shape_equal,
            "twin_value_kind": "scalar" if is_scalar(tv) else "non_scalar",
            "member_value_prefix": (mv if isinstance(mv, str) else _norm(mv))[:160]
            if present else None,
            "twin_value_prefix": (tv if isinstance(tv, str) else _norm(tv))[:160]
            if is_scalar(tv) else None,
        })
    return fields


def compare_scalars(member, twin):
    """The secondary arm: every top-level scalar the twin states, frozen clock names excluded."""
    fields = []
    for name in sorted(twin):
        if name in CLOCK_FIELDS:
            continue
        tv = twin[name]
        if not is_scalar(tv):
            continue
        present = name in member
        mv = member.get(name, MISSING)
        fields.append({
            "name": name,
            "kind": scalar_kind(name),
            "member_present": present,
            "equal": bool(present) and _norm(mv) == _norm(tv),
            "equal_within_tolerance": bool(present) and equal_within_tolerance(mv, tv),
        })
    return fields


def classify_pair(member_path, twin_path, read):
    """Classify one vintage against its twin.  Returns a row dict (path filled by the caller)."""
    try:
        member = read(member_path)
        twin = read(twin_path)
    except Exception:
        return {"class": C_UNREADABLE, "scalar_arm_class": S_UNREADABLE,
                "conclusion_fields": [], "scalar_fields": []}
    if not isinstance(member, dict) or not isinstance(twin, dict):
        return {"class": C_UNREADABLE, "scalar_arm_class": S_UNREADABLE,
                "conclusion_fields": [], "scalar_fields": []}

    concl = compare_conclusion(member, twin)
    scalars = compare_scalars(member, twin)

    if not concl:
        cls = C_NO_CONCL
    elif all(f["equal"] for f in concl):
        cls = C_SAME
    else:
        cls = C_DIFFERENT

    if not scalars:
        scls = S_NONE
    elif all(f["equal"] for f in scalars):
        scls = S_SAME
    else:
        scls = S_DIFFERENT

    differing_concl = [f["name"] for f in concl if not f["equal"]]
    differing_scalars = [f for f in scalars if not f["equal"]]
    kinds = {}
    for f in differing_scalars:
        kinds[f["kind"]] = kinds.get(f["kind"], 0) + 1
    numeric_only = [f["name"] for f in concl
                    if not f["equal"] and f["equal_after_numeric_shape_collapse"]]

    return {
        "class": cls,
        "scalar_arm_class": scls,
        "conclusion_fields": concl,
        "scalar_fields": scalars,
        "conclusion_field_names": [f["name"] for f in concl],
        "differing_conclusion_names": differing_concl,
        "differing_conclusion_names_that_only_move_within_tolerance": [
            f["name"] for f in concl if not f["equal"] and f["equal_within_tolerance"]],
        "differing_conclusion_names_that_only_move_in_their_numbers": numeric_only,
        "conclusion_difference_is_numeric_shape_only": (
            bool(differing_concl) and len(numeric_only) == len(differing_concl)),
        "twin_scalar_fields": len(scalars),
        "differing_scalar_names": [f["name"] for f in differing_scalars],
        "differing_scalar_kind_counts": dict(sorted(kinds.items())),
        "only_difference_is_a_date_shaped_name": (
            bool(differing_scalars) and all(is_date_shaped(f["name"]) for f in differing_scalars)),
    }


def classify(rows_by_family, read, exists, size_of, rel):
    """rows_by_family: {family_key: {'members': [...], 'twin': path or None}}"""
    rows = []
    families = []
    counts = {c: 0 for c in CLASSES}
    byte_counts = {c: 0 for c in CLASSES}
    scalar_counts = {c: 0 for c in SCALAR_CLASSES}
    cross = {}
    vocab = {n: {"twins_stating_it": 0, "agreements": 0, "differences": 0} for n in CONCLUSION_NAMES}
    kind_hist = {}

    for fam_key in sorted(rows_by_family):
        fam = rows_by_family[fam_key]
        twin = fam.get("twin")
        twin_ok = bool(twin) and exists(twin)
        fam_counts = {c: 0 for c in CLASSES}
        fam_bytes = 0
        for member in sorted(fam.get("members") or []):
            try:
                size = size_of(member)
            except OSError:
                size = 0
            if not exists(member) or not twin_ok:
                res = {"class": C_MISSING_TWIN if twin_ok or not twin else C_MISSING_TWIN,
                       "scalar_arm_class": S_UNREADABLE,
                       "conclusion_fields": [], "scalar_fields": []}
            else:
                res = classify_pair(member, twin, read)
            counts[res["class"]] += 1
            byte_counts[res["class"]] += size
            fam_counts[res["class"]] += 1
            fam_bytes += size
            scalar_counts[res["scalar_arm_class"]] += 1
            key = "%s|%s" % (res["class"], res["scalar_arm_class"])
            cross[key] = cross.get(key, 0) + 1
            for f in res.get("conclusion_fields") or []:
                v = vocab[f["name"]]
                v["twins_stating_it"] += 1
                if f["equal"]:
                    v["agreements"] += 1
                else:
                    v["differences"] += 1
            for k, n in (res.get("differing_scalar_kind_counts") or {}).items():
                kind_hist[k] = kind_hist.get(k, 0) + n
            rows.append({
                "path": rel(member),
                "family": fam_key,
                "twin": rel(twin) if twin else None,
                "bytes": size,
                "class": res["class"],
                "scalar_arm_class": res["scalar_arm_class"],
                "conclusion_field_names": res.get("conclusion_field_names") or [],
                "differing_conclusion_names": res.get("differing_conclusion_names") or [],
                "differing_conclusion_names_that_only_move_within_tolerance": (
                    res.get("differing_conclusion_names_that_only_move_within_tolerance") or []),
                "differing_conclusion_names_that_only_move_in_their_numbers": (
                    res.get("differing_conclusion_names_that_only_move_in_their_numbers") or []),
                "conclusion_difference_is_numeric_shape_only": (
                    res.get("conclusion_difference_is_numeric_shape_only")),
                "twin_scalar_fields": res.get("twin_scalar_fields"),
                "differing_scalar_names": res.get("differing_scalar_names") or [],
                "differing_scalar_kind_counts": res.get("differing_scalar_kind_counts") or {},
                "only_difference_is_a_date_shaped_name": res.get("only_difference_is_a_date_shaped_name"),
                "conclusion_fields": res.get("conclusion_fields") or [],
            })
        families.append({
            "family": fam_key,
            "twin": rel(twin) if twin else None,
            "twin_present": twin_ok,
            "members": len(fam.get("members") or []),
            "counts": fam_counts,
            "bytes": fam_bytes,
        })

    return rows, families, counts, byte_counts, scalar_counts, cross, vocab, kind_hist


def _expect_verdict(counts):
    comparable = counts.get(C_SAME, 0) + counts.get(C_DIFFERENT, 0)
    same = counts.get(C_SAME, 0)
    if comparable == 0:
        return V_EMPTY
    if same == comparable:
        return V_ALL_SAME
    if same == 0:
        return V_NONE_SAME
    if same * 2 > comparable:
        return V_MOST_SAME
    return V_SOME_SAME


# ----------------------------------------------------------------------------- build


def build(pop_path=None):
    pop = json.load(io.open(pop_path or os.path.join(OUTDIR, PARENT_FACE), "r", encoding="utf-8"))
    sibling = None
    sib_path = os.path.join(OUTDIR, SIBLING_FACE)
    if os.path.exists(sib_path):
        try:
            sibling = json.load(io.open(sib_path, "r", encoding="utf-8"))
        except Exception:
            sibling = None

    twins_by_family = {}
    for f in pop.get("families") or []:
        twins_by_family[f.get("family")] = f.get("twin")

    rows_by_family = {}
    missing_twin_names = []
    for r in pop.get("rows") or []:
        if r.get("class") != POPULATION_CLASS:
            continue
        fam = "%s/%s" % (r.get("dir", "?") if r.get("dir") is not None else r.get("family", "?").rsplit("/", 1)[0],
                         r.get("family", "?").rsplit("/", 1)[-1])
        fam_key = r.get("family") or fam
        twin_rel = r.get("twin") or twins_by_family.get(fam_key)
        twin_abs = None
        if twin_rel:
            twin_abs = twin_rel if os.path.isabs(twin_rel) else os.path.join(ROOT, twin_rel)
            if not os.path.exists(twin_abs):
                missing_twin_names.append(twin_rel)
                twin_abs = None
        member = r.get("path")
        member_abs = member if os.path.isabs(member) else os.path.join(ROOT, member)
        slot = rows_by_family.setdefault(fam_key, {"members": [], "twin": twin_abs})
        if slot.get("twin") is None and twin_abs:
            slot["twin"] = twin_abs
        slot["members"].append(member_abs)

    rows, families, counts, byte_counts, scalar_counts, cross, vocab, kind_hist = classify(
        rows_by_family,
        lambda p: json.load(io.open(p, "r", encoding="utf-8")),
        os.path.exists,
        os.path.getsize,
        _rel,
    )

    comparable = counts[C_SAME] + counts[C_DIFFERENT]
    same = counts[C_SAME]
    verdict = _expect_verdict(counts)
    summary = {
        "population_card": CARD,
        "population_source_class": POPULATION_CLASS,
        "member_files": len(rows),
        "families": len(families),
        "class_counts": counts,
        "class_bytes": byte_counts,
        "comparable_files": comparable,
        "same_conclusion_in_different_rows": same,
        "same_conclusion_share_of_comparable": round(same / comparable, 6) if comparable else None,
        "bytes_holding_the_same_conclusion": byte_counts[C_SAME],
        "bytes_holding_a_different_conclusion": byte_counts[C_DIFFERENT],
        "scalar_arm_class_counts": scalar_counts,
        "arm_cross_tab": dict(sorted(cross.items())),
        "conclusion_vocabulary": list(CONCLUSION_NAMES),
        "conclusion_vocabulary_histogram": vocab,
        "differing_scalar_kind_histogram": dict(sorted(kind_hist.items(), key=lambda kv: -kv[1])),
        "twins_named_but_missing_on_disk": len(missing_twin_names),
        "e477_bytes_lost_if_retired": ((sibling or {}).get("summary") or {}).get("bytes_lost_if_retired"),
        "e478_comparable_files": ((pop.get("summary") or {}).get("comparable_files")),
        "robustness": {
            "rows_whose_only_differing_scalar_is_a_date_shaped_name": sum(
                1 for r in rows if r.get("only_difference_is_a_date_shaped_name")),
            "rows_whose_conclusion_difference_is_within_float_tolerance": sum(
                1 for r in rows if r.get("class") == C_DIFFERENT
                and len(r.get("differing_conclusion_names") or [])
                == len(r.get("differing_conclusion_names_that_only_move_within_tolerance") or [])),
            "rows_whose_conclusion_difference_is_numeric_shape_only": sum(
                1 for r in rows if r.get("conclusion_difference_is_numeric_shape_only")),
            "bytes_whose_conclusion_difference_is_numeric_shape_only": sum(
                r.get("bytes", 0) for r in rows if r.get("conclusion_difference_is_numeric_shape_only")),
            "rows_classed_no_conclusion_that_state_top_level_scalars": sum(
                1 for r in rows if r.get("class") == C_NO_CONCL and (r.get("twin_scalar_fields") or 0) > 0),
            "date_shaped_names_not_treated_as_conclusions": list(DATE_SHAPED_NOT_A_CONCLUSION),
            "note": "the frozen vocabulary decides the verdict; this block only says whether a row "
                    "that looks like a conclusion difference is a date move, a float repr move, or "
                    "the same sentence with updated numbers",
        },
    }

    face = {
        "card": CARD,
        "study": "E481_do_the_vintages_that_differ_from_their_twin_also_state_a_different_answer",
        "title": "do the vintages that differ from their twin also state a different answer?",
        "evidence_cutoff": time.strftime("%Y-%m-%d"),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "frozen_conclusion_fields": list(CONCLUSION_NAMES),
        "frozen_clock_fields_excluded": list(CLOCK_FIELDS),
        "population_source": {
            "face": PARENT_FACE,
            "face_verdict": pop.get("verdict"),
            "face_evidence_cutoff": pop.get("evidence_cutoff"),
            "class_taken": POPULATION_CLASS,
            "sibling_face": SIBLING_FACE,
            "twin_excluded_from_population": True,
        },
        "class_definition": {
            C_SAME: "the twin states >=1 frozen conclusion field and the member states every one "
                    "of them with an equal value; the difference lies outside the conclusion",
            C_DIFFERENT: "the twin states >=1 frozen conclusion field and at least one disagrees",
            C_NO_CONCL: "the twin states no field in the frozen conclusion vocabulary: unmeasured, "
                        "never a negative",
            C_UNREADABLE: "the member or the twin is missing on disk or does not parse as a JSON object",
            C_MISSING_TWIN: "E478 resolved a twin name for this family that is no longer on disk",
        },
        "summary": summary,
        "verdict": verdict,
        "verdict_vocab": list(VERDICT_VOCAB),
        "families": families,
        "rows": rows,
        "method_limits": [
            "the conclusion vocabulary is eight frozen names; a face that states its answer under a "
            "name outside the tuple reads as twin_states_no_conclusion_field (unmeasured, not equal)",
            "only the twin's fields are compared -- a field the member states and the twin does not "
            "is a difference E478 already recorded and is not re-charged here",
            "scalar equality is exact JSON identity; the robustness block counts rows whose only "
            "conclusion disagreement is a float repr difference or the same prose with different "
            "numbers",
            "the numeric-shape arm collapses every number to '#', so a row it calls shape-equal may "
            "still state a different magnitude -- that is the point: it separates 'different number' "
            "from 'different finding' without deciding which one a reader wants",
            "non-scalar values are not compared in either arm, so a vintage whose only change is one "
            "element inside a `rows` list lands in same_conclusion (E478 already charged it as a row "
            "difference, and this face is about the answer, not the rows)",
            "same-conclusion bytes are a retention estimate under the frozen vocabulary, not a "
            "deletion licence: E479 owns whether the twin is read at all",
        ],
    }
    return face


# ----------------------------------------------------------------------------- guards


def row_problems(face):
    """Every tally must re-add to the rows; injected verbatim into the smoke leg."""
    problems = []
    s = face.get("summary") or {}
    rows = face.get("rows") or []
    counts = s.get("class_counts") or {}
    if set(counts) != set(CLASSES):
        problems.append("class_counts keys are not the published class set: %r" % sorted(counts))
    if sum(counts.values()) != s.get("member_files"):
        problems.append("class counts do not sum to member_files")
    if len(rows) != s.get("member_files"):
        problems.append("row count %d != member_files %r" % (len(rows), s.get("member_files")))
    if sum((s.get("class_bytes") or {}).values()) != sum(r.get("bytes", 0) for r in rows):
        problems.append("class bytes do not sum to the row bytes")

    derived = {c: 0 for c in CLASSES}
    derived_bytes = {c: 0 for c in CLASSES}
    scalar_counts = {c: 0 for c in SCALAR_CLASSES}
    cross = {}
    vocab = {n: {"twins_stating_it": 0, "agreements": 0, "differences": 0} for n in CONCLUSION_NAMES}
    kind_hist = {}
    for r in rows:
        cls = r.get("class")
        if cls not in CLASSES:
            problems.append("row %s carries a class outside the set" % r.get("path"))
            break
        derived[cls] += 1
        derived_bytes[cls] += r.get("bytes", 0)
        scls = r.get("scalar_arm_class")
        if scls not in SCALAR_CLASSES:
            problems.append("row %s carries a scalar-arm class outside the set" % r.get("path"))
            break
        scalar_counts[scls] += 1
        key = "%s|%s" % (cls, scls)
        cross[key] = cross.get(key, 0) + 1
        names = r.get("conclusion_field_names") or []
        if cls == C_SAME and (not names or r.get("differing_conclusion_names")):
            problems.append("row %s is same-conclusion but has no field or names a differing one"
                            % r.get("path"))
            break
        if cls == C_DIFFERENT and not r.get("differing_conclusion_names"):
            problems.append("row %s differs on the conclusion but names no differing field"
                            % r.get("path"))
            break
        if cls == C_NO_CONCL and names:
            problems.append("row %s states no conclusion but lists conclusion fields" % r.get("path"))
            break
        if cls == C_UNREADABLE and (names or (r.get("twin_scalar_fields") or 0)):
            problems.append("row %s is unreadable yet carries a comparison" % r.get("path"))
            break
        if cls in (C_SAME, C_DIFFERENT, C_NO_CONCL) and not r.get("twin"):
            problems.append("row %s was compared but names no twin" % r.get("path"))
            break
        for f in r.get("conclusion_fields") or []:
            if f.get("name") not in CONCLUSION_NAMES:
                problems.append("row %s compares a field outside the frozen vocabulary: %r"
                                % (r.get("path"), f.get("name")))
                break
            v = vocab[f["name"]]
            v["twins_stating_it"] += 1
            if f.get("equal"):
                v["agreements"] += 1
            else:
                v["differences"] += 1
        for k, n in (r.get("differing_scalar_kind_counts") or {}).items():
            kind_hist[k] = kind_hist.get(k, 0) + n

    if derived != counts:
        problems.append("the published class counts do not re-derive from the rows")
    if derived_bytes != (s.get("class_bytes") or {}):
        problems.append("the published class bytes do not re-derive from the rows")
    if scalar_counts != (s.get("scalar_arm_class_counts") or {}):
        problems.append("the scalar-arm counts do not re-derive from the rows")
    if cross != (s.get("arm_cross_tab") or {}):
        problems.append("the arm cross-tab does not re-derive from the rows")
    if vocab != (s.get("conclusion_vocabulary_histogram") or {}):
        problems.append("the vocabulary histogram does not re-derive from the rows")
    if dict(sorted(kind_hist.items(), key=lambda kv: -kv[1])) != (s.get("differing_scalar_kind_histogram") or {}):
        problems.append("the differing-scalar kind histogram does not re-derive from the rows")
    if s.get("comparable_files") != derived.get(C_SAME, 0) + derived.get(C_DIFFERENT, 0):
        problems.append("the comparable tally is not same + different")
    if s.get("same_conclusion_in_different_rows") != derived.get(C_SAME):
        problems.append("the same-conclusion tally does not re-derive from the rows")
    if s.get("bytes_holding_the_same_conclusion") != derived_bytes.get(C_SAME):
        problems.append("the same-conclusion bytes do not re-derive from the rows")
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict is outside the frozen vocabulary: %r" % face.get("verdict"))
    if face.get("verdict") != _expect_verdict(counts):
        problems.append("verdict %r is not the one the counts imply (%r)"
                        % (face.get("verdict"), _expect_verdict(counts)))
    fam_sum = sum(f.get("members", 0) for f in face.get("families") or [])
    if fam_sum != s.get("member_files"):
        problems.append("family member counts do not sum to member_files")

    rob = s.get("robustness") or {}
    if rob:
        differs = [r for r in rows if r.get("class") == C_DIFFERENT]
        if rob.get("rows_whose_only_differing_scalar_is_a_date_shaped_name") != sum(
                1 for r in rows if r.get("only_difference_is_a_date_shaped_name")):
            problems.append("the date-shaped-only tally does not re-derive from the rows")
        if rob.get("rows_whose_conclusion_difference_is_within_float_tolerance") != sum(
                1 for r in differs
                if len(r.get("differing_conclusion_names") or [])
                == len(r.get("differing_conclusion_names_that_only_move_within_tolerance") or [])):
            problems.append("the float-tolerance tally does not re-derive from the rows")
        if rob.get("rows_whose_conclusion_difference_is_numeric_shape_only") != sum(
                1 for r in rows if r.get("conclusion_difference_is_numeric_shape_only")):
            problems.append("the numeric-shape tally does not re-derive from the rows")
        if rob.get("bytes_whose_conclusion_difference_is_numeric_shape_only") != sum(
                r.get("bytes", 0) for r in rows if r.get("conclusion_difference_is_numeric_shape_only")):
            problems.append("the numeric-shape bytes do not re-derive from the rows")
        if any(r.get("conclusion_difference_is_numeric_shape_only") and r.get("class") != C_DIFFERENT
               for r in rows):
            problems.append("a row claims a numeric-shape conclusion difference but is not classed differing")
        if rob.get("rows_classed_no_conclusion_that_state_top_level_scalars") != sum(
                1 for r in rows if r.get("class") == C_NO_CONCL
                and (r.get("twin_scalar_fields") or 0) > 0):
            problems.append("the no-conclusion-but-scalars tally does not re-derive from the rows")
    return problems


def check(face=None):
    face = face or json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    return row_problems(face)


def verify():
    published = json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    fresh = build()
    problems = []
    ps, fs = published.get("summary") or {}, fresh.get("summary") or {}
    for key in ("member_files", "families", "class_counts", "class_bytes", "comparable_files",
                "same_conclusion_in_different_rows", "bytes_holding_the_same_conclusion",
                "scalar_arm_class_counts", "arm_cross_tab", "conclusion_vocabulary_histogram",
                "differing_scalar_kind_histogram", "twins_named_but_missing_on_disk"):
        if ps.get(key) != fs.get(key):
            problems.append("%s: published %r != fresh %r" % (key, ps.get(key), fs.get(key)))
    if published.get("verdict") != fresh.get("verdict"):
        problems.append("verdict: published %r != fresh %r"
                        % (published.get("verdict"), fresh.get("verdict")))
    return problems


def run(face=None):
    face = face or build()
    os.makedirs(OUTDIR, exist_ok=True)
    dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"]))
    latest = os.path.join(OUTDIR, FACE_NAME)
    compact = json.dumps(face, ensure_ascii=False, sort_keys=True)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(compact + "\n")
    problems = check(face)
    print(json.dumps({"face": _rel(latest), "dated": _rel(dated),
                      "summary": {k: face["summary"][k] for k in (
                          "member_files", "comparable_files", "class_counts",
                          "same_conclusion_in_different_rows",
                          "same_conclusion_share_of_comparable",
                          "bytes_holding_the_same_conclusion",
                          "differing_scalar_kind_histogram")},
                      "verdict": face["verdict"], "problems": problems},
                     ensure_ascii=False, sort_keys=True))
    return 0 if not problems else 1


# ----------------------------------------------------------------------------- selftest


def selftest():
    tmp = tempfile.mkdtemp(prefix="e481_")
    fails = []

    def want(name, got, expect):
        if got != expect:
            fails.append("%s: got %r want %r" % (name, got, expect))

    try:
        def w(path, obj):
            d = os.path.dirname(path)
            if d and not os.path.isdir(d):
                os.makedirs(d)
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(obj if isinstance(obj, str) else json.dumps(obj, sort_keys=True))

        base = os.path.join(tmp, "results", "fam")
        twin = os.path.join(base, "FAM_latest.json")
        rows_doc = [{"d": 1}, {"d": 2}]
        w(twin, {"answer": "same", "verdict": "PASS", "study": "E1", "title": "t",
                 "evidence_cutoff": "2026-02-02", "generated": "2026-02-02T00:00",
                 "rows": rows_doc, "cells": 7})

        # 1: same conclusion, different rows (rows list grew -> E478 charged it; conclusion agrees)
        a = os.path.join(base, "FAM-2026-01-01.json")
        w(a, {"answer": "same", "verdict": "PASS", "study": "E1", "title": "t",
              "evidence_cutoff": "2026-02-02", "generated": "2026-01-01T00:00",
              "rows": rows_doc + [{"d": 3}], "cells": 7})
        # 2: different conclusion
        b = os.path.join(base, "FAM-2026-01-02.json")
        w(b, {"answer": "different", "verdict": "PASS", "study": "E1", "title": "t",
              "evidence_cutoff": "2026-02-02", "generated": "2026-01-02T00:00",
              "rows": rows_doc, "cells": 7})
        # 3: twin states no conclusion vocabulary name at all
        twin2 = os.path.join(base, "NOV_latest.json")
        w(twin2, {"study": "E2", "title": "t2", "evidence_cutoff": "2026-02-02", "cells": 1})
        c = os.path.join(base, "NOV-2026-01-03.json")
        w(c, {"study": "E2", "title": "t2", "evidence_cutoff": "2026-02-02", "cells": 2})
        # 4: only difference is the date-shaped name (must still be same conclusion)
        d = os.path.join(base, "FAM-2026-01-04.json")
        w(d, {"answer": "same", "verdict": "PASS", "study": "E1", "title": "t",
              "evidence_cutoff": "2026-02-09", "generated": "2026-01-04T00:00",
              "rows": rows_doc, "cells": 7})
        # 5: does not parse
        e = os.path.join(base, "FAM-2026-01-05.json")
        w(e, "{not json")
        # 6: the same sentence with a different number -- still a different answer by the frozen
        #    definition, but the numeric-shape arm must separate it from a different finding
        twin3 = os.path.join(base, "NUM_latest.json")
        w(twin3, {"answer": "the band holds at 12.5 bp over 2026", "study": "E3"})
        g = os.path.join(base, "NUM-2026-01-06.json")
        w(g, {"answer": "the band holds at 14.25 bp over 2026", "study": "E3"})

        rows_by_family = {
            "fam/FAM": {"members": [a, b, d, e], "twin": twin},
            "fam/NOV": {"members": [c], "twin": twin2},
            "fam/NUM": {"members": [g], "twin": twin3},
        }
        rows, families, counts, byte_counts, scalar_counts, cross, vocab, kind_hist = classify(
            rows_by_family,
            lambda p: json.load(io.open(p, "r", encoding="utf-8")),
            os.path.exists, os.path.getsize, lambda p: os.path.basename(p))

        want("same count", counts[C_SAME], 2)          # a and d
        want("different count", counts[C_DIFFERENT], 2)  # b and g
        want("no-conclusion count", counts[C_NO_CONCL], 1)
        want("unreadable count", counts[C_UNREADABLE], 1)
        want("class sum", sum(counts.values()), 6)
        want("comparable", counts[C_SAME] + counts[C_DIFFERENT], 4)
        want("same bytes", byte_counts[C_SAME],
             os.path.getsize(a) + os.path.getsize(d))
        want("verdict some same", _expect_verdict(counts), V_SOME_SAME)

        by = {os.path.basename(r["path"]): r for r in rows}
        want("a class", by["FAM-2026-01-01.json"]["class"], C_SAME)
        want("a names both conclusion fields",
             by["FAM-2026-01-01.json"]["conclusion_field_names"], ["answer", "verdict"])
        want("b names the differing field",
             by["FAM-2026-01-02.json"]["differing_conclusion_names"], ["answer"])
        want("b scalar arm agrees (title/study/cells all equal)",
             by["FAM-2026-01-02.json"]["scalar_arm_class"], S_DIFFERENT)
        want("d differs only on the date-shaped name",
             (by["FAM-2026-01-04.json"]["class"],
              by["FAM-2026-01-04.json"]["only_difference_is_a_date_shaped_name"]), (C_SAME, True))
        want("d differing scalar names", by["FAM-2026-01-04.json"]["differing_scalar_names"],
             ["evidence_cutoff"])
        want("c is no-conclusion but states scalars",
             (by["NOV-2026-01-03.json"]["class"],
              by["NOV-2026-01-03.json"]["twin_scalar_fields"]), (C_NO_CONCL, 4))
        want("c scalar arm differs on cells",
             by["NOV-2026-01-03.json"]["differing_scalar_names"], ["cells"])
        want("g differs only in its numbers",
             (by["NUM-2026-01-06.json"]["class"],
              by["NUM-2026-01-06.json"]["conclusion_difference_is_numeric_shape_only"]),
             (C_DIFFERENT, True))
        want("b differs in the word, not just the number",
             by["FAM-2026-01-02.json"]["conclusion_difference_is_numeric_shape_only"], False)
        want("numeric shape collapses digits, keeps prose",
             numeric_shape("a 12.5 bp rise in 2026"), "a # bp rise in #")
        want("unreadable carries no comparison", by["FAM-2026-01-05.json"]["conclusion_field_names"], [])
        want("vocabulary histogram counts the twins that state the word",
             (vocab["answer"]["twins_stating_it"], vocab["answer"]["agreements"],
              vocab["answer"]["differences"]), (4, 2, 2))
        want("vocabulary never claims a word no twin stated", vocab["status"]["twins_stating_it"], 0)
        want("kind histogram counts the date move", kind_hist.get("date_shaped"), 1)
        want("kind histogram counts the non-conclusion scalar move", kind_hist.get("other"), 1)
        want("family twin flags", [f["twin_present"] for f in families], [True, True, True])

        # verdict arithmetic
        empty = {c: 0 for c in CLASSES}
        want("verdict empty", _expect_verdict(empty), V_EMPTY)
        want("verdict all same", _expect_verdict(dict(empty, **{C_SAME: 3})), V_ALL_SAME)
        want("verdict none same", _expect_verdict(dict(empty, **{C_DIFFERENT: 3})), V_NONE_SAME)
        want("verdict most same", _expect_verdict(dict(empty, **{C_SAME: 3, C_DIFFERENT: 2})), V_MOST_SAME)
        want("verdict some same", _expect_verdict(dict(empty, **{C_SAME: 2, C_DIFFERENT: 3})), V_SOME_SAME)

        # float repr tolerance is published, never used for the class
        want("tolerance catches a repr move", equal_within_tolerance(1.0000000000000002, 1.0), True)
        want("tolerance refuses a real move", equal_within_tolerance(1.01, 1.0), False)

        # guards: a face whose tallies do not re-add must be refused
        face = {
            "summary": {
                "member_files": 2,
                "class_counts": {c: 0 for c in CLASSES},
                "class_bytes": {c: 0 for c in CLASSES},
                "comparable_files": 2,
                "same_conclusion_in_different_rows": 1,
                "bytes_holding_the_same_conclusion": 0,
                "scalar_arm_class_counts": {c: 0 for c in SCALAR_CLASSES},
                "arm_cross_tab": {},
                "conclusion_vocabulary": list(CONCLUSION_NAMES),
                "conclusion_vocabulary_histogram": {
                    n: {"twins_stating_it": 0, "agreements": 0, "differences": 0}
                    for n in CONCLUSION_NAMES},
                "differing_scalar_kind_histogram": {},
            },
            "families": [{"members": 2, "twin_present": True}],
            "rows": [
                {"path": "a.json", "twin": "t.json", "bytes": 1, "class": C_SAME,
                 "scalar_arm_class": S_DIFFERENT, "conclusion_field_names": ["answer"],
                 "differing_conclusion_names": [], "differing_scalar_names": ["cells"],
                 "differing_scalar_kind_counts": {"other": 1}, "twin_scalar_fields": 2,
                 "only_difference_is_a_date_shaped_name": False,
                 "conclusion_fields": [{"name": "answer", "equal": True}]},
                {"path": "b.json", "twin": "t.json", "bytes": 1, "class": C_DIFFERENT,
                 "scalar_arm_class": S_DIFFERENT, "conclusion_field_names": ["answer"],
                 "differing_conclusion_names": ["answer"], "differing_scalar_names": ["answer"],
                 "differing_scalar_kind_counts": {"conclusion_vocabulary": 1}, "twin_scalar_fields": 2,
                 "only_difference_is_a_date_shaped_name": False,
                 "conclusion_fields": [{"name": "answer", "equal": False}]},
            ],
            "verdict": V_SOME_SAME,
        }
        face["summary"]["class_counts"][C_SAME] = 1
        face["summary"]["class_counts"][C_DIFFERENT] = 1
        face["summary"]["class_bytes"][C_SAME] = 1
        face["summary"]["class_bytes"][C_DIFFERENT] = 1
        face["summary"]["bytes_holding_the_same_conclusion"] = 1
        face["summary"]["scalar_arm_class_counts"][S_DIFFERENT] = 2
        face["summary"]["arm_cross_tab"] = {"%s|%s" % (C_SAME, S_DIFFERENT): 1,
                                            "%s|%s" % (C_DIFFERENT, S_DIFFERENT): 1}
        face["summary"]["conclusion_vocabulary_histogram"]["answer"] = {
            "twins_stating_it": 2, "agreements": 1, "differences": 1}
        face["summary"]["differing_scalar_kind_histogram"] = {
            "conclusion_vocabulary": 1, "other": 1}
        want("clean fixture checks", row_problems(face), [])

        doctored = json.loads(json.dumps(face))
        doctored["verdict"] = V_ALL_SAME
        if not row_problems(doctored):
            fails.append("row_problems() accepted a verdict the counts do not imply")
        doctored2 = json.loads(json.dumps(face))
        doctored2["rows"][0]["differing_conclusion_names"] = ["answer"]
        if not row_problems(doctored2):
            fails.append("row_problems() accepted a same-conclusion row naming a differing field")
        doctored3 = json.loads(json.dumps(face))
        doctored3["summary"]["class_counts"][C_NO_CONCL] = 1
        if not row_problems(doctored3):
            fails.append("row_problems() accepted class counts that do not sum to member_files")
        doctored4 = json.loads(json.dumps(face))
        doctored4["rows"][1]["conclusion_fields"][0]["name"] = "vibe"
        if not row_problems(doctored4):
            fails.append("row_problems() accepted a field outside the frozen vocabulary")
        doctored5 = json.loads(json.dumps(face))
        doctored5["summary"]["conclusion_vocabulary_histogram"]["answer"]["agreements"] = 2
        if not row_problems(doctored5):
            fails.append("row_problems() accepted a vocabulary histogram that does not re-derive")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        for f in fails:
            print("FAIL %s" % f)
        return 1
    print("selftest 34/34: 5 classes + 4 scalar-arm classes + 5 verdict branches + 2 tolerance "
          "branches + 2 arms + 2 histograms + 5 doctored faces: OK")
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run", "check", "verify", "selftest"))
    args = ap.parse_args(argv)
    if args.cmd == "run":
        return run()
    if args.cmd == "check":
        problems = check()
    elif args.cmd == "verify":
        problems = verify()
    else:
        return selftest()
    print(json.dumps({"problems": problems}, ensure_ascii=False))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))