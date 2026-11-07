"""E520 -- where do the forwarded arguments of E519 really come from, one hop further?

E519 (r1545 bm-b) followed every call-site argument that was a local of the calling function
back to the statement that binds it, and stopped at the caller's own boundary: 7 of 61 bindings
turned out to be a *parameter of the caller itself* and 5 names were neither a parameter nor
bound anywhere inside the caller.  "A parameter of the caller" and "unbound" are both the same
non-answer one level up, in opposite directions:

  * a parameter of the caller is supplied by the call sites of that function -- enumerate them
    and publish what each one hands over (a literal, a module constant, an attribute on an
    imported name, a read, the result of another call, again a parameter, a local, a computed
    expression, nothing at all, or no call site in this tree);
  * a name bound nowhere in the caller is bound by some *other* scope -- an enclosing function
    (a closure cell), a comprehension target, a loop or ``with`` or ``except`` target, a walrus,
    a function-local import, a module global, or nowhere at all.

So the deliverable is a ranked answer to "does a caller really hand the surface a population",
with the two classes kept apart instead of folded into one count.

Population: the LOCALARGORIGIN face published by E519, every row whose origin is
a_parameter_of_the_calling_function_itself or no_binding_in_the_calling_function_or_its_parameters.
The row count is asserted against E519's own summary so the two faces cannot drift.

Run:  python scripts/e520_forwarded_argument.py [build|check|verify|selftest]
"""
import ast
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e513_constant_origin as e513  # noqa: E402
import e519_local_arg_origin as e519  # noqa: E402  (reuse the corpus, do not clone)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "forwardedarg_latest.json"
DATED_PREFIX = "FORWARDEDARG"
DATE_STAMP = "2026-11-08"
CARD = ("E520-WHERE-DO-THE-CALLER-PARAMETER-AND-THE-FIVE-UNBOUND-LOCAL-ARGUMENTS-REALLY-"
        "COME-FROM")
STUDY = "E520_forwarded_argument_origin"
UPSTREAM_FACE = os.path.join("results", "state_tilt", "LOCALARGORIGIN-2026-11-08.json")
POPULATION_SOURCE = (
    "results/state_tilt/LOCALARGORIGIN-2026-11-08.json rows whose origin is "
    "a_parameter_of_the_calling_function_itself or "
    "no_binding_in_the_calling_function_or_its_parameters, each followed one hop further: the "
    "call sites of the owning function for the first class, the binding scope for the second"
)
SELF_EXCLUDED = ("e520_", "run_e520", "_e520", "_r1552_leg520")

# ---------------------------------------------------------------- what a call site hands over
A_LITERAL = "a_literal_written_at_the_call_site"
A_MODULE_CONSTANT = "a_module_constant_of_the_calling_module"
A_OTHER_MODULE = "an_attribute_on_a_name_imported_at_the_call_site"
A_READ = "a_file_or_directory_read_at_the_call_site"
A_CALL = "the_result_of_another_call"
A_PARAMETER_AGAIN = "a_parameter_of_the_function_that_contains_the_call_site"
A_LOCAL_AGAIN = "a_local_of_the_function_that_contains_the_call_site"
A_COMPUTED = "an_expression_computed_at_the_call_site"
A_STARRED = "a_star_argument_the_scan_does_not_expand"
A_OMITTED_REQUIRED = (
    "nothing_is_passed_and_the_parameter_has_no_default_so_the_call_would_raise")
A_DEFAULT = "nothing_is_passed_so_the_signature_default_applies"
A_NO_CALL_SITE = "no_call_site_of_this_function_exists_in_this_tree"
ARGUMENT_VOCAB = (A_LITERAL, A_MODULE_CONSTANT, A_OTHER_MODULE, A_READ, A_CALL,
                  A_PARAMETER_AGAIN, A_LOCAL_AGAIN, A_COMPUTED, A_STARRED, A_DEFAULT,
                  A_OMITTED_REQUIRED)

# a value written at the call site by the caller itself: nothing has to be resolved further
SUPPLIED = (A_LITERAL, A_MODULE_CONSTANT, A_OTHER_MODULE)
# the value is not written here at all, it is forwarded again from the containing function
FORWARDED_AGAIN = (A_PARAMETER_AGAIN, A_LOCAL_AGAIN)

# ---------------------------------------------------------------- where an unbound name binds
B_OUTER_PARAM = "a_parameter_of_an_enclosing_function_so_a_closure_cell"
B_OUTER_LOCAL = "a_local_of_an_enclosing_function_so_a_closure_cell"
B_COMPREHENSION_TARGET = "a_comprehension_target"
B_UNPACK_TARGET = "an_element_of_a_tuple_or_list_destructuring_assignment"
B_LOOP_TARGET = "a_for_or_with_or_except_target"
B_WALRUS = "an_assignment_expression_target"
B_FUNCTION_IMPORT = "an_import_inside_the_function"
B_MODULE_GLOBAL = "a_module_scope_assignment"
B_MODULE_IMPORT = "an_import_at_module_scope"
B_GLOBAL_DECLARED = "declared_global_so_the_module_scope_owns_it"
B_NOT_BOUND = "not_bound_anywhere_in_this_tree"
BIND_VOCAB = (B_OUTER_PARAM, B_OUTER_LOCAL, B_COMPREHENSION_TARGET, B_UNPACK_TARGET,
              B_LOOP_TARGET, B_WALRUS, B_FUNCTION_IMPORT, B_MODULE_GLOBAL, B_MODULE_IMPORT,
              B_GLOBAL_DECLARED, B_NOT_BOUND)

