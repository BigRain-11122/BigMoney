"""E646 -- are E642's seven cross-module key-name hits the same key, or generic-word collisions?

E642 published a weak arm beside its per-module zero: 7 module-level two-depth write sites outside the
modules that hold the counted read lines name one of the 6 counted row keys.  E207/E208 say a name is
not a measurement, and "verdict"/"rows" are ordinary English words that a round script uses for its own
report.  So the hit is only interesting if the write can reach the container the counted read reads.

This study takes each hit and asks what a static reader can ask about lineage:

  * the write's container -- the outermost Subscript's `.value`, unparsed, and the leftmost Name that
    holds it, so `A["verdict"] = x` is published as a container expression and not as a key;
  * whether that root name is bound in the hit module's own body, and how (module-level assignment,
    import alias, or nothing in the body);
  * the counted read line every named key belongs to (module, line, function, receiver) -- the same
    join E638/E633 publish, not a second definition;
  * the pair's lineage class: same module, an import edge either way between the two modules, the
    container root's name equalling the read's receiver name, or name collision only;
  * the module class of the hit (throwaway round script / smoke harness / production module), because
    a hit in a round script's own report dict cannot be the corpus face the read reads.

Nothing here re-reads E642's rows: the hits are re-derived from the tree with E642's own population and
owner rule, and E642's published count is carried only as a reconciliation figure.
"""
import argparse
import ast
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-10"
FACE = "CROSSMODULEKEY.json"
LATEST = "crossmodulekey_latest.json"
STUDY = "E646_crossmodule_key"
SELF_PARTS = ("e646_", "run_e646_", "_probe_e646", "_r1664")
SOURCE_FACE = "results/state_tilt/MODULEWRITEKEY.json"
MAX_EXAMPLES = 25

import e638_two_depth_subscripts as e638  # noqa: E402
import e640_writeread_collide as e640  # noqa: E402
import e642_module_write_key as e642  # noqa: E402

V_ALL_GENERIC_WORD_COLLISIONS = (
    "every hit is a word collision: none shares a module, an import edge, or a receiver name with the "
    "counted read it appears to collide with, so the key spelling is the only link between them")
V_SAME_NAME_WITHOUT_LINEAGE = (
    "at least one hit's container root carries the counted read's receiver name, but no hit shares a "
    "module or an import edge with its read, so name equality alone is not lineage")
V_SHARED_LINEAGE = (
    "at least one hit shares a module or an import edge with the counted read it collides with, so "
    "the write can reach the same container")
V_NO_HITS = (
    "the cross-module arm carries no hits, so there is no collision to price and the question does "
    "not apply")
V_OFF_POPULATION = (
    "hits exist but no counted read line joins to them, so the lineage question is unsettled rather "
    "than answered")

LINEAGE_CLASSES = ("same_module", "imported", "same_name_only", "name_collision")


def say(line):
    sys.stdout.write(line + "\n")


def rel(module, root=ROOT):
    return os.path.relpath(module, root).replace("\\", "/")


def corpus(root=ROOT):
    out = []
    for p in e642.corpus(root):
        if os.path.basename(p).startswith(SELF_PARTS):
            continue
        out.append(p)
    return out


def tree_of(path):
    src = io.open(path, encoding="utf-8", errors="replace").read()
    return ast.parse(src), src


def root_name_of(node):
    """Leftmost Name holding a subscript chain, through attributes (`S.x["k"]` -> `S`)."""
    while isinstance(node, (ast.Subscript, ast.Attribute)):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def container_of(path, line, column):
    """(payload, None) or (None, why): the container expression of the outermost Subscript at a site."""
    try:
        if os.path.getsize(path) > e638.MAX_BYTES:
            return None, "over_the_size_cap"
    except OSError:
        return None, "unreadable"
    try:
        tree, src = tree_of(path)
    except (OSError, SyntaxError, ValueError):
        return None, "does_not_parse"
    best = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Subscript):
            continue
        if (node.lineno, node.col_offset) != (line, column):
            continue
        depth = e638.subscript_depth(node)
        if best is None or depth > best[0]:
            best = (depth, node)
    if best is None:
        return None, "site_not_found"
    node = best[1]
    expression = ast.unparse(node.value)
    return {
        "container_expression": expression,
        "container_root": root_name_of(node.value),
        "container_depth": int(best[0]),
        "container_source": expression.replace("\n", " ")[:160],
        "module_lines": len(src.splitlines()),
    }, None


