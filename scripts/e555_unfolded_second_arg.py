"""E555 -- are the 67 unfolded second arguments constants the scan could have evaluated?

E554 (r1580) published the repository's whole ``wrote <path>`` render population
and had to leave 67 rows unresolved with one reason spelled out:
``the_second_argument_is_a_name_this_scan_cannot_fold``.  That reason is a
statement about the *fold*, not about the code.  If the name is a module-level
constant -- written below the message, written inside an ``if``/``try`` block,
or imported from another module -- then a static evaluator could have named the
face, and the 67 are a repair queue rather than a floor.

This study re-reads those 67 rows from E554's own published face (machine-read,
never hand-copied), re-parses each writer at the row's line, and asks of every
free name in the second argument what actually binds it:

  * a module-level constant defined **below** the message (order-blind fold)
  * a module-level constant defined inside a conditional or a loop body
  * a module-level constant **imported** from another module
  * a parameter of the enclosing function (genuinely caller-supplied)
  * a loop / ``with`` target
  * a store into a container or an attribute
  * a name this module never binds at all

A row whose name folds under the wider search is published with the resolved
face path and whether that face exists on disk.  The control arm runs E554's own
resolver over the same 67 rows: it must fold zero of them, or the population is
not the residue it claims to be.

    python scripts/e555_unfolded_second_arg.py build      # publish the face
    python scripts/e555_unfolded_second_arg.py check      # re-derive from source; problems must be []
    python scripts/e555_unfolded_second_arg.py verify     # two builds identical
    python scripts/e555_unfolded_second_arg.py selftest   # offline fixtures + defect refusals
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e554_wrote_population as e554  # noqa: E402  (the fold this study extends)

STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
LATEST = os.path.join(STATE_TILT, "unfoldedname_latest.json")
DATED_PREFIX = "UNFOLDEDNAME"

STUDY = "E555"
CARD = "E555"
TITLE = ("whether the 67 second arguments the wrote-population scan could not fold are "
         "constants a wider static evaluator can name")
EVIDENCE_CUTOFF = "2026-11-08"

U_UNFOLDABLE_NAME = e554.U_UNFOLDABLE_NAME

# ---- what binds the name ---------------------------------------------------
F_FOLDED = "a_module_constant_the_wider_fold_names"
F_BELOW = "a_module_level_binding"
F_NESTED = "a_binding_inside_a_conditional_or_a_loop"
F_IMPORTED = "an_imported_module_constant"
BINDING_VOCAB = (F_BELOW, F_NESTED, F_IMPORTED)
F_PARAMETER = "a_parameter_of_the_enclosing_function"
F_LOOP_WITH = "a_loop_or_with_target"
F_CONTAINER = "a_store_into_a_container_or_an_attribute"
F_NEVER = "a_name_this_module_never_binds"
F_RUNTIME = "a_module_constant_whose_value_is_run_time_data"
F_LOCAL_RUNTIME = "a_local_variable_of_the_enclosing_function"
F_TUPLE_FROM_CALL = "a_tuple_target_of_a_call_the_helper_returns"
F_IMPORT_UNRESOLVED = "a_name_imported_from_a_module_outside_the_tree"
F_NO_CALL = "the_render_call_is_no_longer_at_that_line"
F_ALREADY = "a_module_constant_the_published_fold_already_binds"
FOLD_VOCAB = (F_FOLDED, F_PARAMETER, F_LOOP_WITH,
              F_CONTAINER, F_NEVER, F_RUNTIME, F_LOCAL_RUNTIME, F_TUPLE_FROM_CALL,
              F_IMPORT_UNRESOLVED, F_NO_CALL, F_ALREADY)
CONSTANT_CLASSES = (F_FOLDED,)
BLOCKING_CLASSES = (F_PARAMETER, F_TUPLE_FROM_CALL, F_LOOP_WITH, F_LOCAL_RUNTIME,
                    F_RUNTIME, F_CONTAINER, F_IMPORT_UNRESOLVED, F_NEVER)

V_SOME_CONSTANTS = ("some_of_the_unfolded_names_are_constants_a_wider_evaluator_can_name")
V_ALL_RUNTIME = ("every_unfolded_name_is_bound_by_run_time_data_or_a_caller_not_by_a_constant")

PATHISH = re.compile(r"^(results|docs|data|state|research|knowledge|logs)/")


# ---------------------------------------------------------------- reads
def _read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def _tree_of(rel):
    try:
        return ast.parse(_read(os.path.join(ROOT, rel)))
    except (OSError, SyntaxError):
        return None


def _published_population():
    """The 67 rows, read out of E554's own face -- never retyped here."""
    face = json.load(io.open(e554.LATEST, encoding="utf-8"))
    rows = [r for r in face.get("rows") or []
            if (r.get("face") or {}).get("unresolved_because") == U_UNFOLDABLE_NAME]
    return face.get("evidence_cutoff"), rows