# ---------------------------------------------------------------- call-site ownership
O_SAME_MODULE = "the_call_is_inside_the_module_that_defines_the_function"
O_IMPORTED_BY_NAME = "the_function_name_is_imported_from_that_module_at_the_call_site"
O_ON_AN_IMPORTED_MODULE = "the_call_is_an_attribute_on_a_name_imported_at_the_call_site"
O_NAME_ONLY = "a_same_named_call_in_a_module_that_neither_defines_nor_imports_it"
O_UNRESOLVED_RECEIVER = "the_receiver_of_the_attribute_call_is_not_a_name"
OWNERSHIP_VOCAB = (O_SAME_MODULE, O_IMPORTED_BY_NAME, O_ON_AN_IMPORTED_MODULE, O_NAME_ONLY,
                   O_UNRESOLVED_RECEIVER)

# ---------------------------------------------------------------- verdicts
V_CALLER_SUPPLIES = ("the_forwarded_parameters_are_supplied_by_their_call_sites_with_values_"
                     "the_caller_writes_so_the_population_really_arrives")
V_AGAIN_FORWARDED = ("most_forwarded_parameters_are_again_a_parameter_or_a_local_at_the_next_"
                     "call_site_so_the_hop_did_not_reach_a_source")
V_CLOSURE = ("every_unbound_name_is_bound_by_an_enclosing_or_module_scope_so_it_is_a_closure_"
             "not_a_missing_binding")
V_NEVER_CALLED = ("the_forwarded_parameters_belong_to_functions_this_tree_never_calls_so_no_"
                  "caller_supplies_anything")
V_UNARRIVED = ("the_call_sites_supply_no_literal_and_no_module_constant_so_the_population_"
               "never_arrives_as_a_written_value")
V_NONE = "this_tree_has_no_forwarded_local_argument_to_trace"
VERDICT_VOCAB = (V_CALLER_SUPPLIES, V_AGAIN_FORWARDED, V_CLOSURE, V_NEVER_CALLED, V_UNARRIVED,
                 V_NONE)

ENCLOSING_BINDS = (B_OUTER_PARAM, B_OUTER_LOCAL, B_COMPREHENSION_TARGET, B_UNPACK_TARGET,
                   B_LOOP_TARGET, B_WALRUS, B_FUNCTION_IMPORT, B_MODULE_GLOBAL, B_MODULE_IMPORT,
                   B_GLOBAL_DECLARED)


def _is_self(rel):
    name = os.path.basename(rel or "")
    return name.startswith(SELF_EXCLUDED)


def _short(node):
    try:
        text = ast.unparse(node)
    except Exception:  # pragma: no cover - py<3.9
        return type(node).__name__
    return text if len(text) <= 120 else text[:117] + "..."


class ForwardCorpus(e519.ArgCorpus):
    """E519's corpus (params / bindings / enclosing) plus one name -> call-site index."""

    def __init__(self, root):
        e519.ArgCorpus.__init__(self, root)
        self.call_index = {}
        for module, tree in self.trees.items():
            if tree is None:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                name = None
                if isinstance(node.func, ast.Name):
                    name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    name = node.func.attr
                if name:
                    self.call_index.setdefault(name, []).append((module, node))

    def signature(self, module, funcname):
        return (self.funcs.get(module) or {}).get(funcname)

    def param_names(self, module, funcname):
        return self.params_of(module, funcname)


def _param_index(funcdef, parameter):
    """Positional index of ``parameter`` in a signature (posonly included), else None."""
    if funcdef is None:
        return None
    names = [a.arg for a in getattr(funcdef.args, "posonlyargs", []) or []]
    names += [a.arg for a in funcdef.args.args]
    if parameter in names:
        return names.index(parameter)
    return None


def _keyword_only(funcdef, parameter):
    if funcdef is None:
        return False
    return parameter in [a.arg for a in (funcdef.args.kwonlyargs or [])]


def _has_default(funcdef, parameter):
    """True when ``parameter`` carries a default (so omitting it is legal)."""
    if funcdef is None:
        return False
    args = funcdef.args
    positional = [a.arg for a in getattr(args, "posonlyargs", []) or []] + \
        [a.arg for a in args.args]
    defaults = args.defaults or []
    if defaults and parameter in positional[-len(defaults):]:
        return True
    kwonly = [a.arg for a in (args.kwonlyargs or [])]
    kw_defaults = args.kw_defaults or []
    for index, name in enumerate(kwonly):
        if name == parameter:
            return index < len(kw_defaults) and kw_defaults[index] is not None
    if args.vararg is not None and args.vararg.arg == parameter:
        return True
    if args.kwarg is not None and args.kwarg.arg == parameter:
        return True
    return parameter in positional and bool(defaults) and \
        positional.index(parameter) >= len(positional) - len(defaults)


def _argument_for(call, parameter, funcdef):
    """(node or None, arm) for the argument that lands in ``parameter``."""
    for kw in call.keywords:
        if kw.arg == parameter:
            return kw.value, None
    index = _param_index(funcdef, parameter)
    if index is not None and index < len(call.args):
        node = call.args[index]
        if isinstance(node, ast.Starred):
            return None, A_STARRED
        return node, None
    if isinstance(call.args, list) and any(isinstance(a, ast.Starred) for a in call.args):
        return None, A_STARRED
    if any(kw.arg is None for kw in call.keywords):
        return None, A_STARRED
    if _has_default(funcdef, parameter):
        return None, A_DEFAULT
    return None, A_OMITTED_REQUIRED


def _classify_argument(node, caller_module, corpus):
    """What a call site hands over for one parameter."""
    if isinstance(node, (ast.List, ast.Tuple, ast.Set, ast.Dict)):
        return A_LITERAL
    if isinstance(node, ast.Constant):
        return A_LITERAL
    if isinstance(node, ast.Name):
        if node.id in (corpus.imports.get(caller_module) or {}):
            return A_OTHER_MODULE
        if corpus.lookup(caller_module, node.id) is not None:
            return A_MODULE_CONSTANT
        holder = corpus.enclosing(caller_module, getattr(node, "lineno", 0) or 0)
        if holder is not None:
            if node.id in corpus.param_names(caller_module, holder["func"]):
                return A_PARAMETER_AGAIN
            return A_LOCAL_AGAIN
        return A_COMPUTED
    if isinstance(node, ast.Attribute):
        return A_OTHER_MODULE
    if isinstance(node, ast.Call):
        func = node.func
        name = None
        if isinstance(func, ast.Name):
            name = func.id
        elif isinstance(func, ast.Attribute):
            name = func.attr
        if name in e513.READERS or name in e513.WALKERS:
            return A_READ
        return A_CALL
    return A_COMPUTED


