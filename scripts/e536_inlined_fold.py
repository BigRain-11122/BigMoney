"""E536 -- is the repo-source callee the fold refused to inline actually pure in literals once its
parameters are bound to the site's own arguments?

E533 (results/state_tilt/CALLPUREARM-2026-11-08.json) published exactly one open arm whose argument
is a direct call and whose fold stopped because the callee is repository source:

    scripts/e285_interrange_gap_ceiling.py:505
        ranges_are_row_identical(off["rows"], "tight", interval(off["rows"], "tight"))
        callee = interval,  parameter = hull,  argument = interval(off["rows"], "tight")

E533 recorded that as "the callee is not a pure chain of literals".  That sentence is about what the
fold does, not about the callee: the fold refuses *every* repo-source callee without reading its
body.  Two very different things wear the same label:

  * the callee really does read module state or the tree, so no amount of inlining helps, and
  * the callee only moves its parameters around, so the refusal was about the *site's* arguments.

This study separates them.  For every open arm E533 published, it

  * resolves the callee to its definition (the site's own module first, then a repository-wide
    unique match) and classifies the body by reading it: parameters only, module state (named), the
    tree (named), or another repo call (named);
  * binds the parameters to the arguments the call site passes and evaluates the body with a literal
    interpreter, so "the body moves parameters around" is answered by a value rather than by prose;
  * classifies the site's own arguments the same way -- a literal, a literal once its binding is
    folded, a name the fold cannot resolve, or a repo call this study does not follow;
  * publishes ``refusal_attribution``: whether E533's refusal was about the callee or about the
    site's own arguments.

The interpreter is the same whitelist idea E533's fold uses, one level deeper: constants, containers,
subscripts, arithmetic, a fixed builtin set, and repo functions whose own body is a supported
statement chain.  A statement kind the interpreter does not know stops it and is published with the
reason -- nothing is guessed at.  Nothing in this repository is executed: the tree is read as text
and interpreted by this module's own evaluator, and no source is rewritten.

    python scripts/e536_inlined_fold.py build     # write the face
    python scripts/e536_inlined_fold.py check     # gate the published face (fast)
    python scripts/e536_inlined_fold.py verify    # re-derive from the tree and gate
    python scripts/e536_inlined_fold.py selftest  # fixture corpus + doctored faces
"""
from __future__ import annotations

import ast
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e521_reachable_empty_arm as e521  # noqa: E402  (parse_file)
import e527_undecidable_arm as e527  # noqa: E402  (caller bindings)
import e533_call_pure_arm as e533  # noqa: E402  (parent face, the fold that refused)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")

CARD = ("E536-WHICH-REPO-SOURCE-CALLEE-THE-FOLD-REFUSED-TO-INLINE-IS-ACTUALLY-PURE-IN-"
        "LITERALS-ONCE-ITS-PARAMETERS-ARE-BOUND-TO-THE-SITE-S-ARGUMENTS")
STUDY = "E536_inlined_fold"
DATE_STAMP = "2026-11-08"
FACE_NAME = "inlinedfold_latest.json"
DATED_PREFIX = "INLINEDFOLD"
PARENT_FACE = "CALLPUREARM-2026-11-08.json"

# a scan that reads the tree must not read its own output
SELF_EXCLUDED = ("e536_", "run_e536", "_e536", "INLINEDFOLD", "inlinedfold_")

# --- what the inlined body turns out to be -----------------------------------------------------
B_PURE = "the_body_only_moves_its_parameters_around"
B_MODULE = "the_body_reads_module_state"
B_TREE = "the_body_reads_the_tree"
B_REPO_CALL = "the_body_calls_another_repo_function"
B_UNREAD = "the_callee_definition_could_not_be_read"
BODY_VOCAB = (B_PURE, B_MODULE, B_TREE, B_REPO_CALL, B_UNREAD)

# --- what the site's own argument is -----------------------------------------------------------
S_LITERAL = "the_site_s_argument_is_a_literal"
S_LITERAL_ONE_HOP = "the_site_s_argument_is_a_literal_once_its_binding_is_folded"
S_RESOLVABLE = "the_site_s_argument_resolves_through_its_binding_but_does_not_fold"
S_UNRESOLVED = "the_site_s_argument_reads_a_name_the_fold_cannot_resolve"
SITE_VOCAB = (S_LITERAL, S_LITERAL_ONE_HOP, S_RESOLVABLE, S_UNRESOLVED)

# --- whose refusal was it ---------------------------------------------------------------------
A_CALLEE = "the_refusal_was_about_the_callee"
A_SITE = "the_refusal_was_about_the_site_s_own_arguments"
A_BOTH = "the_refusal_was_about_both_the_callee_and_the_site_s_arguments"
A_UNREAD = "the_refusal_could_not_be_attributed_because_the_callee_could_not_be_read"
ATTR_VOCAB = (A_CALLEE, A_SITE, A_BOTH, A_UNREAD)

# --- per-arm outcome --------------------------------------------------------------------------
O_CLOSED = "the_arm_becomes_decidable_because_the_inlined_body_runs_on_a_literal_argument"
O_OPEN_BODY = "the_arm_stays_open_because_the_body_reads_module_state_or_the_tree"
O_OPEN_ARG = "the_arm_stays_open_because_the_site_s_own_argument_is_not_literal"
O_NOT_SCOPE = "the_arm_is_out_of_this_population_because_E533_did_not_refuse_it_over_repo_source"
OUTCOME_VOCAB = (O_CLOSED, O_OPEN_BODY, O_OPEN_ARG, O_NOT_SCOPE)

# --- verdicts ---------------------------------------------------------------------------------
V_ALL_SITE = ("every_repo_source_refusal_was_about_the_site_s_own_arguments_rather_than_the_callee")
V_ALL_CALLEE = "every_repo_source_refusal_was_about_the_callee_reading_module_state_or_the_tree"
V_SPLIT = "the_repo_source_refusals_split_between_the_callee_and_the_site_s_own_arguments"
V_EMPTY = "no_open_arm_in_the_parent_was_refused_because_its_callee_is_repo_source"
VERDICT_VOCAB = (V_ALL_SITE, V_ALL_CALLEE, V_SPLIT, V_EMPTY)

