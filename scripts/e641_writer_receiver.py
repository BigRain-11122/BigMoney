"""E641 -- inside a counted function, what binds the container each two-depth write writes through?

E640 priced the write population inside E633's six counted functions: 10 write sites, none of
them naming the row's counted key.  That left the interesting half unanswered: a write of a
*different* key can still be a write into the same object the read line reads -- if the write
goes through the container the read uses, then "this line reads k twice" stands next to a write
of that mapping and the read is no longer the only access to it.

For every two-depth write site E640 attributes to a counted function this study:

  * resolves the site to its outermost Subscript node and walks the ``.value`` chain down to the
    root Name -- that Name is the container the write goes through,
  * resolves that Name inside the function: a parameter, a loop target, a local assignment (and,
    for a local, the kind of expression it is bound to), or module scope,
  * publishes whether the container is the *same name* as a receiver a counted read line in that
    same function reads, which is the only way this population can reach the counted key.

The population (which functions are counted, which sites are writes) is machine-read from E640's
face; nothing here re-defines "counted line" or "two-depth write site".
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
FACE = "WRITERBINDING.json"
LATEST = "writerbinding_latest.json"
STUDY = "E641_writer_receiver_binding"
SELF_PARTS = ("e641_", "run_e641_", "_probe_e641", "_r1661")
SOURCE_FACE = "results/state_tilt/WRITEREADCOLLIDE.json"

import e638_two_depth_subscripts as e638  # noqa: E402
import e640_writeread_collide as e640  # noqa: E402

BINDINGS = ("parameter", "loop_target", "local_assignment", "module_scope", "unresolved")
OUTSIDE = ("parameter", "module_scope")

V_SHARES_THE_READERS_CONTAINER = (
    "at_least_one_counted_function_writes_through_the_same_container_name_a_counted_read_line_"
    "reads,_so_a_write_of_another_key_can_land_in_the_mapping_that_read_depends_on")
V_BOUND_OUTSIDE_ONLY = (
    "every_two_depth_write_site_in_the_counted_functions_writes_through_a_container_bound_from_"
    "outside_the_function_(parameter_or_module_scope),_but_no_whose_name_is_a_counted_read_"
    "receiver,_so_the_writes_cannot_reach_the_counted_keys_these_lines_read")
V_LOCAL_ONLY = (
    "the_counted_functions'_two_depth_writes_go_through_containers_bound_inside_the_function,_"
    "so_they_are_local_to_that_function_and_cannot_alias_a_caller's_mapping")
V_NO_WRITE_SITES = (
    "no_counted_function_carries_a_two_depth_write_site_in_this_population,_so_there_is_no_"
    "container_to_bind_and_the_write_side_is_empty_by_measurement")
V_UNRESOLVED = (
    "the_counted_functions_carry_two_depth_write_sites_but_their_containers_cannot_be_resolved_"
    "to_a_binding_in_this_population,_so_no_reachability_claim_is_made")


def say(line):
    sys.stdout.write(line + "\n")


def rel(module, root=ROOT):
    return os.path.relpath(module, root).replace("\\", "/")


# ---------------------------------------------------------------- ast helpers
def find_node(tree, line, column):
    """The Subscript node starting at (line, column) with the greatest depth."""
    best = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Subscript):
            continue
        if node.lineno != line or node.col_offset != column:
            continue
        if best is None or e638.subscript_depth(node) > e638.subscript_depth(best):
            best = node
    return best


def container_chain(node):
    """Root Name plus the attribute/subscript steps walked from the outermost Subscript."""
    chain = []
    cur = node.value if isinstance(node, ast.Subscript) else node
    while True:
        if isinstance(cur, ast.Subscript):
            chain.append("[]")
            cur = cur.value
        elif isinstance(cur, ast.Attribute):
            chain.append("." + cur.attr)
            cur = cur.value
        elif isinstance(cur, ast.Call):
            chain.append("()")
            cur = cur.func
        else:
            break
    chain.reverse()
    name = cur.id if isinstance(cur, ast.Name) else None
    return name, chain


def function_node(tree, span):
    """The FunctionDef whose lineno/name match the published span."""
    want = span["qualname"].split(".")[-1]
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                and node.name == want and node.lineno == span["start"]:
            return node
    return None


def _param_names(fn):
    a = fn.args
    out = [p.arg for p in list(getattr(a, "posonlyargs", [])) + list(a.args)]
    out += [p.arg for p in a.kwonlyargs]
    if a.vararg:
        out.append(a.vararg.arg)
    if a.kwarg:
        out.append(a.kwarg.arg)
    return out


def _scope_nodes(fn):
    """Every node lexically inside ``fn``, not descending into nested defs/classes/lambdas."""
    stack = list(ast.iter_child_nodes(fn))
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        yield node
        stack.extend(ast.iter_child_nodes(node))


def _target_names(target):
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        out = []
        for elt in target.elts:
            out.extend(_target_names(elt))
        return out
    return []


def _rhs_kind(value):
    if isinstance(value, ast.Dict):
        return "dict_literal"
    if isinstance(value, ast.Call):
        return "call"
    if isinstance(value, ast.Subscript):
        return "subscript"
    if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
        return "sequence_literal"
    if isinstance(value, ast.Constant):
        return "constant"
    return "other"


def _assign_pairs(target, value):
    """(name, rhs_kind) pairs for one assignment target/value, pairing tuple elements positionally.

    ``numbers, verdicts = {}, {}`` binds *numbers* to a dict literal; reading the kind off the
    value node alone says "sequence_literal" and describes the tuple, not the container.  When the
    shapes match, the element's own kind is the honest one; when they do not, the fallback is the
    whole value's kind and that is published as-is.
    """
    names = _target_names(target)
    if isinstance(target, (ast.Tuple, ast.List)) and isinstance(value, (ast.Tuple, ast.List)) \
            and len(target.elts) == len(value.elts) == len(names):
        return [(name, _rhs_kind(elt)) for name, elt in zip(names, value.elts)]
    return [(name, _rhs_kind(value)) for name in names]


def binding_index(fn, tree):
    """name -> {binding, line, rhs_kind} resolved inside the function, module scope as fallback."""
    index = {}
    for name in _param_names(fn):
        index[name] = {"binding": "parameter", "line": fn.lineno, "rhs_kind": None}
    for node in _scope_nodes(fn):
        if isinstance(node, (ast.For, ast.AsyncFor)):
            for name in _target_names(node.target):
                index.setdefault(name, {"binding": "loop_target",
                                        "line": getattr(node, "lineno", None),
                                        "rhs_kind": None})
        elif isinstance(node, (ast.comprehension,)):
            for name in _target_names(node.target):
                index.setdefault(name, {"binding": "loop_target",
                                        "line": getattr(node, "lineno", None),
                                        "rhs_kind": None})
        elif isinstance(node, ast.Assign):
            for tgt in node.targets:
                for name, kind in _assign_pairs(tgt, node.value):
                    index.setdefault(name, {"binding": "local_assignment",
                                            "line": getattr(node, "lineno", None),
                                            "rhs_kind": kind})
        elif isinstance(node, ast.AnnAssign):
            for name in _target_names(node.target):
                index.setdefault(name, {"binding": "local_assignment",
                                        "line": getattr(node, "lineno", None),
                                        "rhs_kind": _rhs_kind(node.value) if node.value else None})
        elif isinstance(node, ast.AugAssign):
            for name in _target_names(node.target):
                index.setdefault(name, {"binding": "local_assignment",
                                        "line": getattr(node, "lineno", None),
                                        "rhs_kind": "augmented"})
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = []
            for alias in node.names:
                names.append((alias.asname or alias.name).split(".")[0])
            for name in names:
                index.setdefault(name, {"binding": "module_scope",
                                        "line": getattr(node, "lineno", None),
                                        "rhs_kind": "import"})
        elif isinstance(node, ast.Assign):
            for tgt in node.targets:
                for name in _target_names(tgt):
                    index.setdefault(name, {"binding": "module_scope",
                                            "line": getattr(node, "lineno", None),
                                            "rhs_kind": _rhs_kind(node.value)})
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            index.setdefault(node.name, {"binding": "module_scope",
                                         "line": getattr(node, "lineno", None),
                                         "rhs_kind": "definition"})
    return index


def read_receivers(rows, module, qualname):
    return sorted({r.get("receiver") for r in rows
                   if r.get("module") == module
                   and (r.get("function_span") or {}).get("qualname") == qualname
                   and r.get("receiver")})


# ---------------------------------------------------------------- measure
def load_source(root=ROOT):
    path = os.path.join(root, SOURCE_FACE)
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def measure(root=ROOT):
    src = load_source(root)
    rows = src.get("rows") or []
    functions = src.get("counted_functions") or []
    out = []
    for fn in functions:
        module = fn.get("module")
        span = {"qualname": fn.get("qualname"), "start": fn.get("start"), "end": fn.get("end")}
        path = os.path.join(root, module)
        got, why = e638.file_sites(path)
        receivers = read_receivers(rows, module, span["qualname"])
        entry = {"module": module, "function": span["qualname"],
                 "start": span["start"], "end": span["end"],
                 "read_lines": fn.get("read_lines") or [],
                 "read_receivers": receivers,
                 "sites_in_the_function": fn.get("sites_in_the_function"),
                 "write_sites_in_the_function": fn.get("write_sites_in_the_function"),
                 "write_sites": [], "scope_problem": None}
        if got is None:
            entry["scope_problem"] = why
            out.append(entry)
            continue
        tree = e640.tree_of(path)
        if tree is None:
            entry["scope_problem"] = why or "does_not_parse"
            out.append(entry)
            continue
        fnode = function_node(tree, span)
        if fnode is None:
            entry["scope_problem"] = "function_not_found"
            out.append(entry)
            continue
        index = binding_index(fnode, tree)
        for site in got["sites"]:
            owner = e640.innermost_owner(e640.function_spans(path), site["line"])
            if owner is None or owner["qualname"] != span["qualname"]:
                continue
            row = e640.site_row(site)
            if not row["any_member_is_write"]:
                continue
            node = find_node(tree, site["line"], site["column"])
            if node is None:
                container, chain = None, []
            else:
                container, chain = container_chain(node)
            info = index.get(container) if container else None
            binding = info["binding"] if info else "unresolved"
            entry["write_sites"].append({
                "line": site["line"], "column": site["column"],
                "depth_pair": row["depth_pair"],
                "outer_key": row["outer_key"], "inner_key": row["inner_key"],
                "container": container,
                "container_chain": chain,
                "binding": binding,
                "bound_from_outside_the_function": binding in OUTSIDE,
                "binding_line": info["line"] if info else None,
                "binding_rhs_kind": info["rhs_kind"] if info else None,
                "same_name_as_a_counted_read_receiver": bool(
                    container and container in entry["read_receivers"]),
            })
        entry["write_sites"].sort(key=lambda s: (s["line"], s["column"]))
        out.append(entry)
    out.sort(key=lambda e: (e["module"], e["start"]))
    counts = counts_of(out)
    doc = {
        "study": STUDY,
        "date": TODAY,
        "source_face": SOURCE_FACE,
        "method": ("for every two-depth write site E640 attributes to one of E633's counted "
                   "functions, resolve the outermost Subscript at the site to the root Name its "
                   ".value chain walks through, classify that Name's binding inside the function "
                   "(parameter / loop target / local assignment with its expression kind / module "
                   "scope / unresolved), and publish whether the container is the same name a "
                   "counted read line in that same function reads"),
        "population_source": ("%d counted function(s) machine-read from %s, %d two-depth write "
                              "site(s) among them" % (len(functions), SOURCE_FACE,
                                                      sum(len(f["write_sites"]) for f in out))),
        "counts": counts,
        "functions": out,
        "limits": [
            "the container is the root Name of the site's .value chain; a write whose container is "
            "a call result (f()['a']['b'] = v) resolves to f and is published as such, so an "
            "expression-shaped container is visible in the chain column and never silently called "
            "a name",
            "binding precedence is parameter > loop target > local assignment > module scope > "
            "unresolved; a parameter reassigned inside the function is still published as a "
            "parameter, which is the conservative reading for a reachability claim",
            "'same name as a counted read receiver' is name equality inside one function, not an "
            "alias proof: two parameters with different names can hold one object, and the same "
            "name can be rebound between the write and the read. The face publishes the evidence "
            "for each row rather than a reachability verdict it cannot support",
            "the population of functions and of write sites is E640's, not re-derived here: a "
            "second definition of 'two-depth write site' would be free to drift from the "
            "published one",
        ],
    }
    doc["verdict"] = decide(counts)
    doc["answer"] = answer_of(counts, out)
    return doc


def counts_of(functions):
    sites = [s for f in functions for s in f["write_sites"]]
    hist = {b: 0 for b in BINDINGS}
    for s in sites:
        hist[s["binding"]] = hist.get(s["binding"], 0) + 1
    rhs = {}
    for s in sites:
        key = s["binding_rhs_kind"] or "-"
        rhs[key] = rhs.get(key, 0) + 1
    return {
        "counted_functions": len(functions),
        "counted_functions_with_a_scope_problem": sum(
            1 for f in functions if f.get("scope_problem")),
        "functions_carrying_a_write_site": sum(1 for f in functions if f["write_sites"]),
        "write_sites": len(sites),
        "write_site_container_binding_histogram": dict(sorted(hist.items())),
        "write_site_rhs_kind_histogram": dict(sorted(rhs.items())),
        "write_sites_bound_from_outside_the_function": sum(
            1 for s in sites if s["bound_from_outside_the_function"]),
        "write_sites_bound_inside_the_function": sum(
            1 for s in sites if s["binding"] in ("loop_target", "local_assignment")),
        "write_sites_with_an_unresolved_container": sum(
            1 for s in sites if s["binding"] == "unresolved"),
        "write_sites_without_a_container_name": sum(1 for s in sites if not s["container"]),
        "write_sites_sharing_a_counted_read_receiver_name": sum(
            1 for s in sites if s["same_name_as_a_counted_read_receiver"]),
        "distinct_write_containers": len({s["container"] for s in sites if s["container"]}),
        "functions_whose_writes_share_a_read_receiver_name": sum(
            1 for f in functions
            if any(s["same_name_as_a_counted_read_receiver"] for s in f["write_sites"])),
        "counted_read_receivers": len({r for f in functions for r in f["read_receivers"]}),
        "counted_lines_carried": sum(len(f.get("read_lines") or []) for f in functions),
    }


def decide(c):
    if not c.get("write_sites"):
        return V_NO_WRITE_SITES
    if c.get("write_sites_sharing_a_counted_read_receiver_name"):
        return V_SHARES_THE_READERS_CONTAINER
    if c.get("write_sites_with_an_unresolved_container") == c.get("write_sites"):
        return V_UNRESOLVED
    if c.get("write_sites_bound_from_outside_the_function") == c.get("write_sites"):
        return V_BOUND_OUTSIDE_ONLY
    if c.get("write_sites_bound_inside_the_function") == c.get("write_sites"):
        return V_LOCAL_ONLY
    return V_LOCAL_ONLY if not c.get("write_sites_bound_from_outside_the_function") \
        else V_BOUND_OUTSIDE_ONLY


def answer_of(c, functions):
    parts = []
    for f in functions:
        if not f["write_sites"]:
            continue
        binds = ", ".join("%s:%s" % (s["container"], s["binding"]) for s in f["write_sites"])
        parts.append("%s:%s(%d sites, receivers %s -> %s)"
                     % (f["module"], f["function"], len(f["write_sites"]),
                        ",".join(f["read_receivers"]) or "-", binds))
    return ("%d counted function(s), %d carrying a two-depth write site, %d write site(s) total; "
            "containers bind as %s; %d bound from outside the function, %d inside, %d unresolved, "
            "%d whose container name is a counted read receiver's; read receivers in scope: %d. "
            "%s"
            % (c.get("counted_functions"), c.get("functions_carrying_a_write_site"),
               c.get("write_sites"),
               json.dumps(c.get("write_site_container_binding_histogram") or {}, sort_keys=True),
               c.get("write_sites_bound_from_outside_the_function"),
               c.get("write_sites_bound_inside_the_function"),
               c.get("write_sites_with_an_unresolved_container"),
               c.get("write_sites_sharing_a_counted_read_receiver_name"),
               c.get("counted_read_receivers"),
               " | ".join(parts)))


COUNT_KEYS = (
    "counted_functions", "counted_functions_with_a_scope_problem",
    "functions_carrying_a_write_site", "write_sites",
    "write_site_container_binding_histogram", "write_site_rhs_kind_histogram",
    "write_sites_bound_from_outside_the_function",
    "write_sites_bound_inside_the_function",
    "write_sites_with_an_unresolved_container", "write_sites_without_a_container_name",
    "write_sites_sharing_a_counted_read_receiver_name", "distinct_write_containers",
    "functions_whose_writes_share_a_read_receiver_name", "counted_read_receivers",
    "counted_lines_carried",
)


def face_problems(face):
    problems = []
    if not face:
        return ["face is absent or empty"]
    functions = face.get("functions") or []
    c = face.get("counts") or {}
    live = counts_of(functions)
    for key in COUNT_KEYS:
        if c.get(key) != live.get(key):
            problems.append("counts.%s does not re-add from the functions" % key)
    if decide(live) != face.get("verdict"):
        problems.append("the published verdict is not the one the counts force")
    for f in functions:
        expected = f.get("write_sites_in_the_function")
        if expected is not None and expected != len(f["write_sites"]):
            problems.append("%s:%s carries %d write sites where E640 publishes %d"
                            % (f["module"], f["function"], len(f["write_sites"]), expected))
            break
        for s in f["write_sites"]:
            if not (f["start"] <= s["line"] <= f["end"]):
                problems.append("%s:%s publishes a write outside its own span"
                                % (f["module"], f["function"]))
                break
            if s["binding"] not in BINDINGS:
                problems.append("%s:%s has an unknown binding %r"
                                % (f["module"], f["function"], s["binding"]))
                break
            if s["bound_from_outside_the_function"] != (s["binding"] in OUTSIDE):
                problems.append("%s:%s has an outside flag its binding contradicts"
                                % (f["module"], f["function"]))
                break
            if s["same_name_as_a_counted_read_receiver"] \
                    and s["container"] not in (f.get("read_receivers") or []):
                problems.append("%s:%s claims a shared receiver name it does not carry"
                                % (f["module"], f["function"]))
                break
        if f["write_sites"] and (f.get("write_sites_in_the_function") or 0) == 0:
            problems.append("%s:%s publishes write sites where E640 publishes none"
                            % (f["module"], f["function"]))
            break
    if face.get("verdict") == V_NO_WRITE_SITES and c.get("write_sites", 0):
        problems.append("the verdict says no write site while the face carries them")
    if face.get("verdict") == V_SHARES_THE_READERS_CONTAINER \
            and c.get("write_sites_sharing_a_counted_read_receiver_name", 0) == 0:
        problems.append("the verdict reports a shared container the rows do not carry")
    if face.get("verdict") == V_BOUND_OUTSIDE_ONLY \
            and (c.get("write_sites_bound_from_outside_the_function", 0) != c.get("write_sites")
                 or c.get("write_sites_sharing_a_counted_read_receiver_name", 0)):
        problems.append("the bound-outside verdict is not the one its own totals force")
    return problems


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        path = os.path.join(out_dir, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
        say("run: %s" % os.path.relpath(path, ROOT))


def build(root=ROOT, out_dir=None):
    doc = measure(root)
    write_face(out_dir or OUTDIR, doc)
    c = doc["counts"]
    say("run: functions=%d with_write=%d sites=%d outside=%d inside=%d unresolved=%d shared=%d"
        % (c["counted_functions"], c["functions_carrying_a_write_site"], c["write_sites"],
           c["write_sites_bound_from_outside_the_function"],
           c["write_sites_bound_inside_the_function"],
           c["write_sites_with_an_unresolved_container"],
           c["write_sites_sharing_a_counted_read_receiver_name"]))
    say("run: verdict=" + doc["verdict"])
    say("run: answer=" + doc["answer"])
    return doc, []


def verify(face=None, out_dir=None):
    face = face or json.load(io.open(os.path.join(out_dir or OUTDIR, FACE), encoding="utf-8"))
    return face_problems(face)


# ---------------------------------------------------------------- selftest
FIXTURE_SRC = (
    "def f(P, sleeves, tid, do):\n"
    "    for name in P:\n"
    "        P[name]['x1'] = 1\n"
    "    sleeves[tid]['y'] = 2\n"
    "    local = {}\n"
    "    local['a']['b'] = 3\n"
    "    MOD['c']['d'] = 4\n"
    "    return sleeves[tid]['x1']\n"
)

MODULE_SRC = "MOD = {}\n" + FIXTURE_SRC


def _fixture_measure():
    tree = ast.parse(MODULE_SRC)
    fnode = function_node(tree, {"qualname": "f", "start": 2})
    assert fnode is not None
    index = binding_index(fnode, tree)
    spans = e640.function_spans.__wrapped__ if hasattr(
        e640.function_spans, "__wrapped__") else None
    return tree, fnode, index, spans


def _classify(src, line, column, fn_line=1):
    tree = ast.parse(src)
    fnode = function_node(tree, {"qualname": "f", "start": fn_line})
    assert fnode is not None, "fixture function not found"
    index = binding_index(fnode, tree)
    node = find_node(tree, line, column)
    assert node is not None, "fixture site not found"
    container, chain = container_chain(node)
    info = index.get(container) if container else None
    return container, chain, (info or {}).get("binding", "unresolved"), (info or {})


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

    def a_parameter_container_is_a_parameter():
        c, chain, b, _ = _classify(
            "def f(P):\n    P['a']['b'] = 1\n", 2, 4)
        assert (c, b) == ("P", "parameter"), (c, b)

    def a_loop_target_container_is_a_loop_target():
        c, chain, b, _ = _classify(
            "def f(xs):\n    for P in xs:\n        P['a']['b'] = 1\n", 3, 8)
        assert (c, b) == ("P", "loop_target"), (c, b)

    def a_local_dict_container_is_a_local_assignment():
        c, chain, b, info = _classify(
            "def f():\n    local = {}\n    local['a']['b'] = 1\n", 3, 4)
        assert (c, b) == ("local", "local_assignment"), (c, b)
        assert info["rhs_kind"] == "dict_literal", info

    def a_module_name_container_is_module_scope():
        c, chain, b, _ = _classify(
            "MOD = {}\ndef f():\n    MOD['a']['b'] = 1\n", 3, 4, fn_line=2)
        assert (c, b) == ("MOD", "module_scope"), (c, b)

    def an_imported_container_is_module_scope():
        c, chain, b, info = _classify(
            "import json\ndef f():\n    json['a']['b'] = 1\n", 3, 4, fn_line=2)
        assert b == "module_scope", (c, b, info)
        assert info["rhs_kind"] == "import", info

    def an_unknown_name_is_unresolved():
        c, chain, b, _ = _classify(
            "def f():\n    nosuch['a']['b'] = 1\n", 2, 4)
        assert b == "unresolved", (c, b)

    def the_precedence_puts_the_parameter_first():
        c, chain, b, info = _classify(
            "def f(P):\n    P = {}\n    P['a']['b'] = 1\n", 3, 4)
        assert b == "parameter", (c, b, info)

    def the_chain_carries_the_attribute_steps():
        c, chain, b, _ = _classify(
            "def f(self):\n    self.store['a']['b'] = 1\n", 2, 4)
        assert c == "self", c
        assert ".store" in chain, chain

    def an_augmented_assignment_counts_as_a_local():
        c, chain, b, info = _classify(
            "def f(n):\n    acc = 0\n    acc['a']['b'] = 1\n", 3, 4)
        assert b == "local_assignment", (c, b, info)

    def a_container_bound_in_a_nested_def_is_not_the_outer_functions_local():
        c, chain, b, _ = _classify(
            "def f(P):\n    def g():\n        Q = {}\n        Q['a']['b'] = 1\n", 4, 8)
        assert b == "unresolved", (c, b)

    def the_outermost_subscript_is_the_one_resolved():
        tree = ast.parse("def f(P):\n    P['a']['b'] = 1\n")
        node = find_node(tree, 2, 4)
        assert isinstance(node, ast.Subscript), node
        assert isinstance(node.ctx, ast.Store), node
        assert e638.subscript_depth(node) == 2, e638.subscript_depth(node)

    def a_tuple_assignment_binds_each_name_to_its_own_kind():
        c, chain, b, info = _classify(
            "def f():\n    numbers, verdicts = {}, []\n    numbers['a']['b'] = 1\n", 3, 4)
        assert (c, b) == ("numbers", "local_assignment"), (c, b)
        assert info["rhs_kind"] == "dict_literal", info

    def an_unmatched_tuple_shape_keeps_the_outer_kind():
        c, chain, b, info = _classify(
            "def f(src):\n    a, b = src\n    a['k']['j'] = 1\n", 3, 4)
        assert b == "local_assignment", (c, b)
        assert info["rhs_kind"] == "tuple_element_unknown" or info["rhs_kind"] == "other", info

    def counts_add_up():
        functions = [
            {"module": "a.py", "function": "f", "start": 1, "end": 9,
             "read_lines": [8], "read_receivers": ["sleeves"],
             "sites_in_the_function": 2, "write_sites_in_the_function": 2,
             "write_sites": [
                 {"line": 3, "column": 8, "container": "P", "binding": "parameter",
                  "bound_from_outside_the_function": True, "binding_rhs_kind": None,
                  "same_name_as_a_counted_read_receiver": False},
                 {"line": 4, "column": 4, "container": "sleeves", "binding": "parameter",
                  "bound_from_outside_the_function": True, "binding_rhs_kind": None,
                  "same_name_as_a_counted_read_receiver": True},
             ], "scope_problem": None},
        ]
        c = counts_of(functions)
        assert c["counted_functions"] == 1, c
        assert c["write_sites"] == 2, c
        assert c["write_site_container_binding_histogram"]["parameter"] == 2, c
        assert c["write_sites_bound_from_outside_the_function"] == 2, c
        assert c["write_sites_bound_inside_the_function"] == 0, c
        assert c["write_sites_sharing_a_counted_read_receiver_name"] == 1, c
        assert c["functions_whose_writes_share_a_read_receiver_name"] == 1, c
        assert c["distinct_write_containers"] == 2, c
        assert c["counted_read_receivers"] == 1, c
        assert c["counted_lines_carried"] == 1, c
        assert decide(c) == V_SHARES_THE_READERS_CONTAINER, decide(c)

    def closed_containers_give_the_outside_verdict():
        functions = [{"module": "a.py", "function": "f", "start": 1, "end": 9,
                      "read_lines": [8], "read_receivers": ["sleeves"],
                      "sites_in_the_function": 1, "write_sites_in_the_function": 1,
                      "write_sites": [{"line": 3, "column": 8, "container": "P",
                                       "binding": "parameter",
                                       "bound_from_outside_the_function": True,
                                       "binding_rhs_kind": None,
                                       "same_name_as_a_counted_read_receiver": False}],
                      "scope_problem": None}]
        c = counts_of(functions)
        assert decide(c) == V_BOUND_OUTSIDE_ONLY, decide(c)

    def no_write_site_gives_the_empty_verdict():
        functions = [{"module": "a.py", "function": "f", "start": 1, "end": 9,
                      "read_lines": [8], "read_receivers": ["P"], "sites_in_the_function": 0,
                      "write_sites_in_the_function": 0, "write_sites": [],
                      "scope_problem": None}]
        c = counts_of(functions)
        assert decide(c) == V_NO_WRITE_SITES, decide(c)
        assert c["functions_carrying_a_write_site"] == 0, c

    def the_published_face_re_derives():
        path = os.path.join(OUTDIR, FACE)
        if not os.path.exists(path):
            say("SKIP :: the published face is absent")
            return
        face = json.load(io.open(path, encoding="utf-8"))
        problems = face_problems(face)
        assert not problems, problems[:3]

    def a_tampered_count_is_refused():
        functions = [{"module": "a.py", "function": "f", "start": 1, "end": 9,
                      "read_lines": [8], "read_receivers": [], "sites_in_the_function": 0,
                      "write_sites_in_the_function": 0, "write_sites": [],
                      "scope_problem": None}]
        face = {"functions": functions, "counts": counts_of(functions),
                "verdict": V_NO_WRITE_SITES}
        face["counts"]["write_sites"] = 7
        problems = face_problems(face)
        assert problems and "counts.write_sites" in problems[0], problems

    for name, fn in [
        ("a parameter container is a parameter", a_parameter_container_is_a_parameter),
        ("a loop target container is a loop target", a_loop_target_container_is_a_loop_target),
        ("a local dict container is a local assignment", a_local_dict_container_is_a_local_assignment),
        ("a module name container is module scope", a_module_name_container_is_module_scope),
        ("an imported container is module scope", an_imported_container_is_module_scope),
        ("an unknown name is unresolved", an_unknown_name_is_unresolved),
        ("precedence puts the parameter first", the_precedence_puts_the_parameter_first),
        ("the chain carries the attribute steps", the_chain_carries_the_attribute_steps),
        ("an augmented assignment counts as a local", an_augmented_assignment_counts_as_a_local),
        ("a container bound in a nested def is not the outer function's local",
         a_container_bound_in_a_nested_def_is_not_the_outer_functions_local),
        ("the outermost subscript is the one resolved", the_outermost_subscript_is_the_one_resolved),
        ("a tuple assignment binds each name to its own kind",
         a_tuple_assignment_binds_each_name_to_its_own_kind),
        ("an unmatched tuple shape keeps the outer kind",
         an_unmatched_tuple_shape_keeps_the_outer_kind),
        ("counts add up", counts_add_up),
        ("closed containers give the outside verdict", closed_containers_give_the_outside_verdict),
        ("no write site gives the empty verdict", no_write_site_gives_the_empty_verdict),
        ("the published face re-derives", the_published_face_re_derives),
        ("a tampered count is refused", a_tampered_count_is_refused),
    ]:
        leg(name, fn)

    ok = sum(1 for _, good in legs if good)
    say("selftest: %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", nargs="?", default="run",
                    choices=("run", "check", "verify", "selftest"))
    args = ap.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    if args.mode == "verify":
        problems = verify()
        for p in problems:
            say("verify: " + p)
        say("verify: problems=%d" % len(problems))
        return 0 if not problems else 1
    doc, _ = build()
    if args.mode == "check":
        problems = face_problems(doc)
        for p in problems:
            say("check: " + p)
        say("check: problems=%d" % len(problems))
        return 0 if not problems else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())