def _ownership(caller_module, call, module, funcname, corpus):
    """How the call site names the function: same module, import, or merely the same name."""
    func = call.func
    if isinstance(func, ast.Name):
        if caller_module == module:
            return O_SAME_MODULE
        if (corpus.imports.get(caller_module) or {}).get(func.id) == module:
            return O_IMPORTED_BY_NAME
        return O_NAME_ONLY
    owner = func.value.id if isinstance(func.value, ast.Name) else None
    if owner is None:
        return O_UNRESOLVED_RECEIVER
    target = (corpus.imports.get(caller_module) or {}).get(owner)
    if target is None:
        return O_NAME_ONLY
    stem = os.path.splitext(os.path.basename(target.replace(".", "/")))[0]
    if stem == module:
        return O_ON_AN_IMPORTED_MODULE
    return O_NAME_ONLY


def _binds_target(target, name):
    """True when ``target`` binds ``name``, including inside a tuple/list destructuring."""
    if isinstance(target, ast.Name):
        return target.id == name
    if isinstance(target, (ast.Tuple, ast.List)):
        return any(_binds_target(elt, name) for elt in target.elts)
    if isinstance(target, ast.Starred):
        return _binds_target(target.value, name)
    return False


def _is_unpacking(target, name):
    """A destructuring target that names ``name`` (a plain Name is not a destructuring)."""
    return isinstance(target, (ast.Tuple, ast.List, ast.Starred)) and _binds_target(target, name)


def _bind_scope(module, funcname, name, line, corpus):
    """Where a name that is neither a parameter nor an assignment of the caller is bound."""
    holder = corpus.enclosing(module, line or 0)
    # an enclosing function: walk outwards by body containment
    chain = []
    for rec in corpus.functions.get(module) or []:
        if rec["func"] == funcname:
            continue
        if rec["start"] <= (line or 0) <= rec["end"]:
            chain.append(rec)
    chain.sort(key=lambda r: (r["end"] - r["start"]))
    for rec in chain:
        if name in corpus.param_names(module, rec["func"]):
            return B_OUTER_PARAM, {"scope": rec["func"], "start": rec["start"]}
        if name in (rec.get("values") or {}):
            return B_OUTER_LOCAL, {"scope": rec["func"], "start": rec["start"]}
    # bindings inside the caller itself that E519's assignment scan does not record
    funcdef = corpus.signature(module, funcname)
    if funcdef is not None:
        for node in ast.walk(funcdef):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node is not funcdef:
                continue
            if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
                for gen in node.generators:
                    if isinstance(gen.target, ast.Name) and gen.target.id == name:
                        return B_COMPREHENSION_TARGET, {"line": node.lineno}
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if _is_unpacking(target, name):
                        return B_UNPACK_TARGET, {"line": node.lineno, "kind": "assign"}
            if isinstance(node, (ast.For, ast.AsyncFor)):
                if isinstance(node.target, ast.Name) and node.target.id == name:
                    return B_LOOP_TARGET, {"line": node.lineno, "kind": "for"}
                if _is_unpacking(node.target, name):
                    return B_UNPACK_TARGET, {"line": node.lineno, "kind": "for"}
            if isinstance(node, ast.withitem):
                tgt = node.optional_vars
                if isinstance(tgt, ast.Name) and tgt.id == name:
                    return B_LOOP_TARGET, {"line": getattr(node, "lineno", None), "kind": "with"}
                if _is_unpacking(tgt, name):
                    return B_UNPACK_TARGET, {"line": getattr(node, "lineno", None),
                                             "kind": "with"}
            if isinstance(node, ast.ExceptHandler) and getattr(node, "name", None) == name:
                return B_LOOP_TARGET, {"line": node.lineno, "kind": "except"}
            if isinstance(node, ast.NamedExpr) and isinstance(node.target, ast.Name) and \
                    node.target.id == name:
                return B_WALRUS, {"line": node.lineno}
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    if (alias.asname or alias.name) == name:
                        return B_FUNCTION_IMPORT, {"line": node.lineno}
            if isinstance(node, (ast.Global, ast.Nonlocal)) and name in node.names:
                return B_GLOBAL_DECLARED, {"line": node.lineno,
                                           "keyword": type(node).__name__}
    if name in (corpus.imports.get(module) or {}):
        return B_MODULE_IMPORT, {"module": corpus.imports[module][name]}
    if corpus.lookup(module, name) is not None:
        return B_MODULE_GLOBAL, {"line": None}
    return B_NOT_BOUND, {}


def population(root=None, upstream=None):
    """E519 rows whose origin is a forwarded parameter or an unbound name, in row order."""
    root = root or ROOT
    face = upstream if upstream is not None else e513.base._load_json(
        os.path.join(root, UPSTREAM_FACE))
    targets = []
    for row in face.get("rows") or []:
        origin = row.get("origin")
        if origin not in (e519.LO_CALLER_PARAMETER, e519.LO_UNRESOLVED):
            continue
        sites = row.get("call_sites") or []
        line = min([s.get("line") or 0 for s in sites] or [0]) or None
        targets.append({
            "module": row.get("module"),
            "site_module": row.get("site_module") or row.get("module"),
            "source": row.get("source"),
            "function": row.get("enclosing_function"),
            "local": row.get("local"),
            "upstream_origin": origin,
            "surfaces": row.get("surfaces") or [],
            "parameters": row.get("parameters") or [],
            "upstream_sites": len(sites),
            "line": line,
        })
    return sorted(targets, key=lambda r: (r["source"] or "", r["line"] or 0,
                                          r["local"] or ""))