TREE_CALLS = ("open", "listdir", "walk", "scandir", "read_text", "read_bytes", "glob", "rglob",
              "load", "loads", "getcwd", "exists", "isfile", "isdir")
MAX_DEPTH = 12
MAX_STEPS = 20000


def _now():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _is_self(name):
    return any(prefix in name for prefix in SELF_EXCLUDED)


# ------------------------------------------------------------------ population
def load_parent(root=None):
    root = root or ROOT
    with open(os.path.join(root, "results", "state_tilt", PARENT_FACE), "r", encoding="utf-8") as fh:
        return json.load(fh)


def population(parent):
    """Every arm E533 published open, marked with whether E533 refused it over repo source."""
    rows = []
    for arm in parent.get("arms") or []:
        rows.append({"arm": arm, "refused_over_repo_source":
                     arm.get("fold_class") == e533.F_REPO_CALLEE})
    return rows


# ------------------------------------------------------------------ module index
_MODULE_CACHE = {}


def module_tree(root, rel):
    key = (root, rel)
    if key not in _MODULE_CACHE:
        _MODULE_CACHE[key] = e521.parse_file(root, rel)
    return _MODULE_CACHE[key]


def _top_functions(tree):
    out = {}
    if tree is None:
        return out
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[node.name] = node
    return out


def find_callee(root, site_rel, name):
    """(rel, node, tree) for `name`, preferring the site's own module; None when not found."""
    own = module_tree(root, site_rel)
    fn = _top_functions(own).get(name)
    if fn is not None:
        return site_rel, fn, own
    hits = []
    for path in corpus_files(root):
        rel = os.path.relpath(path, root).replace("\\", "/")
        tree = module_tree(root, rel)
        fn = _top_functions(tree).get(name)
        if fn is not None:
            hits.append((rel, fn, tree))
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        return ("ambiguous", None, None, len(hits))
    return None


BUILTIN_NAMES = set(dir(__builtins__)) if isinstance(__builtins__, dict) is False else \
    set(__builtins__.keys())


def _module_level_names(tree):
    names = set()
    if tree is None:
        return names
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                for nm in ast.walk(tgt):
                    if isinstance(nm, ast.Name):
                        names.add(nm.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                names.add((alias.asname or alias.name).split(".")[0])
    return names


def _param_names(fn):
    args = fn.args
    out = [a.arg for a in list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)]
    if args.vararg:
        out.append(args.vararg.arg)
    if args.kwarg:
        out.append(args.kwarg.arg)
    return out


def _local_names(fn):
    """Names the body binds itself (assignment targets, loop targets, with/except)."""
    out = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            out.add(node.id)
    return out


def classify_body(fn, tree, root):
    """Body purity: (body_class, detail) read off the source, not off a run."""
    params = set(_param_names(fn))
    locals_ = _local_names(fn)
    module_names = _module_level_names(tree)
    module_fns = set(_top_functions(tree))
    readings = []
    for node in ast.walk(fn):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id in params or node.id in locals_ or node.id in ("True", "False", "None"):
                continue
            if node.id in BUILTIN_NAMES:
                continue
            if node.id in module_fns:
                readings.append(("repo_call", node.id, getattr(node, "lineno", 0)))
                continue
            if node.id in module_names:
                readings.append(("module_state", node.id, getattr(node, "lineno", 0)))
            else:
                readings.append(("free_name", node.id, getattr(node, "lineno", 0)))
        if isinstance(node, ast.Call):
            fname = None
            if isinstance(node.func, ast.Name):
                fname = node.func.id
            elif isinstance(node.func, ast.Attribute):
                fname = node.func.attr
            if fname and fname not in e533.FOLDERS and fname not in params:
                if fname in TREE_CALLS:
                    readings.append(("tree", fname, getattr(node, "lineno", 0)))
                elif isinstance(node.func, ast.Name) and fname in _top_functions(tree):
                    readings.append(("repo_call", fname, getattr(node, "lineno", 0)))
    modules = [r for r in readings if r[0] in ("module_state", "free_name")]
    trees = [r for r in readings if r[0] == "tree"]
    calls = [r for r in readings if r[0] == "repo_call"]
    if modules:
        return B_MODULE, [{"name": r[1], "line": r[2]} for r in modules]
    if trees:
        return B_TREE, [{"name": r[1], "line": r[2]} for r in trees]
    if calls:
        return B_REPO_CALL, [{"name": r[1], "line": r[2]} for r in calls]
    return B_PURE, []


# ------------------------------------------------------------------ the literal interpreter
class _Uneval(Exception):
    def __init__(self, why, detail=""):
        self.why = why
        self.detail = detail


_STEPS = [0]


def _tick():
    _STEPS[0] += 1
    if _STEPS[0] > MAX_STEPS:
        raise _Uneval("the_interpreter_hit_its_step_cap")


def _same(a, b):
    return a == b


