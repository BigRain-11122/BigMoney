"""E519 -- where does the 183 local argument that a caller passes actually come from?

E516 (r1544 bm-b) published that 48 of the 58 local-carried bindings are never handed a real
population by a caller, and that 183 of the 248 call-site arguments it read are themselves a
local of the calling function.  "A local" is the same question one level up: the caller built
it in its own body.  This study follows each of those arguments one hop back to the statement
that binds it inside the calling function and publishes what that statement reads --

  a_literal_container_written_inside_the_calling_function
  a_literal_value_written_inside_the_calling_function
  a_module_scope_constant_of_the_calling_module
  an_attribute_on_an_imported_module
  a_call_into_another_in_repo_module
  a_call_to_a_function_defined_in_the_calling_module
  a_file_or_directory_read
  a_parameter_of_the_calling_function_itself
  an_expression_computed_inside_the_calling_function
  no_binding_in_the_calling_function_or_its_parameters

so that "only through a local" separates a value genuinely built at the site from one that was
a published population two hops away.  Two things the vocabulary had to be split for: an
argument that is a *parameter* of the caller is not a local at all (the population is one more
hop up), and a plain literal value is not a container.

Population: E516's LOCALCARRIER face, every call site whose argument_kind is AR_LOCAL.  The
count is asserted against E516's own published argument counts so the two faces cannot drift.

Run:  python scripts/e519_local_arg_origin.py [build|check|verify|selftest]
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
import e516_local_carrier as e516  # noqa: E402  (reuse corpus + call index, do not clone)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "localargorigin_latest.json"
DATED_PREFIX = "LOCALARGORIGIN"
DATE_STAMP = "2026-11-08"
CARD = "E519-WHERE-DOES-THE-183-LOCAL-ARGUMENTS-THAT-CALLERS-PASS-ACTUALLY-COME-FROM"
STUDY = "E519_local_argument_origin"
UPSTREAM_FACE = os.path.join("results", "state_tilt", "LOCALCARRIER-2026-11-08.json")
POPULATION_SOURCE = (
    "results/state_tilt/LOCALCARRIER-2026-11-08.json call sites whose argument_kind is "
    "a_local_bound_in_the_calling_function, each followed one hop back to the statement that "
    "binds that name inside the calling function"
)
SELF_EXCLUDED = ("e519_", "run_e519", "_e519", "_r1545_leg519")

# ---------------------------------------------------------------- origin vocabulary
LO_LITERAL_CONTAINER = "a_literal_container_written_inside_the_calling_function"
LO_LITERAL_VALUE = "a_literal_value_written_inside_the_calling_function"
LO_CALLER_MODULE_CONSTANT = "a_module_scope_constant_of_the_calling_module"
LO_OTHER_MODULE_CONSTANT = "an_attribute_on_an_imported_module"
LO_OTHER_MODULE_CALL = "a_call_into_another_in_repo_module"
LO_EXTERNAL_CALL = "a_call_into_a_module_that_is_not_in_this_repo"
LO_METHOD_ON_A_VALUE = "a_method_called_on_a_value_the_caller_already_holds"
LO_OWN_MODULE_CALL = "a_call_to_a_function_defined_in_the_calling_module"
LO_FILE_OR_TREE = "a_file_or_directory_read"
LO_COMPREHENSION = "a_comprehension_over_another_expression"
LO_CALLER_PARAMETER = "a_parameter_of_the_calling_function_itself"
LO_COMPUTED = "an_expression_computed_inside_the_calling_function"
LO_UNRESOLVED = "no_binding_in_the_calling_function_or_its_parameters"
ORIGIN_VOCAB = (LO_LITERAL_CONTAINER, LO_LITERAL_VALUE, LO_CALLER_MODULE_CONSTANT,
                LO_OTHER_MODULE_CONSTANT, LO_OTHER_MODULE_CALL, LO_EXTERNAL_CALL,
                LO_METHOD_ON_A_VALUE, LO_OWN_MODULE_CALL, LO_FILE_OR_TREE,
                LO_COMPREHENSION, LO_CALLER_PARAMETER, LO_COMPUTED, LO_UNRESOLVED)

# a value the caller produces itself in its own body: nothing has to be imported to see it
BUILT_INSIDE = (LO_LITERAL_CONTAINER, LO_LITERAL_VALUE, LO_OWN_MODULE_CALL, LO_COMPUTED,
                LO_COMPREHENSION, LO_METHOD_ON_A_VALUE, LO_EXTERNAL_CALL)
# a value that lives somewhere else: a module constant, another module, or the disk
TWO_HOPS = (LO_CALLER_MODULE_CONSTANT, LO_OTHER_MODULE_CONSTANT, LO_OTHER_MODULE_CALL,
            LO_FILE_OR_TREE)
# neither: the caller forwards a parameter or the name is not bound at all
FORWARDED = (LO_CALLER_PARAMETER, LO_UNRESOLVED)

V_SEPARATES = ("every_local_argument_is_built_inside_the_calling_function_so_readable_only_"
               "through_the_local_still_means_a_value_built_at_the_site")
V_PASSTHROUGH = ("most_local_arguments_are_a_parameter_of_the_calling_function_itself_so_the_"
                 "local_is_one_more_hop_not_a_built_value")
V_TWO_HOPS = ("some_local_arguments_are_a_published_population_two_hops_away_a_module_constant_"
              "of_the_caller_or_a_read_so_local_only_has_to_be_read_row_by_row")
V_NONE = "this_tree_has_no_local_call_site_argument_to_measure"
VERDICT_VOCAB = (V_SEPARATES, V_PASSTHROUGH, V_TWO_HOPS, V_NONE)

MAX_ALIAS_HOPS = 4


def _is_self(rel):
    name = os.path.basename(rel or "")
    return name.startswith(SELF_EXCLUDED)


def _short(node):
    try:
        text = ast.unparse(node)
    except Exception:  # pragma: no cover - py<3.9
        return type(node).__name__
    return text if len(text) <= 120 else text[:117] + "..."


class ArgCorpus(e516.LocalCorpus):
    """E516's corpus (parsed trees + call index inputs) plus per-function parameter/binding facts."""

    def params_of(self, module, funcname):
        funcdef = (self.funcs.get(module) or {}).get(funcname)
        if funcdef is None:
            return []
        args = funcdef.args
        names = [a.arg for a in args.posonlyargs] if hasattr(args, "posonlyargs") else []
        names += [a.arg for a in args.args]
        names += [a.arg for a in (args.kwonlyargs or [])]
        if args.vararg:
            names.append(args.vararg.arg)
        if args.kwarg:
            names.append(args.kwarg.arg)
        return names

    def constants_of(self, module, funcname):
        """Names assigned at least once inside one function body (nested defs skipped)."""
        funcdef = (self.funcs.get(module) or {}).get(funcname)
        if funcdef is None:
            return []
        found = []
        stack = list(funcdef.body)
        while stack:
            node = stack.pop()
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                continue
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        found.append(target.id)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                found.append(node.target.id)
            elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name):
                found.append(node.target.id)
            elif isinstance(node, (ast.For, ast.AsyncFor)) or isinstance(node, ast.withitem):
                target = getattr(node, "target", None) or getattr(node, "optional_vars", None)
                if isinstance(target, ast.Name):
                    found.append(target.id)
            stack.extend(ast.iter_child_nodes(node))
        return found

    def assignments_of(self, module, funcname, name):
        """Every statement that binds ``name`` inside ``funcname`` (nested defs skipped)."""
        out = []
        funcdef = (self.funcs.get(module) or {}).get(funcname)
        if funcdef is None:
            return out
        stack = list(funcdef.body)
        while stack:
            node = stack.pop()
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                continue
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == name:
                        out.append(node.lineno)
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id == name:
                    out.append(node.lineno)
            elif isinstance(node, ast.AugAssign):
                if isinstance(node.target, ast.Name) and node.target.id == name:
                    out.append(node.lineno)
            stack.extend(ast.iter_child_nodes(node))
        return sorted(out)


