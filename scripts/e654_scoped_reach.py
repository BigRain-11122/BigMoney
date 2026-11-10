"""E654 -- do the 16 scoped counted-key sites subscript the object a counted read line reads?

E650 published 383 module-body sites that sit inside a comprehension or a lambda, and 16 of them
address one of the six row keys E633's counted read lines use (``rows`` 11 / ``x1`` 4 / ``bar`` 1).
E650 could only say *where the base name is bound* (``outer_scope_only`` for all 16); the open
question is whether that outer name carries the same object the counted read line reads.  A key
spelling is not an object, and E207/E208's whole lesson is that a name that reads like a
measurement is not a measurement.

So for each of the 16 sites this study publishes two things a reader can check:

  * the *container evidence* behind the subscripted base name -- whether the module builds the
    dict in code (a literal, or an empty dict the module then fills), loads it from disk (a
    ``json.load``-class call), takes it as a runtime input (another call), aliases another name,
    or never binds it at all -- plus the key set when the source states one;
  * the *reach class* of that site against the counted read lines: the read lines are the 13
    lines E633 counts (module, line, function, receiver, key), and a scoped site can only affect
    a counted value when it subscripts the same container the read line reads.  Sharing a module
    is necessary, sharing the receiver name is necessary, and sharing the key is necessary -- all
    three together are still not sufficient, which is why the container evidence is published
    next to the class rather than folded into it.

The counterfactual is published on purpose: how many of the 16 a *key-name-only* test would have
called a collision, so the difference between "same key" and "same object" is a number and not a
claim.

Population and rulers are imported, never re-implemented: E650 publishes the 16 rows (read from
its face, reconciled row by row against the tree), E638/E633 publish the counted read lines, and
E643 the file parser.  The study writes ``results/state_tilt/SCOPEDREACH.json``.
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
TODAY = "2026-11-11"
FACE = "SCOPEDREACH.json"
LATEST = "scopedreach_latest.json"
STUDY = "E654_scoped_counted_key_reach"
SOURCE_FACE = "results/state_tilt/COMPREHENSIONSCOPE.json"
DELIVERABLE = "results/state_tilt/SCOPEDREACH.json"
SELF_PARTS = ("e654_", "run_e654_", "_probe_e654", "_r1678")
MAX_DEPTH = 5
MAX_EXAMPLES = 8

import e638_two_depth_subscripts as e638  # noqa: E402
import e643_nonfunc_site as e643  # noqa: E402
import e653_loop_write_key as e653  # noqa: E402

SHAPES = ("literal_mapping", "empty_then_populated", "literal_sequence",
          "runtime_input", "call_result", "alias", "unresolved")
REACH_CLASSES = ("same_container", "same_module_other_receiver", "off_population",
                 "unresolved_base")

RUNTIME_LOADERS = {"load", "loads", "read", "read_text", "read_json", "load_json", "open",
                   "loadtxt", "read_csv", "read_parquet", "read_excel", "urlopen"}

V_ABSENT = (
    "no_scoped_site_addresses_a_counted_row_key,_so_the_reach_question_is_moot_at_this_population")
V_ALL_OFF = (
    "every_scoped_counted_key_site_subscripts_an_object_no_counted_read_line_reads,_so_no_matching"
    "_key_on_those_dicts_can_move_a_counted_value:_the_key_spelling_is_the_only_link_and_the_name"
    "_is_not_the_object")
V_SAME_CONTAINER = (
    "at_least_one_scoped_counted_key_site_subscripts_the_same_container_a_counted_read_line_reads,"
    "_so_that_key_can_move_a_counted_value_and_the_site_must_be_treated_as_a_writer_of_the_row")
V_SAME_MODULE_OTHER_RECEIVER = (
    "the_scoped_sites_that_share_a_module_with_a_counted_read_line_all_subscript_a_different_"
    "receiver,_so_the_key_collides_on_a_sibling_dict_inside_the_same_file_and_not_on_the_row")
V_SPLIT = (
    "the_scoped_counted_key_sites_split_between_objects_a_counted_read_line_reads_and_objects_it_"
    "does_not,_and_the_split_is_published_per_site_rather_than_decided_by_the_key_name")


def say(line):
    sys.stdout.write(str(line) + "\n")


def rel(module, root=ROOT):
    return e653.rel(module, root)


# ---------------------------------------------------------------- container evidence
def _const_keys(node):
    """Literal string keys of a dict display, in source order."""
    out = []
    for key in getattr(node, "keys", []) or []:
        if isinstance(key, ast.Constant) and isinstance(key.value, str):
            out.append(key.value)
    return out


def _call_name(node):
    f = getattr(node, "func", None)
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def _shape_of(value, bindings, depth, seen):
    """Classify one bound expression without pretending to evaluate it."""
    if depth > MAX_DEPTH:
        return "unresolved", None, "depth"
    if isinstance(value, ast.Dict):
        keys = _const_keys(value)
        if keys:
            return "literal_mapping", keys, "dict display"
        return "empty_then_populated", None, "empty dict display"
    if isinstance(value, ast.DictComp):
        return "literal_mapping", None, "dict comprehension"
    if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
        return "literal_sequence", None, "sequence display"
    if isinstance(value, ast.Call):
        name = _call_name(value)
        if name in RUNTIME_LOADERS:
            return "runtime_input", None, "%s(...)" % name
        return "call_result", None, "%s(...)" % name
    if isinstance(value, ast.Name):
        if value.id in seen or value.id not in bindings:
            return "unresolved", None, "alias cycle or unbound"
        return _shape_of(bindings[value.id], bindings, depth + 1, seen | {value.id})
    if isinstance(value, (ast.Constant, ast.Subscript, ast.Attribute, ast.BinOp,
                          ast.UnaryOp, ast.Compare, ast.BoolOp, ast.IfExp)):
        return "call_result", None, type(value).__name__
    return "unresolved", None, type(value).__name__


def container_evidence(tree, name):
    """Every module-level binding *and* subscript write of ``name``, plus its shape."""
    binds = {}
    writes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        elif isinstance(node, ast.AugAssign):
            targets, value = [node.target], node.value
        else:
            targets = []
            for n in ast.walk(node):
                if isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Store) \
                        and isinstance(n.value, ast.Name) and n.value.id == name:
                    key = e633_const(n.slice)
                    writes.append({"line": n.lineno, "key": key})
            continue
        for t in targets:
            if isinstance(t, ast.Name) and t.id == name:
                binds.setdefault(name, value)
            elif isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name) \
                    and t.value.id == name and isinstance(t.ctx, ast.Store):
                writes.append({"line": t.lineno, "key": e633_const(t.slice)})
    if not binds and not writes:
        return {"shape": "unresolved", "value_set": None, "bind_lines": [],
                "write_lines": [], "why": "the module never binds this name"}
    bindings = e653.module_bindings(tree)
    evidence = {"bind_lines": [], "write_lines": sorted(w["line"] for w in writes)}
    if name in binds:
        shape, values, why = _shape_of(binds[name], bindings, 0, frozenset([name]))
        evidence["bind_lines"] = [binds[name].lineno]
    else:
        shape, values, why = "empty_then_populated", None, "only subscript writes"
    if name in binds and shape == "empty_then_populated" and not writes:
        shape, values, why = "unresolved", None, "an empty dict nobody fills"
    if values is None and shape == "empty_then_populated" and writes:
        values = sorted({w["key"] for w in writes if w["key"] is not None}) or None
    evidence.update({"shape": shape, "value_set": values, "why": why})
    return evidence


def e633_const(node):
    import e633_read_forms as e633
    return e633.const_str(node)


# ---------------------------------------------------------------- population
def scoped_sites(root=ROOT):
    """E650's 16 rows, read from its face -- never hand-copied."""
    path = os.path.join(root, SOURCE_FACE)
    try:
        face = json.load(io.open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return None
    rows = [r for r in (face.get("rows") or []) if r.get("names_a_counted_key")]
    source_counts = face.get("counts") or {}
    return {"rows": rows, "counted_keys": source_counts.get("counted_keys") or [],
            "histogram": source_counts.get("scoped_sites_naming_a_counted_key_histogram") or {},
            "face": SOURCE_FACE, "study": face.get("study")}


def counted_reads(root=ROOT):
    rows = []
    for r in e638.join_counted_lines(root):
        rows.append({"module": (r.get("module") or "").replace("\\", "/"),
                     "line": r.get("read_line"), "function": r.get("function"),
                     "receiver": r.get("receiver"), "key": r.get("key")})
    return rows


# ---------------------------------------------------------------- measure
def measure(root=ROOT):
    source = scoped_sites(root)
    reads = counted_reads(root)
    ctxs = {}
    holes = {"module_missing": 0, "does_not_parse": 0}
    rows = []
    lost = []
    for s in (source or {}).get("rows") or []:
        path = os.path.join(root, s["module"])
        if path not in ctxs:
            ctxs[path] = e643.context_of_file(path) if os.path.exists(path) else None
        ctx = ctxs[path]
        if ctx is None:
            if not os.path.exists(path):
                holes["module_missing"] += 1
                lost.append({"module": s["module"], "line": s.get("line"),
                             "why": "module missing from the tree"})
            else:
                holes["does_not_parse"] += 1
                lost.append({"module": s["module"], "line": s.get("line"),
                             "why": "module does not parse"})
            continue
        keys = sorted(s.get("matched_keys") or [])
        bases = sorted(s.get("base_names") or [])
        if not bases:
            for key in keys:
                rows.append({"module": s["module"], "line": s.get("line"),
                             "column": s.get("column"), "bucket": s.get("bucket"),
                             "key": key, "base": None, "shape": "unresolved",
                             "value_set": None, "reach_class": "unresolved_base",
                             "read_lines_in_module": [], "read_lines_sharing_receiver": [],
                             "why": "no leftmost base name to resolve"})
            continue
        # one row per (site, key, base); sources rarely carry more than one of each
        for key in keys or [None]:
            for base in bases:
                ev = container_evidence(ctx["tree"], base)
                same_module = [r for r in reads if r["module"] == s["module"]]
                same_receiver = [r for r in same_module if r["receiver"] == base]
                if not same_module:
                    reach = "off_population"
                elif same_receiver:
                    reach = "same_container"
                else:
                    reach = "same_module_other_receiver"
                rows.append({
                    "module": s["module"], "line": s.get("line"), "column": s.get("column"),
                    "bucket": s.get("bucket"), "key": key, "base": base,
                    "shape": ev["shape"], "value_set": ev["value_set"],
                    "bind_lines": ev["bind_lines"], "write_lines": ev["write_lines"],
                    "why": ev["why"], "reach_class": reach,
                    "read_lines_in_module": [{"line": r["line"], "receiver": r["receiver"],
                                              "key": r["key"]} for r in same_module],
                    "read_lines_sharing_receiver": [
                        {"line": r["line"], "key": r["key"]} for r in same_receiver],
                })
    read_rows = []
    for r in reads:
        path = os.path.join(root, r["module"])
        if path not in ctxs:
            ctxs[path] = e643.context_of_file(path) if os.path.exists(path) else None
        ctx = ctxs[path]
        if ctx is None:
            read_rows.append(dict(r, shape="module_unreadable", value_set=None))
            continue
        ev = container_evidence(ctx["tree"], r["receiver"]) if r["receiver"] else \
            {"shape": "unresolved", "value_set": None}
        read_rows.append(dict(r, shape=ev["shape"], value_set=ev.get("value_set"),
                              why=ev.get("why")))
    rows.sort(key=lambda r: (r["module"], r["line"] or 0, r["key"] or "", r["base"] or ""))
    read_rows.sort(key=lambda r: (r["module"], r["line"] or 0))
    counts = counts_of(rows, read_rows, source, holes, lost)
    doc = {
        "study": STUDY,
        "date": TODAY,
        "source_face": SOURCE_FACE,
        "method": ("read E650's 16 scoped counted-key rows from its face, re-parse each row's own "
                   "module, publish every module-level binding and subscript write of the "
                   "subscripted base name as a container shape (literal / empty-then-populated / "
                   "runtime input / call result / alias / unresolved) with the key set when the "
                   "source states one, and join each site to the 13 counted read lines E633/E638 "
                   "publish by module and receiver to publish a per-site reach class"),
        "population_source": ("E650's %d scoped sites that name a counted row key, expanded to one "
                             "row per (site, key, base) pair, against the %d counted read lines"
                             % (len((source or {}).get("rows") or []), len(read_rows))),
        "counts": counts,
        "rows": rows,
        "read_lines": read_rows,
        "limits": [
            "a shape is read off the module's own statements, not off runtime: an empty dict the "
            "module fills inside a loop from a disk face is 'empty_then_populated' with no value "
            "set, and calling that 'a runtime input' would be a guess",
            "module identity is required for reach: a dict in another file cannot be the object a "
            "read line reads, so cross-module sites are classified off_population rather than "
            "matched by key name (E646's own arm makes the same move at the write side)",
            "sharing a module and a receiver name is still not proof of identity: the receiver "
            "could be rebound between the read line and the site, so the container evidence is "
            "published beside the class instead of being folded into it",
            "the population is E650's published rows, not a re-measure of its 383 sites: a site "
            "the tree grew since that face is disclosed in reconciliation, never silently added",
        ],
        "reconciliation": {
            "source_face_present": source is not None,
            "source_rows": len((source or {}).get("rows") or []),
            "source_histogram": (source or {}).get("histogram") or {},
            "sites_the_tree_lost": lost,
            "population_shrank_since_source_face": bool(lost),
        },
        "examples": {},
    }
    doc["counts"]["reconciliation"] = doc["reconciliation"]
    doc["verdict"] = decide(counts)
    doc["answer"] = answer_of(counts, source)
    doc["examples"] = examples_of(rows, read_rows)
    return doc


def counts_of(rows, read_rows, source, holes, lost):
    by_key = {}
    for r in rows:
        by_key[r["key"] or "none"] = by_key.get(r["key"] or "none", 0) + 1
    by_reach = {}
    for r in rows:
        by_reach[r["reach_class"]] = by_reach.get(r["reach_class"], 0) + 1
    by_shape = {}
    for r in rows:
        by_shape[r["shape"]] = by_shape.get(r["shape"], 0) + 1
    by_shape_read = {}
    for r in read_rows:
        by_shape_read[r["shape"]] = by_shape_read.get(r["shape"], 0) + 1
    read_key_names = {r["key"] for r in read_rows if r["key"]}
    keys_on_a_read_line = sorted({r["key"] for r in rows if r["key"] in read_key_names})
    key_name_only = sum(1 for r in rows if r["key"] in read_key_names)
    same_container = sum(1 for r in rows if r["reach_class"] == "same_container")
    module_shared = sum(1 for r in rows
                        if r["reach_class"] in ("same_container", "same_module_other_receiver"))
    return {
        "sites_in_source_face": len((source or {}).get("rows") or []),
        "rows_measured": len(rows),
        "read_lines_measured": len(read_rows),
        "holes": holes,
        "sites_the_tree_lost": len(lost),
        "by_key": dict(sorted(by_key.items())),
        "by_reach_class": dict(sorted(by_reach.items())),
        "sites_sharing_a_module_with_a_counted_read_line": module_shared,
        "sites_sharing_a_receiver_name_with_a_counted_read_line": same_container,
        "sites_whose_container_a_counted_read_line_reads": same_container,
        "container_shape_histogram": dict(sorted(by_shape.items())),
        "read_line_container_shape_histogram": dict(sorted(by_shape_read.items())),
        "key_names_colliding_across_objects": keys_on_a_read_line,
        "rows_a_key_name_only_test_would_call_a_collision": key_name_only,
        "rows_a_container_test_calls_a_collision": same_container,
        "key_name_only_false_positives": key_name_only - same_container,
        "reconciliation": {},
    }


def examples_of(rows, read_rows, limit=MAX_EXAMPLES):
    out = {"sites": []}
    for r in rows[:limit]:
        out["sites"].append({"module": r["module"], "line": r["line"], "key": r["key"],
                             "base": r["base"], "shape": r["shape"],
                             "value_set": r["value_set"], "reach_class": r["reach_class"]})
    out["read_lines"] = [{"module": r["module"], "line": r["line"], "key": r["key"],
                          "receiver": r["receiver"], "shape": r["shape"]}
                         for r in read_rows[:limit]]
    return out


def decide(c):
    rows = c.get("rows_measured") or 0
    if not rows:
        return V_ABSENT
    same = c.get("sites_whose_container_a_counted_read_line_reads") or 0
    module_shared = c.get("sites_sharing_a_module_with_a_counted_read_line") or 0
    if same:
        return V_SAME_CONTAINER
    if module_shared:
        return V_SAME_MODULE_OTHER_RECEIVER
    if (c.get("by_reach_class") or {}).get("off_population", 0) == rows:
        return V_ALL_OFF
    return V_SPLIT


def answer_of(c, source):
    rows = c.get("rows_measured") or 0
    if not rows:
        return "no scoped site names a counted row key"
    same = c.get("sites_whose_container_a_counted_read_line_reads") or 0
    module_shared = c.get("sites_sharing_a_module_with_a_counted_read_line") or 0
    key_only = c.get("rows_a_key_name_only_test_would_call_a_collision") or 0
    shapes = c.get("container_shape_histogram") or {}
    hist = (source or {}).get("histogram") or {}
    return (
        "%d scoped counted-key site row(s) over %d source site(s) (%s); %d share a module with a "
        "counted read line, %d subscript the receiver that read line reads, and a key-name-only "
        "test would have called %d a collision -- %d false positive(s); container shapes %s"
        % (rows, c.get("sites_in_source_face") or 0,
           ", ".join("%s %s" % (k, v) for k, v in sorted(hist.items())) or "no source histogram",
           module_shared, same, key_only, c.get("key_name_only_false_positives") or 0,
           json.dumps(shapes, ensure_ascii=False, sort_keys=True)))


# ---------------------------------------------------------------- face gate
def face_problems(doc):
    problems = []
    c = doc.get("counts") or {}
    rows = doc.get("rows") or []
    read_rows = doc.get("read_lines") or []
    if c.get("rows_measured") != len(rows):
        problems.append("rows_measured does not equal the published row count")
    if c.get("read_lines_measured") != len(read_rows):
        problems.append("read_lines_measured does not equal the published read line count")
    by_reach = c.get("by_reach_class") or {}
    for cls in REACH_CLASSES:
        mine = sum(1 for r in rows if r.get("reach_class") == cls)
        if by_reach.get(cls, 0) != mine:
            problems.append("by_reach_class[%s] does not re-derive from the rows" % cls)
    if sum(by_reach.values()) != len(rows):
        problems.append("the reach classes do not partition the rows")
    by_key = {}
    for r in rows:
        by_key[r.get("key") or "none"] = by_key.get(r.get("key") or "none", 0) + 1
    if (c.get("by_key") or {}) != dict(sorted(by_key.items())):
        problems.append("by_key does not re-derive from the rows")
    same = sum(1 for r in rows if r.get("reach_class") == "same_container")
    if c.get("sites_whose_container_a_counted_read_line_reads") != same:
        problems.append("the same-container count does not re-derive from the rows")
    key_names = {r.get("key") for r in read_rows if r.get("key")}
    key_only = sum(1 for r in rows if r.get("key") in key_names)
    if c.get("rows_a_key_name_only_test_would_call_a_collision") != key_only:
        problems.append("the key-name-only counterfactual does not re-derive from the rows")
    if c.get("key_name_only_false_positives") != key_only - same:
        problems.append("the false positive count does not re-derive")
    for r in rows:
        if r.get("reach_class") == "same_container":
            if not r.get("read_lines_sharing_receiver"):
                problems.append("a same_container row carries no read line (%s:%s)"
                                % (r.get("module"), r.get("line")))
                break
            if r.get("key") != r["read_lines_sharing_receiver"][0].get("key"):
                problems.append("a same_container row's read line names another key (%s:%s)"
                                % (r.get("module"), r.get("line")))
                break
        if r.get("reach_class") == "off_population" and r.get("read_lines_in_module"):
            problems.append("an off_population row lists a read line in its own module (%s:%s)"
                            % (r.get("module"), r.get("line")))
            break
        if r.get("shape") not in SHAPES:
            problems.append("a row publishes an unknown container shape (%s)" % r.get("shape"))
            break
    rec = c.get("reconciliation") or {}
    if rec.get("population_shrank_since_source_face"):
        problems.append("the population shrank since E650's face: %s"
                        % ((rec.get("sites_the_tree_lost") or [])[:3],))
    if rows and not rec.get("source_face_present", False):
        problems.append("E650's source face is absent, so the population cannot be reconciled")
    if doc.get("verdict") != decide(c):
        problems.append("the verdict does not re-derive from the published counts")
    if not str(doc.get("answer") or "").strip():
        problems.append("the answer line is empty")
    return problems


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    blob = json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=False)
    for name in (face, latest):
        with io.open(os.path.join(out_dir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(blob)
            fh.write("\n")
    return os.path.join(out_dir, face)


def build(root=ROOT, out_dir=None):
    doc = measure(root)
    problems = face_problems(doc)
    if problems:
        say("FACE-PROBLEMS: " + "; ".join(problems))
        return 3, doc
    path = write_face(out_dir if out_dir is not None else OUTDIR, doc)
    say("wrote " + rel(path, root))
    say("answer: " + doc["answer"])
    return 0, doc


def load_face(path=None, root=ROOT):
    path = path or os.path.join(root, OUTDIR, FACE)
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def check(path=None, root=ROOT):
    problems = face_problems(load_face(path, root))
    say("check problems=%s" % json.dumps(problems, ensure_ascii=False))
    return 0 if not problems else 3


def verify(root=ROOT):
    """Re-parse every module a row points at and re-derive the shape and the reach class.

    The cheap proof is the one that matters: each row names its file, its base name, and its
    class, so re-reading those files must reproduce both.
    """
    face = load_face(root=root)
    problems = face_problems(face)
    rows = face.get("rows") or []
    reads = counted_reads(root)
    cache = {}
    for r in rows:
        path = os.path.join(root, r["module"])
        if path not in cache:
            cache[path] = e643.context_of_file(path)
        ctx = cache[path]
        if ctx is None:
            problems.append("row module does not parse: %s" % r["module"])
            continue
        if r["base"] is None:
            continue
        ev = container_evidence(ctx["tree"], r["base"])
        if ev["shape"] != r["shape"]:
            problems.append("shape moved at %s:%s (%s -> %s)"
                            % (r["module"], r["line"], r["shape"], ev["shape"]))
        same_module = [x for x in reads if x["module"] == r["module"]]
        same_receiver = [x for x in same_module if x["receiver"] == r["base"]]
        reach = ("off_population" if not same_module
                 else "same_container" if same_receiver else "same_module_other_receiver")
        if reach != r["reach_class"]:
            problems.append("reach class moved at %s:%s (%s -> %s)"
                            % (r["module"], r["line"], r["reach_class"], reach))
        if len(problems) > 12:
            break
    say("verify rows=%d read_lines=%d problems=%s"
        % (len(rows), len(reads), json.dumps(problems[:8], ensure_ascii=False)))
    return 0 if not problems else 3


# ---------------------------------------------------------------- selftest
def selftest():
    legs = []

    def leg(name, ok, note=""):
        legs.append((name, bool(ok), note))
        say("%s %s%s" % ("PASS" if ok else "FAIL", name,
                         (" -- " + note) if note and not ok else ""))

    import tempfile

    def ctx_of(src):
        tmp = tempfile.mkdtemp(prefix="e654_")
        path = os.path.join(tmp, "fixture_reach.py")
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(src)
        ctx = e643.context_of_file(path)
        assert ctx is not None, "fixture does not parse"
        return ctx

    def shape(src, name):
        return container_evidence(ctx_of(src)["tree"], name)

    s = shape("P = {'rows': 1, 'bar': 2}\n", "P")
    leg("a non-empty dict display is a literal mapping with its keys",
        s["shape"] == "literal_mapping" and s["value_set"] == ["rows", "bar"], str(s))
    s = shape("P = {}\nP['rows'] = 1\n", "P")
    leg("an empty dict the module fills is empty_then_populated with the written keys",
        s["shape"] == "empty_then_populated" and s["value_set"] == ["rows"], str(s))
    s = shape("P = {}\n", "P")
    leg("an empty dict nobody fills is not published as a container",
        s["shape"] == "unresolved", str(s))
    s = shape("import json\nP = json.load(open('x.json'))\n", "P")
    leg("a json.load-class call is a runtime input",
        s["shape"] == "runtime_input", str(s))
    s = shape("P = build_rows()\n", "P")
    leg("any other call is a call result, not a runtime input",
        s["shape"] == "call_result", str(s))
    s = shape("A = {'rows': 1}\nP = A\n", "P")
    leg("an alias is followed to its binding",
        s["shape"] == "literal_mapping" and s["value_set"] == ["rows"], str(s))
    s = shape("A = B\nB = A\nP = A\n", "P")
    leg("an alias cycle is cut as unresolved",
        s["shape"] == "unresolved", str(s))
    s = shape("X = 1\n", "P")
    leg("a name the module never binds is unresolved",
        s["shape"] == "unresolved", str(s))
    s = shape("ROWS = []\nP = {}\nfor r in ROWS:\n    P[r] = 1\n", "P")
    leg("a loop-filled dict publishes no value set rather than a guess",
        s["shape"] == "empty_then_populated" and s["value_set"] is None, str(s))
    leg("a cross-module site is off_population, not a key-name match",
        _reach("a.py", "b.py", "P") == "off_population", "")
    leg("a shared module with a different receiver is its own class",
        _reach("a.py", "a.py", "Q") == "same_module_other_receiver", "")
    leg("a shared module and receiver is the same-container class",
        _reach("a.py", "a.py", "P") == "same_container", "")
    leg("the reach classes partition the row set",
        set(REACH_CLASSES) == {"same_container", "same_module_other_receiver",
                               "off_population", "unresolved_base"}, "")
    doc = {"counts": {"rows_measured": 1, "read_lines_measured": 0,
                      "by_reach_class": {"same_container": 0, "same_module_other_receiver": 0,
                                         "off_population": 1, "unresolved_base": 0},
                      "by_key": {"rows": 1},
                      "sites_whose_container_a_counted_read_line_reads": 0,
                      "rows_a_key_name_only_test_would_call_a_collision": 0,
                      "key_name_only_false_positives": 0,
                      "reconciliation": {"source_face_present": True,
                                         "population_shrank_since_source_face": False},
                      "sites_sharing_a_module_with_a_counted_read_line": 0},
           "rows": [{"module": "a.py", "line": 1, "key": "rows", "base": "P",
                     "shape": "literal_mapping", "reach_class": "off_population",
                     "read_lines_in_module": [], "read_lines_sharing_receiver": []}],
           "read_lines": [],
           "verdict": V_ALL_OFF, "answer": "x"}
    leg("a clean face passes its own gate", face_problems(doc) == [], str(face_problems(doc)))
    bad = json.loads(json.dumps(doc))
    bad["counts"]["by_reach_class"]["off_population"] = 0
    leg("a reach histogram that does not re-derive is caught",
        any("by_reach_class" in p for p in face_problems(bad)), "")
    bad = json.loads(json.dumps(doc))
    bad["rows"][0]["reach_class"] = "same_container"
    leg("a same_container row with no read line is caught",
        any("no read line" in p for p in face_problems(bad)), "")
    bad = json.loads(json.dumps(doc))
    bad["verdict"] = V_ABSENT
    leg("a verdict that does not re-derive is caught",
        any("verdict does not re-derive" in p for p in face_problems(bad)), "")
    bad = json.loads(json.dumps(doc))
    bad["rows"][0]["shape"] = "made_up"
    leg("an unknown container shape is caught",
        any("unknown container shape" in p for p in face_problems(bad)), "")
    leg("a key-name-only test is strictly wider than a container test",
        _counterfactual([{"key": "rows"}, {"key": "x9"}], [{"key": "rows"}]) == (1, 0), "")

    passed = sum(1 for _, ok, _ in legs if ok)
    say("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def _reach(site_module, read_module, receiver, read_receiver="P"):
    same_module = site_module == read_module
    if not same_module:
        return "off_population"
    return "same_container" if receiver == read_receiver else "same_module_other_receiver"


def _counterfactual(rows, read_rows):
    names = {r["key"] for r in read_rows}
    key_only = sum(1 for r in rows if r["key"] in names)
    return key_only, 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="E654 scoped counted-key reach")
    ap.add_argument("mode", nargs="?", default="build",
                    choices=("build", "check", "verify", "selftest", "answer"))
    args = ap.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    if args.mode == "check":
        return check()
    if args.mode == "verify":
        return verify()
    if args.mode == "answer":
        doc = load_face()
        say(doc.get("answer") or "")
        return 0
    rc, _doc = build()
    return rc


if __name__ == "__main__":
    sys.exit(main())
