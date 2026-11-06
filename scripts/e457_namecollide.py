"""E457 -- how often is a module-level function's name also a method name in a module that never
imports it?

E450's name arm read 26 hits and the largest single block of them (13, all Tools/pool_worker.py)
carried zero rows where the receiver was that module's own class.  A name test is therefore
optimistic by however often a function name is reused as a method name elsewhere, and nobody had
measured that rate.

For every module-level function this repository defines (the population is the tree itself, not a
curated family) this study asks, per name:

  C  how many OTHER modules define a class carrying a method of that name;
  I  of those modules, how many import that function from the module that defines it;
  N  the residue -- modules that carry the collision and have no import edge to the definition.

Only N is the mechanism: a module that never imports the function cannot be reading it, so its
method of the same name is a different thing that a name-based census would have counted.

Two readings are kept apart: the collision count C is a surface (what a name test can see) and N is
the priced part (what it cannot justify).  A module that imports the function is published in I even
when its own class also carries the name -- ambiguity, not proof.

Usage:
    python scripts/e457_namecollide.py run|verify|check|selftest
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import e437_name_recall as e437
import e456_import_class as e456
import growth_tolerance as gt

ROOT = e456.ROOT
ST = e456.ST
OUTDIR = ST
FACE_NAME = "namecollide_latest.json"
DATED_PREFIX = "NAMECOLLIDE"
CARD_ID = "E457-HOW-OFTEN-A-WRAPPER-NAME-IS-ALSO-A-METHOD-NAME-IN-A-MODULE-THAT-NEVER-IMPORTS-IT"
STUDY = "E457_how_often_a_module_level_function_name_is_a_method_name_in_a_module_that_never_imports_it"
OWN_PREFIXES = ("e457", "_e457", "run_e457")

V_EMPTY = "no_module_level_function_name_collides_with_a_method_name_anywhere"
V_ALL_JUSTIFIED = "every_colliding_module_imports_the_function_so_the_name_test_has_no_unpriced_half"
V_SOME_UNJUSTIFIED = ("some_colliding_modules_never_import_the_function_there_so_a_name_test_counts_"
                      "a_different_thing_that_only_shares_the_name")
V_VERDICT_VOCAB = (V_EMPTY, V_ALL_JUSTIFIED, V_SOME_UNJUSTIFIED)

NEST_TOP = "class_at_module_level"
NEST_IN_FUNC = "class_inside_a_function"
NEST_IN_CLASS = "class_inside_a_class"

METHOD_LIMITS = (
    "the collision is a name collision, not evidence that a call site meant the method: nothing here "
    "reads call sites, so C is an upper bound of what a name test can see and N is an upper bound of "
    "its unpriced half",
    "a class attribute that is not a def is not a method (an assignment named like the function does "
    "not collide)",
    "a class defined inside a function is counted as a class of its module with its own nesting kind, "
    "so the reading can be split rather than silently widened",
    "an aliased from-import (`from a import f as g`) still imports f and is counted as an import edge",
    "a module that imports the whole definition module (`import a`) but never the name is *not* an "
    "import edge: importing a module does not make its module-level function a local name",
    "files that fail to parse are published as a residue, never folded into a zero",
)


def _text(rel: str) -> str:
    """Source text. utf-8-sig strips a BOM: ast.parse rejects U+FEFF, and a BOM is an encoding
    artifact, not a syntax error -- reading it as one would drop 100+ real modules out of the
    population (measured: 117 "failures" collapse to the genuine ones on this fix)."""
    try:
        return io.open(os.path.join(ROOT, rel), "r", encoding="utf-8-sig", errors="replace").read()
    except OSError:
        return ""


def _index_sources(sources: dict) -> dict:
    """Index a {rel: source} mapping: module-level functions, class methods, import edges.

    Pure function over text so the selftest can run the same instrument on fixtures.
    """
    funcs: dict[str, list[dict]] = {}
    methods: dict[str, list[dict]] = {}
    imports: dict[str, dict] = {}
    modules: list[str] = []
    failed: list[dict] = []
    classes_total = 0
    for rel in sorted(sources):
        try:
            tree = ast.parse(sources[rel])
        except SyntaxError as exc:
            failed.append({"file": rel, "error": "%s: %s" % (type(exc).__name__, exc.msg),
                           "line": exc.lineno})
            continue
        modules.append(rel)
        imports[rel] = _imports_of_text(sources[rel])
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                funcs.setdefault(node.name, []).append({"file": rel, "line": node.lineno})
        classes_total += sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
        # ast.walk gives no parent links, so nesting is classified by a parent-aware pass.
        _classify_nesting(tree, methods, rel)
    return {"funcs": funcs, "methods": methods, "imports": imports, "modules": modules,
            "failed": failed, "classes": classes_total}


def _classify_nesting(tree: ast.AST, methods: dict, rel: str) -> None:
    """Parent-aware walk: which class methods exist and how each class is nested."""

    def walk(node, nest: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                inner = NEST_TOP if nest == NEST_TOP else NEST_IN_CLASS
                for body in child.body:
                    if isinstance(body, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods.setdefault(body.name, []).append(
                            {"file": rel, "line": body.lineno, "class": child.name,
                             "nest": inner})
                walk(child, inner)
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for body in child.body:
                    if isinstance(body, ast.ClassDef):
                        for meth in body.body:
                            if isinstance(meth, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                methods.setdefault(meth.name, []).append(
                                    {"file": rel, "line": meth.lineno, "class": body.name,
                                     "nest": NEST_IN_FUNC})
                        walk(body, NEST_IN_FUNC)
                walk(child, nest)
            else:
                walk(child, nest)

    walk(tree, NEST_TOP)


def _imports_of_text(text: str) -> dict:
    """local name -> [{module, imported_name, form}], read from source text (not the disk)."""
    out: dict[str, list[dict]] = {}
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return out
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.setdefault(alias.asname or alias.name.split(".")[0], []).append(
                    {"module": alias.name, "imported_name": None,
                     "form": "module_aliased" if alias.asname else "module"})
        elif isinstance(node, ast.ImportFrom):
            module = ("." * node.level) + (node.module or "")
            for alias in node.names:
                if alias.name == "*":
                    continue
                out.setdefault(alias.asname or alias.name, []).append(
                    {"module": module, "imported_name": alias.name,
                     "form": "function_aliased" if alias.asname else "function"})
    return out


def _imports_the_function(rel: str, name: str, def_files: set, files: set,
                          imports: dict | None = None) -> dict:
    """Does `rel` import `name` from a module that resolves to one of the definition's files?"""
    imps = _imports_of_text(_text(rel)) if imports is None else imports
    for local, recs in imps.items():
        for rec in recs:
            if rec.get("imported_name") != name:
                continue
            targets = e456.module_to_rel(rec.get("module") or "", rel, files)
            if any(t in def_files for t in targets):
                return {"imports": True, "form": rec.get("form"), "local_name": local,
                        "module": rec.get("module")}
    return {"imports": False, "form": None, "local_name": None, "module": None}