# ---------------------------------------------------------------- bindings
def _module_bindings(tree):
    """Every module-level binding, order-blind, with the shape that hid it.

    ``e554._module_constants`` walks ``tree.body`` in source order, so a constant
    written below the message, or written inside an ``if TYPE_CHECKING:`` block,
    is invisible to it.  Neither is a run-time fact.
    """
    out = {}

    def add(name, value, line, nested):
        kind = F_NESTED if nested else F_BELOW
        out.setdefault(name, []).append({"line": line, "value": value, "kind": kind})

    def visit(stmts, nested):
        for st in stmts:
            if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(st, ast.Assign):
                for t in st.targets:
                    if isinstance(t, ast.Name):
                        add(t.id, st.value, st.lineno, nested)
                    elif isinstance(t, ast.Subscript):
                        if isinstance(t.value, ast.Name):
                            out.setdefault("__store__%s" % t.value.id, []).append(
                                {"line": st.lineno, "value": None, "kind": F_CONTAINER})
                    elif isinstance(t, (ast.Tuple, ast.List)):
                        for elt in t.elts:
                            if isinstance(elt, ast.Name):
                                add(elt.id, None, st.lineno, nested)
            elif isinstance(st, ast.AnnAssign) and st.value is not None:
                if isinstance(st.target, ast.Name):
                    add(st.target.id, st.value, st.lineno, nested)
            elif isinstance(st, ast.AugAssign) and isinstance(st.target, ast.Name):
                add(st.target.id, None, st.lineno, nested)
            elif isinstance(st, (ast.For, ast.AsyncFor)):
                for t in ast.walk(st.target):
                    if isinstance(t, ast.Name):
                        out.setdefault(t.id, []).append(
                            {"line": st.lineno, "value": None, "kind": F_LOOP_WITH})
                visit(st.body, True)
                visit(st.orelse, True)
                continue
            elif isinstance(st, (ast.With, ast.AsyncWith)):
                for item in st.items:
                    if item.optional_vars is not None:
                        for t in ast.walk(item.optional_vars):
                            if isinstance(t, ast.Name):
                                out.setdefault(t.id, []).append(
                                    {"line": st.lineno, "value": None, "kind": F_LOOP_WITH})
                visit(st.body, True)
                continue
            elif isinstance(st, (ast.If, ast.While)):
                visit(st.body, True)
                visit(st.orelse, True)
                continue
            elif isinstance(st, ast.Try):
                visit(st.body, True)
                for h in st.handlers:
                    visit(h.body, True)
                visit(st.orelse, True)
                visit(st.finalbody, True)
                continue

    visit(tree.body, False)
    return out


