"""E460 -- which study face lacks an identity its own producer knows.

E458 graded 538 published faces for a machine-readable identity and published 12 that carry none
(10 with no identity at all, 2 whose only identity sits in prose).  Every one of those faces has a
producer, and a producer that knows its own card id is the cheapest possible repair: the value
already exists in the source that writes the face, it just never reaches the payload.

This study takes E458's own published rows as its population -- never a hand-written list -- and
asks three questions of each flagged face, per producer:

  (a) which identity shapes does the producer's own source carry?  A card id from the module name
      (``eNNN_``), from the module docstring, or from a module-level string constant; a study id
      or a prereg note path in the same places.
  (b) does the payload already carry a field named like an identity, and in which dialect?  This
      is the finding that makes the card non-trivial: several of the flagged faces DO carry
      ``study``, and its value is a producer script stem (``e271_donor_choice_sensitivity``)
      rather than the card (``E271``) or the study id.  A field that exists in a dialect no card
      reader keys on is not a missing field -- it is a missing value.
  (c) if the payload's identity names a script, is that script one of this face's own producers?
      A face whose ``study`` value names somebody else's producer carries a *wrong* identity, and
      that is a different repair from carrying none.

Classes are published apart because the repairs differ (add a field / normalise a value / the
producer must be taught), and a face that already carries a card is kept as its own class so a
re-run on a repaired tree reads as repaired instead of silently vanishing from the tally.

Usage:
    python scripts/e460_facegap.py run|check|selftest|verify
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "facegap_latest.json"
DATED_PREFIX = "FACEGAP"
CARD_ID = "E460-WHICH-STUDY-FACE-LACKS-AN-IDENTITY-ITS-OWN-PRODUCER-KNOWS"

# The population is inherited, not restated: E458's own published face is the only source of it.
UPSTREAM_FACE = os.path.join(OUTDIR, "faceidentity_latest.json")
UPSTREAM_STUDY = "E458"
UPSTREAM_MACHINE_CLASS = "carries_a_machine_readable_identity"

PRODUCER_RE = re.compile(r"^(e[0-9]{3,})_[a-z0-9_]*\.py$")
SCRIPT_STEM_RE = re.compile(r"^e[0-9]{3,}_[a-z0-9_]+$")
CARD_RE = re.compile(r"\bE[0-9]{3,}\b")
STUDY_RE = re.compile(r"\b[A-Z][A-Z0-9]+(?:-[A-Z0-9]+)*-P[0-9]+\b")
PREREG_RE = re.compile(r"research/[A-Za-z0-9_./\-]+\.md")

# Field names that promise an identity -- the same vocabulary E458 froze, so the two studies cannot
# drift apart on what "named like an identity" means.
IDENTITY_FIELDS = frozenset({
    "card", "card_id", "cards", "study", "study_id", "studies", "prereg", "prereg_path",
    "prereg_note", "pid", "source_card", "source_cards", "pin", "pinned_note",
})

D_CARD = "a_card_id"
D_STUDY = "a_study_id"
D_PREREG = "a_prereg_note_path"
D_STEM = "a_producer_script_stem"
D_OTHER = "other_text"
D_NOT_STR = "not_a_string"
DIALECTS = (D_CARD, D_STUDY, D_PREREG, D_STEM, D_OTHER, D_NOT_STR)

C_DIALECT = "carries_an_identity_named_field_in_a_dialect_a_card_reader_cannot_key"
C_NO_FIELD = "carries_no_identity_named_field_though_its_producer_knows_a_card"
C_NO_PRODUCER = "no_producer_of_this_face_carries_any_identity_in_its_own_source"
C_ALREADY = "already_carries_a_card_id"
CLASSES = (C_ALREADY, C_DIALECT, C_NO_FIELD, C_NO_PRODUCER)

# What a script-stem value in an identity-named field is actually saying.  The stem is not a broken
# card: on most faces it names the producer that published the face, and on at least one it names the
# study whose corpus the face pinned.  Those are two different questions sharing one field name.
R_AUTHOR = "names_the_producer_that_published_the_face"
R_SUBJECT = "names_a_script_the_producer_chose_as_its_subject_not_its_author"
R_FOREIGN = "names_a_script_no_producer_of_this_face_mentions"
R_NOT_A_STEM = "the_identity_field_does_not_hold_a_script_stem"
READINGS = (R_AUTHOR, R_SUBJECT, R_FOREIGN, R_NOT_A_STEM)

V_EMPTY = "no_face_is_flagged_by_the_identity_census"
V_ALREADY = "every_face_flagged_by_the_identity_census_now_carries_a_card_id"
V_DOMINANT_DIALECT = ("most_flagged_faces_carry_the_identity_as_a_producer_script_stem_in_a_field_"
                      "name_no_card_reader_keys_on")
V_DOMINANT_NO_FIELD = ("most_flagged_faces_carry_no_identity_named_field_although_a_producer_"
                       "knows_a_card")
V_DOMINANT_NO_PRODUCER = "most_flagged_faces_have_no_producer_that_carries_any_identity"
V_SPLIT = "the_flagged_faces_split_between_a_dialect_value_a_missing_field_and_a_producer_gap"
VERDICT_VOCAB = (V_EMPTY, V_ALREADY, V_DOMINANT_DIALECT, V_DOMINANT_NO_FIELD,
                 V_DOMINANT_NO_PRODUCER, V_SPLIT)

MAX_READ_BYTES = 8 * 1024 * 1024
MAX_CARDS_CITED = 5
MAX_CONSTANT_VALUES = 400


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def _load(path: str):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _read_source(rel: str) -> str:
    with io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _filename_card(rel: str) -> str | None:
    m = PRODUCER_RE.match(os.path.basename(rel))
    return m.group(1).upper() if m else None


def dialect_of_value(value) -> str:
    """What kind of identity a payload value spells, or that it spells none."""
    if not isinstance(value, str):
        return D_NOT_STR
    text = value.strip()
    if not text:
        return D_OTHER
    if CARD_RE.fullmatch(text):
        return D_CARD
    if PREREG_RE.fullmatch(text):
        return D_PREREG
    if SCRIPT_STEM_RE.match(text):
        return D_STEM
    if STUDY_RE.fullmatch(text):
        return D_STUDY
    return D_OTHER


# ----------------------------------------------------------------------------- producer side


def identity_keys_written(tree) -> tuple:
    """(sorted identity-named key literals the source writes in ANY dict, number of dict sites)."""
    keys, sites = set(), 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            hits = [k.value for k in node.keys
                    if isinstance(k, ast.Constant) and isinstance(k.value, str)
                    and k.value in IDENTITY_FIELDS]
            if hits:
                sites += 1
                keys.update(hits)
    return sorted(keys), sites


def module_constants(tree) -> list:
    """Module-level string constants: the place a producer pins an id nobody derives."""
    out = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not all(isinstance(t, ast.Name) for t in node.targets):
            continue
        if not isinstance(node.value, ast.Constant) or not isinstance(node.value.value, str):
            continue
        out.append({"name": node.targets[0].id, "value": node.value.value})
    return out


def producer_identities(source: str) -> dict:
    """What a producer's own source knows about the identity of the face it writes.

    The filename card is the producer's own card by construction; a docstring that never mentions
    it is a producer that does not restate what it owns, which is published, not penalised.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {"parseable": False, "docstring_cards": [], "docstring_study_ids": [],
                "docstring_prereg_paths": [], "constants": [], "constant_values": [],
                "identity_keys": [], "identity_key_sites": 0}
    doc = ast.get_docstring(tree) or ""
    constants = module_constants(tree)
    const_text = "\n".join(c["value"] for c in constants)
    keys, sites = identity_keys_written(tree)
    return {
        "parseable": True,
        "docstring_head": doc.strip().splitlines()[0][:120] if doc.strip() else "",
        "docstring_cards": sorted(set(CARD_RE.findall(doc)))[:MAX_CARDS_CITED],
        "docstring_study_ids": sorted(set(STUDY_RE.findall(doc)))[:MAX_CARDS_CITED],
        "docstring_prereg_paths": sorted(set(PREREG_RE.findall(doc)))[:MAX_CARDS_CITED],
        "constants": [c for c in constants
                      if CARD_RE.search(c["value"]) or STUDY_RE.search(c["value"])
                      or PREREG_RE.search(c["value"])][:MAX_CARDS_CITED],
        "constant_cards": sorted(set(CARD_RE.findall(const_text)))[:MAX_CARDS_CITED],
        # every module-level string constant, not only the identity-shaped ones: a producer that
        # pins a *subject* (STUDY = "e323_...") chooses a script stem, which no identity regex sees
        "constant_values": sorted({c["value"] for c in constants})[:MAX_CONSTANT_VALUES],
        "identity_keys": keys,
        "identity_key_sites": sites,
    }


