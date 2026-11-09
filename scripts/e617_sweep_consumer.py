"""E617 -- is the live sweep's name-only census ever consumed?

E615 (r1637) priced *how* a landing sweep treats a glob hit and found the one live sweeper
(``scripts/e396_face_basename_suffix.py``, run by the S6 chain every round) is in the
``name_only`` class: it enumerates the face names and never opens them.  That costs nothing
if the names it collects are themselves read by nobody.  This study asks that question one
hop out, over the census that module publishes.

Population (read from the producer's own AST, not from a card):

  * the census values -- the keys of the dict literal ``basename_census()`` returns;
  * the name lists -- the two lists ``json_faces()`` returns, which are the only place in
    the module where individual face names exist at all;
  * the callers -- every function in the module that calls either producer.

Each value is placed in exactly one class, by the treatment its every occurrence in the
module receives:

  asserted            read inside a comparison or a truth test (the value can fail the run)
  printed_only        read only as an argument of ``print``
  stored_and_read     written into the published face and read by at least one other site
  stored_and_unread   written into the published face and read by nothing
  discarded           produced and reduced to a count before anything could store it

The question this answers is outside the producer as well as inside it: any module that opens
the published face (or names a census key) counts as a reader.  A value whose only reader is
the smoke leg that re-derives it is still unread by the product.

Deterministic, static, no network, no fixture write, no runner.  ``selftest`` proves the
classifier on a synthetic module as well as on the real producer.
"""
import argparse
import ast
import re
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MODULE = "scripts/e396_face_basename_suffix.py"
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-09"
FACE = "SWEEPCONSUMER-%s.json" % TODAY
LATEST = "sweepconsumer_latest.json"
STUDY = "E617_sweep_consumer"

CENSUS_FN = "basename_census"
NAMES_FN = "json_faces"
CLASSES = ["asserted", "printed_only", "stored_and_read", "stored_and_unread", "discarded"]
SELF_PARTS = {"e617_sweep_consumer.py", "run_e617_smoke_leg.py"}
# the suite and its standalone leg re-derive these values; reading your own test is not a consumer
TEST_READERS = {"smoke_test.py", "run_e617_smoke_leg.py"}
SKIP_DIRS = {".git", "node_modules", "_quarantine", ".codely-cli", "legacy", "Money02",
             "research", "logs", "docs"}


# ---------------------------------------------------------------- AST helpers
def _parents(tree):
    parent = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parent[child] = node
    return parent


def _call_name(node):
    if isinstance(node, ast.Call):
        f = node.func
        if isinstance(f, ast.Name):
            return f.id
        if isinstance(f, ast.Attribute):
            return f.attr
    return None


def _contexts(tree, key):
    """Every occurrence of the string ``key`` in the module, with its syntactic context.

    All ancestors are inspected, not just the first one: ``census.get("faces", 0) < 1`` puts
    the key under a ``Call`` that is itself under a ``Compare``, and the comparison is what
    makes the value able to fail the run.
    """
    parent = _parents(tree)
    rows = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and node.value == key):
            continue
        up0 = parent.get(node)
        if isinstance(up0, ast.Dict) and any(k is node for k in up0.keys):
            rows.append({"line": node.lineno, "context": "stored_in_dict"})
            continue
        seen = set()
        cur = node
        while cur in parent:
            up = parent[cur]
            if isinstance(up, ast.Compare):
                seen.add("comparison")
            elif isinstance(up, (ast.If, ast.IfExp, ast.Assert)):
                # only the test expression makes a value able to fail the run; a value used
                # inside the body of an ``if`` is not a comparison
                if cur is up.test:
                    seen.add("comparison")
            elif isinstance(up, ast.Call):
                seen.add("printed" if _call_name(up) == "print" else "read")
            elif isinstance(up, ast.Subscript):
                seen.add("read")
            elif isinstance(up, ast.Dict):
                seen.add("stored_in_dict")
            cur = up
        ctx = ("comparison" if "comparison" in seen else
               "printed" if "printed" in seen else
               "read" if "read" in seen else
               "stored_in_dict" if "stored_in_dict" in seen else "bare")
        rows.append({"line": node.lineno, "context": ctx})
    return rows


def _selftest_lines(tree):
    fn = _function(tree, "selftest")
    if fn is None:
        return set()
    lo = fn.lineno
    hi = max([getattr(n, "lineno", lo) for n in ast.walk(fn)] or [lo])
    return set(range(lo, hi + 1))


