"""E548 -- how much of E527's whole undecidable population closes once the resolver has the
caller module's own functions and one hop of free-name binding inside call arguments?

E527 published 53 arms over 52 sites (results/state_tilt/UNDECIDABLEARM-2026-11-08.json).  Ten of
those arms name a parameter of the callee and publish the argument expression the caller passes;
the other 43 sit behind a guard that names no parameter at all, so no argument resolver can ever
move them.  E533 carried four of the ten and E545 re-read those four with E536's interpreter plus
two additions.  Nothing has ever priced the two additions over *the population*: "the resolver
cannot settle it" has stayed a sentence about a handful of rows.

This study runs every published arm through four passes and publishes what each addition moves on
its own and together:

  * ``verbatim``   -- E536's interpreter, no additions;
  * ``functions``  -- plus the caller module's own top-level functions in its ``_fn_map``;
  * ``bindings``   -- plus one hop of binding for the free names *inside* the argument expression;
  * ``extended``   -- both additions (this is E545's resolver).

An arm that stays open under ``extended`` is classified by the layer that stopped it, so the
residue is actionable rather than one bucket: a caller parameter with no same-module call site that
folds, a binding that reads module state, a binding that reads the tree, a name the caller never
binds, or a guard that names no parameter at all.

Nothing in this repository is executed -- the tree is read as text and interpreted by E536's
evaluator, and no source is rewritten.

    python scripts/e548_extended_resolver.py build     # write the face
    python scripts/e548_extended_resolver.py check     # gate the published face (fast)
    python scripts/e548_extended_resolver.py verify    # re-derive from the tree and gate
    python scripts/e548_extended_resolver.py selftest  # fixture corpus + doctored faces
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

import e533_call_pure_arm as e533  # noqa: E402
import e536_inlined_fold as e536  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")

CARD = ("E548-HOW-MUCH-OF-THE-WHOLE-UNDECIDABLE-POPULATION-CLOSES-ONCE-THE-RESOLVER-HAS-THE-"
        "CALLER-S-MODULE-AND-BINDS-FREE-NAMES-INSIDE-CALL-ARGUMENTS")
STUDY = "E548_extended_resolver"
DATE_STAMP = "2026-11-08"
FACE_NAME = "extendedresolver_latest.json"
DATED_PREFIX = "EXTENDEDRESOLVER"
PARENT_FACE = "UNDECIDABLEARM-2026-11-08.json"
SELF_EXCLUDED = ("e548_", "run_e548", "_e548", "EXTENDEDRESOLVER", "extendedresolver_")

# --- what one pass produced ---------------------------------------------------------------
R_VALUE = "the_expression_folds_to_a_value"
R_PARAM = "the_expression_is_a_parameter_of_the_caller"
R_UNFOLLOWABLE = "the_expression_reads_something_this_resolver_cannot_follow"
R_ERROR = "the_expression_could_not_be_read"
RESULT_VOCAB = (R_VALUE, R_PARAM, R_UNFOLLOWABLE, R_ERROR)

# --- the four passes ---------------------------------------------------------------------
P_VERBATIM = "verbatim_e536_resolver_with_no_additions"
P_FUNCTIONS = "plus_the_caller_module_s_own_top_level_functions"
P_BINDINGS = "plus_one_hop_binding_of_the_free_names_inside_the_expression"
P_EXTENDED = "plus_both_additions"
PASS_VOCAB = (P_VERBATIM, P_FUNCTIONS, P_BINDINGS, P_EXTENDED)
PASS_KEYS = ("verbatim", "functions", "bindings", "extended")

# --- per-arm outcome ---------------------------------------------------------------------
O_CLOSED_VERBATIM = "the_arm_closes_under_the_unmodified_resolver"
O_CLOSED_BY_FUNCTIONS_ONLY = "the_arm_closes_once_the_caller_s_own_functions_are_in_hand_and_not_before"
O_CLOSED_BY_BINDINGS_ONLY = "the_arm_closes_once_the_free_names_are_bound_one_hop_back_and_not_before"
O_CLOSED_BY_BOTH_TOGETHER = "the_arm_closes_only_when_both_additions_are_present"
O_NO_PARAMETER = "the_guard_names_no_parameter_so_no_argument_resolver_can_move_the_arm"
O_OPEN_PARAM_NO_FOLDING_SITE = "the_expression_is_the_callers_parameter_and_no_same_module_call_site_folds_it"
O_OPEN_PARAM_WITH_FOLDING_SITE = "the_expression_is_the_callers_parameter_and_a_call_site_does_fold_it"
O_OPEN_MODULE_STATE = "a_binding_reads_module_state"
O_OPEN_TREE = "a_binding_reads_the_tree"
O_OPEN_UNBOUND = "a_binding_names_something_the_caller_never_binds"
O_OPEN_OTHER = "a_binding_cannot_be_followed_for_another_reason"
O_UNREADABLE = "the_published_argument_expression_does_not_parse"
OUTCOME_VOCAB = (O_CLOSED_VERBATIM, O_CLOSED_BY_FUNCTIONS_ONLY, O_CLOSED_BY_BINDINGS_ONLY,
                 O_CLOSED_BY_BOTH_TOGETHER, O_NO_PARAMETER, O_OPEN_PARAM_NO_FOLDING_SITE,
                 O_OPEN_PARAM_WITH_FOLDING_SITE, O_OPEN_MODULE_STATE, O_OPEN_TREE, O_OPEN_UNBOUND,
                 O_OPEN_OTHER, O_UNREADABLE)
CLOSED = (O_CLOSED_VERBATIM, O_CLOSED_BY_FUNCTIONS_ONLY, O_CLOSED_BY_BINDINGS_ONLY,
          O_CLOSED_BY_BOTH_TOGETHER)

# the arms E527 itself declared settled by a literal the caller binds one hop out
SETTLED_IN_PARENT = (
    "the_arm_is_excluded_by_the_literal_the_caller_binds_one_hop_out",
    "the_arm_is_reached_by_the_falsy_literal_the_caller_binds_one_hop_out",
)

V_ALL_MOVABLE_CLOSED = "every_arm_that_names_a_parameter_closes_under_the_extended_resolver"
V_SOME_MOVABLE_CLOSED = "some_arms_that_name_a_parameter_close_and_the_rest_stop_at_a_named_layer"
V_NONE_MOVED = "no_arm_that_names_a_parameter_moves_under_any_addition"
V_NO_MOVABLE_ARMS = "no_published_arm_names_a_parameter_so_the_additions_have_nothing_to_move"
VERDICT_VOCAB = (V_ALL_MOVABLE_CLOSED, V_SOME_MOVABLE_CLOSED, V_NONE_MOVED, V_NO_MOVABLE_ARMS)


def _now():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _reason(exc):
    return "%s%s" % (exc.why, (":" + exc.detail) if getattr(exc, "detail", None) else "")


def _text(value):
    try:
        return e533._text(value)[:200]
    except Exception:
        return repr(value)[:200]


# ------------------------------------------------------------------ population
def load_parent(root=None):
    root = root or ROOT
    with open(os.path.join(root, "results", "state_tilt", PARENT_FACE), "r", encoding="utf-8") as fh:
        return json.load(fh)


def population(parent):
    """Every arm E527 published, in published order, with its site attached."""
    rows = []
    for site in parent.get("sites") or []:
        for arm in site.get("arms") or []:
            rows.append({
                "source": site.get("source"),
                "line": site.get("line"),
                "call_expression": site.get("call_expression"),
                "callee": site.get("callee"),
                "callee_rel": site.get("callee_rel"),
                "callee_line": site.get("callee_line"),
                "site_outcome": site.get("site_outcome"),
                "arm_kind": arm.get("kind"),
                "arm_line": arm.get("line"),
                "parameter": arm.get("parameter"),
                "argument_expression": arm.get("argument_expression"),
                "e527_binding_class": arm.get("binding_class"),
                "e527_arm_outcome": arm.get("arm_outcome"),
            })
    return rows


# ------------------------------------------------------------------ the resolver with two switches
def free_names(node):
    out = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load) and sub.id not in out:
            out.append(sub.id)
    return out


def _site_env(root, rel, use_functions):
    env = {}
    if use_functions:
        tree = e536.module_tree(root, rel)
        if tree is not None:
            env["_fn_map"] = e536._top_functions(tree)
    return env


def _top_function_names(root, rel):
    tree = e536.module_tree(root, rel)
    return set() if tree is None else set(e536._top_functions(tree))


def eval_binding(bound, root, rel, bound_line, use_functions, depth, seen):
    """The value of one binding expression, following a same-module call once."""
    if depth > 3:
        raise e536._Uneval("the_binding_chain_is_deeper_than_three_hops")
    if isinstance(bound, ast.Call) and isinstance(bound.func, ast.Name):
        name = bound.func.id
        if name in e533.FOLDERS or name in e536.BUILTIN_NAMES:
            return e536.ev(bound, _site_env(root, rel, use_functions), root, 0)
        env = _site_env(root, rel, use_functions)
        fn = (env.get("_fn_map") or {}).get(name)
        if fn is None:
            raise e536._Uneval("the_binding_calls_a_name_the_resolver_cannot_reach", name)
        if name in seen:
            raise e536._Uneval("the_binding_is_cyclic", name)
        fn._e536_rel = rel
        tree = e536.module_tree(root, rel)
        body_class, _reads = e536.classify_body(fn, tree, root)
        if body_class not in (e536.B_PURE, e536.B_REPO_CALL):
            raise e536._Uneval("the_binding_calls_a_body_classed_%s" % body_class, name)
        args = [eval_expr(a, root, rel, bound_line, use_functions, True, depth + 1, seen | {name})
                for a in bound.args]
        return e536.call_function(fn, args, {}, root)
    return eval_expr(bound, root, rel, bound_line, use_functions, True, depth + 1, seen)


def eval_expr(node, root, rel, line, use_functions, use_bindings, depth=0, seen=frozenset()):
    env = _site_env(root, rel, use_functions)
    try:
        return e536.ev(node, env, root, 0)
    except e536._Uneval as exc:
        first = _reason(exc)
    if not use_bindings:
        raise e536._Uneval("unresolved_under_this_pass", first)
    top_fns = _top_function_names(root, rel) if use_functions else set()
    for name in free_names(node):
        if name in env or name in e536.BUILTIN_NAMES or name in e533.FOLDERS or name in top_fns:
            continue
        kind, bound, bound_line = e536._binding_node(root, rel, line, name)
        if bound is None:
            raise e536._Uneval("the_name_is_the_caller_s_own_parameter" if kind == "parameter"
                               else "no_binding_of_this_name_before_the_site", name)
        if name in seen:
            raise e536._Uneval("the_binding_is_cyclic", name)
        env[name] = eval_binding(bound, root, rel, bound_line, use_functions, depth + 1,
                                 seen | {name})
    return e536.ev(node, env, root, 0)


def binding_records(node, root, rel, line, use_functions):
    """One record per free name in the expression: how the caller binds it, and to what."""
    recs = []
    top_fns = _top_function_names(root, rel) if use_functions else set()
    for name in free_names(node):
        if name in e536.BUILTIN_NAMES or name in e533.FOLDERS or name in top_fns:
            continue
        kind, bound, bound_line = e536._binding_node(root, rel, line, name)
        rec = {"name": name, "binding_kind": kind, "bound_line": bound_line,
               "class": None, "value_text": None, "reason": None, "binding_text": None,
               "calls_tree": False}
        if bound is None:
            rec["class"] = R_PARAM if kind == "parameter" else R_UNFOLLOWABLE
            if kind == "parameter":
                rec["reason"] = "the_name_is_the_caller_s_own_parameter"
            else:
                tree = e536.module_tree(root, rel)
                module_names = e536._module_level_names(tree) if tree is not None else set()
                rec["reason"] = ("the_name_is_bound_only_at_module_scope"
                                 if name in module_names
                                 else "no_binding_of_this_name_before_the_site")
            recs.append(rec)
            continue
        try:
            rec["binding_text"] = ast.unparse(bound)[:160]
        except Exception:
            rec["binding_text"] = None
        rec["calls_tree"] = any(isinstance(sub, ast.Call) and _call_name(sub) in e536.TREE_CALLS
                                for sub in ast.walk(bound))
        try:
            value = eval_binding(bound, root, rel, bound_line, use_functions, 0, frozenset({name}))
            rec["class"] = R_VALUE
            rec["value_text"] = _text(value)
        except e536._Uneval as exc:
            rec["class"] = R_UNFOLLOWABLE
            rec["reason"] = _reason(exc)
        recs.append(rec)
    return recs


def _call_name(call):
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def resolve(node, root, rel, line, use_functions, use_bindings):
    """(class, value, value_text, reason, bindings) for one expression under one pass."""
    if e536.module_tree(root, rel) is None:
        return R_ERROR, None, None, "the_site_s_module_could_not_be_parsed", []
    recs = binding_records(node, root, rel, line, use_functions) if use_bindings else []
    try:
        value = eval_expr(node, root, rel, line, use_functions, use_bindings)
        return R_VALUE, value, _text(value), None, recs
    except e536._Uneval as exc:
        why = _reason(exc)
    if any(r["class"] == R_PARAM for r in recs):
        return R_PARAM, None, None, "a_free_name_in_the_expression_is_the_caller_s_parameter", recs
    stuck = [r for r in recs if r["class"] != R_VALUE]
    if stuck:
        return (R_UNFOLLOWABLE, None, None,
                "%s_binds_to_%s" % (stuck[0]["name"], stuck[0]["reason"]), recs)
    return R_UNFOLLOWABLE, None, None, why, recs


def one_hop_out(root, rel, caller_fn, parameter):
    """The caller's own call sites for one of its parameters, with the argument resolved."""
    out = []
    tree = e536.module_tree(root, rel)
    if tree is None or caller_fn is None:
        return out
    params = e536._param_names(caller_fn)
    if parameter not in params:
        return out
    idx = params.index(parameter)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.id if isinstance(func, ast.Name) else None
        if name != caller_fn.name:
            continue
        if idx >= len(node.args):
            out.append({"site_line": getattr(node, "lineno", 0), "argument_expression": None,
                        "class": R_UNFOLLOWABLE, "value_text": None,
                        "reason": "the_site_does_not_pass_this_positional_argument"})
            continue
        arg = node.args[idx]
        cls, _val, txt, why, _b = resolve(arg, root, rel, getattr(node, "lineno", 0), True, True)
        out.append({"site_line": getattr(node, "lineno", 0),
                    "argument_expression": ast.unparse(arg)[:120],
                    "class": cls, "value_text": txt, "reason": why})
    return sorted(out, key=lambda r: r["site_line"] or 0)