def _import_bindings(tree, rel):
    """(from-name -> (module_rel, attr)), (plain module name -> module_rel)."""
    from_map, plain = {}, {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and not node.level:
            target = _module_path(node.module)
            for alias in node.names:
                # an import whose module the tree does not contain is still a binding:
                # the name is supplied at run time from somewhere outside the corpus.
                from_map[alias.asname or alias.name] = (target, alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    target = _module_path(alias.name)
                    if target:
                        plain[alias.asname] = target
    return from_map, plain


_MODULE_CACHE = {}


def _module_path(dotted):
    if dotted in _MODULE_CACHE:
        return _MODULE_CACHE[dotted]
    stub = dotted.replace(".", "/")
    for cand in ("%s.py" % stub, "%s/__init__.py" % stub,
                 "scripts/%s.py" % stub, "Tools/%s.py" % stub):
        if os.path.isfile(os.path.join(ROOT, cand)):
            _MODULE_CACHE[dotted] = cand
            return cand
    _MODULE_CACHE[dotted] = None
    return None


def _wide_constants(tree, rel, depth=0):
    """Order-blind constants for one module, including imported ones (fixpoint)."""
    if depth > 4 or tree is None:
        return {}
    consts = {}
    bindings = _module_bindings(tree)
    from_map, plain = _import_bindings(tree, rel)
    for local, (target, attr) in from_map.items():
        if target is None:
            continue
        sub = _wide_constants(_tree_of(target), target, depth + 1)
        if attr in sub:
            consts[local] = sub[attr]
    # iterate: a constant defined in terms of one defined later needs two passes
    for _ in range(4):
        before = dict(consts)
        for name, sites in bindings.items():
            if name.startswith("__store__") or name in consts:
                continue
            for site in sorted(sites, key=lambda s: s["line"]):
                if site["value"] is None:
                    continue
                val, _why = _fold2(site["value"], consts, rel)
                if val is not None:
                    consts[name] = val
                    break
        if consts == before:
            break
    consts["__plain__"] = plain
    return consts


def _has_name(node, name="__file__"):
    return any(isinstance(n, ast.Name) and n.id == name for n in ast.walk(node))


def _parents_of(rel, steps):
    """``Path(__file__).resolve().parents[k]`` folded against the writer's own path.

    The published fold maps ``__file__`` to the root marker so that
    ``ROOT / "results"`` becomes ``results``.  ``parents[k]`` is the same fact one
    subscript further out: from ``scripts/x.py``, ``parents[1]`` is the root and
    ``parents[0]`` is ``scripts``.  Reading it off the writer's real path keeps the
    answer exact instead of assuming every script sits one level down.
    """
    p = rel
    for _ in range(steps + 1):
        p = os.path.dirname(p)
    return p.replace("\\", "/")


class _ParentsUnfold(ast.NodeTransformer):
    """Rewrite ``parents[k]`` / ``.parent`` into the constant they mean, then fold."""

    def __init__(self, rel):
        self.rel = rel

    def visit_Subscript(self, node):
        node = self.generic_visit(node)
        if isinstance(node.value, ast.Attribute) and node.value.attr == "parents" and \
                isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, int) and \
                _has_name(node.value.value):
            return ast.copy_location(
                ast.Constant(value=_parents_of(self.rel, node.slice.value)), node)
        return node

    def visit_Attribute(self, node):
        node = self.generic_visit(node)
        if node.attr == "parent" and isinstance(node.value, (ast.Call, ast.Attribute, ast.Name)) and \
                _has_name(node.value):
            return ast.copy_location(
                ast.Constant(value=_parents_of(self.rel, 0)), node)
        return node


def _fold2(expr, consts, rel):
    """e554's fold with ``parents[k]`` pre-substituted by the path it means."""
    import copy
    try:
        rewritten = _ParentsUnfold(rel).visit(copy.deepcopy(expr))
    except Exception:
        rewritten = expr
    return e554._fold(rewritten, consts)


def _resolve(expr, tree, rel):
    """(path_or_None, how_or_None) -- wider than e554's own fold, same literal rule."""
    consts = _wide_constants(tree, rel)
    val, why = _fold2(expr, consts, rel)
    if val is not None and PATHISH.match(val):
        return val, "folded_from_a_name_the_order_blind_search_binds"
    if val is not None and PATHISH.match(_norm_path(val)):
        return _norm_path(val), "folded_from_a_name_the_order_blind_search_binds"
    # ``import m`` then ``m.NAME``: e554 folds the receiver and stops.
    if isinstance(expr, ast.Attribute) and isinstance(expr.value, ast.Name):
        target = (consts.get("__plain__") or {}).get(expr.value.id)
        if target:
            sub = _wide_constants(_tree_of(target), target)
            if expr.attr in sub and PATHISH.match(sub[expr.attr]):
                return sub[expr.attr], "folded_through_an_imported_module_constant"
    return None, why


def _norm_path(v):
    v = v.replace("\\", "/")
    while v.startswith("./"):
        v = v[2:]
    return v


def _local_scope(tree, render_line):
    """e554's own scope: module constants in order plus pre-line local binds."""
    return e554._local_scope(tree, render_line, e554._module_constants(tree))


def _local_bindings(func):
    """Every name the enclosing function binds itself: loop/with targets and locals.

    ``e554._local_scope`` folds only ``NAME = <expr>`` above the render line, so a
    ``for path in ...:`` target reads as "a name this scan cannot fold" -- a statement
    about the fold, not about the name.  This census is what tells the two apart.
    """
    out = {}
    if func is None:
        return out
    for node in ast.walk(func):
        if isinstance(node, (ast.For, ast.AsyncFor)):
            for t in ast.walk(node.target):
                if isinstance(t, ast.Name):
                    out.setdefault(t.id, []).append({"line": node.lineno,
                                                     "kind": F_LOOP_WITH})
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                if item.optional_vars is not None:
                    for t in ast.walk(item.optional_vars):
                        if isinstance(t, ast.Name):
                            out.setdefault(t.id, []).append({"line": node.lineno,
                                                             "kind": F_LOOP_WITH})
        elif isinstance(node, ast.comprehension):
            for t in ast.walk(node.target):
                if isinstance(t, ast.Name):
                    out.setdefault(t.id, []).append({"line": 0, "kind": F_LOOP_WITH})
        elif isinstance(node, ast.Assign):
            tuple_target = False
            for t in node.targets:
                if isinstance(t, (ast.Tuple, ast.List)):
                    tuple_target = True
                    for elt in t.elts:
                        if isinstance(elt, ast.Name):
                            out.setdefault(elt.id, []).append(
                                {"line": node.lineno,
                                 "kind": F_TUPLE_FROM_CALL if isinstance(node.value, ast.Call)
                                 else F_LOCAL_RUNTIME})
                elif isinstance(t, ast.Name):
                    out.setdefault(t.id, []).append({"line": node.lineno,
                                                     "kind": F_LOCAL_RUNTIME})
                elif isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name):
                    out.setdefault(t.value.id, []).append({"line": node.lineno,
                                                           "kind": F_CONTAINER})
            if tuple_target:
                continue
    return out