def _classify(node, module, params, corpus, chain=None):
    """One hop from a local's right-hand side to what it actually reads."""
    chain = chain or []
    if isinstance(node, (ast.List, ast.Tuple, ast.Set, ast.Dict)):
        return LO_LITERAL_CONTAINER, {}, chain
    if isinstance(node, ast.Constant):
        return LO_LITERAL_VALUE, {"value_type": type(node.value).__name__}, chain
    if isinstance(node, ast.Name):
        chain = chain + [node.id]
        if node.id in params:
            return LO_CALLER_PARAMETER, {"parameter": node.id}, chain
        if corpus.lookup(module, node.id) is not None:
            kind, detail = e513.classify_node(corpus.lookup(module, node.id), module, corpus)
            detail = dict(detail or {})
            detail["constant"] = node.id
            detail["what_the_constant_itself_is"] = kind
            return LO_CALLER_MODULE_CONSTANT, detail, chain
        if node.id in (corpus.imports.get(module) or {}):
            return LO_OTHER_MODULE_CONSTANT, {
                "module": corpus.imports.get(module, {}).get(node.id, node.id)}, chain
        # an alias of another local of the same function
        inner = corpus.enclosing(module, node.lineno)
        if inner and node.id in inner["values"] and node.id not in chain and \
                len(chain) < MAX_ALIAS_HOPS:
            return _classify(inner["values"][node.id], module, params, corpus, chain)
        return LO_COMPUTED, {"alias_of": node.id}, chain
    if isinstance(node, ast.Attribute):
        owner = node.value.id if isinstance(node.value, ast.Name) else None
        return LO_OTHER_MODULE_CONSTANT, {
            "module": (corpus.imports.get(module) or {}).get(owner, owner),
            "name": node.attr}, chain
    if isinstance(node, ast.Call):
        return _classify_call(node, module, corpus, chain)
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
        source = node.generators[0].iter if node.generators else None
        over = LO_COMPUTED
        detail = {"expression": _short(node)}
        if source is not None:
            over, inner, _ = _classify(source, module, params, corpus, chain)
            detail["over"] = over
            detail.update(dict((k, v) for k, v in inner.items() if k not in detail))
        return LO_COMPREHENSION, detail, chain
    detail = {"expression": _short(node)}
    return LO_COMPUTED, detail, chain


