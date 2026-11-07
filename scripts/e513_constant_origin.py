"""E513 -- which module constant that supplies a population is itself built from something else.

E508 (r1538 bm-b) classified every call site of E505's 35 argument-only surfaces and found 23
surfaces whose population arrives as a module constant (79 sites). A module constant is not a
published population: ``CORPUS_DIRS = tuple(e346.CORPUS_DIRS)`` and ``FILES = py_files(ROOT)``
both look like one name at the call site, but only the first is a literal written in that module
and only the second is recomputed from the working tree at import time. This study follows each
of those constants one hop -- in-module assignment, imported module attribute, or a call -- and
publishes what the constant ultimately holds plus whether an adapter that imports *only* the
surface module can reach it.

Usage:
    python scripts/e513_constant_origin.py run
    python scripts/e513_constant_origin.py check
    python scripts/e513_constant_origin.py verify
    python scripts/e513_constant_origin.py selftest
"""

from __future__ import annotations

import ast
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e508_caller_supplied_population as e508  # noqa: E402

base = e508.base

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "constantorigin_latest.json"
DATED_PREFIX = "CONSTANTORIGIN"
DATE_STAMP = "2026-11-08"
CARD = "E513-WHICH-CONSTANT-THAT-SUPPLIES-A-POPULATION-IS-ITSELF-BUILT-FROM-SOMETHING-ELSE"
STUDY = "E513_constant_origin"
UPSTREAM_FACE = os.path.join("results", "state_tilt", "CALLERSUPPLIED-2026-11-07.json")
POPULATION_SOURCE = ("results/state_tilt/CALLERSUPPLIED-2026-11-07.json arguments whose kind is "
                     "module_constant_literal_a_module_scope_name_bound_only_to_literals or "
                     "module_constant_built_a_module_scope_name_built_by_code or "
                     "imported_constant_an_attribute_of_another_in_repo_module")
SELF_EXCLUDED = ("e513_", "run_e513", "_e513", "_r1541_leg513")

CONSTANT_KINDS = (
    e508.AK_MODULE_CONSTANT_LITERAL,
    e508.AK_MODULE_CONSTANT_BUILT,
    e508.AK_IMPORTED_CONSTANT,
)

# ---------------------------------------------------------------- hop vocabulary
HP_LITERAL_NAMES = "a_literal_list_tuple_set_or_dict_of_names_written_in_that_module"
HP_LITERAL_OTHER = "a_literal_whose_elements_are_not_names"
HP_ALIAS = "another_module_scope_name_of_the_same_module"
HP_OTHER_MODULE_CONSTANT = "an_attribute_on_an_imported_module"
HP_OTHER_MODULE_CALL = "a_call_into_another_in_repo_module"
HP_OWN_MODULE_CALL = "a_call_to_a_function_defined_in_that_module"
HP_WALK = "a_tree_walk_glob_walk_iterdir_or_listdir"
HP_FILE_READ = "a_call_that_loads_a_file_from_disk"
HP_COMPREHENSION = "a_comprehension_over_another_expression"
HP_PATH = "a_joined_path_expression_or_a_relative_root"
HP_UNRESOLVED = "no_module_scope_binding_for_that_name_in_that_module"
HP_VOCAB = (HP_LITERAL_NAMES, HP_LITERAL_OTHER, HP_ALIAS, HP_OTHER_MODULE_CONSTANT,
            HP_OTHER_MODULE_CALL, HP_OWN_MODULE_CALL, HP_WALK, HP_FILE_READ,
            HP_COMPREHENSION, HP_PATH, HP_UNRESOLVED)

# ---------------------------------------------------------------- origin vocabulary
OR_LITERAL = "the_population_is_written_out_as_names_in_that_module"
OR_CODE = "the_population_is_built_by_code_in_that_module_at_import_time"
OR_WALK = "the_population_is_a_tree_walk_so_it_follows_whatever_is_on_disk"
OR_FILE = "the_population_is_loaded_from_a_file_at_import_time"
OR_OTHER_MODULE = "the_population_lives_in_another_module_and_stops_there"
OR_FUNCTION_LOCAL = ("the_name_is_bound_inside_the_function_that_makes_the_call_so_it_is_not_a_"
                     "module_constant_at_all")
OR_UNRESOLVED = "the_name_has_no_module_scope_binding_in_the_module_that_uses_it"
ORIGIN_VOCAB = (OR_LITERAL, OR_CODE, OR_WALK, OR_FILE, OR_OTHER_MODULE, OR_FUNCTION_LOCAL,
                OR_UNRESOLVED)

SCOPE_MODULE = "module_scope_of_the_calling_module"
SCOPE_SURFACE_MODULE = "module_scope_of_the_module_E508_named_the_surface_after"
SCOPE_FUNCTION = "a_local_of_the_enclosing_function"
SCOPE_NONE = "no_binding_in_either_module"
SCOPE_VOCAB = (SCOPE_MODULE, SCOPE_SURFACE_MODULE, SCOPE_FUNCTION, SCOPE_NONE)