def _trace_parameter(target, corpus):
    """Every call site of the owning function, and what it hands to ``local``."""
    module = target["site_module"]
    funcname = target["function"]
    funcdef = corpus.signature(module, funcname)
    if funcdef is None:
        return {"call_sites": [], "call_site_count": 0,
                "note": "the owning function definition is not in this corpus"}
    found = []
    for caller_module, call in corpus.call_index.get(funcname) or []:
        ownership = _ownership(caller_module, call, module, funcname, corpus)
        if ownership == O_NAME_ONLY:
            continue
        node, arm = _argument_for(call, target["local"], funcdef)
        kind = arm or _classify_argument(node, caller_module, corpus)
        found.append({
            "caller_module": caller_module,
            "line": call.lineno,
            "ownership": ownership,
            "argument": _short(node) if node is not None else None,
            "argument_kind": kind,
        })
    found.sort(key=lambda r: (r["caller_module"] or "", r["line"] or 0))
    if not found:
        found = [{"caller_module": None, "line": None, "ownership": None,
                  "argument": None, "argument_kind": A_NO_CALL_SITE}]
    return {"call_sites": found, "call_site_count": len(found), "note": None}


def analyse(root=None, upstream=None):
    root = root or ROOT
    corpus = ForwardCorpus(root)
    targets = population(root, upstream)

    rows = []
    for target in targets:
        rec = dict(target)
        rec["sites"] = target["upstream_sites"]
        if target["upstream_origin"] == e519.LO_CALLER_PARAMETER:
            traced = _trace_parameter(target, corpus)
            rec["parameter_has_a_default"] = _has_default(
                corpus.signature(target["site_module"], target["function"]), target["local"])
            rec["question"] = "who_supplies_this_parameter"
            rec["call_sites"] = traced["call_sites"]
            rec["call_site_count"] = traced["call_site_count"]
            rec["note"] = traced["note"]
            kinds = [s["argument_kind"] for s in rec["call_sites"]]
            counts = {}
            for kind in kinds:
                counts[kind] = counts.get(kind, 0) + 1
            rec["argument_kind_counts"] = counts
            rec["dominant_argument_kind"] = max(sorted(counts), key=lambda k: counts[k]) \
                if counts else None
            unique = set(kinds)
            if unique == {A_NO_CALL_SITE}:
                rec["arrival"] = "never_supplied"
            elif unique <= set(SUPPLIED):
                rec["arrival"] = "written_at_every_call_site"
            elif unique <= set(FORWARDED_AGAIN):
                rec["arrival"] = "forwarded_again_at_every_call_site"
            else:
                rec["arrival"] = "mixed"
            rec["binding"] = None
        else:
            rec["question"] = "where_is_this_name_bound"
            bind, detail = _bind_scope(target["site_module"], target["function"],
                                      target["local"], target["line"], corpus)
            rec["binding"] = bind
            rec["binding_detail"] = detail
            rec["call_sites"] = []
            rec["call_site_count"] = 0
            rec["argument_kind_counts"] = {}
            rec["dominant_argument_kind"] = None
            rec["arrival"] = ("bound_by_another_scope" if bind in ENCLOSING_BINDS
                              else "not_bound")
        rows.append(rec)
    return {"rows": rows, "corpus": corpus, "modules_scanned": len(corpus.by_module),
            "unreadable": corpus.unreadable}


def _count(rows, key, vocab):
    out = dict((v, 0) for v in vocab)
    for rec in rows:
        value = rec.get(key)
        if value in out:
            out[value] += 1
        else:
            out[value] = out.get(value, 0) + 1
    return out


def _summary(rows, modules_scanned, upstream_summary=None):
    param_rows = [r for r in rows if r["question"] == "who_supplies_this_parameter"]
    unbound_rows = [r for r in rows if r["question"] == "where_is_this_name_bound"]
    arg_counts = dict((v, 0) for v in ARGUMENT_VOCAB)
    ownership = dict((v, 0) for v in OWNERSHIP_VOCAB)
    arrivals = {}
    for rec in param_rows:
        for kind in (rec.get("argument_kind_counts") or {}):
            arg_counts[kind] = arg_counts.get(kind, 0) + rec["argument_kind_counts"][kind]
        for site in rec.get("call_sites") or []:
            if site.get("ownership"):
                ownership[site["ownership"]] = ownership.get(site["ownership"], 0) + 1
        arrivals[rec["arrival"]] = arrivals.get(rec["arrival"], 0) + 1
    binds = _count(unbound_rows, "binding", BIND_VOCAB)
    call_sites = sum(rec.get("call_site_count") or 0 for rec in param_rows)
    return {
        "modules_scanned": modules_scanned,
        "forwarded_bindings": len(rows),
        "parameter_bindings": len(param_rows),
        "unbound_name_bindings": len(unbound_rows),
        "call_sites_of_the_owning_functions": call_sites,
        "call_sites_that_are_not_a_call_site_at_all": arg_counts.get(A_NO_CALL_SITE, 0),
        "argument_kind_counts": arg_counts,
        "ownership_counts": ownership,
        "arguments_written_at_the_call_site": sum(arg_counts[a] for a in SUPPLIED),
        "arguments_forwarded_again": sum(arg_counts[a] for a in FORWARDED_AGAIN),
        "arguments_from_a_call_or_a_read": arg_counts[A_CALL] + arg_counts[A_READ],
        "arguments_left_at_the_default": arg_counts[A_DEFAULT],
        "arguments_omitted_for_a_parameter_with_no_default": arg_counts[A_OMITTED_REQUIRED],
        "parameter_bindings_whose_parameter_has_no_default": sum(
            1 for rec in param_rows if not rec.get("parameter_has_a_default")),
        "arguments_passed_through_a_star_argument": arg_counts[A_STARRED],
        "arrival_counts": arrivals,
        "bind_counts": binds,
        "unbound_names_bound_by_another_scope": sum(binds[b] for b in ENCLOSING_BINDS),
        "unbound_names_actually_unbound": binds[B_NOT_BOUND],
        "distinct_supplying_caller_modules": sorted({
            site["caller_module"] for rec in param_rows for site in rec.get("call_sites") or []
            if site.get("caller_module") and site.get("argument_kind") in SUPPLIED}),
        "upstream_forwarded_rows": (upstream_summary or {}).get(
            "arguments_that_are_a_parameter_of_the_caller"),
        "upstream_unbound_rows": (upstream_summary or {}).get(
            "arguments_with_no_binding_in_the_calling_function"),
    }


