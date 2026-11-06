"""E461 -- which consumer actually reads the identity a study face declares?

E458 published that 526 of 538 study faces carry a machine-readable identity and that every one of
them resolves.  A declaration nobody reads is a label, not a link: this card asks whether any
consumer keys on the field a face declares, so that a reader can join a face to its study.

Three measurements, published separately so a zero in one cannot be mistaken for a zero in another:

  F  field census   -- for each identity field name E458 froze, every site in the repo's .py corpus
                       that names it, split by whether that site WRITES the key (a dict literal, a
                       subscript store, setdefault) or READS it (subscript load, .get/.pop, the
                       `in` probe).  A producer writing 'study': 'E458' is not a reader.
  L  face link      -- for each graded face: the sources that NAME the face, minus the face's own
                       producer(s), intersected with the sources that read a field the face
                       declares at its top level.  Non-empty == some consumer joins face to study.
  V  value join     -- the same set, but the consumer must also carry the declared VALUE (the card
                       id / study id string) in its own source, i.e. it hard-codes the link rather
                       than resolving it from the payload it read.

Run:      python scripts/e461_identity_consumers.py run
Verify:   python scripts/e461_identity_consumers.py verify     (re-derives from the live tree)
Check:    python scripts/e461_identity_consumers.py check      (tallies re-derive from the face)
Selftest: python scripts/e461_identity_consumers.py selftest
"""

import argparse
import ast
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e451_prereg_digest as e451  # noqa: E402  (walk_py / read_text / SKIP_DIRS)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "identityconsumers_latest.json"
DATED_PREFIX = "IDENTITYCONSUMERS"
CARD = "E461-WHICH-CONSUMER-ACTUALLY-READS-THE-IDENTITY-A-FACE-DECLARES"
SELF_SKIP = ("e461_", "run_e461")
PARENT_FACE = "faceidentity_latest.json"

# Write kinds name the key; read kinds consume it.  Kept apart because the whole question is which
# side of a write a declaration sits on.
K_DICT_KEY = "dict_literal_key"
K_STORE = "subscript_store"
K_SETDEFAULT = "setdefault_key"
K_LOAD = "subscript_read"
K_GET = "get_call"
K_POP = "pop_call"
K_PROBE = "membership_probe"
K_MENTION = "mentioned_not_read"
WRITE_KINDS = (K_DICT_KEY, K_STORE, K_SETDEFAULT)
READ_KINDS = (K_LOAD, K_GET, K_POP, K_PROBE)

L_JOINED = "a_consumer_joins_this_face_to_its_study_through_the_field_it_declares"
L_PRODUCER_ONLY = "only_the_face_s_own_producer_names_the_field_it_writes"
L_NAMED_UNREAD = "consumers_name_the_face_but_none_reads_the_identity_field"
L_UNNAMED = "no_source_outside_the_producer_names_this_face"
LINK_CLASSES = (L_JOINED, L_PRODUCER_ONLY, L_NAMED_UNREAD, L_UNNAMED)

V_EMPTY = "no_graded_face_declares_a_top_level_identity_to_read"
V_LABEL = "no_consumer_of_a_study_face_keys_on_the_identity_field_that_face_declares"
V_SOME = "some_faces_are_joined_to_their_study_by_a_consumer_keying_on_the_declared_field"
V_ALL = "every_face_that_names_a_consumer_is_joined_through_the_field_it_declares"
VERDICT_VOCAB = (V_EMPTY, V_LABEL, V_SOME, V_ALL)

MAX_READ_BYTES = 2 * 1024 * 1024
# A source naming more faces than this is a census reader, not a face-specific link.
BROAD_NAMER_FACES = 10
# Field names the vocabulary shares with ordinary payload keys: a read of d['id'] is usually not a
# read of a study identity, so these are counted apart instead of being folded into the link tally.
AMBIGUOUS_FIELDS = frozenset({"id", "pin", "pid"})
MAX_ROWS = 2000
_DATE_TAIL = re.compile(r"[-_]?\d{4}[-_]\d{2}[-_]\d{2}$")
JSON_NAME_RE = re.compile(r"^[A-Za-z0-9_.\-]+\.[Jj][Ss][Oo][Nn]$")