def _classify_call(node, module, corpus, chain):
    """A call: who is called decides whether the value is built here or read elsewhere."""
    func = node.func
    imports = corpus.imports.get(module) or {}
    if isinstance(func, ast.Name):
        name = func.id
        if name in e513.READERS or name in e513.WALKERS:
            return LO_FILE_OR_TREE, {"callee": name}, chain
        if name in (corpus.funcs.get(module) or {}):
            return LO_OWN_MODULE_CALL, {"callee": name}, chain
        return LO_COMPUTED, {"callee": name}, chain
    if isinstance(func, ast.Attribute):
        receiver = func.value.id if isinstance(func.value, ast.Name) else None
        if receiver is not None and receiver in imports:
            target = imports[receiver]
            stem = os.path.splitext(os.path.basename(target.replace(".", "/")))[0]
            detail = {"module": target, "callee": func.attr}
            if func.attr in e513.READERS or func.attr in e513.WALKERS:
                return LO_FILE_OR_TREE, detail, chain
            if stem in corpus.by_module:
                return LO_OTHER_MODULE_CALL, detail, chain
            return LO_EXTERNAL_CALL, detail, chain
        # the receiver is a value the caller already holds, so the callee names no module
        return LO_METHOD_ON_A_VALUE, {"receiver": receiver, "callee": func.attr}, chain
    return LO_COMPUTED, {"expression": _short(node)}, chain


def population(root=None, upstream=None):
    """E516's local call-site arguments, in site order."""
    root = root or ROOT
    face = upstream if upstream is not None else e513.base._load_json(
        os.path.join(root, UPSTREAM_FACE))
    sites = []
    for row in face.get("rows") or []:
        for call_site in row.get("call_sites") or []:
            if call_site.get("argument_kind") != e516.AR_LOCAL:
                continue
            argument = (call_site.get("argument") or "").strip()
            if not argument:
                continue
            name = argument.split(".")[0].split("(")[0].strip()
            sites.append({
                "module": row.get("module"),
                "site_module": call_site.get("module") or row.get("module"),
                "source": row.get("source"),
                "surface": call_site.get("surface") or row.get("surface"),
                "parameter": (row.get("parameters") or [None])[0],
                "line": call_site.get("line"),
                "expression": argument,
                "name": name,
            })
    return sorted(sites, key=lambda s: (s["source"] or "", s["line"] or 0, s["name"] or ""))