# ------------------------------------------------------------------ one arm
def analyse_arm(arm, root=None):
    root = root or ROOT
    rec = dict(arm)
    rec.update({"verbatim": None, "functions": None, "bindings": None, "extended": None,
                "one_hop_out": [], "caller_parameter": None, "arm_outcome": O_UNREADABLE,
                "residue_layer_reason": None, "error": None})
    if not rec.get("parameter") or not rec.get("argument_expression"):
        rec["arm_outcome"] = O_NO_PARAMETER
        return rec
    try:
        node = ast.parse(rec["argument_expression"], mode="eval").body
    except Exception as exc:
        rec["error"] = "the_published_argument_expression_does_not_parse: %s" % exc
        return rec
    passes = (("verbatim", P_VERBATIM, False, False), ("functions", P_FUNCTIONS, True, False),
              ("bindings", P_BINDINGS, False, True), ("extended", P_EXTENDED, True, True))
    for key, label, use_fns, use_binds in passes:
        cls, _val, txt, why, binds = resolve(node, root, rec["source"], rec["line"],
                                             use_fns, use_binds)
        rec[key] = {"pass": label, "class": cls, "value_text": txt, "reason": why,
                    "bindings": binds if use_binds else []}
    if rec["extended"]["class"] == R_PARAM:
        tree = e536.module_tree(root, rec["source"])
        caller = e533._caller_function(tree, rec["line"]) if tree is not None else None
        caller_param = None
        for bound in rec["extended"].get("bindings") or []:
            if bound.get("binding_kind") == "parameter":
                caller_param = bound["name"]
                break
        rec["caller_parameter"] = caller_param or rec["parameter"]
        rec["one_hop_out"] = one_hop_out(root, rec["source"], caller, rec["caller_parameter"])
    rec["arm_outcome"] = _outcome(rec)
    rec["residue_layer_reason"] = _layer_reason(rec)
    rec["parent_settlement_reproduced"] = (
        None if rec.get("e527_arm_outcome") not in SETTLED_IN_PARENT
        else rec["arm_outcome"] in CLOSED)
    return rec


