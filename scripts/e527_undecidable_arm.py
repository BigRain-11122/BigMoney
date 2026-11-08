"""E527 -- which of E521's undecidable arms becomes decidable when the argument is followed one hop?

E521 (results/state_tilt/EMPTYARMREACH-2026-11-08.json) priced 199 unguarded production reads and
left 52 of them with the verdict

    the_read_would_raise_and_the_arm_s_reachability_is_not_decidable_from_the_call_site

"Not decidable from the call site" is a statement about one line.  The guard that decides whether the
empty arm is taken reads a parameter of the callee, and the call site passes a *name* instead of a
literal -- so the value that decides the arm sits one hop away, in the caller's own scope.  This study
walks that hop and publishes, per undecided arm:

  * ``arm_class`` -- why E521 left it undecided: the guard names a parameter and the site passes no
    literal, or the guard sits behind a test that names no parameter of the callee at all.  The second
    class cannot be settled by following any argument: the arm does not depend on the call at all.
  * ``parameter`` -- the parameter its guard actually reads (``if not x:`` -> x), taken from the same
    test walk E521 used, so the two faces cannot drift apart.
  * ``argument_expression`` -- what the call site passes for that parameter, verbatim.
  * ``binding_class`` -- what that expression is one hop out: a name the caller function binds to a
    literal, a module-level constant that folds to a literal, a call result, the caller's own
    parameter, a loop/with target, a non-literal expression, or nothing in the caller at all.
  * ``arm_outcome`` -- whether the arm is now excluded, guaranteed, or still open.

A literal is only accepted as decisive when its binding dominates the call: a binding inside a branch
that the call does not itself sit in is published as ``a_binding_inside_a_branch``, and a name rebound
after its first binding is published as ``a_name_that_is_rebound_before_the_call``.  Both stay open
rather than being read as if the static nearest binding were the runtime one.

    python scripts/e527_undecidable_arm.py build     # write the face
    python scripts/e527_undecidable_arm.py check     # gate the published face (fast)
    python scripts/e527_undecidable_arm.py verify    # re-derive from the tree and gate
    python scripts/e527_undecidable_arm.py selftest  # fixture corpus + doctored faces
"""
from __future__ import annotations

import ast
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e521_reachable_empty_arm as e521  # noqa: E402  (population, arm census, literal classes)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")

CARD = ("E527-WHICH-OF-THE-52-UNDECIDABLE-ARMS-BECOMES-DECIDABLE-WHEN-THE-PARAMETER-IS-"
        "FOLLOWED-ONE-HOP")
STUDY = "E527_undecidable_arm"
DATE_STAMP = "2026-11-08"
FACE_NAME = "undecidablearm_latest.json"
DATED_PREFIX = "UNDECIDABLEARM"
PARENT_FACE = "EMPTYARMREACH-2026-11-08.json"

# a scan that reads the tree must not read its own output
SELF_EXCLUDED = ("e527_", "run_e527", "_e527", "UNDECIDABLEARM", "undecidablearm_")

# --- why the arm was undecided in the first place (E521's own two classes) --------------------
ARM_FOLLOWABLE = e521.REACH_UNDECIDED_NON_LITERAL
ARM_STRUCTURAL = e521.REACH_UNDECIDED_OTHER_GUARD
ARM_CLASS_OF = {
    ARM_FOLLOWABLE: "the_guard_names_a_parameter_and_the_site_passes_no_literal",
    ARM_STRUCTURAL: "the_guard_sits_behind_a_test_that_names_no_parameter_of_the_callee",
}

# --- what the argument is, one hop out -------------------------------------------------------
B_LITERAL = "a_name_the_caller_binds_to_a_literal"
B_MODULE_CONSTANT = "a_name_the_caller_binds_to_a_module_constant_that_folds_to_a_literal"
B_CALL = "a_name_the_caller_binds_from_a_call_result"
B_CALLER_PARAM = "the_caller_function_s_own_parameter"
B_LOOP = "a_loop_or_with_target"
B_BRANCH = "a_binding_inside_a_branch_the_call_does_not_sit_in"
B_REBOUND = "a_name_that_is_rebound_before_the_call"
B_NON_LITERAL = "a_non_literal_expression_the_caller_binds"
B_MODULE_ONLY = "a_name_that_only_the_module_scope_binds"
B_UNBOUND = "a_name_no_scope_of_the_caller_binds"
B_NOT_A_NAME = "not_a_plain_name"
BINDING_VOCAB = (B_LITERAL, B_MODULE_CONSTANT, B_CALL, B_CALLER_PARAM, B_LOOP, B_BRANCH, B_REBOUND,
                 B_NON_LITERAL, B_MODULE_ONLY, B_UNBOUND, B_NOT_A_NAME)