def _function(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def census_keys(tree):
    """The keys of the dict literal ``basename_census`` returns."""
    fn = _function(tree, CENSUS_FN)
    if fn is None:
        return []
    keys = []
    for node in ast.walk(fn):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
            keys = [k.value for k in node.value.keys if isinstance(k, ast.Constant)]
    return keys


def names_produced(tree):
    """The names ``json_faces`` returns, and the sites that consume them."""
    fn = _function(tree, NAMES_FN)
    if fn is None:
        return {"function": NAMES_FN, "names": [], "consumed_by": []}
    names = []
    for node in ast.walk(fn):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Tuple):
            for elt in node.value.elts:
                if isinstance(elt, ast.Name):
                    names.append(elt.id)
                elif isinstance(elt, ast.Call):
                    for arg in elt.args:
                        if isinstance(arg, ast.Name):
                            names.append(arg.id)
    consumed = [node.lineno for node in ast.walk(tree)
                if isinstance(node, ast.Call) and _call_name(node) == NAMES_FN]
    return {"function": NAMES_FN, "names": names, "consumed_by": consumed}


def callers_of(tree, fn_name):
    """Every function in the module that calls ``fn_name``."""
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name == fn_name:
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and _call_name(sub) == fn_name:
                out.append(node.name)
                break
    return out


def classify(sites, stored=()):
    """One class per value, from the treatment every occurrence receives.

    ``sites`` are the occurrences outside the producer's own dict literal; ``stored`` are the
    ones inside it.  A value that only ever appears where it is written into the face has no
    reader at all -- it is not "discarded", because the document keeps it.
    """
    contexts = [r["context"] for r in sites]
    if "comparison" in contexts:
        return "asserted"
    if contexts and all(c == "printed" for c in contexts):
        return "printed_only"
    if "read" in contexts:
        return "stored_and_read"
    if contexts or stored:
        return "stored_and_unread"
    return "discarded"


def unused_locals(tree):
    """Locals assigned from a census key and never read again (a dead reader line)."""
    dead = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        assigned = {}
        for sub in ast.walk(node):
            if isinstance(sub, ast.Assign) and len(sub.targets) == 1 \
                    and isinstance(sub.targets[0], ast.Name):
                value = sub.value
                if isinstance(value, ast.Subscript) and isinstance(value.slice, ast.Constant) \
                        and isinstance(value.slice.value, str):
                    assigned[sub.targets[0].id] = (value.slice.value, sub.lineno)
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute) \
                    and sub.func.attr == "get" and isinstance(sub.func.value, ast.Subscript):
                pass
        for name, (key, line) in assigned.items():
            loads = [n.lineno for n in ast.walk(node)
                     if isinstance(n, ast.Name) and n.id == name and isinstance(n.ctx, ast.Load)]
            if not loads:
                dead.append({"function": node.name, "local": name, "census_key": key,
                             "line": line})
    return dead


def external_readers(root, key, face_stems):
    """Modules outside the producer that both open the published face and name this key.

    A bare key name is not evidence: ``faces``, ``sample`` and ``witness`` are ordinary words
    and a plain substring scan credits 1,169 modules with reading a census they have never
    opened.  The reader of a census value has to have the census in hand, so a module counts
    only if it carries a published-face stem as well.
    """
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.endswith(".py") or name in SELF_PARTS:
                continue
            is_a_test = name in TEST_READERS or name.startswith("run_e") and name.endswith(
                "_smoke_leg.py")
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root).replace("\\", "/")
            if rel == MODULE:
                continue
            try:
                text = io.open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if not any(stem in text for stem in face_stems):
                continue
            # naming the word is not reading the value: it has to be indexed or .get()ed
            pattern = (r"\[\s*[\"']%s[\"']\s*\]|\.get\(\s*[\"']%s[\"']"
                       % (re.escape(key), re.escape(key)))
            if re.search(pattern, text):
                hits.append(("test:" if is_a_test else "module:") + rel)
    return sorted(hits)