def _verdict(summary):
    if not summary["forwarded_bindings"]:
        return V_NONE
    supplied = summary["arguments_written_at_the_call_site"]
    again = summary["arguments_forwarded_again"]
    unbound = summary["unbound_name_bindings"]
    if summary["parameter_bindings"] and summary["parameter_bindings"] == \
            summary["arrival_counts"].get("never_supplied", 0):
        return V_NEVER_CALLED
    if again > supplied:
        return V_AGAIN_FORWARDED
    if supplied > 0:
        return V_CALLER_SUPPLIES
    if unbound and summary["unbound_names_bound_by_another_scope"] == unbound:
        return V_CLOSURE
    return V_UNARRIVED


def _answers(summary):
    kinds = summary["argument_kind_counts"]
    return [
        ["How many forwarded bindings does E519 hand on, and of what kind?",
         "%d rows: %d whose local is a parameter of the owning function and %d whose name is "
         "not bound inside it." % (summary["forwarded_bindings"], summary["parameter_bindings"],
                                   summary["unbound_name_bindings"])],
        ["Who supplies the parameters, and with what?",
         "%d call sites of the owning functions hand over %d written values (%d literals, %d "
         "module constants of the caller, %d attributes on imported names), %d values that are "
         "again a parameter or a local one level up, %d results of another call, %d reads, %d "
         "computed expressions, %d defaults, %d omissions of a parameter that has no default, "
         "%d star arguments and %d rows with no call site at all."
         % (summary["call_sites_of_the_owning_functions"],
                   summary["arguments_written_at_the_call_site"], kinds[A_LITERAL],
                   kinds[A_MODULE_CONSTANT], kinds[A_OTHER_MODULE],
                   summary["arguments_forwarded_again"], kinds[A_CALL], kinds[A_READ],
                   kinds[A_COMPUTED], kinds[A_DEFAULT], kinds[A_OMITTED_REQUIRED],
                   kinds[A_STARRED],
                   summary["call_sites_that_are_not_a_call_site_at_all"])],
        ["Does the population really arrive, binding by binding?",
         "%d of %d parameter bindings are written at every call site, %d are forwarded again at "
         "every call site, %d are mixed and %d are never supplied at all."
         % (summary["arrival_counts"].get("written_at_every_call_site", 0),
            summary["parameter_bindings"],
            summary["arrival_counts"].get("forwarded_again_at_every_call_site", 0),
            summary["arrival_counts"].get("mixed", 0),
            summary["arrival_counts"].get("never_supplied", 0))],
        ["Where were the names that the caller does not bind actually bound?",
         "%d of %d are bound by another scope (%d by an enclosing function, %d by a "
         "comprehension or loop target, %d by a destructuring assignment, %d by a module-scope "
         "assignment or import) and %d are bound nowhere in this tree."
         % (summary["unbound_names_bound_by_another_scope"], summary["unbound_name_bindings"],
            summary["bind_counts"][B_OUTER_PARAM] + summary["bind_counts"][B_OUTER_LOCAL],
            summary["bind_counts"][B_COMPREHENSION_TARGET] + summary["bind_counts"][B_LOOP_TARGET],
            summary["bind_counts"][B_UNPACK_TARGET],
            summary["bind_counts"][B_MODULE_GLOBAL] + summary["bind_counts"][B_MODULE_IMPORT] +
            summary["bind_counts"][B_GLOBAL_DECLARED],
            summary["unbound_names_actually_unbound"])],
        ["How were the call sites named?",
         "%d are inside the defining module, %d name the function through a from-import, %d are "
         "an attribute on an imported module, %d are a same-named call elsewhere and %d have a "
         "receiver that is not a name."
         % (summary["ownership_counts"][O_SAME_MODULE],
            summary["ownership_counts"][O_IMPORTED_BY_NAME],
            summary["ownership_counts"][O_ON_AN_IMPORTED_MODULE],
            summary["ownership_counts"][O_NAME_ONLY],
            summary["ownership_counts"][O_UNRESOLVED_RECEIVER])],
        ["Which modules supply the population?",
         "%d distinct: %s." % (len(summary["distinct_supplying_caller_modules"]),
                               ", ".join(summary["distinct_supplying_caller_modules"][:12])
                               or "none")],
    ]