def producer_row(rel: str, payload_identity_keys: list, payload_stems: list) -> dict:
    own = _filename_card(rel)
    source = _read_source(rel)
    ids = producer_identities(source)
    knows_card = bool(own or ids["docstring_cards"] or ids["constant_cards"])
    knows_study = bool(ids["docstring_study_ids"])
    knows_prereg = bool(ids["docstring_prereg_paths"])
    restates = bool(own and own in (ids["docstring_cards"] + ids["constant_cards"]))
    return {
        "source": rel,
        "card_from_filename": own,
        "knows_a_card_id": knows_card,
        "knows_a_study_id": knows_study,
        "knows_a_prereg_path": knows_prereg,
        "restates_its_own_card_in_source": restates,
        "docstring_head": ids["docstring_head"],
        "docstring_cards": ids["docstring_cards"],
        "docstring_study_ids": ids["docstring_study_ids"],
        "docstring_prereg_paths": ids["docstring_prereg_paths"],
        "identity_keys_it_writes": ids["identity_keys"],
        "identity_key_sites": ids["identity_key_sites"],
        "payload_stems_it_names_as_a_constant":
            sorted(set(payload_stems) & set(ids["constant_values"])),
        "writes_an_identity_field_the_payload_lacks":
            sorted(set(ids["identity_keys"]) - set(payload_identity_keys)),
        "parseable": ids["parseable"],
    }


