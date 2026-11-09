"""E623 -- for a live dead reader line, is its key read anywhere else in the same function?

E622 (r1640) closed over reachability: 34 of E619's dead face-key lines sit in a function that is
reachable from module level, so they are defects rather than inert residue.  This study asks what
kind of defect each one is.

Three classes, fixed before the scan:

  superseded_duplicate_read          another read of the same key exists in the same function on a
                                     LATER line and that read is not itself a dead reader line --
                                     the value was taken, dropped, and read again further down
  key_read_only_before_the_dead_line  the key is read again, but only on earlier lines: the shape
                                     of a loop-carried read, where E619's textual "no load after
                                     the assignment line" rule reads a live update as dead
  only_other_reads_are_dead_too      the key is read more than once, but every read is a dead
                                     reader line: the function takes the value and uses no binding
  only_read_of_that_key_in_the_function  the dead line is the sole read of that key in the
                                     function body

A read is a string subscript ``m["k"]`` or a ``.get("k")`` call, the same expression shapes E619
classifies locals from; a store subscript (``face["k"] = ...``) writes the key and is not a read.
"In its own function" means the innermost definition spanning the dead line (the rule E622 uses to
resolve a name that can be defined twice), and reads inside a nested definition are a different
scope and are not counted for the outer function.

Population: E622's live holders, imported rather than re-implemented (``e622_deadlocal_reach``
for the call graph and the reach class, ``e619_dead_reader_locals`` for the dead-line classifier),
with both self-exclusion sets kept so the population is the same one E622 published.

Deterministic, static, no network, no runner, no fixture write.
"""
import argparse
import ast
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-09"
FACE = "DEADLINEKEYUSE-%s.json" % TODAY
LATEST = "deadlinekeyuse_latest.json"
STUDY = "E623_live_dead_line_key_use"
SELF_PARTS = {"e623_deadline_key_use.py", "run_e623_smoke_leg.py", "_probe_e623.py"}
CLASSES = ["superseded_duplicate_read", "key_read_only_before_the_dead_line",
           "only_other_reads_are_dead_too", "only_read_of_that_key_in_the_function"]

if HERE not in sys.path:
    sys.path.insert(0, HERE)
import e619_dead_reader_locals as e619                                              # noqa: E402
import e622_deadlocal_reach as e622                                                 # noqa: E402

FUNC = (ast.FunctionDef, ast.AsyncFunctionDef)


# ---------------------------------------------------------------- AST helpers
def own_scope(fn):
    """Every node in the body of ``fn``, not descending into nested definitions."""
    stack = list(ast.iter_child_nodes(fn))
    out = []
    while stack:
        node = stack.pop()
        if isinstance(node, FUNC):
            continue
        out.append(node)
        stack.extend(ast.iter_child_nodes(node))
    return out


def key_reads(nodes, key):
    """Nodes that read ``key`` as a string subscript or a .get("key") call.

    A subscript in a store context (``face["k"] = ...``) writes the key, it does not read it, so
    it is not a read here even though E619's ``sub_key`` returns the name for both contexts.
    """
    out = []
    for n in nodes:
        if e619.sub_key(n) != key:
            continue
        if isinstance(n, ast.Subscript) and not isinstance(n.ctx, ast.Load):
            continue
        out.append(n)
    return out


def innermost(fns, row):
    """The innermost definition with the row's name spanning its line (E622's resolution)."""
    cand = [f for f in fns if f.name == row["function"]
            and f.lineno <= row["line"] <= (f.end_lineno or f.lineno)]
    cand.sort(key=lambda f: f.lineno)
    return cand[-1] if cand else None