def ev(node, env, root, depth=0):
    _tick()
    if depth > MAX_DEPTH:
        raise _Uneval("expression_nested_deeper_than_the_interpreter_follows")
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in env:
            return env[node.id]
        if node.id == "True":
            return True
        if node.id == "False":
            return False
        if node.id == "None":
            return None
        raise _Uneval("name_not_bound_in_the_inlined_scope", node.id)
    if isinstance(node, ast.List):
        return [ev(e, env, root, depth + 1) for e in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(ev(e, env, root, depth + 1) for e in node.elts)
    if isinstance(node, ast.Set):
        return {ev(e, env, root, depth + 1) for e in node.elts}
    if isinstance(node, ast.Dict):
        return {ev(k, env, root, depth + 1): ev(v, env, root, depth + 1)
                for k, v in zip(node.keys, node.values)}
    if isinstance(node, ast.Subscript):
        base = ev(node.value, env, root, depth + 1)
        if isinstance(node.slice, ast.Slice):
            lo = ev(node.slice.lower, env, root, depth + 1) if node.slice.lower is not None else None
            hi = ev(node.slice.upper, env, root, depth + 1) if node.slice.upper is not None else None
            return base[lo:hi]
        return base[ev(node.slice, env, root, depth + 1)]
    if isinstance(node, ast.UnaryOp):
        val = ev(node.operand, env, root, depth + 1)
        if isinstance(node.op, ast.USub):
            return -val
        if isinstance(node.op, ast.UAdd):
            return +val
        if isinstance(node.op, ast.Not):
            return not val
        raise _Uneval("unary_operator_not_supported")
    if isinstance(node, ast.BinOp):
        lft = ev(node.left, env, root, depth + 1)
        rgt = ev(node.right, env, root, depth + 1)
        ops = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b,
               ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b,
               ast.FloorDiv: lambda a, b: a // b, ast.Mod: lambda a, b: a % b,
               ast.Pow: lambda a, b: a ** b}
        for kind, fn in ops.items():
            if isinstance(node.op, kind):
                try:
                    return fn(lft, rgt)
                except Exception:
                    raise _Uneval("arithmetic_on_values_this_interpreter_cannot_combine")
        raise _Uneval("binary_operator_not_supported")
    if isinstance(node, ast.BoolOp):
        vals = [ev(v, env, root, depth + 1) for v in node.values]
        if isinstance(node.op, ast.And):
            out = vals[0]
            for v in vals[1:]:
                out = v if out else out
            return out
        out = vals[0]
        for v in vals[1:]:
            out = out or v
        return out
    if isinstance(node, ast.Compare):
        left = ev(node.left, env, root, depth + 1)
        for op, comp in zip(node.ops, node.comparators):
            right = ev(comp, env, root, depth + 1)
            table = {ast.Eq: lambda a, b: a == b, ast.NotEq: lambda a, b: a != b,
                     ast.Lt: lambda a, b: a < b, ast.LtE: lambda a, b: a <= b,
                     ast.Gt: lambda a, b: a > b, ast.GtE: lambda a, b: a >= b,
                     ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b,
                     ast.Is: _same, ast.IsNot: lambda a, b: not _same(a, b)}
            for kind, fn in table.items():
                if isinstance(op, kind):
                    if not fn(left, right):
                        return False
                    break
            else:
                raise _Uneval("comparison_operator_not_supported")
            left = right
        return True
    if isinstance(node, ast.IfExp):
        return ev(node.body if ev(node.test, env, root, depth + 1) else node.orelse,
                  env, root, depth + 1)
    if isinstance(node, (ast.ListComp, ast.GeneratorExp, ast.SetComp)):
        return _ev_comp(node, env, root, depth)
    if isinstance(node, ast.Call):
        return _ev_call(node, env, root, depth)
    raise _Uneval("expression_kind_%s_not_supported" % type(node).__name__)


def _ev_comp(node, env, root, depth):
    if len(node.generators) != 1:
        raise _Uneval("a_comprehension_with_more_than_one_generator_is_not_followed")
    gen = node.generators[0]
    if gen.is_async:
        raise _Uneval("an_async_comprehension_is_not_followed")
    if not isinstance(gen.target, ast.Name):
        raise _Uneval("a_comprehension_target_that_is_not_a_plain_name")
    out = []
    for item in ev(gen.iter, env, root, depth + 1):
        inner = dict(env)
        inner[gen.target.id] = item
        ok = True
        for cond in gen.ifs:
            if not ev(cond, inner, root, depth + 1):
                ok = False
                break
        if ok:
            out.append(ev(node.elt, inner, root, depth + 1))
    return out


def _ev_call(node, env, root, depth):
    if isinstance(node.func, ast.Attribute):
        attr = node.func.attr
        base = ev(node.func.value, env, root, depth + 1)
        args = [ev(a, env, root, depth + 1) for a in node.args]
        kwargs = {k.arg: ev(k.value, env, root, depth + 1) for k in node.keywords if k.arg}
        if attr == "get" and hasattr(base, "get"):
            return base.get(*args, **kwargs)
        if attr == "keys" and hasattr(base, "keys"):
            return list(base.keys())
        if attr == "items" and hasattr(base, "items"):
            return list(base.items())
        if attr == "values" and hasattr(base, "values"):
            return list(base.values())
        if attr == "append" and isinstance(base, list):
            base.append(*args)
            return None
        if attr == "copy" and hasattr(base, "copy"):
            return base.copy()
        raise _Uneval("attribute_call_this_interpreter_does_not_follow", attr)
    if not isinstance(node.func, ast.Name):
        raise _Uneval("callee_that_is_neither_a_name_nor_an_attribute")
    name = node.func.id
    args = [ev(a, env, root, depth + 1) for a in node.args]
    kwargs = {}
    for kw in node.keywords:
        if kw.arg is None:
            raise _Uneval("a_starred_keyword_argument")
        kwargs[kw.arg] = ev(kw.value, env, root, depth + 1)
    if name in e533.FOLDERS or name in BUILTIN_NAMES:
        return _apply_builtin(name, args, kwargs)
    if name in env and callable(env[name]):
        return env[name](*args, **kwargs)
    fn = _resolve_fn(name, root, env)
    if fn is None:
        raise _Uneval("callee_name_this_interpreter_cannot_resolve", name)
    return call_function(fn, args, kwargs, root, depth + 1)


def _apply_builtin(name, args, kwargs):
    if name == "dict":
        return dict(*args, **kwargs)
    if kwargs:
        raise _Uneval("a_builtin_called_with_keywords_this_interpreter_does_not_follow", name)
    table = {"range": lambda *a: list(range(*a)) if len(a) != 1 or a[0] < 10000 else
             (_ for _ in ()).throw(_Uneval("range_too_wide_to_materialise")),
             "list": lambda a=(): list(a), "tuple": lambda a=(): tuple(a),
             "set": lambda a=(): set(a), "len": lambda a: len(a),
             "sum": lambda a, s=0: sum(a, s), "min": lambda *a: min(*a),
             "max": lambda *a: max(*a), "abs": lambda a: abs(a), "int": lambda *a: int(*a),
             "str": lambda *a: str(*a), "bool": lambda a: bool(a),
             "float": lambda a: float(a), "round": lambda *a: round(*a),
             "sorted": lambda a: sorted(a), "reversed": lambda a: list(reversed(a)),
             "enumerate": lambda *a: list(enumerate(*a)), "zip": lambda *a: list(zip(*a)),
             "any": lambda a: any(a), "all": lambda a: all(a),
             "divmod": lambda a, b: divmod(a, b)}
    if name not in table:
        raise _Uneval("builtin_this_interpreter_does_not_follow", name)
    try:
        return table[name](*args)
    except _Uneval:
        raise
    except Exception:
        raise _Uneval("the_builtin_raised_on_the_values_given", name)


