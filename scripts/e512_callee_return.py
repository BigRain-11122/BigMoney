"""E512 -- when the site's value enters through the right-hand side of a single binding, what
can the callee name?

E511 anatomised the four pair sites E510 could not collapse and found that three of them are
"one in-scope binding, the value enters through the right-hand side": ``asof = tk[...] or
"unknown"`` where ``tk = card_config_ticket(nav=nav)``.  That verdict stops one hop short.  A
binding whose right-hand side is a *call* has a second author -- the callee -- and the callee may
name one kind of value on every path (in which case the residual ambiguity is read out of it) or
branch over more than one (in which case the ambiguity is real and belongs to the callee's
contract).

This study follows that hop.  Population, two arms, both taken from published faces and never
re-derived from E507's raw pairs:

  * arm ``the_sites_own_binding_is_a_call_result``: E510's published pairs whose single in-scope
    binding has the shape ``call_result`` (E511's binder re-derives the shape from the line);
  * arm ``the_sites_value_reads_an_operand_that_is_a_call_result``: E511's published sites whose
    resolution is ``operand_read_what_the_right_hand_side_actually_returns``.

Per site it publishes the call expression, the callee (same module / imported / builtin / not a
repo function), every return statement of the callee with the *kind of value it names*, whether
the site reads a dict key and where that key's value ultimately comes from (a file read, a
series element, a parameter, a clock, a constant), and whether a guard between the call and the
site terminates on the arm that names nothing -- because a callee that returns ``None`` on a
missing input is not a callee that hands the site two values.

Modes: run|build / check / verify / selftest.  Read-only: check, verify, selftest.
"""
import ast
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import e504_name_compose as base  # noqa: E402
import e507_unresolved_origin as e507  # noqa: E402
import e510_binding_scope as e510  # noqa: E402
import e511_collision_anatomy as e511  # noqa: E402

ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "calleereturn_latest.json"
DATED_PREFIX = "CALLEERETURN"
DATE_STAMP = "2026-11-07"
CARD = "E512-WHAT-DOES-THE-CALLEE-RETURN-WHEN-THE-SITES-ONLY-BINDING-READS-A-CALL"
STUDY = "E512_callee_return"
UPSTREAM_510 = os.path.join("results", "state_tilt", "SCOPEDBINDING-2026-11-07.json")
UPSTREAM_511 = os.path.join("results", "state_tilt", "COLLISIONANATOMY-2026-11-07.json")
POPULATION_SOURCE = ("results/state_tilt/SCOPEDBINDING-2026-11-07.json pairs whose single "
                     "in-scope binding has shape call_result, plus "
                     "results/state_tilt/COLLISIONANATOMY-2026-11-07.json sites whose "
                     "resolution is operand_read_what_the_right_hand_side_actually_returns")
SELF_EXCLUDED = ("e512_", "run_e512", "_e512")

# ------------------------------------------------------------------ vocabulary
ARM_CALL_BINDING = "the_sites_own_binding_is_a_call_result"
ARM_OPERAND = "the_sites_value_reads_an_operand_that_is_a_call_result"
ARM_VOCAB = (ARM_CALL_BINDING, ARM_OPERAND)

CALLEE_SAME_MODULE = "callee_defined_in_the_site_module"
CALLEE_IMPORTED = "callee_defined_in_another_repo_module"
CALLEE_BUILTIN = "callee_is_a_builtin_that_coerces_its_argument"
CALLEE_OTHER = "callee_is_neither_a_repo_function_nor_a_builtin"
CALLEE_UNRESOLVED = "the_call_could_not_be_resolved"
CALLEE_NOT_A_CALL = "the_binding_is_not_a_call_at_all"
CALLEE_VOCAB = (CALLEE_SAME_MODULE, CALLEE_IMPORTED, CALLEE_BUILTIN, CALLEE_OTHER,
                CALLEE_UNRESOLVED, CALLEE_NOT_A_CALL)

RT_BARE_NONE = "bare_return_names_nothing"
RT_LITERAL_NONE = "literal_None"
RT_DICT = "dict_literal"
RT_TUPLE = "tuple_literal"
RT_COMPREHENSION = "comprehension_built_from_something"
RT_CALL = "call_result"
RT_SUBSCRIPT = "subscript_of_another_object"
RT_NAME = "another_name"
RT_LITERAL = "literal_constant"
RT_EXPRESSION = "an_expression"
RT_OTHER = "other"
RETURN_VOCAB = (RT_BARE_NONE, RT_LITERAL_NONE, RT_DICT, RT_TUPLE, RT_COMPREHENSION, RT_CALL,
                RT_SUBSCRIPT, RT_NAME, RT_LITERAL, RT_EXPRESSION, RT_OTHER)
NAMES_NOTHING = (RT_BARE_NONE, RT_LITERAL_NONE)

O_FILE = "a_value_read_from_a_file"
O_SERIES = "an_element_of_a_loaded_series"
O_PARAMETER = "a_parameter_of_the_callee"
O_CLOCK = "the_run_clock"
O_CONSTANT = "a_literal_constant"
O_BUILT_BY_A_CALL = "a_value_built_by_a_call_into_another_module"
O_OTHER = "something_else"
O_NONE = "the_site_reads_no_field_off_the_call"
ORIGIN_VOCAB = (O_FILE, O_SERIES, O_PARAMETER, O_CLOCK, O_CONSTANT, O_BUILT_BY_A_CALL, O_OTHER,
                O_NONE)