def build(sources: dict | None = None) -> dict:
    if sources is None:
        files = [p for p in e437.corpus()
                 if not os.path.basename(p).startswith(OWN_PREFIXES)]
        fileset = set(files)
        sources = {rel: _text(rel) for rel in files}
        bom = 0
        for rel in files:
            try:
                with open(os.path.join(ROOT, rel), "rb") as fh:
                    if fh.read(3) == b"\xef\xbb\xbf":
                        bom += 1
            except OSError:
                pass
    else:
        fileset = set(sources)
        bom = None
    print("stage: %d source files to index" % len(sources), flush=True)

    idx = _index_sources(sources)
    funcs, methods = idx["funcs"], idx["methods"]
    print("stage: %d module-level functions / %d distinct names / %d class methods / %d parse failures"
          % (sum(len(v) for v in funcs.values()), len(funcs),
             sum(len(v) for v in methods.values()), len(idx["failed"])), flush=True)

    rows: list[dict] = []
    names_with_collision = 0
    for name in sorted(funcs):
        def_files = {d["file"] for d in funcs[name]}
        carriers = [m for m in methods.get(name, []) if m["file"] not in def_files]
        if not carriers:
            continue
        names_with_collision += 1
        per_module: dict[str, dict] = {}
        for m in carriers:
            slot = per_module.setdefault(m["file"], {"file": m["file"], "nests": set(),
                                                     "classes": set()})
            slot["nests"].add(m["nest"])
            slot["classes"].add(m["class"])
        with_import, without_import = [], []
        for mod in sorted(per_module):
            edge = _imports_the_function(mod, name, def_files, fileset,
                                         idx["imports"].get(mod))
            rec = {"file": mod, "nests": sorted(per_module[mod]["nests"]),
                   "classes": sorted(per_module[mod]["classes"]),
                   "imports_the_function": edge["imports"],
                   "import_form": edge["form"], "local_name": edge["local_name"]}
            (with_import if edge["imports"] else without_import).append(rec)
        rows.append({
            "name": name,
            "defined_in": sorted(def_files),
            "colliding_modules": len(per_module),
            "colliding_modules_with_import": len(with_import),
            "colliding_modules_without_import": len(without_import),
            "class_carriers": sum(len(v["classes"]) for v in per_module.values()),
            "nests": sorted({n for v in per_module.values() for n in v["nests"]}),
            "without_import_examples": without_import[:3],
            "with_import_examples": with_import[:3],
        })

    pairs = sum(r["colliding_modules"] for r in rows)
    pairs_without = sum(r["colliding_modules_without_import"] for r in rows)
    total_names = len(funcs)
    summary = {
        "source_files": len(sources),
        "modules_indexed": len(idx["modules"]),
        "parse_failures": len(idx["failed"]),
        "classes_indexed": idx["classes"],
        "class_methods_indexed": sum(len(v) for v in methods.values()),
        "module_level_functions": sum(len(v) for v in funcs.values()),
        "distinct_function_names": total_names,
        "names_with_a_method_collision": names_with_collision,
        "share_of_names_colliding": round(names_with_collision / total_names, 6) if total_names else None,
        "collision_pairs": pairs,
        "collision_pairs_without_an_import_edge": pairs_without,
        "share_of_pairs_without_an_import_edge": round(pairs_without / pairs, 6) if pairs else None,
        "names_whose_every_colliding_module_imports_the_function":
            sum(1 for r in rows if r["colliding_modules_without_import"] == 0),
        "names_with_at_least_one_module_that_never_imports_it":
            sum(1 for r in rows if r["colliding_modules_without_import"] > 0),
    }
    verdict = verdict_for(summary)
    face = {
        "study": STUDY,
        "card": CARD_ID,
        "title": "the vocabulary a name test reads is shared with method names in modules that never "
                 "import the function, and that half is invisible to every name-based census",
        "generated": date.today().isoformat(),
        "evidence_cutoff": date.today().isoformat(),
        "corpus": {"source": "e437_name_recall.corpus (self-excluded)",
                   "files": len(sources), "parse_failures": idx["failed"][:20],
                   "files_starting_with_a_utf8_bom": bom,
                   "bom_note": "read with utf-8-sig: a leading U+FEFF makes ast.parse raise, which "
                               "would have published 100+ in-repo modules as syntax errors and "
                               "silently shrunk both the function and the method population"},
        "summary": summary,
        "collisions": sorted(rows, key=lambda r: (-r["colliding_modules_without_import"], r["name"])),
        "anchor": anchor(rows, funcs, methods),
        "method_limits": list(METHOD_LIMITS),
        "verdict": verdict,
        "verdict_vocab": list(V_VERDICT_VOCAB),
    }
    return face