def _row_binding(name, tree, rel, render_line, func):
    """Why the *previous* scan could not fold this name, in a fixed order.

    The order matters: a parameter is supplied by a caller whatever else the module
    does with the same spelling, and a name whose own value is ``sys.argv[2]`` is
    run-time data even though it is assigned at module level on line 4.
    """
    bindings = _module_bindings(tree)
    from_map, plain = _import_bindings(tree, rel)
    if func is not None:
        args = [a.arg for a in func.args.args + func.args.kwonlyargs]
        if func.args.vararg:
            args.append(func.args.vararg.arg)
        if func.args.kwarg:
            args.append(func.args.kwarg.arg)
        if name in args:
            return {"name": name, "kind": F_PARAMETER, "lines": []}
    if name in from_map or name in plain:
        target = from_map.get(name, (plain.get(name), None))[0]
        if target is None:
            return {"name": name, "kind": F_IMPORT_UNRESOLVED, "lines": [],
                    "module": from_map.get(name, (None, name))[0]}
        sub = _wide_constants(_tree_of(target), target)
        attr = from_map.get(name, (None, name))[1]
        if attr in sub:
            return {"name": name, "kind": F_IMPORTED, "lines": [], "module": target,
                    "value": sub[attr]}
        return {"name": name, "kind": F_IMPORTED, "lines": [], "module": target,
                "value": None}
    sites = bindings.get(name) or []
    in_order = e554._module_constants(tree)
    if name in in_order:
        # the published fold already binds it; the row's own reason lies elsewhere
        return {"name": name, "kind": F_ALREADY, "lines": [s["line"] for s in sites],
                "value": in_order[name]}
    folded_sites = []
    for site in sites:
        if site["value"] is None:
            continue
        val, _why = _fold2(site["value"], in_order, rel)
        if val is None:
            val, _why = _fold2(site["value"], _wide_constants(tree, rel), rel)
        if val is not None:
            folded_sites.append((site, val))
    if folded_sites:
        for site, val in folded_sites:
            if site["kind"] == F_NESTED:
                return {"name": name, "kind": F_NESTED, "lines": [site["line"]],
                        "value": val}
        for site, val in folded_sites:
            if site["line"] > render_line:
                return {"name": name, "kind": F_BELOW, "lines": [site["line"]],
                        "value": val}
        for site, val in folded_sites:
            return {"name": name, "kind": F_BELOW, "lines": [site["line"]], "value": val}
    for site in sites:
        if site["kind"] == F_LOOP_WITH:
            return {"name": name, "kind": F_LOOP_WITH, "lines": [site["line"]]}
    if sites:
        return {"name": name, "kind": F_RUNTIME,
                "lines": [s["line"] for s in sites if s["value"] is not None]}
    if ("__store__%s" % name) in bindings:
        return {"name": name, "kind": F_CONTAINER,
                "lines": [s["line"] for s in bindings["__store__%s" % name]]}
    local = _local_bindings(func)
    if name in local:
        kinds = [s["kind"] for s in local[name]]
        for kind in (F_TUPLE_FROM_CALL, F_LOOP_WITH, F_CONTAINER, F_LOCAL_RUNTIME):
            if kind in kinds:
                return {"name": name, "kind": kind,
                        "lines": [s["line"] for s in local[name]]}
    return {"name": name, "kind": F_NEVER, "lines": []}


F_ALREADY = "a_module_constant_the_published_fold_already_binds"


# ---------------------------------------------------------------- population
def _candidate_expressions(call):
    """The second argument, or -- for a one-argument %-format message -- its candidates.

    E554's residue contains rows like ``print("wrote %s + %s" % (a, b))``: there is no
    second argument at all, and the faces live in the format's right-hand tuple.
    """
    if len(call.args) >= 2:
        return [call.args[1]]
    if not call.args:
        return []
    first = call.args[0]
    if isinstance(first, ast.BinOp) and isinstance(first.op, ast.Mod):
        right = first.right
        return list(right.elts) if isinstance(right, ast.Tuple) else [right]
    return [first]


def population():
    cutoff, rows = _published_population()
    out = []
    for row in rows:
        rel, line = row["writer"], row["line"]
        tree = _tree_of(rel)
        item = {"writer": rel, "line": line, "argument": None, "free_names": [],
                "parameter_names": [], "bindings": [], "resolution": None,
                "fold_class": F_NO_CALL, "binding_site": None, "blocker": None,
                "closed_by": None, "face_exists_on_disk": None}
        if tree is None:
            out.append(item)
            continue
        call = e554._render_call(tree, line)
        if call is None:
            out.append(item)
            continue
        exprs = _candidate_expressions(call)
        if not exprs:
            out.append(item)
            continue
        try:
            item["argument"] = " | ".join(
                " ".join(ast.unparse(e).split()) for e in exprs)[:200]
        except Exception:
            item["argument"] = ""
        item["free_names"] = sorted({n.id for e in exprs for n in ast.walk(e)
                                     if isinstance(n, ast.Name)})
        func = e554._enclosing_function(tree, line)
        if func is not None:
            args = [a.arg for a in func.args.args + func.args.kwonlyargs]
            item["parameter_names"] = [n for n in item["free_names"] if n in args]
        for name in item["free_names"]:
            item["bindings"].append(_row_binding(name, tree, rel, line, func))

        path, how = None, None
        path_expr = None
        for expr in exprs:
            path, how = _resolve(expr, tree, rel)
            if path:
                path_expr = expr
                break
        kinds = [b["kind"] for b in item["bindings"]]
        item["blocker"] = None
        item["closed_by"] = None
        if path:
            item["fold_class"] = F_FOLDED
            if F_IMPORTED in kinds:
                item["binding_site"] = F_IMPORTED
            elif F_NESTED in kinds:
                item["binding_site"] = F_NESTED
            else:
                item["binding_site"] = F_BELOW
            item["resolution"] = {"path": path, "how": how}
            item["face_exists_on_disk"] = os.path.isfile(os.path.join(ROOT, path))
            item["closed_by"] = _closed_by(path_expr, tree, rel, line)
        elif F_ALREADY in kinds and len(set(kinds)) == 1:
            item["fold_class"] = F_ALREADY
            item["blocker"] = item["free_names"][0] if item["free_names"] else None
        elif kinds:
            # the row's own reason: the first name that explains the miss
            item["fold_class"] = None
            for kind in BLOCKING_CLASSES:
                if kind in kinds:
                    item["fold_class"] = kind
                    break
            if item["fold_class"] is None:
                item["fold_class"] = kinds[0]
            for b in item["bindings"]:
                if b["kind"] == item["fold_class"]:
                    item["blocker"] = b["name"]
                    break
        out.append(item)
    return out