S_SAME = "the_callee_names_one_kind_on_every_path_so_it_answers_the_site"
S_GUARDED = "the_callee_branches_but_a_terminating_guard_filters_the_empty_arm"
S_REAL = "the_callee_branches_and_nothing_filters_an_arm_at_the_site"
S_NOT_REPO = "the_call_is_not_a_repo_function_so_the_value_is_its_argument"
S_NOT_CALL = "the_binding_does_not_call_anything"
SITE_VOCAB = (S_SAME, S_GUARDED, S_REAL, S_NOT_REPO, S_NOT_CALL)

V_RESOLVED = "every_site_is_answered_by_reading_its_callee_or_its_argument"
V_PART = "some_sites_are_answered_by_the_callee_and_some_really_read_whatever_arrives"
V_REAL = "no_site_is_answered_by_its_callee"
V_EMPTY = "the_published_faces_hold_no_operand_level_site"
VERDICT_VOCAB = (V_RESOLVED, V_PART, V_REAL, V_EMPTY)

BUILTINS = frozenset(("str", "int", "float", "bool", "list", "dict", "tuple", "set", "repr",
                      "len", "abs", "round", "sorted", "min", "max", "format"))
READ_WORDS = ("_read", "load", "read_", "readtext", "_load", "loads", "iterrows", "open")
CLOCK_WORDS = ("now", "today", "utcnow", "time()", "date.today")


# ---------------------------------------------------------------- population
def _face(root, rel):
    return base._load_json(os.path.join(root, rel))


def population(root=None, up510=None, up511=None):
    """The published sites, as (arm, source, line, date_expression, symbol) records."""
    root = root or ROOT
    out = []
    seen = set()
    face510 = up510 if up510 is not None else _face(root, UPSTREAM_510)
    for pair in (face510.get("pairs") or []):
        source = pair.get("source") or ""
        line = pair.get("line") or 0
        symbol = ((pair.get("bindings") or {}).get("symbol")) or ""
        if not source or not line or not symbol:
            continue
        design = e511.design_of(root, source, line, symbol)
        shapes = [b.get("shape") for b in (design.get("bindings") or [])]
        if not shapes or any(shape != "call_result" for shape in shapes):
            continue
        key = (ARM_CALL_BINDING, source, line, pair.get("date_expression") or "")
        if key in seen:
            continue
        seen.add(key)
        out.append({"arm": ARM_CALL_BINDING, "source": source, "line": line,
                    "date_expression": pair.get("date_expression") or "",
                    "symbol": symbol})
    face511 = up511 if up511 is not None else _face(root, UPSTREAM_511)
    for site in (face511.get("sites") or []):
        if site.get("resolution") != e511.RESOLVE_OPERAND:
            continue
        key = (ARM_OPERAND, site.get("source") or "", site.get("line") or 0,
               site.get("date_expression") or "")
        if key in seen:
            continue
        seen.add(key)
        out.append({"arm": ARM_OPERAND, "source": site.get("source") or "",
                    "line": site.get("line") or 0,
                    "date_expression": site.get("date_expression") or "",
                    "symbol": site.get("symbol") or ""})
    return sorted(out, key=lambda s: (s["source"], s["line"], s["arm"]))


# -------------------------------------------------------------- node walking
def _assign_nodes(scope_node):
    """Every simple ``name = value`` inside one function body (nested defs excluded)."""
    out = []

    def rec(node):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) and \
                node is not scope_node:
            return
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    out.append((target.id, node.value, node.lineno))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                and node.value is not None:
            out.append((node.target.id, node.value, node.lineno))
        for child in ast.iter_child_nodes(node):
            rec(child)

    for stmt in getattr(scope_node, "body", []):
        rec(stmt)
    return out


def _binding_at(ctx, fn, symbol, before_line, skip=frozenset()):
    """(value, line) for the last write of ``symbol`` at or above ``before_line``.

    ``skip`` carries the write lines this chain has already consumed, so a rebinding such as
    ``slip = slip[slip.index >= start]`` steps back to the write before it instead of reading
    itself forever (which would silently become "something_else").
    """
    best = None
    pool = _assign_nodes(fn) if fn is not None else []
    for name, value, line in pool:
        if name != symbol or line > before_line or line in skip:
            continue
        if best is None or line > best[0]:
            best = (line, value)
    for value in (ctx.get("assigns") or {}).get(symbol) or []:
        line = getattr(value, "lineno", 0)
        if line > before_line or line in skip:
            continue
        if best is None or line > best[0]:
            best = (line, value)
    return (best[1], best[0]) if best else (None, 0)


def _binding_value(ctx, fn, symbol, before_line):
    """The value node ``symbol`` was last bound to at or above ``before_line``."""
    return _binding_at(ctx, fn, symbol, before_line)[0]


def _unparen(node):
    while isinstance(node, ast.IfExp):
        return node.body
    return node


def _first_call(node):
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            return sub
    return None


def _enclosing_def(tree, lineno, name=""):
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", None) or (node.lineno + 10 ** 6)
            if node.lineno <= lineno <= end and (not name or node.name == name):
                if best is None or node.lineno > best.lineno:
                    best = node
    return best