V_LITERAL = "every_module_constant_that_supplies_a_population_is_a_literal_in_its_own_module"
V_SPLIT = ("some_module_constants_are_literals_in_their_own_module_and_some_are_built_elsewhere_"
           "so_recoverable_from_the_call_site_hides_a_second_import")
V_BUILT = "every_module_constant_is_built_by_code_so_no_supplied_population_is_frozen"
V_MIXED = "both_literal_and_built_constants_exist_and_the_built_ones_need_a_second_module_or_a_walk"
VERDICT_VOCAB = (V_LITERAL, V_SPLIT, V_BUILT, V_MIXED)

SRC_SUFFIX = ".py"
MAX_HOPS = 4
WALKERS = ("walk", "iglob", "glob", "rglob", "listdir", "iterdir", "scandir", "py_files")
READERS = ("open", "read_text", "read_bytes", "load", "loads", "read_csv", "read_parquet",
           "read_json", "yaml", "safe_load")
WRAPPERS = ("list", "tuple", "set", "sorted", "frozenset", "dict", "reversed", "iter")
NAMES_CONTAINERS = (ast.List, ast.Tuple, ast.Set, ast.Dict)


# ---------------------------------------------------------------- corpus
def _is_self(rel):
    name = os.path.basename(rel or "")
    return any(name.startswith(pre) for pre in SELF_EXCLUDED)


def _read(path):
    with io.open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _parse(text):
    try:
        return ast.parse(text)
    except SyntaxError:
        return None


def _module_scope(tree):
    """(name -> rhs node, name -> FunctionDef) for one module's top level."""
    values, funcs = {}, {}
    if tree is None:
        return values, funcs
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    values[target.id] = node.value
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.value is not None:
                values[node.target.id] = node.value
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs[node.name] = node
    return values, funcs


def _imports(tree):
    """local name -> module name (only plain ``import x``/``from x import y``)."""
    out = {}
    if tree is None:
        return out
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    out[alias.asname] = alias.name
                else:
                    out[alias.name.split(".")[0]] = alias.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                for alias in node.names:
                    out[alias.asname or alias.name] = node.module
    return out


def _function_bindings(tree):
    """[{func, start, end, values}] for every function body in one module."""
    out = []
    if tree is None:
        return out
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        values = {}
        for sub in ast.walk(node):
            if isinstance(sub, ast.Assign):
                for target in sub.targets:
                    if isinstance(target, ast.Name):
                        values[target.id] = sub.value
            elif isinstance(sub, ast.AnnAssign):
                if isinstance(sub.target, ast.Name) and sub.value is not None:
                    values[sub.target.id] = sub.value
        out.append({"func": node.name, "start": node.lineno,
                    "end": getattr(node, "end_lineno", node.lineno) or node.lineno,
                    "values": values})
    return out


class Corpus(object):
    """Module-name -> one parsed module, for every python file in the tree."""

    def __init__(self, root):
        self.root = root
        self.by_module = {}       # module stem -> rel path
        self.values = {}          # module stem -> {name: rhs}
        self.funcs = {}           # module stem -> {name: FunctionDef}
        self.imports = {}         # module stem -> {local: module}
        self.functions = {}       # module stem -> [{func, start, end, values}]
        self.unreadable = []
        self.files = []
        for path in base.py_files(root):
            rel = base._rel(path, root).replace("\\", "/")
            if _is_self(rel):
                continue
            self.files.append(rel)
            stem = os.path.splitext(os.path.basename(rel))[0]
            self.by_module.setdefault(stem, rel)
        for module, rel in self.by_module.items():
            try:
                text = _read(os.path.join(root, rel))
            except Exception as exc:  # pragma: no cover - defensive
                self.unreadable.append({"source": rel, "problem": repr(exc)[:120]})
                continue
            tree = _parse(text)
            if tree is None:
                self.unreadable.append({"source": rel, "problem": "syntax error"})
                continue
            self.values[module], self.funcs[module] = _module_scope(tree)
            self.functions[module] = _function_bindings(tree)
            self.imports[module] = _imports(tree)

    def lookup(self, module, name):
        return (self.values.get(module) or {}).get(name)

    def enclosing(self, module, line):
        """The innermost function of ``module`` whose body contains ``line``."""
        best = None
        for rec in self.functions.get(module) or []:
            if rec["start"] <= (line or 0) <= rec["end"]:
                if best is None or (rec["end"] - rec["start"]) < (best["end"] - best["start"]):
                    best = rec
        return best


def _names_container(node):
    """True when the node is a container literal whose elements are all bare names/strings."""
    if not isinstance(node, NAMES_CONTAINERS):
        return False
    elts = []
    if isinstance(node, ast.Dict):
        elts = [k for k in node.keys if k is not None] + list(node.values)
    else:
        elts = list(node.elts)
    if not elts:
        return True
    for elt in elts:
        if isinstance(elt, ast.Name):
            continue
        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
            continue
        if isinstance(elt, (ast.List, ast.Tuple)) and _names_container(elt):
            continue
        return False
    return True


def _callee_of(node):
    """(callee name, owning module-name-or-None) for a Call node."""
    func = node.func
    if isinstance(func, ast.Name):
        return func.id, None
    if isinstance(func, ast.Attribute):
        owner = func.value.id if isinstance(func.value, ast.Name) else None
        return func.attr, owner
    return None, None


