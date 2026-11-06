"""E463 -- which study does a face join when two read names disagree?

E462 published that 4 faces (2 file pairs) carry more than one identity value, and that the shape is
common: 89 of 526 graded faces declare both `card` and `study`.  Where the two values agree the
extra name is a synonym; where they disagree the face is joined to two different studies depending
on which name a consumer keys on, and nothing in the payload arbitrates.  NAMERESOLVE-2026-11-04
declares card=E413 beside study=E421.

Three measurements, published separately so a zero in one cannot be read as a zero in another:

  S  split population -- every face E462 graded that declares more than one identity VALUE, with
                         the values per name and whether the two read voices disagree at all (the
                         89 both-name faces are the denominator, the disagreeing 4 are the subject).
  C  consumer binding -- for each such face, the non-producer sources that NAME it, the declared
                         identity names each of them READS, and therefore the value each consumer
                         ends up bound to.  A consumer that reads both names must choose and the
                         payload gives it no rule, so those are counted apart.
  P  producer voice   -- whether the producers of the two studies the names point at (the cards
                         named by the values) themselves name this face, i.e. whether either side
                         is aware the face is shared.

Run:      python scripts/e463_identity_split.py run
Verify:   python scripts/e463_identity_split.py verify     (re-derives from the live tree)
Check:    python scripts/e463_identity_split.py check      (tallies re-derive from the face)
Selftest: python scripts/e463_identity_split.py selftest
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
import e461_identity_consumers as e461  # noqa: E402  (key_sites / READ_KINDS / norm_stem)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "identitysplit_latest.json"
DATED_PREFIX = "IDENTITYSPLIT"
CARD = "E463-WHICH-STUDY-A-FACE-JOINS-WHEN-TWO-READ-NAMES-DISAGREE"
PARENT_FACE = "identitydialect_latest.json"

# The whole identity family reads identity names as names, so every member would vote itself a
# consumer of the faces it grades.  Excluded by name, and the exclusion is published.
SELF_SKIP = ("e461_", "e462_", "e463_", "run_e461", "run_e462", "run_e463")
MAX_READ_BYTES = 2 * 1024 * 1024
MAX_ROWS = 500
MAX_CONSUMERS_PER_FACE = 40
# A source naming more faces than this is a census reader, not a face-specific consumer (E461 rule).
BROAD_NAMER_FACES = 10

C_NONE = "no_source_outside_the_producer_names_this_face"
C_ONE_NAME = "consumers_read_one_of_the_names_so_each_binds_exactly_one_study"
C_BOTH = "some_consumer_reads_both_names_and_must_choose_with_no_rule_in_the_payload"
CONSUMER_CLASSES = (C_NONE, C_ONE_NAME, C_BOTH)

V_EMPTY = "no_graded_face_declares_two_identity_values"
V_AGREE = "every_multi_name_face_names_one_study_on_every_voice"
V_ONE_NAME = "the_disagreeing_faces_are_read_through_one_name_only_so_one_study_is_joined"
V_SPLIT = "consumers_of_one_face_bind_it_to_two_different_studies"
VERDICT_VOCAB = (V_EMPTY, V_AGREE, V_ONE_NAME, V_SPLIT)


# ----------------------------------------------------------------------------- helpers


def _load(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def is_own_output(rel):
    base = os.path.basename(rel)
    if base == FACE_NAME:
        return True
    return base.startswith(DATED_PREFIX + "-") and base.endswith(".json")


def split_rows(parent_rows):
    """Faces declaring two or more distinct identity values (E462's own columns, machine-read)."""
    out = []
    for row in parent_rows:
        vals = row.get("distinct_declared_values") or []
        if len(vals) < 2:
            continue
        decl = row.get("declared_values") or {}
        out.append({
            "face": row["face"],
            "family": row.get("family"),
            "declared_values": {f: list(v) for f, v in decl.items()},
            "read_names": list(row.get("read_names") or []),
            "never_read_names": list(row.get("never_read_names") or []),
            "producers": list(row.get("producers") or []),
            "read_voices_disagree": bool(row.get("read_voices_disagree")),
        })
    return out


# ----------------------------------------------------------------------------- corpus


def corpus(skip_self=True):
    """[(rel, literals, key_sites, face_stems_named, breadth)] over the repo's .py corpus."""
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
        lits = e461.string_constants(tree)
        stems = set()
        for val in lits:
            v = val.strip()
            if not e461.JSON_NAME_RE.match(v):
                continue
            stem = e461.norm_stem(v)
            if stem:
                stems.add(stem)
        out.append((rel, lits, e461.key_sites(tree), stems))
    breadth = {}
    for rel, _l, _s, stems in out:
        for stem in stems:
            breadth.setdefault(stem, set()).add(rel)
    return [(rel, lits, sites, stems) for rel, lits, sites, stems in out], breadth, errors


def producers_of_card(card_id, rels, lits_by_rel):
    """Producers of a card id: files that WRITE it as an identity value or carry it in the name."""
    hits = []
    for rel in rels:
        base = os.path.basename(rel).lower()
        if card_id.lower() in base:
            hits.append(rel)
            continue
        lits = lits_by_rel.get(rel) or set()
        if any(card_id == v.strip() for v in lits):
            hits.append(rel)
    return sorted(set(hits))


# ----------------------------------------------------------------------------- binding


def bind_consumers(rows, sources, breadth):
    """Per face: which non-producer source binds it to which study value through which name."""
    by_rel = {rel: (lits, sites, stems) for rel, lits, sites, stems in sources}
    graded = []
    for row in rows:
        stem = e461.norm_stem(os.path.basename(row["face"]))
        declared = row["declared_values"]
        producers = set(row["producers"])
        namers = sorted(r for r in (breadth.get(stem) or set()) if r not in producers)
        consumers = []
        for rel in namers:
            lits, sites, _stems = by_rel[rel]
            read = sorted({f for f, kind, _ln in sites if kind in e461.READ_KINDS and f in declared})
            carried = sorted({v for v in (x.strip() for x in lits)
                              for vals in declared.values() if v in vals})
            binds = {f: declared[f][0] for f in read if declared.get(f)}
            consumers.append({
                "source": rel,
                "names_read": read,
                "values_carried": carried,
                "binds_to": binds,
                "binds_more_than_one_study": len(set(binds.values())) > 1,
                "face_specific": len(breadth.get(stem) or ()) <= BROAD_NAMER_FACES,
            })
        per_name = {}
        for name in declared:
            per_name[name] = sum(1 for c in consumers if name in c["names_read"])
        both = [c for c in consumers if c["binds_more_than_one_study"]]
        if both:
            cls = C_BOTH
        elif consumers:
            cls = C_ONE_NAME
        else:
            cls = C_NONE
        bound = sorted({v for c in consumers for v in c["binds_to"].values()})
        graded.append({
            "face": row["face"],
            "family": row.get("family"),
            "declared_values": declared,
            "read_names": row["read_names"],
            "never_read_names": row["never_read_names"],
            "read_voices_disagree": row["read_voices_disagree"],
            "producers": row["producers"][:3],
            "namers_outside_producer_count": len(namers),
            "consumers": consumers[:MAX_CONSUMERS_PER_FACE],
            "consumer_count": len(consumers),
            "consumers_per_name": per_name,
            "consumers_reading_both_names": len(both),
            "studies_bound": bound,
            "face_is_bound_to_more_than_one_study": len(bound) > 1,
            "class": cls,
        })
    return graded


def verdict_for(graded, multi_name_faces, disagreeing_faces):
    if not graded:
        return V_EMPTY
    if not disagreeing_faces:
        return V_AGREE
    split = [g for g in graded if g["face_is_bound_to_more_than_one_study"]]
    if split:
        return V_SPLIT
    return V_ONE_NAME


# ----------------------------------------------------------------------------- build


def build(write=True):
    parent = _load(os.path.join(OUTDIR, PARENT_FACE))
    parent_rows = parent.get("rows") or []
    rows = split_rows(parent_rows)
    both_names = [r for r in parent_rows
                  if {"card", "study"}.issubset(set(r.get("declared_fields") or []))]
    both_agree = [r for r in both_names
                  if len(set(r.get("distinct_declared_values") or [])) <= 1]

    sources, breadth, errors = corpus()
    lits_by_rel = {rel: lits for rel, lits, _s, _st in sources}
    rels = [rel for rel, _l, _s, _st in sources]
    graded = bind_consumers(rows, sources, breadth)

    # P: does the card each voice names have a producer that knows this face is shared?
    cards = sorted({v for g in graded for vals in g["declared_values"].values() for v in vals})
    card_producers = {c: producers_of_card(c, rels, lits_by_rel) for c in cards}
    for g in graded:
        stem = e461.norm_stem(os.path.basename(g["face"]))
        g["cards_named"] = sorted({v for vals in g["declared_values"].values() for v in vals})
        g["card_producers_that_name_the_face"] = {
            c: sorted(r for r in card_producers.get(c, []) if stem in (breadth.get(stem) or set())
                      and r in (breadth.get(stem) or set()))
            for c in g["cards_named"]
        }

    disagreeing = [g for g in graded if len(g["studies_bound"]) > 1 or g["read_voices_disagree"]]
    summary = {
        "card": CARD,
        "corpus_sources": len(sources),
        "corpus_parse_errors": len(errors),
        "multi_name_faces_in_the_population": len(both_names),
        "multi_name_faces_whose_names_agree": len(both_agree),
        "faces_declaring_two_or_more_identity_values": len(graded),
        "faces_whose_read_voices_disagree": sum(1 for g in graded if g["read_voices_disagree"]),
        "faces_bound_to_more_than_one_study_by_a_consumer": sum(
            1 for g in graded if g["face_is_bound_to_more_than_one_study"]),
        "faces_with_a_consumer_outside_the_producer": sum(
            1 for g in graded if g["consumer_count"] > 0),
        "consumer_classes": {c: sum(1 for g in graded if g["class"] == c)
                             for c in CONSUMER_CLASSES},
        "consumers_total": sum(g["consumer_count"] for g in graded),
        "consumers_reading_both_names": sum(
            g["consumers_reading_both_names"] for g in graded),
        "consumers_per_name": {
            name: sum((g["consumers_per_name"] or {}).get(name, 0) for g in graded)
            for name in sorted({n for g in graded for n in g["declared_values"]})
        },
        "studies_bound_per_face": {g["face"]: g["studies_bound"] for g in graded},
        "faces_where_no_consumer_binds_any_study": sum(
            1 for g in graded if not g["studies_bound"]),
        "card_producers": {c: card_producers[c][:5] for c in cards},
        "cards_with_a_producer_that_names_the_face": {
            c: sum(1 for g in graded
                   if c in (g.get("cards_named") or [])
                   and g["card_producers_that_name_the_face"].get(c))
            for c in cards
        },
    }
    face = {
        "card": CARD,
        "study": "E463",
        "title": "which study a face joins when two read names disagree",
        "evidence_cutoff": parent.get("evidence_cutoff"),
        "population_source": (
            "the rows of E462's " + PARENT_FACE + " that declare two or more distinct identity "
            "values (machine-read from that face); consumers re-derived from e451.walk_py minus "
            "this family's own instruments (" + "/".join(SELF_SKIP) + " + this face), non-producer"
            " namers only"
        ),
        "verdict": verdict_for(graded, len(both_names), disagreeing),
        "verdict_vocab": list(VERDICT_VOCAB),
        "consumer_classes": list(CONSUMER_CLASSES),
        "read_kinds": list(e461.READ_KINDS),
        "summary": summary,
        "rows": graded[:MAX_ROWS],
        "parse_errors": errors[:50],
        "method_limits": [
            "static: a consumer is a source that names the face stem AND reads one of the declared "
            "identity names; a consumer reaching the name through a computed key is invisible",
            "a name 'read' is a dict-key read site (subscript load / get / pop / in probe); a "
            "consumer that reads the face's whole payload and picks a field by a variable carries "
            "no name and is not counted",
            "binds_to assigns the value the face declares under the name the consumer reads; a "
            "consumer that ignores the payload and hard-codes a study id is counted in "
            "values_carried, not in binds_to",
            "producer detection for a card is a filename prefix or a literal equal to the card id, "
            "so a producer that names its card only in a docstring sentence is missed",
        ],
    }
    if write:
        os.makedirs(OUTDIR, exist_ok=True)
        for name in (FACE_NAME, "%s-%s.json" % (
                DATED_PREFIX, (face.get("evidence_cutoff") or "undated").split()[0])):
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
    if s.get("faces_declaring_two_or_more_identity_values") != len(rows):
        problems.append("face count %r != rows %r"
                        % (s.get("faces_declaring_two_or_more_identity_values"), len(rows)))
    for cls in CONSUMER_CLASSES:
        got = sum(1 for r in rows if r.get("class") == cls)
        if s.get("consumer_classes", {}).get(cls) != got:
            problems.append("consumer class %s: published %r rows %r"
                            % (cls, s.get("consumer_classes", {}).get(cls), got))
    if s.get("faces_whose_read_voices_disagree") != sum(
            1 for r in rows if r.get("read_voices_disagree")):
        problems.append("read-voice disagreement total does not re-derive from the rows")
    if s.get("faces_bound_to_more_than_one_study_by_a_consumer") != sum(
            1 for r in rows if r.get("face_is_bound_to_more_than_one_study")):
        problems.append("split-face total does not re-derive from the rows")
    if s.get("faces_with_a_consumer_outside_the_producer") != sum(
            1 for r in rows if (r.get("consumer_count") or 0) > 0):
        problems.append("consumer-bearing face total does not re-derive from the rows")
    if s.get("consumers_total") != sum(r.get("consumer_count") or 0 for r in rows):
        problems.append("consumer total does not re-derive from the rows")
    if s.get("consumers_reading_both_names") != sum(
            r.get("consumers_reading_both_names") or 0 for r in rows):
        problems.append("both-name consumer total does not re-derive from the rows")
    if s.get("faces_where_no_consumer_binds_any_study") != sum(
            1 for r in rows if not (r.get("studies_bound") or [])):
        problems.append("unbound face total does not re-derive from the rows")
    per_name = {}
    for r in rows:
        for name, n in (r.get("consumers_per_name") or {}).items():
            per_name[name] = per_name.get(name, 0) + n
    if s.get("consumers_per_name") != {k: per_name.get(k, 0)
                                       for k in s.get("consumers_per_name") or {}}:
        problems.append("per-name consumer counts do not re-derive from the rows")
    for r in rows:
        names_read = {n for c in (r.get("consumers") or []) for n in (c.get("names_read") or [])}
        for name in r.get("declared_values") or {}:
            got = sum(1 for c in (r.get("consumers") or []) if name in (c.get("names_read") or []))
            if (r.get("consumers_per_name") or {}).get(name) != got:
                problems.append("row %s per-name count for %s does not re-derive"
                                % (r.get("face"), name))
        bound = sorted({v for c in (r.get("consumers") or [])
                        for v in (c.get("binds_to") or {}).values()})
        if sorted(r.get("studies_bound") or []) != bound:
            problems.append("row %s studies_bound does not re-derive from its consumers"
                            % r.get("face"))
        if bool(r.get("face_is_bound_to_more_than_one_study")) != (len(bound) > 1):
            problems.append("row %s split flag does not re-derive" % r.get("face"))
        if r.get("class") == C_NONE and r.get("consumer_count"):
            problems.append("row %s is classed unread but carries consumers" % r.get("face"))
        if r.get("class") == C_BOTH and not (r.get("consumers_reading_both_names") or 0) > 0:
            problems.append("row %s is classed split without a both-name consumer" % r.get("face"))
        if not names_read <= set(r.get("declared_values") or {}):
            problems.append("row %s consumer reads a name the face does not declare"
                            % r.get("face"))
    if face.get("verdict") != verdict_for(
            rows,
            s.get("multi_name_faces_in_the_population") or 0,
            [r for r in rows if r.get("read_voices_disagree")]):
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

    leg("own instrument source is skipped by name",
        any("e462_identity_dialect.py".startswith(s) for s in SELF_SKIP))
    leg("own face is skipped by name", is_own_output("results/state_tilt/" + FACE_NAME))
    leg("a dated own output is skipped",
        is_own_output("results/state_tilt/%s-2026-11-06.json" % DATED_PREFIX))
    leg("a neighbour face is not own output",
        not is_own_output("results/state_tilt/identitydialect_latest.json"))

    # population: only multi-value rows enter, and the values are carried verbatim
    parent_rows = [
        {"face": "results/x/SPLIT-2026-11-06.json", "family": "x", "producers": ["p.py"],
         "declared_values": {"card": ["E413"], "study": ["E421"]},
         "read_names": ["card", "study"], "never_read_names": [],
         "distinct_declared_values": ["E413", "E421"], "read_voices_disagree": True},
        {"face": "results/x/AGREE-2026-11-06.json", "family": "x", "producers": ["p.py"],
         "declared_values": {"card": ["E1"], "study": ["E1"]},
         "read_names": ["card", "study"], "never_read_names": [],
         "distinct_declared_values": ["E1"], "read_voices_disagree": False},
    ]
    rows = split_rows(parent_rows)
    leg("only a face with two distinct values enters the population", len(rows) == 1)
    leg("a synonym pair stays out", rows[0]["face"].endswith("SPLIT-2026-11-06.json"))

    # binding classifier on a synthetic corpus
    sources = [
        ("scripts/card_reader.py", {"SPLIT-2026-11-06.json"},
         [("card", e461.K_LOAD, 1)], {"split"}),
        ("scripts/study_reader.py", {"SPLIT-2026-11-06.json"},
         [("study", e461.K_GET, 2)], {"split"}),
        ("scripts/both_reader.py", {"SPLIT-2026-11-06.json"},
         [("card", e461.K_LOAD, 3), ("study", e461.K_LOAD, 4)], {"split"}),
    ]
    breadth = {}
    for rel, _l, _s, stems in sources:
        for stem in stems:
            breadth.setdefault(stem, set()).add(rel)
    graded = bind_consumers(rows, sources, breadth)
    g = graded[0]
    leg("every non-producer namer becomes a consumer", g["consumer_count"] == 3)
    leg("a card reader binds the card's study",
        g["consumers_per_name"]["card"] == 2 and g["consumers_per_name"]["study"] == 2)
    leg("one face is bound to two different studies",
        g["face_is_bound_to_more_than_one_study"] is True
        and sorted(g["studies_bound"]) == ["E413", "E421"])
    leg("the consumer that reads both names must choose",
        g["consumers_reading_both_names"] == 1 and g["class"] == C_BOTH)
    leg("verdict is split when one face is bound twice",
        verdict_for(graded, 2, [g]) == V_SPLIT)

    # a single-name consumer population is not a split, and agreeing names are not disagreeing
    breadth_one = {}
    for rel, _l, _s, stems in sources[:1]:
        for stem in stems:
            breadth_one.setdefault(stem, set()).add(rel)
    one = bind_consumers(rows, sources[:1], breadth_one)
    leg("a one-name consumer binds exactly one study",
        one[0]["studies_bound"] == ["E413"] and one[0]["class"] == C_ONE_NAME)
    leg("verdict is one-name when nothing is bound twice",
        verdict_for(one, 2, one) == V_ONE_NAME)
    leg("verdict is agree when no read voice disagrees",
        verdict_for(one, 2, []) == V_AGREE)
    leg("verdict is empty on an empty population", verdict_for([], 0, []) == V_EMPTY)

    # the producer does not count as a consumer of its own face
    solo = bind_consumers([{"face": rows[0]["face"], "family": "x", "producers": [
        "scripts/card_reader.py"], "declared_values": rows[0]["declared_values"],
        "read_names": rows[0]["read_names"], "never_read_names": [],
        "read_voices_disagree": True}], sources, breadth)
    leg("a producer's own read is not a consumer binding",
        solo[0]["consumer_count"] == 2)
    leg("an unnamed face has no consumer", bind_consumers(rows, [], {})[0]["class"] == C_NONE)

    # a published face whose tallies drift must be refused
    face = {
        "verdict": V_ONE_NAME,
        "summary": {
            "multi_name_faces_in_the_population": 2,
            "faces_declaring_two_or_more_identity_values": 1,
            "faces_whose_read_voices_disagree": 1,
            "faces_bound_to_more_than_one_study_by_a_consumer": 0,
            "faces_with_a_consumer_outside_the_producer": 1,
            "consumer_classes": {c: 0 for c in CONSUMER_CLASSES},
            "consumers_total": 1,
            "consumers_reading_both_names": 0,
            "consumers_per_name": {"card": 1, "study": 0},
            "faces_where_no_consumer_binds_any_study": 0,
        },
        "rows": [{
            "face": "results/x/SPLIT-2026-11-06.json",
            "declared_values": {"card": ["E413"], "study": ["E421"]},
            "read_voices_disagree": True,
            "consumer_count": 1,
            "consumers": [{"source": "a.py", "names_read": ["card"],
                           "values_carried": [], "binds_to": {"card": "E413"}}],
            "consumers_per_name": {"card": 1, "study": 0},
            "consumers_reading_both_names": 0,
            "studies_bound": ["E413"],
            "face_is_bound_to_more_than_one_study": False,
            "class": C_ONE_NAME,
        }],
    }
    leg("gate refuses a consumer class tally that does not re-derive",
        any("consumer class" in p for p in tally_problems(face)))
    face["summary"]["consumer_classes"][C_ONE_NAME] = 1
    leg("gate accepts a consistent one-name face", tally_problems(face) == [])
    face["summary"]["consumers_per_name"] = {"card": 3, "study": 0}
    leg("gate refuses a per-name count that does not re-derive",
        any("per-name" in p for p in tally_problems(face)))
    face["summary"]["consumers_per_name"] = {"card": 1, "study": 0}
    face["rows"][0]["studies_bound"] = ["E413", "E421"]
    leg("gate refuses a split claim with consumers that bind one study",
        any("studies_bound" in p for p in tally_problems(face)))

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
        print("multi-name faces:", s["multi_name_faces_in_the_population"],
              "| agreeing:", s["multi_name_faces_whose_names_agree"],
              "| multi-value faces:", s["faces_declaring_two_or_more_identity_values"])
        print("consumers:", s["consumers_total"],
              "| per name:", s["consumers_per_name"],
              "| both-name:", s["consumers_reading_both_names"])
        print("bound to two studies:", s["faces_bound_to_more_than_one_study_by_a_consumer"])
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
    print("usage: e463_identity_split.py [run|verify|check|selftest]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