def build(root=None, write=True, upstream=None):
    root = root or ROOT
    upstream_face = upstream if upstream is not None else e513.base._load_json(
        os.path.join(root, UPSTREAM_FACE))
    found = analyse(root, upstream_face)
    summary = _summary(found["rows"], found["modules_scanned"],
                       upstream_face.get("summary") or {})
    face = {
        "card": CARD,
        "study": STUDY,
        "title": "Where a forwarded call-site argument really comes from, one hop past the caller",
        "kind": "static_read_of_the_repo_plus_its_own_published_upstream_faces",
        "evidence_cutoff": DATE_STAMP,
        "generated": e513.base._now(),
        "population_source": POPULATION_SOURCE,
        "argument_vocab": list(ARGUMENT_VOCAB),
        "bind_vocab": list(BIND_VOCAB),
        "ownership_vocab": list(OWNERSHIP_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": summary,
        "answers": _answers(summary),
        "verdict": _verdict(summary),
        "rows": found["rows"],
        "unreadable": found["unreadable"],
        "method_limits": [
            ("a parameter is followed one more hop only: the value a supplying caller writes is "
             "not itself traced (a module constant there is published as a constant, not as what "
             "the constant holds)"),
            ("call sites are matched by the callee's bare name and then filtered by ownership "
             "(same module, from-import of that name, or an attribute on a name imported from "
             "that module); a call through an alias of the module, or through a variable holding "
             "the function, is not in the population and the %s arm is printed raw so it is "
             "visible rather than silently dropped" % A_NO_CALL_SITE),
            ("an argument passed through *args/**kwargs is published as a star argument instead "
             "of being guessed"),
            ("a keyword-only parameter that the call site omits is published as the default "
             "arm, which is what the interpreter does"),
            ("the unbound-name arm is a scope search of one module: an enclosing function body, "
             "a comprehension/loop/with/except target, a walrus, a function-local import, a "
             "module-scope name or import; a name supplied by a star-import or by monkeypatching "
             "would be published as not bound"),
        ],
    }
    if write:
        write_face(face, root)
    return face


def write_face(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in ("%s-%s.json" % (DATED_PREFIX, DATE_STAMP), FACE_NAME):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
    return face


def load_face(root=None):
    root = root or ROOT
    return e513.base._load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))


def check(face=None, root=None):
    """Re-derive every published number from the face's own rows."""
    root = root or ROOT
    face = face or load_face(root)
    problems = []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    if len(rows) != summary.get("forwarded_bindings"):
        problems.append("row count %d != summary bindings %r"
                        % (len(rows), summary.get("forwarded_bindings")))
    param = [r for r in rows if r.get("question") == "who_supplies_this_parameter"]
    unbound = [r for r in rows if r.get("question") == "where_is_this_name_bound"]
    if len(param) != summary.get("parameter_bindings"):
        problems.append("parameter row count does not re-derive")
    if len(unbound) != summary.get("unbound_name_bindings"):
        problems.append("unbound row count does not re-derive")
    if len(param) + len(unbound) != len(rows):
        problems.append("a row is neither a parameter nor an unbound name")
    arg_counts = dict((v, 0) for v in ARGUMENT_VOCAB)
    for rec in param:
        for kind, n in (rec.get("argument_kind_counts") or {}).items():
            arg_counts[kind] = arg_counts.get(kind, 0) + n
        if sum((rec.get("argument_kind_counts") or {}).values()) != rec.get("call_site_count"):
            problems.append("%s.%s kind counts disagree with its call site count"
                            % (rec.get("source"), rec.get("local")))
        kinds = [s.get("argument_kind") for s in rec.get("call_sites") or []]
        if kinds.count(A_NO_CALL_SITE) and len(kinds) > 1:
            problems.append("%s.%s mixes the no-call-site arm with real call sites"
                            % (rec.get("source"), rec.get("local")))
    if arg_counts != summary.get("argument_kind_counts"):
        problems.append("argument kind counts do not re-derive")
    if sum(arg_counts[a] for a in SUPPLIED) != summary.get("arguments_written_at_the_call_site"):
        problems.append("supplied count does not re-derive")
    if sum(arg_counts[a] for a in FORWARDED_AGAIN) != summary.get("arguments_forwarded_again"):
        problems.append("forwarded-again count does not re-derive")
    if sum(rec.get("call_site_count") or 0 for rec in param) != summary.get(
            "call_sites_of_the_owning_functions"):
        problems.append("call site total does not re-derive")
    binds = _count(unbound, "binding", BIND_VOCAB)
    if binds != summary.get("bind_counts"):
        problems.append("bind counts do not re-derive")
    if sum(binds[b] for b in ENCLOSING_BINDS) != summary.get(
            "unbound_names_bound_by_another_scope"):
        problems.append("bound-elsewhere count does not re-derive")
    if _verdict(summary) != face.get("verdict"):
        problems.append("verdict does not follow from the summary")
    if _answers(summary) != face.get("answers"):
        problems.append("answers do not re-derive")
    return problems


def site_problems(face=None, root=None):
    """What a consumer needs: provenance intact and every row re-derivable from its own sites."""
    root = root or ROOT
    face = face or load_face(root)
    problems = list(check(face, root))
    if face.get("population_source") != POPULATION_SOURCE:
        problems.append("population_source is not the one this study used")
    if face.get("study") != STUDY or face.get("card") != CARD:
        problems.append("the study or card identity was edited")
    if face.get("evidence_cutoff") != DATE_STAMP:
        problems.append("evidence_cutoff does not match the dated file name")
    for rec in face.get("rows") or []:
        source = rec.get("source") or ""
        if not source or not os.path.exists(os.path.join(root, source)):
            problems.append("%s names a source that is not on disk" % (source or "<empty>"))
        if rec.get("question") == "who_supplies_this_parameter":
            if rec.get("binding") is not None:
                problems.append("%s.%s carries a binding on a parameter row"
                                % (rec.get("source"), rec.get("local")))
            for site in rec.get("call_sites") or []:
                if site.get("argument_kind") not in ARGUMENT_VOCAB + (A_NO_CALL_SITE,):
                    problems.append("%s.%s argument kind outside the vocabulary"
                                    % (rec.get("source"), rec.get("local")))
                if site.get("ownership") is not None and \
                        site.get("ownership") not in OWNERSHIP_VOCAB:
                    problems.append("%s.%s ownership outside the vocabulary"
                                    % (rec.get("source"), rec.get("local")))
        else:
            if rec.get("binding") not in BIND_VOCAB:
                problems.append("%s.%s binding outside the vocabulary"
                                % (rec.get("source"), rec.get("local")))
            if (rec.get("binding") in ENCLOSING_BINDS) != (
                    rec.get("arrival") == "bound_by_another_scope"):
                problems.append("%s.%s arrival contradicts its binding"
                                % (rec.get("source"), rec.get("local")))
    return problems