def needed_field(producers: list) -> dict:
    """The field the payload would need, and the value a producer already knows for it."""
    for p in producers:
        if p.get("card_from_filename"):
            return {"name": "card", "value": p["card_from_filename"], "from": p["source"]}
    for p in producers:
        if p.get("docstring_cards"):
            return {"name": "card", "value": p["docstring_cards"][0], "from": p["source"]}
    for p in producers:
        if p.get("docstring_prereg_paths"):
            return {"name": "prereg_path", "value": p["docstring_prereg_paths"][0],
                    "from": p["source"]}
    for p in producers:
        if p.get("docstring_study_ids"):
            return {"name": "study_id", "value": p["docstring_study_ids"][0],
                    "from": p["source"]}
    return {"name": None, "value": None, "from": None}


# ----------------------------------------------------------------------------- face side


def payload_identity_fields(payload) -> dict:
    """Top-level fields named like an identity, with the dialect of each value."""
    if not isinstance(payload, dict):
        return {}
    out = {}
    for key, value in payload.items():
        if isinstance(key, str) and key in IDENTITY_FIELDS:
            out[key] = {"value": value if isinstance(value, (str, int, float)) else str(type(value)),
                        "dialect": dialect_of_value(value)}
    return out


def study_field_reading(fields: dict, producers: list) -> dict:
    """When an identity field spells a script stem, what is that stem actually saying?

    Three different sentences share one field name, and only the first is a broken card:
      * the stem is the producer that published the face (a correct value in the wrong dialect);
      * the stem is a *subject* the producer pinned in a module constant (a different question --
        CORPUSPIN's ``study`` names the corpus it pinned, not the study that published it);
      * the stem names a script no producer of this face mentions (genuinely foreign).
    """
    owners = {p["source"] for p in producers}
    for key, info in fields.items():
        if info["dialect"] != D_STEM:
            continue
        value = str(info["value"]).strip()
        target = "scripts/%s.py" % value.lower()
        own = target in owners
        chosen = any(value in (p.get("payload_stems_it_names_as_a_constant") or [])
                     for p in producers)
        reading = R_AUTHOR if own else (R_SUBJECT if chosen else R_FOREIGN)
        return {"field": key, "value": value, "resolves_to": target,
                "exists": os.path.exists(os.path.join(ROOT, target)),
                "owned_by_one_of_its_producers": own,
                "chosen_as_a_constant_by_a_producer": chosen,
                "reading": reading}
    return {"field": None, "value": None, "resolves_to": None, "exists": False,
            "owned_by_one_of_its_producers": False,
            "chosen_as_a_constant_by_a_producer": False, "reading": R_NOT_A_STEM}