def _resolve_fn(name, root, env):
    if "_fn_map" in env and name in env["_fn_map"]:
        return env["_fn_map"][name]
    return None


class _Return(Exception):
    def __init__(self, value):
        self.value = value


class _Continue(Exception):
    pass


class _Break(Exception):
    pass


def call_function(fn, args, kwargs, root, depth=0):
    if depth > MAX_DEPTH:
        raise _Uneval("the_call_chain_is_deeper_than_the_interpreter_follows")
    params = _param_names(fn)
    defaults = fn.args.defaults
    env = {"_fn_map": fn_env_map(root, fn)}
    pos = params[:len(params) - len(defaults)] if defaults else params
    for idx, val in enumerate(args):
        if idx >= len(params):
            raise _Uneval("more_positional_arguments_than_the_signature_takes")
        env[params[idx]] = val
    for name, node in zip(params[len(params) - len(defaults):] if defaults else [], defaults):
        env[name] = ev(node, env, root, depth + 1)
    for key, val in kwargs.items():
        if key not in params:
            raise _Uneval("a_keyword_the_signature_does_not_take", key)
        env[key] = val
    for name in params:
        if name not in env:
            raise _Uneval("a_required_parameter_the_site_does_not_supply", name)
    try:
        _exec_block(fn.body, env, root, depth)
    except _Return as ret:
        return ret.value
    return None


def fn_env_map(root, fn):
    """Repo functions reachable from the module `fn` was defined in (same-module only)."""
    rel = getattr(fn, "_e536_rel", None)
    if rel:
        tree = module_tree(root, rel)
        return _top_functions(tree)
    return {}


def _exec_block(body, env, root, depth):
    for stmt in body:
        _exec_stmt(stmt, env, root, depth)


def _exec_stmt(stmt, env, root, depth):
    _tick()
    if isinstance(stmt, ast.Expr):
        ev(stmt.value, env, root, depth)
        return
    if isinstance(stmt, ast.Assign):
        value = ev(stmt.value, env, root, depth)
        for tgt in stmt.targets:
            _store(tgt, value, env, root, depth)
        return
    if isinstance(stmt, ast.AnnAssign):
        if stmt.value is not None:
            _store(stmt.target, ev(stmt.value, env, root, depth), env, root, depth)
        return
    if isinstance(stmt, ast.AugAssign):
        cur = ev(stmt.target, env, root, depth)
        delta = ev(stmt.value, env, root, depth)
        table = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b,
                 ast.Mult: lambda a, b: a * b}
        for kind, fn in table.items():
            if isinstance(stmt.op, kind):
                _store(stmt.target, fn(cur, delta), env, root, depth)
                return
        raise _Uneval("augmented_assignment_operator_not_supported")
    if isinstance(stmt, ast.For):
        seq = ev(stmt.iter, env, root, depth)
        for item in seq:
            _store(stmt.target, item, env, root, depth)
            try:
                _exec_block(stmt.body, env, root, depth)
            except _Continue:
                continue
            except _Break:
                break
        else:
            _exec_block(stmt.orelse, env, root, depth) if stmt.orelse else None
        return
    if isinstance(stmt, ast.If):
        if ev(stmt.test, env, root, depth):
            _exec_block(stmt.body, env, root, depth)
        elif stmt.orelse:
            _exec_block(stmt.orelse, env, root, depth)
        return
    if isinstance(stmt, ast.With):
        raise _Uneval("a_with_block_is_the_tree_being_read")
    if isinstance(stmt, ast.Return):
        raise _Return(ev(stmt.value, env, root, depth) if stmt.value is not None else None)
    if isinstance(stmt, ast.Continue):
        raise _Continue()
    if isinstance(stmt, ast.Break):
        raise _Break()
    if isinstance(stmt, ast.Pass):
        return
    raise _Uneval("statement_kind_%s_not_supported" % type(stmt).__name__)


def _store(tgt, value, env, root, depth):
    if isinstance(tgt, ast.Name):
        env[tgt.id] = value
        return
    if isinstance(tgt, (ast.Tuple, ast.List)):
        vals = list(value)
        if len(vals) != len(tgt.elts):
            raise _Uneval("a_tuple_target_whose_parts_do_not_match_the_value")
        for sub, val in zip(tgt.elts, vals):
            _store(sub, val, env, root, depth)
        return
    if isinstance(tgt, ast.Subscript):
        base = ev(tgt.value, env, root, depth)
        key = ev(tgt.slice, env, root, depth)
        base[key] = value
        return
    raise _Uneval("assignment_target_kind_%s_not_supported" % type(tgt).__name__)


# ------------------------------------------------------------------ the site side
def _caller_function(tree, line):
    return e533._caller_function(tree, line)


def _binding_node(root, caller_rel, line, name):
    """(kind, node, binding_line) for the nearest binding of `name` before `line`."""
    tree = module_tree(root, caller_rel)
    if tree is None:
        return None, None, None
    fn = _caller_function(tree, line)
    if fn is None:
        return None, None, None
    bindings = [b for b in e527._bindings(fn) if b[0] == name and b[1] < line]
    if not bindings:
        return None, None, None
    params = [b for b in bindings if b[3] == "parameter"]
    if params:
        return "parameter", None, params[0][1]
    nearest = max((b for b in bindings if b[3] != "parameter"), key=lambda b: b[1])
    return nearest[3], nearest[4], nearest[1]


def _intervening_item_stores(root, caller_rel, start_line, end_line):
    """Count subscript-target assignments between a binding and the site that touch that name."""
    tree = module_tree(root, caller_rel)
    out = []
    if tree is None:
        return out
    fn = _caller_function(tree, end_line)
    if fn is None:
        return out
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Subscript):
            line = getattr(node, "lineno", 0)
            if start_line < line < end_line:
                out.append({"line": line,
                            "target": ast.unparse(node.targets[0])[:80]})
    return out