def face_problems(face=None, root=None):
    """What a consumer needs from the published face alone (the guards in site_problems)."""
    return site_problems(face, root)


def verify(root=None, upstream=None):
    """Rebuild from the tree and compare with the published file."""
    root = root or ROOT
    problems = []
    face = load_face(root)
    upstream_face = upstream if upstream is not None else e513.base._load_json(
        os.path.join(root, UPSTREAM_FACE))
    rebuilt = build(root, write=False, upstream=upstream_face)
    for key in ("summary", "answers", "verdict", "argument_vocab", "bind_vocab",
                "ownership_vocab", "verdict_vocab"):
        if face.get(key) != rebuilt.get(key):
            problems.append("%s differs from a fresh build" % key)
    if (face.get("rows") or []) != (rebuilt.get("rows") or []):
        problems.append("rows differ from a fresh build (%d published vs %d rebuilt)"
                        % (len(face.get("rows") or []), len(rebuilt.get("rows") or [])))
    if (face.get("unreadable") or []) != (rebuilt.get("unreadable") or []):
        problems.append("the unreadable list differs from a fresh build")
    return problems


# ---------------------------------------------------------------- selftest fixtures
FIX_DEFINING = """\
GLOBAL_NAMES = ("a",)


def surface(groups=None):
    return groups


def pass_through(groups):
    return surface(groups)


def via_attribute(groups):
    return surface(groups)


def closure_holder(names):
    def inner():
        return surface(names)
    return inner


def comprehension():
    return [surface(n) for n in (1, 2)]


def looped(items):
    for item in items:
        return surface(item)


def broken():
    return surface(mystery)


def destructured():
    charge, members = (1, ("a",))
    return surface(members)


def same_module_caller(groups):
    return pass_through(groups)
"""

FIX_CALLER = """\
import defining
from defining import pass_through


NAMES = ("b",)


def supplies_literal():
    return defining.via_attribute(("c", "d"))


def supplies_constant():
    return pass_through(NAMES)


def supplies_again(param):
    return pass_through(param)


def never_reaches():
    return defining.via_attribute(dict())


def omits_a_required_parameter():
    return defining.via_attribute()
"""


def _fixture(root):
    scripts = os.path.join(root, "scripts")
    os.makedirs(scripts)
    for name, text in (("defining", FIX_DEFINING), ("caller", FIX_CALLER)):
        with io.open(os.path.join(scripts, name + ".py"), "w", encoding="utf-8",
                     newline="\n") as fh:
            fh.write(text)
    return scripts


def _fixture_population():
    """E519-shaped rows: two parameters of the owning function and five unbound names."""
    rows = [
        {"module": "defining", "site_module": "defining", "source": "scripts/defining.py",
         "surface": "surface", "parameters": ["groups"], "enclosing_function": "pass_through",
         "local": "groups", "origin": e519.LO_CALLER_PARAMETER,
         "call_sites": [{"surface": "surface", "site_module": "defining", "line": 10,
                         "argument": "groups"}]},
        {"module": "defining", "site_module": "defining", "source": "scripts/defining.py",
         "surface": "surface", "parameters": ["groups"], "enclosing_function": "via_attribute",
         "local": "groups", "origin": e519.LO_CALLER_PARAMETER,
         "call_sites": [{"surface": "surface", "site_module": "defining", "line": 14,
                         "argument": "groups"}]},
        {"module": "defining", "site_module": "defining", "source": "scripts/defining.py",
         "surface": "surface", "parameters": ["groups"], "enclosing_function": "inner",
         "local": "names", "origin": e519.LO_UNRESOLVED,
         "call_sites": [{"surface": "surface", "site_module": "defining", "line": 19,
                         "argument": "names"}]},
        {"module": "defining", "site_module": "defining", "source": "scripts/defining.py",
         "surface": "surface", "parameters": ["groups"], "enclosing_function": "comprehension",
         "local": "n", "origin": e519.LO_UNRESOLVED,
         "call_sites": [{"surface": "surface", "site_module": "defining", "line": 24,
                         "argument": "n"}]},
        {"module": "defining", "site_module": "defining", "source": "scripts/defining.py",
         "surface": "surface", "parameters": ["groups"], "enclosing_function": "looped",
         "local": "item", "origin": e519.LO_UNRESOLVED,
         "call_sites": [{"surface": "surface", "site_module": "defining", "line": 29,
                         "argument": "item"}]},
        {"module": "defining", "site_module": "defining", "source": "scripts/defining.py",
         "surface": "surface", "parameters": ["groups"], "enclosing_function": "broken",
         "local": "mystery", "origin": e519.LO_UNRESOLVED,
         "call_sites": [{"surface": "surface", "site_module": "defining", "line": 34,
                         "argument": "mystery"}]},
        {"module": "defining", "site_module": "defining", "source": "scripts/defining.py",
         "surface": "surface", "parameters": ["groups"], "enclosing_function": "destructured",
         "local": "members", "origin": e519.LO_UNRESOLVED,
         "call_sites": [{"surface": "surface", "site_module": "defining", "line": 39,
                         "argument": "members"}]},
    ]
    return {"rows": rows, "summary": {"arguments_that_are_a_parameter_of_the_caller": 2,
                                      "arguments_with_no_binding_in_the_calling_function": 4}}