def class_of_face(fields: dict, producers: list) -> str:
    if any(f["dialect"] == D_CARD for f in fields.values()):
        return C_ALREADY
    if fields:
        return C_DIALECT
    if any(p.get("knows_a_card_id") or p.get("card_from_filename") for p in producers):
        return C_NO_FIELD
    return C_NO_PRODUCER


# ----------------------------------------------------------------------------- population


def flagged_rows() -> list:
    """E458's own rows, minus the ones it graded machine-readable.  Missing upstream = empty."""
    if not os.path.exists(UPSTREAM_FACE):
        return []
    try:
        upstream = _load(UPSTREAM_FACE)
    except (OSError, ValueError):
        return []
    return [r for r in (upstream.get("rows") or [])
            if r.get("class") and r["class"] != UPSTREAM_MACHINE_CLASS]


# ----------------------------------------------------------------------------- build


def build(write: bool = True) -> dict:
    rows, unreadable = [], []
    for upstream_row in flagged_rows():
        face = upstream_row["face"]
        producers = upstream_row.get("producers") or []
        path = os.path.join(ROOT, face)
        try:
            if os.path.getsize(path) > MAX_READ_BYTES:
                raise ValueError("payload larger than the read cap")
            payload = _load(path)
        except (OSError, ValueError) as exc:
            unreadable.append({"face": face, "reason": str(exc)[:120], "producers": producers})
            continue
        fields = payload_identity_fields(payload)
        stems = sorted({str(f["value"]).strip() for f in fields.values()
                        if f["dialect"] == D_STEM})
        producer_data = [producer_row(p, sorted(fields), stems) for p in producers]
        reading = study_field_reading(fields, producer_data)
        rows.append({
            "face": face,
            "upstream_class": upstream_row.get("class"),
            "producers": producers,
            "class": class_of_face(fields, producer_data),
            "payload_identity_fields": fields,
            "identity_field_names": sorted(fields),
            "needed_field": needed_field(producer_data),
            "producer_knows_a_card": any(p["knows_a_card_id"] for p in producer_data),
            "producer_rows": producer_data,
            "study_field_reading": reading,
            "identity_field_reads_as": reading["reading"],
            "producers_writing_an_identity_field_this_payload_lacks":
                sorted({k for p in producer_data
                        for k in p["writes_an_identity_field_the_payload_lacks"]}),
        })

    by_class = {c: sum(1 for r in rows if r["class"] == c) for c in CLASSES}
    by_reading = {r: sum(1 for x in rows if x["identity_field_reads_as"] == r) for r in READINGS}
    producer_rows = [p for r in rows for p in r["producer_rows"]]
    summary = {
        "faces_graded": len(rows),
        "faces_unreadable": len(unreadable),
        "faces_already_carrying_a_card": by_class[C_ALREADY],
        "faces_carrying_a_dialect_value": by_class[C_DIALECT],
        "faces_with_no_identity_field": by_class[C_NO_FIELD],
        "faces_with_no_producer_identity": by_class[C_NO_PRODUCER],
        "faces_whose_identity_field_names_their_author_producer": by_reading[R_AUTHOR],
        "faces_whose_identity_field_names_a_subject_their_producer_chose": by_reading[R_SUBJECT],
        "faces_whose_identity_field_names_a_foreign_script": by_reading[R_FOREIGN],
        "faces_whose_producer_knows_a_card": sum(1 for r in rows if r["producer_knows_a_card"]),
        "faces_needing_a_card_field": sum(1 for r in rows
                                          if (r["needed_field"] or {}).get("name") == "card"),
        "producers_read": len(producer_rows),
        "producers_that_restate_their_own_card": sum(
            1 for p in producer_rows if p["restates_its_own_card_in_source"]),
        "producers_writing_an_identity_field_name": sum(
            1 for p in producer_rows if p["identity_keys_it_writes"]),
        "upstream_study": UPSTREAM_STUDY,
        "upstream_face": _rel(UPSTREAM_FACE),
    }
    verdict = verdict_for(len(rows), by_class, summary)
    payload = {
        "card": CARD_ID,
        "study": "E460",
        "title": "which study face lacks an identity its own producer knows",
        "evidence_cutoff": date.today().isoformat(),
        "population_source": ("E458's published rows (results/state_tilt/faceidentity_latest.json) "
                              "excluding the machine-readable class; E460 never restates the "
                              "population, so a repair upstream shrinks this study automatically"),
        "class_vocab": list(CLASSES),
        "dialect_vocab": list(DIALECTS),
        "identity_field_vocabulary": sorted(IDENTITY_FIELDS),
        "verdict_vocab": list(VERDICT_VOCAB),
        "method_limits": [
            "the producer's own card is read from its file name (eNNN_) first: that is the one "
            "identity a producer cannot fail to own",
            "docstring cards are published as a set, not as ownership -- a docstring cites the "
            "studies it builds on, so the head card is often NOT this producer's own card",
            "a constant is counted as an identity only when the whole value is a card id, study "
            "id or prereg path (E461's rule: exact literal, not substring)",
            "identity field names are the frozen E458 vocabulary, so the two studies cannot "
            "disagree about what 'named like an identity' means",
            "dialect is decided by the value's shape alone; a stem that happens to end in _p1 is "
            "still a stem",
            "payloads above %d bytes are published as unreadable rather than graded" % MAX_READ_BYTES,
        ],
        "rows": rows,
        "unreadable": unreadable,
        "summary": summary,
        "verdict": verdict,
    }
    if write:
        os.makedirs(OUTDIR, exist_ok=True)
        for name in ("%s-%s.json" % (DATED_PREFIX, payload["evidence_cutoff"]), FACE_NAME):
            with io.open(os.path.join(OUTDIR, name), "w", encoding="utf-8", newline="\n") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
        print("wrote results/state_tilt/%s-%s.json" % (DATED_PREFIX, payload["evidence_cutoff"]))
    return payload