def classify_tree(tree, stem=""):
    """Rows for one module: each live dead face-key line and the class of its key use."""
    graph = e622.call_graph(tree, stem)
    rows = e622.function_rows(tree, graph, stem)
    by_name_line = {(r["function"], r["line"]): r for r in rows}
    dead = e619.dead_reader_locals(tree)
    resolved = {}
    for d in dead:
        fn = innermost(graph["fns"], d)
        if fn is None:
            continue
        resolved.setdefault(id(fn), []).append(d)
    out = []
    inert_lines = 0
    for fid, dead_rows in resolved.items():
        fn = next((f for f in graph["fns"] if id(f) == fid), None)
        if fn is None:
            continue
        holder = by_name_line.get((fn.name, fn.lineno))
        if holder is None:
            continue
        facekey = [d for d in dead_rows if d.get("key_is_a_dict_literal_key")]
        if holder["reach"] not in e622.LIVE:
            inert_lines += len(facekey)
            continue
        scope = own_scope(fn)
        dead_ids = {id(d_node) for d in facekey
                    for d_node in key_reads(scope, d["key"]) if d_node.lineno == d["line"]}
        for d in facekey:
            reads = key_reads(scope, d["key"])
            own_id = {id(n) for n in reads if n.lineno == d["line"]}
            other_live = [n for n in reads if id(n) not in dead_ids]
            if any(n.lineno > d["line"] for n in other_live):
                cls = "superseded_duplicate_read"
            elif other_live:
                cls = "key_read_only_before_the_dead_line"
            elif len([n for n in reads if id(n) in dead_ids]) > 1:
                cls = "only_other_reads_are_dead_too"
            else:
                cls = "only_read_of_that_key_in_the_function"
            module_nodes = [n for other in graph["fns"] if id(other) != fid
                            for n in own_scope(other)]
            out.append({
                "module": stem and ("scripts/" + stem + ".py") or "",
                "function": fn.name,
                "def_line": fn.lineno,
                "line": d["line"],
                "local": d["local"],
                "key": d["key"],
                "reach": holder["reach"],
                "class": cls,
                "reads_of_the_key_in_the_function": len(reads),
                "dead_reads_of_the_key_in_the_function": len(
                    [n for n in reads if id(n) in dead_ids]),
                "other_read_lines": sorted({n.lineno for n in other_live}),
                "key_read_elsewhere_in_the_module": len(key_reads(module_nodes, d["key"])),
                "_own_id": sorted(own_id),
            })
    return out, inert_lines


def measure(root=ROOT):
    mods, skipped = e619.population(root)
    skip = set(e622.SELF_PARTS) | set(SELF_PARTS)
    keep = [(rel, tree) for rel, tree in mods
            if not any(rel.endswith(os.path.basename(p)) or rel.endswith("/" + os.path.basename(p))
                       for p in skip)]
    lines = []
    inert = 0
    for rel, tree in keep:
        stem = os.path.basename(rel)[:-3]
        rows, inert_here = classify_tree(tree, stem)
        for r in rows:
            r["module"] = rel
        lines.extend(rows)
        inert += inert_here
    lines.sort(key=lambda r: (r["module"], r["line"]))
    for r in lines:
        r.pop("_own_id", None)
    return {"population_modules": len(keep), "skipped": skipped, "lines": lines,
            "inert_dead_facekey_lines": inert,
            "cross_check": e622_cross_check(root, lines)}