def classify_node(node, module, corpus):
    """Classify one module-scope right-hand side. Returns (hop kind, detail dict)."""
    detail = {}
    if isinstance(node, ast.Constant):
        return HP_LITERAL_OTHER, detail
    if isinstance(node, NAMES_CONTAINERS):
        return (HP_LITERAL_NAMES if _names_container(node) else HP_LITERAL_OTHER), detail
    if isinstance(node, ast.Name):
        detail["alias"] = node.id
        return HP_ALIAS, detail
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
        detail["element"] = _short(node)
        source = node.generators[0].iter if node.generators else None
        if isinstance(source, ast.Call):
            name, owner = _callee_of(source)
            detail["callee"] = name
            if name in WALKERS:
                return HP_WALK, detail
            if name in READERS:
                return HP_FILE_READ, detail
            if owner is not None:
                detail["module"] = corpus.imports.get(module, {}).get(owner, owner)
                return HP_OTHER_MODULE_CALL, detail
            if name in (corpus.funcs.get(module) or {}):
                return HP_OWN_MODULE_CALL, detail
        if isinstance(source, ast.Attribute) and isinstance(source.value, ast.Name):
            detail["module"] = corpus.imports.get(module, {}).get(source.value.id,
                                                                 source.value.id)
            detail["name"] = source.attr
            return HP_OTHER_MODULE_CONSTANT, detail
        return HP_COMPREHENSION, detail
    if isinstance(node, ast.Attribute):
        owner = node.value
        if isinstance(owner, ast.Name):
            detail["module"] = corpus.imports.get(module, {}).get(owner.id, owner.id)
            detail["name"] = node.attr
        return HP_OTHER_MODULE_CONSTANT, detail
    if isinstance(node, ast.BinOp):
        detail["expression"] = _short(node)
        return HP_PATH, detail
    if isinstance(node, ast.Call):
        name, owner = _callee_of(node)
        detail["callee"] = name
        if owner is None and name in WRAPPERS and len(node.args) == 1:
            inner_kind, inner_detail = classify_node(node.args[0], module, corpus)
            detail["wrapped"] = inner_kind
            detail.update(inner_detail)
            if inner_kind == HP_ALIAS:
                detail["alias"] = inner_detail.get("alias")
            return inner_kind, detail
        if name in WALKERS:
            return HP_WALK, detail
        if name in READERS:
            return HP_FILE_READ, detail
        if owner is None and name in (corpus.funcs.get(module) or {}):
            return HP_OWN_MODULE_CALL, detail
        if owner is not None:
            detail["module"] = corpus.imports.get(module, {}).get(owner, owner)
            return HP_OTHER_MODULE_CALL, detail
        return HP_OTHER_MODULE_CALL if name else HP_PATH, detail
    detail["expression"] = _short(node)
    return HP_PATH, detail


def _short(node):
    try:
        text = ast.unparse(node)
    except Exception:  # pragma: no cover - defensive
        return type(node).__name__
    return text if len(text) <= 120 else text[:117] + "..."


def follow(module, name, corpus):
    """Follow one module-scope name to what it ultimately holds.

    Aliases stay inside the module; an attribute or a call into another module records that
    module and then, when it is a repo module, crosses into it once so the published origin says
    what the population actually holds as well as who has to be imported to see it.
    """
    hops = []
    deps = []
    seen = set()
    current_module, current_name = module, name
    origin = OR_UNRESOLVED
    crossed = None
    for _ in range(MAX_HOPS):
        key = (current_module, current_name)
        if key in seen:
            hops.append({"module": current_module, "name": current_name,
                         "kind": HP_ALIAS, "note": "cycle"})
            origin = OR_UNRESOLVED
            break
        seen.add(key)
        node = corpus.lookup(current_module, current_name)
        if node is None:
            hops.append({"module": current_module, "name": current_name,
                         "kind": HP_UNRESOLVED, "note": "no module-scope binding"})
            origin = OR_OTHER_MODULE if current_module != module else OR_UNRESOLVED
            break
        kind, detail = classify_node(node, current_module, corpus)
        hops.append({"module": current_module, "name": current_name, "kind": kind,
                     "line": getattr(node, "lineno", None), "detail": detail})
        if kind == HP_ALIAS:
            for candidate in [detail.get("alias")]:
                if candidate and corpus.lookup(current_module, candidate) is not None:
                    current_name = candidate
                    break
            else:
                origin = OR_UNRESOLVED
                break
            continue
        if kind in (HP_OTHER_MODULE_CONSTANT, HP_OTHER_MODULE_CALL):
            other = detail.get("module")
            if other and other != current_module:
                if other not in deps:
                    deps.append(other)
                if crossed is None and corpus.lookup(other, detail.get("name") or "") is not None:
                    crossed = other
                    current_module, current_name = other, detail["name"]
                    continue
                if crossed is None and corpus.lookup(other, detail.get("callee") or "") is not None:
                    crossed = other
                    current_module, current_name = other, detail["callee"]
                    continue
            origin = OR_OTHER_MODULE
            break
        if kind == HP_LITERAL_NAMES or kind == HP_LITERAL_OTHER:
            origin = OR_LITERAL
            break
        if kind == HP_WALK:
            origin = OR_WALK
            break
        if kind == HP_FILE_READ:
            origin = OR_FILE
            break
        if kind in (HP_OWN_MODULE_CALL, HP_COMPREHENSION):
            origin = OR_CODE
            break
        origin = OR_CODE
        break
    return {"origin_kind": origin, "hops": hops, "dependency_modules": deps,
            "crossed_into": crossed}


