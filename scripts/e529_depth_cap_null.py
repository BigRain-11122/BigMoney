"""E529 (r1560 bm-b): every depth-cap arm that returns a null sentinel, and who reads it.

E528 (r1555) published that ``_resolve`` ends its recursion at ``if depth > 6: return None``,
so a caller cannot tell "the repository does not contain this path" from "the recursion ran out
of depth".  This study asks the corpus-wide version of that question:

    which function carries a counter, tests it against a constant, and returns a null sentinel
    from that arm -- and which of its call sites read that value?

Two things are kept apart on purpose:

  * ``cap_is_a_publishable_hole``      -- a call site reads the sentinel and no site can separate
                                          the cap from the absence it is spelled as
  * ``cap_cannot_be_reached_from_any_call_site`` -- the function is not recursive at all and every
                                          literal counter handed to it at a call site is below the cap,
                                          so the arm is dead code rather than a hole

Nothing is executed and no source is rewritten.

    python scripts/e529_depth_cap_null.py run       # build + write
    python scripts/e529_depth_cap_null.py check     # re-derive every published number
    python scripts/e529_depth_cap_null.py verify    # rebuild without writing, compare bytes
    python scripts/e529_depth_cap_null.py selftest  # offline fixture
"""
import ast
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

CARD = ("E529-WHICH-RESOLVER-IN-THIS-CORPUS-RETURNS-A-NULL-SENTINEL-AT-A-DEPTH-CAP-"
        "AND-WHICH-CALLER-READS-THAT-NULL-AS-ABSENCE")
STUDY = "E529_depth_cap_null"
DATE_STAMP = "2026-11-08"
FACE_NAME = "depthcapnull_latest.json"
DATED_PREFIX = "DEPTHCAPNULL"

SELF_EXCLUDED = ("e529_", "run_e529", "_e529", "DEPTHCAPNULL", "depthcapnull_",
                 "e528_", "run_e528", "_e528", "RECURSIVEREAD", "recursiveread_")

UPSTREAM_FACE = "results/state_tilt/recursiveread_latest.json"
UPSTREAM_STUDY = "E528_recursive_read"

# ---------------------------------------------------------------- vocabularies
C_FORWARDED = "counter_is_forwarded_to_a_call"
C_PARAMETER = "counter_is_a_parameter_never_changed"
C_LOCAL = "counter_is_assigned_inside_the_body_only"
C_OTHER = "counter_is_read_somewhere_else"
COUNTER_VOCAB = (C_FORWARDED, C_PARAMETER, C_LOCAL, C_OTHER)

J_WORD = "the_counter_name_is_a_depth_or_level_word"
J_INCREMENT = "the_counter_is_bumped_by_one_into_a_call_of_the_same_function"
J_BOTH = "the_name_is_a_depth_word_and_it_is_bumped_into_a_recursive_call"
J_NONE = "neither_a_depth_word_nor_a_recursive_increment_so_it_is_an_index_guard"
JUSTIFY_VOCAB = (J_WORD, J_INCREMENT, J_BOTH, J_NONE)
COUNTER_WORDS = ("depth", "level", "lvl", "ply", "hop")

CAP_CONSTANT = "tested_against_an_int_constant"
CAP_SYMBOLIC = "tested_against_a_name_whose_value_this_scan_does_not_resolve"
CAP_VOCAB = (CAP_CONSTANT, CAP_SYMBOLIC)

ARM_BODY = "the_null_is_returned_by_the_branch_the_test_selects"
ARM_ELSE = "the_null_is_returned_by_the_other_branch"
ARM_SAME = "both_branches_return_a_null"
ARM_VOCAB = (ARM_BODY, ARM_ELSE, ARM_SAME)

U_DISCARD = "discards_the_result"
U_TESTS_INLINE = "tests_the_result_at_the_call_site"
U_BINDS_AND_TESTS = "binds_the_result_then_tests_it"
U_BINDS_AND_INDEXES = "binds_the_result_then_indexes_it"
U_BINDS_AND_PASSES = "binds_the_result_then_passes_it_on"
U_BINDS_AND_RETURNS = "binds_the_result_then_returns_it"
U_BINDS_AND_NEVER = "binds_the_result_and_never_reads_it"
U_PASSES = "passes_the_result_on"
U_RETURNS = "returns_the_result"
U_RECURSIVE = "the_function_calls_itself"
U_OTHER = "other_use"
USE_VOCAB = (U_DISCARD, U_TESTS_INLINE, U_BINDS_AND_TESTS, U_BINDS_AND_INDEXES,
             U_BINDS_AND_PASSES, U_BINDS_AND_RETURNS, U_BINDS_AND_NEVER,
             U_PASSES, U_RETURNS, U_RECURSIVE, U_OTHER)

D_NO_TEST = "reads_the_sentinel_without_testing_it"
D_SAME_SENTINEL = "tests_against_the_same_null_so_the_cap_looks_like_absence"
D_TRUTH = "truth_tests_the_sentinel_so_the_cap_looks_like_absence"
D_DIFFERENT = "tests_against_a_value_that_is_not_a_null_sentinel_so_the_cap_is_visible"
D_NONE_READ = "no_call_site_reads_the_value"
DISTINGUISH_VOCAB = (D_NO_TEST, D_SAME_SENTINEL, D_TRUTH, D_DIFFERENT, D_NONE_READ)
NULL_SPELLINGS = frozenset(("None", "False", "''", "()", "[]", "{}", "set()", "frozenset()",
                            "dict()", "list()", "tuple()"))