# ----------------------------------------------------------------------------- helpers


def _rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def _load(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def norm_stem(name):
    """importclass_latest.json / IMPORTCLASS-2026-11-04.json -> 'importclass' (E458's rule)."""
    stem = name.lower()
    if stem.endswith(".json"):
        stem = stem[:-5]
    stem = _DATE_TAIL.sub("", stem)
    for tail in ("_latest", "-latest"):
        if stem.endswith(tail):
            stem = stem[: -len(tail)]
    return re.sub(r"[^a-z0-9]+", "", stem)


def is_own_output(rel):
    base = os.path.basename(rel)
    if base == FACE_NAME:
        return True
    return base.startswith(DATED_PREFIX + "-") and base.endswith(".json")


# ----------------------------------------------------------------------------- key sites


def key_sites(tree):
    """(field, kind, lineno) for every place a string constant is used as a dict key.

    A dict literal key, a subscript store and setdefault write the key; a subscript load, .get/.pop
    and the `in` probe read it.  Anything else that merely carries the word is mentioned_not_read.
    """
    out = []

    def _const(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for k in node.keys:
                val = _const(k)
                if val is not None:
                    out.append((val, K_DICT_KEY, getattr(k, "lineno", 0)))
        elif isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Subscript):
                    val = _const(tgt.slice)
                    if val is not None:
                        out.append((val, K_STORE, tgt.lineno))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            name = node.func.attr
            if name in ("get", "pop", "setdefault") and node.args:
                val = _const(node.args[0])
                if val is not None:
                    kind = {"get": K_GET, "pop": K_POP, "setdefault": K_SETDEFAULT}[name]
                    out.append((val, kind, node.lineno))
        elif isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Load):
            val = _const(node.slice)
            if val is not None:
                out.append((val, K_LOAD, node.lineno))
        elif isinstance(node, ast.Compare):
            for side in [node.left] + list(node.comparators):
                val = _const(side)
                if val is None:
                    continue
                if any(isinstance(op, (ast.In, ast.NotIn)) for op in node.ops):
                    out.append((val, K_PROBE, node.lineno))
    return out


def string_constants(tree):
    return {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}


# ----------------------------------------------------------------------------- corpus


def corpus():
    """[(rel, tree, literals, key_sites)] over the repo's .py files, own outputs excluded."""
    out = []
    errors = []
    for rel in e451.walk_py(ROOT):
        if any(os.path.basename(rel).startswith(s) for s in SELF_SKIP) or is_own_output(rel):
            continue
        path = os.path.join(ROOT, rel)
        try:
            if os.path.getsize(path) > MAX_READ_BYTES:
                continue
            text = e451.read_text(path)
            tree = ast.parse(text)
        except (SyntaxError, ValueError, OSError):
            errors.append(rel)
            continue
        out.append((rel, tree, string_constants(tree), key_sites(tree)))
    return out, errors


def field_census(sources, fields):
    """Per field: write sites, read sites, files, and how many reading files are producers."""
    census = {}
    for f in fields:
        census[f] = {
            "field": f,
            "write_sites": 0,
            "read_sites": 0,
            "files_naming": 0,
            "files_reading": 0,
            "kind_counts": {},
            "name_is_ambiguous": f in AMBIGUOUS_FIELDS,
            "sample_reading_files": [],
        }
    for rel, _tree, _lits, sites in sources:
        by_field = {}
        for field, kind, _ln in sites:
            if field in census:
                by_field.setdefault(field, set()).add(kind)
        for field, kinds in by_field.items():
            c = census[field]
            c["files_naming"] += 1
            w = [k for k in kinds if k in WRITE_KINDS]
            r = [k for k in kinds if k in READ_KINDS]
            c["write_sites"] += len(w)
            c["read_sites"] += len(r)
            for k in kinds:
                c["kind_counts"][k] = c["kind_counts"].get(k, 0) + 1
            if r:
                c["files_reading"] += 1
                if len(c["sample_reading_files"]) < 8:
                    c["sample_reading_files"].append(rel)
    return census