def population(root=None, upstream=None):
    root = root or ROOT
    face = upstream if upstream is not None else base._load_json(os.path.join(root, UPSTREAM_FACE))
    sites = []
    for row in face.get("rows") or []:
        for arg in row.get("arguments") or []:
            if arg.get("kind") not in CONSTANT_KINDS:
                continue
            expr = (arg.get("expression") or "").strip()
            if not expr:
                continue
            source = (row.get("source") or "").replace("\\", "/")
            site_module = os.path.splitext(os.path.basename(source))[0] or row.get("module")
            sites.append({
                "module": row.get("module"),
                "site_module": site_module,
                "source": source,
                "surface": row.get("surface"),
                "call": row.get("call"),
                "line": row.get("line"),
                "parameter": arg.get("parameter"),
                "expression": expr,
                "kind": arg.get("kind"),
                "in_selftest": bool(row.get("in_selftest")),
            })
    return sorted(sites, key=lambda s: (s["source"] or "", s["line"] or 0, s["expression"]))


def resolve(site, corpus):
    """Resolve one site's constant name, reporting which scope actually holds the binding.

    E508 labelled an expression a module constant when the name exists at module scope
    somewhere relevant; at the call site the same name can be a local of the enclosing
    function, which is not a published population at all. Resolution order: the calling
    module's own module scope, then a local of the enclosing function, then the module E508
    named the surface after.
    """
    name = site["expression"].split(".")[0]
    call_module = site.get("site_module") or site.get("module")
    surface_module = site.get("module")
    if corpus.lookup(call_module, name) is not None:
        followed = follow(call_module, name, corpus)
        followed.update({"scope": SCOPE_MODULE, "scope_module": call_module,
                         "binding_line": getattr(corpus.lookup(call_module, name), "lineno", None)})
        return followed
    enclosing = corpus.enclosing(call_module, site.get("line") or 0)
    if enclosing and name in enclosing["values"]:
        node = enclosing["values"][name]
        kind, detail = classify_node(node, call_module, corpus)
        return {"origin_kind": _origin_of(kind), "scope": SCOPE_FUNCTION,
                "scope_module": call_module, "enclosing_function": enclosing["func"],
                "binding_line": getattr(node, "lineno", None),
                "hops": [{"module": call_module, "name": name, "kind": kind,
                          "line": getattr(node, "lineno", None), "detail": detail}],
                "dependency_modules": [detail["module"]] if detail.get("module")
                and detail.get("module") != call_module else [],
                "crossed_into": None}
    if surface_module and surface_module != call_module and corpus.lookup(surface_module,
                                                                        name) is not None:
        followed = follow(surface_module, name, corpus)
        followed.update({"scope": SCOPE_SURFACE_MODULE, "scope_module": surface_module,
                         "binding_line": getattr(corpus.lookup(surface_module, name), "lineno",
                                                 None)})
        return followed
    return {"origin_kind": OR_UNRESOLVED, "scope": SCOPE_NONE, "scope_module": None,
            "hops": [{"module": call_module, "name": name, "kind": HP_UNRESOLVED,
                      "note": "no binding in module scope, the enclosing function, or the "
                              "surface module"}],
            "dependency_modules": [], "crossed_into": None}


def _origin_of(hop_kind):
    if hop_kind in (HP_LITERAL_NAMES, HP_LITERAL_OTHER):
        return OR_LITERAL
    if hop_kind == HP_WALK:
        return OR_WALK
    if hop_kind == HP_FILE_READ:
        return OR_FILE
    if hop_kind == HP_UNRESOLVED:
        return OR_UNRESOLVED
    if hop_kind in (HP_OTHER_MODULE_CONSTANT, HP_OTHER_MODULE_CALL):
        return OR_OTHER_MODULE
    return OR_CODE