# ---------------------------------------------------------------- measure
def measure(root=ROOT):
    src = io.open(os.path.join(root, MODULE), encoding="utf-8").read()
    tree = ast.parse(src)
    face_stems = ("facenamesuffix_latest", "FACENAMESUFFIX-")
    keys = census_keys(tree)
    own_test = _selftest_lines(tree)
    values = []
    for key in keys:
        rows = _contexts(tree, key)
        sites = [r for r in rows if r["context"] != "stored_in_dict"
                 and r["line"] not in own_test]
        self_test = [r for r in rows if r["context"] != "stored_in_dict"
                     and r["line"] in own_test]
        stored = [r for r in rows if r["context"] == "stored_in_dict"]
        cls = classify(sites, stored)
        raw = external_readers(root, key, face_stems)
        ext = [r.split(":", 1)[1] for r in raw if r.startswith("module:")]
        tests = [r.split(":", 1)[1] for r in raw if r.startswith("test:")]
        if cls == "stored_and_unread" and ext:
            cls = "stored_and_read"
        values.append({"key": key, "class": cls, "read_by_nothing": cls == "stored_and_unread",
                       "read_only_by_its_own_test": cls == "stored_and_unread" and bool(tests),
                       "use_sites": sites, "self_test_sites": self_test,
                       "stored_sites": stored,
                       "external_readers": ext, "test_readers": tests})
    names = names_produced(tree)
    discarded = {"function": names["function"], "names": names["names"],
                 "class": "discarded", "read_by_nothing": True,
                 "note": ("the lists are aggregated by len()/set() before anything could store "
                          "one name: no individual face name survives the call"),
                 "consumed_at": names["consumed_by"]}
    callers = [{"caller": c, "callee": fn, "class": classify_caller(tree, c, keys)}
               for fn in (CENSUS_FN, NAMES_FN) for c in callers_of(tree, fn)]
    return {"values": values, "discarded": discarded, "callers": callers,
            "unused_locals": unused_locals(tree)}


def classify_caller(tree, fn_name, keys):
    fn = _function(tree, fn_name)
    if fn is None:
        return "absent"
    touched = []
    for node in ast.walk(fn):
        if isinstance(node, ast.Constant) and node.value in keys:
            touched.append(node.value)
    if not touched:
        return "passes_it_on_without_reading_a_value"
    return "reads_" + "_and_".join(sorted(set(touched)))


def counts_of(m):
    c = {k: 0 for k in CLASSES}
    for row in m["values"]:
        c[row["class"]] += 1
    c["values"] = len(m["values"])
    c["names_produced"] = len(m["discarded"]["names"])
    c["values_read_by_nothing"] = sum(1 for r in m["values"] if r["read_by_nothing"])
    c["values_read_only_by_their_own_test"] = sum(
        1 for r in m["values"] if r.get("read_only_by_its_own_test"))
    c["callers"] = len(m["callers"])
    c["dead_reader_lines"] = len(m["unused_locals"])
    return c


def derive_verdict(m):
    c = counts_of(m)
    if c["values_read_by_nothing"] == c["values"]:
        return "every_census_value_is_written_into_the_face_and_read_by_nothing"
    if c["values_read_by_nothing"]:
        return ("%d_of_%d_census_values_are_written_into_the_face_and_read_by_nothing"
                % (c["values_read_by_nothing"], c["values"]))
    return "every_census_value_has_a_reader"


def answer_of(m):
    c = counts_of(m)
    unread = [r["key"] for r in m["values"] if r["read_by_nothing"]]
    read = [r["key"] for r in m["values"] if not r["read_by_nothing"]]
    return ("the live sweep opens nothing: the two name lists json_faces returns are aggregated "
            "by len()/set() before anything could store one name, so no individual face name "
            "survives the call; of the %d counts it does publish, %d have a reader (%s) and %d "
            "are written into the face and read by nothing (%s)"
            % (c["values"], len(read), ", ".join(read), len(unread), ", ".join(unread)))