def verdict_for(rows: int, by_class: dict, summary: dict) -> str:
    """The dominant class, not an average: 11 stems and 1 missing field is a stem finding."""
    if rows == 0:
        return V_EMPTY
    if by_class.get(C_ALREADY) == rows:
        return V_ALREADY
    dominant = {
        C_DIALECT: V_DOMINANT_DIALECT,
        C_NO_FIELD: V_DOMINANT_NO_FIELD,
        C_NO_PRODUCER: V_DOMINANT_NO_PRODUCER,
    }
    # a headline needs a majority, not a plurality: eleven stems beside one missing field is a stem
    # finding, but three ways of failing without a majority is a split and is published as one
    ordered = sorted(((by_class.get(c, 0), CLASSES.index(c), c) for c in CLASSES),
                     key=lambda t: (-t[0], t[1]))
    best_count, _idx, best_class = ordered[0]
    if best_count * 2 <= rows:
        return V_SPLIT
    if best_class not in dominant:
        # the biggest single class is the already-repaired one, so this population is a mixture of
        # repaired and unrepaired faces rather than one repair to make
        return V_SPLIT
    return dominant[best_class]


# ----------------------------------------------------------------------------- check


def tally_problems(published: dict) -> list:
    """Every way the published face fails to re-derive from its own rows.  Shared with the leg."""
    rows = published.get("rows") or []
    summary = published.get("summary") or {}
    bad = []
    by_class = {c: sum(1 for r in rows if r["class"] == c) for c in CLASSES}
    if summary.get("faces_graded") != len(rows):
        bad.append("faces_graded does not re-add to its rows")
    if summary.get("faces_unreadable") != len(published.get("unreadable") or []):
        bad.append("faces_unreadable does not re-derive")
    for cls, key in ((C_ALREADY, "faces_already_carrying_a_card"),
                     (C_DIALECT, "faces_carrying_a_dialect_value"),
                     (C_NO_FIELD, "faces_with_no_identity_field"),
                     (C_NO_PRODUCER, "faces_with_no_producer_identity")):
        if summary.get(key) != by_class[cls]:
            bad.append("%s does not re-derive from the rows (%r != %r)"
                       % (key, summary.get(key), by_class[cls]))
    by_reading = {r: sum(1 for x in rows if x["identity_field_reads_as"] == r) for r in READINGS}
    for reading, key in ((R_AUTHOR, "faces_whose_identity_field_names_their_author_producer"),
                         (R_SUBJECT, "faces_whose_identity_field_names_a_subject_their_producer_chose"),
                         (R_FOREIGN, "faces_whose_identity_field_names_a_foreign_script")):
        if summary.get(key) != by_reading[reading]:
            bad.append("%s does not re-derive from the rows" % key)
    if summary.get("faces_whose_producer_knows_a_card") != sum(
            1 for r in rows if r["producer_knows_a_card"]):
        bad.append("faces_whose_producer_knows_a_card does not re-derive")
    if summary.get("producers_read") != sum(len(r["producer_rows"]) for r in rows):
        bad.append("producers_read does not re-derive")
    for r in rows:
        if r["class"] not in CLASSES:
            bad.append("%s: class outside the vocabulary: %r" % (r["face"], r["class"]))
        if r["class"] != class_of_face(r["payload_identity_fields"], r["producer_rows"]):
            bad.append("%s: class disagrees with its own published fields and producers" % r["face"])
        for key, info in (r["payload_identity_fields"] or {}).items():
            if info.get("dialect") not in DIALECTS:
                bad.append("%s: dialect %r outside the vocabulary" % (r["face"], info.get("dialect")))
            if info.get("dialect") != dialect_of_value(info.get("value")):
                bad.append("%s: dialect of %s does not re-derive from its published value"
                           % (r["face"], key))
        if sorted(r["payload_identity_fields"]) != r["identity_field_names"]:
            bad.append("%s: identity_field_names does not re-derive" % r["face"])
        if r["producer_knows_a_card"] != any(p["knows_a_card_id"] for p in r["producer_rows"]):
            bad.append("%s: producer_knows_a_card does not re-derive" % r["face"])
        want_needed = needed_field(r["producer_rows"])
        if want_needed != r["needed_field"]:
            bad.append("%s: needed_field does not re-derive (%r != %r)"
                       % (r["face"], r["needed_field"], want_needed))
        want_own = study_field_reading(r["payload_identity_fields"], r["producer_rows"])
        if want_own != r["study_field_reading"]:
            bad.append("%s: study_field_reading does not re-derive" % r["face"])
        if want_own.get("reading") != r["identity_field_reads_as"]:
            bad.append("%s: identity_field_reads_as does not re-derive" % r["face"])
        if r["identity_field_reads_as"] not in READINGS:
            bad.append("%s: reading outside the vocabulary: %r"
                       % (r["face"], r["identity_field_reads_as"]))
        want_lacking = sorted({k for p in r["producer_rows"]
                               for k in p["writes_an_identity_field_the_payload_lacks"]})
        if want_lacking != r["producers_writing_an_identity_field_this_payload_lacks"]:
            bad.append("%s: the lacking-field set does not re-derive" % r["face"])
    want_verdict = verdict_for(len(rows), by_class, summary)
    if published.get("verdict") != want_verdict:
        bad.append("the verdict does not re-derive: %r != %r"
                   % (published.get("verdict"), want_verdict))
    if published.get("verdict") not in VERDICT_VOCAB:
        bad.append("the verdict is outside the frozen vocabulary")
    return bad