V_HOLE = "every_null_arm_is_spelled_as_the_absence_value_and_no_caller_can_tell_them_apart"
V_DEAD = "every_null_arm_cannot_be_reached_from_any_call_site_in_the_corpus"
V_MIXED = "some_null_arms_are_read_as_absence_and_some_cannot_be_reached_at_all"
V_EMPTY = "no_function_in_the_corpus_returns_a_null_sentinel_from_a_counter_test"
VERDICT_VOCAB = (V_HOLE, V_DEAD, V_MIXED, V_EMPTY)

NULL_CALLS = ("set", "frozenset", "dict", "list", "tuple")
TEST_OPS = (ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq)


def _now():
    import datetime
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


def _sha256_file(path):
    h = hashlib.sha256()
    try:
        with io.open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    except OSError:
        return None
    return h.hexdigest()


# ------------------------------------------------------------------- helpers
def corpus_files(root=None):
    root = root or ROOT
    out = []
    for base in ("scripts", "Tools", "firm", "live", "monitor"):
        dpath = os.path.join(root, base)
        if not os.path.isdir(dpath):
            continue
        for dirpath, dirnames, filenames in os.walk(dpath):
            dirnames[:] = [d for d in dirnames if d not in
                           ("__pycache__", ".git", "_quarantine")]
            for name in sorted(filenames):
                if not name.endswith(".py"):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")
                if any(tag in rel for tag in SELF_EXCLUDED):
                    continue
                out.append(rel)
    return sorted(set(out))


def _read_tree(rel, root=None):
    path = os.path.join(root or ROOT, rel)
    try:
        with io.open(path, "rb") as fh:
            raw = fh.read()
    except OSError:
        return None
    try:
        return ast.parse(raw)
    except SyntaxError:
        return None


def _parents(tree):
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    return parents


def null_repr(node):
    """The published spelling of a null sentinel, or None when the node is not one."""
    if isinstance(node, ast.Constant):
        if node.value is None:
            return "None"
        if node.value is False:
            return "False"
        if isinstance(node.value, str) and node.value == "":
            return "''"
        return None
    if isinstance(node, ast.Tuple) and not node.elts:
        return "()"
    if isinstance(node, ast.List) and not node.elts:
        return "[]"
    if isinstance(node, ast.Dict) and not node.keys:
        return "{}"
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        if node.func.id in NULL_CALLS and not node.args and not node.keywords:
            return node.func.id + "()"
    return None


def _returns_in(stmts):
    """Every null sentinel returned directly by this statement list (not nested functions)."""
    out = []
    stack = list(stmts)
    while stack:
        stmt = stack.pop()
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if isinstance(stmt, ast.Return):
            rep = null_repr(stmt.value) if stmt.value is not None else "None"
            if rep is not None:
                out.append(rep)
            continue
        for field in ("body", "orelse", "finalbody"):
            stack.extend(getattr(stmt, field, []) or [])
        for handler in getattr(stmt, "handlers", []) or []:
            stack.extend(handler.body)
    return out


def _counter_kind(fn, name, tree_parents=None):
    if name in {a.arg for a in fn.args.args + fn.args.kwonlyargs}:
        for node in ast.walk(fn):
            if isinstance(node, ast.Call):
                for arg in list(node.args) + [k.value for k in node.keywords]:
                    if isinstance(arg, ast.BinOp) and isinstance(arg.left, ast.Name) \
                            and arg.left.id == name and isinstance(arg.op, (ast.Add, ast.Sub)):
                        return C_FORWARDED
                    if isinstance(arg, ast.Name) and arg.id == name:
                        return C_FORWARDED
            if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name) \
                    and node.target.id == name:
                return C_FORWARDED
        assigned = False
        for node in ast.walk(fn):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in targets:
                    if isinstance(t, ast.Name) and t.id == name:
                        assigned = True
        return C_LOCAL if assigned else C_PARAMETER
    assigned = False
    for node in ast.walk(fn):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                if isinstance(t, ast.Name) and t.id == name:
                    assigned = True
        if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name) \
                and node.target.id == name:
            assigned = True
    return C_LOCAL if assigned else C_OTHER


def _bumped_into_a_recursive_call(fn, name):
    for node in ast.walk(fn):
        if not isinstance(node, ast.Call) or _call_name(node) != getattr(fn, "name", None):
            continue
        for arg in list(node.args) + [k.value for k in node.keywords]:
            if isinstance(arg, ast.BinOp) and isinstance(arg.left, ast.Name) \
                    and arg.left.id == name and isinstance(arg.op, (ast.Add, ast.Sub)) \
                    and isinstance(arg.right, ast.Constant) and arg.right.value == 1:
                return True
            if isinstance(arg, ast.BinOp) and isinstance(arg.right, ast.Name) \
                    and arg.right.id == name and isinstance(arg.op, (ast.Add, ast.Sub)) \
                    and isinstance(arg.left, ast.Constant) and arg.left.value == 1:
                return True
    return False