def _closes(pass_rec):
    return bool(pass_rec) and pass_rec.get("class") == R_VALUE


def _outcome(rec):
    if _closes(rec["verbatim"]):
        return O_CLOSED_VERBATIM
    if _closes(rec["functions"]) and not _closes(rec["bindings"]):
        return O_CLOSED_BY_FUNCTIONS_ONLY
    if _closes(rec["bindings"]) and not _closes(rec["functions"]):
        return O_CLOSED_BY_BINDINGS_ONLY
    if _closes(rec["extended"]):
        return O_CLOSED_BY_BOTH_TOGETHER
    if rec["extended"]["class"] == R_PARAM:
        folding = [s for s in rec.get("one_hop_out") or [] if s.get("class") == R_VALUE]
        return O_OPEN_PARAM_WITH_FOLDING_SITE if folding else O_OPEN_PARAM_NO_FOLDING_SITE
    if rec["extended"]["class"] == R_ERROR:
        return O_UNREADABLE
    recs = rec["extended"].get("bindings") or []
    stuck = [r for r in recs if r.get("class") != R_VALUE]
    if any("body_reads_module_state" in (r.get("reason") or "") or
           "module_state" in (r.get("reason") or "") or
           "module_scope" in (r.get("reason") or "") for r in stuck):
        return O_OPEN_MODULE_STATE
    if any(r.get("calls_tree") or "reads_the_tree" in (r.get("reason") or "") for r in stuck):
        return O_OPEN_TREE
    if any("no_binding_of_this_name" in (r.get("reason") or "") for r in stuck):
        return O_OPEN_UNBOUND
    return O_OPEN_OTHER