# -------------------------------------------------------------------- callee
def _callee(root, ctx, call):
    """Resolve the call's function to a repo definition, a builtin, or nothing."""
    func = call.func
    if isinstance(func, ast.Name):
        if func.id in ctx["funcs"]:
            return {"class": CALLEE_SAME_MODULE, "name": func.id,
                    "rel": ctx["rel"], "node": ctx["funcs"][func.id],
                    "line": ctx["funcs"][func.id].lineno}
        dotted = (ctx.get("imports") or {}).get(func.id)
        if dotted:
            got = _imported(root, dotted.rsplit(".", 1)[0], dotted.rsplit(".", 1)[-1])
            if got is not None:
                return got
        if func.id in BUILTINS:
            return {"class": CALLEE_BUILTIN, "name": func.id, "rel": "", "node": None,
                    "line": 0}
        return {"class": CALLEE_OTHER, "name": func.id, "rel": "", "node": None, "line": 0}
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        dotted = (ctx.get("imports") or {}).get(func.value.id) or ""
        if dotted:
            got = _imported(root, dotted.rsplit(".", 1)[0], func.attr)
            if got is not None:
                return got
        if func.attr in BUILTINS:
            return {"class": CALLEE_BUILTIN, "name": func.attr, "rel": "", "node": None,
                    "line": 0}
        return {"class": CALLEE_OTHER, "name": func.attr, "rel": "", "node": None, "line": 0}
    return {"class": CALLEE_UNRESOLVED, "name": "", "rel": "", "node": None, "line": 0}


def _imported(root, module, attr):
    path = e507._module_file(root, module)
    if path is None:
        return None
    rel = base._rel(path, root)
    ctx = e507.ctx_of(root, rel)
    if ctx is None or attr not in (ctx.get("funcs") or {}):
        return None
    fn = ctx["funcs"][attr]
    return {"class": CALLEE_IMPORTED, "name": attr, "rel": ctx["rel"], "node": fn,
            "line": fn.lineno}


def return_kind(value):
    if value is None:
        return RT_BARE_NONE
    if isinstance(value, ast.Constant) and value.value is None:
        return RT_LITERAL_NONE
    if isinstance(value, ast.Dict):
        return RT_DICT
    if isinstance(value, ast.Tuple):
        return RT_TUPLE
    if isinstance(value, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
        return RT_COMPREHENSION
    if isinstance(value, ast.Call):
        return RT_CALL
    if isinstance(value, ast.Subscript):
        return RT_SUBSCRIPT
    if isinstance(value, ast.Name):
        return RT_NAME
    if isinstance(value, ast.Constant):
        return RT_LITERAL
    if isinstance(value, (ast.BinOp, ast.JoinedStr, ast.BoolOp, ast.IfExp, ast.Compare)):
        return RT_EXPRESSION
    return RT_OTHER


def return_paths(fn):
    """Every ``return`` in the callee, with the kind of value it names.

    A nested ``def`` inside the callee is another author, so its returns are not this callee's
    paths and are excluded (they are counted separately and published).
    """
    paths, nested = [], []
    own = set()
    for node in ast.walk(fn):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node is not fn:
            own.add(id(node))
    for node in ast.walk(fn):
        if not isinstance(node, ast.Return):
            continue
        if any(_inside(node, sub, fn) for sub in ast.walk(fn)
               if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and sub is not fn):
            nested.append(node.lineno)
            continue
        paths.append({"line": node.lineno, "kind": return_kind(node.value),
                      "expr": _excerpt(node.value)})
    return sorted(paths, key=lambda p: p["line"]), sorted(nested)


def _inside(node, outer, fn):
    if outer is fn:
        return False
    start = outer.lineno
    end = getattr(outer, "end_lineno", None) or start
    return start <= getattr(node, "lineno", 0) <= end


def _excerpt(node, limit=120):
    if node is None:
        return ""
    try:
        text = ast.unparse(node)
    except Exception:
        return ""
    text = " ".join(str(text).split())
    return text[:limit]


DICT_KEY_READS = (ast.Subscript,)


def _dict_key_read(node):
    """The constant key the site reads off a dict, when it reads one."""
    for sub in ast.walk(node):
        if isinstance(sub, ast.Subscript) and isinstance(sub.slice, ast.Constant) \
                and isinstance(sub.slice.value, str):
            base_name = sub.value
            if isinstance(base_name, ast.Name):
                return sub.slice.value, base_name.id
    return None, ""


def _dict_return_for(paths_nodes, name):
    for node in paths_nodes:
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == name:
                    return value
    return None


def provenance(node, fn, ctx, root, depth=0, params=frozenset(), skip=frozenset()):
    """What the callee's value ultimately holds, following names back a bounded number of hops."""
    if node is None or depth > 8:
        return O_OTHER, ""
    if isinstance(node, ast.BoolOp):
        return provenance(node.values[0], fn, ctx, root, depth, params, skip)
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name):
            low = func.id.lower()
            if any(word in low for word in READ_WORDS):
                return O_FILE, func.id
            if any(word in low for word in CLOCK_WORDS):
                return O_CLOCK, func.id
            if func.id in BUILTINS and node.args:
                return provenance(node.args[0], fn, ctx, root, depth + 1, params, skip)
            if func.id in (ctx.get("funcs") or {}):
                return O_OTHER, func.id + "()"
            return O_OTHER, func.id + "()"
        if isinstance(func, ast.Attribute):
            attr = func.attr
            if isinstance(func.value, ast.Name) and \
                    func.value.id in (ctx.get("imports") or {}):
                # a value built by another module's function: readable as "not this module",
                # and not claimed to be a file read (that hop is not followed here)
                return O_BUILT_BY_A_CALL, func.value.id + "." + attr + "()"
            if attr in ("date", "strftime", "isoformat"):
                got, how = provenance(func.value, fn, ctx, root, depth + 1, params, skip)
                return (O_SERIES if got == O_FILE else got), attr + "()"
            got, how = provenance(func.value, fn, ctx, root, depth + 1, params, skip)
            if got == O_FILE and attr in ("get", "values", "items", "keys"):
                return O_FILE, attr
            return got, attr
        return O_OTHER, ""
    if isinstance(node, ast.Subscript):
        return provenance(node.value, fn, ctx, root, depth + 1, params, skip)
    if isinstance(node, ast.Attribute):
        return provenance(node.value, fn, ctx, root, depth + 1, params, skip)
    if isinstance(node, ast.Name):
        if fn is not None and node.id in (getattr(fn, "params", None) or set()):
            return O_PARAMETER, node.id
        bound, bline = _binding_at(ctx, fn, node.id, getattr(node, "lineno", 10 ** 9), skip)
        if bound is None:
            if node.id in params or node.id in (ctx.get("params") or set()):
                return O_PARAMETER, node.id
            return O_OTHER, node.id
        got, how = provenance(bound, fn, ctx, root, depth + 1, params, skip | {bline})
        return got, how or node.id
    if isinstance(node, ast.Constant):
        return O_CONSTANT, repr(node.value)[:40]
    return O_OTHER, ""