# ---------------------------------------------------------------- cross-check
def e622_cross_check(root, lines):
    """Diff the live-holder population here against the face E622 published."""
    out = {"published": False, "agrees": None}
    path = os.path.join(root, "results", "state_tilt", "deadlocalreach_latest.json")
    if not os.path.exists(path):
        out["note"] = "no published E622 face on disk"
        return out
    pub = json.load(io.open(path, encoding="utf-8"))
    published = {}
    for mod in pub.get("modules") or []:
        for h in mod.get("holders") or []:
            if h.get("dead_lines_facekey") and h.get("reach") in e622.LIVE:
                published[(mod.get("module"), h.get("function"), h.get("def_line"))] = \
                    h.get("dead_lines_facekey")
    mine = {}
    for r in lines:
        key = (r["module"], r["function"], r["def_line"])
        mine[key] = mine.get(key, 0) + 1
    differing = sorted(k for k in set(mine) & set(published) if mine[k] != published[k])
    out.update({
        "published": True,
        "published_live_holders": len(published),
        "published_live_dead_facekey_lines": sum(published.values()),
        "rederived_live_holders": len(mine),
        "rederived_live_dead_facekey_lines": sum(mine.values()),
        "holders_with_differing_line_counts": [list(k) for k in differing[:10]],
        "holders_with_differing_line_counts_n": len(differing),
        "holders_only_here": [list(k) for k in sorted(set(mine) - set(published))][:10],
        "holders_only_in_the_published_face":
            [list(k) for k in sorted(set(published) - set(mine))][:10],
        "agrees": not differing and not (set(published) - set(mine)),
    })
    return out


# ---------------------------------------------------------------- counts / verdict
def counts_of(m):
    lines = m["lines"]
    by = {c: sum(1 for r in lines if r["class"] == c) for c in CLASSES}
    c = {
        "population_modules": m["population_modules"],
        "skipped_modules": len(m["skipped"]),
        "live_holder_functions": len({(r["module"], r["def_line"]) for r in lines}),
        "modules_with_a_live_dead_facekey_line": len({r["module"] for r in lines}),
        "live_dead_facekey_lines": len(lines),
        "inert_dead_facekey_lines": m["inert_dead_facekey_lines"],
        "lines_whose_key_is_read_elsewhere_in_the_module": sum(
            1 for r in lines if r["key_read_elsewhere_in_the_module"]),
        "lines_with_a_duplicate_read_in_the_same_function": sum(
            1 for r in lines if r["reads_of_the_key_in_the_function"] > 1),
    }
    for cls in CLASSES:
        c["class_" + cls] = by[cls]
    return c


def derive_verdict(m):
    c = counts_of(m)
    if c["population_modules"] == 0:
        return "no_face_publishers_in_the_population"
    total = c["live_dead_facekey_lines"]
    if total == 0:
        return "no_live_dead_facekey_line_in_the_population"
    n = c["class_superseded_duplicate_read"]
    if n == total:
        return ("every_one_of_the_%d_live_dead_facekey_lines_has_a_live_sibling_read_of_its_key"
                "_in_the_same_function" % total)
    if n == 0:
        return ("none_of_the_%d_live_dead_facekey_lines_has_a_live_sibling_read_of_its_key_in_"
                "the_same_function" % total)
    return ("%d_of_%d_live_dead_facekey_lines_have_a_live_sibling_read_of_their_key_in_the_same_"
            "function" % (n, total))


def answer_of(m):
    c = counts_of(m)
    return ("of E622's %d dead face-key lines in live holders, %d are read again on a later line of "
            "the same function (a superseded duplicate read), %d are read again but only on "
            "earlier lines (the loop-carried shape E619's 'no load after the assignment' rule "
            "cannot see), %d read the key more than once with every read itself dead, and %d are "
            "the only read of that key in the function; the %d lines sit in %d live holder "
            "functions across %d modules, %d of their keys are also read in another function of "
            "the same module, and %d dead face-key lines sit in an inert holder and are outside "
            "this question"
            % (c["live_dead_facekey_lines"], c["class_superseded_duplicate_read"],
               c["class_key_read_only_before_the_dead_line"],
               c["class_only_other_reads_are_dead_too"],
               c["class_only_read_of_that_key_in_the_function"],
               c["live_dead_facekey_lines"], c["live_holder_functions"],
               c["modules_with_a_live_dead_facekey_line"],
               c["lines_whose_key_is_read_elsewhere_in_the_module"],
               c["inert_dead_facekey_lines"]))