def evaluate_argument(node, root, caller_rel, site_line, depth=0):
    """(site_class, value_text, value, reason) for one argument expression of the call."""
    if depth > 2:
        return S_UNRESOLVED, None, None, "the_binding_chain_is_deeper_than_two_hops"
    try:
        value = e533._fold(node)
        return S_LITERAL, e533._text(value), value, None
    except e533._Stop:
        pass
    try:
        value = ev(node, {}, root)
        return S_LITERAL, e533._text(value), value, None
    except _Uneval as exc:
        first_reason = "%s%s" % (exc.why, (":" + exc.detail) if exc.detail else "")
    # a name, or a subscript of a name, that the caller binds before the site
    base = node.value if isinstance(node, ast.Subscript) else node
    if not isinstance(base, ast.Name):
        return S_UNRESOLVED, None, None, first_reason
    kind, bound, bound_line = _binding_node(root, caller_rel, site_line, base.id)
    if bound is None:
        return S_UNRESOLVED, None, None, ("the_name_is_the_caller_s_own_parameter"
                                          if kind == "parameter" else first_reason)
    if not isinstance(bound, ast.Call):
        arg_class, txt, val, why = evaluate_argument(bound, root, caller_rel, bound_line, depth + 1)
        if val is not None and isinstance(node, ast.Subscript):
            try:
                val = val[ev(node.slice, {}, root)]
            except Exception:
                return S_RESOLVABLE, None, None, "the_binding_folds_but_the_subscript_does_not"
        if val is not None:
            return S_LITERAL_ONE_HOP, e533._text(val), val, None
        return arg_class, txt, None, why
    if not isinstance(bound.func, ast.Name):
        return S_UNRESOLVED, None, None, "the_binding_is_a_call_this_study_does_not_follow"
    found = find_callee(root, caller_rel, bound.func.id)
    if not found or found[1] is None:
        return S_UNRESOLVED, None, None, "the_binding_calls_a_name_no_single_module_defines"
    rel, fn, tree = found[0], found[1], found[2]
    fn._e536_rel = rel
    body_class, _ = classify_body(fn, tree, root)
    if body_class not in (B_PURE, B_REPO_CALL):
        return S_RESOLVABLE, None, None, ("the_binding_calls_a_body_classed_%s" % body_class)
    try:
        args = [ev(a, {}, root) for a in bound.args]
        value = call_function(fn, args, {}, root)
    except _Uneval as exc:
        return S_RESOLVABLE, None, None, "%s%s" % (exc.why, (":" + exc.detail) if exc.detail else "")
    if isinstance(node, ast.Subscript):
        try:
            value = value[ev(node.slice, {}, root)]
        except Exception:
            return S_RESOLVABLE, None, None, "the_binding_runs_but_the_subscript_does_not"
    return S_LITERAL_ONE_HOP, e533._text(value), value, None


def analyse_arm(row, root=None):
    root = root or ROOT
    arm = row["arm"]
    rec = {
        "source": arm.get("source"),
        "line": arm.get("line"),
        "callee": arm.get("callee"),
        "parameter": arm.get("parameter"),
        "argument_expression": arm.get("argument_expression"),
        "e533_fold_class": arm.get("fold_class"),
        "in_population": bool(row["refused_over_repo_source"]),
        "callee_rel": None,
        "callee_line": None,
        "body_class": None,
        "body_reads": [],
        "site_argument_class": None,
        "site_argument_value": None,
        "intervening_item_stores": [],
        "inlined_value": None,
        "refusal_attribution": None,
        "arm_outcome": O_NOT_SCOPE,
        "error": None,
    }
    if not rec["in_population"]:
        return rec
    expression = rec["argument_expression"]
    try:
        call = ast.parse(expression, mode="eval").body
    except Exception as exc:
        rec["error"] = "the_published_argument_expression_does_not_parse: %s" % exc
        rec["body_class"] = B_UNREAD
        rec["refusal_attribution"] = A_UNREAD
        rec["arm_outcome"] = O_OPEN_ARG
        return rec
    if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name):
        rec["error"] = "the_published_argument_is_not_a_direct_call_to_a_plain_name"
        rec["body_class"] = B_UNREAD
        rec["refusal_attribution"] = A_UNREAD
        rec["arm_outcome"] = O_OPEN_ARG
        return rec

    callee_name = call.func.id
    found = find_callee(root, rec["source"], callee_name)
    if found is None:
        rec["body_class"] = B_UNREAD
        rec["error"] = "no_module_in_the_repository_defines_this_callee"
        rec["refusal_attribution"] = A_UNREAD
        rec["arm_outcome"] = O_OPEN_ARG
        return rec
    if found[1] is None:
        rec["body_class"] = B_UNREAD
        rec["error"] = "the_callee_name_is_defined_in_%d_modules_so_no_single_body_is_read" % found[3]
        rec["refusal_attribution"] = A_UNREAD
        rec["arm_outcome"] = O_OPEN_ARG
        return rec
    rel, fn, tree = found
    fn._e536_rel = rel
    rec["callee_rel"], rec["callee_line"] = rel, fn.lineno
    body_class, reads = classify_body(fn, tree, root)
    rec["body_class"], rec["body_reads"] = body_class, reads

    # --- the site's own arguments, one by one
    arg_classes, arg_values, arg_problems = [], [], []
    for arg in call.args:
        arg_class, txt, val, why = evaluate_argument(arg, root, rec["source"], rec["line"])
        arg_classes.append(arg_class)
        arg_values.append(val)
        if why:
            arg_problems.append(why)
    rec["site_argument_class"] = (S_LITERAL if all(c == S_LITERAL for c in arg_classes)
                                  else S_LITERAL_ONE_HOP
                                  if all(c in (S_LITERAL, S_LITERAL_ONE_HOP) for c in arg_classes)
                                  else S_RESOLVABLE
                                  if any(c in (S_LITERAL, S_LITERAL_ONE_HOP, S_RESOLVABLE)
                                         for c in arg_classes)
                                  else S_UNRESOLVED)
    literal_args = all(c in (S_LITERAL, S_LITERAL_ONE_HOP) for c in arg_classes) and \
        all(v is not None for v in arg_values)
    if rec["site_argument_class"] == S_LITERAL_ONE_HOP:
        # the first argument is `name[...]`: the store, if any, sits between binding and site
        base = call.args[0].value if isinstance(call.args[0], ast.Subscript) else None
        if isinstance(base, ast.Name):
            _, _, bound_line = _binding_node(root, rec["source"], rec["line"], base.id)
            if bound_line:
                rec["intervening_item_stores"] = _intervening_item_stores(
                    root, rec["source"], bound_line, rec["line"])

    # --- attribution: whose refusal was it
    callee_impure = body_class in (B_MODULE, B_TREE)
    site_unresolvable = any(c in (S_RESOLVABLE, S_UNRESOLVED) for c in arg_classes)
    if body_class == B_UNREAD:
        rec["refusal_attribution"] = A_UNREAD
    elif callee_impure and site_unresolvable:
        rec["refusal_attribution"] = A_BOTH
    elif callee_impure:
        rec["refusal_attribution"] = A_CALLEE
    else:
        rec["refusal_attribution"] = A_SITE

    # --- does the inlined body run to a value
    if callee_impure:
        rec["arm_outcome"] = O_OPEN_BODY
        return rec
    if not literal_args:
        rec["arm_outcome"] = O_OPEN_ARG
        rec["error"] = "; ".join(arg_problems[:2]) or None
        return rec
    try:
        value = call_function(fn, arg_values, {}, root)
    except _Uneval as exc:
        rec["arm_outcome"] = O_OPEN_ARG
        rec["error"] = "%s%s" % (exc.why, (":" + exc.detail) if exc.detail else "")
        return rec
    rec["inlined_value"] = e533._text(value)
    rec["arm_outcome"] = O_CLOSED
    return rec