def _closed_by(expr, tree, rel, line):
    """Which capability closed the row: the parents subscript, or the order-blind search."""
    if expr is None:
        return "the_published_fold_saw_it"
    val, _why = e554._fold(expr, _local_scope(tree, line))
    if val is not None:
        return "the_published_fold_saw_it"
    in_order = e554._module_constants(tree)
    val, _why = _fold2(expr, in_order, rel)
    if val is not None:
        return "the_path_parents_subscript"
    val, _why = _fold2(expr, _wide_constants(tree, rel), rel)
    if val is not None:
        return "the_order_blind_module_constant_search"
    return "an_imported_module_constant"
CLOSE_VOCAB = ("the_published_fold_saw_it", "the_path_parents_subscript",
               "the_order_blind_module_constant_search", "an_imported_module_constant")


def _control_arm(rows):
    """E554's own resolver over the same candidate expressions: it must fold none."""
    folded = 0
    for r in rows:
        if r["resolution"]:
            continue
        tree = _tree_of(r["writer"])
        if tree is None:
            continue
        call = e554._render_call(tree, r["line"])
        if call is None:
            continue
        scope = _local_scope(tree, r["line"])
        for expr in _candidate_expressions(call):
            val, _why = e554._fold(expr, scope)
            if val is not None and PATHISH.match(val):
                folded += 1
                break
    return folded


def build(write=True):
    cutoff, e554_rows = _published_population()
    rows = population()
    by_class = {c: 0 for c in FOLD_VOCAB}
    for r in rows:
        by_class[r["fold_class"]] = by_class.get(r["fold_class"], 0) + 1
    foldable = [r for r in rows if r["resolution"]]
    paths = sorted({r["resolution"]["path"] for r in foldable})
    on_disk = [r for r in foldable if r["face_exists_on_disk"]]
    constants = [r for r in rows if r["fold_class"] in CONSTANT_CLASSES]
    control = _control_arm(rows)
    by_close = {c: 0 for c in CLOSE_VOCAB}
    for r in foldable:
        by_close[r.get("closed_by")] = by_close.get(r.get("closed_by"), 0) + 1
    by_close = {k: v for k, v in by_close.items() if v}
    summary = {
        "rows": len(rows),
        "rows_e554_published": len(e554_rows),
        "by_fold_class": by_class,
        "by_closing_capability": by_close,
        "foldable_rows": len(foldable),
        "foldable_share": round(len(foldable) / len(rows), 4) if rows else 0.0,
        "distinct_faces_named_by_the_folded_rows": len(paths),
        "folded_faces_that_exist_on_disk": len(on_disk),
        "constant_rows": len(constants),
        "rows_whose_name_is_a_caller_parameter": by_class.get(F_PARAMETER, 0),
        "rows_whose_name_this_module_never_binds": by_class.get(F_NEVER, 0),
        "rows_whose_blocker_the_published_fold_already_binds": by_class.get(F_ALREADY, 0),
        "rows_with_no_render_call_at_the_published_line": by_class.get(F_NO_CALL, 0),
        "rows_that_are_run_time_by_construction": sum(
            by_class.get(c, 0) for c in (F_PARAMETER, F_LOOP_WITH, F_LOCAL_RUNTIME,
                                         F_TUPLE_FROM_CALL, F_RUNTIME, F_CONTAINER,
                                         F_IMPORT_UNRESOLVED, F_NEVER)),
        "control_arm_folds_by_the_published_resolver": control,
    }
    verdict = V_SOME_CONSTANTS if foldable else V_ALL_RUNTIME
    face = {
        "study": STUDY,
        "card": CARD,
        "title": TITLE,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "population_source": {
            "method": ("the 67 rows of E554's published face whose unresolved_because is "
                       "'%s', re-parsed at their own writer:line" % U_UNFOLDABLE_NAME),
            "source_face": os.path.relpath(e554.LATEST, ROOT).replace("\\", "/"),
            "source_face_cutoff": cutoff,
        },
        "rows": rows,
        "folded_faces": [{"path": r["resolution"]["path"],
                          "writer": r["writer"], "line": r["line"]} for r in foldable],
        "summary": summary,
        "verdict": verdict,
        "verdict_line": verdict,
        "method_note": (
            "a folded row is a constant only if the whole expression folds from literals; "
            "a parameter or a loop target is published as genuinely run-time, never as a "
            "miss of this study"),
        "method_bound": (
            "the order-blind search reads module-level bindings and plain imports to depth "
            "4; it follows no attribute chains, no function returns and no environment "
            "lookups, so 'never binds' means 'not in this module's literal surface'"),
    }
    if write:
        dated = os.path.join(STATE_TILT, "%s-%s.json" % (DATED_PREFIX, EVIDENCE_CUTOFF))
        blob = json.dumps(face, ensure_ascii=False, indent=1)
        io.open(dated, "w", encoding="utf-8", newline="\n").write(blob + "\n")
        io.open(LATEST, "w", encoding="utf-8", newline="\n").write(blob + "\n")
        print(json.dumps({"rows": len(rows),
                          "foldable": len(foldable),
                          "distinct_faces": len(paths),
                          "on_disk": len(on_disk),
                          "control_folded": control,
                          "by_class": by_class,
                          "verdict": verdict,
                          "wrote": os.path.relpath(dated, ROOT).replace("\\", "/")},
                         ensure_ascii=False))
    return face