def justify_counter(fn, name):
    word = any(w in name.lower() for w in COUNTER_WORDS)
    bumped = _bumped_into_a_recursive_call(fn, name)
    if word and bumped:
        return J_BOTH
    if word:
        return J_WORD
    if bumped:
        return J_INCREMENT
    return J_NONE


def _cap_arms(fn, rejections=None):
    """Every counter test in this function whose selected branch returns a null sentinel."""
    arms = []
    for node in ast.walk(fn):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if not isinstance(test, ast.Compare) or len(test.ops) != 1:
            continue
        if not isinstance(test.ops[0], TEST_OPS):
            continue
        left = test.left
        if not isinstance(left, ast.Name):
            continue
        comp = test.comparators[0]
        if isinstance(comp, ast.Constant) and isinstance(comp.value, int) \
                and not isinstance(comp.value, bool):
            cap = comp.value
            cap_class = CAP_CONSTANT
        elif isinstance(comp, ast.Name):
            cap = comp.id
            cap_class = CAP_SYMBOLIC
        else:
            continue
        body_nulls = _returns_in(node.body)
        else_nulls = _returns_in(node.orelse)
        if body_nulls and else_nulls:
            arm, sentinel = ARM_SAME, body_nulls[0]
        elif body_nulls:
            arm, sentinel = ARM_BODY, body_nulls[0]
        elif else_nulls:
            arm, sentinel = ARM_ELSE, else_nulls[0]
        else:
            continue
        justification = justify_counter(fn, left.id)
        if justification == J_NONE:
            if rejections is not None:
                rejections.append({"function": getattr(fn, "name", None),
                                   "counter": left.id,
                                   "cap": comp.value if isinstance(comp, ast.Constant) else left.id,
                                   "line": getattr(node, "lineno", None)})
            continue
        counter_kind = _counter_kind(fn, left.id)
        if counter_kind not in (C_FORWARDED, C_LOCAL):
            continue
        arms.append({
            "counter": left.id,
            "op": type(test.ops[0]).__name__,
            "cap": cap,
            "cap_class": cap_class,
            "sentinel": sentinel,
            "arm": arm,
            "line": getattr(node, "lineno", None),
            "counter_class": counter_kind,
            "justification": justification,
        })
    return arms


def _enclosing_function(node, parents, tree):
    cur = parents.get(node)
    while cur is not None:
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return cur
        cur = parents.get(cur)
    return None


def _literal_counter_at_call(call, fn):
    names = [a.arg for a in fn.args.args]
    idx = None
    for i, a in enumerate(fn.args.args):
        if a.arg in {str(n) for n in []}:
            idx = i
    return idx, names


def _bound_use(fn, target_name, after_line):
    """How a name bound from the callee's result is used later in the same function."""
    kinds = set()
    sentinel_test = False
    for node in ast.walk(fn):
        if isinstance(node, ast.Name) and node.id == target_name and isinstance(node.ctx, ast.Load):
            if getattr(node, "lineno", 0) <= after_line:
                continue
            kinds.add("load")
        if isinstance(node, ast.Compare):
            sides = [node.left] + list(node.comparators)
            has_name = any(isinstance(s, ast.Name) and s.id == target_name for s in sides)
            if has_name:
                others = [s for s in sides if not (isinstance(s, ast.Name) and s.id == target_name)]
                if any(null_repr(o) is not None for o in others):
                    sentinel_test = True
                    kinds.add("sentinel_test")
                else:
                    kinds.add("other_test")
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) \
                and node.value.id == target_name:
            kinds.add("index")
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
                and node.value.id == target_name:
            kinds.add("attribute")
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Name) \
                and node.value.id == target_name:
            kinds.add("return")
        if isinstance(node, ast.Call):
            for arg in list(node.args) + [k.value for k in node.keywords]:
                if isinstance(arg, ast.Name) and arg.id == target_name:
                    kinds.add("pass")
        if isinstance(node, (ast.If, ast.While)) and isinstance(node.test, ast.Name) \
                and node.test.id == target_name:
            kinds.add("truth")
        if isinstance(node, ast.BoolOp):
            for v in node.values:
                if isinstance(v, ast.Name) and v.id == target_name:
                    kinds.add("truth")
    if "sentinel_test" in kinds:
        return U_BINDS_AND_TESTS, D_SAME_SENTINEL
    if "other_test" in kinds:
        return U_BINDS_AND_TESTS, D_DIFFERENT
    if "truth" in kinds:
        return U_BINDS_AND_TESTS, D_TRUTH
    if "index" in kinds or "attribute" in kinds:
        return U_BINDS_AND_INDEXES, D_NO_TEST
    if "pass" in kinds:
        return U_BINDS_AND_PASSES, D_NO_TEST
    if "return" in kinds:
        return U_BINDS_AND_RETURNS, D_NO_TEST
    return U_BINDS_AND_NEVER, D_NO_TEST