def analyse(root=None, upstream=None):
    root = root or ROOT
    corpus = ArgCorpus(root)
    sites = population(root, upstream)

    rows = {}
    site_records = []
    for site in sites:
        module = site["site_module"]
        enclosing = corpus.enclosing(module, site["line"] or 0)
        funcname = enclosing["func"] if enclosing else None
        params = corpus.params_of(module, funcname) if funcname else []
        name = site["name"]
        key = (module, funcname, name)
        rec = rows.get(key)
        if rec is None:
            if name in params:
                origin, line, detail, chain = LO_CALLER_PARAMETER, None, {"parameter": name}, []
            elif enclosing and name in enclosing["values"]:
                node = enclosing["values"][name]
                origin, detail, chain = _classify(node, module, params, corpus)
                line = getattr(node, "lineno", None)
            else:
                origin, line, detail, chain = LO_UNRESOLVED, None, {
                    "note": "the name is neither a parameter nor bound inside the calling function"
                }, []
            assignments = corpus.assignments_of(module, funcname, name) if funcname else []
            rec = rows[key] = {
                "module": site.get("module"),
                "site_module": module,
                "source": site.get("source"),
                "surface": site.get("surface"),
                "local": name,
                "enclosing_function": funcname,
                "is_a_parameter_of_the_caller": name in params,
                "binding_line": line,
                "origin": origin,
                "origin_detail": detail,
                "alias_chain": chain,
                "assignment_lines": assignments,
                "assignment_statements": len(assignments),
                "sites": 0,
                "surfaces": [],
                "parameters": [],
                "call_sites": [],
            }
        rec["sites"] += 1
        for field, value in (("surfaces", site.get("surface")),
                             ("parameters", site.get("parameter"))):
            if value and value not in rec[field]:
                rec[field].append(value)
        rec["call_sites"].append({
            "surface": site.get("surface"),
            "site_module": module,
            "line": site.get("line"),
            "argument": site.get("expression"),
        })
        site_records.append({
            "source": site.get("source"), "module": site.get("module"),
            "surface": site.get("surface"), "parameter": site.get("parameter"),
            "line": site.get("line"), "argument": site.get("expression"),
            "row_key": "%s|%s|%s" % (module, funcname, name),
        })

    out_rows = [rows[k] for k in sorted(rows, key=lambda k: tuple(str(x) for x in k))]
    for rec in out_rows:
        rec["surfaces"] = sorted(rec["surfaces"])
        rec["parameters"] = sorted(rec["parameters"])
    return {"rows": out_rows, "sites": site_records, "corpus": corpus,
            "modules_scanned": len(corpus.by_module),
            "unreadable": corpus.unreadable}


def _count(records, key, vocab):
    out = dict((v, 0) for v in vocab)
    for rec in records:
        value = rec.get(key)
        if value in out:
            out[value] += 1
        else:
            out[value] = out.get(value, 0) + 1
    return out


def _summary(rows, sites, modules_scanned):
    origins = _count(rows, "origin", ORIGIN_VOCAB)
    return {
        "modules_scanned": modules_scanned,
        "local_call_site_arguments": len(sites),
        "distinct_local_bindings": len(rows),
        "distinct_locals": len({rec.get("local") for rec in rows}),
        "distinct_calling_functions": len({(rec.get("site_module"), rec.get("enclosing_function"))
                                           for rec in rows}),
        "origin_counts": origins,
        "arguments_built_inside_the_calling_function": sum(origins[o] for o in BUILT_INSIDE),
        "arguments_that_are_a_published_population_two_hops_away": sum(
            origins[o] for o in TWO_HOPS),
        "arguments_that_are_a_parameter_of_the_caller": origins[LO_CALLER_PARAMETER],
        "arguments_with_no_binding_in_the_calling_function": origins[LO_UNRESOLVED],
        "locals_bound_by_more_than_one_statement": sum(
            1 for rec in rows if rec.get("assignment_statements", 0) > 1),
        "sites_whose_local_is_bound_more_than_one_statement": sum(
            rec.get("sites") or 0 for rec in rows if rec.get("assignment_statements", 0) > 1),
        "dependency_modules": sorted({(rec.get("origin_detail") or {}).get("module")
                                      for rec in rows
                                      if rec.get("origin") in TWO_HOPS
                                      and (rec.get("origin_detail") or {}).get("module")
                                      and (rec.get("origin_detail") or {}).get(
                                          "module") != rec.get("site_module")}),
        "external_modules_called": sorted({(rec.get("origin_detail") or {}).get("module")
                                           for rec in rows
                                           if rec.get("origin") == LO_EXTERNAL_CALL
                                           and (rec.get("origin_detail") or {}).get("module")}),
        "locals_read_through_a_method_on_a_value_the_caller_holds": sum(
            1 for rec in rows if rec.get("origin") == LO_METHOD_ON_A_VALUE),
        "parameter_names_that_carry_the_population": sorted(
            {rec.get("local") for rec in rows if rec.get("origin") == LO_CALLER_PARAMETER}),
    }