def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    counts = face["counts"]
    lines = face.get("lines") or []
    if counts.get("live_dead_facekey_lines") != len(lines):
        p.append("counts.live_dead_facekey_lines says %r but the face publishes %d lines"
                 % (counts.get("live_dead_facekey_lines"), len(lines)))
    for cls in CLASSES:
        want = sum(1 for r in lines if r.get("class") == cls)
        if counts.get("class_" + cls) != want:
            p.append("counts.class_%s does not re-derive from the lines" % cls)
    if sum(counts.get("class_" + cls, 0) for cls in CLASSES) != len(lines):
        p.append("the three classes do not add up to the published line count")
    if counts.get("live_holder_functions") != len({(r.get("module"), r.get("def_line"))
                                                   for r in lines}):
        p.append("counts.live_holder_functions does not re-derive from the lines")
    if counts.get("modules_with_a_live_dead_facekey_line") != len({r.get("module")
                                                                  for r in lines}):
        p.append("counts.modules_with_a_live_dead_facekey_line does not re-derive")
    if counts.get("lines_whose_key_is_read_elsewhere_in_the_module") != sum(
            1 for r in lines if r.get("key_read_elsewhere_in_the_module")):
        p.append("counts.lines_whose_key_is_read_elsewhere_in_the_module does not re-derive")
    for r in lines:
        if r.get("class") not in CLASSES:
            p.append("line %r in %r carries class=%r, not a published class"
                     % (r.get("line"), r.get("function"), r.get("class")))
        if r.get("reach") not in e622.LIVE:
            p.append("line %r in %r is published as a live line but carries reach=%r"
                     % (r.get("line"), r.get("function"), r.get("reach")))
        if not isinstance(r.get("line"), int) or not isinstance(r.get("def_line"), int):
            p.append("line %r in %r has no integer line identity"
                     % (r.get("line"), r.get("function")))
        if r.get("class") == "superseded_duplicate_read" and not any(
                ln > r.get("line", 0) for ln in (r.get("other_read_lines") or [])):
            p.append("line %r in %r is classed as a superseded duplicate with no read after it"
                     % (r.get("line"), r.get("function")))
        if r.get("class") == "key_read_only_before_the_dead_line" and not (
                r.get("other_read_lines")
                and all(ln < r.get("line", 0) for ln in r["other_read_lines"])):
            p.append("line %r in %r is classed as read only before it without an earlier read line"
                     % (r.get("line"), r.get("function")))
        if r.get("class") in ("only_read_of_that_key_in_the_function",
                              "only_other_reads_are_dead_too") and \
                r.get("other_read_lines"):
            p.append("line %r in %r is classed as %r yet publishes other live reads"
                     % (r.get("line"), r.get("function"), r.get("class")))
    cc = face.get("e622_cross_check") or {}
    if cc.get("published"):
        if cc.get("agrees") is False:
            p.append("the imported E622 population no longer reproduces the published face "
                     "(%r holders differ, %r only in the published face)"
                     % (cc.get("holders_with_differing_line_counts_n"),
                        len(cc.get("holders_only_in_the_published_face") or [])))
        if cc.get("rederived_live_dead_facekey_lines") != counts.get("live_dead_facekey_lines"):
            p.append("the E622 cross-check re-derived %r lines but the counts say %r"
                     % (cc.get("rederived_live_dead_facekey_lines"),
                        counts.get("live_dead_facekey_lines")))
    derived = derive_verdict({"population_modules": counts.get("population_modules"),
                              "lines": lines,
                              "inert_dead_facekey_lines":
                                  counts.get("inert_dead_facekey_lines"),
                              "skipped": [None] * (counts.get("skipped_modules") or 0)})
    if face.get("verdict") != derived:
        p.append("the published verdict %r is not what the line rows force (%r)"
                 % (face.get("verdict"), derived))
    return p