def use_class(call, parents, tree):
    """Classify one call site by what the enclosing code does with the return value."""
    node = call
    parent = parents.get(node)
    enclosing_fn = _enclosing_function(node, parents, tree)
    if enclosing_fn is not None and getattr(enclosing_fn, "name", None) == _call_name(node):
        return U_RECURSIVE, D_NO_TEST
    if isinstance(parent, ast.Expr):
        return U_DISCARD, D_NO_TEST
    if isinstance(parent, (ast.Assign, ast.AnnAssign)):
        targets = parent.targets if isinstance(parent, ast.Assign) else [parent.target]
        name = None
        for t in targets:
            if isinstance(t, ast.Name):
                name = t.id
                break
        if name is None:
            return U_OTHER, D_NO_TEST
        fn = _enclosing_function(node, parents, tree)
        if fn is None:
            return U_OTHER, D_NO_TEST
        return _bound_use(fn, name, getattr(parent, "lineno", 0))
    if isinstance(parent, ast.Compare):
        sides = [parent.left] + list(parent.comparators)
        others = [s for s in sides if s is not node]
        if any(null_repr(o) is not None for o in others):
            return U_TESTS_INLINE, D_SAME_SENTINEL
        return U_TESTS_INLINE, D_DIFFERENT
    if isinstance(parent, (ast.If, ast.While)) and parent.test is node:
        return U_TESTS_INLINE, D_TRUTH
    if isinstance(parent, ast.BoolOp):
        return U_TESTS_INLINE, D_TRUTH
    if isinstance(parent, ast.UnaryOp):
        return U_TESTS_INLINE, D_TRUTH
    if isinstance(parent, ast.Subscript):
        return U_OTHER, D_NO_TEST
    if isinstance(parent, ast.Attribute):
        return U_OTHER, D_NO_TEST
    if isinstance(parent, ast.Return):
        return U_RETURNS, D_NO_TEST
    if isinstance(parent, ast.Call):
        for arg in list(parent.args) + [k.value for k in parent.keywords]:
            if arg is node:
                return U_PASSES, D_NO_TEST
        return U_OTHER, D_NO_TEST
    return U_OTHER, D_NO_TEST