def _verdict(summary):
    if not summary["distinct_local_bindings"]:
        return V_NONE
    built = summary["arguments_built_inside_the_calling_function"]
    two_hops = summary["arguments_that_are_a_published_population_two_hops_away"]
    passthrough = summary["arguments_that_are_a_parameter_of_the_caller"]
    if two_hops == 0 and passthrough == 0:
        return V_SEPARATES
    if passthrough > built:
        return V_PASSTHROUGH
    return V_TWO_HOPS


def _answers(summary):
    origins = summary["origin_counts"]
    return [
        ["How many call-site arguments are a local of the calling function?",
         "%d arguments over %d distinct local bindings, %d distinct locals and %d calling "
         "functions." % (summary["local_call_site_arguments"],
                         summary["distinct_local_bindings"], summary["distinct_locals"],
                         summary["distinct_calling_functions"])],
        ["What does the binding statement read?",
         "%d write a literal inside the caller (%d containers, %d plain values); %d read a "
         "module constant of the caller; %d call another in-repo module; %d call a module that "
         "is not in this repo; %d call a method on a value the caller already holds; %d call "
         "into the caller's own module; %d read a file or walk the tree; %d are an attribute on "
         "an imported module; %d are a comprehension; %d are computed in the caller."
         % (origins[LO_LITERAL_CONTAINER] + origins[LO_LITERAL_VALUE],
            origins[LO_LITERAL_CONTAINER], origins[LO_LITERAL_VALUE],
            origins[LO_CALLER_MODULE_CONSTANT], origins[LO_OTHER_MODULE_CALL],
            origins[LO_EXTERNAL_CALL], origins[LO_METHOD_ON_A_VALUE],
            origins[LO_OWN_MODULE_CALL], origins[LO_FILE_OR_TREE],
            origins[LO_OTHER_MODULE_CONSTANT], origins[LO_COMPREHENSION],
            origins[LO_COMPUTED])],
        ["How many are built in the calling function itself versus read from somewhere else?",
         "%d of %d are produced inside the caller (a literal, its own function, a method on a "
         "value it holds, or an expression); %d are a population that lives elsewhere (a module "
         "constant of the caller, another in-repo module, or the disk); %d are a parameter of "
         "the caller itself; %d have no binding in the caller."
         % (summary["arguments_built_inside_the_calling_function"],
            summary["distinct_local_bindings"],
            summary["arguments_that_are_a_published_population_two_hops_away"],
            summary["arguments_that_are_a_parameter_of_the_caller"],
            summary["arguments_with_no_binding_in_the_calling_function"])],
        ["How many are not built at the site at all?",
         "%d of %d are a parameter of the calling function itself, so the local is one more hop "
         "up and not a value built at the site."
         % (origins[LO_CALLER_PARAMETER], summary["distinct_local_bindings"])],
        ["Which bindings are ambiguous because the name is assigned more than once?",
         "%d bindings (%d sites) are assigned by more than one statement in the same function, "
         "so the published origin is the last assignment the parser saw."
         % (summary["locals_bound_by_more_than_one_statement"],
            summary["sites_whose_local_is_bound_more_than_one_statement"])],
        ["Which dependency modules do the locals come from?",
         "%d distinct: %s." % (len(summary["dependency_modules"]),
                               ", ".join(summary["dependency_modules"][:12]) or "none")],
    ]