# --- per-arm outcome --------------------------------------------------------------------------
A_SETTLED_EXCLUDED = "the_arm_is_excluded_by_the_literal_the_caller_binds_one_hop_out"
A_SETTLED_GUARANTEED = "the_arm_is_reached_by_the_falsy_literal_the_caller_binds_one_hop_out"
A_STRUCTURAL = "the_arm_s_guard_names_no_parameter_so_no_argument_can_settle_it"
A_CALL_RESULT = "the_argument_is_a_call_result_so_the_value_is_one_hop_further_away"
A_CALLER_PARAM = "the_argument_is_the_caller_s_own_parameter_so_the_value_moved_one_scope_out"
A_LOOP = "the_argument_is_a_loop_or_with_target"
A_BRANCH = "the_deciding_binding_sits_inside_a_branch_the_call_does_not_sit_in"
A_REBOUND = "the_deciding_name_is_rebound_before_the_call"
A_NON_LITERAL = "the_binding_is_not_a_literal"
A_MODULE_ONLY = "only_the_module_scope_binds_the_name"
A_UNBOUND = "the_name_has_no_binding_anywhere_in_the_caller"
A_NOT_A_NAME = "the_argument_is_not_a_plain_name"
A_LITERAL_AT_CALL = "the_call_site_itself_passes_a_literal_so_E521_should_not_have_left_it_open"
ARM_OUTCOME_VOCAB = (A_SETTLED_EXCLUDED, A_SETTLED_GUARANTEED, A_STRUCTURAL, A_CALL_RESULT,
                     A_CALLER_PARAM, A_LOOP, A_BRANCH, A_REBOUND, A_NON_LITERAL, A_MODULE_ONLY,
                     A_UNBOUND, A_NOT_A_NAME, A_LITERAL_AT_CALL)
SETTLED = (A_SETTLED_EXCLUDED, A_SETTLED_GUARANTEED)

# --- per-site outcome ---------------------------------------------------------------------------
S_DECIDABLE = "every_undecided_arm_of_the_site_is_settled_by_a_literal_one_hop_out"
S_PARTLY = "some_arms_are_settled_and_at_least_one_is_still_open"
S_STRUCTURAL = "every_undecided_arm_sits_behind_a_test_that_names_no_parameter_of_the_callee"
S_STILL_OPEN = "the_arms_name_parameters_but_following_them_does_not_settle_any_of_them"
SITE_OUTCOME_VOCAB = (S_DECIDABLE, S_PARTLY, S_STRUCTURAL, S_STILL_OPEN)

# --- verdicts ------------------------------------------------------------------------------------
V_EMPTY = "no_site_in_the_population"
V_SOME_DECIDABLE = "following_the_argument_settles_at_least_one_arm_but_not_all_of_them"
V_NONE_DECIDABLE = "following_the_argument_settles_none_of_the_arms_that_name_a_parameter"
V_ALL_STRUCTURAL = ("every_undecided_arm_sits_behind_a_test_that_names_no_parameter_of_the_callee_"
                    "so_no_argument_can_settle_any_of_them")
VERDICT_VOCAB = (V_EMPTY, V_SOME_DECIDABLE, V_NONE_DECIDABLE, V_ALL_STRUCTURAL)


def _now():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _is_self(name):
    return any(name.startswith(prefix) or prefix in name for prefix in SELF_EXCLUDED)


# ------------------------------------------------------------------ population
def load_parent(root=None):
    root = root or ROOT
    path = os.path.join(root, "results", "state_tilt", PARENT_FACE)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def population(parent):
    """E521's rows whose verdict is exactly 'raises and undecidable from the call site'."""
    rows = []
    for site in parent.get("sites", []):
        if site.get("verdict") == e521.V_RAISES_UNDECIDED:
            rows.append(site)
    return rows


# ------------------------------------------------------------------ callee side
def _guard_parameter(stack, test_of, names, kwonly):
    """The parameter the first parameter-naming `if` on this arm's control stack reads."""
    params = set(names + kwonly)
    for node in [c for c in stack if isinstance(c, ast.If)]:
        test = test_of.get(id(node))
        if test is None:
            continue
        hits = e521._names_in(test) & params
        if not hits:
            return None
        return sorted(hits)[0]
    return None


def callee_arms(root, rel, name, lineno, call_expr):
    """E521's arm census, with the parameter each arm's guard reads published beside it."""
    tree = e521.parse_file(root, rel)
    if tree is None:
        return None, "callee_source_does_not_parse"
    fn = e521.find_function(tree, name, lineno)
    if fn is None:
        return None, "callee_not_found_in_its_own_source"

    names, kwonly = e521.parameter_names(fn)
    posargs, kwargs = e521.call_arguments(call_expr)
    posargs = posargs or []
    kwargs = kwargs or {}
    test_of = {id(n): n.test for n in ast.walk(fn) if isinstance(n, ast.If)}

    arms = []
    for node, stack in e521.walk_own(fn, None):
        kind = e521.return_kind(node)
        if not kind:
            continue
        reach = e521.arm_reachability(kind, stack, test_of, posargs, kwargs, names, kwonly)
        arms.append({
            "kind": kind,
            "line": node.lineno,
            "reach": reach,
            "parameter": _guard_parameter(stack, test_of, names, kwonly),
        })
    if not e521.always_terminates(fn.body):
        arms.append({"kind": e521.ARM_IMPLICIT_FALLTHROUGH, "line": fn.lineno,
                     "reach": e521.REACH_UNCONDITIONAL, "parameter": None})
    return {"arms": arms, "names": names, "kwonly": kwonly}, None