def _layer_reason(rec):
    if rec["arm_outcome"] in CLOSED:
        return None
    if rec["arm_outcome"] == O_NO_PARAMETER:
        return "the_guard_names_no_parameter_of_the_callee"
    stuck = [r for r in (rec["extended"].get("bindings") or []) if r.get("class") != R_VALUE]
    if stuck:
        return "%s_binds_to_%s" % (stuck[0]["name"], stuck[0].get("reason"))
    return (rec["extended"].get("reason")
            if rec.get("extended") else rec.get("error"))


# ------------------------------------------------------------------ summary / verdict
def _count(rows, key):
    out = {}
    for row in rows:
        val = row.get(key)
        out[val] = out.get(val, 0) + 1
    return out


def _summary(rows):
    movable = [r for r in rows if r["arm_outcome"] != O_NO_PARAMETER]
    closed = [r for r in rows if r["arm_outcome"] in CLOSED]
    return {
        "arms_in_parent": len(rows),
        "arms_that_name_a_parameter": len(movable),
        "arms_without_a_parameter": len(rows) - len(movable),
        "arms_closed": len(closed),
        "arms_closed_verbatim": sum(1 for r in rows if r["arm_outcome"] == O_CLOSED_VERBATIM),
        "arms_closed_by_functions_alone": sum(1 for r in rows
                                              if r["arm_outcome"] == O_CLOSED_BY_FUNCTIONS_ONLY),
        "arms_closed_by_bindings_alone": sum(1 for r in rows
                                             if r["arm_outcome"] == O_CLOSED_BY_BINDINGS_ONLY),
        "arms_closed_by_both_together": sum(1 for r in rows
                                            if r["arm_outcome"] == O_CLOSED_BY_BOTH_TOGETHER),
        "arms_still_open": len(rows) - len(closed),
        "arms_by_outcome": _count(rows, "arm_outcome"),
        "verbatim_by_class": _count([r["verbatim"] or {} for r in rows if r["verbatim"]], "class"),
        "functions_by_class": _count([r["functions"] or {} for r in rows if r["functions"]], "class"),
        "bindings_by_class": _count([r["bindings"] or {} for r in rows if r["bindings"]], "class"),
        "extended_by_class": _count([r["extended"] or {} for r in rows if r["extended"]], "class"),
        "arms_whose_call_sites_fold": sum(1 for r in rows if r["arm_outcome"] == O_OPEN_PARAM_WITH_FOLDING_SITE),
        "call_sites_published": sum(len(r["one_hop_out"]) for r in rows),
        "sites_in_parent": len({(r["source"], r["line"]) for r in rows}),
        "arms_the_parent_declared_settled": sum(1 for r in rows
                                                if r.get("parent_settlement_reproduced") is not None),
        "parent_settlements_this_resolver_reproduces": sum(
            1 for r in rows if r.get("parent_settlement_reproduced") is True),
        "parent_settlements_this_resolver_leaves_open": sum(
            1 for r in rows if r.get("parent_settlement_reproduced") is False),
        "arms_the_parent_declared_settled_by_a_module_level_constant": sum(
            1 for r in rows if r.get("parent_settlement_reproduced") is False
            and r["arm_outcome"] == O_OPEN_MODULE_STATE),
    }