def argument_names(fn):
    """Every parameter name of a function definition, positional and keyword."""
    args = getattr(fn, "args", None)
    if args is None:
        return set()
    names = {a.arg for a in list(getattr(args, "posonlyargs", []) or [])
             + list(getattr(args, "args", []) or [])
             + list(getattr(args, "kwonlyargs", []) or [])}
    for extra in (args.vararg, args.kwarg):
        if extra is not None:
            names.add(extra.arg)
    return names


def params_visible(tree, lineno):
    """The parameter names of every scope that encloses this line (the value enters the module)."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            end = getattr(node, "end_lineno", None) or (node.lineno + 10 ** 6)
            if node.lineno <= lineno <= end:
                names |= argument_names(node)
    return names


def guards_between(tree, lo, hi, symbol):
    """``if`` statements over the symbol between the call and the site."""
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        if not (lo < node.lineno <= hi):
            continue
        names = {sub.id for sub in ast.walk(node.test) if isinstance(sub, ast.Name)}
        if symbol not in names:
            continue
        terminates = any(isinstance(sub, (ast.Return, ast.Raise, ast.Continue, ast.Break))
                         for arm in (node.body, node.orelse) for stmt in arm
                         for sub in ast.walk(stmt))
        hits.append({"line": node.lineno, "test": _excerpt(node.test),
                     "terminates_before_the_site": bool(terminates)})
    return sorted(hits, key=lambda g: g["line"])


# ------------------------------------------------------------------ analysis
def _site(root, site):
    ctx = e507.ctx_of(root, site["source"])
    record = dict(site)
    record.update({"callee": {}, "callee_class": CALLEE_NOT_A_CALL, "callee_name": "",
                   "callee_rel": "", "callee_line": 0, "call_expression": "",
                   "call_line": 0, "binding_line": 0, "binding_shape": "",
                   "return_path_count": 0, "return_paths": [], "return_kinds": {},
                   "returns_one_kind": False, "nested_def_return_count": 0,
                   "guards_between": [], "empty_arm_filtered": False,
                   "field_key": "", "field_origin": O_NONE, "field_origin_via": "",
                   "verdict": S_NOT_CALL})
    if ctx is None:
        record["verdict"] = S_NOT_CALL
        return record
    symbol = site["symbol"]
    fn = _enclosing_def(ctx["tree"], site["line"])
    design = e511.design_of(root, site["source"], site["line"], symbol)
    bindings = design.get("bindings") or []
    record["binding_shape"] = (bindings[0].get("shape") if bindings else "")
    record["binding_line"] = (bindings[0].get("line") if bindings else 0)
    value = None
    guard_symbol = symbol
    if site["arm"] == ARM_OPERAND:
        operand = (e511._operand_evidence(root, site["source"], site["line"], symbol,
                                          design.get("bindings") or []) or [{}])[0]
        record["binding_line"] = operand.get("line") or record["binding_line"]
        guard_symbol = operand.get("symbol") or symbol
        value = _binding_value(ctx, fn, operand.get("symbol") or "", site["line"])
        if value is None:
            value = _binding_value(ctx, fn, symbol, site["line"])
    else:
        value = _binding_value(ctx, fn, symbol, site["line"])
    call = _first_call(value) if value is not None else None
    if call is None:
        record["verdict"] = S_NOT_CALL
        return record
    record["call_expression"] = _excerpt(call)
    record["call_line"] = call.lineno
    callee = _callee(root, ctx, call)
    record["callee_class"] = callee["class"]
    record["callee_name"] = callee["name"]
    record["callee_rel"] = callee.get("rel") or ""
    record["callee_line"] = callee.get("line") or 0
    record["callee"] = {"class": callee["class"], "name": callee["name"],
                        "rel": callee.get("rel") or "", "line": callee.get("line") or 0}
    if callee["class"] in (CALLEE_SAME_MODULE, CALLEE_IMPORTED):
        paths, nested = return_paths(callee["node"])
        record["return_paths"] = paths
        record["return_path_count"] = len(paths)
        kinds = {}
        for path in paths:
            kinds[path["kind"]] = kinds.get(path["kind"], 0) + 1
        record["return_kinds"] = kinds
        record["returns_one_kind"] = len(kinds) == 1
        record["nested_def_return_count"] = len(nested)
        # the callee's own scope for name lookups
        cctx = ctx if callee["class"] == CALLEE_SAME_MODULE else e507.ctx_of(root, callee["rel"])
        # the key the site reads is on the *site symbol's* own binding, not on the operand's
        site_value = _binding_value(ctx, fn, symbol, site["line"])
        key, _owner = _dict_key_read(site_value) if site_value is not None else (None, "")
        record["field_key"] = key or ""
        if key and cctx is not None:
            nodes = [n for n in ast.walk(callee["node"]) if isinstance(n, ast.Return)]
            target = _dict_return_for([n.value for n in nodes], key)
            if target is not None:
                got, how = provenance(target, callee["node"], cctx, root, 0,
                                      params_visible(cctx["tree"], target.lineno))
                record["field_origin"] = got
                record["field_origin_via"] = how
        record["guards_between"] = guards_between(ctx["tree"], record["call_line"],
                                                  site["line"], guard_symbol)
        record["empty_arm_filtered"] = bool(
            any(k in NAMES_NOTHING for k in record["return_kinds"])
            and any(g["terminates_before_the_site"] for g in record["guards_between"]))
        record["verdict"] = _site_verdict(record)
    elif callee["class"] in (CALLEE_BUILTIN, CALLEE_OTHER):
        record["field_origin"], record["field_origin_via"] = (
            provenance(call.args[0], fn, ctx, root, 0, params_visible(ctx["tree"], call.lineno))
            if call.args else (O_OTHER, ""))
        record["verdict"] = S_NOT_REPO
    else:
        record["verdict"] = S_NOT_CALL
    return record


def _site_verdict(rec):
    kinds = rec.get("return_kinds") or {}
    if not kinds:
        return S_NOT_CALL
    if len(kinds) == 1:
        return S_SAME
    if rec.get("empty_arm_filtered"):
        return S_GUARDED
    return S_REAL


def _expected_verdict(rec):
    """The verdict the published callee class and path kinds imply, for the gate."""
    callee_class = rec.get("callee_class")
    if callee_class in (CALLEE_SAME_MODULE, CALLEE_IMPORTED):
        return _site_verdict(rec)
    if callee_class in (CALLEE_BUILTIN, CALLEE_OTHER):
        return S_NOT_REPO
    return S_NOT_CALL


def analyse(root=None, up510=None, up511=None):
    root = root or ROOT
    return [_site(root, site) for site in population(root, up510=up510, up511=up511)]


def _count(records, key, vocab):
    got = {k: 0 for k in vocab}
    for rec in records:
        value = rec.get(key)
        got[value] = got.get(value, 0) + 1
    return got


def _summary(records):
    by_site = _count(records, "verdict", SITE_VOCAB)
    by_callee = _count(records, "callee_class", CALLEE_VOCAB)
    by_origin = _count(records, "field_origin", ORIGIN_VOCAB)
    return {
        "sites": len(records),
        "sites_by_arm": _count(records, "arm", ARM_VOCAB),
        "sites_by_verdict": by_site,
        "sites_by_callee_class": by_callee,
        "sites_by_field_origin": by_origin,
        "distinct_callees": len({r.get("callee_name") for r in records
                                 if r.get("callee_class") in (CALLEE_SAME_MODULE,
                                                              CALLEE_IMPORTED)}),
        "sites_whose_callee_is_a_repo_function": sum(
            1 for r in records if r.get("callee_class") in (CALLEE_SAME_MODULE,
                                                           CALLEE_IMPORTED)),
        "sites_whose_callee_is_a_builtin": by_callee.get(CALLEE_BUILTIN, 0),
        "sites_whose_callee_branches_over_more_than_one_kind": sum(
            1 for r in records if r.get("return_path_count", 0) > 1
            and not r.get("returns_one_kind")),
        "sites_whose_empty_arm_is_filtered_by_a_guard": sum(
            1 for r in records if r.get("empty_arm_filtered")),
        "sites_that_read_whatever_arrives": by_site.get(S_REAL, 0),
        "sites_answered_by_reading_their_callee_or_argument": (
            by_site.get(S_SAME, 0) + by_site.get(S_GUARDED, 0) + by_site.get(S_NOT_REPO, 0)),
        "return_paths_examined": sum(r.get("return_path_count", 0) for r in records),
        "sites_whose_field_comes_from_a_file": by_origin.get(O_FILE, 0),
        "sites_whose_field_comes_from_a_loaded_series": by_origin.get(O_SERIES, 0),
        "sites_whose_field_is_built_by_another_module_call": by_origin.get(O_BUILT_BY_A_CALL, 0),
    }


def _verdict(summary):
    total = summary["sites"]
    if total == 0:
        return V_EMPTY
    answered = summary["sites_answered_by_reading_their_callee_or_argument"]
    if answered == total:
        return V_RESOLVED
    if answered == 0:
        return V_REAL
    return V_PART


def _answers(summary):
    return {
        "how_many_sites": summary["sites"],
        "how_many_callees_are_repo_functions": summary["sites_whose_callee_is_a_repo_function"],
        "how_many_callees_are_builtins": summary["sites_whose_callee_is_a_builtin"],
        "how_many_distinct_callees": summary["distinct_callees"],
        "how_many_callees_branch_over_more_than_one_kind":
            summary["sites_whose_callee_branches_over_more_than_one_kind"],
        "how_many_empty_arms_are_filtered_by_a_guard":
            summary["sites_whose_empty_arm_is_filtered_by_a_guard"],
        "how_many_sites_still_read_whatever_arrives":
            summary["sites_that_read_whatever_arrives"],
        "how_many_sites_are_answered_by_the_callee":
            summary["sites_answered_by_reading_their_callee_or_argument"],
        "how_many_return_paths_were_examined": summary["return_paths_examined"],
    }


def build(root=None, write=True, up510=None, up511=None):
    root = root or ROOT
    records = analyse(root, up510=up510, up511=up511)
    summary = _summary(records)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("E511 left three sites whose value enters through a call. Follow that hop: "
                  "resolve the call to an in-repo function, enumerate its return statements, "
                  "publish the kind of value each path names, whether a terminating guard "
                  "filters the empty arm before the site, and where the field the site reads "
                  "ultimately comes from."),
        "evidence_cutoff": DATE_STAMP,
        "generated": e507._now(),
        "population_source": POPULATION_SOURCE,
        "arm_vocab": list(ARM_VOCAB),
        "callee_vocab": list(CALLEE_VOCAB),
        "return_kind_vocab": list(RETURN_VOCAB),
        "origin_vocab": list(ORIGIN_VOCAB),
        "site_verdict_vocab": list(SITE_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "method_limits": [
            "the population is two published faces (E510's pairs, E511's operand sites); no "
            "site enters because this study re-read E507's raw pairs",
            "the callee hop follows one call resolved through the site module's own imports; a "
            "callee reached through an attribute chain longer than one module hop is published "
            "as not-resolved, not guessed",
            "return paths are syntactic: a path that raises, or that returns from inside a "
            "branch the site can never reach, is still counted, so 'the callee branches' means "
            "'more than one kind of value is named', not 'more than one can arrive'",
            "the guard test is name-membership and termination only; a guard that narrows the "
            "value without terminating is published as a guard that does not filter",
            "field provenance follows names inside the callee and then module-level "
            "assignments, bounded at eight hops; a value built through a helper the callee "
            "calls is published as something_else, and a call into an imported module is "
            "published as built-by-another-module rather than followed further",
            "the field key is read syntactically off the binding's subscript, so a site that "
            "reads its dict through a helper is published with no field key rather than a "
            "guessed one",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "answers": _answers(summary),
        "sites": records,
    }
    if write:
        write_face(face, root)
    return face


def write_face(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in (FACE_NAME, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP)):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")


# ---------------------------------------------------------------------- gate
def site_problems(face):
    """Re-derive every reading from the site's own published evidence."""
    problems = []
    sites = face.get("sites") or []
    summary = face.get("summary") or {}
    if summary.get("sites") != len(sites):
        problems.append("sites is not the site list length")
    by_verdict = _count(sites, "verdict", SITE_VOCAB)
    if summary.get("sites_by_verdict") != by_verdict:
        problems.append("sites_by_verdict does not re-derive from the sites")
    by_callee = _count(sites, "callee_class", CALLEE_VOCAB)
    if summary.get("sites_by_callee_class") != by_callee:
        problems.append("sites_by_callee_class does not re-derive")
    by_origin = _count(sites, "field_origin", ORIGIN_VOCAB)
    if summary.get("sites_by_field_origin") != by_origin:
        problems.append("sites_by_field_origin does not re-derive")
    if summary.get("sites_by_arm") != _count(sites, "arm", ARM_VOCAB):
        problems.append("sites_by_arm does not re-derive")
    if summary.get("sites_whose_callee_is_a_repo_function") != sum(
            1 for r in sites if r.get("callee_class") in (CALLEE_SAME_MODULE, CALLEE_IMPORTED)):
        problems.append("the repo-function count is not the class count")
    if summary.get("sites_whose_callee_is_a_builtin") != by_callee.get(CALLEE_BUILTIN, 0):
        problems.append("the builtin count is not the class count")
    if summary.get("sites_that_read_whatever_arrives") != by_verdict.get(S_REAL, 0):
        problems.append("sites_that_read_whatever_arrives is not the real-ambiguity count")
    answered = (by_verdict.get(S_SAME, 0) + by_verdict.get(S_GUARDED, 0)
                + by_verdict.get(S_NOT_REPO, 0))
    if summary.get("sites_answered_by_reading_their_callee_or_argument") != answered:
        problems.append("the answered count is not the answered class count")
    if summary.get("return_paths_examined") != sum(r.get("return_path_count", 0)
                                                  for r in sites):
        problems.append("return_paths_examined is not the published path count")
    for rec in sites:
        name = "%s:%s" % (rec.get("source"), rec.get("line"))
        if rec.get("arm") not in ARM_VOCAB:
            problems.append("%s: arm outside the vocabulary" % name)
        if rec.get("callee_class") not in CALLEE_VOCAB:
            problems.append("%s: callee class outside the vocabulary" % name)
        if rec.get("verdict") not in SITE_VOCAB:
            problems.append("%s: verdict outside the vocabulary" % name)
        if rec.get("field_origin") not in ORIGIN_VOCAB:
            problems.append("%s: field origin outside the vocabulary" % name)
        paths = rec.get("return_paths") or []
        if rec.get("return_path_count") != len(paths):
            problems.append("%s: return_path_count is not the path list length" % name)
        for path in paths:
            if path.get("kind") not in RETURN_VOCAB:
                problems.append("%s: a return kind is outside the vocabulary" % name)
        kinds = {}
        for path in paths:
            kinds[path.get("kind")] = kinds.get(path.get("kind"), 0) + 1
        if rec.get("return_kinds") != kinds:
            problems.append("%s: return_kinds does not re-derive from the paths" % name)
        if bool(rec.get("returns_one_kind")) != (len(kinds) == 1):
            problems.append("%s: returns_one_kind contradicts its own path kinds" % name)
        expect = _expected_verdict(rec)
        if rec.get("verdict") != expect:
            problems.append("%s: verdict does not re-derive (%r vs %r)"
                            % (name, rec.get("verdict"), expect))
        if rec.get("empty_arm_filtered"):
            has_empty = any(k in NAMES_NOTHING for k in kinds)
            terminating = any(g.get("terminates_before_the_site")
                              for g in (rec.get("guards_between") or []))
            if not (has_empty and terminating and rec.get("guards_between")):
                problems.append("%s: claims a filtered empty arm without one" % name)
        if rec.get("callee_class") in (CALLEE_SAME_MODULE, CALLEE_IMPORTED) \
                and not rec.get("return_path_count"):
            problems.append("%s: a repo callee with no published return path" % name)
        if rec.get("verdict") == S_GUARDED and not rec.get("empty_arm_filtered"):
            problems.append("%s: guarded verdict without a filtering guard" % name)
    if face.get("verdict") != _verdict(summary):
        problems.append("verdict=%r does not re-derive from the summary (%r)"
                        % (face.get("verdict"), _verdict(summary)))
    answers = face.get("answers") or {}
    if answers.get("how_many_sites") != summary.get("sites"):
        problems.append("answers site count is not the summary site count")
    if answers.get("how_many_sites_are_answered_by_the_callee") != \
            summary.get("sites_answered_by_reading_their_callee_or_argument"):
        problems.append("answers answered count is not the summary count")
    return problems