def analyse(root=None, upstream=None):
    root = root or ROOT
    sites = population(root, upstream)
    corpus = Corpus(root)
    resolved = []
    for site in sites:
        followed = resolve(site, corpus)
        resolved.append((site, followed))
    by_const = {}
    for site, followed in resolved:
        # identity of a resolved binding: the module the name is bound in, the name, the scope
        # kind, and -- for a function local -- the enclosing function, because one module can
        # bind the same name in two different functions
        key = (site["site_module"], site["expression"].split(".")[0], followed["scope"],
               followed.get("enclosing_function"))
        rec = by_const.setdefault(key, {"site": site, "followed": followed,
                                        "sites": [], "surfaces": []})
        rec["sites"].append(site)
        if site["surface"] not in rec["surfaces"]:
            rec["surfaces"].append(site["surface"])
    rows = []
    for key, rec in sorted(by_const.items(), key=lambda kv: tuple(str(x) for x in kv[0])):
        site = rec["site"]
        followed = rec["followed"]
        needs_other = followed["origin_kind"] in (OR_OTHER_MODULE,) or bool(
            followed["dependency_modules"])
        rows.append({
            "module": site["module"],
            "surface_modules": sorted({s["module"] for s in rec["sites"] if s.get("module")}),
            "site_module": site["site_module"],
            "constant": site["expression"].split(".")[0],
            "source": site["source"],
            "scope": followed["scope"],
            "scope_module": followed.get("scope_module"),
            "enclosing_function": followed.get("enclosing_function"),
            "binding_line": followed.get("binding_line"),
            "origin_kind": followed["origin_kind"],
            "hops": followed["hops"],
            "dependency_modules": followed["dependency_modules"],
            "crossed_into": followed["crossed_into"],
            "needs_another_module": needs_other,
            "readable_by_an_adapter_that_imports_only_the_surface_module": (
                followed["scope"] in (SCOPE_MODULE, SCOPE_SURFACE_MODULE)
                and followed["origin_kind"] in (OR_LITERAL, OR_CODE, OR_WALK, OR_FILE)
                and not needs_other),
            "recomputed_at_import": followed["origin_kind"] in (OR_WALK, OR_FILE, OR_CODE),
            "sites": len(rec["sites"]),
            "surfaces": rec["surfaces"],
            "in_selftest_sites": sum(1 for s in rec["sites"] if s["in_selftest"]),
        })
    return {"sites": sites, "rows": rows, "unreadable": corpus.unreadable,
            "modules_scanned": len(corpus.by_module), "files": corpus.files}


def _count(records, key, vocab):
    counts = {k: 0 for k in vocab}
    for rec in records:
        counts[rec.get(key)] = counts.get(rec.get(key), 0) + 1
    return counts


def _summary(rows, sites, modules_scanned):
    origins = _count(rows, "origin_kind", ORIGIN_VOCAB)
    scopes = _count(rows, "scope", SCOPE_VOCAB)
    hops = {}
    for row in rows:
        for hop in row["hops"]:
            hops[hop["kind"]] = hops.get(hop["kind"], 0) + 1
    surfaces = sorted({s for row in rows for s in row["surfaces"]})
    unreachable = sorted({r["module"] for r in rows
                          if not r["readable_by_an_adapter_that_imports_only_the_surface_module"]})
    return {
        "module_constant_sites_in_e508_face": len(sites),
        "distinct_bindings_followed": len(rows),
        "distinct_surfaces_supplied_by_a_constant": len(surfaces),
        "modules_scanned": modules_scanned,
        "origin_counts": origins,
        "scope_counts": scopes,
        "hop_kind_counts": dict(sorted(hops.items())),
        "populations_written_out_as_names_in_their_own_module": origins[OR_LITERAL],
        "populations_that_need_a_second_module": sum(1 for r in rows if r["needs_another_module"]),
        "populations_that_are_recomputed_from_the_tree_or_a_file_at_import_time": (
            origins[OR_WALK] + origins[OR_FILE]),
        "names_that_are_a_function_local_rather_than_a_module_constant": scopes[SCOPE_FUNCTION],
        "sites_whose_name_is_a_function_local": sum(
            r["sites"] for r in rows if r["scope"] == SCOPE_FUNCTION),
        "populations_no_module_scope_binding_can_answer": origins[OR_UNRESOLVED],
        "constants_an_adapter_can_reach_by_importing_only_the_surface_module": sum(
            1 for r in rows if r["readable_by_an_adapter_that_imports_only_the_surface_module"]),
        "modules_that_lose_a_population_if_the_surface_module_is_imported_alone": unreachable,
        "sites_that_lose_reachability": sum(
            r["sites"] for r in rows
            if not r["readable_by_an_adapter_that_imports_only_the_surface_module"]),
        "rows_whose_constant_crosses_into_a_repo_module": sum(
            1 for r in rows if r["crossed_into"]),
    }


def _verdict(summary):
    lit = summary["populations_written_out_as_names_in_their_own_module"]
    other = summary["populations_that_need_a_second_module"]
    computed = summary["populations_that_are_recomputed_from_the_tree_or_a_file_at_import_time"]
    local = summary["names_that_are_a_function_local_rather_than_a_module_constant"]
    total = summary["distinct_bindings_followed"]
    if total and lit == total:
        return V_LITERAL
    if total and lit == 0 and computed == 0 and local == 0:
        return V_BUILT
    if lit and (other or computed):
        return V_SPLIT if other else V_MIXED
    return V_BUILT