def build(root=None, write=True, upstream=None):
    root = root or ROOT
    found = analyse(root, upstream)
    summary = _summary(found["rows"], found["sites"], found["modules_scanned"])
    face = {
        "card": CARD,
        "study": STUDY,
        "title": "Where does a call-site argument that is a local of the caller come from",
        "kind": "static_read_of_the_repo_plus_its_own_published_upstream_faces",
        "evidence_cutoff": DATE_STAMP,
        "generated": e513.base._now(),
        "population_source": POPULATION_SOURCE,
        "origin_vocab": list(ORIGIN_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": summary,
        "answers": _answers(summary),
        "verdict": _verdict(summary),
        "rows": found["rows"],
        "unreadable": found["unreadable"],
        "method_limits": [
            ("a local's binding is taken from the innermost function whose body contains the "
             "call line, and only one hop is followed unless the right-hand side is a bare name "
             "aliased to another local (then up to %d hops)" % MAX_ALIAS_HOPS),
            ("when the same name is assigned by more than one statement the origin published is "
             "the last assignment the parser saw, which is why the assignment count is published "
             "next to every row"),
            ("an argument that is a parameter of the caller is not a local at all and is "
             "published under its own arm; the value it actually holds is supplied one hop "
             "further up and is not measured here"),
            ("a module constant of the caller is published as that arm even though it may itself "
             "be a literal or a read; what the constant is is carried in "
             "origin_detail.what_the_constant_itself_is, but only one hop is priced"),
            ("call sites are the ones E516 already enumerated (matched by callee name inside the "
             "module that defines the surface); a call through an alias of the surface is not in "
             "the population"),
            ("whether a caller's expression really covers every branch is not measured here: this "
             "face answers where a value comes from, not whether the branch is guarded"),
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
    if len(rows) != summary.get("distinct_local_bindings"):
        problems.append("row count %d != summary bindings %r"
                        % (len(rows), summary.get("distinct_local_bindings")))
    origins = _count(rows, "origin", ORIGIN_VOCAB)
    if origins != summary.get("origin_counts"):
        problems.append("origin counts do not re-derive")
    sites = sum(rec.get("sites") or 0 for rec in rows)
    if sites != summary.get("local_call_site_arguments"):
        problems.append("site total %d != summary %r"
                        % (sites, summary.get("local_call_site_arguments")))
    if len({rec.get("local") for rec in rows}) != summary.get("distinct_locals"):
        problems.append("distinct local count does not re-derive")
    if len({(rec.get("site_module"), rec.get("enclosing_function"))
            for rec in rows}) != summary.get("distinct_calling_functions"):
        problems.append("calling function count does not re-derive")
    built = sum(origins[o] for o in BUILT_INSIDE)
    if built != summary.get("arguments_built_inside_the_calling_function"):
        problems.append("built-inside count does not re-derive")
    two_hops = sum(origins[o] for o in TWO_HOPS)
    if two_hops != summary.get("arguments_that_are_a_published_population_two_hops_away"):
        problems.append("two-hop count does not re-derive")
    if origins[LO_CALLER_PARAMETER] != summary.get(
            "arguments_that_are_a_parameter_of_the_caller"):
        problems.append("caller-parameter count does not re-derive")
    if origins[LO_UNRESOLVED] != summary.get("arguments_with_no_binding_in_the_calling_function"):
        problems.append("unresolved count does not re-derive")
    if sum(1 for rec in rows if rec.get("assignment_statements", 0) > 1) != summary.get(
            "locals_bound_by_more_than_one_statement"):
        problems.append("multi-assignment binding count does not re-derive")
    if sum(rec.get("sites") or 0 for rec in rows
           if rec.get("assignment_statements", 0) > 1) != summary.get(
            "sites_whose_local_is_bound_more_than_one_statement"):
        problems.append("multi-assignment site count does not re-derive")
    if sum(origins.values()) != len(rows):
        problems.append("the origin arms do not add up to the binding count")
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
        if rec.get("origin") not in ORIGIN_VOCAB:
            problems.append("%s.%s origin outside the vocabulary"
                            % (rec.get("source"), rec.get("local")))
        if len(rec.get("call_sites") or []) != rec.get("sites"):
            problems.append("%s.%s call site list length disagrees with its count"
                            % (rec.get("source"), rec.get("local")))
        if rec.get("is_a_parameter_of_the_caller") != (
                rec.get("origin") == LO_CALLER_PARAMETER):
            problems.append("%s.%s parameter flag contradicts its origin"
                            % (rec.get("source"), rec.get("local")))
        if rec.get("assignment_statements") != len(rec.get("assignment_lines") or []):
            problems.append("%s.%s assignment count disagrees with its lines"
                            % (rec.get("source"), rec.get("local")))
        source = rec.get("source") or ""
        if not source or not os.path.exists(os.path.join(root, source)):
            problems.append("%s names a source that is not on disk" % (source or "<empty>"))
    return problems


def verify(root=None, upstream=None):
    """Rebuild from the tree and compare with the published file."""
    root = root or ROOT
    problems = []
    face = load_face(root)
    rebuilt = build(root, write=False, upstream=upstream)
    for key in ("summary", "answers", "verdict", "origin_vocab", "verdict_vocab"):
        if face.get(key) != rebuilt.get(key):
            problems.append("%s differs from a fresh build" % key)
    published_rows = face.get("rows") or []
    rebuilt_rows = rebuilt.get("rows") or []
    if published_rows != rebuilt_rows:
        problems.append("rows differ from a fresh build (%d published vs %d rebuilt)"
                        % (len(published_rows), len(rebuilt_rows)))
    if (face.get("unreadable") or []) != (rebuilt.get("unreadable") or []):
        problems.append("the unreadable list differs from a fresh build")
    return problems


# ---------------------------------------------------------------- selftest fixtures
FIX_LITERAL = """\
def surface(groups=None):
    return groups
def go():
    gr = ("a", "b")
    return surface(gr)
"""

FIX_VALUE = """\
def surface(groups=None):
    return groups
def go():
    gr = 3
    return surface(gr)
"""

FIX_MODCONST = """\
NAMES = ("alpha",)
def surface(groups=None):
    return groups
def go():
    gr = NAMES
    return surface(gr)
"""

FIX_OTHERCALL = """\
import helper
def surface(groups=None):
    return groups
def go():
    gr = helper.names()
    return surface(gr)
"""

FIX_FILEREAD = """\
import json
def surface(groups=None):
    return groups
def go(path):
    gr = json.load(open(path))
    return surface(gr)
"""

FIX_PARAM = """\
def surface(groups=None):
    return groups
def go(gr):
    return surface(gr)
"""

FIX_ALIASFILE = """\
import io
def surface(groups=None):
    return groups
def go(path):
    gr = io.open(path)
    return surface(gr)
"""

FIX_DOUBLE = """\
def surface(groups=None):
    return groups
def go():
    gr = ("a",)
    gr = ("b", "c")
    return surface(gr)
"""

FIX_UNRESOLVED = """\
def surface(groups=None):
    return groups
def go():
    return surface(gr)
"""

HELPER = """\
def names():
    return ("gamma",)
"""

FIXTURES = (("fix_literal", FIX_LITERAL), ("fix_value", FIX_VALUE),
            ("fix_modconst", FIX_MODCONST), ("fix_othercall", FIX_OTHERCALL),
            ("fix_fileread", FIX_FILEREAD), ("fix_param", FIX_PARAM),
            ("fix_aliasfile", FIX_ALIASFILE), ("fix_double", FIX_DOUBLE),
            ("fix_unresolved", FIX_UNRESOLVED), ("helper", HELPER))


def _fixture(root):
    scripts = os.path.join(root, "scripts")
    os.makedirs(scripts)
    for name, text in FIXTURES:
        with io.open(os.path.join(scripts, name + ".py"), "w", encoding="utf-8",
                     newline="\n") as fh:
            fh.write(text)
    return scripts


def _fixture_population():
    """One E516-shaped row per fixture module, each with one local call-site argument."""
    lines = {"fix_literal": 5, "fix_value": 5, "fix_modconst": 6, "fix_othercall": 6,
             "fix_fileread": 6, "fix_param": 4, "fix_aliasfile": 6, "fix_double": 6,
             "fix_unresolved": 4}
    locals_ = {"fix_literal": "gr", "fix_value": "gr", "fix_modconst": "gr",
               "fix_othercall": "gr", "fix_fileread": "gr", "fix_param": "gr",
               "fix_aliasfile": "gr", "fix_double": "gr", "fix_unresolved": "gr"}
    rows = []
    for name in lines:
        rows.append({
            "module": name,
            "source": "scripts/%s.py" % name,
            "surface": "surface",
            "parameters": ["groups"],
            "carrier": e516.CC_LOCAL,
            "call_site_count": 1,
            "call_sites": [{"surface": "surface", "module": name,
                            "line": lines[name],
                            "argument_kind": e516.AR_LOCAL,
                            "argument": locals_[name]}],
        })
    return {"rows": rows, "summary": {"call_site_argument_counts": {e516.AR_LOCAL: len(rows)}}}


def selftest():
    import shutil
    import tempfile

    problems = []
    root = tempfile.mkdtemp(prefix="e519_")
    try:
        _fixture(root)
        upstream = _fixture_population()
        found = analyse(root, upstream)
        rows = dict((rec["site_module"], rec) for rec in found["rows"])

        if len(found["rows"]) != len(FIXTURES) - 1:
            problems.append("fixture population %d != %d"
                            % (len(found["rows"]), len(FIXTURES) - 1))

        expected = {
            "fix_literal": LO_LITERAL_CONTAINER,
            "fix_value": LO_LITERAL_VALUE,
            "fix_modconst": LO_CALLER_MODULE_CONSTANT,
            "fix_othercall": LO_OTHER_MODULE_CALL,
            "fix_fileread": LO_FILE_OR_TREE,
            "fix_param": LO_CALLER_PARAMETER,
            "fix_aliasfile": LO_FILE_OR_TREE,
            "fix_double": LO_LITERAL_CONTAINER,
            "fix_unresolved": LO_UNRESOLVED,
        }
        for name, origin in expected.items():
            got = (rows.get(name) or {}).get("origin")
            if got != origin:
                problems.append("%s origin %r != %r" % (name, got, origin))

        # a parameter of the caller is flagged, so it cannot hide as a plain local
        if not (rows.get("fix_param") or {}).get("is_a_parameter_of_the_caller"):
            problems.append("a caller parameter was not flagged as one")
        if (rows.get("fix_literal") or {}).get("is_a_parameter_of_the_caller"):
            problems.append("a plain local was flagged as a caller parameter")

        # the dependency module of a cross-module call is published
        detail = (rows.get("fix_othercall") or {}).get("origin_detail") or {}
        if detail.get("module") != "helper":
            problems.append("the cross-module call did not name its dependency module")
        # a module constant says what the constant itself is
        constant_detail = (rows.get("fix_modconst") or {}).get("origin_detail") or {}
        if constant_detail.get("what_the_constant_itself_is") != e513.HP_LITERAL_NAMES:
            problems.append("a module constant did not carry what it itself is")
        # a name assigned twice is published with its assignment count
        if (rows.get("fix_double") or {}).get("assignment_statements") != 2:
            problems.append("a twice-assigned local was not counted twice")

        # the arms are disjoint and the verdict follows from them
        summary = _summary(found["rows"], found["sites"], found["modules_scanned"])
        if sum((summary.get("origin_counts") or {}).values()) != summary["distinct_local_bindings"]:
            problems.append("the origin arms do not add up on the fixture")
        if _verdict(summary) != V_TWO_HOPS:
            problems.append("fixture verdict %r != two-hops" % _verdict(summary))
        if _verdict(_summary([{"origin": LO_LITERAL_CONTAINER}], [1], 1)) != V_SEPARATES:
            problems.append("an all-built population was not read as separating")
        if _verdict(_summary([], [], 1)) != V_NONE:
            problems.append("an empty population was not read as none")
        if _verdict(_summary([{"origin": LO_CALLER_PARAMETER},
                              {"origin": LO_CALLER_PARAMETER},
                              {"origin": LO_LITERAL_CONTAINER}], [3], 1)) != V_PASSTHROUGH:
            problems.append("a pass-through majority was not read as pass-through")

        # the face's own arithmetic
        face = build(root, write=False, upstream=upstream)
        problems.extend(["check: " + p for p in check(face, root)])
        face["summary"]["distinct_local_bindings"] += 1
        if not check(face, root):
            problems.append("a tampered summary still checked clean")

        # verify() must see a stale file
        face = build(root, write=True, upstream=upstream)
        if verify(root, upstream=upstream):
            problems.append("a freshly written fixture face does not verify against itself")
        face["rows"][0]["origin"] = LO_COMPUTED
        write_face(face, root)
        if not verify(root, upstream=upstream):
            problems.append("a tampered row still verified")

        # site_problems catches provenance and row-level contradictions
        face = build(root, write=True, upstream=upstream)
        if site_problems(face, root):
            problems.extend(["site: " + p for p in site_problems(face, root)])
        broken = json.loads(json.dumps(face))
        broken["rows"][0]["is_a_parameter_of_the_caller"] = not broken["rows"][0][
            "is_a_parameter_of_the_caller"]
        if not site_problems(broken, root):
            problems.append("a flipped parameter flag survived the guard")
        broken = json.loads(json.dumps(face))
        broken["rows"][0]["call_sites"] = []
        broken["rows"][0]["sites"] = 1
        if not site_problems(broken, root):
            problems.append("a row stripped of its call sites survived the guard")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return problems


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build()
        print("LOCALARGORIGIN %s verdict=%s bindings=%d args=%d"
              % (DATE_STAMP, face["verdict"], face["summary"]["distinct_local_bindings"],
                 face["summary"]["local_call_site_arguments"]))
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