def check(face=None, root=None):
    root = root or ROOT
    face = face or base._load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))
    problems = site_problems(face)
    print("check problems=%r" % (problems,))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    face = build(root, write=False)
    problems = site_problems(face)
    print("verify problems=%r" % (problems,))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
ALPHA = '''def stamp_of(frame):
    return str(frame.index[-1].date())


def run(frame):
    asof = stamp_of(frame)
    return asof
'''

BETA = '''def ticket(path):
    doc = _read_card(path)
    if not doc:
        return None
    return {"priced_bar": doc.get("as_of_bar")}


def run(path):
    tk = ticket(path)
    if not tk:
        return 2
    asof = tk["priced_bar"] or "unknown"
    return asof
'''

GAMMA = '''def ticket(path):
    doc = _read_card(path)
    if not doc:
        return None
    return {"priced_bar": doc.get("as_of_bar")}


def run(path):
    tk = ticket(path)
    asof = tk["priced_bar"] or "unknown"
    return asof
'''

DELTA = '''def run(frame):
    stamp = str(frame.index[-1].date())
    return stamp
'''

EPSILON = '''def run(label):
    stamp = label
    return stamp
'''


def _fixture_upstream():
    pairs = [{"source": "scripts/alpha.py", "line": 7, "date_expression": "asof",
              "bindings": {"symbol": "asof"}, "collapse": e510.K_MIXED},
             {"source": "scripts/beta.py", "line": 13, "date_expression": "asof",
              "bindings": {"symbol": "asof"}, "collapse": e510.K_MIXED},
             {"source": "scripts/gamma.py", "line": 11, "date_expression": "asof",
              "bindings": {"symbol": "asof"}, "collapse": e510.K_MIXED},
             {"source": "scripts/delta.py", "line": 3, "date_expression": "stamp",
              "bindings": {"symbol": "stamp"}, "collapse": e510.K_MIXED},
             # a pair whose binding is not a call must not enter this arm
             {"source": "scripts/epsilon.py", "line": 3, "date_expression": "stamp",
              "bindings": {"symbol": "stamp"}, "collapse": e510.K_MIXED}]
    sites = [{"source": "scripts/beta.py", "line": 13, "date_expression": "asof",
              "symbol": "asof", "resolution": e511.RESOLVE_OPERAND},
             {"source": "scripts/gamma.py", "line": 11, "date_expression": "asof",
              "symbol": "asof", "resolution": e511.RESOLVE_OPERAND},
             # an operand site E511 did not publish must not enter
             {"source": "scripts/alpha.py", "line": 7, "date_expression": "asof",
              "symbol": "asof", "resolution": e511.RESOLVE_DATAFLOW}]
    return pairs, {"sites": sites}