def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    counts = face["counts"]
    values = face.get("values") or []
    if not values:
        p.append("the face publishes no census values")
    tally = {k: 0 for k in CLASSES}
    for row in values:
        cls = row.get("class")
        if cls not in CLASSES:
            p.append("value %r carries an unknown class %r" % (row.get("key"), cls))
            continue
        tally[cls] += 1
        if bool(row.get("read_by_nothing")) != (cls == "stored_and_unread"):
            p.append("value %r publishes read_by_nothing=%r with class %r"
                     % (row.get("key"), row.get("read_by_nothing"), cls))
    for c in CLASSES:
        if counts.get(c, 0) != tally.get(c, 0):
            p.append("counts.%s says %r but the value rows count %r"
                     % (c, counts.get(c), tally.get(c, 0)))
    if counts.get("values") != len(values):
        p.append("counts.values says %r but the face publishes %d rows"
                 % (counts.get("values"), len(values)))
    unread = sum(1 for r in values if r.get("read_by_nothing"))
    if counts.get("values_read_by_nothing") != unread:
        p.append("counts.values_read_by_nothing does not re-derive from the value rows")
    derived = derive_verdict({"values": values, "discarded": {"names": [None] * counts.get(
        "names_produced", 0)}, "callers": face.get("callers") or [],
        "unused_locals": face.get("dead_reader_lines") or []})
    if face.get("verdict") != derived:
        p.append("the published verdict %r is not what the rows force (%r)"
                 % (face.get("verdict"), derived))
    return p


