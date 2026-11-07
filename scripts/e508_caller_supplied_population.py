"""E508 -- who supplies the population to the 35 argument-only surfaces.

E505 priced the population-naming surface of 180 studies and found 35 whose only such
surface is a function that needs caller arguments, so no adapter can read the population
and the arm stays unpriced.  That is a fact about the signature.  This study asks the
next question: where does the value come from when the code actually calls it?  For each
of those 35 surfaces it reads every call site in the tree -- the module's own calls and
any other module that imports it -- and publishes, per site, the expression supplied to
each parameter and the kind of value it is: a literal list of names, a module constant,
a tree walk, a file read, another call, a parameter of the calling function, or the
process cwd.  The surface then gets a resolution (what an adapter would have to do to
read the population) and a reach (whether anything outside its own module ever calls it).

So the bucket stops having a class no instrument can read: a surface that everyone calls
with a frozen literal is cheap to price, a surface that only ever receives its caller's
parameter is not priced here at all, and a surface nobody calls has no population to
price until something runs it.

Modes: run|build / check / verify / selftest.  Read-only: check, verify, selftest.

Reuse: the tree walker, text reader and module assignment walker of
``scripts/e504_name_compose.py`` are imported, never copied.  The population is E505's
own published face; it is never re-derived here.
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

ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "callersupplied_latest.json"
DATED_PREFIX = "CALLERSUPPLIED"
DATE_STAMP = "2026-11-07"
CARD = "E508-WHICH-CALLER-SUPPLIES-THE-POPULATION-TO-THE-35-ARGUMENT-ONLY-SURFACES"
STUDY = "E508_caller_supplied_population"
UPSTREAM_FACE = os.path.join("results", "state_tilt", "UNMEASUREDREACH-2026-11-07.json")
POPULATION_SOURCE = ("results/state_tilt/UNMEASUREDREACH-2026-11-07.json rows with class="
                     "the_only_surface_that_names_a_population_requires_caller_arguments")
ARG_ONLY = "the_only_surface_that_names_a_population_requires_caller_arguments"
SELF_EXCLUDED = ("e508_", "run_e508", "_e508")

# ---------------------------------------------------------------- vocabulary
AK_LITERAL_NAMES = ("literal_names_a_list_tuple_set_or_dict_literal_of_string_names_written_"
                    "at_the_call_site")
AK_COMPOSITE_LITERAL = "composite_literal_a_literal_whose_elements_are_not_all_strings"
AK_LITERAL_STRING = "literal_string_a_single_string_literal"
AK_MODULE_CONSTANT_LITERAL = ("module_constant_literal_a_module_scope_name_bound_only_to_"
                              "literals")
AK_MODULE_CONSTANT_BUILT = "module_constant_built_a_module_scope_name_built_by_code"
AK_IMPORTED_CONSTANT = "imported_constant_an_attribute_of_another_in_repo_module"
AK_WALK = ("tree_walk_a_call_that_walks_the_tree_glob_walk_listdir_or_an_in_repo_callee_"
           "that_does")
AK_FILE_READ = "file_read_a_call_that_loads_a_file"
AK_DERIVED = ("derived_from_other_values_a_comprehension_or_a_wrapper_over_a_caller_value_"
              "rather_than_a_name_written_at_the_site")
AK_CALL_RESULT = "call_result_a_call_to_some_other_function"
AK_PARAMETER = "caller_parameter_a_parameter_of_the_enclosing_function"
AK_CWD = "process_cwd_os_getcwd_or_a_bare_dot"
AK_PATH_COMPOSITION = "path_composition_a_joined_path_expression"
AK_FILE_ROOT = "file_relative_root_derived_from_dunder_file_not_the_process_cwd"
AK_KEYWORD_DEFAULT = "not_supplied_the_population_parameter_is_omitted_at_this_site"
AK_UNKNOWN = "unknown_an_expression_this_reader_does_not_classify"
AK_VOCAB = (AK_LITERAL_NAMES, AK_COMPOSITE_LITERAL, AK_LITERAL_STRING,
            AK_MODULE_CONSTANT_LITERAL, AK_MODULE_CONSTANT_BUILT, AK_IMPORTED_CONSTANT,
            AK_WALK, AK_FILE_READ, AK_DERIVED, AK_CALL_RESULT, AK_PARAMETER, AK_CWD,
            AK_PATH_COMPOSITION, AK_FILE_ROOT, AK_KEYWORD_DEFAULT, AK_UNKNOWN)

R_LITERAL = "a_caller_passes_a_literal"
R_CONSTANT = "a_caller_passes_a_module_constant"
R_WALK = "a_caller_passes_a_tree_walk"
R_FILE = "a_caller_passes_a_file_read"
R_DERIVED = "a_caller_derives_the_population_from_other_values_at_the_site"
R_CALL = "a_caller_passes_the_result_of_another_call"
R_PARAMETER = "every_caller_passes_its_own_parameter_so_the_chain_moves_one_hop"
R_DEFAULT = "the_population_parameter_is_omitted_at_every_site"
R_CWD = "the_call_site_names_the_process_cwd_or_a_bare_dot"
R_NO_CALL = "no_call_site_in_the_tree"
RESOLUTION_VOCAB = (R_LITERAL, R_CONSTANT, R_WALK, R_FILE, R_DERIVED, R_CALL,
                    R_PARAMETER,
                    R_DEFAULT, R_CWD, R_NO_CALL)

REACH_EXTERNAL = "called_from_another_module"
REACH_SAME = "called_only_inside_its_own_module"
REACH_SELFTEST = "called_only_from_a_selftest_or_fixture"
REACH_NEVER = "never_called"
REACH_VOCAB = (REACH_EXTERNAL, REACH_SAME, REACH_SELFTEST, REACH_NEVER)

V_RECOVERABLE = "some_surfaces_get_a_population_an_adapter_could_read"
V_CHAIN = "every_called_surface_only_hands_on_a_parameter_of_its_caller"
V_SILENT = "no_surface_has_a_call_site_so_the_population_lives_only_in_the_signature"
V_SPLIT = "both_recoverable_and_unreachable_surfaces_exist"
VERDICT_VOCAB = (V_RECOVERABLE, V_CHAIN, V_SILENT, V_SPLIT)

# strongest first: the kind an adapter would have to read, most direct first
KIND_ORDER = (AK_LITERAL_NAMES, AK_LITERAL_STRING, AK_COMPOSITE_LITERAL,
              AK_IMPORTED_CONSTANT, AK_MODULE_CONSTANT_LITERAL, AK_MODULE_CONSTANT_BUILT,
              AK_WALK, AK_FILE_READ, AK_DERIVED, AK_CALL_RESULT, AK_PATH_COMPOSITION,
              AK_FILE_ROOT,
              AK_PARAMETER, AK_CWD, AK_KEYWORD_DEFAULT, AK_UNKNOWN)

RECOVERABLE_KINDS = (AK_LITERAL_NAMES, AK_LITERAL_STRING, AK_COMPOSITE_LITERAL,
                     AK_IMPORTED_CONSTANT, AK_MODULE_CONSTANT_LITERAL,
                     AK_MODULE_CONSTANT_BUILT, AK_WALK, AK_FILE_READ)

WALKERS = ("walk", "iglob", "glob", "rglob", "listdir", "iterdir", "scandir")
WRAPPERS = ("set", "list", "tuple", "sorted", "frozenset", "dict", "reversed", "iter")
READERS = ("open", "read_text", "read_bytes", "load", "loads", "read_csv", "read_parquet",
           "read_json", "load_face", "_load_json", "_load", "read_excel")

SKIP_DIRS = {".git", "Money02", "legacy", "_quarantine", "node_modules", "__pycache__",
             ".codely-cli", ".mypy_cache", ".pytest_cache", "venv", ".venv"}


def _now():
    return base._now()


def _is_self(rel):
    name = os.path.basename(rel)
    return any(name.startswith(p) for p in SELF_EXCLUDED)


def _text(node):
    try:
        return ast.unparse(node)
    except Exception:  # pragma: no cover - defensive
        return type(node).__name__


# --------------------------------------------------------------- the corpus
class Corpus(object):
    """Parse every source file once and answer call-site questions about it."""

    def __init__(self, root, names):
        self.root = root
        self.names = set(names)
        self.trees = {}
        self.reads = {}
        self.unreadable = []
        self.rows = {}          # (module, name) -> [site]
        self.star_importers = []  # (rel, module) -- a star import hides the binding
        self.defined = {}       # (rel, name) -> FunctionDef
        self.files = []
        for path in base.py_files(root):
            rel = base._rel(path, root)
            if _is_self(rel):
                continue
            self.files.append(rel)

    # ---- parsing
    def _parse(self, rel):
        if rel in self.trees:
            return self.trees[rel]
        try:
            text = base._read_text(os.path.join(self.root, rel))
        except Exception as exc:
            self.unreadable.append({"source": rel, "problem": repr(exc)[:120]})
            self.trees[rel] = None
            return None
        self.reads[rel] = text
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            self.unreadable.append({"source": rel,
                                    "problem": "syntax error line %r" % (exc.lineno,)})
            self.trees[rel] = None
            return None
        self.trees[rel] = tree
        return tree

    def _scan(self):
        for rel in self.files:
            text = self.reads.get(rel)
            if text is None:
                try:
                    text = base._read_text(os.path.join(self.root, rel))
                except Exception as exc:
                    self.unreadable.append({"source": rel, "problem": repr(exc)[:120]})
                    continue
                self.reads[rel] = text
            if not any(name in text for name in self.names):
                continue
            tree = self._parse(rel)
            if tree is None:
                continue
            assigns, _module_params = base.module_assigns(tree)
            self._index_defs(rel, tree)
            imports = self._imports(tree)
            parent = self._parents(tree)
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                for module, name, form in self._matches(rel, imports, node):
                    params = self._params(rel, module, name)
                    if params is None:
                        continue
                    site = self._site(rel, module, name, node, parent, params, assigns, form)
                    self.rows.setdefault((module, name), []).append(site)

    def _index_defs(self, rel, tree):
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.defined[(rel, node.name)] = node

    @staticmethod
    def _imports(tree):
        from_imports = {}
        module_aliases = {}
        star = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                for alias in node.names:
                    if alias.name == "*":
                        star.append(node.module)
                        continue
                    from_imports[alias.asname or alias.name] = (node.module, alias.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    local = alias.asname or alias.name.split(".")[0]
                    module_aliases[local] = alias.name
        return {"from_imports": from_imports, "module_aliases": module_aliases, "star": star}

    def _matches(self, rel, imports, node):
        """(module, name, form) for every population surface this call could reach."""
        out = []
        func = node.func
        if isinstance(func, ast.Name):
            if imports["from_imports"].get(func.id):
                module, orig = imports["from_imports"][func.id]
                if (module, orig) in self.rows or self._is_surface(module, orig):
                    out.append((module, orig, "from_import"))
            else:
                for module in self._module_of_source(rel):
                    if self._is_surface(module, func.id):
                        out.append((module, func.id, "same_module"))
        elif isinstance(func, ast.Attribute):
            receiver = func.value
            if isinstance(receiver, ast.Name):
                target = imports["module_aliases"].get(receiver.id)
                if target is None and self._is_surface(receiver.id, func.attr):
                    target = receiver.id
                if target and self._is_surface(target, func.attr):
                    out.append((target, func.attr, "module_attribute"))
        return out

    def _module_of_source(self, rel):
        return [os.path.splitext(os.path.basename(rel))[0]]

    def _is_surface(self, module, name):
        return (module, name) in self.surfaces

    def _params(self, rel, module, name):
        source_rel = self.surface_source[(module, name)]
        tree = self._parse(source_rel)
        if tree is None:
            return None
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
                a = node.args
                names = [x.arg for x in list(a.posonlyargs) + list(a.args)]
                return names
        return None

    @staticmethod
    def _parents(tree):
        parent = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parent[child] = node
        return parent

    def _enclosing(self, node, parent):
        cur = node
        selftest = False
        while cur is not None:
            cur = parent.get(cur)
            if cur is None:
                break
            if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
                selftest = selftest or cur.name in ("selftest", "_selftest") \
                    or cur.name.startswith("test_")
                return cur.name, cur, selftest
        return "<module>", None, selftest

    def _params_of(self, func_node):
        if func_node is None:
            return set()
        a = func_node.args
        return {x.arg for x in list(a.posonlyargs) + list(a.args) + list(a.kwonlyargs)}

    # ---- one site
    def _site(self, rel, module, name, node, parent, params, assigns, form):
        func_name, func_node, in_selftest = self._enclosing(node, parent)
        params_of_caller = self._params_of(func_node)
        args = []
        for idx, arg in enumerate(node.args):
            pname = params[idx] if idx < len(params) else "<extra:%d>" % idx
            kind = self._kind(arg, rel, params_of_caller, assigns)
            args.append({"parameter": pname, "position": idx,
                         "expression": _text(arg)[:120], "kind": kind})
        supplied = {a["parameter"] for a in args}
        for kw in node.keywords:
            if kw.arg is None:
                continue
            kind = self._kind(kw.value, rel, params_of_caller, assigns)
            args.append({"parameter": kw.arg, "position": None,
                         "expression": _text(kw.value)[:120], "kind": kind})
            supplied.add(kw.arg)
        pop_param = params[0] if params else None
        pop_kind = None
        for rec in args:
            if pop_param and rec["parameter"] == pop_param:
                pop_kind = rec["kind"]
        if pop_kind is None:
            pop_kind = AK_KEYWORD_DEFAULT if pop_param else AK_UNKNOWN
        return {
            "source": rel,
            "line": node.lineno,
            "surface": name,
            "module": module,
            "form": form,
            "call": _text(node.func)[:80],
            "enclosing": func_name,
            "in_selftest": bool(in_selftest),
            "arguments": args,
            "population_parameter": pop_param,
            "population_kind": pop_kind,
        }

    # ---- expression kinds
    def _kind(self, node, rel, caller_params, assigns, depth=0):
        if depth > 3:
            return AK_UNKNOWN
        if isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                return AK_CWD if node.value in ("", ".") else AK_LITERAL_STRING
            return AK_UNKNOWN
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            if node.elts and all(isinstance(e, ast.Constant) and isinstance(e.value, str)
                                 for e in node.elts):
                return AK_LITERAL_NAMES
            return AK_COMPOSITE_LITERAL
        if isinstance(node, ast.Dict):
            return AK_LITERAL_NAMES
        if isinstance(node, ast.Name):
            if node.id in caller_params:
                return AK_PARAMETER
            rhs = assigns.get(node.id)
            if rhs:
                kinds = {self._value_kind(v, rel, assigns, depth + 1) for v in rhs}
                if kinds == {AK_MODULE_CONSTANT_LITERAL}:
                    return AK_MODULE_CONSTANT_LITERAL
                for kind in KIND_ORDER:
                    if kind in kinds:
                        return kind
                return AK_MODULE_CONSTANT_BUILT
            return AK_UNKNOWN
        if isinstance(node, ast.Attribute):
            return AK_IMPORTED_CONSTANT
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
            return AK_DERIVED
        if isinstance(node, ast.Call):
            callee = _text(node.func)
            short = callee.split(".")[-1]
            if short in WALKERS:
                return AK_WALK
            if short in READERS:
                return AK_FILE_READ
            if short in WRAPPERS and len(node.args) == 1 and not node.keywords:
                return self._kind(node.args[0], rel, caller_params, assigns, depth + 1)
            if self._callee_walks(rel, short):
                return AK_WALK
            return AK_CALL_RESULT
        if isinstance(node, ast.BinOp):
            if self._mentions_file(node):
                return AK_FILE_ROOT
            return AK_PATH_COMPOSITION
        if isinstance(node, ast.JoinedStr):
            return AK_PATH_COMPOSITION
        return AK_UNKNOWN

    def _value_kind(self, node, rel, assigns, depth):
        kind = self._kind(node, rel, set(), assigns, depth)
        if kind in (AK_LITERAL_NAMES, AK_LITERAL_STRING, AK_COMPOSITE_LITERAL):
            return AK_MODULE_CONSTANT_LITERAL
        if kind in (AK_WALK, AK_FILE_READ):
            return kind
        if kind in (AK_IMPORTED_CONSTANT, AK_MODULE_CONSTANT_LITERAL):
            return AK_IMPORTED_CONSTANT
        return AK_MODULE_CONSTANT_BUILT

    def _callee_walks(self, rel, name, seen=None):
        """One hop into an in-repo callee: does its body walk the tree?"""
        seen = seen or set()
        if name in seen:
            return False
        seen.add(name)
        node = self.defined.get((rel, name))
        if node is None:
            return False
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                short = _text(sub.func).split(".")[-1]
                if short in WALKERS:
                    return True
                if short == name:
                    continue
                if self._callee_walks(rel, short, seen):
                    return True
        return False

    @staticmethod
    def _mentions_file(node):
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name) and sub.id == "__file__":
                return True
            if isinstance(sub, ast.Attribute) and sub.attr == "__file__":
                return True
            if isinstance(sub, ast.Constant) and sub.value in ("__file__",):
                return True
        return False

    def attach_surfaces(self, surfaces):
        self.surfaces = {(s["module"], s["name"]): s for s in surfaces}
        self.surface_source = {(s["module"], s["name"]): s["source"] for s in surfaces}


# ---------------------------------------------------------------- the reading
def population(root=None, upstream=None):
    root = root or ROOT
    face = upstream if upstream is not None else base._load_json(os.path.join(root, UPSTREAM_FACE))
    out = []
    for row in face.get("rows") or []:
        if row.get("class") != ARG_ONLY:
            continue
        surface = row.get("chosen_surface") or {}
        out.append({
            "module": row.get("module"),
            "name": surface.get("name"),
            "source": surface.get("source") or row.get("source"),
            "line": surface.get("line"),
            "required_args": surface.get("required_args") or 0,
        })
    return sorted(out, key=lambda s: (s["source"] or "", s["name"] or ""))


def resolution_of(surface, sites):
    if not sites:
        return R_NO_CALL
    kinds = {s["population_kind"] for s in sites}
    for kind in KIND_ORDER:
        if kind in kinds:
            if kind in (AK_LITERAL_NAMES, AK_LITERAL_STRING, AK_COMPOSITE_LITERAL):
                return R_LITERAL
            if kind in (AK_MODULE_CONSTANT_LITERAL, AK_MODULE_CONSTANT_BUILT,
                        AK_IMPORTED_CONSTANT):
                return R_CONSTANT
            if kind == AK_WALK:
                return R_WALK
            if kind == AK_FILE_READ:
                return R_FILE
            if kind == AK_DERIVED:
                return R_DERIVED
            if kind == AK_CALL_RESULT:
                return R_CALL
            if kind == AK_PARAMETER:
                return R_PARAMETER
            if kind in (AK_CWD, AK_FILE_ROOT):
                return R_CWD
            if kind == AK_KEYWORD_DEFAULT:
                return R_DEFAULT
            return R_CALL
    return R_NO_CALL


def reach_of(surface, sites):
    if not sites:
        return REACH_NEVER
    outside = [s for s in sites if s["module"] != _module_of(s["source"])]
    if outside:
        return REACH_EXTERNAL
    if all(s["in_selftest"] for s in sites):
        return REACH_SELFTEST
    return REACH_SAME


def _module_of(rel):
    return os.path.splitext(os.path.basename(rel or ""))[0]


def _count(records, key, vocab):
    counts = {k: 0 for k in vocab}
    for rec in records:
        value = rec.get(key)
        counts[value] = counts.get(value, 0) + 1
    return counts


def analyse(root=None, upstream=None):
    root = root or ROOT
    pop = population(root, upstream=upstream)
    corpus = Corpus(root, [s["name"] for s in pop])
    corpus.attach_surfaces(pop)
    corpus._scan()
    surfaces = []
    rows = []
    for surf in pop:
        sites = sorted(corpus.rows.get((surf["module"], surf["name"]), []),
                       key=lambda s: (s["source"], s["line"]))
        rec = dict(surf)
        rec["call_sites"] = len(sites)
        rec["external_sites"] = len([s for s in sites
                                     if s["module"] != _module_of(s["source"])])
        production = [s for s in sites if not s["in_selftest"]]
        rec["resolution_all_sites"] = resolution_of(surf, sites)
        rec["resolution_outside_selftests"] = (resolution_of(surf, production)
                                               if production else None)
        rec["resolution"] = (rec["resolution_outside_selftests"]
                             or rec["resolution_all_sites"])
        rec["resolution_scope"] = ("outside_selftests" if production
                                   else ("selftest_sites_only" if sites
                                         else "no_call_site"))
        rec["production_sites"] = len(production)
        first, strongest, same, strength = _parameter_concreteness(sites)
        rec["first_parameter"] = first
        rec["most_concrete_parameter"] = strongest
        rec["first_parameter_is_the_most_concrete"] = same
        rec["parameter_kinds"] = strength
        rec["reach"] = reach_of(surf, sites)
        rec["population_kind"] = sites[0]["population_kind"] if sites else None
        rec["kinds_by_parameter"] = _kinds_by_parameter(sites)
        rec["sites"] = sites
        surfaces.append(rec)
        rows.extend(sites)
    summary = _summary(surfaces, rows, corpus)
    return {"surfaces": surfaces, "rows": rows, "summary": summary,
            "unreadable": corpus.unreadable}


def _kinds_by_parameter(sites):
    out = {}
    for site in sites:
        for arg in site["arguments"]:
            bucket = out.setdefault(arg["parameter"], {})
            bucket[arg["kind"]] = bucket.get(arg["kind"], 0) + 1
    return out


def _parameter_concreteness(sites):
    """(first, most_concrete, same, per-parameter kind) for one surface.

    E505's surface record carries an arity, not which parameter is the population.  The
    headline reading therefore follows the first declared parameter, and this disclosure
    says how often the most concrete value at the site lands on a different parameter.

    It is an ordering of value FORM, not a claim about which parameter carries the
    population: a literal directory string outranks a loaded index by this ordering even
    when the index is the population, and the per-parameter table shows both.
    """
    if not sites:
        return None, None, None, {}
    order = list(KIND_ORDER)
    best = {}
    for site in sites:
        for arg in site["arguments"]:
            cur = best.get(arg["parameter"])
            if cur is None or order.index(arg["kind"]) < order.index(cur):
                best[arg["parameter"]] = arg["kind"]
    first = sites[0]["population_parameter"]
    strongest = first if first in best else (sorted(best)[0] if best else None)
    for name, kind in best.items():
        if strongest is None or order.index(kind) < order.index(best.get(strongest, AK_UNKNOWN)):
            strongest = name
    return first, strongest, (strongest == first), best


def _summary(surfaces, rows, corpus):
    res = _count(surfaces, "resolution", RESOLUTION_VOCAB)
    res_all = _count(surfaces, "resolution_all_sites", RESOLUTION_VOCAB)
    res_out = _count([s for s in surfaces if s["resolution_outside_selftests"]],
                     "resolution_outside_selftests", RESOLUTION_VOCAB)
    reach = _count(surfaces, "reach", REACH_VOCAB)
    kinds = _count(rows, "population_kind", AK_VOCAB)
    production_kinds = _count([r for r in rows if not r["in_selftest"]],
                              "population_kind", AK_VOCAB)
    recoverable = [s for s in surfaces if s["resolution"] in (R_LITERAL, R_CONSTANT,
                                                             R_WALK, R_FILE)]
    recoverable_all = [s for s in surfaces if s["resolution_all_sites"] in
                       (R_LITERAL, R_CONSTANT, R_WALK, R_FILE)]
    moved = [s for s in surfaces
             if s["resolution_outside_selftests"]
             and s["resolution_outside_selftests"] != s["resolution_all_sites"]]
    return {
        "surfaces": len(surfaces),
        "call_sites": len(rows),
        "sites_by_form": _count(rows, "form", ("same_module", "from_import",
                                              "module_attribute")),
        "surfaces_by_resolution": res,
        "surfaces_by_resolution_all_sites": res_all,
        "surfaces_by_resolution_outside_selftests": res_out,
        "surfaces_whose_reading_changes_when_selftests_are_dropped": len(moved),
        "surfaces_by_reach": reach,
        "sites_by_population_kind": kinds,
        "sites_by_population_kind_outside_selftests": production_kinds,
        "recoverable_surfaces": len(recoverable),
        "recoverable_surfaces_all_sites": len(recoverable_all),
        "recoverable_without_leaving_the_module": len(
            [s for s in recoverable if s["reach"] != REACH_EXTERNAL]),
        "sites_passing_a_parameter": kinds.get(AK_PARAMETER, 0),
        "sites_passing_a_literal": (kinds.get(AK_LITERAL_NAMES, 0)
                                    + kinds.get(AK_LITERAL_STRING, 0)
                                    + kinds.get(AK_COMPOSITE_LITERAL, 0)),
        "sites_passing_a_walk": kinds.get(AK_WALK, 0),
        "sites_passing_a_constant": (kinds.get(AK_MODULE_CONSTANT_LITERAL, 0)
                                     + kinds.get(AK_MODULE_CONSTANT_BUILT, 0)
                                     + kinds.get(AK_IMPORTED_CONSTANT, 0)),
        "sites_passing_the_cwd": kinds.get(AK_CWD, 0) + kinds.get(AK_FILE_ROOT, 0),
        "surfaces_never_called": reach[REACH_NEVER],
        "surfaces_called_from_another_module": reach[REACH_EXTERNAL],
        "files_scanned": len(corpus.files),
        "files_unreadable": len(corpus.unreadable),
        "sites_in_selftests": len([r for r in rows if r["in_selftest"]]),
        "surfaces_with_more_than_one_parameter": len(
            [s for s in surfaces if len(s.get("parameter_kinds") or {}) > 1]),
        "surfaces_where_the_first_parameter_is_not_the_most_concrete_one": len(
            [s for s in surfaces if s.get("first_parameter_is_the_most_concrete") is False]),
    }


def _verdict(summary):
    rec = summary.get("recoverable_surfaces") or 0
    silent = summary.get("surfaces_never_called") or 0
    total = summary.get("surfaces") or 0
    if total and silent == total:
        return V_SILENT
    if rec and silent:
        return V_SPLIT
    if rec:
        return V_RECOVERABLE
    return V_CHAIN


def _answers(summary):
    return {
        "how_many_argument_only_surfaces_did_e505_publish": summary["surfaces"],
        "how_many_have_a_call_site_in_the_tree":
            summary["surfaces"] - summary["surfaces_never_called"],
        "how_many_do_the_call_sites_hand_a_population_an_adapter_could_read":
            summary["recoverable_surfaces"],
        "how_many_of_those_are_never_called_from_outside_their_own_module":
            summary["recoverable_without_leaving_the_module"],
        "how_many_are_called_only_with_their_callers_own_parameter": (
            summary["surfaces_by_resolution"].get(R_PARAMETER, 0)),
        "how_many_have_no_call_site_at_all": summary["surfaces_never_called"],
        "how_many_sites_pass_a_literal": summary["sites_passing_a_literal"],
        "how_many_sites_pass_a_module_constant": summary["sites_passing_a_constant"],
        "how_many_sites_pass_a_tree_walk": summary["sites_passing_a_walk"],
        "how_many_sites_pass_the_process_cwd": summary["sites_passing_the_cwd"],
        "how_many_readings_change_when_selftest_sites_are_dropped":
            summary["surfaces_whose_reading_changes_when_selftests_are_dropped"],
        "how_many_recoverable_if_selftest_sites_are_counted":
            summary["recoverable_surfaces_all_sites"],
        "how_many_surfaces_where_the_most_concrete_argument_is_not_the_first_parameter":
            summary["surfaces_where_the_first_parameter_is_not_the_most_concrete_one"],
    }


def build(root=None, write=True, upstream=None):
    root = root or ROOT
    got = analyse(root, upstream=upstream)
    summary = got["summary"]
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("Read the call sites of E505's 35 argument-only population surfaces: what "
                  "value does each caller hand the surface, and is the population recoverable "
                  "from a call site?"),
        "evidence_cutoff": DATE_STAMP,
        "generated": _now(),
        "population_source": POPULATION_SOURCE,
        "kind_vocab": list(AK_VOCAB),
        "resolution_vocab": list(RESOLUTION_VOCAB),
        "reach_vocab": list(REACH_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "method_limits": [
            "the population is E505's own published face: a surface appears here because "
            "that face classed it argument-only, not because this study re-read E505's rows",
            "the first declared parameter is treated as the population handle; E505's "
            "surface record carries only an arity, so every other argument is published "
            "beside it and a surface whose first parameter is not the population is visible "
            "in its kinds_by_parameter",
            "a call is attributed by import form only: a direct name needs a from-import of "
            "the surface module or a same-module site, and an attribute call needs the "
            "receiver to be an in-repo module alias; calls reached through getattr, a star "
            "import, or a dynamic dispatch are out of this reader's reach and are not counted "
            "as either present or absent",
            "a tree walk is attributed one hop: a callee's body is checked for a walk call, "
            "but a walk hidden two calls deep reads as a plain call result",
            "only the tree is read: a surface called only from git history, a notebook, or a "
            "scheduled task's command line has no site here, which the reach axis says "
            "explicitly rather than folding it into 'never called by code in the tree'",
            "the population parameter is not type-checked; a module constant reaching it may "
            "hold something other than names, and every constant is published with the "
            "expression that supplied it",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "answers": _answers(summary),
        "surfaces": got["surfaces"],
        "rows": got["rows"],
        "unreadable": got["unreadable"],
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
def summary_problems(summary, surfaces, rows):
    problems = []
    if summary.get("surfaces") != len(surfaces):
        problems.append("surfaces=%r is not the surface count %d"
                        % (summary.get("surfaces"), len(surfaces)))
    if summary.get("call_sites") != len(rows):
        problems.append("call_sites is not the site count")
    res = _count(surfaces, "resolution", RESOLUTION_VOCAB)
    if summary.get("surfaces_by_resolution") != res:
        problems.append("surfaces_by_resolution does not re-derive")
    res_all = _count(surfaces, "resolution_all_sites", RESOLUTION_VOCAB)
    if summary.get("surfaces_by_resolution_all_sites") != res_all:
        problems.append("surfaces_by_resolution_all_sites does not re-derive")
    res_out = _count([s for s in surfaces if s.get("resolution_outside_selftests")],
                     "resolution_outside_selftests", RESOLUTION_VOCAB)
    if summary.get("surfaces_by_resolution_outside_selftests") != res_out:
        problems.append("surfaces_by_resolution_outside_selftests does not re-derive")
    moved = len([s for s in surfaces
                 if s.get("resolution_outside_selftests")
                 and s.get("resolution_outside_selftests") != s.get("resolution_all_sites")])
    if summary.get("surfaces_whose_reading_changes_when_selftests_are_dropped") != moved:
        problems.append("the selftest-drop movement count does not re-derive")
    kinds_out = _count([r for r in rows if not r.get("in_selftest")],
                       "population_kind", AK_VOCAB)
    if summary.get("sites_by_population_kind_outside_selftests") != kinds_out:
        problems.append("sites_by_population_kind_outside_selftests does not re-derive")
    if summary.get("surfaces_with_more_than_one_parameter") != len(
            [s for s in surfaces if len(s.get("parameter_kinds") or {}) > 1]):
        problems.append("surfaces_with_more_than_one_parameter does not re-derive")
    if summary.get("surfaces_where_the_first_parameter_is_not_the_most_concrete_one") != len(
            [s for s in surfaces if s.get("first_parameter_is_the_most_concrete") is False]):
        problems.append("the parameter-disclosure count does not re-derive")
    if summary.get("recoverable_surfaces_all_sites") != sum(
            res_all[k] for k in (R_LITERAL, R_CONSTANT, R_WALK, R_FILE)):
        problems.append("recoverable_surfaces_all_sites is not the all-sites total")
    reach = _count(surfaces, "reach", REACH_VOCAB)
    if summary.get("surfaces_by_reach") != reach:
        problems.append("surfaces_by_reach does not re-derive")
    kinds = _count(rows, "population_kind", AK_VOCAB)
    if summary.get("sites_by_population_kind") != kinds:
        problems.append("sites_by_population_kind does not re-derive")
    rec = sum(res[k] for k in (R_LITERAL, R_CONSTANT, R_WALK, R_FILE))
    if summary.get("recoverable_surfaces") != rec:
        problems.append("recoverable_surfaces is not the recoverable class total")
    if summary.get("surfaces_never_called") != reach[REACH_NEVER]:
        problems.append("surfaces_never_called is not the never-called total")
    if summary.get("surfaces_called_from_another_module") != reach[REACH_EXTERNAL]:
        problems.append("surfaces_called_from_another_module is not that reach total")
    lit = kinds[AK_LITERAL_NAMES] + kinds[AK_LITERAL_STRING] + kinds[AK_COMPOSITE_LITERAL]
    if summary.get("sites_passing_a_literal") != lit:
        problems.append("sites_passing_a_literal does not re-derive")
    con = (kinds[AK_MODULE_CONSTANT_LITERAL] + kinds[AK_MODULE_CONSTANT_BUILT]
           + kinds[AK_IMPORTED_CONSTANT])
    if summary.get("sites_passing_a_constant") != con:
        problems.append("sites_passing_a_constant does not re-derive")
    if summary.get("sites_passing_a_walk") != kinds[AK_WALK]:
        problems.append("sites_passing_a_walk does not re-derive")
    form = _count(rows, "form", ("same_module", "from_import", "module_attribute"))
    if sum(form.values()) != len(rows):
        problems.append("a site carries a form outside the vocabulary")
    if summary.get("sites_by_form") != form:
        problems.append("sites_by_form does not re-derive")
    if summary.get("sites_in_selftests") != len([r for r in rows if r.get("in_selftest")]):
        problems.append("sites_in_selftests does not re-derive")
    return problems


def surface_problems(face):
    surfaces = face.get("surfaces") or []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    problems = summary_problems(summary, surfaces, rows)
    by_surface = {}
    for row in rows:
        if row.get("population_kind") not in AK_VOCAB:
            problems.append("%s:%r: kind outside the vocabulary"
                            % (row.get("source"), row.get("line")))
        for arg in row.get("arguments") or []:
            if arg.get("kind") not in AK_VOCAB:
                problems.append("%s:%r: argument kind outside the vocabulary"
                                % (row.get("source"), row.get("line")))
        if not row.get("population_parameter"):
            problems.append("%s:%r: site names no population parameter"
                            % (row.get("source"), row.get("line")))
        by_surface.setdefault((row.get("module"), row.get("surface")), []).append(row)
    seen = set()
    for rec in surfaces:
        key = (rec.get("module"), rec.get("name"))
        if key in seen:
            problems.append("%r appears twice" % (key,))
        seen.add(key)
        sites = sorted(by_surface.get(key, []), key=lambda s: (s["source"], s["line"]))
        production = [s for s in sites if not s.get("in_selftest")]
        if rec.get("resolution") not in RESOLUTION_VOCAB:
            problems.append("%r: resolution outside the vocabulary" % (key,))
        if rec.get("resolution_all_sites") != resolution_of(rec, sites):
            problems.append("%r: the all-sites arm does not re-derive" % (key,))
        expected_out = resolution_of(rec, production) if production else None
        if rec.get("resolution_outside_selftests") != expected_out:
            problems.append("%r: the production arm does not re-derive" % (key,))
        expected = expected_out or rec.get("resolution_all_sites")
        if rec.get("resolution") != expected:
            problems.append("%r: the headline reading is not the stronger arm" % (key,))
        expected_scope = ("outside_selftests" if production
                          else ("selftest_sites_only" if sites else "no_call_site"))
        if rec.get("resolution_scope") != expected_scope:
            problems.append("%r: resolution_scope does not re-derive" % (key,))
        if rec.get("production_sites") != len(production):
            problems.append("%r: production_sites is not the non-selftest site count"
                            % (key,))
        first, strongest, same, strength = _parameter_concreteness(sites)
        if rec.get("first_parameter") != first:
            problems.append("%r: first_parameter does not re-derive" % (key,))
        if rec.get("most_concrete_parameter") != strongest:
            problems.append("%r: most_concrete_parameter does not re-derive" % (key,))
        if rec.get("first_parameter_is_the_most_concrete") != same:
            problems.append("%r: the parameter disclosure does not re-derive" % (key,))
        if rec.get("parameter_kinds") != strength:
            problems.append("%r: parameter_kinds does not re-derive" % (key,))
        if rec.get("reach") not in REACH_VOCAB:
            problems.append("%r: reach outside the vocabulary" % (key,))
        if rec.get("reach") != reach_of(rec, sites):
            problems.append("%r: reach does not re-derive from its sites" % (key,))
        if rec.get("call_sites") != len(sites):
            problems.append("%r: call_sites is not the embedded site count" % (key,))
        if rec.get("kinds_by_parameter") != _kinds_by_parameter(sites):
            problems.append("%r: kinds_by_parameter does not re-derive" % (key,))
        embedded = {(s.get("source"), s.get("line")) for s in rec.get("sites") or []}
        if embedded != {(s["source"], s["line"]) for s in sites}:
            problems.append("%r: embedded sites disagree with the row table" % (key,))
    for key in by_surface:
        if key not in seen:
            problems.append("%r: a call site names a surface the face never publishes"
                            % (key,))
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the vocabulary")
    if face.get("verdict") != _verdict(summary):
        problems.append("verdict=%r does not re-derive from the summary (%r)"
                        % (face.get("verdict"), _verdict(summary)))
    answers = face.get("answers") or {}
    if answers.get("how_many_argument_only_surfaces_did_e505_publish") != \
            summary.get("surfaces"):
        problems.append("answers surface count is not the published surface count")
    if answers.get("how_many_have_a_call_site_in_the_tree") != \
            summary.get("surfaces", 0) - summary.get("surfaces_never_called", 0):
        problems.append("answers called-surface count does not re-derive")
    if answers.get("how_many_are_called_only_with_their_callers_own_parameter") != \
            (summary.get("surfaces_by_resolution") or {}).get(R_PARAMETER, 0):
        problems.append("answers caller-chain count is not the parameter class total")
    if answers.get("how_many_have_no_call_site_at_all") != summary.get("surfaces_never_called"):
        problems.append("answers never-called count is not the reach total")
    if answers.get("how_many_readings_change_when_selftest_sites_are_dropped") != \
            summary.get("surfaces_whose_reading_changes_when_selftests_are_dropped"):
        problems.append("answers selftest-drop count does not re-derive")
    if answers.get("how_many_recoverable_if_selftest_sites_are_counted") != \
            summary.get("recoverable_surfaces_all_sites"):
        problems.append("answers all-sites recoverable count does not re-derive")
    if answers.get("how_many_surfaces_where_the_most_concrete_argument_is_not_the_first_parameter") != \
            summary.get("surfaces_where_the_first_parameter_is_not_the_most_concrete_one"):
        problems.append("answers parameter-disclosure count does not re-derive")
    return problems


def check(face=None, root=None):
    root = root or ROOT
    face = face or base._load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))
    problems = surface_problems(face)
    print("check problems=%r" % (problems,))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    face = build(root, write=False)
    problems = surface_problems(face)
    print("verify problems=%r" % (problems,))
    print("verdict=%s" % face["verdict"])
    print("summary=%s" % json.dumps(face["summary"], ensure_ascii=False, sort_keys=True))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
FIXTURE = {
    "scripts/lit_study.py": '''def census(units):
    return len(units)


def build():
    return census(["alpha", "beta"])


def _selftest():
    return census(["x"])
''',
    "scripts/const_study.py": '''NAMES = ["alpha", "beta", "gamma"]


def census(universe):
    return len(universe)


def build():
    return census(NAMES)
''',
    "scripts/walk_study.py": '''import os


def python_files(root):
    out = []
    for dirpath, dirnames, files in os.walk(root):
        for name in files:
            if name.endswith(".py"):
                out.append(os.path.join(dirpath, name))
    return out


def census(corpus):
    return len(corpus)


def build():
    return census(python_files("."))
''',
    "scripts/chain_study.py": '''def census(members):
    return len(members)


def run(members):
    return census(members)
''',
    "scripts/silent_study.py": '''def census(population):
    return len(population)
''',
    "scripts/external_study.py": '''def census(corpus):
    return len(corpus)
''',
    "scripts/consumer.py": '''import external_study

FROZEN = ["alpha", "beta"]


def go():
    return external_study.census(FROZEN)
''',
}


def _fixture_upstream():
    rows = []
    for module, name, args in (("lit_study", "census", 1), ("const_study", "census", 1),
                               ("walk_study", "census", 1), ("chain_study", "census", 1),
                               ("silent_study", "census", 1), ("external_study", "census", 1)):
        rows.append({
            "module": module,
            "source": "scripts/%s.py" % module,
            "class": ARG_ONLY,
            "chosen_surface": {"name": name, "source": "scripts/%s.py" % module,
                               "line": 1, "required_args": args, "kind": "function"},
        })
    return {"rows": rows}


def selftest():
    checks, failures = 0, []

    def ok(name, cond, detail=None):
        nonlocal checks
        checks += 1
        if not cond:
            failures.append("%s (%r)" % (name, detail))

    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="e508_selftest_")
    try:
        os.makedirs(os.path.join(tmp, "scripts"))
        for rel, body in FIXTURE.items():
            path = os.path.join(tmp, rel.replace("/", os.sep))
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(body)
        face = build(root=tmp, write=False, upstream=_fixture_upstream())
        by = {s["module"]: s for s in face["surfaces"]}

        ok("a literal at the call site is read as a literal",
           by["lit_study"]["resolution"] == R_LITERAL, by["lit_study"]["resolution"])
        ok("a module constant is read as a constant",
           by["const_study"]["resolution"] == R_CONSTANT, by["const_study"]["resolution"])
        ok("a walk wrapped in a local function is followed one hop",
           by["walk_study"]["resolution"] == R_WALK, by["walk_study"]["resolution"])
        ok("a caller's own parameter is not folded into a concrete kind",
           by["chain_study"]["resolution"] == R_PARAMETER, by["chain_study"]["resolution"])
        ok("a surface nobody calls is published as never called",
           by["silent_study"]["reach"] == REACH_NEVER, by["silent_study"]["reach"])
        ok("a surface called from another module is published as external",
           by["external_study"]["reach"] == REACH_EXTERNAL, by["external_study"]["reach"])
        ok("an attribute call through an imported module is attributed to it",
           by["external_study"]["call_sites"] == 1, by["external_study"]["call_sites"])
        ok("a same-module call is attributed to the surface",
           by["lit_study"]["call_sites"] == 2, by["lit_study"]["call_sites"])
        ok("a selftest-only call is separated from production calls",
           by["silent_study"]["reach"] == REACH_NEVER and
           any(s["in_selftest"] for s in by["lit_study"]["sites"]),
           [s["in_selftest"] for s in by["lit_study"]["sites"]])
        ok("the fixture verdict is the split one",
           face["verdict"] == V_SPLIT, face["verdict"])
        ok("gate passes on the built fixture",
           surface_problems(face) == [], surface_problems(face))

        doctored = json.loads(json.dumps(face))
        doctored["surfaces"][0]["resolution"] = R_LITERAL
        ok("gate refuses a resolution its sites contradict",
           surface_problems(doctored) != [])
        doctored2 = json.loads(json.dumps(face))
        doctored2["surfaces"][0]["reach"] = REACH_EXTERNAL
        ok("gate refuses a reach its sites contradict", surface_problems(doctored2) != [])
        doctored3 = json.loads(json.dumps(face))
        doctored3["summary"]["recoverable_surfaces"] += 1
        ok("gate refuses a hand-written recoverable count",
           surface_problems(doctored3) != [])
        doctored4 = json.loads(json.dumps(face))
        doctored4["verdict"] = V_SILENT
        ok("gate refuses a hand-written verdict", surface_problems(doctored4) != [])
        doctored5 = json.loads(json.dumps(face))
        doctored5["rows"][0]["population_kind"] = "guessed"
        ok("gate refuses a kind outside the vocabulary", surface_problems(doctored5) != [])
        doctored6 = json.loads(json.dumps(face))
        doctored6["rows"][0]["surface"] = "census_of_nowhere"
        ok("gate refuses a site naming a surface the face never publishes",
           surface_problems(doctored6) != [])
        doctored7 = json.loads(json.dumps(face))
        doctored7["answers"]["how_many_have_no_call_site_at_all"] += 1
        ok("gate refuses a hand-written never-called count",
           surface_problems(doctored7) != [])
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