def selftest():
    checks, failures = 0, []

    def ok(name, cond, detail=None):
        nonlocal checks
        checks += 1
        if not cond:
            failures.append("%s (%r)" % (name, detail))

    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="e512_selftest_")
    try:
        os.makedirs(os.path.join(tmp, "scripts"))
        for name, body in (("alpha.py", ALPHA), ("beta.py", BETA), ("gamma.py", GAMMA),
                           ("delta.py", DELTA), ("epsilon.py", EPSILON)):
            with io.open(os.path.join(tmp, "scripts", name), "w", encoding="utf-8",
                         newline="\n") as fh:
                fh.write(body)
        pairs, face511 = _fixture_upstream()
        face = build(root=tmp, write=False, up510={"pairs": pairs}, up511=face511)
        by_source = {}
        for rec in face["sites"]:
            by_source.setdefault(rec["source"], []).append(rec)

        alpha = (by_source.get("scripts/alpha.py") or [{}])[0]
        ok("a callee with one return path names one kind, so the site is answered by it",
           alpha.get("verdict") == S_SAME, alpha.get("verdict"))
        ok("the callee is resolved in the same module",
           alpha.get("callee_class") == CALLEE_SAME_MODULE, alpha.get("callee_class"))
        ok("a site that reads no dict key off the call publishes no field",
           alpha.get("field_key") == "" and alpha.get("field_origin") == O_NONE,
           (alpha.get("field_key"), alpha.get("field_origin")))
        ok("every return path of the callee is published",
           alpha.get("return_path_count") == 1, alpha.get("return_paths"))

        beta = (by_source.get("scripts/beta.py") or [{}])[0]
        ok("a callee that returns None or a dict branches over two kinds",
           not beta.get("returns_one_kind") and beta.get("return_path_count") == 2,
           beta.get("return_kinds"))
        ok("a terminating guard between the call and the site filters the empty arm",
           beta.get("empty_arm_filtered") is True, beta.get("guards_between"))
        ok("the guarded site is answered by the callee, not left ambiguous",
           beta.get("verdict") == S_GUARDED, beta.get("verdict"))
        ok("the guard is published with its test and its line",
           bool(beta.get("guards_between")) and beta["guards_between"][0].get("test") == "not tk",
           beta.get("guards_between"))
        ok("the key the site reads is taken from the site's own binding",
           beta.get("field_key") == "priced_bar", beta.get("field_key"))
        ok("the field's origin is read through the callee's doc into a file read",
           beta.get("field_origin") == O_FILE, beta.get("field_origin"))

        gamma = (by_source.get("scripts/gamma.py") or [{}])[0]
        ok("without a guard the same callee leaves the ambiguity to the site",
           gamma.get("verdict") == S_REAL, gamma.get("verdict"))
        ok("a non-terminating path is not reported as filtered",
           gamma.get("empty_arm_filtered") is False, gamma.get("guards_between"))
        ok("the same field origin is read the same way at the unguarded site",
           gamma.get("field_origin") == O_FILE, gamma.get("field_origin"))

        delta = (by_source.get("scripts/delta.py") or [{}])[0]
        ok("a builtin coercion is not a repo function",
           delta.get("callee_class") == CALLEE_BUILTIN, delta.get("callee_class"))
        ok("a builtin coercion is answered by its argument",
           delta.get("verdict") == S_NOT_REPO, delta.get("verdict"))
        ok("the argument's own shape is published for a builtin",
           delta.get("field_origin") == O_PARAMETER, delta.get("field_origin"))

        ok("a pair whose binding is not a call does not enter the population",
           "scripts/epsilon.py" not in by_source, sorted(by_source))
        ok("an operand site whose resolution is not an operand read does not enter",
           len(by_source.get("scripts/beta.py") or []) == 1,
           len(by_source.get("scripts/beta.py") or []))
        ok("the fixture faces are two arms",
           face["summary"]["sites_by_arm"] == {ARM_CALL_BINDING: 2, ARM_OPERAND: 2},
           face["summary"]["sites_by_arm"])
        ok("the fixture verdict is mixed, not a blanket claim",
           face["verdict"] == V_PART, face["verdict"])
        ok("the gate passes on the built fixture", site_problems(face) == [],
           site_problems(face))

        doctored = json.loads(json.dumps(face))
        doctored["sites"][0]["verdict"] = S_REAL
        ok("the gate refuses a verdict its own path kinds contradict",
           site_problems(doctored) != [])
        doctored2 = json.loads(json.dumps(face))
        doctored2["summary"]["sites_answered_by_reading_their_callee_or_argument"] += 1
        ok("the gate refuses a hand-written answered count", site_problems(doctored2) != [])
        doctored3 = json.loads(json.dumps(face))
        doctored3["sites"][0]["return_kinds"] = {"guessed": 1}
        ok("the gate refuses a hand-written return-kind table", site_problems(doctored3) != [])
        doctored4 = json.loads(json.dumps(face))
        doctored4["sites"][0]["field_origin"] = "a_value_read_from_thin_air"
        ok("the gate refuses an origin outside the vocabulary", site_problems(doctored4) != [])
        doctored5 = json.loads(json.dumps(face))
        doctored5["verdict"] = V_RESOLVED
        ok("the gate refuses a hand-written verdict", site_problems(doctored5) != [])
        doctored6 = json.loads(json.dumps(face))
        doctored6["sites"][0]["empty_arm_filtered"] = True
        ok("the gate refuses a filtered arm with no filtering guard",
           site_problems(doctored6) != [])
        doctored7 = json.loads(json.dumps(face))
        doctored7["sites"][1]["return_paths"] = doctored7["sites"][1]["return_paths"][:1]
        ok("the gate refuses a path list shorter than the published count",
           site_problems(doctored7) != [])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("selftest %d/%d" % (checks - len(failures), checks))
    for failure in failures:
        print("FAIL: %s" % failure)
    return 0 if not failures else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    mode = argv[0] if argv else "run"
    if mode in ("run", "build"):
        face = build()
        print("verdict=%s" % face["verdict"])
        print("summary=%s" % json.dumps(face["summary"], ensure_ascii=False, sort_keys=True))
        return 0
    if mode == "check":
        return check()
    if mode == "verify":
        return verify()
    if mode == "selftest":
        return selftest()
    print("unknown mode %r" % mode)
    return 2


if __name__ == "__main__":
    sys.exit(main())