# ------------------------------------------------------------------ caller side
def _parent_map(fn):
    parents = {}
    for node in ast.walk(fn):
        for child in ast.iter_child_nodes(node):
            parents[id(child)] = node
    return parents


def _in_branch(node, parents, stop):
    """Is this node inside an If/For/While/Try that is not the function body itself?"""
    cur = node
    while id(cur) in parents:
        cur = parents[id(cur)]
        if cur is stop:
            return False
        if isinstance(cur, (ast.If, ast.For, ast.While, ast.AsyncFor, ast.Try)):
            return True
    return False


def _bound_names(target):
    out = []
    if isinstance(target, ast.Name):
        out.append(target.id)
    elif isinstance(target, (ast.Tuple, ast.List)):
        for elt in target.elts:
            out.extend(_bound_names(elt))
    elif isinstance(target, ast.Starred):
        out.extend(_bound_names(target.value))
    return out


def _bindings(fn):
    """Every (name, line, node, value_kind, value_node) binding inside this function's own body."""
    out = []

    def visit(node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    for name in _bound_names(target):
                        out.append((name, child.lineno, child, "assign", child.value))
            elif isinstance(child, ast.AnnAssign) and child.value is not None:
                for name in _bound_names(child.target):
                    out.append((name, child.lineno, child, "assign", child.value))
            elif isinstance(child, ast.AugAssign):
                for name in _bound_names(child.target):
                    out.append((name, child.lineno, child, "augassign", child.value))
            elif isinstance(child, ast.NamedExpr):
                for name in _bound_names(child.target):
                    out.append((name, child.lineno, child, "assign", child.value))
            elif isinstance(child, (ast.For, ast.AsyncFor)):
                for name in _bound_names(child.target):
                    out.append((name, child.lineno, child, "loop", None))
            elif isinstance(child, (ast.With, ast.AsyncWith)):
                for item in child.items:
                    if item.optional_vars is not None:
                        for name in _bound_names(item.optional_vars):
                            out.append((name, child.lineno, child, "with", item.context_expr))
            visit(child)

    for arg in list(getattr(fn.args, "posonlyargs", [])) + list(fn.args.args) + \
            list(fn.args.kwonlyargs) + ([fn.args.vararg] if fn.args.vararg else []) + \
            ([fn.args.kwarg] if fn.args.kwarg else []):
        out.append((arg.arg, -1, fn, "parameter", None))
    visit(fn)
    return out


def _module_literals(tree):
    """Module-level `NAME = <literal>` (plus one hop of `NAME = OTHER`) -> (literal_text, truthiness)."""
    consts = {}
    pending = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
                isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if e521.literal_class(node.value) != "not_a_literal":
                consts[name] = (ast.unparse(node.value), e521.literal_class(node.value))
            elif isinstance(node.value, ast.Name):
                pending.append((name, node.value.id))
    for name, other in pending:
        if other in consts:
            consts[name] = consts[other]
    return consts


def _module_bindings(tree):
    """What the module scope itself binds: literal constants, other values, imports, defs."""
    bound = {}

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound.setdefault(node.name, ("def", None, None))
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                name = (alias.asname or alias.name).split(".")[0]
                bound.setdefault(name, ("import", None, None))
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                for name in _bound_names(target):
                    truth = e521.literal_class(node.value)
                    if truth != "not_a_literal":
                        bound.setdefault(name, ("literal", ast.unparse(node.value), truth))
                    else:
                        bound.setdefault(name, ("value", node.value, None))
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            for name in _bound_names(node.target):
                truth = e521.literal_class(node.value)
                if truth != "not_a_literal":
                    bound.setdefault(name, ("literal", ast.unparse(node.value), truth))
                else:
                    bound.setdefault(name, ("value", node.value, None))
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            for name in _bound_names(node.target):
                bound.setdefault(name, ("loop", None, None))
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                if item.optional_vars is not None:
                    for name in _bound_names(item.optional_vars):
                        bound.setdefault(name, ("with", item.context_expr, None))
    return bound


def _argument_node(call_expr, parameter, names):
    try:
        call = ast.parse(call_expr, mode="eval").body
    except Exception:
        return None, "the_call_site_does_not_parse"
    if not isinstance(call, ast.Call):
        return None, "the_call_site_is_not_a_call"
    for kw in call.keywords:
        if kw.arg == parameter:
            return kw.value, None
    if parameter in names:
        idx = names.index(parameter)
        if idx < len(call.args) and not isinstance(call.args[idx], ast.Starred):
            return call.args[idx], None
    return None, "the_parameter_is_not_supplied_at_the_call_site"


def resolve_argument(root, caller_rel, line, call_expr, arm, names):
    """Follow the argument for one arm's guard parameter exactly one hop into the caller."""
    node, err = _argument_node(call_expr, arm["parameter"], names)
    if node is None:
        return {"argument_expression": None, "binding_class": B_NOT_A_NAME,
                "arm_outcome": A_NOT_A_NAME, "note": err}
    expression = ast.unparse(node)
    if not isinstance(node, ast.Name):
        if e521.literal_class(node) != "not_a_literal":
            return {"argument_expression": expression, "binding_class": B_NOT_A_NAME,
                    "arm_outcome": A_LITERAL_AT_CALL, "literal_text": expression}
        return {"argument_expression": expression, "binding_class": B_NOT_A_NAME,
                "arm_outcome": A_NOT_A_NAME}
    name = node.id

    tree = e521.parse_file(root, caller_rel)
    if tree is None:
        return {"argument_expression": expression, "binding_class": B_UNBOUND,
                "arm_outcome": A_UNBOUND, "note": "the_caller_does_not_parse"}
    fn = None
    for cand in ast.walk(tree):
        if isinstance(cand, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(cand, "end_lineno", cand.lineno)
            if cand.lineno <= line <= end and (fn is None or cand.lineno > fn.lineno):
                fn = cand
    if fn is None:
        return {"argument_expression": expression, "binding_class": B_MODULE_ONLY,
                "arm_outcome": A_MODULE_ONLY, "note": "the_call_site_sits_at_module_scope"}

    bindings = [b for b in _bindings(fn) if b[0] == name]
    names_bound_before = [b for b in bindings if b[1] < line]
    if not names_bound_before:
        if bindings:
            return {"argument_expression": expression, "binding_class": B_BRANCH,
                    "arm_outcome": A_BRANCH, "note": "every_binding_sits_after_the_call"}
        # nothing in the caller function binds it: the module scope may still do so
        module_bindings = _module_bindings(tree)
        if name in module_bindings:
            kind, payload, truth = module_bindings[name]
            if kind == "literal":
                return {"argument_expression": expression, "binding_class": B_MODULE_CONSTANT,
                        "arm_outcome": (A_SETTLED_GUARANTEED if truth == "falsy_literal"
                                        else A_SETTLED_EXCLUDED),
                        "literal_text": payload, "literal_truth": truth,
                        "note": "bound_at_module_scope"}
            return {"argument_expression": expression, "binding_class": B_MODULE_ONLY,
                    "arm_outcome": A_MODULE_ONLY, "module_binding": kind}
        return {"argument_expression": expression, "binding_class": B_UNBOUND,
                "arm_outcome": A_UNBOUND}

    params = [b for b in names_bound_before if b[3] == "parameter"]
    if params:
        return {"argument_expression": expression, "binding_class": B_CALLER_PARAM,
                "arm_outcome": A_CALLER_PARAM}

    nearest = max((b for b in names_bound_before if b[3] != "parameter"), key=lambda b: b[1])
    kind = nearest[3]
    parents = _parent_map(fn)
    if kind in ("loop", "with"):
        return {"argument_expression": expression, "binding_class": B_LOOP, "arm_outcome": A_LOOP}

    if len([b for b in names_bound_before if b[3] != "parameter"]) > 1:
        return {"argument_expression": expression, "binding_class": B_REBOUND,
                "arm_outcome": A_REBOUND,
                "binding_text": ast.unparse(nearest[4]) if nearest[4] is not None else None}

    if _in_branch(nearest[2], parents, fn):
        return {"argument_expression": expression, "binding_class": B_BRANCH,
                "arm_outcome": A_BRANCH}

    value = nearest[4]
    truth = e521.literal_class(value) if value is not None else "not_a_literal"
    if truth != "not_a_literal":
        return {"argument_expression": expression, "binding_class": B_LITERAL,
                "arm_outcome": (A_SETTLED_GUARANTEED if truth == "falsy_literal"
                                else A_SETTLED_EXCLUDED),
                "literal_text": ast.unparse(value), "literal_truth": truth}
    if isinstance(value, (ast.Name, ast.Attribute)):
        consts = _module_literals(tree)
        if isinstance(value, ast.Name) and value.id in consts:
            text, truth = consts[value.id]
            return {"argument_expression": expression, "binding_class": B_MODULE_CONSTANT,
                    "arm_outcome": (A_SETTLED_GUARANTEED if truth == "falsy_literal"
                                    else A_SETTLED_EXCLUDED),
                    "literal_text": text, "literal_truth": truth}
    if isinstance(value, ast.Call):
        return {"argument_expression": expression, "binding_class": B_CALL, "arm_outcome": A_CALL_RESULT}
    return {"argument_expression": expression, "binding_class": B_NON_LITERAL,
            "arm_outcome": A_NON_LITERAL}


# ------------------------------------------------------------------ per-site analysis
def _site_outcome(arms):
    settled = [a for a in arms if a["arm_outcome"] in SETTLED]
    structural = [a for a in arms if a["arm_outcome"] == A_STRUCTURAL]
    if len(settled) == len(arms):
        return S_DECIDABLE
    if settled:
        return S_PARTLY
    if len(structural) == len(arms):
        return S_STRUCTURAL
    return S_STILL_OPEN


def analyse_site(site, root=None):
    root = root or ROOT
    call_expr = site.get("call_expression") or ""
    census, err = callee_arms(root, site["callee_rel"], site["callee"], site["callee_line"], call_expr)

    row = {
        "source": site["source"],
        "line": site["line"],
        "call_expression": call_expr,
        "callee": site["callee"],
        "callee_rel": site["callee_rel"],
        "callee_line": site["callee_line"],
        "read_kind": site.get("read_kind"),
        "e521_verdict": site.get("verdict"),
        "error": err,
        "arms": [],
        "site_outcome": None,
        "parameters_followed": [],
    }
    if census is None:
        row["site_outcome"] = S_STILL_OPEN
        return row

    undecided = [a for a in census["arms"] if a["reach"] in (ARM_FOLLOWABLE, ARM_STRUCTURAL)]
    # every undecided arm E521 published must show up here with the same reach class
    published = site.get("arm_reaches")
    if isinstance(published, list) and sorted(a["reach"] for a in census["arms"]) != sorted(published):
        row["error"] = "the_arm_census_does_not_reproduce_E521_s_published_reaches"

    for arm in undecided:
        entry = {
            "kind": arm["kind"],
            "line": arm["line"],
            "arm_class": ARM_CLASS_OF.get(arm["reach"]),
            "parameter": arm["parameter"],
        }
        if arm["reach"] == ARM_STRUCTURAL:
            entry["arm_outcome"] = A_STRUCTURAL
        else:
            if arm["parameter"] is None:
                entry["arm_outcome"] = A_STRUCTURAL
                entry["note"] = "the_guard_names_a_parameter_but_none_resolved"
            else:
                entry.update(resolve_argument(root, site["source"], site["line"], call_expr, arm,
                                             census["names"]))
                if arm["parameter"] not in row["parameters_followed"]:
                    row["parameters_followed"].append(arm["parameter"])
        row["arms"].append(entry)

    row["site_outcome"] = _site_outcome(row["arms"]) if row["arms"] else S_STILL_OPEN
    return row


# ------------------------------------------------------------------ summary / verdict
def _count(rows, key):
    out = {}
    for row in rows:
        value = row.get(key)
        label = "not_applicable" if value is None else str(value)
        out[label] = out.get(label, 0) + 1
    return dict(sorted(out.items()))


def _summary(rows, sources):
    arm_rows = [a for r in rows for a in r["arms"]]
    return {
        "sites_examined": len(rows),
        "arms_examined": len(arm_rows),
        "sites_by_outcome": _count(rows, "site_outcome"),
        "arms_by_class": _count(arm_rows, "arm_class"),
        "arms_by_outcome": _count(arm_rows, "arm_outcome"),
        "arms_by_binding_class": _count(arm_rows, "binding_class"),
        "sites_whose_arms_are_settled_entirely": sum(1 for r in rows if r["site_outcome"] == S_DECIDABLE),
        "sites_partly_settled": sum(1 for r in rows if r["site_outcome"] == S_PARTLY),
        "sites_where_no_parameter_can_ever_settle_the_arm": sum(
            1 for r in rows if r["site_outcome"] == S_STRUCTURAL),
        "sites_still_open_after_the_hop": sum(1 for r in rows if r["site_outcome"] == S_STILL_OPEN),
        "arms_settled": sum(1 for a in arm_rows if a["arm_outcome"] in SETTLED),
        "arms_settled_by_a_literal_the_caller_binds": sum(
            1 for a in arm_rows if a.get("binding_class") in (B_LITERAL, B_MODULE_CONSTANT)
            and a["arm_outcome"] in SETTLED),
        "arms_that_no_argument_can_settle": sum(
            1 for a in arm_rows if a["arm_outcome"] == A_STRUCTURAL),
        "arms_with_an_error": sum(1 for r in rows if r["error"]),
        "distinct_callees": len(set((r["callee_rel"], r["callee"]) for r in rows)),
        "distinct_parameters_followed": len(set(p for r in rows for p in r["parameters_followed"])),
        "sources_read": sources,
    }


def _verdict(summary):
    if not summary["sites_examined"]:
        return V_EMPTY
    if summary["arms_settled"]:
        return V_SOME_DECIDABLE
    if summary["arms_that_no_argument_can_settle"] == summary["arms_examined"]:
        return V_ALL_STRUCTURAL
    return V_NONE_DECIDABLE


def corpus_files(root=None):
    root = root or ROOT
    seen = set()
    for sub in ("scripts", "Tools", "firm", "live", "monitor"):
        base = os.path.join(root, sub)
        for dirpath, _dirs, filenames in os.walk(base):
            for name in filenames:
                if name.endswith(".py") and not _is_self(name):
                    seen.add(os.path.relpath(os.path.join(dirpath, name), root))
    return sorted(seen)


# ------------------------------------------------------------------ build / gate
def build(root=None, write=True, rows=None, sources=None, parent=None):
    root = root or ROOT
    if rows is None:
        parent = parent or load_parent(root)
        rows = [analyse_site(site, root) for site in population(parent)]
        if sources is None:
            sources = len(corpus_files(root))
    summary = _summary(rows, sources or 0)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("which of E521's undecidable arms becomes decidable when the guard's argument is "
                  "followed one hop into the caller"),
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": ("%s::population() -- E521's published sites whose verdict is exactly "
                              "'raises and the arm's reachability is not decidable from the call "
                              "site'" % os.path.basename(__file__)),
        "parent_face": PARENT_FACE,
        "method_limits": [
            "one hop only: a name the caller binds from a call result or from its own parameter is "
            "published as still open rather than followed further",
            "a literal binding is accepted only when it dominates the call -- a binding inside an "
            "if/for/while/try that the call does not itself sit in, and a name bound more than once "
            "before the call, both stay open",
            "the guard parameter is taken from the same first-parameter-naming `if` walk E521 used, "
            "so a parameter published here is the parameter E521's reach class named",
            "an arm behind a test that names no parameter of the callee is published as structural: "
            "following an argument cannot settle an arm that does not read the call",
            "a name the caller function never binds is looked up once in the module scope: a "
            "module-level literal settles the arm, any other module binding is published as "
            "module-scope-only rather than as an unbound name",
            "nothing is executed and no source is rewritten",
            "sources_read is a snapshot of a live tree other lanes write to; it is published but not "
            "gated, while every class, every outcome and the verdict are re-derived",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "arm_class_vocab": list(ARM_CLASS_OF.values()),
        "binding_vocab": list(BINDING_VOCAB),
        "arm_outcome_vocab": list(ARM_OUTCOME_VOCAB),
        "site_outcome_vocab": list(SITE_OUTCOME_VOCAB),
        "sites": rows,
    }
    if write:
        write_face(face, root)
    return face


def write_face(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    text = json.dumps(face, ensure_ascii=False, indent=1) + "\n"
    for path in (os.path.join(outdir, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP)),
                 os.path.join(outdir, FACE_NAME)):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    return text


def load_face(root=None):
    root = root or ROOT
    path = os.path.join(root, "results", "state_tilt", FACE_NAME)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def face_problems(face):
    """Recompute every class, every count and the verdict from the published rows."""
    problems = []
    rows = face.get("sites") or []
    summary = face.get("summary") or {}
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict %r is not in its own vocabulary" % (face.get("verdict"),))
    if summary.get("sites_examined") != len(rows):
        problems.append("sites_examined %r does not equal the published rows %d"
                        % (summary.get("sites_examined"), len(rows)))
    arms = [a for r in rows for a in r["arms"]]
    if summary.get("arms_examined") != len(arms):
        problems.append("arms_examined %r does not equal the published arms %d"
                        % (summary.get("arms_examined"), len(arms)))
    if summary.get("sites_by_outcome") != _count(rows, "site_outcome"):
        problems.append("sites_by_outcome does not re-derive")
    if summary.get("arms_by_outcome") != _count(arms, "arm_outcome"):
        problems.append("arms_by_outcome does not re-derive")
    if summary.get("arms_by_class") != _count(arms, "arm_class"):
        problems.append("arms_by_class does not re-derive")
    if summary.get("arms_by_binding_class") != _count(arms, "binding_class"):
        problems.append("arms_by_binding_class does not re-derive")
    if summary.get("arms_settled") != sum(1 for a in arms if a["arm_outcome"] in SETTLED):
        problems.append("arms_settled does not re-derive from the arm outcomes")
    if summary.get("arms_that_no_argument_can_settle") != sum(
            1 for a in arms if a["arm_outcome"] == A_STRUCTURAL):
        problems.append("arms_that_no_argument_can_settle does not re-derive")
    if _verdict(summary) != face.get("verdict"):
        problems.append("the verdict does not re-derive from the summary")

    for row in rows:
        where = "%s:%s" % (row.get("source"), row.get("line"))
        if row.get("site_outcome") not in SITE_OUTCOME_VOCAB:
            problems.append("%s: site_outcome %r is not in its vocabulary"
                            % (where, row.get("site_outcome")))
        if len(row.get("arms") or []) > 0 and row["site_outcome"] != _site_outcome(row["arms"]):
            problems.append("%s: the site outcome does not re-derive from its arms" % where)
        for arm in row["arms"]:
            if arm.get("arm_class") not in ARM_CLASS_OF.values():
                problems.append("%s: arm_class %r is not in its vocabulary"
                                % (where, arm.get("arm_class")))
            if arm.get("arm_outcome") not in ARM_OUTCOME_VOCAB:
                problems.append("%s: arm_outcome %r is not in its vocabulary"
                                % (where, arm.get("arm_outcome")))
            if arm.get("arm_class") == ARM_CLASS_OF[ARM_STRUCTURAL] and \
                    arm.get("arm_outcome") != A_STRUCTURAL:
                problems.append("%s: a structural arm was published as %r"
                                % (where, arm.get("arm_outcome")))
            if arm.get("arm_outcome") in SETTLED:
                if not arm.get("literal_text"):
                    problems.append("%s: a settled arm carries no literal text" % where)
                if arm.get("binding_class") not in (B_LITERAL, B_MODULE_CONSTANT):
                    problems.append("%s: a settled arm is not bound by a literal" % where)
            if arm.get("arm_outcome") == A_LITERAL_AT_CALL:
                problems.append("%s: the call site passes a literal, so it is not this population"
                                % where)
    return problems


def check(face=None, root=None):
    face = face if face is not None else load_face(root)
    problems = face_problems(face)
    print(json.dumps({"study": STUDY, "face": FACE_NAME, "problems": problems,
                      "verdict": face.get("verdict"),
                      "sites": len(face.get("sites") or [])}, ensure_ascii=False, indent=1))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    live = build(root, write=False)
    published = load_face(root)
    problems = face_problems(live)
    if live.get("sites") != published.get("sites"):
        live_by = {(r["source"], r["line"], r["callee"]): r for r in live["sites"]}
        pub_by = {(r["source"], r["line"], r["callee"]): r for r in published["sites"]}
        missing = sorted(set(live_by) - set(pub_by))
        extra = sorted(set(pub_by) - set(live_by))
        if missing:
            problems.append("the published face is missing %d live sites, e.g. %r"
                            % (len(missing), missing[:3]))
        if extra:
            problems.append("the published face carries %d sites that no longer reproduce, e.g. %r"
                            % (len(extra), extra[:3]))
        for key in sorted(set(live_by) & set(pub_by)):
            if live_by[key] != pub_by[key]:
                problems.append("site %r re-derives differently (published %r, live %r)"
                                % (key, pub_by[key].get("site_outcome"),
                                   live_by[key].get("site_outcome")))
    if live.get("verdict") != published.get("verdict"):
        problems.append("the verdict re-derives to %r, the face publishes %r"
                        % (live.get("verdict"), published.get("verdict")))
    print(json.dumps({"study": STUDY, "problems": problems, "verdict": live.get("verdict"),
                      "sites_live": len(live["sites"]),
                      "sites_published": len(published["sites"])},
                     ensure_ascii=False, indent=1))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
FIXTURE_CALLEE = '''\
"""fixture callee."""


def pick(x, mode=None):
    if not x:
        return None
    return {"v": x}


def behind_state(x):
    if FLAG:
        return None
    return {"v": x}
'''

FIXTURE_CALLER = '''\
"""fixture caller."""

EMPTY = []
FULL = [1, 2]
SETTINGS = load_settings()


def lit_truthy(arg):
    box_t = [3]
    got = pick(box_t)
    return got["v"]


def lit_falsy(arg):
    box_f = EMPTY
    got = pick(box_f)
    return got["v"]


def module_const(arg):
    got = pick(FULL)
    return got["v"]


def module_only(arg):
    got = pick(SETTINGS)
    return got["v"]


def call_result(arg):
    box_c = build(arg)
    got = pick(box_c)
    return got["v"]


def caller_param(arg):
    got = pick(arg)
    return got["v"]


def loop_target(items):
    for box_l in items:
        got = pick(box_l)
    return got["v"]


def branch_binding(flag):
    if flag:
        box_b = [1]
        got = pick(box_b)
        return got["v"]
    return None


def rebound(arg):
    box_r = [1]
    box_r = arg
    got = pick(box_r)
    return got["v"]


def not_a_name(arg):
    got = pick(arg or [])
    return got["v"]


def structural(arg):
    box_s = [1]
    got = behind_state(box_s)
    return got["v"]


def build(arg):
    return [arg]
'''


def _site(source, line, callee, callee_line, call_expr):
    return {
        "source": source, "line": line, "callee": callee, "callee_rel": "fixture_callee.py",
        "callee_line": callee_line, "call_expression": call_expr,
        "read_kind": "subscripted", "verdict": e521.V_RAISES_UNDECIDED,
        "arm_reaches": None,
    }


def _fixture_line(text, marker):
    """The 1-based line whose stripped content is exactly `marker` (fixtures carry no line pins)."""
    for idx, line in enumerate(text.splitlines(), start=1):
        if line.strip() == marker:
            return idx
    return None


def selftest():
    bad = []
    tmp = tempfile.mkdtemp(prefix="e527_")
    try:
        for name, text in (("fixture_callee.py", FIXTURE_CALLEE), ("fixture_caller.py", FIXTURE_CALLER)):
            with open(os.path.join(tmp, name), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)

        cases = [
            ("got = pick(box_t)", "pick", 4, S_DECIDABLE, A_SETTLED_EXCLUDED),
            ("got = pick(box_f)", "pick", 4, S_DECIDABLE, A_SETTLED_GUARANTEED),
            ("got = pick(FULL)", "pick", 4, S_DECIDABLE, A_SETTLED_EXCLUDED),
            ("got = pick(SETTINGS)", "pick", 4, S_STILL_OPEN, A_MODULE_ONLY),
            ("got = pick(box_c)", "pick", 4, S_STILL_OPEN, A_CALL_RESULT),
            ("got = pick(arg)", "pick", 4, S_STILL_OPEN, A_CALLER_PARAM),
            ("got = pick(box_l)", "pick", 4, S_STILL_OPEN, A_LOOP),
            ("got = pick(box_b)", "pick", 4, S_STILL_OPEN, A_BRANCH),
            ("got = pick(box_r)", "pick", 4, S_STILL_OPEN, A_REBOUND),
            ("got = pick(arg or [])", "pick", 4, S_STILL_OPEN, A_NOT_A_NAME),
            ("got = behind_state(box_s)", "behind_state", 10, S_STRUCTURAL, A_STRUCTURAL),
        ]
        rows = []
        for marker, callee, callee_line, want_site, want_arm in cases:
            line = _fixture_line(FIXTURE_CALLER, marker)
            if line is None:
                bad.append("fixture marker %r is not in the fixture caller" % marker)
                continue
            call = marker.split("= ", 1)[1]
            row = analyse_site(_site("fixture_caller.py", line, callee, callee_line, call), root=tmp)
            if row["error"]:
                bad.append("%s: %s" % (marker, row["error"]))
                continue
            rows.append(row)
            if row["site_outcome"] != want_site:
                bad.append("%s: site outcome %r != %r" % (marker, row["site_outcome"], want_site))
            got = [a.get("arm_outcome") for a in row["arms"]]
            if got != [want_arm]:
                bad.append("%s: arm outcomes %r != [%r]" % (marker, got, want_arm))

        face = build(tmp, write=False, rows=rows, sources=2)
        problems = face_problems(face)
        if problems:
            bad.append("the fixture face does not gate clean: %r" % (problems[:3],))
        if face["verdict"] != V_SOME_DECIDABLE:
            bad.append("fixture verdict %r != %r" % (face["verdict"], V_SOME_DECIDABLE))
        if face["summary"]["arms_settled"] != 3:
            bad.append("fixture arms_settled %r != 3" % (face["summary"]["arms_settled"],))
        if face["summary"]["arms_that_no_argument_can_settle"] != 1:
            bad.append("fixture structural arms %r != 1"
                       % (face["summary"]["arms_that_no_argument_can_settle"],))

        # doctored faces must be refused
        def doctored(mutate, why):
            doc = json.loads(json.dumps(face))
            mutate(doc)
            if not face_problems(doc):
                bad.append("a doctored face was accepted: %s" % why)

        doctored(lambda d: d.__setitem__("verdict", V_ALL_STRUCTURAL), "hand-written verdict")
        doctored(lambda d: d["summary"].__setitem__(
            "sites_by_outcome", {"x": 1}), "summary counts that do not re-derive")

        def drop_literal_text(d):
            for row in d["sites"]:
                for arm in row["arms"]:
                    if arm["arm_outcome"] in SETTLED:
                        arm.pop("literal_text", None)
        doctored(drop_literal_text, "a settled arm with no literal text")

        def structural_but_open(d):
            for row in d["sites"]:
                for arm in row["arms"]:
                    if arm["arm_class"] == ARM_CLASS_OF[ARM_STRUCTURAL]:
                        arm["arm_outcome"] = A_CALL_RESULT
                        return
        doctored(structural_but_open, "a structural arm published as open")

        def literal_at_call(d):
            for row in d["sites"]:
                for arm in row["arms"]:
                    arm["arm_outcome"] = A_LITERAL_AT_CALL
                    return
        doctored(literal_at_call, "a literal at the call site inside this population")

        def upset_site(d):
            for row in d["sites"]:
                if row["site_outcome"] in (S_DECIDABLE, S_PARTLY):
                    row["site_outcome"] = S_DECIDABLE if row["site_outcome"] == S_PARTLY else S_PARTLY
                    return
        doctored(upset_site, "a site outcome that does not re-derive from its arms")

        def fake_binding(d):
            for row in d["sites"]:
                for arm in row["arms"]:
                    if arm["arm_outcome"] in SETTLED:
                        arm["binding_class"] = B_CALL
                        return
        doctored(fake_binding, "a settled arm bound by a call result")
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    print(json.dumps({"study": STUDY, "selftest": "green" if not bad else "red",
                      "problems": bad}, ensure_ascii=False, indent=1))
    return 0 if not bad else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build()
        print(json.dumps({"face": FACE_NAME, "sites": len(face["sites"]),
                          "verdict": face["verdict"],
                          "summary": face["summary"]}, ensure_ascii=False, indent=1))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print("unknown command %r (build|check|verify|selftest)" % cmd, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())