def _answers(summary):
    return {
        "how_many_module_constant_sites_did_e508_publish": summary[
            "module_constant_sites_in_e508_face"],
        "how_many_distinct_bindings_are_followed": summary["distinct_bindings_followed"],
        "how_many_are_written_out_as_names_in_their_own_module": summary[
            "populations_written_out_as_names_in_their_own_module"],
        "how_many_need_a_second_module": summary["populations_that_need_a_second_module"],
        "how_many_are_recomputed_from_the_tree_or_a_file": summary[
            "populations_that_are_recomputed_from_the_tree_or_a_file_at_import_time"],
        "how_many_names_are_a_function_local_and_therefore_not_a_module_constant": summary[
            "names_that_are_a_function_local_rather_than_a_module_constant"],
        "how_many_sites_whose_name_is_a_function_local": summary[
            "sites_whose_name_is_a_function_local"],
        "how_many_cannot_be_answered_by_any_module_scope_binding": summary[
            "populations_no_module_scope_binding_can_answer"],
        "how_many_can_be_read_by_importing_only_the_surface_module": summary[
            "constants_an_adapter_can_reach_by_importing_only_the_surface_module"],
        "how_many_sites_lose_reachability": summary["sites_that_lose_reachability"],
        "how_many_surfaces_are_supplied_by_a_constant": summary[
            "distinct_surfaces_supplied_by_a_constant"],
    }