def build(root=ROOT):
    m = measure(root=root)
    face = {
        "study": STUDY,
        "script": "scripts/e623_deadline_key_use.py",
        "evidence_cutoff": TODAY,
        "dept": "research+engineering",
        "method": ("take E622's live holders (imported: call graph, reach class and the E619 "
                   "dead-line classifier are not re-implemented), resolve each dead face-key line "
                   "to its innermost enclosing definition, and ask whether any other expression "
                   "in that same function body reads the same string key as a subscript or a "
                   ".get() call; reads inside a nested definition are a different scope and are "
                   "not counted"),
        "population_source": ("scripts/*.py (AST) via e619.population, face publishers only, "
                              "less E622's and this study's self-exclusion sets"),
        "counts": counts_of(m),
        "e622_cross_check": m["cross_check"],
        "lines": m["lines"],
        "skipped": m["skipped"],
        "limits": [
            "the key has to be a literal string; a key held in a variable is the same blind spot "
            "E619 has, so a line whose key is computed is published as its literal only",
            "a read counts when it indexes the same literal key, whatever the object: m[\"k\"] on "
            "a different dict in the same function would satisfy the duplicate test -- the "
            "population is small enough (34 lines) that each row carries the key and its other "
            "read lines for a reader to check",
            "reads inside a nested function definition are not counted for the outer function, "
            "while E619's dead-local test does count a load in a nested scope; the two rules "
            "differ on purpose and the conflict is one-directional (E619's is more permissive "
            "about what makes a local live)",
            "reachability is E622's measurement inside one module; a holder called only by an "
            "importer is outside both studies",
            "this script excludes itself and its smoke leg, and keeps E622's self-exclusion set, "
            "so the population is the one E622 published",
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
import io, json, os


def build(m):
    face = {"counts": {"n": 1}, "rows": [], "x": None, "d": None}
    sup = m["counts"]
    only = m["rows"]
    twin1 = m["x"]
    twin2 = m["x"]
    if m.get("counts"):
        pass
    face["x"] = m["counts"]

    def inner(k):
        return k["rows"]

    with io.open("x", "w") as fh:
        json.dump(face, fh)
    return face


def scan(rows):
    prev = None
    for r in rows:
        if r["d"] <= (prev or ""):
            raise ValueError("not increasing")
        prev = r["d"]


build({"counts": {"n": 1}, "rows": [], "x": None, "d": None})
scan([{"d": 1}])
'''


def selftest():
    legs = []
    tree = ast.parse(FIXTURE)
    rows, inert = classify_tree(tree, "fixture")
    by_local = {(r["function"], r["local"]): r for r in rows}
    legs.append(("the fixture yields live dead face-key lines", len(rows) > 0 and inert == 0))
    legs.append(("a dead line with a live read of the same key is a superseded duplicate",
                 by_local.get(("build", "sup"), {}).get("class") == "superseded_duplicate_read"))
    legs.append(("the sole read of a key is the only read",
                 by_local.get(("build", "only"), {}).get("class") ==
                 "only_read_of_that_key_in_the_function"))
    legs.append(("two dead reads and no live read are classed as dead-only",
                 by_local.get(("build", "twin1"), {}).get("class") ==
                 "only_other_reads_are_dead_too"))
    legs.append(("both twins are classed alike",
                 by_local.get(("build", "twin2"), {}).get("class") ==
                 by_local.get(("build", "twin1"), {}).get("class")))
    legs.append(("a read inside a nested definition is not the outer function's read",
                 by_local.get(("build", "only"), {}).get("other_read_lines") == []))
    legs.append(("the superseded row names a read after the dead line",
                 any(ln > by_local[("build", "sup")]["line"]
                     for ln in by_local[("build", "sup")]["other_read_lines"])))
    legs.append(("a key read only on earlier lines is the loop-carried class",
                 by_local.get(("scan", "prev"), {}).get("class") ==
                 "key_read_only_before_the_dead_line"))
    legs.append(("the loop-carried row carries only earlier read lines",
                 all(ln < by_local[("scan", "prev")]["line"]
                     for ln in by_local[("scan", "prev")]["other_read_lines"])))
    legs.append(("the twin rows carry no live read line",
                 by_local.get(("build", "twin1"), {}).get("other_read_lines") == []))
    legs.append(("get() on the same key counts as a read",
                 by_local.get(("build", "sup"), {}).get("reads_of_the_key_in_the_function") == 3))
    for r in rows:
        r["module"] = "scripts/fixture.py"
        r["reach"] = "called_from_module_level"
        r.pop("_own_id", None)
    m = {"population_modules": 1, "skipped": [], "lines": rows,
         "inert_dead_facekey_lines": inert}
    c = counts_of(m)
    legs.append(("counts re-add the line rows",
                 c["live_dead_facekey_lines"] == len(rows)
                 and sum(c["class_" + k] for k in CLASSES) == len(rows)))
    legs.append(("the verdict is derived from the class counts",
                 derive_verdict(m).startswith("%d_of_%d_live_dead_facekey_lines"
                                              % (c["class_superseded_duplicate_read"],
                                                 len(rows)))))
    legs.append(("the fixture's five live lines sit in two holders",
                 c["live_holder_functions"] == len({(r["module"], r["def_line"]) for r in rows})
                 == 2))

    mods, skipped = e619.population(ROOT)
    skip = set(e622.SELF_PARTS) | set(SELF_PARTS)
    kept = [rel for rel, _ in mods if os.path.basename(rel) not in skip]
    legs.append(("the real population parses and is non-empty", len(mods) > 100))
    legs.append(("this script excludes itself",
                 "scripts/e623_deadline_key_use.py" not in kept))
    real = measure(root=ROOT)
    cc = real["cross_check"]
    legs.append(("the E622 cross-check read a published face", cc.get("published") is True))
    legs.append(("the live population is the one E622 published", cc.get("agrees") is True))
    face, problems = build(root=ROOT)
    legs.append(("the built face has no problems", problems == []))
    bad = {"counts": dict(face["counts"]), "lines": [dict(r) for r in face["lines"]],
           "verdict": face["verdict"], "e622_cross_check": face["e622_cross_check"]}
    bad["counts"]["class_superseded_duplicate_read"] = int(
        bad["counts"]["class_superseded_duplicate_read"]) + 1
    legs.append(("a perturbed class count fails face_problems", face_problems(bad) != []))
    bad2 = {"counts": dict(face["counts"]), "lines": [dict(r) for r in face["lines"]],
            "verdict": "other", "e622_cross_check": face["e622_cross_check"]}
    legs.append(("a perturbed verdict fails face_problems", face_problems(bad2) != []))
    bad3 = {"counts": dict(face["counts"]), "lines": [dict(r) for r in face["lines"]][:-1],
            "verdict": face["verdict"], "e622_cross_check": face["e622_cross_check"]}
    legs.append(("a dropped line row fails face_problems", face_problems(bad3) != []))

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
    if cmd == "check":
        face, problems = build(root=ROOT)
        print("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "verify":
        path = os.path.join(OUTDIR, FACE)
        if not os.path.exists(path):
            print("no face at %s" % path)
            return 1
        doc = json.load(io.open(path, encoding="utf-8"))
        problems = face_problems(doc)
        print("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    face, problems = build(root=ROOT)
    if cmd in ("build", "run"):
        path = write_face(OUTDIR, face)
        print("face:", path)
    if problems:
        print("PROBLEMS: " + "; ".join(problems))
        return 1
    c = face["counts"]
    print("population=%d live_holders=%d live_lines=%d superseded=%d dead_only=%d only_read=%d "
          "inert_lines=%d skipped=%d"
          % (c["population_modules"], c["live_holder_functions"],
             c["live_dead_facekey_lines"], c["class_superseded_duplicate_read"],
             c["class_only_other_reads_are_dead_too"],
             c["class_only_read_of_that_key_in_the_function"],
             c["inert_dead_facekey_lines"], c["skipped_modules"]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))