# ---------------------------------------------------------------- gates
def _rederive_class(row):
    kinds = [b["kind"] for b in row.get("bindings") or []]
    if row.get("resolution"):
        return F_FOLDED
    if F_ALREADY in kinds and len(set(kinds)) == 1:
        return F_ALREADY
    for kind in BLOCKING_CLASSES:
        if kind in kinds:
            return kind
    return kinds[0] if kinds else row.get("fold_class")


def face_problems(face):
    probs = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if not rows:
        return ["the population is empty"]
    by_class = {c: 0 for c in FOLD_VOCAB}
    for r in rows:
        cls = r.get("fold_class")
        if cls not in FOLD_VOCAB:
            probs.append("a fold class outside the vocabulary: %s" % (cls,))
        else:
            by_class[cls] += 1
        got = _rederive_class(r)
        if cls != got:
            probs.append("a row's class is not what its own bindings say (%s:%s: %s vs %s)"
                         % (r.get("writer"), r.get("line"), cls, got))
        if r.get("resolution") and not PATHISH.match(r["resolution"].get("path") or ""):
            probs.append("a folded row names something that is not a face path (%s:%s)"
                         % (r.get("writer"), r.get("line")))
        if r.get("resolution") and r.get("fold_class") not in CONSTANT_CLASSES:
            probs.append("a folded row is classified as a run-time value (%s:%s)"
                         % (r.get("writer"), r.get("line")))
        if r.get("fold_class") in CONSTANT_CLASSES and not r.get("resolution"):
            probs.append("a constant-class row resolved nothing (%s:%s)"
                         % (r.get("writer"), r.get("line")))
        if r.get("fold_class") in CONSTANT_CLASSES and r.get("parameter_names") and \
                all(n in (r.get("parameter_names") or []) for n in r.get("free_names") or []):
            probs.append("a row called a constant is supplied only by parameters (%s:%s)"
                         % (r.get("writer"), r.get("line")))
        if r.get("resolution") and r.get("closed_by") not in CLOSE_VOCAB:
            probs.append("a folded row does not say which capability closed it (%s:%s)"
                         % (r.get("writer"), r.get("line")))
        if r.get("fold_class") in CONSTANT_CLASSES and r.get("binding_site") not in BINDING_VOCAB:
            probs.append("a folded row does not publish where its name is bound (%s:%s)"
                         % (r.get("writer"), r.get("line")))
        if not r.get("resolution") and r.get("blocker") not in (r.get("free_names") or [None]):
            probs.append("a blocking row does not name the blocker among its free names (%s:%s)"
                         % (r.get("writer"), r.get("line")))
    foldable = [r for r in rows if r.get("resolution")]
    paths = {r["resolution"]["path"] for r in foldable}
    expected = {
        "rows": len(rows),
        "by_fold_class": by_class,
        "foldable_rows": len(foldable),
        "foldable_share": round(len(foldable) / len(rows), 4) if rows else 0.0,
        "distinct_faces_named_by_the_folded_rows": len(paths),
        "folded_faces_that_exist_on_disk": sum(1 for r in foldable if r.get("face_exists_on_disk")),
        "constant_rows": sum(1 for r in rows if r.get("fold_class") in CONSTANT_CLASSES),
        "rows_whose_name_is_a_caller_parameter": by_class.get(F_PARAMETER, 0),
        "rows_whose_name_this_module_never_binds": by_class.get(F_NEVER, 0),
        "rows_whose_blocker_the_published_fold_already_binds": by_class.get(F_ALREADY, 0),
        "rows_with_no_render_call_at_the_published_line": by_class.get(F_NO_CALL, 0),
        "rows_that_are_run_time_by_construction": sum(
            by_class.get(c, 0) for c in (F_PARAMETER, F_LOOP_WITH, F_LOCAL_RUNTIME,
                                         F_TUPLE_FROM_CALL, F_RUNTIME, F_CONTAINER,
                                         F_IMPORT_UNRESOLVED, F_NEVER)),
        "by_closing_capability": {c: 0 for c in CLOSE_VOCAB},
    }
    for r in rows:
        if r.get("closed_by") in expected["by_closing_capability"]:
            expected["by_closing_capability"][r["closed_by"]] += 1
    expected["by_closing_capability"] = {k: v for k, v in expected["by_closing_capability"].items() if v}
    for key, val in expected.items():
        if s.get(key) != val:
            probs.append("summary %s=%r but the rows say %r" % (key, s.get(key), val))
    if s.get("control_arm_folds_by_the_published_resolver") not in (0,):
        probs.append("the control arm folded %r rows: the population is not E554's residue"
                     % (s.get("control_arm_folds_by_the_published_resolver"),))
    want = V_SOME_CONSTANTS if foldable else V_ALL_RUNTIME
    if face.get("verdict") != want:
        probs.append("the verdict is not what the rows derive (%r vs %r)"
                     % (face.get("verdict"), want))
    published_paths = {f.get("path") for f in face.get("folded_faces") or []}
    if published_paths != paths:
        probs.append("the folded_faces list is not the one the rows name")
    if not face.get("evidence_cutoff"):
        probs.append("the face carries no evidence_cutoff")
    return probs