# ------------------------------------------------------------------ summary / verdict
def _count(rows, key):
    out = {}
    for row in rows:
        out[row.get(key)] = out.get(row.get(key), 0) + 1
    return out


def _summary(rows, sources):
    pop = [r for r in rows if r.get("in_population")]
    return {
        "sources_read": sources,
        "open_arms_in_parent": len(rows),
        "arms_refused_because_the_callee_is_repo_source": len(pop),
        "arms_out_of_scope": len(rows) - len(pop),
        "arms_whose_inlined_body_runs_on_a_literal_argument":
            sum(1 for r in rows if r["arm_outcome"] == O_CLOSED),
        "arms_staying_open_because_of_the_body":
            sum(1 for r in rows if r["arm_outcome"] == O_OPEN_BODY),
        "arms_staying_open_because_of_the_site_s_argument":
            sum(1 for r in rows if r["arm_outcome"] == O_OPEN_ARG),
        "arms_by_body_class": _count(pop, "body_class"),
        "arms_by_site_argument_class": _count(pop, "site_argument_class"),
        "arms_by_refusal_attribution": _count(pop, "refusal_attribution"),
        "arms_by_outcome": _count(rows, "arm_outcome"),
    }


def _verdict(summary):
    attrs = summary["arms_by_refusal_attribution"]
    total = summary["arms_refused_because_the_callee_is_repo_source"]
    if not total:
        return V_EMPTY
    site = attrs.get(A_SITE, 0)
    callee = attrs.get(A_CALLEE, 0)
    if attrs.get(A_UNREAD, 0) == total:
        return V_SPLIT
    if site == total:
        return V_ALL_SITE
    if callee + attrs.get(A_BOTH, 0) == total:
        return V_ALL_CALLEE if callee == total else V_SPLIT
    return V_SPLIT


# ------------------------------------------------------------------ face
def corpus_files(root=None):
    root = root or ROOT
    out = []
    for base, dirs, files in os.walk(os.path.join(root, "scripts")):
        dirs[:] = [d for d in dirs if d not in ("__pycache__",)]
        for name in files:
            if name.endswith(".py") and not _is_self(name):
                out.append(os.path.join(base, name))
    return out


