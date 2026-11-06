"""E462 -- which identity declarations sit in a dialect no reader speaks?

E461 published 110 identity-named read sites against 15 identity field names E458 froze, and found
that 7 of them are read by no source at all -- and that the never-read ones are exactly the
shape-named ones (card_id / study_id / prereg_path / prereg_note / pinned_note / source_card /
source_cards).  A face that declares "card_id": "E462" has written its identity in a language the
corpus does not speak: the payload is self-describing to a human reader and silent to every gate.

This card asks that of each face, not of the vocabulary:

  D  dialect split  -- for each graded face, split the identity fields it declares into names some
                       source READS and names no source reads, and classify the face as
                       read-only (speaks the read dialect), redundant (never-read names beside a
                       read name) or silent (never-read names only).
  C  contradiction  -- where a face declares a never-read name beside a read one, do the two agree
                       on the study?  A redundant duplicate that names a different study is a
                       disagreement no gate can currently see, because the second voice is unread.
  J  join exposure  -- the faces that a consumer currently joins are joined through a read name by
                       construction; publishing that count says what dropping the read names would
                       cost, so the silent dialect cannot be read as harmless.

Population: the graded rows of E458's faceidentity_latest.json that declare a top-level machine
readable identity (the same population E461 graded), plus E461's own per-face join class, machine
read.  Read sites are RE-DERIVED from the live corpus here (E461's counts are carried beside them
as a comparison column), with this family's own instruments excluded -- a scanner that reads every
identity field name would otherwise be the only reader of the dialect it is measuring.

Run:      python scripts/e462_identity_dialect.py run
Verify:   python scripts/e462_identity_dialect.py verify     (re-derives from the live tree)
Check:    python scripts/e462_identity_dialect.py check      (tallies re-derive from the face)
Selftest: python scripts/e462_identity_dialect.py selftest
"""

import argparse
import ast
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e451_prereg_digest as e451  # noqa: E402  (walk_py / read_text)
import e461_identity_consumers as e461  # noqa: E402  (key_sites / READ_KINDS / face_rows)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "identitydialect_latest.json"
DATED_PREFIX = "IDENTITYDIALECT"
CARD = "E462-WHICH-IDENTITY-DECLARATIONS-SIT-IN-A-DIALECT-NO-READER-SPEAKS"
PARENT_FACE = "faceidentity_latest.json"
PEER_FACE = "identityconsumers_latest.json"

# The whole family reads identity field names, so every member's own source would vote for the
# dialect it is studying.  Excluded by name, and the exclusion is published.
SELF_SKIP = ("e461_", "e462_", "run_e461", "run_e462")
MAX_READ_BYTES = 2 * 1024 * 1024
MAX_ROWS = 2000

D_READ_ONLY = "declares_only_names_some_source_reads"
D_REDUNDANT = "declares_a_never_read_name_beside_a_read_name"
D_SILENT = "declares_only_names_no_source_reads"
DIALECT_CLASSES = (D_READ_ONLY, D_REDUNDANT, D_SILENT)

V_EMPTY = "no_graded_face_declares_a_top_level_identity"
V_ALL_READ = "every_declared_identity_name_is_read_by_some_source"
V_REDUNDANT = "the_never_read_names_are_a_second_voice_on_faces_that_also_speak_a_read_name"
V_SILENT = "some_faces_declare_their_identity_only_in_names_no_source_reads"
VERDICT_VOCAB = (V_EMPTY, V_ALL_READ, V_REDUNDANT, V_SILENT)


# ----------------------------------------------------------------------------- helpers