def _verdict(summary):
    if not summary["arms_that_name_a_parameter"]:
        return V_NO_MOVABLE_ARMS
    if summary["arms_closed"] == summary["arms_that_name_a_parameter"]:
        return V_ALL_MOVABLE_CLOSED
    if summary["arms_closed"] == 0:
        return V_NONE_MOVED
    return V_SOME_MOVABLE_CLOSED


def build(root=None, write=True, rows=None, parent=None):
    root = root or ROOT
    if rows is None:
        parent = parent or load_parent(root)
        rows = [analyse_arm(a, root) for a in population(parent)]
    summary = _summary(rows)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("how much of E527's whole published arm population closes once E536's "
                  "interpreter has the caller module's own functions and one hop of free-name "
                  "binding inside the argument expression"),
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": ("%s::population() -- every arm in %s, in published order"
                              % (os.path.basename(__file__), PARENT_FACE)),
        "parent_face": PARENT_FACE,
        "method_limits": [
            "the resolver is E536's interpreter with two switches: the caller module's own "
            "top-level functions in its _fn_map, and one hop of binding for the free names inside "
            "the argument expression; all four combinations are published per arm",
            "an arm whose guard names no parameter is not moved by any argument resolver and is "
            "counted as such rather than folded into the closed fraction",
            "one_hop_out is published only for an arm whose argument is the caller's own "
            "parameter, and only over that caller's call sites in the same module",
            "an item store between a binding and the site is not replayed (E544's subject); a "
            "folding call site makes the arm actionable, it does not make it closed here",
            "the arms E527 itself declared settled are re-checked under this resolver and published as "
            "parent_settlement_reproduced: this resolver refuses to read module state, so a "
            "settlement that rests on a module-level constant is expected to come back open",
            "nothing in this repository is executed and no source is rewritten",
            "a fixture corpus is not a repository: the selftest proves the switches behave as "
            "named, the face is the repository's own reading",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "result_vocab": list(RESULT_VOCAB),
        "pass_vocab": list(PASS_VOCAB),
        "arm_outcome_vocab": list(OUTCOME_VOCAB),
        "arms": rows,
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
    with open(os.path.join(root, "results", "state_tilt", FACE_NAME), "r", encoding="utf-8") as fh:
        return json.load(fh)


def face_problems(face):
    problems = []
    rows = face.get("arms") or []
    summary = face.get("summary") or {}
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict %r is not in its own vocabulary" % (face.get("verdict"),))
    rec = _summary(rows)
    for key in ("arms_in_parent", "arms_that_name_a_parameter", "arms_without_a_parameter",
                "arms_closed", "arms_closed_verbatim", "arms_closed_by_functions_alone",
                "arms_closed_by_bindings_alone", "arms_closed_by_both_together",
                "arms_still_open", "arms_whose_call_sites_fold", "call_sites_published",
                "sites_in_parent", "arms_the_parent_declared_settled",
                "parent_settlements_this_resolver_reproduces",
                "parent_settlements_this_resolver_leaves_open",
                "arms_the_parent_declared_settled_by_a_module_level_constant"):
        if summary.get(key) != rec[key]:
            problems.append("%s does not re-derive (%r vs %r)"
                            % (key, summary.get(key), rec[key]))
    for key in ("arms_by_outcome", "verbatim_by_class", "functions_by_class",
                "bindings_by_class", "extended_by_class"):
        if summary.get(key) != rec[key]:
            problems.append("%s does not re-derive" % key)
    if summary.get("arms_closed") != (summary.get("arms_closed_verbatim", 0) +
                                      summary.get("arms_closed_by_functions_alone", 0) +
                                      summary.get("arms_closed_by_bindings_alone", 0) +
                                      summary.get("arms_closed_by_both_together", 0)):
        problems.append("the closed arms do not add up from the four outcome counters")
    if _verdict(summary) != face.get("verdict"):
        problems.append("the verdict does not re-derive from the summary")
    for row in rows:
        where = "%s:%s" % (row.get("source"), row.get("line"))
        if row.get("arm_outcome") not in OUTCOME_VOCAB:
            problems.append("%s: arm_outcome %r is not in its vocabulary"
                            % (where, row.get("arm_outcome")))
            continue
        for name in PASS_KEYS:
            block = row.get(name)
            if block is None:
                if row.get("arm_outcome") != O_NO_PARAMETER:
                    problems.append("%s: an arm that names a parameter publishes no %s pass"
                                    % (where, name))
                continue
            if block.get("class") not in RESULT_VOCAB:
                problems.append("%s: %s class %r is not in its vocabulary"
                                % (where, name, block.get("class")))
        if row.get("arm_outcome") in CLOSED:
            if not (row.get("extended") or {}).get("value_text"):
                problems.append("%s: a closed arm carries no folded value" % where)
        elif row.get("arm_outcome") != O_NO_PARAMETER:
            if (row.get("extended") or {}).get("value_text"):
                problems.append("%s: an open arm carries a folded value" % where)
            if not row.get("residue_layer_reason"):
                problems.append("%s: an open arm names no residue layer" % where)
        expected = (None if row.get("e527_arm_outcome") not in SETTLED_IN_PARENT
                    else row["arm_outcome"] in CLOSED)
        if row.get("parent_settlement_reproduced") != expected:
            problems.append("%s: parent_settlement_reproduced does not re-derive" % where)
        if row.get("arm_outcome") == O_OPEN_PARAM_NO_FOLDING_SITE:
            folding = [s for s in row.get("one_hop_out") or [] if s.get("class") == R_VALUE]
            if folding:
                problems.append("%s: a no-folding-site arm publishes a folding site" % where)
        for site in row.get("one_hop_out") or []:
            if site.get("class") not in RESULT_VOCAB:
                problems.append("%s: a call site class %r is not in its vocabulary"
                                % (where, site.get("class")))
    return problems


def check(face=None, root=None):
    face = face if face is not None else load_face(root)
    problems = face_problems(face)
    print(json.dumps({"study": STUDY, "face": FACE_NAME, "problems": problems,
                      "verdict": face.get("verdict"), "arms": len(face.get("arms") or []),
                      "summary": face.get("summary")}, ensure_ascii=False, indent=1))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    live = build(root, write=False)
    published = load_face(root)
    problems = face_problems(live)
    if live.get("arms") != published.get("arms"):
        live_by = {(r["source"], r["line"], r.get("arm_line")): r for r in live["arms"]}
        pub_by = {(r["source"], r["line"], r.get("arm_line")): r for r in published["arms"]}
        missing = sorted(set(live_by) - set(pub_by))
        extra = sorted(set(pub_by) - set(live_by))
        if missing:
            problems.append("the published face is missing %d live arms, e.g. %r"
                            % (len(missing), missing[:3]))
        if extra:
            problems.append("the published face carries %d arms that no longer reproduce, e.g. %r"
                            % (len(extra), extra[:3]))
        for key in sorted(set(live_by) & set(pub_by)):
            if live_by[key]["arm_outcome"] != pub_by[key]["arm_outcome"]:
                problems.append("arm %r re-derives to %r, the face publishes %r"
                                % (key, live_by[key]["arm_outcome"],
                                   pub_by[key]["arm_outcome"]))
    if live.get("verdict") != published.get("verdict"):
        problems.append("the verdict re-derives to %r, the face publishes %r"
                        % (live.get("verdict"), published.get("verdict")))
    print(json.dumps({"study": STUDY, "problems": problems, "verdict": live.get("verdict"),
                      "arms_live": len(live["arms"]), "arms_published": len(published["arms"]),
                      "summary": live.get("summary")}, ensure_ascii=False, indent=1))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
FIXTURE = '''\
"""fixture module for E548."""

SCALE = 2


def _td(lo, hi):
    return {"lo": lo + 0.0, "hi": hi + 0.0}


def fixture_arm():
    rows = [{"row": "a", "tight": _td(1.0, 1.1)}]
    return {"rows": rows}


def lit_table():
    return table(list(range(6)))


def interval(rows, tail):
    lows = [r[tail]["lo"] for r in rows]
    highs = [r[tail]["hi"] for r in rows]
    return {"lo": min(lows), "hi": max(highs)}


def table(idxs):
    return {"n": len(idxs)}


def bound_caller():
    idxs = [1, 2]
    return table(idxs)


def param_caller(idxs):
    return table(idxs)


def fills_the_param():
    return param_caller([1, 2])


def read_off_disk(path):
    with open(path) as fh:
        return fh.read()


def tree_caller():
    rows = read_off_disk("x.json")
    return table(rows)


def module_caller():
    return table(SCALE)


def calls_module_reader():
    return table(interval(fixture_arm()["rows"], "tight"))
'''


def _fixture_population():
    return [
        {"source": "fixture.py", "line": 15, "callee": "table", "parameter": "idxs",
         "argument_expression": "list(range(6))", "arm_line": 2, "arm_kind": "a_literal"},
        {"source": "fixture.py", "line": 20, "callee": "table", "parameter": "n",
         "argument_expression": "idxs", "arm_line": 2, "arm_kind": "a_name"},
        {"source": "fixture.py", "line": 34, "callee": "table", "parameter": "idxs",
         "argument_expression": "idxs", "arm_line": 3, "arm_kind": "a_parameter"},
        {"source": "fixture.py", "line": 42, "callee": "table", "parameter": "idxs",
         "argument_expression": "rows", "arm_line": 4, "arm_kind": "a_tree_read"},
        {"source": "fixture.py", "line": 46, "callee": "table", "parameter": "idxs",
         "argument_expression": "SCALE", "arm_line": 5, "arm_kind": "a_module_constant"},
        {"source": "fixture.py", "line": 50, "callee": "table", "parameter": "idxs",
         "argument_expression": "interval(fixture_arm()['rows'], 'tight')",
         "arm_line": 6, "arm_kind": "a_nested_call"},
        {"source": "fixture.py", "line": 50, "callee": "table", "parameter": None,
         "argument_expression": None, "arm_line": 7, "arm_kind": "no_parameter"},
    ]


def _line_of(text_lines, needle):
    for idx, line in enumerate(text_lines, start=1):
        if needle in line:
            return idx
    raise AssertionError("fixture line not found: %r" % needle)


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append({"leg": name, "ok": bool(ok), "detail": str(detail)[:220]})

    root = tempfile.mkdtemp(prefix="e548_selftest_")
    try:
        with open(os.path.join(root, "fixture.py"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(FIXTURE)
        text = FIXTURE.split("\n")
        arms = _fixture_population()
        arms[0]["line"] = _line_of(text, "return table(list(range(6)))")
        arms[1]["line"] = _line_of(text, "idxs = [1, 2]") + 1
        # the caller's own parameter sits in the second `return table(idxs)`; the first one is
        # the name-bound arm above it
        occurrences = [i for i, line in enumerate(text, start=1) if "return table(idxs)" in line]
        arms[2]["line"] = occurrences[1]
        arms[3]["line"] = _line_of(text, "return table(rows)")
        arms[4]["line"] = _line_of(text, "return table(SCALE)")
        arms[5]["line"] = _line_of(text, "return table(interval(")
        arms[6]["line"] = arms[5]["line"]

        rows = [analyse_arm(a, root) for a in arms]
        by_kind = {r["arm_kind"]: r for r in rows}

        leg("a literal argument closes verbatim",
            by_kind["a_literal"]["arm_outcome"] == O_CLOSED_VERBATIM,
            by_kind["a_literal"]["arm_outcome"])
        leg("a name bound one hop back closes under the binding switch only",
            by_kind["a_name"]["arm_outcome"] == O_CLOSED_BY_BINDINGS_ONLY,
            by_kind["a_name"]["arm_outcome"])
        leg("the caller's parameter stays open and publishes its call sites",
            by_kind["a_parameter"]["arm_outcome"] == O_OPEN_PARAM_WITH_FOLDING_SITE
            and len(by_kind["a_parameter"]["one_hop_out"]) >= 1,
            by_kind["a_parameter"]["arm_outcome"])
        leg("a tree read is named as the tree layer",
            by_kind["a_tree_read"]["arm_outcome"] == O_OPEN_TREE,
            by_kind["a_tree_read"]["arm_outcome"])
        leg("a module constant is named as the module-state layer",
            by_kind["a_module_constant"]["arm_outcome"] == O_OPEN_MODULE_STATE,
            by_kind["a_module_constant"]["arm_outcome"])
        leg("a nested call into the caller's own module is not reported as no-parameter",
            by_kind["a_nested_call"]["arm_outcome"] != O_NO_PARAMETER,
            by_kind["a_nested_call"]["arm_outcome"])
        leg("an arm with no parameter is counted, not folded",
            by_kind["no_parameter"]["arm_outcome"] == O_NO_PARAMETER)

        face = build(root, write=False, rows=rows)
        problems = face_problems(face)
        leg("the built face gates clean", problems == [], "; ".join(problems)[:180])
        leg("a summary that outgrows its rows is refused", bool(_doctor(face, "count")))
        leg("a class outside the vocabulary is refused", bool(_doctor(face, "class")))
        leg("an open arm that carries a folded value is refused",
            bool(_doctor(face, "value")))
        leg("a closed counter that does not add up is refused", bool(_doctor(face, "split")))
        leg("a verdict outside the vocabulary is refused", bool(_doctor(face, "verdict")))
    finally:
        try:
            import shutil
            shutil.rmtree(root, ignore_errors=True)
        except Exception:
            pass
    good = sum(1 for l in legs if l["ok"])
    print(json.dumps({"study": STUDY, "selftest": "%d/%d" % (good, len(legs)), "legs": legs},
                     ensure_ascii=False, indent=1))
    return 0 if good == len(legs) else 1


def _doctor(face, kind):
    doc = json.loads(json.dumps(face))
    if kind == "verdict":
        doc["verdict"] = "a_verdict_this_study_never_publishes"
    elif kind == "class":
        for row in doc["arms"]:
            if row.get("extended"):
                row["extended"]["class"] = "a_class_not_published"
                break
    elif kind == "count":
        doc["summary"]["arms_closed"] = 99
    elif kind == "value":
        for row in doc["arms"]:
            if row["arm_outcome"] not in CLOSED:
                row["extended"]["value_text"] = "[1, 2]"
                break
    elif kind == "split":
        doc["summary"]["arms_closed_by_bindings_alone"] += 1
    else:
        raise AssertionError("unknown doctoring %r" % kind)
    return face_problems(doc)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    action = argv[0] if argv else "build"
    if action == "build":
        face = build()
        print(json.dumps({"study": STUDY,
                          "wrote": [FACE_NAME, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP)],
                          "verdict": face["verdict"], "summary": face["summary"]},
                         ensure_ascii=False, indent=1))
        return 0
    if action == "check":
        return check()
    if action == "verify":
        return verify()
    if action == "selftest":
        return selftest()
    print("usage: %s [build|check|verify|selftest]" % os.path.basename(__file__))
    return 2


if __name__ == "__main__":
    sys.exit(main())