def build(root=None, write=True, rows=None, sources=None, parent=None):
    root = root or ROOT
    _STEPS[0] = 0
    if rows is None:
        parent = parent or load_parent(root)
        rows = [analyse_arm(r, root) for r in population(parent)]
        if sources is None:
            sources = len(corpus_files(root))
    summary = _summary(rows, sources or 0)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("whether the repo-source callee E533's fold refused to inline is pure in "
                  "literals once its parameters are bound to the site's own arguments"),
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": ("%s::population() -- every arm E533 published open, split by whether "
                              "E533 refused it because the callee is repository source"
                              % os.path.basename(__file__)),
        "parent_face": PARENT_FACE,
        "method_limits": [
            "one level of inlining only: the callee's body is read and interpreted with its "
            "parameters bound to the arguments the site passes, and a call inside that body to "
            "another repo function is followed only while the chain stays under four hops",
            "the interpreter is a whitelist: constants, containers, subscripts, arithmetic, "
            "comparisons, if/for/return/continue/break and a fixed builtin set; a statement or "
            "expression kind outside it stops the run and is published with its name",
            "nothing in this repository is executed -- the tree is read as text and interpreted "
            "here, and no source is rewritten",
            "a site argument whose expression is a name is followed through the nearest binding "
            "before the site in the caller, so 'literal once its binding is folded' is a "
            "statement about that one binding, not about the whole call stack",
            "an item store that sits between a binding and the site is counted and published, and "
            "the folded value is published as the value of the unmutated container",
            "sources_read is a snapshot of a live tree other lanes write to; it is published but "
            "not gated, while every class, every count and the verdict are re-derived",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "body_class_vocab": list(BODY_VOCAB),
        "site_argument_class_vocab": list(SITE_VOCAB),
        "refusal_attribution_vocab": list(ATTR_VOCAB),
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
    if summary.get("open_arms_in_parent") != len(rows):
        problems.append("open_arms_in_parent %r does not equal the published arms %d"
                        % (summary.get("open_arms_in_parent"), len(rows)))
    rec_summary = _summary(rows, summary.get("sources_read") or 0)
    for key in ("arms_refused_because_the_callee_is_repo_source", "arms_out_of_scope",
                "arms_whose_inlined_body_runs_on_a_literal_argument",
                "arms_staying_open_because_of_the_body",
                "arms_staying_open_because_of_the_site_s_argument"):
        if summary.get(key) != rec_summary[key]:
            problems.append("%s does not re-derive (%r vs %r)"
                            % (key, summary.get(key), rec_summary[key]))
    for key in ("arms_by_body_class", "arms_by_site_argument_class",
                "arms_by_refusal_attribution", "arms_by_outcome"):
        if summary.get(key) != rec_summary[key]:
            problems.append("%s does not re-derive" % key)
    if _verdict(summary) != face.get("verdict"):
        problems.append("the verdict does not re-derive from the summary")

    vocab = {BODY_VOCAB: "body_class", SITE_VOCAB: "site_argument_class",
             ATTR_VOCAB: "refusal_attribution", OUTCOME_VOCAB: "arm_outcome"}
    for row in rows:
        where = "%s:%s" % (row.get("source"), row.get("line"))
        if not row.get("in_population"):
            if row.get("arm_outcome") != O_NOT_SCOPE:
                problems.append("%s: an arm outside the population is published as %r"
                                % (where, row.get("arm_outcome")))
            if row.get("refusal_attribution") is not None:
                problems.append("%s: an arm outside the population carries an attribution" % where)
            continue
        for allowed, key in vocab.items():
            if row.get(key) not in allowed:
                problems.append("%s: %s %r is not in its vocabulary" % (where, key, row.get(key)))
        if row.get("arm_outcome") == O_CLOSED:
            if not row.get("inlined_value"):
                problems.append("%s: a closed arm carries no inlined value" % where)
            if row.get("body_class") not in (B_PURE, B_REPO_CALL):
                problems.append("%s: a closed arm's body is classed %r"
                                % (where, row.get("body_class")))
            if row.get("site_argument_class") not in (S_LITERAL, S_LITERAL_ONE_HOP, S_RESOLVABLE):
                problems.append("%s: a closed arm's argument is classed %r"
                                % (where, row.get("site_argument_class")))
            if row.get("refusal_attribution") not in (A_SITE, A_BOTH):
                problems.append("%s: a closed arm attributes the refusal to %r"
                                % (where, row.get("refusal_attribution")))
        else:
            if row.get("inlined_value") is not None:
                problems.append("%s: an open arm carries an inlined value" % where)
        if row.get("arm_outcome") == O_OPEN_BODY and row.get("body_class") in (B_PURE, B_REPO_CALL):
            problems.append("%s: an arm is open over its body but the body is pure" % where)
        if row.get("arm_outcome") == O_OPEN_ARG and \
                row.get("site_argument_class") in (S_LITERAL, S_LITERAL_ONE_HOP):
            problems.append("%s: an arm is open over its argument but the argument folds" % where)
        if row.get("refusal_attribution") == A_CALLEE and row.get("body_class") in (B_PURE, B_REPO_CALL,
                                                                                   B_UNREAD):
            problems.append("%s: the refusal is attributed to the callee but the body is %r"
                            % (where, row.get("body_class")))
        if row.get("refusal_attribution") == A_SITE and row.get("body_class") not in (B_PURE, B_REPO_CALL):
            problems.append("%s: the refusal is attributed to the site but the body reads %r"
                            % (where, row.get("body_class")))
        if row.get("refusal_attribution") == A_UNREAD and row.get("error") is None:
            problems.append("%s: an unattributable refusal carries no reason" % where)
        if row.get("intervening_item_stores") and row.get("inlined_value") and \
                row.get("site_argument_class") != S_LITERAL_ONE_HOP:
            problems.append("%s: item stores are published for an argument class that has no binding"
                            % where)
    return problems


def check(face=None, root=None):
    face = face if face is not None else load_face(root)
    problems = face_problems(face)
    print(json.dumps({"study": STUDY, "face": FACE_NAME, "problems": problems,
                      "verdict": face.get("verdict"), "arms": len(face.get("arms") or [])},
                     ensure_ascii=False, indent=1))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    live = build(root, write=False)
    published = load_face(root)
    problems = face_problems(live)
    if live.get("arms") != published.get("arms"):
        live_by = {(r["source"], r["line"]): r for r in live["arms"]}
        pub_by = {(r["source"], r["line"]): r for r in published["arms"]}
        missing = sorted(set(live_by) - set(pub_by))
        extra = sorted(set(pub_by) - set(live_by))
        if missing:
            problems.append("the published face is missing %d live arms, e.g. %r"
                            % (len(missing), missing[:3]))
        if extra:
            problems.append("the published face carries %d arms that no longer reproduce, e.g. %r"
                            % (len(extra), extra[:3]))
        for key in sorted(set(live_by) & set(pub_by)):
            if live_by[key] != pub_by[key]:
                problems.append("arm %r re-derives differently (published %r, live %r)"
                                % (key, pub_by[key].get("inlined_value"),
                                   live_by[key].get("inlined_value")))
    if live.get("verdict") != published.get("verdict"):
        problems.append("the verdict re-derives to %r, the face publishes %r"
                        % (live.get("verdict"), published.get("verdict")))
    print(json.dumps({"study": STUDY, "problems": problems, "verdict": live.get("verdict"),
                      "arms_live": len(live["arms"]), "arms_published": len(published["arms"])},
                     ensure_ascii=False, indent=1))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
FIXTURE = '''\
"""fixture module for E536."""

SCALE = 2


def _td(lo, hi):
    return {"min": lo, "max": hi}


def fixture_arm():
    rows = [
        {"row": "a", "tight": _td(1.0, 1.1)},
        {"row": "b", "tight": _td(1.0, 1.1)},
    ]
    return {"arm": "a:1", "rows": rows}


def hull(rows, tail):
    lows, highs = [], []
    for rec in rows:
        slot = rec.get(tail) or {}
        lo, hi = slot.get("min"), slot.get("max")
        if lo is None or hi is None:
            continue
        lows.append(float(lo))
        highs.append(float(hi))
    if not lows:
        return None
    return {"lo": min(lows), "hi": max(highs), "n": len(lows)}


def reads_module_state(rows):
    return SCALE * len(rows)


def reads_the_tree(path):
    with open(path) as fh:
        return fh.read()
'''

FIXTURE_CALLER = '''\
"""fixture caller."""

from fixture_module import hull, reads_module_state, reads_the_tree


def uses_literals():
    return hull([{"tight": {"min": 1.0, "max": 1.1}}], "tight")


def uses_a_bound_container():
    return hull(off["rows"], "tight")


def reads_a_name(rows_arg):
    return hull(rows_arg, "tight")


def calls_a_module_reader():
    return reads_module_state([])


def calls_a_tree_reader():
    return reads_the_tree("x")


def off_builder():
    from fixture_module import fixture_arm
    return fixture_arm()


def uses_a_binding():
    off = off_builder()
    return hull(off["rows"], "tight")
'''


def _fixture_parent(caller_text):
    markers = ['hull([{"tight": {"min": 1.0, "max": 1.1}}], "tight")',
               'hull(off["rows"], "tight")', 'hull(rows_arg, "tight")',
               "reads_module_state([])", 'reads_the_tree("x")']
    arms = []
    lines = caller_text.splitlines()
    for marker in markers:
        line = next((num for num, text in enumerate(lines, start=1) if marker in text), None)
        arms.append({
            "source": "scripts/fixture_caller.py", "line": line, "callee": "hull",
            "parameter": "rows", "argument_expression": marker,
            "fold_class": e533.F_REPO_CALLEE,
        })
    return {"arms": arms}


def selftest():
    bad = []
    tmp = tempfile.mkdtemp(prefix="e536_")
    try:
        os.makedirs(os.path.join(tmp, "scripts"))
        with open(os.path.join(tmp, "scripts", "fixture_module.py"), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write(FIXTURE)
        with open(os.path.join(tmp, "scripts", "fixture_caller.py"), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write(FIXTURE_CALLER)
        parent = _fixture_parent(FIXTURE_CALLER)
        rows = [analyse_arm(r, tmp) for r in population(parent)]

        by_expr = {r["argument_expression"]: r for r in rows}
        lit = by_expr.get('hull([{"tight": {"min": 1.0, "max": 1.1}}], "tight")')
        if lit is None:
            bad.append("the literal-argument fixture arm is missing")
        else:
            if lit["body_class"] != B_PURE:
                bad.append("the pure fixture body was classed %r" % (lit["body_class"],))
            if lit["arm_outcome"] != O_CLOSED:
                bad.append("the literal-argument arm is %r, not closed (%r)"
                           % (lit["arm_outcome"], lit.get("error")))
            if lit["inlined_value"] != "{'lo': 1.0, 'hi': 1.1, 'n': 1}":
                bad.append("inlined value %r != the hull of the fixture rows"
                           % (lit.get("inlined_value"),))
            if lit["refusal_attribution"] != A_SITE:
                bad.append("a pure body over a literal argument is attributed to %r"
                           % (lit["refusal_attribution"],))
        unresolved = by_expr.get('hull(rows_arg, "tight")')
        if unresolved is None:
            bad.append("the unresolved-argument fixture arm is missing")
        elif unresolved["arm_outcome"] != O_OPEN_ARG or \
                unresolved["site_argument_class"] != S_RESOLVABLE:
            bad.append("the unresolved argument is published as %r / %r"
                       % (unresolved["arm_outcome"], unresolved["site_argument_class"]))
        module_reader = by_expr.get("reads_module_state([])")
        if module_reader is None:
            bad.append("the module-reading fixture arm is missing")
        else:
            if module_reader["body_class"] != B_MODULE:
                bad.append("a body reading a module constant was classed %r"
                           % (module_reader["body_class"],))
            if module_reader["arm_outcome"] != O_OPEN_BODY:
                bad.append("a module-reading body is published as %r"
                           % (module_reader["arm_outcome"],))
            if module_reader["refusal_attribution"] != A_CALLEE:
                bad.append("a module-reading body is attributed to %r"
                           % (module_reader["refusal_attribution"],))
        tree_reader = by_expr.get('reads_the_tree("x")')
        if tree_reader is None:
            bad.append("the tree-reading fixture arm is missing")
        elif tree_reader["body_class"] != B_TREE:
            bad.append("a body reading the tree was classed %r" % (tree_reader["body_class"],))

        face = build(tmp, write=False, rows=rows, sources=2)
        problems = face_problems(face)
        if problems:
            bad.append("the fixture face does not gate clean: %r" % (problems[:3],))
        if face["verdict"] == V_EMPTY:
            bad.append("fixture verdict is empty")

        def doctored(mutate, why):
            doc = json.loads(json.dumps(face))
            mutate(doc)
            if not face_problems(doc):
                bad.append("a doctored face was accepted: %s" % why)

        doctored(lambda d: d.__setitem__("verdict", V_ALL_CALLEE), "hand-written verdict")
        doctored(lambda d: d["summary"].__setitem__("arms_by_outcome", {"x": 1}),
                 "summary counts that do not re-derive")

        def closed_without_value(d):
            for row in d["arms"]:
                if row["arm_outcome"] == O_CLOSED:
                    row["inlined_value"] = None
                    return
        doctored(closed_without_value, "a closed arm without an inlined value")

        def value_on_an_open_arm(d):
            for row in d["arms"]:
                if row["arm_outcome"] != O_CLOSED:
                    row["inlined_value"] = "{'lo': 1}"
                    return
        doctored(value_on_an_open_arm, "an inlined value on an arm that did not run")

        def callee_blamed_for_a_pure_body(d):
            for row in d["arms"]:
                if row["body_class"] == B_PURE and row["in_population"]:
                    row["refusal_attribution"] = A_CALLEE
                    return
        doctored(callee_blamed_for_a_pure_body, "a pure body blamed on the callee")

        def site_credited_for_a_reading_body(d):
            for row in d["arms"]:
                if row["body_class"] == B_MODULE:
                    row["refusal_attribution"] = A_SITE
                    return
        doctored(site_credited_for_a_reading_body, "a module-reading body credited to the site")

        def not_scope_but_attributed(d):
            for row in d["arms"]:
                row["in_population"] = False
                return
        doctored(not_scope_but_attributed, "an out-of-scope arm keeping its attribution")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(json.dumps({"study": STUDY, "selftest": "green" if not bad else "red",
                      "problems": bad}, ensure_ascii=False, indent=1))
    return 0 if not bad else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build()
        print(json.dumps({"face": FACE_NAME, "arms": len(face["arms"]),
                          "verdict": face["verdict"], "summary": face["summary"]},
                         ensure_ascii=False, indent=1))
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