def selftest():
    import shutil
    import tempfile

    problems = []
    root = tempfile.mkdtemp(prefix="e520_")
    try:
        _fixture(root)
        upstream = _fixture_population()
        found = analyse(root, upstream)
        rows = dict(((r["function"], r["local"]), r) for r in found["rows"])
        if len(found["rows"]) != 7:
            problems.append("fixture population %d != 7" % len(found["rows"]))

        # a parameter of the caller: the next hop is the call sites of that function
        pt = rows.get(("pass_through", "groups")) or {}
        kinds = sorted(s["argument_kind"] for s in pt.get("call_sites") or [])
        if kinds != sorted([A_MODULE_CONSTANT, A_PARAMETER_AGAIN, A_PARAMETER_AGAIN]):
            problems.append("pass_through call-site kinds %r" % (kinds,))
        if pt.get("arrival") != "mixed":
            problems.append("a mixed binding was not read as mixed: %r" % pt.get("arrival"))
        owners = sorted(s["ownership"] for s in pt.get("call_sites") or [])
        if O_IMPORTED_BY_NAME not in owners:
            problems.append("a from-import call site was not recognised")
        if O_SAME_MODULE not in owners:
            problems.append("a same-module call site was not recognised")

        va = rows.get(("via_attribute", "groups")) or {}
        owners = sorted(s["ownership"] for s in va.get("call_sites") or [])
        kinds = sorted(s["argument_kind"] for s in va.get("call_sites") or [])
        if owners != sorted([O_ON_AN_IMPORTED_MODULE] * 3):
            problems.append("attribute call sites %r" % (owners,))
        if kinds != sorted([A_CALL, A_LITERAL, A_OMITTED_REQUIRED]):
            problems.append("attribute call-site kinds %r" % (kinds,))
        if va.get("arrival") != "mixed":
            problems.append("via_attribute arrival %r" % va.get("arrival"))

        # unbound names: each binding scope is named, and none is silently dropped
        expected_binds = {
            ("inner", "names"): B_OUTER_PARAM,
            ("comprehension", "n"): B_COMPREHENSION_TARGET,
            ("looped", "item"): B_LOOP_TARGET,
            ("broken", "mystery"): B_NOT_BOUND,
            ("destructured", "members"): B_UNPACK_TARGET,
        }
        for key, want in expected_binds.items():
            got = (rows.get(key) or {}).get("binding")
            if got != want:
                problems.append("%r binding %r != %r" % (key, got, want))

        summary = _summary(found["rows"], found["modules_scanned"],
                           upstream.get("summary"))
        if sum(summary["argument_kind_counts"].values()) != summary[
                "call_sites_of_the_owning_functions"]:
            problems.append("the argument arms do not add up on the fixture")
        if summary["forwarded_bindings"] != 7:
            problems.append("fixture forwarded bindings %r" % summary["forwarded_bindings"])
        if _verdict(summary) != V_CALLER_SUPPLIES:
            problems.append("fixture verdict %r != caller-supplies" % _verdict(summary))
        if _verdict(_summary([], 1, {})) != V_NONE:
            problems.append("an empty population was not read as none")
        again_rows = [{"question": "who_supplies_this_parameter",
                       "argument_kind_counts": {A_PARAMETER_AGAIN: 3},
                       "call_sites": [{"ownership": O_SAME_MODULE,
                                       "argument_kind": A_PARAMETER_AGAIN}] * 3,
                       "call_site_count": 3, "arrival": "forwarded_again_at_every_call_site"}]
        if _verdict(_summary(again_rows, 1, {})) != V_AGAIN_FORWARDED:
            problems.append("an all-forwarded population was not read as forwarded again")
        never = [{"question": "who_supplies_this_parameter",
                  "argument_kind_counts": {A_NO_CALL_SITE: 1},
                  "call_sites": [{"ownership": None, "argument_kind": A_NO_CALL_SITE}],
                  "call_site_count": 1, "arrival": "never_supplied"}]
        if _verdict(_summary(never, 1, {})) != V_NEVER_CALLED:
            problems.append("an uncalled function was not read as never called")

        # the face's own arithmetic, and a tampered summary must be caught
        face = build(root, write=False, upstream=upstream)
        problems.extend(["check: " + p for p in check(face, root)])
        face["summary"]["forwarded_bindings"] += 1
        if not check(face, root):
            problems.append("a tampered summary still checked clean")

        # verify() must see a stale file
        face = build(root, write=True, upstream=upstream)
        if verify(root, upstream=upstream):
            problems.append("a freshly written fixture face does not verify against itself")
        face["rows"][0]["dominant_argument_kind"] = A_READ
        write_face(face, root)
        if not verify(root, upstream=upstream):
            problems.append("a tampered row still verified")

        # site_problems catches provenance and row-level contradictions
        face = build(root, write=True, upstream=upstream)
        if site_problems(face, root):
            problems.extend(["site: " + p for p in site_problems(face, root)])
        broken = json.loads(json.dumps(face))
        broken["rows"][0]["binding"] = B_NOT_BOUND
        if not site_problems(broken, root):
            problems.append("a binding on a parameter row survived the guard")
        broken = json.loads(json.dumps(face))
        unbound_row = [r for r in broken["rows"] if r["question"] == "where_is_this_name_bound"][0]
        unbound_row["arrival"] = "bound_by_another_scope" if unbound_row["binding"] == B_NOT_BOUND \
            else "not_bound"
        if not site_problems(broken, root):
            problems.append("an arrival contradicting its binding survived the guard")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return problems


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build()
        print("FORWARDEDARG %s verdict=%s headers=%d call_sites=%d"
              % (DATE_STAMP, face["verdict"], face["summary"]["forwarded_bindings"],
                 face["summary"]["call_sites_of_the_owning_functions"]))
        print(json.dumps(face["summary"], ensure_ascii=False, indent=1))
        return 0
    if cmd == "check":
        problems = site_problems()
        for problem in problems:
            print("[FAIL] " + problem)
        print("check problems=%d" % len(problems))
        return 0 if not problems else 1
    if cmd == "verify":
        problems = verify()
        for problem in problems:
            print("[FAIL] " + problem)
        print("verify problems=%d" % len(problems))
        return 0 if not problems else 1
    if cmd == "selftest":
        problems = selftest()
        for problem in problems:
            print("[FAIL] " + problem)
        print("selftest problems=%d" % len(problems))
        return 0 if not problems else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())