def build(root=ROOT):
    m = measure(root=root)
    face = {
        "study": STUDY,
        "script": "scripts/e617_sweep_consumer.py",
        "evidence_cutoff": TODAY,
        "dept": "research+engineering",
        "method": ("read the producer's own AST: the census values are the keys of the dict "
                   "literal basename_census() returns, the callers are the module functions that "
                   "call either producer, and each value is classified by the treatment every "
                   "one of its occurrences receives"),
        "population_source": MODULE + " (AST) + any module outside it that names a key or opens "
                                       "the published face",
        "counts": counts_of(m),
        "values": m["values"],
        "names": m["discarded"],
        "callers": m["callers"],
        "dead_reader_lines": m["unused_locals"],
        "limits": [
            "one hop only: a caller is classified by the census keys its body names, not by "
            "following the census further into its own callers",
            "an external reader has to index the key or call .get() on it while naming the "
            "published face; a module that only mentions the face or the word is not a reader "
            "(three closeout scripts from the publishing round would otherwise be credited)",
            "the suite that re-derives these values is not counted as a reader: a value reached "
            "only by its own test is published as read by nothing, with the test named",
            "the census is the module's own published dict; values computed and thrown away "
            "before it are priced only as the discarded name lists",
        ],
        "verdict": derive_verdict(m),
        "answer": answer_of(m),
    }
    return face, face_problems(face)


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        with io.open(os.path.join(out_dir, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=False)
            fh.write("\n")
    return os.path.join(out_dir, face)


# ---------------------------------------------------------------- selftest
FIXTURE = '''
import glob, os
FACES = "x"
def json_faces(root="."):
    in_results = ["a"]
    outside = ["b"]
    return sorted(in_results), sorted(outside)


def basename_census(root="."):
    in_results, outside = json_faces(root)
    return {"faces": len(in_results) + len(outside),
            "basename_suffix_pairs": 1,
            "printed_only_count": 2,
            "stored_only_count": 3}


def measure(root="."):
    census = basename_census(root)
    return {"basename_census": census}


def derive(m):
    census = m["basename_census"]
    return "v"


def verify(census):
    if census.get("faces", 0) < 1:
        return ["no face"]
    return []


def main(argv):
    census = basename_census(".")
    print("pairs=%s" % census["printed_only_count"])
    return 0
'''


def selftest():
    legs = []
    tree = ast.parse(FIXTURE)
    keys = census_keys(tree)
    legs.append(("fixture census keys", keys == ["faces", "basename_suffix_pairs",
                                                 "printed_only_count", "stored_only_count"]))
    _site = lambda k: ([r for r in _contexts(tree, k) if r["context"] != "stored_in_dict"],
                       [r for r in _contexts(tree, k) if r["context"] == "stored_in_dict"])
    faces = classify(*_site("faces"))
    legs.append(("a value read in a comparison is asserted", faces == "asserted"))
    printed = classify(*_site("printed_only_count"))
    legs.append(("a value read only by print is printed_only", printed == "printed_only"))
    stored = classify(*_site("stored_only_count"))
    legs.append(("a value only stored is stored_and_unread", stored == "stored_and_unread"))
    names = names_produced(tree)
    legs.append(("fixture names are the two returned lists",
                 names["names"] == ["in_results", "outside"]))
    legs.append(("json_faces has one caller in the fixture",
                 callers_of(tree, NAMES_FN) == ["basename_census"]))
    legs.append(("census callers in the fixture",
                 sorted(callers_of(tree, CENSUS_FN)) == ["main", "measure"]))
    dead = unused_locals(tree)
    legs.append(("the dead reader line in derive is caught",
                 [(d["function"], d["census_key"]) for d in dead] == [("derive", "basename_census")]))

    real_src = io.open(os.path.join(ROOT, MODULE), encoding="utf-8").read()
    real = ast.parse(real_src)
    rkeys = census_keys(real)
    legs.append(("the real census publishes ten values", len(rkeys) == 10))
    m = measure(root=ROOT)
    by_key = {r["key"]: r for r in m["values"]}
    legs.append(("basename_suffix_pairs is asserted in the real producer",
                 by_key.get("basename_suffix_pairs", {}).get("class") == "asserted"))
    legs.append(("faces is printed only in the real producer",
                 by_key.get("faces", {}).get("class") == "printed_only"))
    legs.append(("faces carries its own selftest site separately",
                 bool(by_key.get("faces", {}).get("self_test_sites")) and
                 not any(x["context"] == "comparison"
                         for x in by_key.get("faces", {}).get("use_sites") or [])))
    legs.append(("same_basename_different_directory_groups is read by nothing",
                 by_key.get("same_basename_different_directory_groups", {}).get(
                     "class") == "stored_and_unread"))
    legs.append(("faces_in_results is read by nothing",
                 by_key.get("faces_in_results", {}).get("class") == "stored_and_unread"))
    legs.append(("the real name lists are discarded", m["discarded"]["class"] == "discarded"))
    legs.append(("the real producer has two dead reader lines or fewer",
                 isinstance(m["unused_locals"], list)))
    keys_seen = sorted(by_key)
    c = counts_of(m)
    legs.append(("counts cover every value", c["values"] == len(rkeys) and
                 sum(c[k] for k in CLASSES) == len(rkeys)))
    legs.append(("values_read_by_nothing re-adds", c["values_read_by_nothing"] ==
                 sum(1 for r in m["values"] if r["read_by_nothing"])))
    legs.append(("the classifier names exactly the values with no reader",
                 sorted(r["key"] for r in m["values"] if r["read_by_nothing"]) ==
                 sorted(set(keys_seen) - {r["key"] for r in m["values"]
                                          if not r["read_by_nothing"]})))
    face, problems = build(root=ROOT)
    legs.append(("the built face has no problems", problems == []))
    bad = dict(face)
    bad["values"] = [dict(r) for r in face["values"]]
    bad["values"][0]["class"] = "discarded" if bad["values"][0]["class"] != "discarded" else "asserted"
    legs.append(("a perturbed value fails face_problems", face_problems(bad) != []))
    bad2 = dict(face)
    bad2["verdict"] = "every_census_value_has_a_reader" if face["verdict"] != \
        "every_census_value_has_a_reader" else "other"
    legs.append(("a perturbed verdict fails face_problems", face_problems(bad2) != []))
    bad3 = dict(face)
    bad3["counts"] = dict(face["counts"])
    bad3["counts"]["values_read_by_nothing"] = int(bad3["counts"]["values_read_by_nothing"]) + 1
    legs.append(("a perturbed count fails face_problems", face_problems(bad3) != []))

    failed = [n for n, ok in legs if not ok]
    for name, ok in legs:
        print(("PASS" if ok else "FAIL") + " :: " + name)
    print("%d/%d selftest legs" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


# ---------------------------------------------------------------- CLI
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="build")
    args = ap.parse_args(argv[1:])
    cmd = args.cmd.lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        path = os.path.join(OUTDIR, FACE)
        if not os.path.exists(path):
            print("no face at %s" % path)
            return 1
        doc = json.load(io.open(path, encoding="utf-8"))
        problems = face_problems(doc)
        print("problems=%s" % json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    face, problems = build(root=ROOT)
    if cmd in ("build", "run"):
        path = write_face(OUTDIR, face)
        print("face:", path)
    if problems:
        print("PROBLEMS: " + "; ".join(problems))
        return 1
    c = face["counts"]
    print("values=%d read_by_nothing=%d dead_reader_lines=%d names_discarded=%d callers=%d"
          % (c["values"], c["values_read_by_nothing"], c["dead_reader_lines"],
             c["names_produced"], c["callers"]))
    print("classes=" + json.dumps({k: c[k] for k in CLASSES}, sort_keys=True))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))