def check():
    pub = json.load(io.open(LATEST, encoding="utf-8"))
    problems = list(face_problems(pub))
    fresh = build(write=False)
    if [(r["writer"], r["line"]) for r in fresh["rows"]] != \
            [(r["writer"], r["line"]) for r in pub["rows"]]:
        problems.append("the published population is not the one the sources have now")
    else:
        for a, b in zip(fresh["rows"], pub["rows"]):
            if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
                problems.append("a published row is not what the sources say now (%s:%s)"
                                % (a["writer"], a["line"]))
    if fresh["verdict"] != pub["verdict"]:
        problems.append("the published verdict is not the one the sources derive now")
    print(json.dumps({"problems": problems, "verdict": pub.get("verdict"),
                      "rows": len(pub.get("rows") or []),
                      "foldable": (pub.get("summary") or {}).get("foldable_rows")},
                     ensure_ascii=False))
    return 1 if problems else 0


def verify():
    a, b = build(write=False), build(write=False)
    problems = [] if json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True) else \
        ["two builds of the same sources differ"]
    if not problems:
        problems = list(face_problems(a))
    print(json.dumps({"problems": problems}, ensure_ascii=False))
    return 1 if problems else 0


# ---------------------------------------------------------------- selftest
_FIXTURE_BELOW = textwrap.dedent("""\
    import os
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def emit(out):
        print("wrote", OUT)

    OUT = os.path.join(ROOT, "results", "state_tilt", "later.json")
    """)

_FIXTURE_NESTED = textwrap.dedent("""\
    import os
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        TARGET = os.path.join(ROOT, "results", "state_tilt", "guarded.json")
    except OSError:
        TARGET = "results/state_tilt/guarded.json"

    def emit():
        print("wrote", TARGET)
    """)

_FIXTURE_PARENTS = textwrap.dedent("""\
    import os
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
    RESULTS = ROOT / "results"
    OUT = RESULTS / "parents_fixture.json"

    def emit():
        print("wrote", OUT)
    """)

_FIXTURE_LOOP = textwrap.dedent("""\
    import os
    def emit(paths):
        for path in paths:
            print("wrote", path)
    """)

_FIXTURE_TUPLE = textwrap.dedent("""\
    def _write(face):
        return "a", "b"

    def emit():
        dated, latest = _write({})
        print("wrote", dated)
    """)

_FIXTURE_IMPORTED = textwrap.dedent("""\
    from fake_consts import OUT as REAL_OUT

    def emit():
        print("wrote", REAL_OUT)
    """)

_FIXTURE_PARAM = textwrap.dedent("""\
    def emit(path):
        print("wrote", path)
    """)

_FIXTURE_NEVER = textwrap.dedent("""\
    def emit():
        print("wrote", something_from_nowhere)
    """)


def _fixture_face(text, rel="scripts/_e555_fixture.py"):
    tree = ast.parse(text)
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Name) and n.func.id == "print"]
    call = e554._render_call(tree, calls[0].lineno)
    consts = _wide_constants(tree, rel)
    val, _why = _fold2(call.args[1], consts, rel)
    return tree, call, val