def build(root=None, write=True, upstream=None):
    root = root or ROOT
    found = analyse(root, upstream)
    summary = _summary(found["rows"], found["sites"], found["modules_scanned"])
    face = {
        "card": CARD,
        "study": STUDY,
        "title": ("Which module constant that supplies a population is itself built from "
                  "something else"),
        "kind": "static_read_of_the_repo_plus_its_own_published_upstream_face",
        "evidence_cutoff": DATE_STAMP,
        "generated": base._now(),
        "population_source": POPULATION_SOURCE,
        "origin_vocab": list(ORIGIN_VOCAB),
        "scope_vocab": list(SCOPE_VOCAB),
        "hop_vocab": list(HP_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": summary,
        "answers": _answers(summary),
        "verdict": _verdict(summary),
        "rows": found["rows"],
        "unreadable": found["unreadable"],
        "method_limits": [
            ("a module constant is followed at module scope only: a name rebound inside a "
             "function is not part of what the surface module publishes"),
            ("aliases stay inside the module and cycles stop the walk; a call into another "
             "module crosses once and stops, so the published origin names the dependency "
             "instead of resolving the whole tree"),
            ("readable_by_an_adapter_that_imports_only_the_surface_module is about the import "
             "edge, not about side effects: a tree walk is reachable but not frozen"),
            ("the upstream face's own kind labels are taken as given; this study does not "
             "re-derive whether a site really passes a module constant"),
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
    return base._load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))


def check(face=None, root=None):
    """Re-derive every published number from the face's own rows."""
    root = root or ROOT
    face = face or load_face(root)
    problems = []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    if len(rows) != summary.get("distinct_bindings_followed"):
        problems.append("row count %d != summary bindings %r"
                        % (len(rows), summary.get("distinct_bindings_followed")))
    origins = _count(rows, "origin_kind", ORIGIN_VOCAB)
    if origins != summary.get("origin_counts"):
        problems.append("origin counts do not re-derive")
    scopes = _count(rows, "scope", SCOPE_VOCAB)
    if scopes != summary.get("scope_counts"):
        problems.append("scope counts do not re-derive")
    if scopes[SCOPE_FUNCTION] != summary.get(
            "names_that_are_a_function_local_rather_than_a_module_constant"):
        problems.append("function-local count does not re-derive")
    if sum(r["sites"] for r in rows if r["scope"] == SCOPE_FUNCTION) != summary.get(
            "sites_whose_name_is_a_function_local"):
        problems.append("function-local site count does not re-derive")
    lit = sum(1 for r in rows if r["origin_kind"] == OR_LITERAL)
    if lit != summary.get("populations_written_out_as_names_in_their_own_module"):
        problems.append("literal count does not re-derive")
    need = sum(1 for r in rows if r["needs_another_module"])
    if need != summary.get("populations_that_need_a_second_module"):
        problems.append("second-module count does not re-derive")
    recomputed = sum(1 for r in rows
                     if r["origin_kind"] in (OR_WALK, OR_FILE))
    if recomputed != summary.get(
            "populations_that_are_recomputed_from_the_tree_or_a_file_at_import_time"):
        problems.append("recomputed count does not re-derive")
    sites = sum(r["sites"] for r in rows)
    if sites != summary.get("module_constant_sites_in_e508_face"):
        problems.append("site total %d != summary %r"
                        % (sites, summary.get("module_constant_sites_in_e508_face")))
    for row in rows:
        if row["origin_kind"] not in ORIGIN_VOCAB:
            problems.append("%s.%s origin outside the vocabulary"
                            % (row["module"], row["constant"]))
        if row["scope"] not in SCOPE_VOCAB:
            problems.append("%s.%s scope outside the vocabulary"
                            % (row["module"], row["constant"]))
        if not row["hops"]:
            problems.append("%s.%s has no hop" % (row["module"], row["constant"]))
        for hop in row["hops"]:
            if hop["kind"] not in HP_VOCAB:
                problems.append("%s.%s hop kind outside the vocabulary"
                                % (row["module"], row["constant"]))
        expected = (row["scope"] in (SCOPE_MODULE, SCOPE_SURFACE_MODULE)
                    and row["origin_kind"] in (OR_LITERAL, OR_CODE, OR_WALK, OR_FILE)
                    and not row["needs_another_module"])
        if bool(row["readable_by_an_adapter_that_imports_only_the_surface_module"]) != expected:
            problems.append("%s.%s readability contradicts its scope, origin and dependencies"
                            % (row["module"], row["constant"]))
    answers = face.get("answers") or {}
    if answers.get("how_many_can_be_read_by_importing_only_the_surface_module") != sum(
            1 for r in rows if r["readable_by_an_adapter_that_imports_only_the_surface_module"]):
        problems.append("adapter-reach answer does not re-derive")
    if face.get("verdict") != _verdict(summary):
        problems.append("verdict does not re-derive from the summary")
    return problems


def verify(root=None):
    """Rebuild from the tree and compare with the published file."""
    root = root or ROOT
    problems = []
    face = load_face(root)
    rebuilt = build(root, write=False)
    for key in ("summary", "answers", "verdict", "origin_vocab", "scope_vocab", "hop_vocab"):
        if face.get(key) != rebuilt.get(key):
            problems.append("%s differs from a fresh build" % key)
    return problems


# ---------------------------------------------------------------- selftest fixture
FIX_LITERAL = """\
NAMES = ("alpha", "beta")
def surface(groups=(NAMES,)):
    return groups
def go():
    return surface(NAMES)
"""

FIX_ALIAS = """\
BASE = ["alpha", "beta"]
ALIAS = BASE
def surface(groups=()):
    return groups
def go():
    return surface(ALIAS)
"""

FIX_OTHER = """\
import helper
NAMES = tuple(helper.NAMES)
def surface(groups=()):
    return groups
def go():
    return surface(NAMES)
"""

FIX_WALK = """\
import os
HERE = os.path.dirname(os.path.abspath(__file__))
FILES = [p for p in os.listdir(HERE) if p.endswith(".py")]
def surface(groups=()):
    return groups
def go():
    return surface(FILES)
"""

FIX_OWN_CALL = """\
def _names():
    return ("alpha", "beta")
NAMES = _names()
def surface(groups=()):
    return groups
def go():
    return surface(NAMES)
"""

FIX_UNRESOLVED = """\
NAMES = ()
def surface(groups=()):
    return groups
def go():
    return surface(_missing)
"""

FIX_LOCAL = """\
def _names():
    return ("alpha", "beta")
def surface(groups=()):
    return groups
def go():
    NAMES = _names()
    return surface(NAMES)
"""

HELPER = """\
NAMES = ("gamma",)
"""


def _fixture_face():
    """A tiny upstream face with one module-constant site per fixture module."""
    rows = []
    for module, expr, line in (("fix_literal", "NAMES", 1), ("fix_alias", "ALIAS", 1),
                               ("fix_other", "NAMES", 1), ("fix_walk", "FILES", 1),
                               ("fix_own_call", "NAMES", 1), ("fix_unresolved", "_missing", 5),
                               ("fix_local", "NAMES", 7)):
        rows.append({
            "module": module, "source": "scripts/%s.py" % module, "surface": "surface",
            "call": "surface", "line": line, "in_selftest": False,
            "arguments": [{"expression": expr, "parameter": "groups", "position": 0,
                           "kind": e508.AK_MODULE_CONSTANT_BUILT}],
        })
    return {"rows": rows}


def _write_fixture(root):
    files = {
        "scripts/fix_literal.py": FIX_LITERAL,
        "scripts/fix_alias.py": FIX_ALIAS,
        "scripts/fix_other.py": FIX_OTHER,
        "scripts/fix_walk.py": FIX_WALK,
        "scripts/fix_own_call.py": FIX_OWN_CALL,
        "scripts/fix_unresolved.py": FIX_UNRESOLVED,
        "scripts/fix_local.py": FIX_LOCAL,
        "scripts/helper.py": HELPER,
    }
    for rel, text in files.items():
        path = os.path.join(root, rel)
        d = os.path.dirname(path)
        if not os.path.isdir(d):
            os.makedirs(d)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    return files


def selftest():
    bad = []

    def expect(cond, label):
        if not cond:
            bad.append(label)

    tmp = tempfile.mkdtemp(prefix="e513_fixture_")
    try:
        _write_fixture(tmp)
        face = _fixture_face()
        found = analyse(tmp, face)
        by_name = {(r["module"], r["constant"]): r for r in found["rows"]}
        expect(set(by_name) == {("fix_literal", "NAMES"), ("fix_alias", "ALIAS"),
                                ("fix_other", "NAMES"), ("fix_walk", "FILES"),
                                ("fix_own_call", "NAMES"),
                                ("fix_unresolved", "_missing"),
                                ("fix_local", "NAMES")},
               "population of distinct constants is %r" % (sorted(by_name),))

        lit = by_name[("fix_literal", "NAMES")]
        expect(lit["origin_kind"] == OR_LITERAL, "literal fixture resolved to %r"
               % (lit["origin_kind"],))
        expect(lit["readable_by_an_adapter_that_imports_only_the_surface_module"],
               "a literal constant must be readable from its own module")
        expect(lit["recomputed_at_import"] is False, "a literal must not be recomputed")

        alias = by_name[("fix_alias", "ALIAS")]
        expect(alias["origin_kind"] == OR_LITERAL, "alias fixture resolved to %r"
               % (alias["origin_kind"],))
        expect([h["kind"] for h in alias["hops"]] == [HP_ALIAS, HP_LITERAL_NAMES],
               "alias hops are %r" % ([h["kind"] for h in alias["hops"]],))

        other = by_name[("fix_other", "NAMES")]
        expect(other["origin_kind"] == OR_LITERAL, "crossed-module fixture resolved to %r"
               % (other["origin_kind"],))
        expect(other["needs_another_module"] is True, "crossed-module fixture must need a module")
        expect("helper" in other["dependency_modules"], "dependency modules are %r"
               % (other["dependency_modules"],))
        expect(other["crossed_into"] == "helper", "crossed_into is %r" % (other["crossed_into"],))
        expect(other["readable_by_an_adapter_that_imports_only_the_surface_module"] is False,
               "a constant that imports another module is not readable from the surface module")

        walk = by_name[("fix_walk", "FILES")]
        expect(walk["origin_kind"] == OR_WALK, "walk fixture resolved to %r"
               % (walk["origin_kind"],))
        expect(walk["recomputed_at_import"] is True, "a walk must be recomputed")

        own = by_name[("fix_own_call", "NAMES")]
        expect(own["origin_kind"] == OR_CODE, "own-call fixture resolved to %r"
               % (own["origin_kind"],))
        expect(own["readable_by_an_adapter_that_imports_only_the_surface_module"],
               "an in-module build must stay readable")

        missing = by_name[("fix_unresolved", "_missing")]
        expect(missing["origin_kind"] == OR_UNRESOLVED, "unresolved fixture resolved to %r"
               % (missing["origin_kind"],))
        expect(missing["readable_by_an_adapter_that_imports_only_the_surface_module"] is False,
               "an unresolved name cannot be readable")

        local = by_name[("fix_local", "NAMES")]
        expect(local["scope"] == SCOPE_FUNCTION, "local fixture scope is %r" % (local["scope"],))
        expect(local["enclosing_function"] == "go", "local fixture enclosing function is %r"
               % (local["enclosing_function"],))
        expect(local["origin_kind"] == OR_CODE, "local fixture origin is %r"
               % (local["origin_kind"],))
        expect(local["readable_by_an_adapter_that_imports_only_the_surface_module"] is False,
               "a function-local is not readable by importing the module")

        # cycle protection
        cyc_dir = os.path.join(tmp, "scripts")
        with io.open(os.path.join(cyc_dir, "fix_cycle.py"), "w", encoding="utf-8",
                     newline="\n") as fh:
            fh.write("A = B\nB = A\n")
        corpus = Corpus(tmp)
        cyc = follow("fix_cycle", "A", corpus)
        expect(cyc["origin_kind"] == OR_UNRESOLVED, "a cycle must end unresolved, got %r"
               % (cyc["origin_kind"],))
        expect(any(h.get("note") == "cycle" for h in cyc["hops"]), "the cycle hop must be recorded")

        # identity: check() on a fresh fixture face must be clean
        summary = _summary(found["rows"], found["sites"], found["modules_scanned"])
        fixture_face = {"rows": found["rows"], "summary": summary,
                        "answers": _answers(summary), "verdict": _verdict(summary)}
        expect(check(fixture_face, tmp) == [], "check() on the fixture must be clean: %r"
               % (check(fixture_face, tmp),))

        # doctored copies must be refused
        doctored = json.loads(json.dumps(fixture_face))
        doctored["verdict"] = V_LITERAL
        expect(check(doctored, tmp) != [], "a hand-written verdict must be refused")
        doctored = json.loads(json.dumps(fixture_face))
        doctored["summary"]["populations_that_need_a_second_module"] += 1
        expect(check(doctored, tmp) != [], "an inflated dependency count must be refused")
        doctored = json.loads(json.dumps(fixture_face))
        doctored["rows"][0]["readable_by_an_adapter_that_imports_only_the_surface_module"] = (
            not doctored["rows"][0]["readable_by_an_adapter_that_imports_only_the_surface_module"])
        expect(check(doctored, tmp) != [], "a flipped readability flag must be refused")
        doctored = json.loads(json.dumps(fixture_face))
        doctored["rows"][0]["hops"][0]["kind"] = "a_kind_that_is_not_in_the_vocabulary"
        expect(check(doctored, tmp) != [], "a hop kind outside the vocabulary must be refused")
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    return bad


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = build()
        print(json.dumps({"face": FACE_NAME, "card": face["card"],
                          "verdict": face["verdict"],
                          "bindings": face["summary"]["distinct_bindings_followed"],
                          "answers": face["answers"]}, ensure_ascii=False, indent=1))
        return 0
    if cmd == "check":
        problems = check()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "selftest":
        bad = selftest()
        print(json.dumps({"selftest": len(bad), "bad": bad}, ensure_ascii=False))
        return 0 if not bad else 1
    print("usage: run | check | verify | selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())