def anchor(rows: list[dict], funcs: dict, methods: dict) -> dict:
    """E450's own case: the 13 name hits that came from one module with zero binding hits."""
    rel = "Tools/pool_worker.py"
    own_funcs = sorted(n for n, defs in funcs.items() if any(d["file"] == rel for d in defs))
    hit = {r["name"]: r for r in rows if r["name"] in own_funcs}
    return {
        "module": rel,
        "e450_note": "E450 read 13 name hits from this module and 0 binding hits, which is the "
                     "observation this study prices repo-wide",
        "module_level_functions_here": len(own_funcs),
        "of_those_that_also_name_a_method_elsewhere": len(hit),
        "names": sorted(hit),
    }


def verdict_for(summary: dict) -> str:
    if not summary["collision_pairs"]:
        return V_EMPTY
    if not summary["collision_pairs_without_an_import_edge"]:
        return V_ALL_JUSTIFIED
    return V_SOME_UNJUSTIFIED


def write_face(face: dict) -> str:
    os.makedirs(os.path.join(ROOT, OUTDIR), exist_ok=True)
    dated = os.path.join(ROOT, OUTDIR, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"]))
    latest = os.path.join(ROOT, OUTDIR, FACE_NAME)
    body = json.dumps(face, ensure_ascii=False, indent=1)
    with io.open(dated, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body + "\n")
    with io.open(latest, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body + "\n")
    return os.path.relpath(dated, ROOT)


def _load(path: str) -> dict:
    with io.open(os.path.join(ROOT, path), "r", encoding="utf-8") as fh:
        return json.load(fh)


def tally_problems(face: dict) -> list[str]:
    """Every published tally re-derived from the published rows (no corpus walk)."""
    problems: list[str] = []
    rows = face["collisions"]
    s = face["summary"]
    if len(rows) != s["names_with_a_method_collision"]:
        problems.append("row count %d != summary %d" % (len(rows),
                                                        s["names_with_a_method_collision"]))
    pairs = sum(r["colliding_modules"] for r in rows)
    if pairs != s["collision_pairs"]:
        problems.append("pair sum %d != summary %d" % (pairs, s["collision_pairs"]))
    without = sum(r["colliding_modules_without_import"] for r in rows)
    if without != s["collision_pairs_without_an_import_edge"]:
        problems.append("unpriced sum %d != summary %d" % (without,
                                                           s["collision_pairs_without_an_import_edge"]))
    for r in rows:
        if r["colliding_modules_with_import"] + r["colliding_modules_without_import"] != r["colliding_modules"]:
            problems.append("%s: with+without != total" % r["name"])
        if len(r["without_import_examples"]) > r["colliding_modules_without_import"]:
            problems.append("%s: more examples than rows" % r["name"])
        if r["colliding_modules_without_import"] == 0 and r["without_import_examples"]:
            problems.append("%s: examples on a zero arm" % r["name"])
    if s["collision_pairs"]:
        share = round(s["collision_pairs_without_an_import_edge"] / s["collision_pairs"], 6)
        if share != s["share_of_pairs_without_an_import_edge"]:
            problems.append("share does not re-derive")
    if verdict_for({"collision_pairs": s["collision_pairs"],
                    "collision_pairs_without_an_import_edge":
                        s["collision_pairs_without_an_import_edge"]}) != face["verdict"]:
        problems.append("verdict does not re-derive from the summary")
    if s["distinct_function_names"]:
        nr = round(s["names_with_a_method_collision"] / s["distinct_function_names"], 6)
        if nr != s["share_of_names_colliding"]:
            problems.append("name share does not re-derive")
    return problems


def verify(face: dict | None = None) -> list[str]:
    face = face or _load(os.path.join(OUTDIR, FACE_NAME))
    fresh = build()
    res = gt.classify(face, fresh, list_key="collisions", row_id="name",
                      class_fields=("defined_in", "nests"))
    problems = [] if res.get("verdict") in (gt.IDENTICAL, gt.PURE_GROWTH) else [
        "growth: %s" % gt.describe(res)]
    problems += ["tally: " + p for p in tally_problems(fresh)]
    for r in fresh["collisions"][:400]:
        if r["colliding_modules_without_import"] < 0:
            problems.append("%s: negative arm" % r["name"])
    return problems


FIXTURES = {
    "pkg/mod_a.py": "def shared_name(x):\n    return x\n\n\nclass Local(object):\n"
                    "    def shared_name(self):\n        return 1\n",
    "pkg/mod_b.py": "class Carrier(object):\n    def shared_name(self):\n        return 2\n",
    "pkg/mod_c.py": "from pkg.mod_a import shared_name\n\n\nclass Carrier(object):\n"
                    "    def shared_name(self):\n        return 3\n",
    "pkg/mod_d.py": "def outer():\n    class Inner(object):\n        def shared_name(self):\n"
                    "            return 4\n    return Inner\n",
    "pkg/mod_e.py": "class Carrier(object):\n    shared_name = 5\n",
    "pkg/mod_f.py": "import pkg.mod_a\n\n\nclass Carrier(object):\n    def shared_name(self):\n"
                    "        return 6\n",
    "pkg/mod_g.py": "from pkg.mod_a import shared_name as alias\n\n\nclass Carrier(object):\n"
                    "    def shared_name(self):\n        return 7\n",
    "pkg/mod_h.py": "def inner_only():\n    def shared_name(y):\n        return y\n    return shared_name\n",
    "pkg/broken.py": "def oops(:\n",
}


def selftest() -> int:
    legs = 0
    bad = 0

    def leg(ok, what):
        nonlocal legs, bad
        legs += 1
        if not ok:
            bad += 1
            print("FAIL %s" % what)

    face = build(dict(FIXTURES))
    s = face["summary"]
    rows = {r["name"]: r for r in face["collisions"]}

    leg("shared_name" in rows, "a module-level function that names a method elsewhere is a row")
    leg(rows["shared_name"]["colliding_modules"] == 5,
        "carriers counted: mod_b, mod_c, mod_d(nested), mod_f, mod_g (mod_a is the definition, "
        "mod_e is an attribute not a def) -- got %d" % rows["shared_name"]["colliding_modules"])
    leg(rows["shared_name"]["colliding_modules_with_import"] == 2,
        "mod_c and mod_g import the function -- got %d"
        % rows["shared_name"]["colliding_modules_with_import"])
    leg(rows["shared_name"]["colliding_modules_without_import"] == 3,
        "mod_b, mod_d and mod_f never import it (mod_f imports the module, not the name) -- got %d"
        % rows["shared_name"]["colliding_modules_without_import"])
    leg(NEST_IN_FUNC in rows["shared_name"]["nests"],
        "a class defined inside a function is counted with its own nesting kind")
    leg("mod_e.py" not in [x["file"] for x in rows["shared_name"]["without_import_examples"]]
        and not any("mod_e.py" in [m] for m in [x["file"] for x in rows["shared_name"]["with_import_examples"]]),
        "a class attribute that is not a def does not collide")
    leg(s["parse_failures"] == 1 and
        face["corpus"]["parse_failures"][0]["file"] == "pkg/broken.py",
        "a file that fails to parse is published, not dropped")
    leg("inner_only" not in rows and "shared_name" in rows,
        "only module-level functions are the population (a nested def is not)")
    leg(s["classes_indexed"] >= 6, "class census counted %d" % s["classes_indexed"])
    leg(s["collision_pairs"] == rows["shared_name"]["colliding_modules"],
        "pair total equals the single row's carrier count")
    leg(face["verdict"] == V_SOME_UNJUSTIFIED, "verdict is the unpriced half, got %s" % face["verdict"])
    leg(tally_problems(face) == [], "tallies re-derive from the published rows")

    # a justification-only fixture: every carrier imports the function
    just = build({"p/x.py": "def f():\n    return 1\n",
                  "p/y.py": "from p.x import f\n\n\nclass C(object):\n    def f(self):\n        return 2\n"})
    leg(just["verdict"] == V_ALL_JUSTIFIED, "all-carriers-import fixture yields the justified verdict")

    # no collision at all
    empty = build({"p/x.py": "def only_here():\n    return 1\n",
                   "p/y.py": "class C(object):\n    def other(self):\n        return 2\n"})
    leg(empty["verdict"] == V_EMPTY, "no-collision fixture yields the empty verdict")
    leg(empty["collisions"] == [], "no-collision fixture publishes no rows")

    # a shrunken face must not tolerate
    shrunk = json.loads(json.dumps(face))
    shrunk["summary"]["collision_pairs"] += 1
    leg(not gt.tolerates(gt.classify(shrunk, face, list_key="collisions", row_id="name",
                                     class_fields=("defined_in", "nests"))),
        "a stored count larger than the fresh reading is not tolerance")
    # a renamed row is a lost row
    lost = json.loads(json.dumps(face))
    lost["collisions"][0]["name"] = "renamed_away"
    leg(not gt.tolerates(gt.classify(lost, face, list_key="collisions", row_id="name",
                                     class_fields=("defined_in", "nests"))),
        "a vanished name is not tolerance")

    print("selftest %d/%d" % (legs - bad, legs))
    return 0 if bad == 0 else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["run", "verify", "check", "selftest"])
    args = ap.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    if args.mode == "run":
        face = build()
        path = write_face(face)
        problems = tally_problems(face)
        print(json.dumps({"face": path, "summary": face["summary"], "verdict": face["verdict"],
                          "tally_problems": problems}, ensure_ascii=False, indent=1))
        return 0 if not problems else 2
    if args.mode == "check":
        face = _load(os.path.join(OUTDIR, FACE_NAME))
        problems = tally_problems(face)
        print("check problems=%s" % problems)
        return 0 if not problems else 2
    problems = verify()
    print("verify problems=%s" % problems)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))