def selftest():
    fails = []
    n = 0

    def ok(label, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(label)

    # 1. a constant written below the message folds under the wider search
    tree, call, val = _fixture_face(_FIXTURE_BELOW)
    ok("a constant defined below the message folds", val == "results/state_tilt/later.json")

    # 2. the published fold already reads module-level constants order-blind, so this
    #    study claims no order capability -- the leg pins that fact instead of assuming it
    prev, _why = e554._fold(call.args[1], e554._module_constants(ast.parse(_FIXTURE_BELOW)))
    ok("the published fold is already order-blind for module constants", prev is not None)

    # 3. a constant inside a try block folds
    _t, _c, val = _fixture_face(_FIXTURE_NESTED)
    ok("a constant defined inside a conditional block folds",
       val == "results/state_tilt/guarded.json")

    # 4. a parameter is not a constant and must not fold
    _t, _c, val = _fixture_face(_FIXTURE_PARAM)
    ok("a caller parameter does not fold", val is None)

    # 5. a name the module never binds does not fold
    _t, _c, val = _fixture_face(_FIXTURE_NEVER)
    ok("an unbound name does not fold", val is None)

    # 5b. Path(__file__).resolve().parents[1] is the root, and the face under it folds
    _t, _c, val = _fixture_face(_FIXTURE_PARENTS)
    ok("a constant behind a parents subscript folds",
       val == "results/parents_fixture.json")
    ok("the published fold does not fold the parents fixture",
       e554._fold(_c.args[1], e554._module_constants(ast.parse(_FIXTURE_PARENTS)))[0] is None)

    # 5c. a loop target is a run-time value, and it is not called "never bound"
    tree = ast.parse(_FIXTURE_LOOP)
    call = e554._render_call(tree, [n.lineno for n in ast.walk(tree)
                                    if isinstance(n, ast.Call)][0])
    func = e554._enclosing_function(tree, call.lineno)
    kind = _row_binding("path", tree, "scripts/_e555_fixture.py", call.lineno, func)["kind"]
    ok("a loop target is classified as a loop target", kind == F_LOOP_WITH)

    # 5d. a tuple target of a helper call is a run-time value
    tree = ast.parse(_FIXTURE_TUPLE)
    call = e554._render_call(tree, [n.lineno for n in ast.walk(tree)
                                    if isinstance(n, ast.Call)
                                    and isinstance(n.func, ast.Name) and n.func.id == "print"][0])
    func = e554._enclosing_function(tree, call.lineno)
    kind = _row_binding("dated", tree, "scripts/_e555_fixture.py", call.lineno, func)["kind"]
    ok("a tuple target of a call is classified as such", kind == F_TUPLE_FROM_CALL)

    # 5e. an import whose module is not in the tree is not called a constant
    tree = ast.parse(_FIXTURE_IMPORTED)
    call = e554._render_call(tree, [n.lineno for n in ast.walk(tree)
                                    if isinstance(n, ast.Call)][0])
    func = e554._enclosing_function(tree, call.lineno)
    kind = _row_binding("REAL_OUT", tree, "scripts/_e555_fixture.py", call.lineno, func)["kind"]
    ok("an import from outside the tree is published as unresolved",
       kind == F_IMPORT_UNRESOLVED)

    # 6. the wider search never invents a non-face string
    ok("the wider search never names a non-face path",
       not (val and not PATHISH.match(val)))

    # 7. the published class of a fixture row re-derives
    ok("a folded row re-derives its class",
       _rederive_class({"resolution": {"path": "results/x.json"},
                        "bindings": [{"kind": F_BELOW}]}) == F_FOLDED)
    ok("a parameter row re-derives its class",
       _rederive_class({"resolution": None, "bindings": [{"kind": F_PARAMETER}]}) == F_PARAMETER)

    # 8. the live population is exactly E554's residue
    cutoff, e554_rows = _published_population()
    rows = population()
    ok("the population is the published residue of the previous fold",
       len(rows) == len(e554_rows))
    ok("every row carries E554's reason",
       all(r["fold_class"] in FOLD_VOCAB for r in rows))

    # 9. the control arm folds nothing (live)
    ok("the published resolver folds none of the residue", _control_arm(rows) == 0)

    # 10. a folded row is always a constant class and carries a path
    ok("every folded row is a constant class",
       all(r["fold_class"] in CONSTANT_CLASSES for r in rows if r["resolution"]))

    # 11. the face on disk agrees with its own rows (published, not rebuilt)
    try:
        pub = json.load(io.open(LATEST, encoding="utf-8"))
        ok("the published face is free of gate problems", face_problems(pub) == [])
    except OSError:
        fails.append("the published face is missing")

    # 12. the face is written with LF only
    try:
        raw = io.open(LATEST, "rb").read()
        ok("the published face carries no CR", b"\r" not in raw)
    except OSError:
        fails.append("the published face is missing")

    print("%d/%d legs green" % (n - len(fails), n))
    for f in fails:
        print("FAIL: %s" % f)
    return 1 if fails else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        build()
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    if cmd == "population":
        rows = population()
        print(json.dumps({"rows": len(rows),
                          "foldable": sum(1 for r in rows if r["resolution"])},
                         ensure_ascii=False))
        return 0
    raise SystemExit("unknown command: %s (build|check|verify|selftest|population)" % cmd)


if __name__ == "__main__":
    sys.exit(main())