def check() -> int:
    published = _load(os.path.join(OUTDIR, FACE_NAME))
    bad = tally_problems(published)
    for b in bad:
        print("BAD %s" % b)
    print("check %s" % ("clean" if not bad else "%d problem(s)" % len(bad)))
    return 0 if not bad else 1


def verify() -> int:
    """Rebuild and require byte-identical rows: the population is cheap, so re-read it live."""
    published = _load(os.path.join(OUTDIR, FACE_NAME))
    fresh = build(write=False)
    bad = tally_problems(published)
    if (fresh.get("rows") or []) != (published.get("rows") or []):
        bad.append("a live rebuild does not reproduce the published rows")
    if fresh.get("verdict") != published.get("verdict"):
        bad.append("a live rebuild reads a different verdict: %r != %r"
                   % (fresh.get("verdict"), published.get("verdict")))
    for b in bad:
        print("BAD %s" % b)
    print("verify %s" % ("clean" if not bad else "%d problem(s)" % len(bad)))
    return 0 if not bad else 1


# ----------------------------------------------------------------------------- selftest


def selftest() -> int:
    ok = total = 0

    def leg(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL %s" % name)

    leg("a card value is its own dialect", dialect_of_value("E271") == D_CARD)
    leg("a script stem is not a card", dialect_of_value("e271_donor_choice_sensitivity") == D_STEM)
    leg("a study id is its own dialect", dialect_of_value("FUND-DIVLOWVOL-P1") == D_STUDY)
    leg("a prereg path is its own dialect",
        dialect_of_value("research/shortline/AH_PANEL.md") == D_PREREG)
    leg("prose is other text", dialect_of_value("see E458 for the population") == D_OTHER)
    leg("a non-string value has no dialect", dialect_of_value(458) == D_NOT_STR)
    leg("a stem is not a study id even when it ends in _p1",
        dialect_of_value("e271_p1") == D_STEM)
    leg("the producer's own card comes from its file name",
        _filename_card("scripts/e271_donor_choice_sensitivity.py") == "E271")
    leg("a non-study script has no filename card", _filename_card("scripts/smoke_test.py") is None)
    src = '"""E271 -- a study.\n\nE262 proved something else.\n"""\nX = 1\n'
    ids = producer_identities(src)
    leg("a docstring card is found", "E271" in ids["docstring_cards"])
    leg("a cited card in the docstring is published as a citation, not ownership",
        "E262" in ids["docstring_cards"])
    leg("the docstring head is published", ids["docstring_head"].startswith("E271"))
    const = 'CARD = "E271"\nOTHER = "E262"\n'
    leg("a module constant card is found", "E271" in producer_identities(const)["constant_cards"])
    keys = producer_identities('d = {"study": s, "rows": r, "card": "E1"}\n')["identity_keys"]
    leg("an identity-named dict key is found", keys == ["card", "study"])
    leg("a non-identity dict key is not counted",
        producer_identities('d = {"title": t}\n')["identity_keys"] == [])
    p = {"source": "scripts/e271_x.py", "card_from_filename": "E271",
         "docstring_cards": ["E271"], "docstring_study_ids": [], "docstring_prereg_paths": []}
    leg("the needed field is the card the filename already spells",
        needed_field([p]) == {"name": "card", "value": "E271", "from": "scripts/e271_x.py"})
    leg("a producer with no identity needs no field",
        needed_field([{"source": "scripts/x.py", "card_from_filename": None,
                       "docstring_cards": [], "docstring_study_ids": [],
                       "docstring_prereg_paths": []}])["name"] is None)
    leg("a payload carrying study-as-stem is a dialect class",
        class_of_face({"study": {"value": "e271_x", "dialect": D_STEM}}, [p]) == C_DIALECT)
    leg("a payload carrying a card is its own class",
        class_of_face({"card": {"value": "E271", "dialect": D_CARD}}, [p]) == C_ALREADY)
    leg("a payload with no identity field but a knowing producer is the field class",
        class_of_face({}, [p]) == C_NO_FIELD)
    leg("a payload with no identity field and a blank producer is the producer class",
        class_of_face({}, [{"source": "scripts/x.py", "card_from_filename": None,
                            "docstring_cards": [], "docstring_study_ids": [],
                            "docstring_prereg_paths": []}]) == C_NO_PRODUCER)
    leg("a stem naming its own producer reads as the author",
        study_field_reading({"study": {"value": "e271_x", "dialect": D_STEM}},
                            [{"source": "scripts/e271_x.py"}])["reading"] == R_AUTHOR)
    leg("a stem naming somebody else's producer is not owned",
        study_field_reading({"study": {"value": "e271_x", "dialect": D_STEM}},
                            [{"source": "scripts/e999_y.py"}])["owned_by_one_of_its_producers"] is False)
    leg("a stem a producer pinned as a constant reads as a subject",
        study_field_reading(
            {"study": {"value": "e323_y", "dialect": D_STEM}},
            [{"source": "scripts/e361_z.py", "payload_stems_it_names_as_a_constant": ["e323_y"]}]
        )["reading"] == R_SUBJECT)
    leg("a stem nobody names reads as foreign",
        study_field_reading({"study": {"value": "e323_y", "dialect": D_STEM}},
                            [{"source": "scripts/e361_z.py"}])["reading"] == R_FOREIGN)
    leg("a payload with no stem has no reading",
        study_field_reading({}, [])["reading"] == R_NOT_A_STEM)
    leg("the author reading wins over the constant reading when a producer owns the stem",
        study_field_reading(
            {"study": {"value": "e271_x", "dialect": D_STEM}},
            [{"source": "scripts/e271_x.py",
              "payload_stems_it_names_as_a_constant": ["e271_x"]}])["reading"] == R_AUTHOR)
    leg("subject reading needs the constant to be in the producer that pins it",
        study_field_reading(
            {"study": {"value": "e323_y", "dialect": D_STEM}},
            [{"source": "scripts/e361_z.py", "payload_stems_it_names_as_a_constant": ["e999_q"]}]
        )["reading"] == R_FOREIGN)
    leg("a subject pinned in a module constant is visible to producer_identities",
        "e323_y" in producer_identities('STUDY = "e323_y"\n')["constant_values"])
    leg("an empty population is its own verdict",
        verdict_for(0, {}, {}) == V_EMPTY)
    leg("a fully repaired population is its own verdict",
        verdict_for(2, {c: (2 if c == C_ALREADY else 0) for c in CLASSES}, {}) == V_ALREADY)
    leg("a dominant dialect reading is the headline even with one missing field",
        verdict_for(12, {C_ALREADY: 0, C_DIALECT: 11, C_NO_FIELD: 1, C_NO_PRODUCER: 0}, {})
        == V_DOMINANT_DIALECT)
    leg("a dominant missing field is its own verdict",
        verdict_for(3, {C_ALREADY: 0, C_DIALECT: 0, C_NO_FIELD: 3, C_NO_PRODUCER: 0}, {})
        == V_DOMINANT_NO_FIELD)
    leg("a producer gap across the board is its own verdict",
        verdict_for(2, {c: (2 if c == C_NO_PRODUCER else 0) for c in CLASSES}, {})
        == V_DOMINANT_NO_PRODUCER)
    leg("the dominant class needs a majority, and a tie is not one",
        verdict_for(4, {C_ALREADY: 0, C_DIALECT: 2, C_NO_FIELD: 2, C_NO_PRODUCER: 0}, {})
        == V_SPLIT)
    leg("a bare majority of dialect readings is the headline",
        verdict_for(4, {C_ALREADY: 0, C_DIALECT: 3, C_NO_FIELD: 1, C_NO_PRODUCER: 0}, {})
        == V_DOMINANT_DIALECT)
    leg("a three-way split is not reported as a dominant class",
        verdict_for(9, {C_ALREADY: 3, C_DIALECT: 3, C_NO_FIELD: 1, C_NO_PRODUCER: 2}, {})
        == V_SPLIT)
    leg("the class vocabulary is closed", set(CLASSES) == {C_ALREADY, C_DIALECT, C_NO_FIELD,
                                                          C_NO_PRODUCER})
    leg("the reading vocabulary is closed",
        set(READINGS) == {R_AUTHOR, R_SUBJECT, R_FOREIGN, R_NOT_A_STEM})
    leg("the dialect vocabulary is closed",
        set(DIALECTS) == {D_CARD, D_STUDY, D_PREREG, D_STEM, D_OTHER, D_NOT_STR})
    leg("the verdict vocabulary is closed", set(VERDICT_VOCAB) == {
        V_EMPTY, V_ALREADY, V_DOMINANT_DIALECT, V_DOMINANT_NO_FIELD, V_DOMINANT_NO_PRODUCER,
        V_SPLIT})
    leg("this study's own face is not in its own population",
        all(r.get("face") != "results/state_tilt/" + FACE_NAME for r in flagged_rows()))
    print("%d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        payload = build(write=True)
        print(json.dumps(payload["summary"], ensure_ascii=False, sort_keys=True)[:900])
        print(payload["verdict"])
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print("usage: python scripts/e460_facegap.py run|check|verify|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))