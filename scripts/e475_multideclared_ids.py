"""E475 -- of the 56 ids several sources declare, which are two producers and which are one restating itself?

E474 found that 56 stem-shaped identity values are declared as literals by more than one source, so
no channel on disk decides which script wrote the face.  Some of those are one producer restating
its id in a helper; others are genuinely two producers claiming one identity.

For each multi-declared id this card asks three questions and publishes the answers:

  C  carriers  -- which faces under results/ carry the id as an identity value (re-read from the
                  E474 face, not recomputed here).
  W  writers   -- of the declaring sources, which ones name one of those carrier faces in their own
                  source text (an output-path literal, or the face basename in a json.dump target).
  I  imports   -- do the declaring sources import one another (module name == the other's stem)?

Classification per id (pure function, selftested):

  two_independent_producers     -- at least two declaring sources each write a carrier face and
                                   neither imports the other
  one_producer_restated         -- exactly one declaring source writes the carriers and every other
                                   declaring source either imports it or is imported by it
  one_producer_plus_strangers   -- one writer, the rest declare the id but do not write or import
  no_writer_on_the_carriers     -- none of the declaring sources names a carrier face

Run:      python scripts/e475_multideclared_ids.py run
Check:    python scripts/e475_multideclared_ids.py check
Selftest: python scripts/e475_multideclared_ids.py selftest
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

import e451_prereg_digest as e451  # noqa: E402
import e461_identity_consumers as e461  # noqa: E402
import e474_identity_dialect_census as e474  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "multideclared_latest.json"
DATED_PREFIX = "MULTIDECLARED"
CARD = "E475-WHICH-OF-THE-56-MULTI-DECLARED-STUDY-IDS-ARE-TWO-PRODUCERS-AND-WHICH-ARE-ONE-RESTATING-ITSELF"
PARENT_FACE = "identitydialectcensus_latest.json"
CUTOFF_ENV = "E475_CUTOFF"

SELF_SKIP = ("e475_", "run_e475")

K_TWO = "two_independent_producers"
K_ONE = "one_producer_restated"
K_ONE_STRANGERS = "one_producer_plus_strangers"
K_NONE = "no_writer_on_the_carriers"
KINDS = (K_TWO, K_ONE, K_ONE_STRANGERS, K_NONE)


SKIP_DIRS = {".git", "results", "data", "Money02", "legacy", "_quarantine",
             "node_modules", "__pycache__"}
MAX_SOURCE_BYTES = 2 * 1024 * 1024


def _load(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def multi_ids_from_parent(rows):
    """Stem values the E474 face graded as declared_by_several_sources, deduplicated."""
    ids = set()
    for row in rows:
        for field in row.get("identity_fields") or []:
            if field.get("dialect") != e474.D_STEM:
                continue
            if field.get("stem_status") != e474.S_DECLARED_MANY:
                continue
            value = field.get("value") or ""
            ids.add(value[:-3] if value.endswith(".py") else value)
    return sorted(i for i in ids if i)


def declaring_sources(ids):
    """{id: [rel, ...]} for `ids` only, by one plain-text pass for the quoted literal.

    E474 built the tree-wide index from AST string constants for every .py in the repo (~20 min
    here).  Widening that to every quoted stem-shaped word was worse still: ordinary string
    literals (dict keys, config words) outnumber identity declarations by orders of magnitude and
    each one enters the import/AST phase.  So the scan is driven by the ids the parent face already
    graded -- the population is the ids a face actually carries, and the residue is published.
    """
    needles = {i: ('"%s"' % i, "'%s'" % i) for i in ids}
    out = {i: [] for i in ids}
    for dirpath, dirs, files in os.walk(ROOT):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.endswith(".py"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), ROOT).replace(os.sep, "/")
            if any(os.path.basename(rel).startswith(s) for s in SELF_SKIP):
                continue
            path = os.path.join(dirpath, name)
            try:
                if os.path.getsize(path) > MAX_SOURCE_BYTES:
                    continue
                text = e451.read_text(path)
            except OSError:
                continue
            for ident in ids:
                pair = needles[ident]
                if pair[0] in text or pair[1] in text:
                    out[ident].append(rel)
    return {k: sorted(set(v)) for k, v in out.items()}


def is_own_output(rel):
    base = os.path.basename(rel)
    if base in (FACE_NAME, FACE_NAME.replace("multideclared", "identitydialectcensus")):
        return True
    for prefix in (DATED_PREFIX, "IDENTITYDIALECTCENSUS"):
        if base.startswith(prefix + "-") and base.endswith(".json"):
            return True
    return any(base.startswith(s) for s in SELF_SKIP)


# --------------------------------------------------------------------------- pure functions


def carrier_faces(rows, ident):
    """Faces whose identity fields spell `ident` as a multi-declared stem (from the E474 face)."""
    out = []
    for row in rows:
        for field in row.get("identity_fields") or []:
            if field.get("dialect") != e474.D_STEM:
                continue
            if field.get("stem_status") != e474.S_DECLARED_MANY:
                continue
            value = field.get("value") or ""
            stem = value[:-3] if value.endswith(".py") else value
            if stem == ident:
                out.append(row.get("face"))
                break
    return sorted(set(f for f in out if f))


def names_a_face(text, faces):
    """Which of `faces` this source text spells (full relpath or basename)."""
    if not text or not faces:
        return []
    hits = []
    for face in faces:
        base = os.path.basename(face)
        if face in text or (len(base) > 8 and base in text):
            hits.append(face)
    return hits


def imported_modules(tree):
    """Set of module names this AST imports (first component of dotted names, and `from X`)."""
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                out.add(node.module.split(".")[0])
            elif node.level:
                for alias in node.names:
                    out.add(alias.name.split(".")[0])
    return out


def classify(declarers, writers, import_edges):
    """Kind for one id from the declaring sources, the writers among them, and the import graph.

    declarers     : [rel, ...]  sources that declare the id as a literal
    writers       : [rel, ...]  declarers that also name a carrier face in their own text
    import_edges  : [(a, b), ...]  a imports b (both restricted to declarers)
    """
    w = sorted(set(writers))
    if len(w) >= 2:
        linked = {(a, b) for a, b in import_edges}
        for i, a in enumerate(w):
            for b in w[i + 1:]:
                if (a, b) in linked or (b, a) in linked:
                    continue
                return K_TWO
        return K_ONE
    if len(w) == 1:
        owner = w[0]
        others = [d for d in declarers if d != owner]
        linked = {(a, b) for a, b in import_edges}
        if others and all((o, owner) in linked or (owner, o) in linked for o in others):
            return K_ONE
        return K_ONE_STRANGERS
    return K_NONE


# --------------------------------------------------------------------------- build


def build(write=True):
    parent_path = os.path.join(OUTDIR, PARENT_FACE)
    parent = _load(parent_path)
    rows = parent.get("rows") or []
    multi = multi_ids_from_parent(rows)
    index = declaring_sources(multi)
    multi = [i for i in multi if len(index.get(i) or []) > 1]
    parent_instances = int((parent.get("stem_resolution_totals") or {}).get(
        e474.S_DECLARED_MANY, 0))
    text_cache = {}
    trees = {}

    out_rows = []
    for ident in multi:
        declarers = sorted(set(index.get(ident) or []))
        faces = carrier_faces(rows, ident)
        writers = []
        for rel in declarers:
            if rel not in text_cache:
                try:
                    text_cache[rel] = e451.read_text(os.path.join(ROOT, rel))
                except OSError:
                    text_cache[rel] = ""
            if names_a_face(text_cache[rel], faces):
                writers.append(rel)
        import_edges = []
        stems = {rel: os.path.basename(rel)[:-3] for rel in declarers}
        for rel in declarers:
            if rel not in trees:
                try:
                    trees[rel] = ast.parse(text_cache.get(rel) or e451.read_text(
                        os.path.join(ROOT, rel)))
                except (SyntaxError, ValueError, OSError):
                    trees[rel] = None
            tree = trees.get(rel)
            if tree is None:
                continue
            mods = imported_modules(tree)
            for other in declarers:
                if other == rel:
                    continue
                if stems[other] in mods:
                    import_edges.append((rel, other))
        kind = classify(declarers, writers, import_edges)
        out_rows.append({
            "id": ident,
            "declaring_sources": declarers,
            "carrier_faces": faces,
            "writers": sorted(set(writers)),
            "import_edges": import_edges,
            "kind": kind,
        })

    totals = {k: 0 for k in KINDS}
    for r in out_rows:
        totals[r["kind"]] += 1
    shared = [r["id"] for r in out_rows if r["kind"] == K_TWO]
    orphaned = [r["id"] for r in out_rows if r["kind"] == K_NONE]
    cutoff = os.environ.get(CUTOFF_ENV) or "2026-11-07"
    face = {
        "card": CARD,
        "cutoff": cutoff,
        "evidence_cutoff": cutoff,
        "generated": cutoff,
        "verdict": ("some_ids_are_two_independent_producers" if shared
                    else "every_multi_declared_id_has_one_owner"),
        "population": {
            "parent_face": PARENT_FACE,
            "multi_declared_ids": len(multi),
            "parent_face_instances_with_that_status": parent_instances,
            "declaring_sources_indexed": sum(len(v) for v in index.values()),
            "scope": ("the population is the distinct stem VALUES the parent face graded "
                      "declared_by_several_sources (its 56 instances collapse to these values); "
                      "an id no face carries is not in scope because it decides no face"),
            "limit": ("a 'writer' is a source whose OWN TEXT spells a carrier face path or "
                      "basename; a producer that composes its output path at runtime is not a "
                      "writer here (E473 family), so K_NONE is 'no literal writer', not 'no "
                      "producer'.  Declarers come from a plain-text scan for a quoted literal, so "
                      "an id assembled by concatenation is invisible"),
        },
        "kind_totals": totals,
        "rows": out_rows,
        "residue": {
            "ids_with_two_independent_producers": shared,
            "ids_with_no_literal_writer": orphaned,
            "ids_with_no_carrier_face": sorted(r["id"] for r in out_rows if not r["carrier_faces"]),
        },
    }
    if write:
        if not os.path.isdir(OUTDIR):
            os.makedirs(OUTDIR)
        dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, cutoff))
        latest = os.path.join(OUTDIR, FACE_NAME)
        payload = json.dumps(face, indent=1, ensure_ascii=False)
        with io.open(dated, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(payload + "\n")
        with io.open(latest, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(payload + "\n")
        print("wrote", dated)
    return face


def check():
    face = _load(os.path.join(OUTDIR, FACE_NAME))
    problems = []
    ids = [r["id"] for r in face["rows"]]
    if len(ids) != len(set(ids)):
        problems.append("duplicate id rows")
    if sum(face["kind_totals"].values()) != len(ids):
        problems.append("kind totals do not sum to the row count")
    for r in face["rows"]:
        if not r["declaring_sources"] or len(r["declaring_sources"]) < 2:
            problems.append("id declared by fewer than two sources: %s" % r["id"])
        if any(w not in r["declaring_sources"] for w in r["writers"]):
            problems.append("writer not among declarers: %s" % r["id"])
        if r["kind"] == K_TWO and len(set(r["writers"])) < 2:
            problems.append("two-producer claim without two writers: %s" % r["id"])
    print("check problems=%d" % len(problems))
    for p in problems[:20]:
        print(" -", p)
    return 0 if not problems else 1


# --------------------------------------------------------------------------- selftest


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as exc:  # noqa: BLE001
            legs.append((name, False, str(exc)))

    def _eq(a, b, msg=""):
        assert a == b, "%s: %r != %r" % (msg, a, b)

    def t_carriers():
        rows = [
            {"face": "results/a.json", "identity_fields": [
                {"dialect": e474.D_STEM, "value": "study_x", "stem_status": e474.S_DECLARED_MANY}]},
            {"face": "results/b.json", "identity_fields": [
                {"dialect": e474.D_STEM, "value": "study_y", "stem_status": e474.S_DECLARED_MANY}]},
            {"face": "results/c.json", "identity_fields": [
                {"dialect": e474.D_STEM, "value": "study_x",
                 "stem_status": e474.S_DECLARED_ONE}]},
        ]
        _eq(carrier_faces(rows, "study_x"), ["results/a.json"])
        _eq(carrier_faces(rows, "study_y"), ["results/b.json"])
        _eq(carrier_faces(rows, "study_z"), [])

    def t_carriers_py_suffix():
        rows = [{"face": "results/a.json", "identity_fields": [
            {"dialect": e474.D_STEM, "value": "study_x.py",
             "stem_status": e474.S_DECLARED_MANY}]}]
        _eq(carrier_faces(rows, "study_x"), ["results/a.json"])

    def t_names_face():
        faces = ["results/state_tilt/FOO-2026-11-07.json"]
        _eq(names_a_face('p = "results/state_tilt/FOO-2026-11-07.json"', faces), faces)
        _eq(names_a_face('name = "FOO-2026-11-07.json"', faces), faces)
        _eq(names_a_face('name = "BAR-2026-11-07.json"', faces), [])

    def t_names_face_short_basename():
        _eq(names_a_face('x = "a.json"', ["results/a.json"]), [])

    def t_imports():
        tree = ast.parse("import json\nfrom e474_x import build\nimport os.path as p\n")
        mods = imported_modules(tree)
        assert {"json", "e474_x", "os"} <= mods, mods

    def t_two():
        _eq(classify(["a", "b"], ["a", "b"], []), K_TWO)

    def t_two_requires_two_writers():
        _eq(classify(["a", "b"], ["a"], []), K_ONE_STRANGERS)

    def t_one_restated():
        _eq(classify(["a", "b"], ["a"], [("b", "a")]), K_ONE)

    def t_one_strangers():
        _eq(classify(["a", "b"], ["a"], []), K_ONE_STRANGERS)

    def t_none():
        _eq(classify(["a", "b"], [], []), K_NONE)

    def t_linked_pair_still_one():
        # two writers that import one another are one producer split across two files
        _eq(classify(["a", "b"], ["a", "b"], [("a", "b")]), K_ONE)

    for name, fn in [
        ("carrier_faces grades only multi-declared stem rows", t_carriers),
        ("carrier_faces accepts a .py-suffixed value", t_carriers_py_suffix),
        ("names_a_face matches a relpath and a long basename", t_names_face),
        ("names_a_face refuses a short basename", t_names_face_short_basename),
        ("imported_modules reads import and from-import", t_imports),
        ("classify: two unlinked writers are two producers", t_two),
        ("classify: one writer plus a stranger is not two", t_two_requires_two_writers),
        ("classify: a helper that imports the writer is one producer", t_one_restated),
        ("classify: an unlinked stranger is published as such", t_one_strangers),
        ("classify: no writer is not 'no producer'", t_none),
        ("classify: two writers linked by an import are one producer", t_linked_pair_still_one),
    ]:
        leg(name, fn)
    bad = [l for l in legs if not l[1]]
    for name, ok, why in legs:
        print(("PASS " if ok else "FAIL ") + name + ((" :: " + why) if why else ""))
    print("selftest %d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("run", "check", "selftest"))
    args = ap.parse_args(argv)
    if args.mode == "run":
        face = build(write=True)
        print("verdict", face["verdict"])
        print("ids", len(face["rows"]), "kinds", face["kind_totals"])
        return 0
    if args.mode == "check":
        return check()
    return selftest()


if __name__ == "__main__":
    sys.exit(main())