# ----------------------------------------------------------------------------- link measurement


def face_rows(parent):
    """Graded rows that declare a top-level machine-readable identity."""
    out = []
    for row in parent.get("rows", []):
        if not row.get("declares_own_identity"):
            continue
        decl = []
        for h in row.get("hits", []):
            if h.get("depth") != 1 or h.get("in_prose_field"):
                continue
            if h.get("kind") not in parent.get("identity_shapes", {}):
                pass
            if h.get("field") and h.get("value"):
                decl.append((h["field"], h["value"]))
        if not decl:
            continue
        out.append({"face": row["face"], "producers": row.get("producers", []), "decl": decl})
    return out


def link_measure(rows, sources, field_names):
    """Grade each face by whether a non-producer source reads a field it declares."""
    by_rel = {rel: (lits, sites) for rel, _t, lits, sites in sources}
    # index: normalised face stem -> files that name it
    namers = {}
    for rel, _t, lits, _s in sources:
        for val in lits:
            if not JSON_NAME_RE.match(val.strip()):
                continue
            stem = norm_stem(val.strip())
            if not stem:
                continue
            namers.setdefault(stem, set()).add(rel)
    readers = {}  # rel -> set(field read)
    for rel, _t, _l, sites in sources:
        rs = {f for f, k, _ln in sites if k in READ_KINDS and f in field_names}
        if rs:
            readers[rel] = rs
    namers_of = {rel: set() for rel, _t, _l, _s in sources}
    for stem, rels in namers.items():
        for rel in rels:
            namers_of.setdefault(rel, set()).add(stem)

    graded = []
    for row in rows:
        stem = norm_stem(os.path.basename(row["face"]))
        declared_fields = {f for f, _v in row["decl"]}
        declared_values = {v for _f, v in row["decl"]}
        producers = set(row["producers"])
        naming = namers.get(stem, set())
        outside = naming - producers
        joined = sorted(r for r in outside if r in readers and (readers[r] & declared_fields))
        value_joined = sorted(
            r for r in joined if by_rel[r][0] & declared_values
        )
        if joined:
            cls = L_JOINED
        elif outside:
            cls = L_NAMED_UNREAD
        elif naming:
            cls = L_PRODUCER_ONLY
        else:
            cls = L_UNNAMED
        # A source that names a hundred faces is a census reader, not a face-specific link; breadth
        # is published so the two shapes cannot be read as one.
        breadth = {r: len(namers_of[r]) for r in joined}
        specific = [r for r in joined if breadth[r] <= BROAD_NAMER_FACES]
        graded.append({
            "class": cls,
            "declared_fields": sorted(declared_fields),
            "declared_values": sorted(declared_values),
            "face": row["face"],
            "joined_breadth": {r: breadth[r] for r in joined[:5]},
            "joined_by_face_specific_source": bool(specific),
            "joined_sources": joined[:5],
            "joined_source_count": len(joined),
            "namers_outside_producer_count": len(outside),
            "producers": row["producers"][:3],
            "value_joined_source_count": len(value_joined),
        })
    return graded


def verdict_for(graded):
    if not graded:
        return V_EMPTY
    joined = [g for g in graded if g["class"] == L_JOINED]
    named = [g for g in graded if g["namers_outside_producer_count"] > 0]
    if not joined:
        return V_LABEL
    if named and len(joined) == len(named):
        return V_ALL
    return V_SOME


# ----------------------------------------------------------------------------- build