def binding_of(tree, name):
    """How a name is bound in the module body: assignment / import alias / nothing."""
    if not name:
        return {"kind": "no_root_name", "line": None}
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign):
            for t in stmt.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    return {"kind": "module_assignment", "line": stmt.lineno}
                if isinstance(t, (ast.Tuple, ast.List)):
                    for elt in t.elts:
                        if isinstance(elt, ast.Name) and elt.id == name:
                            return {"kind": "module_assignment", "line": stmt.lineno}
        elif isinstance(stmt, ast.AnnAssign):
            t = stmt.target
            if isinstance(t, ast.Name) and t.id == name:
                return {"kind": "module_assignment", "line": stmt.lineno}
        elif isinstance(stmt, ast.Import):
            for a in stmt.names:
                if (a.asname or a.name.split(".")[0]) == name:
                    return {"kind": "import", "line": stmt.lineno, "imports": a.name}
        elif isinstance(stmt, ast.ImportFrom):
            for a in stmt.names:
                if (a.asname or a.name) == name:
                    return {"kind": "import", "line": stmt.lineno,
                            "imports": (stmt.module or "") + "." + a.name}
    return {"kind": "not_bound_in_module_body", "line": None}


def imports_of(tree):
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                out.add(a.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                out.add(node.module)
            for a in node.names:
                if node.module:
                    out.add(node.module + "." + a.name)
    return out


def module_aliases(module_rel):
    """Every spelling an importer could use for a tree module."""
    stem = module_rel[:-3] if module_rel.endswith(".py") else module_rel
    parts = stem.split("/")
    out = {stem.replace("/", ".")}
    for i in range(len(parts)):
        out.add(".".join(parts[i:]))
    out.discard("")
    return out


def module_class(module_rel):
    base = os.path.basename(module_rel)
    if module_rel.startswith("results/") and base.startswith("_r"):
        return "round_scratch_script"
    if base.startswith("run_e") or base.startswith("_probe_"):
        return "smoke_or_probe_harness"
    return "production_module"


def read_population(root=ROOT):
    """The counted read lines, from E638's join (one definition, not a second)."""
    out = []
    for r in e638.join_counted_lines(root):
        module = (r.get("module") or "").replace("\\", "/")
        if not module:
            continue
        out.append({
            "module": module,
            "line": r.get("read_line"),
            "function": r.get("function"),
            "key": r.get("key"),
            "receiver": r.get("receiver"),
        })
    out.sort(key=lambda r: (r["module"], r["line"] or 0, r["key"] or ""))
    return out


def re_derive_hits(root, files, keys):
    """Module-level two-depth writes anywhere naming a counted row key, with E642's own rule."""
    hits = []
    for p in files:
        got, why = e642.module_level_sites(p)
        if got is None:
            continue
        for s in got["sites"]:
            if not s["any_member_is_write"]:
                continue
            named = sorted(set(s["keys"]) & keys)
            if not named:
                continue
            hits.append({"module": rel(p, root), "path": p, "line": s["line"],
                         "column": s["column"], "keys": s["keys"],
                         "row_keys_named": named,
                         "member_ctx": s["member_ctx"]})
    hits.sort(key=lambda h: (h["module"], h["line"], h["column"]))
    return hits


def count_published_hits(root=ROOT):
    """E642's published hit count -- a reconciliation figure, never an input."""
    path = os.path.join(root, SOURCE_FACE)
    try:
        doc = json.load(io.open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return ((doc.get("cross_module") or {})
            .get("module_level_write_sites_naming_a_counted_row_key"))


def classify_pair(hit, read, hit_imports, read_imports, read_aliases, hit_aliases):
    """One hit x one counted read line -> its lineage class and the evidence behind it."""
    hit_module = hit["module"]
    read_module = read["module"]
    same_module = hit_module == read_module
    forward = bool(read_aliases & hit_imports)
    backward = bool(hit_aliases & read_imports)
    same_name = (hit.get("container_root") is not None
                 and read.get("receiver") is not None
                 and hit["container_root"] == read["receiver"])
    if same_module:
        cls = "same_module"
    elif forward or backward:
        cls = "imported"
    elif same_name:
        cls = "same_name_only"
    else:
        cls = "name_collision"
    return {
        "lineage": cls,
        "same_module": same_module,
        "hit_imports_the_read_module": forward,
        "read_module_imports_the_hit": backward,
        "container_root_equals_read_receiver": same_name,
        "container_root": hit.get("container_root"),
        "read_receiver": read.get("receiver"),
    }


def measure(root=ROOT):
    files = corpus(root)
    reads = read_population(root)
    keys = {r["key"] for r in reads if r["key"]}
    hits = re_derive_hits(root, files, keys)

    read_imports_cache = {}
    rows = []
    pairs = []
    for h in hits:
        row = {
            "module": h["module"],
            "line": h["line"],
            "column": h["column"],
            "keys": h["keys"],
            "row_keys_named": h["row_keys_named"],
            "member_ctx": h["member_ctx"],
            "module_class": module_class(h["module"]),
        }
        cont, why = container_of(h["path"], h["line"], h["column"])
        if cont is None:
            row["container_problem"] = why
            row.update({"container_expression": None, "container_root": None,
                        "container_binding": {"kind": "unmeasured", "line": None}})
            tree = None
        else:
            row["container_problem"] = None
            tree, _src = tree_of(h["path"])
            row.update({
                "container_expression": cont["container_expression"],
                "container_root": cont["container_root"],
                "container_depth": cont["container_depth"],
                "container_binding": binding_of(tree, cont["container_root"]),
            })
        hit_imports = imports_of(tree) if tree is not None else set()
        matched = [r for r in reads if r["key"] in row["row_keys_named"]]
        row["matched_read_lines"] = [
            {"module": r["module"], "line": r["line"], "function": r["function"],
             "receiver": r["receiver"], "key": r["key"]} for r in matched]
        for r in matched:
            rm = r["module"]
            if rm not in read_imports_cache:
                path = os.path.join(root, rm)
                try:
                    rtree, _ = tree_of(path)
                    read_imports_cache[rm] = imports_of(rtree)
                except (OSError, SyntaxError, ValueError):
                    read_imports_cache[rm] = set()
            pair = {
                "hit_module": h["module"],
                "hit_line": h["line"],
                "hit_column": h["column"],
                "key": r["key"],
                "read_module": rm,
                "read_line": r["line"],
                "read_function": r["function"],
                "read_receiver": r["receiver"],
                "module_class_of_the_hit": row["module_class"],
            }
            pair.update({"container_root": row.get("container_root")})
            pair.update(classify_pair(row, r, hit_imports, read_imports_cache[rm],
                                      module_aliases(rm), module_aliases(h["module"])))
            pairs.append(pair)
        row["lineage_classes_of_its_pairs"] = sorted({p["lineage"] for p in pairs
                                                       if p["hit_module"] == h["module"]
                                                       and p["hit_line"] == h["line"]})
        rows.append(row)

    counts = counts_of(rows, pairs, len(files), hits, reads, count_published_hits(root))
    m = {
        "study": STUDY,
        "source_face": SOURCE_FACE,
        "method": ("re-derive E642's cross-module arm from the tree (module-level two-depth writes "
                   "naming any counted row key), then for each hit publish its container expression "
                   "and the module-body binding of its root name, join it to the counted read lines "
                   "of the same key via E638, and classify each pair as same_module / imported / "
                   "same_name_only / name_collision"),
        "population_source": ("%d Python files of E642's corpus, %d counted read line(s) over %d key(s), "
                              "%d cross-module hit(s)" % (len(files), len(reads), len(keys), len(hits))),
        "counts": counts,
        "rows": rows,
        "pairs": pairs,
        "limits": [
            "lineage here is static: a module that does not import the read's module cannot reach the "
            "read's container object by name, but it can still share a path or key spelling, so the "
            "test only ever refutes reachability and never proves it",
            "import text is matched against every dotted spelling the read module could be imported "
            "under, so a hit that reaches the read module through an importlib.import_module string "
            "is missed by this leg and is published as a limit of the arm rather than a zero",
            "the container expression is the outermost Subscript's own `.value` unparsed, so a hit "
            "whose container is itself computed (a call result, a comprehension) is published as that "
            "expression and its root name is None",
            "the read population is E638's join (one definition); a change to that join moves this "
            "study's pairs without touching its hits",
            "module class is a filename convention (results/_r* is a throwaway round script, run_e* "
            "is a harness), not a measured property of the code",
            "files over 1MB are skipped rather than parsed (E391's cap) and are counted separately",
        ],
    }
    m["verdict"] = decide(counts)
    m["answer"] = answer_of(counts)
    return m


def counts_of(rows, pairs, files_scanned, hits, reads, published_hits):
    by_class = {k: 0 for k in LINEAGE_CLASSES}
    for p in pairs:
        by_class[p["lineage"]] = by_class.get(p["lineage"], 0) + 1
    key_hist = {}
    for r in rows:
        key_hist[r["module_class"]] = key_hist.get(r["module_class"], 0) + 1
    binding_hist = {}
    for r in rows:
        kind = (r.get("container_binding") or {}).get("kind")
        binding_hist[kind] = binding_hist.get(kind, 0) + 1
    return {
        "python_files_scanned": int(files_scanned),
        "counted_read_lines": len(reads),
        "counted_row_keys": len({r["key"] for r in reads if r["key"]}),
        "hits_re_derived": len(hits),
        "hits_published_by_e642": (None if published_hits is None else int(published_hits)),
        "distinct_hit_modules": len({r["module"] for r in rows}),
        "distinct_hit_keys": len({k for r in rows for k in r["keys"]}),
        "hits_with_a_container_expression": sum(1 for r in rows if r.get("container_expression")),
        "hits_with_a_root_name": sum(1 for r in rows if r.get("container_root")),
        "hits_whose_root_is_bound_in_its_own_module": sum(
            1 for r in rows
            if (r.get("container_binding") or {}).get("kind") in ("module_assignment", "import")),
        "hit_module_class_histogram": dict(sorted(key_hist.items())),
        "container_binding_histogram": dict(sorted(binding_hist.items())),
        "pairs": len(pairs),
        "pairs_by_lineage": dict(sorted(by_class.items())),
        "pairs_sharing_a_module": by_class.get("same_module", 0),
        "pairs_linked_by_an_import_edge": by_class.get("imported", 0),
        "pairs_matching_on_the_name_alone": by_class.get("same_name_only", 0),
        "pairs_that_are_name_collisions": by_class.get("name_collision", 0),
        "read_modules_involved": len({p["read_module"] for p in pairs}),
        "hits_with_no_counted_read_line": sum(1 for r in rows if not r.get("matched_read_lines")),
    }


def decide(c):
    if not c.get("hits_re_derived"):
        return V_NO_HITS
    if not c.get("pairs"):
        return V_OFF_POPULATION
    if c.get("pairs_sharing_a_module") or c.get("pairs_linked_by_an_import_edge"):
        return V_SHARED_LINEAGE
    if c.get("pairs_matching_on_the_name_alone"):
        return V_SAME_NAME_WITHOUT_LINEAGE
    return V_ALL_GENERIC_WORD_COLLISIONS


def answer_of(c):
    return ("%d file(s), %d counted read line(s) over %d key(s); %d cross-module hit(s) re-derived "
            "(E642 published %s) in %d module(s) over %d distinct key(s); %d hit(s) carry a container "
            "expression and %d a root name of which %d are bound in their own module body; the %d "
            "hit x read pair(s) split %d same-module / %d imported / %d same-name-only / %d name "
            "collision(s) across %d read module(s), with %d hit(s) having no counted read line at all"
            % (c.get("python_files_scanned"),
               c.get("counted_read_lines"), c.get("counted_row_keys"),
               c.get("hits_re_derived"), c.get("hits_published_by_e642"),
               c.get("distinct_hit_modules"), c.get("distinct_hit_keys"),
               c.get("hits_with_a_container_expression"), c.get("hits_with_a_root_name"),
               c.get("hits_whose_root_is_bound_in_its_own_module"),
               c.get("pairs"),
               c.get("pairs_sharing_a_module"), c.get("pairs_linked_by_an_import_edge"),
               c.get("pairs_matching_on_the_name_alone"), c.get("pairs_that_are_name_collisions"),
               c.get("read_modules_involved"),
               c.get("hits_with_no_counted_read_line")))


def face_from(m):
    return {
        "study": STUDY,
        "date": TODAY,
        "evidence_cutoff": TODAY,
        "source_face": SOURCE_FACE,
        "method": m["method"],
        "population_source": m["population_source"],
        "counts": m["counts"],
        "rows": m["rows"],
        "pairs": m["pairs"],
        "limits": m["limits"],
        "verdict": m["verdict"],
        "answer": m["answer"],
    }


COUNT_KEYS = (
    "counted_read_lines", "counted_row_keys", "hits_re_derived", "distinct_hit_modules",
    "distinct_hit_keys", "hits_with_a_container_expression", "hits_with_a_root_name",
    "hits_whose_root_is_bound_in_its_own_module", "pairs", "pairs_sharing_a_module",
    "pairs_linked_by_an_import_edge", "pairs_matching_on_the_name_alone",
    "pairs_that_are_name_collisions", "read_modules_involved", "hits_with_no_counted_read_line",
)


def face_problems(face):
    """Everything the smoke leg refuses, re-derived from the face's own rows and pairs."""
    problems = []
    if not face:
        return ["face is absent or empty"]
    rows = face.get("rows") or []
    pairs = face.get("pairs") or []
    c = face.get("counts") or {}
    live = {
        "counted_read_lines": (c.get("counted_read_lines") or 0),
        "counted_row_keys": (c.get("counted_row_keys") or 0),
        "hits_re_derived": len(rows),
        "distinct_hit_modules": len({r.get("module") for r in rows}),
        "distinct_hit_keys": len({k for r in rows for k in (r.get("keys") or [])}),
        "hits_with_a_container_expression": sum(1 for r in rows if r.get("container_expression")),
        "hits_with_a_root_name": sum(1 for r in rows if r.get("container_root")),
        "hits_whose_root_is_bound_in_its_own_module": sum(
            1 for r in rows
            if (r.get("container_binding") or {}).get("kind") in ("module_assignment", "import")),
        "pairs": len(pairs),
        "pairs_sharing_a_module": sum(1 for p in pairs if p.get("lineage") == "same_module"),
        "pairs_linked_by_an_import_edge": sum(1 for p in pairs if p.get("lineage") == "imported"),
        "pairs_matching_on_the_name_alone": sum(
            1 for p in pairs if p.get("lineage") == "same_name_only"),
        "pairs_that_are_name_collisions": sum(
            1 for p in pairs if p.get("lineage") == "name_collision"),
        "read_modules_involved": len({p.get("read_module") for p in pairs}),
        "hits_with_no_counted_read_line": sum(
            1 for r in rows if not r.get("matched_read_lines")),
    }
    for key in COUNT_KEYS:
        if key == "counted_read_lines" or key == "counted_row_keys":
            continue
        if c.get(key) != live.get(key):
            problems.append("counts.%s does not re-add from the rows" % key)
    if (c.get("pairs_sharing_a_module", 0) + c.get("pairs_linked_by_an_import_edge", 0)
            + c.get("pairs_matching_on_the_name_alone", 0)
            + c.get("pairs_that_are_name_collisions", 0)) != len(pairs):
        problems.append("the four lineage buckets do not add up to the pairs")
    hist = c.get("hit_module_class_histogram") or {}
    if sum(hist.values()) != len(rows):
        problems.append("the module-class histogram is not the per-hit count")
    bhist = c.get("container_binding_histogram") or {}
    if sum(bhist.values()) != len(rows):
        problems.append("the binding histogram is not the per-hit count")
    # every pair must be classified by the same rule the face publishes
    for p in pairs:
        forced = {k: v for k, v in (
            ("same_module", p.get("module_class_of_the_hit") is not None
             and p.get("hit_module") == p.get("read_module")),
            ("imported", bool(p.get("hit_imports_the_read_module")
                              or p.get("read_module_imports_the_hit"))),
            ("same_name_only", bool(p.get("container_root_equals_read_receiver"))))}
        want = ("same_module" if forced["same_module"]
                else "imported" if forced["imported"]
                else "same_name_only" if forced["same_name_only"]
                else "name_collision")
        if p.get("lineage") != want:
            problems.append("pair %s:%s x %s:%s is classified %r but its own flags force %r"
                            % (p.get("hit_module"), p.get("hit_line"), p.get("read_module"),
                               p.get("read_line"), p.get("lineage"), want))
            break
    for r in rows:
        named = set(r.get("row_keys_named") or [])
        if not named <= set(r.get("keys") or []):
            problems.append("module %s names a key its members do not carry" % r.get("module"))
            break
        for m in r.get("matched_read_lines") or []:
            if m.get("key") not in named:
                problems.append("module %s joins a read on a key it does not name"
                                % r.get("module"))
                break
        if (r.get("container_binding") or {}).get("kind") == "unmeasured" \
                and r.get("container_expression"):
            problems.append("module %s publishes a container with an unmeasured binding"
                            % r.get("module"))
            break
    if c.get("hits_published_by_e642") is not None \
            and c.get("hits_published_by_e642") != c.get("hits_re_derived"):
        problems.append("the re-derived hit count is not the one E642 published")
    if decide(live) != face.get("verdict"):
        problems.append("the published verdict is not the one the counts force")
    if face.get("verdict") == V_ALL_GENERIC_WORD_COLLISIONS \
            and (live["pairs_linked_by_an_import_edge"] or live["pairs_sharing_a_module"]
                 or live["pairs_matching_on_the_name_alone"]):
        problems.append("the all-collisions verdict is not the one its own counts force")
    if face.get("verdict") == V_SHARED_LINEAGE \
            and not (live["pairs_linked_by_an_import_edge"] or live["pairs_sharing_a_module"]):
        problems.append("the shared-lineage verdict is not the one its own counts force")
    return problems


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        path = os.path.join(out_dir, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
        say("run: %s" % os.path.relpath(path, ROOT))


def build(root=ROOT, out_dir=None):
    doc = face_from(measure(root))
    write_face(out_dir or OUTDIR, doc)
    c = doc["counts"]
    say("run: files=%d reads=%d keys=%d hits=%d(e642 %s) pairs=%d by_lineage=%s"
        % (c["python_files_scanned"], c["counted_read_lines"], c["counted_row_keys"],
           c["hits_re_derived"], c["hits_published_by_e642"], c["pairs"],
           json.dumps(c["pairs_by_lineage"], sort_keys=True)))
    say("run: verdict=" + doc["verdict"])
    say("run: answer=" + doc["answer"])
    return doc, []


# ---------------------------------------------------------------- selftest
def _hit(module="a.py", line=3, column=0, keys=("k",), named=("k",), root="D",
         cls="production_module"):
    return {"module": module, "path": None, "line": line, "column": column, "keys": list(keys),
            "row_keys_named": list(named), "member_ctx": ["load", "store"],
            "module_class": cls, "container_root": root, "container_expression": "%s['k']" % root,
            "container_binding": {"kind": "module_assignment", "line": 1},
            "matched_read_lines": [{"module": "b.py", "line": 20, "function": "f",
                                    "receiver": "R", "key": "k"}]}


def _pair(hit, lineage="name_collision", read_module="b.py", **flags):
    base = {"hit_module": hit["module"], "hit_line": hit["line"], "hit_column": hit["column"],
            "key": "k", "read_module": read_module, "read_line": 20, "read_function": "f",
            "read_receiver": "R", "module_class_of_the_hit": hit["module_class"],
            "container_root": hit["container_root"], "lineage": lineage,
            "same_module": lineage == "same_module",
            "hit_imports_the_read_module": lineage == "imported",
            "read_module_imports_the_hit": False,
            "container_root_equals_read_receiver": lineage == "same_name_only"}
    base.update(flags)
    return base


def _counts(rows, pairs, published=None):
    return counts_of(rows, pairs, 10, rows, [{"key": "k"}] * 1, published)


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True))
            say("PASS :: " + name)
        except AssertionError as exc:
            legs.append((name, False))
            say("FAIL :: %s :: %s" % (name, exc))

    def a_container_is_the_outermost_subscripts_value():
        path = e640._fixture_path('OUT = {}\nOUT["k"]["j"] = 1\n')
        try:
            got, why = container_of(path, 2, 0)
            assert why is None, why
            assert got["container_root"] == "OUT", got
            assert "OUT" in got["container_expression"], got
            assert got["container_depth"] == 2, got
        finally:
            try:
                os.remove(path)
            except OSError:
                pass

    def an_attribute_chain_reports_its_leftmost_name():
        node = ast.parse('S.x["k"]["j"] = 1').body[0].targets[0]
        assert root_name_of(node.value) == "S", ast.dump(node.value)

    def the_binding_of_a_root_name_is_how_the_body_binds_it():
        tree = ast.parse("import json\nD = {}\ndef f(X):\n    return X\n")
        assert binding_of(tree, "D")["kind"] == "module_assignment"
        assert binding_of(tree, "json")["kind"] == "import"
        assert binding_of(tree, "X")["kind"] == "not_bound_in_module_body"
        assert binding_of(tree, None)["kind"] == "no_root_name"

    def import_aliases_cover_every_spelling():
        al = module_aliases("scripts/e382_key_projection_delta.py")
        assert "e382_key_projection_delta" in al, al
        assert "scripts.e382_key_projection_delta" in al, al

    def a_pair_with_no_link_is_a_name_collision():
        p = classify_pair(_hit(), {"module": "b.py", "line": 20, "function": "f", "key": "k",
                                   "receiver": "R"}, {"ast"}, set(), module_aliases("b.py"),
                          module_aliases("a.py"))
        assert p["lineage"] == "name_collision", p

    def a_shared_receiver_name_is_only_a_name():
        p = classify_pair(_hit(root="R"), {"module": "b.py", "line": 20, "function": "f",
                                           "key": "k", "receiver": "R"}, set(), set(),
                          module_aliases("b.py"), module_aliases("a.py"))
        assert p["lineage"] == "same_name_only", p

    def an_import_edge_is_lineage():
        p = classify_pair(_hit(root="R"), {"module": "b.py", "line": 20, "function": "f",
                                           "key": "k", "receiver": "R"}, {"b"}, set(),
                          module_aliases("b.py"), module_aliases("a.py"))
        assert p["lineage"] == "imported", p

    def the_backward_edge_counts_too():
        p = classify_pair(_hit(), {"module": "b.py", "line": 20, "function": "f", "key": "k",
                                   "receiver": "R"}, set(), {"a"}, module_aliases("b.py"),
                          module_aliases("a.py"))
        assert p["lineage"] == "imported", p

    def a_same_module_pair_is_not_a_collision():
        p = classify_pair(_hit(module="b.py"), {"module": "b.py", "line": 20, "function": "f",
                                                "key": "k", "receiver": "R"}, set(), set(),
                          module_aliases("b.py"), module_aliases("b.py"))
        assert p["lineage"] == "same_module", p

    def all_collisions_is_reachable():
        hit = _hit()
        c = _counts([hit], [_pair(hit)])
        assert c["pairs_that_are_name_collisions"] == 1, c
        assert decide(c) == V_ALL_GENERIC_WORD_COLLISIONS, c

    def same_name_only_is_reachable():
        hit = _hit()
        c = _counts([hit], [_pair(hit, "same_name_only")])
        assert decide(c) == V_SAME_NAME_WITHOUT_LINEAGE, c

    def shared_lineage_is_reachable():
        hit = _hit()
        c = _counts([hit], [_pair(hit, "imported")])
        assert decide(c) == V_SHARED_LINEAGE, c

    def no_hits_is_reachable():
        c = counts_of([], [], 10, [], [{"key": "k"}], 0)
        assert decide(c) == V_NO_HITS, c

    def off_population_is_reachable():
        hit = _hit()
        row = dict(hit, matched_read_lines=[])
        c = counts_of([row], [], 10, [row], [{"key": "k"}], 1)
        assert decide(c) == V_OFF_POPULATION, c

    def face_problems_accepts_a_sound_face():
        hit = _hit()
        for lineage in LINEAGE_CLASSES:
            pair = _pair(hit, lineage, read_module=("a.py" if lineage == "same_module"
                                                    else "b.py"))
            c = _counts([hit], [pair])
            face = {"rows": [hit], "pairs": [pair], "counts": c, "verdict": decide(c)}
            assert not face_problems(face), (lineage, face_problems(face))

    def face_problems_catches_a_wrong_verdict():
        hit = _hit()
        pair = _pair(hit)
        c = _counts([hit], [pair])
        face = {"rows": [hit], "pairs": [pair], "counts": c, "verdict": V_SHARED_LINEAGE}
        assert any("verdict" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_pair_whose_flags_do_not_force_its_class():
        hit = _hit()
        pair = _pair(hit, "name_collision", hit_imports_the_read_module=True)
        c = _counts([hit], [pair])
        face = {"rows": [hit], "pairs": [pair], "counts": c, "verdict": decide(c)}
        assert any("classified" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_summary_that_drifts():
        hit = _hit()
        pair = _pair(hit)
        c = _counts([hit], [pair])
        c["pairs"] = 99
        face = {"rows": [hit], "pairs": [pair], "counts": c, "verdict": decide(c)}
        assert any("does not re-add" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_bucket_that_does_not_add_up():
        hit = _hit()
        pair = _pair(hit)
        c = _counts([hit], [pair])
        c["pairs_that_are_name_collisions"] = 0
        face = {"rows": [hit], "pairs": [pair], "counts": c, "verdict": decide(c)}
        assert any("do not add up" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_read_joined_on_a_key_the_hit_does_not_name():
        hit = _hit(named=("zzz",))
        pair = _pair(hit)
        c = _counts([hit], [pair])
        face = {"rows": [hit], "pairs": [pair], "counts": c, "verdict": decide(c)}
        assert any("do not carry" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_reconciliation_that_moves():
        hit = _hit()
        pair = _pair(hit)
        c = _counts([hit], [pair], published=9)
        face = {"rows": [hit], "pairs": [pair], "counts": c, "verdict": decide(c)}
        assert any("E642" in p for p in face_problems(face)), face_problems(face)

    def answer_names_the_numbers():
        hit = _hit()
        a = answer_of(_counts([hit], [_pair(hit)]))
        assert "1 cross-module hit(s) re-derived" in a, a
        assert "1 name collision(s)" in a, a

    for name, fn in [
        ("a_container_is_the_outermost_subscripts_value",
         a_container_is_the_outermost_subscripts_value),
        ("an_attribute_chain_reports_its_leftmost_name",
         an_attribute_chain_reports_its_leftmost_name),
        ("the_binding_of_a_root_name_is_how_the_body_binds_it",
         the_binding_of_a_root_name_is_how_the_body_binds_it),
        ("import_aliases_cover_every_spelling", import_aliases_cover_every_spelling),
        ("a_pair_with_no_link_is_a_name_collision", a_pair_with_no_link_is_a_name_collision),
        ("a_shared_receiver_name_is_only_a_name", a_shared_receiver_name_is_only_a_name),
        ("an_import_edge_is_lineage", an_import_edge_is_lineage),
        ("the_backward_edge_counts_too", the_backward_edge_counts_too),
        ("a_same_module_pair_is_not_a_collision", a_same_module_pair_is_not_a_collision),
        ("all_collisions_is_reachable", all_collisions_is_reachable),
        ("same_name_only_is_reachable", same_name_only_is_reachable),
        ("shared_lineage_is_reachable", shared_lineage_is_reachable),
        ("no_hits_is_reachable", no_hits_is_reachable),
        ("off_population_is_reachable", off_population_is_reachable),
        ("face_problems_accepts_a_sound_face", face_problems_accepts_a_sound_face),
        ("face_problems_catches_a_wrong_verdict", face_problems_catches_a_wrong_verdict),
        ("face_problems_catches_a_pair_whose_flags_do_not_force_its_class",
         face_problems_catches_a_pair_whose_flags_do_not_force_its_class),
        ("face_problems_catches_a_summary_that_drifts",
         face_problems_catches_a_summary_that_drifts),
        ("face_problems_catches_a_bucket_that_does_not_add_up",
         face_problems_catches_a_bucket_that_does_not_add_up),
        ("face_problems_catches_a_read_joined_on_a_key_the_hit_does_not_name",
         face_problems_catches_a_read_joined_on_a_key_the_hit_does_not_name),
        ("face_problems_catches_a_reconciliation_that_moves",
         face_problems_catches_a_reconciliation_that_moves),
        ("answer_names_the_numbers", answer_names_the_numbers),
    ]:
        leg(name, fn)
    ok = sum(1 for _, good in legs if good)
    say("selftest: %d/%d legs green" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


# ---------------------------------------------------------------- CLI
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    args = ap.parse_args(argv[1:])
    cmd = args.cmd.lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        doc, problems = build(root=ROOT)
        problems = problems + face_problems(doc)
        say("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "verify":
        path = os.path.join(OUTDIR, FACE)
        if not os.path.exists(path):
            say("no face at %s" % path)
            return 1
        doc = json.load(io.open(path, encoding="utf-8"))
        problems = face_problems(doc)
        say("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    doc, problems = build(root=ROOT)
    problems = problems + face_problems(doc)
    if problems:
        say("PROBLEMS: " + "; ".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))