def _load(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def is_own_output(rel):
    base = os.path.basename(rel)
    if base == FACE_NAME or base == PEER_FACE:
        return True
    return base.startswith(DATED_PREFIX + "-") and base.endswith(".json")


# ----------------------------------------------------------------------------- corpus


def corpus(skip_self=True):
    """[(rel, key_sites)] over the repo's .py files, this family's instruments excluded."""
    out = []
    errors = []
    for rel in e451.walk_py(ROOT):
        base = os.path.basename(rel)
        if is_own_output(rel):
            continue
        if skip_self and any(base.startswith(s) for s in SELF_SKIP):
            continue
        path = os.path.join(ROOT, rel)
        try:
            if os.path.getsize(path) > MAX_READ_BYTES:
                continue
            tree = ast.parse(e451.read_text(path))
        except (SyntaxError, ValueError, OSError):
            errors.append(rel)
            continue
        out.append((rel, e461.key_sites(tree)))
    return out, errors


def read_census(sources, fields):
    """Per field: how many sites READ it (the same read kinds E461 froze)."""
    census = {}
    for f in fields:
        census[f] = {"field": f, "read_sites": 0, "write_sites": 0, "files_reading": 0,
                     "sample_reading_files": []}
    by_rel = {}
    for rel, sites in sources:
        for field, kind, _ln in sites:
            if field not in census:
                continue
            c = census[field]
            if kind in e461.READ_KINDS:
                c["read_sites"] += 1
                by_rel.setdefault(field, set()).add(rel)
            elif kind in e461.WRITE_KINDS:
                c["write_sites"] += 1
    for field, rels in by_rel.items():
        c = census[field]
        c["files_reading"] = len(rels)
        c["sample_reading_files"] = sorted(rels)[:8]
    return census


# ----------------------------------------------------------------------------- dialect split


def declared_values(row):
    """{field: [values]} for the top-level non-prose identity a face declares.

    Accepts either E458's own row shape (`hits`) or the narrowed shape E461 hands out (`decl`),
    because the population is machine-read from E461's helper and must not be re-implemented.
    """
    pairs = []
    if row.get("decl"):
        pairs = [(f, v) for f, v in row["decl"]]
    else:
        for h in row.get("hits", []):
            if h.get("depth") != 1 or h.get("in_prose_field"):
                continue
            if not h.get("field") or not h.get("value"):
                continue
            pairs.append((h["field"], h["value"]))
    by_field = {}
    for field, value in pairs:
        by_field.setdefault(field, [])
        if value not in by_field[field]:
            by_field[field].append(value)
    return by_field


def dialect_for(rows, read_names, peer_by_face, ambiguous):
    graded = []
    for row in rows:
        decl = declared_values(row)
        if not decl:
            continue
        fields = sorted(decl)
        rn = [f for f in fields if f in read_names]
        un = [f for f in fields if f not in read_names]
        if un and rn:
            cls = D_REDUNDANT
        elif un:
            cls = D_SILENT
        else:
            cls = D_READ_ONLY
        # A never-read voice that names a different study than the read voice is a disagreement no
        # gate can see; published per face rather than summed blindly.
        read_vals = {v for f in rn for v in decl[f]}
        unread_vals = {v for f in un for v in decl[f]}
        all_vals = read_vals | unread_vals
        contradiction = bool(rn and un and unread_vals and read_vals
                             and not (unread_vals & read_vals))
        peer = peer_by_face.get(row["face"]) or {}
        graded.append({
            "face": row["face"],
            "family": row.get("family"),
            "class": cls,
            "declared_fields": fields,
            "declared_values": {f: decl[f] for f in fields},
            "read_names": rn,
            "never_read_names": un,
            "distinct_declared_values": sorted(all_vals),
            "declares_an_ambiguous_read_name": any(f in ambiguous for f in rn),
            "unread_voice_contradicts_read_voice": contradiction,
            # Two READ names disagreeing is the other shape: every voice here is spoken, so the
            # contradiction is visible to consumers and can be resolved two ways at once.
            "read_voices_disagree": len(read_vals) > 1,
            "peer_link_class": peer.get("class"),
            "peer_joined_source_count": peer.get("joined_source_count", 0),
            "producers": (row.get("producers") or [])[:3],
        })
    return graded


def verdict_for(graded):
    if not graded:
        return V_EMPTY
    silent = [g for g in graded if g["class"] == D_SILENT]
    redundant = [g for g in graded if g["class"] == D_REDUNDANT]
    if silent:
        return V_SILENT
    if redundant:
        return V_REDUNDANT
    return V_ALL_READ


# ----------------------------------------------------------------------------- build


def build(write=True):
    parent = _load(os.path.join(OUTDIR, PARENT_FACE))
    peer = _load(os.path.join(OUTDIR, PEER_FACE))
    fields = sorted(parent.get("identity_field_vocabulary") or [])
    ambiguous = set(peer.get("summary", {}).get("ambiguous_fields") or e461.AMBIGUOUS_FIELDS)
    peer_by_face = {r["face"]: r for r in peer.get("rows", []) if r.get("face")}
    rows = e461.face_rows(parent) if hasattr(e461, "face_rows") else []

    sources, errors = corpus()
    # A field a face declares outside the frozen vocabulary is measured too: calling it a
    # never-read name without looking would be an unmeasured claim (E207/E462 family).
    declared_names = set()
    for row in rows:
        declared_names.update(f for f, _v in row.get("decl", []))
    universe = sorted(set(fields) | declared_names)
    census = read_census(sources, universe)
    read_names = {f for f in universe if census[f]["read_sites"] > 0}
    peer_census = peer.get("field_census") or {}

    graded = dialect_for(rows, read_names, peer_by_face, ambiguous)

    joined = [g for g in graded if (g["peer_joined_source_count"] or 0) > 0]
    counts = {c: sum(1 for g in graded if g["class"] == c) for c in DIALECT_CLASSES}
    instances = sum(len(g["declared_fields"]) for g in graded)
    instances_unread = sum(len(g["never_read_names"]) for g in graded)
    disagree = sorted(
        f for f in fields
        if f in peer_census and bool(peer_census[f].get("read_sites"))
        != bool(census[f]["read_sites"]))
    summary = {
        "card": CARD,
        "corpus_sources": len(sources),
        "corpus_parse_errors": len(errors),
        "faces_graded": len(graded),
        "dialect_classes": counts,
        "declared_field_instances": instances,
        "declared_instances_in_a_never_read_name": instances_unread,
        "fields": len(universe),
        "fields_frozen_in_the_vocabulary": len(fields),
        "fields_outside_the_frozen_vocabulary": sorted(declared_names - set(fields)),
        "faces_declaring_a_name_outside_the_vocabulary": sum(
            1 for g in graded
            if set(g["declared_fields"]) - set(fields)),
        "fields_read": sorted(read_names),
        "fields_never_read": sorted(f for f in universe if f not in read_names),
        "fields_frozen_never_read": sorted(f for f in fields if f not in read_names),
        "fields_never_read_per_e461": sorted(peer.get("summary", {}).get("fields_never_read") or []),
        "fields_whose_read_status_disagrees_with_e461": disagree,
        "ambiguous_fields": sorted(ambiguous),
        "faces_declaring_an_ambiguous_read_name": sum(
            1 for g in graded if g["declares_an_ambiguous_read_name"]),
        "faces_with_an_unread_voice_contradicting_a_read_voice": sum(
            1 for g in graded if g["unread_voice_contradicts_read_voice"]),
        "faces_whose_two_read_names_name_different_values": sum(
            1 for g in graded if g["read_voices_disagree"]),
        "faces_carrying_more_than_one_identity_value": sum(
            1 for g in graded if len(g["distinct_declared_values"]) > 1),
        "contradicting_faces": sorted(
            g["face"] for g in graded
            if g["read_voices_disagree"] or g["unread_voice_contradicts_read_voice"])[:10],
        "faces_a_consumer_currently_joins": len(joined),
        "faces_that_would_become_unreadable_if_read_names_were_dropped": len(joined),
        "faces_absent_from_the_e461_face": sum(
            1 for g in graded if g["peer_link_class"] is None),
        "never_read_names_carried_by_faces": {
            f: sum(1 for g in graded if f in g["never_read_names"]) for f in universe
            if f not in read_names
        },
    }
    face = {
        "card": CARD,
        "study": "E462",
        "title": "which identity declarations sit in a dialect no reader speaks",
        "evidence_cutoff": parent.get("evidence_cutoff"),
        "population_source": (
            "the graded rows of E458's " + PARENT_FACE + " that declare a top-level identity; "
            "read sites re-derived from e451.walk_py minus this family's own instruments "
            "(e461_/e462_/run_e461/run_e462 + this face); join class carried from " + PEER_FACE
        ),
        "verdict": verdict_for(graded),
        "verdict_vocab": list(VERDICT_VOCAB),
        "dialect_classes": list(DIALECT_CLASSES),
        "identity_field_vocabulary": fields,
        "read_kinds": list(e461.READ_KINDS),
        "write_kinds": list(e461.WRITE_KINDS),
        "summary": summary,
        "field_census": census,
        "field_census_per_e461": {
            f: {"read_sites": (peer_census.get(f) or {}).get("read_sites")} for f in fields},
        "rows": graded[:MAX_ROWS],
        "parse_errors": errors[:50],
        "method_limits": [
            "static: a name is read if a source uses it as a dict key in a read context; a name "
            "reached through a composed key (d['card' + '_id']) is invisible and counts as unread, "
            "which inflates the silent dialect, never the read one",
            "the never-read set is measured over the same corpus E461 walked, minus this family's "
            "own instruments; a field read ONLY by a census instrument would be published as "
            "never-read here and is named in fields_whose_read_status_disagrees_with_e461",
            "identity field names in the vocabulary are generic payload keys as often as identity "
            "keys ('id' has the most read sites of any name); faces whose read names are all "
            "ambiguous are published with a flag rather than folded into the read-only class",
            "contradiction compares declared VALUES as strings; two ids that differ only in "
            "case/spacing are reported as a contradiction and must be read from the row",
        ],
    }
    if write:
        os.makedirs(OUTDIR, exist_ok=True)
        for name in (FACE_NAME, "%s-%s.json" % (
                DATED_PREFIX, face.get("evidence_cutoff") or "undated")):
            with io.open(os.path.join(OUTDIR, name), "w", encoding="utf-8",
                         newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1)
                fh.write("\n")
    return face


# ----------------------------------------------------------------------------- gates


def tally_problems(face):
    """Every published number must re-derive from the published rows."""
    problems = []
    s = face.get("summary", {})
    rows = face.get("rows", [])
    if s.get("faces_graded") != len(rows):
        problems.append("faces_graded %r != rows %r" % (s.get("faces_graded"), len(rows)))
    for cls in DIALECT_CLASSES:
        got = sum(1 for r in rows if r.get("class") == cls)
        if s.get("dialect_classes", {}).get(cls) != got:
            problems.append("dialect class %s: published %r, rows %r"
                            % (cls, s.get("dialect_classes", {}).get(cls), got))
    if s.get("declared_field_instances") != sum(len(r.get("declared_fields") or []) for r in rows):
        problems.append("declared instances do not re-derive from the rows")
    if s.get("declared_instances_in_a_never_read_name") != sum(
            len(r.get("never_read_names") or []) for r in rows):
        problems.append("never-read instances do not re-derive from the rows")
    if s.get("faces_declaring_an_ambiguous_read_name") != sum(
            1 for r in rows if r.get("declares_an_ambiguous_read_name")):
        problems.append("ambiguous-read-name total does not re-derive from the rows")
    if s.get("faces_with_an_unread_voice_contradicting_a_read_voice") != sum(
            1 for r in rows if r.get("unread_voice_contradicts_read_voice")):
        problems.append("contradiction total does not re-derive from the rows")
    if s.get("faces_whose_two_read_names_name_different_values") != sum(
            1 for r in rows if r.get("read_voices_disagree")):
        problems.append("read-voice disagreement total does not re-derive from the rows")
    if s.get("faces_carrying_more_than_one_identity_value") != sum(
            1 for r in rows if len(r.get("distinct_declared_values") or []) > 1):
        problems.append("multi-value face total does not re-derive from the rows")
    if s.get("contradicting_faces") != sorted(
            r.get("face") for r in rows
            if r.get("read_voices_disagree") or r.get("unread_voice_contradicts_read_voice"))[:10]:
        problems.append("contradicting face list does not re-derive from the rows")
    for r in rows:
        disagree = len({v for f in (r.get("read_names") or [])
                        for v in (r.get("declared_values") or {}).get(f, [])}) > 1
        if bool(r.get("read_voices_disagree")) != disagree:
            problems.append("row %s read-voice flag does not re-derive" % r.get("face"))
    if s.get("faces_a_consumer_currently_joins") != sum(
            1 for r in rows if (r.get("peer_joined_source_count") or 0) > 0):
        problems.append("join-exposure total does not re-derive from the rows")
    census = face.get("field_census") or {}
    if s.get("fields") != len(census):
        problems.append("field count != census rows")
    never = sorted(f for f, c in census.items() if not (c.get("read_sites") or 0))
    if s.get("fields_never_read") != never:
        problems.append("fields_never_read does not re-derive from the census")
    read = sorted(f for f, c in census.items() if (c.get("read_sites") or 0) > 0)
    if s.get("fields_read") != read:
        problems.append("fields_read does not re-derive from the census")
    carried = s.get("never_read_names_carried_by_faces") or {}
    for f in never:
        got = sum(1 for r in rows if f in (r.get("never_read_names") or []))
        if carried.get(f) != got:
            problems.append("never-read name %s carried by %r faces, rows say %r"
                            % (f, carried.get(f), got))
    frozen = set(face.get("identity_field_vocabulary") or [])
    outside = sorted({f for r in rows for f in (r.get("declared_fields") or [])} - frozen)
    if s.get("fields_outside_the_frozen_vocabulary") != outside:
        problems.append("outside-vocabulary names do not re-derive from the rows")
    if s.get("faces_declaring_a_name_outside_the_vocabulary") != sum(
            1 for r in rows if set(r.get("declared_fields") or []) - frozen):
        problems.append("outside-vocabulary face total does not re-derive from the rows")
    for r in rows:
        cls = r.get("class")
        if cls == D_SILENT and r.get("read_names"):
            problems.append("silent face %s declares a read name" % r.get("face"))
        if cls == D_READ_ONLY and r.get("never_read_names"):
            problems.append("read-only face %s declares a never-read name" % r.get("face"))
        if cls == D_REDUNDANT and not (r.get("read_names") and r.get("never_read_names")):
            problems.append("redundant face %s lacks one of the two voices" % r.get("face"))
    if face.get("verdict") != verdict_for(rows):
        problems.append("verdict does not re-derive from the rows")
    return problems


def verify():
    problems = []
    live = build(write=False)
    on_disk = _load(os.path.join(OUTDIR, FACE_NAME))
    if live["summary"] != on_disk.get("summary"):
        diff = sorted(k for k in live["summary"] if live["summary"][k] != on_disk["summary"].get(k))
        problems.append("summary is stale against the live tree: %s" % ", ".join(diff))
    if live.get("verdict") != on_disk.get("verdict"):
        problems.append("verdict differs: live %r disk %r"
                        % (live.get("verdict"), on_disk.get("verdict")))
    problems.extend(tally_problems(on_disk))
    return problems


def check():
    return tally_problems(_load(os.path.join(OUTDIR, FACE_NAME)))


# ----------------------------------------------------------------------------- selftest


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # corpus: the family's own instruments must not vote for the dialect they measure
    leg("own instrument source is skipped by name",
        any(os.path.basename("scripts/e461_identity_consumers.py").startswith(s)
            for s in SELF_SKIP))
    leg("own face is skipped by name", is_own_output("results/state_tilt/" + FACE_NAME))
    leg("a dated own output is skipped",
        is_own_output("results/state_tilt/%s-2026-11-06.json" % DATED_PREFIX))
    leg("a neighbour face is not own output",
        not is_own_output("results/state_tilt/faceidentity_latest.json"))

    # census: a write is not a read
    srcs = [("a.py", [("study", e461.K_DICT_KEY, 1), ("study_id", e461.K_DICT_KEY, 1)]),
            ("b.py", [("study", e461.K_LOAD, 2), ("card_id", e461.K_GET, 3)])]
    cen = read_census(srcs, ["study", "study_id", "card_id"])
    leg("a write-only name has zero read sites", cen["study_id"]["read_sites"] == 0)
    leg("a read name counts its site", cen["study"]["read_sites"] == 1)
    leg("a get counts as a read", cen["card_id"]["read_sites"] == 1)
    leg("files_reading counts distinct files", cen["study"]["files_reading"] == 1)

    # dialect classifier on a synthetic three-face population
    rows = [
        {"face": "results/x/A-2026-11-06.json", "family": "x", "producers": ["p.py"],
         "hits": [{"depth": 1, "field": "study", "value": "E462", "in_prose_field": False}]},
        {"face": "results/x/B-2026-11-06.json", "family": "x", "producers": ["p.py"],
         "hits": [{"depth": 1, "field": "study", "value": "E462", "in_prose_field": False},
                  {"depth": 1, "field": "study_id", "value": "E999",
                   "in_prose_field": False}]},
        {"face": "results/x/C-2026-11-06.json", "family": "x", "producers": ["p.py"],
         "hits": [{"depth": 1, "field": "card_id", "value": "E462",
                   "in_prose_field": False}]},
        {"face": "results/x/D-2026-11-06.json", "family": "x", "producers": ["p.py"],
         "hits": [{"depth": 1, "field": "study", "value": "E462", "in_prose_field": True}]},
    ]
    graded = dialect_for(rows, {"study", "card"}, {}, {"id", "pin", "pid"})
    leg("a face declaring only a read name is read-only", graded[0]["class"] == D_READ_ONLY)
    leg("a face declaring both voices is redundant", graded[1]["class"] == D_REDUNDANT)
    leg("a face declaring only never-read names is silent", graded[2]["class"] == D_SILENT)
    leg("a prose hit is not a machine declaration", len(graded) == 3)
    leg("a redundant duplicate naming a different study is a contradiction",
        graded[1]["unread_voice_contradicts_read_voice"] is True)
    leg("agreeing voices are not a contradiction",
        dialect_for([{"face": "results/x/E-2026-11-06.json", "family": "x", "producers": [],
                      "hits": [{"depth": 1, "field": "study", "value": "E1",
                                "in_prose_field": False},
                               {"depth": 1, "field": "study_id", "value": "E1",
                                "in_prose_field": False}]}],
                    {"study"}, {}, set())[0]["unread_voice_contradicts_read_voice"] is False)
    _two_read = dialect_for([{"face": "results/x/F-2026-11-06.json", "family": "x", "producers": [],
                              "hits": [{"depth": 1, "field": "card", "value": "E413",
                                        "in_prose_field": False},
                                       {"depth": 1, "field": "study", "value": "E421",
                                        "in_prose_field": False}]}],
                            {"card", "study"}, {}, set())[0]
    leg("two read names naming different values is a visible contradiction",
        _two_read["read_voices_disagree"] is True
        and _two_read["unread_voice_contradicts_read_voice"] is False)
    leg("a two-read-name face is still read-only (both voices are spoken)",
        _two_read["class"] == D_READ_ONLY)

    leg("verdict is silent when a face has only never-read names",
        verdict_for(graded) == V_SILENT)
    leg("verdict is redundant when no face is silent",
        verdict_for([g for g in graded if g["class"] != D_SILENT]) == V_REDUNDANT)
    leg("verdict is all-read when every name is read",
        verdict_for([graded[0]]) == V_ALL_READ)
    leg("verdict is empty on an empty population", verdict_for([]) == V_EMPTY)

    # a published face whose tallies drift must be refused
    face = {
        "verdict": V_REDUNDANT,
        "identity_field_vocabulary": ["study", "study_id"],
        "summary": {
            "faces_graded": 1,
            "dialect_classes": {c: 0 for c in DIALECT_CLASSES},
            "declared_field_instances": 0,
            "declared_instances_in_a_never_read_name": 0,
            "faces_declaring_an_ambiguous_read_name": 0,
            "faces_with_an_unread_voice_contradicting_a_read_voice": 0,
            "faces_whose_two_read_names_name_different_values": 0,
            "faces_carrying_more_than_one_identity_value": 0,
            "contradicting_faces": [],
            "faces_a_consumer_currently_joins": 0,
            "fields": 0,
            "fields_read": [],
            "fields_never_read": [],
            "fields_outside_the_frozen_vocabulary": [],
            "faces_declaring_a_name_outside_the_vocabulary": 0,
            "never_read_names_carried_by_faces": {},
        },
        "field_census": {},
        "rows": [{"class": D_REDUNDANT, "face": "x", "declared_fields": ["study"],
                  "declared_values": {"study": ["E1"]},
                  "distinct_declared_values": ["E1"],
                  "read_names": ["study"], "never_read_names": [],
                  "declares_an_ambiguous_read_name": False,
                  "unread_voice_contradicts_read_voice": False,
                  "read_voices_disagree": False,
                  "peer_joined_source_count": 0}],
    }
    leg("gate refuses a class tally that does not re-derive",
        any("dialect class" in p for p in tally_problems(face)))
    face["summary"]["dialect_classes"][D_REDUNDANT] = 1
    face["summary"]["faces_graded"] = 1
    face["summary"]["declared_field_instances"] = 1
    leg("gate still refuses a redundant face with no second voice",
        any("lacks one of the two voices" in p for p in tally_problems(face)))
    face["rows"][0]["never_read_names"] = ["study_id"]
    face["summary"]["declared_instances_in_a_never_read_name"] = 1
    leg("gate accepts a consistent face", tally_problems(face) == [])
    face["rows"][0]["declared_fields"] = ["study", "source_study"]
    leg("gate refuses a name outside the frozen vocabulary folded into the census silently",
        any("outside-vocabulary" in p for p in tally_problems(face)))

    ok = sum(1 for _n, c in legs if c)
    for name, cond in legs:
        print(("PASS " if cond else "FAIL ") + name)
    print("selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


# ----------------------------------------------------------------------------- main


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        face = build(write=True)
        s = face["summary"]
        print("verdict:", face["verdict"])
        print("faces graded:", s["faces_graded"], "| dialect:", s["dialect_classes"])
        print("declared instances:", s["declared_field_instances"],
              "| in a never-read name:", s["declared_instances_in_a_never_read_name"])
        print("fields read:", len(s["fields_read"]), "| never read:", s["fields_never_read"])
        print("join exposure:", s["faces_a_consumer_currently_joins"],
              "| contradictions:", s["faces_with_an_unread_voice_contradicting_a_read_voice"])
        problems = tally_problems(face)
        print("problems:", problems)
        return 0 if not problems else 1
    if cmd == "verify":
        problems = verify()
        print("problems:", problems)
        return 0 if not problems else 1
    if cmd == "check":
        problems = check()
        print("problems:", problems)
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print("usage: e462_identity_dialect.py [run|verify|check|selftest]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))