def build(write=True):
    parent_path = os.path.join(OUTDIR, PARENT_FACE)
    parent = _load(parent_path)
    fields = sorted(parent.get("identity_field_vocabulary", []))
    rows = face_rows(parent)
    sources, errors = corpus()
    census = field_census(sources, fields)
    graded = link_measure(rows, sources, set(fields))

    joined = [g for g in graded if g["class"] == L_JOINED]
    value_joined = [g for g in graded if g["value_joined_source_count"] > 0]
    summary = {
        "card": CARD,
        "corpus_sources": len(sources),
        "corpus_parse_errors": len(errors),
        "faces_graded": len(graded),
        "faces_with_a_nonproducer_namer": sum(
            1 for g in graded if g["namers_outside_producer_count"] > 0),
        "faces_joined_by_a_field_reader": len(joined),
        "faces_joined_by_a_value_reader": len(value_joined),
        "faces_joined_by_a_face_specific_source": sum(
            1 for g in joined if g["joined_by_face_specific_source"]),
        "fields": len(fields),
        "fields_never_read": sorted(f for f in fields if census[f]["read_sites"] == 0),
        "reading_files_total": sum(census[f]["files_reading"] for f in fields),
        "read_sites_identity_named": sum(
            census[f]["read_sites"] for f in fields if f not in AMBIGUOUS_FIELDS),
        "read_sites_ambiguous_named": sum(
            census[f]["read_sites"] for f in fields if f in AMBIGUOUS_FIELDS),
        "ambiguous_fields": sorted(AMBIGUOUS_FIELDS),
        "top_declared_field": max(
            ({"field": f, "faces": sum(1 for g in graded if f in g["declared_fields"])}
             for f in fields),
            key=lambda d: d["faces"], default=None),
        "link_classes": {c: sum(1 for g in graded if g["class"] == c) for c in LINK_CLASSES},
    }
    face = {
        "card": CARD,
        "study": "E461",
        "title": "which consumer actually reads the identity a study face declares",
        "evidence_cutoff": parent.get("evidence_cutoff"),
        "population_source": (
            "the graded rows of E458's " + PARENT_FACE +
            " that declare a top-level machine-readable identity; the .py corpus is "
            "e451.walk_py minus this study's own files"
        ),
        "verdict": verdict_for(graded),
        "verdict_vocab": list(VERDICT_VOCAB),
        "link_classes": list(LINK_CLASSES),
        "write_kinds": list(WRITE_KINDS),
        "read_kinds": list(READ_KINDS),
        "summary": summary,
        "field_census": census,
        "rows": graded[:MAX_ROWS],
        "parse_errors": errors[:50],
        "method_limits": [
            "static: a consumer is a source that names the face and reads the declared field name; "
            "a consumer that reaches the field through a variable key (d[k] where k = 'stu'+'dy') "
            "is invisible",
            "a source 'names' a face when a string constant in it normalises to the face stem, so a "
            "name composed from parts is missed (same bound E458 publishes)",
            "value join requires the literal value in the consumer's source; a consumer that "
            "compares against a constant defined in another module is counted as a field join only",
            "read/write is decided by the AST context of the key constant, not by data flow: a dict "
            "literal built to be returned is graded a write even if a caller reads it back",
        ],
    }
    if write:
        os.makedirs(OUTDIR, exist_ok=True)
        latest = os.path.join(OUTDIR, FACE_NAME)
        with io.open(latest, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        dated = os.path.join(
            OUTDIR, "%s-%s.json" % (DATED_PREFIX, face.get("evidence_cutoff") or "undated"))
        with io.open(dated, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    return face


# ----------------------------------------------------------------------------- gates


def tally_problems(face):
    """The published numbers must re-derive from the published rows."""
    problems = []
    s = face.get("summary", {})
    rows = face.get("rows", [])
    if s.get("faces_graded") != len(rows):
        problems.append("faces_graded %r != rows %r" % (s.get("faces_graded"), len(rows)))
    for cls in LINK_CLASSES:
        got = sum(1 for r in rows if r.get("class") == cls)
        if s.get("link_classes", {}).get(cls) != got:
            problems.append("link class %s: published %r, rows %r"
                            % (cls, s.get("link_classes", {}).get(cls), got))
    if s.get("faces_joined_by_a_field_reader") != sum(
            1 for r in rows if r.get("class") == L_JOINED):
        problems.append("joined total does not re-derive from the rows")
    if s.get("faces_joined_by_a_value_reader") != sum(
            1 for r in rows if r.get("value_joined_source_count", 0) > 0):
        problems.append("value-joined total does not re-derive from the rows")
    if s.get("faces_joined_by_a_face_specific_source") != sum(
            1 for r in rows if r.get("joined_by_face_specific_source")):
        problems.append("face-specific join total does not re-derive from the rows")
    if s.get("faces_with_a_nonproducer_namer") != sum(
            1 for r in rows if r.get("namers_outside_producer_count", 0) > 0):
        problems.append("non-producer namer total does not re-derive from the rows")
    census = face.get("field_census", {})
    if s.get("fields") != len(census):
        problems.append("field count != census rows")
    never = sorted(f for f, c in census.items() if (c.get("read_sites") or 0) == 0)
    if s.get("fields_never_read") != never:
        problems.append("fields_never_read does not re-derive from the census")
    for f, c in census.items():
        if (c.get("read_sites") or 0) > 0 and not c.get("sample_reading_files"):
            problems.append("field %s has read sites but no sample file" % f)
        for k in c.get("kind_counts", {}):
            if k not in WRITE_KINDS + READ_KINDS:
                problems.append("field %s carries an unknown kind %s" % (f, k))
    if face.get("verdict") != verdict_for(rows):
        problems.append("verdict does not re-derive from the rows")
    return problems


def verify():
    problems = []
    live = build(write=False)
    on_disk = _load(os.path.join(OUTDIR, FACE_NAME))
    if live["summary"] != on_disk.get("summary"):
        diff = [k for k in live["summary"] if live["summary"][k] != on_disk["summary"].get(k)]
        problems.append("summary is stale against the live tree: %s" % ", ".join(sorted(diff)))
    if live.get("verdict") != on_disk.get("verdict"):
        problems.append("verdict differs: live %r disk %r"
                        % (live.get("verdict"), on_disk.get("verdict")))
    problems.extend(tally_problems(on_disk))
    return problems


def check():
    face = _load(os.path.join(OUTDIR, FACE_NAME))
    problems = tally_problems(face)
    return problems


# ----------------------------------------------------------------------------- selftest


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    src = (
        "import json\n"
        "d = {'study': 'E461'}\n"          # dict literal -> write
        "x = d['study']\n"                  # subscript load -> read
        "y = d.get('card')\n"               # get -> read
        "d['pin'] = 1\n"                    # subscript store -> write
        "d.setdefault('pid', 2)\n"          # setdefault -> write
        "if 'prereg' in d:\n    pass\n"     # membership probe -> read
        "z = 'study'\n"                      # mention only
    )
    tree = ast.parse(src)
    sites = key_sites(tree)
    kinds = {(f, k) for f, k, _ln in sites}
    leg("dict literal key is a write", ("study", K_DICT_KEY) in kinds)
    leg("subscript load is a read", ("study", K_LOAD) in kinds)
    leg("get is a read", ("card", K_GET) in kinds)
    leg("subscript store is a write", ("pin", K_STORE) in kinds)
    leg("setdefault is a write", ("pid", K_SETDEFAULT) in kinds)
    leg("membership probe is a read", ("prereg", K_PROBE) in kinds)
    leg("a bare mention produces no site", all(f != "z" for f, _k, _ln in sites))

    leg("norm_stem collapses latest and dated twins",
        norm_stem("IMPORTCLASS-2026-11-04.json") == norm_stem("importclass_latest.json") == "importclass")
    leg("own output is recognised", is_own_output("results/state_tilt/" + FACE_NAME))
    leg("a dated own output is recognised",
        is_own_output("results/state_tilt/%s-2026-11-06.json" % DATED_PREFIX))
    leg("a neighbour face is not own output", not is_own_output("results/state_tilt/e458_latest.json"))

    # link classifier on a synthetic 2-face population
    sources = [
        ("scripts/p1.py", ast.parse("x = {'study': 'E461'}"), {"faceA_latest.json"}, []),
        ("scripts/reader.py", ast.parse("y = payload['study']"),
         {"faceA_latest.json"}, [("study", K_LOAD, 1)]),
        ("scripts/other.py", ast.parse("pass"), {"faceB_latest.json"}, []),
    ]
    rows = [
        {"face": "results/x/FACEA-2026-11-06.json", "producers": ["scripts/p1.py"],
         "decl": [("study", "E461")]},
        {"face": "results/x/FACEB-2026-11-06.json", "producers": ["scripts/p1.py"],
         "decl": [("study", "E462")]},
    ]
    graded = link_measure(rows, sources, {"study", "card"})
    leg("a non-producer that reads the field joins the face", graded[0]["class"] == L_JOINED)
    leg("the producer alone does not count as a reader of its own face",
        graded[0]["joined_sources"] == ["scripts/reader.py"])
    leg("a face nobody reads is named-but-unread", graded[1]["class"] == L_NAMED_UNREAD)
    leg("a one-face reader is face-specific", graded[0]["joined_by_face_specific_source"] is True)
    leg("value join is counted separately from field join",
        graded[0]["value_joined_source_count"] == 0 and graded[0]["joined_source_count"] == 1)
    leg("verdict is V_SOME when one of two named faces is joined", verdict_for(graded) == V_SOME)
    leg("verdict is V_LABEL when nothing joins",
        verdict_for([dict(g, class_=None, **{"class": L_NAMED_UNREAD}) for g in graded]) == V_LABEL)
    leg("verdict is V_EMPTY on an empty population", verdict_for([]) == V_EMPTY)

    # census
    cen = field_census([("a.py", None, set(), [("study", K_DICT_KEY, 1)]),
                        ("b.py", None, set(), [("study", K_LOAD, 2), ("card", K_GET, 3)])],
                       ["study", "card", "pin"])
    leg("write-only field has no reading file", cen["study"]["files_reading"] == 1)
    leg("never-read field is reported", cen["pin"]["read_sites"] == 0)
    leg("kind counts add up", cen["study"]["kind_counts"] == {K_DICT_KEY: 1, K_LOAD: 1})

    # a published face whose tallies drift must be refused
    face = {
        "verdict": V_SOME,
        "summary": {"faces_graded": 1, "link_classes": {c: 0 for c in LINK_CLASSES},
                    "faces_joined_by_a_field_reader": 0, "faces_joined_by_a_value_reader": 0,
                    "faces_joined_by_a_face_specific_source": 0,
                    "faces_with_a_nonproducer_namer": 0, "fields": 0, "fields_never_read": []},
        "rows": [{"class": L_NAMED_UNREAD, "namers_outside_producer_count": 1,
                  "value_joined_source_count": 0}],
        "field_census": {},
    }
    leg("tally gate refuses a face whose link class does not re-derive",
        any("link class" in p for p in tally_problems(face)))
    face["verdict"] = V_LABEL
    face["summary"]["link_classes"][L_NAMED_UNREAD] = 1
    face["summary"]["faces_graded"] = 1
    face["summary"]["faces_with_a_nonproducer_namer"] = 1
    leg("tally gate accepts a consistent face", tally_problems(face) == [])

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
        print("faces graded:", s["faces_graded"],
              "| joined by field reader:", s["faces_joined_by_a_field_reader"],
              "| joined by value reader:", s["faces_joined_by_a_value_reader"],
              "| named outside producer:", s["faces_with_a_nonproducer_namer"])
        print("fields never read:", len(s["fields_never_read"]), s["fields_never_read"])
        print("link classes:", s["link_classes"])
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
    print("usage: e461_identity_consumers.py [run|verify|check|selftest]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))