def _imports(tree):
    """The module stems this module imports, so a cross-module call can be attributed."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[-1])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[-1])
    return names


def _call_name(call):
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


# ------------------------------------------------------------------ the scan
def scan(root=None):
    root = root or ROOT
    files = corpus_files(root)
    trees = {}
    for rel in files:
        tree = _read_tree(rel, root)
        if tree is not None:
            trees[rel] = tree

    defs = {}
    for rel in sorted(trees):
        tree = trees[rel]
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defs.setdefault(node.name, []).append((rel, node))

    sites = []
    at_risk = {}
    rejections = []
    for name in sorted(defs):
        for rel, fn in defs[name]:
            arms = _cap_arms(fn, rejections)
            if not arms:
                continue
            recursive = any(isinstance(c, ast.Call) and _call_name(c) == name
                            for c in ast.walk(fn))
            merged = {}
            for arm in arms:
                key = (arm["counter"], arm["sentinel"], arm["cap_class"],
                       arm["cap"] if arm["cap_class"] == CAP_SYMBOLIC else None)
                if key in merged:
                    merged[key]["lines"].append(arm["line"])
                else:
                    arm["lines"] = [arm["line"]]
                    arm.pop("line", None)
                    merged[key] = arm
            at_risk.setdefault(name, []).extend(
                {"module": rel, "function": name, "has_recursive_call": recursive, **a}
                for a in merged.values())
    # every call site of every affected function, over the same corpus
    for rel in sorted(trees):
        tree = trees[rel]
        parents = _parents(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = _call_name(node)
            if name not in at_risk:
                continue
            targets = [(d_rel, d_fn) for d_rel, d_fn in defs.get(name, [])]
            if not targets:
                continue
            def_modules = {d_rel for d_rel, _ in targets}
            imported = _imports(tree)
            attributed_modules = sorted(
                m for m in def_modules
                if m == rel or os.path.splitext(os.path.basename(m))[0] in imported)
            use, dist = use_class(node, parents, tree)
            enclosing = _enclosing_function(node, parents, tree)
            counters = {a["counter"] for d_rel, d_fn in targets for a in at_risk[name]}
            literals = []
            defaults = []
            routes = []
            for d_rel, d_fn in targets:
                params = [a.arg for a in d_fn.args.args]
                for i, pname in enumerate(params):
                    if pname not in counters:
                        continue
                    value = None
                    starred_seen = any(isinstance(a, ast.Starred) for a in node.args[:i])
                    if i < len(node.args) and not starred_seen:
                        value = node.args[i]
                    for kw in node.keywords:
                        if kw.arg == pname:
                            value = kw.value
                    if isinstance(value, ast.Constant) and isinstance(value.value, int) \
                            and not isinstance(value.value, bool):
                        literals.append(value.value)
                        routes.append(value.value)
                        continue
                    if value is not None:
                        routes.append(None)
                        continue
                    resolved = None
                    for pidx, pdef in enumerate(d_fn.args.defaults):
                        pname2 = params[len(params) - len(d_fn.args.defaults) + pidx]
                        if pname2 == pname and isinstance(pdef, ast.Constant) \
                                and isinstance(pdef.value, int) \
                                and not isinstance(pdef.value, bool):
                            resolved = pdef.value
                    defaults.append(resolved)
                    routes.append(resolved)
            sites.append({
                "module": rel,
                "line": getattr(node, "lineno", None),
                "callee": name,
                "callee_modules": sorted(def_modules),
                "attributed_modules": attributed_modules,
                "caller": (getattr(enclosing, "name", None) if enclosing else None),
                "use": use,
                "distinguish": dist,
                "literal_counters_passed": literals,
                "omitted_counter_defaults": defaults,
                "counter_routes": routes,
            })
    return at_risk, sites, len(files), len(trees), rejections


def _reader_sites(arm_sites, module):
    """Call sites this arm can decide: the same module, or a module that imports it."""
    return [s for s in arm_sites
            if s["use"] != U_RECURSIVE and module in s.get("attributed_modules", [])]


def _unattributed(arm_sites, module):
    return [s for s in arm_sites if module not in s.get("attributed_modules", [])]


def _site_verdict(arm, arm_sites):
    if not arm_sites:
        return D_NONE_READ
    dists = {s["distinguish"] for s in arm_sites}
    if D_SAME_SENTINEL in dists or D_TRUTH in dists:
        return D_SAME_SENTINEL if D_SAME_SENTINEL in dists else D_TRUTH
    return D_NO_TEST


def _is_dead(arm, arm_sites, counter_routes):
    """An arm is dead only when every route into the counter is provably below its cap.

    A counter this scan sees assigned inside the body (a loop counter) can reach its cap no
    matter what a caller passes, so it is never published dead.
    """
    if arm["counter_class"] != C_FORWARDED:
        return False
    if arm["has_recursive_call"]:
        return False
    if arm["cap_class"] != CAP_CONSTANT or not isinstance(arm["cap"], int):
        return False
    possible = list(counter_routes)
    if not possible or any(v is None for v in possible):
        return False
    return max(possible) < arm["cap"]


def build(root=None, write=True):
    root = root or ROOT
    at_risk, sites, n_files, n_trees, rejections = scan(root)
    by_callee = {}
    for s in sites:
        by_callee.setdefault(s["callee"], []).append(s)

    rows = []
    for name in sorted(at_risk):
        arm_sites = by_callee.get(name, [])
        for arm in sorted(at_risk[name], key=lambda a: (a["module"], str(a["lines"]))):
            row = dict(arm)
            mine = arm_sites
            readers = _reader_sites(mine, arm["module"])
            local_literals = [v for s in readers for v in s["literal_counters_passed"]]
            local_routes = [v for s in readers for v in s["counter_routes"]]
            row["call_site_count"] = len(readers)
            row["recursive_self_calls"] = len([x for x in mine if x["use"] == U_RECURSIVE
                                              and arm["module"] in x.get("attributed_modules", [])])
            row["unattributed_name_matches"] = len(_unattributed(mine, arm["module"]))
            row["use_counts"] = _count(readers, "use", USE_VOCAB)
            row["distinguish"] = _site_verdict(arm, readers)
            row["counter_routes_seen"] = sorted({str(v) for v in local_routes})
            row["dead_arm"] = _is_dead(arm, readers, local_routes)
            row["max_literal_counter_seen"] = (max(local_literals) if local_literals else None)
            rows.append(row)

    living = [r for r in rows if not r["dead_arm"]]
    dead = [r for r in rows if r["dead_arm"]]
    read_arms = [r for r in living if r["call_site_count"] > 0]
    summary = {
        "sources_read": n_files,
        "sources_parsed": n_trees,
        "functions_with_a_null_cap_arm": len({r["function"] for r in rows}),
        "null_cap_arms": len(rows),
        "arms_reachable_from_a_call_site": len(living),
        "arms_dead_code_from_every_call_site": len(dead),
        "arms_with_at_least_one_call_site": len(read_arms),
        "arms_no_call_site_reads": len([r for r in living if r["call_site_count"] == 0]),
        "call_sites": len([x for x in sites if x.get("attributed_modules")]),
        "unattributed_same_name_calls": len([x for x in sites if not x.get("attributed_modules")]),
        "justification_histogram": _hist([r["justification"] for r in rows]),
        "rejected_counter_tests": len(rejections),
        "rejected_counter_test_examples": rejections[:12],
        "rejected_reason": J_NONE,
        "sentinel_histogram": _hist([r["sentinel"] for r in rows]),
        "counter_class_histogram": _hist([r["counter_class"] for r in rows]),
        "cap_class_histogram": _hist([r["cap_class"] for r in rows]),
        "arm_histogram": _hist([r["arm"] for r in rows]),
        "use_histogram": _count([x for x in sites if x.get("attributed_modules")],
                                "use", USE_VOCAB),
        "distinguish_histogram": _hist([r["distinguish"] for r in rows]),
        "arms_whose_reader_sees_a_non_null_value": len([r for r in rows
                                                        if r["distinguish"] == D_DIFFERENT]),
    }
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("every depth-cap arm that returns a null sentinel, and which call site reads that "
                  "null as absence"),
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": ("%s::scan() -- every FunctionDef under scripts/Tools/firm/live/monitor "
                              "whose body tests a name against an int constant or a symbolic cap and "
                              "returns a null sentinel from the selected branch" % os.path.basename(__file__)),
        "upstream_face": UPSTREAM_FACE,
        "upstream_study": UPSTREAM_STUDY,
        "upstream_face_sha256": _sha256_file(os.path.join(root, UPSTREAM_FACE)),
        "method_limits": [
            "a null sentinel is read off the AST only: None / False / '' / () / [] / {} / set() / "
            "frozenset() / dict() / list() / tuple(). A sentinel computed by a helper "
            "(``NULL = _null()``) is outside this scan and is never published as absent",
            "the counter must be a Name tested against a single comparison: a test hidden behind "
            "``not``, ``all(...)`` or a helper predicate is outside this scan",
            "a name tested against a constant is a *depth counter* only when it is named like one "
            "(depth/level/lvl/ply/hop) or when it is bumped by one into a call of the same function; "
            "every other such test is a bar index or a length guard and is counted in "
            "rejected_counter_tests rather than dropped silently (``elig(prices, i)`` testing "
            "``i < MIN_BARS`` is the shape this rejects)",
            "``distinguishable`` means the call site compares the result against a value that is not "
            "the same null spelling; a site that only tests ``is None`` cannot separate the cap from "
            "the absence, so it is published under D_SAME_SENTINEL rather than as a reader",
            "an arm is published dead only when the counter reaches the function purely by being "
            "forwarded (never assigned in the body), the function carries no recursive call, the cap is "
            "an int constant, and every counter value a call site can supply -- a literal argument or a "
            "literal default when the argument is omitted -- is below the cap. A counter assigned in the "
            "body is a loop counter that can reach the cap from any call, and a non-literal value keeps "
            "the arm alive",
            "a call site decides an arm only when the call and the definition live in the same module, "
            "or when the calling module imports the defining module's stem -- anything else is a "
            "same-name collision and is published as unattributed_same_name_calls (``main`` alone "
            "collides with over a thousand ``sys.exit(main())`` sites), never as a reader",
            "nothing is executed and no source is rewritten",
            "sources_read is a snapshot of a live tree that other lanes write to; it is published but "
            "not gated, while every verdict class is re-derived",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "counter_vocab": list(COUNTER_VOCAB),
        "justify_vocab": list(JUSTIFY_VOCAB),
        "cap_vocab": list(CAP_VOCAB),
        "arm_vocab": list(ARM_VOCAB),
        "use_vocab": list(USE_VOCAB),
        "distinguish_vocab": list(DISTINGUISH_VOCAB),
        "arms": rows,
        "call_sites": sites,
    }
    if write:
        write_face(face, root)
    return face


def _hist(values):
    out = {}
    for v in values:
        out[str(v)] = out.get(str(v), 0) + 1
    return dict(sorted(out.items()))


def _count(records, key, vocab):
    out = {k: 0 for k in vocab}
    for r in records:
        out[r[key]] = out.get(r[key], 0) + 1
    return out


def _verdict(summary):
    if not summary["null_cap_arms"]:
        return V_EMPTY
    dead = summary["arms_dead_code_from_every_call_site"]
    living = summary["arms_reachable_from_a_call_site"]
    if living and not dead:
        return V_HOLE
    if dead and not living:
        return V_DEAD
    return V_MIXED


def write_face(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    os.makedirs(outdir, exist_ok=True)
    dated = os.path.join(outdir, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP))
    latest = os.path.join(outdir, FACE_NAME)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    return latest, dated


def load_face(root=None, name=None):
    root = root or ROOT
    path = os.path.join(root, "results", "state_tilt", name or FACE_NAME)
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def face_problems(face, root=None):
    problems = []
    arms = face.get("arms") or []
    sites = face.get("call_sites") or []
    for i, r in enumerate(arms):
        tag = "arms[%d] %s:%s" % (i, r.get("module"), r.get("function"))
        if r.get("sentinel") not in NULL_SPELLINGS:
            problems.append(tag + " sentinel is not a known null spelling")
        if r.get("cap_class") not in CAP_VOCAB:
            problems.append(tag + " cap_class not in vocab")
        if r.get("justification") not in JUSTIFY_VOCAB or r.get("justification") == J_NONE:
            problems.append(tag + " justification is not a published depth-counter reason")
        if r.get("counter_class") not in COUNTER_VOCAB:
            problems.append(tag + " counter_class not in vocab")
        if r.get("arm") not in ARM_VOCAB:
            problems.append(tag + " arm not in vocab")
        if r.get("distinguish") not in DISTINGUISH_VOCAB:
            problems.append(tag + " distinguish not in vocab")
        if r.get("cap_class") == CAP_CONSTANT and not isinstance(r.get("cap"), int):
            problems.append(tag + " constant cap is not an int")
        mine = _reader_sites([s for s in sites if s.get("callee") == r.get("function")],
                             r.get("module"))
        if r.get("call_site_count") != len(mine):
            problems.append(tag + " call_site_count %r != %d sites" % (r.get("call_site_count"), len(mine)))
        want = _count(mine, "use", USE_VOCAB)
        if r.get("use_counts") != want:
            problems.append(tag + " use_counts do not re-derive")
        callee_sites = [s for s in sites if s.get("callee") == r.get("function")]
        if r.get("recursive_self_calls") != len([x for x in callee_sites if x["use"] == U_RECURSIVE
                                                 and r.get("module") in x.get("attributed_modules", [])]):
            problems.append(tag + " recursive_self_calls does not re-derive")
        if r.get("unattributed_name_matches") != len(_unattributed(callee_sites, r.get("module"))):
            problems.append(tag + " unattributed_name_matches does not re-derive")
        if r.get("distinguish") != _site_verdict(r, mine):
            problems.append(tag + " distinguish does not re-derive")
    for i, s in enumerate(sites):
        if s.get("use") not in USE_VOCAB:
            problems.append("call_sites[%d] use not in vocab" % i)
        if s.get("distinguish") not in DISTINGUISH_VOCAB:
            problems.append("call_sites[%d] distinguish not in vocab" % i)
        if s.get("callee") not in {r.get("function") for r in arms}:
            problems.append("call_sites[%d] names a callee no arm publishes" % i)
    if any("attributed_modules" not in s for s in sites):
        problems.append("a call site carries no attributed_modules list")
    summary = face.get("summary") or {}
    if summary.get("call_sites") != len([s for s in sites if s.get("attributed_modules")]):
        problems.append("summary.call_sites does not count attributed sites")
    if summary.get("unattributed_same_name_calls") != len([s for s in sites
                                                           if not s.get("attributed_modules")]):
        problems.append("summary.unattributed_same_name_calls does not re-derive")
    if summary.get("null_cap_arms") != len(arms):
        problems.append("summary.null_cap_arms != len(arms)")

    dead = len([r for r in arms if r.get("dead_arm")])
    if summary.get("arms_dead_code_from_every_call_site") != dead:
        problems.append("summary dead count does not re-derive")
    if face.get("verdict") != _verdict(summary):
        problems.append("verdict does not re-derive from summary")
    if summary.get("arms_whose_reader_sees_a_non_null_value", 0) != len(
            [r for r in arms if r.get("distinguish") == D_DIFFERENT]):
        problems.append("summary.arms_whose_reader_sees_a_non_null_value does not re-derive")
    return problems


def check(face=None, root=None):
    face = face or load_face(root)
    problems = face_problems(face, root)
    if problems:
        for p in problems[:12]:
            print("PROBLEM", p)
        print("check: %d problems" % len(problems))
        return 1
    print("check: problems=0 over %d arms / %d call sites"
          % (len(face["arms"]), len(face["call_sites"])))
    return 0


def verify(root=None):
    root = root or ROOT
    on_disk = load_face(root)
    fresh = build(root=root, write=False)
    for key in ("generated",):
        fresh.pop(key, None)
        on_disk = dict(on_disk)
        on_disk.pop(key, None)
    a = json.dumps(on_disk, ensure_ascii=False, sort_keys=True)
    b = json.dumps(fresh, ensure_ascii=False, sort_keys=True)
    if a != b:
        problems = 0
        for key in sorted(set(on_disk) | set(fresh)):
            if on_disk.get(key) != fresh.get(key):
                problems += 1
                print("DRIFT", key)
        print("verify: rebuild differs in %d top-level keys" % problems)
        return 1
    print("verify: rebuild identical (%d arms, %d call sites)"
          % (len(fresh["arms"]), len(fresh["call_sites"])))
    return 0


FIXTURE = '''\
import os


def walk(node, depth=0):
    if depth > 2:
        return None
    for child in getattr(node, "children", []):
        walk(child, depth + 1)
    return node


def typed(expr, level=0):
    if level >= 4:
        return ()
    return typed(expr, level + 1)


def local_only(box):
    level = 0
    while box:
        level = level + 1
        if level > 3:
            return {}
    return box


def discard():
    walk(object())


def inline():
    if walk(object()) is None:
        return "absent"
    return "present"


def bound():
    got = typed(object())
    if got is None:
        return 1
    return 2


def dead_call():
    return local_only(1)


def unrelated(n):
    if n > 10:
        return None
    return n
'''


def _fixture_root():
    import tempfile
    base = tempfile.mkdtemp(prefix="e529_")
    os.makedirs(os.path.join(base, "scripts"), exist_ok=True)
    with io.open(os.path.join(base, "scripts", "fx.py"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(FIXTURE)
    return base


def selftest():
    ok = 0
    total = 0

    def leg(name, cond, detail=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print("PASS %s" % name)
        else:
            print("FAIL %s  %s" % (name, detail))

    base = _fixture_root()
    at_risk, sites, n_files, n_trees, rejections = scan(base)
    leg("sources", n_files == 1 and n_trees == 1, "%r/%r" % (n_files, n_trees))
    leg("walk_arm", "walk" in at_risk, sorted(at_risk))
    arm = at_risk["walk"][0]
    leg("walk_counter_forwarded", arm["counter_class"] == C_FORWARDED, arm["counter_class"])
    leg("walk_cap", arm["cap"] == 2 and arm["cap_class"] == CAP_CONSTANT, repr(arm))
    leg("walk_sentinel", arm["sentinel"] == "None", arm["sentinel"])
    leg("walk_recursive", arm["has_recursive_call"] is True, "")
    leg("typed_arm", "typed" in at_risk and at_risk["typed"][0]["sentinel"] == "()",
        at_risk.get("typed"))
    leg("local_arm", "local_only" in at_risk
        and at_risk["local_only"][0]["counter_class"] == C_LOCAL,
        at_risk.get("local_only"))
    leg("parameter_only_excluded", "unrelated" not in at_risk, sorted(at_risk))
    leg("index_guard_rejected", len(rejections) >= 1
        and "unrelated" in {r["function"] for r in rejections}, rejections)

    walk_all = [s for s in sites if s["callee"] == "walk"]
    walk_sites = _reader_sites(walk_all, "scripts/fx.py")
    leg("walk_two_reader_sites", len(walk_sites) == 2, walk_sites)
    leg("walk_self_call_separated",
        len(walk_all) - len(walk_sites) == 1
        and [s for s in walk_all if s["use"] == U_RECURSIVE][0]["caller"] == "walk", walk_all)
    uses = {s["caller"]: s["use"] for s in walk_sites}
    leg("discard_site", uses.get("discard") == U_DISCARD, uses)
    leg("inline_site", uses.get("inline") == U_TESTS_INLINE, uses)
    inline = [s for s in walk_sites if s["caller"] == "inline"][0]
    leg("inline_same_sentinel", inline["distinguish"] == D_SAME_SENTINEL, inline)
    bound_sites = _reader_sites([s for s in sites if s["callee"] == "typed"], "scripts/fx.py")
    leg("bound_tested", bound_sites and bound_sites[0]["use"] == U_BINDS_AND_TESTS, bound_sites)
    leg("bound_same_sentinel", bound_sites and bound_sites[0]["distinguish"] == D_SAME_SENTINEL,
        bound_sites)

    # a call site that passes a literal below the cap keeps the arm alive; no literal and no
    # recursion makes it dead
    dead_arm = at_risk["local_only"][0]
    dead_sites = _reader_sites([s for s in sites if s["callee"] == "local_only"],
                               "scripts/fx.py")
    leg("loop_counter_never_dead",
        _is_dead(dead_arm, dead_sites,
                 [v for s in dead_sites for v in s["counter_routes"]]) is False,
        dead_arm)
    walk_arm = at_risk["walk"][0]
    leg("forwarded_counter_with_recursion_stays_live",
        _is_dead(walk_arm, walk_sites, [0, 1]) is False, walk_arm)
    leg("forwarded_counter_below_cap_without_recursion_is_dead",
        _is_dead({"counter_class": C_FORWARDED, "has_recursive_call": False,
                  "cap_class": CAP_CONSTANT, "cap": 5}, [], [0, 1]) is True, "")
    leg("unknown_counter_value_keeps_arm_live",
        _is_dead({"counter_class": C_FORWARDED, "has_recursive_call": False,
                  "cap_class": CAP_CONSTANT, "cap": 5}, [], [0, None]) is False, "")

    face = build(root=base, write=False)
    leg("face_arms", len(face["arms"]) == 3, len(face["arms"]))
    leg("face_checks", face_problems(face, base) == [], face_problems(face, base)[:3])
    leg("no_non_null_reader", face["summary"]["arms_whose_reader_sees_a_non_null_value"] == 0,
        face["summary"]["arms_whose_reader_sees_a_non_null_value"])

    # a doctored copy must be caught
    import copy
    bad = copy.deepcopy(face)
    bad["arms"][0]["sentinel"] = "SENTINEL"
    leg("doctor_sentinel_caught", face_problems(bad, base) != [], "")
    bad2 = copy.deepcopy(face)
    bad2["arms"][0]["call_site_count"] = 99
    leg("doctor_count_caught", face_problems(bad2, base) != [], "")
    bad3 = copy.deepcopy(face)
    bad3["verdict"] = V_EMPTY
    leg("doctor_verdict_caught", face_problems(bad3, base) != [], "")

    print("selftest: %d/%d" % (ok, total))
    return 0 if ok == total else 1


def run():
    face = build()
    problems = face_problems(face)
    print(json.dumps({
        "verdict": face["verdict"],
        "summary": face["summary"],
        "problems": problems[:5],
    }, ensure_ascii=False, indent=1))
    return 0 if not problems else 1


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    cmd = (argv[0] if argv else "run").lower()
    if cmd == "run":
        return run()
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    if cmd == "probe":
        at_risk, sites, n_files, n_trees, rejections = scan()
        for name in sorted(at_risk):
            for a in at_risk[name]:
                print("%-28s %-42s %s %r %s %s" % (a["function"], a["module"], a["sentinel"],
                                                   a["cap"], a["counter_class"], a["arm"]))
        print("sources=%d parsed=%d functions=%d sites=%d rejected=%d"
              % (n_files, n_trees, len(at_risk), len(sites), len(rejections)))
        return 0
    print("usage: run|check|verify|selftest|probe")
    return 2


if __name__ == "__main__":
    sys.exit(main())